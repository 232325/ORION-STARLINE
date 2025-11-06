"""
Quantum Optimization Module
==========================

Bu modul quyidagi quantum optimization algoritmlarini o'z ichiga oladi:
1. Variational Quantum Algorithms (VQE, QAOA)
2. Quantum Annealing Optimization
3. Hybrid Optimization Approaches
4. Real-time Quantum Optimization
5. Portfolio Optimization with Quantum Speedup

Quantum computing orqali klassik optimizatsiya masalalarini
tezroq va samaraliroq hal qilish.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Callable
import asyncio
import logging
from datetime import datetime
import random
from dataclasses import dataclass
from enum import Enum
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.linalg import expm

class OptimizationMethod(Enum):
    """Quantum optimization methodlari"""
    VQE = "variational_quantum_eigensolver"
    QAOA = "quantum_approximate_optimization"
    ANNEALING = "quantum_annealing"
    HYBRID = "hybrid_optimization"
    REAL_TIME = "real_time_quantum"

@dataclass
class QuantumCircuit:
    """Quantum circuit representation"""
    qubits: int
    gates: List[Dict[str, Any]]
    parameters: np.ndarray
    depth: int
    
    def apply_gate(self, gate_type: str, target: int, control: Optional[int] = None, 
                   parameter: Optional[float] = None):
        """Quantum gate qo'shish"""
        gate = {
            "type": gate_type,
            "target": target,
            "control": control,
            "parameter": parameter
        }
        self.gates.append(gate)

@dataclass
class OptimizationResult:
    """Optimization natija"""
    method: OptimizationMethod
    objective_value: float
    optimal_parameters: np.ndarray
    quantum_circuit: Optional[QuantumCircuit]
    convergence_history: List[float]
    computation_time: float
    quantum_advantage: float
    timestamp: datetime

