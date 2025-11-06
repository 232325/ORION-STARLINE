"""
Quantum Algorithms Implementation - Quantum portfolio optimization
VQE, QAOA, Quantum Monte Carlo, va quantum machine learning integration
"""

import numpy as np
import cmath
from typing import Dict, List, Tuple, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from scipy.optimize import minimize, differential_evolution
from scipy.linalg import expm
from abc import ABC, abstractmethod
import warnings

from quantum_superposition_theory import QuantumState
from superposition_portfolio_models import SuperpositionPortfolio

@dataclass
class QuantumCircuit:
    """Quantum circuit representation for portfolio optimization"""
    num_qubits: int
    num_layers: int = 3
    parameters: np.ndarray = field(default=None)
    
    def __post_init__(self):
        if self.parameters is None:
            # Initialize random circuit parameters
            self.parameters = np.random.uniform(0, 2*np.pi, 
                                               (self.num_layers, self.num_qubits))
    
    def apply_hadamard_layer(self, state: np.ndarray) -> np.ndarray:
        """Apply Hadamard gates for superposition"""
        hadamard = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        
        for qubit in range(self.num_qubits):
            # Apply Hadamard gate to each qubit
            state = self.apply_single_qubit_gate(state, hadamard, qubit)
        
        return state
    
    def apply_rotation_layer(self, state: np.ndarray, layer_idx: int) -> np.ndarray:
        """Apply parameterized rotation gates"""
        for qubit in range(self.num_qubits):
            angle = self.parameters[layer_idx, qubit]
            
            # Rx rotation gate
            rx_gate = np.array([
                [np.cos(angle/2), -1j*np.sin(angle/2)],
                [-1j*np.sin(angle/2), np.cos(angle/2)]
            ])
            
            state = self.apply_single_qubit_gate(state, rx_gate, qubit)
        
        return state
    
    def apply_entanglement_layer(self, state: np.ndarray) -> np.ndarray:
        """Apply entanglement gates between qubits"""
        # CNOT gates for entanglement
        for qubit in range(self.num_qubits - 1):
            state = self.apply_cnot_gate(state, qubit, qubit + 1)
        
        return state
    
    def apply_single_qubit_gate(self, state: np.ndarray, gate: np.ndarray, qubit: int) -> np.ndarray:
        """Apply single qubit gate to quantum state"""
        num_states = 2 ** self.num_qubits
        new_state = np.zeros(num_states, dtype=complex)
        
        for i in range(num_states):
            if (i >> qubit) & 1:  # Check if qubit is in |1⟩ state
                # Apply gate to |1⟩ component
                bit_flip = i ^ (1 << qubit)
                new_state[i] += gate[1, 0] * state[bit_flip]
                new_state[i] += gate[1, 1] * state[i]
            else:
                # Apply gate to |0⟩ component
                new_state[i] += gate[0, 0] * state[i]
                if i + (1 << qubit) < num_states:
                    new_state[i + (1 << qubit)] += gate[0, 1] * state[i]
        
        return new_state
    
    def apply_cnot_gate(self, state: np.ndarray, control: int, target: int) -> np.ndarray:
        """Apply CNOT gate"""
        num_states = 2 ** self.num_qubits
        new_state = np.zeros(num_states, dtype=complex)
        
        for i in range(num_states):
            if (i >> control) & 1:  # Control qubit is |1⟩
                # Flip target qubit
                flipped_i = i ^ (1 << target)
                new_state[flipped_i] = state[i]
            else:
                new_state[i] = state[i]
        
        return new_state
    
    def measure_expectation(self, state: np.ndarray, observable: np.ndarray) -> float:
        """Measure expectation value of observable"""
        # Calculate <ψ|O|ψ>
        expectation = np.conj(state) @ observable @ state
        return np.real(expectation)

class VQEAlgorithm:
    """Base class for Variational Quantum Eigensolver"""
    
    def __init__(self, portfolio: SuperpositionPortfolio, hamiltonian: np.ndarray):
        self.portfolio = portfolio
        self.hamiltonian = hamiltonian
    
    def cost_function(self, parameters: np.ndarray) -> float:
        """Base cost function to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement cost_function")
    
    def optimize(self, **kwargs) -> Tuple[np.ndarray, float]:
        """Base optimization method to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement optimize")

