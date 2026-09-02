"""
test_dendrogram_plot.py
-------------------------
Regression tests for dendrogram_plot.py -- coordinate assignment,
drawing, cluster coloring, and the top-level figure builder.

Uses the SAME hand-built 6-leaf tree as test_tree_utils.py, so its
depths/structure are already worked out by hand there. This file does
NOT import tree_utils, though -- depth_map is passed in as a literal
dict here, matching how dendrogram_plot.py itself has zero dependency
on tree_utils (the caller, dashboard.py, is the one that glues the two
together). Keeping this file decoupled means a bug in tree_utils can't
accidentally mask or fake a passing dendrogram_plot test.

Fixture tree (6 leaves: 0=A, 1=B, 2=C, 3=D, 4=E, 5=F):

              root (id 10, dist 0.8)
             /                      \\
      node8 (id 8, dist 0.5)     node9 (id 9, dist 0.2)
        /            \\               /          \\
  node6 (id 6,     node7 (id 7,   leaf E (4)   leaf F (5)
   dist 0.1)        dist 0.1)
    /     \\           /     \\
 leaf A(0) leaf B(1) leaf C(2) leaf D(3)

Hand-worked x positions (leaves get 0..5 left-to-right, internal nodes
get the midpoint of their children):
  x[0..5] = 0,1,2,3,4,5 (A,B,C,D,E,F)
  x[6] (node6=A,B)   = 0.5
  x[7] (node7=C,D)   = 2.5
  x[8] (node8=A-D)   = 1.5
  x[9] (node9=E,F)   = 4.5
  x[10] (root)       = 3.0

y positions: leaves = 0; internal = that node's own .dist
  y[0..5] = 0
  y[6]=0.1  y[7]=0.1  y[8]=0.5  y[9]=0.2  y[10]=0.8

Run with: pytest test_dendrogram_plot.py -v
"""

import sys

import numpy as np
import plotly.graph_objects as go
import pytest
from scipy.cluster.hierarchy import to_tree

import dendrogram_plot


# -----------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------
@pytest.fixture
def root_0():
    Z = np.array([
        [0, 1, 0.1, 2],   # row0 -> new node id 6:  A,B
        [2, 3, 0.1, 2],   # row1 -> new node id 7:  C,D
        [6, 7, 0.5, 4],   # row2 -> new node id 8:  A,B,C,D
        [4, 5, 0.2, 2],   # row3 -> new node id 9:  E,F
        [8, 9, 0.8, 6],   # row4 -> new node id 10: root, everything
    ])
    return to_tree(Z)


@pytest.fixture
def depth_map():
    """Hand-worked in test_tree_utils.py; duplicated here as a literal
    dict rather than imported, to keep this file decoupled from tree_utils."""
    return {0: 3, 1: 3, 2: 3, 3: 3, 4: 2, 5: 2, 6: 2, 7: 2, 8: 1, 9: 1, 10: 0}


@pytest.fixture
def labels():
    return ["A (x1)", "B (x1)", "C (x1)", "D (x1)", "E (x1)", "F (x1)"]


