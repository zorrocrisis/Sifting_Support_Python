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
  python main_demo.py generate    -> HEADLESS: calls the LLM against an
                                      ALREADY-SELECTED log pool (deliberately
                                      does NOT re-run preprocessing/selection
                                      -- see log_selection/story_llm design
                                      note below) and prints the generated
                                      text as JSON to stdout. Requires
                                      --final-log-pool and --bios-log; see
                                      --generation-mode for narrative vs.
                                      dialogue output.
 
All three headless modes are intended for the C# RimWorld mod to call
directly and read the results back over stdout, with no browser window
ever opening.
 
Optional path overrides (any mode), useful for the C# mod to pass paths
as plain arguments instead of relying on config.RUNNING_WITHIN_GAME's
stdin convention:
 
  python main_demo.py preprocess --full-log X --bios-log Z
 
DESIGN NOTE on why `generate` is separate from `select` rather than a
combined "preprocess+select+generate" mode: NCD preprocessing is cheap,
local, and deterministic, so `select` re-running it on every call is
fine. LLM generation is a paid network call with variable latency --
you often want to retry it, or generate BOTH narrative and dialogue
variants from the exact same pool, without paying the NCD cost again
each time. Keeping `generate` standalone lets the C# side call `select`
once, then call `generate` as many times as needed against that same
pool. `generate` also deliberately never imports pipeline.py (no
scipy/numpy), so it starts fast -- it has nothing to do with clustering.
 
