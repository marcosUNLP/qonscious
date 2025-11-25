from __future__ import annotations

import time
import os
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from qiskit import QuantumCircuit
	from qonscious.results.result_types import ExperimentResult

from qonscious.adapters.backend_adapter import BackendAdapter

try:
	from quafu import User, Task, QuantumCircuit as QuafuQuantumCircuit
	QUAFU_AVAILABLE = True
except ImportError:
	QUAFU_AVAILABLE = False


class QuafuBackendAdapter(BackendAdapter):
	"""Adapter for Quafu with interactive backend selection during CHSH tests."""

	def __init__(
			self,
			backend_name: str | None = None,
			api_token: str | None = None):
		if not QUAFU_AVAILABLE:
			raise ImportError(
				"Quafu is not installed. Please install it with: pip install pyquafu"
			)

		self.backend_name = backend_name
		self.api_token = api_token or os.getenv("QUAFU_TOKEN")
		self._n_qubits = 10  # Default, will be updated if backend is selected
		self._backend_selected = False
		self._token_provided = False

		# Initialize user with or without token
		self._initialize_user()

		# If backend is provided, use it directly
		if backend_name:
			self._set_backend_info(backend_name)
			self._backend_selected = True

	def _initialize_user(self):
		"""Initialize Quafu User with interactive token selection if needed."""
		# If token is already provided via env or parameter, use it
		if self.api_token:
			self.user = User(self.api_token)
			self._token_provided = True
			print("🔐 Using provided API token")
			return

		# Interactive token selection
		print("\n🔐 QUAFU AUTHENTICATION")
		print("=" * 40)
		print("Options:")
		print("  1. Use API token (for real hardware access)")
		print("  2. Continue without token (simulators only)")
		
		while True:
			try:
				choice = input("\nSelect option (1-2): ").strip()
				if choice == '1':
					token = input("Enter your Quafu API token: ").strip()
					if token:
						self.api_token = token
						self.user = User(token)
						self._token_provided = True
						print("✅ Token set successfully")
						break
					else:
						print("❌ Token cannot be empty")
				elif choice == '2':
					self.user = User()  # No token
					self._token_provided = False
					print("ℹ️  Continuing without token - simulators only")
					break
				else:
					print("❌ Invalid selection. Choose 1 or 2.")
			except KeyboardInterrupt:
				print("\n⚠️  Using default (no token)")
				self.user = User()
				self._token_provided = False
				break

	def _set_backend_info(self, backend_name: str):
		"""Set backend information from actual Quafu backend."""
		try:
			backends = self.user.get_available_backends()
			if backend_name in backends:
				backend_obj = backends[backend_name]
				self._n_qubits = getattr(backend_obj, 'qubit_num', 10)
				print(f"✅ Backend {backend_name}: {self._n_qubits} qubits")
			else:
				print(f"⚠️  Backend {backend_name} not found, using default 10 qubits")
				self._n_qubits = 10
		except Exception as e:
			print(f"⚠️  Could not get backend info: {e}, using default 10 qubits")
			self._n_qubits = 10

	def _simplify_angles(self, params):
		"""Convert angles to exact fractions of pi for better precision."""
		simplified = []
		for angle in params:
			# Identificar ángulos comunes con tolerancia
			if abs(angle - 0.7853981633974483) < 1e-10:  # π/4
				simplified_angle = math.pi / 4
				print(f"   🔄 {angle:.15f} → π/4 ({simplified_angle:.15f})")
				simplified.append(simplified_angle)
			elif abs(angle - 1.5707963267948966) < 1e-10:  # π/2  
				simplified_angle = math.pi / 2
				print(f"   🔄 {angle:.15f} → π/2 ({simplified_angle:.15f})")
				simplified.append(simplified_angle)
			elif abs(angle + 0.7853981633974483) < 1e-10:  # -π/4
				simplified_angle = -math.pi / 4
				print(f"   🔄 {angle:.15f} → -π/4 ({simplified_angle:.15f})")
				simplified.append(simplified_angle)
			elif abs(angle + 1.5707963267948966) < 1e-10:  # -π/2
				simplified_angle = -math.pi / 2
				print(f"   🔄 {angle:.15f} → -π/2 ({simplified_angle:.15f})")
				simplified.append(simplified_angle)
			elif abs(angle - 3.141592653589793) < 1e-10:  # π
				simplified_angle = math.pi
				print(f"   🔄 {angle:.15f} → π ({simplified_angle:.15f})")
				simplified.append(simplified_angle)
			elif abs(angle + 3.141592653589793) < 1e-10:  # -π
				simplified_angle = -math.pi
				print(f"   🔄 {angle:.15f} → -π ({simplified_angle:.15f})")
				simplified.append(simplified_angle)
			else:
				simplified.append(angle)
		return simplified

	def _interactive_backend_selection(self):
		"""Interactive backend selection triggered during CHSH execution."""
		if self._backend_selected:
			return

		print("\n🎯 QUAFU BACKEND SELECTION")
		print("=" * 50)

		# Get available backends
		try:
			backends = self.user.get_available_backends()
			backends_list = list(backends.items())

			# Filter backends based on token availability
			available_backends = []
			for name, obj in backends_list:
				status = getattr(obj, 'status', '?').lower()
				# Without token, only show simulators that are online
				if not self._token_provided:
					if 'sim' in name.lower() and status == 'online':
						available_backends.append((name, obj))
				else:
					# With token, show all available backends
					available_backends.append((name, obj))

			if not available_backends:
				if not self._token_provided:
					print("❌ No simulators available. Need API token for hardware access.")
					print("💡 Set QUAFU_TOKEN environment variable or provide token interactively")
				else:
					print("❌ No backends available at the moment")
				# Use default simulator
				self.backend_name = "ScQ-Sim10"
				self._set_backend_info("ScQ-Sim10")
				self._backend_selected = True
				return

			print("\nAvailable Quafu backends:")
			print("-" * 40)
			for i, (name, obj) in enumerate(available_backends, 1):
				qubits = getattr(obj, 'qubit_num', '?')
				status = getattr(obj, 'status', '?').capitalize()
				queued = getattr(obj, 'tasks_queued', '?')
				token_indicator = " 🔐" if not self._token_provided and 'sim' in name.lower() else ""
				print(
					f"{i:2d}. {name:<15} {qubits:>2} qubits  {status:<8} (queue: {queued}){token_indicator}")

			# Show token status
			if not self._token_provided:
				print("\n💡 Using simulators only")

			# Interactive selection
			while True:
				try:
					choice = input(
						f"\nSelect backend (1-{len(available_backends)}): ").strip()
					if choice.isdigit():
						idx = int(choice) - 1
						if 0 <= idx < len(available_backends):
							self.backend_name = available_backends[idx][0]
							self._set_backend_info(self.backend_name)
							self._backend_selected = True
							break
					print("❌ Invalid selection. Try again.")
				except KeyboardInterrupt:
					print("\n⚠️  Selection cancelled. Using default simulator.")
					self.backend_name = "ScQ-Sim10"
					self._set_backend_info("ScQ-Sim10")
					self._backend_selected = True
					break

		except Exception as e:
			print(f"⚠️  Could not load backends: {e}")
			print("Using default: ScQ-Sim10")
			self.backend_name = "ScQ-Sim10"
			self._set_backend_info("ScQ-Sim10")
			self._backend_selected = True

	def run(self, circuit: QuantumCircuit, **kwargs) -> ExperimentResult:
		"""Execute quantum circuit on Quafu backend."""

		if not self._backend_selected:
			self._interactive_backend_selection()

		shots = kwargs.get("shots", 1024)

		# Show token status
		token_status = "PROVIDED" if self._token_provided else "NOT PROVIDED (simulators only)"
		print(f"🔐 Token: {token_status}")

		# Convert Qiskit circuit to Quafu circuit
		quafu_circuit = self._convert_circuit(circuit)

		try:
			task = Task(self.user)
			task.config(
				backend=self.backend_name,
				shots=shots,
				compile=True
			)

			# Submit task
			submit_result = task.send(quafu_circuit, wait=False)
			task_id = submit_result.taskid

			print(f"📤 Task submitted: {task_id}")
			print("⏳ Waiting for results...", end="", flush=True)

			# Wait for completion
			max_wait_time = 300  # 5 minutes maximum
			start_time = time.time()
			
			while time.time() - start_time < max_wait_time:
				try:
					# Get task status
					task_status = task.retrieve(task_id)
					
					# Check status attribute
					status = None
					if hasattr(task_status, 'status'):
						status = task_status.status
					elif hasattr(task_status, 'task_status'):
						status = task_status.task_status
					elif hasattr(task_status, 'state'):
						status = task_status.state
					
					if status == 'Completed':
						print(" ✅")
						break
					elif status in ['Failed', 'Cancelled', 'Error']:
						print(f"\n❌ Task failed: {status}")
						break
						
					print(".", end="", flush=True)
					time.sleep(5)
					
				except Exception as e:
					print(f"\n⚠️  Error checking status: {e}")
					time.sleep(5)
					continue
			else:
				print("\n⏰ Timeout waiting for results")

			# Get results
			counts = {}
			if hasattr(task_status, 'results') and hasattr(task_status.results, 'counts'):
				counts = task_status.results.counts
			elif hasattr(task_status, 'counts'):
				counts = task_status.counts
			elif hasattr(submit_result, 'counts'):
				counts = submit_result.counts

			# 🔥 CRITICAL FIX: Convert Quafu (little-endian) to expected format (big-endian)
			converted_counts = {}
			for bitstring, count in counts.items():
				# Quafu returns little-endian, CHSH function expects big-endian format
				converted_bitstring = bitstring[::-1]  # Reverse the bit order
				converted_counts[converted_bitstring] = count

			print(f"🔀 Endianness conversion: {len(counts)} counts converted")
			if counts:
				example_orig = list(counts.keys())[0]
				example_conv = list(converted_counts.keys())[0]
				print(f"🔀 Example: '{example_orig}' -> '{example_conv}'")

			return {
				"counts": converted_counts,  # 🔥 Use converted counts
				"shots": shots,
				"backend_properties": {
					"name": f"quafu_{self.backend_name}",
					"task_id": task_id,
					"token_used": self._token_provided
				},
				"timestamps": {
					"created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
					"finished": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
				},
				"raw_results": task_status
			}

		except Exception as e:
			print(f"\n❌ Error: {e}")
			import traceback
			traceback.print_exc()
			return {
				"counts": {},
				"shots": shots,
				"backend_properties": {
					"name": f"quafu_{self.backend_name}", 
					"error": str(e),
					"token_used": self._token_provided
				},
				"timestamps": {"created": "", "finished": ""},
				"raw_results": None
			}

	def _convert_circuit(self, qiskit_circuit: QuantumCircuit) -> QuafuQuantumCircuit:
		"""Convert Qiskit circuit to Quafu circuit usando OpenQASM 2.0"""
		
		try:
			# 🔥 NUEVO: Convertir a OpenQASM 2.0
			qasm_str = qiskit_circuit.qasm()
			print(f"🔧 OpenQASM conversion: {len(qasm_str)} characters")
			
			# Crear circuito Quafu desde OpenQASM
			quafu_circuit = QuafuQuantumCircuit(qiskit_circuit.num_qubits)
			quafu_circuit.from_openqasm(qasm_str)
			
			print("✅ Circuito convertido via OpenQASM")
			print(f"✅ Instrucciones Quafu: {len(quafu_circuit.instructions)}")
			
			# Mostrar algunas instrucciones para debug
			print("\n📋 PRIMERAS 10 INSTRUCCIONES QUAFU:")
			for i, gate in enumerate(quafu_circuit.instructions[:10]):
				print(f"  {i:2d}. {gate}")
			if len(quafu_circuit.instructions) > 10:
				print(f"  ... y {len(quafu_circuit.instructions) - 10} más")
			
			return quafu_circuit
			
		except Exception as e:
			print(f"⚠️  OpenQASM conversion failed: {e}")
			print("🔄 Fallback a conversión manual...")
			return self._convert_circuit_manual(qiskit_circuit)

	def _convert_circuit_manual(self, qiskit_circuit: QuantumCircuit) -> QuafuQuantumCircuit:
		"""Fallback: conversión manual de circuito"""
		quafu_circuit = QuafuQuantumCircuit(qiskit_circuit.num_qubits)
		
		print(f"🔧 Converting circuit manually: {len(qiskit_circuit)} instructions")
		print(f"🔧 Qiskit circuit qubits: {qiskit_circuit.num_qubits}")
		
		# Debug: show all Qiskit circuit instructions
		print("\n📋 QISKIT INSTRUCTIONS:")
		for i, instruction in enumerate(qiskit_circuit):
			gate_name = instruction.operation.name
			qubits = [q.index for q in instruction.qubits] if hasattr(instruction.qubits[0], 'index') else [q._index for q in instruction.qubits]
			params = getattr(instruction.operation, 'params', [])
			print(f"  {i:2d}. {gate_name:8} qubits{qubits} params{params}")
		
		converted_count = 0
		print("\n🎯 PRECISION CONVERSION:")
		for i, instruction in enumerate(qiskit_circuit):
			try:
				gate_name = instruction.operation.name
				
				# Extract qubit indices
				qubit_indices = []
				for q in instruction.qubits:
					if hasattr(q, 'index'):
						qubit_indices.append(q.index)
					elif hasattr(q, '_index'):
						qubit_indices.append(q._index)
					else:
						qubit_indices.append(instruction.qubits.index(q))
				
				# PARAMETERS WITH IMPROVED PRECISION
				params = []
				if hasattr(instruction.operation, 'params'):
					original_params = [float(p) for p in instruction.operation.params]
					if original_params and gate_name in ['rx', 'ry', 'rz']:
						print(f"  Gate {i}: {gate_name} on {qubit_indices}")
						params = self._simplify_angles(original_params)
					else:
						params = original_params
				
				# GATE CONVERSION
				converted = False
				if gate_name == 'h' and len(qubit_indices) == 1:
					quafu_circuit.h(qubit_indices[0])
					converted = True
				elif gate_name == 'x' and len(qubit_indices) == 1:
					quafu_circuit.x(qubit_indices[0])
					converted = True
				elif gate_name == 'y' and len(qubit_indices) == 1:
					quafu_circuit.y(qubit_indices[0])
					converted = True
				elif gate_name == 'z' and len(qubit_indices) == 1:
					quafu_circuit.z(qubit_indices[0])
					converted = True
				elif gate_name == 'rx' and len(qubit_indices) == 1 and params:
					quafu_circuit.rx(qubit_indices[0], params[0])
					converted = True
				elif gate_name == 'ry' and len(qubit_indices) == 1 and params:
					quafu_circuit.ry(qubit_indices[0], params[0])
					converted = True
				elif gate_name == 'rz' and len(qubit_indices) == 1 and params:
					quafu_circuit.rz(qubit_indices[0], params[0])
					converted = True
				elif gate_name == 'cx' and len(qubit_indices) == 2:
					quafu_circuit.cnot(qubit_indices[0], qubit_indices[1])
					converted = True
				elif gate_name == 'ccx' and len(qubit_indices) == 3:
					# Para CCX, usar descomposición básica
					print(f"  🔄 CCX {qubit_indices} → descomposición básica")
					self._add_ccx_decomposition(quafu_circuit, qubit_indices[0], qubit_indices[1], qubit_indices[2])
					converted = True
				elif gate_name == 'measure':
					converted = True  # Handled at the end
					pass
				
				if converted:
					converted_count += 1
				else:
					print(f"⚠️  Gate {i}: {gate_name}{params} on {qubit_indices} - not supported")
					
			except Exception as e:
				print(f"❌ Error in instruction {i}: {e}")
				continue
	
		quafu_circuit.measure(list(range(qiskit_circuit.num_qubits)))
		print(f"✅ Circuit converted: {converted_count}/{len(qiskit_circuit)} instructions")
		print(f"✅ Final Quafu instructions: {len(quafu_circuit.instructions)}")
		
		return quafu_circuit

	def _add_ccx_decomposition(self, circuit, control1, control2, target):
		"""Descomposición básica de CCX como fallback"""
		# Implementación simple usando CNOTs y Hadamards
		circuit.h(target)
		circuit.cnot(control2, target)
		circuit.tdg(target)
		circuit.cnot(control1, target)
		circuit.t(target)
		circuit.cnot(control2, target)
		circuit.tdg(target)
		circuit.cnot(control1, target)
		circuit.t(control2)
		circuit.t(target)
		circuit.h(target)
		circuit.cnot(control1, control2)
		circuit.t(control1)
		circuit.tdg(control2)
		circuit.cnot(control1, control2)

	@property
	def n_qubits(self) -> int:
		return self._n_qubits

	@property
	def t1s(self) -> dict[int, float] | None:
		return None

	@property
	def t2s(self) -> dict[int, float] | None:
		return None

	@property
	def name(self) -> str:
		backend_name = self.backend_name or "not_selected"
		return f"quafu_{backend_name}"
