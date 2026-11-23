"""
Pilot A6 -- one summary report from the per-test results.

  python -m experiments.pilot.a6_report

Reads out/a*_result.json and out/a4_parity.json and writes out/PILOT_REPORT.md
with each test's status and the decision rule applied to whatever is known.
"""

from datetime import date

from experiments.common import paths
from experiments.common.report import md_table, read_json

# Author decision (2026-11-17): the A2 interpretation and the A5 blind comparison are on hold.
ON_HOLD = {"A2", "A5"}


def _status(r):
    return (r or {}).get("status", "not run")


def decision(a1, a4, a5):
    s1, s4, s5 = _status(a1), _status(a4), _status(a5)
    if s1 == "fail" and not (a1 or {}).get("embedding_passes"):
        return ("Test 1 fails for both NCD and embeddings: neither finds the author's continuity matches, so CC "
                "retrieval needs rethinking before committing (not covered by the handoff's rule)."
                + (" A4 is still pending." if s4 == "pending" else ""))
    if "pending" in (s1, s4) or "not run" in (s1, s4):
        return ("Undecided: A1 and A4 still need the author's gold matches and topic tags "
                "(see 'What the author needs to do').")
    ncd_ok = s1 == "pass"
    emb_ok = (a1 or {}).get("embedding_passes")
    dial_ok = s4 in ("pass", "partial")
    if not dial_ok:
        return "Test 4 fails: find a different main claim before writing hypotheses."
    if ncd_ok:
        base = "Tests 1 and 4 pass: commit to the full plan."
    elif emb_ok:
        base = "Test 1 fails only for NCD: commit, with embedding-based CC."
    else:
        return "Test 1 fails for both NCD and embeddings: CC retrieval needs rethinking before committing."
    if s5 == "done" and "A5" not in ON_HOLD:
        base += " (Check the A5 tally: if readers can't tell the conditions apart, the problem is in generation.)"
    return base


