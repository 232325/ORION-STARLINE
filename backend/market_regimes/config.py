"""
Market Regime Detection Configuration Module
Comprehensive configuration settings for the market regime system
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np

@dataclass
class RegimeDetectionConfig:
    """Regime detection configuration"""
    lookback_window: int = 252
    transition_threshold: float = 0.7
    min_data_points: int = 60
    volatility_window: int = 20
    crisis_threshold: float = -0.15
    high_vol_percentile: float = 0.75
    low_vol_percentile: float = 0.25
    
@dataclass
class CorrelationConfig:
    """Cross-asset correlation configuration"""
    correlation_window: int = 60
    min_periods: int = 30
    n_regimes: int = 3
    n_factors: int = 5
    factor_method: str = 'pca'
    
@dataclass
class StrategyConfig:
    """Adaptive strategy configuration"""
    max_portfolio_risk: float = 0.02
    var_confidence: float = 0.95
    position_size_limit: float = 0.10
    leverage_limit: float = 3.0
    rebalancing_frequency: str = 'daily'  # 'daily', 'weekly', 'monthly'
    
@dataclass
class RiskManagementConfig:
    """Risk management configuration"""
    max_drawdown_limit: float = 0.20
    stop_loss_percentage: float = 0.05
    take_profit_percentage: float = 0.15
    correlation_limit: float = 0.80
    concentration_limit: float = 0.25
    stress_test_scenarios: List[Dict] = None
    
    def __post_init__(self):
        if self.stress_test_scenarios is None:
            self.stress_test_scenarios = [
                {
                    'name': 'Market Crash',
                    'market_shock': -0.20,
                    'volatility_multiplier': 3.0,
                    'correlation_increase': 0.5
                },
                {
                    'name': 'High Volatility',
                    'market_shock': -0.10,
                    'volatility_multiplier': 2.0,
                    'correlation_increase': 0.3
                },
                {
                    'name': 'Rising Rates',
                    'market_shock': -0.05,
                    'volatility_multiplier': 1.5,
                    'correlation_increase': 0.2
                }
            ]

@dataclass
class DataConfig:
    """Market data configuration"""
    data_source: str = 'yahoo'  # 'yahoo', 'bloomberg', 'alpha_vantage'
    update_frequency: str = '1min'  # '1min', '5min', '1hour', '1day'
    historical_periods: int = 252 * 5  # 5 years
    real_time_buffer_size: int = 1000
    data_validation: bool = True
    missing_data_handling: str = 'forward_fill'  # 'forward_fill', 'drop', 'interpolate'

@dataclass
class BacktestConfig:
    """Backtesting configuration"""
    initial_capital: float = 100000
    start_date: str = '2020-01-01'
    end_date: str = '2024-01-01'
    benchmark_symbol: str = 'SPY'
    transaction_costs: float = 0.001  # 0.1%
    slippage: float = 0.0005  # 0.05%
    min_trade_size: float = 1000
    max_positions: int = 20
    
@dataclass
class SystemConfig:
    """Main system configuration"""
    regime_detection: RegimeDetectionConfig = RegimeDetectionConfig()
    correlation: CorrelationConfig = CorrelationConfig()
    strategy: StrategyConfig = StrategyConfig()
    risk: RiskManagementConfig = RiskManagementConfig()
    data: DataConfig = DataConfig()
    backtest: BacktestConfig = BacktestConfig()
    
    # System parameters
    logging_level: str = 'INFO'
    save_intermediate_results: bool = True
    parallel_processing: bool = True
    max_workers: int = 4
    cache_results: bool = True
    output_directory: str = '/workspace/code/market_regimes/output'
    
    def __post_init__(self):
        # Create output directory
        os.makedirs(self.output_directory, exist_ok=True)

class RegimePreferences:
    """Pre-defined regime preferences for different strategies"""
    
    @staticmethod
    def get_trend_following_preferences() -> Dict:
        return {
            "Trending": {
                'lookback_period': 30,
                'momentum_threshold': 0.015,
                'position_size_multiplier': 1.5,
                'confidence_threshold': 0.7
            },
            "Ranging": {
                'lookback_period': 20,
                'momentum_threshold': 0.03,
                'position_size_multiplier': 0.5,
                'confidence_threshold': 0.8
            },
            "High Volatility": {
                'lookback_period': 40,
                'momentum_threshold': 0.025,
                'position_size_multiplier': 0.8,
                'confidence_threshold': 0.6
            },
            "Low Volatility": {
                'lookback_period': 60,
                'momentum_threshold': 0.01,
                'position_size_multiplier': 1.2,
                'confidence_threshold': 0.9
            },
            "Crisis": {
                'lookback_period': 20,
                'momentum_threshold': 0.05,
                'position_size_multiplier': 0.2,
                'confidence_threshold': 0.4
            }
        }
    
    @staticmethod
    def get_mean_reversion_preferences() -> Dict:
        return {
            "Ranging": {
                'lookback_period': 15,
                'std_multiplier': 1.5,
                'position_size_multiplier': 1.5,
                'mean_reversion_threshold': 2.0
            },
            "Trending": {
                'lookback_period': 30,
                'std_multiplier': 2.5,
                'position_size_multiplier': 0.5,
                'mean_reversion_threshold': 3.0
            },
            "High Volatility": {
                'lookback_period': 25,
                'std_multiplier': 3.0,
                'position_size_multiplier': 0.7,
                'mean_reversion_threshold': 2.5
            },
            "Low Volatility": {
                'lookback_period': 15,
                'std_multiplier': 1.2,
                'position_size_multiplier': 1.3,
                'mean_reversion_threshold': 1.5
            }
        }
    
    @staticmethod
    def get_volatility_targeting_preferences() -> Dict:
        return {
            "High Volatility": {
                'target_volatility': 0.10,
                'leverage_limit': 2.0,
                'rebalance_frequency': 'daily'
            },
            "Low Volatility": {
                'target_volatility': 0.20,
                'leverage_limit': 4.0,
                'rebalance_frequency': 'weekly'
            },
            "Crisis": {
                'target_volatility': 0.05,
                'leverage_limit': 1.0,
                'rebalance_frequency': 'hourly'
            }
        }
    
    @staticmethod
    def get_risk_parity_preferences() -> Dict:
        return {
            "Normal Market": {
                'volatility_target': 0.15,
                'correlation_adjustment': True,
                'rebalance_threshold': 0.05
            },
            "High Correlation": {
                'volatility_target': 0.12,
                'correlation_adjustment': True,
                'rebalance_threshold': 0.03
            },
            "Low Correlation": {
                'volatility_target': 0.18,
                'correlation_adjustment': False,
                'rebalance_threshold': 0.08
            }
        }

class IndicatorWeights:
    """Pre-defined indicator weights for regime detection"""
    
    @staticmethod
    def get_trend_indicators() -> Dict[str, float]:
        return {
            'moving_average_slope': 0.3,
            'momentum': 0.25,
            'price_acceleration': 0.2,
            'volume_trend': 0.15,
            'breakout_strength': 0.1
        }
    
    @staticmethod
    def get_volatility_indicators() -> Dict[str, float]:
        return {
            'realized_volatility': 0.4,
            'garch_volatility': 0.3,
            'atr': 0.2,
            'volatility_regime': 0.1
        }
    
    @staticmethod
    def get_correlation_indicators() -> Dict[str, float]:
        return {
            'rolling_correlation': 0.4,
            'correlation_persistence': 0.3,
            'regime_correlation': 0.2,
            'factor_correlation': 0.1
        }

class AssetUniverse:
    """Pre-defined asset universes for different strategies"""
    
    @staticmethod
    def get_equity_universe() -> List[str]:
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK.B',
            'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'MA', 'BAC', 'ADBE', 'CRM',
            'NFLX', 'DIS', 'PYPL', 'VZ', 'INTC', 'CMCSA', 'PFE', 'T', 'XOM',
            'CVX', 'WMT', 'KO', 'PEP', 'COST', 'ABT', 'TMO', 'MDT', 'DHR',
            'BMY', 'LLY', 'NEE', 'TXN', 'QCOM', 'HON', 'LIN', 'LOW', 'SBUX'
        ]
    
    @staticmethod
    def get_multi_asset_universe() -> Dict[str, List[str]]:
        return {
            'equities': AssetUniverse.get_equity_universe(),
            'bonds': ['TLT', 'IEF', 'SHY', 'LQD', 'HYG', 'EMB', 'BWX'],
            'commodities': ['GLD', 'SLV', 'USO', 'DBA', 'DBB', 'DBE'],
            'currencies': ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 
                          'USDCAD=X', 'NZDUSD=X', 'USDCHF=X'],
            'crypto': ['BTC-USD', 'ETH-USD', 'BNB-USD', 'ADA-USD', 'SOL-USD']
        }
    
    @staticmethod
    def get_sector_etfs() -> List[str]:
        return [
            'XLK', 'XLF', 'XLV', 'XLE', 'XLI', 'XLB', 'XLRE', 'XLU',
            'XLP', 'XLY', 'XLC', 'XLS', 'XPH', 'XME', 'XRT'
        ]

class PerformanceBenchmarks:
    """Performance benchmarks for different market regimes"""
    
    @staticmethod
    def get_benchmarks() -> Dict[str, Dict]:
        return {
            "Trending": {
                "S&P 500": {"return": 0.12, "volatility": 0.18, "sharpe": 0.67},
                "Nasdaq": {"return": 0.15, "volatility": 0.22, "sharpe": 0.68},
                "Russell 2000": {"return": 0.10, "volatility": 0.20, "sharpe": 0.50}
            },
            "Ranging": {
                "S&P 500": {"return": 0.06, "volatility": 0.12, "sharpe": 0.50},
                "Nasdaq": {"return": 0.08, "volatility": 0.15, "sharpe": 0.53},
                "Russell 2000": {"return": 0.05, "volatility": 0.14, "sharpe": 0.36}
            },
            "High Volatility": {
                "S&P 500": {"return": 0.04, "volatility": 0.30, "sharpe": 0.13},
                "Nasdaq": {"return": 0.02, "volatility": 0.35, "sharpe": 0.06},
                "Russell 2000": {"return": 0.00, "volatility": 0.32, "sharpe": 0.00}
            },
            "Low Volatility": {
                "S&P 500": {"return": 0.08, "volatility": 0.10, "sharpe": 0.80},
                "Nasdaq": {"return": 0.10, "volatility": 0.12, "sharpe": 0.83},
                "Russell 2000": {"return": 0.07, "volatility": 0.11, "sharpe": 0.64}
            },
            "Crisis": {
                "S&P 500": {"return": -0.15, "volatility": 0.45, "sharpe": -0.33},
                "Nasdaq": {"return": -0.20, "volatility": 0.50, "sharpe": -0.40},
                "Russell 2000": {"return": -0.18, "volatility": 0.48, "sharpe": -0.38}
            }
        }

def get_default_config() -> SystemConfig:
    """Get default system configuration"""
    return SystemConfig()

def get_conservative_config() -> SystemConfig:
    """Get conservative configuration for risk-averse strategies"""
    config = SystemConfig()
    config.strategy.max_portfolio_risk = 0.015
    config.risk.max_drawdown_limit = 0.15
    config.risk.concentration_limit = 0.20
    config.backtest.transaction_costs = 0.0015
    return config

def get_aggressive_config() -> SystemConfig:
    """Get aggressive configuration for high-return strategies"""
    config = SystemConfig()
    config.strategy.max_portfolio_risk = 0.035
    config.strategy.leverage_limit = 5.0
    config.risk.max_drawdown_limit = 0.25
    config.risk.concentration_limit = 0.30
    config.backtest.transaction_costs = 0.0005
    return config

def get_crypto_config() -> SystemConfig:
    """Get configuration optimized for cryptocurrency trading"""
    config = SystemConfig()
    config.regime_detection.volatility_window = 30
    config.correlation.correlation_window = 30
    config.strategy.max_portfolio_risk = 0.05
    config.risk.stop_loss_percentage = 0.10
    config.data.update_frequency = '5min'
    config.backtest.transaction_costs = 0.002
    return config

if __name__ == "__main__":
    # Test configuration
    print("Testing Market Regime Configuration...")
    
    # Default config
    default_config = get_default_config()
    print(f"Default config created with {len(default_config.__dict__)} parameters")
    
    # Conservative config
    conservative_config = get_conservative_config()
    print(f"Conservative config: max_risk = {conservative_config.strategy.max_portfolio_risk}")
    
    # Aggressive config
    aggressive_config = get_aggressive_config()
    print(f"Aggressive config: leverage_limit = {aggressive_config.strategy.leverage_limit}")
    
    # Crypto config
    crypto_config = get_crypto_config()
    print(f"Crypto config: update_frequency = {crypto_config.data.update_frequency}")
    
    # Test preferences
    trend_prefs = RegimePreferences.get_trend_following_preferences()
    print(f"Trend following preferences: {len(trend_prefs)} regimes")
    
    # Test asset universe
    equity_universe = AssetUniverse.get_equity_universe()
    print(f"Equity universe: {len(equity_universe)} symbols")
    
    print("Configuration module completed successfully")