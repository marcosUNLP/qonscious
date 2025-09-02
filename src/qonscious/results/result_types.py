from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from typing import Any


class ExperimentResult(TypedDict):
    """
    Unified structure returned by any BackendAdapter.run() call.

    Attributes:
        counts: Dictionary mapping bitstring keys to integer counts.
        shots: The number of shots in the job that generated this result
        backend_properties: dictionary with various properties describing the backend
                            used to run the circuit.
        timestamps: Optional dictionary with ISO timestamps for
                    'created', 'running', 'finished'.
        raw_results: Backend-specific result object (e.g., SamplerResult or JobResult).
    """

    counts: dict[str, int]
    shots: int
    backend_properties: dict[str, str]
    timestamps: dict[str, str]
    raw_results: Any | None


class FigureOfMeritResult(TypedDict):
    """
    Unified structure returned by any FigureOfMerit evaluation.
    For now, speficis types of figures of merit will store their results in the
    properties dictionary.
    Refer to the documentation of each figure of merit for details.
    They can eventually subclass this class to better support type-checking and documentation.

    Attributes:
        timestamp: ISO timestamp
        figure_of_merit: a string identifiying the FOM this results relates to
                        (could be the FoM class name)
        properties: dictionary with various properties describing the result.
        experiment_result: The ExperimentResult used to compute the figure of merit (if any).
    """

    timestamp: str
    figure_of_merit: str
    properties: dict[str, Any]
    experiment_result: ExperimentResult | None


class QonsciousResult(TypedDict):
    """
    Unified structure returned by the QonsciousRunner run method.

    Attributes:
        condition: String describing the condition under which the run executed
        (for now only fail/pass).
        experiment_result: ExperimentResult that was obtained in this run.
        figures_of_merit_results: FigureOfMeritResults that were considered in this run.
    """

    condition: str
    experiment_result: ExperimentResult | None
    figures_of_merit_results: list[FigureOfMeritResult]
