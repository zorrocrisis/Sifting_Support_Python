"""
Compare the CC's similarity measure: NCD (the game's) vs event indexing (entities,
place, log type and NCD text; see experiments/common/event_index.py), across the four
set-ups of CANDIDATE_FILTER_COMPARISON.md (dialogue / selected logs x 162 / 43 events).

No embeddings, no A2. Run the eight configurations first, e.g.

  python -m experiments.pilot.run_all --reference dialogue --cc-candidates all --cc-similarity index --no-embeddings --skip-generation

then  python -m experiments.pilot.compare_similarity

Writes experiments/pilot/out_compare/EVENT_INDEX_COMPARISON.md plus a plot. Recomputes nothing.
"""

import csv
import json

from experiments.common import paths
from experiments.common.report import md_table, read_json, short

OUT = paths.PILOT_DIR / "out_compare"
SETUPS = [  # key, label, NCD folder, index folder
    ("dlg_all", "dialogue · 162 events", "out", "out_index"),
    ("dlg_flt", "dialogue · 43 events", "out_filtered", "out_filtered_index"),
    ("s1_all", "selected logs · 162 events", "out_s1_selected", "out_s1_selected_index"),
    ("s1_flt", "selected logs · 43 events", "out_s1_selected_filtered", "out_s1_selected_filtered_index"),
]
SIMS = ("ncd", "index")


def f2(x):
    return "–" if x is None else f"{x:.2f}"


def load(folder):
    out = paths.PILOT_DIR / folder
    r = {k: read_json(out / f"{k}_result.json") for k in ("a1", "a3", "a4")}
    missing = [k for k, v in r.items() if v is None]
    if missing:
        raise SystemExit(f"{folder}: missing {missing}; run that configuration first")
    r["cc"] = r["a1"].get("cc_method", "ncd")
    with open(out / "a1_gold_ranks.csv", encoding="utf-8") as f:
        r["gold_ranks"] = list(csv.DictReader(f))
    with open(out / "a4_pools.jsonl", encoding="utf-8") as f:
        r["pools"] = [json.loads(l) for l in f]
    return r


def a1m(d, m="recall@5", no_exact=False):
    src = d["a1"].get("metrics_without_exact_repeats") if no_exact else d["a1"]["metrics"]
    return (src or {}).get(d["cc"], {}).get(m)


def best_rank_per_line(d):
    best, text = {}, {}
    for g in d["gold_ranks"]:
        best[g["dialogue_id"]] = min(best.get(g["dialogue_id"], 10**9), int(g[f"{d['cc']}_rank"]))
        text[g["dialogue_id"]] = g["dialogue"]
    return best, text


def a4_summary(d, v="nearest"):
    return d["a4"]["summary"].get(v) or {}


def pool_rows(d, variant, share=0.5, seed=42):
    for p in d["pools"]:
        if p["variant"] == variant and p["share"] == share and p["seed"] == seed:
            return [[e["channel"] + (" (ref)" if e["kind"] in ("reference", "dialogue") else ""),
                     short(e["full"].split("FullInfo_", 1)[1], 85)]
                    for e in sorted(p["entries"], key=lambda e: int(e["full"].split("Timestamp_")[1].split("_")[0]))]
    return None