# -----------------------------------------------------------------------
# assign_x
# -----------------------------------------------------------------------
class TestAssignX:
    def test_leaves_get_sequential_positions_left_to_right(self, root_0):
        x_map = dendrogram_plot.assign_x(root_0, {})
        assert [x_map[i] for i in range(6)] == [0, 1, 2, 3, 4, 5]

    def test_internal_nodes_get_midpoint_of_children(self, root_0):
        x_map = dendrogram_plot.assign_x(root_0, {})
        assert x_map[6] == 0.5   # node6 = mid(A=0, B=1)
        assert x_map[7] == 2.5   # node7 = mid(C=2, D=3)
        assert x_map[8] == 1.5   # node8 = mid(node6=0.5, node7=2.5)
        assert x_map[9] == 4.5   # node9 = mid(E=4, F=5)
        assert x_map[10] == 3.0  # root  = mid(node8=1.5, node9=4.5)

    def test_mutable_default_argument_does_not_leak_across_calls(self, root_0):
        """
        REGRESSION TEST for a real, already-shipped-and-fixed bug:
        `next_x` used to default to a shared mutable list ([0]), so
        calling assign_x() a second time silently continued counting
        from wherever the previous call left off, instead of starting
        over at x=0. This corrupted every dendrogram redraw after the
        first. Calling assign_x() on a SMALLER tree right after a
        bigger one is the sharpest way to catch state leaking: leaked
        state means the small tree's leaves would NOT start back at 0.
        """
        dendrogram_plot.assign_x(root_0, {})  # first call: 6 leaves, x reaches 5

        # A tiny 2-leaf tree, called with a fresh empty x_map (as every
        # real call site does -- see draw the pattern in
        # create_dendrogram_new: assign_x(root, {})).
        small_Z = np.array([[0, 1, 0.3, 2]])
        small_root = to_tree(small_Z)
        x_map_small = dendrogram_plot.assign_x(small_root, {})

        assert x_map_small[0] == 0, "leaked state: should start back at x=0, not continue from the previous call"
        assert x_map_small[1] == 1

    def test_repeated_calls_on_same_tree_give_identical_results(self, root_0):
        """Calling assign_x() twice on the SAME tree (as a redraw would)
        must produce the same coordinates both times, not drift."""
        x_map_1 = dendrogram_plot.assign_x(root_0, {})
        x_map_2 = dendrogram_plot.assign_x(root_0, {})
        assert x_map_1 == x_map_2


# -----------------------------------------------------------------------
# assign_y
# -----------------------------------------------------------------------
class TestAssignY:
    def test_leaves_sit_at_zero(self, root_0):
        y_map = dendrogram_plot.assign_y(root_0, {})
        assert [y_map[i] for i in range(6)] == [0, 0, 0, 0, 0, 0]

    def test_internal_nodes_sit_at_their_own_merge_distance(self, root_0):
        y_map = dendrogram_plot.assign_y(root_0, {})
        assert y_map[6] == 0.1
        assert y_map[7] == 0.1
        assert y_map[8] == 0.5
        assert y_map[9] == 0.2
        assert y_map[10] == 0.8


# -----------------------------------------------------------------------
# draw_edge
# -----------------------------------------------------------------------
class TestDrawEdge:
    def test_adds_two_traces_and_records_them_in_edge_map(self, root_0):
        x_map = dendrogram_plot.assign_x(root_0, {})
        y_map = dendrogram_plot.assign_y(root_0, {})
        fig = go.Figure()
        edge_map = {}

        node9 = root_0.right  # E,F subtree (dist 0.2)
        leaf_e = node9.left   # id 4

        dendrogram_plot.draw_edge(node9, leaf_e, fig, x_map, y_map, edge_map, color="blue", width=3)

        assert len(fig.data) == 2
        assert (9, 4, "vertical") in edge_map
        assert (9, 4, "horizontal") in edge_map

    def test_vertical_segment_spans_child_y_to_parent_y_at_child_x(self, root_0):
        x_map = dendrogram_plot.assign_x(root_0, {})
        y_map = dendrogram_plot.assign_y(root_0, {})
        fig = go.Figure()
        edge_map = {}

        node9 = root_0.right
        leaf_e = node9.left  # x=4, y=0

        dendrogram_plot.draw_edge(node9, leaf_e, fig, x_map, y_map, edge_map)

        vertical = fig.data[edge_map[(9, 4, "vertical")]]
        assert list(vertical.x) == [4, 4]           # stays at child's x
        assert list(vertical.y) == [0, 0.2]          # from child y (0) to parent y (0.2)

    def test_horizontal_segment_spans_parent_x_to_child_x_at_parent_y(self, root_0):
        x_map = dendrogram_plot.assign_x(root_0, {})
        y_map = dendrogram_plot.assign_y(root_0, {})
        fig = go.Figure()
        edge_map = {}

        node9 = root_0.right  # x=4.5, y=0.2
        leaf_e = node9.left   # x=4

        dendrogram_plot.draw_edge(node9, leaf_e, fig, x_map, y_map, edge_map)

        horizontal = fig.data[edge_map[(9, 4, "horizontal")]]
        assert list(horizontal.x) == [4.5, 4]
        assert list(horizontal.y) == [0.2, 0.2]       # constant at parent's y

    def test_color_and_width_are_applied_to_both_segments(self, root_0):
        x_map = dendrogram_plot.assign_x(root_0, {})
        y_map = dendrogram_plot.assign_y(root_0, {})
        fig = go.Figure()
        edge_map = {}

        node9 = root_0.right
        leaf_e = node9.left

        dendrogram_plot.draw_edge(node9, leaf_e, fig, x_map, y_map, edge_map, color="red", width=5)

        for part in ("vertical", "horizontal"):
            trace = fig.data[edge_map[(9, 4, part)]]
            assert trace.line.color == "red"
            assert trace.line.width == 5


