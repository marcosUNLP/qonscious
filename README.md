[![CI](https://github.com/lifia-unlp/qonscious/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/lifia-unlp/qonscious/actions/workflows/ci.yml)

**Qonscious** is a runtime framework designed to support conditional execution of quantum circuits based on resource introspection. It helps you build quantum applications that are aware of backend conditions — such as entanglement, coherence, or fidelity — before execution.

## Why Qonscious?

In the NISQ era, quantum hardware is noisy, resource-limited, and variable over time. Static resource assumptions lead to unreliable results. **Qonscious** makes quantum programs introspective and adaptive.

For a deeper discusion on the motivation behind Qonscious, read [our article](https://arxiv.org/html/2508.19276v1)

## Key Features

- Figures of Merit evaluation (e.g., get CHSH score)
- Conditional execution on compliance with figures of merit checks
- Inversion of control: pass a callback, not a circuit
- Built-in logging, extensibility, and fallback logic

## Use cases

These are some scenarios where you may use Qonscious:

- Run a circuit conditional on your target computer (or simulator) checking some figures of merit (e.g., number of qubits, CHSH score, etc.)
- Benchmark a computer (or simulator) in terms of a collection of figures of merit.
- Explore correlations between experiment results and figures of merit of a gicen computer (or simulator)
- ...

## Setting up dependencies

This project is organized with a pyproject.toml file, so there is no longer a need for a requirements.txt file.

Python version is set in .python-version

We recommend working in a Python virtual environment. The following snippet of code provides examples of most of the tasks you'll need to complete. 

```bash
python -m venv .venv 
source .venv/bin/activate
pip install -U pip wheel
pip install -e ".[dev,notebooks,viz,docs]" # you can leave notebooks and viz out of you are only working on the framework.
```

The **-e flag** in pip install tells pip to install Qonscious as a dependency so you can import from any Jupyter notebook working on the same venv while lettig you edit the framework.

## Documentation

Up to date documentation is available on [github pages](https://lifia-unlp.github.io/qonscious/)

## Examples

The notebooks folder contains several examples of using Qonscious in different use cases. 

We suggest you start with **chsh_test_demo.ipynb**

# Development notes

## VisualStudio Code

There is a _vscode_example_settings.json file that you can rename to .vscode/settings.json . It provides most default settings that help VSC find tests, work with notebooks, etc. 

## ruff

pyproject.toml includes default configurations for ruff (linting, etc.). Ruff is part of the [dev] dependencies.

To use ruff from the command line (and let ruff format, and tidy up code),  do as follows:

```python
ruff check . --fix
ruff format .
```

## pyright

This project uses pyright as a typechecker (In VSCode it will work via PyLance).

Settings are defined in pyrightconfig.json


