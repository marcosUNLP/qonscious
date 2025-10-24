from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

import numpy as np
from qiskit import QuantumCircuit

from qonscious.foms.figure_of_merit import FigureOfMerit

if TYPE_CHECKING:
    from qonscious.adapters.backend_adapter import BackendAdapter
    from qonscious.results.result_types import ExperimentResult, FigureOfMeritResult


class PackedCHSHTest(FigureOfMerit):
    """
    I represent a true CHSH test that runs 4 different circuits for the 4 measurement settings.
    Each pair of qubits undergoes complete CHSH testing with all 4 measurement bases.
    """

    def __init__(self, num_qubits: int = 2):
        """
        Initialize with a user-defined number of qubits (must be even).

        Args:
            num_qubits (int): Total number of qubits (default=2). Must be even.

        Raises:
            ValueError: If num_qubits is not even or less than 2
        """
        if num_qubits % 2 != 0 or num_qubits < 2:
            raise ValueError(
                f"Number of qubits must be even and at least 2. Got {num_qubits}."
            )
        self.num_qubits = num_qubits
        self.num_pairs = num_qubits // 2

    def evaluate(self, backend_adapter: BackendAdapter, **kwargs) -> FigureOfMeritResult:
        """
        Execute the true CHSH test by running 4 circuits for the 4 measurement settings.

        Args:
            backend_adapter: The backend adapter to run the circuit on
            **kwargs: Additional arguments including:
                - shots: Total number of shots (default=1024, distributed as 256 per circuit)
                - shots_per_circuit: Direct specification of shots per circuit

        Returns:
            a FigureOfMeritResult with CHSH scores for each pair

        Raises:
            ValueError: If backend doesn't have enough qubits, shots are insufficient, 
                       or backend_adapter is invalid
            TypeError: If backend_adapter is not of the correct type
        """
        # Validate backend_adapter
        if backend_adapter is None:
            raise ValueError("backend_adapter cannot be None")
        
        # Check if backend has enough qubits
        try:
            backend_qubits = backend_adapter.get_backend().num_qubits
        except AttributeError as e:
            raise TypeError(
                "backend_adapter must have a get_backend() method returning a backend with num_qubits"
            ) from e
        
        if backend_qubits < self.num_qubits:
            raise ValueError(
                f"Backend has only {backend_qubits} qubits, "
                f"but {self.num_qubits} are required for this test. "
                f"Please reduce the number of qubits or use a different backend."
            )

        # Determine shots per circuit with validation
        shots_per_circuit = self._validate_and_get_shots(**kwargs)
        
        # Build and run 4 circuits for CHSH test
        circuits = self._build_chsh_circuits()
        
        try:
            all_results = []
            for qc in circuits:
                run_result: ExperimentResult = backend_adapter.run(qc, shots=shots_per_circuit)
                all_results.append(run_result)
        except Exception as e:
            raise RuntimeError(f"Failed to run circuits on backend: {str(e)}") from e
        
        # Compute true CHSH scores
        try:
            CHSH_Scores = compute_true_chsh_scores(all_results, self.num_qubits)
        except Exception as e:
            raise RuntimeError(f"Failed to compute CHSH scores: {str(e)}") from e
        
        evaluation_result: FigureOfMeritResult = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "figure_of_merit": self.__class__.__name__,
            "properties": CHSH_Scores,
            "experiment_result": all_results,
        }
        return evaluation_result

    def _validate_and_get_shots(self, **kwargs) -> int:
        """
        Validate shot parameters and return shots per circuit.
        
        Returns:
            int: Number of shots per circuit
            
        Raises:
            ValueError: If shots are insufficient or parameters are invalid
        """
        if 'shots_per_circuit' in kwargs:
            shots_per_circuit = kwargs['shots_per_circuit']
            if not isinstance(shots_per_circuit, int) or shots_per_circuit <= 0:
                raise ValueError(f"shots_per_circuit must be a positive integer, got {shots_per_circuit}")
            if shots_per_circuit < 10:
                raise ValueError(f"shots_per_circuit too low: {shots_per_circuit}. Minimum 10 recommended.")
            return shots_per_circuit
        else:
            total_shots = kwargs.get('shots', 1024)
            if not isinstance(total_shots, int) or total_shots <= 0:
                raise ValueError(f"shots must be a positive integer, got {total_shots}")
            
            if total_shots < 40:  # Minimum 10 per circuit × 4 circuits
                raise ValueError(
                    f"Total shots ({total_shots}) too low for 4 circuits. "
                    f"Minimum 40 required, 1024 recommended."
                )
            
            shots_per_circuit = total_shots // 4
            if shots_per_circuit < 10:
                raise ValueError(
                    f"Too few shots per circuit ({shots_per_circuit}). "
                    f"With {total_shots} total shots, each circuit gets only {shots_per_circuit} shots. "
                    f"Use at least 40 total shots."
                )
            return shots_per_circuit

    def _build_chsh_circuits(self) -> List[QuantumCircuit]:
        """
        Build 4 circuits for the 4 CHSH measurement settings applied to all pairs.
        
        Returns:
            List of 4 QuantumCircuits for CHSH measurement settings
        """
        circuits = []
        
        # CHSH measurement settings (angles for second qubit of each pair)
        chsh_angles = [
            [np.pi/4, np.pi/4, np.pi/4, np.pi/4],    # Setting 0: E00 bases
            [np.pi/4, -np.pi/4, np.pi/4, -np.pi/4],  # Setting 1: E01 bases  
            [-np.pi/4, np.pi/4, -np.pi/4, np.pi/4],  # Setting 2: E10 bases
            [-np.pi/4, -np.pi/4, -np.pi/4, -np.pi/4] # Setting 3: E11 bases
        ]
        
        for setting_idx, angles in enumerate(chsh_angles):
            qc = QuantumCircuit(self.num_qubits, self.num_qubits)
            
            # Prepare Bell pairs (|00⟩ + |11⟩)/√2 for all pairs
            for i in range(0, self.num_qubits, 2):
                qc.h(i)
                qc.cx(i, i + 1)
            
            # Apply CHSH measurement settings to each pair
            for pair_idx in range(self.num_pairs):
                qubit_idx = 2 * pair_idx + 1  # Second qubit of the pair
                angle = angles[pair_idx % len(angles)]
                qc.ry(angle, qubit_idx)
            
            qc.measure(range(self.num_qubits), range(self.num_qubits))
            circuits.append(qc)
            
        return circuits


