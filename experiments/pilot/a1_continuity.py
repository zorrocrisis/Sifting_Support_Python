"""
Pilot A1 -- can NCD find continuity at all?

  python -m experiments.pilot.a1_continuity [--no-embeddings] [--pass-recall 0.5]

For each past dialogue line, ranks every current-session event by NCD
(ascending, game concatenation order) and by sentence-embedding cosine
similarity (descending). With gold matches filled in, reports the rank of each
expected event, Recall@5/10 and MRR for both methods.

Pass (operationalised): NCD mean Recall@5 >= --pass-recall (default 0.5,
"expected events are mostly in NCD's top 5").

Also reports how much the NCD concatenation order changes the rankings.

Outputs (experiments/pilot/out/):
  a1_rankings.csv   top-10 events per dialogue line per method (for inspection)
  a1_gold_ranks.csv rank of every gold event under each method
  a1_result.json    metrics + status
  a1_report.md
"""

import argparse

import numpy as np

from experiments.common import cc, ncd, paths
from experiments.common.context import PilotContext
from experiments.common.gold import map_to_candidates, read_gold, retrieval_metrics
from experiments.common.report import md_table, short, write_csv, write_json

TOP_N = 10


def orders_for(score_matrix, higher_is_better):
    return {d: cc.rank_events(score_matrix[d], higher_is_better) for d in range(score_matrix.shape[0])}


def order_sensitivity(ctx, k=5, n_pairs=14):
    """Compare event-first (game) vs dialogue-first NCD rankings."""
    M_df_all = ncd.ncd_rect(ctx.dialogue.unique, ctx.events.unique, order=ncd.DIALOGUE_FIRST)
    M_df = ctx.restrict(M_df_all)
    per_d = []
    for d in range(len(ctx.dialogue)):
        a = set(cc.rank_events(ctx.M[d])[:k])
        b = set(cc.rank_events(M_df[d])[:k])
        per_d.append(len(a & b) / k)
    ga = {(p["d"], p["e"]) for p in cc.select_nearest(ctx.M, n_pairs)}
    gb = {(p["d"], p["e"]) for p in cc.select_nearest(M_df, n_pairs)}
    return {
        "k": k,
        "mean_topk_overlap_per_dialogue": sum(per_d) / len(per_d),
        "global_pairs": n_pairs,
        "global_pair_overlap": len(ga & gb) / n_pairs,
        "max_abs_ncd_diff": float(abs(ctx.M_all - M_df_all).max()),
    }


