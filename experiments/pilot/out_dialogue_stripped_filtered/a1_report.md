# A1 — Can NCD find continuity?

**Status: FAIL**

8 past dialogue lines × 162 current-session events. NCD order: `event_first` (matches the game). Pass rule: NCD mean Recall@5 >= 0.5.

**CC candidates: filtered.** The CC may only pick the 43 cluster representatives of session 2 at NCD threshold 0.5 (the AC's unique_logs_after_filtering, before traversal). A gold event folded into a cluster counts as found when its representative is retrieved; 10 of 30 gold events are representatives themselves.

## Metrics

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| ncd | 0.125 | 0.260 | 0.300 | 8 | 18 |

## Rank of each expected event

| dialogue | event | ncd rank | embedding rank | event description |
|---|---|---|---|---|
| S104 | E069 | 25 | – | A(n) grizzly bear wandering. |
| S104 | E070 → E069 | 25 | – | A(n) grizzly bear standing. |
| S104 | E088 → E090 | 11 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S104 | E153 → E069 | 25 | – | A(n) grizzly bear consuming area. |
| S107 | E045 | 25 | – | Boyd is wandering around in a psychotic state. This happened because … |
| S110 | E000 | 19 | – | Boyd watching for targets. |
| S110 | E001 → E124 | 22 | – | Odette tending to Odette. |
| S111 | E007 → E003 | 39 | – | A(n) gazelle wandering. |
| S111 | E008 → E003 | 39 | – | A(n) gazelle standing. |
| S111 | E071 → E072 | 33 | – | A(n) gazelle consuming grass. |
| S111 | E095 | 43 | – | A medieval farm oaf named Ackmann is crashing in a transport pod near… |
| S105 | E051 | 20 | – | Stench shot at the turkey. |
| S105 | E055 → E123 | 9 | – | A(n) turkey was afflicted with (a) gunshot (body) |
| S105 | E085 → E084 | 14 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E084 | 9 | – | Stench burying Anteater, Shaman (dead) in grave. |
| S108 | E085 → E084 | 9 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E135 | 1 | – | Stench missed Odette with a hit from her left fist. |
| S108 | E137 → E139 | 15 | – | Odette attempted to hit Stench, but hesitated at the last second. |
| S108 | E141 → E135 | 1 | – | Odette hit Stench with her left fist. |
| S108 | E143 → E131 | 4 | – | Stench tried to hit Odette, but missed. |
| S112 | E069 | 13 | – | A(n) grizzly bear wandering. |
| S112 | E070 → E069 | 13 | – | A(n) grizzly bear standing. |
| S112 | E153 → E069 | 13 | – | A(n) grizzly bear consuming area. |
| S106 | E050 | 7 | – | Stench leading Papyrus to wooden pen marker. |
| S106 | E086 → E090 | 1 | – | Stench hauling wooden club to Stockpile zone 1. |
| S106 | E088 → E090 | 1 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S106 | E089 → E090 | 1 | – | Stench hauling synthread pants (normal 97%) to Stockpile zone 1. |
| S106 | E090 | 1 | – | Stench hauling silver x500 to Stockpile zone 1. |
| S106 | E091 → E090 | 1 | – | Stench hauling component x30 to Stockpile zone 1. |
| S106 | E159 → E090 | 1 | – | Stench hauling packaged survival meal x10 to Stockpile zone 1. |

## Concatenation order (event-first vs dialogue-first)

- Mean top-5 overlap per dialogue line: 0.33
- Overlap of the global top-14 pairs (what the game requests at share 0.5): 0.14
- Largest NCD difference between orders: 0.146

## Top 5 per dialogue line

**S104** — Lidia 'Stench' Schmitt said 'Boyd, I had those fifty-six steel beams stashed before the grizzly settled in.'

| # | ncd |
|---|---|
| 1 | E118 Odette is no longer on an insulting spree against Stench, H… |
| 2 | E053 Stench fired her bolt-action rifle at the turkey. |
| 3 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 4 | E135 Stench missed Odette with a hit from her left fist. |
| 5 | E119 Odette called Stench a salamander. This drove Stench into a… |

**S107** — Dillon 'Boyd' Boyd said 'Stench, my hands shook when the raiders struck without warning.'

| # | ncd |
|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E053 Stench fired her bolt-action rifle at the turkey. |
| 3 | E041 Stench chatted about fighting tapirs with Odette. |
| 4 | E108 Missing a neck caused the rat to expire. |
| 5 | E131 Stench tried to smash Odette, but missed. |

**S110** — Odette 'Odette' O'Neill said 'Stench, I watched the far treeline for more raiders.'

| # | ncd |
|---|---|
| 1 | E135 Stench missed Odette with a hit from her left fist. |
| 2 | E053 Stench fired her bolt-action rifle at the turkey. |
| 3 | E041 Stench chatted about fighting tapirs with Odette. |
| 4 | E108 Missing a neck caused the rat to expire. |
| 5 | E130 Odette stumbled while trying to strike Stench. |

**S111** — Odette 'Odette' O'Neill said 'Stench, those gazelles were grazing amid the chunks of the downed spacecraft.'

| # | ncd |
|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E118 Odette is no longer on an insulting spree against Stench, H… |
| 3 | E053 Stench fired her bolt-action rifle at the turkey. |
| 4 | E135 Stench missed Odette with a hit from her left fist. |
| 5 | E041 Stench chatted about fighting tapirs with Odette. |

**S105** — Lidia 'Stench' Schmitt said 'Boyd, my shot dropped that walrus in a spray of blood.'

| # | ncd |
|---|---|
| 1 | E053 Stench fired her bolt-action rifle at the turkey. |
| 2 | E041 Stench chatted about fighting tapirs with Odette. |
| 3 | E135 Stench missed Odette with a hit from her left fist. |
| 4 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 5 | E108 Missing a neck caused the rat to expire. |

**S108** — Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, then I stung the anteater.'

| # | ncd |
|---|---|
| 1 | E135 Stench missed Odette with a hit from her left fist. |
| 2 | E053 Stench fired her bolt-action rifle at the turkey. |
| 3 | E108 Missing a neck caused the rat to expire. |
| 4 | E131 Stench tried to smash Odette, but missed. |
| 5 | E082 Stench shared views on aiding the downtrodden with Boyd. |

**S112** — Odette 'Odette' O'Neill said 'Boyd, a grizzly at camp's edge was trouble waiting to happen.'

| # | ncd |
|---|---|
| 1 | E053 Stench fired her bolt-action rifle at the turkey. |
| 2 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 3 | E123 Odette was afflicted with (a) bruise (human fist) (torso) |
| 4 | E084 Stench burying Anteater, Shaman (dead) in grave. |
| 5 | E130 Odette stumbled while trying to strike Stench. |

**S106** — Lidia 'Stench' Schmitt said 'Boyd, Papyrus trailed me all the way to Stockpile One.'

| # | ncd |
|---|---|
| 1 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| 2 | E053 Stench fired her bolt-action rifle at the turkey. |
| 3 | E135 Stench missed Odette with a hit from her left fist. |
| 4 | E130 Odette stumbled while trying to strike Stench. |
| 5 | E041 Stench chatted about fighting tapirs with Odette. |

