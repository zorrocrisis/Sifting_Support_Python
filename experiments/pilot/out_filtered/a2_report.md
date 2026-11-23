# A2 — Name masking

k = 6 CC slots (total 12, share 0.5). Names masked on both sides.

- `per_colonist`: each colonist gets their own token (C1, C2, …), as specified in the handoff. NCD can still match on which colonist is involved.
- `single`: every colonist becomes `C`. NCD can't match on identity at all.
- `removed`: names are deleted. NCD can't see how many colonists a line names either.

| metric | unmasked | per_colonist | single | removed |
|---|---|---|---|---|
| top-k pairs changed vs unmasked | – | 33% | 67% | 50% |
| actor-match rate in top-k | 100% | 100% | 100% | 100% |
| mean top-5 overlap per dialogue line | 1.00 | 0.65 | 0.60 | 0.55 |
| distinct dialogue lines in top-k | 3 | 3 | 4 | 4 |

## A1 metrics on masked text

| text | Recall@5 | Recall@10 | MRR |
|---|---|---|---|
| unmasked | 0.000 | 0.323 | 0.090 |
| per_colonist | 0.135 | 0.260 | 0.235 |
| single | 0.135 | 0.260 | 0.160 |
| removed | 0.135 | 0.260 | 0.157 |

## Unmasked top-6 pairs

| # | NCD | dialogue | event | also unmasked |
|---|---|---|---|---|
| 1 | 0.593 | S110 Odette 'Odette' O'Neill said 'Stench, I watched the fa… | E118 Odette is no longer on an insulting spree against Sten… | yes |
| 2 | 0.600 | S108 Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, th… | E082 Stench shared views on aiding the downtrodden with Boy… | yes |
| 3 | 0.609 | S107 Dillon 'Boyd' Boyd said 'Stench, my hands shook when t… | E082 Stench shared views on aiding the downtrodden with Boy… | yes |
| 4 | 0.613 | S108 Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, th… | E118 Odette is no longer on an insulting spree against Sten… | yes |
| 5 | 0.617 | S110 Odette 'Odette' O'Neill said 'Stench, I watched the fa… | E135 Stench missed Odette with a hit from her left fist. | yes |
| 6 | 0.617 | S110 Odette 'Odette' O'Neill said 'Stench, I watched the fa… | E139 Odette tried to use her right fist to hit Stench, but … | yes |

## Masked (per_colonist) top-6 pairs

| # | NCD | dialogue | event | also unmasked |
|---|---|---|---|---|
| 1 | 0.547 | S108 Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, th… | E118 Odette is no longer on an insulting spree against Sten… | yes |
| 2 | 0.568 | S107 Dillon 'Boyd' Boyd said 'Stench, my hands shook when t… | E139 Odette tried to use her right fist to hit Stench, but … |  |
| 3 | 0.578 | S110 Odette 'Odette' O'Neill said 'Stench, I watched the fa… | E118 Odette is no longer on an insulting spree against Sten… | yes |
| 4 | 0.589 | S107 Dillon 'Boyd' Boyd said 'Stench, my hands shook when t… | E118 Odette is no longer on an insulting spree against Sten… |  |
| 5 | 0.597 | S108 Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, th… | E082 Stench shared views on aiding the downtrodden with Boy… | yes |
| 6 | 0.603 | S107 Dillon 'Boyd' Boyd said 'Stench, my hands shook when t… | E082 Stench shared views on aiding the downtrodden with Boy… | yes |

## Masked (single) top-6 pairs

| # | NCD | dialogue | event | also unmasked |
|---|---|---|---|---|
| 1 | 0.525 | S110 Odette 'Odette' O'Neill said 'Stench, I watched the fa… | E118 Odette is no longer on an insulting spree against Sten… | yes |
| 2 | 0.541 | S108 Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, th… | E118 Odette is no longer on an insulting spree against Sten… | yes |
| 3 | 0.571 | S107 Dillon 'Boyd' Boyd said 'Stench, my hands shook when t… | E139 Odette tried to use her right fist to hit Stench, but … |  |
| 4 | 0.577 | S107 Dillon 'Boyd' Boyd said 'Stench, my hands shook when t… | E119 Odette called Stench a salamander. This drove Stench i… |  |
| 5 | 0.585 | S105 Lidia 'Stench' Schmitt said 'Boyd, my shot dropped tha… | E118 Odette is no longer on an insulting spree against Sten… |  |
| 6 | 0.586 | S107 Dillon 'Boyd' Boyd said 'Stench, my hands shook when t… | E118 Odette is no longer on an insulting spree against Sten… |  |

## Masked (removed) top-6 pairs

| # | NCD | dialogue | event | also unmasked |
|---|---|---|---|---|
| 1 | 0.554 | S108 Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, th… | E118 Odette is no longer on an insulting spree against Sten… | yes |
| 2 | 0.571 | S110 Odette 'Odette' O'Neill said 'Stench, I watched the fa… | E118 Odette is no longer on an insulting spree against Sten… | yes |
| 3 | 0.571 | S110 Odette 'Odette' O'Neill said 'Stench, I watched the fa… | E082 Stench shared views on aiding the downtrodden with Boy… |  |
| 4 | 0.578 | S107 Dillon 'Boyd' Boyd said 'Stench, my hands shook when t… | E082 Stench shared views on aiding the downtrodden with Boy… | yes |
| 5 | 0.582 | S107 Dillon 'Boyd' Boyd said 'Stench, my hands shook when t… | E119 Odette called Stench a salamander. This drove Stench i… |  |
| 6 | 0.583 | S105 Lidia 'Stench' Schmitt said 'Boyd, my shot dropped tha… | E053 Stench fired her bolt-action rifle at the turkey. |  |

## Interpretation (for the author)

- Most pairs change and become more on-topic → adopt masking.
- Most pairs change and become nonsense → names were the only signal.
- Pairs barely change → names weren't driving the matches.

