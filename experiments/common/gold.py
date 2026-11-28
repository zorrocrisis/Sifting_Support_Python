"""
Gold continuity matches (author-written) and retrieval metrics.

gold_matches.csv columns: dialogue_id, expected_event_id, note, dialogue_text
  - dialogue_id: the dialogue line's _ID_ (e.g. S110)
  - expected_event_id: an event code from gold_helper.md (e.g. E042) or any _ID_
    that occurs in the session log (e.g. b146). Several per row are allowed,
    separated by '/' or ';'. Text in [square brackets] is treated as a note.
    Several rows per dialogue are also fine.
  - dialogue_text: filled in by the helper for convenience; ignored when reading.
"""

import csv
import re

import numpy as np

GOLD_COLUMNS = ["dialogue_id", "expected_event_id", "note", "dialogue_text"]


def read_gold(path, ctx):
    """
    Returns (gold, problems):
      gold: {dialogue index: set(event indices)} for dialogue lines with >= 1 expected event
      problems: list of strings (unknown dialogue IDs / event IDs)
    """
    d_by_id = {ctx.dialogue_id(i): i for i in range(len(ctx.dialogue))}
    e_by_desc = {desc: i for i, desc in enumerate(ctx.events.unique)}
    id_to_desc = ctx.events.ids_to_desc()
    code_to_index = ctx.code_to_index
    gold, problems = {}, []

    if not path.exists():
        return gold, [f"{path} does not exist"]

    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            did = (row.get("dialogue_id") or "").strip()
            cell = (row.get("expected_event_id") or "").strip()
            if not did or not cell:
                continue
            if did not in d_by_id:
                problems.append(f"unknown dialogue_id {did!r} (removed from the corpus?)")
                continue
            # Bracketed notes; an unquoted comma inside a note splits the CSV cell, so an
            # unclosed "[..." runs to the end of the cell.
            cell = re.sub(r"\[[^\]]*(\]|$)", " ", cell)
            for code in filter(None, (c.strip() for c in re.split(r"[/;,\s]+", cell))):
                if code in code_to_index:
                    e = code_to_index[code]
                elif code in id_to_desc and id_to_desc[code] in e_by_desc:
                    e = e_by_desc[id_to_desc[code]]
                else:
                    problems.append(f"{did}: unknown event id {code!r}")
                    continue
                gold.setdefault(d_by_id[did], set()).add(e)
    return gold, problems


def map_to_candidates(gold, ctx):
    """
    When the CC may only pick cluster representatives, a gold event that was folded into a
    cluster is represented by that cluster's representative: retrieving the representative
    counts as finding it. Several gold events in one cluster become a single target.
    Unchanged when every event is a candidate.
    """
    return {d: {ctx.representative(e) for e in t} for d, t in gold.items()}


def ranks_of(order, targets):
    """1-based rank of each target event in `order` (a best-first list of event indices)."""
    pos = {e: r + 1 for r, e in enumerate(order)}
    return {e: pos[e] for e in targets}


def strict_retrieval_metrics(orders, gold_original, candidate_mask, ks=(5, 10)):
    """
    Strict scoring for filtered candidates: a gold event counts only if the RC can return that
    exact log. Gold events that aren't candidates are misses (never in any top k); returning their
    cluster's representative doesn't count. Ranks are positions among candidates only.
    A dialogue line whose gold events are all non-candidates scores 0 recall and reciprocal rank 0.
    """
    per = {}
    for d, targets in gold_original.items():
        cand_order = [e for e in orders[d] if candidate_mask[e]]
        pos = {e: r + 1 for r, e in enumerate(cand_order)}
        r = {e: pos.get(e, float("inf")) for e in targets}
        best = min(r.values())
        row = {"ranks": r, "rr": 0.0 if best == float("inf") else 1.0 / best}
        for k in ks:
            row[f"recall@{k}"] = sum(1 for v in r.values() if v <= k) / len(targets)
        per[d] = row
    overall = {}
    if per:
        overall["mrr"] = float(np.mean([v["rr"] for v in per.values()]))
        for k in ks:
            overall[f"recall@{k}"] = float(np.mean([v[f"recall@{k}"] for v in per.values()]))
        overall["n_dialogue_with_gold"] = len(per)
        overall["n_gold_pairs"] = sum(len(t) for t in gold_original.values())
        overall["n_gold_reachable"] = sum(bool(candidate_mask[e]) for t in gold_original.values() for e in t)
    return per, overall


def retrieval_metrics(orders, gold, ks=(5, 10)):
    """
    orders: {dialogue index: best-first event index list}
    gold:   {dialogue index: set(event indices)}
    Per dialogue: Recall@k = share of its expected events in the top k;
    reciprocal rank = 1 / rank of its best-ranked expected event.
    Overall: mean over dialogue lines that have gold.
    """
    per = {}
    for d, targets in gold.items():
        r = ranks_of(orders[d], targets)
        row = {"ranks": r, "rr": 1.0 / min(r.values())}
        for k in ks:
            row[f"recall@{k}"] = sum(1 for v in r.values() if v <= k) / len(targets)
        per[d] = row
    overall = {}
    if per:
        overall["mrr"] = float(np.mean([v["rr"] for v in per.values()]))
        for k in ks:
            overall[f"recall@{k}"] = float(np.mean([v[f"recall@{k}"] for v in per.values()]))
        overall["n_dialogue_with_gold"] = len(per)
        overall["n_gold_pairs"] = sum(len(t) for t in gold.values())
    return per, overall
