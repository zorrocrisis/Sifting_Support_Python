"""
Prepare the hand-written gold file for pilot test A1.

  python -m experiments.pilot.make_gold_helper

- Creates experiments/pilot/gold_matches.csv with one row per past dialogue
  line and an empty expected_event_id (never overwrites an existing file).
- Writes experiments/pilot/out/gold_helper.md: every past dialogue line, then a
  numbered list of current-session event descriptions in chronological order.
  Put the E-codes (or any _ID_ from the log) of the events that continue a
  dialogue line into expected_event_id.

The helper deliberately shows no NCD or embedding scores, so the gold labels
aren't biased toward either method.
"""

import csv

from experiments.common import paths
from experiments.common.context import PilotContext
from experiments.common.gold import GOLD_COLUMNS

GOLD_PATH = paths.PILOT_DIR / "gold_matches.csv"


def main():
    paths.ensure_out()
    ctx = PilotContext()
    ev, dl = ctx.events, ctx.dialogue

    if GOLD_PATH.exists():
        print(f"{GOLD_PATH} already exists, left unchanged.")
    else:
        with open(GOLD_PATH, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=GOLD_COLUMNS)
            w.writeheader()
            for d, text in enumerate(dl.unique):
                w.writerow({"dialogue_id": ctx.dialogue_id(d), "expected_event_id": "",
                            "note": "", "dialogue_text": text})
        print(f"Wrote {GOLD_PATH}")

    lines = ["# Gold helper for pilot test A1", "",
             f"Session events: `{paths.SESSION2_EVENTS.relative_to(paths.REPO_ROOT)}` "
             f"({len(ev)} distinct descriptions, dialogue lines excluded).",
             f"Past dialogue: `{paths.PAST_DIALOGUE.relative_to(paths.REPO_ROOT)}` ({len(dl)} lines).", "",
             "For each dialogue line, write the codes of the events that continue it into "
             "`experiments/pilot/gold_matches.csv` (`expected_event_id`, `;`-separated, or one row each). "
             "Leave it empty if nothing in this session relates to the line.", "",
             "## Past dialogue", "", "| dialogue_id | tick | line |", "|---|---|---|"]
    for d, text in enumerate(dl.unique):
        lines.append(f"| {ctx.dialogue_id(d)} | {dl.timestamp(text):.0f} | {text} |")

    lines += ["", "## Current-session events (chronological)", "",
              "| code | first tick | first _ID_ | count | vis | description |", "|---|---|---|---|---|---|"]
    order = sorted(range(len(ev)), key=lambda e: (ev.timestamp(ev.unique[e]), e))
    for e in order:
        desc = ev.unique[e]
        lines.append(f"| {ctx.event_code(e)} | {ev.timestamp(desc):.0f} | {ev.id_of(desc)} | "
                     f"{ev.counts[desc]} | {ev.visibility[desc]} | {desc.replace('|', '/')} |")

    out = paths.OUT_DIR / "gold_helper.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
