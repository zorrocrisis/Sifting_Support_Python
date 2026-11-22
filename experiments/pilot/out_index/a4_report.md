# A4 — Ratio as a dial (no LLM)

**Status: PARTIAL**

Shares [0.0, 0.25, 0.5, 0.75, 1.0] × seeds [41, 42, 43, 44, 45] × variants ['nearest', 'cap+mmr'], total 12. Pass rule: Spearman rho(share, distinct topics) <= -0.7.

Parity with the game's composition: see `a4_parity.md`.

![metrics](a4_metrics.png)

## `nearest`

Spearman ρ(share, distinct topics): -0.82 (first label only: -0.56); ρ(share, redundancy): 0.99

| share | distinct_topics | distinct_topics_primary | redundancy | dialogue_lines | ac_cc_overlap |
|---|---|---|---|---|---|
| 0.000 | 8.00 ± 0.00 | 6.00 ± 0.00 | 0.21 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| 0.250 | 9.00 ± 0.00 | 9.00 ± 0.00 | 0.26 ± 0.01 | 1.00 ± 0.00 | 0.00 ± 0.00 |
| 0.500 | 8.00 ± 0.00 | 8.00 ± 0.00 | 0.30 ± 0.00 | 1.00 ± 0.00 | 0.00 ± 0.00 |
| 0.750 | 6.00 ± 0.00 | 6.00 ± 0.00 | 0.38 ± 0.01 | 1.00 ± 0.00 | 0.00 ± 0.00 |
| 1.000 | 3.00 ± 0.00 | 3.00 ± 0.00 | 0.46 ± 0.00 | 1.00 ± 0.00 | 0.60 ± 0.49 |

## `cap+mmr`

Spearman ρ(share, distinct topics): -0.67 (first label only: -0.25); ρ(share, redundancy): 0.99

| share | distinct_topics | distinct_topics_primary | redundancy | dialogue_lines | ac_cc_overlap |
|---|---|---|---|---|---|
| 0.000 | 8.00 ± 0.00 | 6.00 ± 0.00 | 0.21 ± 0.00 | 0.00 ± 0.00 | 0.00 ± 0.00 |
| 0.250 | 9.00 ± 0.00 | 8.00 ± 0.00 | 0.25 ± 0.01 | 1.00 ± 0.00 | 1.80 ± 0.98 |
| 0.500 | 8.40 ± 0.49 | 7.40 ± 0.49 | 0.27 ± 0.01 | 2.00 ± 0.00 | 3.80 ± 1.47 |
| 0.750 | 7.40 ± 0.49 | 6.40 ± 0.49 | 0.29 ± 0.00 | 3.00 ± 0.00 | 4.80 ± 1.47 |
| 1.000 | 7.00 ± 0.00 | 6.00 ± 0.00 | 0.30 ± 0.00 | 4.00 ± 0.00 | 4.80 ± 1.47 |

