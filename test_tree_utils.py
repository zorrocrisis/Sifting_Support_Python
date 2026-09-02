"""
test_tree_utils.py
--------------------
Regression tests for tree_utils.py -- depth/frequency computation, the
frontier/early-leaves split used by traversal strategies, and the NCD
"zoom" logic (collapse_tree_at_threshold / build_zoomed_view).

Design choice: every tree here is HAND-BUILT via a manually-written
scipy linkage matrix, not real NCD distances. This means every
expected answer (which leaf collapses to which, which depth each node
sits at, what each frequency sum should be) is worked out by hand and
asserted exactly -- rather than trusting the algorithm to grade
itself against its own output. This is the same style of test used to
manually verify collapse_tree_at_threshold earlier in this project
(see the "confirm node ids aren't mixed up" investigation); this file
makes that verification permanent instead of a one-off exercise.

Fixture tree (6 leaves: 0=A, 1=B, 2=C, 3=D, 4=E, 5=F):

              root (id 10, dist 0.8)
             /                      \\
      node8 (id 8, dist 0.5)     node9 (id 9, dist 0.2)
        /            \\               /          \\
  node6 (id 6,     node7 (id 7,   leaf E (4)   leaf F (5)
   dist 0.1)        dist 0.1)
    /     \\           /     \\
 leaf A(0) leaf B(1) leaf C(2) leaf D(3)

counts:  A=3, B=1, C=2, D=4, E=5, F=6  (sum = 21)
depths:  root=0, node8/node9=1, node6/node7/E/F=2, A/B/C/D=3

Run with: pytest test_tree_utils.py -v
"""

import sys

import numpy as np
import pytest
from scipy.cluster.hierarchy import to_tree

import tree_utils


# -----------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------
@pytest.fixture
def root_0():
    """The hand-built 6-leaf tree described in the module docstring."""
    Z = np.array([
        [0, 1, 0.1, 2],   # row0 -> new node id 6:  A,B
        [2, 3, 0.1, 2],   # row1 -> new node id 7:  C,D
        [6, 7, 0.5, 4],   # row2 -> new node id 8:  A,B,C,D
        [4, 5, 0.2, 2],   # row3 -> new node id 9:  E,F
        [8, 9, 0.8, 6],   # row4 -> new node id 10: root, everything
    ])
    return to_tree(Z)


@pytest.fixture
def unique_logs():
    return ["A", "B", "C", "D", "E", "F"]


@pytest.fixture
def counts():
    return {"A": 3, "B": 1, "C": 2, "D": 4, "E": 5, "F": 6}


@pytest.fixture
def distance_matrix():
    """
    A hand-written 6x6 NCD-like distance matrix, symmetric with zero
    diagonal, consistent with the tree's own merge structure (small
    within-cherry distances, larger across-cherry). Used only by
    build_zoomed_view's "most anomalous" scoring.
    """
    return np.array([
        [0.0, 0.1, 0.6, 0.6, 0.9, 0.9],
        [0.1, 0.0, 0.6, 0.6, 0.9, 0.9],
        [0.6, 0.6, 0.0, 0.1, 0.9, 0.9],
        [0.6, 0.6, 0.1, 0.0, 0.9, 0.9],
        [0.9, 0.9, 0.9, 0.9, 0.0, 0.2],
        [0.9, 0.9, 0.9, 0.9, 0.2, 0.0],
    ])


# -----------------------------------------------------------------------
# assign_depths
# -----------------------------------------------------------------------
class TestAssignDepths:
    def test_matches_hand_worked_depths(self, root_0):
        depth_map = tree_utils.assign_depths(root_0)
        assert depth_map == {
            0: 3, 1: 3, 2: 3, 3: 3,  # A, B, C, D
            4: 2, 5: 2,              # E, F
            6: 2, 7: 2,              # node6, node7
            8: 1, 9: 1,              # node8, node9
            10: 0,                  # root
        }

    def test_covers_every_node_exactly_once(self, root_0):
        """11 nodes total: 6 leaves + 5 internal merges."""
        depth_map = tree_utils.assign_depths(root_0)
        assert len(depth_map) == 11


# -----------------------------------------------------------------------
# get_leaves
# -----------------------------------------------------------------------
class TestGetLeaves:
    def test_returns_leaves_in_left_to_right_order(self, root_0):
        assert tree_utils.get_leaves(root_0) == [0, 1, 2, 3, 4, 5]

    def test_subtree_returns_only_its_own_leaves(self, root_0):
        node8 = root_0.left  # A,B,C,D subtree
        assert tree_utils.get_leaves(node8) == [0, 1, 2, 3]


