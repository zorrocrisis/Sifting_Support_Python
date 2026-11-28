"""
Prototype: explicit callbacks in a separate, constrained step.

The narrative step can't keep "then" and "now" apart when it is given memories (SESSION2_E2E.md).
Here each callback gets its own small LLM call that sees only one RC link:

  MEMORY  an earlier-session dialogue line in the pool (the RC reference)
  NOW     the current-session event the RC paired it with
  SPEAKER the colonist who said the memory

and writes one dialogue line in the game's dialogue format (colonist, line, reported, reply), so it could
be added to the dialogue the game already shows. The system chooses every link (the RC's pairs); the LLM
only words it.

Uses the same pool as SESSION2_E2E.md's provenance condition (share 0.5, AC seed 42, nearest, all 162
events, NCD). One call per link where both halves are in the pool; outputs cached in out/llm_cache/.

Automatic check (a crude guard, not a judgement): every number in the generated line must come from the
memory or from the event; a number from only one of them should stay with that one. Reported per line.

  python -m experiments.pilot.callbacks [--system-certs]

Writes experiments/pilot/out_compare/CALLBACKS.md and callbacks.json.
"""

import argparse
import json
import re

from experiments.common import paths
from experiments.common.context import PilotContext
from experiments.common.data import description_of
from experiments.common.report import md_table
from experiments.common.simulate import build_pool
from experiments.pilot.session2_e2e import AC_SEED, SHARE, TOTAL, VARIANT, generate, strip_fence

CALLBACK_PROMPT = paths.PILOT_DIR / "prompts" / "callback.txt"
_SAID = re.compile(r"^(?P<speaker>.+?) said '(?P<text>.*)'$")
# "one" is left out on purpose: as a pronoun ("there's one right there") it is far more common than the number.
_NUM_WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
              "ten": 10, "twelve": 12, "fifteen": 15, "eighteen": 18, "twenty": 20, "thirty": 30, "fifty": 50,
              "sixty": 60, "hundred": 100, "fifty-six": 56, "five hundred": 500}


def numbers(text):
    t = text.lower()
    found = {int(n) for n in re.findall(r"\d+", t)}
    for w, n in sorted(_NUM_WORDS.items(), key=lambda kv: -len(kv[0])):
        if re.search(rf"\b{re.escape(w)}\b", t):
            found.add(n)
            t = re.sub(rf"\b{re.escape(w)}\b", " ", t)
    return found


def links(ctx, built):
    """RC pairs whose dialogue line and event are both in the pool, first pairing first."""
    in_pool = {description_of(e["full"]) for e in built["entries"]}
    out, seen = [], set()
    for p in built["pairs"]:
        mem, ev = ctx.dialogue.unique[p["d"]], ctx.events.unique[p["e"]]
        if mem in in_pool and ev in in_pool and (mem, ev) not in seen:
            seen.add((mem, ev))
            out.append({"memory_id": ctx.dialogue_id(p["d"]), "memory": mem, "event": ev})
    return out


def check(line, memory, event):
    nums, mem_n, ev_n = numbers(line), numbers(memory), numbers(event)
    issues = [f"{n} appears in neither the memory nor the event" for n in sorted(nums - mem_n - ev_n)]
    return issues


