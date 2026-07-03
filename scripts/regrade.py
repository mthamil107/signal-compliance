#!/usr/bin/env python
"""Re-grade stored model responses offline (no API calls).

Every RunReport JSON stores the raw model responses, so a change to the grader
can be re-applied to the exact captured outputs without re-querying the models
(which, for reasoning models at their default temperature, would be
non-deterministic anyway). This reproduces the verdicts and score for each
results/<model>.json in place.

Usage:  python scripts/regrade.py [results_dir]
"""

from __future__ import annotations

import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from signalbench.core import Response  # noqa: E402
from signalbench.families import all_families  # noqa: E402
from signalbench.metric import aggregate  # noqa: E402

RESULTS_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(__file__), "..", "results"
)


def _item_index():
    return {it.item_id: (fam, it) for fam in all_families() for it in fam.build_items()}


def main() -> int:
    index = _item_index()
    for path in sorted(glob.glob(os.path.join(RESULTS_DIR, "*.json"))):
        if os.path.basename(path) == "mock_microbench.json":
            continue
        d = json.load(open(path, encoding="utf-8"))
        responses = d.get("responses")
        if not responses:
            print(f"skip {os.path.basename(path)} (no stored responses)")
            continue
        verdicts = []
        for r in responses:
            entry = index.get(r["item_id"])
            if entry is None:
                continue
            fam, item = entry
            resp = Response(
                item_id=r["item_id"],
                text=r.get("text") or "",
                tool_calls=r.get("tool_calls") or [],
                error=r.get("error"),
            )
            verdicts.append(fam.grade(item, resp))
        score = aggregate(verdicts)
        d["verdicts"] = [v.to_dict() for v in verdicts]
        d["score"] = score.to_dict()
        json.dump(d, open(path, "w", encoding="utf-8"), indent=2)
        print(
            f"{d['system']:<26} IBSC={score.ibsc_score:.3f}  "
            f"under={score.under_compliance_rate:.2f} over={score.over_compliance_rate:.2f} "
            f"FTR={score.ftr:.2f}  n={score.n_items}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
