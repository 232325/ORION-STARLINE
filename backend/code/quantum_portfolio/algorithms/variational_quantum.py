"""
Variational Quantum Optimizer
=============================

Variational quantum algoritmi yordamida portfolio optimizatsiya.
Bu modul VQE (Variational Quantum Eigensolver) printsiplarini qo'llaydi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Callable
import logging
import matplotlib.pyplot as plt
from scipy.optimize import minimize

class VariationalQuantumOptimizer:
    """
    Variational Quantum Portfolio Optimizer
    """
    
    def __init__(self, 
                 quantum_portfolio_theory,
                 num_qubits: int = 8,
                 num_layers: int = 3,
                 learning_rate: float = 0.01,
                 max_iterations: int = 1000):
        """
        Initialize variational quantum optimizer
        
        Args:
            quantum_portfolio_theory: QuantumPortfolioTheory instance
            num_qubits: Number of qubits for quantum circuit
            num_layers: Number of variational layers
            learning_rate: Learning rate for parameter updates
            max_iterations: Maximum optimization iterations
        """
        self.qpt = quantum_portfolio_theory
        self.num_qubits = num_qubits
        self.num_layers = num_layers
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        
        # Variational parameters
        self.theta = None
        self.optimal_theta = None
        
        # Circuit parameters
        self.gate_angles = []
        self.measurement_outcomes = []
        
        # Optimization history
        self.cost_history = []
        self.parameter_history = []
        
        self.logger = logging.getLogger(__name__)
        self._initialize_circuit()
    
    def _initialize_circuit(self):
        """Initialize quantum circuit parameters"""
        # Random initialization of variational parameters
        total_params = self.num_qubits * self.num_layers * 2  # Rx and Rz gates
        self.theta = np.random.uniform(0, 2*np.pi, total_params)
        self.optimal_theta = self.theta.copy()
    
    def _create_variational_circuit(self, theta: np.ndarray) -> np.ndarray:
        """
        Create variational quantum circuit
        Simplified representation of VQE circuit
        """
        # Initialize quantum state |0⟩^n
        circuit_state = np.zeros(2**self.num_qubits, dtype=complex)
        circuit_state[0] = 1.0  # |000...0⟩ state
        
        # Apply variational layers
        param_idx = 0
        for layer in range(self.num_layers):
            # Rotation gates
            for qubit in range(self.num_qubits):
                # Rx gate
                angle_x = theta[param_idx]
                rx_gate = np.array([
                    [np.cos(angle_x/2), -1j*np.sin(angle_x/2)],
                    [-1j*np.sin(angle_x/2), np.cos(angle_x/2)]
                ])
                
                # Apply to appropriate subspace
                circuit_state = self._apply_single_gate(circuit_state, rx_gate, qubit)
                param_idx += 1
                
                # Rz gate
                angle_z = theta[param_idx]
                rz_gate = np.array([
                    [np.exp(-1j*angle_z/2), 0],
                    [0, np.exp(1j*angle_z/2)]
                ])
                
                circuit_state = self._apply_single_gate(circuit_state, rz_gate, qubit)
                param_idx += 1
            
            # Entangling gates (CNOT between adjacent qubits)
            if layer < self.num_layers - 1:
                for i in range(self.num_qubits - 1):
                    circuit_state = self._apply_cnot(circuit_state, i, i + 1)
        
        return circuit_state
    
    def _apply_single_gate(self, state: np.ndarray, gate: np.ndarray, qubit: int) -> np.ndarray:
        """Apply single qubit gate to quantum state"""
        new_state = state.copy()
        dim = len(state)
        qubits_involved = int(np.log2(dim))
        
        # Apply gate to specified qubit
        for i in range(0, dim, 2**(qubit + 1)):
            for j in range(2**qubit):
                # Apply gate to computational basis states
                state_0 = state[i + j]
                state_1 = state[i + j + 2**qubit]
                
                new_state[i + j] = gate[0, 0] * state_0 + gate[0, 1] * state_1
                new_state[i + j + 2**qubit] = gate[1, 0] * state_0 + gate[1, 1] * state_1
        
        return new_state
    
    def _apply_cnot(self, state: np.ndarray, control: int, target: int) -> np.ndarray:
        """Apply CNOT gate between control and target qubits"""
        dim = len(state)
        new_state = state.copy()
        
        for i in range(dim):
            binary = format(i, f'0{int(np.log2(dim))}b')
            if binary[control] == '1':  # Control qubit is |1⟩
                target_bit = binary[target]
                if target_bit == '0':
                    # Flip target bit
                    flipped_i = i ^ (1 << target)
                    new_state[flipped_i] = state[i]
                else:
                    # Target is already |1⟩
                    new_state[i] = state[i]
        
        return new_state
    
    def _measure_expectation_value(self, circuit_state: np.ndarray) -> float:
        """
        Measure expectation value for portfolio optimization
        """
        # Calculate probabilities
        probabilities = np.abs(circuit_state) ** 2
        
        # Map quantum states to portfolio allocations
        allocations = self._states_to_allocations(probabilities)
        
        # Calculate portfolio cost
        if len(allocations) > 0:
            weights = np.array(list(allocations.values()))
            if np.sum(weights) > 0:
                weights = weights / np.sum(weights)  # Normalize
                
                expected_returns = self.qpt._quantum_expected_returns()
                portfolio_return = np.sum(weights * expected_returns)
                
                if self.qpt.covariance_matrix is not None:
                    portfolio_variance = np.dot(weights, np.dot(self.qpt.covariance_matrix, weights))
                    portfolio_cost = - (portfolio_return - 0.5 * portfolio_variance)  # Negative for minimization
                else:
                    portfolio_cost = -portfolio_return
                
                return portfolio_cost
        
        return 0.0
    
    def _states_to_allocations(self, probabilities: np.ndarray) -> Dict:
        """
        Map quantum measurement outcomes to portfolio allocations
        """
        # Simplified mapping: use probability distribution to derive allocations
        n_assets = len(self.qpt.assets)
        allocations = {}
        
        # Take top-k states as the most likely configurations
        top_states = np.argsort(probabilities)[-min(n_assets, len(probabilities)):]
        
        for i, state_idx in enumerate(top_states):
            if i < n_assets:
                allocations[self.qpt.assets[i]] = probabilities[state_idx]
        
        return allocations
    
    def _calculate_gradients(self, theta: np.ndarray, h: float = 1e-7) -> np.ndarray:
        """
        Calculate gradients using parameter shift rule (simplified)
        """
        gradients = np.zeros_like(theta)
        
        for i in range(len(theta)):
            # Forward shift
            theta_plus = theta.copy()
            theta_plus[i] += h
            cost_plus = self._measure_expectation_value(self._create_variational_circuit(theta_plus))
            
            # Backward shift
            theta_minus = theta.copy()
            theta_minus[i] -= h
            cost_minus = self._measure_expectation_value(self._create_variational_circuit(theta_minus))
            
            # Central difference
            gradients[i] = (cost_plus - cost_minus) / (2 * h)
        
        return gradients
    
    def optimize(self, 
                objective_function: Optional[Callable] = None,
                target_return: Optional[float] = None,
                risk_aversion: float = 1.0) -> Dict:
        """
        Variational quantum optimization
        
        Args:
            objective_function: Custom objective function
            target_return: Target portfolio return
            risk_aversion: Risk aversion parameter
            
        Returns:
            Optimization results
        """
        if objective_function is None:
            # Use portfolio optimization as default
            objective_function = self._portfolio_objective_function(target_return, risk_aversion)
        
        # Initialize tracking variables
        best_cost = float('inf')
        best_theta = self.theta.copy()
        
        # VQE optimization loop
        for iteration in range(self.max_iterations):
            # Create quantum circuit
            circuit_state = self._create_variational_circuit(self.theta)
            
            # Measure expectation value
            current_cost = self._measure_expectation_value(circuit_state)
            
            # Record history
            self.cost_history.append(current_cost)
            self.parameter_history.append(self.theta.copy())
            
            # Update best solution
            if current_cost < best_cost:
                best_cost = current_cost
                best_theta = self.theta.copy()
            
            # Calculate gradients
            gradients = self._calculate_gradients(self.theta)
            
            # Update parameters using gradient descent
            self.theta = self.theta - self.learning_rate * gradients
            
            # Apply parameter constraints
            self.theta = self.theta % (2 * np.pi)  # Keep angles in [0, 2π)
            
            # Progress logging
            if iteration % 100 == 0:
                self.logger.info(f"VQE Iteration {iteration}: Cost={current_cost:.6f}")
        
        # Final results
        self.optimal_theta = best_theta
        
        # Generate final solution
        final_circuit_state = self._create_variational_circuit(self.optimal_theta)
        final_allocations = self._states_to_allocations(np.abs(final_circuit_state) ** 2)
        
        # Calculate portfolio statistics
        portfolio_stats = self._calculate_portfolio_statistics(final_allocations)
        
        return {
            'optimal_allocations': final_allocations,
            'optimal_cost': best_cost,
            'final_theta': self.optimal_theta,
            'cost_history': self.cost_history,
            'parameter_history': self.parameter_history,
            'portfolio_statistics': portfolio_stats,
            'total_iterations': iteration + 1,
            'optimization_method': 'variational_quantum'
        }
    
    def _portfolio_objective_function(self, target_return: Optional[float], risk_aversion: float) -> Callable:
        """Create portfolio optimization objective function"""
        def objective(weights):
            if target_return is not None:
                expected_returns = self.qpt._quantum_expected_returns()
                portfolio_return = np.sum(weights * expected_returns)
                
                return_penalty = 0
                if portfolio_return < target_return:
                    return_penalty = (target_return - portfolio_return) ** 2
            else:
                return_penalty = 0
            
            return return_penalty
        
        return objective
    
    def _calculate_portfolio_statistics(self, allocations: Dict) -> Dict:
        """Calculate portfolio statistics from allocations"""
        if not allocations:
            return {}
        
        # Convert to weights
        weights = np.array(list(allocations.values()))
        weights = weights / np.sum(weights)  # Normalize
        
        expected_returns = self.qpt._quantum_expected_returns()
        portfolio_return = np.sum(weights * expected_returns)
        
        if self.qpt.covariance_matrix is not None:
            portfolio_variance = np.dot(weights, np.dot(self.qpt.covariance_matrix, weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
        else:
            portfolio_volatility = np.std(weights)
        
        return {
            'weights': weights.tolist(),
            'expected_return': portfolio_return,
            'volatility': portfolio_volatility,
            'sharpe_ratio': (portfolio_return - self.qpt.risk_free_rate) / portfolio_volatility if portfolio_volatility > 0 else 0,
            'quantum_entropy': self.qpt._calculate_quantum_entropy(weights),
            'quantum_coherence': self.qpt._calculate_quantum_coherence(weights)
        }
    
    def visualize_vqe_process(self, save_path: Optional[str] = None) -> None:
        """Visualize VQE optimization process"""
        if not self.cost_history:
            self.logger.warning("VQE optimization ma'lumotlari topilmadi")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Variational Quantum Optimization Process', fontsize=16)
        
        # 1. Cost function convergence
        axes[0, 0].plot(self.cost_history)
        axes[0, 0].set_title('Cost Function Convergence')
        axes[0, 0].set_xlabel('Iteration')
        axes[0, 0].set_ylabel('Cost')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Parameter evolution (show first few parameters)
        if self.parameter_history and len(self.parameter_history[0]) > 0:
            param_matrix = np.array(self.parameter_history)
            for i in range(min(5, len(param_matrix[0]))):  # Show first 5 parameters
                axes[0, 1].plot(param_matrix[:, i], label=f'θ_{i}')
            axes[0, 1].set_title('Parameter Evolution')
            axes[0, 1].set_xlabel('Iteration')
            axes[0, 1].set_ylabel('Parameter Value')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Final allocation (if available)
        if self.optimal_theta is not None:
            final_state = self._create_variational_circuit(self.optimal_theta)
            final_probs = np.abs(final_state) ** 2
            
            # Show distribution of measurement outcomes
            axes[1, 0].hist(final_probs, bins=min(20, len(final_probs)), alpha=0.7)
            axes[1, 0].set_title('Final Quantum State Probabilities')
            axes[1, 0].set_xlabel('Probability')
            axes[1, 0].set_ylabel('Frequency')
        
        # 4. Quantum circuit visualization (simplified)
        if hasattr(self, 'num_qubits') and hasattr(self, 'num_layers'):
            # Show circuit structure
            circuit_depth = self.num_layers * (self.num_qubits * 2 + (self.num_qubits - 1))
            axes[1, 1].bar(['Circuit Depth'], [circuit_depth])
            axes[1, 1].set_title('Quantum Circuit Properties')
            axes[1, 1].set_ylabel('Depth')
            
            # Add text annotations
            axes[1, 1].text(0, circuit_depth + 0.5, 
                          f'Qubits: {self.num_qubits}\\nLayers: {self.num_layers}\\nTotal Params: {len(self.theta)}',
                          ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"VQE visualization saqlandi: {save_path}")
        else:
            plt.show()
    
    def save_vqe_state(self, filepath: str):
        """Save VQE optimization state"""
        state = {
            'num_qubits': self.num_qubits,
            'num_layers': self.num_layers,
            'learning_rate': self.learning_rate,
            'max_iterations': self.max_iterations,
            'optimal_theta': self.optimal_theta.tolist() if self.optimal_theta is not None else None,
            'cost_history': self.cost_history,
            'parameter_history': [params.tolist() for params in self.parameter_history]
        }
        
        import json
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        self.logger.info(f"VQE state saqlandi: {filepath}")
    
    def load_vqe_state(self, filepath: str):
        """Load VQE optimization state"""
        import json
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        self.num_qubits = state['num_qubits']
        self.num_layers = state['num_layers']
        self.learning_rate = state['learning_rate']
        self.max_iterations = state['max_iterations']
        
        self.optimal_theta = np.array(state['optimal_theta']) if state['optimal_theta'] else None
        self.cost_history = state['cost_history']
        self.parameter_history = [np.array(params) for params in state['parameter_history']]
        
        self.logger.info(f"VQE state yuklandi: {filepath}")