class VariationalQuantumEigensolver(VQEAlgorithm):
    """Variational Quantum Eigensolver for portfolio optimization"""
    
    def __init__(self, portfolio: SuperpositionPortfolio, hamiltonian: np.ndarray):
        super().__init__(portfolio, hamiltonian)
        self.circuit = QuantumCircuit(num_qubits=len(portfolio.assets))
        self.energy_history: List[float] = []
        self.parameter_history: List[np.ndarray] = []
    
    def prepare_hamiltonian(self, 
                          expected_returns: np.ndarray,
                          covariance_matrix: np.ndarray,
                          risk_aversion: float = 1.0) -> np.ndarray:
        """Prepare portfolio Hamiltonian"""
        n_assets = len(expected_returns)
        
        # Expected return term
        return_term = np.diag(expected_returns)
        
        # Risk term (quadratic in weights)
        risk_term = risk_aversion * covariance_matrix
        
        # Total Hamiltonian H = return_term - risk_term
        hamiltonian = return_term - risk_term
        
        # Convert to Pauli operators basis (simplified)
        pauli_hamiltonian = np.zeros((2**n_assets, 2**n_assets), dtype=complex)
        
        # Mapping from weights to quantum states
        for i in range(2**n_assets):
            # Classical weight from binary representation
            weights = np.array([(i >> j) & 1 for j in range(n_assets)], dtype=float)
            weights = weights / np.sum(weights) if np.sum(weights) > 0 else weights
            
            # Diagonal element
            hamiltonian_value = np.dot(weights, np.dot(hamiltonian, weights))
            pauli_hamiltonian[i, i] = hamiltonian_value
        
        return pauli_hamiltonian
    
    def ansatz_circuit(self, parameters: np.ndarray) -> np.ndarray:
        """Variational ansatz circuit"""
        # Initialize |0⟩ state
        num_states = 2 ** self.circuit.num_qubits
        state = np.zeros(num_states, dtype=complex)
        state[0] = 1.0  # |0...0⟩ state
        
        # Layer 1: Hadamard for superposition
        state = self.circuit.apply_hadamard_layer(state)
        
        # Variational layers
        for layer in range(self.circuit.num_layers):
            # Rotation layer
            layer_params = parameters[layer] if layer < len(parameters) else self.circuit.parameters[layer]
            state = self.circuit.apply_rotation_layer(state, layer)
            
            # Entanglement layer
            state = self.circuit.apply_entanglement_layer(state)
        
        return state
    
    def cost_function(self, parameters: np.ndarray) -> float:
        """Variational cost function"""
        # Ensure correct parameter shape
        if parameters.shape != self.circuit.parameters.shape:
            parameters = parameters.reshape(self.circuit.parameters.shape)
        
        # Update circuit parameters
        self.circuit.parameters = parameters
        
        # Prepare quantum state
        quantum_state = self.ansatz_circuit(parameters)
        
        # Calculate expectation value
        energy = self.circuit.measure_expectation(quantum_state, self.hamiltonian)
        
        # Record history
        self.energy_history.append(energy)
        self.parameter_history.append(parameters.copy())
        
        return energy
    
    def optimize(self, 
                max_iterations: int = 100,
                tolerance: float = 1e-6) -> Tuple[np.ndarray, float]:
        """Optimize using classical optimizer"""
        # Flatten parameters for optimizer
        initial_params = self.circuit.parameters.flatten()
        
        # Optimization
        result = minimize(
            self.cost_function,
            initial_params,
            method='L-BFGS-B',
            options={'maxiter': max_iterations, 'ftol': tolerance}
        )
        
        if result.success:
            # Reshape optimized parameters
            optimized_params = result.x.reshape(self.circuit.parameters.shape)
            min_energy = result.fun
            
            # Update circuit with optimized parameters
            self.circuit.parameters = optimized_params
            
            return optimized_params, min_energy
        else:
            raise RuntimeError(f"VQE optimization failed: {result.message}")
    
    def get_optimal_weights(self, optimized_params: np.ndarray) -> Dict[str, float]:
        """Extract optimal portfolio weights from quantum result"""
        # Prepare optimal quantum state
        optimal_state = self.ansatz_circuit(optimized_params)
        
        # Measure probabilities
        probabilities = np.abs(optimal_state) ** 2
        
        # Map quantum states to portfolio weights
        weights = {}
        for i, (asset_id, _) in enumerate(self.portfolio.assets.items()):
            if i < len(probabilities):
                # Classical interpretation of quantum result
                weight = probabilities[i] if i < len(probabilities) else 0.0
                weights[asset_id] = weight
        
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v/total_weight for k, v in weights.items()}
        
        return weights

