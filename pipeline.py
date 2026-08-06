"""
pipeline.py
-----------
The log-processing + hierarchical-clustering pipeline, decoupled from
the Panel dashboard. This module does NOT import panel/plotly, so it's
safe (and fast) to call from a headless context -- e.g. the C# RimWorld
mod invoking `python main_demo.py preprocess` just to get the
deduplicated logs back, with no browser window ever opening.

Call run_preprocessing() to get everything the dashboard (or a headless
caller) needs; pass its result into dashboard.build_dashboard() for the
full UI.
"""

from scipy.cluster.hierarchy import linkage, to_tree
from scipy.spatial.distance import squareform

import config
from ncd_data import build_earliest_full_log_index, compute_ncd_distance_matrix, extract_descriptions, load_character_bios, load_unique_logs, log_dictionary_ids, temporal_sort_key
from tree_utils import build_zoomed_view


def resolve_input_paths():
    """
    Decide where to read logs/bios from:
      - config.RUNNING_WITHIN_GAME=True: paths sent over stdin by the
        game (see config.get_input_paths).
      - otherwise: the hardcoded case-study file paths in config.py.
    """
    if config.RUNNING_WITHIN_GAME:
        return config.get_input_paths()
    return config.FULL_LOG_FILE, config.CHARACTERS_BIOS_LOG_FILE


def run_preprocessing(full_log=None, characters_bios_log=None, ncd_threshold=None):
    """
    Load + deduplicate the logs, compute the full NCD distance matrix,
    and build the ONE canonical hierarchical-clustering tree. This is
    the expensive, one-time part of the pipeline -- run it once and
    reuse the result (e.g. across dashboard redraws, or just once for a
    headless preprocess call).

    Parameters
    ----------
    full_log, characters_bios_log : str or None
        File paths to use. If any is omitted (None), both are
        resolved via resolve_input_paths() instead (explicit paths are
        all-or-nothing, since mixing resolved + provided paths could
        silently pair mismatched files).
    ncd_threshold : float or None
        Initial NCD "zoom" threshold for the returned view_data.
        Defaults to config.INITIAL_NCD_THRESHOLD.

    Returns
    -------
    dict with keys:
        full_log, short_log, characters_bios_log : the resolved paths used
        characters_bios : str
        log_dict : dict[str, str]                    (full log -> short log text; many-to-one)
        short_to_full : dict[str, str]                (short log -> its earliest matching full log text)
        unique_logs : list[str]
        counts : OrderedDict[str, int]
        visibility : OrderedDict[str, str]            ("V" or "NV" per unique log)
        log_to_temporal_key : dict[str, float]        (real timestamp, or +inf)
        log_to_temporal_index : dict[str, int]        (file-order fallback)
        distance_matrix : np.ndarray, shape (n, n)
        Z_0 : linkage matrix
        root_0 : ClusterNode                          (the ONE canonical tree)
        view_data : dict                              (see tree_utils.build_zoomed_view)
    """
    if full_log is None or characters_bios_log is None:
        full_log, characters_bios_log = resolve_input_paths()

    if ncd_threshold is None:
        ncd_threshold = config.INITIAL_NCD_THRESHOLD

    characters_bios = load_character_bios(characters_bios_log)
    short_log = extract_descriptions(full_log)

    log_dict = log_dictionary_ids(short_log, full_log)
    unique_logs, counts, visibility = load_unique_logs(full_log, log_dict, max_lines=config.MAX_LOG_LINES)

    # For each unique (short) log, find its chronologically-earliest
    # matching full-length log line -- in ONE pass over log_dict, not
    # one pass per unique log (see ncd_data.build_earliest_full_log_index
    # for why that distinction matters at real game-log scale). This
    # serves double duty:
    #   - log_to_temporal_key: sort key for reordering a selected log
    #     pool back into the order events actually happened.
    #   - short_to_full: which REAL full-length log line to display for
    #     a given short log (dashboard.py / log_selection.py use this
    #     instead of indexing log_dict directly, since log_dict is now
    #     keyed the other way around -- full_log -> short_log -- and is
    #     many-to-one, so there's no single "the" full text to look up
    #     by short text without picking one; we pick the earliest).
    short_to_full = build_earliest_full_log_index(log_dict)
    log_to_temporal_key = {log: temporal_sort_key(short_to_full[log]) for log in unique_logs}
    log_to_temporal_index = {log: idx for idx, log in enumerate(unique_logs)}

    # Full NCD distance matrix + ONE canonical tree, computed once.
    # Any "zoom" over this tree (see tree_utils.build_zoomed_view /
    # collapse_tree_at_threshold) never rebuilds it.
    distance_matrix = compute_ncd_distance_matrix(unique_logs)  # square (n x n)
    distances = squareform(distance_matrix)                     # condensed
    Z_0 = linkage(distances, method="average")
    root_0 = to_tree(Z_0)

    view_data = build_zoomed_view(
        root_0, unique_logs, counts, distance_matrix,
        threshold=ncd_threshold, log_dict=log_dict
    )

    return {
        "full_log": full_log,
        "short_log": short_log,
        "characters_bios_log": characters_bios_log,
        "characters_bios": characters_bios,
        "log_dict": log_dict,
        "short_to_full": short_to_full,
        "counts": counts,
        "unique_logs": unique_logs,
        "visibility": visibility,
        "log_to_temporal_key": log_to_temporal_key,
        "log_to_temporal_index": log_to_temporal_index,
        "distance_matrix": distance_matrix,
        "Z_0": Z_0,
        "root_0": root_0,
        "view_data": view_data
    }