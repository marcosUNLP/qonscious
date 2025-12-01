# src/qonscious/adapters/pasqal_backend_adapter.py
from .backend_adapter import BackendAdapter
from typing import Dict, Any, List, Optional
import requests
import os
import time
from qiskit import QuantumCircuit

class PasqalBackendAdapter(BackendAdapter):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._connected = False
        self._client = None
        self._backend_info = None
        self.api_key = config.get('api_key') or os.getenv('PASQAL_API_KEY')
        self.base_url = config.get('base_url', 'https://api.pasqal.cloud')
        self._n_qubits = config.get('n_qubits', 100)  # Valor por defecto
        
    @property
    def n_qubits(self) -> int:
        """Número de qubits disponibles"""
        return self._n_qubits
    
    @property
    def t1s(self) -> Dict[int, float]:
        """Tiempos T1 por qubit - estimados para Pasqal"""
        estimated_t1 = 30000.0  # 30ms en microsegundos
        return {i: estimated_t1 for i in range(self.n_qubits)}
    
    @property
    def t2s(self) -> Dict[int, float]:
        """Tiempos T2 por qubit - estimados para Pasqal"""
        estimated_t2 = 20000.0  # 20ms en microsegundos
        return {i: estimated_t2 for i in range(self.n_qubits)}
    
    def connect(self) -> bool:
        """Conectar con la plataforma Pasqal"""
        try:
            if not self.api_key:
                raise ValueError("PASQAL_API_KEY no configurada")
                
            headers = {'Authorization': f'Bearer {self.api_key}'}
            response = requests.get(f'{self.base_url}/devices', headers=headers)
            
            if response.status_code == 200:
                devices = response.json()
                if devices:
                    self._backend_info = devices[0]  # Tomar el primer dispositivo
                    self._n_qubits = self._backend_info.get('qubit_count', 100)
                self._connected = True
                return True
            else:
                raise ConnectionError(f"Error connecting to Pasqal: {response.status_code}")
                
        except Exception as e:
            print(f"Connection failed: {e}")
            self._connected = False
            return False

    # ✅ AGREGAR ESTOS MÉTODOS QUE FALTAN:
    
    def _format_qonscious_result(self, pasqal_results: Dict[str, Any]) -> Dict[str, Any]:
        """Convertir resultados de Pasqal al formato que espera Qonscious"""
        if 'counts' in pasqal_results:
            # Si Pasqal ya devuelve counts en formato estándar
            counts = pasqal_results['counts']
        else:
            # Convertir formato de Pasqal a counts estándar
            counts = self._convert_pasqal_to_counts(pasqal_results)
        
        return {
            'counts': counts,
            'metadata': {
                'backend': 'pasqal',
                'shots': pasqal_results.get('shots', 1000),
                'success': True
            },
            'execution_time': pasqal_results.get('execution_time', 0)
        }
    
    def _convert_pasqal_to_counts(self, pasqal_results: Dict[str, Any]) -> Dict[str, int]:
        """Convertir resultados específicos de Pasqal a formato counts"""
        # Esto depende de cómo Pasqal devuelve los resultados
        # Ejemplo simplificado:
        counts = {}
        if 'results' in pasqal_results and isinstance(pasqal_results['results'], list):
            for result in pasqal_results['results']:
                bitstring = result.get('bitstring', '0' * self.n_qubits)
                counts[bitstring] = counts.get(bitstring, 0) + 1
        return counts

    def execute(self, circuit: QuantumCircuit, **kwargs) -> Dict[str, Any]:
        """Método execute requerido por BackendAdapter"""
        return self.execute_circuit(circuit, **kwargs)

    # ✅ TUS MÉTODOS (con algunas mejoras):

    def execute_circuit(self, circuit, **kwargs):
        """Ejecutar un circuito en Pasqal"""
        if not self._connected:
            if not self.connect():
                raise ConnectionError("No se pudo conectar a Pasqal")
        
        # Convertir circuito Qiskit a formato Pasqal
        pasqal_circuit = self._convert_to_pasqal_format(circuit)
        
        # Enviar job a Pasqal
        job_result = self._submit_to_pasqal(pasqal_circuit, **kwargs)
        
        return self._format_qonscious_result(job_result)
    
    def _convert_to_pasqal_format(self, qiskit_circuit):
        """Convertir circuito Qiskit a formato Pasqal"""
        pasqal_sequence = {
            "operations": [],
            "qubits": self.n_qubits
        }
        
        # Mapear operaciones de Qiskit a Pulser/Pasqal
        for instruction in qiskit_circuit.data:
            op_name = instruction.operation.name
            qubit_index = instruction.qubits[0].index
            
            if op_name == 'h':
                pasqal_sequence["operations"].append({
                    "type": "hadamard",
                    "target": qubit_index
                })
            elif op_name == 'x':
                pasqal_sequence["operations"].append({
                    "type": "x_gate", 
                    "target": qubit_index
                })
            elif op_name == 'y':
                pasqal_sequence["operations"].append({
                    "type": "y_gate",
                    "target": qubit_index
                })
            elif op_name == 'z':
                pasqal_sequence["operations"].append({
                    "type": "z_gate", 
                    "target": qubit_index
                })
            elif op_name == 'cx':
                control_index = instruction.qubits[0].index
                target_index = instruction.qubits[1].index
                pasqal_sequence["operations"].append({
                    "type": "cnot",
                    "control": control_index,
                    "target": target_index
                })
            # Agregar más mapeos según necesites
            
        return pasqal_sequence
    
    def _submit_to_pasqal(self, circuit_data, **kwargs):
        """Enviar circuito a Pasqal Cloud"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "circuit": circuit_data,
            "shots": kwargs.get('shots', 1000),
            "device_type": kwargs.get('device_type', 'qpu')  # 'qpu' o 'emulator'
        }
        
        response = requests.post(
            f'{self.base_url}/jobs',
            json=payload,
            headers=headers
        )
        
        if response.status_code == 202:
            job_id = response.json()['id']
            return self._wait_for_completion(job_id)
        else:
            raise Exception(f"Job submission failed: {response.text}")
    
    def _wait_for_completion(self, job_id, timeout=300):
        """Esperar a que el job termine"""
        start_time = time.time()
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        while time.time() - start_time < timeout:
            response = requests.get(f'{self.base_url}/jobs/{job_id}', headers=headers)
            
            if response.status_code == 200:
                job_data = response.json()
                status = job_data['status']
                
                if status == 'completed':
                    return job_data['results']
                elif status == 'failed':
                    raise Exception(f"Job failed: {job_data.get('error', 'Unknown error')}")
            else:
                raise Exception(f"Error checking job status: {response.status_code}")
            
            time.sleep(5)  # Poll cada 5 segundos
        
        raise TimeoutError("Job execution timeout")

    # ✅ MÉTODOS DE CONVENIENCIA:
    
    @classmethod
    def from_cloud(cls, api_key: str = None):
        """Crear adapter para Pasqal Cloud"""
        config = {
            'api_key': api_key or os.getenv('PASQAL_API_KEY'),
            'base_url': 'https://api.pasqal.cloud'
        }
        return cls(config)
    
    @classmethod
    def emulator(cls, api_key: str = None):
        """Crear adapter para el emulador de Pasqal"""
        config = {
            'api_key': api_key or os.getenv('PASQAL_API_KEY'),
            'device_type': 'emulator',
            'base_url': 'https://api.pasqal.cloud'
        }
        return cls(config)
    
    @classmethod
    def fresnel_qpu(cls, api_key: str = None):
        """Crear adapter para Fresnel QPU (100 qubits)"""
        config = {
            'api_key': api_key or os.getenv('PASQAL_API_KEY'),
            'device_type': 'qpu',
            'qpu_type': 'fresnel',
            'n_qubits': 100,
            'base_url': 'https://api.pasqal.cloud'
        }
        return cls(config)