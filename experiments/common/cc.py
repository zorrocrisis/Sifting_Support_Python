"""
Continuity channel (CC, called RC / "reference channel" in the game code):
ranking current-session events against past dialogue, plus the redundancy
controls tested in pilot A3.

All selectors take M, the (n_dialogue x n_events) NCD matrix from
ncd.ncd_rect, and return an ordered list of pairs:
    {"d": dialogue index, "e": event index, "ncd": float}

Variants
  nearest  -- the game's current behaviour (log_selection.select_final_dialogue_channel_pool):
              globally lowest NCD pairs; the same event may appear in several pairs.
  cap      -- same order, at most `cap` events per dialogue line, each event once.
  mmr      -- Maximal Marginal Relevance (Carbonell & Goldstein, 1998), sim = 1 - NCD:
                score(e) = lam * max_d sim(d, e) - (1 - lam) * max_{s in S} sim(s, e)
              greedy; each event once, paired with its most similar dialogue line.
  cap+mmr  -- mmr where a dialogue line that already has `cap` events can't be the pair partner.
"""

import numpy as np

VARIANTS = ("nearest", "cap", "mmr", "cap+mmr")


def game_pair_order(M):
    """
    Flat order of (d, e) pairs exactly as the game produces it:
    np.argsort on the (events x dialogue) matrix, flattened. Using the same
    array layout and call keeps tie-breaking identical.
    """
    flat = np.argsort(np.ascontiguousarray(M.T), axis=None)
    e_idx, d_idx = np.unravel_index(flat, M.T.shape)
    return [(int(d), int(e)) for e, d in zip(e_idx, d_idx)]


def select_nearest(M, n_pairs):
    order = game_pair_order(M)[:max(0, n_pairs)]
    return [{"d": d, "e": e, "ncd": float(M[d, e])} for d, e in order]


def select_cap(M, n_pairs, cap=2):
    picked, used_e, per_d = [], set(), {}
    for d, e in game_pair_order(M):
        if len(picked) >= n_pairs:
            break
        if e in used_e or per_d.get(d, 0) >= cap:
            continue
        picked.append({"d": d, "e": e, "ncd": float(M[d, e])})
        used_e.add(e)
        per_d[d] = per_d.get(d, 0) + 1
    return picked


def select_mmr(M, S_ee, n_pairs, lam=0.7, cap=None):
    """
    S_ee: (n_events x n_events) similarity between events (1 - NCD).
    Ties are broken by lowest event index, so the result is deterministic.
    """
    sim_de = 1.0 - M
    n_d, n_e = M.shape
    selected, picked, per_d = [], [], {}
    remaining = np.ones(n_e, dtype=bool)

    while len(picked) < n_pairs and remaining.any():
        allowed_d = np.array([cap is None or per_d.get(d, 0) < cap for d in range(n_d)])
        if not allowed_d.any():
            break
        rel_matrix = np.where(allowed_d[:, None], sim_de, -np.inf)
        rel = rel_matrix.max(axis=0)
        red = S_ee[:, selected].max(axis=1) if selected else np.zeros(n_e)
        score = lam * rel - (1 - lam) * red
        score[~remaining] = -np.inf
        e = int(np.argmax(score))
        if not np.isfinite(score[e]):
            break
        d = int(np.argmax(rel_matrix[:, e]))
        picked.append({"d": d, "e": e, "ncd": float(M[d, e]), "mmr_score": float(score[e])})
        selected.append(e)
        remaining[e] = False
        per_d[d] = per_d.get(d, 0) + 1
    return picked


# MMR whose redundancy term uses event-indexing similarity between events (shared entities, place,
# log type, NCD text) instead of 1 - NCD. Only offered when the CC itself scores with event indexing,
# so relevance and redundancy are measured the same way.
INDEX_VARIANTS = ("mmr_ix", "cap+mmr_ix")


def variants_for(similarity_mode):
    return VARIANTS + (INDEX_VARIANTS if similarity_mode == "index" else ())


def select_pairs(variant, M, n_pairs, S_ee=None, cap=2, lam=0.7, S_ee_index=None):
    if variant == "nearest":
        return select_nearest(M, n_pairs)
    if variant == "cap":
        return select_cap(M, n_pairs, cap=cap)
    if variant == "mmr":
        return select_mmr(M, S_ee, n_pairs, lam=lam)
    if variant == "cap+mmr":
        return select_mmr(M, S_ee, n_pairs, lam=lam, cap=cap)
    if variant in INDEX_VARIANTS:
        if S_ee_index is None:
            raise ValueError(f"{variant} needs the event-indexing event x event similarity")
        return select_mmr(M, S_ee_index, n_pairs, lam=lam, cap=cap if variant.startswith("cap") else None)
    raise ValueError(f"unknown CC variant {variant!r}; expected one of {VARIANTS + INDEX_VARIANTS}")


def rank_events(M_row, higher_is_better=False):
    """Event indices for one dialogue line, best first (stable on ties: lower index first)."""
    keys = -M_row if higher_is_better else M_row
    return list(np.argsort(keys, kind="stable"))
