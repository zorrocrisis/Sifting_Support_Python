"""
NCD helpers for experiments.

Concatenation order: deflate compresses `a + b` and `b + a` to slightly
different sizes, so NCD(d, e) != NCD(e, d) by a little. The game's
reference channel (ncd_data.compute_ncd_distance_matrix_asymmetric) computes
C(event + dialogue). ncd_rect defaults to that order ("event_first") so pilot
rankings match what F11 does in game; "dialogue_first" is available to measure
how much the order matters.
"""

import numpy as np

from experiments.common import paths  # noqa: F401
from compression_algorithms import compress_with_algorithm
from ncd_data import NCD_text, compute_ncd_distance_matrix

EVENT_FIRST = "event_first"
DIALOGUE_FIRST = "dialogue_first"


def compressed_sizes(strings, cache=None):
    cache = {} if cache is None else cache
    for s in strings:
        if s not in cache:
            cache[s] = compress_with_algorithm(s, algorithm="deflate")
    return cache


def ncd_rect(D, E, order=EVENT_FIRST, size_cache=None):
    """
    NCD between every dialogue line in D and every event in E.

    Returns np.ndarray of shape (|D|, |E|). Single-string compressed sizes are
    computed once per string (the game's version recompresses each event for
    every dialogue line; the values are identical).
    """
    if order not in (EVENT_FIRST, DIALOGUE_FIRST):
        raise ValueError(f"order must be {EVENT_FIRST!r} or {DIALOGUE_FIRST!r}")
    sizes = compressed_sizes(list(D) + list(E), size_cache)
    out = np.zeros((len(D), len(E)))
    for i, d in enumerate(D):
        for j, e in enumerate(E):
            if order == EVENT_FIRST:
                out[i, j] = NCD_text(e, d, sizes[e], sizes[d])
            else:
                out[i, j] = NCD_text(d, e, sizes[d], sizes[e])
    return out


def ncd_square(strings):
    """Symmetric n x n NCD matrix (the existing pipeline function)."""
    return compute_ncd_distance_matrix(list(strings))


def mean_pairwise_sim(indices, sim_matrix):
    """Mean of sim_matrix[i, j] over unordered pairs i < j of `indices` (nan if fewer than 2)."""
    idx = list(indices)
    if len(idx) < 2:
        return float("nan")
    vals = [sim_matrix[a, b] for k, a in enumerate(idx) for b in idx[k + 1:]]
    return float(np.mean(vals))
