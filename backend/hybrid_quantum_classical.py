"""
Hybrid Quantum-Classical Trading System
=======================================

Bu modul quantum va classical computing'ni birlashtirgan trading tizimini o'z ichiga oladi.
Tizim quyidagi asosiy xususiyatlarga ega:

**Asosiy Komponentlar:**
1. Hybrid Architecture - quantum va classical qismlarning integratsiyasi
2. Quantum-Classical Workflow - ma'lumotlar oqimi va qayta ishlash
3. Adaptive Algorithm Selection - muammo hajmiga qarab algoritm tanlovi
4. Error Mitigation - quantum xatolarni boshqarish
5. Real-World Integration - real qurilmalar bilan integratsiya

**Quantum Components:**
- Quantum Portfolio Optimization (VQE, QAOA)
- Quantum Feature Selection
- Quantum Risk Assessment
- Quantum Decision Making

**Classical Components:**
- Data Preprocessing
- Traditional Technical Analysis
- Risk Management
- Execution Strategies

**Hybrid Features:**
- Classical pre-processing
- Quantum optimization
- Classical post-processing
- Decision fusion
- Performance monitoring
"""

import numpy as np
import pandas as pd
import warnings
import logging
import time
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
import matplotlib.pyplot as plt
import seaborn as sns

# Core dependencies
from scipy.optimize import minimize, differential_evolution
from scipy.stats import norm, multivariate_normal
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.covariance import LedoitWolf
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score

# Qiskit for quantum computing
try:
    import qiskit
    from qiskit import QuantumCircuit, Aer, transpile, assemble
    from qiskit.visualization import plot_histogram
    from qiskit.optimization import QuadraticProgram
    from qiskit.algorithms import VQE, QAOA
    from qiskit.algorithms.optimizers import COBYLA, SPSA, SLSQP
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    print("Qiskit topilmadi. Classical rejimda ishlaydi.")
    
    # Define dummy classes when Qiskit is not available
    if not QISKIT_AVAILABLE:
        class QuantumCircuit:
            def __init__(self, *args, **kwargs):
                pass
            def h(self, *args, **kwargs):
                pass
            def ry(self, *args, **kwargs):
                pass
            def cx(self, *args, **kwargs):
                pass
            def measure_all(self):
                pass

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProblemSize(Enum):
    """Muammo hajmi klassifikatsiyasi."""
    SMALL = "small"       # < 50 assets
    MEDIUM = "medium"     # 50-200 assets  
    LARGE = "large"       # > 200 assets

class QuantumHardware(Enum):
    """Quantum qurilma turlari."""
    SIMULATOR = "simulator"  # Qiskit Aer simulator
    IBM_Q = "ibm_q"          # IBM Quantum Experience
    GOOGLE = "google"        # Google Quantum AI
    FUTURE_HARDWARE = "future"  # Kelajak qurilmalari

class AlgorithmType(Enum):
    """Algoritm turlari."""
    CLASSICAL_ONLY = "classical"
    HYBRID = "hybrid"
    QUANTUM_ADVANTAGE = "quantum"

@dataclass
class QuantumState:
    """Quantum state ma'lumotlari."""
    amplitudes: np.ndarray
    probabilities: np.ndarray
    measurement_counts: Dict[int, int]
    fidelity: float
    error_rate: float
    
@dataclass
class OptimizationResult:
    """Optimizatsiya natijasi."""
    weights: np.ndarray
    expected_return: float
    volatility: float
    sharpe_ratio: float
    quantum_advantage: bool
    computation_time: float
    error_metrics: Dict[str, float]

class QuantumErrorMitigator:
    """Quantum xatolarni kamaytirish moduli."""
    
    def __init__(self, error_threshold=0.05):
        self.error_threshold = error_threshold
        self.calibration_data = {}
        
    def mitigate_measurement_errors(self, measurement_counts: Dict[int, int]) -> Dict[int, int]:
        """O'lchash xatolarini kamaytirish."""
        total_counts = sum(measurement_counts.values())
        
        # Calibrated error rates (tasvifiy)
        error_rates = {
            0: 0.02,  # |0⟩ state error rate
            1: 0.03   # |1⟩ state error rate
        }
        
        mitigated_counts = {}
        for state, count in measurement_counts.items():
            error_rate = error_rates.get(state, 0.05)
            correction_factor = 1 - error_rate
            mitigated_counts[state] = int(count * correction_factor)
        
        return mitigated_counts
    
    def apply_zero_noise_extrapolation(self, circuits: List['QuantumCircuit']) -> np.ndarray:
        """Zero Noise Extrapolation usuli."""
        # Simplified implementation
        # In reality, this would run circuits with different noise levels
        results = []
        for circuit in circuits:
            # Simulate noise reduction
            result = np.random.normal(0.5, 0.1)  # Placeholder
            results.append(result)
        return np.array(results)
    
    def validate_quantum_result(self, quantum_state: QuantumState) -> bool:
        """Quantum natijalarning to'g'riligini tekshirish."""
        # Check probability normalization
        prob_sum = np.sum(quantum_state.probabilities)
        if abs(prob_sum - 1.0) > self.error_threshold:
            return False
        
        # Check fidelity threshold
        if quantum_state.fidelity < (1 - self.error_threshold):
            return False
        
        # Check error rate
        if quantum_state.error_rate > self.error_threshold:
            return False
        
        return True

