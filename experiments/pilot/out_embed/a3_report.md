# A3 — Redundancy control in CC

**Status: PASS** — best variant by rule: `cap`

Share 0.5, total 12, AC seed 42, cap 2, λ 0.7. Pass rule: >= 3 relevant dialogue lines contribute (relevant = lines with gold matches).

The game's composer counts each paired dialogue line against the CC quota, so a new dialogue line costs two slots. At quota 6, at most 3 distinct dialogue lines can contribute, whatever the selector.

| variant | dialogue lines in pool | CC events | CC redundancy | pool redundancy | distinct dialogue in requested pairs | passes |
|---|---|---|---|---|---|---|
| nearest | 3 | 3 | 0.292 | 0.258 | 5 | yes |
| cap | 3 | 3 | 0.292 | 0.258 | 7 | yes |
| mmr | 2 | 4 | 0.226 | 0.246 | 5 | no |
| cap+mmr | 2 | 4 | 0.222 | 0.223 | 7 | no |

## `nearest` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S112 | 0.361 | E046 Boyd wandering. |
| S111 | 0.365 | E130 Odette stumbled while trying to strike Stench. |
| S110 | 0.387 | E160 Stench tending to Odette. |

## `cap` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S112 | 0.361 | E046 Boyd wandering. |
| S111 | 0.365 | E130 Odette stumbled while trying to strike Stench. |
| S110 | 0.387 | E160 Stench tending to Odette. |

## `mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S112 | 0.361 | E046 Boyd wandering. |
| S111 | 0.411 | E111 Odette has fixated her rage on Stench. She will follow Stench around,… |
| S111 | 0.365 | E130 Odette stumbled while trying to strike Stench. |
| S111 | 0.409 | E125 Odette flailed at Stench, but stumbled at the last second. |

## `cap+mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S112 | 0.361 | E046 Boyd wandering. |
| S111 | 0.411 | E111 Odette has fixated her rage on Stench. She will follow Stench around,… |
| S111 | 0.365 | E130 Odette stumbled while trying to strike Stench. |
| S112 | 0.461 | E000 Boyd watching for targets. |

