# A3 — Redundancy control in CC

**Status: PASS** — best variant by rule: `mmr`

Share 0.5, total 12, AC seed 42, cap 2, λ 0.7. Pass rule: >= 3 relevant dialogue lines contribute (relevant = lines with gold matches).

The game's composer counts each paired dialogue line against the CC quota, so a new dialogue line costs two slots. At quota 6, at most 3 distinct dialogue lines can contribute, whatever the selector.

| variant | dialogue lines in pool | CC events | CC redundancy | pool redundancy | distinct dialogue in requested pairs | passes |
|---|---|---|---|---|---|---|
| nearest | 3 | 3 | 0.260 | 0.254 | 3 | yes |
| cap | 2 | 4 | 0.296 | 0.252 | 7 | no |
| mmr | 3 | 3 | 0.260 | 0.254 | 4 | yes |
| cap+mmr | 3 | 3 | 0.260 | 0.254 | 7 | yes |
| mmr_ix | 3 | 3 | 0.260 | 0.254 | 5 | yes |
| cap+mmr_ix | 3 | 3 | 0.260 | 0.254 | 7 | yes |

## `nearest` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S106 | 0.071 | E088 Stench hauling steel x18 to Stockpile zone 1. |
| S111 | 0.080 | E071 A(n) gazelle consuming grass. |
| S106 | 0.081 | E049 Papyrus following Stench. |

## `cap` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S106 | 0.071 | E088 Stench hauling steel x18 to Stockpile zone 1. |
| S111 | 0.080 | E071 A(n) gazelle consuming grass. |
| S106 | 0.081 | E049 Papyrus following Stench. |
| S111 | 0.186 | E007 A(n) gazelle wandering. |

## `mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S104 | 0.071 | E088 Stench hauling steel x18 to Stockpile zone 1. |
| S111 | 0.080 | E071 A(n) gazelle consuming grass. |
| S106 | 0.081 | E049 Papyrus following Stench. |

## `cap+mmr` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S104 | 0.071 | E088 Stench hauling steel x18 to Stockpile zone 1. |
| S111 | 0.080 | E071 A(n) gazelle consuming grass. |
| S106 | 0.081 | E049 Papyrus following Stench. |

## `mmr_ix` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S104 | 0.071 | E088 Stench hauling steel x18 to Stockpile zone 1. |
| S111 | 0.080 | E071 A(n) gazelle consuming grass. |
| S106 | 0.081 | E049 Papyrus following Stench. |

## `cap+mmr_ix` — CC events in the pool

| dialogue | NCD | event |
|---|---|---|
| S104 | 0.071 | E088 Stench hauling steel x18 to Stockpile zone 1. |
| S111 | 0.080 | E071 A(n) gazelle consuming grass. |
| S106 | 0.081 | E049 Papyrus following Stench. |