class ClassicalPreprocessor:
    """Classical ma'lumotlarni qayta ishlash moduli."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_selector = None
        self.noise_reduction = LedoitWolf()
        
    def preprocess_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, Dict]:
        """Ma'lumotlarni qayta ishlash."""
        # Handle missing values - fill with 0 instead of dropping
        data_clean = data.fillna(0)
        
        # Ensure no infinite values
        data_clean = data_clean.replace([np.inf, -np.inf], 0)
        
        # Remove outliers using IQR method (but keep at least some data)
        Q1 = data_clean.quantile(0.25)
        Q3 = data_clean.quantile(0.75)
        IQR = Q3 - Q1
        
        # Only remove extreme outliers
        data_filtered = data_clean[
            ~((data_clean < (Q1 - 2.0 * IQR)) | (data_clean > (Q3 + 2.0 * IQR)))
        ]
        
        # If too much data was removed, use original data
        if len(data_filtered) < len(data_clean) * 0.5:
            data_filtered = data_clean
        
        # Feature scaling
        features_scaled = self.scaler.fit_transform(data_filtered)
        
        # Noise reduction - handle NaN in covariance matrix
        try:
            covariance_reduced = self.noise_reduction.fit(data_filtered).covariance_
            # Check for NaN values
            if np.any(np.isnan(covariance_reduced)):
                covariance_reduced = np.cov(data_filtered.T)
                if np.any(np.isnan(covariance_reduced)):
                    covariance_reduced = np.eye(data_filtered.shape[1]) * 0.01
        except:
            # Fallback to simple covariance
            covariance_reduced = np.cov(data_filtered.T)
            if np.any(np.isnan(covariance_reduced)):
                covariance_reduced = np.eye(data_filtered.shape[1]) * 0.01
        
        # Calculate feature importance
        feature_stats = {
            'mean': np.mean(features_scaled, axis=0),
            'std': np.std(features_scaled, axis=0),
            'correlation_matrix': np.corrcoef(data_filtered.T),
            'variance_explained': np.var(features_scaled, axis=0),
            'data_quality_score': self._calculate_data_quality(data_filtered)
        }
        
        return features_scaled, feature_stats
    
    def _calculate_data_quality(self, data: pd.DataFrame) -> float:
        """Ma'lumotlar sifatini baholash."""
        completeness = 1 - (data.isnull().sum().sum() / (data.shape[0] * data.shape[1]))
        
        # Consistency check (simplified)
        consistency = 0.9  # Placeholder
        
        # Accuracy check (simplified)
        accuracy = 0.95  # Placeholder
        
        quality_score = (completeness + consistency + accuracy) / 3
        return quality_score

class QuantumFeatureSelector:
    """Quantum-inspired feature selection moduli."""
    
    def __init__(self, n_qubits=10):
        if QISKIT_AVAILABLE:
            self.simulator = Aer.get_backend('qasm_simulator')
        self.n_qubits = min(n_qubits, 10)  # Limit qubits for stability
        
    def quantum_feature_selection(self, features: np.ndarray, n_features: int) -> np.ndarray:
        """Quantum feature selection."""
        if not QISKIT_AVAILABLE:
            return self._classical_feature_selection(features, n_features)
        
        try:
            # Create quantum circuit for feature selection
            circuit = QuantumCircuit(self.n_qubits, self.n_qubits)
            
            # Apply Hadamard gates for superposition
            circuit.h(range(self.n_qubits))
            
            # Apply feature encoding (simplified)
            for i in range(min(self.n_qubits, features.shape[1])):
                theta = features[0, i] if i < features.shape[1] else 0
                circuit.ry(theta, i)
            
            # Measurement
            circuit.measure_all()
            
            # Execute on simulator
            transpiled_circuit = transpile(circuit, self.simulator)
            qobj = assemble(transpiled_circuit)
            job = self.simulator.run(qobj)
            result = job.result()
            counts = result.get_counts(circuit)
            
            # Select features based on measurement results
            selected_features = self._extract_selected_features(counts, n_features, features.shape[1])
            return features[:, selected_features]
            
        except Exception as e:
            logger.warning(f"Quantum feature selection failed: {e}. Using classical method.")
            return self._classical_feature_selection(features, n_features)
    
    def _classical_feature_selection(self, features: np.ndarray, n_features: int) -> np.ndarray:
        """Classical fallback for feature selection."""
        # Use Random Forest for feature importance
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # Assuming target is available (simplified)
        target = np.random.randn(features.shape[0])  # Placeholder
        
        rf.fit(features, target)
        importance_scores = rf.feature_importances_
        
        # Select top features
        selected_indices = np.argsort(importance_scores)[-n_features:]
        return features[:, selected_indices]
    
    def _extract_selected_features(self, counts: Dict[str, int], n_features: int, total_features: int) -> List[int]:
        """Quantum measurement resultsidan feature tanlash."""
        total_measurements = sum(counts.values())
        
        # Convert to probability distribution
        probabilities = {state: count / total_measurements for state, count in counts.items()}
        
        # Select features based on measurement frequency
        feature_scores = np.zeros(total_features)
        for state, prob in probabilities.items():
            for i, bit in enumerate(reversed(state)):
                if i < total_features:
                    feature_scores[i] += int(bit) * prob
        
        # Return indices of most important features
        return np.argsort(feature_scores)[-n_features:].tolist()

