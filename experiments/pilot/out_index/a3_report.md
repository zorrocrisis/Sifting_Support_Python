# A3 — Redundancy control in CC

**Status: FAIL** — best variant by rule: `cap+mmr`

Share 0.5, total 12, AC seed 42, cap 2, λ 0.7. Pass rule: >= 3 relevant dialogue lines contribute (relevant = lines with gold matches).

The game's composer counts each paired dialogue line against the CC quota, so a new dialogue line costs two slots. At quota 6, at most 3 distinct dialogue lines can contribute, whatever the selector.

| variant | dialogue lines in pool | CC events | CC redundancy | pool redundancy | distinct dialogue in requested pairs | passes |
|---|---|---|---|---|---|---|
| nearest | 1 | 5 | 0.448 | 0.308 | 1 | no |
| cap | 2 | 4 | 0.339 | 0.274 | 8 | no |
| mmr | 1 | 5 | 0.342 | 0.288 | 1 | no |
| cap+mmr | 2 | 4 | 0.293 | 0.261 | 7 | no |
| mmr_ix | 2 | 4 | 0.331 | 0.291 | 2 | no |
| cap+mmr_ix | 2 | 4 | 0.330 | 0.272 | 8 | no |

## `nearest` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.232 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S110 | 0.234 | E137 Odette attempted to hit Stench, but hesitated at the last second. |
| S110 | 0.238 | E128 Odette missed Stench with a beat from her left fist. |
| S110 | 0.240 | E138 Stench flailed at Odette with her left fist, but stumbled at the last… |
| S110 | 0.240 | E119 Odette called Stench a salamander. This drove Stench into a rage and … |

## `cap` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.232 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S110 | 0.234 | E137 Odette attempted to hit Stench, but hesitated at the last second. |
| S107 | 0.325 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S107 | 0.396 | E000 Boyd watching for targets. |

## `mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.232 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S110 | 0.283 | E160 Stench tending to Odette. |
| S110 | 0.254 | E141 Odette hit Stench with her left fist. |
| S110 | 0.240 | E119 Odette called Stench a salamander. This drove Stench into a rage and … |
| S110 | 0.246 | E125 Odette flailed at Stench, but stumbled at the last second. |

## `cap+mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.232 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S110 | 0.283 | E160 Stench tending to Odette. |
| S107 | 0.325 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S107 | 0.396 | E000 Boyd watching for targets. |

## `mmr_ix` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.232 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S107 | 0.325 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S110 | 0.240 | E138 Stench flailed at Odette with her left fist, but stumbled at the last… |
| S110 | 0.283 | E160 Stench tending to Odette. |

## `cap+mmr_ix` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.232 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S107 | 0.325 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S110 | 0.240 | E138 Stench flailed at Odette with her left fist, but stumbled at the last… |
| S107 | 0.396 | E000 Boyd watching for targets. |

