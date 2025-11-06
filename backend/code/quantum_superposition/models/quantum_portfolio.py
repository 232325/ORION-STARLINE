"""
Quantum Portfolio Model
======================

Quantum superposition nazariyasi asosida portfolio optimization model.
"""

import numpy as np
import cmath
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
from scipy.optimize import minimize, differential_evolution
from scipy.linalg import norm, eigh
import matplotlib.pyplot as plt

try:
    from ..core.quantum_state import QuantumPortfolioState
    from ..core.superposition import QuantumSuperposition, SuperpositionConfig
    from ..core.measurement import QuantumMeasurement, MeasurementConfig
    from ..core.entanglement import QuantumEntanglement
except ImportError:
    # Fallback for standalone execution
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from core.quantum_state import QuantumPortfolioState
    from core.superposition import QuantumSuperposition, SuperpositionConfig
    from core.measurement import QuantumMeasurement, MeasurementConfig
    from core.entanglement import QuantumEntanglement


@dataclass
class QuantumPortfolioConfig:
    """Quantum portfolio konfiguratsiya parametrlari"""
    target_return: float = 0.1
    risk_aversion: float = 1.0
    quantum_coherence_time: int = 100
    entanglement_strength: float = 0.8
    measurement_precision: float = 0.95
    diversification_threshold: float = 0.3
    max_quantum_assets: int = 10
    rebalancing_frequency: int = 30


