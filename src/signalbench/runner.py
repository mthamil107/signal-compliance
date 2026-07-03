"""Runner: drive a Provider over SignalFamilies and collect a RunReport."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional

from .core import Item, Response, Verdict
from .families.base import SignalFamily
from .metric import ScoreReport, aggregate
from .providers.base import Provider

__all__ = ["Runner", "RunReport"]


@dataclass
class RunReport:
    provider_name: str
    seed: int
    items: list[Item] = field(default_factory=list)
    responses: list[Response] = field(default_factory=list)
    verdicts: list[Verdict] = field(default_factory=list)
    score: Optional[ScoreReport] = None

    def to_json(self, path: Optional[str] = None) -> str:
        by_id = {r.item_id: r for r in self.responses}
        payload = {
            "system": self.provider_name,
            "seed": self.seed,
            "score": self.score.to_dict() if self.score else {},
            "verdicts": [v.to_dict() for v in self.verdicts],
            # store the raw observed responses so a grading change can be
            # re-applied offline without re-querying the models.
            "responses": [
                {
                    "item_id": r.item_id,
                    "text": r.text,
                    "tool_calls": r.tool_calls,
                    "error": r.error,
                }
                for r in (by_id.get(v.item_id) for v in self.verdicts)
                if r is not None
            ],
        }
        text = json.dumps(payload, indent=2)
        if path:
            import os

            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
        return text

    @classmethod
    def from_json(cls, path: str) -> "RunReport":
        with open(path, "r", encoding="utf-8") as fh:
            d = json.load(fh)
        verdicts = [Verdict.from_dict(v) for v in d.get("verdicts", [])]
        score = ScoreReport.from_dict(d["score"]) if d.get("score") else None
        return cls(
            provider_name=d.get("system", "unknown"),
            seed=int(d.get("seed", 0)),
            items=[],
            responses=[],
            verdicts=verdicts,
            score=score,
        )


class Runner:
    def __init__(
        self, provider: Provider, families: list[SignalFamily], seed: int = 0
    ):
        self.provider = provider
        self.families = families
        self.seed = seed

    def run_family(self, family: SignalFamily, n: Optional[int]) -> list[Verdict]:
        items = family.build_items(seed=self.seed, n=n)
        responses = self.provider.batch(items)
        by_id = {r.item_id: r for r in responses}
        return [family.grade(it, by_id[it.item_id]) for it in items]

    def run(self, n_per_family: Optional[int] = None) -> RunReport:
        all_items: list[Item] = []
        all_responses: list[Response] = []
        all_verdicts: list[Verdict] = []
        for family in self.families:
            items = family.build_items(seed=self.seed, n=n_per_family)
            responses = self.provider.batch(items)
            by_id = {r.item_id: r for r in responses}
            for it in items:
                resp = by_id[it.item_id]
                all_items.append(it)
                all_responses.append(resp)
                all_verdicts.append(family.grade(it, resp))
        score = aggregate(all_verdicts)
        return RunReport(
            provider_name=self.provider.name,
            seed=self.seed,
            items=all_items,
            responses=all_responses,
            verdicts=all_verdicts,
            score=score,
        )
