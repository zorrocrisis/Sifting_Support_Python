# Pilot report — two-channel sifting (Week 0, reference: dialogue)

Generated 2026-11-21 by `python -m experiments.pilot.run_all --reference dialogue --cc-candidates filtered`. Corpus: one colony; session 2 = `SimulatedDay2/formatted_event_logs.txt` (truncated `Ackmann` line removed), past dialogue = `dialogue_logs.txt` (8 lines spoken in session 1, S116 removed). NCD concatenation order: event first, as in the game. CC candidates: only session 2's cluster representatives at NCD threshold 0.5 (the AC's logs after filtering, before traversal).

## Decision

**Test 1 fails for both NCD and embeddings: neither finds the author's continuity matches, so CC retrieval needs rethinking before committing (not covered by the handoff's rule).**

## Results

| test | status | details |
|---|---|---|
| A1 NCD finds continuity | fail | ncd: R@5 0.00, R@10 0.32, MRR 0.09; embedding: R@5 0.29, R@10 0.45, MRR 0.31 |
| A2 name masking | done (interpretation on hold) | per_colonist: 33% of top-6 pairs changed, actor match 100%→100%, NCD R@5 0.00→0.14; single: 67% of top-6 pairs changed, actor match 100%→100%, NCD R@5 0.00→0.14; removed: 50% of top-6 pairs changed, actor match 100%→100%, NCD R@5 0.00→0.14 |
| A3 redundancy control | pass | nearest: 3 lines, CC red. 0.43, cap: 2 lines, CC red. 0.40, mmr: 3 lines, CC red. 0.35, cap+mmr: 3 lines, CC red. 0.35; best `mmr` |
| A4 share as a dial | pass | nearest: ρ(share, topics) -0.82 (first label only -0.46), ρ(share, redundancy) 0.99; mmr: ρ(share, topics) -0.79 (first label only -0.34), ρ(share, redundancy) 0.99 |

Per-test reports: `a1_report.md`, `a2_report.md`, `a3_report.md`, `a4_parity.md`, `a4_report.md`, `a5_comparison_sheet.md` (answer key: `a5_answer_key.json`), `a5_tally.md`.

## What the author needs to do


On hold: A2, A5 (A2 interpretation, A5 blind comparison).

## Decision rule

- Tests 1 and 4 pass: commit to the full plan.
- Test 1 fails only for NCD: commit, with embedding-based CC.
- Test 4 fails: find a different main claim before writing hypotheses.
- Test 5 fails but tests 1–4 pass: sifting works; the problem is in generation.

## Caveats

- A4's pass depends on multi-topic tags (e.g. `hunting/fight/raid`): counting only each tag's first topic, ρ(share, topics) misses the threshold for nearest, mmr.
- One colony, two sessions, 8 reference lines, 162 distinct session-2 events: every number here is from a very small corpus.
- Seeds only affect the AC, and with `least_frequent` the AC barely changes across seeds 41–45, so the ± over seeds in A4 understates real variability.
- The game's composer counts each paired reference line against the CC quota, so at share 0.5 / total 12 at most 3 reference lines can contribute.

