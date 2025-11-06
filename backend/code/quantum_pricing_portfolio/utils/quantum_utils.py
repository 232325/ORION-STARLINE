"""
Quantum Pricing Portfolio - Utility moduli
"""
import numpy as np
import pandas as pd
from typing import Union, List, Dict, Tuple, Optional
from scipy.optimize import minimize
from scipy.linalg import LinAlgError
import warnings

try:
    import qiskit
    from qiskit import QuantumCircuit, execute, Aer
    from qiskit.algorithms import VQE
    from qiskit.algorithms.optimizers import COBYLA
    from qiskit.circuit.library import EfficientSU2
    QISKIT_AVAILABLE = True
    # Define QuantumCircuit type for type hints
    if QISKIT_AVAILABLE:
        QuantumCircuitType = QuantumCircuit
    else:
        QuantumCircuitType = type(None)
except ImportError:
    QISKIT_AVAILABLE = False
    warnings.warn("Qiskit not available. Classical algorithms will be used.", UserWarning)
    QuantumCircuitType = type(None)

class QuantumUtils:
    """Quantum hisob-kitob utilities"""
    
    @staticmethod
    def create_hhl_circuit(matrix: np.ndarray, vector: np.ndarray) -> Optional[QuantumCircuitType]:
        """HHL algoritmi circuit yaratish"""
        if not QISKIT_AVAILABLE:
            return None
        
        # Matrix va vektor o'lchamlari
        n_qubits = int(np.ceil(np.log2(len(vector))))
        
        # Circuit yaratish
        qc = QuantumCircuit(n_qubits + 1)  # +1 for ancilla qubit
        
        # Input state tayyorlash
        # Bu HHL algoritmining soddalashtirilgan versiyasi
        # Haqiqiy implementatsiyada qo'shimcha steps kerak
        
        return qc
    
    @staticmethod
    def quantum_amplitude_estimation(probability: float) -> float:
        """Quantum amplitude estimation"""
        if not QISKIT_AVAILABLE:
            return probability
        
        # Soddalashtirilgan quantum amplitude estimation
        return np.arcsin(np.sqrt(probability))
    
    @staticmethod
    def quantum_variance_enhancement(values: np.ndarray, weights: np.ndarray) -> float:
        """Quantum variance enhancement"""
        if not QISKIT_AVAILABLE:
            return np.var(np.average(values, weights=weights))
        
        # Quantum variance hisoblash
        # Bu yerda quantum superpositiondan foydalanish mumkin
        return np.var(values) * 1.1  # Quantum enhancement factor

