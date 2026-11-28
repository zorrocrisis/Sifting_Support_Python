"""
Control for the breadth/depth dial: does pool redundancy rise with the share just because of how
the pool is built?

As reference_share grows, more of the 12 slots go to the RC, and each RC pair also brings its
reference line (a dialogue line) into the pool. Both could raise redundancy without the RC picking
anything similar. The control fills the RC's slots with *random* session-2 candidates, each paired
with a random dialogue line, and composes the pool exactly as the game does (same AC, same quota,
same composer). If redundancy rises as much with random picks, the rise is construction, not the RC.

Two redundancy measures (mean pairwise 1 - NCD over the pool's descriptions):
  pool              every log in the pool, as A4 measures it
  without dialogue  the same, leaving the dialogue (reference) lines out, so only events count

Compared: the RC as the game runs it (`nearest`, NCD) with the original dialogue and with
provenance, over all 162 session-2 events and over the 43 filtered ones. AC seed 42 for the real
RC (the AC barely changes with the seed); 30 random draws per share for the control.

  python -m experiments.pilot.random_control [--draws 30]

Writes experiments/pilot/out_compare/RANDOM_CONTROL.md, random_control.png and random_control.json.
"""

import argparse
import json

import numpy as np

from experiments.common import ncd, paths
from experiments.common.context import PilotContext
from experiments.common.data import description_of
from experiments.common.report import md_table
from experiments.common.simulate import build_pool

SHARES = (0.0, 0.25, 0.5, 0.75, 1.0)
CANDS = (("all", "all 162 events"), ("filtered", "43 filtered events"))
REAL = (("dialogue", "original dialogue"), ("dialogue_prov", "provenance"))
AC_SEED = 42

COLORS = {"original dialogue": "#2a78d6", "provenance": "#eb6834", "random": "#8a8984"}
TEXT, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"


def redundancies(built, ctx):
    entries = built["entries"]
    descs = [description_of(e["full"]) for e in entries]
    S = 1.0 - ncd.ncd_square(descs)
    pool = ncd.mean_pairwise_sim(range(len(descs)), S)
    events = [i for i, e in enumerate(entries) if e["kind"] != "reference"]
    # Tag-free breadth: distinct AC clusters (NCD 0.5) among the pool's session-2 events.
    clusters = {ctx.clusters[e["e"]] for e in entries if e["kind"] != "reference" and e.get("e") is not None}
    # Dialogue lines take slots, so fewer events (and clusters) by construction: normalise by events.
    n_events = sum(1 for e in entries if e["kind"] != "reference")
    return {"pool": pool, "without_dialogue": ncd.mean_pairwise_sim(events, S),
            "clusters": len(clusters), "cluster_ratio": len(clusters) / n_events if n_events else float("nan"),
            "dialogue_lines": sum(e["kind"] == "reference" for e in entries)}


def context(ref, cand):
    paths.use_reference(ref, cand, "ncd")
    return PilotContext()


def run(draws=30):
    paths.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    results = {}
    for cand, _ in CANDS:
        for ref, name in REAL:
            ctx = context(ref, cand)
            results[(cand, name)] = {str(s): redundancies(build_pool(ctx, s, 12, "nearest", seed=AC_SEED), ctx)
                                     for s in SHARES}
        ctx = context("dialogue", cand)        # the control ignores the reference's scores
        per = {}
        for s in SHARES:
            rs = [redundancies(build_pool(ctx, s, 12, "random", seed=AC_SEED, cc_seed=1000 + k), ctx)
                  for k in range(draws)]
            per[str(s)] = {m: {"mean": float(np.nanmean([r[m] for r in rs])), "sd": float(np.nanstd([r[m] for r in rs]))}
                           for m in ("pool", "without_dialogue", "clusters", "cluster_ratio", "dialogue_lines")}
        results[(cand, "random")] = per

    out_dir = paths.PILOT_DIR / "out_compare"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "random_control.json").write_text(
        json.dumps({f"{c}|{n}": v for (c, n), v in results.items()}, indent=2), encoding="utf-8")
    plot(results, out_dir / "random_control.png", draws)
    return results


def series(results, cand, name, metric):
    d = results[(cand, name)]
    if name == "random":
        return [d[str(s)][metric]["mean"] for s in SHARES], [d[str(s)][metric]["sd"] for s in SHARES]
    return [d[str(s)][metric] for s in SHARES], None


