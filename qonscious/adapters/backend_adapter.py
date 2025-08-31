from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from qiskit import QuantumCircuit

    from qonscious.core.types import ExperimentResult


class BackendAdapter(Protocol):
    def run(self, circuit: QuantumCircuit, **kwargs) -> ExperimentResult: ...

    def t1s(self) -> dict[int, float]: ...
