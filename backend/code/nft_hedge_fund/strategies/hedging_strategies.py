"""
Precious Metals Hedging Strategies
Advanced hedging strategies for Gold, Silver, Platinum, and Palladium
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import math
from scipy.optimize import minimize
import logging
from abc import ABC, abstractmethod

class MetalType(Enum):
    GOLD = "XAU"
    SILVER = "XAG"
    PLATINUM = "XPT"
    PALLADIUM = "XPD"

class HedgeStrategy(Enum):
    STATIC_DYNAMIC = "static_dynamic"
    VOLATILITY_TARGETING = "volatility_targeting"
    MOMENTUM_BASED = "momentum_based"
    MEAN_REVERSION = "mean_reversion"
    QUANTUM_SUPERPOSITION = "quantum_superposition"
    CROSS_METAL_ARBITRAGE = "cross_metal_arbitrage"

@dataclass
class MetalPriceData:
    """Metal price and market data"""
    metal: MetalType
    current_price: float
    bid: float
    ask: float
    volume: float
    open_interest: float
    implied_volatility: float
    historical_volatility: float
    timestamp: float
    
@dataclass
class HedgePosition:
    """Individual hedge position"""
    position_id: str
    metal: MetalType
    strategy: HedgeStrategy
    quantity: float
    entry_price: float
    current_price: float
    hedge_ratio: float
    pnl: float
    risk_contribution: float
    created_at: float

@dataclass
class PortfolioRisk:
    """Portfolio risk metrics"""
    total_value: float
    portfolio_volatility: float
    portfolio_var: float
    metal_correlations: Dict[Tuple[MetalType, MetalType], float]
    individual_volatilities: Dict[MetalType, float]
    risk_contributions: Dict[MetalType, float]
    concentration_risk: float

class BaseHedgingStrategy(ABC):
    """Abstract base class for hedging strategies"""
    
    def __init__(self, name: str, target_volatility: float = 0.15):
        self.name = name
        self.target_volatility = target_volatility
        self.positions: Dict[str, HedgePosition] = {}
        self.performance_history: List[float] = []
        
    @abstractmethod
    def calculate_hedge_ratio(
        self, 
        metal_data: Dict[MetalType, MetalPriceData],
        portfolio_exposure: Dict[MetalType, float]
    ) -> Dict[MetalType, float]:
        """Calculate optimal hedge ratios for metals"""
        pass
    
    @abstractmethod
    def rebalance_positions(
        self, 
        current_positions: Dict[str, HedgePosition],
        target_hedge_ratios: Dict[MetalType, float],
        market_data: Dict[MetalType, MetalPriceData]
    ) -> List[str]:
        """Rebalance positions to target hedge ratios"""
        pass

class StaticDynamicHedging(BaseHedgingStrategy):
    """
    Static-Dynamic Hedging Strategy
    Combines static hedge ratios with dynamic adjustments based on market conditions
    """
    
    def __init__(self):
        super().__init__("Static_Dynamic", 0.12)
        self.base_hedge_ratios = {
            MetalType.GOLD: 0.60,
            MetalType.SILVER: 0.70,
            MetalType.PLATINUM: 0.65,
            MetalType.PALLADIUM: 0.75
        }
        self.volatility_threshold = 0.25
        self.trend_lookback = 20
        
    def calculate_hedge_ratio(
        self, 
        metal_data: Dict[MetalType, MetalPriceData],
        portfolio_exposure: Dict[MetalType, float]
    ) -> Dict[MetalType, float]:
        """Calculate static-dynamic hedge ratios"""
        
        hedge_ratios = {}
        
        for metal, data in metal_data.items():
            # Base hedge ratio
            base_ratio = self.base_hedge_ratios[metal]
            
            # Dynamic adjustments
            vol_adjustment = self._calculate_volatility_adjustment(data)
            trend_adjustment = self._calculate_trend_adjustment(metal, data)
            liquidity_adjustment = self._calculate_liquidity_adjustment(data)
            
            # Combine adjustments
            dynamic_ratio = base_ratio * (1 + vol_adjustment + trend_adjustment + liquidity_adjustment)
            
            # Ensure ratio is within reasonable bounds
            hedge_ratios[metal] = np.clip(dynamic_ratio, 0.3, 0.95)
        
        return hedge_ratios
    
    def _calculate_volatility_adjustment(self, data: MetalPriceData) -> float:
        """Calculate volatility-based adjustment"""
        if data.historical_volatility > self.volatility_threshold:
            # Increase hedge ratio in high volatility
            return min(0.2, (data.historical_volatility - self.volatility_threshold) * 0.8)
        else:
            # Decrease hedge ratio in low volatility
            return -min(0.1, (self.volatility_threshold - data.historical_volatility) * 0.4)
    
    def _calculate_trend_adjustment(self, metal: MetalType, data: MetalPriceData) -> float:
        """Calculate trend-based adjustment"""
        # Simplified trend calculation using price momentum
        # In practice, would use more sophisticated trend indicators
        
        # Placeholder for trend calculation
        trend_signal = np.sin(np.random.random() * 2 * np.pi)  # Random trend signal
        
        if trend_signal > 0.5:
            # Uptrend - reduce hedge
            return -0.05
        elif trend_signal < -0.5:
            # Downtrend - increase hedge  
            return 0.10
        else:
            return 0.0
    
    def _calculate_liquidity_adjustment(self, data: MetalPriceData) -> float:
        """Calculate liquidity-based adjustment"""
        # Higher liquidity allows for more aggressive hedging
        normalized_volume = data.volume / 1000000  # Normalize to millions
        liquidity_factor = min(normalized_volume / 10.0, 1.0)  # Cap at 1.0
        
        return (liquidity_factor - 0.5) * 0.1  # ±5% adjustment
    
    def rebalance_positions(
        self, 
        current_positions: Dict[str, HedgePosition],
        target_hedge_ratios: Dict[MetalType, float],
        market_data: Dict[MetalType, MetalPriceData]
    ) -> List[str]:
        """Rebalance positions based on target ratios"""
        
        rebalancing_actions = []
        
        for metal, target_ratio in target_hedge_ratios.items():
            # Calculate current hedge ratio for metal
            current_exposure = sum(
                pos.quantity * pos.current_price 
                for pos in current_positions.values() 
                if pos.metal == metal
            )
            
            # Calculate target hedge position value
            metal_price = market_data[metal].current_price
            target_position_value = target_ratio * current_exposure
            target_quantity = target_position_value / metal_price
            
            # Find existing positions
            metal_positions = [
                pos for pos in current_positions.values() 
                if pos.metal == metal
            ]
            
            if not metal_positions:
                # Create new position
                action = f"CREATE_{metal.value}_{target_quantity:.2f}"
                rebalancing_actions.append(action)
            else:
                # Adjust existing position
                current_quantity = metal_positions[0].quantity
                adjustment = target_quantity - current_quantity
                
                if abs(adjustment) > 0.01:  # Minimum adjustment threshold
                    action = f"ADJUST_{metal.value}_{adjustment:.2f}"
                    rebalancing_actions.append(action)
        
        return rebalancing_actions

class VolatilityTargetingHedging(BaseHedgingStrategy):
    """
    Volatility Targeting Hedging Strategy
    Dynamically adjusts hedge ratios to target specific portfolio volatility
    """
    
    def __init__(self):
        super().__init__("Volatility_Targeting", 0.10)
        self.correlation_window = 60
        self.rebalancing_frequency = 1  # Daily rebalancing
        
    def calculate_hedge_ratio(
        self, 
        metal_data: Dict[MetalType, MetalPriceData],
        portfolio_exposure: Dict[MetalType, float]
    ) -> Dict[MetalType, float]:
        """Calculate volatility-targeted hedge ratios"""
        
        # Calculate current portfolio volatility
        current_volatility = self._calculate_portfolio_volatility(metal_data, portfolio_exposure)
        
        # Calculate hedge ratios to achieve target volatility
        hedge_ratios = {}
        
        for metal in metal_data.keys():
            # Estimate marginal contribution to portfolio volatility
            marginal_contribution = self._calculate_marginal_volatility_contribution(
                metal, metal_data, portfolio_exposure
            )
            
            # Calculate optimal hedge ratio
            if current_volatility > 0 and marginal_contribution > 0:
                vol_adjustment_factor = self.target_volatility / current_volatility
                base_ratio = 0.5  # Base hedge ratio
                
                # Adjust hedge ratio based on volatility targeting
                hedge_ratio = base_ratio * vol_adjustment_factor * (marginal_contribution / current_volatility)
                hedge_ratios[metal] = np.clip(hedge_ratio, 0.2, 0.9)
            else:
                hedge_ratios[metal] = 0.5
        
        return hedge_ratios
    
    def _calculate_portfolio_volatility(
        self, 
        metal_data: Dict[MetalType, MetalPriceData],
        portfolio_exposure: Dict[MetalType, float]
    ) -> float:
        """Calculate current portfolio volatility"""
        
        # Build variance-covariance matrix
        metals = list(metal_data.keys())
        n_metals = len(metals)
        
        if n_metals == 0:
            return 0.0
        
        # Simplified correlation matrix (in practice, would use historical data)
        correlations = np.eye(n_metals)
        for i in range(n_metals):
            for j in range(i+1, n_metals):
                # Simplified correlation based on metal type relationships
                metal1, metal2 = metals[i], metals[j]
                correlation = self._get_metal_correlation(metal1, metal2)
                correlations[i, j] = correlation
                correlations[j, i] = correlation
        
        # Volatility vector
        volatilities = np.array([metal_data[m].historical_volatility for m in metals])
        
        # Portfolio weights
        total_exposure = sum(portfolio_exposure.values())
        if total_exposure == 0:
            return 0.0
        
        weights = np.array([portfolio_exposure[m] / total_exposure for m in metals])
        
        # Portfolio variance
        variance = np.dot(weights, np.dot(np.outer(volatilities, volatilities) * correlations, weights))
        
        return math.sqrt(variance)
    
    def _calculate_marginal_volatility_contribution(
        self, 
        metal: MetalType,
        metal_data: Dict[MetalType, MetalPriceData],
        portfolio_exposure: Dict[MetalType, float]
    ) -> float:
        """Calculate marginal contribution of metal to portfolio volatility"""
        
        # Simplified marginal contribution calculation
        metal_vol = metal_data[metal].historical_volatility
        
        # Calculate correlation-weighted exposure
        correlation_factor = 0.0
        total_other_exposure = sum(
            exposure for m, exposure in portfolio_exposure.items() if m != metal
        )
        
        if total_other_exposure > 0:
            avg_correlation = 0.6  # Simplified average correlation
            correlation_factor = avg_correlation * total_other_exposure / len(portfolio_exposure)
        
        return metal_vol * (1 + correlation_factor)
    
    def _get_metal_correlation(self, metal1: MetalType, metal2: MetalType) -> float:
        """Get correlation between two metals"""
        correlation_map = {
            (MetalType.GOLD, MetalType.SILVER): 0.75,
            (MetalType.GOLD, MetalType.PLATINUM): 0.65,
            (MetalType.GOLD, MetalType.PALLADIUM): 0.55,
            (MetalType.SILVER, MetalType.PLATINUM): 0.70,
            (MetalType.SILVER, MetalType.PALLADIUM): 0.60,
            (MetalType.PLATINUM, MetalType.PALLADIUM): 0.80
        }
        
        if metal1 == metal2:
            return 1.0
        
        return correlation_map.get((metal1, metal2), 0.5)  # Default correlation
    
    def rebalance_positions(
        self, 
        current_positions: Dict[str, HedgePosition],
        target_hedge_ratios: Dict[MetalType, float],
        market_data: Dict[MetalType, MetalPriceData]
    ) -> List[str]:
        """Rebalance positions for volatility targeting"""
        
        rebalancing_actions = []
        
        for metal, target_ratio in target_hedge_ratios.items():
            # Calculate target position based on portfolio value
            total_portfolio_value = sum(
                pos.quantity * pos.current_price 
                for pos in current_positions.values()
            )
            
            metal_price = market_data[metal].current_price
            target_position_value = target_ratio * total_portfolio_value
            target_quantity = target_position_value / metal_price
            
            # Find existing position
            metal_positions = [
                pos for pos in current_positions.values() 
                if pos.metal == metal
            ]
            
            if metal_positions:
                current_quantity = metal_positions[0].quantity
                adjustment = target_quantity - current_quantity
                
                if abs(adjustment) > 0.01:  # Minimum adjustment threshold
                    action = f"REBALANCE_{metal.value}_{adjustment:.2f}"
                    rebalancing_actions.append(action)
            else:
                # Create new position
                action = f"CREATE_{metal.value}_{target_quantity:.2f}"
                rebalancing_actions.append(action)
        
        return rebalancing_actions

class QuantumSuperpositionHedging(BaseHedgingStrategy):
    """
    Quantum Superposition Hedging Strategy
    Uses quantum superposition concepts to maintain multiple hedge states simultaneously
    """
    
    def __init__(self):
        super().__init__("Quantum_Superposition", 0.08)
        self.superposition_states = 4
        self.coherence_decay = 0.95
        self.quantum_measurement_threshold = 0.7
        
    def calculate_hedge_ratio(
        self, 
        metal_data: Dict[MetalType, MetalPriceData],
        portfolio_exposure: Dict[MetalType, float]
    ) -> Dict[MetalType, float]:
        """Calculate quantum superposition hedge ratios"""
        
        hedge_ratios = {}
        
        # Generate quantum superposition states
        quantum_states = self._generate_quantum_states(metal_data)
        
        # Calculate expected hedge ratios from superposition
        for metal in metal_data.keys():
            metal_states = [state[metal] for state in quantum_states]
            
            # Quantum expectation value
            expected_hedge_ratio = np.mean(metal_states)
            
            # Apply quantum coherence
            coherence_factor = self._calculate_coherence(metal, metal_data)
            coherent_ratio = expected_hedge_ratio * coherence_factor
            
            hedge_ratios[metal] = np.clip(coherent_ratio, 0.1, 0.95)
        
        return hedge_ratios
    
    def _generate_quantum_states(
        self, 
        metal_data: Dict[MetalType, MetalPriceData]
    ) -> List[Dict[MetalType, float]]:
        """Generate quantum superposition states for hedge ratios"""
        
        states = []
        
        # Define base strategies for superposition
        strategy_mix = [
            self._conservative_strategy,
            self._aggressive_strategy,
            self._momentum_strategy,
            self._mean_reversion_strategy
        ]
        
        for strategy_func in strategy_mix:
            state = {}
            for metal, data in metal_data.items():
                # Calculate hedge ratio using specific strategy
                hedge_ratio = strategy_func(metal, data)
                state[metal] = hedge_ratio
            
            states.append(state)
        
        return states
    
    def _conservative_strategy(self, metal: MetalType, data: MetalPriceData) -> float:
        """Conservative hedging strategy"""
        base_ratio = 0.80
        vol_adjustment = min(0.1, data.historical_volatility * 0.3)
        return base_ratio + vol_adjustment
    
    def _aggressive_strategy(self, metal: MetalType, data: MetalPriceData) -> float:
        """Aggressive hedging strategy"""
        base_ratio = 0.40
        vol_adjustment = max(-0.2, -data.historical_volatility * 0.2)
        return base_ratio + vol_adjustment
    
    def _momentum_strategy(self, metal: MetalType, data: MetalPriceData) -> float:
        """Momentum-based hedging strategy"""
        # Simplified momentum calculation
        momentum_signal = np.random.normal(0, 0.1)  # Random momentum signal
        
        if momentum_signal > 0:
            return 0.50  # Reduce hedge in uptrend
        else:
            return 0.75  # Increase hedge in downtrend
    
    def _mean_reversion_strategy(self, metal: MetalType, data: MetalPriceData) -> float:
        """Mean reversion hedging strategy"""
        # Simplified mean reversion calculation
        deviation = abs(data.implied_volatility - data.historical_volatility) / data.historical_volatility
        
        if deviation > 0.2:
            return 0.60  # Moderate hedge during high deviation
        else:
            return 0.55  # Slightly lower hedge when volatility converges
    
    def _calculate_coherence(self, metal: MetalType, metal_data: Dict[MetalType, MetalPriceData]) -> float:
        """Calculate quantum coherence factor"""
        # Coherence decreases with volatility and increases with trend consistency
        data = metal_data[metal]
        
        # Volatility coherence reduction
        vol_coherence = max(0.1, 1.0 - data.historical_volatility * 2)
        
        # Market stability factor
        stability_factor = max(0.1, 1.0 - abs(data.implied_volatility - data.historical_volatility))
        
        # Combined coherence
        coherence = vol_coherence * stability_factor * self.coherence_decay
        
        return np.clip(coherence, 0.1, 1.0)
    
    def rebalance_positions(
        self, 
        current_positions: Dict[str, HedgePosition],
        target_hedge_ratios: Dict[MetalType, float],
        market_data: Dict[MetalType, MetalPriceData]
    ) -> List[str]:
        """Rebalance positions using quantum measurement"""
        
        rebalancing_actions = []
        
        # Perform quantum measurement to collapse superposition
        measured_state = self._quantum_measure_superposition(current_positions)
        
        for metal, target_ratio in target_hedge_ratios.items():
            # Compare with measured state
            measured_ratio = measured_state.get(metal, 0.5)
            
            # Calculate adjustment based on quantum difference
            quantum_difference = abs(target_ratio - measured_ratio)
            
            if quantum_difference > self.quantum_measurement_threshold:
                # Collapse to classical position
                current_metal_positions = [
                    pos for pos in current_positions.values() 
                    if pos.metal == metal
                ]
                
                if current_metal_positions:
                    # Adjust existing position
                    metal_price = market_data[metal].current_price
                    portfolio_value = sum(
                        pos.quantity * pos.current_price 
                        for pos in current_positions.values()
                    )
                    
                    target_quantity = target_ratio * portfolio_value / metal_price
                    current_quantity = current_metal_positions[0].quantity
                    adjustment = target_quantity - current_quantity
                    
                    if abs(adjustment) > 0.01:
                        action = f"QUANTUM_ADJUST_{metal.value}_{adjustment:.2f}"
                        rebalancing_actions.append(action)
        
        return rebalancing_actions
    
    def _quantum_measure_superposition(
        self, 
        current_positions: Dict[str, HedgePosition]
    ) -> Dict[MetalType, float]:
        """Perform quantum measurement on current superposition state"""
        
        measured_state = {}
        
        # Group positions by metal and calculate effective hedge ratios
        for metal in MetalType:
            metal_positions = [
                pos for pos in current_positions.values() 
                if pos.metal == metal
            ]
            
            if metal_positions:
                # Calculate effective hedge ratio from positions
                total_value = sum(pos.quantity * pos.current_price for pos in metal_positions)
                if total_value > 0:
                    # Simplified measurement - in practice would use more sophisticated quantum measurement
                    measurement_noise = np.random.normal(0, 0.05)  # 5% measurement noise
                    effective_ratio = 0.5 + measurement_noise  # Simplified hedge ratio
                    measured_state[metal] = np.clip(effective_ratio, 0.0, 1.0)
            else:
                measured_state[metal] = 0.5  # Default when no positions
        
        return measured_state

class CrossMetalArbitrageHedging(BaseHedgingStrategy):
    """
    Cross-Metal Arbitrage Hedging Strategy
    Exploits relative value opportunities between different metals
    """
    
    def __init__(self):
        super().__init__("Cross_Metal_Arbitrage", 0.12)
        self.correlation_threshold = 0.7
        self.arbitrage_threshold = 0.03  # 3% minimum arbitrage opportunity
        
    def calculate_hedge_ratio(
        self, 
        metal_data: Dict[MetalType, MetalPriceData],
        portfolio_exposure: Dict[MetalType, float]
    ) -> Dict[MetalType, float]:
        """Calculate arbitrage-based hedge ratios"""
        
        hedge_ratios = {}
        arbitrage_opportunities = self._find_arbitrage_opportunities(metal_data)
        
        # Base hedge ratio
        base_ratio = 0.60
        
        for metal in metal_data.keys():
            # Start with base ratio
            adjusted_ratio = base_ratio
            
            # Adjust based on arbitrage opportunities
            metal_arbitrage = [
                arb for arb in arbitrage_opportunities 
                if metal in [arb['metal1'], arb['metal2']]
            ]
            
            if metal_arbitrage:
                # Calculate arbitrage-weighted adjustment
                arbitrage_impact = sum(
                    abs(arb['spread']) * (1 if metal == arb.get('long_metal') else -1)
                    for arb in metal_arbitrage
                )
                
                # Apply arbitrage adjustment
                adjustment = np.clip(arbitrage_impact * 0.5, -0.2, 0.2)
                adjusted_ratio += adjustment
            
            hedge_ratios[metal] = np.clip(adjusted_ratio, 0.2, 0.9)
        
        return hedge_ratios
    
    def _find_arbitrage_opportunities(self, metal_data: Dict[MetalType, MetalPriceData]) -> List[Dict]:
        """Find cross-metal arbitrage opportunities"""
        
        opportunities = []
        metals = list(metal_data.keys())
        
        for i, metal1 in enumerate(metals):
            for j, metal2 in enumerate(metals[i+1:], i+1):
                data1 = metal_data[metal1]
                data2 = metal_data[metal2]
                
                # Calculate relative value metrics
                price_ratio = data1.current_price / data2.current_price
                vol_ratio = data1.historical_volatility / data2.historical_volatility
                
                # Check for arbitrage opportunity
                if abs(price_ratio - vol_ratio) > self.arbitrage_threshold:
                    opportunity = {
                        'metal1': metal1,
                        'metal2': metal2,
                        'spread': price_ratio - vol_ratio,
                        'long_metal': metal1 if price_ratio > vol_ratio else metal2,
                        'short_metal': metal2 if price_ratio > vol_ratio else metal1,
                        'strength': abs(price_ratio - vol_ratio)
                    }
                    opportunities.append(opportunity)
        
        # Sort by strength and return top opportunities
        opportunities.sort(key=lambda x: x['strength'], reverse=True)
        return opportunities[:3]  # Top 3 opportunities
    
    def rebalance_positions(
        self, 
        current_positions: Dict[str, HedgePosition],
        target_hedge_ratios: Dict[MetalType, float],
        market_data: Dict[MetalType, MetalPriceData]
    ) -> List[str]:
        """Rebalance positions for arbitrage opportunities"""
        
        rebalancing_actions = []
        arbitrage_opportunities = self._find_arbitrage_opportunities(market_data)
        
        # Execute arbitrage trades
        for arb in arbitrage_opportunities:
            long_metal = arb['long_metal']
            short_metal = arb['short_metal']
            
            # Calculate position sizes for arbitrage
            portfolio_value = sum(
                pos.quantity * pos.current_price 
                for pos in current_positions.values()
            )
            
            arb_size = portfolio_value * 0.1  # 10% of portfolio for arbitrage
            
            # Long position
            long_price = market_data[long_metal].current_price
            long_quantity = arb_size / long_price
            
            # Short position (simplified - in practice would use futures/derivatives)
            short_price = market_data[short_metal].current_price
            short_quantity = arb_size / short_price
            
            # Add arbitrage actions
            rebalancing_actions.append(f"ARBITRAGE_LONG_{long_metal.value}_{long_quantity:.2f}")
            rebalancing_actions.append(f"ARBITRAGE_SHORT_{short_metal.value}_{short_quantity:.2f}")
        
        # Also implement standard rebalancing
        standard_actions = super().rebalance_positions(
            current_positions, target_hedge_ratios, market_data
        )
        
        rebalancing_actions.extend(standard_actions)
        return rebalancing_actions
    
    def rebalance_positions(
        self, 
        current_positions: Dict[str, HedgePosition],
        target_hedge_ratios: Dict[MetalType, float],
        market_data: Dict[MetalType, MetalPriceData]
    ) -> List[str]:
        """Rebalance positions for arbitrage opportunities"""
        
        rebalancing_actions = []
        
        # First, implement standard rebalancing for target ratios
        for metal, target_ratio in target_hedge_ratios.items():
            # Calculate target position
            total_portfolio_value = sum(
                pos.quantity * pos.current_price 
                for pos in current_positions.values()
            )
            
            if total_portfolio_value == 0:
                continue
            
            metal_price = market_data[metal].current_price
            target_position_value = target_ratio * total_portfolio_value
            target_quantity = target_position_value / metal_price
            
            # Find existing position
            metal_positions = [
                pos for pos in current_positions.values() 
                if pos.metal == metal
            ]
            
            if metal_positions:
                current_quantity = metal_positions[0].quantity
                adjustment = target_quantity - current_quantity
                
                if abs(adjustment) > 0.01:
                    action = f"REBALANCE_{metal.value}_{adjustment:.2f}"
                    rebalancing_actions.append(action)
            else:
                # Create new position
                action = f"CREATE_{metal.value}_{target_quantity:.2f}"
                rebalancing_actions.append(action)
        
        # Add arbitrage opportunities
        arbitrage_opportunities = self._find_arbitrage_opportunities(market_data)
        
        for arb in arbitrage_opportunities:
            # Calculate arbitrage position sizes
            portfolio_value = sum(
                pos.quantity * pos.current_price 
                for pos in current_positions.values()
            )
            
            arb_allocation = portfolio_value * 0.05  # 5% of portfolio for each arbitrage
            
            long_metal = arb['long_metal']
            short_metal = arb['short_metal']
            
            long_price = market_data[long_metal].current_price
            short_price = market_data[short_metal].current_price
            
            long_quantity = arb_allocation / long_price
            short_quantity = arb_allocation / short_price
            
            rebalancing_actions.append(f"ARB_LONG_{long_metal.value}_{long_quantity:.2f}")
            rebalancing_actions.append(f"ARB_SHORT_{short_metal.value}_{short_quantity:.2f}")
        
        return rebalancing_actions

class HedgingPortfolioManager:
    """
    Portfolio Manager for Multiple Hedging Strategies
    Coordinates multiple hedging strategies and manages risk
    """
    
    def __init__(self):
        self.strategies: Dict[HedgeStrategy, BaseHedgingStrategy] = {
            HedgeStrategy.STATIC_DYNAMIC: StaticDynamicHedging(),
            HedgeStrategy.VOLATILITY_TARGETING: VolatilityTargetingHedging(),
            HedgeStrategy.QUANTUM_SUPERPOSITION: QuantumSuperpositionHedging(),
            HedgeStrategy.CROSS_METAL_ARBITRAGE: CrossMetalArbitrageHedging()
        }
        
        self.active_strategies: List[HedgeStrategy] = [
            HedgeStrategy.STATIC_DYNAMIC,
            HedgeStrategy.VOLATILITY_TARGETING
        ]
        
        self.strategy_weights: Dict[HedgeStrategy, float] = {
            HedgeStrategy.STATIC_DYNAMIC: 0.40,
            HedgeStrategy.VOLATILITY_TARGETING: 0.30,
            HedgeStrategy.QUANTUM_SUPERPOSITION: 0.20,
            HedgeStrategy.CROSS_METAL_ARBITRAGE: 0.10
        }
        
        self.portfolio_positions: Dict[str, HedgePosition] = {}
        
    def calculate_optimal_hedge_ratios(
        self, 
        metal_data: Dict[MetalType, MetalPriceData],
        portfolio_exposure: Dict[MetalType, float]
    ) -> Dict[MetalType, float]:
        """Calculate optimal hedge ratios using weighted strategy combination"""
        
        strategy_ratios = {}
        
        # Get hedge ratios from each active strategy
        for strategy_type in self.active_strategies:
            strategy = self.strategies[strategy_type]
            weight = self.strategy_weights[strategy_type]
            
            strategy_hedge_ratios = strategy.calculate_hedge_ratio(metal_data, portfolio_exposure)
            strategy_ratios[strategy_type] = strategy_hedge_ratios
        
        # Combine hedge ratios using strategy weights
        combined_ratios = {}
        for metal in metal_data.keys():
            weighted_ratio = sum(
                strategy_ratios[strategy][metal] * self.strategy_weights[strategy]
                for strategy in self.active_strategies
            )
            combined_ratios[metal] = weighted_ratio
        
        return combined_ratios
    
    def execute_rebalancing(
        self, 
        target_ratios: Dict[MetalType, float],
        market_data: Dict[MetalType, MetalPriceData]
    ) -> List[str]:
        """Execute rebalancing across all strategies"""
        
        all_actions = []
        
        for strategy_type in self.active_strategies:
            strategy = self.strategies[strategy_type]
            weight = self.strategy_weights[strategy_type]
            
            # Scale target ratios by strategy weight
            scaled_ratios = {
                metal: ratio * weight 
                for metal, ratio in target_ratios.items()
            }
            
            strategy_actions = strategy.rebalance_positions(
                self.portfolio_positions,
                scaled_ratios,
                market_data
            )
            
            all_actions.extend(strategy_actions)
        
        return all_actions
    
    def calculate_portfolio_risk(
        self, 
        market_data: Dict[MetalType, MetalPriceData]
    ) -> PortfolioRisk:
        """Calculate comprehensive portfolio risk metrics"""
        
        # Get all positions
        positions = list(self.portfolio_positions.values())
        
        if not positions:
            return PortfolioRisk(
                total_value=0.0,
                portfolio_volatility=0.0,
                portfolio_var=0.0,
                metal_correlations={},
                individual_volatilities={},
                risk_contributions={},
                concentration_risk=0.0
            )
        
        # Calculate total portfolio value
        total_value = sum(pos.quantity * pos.current_price for pos in positions)
        
        # Individual volatilities
        individual_vols = {}
        for metal in MetalType:
            metal_positions = [pos for pos in positions if pos.metal == metal]
            if metal_positions:
                metal_data = market_data[metal]
                individual_vols[metal] = metal_data.historical_volatility
            else:
                individual_vols[metal] = 0.0
        
        # Portfolio volatility (simplified)
        portfolio_vol = np.sqrt(
            sum(
                (pos.quantity * pos.current_price / total_value) ** 2 * individual_vols[pos.metal] ** 2
                for pos in positions
            )
        )
        
        # VaR calculation (95% confidence)
        portfolio_var = -portfolio_vol * 1.645 * math.sqrt(1/252)  # Daily VaR
        
        # Metal correlations
        metal_correlations = {}
        for metal1 in MetalType:
            for metal2 in MetalType:
                if metal1 != metal2:
                    correlation = self._get_metal_correlation(metal1, metal2)
                    metal_correlations[(metal1, metal2)] = correlation
        
        # Risk contributions
        risk_contributions = {}
        for metal in MetalType:
            metal_value = sum(
                pos.quantity * pos.current_price 
                for pos in positions 
                if pos.metal == metal
            )
            if total_value > 0:
                weight = metal_value / total_value
                risk_contributions[metal] = weight * individual_vols[metal]
        
        # Concentration risk (Herfindahl index)
        concentrations = [
            (pos.quantity * pos.current_price / total_value) ** 2
            for pos in positions
        ]
        concentration_risk = sum(concentrations)
        
        return PortfolioRisk(
            total_value=total_value,
            portfolio_volatility=portfolio_vol,
            portfolio_var=portfolio_var,
            metal_correlations=metal_correlations,
            individual_volatilities=individual_vols,
            risk_contributions=risk_contributions,
            concentration_risk=concentration_risk
        )
    
    def _get_metal_correlation(self, metal1: MetalType, metal2: MetalType) -> float:
        """Get correlation between two metals"""
        # Same as in VolatilityTargetingHedging
        if metal1 == metal2:
            return 1.0
        
        correlation_map = {
            (MetalType.GOLD, MetalType.SILVER): 0.75,
            (MetalType.GOLD, MetalType.PLATINUM): 0.65,
            (MetalType.GOLD, MetalType.PALLADIUM): 0.55,
            (MetalType.SILVER, MetalType.PLATINUM): 0.70,
            (MetalType.SILVER, MetalType.PALLADIUM): 0.60,
            (MetalType.PLATINUM, MetalType.PALLADIUM): 0.80
        }
        
        return correlation_map.get((metal1, metal2), 0.5)


# Example usage
if __name__ == "__main__":
    # Initialize portfolio manager
    manager = HedgingPortfolioManager()
    
    # Sample market data
    market_data = {
        MetalType.GOLD: MetalPriceData(
            metal=MetalType.GOLD,
            current_price=2000.0,
            bid=1999.5,
            ask=2000.5,
            volume=1000000,
            open_interest=500000,
            implied_volatility=0.15,
            historical_volatility=0.12,
            timestamp=time.time()
        ),
        MetalType.SILVER: MetalPriceData(
            metal=MetalType.SILVER,
            current_price=25.0,
            bid=24.95,
            ask=25.05,
            volume=2000000,
            open_interest=800000,
            implied_volatility=0.25,
            historical_volatility=0.22,
            timestamp=time.time()
        ),
        MetalType.PLATINUM: MetalPriceData(
            metal=MetalType.PLATINUM,
            current_price=1000.0,
            bid=999.0,
            ask=1001.0,
            volume=500000,
            open_interest=200000,
            implied_volatility=0.20,
            historical_volatility=0.18,
            timestamp=time.time()
        ),
        MetalType.PALLADIUM: MetalPriceData(
            metal=MetalType.PALLADIUM,
            current_price=2000.0,
            bid=1998.0,
            ask=2002.0,
            volume=300000,
            open_interest=150000,
            implied_volatility=0.35,
            historical_volatility=0.30,
            timestamp=time.time()
        )
    }
    
    # Portfolio exposure
    portfolio_exposure = {
        MetalType.GOLD: 5000000.0,   # $5M
        MetalType.SILVER: 2000000.0, # $2M
        MetalType.PLATINUM: 1500000.0, # $1.5M
        MetalType.PALLADIUM: 1500000.0  # $1.5M
    }
    
    # Calculate optimal hedge ratios
    optimal_ratios = manager.calculate_optimal_hedge_ratios(market_data, portfolio_exposure)
    
    print("Optimal Hedge Ratios:")
    for metal, ratio in optimal_ratios.items():
        print(f"{metal.value}: {ratio:.3f} ({ratio*100:.1f}%)")
    
    # Execute rebalancing
    rebalancing_actions = manager.execute_rebalancing(optimal_ratios, market_data)
    
    print("\nRebalancing Actions:")
    for action in rebalancing_actions:
        print(f"  {action}")
    
    # Calculate portfolio risk
    risk_metrics = manager.calculate_portfolio_risk(market_data)
    
    print("\nPortfolio Risk Metrics:")
    print(f"Total Value: ${risk_metrics.total_value:,.2f}")
    print(f"Portfolio Volatility: {risk_metrics.portfolio_volatility:.3f}")
    print(f"Portfolio VaR (95%): {risk_metrics.portfolio_var:.3f}")
    print(f"Concentration Risk: {risk_metrics.concentration_risk:.3f}")
    
    print("\nRisk Contributions by Metal:")
    for metal, contribution in risk_metrics.risk_contributions.items():
        print(f"{metal.value}: {contribution:.3f}")