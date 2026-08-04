"""
dendrogram_plot.py
-------------------
Renders a scipy ClusterNode tree as a Plotly figure by hand (rather than
using scipy's own dendrogram() + matplotlib), so we can control the
"zoom" y-axis range and highlight arbitrary traversal paths in red.
"""

from itertools import cycle

import plotly.graph_objects as go


# -----------------------------------------------------------------------
# Coordinate assignment
# -----------------------------------------------------------------------
def assign_x(node, x_map, next_x=None):
    """
    Assign each leaf an x position 0, 1, 2, ... in left-to-right order;
    internal nodes get the midpoint of their children.

    NOTE: `next_x` used to default to a mutable list ([0]), which is a
    classic Python bug -- default arguments are evaluated ONCE, so the
    same list object was reused (and kept incrementing) across every
    call to assign_x(). That silently corrupted leaf x-positions after
    the very first render. Using None + lazy init avoids it.
    """
    if next_x is None:
        next_x = [0]

    if node.is_leaf():
        x_map[node.id] = next_x[0]
        next_x[0] += 1
    else:
        assign_x(node.left, x_map, next_x)
        assign_x(node.right, x_map, next_x)
        x_map[node.id] = (x_map[node.left.id] + x_map[node.right.id]) / 2

    return x_map


def assign_y(node, y_map):
    """Leaves sit at y=0; internal nodes sit at their merge distance."""
    if node.is_leaf():
        y_map[node.id] = 0
    else:
        assign_y(node.left, y_map)
        assign_y(node.right, y_map)
        y_map[node.id] = node.dist

    return y_map


# -----------------------------------------------------------------------
# Drawing
# -----------------------------------------------------------------------
def draw_edge(parent, child, fig, x_map, y_map, edge_map, color="black", width=2):
    """
    Draw one branch as an L-shaped pair of line segments (vertical +
    horizontal), and record their trace indices in `edge_map` so they
    can be recolored later (e.g. for highlighting a traversal path).
    """
    x_parent, y_parent = x_map[parent.id], y_map[parent.id]
    x_child, y_child = x_map[child.id], y_map[child.id]

    fig.add_trace(go.Scatter(
        x=[x_child, x_child], y=[y_child, y_parent],
        mode="lines", line=dict(color=color, width=width),
        hoverinfo="skip", showlegend=False
    ))
    edge_map[(parent.id, child.id, "vertical")] = len(fig.data) - 1

    fig.add_trace(go.Scatter(
        x=[x_parent, x_child], y=[y_parent, y_parent],
        mode="lines", line=dict(color=color, width=width),
        hoverinfo="skip", showlegend=False
    ))
    edge_map[(parent.id, child.id, "horizontal")] = len(fig.data) - 1


def draw_tree(node, fig, x_map, y_map, edge_map, color_map):
    """Recursively draw every branch in the tree."""
    if node.is_leaf():
        return

    color = color_map[node.id]
    draw_edge(node, node.left, fig, x_map, y_map, edge_map, color=color)
    draw_edge(node, node.right, fig, x_map, y_map, edge_map, color=color)

    draw_tree(node.left, fig, x_map, y_map, edge_map, color_map)
    draw_tree(node.right, fig, x_map, y_map, edge_map, color_map)


def draw_labels(fig, x_map, labels):
    """
    Draw leaf labels as a text trace below the dendrogram.
    Not currently called by create_dendrogram_new (leaf labels are
    instead rendered via the x-axis tick labels), but kept as an
    alternative if you ever want labels as plot annotations instead.
    """
    xs, ys, texts = [], [], []

    for leaf_id, label in enumerate(labels):
        xs.append(x_map[leaf_id])
        ys.append(-0.02)
        texts.append(label)

    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="text", text=texts,
        textposition="bottom center", hoverinfo="text", showlegend=False
    ))


def draw_depth_annotations(fig, root, x_map, y_map, depth_map):
    """
    Label each internal (merge) node with its depth from depth_map,
    so people can see which depth the "Fixed Depth" slider corresponds
    to directly on the tree.
    """
    xs, ys, texts = [], [], []

    def walk(node):
        if node.is_leaf():
            return
        xs.append(x_map[node.id])
        ys.append(y_map[node.id])
        texts.append(str(depth_map[node.id]))
        walk(node.left)
        walk(node.right)

    walk(root)

    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="markers+text", text=texts,
        textposition="top right",
        textfont=dict(size=10, color="#1B365D"),
        marker=dict(size=5, color="#1B365D", line=dict(width=1, color="white")),
        hoverinfo="skip", showlegend=False
    ))


