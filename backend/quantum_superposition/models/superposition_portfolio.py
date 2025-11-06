"""
Superposition Portfolio Model
============================

Quantum superposition asosida portfolio optimization model.
"""

import numpy as np
import cmath
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
from scipy.optimize import minimize
from scipy.linalg import norm, eigh
import matplotlib.pyplot as plt

try:
    from ..core.quantum_state import QuantumPortfolioState, QuantumState
    from ..core.superposition import QuantumSuperposition, SuperpositionConfig
    from ..core.entanglement import QuantumEntanglement
except ImportError:
    # Fallback for standalone execution
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from core.quantum_state import QuantumPortfolioState, QuantumState
    from core.superposition import QuantumSuperposition, SuperpositionConfig
    from core.entanglement import QuantumEntanglement


@dataclass
class SuperpositionPortfolioConfig:
    """Superposition portfolio konfiguratsiya parametrlari"""
    n_superposition_states: int = 4  # Superposition state'lar soni
    superposition_coefficient: float = 1/np.sqrt(4)  # Default coefficient
    measurement_frequency: int = 10  # O'lchov chastotasi
    coherence_preservation: bool = True  # Coherence saqlash
    interference_enhancement: float = 0.1  # Interference kuchaytirish
    quantum_advantage_threshold: float = 0.05  # Quantum afzallik threshold


