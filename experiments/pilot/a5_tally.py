"""
Pilot A5 -- tally the blind comparison answers.

  python -m experiments.pilot.a5_tally

Reads experiments/pilot/a5_answers.csv (columns rater, pair, q1, q2; q1/q2 = A or B)
and the answer key, and counts, per question, how often each share condition was chosen.
Updates a5_result.json and writes a5_tally.md.
"""

import csv
from collections import Counter

from experiments.common import paths
from experiments.common.report import md_table, read_json, write_json
from experiments.pilot.a5_generation import ANSWERS_PATH, QUESTIONS


def run():
    key = read_json(paths.OUT_DIR / "a5_answer_key.json")
    if key is None:
        raise SystemExit("Run a5_generation first.")
    by_pair = {p["pair"]: p for p in key["pairs"]}
    tallies = {q: Counter() for q in ("q1", "q2")}
    head_to_head = {q: Counter() for q in ("q1", "q2")}
    n, bad = 0, []
    with open(ANSWERS_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                p = by_pair[int(row["pair"])]
            except (KeyError, ValueError):
                bad.append(row)
                continue
            n += 1
            for q in ("q1", "q2"):
                ans = (row.get(q) or "").strip().upper()
                if ans not in ("A", "B"):
                    continue
                win, lose = (p["A"], p["B"]) if ans == "A" else (p["B"], p["A"])
                tallies[q][win] += 1
                head_to_head[q][(win, lose)] += 1

    result = read_json(paths.OUT_DIR / "a5_result.json") or {"test": "A5"}
    result.update({"answers": n, "bad_rows": len(bad),
                   "wins": {q: {str(k): v for k, v in t.items()} for q, t in tallies.items()},
                   "status": "done" if n else "pending"})
    if n:
        result.pop("status_reason", None)
    write_json(paths.OUT_DIR / "a5_result.json", result)

    shares = sorted({p["A"] for p in key["pairs"]} | {p["B"] for p in key["pairs"]})
    L = ["# A5 — Blind comparison tally", "", f"{n} answers.", ""]
    for q, text in zip(("q1", "q2"), QUESTIONS):
        L += [f"## {text}", "", md_table(["share", "times chosen"], [[s, tallies[q][s]] for s in shares]), ""]
    (paths.OUT_DIR / "a5_tally.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    r = run()
    print(f"A5 tally: {r['answers']} answers")
