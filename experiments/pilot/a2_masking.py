"""
Pilot A2 -- name masking.

  python -m experiments.pilot.a2_masking [--mask-pawn-ids] [--total 12 --share 0.5]

Re-runs the CC ranking with colonist names masked on both sides and compares
it with the unmasked ranking. Two masking modes:
  per_colonist -- the handoff's design: every spelling of one colonist -> the same
                  token (C1, C2, ...). Removes spelling differences (full name vs
                  nickname) but NCD can still match on *which* colonist is involved.
  single       -- every colonist -> "C". NCD can no longer match on identity at all.
  removed      -- names deleted outright. NCD can no longer see how many colonists a line names
                  (the "C ... C" shape that `single` keeps).

Per mode:
  - % of the top-k pairs that changed, k = CC slots at (share, total) = round(total*share)
  - actor-match rate before/after: share of top-k pairs whose dialogue and event
    mention at least one common colonist (detected on the unmasked text)
  - A1 metrics recomputed on masked text (if gold matches exist)
  - the pair lists, for the author to judge whether masked pairs are more on-topic

Interpretation (author's call, using the pair lists):
  most pairs change and become more on-topic  -> adopt masking
  most pairs change and become nonsense       -> names were the only signal
  pairs barely change                          -> names weren't driving the matches

Outputs: a2_pairs.csv, a2_result.json, a2_report.md
"""

import argparse

from experiments.common import cc, paths
from experiments.common.context import PilotContext
from experiments.common.gold import map_to_candidates, read_gold, retrieval_metrics
from experiments.common.pool import pipeline_targets
from experiments.common.report import md_table, short, write_csv, write_json

MODES = {"per_colonist": None, "single": "C", "removed": ""}


def actor_match_rate(ctx, pairs):
    if not pairs:
        return float("nan")
    hits = 0
    for p in pairs:
        a = ctx.masker.colonists_in(ctx.dialogue.unique[p["d"]])
        b = ctx.masker.colonists_in(ctx.events.unique[p["e"]])
        hits += bool(a & b)
    return hits / len(pairs)


def _key(p):
    return p["d"], p["e"]


def run(total=12, share=0.5, mask_pawn_ids=False, per_dialogue_k=5):
    paths.ensure_out()
    _, k = pipeline_targets(total, share)
    base = PilotContext()
    before = cc.select_nearest(base.M, k)
    gold = map_to_candidates(read_gold(paths.GOLD_PATH, base)[0], base)

    def orders(M):
        return {d: cc.rank_events(M[d]) for d in range(M.shape[0])}

    result = {"test": "A2", "k": k, "total": total, "share": share, "mask_pawn_ids": mask_pawn_ids,
              "masking_variants": base.masker.variants, "masking_ambiguous": base.masker.ambiguous,
              "actor_match_unmasked": actor_match_rate(base, before),
              "distinct_dialogue_lines_unmasked": len({p["d"] for p in before}),
              "a1_metrics_unmasked": retrieval_metrics(orders(base.M), gold)[1] if gold else None,
              "modes": {}, "status": "done (interpretation by author)"}

    rows = [{"ranking": "unmasked", "rank": r + 1, "dialogue_id": base.dialogue_id(p["d"]),
             "event": base.event_code(p["e"]), "ncd": round(p["ncd"], 4),
             "dialogue": base.dialogue.unique[p["d"]], "event_description": base.events.unique[p["e"]]}
            for r, p in enumerate(before)]
    after_by_mode = {}

    for mode, token in MODES.items():
        ctx = PilotContext(mask_pawn_ids=mask_pawn_ids, single_token=token)
        after = cc.select_nearest(ctx.M_masked, k)
        after_by_mode[mode] = (ctx, after)
        kept = {_key(p) for p in before} & {_key(p) for p in after}
        overlap = [len(set(cc.rank_events(base.M[d])[:per_dialogue_k]) &
                       set(cc.rank_events(ctx.M_masked[d])[:per_dialogue_k])) / per_dialogue_k
                   for d in range(len(base.dialogue))]
        result["modes"][mode] = {
            "pct_topk_pairs_changed": 1 - len(kept) / k if k else float("nan"),
            "actor_match_masked": actor_match_rate(ctx, after),
            f"mean_top{per_dialogue_k}_overlap_per_dialogue": sum(overlap) / len(overlap),
            "distinct_dialogue_lines_masked": len({p["d"] for p in after}),
            "a1_metrics_masked": retrieval_metrics(orders(ctx.M_masked), gold)[1] if gold else None,
            "example_masked": ctx.masked_dialogue[0],
        }
        for r, p in enumerate(after):
            rows.append({"ranking": f"masked_{mode}", "rank": r + 1, "dialogue_id": ctx.dialogue_id(p["d"]),
                         "event": ctx.event_code(p["e"]), "ncd": round(p["ncd"], 4),
                         "in_unmasked_topk": _key(p) in {_key(q) for q in before},
                         "dialogue": ctx.dialogue.unique[p["d"]], "event_description": ctx.events.unique[p["e"]],
                         "masked_dialogue": ctx.masked_dialogue[p["d"]], "masked_event": ctx.masked_events[p["e"]]})

    write_csv(paths.OUT_DIR / "a2_pairs.csv", rows,
              ["ranking", "rank", "dialogue_id", "event", "ncd", "in_unmasked_topk", "dialogue",
               "event_description", "masked_dialogue", "masked_event"])
    write_json(paths.OUT_DIR / "a2_result.json", result)
    write_report(base, result, before, after_by_mode, per_dialogue_k, gold)
    return result


