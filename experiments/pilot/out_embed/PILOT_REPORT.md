# Pilot report — two-channel sifting (Week 0, reference: dialogue)

Generated 2026-11-22 by `python -m experiments.pilot.run_all --reference dialogue --cc-candidates all --cc-similarity embed`. Corpus: one colony; session 2 = `SimulatedDay2/formatted_event_logs.txt` (truncated `Ackmann` line removed), past dialogue = `dialogue_logs.txt` (8 lines spoken in session 1, S116 removed). NCD concatenation order: event first, as in the game. CC candidates: all session-2 events. CC similarity: sentence embeddings (all-MiniLM-L6-v2 cosine; comparison only).

## Decision

**Test 1 fails for both NCD and embeddings: neither finds the author's continuity matches, so CC retrieval needs rethinking before committing (not covered by the handoff's rule).**

## Results

| test | status | details |
|---|---|---|
| A1 CC (embed) finds continuity | fail | embed: R@5 0.17, R@10 0.18, MRR 0.15 |
| A3 redundancy control | pass | nearest: 3 lines, CC red. 0.29, cap: 3 lines, CC red. 0.29, mmr: 2 lines, CC red. 0.23, cap+mmr: 2 lines, CC red. 0.22; best `cap` |
| A4 share as a dial | fail | nearest: ρ(share, topics) -0.61 (first label only 0.04), ρ(share, redundancy) 0.94; cap: ρ(share, topics) -0.58 (first label only 0.45), ρ(share, redundancy) 0.94 |

Per-test reports: `a1_report.md`, `a2_report.md`, `a3_report.md`, `a4_parity.md`, `a4_report.md`, `a5_comparison_sheet.md` (answer key: `a5_answer_key.json`), `a5_tally.md`.

## What the author needs to do


On hold: A2, A5 (A2 interpretation, A5 blind comparison).

## Decision rule

- Tests 1 and 4 pass: commit to the full plan.
- Test 1 fails only for NCD: commit, with embedding-based CC.
- Test 4 fails: find a different main claim before writing hypotheses.
- Test 5 fails but tests 1–4 pass: sifting works; the problem is in generation.

## Caveats

- One colony, two sessions, 8 reference lines, 162 distinct session-2 events: every number here is from a very small corpus.
- Seeds only affect the AC, and with `least_frequent` the AC barely changes across seeds 41–45, so the ± over seeds in A4 understates real variability.
- The game's composer counts each paired reference line against the CC quota, so at share 0.5 / total 12 at most 3 reference lines can contribute.

