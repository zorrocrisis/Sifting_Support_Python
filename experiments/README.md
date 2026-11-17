# Experiments — two-channel sifting

Offline, headless Python on frozen logs. Nothing here changes the game, `sipport.py`, or the corpus folders.

## Week 0 pilot

```
.venv/Scripts/python.exe -m experiments.pilot.run_all
```

Writes everything to `experiments/pilot/out/`, with the summary in `out/PILOT_REPORT.md`. Each test also runs on its own:

| test | command | needs from the author |
|---|---|---|
| A1 NCD vs embeddings | `python -m experiments.pilot.a1_continuity` | `pilot/gold_matches.csv` (use `out/gold_helper.md`) |
| A2 name masking | `python -m experiments.pilot.a2_masking` | judging the pair lists |
| A3 cap / MMR | `python -m experiments.pilot.a3_redundancy` | (gold, to define "relevant" lines) |
| A4 parity with game | `python -m experiments.pilot.a4_parity` | — |
| A4 share sweep | `python -m experiments.pilot.a4_share_sweep` | `pilot/topic_tags.csv` topics |
| A5 blind comparison | `python -m experiments.pilot.a5_generation [--system-certs]`, then `a5_tally` | `pilot/session1_summary.md`, reader answers in `pilot/a5_answers.csv` |
| A6 report | `python -m experiments.pilot.a6_report` | — |

Inputs (read only): `Test Scenarios/SiftingChannels/SimulatedDay2/` (session 2 events, bios, past dialogue). The A4 parity check reads the saved Nov 8 runs in `8_11_2026/` and never writes there. Logs are copied to `out/cache/` before the existing readers touch them, because `extract_descriptions` writes a sidecar file next to its input.

Choices that matter:

- **NCD concatenation order** is event first, `C(event + dialogue)`, as in the game's reference channel (`ncd.ncd_rect(order=...)`). A1 reports how much rankings change with the other order.
- **Masking** has two modes: `per_colonist` (C1, C2, …, as specified) and `single` (every colonist becomes `C`).
- **Pool composition** is a line-for-line port of `FinalPoolComposer` and `SiftingChannelsUtils.SiftLogs` (`common/pool.py`). It is checked against the game's saved pools by `a4_parity`.
- **Dialogue detection** is `common/data.is_dialogue`, the one place to change when a `DLG_` tag exists.
- **API key:** A5 uses `story_llm.generate_story_llm` unchanged, with `GEMINI_API_KEY`, `models/`, and `prompts/narrative.txt`. Behind a TLS-inspecting proxy, pass `--system-certs`.

Unit tests: `.venv/Scripts/python.exe -m pytest experiments/tests -q`

Extra packages, installed with `uv pip install --python .venv/Scripts/python.exe`: `sentence-transformers` and `matplotlib`.
