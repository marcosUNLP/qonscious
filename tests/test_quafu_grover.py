import os
import sys

# Agregar el directorio src al path de Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from qonscious import run_conditionally
from qonscious.actions import QonsciousCallable
from qonscious.adapters import QuafuBackendAdapter
from qonscious.checks import MeritComplianceCheck
from qonscious.foms import GroverFigureOfMerit


def test_grover_quafu():
    """Prueba el test GRADE Grover con Quafu"""

    print("🧪 TEST GROVER GRADE CON QUAFU")
    print("=" * 50)

    try:
        # Crear adapter Quafu
        print("🔄 Creando adapter Quafu...")
        adapter = QuafuBackendAdapter()

        # Configurar test Grover
        grover_fom = GroverFigureOfMerit(
            num_targets=2,           # 2 estados target
            lambda_factor=0.1,       # factor lambda para desviación estándar
            mu_factor=0.5,           # factor mu para no-targets
            num_qubits=3,            # 3 qubits (espacio de búsqueda de 8 estados)
            targets_int=[2, 5]       # estados target específicos: |010⟩ y |101⟩
        )

        # Configurar check - considerar éxito si score > 0.1
        grover_check = MeritComplianceCheck(
            figure_of_merit=grover_fom,
            decision_function=lambda result: (
                result is not None and
                result["properties"]["score"] > 0.1
            )
        )

        # Acciones
        def grover_success(backend, fom_results, **kwargs):
            result = fom_results[0]["properties"]
            score = result["score"]
            P_T = result["P_T"]
            P_N = result["P_N"]
            sigma_T = result["sigma_T"]

            print(f"✅ GROVER EXITOSO - Score: {score:.3f}")
            print(f"   Probabilidad targets (P_T): {P_T:.3f}")
            print(f"   Probabilidad no-targets (P_N): {P_N:.3f}")
            print(f"   Desviación estándar targets (σ_T): {sigma_T:.3f}")
            print(f"   Iteraciones Grover: {result['grover_iterations']}")
            print(f"   Targets: {result['target_states']}")

            return {
                "resultado": "grover_exitoso",
                "score": score,
                "P_T": P_T,
                "P_N": P_N,
                "sigma_T": sigma_T
            }

        def grover_fail(backend, fom_results, **kwargs):
            result = fom_results[0]["properties"]
            score = result["score"]
            P_T = result["P_T"]

            print(f"❌ GROVER FALLÓ - Score: {score:.3f}")
            print(f"   Probabilidad targets: {P_T:.3f}")
            print(f"   Iteraciones Grover: {result['grover_iterations']}")

            return {
                "resultado": "grover_fallido",
                "score": score,
                "P_T": P_T
            }

        print("\n🎯 EJECUTANDO TEST GROVER...")
        print("   Configuración:")
        print(f"   - Qubits: {grover_fom.num_qubits}")
        print(f"   - Targets: {[2, 5]} → {['010', '101']}")
        print(f"   - Espacio búsqueda: 2^{grover_fom.num_qubits} = {2**grover_fom.num_qubits} estados")
        print(f"   - Iteraciones Grover: {grover_fom._optimal_rounds(8, 2)}")

        # Ejecutar test
        result = run_conditionally(
            backend_adapter=adapter,
            checks=[grover_check],
            on_pass=QonsciousCallable(grover_success),
            on_fail=QonsciousCallable(grover_fail),
        )

        # Mostrar resultados detallados
        print("\n" + "=" * 50)
        print("📊 RESULTADOS GROVER FINALES:")
        print(f"   Backend usado: {adapter.name}")
        print(f"   Condición: {result['condition']}")

        if result['figures_of_merit_results']:
            grover_result = result['figures_of_merit_results'][0]["properties"]
            print(f"   Score Grover: {grover_result['score']:.3f}")
            print(f"   P_T: {grover_result['P_T']:.3f}")
            print(f"   P_N: {grover_result['P_N']:.3f}")
            print(f"   σ_T: {grover_result['sigma_T']:.3f}")
            print(f"   Iteraciones: {grover_result['grover_iterations']}")
            print(f"   Targets: {grover_result['target_states']}")

        if result['experiment_result']:
            print(f"   Acción ejecutada: {result['experiment_result']}")

        return result

    except Exception as e:
        print(f"❌ Error en test Grover: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_grover_variations():
    """Prueba diferentes configuraciones de Grover"""

    print("\n🧪 VARIACIONES DE GROVER")
    print("=" * 50)

    variations = [
        {
            "name": "Grover 2 qubits - 1 target",
            "num_qubits": 2,
            "num_targets": 1,
            "targets_int": [2],  # |10⟩
            "shots": 1000
        },
        {
            "name": "Grover 3 qubits - 2 targets",
            "num_qubits": 3,
            "num_targets": 2,
            "targets_int": [3, 6],  # |011⟩, |110⟩
            "shots": 1000
        },
        {
            "name": "Grover 3 qubits - 1 target",
            "num_qubits": 3,
            "num_targets": 1,
            "targets_int": [5],  # |101⟩
            "shots": 1000
        }
    ]

    adapter = QuafuBackendAdapter()

    for config in variations:
        print(f"\n🔧 Probando: {config['name']}")
        print("-" * 40)

        try:
            grover_fom = GroverFigureOfMerit(
                num_targets=config["num_targets"],
                lambda_factor=0.1,
                mu_factor=0.5,
                num_qubits=config["num_qubits"],
                targets_int=config["targets_int"]
            )

            # Ejecutar directamente sin check condicional
            qc = grover_fom._build_grover_circuit(
                grover_fom.num_qubits,
                [format(t, f"0{grover_fom.num_qubits}b") for t in config["targets_int"]],
                grover_fom._optimal_rounds(2**grover_fom.num_qubits, config["num_targets"])
            )

            run_result = adapter.run(qc, shots=config["shots"])
            counts = run_result["counts"]

            # Calcular métricas manualmente
            metrics = grover_fom._compute_score(
                counts,
                [format(t, f"0{grover_fom.num_qubits}b") for t in config["targets_int"]],
                config["shots"],
                0.1, 0.5
            )

            print(f"   Score: {metrics['score']:.3f}")
            print(f"   P_T: {metrics['P_T']:.3f}")
            print(f"   P_N: {metrics['P_N']:.3f}")
            print(f"   Mejor resultado: {max(counts, key=counts.get) if counts else 'N/A'}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    # Ejecutar test principal
    main_result = test_grover_quafu()

    # Ejecutar variaciones (opcional)
    if main_result and main_result['condition'] == 'pass':
        print("\n" + "=" * 60)
        test_grover_variations()
