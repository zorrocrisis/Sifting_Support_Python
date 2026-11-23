# Pilot report — two-channel sifting (Week 0, reference: s1_selected)

Generated 2026-11-21 by `python -m experiments.pilot.run_all --reference s1_selected --cc-candidates all`. Corpus: one colony; session 2 = `SimulatedDay2/formatted_event_logs.txt` (truncated `Ackmann` line removed), reference set `s1_selected` = `Test Scenarios/SiftingChannels/SimulatedDay1/selected_reference_logs.txt` (13 events lines). NCD concatenation order: event first, as in the game. CC candidates: all session-2 events.

## Decision

**Test 1 fails only for NCD: commit, with embedding-based CC.**

## Results

| test | status | details |
|---|---|---|
| A1 NCD finds continuity | fail | ncd: R@5 0.33, R@10 0.35, MRR 0.40; embedding: R@5 0.64, R@10 0.65, MRR 0.49 |
| A2 name masking | done (interpretation on hold) | per_colonist: 0% of top-6 pairs changed, actor match 33%→33%, NCD R@5 0.33→0.33; single: 0% of top-6 pairs changed, actor match 33%→33%, NCD R@5 0.33→0.33; removed: 0% of top-6 pairs changed, actor match 33%→33%, NCD R@5 0.33→0.33 |
| A3 redundancy control | pass | nearest: 3 lines, CC red. 0.30, cap: 3 lines, CC red. 0.30, mmr: 3 lines, CC red. 0.30, cap+mmr: 3 lines, CC red. 0.30; best `cap` |
| A4 share as a dial | pass | nearest: ρ(share, topics) -0.96 (first label only -0.96), ρ(share, redundancy) 0.99; cap: ρ(share, topics) -0.96 (first label only -0.96), ρ(share, redundancy) 0.99 |

Per-test reports: `a1_report.md`, `a2_report.md`, `a3_report.md`, `a4_parity.md`, `a4_report.md`, `a5_comparison_sheet.md` (answer key: `a5_answer_key.json`), `a5_tally.md`.

## What the author needs to do


On hold: A2, A5 (A2 interpretation, A5 blind comparison).

## Decision rule

- Tests 1 and 4 pass: commit to the full plan.
- Test 1 fails only for NCD: commit, with embedding-based CC.
- Test 4 fails: find a different main claim before writing hypotheses.
- Test 5 fails but tests 1–4 pass: sifting works; the problem is in generation.

## Caveats

- 3 A1 gold pairs are the reference line's exact description repeated in session 2; see `a1_report.md` for the metrics without them.
- One colony, two sessions, 13 reference lines, 162 distinct session-2 events: every number here is from a very small corpus.
- Seeds only affect the AC, and with `least_frequent` the AC barely changes across seeds 41–45, so the ± over seeds in A4 understates real variability.
- The game's composer counts each paired reference line against the CC quota, so at share 0.5 / total 12 at most 3 reference lines can contribute.
- Reference lines are event logs with their own _ID_s, and the composer removes duplicates by _ID_, so a session-1 log and its exact session-2 repeat can both enter the pool (same text twice).

