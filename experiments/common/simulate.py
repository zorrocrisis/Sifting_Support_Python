"""
Simulate the game's F11 sifting step offline: AC + CC + composition + merge,
with the CC variant, masking and share as parameters.
"""

from experiments.common import cc, ncd
from experiments.common.data import dedup_key, description_of
from experiments.common.pool import (cc_pair_request, compose_pool, merge_pool,
                                     pipeline_targets, run_ac)


def build_pool(ctx, share, total=12, variant="nearest", seed=42, masked=False,
               cap=2, lam=0.7, ac_params=None, cc_seed=None):
    """
    cc_seed: random seed for the `random` CC variant (the control); defaults to `seed`.
    """
    total, quota = pipeline_targets(total, share)
    n_pairs = cc_pair_request(quota)
    M = ctx.M_masked if masked else ctx.M

    S_ix = ctx.S_ee_index if variant in cc.INDEX_VARIANTS else None
    pairs = cc.select_pairs(variant, M, n_pairs, S_ee=ctx.S_ee, cap=cap, lam=lam, S_ee_index=S_ix,
                            seed=seed if cc_seed is None else cc_seed) if n_pairs else []
    pair_lines = ctx.pair_lines(pairs)

    ac = run_ac(ctx.events, total, seed, ac_params)
    ref_logs, ac_logs = compose_pool(pair_lines, ac["ranked_full"], total, quota)
    pool = merge_pool(ref_logs, ac_logs, ctx.label_suffix)

    ev_index = {desc: i for i, desc in enumerate(ctx.events.unique)}
    dl_index = {desc: i for i, desc in enumerate(ctx.dialogue.unique)}

    # Attribute each CC event in the pool to its first pair
    first_pair = {}
    for p, (ev_line, _) in zip(pairs, pair_lines):
        first_pair.setdefault(dedup_key(ev_line), p)

    # A CC line is a reference line if it came in as the reference half of a pair (past dialogue,
    # or an earlier-session event when the reference set is events), otherwise a session-2 event.
    reference_lines = {ref for _, ref in pair_lines}

    entries = []
    for line in ref_logs:
        desc = description_of(line)
        if line in reference_lines:
            entries.append({"channel": "CC", "kind": "reference", "full": line, "d": dl_index.get(desc)})
        else:
            p = first_pair.get(dedup_key(line))
            entries.append({"channel": "CC", "kind": "event", "full": line, "e": ev_index.get(desc),
                            "paired_d": p["d"] if p else None, "ncd": p["ncd"] if p else None})
    for line in ac_logs:
        entries.append({"channel": "AC", "kind": "event", "full": line, "e": ev_index.get(description_of(line))})

    ac_keys = {dedup_key(l) for l in ac["ranked_full"]}
    cc_keys = {dedup_key(ev) for ev, _ in pair_lines}
    return {
        "share": share, "total": total, "quota": quota, "variant": variant, "seed": seed,
        "masked": masked, "n_pairs_requested": n_pairs,
        "pairs": pairs, "entries": entries, "pool": pool,
        "ac_candidates": ac["ranked_full"],
        # Overlap = CC candidate events that the AC also returned (the composed pool is deduplicated,
        # so overlap can only be seen at candidate level).
        "ac_cc_overlap": len(ac_keys & cc_keys),
    }


def pool_metrics(ctx, built, topic_of=None):
    """
    Metrics for one composed pool.
      redundancy      mean pairwise 1-NCD over all pool descriptions (dialogue included)
      cc_redundancy   same, over the CC events only
      dialogue_lines  number of past dialogue lines in the pool
      distinct_topics number of distinct author topics (None while topics are untagged)
    """
    entries = built["entries"]
    descs = [description_of(e["full"]) for e in entries]
    S = 1.0 - ncd.ncd_square(descs)
    redundancy = ncd.mean_pairwise_sim(range(len(descs)), S)

    cc_events = [e["e"] for e in entries if e["channel"] == "CC" and e["kind"] == "event" and e["e"] is not None]
    cc_red = ncd.mean_pairwise_sim(cc_events, ctx.S_ee)

    contributing = {e["d"] for e in entries if e["kind"] == "reference"}
    out = {
        "pool_size": len(entries),
        "n_cc": sum(e["channel"] == "CC" for e in entries),
        "n_ac": sum(e["channel"] == "AC" for e in entries),
        "n_cc_events": len(cc_events),
        "dialogue_lines": len(contributing),
        "redundancy": redundancy,
        "cc_redundancy": cc_red,
        "ac_cc_overlap": built["ac_cc_overlap"],
        "distinct_topics": None,           # multi-topic tags count every topic they name
        "distinct_topics_primary": None,   # multi-topic tags count only their first topic
        "untagged": None,
    }
    if topic_of is not None:
        from experiments.common.topics import split_topics
        topics = [topic_of.get(d) for d in descs]
        out["untagged"] = sum(t is None for t in topics)
        if out["untagged"] == 0:
            out["distinct_topics"] = len({x for t in topics for x in split_topics(t)})
            out["distinct_topics_primary"] = len({split_topics(t)[0] for t in topics})
    return out
