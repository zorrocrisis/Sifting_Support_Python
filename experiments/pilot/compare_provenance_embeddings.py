"""
Provenance vs embeddings for dialogue as the RC reference.

Two separate fixes for "dialogue paraphrases events":
  - provenance: the RC scores a dialogue line through the session-1 logs it was generated from
    (no language model; needs the game to log source IDs);
  - embeddings: a sentence-embedding model (all-MiniLM-L6-v2, cosine) scores the dialogue line
    itself, so a paraphrase can still match (no game change; depends on a model trained on
    general English).

Crossing them gives a 2 x 3 grid per candidate set: {original, provenance} x {NCD, event
indexing, embeddings}, over all 162 session-2 events and over the 43 the AC keeps after
filtering. Run the configurations first (run_all --reference dialogue|dialogue_prov
--cc-candidates all|filtered --cc-similarity ncd|index|embed --no-embeddings --skip-generation
--skip-masking), then

  python -m experiments.pilot.compare_provenance_embeddings

Writes experiments/pilot/out_compare/PROVENANCE_VS_EMBEDDINGS.md. Recomputes nothing.
"""

import csv

from experiments.common import paths
from experiments.common.report import md_table, read_json, short

OUT = paths.PILOT_DIR / "out_compare"
LOGGING = [("original", "out"), ("provenance", "out_dialogue_prov")]
SIMS = [("ncd", "", "NCD"), ("index", "_index", "event indexing"), ("embed", "_embed", "embeddings")]
CANDS = [("", "162 events"), ("_filtered", "43 events")]


def f2(x):
    return "–" if x is None else f"{x:.2f}"


def folder(base, cand, sim_sfx):
    return base + cand + sim_sfx


def load(name):
    out = paths.PILOT_DIR / name
    r = {k: read_json(out / f"{k}_result.json") for k in ("a1", "a3", "a4")}
    if any(v is None for v in r.values()):
        raise SystemExit(f"{name}: results missing; run that configuration first")
    r["cc"] = r["a1"].get("cc_method", "ncd")
    with open(out / "a1_gold_ranks.csv", encoding="utf-8") as f:
        r["gold_ranks"] = list(csv.DictReader(f))
    return r


def a1m(d, m="recall@5"):
    return d["a1"]["metrics"][d["cc"]][m]


def best_rank(d):
    out = {}
    for g in d["gold_ranks"]:
        out[g["dialogue_id"]] = min(out.get(g["dialogue_id"], 10**9), int(g[f"{d['cc']}_rank"]))
    return out


COLORS = {"original": "#2a78d6", "provenance": "#eb6834"}   # validated categorical slots 1-2
TEXT, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"


