"""
Pilot A4 (part 1) -- does the Python pool composition match the game?

  python -m experiments.pilot.a4_parity

For each saved Nov 8 run in Test Scenarios/SiftingChannels/8_11_2026/{0,50,100}PercentAC
(read only), two checks:

  compose  Feed the C#-produced candidate lists (pipeline_anomaly_candidates.txt,
           pipeline_reference_candidates.txt) to compose_pool + merge_pool and compare
           with the C#-produced pool (sifting_channels_short_output.txt). Tests the port
           of FinalPoolComposer / SiftingChannelsUtils in isolation.
  channels Re-run both channels in Python on the same inputs (that run's
           formatted_event_logs.txt and dialogue_logs.txt, AC parameters from its
           select_logs.txt) and compare the candidate lists with the C# ones.

total_log_count is 12 for all three runs; the CC quota is recovered from the
number of pairs requested (2*quota + 2).

Outputs: a4_parity.json, a4_parity.md
"""

import json
import re

from experiments.common import cc, paths
from experiments.common.context import PilotContext
from experiments.common.pool import compose_pool, merge_pool, run_ac
from experiments.common.report import md_table, short, write_json

RUNS = ["0PercentAC", "50PercentAC", "100PercentAC"]
SUFFIX_RE = re.compile(r"(\[x\d+\]\[N?V\])$")
TOTAL = 12


def read_candidates(path):
    header, lines = None, []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("#"):
            header = raw
        elif raw.strip():
            lines.append(raw.strip())
    return header, lines


def split_suffix(line):
    m = SUFFIX_RE.search(line)
    return (line[: m.start()], m.group(1)) if m else (line, "")


def check_compose(run_dir):
    _, ac_lines = read_candidates(run_dir / "pipeline_anomaly_candidates.txt")
    header, ref_lines = read_candidates(run_dir / "pipeline_reference_candidates.txt")
    n_pairs = int(re.search(r"requested (\d+) pairs", header).group(1))
    quota = (n_pairs - 2) // 2 if n_pairs else 0

    suffix = {}
    ac_full, ref_full = [], []
    for line in ac_lines:
        full, sfx = split_suffix(line)
        suffix[full] = sfx
        ac_full.append(full)
    for line in ref_lines:
        full, sfx = split_suffix(line)
        suffix[full] = sfx
        ref_full.append(full)
    pairs = list(zip(ref_full[0::2], ref_full[1::2]))

    ref_logs, ac_logs = compose_pool(pairs, ac_full, TOTAL, quota)
    py_pool = merge_pool(ref_logs, ac_logs, lambda l: suffix.get(l, ""))
    cs_pool = [l.strip() for l in (run_dir / "sifting_channels_short_output.txt").read_text(encoding="utf-8").splitlines()
               if l.strip()]
    return {"quota": quota, "n_pairs": n_pairs, "match": py_pool == cs_pool,
            "same_set": sorted(py_pool) == sorted(cs_pool),
            "only_python": [l for l in py_pool if l not in cs_pool],
            "only_csharp": [l for l in cs_pool if l not in py_pool],
            "python_pool": py_pool}


def check_channels(run_dir):
    params = json.loads((run_dir / "select_logs.txt").read_text(encoding="utf-8"))
    ac_params = {"ncd_threshold": params["ncd_threshold"], "strategy": params["strategy"], "depth": params["depth"]}
    ctx = PilotContext(events_path=run_dir / "formatted_event_logs.txt",
                       dialogue_path=run_dir / "dialogue_logs.txt",
                       session_name=f"nov8_{run_dir.name}")
    _, cs_ac = read_candidates(run_dir / "pipeline_anomaly_candidates.txt")
    header, cs_ref = read_candidates(run_dir / "pipeline_reference_candidates.txt")
    n_pairs = int(re.search(r"requested (\d+) pairs", header).group(1))

    ac = run_ac(ctx.events, params["target_count"], params["seed"], ac_params)
    py_ac = [f + ctx.label_suffix(f) for f in ac["ranked_full"]]
    out = {"ac_match": py_ac == cs_ac, "ac_same_set": sorted(py_ac) == sorted(cs_ac),
           "ac_only_python": [l for l in py_ac if l not in cs_ac],
           "ac_only_csharp": [l for l in cs_ac if l not in py_ac]}
    if n_pairs:
        pairs = cc.select_nearest(ctx.M, n_pairs)
        py_ref = [l + ctx.label_suffix(l) for ev, dl in ctx.pair_lines(pairs) for l in (ev, dl)]
        out.update({"cc_match": py_ref == cs_ref, "cc_same_set": sorted(py_ref) == sorted(cs_ref),
                    "cc_first_mismatch": next((i // 2 for i, (a, b) in enumerate(zip(py_ref, cs_ref)) if a != b), None)})
    return out


def run():
    paths.ensure_out()
    results = {}
    for name in RUNS:
        run_dir = paths.NOV8_DIR / name
        results[name] = {"compose": check_compose(run_dir), "channels": check_channels(run_dir)}

    ok = all(r["compose"]["match"] for r in results.values())
    ch_ok = all(r["channels"]["ac_match"] and r["channels"].get("cc_match", True) for r in results.values())
    summary = {"compose_parity": ok, "channel_parity": ch_ok, "runs": results}
    write_json(paths.OUT_DIR / "a4_parity.json", summary)

    rows = []
    for name, r in results.items():
        c, ch = r["compose"], r["channels"]
        rows.append([name, c["quota"], "yes" if c["match"] else ("same set, other order" if c["same_set"] else "NO"),
                     "yes" if ch["ac_match"] else ("same set" if ch["ac_same_set"] else "NO"),
                     "–" if "cc_match" not in ch else ("yes" if ch["cc_match"] else
                                                      ("same set" if ch["cc_same_set"] else "NO"))])
    L = ["# A4 parity — Python vs the game's Nov 8 pools", "",
         f"Compose parity: **{'PASS' if ok else 'FAIL'}**. Channel parity: **{'PASS' if ch_ok else 'FAIL'}**.", "",
         md_table(["run", "CC quota", "pool identical", "AC candidates identical", "CC pairs identical"], rows), ""]
    for name, r in results.items():
        c = r["compose"]
        if c["only_python"] or c["only_csharp"]:
            L += [f"## {name} differences", ""]
            L += [f"- only Python: {short(l, 100)}" for l in c["only_python"]]
            L += [f"- only C#: {short(l, 100)}" for l in c["only_csharp"]]
            L += [""]
        ch = r["channels"]
        if ch["ac_only_python"] or ch["ac_only_csharp"]:
            L += [f"## {name} AC candidate differences", ""]
            L += [f"- only Python: {short(l, 100)}" for l in ch["ac_only_python"]]
            L += [f"- only C#: {short(l, 100)}" for l in ch["ac_only_csharp"]]
            L += [""]
    (paths.OUT_DIR / "a4_parity.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return summary


def main():
    s = run()
    print(f"A4 parity: compose {'PASS' if s['compose_parity'] else 'FAIL'}, "
          f"channels {'PASS' if s['channel_parity'] else 'FAIL'}")
    for name, r in s["runs"].items():
        print(f"  {name}: pool match={r['compose']['match']} ac={r['channels']['ac_match']} "
              f"cc={r['channels'].get('cc_match', '-')}")


if __name__ == "__main__":
    main()
