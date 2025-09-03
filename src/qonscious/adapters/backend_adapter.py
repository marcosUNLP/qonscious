from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from qiskit import QuantumCircuit

    from qonscious.results.result_types import ExperimentResult


class BackendAdapter(Protocol):
    def run(self, circuit: QuantumCircuit, **kwargs) -> ExperimentResult: ...

    @property
    def n_qubits(self) -> int:
        """
        Returns:
            int: The number of qubits of the backend.
        """
        ...

    @property
    def t1s(self) -> dict[int, float]:
        """
        Returns:
            dict[int, float]: The T1 (relaxation time) for each qubit.
        """
        ...

    @property
    def t2s(self) -> dict[int, float]:
        """
        Returns:
            dict[int, float]: The T2 (dephasing time) for each qubit.
        """
        ...