class QAOAAlgorithm:
    """Quantum Approximate Optimization Algorithm for portfolio selection"""
    
    def __init__(self, portfolio: SuperpositionPortfolio, problem_hamiltonian: np.ndarray):
        self.portfolio = portfolio
        self.problem_hamiltonian = problem_hamiltonian
        self.num_qubits = len(portfolio.assets)
        self.mixer_hamiltonian = self.create_mixer_hamiltonian()
        self.optimization_history: List[Dict] = []
    
    def create_mixer_hamiltonian(self) -> np.ndarray:
        """Create mixer Hamiltonian for QAOA"""
        mixer = np.zeros((2**self.num_qubits, 2**self.num_qubits))
        
        # X mixer (sum of Pauli-X operators)
        for i in range(2**self.num_qubits):
            for qubit in range(self.num_qubits):
                # Bit flip operation
                flipped_state = i ^ (1 << qubit)
                mixer[flipped_state, i] += 1.0
        
        return mixer
    
    def qaoa_circuit(self, parameters: np.ndarray) -> np.ndarray:
        """QAOA circuit evolution"""
        # Initial state |+⟩^⊗n
        num_states = 2 ** self.num_qubits
        state = np.ones(num_states) / np.sqrt(num_states)
        
        # QAOA layers
        gamma_params = parameters[:self.num_qubits]  # Problem parameters
        beta_params = parameters[self.num_qubits:2*self.num_qubits]  # Mixer parameters
        
        for i in range(len(gamma_params)):
            # Problem evolution
            problem_unitary = expm(-1j * gamma_params[i] * self.problem_hamiltonian)
            state = problem_unitary @ state
            
            # Mixer evolution
            mixer_unitary = expm(-1j * beta_params[i] * self.mixer_hamiltonian)
            state = mixer_unitary @ state
        
        return state
    
    def qaoa_cost_function(self, parameters: np.ndarray) -> float:
        """QAOA cost function"""
        if len(parameters) != 2 * self.num_qubits:
            raise ValueError("Parameters must have length 2 * num_qubits")
        
        # Prepare quantum state
        quantum_state = self.qaoa_circuit(parameters)
        
        # Calculate expectation value
        cost = np.real(np.conj(quantum_state) @ self.problem_hamiltonian @ quantum_state)
        
        # Record optimization
        self.optimization_history.append({
            'parameters': parameters.copy(),
            'cost': cost,
            'iteration': len(self.optimization_history)
        })
        
        return cost
    
    def optimize_qaoa(self, max_iterations: int = 200) -> Tuple[np.ndarray, float]:
        """Optimize QAOA parameters"""
        # Random initial parameters
        initial_params = np.random.uniform(0, 2*np.pi, 2 * self.num_qubits)
        
        # Optimize using differential evolution for global optimization
        result = differential_evolution(
            self.qaoa_cost_function,
            bounds=[(0, 2*np.pi)] * (2 * self.num_qubits),
            maxiter=max_iterations,
            popsize=15
        )
        
        if result.success:
            return result.x, result.fun
        else:
            raise RuntimeError(f"QAOA optimization failed: {result.message}")
    
    def get_qaoa_solution(self, optimal_params: np.ndarray) -> Dict[str, float]:
        """Get portfolio selection from QAOA solution"""
        # Prepare optimal quantum state
        optimal_state = self.qaoa_circuit(optimal_params)
        
        # Find best classical solution by measurement
        probabilities = np.abs(optimal_state) ** 2
        best_state_idx = np.argmax(probabilities)
        
        # Convert to portfolio weights
        weights = {}
        for i, (asset_id, _) in enumerate(self.portfolio.assets.items()):
            # Binary representation gives selection
            is_selected = (best_state_idx >> i) & 1
            weight = 1.0 if is_selected else 0.0
            weights[asset_id] = weight
        
        # Normalize to get weights
        total_selected = sum(weights.values())
        if total_selected > 0:
            weights = {k: v/total_selected for k, v in weights.items()}
        else:
            # Equal weights if nothing selected
            equal_weight = 1.0 / len(self.portfolio.assets)
            weights = {k: equal_weight for k in self.portfolio.assets.keys()}
        
        return weights

