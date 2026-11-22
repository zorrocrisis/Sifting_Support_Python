# A3 — Redundancy control in CC

**Status: PASS** — best variant by rule: `mmr`

Share 0.5, total 12, AC seed 42, cap 2, λ 0.7. Pass rule: >= 3 relevant dialogue lines contribute (relevant = lines with gold matches).

The game's composer counts each paired dialogue line against the CC quota, so a new dialogue line costs two slots. At quota 6, at most 3 distinct dialogue lines can contribute, whatever the selector.

| variant | dialogue lines in pool | CC events | CC redundancy | pool redundancy | distinct dialogue in requested pairs | passes |
|---|---|---|---|---|---|---|
| nearest | 2 | 4 | 0.454 | 0.312 | 3 | no |
| cap | 2 | 4 | 0.472 | 0.313 | 8 | no |
| mmr | 3 | 3 | 0.384 | 0.295 | 3 | yes |
| cap+mmr | 3 | 3 | 0.384 | 0.295 | 8 | yes |

## `nearest` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S106 | 0.527 | E086 Stench hauling wooden club to Stockpile zone 1. |
| S105 | 0.536 | E146 Stench and Odette are no longer social fighting. |
| S105 | 0.544 | E053 Stench fired her bolt-action rifle at the turkey. |
| S105 | 0.554 | E132 Odette ineptly bashed Stench with her left fist. |

## `cap` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S106 | 0.527 | E086 Stench hauling wooden club to Stockpile zone 1. |
| S105 | 0.536 | E146 Stench and Odette are no longer social fighting. |
| S105 | 0.544 | E053 Stench fired her bolt-action rifle at the turkey. |
| S106 | 0.554 | E091 Stench hauling component x30 to Stockpile zone 1. |

## `mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S106 | 0.527 | E086 Stench hauling wooden club to Stockpile zone 1. |
| S107 | 0.548 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S105 | 0.557 | E056 A(n) turkey was afflicted with (a) blood loss (minor) |

## `cap+mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S106 | 0.527 | E086 Stench hauling wooden club to Stockpile zone 1. |
| S107 | 0.548 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S105 | 0.557 | E056 A(n) turkey was afflicted with (a) blood loss (minor) |

