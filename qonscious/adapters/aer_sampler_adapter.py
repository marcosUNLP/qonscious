from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import psutil
from qiskit_aer.primitives import Sampler

from .backend_adapter import BackendAdapter

if TYPE_CHECKING:
    from qiskit import QuantumCircuit

    from qonscious.core.types import ExperimentResult


class AerSamplerAdapter(BackendAdapter):
    def __init__(self, sampler: Sampler | None = None):
        self.sampler = sampler or Sampler()

    @property
    def n_qubits(self) -> int:
        "Estimates the maximum number of qubits this computer can simulate"
        "considering the available memory and some rules of thumb"
        return int(math.log2(psutil.virtual_memory().available / 16))

    @property
    def t1s(self) -> dict[int, float]:
        "In an aer simulator, there is no limit on the t1."
        "It could be different if we include a noise model"
        return {qubit: float("inf") for qubit in range(self.n_qubits)}

    @property
    def t2s(self) -> dict[int, float]:
        "In an aer simulator, there is no limit on the t2."
        "It could be different if we include a noise model"
        return {qubit: float("inf") for qubit in range(self.n_qubits)}

    def run(self, circuit: QuantumCircuit, **kwargs) -> ExperimentResult:
        shots = kwargs.get("shots", 1024)
        created = datetime.now(timezone.utc).isoformat()
        job = self.sampler.run(circuits=[circuit], shots=shots)
        running = datetime.now(timezone.utc).isoformat()
        quasi_dist = job.result().quasi_dists[0]
        finished = datetime.now(timezone.utc).isoformat()
        # Convert to counts with bitstring keys (e.g., '00', '11')
        counts = {
            format(k, f"0{circuit.num_qubits}b"): int(round(prob * shots))
            for k, prob in quasi_dist.items()
        }

        return {
            "counts": counts,
            "shots": shots,
            "backend_properties": {
                "name": self.sampler.options.get("backend_name", "aer_simulator")
            },
            "timestamps": {
                "created": created,
                "running": running,
                "finished": finished,
            },
            "raw_results": job.result(),
        }