def plot_a1(data, metric="recall@5", threshold=0.5):
    """
    Grouped bars: A1 Recall@5 for original dialogue vs provenance, per similarity measure,
    one panel per candidate set. Dashed line = the pass threshold.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    fig = plt.figure(figsize=(11.5, 5.6), facecolor=SURFACE)
    gs = fig.add_gridspec(2, 2, height_ratios=[4.2, 1.0])
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
    ax_leg = fig.add_subplot(gs[1, :])
    ax_leg.axis("off")

    width, gap = 0.36, 0.04
    for ax, (cand, cname) in zip(axes, CANDS):
        for i, (lg, _) in enumerate(LOGGING):
            xs = [j + (i - 0.5) * (width + gap) for j in range(len(SIMS))]
            vals = [a1m(data[(lg, cand, sim)], metric) for sim, _, _ in SIMS]
            ax.bar(xs, vals, width=width, color=COLORS[lg], zorder=3, edgecolor=SURFACE, linewidth=2)
            for x, v in zip(xs, vals):
                ax.text(x, v + 0.015, f"{v:.2f}", ha="center", va="bottom", fontsize=9, color=TEXT, zorder=4,
                        bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1.0))
        ax.axhline(threshold, color=MUTED, ls="--", lw=1.5, zorder=2)
        ax.text(1.01, threshold, f"pass\n≥ {threshold}", transform=ax.get_yaxis_transform(),
                ha="left", va="center", fontsize=8.5, color=MUTED)
        ax.set_xticks(range(len(SIMS)))
        ax.set_xticklabels([n for _, _, n in SIMS], color=TEXT)
        ax.set_ylim(0, 1.0)
        ax.set_ylabel("A1 Recall@5" if metric == "recall@5" else f"A1 {metric}", color=MUTED)
        ax.set_title(f"CC candidates: {cname}", fontsize=11, color=TEXT, loc="left")
        ax.set_facecolor(SURFACE)
        ax.grid(True, axis="y", color=GRID, lw=1)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GRID)
        ax.tick_params(colors=MUTED)

    ax_leg.legend(handles=[Patch(color=COLORS["original"], label="original dialogue line (as the game logs it)"),
                           Patch(color=COLORS["provenance"], label="provenance (scored through its session-1 source logs)"),
                           Line2D([], [], color=MUTED, ls="--", lw=1.5, label="A1 pass threshold")],
                  title="Bars = what the RC compares", loc="upper left", bbox_to_anchor=(0.0, 1.0),
                  fontsize=8.5, title_fontsize=9, frameon=False, alignment="left", ncol=3,
                  columnspacing=2.0)
    ax_leg.text(0.0, 0.0, "A1 Recall@5: share of the author's gold events in the RC's top 5 for each dialogue line, "
                          "averaged over the 8 lines. Embeddings: all-MiniLM-L6-v2 cosine.",
                transform=ax_leg.transAxes, fontsize=9, color=MUTED, ha="left", va="bottom")
    fig.subplots_adjust(left=0.06, right=0.94, top=0.94, bottom=0.03, wspace=0.28, hspace=0.3)
    out = OUT / "provenance_vs_embeddings_a1.png"
    fig.savefig(out, dpi=140, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    return out


SIM_COLORS = {"ncd": "#1baf7a", "embed": "#6250d6"}   # validated pair (aqua needs value labels: < 3:1)


def plot_prov_ncd_vs_embed(data, threshold=0.5):
    """
    Provenance only: A1 Recall@5 and Recall@10 with NCD vs embeddings, grouped by candidate set.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    fig = plt.figure(figsize=(10.5, 5.4), facecolor=SURFACE)
    gs = fig.add_gridspec(2, 2, height_ratios=[4.2, 1.0])
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
    ax_leg = fig.add_subplot(gs[1, :])
    ax_leg.axis("off")

    sims = [("ncd", "NCD (no language model)"), ("embed", "embeddings (all-MiniLM-L6-v2)")]
    width, gap = 0.34, 0.04
    for ax, (metric, mname) in zip(axes, (("recall@5", "A1 Recall@5"), ("recall@10", "A1 Recall@10"))):
        for i, (sim, _) in enumerate(sims):
            xs = [j + (i - 0.5) * (width + gap) for j in range(len(CANDS))]
            vals = [a1m(data[("provenance", cand, sim)], metric) for cand, _ in CANDS]
            ax.bar(xs, vals, width=width, color=SIM_COLORS[sim], zorder=3, edgecolor=SURFACE, linewidth=2)
            for x, v in zip(xs, vals):
                ax.text(x, v + 0.015, f"{v:.2f}", ha="center", va="bottom", fontsize=9.5, color=TEXT, zorder=4,
                        bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1.0))
        if metric == "recall@5":
            ax.axhline(threshold, color=MUTED, ls="--", lw=1.5, zorder=2)
            ax.text(1.01, threshold, f"pass\n≥ {threshold}", transform=ax.get_yaxis_transform(),
                    ha="left", va="center", fontsize=8.5, color=MUTED)
        ax.set_xticks(range(len(CANDS)))
        ax.set_xticklabels([("all 162 events" if c == "" else "43 filtered events") for c, _ in CANDS], color=TEXT)
        ax.set_ylim(0, 1.0)
        ax.set_ylabel(mname, color=MUTED)
        ax.set_title(mname, fontsize=11, color=TEXT, loc="left")
        ax.set_facecolor(SURFACE)
        ax.grid(True, axis="y", color=GRID, lw=1)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GRID)
        ax.tick_params(colors=MUTED)

    ax_leg.legend(handles=[Patch(color=SIM_COLORS[k], label=lab) for k, lab in sims]
                  + [Line2D([], [], color=MUTED, ls="--", lw=1.5, label="A1 pass threshold (Recall@5)")],
                  title="Bars = how the RC scores a dialogue line through its source logs", loc="upper left",
                  bbox_to_anchor=(0.0, 1.0), fontsize=8.5, title_fontsize=9, frameon=False, alignment="left",
                  ncol=3, columnspacing=2.0)
    ax_leg.text(0.0, 0.0, "Dialogue with provenance as the RC reference: share of the author's gold events in the "
                          "RC's top 5 / top 10 per dialogue line, averaged over the 8 lines.",
                transform=ax_leg.transAxes, fontsize=9, color=MUTED, ha="left", va="bottom")
    fig.subplots_adjust(left=0.07, right=0.93, top=0.94, bottom=0.03, wspace=0.3, hspace=0.3)
    out = OUT / "provenance_ncd_vs_embeddings_recall.png"
    fig.savefig(out, dpi=140, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    return out


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    data = {(lg, c, s): load(folder(base, c, sfx))
            for lg, base in LOGGING for c, _ in CANDS for s, sfx, _ in SIMS}
    simname = {s: n for s, _, n in SIMS}

    L = ["# Provenance vs embeddings for dialogue as the RC reference", "",
         "Dialogue is the reference the player sees, but it paraphrases the events it is about. Two different fixes:", "",
         "| fix | how | needs |", "|---|---|---|",
         "| **provenance** | the RC scores each dialogue line through the session-1 logs it was generated from; "
         "the pool still shows the line | the game logs the source `_ID_`s with each line; no language model |",
         "| **embeddings** | a sentence-embedding model (all-MiniLM-L6-v2, cosine) scores the dialogue line itself, "
         "so a paraphrase can still match | no game change; a model trained on general English, run locally |", "",
         "Crossing them: {original dialogue, provenance} × {NCD, event indexing, embeddings}, each over all 162 "
         "session-2 events and over the 43 the AC keeps after filtering. Same dialogue gold, AC, composer, total 12 "
         "and MMR λ 0.7 (MMR's redundancy term stays NCD in every run) as the other reports.", ""]

    # --- A1 grid ---------------------------------------------------------------------
    for c, cname in CANDS:
        L += [f"## A1 — {cname}: Recall@5 / Recall@10 / MRR (pass: Recall@5 ≥ 0.5)", "",
              md_table(["logging", *[n for _, _, n in SIMS]],
                       [[lg, *[f"{f2(a1m(data[(lg, c, s)]))} / {f2(a1m(data[(lg, c, s)], 'recall@10'))} / "
                               f"{f2(a1m(data[(lg, c, s)], 'mrr'))} ({data[(lg, c, s)]['a1']['status']})"
                               for s, _, _ in SIMS]] for lg, _ in LOGGING]), ""]

    L += ["![provenance vs embeddings, A1](provenance_vs_embeddings_a1.png)", ""]

    o, p = ("original", "", "embed"), ("provenance", "", "ncd")
    L += ["**Provenance with plain NCD finds far more than embeddings on the original line** "
          f"(Recall@5 {f2(a1m(data[p]))} vs {f2(a1m(data[o]))} with all events; "
          f"{f2(a1m(data[('provenance', '_filtered', 'ncd')]))} vs {f2(a1m(data[('original', '_filtered', 'embed')]))} "
          "filtered). Embeddings on top of provenance add a little more "
          f"({f2(a1m(data[('provenance', '', 'embed')]))} and {f2(a1m(data[('provenance', '_filtered', 'embed')]))}), "
          "about as much as event indexing does with filtered candidates "
          f"({f2(a1m(data[('provenance', '_filtered', 'index')]))}).", ""]

    L += ["With provenance only, NCD vs embeddings on Recall@5 and Recall@10:", "",
          "![provenance: NCD vs embeddings](provenance_ncd_vs_embeddings_recall.png)", ""]

    # --- per line ---------------------------------------------------------------------
    cols = [("original", "", "embed"), ("provenance", "", "ncd"), ("provenance", "", "index"), ("provenance", "", "embed")]
    ranks = {k: best_rank(data[k]) for k in cols}
    texts = {g["dialogue_id"]: g["dialogue"] for g in data[cols[0]]["gold_ranks"]}
    L += ["Rank of the best-ranked gold event per dialogue line (all 162 events; lower is better):", "",
          md_table(["line", "dialogue", *[f"{lg} · {simname[s]}" for lg, _, s in cols]],
                   [[i, short(texts[i], 60), *[ranks[k].get(i, "–") for k in cols]] for i in texts]), ""]

    # --- A3 / A4 -------------------------------------------------------------------------
    rows = []
    for lg, _ in LOGGING:
        for c, cname in CANDS:
            for s, _, sn in SIMS:
                d = data[(lg, c, s)]
                v = d["a3"]["variants"]
                best = d["a3"]["best_variant"]
                sm = d["a4"]["summary"].get("nearest", {})
                rows.append([lg, cname, sn,
                             f"{v['nearest']['dialogue_lines']} / {f2(v['nearest']['cc_redundancy'])}",
                             f"`{best}` {v[best]['dialogue_lines']} / {f2(v[best]['cc_redundancy'])}",
                             d["a3"]["status"].split(" ")[0],
                             f"{f2(sm.get('spearman_share_topics'))} / {f2(sm.get('spearman_share_topics_primary'))}",
                             d["a4"]["status"]])
    L += ["## A3 and A4", "",
          "A3: dialogue lines in the pool / CC redundancy at share 0.5. A4: ρ(share, topics) with `nearest`, all labels "
          "/ first label (pass ≤ −0.7).", "",
          md_table(["logging", "candidates", "similarity", "A3 `nearest`", "A3's pick", "A3",
                    "A4 ρ", "A4"], rows), ""]
    pend = [f"`{folder(dict(LOGGING)[lg], c, dict((s, x) for s, x, _ in SIMS)[s])}`"
            for (lg, c, s), d in data.items() if d["a4"]["status"] == "pending"]
    if pend:
        L += [f"A4 is **pending** for {', '.join(pend)}: some pooled descriptions have no topic yet (see each "
              "folder's `topic_tags_missing.csv`). ρ for `nearest` is shown where its pools are fully tagged.", ""]

    # --- Reading ------------------------------------------------------------------------
    L += ["## Reading", "",
          "- **Provenance is the bigger lever.** Moving from the original line to its source logs raises Recall@5 "
          f"for every measure (NCD {f2(a1m(data[('original', '', 'ncd')]))} → {f2(a1m(data[('provenance', '', 'ncd')]))}, "
          f"embeddings {f2(a1m(data[('original', '', 'embed')]))} → {f2(a1m(data[('provenance', '', 'embed')]))}). "
          "Changing the measure on the original line helps much less (best: embeddings with filtered candidates, "
          f"{f2(a1m(data[('original', '_filtered', 'embed')]))}).",
          "- **Embeddings do avoid the name flooding.** On the original dialogue, `nearest` with embeddings already "
          "spreads over 3 dialogue lines (NCD: 1), because a sentence model doesn't weigh shared colonist names the "
          "way a compressor does. But that alone doesn't make the matches right:",
          "- **Embeddings alone don't solve the paraphrase problem here.** On the original dialogue they fail A1 in "
          "both candidate sets. A small general-English model doesn't know that \"I hit that walrus\" is about a "
          "tribesperson called Walrus (its best gold event, the burial, ranks "
          f"{best_rank(data[('original', '', 'embed')]).get('S108')}), nor that the gazelles and the grizzly in the "
          "dialogue are the game's animals logged under those names (ranks "
          f"{best_rank(data[('original', '', 'embed')]).get('S111')} and "
          f"{best_rank(data[('original', '', 'embed')]).get('S112')}).",
          "- **With provenance, the measure matters less.** NCD, event indexing and embeddings all pass or come "
          "close; with all events embeddings are ahead on Recall@5 and event indexing on MRR. The source logs "
          "share the game's own vocabulary with the session-2 events, so even a compression measure works.",
          "- **Embeddings on the original dialogue give no dial** (A4 with all events: ρ "
          f"{f2(data[('original', '', 'embed')]['a4']['summary']['nearest']['spearman_share_topics'])}, first label "
          f"{f2(data[('original', '', 'embed')]['a4']['summary']['nearest']['spearman_share_topics_primary'])}): "
          "the model spreads its picks across topics, which avoids flooding but leaves breadth flat until share 0.75. "
          "With provenance the dial returns for `nearest`.",
          "- **For the paper:** with filtered candidates, provenance with event indexing is within 0.01 of "
          f"embeddings on Recall@5 ({f2(a1m(data[('provenance', '_filtered', 'index')]))} vs "
          f"{f2(a1m(data[('provenance', '_filtered', 'embed')]))}) without any language model. With all events, "
          f"NCD trails embeddings on Recall@5 ({f2(a1m(data[('provenance', '', 'ncd')]))} vs "
          f"{f2(a1m(data[('provenance', '', 'embed')]))}) but ties on MRR "
          f"({f2(a1m(data[('provenance', '', 'ncd')], 'mrr'))} vs {f2(a1m(data[('provenance', '', 'embed')], 'mrr'))}), "
          f"and event indexing has the best MRR of all ({f2(a1m(data[('provenance', '', 'index')], 'mrr'))}). "
          "That supports dropping embeddings for domain generalisation, provided the game logs provenance.", "",
          "## Caveats", "",
          "- One colony, 8 dialogue lines, single author's gold; provenance is hand-mapped (the game would get it "
          "from the LLM, which could cite the wrong logs).",
          "- One embedding model, no tuning; a larger or domain-tuned model could do better on the original lines.",
          "- MMR's redundancy term uses NCD in every run here, including the embedding runs.", ""]

    (OUT / "PROVENANCE_VS_EMBEDDINGS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    plot_a1(data)
    plot_prov_ncd_vs_embed(data)
    return OUT / "PROVENANCE_VS_EMBEDDINGS.md"


if __name__ == "__main__":
    print(f"Wrote {run()}")
