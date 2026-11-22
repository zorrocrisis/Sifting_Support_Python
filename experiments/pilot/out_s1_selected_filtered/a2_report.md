# A2 — Name masking

k = 6 CC slots (total 12, share 0.5). Names masked on both sides.

- `per_colonist`: each colonist gets their own token (C1, C2, …), as specified in the handoff. NCD can still match on which colonist is involved.
- `single`: every colonist becomes `C`. NCD can't match on identity at all.
- `removed`: names are deleted. NCD can't see how many colonists a line names either.

| metric | unmasked | per_colonist | single | removed |
|---|---|---|---|---|
| top-k pairs changed vs unmasked | – | 0% | 0% | 0% |
| actor-match rate in top-k | 50% | 50% | 50% | 50% |
| mean top-5 overlap per dialogue line | 1.00 | 0.71 | 0.69 | 0.60 |
| distinct dialogue lines in top-k | 6 | 6 | 6 | 6 |

## A1 metrics on masked text

| text | Recall@5 | Recall@10 | MRR |
|---|---|---|---|
| unmasked | 0.462 | 0.577 | 0.435 |
| per_colonist | 0.462 | 0.462 | 0.448 |
| single | 0.462 | 0.462 | 0.434 |
| removed | 0.346 | 0.462 | 0.418 |

## Unmasked top-6 pairs

| # | NCD | dialogue | event | also unmasked |
|---|---|---|---|---|
| 1 | 0.091 | J6248 Papyrus following Stench. | E049 Papyrus following Stench. | yes |
| 2 | 0.222 | J11165 Odette watching for targets. | E000 Boyd watching for targets. | yes |
| 3 | 0.250 | J197 A(n) grizzly bear standing. | E069 A(n) grizzly bear wandering. | yes |
| 4 | 0.255 | J784 Stench hauling steel x56 to Stockpile zone 1. | E090 Stench hauling silver x500 to Stockpile zone 1. | yes |
| 5 | 0.297 | J19592 A(n) gazelle consuming grass. | E072 A(n) hare consuming grass. | yes |
| 6 | 0.348 | J23595 Stench moving. | E157 Stench resting. | yes |

## Masked (per_colonist) top-6 pairs

| # | NCD | dialogue | event | also unmasked |
|---|---|---|---|---|
| 1 | 0.103 | J6248 Papyrus following Stench. | E049 Papyrus following Stench. | yes |
| 2 | 0.125 | J11165 Odette watching for targets. | E000 Boyd watching for targets. | yes |
| 3 | 0.250 | J197 A(n) grizzly bear standing. | E069 A(n) grizzly bear wandering. | yes |
| 4 | 0.275 | J784 Stench hauling steel x56 to Stockpile zone 1. | E090 Stench hauling silver x500 to Stockpile zone 1. | yes |
| 5 | 0.297 | J19592 A(n) gazelle consuming grass. | E072 A(n) hare consuming grass. | yes |
| 6 | 0.421 | J23595 Stench moving. | E157 Stench resting. | yes |

## Masked (single) top-6 pairs

| # | NCD | dialogue | event | also unmasked |
|---|---|---|---|---|
| 1 | 0.097 | J11165 Odette watching for targets. | E000 Boyd watching for targets. | yes |
| 2 | 0.107 | J6248 Papyrus following Stench. | E049 Papyrus following Stench. | yes |
| 3 | 0.250 | J197 A(n) grizzly bear standing. | E069 A(n) grizzly bear wandering. | yes |
| 4 | 0.280 | J784 Stench hauling steel x56 to Stockpile zone 1. | E090 Stench hauling silver x500 to Stockpile zone 1. | yes |
| 5 | 0.297 | J19592 A(n) gazelle consuming grass. | E072 A(n) hare consuming grass. | yes |
| 6 | 0.389 | J23595 Stench moving. | E157 Stench resting. | yes |

## Masked (removed) top-6 pairs

| # | NCD | dialogue | event | also unmasked |
|---|---|---|---|---|
| 1 | 0.103 | J11165 Odette watching for targets. | E000 Boyd watching for targets. | yes |
| 2 | 0.115 | J6248 Papyrus following Stench. | E049 Papyrus following Stench. | yes |
| 3 | 0.250 | J197 A(n) grizzly bear standing. | E069 A(n) grizzly bear wandering. | yes |
| 4 | 0.292 | J784 Stench hauling steel x56 to Stockpile zone 1. | E090 Stench hauling silver x500 to Stockpile zone 1. | yes |
| 5 | 0.297 | J19592 A(n) gazelle consuming grass. | E072 A(n) hare consuming grass. | yes |
| 6 | 0.312 | J23595 Stench moving. | E157 Stench resting. | yes |

## Interpretation (for the author)

- Most pairs change and become more on-topic → adopt masking.
- Most pairs change and become nonsense → names were the only signal.
- Pairs barely change → names weren't driving the matches.

