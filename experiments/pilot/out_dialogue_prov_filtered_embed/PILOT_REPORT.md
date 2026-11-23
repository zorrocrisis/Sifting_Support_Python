# Pilot report — two-channel sifting (Week 0, reference: dialogue_prov)

Generated 2026-11-22 by `python -m experiments.pilot.run_all --reference dialogue_prov --cc-candidates filtered --cc-similarity embed`. Corpus: one colony; session 2 = `SimulatedDay2/formatted_event_logs.txt` (truncated `Ackmann` line removed), reference set `dialogue_prov` = `Test Scenarios/SiftingChannels/SimulatedDay2/dialogue_logs.txt` (8 dialogue lines). NCD concatenation order: event first, as in the game. CC candidates: only session 2's cluster representatives at NCD threshold 0.5 (the AC's logs after filtering, before traversal). CC similarity: sentence embeddings (all-MiniLM-L6-v2 cosine; comparison only).

## Decision

**Tests 1 and 4 pass: commit to the full plan.**

## Results

| test | status | details |
|---|---|---|
| A1 CC (embed) finds continuity | pass | embed: R@5 0.75, R@10 0.78, MRR 0.77 |
| A3 redundancy control | fail | nearest: 2 lines, CC red. 0.27, cap: 2 lines, CC red. 0.27, mmr: 2 lines, CC red. 0.27, cap+mmr: 2 lines, CC red. 0.27; best `cap` |
| A4 share as a dial | pass | nearest: ρ(share, topics) -0.89 (first label only -0.81), ρ(share, redundancy) 0.87; cap: ρ(share, topics) -0.89 (first label only -0.81), ρ(share, redundancy) 0.87 |

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

