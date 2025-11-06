"""
Advanced Backtesting System

Bu modul comprehensive backtesting tizimini ta'minlaydi. Unda historical data analysis,
performance metrics, risk metrics, va advanced testing metodlari mavjud.

Asosiy xususiyatlar:
- Historical data analysis
- Multiple timeframes support
- Commission va slippage modeling
- Spread analysis
- Performance va risk metrics
- Drawdown analysis
- Walk-forward analysis
- Monte Carlo simulation
- Stress testing
- Out-of-sample testing
- Cross-validation
- Strategy ranking
"""

import numpy as np
import pandas as pd
import warnings
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import json
import asyncio

# Technical analysis (with fallbacks for missing libraries)
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    warnings.warn("TA-Lib not available, using alternative indicators")
    
    # Create dummy talib functions for compatibility
    class talib:
        @staticmethod
        def SMA(*args, **kwargs):
            return np.array([1.0] * len(args[0]))
        
        @staticmethod
        def RSI(*args, **kwargs):
            return np.array([50.0] * len(args[0]))
        
        @staticmethod
        def BBANDS(*args, **kwargs):
            n = len(args[0])
            return np.array([1.0] * n), np.array([1.0] * n), np.array([1.0] * n)
        
        @staticmethod
        def MACD(*args, **kwargs):
            n = len(args[0])
            return np.array([0.0] * n), np.array([0.0] * n), np.array([0.0] * n)

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    warnings.warn("SciPy not available, basic stats only")
    
    class stats:
        @staticmethod
        def linregress(x, y):
            return 0, 0, 0, 0, 0  # slope, intercept, r_value, p_value, std_err

try:
    import matplotlib.pyplot as plt
    MPL_AVAILABLE = True
except ImportError:
    MPL_AVAILABLE = False
    warnings.warn("Matplotlib not available, plotting disabled")

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False
    warnings.warn("Seaborn not available")

# Supabase integration
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    warnings.warn("Supabase client topilmadi, database integratsiyasi yo'qoladi")

@dataclass
class MarketData:
    """Market data structure"""
    timestamp: pd.Timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str = "EURUSD"
    timeframe: str = "1h"

@dataclass
class Trade:
    """Individual trade record"""
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    quantity: float
    side: str  # 'long' or 'short'
    pnl: float
    pnl_pct: float
    commission: float
    slippage: float
    duration: timedelta
    max_adverse_excursion: float = 0.0
    max_favorable_excursion: float = 0.0

@dataclass
class BacktestConfig:
    """Backtest configuration"""
    initial_capital: float = 10000.0
    commission: float = 0.0001  # 1 pip for forex
    slippage: float = 0.00005   # 0.5 pip
    spread: float = 0.0002      # 2 pips
    max_position_size: float = 1.0
    risk_per_trade: float = 0.02  # 2% risk per trade
    max_drawdown_limit: float = 0.1  # 10% max drawdown
    timezone: str = "UTC"
    benchmark_symbol: str = "EURUSD"
    risk_free_rate: float = 0.02  # 2% annual

@dataclass
class BacktestResult:
    """Comprehensive backtest results"""
    # Basic metrics
    total_return: float
    annual_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    
    # Risk metrics
    max_drawdown: float
    max_drawdown_duration: int  # days
    var_95: float  # Value at Risk 95%
    cvar_95: float  # Conditional VaR 95%
    
    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    largest_win: float
    largest_loss: float
    
    # Advanced metrics
    skewness: float
    kurtosis: float
    beta: Optional[float] = None
    alpha: Optional[float] = None
    information_ratio: Optional[float] = None
    
    # Additional data
    trades: List[Trade] = field(default_factory=list)
    equity_curve: pd.Series = field(default_factory=pd.Series)
    drawdown_series: pd.Series = field(default_factory=pd.Series)
    returns_series: pd.Series = field(default_factory=pd.Series)
    
    # Performance attribution
    benchmark_returns: Optional[pd.Series] = None
    excess_returns: Optional[pd.Series] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'total_return': self.total_return,
            'annual_return': self.annual_return,
            'volatility': self.volatility,
            'sharpe_ratio': self.sharpe_ratio,
            'sortino_ratio': self.sortino_ratio,
            'calmar_ratio': self.calmar_ratio,
            'max_drawdown': self.max_drawdown,
            'max_drawdown_duration': self.max_drawdown_duration,
            'var_95': self.var_95,
            'cvar_95': self.cvar_95,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'profit_factor': self.profit_factor,
            'largest_win': self.largest_win,
            'largest_loss': self.largest_loss,
            'skewness': self.skewness,
            'kurtosis': self.kurtosis,
            'beta': self.beta,
            'alpha': self.alpha,
            'information_ratio': self.information_ratio
        }