def run(use_embeddings=True, pass_recall=0.5):
    paths.ensure_out()
    ctx = PilotContext()
    ev, dl = ctx.events, ctx.dialogue

    cc_name = ctx.similarity_mode   # the CC's own measure: "ncd", "index" or "embed"
    methods = {cc_name: orders_for(ctx.M, higher_is_better=False)}
    scores = {cc_name: ctx.M}
    if use_embeddings:
        from experiments.common.embed import DEFAULT_MODEL, cosine_rect
        S = ctx.restrict(cosine_rect(dl.unique, ev.unique), fill=-np.inf)
        methods["embedding"] = orders_for(S, higher_is_better=True)
        scores["embedding"] = S

    # Top-N rankings for inspection
    rows = []
    for d in range(len(dl)):
        for m, orders in methods.items():
            for r, e in enumerate(orders[d][:TOP_N]):
                rows.append({"dialogue_id": ctx.dialogue_id(d), "method": m, "rank": r + 1,
                             "event": ctx.event_code(e), "score": round(float(scores[m][d, e]), 4),
                             "dialogue": dl.unique[d], "event_description": ev.unique[e]})
    write_csv(paths.OUT_DIR / "a1_rankings.csv", rows)

    gold_original, problems = read_gold(paths.GOLD_PATH, ctx)
    gold = map_to_candidates(gold_original, ctx)
    sens = order_sensitivity(ctx) if ctx.similarity_mode == "ncd" else None
    result = {"test": "A1", "gold_file": str(paths.GOLD_PATH.relative_to(paths.REPO_ROOT)),
              "n_events": len(ev), "n_dialogue": len(dl), "gold_problems": problems,
              "ncd_order": ctx.order, "order_sensitivity": sens, "cc_method": cc_name,
              "embedding_model": DEFAULT_MODEL if use_embeddings else None,
              "pass_rule": f"NCD mean Recall@5 >= {pass_recall}",
              "cc_candidates": ctx.candidate_mode, "n_candidates": int(ctx.candidate_mask.sum()),
              "n_gold_pairs_original": sum(len(t) for t in gold_original.values()),
              "n_gold_events_that_are_candidates": sum(bool(ctx.candidate_mask[e])
                                                       for t in gold_original.values() for e in t)}

    gold_rows = []
    if not gold:
        result["status"] = "pending"
        result["status_reason"] = "gold_matches.csv has no expected events yet"
    else:
        result["metrics"] = {}
        per_method = {}
        for m, orders in methods.items():
            per, overall = retrieval_metrics(orders, gold)
            result["metrics"][m] = overall
            per_method[m] = per
        # Sensitivity: gold pairs whose event has exactly the reference line's description are
        # trivial for any method (the same log happening again). Recompute without them.
        gold_nontrivial = {d: {e for e in t if ev.unique[e] != dl.unique[d]} for d, t in gold.items()}
        gold_nontrivial = {d: t for d, t in gold_nontrivial.items() if t}
        n_exact = sum(len(t) for t in gold.values()) - sum(len(t) for t in gold_nontrivial.values())
        result["n_exact_repeat_gold_pairs"] = n_exact
        if n_exact and gold_nontrivial:
            result["metrics_without_exact_repeats"] = {
                m: retrieval_metrics(orders, gold_nontrivial)[1] for m, orders in methods.items()}
        for d, targets in sorted(gold_original.items()):
            for e in sorted(targets):
                r = ctx.representative(e)
                row = {"dialogue_id": ctx.dialogue_id(d), "event": ctx.event_code(e),
                       "represented_by": "" if r == e else ctx.event_code(r),
                       "dialogue": dl.unique[d], "event_description": ev.unique[e]}
                for m in methods:
                    row[f"{m}_rank"] = per_method[m][d]["ranks"][r]
                gold_rows.append(row)
        if ctx.candidate_mode == "filtered":
            # Strict scoring: only the exact gold log counts (the pass rule stays on lenient scoring,
            # as in every earlier run; strict is reported alongside).
            from experiments.common.gold import strict_retrieval_metrics
            result["metrics_strict"] = {
                m: strict_retrieval_metrics(orders, gold_original, ctx.candidate_mask)[1]
                for m, orders in methods.items()}
            result["status_strict"] = ("pass" if result["metrics_strict"][cc_name]["recall@5"] >= pass_recall
                                       else "fail")
        r5 = result["metrics"][cc_name]["recall@5"]
        result["status"] = "pass" if r5 >= pass_recall else "fail"
        if "embedding" in result["metrics"]:
            emb_ok = result["metrics"]["embedding"]["recall@5"] >= pass_recall
            result["embedding_passes"] = emb_ok
    write_csv(paths.OUT_DIR / "a1_gold_ranks.csv", gold_rows,
              ["dialogue_id", "event", "represented_by", f"{cc_name}_rank", "embedding_rank", "dialogue",
               "event_description"])
    write_json(paths.OUT_DIR / "a1_result.json", result)
    write_report(ctx, result, methods, gold_rows)
    return result


