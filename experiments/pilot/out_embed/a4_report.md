# A4 — Ratio as a dial (no LLM)

**Status: FAIL**

Shares [0.0, 0.25, 0.5, 0.75, 1.0] × seeds [41, 42, 43, 44, 45] × variants ['nearest', 'cap'], total 12. Pass rule: Spearman rho(share, distinct topics) <= -0.7.

Parity with the game's composition: see `a4_parity.md`.

![metrics](a4_metrics.png)

## `nearest`

Spearman ρ(share, distinct topics): -0.61 (first label only: 0.04); ρ(share, redundancy): 0.94

| share | distinct_topics | distinct_topics_primary | redundancy | dialogue_lines | ac_cc_overlap |
|---|---|---|---|---|---|
| 0.000 | 8.00 ± 0.00 | 6.00 ± 0.00 | 0.21 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| 0.250 | 9.00 ± 0.00 | 7.00 ± 0.00 | 0.21 ± 0.00 | 1.00 ± 0.00 | 0.00 ± 0.00 |
| 0.500 | 9.00 ± 0.00 | 9.00 ± 0.00 | 0.25 ± 0.00 | 3.00 ± 0.00 | 0.60 ± 0.49 |
| 0.750 | 7.40 ± 0.49 | 7.40 ± 0.49 | 0.30 ± 0.01 | 3.00 ± 0.00 | 0.60 ± 0.49 |
| 1.000 | 6.00 ± 0.00 | 6.00 ± 0.00 | 0.31 ± 0.00 | 4.00 ± 0.00 | 0.60 ± 0.49 |

## `cap`

Spearman ρ(share, distinct topics): -0.58 (first label only: 0.45); ρ(share, redundancy): 0.94

| share | distinct_topics | distinct_topics_primary | redundancy | dialogue_lines | ac_cc_overlap |
|---|---|---|---|---|---|
| 0.000 | 8.00 ± 0.00 | 6.00 ± 0.00 | 0.21 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| 0.250 | 9.00 ± 0.00 | 7.00 ± 0.00 | 0.21 ± 0.00 | 1.00 ± 0.00 | 0.00 ± 0.00 |
| 0.500 | 9.00 ± 0.00 | 9.00 ± 0.00 | 0.25 ± 0.00 | 3.00 ± 0.00 | 0.80 ± 0.98 |
| 0.750 | 7.40 ± 0.49 | 7.40 ± 0.49 | 0.28 ± 0.01 | 4.00 ± 0.00 | 0.80 ± 0.98 |
| 1.000 | 7.00 ± 0.00 | 7.00 ± 0.00 | 0.30 ± 0.00 | 5.00 ± 0.00 | 0.80 ± 0.98 |

