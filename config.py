"""
config.py
---------
Static configuration for the Log Dendrogram Explorer: file paths, CSS,
and the small HTML template used to render the "Dataset Summary" stats
panel. Nothing in here depends on Panel/Plotly/scipy, so it's safe to
import from anywhere without triggering side effects.
"""

import sys

# -----------------------------------------------------------------------
# Running within game enabler
# -----------------------------------------------------------------------
RUNNING_WITHIN_GAME = False # Set to True when running inside the game enabler (C# host process)

# -----------------------------------------------------------------------
# Input file paths
# -----------------------------------------------------------------------
# TEST SCENARIO 1 (active)
FULL_LOG_FILE = "CoG10Min.txt"
CHARACTERS_BIOS_LOG_FILE = "bios.txt"

# TEST SCENARIO 2 (kept for quick swapping during testing)
# SHORT_LOG_FILE = "all_events_descriptionsonly.txt"
# FULL_LOG_FILE = "all_events_complete.txt"
# CHARACTERS_BIOS_LOG_FILE = "bios.txt"

# Starting point for the NCD filtering slider.
INITIAL_NCD_THRESHOLD = 0.5

# Cap on how many unique log lines we load before deduplication kicks in.
MAX_LOG_LINES = 20000


def get_input_paths():
    """
    Reads three lines from stdin (sent by an external host process, e.g.
    a C# game client): full log path, short log path, character bios path.

    NOT currently called -- the app uses the hardcoded SHORT_LOG_FILE /
    FULL_LOG_FILE / CHARACTERS_BIOS_LOG_FILE constants above instead.
    Kept here so wiring it back in (for real game integration) is a
    one-line change in main_demo.py rather than a rewrite.
    """
    full_log = sys.stdin.readline().strip()
    short_log = sys.stdin.readline().strip()
    characters_bios_log = sys.stdin.readline().strip()

    if not full_log or not short_log or not characters_bios_log:
        raise ValueError(
            "Expected three non-empty lines on stdin "
            "(full_log_file, short_log_file, characters_bios_log_file), "
            f"got: full={full_log!r}, short={short_log!r}, "
            f"character_bios={characters_bios_log!r}"
        )
    return full_log, short_log, characters_bios_log


# -----------------------------------------------------------------------
# Stats panel
# -----------------------------------------------------------------------
STATS_TEMPLATE = (
    "<div class='panel-card' style='margin-bottom: 12px;'>"
    "<div class='section-title'>Dataset Summary</div>"
    "<div class='helper-text'>"
    "<b>Total log in session:</b> {total}<br>"
    "<b>Unique logs after string deduplication:</b> {unique}<br>"
    "<b>Unique logs after NCD-based filtering:</b> {unique_filtered}<br>"
    "<b>Most 'unique' log:</b> {most_unique_log} (NCD score of {highest_NCD:.2f})<br>"
    "</div></div>"
)


def render_stats(counts, unique_logs, unique_logs_after_filtering, most_unique_log, highest_NCD):
    """Fill in STATS_TEMPLATE with the current session's numbers."""
    return STATS_TEMPLATE.format(
        total=sum(counts.values()),
        unique=len(unique_logs),
        unique_filtered=len(unique_logs_after_filtering),
        most_unique_log=most_unique_log,
        highest_NCD=highest_NCD
    )


# -----------------------------------------------------------------------
# Panel / CSS theming
# -----------------------------------------------------------------------
DASHBOARD_CSS = [
    ".app-shell { background: linear-gradient(135deg, #f8fbff 0%, #eef4ff 100%); "
    "padding: 20px; border-radius: 16px; overflow: hidden; }",

    ".panel-card { background: white; border: 1px solid #dfe8f7; border-radius: 14px; "
    "padding: 16px; box-shadow: 0 4px 14px rgba(27, 54, 93, 0.08); }",

    ".title-block { background: linear-gradient(90deg, #1b365d 0%, #3563a5 100%); "
    "color: white; padding: 16px 20px; border-radius: 12px; margin-bottom: 12px; }",

    ".section-title { font-size: 14px; font-weight: 700; color: #1b365d; "
    "letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: 8px; }",

    ".helper-text { color: #4b5f7a; font-size: 13px; line-height: 1.45; margin-bottom: 10px; }",

    ".active-slider-panel { background: linear-gradient(135deg, #eefcf2 0%, #dcf8e4 100%); "
    "border: 1px solid #5fcf7a; border-radius: 10px; padding: 10px; }",

    ".inactive-slider-panel { background: #f9fbff; border: 1px solid #dde7f3; "
    "border-radius: 10px; padding: 10px; }",

    ".bk-Widget { border-radius: 8px; }",
]
