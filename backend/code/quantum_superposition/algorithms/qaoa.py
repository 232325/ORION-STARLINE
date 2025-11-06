"""
Quantum Approximate Optimization Algorithm (QAOA)
================================================

Portfolio optimizatsiya uchun QAOA algoritmi.
"""

import numpy as np
import cmath
from typing import List, Dict, Tuple, Optional, Union, Callable
from dataclasses import dataclass
from scipy.optimize import minimize, differential_evolution
from scipy.linalg import norm, eigh
import matplotlib.pyplot as plt

try:
    from ..core.quantum_state import QuantumPortfolioState, QuantumState
except ImportError:
    # Fallback for standalone execution
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from core.quantum_state import QuantumPortfolioState, QuantumState


@dataclass
class QAOAConfig:
    """QAOA konfiguratsiya parametrlari"""
    n_qubits: int = 4  # Qubit soni
    p_levels: int = 5  # QAOA p parameter
    max_iterations: int = 500  # Maksimal iterations
    tolerance: float = 1e-8  # Tolerance
    gamma_range: Tuple[float, float] = (0, 2*np.pi)  # Gamma parameter range
    beta_range: Tuple[float, float] = (0, np.pi)    # Beta parameter range
    optimization_method: str = 'COBYLA'  # Classical optimizer
    initial_parameters: np.ndarray = None  # Boshlang'ich parameters


