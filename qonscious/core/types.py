from typing import TypedDict, Optional, Any, Dict


class BackendRunResult(TypedDict):
    """
    Unified structure returned by any BackendAdapter.run() call.

    Attributes:
        counts: Dictionary mapping bitstring keys to integer counts.
        backend: Name of the backend used to run the circuit.
        shots: The number of shots in the job that generated this result
        timestamps: Optional dictionary with ISO timestamps for
                    'created', 'running', 'finished'.
        raw: Backend-specific result object (e.g., SamplerResult or JobResult).
    """
    counts: Dict[str, int]
    backend: str
    shots: int
    timestamps: Optional[Dict[str, str]]
    raw: Any

class PackedCHSHResult(BackendRunResult):
    CHSH_score: float
    E00: float
    E01: float
    E10: float
    E11: float