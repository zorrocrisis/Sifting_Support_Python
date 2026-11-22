# A2 — Name masking

k = 6 CC slots (total 12, share 0.5). Names masked on both sides.

- `per_colonist`: each colonist gets their own token (C1, C2, …), as specified in the handoff. NCD can still match on which colonist is involved.
- `single`: every colonist becomes `C`. NCD can't match on identity at all.
- `removed`: names are deleted. NCD can't see how many colonists a line names either.

| metric | unmasked | per_colonist | single | removed |
|---|---|---|---|---|
| top-k pairs changed vs unmasked | – | 67% | 83% | 83% |
| actor-match rate in top-k | 100% | 100% | 100% | 100% |
| mean top-5 overlap per dialogue line | 1.00 | 0.50 | 0.42 | 0.45 |
| distinct dialogue lines in top-k | 2 | 3 | 3 | 4 |

## A1 metrics on masked text

| text | Recall@5 | Recall@10 | MRR |
|---|---|---|---|
| unmasked | 0.098 | 0.137 | 0.205 |
| per_colonist | 0.074 | 0.128 | 0.202 |
| single | 0.074 | 0.074 | 0.203 |
| removed | 0.057 | 0.116 | 0.217 |

## Unmasked top-6 pairs

| # | NCD | dialogue | event | also unmasked |
|---|---|---|---|---|
| 1 | 0.580 | S110 Odette 'Odette' O'Neill said 'Stench, I watched the fa… | E138 Stench flailed at Odette with her left fist, but stumb… | yes |
| 2 | 0.580 | S110 Odette 'Odette' O'Neill said 'Stench, I watched the fa… | E137 Odette attempted to hit Stench, but hesitated at the l… | yes |
| 3 | 0.593 | S110 Odette 'Odette' O'Neill said 'Stench, I watched the fa… | E118 Odette is no longer on an insulting spree against Sten… | yes |
| 4 | 0.593 | S110 Odette 'Odette' O'Neill said 'Stench, I watched the fa… | E128 Odette missed Stench with a beat from her left fist. | yes |
| 5 | 0.600 | S108 Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, th… | E082 Stench shared views on aiding the downtrodden with Boy… | yes |
| 6 | 0.605 | S110 Odette 'Odette' O'Neill said 'Stench, I watched the fa… | E129 Stench missed Odette with a smash from her left fist. | yes |

## Masked (per_colonist) top-6 pairs

| # | NCD | dialogue | event | also unmasked |
|---|---|---|---|---|
| 1 | 0.547 | S108 Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, th… | E118 Odette is no longer on an insulting spree against Sten… |  |
| 2 | 0.556 | S108 Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, th… | E137 Odette attempted to hit Stench, but hesitated at the l… |  |
| 3 | 0.568 | S107 Dillon 'Boyd' Boyd said 'Stench, my hands shook when t… | E139 Odette tried to use her right fist to hit Stench, but … |  |
| 4 | 0.571 | S110 Odette 'Odette' O'Neill said 'Stench, I watched the fa… | E137 Odette attempted to hit Stench, but hesitated at the l… | yes |
| 5 | 0.578 | S110 Odette 'Odette' O'Neill said 'Stench, I watched the fa… | E118 Odette is no longer on an insulting spree against Sten… | yes |
| 6 | 0.587 | S110 Odette 'Odette' O'Neill said 'Stench, I watched the fa… | E058 Stench's bolt-action rifle bullet missed by a small ma… |  |

## Masked (single) top-6 pairs

| # | NCD | dialogue | event | also unmasked |
|---|---|---|---|---|
| 1 | 0.525 | S110 Odette 'Odette' O'Neill said 'Stench, I watched the fa… | E118 Odette is no longer on an insulting spree against Sten… | yes |
| 2 | 0.541 | S108 Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, th… | E118 Odette is no longer on an insulting spree against Sten… |  |
| 3 | 0.550 | S108 Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, th… | E137 Odette attempted to hit Stench, but hesitated at the l… |  |
| 4 | 0.552 | S105 Lidia 'Stench' Schmitt said 'Boyd, my shot dropped tha… | E138 Stench flailed at Odette with her left fist, but stumb… |  |
| 5 | 0.554 | S105 Lidia 'Stench' Schmitt said 'Boyd, my shot dropped tha… | E144 Odette attempted to use her right fist to beat Stench,… |  |
| 6 | 0.554 | S105 Lidia 'Stench' Schmitt said 'Boyd, my shot dropped tha… | E058 Stench's bolt-action rifle bullet missed by a small ma… |  |

## Masked (removed) top-6 pairs

| # | NCD | dialogue | event | also unmasked |
|---|---|---|---|---|
| 1 | 0.548 | S106 Lidia 'Stench' Schmitt said 'Boyd, Papyrus trailed me … | E159 Stench hauling packaged survival meal x10 to Stockpile… |  |
| 2 | 0.550 | S105 Lidia 'Stench' Schmitt said 'Boyd, my shot dropped tha… | E137 Odette attempted to hit Stench, but hesitated at the l… |  |
| 3 | 0.550 | S105 Lidia 'Stench' Schmitt said 'Boyd, my shot dropped tha… | E140 Stench missed while trying to bash Odette with her lef… |  |
| 4 | 0.550 | S105 Lidia 'Stench' Schmitt said 'Boyd, my shot dropped tha… | E058 Stench's bolt-action rifle bullet missed by a small ma… |  |
| 5 | 0.554 | S110 Odette 'Odette' O'Neill said 'Stench, I watched the fa… | E137 Odette attempted to hit Stench, but hesitated at the l… | yes |
| 6 | 0.554 | S108 Dillon 'Boyd' Boyd said 'Stench, I hit that walrus, th… | E118 Odette is no longer on an insulting spree against Sten… |  |

## Interpretation (for the author)

- Most pairs change and become more on-topic → adopt masking.
- Most pairs change and become nonsense → names were the only signal.
- Pairs barely change → names weren't driving the matches.

