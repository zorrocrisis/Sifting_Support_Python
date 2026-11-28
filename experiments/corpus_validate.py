"""
Check the session corpus against the recording protocol (corpus/README.md). Read-only.

  python -m experiments.corpus_validate [--root corpus] [--strict]

Errors (exit code 1): missing required files, empty logs, unparseable formatted logs, sessions
numbered with gaps. Warnings: leftover template placeholders, color tags or meta lines in the
formatted log, dialogue lines inside the event log, sessions overlapping in time, colonists changing
between sessions. --strict turns warnings into errors.
"""

import argparse
import re
import sys
from pathlib import Path

from experiments.common import paths
from experiments.common.data import is_dialogue, parse_colonists, parse_line

REQUIRED_SESSION_FILES = ("session_plan.md", "event_logs.txt", "formatted_event_logs.txt", "character_bios.txt",
                          "notes.md")
PLACEHOLDER = re.compile(r"<[a-z_ /.,'-]+>|<\.\.\.>", re.IGNORECASE)
SESSION_DIR = re.compile(r"^s(\d+)$")


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def error(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")


def read_lines(p):
    with open(p, encoding="utf-8", errors="ignore") as f:
        return [l.rstrip("\r\n") for l in f if l.strip()]


def placeholders(p):
    return sorted(set(PLACEHOLDER.findall(p.read_text(encoding="utf-8", errors="ignore"))))


def check_session(sdir, rep):
    where = f"{sdir.parent.name}/{sdir.name}"
    info = {"session": where}
    for f in REQUIRED_SESSION_FILES:
        if not (sdir / f).exists():
            rep.error(where, f"missing {f}")
    for f in ("session_plan.md", "notes.md"):
        if (sdir / f).exists() and placeholders(sdir / f):
            rep.warn(where, f"{f} still has template placeholders: {', '.join(placeholders(sdir / f)[:4])}")

    raw_p, fmt_p, bios_p = sdir / "event_logs.txt", sdir / "formatted_event_logs.txt", sdir / "character_bios.txt"
    if fmt_p.exists():
        fmt = read_lines(fmt_p)
        if not fmt:
            rep.error(where, "formatted_event_logs.txt is empty")
        else:
            parsed = [parse_line(l) for l in fmt]
            bad = sum(p is None for p in parsed)
            if bad / len(fmt) > 0.01:
                rep.error(where, f"{bad} of {len(fmt)} formatted lines don't match the log format")
            elif bad:
                rep.warn(where, f"{bad} formatted line(s) don't match the log format")
            if any("<color" in l for l in fmt):
                rep.warn(where, "formatted log still contains <color> tags (was it written by F9?)")
            if any("[IGN_P]" in l for l in fmt):
                rep.warn(where, "formatted log contains [IGN_P] meta lines")
            n_dlg = sum(is_dialogue(l) for l in fmt)
            if n_dlg:
                rep.warn(where, f"{n_dlg} dialogue line(s) inside the event log; dialogue is generated offline")
            ts = [p["ts"] for p in parsed if p]
            descs = {p["desc"] for p in parsed if p}
            info.update(lines=len(fmt), unique=len(descs), ts_min=min(ts) if ts else None, ts_max=max(ts) if ts else None)
    if raw_p.exists():
        raw = read_lines(raw_p)
        if not raw:
            rep.error(where, "event_logs.txt is empty")
        elif fmt_p.exists() and len(raw) < info.get("lines", 0):
            rep.warn(where, "raw log has fewer lines than the formatted log (copied from different folders?)")
    if bios_p.exists():
        colonists = parse_colonists(bios_p.read_text(encoding="utf-8", errors="ignore"))
        if not colonists:
            rep.error(where, "character_bios.txt lists no colonists (no 'Name:' lines)")
        info["colonists"] = sorted(c.full_name for c in colonists)
    return info


def check_colony(cdir, rep):
    where = cdir.name
    if not (cdir / "colony.md").exists():
        rep.error(where, "missing colony.md")
    elif placeholders(cdir / "colony.md"):
        rep.warn(where, f"colony.md still has template placeholders: {', '.join(placeholders(cdir / 'colony.md')[:4])}")
    sessions = sorted((int(m.group(1)), d) for d in cdir.iterdir() if d.is_dir() and (m := SESSION_DIR.match(d.name)))
    if not sessions:
        rep.error(where, "no session folders (s1, s2, ...)")
        return []
    numbers = [n for n, _ in sessions]
    if numbers != list(range(1, len(numbers) + 1)):
        rep.error(where, f"sessions should be s1..s{len(numbers)} without gaps, found {['s%d' % n for n in numbers]}")
    infos = [check_session(d, rep) for _, d in sessions]
    for a, b in zip(infos, infos[1:]):
        if a.get("ts_max") is not None and b.get("ts_min") is not None and b["ts_min"] < a["ts_max"]:
            rep.warn(b["session"], f"starts at tick {b['ts_min']}, before {a['session']} ends ({a['ts_max']}); "
                                   "overlapping logs, or a reload?")
        if a.get("colonists") and b.get("colonists") and a["colonists"] != b["colonists"]:
            gone = sorted(set(a["colonists"]) - set(b["colonists"]))
            new = sorted(set(b["colonists"]) - set(a["colonists"]))
            rep.warn(b["session"], f"colonists changed since {a['session']}"
                                   + (f"; left: {', '.join(gone)}" if gone else "")
                                   + (f"; joined: {', '.join(new)}" if new else ""))
    return infos


def run(root, strict=False):
    rep = Report()
    root = Path(root)
    for f in ("README.md", "CONTINUITY.md"):
        if not (root / f).exists():
            rep.error("corpus", f"missing {f}")
    if (root / "CONTINUITY.md").exists() and "Status: DRAFT" in (root / "CONTINUITY.md").read_text(encoding="utf-8"):
        rep.warn("corpus", "CONTINUITY.md is still marked DRAFT")
    colonies = sorted(d for d in root.iterdir() if d.is_dir() and not d.name.startswith(("_", ".")))
    if not colonies:
        rep.warn("corpus", "no colonies yet")
    table = []
    for c in colonies:
        table += check_colony(c, rep)
    return rep, table


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(paths.REPO_ROOT / "corpus"))
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    a = ap.parse_args()
    rep, table = run(a.root, a.strict)

    if table:
        print(f"{'session':24s} {'lines':>7s} {'unique':>7s} {'ticks':>21s}  colonists")
        for t in table:
            ticks = f"{t.get('ts_min', '?')}-{t.get('ts_max', '?')}"
            print(f"{t['session']:24s} {t.get('lines', '-'):>7} {t.get('unique', '-'):>7} {ticks:>21s}  "
                  f"{len(t.get('colonists', []))}")
        print()
    for w in rep.warnings:
        print(f"WARNING  {w}")
    for e in rep.errors:
        print(f"ERROR    {e}")
    n_colonies = len({t['session'].split('/')[0] for t in table})
    print(f"\n{n_colonies} colonies, {len(table)} sessions: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    sys.exit(1 if rep.errors or (a.strict and rep.warnings) else 0)


if __name__ == "__main__":
    main()
