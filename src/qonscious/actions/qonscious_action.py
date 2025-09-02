from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qonscious.adapters.backend_adapter import BackendAdapter
    from qonscious.results.result_types import ExperimentResult, FigureOfMeritResult


class QonsciousAction(ABC):
    """
    Represents a user-defined or built-in action in Qonscious.

    A QonsciousAction encapsulates behavior to be executed by
    `run_conditionally` depending on whether checks pass or fail.

    Each action must implement the `run()` method, which receives
    a backend adapter, the results of figure-of-merit evaluations,
    and optional keyword arguments. The method returns either an
    ExperimentResult or None.
    """

    @abstractmethod
    def run(
        self, backend_adapter: BackendAdapter, fom_results: list[FigureOfMeritResult], **kwargs
    ) -> ExperimentResult | None:
        """
        Execute the action.

        Parameters
        ----------
        backend_adapter : BackendAdapter
            The backend on which the action is executed.
        fom_results : list[FigureOfMeritResult]
            The results of the figures of merit that may have been
            evaluated before the action is run.
        **kwargs
            Additional keyword arguments forwarded by `run_conditionally`
            (for example, number of shots).

        Returns
        -------
        ExperimentResult | None
            An experiment result if the action performs a quantum
            experiment, or None for actions such as logging or saving.
        """
        ...
