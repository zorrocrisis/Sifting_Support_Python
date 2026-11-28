"""
A1 under strict vs lenient scoring.

Lenient (what the pilot did with filtered candidates): if the RC returns representative Y and a
gold event X is in Y's cluster, X counts as found. Strict: only the exact gold log counts; a gold
event that isn't one of the 43 representatives can never be found. With all 162 events every gold
event can be returned itself, so both scorings are identical there.

Reads the A1 results (run a1_continuity on the filtered configurations first; they store
`metrics_strict`), and writes experiments/pilot/out_compare/STRICT_SCORING.md and
strict_scoring_a1.png.

  python -m experiments.pilot.strict_scoring
"""

import numpy as np

from experiments.common import paths
from experiments.common.context import PilotContext
from experiments.common.gold import read_gold
from experiments.common.report import md_table, read_json

OUT = paths.PILOT_DIR / "out_compare"
LOGGING = (("dialogue", "out", "original dialogue"), ("dialogue_prov", "out_dialogue_prov", "provenance"))
SIMS = (("ncd", "", "NCD"), ("index", "_index", "event indexing"), ("embed", "_embed", "embeddings"))
BARS = (("all", "all 162 events (lenient = strict)"), ("lenient", "43 filtered · lenient"),
        ("strict", "43 filtered · strict"))
COLORS = {"all": "#008300", "lenient": "#6250d6", "strict": "#6250d6"}   # validated pair; strict is hatched
TEXT, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
THRESHOLD = 0.5


def values(metric="recall@5"):
    v = {}
    for _, base, lname in LOGGING:
        for sim, sfx, _ in SIMS:
            a_all = read_json(paths.PILOT_DIR / f"{base}{sfx}" / "a1_result.json")
            a_flt = read_json(paths.PILOT_DIR / f"{base}_filtered{sfx}" / "a1_result.json")
            cc = a_all.get("cc_method", "ncd")
            if "metrics_strict" not in a_flt:
                raise SystemExit(f"{base}_filtered{sfx}: no strict metrics; rerun a1_continuity there first")
            v[(lname, sim)] = {"all": a_all["metrics"][cc][metric], "lenient": a_flt["metrics"][cc][metric],
                               "strict": a_flt["metrics_strict"][cc][metric],
                               "all_status": a_all["status"], "lenient_status": a_flt["status"],
                               "strict_status": a_flt["status_strict"]}
    return v


def ceiling():
    """Best strict Recall@5 / @10 a perfect RC could reach with only the filtered candidates."""
    paths.use_reference("dialogue", "filtered", "ncd")
    c = PilotContext()
    g, _ = read_gold(paths.GOLD_PATH, c)
    m = c.candidate_mask
    reach = {d: sum(bool(m[e]) for e in t) for d, t in g.items()}
    return {k: float(np.mean([min(reach[d], k) / len(t) for d, t in g.items()])) for k in (5, 10)}, \
        sum(reach.values()), sum(len(t) for t in g.values())


