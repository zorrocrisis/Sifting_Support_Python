"""
Offline simulations of two ways the game could log dialogue so the CC (game: RC) can match it
more like an event log, while the player still sees the dialogue line.

1. Provenance (`dialogue_prov`): each dialogue line records the IDs of the session-1 logs it was
   generated from (experiments/pilot/dialogue_provenance.csv). The CC scores a dialogue line
   against a session-2 event through its sources: distance = the smallest distance from any of
   its source logs to the event. The pool still shows the dialogue line.

2. Speech frame stripped (`dialogue_stripped`): before computing text similarity, drop the
   "{Name} said '...'" wrapper and the opening vocative ("Stench, ..."), so NCD can't match on the
   name-heavy frame. No game change needed.
"""

import csv
import re

from experiments.common import paths

_SAID = re.compile(r"^.*? said '(.*)'$")


def strip_speech(desc, masker=None):
    """
    "Odette 'Odette' O'Neill said 'Stench, I watched the far treeline.'" -> "I watched the far treeline."
    Drops the speaker frame and a leading vocative naming a colonist (detected with the masker).
    """
    m = _SAID.match(desc.strip())
    text = m.group(1) if m else desc.strip()
    head, sep, rest = text.partition(", ")
    if sep and masker is not None and masker.colonists_in(head) and masker.mask(head).strip() in ("", *masker.tokens.values()):
        text = rest
    elif sep and masker is None and len(head.split()) <= 3:
        text = rest
    return text[:1].upper() + text[1:] if text else text


def read_provenance(path=None):
    """
    {dialogue_id: [source _ID_, ...]}, plus whether any row used the suggested (unconfirmed) sources.
    The author's `source_ids` column wins; when it is empty for a line, `suggested_source_ids` is used.
    """
    path = path or (paths.PILOT_DIR / "dialogue_provenance.csv")
    out, used_suggested = {}, []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            did = (row.get("dialogue_id") or "").strip()
            confirmed = (row.get("source_ids") or "").strip()
            cell = confirmed or (row.get("suggested_source_ids") or "").strip()
            if not confirmed and cell:
                used_suggested.append(did)
            ids = [x for x in re.split(r"[;/,\s]+", cell) if x]
            if did and ids:
                out[did] = ids
    return out, used_suggested


def source_lines(ids, search=None):
    """Full session-1 log lines for the given _ID_s (searched in the session-1 event logs)."""
    from experiments.common.data import dedup_key
    search = search or [paths.SCENARIOS / "SimulatedDay1" / "selected_reference_logs.txt",
                        paths.SESSION1_EVENTS]
    want, found = set(ids), {}
    for p in search:
        if not p.exists():
            continue
        with open(p, encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                k = dedup_key(line)
                if k in want and k not in found:
                    found[k] = line
        if len(found) == len(want):
            break
    return found
