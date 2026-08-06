"""
ncd_data.py
-----------
Loading raw log files, deduplicating them by exact string match, and
computing pairwise Normalized Compression Distance (NCD) between log
lines. This is the data layer the clustering/visualization code builds
on top of.
"""

import re
from collections import OrderedDict
import numpy as np
from compression_algorithms import compress_with_algorithm

def NCD_text(A: str,
                  B: str,
                  A_size: int,
                  B_size: int,
                  switched:bool = False,
                  compress_level: int = 9,
                  algo: str = "deflate") -> float:
    """
    Compute NCD between two strings
    using compression entirely in memory (no temporary files).
    """

    # No need to compress individually

    # Compress concatenation
    if(switched):
      A_n_B_size = compress_with_algorithm(B + A, compress_factor=compress_level, algorithm=algo)
    else:
      A_n_B_size = compress_with_algorithm(A + B, compress_factor=compress_level, algorithm=algo)

    # Compute NCD
    return (A_n_B_size - min(A_size,B_size)) / max(A_size, B_size)


def extract_descriptions(full_log_file):
    """
    Extract the short/description text from a full-length log line,
    e.g. "...FullInfo_This is the description text" -> "This is the
    description text". Returns None if no FullInfo_ tag is present.
    """
    short_log_file = full_log_file.replace(".txt", "_descriptionsonly.txt")

    with open(full_log_file, "r", encoding="utf-8", errors="ignore") as f, \
            open (short_log_file, "w", encoding="utf-8", errors="ignore") as out:
        for line in f:
            if not line:
                continue

            match = re.search(r"FullInfo_\s*(.*)", line)

            if match:
                out.write(match.group(1) + "\n")
    return short_log_file


def normalize_log(line: str) -> str:
    """
    Light normalization to avoid trivial differences between otherwise
    identical log lines (currently just whitespace trimming). Adjust
    here if you need more aggressive normalization later.
    """
    return line.strip()


