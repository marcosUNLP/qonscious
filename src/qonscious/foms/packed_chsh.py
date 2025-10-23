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
    I represent a CHSH test, run on 8 qubits (the four Bell pairs), in parallel.
    """

    def evaluate(self, backend_adapter: BackendAdapter, **kwargs) -> FigureOfMeritResult:
        """
        Returns:
            a FigureOfMeritResult with the following properties:
                figure_of_merit: "PackedCHSHTest" (a str).
                properties: a dict with keys "E00", "E01", "E10", "E11", representing the individual
                counts of each observed pait, and "score", computed as E00 + E01 + E10 - E11.
                experiment_result: an instance of ExperimentResult; the result of the experiment.
        """
        qc = self._build_circuit()
        run_result: ExperimentResult = backend_adapter.run(qc, shots=kwargs.get("shots", 1024))
        CHSH_Scores: dict = compute_parallel_CHSH_scores(run_result["counts"])
        evaluation_result: FigureOfMeritResult = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "figure_of_merit": self.__class__.__name__,
            "properties": CHSH_Scores,
            "experiment_result": run_result,
        }
        return evaluation_result

    def _build_circuit(self) -> QuantumCircuit:
        qc = QuantumCircuit(8, 8)

        for i in range(0, 8, 2):
            qc.h(i)
            qc.cx(i, i + 1)

        # Measurement settings
        qc.ry(-np.pi / 4, 1)
        qc.ry(np.pi / 4, 3)
        qc.ry(-np.pi / 2, 4)
        qc.ry(-np.pi / 4, 5)
        qc.ry(-np.pi / 2, 6)
        qc.ry(np.pi / 4, 7)

        qc.measure(range(8), range(8))
        return qc


def compute_parallel_CHSH_scores(counts: dict) -> dict:
    pair_counts = [defaultdict(int) for _ in range(4)]

    for bitstring, count in counts.items():
        bits = bitstring[::-1]  # little-endian
        for i in range(4):
            a = bits[2 * i]
            b = bits[2 * i + 1]
            pair_counts[i][a + b] += count

    def compute_E(c):
        total = sum(c.values())
        if total == 0:
            return 0
        return sum((1 if k in ("00", "11") else -1) * n / total for k, n in c.items())

    E = [compute_E(c) for c in pair_counts]
    S = E[0] + E[1] + E[2] - E[3]

    return {
        "E00": E[0],
        "E01": E[1],
        "E10": E[2],
        "E11": E[3],
        "score": S,
    }
