"""
Run the whole Week 0 pilot and write out/PILOT_REPORT.md.

  python -m experiments.pilot.run_all [--skip-generation] [--system-certs]

A5 calls the LLM only for pools it hasn't generated before (outputs are cached).
"""

import argparse

from experiments.pilot import (a1_continuity, a2_masking, a3_redundancy, a4_parity, a4_share_sweep,
                               a5_generation, a5_tally, a6_report, make_gold_helper)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip-generation", action="store_true", help="don't run A5 generation")
    ap.add_argument("--system-certs", action="store_true", help="see a5_generation --system-certs")
    a = ap.parse_args()

    make_gold_helper.main()
    print("A1:", a1_continuity.run()["status"])
    a2_masking.run()
    print("A2: done")
    print("A3:", a3_redundancy.run()["status"])
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
    print("Wrote experiments/pilot/out/PILOT_REPORT.md")


if __name__ == "__main__":
    main()
