"""
Advanced Backtesting Framework
===============================

Bu modul ilg'or backtesting texnikalarini o'z ichiga oladi:
- Walk-Forward Optimization - Rolling window optimization
- Monte Carlo Simulation - Statistical robustness testing
- Multi-Asset Backtesting - Portfolio-level testing
- Transaction Cost Modeling - Realistic slippage and fees
- Risk-Adjusted Metrics - Sharpe, Sortino, Calmar ratios
- Market Regime Analysis - Performance across different market conditions

Author: AI Trading Evolution
Date: 2025-11-04
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict
import matplotlib.pyplot as plt
from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Enums & Data Classes
# ============================================================================

class MarketRegime(Enum):
    """Market rejimi"""
    BULL = "bull_market"
    BEAR = "bear_market"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"


class OrderType(Enum):
    """Order turi"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"


@dataclass
class Trade:
    """Trade ma'lumoti"""
    entry_time: datetime
    exit_time: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    size: float
    direction: str  # 'long' or 'short'
    pnl: float = 0.0
    fees: float = 0.0
    slippage: float = 0.0
    
    def close(self, exit_time: datetime, exit_price: float, fees: float, slippage: float):
        """Trade yopish"""
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.fees += fees
        self.slippage += slippage
        
        if self.direction == 'long':
            self.pnl = (exit_price - self.entry_price) * self.size - self.fees - self.slippage
        else:  # short
            self.pnl = (self.entry_price - exit_price) * self.size - self.fees - self.slippage
            
    def to_dict(self) -> Dict:
        return {
            'entry_time': self.entry_time,
            'exit_time': self.exit_time,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'size': self.size,
            'direction': self.direction,
            'pnl': self.pnl,
            'fees': self.fees,
            'slippage': self.slippage
        }


@dataclass
class BacktestConfig:
    """Backtest konfiguratsiya"""
    initial_capital: float = 10000.0
    commission: float = 0.001  # 0.1%
    slippage_pct: float = 0.0005  # 0.05%
    position_size_pct: float = 0.95  # Use 95% of capital
    max_positions: int = 1
    enable_shorting: bool = True
    risk_free_rate: float = 0.02  # 2% annual


@dataclass
class BacktestResult:
    """Backtest natijasi"""
    trades: List[Trade] = field(default_factory=list)
    equity_curve: List[float] = field(default_factory=list)
    timestamps: List[datetime] = field(default_factory=list)
    
    # Performance metrics
    total_return: float = 0.0
    annual_return: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    
    # Trade statistics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0
    
    def calculate_metrics(self, initial_capital: float, risk_free_rate: float = 0.02):
        """Metrics hisoblash"""
        if not self.trades or not self.equity_curve:
            return
            
        # Total return
        final_equity = self.equity_curve[-1]
        self.total_return = (final_equity - initial_capital) / initial_capital
        
        # Annualized return
        days = (self.timestamps[-1] - self.timestamps[0]).days
        years = days / 365.25
        self.annual_return = ((final_equity / initial_capital) ** (1 / years)) - 1 if years > 0 else 0
        
        # Returns for Sharpe and Sortino
        returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
        
        if len(returns) > 0:
            # Sharpe Ratio
            excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
            self.sharpe_ratio = np.sqrt(252) * np.mean(excess_returns) / np.std(returns) if np.std(returns) > 0 else 0
            
            # Sortino Ratio
            downside_returns = returns[returns < 0]
            downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0.0001
            self.sortino_ratio = np.sqrt(252) * np.mean(excess_returns) / downside_std
        
        # Maximum Drawdown
        peak = self.equity_curve[0]
        max_dd = 0
        for equity in self.equity_curve:
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak
            if dd > max_dd:
                max_dd = dd
        self.max_drawdown = max_dd
        
        # Calmar Ratio
        self.calmar_ratio = self.annual_return / self.max_drawdown if self.max_drawdown > 0 else 0
        
        # Trade statistics
        self.total_trades = len([t for t in self.trades if t.exit_time is not None])
        winning = [t for t in self.trades if t.pnl > 0]
        losing = [t for t in self.trades if t.pnl < 0]
        
        self.winning_trades = len(winning)
        self.losing_trades = len(losing)
        self.win_rate = self.winning_trades / self.total_trades if self.total_trades > 0 else 0
        
        self.avg_win = np.mean([t.pnl for t in winning]) if winning else 0
        self.avg_loss = np.mean([t.pnl for t in losing]) if losing else 0
        self.largest_win = max([t.pnl for t in winning]) if winning else 0
        self.largest_loss = min([t.pnl for t in losing]) if losing else 0
        
        # Profit Factor
        total_wins = sum([t.pnl for t in winning])
        total_losses = abs(sum([t.pnl for t in losing]))
        self.profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
    def to_dict(self) -> Dict:
        return {
            'total_return': self.total_return,
            'annual_return': self.annual_return,
            'sharpe_ratio': self.sharpe_ratio,
            'sortino_ratio': self.sortino_ratio,
            'calmar_ratio': self.calmar_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'largest_win': self.largest_win,
            'largest_loss': self.largest_loss
        }


