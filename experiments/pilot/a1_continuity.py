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

from experiments.common import cc, ncd, paths
from experiments.common.context import PilotContext
from experiments.common.gold import read_gold, retrieval_metrics
from experiments.common.report import md_table, short, write_csv, write_json
from experiments.pilot.make_gold_helper import GOLD_PATH

TOP_N = 10


def orders_for(score_matrix, higher_is_better):
    return {d: cc.rank_events(score_matrix[d], higher_is_better) for d in range(score_matrix.shape[0])}


def order_sensitivity(ctx, k=5, n_pairs=14):
    """Compare event-first (game) vs dialogue-first NCD rankings."""
    M_df = ncd.ncd_rect(ctx.dialogue.unique, ctx.events.unique, order=ncd.DIALOGUE_FIRST)
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
        "max_abs_ncd_diff": float(abs(ctx.M - M_df).max()),
    }


def run(use_embeddings=True, pass_recall=0.5):
    paths.ensure_out()
    ctx = PilotContext()
    ev, dl = ctx.events, ctx.dialogue

    methods = {"ncd": orders_for(ctx.M, higher_is_better=False)}
    scores = {"ncd": ctx.M}
    if use_embeddings:
        from experiments.common.embed import DEFAULT_MODEL, cosine_rect
        S = cosine_rect(dl.unique, ev.unique)
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

    gold, problems = read_gold(GOLD_PATH, ctx)
    sens = order_sensitivity(ctx)
    result = {"test": "A1", "gold_file": str(GOLD_PATH.relative_to(paths.REPO_ROOT)),
              "n_events": len(ev), "n_dialogue": len(dl), "gold_problems": problems,
              "ncd_order": ctx.order, "order_sensitivity": sens,
              "embedding_model": DEFAULT_MODEL if use_embeddings else None,
              "pass_rule": f"NCD mean Recall@5 >= {pass_recall}"}

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
        for d, targets in sorted(gold.items()):
            for e in sorted(targets):
                row = {"dialogue_id": ctx.dialogue_id(d), "event": ctx.event_code(e),
                       "dialogue": dl.unique[d], "event_description": ev.unique[e]}
                for m in methods:
                    row[f"{m}_rank"] = per_method[m][d]["ranks"][e]
                gold_rows.append(row)
        r5 = result["metrics"]["ncd"]["recall@5"]
        result["status"] = "pass" if r5 >= pass_recall else "fail"
        if "embedding" in result["metrics"]:
            emb_ok = result["metrics"]["embedding"]["recall@5"] >= pass_recall
            result["embedding_passes"] = emb_ok
    write_csv(paths.OUT_DIR / "a1_gold_ranks.csv", gold_rows,
              ["dialogue_id", "event", "ncd_rank", "embedding_rank", "dialogue", "event_description"])
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
    if result.get("gold_problems"):
        L += ["Gold file problems:", ""] + [f"- {p}" for p in result["gold_problems"]] + [""]
    if "metrics" in result:
        L += ["## Metrics", ""]
        rows = [[m, v["recall@5"], v["recall@10"], v["mrr"], v["n_dialogue_with_gold"], v["n_gold_pairs"]]
                for m, v in result["metrics"].items()]
        L += [md_table(["method", "Recall@5", "Recall@10", "MRR", "dialogue lines", "gold pairs"], rows), ""]
        L += ["## Rank of each expected event", ""]
        L += [md_table(["dialogue", "event", "NCD rank", "embedding rank", "event description"],
                       [[g["dialogue_id"], g["event"], g["ncd_rank"], g.get("embedding_rank", "–"),
                         short(g["event_description"], 70)] for g in gold_rows]), ""]
    s = result["order_sensitivity"]
    L += ["## Concatenation order (event-first vs dialogue-first)", "",
          f"- Mean top-{s['k']} overlap per dialogue line: {s['mean_topk_overlap_per_dialogue']:.2f}",
          f"- Overlap of the global top-{s['global_pairs']} pairs (what the game requests at share 0.5): "
          f"{s['global_pair_overlap']:.2f}",
          f"- Largest NCD difference between orders: {s['max_abs_ncd_diff']:.3f}", "",
          "## Top 5 per dialogue line", ""]
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
