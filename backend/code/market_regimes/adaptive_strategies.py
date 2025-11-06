"""
Adaptive Strategies Module
Regime-adaptive trading strategies and dynamic risk management
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import warnings

warnings.filterwarnings('ignore')

class StrategyType(Enum):
    """Strategy type enumeration"""
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"
    VOLATILITY_TARGETING = "volatility_targeting"
    RISK_PARITY = "risk_parity"
    DYNAMIC_HEDGING = "dynamic_hedging"

@dataclass
class Position:
    """Position data structure"""
    asset: str
    size: float
    entry_price: float
    current_price: float
    pnl: float
    timestamp: pd.Timestamp

@dataclass
class RiskMetrics:
    """Risk metrics structure"""
    portfolio_volatility: float
    max_drawdown: float
    var_95: float
    expected_shortfall: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float

class RegimeAdaptiveStrategy(ABC):
    """
    Abstract base class for regime-adaptive strategies
    """
    
    def __init__(self, name: str, regime_preferences: Dict):
        """
        Args:
            name: Strategy name
            regime_preferences: Regime-specific preferences
        """
        self.name = name
        self.regime_preferences = regime_preferences
        self.current_regime = "Unknown"
        self.positions = {}
        self.performance_history = []
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame, regime: str) -> pd.DataFrame:
        """Generate trading signals based on regime"""
        pass
        
    @abstractmethod
    def calculate_position_size(self, signal: float, risk_budget: float, regime: str) -> float:
        """Calculate position size based on regime"""
        pass
        
    def update_regime(self, regime: str):
        """Update current regime"""
        self.current_regime = regime
        self._adjust_parameters_for_regime(regime)
        
    def _adjust_parameters_for_regime(self, regime: str):
        """Adjust strategy parameters based on regime"""
        if regime in self.regime_preferences:
            preferences = self.regime_preferences[regime]
            for param, value in preferences.items():
                if hasattr(self, param):
                    setattr(self, param, value)

class TrendFollowingStrategy(RegimeAdaptiveStrategy):
    """
    Regime-adaptive trend following strategy
    """
    
    def __init__(self, lookback_period: int = 50, momentum_threshold: float = 0.02):
        """
        Args:
            lookback_period: Trend detection period
            momentum_threshold: Minimum momentum threshold
        """
        regime_preferences = {
            "Trending": {
                'lookback_period': 30,
                'momentum_threshold': 0.015,
                'position_size_multiplier': 1.5
            },
            "Ranging": {
                'lookback_period': 20,
                'momentum_threshold': 0.03,
                'position_size_multiplier': 0.5
            },
            "High Volatility": {
                'lookback_period': 40,
                'momentum_threshold': 0.025,
                'position_size_multiplier': 0.8
            },
            "Low Volatility": {
                'lookback_period': 60,
                'momentum_threshold': 0.01,
                'position_size_multiplier': 1.2
            },
            "Crisis": {
                'lookback_period': 20,
                'momentum_threshold': 0.05,
                'position_size_multiplier': 0.2
            }
        }
        
        super().__init__("TrendFollowing", regime_preferences)
        self.lookback_period = lookback_period
        self.momentum_threshold = momentum_threshold
        self.position_size_multiplier = 1.0
        
    def generate_signals(self, data: pd.DataFrame, regime: str) -> pd.DataFrame:
        """Generate trend following signals"""
        signals = pd.DataFrame(index=data.index)
        
        for column in data.columns:
            price_series = data[column]
            
            # Calculate moving averages
            short_ma = price_series.rolling(window=min(self.lookback_period//2, 20)).mean()
            long_ma = price_series.rolling(window=self.lookback_period).mean()
            
            # Calculate momentum
            momentum = (price_series - price_series.shift(self.lookback_period)) / price_series.shift(self.lookback_period)
            
            # Generate signals
            long_signal = (short_ma > long_ma) & (momentum > self.momentum_threshold)
            short_signal = (short_ma < long_ma) & (momentum < -self.momentum_threshold)
            
            signals[column] = np.where(long_signal, 1, np.where(short_signal, -1, 0))
            
        return signals
        
    def calculate_position_size(self, signal: float, risk_budget: float, regime: str) -> float:
        """Calculate position size with regime adaptation"""
        base_size = risk_budget
        
        # Apply regime-specific multiplier
        if regime in self.regime_preferences:
            multiplier = self.regime_preferences[regime].get('position_size_multiplier', 1.0)
        else:
            multiplier = 1.0
            
        # Apply volatility adjustment
        volatility_adjustment = min(1.0, 0.1 / risk_budget) if risk_budget > 0 else 0.1
        
        position_size = base_size * self.position_size_multiplier * multiplier * volatility_adjustment
        
        # Limit position size
        max_position = 0.1  # 10% max position
        return np.clip(position_size, -max_position, max_position)

class MeanReversionStrategy(RegimeAdaptiveStrategy):
    """
    Regime-adaptive mean reversion strategy
    """
    
    def __init__(self, lookback_period: int = 20, std_multiplier: float = 2.0):
        """
        Args:
            lookback_period: Mean reversion calculation period
            std_multiplier: Standard deviation multiplier for entry
        """
        regime_preferences = {
            "Ranging": {
                'lookback_period': 15,
                'std_multiplier': 1.5,
                'position_size_multiplier': 1.5
            },
            "Trending": {
                'lookback_period': 30,
                'std_multiplier': 2.5,
                'position_size_multiplier': 0.5
            },
            "High Volatility": {
                'lookback_period': 25,
                'std_multiplier': 3.0,
                'position_size_multiplier': 0.7
            },
            "Low Volatility": {
                'lookback_period': 15,
                'std_multiplier': 1.2,
                'position_size_multiplier': 1.3
            }
        }
        
        super().__init__("MeanReversion", regime_preferences)
        self.lookback_period = lookback_period
        self.std_multiplier = std_multiplier
        self.position_size_multiplier = 1.0
        
    def generate_signals(self, data: pd.DataFrame, regime: str) -> pd.DataFrame:
        """Generate mean reversion signals"""
        signals = pd.DataFrame(index=data.index)
        
        for column in data.columns:
            price_series = data[column]
            
            # Calculate mean and standard deviation
            rolling_mean = price_series.rolling(window=self.lookback_period).mean()
            rolling_std = price_series.rolling(window=self.lookback_period).std()
            
            # Z-score
            z_score = (price_series - rolling_mean) / rolling_std
            
            # Generate signals
            long_signal = z_score < -self.std_multiplier
            short_signal = z_score > self.std_multiplier
            
            signals[column] = np.where(long_signal, 1, np.where(short_signal, -1, 0))
            
        return signals
        
    def calculate_position_size(self, signal: float, risk_budget: float, regime: str) -> float:
        """Calculate position size for mean reversion"""
        base_size = risk_budget
        
        if regime in self.regime_preferences:
            multiplier = self.regime_preferences[regime].get('position_size_multiplier', 1.0)
        else:
            multiplier = 1.0
            
        position_size = base_size * self.position_size_multiplier * multiplier
        
        max_position = 0.08  # 8% max position
        return np.clip(position_size, -max_position, max_position)

class VolatilityTargetingStrategy(RegimeAdaptiveStrategy):
    """
    Volatility targeting strategy with regime adaptation
    """
    
    def __init__(self, target_volatility: float = 0.15, lookback_period: int = 60):
        """
        Args:
            target_volatility: Target portfolio volatility
            lookback_period: Volatility calculation period
        """
        regime_preferences = {
            "High Volatility": {
                'target_volatility': 0.10,
                'leverage_limit': 2.0
            },
            "Low Volatility": {
                'target_volatility': 0.20,
                'leverage_limit': 4.0
            },
            "Crisis": {
                'target_volatility': 0.05,
                'leverage_limit': 1.0
            }
        }
        
        super().__init__("VolatilityTargeting", regime_preferences)
        self.target_volatility = target_volatility
        self.lookback_period = lookback_period
        self.leverage_limit = 3.0
        
    def generate_signals(self, data: pd.DataFrame, regime: str) -> pd.DataFrame:
        """Generate volatility targeting signals"""
        returns = data.pct_change().dropna()
        
        # Calculate rolling volatility
        rolling_vol = returns.rolling(window=self.lookback_period).std() * np.sqrt(252)
        
        # Generate signals based on volatility (long when vol is low, short when vol is high)
        signals = pd.DataFrame(index=data.index)
        
        for column in returns.columns:
            vol_series = rolling_vol[column].dropna()
            
            if len(vol_series) == 0:
                signals[column] = 0
                continue
                
            # Volatility percentile ranks
            vol_percentiles = vol_series.rank(pct=True)
            
            # Long when volatility is in lower percentile, short when high
            long_threshold = 0.3
            short_threshold = 0.7
            
            long_signal = vol_percentiles < long_threshold
            short_signal = vol_percentiles > short_threshold
            
            signals[column] = np.where(long_signal, 1, np.where(short_signal, -1, 0))
            
        return signals
        
    def calculate_position_size(self, signal: float, risk_budget: float, regime: str) -> float:
        """Calculate volatility-adjusted position size"""
        base_size = risk_budget
        
        # Apply regime-specific target volatility
        target_vol = self.target_volatility
        if regime in self.regime_preferences:
            regime_vol = self.regime_preferences[regime].get('target_volatility', self.target_volatility)
            target_vol = regime_vol
            
        # Calculate leverage based on current vs target volatility
        current_vol = 0.15  # This would be calculated from current portfolio
        leverage = target_vol / current_vol if current_vol > 0 else 1.0
        
        # Limit leverage
        leverage = min(leverage, self.leverage_limit)
        
        position_size = base_size * leverage
        
        max_position = 0.15  # 15% max position
        return np.clip(position_size, -max_position, max_position)

class DynamicRiskManager:
    """
    Dynamic risk management system
    """
    
    def __init__(self, max_portfolio_risk: float = 0.02, var_confidence: float = 0.95):
        """
        Args:
            max_portfolio_risk: Maximum portfolio risk (2%)
            var_confidence: VaR confidence level
        """
        self.max_portfolio_risk = max_portfolio_risk
        self.var_confidence = var_confidence
        self.risk_budget_history = []
        
    def calculate_position_limits(self, portfolio_value: float, correlation_matrix: pd.DataFrame, 
                                regime: str) -> Dict[str, float]:
        """
        Calculate position limits based on regime and correlation
        
        Args:
            portfolio_value: Current portfolio value
            correlation_matrix: Asset correlation matrix
            regime: Current market regime
            
        Returns:
            Dict: Position limits for each asset
        """
        # Base risk budget
        base_risk = self.max_portfolio_risk
        
        # Regime-based risk adjustments
        regime_multipliers = {
            "Crisis": 0.3,
            "High Volatility": 0.6,
            "Low Volatility": 1.2,
            "Trending": 1.0,
            "Ranging": 1.1,
            "Mixed/Neutral": 0.8
        }
        
        risk_multiplier = regime_multipliers.get(regime, 1.0)
        adjusted_risk = base_risk * risk_multiplier
        
        # Calculate position limits
        position_limits = {}
        
        for asset in correlation_matrix.columns:
            # Individual asset volatility (would be calculated from historical returns)
            asset_vol = 0.20  # Placeholder
            
            # Position limit based on risk budget and volatility
            max_position = adjusted_risk * portfolio_value / asset_vol
            
            # Apply correlation-based diversification limits
            avg_correlation = correlation_matrix[asset].mean()
            diversification_factor = 1 - avg_correlation * 0.5
            
            final_limit = max_position * diversification_factor
            
            position_limits[asset] = min(final_limit, portfolio_value * 0.10)  # 10% max per asset
            
        return position_limits
        
    def calculate_portfolio_var(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        Calculate portfolio Value at Risk
        
        Args:
            returns: Portfolio returns
            confidence_level: Confidence level for VaR
            
        Returns:
            float: VaR value
        """
        if len(returns) < 30:
            return 0.0
            
        # Historical VaR
        sorted_returns = returns.sort_values()
        var_index = int((1 - confidence_level) * len(sorted_returns))
        var = -sorted_returns.iloc[var_index]
        
        # Adjust for regime
        recent_vol = returns.tail(60).std()
        long_term_vol = returns.std()
        
        if recent_vol > long_term_vol * 1.5:  # High volatility regime
            var *= 1.3
        elif recent_vol < long_term_vol * 0.7:  # Low volatility regime
            var *= 0.8
            
        return var
        
    def calculate_expected_shortfall(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        Calculate Expected Shortfall (Conditional VaR)
        
        Args:
            returns: Portfolio returns
            confidence_level: Confidence level
            
        Returns:
            float: Expected Shortfall
        """
        var = self.calculate_portfolio_var(returns, confidence_level)
        
        tail_returns = returns[returns <= -var]
        if len(tail_returns) > 0:
            return abs(tail_returns.mean())
        else:
            return var
            
    def dynamic_risk_budgeting(self, portfolio_returns: pd.Series, regime: str) -> float:
        """
        Dynamic risk budgeting based on regime
        
        Args:
            portfolio_returns: Historical portfolio returns
            regime: Current market regime
            
        Returns:
            float: Risk budget for current period
        """
        if len(portfolio_returns) < 60:
            return self.max_portfolio_risk
            
        # Calculate recent performance
        recent_performance = portfolio_returns.tail(60)
        
        # Base risk allocation
        risk_budget = self.max_portfolio_risk
        
        # Performance-based adjustments
        recent_sharpe = recent_performance.mean() / recent_performance.std() if recent_performance.std() > 0 else 0
        
        if recent_sharpe > 1.0:  # Good performance
            risk_budget *= 1.1
        elif recent_sharpe < -0.5:  # Poor performance
            risk_budget *= 0.7
            
        # Regime-based adjustments
        regime_adjustments = {
            "Crisis": 0.5,
            "High Volatility": 0.7,
            "Low Volatility": 1.2,
            "Trending": 1.0,
            "Ranging": 1.1
        }
        
        regime_factor = regime_adjustments.get(regime, 1.0)
        risk_budget *= regime_factor
        
        # Volatility-based adjustment
        current_vol = portfolio_returns.tail(60).std()
        long_term_vol = portfolio_returns.std()
        
        if current_vol > long_term_vol * 1.5:
            risk_budget *= 0.8
        elif current_vol < long_term_vol * 0.7:
            risk_budget *= 1.1
            
        return max(risk_budget, 0.005)  # Minimum 0.5% risk

class AdaptivePortfolioManager:
    """
    Multi-regime adaptive portfolio management
    """
    
    def __init__(self, strategies: List[RegimeAdaptiveStrategy], risk_manager: DynamicRiskManager):
        """
        Args:
            strategies: List of adaptive strategies
            risk_manager: Dynamic risk manager
        """
        self.strategies = {strategy.name: strategy for strategy in strategies}
        self.risk_manager = risk_manager
        self.regime_weights = {}
        self.portfolio_history = []
        
    def select_optimal_strategy(self, data: pd.DataFrame, regime: str, 
                              historical_performance: Dict[str, pd.Series]) -> str:
        """
        Select optimal strategy for current regime
        
        Args:
            data: Market data
            regime: Current market regime
            historical_performance: Historical performance by strategy
            
        Returns:
            str: Selected strategy name
        """
        strategy_scores = {}
        
        for strategy_name, strategy in self.strategies.items():
            # Score based on regime fit
            regime_score = self._calculate_regime_fit_score(strategy, regime)
            
            # Score based on historical performance in similar regimes
            performance_score = self._calculate_performance_score(
                historical_performance.get(strategy_name, pd.Series()), regime
            )
            
            # Combined score
            strategy_scores[strategy_name] = 0.6 * regime_score + 0.4 * performance_score
            
        # Select best strategy
        best_strategy = max(strategy_scores, key=strategy_scores.get)
        return best_strategy
        
    def _calculate_regime_fit_score(self, strategy: RegimeAdaptiveStrategy, regime: str) -> float:
        """Calculate how well strategy fits current regime"""
        if regime in strategy.regime_preferences:
            return 1.0  # Perfect fit
        else:
            return 0.3  # Poor fit
            
    def _calculate_performance_score(self, performance: pd.Series, regime: str) -> float:
        """Calculate performance score for regime"""
        if len(performance) == 0:
            return 0.5  # Neutral score for no data
            
        # Calculate performance metrics
        if performance.std() > 0:
            sharpe = performance.mean() / performance.std()
            return min(max(sharpe / 2 + 0.5, 0), 1)  # Normalize to [0,1]
        else:
            return 0.5
            
    def allocate_regime_weights(self, regime_history: pd.Series, 
                              lookback_period: int = 30) -> Dict[str, float]:
        """
        Allocate strategy weights based on regime persistence
        
        Args:
            regime_history: Historical regime classifications
            lookback_period: Weight calculation period
            
        Returns:
            Dict: Strategy weights by regime
        """
        if len(regime_history) < lookback_period:
            # Equal weights if insufficient data
            return {name: 1.0/len(self.strategies) for name in self.strategies.keys()}
            
        # Calculate regime persistence and frequency
        recent_regimes = regime_history.tail(lookback_period)
        
        regime_counts = recent_regimes.value_counts()
        regime_frequencies = regime_counts / len(recent_regimes)
        
        # Allocate weights based on regime frequency
        weights = {}
        
        for strategy_name, strategy in self.strategies.items():
            weight = 0
            
            # Weight based on regime preferences
            for regime, freq in regime_frequencies.items():
                if regime in strategy.regime_preferences:
                    weight += freq
                    
            weights[strategy_name] = weight
            
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v/total_weight for k, v in weights.items()}
        else:
            # Equal weights if no matches
            weights = {name: 1.0/len(self.strategies) for name in self.strategies.keys()}
            
        self.regime_weights = weights
        return weights
        
    def backtest_adaptive_strategy(self, data: pd.DataFrame, regime_data: pd.DataFrame,
                                 initial_capital: float = 100000) -> Dict:
        """
        Backtest adaptive strategy
        
        Args:
            data: Market data
            regime_data: Regime classification data
            initial_capital: Initial portfolio capital
            
        Returns:
            Dict: Backtest results
        """
        portfolio_value = initial_capital
        portfolio_returns = []
        positions = {}
        
        # Align data
        common_index = data.index.intersection(regime_data.index)
        data_aligned = data.loc[common_index]
        regimes_aligned = regime_data.loc[common_index]
        
        # Performance tracking
        strategy_returns = {name: [] for name in self.strategies.keys()}
        regime_performance = {}
        
        for i, (date, row) in enumerate(data_aligned.iterrows()):
            regime = regimes_aligned.iloc[i] if i < len(regimes_aligned) else "Unknown"
            
            # Select strategy for current regime
            historical_perf = {name: pd.Series(strategy_returns[name]) for name in self.strategies.keys()}
            selected_strategy = self.select_optimal_strategy(
                data_aligned.iloc[:i+1], regime, historical_perf
            )
            
            # Generate signals and calculate positions
            strategy = self.strategies[selected_strategy]
            signals = strategy.generate_signals(data_aligned.iloc[:i+1], regime)
            
            if len(signals) > 0:
                latest_signals = signals.iloc[-1]
                
                # Calculate position sizes
                for asset in data_aligned.columns:
                    signal = latest_signals.get(asset, 0)
                    
                    if signal != 0:
                        # Risk-based position sizing
                        risk_budget = self.risk_manager.dynamic_risk_budgeting(
                            pd.Series(portfolio_returns), regime
                        )
                        position_size = strategy.calculate_position_size(
                            signal, risk_budget, regime
                        )
                        
                        positions[asset] = position_size
                        
            # Calculate portfolio return
            if len(portfolio_returns) > 0:
                portfolio_return = 0
                
                for asset, position in positions.items():
                    if asset in data_aligned.columns:
                        asset_return = data_aligned[asset].pct_change().iloc[-1]
                        portfolio_return += position * asset_return
                        
                portfolio_returns.append(portfolio_return)
                portfolio_value *= (1 + portfolio_return)
                
                # Track strategy performance
                strategy_returns[selected_strategy].append(portfolio_return)
                
        # Calculate performance metrics
        portfolio_series = pd.Series(portfolio_returns)
        
        results = {
            'total_return': (portfolio_value / initial_capital) - 1,
            'annualized_return': portfolio_series.mean() * 252,
            'annualized_volatility': portfolio_series.std() * np.sqrt(252),
            'sharpe_ratio': (portfolio_series.mean() * 252) / (portfolio_series.std() * np.sqrt(252)) if portfolio_series.std() > 0 else 0,
            'max_drawdown': self._calculate_max_drawdown(portfolio_series),
            'portfolio_values': initial_capital * (1 + portfolio_series).cumprod(),
            'strategy_usage': {name: len(returns)/len(portfolio_returns) for name, returns in strategy_returns.items()},
            'regime_performance': regime_performance
        }
        
        return results
        
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        cumulative = (1 + returns).cumprod()
        peak = cumulative.expanding().max()
        drawdown = (cumulative - peak) / peak
        return drawdown.min()


if __name__ == "__main__":
    # Test adaptive strategies
    np.random.seed(42)
    
    # Generate sample data
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    asset_data = pd.DataFrame(
        np.random.randn(500, 3).cumsum(axis=0) * 0.02 + 100,
        index=dates,
        columns=['Asset_A', 'Asset_B', 'Asset_C']
    )
    
    # Create strategies
    trend_strategy = TrendFollowingStrategy()
    mean_rev_strategy = MeanReversionStrategy()
    vol_target_strategy = VolatilityTargetingStrategy()
    
    strategies = [trend_strategy, mean_rev_strategy, vol_target_strategy]
    
    # Create risk manager
    risk_manager = DynamicRiskManager(max_portfolio_risk=0.02)
    
    # Create portfolio manager
    portfolio_manager = AdaptivePortfolioManager(strategies, risk_manager)
    
    # Test strategy allocation
    regime_weights = portfolio_manager.allocate_regime_weights(
        pd.Series(['Trending', 'Ranging', 'High Volatility'] * 10)
    )
    
    print("Adaptive Strategy Testing Results:")
    print(f"Strategy weights: {regime_weights}")
    print("Strategies implemented:")
    for name, strategy in portfolio_manager.strategies.items():
        print(f"- {name}: {len(strategy.regime_preferences)} regime preferences")
        
    print("Adaptive strategies module completed successfully")