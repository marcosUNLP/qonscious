from qonscious.constraints.packed_chsh import PackedCHSHTest
from qonscious.policies import MinimumAcceptableValue
from qonscious.core.aer_sampler_adapter import AerSamplerAdapter
from qonscious.core.types import BackendRunResult


def test_packed_chsh_constraint_passes():
    # Create backend and constraint
    backend = AerSamplerAdapter()
    policy = MinimumAcceptableValue(1.5)  # loose threshold to ensure pass
    constraint = PackedCHSHTest(policy)

    # Run introspection
    result = constraint.introspect(backend, shots=2048)

    # Check expected keys
    assert "CHSH_score" in result
    assert all(k in result for k in ("E00", "E01", "E10", "E11"))

    # Evaluate the result
    passed = constraint.evaluate(result)

    # In ideal case, CHSH score should be > 2
    assert passed is True
    assert result["CHSH_score"] > 1.5