# ============================================================================
# Backtesting Engine
# ============================================================================

class BacktestEngine:
    """Advanced backtesting engine"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.reset()
        
    def reset(self):
        """Reset engine"""
        self.equity = self.config.initial_capital
        self.positions = []
        self.trades = []
        self.equity_curve = [self.config.initial_capital]
        self.timestamps = []
        
    def execute_trade(self, timestamp: datetime, price: float, 
                     signal: str, size: Optional[float] = None):
        """Trade bajarish"""
        
        # Calculate fees and slippage
        if size is None:
            size = (self.equity * self.config.position_size_pct) / price
            
        fees = size * price * self.config.commission
        slippage = size * price * self.config.slippage_pct
        
        if signal == 'buy' or signal == 'long':
            # Open long position
            if len(self.positions) < self.config.max_positions:
                trade = Trade(
                    entry_time=timestamp,
                    exit_time=None,
                    entry_price=price,
                    exit_price=None,
                    size=size,
                    direction='long',
                    fees=fees,
                    slippage=slippage
                )
                self.positions.append(trade)
                self.equity -= (size * price + fees + slippage)
                
        elif signal == 'sell' or signal == 'short':
            # Close long positions
            for pos in self.positions[:]:
                if pos.direction == 'long':
                    pos.close(timestamp, price, fees, slippage)
                    self.equity += (pos.size * price - fees - slippage)
                    self.trades.append(pos)
                    self.positions.remove(pos)
                    
            # Open short position if enabled
            if self.config.enable_shorting and signal == 'short':
                if len(self.positions) < self.config.max_positions:
                    trade = Trade(
                        entry_time=timestamp,
                        exit_time=None,
                        entry_price=price,
                        exit_price=None,
                        size=size,
                        direction='short',
                        fees=fees,
                        slippage=slippage
                    )
                    self.positions.append(trade)
                    self.equity += (size * price - fees - slippage)
                    
    def update_equity(self, timestamp: datetime, current_price: float):
        """Equity yangilash"""
        # Mark-to-market equity
        unrealized_pnl = 0
        for pos in self.positions:
            if pos.direction == 'long':
                unrealized_pnl += (current_price - pos.entry_price) * pos.size
            else:  # short
                unrealized_pnl += (pos.entry_price - current_price) * pos.size
                
        total_equity = self.equity + unrealized_pnl
        self.equity_curve.append(total_equity)
        self.timestamps.append(timestamp)
        
    def run(self, df: pd.DataFrame, strategy: Callable) -> BacktestResult:
        """Backtest ishlatish"""
        self.reset()
        
        logger.info(f"Running backtest on {len(df)} data points")
        
        for i, row in df.iterrows():
            # Get strategy signal
            signal = strategy(df.iloc[:i+1])
            
            # Execute trade if signal
            if signal in ['buy', 'sell', 'long', 'short']:
                self.execute_trade(row['timestamp'], row['close'], signal)
                
            # Update equity
            self.update_equity(row['timestamp'], row['close'])
            
        # Close all open positions
        if len(df) > 0:
            last_row = df.iloc[-1]
            for pos in self.positions[:]:
                fees = pos.size * last_row['close'] * self.config.commission
                slippage = pos.size * last_row['close'] * self.config.slippage_pct
                pos.close(last_row['timestamp'], last_row['close'], fees, slippage)
                self.trades.append(pos)
                
        # Create result
        result = BacktestResult(
            trades=self.trades,
            equity_curve=self.equity_curve,
            timestamps=self.timestamps
        )
        result.calculate_metrics(self.config.initial_capital, self.config.risk_free_rate)
        
        logger.info(f"Backtest complete: {result.total_trades} trades, "
                   f"{result.total_return*100:.2f}% return, "
                   f"Sharpe: {result.sharpe_ratio:.2f}")
        
        return result


# ============================================================================
# Walk-Forward Optimization
# ============================================================================

class WalkForwardOptimizer:
    """Walk-forward optimization"""
    
    def __init__(self, config: BacktestConfig,
                 training_window: int = 252,  # 1 year
                 testing_window: int = 63,    # 3 months
                 step_size: int = 21):        # 1 month
        self.config = config
        self.training_window = training_window
        self.testing_window = testing_window
        self.step_size = step_size
        self.engine = BacktestEngine(config)
        
    def optimize_parameters(self, df_train: pd.DataFrame, 
                           strategy_generator: Callable,
                           param_grid: Dict[str, List]) -> Dict:
        """Parametrlarni optimize qilish"""
        
        best_sharpe = -np.inf
        best_params = None
        
        # Generate all parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        from itertools import product
        param_combinations = list(product(*param_values))
        
        logger.info(f"Testing {len(param_combinations)} parameter combinations")
        
        for params in param_combinations:
            param_dict = dict(zip(param_names, params))
            
            # Create strategy with these parameters
            strategy = strategy_generator(param_dict)
            
            # Run backtest
            result = self.engine.run(df_train, strategy)
            
            # Check if better
            if result.sharpe_ratio > best_sharpe:
                best_sharpe = result.sharpe_ratio
                best_params = param_dict
                
        logger.info(f"Best parameters: {best_params} (Sharpe: {best_sharpe:.2f})")
        
        return best_params
        
    def walk_forward(self, df: pd.DataFrame,
                    strategy_generator: Callable,
                    param_grid: Dict[str, List]) -> Dict[str, Any]:
        """Walk-forward optimization"""
        
        results = []
        optimal_params_history = []
        
        start_idx = 0
        
        while start_idx + self.training_window + self.testing_window <= len(df):
            # Training period
            train_end_idx = start_idx + self.training_window
            df_train = df.iloc[start_idx:train_end_idx]
            
            # Optimize on training data
            logger.info(f"\nOptimizing on training period: {df_train.iloc[0]['timestamp']} to {df_train.iloc[-1]['timestamp']}")
            best_params = self.optimize_parameters(df_train, strategy_generator, param_grid)
            optimal_params_history.append(best_params)
            
            # Testing period
            test_end_idx = train_end_idx + self.testing_window
            df_test = df.iloc[train_end_idx:test_end_idx]
            
            # Test with optimized parameters
            logger.info(f"Testing on period: {df_test.iloc[0]['timestamp']} to {df_test.iloc[-1]['timestamp']}")
            strategy = strategy_generator(best_params)
            result = self.engine.run(df_test, strategy)
            results.append(result)
            
            # Move window forward
            start_idx += self.step_size
            
        # Aggregate results
        aggregate_result = self._aggregate_results(results)
        
        return {
            'aggregate_result': aggregate_result,
            'individual_results': results,
            'optimal_params_history': optimal_params_history
        }
        
    def _aggregate_results(self, results: List[BacktestResult]) -> Dict:
        """Natijalarni agregat qilish"""
        
        all_trades = []
        for r in results:
            all_trades.extend(r.trades)
            
        # Calculate aggregate metrics
        total_return = np.prod([1 + r.total_return for r in results]) - 1
        avg_sharpe = np.mean([r.sharpe_ratio for r in results])
        avg_win_rate = np.mean([r.win_rate for r in results])
        
        return {
            'total_return': total_return,
            'average_sharpe': avg_sharpe,
            'average_win_rate': avg_win_rate,
            'total_trades': len(all_trades),
            'num_periods': len(results)
        }


# ============================================================================
# Monte Carlo Simulation
# ============================================================================

class MonteCarloSimulator:
    """Monte Carlo simulation for strategy robustness"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.engine = BacktestEngine(config)
        
    def simulate_random_entry(self, df: pd.DataFrame, 
                             strategy: Callable,
                             num_simulations: int = 1000,
                             entry_randomness: float = 0.1) -> Dict:
        """Random entry timing simulation"""
        
        results = []
        
        logger.info(f"Running {num_simulations} Monte Carlo simulations")
        
        for sim in range(num_simulations):
            # Create randomized dataset
            df_sim = df.copy()
            
            # Add random noise to entry points
            np.random.seed(sim)
            random_shift = np.random.randint(-int(entry_randomness * len(df)), 
                                            int(entry_randomness * len(df)))
            
            # Shift the data
            if random_shift != 0:
                df_sim = df_sim.iloc[abs(random_shift):] if random_shift > 0 else df_sim
                
            # Run backtest
            result = self.engine.run(df_sim, strategy)
            results.append(result)
            
            if (sim + 1) % 100 == 0:
                logger.info(f"Completed {sim + 1}/{num_simulations} simulations")
                
        return self._analyze_simulations(results)
        
    def simulate_price_paths(self, df: pd.DataFrame,
                            strategy: Callable,
                            num_simulations: int = 1000,
                            volatility_multiplier: float = 1.0) -> Dict:
        """Price path simulation using GBM"""
        
        results = []
        
        # Calculate historical returns
        returns = df['close'].pct_change().dropna()
        mu = returns.mean()
        sigma = returns.std() * volatility_multiplier
        
        logger.info(f"Running {num_simulations} price path simulations (mu={mu:.4f}, sigma={sigma:.4f})")
        
        for sim in range(num_simulations):
            np.random.seed(sim)
            
            # Generate random price path
            random_returns = np.random.normal(mu, sigma, len(df))
            simulated_prices = df['close'].iloc[0] * np.exp(np.cumsum(random_returns))
            
            # Create simulated dataframe
            df_sim = df.copy()
            df_sim['close'] = simulated_prices
            
            # Run backtest
            result = self.engine.run(df_sim, strategy)
            results.append(result)
            
            if (sim + 1) % 100 == 0:
                logger.info(f"Completed {sim + 1}/{num_simulations} simulations")
                
        return self._analyze_simulations(results)
        
    def _analyze_simulations(self, results: List[BacktestResult]) -> Dict:
        """Simulation natijalarini tahlil qilish"""
        
        returns = [r.total_return for r in results]
        sharpes = [r.sharpe_ratio for r in results]
        max_dds = [r.max_drawdown for r in results]
        win_rates = [r.win_rate for r in results]
        
        # Calculate statistics
        analysis = {
            'mean_return': np.mean(returns),
            'median_return': np.median(returns),
            'std_return': np.std(returns),
            'min_return': np.min(returns),
            'max_return': np.max(returns),
            'percentile_5': np.percentile(returns, 5),
            'percentile_95': np.percentile(returns, 95),
            
            'mean_sharpe': np.mean(sharpes),
            'median_sharpe': np.median(sharpes),
            
            'mean_max_dd': np.mean(max_dds),
            'worst_max_dd': np.max(max_dds),
            
            'mean_win_rate': np.mean(win_rates),
            
            'probability_of_profit': len([r for r in returns if r > 0]) / len(returns),
            'num_simulations': len(results)
        }
        
        logger.info(f"\nMonte Carlo Results:")
        logger.info(f"Mean Return: {analysis['mean_return']*100:.2f}%")
        logger.info(f"Probability of Profit: {analysis['probability_of_profit']*100:.2f}%")
        logger.info(f"5th Percentile Return: {analysis['percentile_5']*100:.2f}%")
        logger.info(f"95th Percentile Return: {analysis['percentile_95']*100:.2f}%")
        
        return analysis