class QuantumMonteCarlo:
    """Quantum Monte Carlo methods for portfolio analysis"""
    
    def __init__(self, portfolio: SuperpositionPortfolio):
        self.portfolio = portfolio
        self.paths: List[Dict] = []
        self.convergence_history: List[float] = []
    
    def quantum_walk_simulation(self, 
                              num_steps: int = 1000,
                              num_paths: int = 1000) -> Dict[str, Any]:
        """Simulate quantum walks for portfolio paths"""
        quantum_paths = []
        
        for path_idx in range(num_paths):
            # Initialize quantum state
            current_state = np.array(list(self.portfolio.assets.values()))
            current_state = current_state / np.sum(current_state)  # Normalize
            
            path = {
                'weights': [current_state.copy()],
                'returns': [0.0],
                'quantum_phases': [np.random.uniform(0, 2*np.pi)]
            }
            
            for step in range(num_steps):
                # Quantum walk step
                next_state = self.quantum_walk_step(current_state)
                
                # Calculate return
                total_weight = np.sum(next_state)
                if total_weight > 0:
                    next_state = next_state / total_weight
                    
                    # Portfolio return calculation
                    asset_returns = np.random.normal(0.0001, 0.02, len(next_state))
                    portfolio_return = np.dot(next_state, asset_returns)
                    
                    # Quantum phase evolution
                    quantum_phase = path['quantum_phases'][-1] + portfolio_return * np.pi
                    
                    path['weights'].append(next_state.copy())
                    path['returns'].append(portfolio_return)
                    path['quantum_phases'].append(quantum_phase)
                    
                    current_state = next_state
            
            quantum_paths.append(path)
        
        self.paths = quantum_paths
        
        # Calculate statistics
        returns = [path['returns'][-1] for path in quantum_paths]
        
        statistics = {
            'mean_return': np.mean(returns),
            'volatility': np.std(returns),
            'sharpe_ratio': np.mean(returns) / (np.std(returns) + 1e-15),
            'max_return': np.max(returns),
            'min_return': np.min(returns),
            'var_95': np.percentile(returns, 5),
            'num_paths': len(quantum_paths),
            'path_length': num_steps
        }
        
        return statistics
    
    def quantum_walk_step(self, current_weights: np.ndarray) -> np.ndarray:
        """Single quantum walk step"""
        # Quantum coin operator
        coin_operators = []
        for i in range(len(current_weights)):
            angle = current_weights[i] * np.pi
            coin_op = np.array([
                [np.cos(angle), np.sin(angle)],
                [np.sin(angle), -np.cos(angle)]
            ])
            coin_operators.append(coin_op)
        
        # Apply coin and shift
        new_weights = np.zeros_like(current_weights)
        
        for i, weight in enumerate(current_weights):
            # Coin flip
            new_value = coin_operators[i][0, 0] * weight + coin_operators[i][0, 1] * weight
            
            # Shift to adjacent position (cyclic)
            new_index = (i + 1) % len(current_weights)
            new_weights[new_index] += new_value
        
        # Add quantum noise
        quantum_noise = np.random.normal(0, 0.001, len(current_weights))
        new_weights += quantum_noise
        
        # Ensure non-negative
        new_weights = np.maximum(new_weights, 0)
        
        return new_weights
    
    def quantum_monte_carlo_integration(self, 
                                      num_samples: int = 10000) -> Dict[str, float]:
        """Quantum Monte Carlo integration for portfolio metrics"""
        samples = []
        
        for _ in range(num_samples):
            # Sample quantum state
            quantum_state = self.sample_quantum_portfolio()
            
            # Calculate portfolio metrics
            metrics = self.calculate_portfolio_metrics(quantum_state)
            samples.append(metrics)
        
        # Calculate statistics
        results = {}
        for metric in samples[0].keys():
            values = [sample[metric] for sample in samples]
            results[f'{metric}_mean'] = np.mean(values)
            results[f'{metric}_std'] = np.std(values)
            results[f'{metric}_var'] = np.var(values)
        
        return results
    
    def sample_quantum_portfolio(self) -> Dict[str, float]:
        """Sample portfolio weights from quantum distribution"""
        # Quantum amplitude-based sampling
        total_weight = sum(self.portfolio.assets.values())
        
        sampled_weights = {}
        remaining_weight = 1.0
        
        for i, (asset_id, original_weight) in enumerate(self.portfolio.assets.items()):
            # Quantum probability
            quantum_prob = abs(self.portfolio.quantum_states[asset_id].amplitude) ** 2
            
            # Sample weight
            if i == len(self.portfolio.assets) - 1:
                # Last asset gets remaining weight
                sampled_weights[asset_id] = remaining_weight
            else:
                # Sample based on quantum probability
                max_weight = min(original_weight / total_weight, remaining_weight)
                sampled_weight = min(quantum_prob * remaining_weight, max_weight)
                sampled_weights[asset_id] = sampled_weight
                remaining_weight -= sampled_weight
        
        # Normalize
        total_sampled = sum(sampled_weights.values())
        if total_sampled > 0:
            sampled_weights = {k: v/total_sampled for k, v in sampled_weights.items()}
        
        return sampled_weights
    
    def calculate_portfolio_metrics(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Calculate portfolio metrics for sampled weights"""
        # Simplified metrics calculation
        weights_array = np.array(list(weights.values()))
        
        # Expected return (simplified)
        expected_returns = np.array([0.1, 0.08, 0.12, 0.15, 0.06][:len(weights)])
        expected_return = np.dot(weights_array, expected_returns[:len(weights)])
        
        # Risk (simplified)
        covariance_matrix = np.eye(len(weights)) * 0.02
        risk = np.sqrt(np.dot(weights_array, np.dot(covariance_matrix, weights_array)))
        
        # Sharpe ratio
        risk_free_rate = 0.02
        sharpe_ratio = (expected_return - risk_free_rate) / (risk + 1e-15)
        
        # Concentration (Herfindahl index)
        concentration = np.sum(weights_array ** 2)
        
        return {
            'expected_return': expected_return,
            'risk': risk,
            'sharpe_ratio': sharpe_ratio,
            'concentration': concentration
        }

class QuantumOptimizer:
    """Main quantum optimizer combining multiple algorithms"""
    
    def __init__(self, portfolio: SuperpositionPortfolio):
        self.portfolio = portfolio
        self.vqe: Optional[VariationalQuantumEigensolver] = None
        self.qaoa: Optional[QAOAAlgorithm] = None
        self.qmc: Optional[QuantumMonteCarlo] = None
        self.optimization_results: Dict[str, Any] = {}
    
    def prepare_portfolio_problem(self, 
                                expected_returns: np.ndarray,
                                covariance_matrix: np.ndarray,
                                risk_aversion: float = 1.0) -> np.ndarray:
        """Prepare portfolio optimization problem Hamiltonian"""
        n_assets = len(expected_returns)
        
        # Portfolio Hamiltonian H = μ^T w - (λ/2) w^T Σ w
        portfolio_hamiltonian = np.zeros((2**n_assets, 2**n_assets))
        
        for i in range(2**n_assets):
            # Convert binary to weights
            weights = np.array([(i >> j) & 1 for j in range(n_assets)], dtype=float)
            
            if np.sum(weights) > 0:
                weights = weights / np.sum(weights)  # Normalize
                
                # Expected return
                return_term = np.dot(weights, expected_returns)
                
                # Risk penalty
                risk_term = (risk_aversion / 2) * np.dot(weights, np.dot(covariance_matrix, weights))
                
                # Total value
                hamiltonian_value = return_term - risk_term
                portfolio_hamiltonian[i, i] = hamiltonian_value
        
        return portfolio_hamiltonian
    
    def optimize_portfolio(self, 
                         expected_returns: np.ndarray,
                         covariance_matrix: np.ndarray,
                         risk_aversion: float = 1.0,
                         methods: List[str] = ['vqe', 'qaoa']) -> Dict[str, Any]:
        """Optimize portfolio using multiple quantum methods"""
        
        results = {}
        
        # Prepare problem
        problem_hamiltonian = self.prepare_portfolio_problem(
            expected_returns, covariance_matrix, risk_aversion
        )
        
        for method in methods:
            print(f"Optimizing with {method.upper()}...")
            
            if method.lower() == 'vqe':
                # Variational Quantum Eigensolver
                self.vqe = VariationalQuantumEigensolver(self.portfolio, problem_hamiltonian)
                optimal_params, min_energy = self.vqe.optimize(max_iterations=50)
                optimal_weights = self.vqe.get_optimal_weights(optimal_params)
                
                results['vqe'] = {
                    'optimal_weights': optimal_weights,
                    'min_energy': min_energy,
                    'energy_history': self.vqe.energy_history,
                    'parameters': optimal_params
                }
            
            elif method.lower() == 'qaoa':
                # Quantum Approximate Optimization Algorithm
                self.qaoa = QAOAAlgorithm(self.portfolio, problem_hamiltonian)
                optimal_params, min_cost = self.qaoa.optimize_qaoa(max_iterations=100)
                qaoa_weights = self.qaoa.get_qaoa_solution(optimal_params)
                
                results['qaoa'] = {
                    'optimal_weights': qaoa_weights,
                    'min_cost': min_cost,
                    'optimization_history': self.qaoa.optimization_history,
                    'parameters': optimal_params
                }
            
            elif method.lower() == 'qmc':
                # Quantum Monte Carlo
                self.qmc = QuantumMonteCarlo(self.portfolio)
                qmc_statistics = self.qmc.quantum_walk_simulation(num_steps=500, num_paths=500)
                qmc_integration = self.qmc.quantum_monte_carlo_integration(num_samples=5000)
                
                results['qmc'] = {
                    'walk_statistics': qmc_statistics,
                    'integration_results': qmc_integration
                }
        
        self.optimization_results = results
        return results
    
    def compare_methods(self) -> Dict[str, Dict[str, float]]:
        """Compare results from different quantum methods"""
        if not self.optimization_results:
            return {}
        
        comparison = {}
        
        for method, results in self.optimization_results.items():
            if 'optimal_weights' in results:
                weights = results['optimal_weights']
                
                # Calculate performance metrics
                expected_returns = np.array([0.1, 0.08, 0.12, 0.15, 0.06][:len(weights)])
                weights_array = np.array(list(weights.values()))
                
                exp_return = np.dot(weights_array, expected_returns)
                volatility = np.sqrt(np.dot(weights_array, np.dot(np.eye(len(weights)) * 0.02, weights_array)))
                sharpe = (exp_return - 0.02) / (volatility + 1e-15)
                
                comparison[method] = {
                    'expected_return': exp_return,
                    'volatility': volatility,
                    'sharpe_ratio': sharpe,
                    'concentration': np.sum(weights_array ** 2)
                }
        
        return comparison
    
    def get_ensemble_weights(self, method_weights: Dict[str, float] = None) -> Dict[str, float]:
        """Get ensemble weights combining multiple methods"""
        if method_weights is None:
            method_weights = {method: 1.0 for method in self.optimization_results.keys()}
        
        # Normalize method weights
        total_method_weight = sum(method_weights.values())
        if total_method_weight > 0:
            method_weights = {k: v/total_method_weight for k, v in method_weights.items()}
        
        # Combine weights from different methods
        ensemble_weights = {}
        asset_list = list(self.portfolio.assets.keys())
        
        for asset_id in asset_list:
            total_weight = 0
            
            for method, results in self.optimization_results.items():
                if 'optimal_weights' in results and asset_id in results['optimal_weights']:
                    weight = results['optimal_weights'][asset_id]
                    method_contribution = method_weights.get(method, 0)
                    total_weight += weight * method_contribution
            
            ensemble_weights[asset_id] = total_weight
        
        # Normalize ensemble weights
        total_ensemble = sum(ensemble_weights.values())
        if total_ensemble > 0:
            ensemble_weights = {k: v/total_ensemble for k, v in ensemble_weights.items()}
        
        return ensemble_weights

class QuantumMachineLearning:
    """Quantum machine learning integration for portfolio prediction"""
    
    def __init__(self, portfolio: SuperpositionPortfolio):
        self.portfolio = portfolio
        self.quantum_features: Dict[str, np.ndarray] = {}
        self.prediction_history: List[Dict] = []
    
    def extract_quantum_features(self, 
                               market_data: Dict[str, List[float]],
                               lookback_window: int = 20) -> Dict[str, np.ndarray]:
        """Extract quantum features from market data"""
        quantum_features = {}
        
        for asset_id, price_series in market_data.items():
            if len(price_series) >= lookback_window:
                # Classical features
                returns = np.diff(price_series) / price_series[:-1]
                rolling_mean = np.convolve(returns, np.ones(5)/5, mode='valid')
                rolling_std = np.array([np.std(returns[max(0, i-4):i+1]) 
                                      for i in range(4, len(returns))])
                
                # Quantum features
                quantum_phases = np.angle(returns + 1j * 0.01)  # Add small imaginary part
                quantum_amplitudes = np.abs(returns + 1j * 0.01)
                
                # Combine features
                features = np.column_stack([
                    returns[-lookback_window:],
                    quantum_phases[-lookback_window:],
                    quantum_amplitudes[-lookback_window:],
                    rolling_mean[-lookback_window:] if len(rolling_mean) >= lookback_window else np.zeros(lookback_window),
                    rolling_std[-lookback_window:] if len(rolling_std) >= lookback_window else np.ones(lookback_window) * 0.02
                ])
                
                quantum_features[asset_id] = features
        
        self.quantum_features = quantum_features
        return quantum_features
    
    def quantum_feature_selection(self, 
                                target_returns: Dict[str, float],
                                num_features: int = 5) -> Dict[str, List[int]]:
        """Select most relevant quantum features using quantum importance"""
        selected_features = {}
        
        for asset_id, features in self.quantum_features.items():
            if asset_id in target_returns:
                target = target_returns[asset_id]
                
                # Quantum feature importance calculation
                feature_importance = []
                
                for feature_idx in range(features.shape[1]):
                    # Quantum correlation measure
                    feature_values = features[:, feature_idx]
                    
                    # Add quantum phase and amplitude
                    quantum_phase = np.angle(feature_values + 1j * 0.01)
                    quantum_amplitude = np.abs(feature_values + 1j * 0.01)
                    
                    # Combined quantum correlation
                    classical_corr = np.corrcoef(feature_values, np.full(len(feature_values), target))[0, 1]
                    quantum_corr = np.mean(np.cos(quantum_phase - np.angle(target + 1j * 0.01)))
                    
                    importance = 0.7 * abs(classical_corr if not np.isnan(classical_corr) else 0) + \
                               0.3 * abs(quantum_corr)
                    
                    feature_importance.append(importance)
                
                # Select top features
                top_indices = np.argsort(feature_importance)[-num_features:]
                selected_features[asset_id] = top_indices.tolist()
        
        return selected_features
    
    def quantum_regression_prediction(self, 
                                    features: np.ndarray,
                                    target: np.ndarray,
                                    quantum_regularization: float = 0.1) -> Dict[str, Any]:
        """Quantum regularized regression for prediction"""
        # Classical linear regression
        X = features
        y = target
        
        # Add quantum regularization
        n_features = X.shape[1]
        quantum_identity = np.eye(n_features)
        quantum_phases = np.exp(1j * np.random.uniform(0, 2*np.pi, n_features))
        
        # Quantum regularized solution: (X^T X + λI + quantum_term)^-1 X^T y
        classical_term = X.T @ X
        quantum_term = np.outer(quantum_phases, np.conj(quantum_phases))
        
        regularized_matrix = classical_term + quantum_regularization * quantum_identity + \
                           0.1 * quantum_term
        
        try:
            weights = np.linalg.solve(regularized_matrix, X.T @ y)
            predictions = X @ weights
            
            # Calculate metrics
            mse = np.mean((predictions - y) ** 2)
            r_squared = 1 - np.sum((y - predictions) ** 2) / np.sum((y - np.mean(y)) ** 2)
            
            return {
                'weights': weights,
                'predictions': predictions,
                'mse': mse,
                'r_squared': r_squared,
                'quantum_phases': quantum_phases
            }
        except np.linalg.LinAlgError:
            # Fallback to simple least squares
            weights = np.linalg.lstsq(X, y, rcond=None)[0]
            predictions = X @ weights
            mse = np.mean((predictions - y) ** 2)
            
            return {
                'weights': weights,
                'predictions': predictions,
                'mse': mse,
                'r_squared': 0.0,
                'quantum_phases': quantum_phases
            }

def demonstrate_quantum_algorithms():
    """Demonstrate quantum algorithms for portfolio optimization"""
    print("=== Quantum Algorithms Demo ===")
    
    # Create sample portfolio
    assets = {
        'AAPL': 0.25,
        'GOOGL': 0.20,
        'MSFT': 0.15,
        'TSLA': 0.25,
        'AMZN': 0.15
    }
    
    portfolio = SuperpositionPortfolio(assets)
    
    # Expected returns and covariance
    expected_returns = np.array([0.1, 0.08, 0.12, 0.15, 0.06])
    covariance_matrix = np.eye(5) * 0.02
    covariance_matrix[0, 1] = covariance_matrix[1, 0] = 0.01  # Add some correlation
    covariance_matrix[2, 3] = covariance_matrix[3, 2] = 0.015
    
    # Initialize quantum optimizer
    optimizer = QuantumOptimizer(portfolio)
    
    # Optimize with multiple methods
    results = optimizer.optimize_portfolio(
        expected_returns=expected_returns,
        covariance_matrix=covariance_matrix,
        risk_aversion=2.0,
        methods=['vqe', 'qaoa']
    )
    
    # Display results
    print("\nOptimization Results:")
    for method, result in results.items():
        if 'optimal_weights' in result:
            print(f"\n{method.upper()} Optimal Weights:")
            for asset_id, weight in result['optimal_weights'].items():
                print(f"  {asset_id}: {weight:.4f}")
            
            if 'min_energy' in result:
                print(f"  Minimum Energy: {result['min_energy']:.6f}")
            if 'min_cost' in result:
                print(f"  Minimum Cost: {result['min_cost']:.6f}")
    
    # Compare methods
    comparison = optimizer.compare_methods()
    print("\nMethod Comparison:")
    for method, metrics in comparison.items():
        print(f"\n{method.upper()}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value:.4f}")
    
    # Quantum machine learning demo
    qml = QuantumMachineLearning(portfolio)
    
    # Generate sample market data
    market_data = {}
    for asset_id in assets.keys():
        # Generate random walk
        prices = [100]
        for _ in range(100):
            return_rate = np.random.normal(0.0001, 0.02)
            new_price = prices[-1] * (1 + return_rate)
            prices.append(new_price)
        market_data[asset_id] = prices
    
    # Extract quantum features
    quantum_features = qml.extract_quantum_features(market_data)
    print(f"\nExtracted quantum features for {len(quantum_features)} assets")
    
    return optimizer, results, comparison

if __name__ == "__main__":
    demonstrate_quantum_algorithms()