"""
Pilot A5 -- can people tell? (generation)

  python -m experiments.pilot.a5_generation [--variant mmr] [--seed 42] [--shuffle-seed 7]

For share in {0, 0.5, 1} (one AC seed, best CC variant from A3), composes the
pool exactly as the game does and generates a narrative with the existing
story_llm.generate_story_llm(mode="narrative"): same model (models/model_URL.txt),
same prompt (prompts/narrative.txt), no cast block (the Nov 8 runs had an empty
one). generate_story_llm doesn't set a temperature, so every call uses the
provider default -- the same for all conditions.

LLM outputs are cached in out/llm_cache/ (kept in git) keyed by a hash of
(pool, prompt text, model, repeat index); rerunning never calls the API twice
for the same input.

Builds a blind comparison sheet (a5_comparison_sheet.md): the author's
session-1 summary (from experiments/pilot/session1_summary.md), then the 3 pairs of narratives in random order with
random A/B sides. The answer key is saved separately (a5_answer_key.json).
Answers go in experiments/pilot/a5_answers.csv; tally with a5_tally.py.
"""

import argparse
import hashlib
import json
import random
from itertools import combinations

from experiments.common import paths
from experiments.common.context import PilotContext
from experiments.common.report import read_json, write_json
from experiments.common.simulate import build_pool

SHARES = (0.0, 0.5, 1.0)
ANSWERS_PATH = paths.PILOT_DIR / "a5_answers.csv"
# Author-written; the sheet is regenerated on every run, so the summary lives in its own file.
SUMMARY_PATH = paths.PILOT_DIR / "session1_summary.md"
SUMMARY_PLACEHOLDER = "> _[Author: replace this line with a short summary of session 1, then rerun a5_generation.]_"
QUESTIONS = ("Which connects more to what happened before?", "Which is more surprising?")


def _llm_config():
    import story_llm
    return {"model": story_llm.get_model_url(), "prompt": story_llm.get_prompt("narrative")}


def generate_cached(bios, pool_lines, repeat=0):
    import story_llm
    cfg = _llm_config()
    content = "\n\n".join(pool_lines)          # same joining as sipport.run_generate_from_logs
    key = hashlib.sha256(json.dumps([content, bios, cfg["prompt"], cfg["model"], repeat]).encode()).hexdigest()[:20]
    cache_dir = paths.OUT_DIR / "llm_cache"     # kept in git: frozen LLM outputs
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = cache_dir / f"{key}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8")), True
    story, usage = story_llm.generate_story_llm(bios, content, mode="narrative", return_usage=True)
    rec = {"story": story, "usage": usage, "model": cfg["model"], "repeat": repeat, "key": key}
    cache.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    return rec, False


def run(variant=None, seed=42, shuffle_seed=7):
    paths.ensure_out()
    a3 = read_json(paths.OUT_DIR / "a3_result.json")
    variant = variant or (a3 or {}).get("best_variant") or "mmr"
    ctx = PilotContext()

    narratives = {}
    for share in SHARES:
        built = build_pool(ctx, share, 12, variant=variant, seed=seed)
        rec, cached = generate_cached(ctx.bios_text, built["pool"])
        narratives[share] = {"pool": built["pool"], "story": rec["story"], "model": rec["model"],
                             "usage": rec.get("usage"), "cached": cached}

    rng = random.Random(shuffle_seed)
    pairs = list(combinations(SHARES, 2))
    rng.shuffle(pairs)
    if not SUMMARY_PATH.exists():
        SUMMARY_PATH.write_text(SUMMARY_PLACEHOLDER + "\n", encoding="utf-8")
    summary = SUMMARY_PATH.read_text(encoding="utf-8").strip()
    key, L = [], ["# Blind comparison", "",
                  "## What happened before (session 1)", "", summary, "",
                  "For each pair, read both stories and answer:", ""]
    L += [f"{i + 1}. {q} (A or B)" for i, q in enumerate(QUESTIONS)] + [""]
    for n, (x, y) in enumerate(pairs, start=1):
        a, b = (x, y) if rng.random() < 0.5 else (y, x)
        key.append({"pair": n, "A": a, "B": b})
        L += [f"## Pair {n}", "", "### Story A", "", narratives[a]["story"].strip(), "",
              "### Story B", "", narratives[b]["story"].strip(), "",
              f"- Q1 ({QUESTIONS[0]}): ____", f"- Q2 ({QUESTIONS[1]}): ____", ""]
    (paths.OUT_DIR / "a5_comparison_sheet.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    write_json(paths.OUT_DIR / "a5_answer_key.json",
               {"pairs": key, "variant": variant, "seed": seed, "shuffle_seed": shuffle_seed,
                "questions": list(QUESTIONS)})
    write_json(paths.OUT_DIR / "a5_narratives.json", {str(k): v for k, v in narratives.items()})

    if not ANSWERS_PATH.exists():
        ANSWERS_PATH.write_text("rater,pair,q1,q2\n", encoding="utf-8")

    result = {"test": "A5", "variant": variant, "seed": seed, "model": narratives[SHARES[0]]["model"],
              "n_pairs": len(pairs), "status": "pending",
              "status_reason": "awaiting reader answers in a5_answers.csv",
              "api_calls": sum(not v["cached"] for v in narratives.values())}
    write_json(paths.OUT_DIR / "a5_result.json", result)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variant")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--shuffle-seed", type=int, default=7)
    ap.add_argument("--system-certs", action="store_true",
                    help="verify HTTPS against the OS certificate store (needs `truststore`), "
                         "for networks with a TLS-inspecting proxy")
    a = ap.parse_args()
    if a.system_certs:
        import truststore
        truststore.inject_into_ssl()
    r = run(a.variant, a.seed, a.shuffle_seed)
    print(f"A5: sheet written ({r['api_calls']} new API calls, model {r['model']})")


if __name__ == "__main__":
    main()
