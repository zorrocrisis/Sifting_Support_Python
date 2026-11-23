"""
Loading session logs, past dialogue and character bios for experiments.

Log reading goes through the existing ncd_data readers (extract_descriptions,
log_dictionary_ids, load_unique_logs, build_earliest_full_log_index), so the
unique logs, counts, visibility and short->full mapping are exactly what the
game's Python side sees. extract_descriptions() writes a *_descriptionsonly.txt
file next to its input, so every log is first copied ("staged") into
experiments/pilot/out/cache/ and read from there; the corpus folders are never
written to.
"""

import hashlib
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from experiments.common import paths  # noqa: F401  (puts the repo root on sys.path)
from ncd_data import (build_earliest_full_log_index, extract_descriptions,
                      load_unique_logs, log_dictionary_ids, temporal_sort_key)

# ---------------------------------------------------------------------------
# Log line parsing
# ---------------------------------------------------------------------------
# {V._|NV._}{TAG}_Timestamp_{tick}_Location_({x}, {y}, {z})_ID_{id}_Actors_{names}_FullInfo_{description}
LINE_RE = re.compile(
    r"^(?P<vis>N?V)\._(?P<tag>[A-Z]+)_Timestamp_(?P<ts>\d+)_Location_(?P<loc>\(.*?\))"
    r"_ID_(?P<id>[^_]+)_Actors_(?P<actors>.*?)_FullInfo_(?P<desc>.*)$"
)
# Same dedup key the C# merge uses: SiftingChannelsUtils.IdRegex
ID_RE = re.compile(r"_ID_(?P<id>[^_]+)_")


def parse_line(full_line):
    """Split a full log line into its fields. Returns None if it doesn't match the format."""
    m = LINE_RE.match(full_line.strip())
    if not m:
        return None
    d = m.groupdict()
    d["ts"] = int(d["ts"])
    d["actors"] = [a.strip() for a in d["actors"].split(",") if a.strip()]
    return d


def dedup_key(full_line):
    """C# FinalPoolComposer / SiftingChannelsUtils.GetDedupKey: the _ID_ value, or the whole line."""
    m = ID_RE.search(full_line)
    return m.group("id") if m else full_line


def description_of(full_line):
    """Text after FullInfo_ (same regex as ncd_data.extract_descriptions)."""
    m = re.search(r"FullInfo_\s*(.*)", full_line)
    return m.group(1).strip() if m else full_line.strip()


# ---------------------------------------------------------------------------
# Dialogue detection -- the one place to change when a DLG_ tag exists.
# ---------------------------------------------------------------------------
_DIALOGUE_DESC_RE = re.compile(r"^.+ said '.*'$")


def is_dialogue(full_line):
    """A dialogue line is an SL_ line whose description reads "{name} said '{line}'"."""
    parsed = parse_line(full_line)
    if parsed is None:
        return False
    return parsed["tag"] == "SL" and bool(_DIALOGUE_DESC_RE.match(parsed["desc"]))


# ---------------------------------------------------------------------------
# Staging (read-only corpus -> writable cache copy)
# ---------------------------------------------------------------------------
def stage_log(src, name=None, keep=None):
    """
    Copy `src` into the cache folder and return the copy's path. `keep` is an
    optional predicate on each (stripped, non-empty) line; lines it rejects are
    dropped from the copy. The copy's name includes a hash of the source path
    and filter so different inputs never collide.
    """
    src = Path(src)
    paths.ensure_out()
    tag = hashlib.sha1(f"{src.resolve()}|{getattr(keep, '__name__', None)}".encode()).hexdigest()[:8]
    dst_dir = paths.CACHE_DIR / f"{name or src.parent.name}_{tag}"
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name

    if keep is None:
        shutil.copyfile(src, dst)
    else:
        with open(src, "r", encoding="utf-8", errors="ignore") as f, \
                open(dst, "w", encoding="utf-8", errors="ignore") as out:
            for line in f:
                s = line.strip()
                if s and keep(s):
                    out.write(s + "\n")
    return dst


