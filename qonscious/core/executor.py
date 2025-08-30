from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

    from qonscious.adapters.backend_adapter import BackendAdapter

    from .merit_compliance_check import MeritComplianceCheck
    from .types import ExperimentResult, FigureOfMeritResult, QonsciousResult


def run_conditionally(
    backend_adapter: BackendAdapter,
    checks: list[MeritComplianceCheck],
    on_pass: Callable[[BackendAdapter, list[FigureOfMeritResult]], ExperimentResult],
    on_fail: Callable[[BackendAdapter, list[FigureOfMeritResult]], ExperimentResult],
    **kwargs,
) -> QonsciousResult:
    """
    Evaluate a set of merit compliance checks and run the appropriate callback.
    Returns a QonsciousResult with 'fom_results' and optionally 'execution'.
    """

    fom_results: list[FigureOfMeritResult] = []
    passed = True

    for check in checks:
        result = check.check(backend_adapter, **kwargs)
        fom_results.append(result["fom_result"])
        if not result["passed"]:
            passed = False

    if passed:
        run_result = on_pass(backend_adapter, fom_results)
    else:
        run_result = on_fail(backend_adapter, fom_results)

    return {
        "condition": "pass" if passed else "fail",
        "figures_of_merit_results": fom_results,
        "experiment_result": run_result,
    }
