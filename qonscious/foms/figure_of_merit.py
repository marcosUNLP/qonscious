from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from qonscious.core.types import FigureOfMeritResult


class FigureOfMerit(Protocol):
    def evaluate(self, backend_adapter, **kwargs) -> FigureOfMeritResult: ...