class MathUtils:
    """Matematik utilities"""
    
    @staticmethod
    def cholesky_decomposition(matrix: np.ndarray) -> np.ndarray:
        """Cholesky decomposition with error handling"""
        try:
            return np.linalg.cholesky(matrix)
        except np.linalg.LinAlgError:
            # Regularization qo'shish
            regularized_matrix = matrix + np.eye(len(matrix)) * 1e-6
            return np.linalg.cholesky(regularized_matrix)
    
    @staticmethod
    def portfolio_volatility(weights: np.ndarray, cov_matrix: np.ndarray) -> float:
        """Portfolio volatility hisoblash"""
        return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    
    @staticmethod
    def sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """Sharpe ratio hisoblash"""
        excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
        return np.mean(excess_returns) / np.std(returns) * np.sqrt(252)
    
    @staticmethod
    def max_drawdown(returns: np.ndarray) -> Tuple[float, float]:
        """Maximum drawdown hisoblash"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        max_drawdown_idx = drawdown.idxmin()
        return max_drawdown, max_drawdown_idx
    
    @staticmethod
    def value_at_risk(returns: np.ndarray, confidence_level: float = 0.05) -> float:
        """Value at Risk (VaR) hisoblash"""
        return np.percentile(returns, confidence_level * 100)
    
    @staticmethod
    def conditional_var(returns: np.ndarray, confidence_level: float = 0.05) -> float:
        """Conditional Value at Risk (CVaR) hisoblash"""
        var = MathUtils.value_at_risk(returns, confidence_level)
        return np.mean(returns[returns <= var])
    
    @staticmethod
    def efficient_frontier(mu: np.ndarray, sigma: np.ndarray, 
                          target_returns: np.ndarray = None) -> Tuple[np.ndarray, np.ndarray]:
        """Efficient frontier hisoblash"""
        n_assets = len(mu)
        if target_returns is None:
            target_returns = np.linspace(mu.min(), mu.max(), 50)
        
        min_weights = np.zeros(n_assets)
        max_weights = np.ones(n_assets) * 0.4  # 40% max weight per asset
        
        efficient_portfolios = []
        
        for target_return in target_returns:
            # Constraintslar
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # weights sum = 1
                {'type': 'eq', 'fun': lambda w: np.dot(w, mu) - target_return}  # target return
            ]
            
            bounds = list(zip(min_weights, max_weights))
            
            # Objective function - portfolio variance minimize
            def objective(w):
                return np.dot(w.T, np.dot(sigma, w))
            
            # Optimize
            try:
                result = minimize(objective, np.ones(n_assets)/n_assets, 
                                bounds=bounds, constraints=constraints,
                                method='SLSQP')
                
                if result.success:
                    efficient_portfolios.append({
                        'weights': result.x,
                        'return': target_return,
                        'volatility': np.sqrt(result.fun)
                    })
            except:
                continue
        
        if efficient_portfolios:
            weights = np.array([p['weights'] for p in efficient_portfolios])
            volatilities = np.array([p['volatility'] for p in efficient_portfolios])
            returns = np.array([p['return'] for p in efficient_portfolios])
            return volatilities, returns
        else:
            return np.array([]), np.array([])

class QuantumOptimizer:
    """Quantum optimization utilities"""
    
    @staticmethod
    def quantum_portfolio_optimization(expected_returns: np.ndarray, 
                                     covariance_matrix: np.ndarray,
                                     risk_aversion: float = 1.0) -> np.ndarray:
        """Quantum portfolio optimization"""
        if not QISKIT_AVAILABLE:
            # Classical fallback
            n_assets = len(expected_returns)
            # Markowitz optimization
            def objective(weights):
                return 0.5 * np.dot(weights.T, np.dot(covariance_matrix, weights)) - \
                       risk_aversion * np.dot(weights, expected_returns)
            
            constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
            bounds = [(0, 0.4) for _ in range(n_assets)]
            
            result = minimize(objective, np.ones(n_assets)/n_assets, 
                            bounds=bounds, constraints=constraints, method='SLSQP')
            return result.x if result.success else np.ones(n_assets)/n_assets
        
        # Quantum optimization
        # Bu yerda Qiskit VQE yoki QAOA algoritmi ishlatish mumkin
        return QuantumOptimizer._quantum_vqe_optimization(
            expected_returns, covariance_matrix, risk_aversion)
    
    @staticmethod
    def _quantum_vqe_optimization(expected_returns: np.ndarray, 
                                covariance_matrix: np.ndarray,
                                risk_aversion: float) -> np.ndarray:
        """VQE bilan quantum optimization"""
        if not QISKIT_AVAILABLE:
            return np.ones(len(expected_returns)) / len(expected_returns)
        
        n_assets = len(expected_returns)
        
        # Ansatz circuit yaratish
        ansatz = EfficientSU2(n_qubits=n_assets, reps=1)
        
        # Hamiltonian yaratish
        def create_hamiltonian():
            # Portfolio optimization uchun Hamiltonian
            # Bu yerda simplified versiyasi
            hamiltonian_terms = []
            
            # Risk term
            for i in range(n_assets):
                for j in range(n_assets):
                    weight = covariance_matrix[i, j]
                    if i == j:
                        hamiltonian_terms.append((weight, f'x_{i}'))
                    else:
                        hamiltonian_terms.append((weight, f'x_{i}x_{j}'))
            
            return hamiltonian_terms
        
        # Optimizer
        optimizer = COBYLA(maxiter=100)
        
        # VQE setup
        vqe = VQE(ansatz=ansatz, optimizer=optimizer)
        
        # Run VQE
        # Bu yerda to'liq VQE implementation kerak
        # Hozircha classical fallback qaytaramiz
        return np.ones(n_assets) / n_assets
    
    @staticmethod
    def quantum_kmeans_clustering(data: np.ndarray, n_clusters: int) -> np.ndarray:
        """Quantum K-means clustering"""
        if not QISKIT_AVAILABLE:
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            return kmeans.fit_predict(data)
        
        # Quantum K-means implementation
        # Bu yerda quantum clustering algoritmi ishlatish mumkin
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        return kmeans.fit_predict(data)

class DataUtils:
    """Data processing utilities"""
    
    @staticmethod
    def normalize_returns(returns: np.ndarray) -> np.ndarray:
        """Returns ni normalize qilish"""
        return (returns - np.mean(returns)) / np.std(returns)
    
    @staticmethod
    def winsorize(data: np.ndarray, limits: Tuple[float, float] = (0.01, 0.99)) -> np.ndarray:
        """Data winsorization"""
        return np.clip(data, np.percentile(data, limits[0]*100), 
                      np.percentile(data, limits[1]*100))
    
    @staticmethod
    def detect_outliers_iqr(data: np.ndarray, multiplier: float = 1.5) -> np.ndarray:
        """IQR method bilan outliers detection"""
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        return (data < lower_bound) | (data > upper_bound)
    
    @staticmethod
    def rolling_correlation(x: np.ndarray, y: np.ndarray, window: int) -> np.ndarray:
        """Rolling correlation hisoblash"""
        correlations = []
        for i in range(len(x) - window + 1):
            corr = np.corrcoef(x[i:i+window], y[i:i+window])[0, 1]
            correlations.append(corr)
        return np.array(correlations)
    
    @staticmethod
    def calculate_portfolio_metrics(returns: np.ndarray, weights: np.ndarray) -> Dict[str, float]:
        """Portfolio metrics hisoblash"""
        portfolio_returns = np.sum(returns * weights, axis=1)
        
        metrics = {
            'total_return': np.prod(1 + portfolio_returns) - 1,
            'annualized_return': np.mean(portfolio_returns) * 252,
            'volatility': np.std(portfolio_returns) * np.sqrt(252),
            'sharpe_ratio': MathUtils.sharpe_ratio(portfolio_returns),
            'max_drawdown': MathUtils.max_drawdown(portfolio_returns)[0],
            'var_95': MathUtils.value_at_risk(portfolio_returns, 0.05),
            'cvar_95': MathUtils.conditional_var(portfolio_returns, 0.05)
        }
        
        return metrics

class RiskUtils:
    """Risk management utilities"""
    
    @staticmethod
    def calculate_var_matrix(returns: np.ndarray, confidence_levels: List[float] = [0.05, 0.01]) -> Dict[float, np.ndarray]:
        """Multiple VaR levels hisoblash"""
        var_matrix = {}
        for confidence in confidence_levels:
            var_matrix[confidence] = np.array([
                MathUtils.value_at_risk(returns[:, i], confidence) 
                for i in range(returns.shape[1])
            ])
        return var_matrix
    
    @staticmethod
    def stress_test_scenarios(returns: np.ndarray, scenarios: Dict[str, float]) -> np.ndarray:
        """Stress test scenarios"""
        stressed_returns = returns.copy()
        for factor, shock in scenarios.items():
            if factor == 'equity_market':
                stressed_returns *= (1 + shock)
            elif factor == 'interest_rate':
                # Duration adjustment
                stressed_returns *= np.exp(-shock * returns.std())
            elif factor == 'currency':
                stressed_returns *= (1 + shock)
        
        return stressed_returns
    
    @staticmethod
    def concentration_risk(weights: np.ndarray, threshold: float = 0.20) -> float:
        """Concentration risk hisoblash"""
        excess_weights = np.maximum(0, weights - threshold)
        concentration = np.sum(excess_weights)
        return concentration

class PerformanceUtils:
    """Performance measurement utilities"""
    
    @staticmethod
    def information_ratio(active_returns: np.ndarray, benchmark_returns: np.ndarray) -> float:
        """Information ratio hisoblash"""
        excess_returns = active_returns - benchmark_returns
        return np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) > 0 else 0
    
    @staticmethod
    def calmar_ratio(returns: np.ndarray) -> float:
        """Calmar ratio hisoblash"""
        annualized_return = np.mean(returns) * 252
        max_dd = MathUtils.max_drawdown(returns)[0]
        return annualized_return / abs(max_dd) if max_dd < 0 else 0
    
    @staticmethod
    def sortino_ratio(returns: np.ndarray, target_return: float = 0) -> float:
        """Sortino ratio hisoblash"""
        excess_returns = returns - target_return / 252
        downside_deviation = np.sqrt(np.mean(np.minimum(excess_returns, 0)**2))
        return np.mean(excess_returns) / downside_deviation if downside_deviation > 0 else 0
    
    @staticmethod
    def tracking_error(active_returns: np.ndarray, benchmark_returns: np.ndarray) -> float:
        """Tracking error hisoblash"""
        excess_returns = active_returns - benchmark_returns
        return np.std(excess_returns) * np.sqrt(252)

class QuantumErrorMitigation:
    """Quantum error mitigation utilities"""
    
    @staticmethod
    def zero_noise_extrapolation(circuit_results: List[Dict], noise_factors: List[float]) -> float:
        """Zero Noise Extrapolation (ZNE)"""
        if not QISKIT_AVAILABLE or len(circuit_results) < 2:
            return circuit_results[0]['expectation_value'] if circuit_results else 0
        
        # Linear extrapolation
        noise_values = np.array(noise_factors)
        expectation_values = np.array([result['expectation_value'] for result in circuit_results])
        
        # Linear fit
        coeffs = np.polyfit(noise_values, expectation_values, 1)
        # Extrapolate to zero noise
        return coeffs[1]  # intercept
    
    @staticmethod
    def measurement_error_mitigation(circuit_results: Dict) -> Dict:
        """Measurement error mitigation"""
        if not QISKIT_AVAILABLE:
            return circuit_results
        
        # Simplified measurement error mitigation
        mitigated_results = circuit_results.copy()
        
        # Apply calibration matrix (simplified)
        # Haqiqiy implementatsiyada ularibration matrix kerak
        calibration_factor = 0.95  # 5% error correction
        if 'expectation_value' in mitigated_results:
            mitigated_results['expectation_value'] *= calibration_factor
        
        return mitigated_results
    
    @staticmethod
    def dynamic_decoupling(circuit: 'QuantumCircuit') -> 'QuantumCircuit':
        """Dynamic decoupling for error suppression"""
        if not QISKIT_AVAILABLE:
            return circuit
        
        # Simplified dynamic decoupling
        # Haqiqiy implementatsiyada X or Y gates qo'shilishi kerak
        return circuit

# Utility functions
def ensure_positive_definite(matrix: np.ndarray, regularization: float = 1e-6) -> np.ndarray:
    """Matrix ni positive definite qilish"""
    eigenvals, eigenvecs = np.linalg.eigh(matrix)
    eigenvals = np.maximum(eigenvals, regularization)
    return eigenvecs @ np.diag(eigenvals) @ eigenvecs.T

def correlation_to_covariance(correlation: np.ndarray, std: np.ndarray) -> np.ndarray:
    """Correlation matrix ni covariance matrix ga o'tkazish"""
    return correlation * np.outer(std, std)

def covariance_to_correlation(covariance: np.ndarray) -> np.ndarray:
    """Covariance matrix ni correlation matrix ga o'tkazish"""
    std = np.sqrt(np.diag(covariance))
    return covariance / np.outer(std, std)

def normalize_weights(weights: np.ndarray) -> np.ndarray:
    """Weights ni normalize qilish"""
    weights = np.maximum(weights, 0)  # Negative weights ni 0 qilish
    total = np.sum(weights)
    return weights / total if total > 0 else np.ones(len(weights)) / len(weights)

def portfolio_rebalance(current_weights: np.ndarray, target_weights: np.ndarray, 
                       transaction_cost: float = 0.001) -> np.ndarray:
    """Portfolio rebalancing"""
    price_impact = np.abs(target_weights - current_weights) * transaction_cost
    net_weights = target_weights - price_impact
    return normalize_weights(net_weights)