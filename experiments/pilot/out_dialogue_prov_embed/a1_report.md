# A1 — Can NCD find continuity?

**Status: PASS**

8 past dialogue lines × 162 current-session events. NCD order: `event_first` (matches the game). Pass rule: NCD mean Recall@5 >= 0.5.

## Metrics

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| embed | 0.699 | 0.784 | 0.665 | 8 | 30 |

## Rank of each expected event

| dialogue | event | embed rank | embedding rank | event description |
|---|---|---|---|---|
| S104 | E069 | 5 | – | A(n) grizzly bear wandering. |
| S104 | E070 | 1 | – | A(n) grizzly bear standing. |
| S104 | E088 | 2 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S104 | E153 | 6 | – | A(n) grizzly bear consuming area. |
| S107 | E045 | 4 | – | Boyd is wandering around in a psychotic state. This happened because … |
| S110 | E000 | 3 | – | Boyd watching for targets. |
| S110 | E001 | 1 | – | Odette tending to Odette. |
| S111 | E007 | 2 | – | A(n) gazelle wandering. |
| S111 | E008 | 3 | – | A(n) gazelle standing. |
| S111 | E071 | 1 | – | A(n) gazelle consuming grass. |
| S111 | E095 | 101 | – | A medieval farm oaf named Ackmann is crashing in a transport pod near… |
| S105 | E051 | 4 | – | Stench shot at the turkey. |
| S105 | E055 | 87 | – | A(n) turkey was afflicted with (a) gunshot (body) |
| S105 | E085 | 2 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E084 | 111 | – | Stench burying Anteater, Shaman (dead) in grave. |
| S108 | E085 | 41 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E135 | 15 | – | Stench missed Odette with a hit from her left fist. |
| S108 | E137 | 48 | – | Odette attempted to hit Stench, but hesitated at the last second. |
| S108 | E141 | 24 | – | Odette hit Stench with her left fist. |
| S108 | E143 | 17 | – | Stench tried to hit Odette, but missed. |
| S112 | E069 | 2 | – | A(n) grizzly bear wandering. |
| S112 | E070 | 1 | – | A(n) grizzly bear standing. |
| S112 | E153 | 3 | – | A(n) grizzly bear consuming area. |
| S106 | E050 | 6 | – | Stench leading Papyrus to wooden pen marker. |
| S106 | E086 | 7 | – | Stench hauling wooden club to Stockpile zone 1. |
| S106 | E088 | 2 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S106 | E089 | 11 | – | Stench hauling synthread pants (normal 97%) to Stockpile zone 1. |
| S106 | E090 | 5 | – | Stench hauling silver x500 to Stockpile zone 1. |
| S106 | E091 | 4 | – | Stench hauling component x30 to Stockpile zone 1. |
| S106 | E159 | 9 | – | Stench hauling packaged survival meal x10 to Stockpile zone 1. |

## Top 5 per dialogue line

**S104** — Lidia 'Stench' Schmitt said 'Boyd, I had those fifty-six steel beams stashed before the grizzly settled in.'

| # | embed |
|---|---|
| 1 | E070 A(n) grizzly bear standing. |
| 2 | E088 Stench hauling steel x18 to Stockpile zone 1. |
| 3 | E091 Stench hauling component x30 to Stockpile zone 1. |
| 4 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| 5 | E069 A(n) grizzly bear wandering. |

**S107** — Dillon 'Boyd' Boyd said 'Stench, my hands shook when the raiders struck without warning.'

| # | embed |
|---|---|
| 1 | E000 Boyd watching for targets. |
| 2 | E039 Boyd standing. |
| 3 | E046 Boyd wandering. |
| 4 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 5 | E053 Stench fired her bolt-action rifle at the turkey. |

**S110** — Odette 'Odette' O'Neill said 'Stench, I watched the far treeline for more raiders.'

| # | embed |
|---|---|
| 1 | E001 Odette tending to Odette. |
| 2 | E040 Odette standing. |
| 3 | E000 Boyd watching for targets. |
| 4 | E152 Odette downed. |
| 5 | E143 Stench tried to hit Odette, but missed. |

**S111** — Odette 'Odette' O'Neill said 'Stench, those gazelles were grazing amid the chunks of the downed spacecraft.'

| # | embed |
|---|---|
| 1 | E071 A(n) gazelle consuming grass. |
| 2 | E007 A(n) gazelle wandering. |
| 3 | E008 A(n) gazelle standing. |
| 4 | E074 A(n) turkey consuming grass. |
| 5 | E068 A(n) squirrel consuming grass. |

**S105** — Lidia 'Stench' Schmitt said 'Boyd, my shot dropped that walrus in a spray of blood.'

| # | embed |
|---|---|
| 1 | E054 Stench hit the turkey with a bolt-action rifle bullet. |
| 2 | E085 Stench burying Walrus, Treehouse builder (dead) in grave. |
| 3 | E002 Stench watching for targets. |
| 4 | E051 Stench shot at the turkey. |
| 5 | E053 Stench fired her bolt-action rifle at the turkey. |

**S108** — Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, then I stung the anteater.'

| # | embed |
|---|---|
| 1 | E000 Boyd watching for targets. |
| 2 | E046 Boyd wandering. |
| 3 | E039 Boyd standing. |
| 4 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 5 | E053 Stench fired her bolt-action rifle at the turkey. |

**S112** — Odette 'Odette' O'Neill said 'Boyd, a grizzly at camp's edge was trouble waiting to happen.'

| # | embed |
|---|---|
| 1 | E070 A(n) grizzly bear standing. |
| 2 | E069 A(n) grizzly bear wandering. |
| 3 | E153 A(n) grizzly bear consuming area. |
| 4 | E029 A(n) doe standing. |
| 5 | E035 A(n) timber wolf standing. |

**S106** — Lidia 'Stench' Schmitt said 'Boyd, Papyrus trailed me all the way to Stockpile One.'

| # | embed |
|---|---|
| 1 | E049 Papyrus following Stench. |
| 2 | E088 Stench hauling steel x18 to Stockpile zone 1. |
| 3 | E081 Stench milking Papyrus. |
| 4 | E091 Stench hauling component x30 to Stockpile zone 1. |
| 5 | E090 Stench hauling silver x500 to Stockpile zone 1. |

