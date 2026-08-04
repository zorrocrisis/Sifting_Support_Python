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
                                      to stdout. Intended for the C# RimWorld
                                      mod to call directly and read the
                                      deduplicated logs back over stdout.

Optional path overrides (either mode), useful for the C# mod to pass
paths as plain arguments instead of relying on config.RUNNING_WITHIN_GAME's
stdin convention:

  python main_demo.py preprocess --full-log X --short-log Y --bios-log Z

The pipeline itself lives in pipeline.py (run_preprocessing), and the
dashboard UI lives in dashboard.py (build_dashboard) -- both are
importable and callable on their own, independent of this CLI wrapper.
Neither of those modules imports Panel eagerly here: `demo` mode imports
it lazily so `preprocess` mode never touches Panel/Bokeh at all.
"""

import argparse
import json

import pipeline


def parse_args():
    parser = argparse.ArgumentParser(description="Log Dendrogram Explorer")
    parser.add_argument(
        "mode", nargs="?", default="demo", choices=["demo", "preprocess"],
        help="'demo' (default): open the interactive dashboard in a browser tab. "
             "'preprocess': run only the log loading + clustering pipeline and "
             "print the results as JSON to stdout -- no browser/UI, for headless "
             "use by the C# mod."
    )
    parser.add_argument("--full-log", dest="full_log", default=None,
                         help="Path to the full-length log file (overrides config/stdin resolution).")
    parser.add_argument("--short-log", dest="short_log", default=None,
                         help="Path to the short-description log file (overrides config/stdin resolution).")
    parser.add_argument("--bios-log", dest="characters_bios_log", default=None,
                         help="Path to the character bios file (overrides config/stdin resolution).")
    return parser.parse_args()


def run_demo(full_log=None, short_log=None, characters_bios_log=None):
    """Run the full pipeline and open the interactive dashboard in a browser tab."""
    # Imported lazily so `preprocess` mode never touches Panel/Bokeh at all.
    import panel as pn
    import config
    from dashboard import build_dashboard
    import server

    pn.extension("plotly")
    pn.extension(raw_css=config.DASHBOARD_CSS)

    pipeline_state = pipeline.run_preprocessing(full_log, short_log, characters_bios_log)
    dashboard = build_dashboard(pipeline_state)
    dashboard.servable(title="Log Dendrogram Explorer")

    server.serve_dashboard(dashboard)


def run_preprocess_headless(full_log=None, short_log=None, characters_bios_log=None):
    """
    Run only the log loading + hierarchical-clustering pipeline (no
    Panel, no browser) and print the resulting unique logs + a bit of
    metadata as a single line of JSON to stdout, for the C# mod to read
    directly from the process's standard output.
    """
    pipeline_state = pipeline.run_preprocessing(full_log, short_log, characters_bios_log)
    view_data = pipeline_state["view_data"]

    result = {
        "unique_logs": pipeline_state["unique_logs"],
        "counts": pipeline_state["counts"],
        "unique_logs_after_filtering": view_data["unique_logs_after_filtering"]
    }
    print(json.dumps(result))


if __name__ == "__main__":
    args = parse_args()

    if args.mode == "preprocess":
        run_preprocess_headless(args.full_log, args.short_log, args.characters_bios_log)
    else:
        run_demo(args.full_log, args.short_log, args.characters_bios_log)