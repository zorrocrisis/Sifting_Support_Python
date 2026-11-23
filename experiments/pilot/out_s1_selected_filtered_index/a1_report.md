# A1 — Can NCD find continuity?

**Status: PASS**

13 past dialogue lines × 162 current-session events. NCD order: `event_first` (matches the game). Pass rule: NCD mean Recall@5 >= 0.5.

**CC candidates: filtered.** The CC may only pick the 43 cluster representatives of session 2 at NCD threshold 0.5 (the AC's unique_logs_after_filtering, before traversal). A gold event folded into a cluster counts as found when its representative is retrieved; 7 of 20 gold events are representatives themselves.

## Metrics

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| index | 0.654 | 0.654 | 0.539 | 13 | 15 |

Without the 1 gold pairs whose event is the reference line's exact description repeated (sensitivity check, not the pass rule):

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| index | 0.654 | 0.654 | 0.501 | 13 | 14 |

## Rank of each expected event

| dialogue | event | index rank | embedding rank | event description |
|---|---|---|---|---|
| J197 | E070 → E069 | 1 | – | A(n) grizzly bear standing. |
| J784 | E086 → E090 | 1 | – | Stench hauling wooden club to Stockpile zone 1. |
| J784 | E088 → E090 | 1 | – | Stench hauling steel x18 to Stockpile zone 1. |
| J784 | E089 → E090 | 1 | – | Stench hauling synthread pants (normal 97%) to Stockpile zone 1. |
| J784 | E090 | 1 | – | Stench hauling silver x500 to Stockpile zone 1. |
| J784 | E091 → E090 | 1 | – | Stench hauling component x30 to Stockpile zone 1. |
| J6248 | E049 | 1 | – | Papyrus following Stench. |
| J6248 | E050 | 2 | – | Stench leading Papyrus to wooden pen marker. |
| J23595 | E002 → E000 | 20 | – | Stench watching for targets. |
| L0 | E085 → E084 | 1 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| L0 | E086 → E090 | 20 | – | Stench hauling wooden club to Stockpile zone 1. |
| J11087 | E082 | 4 | – | Stench shared views on aiding the downtrodden with Boyd. |
| J11165 | E000 | 3 | – | Boyd watching for targets. |
| J11165 | E002 → E000 | 3 | – | Stench watching for targets. |
| b57 | E085 → E084 | 15 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| b74 | E085 → E084 | 18 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| b81 | E085 → E084 | 19 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| b88 | E084 | 1 | – | Stench burying Anteater, Shaman (dead) in grave. |
| J19592 | E071 → E072 | 1 | – | A(n) gazelle consuming grass. |
| L5 | E095 | 5 | – | A medieval farm oaf named Ackmann is crashing in a transport pod near… |

**CC similarity: event indexing** (entities, place, log type, NCD text; see `experiments/common/event_index.py`). The `index` method ranks by that score.

## Top 5 per dialogue line

**J197** — A(n) grizzly bear standing.

| # | index |
|---|---|
| 1 | E069 A(n) grizzly bear wandering. |
| 2 | E023 A(n) tortoise standing. |
| 3 | E030 A(n) rhinoceros wandering. |
| 4 | E029 A(n) doe standing. |
| 5 | E064 A(n) turkey fleeing. |

**J784** — Stench hauling steel x56 to Stockpile zone 1.

| # | index |
|---|---|
| 1 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| 2 | E097 Stench hauling wood x7 to wooden stool (building). |
| 3 | E080 Stench cloudwatching. |
| 4 | E096 Stench harvesting area. |
| 5 | E157 Stench resting. |

**J6248** — Papyrus following Stench.

| # | index |
|---|---|
| 1 | E049 Papyrus following Stench. |
| 2 | E050 Stench leading Papyrus to wooden pen marker. |
| 3 | E096 Stench harvesting area. |
| 4 | E157 Stench resting. |
| 5 | E080 Stench cloudwatching. |

**J23595** — Stench moving.

| # | index |
|---|---|
| 1 | E080 Stench cloudwatching. |
| 2 | E157 Stench resting. |
| 3 | E096 Stench harvesting area. |
| 4 | E097 Stench hauling wood x7 to wooden stool (building). |
| 5 | E090 Stench hauling silver x500 to Stockpile zone 1. |

**L0** — A group of tribespeople from Confederacy of Loucó have arrived nearby. They are attacking immediately.

| # | index |
|---|---|
| 1 | E084 Stench burying Anteater, Shaman (dead) in grave. |
| 2 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 3 | E118 Odette is no longer on an insulting spree against Stench, H… |
| 4 | E042 Critical alert (UI notification): Major break risk |
| 5 | E095 A medieval farm oaf named Ackmann is crashing in a transpor… |

**J11087** — Boyd relaxing socially.

| # | index |
|---|---|
| 1 | E000 Boyd watching for targets. |
| 2 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 3 | E042 Critical alert (UI notification): Major break risk |
| 4 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 5 | E096 Stench harvesting area. |

**J11165** — Odette watching for targets.

| # | index |
|---|---|
| 1 | E123 Odette was afflicted with (a) bruise (human fist) (torso) |
| 2 | E124 Stench fighting with Odette. |
| 3 | E000 Boyd watching for targets. |
| 4 | E135 Stench missed Odette with a hit from her left fist. |
| 5 | E131 Stench tried to smash Odette, but missed. |

**b57** — Boyd fired timidly at Walrus.

| # | index |
|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E042 Critical alert (UI notification): Major break risk |
| 3 | E000 Boyd watching for targets. |
| 4 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 5 | E062 Stench missed the tortoise. |

**b74** — Stench hit Walrus with a shot.

| # | index |
|---|---|
| 1 | E062 Stench missed the tortoise. |
| 2 | E051 Stench shot at the turkey. |
| 3 | E135 Stench missed Odette with a hit from her left fist. |
| 4 | E053 Stench fired her bolt-action rifle at the turkey. |
| 5 | E131 Stench tried to smash Odette, but missed. |

**b81** — Walrus died.

| # | index |
|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E000 Boyd watching for targets. |
| 3 | E042 Critical alert (UI notification): Major break risk |
| 4 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 5 | E062 Stench missed the tortoise. |

**b88** — Boyd's shot hit Anteater.

| # | index |
|---|---|
| 1 | E084 Stench burying Anteater, Shaman (dead) in grave. |
| 2 | E000 Boyd watching for targets. |
| 3 | E042 Critical alert (UI notification): Major break risk |
| 4 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 5 | E082 Stench shared views on aiding the downtrodden with Boyd. |

**J19592** — A(n) gazelle consuming grass.

| # | index |
|---|---|
| 1 | E072 A(n) hare consuming grass. |
| 2 | E029 A(n) doe standing. |
| 3 | E069 A(n) grizzly bear wandering. |
| 4 | E154 A(n) turkey downed, unconscious. |
| 5 | E064 A(n) turkey fleeing. |

**L5** — Chunks of a spacecraft have impacted nearby. You can deconstruct them to yield resources.

| # | index |
|---|---|
| 1 | E118 Odette is no longer on an insulting spree against Stench, H… |
| 2 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 3 | E042 Critical alert (UI notification): Major break risk |
| 4 | E043 Stench, Hunter is fully healed. |
| 5 | E095 A medieval farm oaf named Ackmann is crashing in a transpor… |

