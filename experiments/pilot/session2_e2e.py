"""
Session 2 end to end: selection, narrative and dialogue, with and without provenance.

Builds the share-0.5 pool as the game's F11 pipeline would (AC seed 42, CC variant `nearest`,
all 162 session-2 events, NCD) for two RC references:
  original    the session-1 dialogue lines as the game logs them (what the game does today)
  provenance  the same lines, scored through the session-1 logs they were generated from
then runs the game's two generation steps with the existing prompts and model:
  N  narrative from the pool        (story_llm.generate_story_llm, mode "narrative")
  M  dialogue from the narrative    (mode "dialogue_from_narrative")

LLM outputs are cached in out/llm_cache/ (key: pool or narrative, prompt text, model, mode), so a
rerun makes no new API calls.

  python -m experiments.pilot.session2_e2e [--system-certs]

Writes experiments/pilot/out_compare/SESSION2_E2E.md and session2_e2e.json.
"""

import argparse
import hashlib
import json

from experiments.common import paths
from experiments.common.context import PilotContext
from experiments.common.data import description_of
from experiments.common.report import md_table
from experiments.common.simulate import build_pool

SHARE, TOTAL, AC_SEED, VARIANT = 0.5, 12, 42, "nearest"
# (name, RC reference, how the pool is given to the LLM, narrative prompt override or None)
MEMORY_PROMPT = paths.PILOT_DIR / "prompts" / "narrative_memory.txt"
EXPLICIT_PROMPT = paths.PILOT_DIR / "prompts" / "narrative_memory_explicit.txt"
LINKS_PROMPT = paths.PILOT_DIR / "prompts" / "narrative_memory_links.txt"
CONDITIONS = (("original", "dialogue", "flat", None), ("provenance", "dialogue_prov", "flat", None),
              ("provenance + memory block", "dialogue_prov", "memory", None),
              ("provenance + memory block + memory prompt", "dialogue_prov", "memory", MEMORY_PROMPT),
              ("provenance + memory block + explicit-callback prompt", "dialogue_prov", "memory", EXPLICIT_PROMPT),
              ("provenance + RC links + links prompt", "dialogue_prov", "links", LINKS_PROMPT))

MEMORY_HEADER = ("Earlier sessions (things the colonists said in a previous session; these are memories and "
                 "background, not events happening now):")
SESSION_HEADER = "This session (events in temporal order):"


def llm_input(ctx, built, fmt):
    """
    flat:   the pool as the game sends it today, one line per log ("\\n\\n"-joined, as sipport does).
    memory: the pool's dialogue lines from earlier sessions in a separate block, labelled as memories,
            then this session's logs. Same pool and prompt; only the formatting changes.
    """
    if fmt == "flat":
        return "\n\n".join(built["pool"])
    ref_descs = {description_of(e["full"]) for e in built["entries"] if e["kind"] == "reference"}
    earlier = [l for l in built["pool"] if l.split("[x")[0] in ref_descs]
    current = [l for l in built["pool"] if l.split("[x")[0] not in ref_descs]
    if fmt == "memory":
        return "\n\n".join([MEMORY_HEADER, *earlier, SESSION_HEADER, *current])

    # links: memories labelled M1.., and each RC event marked with the memories the RC paired it with
    # (only pairs whose dialogue line is in the pool). The system decides every link.
    label = {l.split("[x")[0]: f"M{i + 1}" for i, l in enumerate(earlier)}
    recalls = {}
    for p in built["pairs"]:
        mem = label.get(ctx.dialogue.unique[p["d"]])
        if mem:
            recalls.setdefault(ctx.events.unique[p["e"]], [])
            if mem not in recalls[ctx.events.unique[p["e"]]]:
                recalls[ctx.events.unique[p["e"]]].append(mem)
    cc_descs = {description_of(e["full"]) for e in built["entries"] if e["channel"] == "CC" and e["kind"] != "reference"}
    marked = [l + (f" (recalls {', '.join(recalls[l.split('[x')[0]])})"
                   if l.split("[x")[0] in cc_descs and l.split("[x")[0] in recalls else "") for l in current]
    return "\n\n".join([MEMORY_HEADER, *[f"{label[l.split('[x')[0]]}: {l}" for l in earlier], SESSION_HEADER, *marked])
# Session-1 things a continuity-aware story could pick up (from the session-1 selected logs and dialogue).
SESSION1_TERMS = ("raid", "raider", "tribe", "walrus", "anteater", "grizzly", "gazelle", "spacecraft",
                  "chunks", "steel", "stockpile", "papyrus", "treeline")