class SuperpositionPortfolio:
    """
    Superposition Portfolio Model
    
    Bir nechta quantum portfolio state'larining superposition'i.
    """
    
    def __init__(self, config: SuperpositionPortfolioConfig = None):
        self.config = config or SuperpositionPortfolioConfig()
        self.superposition_manager = QuantumSuperposition()
        self.component_portfolios = []
        self.superposition_weights = None
        self.combined_superposition = None
        
        self.performance_history = []
        self.measurement_history = []
        self.interference_patterns = {}
        
    def add_component_portfolio(self, portfolio: QuantumPortfolioState,
                              weight: float = None) -> None:
        """
        Component portfolio qo'shish
        
        Args:
            portfolio: Qo'shiladigan portfolio
            weight: Portfolio vazni (agar None bo'lsa, equal weights)
        """
        if len(self.component_portfolios) >= self.config.n_superposition_states:
            raise ValueError(f"Maksimal {self.config.n_superposition_states} portfolio qo'shish mumkin")
        
        self.component_portfolios.append(portfolio)
        
        # Update superposition weights
        n_components = len(self.component_portfolios)
        if weight is None:
            self.superposition_weights = np.ones(n_components) / n_components
        else:
            if self.superposition_weights is None:
                self.superposition_weights = np.ones(n_components)
            self.superposition_weights = np.append(self.superposition_weights, weight)
            
        # Renormalize
        self.superposition_weights = self.superposition_weights / np.sum(self.superposition_weights)
    
    def create_superposition(self) -> QuantumState:
        """
        Component portfolio'lardan superposition yaratish
        
        Returns:
            Combined quantum superposition state
        """
        if len(self.component_portfolios) == 0:
            raise ValueError("Kamida bitta portfolio qo'shish kerak")
        
        # Superposition yaratish
        self.combined_superposition = self.superposition_manager.create_portfolio_superposition(
            self.component_portfolios, self.superposition_weights
        )
        
        return self.combined_superposition
    
    def optimize_superposition_weights(self, target_return: float,
                                     risk_tolerance: float,
                                     optimization_method: str = 'quantum') -> Dict:
        """
        Superposition weight'larini optimallashtirish
        
        Args:
            target_return: Maqsad daromad
            risk_tolerance: Risk tolerance
            optimization_method: Optimization usuli
        
        Returns:
            Optimization natijasi
        """
        if len(self.component_portfolios) == 0:
            raise ValueError("Portfolio component'lari mavjud emas")
        
        if optimization_method == 'quantum':
            # Quantum optimization
            optimal_weights = self.superposition_manager.optimize_superposition_weights(
                self.component_portfolios, target_return, risk_tolerance
            )
        else:
            # Classical optimization
            def classical_objective(weights):
                weights = weights / norm(weights)
                # Simplified classical objective
                total_return = 0
                total_risk = 0
                
                for i, portfolio in enumerate(self.component_portfolios):
                    # Expected return (simplified)
                    portfolio_return = np.sum(np.abs(portfolio.state.amplitudes)**2 * 0.1)
                    total_return += weights[i] * portfolio_return
                    
                    # Risk calculation
                    portfolio_risk = np.sqrt(np.sum(np.abs(portfolio.state.amplitudes)**2 * 0.15**2))
                    total_risk += weights[i]**2 * portfolio_risk**2
                
                return -(total_return - risk_tolerance * total_risk)
            
            # Classical optimization
            bounds = [(0.01, 1.0) for _ in range(len(self.component_portfolios))]
            constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0}]
            
            result = minimize(classical_objective, self.superposition_weights, 
                            method='SLSQP', bounds=bounds, constraints=constraints)
            
            if result.success:
                optimal_weights = result.x / norm(result.x)
            else:
                optimal_weights = self.superposition_weights
        
        # Update weights
        self.superposition_weights = optimal_weights
        self.combined_superposition = self.create_superposition()
        
        # Performance evaluation
        performance_metrics = self._evaluate_superposition_performance()
        
        return {
            'optimal_weights': optimal_weights,
            'superposition_state': self.combined_superposition,
            'performance_metrics': performance_metrics,
            'quantum_advantage': performance_metrics.get('quantum_advantage', 0),
            'optimization_method': optimization_method
        }
    
    def quantum_interference_analysis(self) -> Dict:
        """
        Quantum interference analizi
        
        Returns:
            Interference pattern va analysis
        """
        if len(self.component_portfolios) < 2:
            return {'error': 'Kamida 2 portfolio kerak interference uchun'}
        
        interference_results = {}
        
        # Pairwise interference
        for i in range(len(self.component_portfolios)):
            for j in range(i+1, len(self.component_portfolios)):
                port1 = self.component_portfolios[i]
                port2 = self.component_portfolios[j]
                
                interference = self.superposition_manager.quantum_interference_effects(
                    port1.state, port2.state
                )
                
                pair_name = f"{port1.assets[0]}_{port2.assets[0]}"
                interference_results[pair_name] = interference
        
        # Multi-component interference
        if len(self.component_portfolios) > 2:
            multi_interference = self._analyze_multi_interference()
            interference_results['multi_component'] = multi_interference
        
        # Interference enhancement
        total_visibility = np.mean([result['visibility'] 
                                  for result in interference_results.values() 
                                  if isinstance(result, dict) and 'visibility' in result])
        
        self.interference_patterns = interference_results
        
        return {
            'interference_results': interference_results,
            'average_visibility': total_visibility,
            'interference_strength': total_visibility,
            'quantum_coherence': total_visibility > self.config.interference_enhancement
        }
    
    def measure_superposition_collapse(self, measurement_type: str = 'strong') -> Dict:
        """
        Superposition collapse o'lchovi
        
        Args:
            measurement_type: O'lchov turi
        
        Returns:
            Collapse natijasi
        """
        if self.combined_superposition is None:
            self.create_superposition()
        
        measurement_config = MeasurementConfig(measurement_type=measurement_type)
        measurement_engine = QuantumMeasurement(measurement_config)
        
        # Perform measurement
        if measurement_type == 'weak':
            result = measurement_engine.weak_measurement(self.combined_superposition)
            collapse_result = {
                'measurement_type': 'weak',
                'estimated_expectation': result['estimated_expectation'],
                'post_measurement_state': result['measured_state'],
                'disturbance': result['disturbance']
            }
        else:
            result = measurement_engine.strong_measurement(self.combined_superposition)
            collapse_result = {
                'measurement_type': 'strong',
                'collapsed_result': result['result'],
                'probability': result['probability'],
                'collapsed_state': result['collapsed_state']
            }
        
        # Record measurement
        self.measurement_history.append({
            'measurement': collapse_result,
            'timestamp': len(self.measurement_history),
            'superposition_state': self.combined_superposition.get_state_vector().copy()
        })
        
        return collapse_result
    
    def coherence_preservation_analysis(self) -> Dict:
        """
        Quantum coherence preservation analizi
        
        Returns:
            Coherence metrics
        """
        if self.combined_superposition is None:
            self.create_superposition()
        
        # Coherence time analysis
        coherence_analysis = self.superposition_manager.coherence_time_analysis(
            self.combined_superposition
        )
        
        # Component coherence
        component_coherence = []
        for i, portfolio in enumerate(self.component_portfolios):
            component_coherence.append({
                'portfolio_id': i,
                'assets': portfolio.assets,
                'coherence_strength': np.sum(np.abs(portfolio.state.amplitudes)**4),
                'quantum_entropy': -np.sum(np.abs(portfolio.state.amplitudes)**2 * 
                                          np.log(np.abs(portfolio.state.amplitudes)**2 + 1e-10))
            })
        
        # Overall superposition coherence
        overall_coherence = self._calculate_overall_coherence()
        
        # Coherence preservation recommendations
        recommendations = self._generate_coherence_recommendations(component_coherence, overall_coherence)
        
        return {
            'coherence_analysis': coherence_analysis,
            'component_coherence': component_coherence,
            'overall_coherence': overall_coherence,
            'preservation_quality': overall_coherence / len(self.component_portfolios),
            'coherence_half_life': coherence_analysis['half_life'],
            'recommendations': recommendations
        }
    
    def quantum_advantage_assessment(self, benchmark_performance: float = None) -> Dict:
        """
        Quantum afzallik baholash
        
        Args:
            benchmark_performance: Benchmark performance
        
        Returns:
            Quantum advantage analysis
        """
        # Calculate superposition performance
        if self.combined_superposition is None:
            self.create_superposition()
        
        performance_metrics = self._evaluate_superposition_performance()
        
        # Calculate classical equivalent performance
        classical_performance = self._calculate_classical_equivalent_performance()
        
        # Quantum advantage calculation
        quantum_advantage = (performance_metrics['expected_return'] - 
                           classical_performance['expected_return'])
        
        risk_adjusted_advantage = (performance_metrics['sharpe_ratio'] - 
                                 classical_performance['sharpe_ratio'])
        
        # Coherence benefit
        coherence_benefit = self._calculate_coherence_benefit()
        
        # Interference benefit
        interference_benefit = self._calculate_interference_benefit()
        
        # Overall quantum advantage
        total_quantum_advantage = quantum_advantage + coherence_benefit + interference_benefit
        
        is_quantum_advantageous = (total_quantum_advantage > 
                                 self.config.quantum_advantage_threshold)
        
        # Benchmark comparison
        benchmark_advantage = 0
        if benchmark_performance is not None:
            benchmark_advantage = performance_metrics['expected_return'] - benchmark_performance
        
        return {
            'quantum_advantage': quantum_advantage,
            'risk_adjusted_advantage': risk_adjusted_advantage,
            'coherence_benefit': coherence_benefit,
            'interference_benefit': interference_benefit,
            'total_quantum_advantage': total_quantum_advantage,
            'is_advantageous': is_quantum_advantageous,
            'quantum_efficiency': performance_metrics['quantum_efficiency'],
            'performance_metrics': performance_metrics,
            'classical_performance': classical_performance,
            'benchmark_advantage': benchmark_advantage,
            'advantage_threshold': self.config.quantum_advantage_threshold
        }
    
    def adaptive_superposition(self, market_conditions: Dict) -> Dict:
        """
        Adaptiv superposition management
        
        Args:
            market_conditions: Bozor shartlari
        
        Returns:
            Adaptive strategy
        """
        # Analyze market conditions
        volatility = market_conditions.get('volatility', 0.15)
        market_trend = market_conditions.get('trend', 'neutral')
        correlation_environment = market_conditions.get('correlation', 0.3)
        
        # Adaptive adjustments
        if volatility > 0.25:
            # High volatility - increase coherence preservation
            self.config.coherence_preservation = True
            adjustment_factor = 0.8  # Reduce superposition complexity
        elif volatility < 0.1:
            # Low volatility - can handle more complexity
            self.config.coherence_preservation = False
            adjustment_factor = 1.2  # Increase superposition complexity
        else:
            adjustment_factor = 1.0
        
        # Market trend adjustments
        if market_trend == 'bullish':
            # Positive trend - weight towards growth portfolios
            trend_adjustment = 1.1
        elif market_trend == 'bearish':
            # Negative trend - weight towards defensive portfolios
            trend_adjustment = 0.9
        else:
            trend_adjustment = 1.0
        
        # Adjust superposition weights based on conditions
        adjusted_weights = self.superposition_weights * adjustment_factor * trend_adjustment
        adjusted_weights = adjusted_weights / np.sum(adjusted_weights)
        
        # Update portfolio
        self.superposition_weights = adjusted_weights
        self.combined_superposition = self.create_superposition()
        
        # Performance impact
        original_performance = self._evaluate_superposition_performance()
        
        return {
            'market_conditions': market_conditions,
            'adjustments': {
                'coherence_preservation': self.config.coherence_preservation,
                'adjustment_factor': adjustment_factor,
                'trend_adjustment': trend_adjustment
            },
            'adjusted_weights': adjusted_weights,
            'performance_impact': 'Calculation completed',
            'adaptive_strategy': 'executed'
        }
    
    def _evaluate_superposition_performance(self) -> Dict:
        """Superposition performance baholash"""
        if self.combined_superposition is None:
            self.create_superposition()
        
        # Expected return (simplified)
        expected_return = np.sum(np.abs(self.combined_superposition.amplitudes)**2 * 0.1)
        
        # Quantum risk
        quantum_variance = np.sum(np.abs(self.combined_superposition.amplitudes)**4 * 0.15**2)
        quantum_risk = np.sqrt(quantum_variance)
        
        # Sharpe ratio
        sharpe_ratio = expected_return / quantum_risk if quantum_risk > 0 else 0
        
        # Quantum efficiency
        quantum_efficiency = 1 - np.sum(np.abs(self.superposition_weights)**4)
        
        # Coherence
        coherence = 1 - np.sum(np.abs(self.combined_superposition.amplitudes)**4)
        
        return {
            'expected_return': expected_return,
            'quantum_risk': quantum_risk,
            'sharpe_ratio': sharpe_ratio,
            'quantum_efficiency': quantum_efficiency,
            'coherence': coherence,
            'entropy': -np.sum(np.abs(self.combined_superposition.amplitudes)**2 * 
                              np.log(np.abs(self.combined_superposition.amplitudes)**2 + 1e-10))
        }
    
    def _analyze_multi_interference(self) -> Dict:
        """Multi-component interference analizi"""
        if len(self.component_portfolios) < 3:
            return {}
        
        # Multi-phase interference analysis
        phases = np.linspace(0, 2*np.pi, 50)
        interference_patterns = []
        
        for phase in phases:
            # Apply phase shifts to all components except first
            combined_amplitude = self.component_portfolios[0].state.amplitudes.copy()
            
            for i in range(1, len(self.component_portfolios)):
                phase_shifted = np.exp(1j * phase * i) * self.component_portfolios[i].state.amplitudes
                combined_amplitude = np.concatenate([combined_amplitude, phase_shifted])
            
            # Normalize
            combined_amplitude = combined_amplitude / norm(combined_amplitude)
            
            # Calculate probability
            probability = np.sum(np.abs(combined_amplitude)**2)
            interference_patterns.append(probability)
        
        # Multi-interference metrics
        pattern_visibility = (np.max(interference_patterns) - np.min(interference_patterns)) / \
                           (np.max(interference_patterns) + np.min(interference_patterns))
        
        return {
            'phases': phases,
            'interference_patterns': interference_patterns,
            'visibility': pattern_visibility,
            'fringe_contrast': np.max(interference_patterns) - np.min(interference_patterns),
            'coherence_length': len([p for p in interference_patterns if p > np.mean(interference_patterns)])
        }
    
    def _calculate_overall_coherence(self) -> float:
        """Umumiy coherence hisoblash"""
        if self.combined_superposition is None:
            self.create_superposition()
        
        # Coherence based on off-diagonal elements
        coherence = 1 - np.sum(np.abs(self.combined_superposition.amplitudes)**4)
        return coherence
    
    def _generate_coherence_recommendations(self, component_coherence: List[Dict], 
                                          overall_coherence: float) -> List[str]:
        """Coherence tavsiyalar yaratish"""
        recommendations = []
        
        if overall_coherence < 0.5:
            recommendations.append("Increase coherence preservation")
            recommendations.append("Reduce measurement frequency")
        
        weak_components = [c for c in component_coherence if c['coherence_strength'] < 0.5]
        if weak_components:
            recommendations.append(f"Improve coherence in {len(weak_components)} weak components")
        
        if len(component_coherence) > self.config.n_superposition_states // 2:
            recommendations.append("Consider reducing superposition complexity")
        
        return recommendations
    
    def _calculate_classical_equivalent_performance(self) -> Dict:
        """Classical ekvivalent performance hisoblash"""
        # Equal-weight classical portfolio
        n_components = len(self.component_portfolios)
        classical_weights = np.ones(n_components) / n_components
        
        # Classical performance
        classical_return = 0
        classical_risk = 0
        
        for i, portfolio in enumerate(self.component_portfolios):
            weight = classical_weights[i]
            # Simplified return calculation
            portfolio_return = np.sum(np.abs(portfolio.state.amplitudes)**2 * 0.1)
            portfolio_risk = np.sqrt(np.sum(np.abs(portfolio.state.amplitudes)**2 * 0.15**2))
            
            classical_return += weight * portfolio_return
            classical_risk += weight**2 * portfolio_risk**2
        
        classical_risk = np.sqrt(classical_risk)
        classical_sharpe = classical_return / classical_risk if classical_risk > 0 else 0
        
        return {
            'expected_return': classical_return,
            'risk': classical_risk,
            'sharpe_ratio': classical_sharpe
        }
    
    def _calculate_coherence_benefit(self) -> float:
        """Coherence benefit hisoblash"""
        coherence = self._calculate_overall_coherence()
        # Quantum coherence provides stability benefit
        coherence_benefit = 0.02 * coherence
        return coherence_benefit
    
    def _calculate_interference_benefit(self) -> float:
        """Interference benefit hisoblash"""
        if not self.interference_patterns:
            self.quantum_interference_analysis()
        
        # Average interference visibility
        visibilities = []
        for result in self.interference_patterns.values():
            if isinstance(result, dict) and 'visibility' in result:
                visibilities.append(result['visibility'])
        
        avg_visibility = np.mean(visibilities) if visibilities else 0
        interference_benefit = 0.015 * avg_visibility
        return interference_benefit