def load_unique_logs(full_log_file, log_dict, max_lines=20000):
    """
    Load logs from `full_log_file` (the raw, full-length log lines --
    each one containing a Timestamp_..._ tag and, per check_if_visible,
    a "V_"/other prefix), translate each one to its short/description
    text via `log_dict` (full_log -> short_log, see log_dictionary_ids),
    and deduplicate by that short text while preserving first-seen order.

    Also aggregates a `visibility` tag per short log: "V" if ANY
    occurrence of that short log was witnessed by the player, "NV"
    otherwise (upgrading to "V" as soon as one visible occurrence is seen).

    Returns
    -------
    unique_logs : list[str]
        Deduplicated SHORT log lines, in first-seen order.
    counts : OrderedDict[str, int]
        How many times each unique (short) log line occurred.
    visibility : OrderedDict[str, str]
        "V" or "NV" per unique (short) log line.
    """
    counts = OrderedDict()
    visibility = OrderedDict()

    with open(full_log_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = normalize_log(line)
            if not line:
                continue

            vis = "V" if check_if_visible(line) else "NV"

            short_log = log_dict[line]

            counts[short_log] = counts.get(short_log, 0) + 1

            # Store visibility, upgrading to V if any occurrence is visible.
            if short_log not in visibility:
                visibility[short_log] = vis
            elif vis == "V":
                visibility[short_log] = "V"

            if len(counts) >= max_lines:
                break

    unique_logs = list(counts.keys())
    return unique_logs, counts, visibility


def load_character_bios(file):
    """Read the raw character bios file as a single string."""
    with open(file, "r", encoding="utf-8") as f:
        return f.read()


def log_dictionary_ids(log_file_path, full_log_file_path):
    """
    Build a mapping from full-length log line -> short/description log
    line: log_dict[full_log_lines[i]] = log_lines[i]. Since many full
    log lines can share the same short description (they differ only
    by timestamp/details), this is a many-to-one mapping -- multiple
    keys can map to the same value. Assumes the two files have the same
    number of lines in the same order (line i in log_file_path
    corresponds to line i in full_log_file_path).

    NOTE: opened with the SAME encoding/error-handling as
    load_unique_logs() (utf-8, errors="ignore"). This matters more than
    it used to: since load_unique_logs() looks up log_dict by the exact
    full-log line text it reads from disk, any decoding difference
    between the two reads (e.g. one function using the platform default
    encoding, the other utf-8) could produce two different Python
    strings for what's really the same line -- causing a KeyError on
    any line with a non-ASCII character. Keep these two functions'
    open() calls in sync if either one changes.
    """
    log_dict = {}

    with open(log_file_path, "r", encoding="utf-8", errors="ignore") as log_file, \
            open(full_log_file_path, "r", encoding="utf-8", errors="ignore") as full_log_file:
        log_lines = log_file.readlines()
        full_log_lines = full_log_file.readlines()

        for i, log in enumerate(full_log_lines):
            log_dict[log.strip()] = log_lines[i].strip()

    return log_dict


def compute_ncd_distance_matrix(strings):
    """
    Compute the full pairwise NCD distance matrix for a list of strings.

    Returns
    -------
    np.ndarray, shape (n, n)
        Symmetric matrix with zero diagonal; dist_matrix[i, j] is the
        NCD between strings[i] and strings[j].
    """
    n = len(strings)
    dist_matrix = np.zeros((n, n))

    compressed_sizes = [0] * n

    # Calculate all the compressed sizes first
    for i in range(n):
        compressed_sizes[i] = compress_with_algorithm(strings[i], algorithm="deflate")

    # Compute NCD for each pair
    for i in range(n):
        for j in range(i + 1, n):
            d = NCD_text(
                strings[i],
                strings[j],
                compressed_sizes[i],
                compressed_sizes[j]
            )

            dist_matrix[i, j] = d
            dist_matrix[j, i] = d

    return dist_matrix


# -----------------------------------------------------------------------
# Log tag helpers
# -----------------------------------------------------------------------
def check_if_visible(log):
    """Whether a raw (long-form) log line represents a player-visible event."""
    return log.startswith("V._")


def extract_timestamp(long_log):
    """
    Extract the raw tick/timestamp string embedded in a full-length log
    line, e.g. "...Timestamp_1043216_..." -> "1043216".
    Returns None if no timestamp tag is present.
    """
    match = re.search(r"Timestamp_(.+?)_", long_log)
    return match.group(1) if match else None


def temporal_sort_key(long_log):
    """
    Numeric sort key derived from extract_timestamp(), for ordering log
    entries chronologically (e.g. the Final Log Pool, before it's shown
    or sent to the story LLM). Falls back to +inf -- i.e. sorts last --
    if the log has no timestamp tag, or the tag isn't numeric.
    """

    raw = extract_timestamp(long_log)
    if raw is None:
        return float("inf")
    try:
        return float(raw)
    except ValueError:
        return float("inf")

def earliest_key_for_log(log, log_dict):
    """
    Find all keys in log_dict whose value equals `log` and return
    the key with the earliest timestamp.

    If no matching key has a valid numeric timestamp, the first
    matching key is returned.

    COST WARNING: this scans the entire log_dict (all full-log lines)
    on every call -- O(len(log_dict)). Fine for a one-off lookup, but
    calling it once per unique log (as pipeline.py used to) makes the
    whole pass O(len(log_dict) * len(unique_logs)), which can get slow
    for a real game session. If you need this for EVERY unique log,
    use build_earliest_full_log_index() instead -- it computes the same
    result for all logs in one O(len(log_dict)) pass.
    """
    matching_keys = [
        key for key, value in log_dict.items()
        if value == log
    ]

    if not matching_keys:
        return None

    return min(matching_keys, key=temporal_sort_key)


def build_earliest_full_log_index(log_dict):
    """
    Bulk version of calling earliest_key_for_log() once per unique short
    log: groups log_dict (full_log -> short_log) by short log in a
    single O(len(log_dict)) pass, keeping the chronologically-earliest
    full log line seen for each short log -- instead of re-scanning the
    whole log_dict from scratch for every unique log.

    Returns
    -------
    dict[str, str]
        short_log -> the earliest full_log line that maps to it. Useful
        both for chronological sorting (feed each value through
        temporal_sort_key) and for display (each value is a real,
        representative full-length log line for that short log).
    """
    earliest = {}
    for full_log, short_log in log_dict.items():
        if short_log not in earliest or temporal_sort_key(full_log) < temporal_sort_key(earliest[short_log]):
            earliest[short_log] = full_log
    return earliest


def add_tags(short_log, long_log, add_visibility_tag=False, add_timestamp_tag=False):
    """
    Optionally prefix `short_log` with a timestamp and/or suffix it with
    a [V]/[NV] visibility tag, both derived from the corresponding
    `long_log` line.

    Not currently wired into the dashboard, but kept since it's small,
    self-contained, and useful if you want to annotate labels with
    visibility/timestamp tags later.
    """
    temp_log = short_log

    if add_timestamp_tag:
        timestamp = extract_timestamp(long_log)
        if timestamp:
            temp_log = f"[{timestamp}] " + temp_log

    if add_visibility_tag:
        temp_log = temp_log + (" [V]" if check_if_visible(long_log) else " [NV]")

    return temp_log