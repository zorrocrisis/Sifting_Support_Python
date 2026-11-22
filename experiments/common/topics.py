"""
Author topic tags (topic_tags.csv: description, topic, n_pools).

Topics are written by the author, never filled in automatically.
write_topic_template() adds new descriptions with an empty topic and keeps
every topic already filled in.
"""

import csv

TOPICS = ("raid", "fight", "hunting", "hauling", "mental_break", "health", "social", "animals", "visitor", "other",
          "refugee", "farming", "building")   # added by the author while tagging the pilot
COLUMNS = ["description", "topic", "n_pools"]


def split_topics(t):
    """A tag may hold several topics, e.g. "hunting/fight/raid"; the first is the primary one."""
    return [x.strip() for x in (t or "").replace(";", "/").split("/") if x.strip()]


def read_topics(path):
    """{description: topic} for rows with a topic; plus a list of unknown topic labels."""
    tags, unknown = {}, []
    if not path.exists():
        return tags, unknown
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            t = (row.get("topic") or "").strip()
            if not t:
                continue
            unknown += [x for x in split_topics(t) if x not in TOPICS]
            tags[row["description"]] = t
    return tags, sorted(set(unknown))


def write_topic_template(path, description_counts, missing_path):
    """
    Create `path` ({description: n_pools} with empty topics) if it doesn't exist yet.
    Once it exists it is the author's file and is never rewritten: pooled descriptions
    that have no topic there are listed in `missing_path` instead (removed when none are missing).
    Returns the number of pooled descriptions without a topic.
    """
    def dump(p, rows):
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)

    rows = sorted(({"description": d, "topic": "", "n_pools": n} for d, n in description_counts.items()),
                  key=lambda r: (-r["n_pools"], r["description"]))
    if not path.exists():
        dump(path, rows)
        return len(rows)
    tags, _ = read_all_topics(path, missing_path)
    if missing_path.exists() and any(read_topics(missing_path)[0]):
        # The author has tagged rows in the missing file: never rewrite or delete it.
        return sum(1 for r in rows if r["description"] not in tags)
    missing = [r for r in rows if r["description"] not in tags]
    if missing:
        dump(missing_path, missing)
    elif missing_path.exists():
        missing_path.unlink()
    return len(missing)


def read_all_topics(path, missing_path):
    """
    Tags from the author's file plus any filled in in a missing file: this run's and every
    other run folder's (pilot/out*/topic_tags_missing.csv), since descriptions are shared
    between runs. The main file wins over missing files; this run's missing file wins over others.
    """
    tags, unknown = {}, set()
    others = sorted(p for p in path.parent.glob("out*/topic_tags_missing.csv") if p != missing_path)
    for p in others + [missing_path, path]:
        t, u = read_topics(p)
        tags.update(t)
        unknown |= set(u)
    return tags, sorted(unknown)
