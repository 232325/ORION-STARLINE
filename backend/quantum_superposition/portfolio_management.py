"""
Portfolio Management - Dynamic superposition weights va quantum portfolio rebalancing
Performance attribution va risk-adjusted quantum strategies
"""

import numpy as np
import cmath
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import warnings

from quantum_superposition_theory import QuantumState, QuantumSuperpositionManager
from superposition_portfolio_models import SuperpositionPortfolio, CoherentTrading
from diversification_quantum_models import QuantumDiversification, EntanglementCorrelations

@dataclass
class DynamicPortfolioManager:
    """Dynamic portfolio management with quantum superposition"""
    initial_portfolio: SuperpositionPortfolio
    rebalancing_rules: Dict[str, Any] = field(default_factory=dict)
    market_conditions: Dict[str, float] = field(default_factory=dict)
    trading_history: List[Dict] = field(default_factory=list)
    performance_history: List[Dict] = field(default_factory=list)
    
    def __post_init__(self):
        self.setup_rebalancing_rules()
        self.setup_market_conditions()
    
    def setup_rebalancing_rules(self):
        """Setup portfolio rebalancing rules"""
        self.rebalancing_rules = {
            'rebalance_threshold': 0.05,  # 5% deviation triggers rebalancing
            'max_single_position': 0.30,  # Max 30% in single asset
            'min_single_position': 0.02,  # Min 2% in each asset
            'rebalancing_frequency': 'monthly',
            'quantum_coherence_threshold': 0.6,
            'volatility_threshold': 0.25,
            'max_turnover': 0.50  # Max 50% turnover
        }
    
    def setup_market_conditions(self):
        """Initialize market conditions tracking"""
        self.market_conditions = {
            'volatility_regime': 'normal',  # low, normal, high
            'market_trend': 'sideways',     # bullish, bearish, sideways
            'quantum_coherence': 0.5,
            'correlation_regime': 'stable',
            'risk_sentiment': 0.0
        }
    
    def update_market_conditions(self, 
                               market_data: Dict[str, Any],
                               market_signals: Dict[str, float]) -> None:
        """Update market conditions based on current data"""
        # Volatility regime
        market_volatility = market_signals.get('volatility', 0.2)
        if market_volatility < 0.15:
            self.market_conditions['volatility_regime'] = 'low'
        elif market_volatility > 0.30:
            self.market_conditions['volatility_regime'] = 'high'
        else:
            self.market_conditions['volatility_regime'] = 'normal'
        
        # Market trend
        market_return = market_signals.get('market_return', 0.0)
        if market_return > 0.02:
            self.market_conditions['market_trend'] = 'bullish'
        elif market_return < -0.02:
            self.market_conditions['market_trend'] = 'bearish'
        else:
            self.market_conditions['market_trend'] = 'sideways'
        
        # Quantum coherence
        if 'quantum_coherence' in market_signals:
            self.market_conditions['quantum_coherence'] = market_signals['quantum_coherence']
        
        # Risk sentiment
        risk_indicators = market_signals.get('risk_indicators', {})
        sentiment_score = np.mean(list(risk_indicators.values())) if risk_indicators else 0.0
        self.market_conditions['risk_sentiment'] = sentiment_score
    
    def calculate_dynamic_weights(self, 
                                target_weights: Dict[str, float],
                                market_data: Dict[str, Any] = None) -> Dict[str, float]:
        """Calculate dynamic portfolio weights based on market conditions"""
        dynamic_weights = target_weights.copy()
        
        # Volatility-based adjustments
        volatility_adjustment = self.get_volatility_adjustment()
        
        # Trend-based adjustments
        trend_adjustment = self.get_trend_adjustment()
        
        # Quantum coherence adjustment
        coherence_adjustment = self.get_coherence_adjustment()
        
        # Apply adjustments
        for asset_id in dynamic_weights.keys():
            adjustment_factor = (1 + volatility_adjustment + trend_adjustment + coherence_adjustment)
            dynamic_weights[asset_id] *= adjustment_factor
        
        # Apply constraints
        dynamic_weights = self.apply_weight_constraints(dynamic_weights)
        
        # Normalize
        total_weight = sum(dynamic_weights.values())
        if total_weight > 0:
            dynamic_weights = {k: v/total_weight for k, v in dynamic_weights.items()}
        
        return dynamic_weights
    
    def get_volatility_adjustment(self) -> float:
        """Get volatility-based weight adjustment"""
        volatility_regime = self.market_conditions['volatility_regime']
        
        if volatility_regime == 'high':
            return -0.1  # Reduce risk in high volatility
        elif volatility_regime == 'low':
            return 0.05  # Increase risk in low volatility
        else:
            return 0.0   # No change in normal volatility
    
    def get_trend_adjustment(self) -> float:
        """Get trend-based weight adjustment"""
        market_trend = self.market_conditions['market_trend']
        
        if market_trend == 'bullish':
            return 0.02  # Slight increase in risk
        elif market_trend == 'bearish':
            return -0.03  # Reduce risk
        else:
            return 0.0   # No change in sideways market
    
    def get_coherence_adjustment(self) -> float:
        """Get quantum coherence-based adjustment"""
        coherence = self.market_conditions.get('quantum_coherence', 0.5)
        
        if coherence < self.rebalancing_rules['quantum_coherence_threshold']:
            return -0.02  # Reduce weights when coherence is low
        elif coherence > 0.8:
            return 0.01   # Slight increase when coherence is high
        else:
            return 0.0
    
    def apply_weight_constraints(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Apply portfolio weight constraints"""
        # Apply minimum and maximum position limits
        for asset_id in weights.keys():
            weights[asset_id] = max(
                self.rebalancing_rules['min_single_position'],
                min(self.rebalancing_rules['max_single_position'], weights[asset_id])
            )
        
        return weights
    
    def should_rebalance(self, 
                        current_weights: Dict[str, float],
                        target_weights: Dict[str, float]) -> bool:
        """Determine if portfolio should be rebalanced"""
        for asset_id in current_weights.keys():
            if asset_id in target_weights:
                deviation = abs(current_weights[asset_id] - target_weights[asset_id])
                if deviation > self.rebalancing_rules['rebalance_threshold']:
                    return True
        
        return False
    
    def calculate_rebalancing_trades(self, 
                                   current_weights: Dict[str, float],
                                   target_weights: Dict[str, float],
                                   portfolio_value: float) -> List[Dict]:
        """Calculate trades needed for rebalancing"""
        trades = []
        
        for asset_id in current_weights.keys():
            if asset_id in target_weights:
                current_value = portfolio_value * current_weights[asset_id]
                target_value = portfolio_value * target_weights[asset_id]
                trade_amount = target_value - current_value
                
                if abs(trade_amount) > portfolio_value * 0.001:  # Minimum trade size
                    trade_direction = 'BUY' if trade_amount > 0 else 'SELL'
                    
                    trades.append({
                        'asset_id': asset_id,
                        'direction': trade_direction,
                        'amount': abs(trade_amount),
                        'current_weight': current_weights[asset_id],
                        'target_weight': target_weights[asset_id],
                        'weight_change': target_weights[asset_id] - current_weights[asset_id]
                    })
        
        return trades
    
    def execute_quantum_rebalancing(self, 
                                  target_weights: Dict[str, float],
                                  execution_style: str = 'gradual') -> Dict[str, Any]:
        """Execute quantum-aware rebalancing"""
        current_weights = self.initial_portfolio.assets
        
        if not self.should_rebalance(current_weights, target_weights):
            return {
                'action': 'hold',
                'reason': 'weights_within_threshold',
                'trades': []
            }
        
        if execution_style == 'immediate':
            # Immediate rebalancing
            trades = self.calculate_rebalancing_trades(current_weights, target_weights, 1000000)
            
            # Update portfolio weights
            self.initial_portfolio.assets = target_weights.copy()
            
            # Record rebalancing
            rebalancing_record = {
                'timestamp': datetime.now(),
                'action': 'rebalance',
                'style': 'immediate',
                'trades': trades,
                'target_weights': target_weights
            }
            
            self.trading_history.append(rebalancing_record)
            
            return {
                'action': 'rebalance',
                'trades': trades,
                'execution_style': execution_style
            }
        
        elif execution_style == 'gradual':
            # Gradual rebalancing over multiple steps
            gradual_trades = []
            current_state = current_weights.copy()
            
            steps = 5  # Rebalance over 5 steps
            step_size = 1.0 / steps
            
            for step in range(steps):
                # Calculate intermediate target
                intermediate_weights = {}
                for asset_id in current_weights.keys():
                    if asset_id in target_weights:
                        weight_diff = target_weights[asset_id] - current_state[asset_id]
                        intermediate_weights[asset_id] = current_state[asset_id] + weight_diff * step_size
                
                # Calculate trades for this step
                step_trades = self.calculate_rebalancing_trades(current_state, intermediate_weights, 1000000)
                gradual_trades.extend(step_trades)
                
                # Update current state
                current_state = intermediate_weights.copy()
            
            # Final update
            self.initial_portfolio.assets = target_weights.copy()
            
            rebalancing_record = {
                'timestamp': datetime.now(),
                'action': 'rebalance',
                'style': 'gradual',
                'trades': gradual_trades,
                'steps': steps,
                'target_weights': target_weights
            }
            
            self.trading_history.append(rebalancing_record)
            
            return {
                'action': 'rebalance',
                'trades': gradual_trades,
                'execution_style': execution_style,
                'steps': steps
            }
    
    def monitor_portfolio_performance(self, 
                                    portfolio_returns: Dict[str, float],
                                    benchmark_returns: Dict[str, float] = None) -> Dict[str, Any]:
        """Monitor and analyze portfolio performance"""
        # Calculate performance metrics
        performance_metrics = {}
        
        for asset_id, asset_return in portfolio_returns.items():
            performance_metrics[asset_id] = {
                'return': asset_return,
                'quantum_enhanced': self.calculate_quantum_enhancement(asset_id, asset_return)
            }
        
        # Portfolio-level metrics
        portfolio_weights = np.array(list(self.initial_portfolio.assets.values()))
        portfolio_returns_array = np.array(list(portfolio_returns.values()))
        
        portfolio_return = np.dot(portfolio_weights, portfolio_returns_array)
        
        # Quantum portfolio metrics
        quantum_metrics = self.calculate_quantum_portfolio_metrics()
        
        performance_record = {
            'timestamp': datetime.now(),
            'portfolio_return': portfolio_return,
            'asset_performance': performance_metrics,
            'quantum_metrics': quantum_metrics,
            'market_conditions': self.market_conditions.copy()
        }
        
        self.performance_history.append(performance_record)
        
        return performance_record
    
    def calculate_quantum_enhancement(self, asset_id: str, return_value: float) -> float:
        """Calculate quantum enhancement to returns"""
        if asset_id in self.initial_portfolio.quantum_states:
            quantum_state = self.initial_portfolio.quantum_states[asset_id]
            
            # Quantum enhancement based on coherence and amplitude
            coherence_factor = abs(quantum_state.amplitude) ** 2
            phase_enhancement = np.cos(quantum_state.phase) * 0.01  # Small phase effect
            
            quantum_enhancement = coherence_factor * phase_enhancement
            return quantum_enhancement
        
        return 0.0
    
    def calculate_quantum_portfolio_metrics(self) -> Dict[str, float]:
        """Calculate quantum-specific portfolio metrics"""
        metrics = {}
        
        # Portfolio quantum coherence
        total_coherence = 0
        for state in self.initial_portfolio.quantum_states.values():
            coherence = abs(state.amplitude) ** 2
            total_coherence += coherence
        
        metrics['portfolio_coherence'] = total_coherence / len(self.initial_portfolio.quantum_states)
        
        # Quantum entanglement
        entanglement_sum = 0
        states_list = list(self.initial_portfolio.quantum_states.values())
        for i, state1 in enumerate(states_list):
            for j, state2 in enumerate(states_list):
                if i != j:
                    entanglement = abs(state1.amplitude * np.conj(state2.amplitude))
                    entanglement_sum += entanglement
        
        metrics['average_entanglement'] = entanglement_sum / (len(states_list) * (len(states_list) - 1))
        
        # Quantum phase alignment
        phases = [state.phase for state in self.initial_portfolio.quantum_states.values()]
        phase_variance = np.var(phases)
        metrics['phase_coherence'] = 1.0 / (1.0 + phase_variance)
        
        return metrics

@dataclass
class QuantumRebalancing:
    """Advanced quantum rebalancing strategies"""
    portfolio_manager: DynamicPortfolioManager
    quantum_strategies: List[str] = field(default_factory=lambda: [
        'coherence_maximization',
        'entanglement_balancing', 
        'quantum_hedging',
        'phase_optimization'
    ])
    strategy_weights: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        self.initialize_strategy_weights()
    
    def initialize_strategy_weights(self):
        """Initialize weights for different quantum strategies"""
        equal_weight = 1.0 / len(self.quantum_strategies)
        self.strategy_weights = {strategy: equal_weight for strategy in self.quantum_strategies}
    
    def coherence_maximization_rebalancing(self, target_weights: Dict[str, float]) -> Dict[str, float]:
        """Rebalance to maximize quantum coherence"""
        current_weights = self.portfolio_manager.initial_portfolio.assets
        
        # Calculate coherence for different weight combinations
        coherence_scores = {}
        
        # Generate candidate weight sets
        num_candidates = 10
        for i in range(num_candidates):
            # Small variations around target weights
            variation = np.random.normal(0, 0.02, len(target_weights))
            candidate_weights = np.array(list(target_weights.values())) + variation
            
            # Ensure non-negative and normalize
            candidate_weights = np.maximum(candidate_weights, 0.01)
            candidate_weights = candidate_weights / np.sum(candidate_weights)
            
            # Calculate coherence
            coherence = self.calculate_coherence_score(candidate_weights)
            coherence_scores[tuple(candidate_weights)] = coherence
        
        # Select weights with highest coherence
        best_weights = max(coherence_scores.keys(), key=lambda w: coherence_scores[w])
        
        return {list(target_weights.keys())[i]: best_weights[i] for i in range(len(target_weights))}
    
    def entanglement_balancing_rebalancing(self, target_weights: Dict[str, float]) -> Dict[str, float]:
        """Rebalance to balance quantum entanglement"""
        current_weights = self.portfolio_manager.initial_portfolio.assets
        
        # Calculate current entanglement matrix
        entanglement_matrix = self.portfolio_manager.initial_portfolio.get_quantum_correlation_matrix()
        
        # Calculate entanglement balance
        target_entanglement = 0.3  # Target entanglement level
        current_entanglement = np.mean(np.abs(entanglement_matrix - np.eye(len(entanglement_matrix))))
        
        # Adjust weights to achieve target entanglement
        adjustment_factor = (target_entanglement - current_entanglement) / target_entanglement
        adjustment_factor = max(-0.1, min(0.1, adjustment_factor))  # Limit adjustment
        
        # Apply adjustment
        balanced_weights = {}
        for i, (asset_id, weight) in enumerate(target_weights.items()):
            # Adjust based on entanglement contribution
            entanglement_contribution = np.mean(np.abs(entanglement_matrix[i, :]))
            adjusted_weight = weight * (1 + adjustment_factor * entanglement_contribution)
            balanced_weights[asset_id] = adjusted_weight
        
        # Normalize
        total = sum(balanced_weights.values())
        if total > 0:
            balanced_weights = {k: v/total for k, v in balanced_weights.items()}
        
        return balanced_weights
    
    def quantum_hedging_rebalancing(self, target_weights: Dict[str, float]) -> Dict[str, float]:
        """Rebalance with quantum hedging considerations"""
        current_weights = self.portfolio_manager.initial_portfolio.assets
        
        # Calculate current risk metrics
        portfolio_vol = self.calculate_portfolio_volatility(current_weights)
        
        # Target volatility
        target_vol = 0.15
        
        # Adjust weights for volatility target
        if portfolio_vol > target_vol:
            # Need to reduce risk
            vol_adjustment = (target_vol / portfolio_vol) ** 0.5  # Square root for smoothness
        else:
            vol_adjustment = 1.0
        
        # Apply quantum-specific adjustments
        quantum_adjustments = {}
        for asset_id, weight in target_weights.items():
            # Quantum hedge factor
            if asset_id in self.portfolio_manager.initial_portfolio.quantum_states:
                quantum_state = self.portfolio_manager.initial_portfolio.quantum_states[asset_id]
                hedge_factor = abs(quantum_state.amplitude) ** 2 * np.cos(quantum_state.phase)
            else:
                hedge_factor = 1.0
            
            adjusted_weight = weight * vol_adjustment * (1 + hedge_factor * 0.1)
            quantum_adjustments[asset_id] = adjusted_weight
        
        # Normalize
        total = sum(quantum_adjustments.values())
        if total > 0:
            quantum_adjustments = {k: v/total for k, v in quantum_adjustments.items()}
        
        return quantum_adjustments
    
    def phase_optimization_rebalancing(self, target_weights: Dict[str, float]) -> Dict[str, float]:
        """Rebalance to optimize quantum phases"""
        current_weights = self.portfolio_manager.initial_portfolio.assets
        
        # Current phase configuration
        current_phases = {}
        for asset_id, state in self.portfolio_manager.initial_portfolio.quantum_states.items():
            current_phases[asset_id] = state.phase
        
        # Target phase alignment
        target_phase_alignment = np.pi / 4  # 45 degrees
        
        # Calculate phase optimization
        optimized_weights = {}
        for asset_id, weight in target_weights.items():
            current_phase = current_phases.get(asset_id, 0)
            
            # Phase optimization factor
            phase_deviation = abs(current_phase - target_phase_alignment)
            phase_optimization = np.exp(-phase_deviation / (np.pi / 2))  # Exponential decay
            
            optimized_weight = weight * (0.8 + 0.4 * phase_optimization)
            optimized_weights[asset_id] = optimized_weight
        
        # Normalize
        total = sum(optimized_weights.values())
        if total > 0:
            optimized_weights = {k: v/total for k, v in optimized_weights.items()}
        
        return optimized_weights
    
    def calculate_coherence_score(self, weights: np.ndarray) -> float:
        """Calculate quantum coherence score for given weights"""
        # Simplified coherence calculation
        # High coherence when weights are balanced and amplitudes align
        
        # Weight balance score
        weight_variance = np.var(weights)
        balance_score = 1.0 / (1.0 + weight_variance * 10)
        
        # Amplitude coherence score (assuming current amplitudes)
        current_amplitudes = []
        for weight in weights:
            amplitude = np.sqrt(max(0, weight))
            current_amplitudes.append(amplitude)
        
        amplitude_coherence = 1.0 - np.var(current_amplitudes)
        
        # Combined score
        coherence_score = 0.6 * balance_score + 0.4 * amplitude_coherence
        return max(0.0, coherence_score)
    
    def calculate_portfolio_volatility(self, weights: Dict[str, float]) -> float:
        """Calculate portfolio volatility"""
        weights_array = np.array(list(weights.values()))
        
        # Simplified covariance matrix
        covariance_matrix = np.eye(len(weights)) * 0.02
        covariance_matrix[0, 1] = covariance_matrix[1, 0] = 0.01
        covariance_matrix[2, 3] = covariance_matrix[3, 2] = 0.015
        
        portfolio_variance = np.dot(weights_array, np.dot(covariance_matrix, weights_array))
        return np.sqrt(portfolio_variance)
    
    def execute_multi_strategy_rebalancing(self, target_weights: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """Execute rebalancing using multiple quantum strategies"""
        strategy_results = {}
        
        for strategy in self.quantum_strategies:
            if strategy == 'coherence_maximization':
                result = self.coherence_maximization_rebalancing(target_weights)
            elif strategy == 'entanglement_balancing':
                result = self.entanglement_balancing_rebalancing(target_weights)
            elif strategy == 'quantum_hedging':
                result = self.quantum_hedging_rebalancing(target_weights)
            elif strategy == 'phase_optimization':
                result = self.phase_optimization_rebalancing(target_weights)
            else:
                result = target_weights.copy()
            
            strategy_results[strategy] = result
        
        return strategy_results
    
    def ensemble_rebalancing(self, 
                           target_weights: Dict[str, float],
                           strategy_weights: Dict[str, float] = None) -> Dict[str, float]:
        """Create ensemble rebalancing using weighted combination of strategies"""
        if strategy_weights is None:
            strategy_weights = self.strategy_weights
        
        # Normalize strategy weights
        total_strategy_weight = sum(strategy_weights.values())
        if total_strategy_weight > 0:
            strategy_weights = {k: v/total_strategy_weight for k, v in strategy_weights.items()}
        
        # Get individual strategy results
        strategy_results = self.execute_multi_strategy_rebalancing(target_weights)
        
        # Combine results
        ensemble_weights = {}
        for asset_id in target_weights.keys():
            total_weight = 0
            for strategy, result in strategy_results.items():
                strategy_contribution = strategy_weights.get(strategy, 0)
                weight_contribution = result.get(asset_id, 0)
                total_weight += weight_contribution * strategy_contribution
            
            ensemble_weights[asset_id] = total_weight
        
        # Normalize ensemble weights
        total_ensemble = sum(ensemble_weights.values())
        if total_ensemble > 0:
            ensemble_weights = {k: v/total_ensemble for k, v in ensemble_weights.items()}
        
        return ensemble_weights

@dataclass
class PerformanceAttribution:
    """Performance attribution for quantum portfolios"""
    portfolio_manager: DynamicPortfolioManager
    benchmark_assets: Dict[str, float] = field(default_factory=dict)
    attribution_periods: List[Tuple[datetime, datetime]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.benchmark_assets:
            # Default equal-weight benchmark
            num_assets = len(self.portfolio_manager.initial_portfolio.assets)
            equal_weight = 1.0 / num_assets
            self.benchmark_assets = {
                asset_id: equal_weight for asset_id in self.portfolio_manager.initial_portfolio.assets.keys()
            }
    
    def calculate_basic_attribution(self, 
                                  portfolio_returns: Dict[str, float],
                                  benchmark_returns: Dict[str, float]) -> Dict[str, Any]:
        """Calculate basic performance attribution"""
        # Portfolio weights and returns
        portfolio_weights = self.portfolio_manager.initial_portfolio.assets
        portfolio_weights_array = np.array(list(portfolio_weights.values()))
        portfolio_returns_array = np.array([portfolio_returns.get(asset_id, 0) 
                                          for asset_id in portfolio_weights.keys()])
        
        # Benchmark weights and returns
        benchmark_weights_array = np.array(list(self.benchmark_assets.values()))
        benchmark_returns_array = np.array([benchmark_returns.get(asset_id, 0) 
                                          for asset_id in self.benchmark_assets.keys()])
        
        # Calculate attribution components
        allocation_effect = self.calculate_allocation_effect(
            portfolio_weights_array, benchmark_weights_array, benchmark_returns_array
        )
        
        selection_effect = self.calculate_selection_effect(
            portfolio_weights_array, benchmark_weights_array, 
            portfolio_returns_array, benchmark_returns_array
        )
        
        interaction_effect = self.calculate_interaction_effect(
            portfolio_weights_array, benchmark_weights_array,
            portfolio_returns_array, benchmark_returns_array
        )
        
        # Total return difference
        portfolio_return = np.dot(portfolio_weights_array, portfolio_returns_array)
        benchmark_return = np.dot(benchmark_weights_array, benchmark_returns_array)
        total_difference = portfolio_return - benchmark_return
        
        attribution = {
            'period': datetime.now(),
            'portfolio_return': portfolio_return,
            'benchmark_return': benchmark_return,
            'total_difference': total_difference,
            'allocation_effect': allocation_effect,
            'selection_effect': selection_effect,
            'interaction_effect': interaction_effect,
            'asset_contributions': self.calculate_asset_contributions(
                portfolio_weights_array, portfolio_returns_array
            )
        }
        
        return attribution
    
    def calculate_allocation_effect(self, 
                                  pw: np.ndarray, 
                                  bw: np.ndarray, 
                                  br: np.ndarray) -> float:
        """Calculate allocation effect"""
        weight_diff = pw - bw
        return np.sum(weight_diff * br)
    
    def calculate_selection_effect(self, 
                                 pw: np.ndarray, 
                                 bw: np.ndarray, 
                                 pr: np.ndarray, 
                                 br: np.ndarray) -> float:
        """Calculate selection effect"""
        return np.sum(bw * (pr - br))
    
    def calculate_interaction_effect(self, 
                                   pw: np.ndarray, 
                                   bw: np.ndarray, 
                                   pr: np.ndarray, 
                                   br: np.ndarray) -> float:
        """Calculate interaction effect"""
        weight_diff = pw - bw
        return np.sum(weight_diff * (pr - br))
    
    def calculate_asset_contributions(self, weights: np.ndarray, returns: np.ndarray) -> Dict[str, float]:
        """Calculate individual asset contributions"""
        contributions = {}
        asset_ids = list(self.portfolio_manager.initial_portfolio.assets.keys())
        
        for i, asset_id in enumerate(asset_ids):
            contributions[asset_id] = weights[i] * returns[i]
        
        return contributions
    
    def calculate_quantum_attribution(self, 
                                    portfolio_returns: Dict[str, float],
                                    quantum_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Calculate quantum-specific performance attribution"""
        quantum_attribution = {}
        
        # Quantum coherence contribution
        coherence = quantum_metrics.get('portfolio_coherence', 0.5)
        total_portfolio_return = np.mean(list(portfolio_returns.values()))
        
        quantum_attribution['coherence_contribution'] = coherence * total_portfolio_return * 0.1
        
        # Quantum entanglement contribution
        entanglement = quantum_metrics.get('average_entanglement', 0.3)
        quantum_attribution['entanglement_contribution'] = entanglement * total_portfolio_return * 0.05
        
        # Quantum phase contribution
        phase_coherence = quantum_metrics.get('phase_coherence', 0.5)
        quantum_attribution['phase_contribution'] = phase_coherence * total_portfolio_return * 0.02
        
        # Total quantum effect
        quantum_attribution['total_quantum_effect'] = sum([
            quantum_attribution['coherence_contribution'],
            quantum_attribution['entanglement_contribution'],
            quantum_attribution['phase_contribution']
        ])
        
        return quantum_attribution
    
    def calculate_risk_attribution(self, 
                                 portfolio_volatility: float,
                                 benchmark_volatility: float) -> Dict[str, float]:
        """Calculate risk attribution"""
        risk_attribution = {
            'portfolio_volatility': portfolio_volatility,
            'benchmark_volatility': benchmark_volatility,
            'volatility_difference': portfolio_volatility - benchmark_volatility,
            'volatility_contribution': (portfolio_volatility - benchmark_volatility) / benchmark_volatility
        }
        
        return risk_attribution
    
    def comprehensive_performance_report(self, 
                                       portfolio_returns: Dict[str, float],
                                       benchmark_returns: Dict[str, float],
                                       quantum_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        # Basic attribution
        basic_attribution = self.calculate_basic_attribution(portfolio_returns, benchmark_returns)
        
        # Quantum attribution
        quantum_attribution = self.calculate_quantum_attribution(portfolio_returns, quantum_metrics)
        
        # Risk attribution
        portfolio_vol = np.sqrt(np.mean([r**2 for r in portfolio_returns.values()]))
        benchmark_vol = np.sqrt(np.mean([r**2 for r in benchmark_returns.values()]))
        risk_attribution = self.calculate_risk_attribution(portfolio_vol, benchmark_vol)
        
        # Performance summary
        performance_summary = {
            'total_return': basic_attribution['portfolio_return'],
            'benchmark_return': basic_attribution['benchmark_return'],
            'excess_return': basic_attribution['total_difference'],
            'quantum_contribution': quantum_attribution['total_quantum_effect'],
            'risk_contribution': risk_attribution['volatility_contribution']
        }
        
        report = {
            'timestamp': datetime.now(),
            'performance_summary': performance_summary,
            'basic_attribution': basic_attribution,
            'quantum_attribution': quantum_attribution,
            'risk_attribution': risk_attribution,
            'market_conditions': self.portfolio_manager.market_conditions
        }
        
        return report

def demonstrate_portfolio_management():
    """Demonstrate quantum portfolio management"""
    print("=== Quantum Portfolio Management Demo ===")
    
    # Create sample portfolio
    assets = {
        'AAPL': 0.25,
        'GOOGL': 0.20,
        'MSFT': 0.15,
        'TSLA': 0.25,
        'AMZN': 0.15
    }
    
    portfolio = SuperpositionPortfolio(assets)
    manager = DynamicPortfolioManager(portfolio)
    
    # Test dynamic weight calculation
    target_weights = {
        'AAPL': 0.30,
        'GOOGL': 0.15,
        'MSFT': 0.20,
        'TSLA': 0.20,
        'AMZN': 0.15
    }
    
    # Update market conditions
    market_signals = {
        'volatility': 0.25,
        'market_return': 0.01,
        'quantum_coherence': 0.7,
        'risk_indicators': {'VIX': 0.6, 'put_call_ratio': 0.4}
    }
    
    manager.update_market_conditions({}, market_signals)
    dynamic_weights = manager.calculate_dynamic_weights(target_weights)
    
    print(f"Target weights: {target_weights}")
    print(f"Dynamic weights: {dynamic_weights}")
    print(f"Market conditions: {manager.market_conditions}")
    
    # Test rebalancing
    rebalancer = QuantumRebalancing(manager)
    ensemble_weights = rebalancer.ensemble_rebalancing(target_weights)
    print(f"Ensemble weights: {ensemble_weights}")
    
    # Test performance attribution
    portfolio_returns = {
        'AAPL': 0.015,
        'GOOGL': 0.008,
        'MSFT': 0.012,
        'TSLA': 0.020,
        'AMZN': 0.010
    }
    
    benchmark_returns = {
        'AAPL': 0.010,
        'GOOGL': 0.012,
        'MSFT': 0.008,
        'TSLA': 0.018,
        'AMZN': 0.009
    }
    
    quantum_metrics = {
        'portfolio_coherence': 0.65,
        'average_entanglement': 0.35,
        'phase_coherence': 0.75
    }
    
    performance_attributor = PerformanceAttribution(manager)
    performance_report = performance_attributor.comprehensive_performance_report(
        portfolio_returns, benchmark_returns, quantum_metrics
    )
    
    print("\nPerformance Report:")
    print(f"Total Return: {performance_report['performance_summary']['total_return']:.4f}")
    print(f"Excess Return: {performance_report['performance_summary']['excess_return']:.4f}")
    print(f"Quantum Contribution: {performance_report['performance_summary']['quantum_contribution']:.4f}")
    
    return manager, rebalancer, performance_attributor

if __name__ == "__main__":
    demonstrate_portfolio_management()