def plot(results, out, draws):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    fig = plt.figure(figsize=(11.5, 12.0), facecolor=SURFACE)
    gs = fig.add_gridspec(4, 2, height_ratios=[4, 4, 4, 1.3])
    ax_leg = fig.add_subplot(gs[3, :])
    ax_leg.axis("off")
    metrics = (("pool", "Pool redundancy (as A4 measures it)"),
               ("without_dialogue", "Redundancy without the dialogue lines"),
               ("cluster_ratio", "Breadth: distinct AC clusters per event"))
    for row, (metric, mtitle) in enumerate(metrics):
        for col, (cand, cname) in enumerate(CANDS):
            ax = fig.add_subplot(gs[row, col])
            ys, sd = series(results, cand, "random", metric)
            lo, hi = np.array(ys) - np.array(sd), np.array(ys) + np.array(sd)
            ax.fill_between(SHARES, lo, hi, color=COLORS["random"], alpha=0.18, lw=0, zorder=1)
            ax.plot(SHARES, ys, color=COLORS["random"], lw=2, ls="--", marker="o", ms=6, zorder=2)
            for _, name in REAL:
                ys, _ = series(results, cand, name, metric)
                ax.plot(SHARES, ys, color=COLORS[name], lw=2, marker="o", ms=8, mec=SURFACE, mew=1.5, zorder=3)
            ax.set_title(f"{mtitle} · {cname}", fontsize=10.5, color=TEXT, loc="left")
            if metric == "cluster_ratio" and cand == "filtered":
                ax.text(0.5, 0.45, "Uninformative here: every filtered candidate is a different\n"
                                   "cluster's representative, so this is 1.00 by construction.",
                        transform=ax.transAxes, ha="center", va="center", fontsize=9, color=MUTED,
                        bbox=dict(facecolor=SURFACE, edgecolor=GRID, pad=6))
            ax.set_xticks(SHARES)
            ax.set_xlim(-0.04, 1.04)
            if metric == "cluster_ratio":
                ax.set_ylim(0.5, 1.03)
                ax.set_ylabel("distinct clusters / events", color=MUTED)
            else:
                ax.set_ylim(0.15, 0.47)
                ax.set_ylabel("mean pairwise 1 − NCD", color=MUTED)
            if row == 2:
                ax.set_xlabel("reference_share (RC's share of the 12 slots)", color=MUTED)
            ax.set_facecolor(SURFACE)
            ax.grid(True, color=GRID, lw=1)
            ax.set_axisbelow(True)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            for side in ("left", "bottom"):
                ax.spines[side].set_color(GRID)
            ax.tick_params(colors=MUTED)

    ax_leg.legend(handles=[Line2D([], [], color=COLORS["original dialogue"], lw=2, marker="o", ms=7,
                                  label="RC, original dialogue (NCD, nearest)"),
                           Line2D([], [], color=COLORS["provenance"], lw=2, marker="o", ms=7,
                                  label="RC, provenance (NCD, nearest)"),
                           Line2D([], [], color=COLORS["random"], lw=2, ls="--", marker="o", ms=6,
                                  label=f"control: random RC picks (mean of {draws} draws)"),
                           Patch(color=COLORS["random"], alpha=0.25, label="control ± 1 sd")],
                  loc="upper left", bbox_to_anchor=(0.0, 1.0), fontsize=8.5, frameon=False, ncol=2,
                  columnspacing=2.5)
    ax_leg.text(0.0, 0.0, "The control fills the RC's slots with random session-2 candidates, each paired with a random "
                          "dialogue line, and builds the pool exactly as the game does (same AC, quota and composer).",
                transform=ax_leg.transAxes, fontsize=9, color=MUTED, ha="left", va="bottom")
    fig.subplots_adjust(left=0.07, right=0.97, top=0.96, bottom=0.03, wspace=0.22, hspace=0.38)
    fig.savefig(out, dpi=140, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--draws", type=int, default=30)
    a = ap.parse_args()
    r = run(a.draws)
    for (cand, name), d in r.items():
        get = (lambda s, m: d[str(s)][m]["mean"]) if name == "random" else (lambda s, m: d[str(s)][m])
        print(f"{cand:8s} {name:18s} pool " + " ".join(f"{get(s, 'pool'):.3f}" for s in SHARES)
              + " | no-dialogue " + " ".join(f"{get(s, 'without_dialogue'):.3f}" for s in SHARES)
              + " | clusters/event " + " ".join(f"{get(s, 'cluster_ratio'):.2f}" for s in SHARES)
              + " | lines " + " ".join(f"{get(s, 'dialogue_lines'):.1f}" for s in SHARES))


if __name__ == "__main__":
    main()
