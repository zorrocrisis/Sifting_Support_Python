"""
Compare four CC set-ups: two reference sets (session-1 dialogue, session-1 AC-selected
logs) x two CC candidate sets (all 162 session-2 events, or only the 43 cluster
representatives the AC keeps after filtering at NCD threshold 0.5).

NCD only: embeddings are left out on purpose (they depend on a model trained on
general English, which hurts domain generalisation). A2 (masking) is not repeated.

  python -m experiments.pilot.run_all --reference dialogue    --cc-candidates all      --skip-generation
  python -m experiments.pilot.run_all --reference dialogue    --cc-candidates filtered --skip-generation
  python -m experiments.pilot.run_all --reference s1_selected --cc-candidates all      --skip-generation
  python -m experiments.pilot.run_all --reference s1_selected --cc-candidates filtered --skip-generation
  python -m experiments.pilot.compare_candidates

Reads each run's result files and writes
experiments/pilot/out_compare/CANDIDATE_FILTER_COMPARISON.md plus a plot. Recomputes nothing.
"""

import csv
import json

from experiments.common import paths
from experiments.common.report import md_table, read_json, short

OUT = paths.PILOT_DIR / "out_compare"
RUNS = [  # key, reference, candidates, folder, label
    ("dlg_all", "dialogue", "all", "out", "dialogue · 162 events"),
    ("dlg_flt", "dialogue", "filtered", "out_filtered", "dialogue · 43 events (filtered)"),
    ("s1_all", "s1_selected", "all", "out_s1_selected", "selected logs · 162 events"),
    ("s1_flt", "s1_selected", "filtered", "out_s1_selected_filtered", "selected logs · 43 events (filtered)"),
]


def f2(x):
    return "–" if x is None else f"{x:.2f}"


def load(folder):
    out = paths.PILOT_DIR / folder
    r = {k: read_json(out / f"{k}_result.json") for k in ("a1", "a3", "a4")}
    missing = [k for k, v in r.items() if v is None]
    if missing:
        raise SystemExit(f"{folder}: missing {missing}; run that configuration first")
    with open(out / "a1_gold_ranks.csv", encoding="utf-8") as f:
        r["gold_ranks"] = list(csv.DictReader(f))
    with open(out / "a4_pools.jsonl", encoding="utf-8") as f:
        r["pools"] = [json.loads(l) for l in f]
    return r


def best_rank_per_line(d):
    best, text = {}, {}
    for g in d["gold_ranks"]:
        best[g["dialogue_id"]] = min(best.get(g["dialogue_id"], 10**9), int(g["ncd_rank"]))
        text[g["dialogue_id"]] = g["dialogue"]
    return best, text


def pool_rows(d, variant, share=0.5, seed=42):
    for p in d["pools"]:
        if p["variant"] == variant and p["share"] == share and p["seed"] == seed:
            out = []
            for e in sorted(p["entries"], key=lambda e: int(e["full"].split("Timestamp_")[1].split("_")[0])):
                ref = e["kind"] in ("reference", "dialogue")
                out.append([e["channel"] + (" (ref)" if ref else ""), short(e["full"].split("FullInfo_", 1)[1], 85)])
            return out
    return None


