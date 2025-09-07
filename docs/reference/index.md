# API Reference

Qonscious combines backend adapters, figures of merits, merit compliance checks, and actions to abstract what it means to perform resource aware conditional quantum computation in the NISQ era.

## Adapters

A BackendAdapter is the abstraction layer in Qonscious that standardizes access to quantum backends, whether they are real devices, cloud simulators, or local emulators. It exposes a uniform interface for executing quantum circuits and retrieving results in a consistent format, including counts, backend characteristics, and execution metadata. This allows Qonscious to remain agnostic to the specifics of backend APIs (such as IBM Sampler or Aer), while still supporting resource introspection, circuit execution, measurement, and runtime resource checks. Developers are free to implement custom adapters to integrate other platforms.

You can create an adapter on Qiskit's SamplerV2 as follows:

```Python
from qonscious.adapters import AerSamplerAdapter
backend = AerSamplerAdapter()
```

You can create an adapter to work with one of IBM's fake (simulated computers) as follows:

```Python
from qiskit_ibm_runtime.fake_provider import FakeManilaV2
from qonscious.adapters import IBMSamplerAdapter
adapter = IBMSamplerAdapter(FakeManilaV2()) # edit as needed
```

You can create an adapter on IBM's least bussy (real) quantum computer as follows:

```Python
import os
from qonscious.adapters import IBMSamplerAdapter
ibm_token = os.getenv("IBM_QUANTUM_TOKEN") # edit as needed
adapter = IBMSamplerAdapter.least_busy_backend(ibm_token)
```

You can create an adapter that simulates one of IBM's real computers (using Aer's Simulator, and the real noise models)

```Python
import os
from qonscious.adapters import AerSimulatorAdapter
ibm_token = os.getenv("IBM_QUANTUM_TOKEN") # edit as needed
adapter = AerSimulatorAdapter.based_on(ibm_token, backend_name="ibm_brisbane") # you can choose a different one
```

You can even create an adapter on IonQ's QPU. This example shows how to work with
the simulator of Aria-1 (including its noise model).

```Python
import os
from qonscious.adapters import IonQBackendAdapter
api_key = os.getenv("IONQ_API_KEY")
adapter = IonQBackendAdapter.simulated_aria(api_key)
```

::: qonscious.adapters.backend_adapter
    options:
      members:
        - BackendAdapter

## Figures of merit

A Figure of Merit in Qonscious represents a measurable property of a quantum backend (device or simulator) that is relevant to the quality or feasibility of circuit execution. Examples include physical metrics such as average T₁ time, CHSH score, or backend connectivity, as well as derived quantities like estimated circuit error after transpilation. When a figure of merit is evaluated, it produces a structured object called a Figure of Merit Result, which contains the computed value (or outcome), relevant metadata (such as backend name, timestamps, or raw introspection data), and any additional fields needed to interpret the result. These results are in merit checks to determine whether the backend conditions meet the criteria required for executing a quantum task.

You can use Figures of Merit as stand-alone objects, to analyse a backend but you normally used them in merit checks of the run_conditional() function.

You can get an aggregate figure of merit (T1, T2, numer of qubits, etc) of IBM's least bussy computer as follows:

```Python
import os
from qonscious.adapters import IBMSamplerAdapter
from qonscious.foms.aggregate_qpu_fom import AggregateQPUFigureOfMerit

ibm_token = os.getenv("IBM_QUANTUM_TOKEN")
adapter = IBMSamplerAdapter.least_busy_backend(ibm_token)
agg_fom = AggregateQPUFigureOfMerit()
agg_fom.evaluate(adapter)
```

You can see what the CHSH (a figure of merit) looks like in IBM's FakeKawasaki() as follows. Pay attention to the properties attribute of the result object.

```Python
from qiskit_ibm_runtime.fake_provider import FakeKawasaki
from qonscious.adapters import IBMSamplerAdapter
from qonscious.foms import PackedCHSHTest

adapter = IBMSamplerAdapter(FakeKawasaki())
chsh_test = PackedCHSHTest()
chsh_test.evaluate(adapter)
```

::: qonscious.foms.aggregate_qpu_fom
::: qonscious.foms.packed_chsh

## Merit checks

You use figures of merit to evaluate whether a quantum computer meets the requirements of your experiment. A merit check consists of computing a figure of merit on a given backend and then deciding, based on the result, whether the device passes or fails your criteria.

The current mechanism for performing such a check is the MeritComplianceCheck, which takes two components:

* a FigureOfMerit that defines what to measure, and
* a decision function that receives the result of the measurement and returns True (pass) or False (fail).

For example, the following code checks whether IBM’s FakeKawasaki simulator is capable of producing a level of entanglement high enough to yield a CHSH score greater than 2.7 (run it a few times; 2.7 is in the limit of that fake computer)

