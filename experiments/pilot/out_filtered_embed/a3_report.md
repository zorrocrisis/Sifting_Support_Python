# A3 — Redundancy control in CC

**Status: PASS** — best variant by rule: `mmr`

Share 0.5, total 12, AC seed 42, cap 2, λ 0.7. Pass rule: >= 3 relevant dialogue lines contribute (relevant = lines with gold matches).

The game's composer counts each paired dialogue line against the CC quota, so a new dialogue line costs two slots. At quota 6, at most 3 distinct dialogue lines can contribute, whatever the selector.

| variant | dialogue lines in pool | CC events | CC redundancy | pool redundancy | distinct dialogue in requested pairs | passes |
|---|---|---|---|---|---|---|
| nearest | 3 | 3 | 0.353 | 0.272 | 6 | yes |
| cap | 3 | 3 | 0.353 | 0.272 | 7 | yes |
| mmr | 3 | 3 | 0.271 | 0.270 | 6 | yes |
| cap+mmr | 3 | 3 | 0.271 | 0.270 | 7 | yes |

## `nearest` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S111 | 0.365 | E130 Odette stumbled while trying to strike Stench. |
| S110 | 0.393 | E124 Stench fighting with Odette. |
| S106 | 0.408 | E049 Papyrus following Stench. |

## `cap` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S111 | 0.365 | E130 Odette stumbled while trying to strike Stench. |
| S110 | 0.393 | E124 Stench fighting with Odette. |
| S106 | 0.408 | E049 Papyrus following Stench. |

## `mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S111 | 0.365 | E130 Odette stumbled while trying to strike Stench. |
| S106 | 0.408 | E049 Papyrus following Stench. |
| S105 | 0.432 | E052 The turkey ducked aside at the last second, Stench's bolt-action rifl… |

## `cap+mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S111 | 0.365 | E130 Odette stumbled while trying to strike Stench. |
| S106 | 0.408 | E049 Papyrus following Stench. |
| S105 | 0.432 | E052 The turkey ducked aside at the last second, Stench's bolt-action rifl… |

