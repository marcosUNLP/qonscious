from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from qonscious.adapters.backend_adapter import BackendAdapter
    from qonscious.results.result_types import FigureOfMeritResult


class FigureOfMerit(Protocol):
    """
    I represent a Figure of Merit (FoM) of a quantum computing backend.
    """

    def evaluate(self, backend_adapter: BackendAdapter, **kwargs) -> FigureOfMeritResult:
        """
        Params:
            backend_adapter: an instance of ; they are all polimorphic
        Returns:
            FigureOfMeritResult: with properties set to a dictionary with values that
            are specific to each subclass. Read the comment of class FigureOfMeritResult
            to learn about the attributes that are common to all cases.
        """
        ...
