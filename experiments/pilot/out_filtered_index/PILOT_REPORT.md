# Pilot report — two-channel sifting (Week 0, reference: dialogue)

Generated 2026-11-22 by `python -m experiments.pilot.run_all --reference dialogue --cc-candidates filtered --cc-similarity index`. Corpus: one colony; session 2 = `SimulatedDay2/formatted_event_logs.txt` (truncated `Ackmann` line removed), past dialogue = `dialogue_logs.txt` (8 lines spoken in session 1, S116 removed). NCD concatenation order: event first, as in the game. CC candidates: only session 2's cluster representatives at NCD threshold 0.5 (the AC's logs after filtering, before traversal). CC similarity: event indexing (entities, place, log type, NCD text).

## Decision

**Test 1 fails for both NCD and embeddings: neither finds the author's continuity matches, so CC retrieval needs rethinking before committing (not covered by the handoff's rule).**

## Results

| test | status | details |
|---|---|---|
| A1 CC (index) finds continuity | fail | index: R@5 0.22, R@10 0.31, MRR 0.27 |
| A3 redundancy control | fail | nearest: 1 lines, CC red. 0.40, cap: 2 lines, CC red. 0.31, mmr: 1 lines, CC red. 0.36, cap+mmr: 2 lines, CC red. 0.31, mmr_ix: 2 lines, CC red. 0.39, cap+mmr_ix: 2 lines, CC red. 0.31; best `cap+mmr` |
| A4 share as a dial | partial | nearest: ρ(share, topics) -0.82 (first label only -0.56), ρ(share, redundancy) 0.99; cap+mmr: ρ(share, topics) -0.67 (first label only 0.06), ρ(share, redundancy) 0.99 |

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

