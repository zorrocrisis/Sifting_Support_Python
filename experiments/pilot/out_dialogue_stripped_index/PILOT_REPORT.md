# Pilot report — two-channel sifting (Week 0, reference: dialogue_stripped)

Generated 2026-11-22 by `python -m experiments.pilot.run_all --reference dialogue_stripped --cc-candidates all --cc-similarity index`. Corpus: one colony; session 2 = `SimulatedDay2/formatted_event_logs.txt` (truncated `Ackmann` line removed), reference set `dialogue_stripped` = `Test Scenarios/SiftingChannels/SimulatedDay2/dialogue_logs.txt` (8 dialogue lines). NCD concatenation order: event first, as in the game. CC candidates: all session-2 events. CC similarity: event indexing (entities, place, log type, NCD text).

## Decision

**Test 1 fails for both NCD and embeddings: neither finds the author's continuity matches, so CC retrieval needs rethinking before committing (not covered by the handoff's rule).**

## Results

| test | status | details |
|---|---|---|
| A1 CC (index) finds continuity | fail | index: R@5 0.23, R@10 0.23, MRR 0.42 |
| A3 redundancy control | fail | nearest: 1 lines, CC red. 0.58, cap: 2 lines, CC red. 0.39, mmr: 1 lines, CC red. 0.33, cap+mmr: 2 lines, CC red. 0.30, mmr_ix: 2 lines, CC red. 0.45, cap+mmr_ix: 2 lines, CC red. 0.36; best `cap+mmr` |
| A4 share as a dial | partial | nearest: ρ(share, topics) -0.89 (first label only -0.53), ρ(share, redundancy) 0.99; cap+mmr: ρ(share, topics) -0.70 (first label only -0.08), ρ(share, redundancy) 0.99 |

Per-test reports: `a1_report.md`, `a2_report.md`, `a3_report.md`, `a4_parity.md`, `a4_report.md`, `a5_comparison_sheet.md` (answer key: `a5_answer_key.json`), `a5_tally.md`.

## What the author needs to do


On hold: A2, A5 (A2 interpretation, A5 blind comparison).

## Decision rule

- Tests 1 and 4 pass: commit to the full plan.
- Test 1 fails only for NCD: commit, with embedding-based CC.
- Test 4 fails: find a different main claim before writing hypotheses.
- Test 5 fails but tests 1–4 pass: sifting works; the problem is in generation.

## Caveats

- A4's pass depends on multi-topic tags (e.g. `hunting/fight/raid`): counting only each tag's first topic, ρ(share, topics) misses the threshold for nearest.
- One colony, two sessions, 8 reference lines, 162 distinct session-2 events: every number here is from a very small corpus.
- Seeds only affect the AC, and with `least_frequent` the AC barely changes across seeds 41–45, so the ± over seeds in A4 understates real variability.
- The game's composer counts each paired reference line against the CC quota, so at share 0.5 / total 12 at most 3 reference lines can contribute.

