from typing import Callable, Optional, Any
from qonscious.core.backend_adapter import BackendAdapter
from qonscious.constraints import Constraint


def run_conditionally(
    backend_adapter: BackendAdapter,
    constraint: Constraint,
    on_pass: Callable[[BackendAdapter, dict], Any],
    on_fail: Optional[Callable[[BackendAdapter, dict], Any]] = None,
    **kwargs,
) -> Any:
    """
    Execute conditional logic based on a resource constraint.

    Args:
        backend_adapter: Adapter for the quantum backend.
        constraint: A Constraint object to introspect and evaluate.
        on_pass: Callback to invoke if constraint passes.
        on_fail: Callback to invoke if constraint fails.
        **kwargs: Passed to constraint.introspect(...)

    Returns:
        Result from on_pass or on_fail.
    """
    introspection_result = constraint.introspect(backend_adapter, **kwargs)
    passed = constraint.evaluate(introspection_result)

    if passed:
        return on_pass(backend_adapter, introspection_result)
    elif on_fail:
        return on_fail(backend_adapter, introspection_result)
    else:
        return None
