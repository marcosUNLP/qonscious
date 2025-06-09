
from qiskit_aer.primitives import Sampler
from qiskit import QuantumCircuit
from .backend_adapter import BackendAdapter
from .types import BackendRunResult
from datetime import datetime, timezone


class AerSamplerAdapter(BackendAdapter):

    def __init__(self, sampler: Sampler = None):
        self.sampler = sampler or Sampler()

    def run(self, circuit: QuantumCircuit, **kwargs)  -> BackendRunResult:
        shots = kwargs.get("shots", 1024)
        created = datetime.now(timezone.utc).isoformat()
        job = self.sampler.run(circuits=[circuit], shots=shots)
        running = datetime.now(timezone.utc).isoformat()
        quasi_dist = job.result().quasi_dists[0]
        finished = datetime.now(timezone.utc).isoformat()
        # Convert to counts with bitstring keys (e.g., '00', '11')
        counts = {
            format(k, f'0{circuit.num_qubits}b'): int(round(prob * shots))
            for k, prob in quasi_dist.items()
        }

        return {
            "counts": counts,
            "shots": shots,
            "backend": self.sampler.options.get("backend_name", "aer_simulator"),
             "timestamps": {
                "created": created,
                "running": running,
                "finished": finished,
            },
            "raw": job.result()
        }

