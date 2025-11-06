"""
Kyle's Lambda Price Impact Model

Bu model quyidagi formula bo'yicha ishlaydi:
price_impact = lambda * trade_size / sqrt(market_liquidity)

Model assumptions:
- Informed trader raqobatli (competitive market)
- Noise trader random trading qiladi
- Market maker risk-averse

Kelvin Kyle tomonidan ishlab chiqilgan.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class KyleModelParameters:
    """Kyle model parametrlari"""
    lambda_param: float  # Price impact koeffitsiyenti
    sigma_v: float  # Asset return volatility
    sigma_u: float  # Noise trader flow volatility
    theta: float  # Market maker risk aversion


class KyleLambdaModel:
    """
    Kyle's Lambda Model - Informed trading va noise trader ta'sirini hisoblaydi
    """
    
    def __init__(self, parameters: KyleModelParameters):
        """
        Initialize model
        
        Args:
            parameters: Model parametrlari
        """
        self.lambda_param = parameters.lambda_param
        self.sigma_v = parameters.sigma_v
        self.sigma_u = parameters.sigma_u  
        self.theta = parameters.theta
        
        # Model constants
        self.gamma = np.sqrt(self.theta) * self.sigma_v / self.sigma_u
        
    def calculate_price_impact(self, trade_size: float, 
                             market_liquidity: float = 1.0) -> float:
        """
        Trade uchun price impact hisoblash
        
        Args:
            trade_size: Trade hajmi
            market_liquidity: Market likvidligi
            
        Returns:
            Price impact (narx o'zgarishi)
        """
        # Kyle's Lambda formula
        price_impact = self.lambda_param * trade_size / np.sqrt(market_liquidity)
        return price_impact
        
    def calculate_lambda_estimate(self, trade_data: pd.DataFrame) -> float:
        """
        Historical data dan lambda parametrini hisoblash
        
        Args:
            trade_data: Historical trade data (price, volume, etc.)
            
        Returns:
            Lambda parameter estimate
        """
        # Calculate returns
        price_changes = trade_data['price'].pct_change().dropna()
        volumes = trade_data['volume']
        
        # Regression: price_change = lambda * volume + noise
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(volumes, price_changes)
        
        return abs(slope)  # Lambda should be positive
        
    def calculate_market_efficiency_ratio(self) -> float:
        """
        Market efficiency ratio hisoblash
        
        Returns:
            Efficiency ratio (0-1)
        """
        # Higher gamma means more informed trading
        efficiency_ratio = self.gamma / (1 + self.gamma)
        return min(efficiency_ratio, 0.99)
        
    def simulate_trade_impact(self, initial_price: float, 
                            trade_sequence: np.ndarray,
                            time_steps: int = 100) -> Dict[str, np.ndarray]:
        """
        Trade sequence impact simulation
        
        Args:
            initial_price: Boshlang'ich narx
            trade_sequence: Trade hajmlari sequence
            time_steps: Time steps soni
            
        Returns:
            Simulation results
        """
        prices = np.zeros(time_steps)
        cumulative_volume = 0.0
        current_price = initial_price
        
        for i in range(time_steps):
            if i < len(trade_sequence):
                trade_size = trade_sequence[i]
                
                # Price impact calculation
                impact = self.calculate_price_impact(trade_size)
                
                # Update price
                current_price += impact
                
                # Update cumulative volume
                cumulative_volume += abs(trade_size)
                
            prices[i] = current_price
            
        return {
            'prices': prices,
            'cumulative_volume': np.cumsum(np.abs(trade_sequence[:time_steps])),
            'price_impacts': np.diff(np.concatenate([[initial_price], prices]))
        }
        
    def calculate_informed_trader_advantage(self, signal_strength: float) -> float:
        """
        Informed trader advantage hisoblash
        
        Args:
            signal_strength: Signal kuchi (-1 to 1)
            
        Returns:
            Trader advantage
        """
        # Informed trader can predict price direction
        advantage = self.gamma * signal_strength * np.sqrt(self.sigma_v)
        return advantage
        
    def estimate_market_depth(self, current_spread: float) -> float:
        """
        Market depth estimation
        
        Args:
            current_spread: Current bid-ask spread
            
        Returns:
            Estimated market depth
        """
        # Inverse relationship between spread and depth
        # Wider spreads indicate lower liquidity/depth
        estimated_depth = 1.0 / (current_spread + 1e-6)
        return estimated_depth
        
    def calculate_optimal_order_size(self, target_price_impact: float,
                                   market_liquidity: float = 1.0) -> float:
        """
        Optimal order size hisoblash
        
        Args:
            target_price_impact: Maqsadli price impact
            market_liquidity: Market likvidligi
            
        Returns:
            Optimal order size
        """
        # Inverse of price impact formula
        optimal_size = target_price_impact * np.sqrt(market_liquidity) / self.lambda_param
        return optimal_size
        
    def get_model_statistics(self) -> Dict[str, float]:
        """
        Model statistikalari
        
        Returns:
            Dictionary with model statistics
        """
        return {
            'lambda_param': self.lambda_param,
            'sigma_v': self.sigma_v,
            'sigma_u': self.sigma_u,
            'theta': self.theta,
            'gamma': self.gamma,
            'efficiency_ratio': self.calculate_market_efficiency_ratio()
        }
        
    def backtest_model(self, historical_data: pd.DataFrame) -> Dict[str, float]:
        """
        Modelni historical data bo'yicha backtest qilish
        
        Args:
            historical_data: Historical price va volume data
            
        Returns:
            Backtest results
        """
        if len(historical_data) < 50:
            return {'error': 'Insufficient data for backtesting'}
            
        # Calculate actual vs predicted price impacts
        actual_impact = historical_data['price'].pct_change()
        predicted_impact = self.lambda_param * historical_data['volume'] / 1000
        
        # Calculate metrics
        mae = np.mean(np.abs(actual_impact - predicted_impact))
        mse = np.mean((actual_impact - predicted_impact) ** 2)
        
        # Correlation
        correlation = np.corrcoef(actual_impact[1:], predicted_impact[:-1])[0, 1]
        
        return {
            'mae': mae,
            'mse': mse,
            'correlation': correlation,
            'r_squared': correlation ** 2
        }