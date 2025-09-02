from __future__ import annotations

from typing import TYPE_CHECKING

from qonscious.adapters.aer_sampler_adapter import AerSamplerAdapter
from qonscious.foms.packed_chsh import PackedCHSHTest

if TYPE_CHECKING:
    from qonscious.results.result_types import FigureOfMeritResult


def test_packed_chsh_constraint_passes():
    # Create backend and constraint
    backend = AerSamplerAdapter()
    fom = PackedCHSHTest()

    # Run introspection
    result: FigureOfMeritResult = fom.evaluate(backend, shots=2048)

    # Checks that the FoM name is correctly set
    assert result["figure_of_merit"] == fom.__class__.__name__

    # Check expected keys
    props = result.get("properties")
    assert props is not None and isinstance(props, dict)  # narrows type for Pyright
    assert all(k in props for k in ("E00", "E01", "E10", "E11", "score"))

    # Evaluate the result
    assert result["properties"]["score"] > 2