# -----------------------------------------------------------------------
# draw_tree
# -----------------------------------------------------------------------
class TestDrawTree:
    def test_draws_two_traces_per_edge_for_every_internal_node(self, root_0):
        """
        5 internal nodes (root, node8, node9, node6, node7), each
        drawing an edge to its left AND right child = 10 draw_edge
        calls = 20 traces total (2 per call).
        """
        x_map = dendrogram_plot.assign_x(root_0, {})
        y_map = dendrogram_plot.assign_y(root_0, {})
        fig = go.Figure()
        edge_map = {}
        color_map = {i: "black" for i in range(11)}

        dendrogram_plot.draw_tree(root_0, fig, x_map, y_map, edge_map, color_map)

        assert len(fig.data) == 20
        assert len(edge_map) == 20

    def test_every_parent_child_pair_in_the_tree_is_present(self, root_0):
        x_map = dendrogram_plot.assign_x(root_0, {})
        y_map = dendrogram_plot.assign_y(root_0, {})
        fig = go.Figure()
        edge_map = {}
        color_map = {i: "black" for i in range(11)}

        dendrogram_plot.draw_tree(root_0, fig, x_map, y_map, edge_map, color_map)

        expected_pairs = {
            (10, 8), (10, 9),  # root -> node8, node9
            (8, 6), (8, 7),    # node8 -> node6, node7
            (9, 4), (9, 5),    # node9 -> E, F
            (6, 0), (6, 1),    # node6 -> A, B
            (7, 2), (7, 3),    # node7 -> C, D
        }
        actual_pairs = {(parent, child) for (parent, child, part) in edge_map.keys()}
        assert actual_pairs == expected_pairs

    def test_both_children_of_a_node_share_that_nodes_color(self, root_0):
        """draw_tree colors an edge using the PARENT's color_map entry,
        so both children of the same parent should share one color."""
        x_map = dendrogram_plot.assign_x(root_0, {})
        y_map = dendrogram_plot.assign_y(root_0, {})
        fig = go.Figure()
        edge_map = {}
        color_map = {10: "navy", 8: "green", 9: "orange", 6: "black", 7: "black"}

        dendrogram_plot.draw_tree(root_0, fig, x_map, y_map, edge_map, color_map)

        # root's two edges (to node8 and node9) should both be "navy".
        assert fig.data[edge_map[(10, 8, "vertical")]].line.color == "navy"
        assert fig.data[edge_map[(10, 9, "vertical")]].line.color == "navy"
        # node8's two edges (to node6 and node7) should both be "green".
        assert fig.data[edge_map[(8, 6, "vertical")]].line.color == "green"
        assert fig.data[edge_map[(8, 7, "vertical")]].line.color == "green"


# -----------------------------------------------------------------------
# draw_labels
# -----------------------------------------------------------------------
class TestDrawLabels:
    def test_one_text_point_per_label_at_correct_x_position(self, root_0, labels):
        x_map = dendrogram_plot.assign_x(root_0, {})
        fig = go.Figure()

        dendrogram_plot.draw_labels(fig, x_map, labels)

        assert len(fig.data) == 1
        trace = fig.data[0]
        assert list(trace.x) == [0, 1, 2, 3, 4, 5]
        assert list(trace.text) == labels
        assert trace.mode == "text"

    def test_all_labels_sit_at_the_same_y_below_the_axis(self, root_0, labels):
        x_map = dendrogram_plot.assign_x(root_0, {})
        fig = go.Figure()
        dendrogram_plot.draw_labels(fig, x_map, labels)
        assert all(y == -0.02 for y in fig.data[0].y)