```Python
from qiskit_ibm_runtime.fake_provider import FakeKawasaki

from qonscious.adapters import IBMSamplerAdapter
from qonscious.checks import MeritComplianceCheck
from qonscious.foms import PackedCHSHTest

adapter = IBMSamplerAdapter(FakeKawasaki())

# Build the compliance check using a PackedCHSHTest and the score-checking function (a lambda in this case)
chsh_compliance = MeritComplianceCheck(
    figure_of_merit=PackedCHSHTest(),
    decision_function=lambda chsh_result: chsh_result is not None and
        chsh_result["properties"]["score"] > 2.7,
)

chsh_compliance.check(adapter)
```

This approach lets you define flexible and reusable checks based on any figure of merit supported by Qonscious; not just CHSH, but also qubit count, coherence time, circuit error estimates, or even custom benchmarks.

::: qonscious.checks.merit_compliance_check

## Conditionally running circuits

You use Qoncsious to conditionaly (being aware of the resources on your computing platform) perform actions. This could be running a quantum circuit, reporting results, or running any arbitrary function. We call these actions, qonscious actions. A QonsciousAction is objects that implement the `run()` method, which receives a backend adapter, the results of figure-of-merit evaluations, and optional keyword arguments. The method returns either an ExperimentResult or None.

This example shows how to use a QonsciousCircuit object, to run a simple quantum circuit. It basically does nothing with the figures of merit it receives (they are important in other scenarios), therefore we send an empty list.

The result is a QonsciousResult object, that provides a uniform way to access the bistrings counts, execution stats, the raw results returned by the real backend. 

```Python
from qiskit import QuantumCircuit

from qonscious.actions import QonsciousCircuit
from qonscious.adapters import IBMSamplerAdapter

# A simple Bell state
phi_plus = QuantumCircuit(2)
phi_plus.h(0)
phi_plus.cx(0, 1)
phi_plus.measure_all()

q_action = QonsciousCircuit(phi_plus)
adapter = IBMSamplerAdapter(FakeKawasaki())
q_result = q_action.run(adapter,[],shots=2048)
```

This example shows how to use a QonsciousCallable to wrap a python function that logs the score of the CHSH test (a merit test).

```Python
from qiskit_ibm_runtime.fake_provider import FakeKawasaki

from qonscious.actions import QonsciousCallable
from qonscious.adapters import IBMSamplerAdapter
from qonscious.checks import MeritComplianceCheck
from qonscious.foms import PackedCHSHTest

adapter = IBMSamplerAdapter(FakeKawasaki())

chsh_compliance = MeritComplianceCheck(
    figure_of_merit=PackedCHSHTest(),
    decision_function=lambda chsh_result: chsh_result is not None and
        chsh_result["properties"]["score"] > 2.7,
)

chsg_result = chsh_compliance.check(adapter)["fom_result"]

def log_chsh_score(backend_adapter, figureOfMeritResults):
    firstFoMResult = figureOfMeritResults[0]
    print(f"CHSH Score: {firstFoMResult['properties']['score']:.3f}")
    return None

q_callable = QonsciousCallable(log_chsh_score)
q_callable.run(adapter,[chsg_result])
```

That last example looks a bit cumbersome. Luckily, we use actions via the run_conditionally function. 

So, if we put all of that together, we get:

```Python
from qiskit_ibm_runtime.fake_provider import FakeKawasaki

from qonscious import run_conditionally
from qonscious.actions import QonsciousCallable
from qonscious.adapters import IBMSamplerAdapter
from qonscious.checks import MeritComplianceCheck
from qonscious.foms import PackedCHSHTest

# Prepare our backend adapter
adapter = IBMSamplerAdapter(FakeKawasaki())

# Prepare our check - CHSH score over 2.7
chsh_compliance = MeritComplianceCheck(
    figure_of_merit=PackedCHSHTest(),
    decision_function=lambda chsh_result: chsh_result is not None and
        chsh_result["properties"]["score"] > 2.7,
)

# Prepare our action for the case CHSH is over 2.7 (A Bell pair)
phi_plus = QuantumCircuit(2)
phi_plus.h(0)
phi_plus.cx(0, 1)
phi_plus.measure_all()
pass_action = QonsciousCircuit(phi_plus)

# Prepare our action for the case CHSH in under 2.7 (report the score)
def log_chsh_score(backend_adapter, figureOfMeritResults):
    firstFoMResult = figureOfMeritResults[0]
    print(f"CHSH score was too low: {firstFoMResult['properties']['score']:.3f}")
    return None
fail_action = QonsciousCallable(log_chsh_score)

# Run either one of the actions conditionally on the CHSH figure of merit of our backend
q_result = run_conditionally(adapter, [chsh_compliance], pass_action, fail_action)

print(q_result)
```

::: qonscious.actions.qonscious_circuit
::: qonscious.actions.qonscious_callable
::: qonscious.run_conditionally
