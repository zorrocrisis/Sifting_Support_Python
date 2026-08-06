"""
main_demo.py
------------
Entry point for the Log Dendrogram Explorer.

  python main_demo.py             -> opens the interactive dashboard (default)
  python main_demo.py demo        -> same as above, explicit
  python main_demo.py preprocess  -> HEADLESS: runs only the log loading +
                                      hierarchical-clustering pipeline (no
                                      Panel, no browser window at all) and
                                      prints the results as one line of JSON
                                      to stdout.
  python main_demo.py select      -> HEADLESS: runs the same preprocessing as
                                      `preprocess`, THEN also selects a "final
                                      log pool" (same traversal control /
                                      strategy / seed knobs the dashboard
                                      exposes) and includes it in the JSON
                                      printed to stdout. See --ncd-threshold,
                                      --control, --strategy, --depth,
                                      --target-count, --seed below.

Both headless modes are intended for the C# RimWorld mod to call directly
and read the results back over stdout, with no browser window ever opening.

Optional path overrides (any mode), useful for the C# mod to pass paths
as plain arguments instead of relying on config.RUNNING_WITHIN_GAME's
stdin convention:

  python main_demo.py preprocess --full-log X --short-log Y --bios-log Z

The pipeline itself lives in pipeline.py (run_preprocessing), the "final
log pool" selection logic lives in log_selection.py (select_final_log_pool
/ select_leaf_ids -- shared with the dashboard, so both always pick logs
the same way), and the dashboard UI lives in dashboard.py (build_dashboard).
All three are importable and callable on their own, independent of this
CLI wrapper. Neither `preprocess` nor `select` mode imports Panel: `demo`
mode imports it lazily so headless modes never touch Panel/Bokeh at all.
"""

import argparse
import json

import pipeline


def parse_args():
    parser = argparse.ArgumentParser(description="Log Dendrogram Explorer")
    parser.add_argument(
        "mode", nargs="?", default="demo", choices=["demo", "preprocess", "select"],
        help="'demo' (default): open the interactive dashboard in a browser tab. "
             "'preprocess': run only the log loading + clustering pipeline and "
             "print the results as JSON to stdout -- no browser/UI. "
             "'select': same as 'preprocess', but also selects and includes a "
             "final log pool (see --ncd-threshold/--control/--strategy/etc below)."
    )
    parser.add_argument("--full-log", dest="full_log", default=None,
                         help="Path to the full-length log file (overrides config/stdin resolution).")
    parser.add_argument("--short-log", dest="short_log", default=None,
                         help="Path to the short-description log file (overrides config/stdin resolution).")
    parser.add_argument("--bios-log", dest="characters_bios_log", default=None,
                         help="Path to the character bios file (overrides config/stdin resolution).")

    # 'select'-mode only: mirror the dashboard's traversal controls.
    parser.add_argument("--ncd-threshold", dest="ncd_threshold", type=float, default=None,
                         help="NCD 'zoom' threshold for log deduplication (default: config.INITIAL_NCD_THRESHOLD).")
    parser.add_argument("--control", dest="control", choices=["fixed_depth", "target_count"], default="fixed_depth",
                         help="'fixed_depth': start traversal at --depth. "
                              "'target_count': pick the depth that yields ~--target-count logs.")
    parser.add_argument("--strategy", dest="strategy", choices=["random", "least_frequent"], default="random",
                         help="Branch selection strategy at each split below the starting depth.")
    parser.add_argument("--depth", dest="depth", type=int, default=1,
                         help="Starting depth, used when --control=fixed_depth.")
    parser.add_argument("--target-count", dest="target_count", type=int, default=2,
                         help="Desired final log pool size, used when --control=target_count.")
    parser.add_argument("--seed", dest="seed", type=int, default=42,
                         help="Random seed for the 'random' strategy (and tie-breaking in 'least_frequent').")

    return parser.parse_args()


def run_demo(full_log=None, characters_bios_log=None):
    """Run the full pipeline and open the interactive dashboard in a browser tab."""
    # Imported lazily so `preprocess` mode never touches Panel/Bokeh at all.
    import panel as pn
    import config
    from dashboard import build_dashboard
    import server

    pn.extension("plotly")
    pn.extension(raw_css=config.DASHBOARD_CSS)

    pipeline_state = pipeline.run_preprocessing(full_log, characters_bios_log)
    dashboard = build_dashboard(pipeline_state)
    dashboard.servable(title="Log Dendrogram Explorer")

    server.serve_dashboard(dashboard)


def run_preprocess_headless(full_log=None, characters_bios_log=None):
    """
    Run only the log loading + hierarchical-clustering pipeline (no
    Panel, no browser) and print the resulting unique logs + a bit of
    metadata as a single line of JSON to stdout, for the C# mod to read
    directly from the process's standard output.
    """
    pipeline_state = pipeline.run_preprocessing(full_log, characters_bios_log)
    view_data = pipeline_state["view_data"]

    result = {
        "counts": pipeline_state["counts"],
        "unique_logs": pipeline_state["unique_logs"],
        "visibility": pipeline_state["visibility"],
        "unique_logs_after_filtering": view_data["unique_logs_after_filtering"]
    }

    print(json.dumps(result))


def run_select_headless(args):
    """
    Run the same preprocessing as `preprocess`, then ALSO select a final
    log pool using the given traversal knobs, and print everything as a
    single line of JSON to stdout. No Panel, no browser.
    """
    # Imported lazily (rather than at module scope) purely for symmetry
    # with run_demo()'s lazy Panel import -- log_selection.py itself
    # doesn't touch Panel, but keeping headless-mode imports scoped to
    # their function makes it obvious at a glance which modes are heavy.
    from log_selection import select_final_log_pool

    pipeline_state = pipeline.run_preprocessing(args.full_log, args.characters_bios_log)

    ncd_threshold = args.ncd_threshold
    if ncd_threshold is None:
        import config
        ncd_threshold = config.INITIAL_NCD_THRESHOLD

    selection = select_final_log_pool(
        pipeline_state,
        ncd_threshold=ncd_threshold,
        control=args.control,
        strategy=args.strategy,
        depth=args.depth,
        target_count=args.target_count,
        seed=args.seed,
    )

    result = {
        "counts": pipeline_state["counts"],
        "unique_logs": pipeline_state["unique_logs"],
        "visibility": pipeline_state["visibility"],
        **selection
        
    }

    print(json.dumps(result))


if __name__ == "__main__":
    args = parse_args()

    if args.mode == "preprocess":
        run_preprocess_headless(args.full_log, args.characters_bios_log)
    elif args.mode == "select":
        run_select_headless(args)
    else:
        run_demo(args.full_log, args.characters_bios_log)