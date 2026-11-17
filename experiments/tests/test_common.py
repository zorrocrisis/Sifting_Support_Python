"""Unit tests for the experiment utilities (no corpus files needed).

  .venv/Scripts/python.exe -m pytest experiments/tests -q
"""

import numpy as np

from experiments.common import cc
from experiments.common.data import dedup_key, is_dialogue, parse_line
from experiments.common.masking import NameMasker
from experiments.common.ncd import DIALOGUE_FIRST, EVENT_FIRST, ncd_rect
from experiments.common.pool import compose_pool, merge_pool, pipeline_targets

BIOS = """Name: Lidia 'Stench' Schmitt
Gender: female

Name: Dillon Boyd
Gender: male

Name: Odette O'Neill
Gender: female
"""


def L(tag, ts, id_, desc, vis="V"):
    return f"{vis}._{tag}_Timestamp_{ts}_Location_(1, 0, 1)_ID_{id_}_Actors_X_FullInfo_{desc}"


# --- parsing / dialogue -----------------------------------------------------

def test_parse_and_dedup_key():
    line = L("CL", 5, "b146", "Odette attempted to hit Stench.")
    p = parse_line(line)
    assert p["ts"] == 5 and p["id"] == "b146" and p["tag"] == "CL"
    assert dedup_key(line) == "b146"


def test_is_dialogue():
    assert is_dialogue(L("SL", 1, "S1", "Odette 'Odette' O'Neill said 'Stench, hi.'"))
    assert not is_dialogue(L("SL", 1, "S2", "Stench chatted about tapirs with Odette."))
    assert not is_dialogue(L("CL", 1, "b1", "Boyd said 'x'"))


# --- masking ------------------------------------------------------------------

def test_masking_longest_first_and_consistent():
    m = NameMasker(BIOS)
    assert m.mask("Odette 'Odette' O'Neill said 'Stench, hi.'") == "C3 said 'C1, hi.'"
    assert m.mask("Dillon 'Boyd' Boyd said 'Stench'") == "C2 said 'C1'"
    assert m.mask("Lidia 'Stench' Schmitt hit Boyd") == "C1 hit C2"
    assert m.mask("Stench's rifle") == "C1's rifle"


def test_masking_single_token_and_pawn_ids():
    m = NameMasker(BIOS, single_token="C", mask_pawn_ids=True)
    assert m.mask("Stench fired at Turkey38339 and Boyd") == "C fired at P1 and C"
    assert m.mask("Turkey38339 ran") == "P1 ran"
    assert m.colonists_in("Stench and Odette") == {"C1", "C3"}


# --- NCD ----------------------------------------------------------------------

def test_ncd_rect_shape_and_order():
    D, E = ["Stench said 'raiders at the treeline'"], ["Raiders arrived.", "Stench hauling silver."]
    a = ncd_rect(D, E, order=EVENT_FIRST)
    b = ncd_rect(D, E, order=DIALOGUE_FIRST)
    assert a.shape == (1, 2) and b.shape == (1, 2)
    assert np.all(a > 0) and np.all(b > 0)


# --- CC selectors ---------------------------------------------------------------

def test_selectors():
    M = np.array([[0.1, 0.2, 0.3, 0.9],
                  [0.8, 0.85, 0.9, 0.4]])
    S = np.eye(4)
    S[0, 1] = S[1, 0] = 0.95        # events 0 and 1 are near-duplicates
    near = cc.select_nearest(M, 3)
    assert [(p["d"], p["e"]) for p in near] == [(0, 0), (0, 1), (0, 2)]
    capped = cc.select_cap(M, 3, cap=2)
    assert [(p["d"], p["e"]) for p in capped] == [(0, 0), (0, 1), (1, 3)]
    mmr = cc.select_mmr(M, S, 2, lam=0.5)
    assert mmr[0]["e"] == 0 and mmr[1]["e"] != 1   # the near-duplicate is penalised


# --- pool composition (port of FinalPoolComposer) ---------------------------------

def test_pipeline_targets_rounding():
    assert pipeline_targets(12, 0.5) == (12, 6)
    assert pipeline_targets(12, 0.25) == (12, 3)
    assert pipeline_targets(10, 0.25) == (10, 3)    # 2.5 rounds away from zero, like C#


def test_compose_pairs_whole_and_shared_halves():
    d = L("SL", 1, "S1", "A said 'x'")
    e1, e2, e3 = (L("CL", t, f"b{t}", f"event {t}") for t in (10, 11, 12))
    ac = [L("JOB", t, f"J{t}", f"job {t}") for t in (20, 21, 22, 23)]
    ref, an = compose_pool([(e1, d), (e2, d), (e3, d)], ac, total=5, reference_quota=3)
    assert ref == [e1, d, e2]                # second pair adds one line: its dialogue is already in
    assert an == ac[:2]


def test_compose_skips_overshooting_pair_and_tops_up():
    d1, d2 = L("SL", 1, "S1", "A said 'x'"), L("SL", 2, "S2", "B said 'y'")
    e1, e2 = L("CL", 10, "b1", "event 1"), L("CL", 11, "b2", "event 2")
    ref, an = compose_pool([(e1, d1), (e2, d2)], [], total=4, reference_quota=3)
    # quota 3: first pair (2 lines) fits, second (2 lines) would overshoot -> skipped;
    # no AC logs, so step 3 tops up with the leftover reference lines
    assert ref == [e1, d1, e2, d2] and an == []


def test_topic_files_never_lose_author_tags(tmp_path):
    from experiments.common.topics import read_all_topics, write_topic_template
    main, missing = tmp_path / "topic_tags.csv", tmp_path / "missing.csv"
    main.write_text("description,topic,n_pools\nA,fight,3\n", encoding="utf-8")
    assert write_topic_template(main, {"A": 3, "B": 2}, missing) == 1
    assert main.read_text(encoding="utf-8") == "description,topic,n_pools\nA,fight,3\n"
    missing.write_text("description,topic,n_pools\nB,animals,2\n", encoding="utf-8")   # author tags here
    assert write_topic_template(main, {"A": 3, "B": 2, "C": 1}, missing) == 1
    assert "B,animals" in missing.read_text(encoding="utf-8")                        # not overwritten
    assert read_all_topics(main, missing)[0] == {"A": "fight", "B": "animals"}


def test_merge_sorts_and_dedups():
    a, b = L("CL", 30, "b1", "late"), L("SL", 5, "S1", "early")
    out = merge_pool([a], [b, a], lambda l: "[x1][V]")
    assert out == ["early[x1][V]", "late[x1][V]"]
