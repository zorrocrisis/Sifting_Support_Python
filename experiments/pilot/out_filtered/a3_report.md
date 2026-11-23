# A3 — Redundancy control in CC

**Status: PASS** — best variant by rule: `mmr`

Share 0.5, total 12, AC seed 42, cap 2, λ 0.7. Pass rule: >= 3 relevant dialogue lines contribute (relevant = lines with gold matches).

The game's composer counts each paired dialogue line against the CC quota, so a new dialogue line costs two slots. At quota 6, at most 3 distinct dialogue lines can contribute, whatever the selector.

| variant | dialogue lines in pool | CC events | CC redundancy | pool redundancy | distinct dialogue in requested pairs | passes |
|---|---|---|---|---|---|---|
| nearest | 3 | 3 | 0.425 | 0.307 | 5 | yes |
| cap | 2 | 4 | 0.400 | 0.303 | 7 | no |
| mmr | 3 | 3 | 0.355 | 0.299 | 4 | yes |
| cap+mmr | 3 | 3 | 0.355 | 0.299 | 7 | yes |

## `nearest` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.593 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S108 | 0.600 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S110 | 0.617 | E135 Stench missed Odette with a hit from her left fist. |

## `cap` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.593 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S108 | 0.600 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S110 | 0.617 | E135 Stench missed Odette with a hit from her left fist. |
| S108 | 0.637 | E119 Odette called Stench a salamander. This drove Stench into a rage and … |

## `mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.593 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S108 | 0.600 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S107 | 0.633 | E052 The turkey ducked aside at the last second, Stench's bolt-action rifl… |

## `cap+mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.593 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S108 | 0.600 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S107 | 0.633 | E052 The turkey ducked aside at the last second, Stench's bolt-action rifl… |