def generate(bios, content, mode, prompt_file=None):
    """
    prompt_file: an experiment-only system prompt used instead of prompts/<mode>.txt (story_llm itself
    is unchanged; its get_prompt is swapped only for this call).
    """
    import story_llm
    model = story_llm.get_model_url()
    prompt = prompt_file.read_text(encoding="utf-8") if prompt_file else story_llm.get_prompt(mode)
    key = hashlib.sha256(json.dumps([content, bios, prompt, model, mode, 0]).encode()).hexdigest()[:20]
    cache_dir = paths.PILOT_DIR / "out" / "llm_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = cache_dir / f"{key}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8")), True
    original_get_prompt = story_llm.get_prompt
    if prompt_file:
        story_llm.get_prompt = lambda m: prompt if m == mode else original_get_prompt(m)
    try:
        text, usage = story_llm.generate_story_llm(bios, content, mode=mode, return_usage=True)
    finally:
        story_llm.get_prompt = original_get_prompt
    rec = {"text": text, "usage": usage, "model": model, "mode": mode, "key": key}
    cache.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    return rec, False


def pool_rows(ctx, built):
    pair_of = {}
    for p in built["pairs"]:
        pair_of.setdefault(p["e"], ctx.dialogue_id(p["d"]))
    rows = []
    entries = sorted(built["entries"], key=lambda e: int(e["full"].split("Timestamp_")[1].split("_")[0]))
    for e in entries:
        desc = description_of(e["full"])
        if e["kind"] == "reference":
            rows.append(["RC · dialogue line", ctx.dialogue_id(e["d"]), desc])
        elif e["channel"] == "CC":
            rows.append(["RC · event", f"linked to {pair_of.get(e['e'], '?')}", desc])
        else:
            rows.append(["AC", "", desc])
    return rows