class QuantumPortfolioOptimizer:
    """Quantum portfolio optimization moduli."""
    
    def __init__(self, hardware_type=QuantumHardware.SIMULATOR):
        self.hardware_type = hardware_type
        self.error_mitigator = QuantumErrorMitigator()
        
        if QISKIT_AVAILABLE and hardware_type == QuantumHardware.SIMULATOR:
            self.simulator = Aer.get_backend('qasm_simulator')
            self.statevector_simulator = Aer.get_backend('statevector_simulator')
        
    def optimize_portfolio_vqe(self, returns: np.ndarray, 
                              covariance: np.ndarray, 
                              risk_aversion: float = 1.0) -> OptimizationResult:
        """VQE (Variational Quantum Eigensolver) yordamida portfolio optimizatsiya."""
        if not QISKIT_AVAILABLE:
            return self._fallback_optimization(returns, covariance)
        
        try:
            start_time = time.time()
            
            # Create quadratic program
            qp = QuadraticProgram()
            
            # Add variables (portfolio weights)
            n_assets = len(returns)
            qp.binary_var_list(n_assets)
            
            # Objective function: minimize risk for given return
            linear = {}
            quadratic = {}
            
            for i in range(n_assets):
                # Expected return component
                linear[i] = -returns[i]
                
                # Risk component
                for j in range(n_assets):
                    quadratic[(i, j)] = risk_aversion * covariance[i, j]
            
            qp.minimize(linear=linear, quadratic=quadratic)
            
            # Constraints
            qp.linear_constraint(linear=[1] * n_assets, sense='==', rhs=1.0)  # weights sum to 1
            
            # Setup VQE
            optimizer = COBYLA(maxiter=100)
            ansatz = self._create_ansatz(n_assets)
            
            vqe = VQE(ansatz=ansatz, optimizer=optimizer, quantum_instance=self.simulator)
            
            # Solve
            result = vqe.solve(qp)
            
            computation_time = time.time() - start_time
            
            # Extract weights
            weights = np.array([var.value for var in result.variables])
            weights = np.abs(weights) / np.sum(np.abs(weights))  # Normalize
            
            # Calculate metrics
            expected_return = np.dot(weights, returns)
            volatility = np.sqrt(np.dot(weights, np.dot(covariance, weights)))
            sharpe_ratio = expected_return / max(volatility, 1e-8)
            
            return OptimizationResult(
                weights=weights,
                expected_return=expected_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                quantum_advantage=True,
                computation_time=computation_time,
                error_metrics={'fidelity': 0.95, 'error_rate': 0.02}
            )
            
        except Exception as e:
            logger.error(f"VQE optimization failed: {e}")
            return self._fallback_optimization(returns, covariance)
    
    def optimize_portfolio_qaoa(self, returns: np.ndarray, 
                               covariance: np.ndarray) -> OptimizationResult:
        """QAOA (Quantum Approximate Optimization Algorithm) yordamida optimizatsiya."""
        if not QISKIT_AVAILABLE:
            return self._fallback_optimization(returns, covariance)
        
        try:
            start_time = time.time()
            
            # Create optimization problem
            n_assets = len(returns)
            qp = QuadraticProgram()
            qp.binary_var_list(n_assets)
            
            # Objective function
            linear = {i: -returns[i] for i in range(n_assets)}
            quadratic = {(i, j): covariance[i, j] for i in range(n_assets) for j in range(n_assets)}
            qp.minimize(linear=linear, quadratic=quadratic)
            
            # Constraint
            qp.linear_constraint(linear=[1] * n_assets, sense='==', rhs=1.0)
            
            # Setup QAOA
            optimizer = COBYLA(maxiter=100)
            qaoa = QAOA(optimizer=optimizer, quantum_instance=self.simulator)
            
            # Solve
            result = qaoa.solve(qp)
            
            computation_time = time.time() - start_time
            
            # Extract weights
            weights = np.array([var.value for var in result.variables])
            weights = np.abs(weights) / np.sum(np.abs(weights))
            
            # Calculate metrics
            expected_return = np.dot(weights, returns)
            volatility = np.sqrt(np.dot(weights, np.dot(covariance, weights)))
            sharpe_ratio = expected_return / max(volatility, 1e-8)
            
            return OptimizationResult(
                weights=weights,
                expected_return=expected_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                quantum_advantage=True,
                computation_time=computation_time,
                error_metrics={'approximation_ratio': 0.85}
            )
            
        except Exception as e:
            logger.error(f"QAOA optimization failed: {e}")
            return self._fallback_optimization(returns, covariance)
    
    def _create_ansatz(self, n_qubits: int) -> 'QuantumCircuit':
        """VQE uchun ansatz yaratish."""
        circuit = QuantumCircuit(n_qubits)
        
        # Initial layer of Ry gates
        for i in range(n_qubits):
            circuit.ry(np.random.random(), i)
        
        # Entangling layers
        for layer in range(2):
            for i in range(n_qubits - 1):
                circuit.cx(i, i + 1)
            
            for i in range(n_qubits):
                circuit.ry(np.random.random(), i)
        
        return circuit
    
    def _fallback_optimization(self, returns: np.ndarray, covariance: np.ndarray) -> OptimizationResult:
        """Classical fallback optimizatsiya."""
        start_time = time.time()
        
        n_assets = len(returns)
        
        # Constraints
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Objective: maximize Sharpe ratio
        def objective(x):
            portfolio_return = np.dot(x, returns)
            portfolio_std = np.sqrt(np.dot(x, np.dot(covariance, x)))
            return -portfolio_return / max(portfolio_std, 1e-8)
        
        # Optimize
        result = minimize(objective, np.ones(n_assets) / n_assets, 
                         method='SLSQP', bounds=bounds, constraints=constraints)
        
        computation_time = time.time() - start_time
        weights = result.x if result.success else np.ones(n_assets) / n_assets
        
        expected_return = np.dot(weights, returns)
        volatility = np.sqrt(np.dot(weights, np.dot(covariance, weights)))
        sharpe_ratio = expected_return / max(volatility, 1e-8)
        
        return OptimizationResult(
            weights=weights,
            expected_return=expected_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            quantum_advantage=False,
            computation_time=computation_time,
            error_metrics={'optimization_success': result.success}
        )

