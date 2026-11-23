"""
Anomaly channel (AC) runs and final-pool composition, reproducing the C# side
so share sweeps can run without the game.

Ported from the mod:
  SiftingParameters.GetPipelineTargets   -> pipeline_targets
  PythonBridge (story pipeline, F11)     -> AC request = total; CC request = 2*quota + 2 pairs
  FinalPoolComposer.RankByAnomaly        -> rank_by_anomaly
  FinalPoolComposer.Compose              -> compose_pool
  SiftingChannelsUtils.SiftLogs          -> merge_pool (merge reference-first, stable sort by
                                            timestamp, dedup by _ID_, reduce to description)
"""

import math

from experiments.common import paths  # noqa: F401
from experiments.common.data import dedup_key, description_of
import pipeline
from log_selection import select_final_log_pool

DEFAULT_AC_PARAMS = {
    "ncd_threshold": 0.5,
    "strategy": "least_frequent",
    "depth": 1,
}


def round_half_away(x):
    """C# Math.Round(x, MidpointRounding.AwayFromZero) for x >= 0."""
    return int(math.floor(x + 0.5))


def pipeline_targets(total, share):
    share = max(0.0, min(1.0, float(share)))
    total = max(0, int(total))
    quota = round_half_away(total * share)
    return total, quota


def cc_pair_request(quota):
    return quota * 2 + 2 if quota > 0 else 0


# ---------------------------------------------------------------------------
# Anomaly channel
# ---------------------------------------------------------------------------
_PREPROCESS_CACHE = {}


def preprocess(events_logset, seed=42):
    """pipeline.run_preprocessing on the staged event log (cached per file)."""
    key = str(events_logset.path)
    if key not in _PREPROCESS_CACHE:
        _PREPROCESS_CACHE[key] = pipeline.run_preprocessing(key, seed=seed)
    return _PREPROCESS_CACHE[key]


def run_ac(events_logset, total, seed, ac_params=None):
    """
    The AC request the F11 pipeline makes: control=target_count, target_count=total.
    Returns the select result plus `ranked_full` (RankByAnomaly order).
    """
    p = {**DEFAULT_AC_PARAMS, **(ac_params or {})}
    state = preprocess(events_logset)
    sel = select_final_log_pool(
        state, ncd_threshold=p["ncd_threshold"], control="target_count",
        strategy=p["strategy"], depth=p["depth"], target_count=total, seed=seed)
    if sel.get("error"):
        raise RuntimeError(f"AC selection failed: {sel['error']}")
    sel["counts"] = state["counts"]
    sel["ranked_full"] = rank_by_anomaly(sel["final_log_pool_short"], sel["final_log_pool_full"], state["counts"])
    return sel


def rank_by_anomaly(short_logs, full_logs, counts):
    """Least frequent first; ties keep their original (chronological) order."""
    def freq(i):
        return counts.get(short_logs[i], 0) if i < len(short_logs) else 0
    order = sorted(range(len(full_logs)), key=lambda i: (freq(i), i))
    return [full_logs[i] for i in order]


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------
def compose_pool(reference_pairs, ranked_anomaly, total, reference_quota):
    """
    Port of FinalPoolComposer.Compose.

    reference_pairs: list of (event_full, reference_full) in CC order.
    ranked_anomaly:  AC full logs, most anomalous first.
    Returns (reference_logs, anomaly_logs), lists of full lines.
    """
    picked = set()
    reference_logs, anomaly_logs = [], []

    def new_lines(*lines):
        out, seen_here = [], set()
        for line in lines:
            if not line or not line.strip():
                continue
            k = dedup_key(line)
            if k in seen_here:
                continue
            seen_here.add(k)
            if k not in picked:
                out.append(line)
        return out

    def take(target, line):
        picked.add(dedup_key(line))
        target.append(line)

    # 1. Reference channel, up to its quota
    reference_quota = min(reference_quota, total)
    for ev, ref in reference_pairs:
        if len(reference_logs) >= reference_quota:
            break
        nl = new_lines(ev, ref)
        if not nl or len(reference_logs) + len(nl) > reference_quota:
            continue
        for line in nl:
            take(reference_logs, line)

    # 2. Anomaly channel fills the rest
    for line in ranked_anomaly:
        if len(reference_logs) + len(anomaly_logs) >= total:
            break
        if len(new_lines(line)) == 1:
            take(anomaly_logs, line)

    # 3. Not enough anomaly logs: top up with leftover reference lines
    for ev, ref in reference_pairs:
        for line in new_lines(ev, ref):
            if len(reference_logs) + len(anomaly_logs) >= total:
                return reference_logs, anomaly_logs
            take(reference_logs, line)

    return reference_logs, anomaly_logs


def _timestamp(full_line):
    from experiments.common.data import parse_line
    p = parse_line(full_line)
    if p is None:
        raise ValueError(f"line has no timestamp: {full_line[:120]}")
    return p["ts"]


def merge_pool(reference_logs, anomaly_logs, label_suffix):
    """
    Port of SiftingChannelsUtils.SiftLogs on the two written files.
    label_suffix(full_line) -> "[xN][V]" (what FormatLogsWithCountsAndVisibility appends).
    Returns the pool as the LLM sees it: "description[xN][V/NV]" lines, oldest first.
    """
    lines = list(reference_logs) + list(anomaly_logs)
    lines = sorted(enumerate(lines), key=lambda t: (_timestamp(t[1]), t[0]))
    seen, out = set(), []
    for _, line in lines:
        k = dedup_key(line)
        if k in seen:
            continue
        seen.add(k)
        out.append(description_of(line) + label_suffix(line))
    return out
