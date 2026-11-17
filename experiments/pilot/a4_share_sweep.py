"""
Pilot A4 (part 2) -- is reference_share a breadth/depth dial? (no LLM)

  python -m experiments.pilot.a4_share_sweep [--variant mmr] [--seeds 41 42 43 44 45]

Grid: reference_share in {0, 0.25, 0.5, 0.75, 1} x seeds x CC variant
{nearest, best of A3}, total_log_count = 12, AC parameters as in the game's
sifting_parameters.txt (threshold 0.5, least_frequent, depth 1).

Seeds only affect the AC; the CC ranking is deterministic.

Per pool: distinct topics (from the author's topic_tags.csv; empty until
tagged), redundancy (mean pairwise 1-NCD over the pool), dialogue lines used,
AC-CC overlap (CC candidate events the AC also returned).

Creates experiments/pilot/topic_tags.csv (every pooled description, topic column
empty) if it doesn't exist. Once it exists it is the author's file and is never
rewritten; pooled descriptions it doesn't tag are listed in out/topic_tags_missing.csv.
Topics filled in there are read too, and a missing file with any topic in it is never rewritten.

Pass (operationalised): Spearman rho(share, distinct topics) <= --pass-rho
(default -0.7) over all runs of a variant. Pending until every pooled
description has a topic.

Outputs: a4_runs.csv, a4_pools.jsonl, a4_metrics.png, a4_result.json, a4_report.md
"""

import argparse
import json
from collections import Counter

import numpy as np

from experiments.common import paths
from experiments.common.context import PilotContext
from experiments.common.data import description_of
from experiments.common.report import md_table, read_json, write_csv, write_json
from experiments.common.simulate import build_pool, pool_metrics
from experiments.common.topics import read_all_topics, write_topic_template

SHARES = (0.0, 0.25, 0.5, 0.75, 1.0)
SEEDS = (41, 42, 43, 44, 45)
TOPIC_PATH = paths.PILOT_DIR / "topic_tags.csv"
METRICS = ("distinct_topics", "distinct_topics_primary", "redundancy", "dialogue_lines", "ac_cc_overlap")


def best_variant_from_a3():
    r = read_json(paths.OUT_DIR / "a3_result.json")
    return r["best_variant"] if r else None


def run(variant=None, seeds=SEEDS, shares=SHARES, total=12, pass_rho=-0.7):
    from scipy.stats import spearmanr
    paths.ensure_out()
    best = variant or best_variant_from_a3() or "mmr"
    variants = ["nearest"] + ([best] if best != "nearest" else [])
    ctx = PilotContext()

    built_all = []
    for v in variants:
        for share in shares:
            for seed in seeds:
                built_all.append(build_pool(ctx, share, total, variant=v, seed=seed))

    # Topic template: every description that appears in any pool
    desc_counts = Counter(description_of(e["full"]) for b in built_all for e in b["entries"])
    missing_path = paths.OUT_DIR / "topic_tags_missing.csv"
    untagged_total = write_topic_template(TOPIC_PATH, dict(desc_counts), missing_path)
    topic_of, unknown_topics = read_all_topics(TOPIC_PATH, missing_path)

    rows = []
    with open(paths.OUT_DIR / "a4_pools.jsonl", "w", encoding="utf-8") as f:
        for b in built_all:
            m = pool_metrics(ctx, b, topic_of=topic_of)
            rows.append({"variant": b["variant"], "share": b["share"], "seed": b["seed"], **m})
            f.write(json.dumps({"variant": b["variant"], "share": b["share"], "seed": b["seed"],
                                "pool": b["pool"],
                                "entries": [{"channel": e["channel"], "kind": e["kind"], "full": e["full"]}
                                            for e in b["entries"]]}, ensure_ascii=False) + "\n")
    write_csv(paths.OUT_DIR / "a4_runs.csv", rows)

    summary = {}
    for v in variants:
        vr = [r for r in rows if r["variant"] == v]
        per_share = {}
        for share in shares:
            sr = [r for r in vr if r["share"] == share]
            per_share[share] = {m: _mean_std([r[m] for r in sr]) for m in METRICS}
        tagged = all(r["distinct_topics"] is not None for r in vr)
        rho = rho_primary = None
        if tagged:
            rho = float(spearmanr([r["share"] for r in vr], [r["distinct_topics"] for r in vr]).statistic)
            rho_primary = float(spearmanr([r["share"] for r in vr],
                                          [r["distinct_topics_primary"] for r in vr]).statistic)
        summary[v] = {"per_share": per_share, "spearman_share_topics": rho,
                      "spearman_share_topics_primary": rho_primary,
                      "passes": (rho is not None and rho <= pass_rho) if tagged else None,
                      "spearman_share_redundancy": float(spearmanr([r["share"] for r in vr],
                                                                   [r["redundancy"] for r in vr]).statistic)}

    if any(summary[v]["passes"] is None for v in variants):
        status = "pending"
    elif all(summary[v]["passes"] for v in variants):
        status = "pass"
    elif any(summary[v]["passes"] for v in variants):
        status = "partial"
    else:
        status = "fail"

    result = {"test": "A4", "variants": variants, "seeds": list(seeds), "shares": list(shares), "total": total,
              "status": status, "pass_rule": f"Spearman rho(share, distinct topics) <= {pass_rho}",
              "untagged_descriptions": untagged_total, "unknown_topic_labels": unknown_topics,
              "summary": summary}
    if status == "pending":
        result["status_reason"] = (f"{untagged_total} pooled descriptions have no topic in topic_tags.csv "
                                   "(listed in out/topic_tags_missing.csv)")
    write_json(paths.OUT_DIR / "a4_result.json", result)
    plot(rows, variants, shares)
    write_report(result)
    return result


