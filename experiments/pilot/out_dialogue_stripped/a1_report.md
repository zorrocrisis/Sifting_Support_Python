# A1 — Can NCD find continuity?

**Status: FAIL**

8 past dialogue lines × 162 current-session events. NCD order: `event_first` (matches the game). Pass rule: NCD mean Recall@5 >= 0.5.

## Metrics

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| ncd | 0.074 | 0.131 | 0.181 | 8 | 30 |

## Rank of each expected event

| dialogue | event | ncd rank | embedding rank | event description |
|---|---|---|---|---|
| S104 | E069 | 73 | – | A(n) grizzly bear wandering. |
| S104 | E070 | 67 | – | A(n) grizzly bear standing. |
| S104 | E088 | 54 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S104 | E153 | 63 | – | A(n) grizzly bear consuming area. |
| S107 | E045 | 77 | – | Boyd is wandering around in a psychotic state. This happened because … |
| S110 | E000 | 62 | – | Boyd watching for targets. |
| S110 | E001 | 88 | – | Odette tending to Odette. |
| S111 | E007 | 92 | – | A(n) gazelle wandering. |
| S111 | E008 | 110 | – | A(n) gazelle standing. |
| S111 | E071 | 68 | – | A(n) gazelle consuming grass. |
| S111 | E095 | 161 | – | A medieval farm oaf named Ackmann is crashing in a transport pod near… |
| S105 | E051 | 67 | – | Stench shot at the turkey. |
| S105 | E055 | 33 | – | A(n) turkey was afflicted with (a) gunshot (body) |
| S105 | E085 | 38 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E084 | 29 | – | Stench burying Anteater, Shaman (dead) in grave. |
| S108 | E085 | 24 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E135 | 3 | – | Stench missed Odette with a hit from her left fist. |
| S108 | E137 | 21 | – | Odette attempted to hit Stench, but hesitated at the last second. |
| S108 | E141 | 10 | – | Odette hit Stench with her left fist. |
| S108 | E143 | 11 | – | Stench tried to hit Odette, but missed. |
| S112 | E069 | 56 | – | A(n) grizzly bear wandering. |
| S112 | E070 | 64 | – | A(n) grizzly bear standing. |
| S112 | E153 | 52 | – | A(n) grizzly bear consuming area. |
| S106 | E050 | 24 | – | Stench leading Papyrus to wooden pen marker. |
| S106 | E086 | 1 | – | Stench hauling wooden club to Stockpile zone 1. |
| S106 | E088 | 5 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S106 | E089 | 19 | – | Stench hauling synthread pants (normal 97%) to Stockpile zone 1. |
| S106 | E090 | 6 | – | Stench hauling silver x500 to Stockpile zone 1. |
| S106 | E091 | 2 | – | Stench hauling component x30 to Stockpile zone 1. |
| S106 | E159 | 8 | – | Stench hauling packaged survival meal x10 to Stockpile zone 1. |

## Concatenation order (event-first vs dialogue-first)

- Mean top-5 overlap per dialogue line: 0.15
- Overlap of the global top-14 pairs (what the game requests at share 0.5): 0.07
- Largest NCD difference between orders: 0.146

## Top 5 per dialogue line

**S104** — Lidia 'Stench' Schmitt said 'Boyd, I had those fifty-six steel beams stashed before the grizzly settled in.'

| # | ncd |
|---|---|
| 1 | E058 Stench's bolt-action rifle bullet missed by a small margin. |
| 2 | E138 Stench flailed at Odette with her left fist, but stumbled a… |
| 3 | E118 Odette is no longer on an insulting spree against Stench, H… |
| 4 | E128 Odette missed Stench with a beat from her left fist. |
| 5 | E140 Stench missed while trying to bash Odette with her left fis… |

**S107** — Dillon 'Boyd' Boyd said 'Stench, my hands shook when the raiders struck without warning.'

| # | ncd |
|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E053 Stench fired her bolt-action rifle at the turkey. |
| 3 | E146 Stench and Odette are no longer social fighting. |
| 4 | E041 Stench chatted about fighting tapirs with Odette. |
| 5 | E060 Stench fired her bolt-action rifle at the tortoise. |

**S110** — Odette 'Odette' O'Neill said 'Stench, I watched the far treeline for more raiders.'

| # | ncd |
|---|---|
| 1 | E135 Stench missed Odette with a hit from her left fist. |
| 2 | E128 Odette missed Stench with a beat from her left fist. |
| 3 | E132 Odette ineptly bashed Stench with her left fist. |
| 4 | E146 Stench and Odette are no longer social fighting. |
| 5 | E129 Stench missed Odette with a smash from her left fist. |

**S111** — Odette 'Odette' O'Neill said 'Stench, those gazelles were grazing amid the chunks of the downed spacecraft.'

| # | ncd |
|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E159 Stench hauling packaged survival meal x10 to Stockpile zone… |
| 3 | E054 Stench hit the turkey with a bolt-action rifle bullet. |
| 4 | E118 Odette is no longer on an insulting spree against Stench, H… |
| 5 | E138 Stench flailed at Odette with her left fist, but stumbled a… |

**S105** — Lidia 'Stench' Schmitt said 'Boyd, my shot dropped that walrus in a spray of blood.'

| # | ncd |
|---|---|
| 1 | E146 Stench and Odette are no longer social fighting. |
| 2 | E053 Stench fired her bolt-action rifle at the turkey. |
| 3 | E041 Stench chatted about fighting tapirs with Odette. |
| 4 | E132 Odette ineptly bashed Stench with her left fist. |
| 5 | E056 A(n) turkey was afflicted with (a) blood loss (minor) |

**S108** — Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, then I stung the anteater.'

| # | ncd |
|---|---|
| 1 | E122 Stench smashed Odette with her left fist. |
| 2 | E126 Stench slammed Odette with her left fist. |
| 3 | E135 Stench missed Odette with a hit from her left fist. |
| 4 | E132 Odette ineptly bashed Stench with her left fist. |
| 5 | E054 Stench hit the turkey with a bolt-action rifle bullet. |

**S112** — Odette 'Odette' O'Neill said 'Boyd, a grizzly at camp's edge was trouble waiting to happen.'

| # | ncd |
|---|---|
| 1 | E056 A(n) turkey was afflicted with (a) blood loss (minor) |
| 2 | E103 A(n) rat was afflicted with (a) Bitten out (right eye) |
| 3 | E055 A(n) turkey was afflicted with (a) gunshot (body) |
| 4 | E102 A(n) rat was afflicted with (a) Bitten out (left eye) |
| 5 | E107 A(n) rat was afflicted with (a) Bitten off (jaw) |

**S106** — Lidia 'Stench' Schmitt said 'Boyd, Papyrus trailed me all the way to Stockpile One.'

| # | ncd |
|---|---|
| 1 | E086 Stench hauling wooden club to Stockpile zone 1. |
| 2 | E091 Stench hauling component x30 to Stockpile zone 1. |
| 3 | E132 Odette ineptly bashed Stench with her left fist. |
| 4 | E129 Stench missed Odette with a smash from her left fist. |
| 5 | E088 Stench hauling steel x18 to Stockpile zone 1. |

