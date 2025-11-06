"""
Variational Quantum Eigensolver (VQE) Algorithm
==============================================

Quantum portfolio optimization uchun VQE algoritmi.
"""

import numpy as np
import cmath
from typing import List, Dict, Tuple, Optional, Union, Callable
from dataclasses import dataclass
from scipy.optimize import minimize, differential_evolution
from scipy.linalg import norm, eigh, expm
import matplotlib.pyplot as plt

try:
    from ..core.quantum_state import QuantumPortfolioState, QuantumState
    from ..core.superposition import QuantumSuperposition
except ImportError:
    # Fallback for standalone execution
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from core.quantum_state import QuantumPortfolioState, QuantumState
    from core.superposition import QuantumSuperposition


@dataclass
class VQEConfig:
    """VQE konfiguratsiya parametrlari"""
    n_qubits: int = 4  # Qubit soni
    n_layers: int = 3  # Variational layers soni
    max_iterations: int = 1000  # Maksimal iterations
    tolerance: float = 1e-6  # Tolerance
    ansatz_type: str = 'hardware_efficient'  # Ansatz turi
    optimization_method: str = 'COBYLA'  # Classical optimizer
    initial_parameters: np.ndarray = None  # Boshlang'ich parameters
    shot_count: int = 1000  # Quantum measurements soni


