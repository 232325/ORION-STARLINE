"""
Quantum Measurement Module
=========================

Quantum o'lchov operatsiyalari va portfolio measurement algorithms.
"""

import numpy as np
import cmath
from typing import List, Dict, Tuple, Optional, Union, Callable
from dataclasses import dataclass
from scipy.stats import chi2, norm
from scipy.linalg import eig, eigh
import matplotlib.pyplot as plt

from .quantum_state import QuantumPortfolioState, QuantumState


@dataclass
class MeasurementConfig:
    """Quantum o'lchov konfiguratsiya parametrlari"""
    measurement_basis: str = 'computational'  # computational, pauli_x, pauli_y, pauli_z
    measurement_type: str = 'weak'  # strong, weak, continuous
    collapse_threshold: float = 0.1  # Collapse threshold
    measurement_noise: float = 0.01  # Measurement noise level
    n_measurements: int = 1000  # Default measurement count
    confidence_level: float = 0.95  # Confidence level for statistics


class QuantumMeasurement:
    """
    Quantum Measurement Operations
    
    Quantum portfolio measurement va collapse operatsiyalari.
    """
    
    def __init__(self, config: MeasurementConfig = None):
        self.config = config or MeasurementConfig()
        self.measurement_history = []
        self.collapse_statistics = {}
        self.measurement_errors = []
        
    def strong_measurement(self, quantum_state: QuantumState,
                         observable: np.ndarray = None) -> Dict:
        """
        Strong (ideal) quantum measurement
        
        Args:
            quantum_state: O'lchanadigan quantum state
            observable: Observable operator (default: identity)
        
        Returns:
            Measurement result va statistics
        """
        if observable is None:
            observable = np.eye(len(quantum_state.basis_states))
        
        # Eigenvalue decomposition
        eigenvals, eigenvecs = eigh(observable)
        
        # Measurement probabilities
        probabilities = quantum_state.get_probabilities()
        
        # Random measurement
        measurement_result_idx = np.random.choice(
            len(quantum_state.basis_states), 
            p=probabilities
        )
        
        measurement_result = quantum_state.basis_states[measurement_result_idx]
        
        # Collapse state
        collapsed_state = quantum_state.collapse_to_state(measurement_result)
        
        # Record measurement
        measurement_record = {
            'result': measurement_result,
            'probability': probabilities[measurement_result_idx],
            'expected_value': quantum_state.expectation_value(observable),
            'collapsed_state': collapsed_state,
            'measurement_type': 'strong'
        }
        
        self.measurement_history.append(measurement_record)
        
        return measurement_record
    
    def weak_measurement(self, quantum_state: QuantumState,
                        observable: np.ndarray = None,
                        coupling_strength: float = 0.1) -> Dict:
        """
        Weak measurement (minimal disturbance)
        
        Args:
            quantum_state: O'lchanadigan quantum state
            observable: Observable operator
            coupling_strength: Weak coupling strength
        
        Returns:
            Weak measurement result
        """
        if observable is None:
            observable = np.eye(len(quantum_state.basis_states))
        
        # Weak measurement operator (simplified)
        weak_operator = np.eye(len(quantum_state.basis_states)) + \
                       coupling_strength * (observable - np.trace(observable) * np.eye(len(quantum_state.basis_states)) / len(quantum_state.basis_states))
        
        # Apply weak measurement
        measured_state_amplitudes = np.dot(weak_operator, quantum_state.amplitudes)
        measured_state_amplitudes = measured_state_amplitudes / np.linalg.norm(measured_state_amplitudes)
        
        measured_state = QuantumState(measured_state_amplitudes, quantum_state.basis_states)
        
        # Estimate expectation value (weak measurement approximation)
        estimated_expectation = np.real(np.dot(
            np.conj(measured_state_amplitudes), 
            np.dot(observable, measured_state_amplitudes)
        ))
        
        measurement_record = {
            'estimated_expectation': estimated_expectation,
            'measured_state': measured_state,
            'coupling_strength': coupling_strength,
            'disturbance': np.linalg.norm(quantum_state.amplitudes - measured_state_amplitudes),
            'measurement_type': 'weak'
        }
        
        return measurement_record
    
    def portfolio_measurement_analysis(self, portfolio: QuantumPortfolioState,
                                     n_measurements: int = 1000) -> Dict:
        """
        Portfolio uchun comprehensive measurement analysis
        
        Args:
            portfolio: O'lchanadigan portfolio
            n_measurements: O'lchovlar soni
        
        Returns:
            Comprehensive measurement analysis
        """
        measurement_results = []
        collapse_times = []
        
        for i in range(n_measurements):
            # Pre-measurement state
            original_state = portfolio.state
            
            # Perform measurement
            result = self.strong_measurement(original_state)
            measurement_results.append(result['result'])
            
            # Track collapse time (number of measurements until collapse)
            if i == 0:
                collapse_times.append(i + 1)
            else:
                if measurement_results[i] != measurement_results[i-1]:
                    collapse_times.append(i + 1)
        
        # Statistical analysis
        unique_results = list(set(measurement_results))
        result_frequencies = {}
        
        for result in unique_results:
            count = measurement_results.count(result)
            result_frequencies[result] = count / n_measurements
        
        # Quantum statistics
        expected_frequencies = {}
        for asset in portfolio.assets:
            if asset in original_state.basis_states:
                idx = original_state.basis_states.index(asset)
                expected_frequencies[asset] = np.abs(original_state.amplitudes[idx])**2
            else:
                expected_frequencies[asset] = 0
        
        # Chi-square test for quantum behavior
        chi_square_stat = 0
        for asset in unique_results:
            observed = result_frequencies[asset] * n_measurements
            expected = expected_frequencies[asset] * n_measurements
            if expected > 0:
                chi_square_stat += (observed - expected)**2 / expected
        
        degrees_of_freedom = len(unique_results) - 1
        p_value = 1 - chi2.cdf(chi_square_stat, degrees_of_freedom)
        
        # Collapse statistics
        collapse_analysis = {
            'avg_collapse_time': np.mean(collapse_times),
            'collapse_variance': np.var(collapse_times),
            'stable_measurements': sum(1 for i in range(1, len(measurement_results)) 
                                     if measurement_results[i] == measurement_results[i-1]),
            'quantum_signature': p_value < 0.05  # Statistically significant quantum behavior
        }
        
        return {
            'measurement_results': measurement_results,
            'result_frequencies': result_frequencies,
            'expected_frequencies': expected_frequencies,
            'chi_square_stat': chi_square_stat,
            'p_value': p_value,
            'degrees_of_freedom': degrees_of_freedom,
            'collapse_analysis': collapse_analysis,
            'quantum_efficiency': np.mean(list(result_frequencies.values())),
            'measurement_noise': np.std(list(result_frequencies.values()))
        }
    
    def continuous_measurement(self, portfolio: QuantumPortfolioState,
                             time_steps: int = 100,
                             decoherence_rate: float = 0.01) -> Dict:
        """
        Continuous quantum measurement with decoherence
        
        Args:
            portfolio: Measurement qilinadigan portfolio
            time_steps: Vaqt qadamlari soni
            decoherence_rate: Decoherence rate
        
        Returns:
            Continuous measurement trajectory
        """
        trajectory = []
        current_state = portfolio.state
        
        for t in range(time_steps):
            # Apply decoherence
            if t > 0:
                decoherence_factor = np.exp(-decoherence_rate * t)
                current_state.amplitudes *= decoherence_factor
                current_state.normalize()
            
            # Perform measurement
            measurement_result = current_state.measure()
            
            # Record trajectory
            trajectory_point = {
                'time_step': t,
                'measurement_result': measurement_result,
                'state_vector': current_state.get_state_vector(),
                'probabilities': current_state.get_probabilities(),
                'decoherence_factor': decoherence_factor if t > 0 else 1.0
            }
            
            trajectory.append(trajectory_point)
        
        # Analysis
        measurement_sequence = [point['measurement_result'] for point in trajectory]
        
        # Quantum trajectory statistics
        transitions = 0
        for i in range(1, len(measurement_sequence)):
            if measurement_sequence[i] != measurement_sequence[i-1]:
                transitions += 1
        
        return {
            'trajectory': trajectory,
            'measurement_sequence': measurement_sequence,
            'transition_rate': transitions / time_steps,
            'final_state': trajectory[-1]['state_vector'],
            'quantum_efficiency': 1 - transitions / time_steps,
            'coherence_decay': trajectory[0]['probabilities'][-1] / trajectory[0]['probabilities'][0]
        }
    
    def quantum_tomography(self, portfolio: QuantumPortfolioState,
                         measurement_settings: List[Dict] = None) -> Dict:
        """
        Quantum state tomography
        
        Args:
            portfolio: Tomography qilinadigan portfolio
            measurement_settings: Measurement sozlamalar
        
        Returns:
            Reconstructed quantum state
        """
        if measurement_settings is None:
            # Default measurement settings (Pauli measurements)
            measurement_settings = [
                {'basis': 'pauli_z', 'observable': np.eye(len(portfolio.assets))},
                {'basis': 'pauli_x', 'observable': self._pauli_x_matrix(len(portfolio.assets))},
                {'basis': 'pauli_y', 'observable': self._pauli_y_matrix(len(portfolio.assets))}
            ]
        
        tomography_data = {}
        
        for setting in measurement_settings:
            basis_name = setting['basis']
            observable = setting['observable']
            
            # Perform measurements in this basis
            measurements = []
            for _ in range(self.config.n_measurements):
                result = self.strong_measurement(portfolio.state, observable)
                measurements.append(result)
            
            # Process measurement data
            measurement_frequencies = {}
            for result in measurements:
                outcome = result['result']
                if outcome not in measurement_frequencies:
                    measurement_frequencies[outcome] = 0
                measurement_frequencies[outcome] += 1
            
            # Normalize frequencies
            total_measurements = len(measurements)
            for outcome in measurement_frequencies:
                measurement_frequencies[outcome] /= total_measurements
            
            tomography_data[basis_name] = {
                'frequencies': measurement_frequencies,
                'observable': observable,
                'expectation_value': portfolio.state.expectation_value(observable)
            }
        
        # Reconstruct density matrix (simplified reconstruction)
        reconstructed_state = self._reconstruct_density_matrix(tomography_data, len(portfolio.assets))
        
        # Calculate fidelity with original state
        original_density_matrix = np.outer(portfolio.state.amplitudes, np.conj(portfolio.state.amplitudes))
        fidelity = self._calculate_fidelity(original_density_matrix, reconstructed_state)
        
        return {
            'tomography_data': tomography_data,
            'reconstructed_state': reconstructed_state,
            'original_state': original_density_matrix,
            'fidelity': fidelity,
            'reconstruction_error': 1 - fidelity,
            'measurement_completeness': len(measurement_settings) / 3  # Pauli basis completeness
        }
    
    def adaptive_measurement(self, portfolio: QuantumPortfolioState,
                           target_asset: str,
                           adaptation_threshold: float = 0.8) -> Dict:
        """
        Adaptive quantum measurement
        
        Args:
            portfolio: Measurement qilinadigan portfolio
            target_asset: Maqsad asset
            adaptation_threshold: Adaptation threshold
        
        Returns:
            Adaptive measurement strategy va results
        """
        current_state = portfolio.state
        measurement_sequence = []
        adaptation_history = []
        
        max_iterations = 50
        iteration = 0
        
        while iteration < max_iterations:
            # Check current probability of target asset
            if target_asset in current_state.basis_states:
                target_idx = current_state.basis_states.index(target_asset)
                target_probability = np.abs(current_state.amplitudes[target_idx])**2
            else:
                target_probability = 0
            
            # Adaptive strategy
            if target_probability > adaptation_threshold:
                # High confidence - perform strong measurement
                result = self.strong_measurement(current_state)
                measurement_sequence.append({
                    'iteration': iteration,
                    'measurement_type': 'strong',
                    'result': result,
                    'target_probability': target_probability
                })
                
                if result['result'] == target_asset:
                    # Target asset measured successfully
                    break
                    
            else:
                # Low confidence - perform weak measurement
                weak_result = self.weak_measurement(current_state, 
                                                  coupling_strength=0.1)
                measurement_sequence.append({
                    'iteration': iteration,
                    'measurement_type': 'weak',
                    'result': weak_result,
                    'estimated_expectation': weak_result['estimated_expectation']
                })
                
                # Update state based on weak measurement
                current_state = weak_result['measured_state']
            
            adaptation_history.append({
                'iteration': iteration,
                'target_probability': target_probability,
                'measurement_strategy': 'strong' if target_probability > adaptation_threshold else 'weak',
                'state_norm': np.linalg.norm(current_state.amplitudes)
            })
            
            iteration += 1
        
        # Final analysis
        successful_measurement = (measurement_sequence[-1]['measurement_type'] == 'strong' and
                                measurement_sequence[-1]['result']['result'] == target_asset)
        
        return {
            'measurement_sequence': measurement_sequence,
            'adaptation_history': adaptation_history,
            'final_state': current_state,
            'successful_measurement': successful_measurement,
            'total_iterations': iteration,
            'measurement_efficiency': 1 - iteration / max_iterations
        }
    
    def _pauli_x_matrix(self, n: int) -> np.ndarray:
        """Pauli X matrix generator"""
        if n == 2:
            return np.array([[0, 1], [1, 0]])
        else:
            # Higher dimensional generalization
            matrix = np.zeros((n, n))
            for i in range(n-1):
                matrix[i, i+1] = 1
                matrix[i+1, i] = 1
            return matrix
    
    def _pauli_y_matrix(self, n: int) -> np.ndarray:
        """Pauli Y matrix generator"""
        if n == 2:
            return np.array([[0, -1j], [1j, 0]])
        else:
            matrix = np.zeros((n, n), dtype=complex)
            for i in range(n-1):
                matrix[i, i+1] = -1j
                matrix[i+1, i] = 1j
            return matrix
    
    def _reconstruct_density_matrix(self, tomography_data: Dict, n_dim: int) -> np.ndarray:
        """Density matrix reconstruction from tomography data"""
        # Simplified reconstruction - in practice, more sophisticated methods needed
        density_matrix = np.zeros((n_dim, n_dim), dtype=complex)
        
        # Use measurement data to estimate density matrix elements
        for basis, data in tomography_data.items():
            frequencies = data['frequencies']
            # Simplified reconstruction logic
            for i in range(n_dim):
                for j in range(n_dim):
                    if str(i) in frequencies:
                        density_matrix[i, i] += frequencies[str(i)] / len(tomography_data)
        
        return density_matrix
    
    def _calculate_fidelity(self, state1: np.ndarray, state2: np.ndarray) -> float:
        """Fidelity calculation between two density matrices"""
        # Simplified fidelity calculation
        eigenvals = eig(np.dot(state1, state2))[0]
        eigenvals = np.real(eigenvals)
        eigenvals = np.maximum(eigenvals, 0)  # Ensure non-negative
        
        return np.sqrt(np.sum(np.sqrt(eigenvals)))**2