# A1 — Can NCD find continuity?

**Status: FAIL**

13 past dialogue lines × 162 current-session events. NCD order: `event_first` (matches the game). Pass rule: NCD mean Recall@5 >= 0.5.

**CC candidates: filtered.** The CC may only pick the 43 cluster representatives of session 2 at NCD threshold 0.5 (the AC's unique_logs_after_filtering, before traversal). A gold event folded into a cluster counts as found when its representative is retrieved; 7 of 20 gold events are representatives themselves.

## Metrics

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| ncd | 0.462 | 0.577 | 0.435 | 13 | 15 |
| embedding | 0.538 | 0.615 | 0.460 | 13 | 15 |

Without the 1 gold pairs whose event is the reference line's exact description repeated (sensitivity check, not the pass rule):

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| ncd | 0.462 | 0.577 | 0.377 | 13 | 14 |
| embedding | 0.538 | 0.615 | 0.422 | 13 | 14 |

## Rank of each expected event

| dialogue | event | NCD rank | embedding rank | event description |
|---|---|---|---|---|
| J197 | E070 → E069 | 1 | 1 | A(n) grizzly bear standing. |
| J784 | E086 → E090 | 1 | 1 | Stench hauling wooden club to Stockpile zone 1. |
| J784 | E088 → E090 | 1 | 1 | Stench hauling steel x18 to Stockpile zone 1. |
| J784 | E089 → E090 | 1 | 1 | Stench hauling synthread pants (normal 97%) to Stockpile zone 1. |
| J784 | E090 | 1 | 1 | Stench hauling silver x500 to Stockpile zone 1. |
| J784 | E091 → E090 | 1 | 1 | Stench hauling component x30 to Stockpile zone 1. |
| J6248 | E049 | 1 | 1 | Papyrus following Stench. |
| J6248 | E050 | 4 | 2 | Stench leading Papyrus to wooden pen marker. |
| J23595 | E002 → E000 | 19 | 31 | Stench watching for targets. |
| L0 | E085 → E084 | 10 | 11 | Stench burying Walrus, Treehouse builder (dead) in grave. |
| L0 | E086 → E090 | 18 | 15 | Stench hauling wooden club to Stockpile zone 1. |
| J11087 | E082 | 17 | 3 | Stench shared views on aiding the downtrodden with Boyd. |
| J11165 | E000 | 1 | 1 | Boyd watching for targets. |
| J11165 | E002 → E000 | 1 | 1 | Stench watching for targets. |
| b57 | E085 → E084 | 8 | 32 | Stench burying Walrus, Treehouse builder (dead) in grave. |
| b74 | E085 → E084 | 24 | 14 | Stench burying Walrus, Treehouse builder (dead) in grave. |
| b81 | E085 → E084 | 39 | 4 | Stench burying Walrus, Treehouse builder (dead) in grave. |
| b88 | E084 | 5 | 30 | Stench burying Anteater, Shaman (dead) in grave. |
| J19592 | E071 → E072 | 1 | 1 | A(n) gazelle consuming grass. |
| L5 | E095 | 20 | 7 | A medieval farm oaf named Ackmann is crashing in a transport pod near… |

## Concatenation order (event-first vs dialogue-first)

- Mean top-5 overlap per dialogue line: 0.75
- Overlap of the global top-14 pairs (what the game requests at share 0.5): 0.79
- Largest NCD difference between orders: 0.061

## Top 5 per dialogue line

**J197** — A(n) grizzly bear standing.

| # | ncd | embedding |
|---|---|---|
| 1 | E069 A(n) grizzly bear wandering. | E069 A(n) grizzly bear wandering. |
| 2 | E023 A(n) tortoise standing. | E029 A(n) doe standing. |
| 3 | E029 A(n) doe standing. | E034 A(n) timber wolf wandering. |
| 4 | E003 A(n) rat wandering. | E023 A(n) tortoise standing. |
| 5 | E030 A(n) rhinoceros wandering. | E030 A(n) rhinoceros wandering. |

**J784** — Stench hauling steel x56 to Stockpile zone 1.

| # | ncd | embedding |
|---|---|---|
| 1 | E090 Stench hauling silver x500 to Stockpile zone 1. | E090 Stench hauling silver x500 to Stockpile zone 1. |
| 2 | E097 Stench hauling wood x7 to wooden stool (building). | E097 Stench hauling wood x7 to wooden stool (building). |
| 3 | E053 Stench fired her bolt-action rifle at the turkey. | E096 Stench harvesting area. |
| 4 | E130 Odette stumbled while trying to strike Stench. | E065 Stench building grave (building). |
| 5 | E041 Stench chatted about fighting tapirs with Odette. | E157 Stench resting. |

**J6248** — Papyrus following Stench.

| # | ncd | embedding |
|---|---|---|
| 1 | E049 Papyrus following Stench. | E049 Papyrus following Stench. |
| 2 | E096 Stench harvesting area. | E050 Stench leading Papyrus to wooden pen marker. |
| 3 | E065 Stench building grave (building). | E084 Stench burying Anteater, Shaman (dead) in grave. |
| 4 | E050 Stench leading Papyrus to wooden pen marker. | E157 Stench resting. |
| 5 | E080 Stench cloudwatching. | E065 Stench building grave (building). |

**J23595** — Stench moving.

| # | ncd | embedding |
|---|---|---|
| 1 | E157 Stench resting. | E157 Stench resting. |
| 2 | E080 Stench cloudwatching. | E080 Stench cloudwatching. |
| 3 | E096 Stench harvesting area. | E096 Stench harvesting area. |
| 4 | E049 Papyrus following Stench. | E065 Stench building grave (building). |
| 5 | E029 A(n) doe standing. | E062 Stench missed the tortoise. |

**L0** — A group of tribespeople from Confederacy of Loucó have arrived nearby. They are attacking immediately.

| # | ncd | embedding |
|---|---|---|
| 1 | E045 Boyd is wandering around in a psychotic state. This happene… | E064 A(n) turkey fleeing. |
| 2 | E052 The turkey ducked aside at the last second, Stench's bolt-a… | E030 A(n) rhinoceros wandering. |
| 3 | E082 Stench shared views on aiding the downtrodden with Boyd. | E095 A medieval farm oaf named Ackmann is crashing in a transpor… |
| 4 | E053 Stench fired her bolt-action rifle at the turkey. | E034 A(n) timber wolf wandering. |
| 5 | E119 Odette called Stench a salamander. This drove Stench into a… | E155 Battle: The turkey's report |

**J11087** — Boyd relaxing socially.

| # | ncd | embedding |
|---|---|---|
| 1 | E000 Boyd watching for targets. | E045 Boyd is wandering around in a psychotic state. This happene… |
| 2 | E157 Stench resting. | E000 Boyd watching for targets. |
| 3 | E003 A(n) rat wandering. | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 4 | E023 A(n) tortoise standing. | E154 A(n) turkey downed, unconscious. |
| 5 | E029 A(n) doe standing. | E157 Stench resting. |

**J11165** — Odette watching for targets.

| # | ncd | embedding |
|---|---|---|
| 1 | E000 Boyd watching for targets. | E000 Boyd watching for targets. |
| 2 | E080 Stench cloudwatching. | E124 Stench fighting with Odette. |
| 3 | E124 Stench fighting with Odette. | E147 Odette collapsed due to a bruise. |
| 4 | E041 Stench chatted about fighting tapirs with Odette. | E130 Odette stumbled while trying to strike Stench. |
| 5 | E053 Stench fired her bolt-action rifle at the turkey. | E135 Stench missed Odette with a hit from her left fist. |

**b57** — Boyd fired timidly at Walrus.

| # | ncd | embedding |
|---|---|---|
| 1 | E053 Stench fired her bolt-action rifle at the turkey. | E000 Boyd watching for targets. |
| 2 | E082 Stench shared views on aiding the downtrodden with Boyd. | E045 Boyd is wandering around in a psychotic state. This happene… |
| 3 | E000 Boyd watching for targets. | E053 Stench fired her bolt-action rifle at the turkey. |
| 4 | E034 A(n) timber wolf wandering. | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 5 | E051 Stench shot at the turkey. | E052 The turkey ducked aside at the last second, Stench's bolt-a… |

**b74** — Stench hit Walrus with a shot.

| # | ncd | embedding |
|---|---|---|
| 1 | E124 Stench fighting with Odette. | E051 Stench shot at the turkey. |
| 2 | E049 Papyrus following Stench. | E053 Stench fired her bolt-action rifle at the turkey. |
| 3 | E051 Stench shot at the turkey. | E052 The turkey ducked aside at the last second, Stench's bolt-a… |
| 4 | E135 Stench missed Odette with a hit from her left fist. | E157 Stench resting. |
| 5 | E096 Stench harvesting area. | E043 Stench, Hunter is fully healed. |

**b81** — Walrus died.

| # | ncd | embedding |
|---|---|---|
| 1 | E116 Ackmann downed. | E052 The turkey ducked aside at the last second, Stench's bolt-a… |
| 2 | E157 Stench resting. | E154 A(n) turkey downed, unconscious. |
| 3 | E029 A(n) doe standing. | E069 A(n) grizzly bear wandering. |
| 4 | E049 Papyrus following Stench. | E084 Stench burying Anteater, Shaman (dead) in grave. |
| 5 | E003 A(n) rat wandering. | E053 Stench fired her bolt-action rifle at the turkey. |

**b88** — Boyd's shot hit Anteater.

| # | ncd | embedding |
|---|---|---|
| 1 | E051 Stench shot at the turkey. | E000 Boyd watching for targets. |
| 2 | E082 Stench shared views on aiding the downtrodden with Boyd. | E052 The turkey ducked aside at the last second, Stench's bolt-a… |
| 3 | E155 Battle: The turkey's report | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 4 | E053 Stench fired her bolt-action rifle at the turkey. | E045 Boyd is wandering around in a psychotic state. This happene… |
| 5 | E084 Stench burying Anteater, Shaman (dead) in grave. | E053 Stench fired her bolt-action rifle at the turkey. |

**J19592** — A(n) gazelle consuming grass.

| # | ncd | embedding |
|---|---|---|
| 1 | E072 A(n) hare consuming grass. | E072 A(n) hare consuming grass. |
| 2 | E069 A(n) grizzly bear wandering. | E003 A(n) rat wandering. |
| 3 | E065 Stench building grave (building). | E034 A(n) timber wolf wandering. |
| 4 | E154 A(n) turkey downed, unconscious. | E069 A(n) grizzly bear wandering. |
| 5 | E003 A(n) rat wandering. | E023 A(n) tortoise standing. |

**L5** — Chunks of a spacecraft have impacted nearby. You can deconstruct them to yield resources.

| # | ncd | embedding |
|---|---|---|
| 1 | E052 The turkey ducked aside at the last second, Stench's bolt-a… | E150 The turkey dropped. |
| 2 | E053 Stench fired her bolt-action rifle at the turkey. | E097 Stench hauling wood x7 to wooden stool (building). |
| 3 | E082 Stench shared views on aiding the downtrodden with Boyd. | E090 Stench hauling silver x500 to Stockpile zone 1. |
| 4 | E118 Odette is no longer on an insulting spree against Stench, H… | E096 Stench harvesting area. |
| 5 | E139 Odette tried to use her right fist to hit Stench, but stumb… | E052 The turkey ducked aside at the last second, Stench's bolt-a… |