# -----------------------------------------------------------------------
# draw_depth_annotations
# -----------------------------------------------------------------------
class TestDrawDepthAnnotations:
    def test_one_marker_per_internal_node_only(self, root_0, depth_map):
        x_map = dendrogram_plot.assign_x(root_0, {})
        y_map = dendrogram_plot.assign_y(root_0, {})
        fig = go.Figure()

        dendrogram_plot.draw_depth_annotations(fig, root_0, x_map, y_map, depth_map)

        assert len(fig.data) == 1
        trace = fig.data[0]
        assert len(trace.x) == 5  # 5 internal nodes, leaves excluded

    def test_labels_show_the_correct_depth_for_each_node(self, root_0, depth_map):
        x_map = dendrogram_plot.assign_x(root_0, {})
        y_map = dendrogram_plot.assign_y(root_0, {})
        fig = go.Figure()

        dendrogram_plot.draw_depth_annotations(fig, root_0, x_map, y_map, depth_map)

        trace = fig.data[0]
        shown = dict(zip(zip(trace.x, trace.y), trace.text))
        # root sits at (x=3.0, y=0.8), depth 0.
        assert shown[(3.0, 0.8)] == "0"
        # node9 sits at (x=4.5, y=0.2), depth 1.
        assert shown[(4.5, 0.2)] == "1"


# -----------------------------------------------------------------------
# assign_cluster_colors
# -----------------------------------------------------------------------
class TestAssignClusterColors:
    def test_default_threshold_paints_two_subtrees_and_leaves_root_alone(self, root_0):
        """
        Default color_threshold = 0.7 * root.dist = 0.7*0.8 = 0.56.
        node8 (0.5) and node9 (0.2) both fall below it, and neither's
        parent (root, 0.8) is below threshold -- so each becomes its
        own painted subtree, root stays DEFAULT_COLOR.
        """
        color_map = dendrogram_plot.assign_cluster_colors(root_0)

        assert color_map[10] == dendrogram_plot.DEFAULT_COLOR  # root, unpainted

        node8_color = color_map[8]
        node9_color = color_map[9]
        assert node8_color != node9_color
        assert node8_color != dendrogram_plot.DEFAULT_COLOR
        assert node9_color != dendrogram_plot.DEFAULT_COLOR

        # Every descendant of node8 shares node8's color.
        for node_id in (8, 6, 7, 0, 1, 2, 3):
            assert color_map[node_id] == node8_color
        # Every descendant of node9 shares node9's color.
        for node_id in (9, 4, 5):
            assert color_map[node_id] == node9_color

    def test_first_and_second_clusters_get_the_first_two_scipy_colors_in_order(self, root_0):
        """node8 is encountered before node9 (root.left before root.right),
        so it should get SCIPY_COLORS[0] and node9 should get SCIPY_COLORS[1]."""
        color_map = dendrogram_plot.assign_cluster_colors(root_0)
        assert color_map[8] == dendrogram_plot.SCIPY_COLORS[0]
        assert color_map[9] == dendrogram_plot.SCIPY_COLORS[1]

    def test_every_node_in_the_tree_gets_a_color(self, root_0):
        color_map = dendrogram_plot.assign_cluster_colors(root_0)
        assert set(color_map.keys()) == set(range(11))

    def test_very_high_threshold_paints_everything_one_color(self, root_0):
        """threshold above the root's own dist means even the root
        counts as 'below threshold', so the whole tree paints as one
        single subtree."""
        color_map = dendrogram_plot.assign_cluster_colors(root_0, color_threshold=1.0)
        assert len(set(color_map.values())) == 1

    def test_zero_threshold_leaves_everything_default_colored(self, root_0):
        """No node's dist can be below a threshold of 0 (all dists > 0
        in this tree), so nothing ever gets painted -- every node falls
        back to DEFAULT_COLOR individually."""
        color_map = dendrogram_plot.assign_cluster_colors(root_0, color_threshold=0.0)
        assert set(color_map.values()) == {dendrogram_plot.DEFAULT_COLOR}


