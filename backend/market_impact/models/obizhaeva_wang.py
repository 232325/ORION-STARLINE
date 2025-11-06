"""
Obizhaeva-Wang Price Impact Model

Bu model order flow va market microstructure ga asoslangan price impact modeli.

Model assumptions:
- Market maker optimal trading strategy ishlatadi  
- Inventory management muhim
- Price impact order flow volatility ga bog'liq

Anna Obizhaeva va Tongling Wang tomonidan ishlab chiqilgan.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ObizhaevaWangParameters:
    """Obizhaeva-Wang model parametrlari"""
    alpha: float  # Price impact koeffitsiyenti
    beta: float  # Risk aversion koeffitsiyenti  
    gamma: float  # Inventory holding cost
    delta: float  # Market making intensity
    sigma: float  # Volatility parameter


class ObizhaevaWangModel:
    """
    Obizhaeva-Wang Model - Order flow va inventory ta'sirini hisoblaydi
    """
    
    def __init__(self, parameters: ObizhaevaWangParameters):
        """
        Initialize model
        
        Args:
            parameters: Model parametrlari
        """
        self.alpha = parameters.alpha
        self.beta = parameters.beta
        self.gamma = parameters.gamma
        self.delta = parameters.delta
        self.sigma = parameters.sigma
        
    def calculate_inventory_impact(self, order_size: float, 
                                 current_inventory: float,
                                 market_volatility: float) -> float:
        """
        Inventory-based price impact hisoblash
        
        Args:
            order_size: Order hajmi
            current_inventory: Current inventory
            market_volatility: Market volatility
            
        Returns:
            Inventory impact
        """
        # Inventory penalty component
        inventory_penalty = self.gamma * current_inventory * order_size
        
        # Volatility adjustment
        volatility_adjustment = self.sigma * np.sqrt(abs(current_inventory)) * market_volatility
        
        # Combined impact
        total_impact = inventory_penalty + volatility_adjustment
        
        return total_impact
        
    def calculate_market_making_impact(self, bid_size: float, ask_size: float,
                                     order_flow_intensity: float) -> Dict[str, float]:
        """
        Market making impact hisoblash
        
        Args:
            bid_size: Bid size
            ask_size: Ask size  
            order_flow_intensity: Order flow intensity
            
        Returns:
            Market making impacts for bid va ask
        """
        # Order flow impact
        flow_impact = self.delta * order_flow_intensity
        
        # Imbalance impact
        imbalance = (bid_size - ask_size) / (bid_size + ask_size + 1e-6)
        
        # Bid impact (buy orders push price up)
        bid_impact = flow_impact + self.alpha * imbalance
        
        # Ask impact (sell orders push price down)
        ask_impact = flow_impact - self.alpha * imbalance
        
        return {
            'bid_impact': bid_impact,
            'ask_impact': ask_impact,
            'spread_impact': bid_impact + ask_impact
        }
        
    def calculate_optimal_spread(self, inventory_level: float,
                               volatility: float) -> float:
        """
        Optimal bid-ask spread hisoblash
        
        Args:
            inventory_level: Current inventory level
            volatility: Market volatility
            
        Returns:
            Optimal spread
        """
        # Base spread from volatility
        base_spread = self.sigma * np.sqrt(volatility) * np.sqrt(0.01)  # 10-minute horizon
        
        # Inventory adjustment
        inventory_adjustment = abs(inventory_level) * self.gamma
        
        # Total optimal spread
        optimal_spread = base_spread + inventory_adjustment
        
        return optimal_spread
        
    def calculate_price_impact_from_order_flow(self, 
                                             order_flow_history: np.ndarray,
                                             time_horizon: int = 100) -> np.ndarray:
        """
        Order flow dan price impact hisoblash
        
        Args:
            order_flow_history: Historical order flow data
            time_horizon: Time horizon
            
        Returns:
            Price impacts sequence
        """
        impacts = np.zeros(len(order_flow_history))
        
        for i in range(1, len(order_flow_history)):
            # Current order flow
            current_flow = order_flow_history[i]
            previous_flow = order_flow_history[i-1]
            
            # Flow change impact
            flow_change = current_flow - previous_flow
            
            # Calculate impact with memory effect
            memory_effect = np.sum(self.alpha * flow_change * 
                                 np.exp(-0.01 * np.arange(i)))
            
            impacts[i] = memory_effect
            
        return impacts
        
    def calculate_inventory_risk_premium(self, inventory_position: float,
                                       volatility: float,
                                       risk_aversion: float = None) -> float:
        """
        Inventory risk premium hisoblash
        
        Args:
            inventory_position: Current inventory position
            volatility: Market volatility
            risk_aversion: Risk aversion parameter (default: beta)
            
        Returns:
            Risk premium
        """
        if risk_aversion is None:
            risk_aversion = self.beta
            
        # Portfolio variance
        portfolio_var = inventory_position ** 2 * volatility ** 2
        
        # Risk premium
        risk_premium = risk_aversion * portfolio_var
        
        return risk_premium
        
    def calculate_optimal_inventory_target(self, expected_flow: float,
                                         volatility: float,
                                         time_horizon: float) -> float:
        """
        Optimal inventory target hisoblash
        
        Args:
            expected_flow: Expected order flow
            volatility: Market volatility
            time_horizon: Time horizon
            
        Returns:
            Optimal inventory target
        """
        # Mean-variance optimization for inventory
        numerator = expected_flow * time_horizon
        denominator = 2 * self.beta * volatility ** 2 * time_horizon
        
        if denominator == 0:
            return 0.0
            
        optimal_target = numerator / denominator
        
        return optimal_target
        
    def simulate_market_maker_behavior(self, 
                                     inventory_initial: float,
                                     price_initial: float,
                                     order_flow_sequence: np.ndarray,
                                     num_periods: int = 100) -> Dict[str, np.ndarray]:
        """
        Market maker behavior simulation
        
        Args:
            inventory_initial: Initial inventory
            price_initial: Initial price
            order_flow_sequence: Order flow sequence
            num_periods: Number of periods to simulate
            
        Returns:
            Simulation results
        """
        # Initialize arrays
        inventory = np.zeros(num_periods)
        prices = np.zeros(num_periods)
        spreads = np.zeros(num_periods)
        
        # Set initial values
        inventory[0] = inventory_initial
        prices[0] = price_initial
        
        for t in range(1, num_periods):
            if t < len(order_flow_sequence):
                # Current period metrics
                current_flow = order_flow_sequence[t]
                current_inventory = inventory[t-1]
                
                # Calculate spread
                volatility = self.sigma * np.sqrt(0.01)  # 10-minute volatility
                spread = self.calculate_optimal_spread(current_inventory, volatility)
                spreads[t-1] = spread
                
                # Update inventory based on order flow
                inventory_impact = self.calculate_inventory_impact(
                    current_flow, current_inventory, volatility)
                
                # Simple inventory update
                inventory[t] = inventory[t-1] + current_flow
                
                # Price impact
                price_impact = self.alpha * current_flow + inventory_impact
                prices[t] = prices[t-1] + price_impact
                
        return {
            'inventory': inventory,
            'prices': prices,
            'spreads': spreads,
            'order_flow': order_flow_sequence[:num_periods]
        }
        
    def calculate_market_impact_coefficients(self, historical_data: pd.DataFrame) -> Dict[str, float]:
        """
        Historical data dan model coefficients hisoblash
        
        Args:
            historical_data: Historical price va order flow data
            
        Returns:
            Estimated coefficients
        """
        # Required columns: price_changes, order_flow, inventory_level
        if len(historical_data) < 50:
            return {'error': 'Insufficient data for coefficient estimation'}
            
        # Calculate price changes
        price_changes = historical_data['price'].pct_change().dropna()
        order_flow = historical_data['order_flow'].iloc[1:].values
        inventory_level = historical_data['inventory_level'].iloc[1:].values
        
        # Simple regression: price_change = alpha * order_flow + beta * inventory_level
        from scipy import stats
        
        # Prepare data
        X = np.column_stack([order_flow, inventory_level])
        
        # Regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            X, price_changes[:len(X)])
            
        return {
            'alpha_estimate': slope,
            'beta_estimate': intercept,
            'r_squared': r_value ** 2,
            'p_value': p_value
        }
        
    def get_model_statistics(self) -> Dict[str, float]:
        """
        Model statistikalari
        
        Returns:
            Dictionary with model statistics
        """
        return {
            'alpha': self.alpha,
            'beta': self.beta,
            'gamma': self.gamma,
            'delta': self.delta,
            'sigma': self.sigma,
            'impact_sensitivity': self.alpha,
            'inventory_sensitivity': self.gamma
        }
        
    def estimate_price_impact_time_decay(self, initial_impact: float,
                                       decay_rate: float = 0.1) -> np.ndarray:
        """
        Price impact time decay hisoblash
        
        Args:
            initial_impact: Initial price impact
            decay_rate: Decay rate
            
        Returns:
            Time decay of price impact
        """
        time_points = np.arange(0, 24)  # 24 periods
        decay = initial_impact * np.exp(-decay_rate * time_points)
        
        return decay