from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from dotenv import load_dotenv
from qiskit import QuantumCircuit

from qonscious.adapters.ibm_sampler_adapter import IBMSamplerAdapter

if TYPE_CHECKING:
    from qonscious.results.result_types import ExperimentResult


@pytest.mark.ibm_token_required
def test_ibm_sampler_adapter_basic_run():
    # Setup IBM Runtime service and adapter
    load_dotenv()
    ibm_token = os.getenv("IBM_QUANTUM_TOKEN")
    if not ibm_token:
        pytest.skip("IBM token not set")
    adapter = IBMSamplerAdapter.least_busy_backend(ibm_token)

    # Create test circuit
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    # Run
    result: ExperimentResult = adapter.run(qc, shots=512)

    # Validate structure // should not be necessary now that I use typing
    assert set(result.keys()) >= {
        "counts",
        "backend_properties",
        "shots",
        "timestamps",
        "raw_results",
    }

    counts = result["counts"]
    assert isinstance(counts, dict)
    assert all(isinstance(k, str) and len(k) == 2 for k in counts)
    assert all(isinstance(v, int) for v in counts.values())
    assert sum(counts.values()) == 512

    assert isinstance(result["backend_properties"]["name"], str)
    assert result["shots"] == 512

    timestamps = result["timestamps"]
    assert isinstance(timestamps, dict)
    assert all(k in timestamps for k in ("created", "running", "finished"))
    assert all(isinstance(timestamps[k], str) for k in timestamps)
