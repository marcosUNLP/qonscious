from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from qiskit import QuantumCircuit

    from qonscious.core.types import ExperimentResult


class BackendAdapter(Protocol):
    def run(self, circuit: QuantumCircuit, **kwargs) -> ExperimentResult: ...

    def n_qubits(self) -> int: ...

    def t1s(self) -> dict[int, float]: ...

    def t2s(self) -> dict[int, float]: ...
