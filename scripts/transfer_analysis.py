#!/usr/bin/env python
"""Cross-signal transfer analysis: do the five IBSC families measure one ability?

For every system with full family coverage, take its five per-family SRC scores and
compute the pairwise Pearson correlation across systems. If a model good at one signal
type is reliably good at the others (all pairs positively correlated), that is evidence
the families measure ONE underlying ability rather than five separate skills — i.e. that
over- and under-compliance sit on a single axis, which is IBSC's central claim.

Usage: python scripts/transfer_analysis.py [results_dir]
Prints the family-by-family correlation matrix and the mean off-diagonal correlation,
for (a) bare models only and (b) all systems.
"""

from __future__ import annotations

import glob
import json
import math
import os
import sys

FAMS = ["time", "access_deny", "memory_label", "injection", "bot_policy"]
RESULTS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(__file__), "..", "results"
)


def _pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return cov / (sx * sy) if sx and sy else float("nan")


def _collect(bare_only: bool):
    vecs = []
    for f in glob.glob(os.path.join(RESULTS, "*.json")):
        d = json.load(open(f, encoding="utf-8"))
        sysn = d["system"]
        if sysn.startswith("mock"):
            continue
        if bare_only and sysn.startswith("claude-code"):
            continue  # deployed-agent = different harness
        s = d["score"]
        errs = sum(1 for v in d["verdicts"] if v["label"] == "error")
        if errs >= 10:  # tool-less model: degenerate families
            continue
        pf = s.get("per_family", {})
        if all(k in pf for k in FAMS):
            vecs.append([pf[k]["src_balanced"] for k in FAMS])
    return vecs


def _report(label, vecs):
    if len(vecs) < 3:
        print(f"\n[{label}] too few systems ({len(vecs)})")
        return
    cols = {i: [v[i] for v in vecs] for i in range(5)}
    print(f"\n[{label}] {len(vecs)} systems")
    print("             " + " ".join(f"{f[:8]:>8}" for f in FAMS))
    off = []
    for i, a in enumerate(FAMS):
        row = []
        for j, _ in enumerate(FAMS):
            r = _pearson(cols[i], cols[j])
            row.append(r)
            if i < j:
                off.append(r)
        print(f"{a:>12} " + " ".join(f"{r:>8.2f}" for r in row))
    print(f"  mean off-diagonal r = {sum(off)/len(off):+.3f}  "
          f"(range {min(off):+.2f}..{max(off):+.2f}, "
          f"{sum(1 for r in off if r > 0)}/{len(off)} positive)")


def main() -> int:
    _report("bare models (API + tool-capable open)", _collect(bare_only=True))
    _report("all systems (incl. deployed-agent rows)", _collect(bare_only=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