def plot(v, ceil5):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    fig = plt.figure(figsize=(12, 5.8), facecolor=SURFACE)
    gs = fig.add_gridspec(2, 2, height_ratios=[4.2, 1.1])
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
    ax_leg = fig.add_subplot(gs[1, :])
    ax_leg.axis("off")
    width, gap = 0.26, 0.03
    for ax, (_, _, lname) in zip(axes, LOGGING):
        for i, (bar, _) in enumerate(BARS):
            xs = [j + (i - 1) * (width + gap) for j in range(len(SIMS))]
            vals = [v[(lname, sim)][bar] for sim, _, _ in SIMS]
            strict = bar == "strict"
            ax.bar(xs, vals, width=width, color=SURFACE if strict else COLORS[bar], edgecolor=COLORS[bar],
                   hatch="///" if strict else None, linewidth=1.8, zorder=3)
            for x, val in zip(xs, vals):
                ax.text(x, val + 0.015, f"{val:.2f}", ha="center", va="bottom", fontsize=8.5, color=TEXT, zorder=4,
                        bbox=dict(facecolor=SURFACE, edgecolor="none", pad=0.8))
        ax.axhline(THRESHOLD, color=MUTED, ls="--", lw=1.5, zorder=2)
        ax.axhline(ceil5, color=COLORS["strict"], ls=":", lw=1.8, zorder=2)
        ax.text(1.01, THRESHOLD, f"pass\n≥ {THRESHOLD}", transform=ax.get_yaxis_transform(), ha="left",
                va="center", fontsize=8.5, color=MUTED)
        ax.text(1.01, ceil5 - 0.01, f"strict\nceiling\n{ceil5:.2f}", transform=ax.get_yaxis_transform(), ha="left",
                va="top", fontsize=8.5, color=COLORS["strict"])
        ax.set_xticks(range(len(SIMS)))
        ax.set_xticklabels([n for _, _, n in SIMS], color=TEXT)
        ax.set_ylim(0, 1.0)
        ax.set_ylabel("A1 Recall@5", color=MUTED)
        ax.set_title(f"RC reference: {lname}", fontsize=11, color=TEXT, loc="left")
        ax.set_facecolor(SURFACE)
        ax.grid(True, axis="y", color=GRID, lw=1)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GRID)
        ax.tick_params(colors=MUTED)

    ax_leg.legend(handles=[Patch(facecolor=COLORS["all"], edgecolor=COLORS["all"], label=BARS[0][1]),
                           Patch(facecolor=COLORS["lenient"], edgecolor=COLORS["lenient"], label=BARS[1][1]),
                           Patch(facecolor=SURFACE, edgecolor=COLORS["strict"], hatch="///", label=BARS[2][1]),
                           Line2D([], [], color=MUTED, ls="--", lw=1.5, label="A1 pass threshold"),
                           Line2D([], [], color=COLORS["strict"], ls=":", lw=1.8,
                                  label="best strict Recall@5 possible with 43 candidates")],
                  loc="upper left", bbox_to_anchor=(0.0, 1.0), fontsize=8.5, frameon=False, ncol=3,
                  columnspacing=2.0)
    ax_leg.text(0.0, 0.0, "Lenient: returning a gold event's cluster representative counts as finding it. "
                          "Strict: only the exact gold log counts.",
                transform=ax_leg.transAxes, fontsize=9, color=MUTED, ha="left", va="bottom")
    fig.subplots_adjust(left=0.06, right=0.93, top=0.94, bottom=0.03, wspace=0.3, hspace=0.3)
    fig.savefig(OUT / "strict_scoring_a1.png", dpi=140, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    v, v10 = values("recall@5"), values("recall@10")
    vm = values("mrr")
    ceil, reach, n_gold = ceiling()
    plot(v, ceil[5])

    rows = []
    for _, _, lname in LOGGING:
        for sim, _, sname in SIMS:
            x = v[(lname, sim)]
            rows.append([lname, sname, f"{x['all']:.2f} ({x['all_status']})", f"{x['lenient']:.2f} ({x['lenient_status']})",
                         f"{x['strict']:.2f} ({x['strict_status']})", f"{vm[(lname, sim)]['lenient']:.2f} → "
                         f"{vm[(lname, sim)]['strict']:.2f}"])
    p = {s: v[("provenance", s)] for s, _, _ in SIMS}
    L = ["# A1 under strict scoring", "",
         "**Review point:** with filtered candidates the pilot scored leniently. If the RC returns representative Y "
         "and gold event X is in Y's cluster, X counts as found. **Strict scoring** counts a hit only when the "
         "returned log *is* the gold event. With all 162 events every gold event can be returned itself, so the two "
         "scorings only differ with the 43 filtered candidates.", "",
         "![strict vs lenient](strict_scoring_a1.png)", "",
         "## A1 Recall@5 (pass ≥ 0.5)", "",
         md_table(["reference", "similarity", "162 events", "43 · lenient", "43 · strict", "MRR 43: lenient → strict"],
                  rows), "",
         f"**Ceiling:** only {reach} of the {n_gold} gold events are among the 43 representatives, so even a perfect RC "
         f"would reach at most Recall@5 {ceil[5]:.2f} (Recall@10 {ceil[10]:.2f}) under strict scoring. Every dialogue line "
         "has at least one reachable gold event.", "",
         "## What it shows", "",
         "- **Strict scoring roughly halves recall with filtered candidates.** Provenance falls from 0.65–0.75 to "
         f"{min(x['strict'] for x in p.values()):.2f}–{max(x['strict'] for x in p.values()):.2f}, below the pass threshold.",
         f"- **But the threshold is out of reach by construction.** The strict ceiling is {ceil[5]:.2f}. Relative to it, "
         f"provenance gets {min(x['strict'] for x in p.values()) / ceil[5]:.0%}–{max(x['strict'] for x in p.values()) / ceil[5]:.0%} "
         "of what is possible, so it still ranks the reachable gold events well. "
         "MRR also drops less than recall (NCD 0.74 → 0.62): the first hit usually stays near the top.",
         "- **With all 162 events, scoring doesn't matter and provenance passes** with NCD "
         f"({p['ncd']['all']:.2f}) and embeddings ({p['embed']['all']:.2f}); event indexing ({p['index']['all']:.2f}) is just short.",
         "- **The lenient A1 advantage of filtering is a scoring artefact.** Filtering raised lenient Recall@5 "
         f"(NCD {p['ncd']['all']:.2f} → {p['ncd']['lenient']:.2f}); strictly it lowers it ({p['ncd']['strict']:.2f}).", "",
         "## Consequence for the implementation steps", "",
         "- **Step 2 (43 filtered candidates by default) should be revisited.** Its A1 gain doesn't hold under strict "
         "scoring. Its other benefit, lower redundancy, mattered for the original dialogue. With provenance, though, "
         "redundancy is already at the random level with all 162 events (`RANDOM_CONTROL.md`).",
         "- **Revised recommendation:** with provenance, let the RC pick from **all** events by default. Keep filtering as "
         "an option for long sessions, where comparing against thousands of distinct logs gets expensive, and score it "
         "strictly when it's used.",
         "- **For the paper:** report strict scoring as the main A1 number, with lenient as a secondary reading, and "
         "state the ceiling whenever candidates are filtered.", ""]
    (OUT / "STRICT_SCORING.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return OUT / "STRICT_SCORING.md"


if __name__ == "__main__":
    print(f"Wrote {run()}")
