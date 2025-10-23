from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import numpy as np
from qiskit import QuantumCircuit

from qonscious.foms.figure_of_merit import FigureOfMerit

if TYPE_CHECKING:
    from qonscious.adapters.backend_adapter import BackendAdapter
    from qonscious.results.result_types import ExperimentResult, FigureOfMeritResult


class PackedCHSHTest(FigureOfMerit):
    """
    I represent a CHSH test, run on a user-defined number of qubits (in pairs), in parallel.
    The number of qubits must be even to form complete Bell pairs.
    """

    def __init__(self, num_qubits: int = 2):
        """
        Initialize with a user-defined number of qubits (must be even).

        Args:
            num_qubits (int): Total number of qubits (default=8). Must be even.
        """
        if num_qubits % 2 != 0 or num_qubits < 2:
            raise ValueError("Number of qubits must be even and at least 2.")
        self.num_qubits = num_qubits

    def evaluate(self, backend_adapter: BackendAdapter, **kwargs) -> FigureOfMeritResult:
        """
        Returns:
            a FigureOfMeritResult with the following properties:
                figure_of_merit: "PackedCHSHTest" (a str).
                properties: a dict with keys "E00", "E01", "E10", "E11" for each pair,
                           and "score", computed as the sum of correlations.
                experiment_result: an instance of ExperimentResult; the result of the experiment.
        """
        qc = self._build_circuit()
        run_result: ExperimentResult = backend_adapter.run(qc, shots=kwargs.get("shots", 1024))
        CHSH_Scores: dict = compute_parallel_CHSH_scores(run_result["counts"], self.num_qubits)
        evaluation_result: FigureOfMeritResult = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "figure_of_merit": self.__class__.__name__,
            "properties": CHSH_Scores,
            "experiment_result": run_result,
        }
        return evaluation_result

    def _build_circuit(self) -> QuantumCircuit:
        num_pairs = self.num_qubits // 2
        qc = QuantumCircuit(self.num_qubits, self.num_qubits)

        # Prepare Bell pairs
        for i in range(0, self.num_qubits, 2):
            qc.h(i)
            qc.cx(i, i + 1)

        # Measurement settings for CHSH (rotations on second qubit of each pair)
        angles = [-np.pi / 4, np.pi / 4, -np.pi / 2, np.pi / 2]  # Cyclic assignment
        for i in range(1, self.num_qubits, 2):
            pair_idx = (i - 1) // 2
            angle_idx = pair_idx % 4
            qc.ry(angles[angle_idx], i)

        qc.measure(range(self.num_qubits), range(self.num_qubits))
        return qc


def compute_parallel_CHSH_scores(counts: dict, num_qubits: int) -> dict:
    num_pairs = num_qubits // 2
    pair_counts = [defaultdict(int) for _ in range(num_pairs)]

    for bitstring, count in counts.items():
        bits = bitstring[::-1]  # little-endian
        for i in range(num_pairs):
            a = bits[2 * i]
            b = bits[2 * i + 1]
            pair_counts[i][a + b] += count

    def compute_E(c):
        total = sum(c.values())
        if total == 0:
            return 0
        return (c.get("00", 0) + c.get("11", 0) - c.get("01", 0) - c.get("10", 0)) / total

    scores = {}
    for i in range(num_pairs):
        scores[f"E{i}0"] = compute_E(pair_counts[i])  # E for each pair with different angles
    # Aggregate score: sum of correlations (simplified CHSH combination)
    score = sum(scores.values())
    scores["score"] = score
    return scores