class QuantumVQE:
    """
    Variational Quantum Eigensolver for Portfolio Optimization
    
    Quantum portfolio optimizatsiyasi uchun VQE algoritmi implementation.
    """
    
    def __init__(self, config: VQEConfig = None):
        self.config = config or VQEConfig()
        
        # Variational parameters
        self.parameters = None
        self.parameter_history = []
        self.energy_history = []
        
        # Ansatz configuration
        self.ansatz_gates = []
        self.observable_operators = {}
        
        # Optimization results
        self.optimization_results = {}
        self.quantum_states = []
        
    def setup_portfolio_problem(self, portfolio: QuantumPortfolioState,
                              returns_data: np.ndarray,
                              covariance_matrix: np.ndarray = None) -> None:
        """
        Portfolio optimizatsiya muammosini VQE uchun sozlash
        
        Args:
            portfolio: Portfolio quantum state
            returns_data: Returns ma'lumotlari
            covariance_matrix: Covariance matrix
        """
        # Convert portfolio to quantum circuit representation
        n_assets = len(portfolio.assets)
        self.config.n_qubits = max(2, min(n_assets, self.config.n_qubits))
        
        # Hamiltonian construction for portfolio optimization
        self._construct_portfolio_hamiltonian(portfolio, returns_data, covariance_matrix)
        
        # Ansatz setup
        self._setup_variational_ansatz()
        
        # Initialize parameters
        if self.config.initial_parameters is None:
            self.parameters = np.random.uniform(0, 2*np.pi, self._get_parameter_count())
        else:
            self.parameters = self.config.initial_parameters.copy()
        
        print(f"VQE setup completed: {self.config.n_qubits} qubits, {self._get_parameter_count()} parameters")
    
    def _construct_portfolio_hamiltonian(self, portfolio: QuantumPortfolioState,
                                       returns_data: np.ndarray,
                                       covariance_matrix: np.ndarray) -> None:
        """
        Portfolio optimization uchun Hamiltonian qurish
        
        Args:
            portfolio: Portfolio quantum state
            returns_data: Returns ma'lumotlari
            covariance_matrix: Covariance matrix
        """
        n_qubits = self.config.n_qubits
        
        # Cost Hamiltonian (portfolio objective)
        cost_hamiltonian = np.zeros((2**n_qubits, 2**n_qubits), dtype=complex)
        
        # Expected return term
        expected_return = portfolio.get_expected_return(returns_data)
        
        # Risk term (variance)
        if covariance_matrix is not None:
            portfolio_risk = portfolio.get_risk(covariance_matrix)
        else:
            portfolio_risk = np.sqrt(np.sum(portfolio.get_portfolio_weights()**2 * 0.15**2))
        
        # Construct Hamiltonian matrix
        # Simplified Hamiltonian: H = return_coeff * Z + risk_coeff * Z^2
        for i in range(2**n_qubits):
            # Z operator expectation
            z_expectation = self._calculate_z_expectation(i, n_qubits)
            
            # Z^2 operator expectation  
            z2_expectation = z_expectation**2
            
            cost_hamiltonian[i, i] = (expected_return * z_expectation + 
                                     self.config.risk_aversion * portfolio_risk * z2_expectation)
        
        # Add penalty terms for portfolio constraints
        penalty_hamiltonian = self._construct_penalty_hamiltonian(n_qubits)
        
        # Total Hamiltonian
        total_hamiltonian = cost_hamiltonian + 0.1 * penalty_hamiltonian
        
        self.observable_operators['total_hamiltonian'] = total_hamiltonian
        self.observable_operators['cost_hamiltonian'] = cost_hamiltonian
        self.observable_operators['penalty_hamiltonian'] = penalty_hamiltonian
        
        print(f"Hamiltonian constructed: {2**n_qubits}x{2**n_qubits} matrix")
    
    def _construct_penalty_hamiltonian(self, n_qubits: int) -> np.ndarray:
        """Penalty terms uchun Hamiltonian"""
        penalty_hamiltonian = np.zeros((2**n_qubits, 2**n_qubits), dtype=complex)
        
        # Weight sum penalty (|∑wᵢ - 1|²)
        for i in range(2**n_qubits):
            binary_repr = format(i, f'0{n_qubits}b')
            weight_sum = sum(int(bit) for bit in binary_repr) / n_qubits
            penalty = (weight_sum - 1.0)**2
            penalty_hamiltonian[i, i] += penalty
        
        # Individual weight bounds penalty
        for qubit_idx in range(n_qubits):
            for i in range(2**n_qubits):
                binary_repr = format(i, f'0{n_qubits}b')
                if int(binary_repr[qubit_idx]) == 1:  # Weight > 0.5
                    penalty_hamiltonian[i, i] += 0.1
        
        return penalty_hamiltonian
    
    def _setup_variational_ansatz(self) -> None:
        """Variational ansatz sozlamasi"""
        n_qubits = self.config.n_qubits
        n_layers = self.config.n_layers
        
        if self.config.ansatz_type == 'hardware_efficient':
            self.ansatz_gates = self._create_hardware_efficient_ansatz(n_qubits, n_layers)
        elif self.config.ansatz_type == 'alternating_layer':
            self.ansatz_gates = self._create_alternating_layer_ansatz(n_qubits, n_layers)
        else:
            raise ValueError(f"Noma'lum ansatz type: {self.config.ansatz_type}")
        
        print(f"Variational ansatz created: {len(self.ansatz_gates)} gates")
    
    def _create_hardware_efficient_ansatz(self, n_qubits: int, n_layers: int) -> List[Dict]:
        """Hardware-efficient variational ansatz"""
        gates = []
        
        # Initial layer
        for qubit in range(n_qubits):
            gates.append({
                'type': 'RY',
                'qubit': qubit,
                'parameter_index': len(gates)
            })
        
        # Alternating layers
        for layer in range(n_layers):
            # Entangling layer
            for qubit in range(n_qubits - 1):
                gates.append({
                    'type': 'CNOT',
                    'control': qubit,
                    'target': qubit + 1
                })
            
            # Rotation layer
            for qubit in range(n_qubits):
                gates.append({
                    'type': 'RY',
                    'qubit': qubit,
                    'parameter_index': len(gates)
                })
                
                # Add RZ for more expressivity
                gates.append({
                    'type': 'RZ', 
                    'qubit': qubit,
                    'parameter_index': len(gates)
                })
        
        return gates
    
    def _create_alternating_layer_ansatz(self, n_qubits: int, n_layers: int) -> List[Dict]:
        """Alternating layer variational ansatz"""
        gates = []
        
        for layer in range(n_layers):
            # Y rotations
            for qubit in range(n_qubits):
                gates.append({
                    'type': 'RY',
                    'qubit': qubit,
                    'parameter_index': len(gates)
                })
            
            # Z rotations
            for qubit in range(n_qubits):
                gates.append({
                    'type': 'RZ',
                    'qubit': qubit,
                    'parameter_index': len(gates)
                })
            
            # Entangling gates
            if layer % 2 == 0:
                # Even layers: forward CNOTs
                for qubit in range(n_qubits - 1):
                    gates.append({
                        'type': 'CNOT',
                        'control': qubit,
                        'target': qubit + 1
                    })
            else:
                # Odd layers: backward CNOTs
                for qubit in range(n_qubits - 1, 0, -1):
                    gates.append({
                        'type': 'CNOT',
                        'control': qubit,
                        'target': qubit - 1
                    })
        
        return gates
    
    def _get_parameter_count(self) -> int:
        """Variational parameters sonini olish"""
        return sum(1 for gate in self.ansatz_gates if 'parameter_index' in gate)
    
    def _apply_ansatz(self, parameters: np.ndarray) -> np.ndarray:
        """
        Variational ansatz qo'llash
        
        Args:
            parameters: Variational parameters
        
        Returns:
            Quantum state amplitudes
        """
        n_qubits = self.config.n_qubits
        state = np.zeros(2**n_qubits, dtype=complex)
        state[0] = 1.0  # |00...0⟩ initial state
        
        param_idx = 0
        
        for gate in self.ansatz_gates:
            if gate['type'] == 'RY':
                # Y rotation
                angle = parameters[gate['parameter_index']]
                self._apply_ry_gate(state, gate['qubit'], angle)
                
            elif gate['type'] == 'RZ':
                # Z rotation  
                angle = parameters[gate['parameter_index']]
                self._apply_rz_gate(state, gate['qubit'], angle)
                
            elif gate['type'] == 'CNOT':
                # CNOT gate
                self._apply_cnot_gate(state, gate['control'], gate['target'])
        
        return state
    
    def _apply_ry_gate(self, state: np.ndarray, qubit: int, angle: float) -> None:
        """RY gate qo'llash"""
        n_qubits = int(np.log2(len(state)))
        rotation_matrix = np.array([
            [np.cos(angle/2), -np.sin(angle/2)],
            [np.sin(angle/2), np.cos(angle/2)]
        ])
        
        # Apply to all basis states
        new_state = np.zeros_like(state)
        
        for i in range(2**n_qubits):
            binary_repr = format(i, f'0{n_qubits}b')
            qubit_value = int(binary_repr[-(qubit+1)])
            
            if qubit_value == 0:
                # |0⟩ component
                j = i  # Same index
                k = i | (1 << qubit)  # Flip qubit to |1⟩
                
                new_state[j] += rotation_matrix[0, 0] * state[j] + rotation_matrix[0, 1] * state[k]
                new_state[k] += rotation_matrix[1, 0] * state[j] + rotation_matrix[1, 1] * state[k]
            else:
                # |1⟩ component already handled above
                pass
        
        state[:] = new_state
    
    def _apply_rz_gate(self, state: np.ndarray, qubit: int, angle: float) -> None:
        """RZ gate qo'llash"""
        n_qubits = int(np.log2(len(state)))
        rotation_matrix = np.array([
            [np.exp(-1j * angle/2), 0],
            [0, np.exp(1j * angle/2)]
        ])
        
        for i in range(2**n_qubits):
            binary_repr = format(i, f'0{n_qubits}b')
            qubit_value = int(binary_repr[-(qubit+1)])
            
            if qubit_value == 1:
                state[i] *= rotation_matrix[1, 1]
    
    def _apply_cnot_gate(self, state: np.ndarray, control: int, target: int) -> None:
        """CNOT gate qo'llash"""
        n_qubits = int(np.log2(len(state)))
        new_state = np.zeros_like(state)
        
        for i in range(2**n_qubits):
            binary_repr = format(i, f'0{n_qubits}b')
            control_value = int(binary_repr[-(control+1)])
            target_value = int(binary_repr[-(target+1)])
            
            if control_value == 1:
                # Flip target bit
                new_index = i ^ (1 << target)
                new_state[new_index] = state[i]
            else:
                new_state[i] = state[i]
        
        state[:] = new_state
    
    def _calculate_z_expectation(self, state_index: int, n_qubits: int) -> float:
        """Z operator expectation qiymati hisoblash"""
        binary_repr = format(state_index, f'0{n_qubits}b')
        # Z expectation: +1 for |0⟩, -1 for |1⟩
        z_expectation = sum(1 if bit == '0' else -1 for bit in binary_repr) / n_qubits
        return z_expectation
    
    def _evaluate_energy(self, parameters: np.ndarray) -> float:
        """
        Energy expectation qiymati hisoblash
        
        Args:
            parameters: Variational parameters
        
        Returns:
            Energy expectation
        """
        # Prepare quantum state
        quantum_state = self._apply_ansatz(parameters)
        
        # Calculate expectation value
        hamiltonian = self.observable_operators['total_hamiltonian']
        
        # Energy = ⟨ψ|H|ψ⟩
        energy = np.real(np.dot(np.conj(quantum_state), np.dot(hamiltonian, quantum_state)))
        
        return energy
    
    def optimize(self, callback: Callable = None) -> Dict:
        """
        VQE optimization jarayoni
        
        Args:
            callback: Har bir iteratsiyada chaqiriladigan function
        
        Returns:
            Optimization natijalari
        """
        print("Starting VQE optimization...")
        
        def objective_function(params):
            energy = self._evaluate_energy(params)
            
            # Record history
            self.energy_history.append(energy)
            self.parameter_history.append(params.copy())
            
            if callback:
                callback(energy, params)
            
            return energy
        
        # Optimization methods
        methods_config = {
            'COBYLA': {'options': {'maxiter': self.config.max_iterations}},
            'L-BFGS-B': {'options': {'maxiter': self.config.max_iterations}},
            'SLSQP': {'options': {'maxiter': self.config.max_iterations}}
        }
        
        best_result = None
        best_energy = float('inf')
        
        for method_name, method_config in methods_config.items():
            try:
                print(f"Trying optimization method: {method_name}")
                
                result = minimize(
                    objective_function,
                    self.parameters,
                    method=method_name,
                    **method_config,
                    options={'ftol': self.config.tolerance, 'disp': False}
                )
                
                if result.fun < best_energy:
                    best_energy = result.fun
                    best_result = result
                    self.parameters = result.x.copy()
                
                print(f"{method_name} - Energy: {result.fun:.6f}, Success: {result.success}")
                
            except Exception as e:
                print(f"Optimization method {method_name} failed: {e}")
        
        # Final optimization with best method
        if best_result and best_result.success:
            # Get final quantum state
            final_quantum_state = self._apply_ansatz(self.parameters)
            
            # Calculate portfolio weights from quantum state
            portfolio_weights = self._extract_portfolio_weights(final_quantum_state)
            
            # Store results
            self.optimization_results = {
                'success': True,
                'optimal_energy': best_energy,
                'optimal_parameters': self.parameters.copy(),
                'final_quantum_state': final_quantum_state,
                'portfolio_weights': portfolio_weights,
                'optimization_method': best_result.method,
                'iterations': len(self.energy_history),
                'convergence_history': {
                    'energies': self.energy_history.copy(),
                    'parameters': [p.copy() for p in self.parameter_history]
                }
            }
            
            print(f"VQE optimization completed successfully!")
            print(f"Optimal energy: {best_energy:.6f}")
            print(f"Portfolio weights: {portfolio_weights}")
            
        else:
            print("VQE optimization failed!")
            self.optimization_results = {
                'success': False,
                'error': 'Optimization did not converge'
            }
        
        return self.optimization_results
    
    def _extract_portfolio_weights(self, quantum_state: np.ndarray) -> np.ndarray:
        """Quantum statedan portfolio weightlarni olish"""
        n_qubits = self.config.n_qubits
        n_states = len(quantum_state)
        
        # Normalize probabilities
        probabilities = np.abs(quantum_state)**2
        probabilities = probabilities / np.sum(probabilities)
        
        # Extract weights from probability distribution
        # Simplified: weight proportional to probability
        weights = probabilities[:min(len(probabilities), 8)]  # Use first 8 states
        weights = weights / np.sum(weights)  # Normalize
        
        # Pad with zeros if needed
        if len(weights) < n_qubits:
            weights = np.pad(weights, (0, n_qubits - len(weights)))
        
        return weights[:n_qubits]
    
    def get_variational_circuit(self) -> Dict:
        """
        Variational circuit ko'rinishi
        
        Returns:
            Circuit ma'lumotlari
        """
        return {
            'n_qubits': self.config.n_qubits,
            'n_layers': self.config.n_layers,
            'n_parameters': self._get_parameter_count(),
            'ansatz_type': self.config.ansatz_type,
            'gates': self.ansatz_gates,
            'optimal_parameters': self.parameters.copy() if self.parameters is not None else None
        }
    
    def analyze_optimization_convergence(self) -> Dict:
        """
        Optimization convergence analizi
        
        Returns:
            Convergence analysis
        """
        if not self.energy_history:
            return {'error': 'Optimization history mavjud emas'}
        
        energies = np.array(self.energy_history)
        
        # Convergence metrics
        initial_energy = energies[0]
        final_energy = energies[-1]
        energy_improvement = initial_energy - final_energy
        
        # Convergence rate
        if len(energies) > 1:
            energy_differences = np.abs(np.diff(energies))
            avg_convergence_rate = np.mean(energy_differences[-10:])  # Last 10 iterations
        else:
            avg_convergence_rate = 0
        
        # Check for convergence
        tolerance_achieved = abs(energies[-1] - energies[-2]) < self.config.tolerance if len(energies) > 1 else False
        
        return {
            'initial_energy': initial_energy,
            'final_energy': final_energy,
            'energy_improvement': energy_improvement,
            'total_iterations': len(energies),
            'convergence_rate': avg_convergence_rate,
            'tolerance_achieved': tolerance_achieved,
            'optimization_success': self.optimization_results.get('success', False),
            'energy_history': energies.tolist(),
            'relative_improvement': energy_improvement / abs(initial_energy) if initial_energy != 0 else 0
        }
    
    def quantum_advantage_analysis(self, classical_result: Dict = None) -> Dict:
        """
        Quantum advantage tahlili
        
        Args:
            classical_result: Classical optimizatsiya natijasi
        
        Returns:
            Quantum advantage analysis
        """
        if not self.optimization_results.get('success'):
            return {'error': 'VQE optimization successful emas'}
        
        vqe_energy = self.optimization_results['optimal_energy']
        
        # Quantum circuit metrics
        n_gates = len(self.ansatz_gates)
        circuit_depth = self._calculate_circuit_depth()
        parameter_efficiency = self._get_parameter_count() / (2**self.config.n_qubits)
        
        # Quantum resources
        quantum_resources = {
            'n_qubits': self.config.n_qubits,
            'n_gates': n_gates,
            'circuit_depth': circuit_depth,
            'parameter_count': self._get_parameter_count(),
            'parameter_efficiency': parameter_efficiency
        }
        
        # Classical comparison
        classical_comparison = {}
        if classical_result:
            classical_energy = classical_result.get('optimal_energy', float('inf'))
            classical_resources = classical_result.get('classical_resources', {})
            
            classical_comparison = {
                'classical_energy': classical_energy,
                'quantum_energy': vqe_energy,
                'energy_improvement': classical_energy - vqe_energy,
                'relative_improvement': (classical_energy - vqe_energy) / classical_energy if classical_energy != 0 else 0,
                'classical_resources': classical_resources
            }
        
        # Quantum advantage assessment
        has_advantage = False
        if classical_comparison:
            has_advantage = classical_comparison['relative_improvement'] > 0.01  # 1% improvement
        
        return {
            'quantum_energy': vqe_energy,
            'quantum_resources': quantum_resources,
            'classical_comparison': classical_comparison,
            'has_quantum_advantage': has_advantage,
            'quantum_efficiency': parameter_efficiency,
            'circuit_complexity': n_gates / (2**self.config.n_qubits)
        }
    
    def _calculate_circuit_depth(self) -> int:
        """Circuit chuqurligini hisoblash"""
        # Simplified depth calculation
        # In practice, would track gate dependencies
        return len(self.ansatz_gates) // self.config.n_qubits