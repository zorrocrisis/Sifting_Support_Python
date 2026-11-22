# A3 — Redundancy control in CC

**Status: FAIL** — best variant by rule: `cap`

Share 0.5, total 12, AC seed 42, cap 2, λ 0.7. Pass rule: >= 3 relevant dialogue lines contribute (relevant = lines with gold matches).

The game's composer counts each paired dialogue line against the CC quota, so a new dialogue line costs two slots. At quota 6, at most 3 distinct dialogue lines can contribute, whatever the selector.

| variant | dialogue lines in pool | CC events | CC redundancy | pool redundancy | distinct dialogue in requested pairs | passes |
|---|---|---|---|---|---|---|
| nearest | 2 | 4 | 0.268 | 0.230 | 3 | no |
| cap | 2 | 4 | 0.259 | 0.228 | 8 | no |
| mmr | 2 | 4 | 0.268 | 0.230 | 3 | no |
| cap+mmr | 2 | 4 | 0.268 | 0.230 | 8 | no |
| mmr_ix | 2 | 4 | 0.268 | 0.230 | 3 | no |
| cap+mmr_ix | 2 | 4 | 0.268 | 0.230 | 7 | no |

## `nearest` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S106 | 0.081 | E049 Papyrus following Stench. |
| S106 | 0.117 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| S106 | 0.244 | E050 Stench leading Papyrus to wooden pen marker. |
| S104 | 0.258 | E069 A(n) grizzly bear wandering. |

## `cap` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S106 | 0.081 | E049 Papyrus following Stench. |
| S106 | 0.117 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| S104 | 0.258 | E069 A(n) grizzly bear wandering. |
| S104 | 0.268 | E097 Stench hauling wood x7 to wooden stool (building). |

## `mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S106 | 0.081 | E049 Papyrus following Stench. |
| S104 | 0.117 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| S104 | 0.258 | E069 A(n) grizzly bear wandering. |
| S106 | 0.244 | E050 Stench leading Papyrus to wooden pen marker. |

## `cap+mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S106 | 0.081 | E049 Papyrus following Stench. |
| S104 | 0.117 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| S104 | 0.258 | E069 A(n) grizzly bear wandering. |
| S106 | 0.244 | E050 Stench leading Papyrus to wooden pen marker. |

## `mmr_ix` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S106 | 0.081 | E049 Papyrus following Stench. |
| S104 | 0.117 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| S104 | 0.258 | E069 A(n) grizzly bear wandering. |
| S106 | 0.244 | E050 Stench leading Papyrus to wooden pen marker. |

## `cap+mmr_ix` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S106 | 0.081 | E049 Papyrus following Stench. |
| S104 | 0.117 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| S104 | 0.258 | E069 A(n) grizzly bear wandering. |
| S106 | 0.244 | E050 Stench leading Papyrus to wooden pen marker. |

