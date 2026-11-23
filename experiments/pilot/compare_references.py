"""
Compare the pilot results for two CC reference sets: session-1 dialogue vs the
logs the AC selected in session 1.

  python -m experiments.pilot.run_all --reference dialogue    --skip-generation --skip-masking
  python -m experiments.pilot.run_all --reference s1_selected --skip-generation --skip-masking
  python -m experiments.pilot.compare_references

Reads the result files each run wrote (out/ and out_s1_selected/) and writes
experiments/pilot/out_compare/REFERENCE_COMPARISON.md plus a plot. Recomputes
nothing; run both references first.
"""

import csv
import json

from experiments.common import paths
from experiments.common.report import md_table, read_json, short

REFS = {"dialogue": "Session-1 dialogue", "s1_selected": "Session-1 AC-selected logs"}
OUT = paths.PILOT_DIR / "out_compare"


def load(ref):
    out = paths.REFERENCES[ref]["out"]
    r = {k: read_json(out / f"{k}_result.json") for k in ("a1", "a2", "a3", "a4")}
    r["out"] = out
    r["gold_ranks"] = list(csv.DictReader(open(out / "a1_gold_ranks.csv", encoding="utf-8"))) \
        if (out / "a1_gold_ranks.csv").exists() else []
    r["pools"] = [json.loads(l) for l in open(out / "a4_pools.jsonl", encoding="utf-8")] \
        if (out / "a4_pools.jsonl").exists() else []
    missing = [k for k in ("a1", "a3", "a4") if r[k] is None]
    if missing:
        raise SystemExit(f"{ref}: missing {missing}; run run_all --reference {ref} first")
    return r


def f2(x):
    return "–" if x is None else f"{x:.2f}"


def a3_best(d):
    vs = d["a3"]["variants"].values()
    tie = len({(m["dialogue_lines"], round(m["cc_redundancy"] or 0, 6)) for m in vs}) == 1
    return f"`{d['a3']['best_variant']}`" + (" (all variants tie)" if tie else "")


def plot(data):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    metrics = [("distinct_topics", "distinct topics"), ("redundancy", "redundancy (mean 1−NCD)"),
               ("dialogue_lines", "reference lines in pool")]
    fig, axes = plt.subplots(1, len(metrics), figsize=(4.2 * len(metrics), 3.4))
    colors = {"dialogue": "#2f6db5", "s1_selected": "#c4612f"}
    for ax, (m, title) in zip(axes, metrics):
        for ref, d in data.items():
            for v in d["a4"]["variants"]:
                ps = d["a4"]["summary"][v]["per_share"]
                xs = [float(s) for s in ps if ps[s][m]["mean"] is not None]
                ys = [ps[s][m]["mean"] for s in ps if ps[s][m]["mean"] is not None]
                err = [ps[s][m]["std"] for s in ps if ps[s][m]["mean"] is not None]
                ax.errorbar(xs, ys, yerr=err, marker="o", capsize=3, color=colors[ref],
                            linestyle="-" if v == "nearest" else "--", label=f"{ref} · {v}")
        ax.set_title(title)
        ax.set_xlabel("reference_share")
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "reference_comparison.png", dpi=130)
    plt.close(fig)


