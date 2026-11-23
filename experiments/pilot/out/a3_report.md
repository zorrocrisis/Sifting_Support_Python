# A3 — Redundancy control in CC

**Status: PASS** — best variant by rule: `mmr`

Share 0.5, total 12, AC seed 42, cap 2, λ 0.7. Pass rule: >= 3 relevant dialogue lines contribute (relevant = lines with gold matches).

The game's composer counts each paired dialogue line against the CC quota, so a new dialogue line costs two slots. At quota 6, at most 3 distinct dialogue lines can contribute, whatever the selector.

| variant | dialogue lines in pool | CC events | CC redundancy | pool redundancy | distinct dialogue in requested pairs | passes |
|---|---|---|---|---|---|---|
| nearest | 1 | 5 | 0.497 | 0.322 | 4 | no |
| cap | 2 | 4 | 0.447 | 0.309 | 7 | no |
| mmr | 3 | 3 | 0.377 | 0.299 | 4 | yes |
| cap+mmr | 3 | 3 | 0.377 | 0.299 | 8 | yes |

## `nearest` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.580 | E138 Stench flailed at Odette with her left fist, but stumbled at the last… |
| S110 | 0.580 | E137 Odette attempted to hit Stench, but hesitated at the last second. |
| S110 | 0.593 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |
| S110 | 0.593 | E128 Odette missed Stench with a beat from her left fist. |
| S110 | 0.605 | E129 Stench missed Odette with a smash from her left fist. |

## `cap` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.580 | E138 Stench flailed at Odette with her left fist, but stumbled at the last… |
| S110 | 0.580 | E137 Odette attempted to hit Stench, but hesitated at the last second. |
| S108 | 0.600 | E082 Stench shared views on aiding the downtrodden with Boyd. |
| S108 | 0.613 | E118 Odette is no longer on an insulting spree against Stench, Hunter. |

## `mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.580 | E137 Odette attempted to hit Stench, but hesitated at the last second. |
| S106 | 0.607 | E089 Stench hauling synthread pants (normal 97%) to Stockpile zone 1. |
| S108 | 0.600 | E082 Stench shared views on aiding the downtrodden with Boyd. |

## `cap+mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S110 | 0.580 | E137 Odette attempted to hit Stench, but hesitated at the last second. |
| S106 | 0.607 | E089 Stench hauling synthread pants (normal 97%) to Stockpile zone 1. |
| S108 | 0.600 | E082 Stench shared views on aiding the downtrodden with Boyd. |