def run():
    paths.ensure_out()
    a1, a2, a3 = (read_json(paths.OUT_DIR / f"a{i}_result.json") for i in (1, 2, 3))
    a4, a5 = read_json(paths.OUT_DIR / "a4_result.json"), read_json(paths.OUT_DIR / "a5_result.json")
    parity = read_json(paths.OUT_DIR / "a4_parity.json")
    nd, ne = (a1 or {}).get("n_dialogue", "?"), (a1 or {}).get("n_events", "?")

    if paths.REFERENCE == "dialogue":
        ref_text = f"past dialogue = `dialogue_logs.txt` ({nd} lines spoken in session 1, S116 removed)"
    else:
        ref_text = (f"reference set `{paths.REFERENCE}` = "
                    f"`{paths.REFERENCE_PATH.relative_to(paths.REPO_ROOT).as_posix()}` ({nd} {paths.REFERENCE_KIND} lines)")
    L = [f"# Pilot report — two-channel sifting (Week 0, reference: {paths.REFERENCE})", "",
         f"Generated {date.today().isoformat()} by "
         f"`python -m experiments.pilot.run_all --reference {paths.REFERENCE} --cc-candidates {paths.CC_CANDIDATES} "
         f"--cc-similarity {paths.CC_SIMILARITY}`. "
         "Corpus: one colony; session 2 = `SimulatedDay2/formatted_event_logs.txt` (truncated `Ackmann` line "
         f"removed), {ref_text}. "
         "NCD concatenation order: event first, as in the game. CC candidates: "
         + ("all session-2 events." if paths.CC_CANDIDATES == "all" else
            f"only session 2's cluster representatives at NCD threshold {paths.CC_FILTER_THRESHOLD} "
            "(the AC's logs after filtering, before traversal).")
         + {"index": " CC similarity: event indexing (entities, place, log type, NCD text).",
            "embed": " CC similarity: sentence embeddings (all-MiniLM-L6-v2 cosine; comparison only)."}
           .get(paths.CC_SIMILARITY, ""), "",
         "## Decision", "", f"**{decision(a1, a4, a5)}**", "",
         "## Results", ""]

    rows = []
    if a1:
        m = a1.get("metrics", {})
        det = ("; ".join(f"{k}: R@5 {v['recall@5']:.2f}, R@10 {v['recall@10']:.2f}, MRR {v['mrr']:.2f}"
                         for k, v in m.items()) or a1.get("status_reason", ""))
        rows.append([f"A1 CC ({(a1 or {}).get('cc_method', 'ncd')}) finds continuity", _status(a1), det])
    if a2:
        def r5(m):
            return "–" if not m else f"{m['recall@5']:.2f}"
        det = "; ".join(f"{mode}: {v['pct_topk_pairs_changed']:.0%} of top-{a2['k']} pairs changed, "
                        f"actor match {a2['actor_match_unmasked']:.0%}→{v['actor_match_masked']:.0%}, "
                        f"NCD R@5 {r5(a2.get('a1_metrics_unmasked'))}→{r5(v.get('a1_metrics_masked'))}"
                        for mode, v in a2["modes"].items())
        rows.append(["A2 name masking",
                     "done (interpretation on hold)" if "A2" in ON_HOLD else _status(a2), det])
    if a3:
        det = ", ".join(f"{v}: {m['dialogue_lines']} lines, CC red. {m['cc_redundancy']:.2f}"
                        for v, m in a3["variants"].items()) + f"; best `{a3['best_variant']}`"
        rows.append(["A3 redundancy control", _status(a3), det])
    if parity:
        rows.append(["A4 parity with game", "pass" if parity["compose_parity"] and parity["channel_parity"] else "fail",
                     "Python pools and channel candidates identical to the 3 saved Nov 8 runs"
                     if parity["compose_parity"] and parity["channel_parity"] else "see a4_parity.md"])
    if a4:
        det = "; ".join(f"{v}: ρ(share, topics) "
                        + ("–" if s["spearman_share_topics"] is None else f"{s['spearman_share_topics']:.2f}")
                        + ("" if s.get("spearman_share_topics_primary") is None
                           else f" (first label only {s['spearman_share_topics_primary']:.2f})")
                        + f", ρ(share, redundancy) {s['spearman_share_redundancy']:.2f}"
                        for v, s in a4["summary"].items())
        rows.append(["A4 share as a dial", _status(a4), det + (f" — {a4['status_reason']}" if a4.get("status_reason") else "")])
    if a5:
        det = (f"{a5.get('answers', 0)} answers" if a5.get("answers") else a5.get("status_reason", "")) \
              + f"; model {a5.get('model')}, variant {a5.get('variant')}"
        if "A5" in ON_HOLD:
            det = "on hold; the existing narratives were generated before the Ackmann/S116 lines were removed, " \
                  "so rerun a5_generation before using them"
        rows.append(["A5 can people tell", "on hold" if "A5" in ON_HOLD else _status(a5), det])
    L += [md_table(["test", "status", "details"], rows), ""]

    L += ["Per-test reports: `a1_report.md`, `a2_report.md`, `a3_report.md`, `a4_parity.md`, `a4_report.md`, "
          "`a5_comparison_sheet.md` (answer key: `a5_answer_key.json`), `a5_tally.md`.", ""]

    todo = []
    if _status(a1) == "pending":
        todo.append("Fill `experiments/pilot/gold_matches.csv` using `out/gold_helper.md`, then rerun.")
    if _status(a4) == "pending":
        todo.append(f"Add topics for the {a4.get('untagged_descriptions')} descriptions listed in "
                    f"`{(paths.OUT_DIR / 'topic_tags_missing.csv').relative_to(paths.PILOT_DIR).as_posix()}` (fill the topic column there), then rerun A4.")
    if a2 and "A2" not in ON_HOLD:
        todo.append("Read the A2 pair lists and decide which interpretation applies (on-topic / nonsense / unchanged).")
    if "A5" in ON_HOLD:
        pass
    elif _status(a5) == "pending":
        todo.append("Write the session-1 summary in `experiments/pilot/session1_summary.md` and rerun "
                    "`python -m experiments.pilot.a5_generation` (cached, no new API calls); hand out "
                    "`out/a5_comparison_sheet.md`, collect answers in `experiments/pilot/a5_answers.csv`, "
                    "then run `python -m experiments.pilot.a5_tally`.")
    L += ["## What the author needs to do", ""] + [f"{i + 1}. {t}" for i, t in enumerate(todo)] + [""]
    if ON_HOLD:
        L += ["On hold: " + ", ".join(sorted(ON_HOLD)) + " (A2 interpretation, A5 blind comparison).", ""]

    L += ["## Decision rule", "",
          "- Tests 1 and 4 pass: commit to the full plan.",
          "- Test 1 fails only for NCD: commit, with embedding-based CC.",
          "- Test 4 fails: find a different main claim before writing hypotheses.",
          "- Test 5 fails but tests 1–4 pass: sifting works; the problem is in generation.", ""]

    caveats = [f"One colony, two sessions, {nd} reference lines, {ne} distinct session-2 events: every number "
               "here is from a very small corpus.",
               "Seeds only affect the AC, and with `least_frequent` the AC barely changes across seeds 41–45, "
               "so the ± over seeds in A4 understates real variability.",
               "The game's composer counts each paired reference line against the CC quota, so at share 0.5 / "
               "total 12 at most 3 reference lines can contribute."]
    if a4 and a4.get("summary"):
        fragile = [v for v, s in a4["summary"].items()
                   if s.get("passes") and (s.get("spearman_share_topics_primary") or 0) > -0.7]
        if fragile:
            caveats.insert(0, "A4's pass depends on multi-topic tags (e.g. `hunting/fight/raid`): counting only "
                              f"each tag's first topic, ρ(share, topics) misses the threshold for {', '.join(fragile)}.")
    if a1 and a1.get("metrics_without_exact_repeats"):
        caveats.insert(0, f"{a1['n_exact_repeat_gold_pairs']} A1 gold pairs are the reference line's exact description "
                          "repeated in session 2; see `a1_report.md` for the metrics without them.")
    sens = (a1 or {}).get("order_sensitivity")
    if sens and sens["mean_topk_overlap_per_dialogue"] < 0.8:
        caveats.append(f"NCD concatenation order matters: only {sens['mean_topk_overlap_per_dialogue']:.0%} top-5 "
                       "overlap per reference line between event-first and dialogue-first.")
    if paths.REFERENCE_KIND == "events":
        caveats.append("Reference lines are event logs with their own _ID_s, and the composer removes duplicates by "
                       "_ID_, so a session-1 log and its exact session-2 repeat can both enter the pool (same text twice).")
    L += ["## Caveats", ""] + [f"- {c}" for c in caveats] + [""]
    (paths.OUT_DIR / "PILOT_REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    run()
    print(f"Wrote {paths.OUT_DIR / 'PILOT_REPORT.md'}")
