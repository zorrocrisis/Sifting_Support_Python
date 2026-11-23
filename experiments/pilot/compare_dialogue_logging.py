"""
Compare three ways of using session-1 dialogue as the CC (game: RC) reference, each with
NCD / event indexing and all / filtered candidates (12 runs):

  original   the dialogue line as the game logs it ("{Name} said '...'")
  stripped   speech frame and opening vocative removed before computing similarity
  provenance the CC scores each dialogue line through the session-1 logs it was generated
             from (experiments/pilot/dialogue_provenance.csv); the pool still shows the line

No embeddings, no A2. Run the configurations first (run_all --reference dialogue /
dialogue_stripped / dialogue_prov, --cc-candidates all|filtered, --cc-similarity ncd|index,
--no-embeddings --skip-generation --skip-masking), then

  python -m experiments.pilot.compare_dialogue_logging

Writes experiments/pilot/out_compare/DIALOGUE_LOGGING_COMPARISON.md. Recomputes nothing.
"""

import csv
import json

from experiments.common import paths
from experiments.common.dialogue_logging import read_provenance
from experiments.common.report import md_table, read_json, short

OUT = paths.PILOT_DIR / "out_compare"
LOGGING = [("original", "out"), ("stripped", "out_dialogue_stripped"), ("provenance", "out_dialogue_prov")]
CONFIGS = [("", "162 events · NCD"), ("_index", "162 events · index"),
           ("_filtered", "43 events · NCD"), ("_filtered_index", "43 events · index")]


def f2(x):
    return "–" if x is None else f"{x:.2f}"


def load(folder):
    out = paths.PILOT_DIR / folder
    r = {k: read_json(out / f"{k}_result.json") for k in ("a1", "a3", "a4")}
    if any(v is None for v in r.values()):
        raise SystemExit(f"{folder}: results missing; run that configuration first")
    r["cc"] = r["a1"].get("cc_method", "ncd")
    with open(out / "a1_gold_ranks.csv", encoding="utf-8") as f:
        r["gold_ranks"] = list(csv.DictReader(f))
    with open(out / "a4_pools.jsonl", encoding="utf-8") as f:
        r["pools"] = [json.loads(l) for l in f]
    return r


def a1m(d, m="recall@5"):
    return d["a1"]["metrics"][d["cc"]][m]


def a3v(d, v):
    x = d["a3"]["variants"].get(v)
    return "–" if x is None else f"{x['dialogue_lines']} / {f2(x['cc_redundancy'])}"


def pool_rows(d, variant="nearest", share=0.5, seed=42):
    for p in d["pools"]:
        if p["variant"] == variant and p["share"] == share and p["seed"] == seed:
            return [[e["channel"] + (" (ref)" if e["kind"] in ("reference", "dialogue") else ""),
                     short(e["full"].split("FullInfo_", 1)[1], 90)]
                    for e in sorted(p["entries"], key=lambda e: int(e["full"].split("Timestamp_")[1].split("_")[0]))]
    return []


COLORS = {"original": "#2a78d6", "provenance": "#eb6834"}   # validated categorical slots 1-2
TEXT, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"