The pipeline itself lives in pipeline.py (run_preprocessing), the "final
log pool" selection logic lives in log_selection.py (select_final_log_pool
/ select_leaf_ids -- shared with the dashboard, so both always pick logs
the same way), the LLM call lives in story_llm.py (generate_story_llm),
and the dashboard UI lives in dashboard.py (build_dashboard). All of
these are importable and callable on their own, independent of this CLI
wrapper. Heavy imports (panel, pipeline) are all done lazily inside the
functions that need them, so each headless mode only pays for what it
actually uses.
"""
 
import argparse
import json
import sys

# Force stdout/stderr to UTF-8 regardless of the host's default console
# codepage (Windows in particular can default to something like cp1252,
# which would either mangle non-ASCII characters or raise
# UnicodeEncodeError once we stop escaping them as \uXXXX below).
# Requires the corresponding C# side to read this process's stdout/stderr
# as UTF-8 too (ProcessStartInfo.StandardOutputEncoding/StandardErrorEncoding
# = Encoding.UTF8) -- otherwise Python emits correct UTF-8 bytes but C#
# decodes them with the wrong codepage, producing mojibake instead of
# clean text.
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
 
 
def print_json(obj):
    """
    print(json.dumps(...)) but with ensure_ascii=False, so characters
    like curly quotes/em dashes come through as themselves (e.g. an
    apostrophe) instead of escaped as \\uXXXX. Used for every JSON
    result this CLI emits, so stdout stays consistent across modes.
    """
    print(json.dumps(obj, ensure_ascii=False))
 
 
 
def parse_args():
    parser = argparse.ArgumentParser(description="Log Dendrogram Explorer")
    parser.add_argument(
        "mode", nargs="?", default="demo", choices=["demo", "preprocess", "select", "generate"],
        help="'demo' (default): open the interactive dashboard in a browser tab. "
             "'preprocess': run only the log loading + clustering pipeline and "
             "print the results as JSON to stdout -- no browser/UI. "
             "'select': same as 'preprocess', but also selects and includes a "
             "final log pool (see --ncd-threshold/--control/--strategy/etc below). "
             "'generate': call the LLM against an ALREADY-SELECTED log pool "
             "(see --final-log-pool/--bios-log/--generation-mode below) -- no "
             "preprocessing/selection re-run, no scipy/numpy import."
    )
    parser.add_argument("--full-log", dest="full_log", default=None,
                         help="Path to the full-length log file (overrides config/stdin resolution).")
    parser.add_argument("--bios-log", dest="characters_bios_log", default=None,
                         help="Path to the character bios file (overrides config/stdin resolution). "
                              "Also used by 'generate' mode.")
 
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
 
    # 'generate'-mode only.
    parser.add_argument("--final-log-pool", dest="final_log_pool", default=None,
                         help="[generate mode] Path to a plain text file, one formatted log line per line "
                              "(e.g. the file C#'s WriteFinalLogsToFiles already writes).")
    parser.add_argument("--generation-mode", dest="generation_mode", choices=["narrative", "dialogue"], default="narrative",
                         help="[generate mode] Which prompt to use (see story_llm.PROMPTS).")
 
    return parser.parse_args()
 

def run_demo(full_log=None, characters_bios_log=None):
    """Run the full pipeline and open the interactive dashboard in a browser tab."""
    # Imported lazily so headless modes never touch Panel/Bokeh/scipy at all.
    import panel as pn
    import config
    import pipeline
    from dashboard import build_dashboard
    import server

    pn.extension("plotly")
    pn.extension(raw_css=config.DASHBOARD_CSS)

    # If the user didn't explicitly pass paths, resolve them via config/stdin.
    if full_log is None or characters_bios_log is None:
        full_log, characters_bios_log = pipeline.resolve_input_paths()

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
    import pipeline
    import time

    # If the user didn't explicitly pass paths, resolve them via config/stdin.
    if full_log is None or characters_bios_log is None:
        full_log, characters_bios_log = pipeline.resolve_input_paths()

    # try/finally (not try/except): a real failure here should still
    # crash the process with a non-zero exit code, same as before this
    # logging was added -- if the C# side checks process.ExitCode to
    # detect failure, silently swallowing the exception into a JSON
    # "error" field would break that. finally still lets us log timing
    # and failure metrics before the exception propagates.
    start = time.perf_counter()
    pipeline_state = None
    error = None
    try:
        pipeline_state = pipeline.run_preprocessing(full_log, characters_bios_log)
    except Exception as e:
        error = str(e)
        raise
    finally:
        duration_seconds = time.perf_counter() - start
        view_data = pipeline_state["view_data"] if pipeline_state else None
        log_run_metrics({
            "mode": "preprocess",
            "full_log_path": full_log,
            "characters_bios_log_path": characters_bios_log,
            "duration_seconds": round(duration_seconds, 4),
            "success": error is None,
            "error": error,
            "unique_log_count": len(pipeline_state["unique_logs"]) if pipeline_state else None,
            "unique_log_count_after_filtering": len(view_data["unique_logs_after_filtering"]) if view_data else None,
        })

    view_data = pipeline_state["view_data"]
    result = {
        "counts": pipeline_state["counts"],
        "unique_logs": pipeline_state["unique_logs"],
        "visibility": pipeline_state["visibility"],
        "unique_logs_after_filtering": view_data["unique_logs_after_filtering"]
    }

    print_json(result)

    # Logging
    write_to_file(full_log, json.dumps(result, ensure_ascii=False), "preprocess_logs")



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
    import pipeline
    import time

    # If the user didn't explicitly pass paths, resolve them via config/stdin.
    if args.full_log is None or args.characters_bios_log is None:
        args.full_log, args.characters_bios_log = pipeline.resolve_input_paths()

    # try/finally, not try/except -- see the matching comment in
    # run_preprocess_headless for why a real failure must still crash
    # the process rather than being swallowed into a JSON error field.
    overall_start = time.perf_counter()
    pipeline_state = None
    selection = None
    error = None
    preprocessing_duration = None
    selection_duration = None
    try:
        t0 = time.perf_counter()
        pipeline_state = pipeline.run_preprocessing(args.full_log, args.characters_bios_log)
        preprocessing_duration = time.perf_counter() - t0

        ncd_threshold = args.ncd_threshold
        if ncd_threshold is None:
            import config
            ncd_threshold = config.INITIAL_NCD_THRESHOLD

        t1 = time.perf_counter()
        selection = select_final_log_pool(
            pipeline_state,
            ncd_threshold=ncd_threshold,
            control=args.control,
            strategy=args.strategy,
            depth=args.depth,
            target_count=args.target_count,
            seed=args.seed,
        )
        selection_duration = time.perf_counter() - t1
    except Exception as e:
        error = str(e)
        raise
    finally:
        total_duration = time.perf_counter() - overall_start
        log_run_metrics({
            "mode": "select",
            "full_log_path": args.full_log,
            "characters_bios_log_path": args.characters_bios_log,
            "ncd_threshold": args.ncd_threshold,
            "control": args.control,
            "strategy": args.strategy,
            "depth": args.depth,
            "target_count": args.target_count,
            "seed": args.seed,
            "resolved_depth": selection.get("resolved_depth") if selection else None,
            "preprocessing_duration_seconds": round(preprocessing_duration, 4) if preprocessing_duration is not None else None,
            "selection_duration_seconds": round(selection_duration, 4) if selection_duration is not None else None,
            "total_duration_seconds": round(total_duration, 4),
            "success": error is None,
            "error": error,
            "unique_log_count": len(pipeline_state["unique_logs"]) if pipeline_state else None,
            "final_log_pool_size": len(selection["final_log_pool_short"]) if selection else None,
        })

    result = {
        "counts": pipeline_state["counts"],
        "unique_logs": pipeline_state["unique_logs"],
        "visibility": pipeline_state["visibility"],
        **selection
        
    }

    print_json(result)

    # Logging
    write_to_file(args.full_log, json.dumps(result, ensure_ascii=False), "select_logs")


def run_generate_headless(args):
    """
    Call the LLM against an ALREADY-SELECTED log pool and print the
    result as JSON to stdout. Deliberately does not import pipeline.py
    (no scipy/numpy) -- this mode has nothing to do with clustering, it
    just reads two text files and makes one API call.
    """
    from story_llm import generate_story_llm, load_final_log_pool
    import time

    if not args.final_log_pool:
        result = {"story": None, "mode": args.generation_mode, "usage": None,
                   "error": "generate mode requires --final-log-pool <path>"}
        print_json(result)
        log_run_metrics({
            "mode": "generate",
            "generation_mode": args.generation_mode,
            "final_log_pool_path": args.final_log_pool,
            "characters_bios_log_path": args.characters_bios_log,
            "duration_seconds": 0.0,
            "success": False,
            "error": result["error"],
            "final_log_pool_size": None,
            "story_length_chars": None,
        })
        return
    if not args.characters_bios_log:
        result = {"story": None, "mode": args.generation_mode, "usage": None,
                   "error": "generate mode requires --bios-log <path>"}
        print_json(result)
        log_run_metrics({
            "mode": "generate",
            "generation_mode": args.generation_mode,
            "final_log_pool_path": args.final_log_pool,
            "characters_bios_log_path": args.characters_bios_log,
            "duration_seconds": 0.0,
            "success": False,
            "error": result["error"],
            "final_log_pool_size": None,
            "story_length_chars": None,
        })
        return

    start = time.perf_counter()
    selected_descriptions = []
    usage = None
    try:
        selected_descriptions = load_final_log_pool(args.final_log_pool)
        with open(args.characters_bios_log, "r", encoding="utf-8", errors="ignore") as f:
            characters_bios = f.read()

        story, usage = generate_story_llm(characters_bios, selected_descriptions, mode=args.generation_mode, return_usage=True)
        result = {"story": story, "mode": args.generation_mode, "usage": usage, "error": None}
    except Exception as e:
        # Mirror dashboard.py's generate_story(): never let an LLM/network
        # failure crash the process -- report it as data instead, same as
        # every other headless mode's error handling.
        result = {"story": None, "mode": args.generation_mode, "usage": None, "error": str(e)}
    duration_seconds = time.perf_counter() - start

    # `result` is built in BOTH the try and except branches above, so this
    # must stay unconditional and outside the try/except -- printing it
    # only from inside the try (as a previous version of this function
    # did) means a failure prints nothing at all to stdout.
    print_json(result)

    write_to_file(args.final_log_pool, json.dumps(result, ensure_ascii=False), f"generate_{args.generation_mode}_logs")

    log_run_metrics({
        "mode": "generate",
        "generation_mode": args.generation_mode,
        "final_log_pool_path": args.final_log_pool,
        "characters_bios_log_path": args.characters_bios_log,
        "duration_seconds": round(duration_seconds, 4),
        "success": result["error"] is None,
        "error": result["error"],
        "final_log_pool_size": len(selected_descriptions),
        "story_length_chars": len(result["story"]) if result["story"] else None,
        "prompt_tokens": usage.get("prompt_tokens") if usage else None,
        "completion_tokens": usage.get("completion_tokens") if usage else None,
        "total_tokens": usage.get("total_tokens") if usage else None,
        "model": usage.get("model") if usage else None,
    })

def write_to_file(log_path, content, file_name):
    """
    Write `content` (a string) to <parent of log_path>/<file_name>.txt,
    overwriting any previous file with that name -- a per-run debug
    snapshot of the most recent result. This is great for "what did the
    last run actually return", but since it overwrites, it can't be
    used for analysis across many runs -- see log_run_metrics() for that.
    """
    from pathlib import Path

    path = Path(log_path)
    story_file = str(path.parent) + "\\" + file_name + ".txt"

    with open (story_file, "w", encoding="utf-8", errors="ignore") as out:
        out.write(content)


# Where log_run_metrics() appends to. Relative to the working directory
# main_demo.exe is launched from -- C# already sets WorkingDirectory to
# the exe's own folder, so this resolves to a stable, predictable path
# next to the exe rather than somewhere inside a per-session RimWorld
# log folder. Change to an absolute path if you'd rather keep it
# elsewhere (e.g. alongside the RimWorld log folders themselves).
RUN_METRICS_LOG_PATH = "run_metrics.jsonl"


def log_run_metrics(metrics):
    """
    Append one JSON-line record to RUN_METRICS_LOG_PATH -- an
    append-only log of every CLI invocation (any mode, success or
    failure), meant for later data analysis (e.g.
    `pandas.read_json(RUN_METRICS_LOG_PATH, lines=True)`) rather than
    just "what did the last run do" debugging, which write_to_file()
    already covers.

    Never raises: a logging failure (e.g. a file permissions issue)
    should never take down the actual demo/generation run, so any
    error here is reported to stderr and swallowed rather than
    propagated.

    `metrics` should be a flat, JSON-serializable dict. This function
    adds `timestamp` and `argv` itself -- don't pass those keys.
    """
    from datetime import datetime, timezone

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "argv": sys.argv[1:],
        **metrics,
    }

    try:
        with open(RUN_METRICS_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[main_demo] Warning: failed to write run metrics: {e}", file=sys.stderr)


if __name__ == "__main__":
    args = parse_args()

    if args.mode == "preprocess":
        run_preprocess_headless(args.full_log, args.characters_bios_log)
    elif args.mode == "select":
        run_select_headless(args)
    elif args.mode == "generate":
        run_generate_headless(args)
    else:
        run_demo(args.full_log, args.characters_bios_log)