def write_report(base, result, before, after_by_mode, per_dialogue_k, gold):
    k = result["k"]
    L = ["# A2 — Name masking", "",
         f"k = {k} CC slots (total {result['total']}, share {result['share']}). "
         "Names masked on both sides" + (", pawn IDs too" if result["mask_pawn_ids"] else "") + ".", "",
         "- `per_colonist`: each colonist gets their own token (C1, C2, …), as specified in the handoff. "
         "NCD can still match on which colonist is involved.",
         "- `single`: every colonist becomes `C`. NCD can't match on identity at all.",
         "- `removed`: names are deleted. NCD can't see how many colonists a line names either.", ""]
    hdr = ["metric", "unmasked"] + list(result["modes"])
    m = result["modes"]
    L += [md_table(hdr, [
        ["top-k pairs changed vs unmasked", "–"] + [f"{m[x]['pct_topk_pairs_changed']:.0%}" for x in m],
        ["actor-match rate in top-k", f"{result['actor_match_unmasked']:.0%}"]
        + [f"{m[x]['actor_match_masked']:.0%}" for x in m],
        [f"mean top-{per_dialogue_k} overlap per dialogue line", "1.00"]
        + [f"{m[x][f'mean_top{per_dialogue_k}_overlap_per_dialogue']:.2f}" for x in m],
        ["distinct dialogue lines in top-k", result["distinct_dialogue_lines_unmasked"]]
        + [m[x]["distinct_dialogue_lines_masked"] for x in m],
    ]), ""]
    if gold:
        rows = [["unmasked", *(result["a1_metrics_unmasked"][c] for c in ("recall@5", "recall@10", "mrr"))]]
        rows += [[x, *(m[x]["a1_metrics_masked"][c] for c in ("recall@5", "recall@10", "mrr"))] for x in m]
        L += ["## A1 metrics on masked text", "", md_table(["text", "Recall@5", "Recall@10", "MRR"], rows), ""]
    else:
        L += ["A1 metrics on masked text: pending gold matches.", ""]

    lists = [("Unmasked", base, before)] + [(f"Masked ({x})", c, a) for x, (c, a) in after_by_mode.items()]
    before_keys = {_key(p) for p in before}
    for name, ctx, pairs in lists:
        L += [f"## {name} top-{k} pairs", "",
              md_table(["#", "NCD", "dialogue", "event", "also unmasked"],
                       [[r + 1, p["ncd"], f"{ctx.dialogue_id(p['d'])} {short(ctx.dialogue.unique[p['d']], 55)}",
                         f"{ctx.event_code(p['e'])} {short(ctx.events.unique[p['e']], 55)}",
                         "yes" if _key(p) in before_keys else ""] for r, p in enumerate(pairs)]), ""]
    L += ["## Interpretation (for the author)", "",
          "- Most pairs change and become more on-topic → adopt masking.",
          "- Most pairs change and become nonsense → names were the only signal.",
          "- Pairs barely change → names weren't driving the matches.", ""]
    (paths.OUT_DIR / "a2_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--total", type=int, default=12)
    ap.add_argument("--share", type=float, default=0.5)
    ap.add_argument("--mask-pawn-ids", action="store_true")
    a = ap.parse_args()
    r = run(a.total, a.share, a.mask_pawn_ids)
    for mode, v in r["modes"].items():
        print(f"A2 [{mode}]: {v['pct_topk_pairs_changed']:.0%} of top-{r['k']} pairs changed; "
              f"actor match {r['actor_match_unmasked']:.0%} -> {v['actor_match_masked']:.0%}")


if __name__ == "__main__":
    main()