def plot_dial(data, sfx="", title_setup="162 events · NCD", filename="dial_original_vs_provenance.png"):
    """
    Original dialogue vs provenance: distinct topics (all labels vs first label) and pool
    redundancy against reference_share, CC variant `nearest`. Colour = how dialogue is logged;
    line style = how multi-topic tags are counted.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    fig = plt.figure(figsize=(11.5, 6.2), facecolor=SURFACE)
    gs = fig.add_gridspec(2, 2, height_ratios=[4.2, 1.2])
    ax_t, ax_r = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
    ax_leg = fig.add_subplot(gs[1, :])
    ax_leg.axis("off")
    # The first-label series is nudged right by DX so it stays visible where it equals the all-labels one.
    DX = 0.018
    styles = {"distinct_topics": dict(ls="-", marker="o", filled=True, label="all labels", dx=0.0),
              "distinct_topics_primary": dict(ls="--", marker="s", filled=False, label="first label", dx=DX)}

    def series(lg, metric):
        ps = data[(lg, sfx)]["a4"]["summary"]["nearest"]["per_share"]
        pts = [(float(k), ps[k][metric]["mean"], ps[k][metric]["std"])
               for k in ps if ps[k][metric]["mean"] is not None]
        return [list(t) for t in zip(*pts)]

    for lg in ("original", "provenance"):
        c = COLORS[lg]
        for metric, st in styles.items():
            xs, ys, es = series(lg, metric)
            xs = [x + st["dx"] for x in xs]
            ax_t.errorbar(xs, ys, yerr=es, color=c, ls=st["ls"], lw=2, marker=st["marker"], ms=8,
                          mfc=c if st["filled"] else SURFACE, mec=c, mew=2, capsize=3, zorder=3)
        xs, ys, es = series(lg, "redundancy")
        ax_r.errorbar(xs, ys, yerr=es, color=c, lw=2, marker="o", ms=8, mec=SURFACE, mew=1.5,
                      capsize=3, zorder=3)
        ax_r.annotate(lg, (xs[-1], ys[-1]), xytext=(9, 0), textcoords="offset points", va="center",
                      fontsize=9, color=TEXT)

    for ax, t, yl in ((ax_t, "Breadth: distinct topics in the pool", "distinct topics (pool of 12 logs)"),
                      (ax_r, "Depth: pool redundancy", "mean pairwise 1 − NCD")):
        ax.set_facecolor(SURFACE)
        ax.set_title(t, fontsize=11, color=TEXT, loc="left")
        ax.set_xlabel("reference_share (RC's share of the 12 slots)", color=MUTED)
        ax.set_ylabel(yl, color=MUTED)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
        ax.set_xlim(-0.05, 1.05 if ax is ax_t else 1.3)
        ax.grid(True, color=GRID, lw=1)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GRID)
        ax.tick_params(colors=MUTED)

    # Bottom strip, below both graphs: the two legends side by side, then the caption.
    colour_legend = ax_leg.legend(
        handles=[Line2D([], [], color=COLORS[k], lw=3, label=f"{k} dialogue logging") for k in COLORS],
        title="Colour = how dialogue is logged", loc="upper left", bbox_to_anchor=(0.0, 1.0),
        fontsize=8.5, title_fontsize=9, frameon=False, alignment="left", handlelength=3.5)
    ax_leg.add_artist(colour_legend)
    ax_leg.legend(
        handles=[Line2D([], [], color=MUTED, lw=2, ls="-", marker="o", ms=7,
                        label="solid line, filled circles: all labels (a multi-topic tag counts every topic)"),
                 Line2D([], [], color=MUTED, lw=2, ls="--", marker="s", ms=7, mfc=SURFACE, mew=2,
                        label="dashed line, open squares: first label only (nudged right so overlaps stay visible)")],
        title="Line style = how topics are counted (left graph)", loc="upper left", bbox_to_anchor=(0.3, 1.0),
        fontsize=8.5, title_fontsize=9, frameon=False, alignment="left", handlelength=3.5)
    ax_leg.text(0.0, 0.0, f"Original dialogue vs provenance as the RC reference: {title_setup}, CC variant "
                          "nearest, pool of 12 logs; points are the mean over 5 seeds, bars ± 1 sd.",
                transform=ax_leg.transAxes, fontsize=9, color=MUTED, ha="left", va="bottom")
    fig.subplots_adjust(left=0.06, right=0.97, top=0.94, bottom=0.03, wspace=0.28, hspace=0.32)
    out = OUT / filename
    fig.savefig(out, dpi=140, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    return out


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    data = {(lg, sfx): load(base + sfx) for lg, base in LOGGING for sfx, _ in CONFIGS}
    prov, used_suggested = read_provenance()

    L = ["# Logging dialogue so the RC can match it: original vs stripped vs provenance", "",
         "Dialogue is the RC reference the player actually sees, but it paraphrases the events it is about, so "
         "matching it against session-2 event logs is hard. This compares three ways of using the same 8 "
         "session-1 dialogue lines, scored against the same dialogue gold:", "",
         "| logging | what the RC compares | game change needed |", "|---|---|---|",
         "| original | the line as logged: `Odette 'Odette' O'Neill said 'Stench, I watched the far treeline…'` | none |",
         "| stripped | the line without the speech frame and vocative: `I watched the far treeline for more raiders.` | "
         "none (preprocessing) |",
         "| provenance | the session-1 logs the line was generated from (best match over its sources); the pool and "
         "the player still get the dialogue line | log source `_ID_`s with each dialogue line |", "",
         "Each is run with NCD and event indexing, over all 162 session-2 events and over the 43 the AC keeps "
         "after filtering. Session 2, AC, composer, total 12 and MMR λ 0.7 as in the other reports. No embeddings, "
         "no A2.", ""]
    if used_suggested:
        L += [f"**Provisional:** provenance uses Claude's suggested sources for {len(used_suggested)} of "
              f"{len(prov)} lines (`suggested_source_ids` in `experiments/pilot/dialogue_provenance.csv`); the "
              "author hasn't confirmed them in `source_ids` yet.", ""]
    L += ["Sources used:", "", md_table(["line", "source logs (session 1)"],
                                        [[k, ", ".join(v)] for k, v in prov.items()]), ""]

    # --- A1 ---------------------------------------------------------------------------
    L += ["## A1 — does the RC find the events the author says continue a dialogue line?", "",
          "Recall@5 (pass ≥ 0.5) / MRR:", "",
          md_table(["logging", *[c for _, c in CONFIGS]],
                   [[lg, *[f"{f2(a1m(data[(lg, s)]))} / {f2(a1m(data[(lg, s)], 'mrr'))}" for s, _ in CONFIGS]]
                    for lg, _ in LOGGING]), "",
          "Verdict:", "",
          md_table(["logging", *[c for _, c in CONFIGS]],
                   [[lg, *[data[(lg, s)]["a1"]["status"] for s, _ in CONFIGS]] for lg, _ in LOGGING]), ""]

    orig, pn, pi = data[("original", "")], data[("provenance", "")], data[("provenance", "_index")]
    idx = {(g["dialogue_id"], g["event"]): g for g in pi["gold_ranks"]}
    base = {(g["dialogue_id"], g["event"]): g for g in orig["gold_ranks"]}
    L += ["Rank of every gold event (out of 162), original dialogue vs provenance:", "",
          md_table(["line", "gold event", "original · NCD", "provenance · NCD", "provenance · index"],
                   [[g["dialogue_id"], f"{g['event']} {short(g['event_description'], 55)}",
                     base[(g["dialogue_id"], g["event"])]["ncd_rank"], g["ncd_rank"],
                     idx[(g["dialogue_id"], g["event"])]["index_rank"]] for g in pn["gold_ranks"]]), ""]

    # --- A3 ---------------------------------------------------------------------------
    L += ["## A3 — redundancy in what the RC picks (share 0.5, total 12)", "",
          "Dialogue lines in the pool / CC redundancy (mean 1−NCD over pairs of CC events), for `nearest` (the "
          "game's selector) and the variant A3 picks by its rule:", ""]
    rows = []
    for lg, _ in LOGGING:
        for s, c in CONFIGS:
            d = data[(lg, s)]
            best = d["a3"]["best_variant"]
            rows.append([lg, c, a3v(d, "nearest"), f"`{best}` {a3v(d, best)}", d["a3"]["status"].split(" ")[0]])
    L += [md_table(["logging", "set-up", "`nearest`", "A3's pick", "A3"], rows), ""]

    # --- A4 ---------------------------------------------------------------------------
    rows, pend = [], []
    for lg, _ in LOGGING:
        for s, c in CONFIGS:
            d = data[(lg, s)]
            sm = d["a4"]["summary"].get("nearest", {})
            rows.append([lg, c, f2(sm.get("spearman_share_topics")), f2(sm.get("spearman_share_topics_primary")),
                         f2(sm.get("spearman_share_redundancy")), d["a4"]["status"]])
            if d["a4"]["status"] == "pending":
                pend.append(f"`{dict(LOGGING)[lg] + s}`")
    L += ["## A4 — is the share a breadth/depth dial? (`nearest`)", "",
          "![original vs provenance](dial_original_vs_provenance.png)", "",
          "Original dialogue vs provenance, with all 162 events and NCD. Left, breadth: solid lines count every "
          "topic of a multi-topic tag, dashed lines only its first (nudged slightly right so overlapping points "
          "stay visible). Right, depth: redundancy against the share.", "",
          "The same with the 43 filtered candidates (the AC's cluster representatives):", "",
          "![original vs provenance, 43 events](dial_original_vs_provenance_43.png)", ""]
    if pend:
        L += ["**Pending** for " + ", ".join(pend) + ": some pooled descriptions have no topic yet (see each "
              "folder's `topic_tags_missing.csv`).", ""]
    L += [md_table(["logging", "set-up", "ρ(share, topics)", "first label", "ρ(share, redundancy)", "A4"], rows), ""]

    # --- Pools ------------------------------------------------------------------------
    L += ["## The pool at share 0.5 (`nearest`, seed 42), as the LLM would see it", ""]
    for key, title in ((("original", ""), "original · 162 events · NCD (the game today)"),
                       (("provenance", ""), "provenance · 162 events · NCD"),
                       (("provenance", "_index"), "provenance · 162 events · event indexing")):
        L += [f"`{title}`", "", md_table(["channel", "description"], pool_rows(data[key])), ""]

    # --- Reading ----------------------------------------------------------------------
    po, pf = data[("provenance", "")], data[("provenance", "_filtered")]
    so = data[("stripped", "")]
    L += ["## Reading", "",
          "- **Provenance solves the paraphrase problem, even with plain NCD.** Recall@5 goes from "
          f"{f2(a1m(orig))} to {f2(a1m(po))} (MRR {f2(a1m(orig, 'mrr'))} → {f2(a1m(po, 'mrr'))}) with the game's "
          f"own measure, and to {f2(a1m(pf))} with filtered candidates. Dialogue passes A1 for the first time, "
          "without embeddings. The player still sees the dialogue line; only what the RC matches changes.",
          "- **It also fixes redundancy.** The treeline line no longer floods the pool with fight lines: its "
          "sources are *Odette watching for targets* and the raid, so `nearest` alone gives 3 dialogue lines and "
          f"the joint-lowest CC redundancy of any dialogue set-up ({a3v(po, 'nearest')}). The fights only came from "
          "matching on colonist names.",
          "- **The share works as a dial with provenance, and more robustly.** A4 passes in all four provenance "
          "set-ups, and the first-label reading mostly holds too (ρ "
          + ", ".join(f2(data[("provenance", sfx)]["a4"]["summary"]["nearest"]["spearman_share_topics_primary"])
                      for sfx, _ in CONFIGS)
          + f"), where original dialogue's pass rests on multi-topic tags (first label "
          f"{f2(orig['a4']['summary']['nearest']['spearman_share_topics_primary'])}).",
          "- **Event indexing helps the lines whose sources share entities but not wording.** The walrus lines "
          "find the walrus and anteater burials (rank 1–4 instead of 27–36 with NCD), but it misses lines where "
          "NCD's wording match is right (*Odette watching for targets* → *Boyd watching for targets*: 1 with NCD, "
          "16 with indexing). With all 162 events it has the better MRR and Recall@10 and NCD the better "
          "Recall@5; with filtered candidates it is ahead on Recall@5 too "
          f"({f2(a1m(data[('provenance', '_filtered_index')]))} vs {f2(a1m(pf))}).",
          "- **Stripping the speech frame doesn't help** (Recall@5 "
          f"{f2(a1m(orig))} → {f2(a1m(so))} with NCD). Names were not the main obstacle; paraphrase was.",
          "- **What it means for the game:** log the `_ID_`s of the pool logs each dialogue line was generated "
          "from, and let the RC match on those. The dialogue step currently works from the narrative, so it would "
          "need the pool logs too and return the source IDs with each line.", "",
          "## Caveats", "",
          "- The provenance is simulated by hand-mapping each line to session-1 logs; in the game it would come from "
          "the LLM, which could cite the wrong logs.",
          "- The 8 lines were generated from the 13 logs the AC selected in session 1, so every source is one of "
          "those; this is close to the `s1_selected` reference, with the dialogue lines kept as the player-facing "
          "layer.",
          "- One colony, two sessions, 8 dialogue lines, single author's gold and tags.", ""]

    (OUT / "DIALOGUE_LOGGING_COMPARISON.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    plot_dial(data)
    plot_dial(data, sfx="_filtered", title_setup="43 events (filtered) · NCD",
              filename="dial_original_vs_provenance_43.png")
    return OUT / "DIALOGUE_LOGGING_COMPARISON.md"


if __name__ == "__main__":
    print(f"Wrote {run()}")