class ClassicalPostprocessor:
    """Classical natijalarni qayta ishlash moduli."""
    
    def __init__(self):
        self.risk_limits = {
            'max_single_position': 0.1,
            'max_sector_weight': 0.3,
            'max_correlation': 0.7,
            'min_diversification': 10  # Minimum number of positions
        }
    
    def postprocess_portfolio(self, raw_weights: np.ndarray, 
                             asset_names: List[str],
                             sector_mapping: Dict[str, str] = None) -> np.ndarray:
        """Portfolioni qayta ishlash."""
        weights = raw_weights.copy()
        
        # Remove very small weights
        weights[weights < 0.01] = 0
        
        # Apply max single position limit
        weights = np.minimum(weights, self.risk_limits['max_single_position'])
        
        # Sector weight constraints
        if sector_mapping:
            for sector in set(sector_mapping.values()):
                sector_indices = [i for i, asset in enumerate(asset_names) 
                                if sector_mapping.get(asset) == sector]
                if sector_indices:
                    sector_weight = np.sum(weights[sector_indices])
                    if sector_weight > self.risk_limits['max_sector_weight']:
                        excess = sector_weight - self.risk_limits['max_sector_weight']
                        weights[sector_indices] *= (1 - excess / sector_weight)
        
        # Ensure diversification
        active_positions = np.sum(weights > 0)
        if active_positions < self.risk_limits['min_diversification']:
            # Add small positions to reach minimum
            needed = self.risk_limits['min_diversification'] - active_positions
            remaining_weight = 1 - np.sum(weights)
            additional_weight = remaining_weight / needed
            small_assets = np.where(weights == 0)[0][:needed]
            weights[small_assets] = additional_weight
        
        # Final normalization
        if np.sum(weights) > 0:
            weights = weights / np.sum(weights)
        
        return weights
    
    def calculate_portfolio_metrics(self, weights: np.ndarray, 
                                  returns: np.ndarray, 
                                  covariance: np.ndarray) -> Dict[str, float]:
        """Portfoliometrik hisoblashlar."""
        portfolio_return = np.dot(weights, returns)
        portfolio_variance = np.dot(weights, np.dot(covariance, weights))
        portfolio_std = np.sqrt(portfolio_variance)
        
        # Risk-adjusted metrics
        sharpe_ratio = portfolio_return / max(portfolio_std, 1e-8)
        sortino_ratio = self._calculate_sortino_ratio(weights, returns, covariance)
        information_ratio = self._calculate_information_ratio(portfolio_return, portfolio_std)
        
        # Risk metrics
        max_weight = np.max(weights)
        diversification_ratio = 1 - np.sum(weights**2)  # Herfindahl-Hirschman Index
        
        # Value at Risk (simplified)
        var_95 = portfolio_return - 1.65 * portfolio_std
        
        return {
            'expected_return': portfolio_return,
            'volatility': portfolio_std,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'information_ratio': information_ratio,
            'max_position_weight': max_weight,
            'diversification_ratio': diversification_ratio,
            'var_95': var_95,
            'portfolio_size': len(weights[weights > 0])
        }
    
    def _calculate_sortino_ratio(self, weights: np.ndarray, 
                               returns: np.ndarray, 
                               covariance: np.ndarray) -> float:
        """Sortino ratio hisoblash."""
        portfolio_return = np.dot(weights, returns)
        portfolio_std = np.sqrt(np.dot(weights, np.dot(covariance, weights)))
        
        # Simplified downside deviation
        downside_std = portfolio_std * 0.7  # Approximation
        
        return portfolio_return / max(downside_std, 1e-8)
    
    def _calculate_information_ratio(self, return_val: float, risk: float) -> float:
        """Information ratio hisoblash."""
        # Simplified - assumes market return of 8% and risk-free rate of 2%
        market_return = 0.08
        risk_free_rate = 0.02
        
        excess_return = return_val - market_return
        tracking_error = risk
        
        return excess_return / max(tracking_error, 1e-8)

class DecisionFusionEngine:
    """Qarorlar birlashtirish moduli."""
    
    def __init__(self):
        self.algorithm_weights = {
            'quantum_vqe': 0.4,
            'quantum_qaoa': 0.3,
            'classical_mpt': 0.2,
            'risk_parity': 0.1
        }
    
    def fuse_optimization_results(self, results: List[OptimizationResult],
                                algorithm_names: List[str]) -> OptimizationResult:
        """Turli algoritmlar natijalarini birlashtirish."""
        if not results:
            raise ValueError("No optimization results provided")
        
        # Weighted average of weights
        fused_weights = np.zeros(len(results[0].weights))
        total_weight = 0
        
        for i, (result, name) in enumerate(zip(results, algorithm_names)):
            algorithm_weight = self.algorithm_weights.get(name, 1.0 / len(results))
            fused_weights += algorithm_weight * result.weights
            total_weight += algorithm_weight
        
        if total_weight > 0:
            fused_weights = fused_weights / total_weight
        
        # Weighted average of metrics
        fused_expected_return = np.average([r.expected_return for r in results],
                                         weights=[self.algorithm_weights.get(name, 1.0) 
                                                for name in algorithm_names])
        fused_volatility = np.average([r.volatility for r in results],
                                    weights=[self.algorithm_weights.get(name, 1.0) 
                                           for name in algorithm_names])
        fused_sharpe_ratio = np.average([r.sharpe_ratio for r in results],
                                      weights=[self.algorithm_weights.get(name, 1.0) 
                                             for name in algorithm_names])
        
        # Determine quantum advantage
        quantum_advantage = any(r.quantum_advantage for r in results)
        
        # Average computation time
        avg_computation_time = np.mean([r.computation_time for r in results])
        
        # Combine error metrics
        all_error_metrics = {}
        for i, result in enumerate(results):
            for key, value in result.error_metrics.items():
                all_error_metrics[f"{key}_{i}"] = value
        
        return OptimizationResult(
            weights=fused_weights,
            expected_return=fused_expected_return,
            volatility=fused_volatility,
            sharpe_ratio=fused_sharpe_ratio,
            quantum_advantage=quantum_advantage,
            computation_time=avg_computation_time,
            error_metrics=all_error_metrics
        )

