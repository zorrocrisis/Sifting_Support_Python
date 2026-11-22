# A4 — Ratio as a dial (no LLM)

**Status: FAIL**

Shares [0.0, 0.25, 0.5, 0.75, 1.0] × seeds [41, 42, 43, 44, 45] × variants ['nearest', 'mmr_ix'], total 12. Pass rule: Spearman rho(share, distinct topics) <= -0.7.

Parity with the game's composition: see `a4_parity.md`.

![metrics](a4_metrics.png)

## `nearest`

Spearman ρ(share, distinct topics): 0.13 (first label only: 0.13); ρ(share, redundancy): 0.93

| share | distinct_topics | distinct_topics_primary | redundancy | dialogue_lines | ac_cc_overlap |
|---|---|---|---|---|---|
| 0.000 | 8.00 ± 0.00 | 6.00 ± 0.00 | 0.21 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| 0.250 | 8.00 ± 0.00 | 6.00 ± 0.00 | 0.24 ± 0.00 | 1.00 ± 0.00 | 2.40 ± 0.49 |
| 0.500 | 8.80 ± 0.40 | 6.80 ± 0.40 | 0.28 ± 0.01 | 3.00 ± 0.00 | 2.80 ± 0.98 |
| 0.750 | 8.40 ± 0.49 | 6.40 ± 0.49 | 0.34 ± 0.02 | 3.00 ± 0.00 | 4.60 ± 1.96 |
| 1.000 | 8.00 ± 0.00 | 6.00 ± 0.00 | 0.34 ± 0.00 | 4.00 ± 0.00 | 4.60 ± 1.96 |

## `mmr_ix`

Spearman ρ(share, distinct topics): -0.23 (first label only: -0.23); ρ(share, redundancy): 0.99

| share | distinct_topics | distinct_topics_primary | redundancy | dialogue_lines | ac_cc_overlap |
|---|---|---|---|---|---|
| 0.000 | 8.00 ± 0.00 | 6.00 ± 0.00 | 0.21 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| 0.250 | 8.00 ± 0.00 | 6.00 ± 0.00 | 0.24 ± 0.00 | 1.00 ± 0.00 | 1.80 ± 0.98 |
| 0.500 | 7.80 ± 0.40 | 5.80 ± 0.40 | 0.26 ± 0.01 | 3.00 ± 0.00 | 3.20 ± 1.47 |
| 0.750 | 7.40 ± 0.49 | 5.40 ± 0.49 | 0.29 ± 0.01 | 4.00 ± 0.00 | 5.60 ± 1.96 |
| 1.000 | 8.00 ± 0.00 | 6.00 ± 0.00 | 0.31 ± 0.00 | 6.00 ± 0.00 | 6.00 ± 2.45 |

