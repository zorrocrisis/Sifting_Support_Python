# Pilot report — two-channel sifting (Week 0, reference: dialogue)

Generated 2026-11-21 by `python -m experiments.pilot.run_all --reference dialogue --cc-candidates all`. Corpus: one colony; session 2 = `SimulatedDay2/formatted_event_logs.txt` (truncated `Ackmann` line removed), past dialogue = `dialogue_logs.txt` (8 lines spoken in session 1, S116 removed). NCD concatenation order: event first, as in the game. CC candidates: all session-2 events.

## Decision

**Test 1 fails for both NCD and embeddings: neither finds the author's continuity matches, so CC retrieval needs rethinking before committing (not covered by the handoff's rule).**

## Results

| test | status | details |
|---|---|---|
| A1 NCD finds continuity | fail | ncd: R@5 0.10, R@10 0.14, MRR 0.20; embedding: R@5 0.17, R@10 0.18, MRR 0.15 |
| A2 name masking | done (interpretation on hold) | per_colonist: 67% of top-6 pairs changed, actor match 100%→100%, NCD R@5 0.10→0.07; single: 83% of top-6 pairs changed, actor match 100%→100%, NCD R@5 0.10→0.07; removed: 83% of top-6 pairs changed, actor match 100%→100%, NCD R@5 0.10→0.06 |
| A3 redundancy control | pass | nearest: 1 lines, CC red. 0.50, cap: 2 lines, CC red. 0.45, mmr: 3 lines, CC red. 0.38, cap+mmr: 3 lines, CC red. 0.38; best `mmr` |
| A4 parity with game | pass | Python pools and channel candidates identical to the 3 saved Nov 8 runs |
| A4 share as a dial | pass | nearest: ρ(share, topics) -0.89 (first label only -0.53), ρ(share, redundancy) 0.99; mmr: ρ(share, topics) -0.79 (first label only 0.15), ρ(share, redundancy) 0.99 |
| A5 can people tell | on hold | on hold; the existing narratives were generated before the Ackmann/S116 lines were removed, so rerun a5_generation before using them |

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
- NCD concatenation order matters: only 68% top-5 overlap per reference line between event-first and dialogue-first.

