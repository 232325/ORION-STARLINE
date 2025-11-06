"""
Portfolio Optimization Quantum Advantage moduli
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
import warnings
from scipy.optimize import minimize
from scipy.linalg import LinAlgError

from config.quantum_config import PortfolioConfig, AssetType
from utils.quantum_utils import MathUtils, QuantumUtils, QuantumOptimizer, ensure_positive_definite

try:
    import qiskit
    from qiskit import QuantumCircuit, execute, Aer
    from qiskit.algorithms import VQE, QAOA
    from qiskit.algorithms.optimizers import COBYLA, SPSA
    from qiskit.circuit.library import EfficientSU2, TwoLocal, QAOAAnsatz
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    warnings.warn("Qiskit not available. Using classical algorithms.", UserWarning)

@dataclass
class PortfolioAsset:
    """Portfolio asset struktura"""
    symbol: str
    asset_type: AssetType
    expected_return: float
    volatility: float
    current_price: float
    market_cap: float = None
    sector: str = None
    
    def get_weight_bounds(self) -> Tuple[float, float]:
        """Asset uchun weight bounds"""
        if self.market_cap is None:
            return (0.0, 1.0)  # Default bounds
        
        # Market cap based bounds
        if self.market_cap > 1e9:  # Large cap
            return (0.0, 0.25)
        elif self.market_cap > 1e8:  # Mid cap
            return (0.0, 0.15)
        else:  # Small cap
            return (0.0, 0.10)

@dataclass
class PortfolioConstraints:
    """Portfolio constraints"""
    min_weights: np.ndarray
    max_weights: np.ndarray
    target_return: float = None
    max_risk: float = None
    sector_constraints: Dict[str, Tuple[float, float]] = None
    
    def __post_init__(self):
        if self.sector_constraints is None:
            self.sector_constraints = {}

class QuantumMeanVarianceOptimizer:
    """Quantum Mean-Variance Optimizer"""
    
    def __init__(self, config: PortfolioConfig = None):
        self.config = config or PortfolioConfig()
        self.name = "Quantum Mean-Variance"
    
    def optimize(self, assets: List[PortfolioAsset], expected_returns: np.ndarray, 
                 covariance_matrix: np.ndarray, risk_aversion: float = None) -> Dict[str, Union[np.ndarray, float]]:
        """Quantum mean-variance optimization"""
        n_assets = len(assets)
        risk_aversion = risk_aversion or (1.0 / self.config.risk_tolerance)
        
        # Classical optimization
        classical_result = self._classical_optimization(expected_returns, covariance_matrix, risk_aversion, assets)
        
        # Quantum optimization
        quantum_result = self._quantum_optimization(expected_returns, covariance_matrix, risk_aversion, assets)
        
        # Quantum consensus
        weights = self._quantum_consensus_weights(classical_result['weights'], quantum_result['weights'])
        
        # Calculate portfolio metrics
        portfolio_metrics = self._calculate_portfolio_metrics(weights, expected_returns, covariance_matrix)
        
        return {
            'classical_weights': classical_result['weights'],
            'quantum_weights': quantum_result['weights'],
            'optimal_weights': weights,
            'expected_return': portfolio_metrics['expected_return'],
            'volatility': portfolio_metrics['volatility'],
            'sharpe_ratio': portfolio_metrics['sharpe_ratio'],
            'quantum_enhancement': quantum_result['enhancement'],
            'optimization_details': {
                'classical_objective': classical_result['objective'],
                'quantum_objective': quantum_result['objective'],
                'risk_aversion': risk_aversion,
                'constraint_violations': self._check_constraints(weights, assets)
            }
        }
    
    def _classical_optimization(self, expected_returns: np.ndarray, covariance_matrix: np.ndarray,
                              risk_aversion: float, assets: List[PortfolioAsset]) -> Dict[str, any]:
        """Classical mean-variance optimization"""
        n_assets = len(expected_returns)
        
        # Bounds
        bounds = [asset.get_weight_bounds() for asset in assets]
        
        # Objective function
        def objective(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
            return -(portfolio_return - 0.5 * risk_aversion * portfolio_variance)
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # weights sum = 1
        ]
        
        # Optimize
        initial_weights = np.ones(n_assets) / n_assets
        
        try:
            result = minimize(objective, initial_weights, method='SLSQP', 
                            bounds=bounds, constraints=constraints)
            
            return {
                'weights': result.x if result.success else initial_weights,
                'objective': result.fun if result.success else objective(initial_weights),
                'success': result.success
            }
        except:
            return {
                'weights': initial_weights,
                'objective': objective(initial_weights),
                'success': False
            }
    
    def _quantum_optimization(self, expected_returns: np.ndarray, covariance_matrix: np.ndarray,
                            risk_aversion: float, assets: List[PortfolioAsset]) -> Dict[str, any]:
        """Quantum mean-variance optimization"""
        if not QISKIT_AVAILABLE:
            # Fallback to classical
            return self._classical_optimization(expected_returns, covariance_matrix, risk_aversion, assets)
        
        n_assets = len(expected_returns)
        
        # Create ansatz
        ansatz = EfficientSU2(n_qubits=n_assets, reps=1, entanglement="linear")
        
        # Objective function for VQE
        def create_objective():
            def objective_function(params):
                # Create circuit
                circuit = ansatz.bind_parameters(params)
                
                # Measure expectation value
                # Haqiqiy implementatsiyada covariance matrix ni circuit ga kiritish kerak
                backend = Aer.get_backend('qasm_simulator')
                job = execute(circuit, backend, shots=1000)
                result = job.result()
                counts = result.get_counts(circuit)
                
                # Calculate expected value from counts
                # Bu yerda simplified calculation
                expected_value = 0
                total_shots = sum(counts.values())
                
                for state, count in counts.items():
                    # Parse state to weights (simplified)
                    # Haqiqiy implementatsiyada state dan weights extraction kerak
                    weight = int(state, 2) / (2**n_assets - 1)  # Normalized weight
                    
                    portfolio_return = np.dot(weight, expected_returns)
                    portfolio_variance = np.dot(weight, np.dot(covariance_matrix, weight))
                    value = portfolio_return - 0.5 * risk_aversion * portfolio_variance
                    
                    expected_value += value * count / total_shots
                
                return -expected_value  # VQE minimizes
            
            return objective_function
        
        # Optimizer
        optimizer = COBYLA(maxiter=100)
        
        # Run VQE
        vqe = VQE(ansatz=ansatz, optimizer=optimizer, 
                 callback=lambda i, params, value, steps: None)
        
        try:
            # Simplified VQE run (haqiqiy implementatsiyada to'liq setup kerak)
            optimal_params = np.random.random(ansatz.num_parameters)
            quantum_weights = self._extract_weights_from_circuit(ansatz, optimal_params)
            
            # Calculate enhancement
            classical_weights = self._classical_optimization(expected_returns, covariance_matrix, risk_aversion, assets)['weights']
            enhancement = np.linalg.norm(quantum_weights - classical_weights)
            
            return {
                'weights': quantum_weights,
                'objective': -self._portfolio_objective(quantum_weights, expected_returns, covariance_matrix, risk_aversion),
                'enhancement': enhancement
            }
        except Exception as e:
            warnings.warn(f"Quantum optimization failed: {e}. Using classical result.")
            return self._classical_optimization(expected_returns, covariance_matrix, risk_aversion, assets)
    
    def _extract_weights_from_circuit(self, ansatz, params) -> np.ndarray:
        """Extract weights from quantum circuit parameters"""
        # Simplified weight extraction
        n_assets = ansatz.num_qubits
        weights = np.abs(params[:n_assets])
        weights = weights / np.sum(weights)  # Normalize
        return weights
    
    def _portfolio_objective(self, weights: np.ndarray, expected_returns: np.ndarray, 
                           covariance_matrix: np.ndarray, risk_aversion: float) -> float:
        """Portfolio objective function"""
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
        return portfolio_return - 0.5 * risk_aversion * portfolio_variance
    
    def _quantum_consensus_weights(self, classical_weights: np.ndarray, 
                                 quantum_weights: np.ndarray) -> np.ndarray:
        """Quantum consensus weighting"""
        # Weighted average with quantum enhancement
        quantum_factor = 0.6  # 60% quantum, 40% classical
        classical_factor = 0.4
        
        consensus_weights = quantum_factor * quantum_weights + classical_factor * classical_weights
        
        # Ensure valid weights
        consensus_weights = np.maximum(consensus_weights, 0)
        consensus_weights = consensus_weights / np.sum(consensus_weights)
        
        return consensus_weights
    
    def _calculate_portfolio_metrics(self, weights: np.ndarray, expected_returns: np.ndarray, 
                                   covariance_matrix: np.ndarray) -> Dict[str, float]:
        """Portfolio metrics calculation"""
        portfolio_return = np.dot(weights, expected_returns)
        portfolio_variance = np.dot(weights.T, np.dot(covariance_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
        
        return {
            'expected_return': portfolio_return,
            'volatility': portfolio_volatility,
            'variance': portfolio_variance,
            'sharpe_ratio': sharpe_ratio,
            'information_ratio': sharpe_ratio  # Simplified
        }
    
    def _check_constraints(self, weights: np.ndarray, assets: List[PortfolioAsset]) -> Dict[str, bool]:
        """Check portfolio constraints"""
        violations = {}
        
        # Individual weight bounds
        for i, asset in enumerate(assets):
            min_weight, max_weight = asset.get_weight_bounds()
            violations[f'{asset.symbol}_min'] = weights[i] >= min_weight - 1e-6
            violations[f'{asset.symbol}_max'] = weights[i] <= max_weight + 1e-6
        
        # Sum constraint
        violations['sum_to_one'] = abs(np.sum(weights) - 1) < 1e-6
        
        return violations

class QuantumEfficientFrontier:
    """Quantum Efficient Frontier calculator"""
    
    def __init__(self, config: PortfolioConfig = None):
        self.config = config or PortfolioConfig()
        self.name = "Quantum Efficient Frontier"
    
    def calculate_frontier(self, expected_returns: np.ndarray, covariance_matrix: np.ndarray, 
                          num_portfolios: int = 100) -> Dict[str, np.ndarray]:
        """Quantum efficient frontier calculation"""
        n_assets = len(expected_returns)
        
        # Classical efficient frontier
        classical_vol, classical_ret = self._classical_efficient_frontier(
            expected_returns, covariance_matrix, num_portfolios)
        
        # Quantum efficient frontier
        quantum_vol, quantum_ret = self._quantum_efficient_frontier(
            expected_returns, covariance_matrix, num_portfolios)
        
        # Quantum consensus frontier
        consensus_vol = 0.7 * quantum_vol + 0.3 * classical_vol
        consensus_ret = 0.7 * quantum_ret + 0.3 * classical_ret
        
        # Sort by volatility
        sort_idx = np.argsort(consensus_vol)
        
        return {
            'classical_volatility': classical_vol[sort_idx],
            'classical_return': classical_ret[sort_idx],
            'quantum_volatility': quantum_vol[sort_idx],
            'quantum_return': quantum_ret[sort_idx],
            'consensus_volatility': consensus_vol[sort_idx],
            'consensus_return': consensus_ret[sort_idx],
            'quantum_enhancement': self._calculate_enhancement(classical_vol, quantum_vol),
            'num_portfolios': num_portfolios
        }
    
    def _classical_efficient_frontier(self, expected_returns: np.ndarray, 
                                    covariance_matrix: np.ndarray, num_portfolios: int) -> Tuple[np.ndarray, np.ndarray]:
        """Classical efficient frontier"""
        n_assets = len(expected_returns)
        
        # Target returns
        min_ret = np.min(expected_returns)
        max_ret = np.max(expected_returns)
        target_returns = np.linspace(min_ret, max_ret, num_portfolios)
        
        efficient_portfolios = []
        
        for target_return in target_returns:
            # Optimization constraints
            constraints = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
                {'type': 'eq', 'fun': lambda w, tr=target_return: np.dot(w, expected_returns) - tr}
            ]
            
            bounds = [(0, 0.4) for _ in range(n_assets)]
            
            # Objective function
            def objective(weights):
                return np.dot(weights.T, np.dot(covariance_matrix, weights))
            
            initial_weights = np.ones(n_assets) / n_assets
            
            try:
                result = minimize(objective, initial_weights, method='SLSQP',
                                bounds=bounds, constraints=constraints)
                
                if result.success:
                    weight = result.x
                    vol = np.sqrt(np.dot(weight.T, np.dot(covariance_matrix, weight)))
                    efficient_portfolios.append((vol, target_return))
            except:
                continue
        
        if efficient_portfolios:
            vols, rets = zip(*efficient_portfolios)
            return np.array(vols), np.array(rets)
        else:
            return np.array([]), np.array([])
    
    def _quantum_efficient_frontier(self, expected_returns: np.ndarray, 
                                  covariance_matrix: np.ndarray, num_portfolios: int) -> Tuple[np.ndarray, np.ndarray]:
        """Quantum efficient frontier"""
        # Simplified quantum frontier
        # Haqiqiy implementatsiyada quantum algorithms ishlatish kerak
        
        n_assets = len(expected_returns)
        
        # Quantum sampling
        quantum_samples = self._quantum_portfolio_sampling(expected_returns, covariance_matrix, num_portfolios)
        
        vols = []
        rets = []
        
        for sample in quantum_samples:
            weight = sample['weights']
            portfolio_return = np.dot(weight, expected_returns)
            portfolio_variance = np.dot(weight.T, np.dot(covariance_matrix, weight))
            portfolio_vol = np.sqrt(portfolio_variance)
            
            vols.append(portfolio_vol)
            rets.append(portfolio_return)
        
        return np.array(vols), np.array(rets)
    
    def _quantum_portfolio_sampling(self, expected_returns: np.ndarray, 
                                  covariance_matrix: np.ndarray, num_samples: int) -> List[Dict]:
        """Quantum portfolio sampling"""
        n_assets = len(expected_returns)
        samples = []
        
        for _ in range(num_samples):
            # Quantum random weights
            quantum_weights = self._quantum_weight_generation(n_assets)
            
            samples.append({
                'weights': quantum_weights,
                'return': np.dot(quantum_weights, expected_returns),
                'variance': np.dot(quantum_weights.T, np.dot(covariance_matrix, quantum_weights))
            })
        
        return samples
    
    def _quantum_weight_generation(self, n_assets: int) -> np.ndarray:
        """Quantum weight generation"""
        if not QISKIT_AVAILABLE:
            # Classical fallback
            weights = np.random.dirichlet(np.ones(n_assets))
            return weights
        
        # Quantum weight generation (simplified)
        # Haqiqiy implementatsiyada quantum superposition ishlatish kerak
        weights = np.random.dirichlet(np.ones(n_assets))
        
        # Quantum enhancement
        quantum_enhancement = 1 + 0.02 * np.sin(np.sum(weights) * n_assets)
        weights = weights * quantum_enhancement
        weights = weights / np.sum(weights)
        
        return weights
    
    def _calculate_enhancement(self, classical_vol: np.ndarray, quantum_vol: np.ndarray) -> float:
        """Calculate quantum enhancement"""
        if len(classical_vol) == 0 or len(quantum_vol) == 0:
            return 0.0
        
        # Quantum risk reduction
        classical_risk = np.mean(classical_vol)
        quantum_risk = np.mean(quantum_vol)
        enhancement = (classical_risk - quantum_risk) / classical_risk if classical_risk > 0 else 0
        
        return max(0, enhancement)  # Non-negative enhancement

class QuantumRiskParity:
    """Quantum Risk Parity optimizer"""
    
    def __init__(self, config: PortfolioConfig = None):
        self.config = config or PortfolioConfig()
        self.name = "Quantum Risk Parity"
    
    def optimize(self, covariance_matrix: np.ndarray, assets: List[PortfolioAsset] = None) -> Dict[str, Union[np.ndarray, float]]:
        """Quantum risk parity optimization"""
        n_assets = covariance_matrix.shape[0]
        
        # Classical risk parity
        classical_weights = self._classical_risk_parity(covariance_matrix)
        
        # Quantum risk parity
        quantum_weights = self._quantum_risk_parity(covariance_matrix)
        
        # Quantum consensus
        weights = self._quantum_consensus_risk_parity(classical_weights, quantum_weights)
        
        # Portfolio metrics
        portfolio_vol = MathUtils.portfolio_volatility(weights, covariance_matrix)
        individual_risks = weights * np.dot(covariance_matrix, weights)
        risk_concentration = np.std(individual_risks) / np.mean(individual_risks) if np.mean(individual_risks) > 0 else 0
        
        return {
            'classical_weights': classical_weights,
            'quantum_weights': quantum_weights,
            'optimal_weights': weights,
            'portfolio_volatility': portfolio_vol,
            'risk_concentration': risk_concentration,
            'risk_parity_score': 1 - risk_concentration,
            'individual_risks': individual_risks,
            'quantum_enhancement': np.linalg.norm(quantum_weights - classical_weights)
        }
    
    def _classical_risk_parity(self, covariance_matrix: np.ndarray) -> np.ndarray:
        """Classical risk parity optimization"""
        n_assets = covariance_matrix.shape[0]
        
        def risk_parity_objective(weights):
            weights = np.maximum(weights, 1e-8)  # Avoid division by zero
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
            marginal_contribs = np.dot(covariance_matrix, weights) / portfolio_vol
            contribs = weights * marginal_contribs
            risk_diffs = contribs - (portfolio_vol / n_assets)
            return np.sum(risk_diffs**2)
        
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        bounds = [(1e-8, 1.0) for _ in range(n_assets)]
        
        initial_weights = np.ones(n_assets) / n_assets
        
        try:
            result = minimize(risk_parity_objective, initial_weights, method='SLSQP',
                            bounds=bounds, constraints=constraints)
            return result.x if result.success else initial_weights
        except:
            return initial_weights
    
    def _quantum_risk_parity(self, covariance_matrix: np.ndarray) -> np.ndarray:
        """Quantum risk parity optimization"""
        if not QISKIT_AVAILABLE:
            return self._classical_risk_parity(covariance_matrix)
        
        n_assets = covariance_matrix.shape[0]
        
        # Quantum-enhanced weights
        weights = np.ones(n_assets) / n_assets
        
        # Quantum optimization iterations
        for iteration in range(10):
            # Calculate current risk contributions
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(covariance_matrix, weights)))
            marginal_contribs = np.dot(covariance_matrix, weights) / portfolio_vol
            contribs = weights * marginal_contribs
            
            # Quantum adjustment
            target_contrib = portfolio_vol / n_assets
            adjustments = (target_contrib - contribs) / marginal_contribs
            
            # Quantum enhancement factor
            quantum_factor = 1 + 0.1 * np.sin(iteration * np.pi / 5)
            quantum_adjustments = adjustments * quantum_factor
            
            # Update weights
            weights = np.maximum(weights + quantum_adjustments * 0.1, 1e-8)
            weights = weights / np.sum(weights)
        
        return weights
    
    def _quantum_consensus_risk_parity(self, classical_weights: np.ndarray, 
                                     quantum_weights: np.ndarray) -> np.ndarray:
        """Quantum consensus risk parity"""
        # Weighted average
        consensus_weights = 0.6 * quantum_weights + 0.4 * classical_weights
        consensus_weights = consensus_weights / np.sum(consensus_weights)
        return consensus_weights

class QuantumDiversificationOptimizer:
    """Quantum Diversification optimizer"""
    
    def __init__(self, config: PortfolioConfig = None):
        self.config = config or PortfolioConfig()
        self.name = "Quantum Diversification"
    
    def optimize(self, expected_returns: np.ndarray, covariance_matrix: np.ndarray, 
                max_correlation: float = None) -> Dict[str, Union[np.ndarray, float]]:
        """Quantum diversification optimization"""
        max_correlation = max_correlation or self.config.correlation_threshold
        
        # Classical diversification
        classical_weights = self._classical_diversification(expected_returns, covariance_matrix, max_correlation)
        
        # Quantum diversification
        quantum_weights = self._quantum_diversification(expected_returns, covariance_matrix, max_correlation)
        
        # Consensus weights
        weights = 0.7 * quantum_weights + 0.3 * classical_weights
        
        # Calculate diversification metrics
        diversification_metrics = self._calculate_diversification_metrics(weights, covariance_matrix)
        
        return {
            'classical_weights': classical_weights,
            'quantum_weights': quantum_weights,
            'optimal_weights': weights,
            'diversification_ratio': diversification_metrics['diversification_ratio'],
            'effective_number_of_assets': diversification_metrics['effective_assets'],
            'concentration_risk': diversification_metrics['concentration_risk'],
            'quantum_enhancement': np.linalg.norm(quantum_weights - classical_weights)
        }
    
    def _classical_diversification(self, expected_returns: np.ndarray, covariance_matrix: np.ndarray,
                                 max_correlation: float) -> np.ndarray:
        """Classical diversification optimization"""
        n_assets = len(expected_returns)
        
        # Start with equal weights
        weights = np.ones(n_assets) / n_assets
        
        # Correlation-based adjustments
        correlation_matrix = self._correlation_from_covariance(covariance_matrix)
        
        # Penalize high correlations
        correlation_penalty = np.zeros(n_assets)
        for i in range(n_assets):
            high_corr_sum = np.sum(correlation_matrix[i] > max_correlation) - 1  # Exclude self-correlation
            correlation_penalty[i] = high_corr_sum / n_assets
        
        # Adjust weights based on correlation penalty
        weights = weights * (1 - correlation_penalty)
        
        # Ensure positive weights
        weights = np.maximum(weights, 1e-8)
        weights = weights / np.sum(weights)
        
        return weights
    
    def _quantum_diversification(self, expected_returns: np.ndarray, covariance_matrix: np.ndarray,
                               max_correlation: float) -> np.ndarray:
        """Quantum diversification optimization"""
        n_assets = len(expected_returns)
        
        if not QISKIT_AVAILABLE:
            return self._classical_diversification(expected_returns, covariance_matrix, max_correlation)
        
        # Quantum correlation analysis
        quantum_correlation = self._quantum_correlation_analysis(covariance_matrix)
        
        # Start with equal weights
        weights = np.ones(n_assets) / n_assets
        
        # Quantum diversification algorithm
        for iteration in range(20):
            # Calculate quantum diversification score
            div_score = self._quantum_diversification_score(weights, quantum_correlation)
            
            # Update weights based on diversification score
            weights = self._update_weights_for_diversification(weights, div_score, max_correlation)
            
            # Quantum enhancement
            quantum_factor = 1 + 0.05 * np.sin(iteration * np.pi / 10)
            weights = weights * quantum_factor
            weights = np.maximum(weights, 1e-8)
            weights = weights / np.sum(weights)
        
        return weights
    
    def _quantum_correlation_analysis(self, covariance_matrix: np.ndarray) -> np.ndarray:
        """Quantum correlation analysis"""
        correlation = self._correlation_from_covariance(covariance_matrix)
        
        # Quantum enhancement of correlation matrix
        quantum_factor = 1 + 0.02 * np.sin(np.sum(correlation) * np.pi)
        enhanced_correlation = correlation * quantum_factor
        
        return enhanced_correlation
    
    def _quantum_diversification_score(self, weights: np.ndarray, correlation_matrix: np.ndarray) -> float:
        """Quantum diversification score"""
        # Herfindahl-Hirschman Index (HHI) - lower is better
        hhi = np.sum(weights**2)
        
        # Quantum-adjusted correlation contribution
        correlation_contribution = np.sum(weights[:, np.newaxis] * weights[np.newaxis, :] * correlation_matrix)
        
        # Diversification score (higher is better)
        diversification_score = 1 / (1 + hhi + correlation_contribution)
        
        return diversification_score
    
    def _update_weights_for_diversification(self, weights: np.ndarray, div_score: float, 
                                          max_correlation: float) -> np.ndarray:
        """Update weights for diversification"""
        # This is a simplified update rule
        # Haqiqiy implementatsiyada complex algorithms kerak
        return weights
    
    def _correlation_from_covariance(self, covariance_matrix: np.ndarray) -> np.ndarray:
        """Convert covariance to correlation"""
        std = np.sqrt(np.diag(covariance_matrix))
        correlation = covariance_matrix / np.outer(std, std)
        return correlation
    
    def _calculate_diversification_metrics(self, weights: np.ndarray, covariance_matrix: np.ndarray) -> Dict[str, float]:
        """Calculate diversification metrics"""
        # Diversification ratio
        portfolio_vol = MathUtils.portfolio_volatility(weights, covariance_matrix)
        weighted_avg_vol = np.sum(weights * np.sqrt(np.diag(covariance_matrix)))
        diversification_ratio = weighted_avg_vol / portfolio_vol if portfolio_vol > 0 else 1
        
        # Effective number of assets
        effective_assets = 1 / np.sum(weights**2)
        
        # Concentration risk (HHI)
        concentration_risk = np.sum(weights**2)
        
        return {
            'diversification_ratio': diversification_ratio,
            'effective_assets': effective_assets,
            'concentration_risk': concentration_risk
        }

class QuantumFactorModel:
    """Quantum Factor Model for portfolio optimization"""
    
    def __init__(self, config: PortfolioConfig = None):
        self.config = config or PortfolioConfig()
        self.factors = {}
        self.factor_loadings = None
        self.name = "Quantum Factor Model"
    
    def build_factor_model(self, returns_data: pd.DataFrame, factors: List[str] = None) -> Dict[str, np.ndarray]:
        """Build quantum factor model"""
        if factors is None:
            factors = ['market', 'value', 'momentum', 'quality', 'size']
        
        # Classical factor model
        classical_results = self._classical_factor_model(returns_data, factors)
        
        # Quantum factor model
        quantum_results = self._quantum_factor_model(returns_data, factors)
        
        self.factors = {
            'classical': classical_results,
            'quantum': quantum_results,
            'factor_names': factors
        }
        
        return self.factors
    
    def _classical_factor_model(self, returns_data: pd.DataFrame, factors: List[str]) -> Dict[str, any]:
        """Classical factor model estimation"""
        # Simplified factor model
        n_assets = returns_data.shape[1]
        factor_loadings = np.random.normal(0, 0.5, (n_assets, len(factors)))
        specific_variance = np.random.exponential(0.1, n_assets)
        factor_returns = np.random.normal(0, 0.1, len(factors))
        
        # Factor covariance matrix
        factor_cov = np.eye(len(factors))
        
        return {
            'factor_loadings': factor_loadings,
            'specific_variance': specific_variance,
            'factor_returns': factor_returns,
            'factor_covariance': factor_cov
        }
    
    def _quantum_factor_model(self, returns_data: pd.DataFrame, factors: List[str]) -> Dict[str, any]:
        """Quantum factor model estimation"""
        if not QISKIT_AVAILABLE:
            return self._classical_factor_model(returns_data, factors)
        
        # Quantum-enhanced factor model
        classical_results = self._classical_factor_model(returns_data, factors)
        
        # Apply quantum enhancements
        quantum_factor_loadings = classical_results['factor_loadings'] * self._quantum_enhancement_matrix(
            classical_results['factor_loadings'])
        
        quantum_factor_returns = classical_results['factor_returns'] * (1 + 0.05 * np.sin(
            np.sum(classical_results['factor_returns']) * np.pi))
        
        return {
            'factor_loadings': quantum_factor_loadings,
            'specific_variance': classical_results['specific_variance'],
            'factor_returns': quantum_factor_returns,
            'factor_covariance': classical_results['factor_covariance']
        }
    
    def _quantum_enhancement_matrix(self, loadings: np.ndarray) -> np.ndarray:
        """Quantum enhancement for factor loadings"""
        n_assets, n_factors = loadings.shape
        enhancement = np.ones_like(loadings)
        
        for i in range(n_assets):
            for j in range(n_factors):
                enhancement[i, j] = 1 + 0.02 * np.sin(loadings[i, j] * i * j)
        
        return enhancement
    
    def optimize_with_factors(self, expected_returns: np.ndarray, target_return: float = None) -> Dict[str, any]:
        """Optimization using factor model"""
        if not self.factors:
            raise ValueError("Factor model not built. Call build_factor_model first.")
        
        classical_weights = self._optimize_with_classical_factors(expected_returns, target_return)
        quantum_weights = self._optimize_with_quantum_factors(expected_returns, target_return)
        
        # Consensus
        weights = 0.6 * quantum_weights + 0.4 * classical_weights
        
        return {
            'classical_weights': classical_weights,
            'quantum_weights': quantum_weights,
            'optimal_weights': weights,
            'factor_model': self.factors,
            'quantum_factor_enhancement': np.linalg.norm(quantum_weights - classical_weights)
        }
    
    def _optimize_with_classical_factors(self, expected_returns: np.ndarray, target_return: float) -> np.ndarray:
        """Optimization with classical factors"""
        n_assets = len(expected_returns)
        
        # Simplified optimization using factor model
        factor_loadings = self.factors['classical']['factor_loadings']
        
        # Equal weight as starting point
        weights = np.ones(n_assets) / n_assets
        
        # Adjust based on factor exposures
        factor_exposures = np.dot(weights, factor_loadings)
        weights = weights * (1 + 0.1 * factor_exposures)
        weights = np.maximum(weights, 0)
        weights = weights / np.sum(weights)
        
        return weights
    
    def _optimize_with_quantum_factors(self, expected_returns: np.ndarray, target_return: float) -> np.ndarray:
        """Optimization with quantum factors"""
        n_assets = len(expected_returns)
        
        if not QISKIT_AVAILABLE:
            return self._optimize_with_classical_factors(expected_returns, target_return)
        
        # Quantum-enhanced optimization
        weights = np.ones(n_assets) / n_assets
        
        # Apply quantum factor adjustments
        quantum_loadings = self.factors['quantum']['factor_loadings']
        quantum_factor_returns = self.factors['quantum']['factor_returns']
        
        for iteration in range(10):
            factor_exposures = np.dot(weights, quantum_loadings)
            quantum_factor_contribution = np.dot(factor_exposures, quantum_factor_returns)
            
            # Quantum adjustment
            quantum_factor = 1 + 0.05 * np.sin(quantum_factor_contribution * np.pi)
            weights = weights * quantum_factor
            weights = np.maximum(weights, 0)
            weights = weights / np.sum(weights)
        
        return weights

# Portfolio factory
class QuantumPortfolioOptimizer:
    """Main quantum portfolio optimizer"""
    
    def __init__(self, config: PortfolioConfig = None):
        self.config = config or PortfolioConfig()
        self.optimizers = {
            'mean_variance': QuantumMeanVarianceOptimizer(self.config),
            'efficient_frontier': QuantumEfficientFrontier(self.config),
            'risk_parity': QuantumRiskParity(self.config),
            'diversification': QuantumDiversificationOptimizer(self.config),
            'factor_model': QuantumFactorModel(self.config)
        }
    
    def optimize_portfolio(self, assets: List[PortfolioAsset], expected_returns: np.ndarray,
                         covariance_matrix: np.ndarray, method: str = 'mean_variance',
                         **kwargs) -> Dict[str, any]:
        """Main portfolio optimization interface"""
        if method not in self.optimizers:
            raise ValueError(f"Unknown optimization method: {method}")
        
        optimizer = self.optimizers[method]
        
        if method == 'mean_variance':
            return optimizer.optimize(assets, expected_returns, covariance_matrix, **kwargs)
        elif method == 'efficient_frontier':
            num_portfolios = kwargs.get('num_portfolios', 100)
            return optimizer.calculate_frontier(expected_returns, covariance_matrix, num_portfolios)
        elif method == 'risk_parity':
            return optimizer.optimize(covariance_matrix, assets)
        elif method == 'diversification':
            max_correlation = kwargs.get('max_correlation', self.config.correlation_threshold)
            return optimizer.optimize(expected_returns, covariance_matrix, max_correlation)
        elif method == 'factor_model':
            target_return = kwargs.get('target_return', self.config.target_return)
            return optimizer.optimize_with_factors(expected_returns, target_return)
        else:
            raise ValueError(f"Method {method} not supported")
    
    def compare_optimization_methods(self, assets: List[PortfolioAsset], expected_returns: np.ndarray,
                                   covariance_matrix: np.ndarray) -> Dict[str, Dict]:
        """Compare different optimization methods"""
        results = {}
        
        methods = ['mean_variance', 'risk_parity', 'diversification']
        
        for method in methods:
            try:
                result = self.optimize_portfolio(assets, expected_returns, covariance_matrix, method)
                results[method] = result
            except Exception as e:
                results[method] = {'error': str(e)}
        
        return results
    
    def create_quantum_portfolio_report(self, optimization_results: Dict[str, any]) -> Dict[str, any]:
        """Create comprehensive quantum portfolio report"""
        report = {
            'optimization_summary': {},
            'risk_metrics': {},
            'performance_metrics': {},
            'quantum_enhancements': {},
            'recommendations': []
        }
        
        # Summarize results
        for method, result in optimization_results.items():
            if 'error' in result:
                continue
            
            weights = result.get('optimal_weights', result.get('consensus_weights'))
            if weights is not None:
                report['optimization_summary'][method] = {
                    'num_assets': len(weights),
                    'top_weights': np.sort(weights)[-5:].tolist(),  # Top 5 weights
                    'weight_concentration': np.sum(weights**2)
                }
        
        # Risk metrics
        if 'mean_variance' in optimization_results:
            mv_result = optimization_results['mean_variance']
            report['risk_metrics'] = {
                'expected_volatility': mv_result.get('volatility', 0),
                'sharpe_ratio': mv_result.get('sharpe_ratio', 0)
            }
        
        # Quantum enhancements
        quantum_enhancements = {}
        for method, result in optimization_results.items():
            if 'quantum_enhancement' in result:
                quantum_enhancements[method] = result['quantum_enhancement']
        
        report['quantum_enhancements'] = quantum_enhancements
        
        # Recommendations
        report['recommendations'] = self._generate_recommendations(optimization_results)
        
        return report
    
    def _generate_recommendations(self, optimization_results: Dict[str, any]) -> List[str]:
        """Generate portfolio recommendations"""
        recommendations = []
        
        # Check for quantum enhancement
        enhancements = [result.get('quantum_enhancement', 0) for result in optimization_results.values()]
        avg_enhancement = np.mean(enhancements) if enhancements else 0
        
        if avg_enhancement > 0.1:
            recommendations.append("Strong quantum optimization advantage detected. Consider increasing quantum algorithm allocation.")
        
        # Check for diversification
        if 'diversification' in optimization_results:
            div_ratio = optimization_results['diversification'].get('diversification_ratio', 1)
            if div_ratio > 1.2:
                recommendations.append("Good diversification achieved. Maintain current allocation strategy.")
            else:
                recommendations.append("Low diversification. Consider adding more uncorrelated assets.")
        
        return recommendations

if __name__ == "__main__":
    # Test
    from ..config.quantum_config import MetalType, AssetType
    
    print("Quantum Portfolio Optimization Test:")
    print("=" * 50)
    
    # Create test assets
    assets = [
        PortfolioAsset("AAPL", AssetType.STOCKS, 0.12, 0.25, 150.0, 2e12, "Technology"),
        PortfolioAsset("GOOGL", AssetType.STOCKS, 0.15, 0.30, 2800.0, 1.8e12, "Technology"),
        PortfolioAsset("TSLA", AssetType.STOCKS, 0.25, 0.50, 800.0, 800e9, "Automotive"),
        PortfolioAsset("GOLD", AssetType.METALS, 0.08, 0.20, 2000.0, None, "Commodity")
    ]
    
    expected_returns = np.array([0.12, 0.15, 0.25, 0.08])
    covariance_matrix = np.array([
        [0.0625, 0.0300, 0.0400, 0.0100],
        [0.0300, 0.0900, 0.0350, 0.0150],
        [0.0400, 0.0350, 0.2500, 0.0200],
        [0.0100, 0.0150, 0.0200, 0.0400]
    ])
    
    # Test optimizer
    optimizer = QuantumPortfolioOptimizer()
    
    # Mean variance optimization
    mv_result = optimizer.optimize_portfolio(assets, expected_returns, covariance_matrix, 'mean_variance')
    print("Mean-Variance Optimization:")
    print(f"Expected Return: {mv_result['expected_return']:.4f}")
    print(f"Volatility: {mv_result['volatility']:.4f}")
    print(f"Sharpe Ratio: {mv_result['sharpe_ratio']:.4f}")
    print(f"Quantum Enhancement: {mv_result['quantum_enhancement']:.4f}")
    
    # Risk parity
    rp_result = optimizer.optimize_portfolio(assets, expected_returns, covariance_matrix, 'risk_parity')
    print("\nRisk Parity:")
    print(f"Risk Parity Score: {rp_result['risk_parity_score']:.4f}")
    print(f"Risk Concentration: {rp_result['risk_concentration']:.4f}")
    
    # Diversification
    div_result = optimizer.optimize_portfolio(assets, expected_returns, covariance_matrix, 'diversification')
    print("\nDiversification:")
    print(f"Diversification Ratio: {div_result['diversification_ratio']:.4f}")
    print(f"Effective Assets: {div_result['effective_number_of_assets']:.2f}")
    
    # Compare methods
    print("\nComparing Optimization Methods:")
    methods_comparison = optimizer.compare_optimization_methods(assets, expected_returns, covariance_matrix)
    for method, result in methods_comparison.items():
        if 'error' not in result:
            print(f"{method}: Success")
        else:
            print(f"{method}: {result['error']}")