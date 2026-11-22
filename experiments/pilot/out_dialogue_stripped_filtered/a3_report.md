# A3 — Redundancy control in CC

**Status: PASS** — best variant by rule: `mmr`

Share 0.5, total 12, AC seed 42, cap 2, λ 0.7. Pass rule: >= 3 relevant dialogue lines contribute (relevant = lines with gold matches).

The game's composer counts each paired dialogue line against the CC quota, so a new dialogue line costs two slots. At quota 6, at most 3 distinct dialogue lines can contribute, whatever the selector.

| variant | dialogue lines in pool | CC events | CC redundancy | pool redundancy | distinct dialogue in requested pairs | passes |
|---|---|---|---|---|---|---|
| nearest | 2 | 4 | 0.473 | 0.309 | 4 | no |
| cap | 2 | 4 | 0.432 | 0.303 | 8 | no |
| mmr | 3 | 3 | 0.378 | 0.261 | 4 | yes |
| cap+mmr | 3 | 3 | 0.378 | 0.261 | 8 | yes |

## `nearest` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S105 | 0.544 | E053 Stench fired her bolt-action rifle at the turkey. |
| S107 | 0.548 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S105 | 0.554 | E041 Stench chatted about fighting tapirs with Odette. |
| S105 | 0.561 | E135 Stench missed Odette with a hit from her left fist. |

## `cap` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S105 | 0.544 | E053 Stench fired her bolt-action rifle at the turkey. |
| S107 | 0.548 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S105 | 0.554 | E041 Stench chatted about fighting tapirs with Odette. |
| S107 | 0.583 | E108 Missing a neck caused the rat to expire. |

## `mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S105 | 0.544 | E053 Stench fired her bolt-action rifle at the turkey. |
| S106 | 0.564 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| S107 | 0.583 | E108 Missing a neck caused the rat to expire. |

## `cap+mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S105 | 0.544 | E053 Stench fired her bolt-action rifle at the turkey. |
| S106 | 0.564 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| S107 | 0.583 | E108 Missing a neck caused the rat to expire. |

