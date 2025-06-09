from abc import ABC, abstractmethod
from qiskit import QuantumCircuit
from typing import Any
from .types import BackendRunResult

class BackendAdapter(ABC):

    @abstractmethod
    def run(self, circuit: QuantumCircuit, **kwargs) -> BackendRunResult:
        pass
