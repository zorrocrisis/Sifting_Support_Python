# A1 — Can NCD find continuity?

**Status: FAIL**

8 past dialogue lines × 162 current-session events. NCD order: `event_first` (matches the game). Pass rule: NCD mean Recall@5 >= 0.5.

**CC candidates: filtered.** The CC may only pick the 43 cluster representatives of session 2 at NCD threshold 0.5 (the AC's unique_logs_after_filtering, before traversal). A gold event folded into a cluster counts as found when its representative is retrieved; 10 of 30 gold events are representatives themselves.

## Metrics

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| index | 0.219 | 0.312 | 0.272 | 8 | 18 |

**Strict scoring** (only the exact gold log counts; 10 of 30 gold events are candidates at all). Strict verdict: fail.

| method | Recall@5 | Recall@10 | MRR |
|---|---|---|---|
| index | 0.164 | 0.164 | 0.253 |

## Rank of each expected event

| dialogue | event | index rank | embedding rank | event description |
|---|---|---|---|---|
| S104 | E069 | 29 | – | A(n) grizzly bear wandering. |
| S104 | E070 → E069 | 29 | – | A(n) grizzly bear standing. |
| S104 | E088 → E090 | 11 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S104 | E153 → E069 | 29 | – | A(n) grizzly bear consuming area. |
| S107 | E045 | 3 | – | Boyd is wandering around in a psychotic state. This happened because … |
| S110 | E000 | 26 | – | Boyd watching for targets. |
| S110 | E001 → E124 | 8 | – | Odette tending to Odette. |
| S111 | E007 → E003 | 41 | – | A(n) gazelle wandering. |
| S111 | E008 → E003 | 41 | – | A(n) gazelle standing. |
| S111 | E071 → E072 | 34 | – | A(n) gazelle consuming grass. |
| S111 | E095 | 36 | – | A medieval farm oaf named Ackmann is crashing in a transport pod near… |
| S105 | E051 | 20 | – | Stench shot at the turkey. |
| S105 | E055 → E123 | 28 | – | A(n) turkey was afflicted with (a) gunshot (body) |
| S105 | E085 → E084 | 18 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E084 | 1 | – | Stench burying Anteater, Shaman (dead) in grave. |
| S108 | E085 → E084 | 1 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E135 | 12 | – | Stench missed Odette with a hit from her left fist. |
| S108 | E137 → E139 | 10 | – | Odette attempted to hit Stench, but hesitated at the last second. |
| S108 | E141 → E135 | 12 | – | Odette hit Stench with her left fist. |
| S108 | E143 → E131 | 17 | – | Stench tried to hit Odette, but missed. |
| S112 | E069 | 25 | – | A(n) grizzly bear wandering. |
| S112 | E070 → E069 | 25 | – | A(n) grizzly bear standing. |
| S112 | E153 → E069 | 25 | – | A(n) grizzly bear consuming area. |
| S106 | E050 | 2 | – | Stench leading Papyrus to wooden pen marker. |
| S106 | E086 → E090 | 23 | – | Stench hauling wooden club to Stockpile zone 1. |
| S106 | E088 → E090 | 23 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S106 | E089 → E090 | 23 | – | Stench hauling synthread pants (normal 97%) to Stockpile zone 1. |
| S106 | E090 | 23 | – | Stench hauling silver x500 to Stockpile zone 1. |
| S106 | E091 → E090 | 23 | – | Stench hauling component x30 to Stockpile zone 1. |
| S106 | E159 → E090 | 23 | – | Stench hauling packaged survival meal x10 to Stockpile zone 1. |

**CC similarity: event indexing** (entities, place, log type, NCD text; see `experiments/common/event_index.py`). The `index` method ranks by that score.

## Top 5 per dialogue line

**S104** — Lidia 'Stench' Schmitt said 'Boyd, I had those fifty-six steel beams stashed before the grizzly settled in.'

| # | index |
|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E000 Boyd watching for targets. |
| 3 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 4 | E042 Critical alert (UI notification): Major break risk |
| 5 | E097 Stench hauling wood x7 to wooden stool (building). |

**S107** — Dillon 'Boyd' Boyd said 'Stench, my hands shook when the raiders struck without warning.'

| # | index |
|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E000 Boyd watching for targets. |
| 3 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 4 | E042 Critical alert (UI notification): Major break risk |
| 5 | E097 Stench hauling wood x7 to wooden stool (building). |

**S110** — Odette 'Odette' O'Neill said 'Stench, I watched the far treeline for more raiders.'

| # | index |
|---|---|
| 1 | E118 Odette is no longer on an insulting spree against Stench, H… |
| 2 | E119 Odette called Stench a salamander. This drove Stench into a… |
| 3 | E139 Odette tried to use her right fist to hit Stench, but stumb… |
| 4 | E114 Odette flagrantly insulted Stench's leg hair. |
| 5 | E135 Stench missed Odette with a hit from her left fist. |

**S111** — Odette 'Odette' O'Neill said 'Stench, those gazelles were grazing amid the chunks of the downed spacecraft.'

| # | index |
|---|---|
| 1 | E118 Odette is no longer on an insulting spree against Stench, H… |
| 2 | E119 Odette called Stench a salamander. This drove Stench into a… |
| 3 | E139 Odette tried to use her right fist to hit Stench, but stumb… |
| 4 | E114 Odette flagrantly insulted Stench's leg hair. |
| 5 | E130 Odette stumbled while trying to strike Stench. |

**S105** — Lidia 'Stench' Schmitt said 'Boyd, my shot dropped that walrus in a spray of blood.'

| # | index |
|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 3 | E042 Critical alert (UI notification): Major break risk |
| 4 | E041 Stench chatted about fighting tapirs with Odette. |
| 5 | E000 Boyd watching for targets. |

**S108** — Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, then I stung the anteater.'

| # | index |
|---|---|
| 1 | E084 Stench burying Anteater, Shaman (dead) in grave. |
| 2 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 3 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 4 | E042 Critical alert (UI notification): Major break risk |
| 5 | E041 Stench chatted about fighting tapirs with Odette. |

**S112** — Odette 'Odette' O'Neill said 'Boyd, a grizzly at camp's edge was trouble waiting to happen.'

| # | index |
|---|---|
| 1 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 2 | E042 Critical alert (UI notification): Major break risk |
| 3 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 4 | E041 Stench chatted about fighting tapirs with Odette. |
| 5 | E000 Boyd watching for targets. |

**S106** — Lidia 'Stench' Schmitt said 'Boyd, Papyrus trailed me all the way to Stockpile One.'

| # | index |
|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E050 Stench leading Papyrus to wooden pen marker. |
| 3 | E049 Papyrus following Stench. |
| 4 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 5 | E042 Critical alert (UI notification): Major break risk |

