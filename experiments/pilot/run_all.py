"""
Run the whole Week 0 pilot and write <out>/PILOT_REPORT.md.

  python -m experiments.pilot.run_all [--reference dialogue|s1_selected] [--cc-candidates all|filtered]
                                      [--cc-similarity ncd|index] [--no-embeddings]
                                      [--skip-generation] [--skip-masking] [--system-certs]

--reference picks what the CC matches session-2 events against (see
experiments/common/paths.REFERENCES): "dialogue" (session-1 dialogue, default,
results in pilot/out/) or "s1_selected" (the 13 logs the AC selected in session 1,
results in pilot/out_s1_selected/). The same choice can be made for a single
script with the PILOT_REFERENCE environment variable.

The parity check against the Nov 8 game runs only applies to the dialogue
reference (that is what the game ran). A5 calls the LLM only for pools it hasn't
generated before (outputs are cached).
"""

import argparse

from experiments.common import paths


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reference", default=paths.REFERENCE, choices=sorted(paths.REFERENCES))
    ap.add_argument("--cc-candidates", default=paths.CC_CANDIDATES, choices=paths.CC_CANDIDATE_MODES,
                    help="all session-2 events, or only the AC's cluster representatives (results in <out>_filtered/)")
    ap.add_argument("--cc-similarity", default=paths.CC_SIMILARITY, choices=paths.CC_SIMILARITY_MODES,
                    help="NCD, or event indexing (entities, place, type, text; results in <out>_index/)")
    ap.add_argument("--no-embeddings", action="store_true", help="A1 without the embedding reference ranking")
    ap.add_argument("--skip-generation", action="store_true", help="don't run A5 generation")
    ap.add_argument("--skip-masking", action="store_true", help="don't run A2")
    ap.add_argument("--system-certs", action="store_true", help="see a5_generation --system-certs")
    a = ap.parse_args()
    paths.use_reference(a.reference, a.cc_candidates, a.cc_similarity)

    from experiments.pilot import (a1_continuity, a2_masking, a3_redundancy, a4_parity, a4_share_sweep,
                                   a5_generation, a5_tally, a6_report, make_gold_helper)
    print(f"Reference set: {paths.REFERENCE}, CC candidates: {paths.CC_CANDIDATES}, "
          f"CC similarity: {paths.CC_SIMILARITY} -> "
          f"{paths.OUT_DIR.relative_to(paths.REPO_ROOT)}")
    make_gold_helper.main()
    print("A1:", a1_continuity.run(use_embeddings=not a.no_embeddings)["status"])
    if not a.skip_masking and paths.CC_SIMILARITY == "ncd":   # masking only applies to NCD
        a2_masking.run()
        print("A2: done")
    print("A3:", a3_redundancy.run()["status"])
    if paths.REFERENCE == "dialogue" and paths.CC_CANDIDATES == "all" and paths.CC_SIMILARITY == "ncd":
        p = a4_parity.run()
        print("A4 parity:", "pass" if p["compose_parity"] and p["channel_parity"] else "FAIL")
    print("A4:", a4_share_sweep.run()["status"])
    if not a.skip_generation:
        if a.system_certs:
            import truststore
            truststore.inject_into_ssl()
        a5_generation.run()
        a5_tally.run()
        print("A5: sheet ready")
    a6_report.run()
    print(f"Wrote {(paths.OUT_DIR / 'PILOT_REPORT.md').relative_to(paths.REPO_ROOT)}")


if __name__ == "__main__":
    main()
