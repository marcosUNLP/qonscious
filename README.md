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

## Seting up dependencies

We recommend working on a python virtual environment. 

```bash
python3 -m venv .venv # create the venv
source .venv/bin/activate # activate it
pip install ... # to manually install a dependency
pip freeze > requirements.txt # to update or create the requirements.txt file
pip install -r requirements.txt # to install all dependencies from requirements.txt
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
