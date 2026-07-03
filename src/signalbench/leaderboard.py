"""Leaderboard: load / aggregate ScoreReports and render them."""

from __future__ import annotations

import glob
import json
import os

from .metric import FAMILY_ORDER, ScoreReport

__all__ = ["Leaderboard", "LEADERBOARD_COLUMNS"]

LEADERBOARD_COLUMNS = [
    "rank",
    "system",
    "IBSC_Score",
    "IBSC_Score_cal",
    "LSU",
    "ISR",
    "under_compliance_rate",
    "over_compliance_rate",
    "FTR",
    "abstain_rate",
    "SRC_micro",
    "n_items",
    "src_time",
    "src_access_deny",
    "src_memory_label",
    "src_injection",
    "src_bot_policy",
]


def _r(x: float, nd: int = 3) -> float:
    return round(float(x), nd)


class Leaderboard:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def add_report(self, system: str, score: ScoreReport) -> None:
        row = {
            "system": system,
            "IBSC_Score": _r(score.ibsc_score),
            "IBSC_Score_cal": _r(score.ibsc_score_cal),
            "LSU": _r(score.lsu),
            "ISR": _r(score.isr),
            "under_compliance_rate": _r(score.under_compliance_rate),
            "over_compliance_rate": _r(score.over_compliance_rate),
            "FTR": _r(score.ftr),
            "abstain_rate": _r(score.abstain_rate),
            "SRC_micro": _r(score.src_micro),
            "n_items": score.n_items,
        }
        for fam in FAMILY_ORDER:
            block = score.per_family.get(fam, {})
            row[f"src_{fam}"] = _r(block.get("src_balanced", 0.0))
        self.rows.append(row)

    @classmethod
    def from_results_dir(cls, path: str) -> "Leaderboard":
        lb = cls()
        for fp in sorted(glob.glob(os.path.join(path, "*.json"))):
            with open(fp, "r", encoding="utf-8") as fh:
                d = json.load(fh)
            if not d.get("score"):
                continue
            system = d.get("system", os.path.splitext(os.path.basename(fp))[0])
            lb.add_report(system, ScoreReport.from_dict(d["score"]))
        return lb

    def sorted(self) -> list[dict]:
        ordered = sorted(self.rows, key=lambda r: r["IBSC_Score"], reverse=True)
        out = []
        for i, row in enumerate(ordered, start=1):
            r = dict(row)
            r["rank"] = i
            out.append(r)
        return out

    def to_rows(self) -> list[dict]:
        return [{col: row.get(col, "") for col in LEADERBOARD_COLUMNS} for row in self.sorted()]

    def to_json(self) -> str:
        return json.dumps(self.to_rows(), indent=2)

    def to_markdown(self) -> str:
        rows = self.to_rows()
        header = "| " + " | ".join(LEADERBOARD_COLUMNS) + " |"
        sep = "| " + " | ".join("---" for _ in LEADERBOARD_COLUMNS) + " |"
        lines = [header, sep]
        for row in rows:
            lines.append("| " + " | ".join(str(row[c]) for c in LEADERBOARD_COLUMNS) + " |")
        return "\n".join(lines)

    def to_table(self) -> str:
        rows = self.to_rows()
        cols = LEADERBOARD_COLUMNS
        widths = {c: len(c) for c in cols}
        for row in rows:
            for c in cols:
                widths[c] = max(widths[c], len(str(row[c])))
        def fmt(vals):
            return "  ".join(str(v).ljust(widths[c]) for c, v in zip(cols, vals))
        lines = [fmt(cols), fmt(["-" * widths[c] for c in cols])]
        for row in rows:
            lines.append(fmt([row[c] for c in cols]))
        return "\n".join(lines)
