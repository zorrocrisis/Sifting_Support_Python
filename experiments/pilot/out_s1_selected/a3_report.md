# A3 — Redundancy control in CC

**Status: PASS** — best variant by rule: `cap`

Share 0.5, total 12, AC seed 42, cap 2, λ 0.7. Pass rule: >= 3 relevant dialogue lines contribute (relevant = lines with gold matches).

The game's composer counts each paired dialogue line against the CC quota, so a new dialogue line costs two slots. At quota 6, at most 3 distinct dialogue lines can contribute, whatever the selector.

| variant | dialogue lines in pool | CC events | CC redundancy | pool redundancy | distinct dialogue in requested pairs | passes |
|---|---|---|---|---|---|---|
| nearest | 3 | 3 | 0.302 | 0.279 | 5 | yes |
| cap | 3 | 3 | 0.302 | 0.279 | 8 | yes |
| mmr | 3 | 3 | 0.302 | 0.279 | 6 | yes |
| cap+mmr | 3 | 3 | 0.302 | 0.279 | 8 | yes |

## `nearest` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| J19592 | 0.081 | E071 A(n) gazelle consuming grass. |
| J197 | 0.086 | E070 A(n) grizzly bear standing. |
| J6248 | 0.091 | E049 Papyrus following Stench. |

## `cap` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| J19592 | 0.081 | E071 A(n) gazelle consuming grass. |
| J197 | 0.086 | E070 A(n) grizzly bear standing. |
| J6248 | 0.091 | E049 Papyrus following Stench. |

## `mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| J19592 | 0.081 | E071 A(n) gazelle consuming grass. |
| J6248 | 0.091 | E049 Papyrus following Stench. |
| J197 | 0.086 | E070 A(n) grizzly bear standing. |

## `cap+mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| J19592 | 0.081 | E071 A(n) gazelle consuming grass. |
| J6248 | 0.091 | E049 Papyrus following Stench. |
| J197 | 0.086 | E070 A(n) grizzly bear standing. |

