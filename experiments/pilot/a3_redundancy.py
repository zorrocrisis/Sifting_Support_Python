"""
Pilot A3 -- redundancy control in CC.

  python -m experiments.pilot.a3_redundancy [--cap 2] [--lam 0.7] [--seed 42]

Compares four CC selectors at share 0.5, total 12, by composing the full pool
the way the game does (AC seed --seed):
  nearest  (current game behaviour), cap, mmr, cap+mmr

Per variant: distinct dialogue lines that contribute to the pool, CC
redundancy (mean pairwise 1-NCD between the CC events picked), and the pairs.

Pass: at least 3 of the relevant dialogue lines contribute. "Relevant" = the
dialogue lines that have gold matches in gold_matches.csv (handoff: "3 of the
4 relevant lines"); while the gold file is empty, the check uses any dialogue
line and is marked provisional.

Note: the game's composer counts the paired dialogue line itself against the
CC quota (round(total*share) = 6 here), so each new dialogue line costs two
slots. With quota 6, at most 3 distinct dialogue lines can contribute.

The "best" variant (used by A4/A5) is chosen by rule: among cap, mmr, cap+mmr,
the most contributing dialogue lines, then the lowest CC redundancy.

Outputs: a3_pairs.csv, a3_result.json, a3_report.md
"""

import argparse

from experiments.common import cc, paths
from experiments.common.context import PilotContext
from experiments.common.data import description_of
from experiments.common.gold import read_gold
from experiments.common.report import md_table, short, write_csv, write_json
from experiments.common.simulate import build_pool, pool_metrics
from experiments.pilot.make_gold_helper import GOLD_PATH


def pick_best(by_variant):
    candidates = [v for v in ("cap", "mmr", "cap+mmr") if v in by_variant]
    return max(candidates, key=lambda v: (by_variant[v]["dialogue_lines"],
                                          -(by_variant[v]["cc_redundancy"] or 0.0),
                                          -candidates.index(v)))


def run(cap=2, lam=0.7, seed=42, total=12, share=0.5):
    paths.ensure_out()
    ctx = PilotContext()
    gold, _ = read_gold(GOLD_PATH, ctx)
    relevant = set(gold)

    by_variant, rows, built_by = {}, [], {}
    for v in cc.VARIANTS:
        built = build_pool(ctx, share, total, variant=v, seed=seed, cap=cap, lam=lam)
        built_by[v] = built
        m = pool_metrics(ctx, built)
        contributing = {e["d"] for e in built["entries"] if e["kind"] == "dialogue"}
        m["contributing_dialogue_ids"] = sorted(ctx.dialogue_id(d) for d in contributing)
        m["requested_pairs_distinct_dialogue"] = len({p["d"] for p in built["pairs"]})
        if relevant:
            m["relevant_contributing"] = len(contributing & relevant)
        by_variant[v] = m
        for e in built["entries"]:
            if e["channel"] != "CC" or e["kind"] != "event":
                continue
            rows.append({"variant": v, "event": ctx.event_code(e["e"]),
                         "dialogue_id": ctx.dialogue_id(e["paired_d"]) if e["paired_d"] is not None else "",
                         "ncd": round(e["ncd"], 4) if e["ncd"] is not None else "",
                         "event_description": description_of(e["full"]),
                         "dialogue": ctx.dialogue.unique[e["paired_d"]] if e["paired_d"] is not None else ""})

    best = pick_best(by_variant)
    need = 3
    if relevant:
        ok = {v: by_variant[v]["relevant_contributing"] >= min(need, len(relevant)) for v in by_variant}
        provisional = False
    else:
        ok = {v: by_variant[v]["dialogue_lines"] >= need for v in by_variant}
        provisional = True
    status = "pass" if any(ok[v] for v in ("cap", "mmr", "cap+mmr")) else "fail"

    result = {"test": "A3", "cap": cap, "lambda": lam, "seed": seed, "total": total, "share": share,
              "variants": by_variant, "passes": ok, "best_variant": best,
              "relevant_dialogue_ids": sorted(ctx.dialogue_id(d) for d in relevant),
              "status": status + (" (provisional: no gold yet)" if provisional else ""),
              "pass_rule": f">= {need} relevant dialogue lines contribute (relevant = lines with gold matches)"}
    write_csv(paths.OUT_DIR / "a3_pairs.csv", rows)
    write_json(paths.OUT_DIR / "a3_result.json", result)

    L = ["# A3 — Redundancy control in CC", "",
         f"**Status: {result['status'].upper()}** — best variant by rule: `{best}`", "",
         f"Share {share}, total {total}, AC seed {seed}, cap {cap}, λ {lam}. Pass rule: {result['pass_rule']}.", "",
         "The game's composer counts each paired dialogue line against the CC quota, so a new dialogue line "
         f"costs two slots. At quota {round(total * share)}, at most {round(total * share) // 2} distinct "
         "dialogue lines can contribute, whatever the selector.", "",
         md_table(["variant", "dialogue lines in pool", "CC events", "CC redundancy", "pool redundancy",
                   "distinct dialogue in requested pairs", "passes"],
                  [[v, m["dialogue_lines"], m["n_cc_events"], m["cc_redundancy"], m["redundancy"],
                    m["requested_pairs_distinct_dialogue"], "yes" if ok[v] else "no"] for v, m in by_variant.items()]),
         ""]
    for v in cc.VARIANTS:
        L += [f"## `{v}` — CC events in the pool", "",
              md_table(["dialogue", "NCD", "event"],
                       [[r["dialogue_id"], r["ncd"], f"{r['event']} {short(r['event_description'], 70)}"]
                        for r in rows if r["variant"] == v]), ""]
    (paths.OUT_DIR / "a3_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cap", type=int, default=2)
    ap.add_argument("--lam", type=float, default=0.7)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    r = run(a.cap, a.lam, a.seed)
    print(f"A3: {r['status']}; best = {r['best_variant']}")
    for v, m in r["variants"].items():
        print(f"  {v:8s} dialogue lines {m['dialogue_lines']}  CC redundancy {m['cc_redundancy']:.3f}")


if __name__ == "__main__":
    main()
