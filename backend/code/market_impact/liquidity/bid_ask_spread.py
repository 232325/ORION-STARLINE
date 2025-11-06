"""
Bid-Ask Spread Analyzer

Bu modul bid-ask spread ni detailed tahlil qilish uchun
maxsus methods ta'minlaydi.

Bid-ask spread likvidlikning asosiy ko'rsatkichi hisoblanadi va
trading cost larni hisoblashda muhim rol o'ynaydi.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from scipy import stats


@dataclass
class SpreadMetrics:
    """Spread metrics data class"""
    absolute_spread: float
    relative_spread: float
    percentage_spread: float
    mid_price: float
    timestamp: datetime


class BidAskSpreadAnalyzer:
    """
    Bid-Ask Spread Analyzer
    
    Spread tahlili, modeling va forecasting
    """
    
    def __init__(self, data_window: int = 1000):
        """
        Initialize analyzer
        
        Args:
            data_window: Historical data window size
        """
        self.data_window = data_window
        self.spread_history = []
        self.mid_price_history = []
        
    def calculate_spread_metrics(self, bid_price: float, ask_price: float) -> SpreadMetrics:
        """
        Basic spread metrics hisoblash
        
        Args:
            bid_price: Bid price
            ask_price: Ask price
            
        Returns:
            SpreadMetrics object
        """
        absolute_spread = ask_price - bid_price
        mid_price = (bid_price + ask_price) / 2
        relative_spread = absolute_spread / mid_price if mid_price > 0 else 0
        percentage_spread = relative_spread * 100
        
        return SpreadMetrics(
            absolute_spread=absolute_spread,
            relative_spread=relative_spread,
            percentage_spread=percentage_spread,
            mid_price=mid_price,
            timestamp=datetime.now()
        )
        
    def analyze_spread_distribution(self, spread_data: pd.DataFrame) -> Dict[str, float]:
        """
        Spread distribution tahlili
        
        Args:
            spread_data: Historical spread data
            
        Returns:
            Distribution statistics
        """
        spreads = spread_data['spread'].values
        mid_prices = spread_data['mid_price'].values
        relative_spreads = spreads / mid_prices
        
        return {
            'mean_spread': np.mean(spreads),
            'median_spread': np.median(spreads),
            'std_spread': np.std(spreads),
            'min_spread': np.min(spreads),
            'max_spread': np.max(spreads),
            'q25_spread': np.percentile(spreads, 25),
            'q75_spread': np.percentile(spreads, 75),
            'mean_relative_spread': np.mean(relative_spreads),
            'median_relative_spread': np.median(relative_spreads),
            'spread_skewness': stats.skew(spreads),
            'spread_kurtosis': stats.kurtosis(spreads)
        }
        
    def detect_spread_patterns(self, spread_data: pd.DataFrame,
                             time_series: bool = True) -> Dict[str, any]:
        """
        Spread patterns ni detection qilish
        
        Args:
            spread_data: Spread time series data
            time_series: Whether data is time series
            
        Returns:
            Pattern detection results
        """
        results = {
            'patterns': [],
            'statistics': {}
        }
        
        spreads = spread_data['spread'].values
        
        # Trend analysis
        if len(spreads) > 1:
            # Linear trend
            x = np.arange(len(spreads))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, spreads)
            
            results['trend'] = {
                'slope': slope,
                'r_squared': r_value ** 2,
                'is_trending': abs(slope) > std_err * 2
            }
            
            # Mean reversion
            spreads_centered = spreads - np.mean(spreads)
            autocorr = np.corrcoef(spreads_centered[:-1], spreads_centered[1:])[0, 1]
            results['mean_reversion'] = {
                'autocorrelation': autocorr,
                'half_life': -np.log(0.5) / np.log(abs(autocorr)) if autocorr != 0 else np.inf
            }
            
        # Outlier detection
        mean_spread = np.mean(spreads)
        std_spread = np.std(spreads)
        outliers = np.abs(spreads - mean_spread) > 2 * std_spread
        
        results['outliers'] = {
            'count': np.sum(outliers),
            'percentage': np.sum(outliers) / len(spreads) * 100,
            'indices': np.where(outliers)[0].tolist()
        }
        
        # Regime detection
        regimes = self._detect_spread_regimes(spreads)
        results['regimes'] = regimes
        
        return results
        
    def _detect_spread_regimes(self, spreads: np.ndarray) -> Dict[str, any]:
        """Spread regime detection using statistical methods"""
        # Simple regime detection based on percentiles
        q25 = np.percentile(spreads, 25)
        q75 = np.percentile(spreads, 75)
        
        low_regime = spreads <= q25
        high_regime = spreads >= q75
        normal_regime = (spreads > q25) & (spreads < q75)
        
        return {
            'low_spread_periods': {
                'count': np.sum(low_regime),
                'percentage': np.sum(low_regime) / len(spreads) * 100,
                'thresholds': {'max': q25}
            },
            'normal_spread_periods': {
                'count': np.sum(normal_regime),
                'percentage': np.sum(normal_regime) / len(spreads) * 100,
                'thresholds': {'min': q25, 'max': q75}
            },
            'high_spread_periods': {
                'count': np.sum(high_regime),
                'percentage': np.sum(high_regime) / len(spreads) * 100,
                'thresholds': {'min': q75}
            }
        }
        
    def forecast_spread(self, spread_history: pd.DataFrame,
                      forecast_horizon: int = 10,
                      method: str = 'arima') -> Dict[str, any]:
        """
        Spread forecasting
        
        Args:
            spread_history: Historical spread data
            forecast_horizon: Number of periods to forecast
            method: Forecasting method ('arima', 'linear', 'moving_average')
            
        Returns:
            Forecast results
        """
        spreads = spread_history['spread'].values
        
        if method == 'arima':
            return self._arima_forecast(spreads, forecast_horizon)
        elif method == 'linear':
            return self._linear_forecast(spreads, forecast_horizon)
        elif method == 'moving_average':
            return self._moving_average_forecast(spreads, forecast_horizon)
        else:
            raise ValueError(f"Unknown forecast method: {method}")
            
    def _arima_forecast(self, spreads: np.ndarray, horizon: int) -> Dict[str, any]:
        """Simple ARIMA(1,1,1) forecast"""
        try:
            from statsmodels.tsa.arima.model import ARIMA
            
            model = ARIMA(spreads, order=(1, 1, 1))
            fitted_model = model.fit()
            forecast = fitted_model.forecast(steps=horizon)
            
            return {
                'method': 'arima',
                'forecast': forecast.tolist(),
                'confidence_intervals': fitted_model.get_forecast(horizon).conf_int().values.tolist(),
                'model_summary': str(fitted_model.summary())
            }
        except ImportError:
            return self._linear_forecast(spreads, horizon)
            
    def _linear_forecast(self, spreads: np.ndarray, horizon: int) -> Dict[str, any]:
        """Linear trend forecast"""
        x = np.arange(len(spreads))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, spreads)
        
        future_x = np.arange(len(spreads), len(spreads) + horizon)
        forecast = slope * future_x + intercept
        
        # Simple confidence intervals
        prediction_std = np.sqrt(np.mean((spreads - (slope * x + intercept)) ** 2))
        confidence_intervals = []
        
        for i, pred in enumerate(forecast):
            lower = pred - 1.96 * prediction_std
            upper = pred + 1.96 * prediction_std
            confidence_intervals.append([lower, upper])
            
        return {
            'method': 'linear',
            'forecast': forecast.tolist(),
            'confidence_intervals': confidence_intervals,
            'trend_slope': slope,
            'r_squared': r_value ** 2
        }
        
    def _moving_average_forecast(self, spreads: np.ndarray, horizon: int) -> Dict[str, any]:
        """Moving average forecast"""
        window = min(20, len(spreads) // 2)
        ma = np.convolve(spreads, np.ones(window)/window, mode='valid')
        
        # Use last moving average value for all future forecasts
        last_ma = ma[-1] if len(ma) > 0 else np.mean(spreads)
        forecast = [last_ma] * horizon
        
        # Confidence intervals based on historical volatility
        recent_std = np.std(spreads[-window:]) if len(spreads) >= window else np.std(spreads)
        confidence_intervals = []
        
        for i in range(horizon):
            lower = last_ma - 1.96 * recent_std
            upper = last_ma + 1.96 * recent_std
            confidence_intervals.append([lower, upper])
            
        return {
            'method': 'moving_average',
            'forecast': forecast,
            'confidence_intervals': confidence_intervals,
            'ma_window': window,
            'last_ma_value': last_ma
        }
        
    def calculate_spread_cost_impact(self, trade_size: float,
                                   spread_data: pd.DataFrame,
                                   market_impact: float = 0.001) -> Dict[str, float]:
        """
        Spread ni trading cost ga ta'siri hisoblash
        
        Args:
            trade_size: Trade size
            spread_data: Historical spread data
            market_impact: Market impact coefficient
            
        Returns:
            Cost impact analysis
        """
        mean_spread = spread_data['spread'].mean()
        spread_volatility = spread_data['spread'].std()
        
        # Direct spread cost
        direct_spread_cost = mean_spread * trade_size
        
        # Market impact cost
        impact_cost = market_impact * trade_size ** 1.5
        
        # Volatility cost
        volatility_cost = spread_volatility * trade_size * 0.5
        
        total_cost = direct_spread_cost + impact_cost + volatility_cost
        
        return {
            'direct_spread_cost': direct_spread_cost,
            'market_impact_cost': impact_cost,
            'volatility_cost': volatility_cost,
            'total_cost': total_cost,
            'cost_per_share': total_cost / trade_size if trade_size > 0 else 0,
            'cost_percentage': (total_cost / (trade_size * spread_data['mid_price'].mean())) * 100 if trade_size > 0 else 0
        }
        
    def optimize_spread_targets(self, historical_spreads: pd.DataFrame,
                              target_metrics: Dict[str, float]) -> Dict[str, float]:
        """
        Optimal spread targets hisoblash
        
        Args:
            historical_spreads: Historical spread data
            target_metrics: Target performance metrics
            
        Returns:
            Optimal spread targets
        """
        spreads = historical_spreads['spread'].values
        
        # Current statistics
        mean_spread = np.mean(spreads)
        std_spread = np.std(spreads)
        
        # Optimization targets
        if 'cost_reduction_pct' in target_metrics:
            # Reduce cost by certain percentage
            cost_reduction = target_metrics['cost_reduction_pct'] / 100
            optimal_spread = mean_spread * (1 - cost_reduction)
            
        elif 'volatility_threshold' in target_metrics:
            # Target volatility threshold
            vol_threshold = target_metrics['volatility_threshold']
            optimal_spread = mean_spread * (vol_threshold / std_spread) if std_spread > 0 else mean_spread
            
        elif 'spread_target' in target_metrics:
            # Direct spread target
            optimal_spread = target_metrics['spread_target']
            
        else:
            optimal_spread = mean_spread
            
        # Calculate implementation difficulty
        current_variance = np.var(spreads)
        target_variance = (optimal_spread - mean_spread) ** 2
        implementation_difficulty = min(100, (target_variance / current_variance) * 100)
        
        return {
            'optimal_spread': optimal_spread,
            'current_spread': mean_spread,
            'spread_adjustment': optimal_spread - mean_spread,
            'adjustment_percentage': ((optimal_spread - mean_spread) / mean_spread) * 100,
            'implementation_difficulty': implementation_difficulty,
            'expected_cost_impact': self.calculate_spread_cost_impact(
                1000, historical_spreads.iloc[:100].assign(spread=[optimal_spread]*100)
            )
        }
        
    def analyze_spread_microstructure(self, order_book_data: pd.DataFrame) -> Dict[str, any]:
        """
        Order book level da spread microstructure tahlili
        
        Args:
            order_book_data: Order book level data
            
        Returns:
            Microstructure analysis
        """
        results = {}
        
        # Extract bid and ask levels
        bid_levels = []
        ask_levels = []
        
        if 'bids' in order_book_data.columns:
            for bids_str in order_book_data['bids']:
                if isinstance(bids_str, str):
                    # Parse bid levels (price, size format)
                    levels = bids_str.split(';')
                    for level in levels:
                        if ',' in level:
                            price, size = level.split(',')
                            bid_levels.append(float(price))
        
        if 'asks' in order_book_data.columns:
            for asks_str in order_book_data['asks']:
                if isinstance(asks_str, str):
                    # Parse ask levels
                    levels = asks_str.split(';')
                    for level in levels:
                        if ',' in level:
                            price, size = level.split(',')
                            ask_levels.append(float(price))
                            
        if bid_levels and ask_levels:
            # Best bid and ask
            best_bid = max(bid_levels)
            best_ask = min(ask_levels)
            
            # Spread calculations
            absolute_spread = best_ask - best_bid
            mid_price = (best_bid + best_ask) / 2
            
            # Level analysis
            bid_depth = len([p for p in bid_levels if p >= best_bid * 0.99])
            ask_depth = len([p for p in ask_levels if p <= best_ask * 1.01])
            
            results = {
                'best_bid': best_bid,
                'best_ask': best_ask,
                'absolute_spread': absolute_spread,
                'relative_spread': absolute_spread / mid_price,
                'mid_price': mid_price,
                'bid_levels_count': bid_depth,
                'ask_levels_count': ask_depth,
                'total_levels': bid_depth + ask_depth,
                'book_imbalance': (bid_depth - ask_depth) / (bid_depth + ask_depth + 1e-6),
                'depth_spread_ratio': absolute_spread / (bid_depth + ask_depth + 1e-6)
            }
            
        return results
        
    def generate_spread_report(self, spread_data: pd.DataFrame,
                             analysis_results: Dict[str, any]) -> str:
        """
        Spread analysis report generation
        
        Args:
            spread_data: Original spread data
            analysis_results: Analysis results
            
        Returns:
            Formatted report
        """
        report = []
        report.append("=== BID-ASK SPREAD ANALYSIS REPORT ===")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Data points: {len(spread_data)}")
        report.append("")
        
        # Distribution statistics
        if 'statistics' in analysis_results:
            stats = analysis_results['statistics']
            report.append("SPREAD DISTRIBUTION:")
            report.append(f"  Mean: {stats.get('mean_spread', 0):.4f}")
            report.append(f"  Median: {stats.get('median_spread', 0):.4f}")
            report.append(f"  Std Dev: {stats.get('std_spread', 0):.4f}")
            report.append(f"  Range: [{stats.get('min_spread', 0):.4f}, {stats.get('max_spread', 0):.4f}]")
            report.append(f"  Relative Spread: {stats.get('mean_relative_spread', 0):.4f}")
            report.append("")
            
        # Patterns
        if 'patterns' in analysis_results:
            report.append("SPREAD PATTERNS:")
            if 'trend' in analysis_results['patterns']:
                trend = analysis_results['patterns']['trend']
                report.append(f"  Trend: {'Yes' if trend['is_trending'] else 'No'} (R²: {trend['r_squared']:.3f})")
            if 'mean_reversion' in analysis_results['patterns']:
                mr = analysis_results['patterns']['mean_reversion']
                report.append(f"  Mean Reversion: {mr['autocorrelation']:.3f} (Half-life: {mr['half_life']:.1f})")
            report.append("")
            
        # Outliers
        if 'outliers' in analysis_results:
            outliers = analysis_results['outliers']
            report.append("OUTLIERS:")
            report.append(f"  Count: {outliers['count']}")
            report.append(f"  Percentage: {outliers['percentage']:.1f}%")
            report.append("")
            
        # Regimes
        if 'regimes' in analysis_results:
            report.append("SPREAD REGIMES:")
            for regime, data in analysis_results['regimes'].items():
                report.append(f"  {regime}: {data['count']} periods ({data['percentage']:.1f}%)")
            report.append("")
            
        return "\n".join(report)
        
    def get_analyzer_statistics(self) -> Dict[str, any]:
        """
        Analyzer statistics
        
        Returns:
            Analyzer statistics
        """
        return {
            'data_window': self.data_window,
            'history_size': len(self.spread_history),
            'mid_price_history_size': len(self.mid_price_history),
            'last_update': datetime.now().isoformat() if self.spread_history else None
        }