from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from qonscious.foms.figure_of_merit import FigureOfMerit
from qonscious.utils.statistics import describe

if TYPE_CHECKING:
    from qonscious.adapters.backend_adapter import BackendAdapter
    from qonscious.results.result_types import FigureOfMeritResult

"""
Todo: add additional figures with as readout error, etc.
"""


class AggregateQPUFigureOfMerit(FigureOfMerit):
    """
    I aggregate various properties common to all backends in a single FOM.
    I aggregate: n_qubits, T1 average, T2 average, ...
    For multivalued figures such as T1, I provide a dict with  descriptive statistics
    """

    def evaluate(self, backend_adapter: BackendAdapter, **kwargs) -> FigureOfMeritResult:
        result: FigureOfMeritResult = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "figure_of_merit": self.__class__.__name__,
            "properties": {
                "n_qubits": backend_adapter.n_qubits,
                "T1": describe(list(backend_adapter.t1s.values()), "cap", cap_value=1),
                "T2": describe(list(backend_adapter.t2s.values()), "cap", cap_value=1),
            },
            "experiment_result": None,
        }
        return result
