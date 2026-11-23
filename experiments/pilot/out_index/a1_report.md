# A1 — Can NCD find continuity?

**Status: FAIL**

8 past dialogue lines × 162 current-session events. NCD order: `event_first` (matches the game). Pass rule: NCD mean Recall@5 >= 0.5.

## Metrics

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| index | 0.226 | 0.226 | 0.366 | 8 | 30 |

## Rank of each expected event

| dialogue | event | index rank | embedding rank | event description |
|---|---|---|---|---|
| S104 | E069 | 82 | – | A(n) grizzly bear wandering. |
| S104 | E070 | 83 | – | A(n) grizzly bear standing. |
| S104 | E088 | 31 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S104 | E153 | 78 | – | A(n) grizzly bear consuming area. |
| S107 | E045 | 3 | – | Boyd is wandering around in a psychotic state. This happened because … |
| S110 | E000 | 74 | – | Boyd watching for targets. |
| S110 | E001 | 31 | – | Odette tending to Odette. |
| S111 | E007 | 59 | – | A(n) gazelle wandering. |
| S111 | E008 | 64 | – | A(n) gazelle standing. |
| S111 | E071 | 58 | – | A(n) gazelle consuming grass. |
| S111 | E095 | 128 | – | A medieval farm oaf named Ackmann is crashing in a transport pod near… |
| S105 | E051 | 46 | – | Stench shot at the turkey. |
| S105 | E055 | 85 | – | A(n) turkey was afflicted with (a) gunshot (body) |
| S105 | E085 | 1 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E084 | 1 | – | Stench burying Anteater, Shaman (dead) in grave. |
| S108 | E085 | 2 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E135 | 28 | – | Stench missed Odette with a hit from her left fist. |
| S108 | E137 | 12 | – | Odette attempted to hit Stench, but hesitated at the last second. |
| S108 | E141 | 41 | – | Odette hit Stench with her left fist. |
| S108 | E143 | 39 | – | Stench tried to hit Odette, but missed. |
| S112 | E069 | 71 | – | A(n) grizzly bear wandering. |
| S112 | E070 | 72 | – | A(n) grizzly bear standing. |
| S112 | E153 | 63 | – | A(n) grizzly bear consuming area. |
| S106 | E050 | 2 | – | Stench leading Papyrus to wooden pen marker. |
| S106 | E086 | 60 | – | Stench hauling wooden club to Stockpile zone 1. |
| S106 | E088 | 56 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S106 | E089 | 46 | – | Stench hauling synthread pants (normal 97%) to Stockpile zone 1. |
| S106 | E090 | 55 | – | Stench hauling silver x500 to Stockpile zone 1. |
| S106 | E091 | 62 | – | Stench hauling component x30 to Stockpile zone 1. |
| S106 | E159 | 51 | – | Stench hauling packaged survival meal x10 to Stockpile zone 1. |

**CC similarity: event indexing** (entities, place, log type, NCD text; see `experiments/common/event_index.py`). The `index` method ranks by that score.

## Top 5 per dialogue line

**S104** — Lidia 'Stench' Schmitt said 'Boyd, I had those fifty-six steel beams stashed before the grizzly settled in.'

| # | index |
|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E000 Boyd watching for targets. |
| 3 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 4 | E042 Critical alert (UI notification): Major break risk |
| 5 | E002 Stench watching for targets. |

**S107** — Dillon 'Boyd' Boyd said 'Stench, my hands shook when the raiders struck without warning.'

| # | index |
|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E000 Boyd watching for targets. |
| 3 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 4 | E042 Critical alert (UI notification): Major break risk |
| 5 | E046 Boyd wandering. |

**S110** — Odette 'Odette' O'Neill said 'Stench, I watched the far treeline for more raiders.'

| # | index |
|---|---|
| 1 | E118 Odette is no longer on an insulting spree against Stench, H… |
| 2 | E137 Odette attempted to hit Stench, but hesitated at the last s… |
| 3 | E128 Odette missed Stench with a beat from her left fist. |
| 4 | E138 Stench flailed at Odette with her left fist, but stumbled a… |
| 5 | E119 Odette called Stench a salamander. This drove Stench into a… |

**S111** — Odette 'Odette' O'Neill said 'Stench, those gazelles were grazing amid the chunks of the downed spacecraft.'

| # | index |
|---|---|
| 1 | E118 Odette is no longer on an insulting spree against Stench, H… |
| 2 | E119 Odette called Stench a salamander. This drove Stench into a… |
| 3 | E138 Stench flailed at Odette with her left fist, but stumbled a… |
| 4 | E137 Odette attempted to hit Stench, but hesitated at the last s… |
| 5 | E144 Odette attempted to use her right fist to beat Stench, but … |

**S105** — Lidia 'Stench' Schmitt said 'Boyd, my shot dropped that walrus in a spray of blood.'

| # | index |
|---|---|
| 1 | E085 Stench burying Walrus, Treehouse builder (dead) in grave. |
| 2 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 3 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 4 | E042 Critical alert (UI notification): Major break risk |
| 5 | E046 Boyd wandering. |

**S108** — Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, then I stung the anteater.'

| # | index |
|---|---|
| 1 | E084 Stench burying Anteater, Shaman (dead) in grave. |
| 2 | E085 Stench burying Walrus, Treehouse builder (dead) in grave. |
| 3 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 4 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 5 | E042 Critical alert (UI notification): Major break risk |

**S112** — Odette 'Odette' O'Neill said 'Boyd, a grizzly at camp's edge was trouble waiting to happen.'

| # | index |
|---|---|
| 1 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 2 | E042 Critical alert (UI notification): Major break risk |
| 3 | E046 Boyd wandering. |
| 4 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 5 | E041 Stench chatted about fighting tapirs with Odette. |

**S106** — Lidia 'Stench' Schmitt said 'Boyd, Papyrus trailed me all the way to Stockpile One.'

| # | index |
|---|---|
| 1 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 2 | E050 Stench leading Papyrus to wooden pen marker. |
| 3 | E049 Papyrus following Stench. |
| 4 | E081 Stench milking Papyrus. |
| 5 | E045 Boyd is wandering around in a psychotic state. This happene… |

