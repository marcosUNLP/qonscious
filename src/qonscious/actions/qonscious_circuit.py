from qiskit import QuantumCircuit

from qonscious.actions.qonscious_action import QonsciousAction
from qonscious.adapters.backend_adapter import BackendAdapter
from qonscious.results.result_types import ExperimentResult, FigureOfMeritResult


class QonsciousCircuit(QonsciousAction):
    """
    A Quantum circuit wrapped as as QonsciousAction

    Attributes:
        circuit (QuantumCircuit): the quantum circuit to run
    """

    def __init__(self, circuit: QuantumCircuit):
        self.circuit = circuit

    def run(
        self, backend_adapter: BackendAdapter, fom_results: list[FigureOfMeritResult], **kwargs
    ) -> ExperimentResult:
        return backend_adapter.run(self.circuit, **kwargs)