def compute_true_chsh_scores(experiment_results: List[ExperimentResult], num_qubits: int) -> dict:
    """
    Compute true CHSH scores from 4 experiment results.
    
    Args:
        experiment_results: List of 4 ExperimentResults for the 4 CHSH settings
        num_qubits: Total number of qubits used
        
    Returns:
        Dictionary with CHSH scores for each pair
        
    Raises:
        ValueError: If inputs are invalid or results are inconsistent
    """
    # Input validation
    if not experiment_results:
        raise ValueError("experiment_results cannot be empty")
    
    if len(experiment_results) != 4:
        raise ValueError(f"Need exactly 4 experiment results for CHSH test, got {len(experiment_results)}")
    
    if num_qubits % 2 != 0:
        raise ValueError(f"num_qubits must be even, got {num_qubits}")
    
    num_pairs = num_qubits // 2
    
    # Validate that all results have counts
    for i, result in enumerate(experiment_results):
        if "counts" not in result:
            raise ValueError(f"Experiment result {i} missing 'counts' key")
        if not isinstance(result["counts"], dict):
            raise ValueError(f"Experiment result {i} 'counts' must be a dictionary")
        if not result["counts"]:
            raise ValueError(f"Experiment result {i} has empty counts")

    # Process counts for each setting and each pair
    all_pair_counts = [[defaultdict(int) for _ in range(num_pairs)] for _ in range(4)]
    
    for setting_idx, result in enumerate(experiment_results):
        counts = result["counts"]
        
        for bitstring, count in counts.items():
            # Validate bitstring length
            if len(bitstring) != num_qubits:
                raise ValueError(
                    f"Bitstring length mismatch: expected {num_qubits}, "
                    f"got {len(bitstring)} in setting {setting_idx}"
                )
            
            bits = bitstring[::-1]  # Convert to little-endian
            for pair_idx in range(num_pairs):
                a = bits[2 * pair_idx]
                b = bits[2 * pair_idx + 1]
                all_pair_counts[setting_idx][pair_idx][a + b] += count

    def compute_E(correlation_counts):
        """Compute correlation value E = P(00) + P(11) - P(01) - P(10)"""
        total = sum(correlation_counts.values())
        if total == 0:
            return 0.0
        return (correlation_counts.get("00", 0) + correlation_counts.get("11", 0) - 
                correlation_counts.get("01", 0) - correlation_counts.get("10", 0)) / total

    # Compute CHSH scores for each pair
    results = {
        "shots_per_circuit": sum(experiment_results[0]["counts"].values()),
        "total_shots": sum(experiment_results[0]["counts"].values()) * 4,
        "pairs": {}
    }
    
    chsh_scores = []
    
    for pair_idx in range(num_pairs):
        # Get E values for this pair from all 4 settings
        E_values = [
            compute_E(all_pair_counts[0][pair_idx]),  # E00
            compute_E(all_pair_counts[1][pair_idx]),  # E01
            compute_E(all_pair_counts[2][pair_idx]),  # E10  
            compute_E(all_pair_counts[3][pair_idx])   # E11
        ]
        
        # True CHSH score: S = E00 + E01 + E10 - E11
        S = E_values[0] + E_values[1] + E_values[2] - E_values[3]
        chsh_scores.append(S)
        
        results["pairs"][f"pair_{pair_idx}"] = {
            "CHSH_score": S,
            "E00": E_values[0],
            "E01": E_values[1], 
            "E10": E_values[2],
            "E11": E_values[3]
        }
    
    # Calculate statistics
    results["average_chsh_score"] = sum(chsh_scores) / len(chsh_scores) if chsh_scores else 0.0
    results["individual_chsh_scores"] = chsh_scores
    results["violates_classical"] = any(score > 2 for score in chsh_scores)
    results["max_chsh_score"] = max(chsh_scores) if chsh_scores else 0.0
    
    return results
