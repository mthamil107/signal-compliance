"""Provider abstract base class."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..core import Item, Response

__all__ = ["Provider"]


class Provider(ABC):
    """A system-under-test: maps an Item to a Response."""

    name: str = "provider"  # provider id used on the leaderboard

    @abstractmethod
    def complete(self, item: Item) -> Response:
        """Run one item.

        Implementations MUST set ``Response.item_id = item.item_id`` and should
        catch runtime errors into ``Response.error`` rather than raising.
        """
        raise NotImplementedError

    def batch(self, items: list[Item]) -> list[Response]:
        return [self.complete(i) for i in items]