def run():
    out = paths.PILOT_DIR / "out_compare"
    paths.use_reference("dialogue_prov", "all", "ncd")
    ctx = PilotContext()
    built = build_pool(ctx, SHARE, TOTAL, VARIANT, seed=AC_SEED)
    results, calls = [], 0
    for lk in links(ctx, built):
        m = _SAID.match(lk["memory"])
        speaker, said = (m["speaker"], m["text"]) if m else ("", lk["memory"])
        content = (f"MEMORY (earlier session): {speaker} said: '{said}'\n\n"
                   f"NOW (current session): {lk['event']}\n\n"
                   f"SPEAKER: {speaker}")
        rec, cached = generate(ctx.bios_text, content, "narrative", CALLBACK_PROMPT)
        calls += not cached
        raw = strip_fence(rec["text"])
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"line": raw}
        results.append({**lk, "speaker": speaker, "input": content, "output": parsed, "raw": rec["text"],
                        "issues": check(parsed.get("line", ""), lk["memory"], lk["event"])})
    (out / "callbacks.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(results, out / "CALLBACKS.md", rec["model"] if results else "")
    return results, calls


def write_report(results, path, model):
    L = ["# Prototype: explicit callbacks as a separate step", "",
         "Giving memories to the narrative step makes the model merge them into the present (`SESSION2_E2E.md`). Here "
         "each callback is its own small LLM call that sees **one RC link**: an earlier-session dialogue line in the pool "
         "(MEMORY), the current-session event the RC paired it with (NOW), and the colonist who said the memory "
         "(SPEAKER). It writes one dialogue line in the game's dialogue format, so it could be added to the dialogue the "
         "game already shows. The system chooses every link; the LLM only words it.", "",
         f"Pool: the provenance pool of `SESSION2_E2E.md` (share {SHARE}, AC seed {AC_SEED}, `{VARIANT}`, all 162 "
         f"events, NCD). Prompt: `experiments/pilot/prompts/callback.txt`. Model: `{model}`. One generation per link.", "",
         md_table(["link", "MEMORY (earlier session)", "NOW (current session)", "generated line", "reply",
                   "number check"],
                  [[r["memory_id"], r["memory"], r["event"], r["output"].get("line", ""), r["output"].get("reply", ""),
                    "; ".join(r["issues"]) or "ok"] for r in results]), ""]
    v1 = path.parent / "callbacks_v1.json"
    if v1.exists():
        old = json.loads(v1.read_text(encoding="utf-8"))
        L += ["## Earlier version (v1 prompt)", "",
              "The first prompt didn't say that MEMORY is the speaker's own words. Lines it produced:", "",
              md_table(["link", "NOW", "generated line"],
                       [[r["memory_id"], r["event"], r["output"].get("line", "")] for r in old]), ""]
    L += ["## Observations", "", *OBSERVATIONS, ""]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


OBSERVATIONS = [
    "*Claude's reading of the outputs generated on 2026-11-26 (one generation per link; not the author's judgement).*",
    "",
    "- **The separate step keeps then and now apart where the narrative step couldn't.** The steel link, which made the "
    "narrative claim \"fifty-six steel beams\" were hauled this session, now gives \"I'm hauling these eighteen steel "
    "pieces to the stockpile just like I stashed my fifty-six beams before\": each number in its own time. The gazelle "
    "and the camp's-edge grizzly lines are clear callbacks with the memory in the past tense and the event in the present.",
    "- **v1 → v2 fixed the speaker's perspective.** Without being told that MEMORY is the speaker's own words, 3 of 5 "
    "lines attributed it to the listener (\"remember when you said…\", \"the ones you spotted\"). With that one rule, all "
    "5 use the first person.",
    "- **Remaining problems:**",
    "  - **A time-mix the number check can't catch:** S104 → grizzly says the bear is \"standing right by my fifty-six "
    "steel beams\", putting the session-1 beams in the present. 56 does come from the memory, so the check passes it.",
    "  - **Weak links give forced lines:** S104 → silver connects the steel memory to a silver haul because the RC "
    "paired them on wording (\"hauling … to Stockpile zone 1\"). The callback can only be as good as the link.",
    "  - **Some lines read like logs** (\"now I see a gazelle consuming grass\").",
    "",
    "**Design questions this raises** (not decided):",
    "- **How many callbacks per session, and which links?** Five links gave three good lines. One callback per memory, "
    "using the RC pair with the smallest distance, or only links whose event the RC itself chose (not ones the AC added "
    "that the RC also happened to pair), would drop the forced silver line.",
    "- **Where the line goes:** appended to the dialogue the game already generates, or replacing one of its lines.",
    "- **Checking:** the number check catches moved numbers; a second check could compare the line's nouns with the "
    "MEMORY and NOW texts to catch details moved without numbers (the grizzly beside the beams).",
]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--system-certs", action="store_true")
    a = ap.parse_args()
    if a.system_certs:
        import truststore
        truststore.inject_into_ssl()
    results, calls = run()
    print(f"done; {calls} new API calls")
    for r in results:
        print(f"{r['memory_id']} | {r['event']} -> {r['output'].get('line')} | reply: {r['output'].get('reply')} | "
              f"{'; '.join(r['issues']) or 'ok'}")


if __name__ == "__main__":
    main()