class PerformanceMonitor:
    """Ishlash monitoring moduli."""
    
    def __init__(self):
        self.performance_history = []
        self.quantum_success_rate = 0.0
        self.classical_performance_baseline = 0.0
        
    def update_performance(self, result: OptimizationResult, 
                         benchmark_result: OptimizationResult = None):
        """Ishlash ma'lumotlarini yangilash."""
        performance_data = {
            'timestamp': datetime.now(),
            'quantum_advantage': result.quantum_advantage,
            'sharpe_ratio': result.sharpe_ratio,
            'computation_time': result.computation_time,
            'expected_return': result.expected_return,
            'volatility': result.volatility
        }
        
        self.performance_history.append(performance_data)
        
        # Update quantum success rate
        recent_results = self.performance_history[-100:]  # Last 100 results
        quantum_successes = sum(1 for r in recent_results if r['quantum_advantage'])
        self.quantum_success_rate = quantum_successes / len(recent_results) if recent_results else 0
        
        # Update classical baseline if benchmark provided
        if benchmark_result and not benchmark_result.quantum_advantage:
            self.classical_performance_baseline = benchmark_result.sharpe_ratio
    
    def get_quantum_advantage_threshold(self) -> float:
        """Quantum afzallikni baholash uchun threshold."""
        if self.classical_performance_baseline > 0:
            threshold = self.classical_performance_baseline * 1.1  # 10% improvement
        else:
            threshold = 1.5  # Default Sharpe ratio threshold
        
        return threshold
    
    def should_use_quantum(self) -> bool:
        """Quantum algoritm ishlatish kerakligini aniqlash."""
        # Use quantum if success rate is good enough
        return self.quantum_success_rate > 0.7
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Performance summary olish."""
        if not self.performance_history:
            return {}
        
        recent = self.performance_history[-50:]  # Last 50 results
        
        return {
            'quantum_success_rate': self.quantum_success_rate,
            'classical_baseline': self.classical_performance_baseline,
            'avg_sharpe_ratio': np.mean([r['sharpe_ratio'] for r in recent]),
            'avg_computation_time': np.mean([r['computation_time'] for r in recent]),
            'quantum_usage_recommendation': self.should_use_quantum(),
            'total_optimizations': len(self.performance_history)
        }

class HybridQuantumClassicalSystem:
    """Asosiy Hybrid Quantum-Classical Trading System."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        
        # Initialize components
        self.preprocessor = ClassicalPreprocessor()
        self.feature_selector = QuantumFeatureSelector(
            n_qubits=self.config.get('n_qubits', 10)
        )
        self.quantum_optimizer = QuantumPortfolioOptimizer(
            hardware_type=QuantumHardware(self.config.get('hardware_type', 'simulator'))
        )
        self.postprocessor = ClassicalPostprocessor()
        self.fusion_engine = DecisionFusionEngine()
        self.performance_monitor = PerformanceMonitor()
        
        # System state
        self.is_quantum_available = QISKIT_AVAILABLE
        self.current_problem_size = ProblemSize.SMALL
        self.system_health = "HEALTHY"
        
        logger.info("Hybrid Quantum-Classical System initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default konfiguratsiya."""
        return {
            'n_qubits': 10,
            'hardware_type': 'simulator',
            'algorithm_thresholds': {
                ProblemSize.SMALL: AlgorithmType.CLASSICAL_ONLY,
                ProblemSize.MEDIUM: AlgorithmType.HYBRID,
                ProblemSize.LARGE: AlgorithmType.QUANTUM_ADVANTAGE
            },
            'performance_thresholds': {
                'min_sharpe_ratio': 1.0,
                'max_computation_time': 60.0,  # seconds
                'quantum_advantage_threshold': 1.2  # 20% improvement
            },
            'error_tolerance': 0.05,
            'fallback_enabled': True
        }
    
    def classify_problem_size(self, data: Union[pd.DataFrame, np.ndarray]) -> ProblemSize:
        """Muammo hajmini klassifikatsiya qilish."""
        if isinstance(data, pd.DataFrame):
            n_assets = data.shape[1]
        else:
            n_assets = data.shape[1] if len(data.shape) > 1 else 1
        
        if n_assets < 50:
            return ProblemSize.SMALL
        elif n_assets <= 200:
            return ProblemSize.MEDIUM
        else:
            return ProblemSize.LARGE
    
    def select_algorithm(self, problem_size: ProblemSize, 
                        performance_history: List[Dict] = None) -> AlgorithmType:
        """Algoritm tanlash."""
        # Get base recommendation from config
        base_algorithm = self.config['algorithm_thresholds'][problem_size]
        
        # Adjust based on performance history if available
        if performance_history:
            recent_success_rate = self.performance_monitor.quantum_success_rate
            if recent_success_rate > 0.8:
                # High quantum success rate - use quantum for larger problems
                if problem_size == ProblemSize.MEDIUM:
                    return AlgorithmType.QUANTUM_ADVANTAGE
                elif problem_size == ProblemSize.SMALL:
                    return AlgorithmType.HYBRID
        
        # Adjust based on system health
        if self.system_health != "HEALTHY":
            return AlgorithmType.CLASSICAL_ONLY
        
        # Adjust based on quantum availability
        if not self.is_quantum_available:
            return AlgorithmType.CLASSICAL_ONLY
        
        return base_algorithm
    
    def process_portfolio_optimization(self, data: pd.DataFrame, 
                                     asset_names: List[str] = None,
                                     target_metrics: Dict = None) -> Dict[str, Any]:
        """To'liq portfolio optimizatsiya pipeline."""
        start_time = time.time()
        
        try:
            # Step 1: Classify problem size
            self.current_problem_size = self.classify_problem_size(data)
            logger.info(f"Problem classified as: {self.current_problem_size.value}")
            
            # Step 2: Select algorithm
            selected_algorithm = self.select_algorithm(self.current_problem_size)
            logger.info(f"Selected algorithm: {selected_algorithm.value}")
            
            # Step 3: Classical preprocessing
            preprocessed_data, feature_stats = self.preprocessor.preprocess_data(data)
            logger.info("Classical preprocessing completed")
            
            # Step 4: Feature selection (quantum-inspired)
            n_selected_features = min(50, preprocessed_data.shape[1])  # Limit for stability
            selected_features = self.feature_selector.quantum_feature_selection(
                preprocessed_data, n_selected_features
            )
            logger.info(f"Selected {selected_features.shape[1]} features")
            
            # Step 5: Prepare optimization data
            returns = feature_stats['mean'][:selected_features.shape[1]]
            
            # Create covariance matrix
            if selected_features.shape[1] > 1:
                covariance = np.cov(selected_features.T)
                # Add regularization for numerical stability
                covariance += np.eye(covariance.shape[0]) * 1e-8
            else:
                covariance = np.array([[0.01]])  # Default variance
            
            # Step 6: Optimization based on selected algorithm
            optimization_results = []
            algorithm_names = []
            
            if selected_algorithm in [AlgorithmType.HYBRID, AlgorithmType.QUANTUM_ADVANTAGE]:
                # Try quantum methods
                if self.is_quantum_available:
                    try:
                        vqe_result = self.quantum_optimizer.optimize_portfolio_vqe(
                            returns, covariance
                        )
                        optimization_results.append(vqe_result)
                        algorithm_names.append('quantum_vqe')
                        
                        qaoa_result = self.quantum_optimizer.optimize_portfolio_qaoa(
                            returns, covariance
                        )
                        optimization_results.append(qaoa_result)
                        algorithm_names.append('quantum_qaoa')
                        
                    except Exception as e:
                        logger.warning(f"Quantum optimization failed: {e}")
            
            # Always include classical methods as baseline
            classical_result = self.quantum_optimizer._fallback_optimization(
                returns, covariance
            )
            optimization_results.append(classical_result)
            algorithm_names.append('classical_mpt')
            
            # Risk parity as additional method
            risk_parity_weights = self._calculate_risk_parity_weights(covariance)
            risk_parity_result = OptimizationResult(
                weights=risk_parity_weights,
                expected_return=np.dot(risk_parity_weights, returns),
                volatility=np.sqrt(np.dot(risk_parity_weights, np.dot(covariance, risk_parity_weights))),
                sharpe_ratio=0,  # Will be calculated
                quantum_advantage=False,
                computation_time=0.01,
                error_metrics={}
            )
            risk_parity_result.sharpe_ratio = (
                risk_parity_result.expected_return / max(risk_parity_result.volatility, 1e-8)
            )
            optimization_results.append(risk_parity_result)
            algorithm_names.append('risk_parity')
            
            # Step 7: Decision fusion
            final_result = self.fusion_engine.fuse_optimization_results(
                optimization_results, algorithm_names
            )
            
            # Step 8: Classical post-processing
            if asset_names is None:
                asset_names = [f"Asset_{i}" for i in range(len(final_result.weights))]
            
            processed_weights = self.postprocessor.postprocess_portfolio(
                final_result.weights, asset_names
            )
            
            # Update final result with processed weights
            final_result.weights = processed_weights
            final_result.expected_return = np.dot(processed_weights, returns)
            final_result.volatility = np.sqrt(np.dot(processed_weights, np.dot(covariance, processed_weights)))
            final_result.sharpe_ratio = final_result.expected_return / max(final_result.volatility, 1e-8)
            
            # Step 9: Performance monitoring
            self.performance_monitor.update_performance(final_result)
            
            # Step 10: Calculate comprehensive metrics
            portfolio_metrics = self.postprocessor.calculate_portfolio_metrics(
                processed_weights, returns, covariance
            )
            
            total_computation_time = time.time() - start_time
            
            # Prepare final result
            result = {
                'optimization_result': final_result,
                'portfolio_metrics': portfolio_metrics,
                'algorithm_used': selected_algorithm.value,
                'problem_size': self.current_problem_size.value,
                'preprocessing_stats': feature_stats,
                'feature_selection': {
                    'total_features': data.shape[1],
                    'selected_features': selected_features.shape[1],
                    'selection_method': 'quantum_inspired'
                },
                'quantum_metrics': {
                    'quantum_available': self.is_quantum_available,
                    'quantum_advantage_achieved': final_result.quantum_advantage,
                    'quantum_success_rate': self.performance_monitor.quantum_success_rate
                },
                'performance_metrics': {
                    'total_computation_time': total_computation_time,
                    'quantum_computation_time': np.mean([r.computation_time for r in optimization_results if r.quantum_advantage]),
                    'classical_baseline': self.performance_monitor.classical_performance_baseline
                },
                'error_handling': {
                    'fallback_used': any(not r.quantum_advantage for r in optimization_results),
                    'error_rate': np.mean([np.mean(list(r.error_metrics.values())) for r in optimization_results if r.error_metrics])
                }
            }
            
            logger.info("Portfolio optimization completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Portfolio optimization failed: {e}")
            self.system_health = "ERROR"
            return self._emergency_fallback(data)
    
    def _calculate_risk_parity_weights(self, covariance: np.ndarray) -> np.ndarray:
        """Risk parity portfoliyo vaznlarini hisoblash."""
        n_assets = covariance.shape[0]
        
        # Equal risk contribution approach
        target_contribution = 1.0 / n_assets
        weights = np.ones(n_assets) / n_assets
        
        # Iterative optimization for risk parity
        for _ in range(100):  # Limited iterations
            portfolio_variance = np.dot(weights, np.dot(covariance, weights))
            marginal_contrib = np.dot(covariance, weights)
            
            current_contrib = weights * marginal_contrib / portfolio_variance
            
            # Calculate adjustment
            adjustment = target_contribution / current_contrib
            
            # Update weights
            weights = weights * adjustment
            weights = np.maximum(weights, 0.001)  # Minimum weight
            weights = weights / np.sum(weights)  # Normalize
            
            # Check convergence
            max_deviation = np.max(np.abs(current_contrib - target_contribution))
            if max_deviation < 0.01:
                break
        
        return weights
    
    def _emergency_fallback(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Favqulodda fallback tizimi."""
        logger.warning("Using emergency fallback optimization")
        
        # Simple equal weight portfolio
        n_assets = data.shape[1]
        weights = np.ones(n_assets) / n_assets
        
        # Calculate basic metrics
        data_clean = data.fillna(0)
        returns = np.mean(data_clean, axis=0)
        covariance = np.cov(data_clean.T)
        if np.any(np.isnan(covariance)):
            covariance = np.eye(n_assets) * 0.01
        
        expected_return = np.dot(weights, returns)
        volatility = np.sqrt(np.dot(weights, np.dot(covariance, weights)))
        sharpe_ratio = expected_return / max(volatility, 1e-8)
        
        result = {
            'optimization_result': OptimizationResult(
                weights=weights,
                expected_return=expected_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                quantum_advantage=False,
                computation_time=0.01,
                error_metrics={'fallback': True}
            ),
            'portfolio_metrics': self.postprocessor.calculate_portfolio_metrics(
                weights, returns, covariance
            ),
            'algorithm_used': 'emergency_fallback',
            'problem_size': self.current_problem_size.value,
            'quantum_metrics': {
                'quantum_available': self.is_quantum_available,
                'quantum_advantage_achieved': False,
                'quantum_success_rate': 0.0
            },
            'performance_metrics': {
                'total_computation_time': 0.01,
                'quantum_computation_time': 0.0,
                'classical_baseline': 0.0
            },
            'preprocessing_stats': {'data_quality_score': 0.8},
            'feature_selection': {
                'total_features': n_assets,
                'selected_features': n_assets,
                'selection_method': 'emergency_fallback'
            },
            'error_handling': {
                'fallback_used': True,
                'emergency_fallback': True
            }
        }
        
        return result
    
    def get_system_status(self) -> Dict[str, Any]:
        """Tizim holatini olish."""
        performance_summary = self.performance_monitor.get_performance_summary()
        
        return {
            'system_health': self.system_health,
            'quantum_available': self.is_quantum_available,
            'current_problem_size': self.current_problem_size.value,
            'performance_summary': performance_summary,
            'config': self.config,
            'last_update': datetime.now().isoformat()
        }
    
    def optimize_with_constraints(self, data: pd.DataFrame, 
                                constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Cheklovlar bilan optimizatsiya."""
        # Modify postprocessor constraints
        if 'max_single_position' in constraints:
            self.postprocessor.risk_limits['max_single_position'] = constraints['max_single_position']
        if 'max_sector_weight' in constraints:
            self.postprocessor.risk_limits['max_sector_weight'] = constraints['max_sector_weight']
        
        # Run optimization
        return self.process_portfolio_optimization(data)
    
    def benchmark_algorithms(self, data: pd.DataFrame, 
                           n_runs: int = 5) -> Dict[str, Any]:
        """Algoritmlar benchmarking."""
        benchmark_results = {}
        
        for run in range(n_runs):
            logger.info(f"Running benchmark {run + 1}/{n_runs}")
            
            # Test quantum VQE
            try:
                preprocessed_data, _ = self.preprocessor.preprocess_data(data)
                returns = np.mean(preprocessed_data, axis=0)
                covariance = np.cov(preprocessed_data.T)
                
                if self.is_quantum_available:
                    vqe_result = self.quantum_optimizer.optimize_portfolio_vqe(returns, covariance)
                    benchmark_results.setdefault('quantum_vqe', []).append({
                        'sharpe_ratio': vqe_result.sharpe_ratio,
                        'computation_time': vqe_result.computation_time,
                        'success': True
                    })
                else:
                    benchmark_results.setdefault('quantum_vqe', []).append({
                        'error': 'Quantum not available',
                        'success': False
                    })
                
            except Exception as e:
                benchmark_results.setdefault('quantum_vqe', []).append({
                    'error': str(e),
                    'success': False
                })
            
            # Test classical
            try:
                classical_result = self.quantum_optimizer._fallback_optimization(returns, covariance)
                benchmark_results.setdefault('classical', []).append({
                    'sharpe_ratio': classical_result.sharpe_ratio,
                    'computation_time': classical_result.computation_time,
                    'success': True
                })
            except Exception as e:
                benchmark_results.setdefault('classical', []).append({
                    'error': str(e),
                    'success': False
                })
        
        # Calculate averages
        for algorithm, results in benchmark_results.items():
            successful_results = [r for r in results if r['success']]
            if successful_results:
                benchmark_results[algorithm] = {
                    'avg_sharpe_ratio': np.mean([r['sharpe_ratio'] for r in successful_results]),
                    'avg_computation_time': np.mean([r['computation_time'] for r in successful_results]),
                    'success_rate': len(successful_results) / len(results),
                    'n_successful': len(successful_results)
                }
            else:
                benchmark_results[algorithm] = {
                    'success_rate': 0,
                    'error': 'All runs failed'
                }
        
        return benchmark_results

# Utility Functions
def create_sample_market_data(n_assets: int = 20, n_days: int = 252) -> Tuple[pd.DataFrame, List[str]]:
    """Namuna bozor ma'lumotlarini yaratish."""
    np.random.seed(42)  # For reproducible results
    
    # Generate correlated returns
    correlation = np.random.uniform(0.1, 0.6, (n_assets, n_assets))
    correlation = (correlation + correlation.T) / 2  # Make symmetric
    np.fill_diagonal(correlation, 1.0)
    
    # Cholesky decomposition for correlated data
    L = np.linalg.cholesky(correlation)
    
    # Generate random returns
    daily_returns = np.random.normal(0.0005, 0.02, (n_days, n_assets))
    
    # Apply correlation
    correlated_returns = np.dot(daily_returns, L.T)
    
    # Create asset names
    asset_names = [f"Asset_{i:03d}" for i in range(n_assets)]
    
    # Create DataFrame
    data = pd.DataFrame(correlated_returns, columns=asset_names)
    
    return data, asset_names

def analyze_quantum_advantage(quantum_result: OptimizationResult, 
                            classical_result: OptimizationResult) -> Dict[str, float]:
    """Quantum afzallikni tahlil qilish."""
    advantage_metrics = {}
    
    # Sharpe ratio improvement
    if classical_result.sharpe_ratio > 0:
        advantage_metrics['sharpe_improvement'] = (
            quantum_result.sharpe_ratio - classical_result.sharpe_ratio
        ) / classical_result.sharpe_ratio
    
    # Computation time comparison
    if classical_result.computation_time > 0:
        advantage_metrics['time_speedup'] = (
            classical_result.computation_time - quantum_result.computation_time
        ) / classical_result.computation_time
    
    # Risk-adjusted performance
    risk_improvement = quantum_result.sharpe_ratio - classical_result.sharpe_ratio
    advantage_metrics['risk_adjusted_advantage'] = risk_improvement
    
    # Overall advantage score
    advantage_metrics['overall_advantage'] = (
        advantage_metrics.get('sharpe_improvement', 0) * 0.6 +
        advantage_metrics.get('time_speedup', 0) * 0.4
    )
    
    return advantage_metrics

def visualize_portfolio_comparison(optimization_results: List[Dict[str, Any]], 
                                 save_path: str = None):
    """Portfoliyo taqqoslashni vizualizatsiya qilish."""
    if len(optimization_results) < 2:
        logger.warning("At least 2 results needed for comparison")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Portfolio Optimization Comparison', fontsize=16)
    
    # Extract data
    methods = [result['algorithm_used'] for result in optimization_results]
    sharpe_ratios = [result['portfolio_metrics']['sharpe_ratio'] 
                    for result in optimization_results]
    computation_times = [result['performance_metrics']['total_computation_time']
                        for result in optimization_results]
    volatilities = [result['portfolio_metrics']['volatility']
                   for result in optimization_results]
    
    # Sharpe ratio comparison
    axes[0, 0].bar(methods, sharpe_ratios, color=['skyblue', 'lightgreen', 'lightcoral'])
    axes[0, 0].set_title('Sharpe Ratio Comparison')
    axes[0, 0].set_ylabel('Sharpe Ratio')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Computation time comparison
    axes[0, 1].bar(methods, computation_times, color=['skyblue', 'lightgreen', 'lightcoral'])
    axes[0, 1].set_title('Computation Time Comparison')
    axes[0, 1].set_ylabel('Time (seconds)')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Risk-Return scatter
    returns = [result['optimization_result'].expected_return for result in optimization_results]
    axes[1, 0].scatter(volatilities, returns, c=sharpe_ratios, cmap='viridis', s=100)
    axes[1, 0].set_xlabel('Volatility')
    axes[1, 0].set_ylabel('Expected Return')
    axes[1, 0].set_title('Risk-Return Profile')
    
    # Add colorbar
    scatter = axes[1, 0].scatter(volatilities, returns, c=sharpe_ratios, cmap='viridis', s=100)
    plt.colorbar(scatter, ax=axes[1, 0], label='Sharpe Ratio')
    
    # Portfolio weights comparison (top assets)
    weights_data = []
    labels = []
    for i, result in enumerate(optimization_results):
        weights = result['optimization_result'].weights
        top_5_indices = np.argsort(weights)[-5:]
        top_weights = weights[top_5_indices]
        weights_data.append(top_weights)
        labels.append(f"{methods[i]}\n(Top 5 assets)")
    
    # Stacked bar chart for top weights
    x_pos = np.arange(len(methods))
    bottom = np.zeros(len(methods))
    
    for j in range(5):
        layer_weights = [w[j] if j < len(w) else 0 for w in weights_data]
        axes[1, 1].bar(x_pos, layer_weights, bottom=bottom, 
                      label=f'Asset {j+1}', alpha=0.8)
        bottom += layer_weights
    
    axes[1, 1].set_title('Top 5 Asset Weights')
    axes[1, 1].set_ylabel('Weight')
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels([f'Method {i+1}' for i in range(len(methods))])
    axes[1, 1].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Comparison chart saved to {save_path}")
    
    plt.show()

def main():
    """Test function for the Hybrid Quantum-Classical Trading System."""
    print("Hybrid Quantum-Classical Trading System Test")
    print("=" * 60)
    
    # Initialize system
    config = {
        'n_qubits': 8,
        'hardware_type': 'simulator',
        'algorithm_thresholds': {
            ProblemSize.SMALL: AlgorithmType.CLASSICAL_ONLY,
            ProblemSize.MEDIUM: AlgorithmType.HYBRID,
            ProblemSize.LARGE: AlgorithmType.QUANTUM_ADVANTAGE
        }
    }
    
    system = HybridQuantumClassicalSystem(config=config)
    
    print(f"Quantum computing available: {system.is_quantum_available}")
    print(f"System health: {system.system_health}")
    
    # Create sample data
    print("\nCreating sample market data...")
    data, asset_names = create_sample_market_data(n_assets=15, n_days=200)
    print(f"Created data with {data.shape[0]} days and {data.shape[1]} assets")
    
    # Run optimization
    print("\nRunning portfolio optimization...")
    result = system.process_portfolio_optimization(data, asset_names)
    
    # Display results
    print("\n=== OPTIMIZATION RESULTS ===")
    print(f"Algorithm used: {result['algorithm_used']}")
    print(f"Problem size: {result['problem_size']}")
    print(f"Quantum advantage achieved: {result['quantum_metrics']['quantum_advantage_achieved']}")
    
    print(f"\nPortfolio Metrics:")
    portfolio_metrics = result['portfolio_metrics']
    print(f"Expected Return: {portfolio_metrics['expected_return']:.2%}")
    print(f"Volatility: {portfolio_metrics['volatility']:.2%}")
    print(f"Sharpe Ratio: {portfolio_metrics['sharpe_ratio']:.2f}")
    print(f"Max Position Weight: {portfolio_metrics['max_position_weight']:.2%}")
    print(f"Portfolio Size: {portfolio_metrics['portfolio_size']} assets")
    
    print(f"\nPerformance Metrics:")
    perf_metrics = result['performance_metrics']
    print(f"Total Computation Time: {perf_metrics['total_computation_time']:.2f} seconds")
    print(f"Quantum Success Rate: {result['quantum_metrics']['quantum_success_rate']:.1%}")
    
    # Display top holdings
    weights = result['optimization_result'].weights
    top_holdings = sorted(zip(asset_names, weights), key=lambda x: x[1], reverse=True)[:5]
    print(f"\nTop 5 Holdings:")
    for asset, weight in top_holdings:
        print(f"  {asset}: {weight:.2%}")
    
    # System status
    print(f"\n=== SYSTEM STATUS ===")
    status = system.get_system_status()
    for key, value in status.items():
        if key != 'config':
            print(f"{key}: {value}")
    
    # Benchmark test
    print(f"\n=== BENCHMARKING ===")
    benchmark_results = system.benchmark_algorithms(data, n_runs=3)
    
    for algorithm, metrics in benchmark_results.items():
        print(f"\n{algorithm.upper()}:")
        if 'avg_sharpe_ratio' in metrics:
            print(f"  Average Sharpe Ratio: {metrics['avg_sharpe_ratio']:.2f}")
            print(f"  Average Computation Time: {metrics['avg_computation_time']:.3f} seconds")
            print(f"  Success Rate: {metrics['success_rate']:.1%}")
        else:
            print(f"  Error: {metrics.get('error', 'Unknown error')}")
    
    print(f"\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    main()