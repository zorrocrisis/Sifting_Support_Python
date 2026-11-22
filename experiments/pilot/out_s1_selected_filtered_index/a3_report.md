# A3 — Redundancy control in CC

**Status: PASS** — best variant by rule: `mmr_ix`

Share 0.5, total 12, AC seed 42, cap 2, λ 0.7. Pass rule: >= 3 relevant dialogue lines contribute (relevant = lines with gold matches).

The game's composer counts each paired dialogue line against the CC quota, so a new dialogue line costs two slots. At quota 6, at most 3 distinct dialogue lines can contribute, whatever the selector.

| variant | dialogue lines in pool | CC events | CC redundancy | pool redundancy | distinct dialogue in requested pairs | passes |
|---|---|---|---|---|---|---|
| nearest | 3 | 3 | 0.323 | 0.273 | 5 | yes |
| cap | 3 | 3 | 0.323 | 0.273 | 8 | yes |
| mmr | 3 | 3 | 0.281 | 0.259 | 6 | yes |
| cap+mmr | 3 | 3 | 0.281 | 0.259 | 7 | yes |
| mmr_ix | 3 | 3 | 0.241 | 0.253 | 6 | yes |
| cap+mmr_ix | 3 | 3 | 0.241 | 0.253 | 8 | yes |

## `nearest` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| J6248 | 0.081 | E049 Papyrus following Stench. |
| J784 | 0.117 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| J23595 | 0.178 | E080 Stench cloudwatching. |

## `cap` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| J6248 | 0.081 | E049 Papyrus following Stench. |
| J784 | 0.117 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| J23595 | 0.178 | E080 Stench cloudwatching. |

## `mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| J6248 | 0.081 | E049 Papyrus following Stench. |
| J784 | 0.117 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| J11087 | 0.202 | E000 Boyd watching for targets. |

## `cap+mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| J6248 | 0.081 | E049 Papyrus following Stench. |
| J784 | 0.117 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| J11087 | 0.202 | E000 Boyd watching for targets. |

## `mmr_ix` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| J6248 | 0.081 | E049 Papyrus following Stench. |
| J784 | 0.117 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| J197 | 0.258 | E069 A(n) grizzly bear wandering. |

## `cap+mmr_ix` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| J6248 | 0.081 | E049 Papyrus following Stench. |
| J784 | 0.117 | E090 Stench hauling silver x500 to Stockpile zone 1. |
| J197 | 0.258 | E069 A(n) grizzly bear wandering. |

