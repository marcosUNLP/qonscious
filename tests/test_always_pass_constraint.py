from qonscious.constraints import AlwaysPassConstraint
from qonscious.core import AerSamplerAdapter
from qiskit import QuantumCircuit

def test_always_pass_constraint():
    constraint = AlwaysPassConstraint()
    backend = AerSamplerAdapter()

    qc = QuantumCircuit(1)
    qc.h(0)

    result = constraint.introspect(backend)
    assert constraint.evaluate(result) is True
