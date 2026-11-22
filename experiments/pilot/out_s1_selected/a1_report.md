# A1 — Can NCD find continuity?

**Status: FAIL**

13 past dialogue lines × 162 current-session events. NCD order: `event_first` (matches the game). Pass rule: NCD mean Recall@5 >= 0.5.

## Metrics

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| ncd | 0.331 | 0.346 | 0.404 | 13 | 20 |
| embedding | 0.638 | 0.654 | 0.491 | 13 | 20 |

Without the 3 gold pairs whose event is the reference line's exact description repeated (sensitivity check, not the pass rule):

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| ncd | 0.164 | 0.182 | 0.211 | 11 | 17 |
| embedding | 0.573 | 0.591 | 0.338 | 11 | 17 |

## Rank of each expected event

| dialogue | event | NCD rank | embedding rank | event description |
|---|---|---|---|---|
| J197 | E070 | 1 | 1 | A(n) grizzly bear standing. |
| J784 | E086 | 3 | 4 | Stench hauling wooden club to Stockpile zone 1. |
| J784 | E088 | 1 | 1 | Stench hauling steel x18 to Stockpile zone 1. |
| J784 | E089 | 6 | 6 | Stench hauling synthread pants (normal 97%) to Stockpile zone 1. |
| J784 | E090 | 2 | 3 | Stench hauling silver x500 to Stockpile zone 1. |
| J784 | E091 | 4 | 2 | Stench hauling component x30 to Stockpile zone 1. |
| J6248 | E049 | 1 | 1 | Papyrus following Stench. |
| J6248 | E050 | 15 | 3 | Stench leading Papyrus to wooden pen marker. |
| J23595 | E002 | 29 | 4 | Stench watching for targets. |
| L0 | E085 | 23 | 104 | Stench burying Walrus, Treehouse builder (dead) in grave. |
| L0 | E086 | 38 | 91 | Stench hauling wooden club to Stockpile zone 1. |
| J11087 | E082 | 80 | 5 | Stench shared views on aiding the downtrodden with Boyd. |
| J11165 | E000 | 1 | 3 | Boyd watching for targets. |
| J11165 | E002 | 2 | 17 | Stench watching for targets. |
| b57 | E085 | 23 | 24 | Stench burying Walrus, Treehouse builder (dead) in grave. |
| b74 | E085 | 28 | 2 | Stench burying Walrus, Treehouse builder (dead) in grave. |
| b81 | E085 | 104 | 1 | Stench burying Walrus, Treehouse builder (dead) in grave. |
| b88 | E084 | 18 | 106 | Stench burying Anteater, Shaman (dead) in grave. |
| J19592 | E071 | 1 | 1 | A(n) gazelle consuming grass. |
| L5 | E095 | 68 | 23 | A medieval farm oaf named Ackmann is crashing in a transport pod near… |

## Concatenation order (event-first vs dialogue-first)

- Mean top-5 overlap per dialogue line: 0.82
- Overlap of the global top-14 pairs (what the game requests at share 0.5): 0.93
- Largest NCD difference between orders: 0.061

## Top 5 per dialogue line

**J197** — A(n) grizzly bear standing.

| # | ncd | embedding |
|---|---|---|
| 1 | E070 A(n) grizzly bear standing. | E070 A(n) grizzly bear standing. |
| 2 | E069 A(n) grizzly bear wandering. | E069 A(n) grizzly bear wandering. |
| 3 | E153 A(n) grizzly bear consuming area. | E153 A(n) grizzly bear consuming area. |
| 4 | E008 A(n) gazelle standing. | E029 A(n) doe standing. |
| 5 | E004 A(n) rat standing. | E035 A(n) timber wolf standing. |

**J784** — Stench hauling steel x56 to Stockpile zone 1.

| # | ncd | embedding |
|---|---|---|
| 1 | E088 Stench hauling steel x18 to Stockpile zone 1. | E088 Stench hauling steel x18 to Stockpile zone 1. |
| 2 | E090 Stench hauling silver x500 to Stockpile zone 1. | E091 Stench hauling component x30 to Stockpile zone 1. |
| 3 | E086 Stench hauling wooden club to Stockpile zone 1. | E090 Stench hauling silver x500 to Stockpile zone 1. |
| 4 | E091 Stench hauling component x30 to Stockpile zone 1. | E086 Stench hauling wooden club to Stockpile zone 1. |
| 5 | E159 Stench hauling packaged survival meal x10 to Stockpile zone… | E159 Stench hauling packaged survival meal x10 to Stockpile zone… |

**J6248** — Papyrus following Stench.

| # | ncd | embedding |
|---|---|---|
| 1 | E049 Papyrus following Stench. | E049 Papyrus following Stench. |
| 2 | E081 Stench milking Papyrus. | E081 Stench milking Papyrus. |
| 3 | E115 Odette insulting Stench. | E050 Stench leading Papyrus to wooden pen marker. |
| 4 | E010 Papyrus wandering. | E048 Papyrus resting. |
| 5 | E013 Papyrus standing. | E010 Papyrus wandering. |

**J23595** — Stench moving.

| # | ncd | embedding |
|---|---|---|
| 1 | E093 Stench hauling. | E157 Stench resting. |
| 2 | E157 Stench resting. | E093 Stench hauling. |
| 3 | E047 Stench standing. | E047 Stench standing. |
| 4 | E080 Stench cloudwatching. | E002 Stench watching for targets. |
| 5 | E039 Boyd standing. | E083 Stench building area. |

**L0** — A group of tribespeople from Confederacy of Loucó have arrived nearby. They are attacking immediately.

