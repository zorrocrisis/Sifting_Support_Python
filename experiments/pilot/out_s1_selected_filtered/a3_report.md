# A3 — Redundancy control in CC

**Status: PASS** — best variant by rule: `cap`

Share 0.5, total 12, AC seed 42, cap 2, λ 0.7. Pass rule: >= 3 relevant dialogue lines contribute (relevant = lines with gold matches).

The game's composer counts each paired dialogue line against the CC quota, so a new dialogue line costs two slots. At quota 6, at most 3 distinct dialogue lines can contribute, whatever the selector.

| variant | dialogue lines in pool | CC events | CC redundancy | pool redundancy | distinct dialogue in requested pairs | passes |
|---|---|---|---|---|---|---|
| nearest | 3 | 3 | 0.294 | 0.253 | 7 | yes |
| cap | 3 | 3 | 0.294 | 0.253 | 8 | yes |
| mmr | 3 | 3 | 0.294 | 0.255 | 8 | yes |
| cap+mmr | 3 | 3 | 0.294 | 0.255 | 9 | yes |

## `nearest` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| J6248 | 0.091 | E049 Papyrus following Stench. |
| J11165 | 0.222 | E000 Boyd watching for targets. |
| J197 | 0.250 | E069 A(n) grizzly bear wandering. |

## `cap` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| J6248 | 0.091 | E049 Papyrus following Stench. |
| J11165 | 0.222 | E000 Boyd watching for targets. |
| J197 | 0.250 | E069 A(n) grizzly bear wandering. |

## `mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| J6248 | 0.091 | E049 Papyrus following Stench. |
| J197 | 0.250 | E069 A(n) grizzly bear wandering. |
| J11165 | 0.222 | E000 Boyd watching for targets. |

## `cap+mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| J6248 | 0.091 | E049 Papyrus following Stench. |
| J197 | 0.250 | E069 A(n) grizzly bear wandering. |
| J11165 | 0.222 | E000 Boyd watching for targets. |

