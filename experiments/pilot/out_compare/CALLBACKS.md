# Prototype: explicit callbacks as a separate step

Giving memories to the narrative step makes the model merge them into the present (`SESSION2_E2E.md`). Here each callback is its own small LLM call that sees **one RC link**: an earlier-session dialogue line in the pool (MEMORY), the current-session event the RC paired it with (NOW), and the colonist who said the memory (SPEAKER). It writes one dialogue line in the game's dialogue format, so it could be added to the dialogue the game already shows. The system chooses every link; the LLM only words it.

Pool: the provenance pool of `SESSION2_E2E.md` (share 0.5, AC seed 42, `nearest`, all 162 events, NCD). Prompt: `experiments/pilot/prompts/callback.txt`. Model: `gemini-3.5-flash-lite`. One generation per link.

| link | MEMORY (earlier session) | NOW (current session) | generated line | reply | number check |
|---|---|---|---|---|---|
| S111 | Odette 'Odette' O'Neill said 'Stench, those gazelles were grazing amid the chunks of the downed spacecraft.' | A(n) gazelle consuming grass. | [N], I said those gazelles were grazing amid the chunks of the downed spacecraft, and now I see a gazelle consuming grass. | Nature finds a way, even around the wreckage. | ok |
| S104 | Lidia 'Stench' Schmitt said 'Boyd, I had those fifty-six steel beams stashed before the grizzly settled in.' | A(n) grizzly bear standing. | [N], that grizzly I mentioned earlier is standing right by my fifty-six steel beams. | Get away from it right now! | ok |
| S112 | Odette 'Odette' O'Neill said 'Boyd, a grizzly at camp's edge was trouble waiting to happen.' | A(n) grizzly bear standing. | [N], I said a grizzly at camp's edge was trouble waiting to happen, and now there's one just standing right there. | Grab your weapon before it decides to charge us! | ok |
| S104 | Lidia 'Stench' Schmitt said 'Boyd, I had those fifty-six steel beams stashed before the grizzly settled in.' | Stench hauling steel x18 to Stockpile zone 1. | [N], I'm hauling these eighteen steel pieces to the stockpile just like I stashed my fifty-six beams before. | Just make sure you don't burn anything this time, Lidia. | ok |
| S104 | Lidia 'Stench' Schmitt said 'Boyd, I had those fifty-six steel beams stashed before the grizzly settled in.' | Stench hauling silver x500 to Stockpile zone 1. | [N], I had those fifty-six steel beams stashed before the grizzly settled in, but now I'm hauling five hundred silver. | Just make sure you don't drop it all in the dirt! | ok |

## Earlier version (v1 prompt)

The first prompt didn't say that MEMORY is the speaker's own words. Lines it produced:

| link | NOW | generated line |
|---|---|---|
| S111 | A(n) gazelle consuming grass. | [N], that gazelle is eating grass just like the ones you spotted near the spacecraft wreckage earlier. |
| S104 | A(n) grizzly bear standing. | [N], that grizzly I mentioned having the fifty-six steel beams stashed from is standing right outside now. |
| S112 | A(n) grizzly bear standing. | [N], remember when you said a grizzly at camp's edge was trouble? Well, there's a grizzly bear standing right out there now. |
| S104 | Stench hauling steel x18 to Stockpile zone 1. | [N], I'm hauling these eighteen steel pieces to the stockpile now, unlike those fifty-six beams I had stashed before. |
| S104 | Stench hauling silver x500 to Stockpile zone 1. | [N], you said I had those steel beams stashed, but now I'm just hauling this silver to the stockpile. |

## Observations

*Claude's reading of the outputs generated on 2026-11-26 (one generation per link; not the author's judgement).*

- **The separate step keeps then and now apart where the narrative step couldn't.** The steel link, which made the narrative claim "fifty-six steel beams" were hauled this session, now gives "I'm hauling these eighteen steel pieces to the stockpile just like I stashed my fifty-six beams before": each number in its own time. The gazelle and the camp's-edge grizzly lines are clear callbacks with the memory in the past tense and the event in the present.
- **v1 → v2 fixed the speaker's perspective.** Without being told that MEMORY is the speaker's own words, 3 of 5 lines attributed it to the listener ("remember when you said…", "the ones you spotted"). With that one rule, all 5 use the first person.
- **Remaining problems:**
  - **A time-mix the number check can't catch:** S104 → grizzly says the bear is "standing right by my fifty-six steel beams", putting the session-1 beams in the present. 56 does come from the memory, so the check passes it.
  - **Weak links give forced lines:** S104 → silver connects the steel memory to a silver haul because the RC paired them on wording ("hauling … to Stockpile zone 1"). The callback can only be as good as the link.
  - **Some lines read like logs** ("now I see a gazelle consuming grass").

**Design questions this raises** (not decided):
- **How many callbacks per session, and which links?** Five links gave three good lines. One callback per memory, using the RC pair with the smallest distance, or only links whose event the RC itself chose (not ones the AC added that the RC also happened to pair), would drop the forced silver line.
- **Where the line goes:** appended to the dialogue the game already generates, or replacing one of its lines.
- **Checking:** the number check catches moved numbers; a second check could compare the line's nouns with the MEMORY and NOW texts to catch details moved without numbers (the grizzly beside the beams).

