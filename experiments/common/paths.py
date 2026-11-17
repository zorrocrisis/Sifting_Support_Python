"""
Where the experiment inputs live, and where outputs go.

Input folders are read-only: nothing in experiments/ writes next to the
session logs. Code that needs a writable copy of a log (the existing
pipeline writes a *_descriptionsonly.txt file beside its input) stages
one under OUT_DIR / "cache" first, see data.stage_log().
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The existing pipeline modules (ncd_data, pipeline, log_selection, ...)
# live at the repo root. Make them importable however the experiment is run.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SCENARIOS = REPO_ROOT / "Test Scenarios" / "SiftingChannels"

# Pilot corpus: one colony, two sessions.
#   Session 1 -> SimulatedDay1/ ; its spoken dialogue is dialogue_logs.txt.
#   Session 2 (the "current" session) -> SimulatedDay2/.
SESSION2_DIR = SCENARIOS / "SimulatedDay2"
SESSION2_EVENTS = SESSION2_DIR / "formatted_event_logs.txt"
PAST_DIALOGUE = SESSION2_DIR / "dialogue_logs.txt"   # identical to 8_11_2026/dialogue_logs.txt
BIOS = SESSION2_DIR / "character_bios.txt"

# Saved Nov 8 runs from the game. READ ONLY -- never write here.
NOV8_DIR = SCENARIOS / "8_11_2026"

EXPERIMENTS_DIR = REPO_ROOT / "experiments"
PILOT_DIR = EXPERIMENTS_DIR / "pilot"
OUT_DIR = PILOT_DIR / "out"
EVENT_CODES = PILOT_DIR / "event_codes.csv"   # frozen code -> description map (see context.code_map)
CACHE_DIR = OUT_DIR / "cache"


def ensure_out():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return OUT_DIR
