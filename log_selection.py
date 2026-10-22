"""
log_selection.py
-----------------
Selects a "final log pool" -- a representative, chronologically-ordered
subset of logs -- from an already-built pipeline state (see
pipeline.run_preprocessing), given the same NCD threshold / traversal
control / branch-selection strategy / seed knobs the dashboard exposes.

Split into two levels:
  - select_leaf_ids(): the core tree-traversal choice (which leaves,
    which edges to highlight). Used by dashboard.py, which also needs
    `root`/`depth_map`/edges for rendering the figure.
  - select_final_log_pool(): a headless-friendly wrapper that also
    handles the NCD "zoom" step and temporal sorting/formatting, with
    no dependency on Panel or any figure. Used by sipport.py's
    "select" CLI mode.

Both entry points share the exact same traversal algorithm, so the
dashboard and the headless C#-facing CLI can never silently disagree
about which logs get selected.
"""

from tree_utils import build_zoomed_view, collect_frontier_with_early_leaves, path_to_leaf
from traversal_strategies import random_leaves_after_depth, rare_logs_after_depth, compute_depth_from_target_count


def select_leaf_ids(root, depth_map, freq_map, control="fixed_depth", strategy="random", depth=1, target_count=2, seed=42):
    """
    Choose which leaves (by id, into the CURRENT zoomed tree) make up
    the final log pool, and which edges should be highlighted to show
    how the traversal reached them.

    Parameters
    ----------
    control : "fixed_depth" | "target_count"
        "fixed_depth": start traversal at `depth`.
        "target_count": pick the depth that yields ~`target_count` logs.
    strategy : "random" | "least_frequent"
        Branch selection strategy at each split below the starting depth.

    Returns
    -------
    resolved_depth : int      -- the depth actually used (echoes `depth`
                                  unless control == "target_count")
    leaf_ids : list[int]      -- deduplicated, in TRAVERSAL order (not
                                  yet sorted chronologically -- see
                                  sort_leaf_ids_temporally)
    traversed_edges : set[(int, int)]
    """
    max_depth = max(depth_map.values())
    depth = max(0, min(depth, max_depth))

    resolved_depth = depth
    if control == "target_count":
        resolved_depth = compute_depth_from_target_count(root, depth_map, target_count)

    frontier_nodes, early_leaf_nodes = collect_frontier_with_early_leaves(root, depth_map, resolved_depth)

    if strategy == "least_frequent":
        leaf_ids, traversed_edges = rare_logs_after_depth(
            root=root, depth_map=depth_map, freq_map=freq_map, target_depth=resolved_depth, seed=seed
        )
    else:
        leaf_ids, traversed_edges = random_leaves_after_depth(
            root=root, depth_map=depth_map, target_depth=resolved_depth, seed=seed
        )

    for leaf in early_leaf_nodes:
        leaf_ids.append(leaf.id)
        traversed_edges.update(path_to_leaf(root, leaf.id))

    # Deduplicate while preserving first-seen (traversal) order.
    leaf_ids = list(dict.fromkeys(leaf_ids))

    return resolved_depth, leaf_ids, traversed_edges


def sort_leaf_ids_temporally(leaf_ids, unique_logs_after_filtering, log_to_temporal_key, log_to_temporal_index):
    """
    Reorder leaf ids chronologically: by each log's real embedded
    timestamp, falling back to its original file position for logs
    with no timestamp tag (see ncd_data.temporal_sort_key) -- so
    ordering stays deterministic either way.
    """
    return sorted(leaf_ids, key=lambda i: (
        log_to_temporal_key[unique_logs_after_filtering[i]],
        log_to_temporal_index[unique_logs_after_filtering[i]],
    ))


