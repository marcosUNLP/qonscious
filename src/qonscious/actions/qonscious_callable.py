from typing import Callable

from qonscious.actions.qonscious_action import QonsciousAction
from qonscious.adapters.backend_adapter import BackendAdapter
from qonscious.results.result_types import ExperimentResult, FigureOfMeritResult


class QonsciousCallable(QonsciousAction):
    """
    A callable wraped as QonsciousAction

    Attributes:
        callable ( Callable[[BackendAdapter, list[FigureOfMeritResult]], ExperimentResult | None]):
            the callable to execute
    """

    def __init__(
        self,
        callable: Callable[[BackendAdapter, list[FigureOfMeritResult]], ExperimentResult | None],
    ):
        self.callable = callable

    def run(
        self, backend_adapter: BackendAdapter, fom_results: list[FigureOfMeritResult], **kwargs
    ) -> ExperimentResult | None:
        return self.callable(backend_adapter, fom_results, **kwargs)
