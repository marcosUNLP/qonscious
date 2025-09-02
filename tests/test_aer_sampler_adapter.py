from __future__ import annotations

from typing import TYPE_CHECKING

from qiskit import QuantumCircuit

from qonscious.adapters.aer_sampler_adapter import AerSamplerAdapter

if TYPE_CHECKING:
    from qonscious.results.result_types import ExperimentResult


def test_aer_sampler_basic_run():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    adapter = AerSamplerAdapter()
    result: ExperimentResult = adapter.run(qc, shots=1024)

    # Check result is a dict with expected keys
    assert isinstance(result, dict)
    assert set(result.keys()) >= {
        "counts",
        "shots",
        "timestamps",
        "raw_results",
        "backend_properties",
    }

    # Validate counts format
    counts = result["counts"]
    assert isinstance(counts, dict)
    assert all(isinstance(k, str) and len(k) == 2 for k in counts)
    assert all(isinstance(v, int) and v >= 0 for v in counts.values())
    assert sum(counts.values()) == 1024

    # Validate backend name
    assert result["backend_properties"]["name"] == "qiskit_aer.primitives.SamplerV2"

    # Validate timestamps
    timestamps = result["timestamps"]
    assert isinstance(timestamps, dict)
    assert all(k in timestamps for k in ("created", "running", "finished"))
    assert all(isinstance(timestamps[k], str) for k in timestamps)


def test_t1s():
    adapter = AerSamplerAdapter()
    t1s = adapter.t1s
    assert all(k in t1s for k in range(1, adapter.n_qubits))
    assert all(t1s[k] == float("inf") for k in range(1, adapter.n_qubits))
