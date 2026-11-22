# A1 — Can NCD find continuity?

**Status: PASS**

8 past dialogue lines × 162 current-session events. NCD order: `event_first` (matches the game). Pass rule: NCD mean Recall@5 >= 0.5.

## Metrics

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| ncd | 0.571 | 0.680 | 0.647 | 8 | 30 |

## Rank of each expected event

| dialogue | event | ncd rank | embedding rank | event description |
|---|---|---|---|---|
| S104 | E069 | 3 | – | A(n) grizzly bear wandering. |
| S104 | E070 | 1 | – | A(n) grizzly bear standing. |
| S104 | E088 | 2 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S104 | E153 | 7 | – | A(n) grizzly bear consuming area. |
| S107 | E045 | 2 | – | Boyd is wandering around in a psychotic state. This happened because … |
| S110 | E000 | 1 | – | Boyd watching for targets. |
| S110 | E001 | 3 | – | Odette tending to Odette. |
| S111 | E007 | 14 | – | A(n) gazelle wandering. |
| S111 | E008 | 15 | – | A(n) gazelle standing. |
| S111 | E071 | 1 | – | A(n) gazelle consuming grass. |
| S111 | E095 | 151 | – | A medieval farm oaf named Ackmann is crashing in a transport pod near… |
| S105 | E051 | 7 | – | Stench shot at the turkey. |
| S105 | E055 | 84 | – | A(n) turkey was afflicted with (a) gunshot (body) |
| S105 | E085 | 36 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E084 | 27 | – | Stench burying Anteater, Shaman (dead) in grave. |
| S108 | E085 | 30 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E135 | 42 | – | Stench missed Odette with a hit from her left fist. |
| S108 | E137 | 102 | – | Odette attempted to hit Stench, but hesitated at the last second. |
| S108 | E141 | 45 | – | Odette hit Stench with her left fist. |
| S108 | E143 | 118 | – | Stench tried to hit Odette, but missed. |
| S112 | E069 | 2 | – | A(n) grizzly bear wandering. |
| S112 | E070 | 1 | – | A(n) grizzly bear standing. |
| S112 | E153 | 3 | – | A(n) grizzly bear consuming area. |
| S106 | E050 | 25 | – | Stench leading Papyrus to wooden pen marker. |
| S106 | E086 | 4 | – | Stench hauling wooden club to Stockpile zone 1. |
| S106 | E088 | 2 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S106 | E089 | 8 | – | Stench hauling synthread pants (normal 97%) to Stockpile zone 1. |
| S106 | E090 | 3 | – | Stench hauling silver x500 to Stockpile zone 1. |
| S106 | E091 | 5 | – | Stench hauling component x30 to Stockpile zone 1. |
| S106 | E159 | 7 | – | Stench hauling packaged survival meal x10 to Stockpile zone 1. |

## Concatenation order (event-first vs dialogue-first)

- Mean top-5 overlap per dialogue line: 0.03
- Overlap of the global top-14 pairs (what the game requests at share 0.5): 0.00
- Largest NCD difference between orders: 0.733

## Top 5 per dialogue line

**S104** — Lidia 'Stench' Schmitt said 'Boyd, I had those fifty-six steel beams stashed before the grizzly settled in.'

| # | ncd |
|---|---|
| 1 | E070 A(n) grizzly bear standing. |
| 2 | E088 Stench hauling steel x18 to Stockpile zone 1. |
| 3 | E069 A(n) grizzly bear wandering. |
| 4 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| 5 | E086 Stench hauling wooden club to Stockpile zone 1. |

**S107** — Dillon 'Boyd' Boyd said 'Stench, my hands shook when the raiders struck without warning.'

| # | ncd |
|---|---|
| 1 | E057 Stench fired at the turkey. |
| 2 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 3 | E052 The turkey ducked aside at the last second, Stench's bolt-a… |
| 4 | E053 Stench fired her bolt-action rifle at the turkey. |
| 5 | E039 Boyd standing. |

**S110** — Odette 'Odette' O'Neill said 'Stench, I watched the far treeline for more raiders.'

| # | ncd |
|---|---|
| 1 | E000 Boyd watching for targets. |
| 2 | E002 Stench watching for targets. |
| 3 | E001 Odette tending to Odette. |
| 4 | E080 Stench cloudwatching. |
| 5 | E115 Odette insulting Stench. |

**S111** — Odette 'Odette' O'Neill said 'Stench, those gazelles were grazing amid the chunks of the downed spacecraft.'

| # | ncd |
|---|---|
| 1 | E071 A(n) gazelle consuming grass. |
| 2 | E072 A(n) hare consuming grass. |
| 3 | E027 A(n) rat consuming grass. |
| 4 | E074 A(n) turkey consuming grass. |
| 5 | E076 A(n) raccoon consuming grass. |

**S105** — Lidia 'Stench' Schmitt said 'Boyd, my shot dropped that walrus in a spray of blood.'

| # | ncd |
|---|---|
| 1 | E048 Papyrus resting. |
| 2 | E121 Odette fighting with Stench. |
| 3 | E124 Stench fighting with Odette. |
| 4 | E013 Papyrus standing. |
| 5 | E141 Odette hit Stench with her left fist. |

**S108** — Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, then I stung the anteater.'

| # | ncd |
|---|---|
| 1 | E057 Stench fired at the turkey. |
| 2 | E051 Stench shot at the turkey. |
| 3 | E013 Papyrus standing. |
| 4 | E031 A(n) rhinoceros standing. |
| 5 | E039 Boyd standing. |

**S112** — Odette 'Odette' O'Neill said 'Boyd, a grizzly at camp's edge was trouble waiting to happen.'

| # | ncd |
|---|---|
| 1 | E070 A(n) grizzly bear standing. |
| 2 | E069 A(n) grizzly bear wandering. |
| 3 | E153 A(n) grizzly bear consuming area. |
| 4 | E008 A(n) gazelle standing. |
| 5 | E004 A(n) rat standing. |

**S106** — Lidia 'Stench' Schmitt said 'Boyd, Papyrus trailed me all the way to Stockpile One.'

| # | ncd |
|---|---|
| 1 | E049 Papyrus following Stench. |
| 2 | E088 Stench hauling steel x18 to Stockpile zone 1. |
| 3 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| 4 | E086 Stench hauling wooden club to Stockpile zone 1. |
| 5 | E091 Stench hauling component x30 to Stockpile zone 1. |