def write_report(ctx, result, methods, gold_rows):
    dl, ev = ctx.dialogue, ctx.events
    L = ["# A1 — Can NCD find continuity?", "",
         f"**Status: {result['status'].upper()}**"
         + (f" — {result.get('status_reason')}" if result.get("status_reason") else ""), "",
         f"{len(dl)} past dialogue lines × {len(ev)} current-session events. "
         f"NCD order: `{ctx.order}` (matches the game). Pass rule: {result['pass_rule']}.", ""]
    if result["cc_candidates"] == "filtered":
        L += [f"**CC candidates: filtered.** The CC may only pick the {result['n_candidates']} cluster "
              f"representatives of session 2 at NCD threshold {paths.CC_FILTER_THRESHOLD} (the AC's "
              "unique_logs_after_filtering, before traversal). A gold event folded into a cluster counts as "
              "found when its representative is retrieved; "
              f"{result['n_gold_events_that_are_candidates']} of {result['n_gold_pairs_original']} gold events "
              "are representatives themselves.", ""]
    if result.get("gold_problems"):
        L += ["Gold file problems:", ""] + [f"- {p}" for p in result["gold_problems"]] + [""]
    if "metrics" in result:
        L += ["## Metrics", ""]
        rows = [[m, v["recall@5"], v["recall@10"], v["mrr"], v["n_dialogue_with_gold"], v["n_gold_pairs"]]
                for m, v in result["metrics"].items()]
        L += [md_table(["method", "Recall@5", "Recall@10", "MRR", "dialogue lines", "gold pairs"], rows), ""]
        if result.get("metrics_strict"):
            ms = result["metrics_strict"]
            reach = next(iter(ms.values()))["n_gold_reachable"]
            L += [f"**Strict scoring** (only the exact gold log counts; {reach} of "
                  f"{next(iter(ms.values()))['n_gold_pairs']} gold events are candidates at all). "
                  f"Strict verdict: {result['status_strict']}.", "",
                  md_table(["method", "Recall@5", "Recall@10", "MRR"],
                           [[m, v["recall@5"], v["recall@10"], v["mrr"]] for m, v in ms.items()]), ""]
        if result.get("metrics_without_exact_repeats"):
            L += [f"Without the {result['n_exact_repeat_gold_pairs']} gold pairs whose event is the reference "
                  "line's exact description repeated (sensitivity check, not the pass rule):", "",
                  md_table(["method", "Recall@5", "Recall@10", "MRR", "dialogue lines", "gold pairs"],
                           [[m, v["recall@5"], v["recall@10"], v["mrr"], v["n_dialogue_with_gold"], v["n_gold_pairs"]]
                            for m, v in result["metrics_without_exact_repeats"].items()]), ""]
        L += ["## Rank of each expected event", ""]
        cc_name = result["cc_method"]
        L += [md_table(["dialogue", "event", f"{cc_name} rank", "embedding rank", "event description"],
                       [[g["dialogue_id"], g["event"] + (f" → {g['represented_by']}" if g.get("represented_by") else ""), g[f"{cc_name}_rank"], g.get("embedding_rank", "–"),
                         short(g["event_description"], 70)] for g in gold_rows]), ""]
    s = result["order_sensitivity"]
    if s:
        L += ["## Concatenation order (event-first vs dialogue-first)", "",
              f"- Mean top-{s['k']} overlap per dialogue line: {s['mean_topk_overlap_per_dialogue']:.2f}",
              f"- Overlap of the global top-{s['global_pairs']} pairs (what the game requests at share 0.5): "
              f"{s['global_pair_overlap']:.2f}",
              f"- Largest NCD difference between orders: {s['max_abs_ncd_diff']:.3f}", ""]
    if ctx.similarity_mode == "index":
        L += ["**CC similarity: event indexing** (entities, place, log type, NCD text; see "
              "`experiments/common/event_index.py`). The `index` method ranks by that score.", ""]
    L += ["## Top 5 per dialogue line", ""]
    for d in range(len(dl)):
        L += [f"**{ctx.dialogue_id(d)}** — {dl.unique[d]}", ""]
        header = ["#"] + list(methods)
        rows = [[r + 1] + [f"{ctx.event_code(methods[m][d][r])} {short(ev.unique[methods[m][d][r]], 60)}"
                           for m in methods] for r in range(5)]
        L += [md_table(header, rows), ""]
    (paths.OUT_DIR / "a1_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-embeddings", action="store_true")
    ap.add_argument("--pass-recall", type=float, default=0.5)
    a = ap.parse_args()
    r = run(use_embeddings=not a.no_embeddings, pass_recall=a.pass_recall)
    print(f"A1: {r['status']}")


if __name__ == "__main__":
    main()
