from __future__ import annotations

from typing import TYPE_CHECKING

from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from typing_extensions import Self

from .backend_adapter import BackendAdapter

if TYPE_CHECKING:
    from qiskit import QuantumCircuit

    from qonscious.core.types import ExperimentResult


class IBMSamplerAdapter(BackendAdapter):
    def __init__(self, backend):
        self.backend = backend

    @classmethod
    def least_busy_backend(cls, token) -> Self:
        """Simply provide your IBM Quantum token to get an adaptor on the least busy backend."""
        service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
        return cls(service.least_busy(operational=True, simulator=False))

    def extract_counts(self, result) -> dict:
        data = result[0].data
        field_names = [
            k
            for k in dir(data)
            if not k.startswith("_") and hasattr(getattr(data, k), "get_counts")
        ]
        if len(field_names) != 1:
            raise ValueError(
                f"Expected exactly one data field with get_counts(), got: {field_names}"
            )
        return getattr(data, field_names[0]).get_counts()

    def run(self, circuit: QuantumCircuit, **kwargs) -> ExperimentResult:
        kwargs.setdefault("shots", 1024)
        sampler = Sampler(mode=self.backend)
        transpiled_circuit = transpile(circuit, self.backend, optimization_level=3)
        job = sampler.run([transpiled_circuit], **kwargs)
        result = job.result()
        timestamps = job.metrics().get("timestamps", {})
        counts = self.extract_counts(result)
        return {
            "counts": counts,
            "shots": kwargs["shots"],
            "backend_properties": {"name": self.backend.name},
            "timestamps": timestamps,
            "raw_results": result,
        }
