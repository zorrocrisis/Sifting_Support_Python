"""
tree_utils.py
-------------
Pure structural utilities for working with scipy ClusterNode trees:
computing depths, subtree frequencies, walking to a specific leaf, and
the "zoom" logic that lets the NCD threshold slider crop the tree
without ever re-running linkage().
"""

import random

import numpy as np
from scipy.cluster.hierarchy import ClusterNode


# -----------------------------------------------------------------------
# Basic tree metadata
# -----------------------------------------------------------------------
def assign_depths(node, depth=0, depth_map=None):
    """Return {node.id: depth from root} for every node in the tree."""
    if depth_map is None:
        depth_map = {}

    depth_map[node.id] = depth

    if not node.is_leaf():
        assign_depths(node.left, depth + 1, depth_map)
        assign_depths(node.right, depth + 1, depth_map)

    return depth_map


def get_leaves(node):
    """Return leaf ids under `node`, in left-to-right order."""
    if node.is_leaf():
        return [node.id]
    return get_leaves(node.left) + get_leaves(node.right)


def compute_subtree_frequencies(node, log_lines, counts, freq_map=None):
    """
    freq_map[node.id] = total occurrence count of every log under this
    subtree, i.e. sum of `counts[log]` for each leaf log in the subtree.

    `log_lines` must be indexable by leaf id (log_lines[leaf.id] gives
    the log text for that leaf), and `counts` must be keyed by that text.
    """
    if freq_map is None:
        freq_map = {}

    if node.is_leaf():
        freq_map[node.id] = counts[log_lines[node.id]]
    else:
        compute_subtree_frequencies(node.left, log_lines, counts, freq_map)
        compute_subtree_frequencies(node.right, log_lines, counts, freq_map)
        freq_map[node.id] = freq_map[node.left.id] + freq_map[node.right.id]

    return freq_map


def path_to_leaf(root, target_leaf_id):
    """
    Return the list of (parent_id, child_id) edges from `root` down to
    the leaf with id `target_leaf_id`, in root-to-leaf order.
    """
    path = []

    def dfs(node):
        if node.is_leaf():
            return node.id == target_leaf_id

        if dfs(node.left):
            path.append((node.id, node.left.id))
            return True

        if dfs(node.right):
            path.append((node.id, node.right.id))
            return True

        return False

    dfs(root)
    path.reverse()
    return path


# -----------------------------------------------------------------------
# Depth-based selection (frontier + early leaves)
# -----------------------------------------------------------------------
def collect_nodes_at_depth(node, depth_map, target_depth, nodes=None):
    """Collect every node whose depth exactly equals `target_depth`."""
    if nodes is None:
        nodes = []

    if depth_map[node.id] == target_depth:
        nodes.append(node)
        return nodes

    if not node.is_leaf():
        collect_nodes_at_depth(node.left, depth_map, target_depth, nodes)
        collect_nodes_at_depth(node.right, depth_map, target_depth, nodes)

    return nodes


def collect_early_leaves(node, depth_map, target_depth, leaves=None):
    """Collect leaf ids that occur strictly before `target_depth`."""
    if leaves is None:
        leaves = []

    node_depth = depth_map[node.id]

    if node.is_leaf() and node_depth < target_depth:
        leaves.append(node.id)
        return leaves

    if not node.is_leaf():
        collect_early_leaves(node.left, depth_map, target_depth, leaves)
        collect_early_leaves(node.right, depth_map, target_depth, leaves)

    return leaves