def run():
    out = paths.PILOT_DIR / "out_compare"
    out.mkdir(parents=True, exist_ok=True)
    results, calls = {}, 0
    for name, ref, fmt, prompt_file in CONDITIONS:
        paths.use_reference(ref, "all", "ncd")
        ctx = PilotContext()
        built = build_pool(ctx, SHARE, TOTAL, VARIANT, seed=AC_SEED)
        content = llm_input(ctx, built, fmt)
        narr, c1 = generate(ctx.bios_text, content, "narrative", prompt_file)
        dial, c2 = generate(ctx.bios_text, narr["text"], "dialogue_from_narrative")
        calls += (not c1) + (not c2)
        results[name] = {"pool": built["pool"], "rows": pool_rows(ctx, built), "narrative": narr["text"],
                         "dialogue": dial["text"], "model": narr["model"], "format": fmt, "llm_input": content}
    (out / "session2_e2e.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(results, out / "SESSION2_E2E.md")
    return results, calls


def strip_fence(text):
    """The dialogue step returns JSON wrapped in a ```json fence; drop it so the report can add its own."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else ""
        if t.rstrip().endswith("```"):
            t = t.rstrip()[:-3]
    return t.strip()


OBSERVATIONS = [
    "*Claude's reading of the cached outputs generated on 2026-11-26 (not the author's judgement; regenerating "
    "with a different model or prompt would need a fresh read).*", "",
    "- **Selection.** *Original*: one dialogue line (S110, the treeline) brings five near-identical fight lines; "
    "none relates to the treeline or the raiders. *Provenance*: three lines (S104 steel/grizzly, S111 gazelles/"
    "spacecraft, S112 grizzly) bring a grizzly, a grazing gazelle and a steel haul to the stockpile. These are clearly "
    "linked to what the lines are about, but they are mostly routine logs.",
    "- **The provenance pool loses session 2's main drama.** The Odette–Stench fistfight and insult spree are the most "
    "eventful things in session 2, and in the original pool they came only through the RC's name matching. The AC "
    "didn't select them at this share, so with provenance they disappear from the pool and from the story. Continuity "
    "now competes with the current session's salient events for the same 12 slots.",
    "- **Narrative.** *Original* is coherent and dramatic, but has no link to session 1 (keyword check: none). "
    "*Provenance* picks up session 1 (steel beams, the grizzly at the camp's edge, gazelles among the spacecraft "
    "wreckage), but **it narrates the old dialogue as if it were happening now** (\"secured vital steel beams … before "
    "a dangerous grizzly bear established its territory\"). The LLM isn't told which pool lines are memories from an "
    "earlier session, so continuity turns into retelling.",
    "- **Dialogue.** Both are fluent. *Provenance* refers back to session 1 naturally (\"that grizzly bear is still "
    "lingering right by the camp edge\", \"those steel beams … took forever to haul back\"), but also invents a detail "
    "(\"steel beams from the wreckage\": nothing links the steel to the spacecraft).",
    "",
    "- **Provenance + memory block** (same pool, same prompt; the earlier-session dialogue lines are given in a "
    "separate block labelled as memories, not events happening now):",
    "  - The narrative **no longer retells the old dialogue as current events**.",
    "  - But it **drops the session-1 continuity altogether**: the memories are treated as background and not used. "
    "The gazelles and grizzly it mentions are session 2's own wildlife; nothing refers back to session 1.",
    "  - **New errors:** it reads \"Stench, Hunter is fully healed\" as an animal called Hunter recovering, and calls the "
    "18 steel hauled this session \"eighteen steel beams\", borrowing \"beams\" from the session-1 memory.",
    "  - Formatting alone swings the model from retelling to ignoring. The narrative prompt asks for \"an objective "
    "summary of the provided logs\" and says nothing about memories.",
    "- **Provenance + memory block + memory prompt** (the narrative prompt is told what memories are and to refer "
    "back to them only where a current event connects):",
    "  - **No retelling:** session-1 content is not narrated as new events.",
    "  - **Implicit continuity:** \"the persistent grizzly bear and grazing gazelles remained an ever-present fixture\"; "
    "in the dialogue, \"that bear is still prowling just outside the perimeter fence\". There is no explicit past-tense "
    "reference (nothing about the steel beams stashed before the grizzly settled in).",
    "  - **Fewer errors:** the \"Hunter\" misreading is gone (Stench recovers), and the dialogue uses the family tie "
    "from the bios (\"dad just wandered off\"). One slip: \"salvaged steel\" leaks the wreckage from the memories.",
    "- **Provenance + memory block + explicit-callback prompt** (asks for exactly one explicit past-tense callback "
    "when a connection exists, none otherwise):",
    "  - **No explicit callback** (\"a lingering grizzly bear\").",
    "  - **Memories leak into the present:** Lidia hauls steel and silver \"from the debris of a downed spacecraft\", and "
    "the dialogue says \"we really need to clear out the debris from that downed spacecraft\". That is retelling plus "
    "an invented link, the failure the prompt was meant to prevent.",
    "- **Provenance + RC links + links prompt** (memories labelled M1–M3; each RC event marked with the memories the RC "
    "paired it with, e.g. the steel haul `(recalls M1)`; the prompt allows referring back only through the marks):",
    "  - The model **does use the memories**, but **fuses them into the present** rather than referring back: "
    "\"gazelles grazed among distant spacecraft debris\", with no past tense anywhere.",
    "  - **A session-1 fact overwrites a session-2 fact:** Stench \"hauled fifty-six steel beams back to the stockpile\". "
    "This session's log says 18 steel; 56 comes from memory M1. The dialogue repeats it (\"dragging fifty-six heavy "
    "beams across camp\").",
    "- **A contamination check worth recording:** the first versions of both memory prompts used an example sentence "
    "about this colony's grizzly, and with it the explicit-callback prompt produced a clean callback (\"the grizzly "
    "bear—which had settled at the camp's edge in the colony's early days—was still prowling nearby\"), nearly word "
    "for word from the example. With a neutral example (a well running dry) that callback disappeared. Those outputs "
    "are kept in `session2_e2e_contaminated.json`.",
    "",
    "| condition | uses session 1? | treats it as past? | errors noticed |",
    "|---|---|---|---|",
    "| original | no | n/a | none major |",
    "| provenance | yes, strongly | no (retold as now) | steel \"from the wreckage\" |",
    "| + memory block | no | n/a | \"Hunter\" as an animal; \"eighteen steel beams\" |",
    "| + memory prompt | implicitly (grizzly as an ever-present fixture) | yes | \"salvaged steel\" |",
    "| + explicit-callback prompt | yes, as present events | no | steel \"from the debris of a downed spacecraft\" |",
    "| + RC links + links prompt | yes, fused with present events | no | \"fifty-six steel beams\" hauled now (log: 18) |",
    "",
    "**Reading:** the more the narrative step is pushed to use memories, the more it merges them into the present. "
    "Asking softly gives faint but correct continuity. Asking firmly, or handing it the exact links, makes it retell the "
    "memories as current events, and with the links it even overwrote a current fact with a remembered one. Within a "
    "single summarisation call, this model doesn't keep \"then\" and \"now\" apart.",
    "",
    "**Suggested follow-ups** (not done):",
    "- **Keep the narrative step on the current session** (the memory-prompt version, or the flat pool without the "
    "dialogue lines). Let continuity come from the selection: the RC already puts events that connect to earlier "
    "dialogue into the pool.",
    "- **Deliver explicit callbacks separately and constrained:** e.g. a short, dedicated step that receives one "
    "RC link (a memory and the current event the RC paired with it) and writes a single past-tense sentence or "
    "dialogue line about it, which can be checked against both logs. The system chooses the link; the LLM only words it.",
    "- Check the share: at 0.5 the RC takes 6 of 12 slots, enough to crowd out session 2's own highlights. A lower "
    "share (e.g. 0.25) or a quota that counts events only may keep both.",
    "- Read more than one run: this is one AC seed and one generation per condition.",
]


def term_hits(text):
    t = text.lower()
    return [w for w in SESSION1_TERMS if w in t]


def write_report(results, path):
    model = results["provenance"]["model"]
    L = ["# Session 2 end to end: selection, narrative and dialogue", "",
         f"Share {SHARE}, total {TOTAL}, AC seed {AC_SEED}, CC variant `{VARIANT}`, all 162 session-2 events, NCD. "
         f"Generation: the game's two steps with the existing prompts (`prompts/narrative.txt`, "
         f"`prompts/dialogue_from_narrative.txt`) and model `{model}`, no cast block. **original** is what the game does "
         "today; **provenance** scores each session-1 dialogue line through the logs it was generated from; "
         "**provenance + memory block** uses the same pool and prompt, but gives the earlier-session dialogue lines to "
         "the LLM in a separate block labelled as memories.", "",
         "Things to check (author's judgement):", "",
         "1. **Selection:** are the RC's events plausibly connected to the session-1 dialogue lines they're linked to?",
         "2. **Narrative:** does it pick up what happened in session 1, and does it read well?",
         "3. **Dialogue:** is it good dialogue, and does it refer back to session 1 naturally?", ""]
    for name, _, fmt, prompt_file in CONDITIONS:
        r = results[name]
        L += [f"## {name[:1].upper() + name[1:]}", ""]
        if fmt == "links":
            L += ["Same pool as *provenance*. The memories are labelled M1, M2, …, and each event the RC picked for a "
                  "memory is marked with the RC's own pairing, e.g. `(recalls M1)`; the system decides every link. "
                  f"Narrative prompt: `{prompt_file.relative_to(paths.REPO_ROOT).as_posix()}`, which explains the marks "
                  "and adds: *\"For an event marked (recalls Mx), you may refer back to memory Mx briefly, in the past "
                  "tense, where it fits the story … Only link memories to the events marked with them; do not link any "
                  "other event to a memory, and never narrate memories as new events.\"* The dialogue step is unchanged. "
                  "What the LLM receives as its input logs:", "", "```", r["llm_input"], "```", ""]
        elif fmt == "memory" and prompt_file:
            guideline = ("*\"If a current event connects to a memory, make that connection once, explicitly, in the past "
                         "tense, so a reader who remembers the earlier session recognises it … Mention at most one such "
                         "connection … If no current event connects to a memory, do not mention the memories at all.\"*"
                         if prompt_file == EXPLICIT_PROMPT else
                         "*\"Memories are not events happening now. Where a current event connects to a memory, refer "
                         "back to it briefly in the past tense … Do not narrate memories as new events, and do not "
                         "invent links that the logs and memories don't support.\"*")
            L += ["Same input as *provenance + memory block*. Narrative prompt: "
                  f"`{prompt_file.relative_to(paths.REPO_ROOT).as_posix()}`, a copy of `prompts/narrative.txt` that "
                  "says the input may start with memories from earlier sessions, asks to summarise the current-session "
                  f"logs, and adds: {guideline} The dialogue step is unchanged.", ""]
        elif fmt == "memory":
            L += ["Same pool as *provenance*. What the LLM receives as its input logs:", "", "```",
                  r["llm_input"], "```", ""]
        else:
            L += ["### Pool (as the LLM receives it, oldest first)", "",
                  md_table(["channel", "link", "description"], r["rows"]), ""]
        L += [
              "### Narrative", "", r["narrative"].strip(), "", "### Dialogue", "", "```json",
              strip_fence(r["dialogue"]), "```", "",
              "Keyword check (session-1 terms appearing; a crude indicator, not a judgement): "
              f"narrative: {', '.join(term_hits(r['narrative'])) or 'none'}; "
              f"dialogue: {', '.join(term_hits(r['dialogue'])) or 'none'}.", ""]
    L += ["## Observations", ""] + OBSERVATIONS + [""]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--system-certs", action="store_true",
                    help="verify HTTPS against the OS certificate store (needs `truststore`)")
    a = ap.parse_args()
    if a.system_certs:
        import truststore
        truststore.inject_into_ssl()
    results, calls = run()
    print(f"done; {calls} new API calls")


if __name__ == "__main__":
    main()