class PerformanceAnalyzer:
    """Performance metrics calculator"""
    
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        excess_returns = returns.mean() * 252 - risk_free_rate
        return excess_returns / (returns.std() * np.sqrt(252))
    
    @staticmethod
    def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio (downside deviation)"""
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns.mean() * 252 - risk_free_rate
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0:
            return float('inf') if excess_returns > 0 else 0.0
        
        downside_std = downside_returns.std() * np.sqrt(252)
        return excess_returns / downside_std if downside_std > 0 else 0.0
    
    @staticmethod
    def calculate_calmar_ratio(returns: pd.Series, max_drawdown: float) -> float:
        """Calculate Calmar ratio"""
        annual_return = returns.mean() * 252
        return annual_return / abs(max_drawdown) if max_drawdown != 0 else 0.0
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> Tuple[float, int]:
        """Calculate maximum drawdown and duration"""
        if len(equity_curve) == 0:
            return 0.0, 0
        
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve - peak) / peak
        
        max_dd = abs(drawdown.min())
        
        # Calculate drawdown duration
        in_drawdown = drawdown < 0
        drawdown_periods = []
        current_period = 0
        
        for in_dd in in_drawdown:
            if in_dd:
                current_period += 1
            else:
                if current_period > 0:
                    drawdown_periods.append(current_period)
                current_period = 0
        
        max_dd_duration = max(drawdown_periods) if drawdown_periods else 0
        
        return max_dd, max_dd_duration
    
    @staticmethod
    def calculate_var_cvar(returns: pd.Series, confidence_level: float = 0.05) -> Tuple[float, float]:
        """Calculate Value at Risk and Conditional VaR"""
        if len(returns) == 0:
            return 0.0, 0.0
        
        var = np.percentile(returns, confidence_level * 100)
        cvar = returns[returns <= var].mean()
        
        return abs(var), abs(cvar)
    
    @staticmethod
    def calculate_information_ratio(portfolio_returns: pd.Series, 
                                  benchmark_returns: pd.Series) -> float:
        """Calculate Information Ratio"""
        if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
            return 0.0
        
        # Align the series
        min_len = min(len(portfolio_returns), len(benchmark_returns))
        portfolio_aligned = portfolio_returns.tail(min_len)
        benchmark_aligned = benchmark_returns.tail(min_len)
        
        excess_returns = portfolio_aligned - benchmark_aligned
        tracking_error = excess_returns.std() * np.sqrt(252)
        
        if tracking_error == 0:
            return 0.0
        
        return (excess_returns.mean() * 252) / tracking_error

class RiskAnalyzer:
    """Risk analysis components"""
    
    @staticmethod
    def calculate_beta_alpha(portfolio_returns: pd.Series, 
                           benchmark_returns: pd.Series) -> Tuple[Optional[float], Optional[float]]:
        """Calculate beta and alpha"""
        if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
            return None, None
        
        # Align the series
        min_len = min(len(portfolio_returns), len(benchmark_returns))
        portfolio_aligned = portfolio_returns.tail(min_len)
        benchmark_aligned = benchmark_returns.tail(min_len)
        
        # Remove any NaN values
        valid_mask = ~(portfolio_aligned.isna() | benchmark_aligned.isna())
        portfolio_clean = portfolio_aligned[valid_mask]
        benchmark_clean = benchmark_aligned[valid_mask]
        
        if len(portfolio_clean) < 2:
            return None, None
        
        # Calculate beta using linear regression
        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(benchmark_clean, portfolio_clean)
            beta = slope
            alpha = intercept * 252  # Annualized alpha
            return beta, alpha
        except:
            return None, None
    
    @staticmethod
    def stress_test_scenarios() -> List[Dict[str, Any]]:
        """Define stress testing scenarios"""
        return [
            {
                'name': 'High Volatility',
                'description': 'Volatility 3x normal',
                'volatility_multiplier': 3.0
            },
            {
                'name': 'Market Crash',
                'description': 'Sudden 20% drop',
                'trend_shift': -0.20
            },
            {
                'name': 'Bull Market',
                'description': 'Strong uptrend',
                'trend_shift': 0.15
            },
            {
                'name': 'Gap Down Risk',
                'description': 'High gap probability',
                'gap_probability': 0.05
            },
            {
                'name': 'Whipsaw Market',
                'description': 'High frequency reversals',
                'volatility_multiplier': 2.0,
                'trend_shift': 0.0
            }
        ]
    
    @staticmethod
    def apply_stress_scenario(data: pd.DataFrame, scenario: Dict[str, Any]) -> pd.DataFrame:
        """Apply stress scenario to data"""
        stressed_data = data.copy()
        
        # Volatility shock
        if 'volatility_multiplier' in scenario:
            returns = data['close'].pct_change().dropna()
            stressed_returns = returns * scenario['volatility_multiplier']
            stressed_data['close'] = data['close'].iloc[0] * (1 + stressed_returns.cumsum())
            
            # Update OHLC based on new close
            price_range = data['high'] - data['low']
            stressed_data['high'] = stressed_data['close'] + price_range * 0.6
            stressed_data['low'] = stressed_data['close'] - price_range * 0.6
            stressed_data['open'] = stressed_data['close'].shift(1).fillna(stressed_data['close'].iloc[0])
        
        # Trend shift
        if 'trend_shift' in scenario:
            shift_factor = 1 + scenario['trend_shift']
            stressed_data['close'] *= shift_factor
            stressed_data['high'] *= shift_factor
            stressed_data['low'] *= shift_factor
            stressed_data['open'] *= shift_factor
        
        # Gap risk
        if 'gap_probability' in scenario:
            n_gaps = int(len(data) * scenario['gap_probability'])
            gap_indices = np.random.choice(len(data), size=min(n_gaps, len(data)), replace=False)
            
            for idx in gap_indices:
                if idx > 0:
                    gap_size = np.random.uniform(-0.05, 0.05)
                    stressed_data.iloc[idx, stressed_data.columns.get_loc('open')] = \
                        stressed_data.iloc[idx-1, stressed_data.columns.get_loc('close')] * (1 + gap_size)
        
        return stressed_data

class Backtester:
    """Advanced backtesting engine"""
    
    def __init__(self, config: Optional[BacktestConfig] = None):
        self.config = config or BacktestConfig()
        self.performance_analyzer = PerformanceAnalyzer()
        self.risk_analyzer = RiskAnalyzer()
        self.logger = logging.getLogger(__name__)
    
    def run_backtest(self, strategy: Any, data: pd.DataFrame) -> BacktestResult:
        """Run complete backtest"""
        try:
            # Initialize tracking variables
            equity = self.config.initial_capital
            position = 0.0
            entry_price = 0.0
            trades = []
            equity_curve = []
            in_position = False
            position_side = None
            entry_time = None
            
            # Strategy signals simulation (simplified)
            for i, (timestamp, row) in enumerate(data.iterrows()):
                current_price = row['close']
                
                # Get strategy signal (simplified for demo)
                signal = getattr(strategy, 'get_signal', lambda x, y: 0)(data.iloc[:i+1], row)
                
                # Position management
                if not in_position and signal != 0:
                    # Enter position
                    position_size = self._calculate_position_size(equity, current_price)
                    
                    if signal > 0:  # Long
                        entry_price = current_price + self.config.spread
                        position = position_size
                        position_side = 'long'
                    else:  # Short
                        entry_price = current_price - self.config.spread
                        position = -position_size
                        position_side = 'short'
                    
                    in_position = True
                    entry_time = timestamp
                    commission = abs(position) * entry_price * self.config.commission
                    equity -= commission
                
                elif in_position and self._should_exit(signal, current_price, entry_price, position_side):
                    # Exit position
                    if position_side == 'long':
                        exit_price = current_price - self.config.spread
                    else:
                        exit_price = current_price + self.config.spread
                    
                    pnl = position * (exit_price - entry_price)
                    commission = abs(position) * exit_price * self.config.commission
                    slippage = abs(position) * self.config.slippage
                    
                    pnl -= commission + slippage
                    equity += pnl
                    
                    # Create trade record
                    trade = Trade(
                        entry_time=entry_time,
                        exit_time=timestamp,
                        entry_price=entry_price,
                        exit_price=exit_price,
                        quantity=abs(position),
                        side=position_side,
                        pnl=pnl,
                        pnl_pct=pnl / (equity - pnl),
                        commission=commission,
                        slippage=slippage,
                        duration=timestamp - entry_time
                    )
                    trades.append(trade)
                    
                    # Reset position
                    in_position = False
                    position = 0.0
                    position_side = None
                    entry_time = None
                
                # Update equity
                if in_position:
                    current_equity = equity + position * (current_price - entry_price)
                else:
                    current_equity = equity
                
                equity_curve.append({
                    'timestamp': timestamp,
                    'equity': current_equity
                })
            
            # Create DataFrames
            equity_df = pd.DataFrame(equity_curve)
            equity_df.set_index('timestamp', inplace=True)
            returns = equity_df['equity'].pct_change().dropna()
            
            # Calculate performance metrics
            total_return = (equity - self.config.initial_capital) / self.config.initial_capital
            annual_return = returns.mean() * 252
            volatility = returns.std() * np.sqrt(252)
            
            sharpe_ratio = self.performance_analyzer.calculate_sharpe_ratio(returns, self.config.risk_free_rate)
            sortino_ratio = self.performance_analyzer.calculate_sortino_ratio(returns, self.config.risk_free_rate)
            max_drawdown, max_dd_duration = self.performance_analyzer.calculate_max_drawdown(equity_df['equity'])
            calmar_ratio = self.performance_analyzer.calculate_calmar_ratio(returns, max_drawdown)
            
            var_95, cvar_95 = self.performance_analyzer.calculate_var_cvar(returns, 0.05)
            
            # Trade statistics
            winning_trades = [t for t in trades if t.pnl > 0]
            losing_trades = [t for t in trades if t.pnl <= 0]
            
            total_trades = len(trades)
            win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
            avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
            profit_factor = abs(avg_win * len(winning_trades) / (avg_loss * len(losing_trades))) if losing_trades and avg_loss != 0 else float('inf')
            
            largest_win = max([t.pnl for t in trades]) if trades else 0
            largest_loss = min([t.pnl for t in trades]) if trades else 0
            
            # Risk metrics
            skewness = returns.skew() if len(returns) > 0 else 0
            kurtosis = returns.kurtosis() if len(returns) > 0 else 0
            
            # Create result
            result = BacktestResult(
                total_return=total_return,
                annual_return=annual_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                calmar_ratio=calmar_ratio,
                max_drawdown=max_drawdown,
                max_drawdown_duration=max_dd_duration,
                var_95=var_95,
                cvar_95=cvar_95,
                total_trades=total_trades,
                winning_trades=len(winning_trades),
                losing_trades=len(losing_trades),
                win_rate=win_rate,
                avg_win=avg_win,
                avg_loss=avg_loss,
                profit_factor=profit_factor,
                largest_win=largest_win,
                largest_loss=largest_loss,
                skewness=skewness,
                kurtosis=kurtosis,
                trades=trades,
                equity_curve=equity_df['equity'],
                drawdown_series=equity_df['equity'] / equity_df['equity'].expanding().max() - 1,
                returns_series=returns
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Backtest xatosi: {e}")
            raise
    
    def _calculate_position_size(self, equity: float, price: float) -> float:
        """Calculate position size based on risk management"""
        risk_amount = equity * self.config.risk_per_trade
        position_value = risk_amount / self.config.max_drawdown_limit
        position_size = position_value / price
        
        # Apply max position size limit
        max_position_value = equity * self.config.max_position_size
        max_position_size = max_position_value / price
        
        return min(position_size, max_position_size)
    
    def _should_exit(self, signal: int, current_price: float, entry_price: float, side: str) -> bool:
        """Determine if position should be exited"""
        # Simple exit logic - in real implementation, this would be more sophisticated
        if side == 'long':
            return signal < 0 or (current_price - entry_price) / entry_price < -self.config.max_drawdown_limit
        else:
            return signal > 0 or (entry_price - current_price) / entry_price < -self.config.max_drawdown_limit
    
    def walk_forward_analysis(self, strategy: Any, data: pd.DataFrame, 
                            window_size: int = 252, step_size: int = 21) -> Dict[str, Any]:
        """Walk-forward analysis"""
        results = []
        
        for i in range(0, len(data) - window_size, step_size):
            # Train window
            train_data = data.iloc[i:i+window_size]
            test_data = data.iloc[i+window_size:i+window_size+step_size] if i+window_size+step_size <= len(data) else data.iloc[i+window_size:]
            
            if len(test_data) == 0:
                continue
            
            try:
                train_result = self.run_backtest(strategy, train_data)
                test_result = self.run_backtest(strategy, test_data)
                
                results.append({
                    'train_period': f"{train_data.index[0]}_{train_data.index[-1]}",
                    'test_period': f"{test_data.index[0]}_{test_data.index[-1]}",
                    'train_sharpe': train_result.sharpe_ratio,
                    'test_sharpe': test_result.sharpe_ratio,
                    'train_return': train_result.total_return,
                    'test_return': test_result.total_return
                })
            except Exception as e:
                self.logger.warning(f"Walk-forward window {i} failed: {e}")
        
        if not results:
            return {'error': 'No valid walk-forward windows'}
        
        # Analysis
        test_sharpes = [r['test_sharpe'] for r in results]
        test_returns = [r['test_return'] for r in results]
        
        analysis = {
            'windows_analyzed': len(results),
            'avg_test_sharpe': np.mean(test_sharpes),
            'std_test_sharpe': np.std(test_sharpes),
            'avg_test_return': np.mean(test_returns),
            'sharpe_stability': 1 / (1 + np.std(test_sharpes)) if test_sharpes else 0,
            'return_stability': 1 / (1 + np.std(test_returns)) if test_returns else 0,
            'window_results': results
        }
        
        return analysis
    
    def monte_carlo_simulation(self, strategy: Any, data: pd.DataFrame, 
                             num_simulations: int = 1000) -> Dict[str, Any]:
        """Monte Carlo simulation"""
        simulation_results = []
        
        for i in range(num_simulations):
            try:
                # Bootstrap sampling
                sampled_data = data.sample(n=len(data), replace=True)
                result = self.run_backtest(strategy, sampled_data)
                
                simulation_results.append({
                    'total_return': result.total_return,
                    'sharpe_ratio': result.sharpe_ratio,
                    'max_drawdown': result.max_drawdown,
                    'total_trades': result.total_trades
                })
            except Exception as e:
                self.logger.warning(f"Simulation {i} failed: {e}")
        
        if not simulation_results:
            return {'error': 'No successful simulations'}
        
        returns = [r['total_return'] for r in simulation_results]
        sharpes = [r['sharpe_ratio'] for r in simulation_results]
        
        analysis = {
            'num_simulations': len(simulation_results),
            'mean_return': np.mean(returns),
            'std_return': np.std(returns),
            'percentile_5': np.percentile(returns, 5),
            'percentile_25': np.percentile(returns, 25),
            'percentile_50': np.percentile(returns, 50),
            'percentile_75': np.percentile(returns, 75),
            'percentile_95': np.percentile(returns, 95),
            'var_5': abs(np.percentile(returns, 5)),
            'prob_profit': len([r for r in returns if r > 0]) / len(returns),
            'mean_sharpe': np.mean(sharpes),
            'sharpe_prob_positive': len([s for s in sharpes if s > 0]) / len(sharpes)
        }
        
        return analysis
    
    def stress_test(self, strategy: Any, data: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive stress testing"""
        scenarios = self.risk_analyzer.stress_test_scenarios()
        stress_results = []
        
        for scenario in scenarios:
            try:
                # Apply stress scenario
                stressed_data = self.risk_analyzer.apply_stress_scenario(data, scenario)
                result = self.run_backtest(strategy, stressed_data)
                
                stress_results.append({
                    'scenario': scenario['name'],
                    'total_return': result.total_return,
                    'sharpe_ratio': result.sharpe_ratio,
                    'max_drawdown': result.max_drawdown,
                    'total_trades': result.total_trades,
                    'win_rate': result.win_rate
                })
            except Exception as e:
                self.logger.warning(f"Stress test {scenario['name']} failed: {e}")
                stress_results.append({
                    'scenario': scenario['name'],
                    'error': str(e)
                })
        
        # Normal condition test
        try:
            normal_result = self.run_backtest(strategy, data)
            normal_performance = {
                'total_return': normal_result.total_return,
                'sharpe_ratio': normal_result.sharpe_ratio,
                'max_drawdown': normal_result.max_drawdown
            }
        except:
            normal_performance = {'error': 'Normal test failed'}
        
        return {
            'normal_performance': normal_performance,
            'stress_results': stress_results,
            'stress_summary': self._summarize_stress_results(stress_results)
        }
    
    def _summarize_stress_results(self, stress_results: List[Dict]) -> Dict[str, Any]:
        """Summarize stress test results"""
        successful_results = [r for r in stress_results if 'error' not in r]
        
        if not successful_results:
            return {'error': 'No successful stress tests'}
        
        returns = [r.get('total_return', 0) for r in successful_results]
        sharpes = [r.get('sharpe_ratio', 0) for r in successful_results]
        drawdowns = [r.get('max_drawdown', 0) for r in successful_results]
        
        return {
            'success_rate': len(successful_results) / len(stress_results),
            'worst_return': min(returns),
            'best_return': max(returns),
            'avg_stress_return': np.mean(returns),
            'avg_stress_sharpe': np.mean(sharpes),
            'worst_drawdown': max(drawdowns),
            'robustness_score': 1 / (1 + np.std(returns)) if returns else 0
        }
    
    def cross_validation(self, strategy: Any, data: pd.DataFrame, n_folds: int = 5) -> Dict[str, Any]:
        """Cross-validation testing"""
        fold_size = len(data) // n_folds
        cv_results = []
        
        for i in range(n_folds):
            test_start = i * fold_size
            test_end = (i + 1) * fold_size if i < n_folds - 1 else len(data)
            
            test_data = data.iloc[test_start:test_end]
            
            if len(test_data) == 0:
                continue
            
            try:
                result = self.run_backtest(strategy, test_data)
                cv_results.append({
                    'fold': i + 1,
                    'total_return': result.total_return,
                    'sharpe_ratio': result.sharpe_ratio,
                    'max_drawdown': result.max_drawdown,
                    'total_trades': result.total_trades
                })
            except Exception as e:
                self.logger.warning(f"CV fold {i + 1} failed: {e}")
        
        if not cv_results:
            return {'error': 'No successful CV folds'}
        
        returns = [r['total_return'] for r in cv_results]
        sharpes = [r['sharpe_ratio'] for r in cv_results]
        
        return {
            'n_folds': n_folds,
            'successful_folds': len(cv_results),
            'avg_return': np.mean(returns),
            'std_return': np.std(returns),
            'avg_sharpe': np.mean(sharpes),
            'sharpe_stability': np.mean(sharpes) / (np.std(sharpes) + 1e-8),
            'cv_score': np.mean(sharpes) / (1 + np.std(sharpes)),
            'fold_results': cv_results
        }
    
    def benchmark_comparison(self, strategy: Any, data: pd.DataFrame, 
                           benchmark_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Compare strategy performance against benchmark"""
        try:
            # Get strategy results
            strategy_result = self.run_backtest(strategy, data)
            
            # Create or use benchmark data
            if benchmark_data is None:
                # Simple buy-and-hold benchmark
                benchmark_data = data.copy()
            
            # Calculate benchmark returns
            initial_capital = self.config.initial_capital
            benchmark_position = initial_capital / data['close'].iloc[0]
            benchmark_equity = benchmark_position * data['close']
            benchmark_returns = benchmark_equity.pct_change().dropna()
            
            # Calculate benchmark metrics
            benchmark_total_return = (benchmark_equity.iloc[-1] - initial_capital) / initial_capital
            benchmark_sharpe = self.performance_analyzer.calculate_sharpe_ratio(benchmark_returns, self.config.risk_free_rate)
            benchmark_volatility = benchmark_returns.std() * np.sqrt(252)
            
            # Calculate beta and alpha
            beta, alpha = self.risk_analyzer.calculate_beta_alpha(
                strategy_result.returns_series, benchmark_returns
            )
            
            # Information ratio
            information_ratio = self.performance_analyzer.calculate_information_ratio(
                strategy_result.returns_series, benchmark_returns
            )
            
            # Outperformance
            excess_return = strategy_result.total_return - benchmark_total_return
            excess_sharpe = strategy_result.sharpe_ratio - benchmark_sharpe
            
            return {
                'strategy': {
                    'total_return': strategy_result.total_return,
                    'sharpe_ratio': strategy_result.sharpe_ratio,
                    'volatility': strategy_result.volatility,
                    'max_drawdown': strategy_result.max_drawdown
                },
                'benchmark': {
                    'total_return': benchmark_total_return,
                    'sharpe_ratio': benchmark_sharpe,
                    'volatility': benchmark_volatility
                },
                'outperformance': {
                    'excess_return': excess_return,
                    'excess_sharpe': excess_sharpe,
                    'beta': beta,
                    'alpha': alpha,
                    'information_ratio': information_ratio
                }
            }
            
        except Exception as e:
            self.logger.error(f"Benchmark comparison failed: {e}")
            return {'error': str(e)}
    
    def generate_performance_report(self, result: BacktestResult, 
                                  output_file: Optional[str] = None) -> str:
        """Generate comprehensive performance report"""
        report = f"""
=== STRATEGY PERFORMANCE REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== BASIC PERFORMANCE METRICS ===
Total Return: {result.total_return:.2%}
Annual Return: {result.annual_return:.2%}
Volatility: {result.volatility:.2%}
Sharpe Ratio: {result.sharpe_ratio:.3f}
Sortino Ratio: {result.sortino_ratio:.3f}
Calmar Ratio: {result.calmar_ratio:.3f}

=== RISK METRICS ===
Maximum Drawdown: {result.max_drawdown:.2%}
Max Drawdown Duration: {result.max_drawdown_duration} days
Value at Risk (95%): {result.var_95:.2%}
Conditional VaR (95%): {result.cvar_95:.2%}

=== TRADE STATISTICS ===
Total Trades: {result.total_trades}
Winning Trades: {result.winning_trades}
Losing Trades: {result.losing_trades}
Win Rate: {result.win_rate:.2%}
Average Win: {result.avg_win:.2f}
Average Loss: {result.avg_loss:.2f}
Profit Factor: {result.profit_factor:.2f}
Largest Win: {result.largest_win:.2f}
Largest Loss: {result.largest_loss:.2f}

=== DISTRIBUTION METRICS ===
Skewness: {result.skewness:.3f}
Kurtosis: {result.kurtosis:.3f}

=== ADDITIONAL METRICS ===
Beta: {result.beta:.3f if result.beta else 'N/A'}
Alpha: {result.alpha:.3f if result.alpha else 'N/A'}
Information Ratio: {result.information_ratio:.3f if result.information_ratio else 'N/A'}

=== SUMMARY ===
Strategy shows {'positive' if result.total_return > 0 else 'negative'} performance
with {'high' if result.sharpe_ratio > 1.5 else 'moderate' if result.sharpe_ratio > 0.5 else 'low'} risk-adjusted returns.
Win rate of {result.win_rate:.1%} indicates {'good' if result.win_rate > 0.5 else 'poor'} trade success.
Maximum drawdown of {result.max_drawdown:.1%} is {'acceptable' if result.max_drawdown < 0.15 else 'high'}.

"""
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            self.logger.info(f"Performance report saved to {output_file}")
        
        return report

# Mock strategy for testing
class MockStrategy:
    """Mock strategy for testing purposes"""
    
    def __init__(self, signal_frequency: float = 0.1):
        self.signal_frequency = signal_frequency
    
    def get_signal(self, data: pd.DataFrame, current_row: pd.Series) -> int:
        """Generate trading signals based on simple moving average crossover"""
        if len(data) < 20:  # Need enough data
            return 0
        
        # Simple moving average crossover
        short_ma = data['close'].tail(10).mean()
        long_ma = data['close'].tail(20).mean()
        
        if short_ma > long_ma:
            return 1  # Long signal
        elif short_ma < long_ma:
            return -1  # Short signal
        else:
            return 0  # No signal

# Demo function
async def main():
    """Main demo function"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize backtester
    config = BacktestConfig(
        initial_capital=10000,
        commission=0.0001,
        slippage=0.00005,
        spread=0.0002
    )
    backtester = Backtester(config)
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=1000, freq='H')
    
    # Simulated price data
    price_changes = np.random.normal(0, 0.001, 1000)
    prices = 1.1000 + np.cumsum(price_changes)
    
    data = pd.DataFrame({
        'timestamp': dates,
        'open': prices + np.random.normal(0, 0.0005, 1000),
        'high': prices + np.abs(np.random.normal(0, 0.001, 1000)),
        'low': prices - np.abs(np.random.normal(0, 0.001, 1000)),
        'close': prices,
        'volume': np.random.lognormal(10, 1, 1000)
    })
    data.set_index('timestamp', inplace=True)
    
    # Create mock strategy
    strategy = MockStrategy(signal_frequency=0.05)
    
    print("=== BACKTESTER DEMO ===")
    
    # Run basic backtest
    result = backtester.run_backtest(strategy, data)
    print(f"Total Return: {result.total_return:.2%}")
    print(f"Sharpe Ratio: {result.sharpe_ratio:.3f}")
    print(f"Max Drawdown: {result.max_drawdown:.2%}")
    print(f"Total Trades: {result.total_trades}")
    print(f"Win Rate: {result.win_rate:.2%}")
    
    # Walk-forward analysis
    print("\n=== WALK-FORWARD ANALYSIS ===")
    wf_result = backtester.walk_forward_analysis(strategy, data, window_size=200, step_size=50)
    print(f"Windows analyzed: {wf_result.get('windows_analyzed', 0)}")
    print(f"Average test Sharpe: {wf_result.get('avg_test_sharpe', 0):.3f}")
    print(f"Sharpe stability: {wf_result.get('sharpe_stability', 0):.3f}")
    
    # Monte Carlo simulation
    print("\n=== MONTE CARLO SIMULATION ===")
    mc_result = backtester.monte_carlo_simulation(strategy, data, num_simulations=100)
    print(f"Simulations completed: {mc_result.get('num_simulations', 0)}")
    print(f"Mean return: {mc_result.get('mean_return', 0):.2%}")
    print(f"95% VaR: {mc_result.get('var_5', 0):.2%}")
    print(f"Probability of profit: {mc_result.get('prob_profit', 0):.2%}")
    
    # Stress testing
    print("\n=== STRESS TESTING ===")
    stress_result = backtester.stress_test(strategy, data)
    print(f"Scenarios tested: {len(stress_result.get('stress_results', []))}")
    if 'stress_summary' in stress_result:
        summary = stress_result['stress_summary']
        print(f"Success rate: {summary.get('success_rate', 0):.2%}")
        print(f"Worst return: {summary.get('worst_return', 0):.2%}")
        print(f"Robustness score: {summary.get('robustness_score', 0):.3f}")
    
    # Generate report
    print("\n=== GENERATING REPORT ===")
    report = backtester.generate_performance_report(result)
    print("Performance report generated successfully")
    
    print("\n=== BACKTESTER DEMO COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(main())