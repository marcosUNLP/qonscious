# Todos los imports con manejo de errores
_adapters = {}

try:
    from .aer_sampler_adapter import AerSamplerAdapter
    _adapters["AerSamplerAdapter"] = AerSamplerAdapter
except ImportError as e:
    AerSamplerAdapter = None
    print(f"⚠️  AerSamplerAdapter no disponible: {e}")

try:
    from .aer_simulator_adapter import AerSimulatorAdapter
    _adapters["AerSimulatorAdapter"] = AerSimulatorAdapter
except ImportError as e:
    AerSimulatorAdapter = None
    print(f"⚠️  AerSimulatorAdapter no disponible: {e}")

try:
    from .ibm_sampler_adapter import IBMSamplerAdapter
    _adapters["IBMSamplerAdapter"] = IBMSamplerAdapter
except ImportError as e:
    IBMSamplerAdapter = None
    print(f"⚠️  IBMSamplerAdapter no disponible: {e}")

try:
    from .ionq_backend_adapter import IonQBackendAdapter
    _adapters["IonQBackendAdapter"] = IonQBackendAdapter
except ImportError as e:
    IonQBackendAdapter = None
    print(f"⚠️  IonQBackendAdapter no disponible: {e}")

try:
    from .quafu_backend_adapter import QuafuBackendAdapter
    _adapters["QuafuBackendAdapter"] = QuafuBackendAdapter
except ImportError as e:
    QuafuBackendAdapter = None
    print(f"⚠️  QuafuBackendAdapter no disponible: {e}")

# BackendAdapter es esencial - si falla, hay un problema grave
try:
    from .backend_adapter import BackendAdapter
    _adapters["BackendAdapter"] = BackendAdapter
except ImportError as e:
    raise ImportError(f"❌ BackendAdapter esencial no disponible: {e}")

# Hacer disponibles todos en el namespace
globals().update(_adapters)

# Solo exportar los que se importaron correctamente
__all__ = list(_adapters.keys())

# Información de disponibilidad
available_adapters = {name: adapter is not None for name, adapter in _adapters.items()}
__all__.append("available_adapters")

print(f"✅ Adapters cargados: {len(_adapters)}/{len(__all__)-1}")
