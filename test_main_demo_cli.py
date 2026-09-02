"""
test_main_demo_cli.py
----------------------
Regression tests for main_demo.py's CLI wrapper -- the headless
preprocess/select/generate_from_logs/generate_from_narrative entry
points the C# mod calls directly.

Design choices, deliberately:

- Heavy/external dependencies (pipeline.run_preprocessing,
  log_selection.select_final_log_pool, story_llm.generate_story_llm)
  are ALWAYS mocked here, never actually invoked. This suite tests
  main_demo.py's own logic (arg handling, JSON shape, error handling,
  metrics logging, the calling CONTRACT to those other modules) -- not
  NCD clustering correctness (see test_tree_utils.py /
  test_log_selection.py for that) and not real LLM calls (no API key
  needed, no cost, no network, no flakiness).

- Several tests assert the EXACT arguments a mock was called with
  (e.g. `mock.assert_called_once_with(...)`), not just that it was
  called. This is deliberate: main_demo.py's calling conventions to
  pipeline/story_llm have changed multiple times already in this
  project's history (positional args, then keyword-only, parameter
  renames), and each change was a real, silent bug at least once. A
  test that only checks "was the mock called" would not have caught
  any of those regressions; asserting the exact call signature would.

- A few tests are explicitly named after and modeled on REAL bugs this
  project has already shipped and fixed once (see each docstring for
  which one). These are the highest-value tests in this file: they
  exist specifically so that class of bug can't silently reappear.

Run with: pytest test_main_demo_cli.py -v
"""

import json
import sys
from unittest.mock import MagicMock, patch

import pytest

import main_demo


# -----------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------
@pytest.fixture
def test_files(tmp_path):
    """A minimal set of on-disk files the CLI functions expect to find."""
    full_log = tmp_path / "all_events.txt"
    full_log.write_text("some raw log content\n", encoding="utf-8")

    bios = tmp_path / "all_events_charactersbios.txt"
    bios.write_text("Ava: a hardy farmer.\n", encoding="utf-8")

    final_log_pool = tmp_path / "all_events_final_logs.txt"
    final_log_pool.write_text(
        "Colonist Ava planted crops.[x5][NV]\nA meteor shower struck the base.[x1][V]\n",
        encoding="utf-8",
    )

    narrative = tmp_path / "narrative.txt"
    narrative.write_text("The colony endured a long winter.", encoding="utf-8")

    return {
        "full_log": str(full_log),
        "bios": str(bios),
        "final_log_pool": str(final_log_pool),
        "narrative": str(narrative),
        "tmp_path": tmp_path,
    }


@pytest.fixture(autouse=True)
def isolated_metrics_log(tmp_path, monkeypatch):
    """
    Every test gets its own RUN_METRICS_LOG_PATH, so tests can't see
    each other's records and running the suite never touches (or
    pollutes) a real run_metrics.jsonl on disk.
    """
    metrics_path = tmp_path / "test_run_metrics.jsonl"
    monkeypatch.setattr(main_demo, "RUN_METRICS_LOG_PATH", str(metrics_path))
    return metrics_path


