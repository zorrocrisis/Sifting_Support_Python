# A1 — Can NCD find continuity?

**Status: PASS**

8 past dialogue lines × 162 current-session events. NCD order: `event_first` (matches the game). Pass rule: NCD mean Recall@5 >= 0.5.

**CC candidates: filtered.** The CC may only pick the 43 cluster representatives of session 2 at NCD threshold 0.5 (the AC's unique_logs_after_filtering, before traversal). A gold event folded into a cluster counts as found when its representative is retrieved; 10 of 30 gold events are representatives themselves.

## Metrics

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| index | 0.740 | 0.802 | 0.719 | 8 | 18 |

## Rank of each expected event

| dialogue | event | index rank | embedding rank | event description |
|---|---|---|---|---|
| S104 | E069 | 2 | – | A(n) grizzly bear wandering. |
| S104 | E070 → E069 | 2 | – | A(n) grizzly bear standing. |
| S104 | E088 → E090 | 1 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S104 | E153 → E069 | 2 | – | A(n) grizzly bear consuming area. |
| S107 | E045 | 4 | – | Boyd is wandering around in a psychotic state. This happened because … |
| S110 | E000 | 3 | – | Boyd watching for targets. |
| S110 | E001 → E124 | 2 | – | Odette tending to Odette. |
| S111 | E007 → E003 | 12 | – | A(n) gazelle wandering. |
| S111 | E008 → E003 | 12 | – | A(n) gazelle standing. |
| S111 | E071 → E072 | 1 | – | A(n) gazelle consuming grass. |
| S111 | E095 | 23 | – | A medieval farm oaf named Ackmann is crashing in a transport pod near… |
| S105 | E051 | 2 | – | Stench shot at the turkey. |
| S105 | E055 → E123 | 32 | – | A(n) turkey was afflicted with (a) gunshot (body) |
| S105 | E085 → E084 | 21 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E084 | 1 | – | Stench burying Anteater, Shaman (dead) in grave. |
| S108 | E085 → E084 | 1 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E135 | 6 | – | Stench missed Odette with a hit from her left fist. |
| S108 | E137 → E139 | 11 | – | Odette attempted to hit Stench, but hesitated at the last second. |
| S108 | E141 → E135 | 6 | – | Odette hit Stench with her left fist. |
| S108 | E143 → E131 | 7 | – | Stench tried to hit Odette, but missed. |
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

**CC similarity: event indexing** (entities, place, log type, NCD text; see `experiments/common/event_index.py`). The `index` method ranks by that score.

## Top 5 per dialogue line

**S104** — Lidia 'Stench' Schmitt said 'Boyd, I had those fifty-six steel beams stashed before the grizzly settled in.'

| # | index |
|---|---|
| 1 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| 2 | E069 A(n) grizzly bear wandering. |
| 3 | E097 Stench hauling wood x7 to wooden stool (building). |
| 4 | E080 Stench cloudwatching. |
| 5 | E096 Stench harvesting area. |

**S107** — Dillon 'Boyd' Boyd said 'Stench, my hands shook when the raiders struck without warning.'

| # | index |
|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E042 Critical alert (UI notification): Major break risk |
| 3 | E000 Boyd watching for targets. |
| 4 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 5 | E062 Stench missed the tortoise. |

**S110** — Odette 'Odette' O'Neill said 'Stench, I watched the far treeline for more raiders.'

| # | index |
|---|---|
| 1 | E123 Odette was afflicted with (a) bruise (human fist) (torso) |
| 2 | E124 Stench fighting with Odette. |
| 3 | E000 Boyd watching for targets. |
| 4 | E135 Stench missed Odette with a hit from her left fist. |
| 5 | E131 Stench tried to smash Odette, but missed. |

**S111** — Odette 'Odette' O'Neill said 'Stench, those gazelles were grazing amid the chunks of the downed spacecraft.'

| # | index |
|---|---|
| 1 | E072 A(n) hare consuming grass. |
| 2 | E029 A(n) doe standing. |
| 3 | E069 A(n) grizzly bear wandering. |
| 4 | E154 A(n) turkey downed, unconscious. |
| 5 | E064 A(n) turkey fleeing. |

**S105** — Lidia 'Stench' Schmitt said 'Boyd, my shot dropped that walrus in a spray of blood.'

| # | index |
|---|---|
| 1 | E062 Stench missed the tortoise. |
| 2 | E051 Stench shot at the turkey. |
| 3 | E135 Stench missed Odette with a hit from her left fist. |
| 4 | E053 Stench fired her bolt-action rifle at the turkey. |
| 5 | E131 Stench tried to smash Odette, but missed. |

**S108** — Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, then I stung the anteater.'

| # | index |
|---|---|
| 1 | E084 Stench burying Anteater, Shaman (dead) in grave. |
| 2 | E000 Boyd watching for targets. |
| 3 | E042 Critical alert (UI notification): Major break risk |
| 4 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 5 | E082 Stench shared views on aiding the downtrodden with Boyd. |

**S112** — Odette 'Odette' O'Neill said 'Boyd, a grizzly at camp's edge was trouble waiting to happen.'

| # | index |
|---|---|
| 1 | E069 A(n) grizzly bear wandering. |
| 2 | E023 A(n) tortoise standing. |
| 3 | E030 A(n) rhinoceros wandering. |
| 4 | E029 A(n) doe standing. |
| 5 | E064 A(n) turkey fleeing. |

**S106** — Lidia 'Stench' Schmitt said 'Boyd, Papyrus trailed me all the way to Stockpile One.'

| # | index |
|---|---|
| 1 | E049 Papyrus following Stench. |
| 2 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| 3 | E050 Stench leading Papyrus to wooden pen marker. |
| 4 | E097 Stench hauling wood x7 to wooden stool (building). |
| 5 | E080 Stench cloudwatching. |

