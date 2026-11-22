# A1 — Can NCD find continuity?

**Status: FAIL**

8 past dialogue lines × 162 current-session events. NCD order: `event_first` (matches the game). Pass rule: NCD mean Recall@5 >= 0.5.

## Metrics

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| index | 0.467 | 0.781 | 0.810 | 8 | 30 |

## Rank of each expected event

| dialogue | event | index rank | embedding rank | event description |
|---|---|---|---|---|
| S104 | E069 | 10 | – | A(n) grizzly bear wandering. |
| S104 | E070 | 7 | – | A(n) grizzly bear standing. |
| S104 | E088 | 1 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S104 | E153 | 9 | – | A(n) grizzly bear consuming area. |
| S107 | E045 | 7 | – | Boyd is wandering around in a psychotic state. This happened because … |
| S110 | E000 | 16 | – | Boyd watching for targets. |
| S110 | E001 | 1 | – | Odette tending to Odette. |
| S111 | E007 | 2 | – | A(n) gazelle wandering. |
| S111 | E008 | 3 | – | A(n) gazelle standing. |
| S111 | E071 | 1 | – | A(n) gazelle consuming grass. |
| S111 | E095 | 102 | – | A medieval farm oaf named Ackmann is crashing in a transport pod near… |
| S105 | E051 | 6 | – | Stench shot at the turkey. |
| S105 | E055 | 59 | – | A(n) turkey was afflicted with (a) gunshot (body) |
| S105 | E085 | 1 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E084 | 3 | – | Stench burying Anteater, Shaman (dead) in grave. |
| S108 | E085 | 4 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| S108 | E135 | 15 | – | Stench missed Odette with a hit from her left fist. |
| S108 | E137 | 20 | – | Odette attempted to hit Stench, but hesitated at the last second. |
| S108 | E141 | 14 | – | Odette hit Stench with her left fist. |
| S108 | E143 | 13 | – | Stench tried to hit Odette, but missed. |
| S112 | E069 | 3 | – | A(n) grizzly bear wandering. |
| S112 | E070 | 1 | – | A(n) grizzly bear standing. |
| S112 | E153 | 2 | – | A(n) grizzly bear consuming area. |
| S106 | E050 | 10 | – | Stench leading Papyrus to wooden pen marker. |
| S106 | E086 | 5 | – | Stench hauling wooden club to Stockpile zone 1. |
| S106 | E088 | 1 | – | Stench hauling steel x18 to Stockpile zone 1. |
| S106 | E089 | 7 | – | Stench hauling synthread pants (normal 97%) to Stockpile zone 1. |
| S106 | E090 | 3 | – | Stench hauling silver x500 to Stockpile zone 1. |
| S106 | E091 | 4 | – | Stench hauling component x30 to Stockpile zone 1. |
| S106 | E159 | 6 | – | Stench hauling packaged survival meal x10 to Stockpile zone 1. |

**CC similarity: event indexing** (entities, place, log type, NCD text; see `experiments/common/event_index.py`). The `index` method ranks by that score.

## Top 5 per dialogue line

**S104** — Lidia 'Stench' Schmitt said 'Boyd, I had those fifty-six steel beams stashed before the grizzly settled in.'

| # | index |
|---|---|
| 1 | E088 Stench hauling steel x18 to Stockpile zone 1. |
| 2 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| 3 | E091 Stench hauling component x30 to Stockpile zone 1. |
| 4 | E086 Stench hauling wooden club to Stockpile zone 1. |
| 5 | E159 Stench hauling packaged survival meal x10 to Stockpile zone… |

**S107** — Dillon 'Boyd' Boyd said 'Stench, my hands shook when the raiders struck without warning.'

| # | index |
|---|---|
| 1 | E085 Stench burying Walrus, Treehouse builder (dead) in grave. |
| 2 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 3 | E039 Boyd standing. |
| 4 | E046 Boyd wandering. |
| 5 | E042 Critical alert (UI notification): Major break risk |

**S110** — Odette 'Odette' O'Neill said 'Stench, I watched the far treeline for more raiders.'

| # | index |
|---|---|
| 1 | E001 Odette tending to Odette. |
| 2 | E152 Odette downed. |
| 3 | E040 Odette standing. |
| 4 | E123 Odette was afflicted with (a) bruise (human fist) (torso) |
| 5 | E145 Odette was afflicted with (a) bruise (human fist) (left leg) |

**S111** — Odette 'Odette' O'Neill said 'Stench, those gazelles were grazing amid the chunks of the downed spacecraft.'

| # | index |
|---|---|
| 1 | E071 A(n) gazelle consuming grass. |
| 2 | E007 A(n) gazelle wandering. |
| 3 | E008 A(n) gazelle standing. |
| 4 | E158 A(n) doe consuming area. |
| 5 | E094 A(n) buck consuming area. |

**S105** — Lidia 'Stench' Schmitt said 'Boyd, my shot dropped that walrus in a spray of blood.'

| # | index |
|---|---|
| 1 | E085 Stench burying Walrus, Treehouse builder (dead) in grave. |
| 2 | E060 Stench fired her bolt-action rifle at the tortoise. |
| 3 | E062 Stench missed the tortoise. |
| 4 | E039 Boyd standing. |
| 5 | E141 Odette hit Stench with her left fist. |

**S108** — Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, then I stung the anteater.'

| # | index |
|---|---|
| 1 | E039 Boyd standing. |
| 2 | E046 Boyd wandering. |
| 3 | E084 Stench burying Anteater, Shaman (dead) in grave. |
| 4 | E085 Stench burying Walrus, Treehouse builder (dead) in grave. |
| 5 | E000 Boyd watching for targets. |

**S112** — Odette 'Odette' O'Neill said 'Boyd, a grizzly at camp's edge was trouble waiting to happen.'

| # | index |
|---|---|
| 1 | E070 A(n) grizzly bear standing. |
| 2 | E153 A(n) grizzly bear consuming area. |
| 3 | E069 A(n) grizzly bear wandering. |
| 4 | E023 A(n) tortoise standing. |
| 5 | E021 A(n) tortoise wandering. |

**S106** — Lidia 'Stench' Schmitt said 'Boyd, Papyrus trailed me all the way to Stockpile One.'

| # | index |
|---|---|
| 1 | E088 Stench hauling steel x18 to Stockpile zone 1. |
| 2 | E049 Papyrus following Stench. |
| 3 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| 4 | E091 Stench hauling component x30 to Stockpile zone 1. |
| 5 | E086 Stench hauling wooden club to Stockpile zone 1. |

