# A1 — Can NCD find continuity?

**Status: FAIL**

8 past dialogue lines × 162 current-session events. NCD order: `event_first` (matches the game). Pass rule: NCD mean Recall@5 >= 0.5.

## Metrics

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| ncd | 0.098 | 0.137 | 0.205 | 8 | 30 |
| embedding | 0.167 | 0.185 | 0.148 | 8 | 30 |

## Rank of each expected event

| dialogue | event | ncd rank | embedding rank | event description |
|---|---|---|---|---|
| S104 | E069 | 82 | 71 | A(n) grizzly bear wandering. |
| S104 | E070 | 83 | 88 | A(n) grizzly bear standing. |
| S104 | E088 | 49 | 11 | Stench hauling steel x18 to Stockpile zone 1. |
| S104 | E153 | 70 | 83 | A(n) grizzly bear consuming area. |
| S107 | E045 | 22 | 2 | Boyd is wandering around in a psychotic state. This happened because … |
| S110 | E000 | 77 | 64 | Boyd watching for targets. |
| S110 | E001 | 73 | 31 | Odette tending to Odette. |
| S111 | E007 | 92 | 50 | A(n) gazelle wandering. |
| S111 | E008 | 103 | 77 | A(n) gazelle standing. |
| S111 | E071 | 86 | 65 | A(n) gazelle consuming grass. |
| S111 | E095 | 102 | 82 | A medieval farm oaf named Ackmann is crashing in a transport pod near… |
| S105 | E051 | 66 | 4 | Stench shot at the turkey. |
| S105 | E055 | 43 | 20 | A(n) turkey was afflicted with (a) gunshot (body) |
| S105 | E085 | 5 | 18 | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E084 | 29 | 37 | Stench burying Anteater, Shaman (dead) in grave. |
| S108 | E085 | 10 | 47 | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E135 | 33 | 24 | Stench missed Odette with a hit from her left fist. |
| S108 | E137 | 3 | 19 | Odette attempted to hit Stench, but hesitated at the last second. |
| S108 | E141 | 58 | 16 | Odette hit Stench with her left fist. |
| S108 | E143 | 53 | 13 | Stench tried to hit Odette, but missed. |
| S112 | E069 | 75 | 22 | A(n) grizzly bear wandering. |
| S112 | E070 | 76 | 63 | A(n) grizzly bear standing. |
| S112 | E153 | 67 | 78 | A(n) grizzly bear consuming area. |
| S106 | E050 | 34 | 6 | Stench leading Papyrus to wooden pen marker. |
| S106 | E086 | 10 | 63 | Stench hauling wooden club to Stockpile zone 1. |
| S106 | E088 | 15 | 38 | Stench hauling steel x18 to Stockpile zone 1. |
| S106 | E089 | 1 | 66 | Stench hauling synthread pants (normal 97%) to Stockpile zone 1. |
| S106 | E090 | 25 | 43 | Stench hauling silver x500 to Stockpile zone 1. |
| S106 | E091 | 26 | 34 | Stench hauling component x30 to Stockpile zone 1. |
| S106 | E159 | 4 | 56 | Stench hauling packaged survival meal x10 to Stockpile zone 1. |

## Concatenation order (event-first vs dialogue-first)

- Mean top-5 overlap per dialogue line: 0.68
- Overlap of the global top-14 pairs (what the game requests at share 0.5): 0.79
- Largest NCD difference between orders: 0.058

## Top 5 per dialogue line

**S104** — Lidia 'Stench' Schmitt said 'Boyd, I had those fifty-six steel beams stashed before the grizzly settled in.'

| # | ncd | embedding |
|---|---|---|
| 1 | E052 The turkey ducked aside at the last second, Stench's bolt-a… | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E058 Stench's bolt-action rifle bullet missed by a small margin. | E046 Boyd wandering. |
| 3 | E082 Stench shared views on aiding the downtrodden with Boyd. | E053 Stench fired her bolt-action rifle at the turkey. |
| 4 | E119 Odette called Stench a salamander. This drove Stench into a… | E045 Boyd is wandering around in a psychotic state. This happene… |
| 5 | E128 Odette missed Stench with a beat from her left fist. | E054 Stench hit the turkey with a bolt-action rifle bullet. |

**S107** — Dillon 'Boyd' Boyd said 'Stench, my hands shook when the raiders struck without warning.'

| # | ncd | embedding |
|---|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E118 Odette is no longer on an insulting spree against Stench, H… | E045 Boyd is wandering around in a psychotic state. This happene… |
| 3 | E052 The turkey ducked aside at the last second, Stench's bolt-a… | E039 Boyd standing. |
| 4 | E119 Odette called Stench a salamander. This drove Stench into a… | E046 Boyd wandering. |
| 5 | E137 Odette attempted to hit Stench, but hesitated at the last s… | E000 Boyd watching for targets. |