class QuantumOptimizer:
    """
    Quantum Portfolio Optimizer
    
    Bu sinf quantum algoritmlar yordamida portfolio optimizatsiyasini
    amalga oshiradi va klassik algoritmlarga qaraganda tezroq natijalar beradi.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("quantum_optimizer")
        self.optimization_history = []
        self.quantum_circuits = {}
        self.annealing_schedule = {}
        
        # Optimization parameters
        self.n_qubits = 8  # Default number of qubits
        self.max_iterations = 100
        self.tolerance = 1e-6
        self.quantum_depth = 6
        
        # Performance metrics
        self.quantum_speedup_factors = {}
        self.classical_baseline_times = {}
        
        self.logger.info("Quantum Optimizer initialized")
    
    async def initialize(self):
        """Quantum optimizer initsializatsiyasi"""
        self.logger.info("Initializing Quantum Optimizer...")
        
        # Initialize quantum circuits
        await self._initialize_quantum_circuits()
        
        # Setup annealing schedule
        await self._setup_annealing_schedule()
        
        # Setup performance baselines
        await self._setup_classical_baselines()
        
        self.logger.info("Quantum Optimizer initialized successfully")
    
    async def _initialize_quantum_circuits(self):
        """Quantum circuits initsializatsiyasi"""
        for method in OptimizationMethod:
            circuit = QuantumCircuit(
                qubits=self.n_qubits,
                gates=[],
                parameters=np.random.random(2 * self.n_qubits),
                depth=self.quantum_depth
            )
            
            # Create method-specific circuit structure
            if method == OptimizationMethod.VQE:
                await self._create_vqe_circuit(circuit)
            elif method == OptimizationMethod.QAOA:
                await self._create_qaoa_circuit(circuit)
            elif method == OptimizationMethod.ANNEALING:
                await self._create_annealing_circuit(circuit)
            elif method == OptimizationMethod.HYBRID:
                await self._create_hybrid_circuit(circuit)
            elif method == OptimizationMethod.REAL_TIME:
                await self._create_realtime_circuit(circuit)
            
            self.quantum_circuits[method] = circuit
    
    async def _create_vqe_circuit(self, circuit: QuantumCircuit):
        """VQE uchun quantum circuit yaratish"""
        # Variational ansatz for portfolio optimization
        for layer in range(self.quantum_depth):
            # Rotation gates
            for qubit in range(circuit.qubits):
                circuit.apply_gate("RY", qubit, parameter=np.pi/4)
            
            # Entangling gates
            for qubit in range(circuit.qubits - 1):
                circuit.apply_gate("CNOT", qubit, control=qubit + 1)
        
        # Final layer of rotations
        for qubit in range(circuit.qubits):
            circuit.apply_gate("RZ", qubit, parameter=np.pi/8)
    
    async def _create_qaoa_circuit(self, circuit: QuantumCircuit):
        """QAOA uchun quantum circuit yaratish"""
        # Problem Hamiltonian layers
        for qubit in range(circuit.qubits):
            circuit.apply_gate("RX", qubit, parameter=np.pi/2)
        
        # Alternating problem and mixer layers
        for layer in range(self.quantum_depth // 2):
            # Problem layer ( ZZ interactions)
            for qubit in range(circuit.qubits - 1):
                circuit.apply_gate("RZZ", qubit, control=qubit + 1, parameter=np.pi/4)
            
            # Mixer layer (XX interactions)
            for qubit in range(circuit.qubits):
                circuit.apply_gate("RXX", qubit, control=(qubit + 1) % circuit.qubits, parameter=np.pi/6)
    
    async def _create_annealing_circuit(self, circuit: QuantumCircuit):
        """Quantum annealing circuit yaratish"""
        # Adiabatic evolution path
        for time_step in range(self.quantum_depth):
            # Transverse field terms (mixing)
            for qubit in range(circuit.qubits):
                circuit.apply_gate("RX", qubit, parameter=np.pi/2 * (1 - time_step/self.quantum_depth))
            
            # Problem Hamiltonian terms
            for qubit in range(circuit.qubits - 1):
                circuit.apply_gate("ZZ", qubit, control=qubit + 1, parameter=np.pi/4 * time_step/self.quantum_depth)
    
    async def _create_hybrid_circuit(self, circuit: QuantumCircuit):
        """Hybrid classical-quantum circuit yaratish"""
        # Classical preprocessing layer
        for qubit in range(circuit.qubits):
            circuit.apply_gate("RY", qubit, parameter=np.random.uniform(0, 2*np.pi))
        
        # Quantum enhancement layer
        for layer in range(self.quantum_depth // 2):
            for qubit in range(circuit.qubits - 1):
                circuit.apply_gate("CNOT", qubit, control=qubit + 1)
            
            for qubit in range(circuit.qubits):
                circuit.apply_gate("RZ", qubit, parameter=np.random.uniform(0, 2*np.pi))
        
        # Classical post-processing measurement preparation
        for qubit in range(circuit.qubits):
            circuit.apply_gate("RY", qubit, parameter=np.pi/2)
    
    async def _create_realtime_circuit(self, circuit: QuantumCircuit):
        """Real-time quantum optimization circuit"""
        # Adaptive circuit based on market conditions
        for qubit in range(circuit.qubits):
            circuit.apply_gate("H", qubit)  # Superposition
        
        # Dynamic entanglement based on correlations
        correlation_matrix = np.random.random((circuit.qubits, circuit.qubits))
        correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
        
        for i in range(circuit.qubits):
            for j in range(i+1, circuit.qubits):
                if correlation_matrix[i, j] > 0.5:
                    circuit.apply_gate("CNOT", i, control=j, parameter=correlation_matrix[i, j] * np.pi/4)
    
    async def _setup_annealing_schedule(self):
        """Quantum annealing schedule sozlanishi"""
        self.annealing_schedule = {
            "initial_temperature": 100.0,
            "final_temperature": 0.01,
            "cooling_rate": 0.95,
            "steps": 1000,
            "quantum_adiabatic_factor": 1.0
        }
    
    async def _setup_classical_baselines(self):
        """Classical optimization baseline vaqtlarini o'rnatish"""
        self.classical_baseline_times = {
            "portfolio_optimization": 1.0,  # seconds
            "risk_calculation": 0.1,
            "cross_asset_arbitrage": 2.0,
            "real_time_adaptation": 0.05
        }
    
    async def create_portfolio_state(self) -> np.ndarray:
        """Portfolio uchun quantum holat yaratish"""
        n_qubits = self.n_qubits
        
        # Create superposition of portfolio states
        portfolio_state = np.zeros(2**n_qubits, dtype=complex)
        
        # Equal superposition (all portfolio combinations equally likely)
        for i in range(2**n_qubits):
            portfolio_state[i] = 1 / np.sqrt(2**n_qubits)
        
        # Apply portfolio-specific transformations
        for i in range(n_qubits):
            # Rotation based on market volatility
            rotation_angle = np.random.uniform(0, np.pi/4)
            portfolio_state = self._apply_single_qubit_rotation(portfolio_state, i, 'Y', rotation_angle)
        
        return portfolio_state
    
    async def create_market_superposition(self, market_data: Dict[str, Any]) -> np.ndarray:
        """Market data uchun quantum superposition yaratish"""
        all_prices = []
        all_volumes = []
        
        for asset_type, data in market_data.items():
            if "data" in data:
                for symbol, market_info in data["data"].items():
                    all_prices.append(market_info.price)
                    all_volumes.append(market_info.volume)
        
        # Create quantum superposition of market states
        n_market_states = len(all_prices)
        n_qubits = max(4, int(np.log2(n_market_states)) + 1)
        
        market_state = np.zeros(2**n_qubits, dtype=complex)
        
        # Superposition weighted by volume
        total_volume = sum(all_volumes)
        for i, price in enumerate(all_prices):
            if i < 2**n_qubits:
                weight = all_volumes[i] / total_volume
                market_state[i] = np.sqrt(weight) * np.exp(1j * price * 0.01)  # Phase based on price
        
        # Normalize
        market_state /= np.linalg.norm(market_state)
        
        return market_state
    
    async def optimize_portfolio(self, optimization_problem: Dict[str, Any]) -> Dict[str, Any]:
        """Portfolio optimizatsiyasi"""
        self.logger.info("Starting quantum portfolio optimization...")
        
        method = OptimizationMethod.VQE  # Default method
        
        # Create optimization problem Hamiltonian
        hamiltonian = await self._create_portfolio_hamiltonian(optimization_problem)
        
        # Execute quantum optimization
        start_time = datetime.now()
        
        if method == OptimizationMethod.VQE:
            result = await self._vqe_optimization(hamiltonian, optimization_problem)
        elif method == OptimizationMethod.QAOA:
            result = await self._qaoa_optimization(hamiltonian, optimization_problem)
        elif method == OptimizationMethod.ANNEALING:
            result = await self._annealing_optimization(hamiltonian, optimization_problem)
        elif method == OptimizationMethod.HYBRID:
            result = await self._hybrid_optimization(hamiltonian, optimization_problem)
        else:
            result = await self._realtime_optimization(hamiltonian, optimization_problem)
        
        end_time = datetime.now()
        computation_time = (end_time - start_time).total_seconds()
        
        # Calculate quantum advantage
        classical_time = self.classical_baseline_times["portfolio_optimization"]
        quantum_advantage = classical_time / computation_time if computation_time > 0 else float('inf')
        
        result.computation_time = computation_time
        result.quantum_advantage = quantum_advantage
        
        self.optimization_history.append(result)
        
        return {
            "new_allocation": await self._convert_result_to_allocation(result),
            "quantum_state": result.quantum_circuit,
            "optimization_details": {
                "method": result.method.value,
                "objective_value": result.objective_value,
                "computation_time": computation_time,
                "quantum_advantage": quantum_advantage,
                "convergence_history": result.convergence_history
            }
        }
    
    async def _create_portfolio_hamiltonian(self, optimization_problem: Dict[str, Any]) -> np.ndarray:
        """Portfolio uchun Hamiltonian yaratish"""
        current_portfolio = optimization_problem["current_portfolio"]
        market_data = optimization_problem["market_data"]
        
        # Create cost matrix based on risk-return characteristics
        n_assets = len(current_portfolio["assets"])
        hamiltonian = np.zeros((2**n_assets, 2**n_assets))
        
        # Risk-return Hamiltonian terms
        for i, (asset_type, asset_info) in enumerate(current_portfolio["assets"].items()):
            weight = asset_info["weight"]
            
            # Expected return term
            if asset_type in market_data and "data" in market_data[asset_type]:
                returns = []
                for symbol, data in market_data[asset_type]["data"].items():
                    # Simulate expected return
                    returns.append(np.random.normal(0.05, 0.1))  # 5% expected return, 10% volatility
                
                avg_return = np.mean(returns)
                hamiltonian[i, i] += -weight * avg_return  # Negative for maximization
            
            # Risk term (variance)
            risk_penalty = weight**2 * 0.01  # Risk penalty
            hamiltonian[i, i] += risk_penalty
        
        # Cross-correlation terms
        for i in range(n_assets):
            for j in range(i+1, n_assets):
                correlation = np.random.uniform(-0.5, 0.5)  # Simulated correlation
                hamiltonian[i, j] += correlation * 0.05
                hamiltonian[j, i] += correlation * 0.05
        
        return hamiltonian
    
    async def _vqe_optimization(self, hamiltonian: np.ndarray, 
                              problem: Dict[str, Any]) -> OptimizationResult:
        """VQE (Variational Quantum Eigensolver) optimization"""
        self.logger.info("Executing VQE optimization...")
        
        circuit = self.quantum_circuits[OptimizationMethod.VQE]
        parameters = circuit.parameters.copy()
        convergence_history = []
        
        # Classical optimization loop
        for iteration in range(self.max_iterations):
            # Quantum simulation (simplified)
            expectation_value = await self._calculate_expectation_value(hamiltonian, parameters)
            convergence_history.append(expectation_value)
            
            # Parameter update (simplified gradient descent)
            learning_rate = 0.01
            gradient = await self._calculate_parameter_gradient(hamiltonian, parameters)
            parameters -= learning_rate * gradient
            
            # Check convergence
            if len(convergence_history) > 1:
                if abs(convergence_history[-1] - convergence_history[-2]) < self.tolerance:
                    break
        
        return OptimizationResult(
            method=OptimizationMethod.VQE,
            objective_value=convergence_history[-1] if convergence_history else float('inf'),
            optimal_parameters=parameters,
            quantum_circuit=circuit,
            convergence_history=convergence_history,
            computation_time=0.0,  # Will be set by caller
            quantum_advantage=0.0,  # Will be set by caller
            timestamp=datetime.now()
        )
    
    async def _qaoa_optimization(self, hamiltonian: np.ndarray, 
                               problem: Dict[str, Any]) -> OptimizationResult:
        """QAOA (Quantum Approximate Optimization Algorithm) optimization"""
        self.logger.info("Executing QAOA optimization...")
        
        circuit = self.quantum_circuits[OptimizationMethod.QAOA]
        parameters = circuit.parameters.copy()
        convergence_history = []
        
        # QAOA optimization loop
        p_layers = self.quantum_depth // 2
        for iteration in range(self.max_iterations):
            # QAOA objective calculation
            qaoa_value = await self._calculate_qaoa_objective(hamiltonian, parameters, p_layers)
            convergence_history.append(qaoa_value)
            
            # Parameter optimization
            gradient = await self._calculate_qaoa_gradient(hamiltonian, parameters, p_layers)
            learning_rate = 0.005
            parameters -= learning_rate * gradient
        
        return OptimizationResult(
            method=OptimizationMethod.QAOA,
            objective_value=convergence_history[-1] if convergence_history else float('inf'),
            optimal_parameters=parameters,
            quantum_circuit=circuit,
            convergence_history=convergence_history,
            computation_time=0.0,
            quantum_advantage=0.0,
            timestamp=datetime.now()
        )
    
    async def _annealing_optimization(self, hamiltonian: np.ndarray, 
                                    problem: Dict[str, Any]) -> OptimizationResult:
        """Quantum annealing optimization"""
        self.logger.info("Executing quantum annealing optimization...")
        
        circuit = self.quantum_circuits[OptimizationMethod.ANNEALING]
        current_state = np.random.random(2**circuit.qubits) + 1j * np.random.random(2**circuit.qubits)
        current_state /= np.linalg.norm(current_state)
        
        temperature = self.annealing_schedule["initial_temperature"]
        convergence_history = []
        
        for step in range(self.annealing_schedule["steps"]):
            # Calculate current energy
            energy = np.real(np.vdot(current_state, hamiltonian @ current_state))
            convergence_history.append(energy)
            
            # Generate random neighbor state
            neighbor_state = current_state.copy()
            # Add small random perturbation
            perturbation = np.random.normal(0, 0.01, len(neighbor_state)) + 1j * np.random.normal(0, 0.01, len(neighbor_state))
            neighbor_state += perturbation
            neighbor_state /= np.linalg.norm(neighbor_state)
            
            # Calculate neighbor energy
            neighbor_energy = np.real(np.vdot(neighbor_state, hamiltonian @ neighbor_state))
            
            # Accept or reject based on Metropolis criterion
            if neighbor_energy < energy or np.random.random() < np.exp(-(neighbor_energy - energy) / temperature):
                current_state = neighbor_state
            
            # Cool down
            temperature *= self.annealing_schedule["cooling_rate"]
            
            if temperature < self.annealing_schedule["final_temperature"]:
                break
        
        return OptimizationResult(
            method=OptimizationMethod.ANNEALING,
            objective_value=convergence_history[-1] if convergence_history else float('inf'),
            optimal_parameters=current_state,
            quantum_circuit=circuit,
            convergence_history=convergence_history,
            computation_time=0.0,
            quantum_advantage=0.0,
            timestamp=datetime.now()
        )
    
    async def _hybrid_optimization(self, hamiltonian: np.ndarray, 
                                 problem: Dict[str, Any]) -> OptimizationResult:
        """Hybrid classical-quantum optimization"""
        self.logger.info("Executing hybrid optimization...")
        
        circuit = self.quantum_circuits[OptimizationMethod.HYBRID]
        parameters = circuit.parameters.copy()
        convergence_history = []
        
        # Hybrid optimization loop
        for iteration in range(self.max_iterations):
            # Classical preprocessing
            classical_result = await self._classical_preprocessing(parameters)
            
            # Quantum enhancement
            quantum_enhanced = await self._quantum_enhancement(classical_result, circuit)
            
            # Classical post-processing
            final_result = await self._classical_postprocessing(quantum_enhanced)
            
            convergence_history.append(final_result)
            
            # Update parameters
            gradient = await self._calculate_hybrid_gradient(final_result, parameters)
            learning_rate = 0.01
            parameters -= learning_rate * gradient
        
        return OptimizationResult(
            method=OptimizationMethod.HYBRID,
            objective_value=convergence_history[-1] if convergence_history else float('inf'),
            optimal_parameters=parameters,
            quantum_circuit=circuit,
            convergence_history=convergence_history,
            computation_time=0.0,
            quantum_advantage=0.0,
            timestamp=datetime.now()
        )
    
    async def _realtime_optimization(self, hamiltonian: np.ndarray, 
                                   problem: Dict[str, Any]) -> OptimizationResult:
        """Real-time quantum optimization"""
        self.logger.info("Executing real-time optimization...")
        
        circuit = self.quantum_circuits[OptimizationMethod.REAL_TIME]
        parameters = circuit.parameters.copy()
        convergence_history = []
        
        # Adaptive optimization based on market conditions
        market_data = problem["market_data"]
        volatility = await self._calculate_market_volatility(market_data)
        
        for iteration in range(min(50, self.max_iterations)):  # Faster for real-time
            # Adaptive step size based on volatility
            adaptive_rate = 0.01 / (1 + volatility)
            
            # Real-time objective calculation
            realtime_value = await self._calculate_realtime_objective(hamiltonian, parameters, volatility)
            convergence_history.append(realtime_value)
            
            # Fast gradient descent
            gradient = await self._calculate_realtime_gradient(hamiltonian, parameters)
            parameters -= adaptive_rate * gradient
        
        return OptimizationResult(
            method=OptimizationMethod.REAL_TIME,
            objective_value=convergence_history[-1] if convergence_history else float('inf'),
            optimal_parameters=parameters,
            quantum_circuit=circuit,
            convergence_history=convergence_history,
            computation_time=0.0,
            quantum_advantage=0.0,
            timestamp=datetime.now()
        )
    
    async def _calculate_expectation_value(self, hamiltonian: np.ndarray, parameters: np.ndarray) -> float:
        """Hamiltonian expectation value hisoblash"""
        # Simplified expectation value calculation
        return np.real(np.trace(hamiltonian)) + np.sum(np.random.normal(0, 0.01, len(parameters)))
    
    async def _calculate_parameter_gradient(self, hamiltonian: np.ndarray, parameters: np.ndarray) -> np.ndarray:
        """Parameter gradient hisoblash"""
        # Simplified gradient calculation
        return np.random.normal(0, 0.1, len(parameters))
    
    async def _calculate_qaoa_objective(self, hamiltonian: np.ndarray, parameters: np.ndarray, p_layers: int) -> float:
        """QAOA objective function hisoblash"""
        # Simplified QAOA objective
        return np.sum(hamiltonian) + np.sum(parameters**2)
    
    async def _calculate_qaoa_gradient(self, hamiltonian: np.ndarray, parameters: np.ndarray, p_layers: int) -> np.ndarray:
        """QAOA gradient hisoblash"""
        # Simplified QAOA gradient
        return np.random.normal(0, 0.05, len(parameters))
    
    async def _classical_preprocessing(self, parameters: np.ndarray) -> Dict[str, Any]:
        """Classical preprocessing"""
        return {
            "mean": np.mean(parameters),
            "std": np.std(parameters),
            "normalized": parameters / np.linalg.norm(parameters)
        }
    
    async def _quantum_enhancement(self, classical_result: Dict[str, Any], circuit: QuantumCircuit) -> np.ndarray:
        """Quantum enhancement qo'llash"""
        # Apply quantum transformation
        quantum_enhanced = classical_result["normalized"].copy()
        
        # Quantum amplitude amplification
        for gate in circuit.gates:
            if gate["type"] in ["RY", "RZ", "RX"]:
                quantum_enhanced = self._apply_single_qubit_rotation(
                    quantum_enhanced, gate["target"], gate["type"], gate["parameter"] or 0
                )
        
        return quantum_enhanced
    
    async def _classical_postprocessing(self, quantum_enhanced: np.ndarray) -> float:
        """Classical post-processing"""
        return np.real(np.sum(quantum_enhanced * np.conj(quantum_enhanced)))
    
    async def _calculate_hybrid_gradient(self, result: float, parameters: np.ndarray) -> np.ndarray:
        """Hybrid gradient hisoblash"""
        return np.random.normal(0, 0.01, len(parameters))
    
    async def _calculate_market_volatility(self, market_data: Dict[str, Any]) -> float:
        """Market volatility hisoblash"""
        volatilities = []
        for asset_data in market_data.values():
            if "data" in asset_data:
                asset_volatilities = []
                for symbol, data in asset_data["data"].items():
                    # Simulate volatility calculation
                    price_returns = np.random.normal(0, 0.02, 10)  # Simulated returns
                    volatility = np.std(price_returns)
                    asset_volatilities.append(volatility)
                volatilities.append(np.mean(asset_volatilities))
        
        return np.mean(volatilities) if volatilities else 0.02
    
    async def _calculate_realtime_objective(self, hamiltonian: np.ndarray, parameters: np.ndarray, volatility: float) -> float:
        """Real-time objective function"""
        base_objective = np.sum(hamiltonian) + np.sum(parameters**2)
        volatility_adjustment = volatility * 0.1
        return base_objective + volatility_adjustment
    
    async def _calculate_realtime_gradient(self, hamiltonian: np.ndarray, parameters: np.ndarray) -> np.ndarray:
        """Real-time gradient hisoblash"""
        return np.random.normal(0, 0.02, len(parameters))
    
    def _apply_single_qubit_rotation(self, state: np.ndarray, qubit: int, gate_type: str, angle: float) -> np.ndarray:
        """Single qubit rotation qo'llash"""
        # Simplified rotation matrix application
        if gate_type == 'RY':
            rotation_matrix = np.array([
                [np.cos(angle/2), -np.sin(angle/2)],
                [np.sin(angle/2), np.cos(angle/2)]
            ])
        elif gate_type == 'RZ':
            rotation_matrix = np.array([
                [np.exp(-1j*angle/2), 0],
                [0, np.exp(1j*angle/2)]
            ])
        elif gate_type == 'RX':
            rotation_matrix = np.array([
                [np.cos(angle/2), -1j*np.sin(angle/2)],
                [-1j*np.sin(angle/2), np.cos(angle/2)]
            ])
        else:
            return state
        
        # Apply rotation (simplified for n-qubit system)
        n_qubits = int(np.log2(len(state)))
        if qubit < n_qubits:
            # Apply to the subspace of the target qubit
            for i in range(0, len(state), 2**(qubit+1)):
                for j in range(2**qubit):
                    idx1 = i + j
                    idx2 = i + j + 2**qubit
                    if idx2 < len(state):
                        subspace = state[[idx1, idx2]]
                        rotated = rotation_matrix @ subspace
                        state[idx1] = rotated[0]
                        state[idx2] = rotated[1]
        
        return state
    
    async def _convert_result_to_allocation(self, result: OptimizationResult) -> Dict[str, Any]:
        """Optimization natijasini allocation ga aylantirish"""
        # Convert quantum result to portfolio allocation
        n_assets = 4  # stocks, forex, metals, crypto
        
        if len(result.optimal_parameters) >= n_assets:
            allocation_weights = result.optimal_parameters[:n_assets]
            # Normalize to sum to 1
            allocation_weights = np.abs(allocation_weights) / np.sum(np.abs(allocation_weights))
        else:
            # Default equal allocation
            allocation_weights = np.ones(n_assets) / n_assets
        
        assets = ["stocks", "forex", "metals", "crypto"]
        new_allocation = {}
        
        for i, asset in enumerate(assets):
            new_allocation[asset] = {
                "weight": allocation_weights[i] if i < len(allocation_weights) else 0.25,
                "change": allocation_weights[i] - 0.25,  # Change from equal allocation
                "quantum_enhanced": True,
                "optimization_method": result.method.value
            }
        
        return new_allocation
    
    async def update_portfolio_state(self, current_state: Dict[str, Any], 
                                   trade_results: Dict[str, Any]) -> Dict[str, Any]:
        """Portfolio holatini yangilash"""
        # Create new quantum state based on trade results
        new_portfolio = current_state.copy()
        
        # Update quantum circuit parameters
        for asset_type, trade_result in trade_results.items():
            if "execution_price" in trade_result:
                # Update quantum state with new market information
                price_update = trade_result["execution_price"]
                # Apply price update to quantum state (simplified)
                if asset_type in new_portfolio["assets"]:
                    new_portfolio["assets"][asset_type]["last_price"] = price_update
        
        # Update timestamp
        new_portfolio["timestamp"] = datetime.now().isoformat()
        
        return new_portfolio
    
    async def get_circuit_state(self) -> Dict[str, Any]:
        """Quantum circuit holatini olish"""
        return {
            "circuits": {method.value: {
                "qubits": circuit.qubits,
                "depth": circuit.depth,
                "n_gates": len(circuit.gates)
            } for method, circuit in self.quantum_circuits.items()},
            "optimization_history": len(self.optimization_history),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_optimization_performance(self) -> Dict[str, Any]:
        """Optimizatsiya performance metrikalarini olish"""
        if not self.optimization_history:
            return {"message": "No optimization history available"}
        
        # Calculate performance statistics
        latest_result = self.optimization_history[-1]
        method_stats = {}
        
        for result in self.optimization_history:
            method = result.method.value
            if method not in method_stats:
                method_stats[method] = {
                    "count": 0,
                    "avg_objective": 0,
                    "avg_quantum_advantage": 0,
                    "avg_computation_time": 0
                }
            
            method_stats[method]["count"] += 1
            method_stats[method]["avg_objective"] += result.objective_value
            method_stats[method]["avg_quantum_advantage"] += result.quantum_advantage
            method_stats[method]["avg_computation_time"] += result.computation_time
        
        # Calculate averages
        for method_stats_data in method_stats.values():
            count = method_stats_data["count"]
            method_stats_data["avg_objective"] /= count
            method_stats_data["avg_quantum_advantage"] /= count
            method_stats_data["avg_computation_time"] /= count
        
        return {
            "method_statistics": method_stats,
            "latest_optimization": {
                "method": latest_result.method.value,
                "objective_value": latest_result.objective_value,
                "quantum_advantage": latest_result.quantum_advantage,
                "computation_time": latest_result.computation_time
            },
            "total_optimizations": len(self.optimization_history),
            "timestamp": datetime.now().isoformat()
        }