# -----------------------------------------------------------------------
# compute_subtree_frequencies
# -----------------------------------------------------------------------
class TestComputeSubtreeFrequencies:
    def test_matches_hand_worked_sums(self, root_0, unique_logs, counts):
        freq_map = tree_utils.compute_subtree_frequencies(root_0, unique_logs, counts)
        assert freq_map[0] == 3   # A
        assert freq_map[1] == 1   # B
        assert freq_map[2] == 2   # C
        assert freq_map[3] == 4   # D
        assert freq_map[4] == 5   # E
        assert freq_map[5] == 6   # F
        assert freq_map[6] == 4   # node6 = A+B = 3+1
        assert freq_map[7] == 6   # node7 = C+D = 2+4
        assert freq_map[9] == 11  # node9 = E+F = 5+6
        assert freq_map[8] == 10  # node8 = node6+node7 = 4+6
        assert freq_map[10] == 21  # root = node8+node9 = 10+11 = sum(counts)

    def test_root_frequency_equals_total_count(self, root_0, unique_logs, counts):
        freq_map = tree_utils.compute_subtree_frequencies(root_0, unique_logs, counts)
        assert freq_map[root_0.id] == sum(counts.values())


# -----------------------------------------------------------------------
# path_to_leaf
# -----------------------------------------------------------------------
class TestPathToLeaf:
    def test_returns_root_to_leaf_edges_in_order(self, root_0):
        # D (leaf id 3): root(10) -> node8(8) -> node7(7) -> leaf(3)
        path = tree_utils.path_to_leaf(root_0, target_leaf_id=3)
        assert path == [(10, 8), (8, 7), (7, 3)]

    def test_different_leaf_gives_different_path(self, root_0):
        # E (leaf id 4): root(10) -> node9(9) -> leaf(4)
        path = tree_utils.path_to_leaf(root_0, target_leaf_id=4)
        assert path == [(10, 9), (9, 4)]

    def test_path_edges_are_consistent_with_depth(self, root_0):
        """Path length to a leaf should equal that leaf's depth."""
        depth_map = tree_utils.assign_depths(root_0)
        for leaf_id in tree_utils.get_leaves(root_0):
            path = tree_utils.path_to_leaf(root_0, leaf_id)
            assert len(path) == depth_map[leaf_id]


# -----------------------------------------------------------------------
# collect_nodes_at_depth
# -----------------------------------------------------------------------
class TestCollectNodesAtDepth:
    def test_depth_2_returns_two_internal_and_two_leaf_nodes(self, root_0):
        depth_map = tree_utils.assign_depths(root_0)
        nodes = tree_utils.collect_nodes_at_depth(root_0, depth_map, target_depth=2)
        assert sorted(n.id for n in nodes) == [4, 5, 6, 7]

    def test_depth_0_returns_only_root(self, root_0):
        depth_map = tree_utils.assign_depths(root_0)
        nodes = tree_utils.collect_nodes_at_depth(root_0, depth_map, target_depth=0)
        assert [n.id for n in nodes] == [root_0.id]

    def test_depth_beyond_tree_returns_empty(self, root_0):
        depth_map = tree_utils.assign_depths(root_0)
        nodes = tree_utils.collect_nodes_at_depth(root_0, depth_map, target_depth=99)
        assert nodes == []


# -----------------------------------------------------------------------
# collect_early_leaves
# -----------------------------------------------------------------------
class TestCollectEarlyLeaves:
    def test_strictly_before_target_depth(self, root_0):
        """E, F sit at depth 2 -- strictly before target_depth=3 (A-D sit AT 3, excluded)."""
        depth_map = tree_utils.assign_depths(root_0)
        leaves = tree_utils.collect_early_leaves(root_0, depth_map, target_depth=3)
        assert sorted(leaves) == [4, 5]

    def test_target_depth_zero_returns_nothing(self, root_0):
        depth_map = tree_utils.assign_depths(root_0)
        assert tree_utils.collect_early_leaves(root_0, depth_map, target_depth=0) == []


