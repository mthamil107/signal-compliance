#!/usr/bin/env python3
"""Render the signalbench leaderboard from a results/ directory.

Run:  python scripts/render_leaderboard.py [--results results/] [--format md|json|table]
"""

from __future__ import annotations

import argparse
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, os.pardir, "src")
if os.path.isdir(_SRC):
    sys.path.insert(0, _SRC)

from signalbench import Leaderboard  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Render the IBSC leaderboard.")
    ap.add_argument("--results", default=os.path.join(_HERE, os.pardir, "results"))
    ap.add_argument("--format", default="table", choices=["md", "json", "table"])
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    lb = Leaderboard.from_results_dir(args.results)
    if not lb.rows:
        print(f"No result JSON files found in {os.path.abspath(args.results)}.")
        print("Run: python scripts/run_microbench.py")
        return 1

    if args.format == "md":
        out = lb.to_markdown()
    elif args.format == "json":
        out = lb.to_json()
    else:
        out = lb.to_table()

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(out + "\n")
        print(f"wrote {args.out}")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
