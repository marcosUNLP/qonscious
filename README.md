Meet **Qonscious**, a framework for resource-aware quantum computing in the NISQ era.

# Qonscious

**Qonscious** is a runtime framework designed to support conditional execution of quantum circuits based on resource introspection. It helps you build quantum applications that are aware of backend conditions — such as entanglement, coherence, or fidelity — before execution.

## Why Qonscious?

In the NISQ era, quantum hardware is noisy, resource-limited, and variable over time. Static resource assumptions lead to unreliable results. **Qonscious** makes quantum programs introspective and adaptive.

## Key Features

- Constraint-based introspection (e.g., CHSH score > 1.9)
- Flexible threshold policies (fixed, ranges, percentiles)
- Inversion of control: pass a callback, not a circuit
- Composable constraints (AND, OR, NOT)
- Built-in logging, extensibility, and fallback logic

## Setting up dependencies

We recommend working on a Python virtual environment.  This snippet of code provides examples of most of the things you'll need to do. 

This project is organized with a pyproject.toml file, so there is no need for a requirements.txt file anymore.

Python version is set in .python-version

```bash
python -m venv .venv 
source .venv/bin/activate
pip install -U pip wheel
pip install -e ".[dev,notebooks,viz]" # you can leave notebooks and viz out of you are only working on the framework.
```

## Example

```python
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from qonscious.constraints import PackedCHSHTest
from qonscious.policies import MinimumAcceptableValue
from qonscious.core import run_conditionally, IBMSamplerAdapter


# Define a sample main circuit
def build_my_main_circuit():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    return qc


# Create constraint
constraint = PackedCHSHTest(policy=MinimumAcceptableValue(1.9))

# Set up IBM backend adapter
service = QiskitRuntimeService()
backend = ...
adapter = IBMSamplerAdapter(backend)

# Callback on pass
def on_pass(backend_adapter, introspection):
    print("CHSH passed with score:", introspection["CHSH_score"])
    qc = build_my_main_circuit()
    return backend_adapter.run(qc, shots=1024)["counts"]

# Callback on fail
def on_fail(backend_adapter, introspection):
    print("CHSH failed with score:", introspection["CHSH_score"])
    return {"status": "skipped"}

# Conditional execution
result = run_conditionally(
    backend_adapter=adapter,
    constraint=constraint,
    on_pass=on_pass,
    on_fail=on_fail,
    shots=2048
)

```

# Development notes

## ruff

pyproject.toml includes default configurations for ruff (linting, etc.). Ruff is part of the [dev] dependencies.

To use ruff from the command (and let ruff format, and tiddy up code) line do as follows:

```python
ruff check . --fix
ruff format .
```

## pyright

This projects uses pyright as a typechecker (In VSCode it will work via PyLance).

Settings are defined in pyrightconfig.json