def collect_frontier_with_early_leaves(node, depth_map, target_depth, frontier=None, early_leaves=None):
    """
    Split the tree at `target_depth`:
      - `frontier`: subtree roots sitting exactly at target_depth
      - `early_leaves`: leaf nodes that terminated before reaching it

    Note: because recursion stops as soon as a node's depth ==
    target_depth (it's added to `frontier` and not descended into), a
    node's own depth can never exceed target_depth by the time this
    function looks at it -- so every leaf is guaranteed to land in
    exactly one of the two buckets.
    """
    if frontier is None:
        frontier = []
    if early_leaves is None:
        early_leaves = []

    node_depth = depth_map[node.id]

    if node.is_leaf() and node_depth <= target_depth:
        early_leaves.append(node)
        return frontier, early_leaves

    if node_depth == target_depth:
        frontier.append(node)
        return frontier, early_leaves

    if not node.is_leaf():
        collect_frontier_with_early_leaves(node.left, depth_map, target_depth, frontier, early_leaves)
        collect_frontier_with_early_leaves(node.right, depth_map, target_depth, frontier, early_leaves)

    return frontier, early_leaves


# -----------------------------------------------------------------------
# NCD-threshold "zoom" (replaces re-clustering a filtered subset)
# -----------------------------------------------------------------------
def representative_leaf(node, distance_matrix, seed=42):
    """
    Return a representative original leaf for `node`.

    The representative is the medoid of all leaves in the subtree:
        argmin_x sum_y d(x, y)

    If multiple leaves have the same minimum total distance, one of
    the tied leaves is chosen randomly.

    Parameters
    ----------
    node : ClusterNode
        Root of the subtree.
    distance_matrix : np.ndarray
        Full original NCD distance matrix. Leaf IDs must correspond
        to its indices.
    seed : int, optional
        Random seed for tie-breaking. If None, uses NumPy's default RNG.

    Returns
    -------
    int
        Original leaf ID of the representative.
    """

    rng = random.Random(seed)

    leaves = get_leaves(node)

    if len(leaves) == 1:
        return leaves[0]

    sub_matrix = distance_matrix[np.ix_(leaves, leaves)]
    total_distances = sub_matrix.sum(axis=1)

    min_distance = total_distances.min()

    # Use isclose so floating-point equality doesn't cause
    # theoretically tied medoids to be treated differently.
    tied = np.flatnonzero(
        np.isclose(total_distances, min_distance)
    )

    chosen_idx = rng.choice(tied)

    return leaves[chosen_idx]


def collapse_tree_at_threshold(root, threshold, distance_matrix=None, seed=42):
    """
    Build a new tree where every subtree whose merge height is below
    `threshold` is collapsed into a single leaf. Nodes above the
    threshold keep their real, original merge heights -- nothing is
    re-clustered or re-linked, so this is a genuine "zoom" into the
    original dendrogram rather than a fresh clustering on a subset.

    Parameters
    ----------
    distance_matrix : np.ndarray or None
        Square (n x n) NCD distance matrix over the ORIGINAL leaves
        (same indexing as leaf ids in `root`). When provided, each
        collapsed cluster's representative is its MEDOID (see
        representative_leaf) -- the original leaf minimizing total
        distance to every other leaf in that same cluster, i.e. the
        most centrally-located / "most representative" event, using
        real NCD distances rather than tree structure alone. When
        None (the default, kept for backward compatibility with any
        caller that doesn't have a distance matrix handy), falls back
        to the old leftmost-leaf behavior -- arbitrary, but still
        deterministic.
    seed : int
        Passed through to representative_leaf() for tie-breaking when
        a cluster has more than one leaf tied for minimum total
        distance (e.g. a 2-leaf cherry, where both leaves are
        necessarily "equally central" to each other).

    Returns
    -------
    collapsed_root : ClusterNode
    leaf_original_ids : list[int]
        leaf_original_ids[i] = the id of the representative leaf in the
        ORIGINAL tree for new leaf `i`. New leaves are numbered 0..k-1
        in left-to-right (DFS) order, matching what labels/x_map expect.
    """
    leaf_original_ids = []

    def leftmost_original_leaf(node):
        # Fallback only, used when no distance_matrix is available.
        # Arbitrary (always .left) -- not based on content or centrality.
        while not node.is_leaf():
            node = node.left
        return node.id

    def pick_representative(node):
        if distance_matrix is not None:
            return representative_leaf(node, distance_matrix, seed=seed)
        return leftmost_original_leaf(node)

    def build(node):
        if node.is_leaf() or node.dist < threshold:
            new_id = len(leaf_original_ids)
            leaf_original_ids.append(pick_representative(node))
            return ClusterNode(id=new_id, count=node.count)

        left = build(node.left)
        right = build(node.right)
        # id=0 is a placeholder -- ClusterNode requires a non-negative id
        # at construction time; the real id is assigned in the second
        # pass below, once we know how many leaves there are.
        return ClusterNode(id=0, left=left, right=right,
                            dist=node.dist, count=node.count)

    collapsed_root = build(root)

    # Second pass: number internal nodes n_leaves..2*n_leaves-2,
    # matching scipy's usual convention, now that leaves are numbered.
    n_leaves = len(leaf_original_ids)
    next_internal_id = [n_leaves]

    def assign_internal_ids(node):
        if node.is_leaf():
            return
        assign_internal_ids(node.left)
        assign_internal_ids(node.right)
        node.id = next_internal_id[0]
        next_internal_id[0] += 1

    assign_internal_ids(collapsed_root)

    return collapsed_root, leaf_original_ids


