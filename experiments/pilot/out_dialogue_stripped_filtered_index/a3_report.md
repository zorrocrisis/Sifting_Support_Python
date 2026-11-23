# A3 — Redundancy control in CC

**Status: FAIL** — best variant by rule: `cap+mmr`

Share 0.5, total 12, AC seed 42, cap 2, λ 0.7. Pass rule: >= 3 relevant dialogue lines contribute (relevant = lines with gold matches).

The game's composer counts each paired dialogue line against the CC quota, so a new dialogue line costs two slots. At quota 6, at most 3 distinct dialogue lines can contribute, whatever the selector.

| variant | dialogue lines in pool | CC events | CC redundancy | pool redundancy | distinct dialogue in requested pairs | passes |
|---|---|---|---|---|---|---|
| nearest | 1 | 5 | 0.387 | 0.296 | 3 | no |
| cap | 2 | 4 | 0.351 | 0.270 | 8 | no |
| mmr | 1 | 5 | 0.366 | 0.293 | 2 | no |
| cap+mmr | 2 | 4 | 0.320 | 0.262 | 7 | no |
| mmr_ix | 2 | 4 | 0.419 | 0.302 | 3 | no |
| cap+mmr_ix | 2 | 4 | 0.347 | 0.273 | 7 | no |

## `nearest` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.239 | E135 Stench missed Odette with a hit from her left fist. |
| S110 | 0.254 | E130 Odette stumbled while trying to strike Stench. |
| S110 | 0.255 | E114 Odette flagrantly insulted Stench's leg hair. |
| S110 | 0.255 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S110 | 0.266 | E147 Odette collapsed due to a bruise. |

## `cap` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.239 | E135 Stench missed Odette with a hit from her left fist. |
| S110 | 0.254 | E130 Odette stumbled while trying to strike Stench. |
| S107 | 0.305 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S107 | 0.378 | E000 Boyd watching for targets. |

## `mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.239 | E135 Stench missed Odette with a hit from her left fist. |
| S110 | 0.266 | E147 Odette collapsed due to a bruise. |
| S110 | 0.267 | E119 Odette called Stench a salamander. This drove Stench into a rage and … |
| S110 | 0.255 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S110 | 0.254 | E130 Odette stumbled while trying to strike Stench. |

## `cap+mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.239 | E135 Stench missed Odette with a hit from her left fist. |
| S110 | 0.266 | E147 Odette collapsed due to a bruise. |
| S107 | 0.378 | E000 Boyd watching for targets. |
| S107 | 0.305 | E082 Stench shared views on aiding the downtrodden with Boyd. |

## `mmr_ix` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.239 | E135 Stench missed Odette with a hit from her left fist. |
| S107 | 0.305 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S110 | 0.255 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S110 | 0.255 | E114 Odette flagrantly insulted Stench's leg hair. |

## `cap+mmr_ix` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.239 | E135 Stench missed Odette with a hit from her left fist. |
| S107 | 0.305 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S110 | 0.255 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S107 | 0.378 | E000 Boyd watching for targets. |

