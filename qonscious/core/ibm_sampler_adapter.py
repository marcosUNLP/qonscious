from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit import QuantumCircuit, transpile
from .backend_adapter import BackendAdapter
from .types import BackendRunResult

class IBMSamplerAdapter(BackendAdapter):

    def __init__(self, backend):
        self.backend = backend

    
    def extract_counts(this, result) -> dict:
        data = result[0].data
        field_names = [k for k in dir(data) if not k.startswith("_") and hasattr(getattr(data, k), "get_counts")]
        if len(field_names) != 1:
            raise ValueError(f"Expected exactly one data field with get_counts(), got: {field_names}")
        return getattr(data, field_names[0]).get_counts()

    def run(self, circuit: QuantumCircuit, **kwargs) -> BackendRunResult:
        kwargs.setdefault("shots", 1024)
        sampler = Sampler(mode=self.backend)
        transpiled_circuit = transpile(circuit, self.backend, optimization_level=3)  
        job = sampler.run([transpiled_circuit], **kwargs)
        result = job.result()

        timestamps = None
        try:
            timestamps = job.metrics().get("timestamps", None)
        except Exception:
            pass  # Not all jobs have metrics (esp. on simulators)

        counts = self.extract_counts(result)

        return {
            "counts": counts,
            "backend": self.backend.name,
            "shots": kwargs.get("shots"),
            "timestamps": timestamps,
            "raw": result
        }
    