def plot(data):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    metrics = [("redundancy", "pool redundancy (mean 1−NCD)"), ("distinct_topics", "distinct topics"),
               ("dialogue_lines", "reference lines in pool")]
    colors = {"dlg_all": "#2f6db5", "dlg_flt": "#7fa7d9", "s1_all": "#c4612f", "s1_flt": "#e3a37f"}
    fig, axes = plt.subplots(1, len(metrics), figsize=(4.4 * len(metrics), 3.6))
    for ax, (m, title) in zip(axes, metrics):
        for key, label, *_ in SETUPS:
            for sim, ls in (("ncd", "-"), ("index", "--")):
                ps = a4_summary(data[key][sim]).get("per_share", {})
                pts = [(float(s), ps[s][m]["mean"], ps[s][m]["std"]) for s in ps if ps[s][m]["mean"] is not None]
                if pts:
                    xs, ys, es = zip(*pts)
                    ax.errorbar(xs, ys, yerr=es, marker="o", capsize=3, color=colors[key], linestyle=ls,
                                label=f"{label} · {sim}")
        ax.set_title(title)
        ax.set_xlabel("reference_share")
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
        if not ax.lines:
            ax.text(0.5, 0.5, "pending\n(topics not tagged)", ha="center", va="center", transform=ax.transAxes)
    axes[0].legend(fontsize=6.5)
    fig.suptitle("CC variant `nearest`; solid = NCD, dashed = event indexing", fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "event_index_comparison.png", dpi=130)
    plt.close(fig)


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    data = {key: {"ncd": load(fn), "index": load(fi)} for key, _, fn, fi in SETUPS}
    label = {key: lab for key, lab, *_ in SETUPS}
    keys = [k for k, *_ in SETUPS]
    cols = [f"{label[k]} · {s}" for k in keys for s in SIMS]

    def cells(fn):
        return [fn(data[k][s]) for k in keys for s in SIMS]

    L = ["# CC similarity: NCD vs event indexing", "",
         "The CC (game: RC) scores how close a session-2 event is to a reference line. The game uses **NCD** on the "
         "descriptions. **Event indexing** follows the event-indexing model of story comprehension (Zwaan, Langston "
         "& Graesser, 1995), where readers link events that share a protagonist, place, time, cause or goal. "
         "It combines four dimensions read from the logs' structured fields:", "",
         "| dimension | what it measures | weight |", "|---|---|---|",
         "| entity | overlap of the entities involved: colonists, animals and other pawns from the `Actors` field "
         "and named in the text, each weighted by how rare it is in session 2 (IDF) | 0.4 |",
         "| text | 1 − NCD on the descriptions (the existing measure) | 0.3 |",
         "| place | exp(−distance / 25 cells) between map positions | 0.2 |",
         "| type | same log tag (CL/JOB/ARC/HP), only with event references (dialogue is always SL) | 0.1 |", "",
         "The weights are untuned defaults: with 8–13 reference lines, fitting them to the gold would overfit. "
         "Time and causality are not used: across sessions every reference line is \"long ago\", and the logs "
         "record no causes. No language model is involved.", "",
         "Everything else matches `CANDIDATE_FILTER_COMPARISON.md`: session 2 = `SimulatedDay2`, AC at threshold "
         "0.5 with `least_frequent`, the game's composer, total 12. No embeddings, no A2.", ""]

    # --- At a glance -------------------------------------------------------------------
    def rho(d, primary=False):
        s = a4_summary(d)
        return s.get("spearman_share_topics_primary" if primary else "spearman_share_topics")

    L += ["## At a glance", "", md_table(["", *cols], [
        ["A1 Recall@5 (pass ≥ 0.5)", *cells(lambda d: f2(a1m(d)))],
        ["A1 Recall@5, no exact repeats", *cells(lambda d: f2(a1m(d, no_exact=True)))],
        ["A1 MRR", *cells(lambda d: f2(a1m(d, "mrr")))],
        ["A1 verdict", *cells(lambda d: d["a1"]["status"])],
        ["A3 `nearest`: ref lines / CC redundancy",
         *cells(lambda d: f"{d['a3']['variants']['nearest']['dialogue_lines']} / "
                          f"{f2(d['a3']['variants']['nearest']['cc_redundancy'])}")],
        ["A3 `mmr`: ref lines / CC redundancy",
         *cells(lambda d: f"{d['a3']['variants']['mmr']['dialogue_lines']} / "
                          f"{f2(d['a3']['variants']['mmr']['cc_redundancy'])}")],
        ["A3 verdict", *cells(lambda d: d["a3"]["status"].split(" ")[0])],
        ["A4 ρ(share, topics) / first label", *cells(lambda d: f"{f2(rho(d))} / {f2(rho(d, True))}")],
        ["A4 verdict", *cells(lambda d: d["a4"]["status"])],
    ]), ""]

    # --- A1 -----------------------------------------------------------------------------
    rows = []
    for k in keys:
        for s in SIMS:
            d = data[k][s]
            rows.append([label[k], s, a1m(d), a1m(d, "recall@10"), a1m(d, "mrr"), d["a1"]["metrics"][d["cc"]]["n_gold_pairs"]])
    L += ["## A1 — does the CC find the events the author says continue a reference line?", "",
          md_table(["set-up", "similarity", "Recall@5", "Recall@10", "MRR", "gold targets"], rows), ""]
    for k in ("dlg_all", "s1_all"):
        (bn, text), (bi, _) = best_rank_per_line(data[k]["ncd"]), best_rank_per_line(data[k]["index"])
        L += [f"Rank of the best-ranked gold event per reference line, {label[k]} (lower is better):", "",
              md_table(["line", "reference text", "NCD", "event indexing"],
                       [[i, short(text[i], 72), bn[i], bi.get(i, "–")] for i in bn]), ""]

    # --- A3 -----------------------------------------------------------------------------
    variants = list(data["dlg_all"]["index"]["a3"]["variants"])     # includes the *_ix variants
    L += ["## A3 — redundancy in what the CC picks (share 0.5, total 12)", "",
          "Each cell: reference lines in the pool / CC redundancy (mean 1−NCD over pairs of CC events; "
          "redundancy is measured with NCD in every set-up so the numbers stay comparable).", "",
          md_table(["variant", *cols],
                   [[v, *cells(lambda d, v=v: "–" if v not in d["a3"]["variants"] else
                                   f"{d['a3']['variants'][v]['dialogue_lines']} / "
                                   f"{f2(d['a3']['variants'][v]['cc_redundancy'])}")] for v in variants]), "",
          "`mmr_ix` and `cap+mmr_ix` exist only with event indexing: MMR whose redundancy term uses the "
          "event-indexing similarity between two session-2 events (shared entities, place, log type, NCD text) "
          "instead of 1 − NCD, so relevance and redundancy are measured the same way.", ""]

    sweep_rows = []
    for k in keys:
        sw = data[k]["index"]["a3"].get("lambda_sweep") or {}
        for v, by_lam in sw.items():
            sweep_rows.append([label[k], v, *[f"{x['dialogue_lines']} / {f2(x['cc_redundancy'])}"
                                              for x in by_lam.values()]])
    if sweep_rows:
        lams = list(next(iter(next(iter(
            data[k]["index"]["a3"]["lambda_sweep"] for k in keys if data[k]["index"]["a3"].get("lambda_sweep"))).values())))
        L += ["### MMR's λ (relevance vs diversity), event indexing", "",
              "Reference lines in the pool / CC redundancy at share 0.5. λ = 0.7 is the default used everywhere "
              "else; lower λ weighs diversity more.", "",
              md_table(["set-up", "variant", *[f"λ {l}" for l in lams]], sweep_rows), ""]

    # --- A4 -----------------------------------------------------------------------------
    L += ["## A4 — is the share a breadth/depth dial?", "", "![comparison](event_index_comparison.png)", ""]
    pend = [f"`{label[k]} · {s}` ({data[k][s]['a4'].get('untagged_descriptions')} untagged)"
            for k in keys for s in SIMS if data[k][s]["a4"]["status"] == "pending"]
    if pend:
        L += ["**Pending:** topic counts need tags for descriptions that only appear with event indexing: "
              + ", ".join(pend) + ". Redundancy below doesn't need tags.", ""]
    L += [md_table(["set-up", "similarity", "ρ(share, topics)", "first label", "ρ(share, redundancy)", "A4"],
                   [[label[k], s, f2(rho(data[k][s])), f2(rho(data[k][s], True)),
                     f2(a4_summary(data[k][s]).get("spearman_share_redundancy")), data[k][s]["a4"]["status"]]
                    for k in keys for s in SIMS]), ""]

    def topics_by_share(d, v="nearest"):
        ps = a4_summary(d, v).get("per_share", {})
        return " → ".join(f2(ps[k]["distinct_topics"]["mean"]) for k in ps)

    if not pend:
        L += ["Distinct topics from share 0 to 1 (`nearest`):", "",
              md_table(["set-up", "NCD", "event indexing"],
                       [[label[k], topics_by_share(data[k]["ncd"]), topics_by_share(data[k]["index"])] for k in keys]), "",
              "- **Selected logs, all events:** event indexing keeps the dial (ρ "
              f"{f2(rho(data['s1_all']['index']))}): at share 1 the CC fills the pool with hauling and animal "
              "events linked to the selected logs, and the topic count drops to 3.",
              "- **Selected logs, filtered candidates:** the dial disappears (ρ "
              f"{f2(rho(data['s1_flt']['index']))}): topics stay at 8–9 at every share while redundancy still rises. "
              "With one representative per cluster and links through entities and places, the CC reaches into "
              "different topics instead of repeating one. This fails A4's breadth/depth claim, but it is the only "
              "set-up where adding continuity doesn't cost breadth.",
              "- **Dialogue:** `nearest` keeps a dial driven by the fight lines (topics fall to 3 with all events). The "
              "variant A3 picks now (`cap+mmr`) keeps breadth (7 topics at share 1) and misses the threshold "
              f"(ρ {f2(a4_summary(data['dlg_all']['index'], 'cap+mmr').get('spearman_share_topics'))}), "
              "so A4 is only partial.", ""]

    # --- Pools --------------------------------------------------------------------------
    L += ["## The pool at share 0.5 (`nearest`, seed 42) with event indexing", ""]
    for k in keys:
        rows = pool_rows(data[k]["index"], "nearest")
        if rows:
            L += [f"`{label[k]}`", "", md_table(["channel", "description"], rows), ""]

    # --- Reading ------------------------------------------------------------------------
    d_all, s_all, s_flt = data["dlg_all"], data["s1_all"], data["s1_flt"]
    L += ["## Reading", "",
          "- **With selected logs, event indexing is the best CC measure so far, and needs no language model.** "
          f"Recall@5 rises from {f2(a1m(s_all['ncd']))} to {f2(a1m(s_all['index']))} with all events "
          f"({f2(a1m(s_all['ncd'], no_exact=True))} → {f2(a1m(s_all['index'], no_exact=True))} without exact repeats) "
          f"and from {f2(a1m(s_flt['ncd']))} to {f2(a1m(s_flt['index']))} with filtered candidates. Both pass A1. "
          "The gains are the links NCD couldn't make: the walrus shot and the walrus's death to the walrus burial "
          "(ranks 23/28/104 → 1), the tribal raid to the burials (23 → 1), the spacecraft chunks to the crashing pod "
          "(68 → 9). One line gets worse: *Odette watching for targets* (1 → 15), because the entity dimension now "
          "prefers events involving Odette over the *watching for targets* lines about Boyd and Stench.",
          "- **With dialogue, event indexing finds more but concentrates the pool.** Recall@5 "
          f"{f2(a1m(d_all['ncd']))} → {f2(a1m(d_all['index']))} and MRR {f2(a1m(d_all['ncd'], 'mrr'))} → "
          f"{f2(a1m(d_all['index'], 'mrr'))}: the walrus lines now find the walrus and anteater burials. But the "
          "treeline line shares both of its colonists with every Odette–Stench fight event, so those score far "
          "above everything else and take every CC slot with `nearest` or MMR, even with filtered candidates. Only "
          "the per-line cap breaks this up (2 dialogue lines, CC redundancy down to 0.29 with cap+MMR). The "
          "protagonist dimension amplifies what NCD did with names.",
          "- **MMR needs the same similarity for redundancy as for relevance.** Two people in a long fight produce "
          "many events with identical entities. With NCD redundancy, MMR can't push the CC off the fight lines "
          "(1 dialogue line at λ 0.7 and 0.5). With event-indexing redundancy (`mmr_ix`) it reaches 2 lines at "
          "λ 0.7 and all 3 at λ 0.5, without a hard cap. At the default λ 0.7 that is still one line short, so A3 "
          "still fails for dialogue. By NCD's measure the picks are about as redundant as plain MMR's (0.33 vs 0.34 "
          "with all events, 0.39 vs 0.36 with filtered candidates) because they still share colonist names, but they "
          "are different kinds of event: an insult spree ending, a punch, Stench tending Odette afterwards. With "
          "selected logs, `mmr_ix` gives the lowest redundancy with filtered candidates (0.24) and is the variant A3 "
          "picks there.",
          "- **Psychology:** event indexing shifts the CC from repetition priming (surface overlap) towards the "
          "situation-model links readers use to keep a story coherent. With selected logs as the reference it still "
          "implements selection history (what was selected before biases what is selected now), but at the level of "
          "who, where and what kind of event rather than wording.", "",
          "## Caveats", "",
          "- One colony, two sessions, 8 and 13 reference lines, single author's gold and tags.",
          "- The weights (0.4 / 0.3 / 0.2 / 0.1) and the place scale (25 cells) were set by hand, not fitted; "
          "other values may rank differently.",
          "- The entity vocabulary comes from the `Actors` fields of both sessions. An entity that is never an "
          "actor (e.g. \"raiders\", \"treeline\") is invisible to the entity dimension.",
          "- Dialogue lines' positions are where they were spoken, a weak cue for what they're about.",
          "- With filtered candidates, A1 credits a representative for its whole cluster.", ""]

    (OUT / "EVENT_INDEX_COMPARISON.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    plot(data)
    return OUT / "EVENT_INDEX_COMPARISON.md"


if __name__ == "__main__":
    print(f"Wrote {run()}")