**S110** — Odette 'Odette' O'Neill said 'Stench, I watched the far treeline for more raiders.'

| # | ncd | embedding |
|---|---|---|
| 1 | E137 Odette attempted to hit Stench, but hesitated at the last s… | E160 Stench tending to Odette. |
| 2 | E138 Stench flailed at Odette with her left fist, but stumbled a… | E124 Stench fighting with Odette. |
| 3 | E118 Odette is no longer on an insulting spree against Stench, H… | E115 Odette insulting Stench. |
| 4 | E128 Odette missed Stench with a beat from her left fist. | E121 Odette fighting with Stench. |
| 5 | E129 Stench missed Odette with a smash from her left fist. | E118 Odette is no longer on an insulting spree against Stench, H… |

**S111** — Odette 'Odette' O'Neill said 'Stench, those gazelles were grazing amid the chunks of the downed spacecraft.'

| # | ncd | embedding |
|---|---|---|
| 1 | E138 Stench flailed at Odette with her left fist, but stumbled a… | E130 Odette stumbled while trying to strike Stench. |
| 2 | E052 The turkey ducked aside at the last second, Stench's bolt-a… | E160 Stench tending to Odette. |
| 3 | E118 Odette is no longer on an insulting spree against Stench, H… | E125 Odette flailed at Stench, but stumbled at the last second. |
| 4 | E119 Odette called Stench a salamander. This drove Stench into a… | E111 Odette has fixated her rage on Stench. She will follow Sten… |
| 5 | E137 Odette attempted to hit Stench, but hesitated at the last s… | E115 Odette insulting Stench. |

**S105** — Lidia 'Stench' Schmitt said 'Boyd, my shot dropped that walrus in a spray of blood.'

| # | ncd | embedding |
|---|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. | E053 Stench fired her bolt-action rifle at the turkey. |
| 2 | E058 Stench's bolt-action rifle bullet missed by a small margin. | E054 Stench hit the turkey with a bolt-action rifle bullet. |
| 3 | E118 Odette is no longer on an insulting spree against Stench, H… | E052 The turkey ducked aside at the last second, Stench's bolt-a… |
| 4 | E052 The turkey ducked aside at the last second, Stench's bolt-a… | E051 Stench shot at the turkey. |
| 5 | E085 Stench burying Walrus, Treehouse builder (dead) in grave. | E082 Stench shared views on aiding the downtrodden with Boyd. |

**S108** — Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, then I stung the anteater.'

| # | ncd | embedding |
|---|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E118 Odette is no longer on an insulting spree against Stench, H… | E054 Stench hit the turkey with a bolt-action rifle bullet. |
| 3 | E137 Odette attempted to hit Stench, but hesitated at the last s… | E053 Stench fired her bolt-action rifle at the turkey. |
| 4 | E058 Stench's bolt-action rifle bullet missed by a small margin. | E046 Boyd wandering. |
| 5 | E119 Odette called Stench a salamander. This drove Stench into a… | E052 The turkey ducked aside at the last second, Stench's bolt-a… |

**S112** — Odette 'Odette' O'Neill said 'Boyd, a grizzly at camp's edge was trouble waiting to happen.'

| # | ncd | embedding |
|---|---|---|
| 1 | E138 Stench flailed at Odette with her left fist, but stumbled a… | E046 Boyd wandering. |
| 2 | E118 Odette is no longer on an insulting spree against Stench, H… | E039 Boyd standing. |
| 3 | E123 Odette was afflicted with (a) bruise (human fist) (torso) | E000 Boyd watching for targets. |
| 4 | E127 Odette was afflicted with (a) bruise (human fist) (right le… | E045 Boyd is wandering around in a psychotic state. This happene… |
| 5 | E140 Stench missed while trying to bash Odette with her left fis… | E001 Odette tending to Odette. |

**S106** — Lidia 'Stench' Schmitt said 'Boyd, Papyrus trailed me all the way to Stockpile One.'

| # | ncd | embedding |
|---|---|---|
| 1 | E089 Stench hauling synthread pants (normal 97%) to Stockpile zo… | E049 Papyrus following Stench. |
| 2 | E082 Stench shared views on aiding the downtrodden with Boyd. | E081 Stench milking Papyrus. |
| 3 | E138 Stench flailed at Odette with her left fist, but stumbled a… | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 4 | E159 Stench hauling packaged survival meal x10 to Stockpile zone… | E010 Papyrus wandering. |
| 5 | E052 The turkey ducked aside at the last second, Stench's bolt-a… | E048 Papyrus resting. |