def read_metrics(metrics_path):
    """Parse every JSON-line record currently in the metrics log."""
    if not metrics_path.exists():
        return []
    return [json.loads(line) for line in metrics_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def fake_pipeline_state(unique_logs=("log A", "log B"), after_filtering=("log A",)):
    return {
        "unique_logs": list(unique_logs),
        "counts": {log: 1 for log in unique_logs},
        "visibility": {log: "NV" for log in unique_logs},
        "view_data": {"unique_logs_after_filtering": list(after_filtering)},
    }


def fake_selection(pool=("log A",), resolved_depth=1):
    return {
        "resolved_depth": resolved_depth,
        "final_log_pool_short": list(pool),
        "final_log_pool_full": [f"FULL {p}" for p in pool],
        "final_log_pool_labels": [f"{p} (x1)" for p in pool],
        "most_anomalous_log": pool[0] if pool else None,
        "highest_ncd": 0.5,
        "error": None,
    }


# -----------------------------------------------------------------------
# print_json
# -----------------------------------------------------------------------
class TestPrintJson:
    def test_emits_literal_unicode_not_escaped(self, capsys):
        """
        Regression test: json.dumps() defaults to ensure_ascii=True,
        which would print curly quotes/em dashes as \\uXXXX escapes.
        This bit us for real once (generated story text came through
        as "colony\\u2019s" instead of "colony's").
        """
        main_demo.print_json({"story": "The colony\u2019s dawn\u2014quiet."})
        out = capsys.readouterr().out
        assert "\u2019" in out
        assert "\\u2019" not in out

    def test_output_is_valid_json(self, capsys):
        main_demo.print_json({"a": 1, "b": [1, 2, 3], "c": None})
        out = capsys.readouterr().out
        assert json.loads(out) == {"a": 1, "b": [1, 2, 3], "c": None}


# -----------------------------------------------------------------------
# _derive_session_id
# -----------------------------------------------------------------------
class TestDeriveSessionId:
    def test_prefers_full_log_path(self):
        metrics = {
            "full_log_path": "/x/2026-08-14_16-29-05/all_events.txt",
            "final_log_pool_path": "/x/OTHER_SESSION/final.txt",
        }
        assert main_demo._derive_session_id(metrics) == "2026-08-14_16-29-05"

    def test_falls_back_to_final_log_pool_path(self):
        metrics = {"final_log_pool_path": "/x/2026-08-14_16-29-05/final.txt"}
        assert main_demo._derive_session_id(metrics) == "2026-08-14_16-29-05"

    def test_falls_back_to_bios_path(self):
        metrics = {"characters_bios_log_path": "/x/2026-08-14_16-29-05/bios.txt"}
        assert main_demo._derive_session_id(metrics) == "2026-08-14_16-29-05"

    def test_returns_none_with_no_usable_path(self):
        metrics = {"final_log_pool_path": None, "characters_bios_log_path": None}
        assert main_demo._derive_session_id(metrics) is None

    def test_returns_none_with_no_path_keys_at_all(self):
        assert main_demo._derive_session_id({"mode": "generate"}) is None


# -----------------------------------------------------------------------
# log_run_metrics
# -----------------------------------------------------------------------
class TestLogRunMetrics:
    def test_appends_one_json_line_with_added_fields(self, isolated_metrics_log):
        main_demo.log_run_metrics({"mode": "preprocess", "success": True})
        records = read_metrics(isolated_metrics_log)
        assert len(records) == 1
        assert records[0]["mode"] == "preprocess"
        assert records[0]["success"] is True
        assert "timestamp" in records[0]
        assert "session_id" in records[0]
        assert "argv" in records[0]

    def test_accumulates_across_multiple_calls_does_not_overwrite(self, isolated_metrics_log):
        """
        This is the entire point of log_run_metrics over write_to_file:
        it must APPEND, not overwrite, so history survives across runs.
        """
        main_demo.log_run_metrics({"mode": "preprocess"})
        main_demo.log_run_metrics({"mode": "select"})
        main_demo.log_run_metrics({"mode": "generate"})
        records = read_metrics(isolated_metrics_log)
        assert [r["mode"] for r in records] == ["preprocess", "select", "generate"]

    def test_never_raises_on_write_failure(self, monkeypatch, capsys):
        """A logging failure must never take down the actual run."""
        monkeypatch.setattr(main_demo, "RUN_METRICS_LOG_PATH", "/nonexistent_dir_xyz/metrics.jsonl")
        main_demo.log_run_metrics({"mode": "preprocess"})  # must not raise
        assert "Warning" in capsys.readouterr().err


# -----------------------------------------------------------------------
# run_preprocess_headless
# -----------------------------------------------------------------------
class TestRunPreprocessHeadless:
    def test_success_prints_expected_shape_and_logs_metrics(self, test_files, isolated_metrics_log, capsys):
        state = fake_pipeline_state(unique_logs=("A", "B", "C"), after_filtering=("A", "C"))
        with patch("pipeline.run_preprocessing", return_value=state) as mock_run:
            main_demo.run_preprocess_headless(test_files["full_log"], test_files["bios"])

        out = json.loads(capsys.readouterr().out)
        assert out["unique_logs"] == ["A", "B", "C"]
        assert out["unique_logs_after_filtering"] == ["A", "C"]
        assert "counts" in out and "visibility" in out

        mock_run.assert_called_once_with(test_files["full_log"], test_files["bios"])

        records = read_metrics(isolated_metrics_log)
        assert len(records) == 1
        assert records[0]["success"] is True
        assert records[0]["unique_log_count"] == 3
        assert records[0]["unique_log_count_after_filtering"] == 2
        assert records[0]["duration_seconds"] >= 0

    def test_resolves_paths_via_pipeline_when_not_given(self, test_files, isolated_metrics_log):
        state = fake_pipeline_state()
        with patch("pipeline.resolve_input_paths", return_value=(test_files["full_log"], test_files["bios"])) as mock_resolve, \
             patch("pipeline.run_preprocessing", return_value=state) as mock_run:
            main_demo.run_preprocess_headless(None, None)

        mock_resolve.assert_called_once()
        mock_run.assert_called_once_with(test_files["full_log"], test_files["bios"])

    def test_failure_still_propagates_with_metrics_logged_first(self, test_files, isolated_metrics_log):
        """
        Contract test: preprocess/select intentionally use try/FINALLY,
        not try/except, so a real failure still crashes the process
        with a non-zero exit code (matching pre-logging behavior, which
        the C# side's exit-code check may depend on) -- while still
        getting a metrics record for the failed run.
        """
        with patch("pipeline.run_preprocessing", side_effect=RuntimeError("simulated failure")):
            with pytest.raises(RuntimeError, match="simulated failure"):
                main_demo.run_preprocess_headless(test_files["full_log"], test_files["bios"])

        records = read_metrics(isolated_metrics_log)
        assert len(records) == 1
        assert records[0]["success"] is False
        assert "simulated failure" in records[0]["error"]
        assert records[0]["unique_log_count"] is None


# -----------------------------------------------------------------------
# run_select_headless
# -----------------------------------------------------------------------
class TestRunSelectHeadless:
    def _args(self, test_files, **overrides):
        defaults = dict(
            full_log=test_files["full_log"], characters_bios_log=test_files["bios"],
            ncd_threshold=0.5, control="fixed_depth", strategy="random", depth=1,
            target_count=2, seed=42,
        )
        defaults.update(overrides)
        return MagicMock(**defaults)

    def test_success_includes_selection_and_per_phase_timing(self, test_files, isolated_metrics_log, capsys):
        state = fake_pipeline_state(unique_logs=("A", "B"), after_filtering=("A",))
        selection = fake_selection(pool=("A",), resolved_depth=1)

        with patch("pipeline.run_preprocessing", return_value=state), \
             patch("log_selection.select_final_log_pool", return_value=selection) as mock_select:
            main_demo.run_select_headless(self._args(test_files))

        out = json.loads(capsys.readouterr().out)
        assert out["final_log_pool_short"] == ["A"]
        assert out["resolved_depth"] == 1

        mock_select.assert_called_once()
        _, kwargs = mock_select.call_args
        assert kwargs["ncd_threshold"] == 0.5
        assert kwargs["control"] == "fixed_depth"
        assert kwargs["strategy"] == "random"
        assert kwargs["depth"] == 1
        assert kwargs["target_count"] == 2
        assert kwargs["seed"] == 42

        records = read_metrics(isolated_metrics_log)
        assert records[0]["preprocessing_duration_seconds"] >= 0
        assert records[0]["selection_duration_seconds"] >= 0
        assert records[0]["total_duration_seconds"] >= 0
        assert records[0]["final_log_pool_size"] == 1

    def test_uses_config_default_threshold_when_none_given(self, test_files):
        state = fake_pipeline_state()
        selection = fake_selection()
        with patch("pipeline.run_preprocessing", return_value=state), \
             patch("log_selection.select_final_log_pool", return_value=selection) as mock_select, \
             patch("config.INITIAL_NCD_THRESHOLD", 0.77):
            main_demo.run_select_headless(self._args(test_files, ncd_threshold=None))

        assert mock_select.call_args.kwargs["ncd_threshold"] == 0.77

    def test_failure_in_selection_still_propagates_with_metrics_logged(self, test_files, isolated_metrics_log):
        state = fake_pipeline_state()
        with patch("pipeline.run_preprocessing", return_value=state), \
             patch("log_selection.select_final_log_pool", side_effect=RuntimeError("selection blew up")):
            with pytest.raises(RuntimeError, match="selection blew up"):
                main_demo.run_select_headless(self._args(test_files))

        records = read_metrics(isolated_metrics_log)
        assert records[0]["success"] is False
        assert records[0]["final_log_pool_size"] is None
        # Preprocessing succeeded before selection failed -- that timing
        # should still be captured even though the overall call failed.
        assert records[0]["preprocessing_duration_seconds"] is not None
        assert records[0]["selection_duration_seconds"] is None


# -----------------------------------------------------------------------
# run_generate_from_logs / run_generate_from_narrative
# (the thin wrappers that build `supporting_content` and delegate)
# -----------------------------------------------------------------------
class TestRunGenerateFromLogs:
    def test_missing_final_log_pool_short_circuits(self, test_files, isolated_metrics_log, capsys):
        args = MagicMock(final_log_pool=None, characters_bios_log=test_files["bios"], generation_mode="narrative")
        main_demo.run_generate_from_logs(args)

        out = json.loads(capsys.readouterr().out)
        assert out["error"] == "generate mode requires --final-log-pool <path>"
        assert out["usage"] is None

        records = read_metrics(isolated_metrics_log)
        assert records[0]["success"] is False

    def test_success_joins_logs_and_delegates_with_correct_kwargs(self, test_files):
        """
        Locks in the exact hand-off contract to run_generate_headless:
        keyword args, log lines joined with a blank line between them.
        """
        args = MagicMock(
            final_log_pool=test_files["final_log_pool"],
            characters_bios_log=test_files["bios"],
            generation_mode="narrative",
        )
        fake_logs = ["Colonist Ava planted crops.[x5][NV]", "A meteor shower struck the base.[x1][V]"]

        with patch("story_llm.load_final_log_pool", return_value=fake_logs) as mock_load, \
             patch.object(main_demo, "run_generate_headless") as mock_generate:
            main_demo.run_generate_from_logs(args)

        mock_load.assert_called_once_with(test_files["final_log_pool"])
        mock_generate.assert_called_once_with(
            bios_path=test_files["bios"],
            supporting_content="\n\n".join(fake_logs),
            generation_mode="narrative",
        )


class TestRunGenerateFromNarrative:
    def test_missing_input_narrative_path_short_circuits(self, isolated_metrics_log, capsys):
        args = MagicMock(input_narrative_path=None, characters_bios_log="bios.txt", generation_mode="narrative")
        main_demo.run_generate_from_narrative(args)

        out = json.loads(capsys.readouterr().out)
        assert out["error"] == "generate mode requires --input-narrative-path <path>"

        records = read_metrics(isolated_metrics_log)
        assert records[0]["success"] is False

    def test_success_reads_narrative_and_forces_dialogue_from_narrative_mode(self, test_files):
        """
        run_generate_from_narrative always forces generation_mode=
        "dialogue_from_narrative", regardless of --generation-mode --
        this is a real, easy-to-accidentally-revert design choice
        (someone "cleaning up" might pass through args.generation_mode
        instead), so it's worth locking in explicitly.
        """
        args = MagicMock(
            input_narrative_path=test_files["narrative"],
            characters_bios_log=test_files["bios"],
            generation_mode="narrative",  # deliberately NOT dialogue_from_narrative
        )

        with patch.object(main_demo, "run_generate_headless") as mock_generate:
            main_demo.run_generate_from_narrative(args)

        mock_generate.assert_called_once_with(
            bios_path=test_files["bios"],
            supporting_content="The colony endured a long winter.",
            generation_mode="dialogue_from_narrative",
        )


# -----------------------------------------------------------------------
# run_generate_headless (the shared LLM-calling core)
# -----------------------------------------------------------------------
class TestRunGenerateHeadless:
    def test_missing_bios_path_short_circuits(self, isolated_metrics_log, capsys):
        main_demo.run_generate_headless(bios_path=None, supporting_content="some logs", generation_mode="narrative")

        out = json.loads(capsys.readouterr().out)
        assert out["error"] == "generate mode requires --bios-log <path>"
        assert out["usage"] is None

    def test_success_calls_generate_story_llm_with_exact_kwargs(self, test_files):
        """
        Locks in the current calling convention: characters_bios=,
        supporting_content=, mode=, return_usage=True, all as keywords.
        This has changed at least twice already (positional ->
        selected_descriptions= -> supporting_content=); asserting the
        exact call is what actually catches the next drift.
        """
        with patch("story_llm.generate_story_llm", return_value=("a story", {"total_tokens": 10})) as mock_gen:
            main_demo.run_generate_headless(
                bios_path=test_files["bios"], supporting_content="the logs", generation_mode="narrative"
            )

        mock_gen.assert_called_once_with(
            characters_bios="Ava: a hardy farmer.\n",
            supporting_content="the logs",
            mode="narrative",
            return_usage=True,
        )

    def test_success_prints_full_result_with_usage(self, test_files, capsys):
        usage = {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120, "model": "some/model"}
        with patch("story_llm.generate_story_llm", return_value=("a generated story", usage)):
            main_demo.run_generate_headless(
                bios_path=test_files["bios"], supporting_content="the logs", generation_mode="narrative"
            )

        out = json.loads(capsys.readouterr().out)
        assert out == {"story": "a generated story", "mode": "narrative", "usage": usage, "error": None}

    def test_failure_still_prints_result_not_silently_empty(self, test_files, capsys):
        """
        REGRESSION TEST for a real, already-shipped-and-fixed bug: an
        earlier version called print_json(story) *inside* the try
        block, so when generate_story_llm raised, nothing was ever
        printed to stdout at all -- the failure was completely silent
        (worse than a crash, since `preprocessJson == null` checks on
        the C# side don't catch an empty string). This test fails if
        that regresses, in either form: printing nothing, or printing
        only the bare story value instead of the wrapped result dict.
        """
        with patch("story_llm.generate_story_llm", side_effect=RuntimeError("simulated LLM failure")):
            main_demo.run_generate_headless(
                bios_path=test_files["bios"], supporting_content="the logs", generation_mode="narrative"
            )

        captured = capsys.readouterr().out
        assert captured.strip() != "", "nothing was printed to stdout on failure"

        out = json.loads(captured)
        assert out["story"] is None
        assert out["usage"] is None
        assert "simulated LLM failure" in out["error"]
        assert out["mode"] == "narrative"

    def test_failure_does_not_crash_process(self, test_files):
        """
        Unlike preprocess/select, generate is designed to degrade
        gracefully (mirrors dashboard.py's generate_story()) -- a
        network/LLM failure must NOT propagate as an exception.
        """
        with patch("story_llm.generate_story_llm", side_effect=RuntimeError("simulated LLM failure")):
            main_demo.run_generate_headless(  # must not raise
                bios_path=test_files["bios"], supporting_content="the logs", generation_mode="narrative"
            )

    def test_usage_is_none_on_failure_in_metrics(self, test_files, isolated_metrics_log):
        with patch("story_llm.generate_story_llm", side_effect=RuntimeError("boom")):
            main_demo.run_generate_headless(
                bios_path=test_files["bios"], supporting_content="the logs", generation_mode="narrative"
            )

        records = read_metrics(isolated_metrics_log)
        assert records[0]["prompt_tokens"] is None
        assert records[0]["completion_tokens"] is None
        assert records[0]["total_tokens"] is None
        assert records[0]["model"] is None

    def test_usage_threaded_through_to_metrics_on_success(self, test_files, isolated_metrics_log):
        usage = {"prompt_tokens": 200, "completion_tokens": 60, "total_tokens": 260, "model": "openai/gpt-oss-20b:free"}
        with patch("story_llm.generate_story_llm", return_value=("a story", usage)):
            main_demo.run_generate_headless(
                bios_path=test_files["bios"], supporting_content="the logs", generation_mode="narrative"
            )

        records = read_metrics(isolated_metrics_log)
        assert records[0]["prompt_tokens"] == 200
        assert records[0]["completion_tokens"] == 60
        assert records[0]["total_tokens"] == 260
        assert records[0]["model"] == "openai/gpt-oss-20b:free"
        assert records[0]["story_length_chars"] == len("a story")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))