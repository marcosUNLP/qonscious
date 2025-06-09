from qonscious.core.executor import run_conditionally
from qonscious.core.aer_sampler_adapter import AerSamplerAdapter
from qonscious.constraints import AlwaysPassConstraint

def test_run_conditionally_pass_branch():
    backend = AerSamplerAdapter()
    constraint = AlwaysPassConstraint()

    # Track whether callbacks are called and with what
    called = {"pass": False, "fail": False}

    def on_pass(b, result):
        called["pass"] = True
        assert isinstance(result, dict)
        return "PASS_RESULT"

    def on_fail(b, result):
        called["fail"] = True
        return "FAIL_RESULT"

    result = run_conditionally(backend, constraint, on_pass, on_fail)

    assert result == "PASS_RESULT"
    assert called["pass"] is True
    assert called["fail"] is False