# -----------------------------------------------------------------------
# collect_frontier_with_early_leaves
# -----------------------------------------------------------------------
class TestCollectFrontierWithEarlyLeaves:
    def test_middle_depth_splits_internal_vs_leaf_nodes(self, root_0):
        """
        At target_depth=2: node6/node7 (internal, depth 2) go to
        frontier; E/F (LEAVES, also depth 2) go to early_leaves, not
        frontier -- the is_leaf() check has priority even when a leaf
        sits exactly at target_depth. frontier only ever holds subtree
        roots to keep descending from, never leaves.
        """
        depth_map = tree_utils.assign_depths(root_0)
        frontier, early_leaves = tree_utils.collect_frontier_with_early_leaves(root_0, depth_map, target_depth=2)

        assert sorted(n.id for n in frontier) == [6, 7]
        assert sorted(n.id for n in early_leaves) == [4, 5]

    def test_depth_beyond_all_internal_nodes_puts_everything_in_early_leaves(self, root_0):
        """target_depth=3 exceeds every internal node's depth (max 2), so
        frontier is empty and every original leaf ends up in early_leaves."""
        depth_map = tree_utils.assign_depths(root_0)
        frontier, early_leaves = tree_utils.collect_frontier_with_early_leaves(root_0, depth_map, target_depth=3)

        assert frontier == []
        assert sorted(n.id for n in early_leaves) == [0, 1, 2, 3, 4, 5]

    def test_depth_zero_frontier_is_just_the_root(self, root_0):
        depth_map = tree_utils.assign_depths(root_0)
        frontier, early_leaves = tree_utils.collect_frontier_with_early_leaves(root_0, depth_map, target_depth=0)

        assert [n.id for n in frontier] == [root_0.id]
        assert early_leaves == []

    def test_every_original_leaf_is_reachable_from_exactly_one_bucket(self, root_0):
        """
        Exhaustiveness property the function's own docstring claims:
        every leaf ends up covered by early_leaves directly, or by
        being a descendant of exactly one frontier node -- never both,
        never neither. Checked at every possible target_depth.
        """
        depth_map = tree_utils.assign_depths(root_0)
        all_leaves = set(tree_utils.get_leaves(root_0))
        max_depth = max(depth_map.values())

        for target_depth in range(max_depth + 2):  # +1 past the deepest depth too
            frontier, early_leaves = tree_utils.collect_frontier_with_early_leaves(root_0, depth_map, target_depth)

            early_leaf_ids = [n.id for n in early_leaves]
            covered = set(early_leaf_ids)
            for node in frontier:
                covered |= set(tree_utils.get_leaves(node))

            assert covered == all_leaves, f"target_depth={target_depth} did not exactly cover all leaves"
            # And no leaf double-counted between early_leaves and any frontier subtree.
            for node in frontier:
                subtree_leaves = set(tree_utils.get_leaves(node))
                assert not (subtree_leaves & set(early_leaf_ids)), f"target_depth={target_depth} double-counted a leaf"


# -----------------------------------------------------------------------
# collapse_tree_at_threshold
# -----------------------------------------------------------------------
class TestCollapseTreeAtThreshold:
    def test_original_tree_leaves_are_exactly_range_n(self, root_0):
        """Sanity check on the fixture itself: scipy's own leaf numbering
        must match the assumption everything downstream relies on."""
        assert sorted(tree_utils.get_leaves(root_0)) == list(range(6))

    def test_partial_collapse_maps_leaves_to_correct_originals(self, root_0):
        """
        threshold=0.15 collapses both dist-0.1 cherries ((A,B) and
        (C,D)), leaving node9 (dist 0.2) and root (dist 0.8) intact.
        leftmost_original_leaf always walks .left, so (A,B) -> A and
        (C,D) -> C.
        """
        collapsed_root, leaf_original_ids = tree_utils.collapse_tree_at_threshold(root_0, threshold=0.15)
        assert leaf_original_ids == [0, 2, 4, 5]  # A, C, E, F

    def test_partial_collapse_new_leaf_ids_are_contiguous_from_zero(self, root_0):
        collapsed_root, leaf_original_ids = tree_utils.collapse_tree_at_threshold(root_0, threshold=0.15)
        new_leaves = sorted(tree_utils.get_leaves(collapsed_root))
        assert new_leaves == [0, 1, 2, 3]

    def test_partial_collapse_internal_ids_dont_collide_with_leaf_ids(self, root_0):
        collapsed_root, leaf_original_ids = tree_utils.collapse_tree_at_threshold(root_0, threshold=0.15)
        all_ids = {collapsed_root.id, collapsed_root.left.id, collapsed_root.right.id}
        assert all_ids == {4, 5, 6}  # internal ids start right after the 4 leaves

    def test_no_collapse_at_threshold_zero_is_identity_mapping(self, root_0):
        collapsed_root, leaf_original_ids = tree_utils.collapse_tree_at_threshold(root_0, threshold=0.0)
        assert leaf_original_ids == [0, 1, 2, 3, 4, 5]

    def test_total_collapse_at_high_threshold_yields_single_leaf(self, root_0):
        """threshold=0.9 exceeds even the root's own dist (0.8), so the
        whole tree collapses into one leaf: A (leftmost of everything)."""
        collapsed_root, leaf_original_ids = tree_utils.collapse_tree_at_threshold(root_0, threshold=0.9)
        assert leaf_original_ids == [0]
        assert collapsed_root.is_leaf()
        assert collapsed_root.id == 0

    @pytest.mark.parametrize("threshold", [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 0.6, 0.8, 0.9, 1.0])
    def test_depth_map_of_collapsed_tree_has_no_orphans_or_gaps(self, root_0, threshold):
        """
        For every threshold, depth_map's keys must exactly match every
        id actually present in the collapsed tree -- no missing entries
        (which would KeyError downstream) and no stale/extra entries.
        """
        collapsed_root, leaf_original_ids = tree_utils.collapse_tree_at_threshold(root_0, threshold)
        depth_map = tree_utils.assign_depths(collapsed_root)

        def all_ids(node):
            if node.is_leaf():
                return {node.id}
            return {node.id} | all_ids(node.left) | all_ids(node.right)

        assert set(depth_map.keys()) == all_ids(collapsed_root)

    @pytest.mark.parametrize("threshold", [0.0, 0.1, 0.15, 0.2, 0.5, 0.9])
    def test_leaf_original_ids_are_unique_and_in_range(self, root_0, threshold):
        _, leaf_original_ids = tree_utils.collapse_tree_at_threshold(root_0, threshold)
        assert len(leaf_original_ids) == len(set(leaf_original_ids)), "duplicate original leaf id"
        assert all(0 <= i < 6 for i in leaf_original_ids)