# -----------------------------------------------------------------------
# Cluster coloring (mirrors scipy's default dendrogram coloring)
# -----------------------------------------------------------------------
DEFAULT_COLOR = "#1B365D"  # dark navy blue

SCIPY_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
]


def assign_cluster_colors(root, color_threshold=None):
    """
    Assign colors to nodes following SciPy's dendrogram coloring
    convention: the highest node below `color_threshold` starts a new
    cluster color, which then paints its entire subtree.

    color_threshold defaults to SciPy's own default: 0.7 * root.dist.
    """
    if color_threshold is None:
        color_threshold = 0.7 * root.dist

    color_map = {}
    color_cycle = cycle(SCIPY_COLORS)

    def paint_subtree(node, color):
        color_map[node.id] = color
        if not node.is_leaf():
            paint_subtree(node.left, color)
            paint_subtree(node.right, color)

    def recurse(node, parent_below_threshold=False):
        if node.is_leaf():
            if node.id not in color_map:
                color_map[node.id] = DEFAULT_COLOR
            return

        below = node.dist < color_threshold

        if below and not parent_below_threshold:
            paint_subtree(node, next(color_cycle))
            return

        if node.id not in color_map:
            color_map[node.id] = DEFAULT_COLOR

        recurse(node.left, below)
        recurse(node.right, below)

    recurse(root)
    return color_map


# -----------------------------------------------------------------------
# Top-level entry point
# -----------------------------------------------------------------------
def create_dendrogram_new(
    root,
    labels,
    depth_map,
    highlighted_edges=None,
    y_min=0.0,
    show_depth_labels=True
):
    """
    Build the full Plotly figure for the current (possibly zoomed) tree.

    y_min zooms the view: only the region [y_min, max_y] is shown.
    Since branches below y_min were already collapsed into single
    leaves upstream (see tree_utils.collapse_tree_at_threshold), this
    just trims the empty space below the cut rather than hiding real
    structure that's still in the figure.
    """
    fig = go.Figure()

    x_map = assign_x(root, {})
    y_map = assign_y(root, {})
    edge_map = {}

    color_map = assign_cluster_colors(root)
    draw_tree(root, fig, x_map, y_map, edge_map, color_map)

    if show_depth_labels:
        draw_depth_annotations(fig, root, x_map, y_map, depth_map)

    n = len(labels)
    fig_width = max(750, min(1000, 50 * n))
    fig_height = 1560

    # Pad the x-axis range a bit wider than the data to avoid cutting off labels.
    tick_interval = (x_map[1] - x_map[0]) if n > 1 else 1
    x_padding = tick_interval

    max_y = max(y_map.values())

    fig.update_layout(
        autosize=False,
        width=fig_width,
        height=fig_height,
        plot_bgcolor="white",
        margin=dict(l=60, r=40, t=10, b=140)
    )

    fig.update_xaxes(
        title=dict(text="Log Entry (with frequency)", font=dict(size=13, color="#1B365D")),
        tickmode="array",
        tickvals=[x_map[i] for i in range(len(labels))],
        ticktext=labels,
        tickangle=-90,
        range=[min(x_map.values()) - x_padding, max(x_map.values()) + x_padding],
        fixedrange=True,
        showline=True, linewidth=2, linecolor="black", mirror=False,
        ticks="outside", ticklen=5, tickwidth=1, tickcolor="black",
    )

    top = max_y * 1.05 if max_y > y_min else y_min + 0.05
    fig.update_yaxes(
        title=dict(text="NCD Distance", font=dict(size=13, color="#1B365D")),
        range=[y_min, top],
        fixedrange=True,
        showline=True, linewidth=2, linecolor="black", mirror=False,
        ticks="outside", ticklen=5, tickwidth=1, tickcolor="black",
    )

    if highlighted_edges is not None:
        for parent, child in highlighted_edges:
            for part in ("vertical", "horizontal"):
                idx = edge_map[(parent, child, part)]
                fig.data[idx].line.color = "red"
                fig.data[idx].line.width = 5

    return fig