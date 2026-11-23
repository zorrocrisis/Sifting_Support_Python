# A1 — Can NCD find continuity?

**Status: PASS**

8 past dialogue lines × 162 current-session events. NCD order: `event_first` (matches the game). Pass rule: NCD mean Recall@5 >= 0.5.

**CC candidates: filtered.** The CC may only pick the 43 cluster representatives of session 2 at NCD threshold 0.5 (the AC's unique_logs_after_filtering, before traversal). A gold event folded into a cluster counts as found when its representative is retrieved; 10 of 30 gold events are representatives themselves.

## Metrics

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| embed | 0.750 | 0.781 | 0.766 | 8 | 18 |

## Rank of each expected event

| dialogue | event | embed rank | embedding rank | event description |
|---|---|---|---|---|
| S104 | E069 | 2 | – | A(n) grizzly bear wandering. |
| S104 | E070 → E069 | 2 | – | A(n) grizzly bear standing. |
| S104 | E088 → E090 | 1 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S104 | E153 → E069 | 2 | – | A(n) grizzly bear consuming area. |
| S107 | E045 | 2 | – | Boyd is wandering around in a psychotic state. This happened because … |
| S110 | E000 | 1 | – | Boyd watching for targets. |
| S110 | E001 → E124 | 2 | – | Odette tending to Odette. |
| S111 | E007 → E003 | 2 | – | A(n) gazelle wandering. |
| S111 | E008 → E003 | 2 | – | A(n) gazelle standing. |
| S111 | E071 → E072 | 1 | – | A(n) gazelle consuming grass. |
| S111 | E095 | 22 | – | A medieval farm oaf named Ackmann is crashing in a transport pod near… |
| S105 | E051 | 1 | – | Stench shot at the turkey. |
| S105 | E055 → E123 | 41 | – | A(n) turkey was afflicted with (a) gunshot (body) |
| S105 | E085 → E084 | 14 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E084 | 31 | – | Stench burying Anteater, Shaman (dead) in grave. |
| S108 | E085 → E084 | 31 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E135 | 8 | – | Stench missed Odette with a hit from her left fist. |
| S108 | E137 → E139 | 14 | – | Odette attempted to hit Stench, but hesitated at the last second. |
| S108 | E141 → E135 | 8 | – | Odette hit Stench with her left fist. |
| S108 | E143 → E131 | 17 | – | Stench tried to hit Odette, but missed. |
| S112 | E069 | 1 | – | A(n) grizzly bear wandering. |
| S112 | E070 → E069 | 1 | – | A(n) grizzly bear standing. |
| S112 | E153 → E069 | 1 | – | A(n) grizzly bear consuming area. |
| S106 | E050 | 3 | – | Stench leading Papyrus to wooden pen marker. |
| S106 | E086 → E090 | 2 | – | Stench hauling wooden club to Stockpile zone 1. |
| S106 | E088 → E090 | 2 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S106 | E089 → E090 | 2 | – | Stench hauling synthread pants (normal 97%) to Stockpile zone 1. |
| S106 | E090 | 2 | – | Stench hauling silver x500 to Stockpile zone 1. |
| S106 | E091 → E090 | 2 | – | Stench hauling component x30 to Stockpile zone 1. |
| S106 | E159 → E090 | 2 | – | Stench hauling packaged survival meal x10 to Stockpile zone 1. |

## Top 5 per dialogue line

**S104** — Lidia 'Stench' Schmitt said 'Boyd, I had those fifty-six steel beams stashed before the grizzly settled in.'

| # | embed |
|---|---|
| 1 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| 2 | E069 A(n) grizzly bear wandering. |
| 3 | E029 A(n) doe standing. |
| 4 | E097 Stench hauling wood x7 to wooden stool (building). |
| 5 | E096 Stench harvesting area. |

**S107** — Dillon 'Boyd' Boyd said 'Stench, my hands shook when the raiders struck without warning.'

| # | embed |
|---|---|
| 1 | E000 Boyd watching for targets. |
| 2 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 3 | E053 Stench fired her bolt-action rifle at the turkey. |
| 4 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 5 | E052 The turkey ducked aside at the last second, Stench's bolt-a… |

**S110** — Odette 'Odette' O'Neill said 'Stench, I watched the far treeline for more raiders.'

| # | embed |
|---|---|
| 1 | E000 Boyd watching for targets. |
| 2 | E124 Stench fighting with Odette. |
| 3 | E147 Odette collapsed due to a bruise. |
| 4 | E130 Odette stumbled while trying to strike Stench. |
| 5 | E135 Stench missed Odette with a hit from her left fist. |

**S111** — Odette 'Odette' O'Neill said 'Stench, those gazelles were grazing amid the chunks of the downed spacecraft.'

| # | embed |
|---|---|
| 1 | E072 A(n) hare consuming grass. |
| 2 | E003 A(n) rat wandering. |
| 3 | E034 A(n) timber wolf wandering. |
| 4 | E069 A(n) grizzly bear wandering. |
| 5 | E023 A(n) tortoise standing. |

**S105** — Lidia 'Stench' Schmitt said 'Boyd, my shot dropped that walrus in a spray of blood.'

| # | embed |
|---|---|
| 1 | E051 Stench shot at the turkey. |
| 2 | E053 Stench fired her bolt-action rifle at the turkey. |
| 3 | E052 The turkey ducked aside at the last second, Stench's bolt-a… |
| 4 | E157 Stench resting. |
| 5 | E043 Stench, Hunter is fully healed. |

**S108** — Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, then I stung the anteater.'

| # | embed |
|---|---|
| 1 | E000 Boyd watching for targets. |
| 2 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 3 | E053 Stench fired her bolt-action rifle at the turkey. |
| 4 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 5 | E052 The turkey ducked aside at the last second, Stench's bolt-a… |

**S112** — Odette 'Odette' O'Neill said 'Boyd, a grizzly at camp's edge was trouble waiting to happen.'

| # | embed |
|---|---|
| 1 | E069 A(n) grizzly bear wandering. |
| 2 | E029 A(n) doe standing. |
| 3 | E034 A(n) timber wolf wandering. |
| 4 | E023 A(n) tortoise standing. |
| 5 | E030 A(n) rhinoceros wandering. |

**S106** — Lidia 'Stench' Schmitt said 'Boyd, Papyrus trailed me all the way to Stockpile One.'

| # | embed |
|---|---|
| 1 | E049 Papyrus following Stench. |
| 2 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| 3 | E050 Stench leading Papyrus to wooden pen marker. |
| 4 | E097 Stench hauling wood x7 to wooden stool (building). |
| 5 | E084 Stench burying Anteater, Shaman (dead) in grave. |

