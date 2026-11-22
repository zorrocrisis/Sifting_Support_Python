# Pilot report — two-channel sifting (Week 0, reference: dialogue_prov)

Generated 2026-11-22 by `python -m experiments.pilot.run_all --reference dialogue_prov --cc-candidates all --cc-similarity index`. Corpus: one colony; session 2 = `SimulatedDay2/formatted_event_logs.txt` (truncated `Ackmann` line removed), reference set `dialogue_prov` = `Test Scenarios/SiftingChannels/SimulatedDay2/dialogue_logs.txt` (8 dialogue lines). NCD concatenation order: event first, as in the game. CC candidates: all session-2 events. CC similarity: event indexing (entities, place, log type, NCD text).

## Decision

**Test 1 fails for both NCD and embeddings: neither finds the author's continuity matches, so CC retrieval needs rethinking before committing (not covered by the handoff's rule).**

## Results

| test | status | details |
|---|---|---|
| A1 CC (index) finds continuity | fail | index: R@5 0.47, R@10 0.78, MRR 0.81 |
| A3 redundancy control | pass | nearest: 3 lines, CC red. 0.26, cap: 2 lines, CC red. 0.30, mmr: 3 lines, CC red. 0.26, cap+mmr: 3 lines, CC red. 0.26, mmr_ix: 3 lines, CC red. 0.26, cap+mmr_ix: 3 lines, CC red. 0.26; best `mmr` |
| A4 share as a dial | pass | nearest: ρ(share, topics) -0.81 (first label only -0.81), ρ(share, redundancy) 0.99; mmr: ρ(share, topics) -0.81 (first label only 0.21), ρ(share, redundancy) 0.92 |

Per-test reports: `a1_report.md`, `a2_report.md`, `a3_report.md`, `a4_parity.md`, `a4_report.md`, `a5_comparison_sheet.md` (answer key: `a5_answer_key.json`), `a5_tally.md`.

## What the author needs to do


On hold: A2, A5 (A2 interpretation, A5 blind comparison).

## Decision rule

- Tests 1 and 4 pass: commit to the full plan.
- Test 1 fails only for NCD: commit, with embedding-based CC.
- Test 4 fails: find a different main claim before writing hypotheses.
- Test 5 fails but tests 1–4 pass: sifting works; the problem is in generation.

## Caveats

- A4's pass depends on multi-topic tags (e.g. `hunting/fight/raid`): counting only each tag's first topic, ρ(share, topics) misses the threshold for mmr.
- One colony, two sessions, 8 reference lines, 162 distinct session-2 events: every number here is from a very small corpus.
- Seeds only affect the AC, and with `least_frequent` the AC barely changes across seeds 41–45, so the ± over seeds in A4 understates real variability.
- The game's composer counts each paired reference line against the CC quota, so at share 0.5 / total 12 at most 3 reference lines can contribute.