| # | ncd | embedding |
|---|---|---|
| 1 | E045 Boyd is wandering around in a psychotic state. This happene… | E064 A(n) turkey fleeing. |
| 2 | E052 The turkey ducked aside at the last second, Stench's bolt-a… | E017 A(n) raccoon wandering. |
| 3 | E058 Stench's bolt-action rifle bullet missed by a small margin. | E030 A(n) rhinoceros wandering. |
| 4 | E082 Stench shared views on aiding the downtrodden with Boyd. | E095 A medieval farm oaf named Ackmann is crashing in a transpor… |
| 5 | E138 Stench flailed at Odette with her left fist, but stumbled a… | E034 A(n) timber wolf wandering. |

**J11087** — Boyd relaxing socially.

| # | ncd | embedding |
|---|---|---|
| 1 | E039 Boyd standing. | E046 Boyd wandering. |
| 2 | E046 Boyd wandering. | E045 Boyd is wandering around in a psychotic state. This happene… |
| 3 | E000 Boyd watching for targets. | E039 Boyd standing. |
| 4 | E001 Odette tending to Odette. | E000 Boyd watching for targets. |
| 5 | E014 A(n) squirrel standing. | E082 Stench shared views on aiding the downtrodden with Boyd. |

**J11165** — Odette watching for targets.

| # | ncd | embedding |
|---|---|---|
| 1 | E000 Boyd watching for targets. | E001 Odette tending to Odette. |
| 2 | E002 Stench watching for targets. | E040 Odette standing. |
| 3 | E001 Odette tending to Odette. | E000 Boyd watching for targets. |
| 4 | E080 Stench cloudwatching. | E152 Odette downed. |
| 5 | E115 Odette insulting Stench. | E143 Stench tried to hit Odette, but missed. |

**b57** — Boyd fired timidly at Walrus.

| # | ncd | embedding |
|---|---|---|
| 1 | E057 Stench fired at the turkey. | E000 Boyd watching for targets. |
| 2 | E053 Stench fired her bolt-action rifle at the turkey. | E039 Boyd standing. |
| 3 | E039 Boyd standing. | E046 Boyd wandering. |
| 4 | E046 Boyd wandering. | E045 Boyd is wandering around in a psychotic state. This happene… |
| 5 | E082 Stench shared views on aiding the downtrodden with Boyd. | E053 Stench fired her bolt-action rifle at the turkey. |

**b74** — Stench hit Walrus with a shot.

| # | ncd | embedding |
|---|---|---|
| 1 | E121 Odette fighting with Stench. | E054 Stench hit the turkey with a bolt-action rifle bullet. |
| 2 | E124 Stench fighting with Odette. | E085 Stench burying Walrus, Treehouse builder (dead) in grave. |
| 3 | E141 Odette hit Stench with her left fist. | E002 Stench watching for targets. |
| 4 | E049 Papyrus following Stench. | E051 Stench shot at the turkey. |
| 5 | E051 Stench shot at the turkey. | E053 Stench fired her bolt-action rifle at the turkey. |

**b81** — Walrus died.

| # | ncd | embedding |
|---|---|---|
| 1 | E048 Papyrus resting. | E085 Stench burying Walrus, Treehouse builder (dead) in grave. |
| 2 | E013 Papyrus standing. | E052 The turkey ducked aside at the last second, Stench's bolt-a… |
| 3 | E010 Papyrus wandering. | E154 A(n) turkey downed, unconscious. |
| 4 | E039 Boyd standing. | E100 The timber wolf bit the rat. |
| 5 | E152 Odette downed. | E069 A(n) grizzly bear wandering. |

**b88** — Boyd's shot hit Anteater.

| # | ncd | embedding |
|---|---|---|
| 1 | E051 Stench shot at the turkey. | E000 Boyd watching for targets. |
| 2 | E013 Papyrus standing. | E046 Boyd wandering. |
| 3 | E031 A(n) rhinoceros standing. | E039 Boyd standing. |
| 4 | E039 Boyd standing. | E058 Stench's bolt-action rifle bullet missed by a small margin. |
| 5 | E046 Boyd wandering. | E052 The turkey ducked aside at the last second, Stench's bolt-a… |

**J19592** — A(n) gazelle consuming grass.

| # | ncd | embedding |
|---|---|---|
| 1 | E071 A(n) gazelle consuming grass. | E071 A(n) gazelle consuming grass. |
| 2 | E072 A(n) hare consuming grass. | E007 A(n) gazelle wandering. |
| 3 | E027 A(n) rat consuming grass. | E008 A(n) gazelle standing. |
| 4 | E074 A(n) turkey consuming grass. | E074 A(n) turkey consuming grass. |
| 5 | E076 A(n) raccoon consuming grass. | E068 A(n) squirrel consuming grass. |

**L5** — Chunks of a spacecraft have impacted nearby. You can deconstruct them to yield resources.

| # | ncd | embedding |
|---|---|---|
| 1 | E052 The turkey ducked aside at the last second, Stench's bolt-a… | E091 Stench hauling component x30 to Stockpile zone 1. |
| 2 | E058 Stench's bolt-action rifle bullet missed by a small margin. | E150 The turkey dropped. |
| 3 | E138 Stench flailed at Odette with her left fist, but stumbled a… | E159 Stench hauling packaged survival meal x10 to Stockpile zone… |
| 4 | E053 Stench fired her bolt-action rifle at the turkey. | E088 Stench hauling steel x18 to Stockpile zone 1. |
| 5 | E056 A(n) turkey was afflicted with (a) blood loss (minor) | E097 Stench hauling wood x7 to wooden stool (building). |