def select_final_log_pool(pipeline_state, ncd_threshold, control="fixed_depth", strategy="random", depth=1, target_count=2, seed=42):
    """
    Headless-friendly entry point: given a pipeline_state (from
    pipeline.run_preprocessing) and the same knobs the dashboard
    exposes, zoom the tree to `ncd_threshold`, select a final log pool,
    and return everything as plain data (no ClusterNode/figure objects),
    ready to serialize as JSON for the C# side.

    Parameters
    ----------
    pipeline_state : dict
        Output of pipeline.run_preprocessing().
    ncd_threshold : float
        "Zoom" threshold -- which NCD-collapsed tree to select from.
    control, strategy, depth, target_count, seed : see select_leaf_ids().

    Returns
    -------
    dict with keys:
        ncd_threshold, control, strategy, depth, target_count, seed : echoed inputs
        resolved_depth : int or None            -- None if selection failed (see `error`)
        unique_logs_after_filtering : list[str] -- the NCD-collapsed representative logs
        most_anomalous_log, highest_ncd : from the zoomed view
        final_log_pool_short : list[str]        -- short/description log text, chronological
        final_log_pool_full : list[str]         -- corresponding full log text
        final_log_pool_labels : list[str]       -- "log text (xN)" labels, as shown in the dashboard
        error : str or None                     -- set (with the pool lists empty) if fewer
                                                    than 2 logs survive NCD filtering
    """
    root_0 = pipeline_state["root_0"]
    unique_logs = pipeline_state["unique_logs"]
    counts = pipeline_state["counts"]
    distance_matrix = pipeline_state["distance_matrix"]
    log_dict = pipeline_state["log_dict"]
    short_to_full = pipeline_state["short_to_full"]
    log_to_temporal_key = pipeline_state["log_to_temporal_key"]
    log_to_temporal_index = pipeline_state["log_to_temporal_index"]

    view_data = build_zoomed_view(
        root_0, unique_logs, counts, distance_matrix,
        threshold=ncd_threshold, log_dict=log_dict,
        seed=seed
    )

    unique_logs_after_filtering = view_data["unique_logs_after_filtering"]
    most_anomalous_log = view_data["most_anomalous_log"]
    highest_NCD = view_data["highest_NCD"]

    base_result = {
        "unique_logs_after_filtering": unique_logs_after_filtering,
        "ncd_threshold": ncd_threshold,
        "control": control,
        "strategy": strategy,
        "depth": depth,
        "target_count": target_count,
        "seed": seed,
        "most_anomalous_log": most_anomalous_log,
        "highest_ncd": highest_NCD,
    }

    if len(unique_logs_after_filtering) < 2:
        return {
            **base_result,
            "resolved_depth": None,
            "final_log_pool_short": [],
            "final_log_pool_full": [],
            "final_log_pool_labels": [],
            "error": "Fewer than 2 logs remain after NCD filtering at this threshold.",
        }

    root = view_data["root"]
    depth_map = view_data["depth_map"]
    freq_map = view_data["freq_map"]
    labels = view_data["labels"]

    # Clamp target_count into range, mirroring the dashboard's slider guard.
    target_count = max(1, min(target_count, len(unique_logs_after_filtering)))

    resolved_depth, leaf_ids, _traversed_edges = select_leaf_ids(
        root, depth_map, freq_map, control=control, strategy=strategy,
        depth=depth, target_count=target_count, seed=seed
    )

    leaf_ids = sort_leaf_ids_temporally(leaf_ids, unique_logs_after_filtering, log_to_temporal_key, log_to_temporal_index)

    final_log_pool_short = [unique_logs_after_filtering[i] for i in leaf_ids]
    final_log_pool_full = [short_to_full[text] for text in final_log_pool_short]
    final_log_pool_labels = [labels[i] for i in leaf_ids]


    return {
        **base_result,
        "resolved_depth": resolved_depth,
        "final_log_pool_short": final_log_pool_short,
        "final_log_pool_full": final_log_pool_full,
        "final_log_pool_labels": final_log_pool_labels,
        "error": None,
    }


def select_final_dialogue_channel_pool(pipeline_state, target_number_of_pairs=2, seed=42):
    """
    
    """

    # Get event logs
    unique_logs = pipeline_state["unique_logs"]
    short_to_full = pipeline_state["short_to_full"]

    # Get dialogue logs
    d_unique_logs = pipeline_state["d_unique_logs"]
    d_short_to_full = pipeline_state["d_short_to_full"]

    # Get distance matrix 
    distance_matrix = pipeline_state["distance_matrix"]    

    import numpy as np

    # Clamp target_count to the number of available pairs
    target_number_of_pairs = max(1, min(target_number_of_pairs, distance_matrix.size))

    # Flatten the matrix and get the indices of the X lowest NCD scores
    flat_indices = np.argsort(distance_matrix, axis=None)[:target_number_of_pairs]

    # Convert flattened indices back to (event_index, dialogue_index)
    event_indices, dialogue_indices = np.unravel_index(
        flat_indices, distance_matrix.shape
    )

    # Retrieve the corresponding logs and NCD scores
    selected_pairs = [
        {
            "event_index": int(i),
            "dialogue_index": int(j),
            "event_log_short": unique_logs[i],
            "event_log_full": short_to_full[unique_logs[i]],
            "dialogue_log_short": d_unique_logs[j],
            "dialogue_log_full": d_short_to_full[d_unique_logs[j]],
            "ncd": float(distance_matrix[i, j]),
        }
        for i, j in zip(event_indices, dialogue_indices)
    ]


    return {
        "selected_pairs": selected_pairs
    }