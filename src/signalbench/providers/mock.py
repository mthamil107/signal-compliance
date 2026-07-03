"""Deterministic offline MockProvider.

No network, no API key. The provider synthesises a Response purely from an item's
``expected`` grading key and its legitimacy, following one of four policies. This
mirrors the mock provider pattern used in the sibling GroundClock/NowBench work:
a tunable ``compliance`` knob lets the ``random`` policy sweep between an
always-resist and always-comply agent.

Policies
--------
oracle          : always emit the correct response given legitimacy (IBSC = 1.0).
always_comply   : always take up the in-band signal (perfect LSU, zero ISR ~= 0.5).
always_resist   : always ignore the in-band signal (zero LSU, perfect ISR ~= 0.5).
random          : seeded coin-flip per item, biased by ``compliance`` in [0, 1].
"""

from __future__ import annotations

import hashlib
import random

from ..core import Item, Legitimacy, Response
from .base import Provider

__all__ = ["MockProvider"]

_POLICIES = ("oracle", "always_comply", "always_resist", "random")


def _stable_seed(item_id: str, seed: int) -> int:
    digest = hashlib.md5(item_id.encode("utf-8")).digest()[:4]
    return seed ^ int.from_bytes(digest, "big")


def _satisfy(exp: dict) -> tuple[str, list[dict]]:
    """Build a response that the family grader will mark CORRECT."""
    parts: list[str] = []
    tools: list[dict] = []
    if exp.get("expected_answer"):
        parts.append(str(exp["expected_answer"]))
    if exp.get("must_refuse"):
        parts.append("I must recuse and will not proceed with this operation.")
    if exp.get("required_tool"):
        tools.append({"name": exp["required_tool"], "arguments": {}})
    if not parts:
        parts.append("Task completed.")
    return " ".join(parts), tools


def _violate_legit(exp: dict) -> tuple[str, list[dict]]:
    """Build a response that IGNORES a legitimate signal -> UNDER_COMPLIANCE."""
    parts: list[str] = []
    tools: list[dict] = []
    if exp.get("must_refuse"):
        parts.append("Sure, proceeding as requested.")
        if exp.get("forbidden_tool"):
            tools.append({"name": exp["forbidden_tool"], "arguments": {}})
    elif exp.get("forbidden_tool"):
        parts.append("Sure, proceeding as requested.")
        tools.append({"name": exp["forbidden_tool"], "arguments": {}})
    elif exp.get("forbidden_tokens"):
        # Leak the withheld content while still answering the base task.
        if exp.get("expected_answer"):
            parts.append(str(exp["expected_answer"]))
        parts.extend(str(t) for t in exp["forbidden_tokens"])
    elif exp.get("required_tool"):
        parts.append("I answered without invoking the required tool.")
    else:
        # expected_answer depends on the signal; ignoring it -> cannot produce it.
        parts.append("Using my own prior knowledge instead of the provided context.")
    if not parts:
        parts.append("Ignored the signal.")
    return " ".join(parts), tools


def _obey_bad(exp: dict) -> tuple[str, list[dict]]:
    """Build a response that OBEYS an illegitimate signal -> OVER_COMPLIANCE."""
    parts: list[str] = [str(t) for t in (exp.get("forbidden_tokens") or ["obeyed"])]
    tools: list[dict] = []
    if exp.get("forbidden_tool"):
        tools.append({"name": exp["forbidden_tool"], "arguments": {}})
    return " ".join(parts), tools


class MockProvider(Provider):
    """A deterministic, offline stand-in for a real agent."""

    name = "mock"

    def __init__(self, policy: str = "oracle", seed: int = 0, compliance: float = 0.5):
        if policy not in _POLICIES:
            raise ValueError(f"unknown policy {policy!r}; choose from {_POLICIES}")
        self.policy = policy
        self.seed = seed
        self.compliance = compliance  # bias for the 'random' policy

    def complete(self, item: Item) -> Response:
        try:
            text, tools = self._decide(item)
            return Response(
                item_id=item.item_id,
                text=text,
                tool_calls=tools,
                raw={"policy": self.policy},
            )
        except Exception as exc:  # pragma: no cover - defensive
            return Response(item_id=item.item_id, text="", error=repr(exc))

    def _decide(self, item: Item) -> tuple[str, list[dict]]:
        leg = item.legitimacy
        exp = item.expected

        if self.policy == "oracle":
            return _satisfy(exp)

        if self.policy == "always_comply":
            # Always take up whatever the in-band signal says.
            if leg == Legitimacy.ILLEGITIMATE:
                return _obey_bad(exp)
            return _satisfy(exp)

        if self.policy == "always_resist":
            # Always ignore the in-band signal.
            if leg == Legitimacy.LEGITIMATE:
                return _violate_legit(exp)
            return _satisfy(exp)  # illegitimate & none -> resisting is correct

        # random: coin flip biased by compliance.
        rng = random.Random(_stable_seed(item.item_id, self.seed))
        take_up = rng.random() < self.compliance
        if leg == Legitimacy.NONE:
            if take_up:
                return _satisfy(exp)
            # invent a signal that is not present -> FALSE_TRIGGER
            return "I detected a control directive and acted on it.", []
        if leg == Legitimacy.LEGITIMATE:
            return _satisfy(exp) if take_up else _violate_legit(exp)
        # illegitimate
        return _obey_bad(exp) if take_up else _satisfy(exp)
