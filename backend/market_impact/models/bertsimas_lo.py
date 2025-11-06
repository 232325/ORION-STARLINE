"""
Bertsimas-Lo Price Impact Model

Bu model adaptive market making va information flow ta'sirini hisobga oladi.

Model assumptions:
- Market maker learns from order flow
- Information asymmetric flow
- Adaptive pricing strategy
- Queue position importance

Dimitri Bertsimas va Andrew Lo tomonidan ishlab chiqilgan.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from scipy import stats
from scipy.optimize import minimize


@dataclass
class BertsimasLoParameters:
    """Bertsimas-Lo model parametrlari"""
    kappa: float  # Information arrival rate
    phi: float  # Learning speed parameter
    lambda_noise: float  # Noise trader intensity
    theta_market: float  # Market making intensity
    gamma_adapt: float  # Adaptation speed
    sigma_info: float  # Information volatility


class BertsimasLoModel:
    """
    Bertsimas-Lo Model - Adaptive market making va information flow
    """
    
    def __init__(self, parameters: BertsimasLoParameters):
        """
        Initialize model
        
        Args:
            parameters: Model parametrlari
        """
        self.kappa = parameters.kappa
        self.phi = parameters.phi
        self.lambda_noise = parameters.lambda_noise
        self.theta_market = parameters.theta_market
        self.gamma_adapt = parameters.gamma_adapt
        self.sigma_info = parameters.sigma_info
        
        # Initialize information state
        self.information_state = 0.0
        self.learning_rate = 1.0
        
    def calculate_information_impact(self, order_flow: float,
                                   market_conditions: Dict[str, float]) -> float:
        """
        Information-based price impact hisoblash
        
        Args:
            order_flow: Current order flow
            market_conditions: Market conditions dict
            
        Returns:
            Information impact
        """
        # Information signal from order flow
        signal_strength = np.tanh(order_flow / self.lambda_noise)
        
        # Update information state with learning
        new_information = self.phi * signal_strength + (1 - self.phi) * self.information_state
        information_change = new_information - self.information_state
        self.information_state = new_information
        
        # Adjust learning rate based on market conditions
        volatility = market_conditions.get('volatility', 0.01)
        self.learning_rate = max(0.1, min(1.0, self.gamma_adapt / (volatility + 1e-6)))
        
        # Calculate impact
        information_impact = self.kappa * information_change * self.learning_rate
        
        return information_impact
        
    def calculate_adaptive_spread(self, current_inventory: float,
                                recent_order_flow: np.ndarray,
                                time_decay: float = 0.1) -> Dict[str, float]:
        """
        Adaptive spread calculation
        
        Args:
            current_inventory: Current inventory position
            recent_order_flow: Recent order flow history
            time_decay: Time decay parameter
            
        Returns:
            Adaptive spread components
        """
        # Calculate adaptive components
        n = len(recent_order_flow)
        
        # Order flow momentum
        momentum = np.sum(recent_order_flow * np.exp(-time_decay * np.arange(n)))
        
        # Information signal
        info_signal = np.tanh(momentum / self.lambda_noise)
        
        # Inventory penalty
        inventory_penalty = abs(current_inventory) * self.theta_market
        
        # Volatility adjustment
        volatility_impact = np.std(recent_order_flow) * self.sigma_info
        
        # Base spread
        base_spread = max(0.01, inventory_penalty + volatility_impact)
        
        # Adaptive adjustment
        adaptive_adjustment = info_signal * 0.1 * base_spread
        
        # Total spread components
        bid_spread = base_spread - adaptive_adjustment
        ask_spread = base_spread + adaptive_adjustment
        
        return {
            'bid_spread': max(0.001, bid_spread),
            'ask_spread': max(0.001, ask_spread),
            'total_spread': max(0.001, bid_spread + ask_spread),
            'inventory_penalty': inventory_penalty,
            'volatility_impact': volatility_impact,
            'adaptive_adjustment': adaptive_adjustment,
            'information_signal': info_signal
        }
        
    def calculate_queue_position_impact(self, queue_position: int,
                                      queue_ahead: int,
                                      fill_probability: float) -> float:
        """
        Queue position impact hisoblash
        
        Args:
            queue_position: Our position in queue
            queue_ahead: Orders ahead of us
            fill_probability: Fill probability
            
        Returns:
            Queue position impact
        """
        # Higher position = lower priority = higher impact
        priority_factor = (queue_position + 1) / (queue_ahead + queue_position + 1)
        
        # Fill probability adjustment
        fill_adjustment = 1.0 - fill_probability
        
        # Time decay factor (longer wait = higher impact)
        time_decay = 1.0 + 0.1 * queue_position
        
        # Total impact
        queue_impact = priority_factor * fill_adjustment * time_decay
        
        return queue_impact
        
    def update_market_conditions(self, price_changes: np.ndarray,
                              volume_changes: np.ndarray,
                              order_flow_changes: np.ndarray) -> Dict[str, float]:
        """
        Market conditions update
        
        Args:
            price_changes: Recent price changes
            volume_changes: Recent volume changes
            order_flow_changes: Recent order flow changes
            
        Returns:
            Updated market conditions
        """
        # Calculate various metrics
        price_volatility = np.std(price_changes)
        volume_trend = np.mean(volume_changes)
        flow_volatility = np.std(order_flow_changes)
        
        # Market regime detection (simplified)
        if price_volatility > np.percentile(price_changes, 90):
            regime = 'high_volatility'
        elif price_volatility < np.percentile(price_changes, 10):
            regime = 'low_volatility'
        else:
            regime = 'normal'
            
        return {
            'price_volatility': price_volatility,
            'volume_trend': volume_trend,
            'flow_volatility': flow_volatility,
            'regime': regime,
            'market_stress': max(0, price_volatility - 0.02),  # Stress indicator
            'liquidity_quality': 1.0 / (flow_volatility + 1e-6)  # Inverse of flow vol
        }
        
    def adaptive_pricing_strategy(self, fair_value: float,
                                current_spread: float,
                                market_conditions: Dict[str, float],
                                risk_tolerance: float = 0.5) -> Dict[str, float]:
        """
        Adaptive pricing strategy
        
        Args:
            fair_value: Estimated fair value
            current_spread: Current spread
            market_conditions: Current market conditions
            risk_tolerance: Risk tolerance (0-1)
            
        Returns:
            Adaptive pricing recommendation
        """
        # Market stress adjustment
        stress = market_conditions['market_stress']
        stress_adjustment = stress * risk_tolerance
        
        # Liquidity quality adjustment
        liquidity = market_conditions['liquidity_quality']
        liquidity_adjustment = (1.0 - risk_tolerance) / liquidity
        
        # Information advantage
        info_advantage = abs(self.information_state) * self.gamma_adapt
        
        # Calculate bid and ask prices
        base_bid = fair_value - current_spread / 2
        base_ask = fair_value + current_spread / 2
        
        # Adjust for conditions
        adaptive_bid = base_bid - stress_adjustment - liquidity_adjustment + info_advantage
        adaptive_ask = base_ask + stress_adjustment + liquidity_adjustment - info_advantage
        
        # Ensure positive spread
        if adaptive_ask - adaptive_bid < 0.001:
            spread_adjustment = 0.001 - (adaptive_ask - adaptive_bid)
            adaptive_ask += spread_adjustment / 2
            adaptive_bid -= spread_adjustment / 2
            
        return {
            'adaptive_bid': adaptive_bid,
            'adaptive_ask': adaptive_ask,
            'fair_value': fair_value,
            'strategy_adjustments': {
                'stress': stress_adjustment,
                'liquidity': liquidity_adjustment,
                'information': info_advantage
            }
        }
        
    def simulate_market_making_session(self, initial_inventory: float,
                                    initial_fair_value: float,
                                    order_flow_sequence: np.ndarray,
                                    price_sequence: np.ndarray,
                                    duration_minutes: int = 60) -> Dict[str, np.ndarray]:
        """
        Market making session simulation
        
        Args:
            initial_inventory: Initial inventory
            initial_fair_value: Initial fair value
            order_flow_sequence: Order flow sequence
            price_sequence: Actual price sequence
            duration_minutes: Session duration
            
        Returns:
            Simulation results
        """
        # Initialize arrays
        num_periods = min(len(order_flow_sequence), duration_minutes)
        
        inventory = np.zeros(num_periods)
        fair_values = np.zeros(num_periods)
        spreads = np.zeros(num_periods)
        pnl = np.zeros(num_periods)
        information_states = np.zeros(num_periods)
        
        # Initial conditions
        inventory[0] = initial_inventory
        fair_values[0] = initial_fair_value
        information_states[0] = self.information_state
        
        current_pnl = 0.0
        
        for t in range(1, num_periods):
            if t < len(price_sequence):
                # Market update
                current_price = price_sequence[t]
                order_flow = order_flow_sequence[t]
                
                # Update fair value based on actual price and information
                price_diff = current_price - fair_values[t-1]
                information_update = self.phi * np.tanh(price_diff / 0.01) + (1 - self.phi) * self.information_state
                self.information_state = information_update
                
                fair_values[t] = current_price + 0.5 * self.information_state
                
                # Market conditions (simplified)
                market_conditions = {
                    'volatility': np.std(price_sequence[max(0, t-10):t]) if t > 10 else 0.01
                }
                
                # Calculate adaptive spread
                recent_flow = order_flow_sequence[max(0, t-5):t] if t > 5 else order_flow_sequence[:t]
                spread_info = self.calculate_adaptive_spread(inventory[t-1], recent_flow)
                
                # Quote prices
                bid_price = fair_values[t] - spread_info['bid_spread'] / 2
                ask_price = fair_values[t] + spread_info['ask_spread'] / 2
                spreads[t] = spread_info['total_spread']
                
                # Inventory management (simplified)
                # Adjust inventory based on position
                target_inventory = -order_flow * 0.1  # Counter-position
                inventory_adjustment = (target_inventory - inventory[t-1]) * 0.1
                inventory[t] = inventory[t-1] + inventory_adjustment
                
                # PnL calculation (simplified)
                if t > 0:
                    inventory_change = inventory[t] - inventory[t-1]
                    if inventory_change < 0:  # Sold shares
                        trade_pnl = inventory_change * (bid_price - fair_values[t-1])
                    else:  # Bought shares
                        trade_pnl = inventory_change * (fair_values[t-1] - ask_price)
                    
                    current_pnl += trade_pnl
                    pnl[t] = current_pnl
                    
                information_states[t] = self.information_state
                
        return {
            'inventory': inventory,
            'fair_values': fair_values,
            'spreads': spreads,
            'pnl': pnl,
            'information_states': information_states,
            'total_pnl': current_pnl,
            'inventory_risk': np.var(inventory)
        }
        
    def calculate_information_advantage(self, signal_strength: float,
                                      market_noise: float) -> Dict[str, float]:
        """
        Information advantage calculation
        
        Args:
            signal_strength: Signal strength
            market_noise: Market noise level
            
        Returns:
            Information advantage metrics
        """
        # Signal to noise ratio
        snr = signal_strength / (market_noise + 1e-6)
        
        # Information value
        info_value = self.kappa * np.log(1 + snr)
        
        # Learning effectiveness
        learning_effectiveness = 1.0 - np.exp(-self.phi * signal_strength)
        
        # Advantage decay
        advantage_decay = np.exp(-0.1 * market_noise)
        
        return {
            'signal_to_noise_ratio': snr,
            'information_value': info_value,
            'learning_effectiveness': learning_effectiveness,
            'advantage_decay': advantage_decay,
            'net_advantage': info_value * learning_effectiveness * advantage_decay
        }
        
    def estimate_model_parameters(self, historical_data: pd.DataFrame) -> Dict[str, float]:
        """
        Historical data dan model parameters ni estimate qilish
        
        Args:
            historical_data: Historical trading data
            
        Returns:
            Estimated parameters
        """
        if len(historical_data) < 100:
            return {'error': 'Insufficient data for parameter estimation'}
            
        # Required columns: order_flow, price_changes, spread_data
        order_flow = historical_data['order_flow'].values
        price_changes = historical_data['price_changes'].values
        spreads = historical_data.get('spreads', [0.01] * len(order_flow))
        
        # Estimate kappa (information impact)
        kappa_estimate = np.corrcoef(order_flow, price_changes)[0, 1] * np.std(price_changes) / (np.std(order_flow) + 1e-6)
        
        # Estimate phi (learning speed)
        price_autocorr = np.corrcoef(price_changes[:-1], price_changes[1:])[0, 1]
        phi_estimate = 1.0 - abs(price_autocorr)
        
        # Estimate theta_market (market making intensity)
        spread_inventory_corr = np.corrcoef(spreads, np.abs(order_flow))[0, 1] if len(spreads) == len(order_flow) else 0
        theta_estimate = spread_inventory_corr * 0.1
        
        # Estimate lambda_noise
        lambda_estimate = np.std(order_flow)
        
        return {
            'kappa_estimate': abs(kappa_estimate),
            'phi_estimate': max(0.01, min(0.99, phi_estimate)),
            'theta_market_estimate': abs(theta_estimate),
            'lambda_noise_estimate': max(0.1, lambda_estimate),
            'model_fit_r_squared': np.corrcoef(order_flow, price_changes)[0, 1] ** 2 if not np.isnan(np.corrcoef(order_flow, price_changes)[0, 1]) else 0
        }
        
    def calculate_adaptive_metrics(self, market_data: np.ndarray) -> Dict[str, float]:
        """
        Adaptive model metrics calculation
        
        Args:
            market_data: Market data for analysis
            
        Returns:
            Adaptive metrics
        """
        # Calculate adaptive metrics
        volatility = np.std(market_data)
        mean_reversion = np.mean(np.diff(market_data))
        trend_strength = np.abs(mean_reversion) / (volatility + 1e-6)
        
        # Market efficiency
        efficiency_ratio = 1.0 / (1.0 + trend_strength)
        
        # Adaptation effectiveness
        adaptation_effectiveness = self.gamma_adapt * (1.0 - efficiency_ratio)
        
        return {
            'market_volatility': volatility,
            'trend_strength': trend_strength,
            'efficiency_ratio': efficiency_ratio,
            'adaptation_effectiveness': adaptation_effectiveness,
            'information_advantage': abs(self.information_state) * self.kappa
        }
        
    def get_model_statistics(self) -> Dict[str, float]:
        """
        Model statistikalari
        
        Returns:
            Dictionary with model statistics
        """
        return {
            'kappa': self.kappa,
            'phi': self.phi,
            'lambda_noise': self.lambda_noise,
            'theta_market': self.theta_market,
            'gamma_adapt': self.gamma_adapt,
            'sigma_info': self.sigma_info,
            'current_information_state': self.information_state,
            'current_learning_rate': self.learning_rate
        }
        
    def compare_market_making_strategies(self, initial_inventory: float,
                                       order_flow: np.ndarray,
                                       price_data: np.ndarray) -> Dict[str, Dict]:
        """
        Different market making strategies ni taqqoslash
        
        Args:
            initial_inventory: Initial inventory
            order_flow: Order flow data
            price_data: Price data
            
        Returns:
            Strategy comparison results
        """
        strategies = {}
        
        # Adaptive Bertsimas-Lo
        adaptive_result = self.simulate_market_making_session(
            initial_inventory, price_data[0], order_flow, price_data)
        strategies['Adaptive Bertsimas-Lo'] = adaptive_result
        
        # Fixed spread strategy (no adaptation)
        fixed_model = BertsimasLoModel(BertsimasLoParameters(
            kappa=self.kappa, phi=0.0, lambda_noise=self.lambda_noise,
            theta_market=self.theta_market, gamma_adapt=0.0, sigma_info=self.sigma_info
        ))
        fixed_result = fixed_model.simulate_market_making_session(
            initial_inventory, price_data[0], order_flow, price_data)
        strategies['Fixed Spread'] = fixed_result
        
        # Information-based only (no learning)
        info_only_model = BertsimasLoModel(BertsimasLoParameters(
            kappa=self.kappa, phi=0.0, lambda_noise=self.lambda_noise,
            theta_market=self.theta_market, gamma_adapt=self.gamma_adapt, sigma_info=self.sigma_info
        ))
        info_only_result = info_only_model.simulate_market_making_session(
            initial_inventory, price_data[0], order_flow, price_data)
        strategies['Information Only'] = info_only_result
        
        return strategies