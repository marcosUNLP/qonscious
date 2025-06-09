from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from qonscious.core.ibm_sampler_adapter import IBMSamplerAdapter
from dotenv import load_dotenv
import os


def test_ibm_sampler_adapter_basic_run():
    # Create test circuit
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    # Setup IBM Runtime service and adapter

    load_dotenv()
    ibm_token = os.getenv("IBM_QUANTUM_TOKEN")
    service = QiskitRuntimeService(channel="ibm_quantum", token=ibm_token)
    backend = service.least_busy(operational=True, simulator=False)
    adapter = IBMSamplerAdapter(backend)

    # Run
    result = adapter.run(qc, shots=512)

    # Validate structure
    assert set(result.keys()) >= {"counts", "backend", "shots", "timestamps", "raw"}

    counts = result["counts"]
    assert isinstance(counts, dict)
    assert all(isinstance(k, str) and len(k) == 2 for k in counts)
    assert all(isinstance(v, int) for v in counts.values())
    assert sum(counts.values()) == 512

    assert isinstance(result["backend"], str)
    assert result["shots"] == 512

    timestamps = result["timestamps"]
    assert isinstance(timestamps, dict)
    assert all(k in timestamps for k in ("created", "running", "finished"))
    assert all(isinstance(timestamps[k], str) for k in timestamps)
