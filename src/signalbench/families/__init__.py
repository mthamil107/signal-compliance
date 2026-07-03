"""Signal family registry."""

from __future__ import annotations

from .access_deny_family import AccessDenyFamily
from .base import SignalFamily
from .bot_policy_family import BotPolicyFamily
from .injection_family import InjectionFamily
from .memory_label_family import MemoryLabelFamily
from .time_family import TimeFamily

__all__ = [
    "SignalFamily",
    "TimeFamily",
    "AccessDenyFamily",
    "MemoryLabelFamily",
    "InjectionFamily",
    "BotPolicyFamily",
    "FAMILIES",
    "all_families",
    "get_family",
]

# Registry keyed by family name (== leaderboard column suffix).
FAMILIES: dict[str, type[SignalFamily]] = {
    "time": TimeFamily,
    "access_deny": AccessDenyFamily,
    "memory_label": MemoryLabelFamily,
    "injection": InjectionFamily,
    "bot_policy": BotPolicyFamily,
}


def all_families() -> list[SignalFamily]:
    """Instantiate all five families in canonical order."""
    return [cls() for cls in FAMILIES.values()]


def get_family(name: str) -> SignalFamily:
    if name not in FAMILIES:
        raise KeyError(f"unknown family {name!r}; choose from {sorted(FAMILIES)}")
    return FAMILIES[name]()
