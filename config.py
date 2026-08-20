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
RUNNING_WITHIN_GAME = True # Set to True when running inside the game enabler (C# host process)

# -----------------------------------------------------------------------
# Input file paths
# -----------------------------------------------------------------------
# TEST SCENARIO 1 (active)
#FULL_LOG_FILE = "Test Scenarios/CoG10Min.txt"
#CHARACTERS_BIOS_LOG_FILE = "Test Scenarios/bios.txt"

# TEST SCENARIO 2 (kept for quick swapping during testing)
#FULL_LOG_FILE = "Test Scenarios/all_events_complete.txt"
#CHARACTERS_BIOS_LOG_FILE = "Test Scenarios/bios.txt"

# TEST SCENARIO 3 (kept for quick swapping during testing)
FULL_LOG_FILE = "Test Scenarios/demo_all_events_complete.txt"
CHARACTERS_BIOS_LOG_FILE = "Test Scenarios/demo_all_events_charactersbios.txt"

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
    characters_bios_log = sys.stdin.readline().strip()

    if not full_log or not characters_bios_log:
        raise ValueError(
            "Expected two non-empty lines on stdin "
            "(full_log_file, characters_bios_log_file), "
            f"got: full={full_log!r}, "
            f"character_bios={characters_bios_log!r}"
        )
    return full_log, characters_bios_log


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


# -----------------------------------------------------------------------
# Demo fallback content
# -----------------------------------------------------------------------
# Shown instantly by the dashboard's "Show Backup Story" button, and by
# the standalone backup_story.html page (see build_backup_page.py) --
# with NO dependency on the LLM API, the game connection, or the log
# pipeline. Edit this before a demo/presentation so it's a real story
# from a real session, not placeholder text.
BACKUP_STORY_TITLE = "Blood in the Potato Rows"
BACKUP_STORY_BODY = (
    "The timber wolves circled the perimeter like ghosts, their shadows long across the potato rows where April worked from dawn to dusk, her hands steady despite the psychic static that always hummed at the edge of her perception. Oleg, seventy years of scars and cynicism, moved between the workshop and the treeline—hauling timber for a stool he'd sworn he'd finish, dropping hares and a turkey with the economy of a man who'd once made killing a trade. Stevenson drifted through it all like a separate weather system, packing a survival meal into his bag with the absent focus of someone drafting a story in his head, his psychopath's calm untouched by the colony's quiet rhythm."
    "\n\n"
    "Then the Toba Pact crested the ridge, and the rhythm broke. Oleg didn't hesitate—he'd been watching the treeline, the bolt-action rifle already shouldered. The first raider, Abexada, dropped with a shattered femur before he could raise his weapon, the shot clean as a sentence written in blood. April abandoned her sandstone and ran—not to fight, never to fight, but to Oleg's side, her herbalist's kit open before the dust settled. The wolves fled. The yaks lowed, indifferent. And somewhere in the chaos, Stevenson simply kept moving, a ghost in his own colony, already filing the moment away for later."
)
BACKUP_STORY_CAPTION = "[ Generated from 7337 structured logs derived from 5 minutes of gameplay ]"