class QuantumPortfolioModel:
    """
    Quantum Portfolio Model
    
    Quantum superposition va entanglement asosida portfolio optimization.
    """
    
    def __init__(self, config: QuantumPortfolioConfig = None):
        self.config = config or QuantumPortfolioConfig()
        self.portfolio_state = None
        self.quantum_optimizer = QuantumSuperposition()
        self.measurement_engine = QuantumMeasurement()
        self.entanglement_manager = QuantumEntanglement()
        
        self.performance_history = []
        self.risk_history = []
        self.quantum_metrics = {}
        
    def initialize_portfolio(self, assets: List[str], 
                           returns_data: np.ndarray = None,
                           initial_weights: np.ndarray = None) -> QuantumPortfolioState:
        """
        Portfolio'ni quantum holatda initialize qilish
        
        Args:
            assets: Portfolio assetlari
            returns_data: Historical returns ma'lumotlari
            initial_weights: Boshlang'ich weightlar
        
        Returns:
            Initialized quantum portfolio state
        """
        if len(assets) > self.config.max_quantum_assets:
            raise ValueError(f"Juda ko'p asset: maksimal {self.config.max_quantum_assets} ta")
        
        if initial_weights is None:
            if returns_data is not None:
                # Returns asosida smart initialization
                mean_returns = np.mean(returns_data, axis=1)
                positive_returns = np.maximum(mean_returns, 0.001)
                initial_weights = positive_returns / np.sum(positive_returns)
            else:
                # Equal weights
                initial_weights = np.ones(len(assets)) / len(assets)
        
        self.portfolio_state = QuantumPortfolioState(assets, initial_weights)
        return self.portfolio_state
    
    def quantum_optimization(self, returns_data: np.ndarray,
                           covariance_matrix: np.ndarray = None,
                           constraints: Dict = None) -> Dict:
        """
        Quantum optimization algoritmi
        
        Args:
            returns_data: Returns ma'lumotlari
            covariance_matrix: Covariance matrix
            constraints: Qo'shimcha cheklovlar
        
        Returns:
            Optimization natijasi
        """
        if self.portfolio_state is None:
            raise ValueError("Portfolio initialize qilinmagan")
        
        def quantum_objective_function(weights):
            """Quantum objective function"""
            # Weights normalization
            weights = weights / norm(weights)
            
            # Quantum state yaratish
            temp_portfolio = QuantumPortfolioState(self.portfolio_state.assets, weights)
            
            # Expected return
            expected_return = temp_portfolio.get_expected_return(returns_data)
            
            # Quantum risk (variance)
            if covariance_matrix is not None:
                quantum_risk = temp_portfolio.get_risk(covariance_matrix)
            else:
                quantum_risk = np.sqrt(np.sum(weights**2 * 0.15**2))  # Simplified risk
            
            # Quantum entanglement penalty
            entanglement_penalty = 0
            if len(self.portfolio_state.assets) > 1:
                for i in range(len(weights)):
                    for j in range(i+1, len(weights)):
                        if abs(weights[i] * weights[j]) > 0.1:
                            entanglement_penalty += abs(weights[i] * weights[j]) * 0.01
            
            # Multi-objective function
            risk_adjusted_return = expected_return - self.config.risk_aversion * quantum_risk
            quantum_penalty = -entanglement_penalty
            
            return -(risk_adjusted_return + quantum_penalty)  # Minimize negative
        
        # Constraints
        constraint_list = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},  # Weight sum = 1
            {'type': 'ineq', 'fun': lambda x: np.min(x) - 0.01},  # Minimum weight
            {'type': 'ineq', 'fun': lambda x: 0.99 - np.max(x)}   # Maximum weight
        ]
        
        # Add custom constraints
        if constraints:
            for key, value in constraints.items():
                if key == 'max_single_weight':
                    constraint_list.append({
                        'type': 'ineq', 
                        'fun': lambda x, v=value: v - np.max(x)
                    })
                elif key == 'min_diversification':
                    # Diversification constraint
                    def diversification_constraint(x):
                        hhi = np.sum(x**2)  # Herfindahl-Hirschman Index
                        return 1 - hhi - v
                    
                    constraint_list.append({
                        'type': 'ineq',
                        'fun': diversification_constraint
                    })
        
        # Bounds
        bounds = [(0.01, 0.8) for _ in range(len(self.portfolio_state.assets))]
        
        # Optimization methods comparison
        methods = ['SLSQP', 'differential_evolution']
        results = {}
        
        for method in methods:
            try:
                if method == 'differential_evolution':
                    result = differential_evolution(
                        quantum_objective_function,
                        bounds,
                        seed=42,
                        maxiter=100
                    )
                else:
                    x0 = np.ones(len(self.portfolio_state.assets)) / len(self.portfolio_state.assets)
                    result = minimize(
                        quantum_objective_function,
                        x0,
                        method=method,
                        bounds=bounds,
                        constraints=constraint_list
                    )
                
                # Calculate final metrics
                optimal_weights = result.x / norm(result.x)
                final_portfolio = QuantumPortfolioState(self.portfolio_state.assets, optimal_weights)
                
                final_return = final_portfolio.get_expected_return(returns_data)
                final_risk = (final_portfolio.get_risk(covariance_matrix) 
                            if covariance_matrix is not None 
                            else np.sqrt(np.sum(optimal_weights**2 * 0.15**2)))
                
                results[method] = {
                    'success': result.success,
                    'optimal_weights': optimal_weights,
                    'expected_return': final_return,
                    'quantum_risk': final_risk,
                    'sharpe_ratio': final_return / final_risk if final_risk > 0 else 0,
                    'quantum_coherence': self._calculate_quantum_coherence(optimal_weights),
                    'entanglement_strength': self._calculate_entanglement_strength(optimal_weights),
                    'optimization_details': result
                }
                
            except Exception as e:
                results[method] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Select best result
        best_method = max(results.keys(), 
                         key=lambda k: results[k].get('sharpe_ratio', 0) 
                         if results[k].get('success', False) else 0)
        
        best_result = results[best_method]
        
        if best_result['success']:
            # Update portfolio state
            self.portfolio_state.set_portfolio_state(best_result['optimal_weights'])
            
            # Store metrics
            self.quantum_metrics.update({
                'optimization_method': best_method,
                'quantum_coherence': best_result['quantum_coherence'],
                'entanglement_strength': best_result['entanglement_strength'],
                'convergence_iterations': best_result['optimization_details'].get('nit', 0)
            })
        
        return {
            'optimization_results': results,
            'best_method': best_method,
            'best_result': best_result,
            'quantum_metrics': self.quantum_metrics
        }
    
    def quantum_diversification(self, target_diversification: float = 0.5) -> Dict:
        """
        Quantum diversifikatsiya strategiyasi
        
        Args:
            target_diversification: Maqsad diversifikatsiya darajasi
        
        Returns:
            Diversifikatsiya analizi
        """
        if self.portfolio_state is None:
            raise ValueError("Portfolio initialize qilinmagan")
        
        weights = self.portfolio_state.get_portfolio_weights()
        
        # Traditional diversification metrics
        hhi = np.sum(weights**2)  # Herfindahl-Hirschman Index
        effective_assets = 1 / hhi
        current_diversification = 1 - hhi
        
        # Quantum diversification
        amplitudes = self.portfolio_state.state.amplitudes
        quantum_entanglement = np.sum(np.abs(amplitudes)**4)
        quantum_coherence = 1 - quantum_entanglement
        
        # Asset-level correlations
        asset_correlations = {}
        for i, asset1 in enumerate(self.portfolio_state.assets):
            for j, asset2 in enumerate(self.portfolio_state.assets):
                if i < j:
                    correlation = self._calculate_asset_correlation(asset1, asset2)
                    asset_correlations[f"{asset1}_{asset2}"] = correlation
        
        # Diversification optimization
        optimal_weights = self._optimize_quantum_diversification(
            weights, target_diversification
        )
        
        # Diversification improvements
        new_portfolio = QuantumPortfolioState(self.portfolio_state.assets, optimal_weights)
        new_hhi = np.sum(optimal_weights**2)
        new_diversification = 1 - new_hhi
        improvement = new_diversification - current_diversification
        
        return {
            'current_diversification': current_diversification,
            'target_diversification': target_diversification,
            'quantum_coherence': quantum_coherence,
            'effective_assets': effective_assets,
            'hhi': hhi,
            'asset_correlations': asset_correlations,
            'optimal_weights': optimal_weights,
            'improved_diversification': new_diversification,
            'improvement': improvement,
            'diversification_achieved': new_diversification >= target_diversification,
            'quantum_entanglement': quantum_entanglement
        }
    
    def quantum_rebalancing(self, returns_data: np.ndarray,
                          rebalancing_threshold: float = 0.05) -> Dict:
        """
        Quantum rebalancing strategy
        
        Args:
            returns_data: Returns ma'lumotlari
            rebalancing_threshold: Rebalancing threshold
        
        Returns:
            Rebalancing qaror va natijalar
        """
        current_weights = self.portfolio_state.get_portfolio_weights()
        
        # Current performance
        current_return = self.portfolio_state.get_expected_return(returns_data)
        current_risk = np.sqrt(np.sum(current_weights**2 * 0.15**2))
        
        # Target weights (optimized)
        target_result = self.quantum_optimization(returns_data)
        target_weights = target_result['best_result']['optimal_weights']
        
        # Calculate deviations
        weight_deviations = np.abs(current_weights - target_weights)
        max_deviation = np.max(weight_deviations)
        mean_deviation = np.mean(weight_deviations)
        
        # Rebalancing decision
        needs_rebalancing = max_deviation > rebalancing_threshold
        
        if needs_rebalancing:
            # Execute rebalancing
            self.portfolio_state.set_portfolio_state(target_weights)
            
            # Calculate rebalancing impact
            new_return = self.portfolio_state.get_expected_return(returns_data)
            new_risk = np.sqrt(np.sum(target_weights**2 * 0.15**2))
            
            return_impact = new_return - current_return
            risk_impact = new_risk - current_risk
            
            # Transaction costs (simplified)
            transaction_costs = np.sum(weight_deviations) * 0.001  # 0.1% per unit
            
            net_improvement = return_impact - transaction_costs
            
            rebalancing_action = 'EXECUTED'
            performance_impact = net_improvement
        else:
            # No rebalancing needed
            rebalancing_action = 'SKIPPED'
            performance_impact = 0
            return_impact = 0
            risk_impact = 0
            transaction_costs = 0
        
        return {
            'action': rebalancing_action,
            'current_weights': current_weights,
            'target_weights': target_weights,
            'weight_deviations': weight_deviations,
            'max_deviation': max_deviation,
            'mean_deviation': mean_deviation,
            'rebalancing_threshold': rebalancing_threshold,
            'needs_rebalancing': needs_rebalancing,
            'return_impact': return_impact,
            'risk_impact': risk_impact,
            'transaction_costs': transaction_costs,
            'net_performance_impact': performance_impact,
            'quantum_metrics': self.quantum_metrics
        }
    
    def quantum_risk_management(self, risk_budget: float = 0.15,
                              stress_scenarios: Dict = None) -> Dict:
        """
        Quantum risk management
        
        Args:
            risk_budget: Risk budget
            stress_scenarios: Stress test senariylari
        
        Returns:
            Risk management natijalari
        """
        if self.portfolio_state is None:
            raise ValueError("Portfolio initialize qilinmagan")
        
        weights = self.portfolio_state.get_portfolio_weights()
        current_risk = np.sqrt(np.sum(weights**2 * 0.15**2))
        
        # Current risk assessment
        risk_utilization = current_risk / risk_budget if risk_budget > 0 else 0
        
        # Quantum risk measures
        quantum_var = self._calculate_quantum_var(weights)
        quantum_es = self._calculate_quantum_expected_shortfall(weights)
        
        # Stress testing
        stress_results = {}
        if stress_scenarios:
            for scenario_name, scenario in stress_scenarios.items():
                stressed_weights = self._apply_stress_scenario(weights, scenario)
                stressed_risk = np.sqrt(np.sum(stressed_weights**2 * 0.15**2))
                stress_impact = stressed_risk - current_risk
                
                stress_results[scenario_name] = {
                    'stressed_risk': stressed_risk,
                    'risk_increase': stress_impact,
                    'stress_ratio': stressed_risk / current_risk,
                    'stressed_weights': stressed_weights
                }
        
        # Risk alerts
        alerts = []
        if risk_utilization > 0.8:
            alerts.append("HIGH_RISK_UTILIZATION")
        if current_risk > risk_budget:
            alerts.append("RISK_BUDGET_EXCEEDED")
        if quantum_var > risk_budget * 1.5:
            alerts.append("HIGH_QUANTUM_VAR")
        
        # Risk mitigation recommendations
        recommendations = self._generate_risk_recommendations(
            weights, current_risk, risk_budget, risk_utilization
        )
        
        return {
            'current_risk': current_risk,
            'risk_budget': risk_budget,
            'risk_utilization': risk_utilization,
            'quantum_var': quantum_var,
            'quantum_expected_shortfall': quantum_es,
            'stress_results': stress_results,
            'alerts': alerts,
            'recommendations': recommendations,
            'quantum_risk_premium': (quantum_var - current_risk) / current_risk if current_risk > 0 else 0
        }
    
    def quantum_performance_attribution(self, returns_data: np.ndarray,
                                      benchmark_weights: np.ndarray = None) -> Dict:
        """
        Quantum performance attribution
        
        Args:
            returns_data: Returns ma'lumotlari
            benchmark_weights: Benchmark weightlar
        
        Returns:
            Performance attribution analizi
        """
        if self.portfolio_state is None:
            raise ValueError("Portfolio initialize qilinmagan")
        
        weights = self.portfolio_state.get_portfolio_weights()
        assets = self.portfolio_state.assets
        
        # Total portfolio return
        portfolio_return = self.portfolio_state.get_expected_return(returns_data)
        
        # Asset-level contributions
        asset_contributions = {}
        for i, asset in enumerate(assets):
            if i < len(returns_data):
                asset_return = np.mean(returns_data[i])
                weight_contribution = weights[i] * asset_return
                asset_contributions[asset] = {
                    'weight': weights[i],
                    'return': asset_return,
                    'contribution': weight_contribution,
                    'selection_effect': weight_contribution - weights[i] * portfolio_return
                }
        
        # Total selection effect
        total_selection_effect = sum(asset['selection_effect'] 
                                   for asset in asset_contributions.values())
        
        # Allocation effect (if benchmark provided)
        allocation_effect = 0
        benchmark_contribution = 0
        if benchmark_weights is not None:
            # Simplified allocation effect
            for i, asset in enumerate(assets):
                if i < len(benchmark_weights):
                    benchmark_weight = benchmark_weights[i] if i < len(benchmark_weights) else 0
                    weight_diff = weights[i] - benchmark_weight
                    benchmark_asset_return = 0.1 if i < len(returns_data) else 0  # Simplified
                    allocation_effect += weight_diff * benchmark_asset_return
                    benchmark_contribution += benchmark_weight * benchmark_asset_return
        
        # Quantum effects
        quantum_effect = self._calculate_quantum_performance_effect(weights, returns_data)
        entanglement_benefit = self._calculate_entanglement_benefit(weights)
        
        return {
            'portfolio_return': portfolio_return,
            'asset_contributions': asset_contributions,
            'total_selection_effect': total_selection_effect,
            'allocation_effect': allocation_effect,
            'benchmark_contribution': benchmark_contribution,
            'quantum_performance_effect': quantum_effect,
            'entanglement_benefit': entanglement_benefit,
            'total_attribution': (total_selection_effect + allocation_effect + 
                                quantum_effect + entanglement_benefit),
            'quantum_excess_return': quantum_effect + entanglement_benefit
        }
    
    def _calculate_quantum_coherence(self, weights: np.ndarray) -> float:
        """Quantum coherence hisoblash"""
        amplitudes = weights / norm(weights)
        coherence = 1 - np.sum(np.abs(amplitudes)**4)
        return coherence
    
    def _calculate_entanglement_strength(self, weights: np.ndarray) -> float:
        """Entanglement strength hisoblash"""
        if len(weights) < 2:
            return 0
        
        # Pairwise entanglement
        total_entanglement = 0
        pair_count = 0
        
        for i in range(len(weights)):
            for j in range(i+1, len(weights)):
                if weights[i] > 0.01 and weights[j] > 0.01:
                    pair_entanglement = weights[i] * weights[j]
                    total_entanglement += pair_entanglement
                    pair_count += 1
        
        return total_entanglement / pair_count if pair_count > 0 else 0
    
    def _calculate_asset_correlation(self, asset1: str, asset2: str) -> float:
        """Asset o'rtasidagi korrelatsiya hisoblash"""
        # Simplified correlation calculation
        # In practice, would use historical returns
        correlation = np.random.uniform(-0.5, 0.5)
        return correlation
    
    def _optimize_quantum_diversification(self, weights: np.ndarray, 
                                        target: float) -> np.ndarray:
        """Quantum diversifikatsiya optimizatsiyasi"""
        def objective(weights_new):
            # Diversification objective
            hhi = np.sum(weights_new**2)
            diversification = 1 - hhi
            return -(diversification - target)**2
        
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0},
            {'type': 'ineq', 'fun': lambda x: np.min(x) - 0.01}
        ]
        
        bounds = [(0.01, 0.8) for _ in range(len(weights))]
        
        result = minimize(objective, weights, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            return result.x / norm(result.x)
        else:
            return weights  # Return original if optimization fails
    
    def _calculate_quantum_var(self, weights: np.ndarray, confidence_level: float = 0.95) -> float:
        """Quantum Value at Risk hisoblash"""
        # Simplified VaR calculation
        portfolio_volatility = np.sqrt(np.sum(weights**2 * 0.15**2))
        z_score = 1.645 if confidence_level == 0.95 else 2.33  # 95% or 99%
        quantum_var = z_score * portfolio_volatility
        return quantum_var
    
    def _calculate_quantum_expected_shortfall(self, weights: np.ndarray) -> float:
        """Quantum Expected Shortfall hisoblash"""
        # Simplified Expected Shortfall
        quantum_var = self._calculate_quantum_var(weights)
        expected_shortfall = quantum_var * 1.5  # Conservative estimate
        return expected_shortfall
    
    def _apply_stress_scenario(self, weights: np.ndarray, scenario: Dict) -> np.ndarray:
        """Stress scenario qo'llash"""
        stressed_weights = weights.copy()
        
        if 'market_shock' in scenario:
            shock_factor = scenario['market_shock']
            stressed_weights *= (1 - shock_factor)
        
        if 'volatility_shock' in scenario:
            vol_factor = scenario['volatility_shock']
            stressed_weights *= np.random.uniform(1-vol_factor, 1+vol_factor, len(stressed_weights))
        
        # Renormalize
        stressed_weights = stressed_weights / np.sum(stressed_weights)
        
        return stressed_weights
    
    def _generate_risk_recommendations(self, weights: np.ndarray, current_risk: float,
                                     risk_budget: float, utilization: float) -> List[str]:
        """Risk mitigation tavsiyalari"""
        recommendations = []
        
        if utilization > 0.9:
            recommendations.append("Immediate risk reduction required")
        elif utilization > 0.8:
            recommendations.append("Consider reducing position sizes")
        
        if len([w for w in weights if w > 0.3]) > 0:
            recommendations.append("Diversify concentrated positions")
        
        # Quantum-specific recommendations
        coherence = self._calculate_quantum_coherence(weights)
        if coherence < 0.5:
            recommendations.append("Increase quantum coherence for better stability")
        
        entanglement = self._calculate_entanglement_strength(weights)
        if entanglement > 0.7:
            recommendations.append("Monitor entanglement risk")
        
        return recommendations
    
    def _calculate_quantum_performance_effect(self, weights: np.ndarray, 
                                            returns_data: np.ndarray) -> float:
        """Quantum performance effect hisoblash"""
        coherence = self._calculate_quantum_coherence(weights)
        entanglement = self._calculate_entanglement_strength(weights)
        
        # Quantum premium based on coherence and entanglement
        quantum_premium = 0.02 * coherence + 0.01 * entanglement
        return quantum_premium
    
    def _calculate_entanglement_benefit(self, weights: np.ndarray) -> float:
        """Entanglement benefit hisoblash"""
        entanglement = self._calculate_entanglement_strength(weights)
        # Benefits from correlated hedging
        entanglement_benefit = 0.005 * entanglement
        return entanglement_benefit