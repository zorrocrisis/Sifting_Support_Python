"""
traversal_strategies.py
------------------------
Given a tree (already built/zoomed by tree_utils), these functions pick
a representative "final log pool" -- either by random descent or by
always favoring the least-frequent branch -- starting from a target
depth. Used to drive the "Random" / "Least Frequent" strategy selector
in the dashboard.
"""

import random

from tree_utils import collect_nodes_at_depth, collect_early_leaves, collect_frontier_with_early_leaves


# -----------------------------------------------------------------------
# Random strategy
# -----------------------------------------------------------------------
def random_descent_to_leaf(node, rng):
    """Randomly walk left/right from `node` until hitting a leaf."""
    path = []
    current = node

    while not current.is_leaf():
        nxt = current.left if rng.random() < 0.5 else current.right
        path.append((current.id, nxt.id))
        current = nxt

    return current.id, path


def random_leaves_after_depth(root, depth_map, target_depth, seed=42):
    """
    For every subtree rooted at target_depth, descend randomly to a leaf.
    Leaves occurring before target_depth are preserved as-is.
    """
    rng = random.Random(seed)

    frontier_nodes = collect_nodes_at_depth(root, depth_map, target_depth)

    leaf_ids = []
    traversed_edges = set()

    for node in frontier_nodes:
        leaf, path = random_descent_to_leaf(node, rng)
        leaf_ids.append(leaf)
        traversed_edges.update(path)

    return leaf_ids, traversed_edges


# -----------------------------------------------------------------------
# "Least Frequent" strategy
# -----------------------------------------------------------------------
def frequency_descent_to_leaf(node, freq_map, rng):
    """Walk toward the least-frequent child at each split (ties broken randomly)."""
    path = []
    current = node

    while not current.is_leaf():
        left, right = current.left, current.right
        left_freq, right_freq = freq_map[left.id], freq_map[right.id]

        if left_freq < right_freq:
            nxt = left
        elif right_freq < left_freq:
            nxt = right
        else:
            nxt = rng.choice([left, right])

        path.append((current.id, nxt.id))
        current = nxt

    return current.id, path


def rare_logs_after_depth(root, depth_map, freq_map, target_depth, seed=42):
    """
    For every subtree rooted at target_depth, descend by always choosing
    the least frequent subtree. Leaves occurring before target_depth
    are preserved.
    """
    rng = random.Random(seed)

    frontier_nodes = collect_nodes_at_depth(root, depth_map, target_depth)
    early_leaf_ids = collect_early_leaves(root, depth_map, target_depth)

    selected_leaf_ids = []
    path = []
    for node in frontier_nodes:
        leaf_id, edge_path = frequency_descent_to_leaf(node, freq_map, rng)
        selected_leaf_ids.append(leaf_id)
        path.extend(edge_path)

    return list(set(selected_leaf_ids + early_leaf_ids)), set(path)


# -----------------------------------------------------------------------
# "Target Log Count" -> depth resolution
# -----------------------------------------------------------------------
def compute_depth_from_target_count(root, depth_map, target_count):
    """
    Compute the depth at which the number of selected logs (frontier
    nodes + early leaves) is as close as possible to `target_count`,
    without going under it.
    """
    max_depth = max(depth_map.values())

    for depth in range(max_depth + 1):
        frontier_nodes, early_leaf_nodes = collect_frontier_with_early_leaves(root, depth_map, depth)
        selected_logs = len(frontier_nodes) + len(early_leaf_nodes)

        if selected_logs >= target_count:
            return depth

    return max_depth
