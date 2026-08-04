"""
dashboard.py
------------
Builds the Panel dashboard (widgets, callbacks, layout) on top of an
already-computed pipeline state (see pipeline.run_preprocessing()).

Nothing in here starts a server or opens a browser -- build_dashboard()
just constructs and returns a pn.Column. Call server.serve_dashboard()
on the result (see main_demo.py) to actually show it.
"""

import panel as pn

import config
from tree_utils import build_zoomed_view, collect_frontier_with_early_leaves, path_to_leaf
from traversal_strategies import random_leaves_after_depth, rare_logs_after_depth, compute_depth_from_target_count
from dendrogram_plot import create_dendrogram_new
from story_llm import generate_story_llm


def build_dashboard(pipeline_state):
    """
    Build and return the Panel dashboard for the given pipeline_state
    dict (as returned by pipeline.run_preprocessing()).
    """
    # -------------------------------------------------------------------
    # Unpack the precomputed pipeline state
    # -------------------------------------------------------------------
    characters_bios = pipeline_state["characters_bios"]
    log_dict = pipeline_state["log_dict"]
    unique_logs = pipeline_state["unique_logs"]
    counts = pipeline_state["counts"]
    log_to_temporal_key = pipeline_state["log_to_temporal_key"]
    log_to_temporal_index = pipeline_state["log_to_temporal_index"]
    distance_matrix = pipeline_state["distance_matrix"]
    root_0 = pipeline_state["root_0"]
    view_data = pipeline_state["view_data"]

    depth_map = view_data["depth_map"]
    unique_logs_after_filtering = view_data["unique_logs_after_filtering"]
    most_anomalous_log = view_data["most_anomalous_log"]
    highest_NCD = view_data["highest_NCD"]

    selected_descriptions = []  # populated by update(); read by generate_story()

    # -------------------------------------------------------------------
    # Widgets
    # -------------------------------------------------------------------
    control_selector = pn.widgets.RadioButtonGroup(
        name="Control",
        options=["Fixed Depth", "Target Log Count"],
        value="Fixed Depth"
    )

    strategy_selector = pn.widgets.RadioButtonGroup(
        name="Strategy",
        options=["Random", "Least Frequent"],
        value="Random"
    )

    NCD_slider = pn.widgets.FloatSlider(
        name="NCD Filtering Threshold",
        start=0.0,
        end=0.9,
        value=config.INITIAL_NCD_THRESHOLD,
        step=0.05
    )

    depth_slider = pn.widgets.IntSlider(
        name="Starting Depth",
        start=0,
        end=max(depth_map.values()),
        value=1
    )

    target_count_slider = pn.widgets.IntSlider(
        name="Number of Target Logs (Calc. Depth)",
        start=1,
        end=len(unique_logs_after_filtering),
        value=2
    )

    seed_input = pn.widgets.IntInput(
        name="Seed",
        value=42,
        start=0,
        step=1
    )

    depth_slider_panel = pn.Column(
        depth_slider,
        sizing_mode="stretch_width",
        css_classes=["active-slider-panel"],
        margin=(0, 0, 0, 0),
    )

    target_count_slider_panel = pn.Column(
        target_count_slider,
        sizing_mode="stretch_width",
        css_classes=["inactive-slider-panel"],
        margin=(0, 0, 0, 0),
    )

    generate_story_button = pn.widgets.Button(
        name="Generate Story",
        button_type="primary",
        sizing_mode="stretch_width",
        height=45
    )

    story_pane = pn.pane.Markdown(
        "### Final Log-based Generated Story \n\nPress the button above to generate a story based on the logs.",
        sizing_mode="stretch_width",
        css_classes=["panel-card"],
    )

    story_column = pn.Column(
        generate_story_button,
        story_pane,
        sizing_mode="stretch_width",
        margin=(0, 0, 0, 0),
    )

    stats_pane = pn.pane.HTML(
        config.render_stats(counts, unique_logs, unique_logs_after_filtering, most_anomalous_log, highest_NCD),
        sizing_mode="stretch_width"
    )

    controls = pn.Column(
        pn.pane.HTML("""
        <div class='title-block'>
          <h2 style='margin:0; font-size:20px;'>Log Dendrogram Explorer</h2>
          <div style='margin-top:4px; opacity:0.9;'>Explore representative log pools from the dendrogram.</div>
        </div>
        """),
        pn.pane.HTML(
            "<div class='section-title'>Controls</div>"
            "<div class='helper-text'>Choose a traversal control mode (where to start the traversal), "
            "then a branch selection strategy (which branches are selected) and seed to explore "
            "different representative log pools.</div>"
        ),
        pn.Column(
            pn.pane.HTML("<div class='section-title'>Traversal Control Mode</div>"),
            NCD_slider,
            control_selector,
            depth_slider_panel,
            target_count_slider_panel,
            pn.pane.HTML("<div class='section-title'>Branch Selection Strategy</div>"),
            strategy_selector,
            pn.pane.HTML("<div class='section-title'>Random Seed</div>"),
            seed_input,
            css_classes=["panel-card"],
            sizing_mode="stretch_width",
            margin=(0, 0, 0, 0)
        ),
        stats_pane,
        sizing_mode="stretch_width",
        margin=(0, 0, 0, 0)
    )

    output = pn.Column(sizing_mode="stretch_width", margin=(0, 0, 0, 0))

    details_pane = pn.pane.Markdown(
        "### Final Log Pool\n\nChoose a strategy to populate this panel with the representative log entries.",
        sizing_mode="stretch_width",
        css_classes=["panel-card"]
    )

    bios_pane = pn.pane.Markdown(
        "### Characters' Bios\n\n" + characters_bios.replace("\n", "<br>"),
        sizing_mode="stretch_width",
        css_classes=["panel-card"]
    )

    # -------------------------------------------------------------------
    # Callbacks
    # -------------------------------------------------------------------
    def update_controls(event=None):
        """Toggle which of depth_slider / target_count_slider is active."""
        if control_selector.value == "Fixed Depth":
            depth_slider.disabled = False
            target_count_slider.disabled = True
            depth_slider_panel.css_classes = ["active-slider-panel"]
            target_count_slider_panel.css_classes = ["inactive-slider-panel"]
        else:
            depth_slider.disabled = True
            target_count_slider.disabled = False
            depth_slider_panel.css_classes = ["inactive-slider-panel"]
            target_count_slider_panel.css_classes = ["active-slider-panel"]

    def update(event=None):
        """Recompute the zoomed tree + selected log pool and redraw the dendrogram."""
        NCD_threshold = NCD_slider.value
        control = control_selector.value
        strategy = strategy_selector.value
        depth = depth_slider.value
        target_count = target_count_slider.value
        seed = seed_input.value

        # Zoom into the SAME canonical tree (root_0) at the new threshold --
        # this does not re-cluster, so merge heights stay true to the original data.
        view_data = build_zoomed_view(
            root_0, unique_logs, counts, distance_matrix,
            threshold=NCD_threshold, log_dict=log_dict
        )

        root = view_data["root"]
        depth_map = view_data["depth_map"]
        freq_map = view_data["freq_map"]
        labels = view_data["labels"]
        unique_logs_after_filtering = view_data["unique_logs_after_filtering"]
        most_anomalous_log = view_data["most_anomalous_log"]
        highest_NCD = view_data["highest_NCD"]

        # We can only display a dendrogram with more than 1 log (else, distance matrix won't even work).
        if len(unique_logs_after_filtering) < 2:
            output[:] = [pn.pane.Markdown(
                "### <2 logs remain after filtering. Please adjust the NCD threshold.",
                sizing_mode="stretch_width", css_classes=["panel-card"]
            )]
            details_pane.object = "### Final Log Pool\n\n<2 logs remain after filtering. Please adjust the NCD threshold."
            return

        # Update the other sliders' bounds. Guard against the new `.end` being
        # lower than the widget's current `.value` -- Panel raises a
        # ValueError if you leave a widget's value outside its own bounds,
        # and since the collapsed tree's size can shrink a lot between
        # thresholds, this is easy to hit in practice.
        depth_slider.end = max(depth_map.values())
        if depth_slider.value > depth_slider.end:
            depth_slider.value = depth_slider.end
            depth = depth_slider.value

        target_count_slider.end = len(unique_logs_after_filtering)
        if target_count_slider.value > target_count_slider.end:
            target_count_slider.value = target_count_slider.end
            target_count = target_count_slider.value

        stats_pane.object = config.render_stats(
            counts, unique_logs, unique_logs_after_filtering, most_anomalous_log, highest_NCD
        )

        if control == "Target Log Count":
            depth = compute_depth_from_target_count(root, depth_map, target_count)
            target_count_slider.name = f"Number of Target Logs (Calc. Depth {depth})"

        frontier_nodes, early_leaf_nodes = collect_frontier_with_early_leaves(root, depth_map, depth)

        if strategy == "Random":
            leaf_ids, traversed_edges = random_leaves_after_depth(
                root=root, depth_map=depth_map, target_depth=depth, seed=seed
            )
        else:
            leaf_ids, traversed_edges = rare_logs_after_depth(
                root=root, depth_map=depth_map, freq_map=freq_map, target_depth=depth, seed=seed
            )

        for leaf in early_leaf_nodes:
            leaf_ids.append(leaf.id)
            traversed_edges.update(path_to_leaf(root, leaf.id))

        fig = create_dendrogram_new(root, labels, depth_map, highlighted_edges=traversed_edges, y_min=NCD_threshold)

        # Deduplicate while preserving first-seen order...
        leaf_ids = list(dict.fromkeys(leaf_ids))

        # ...then reorder chronologically, using each log's real embedded
        # timestamp (falls back to original file position for logs with no
        # timestamp tag, so ordering stays deterministic either way). This
        # is what both the "Final Log Pool" display and the story LLM
        # prompt see.
        leaf_ids.sort(key=lambda i: (
            log_to_temporal_key[unique_logs_after_filtering[i]],
            log_to_temporal_index[unique_logs_after_filtering[i]],
        ))

        selected_descriptions.clear()
        selected_rows = []
        for i in leaf_ids:
            event_text = unique_logs_after_filtering[i]
            selected_descriptions.append(labels[i])
            selected_rows.append(f"- {log_dict[event_text]}  \n `{labels[i]}`")

        details = "### Final Log Pool\n\n" + "\n".join(selected_rows)

        output[:] = [
            pn.pane.Plotly(
                fig,
                config={"responsive": False},
                sizing_mode="fixed",
                width=fig.layout.width,
                height=fig.layout.height
            )
        ]
        details_pane.object = details

    def generate_story(event):
        """Send the currently selected log pool to the LLM and show the resulting story."""
        story_pane.loading = True
        generate_story_button.name = "Generating Story..."
        generate_story_button.disabled = True

        try:
            story = generate_story_llm(characters_bios, selected_descriptions)
            story_pane.object = "### Final Log-based Generated Story\n\n" + story
        except Exception as e:
            story_pane.object = f"**Error:**\n\n```\n{e}\n```"
        finally:
            generate_story_button.name = "Generate Story"
            generate_story_button.disabled = False
            story_pane.loading = False

    # -------------------------------------------------------------------
    # Wire up widgets + build the layout
    # -------------------------------------------------------------------
    depth_slider.disabled = False
    target_count_slider.disabled = True

    update_controls()
    control_selector.param.watch(update_controls, "value")
    for widget in (depth_slider, target_count_slider, strategy_selector, control_selector, seed_input, NCD_slider):
        widget.param.watch(update, "value")

    generate_story_button.on_click(generate_story)

    update()  # initial render

    dashboard = pn.Column(
        pn.Row(
            pn.Column(
                controls,
                details_pane,
                bios_pane,
                story_column,
                sizing_mode="stretch_width",
                css_classes=["app-shell"],
                min_width=320,
                max_width=380
            ),
            pn.Spacer(width=20),
            pn.Column(
                pn.pane.HTML(
                    "<div class='section-title'>Dendrogram</div>"
                    "<div class='helper-text'>Highlighted red branches show the paths selected by "
                    "the current traversal strategies.</div>"
                ),
                output,
                sizing_mode="stretch_both",
                css_classes=["app-shell"],
                width_policy="max",
                min_width=700,
                max_width=1100
            ),
            align="start"
        ),
        sizing_mode="stretch_width",
        name="Log Dendrogram Explorer"
    )

    return dashboard