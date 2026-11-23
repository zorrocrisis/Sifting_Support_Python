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
EVENT_CODES = PILOT_DIR / "event_codes.csv"   # frozen code -> description map (see context.code_map)
CACHE_DIR = PILOT_DIR / "out" / "cache"        # shared by every reference set

# ---------------------------------------------------------------------------
# Reference sets: what the CC (game: RC, "reference channel") matches session-2 events against.
# Pick one with the PILOT_REFERENCE environment variable or use_reference(); each has its own
# gold file and output folder, so results for different references never overwrite each other.
# ---------------------------------------------------------------------------
REFERENCES = {
    # Dialogue spoken in session 1 (the original pilot).
    "dialogue": {"path": PAST_DIALOGUE, "kind": "dialogue",
                 "gold": PILOT_DIR / "gold_matches.csv", "out": PILOT_DIR / "out"},
    # The 13 logs the AC selected in session 1 (SimulatedDay1/sifted_full_logs.txt without the
    # [xN][V] suffixes, so every reference line has count 1).
    "s1_selected": {"path": SCENARIOS / "SimulatedDay1" / "selected_reference_logs.txt", "kind": "events",
                    "gold": PILOT_DIR / "gold_matches_s1_selected.csv", "out": PILOT_DIR / "out_s1_selected"},
    # Dialogue logging simulations (see experiments/common/dialogue_logging.py). Both show and pool the
    # dialogue lines and reuse the dialogue gold; only how the CC scores a dialogue line changes.
    "dialogue_stripped": {"path": PAST_DIALOGUE, "kind": "dialogue", "transform": "strip_speech",
                          "gold": PILOT_DIR / "gold_matches.csv", "out": PILOT_DIR / "out_dialogue_stripped"},
    "dialogue_prov": {"path": PAST_DIALOGUE, "kind": "dialogue", "provenance": PILOT_DIR / "dialogue_provenance.csv",
                      "gold": PILOT_DIR / "gold_matches.csv", "out": PILOT_DIR / "out_dialogue_prov"},
}


# Which session-2 events the CC may pick ("candidates"):
#   "all"      -- every distinct session-2 event (the game's current behaviour)
#   "filtered" -- only the AC's cluster representatives at NCD threshold CC_FILTER_THRESHOLD,
#                 i.e. unique_logs_after_filtering before dendrogram traversal
CC_CANDIDATE_MODES = ("all", "filtered")
CC_FILTER_THRESHOLD = 0.5

# How the CC scores a reference line against a session-2 event:
#   "ncd"   -- NCD on the descriptions (the game's current behaviour)
#   "index" -- event-indexing similarity: entities, place, log type and NCD text (see event_index.py)
CC_SIMILARITY_MODES = ("ncd", "index", "embed")   # "embed": 1 - cosine of sentence embeddings (comparison only)
SESSION1_EVENTS = SCENARIOS / "SimulatedDay1" / "formatted_event_logs.txt"   # entity vocabulary for "index"


def use_reference(name, cc_candidates="all", cc_similarity="ncd"):
    """
    Switch every pilot script to reference set `name` (see REFERENCES), CC candidate mode and
    CC similarity. Results go to the reference's output folder, with "_filtered" appended when the
    CC candidates are filtered and "_index" when the CC uses event indexing; gold files are shared.
    """
    global REFERENCE, REFERENCE_PATH, REFERENCE_KIND, GOLD_PATH, OUT_DIR, CC_CANDIDATES, CC_SIMILARITY
    if name not in REFERENCES:
        raise ValueError(f"unknown reference {name!r}; choose from {sorted(REFERENCES)}")
    if cc_candidates not in CC_CANDIDATE_MODES:
        raise ValueError(f"unknown CC candidate mode {cc_candidates!r}; choose from {CC_CANDIDATE_MODES}")
    if cc_similarity not in CC_SIMILARITY_MODES:
        raise ValueError(f"unknown CC similarity {cc_similarity!r}; choose from {CC_SIMILARITY_MODES}")
    r = REFERENCES[name]
    global REFERENCE_SPEC
    REFERENCE_SPEC = r
    REFERENCE, REFERENCE_PATH, REFERENCE_KIND = name, r["path"], r["kind"]
    CC_CANDIDATES, CC_SIMILARITY = cc_candidates, cc_similarity
    GOLD_PATH = r["gold"]
    suffix = ("_filtered" if cc_candidates == "filtered" else "") + ({"index": "_index", "embed": "_embed"}.get(cc_similarity, ""))
    OUT_DIR = r["out"].with_name(r["out"].name + suffix)


import os  # noqa: E402
use_reference(os.environ.get("PILOT_REFERENCE", "dialogue"), os.environ.get("PILOT_CC_CANDIDATES", "all"),
              os.environ.get("PILOT_CC_SIMILARITY", "ncd"))


def ensure_out():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return OUT_DIR
