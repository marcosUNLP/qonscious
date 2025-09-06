from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from qiskit import QuantumCircuit

from qonscious.adapters.ionq_backend_adapter import IonQBackendAdapter

if TYPE_CHECKING:
    from qonscious.results.result_types import ExperimentResult


@pytest.mark.ionq_apikey_required
def test_ionq_backend_basic_run():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    api_key = os.getenv("IONQ_API_KEY")
    adapter = IonQBackendAdapter.aria_simulator(api_key)
    result: ExperimentResult = adapter.run(qc, shots=2048)

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
    assert sum(counts.values()) == 2048  # Total counts should equal shots

    # Validate backend name
    assert result["backend_properties"]["name"] == "ionq_simulator"

    # Validate timestamps
    timestamps = result["timestamps"]
    assert isinstance(timestamps, dict)
    assert all(k in timestamps for k in ("created", "running", "finished"))
    assert all(isinstance(timestamps[k], str) for k in timestamps)