def plot(data):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    metrics = [("distinct_topics", "distinct topics"), ("distinct_topics_primary", "distinct topics (first label)"),
               ("redundancy", "pool redundancy (mean 1−NCD)")]
    style = {"dlg_all": ("#2f6db5", "-"), "dlg_flt": ("#2f6db5", "--"),
             "s1_all": ("#c4612f", "-"), "s1_flt": ("#c4612f", "--")}
    fig, axes = plt.subplots(1, len(metrics), figsize=(4.4 * len(metrics), 3.5))
    for ax, (m, title) in zip(axes, metrics):
        for key, _, _, _, label in RUNS:
            ps = data[key]["a4"]["summary"]["nearest"]["per_share"]
            xs = [float(s) for s in ps if ps[s][m]["mean"] is not None]
            ys = [ps[s][m]["mean"] for s in ps if ps[s][m]["mean"] is not None]
            err = [ps[s][m]["std"] for s in ps if ps[s][m]["mean"] is not None]
            color, ls = style[key]
            ax.errorbar(xs, ys, yerr=err, marker="o", capsize=3, color=color, linestyle=ls, label=label)
        ax.set_title(title)
        ax.set_xlabel("reference_share")
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
    axes[0].legend(fontsize=7.5)
    fig.suptitle("CC variant `nearest` (the game's current selector)", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "candidate_filter_comparison.png", dpi=130)
    plt.close(fig)


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    data = {key: load(folder) for key, _, _, folder, _ in RUNS}
    label = {key: lab for key, _, _, _, lab in RUNS}
    keys = [k for k, *_ in RUNS]

    def a1(k, m="recall@5"):
        return data[k]["a1"]["metrics"]["ncd"][m]

    def a3(k, v, m):
        return data[k]["a3"]["variants"][v][m]

    def a4rho(k, v, primary=False):
        s = data[k]["a4"]["summary"].get(v)
        return None if s is None else s["spearman_share_topics_primary" if primary else "spearman_share_topics"]

    L = ["# CC candidates: all 162 session-2 events vs the 43 the AC keeps after filtering", "",
         "Four set-ups, crossing two **reference sets** (what the CC matches against) with two **candidate sets** "
         "(which session-2 events the CC may pick). Everything else is identical: session 2 = `SimulatedDay2` "
         "(162 distinct events), AC at NCD threshold 0.5 with `least_frequent`, NCD event-first as in the game, "
         "the game's pool composer, total 12.", "",
         "**Filtered candidates** = the AC's `unique_logs_after_filtering` at threshold 0.5: one representative "
         "(medoid) per cluster of near-duplicate events, taken before dendrogram traversal. In A1 a gold event "
         "folded into a cluster counts as found when its representative is retrieved, so several gold events can "
         "become one target.", "",
         "NCD only. Embeddings are left out on purpose, and A2 (name masking) is not repeated here; see "
         "`REFERENCE_COMPARISON.md` for both.", "",
         md_table(["", *[label[k] for k in keys]], [
             ["reference lines", *[data[k]["a1"]["n_dialogue"] for k in keys]],
             ["CC candidates", *[data[k]["a1"].get("n_candidates", 162) for k in keys]],
             ["gold events (author)", *[data[k]["a1"].get("n_gold_pairs_original", "–") for k in keys]],
             ["gold targets after mapping to representatives",
              *[data[k]["a1"]["metrics"]["ncd"]["n_gold_pairs"] for k in keys]],
             ["gold events that are candidates themselves",
              *[data[k]["a1"].get("n_gold_events_that_are_candidates", "–") for k in keys]],
         ]), ""]

    # --- At a glance ----------------------------------------------------------------
    best = {k: data[k]["a3"]["best_variant"] for k in keys}
    L += ["## At a glance", "",
          md_table(["", *[label[k] for k in keys]], [
              ["A1 NCD Recall@5 (pass ≥ 0.5)", *[f2(a1(k)) for k in keys]],
              ["A1 NCD MRR", *[f2(a1(k, "mrr")) for k in keys]],
              ["A3 `nearest`: reference lines in pool", *[a3(k, "nearest", "dialogue_lines") for k in keys]],
              ["A3 `nearest`: CC redundancy", *[f2(a3(k, "nearest", "cc_redundancy")) for k in keys]],
              ["A3 `mmr`: CC redundancy", *[f2(a3(k, "mmr", "cc_redundancy")) for k in keys]],
              ["A4 ρ(share, topics), `nearest` (pass ≤ −0.7)", *[f2(a4rho(k, "nearest")) for k in keys]],
              ["A4 same, first label only", *[f2(a4rho(k, "nearest", True)) for k in keys]],
          ]), "",
          "With embeddings out of the picture, A1 is NCD's alone, and it fails in all four set-ups; the best is "
          f"selected logs with filtered candidates ({f2(a1('s1_flt'))}).", ""]

    # --- A1 ---------------------------------------------------------------------------
    rows = []
    for k in keys:
        m = data[k]["a1"]["metrics"]["ncd"]
        rows.append([label[k], m["recall@5"], m["recall@10"], m["mrr"], m["n_gold_pairs"]])
        x = (data[k]["a1"].get("metrics_without_exact_repeats") or {}).get("ncd")
        if x:
            rows.append([f"{label[k]}, no exact repeats", x["recall@5"], x["recall@10"], x["mrr"], x["n_gold_pairs"]])
    L += ["## A1 — does NCD find the events the author says continue a reference line?", "",
          md_table(["set-up", "Recall@5", "Recall@10", "MRR", "gold targets"], rows), "",
          "Each reference set has its own gold file, so compare the two candidate sets *within* a reference set; "
          "across reference sets the numbers say how findable each kind of continuity is, not the same items.", ""]

    for ref_keys, ref_name in ((("dlg_all", "dlg_flt"), "dialogue"), (("s1_all", "s1_flt"), "selected logs")):
        (ba, text), (bf, _) = best_rank_per_line(data[ref_keys[0]]), best_rank_per_line(data[ref_keys[1]])
        L += [f"NCD rank of the best-ranked gold event per reference line, {ref_name} "
              "(lower is better; filtered ranks are out of 43 candidates, unfiltered out of 162):", "",
              md_table(["line", "reference text", "162 events", "43 events"],
                       [[i, short(text[i], 72), ba[i], bf.get(i, "–")] for i in ba]), ""]

    L += ["- **Dialogue:** filtering moves NCD's hits down from the very top but brings more into the top 10 "
          f"(Recall@5 {f2(a1('dlg_all'))} → {f2(a1('dlg_flt'))}, Recall@10 {f2(a1('dlg_all', 'recall@10'))} → "
          f"{f2(a1('dlg_flt', 'recall@10'))}, MRR {f2(a1('dlg_all', 'mrr'))} → {f2(a1('dlg_flt', 'mrr'))}). "
          "The lines NCD matched best before (walrus, Papyrus/Stockpile) drop a few places, because the events they "
          "matched are not representatives and their representatives share less wording. The lines it matched worst "
          "move up, but only because there are fewer candidates to rank.",
          "- **Selected logs:** filtering helps NCD (Recall@5 "
          f"{f2(a1('s1_all'))} → {f2(a1('s1_flt'))}), but partly by construction: several gold events merge into "
          "one target, and the exact repeats mostly drop out of the candidates (e.g. *grizzly bear standing* is "
          "represented by *grizzly bear wandering*).", ""]

    # --- A3 ---------------------------------------------------------------------------
    variants = list(data["dlg_all"]["a3"]["variants"])
    rows = [[v, *[f"{a3(k, v, 'dialogue_lines')} / {f2(a3(k, v, 'cc_redundancy'))}" for k in keys]] for v in variants]
    L += ["## A3 — redundancy in what the CC picks (share 0.5, total 12)", "",
          "Each cell: reference lines in the pool / CC redundancy (mean 1−NCD over all pairs of CC events).", "",
          md_table(["variant", *[label[k] for k in keys]], rows), "",
          "- **Dialogue:** filtering alone does part of what MMR did: `nearest` goes from 1 reference line and "
          f"redundancy {f2(a3('dlg_all', 'nearest', 'cc_redundancy'))} to 3 lines and "
          f"{f2(a3('dlg_flt', 'nearest', 'cc_redundancy'))} (MMR on all events: "
          f"{f2(a3('dlg_all', 'mmr', 'cc_redundancy'))}), because the 13 near-identical fight lines collapse to "
          "2 representatives. Filtering plus MMR gives the lowest redundancy "
          f"({f2(a3('dlg_flt', 'mmr', 'cc_redundancy'))}).",
          "- **Selected logs:** redundancy was already low and stays so; every variant picks 3 different reference "
          "lines in both candidate sets, so cap and MMR have nothing to fix.", ""]

    # --- A4 ---------------------------------------------------------------------------
    L += ["## A4 — is the share a breadth/depth dial?", "",
          "![comparison](candidate_filter_comparison.png)", "",
          md_table(["set-up", "variant", "ρ(share, topics)", "first label only", "ρ(share, redundancy)", "passes"],
                   [[label[k], v, f2(s["spearman_share_topics"]), f2(s["spearman_share_topics_primary"]),
                     f2(s["spearman_share_redundancy"]), "yes" if s["passes"] else "no"]
                    for k in keys for v, s in data[k]["a4"]["summary"].items()]), ""]
    for k in keys:
        ps = data[k]["a4"]["summary"]["nearest"]["per_share"]
        L += [f"`{label[k]}` · `nearest`", "",
              md_table(["share", "distinct topics", "first label", "redundancy", "reference lines", "AC–CC overlap"],
                       [[sh, f2(ps[sh]["distinct_topics"]["mean"]), f2(ps[sh]["distinct_topics_primary"]["mean"]),
                         f2(ps[sh]["redundancy"]["mean"]), f2(ps[sh]["dialogue_lines"]["mean"]),
                         f2(ps[sh]["ac_cc_overlap"]["mean"])] for sh in ps]), ""]
    L += ["All four pass the agreed rule (multi-topic tags count every topic). Only the selected-log set-ups also "
          "pass when each tag counts as its first topic; with dialogue the drop in topics rests on the multi-topic "
          "\"watching for targets\" tags in either candidate set, and with filtered candidates the topic count "
          "is not even monotone (9 at share 0.25). Filtering lowers pool redundancy at every share above 0 for "
          "dialogue. For selected logs it cuts the descriptions that appear twice in the pool from 3 to 1: "
          "*Papyrus following Stench* is itself a representative, so its session-2 copy can still be picked "
          "next to the session-1 line.", ""]

    # --- Pools ------------------------------------------------------------------------
    L += ["## The pool at share 0.5 (seed 42), as the LLM would see it", ""]
    for k in keys:
        for v in ("nearest", "mmr"):
            rows = pool_rows(data[k], v)
            if rows is not None:
                L += [f"`{label[k]}` · `{v}`", "", md_table(["channel", "description"], rows), ""]

    # --- Reading ----------------------------------------------------------------------
    L += ["## Reading", "",
          "- **Filtering the candidates fixes the redundancy problem it was meant to fix.** With dialogue, the "
          "blow-by-blow fight lines can no longer take every CC slot, even with the game's current `nearest` "
          "selector. It reuses the AC's own clustering, so no new mechanism is needed.",
          "- **It doesn't make NCD better at finding continuity with dialogue.** NCD still can't connect "
          "paraphrased dialogue to events, and with fewer candidates its few top-5 hits slip to ranks 6–10.",
          "- **With selected logs, filtering and the event reference work well together.** Fewer duplicates in the "
          "pool (1 instead of 3), NCD's best A1 score of the four, and a clean dial in A4 under both readings, "
          "slightly weaker than with all events (ρ −0.90 vs −0.96). NCD still falls short of the A1 threshold.",
          "- **Filtering also changes what counts as a match.** The CC now returns a cluster's representative, not "
          "the specific event, so its precision can't exceed the AC's clustering at 0.5.", "",
          "## Caveats", "",
          "- One colony, two sessions, 8 and 13 reference lines, single author's gold and tags.",
          "- The filtered A1 credits a representative for its whole cluster; a stricter reading (only exact gold "
          "events count) would score the filtered set-ups lower.",
          "- Reference lines count against the CC quota, so at share 0.5 at most 3 can contribute.",
          "- Seeds only affect the AC and barely change it, so the ± over seeds understates variability.",
          "- The medoids used as CC candidates are fixed with seed 42; the AC re-picks medoids per seed, which "
          "only matters for 2-event clusters.", ""]

    (OUT / "CANDIDATE_FILTER_COMPARISON.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    plot(data)
    return OUT / "CANDIDATE_FILTER_COMPARISON.md"


if __name__ == "__main__":
    print(f"Wrote {run()}")
