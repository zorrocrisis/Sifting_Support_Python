# A2 — Name masking

k = 6 CC slots (total 12, share 0.5). Names masked on both sides.

- `per_colonist`: each colonist gets their own token (C1, C2, …), as specified in the handoff. NCD can still match on which colonist is involved.
- `single`: every colonist becomes `C`. NCD can't match on identity at all.
- `removed`: names are deleted. NCD can't see how many colonists a line names either.

| metric | unmasked | per_colonist | single | removed |
|---|---|---|---|---|
| top-k pairs changed vs unmasked | – | 0% | 0% | 0% |
| actor-match rate in top-k | 33% | 33% | 33% | 33% |
| mean top-5 overlap per dialogue line | 1.00 | 0.63 | 0.66 | 0.63 |
| distinct dialogue lines in top-k | 5 | 5 | 5 | 5 |

## A1 metrics on masked text

| text | Recall@5 | Recall@10 | MRR |
|---|---|---|---|
| unmasked | 0.331 | 0.346 | 0.404 |
| per_colonist | 0.331 | 0.462 | 0.405 |
| single | 0.331 | 0.423 | 0.403 |
| removed | 0.331 | 0.346 | 0.398 |

## Unmasked top-6 pairs

| # | NCD | dialogue | event | also unmasked |
|---|---|---|---|---|
| 1 | 0.081 | J19592 A(n) gazelle consuming grass. | E071 A(n) gazelle consuming grass. | yes |
| 2 | 0.086 | J197 A(n) grizzly bear standing. | E070 A(n) grizzly bear standing. | yes |
| 3 | 0.091 | J6248 Papyrus following Stench. | E049 Papyrus following Stench. | yes |
| 4 | 0.132 | J784 Stench hauling steel x56 to Stockpile zone 1. | E088 Stench hauling steel x18 to Stockpile zone 1. | yes |
| 5 | 0.222 | J11165 Odette watching for targets. | E002 Stench watching for targets. | yes |
| 6 | 0.222 | J11165 Odette watching for targets. | E000 Boyd watching for targets. | yes |

## Masked (per_colonist) top-6 pairs

| # | NCD | dialogue | event | also unmasked |
|---|---|---|---|---|
| 1 | 0.081 | J19592 A(n) gazelle consuming grass. | E071 A(n) gazelle consuming grass. | yes |
| 2 | 0.086 | J197 A(n) grizzly bear standing. | E070 A(n) grizzly bear standing. | yes |
| 3 | 0.103 | J6248 Papyrus following Stench. | E049 Papyrus following Stench. | yes |
| 4 | 0.125 | J11165 Odette watching for targets. | E002 Stench watching for targets. | yes |
| 5 | 0.125 | J11165 Odette watching for targets. | E000 Boyd watching for targets. | yes |
| 6 | 0.143 | J784 Stench hauling steel x56 to Stockpile zone 1. | E088 Stench hauling steel x18 to Stockpile zone 1. | yes |

## Masked (single) top-6 pairs

| # | NCD | dialogue | event | also unmasked |
|---|---|---|---|---|
| 1 | 0.081 | J19592 A(n) gazelle consuming grass. | E071 A(n) gazelle consuming grass. | yes |
| 2 | 0.086 | J197 A(n) grizzly bear standing. | E070 A(n) grizzly bear standing. | yes |
| 3 | 0.097 | J11165 Odette watching for targets. | E000 Boyd watching for targets. | yes |
| 4 | 0.097 | J11165 Odette watching for targets. | E002 Stench watching for targets. | yes |
| 5 | 0.107 | J6248 Papyrus following Stench. | E049 Papyrus following Stench. | yes |
| 6 | 0.146 | J784 Stench hauling steel x56 to Stockpile zone 1. | E088 Stench hauling steel x18 to Stockpile zone 1. | yes |

## Masked (removed) top-6 pairs

| # | NCD | dialogue | event | also unmasked |
|---|---|---|---|---|
| 1 | 0.081 | J19592 A(n) gazelle consuming grass. | E071 A(n) gazelle consuming grass. | yes |
| 2 | 0.086 | J197 A(n) grizzly bear standing. | E070 A(n) grizzly bear standing. | yes |
| 3 | 0.103 | J11165 Odette watching for targets. | E000 Boyd watching for targets. | yes |
| 4 | 0.103 | J11165 Odette watching for targets. | E002 Stench watching for targets. | yes |
| 5 | 0.115 | J6248 Papyrus following Stench. | E049 Papyrus following Stench. | yes |
| 6 | 0.152 | J784 Stench hauling steel x56 to Stockpile zone 1. | E088 Stench hauling steel x18 to Stockpile zone 1. | yes |

## Interpretation (for the author)

- Most pairs change and become more on-topic → adopt masking.
- Most pairs change and become nonsense → names were the only signal.
- Pairs barely change → names weren't driving the matches.

