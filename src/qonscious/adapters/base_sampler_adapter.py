from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from qiskit.primitives.containers import BitArray
from qiskit_aer.primitives import SamplerV2 as Sampler

from .backend_adapter import BackendAdapter

if TYPE_CHECKING:
    from qiskit import QuantumCircuit

    from qonscious.results.result_types import ExperimentResult


class BaseSamplerAdapter(BackendAdapter):
    def __init__(self, sampler: Sampler | None = None):
        self.sampler = sampler or Sampler()

    def transpile(self, circuit: QuantumCircuit) -> QuantumCircuit:
        return circuit

    def run(self, circuit: QuantumCircuit, **kwargs) -> ExperimentResult:
        shots = kwargs.get("shots", 1024)
        created = datetime.now(timezone.utc).isoformat()
        transpiled_circuit = self.transpile(circuit)
        job = self.sampler.run(pubs=[transpiled_circuit], shots=shots)
        running = datetime.now(timezone.utc).isoformat()
        result = job.result()[0]
        finished = datetime.now(timezone.utc).isoformat()

        raw = result.join_data()
        arr = raw.astype("uint8", copy=False) if not isinstance(raw, BitArray) else raw.array
        counts = BitArray(arr, circuit.num_clbits).get_counts()

        return {
            "counts": counts,
            "shots": shots,
            "backend_properties": {"name": "qiskit_aer.primitives.SamplerV2"},
            "timestamps": {
                "created": created,
                "running": running,
                "finished": finished,
            },
            "raw_results": job.result(),
        }
