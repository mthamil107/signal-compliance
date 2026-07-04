#!/usr/bin/env python
"""Run the Claude Code (deployed-agent) provider over all IBSC families.

Uses the local `claude` CLI (subscription, no API credit). Results are written
to results/ with a `claude-code_` prefix and are a SEPARATE, labeled datapoint —
Claude Code runs under its own system prompt with tools disabled, so this is not
comparable to the bare-model API rows and must not be merged into that leaderboard.

Usage:
    python scripts/run_claudecode.py                         # haiku, all families
    python scripts/run_claudecode.py --model claude-sonnet-5
    python scripts/run_claudecode.py --families memory_label,injection
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from signalbench.families import FAMILIES, all_families, get_family  # noqa: E402
from signalbench.providers.claudecode_provider import ClaudeCodeProvider  # noqa: E402
from signalbench.runner import Runner  # noqa: E402

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


def _families(spec: str):
    if spec in ("all", "", None):
        return all_families()
    return [get_family(s.strip()) for s in spec.split(",") if s.strip()]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default="claude-haiku-4-5-20251001")
    ap.add_argument("--families", default="all")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)

    provider = ClaudeCodeProvider(model=args.model)
    fams = _families(args.families)
    print(f"Claude Code (deployed agent): {args.model}  |  families: "
          f"{','.join(f.name for f in fams)}")

    report = Runner(provider, fams, seed=args.seed).run()
    report.provider_name = provider.name
    safe = provider.name.replace(":", "_").replace("/", "_")
    out = os.path.join(RESULTS_DIR, f"{safe}.json")
    report.to_json(out)

    s = report.score
    cost = sum((r.raw or {}).get("cost_usd") or 0.0 for r in report.responses)
    n_err = sum(1 for v in report.verdicts if v.label.value == "error")
    print(f"\nIBSC={s.ibsc_score:.3f}  LSU={s.lsu:.2f}  ISR={s.isr:.2f}  "
          f"under={s.under_compliance_rate:.2f}  over={s.over_compliance_rate:.2f}  "
          f"FTR={s.ftr:.2f}  errors={n_err}/{s.n_items}")
    print("per-family:", {f: round(b["src_balanced"], 3) for f, b in s.per_family.items()})
    print(f"subscription cost this run: ${cost:.3f}")
    print(f"wrote {os.path.relpath(out)}")
    print("\nNOTE: deployed-agent datapoint (own system prompt, tools disabled); "
          "report separately from the API-model leaderboard.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
