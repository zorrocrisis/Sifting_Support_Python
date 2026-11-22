# A3 — Redundancy control in CC

**Status: FAIL** — best variant by rule: `cap+mmr`

Share 0.5, total 12, AC seed 42, cap 2, λ 0.7. Pass rule: >= 3 relevant dialogue lines contribute (relevant = lines with gold matches).

The game's composer counts each paired dialogue line against the CC quota, so a new dialogue line costs two slots. At quota 6, at most 3 distinct dialogue lines can contribute, whatever the selector.

| variant | dialogue lines in pool | CC events | CC redundancy | pool redundancy | distinct dialogue in requested pairs | passes |
|---|---|---|---|---|---|---|
| nearest | 1 | 5 | 0.402 | 0.296 | 2 | no |
| cap | 2 | 4 | 0.315 | 0.268 | 8 | no |
| mmr | 1 | 5 | 0.355 | 0.285 | 2 | no |
| cap+mmr | 2 | 4 | 0.305 | 0.263 | 8 | no |
| mmr_ix | 2 | 4 | 0.387 | 0.294 | 3 | no |
| cap+mmr_ix | 2 | 4 | 0.315 | 0.268 | 7 | no |

## `nearest` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.232 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S110 | 0.240 | E119 Odette called Stench a salamander. This drove Stench into a rage and … |
| S110 | 0.246 | E139 Odette tried to use her right fist to hit Stench, but stumbled at the… |
| S110 | 0.249 | E114 Odette flagrantly insulted Stench's leg hair. |
| S110 | 0.252 | E135 Stench missed Odette with a hit from her left fist. |

## `cap` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.232 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S110 | 0.240 | E119 Odette called Stench a salamander. This drove Stench into a rage and … |
| S107 | 0.325 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S107 | 0.396 | E000 Boyd watching for targets. |

## `mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.232 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S110 | 0.285 | E124 Stench fighting with Odette. |
| S110 | 0.240 | E119 Odette called Stench a salamander. This drove Stench into a rage and … |
| S110 | 0.263 | E130 Odette stumbled while trying to strike Stench. |
| S110 | 0.246 | E139 Odette tried to use her right fist to hit Stench, but stumbled at the… |

## `cap+mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.232 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S110 | 0.285 | E124 Stench fighting with Odette. |
| S107 | 0.325 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S107 | 0.396 | E000 Boyd watching for targets. |

## `mmr_ix` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.232 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S107 | 0.325 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S110 | 0.240 | E119 Odette called Stench a salamander. This drove Stench into a rage and … |
| S110 | 0.246 | E139 Odette tried to use her right fist to hit Stench, but stumbled at the… |

## `cap+mmr_ix` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.232 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S107 | 0.325 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S110 | 0.240 | E119 Odette called Stench a salamander. This drove Stench into a rage and … |
| S107 | 0.396 | E000 Boyd watching for targets. |