def _mean_std(vals):
    vals = [v for v in vals if v is not None and not (isinstance(v, float) and np.isnan(v))]
    if not vals:
        return {"mean": None, "std": None}
    return {"mean": float(np.mean(vals)), "std": float(np.std(vals))}


def plot(rows, variants, shares):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, len(METRICS), figsize=(4 * len(METRICS), 3.4))
    for ax, metric in zip(axes, METRICS):
        for v in variants:
            means, stds, xs = [], [], []
            for s in shares:
                vals = [r[metric] for r in rows if r["variant"] == v and r["share"] == s and r[metric] is not None]
                if vals:
                    xs.append(s)
                    means.append(np.mean(vals))
                    stds.append(np.std(vals))
            if xs:
                ax.errorbar(xs, means, yerr=stds, marker="o", capsize=3, label=v)
        ax.set_title(metric.replace("_", " "))
        ax.set_xlabel("reference_share")
        ax.set_xticks(list(shares))
        if not any(r[metric] is not None for r in rows):
            ax.text(0.5, 0.5, "pending\n(topics not tagged)", ha="center", va="center", transform=ax.transAxes)
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(paths.OUT_DIR / "a4_metrics.png", dpi=130)
    plt.close(fig)


def write_report(result):
    def fmt(ms):
        return "–" if ms["mean"] is None else f"{ms['mean']:.2f} ± {ms['std']:.2f}"

    L = ["# A4 — Ratio as a dial (no LLM)", "",
         f"**Status: {result['status'].upper()}**"
         + (f" — {result['status_reason']}" if result.get("status_reason") else ""), "",
         f"Shares {result['shares']} × seeds {result['seeds']} × variants {result['variants']}, total "
         f"{result['total']}. Pass rule: {result['pass_rule']}.", "",
         "Parity with the game's composition: see `a4_parity.md`.", "", "![metrics](a4_metrics.png)", ""]
    if result["unknown_topic_labels"]:
        L += [f"Unknown topic labels in topic_tags.csv: {', '.join(result['unknown_topic_labels'])}", ""]
    for v, s in result["summary"].items():
        rho, rho_p = s["spearman_share_topics"], s["spearman_share_topics_primary"]
        L += [f"## `{v}`", "",
              "Spearman ρ(share, distinct topics): " + ("–" if rho is None else f"{rho:.2f}")
              + " (first label only: " + ("–" if rho_p is None else f"{rho_p:.2f}") + ")"
              + f"; ρ(share, redundancy): {s['spearman_share_redundancy']:.2f}", "",
              md_table(["share"] + list(METRICS),
                       [[sh] + [fmt(s["per_share"][sh][m]) for m in METRICS] for sh in s["per_share"]]), ""]
    (paths.OUT_DIR / "a4_report.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variant", help="CC variant to compare with nearest (default: best from A3)")
    ap.add_argument("--seeds", type=int, nargs="+", default=list(SEEDS))
    ap.add_argument("--pass-rho", type=float, default=-0.7)
    a = ap.parse_args()
    r = run(a.variant, tuple(a.seeds), pass_rho=a.pass_rho)
    print(f"A4: {r['status']} ({r.get('status_reason', '')})")


if __name__ == "__main__":
    main()