# ============================================================================
# Market Regime Analyzer
# ============================================================================

class MarketRegimeAnalyzer:
    """Turli market rejimlarda performans tahlili"""
    
    @staticmethod
    def detect_regime(df: pd.DataFrame, window: int = 30) -> pd.Series:
        """Market rejimini aniqlash"""
        
        regimes = []
        
        for i in range(window, len(df)):
            window_data = df.iloc[i-window:i]
            
            # Calculate metrics
            returns = window_data['close'].pct_change()
            avg_return = returns.mean()
            volatility = returns.std()
            
            # Trend detection (using simple slope)
            x = np.arange(window)
            y = window_data['close'].values
            slope = np.polyfit(x, y, 1)[0]
            
            # Classify regime
            if avg_return > 0.001 and slope > 0:
                regime = MarketRegime.BULL
            elif avg_return < -0.001 and slope < 0:
                regime = MarketRegime.BEAR
            elif volatility > returns.std() * 1.5:
                regime = MarketRegime.HIGH_VOLATILITY
            elif volatility < returns.std() * 0.5:
                regime = MarketRegime.LOW_VOLATILITY
            else:
                regime = MarketRegime.SIDEWAYS
                
            regimes.append(regime)
            
        # Pad beginning
        regimes = [MarketRegime.SIDEWAYS] * window + regimes
        
        return pd.Series(regimes, index=df.index)
        
    def analyze_by_regime(self, df: pd.DataFrame, 
                         backtest_result: BacktestResult) -> Dict[MarketRegime, Dict]:
        """Rejimlar bo'yicha tahlil"""
        
        # Detect regimes
        df_with_regime = df.copy()
        df_with_regime['regime'] = self.detect_regime(df)
        
        # Group trades by regime
        regime_trades = defaultdict(list)
        
        for trade in backtest_result.trades:
            # Find regime at trade entry
            trade_regime = df_with_regime[df_with_regime['timestamp'] == trade.entry_time]['regime'].iloc[0]
            regime_trades[trade_regime].append(trade)
            
        # Calculate metrics for each regime
        regime_analysis = {}
        
        for regime, trades in regime_trades.items():
            if not trades:
                continue
                
            wins = [t for t in trades if t.pnl > 0]
            losses = [t for t in trades if t.pnl < 0]
            
            regime_analysis[regime] = {
                'total_trades': len(trades),
                'win_rate': len(wins) / len(trades) if trades else 0,
                'avg_pnl': np.mean([t.pnl for t in trades]),
                'total_pnl': sum([t.pnl for t in trades]),
                'avg_win': np.mean([t.pnl for t in wins]) if wins else 0,
                'avg_loss': np.mean([t.pnl for t in losses]) if losses else 0
            }
            
        return regime_analysis


if __name__ == "__main__":
    logger.info("Advanced Backtesting moduli yuklandi!")
    logger.info("Walk-Forward Optimization, Monte Carlo, Regime Analysis tayyor")
