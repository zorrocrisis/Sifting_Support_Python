# A1 — Can NCD find continuity?

**Status: PASS**

13 past dialogue lines × 162 current-session events. NCD order: `event_first` (matches the game). Pass rule: NCD mean Recall@5 >= 0.5.

## Metrics

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| index | 0.715 | 0.885 | 0.683 | 13 | 20 |

Without the 3 gold pairs whose event is the reference line's exact description repeated (sensitivity check, not the pass rule):

| method | Recall@5 | Recall@10 | MRR | dialogue lines | gold pairs |
|---|---|---|---|---|---|
| index | 0.664 | 0.864 | 0.565 | 11 | 17 |

## Rank of each expected event

| dialogue | event | index rank | embedding rank | event description |
|---|---|---|---|---|
| J197 | E070 | 1 | – | A(n) grizzly bear standing. |
| J784 | E086 | 4 | – | Stench hauling wooden club to Stockpile zone 1. |
| J784 | E088 | 1 | – | Stench hauling steel x18 to Stockpile zone 1. |
| J784 | E089 | 6 | – | Stench hauling synthread pants (normal 97%) to Stockpile zone 1. |
| J784 | E090 | 2 | – | Stench hauling silver x500 to Stockpile zone 1. |
| J784 | E091 | 3 | – | Stench hauling component x30 to Stockpile zone 1. |
| J6248 | E049 | 1 | – | Papyrus following Stench. |
| J6248 | E050 | 3 | – | Stench leading Papyrus to wooden pen marker. |
| J23595 | E002 | 5 | – | Stench watching for targets. |
| L0 | E085 | 1 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| L0 | E086 | 53 | – | Stench hauling wooden club to Stockpile zone 1. |
| J11087 | E082 | 6 | – | Stench shared views on aiding the downtrodden with Boyd. |
| J11165 | E000 | 16 | – | Boyd watching for targets. |
| J11165 | E002 | 15 | – | Stench watching for targets. |
| b57 | E085 | 1 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| b74 | E085 | 1 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| b81 | E085 | 1 | – | Stench burying Walrus, Treehouse builder (dead) in grave. |
| b88 | E084 | 3 | – | Stench burying Anteater, Shaman (dead) in grave. |
| J19592 | E071 | 1 | – | A(n) gazelle consuming grass. |
| L5 | E095 | 9 | – | A medieval farm oaf named Ackmann is crashing in a transport pod near… |

**CC similarity: event indexing** (entities, place, log type, NCD text; see `experiments/common/event_index.py`). The `index` method ranks by that score.

## Top 5 per dialogue line

**J197** — A(n) grizzly bear standing.

| # | index |
|---|---|
| 1 | E070 A(n) grizzly bear standing. |
| 2 | E153 A(n) grizzly bear consuming area. |
| 3 | E069 A(n) grizzly bear wandering. |
| 4 | E023 A(n) tortoise standing. |
| 5 | E021 A(n) tortoise wandering. |

**J784** — Stench hauling steel x56 to Stockpile zone 1.

| # | index |
|---|---|
| 1 | E088 Stench hauling steel x18 to Stockpile zone 1. |
| 2 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| 3 | E091 Stench hauling component x30 to Stockpile zone 1. |
| 4 | E086 Stench hauling wooden club to Stockpile zone 1. |
| 5 | E159 Stench hauling packaged survival meal x10 to Stockpile zone… |

**J6248** — Papyrus following Stench.

| # | index |
|---|---|
| 1 | E049 Papyrus following Stench. |
| 2 | E081 Stench milking Papyrus. |
| 3 | E050 Stench leading Papyrus to wooden pen marker. |
| 4 | E010 Papyrus wandering. |
| 5 | E013 Papyrus standing. |

**J23595** — Stench moving.

| # | index |
|---|---|
| 1 | E093 Stench hauling. |
| 2 | E080 Stench cloudwatching. |
| 3 | E047 Stench standing. |
| 4 | E157 Stench resting. |
| 5 | E002 Stench watching for targets. |

**L0** — A group of tribespeople from Confederacy of Loucó have arrived nearby. They are attacking immediately.

| # | index |
|---|---|
| 1 | E085 Stench burying Walrus, Treehouse builder (dead) in grave. |
| 2 | E084 Stench burying Anteater, Shaman (dead) in grave. |
| 3 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 4 | E146 Stench and Odette are no longer social fighting. |
| 5 | E118 Odette is no longer on an insulting spree against Stench, H… |

**J11087** — Boyd relaxing socially.

| # | index |
|---|---|
| 1 | E000 Boyd watching for targets. |
| 2 | E046 Boyd wandering. |
| 3 | E039 Boyd standing. |
| 4 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 5 | E042 Critical alert (UI notification): Major break risk |

**J11165** — Odette watching for targets.

| # | index |
|---|---|
| 1 | E001 Odette tending to Odette. |
| 2 | E152 Odette downed. |
| 3 | E040 Odette standing. |
| 4 | E123 Odette was afflicted with (a) bruise (human fist) (torso) |
| 5 | E145 Odette was afflicted with (a) bruise (human fist) (left leg) |

**b57** — Boyd fired timidly at Walrus.

| # | index |
|---|---|
| 1 | E085 Stench burying Walrus, Treehouse builder (dead) in grave. |
| 2 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 3 | E039 Boyd standing. |
| 4 | E046 Boyd wandering. |
| 5 | E042 Critical alert (UI notification): Major break risk |

**b74** — Stench hit Walrus with a shot.

| # | index |
|---|---|
| 1 | E085 Stench burying Walrus, Treehouse builder (dead) in grave. |
| 2 | E060 Stench fired her bolt-action rifle at the tortoise. |
| 3 | E062 Stench missed the tortoise. |
| 4 | E141 Odette hit Stench with her left fist. |
| 5 | E051 Stench shot at the turkey. |

**b81** — Walrus died.

| # | index |
|---|---|
| 1 | E085 Stench burying Walrus, Treehouse builder (dead) in grave. |
| 2 | E039 Boyd standing. |
| 3 | E046 Boyd wandering. |
| 4 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| 5 | E000 Boyd watching for targets. |

**b88** — Boyd's shot hit Anteater.

| # | index |
|---|---|
| 1 | E039 Boyd standing. |
| 2 | E046 Boyd wandering. |
| 3 | E084 Stench burying Anteater, Shaman (dead) in grave. |
| 4 | E000 Boyd watching for targets. |
| 5 | E042 Critical alert (UI notification): Major break risk |

**J19592** — A(n) gazelle consuming grass.

| # | index |
|---|---|
| 1 | E071 A(n) gazelle consuming grass. |
| 2 | E007 A(n) gazelle wandering. |
| 3 | E008 A(n) gazelle standing. |
| 4 | E158 A(n) doe consuming area. |
| 5 | E094 A(n) buck consuming area. |

**L5** — Chunks of a spacecraft have impacted nearby. You can deconstruct them to yield resources.

| # | index |
|---|---|
| 1 | E118 Odette is no longer on an insulting spree against Stench, H… |
| 2 | E146 Stench and Odette are no longer social fighting. |
| 3 | E045 Boyd is wandering around in a psychotic state. This happene… |
| 4 | E149 Critical alert (UI notification): Colonist needs rescue |
| 5 | E117 Stench started a social fight with Odette. |