def pool_example(d, variant="nearest", share=0.5, seed=42):
    for p in d["pools"]:
        if p["variant"] == variant and p["share"] == share and p["seed"] == seed:
            rows = []
            for e in sorted(p["entries"], key=lambda e: int(e["full"].split("Timestamp_")[1].split("_")[0])):
                kind = "reference" if e["kind"] in ("reference", "dialogue") else "event"
                rows.append([e["channel"] + (" (ref)" if kind == "reference" else ""),
                             short(e["full"].split("FullInfo_", 1)[1], 85)])
            return rows
    return []


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    data = {ref: load(ref) for ref in REFS}
    dg, s1 = data["dialogue"], data["s1_selected"]
    L = ["# CC reference sets compared: session-1 dialogue vs session-1 selected logs", "",
         "Same session 2 (`SimulatedDay2`, 162 distinct events), same AC (threshold 0.5, `least_frequent`), "
         "same NCD order (event first, as in the game), same composer (port of the game's, total 12). "
         "Only the CC reference set changes:", "",
         md_table(["", "dialogue", "s1_selected"], [
             ["what", "lines colonists spoke in session 1", "the 13 logs the AC picked in session 1"],
             ["file", "`SimulatedDay2/dialogue_logs.txt`", "`SimulatedDay1/selected_reference_logs.txt`"],
             ["reference lines", dg["a1"]["n_dialogue"], s1["a1"]["n_dialogue"]],
             ["gold pairs (author)", dg["a1"]["metrics"]["ncd"]["n_gold_pairs"], s1["a1"]["metrics"]["ncd"]["n_gold_pairs"]],
             ["gold pairs that are exact repeats", dg["a1"].get("n_exact_repeat_gold_pairs", 0),
              s1["a1"].get("n_exact_repeat_gold_pairs", 0)],
         ]), ""]

    # --- Summary -----------------------------------------------------------
    def a4_line(d):
        return "; ".join(f"`{v}` ρ {f2(s['spearman_share_topics'])} (first label {f2(s['spearman_share_topics_primary'])})"
                         for v, s in d["a4"]["summary"].items())
    L += ["## At a glance", "",
          md_table(["test", "dialogue", "s1_selected"], [
              ["A1 NCD Recall@5 (pass ≥ 0.5)", f2(dg["a1"]["metrics"]["ncd"]["recall@5"]), f2(s1["a1"]["metrics"]["ncd"]["recall@5"])],
              ["A1 embedding Recall@5", f2(dg["a1"]["metrics"]["embedding"]["recall@5"]), f2(s1["a1"]["metrics"]["embedding"]["recall@5"])],
              ["A1 verdict", "fail (both methods)" if not dg["a1"].get("embedding_passes") else "NCD fails, embeddings pass",
               "fail (both methods)" if not s1["a1"].get("embedding_passes") else "NCD fails, embeddings pass"],
              ["A3 best variant", a3_best(dg), a3_best(s1)],
              ["A4 ρ(share, topics) (pass ≤ −0.7)", a4_line(dg), a4_line(s1)],
              ["Decision rule", "both A1 methods fail → rethink CC", "NCD fails only → commit with embedding-based CC"],
          ]), ""]

    # --- A1 ----------------------------------------------------------------
    rows = []
    for ref, d in data.items():
        for m in ("ncd", "embedding"):
            v = d["a1"]["metrics"][m]
            rows.append([ref, m, v["recall@5"], v["recall@10"], v["mrr"]])
        if d["a1"].get("metrics_without_exact_repeats"):
            for m in ("ncd", "embedding"):
                v = d["a1"]["metrics_without_exact_repeats"][m]
                rows.append([f"{ref}, no exact repeats", m, v["recall@5"], v["recall@10"], v["mrr"]])
    L += ["## A1 — does the CC find what the author says continues?", "",
          md_table(["reference", "method", "Recall@5", "Recall@10", "MRR"], rows), "",
          "The two gold sets were written separately for different reference lines, so the numbers compare "
          "how findable each kind of continuity is, not the same items.", ""]

    def best_rank(d, col):
        by_line = {}
        for g in d["gold_ranks"]:
            r = int(g[col])
            by_line[g["dialogue_id"]] = min(by_line.get(g["dialogue_id"], 10**9), r)
        return by_line

    for ref, d in data.items():
        n, e = best_rank(d, "ncd_rank"), best_rank(d, "embedding_rank")
        texts = {g["dialogue_id"]: g["dialogue"] for g in d["gold_ranks"]}
        L += [f"Best-ranked gold event per reference line, `{ref}`:", "",
              md_table(["line", "reference text", "NCD", "embedding"],
                       [[k, short(texts[k], 70), n[k], e[k]] for k in n]), ""]

    s = {ref: d["a1"]["order_sensitivity"] for ref, d in data.items()}
    L += ["**NCD concatenation order** (event-first vs dialogue-first): mean top-5 overlap per reference line "
          f"{s['dialogue']['mean_topk_overlap_per_dialogue']:.0%} with dialogue vs "
          f"{s['s1_selected']['mean_topk_overlap_per_dialogue']:.0%} with selected logs. Short event lines against "
          "event lines are much less sensitive to the order than dialogue against events.", ""]

    # --- A2 ----------------------------------------------------------------
    if dg["a2"] and s1["a2"]:
        rows = []
        for ref, d in data.items():
            a2 = d["a2"]
            un = a2.get("a1_metrics_unmasked") or {}
            rows.append([ref, "unmasked", "–", f"{a2['actor_match_unmasked']:.0%}", "1.00",
                         f2(un.get("recall@5")), f2(un.get("mrr"))])
            for mode, v in a2["modes"].items():
                m = v.get("a1_metrics_masked") or {}
                rows.append([ref, mode, f"{v['pct_topk_pairs_changed']:.0%}", f"{v['actor_match_masked']:.0%}",
                             f2(v["mean_top5_overlap_per_dialogue"]), f2(m.get("recall@5")), f2(m.get("mrr"))])
        L += ["## A2 — does NCD match on names?", "",
              f"Colonist names masked on both sides; top-k = {dg['a2']['k']} CC slots (share 0.5, total 12). "
              "`per_colonist`: each colonist becomes their own token (C1, C2, …). `single`: every colonist becomes `C`. `removed`: names are deleted, so the two-person \"C … C\" shape is gone too.", "",
              md_table(["reference", "masking", "top-k pairs changed", "actor match in top-k",
                        "top-5 overlap per line", "NCD Recall@5", "NCD MRR"], rows), "",
              "With dialogue, masking reshuffles the top pairs (most change) but they are still mostly the "
              "Odette–Stench fight lines, and retrieval of the gold events doesn't improve: names steer which events win, "
              "but removing them doesn't reveal the intended matches. With selected logs, the top pairs don't change "
              "at all: they are exact or near-exact repeats, which match with or without names. Deeper in the "
              "ranking about a third of each line's top 5 still changes, without moving Recall@5.", "",
              "Removing the names outright (`removed`) gives about the same picture as `single` for dialogue: the "
              "top pairs still share a colonist with the reference line, so the two-person \"C … C\" shape wasn't what "
              "kept them there. Some masked pairs move on-topic (the walrus shot → the rifle-shot lines; Papyrus to "
              "Stockpile One → hauling to Stockpile zone 1). Note that 41% of all dialogue × event combinations share "
              "a colonist by chance, mostly Stench, so a high actor match is weaker evidence than it looks.", "",
              "Interpreting the masked pairs (on-topic / nonsense / unchanged) is still on hold for the author; "
              "the pair lists are in each run's `a2_report.md`.", ""]

    # --- A3 ----------------------------------------------------------------
    rows = []
    for v in dg["a3"]["variants"]:
        a, b = dg["a3"]["variants"][v], s1["a3"]["variants"][v]
        rows.append([v, a["dialogue_lines"], f2(a["cc_redundancy"]), b["dialogue_lines"], f2(b["cc_redundancy"])])
    L += ["## A3 — redundancy control (share 0.5, total 12)", "",
          md_table(["variant", "dialogue: ref lines", "dialogue: CC redundancy",
                    "s1_selected: ref lines", "s1_selected: CC redundancy"], rows), "",
          "With dialogue, `nearest` lets one line (S110) take every CC slot with near-duplicate fight lines, and "
          "MMR spreads the slots over 3 lines. With selected logs, every variant already picks 3 different lines: "
          "each reference line's best match is an exact or near-exact repeat with NCD below 0.1, far ahead of "
          "everything else, so there is nothing for cap or MMR to fix.", ""]

    # --- A4 ----------------------------------------------------------------
    L += ["## A4 — is the share a breadth/depth dial?", "", "![comparison](reference_comparison.png)", ""]
    for ref, d in data.items():
        for v in d["a4"]["variants"]:
            ps = d["a4"]["summary"][v]["per_share"]
            L += [f"`{ref}` · `{v}`", "",
                  md_table(["share", "distinct topics", "first-label topics", "redundancy", "ref lines", "AC–CC overlap"],
                           [[sh, f2(ps[sh]["distinct_topics"]["mean"]), f2(ps[sh]["distinct_topics_primary"]["mean"]),
                             f2(ps[sh]["redundancy"]["mean"]), f2(ps[sh]["dialogue_lines"]["mean"]),
                             f2(ps[sh]["ac_cc_overlap"]["mean"])] for sh in ps]), ""]
    L += ["With dialogue, the topic count is flat up to share 0.5 and its drop rests on the multi-topic "
          "\"watching for targets\" tags; counting first labels only, it fails. With selected logs it falls steadily "
          "under both readings. In both, redundancy rises steadily with share (ρ ≈ 0.99).", "",
          f"**AC–CC overlap** (CC candidate events that the AC also returned) at share 0.5 with `nearest`: "
          f"{f2(dg['a4']['summary']['nearest']['per_share']['0.5']['ac_cc_overlap']['mean'])} with dialogue vs "
          f"{f2(s1['a4']['summary']['nearest']['per_share']['0.5']['ac_cc_overlap']['mean'])} with selected logs. "
          "With dialogue the channels only overlap once MMR pushes the CC away from the fight lines.", ""]

    # --- Example pools -------------------------------------------------------
    L += ["## The pool at share 0.5 (`nearest`, seed 42), as the LLM would see it", ""]
    for ref, d in data.items():
        L += [f"`{ref}`", "", md_table(["channel", "description"], pool_example(d)), ""]
    L += ["With selected logs, half the pool is three descriptions written twice: each session-1 log and its exact "
          "session-2 repeat both enter, because the game's composer removes duplicates by `_ID_`, not by text. "
          "The in-game F11 would do the same with this reference file.", ""]

    # --- Reading ---------------------------------------------------------------
    r5 = lambda d, m: f2(d["a1"]["metrics"][m]["recall@5"])                                    # noqa: E731
    r5x = lambda d, m: f2((d["a1"].get("metrics_without_exact_repeats") or {}).get(m, {}).get("recall@5"))  # noqa: E731
    L += ["## Reading", "",
          "- **Selected logs are easier to match, but much of what's matched is repetition.** Embeddings reach "
          f"Recall@5 {r5(s1, 'embedding')} with selected logs ({r5x(s1, 'embedding')} without exact repeats) and "
          f"{r5(dg, 'embedding')} with dialogue. NCD fails with both; with selected logs it mostly finds exact or "
          f"near-exact repeats ({r5(s1, 'ncd')}, falling to {r5x(s1, 'ncd')} without them).",
          "- **Dialogue continuity is the harder and more interesting signal.** The dialogue lines paraphrase "
          "events (\"I watched the far treeline for more raiders\"), so neither method connects them to "
          "session-2 events reliably; NCD falls back to matching colonist names.",
          "- **The dial works more cleanly with selected logs**, but partly because the CC fills the pool with "
          "repeats of topics the AC already covers (animals, hauling), which lowers breadth by construction.",
          "- **The CC mechanics differ with the reference.** Redundancy control matters for dialogue and is moot "
          "for selected logs; deduplicating by text would matter for selected logs and is moot for dialogue.",
          "",
          "## Caveats", "",
          "- One colony, two sessions, 8 and 13 reference lines: very small samples, single author's gold and tags.",
          "- Reference lines count against the CC quota, so at share 0.5 at most 3 can contribute in either set.",
          "- Selected-log reference lines carry count `[x1]`: the session-1 counts (e.g. `[x179]` for the grizzly) "
          "were dropped when the file was written.",
          "- Seeds only affect the AC and barely change it, so the ± over seeds understates variability.", ""]
    (OUT / "REFERENCE_COMPARISON.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    plot(data)
    return OUT / "REFERENCE_COMPARISON.md"


if __name__ == "__main__":
    print(f"Wrote {run()}")
