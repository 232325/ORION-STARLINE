"""
Market Utilities
===============

Market-specific utility functions
"""

import math
from typing import Dict, List, Optional, Any, Tuple

class PriceFormatter:
    """Price formatting utility"""
    
    @staticmethod
    def format_price(price: float, symbol: str) -> str:
        """Format price based on symbol type"""
        if '/' in symbol and len(symbol.split('/')) == 2:
            # Forex pairs - 5 decimal places
            return f"{price:.5f}"
        elif symbol.startswith('XAU') or symbol.startswith('XAG'):
            # Precious metals - 2 decimal places
            return f"{price:.2f}"
        elif symbol in ['BTC/USD', 'ETH/USD']:
            # Crypto - 2 decimal places
            return f"{price:.2f}"
        else:
            # Stocks - 2 decimal places
            return f"{price:.2f}"
    
    @staticmethod
    def calculate_spread_bps(buy_price: float, sell_price: float) -> float:
        """Calculate spread in basis points"""
        if buy_price <= 0 or sell_price <= 0:
            return 0.0
        
        mid_price = (buy_price + sell_price) / 2
        spread = sell_price - buy_price
        return (spread / mid_price) * 10000
    
    @staticmethod
    def calculate_price_impact(executed_quantity: int, remaining_quantity: int, 
                             initial_price: float) -> float:
        """Calculate price impact of order"""
        if remaining_quantity <= 0:
            return 0.0
        
        # Simplified square root impact model
        filled_ratio = executed_quantity / (executed_quantity + remaining_quantity)
        impact_factor = math.sqrt(filled_ratio)
        
        return initial_price * 0.001 * impact_factor  # 0.1% base impact

class VolumeCalculator:
    """Volume calculation utility"""
    
    @staticmethod
    def calculate_adv(volume_data: List[float], window: int = 20) -> float:
        """Calculate Average Daily Volume"""
        if not volume_data:
            return 0.0
        
        recent_volume = volume_data[-window:] if len(volume_data) >= window else volume_data
        return sum(recent_volume) / len(recent_volume)
    
    @staticmethod
    def calculate_volume_weighted_average_price(trades: List[Dict]) -> float:
        """Calculate VWAP from trade data"""
        if not trades:
            return 0.0
        
        total_volume = sum(trade['quantity'] for trade in trades)
        if total_volume == 0:
            return 0.0
        
        vwap = sum(trade['price'] * trade['quantity'] for trade in trades) / total_volume
        return vwap
    
    @staticmethod
    def calculate_market_impact_cost(position_size: float, avg_daily_volume: float,
                                   volatility: float) -> float:
        """Estimate market impact cost"""
        if avg_daily_volume <= 0:
            return 0.0
        
        # Participation rate
        participation_rate = position_size / avg_daily_volume
        
        # Market impact cost (simplified model)
        impact_cost = volatility * math.sqrt(participation_rate) * position_size
        
        return impact_cost

class RiskCalculator:
    """Risk calculation utility"""
    
    @staticmethod
    def calculate_var(returns: List[float], confidence_level: float = 0.95) -> Optional[float]:
        """Calculate Value at Risk"""
        if len(returns) < 2:
            return None
        
        sorted_returns = sorted(returns)
        index = int((1 - confidence_level) * len(sorted_returns))
        
        if index >= len(sorted_returns):
            index = len(sorted_returns) - 1
        
        return abs(sorted_returns[index])
    
    @staticmethod
    def calculate_max_drawdown(prices: List[float]) -> Tuple[float, float, float]:
        """Calculate maximum drawdown"""
        if len(prices) < 2:
            return 0.0, 0, 0
        
        max_drawdown = 0.0
        peak_index = 0
        trough_index = 0
        
        peak = prices[0]
        
        for i, price in enumerate(prices):
            if price > peak:
                peak = price
                peak_index = i
            
            drawdown = (peak - price) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                trough_index = i
        
        return max_drawdown, peak_index, trough_index
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> Optional[float]:
        """Calculate Sharpe ratio"""
        if len(returns) < 2:
            return None
        
        avg_return = sum(returns) / len(returns)
        excess_return = avg_return - risk_free_rate
        
        # Calculate standard deviation
        variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            return None
        
        return excess_return / std_dev
    
    @staticmethod
    def calculate_beta(stock_returns: List[float], market_returns: List[float]) -> Optional[float]:
        """Calculate beta coefficient"""
        if len(stock_returns) != len(market_returns) or len(stock_returns) < 2:
            return None
        
        n = len(stock_returns)
        
        # Calculate means
        stock_mean = sum(stock_returns) / n
        market_mean = sum(market_returns) / n
        
        # Calculate covariance and variance
        covariance = sum((stock_returns[i] - stock_mean) * (market_returns[i] - market_mean) 
                        for i in range(n)) / (n - 1)
        
        market_variance = sum((r - market_mean) ** 2 for r in market_returns) / (n - 1)
        
        if market_variance == 0:
            return None
        
        return covariance / market_variance

class SharpeRatioCalculator:
    """Sharpe ratio calculator with additional metrics"""
    
    def __init__(self, risk_free_rate: float = 0.0):
        self.risk_free_rate = risk_free_rate
    
    def calculate_portfolio_metrics(self, returns: List[float]) -> Dict[str, float]:
        """Calculate comprehensive portfolio metrics"""
        if len(returns) < 2:
            return {}
        
        # Basic statistics
        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
        std_dev = math.sqrt(variance)
        
        # Sharpe ratio
        excess_return = avg_return - self.risk_free_rate
        sharpe_ratio = excess_return / std_dev if std_dev > 0 else 0.0
        
        # Additional metrics
        min_return = min(returns)
        max_return = max(returns)
        
        # Skewness (simplified)
        skewness = sum((r - avg_return) ** 3 for r in returns) / (len(returns) * std_dev ** 3) if std_dev > 0 else 0
        
        # Kurtosis (simplified)
        kurtosis = sum((r - avg_return) ** 4 for r in returns) / (len(returns) * std_dev ** 4) if std_dev > 0 else 0
        
        return {
            'avg_return': avg_return,
            'std_dev': std_dev,
            'sharpe_ratio': sharpe_ratio,
            'min_return': min_return,
            'max_return': max_return,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'excess_return': excess_return
        }