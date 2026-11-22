# A1 — Can NCD find continuity?

**Status: FAIL**

8 past dialogue lines × 162 current-session events. NCD order: `event_first` (matches the game). Pass rule: NCD mean Recall@5 >= 0.5.

## Metrics

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| embed | 0.167 | 0.185 | 0.148 | 8 | 30 |

## Rank of each expected event

| dialogue | event | embed rank | embedding rank | event description |
|---|---|---|---|---|
| S104 | E069 | 71 | – | A(n) grizzly bear wandering. |
| S104 | E070 | 88 | – | A(n) grizzly bear standing. |
| S104 | E088 | 11 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S104 | E153 | 83 | – | A(n) grizzly bear consuming area. |
| S107 | E045 | 2 | – | Boyd is wandering around in a psychotic state. This happened because … |
| S110 | E000 | 64 | – | Boyd watching for targets. |
| S110 | E001 | 31 | – | Odette tending to Odette. |
| S111 | E007 | 50 | – | A(n) gazelle wandering. |
| S111 | E008 | 77 | – | A(n) gazelle standing. |
| S111 | E071 | 65 | – | A(n) gazelle consuming grass. |
| S111 | E095 | 82 | – | A medieval farm oaf named Ackmann is crashing in a transport pod near… |
| S105 | E051 | 4 | – | Stench shot at the turkey. |
| S105 | E055 | 20 | – | A(n) turkey was afflicted with (a) gunshot (body) |
| S105 | E085 | 18 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E084 | 37 | – | Stench burying Anteater, Shaman (dead) in grave. |
| S108 | E085 | 47 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E135 | 24 | – | Stench missed Odette with a hit from her left fist. |
| S108 | E137 | 19 | – | Odette attempted to hit Stench, but hesitated at the last second. |
| S108 | E141 | 16 | – | Odette hit Stench with her left fist. |
| S108 | E143 | 13 | – | Stench tried to hit Odette, but missed. |
| S112 | E069 | 22 | – | A(n) grizzly bear wandering. |
| S112 | E070 | 63 | – | A(n) grizzly bear standing. |
| S112 | E153 | 78 | – | A(n) grizzly bear consuming area. |
| S106 | E050 | 6 | – | Stench leading Papyrus to wooden pen marker. |
| S106 | E086 | 63 | – | Stench hauling wooden club to Stockpile zone 1. |
| S106 | E088 | 38 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S106 | E089 | 66 | – | Stench hauling synthread pants (normal 97%) to Stockpile zone 1. |
| S106 | E090 | 43 | – | Stench hauling silver x500 to Stockpile zone 1. |
| S106 | E091 | 34 | – | Stench hauling component x30 to Stockpile zone 1. |
| S106 | E159 | 56 | – | Stench hauling packaged survival meal x10 to Stockpile zone 1. |

## Top 5 per dialogue line

**S104** — Lidia 'Stench' Schmitt said 'Boyd, I had those fifty-six steel beams stashed before the grizzly settled in.'

| # | embed |
|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E046 Boyd wandering. |
| 3 | E053 Stench fired her bolt-action rifle at the turkey. |
| 4 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 5 | E054 Stench hit the turkey with a bolt-action rifle bullet. |

**S107** — Dillon 'Boyd' Boyd said 'Stench, my hands shook when the raiders struck without warning.'

| # | embed |
|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 3 | E039 Boyd standing. |
| 4 | E046 Boyd wandering. |
| 5 | E000 Boyd watching for targets. |

**S110** — Odette 'Odette' O'Neill said 'Stench, I watched the far treeline for more raiders.'

| # | embed |
|---|---|
| 1 | E160 Stench tending to Odette. |
| 2 | E124 Stench fighting with Odette. |
| 3 | E115 Odette insulting Stench. |
| 4 | E121 Odette fighting with Stench. |
| 5 | E118 Odette is no longer on an insulting spree against Stench, H… |

**S111** — Odette 'Odette' O'Neill said 'Stench, those gazelles were grazing amid the chunks of the downed spacecraft.'

| # | embed |
|---|---|
| 1 | E130 Odette stumbled while trying to strike Stench. |
| 2 | E160 Stench tending to Odette. |
| 3 | E125 Odette flailed at Stench, but stumbled at the last second. |
| 4 | E111 Odette has fixated her rage on Stench. She will follow Sten… |
| 5 | E115 Odette insulting Stench. |

**S105** — Lidia 'Stench' Schmitt said 'Boyd, my shot dropped that walrus in a spray of blood.'

| # | embed |
|---|---|
| 1 | E053 Stench fired her bolt-action rifle at the turkey. |
| 2 | E054 Stench hit the turkey with a bolt-action rifle bullet. |
| 3 | E052 The turkey ducked aside at the last second, Stench's bolt-a… |
| 4 | E051 Stench shot at the turkey. |
| 5 | E082 Stench shared views on aiding the downtrodden with Boyd. |

**S108** — Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, then I stung the anteater.'

| # | embed |
|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E054 Stench hit the turkey with a bolt-action rifle bullet. |
| 3 | E053 Stench fired her bolt-action rifle at the turkey. |
| 4 | E046 Boyd wandering. |
| 5 | E052 The turkey ducked aside at the last second, Stench's bolt-a… |

**S112** — Odette 'Odette' O'Neill said 'Boyd, a grizzly at camp's edge was trouble waiting to happen.'

| # | embed |
|---|---|
| 1 | E046 Boyd wandering. |
| 2 | E039 Boyd standing. |
| 3 | E000 Boyd watching for targets. |
| 4 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 5 | E001 Odette tending to Odette. |

**S106** — Lidia 'Stench' Schmitt said 'Boyd, Papyrus trailed me all the way to Stockpile One.'

| # | embed |
|---|---|
| 1 | E049 Papyrus following Stench. |
| 2 | E081 Stench milking Papyrus. |
| 3 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 4 | E010 Papyrus wandering. |
| 5 | E048 Papyrus resting. |