# -----------------------------------------------------------------------
# create_dendrogram_new (top-level integration)
# -----------------------------------------------------------------------
class TestCreateDendrogramNew:
    def test_axis_titles_are_set(self, root_0, labels, depth_map):
        fig = dendrogram_plot.create_dendrogram_new(root_0, labels, depth_map)
        assert fig.layout.xaxis.title.text == "Log Entry (with frequency)"
        assert fig.layout.yaxis.title.text == "NCD Distance"

    def test_y_axis_range_starts_at_y_min_and_pads_above_max(self, root_0, labels, depth_map):
        fig = dendrogram_plot.create_dendrogram_new(root_0, labels, depth_map, y_min=0.1)
        # max_y = 0.8 (root's dist); top = 0.8 * 1.05
        assert fig.layout.yaxis.range == (0.1, pytest.approx(0.8 * 1.05))

    def test_y_axis_top_falls_back_when_y_min_exceeds_max_y(self, root_0, labels, depth_map):
        """If y_min is somehow above max_y (e.g. an all-collapsed single-leaf
        tree), the top must still end up above y_min, not below/equal to it."""
        fig = dendrogram_plot.create_dendrogram_new(root_0, labels, depth_map, y_min=10.0)
        low, high = fig.layout.yaxis.range
        assert low == 10.0
        assert high > low

    def test_x_axis_ticks_match_labels_in_order(self, root_0, labels, depth_map):
        fig = dendrogram_plot.create_dendrogram_new(root_0, labels, depth_map)
        assert list(fig.layout.xaxis.ticktext) == labels
        assert list(fig.layout.xaxis.tickvals) == [0, 1, 2, 3, 4, 5]

    def test_show_depth_labels_toggle_adds_or_omits_one_trace(self, root_0, labels, depth_map):
        fig_with = dendrogram_plot.create_dendrogram_new(root_0, labels, depth_map, show_depth_labels=True)
        fig_without = dendrogram_plot.create_dendrogram_new(root_0, labels, depth_map, show_depth_labels=False)
        assert len(fig_with.data) == len(fig_without.data) + 1

    def test_highlighted_edges_turn_red_and_others_do_not(self, root_0, labels, depth_map):
        """
        Default color_threshold paints node8/node9's subtrees, but
        root's own two edges (to node8 and to node9) stay
        DEFAULT_COLOR -- highlighting (10, 8) only should turn exactly
        that edge red and leave (10, 9) at DEFAULT_COLOR.
        """
        fig = dendrogram_plot.create_dendrogram_new(
            root_0, labels, depth_map, highlighted_edges=[(10, 8)]
        )

        edge_map = {}
        # Rebuild edge_map the same way create_dendrogram_new does internally,
        # to find the right trace indices -- order matches draw_tree's DFS.
        x_map = dendrogram_plot.assign_x(root_0, {})
        y_map = dendrogram_plot.assign_y(root_0, {})
        color_map = dendrogram_plot.assign_cluster_colors(root_0)
        probe_fig = go.Figure()
        dendrogram_plot.draw_tree(root_0, probe_fig, x_map, y_map, edge_map, color_map)

        highlighted_idx = edge_map[(10, 8, "vertical")]
        untouched_idx = edge_map[(10, 9, "vertical")]

        assert fig.data[highlighted_idx].line.color == "red"
        assert fig.data[highlighted_idx].line.width == 5
        assert fig.data[untouched_idx].line.color == dendrogram_plot.DEFAULT_COLOR

    def test_no_highlighted_edges_leaves_all_colors_as_cluster_colors(self, root_0, labels, depth_map):
        fig = dendrogram_plot.create_dendrogram_new(root_0, labels, depth_map, highlighted_edges=None)
        assert not any(trace.line.color == "red" for trace in fig.data if hasattr(trace, "line"))

    def test_figure_dimensions_scale_with_label_count(self, root_0, labels, depth_map):
        fig = dendrogram_plot.create_dendrogram_new(root_0, labels, depth_map)
        # n=6 labels -> fig_width = max(750, min(1000, 50*6=300)) = 750
        assert fig.layout.width == 750
        assert fig.layout.height == 1560


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))