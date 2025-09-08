# Running Qonscious in Google Colab

This tutorial guides you through setting up and running the `qonscious` project in Google Colab, a free cloud-based Jupyter notebook environment. The example demonstrates a quantum circuit using Qiskit to create a Bell state (Phi+), perform a CHSH test, and visualize results.

## Prerequisites
- A Google account to access [Google Colab](https://colab.research.google.com).
- Basic familiarity with Python, Git, and quantum computing concepts.
- Access to the `qonscious` repository: [https://github.com/lifia-unlp/qonscious](https://github.com/lifia-unlp/qonscious).

## Step-by-Step Instructions

### 1. Open Google Colab
- Navigate to [Google Colab](https://colab.research.google.com).
- Click **File > New Notebook** to create a new notebook.

### 2. Clone the Qonscious Repository
Clone the `qonscious` repository and navigate to its root directory:

```bash
!git clone https://github.com/lifia-unlp/qonscious.git
%cd qonscious
```

Run this in a Colab cell by clicking the play button or pressing `Shift + Enter`.

### 3. Install Dependencies
Install the required packages, including `qiskit` and the `qonscious` project in editable mode with its development, notebook, visualization, and documentation dependencies:

```bash
!pip install -U pip wheel
!pip install -e ".[dev,notebooks,viz,docs]"
```

The `-e` flag installs `qonscious` in editable mode, linking to the local repository. The `[dev,notebooks,viz,docs]` extras include:
- `dev`: Development tools (e.g., testing frameworks).
- `notebooks`: Jupyter notebook dependencies.
- `viz`: Visualization libraries (e.g., `matplotlib`, `seaborn`).
- `docs`: Tools for building documentation (e.g., `sphinx`).

### 4. Run the Qonscious Example
The following code creates a Phi+ Bell state, runs a CHSH test, and visualizes the results. Copy and paste this into a Colab cell:

```python
from qiskit import QuantumCircuit


# A helper function to create our phi_plus circuit.
def build_phi_plus_circuit() :
    phi_plus = QuantumCircuit(2)
    phi_plus.h(0)
    phi_plus.cx(0, 1)
    phi_plus.measure_all()
    return phi_plus
```
```python
from qonscious.adapters import BackendAdapter


# This is the callback function that will run if the CHSH checks passes.
# It prints the chsh score, and runs the phi_plus cirtuit.
def on_pass(backend_adapter : BackendAdapter, figureOfMeritResults):
    firstFoMResult = figureOfMeritResults[0]
    print("CHSH test passed!")
    print(f"Score: {firstFoMResult['properties']['score']:.3f}")
    print("Running our Phi+ circuit")
    run_result = backend_adapter.run(build_phi_plus_circuit(), shots=2048)
    print("Phi+ circuit finished running")
    return run_result

# This is the callback function that will run if the CHSH checks fails.
# Iit just prints a message and the CHSH score
def on_fail(backend_adapter : BackendAdapter, figureOfMeritResults):
    firstFoMResult = figureOfMeritResults[0]
    print("CHSH test failed!")
    print(f"Score: {firstFoMResult['properties']['score']:.3f}")
    return None
```

```python
from qonscious.checks import MeritComplianceCheck
from qonscious.foms import PackedCHSHTest


#This is a utility function to check that the score of the CHSH test
# (in the properties a FigureOfMeritResult) is over a given threshold
def chsh_score_over(threshold: float):
    return lambda r: r["properties"]["score"] > threshold

# This is our main (only) figure of merit compliance check.
# We pass this as an argument to the run_conditional function.
# Feel free to play with the threshold value.
# Simulators can get almost to the 2.82 bound; IBM's computers get in the range 2.5-2.7.
check_chsh_is_ok = MeritComplianceCheck(
    figure_of_merit=PackedCHSHTest(),
    decision_function=chsh_score_over(2.4),
)
```

```python
import os

from qonscious import run_conditionally
from qonscious.actions import QonsciousCallable
from qonscious.adapters import AerSamplerAdapter, IBMSamplerAdapter

# Uncomment this line to use the Aer simulator instead of a real
backend = AerSamplerAdapter()

# Uncomment these lines to use a real backend instead of the Aer simulator
# ibm_token = os.getenv("IBM_QUANTUM_TOKEN")
# backend = IBMSamplerAdapter.least_busy_backend(ibm_token)

print("Running Phi+ conditional on a CHSH score check ...\n")
qunscious_result = run_conditionally(
    backend_adapter=backend,
    checks= [check_chsh_is_ok],
    on_pass=QonsciousCallable(on_pass),
    on_fail=QonsciousCallable(on_fail)
)
```

```python
# Plot the observed results (only run this cell if the CHSH test passed!)
# F_Z is a simplified fidelity measure only considering the computational basis (it should be 1)

import matplotlib.pyplot as plt

# Get the counts of each possibly observed result 00, 01, 10, 11
counts = qunscious_result['experiment_result']['counts'] # type: ignore

# Choose a fixed label order for 2-qubit outcomes
labels = ['00', '01', '10', '11']
values = [counts.get(k, 0) for k in labels]

N = sum(values)
F_Z = (counts.get('00', 0) + counts.get('11', 0)) / N if N else float('nan')
title = f"Z-basis outcomes (F_Z = {F_Z:.3f})"

fig, ax = plt.subplots()
bars = ax.bar(labels, values)
ax.set_title(title)
ax.set_xlabel("Outcome")
ax.set_ylabel("Counts")
ax.set_ylim(bottom=0)
ax.grid(True, axis='y', linestyle=':', linewidth=0.5)

# Add labels on top of each bar
for bar, value in zip(bars, values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        str(value),
        ha='center', va='bottom'
    )
plt.show()
```

### 5. Using a Real IBM Quantum Backend (Optional)
To use a real IBM Quantum backend instead of the Aer simulator, set up your IBM Quantum token and modify the backend:

```python
import os
from qonscious.adapters import IBMSamplerAdapter

# Set your IBM Quantum token
ibm_token = "YOUR_IBM_QUANTUM_TOKEN"  # Replace with your token
os.environ["IBM_QUANTUM_TOKEN"] = ibm_token

# Use the least busy IBM backend
backend = IBMSamplerAdapter.least_busy_backend(ibm_token)
```

Obtain your token from [IBM Quantum](https://quantum-computing.ibm.com/). Note that real backends may have queue times and require a valid token.

### 6. View Outputs
- **Plots**: Visualizations (e.g., bar charts) will display in the notebook after running the code.

### Troubleshooting
- **Module Not Found**: If `qiskit` or other modules are missing, ensure all dependencies are installed. Re-run `!pip install qiskit` or `!pip install -e ".[dev,notebooks,viz,docs]"`. To verify `qiskit` installation, check:
  ```python
  import qiskit
  print(qiskit.__version__)
  ```
- **Editable Install Issues**: If the `-e` install fails, confirm that `pyproject.toml` exists in the `qonscious` directory. Install build tools if needed:
  ```bash
  !pip install build
  ```
- **File Not Found**: Verify that the repository was cloned successfully (`!ls qonscious` should list `pyproject.toml` and other files) and that you’re in the correct directory (`%cd qonscious`).
- **CHSH Test Fails**: Adjust the `chsh_score_over` threshold (e.g., lower from 2.4 to 2.0) if using a noisy backend.
- **Runtime Limits**: Colab sessions may disconnect after 12 hours. For long-running tasks, consider a local environment.
- Check the `qonscious` repository’s [issues](https://github.com/lifia-unlp/qonscious/issues) or `README.md` for specific guidance.

## Example Notebook
Here’s a complete Colab notebook structure:

```python
# Clone the repository
!git clone https://github.com/lifia-unlp/qonscious.git
%cd qonscious

# Install dependencies
!pip install -U pip wheel
!pip install -e ".[dev,notebooks,viz,docs]"

# Insert the Qonscious example code from Step 4 here
```

## Next Steps
- Explore other tutorials in the `qonscious` repository’s `docs/tutorials` folder.
- Contribute to `qonscious` by submitting pull requests (see `CONTRIBUTING.md`).
- Contact the LIFIA-UNLP team via [GitHub issues](https://github.com/lifia-unlp/qonscious/issues) for support.
