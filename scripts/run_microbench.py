#!/usr/bin/env python3
"""Offline IBSC micro-benchmark -- no API key, no network, std-lib only.

Builds all five signal families, runs the deterministic MockProvider under two
reference policies (oracle and always_comply), prints a per-family + overall
condition table (in the spirit of NowBench's condition table), and writes
results/mock_microbench.json for the leaderboard.

Run:  python scripts/run_microbench.py
"""

from __future__ import annotations

import os
import sys

# Make ``import signalbench`` work when run from a source checkout.
_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, os.pardir, "src")
if os.path.isdir(_SRC):
    sys.path.insert(0, _SRC)

from signalbench import Leaderboard, MockProvider, Runner, all_families  # noqa: E402
from signalbench.metric import FAMILY_ORDER  # noqa: E402

RESULTS_DIR = os.path.join(_HERE, os.pardir, "results")


def _print_condition_table(reports: dict) -> None:
    fams = FAMILY_ORDER
    col_w = 14
    header = "policy".ljust(18) + "".join(f.ljust(col_w) for f in fams) + "OVERALL"
    print(header)
    print("-" * len(header))
    for policy, report in reports.items():
        score = report.score
        cells = []
        for f in fams:
            block = score.per_family.get(f, {})
            cells.append(f"{block.get('src_balanced', 0.0):.2f}".ljust(col_w))
        print(policy.ljust(18) + "".join(cells) + f"{score.ibsc_score:.3f}")
    print()


def main() -> int:
    families = all_families()
    reports = {}
    for policy in ("oracle", "always_comply", "always_resist"):
        runner = Runner(MockProvider(policy=policy), families, seed=0)
        reports[policy] = runner.run()

    print("=" * 72)
    print("IBSC micro-benchmark (signalbench) -- offline MockProvider, seed=0")
    print("=" * 72)
    print()
    print("Per-family SRC_balanced by policy (condition table):")
    print()
    _print_condition_table(reports)

    # Detailed summary per policy.
    for policy, report in reports.items():
        s = report.score
        print(f"[{policy}]")
        print(f"  IBSC-Score={s.ibsc_score:.3f}  cal={s.ibsc_score_cal:.3f}  "
              f"LSU={s.lsu:.3f}  ISR={s.isr:.3f}  FTR={s.ftr:.3f}  "
              f"n_items={s.n_items}")
        print(f"  under_compliance_rate={s.under_compliance_rate:.3f}  "
              f"over_compliance_rate={s.over_compliance_rate:.3f}")
        print(f"  verdict counts: {s.counts}")
        print()

    # Leaderboard across the three reference policies.
    lb = Leaderboard()
    for policy, report in reports.items():
        lb.add_report(f"mock:{policy}", report.score)
    print("Leaderboard:")
    print(lb.to_table())
    print()

    # Persist the headline (oracle vs always_comply) for the leaderboard demo.
    os.makedirs(RESULTS_DIR, exist_ok=True)
    for policy in ("oracle", "always_comply"):
        report = reports[policy]
        report.provider_name = f"mock:{policy}"
        out = os.path.join(RESULTS_DIR, f"mock_{policy}.json")
        report.to_json(out)
    # Combined marker file requested by the spec.
    reports["oracle"].provider_name = "mock:oracle"
    reports["oracle"].to_json(os.path.join(RESULTS_DIR, "mock_microbench.json"))
    print(f"Wrote results to {os.path.abspath(RESULTS_DIR)}")

    # Sanity assertions so the demo self-checks.
    assert reports["oracle"].score.ibsc_score == 1.0, "oracle must score 1.0"
    assert reports["always_comply"].score.isr == 0.0, "always_comply must have ISR=0"
    assert reports["always_resist"].score.lsu == 0.0, "always_resist must have LSU=0"
    print("Self-check passed: oracle=1.0, always_comply ISR=0, always_resist LSU=0.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