def build_zoomed_view(root_0, unique_logs, counts, distance_matrix, threshold, log_dict=None, seed=42):
    """
    Produce everything the dashboard needs to render the dendrogram
    "zoomed" to `threshold`, without ever re-running linkage() on a subset.

    Parameters
    ----------
    root_0 : ClusterNode
        The ONE canonical tree, built once from all unique_logs.
    distance_matrix : np.ndarray, shape (n, n)
        Square NCD matrix over `unique_logs` (i.e. squareform of the
        condensed distances used to build root_0). Used for two things:
        scoring "most anomalous" among the surviving representatives,
        and -- via collapse_tree_at_threshold -- picking each collapsed
        cluster's MEDOID as its representative, instead of an arbitrary
        leftmost leaf.
    seed : int
        Tie-breaking seed, passed through to collapse_tree_at_threshold
        / representative_leaf for clusters where more than one leaf is
        equally central (e.g. any 2-leaf cherry).

    Returns
    -------
    dict with keys: root, depth_map, freq_map, labels,
    unique_logs_after_filtering, most_anomalous_log, highest_NCD.
    """
    collapsed_root, leaf_original_ids = collapse_tree_at_threshold(
        root_0, threshold, distance_matrix=distance_matrix, seed=seed
    )

    depth_map = assign_depths(collapsed_root)

    collapsed_logs = [unique_logs[i] for i in leaf_original_ids]

    freq_map = compute_subtree_frequencies(collapsed_root, collapsed_logs, counts)

    if log_dict is None:
        labels = [
            f"{collapsed_logs[i]} (x{counts[collapsed_logs[i]]})"
            for i in range(len(collapsed_logs))
        ]
    else:
        labels = [f"{line} (x{counts[line]})" for line in collapsed_logs]

    if len(leaf_original_ids) > 1:
        sub_matrix = distance_matrix[np.ix_(leaf_original_ids, leaf_original_ids)]
        mean_dist = sub_matrix.mean(axis=1)
        most_anomalous_idx = int(np.argmax(mean_dist))
        most_anomalous_log = collapsed_logs[most_anomalous_idx]
        highest_NCD = mean_dist[most_anomalous_idx]
    else:
        most_anomalous_log = collapsed_logs[0] if collapsed_logs else None
        highest_NCD = 0.0

    return {
        "root": collapsed_root,
        "depth_map": depth_map,
        "freq_map": freq_map,
        "labels": labels,
        "unique_logs_after_filtering": collapsed_logs,
        "most_anomalous_log": most_anomalous_log,
        "highest_NCD": highest_NCD,
    }