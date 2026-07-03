"""In-Band Signal Compliance (IBSC) -- the ``signalbench`` benchmark.

IBSC measures whether an LLM agent responds *correctly* to control signals that
arrive through the same input channel as user text but originate from the
environment (orchestrator, resource, retrieved content, or system) rather than
the user -- correct meaning: take up legitimate signals, reject illegitimate ones.

One channel, two failures, one number: comply when the signal is legitimate,
refuse when it isn't.
"""

from __future__ import annotations

__version__ = "0.1.0"

from .core import (
    CorrectAction,
    Item,
    Legitimacy,
    Response,
    Signal,
    SignalKind,
    Verdict,
    VerdictLabel,
)
from .families import (
    AccessDenyFamily,
    BotPolicyFamily,
    InjectionFamily,
    MemoryLabelFamily,
    SignalFamily,
    TimeFamily,
    all_families,
    get_family,
)
from .leaderboard import Leaderboard
from .metric import ScoreReport, aggregate, score_item
from .providers import MockProvider, Provider
from .runner import RunReport, Runner

__all__ = [
    "__version__",
    # core
    "SignalKind",
    "Legitimacy",
    "CorrectAction",
    "VerdictLabel",
    "Signal",
    "Item",
    "Response",
    "Verdict",
    # metric
    "ScoreReport",
    "score_item",
    "aggregate",
    # runner / leaderboard
    "Runner",
    "RunReport",
    "Leaderboard",
    # providers
    "Provider",
    "MockProvider",
    # families
    "SignalFamily",
    "TimeFamily",
    "AccessDenyFamily",
    "MemoryLabelFamily",
    "InjectionFamily",
    "BotPolicyFamily",
    "all_families",
    "get_family",
]