class QuantumQAOA:
    """
    Quantum Approximate Optimization Algorithm for Portfolio Optimization
    
    Portfolio optimizatsiya uchun QAOA algoritmi implementation.
    """
    
    def __init__(self, config: QAOAConfig = None):
        self.config = config or QAOAConfig()
        
        # QAOA parameters
        self.gamma_parameters = None
        self.beta_parameters = None
        self.optimal_parameters = None
        
        # Problem Hamiltonian
        self.cost_hamiltonian = None
        self.mixer_hamiltonian = None
        
        # Optimization history
        self.parameter_history = []
        self.expectation_history = []
        self.measurement_history = []
        
        # Results
        self.optimization_results = {}
        
    def setup_portfolio_problem(self, portfolio: QuantumPortfolioState,
                              returns_data: np.ndarray,
                              covariance_matrix: np.ndarray = None) -> None:
        """
        Portfolio optimizatsiya muammosini QAOA uchun sozlash
        
        Args:
            portfolio: Portfolio quantum state
            returns_data: Returns ma'lumotlari
            covariance_matrix: Covariance matrix
        """
        # Set qubit count based on portfolio size
        n_assets = len(portfolio.assets)
        self.config.n_qubits = min(n_assets, max(2, self.config.n_qubits))
        
        # Construct problem Hamiltonian (cost function)
        self._construct_cost_hamiltonian(portfolio, returns_data, covariance_matrix)
        
        # Construct mixer Hamiltonian
        self._construct_mixer_hamiltonian()
        
        # Initialize parameters
        p = self.config.p_levels
        self.gamma_parameters = np.random.uniform(*self.config.gamma_range, p)
        self.beta_parameters = np.random.uniform(*self.config.beta_range, p)
        
        print(f"QAOA setup completed: {self.config.n_qubits} qubits, p={p} levels")
    
    def _construct_cost_hamiltonian(self, portfolio: QuantumPortfolioState,
                                  returns_data: np.ndarray,
                                  covariance_matrix: np.ndarray) -> None:
        """
        Cost Hamiltonian qurish
        
        Args:
            portfolio: Portfolio quantum state
            returns_data: Returns ma'lumotlari
            covariance_matrix: Covariance matrix
        """
        n_qubits = self.config.n_qubits
        n_states = 2**n_qubits
        
        # Initialize cost Hamiltonian
        cost_hamiltonian = np.zeros((n_states, n_states), dtype=complex)
        
        # Calculate portfolio metrics
        expected_return = portfolio.get_expected_return(returns_data)
        
        if covariance_matrix is not None:
            portfolio_risk = portfolio.get_risk(covariance_matrix)
        else:
            portfolio_risk = np.sqrt(np.sum(portfolio.get_portfolio_weights()**2 * 0.15**2))
        
        # Construct Hamiltonian for each basis state
        for state_idx in range(n_states):
            # Convert to binary representation
            binary_repr = format(state_idx, f'0{n_qubits}b')
            
            # Calculate portfolio weight for this state
            weights = self._binary_state_to_weights(binary_repr, len(portfolio.assets))
            
            # Cost function components
            return_cost = expected_return * np.sum(weights)
            risk_cost = self.config.risk_aversion * portfolio_risk * np.sum(weights**2)
            
            # Portfolio constraints penalty
            weight_sum_penalty = 10 * (np.sum(weights) - 1.0)**2
            individual_weight_penalty = 5 * np.sum(np.maximum(0, weights - 0.5))
            
            # Total cost
            total_cost = -(return_cost - risk_cost + weight_sum_penalty + individual_weight_penalty)
            cost_hamiltonian[state_idx, state_idx] = total_cost
        
        self.cost_hamiltonian = cost_hamiltonian
        print(f"Cost Hamiltonian constructed: {n_states}x{n_states}")
    
    def _construct_mixer_hamiltonian(self) -> None:
        """Mixer Hamiltonian qurish"""
        n_qubits = self.config.n_qubits
        n_states = 2**n_qubits
        
        # XY mixer Hamiltonian: H_M = Σᵢ (XᵢXᵢ₊₁ + YᵢYᵢ₊₁)
        mixer_hamiltonian = np.zeros((n_states, n_states), dtype=complex)
        
        for state_idx in range(n_states):
            binary_repr = format(state_idx, f'0{n_qubits}b')
            
            # Apply X_i X_{i+1} terms
            for i in range(n_qubits - 1):
                # Flip two adjacent bits
                new_state_idx = state_idx ^ ((1 << i) | (1 << (i + 1)))
                if new_state_idx < n_states:
                    mixer_hamiltonian[state_idx, new_state_idx] = 1.0
                    mixer_hamiltonian[new_state_idx, state_idx] = 1.0
        
        self.mixer_hamiltonian = mixer_hamiltonian
        print("Mixer Hamiltonian constructed")
    
    def _binary_state_to_weights(self, binary_repr: str, n_assets: int) -> np.ndarray:
        """Binary statedan portfolio weightlarni olish"""
        weights = np.zeros(n_assets)
        
        # Convert binary to weights
        for i, bit in enumerate(binary_repr):
            if i < n_assets:
                weights[i] = float(bit)
        
        # Normalize weights
        if np.sum(weights) > 0:
            weights = weights / np.sum(weights)
        
        return weights
    
    def _apply_qaoa_circuit(self, gamma_params: np.ndarray, beta_params: np.ndarray) -> np.ndarray:
        """
        QAOA circuit qo'llash
        
        Args:
            gamma_params: Cost Hamiltonian parameters
            beta_params: Mixer Hamiltonian parameters
        
        Returns:
            Final quantum state amplitudes
        """
        n_qubits = self.config.n_qubits
        n_states = 2**n_qubits
        
        # Initial state |+⟩^⊗n
        initial_state = np.ones(n_states) / np.sqrt(n_states)
        current_state = initial_state.copy()
        
        # Apply QAOA layers
        for p in range(self.config.p_levels):
            gamma = gamma_params[p]
            beta = beta_params[p]
            
            # Cost operator e^(-iγH_C)
            cost_unitary = self._time_evolution_operator(self.cost_hamiltonian, gamma)
            current_state = np.dot(cost_unitary, current_state)
            
            # Mixer operator e^(-iβH_M)
            mixer_unitary = self._time_evolution_operator(self.mixer_hamiltonian, beta)
            current_state = np.dot(mixer_unitary, current_state)
        
        return current_state
    
    def _time_evolution_operator(self, hamiltonian: np.ndarray, time: float) -> np.ndarray:
        """
        Time evolution operator: U = e^(-iHt)
        
        Args:
            hamiltonian: Hamiltonian matrix
            time: Evolution time
        
        Returns:
            Time evolution unitary operator
        """
        # Simple Trotterization for small matrices
        n_states = len(hamiltonian)
        dt = time / 10  # Small time step
        
        # Approximate using matrix exponential
        evolution_operator = np.eye(n_states, dtype=complex)
        
        # Split into small steps
        for _ in range(10):
            step_operator = np.eye(n_states) - 1j * dt * hamiltonian
            evolution_operator = np.dot(step_operator, evolution_operator)
        
        return evolution_operator
    
    def _evaluate_expectation_value(self, gamma_params: np.ndarray, beta_params: np.ndarray) -> float:
        """
        Expectation value hisoblash ⟨ψ(γ,β)|H_C|ψ(γ,β)⟩
        
        Args:
            gamma_params: Cost Hamiltonian parameters
            beta_params: Mixer Hamiltonian parameters
        
        Returns:
            Expectation value
        """
        # Apply QAOA circuit
        quantum_state = self._apply_qaoa_circuit(gamma_params, beta_params)
        
        # Calculate expectation value
        expectation = np.real(np.dot(
            np.conj(quantum_state),
            np.dot(self.cost_hamiltonian, quantum_state)
        ))
        
        return expectation
    
    def _measure_portfolio(self, quantum_state: np.ndarray) -> Dict:
        """
        Portfolio o'lchovi
        
        Args:
            quantum_state: Quantum state amplitudes
        
        Returns:
            Measurement result
        """
        n_qubits = self.config.n_qubits
        probabilities = np.abs(quantum_state)**2
        
        # Sample from probability distribution
        state_idx = np.random.choice(len(probabilities), p=probabilities)
        
        # Convert to binary
        binary_result = format(state_idx, f'0{n_qubits}b')
        
        # Calculate portfolio metrics
        portfolio_weights = self._binary_state_to_weights(binary_result, len(quantum_state))
        
        return {
            'state_index': state_idx,
            'binary_representation': binary_result,
            'portfolio_weights': portfolio_weights,
            'probability': probabilities[state_idx]
        }
    
    def optimize(self, callback: Callable = None) -> Dict:
        """
        QAOA optimization jarayoni
        
        Args:
            callback: Optimization callback function
        
        Returns:
            Optimization natijalari
        """
        print("Starting QAOA optimization...")
        
        # Combine parameters for optimization
        initial_params = np.concatenate([self.gamma_parameters, self.beta_parameters])
        
        def objective_function(combined_params):
            # Extract gamma and beta parameters
            p = self.config.p_levels
            gamma = combined_params[:p]
            beta = combined_params[p:]
            
            # Calculate expectation value
            expectation = self._evaluate_expectation_value(gamma, beta)
            
            # Record history
            self.expectation_history.append(expectation)
            self.parameter_history.append(combined_params.copy())
            
            if callback:
                callback(expectation, combined_params)
            
            return expectation
        
        # Parameter bounds
        p = self.config.p_levels
        bounds = ([self.config.gamma_range[0], self.config.gamma_range[1]] * p + 
                 [self.config.beta_range[0], self.config.beta_range[1]] * p)
        
        # Optimization
        result = minimize(
            objective_function,
            initial_params,
            method=self.config.optimization_method,
            bounds=bounds,
            options={
                'maxiter': self.config.max_iterations,
                'ftol': self.config.tolerance,
                'disp': True
            }
        )
        
        if result.success:
            # Extract optimal parameters
            p = self.config.p_levels
            self.optimal_parameters = result.x
            self.gamma_parameters = result.x[:p]
            self.beta_parameters = result.x[p:]
            
            # Get final quantum state
            final_state = self._apply_qaoa_circuit(self.gamma_parameters, self.beta_parameters)
            
            # Perform measurements
            measurement_results = []
            n_measurements = 100
            
            for _ in range(n_measurements):
                measurement = self._measure_portfolio(final_state)
                measurement_results.append(measurement)
            
            # Analyze measurements
            portfolio_weights = self._analyze_measurement_results(measurement_results)
            
            # Store results
            self.optimization_results = {
                'success': True,
                'optimal_energy': result.fun,
                'optimal_gamma': self.gamma_parameters.copy(),
                'optimal_beta': self.beta_parameters.copy(),
                'final_quantum_state': final_state,
                'portfolio_weights': portfolio_weights,
                'measurement_results': measurement_results,
                'optimization_details': result,
                'convergence_history': {
                    'expectation_values': self.expectation_history.copy(),
                    'parameters': [p.copy() for p in self.parameter_history]
                }
            }
            
            print(f"QAOA optimization completed!")
            print(f"Optimal energy: {result.fun:.6f}")
            print(f"Portfolio weights: {portfolio_weights}")
            
        else:
            print("QAOA optimization failed!")
            self.optimization_results = {
                'success': False,
                'error': 'Optimization did not converge',
                'optimization_details': result
            }
        
        return self.optimization_results
    
    def _analyze_measurement_results(self, measurement_results: List[Dict]) -> np.ndarray:
        """Measurement natijalarini tahlil qilish"""
        # Collect all portfolio weights
        all_weights = [result['portfolio_weights'] for result in measurement_results]
        
        # Average weights
        avg_weights = np.mean(all_weights, axis=0)
        
        # Weight with highest probability
        probabilities = [result['probability'] for result in measurement_results]
        max_prob_idx = np.argmax(probabilities)
        best_weights = measurement_results[max_prob_idx]['portfolio_weights']
        
        return {
            'average_weights': avg_weights,
            'best_weights': best_weights,
            'best_probability': probabilities[max_prob_idx],
            'measurement_entropy': -np.sum(p * np.log(p + 1e-10) for p in probabilities)
        }
    
    def get_qaoa_circuit_info(self) -> Dict:
        """
        QAOA circuit ma'lumotlari
        
        Returns:
            Circuit information
        """
        return {
            'n_qubits': self.config.n_qubits,
            'p_levels': self.config.p_levels,
            'total_parameters': len(self.gamma_parameters) + len(self.beta_parameters),
            'gamma_parameters': self.gamma_parameters.copy() if self.gamma_parameters is not None else None,
            'beta_parameters': self.beta_parameters.copy() if self.beta_parameters is not None else None,
            'optimal_parameters': self.optimal_parameters.copy() if self.optimal_parameters is not None else None
        }
    
    def analyze_approximation_ratio(self, classical_optimal: float = None) -> Dict:
        """
        Approximation ratio tahlili
        
        Args:
            classical_optimal: Classical optimal energy
        
        Returns:
            Approximation analysis
        """
        if not self.optimization_results.get('success'):
            return {'error': 'QAOA optimization successful emas'}
        
        qaoa_energy = self.optimization_results['optimal_energy']
        
        # Find best measurement result
        measurement_results = self.optimization_results['measurement_results']
        portfolio_weights = self.optimization_results['portfolio_weights']
        
        # Estimate classical optimal if not provided
        if classical_optimal is None:
            # Use best measurement energy as approximation
            classical_optimal = self._calculate_classical_baseline(portfolio_weights)
        
        # Calculate approximation ratio
        approximation_ratio = qaoa_energy / classical_optimal if classical_optimal != 0 else 0
        
        # Quantum advantage assessment
        has_advantage = approximation_ratio > 0.95  # Within 5% of classical optimum
        
        # Performance metrics
        measurement_energies = []
        for measurement in measurement_results:
            weights = measurement['portfolio_weights']
            energy = self._evaluate_weights_energy(weights)
            measurement_energies.append(energy)
        
        best_measurement_energy = min(measurement_energies)
        avg_measurement_energy = np.mean(measurement_energies)
        
        return {
            'qaoa_energy': qaoa_energy,
            'classical_optimal': classical_optimal,
            'approximation_ratio': approximation_ratio,
            'best_measurement_energy': best_measurement_energy,
            'avg_measurement_energy': avg_measurement_energy,
            'measurement_variance': np.var(measurement_energies),
            'has_quantum_advantage': has_advantage,
            'performance_assessment': 'good' if approximation_ratio > 0.9 else 'needs_improvement'
        }
    
    def _calculate_classical_baseline(self, portfolio_weights: Dict) -> float:
        """Classical baseline hisoblash"""
        if isinstance(portfolio_weights, dict):
            weights = portfolio_weights.get('best_weights', np.array([0.25, 0.25, 0.25, 0.25]))
        else:
            weights = portfolio_weights
        
        # Simplified classical optimization baseline
        # In practice, would use actual classical optimization
        baseline_energy = -np.sum(weights**2) + np.sum(weights) * 0.1
        return baseline_energy
    
    def _evaluate_weights_energy(self, weights: np.ndarray) -> float:
        """Portfolio weightlarining energy hisoblash"""
        # Simplified energy evaluation
        return -np.sum(weights**2) + 0.1 * np.sum(weights)
    
    def qaoa_depth_analysis(self) -> Dict:
        """
        QAOA depth tahlili
        
        Returns:
            Depth analysis
        """
        p_levels = self.config.p_levels
        
        # Circuit depth estimation
        cost_depth = p_levels  # One cost evolution per layer
        mixer_depth = p_levels  # One mixer evolution per layer
        
        # Total circuit operations
        total_gates = p_levels * 2  # Cost + mixer per layer
        
        # Parameter efficiency
        parameter_efficiency = total_gates / self.config.n_qubits
        
        return {
            'p_levels': p_levels,
            'cost_depth': cost_depth,
            'mixer_depth': mixer_depth,
            'total_depth': cost_depth + mixer_depth,
            'total_gates': total_gates,
            'parameter_efficiency': parameter_efficiency,
            'circuit_complexity': total_gates / (2**self.config.n_qubits)
        }
    
    def variational_landscape_analysis(self) -> Dict:
        """
        Variational landscape tahlili
        
        Returns:
            Landscape analysis
        """
        if not self.expectation_history:
            return {'error': 'Optimization history mavjud emas'}
        
        energies = np.array(self.expectation_history)
        
        # Landscape statistics
        min_energy = np.min(energies)
        max_energy = np.max(energies)
        energy_range = max_energy - min_energy
        
        # Optimization trajectory
        if len(energies) > 1:
            energy_gradients = np.diff(energies)
            avg_gradient = np.mean(np.abs(energy_gradients))
            gradient_variance = np.var(energy_gradients)
        else:
            avg_gradient = 0
            gradient_variance = 0
        
        # Check for local minima
        local_minima = []
        for i in range(1, len(energies) - 1):
            if energies[i] < energies[i-1] and energies[i] < energies[i+1]:
                local_minima.append(energies[i])
        
        return {
            'energy_statistics': {
                'min_energy': min_energy,
                'max_energy': max_energy,
                'energy_range': energy_range,
                'final_energy': energies[-1]
            },
            'optimization_trajectory': {
                'avg_gradient_magnitude': avg_gradient,
                'gradient_variance': gradient_variance,
                'convergence_rate': 1 / avg_gradient if avg_gradient > 0 else float('inf')
            },
            'landscape_features': {
                'n_local_minima': len(local_minima),
                'local_minima_energies': local_minima,
                'landscape_roughness': gradient_variance / energy_range if energy_range > 0 else 0
            }
        }