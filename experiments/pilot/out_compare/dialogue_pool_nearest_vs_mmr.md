# Final log pool with dialogue as reference: without vs with MMR

Share 0.5, total 12, AC seed 42, reference = session-1 dialogue. Pools are in time order, as the LLM receives them.

Source: `experiments/pilot/out/a4_pools.jsonl` (share 0.5, seed 42) and `experiments/pilot/out/a3_pairs.csv` (which dialogue line each CC event was paired with).

## Without MMR (`nearest`, what the game does now)

| channel | log | paired with |
|---|---|---|
| CC (ref) | Odette 'Odette' O'Neill said 'Stench, I watched the far treeline for more raiders.' | — |
| AC | Boyd watching for targets. | |
| AC | Stench, Hunter is fully healed. | |
| AC | Boyd is wandering around in a psychotic state. This happened because of poor mood. The final straw was: Awful barracks | |
| AC | Stench leading Papyrus to wooden pen marker. | |
| AC | Stench missed the tortoise. | |
| AC | Stench hauling silver x500 to Stockpile zone 1. | |
| CC | Odette is no longer on an insulting spree against Stench, Hunter. | S110 (treeline) |
| CC | Odette missed Stench with a beat from her left fist. | S110 |
| CC | Stench missed Odette with a smash from her left fist. | S110 |
| CC | Odette attempted to hit Stench, but hesitated at the last second. | S110 |
| CC | Stench flailed at Odette with her left fist, but stumbled at the last second. | S110 |

## With MMR

| channel | log | paired with |
|---|---|---|
| CC (ref) | Odette 'Odette' O'Neill said 'Stench, I watched the far treeline for more raiders.' | — |
| CC (ref) | Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, then I stung the anteater.' | — |
| CC (ref) | Lidia 'Stench' Schmitt said 'Boyd, Papyrus trailed me all the way to Stockpile One.' | — |
| AC | Boyd watching for targets. | |
| AC | Stench, Hunter is fully healed. | |
| AC | Boyd is wandering around in a psychotic state. This happened because of poor mood. The final straw was: Awful barracks | |
| AC | Stench leading Papyrus to wooden pen marker. | |
| AC | Stench missed the tortoise. | |
| CC | Stench shared views on aiding the downtrodden with Boyd. | S108 (walrus) |
| CC | Stench hauling synthread pants (normal 97%) to Stockpile zone 1. | S106 (Papyrus / Stockpile One) |
| AC | Stench hauling silver x500 to Stockpile zone 1. | |
| CC | Odette attempted to hit Stench, but hesitated at the last second. | S110 (treeline) |

## What changes

The AC half is nearly the same in both pools. The CC gets 6 slots either way, and every paired dialogue line uses one of them.

- **Without MMR**, one dialogue line takes all 6 CC slots: the line itself plus 5 events that describe the same fistfight blow by blow. The LLM gets one story told five times, matched to the treeline line only through the names Odette and Stench.
- **With MMR**, three dialogue lines get one event each (3 slots for the lines, 3 for the events). The pool covers more ground: one fight line, a conversation with Boyd, and a hauling job to the stockpile, which really does echo "Stockpile One".
- **The matches are still loose.** "I hit that walrus" pairs with a conversation about the downtrodden, not with the walrus burial marked as gold.

MMR fixes the redundancy; it doesn't fix NCD's poor sense of what's related.
