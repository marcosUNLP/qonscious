from qiskit import QuantumCircuit
from qonscious.core import AerSamplerAdapter

def test_aer_sampler_basic_run():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    adapter = AerSamplerAdapter()
    result = adapter.run(qc, shots=1024)

    # Check result is a dict with expected keys
    assert isinstance(result, dict)
    assert set(result.keys()) >= {"counts", "backend", "timestamps", "raw"}

    # Validate counts format
    counts = result["counts"]
    assert isinstance(counts, dict)
    assert all(isinstance(k, str) and len(k) == 2 for k in counts.keys())
    assert all(isinstance(v, int) and v >= 0 for v in counts.values())
    assert sum(counts.values()) == 1024

    # Validate backend name
    assert result["backend"] == "aer_simulator"

    # Validate timestamps
    timestamps = result["timestamps"]
    assert isinstance(timestamps, dict)
    assert all(k in timestamps for k in ("created", "running", "finished"))
    assert all(isinstance(timestamps[k], str) for k in timestamps)