# -----------------------------------------------------------------------
# build_zoomed_view (full pipeline)
# -----------------------------------------------------------------------
class TestBuildZoomedView:
    def test_unique_logs_after_filtering_matches_hand_verified_collapse(self, root_0, unique_logs, counts, distance_matrix):
        view_data = tree_utils.build_zoomed_view(root_0, unique_logs, counts, distance_matrix, threshold=0.15)
        assert view_data["unique_logs_after_filtering"] == ["A", "C", "E", "F"]

    def test_freq_map_and_depth_map_share_the_same_id_space(self, root_0, unique_logs, counts, distance_matrix):
        view_data = tree_utils.build_zoomed_view(root_0, unique_logs, counts, distance_matrix, threshold=0.15)
        assert set(view_data["freq_map"].keys()) == set(view_data["depth_map"].keys())

    def test_freq_map_leaf_values_match_counts_for_correct_log(self, root_0, unique_logs, counts, distance_matrix):
        """Guards against a collapsed leaf's frequency being attributed
        to the WRONG log (a real class of bug this project hit once,
        from the log_dict direction swap)."""
        view_data = tree_utils.build_zoomed_view(root_0, unique_logs, counts, distance_matrix, threshold=0.15)
        pool = view_data["unique_logs_after_filtering"]
        for i, log in enumerate(pool):
            assert view_data["freq_map"][i] == counts[log]

    def test_labels_start_with_the_correct_log_text_for_each_leaf(self, root_0, unique_logs, counts, distance_matrix):
        view_data = tree_utils.build_zoomed_view(root_0, unique_logs, counts, distance_matrix, threshold=0.15)
        pool = view_data["unique_logs_after_filtering"]
        for i, log in enumerate(pool):
            assert view_data["labels"][i].startswith(log)

    def test_labels_include_correct_count_suffix(self, root_0, unique_logs, counts, distance_matrix):
        view_data = tree_utils.build_zoomed_view(root_0, unique_logs, counts, distance_matrix, threshold=0.15)
        pool = view_data["unique_logs_after_filtering"]
        for i, log in enumerate(pool):
            assert f"(x{counts[log]})" in view_data["labels"][i]

    def test_most_anomalous_log_is_one_of_the_surviving_logs(self, root_0, unique_logs, counts, distance_matrix):
        view_data = tree_utils.build_zoomed_view(root_0, unique_logs, counts, distance_matrix, threshold=0.15)
        assert view_data["most_anomalous_log"] in view_data["unique_logs_after_filtering"]

    def test_highest_ncd_is_zero_when_only_one_log_survives(self, root_0, unique_logs, counts, distance_matrix):
        """threshold=0.9 collapses everything down to a single log --
        can't compute a mean distance to "everything else" with only
        one entry, so this should degrade to 0.0 rather than crash."""
        view_data = tree_utils.build_zoomed_view(root_0, unique_logs, counts, distance_matrix, threshold=0.9)
        assert len(view_data["unique_logs_after_filtering"]) == 1
        assert view_data["highest_NCD"] == 0.0

    def test_log_dict_argument_does_not_change_which_logs_survive(self, root_0, unique_logs, counts, distance_matrix):
        """
        build_zoomed_view's log_dict parameter doesn't actually get
        indexed into for label text (both branches use the log's own
        text) -- this test locks in that log_dict is a no-op for THIS
        function's output, so nobody "fixes" it into doing a lookup
        that would break once log_dict's key direction changes again.
        """
        without = tree_utils.build_zoomed_view(root_0, unique_logs, counts, distance_matrix, threshold=0.15, log_dict=None)
        with_dict = tree_utils.build_zoomed_view(
            root_0, unique_logs, counts, distance_matrix, threshold=0.15,
            log_dict={"anything": "irrelevant"},
        )
        assert without["unique_logs_after_filtering"] == with_dict["unique_logs_after_filtering"]
        assert without["labels"] == with_dict["labels"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))