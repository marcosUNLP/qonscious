import numpy as np
from collections import defaultdict
from qiskit import QuantumCircuit
from qonscious.constraints import Constraint
from qonscious.policies import ThresholdPolicy  
from qonscious.core import BackendAdapter
from qonscious.core import BackendRunResult
from qonscious.core import PackedCHSHResult

class PackedCHSHTest(Constraint):
    def __init__(self, policy: ThresholdPolicy):
        self.policy = policy
    
    def introspect(self, backend_adapter: BackendAdapter, **kwargs) -> PackedCHSHResult:
        qc = self._build_circuit()
        run_result: BackendRunResult = backend_adapter.run(qc, shots=kwargs.get("shots", 1024))   
        chsh_data = compute_parallel_CHSH_scores(run_result["counts"])
        return {
            **chsh_data,
            "backend": run_result["backend"],
            "shots": run_result["shots"],
            "timestamps": run_result["timestamps"],
            "raw": run_result["raw"],
        }  

    def evaluate(self, introspection_result: dict) -> bool:
        return self.policy.evaluate(introspection_result["CHSH_score"])

    def _build_circuit(self) -> QuantumCircuit:
        qc = QuantumCircuit(8, 8)

        for i in range(0, 8, 2):
            qc.h(i)
            qc.cx(i, i+1)

        # Measurement settings
        qc.ry(-np.pi/4, 1)
        qc.ry(np.pi/4, 3)
        qc.ry(-np.pi/2, 4)
        qc.ry(-np.pi/4, 5)
        qc.ry(-np.pi/2, 6)
        qc.ry(np.pi/4, 7)

        qc.measure(range(8), range(8))
        return qc


def compute_parallel_CHSH_scores(counts: dict) -> dict:
    pair_counts = [defaultdict(int) for _ in range(4)]

    for bitstring, count in counts.items():
        bits = bitstring[::-1]  # little-endian
        for i in range(4):
            a = bits[2*i]
            b = bits[2*i + 1]
            pair_counts[i][a + b] += count

    def compute_E(c):
        total = sum(c.values())
        if total == 0:
            return 0
        return sum((1 if k in ('00', '11') else -1) * n / total for k, n in c.items())

    E = [compute_E(c) for c in pair_counts]
    S = E[0] + E[1] + E[2] - E[3]

    return {
        'E00': E[0],
        'E01': E[1],
        'E10': E[2],
        'E11': E[3],
        'CHSH_score': S
    }

    
