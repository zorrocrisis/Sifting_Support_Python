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
                  switched:bool = False,
                  compress_level: int = 9,
                  algo: str = "deflate") -> float:
    """
    Compute NCD between two strings
    using compression entirely in memory (no temporary files).
    """

    # Compress individually
    A_size = compress_with_algorithm(A, compress_factor=compress_level, algorithm=algo)
    B_size = compress_with_algorithm(B, compress_factor=compress_level, algorithm=algo)

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


def load_unique_logs(log_file, max_lines=50):
    """
    Load logs from `log_file`, normalize each line, and deduplicate by
    exact string match while preserving first-seen order.

    Returns
    -------
    unique_logs : list[str]
        Deduplicated log lines, in first-seen order.
    counts : OrderedDict[str, int]
        How many times each unique log line occurred.
    """
    counts = OrderedDict()

    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = normalize_log(line)
            if not line:
                continue

            counts[line] = counts.get(line, 0) + 1

            if len(counts) >= max_lines:
                break

    unique_logs = list(counts.keys())
    return unique_logs, counts


def load_character_bios(file):
    """Read the raw character bios file as a single string."""
    with open(file, "r", encoding="utf-8") as f:
        return f.read()


def log_dictionary_ids(log_file_path, content_file_path):
    """
    Build a mapping from short log line -> full content line, assuming
    the two files have the same number of lines in the same order
    (line i in log_file_path corresponds to line i in content_file_path).
    """
    log_dict = {}

    with open(log_file_path, "r") as log_file, open(content_file_path, "r") as content_file:
        log_lines = log_file.readlines()
        content_lines = content_file.readlines()

        for i, log in enumerate(log_lines):
            log_dict[log.strip()] = content_lines[i].strip()

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

    for i in range(n):
        for j in range(i + 1, n):
            d = NCD_text(strings[i], strings[j], algo="deflate")
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