def not_dialogue(line):
    return not is_dialogue(line)


def only_dialogue(line):
    return is_dialogue(line)


# ---------------------------------------------------------------------------
# Log sets
# ---------------------------------------------------------------------------
@dataclass
class LogSet:
    """Unique (description-level) logs of one file, as the existing pipeline sees them."""
    path: Path                      # staged copy that was read
    unique: list                    # unique descriptions, first-seen order
    counts: dict                    # description -> occurrences
    visibility: dict                # description -> "V" | "NV"
    short_to_full: dict             # description -> earliest full line
    log_dict: dict = field(repr=False, default_factory=dict)   # full line -> description

    def __len__(self):
        return len(self.unique)

    @property
    def full(self):
        return [self.short_to_full[u] for u in self.unique]

    def timestamp(self, desc):
        return temporal_sort_key(self.short_to_full[desc])

    def id_of(self, desc):
        return dedup_key(self.short_to_full[desc])

    def ids_to_desc(self):
        """Every _ID_ that occurs in the file -> its description (for resolving gold IDs)."""
        return {dedup_key(full): short for full, short in self.log_dict.items()}

    def label(self, desc):
        """Pool formatting used for the LLM: description[xN][V/NV]."""
        return f"{desc}[x{self.counts[desc]}][{self.visibility[desc]}]"


def load_logset(src, name=None, keep=None):
    """Stage `src` (optionally filtered) and load it with the existing ncd_data readers."""
    staged = stage_log(src, name=name, keep=keep)
    short_path = extract_descriptions(str(staged))
    log_dict = log_dictionary_ids(short_path, str(staged))
    unique, counts, visibility = load_unique_logs(str(staged), log_dict, max_lines=10**9)
    short_to_full = build_earliest_full_log_index(log_dict)
    return LogSet(Path(staged), unique, dict(counts), dict(visibility), short_to_full, log_dict)


def load_session_events(src=None, name="session2"):
    """Current-session events, dialogue lines excluded (AC and CC candidates)."""
    return load_logset(src or paths.SESSION2_EVENTS, name=name, keep=not_dialogue)


def load_past_dialogue(src=None, name="dialogue"):
    """Dialogue spoken in earlier sessions (only lines that pass is_dialogue)."""
    return load_logset(src or paths.PAST_DIALOGUE, name=name, keep=only_dialogue)


def load_reference(src=None, kind=None, name=None):
    """
    The CC reference set. kind "dialogue": past dialogue lines only; kind "events":
    earlier-session event logs (dialogue lines dropped).
    """
    kind = kind or paths.REFERENCE_KIND
    src = src or paths.REFERENCE_PATH
    if kind == "dialogue":
        return load_past_dialogue(src, name=name or "dialogue")
    if kind == "events":
        return load_logset(src, name=name or "reference_events", keep=not_dialogue)
    raise ValueError(f"unknown reference kind {kind!r}")


# ---------------------------------------------------------------------------
# Character bios
# ---------------------------------------------------------------------------
_NICK_RE = re.compile(r"^(?P<first>\S+)\s+'(?P<nick>[^']+)'\s+(?P<last>.+)$")


@dataclass
class Colonist:
    full_name: str        # as written in the bios, e.g. "Lidia 'Stench' Schmitt" or "Dillon Boyd"
    first: str
    last: str
    nick: str | None      # the quoted part, if the bios give one


def load_bios_text(src=None):
    with open(src or paths.BIOS, "r", encoding="utf-8") as f:
        return f.read()


def parse_colonists(bios_text):
    """Colonists listed in a character_bios.txt ("Name: ..." lines)."""
    colonists = []
    for line in bios_text.splitlines():
        if not line.startswith("Name:"):
            continue
        full = line[len("Name:"):].strip()
        m = _NICK_RE.match(full)
        if m:
            colonists.append(Colonist(full, m["first"], m["last"].strip(), m["nick"]))
        else:
            parts = full.split()
            colonists.append(Colonist(full, parts[0], parts[-1] if len(parts) > 1 else parts[0], None))
    return colonists
