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



def normalize_log(line: str) -> str:
    """
    Light normalization to avoid trivial differences between otherwise
    identical log lines (currently just whitespace trimming). Adjust
    here if you need more aggressive normalization later.
    """
    return line.strip()


def load_unique_logs(full_log_file, log_dict, max_lines=20000):
    """
    Load logs from `full_log_file`, normalize each line, and deduplicate by
    exact string match while preserving first-seen order.

    Returns
    -------
    unique_logs : list[str]
        Deduplicated log lines, in first-seen order.
    counts : OrderedDict[str, int]
        How many times each unique log line occurred.
    """
    counts = OrderedDict()
    visibility = OrderedDict()

    with open(full_log_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = normalize_log(line)
            if not line:
                continue

            # Extract visibility before the first "."
            vis = line.split(".", 1)[0]

            counts[log_dict[line]] = counts.get(log_dict[line], 0) + 1

            # Store visibility, upgrading to V if any occurrence is visible
            if log_dict[line] not in visibility.keys():
                visibility[log_dict[line]] = vis
            elif vis == "V":
                visibility[log_dict[line]] = "V"

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
    Build a mapping from short full content line -> short log line, assuming
    the two files have the same number of lines in the same order
    (line i in log_file_path corresponds to line i in content_file_path).
    """
    log_dict = {}

    with open(log_file_path, "r") as log_file, open(full_log_file_path, "r") as full_log_file:
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
    return log.startswith("V_")


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
    """
    matching_keys = [
        key for key, value in log_dict.items()
        if value == log
    ]

    if not matching_keys:
        return None

    return min(matching_keys, key=temporal_sort_key)


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