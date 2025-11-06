"""
Advanced Backtesting Dashboard UI Backend
==========================================

Interaktiv backtesting dashboard uchun backend API.
Grafik vizualizatsiya, parametr optimizatsiyasi, walk-forward testing.

Features:
- Interaktiv backtesting UI
- Parametr optimizatsiya
- Walk-forward testing
- Monte Carlo simulation
- Equity curve vizualizatsiya
- Drawdown analysis
- Trade distribution
- Performance metrics
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
import json
from enum import Enum


class BacktestStatus(Enum):
    """Backtest status enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OptimizationMethod(Enum):
    """Optimization method enum"""
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN = "bayesian"
    GENETIC = "genetic"


@dataclass
class BacktestConfig:
    """Backtest configuration"""
    strategy_name: str
    symbol: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    parameters: Dict[str, Any]
    commission: float = 0.001
    slippage: float = 0.0005
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['start_date'] = self.start_date.isoformat()
        data['end_date'] = self.end_date.isoformat()
        return data


@dataclass
class BacktestResult:
    """Backtest result"""
    backtest_id: str
    config: BacktestConfig
    status: BacktestStatus
    
    # Performance metrics
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    
    # Time series data
    equity_curve: List[Dict[str, Any]]
    drawdown_curve: List[Dict[str, Any]]
    trades: List[Dict[str, Any]]
    
    # Additional metrics
    sortino_ratio: float
    calmar_ratio: float
    recovery_factor: float
    expectancy: float
    
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = {
            'backtest_id': self.backtest_id,
            'config': self.config.to_dict(),
            'status': self.status.value,
            'total_return': self.total_return,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'avg_win': self.avg_win,
            'avg_loss': self.avg_loss,
            'largest_win': self.largest_win,
            'largest_loss': self.largest_loss,
            'equity_curve': self.equity_curve,
            'drawdown_curve': self.drawdown_curve,
            'trades': self.trades,
            'sortino_ratio': self.sortino_ratio,
            'calmar_ratio': self.calmar_ratio,
            'recovery_factor': self.recovery_factor,
            'expectancy': self.expectancy,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message
        }
        return data


@dataclass
class OptimizationResult:
    """Optimization result"""
    optimization_id: str
    config: BacktestConfig
    method: OptimizationMethod
    parameter_space: Dict[str, List[Any]]
    
    # Results
    best_parameters: Dict[str, Any]
    best_result: BacktestResult
    all_results: List[BacktestResult]
    
    # Statistics
    total_iterations: int
    successful_iterations: int
    failed_iterations: int
    
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'optimization_id': self.optimization_id,
            'config': self.config.to_dict(),
            'method': self.method.value,
            'parameter_space': self.parameter_space,
            'best_parameters': self.best_parameters,
            'best_result': self.best_result.to_dict(),
            'all_results': [r.to_dict() for r in self.all_results],
            'total_iterations': self.total_iterations,
            'successful_iterations': self.successful_iterations,
            'failed_iterations': self.failed_iterations,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class BacktestingDashboard:
    """
    Advanced Backtesting Dashboard Backend
    
    Provides comprehensive backtesting and optimization capabilities
    with interactive visualization support.
    """
    
    def __init__(self):
        self.backtests: Dict[str, BacktestResult] = {}
        self.optimizations: Dict[str, OptimizationResult] = {}
        self.active_backtests: Dict[str, asyncio.Task] = {}
    
    async def run_backtest(
        self,
        config: BacktestConfig,
        backtest_id: Optional[str] = None
    ) -> BacktestResult:
        """
        Run backtest with given configuration
        
        Args:
            config: Backtest configuration
            backtest_id: Optional backtest ID
            
        Returns:
            BacktestResult
        """
        if backtest_id is None:
            backtest_id = f"bt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create initial result
        result = BacktestResult(
            backtest_id=backtest_id,
            config=config,
            status=BacktestStatus.RUNNING,
            total_return=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            win_rate=0.0,
            profit_factor=0.0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            avg_win=0.0,
            avg_loss=0.0,
            largest_win=0.0,
            largest_loss=0.0,
            equity_curve=[],
            drawdown_curve=[],
            trades=[],
            sortino_ratio=0.0,
            calmar_ratio=0.0,
            recovery_factor=0.0,
            expectancy=0.0,
            created_at=datetime.now()
        )
        
        self.backtests[backtest_id] = result
        
        try:
            # Simulate backtest execution
            await self._execute_backtest(config, result)
            
            result.status = BacktestStatus.COMPLETED
            result.completed_at = datetime.now()
            
        except Exception as e:
            result.status = BacktestStatus.FAILED
            result.error_message = str(e)
            result.completed_at = datetime.now()
        
        return result
    
    async def _execute_backtest(
        self,
        config: BacktestConfig,
        result: BacktestResult
    ) -> None:
        """Execute backtest logic"""
        # Generate synthetic equity curve
        days = (config.end_date - config.start_date).days
        returns = np.random.normal(0.001, 0.02, days)  # Daily returns
        
        equity = [config.initial_capital]
        dates = [config.start_date + timedelta(days=i) for i in range(days)]
        
        for ret in returns:
            equity.append(equity[-1] * (1 + ret))
        
        # Build equity curve
        result.equity_curve = [
            {'date': d.isoformat(), 'equity': e}
            for d, e in zip(dates, equity)
        ]
        
        # Calculate drawdown
        peak = np.maximum.accumulate(equity)
        drawdown = [(e - p) / p for e, p in zip(equity, peak)]
        
        result.drawdown_curve = [
            {'date': d.isoformat(), 'drawdown': dd}
            for d, dd in zip(dates, drawdown)
        ]
        
        # Generate synthetic trades
        num_trades = np.random.randint(50, 200)
        trades = []
        
        for i in range(num_trades):
            entry_date = config.start_date + timedelta(
                days=np.random.randint(0, days-1)
            )
            exit_date = entry_date + timedelta(
                days=np.random.randint(1, 10)
            )
            
            pnl = np.random.normal(10, 50)
            
            trade = {
                'trade_id': i + 1,
                'entry_date': entry_date.isoformat(),
                'exit_date': exit_date.isoformat(),
                'side': np.random.choice(['long', 'short']),
                'entry_price': np.random.uniform(100, 200),
                'exit_price': np.random.uniform(100, 200),
                'size': np.random.uniform(0.1, 2.0),
                'pnl': pnl,
                'pnl_percent': pnl / 1000,
                'commission': pnl * config.commission,
                'slippage': pnl * config.slippage
            }
            trades.append(trade)
        
        result.trades = trades
        
        # Calculate performance metrics
        final_equity = equity[-1]
        result.total_return = (final_equity - config.initial_capital) / config.initial_capital
        
        # Win rate
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] < 0]
        
        result.total_trades = len(trades)
        result.winning_trades = len(winning_trades)
        result.losing_trades = len(losing_trades)
        result.win_rate = len(winning_trades) / len(trades) if trades else 0
        
        # Profit metrics
        if winning_trades:
            result.avg_win = np.mean([t['pnl'] for t in winning_trades])
            result.largest_win = max([t['pnl'] for t in winning_trades])
        
        if losing_trades:
            result.avg_loss = np.mean([t['pnl'] for t in losing_trades])
            result.largest_loss = min([t['pnl'] for t in losing_trades])
        
        # Profit factor
        total_profit = sum([t['pnl'] for t in winning_trades])
        total_loss = abs(sum([t['pnl'] for t in losing_trades]))
        result.profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        # Sharpe ratio
        daily_returns = np.diff(equity) / equity[:-1]
        result.sharpe_ratio = (
            np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)
            if np.std(daily_returns) > 0 else 0
        )
        
        # Sortino ratio
        downside_returns = daily_returns[daily_returns < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 1e-10
        result.sortino_ratio = (
            np.mean(daily_returns) / downside_std * np.sqrt(252)
        )
        
        # Max drawdown
        result.max_drawdown = min(drawdown)
        
        # Calmar ratio
        result.calmar_ratio = (
            result.total_return / abs(result.max_drawdown)
            if result.max_drawdown != 0 else 0
        )
        
        # Recovery factor
        result.recovery_factor = (
            total_profit / abs(result.max_drawdown * config.initial_capital)
            if result.max_drawdown != 0 else 0
        )
        
        # Expectancy
        result.expectancy = (
            result.win_rate * result.avg_win -
            (1 - result.win_rate) * abs(result.avg_loss)
        )
    
    async def optimize_parameters(
        self,
        config: BacktestConfig,
        parameter_space: Dict[str, List[Any]],
        method: OptimizationMethod = OptimizationMethod.GRID_SEARCH,
        optimization_id: Optional[str] = None
    ) -> OptimizationResult:
        """
        Optimize strategy parameters
        
        Args:
            config: Base backtest configuration
            parameter_space: Parameter ranges to optimize
            method: Optimization method
            optimization_id: Optional optimization ID
            
        Returns:
            OptimizationResult
        """
        if optimization_id is None:
            optimization_id = f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        all_results = []
        
        if method == OptimizationMethod.GRID_SEARCH:
            # Grid search
            param_combinations = self._generate_grid_combinations(parameter_space)
            
            for params in param_combinations:
                test_config = BacktestConfig(
                    strategy_name=config.strategy_name,
                    symbol=config.symbol,
                    timeframe=config.timeframe,
                    start_date=config.start_date,
                    end_date=config.end_date,
                    initial_capital=config.initial_capital,
                    parameters=params,
                    commission=config.commission,
                    slippage=config.slippage
                )
                
                result = await self.run_backtest(test_config)
                all_results.append(result)
        
        elif method == OptimizationMethod.RANDOM_SEARCH:
            # Random search
            num_iterations = 50
            
            for i in range(num_iterations):
                params = self._sample_random_parameters(parameter_space)
                
                test_config = BacktestConfig(
                    strategy_name=config.strategy_name,
                    symbol=config.symbol,
                    timeframe=config.timeframe,
                    start_date=config.start_date,
                    end_date=config.end_date,
                    initial_capital=config.initial_capital,
                    parameters=params,
                    commission=config.commission,
                    slippage=config.slippage
                )
                
                result = await self.run_backtest(test_config)
                all_results.append(result)
        
        # Find best result
        successful_results = [
            r for r in all_results if r.status == BacktestStatus.COMPLETED
        ]
        
        best_result = max(
            successful_results,
            key=lambda r: r.sharpe_ratio
        ) if successful_results else all_results[0]
        
        # Create optimization result
        optimization_result = OptimizationResult(
            optimization_id=optimization_id,
            config=config,
            method=method,
            parameter_space=parameter_space,
            best_parameters=best_result.config.parameters,
            best_result=best_result,
            all_results=successful_results,
            total_iterations=len(all_results),
            successful_iterations=len(successful_results),
            failed_iterations=len(all_results) - len(successful_results),
            created_at=datetime.now(),
            completed_at=datetime.now()
        )
        
        self.optimizations[optimization_id] = optimization_result
        
        return optimization_result
    
    def _generate_grid_combinations(
        self,
        parameter_space: Dict[str, List[Any]]
    ) -> List[Dict[str, Any]]:
        """Generate all parameter combinations for grid search"""
        keys = list(parameter_space.keys())
        values = list(parameter_space.values())
        
        combinations = []
        
        def generate(index: int, current: Dict):
            if index == len(keys):
                combinations.append(current.copy())
                return
            
            key = keys[index]
            for value in values[index]:
                current[key] = value
                generate(index + 1, current)
        
        generate(0, {})
        
        return combinations
    
    def _sample_random_parameters(
        self,
        parameter_space: Dict[str, List[Any]]
    ) -> Dict[str, Any]:
        """Sample random parameters from parameter space"""
        return {
            key: np.random.choice(values)
            for key, values in parameter_space.items()
        }
    
    async def run_walk_forward_analysis(
        self,
        config: BacktestConfig,
        window_size: int = 90,  # days
        optimization_period: int = 30,  # days
        parameter_space: Dict[str, List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Run walk-forward analysis
        
        Args:
            config: Base configuration
            window_size: Training window size in days
            optimization_period: Out-of-sample test period in days
            parameter_space: Parameters to optimize
            
        Returns:
            Walk-forward analysis results
        """
        results = []
        
        start_date = config.start_date
        end_date = config.end_date
        
        current_date = start_date
        
        while current_date + timedelta(days=window_size + optimization_period) <= end_date:
            # In-sample optimization
            is_start = current_date
            is_end = current_date + timedelta(days=window_size)
            
            is_config = BacktestConfig(
                strategy_name=config.strategy_name,
                symbol=config.symbol,
                timeframe=config.timeframe,
                start_date=is_start,
                end_date=is_end,
                initial_capital=config.initial_capital,
                parameters=config.parameters,
                commission=config.commission,
                slippage=config.slippage
            )
            
            if parameter_space:
                opt_result = await self.optimize_parameters(
                    is_config,
                    parameter_space,
                    method=OptimizationMethod.RANDOM_SEARCH
                )
                best_params = opt_result.best_parameters
            else:
                best_params = config.parameters
            
            # Out-of-sample test
            oos_start = is_end
            oos_end = oos_start + timedelta(days=optimization_period)
            
            oos_config = BacktestConfig(
                strategy_name=config.strategy_name,
                symbol=config.symbol,
                timeframe=config.timeframe,
                start_date=oos_start,
                end_date=oos_end,
                initial_capital=config.initial_capital,
                parameters=best_params,
                commission=config.commission,
                slippage=config.slippage
            )
            
            oos_result = await self.run_backtest(oos_config)
            
            results.append({
                'period': f"{oos_start.date()} - {oos_end.date()}",
                'parameters': best_params,
                'return': oos_result.total_return,
                'sharpe': oos_result.sharpe_ratio,
                'max_drawdown': oos_result.max_drawdown,
                'total_trades': oos_result.total_trades
            })
            
            current_date = oos_end
        
        # Aggregate results
        total_return = sum([r['return'] for r in results])
        avg_sharpe = np.mean([r['sharpe'] for r in results])
        max_drawdown = min([r['max_drawdown'] for r in results])
        
        return {
            'periods': results,
            'summary': {
                'total_return': total_return,
                'avg_sharpe': avg_sharpe,
                'max_drawdown': max_drawdown,
                'num_periods': len(results)
            }
        }
    
    def get_backtest(self, backtest_id: str) -> Optional[BacktestResult]:
        """Get backtest result by ID"""
        return self.backtests.get(backtest_id)
    
    def list_backtests(
        self,
        status: Optional[BacktestStatus] = None,
        limit: int = 50
    ) -> List[BacktestResult]:
        """List backtests with optional filtering"""
        results = list(self.backtests.values())
        
        if status:
            results = [r for r in results if r.status == status]
        
        # Sort by creation date descending
        results.sort(key=lambda r: r.created_at, reverse=True)
        
        return results[:limit]
    
    def get_optimization(self, optimization_id: str) -> Optional[OptimizationResult]:
        """Get optimization result by ID"""
        return self.optimizations.get(optimization_id)
    
    def compare_backtests(
        self,
        backtest_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Compare multiple backtests
        
        Args:
            backtest_ids: List of backtest IDs to compare
            
        Returns:
            Comparison results
        """
        results = [self.backtests[bid] for bid in backtest_ids if bid in self.backtests]
        
        if not results:
            return {'error': 'No valid backtests found'}
        
        comparison = {
            'backtests': [r.to_dict() for r in results],
            'metrics_comparison': {
                'total_return': {r.backtest_id: r.total_return for r in results},
                'sharpe_ratio': {r.backtest_id: r.sharpe_ratio for r in results},
                'max_drawdown': {r.backtest_id: r.max_drawdown for r in results},
                'win_rate': {r.backtest_id: r.win_rate for r in results},
                'profit_factor': {r.backtest_id: r.profit_factor for r in results},
            },
            'best_by_metric': {
                'sharpe_ratio': max(results, key=lambda r: r.sharpe_ratio).backtest_id,
                'total_return': max(results, key=lambda r: r.total_return).backtest_id,
                'win_rate': max(results, key=lambda r: r.win_rate).backtest_id,
            }
        }
        
        return comparison

    async def portfolio_backtest(
        self,
        strategies: List[Dict[str, Any]],  # Each strategy with name, weight, config
        portfolio_config: Dict[str, Any],
        backtest_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run portfolio backtest with multiple strategies
        
        Args:
            strategies: List of strategies with name, weight, and configuration
            portfolio_config: Portfolio configuration (start_date, end_date, etc.)
            backtest_id: Optional backtest ID
            
        Returns:
            Portfolio backtest results
        """
        if backtest_id is None:
            backtest_id = f"pf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Run individual strategy backtests
        strategy_results = {}
        
        for strategy in strategies:
            strategy_name = strategy['name']
            strategy_weight = strategy['weight']
            strategy_config = strategy['config']
            
            # Create backtest config
            config = BacktestConfig(
                strategy_name=strategy_name,
                symbol=strategy_config.get('symbol', 'BTC/USDT'),
                timeframe=strategy_config.get('timeframe', '1h'),
                start_date=datetime.fromisoformat(portfolio_config['start_date']),
                end_date=datetime.fromisoformat(portfolio_config['end_date']),
                initial_capital=portfolio_config.get('initial_capital', 10000),
                parameters=strategy_config.get('parameters', {}),
                commission=strategy_config.get('commission', 0.001),
                slippage=strategy_config.get('slippage', 0.0005)
            )
            
            result = await self.run_backtest(config)
            strategy_results[strategy_name] = {
                'weight': strategy_weight,
                'result': result,
                'equity_curve': result.equity_curve
            }
        
        # Combine portfolio results
        portfolio_equity = self._combine_portfolio_equity(
            strategy_results, 
            portfolio_config.get('rebalancing_frequency', 'daily')
        )
        
        # Calculate portfolio metrics
        portfolio_metrics = self._calculate_portfolio_metrics(
            portfolio_equity, 
            portfolio_config.get('initial_capital', 10000)
        )
        
        # Performance attribution
        attribution = self._calculate_performance_attribution(
            strategy_results, 
            portfolio_metrics['total_return']
        )
        
        return {
            'portfolio_id': backtest_id,
            'portfolio_metrics': portfolio_metrics,
            'strategy_results': strategy_results,
            'equity_curve': portfolio_equity,
            'performance_attribution': attribution,
            'created_at': datetime.now().isoformat()
        }
    
    async def monte_carlo_simulation(
        self,
        base_config: BacktestConfig,
        num_simulations: int = 1000,
        confidence_levels: List[float] = [0.05, 0.95]
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation for backtesting
        
        Args:
            base_config: Base backtest configuration
            num_simulations: Number of simulations to run
            confidence_levels: Confidence levels for statistics
            
        Returns:
            Monte Carlo simulation results
        """
        simulation_results = []
        
        # Run simulations
        for i in range(num_simulations):
            # Create a modified config with slight variations
            sim_config = BacktestConfig(
                strategy_name=base_config.strategy_name,
                symbol=base_config.symbol,
                timeframe=base_config.timeframe,
                start_date=base_config.start_date,
                end_date=base_config.end_date,
                initial_capital=base_config.initial_capital,
                parameters=base_config.parameters.copy(),
                commission=base_config.commission * np.random.uniform(0.5, 1.5),
                slippage=base_config.slippage * np.random.uniform(0.5, 1.5)
            )
            
            # Add small noise to parameters
            for key, value in sim_config.parameters.items():
                if isinstance(value, (int, float)):
                    noise = np.random.normal(0, abs(value) * 0.05)
                    sim_config.parameters[key] = value + noise
            
            try:
                result = await self.run_backtest(sim_config)
                if result.status == BacktestStatus.COMPLETED:
                    simulation_results.append(result)
            except Exception as e:
                print(f"Simulation {i} failed: {e}")
                continue
        
        if not simulation_results:
            return {'error': 'No successful simulations'}
        
        # Calculate statistics
        metrics = {
            'returns': [r.total_return for r in simulation_results],
            'sharpe_ratios': [r.sharpe_ratio for r in simulation_results],
            'max_drawdowns': [r.max_drawdown for r in simulation_results],
            'win_rates': [r.win_rate for r in simulation_results],
            'total_trades': [r.total_trades for r in simulation_results]
        }
        
        # Calculate confidence intervals
        statistics = {}
        for metric_name, values in metrics.items():
            statistics[metric_name] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values),
                'percentiles': {
                    str(level): np.percentile(values, level * 100)
                    for level in confidence_levels
                }
            }
        
        # Risk metrics
        returns_array = np.array(metrics['returns'])
        var_95 = np.percentile(returns_array, 5)  # 95% VaR
        var_99 = np.percentile(returns_array, 1)  # 99% VaR
        
        cvar_95 = np.mean(returns_array[returns_array <= var_95])  # CVaR
        cvar_99 = np.mean(returns_array[returns_array <= var_99])
        
        # Maximum drawdown distribution
        dd_array = np.array(metrics['max_drawdowns'])
        avg_dd = np.mean(dd_array)
        dd_std = np.std(dd_array)
        
        # Sharpe ratio distribution
        sharpe_array = np.array(metrics['sharpe_ratios'])
        prob_positive_sharpe = np.mean(sharpe_array > 0)
        prob_sharpe_gt_1 = np.mean(sharpe_array > 1)
        
        return {
            'simulation_id': f"mc_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'num_simulations': num_simulations,
            'successful_simulations': len(simulation_results),
            'base_config': base_config.to_dict(),
            'statistics': statistics,
            'risk_metrics': {
                'var_95': var_95,
                'var_99': var_99,
                'cvar_95': cvar_95,
                'cvar_99': cvar_99,
                'expected_shortfall_95': cvar_95,
                'max_drawdown_avg': avg_dd,
                'max_drawdown_std': dd_std,
                'prob_positive_sharpe': prob_positive_sharpe,
                'prob_sharpe_gt_1': prob_sharpe_gt_1
            },
            'distribution_summary': {
                'best_return': np.max(returns_array),
                'worst_return': np.min(returns_array),
                'median_return': np.median(returns_array),
                'return_volatility': np.std(returns_array),
                'skewness': float(self._calculate_skewness(returns_array)),
                'kurtosis': float(self._calculate_kurtosis(returns_array))
            },
            'created_at': datetime.now().isoformat()
        }
    
    def _combine_portfolio_equity(
        self, 
        strategy_results: Dict[str, Any], 
        rebalancing_frequency: str
    ) -> List[Dict[str, Any]]:
        """Combine equity curves for portfolio"""
        if not strategy_results:
            return []
        
        # Get common date range
        all_dates = set()
        for strategy_data in strategy_results.values():
            for point in strategy_data['equity_curve']:
                all_dates.add(point['date'])
        
        dates = sorted(list(all_dates))
        
        portfolio_equity = []
        for date in dates:
            portfolio_value = 0
            for strategy_name, strategy_data in strategy_results.items():
                weight = strategy_data['weight']
                
                # Find equity value for this date
                equity_value = 0
                for point in strategy_data['equity_curve']:
                    if point['date'] == date:
                        equity_value = point['equity']
                        break
                
                portfolio_value += equity_value * weight
            
            portfolio_equity.append({
                'date': date,
                'equity': portfolio_value
            })
        
        return portfolio_equity
    
    def _calculate_portfolio_metrics(
        self, 
        equity_curve: List[Dict[str, Any]], 
        initial_capital: float
    ) -> Dict[str, Any]:
        """Calculate portfolio performance metrics"""
        if not equity_curve:
            return {}
        
        equity_values = [point['equity'] for point in equity_curve]
        dates = [point['date'] for point in equity_curve]
        
        # Total return
        final_value = equity_values[-1]
        total_return = (final_value - initial_capital) / initial_capital
        
        # Daily returns
        daily_returns = np.diff(equity_values) / equity_values[:-1]
        
        # Sharpe ratio
        sharpe_ratio = (
            np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)
            if np.std(daily_returns) > 0 else 0
        )
        
        # Sortino ratio
        downside_returns = daily_returns[daily_returns < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 1e-10
        sortino_ratio = (
            np.mean(daily_returns) / downside_std * np.sqrt(252)
        )
        
        # Maximum drawdown
        peak = np.maximum.accumulate(equity_values)
        drawdown = (np.array(equity_values) - peak) / peak
        max_drawdown = np.min(drawdown)
        
        # Calmar ratio
        calmar_ratio = total_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Volatility (annualized)
        volatility = np.std(daily_returns) * np.sqrt(252)
        
        # Win rate (assuming we have trade data)
        # This would need to be calculated based on actual trade results
        
        return {
            'total_return': total_return,
            'annual_return': total_return,  # Simplified
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar_ratio,
            'initial_capital': initial_capital,
            'final_value': final_value
        }
    
    def _calculate_performance_attribution(
        self, 
        strategy_results: Dict[str, Any], 
        total_portfolio_return: float
    ) -> Dict[str, Any]:
        """Calculate performance attribution"""
        attribution = {}
        total_weighted_return = 0
        
        for strategy_name, strategy_data in strategy_results.items():
            weight = strategy_data['weight']
            strategy_return = strategy_data['result'].total_return
            weighted_return = weight * strategy_return
            
            attribution[strategy_name] = {
                'weight': weight,
                'strategy_return': strategy_return,
                'contribution': weighted_return,
                'attribution_pct': (weighted_return / total_portfolio_return * 100 
                                  if total_portfolio_return != 0 else 0)
            }
            
            total_weighted_return += weighted_return
        
        return {
            'strategy_attribution': attribution,
            'total_contribution': total_weighted_return,
            'residual': total_portfolio_return - total_weighted_return
        }
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return np.mean(((data - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0
        return np.mean(((data - mean) / std) ** 4) - 3


def _calculate_skewness(data: np.ndarray) -> float:
    """Calculate skewness"""
    mean = np.mean(data)
    std = np.std(data)
    if std == 0:
        return 0
    return np.mean(((data - mean) / std) ** 3)

def _calculate_kurtosis(data: np.ndarray) -> float:
    """Calculate kurtosis"""
    mean = np.mean(data)
    std = np.std(data)
    if std == 0:
        return 0
    return np.mean(((data - mean) / std) ** 4) - 3

def calculate_comprehensive_metrics(backtest_result: BacktestResult) -> Dict[str, Any]:
    """
    Calculate comprehensive performance metrics for a backtest result
    
    Args:
        backtest_result: BacktestResult object
        
    Returns:
        Dictionary containing comprehensive metrics
    """
    # Extract data
    trades = backtest_result.trades
    equity_curve = backtest_result.equity_curve
    initial_capital = backtest_result.config.initial_capital
    
    if not trades or not equity_curve:
        return {}
    
    equity_values = [point['equity'] for point in equity_curve]
    daily_returns = np.diff(equity_values) / equity_values[:-1]
    
    # Advanced return metrics
    returns = [t['pnl_percent'] for t in trades]
    
    # Ulcer Index (risk metric)
    peak_values = np.maximum.accumulate(equity_values)
    drawdowns = (np.array(equity_values) - peak_values) / peak_values
    ulcer_index = np.sqrt(np.mean(drawdowns ** 2))
    
    # Pain Index
    pain_index = np.mean(np.abs(drawdowns))
    
    # Kelly Criterion (optimal bet sizing)
    if backtest_result.win_rate > 0 and backtest_result.avg_loss != 0:
        win_loss_ratio = abs(backtest_result.avg_win / backtest_result.avg_loss)
        kelly_criterion = backtest_result.win_rate - ((1 - backtest_result.win_rate) / win_loss_ratio)
    else:
        kelly_criterion = 0
    
    # Trade distribution metrics
    winning_trades = [t for t in trades if t['pnl'] > 0]
    losing_trades = [t for t in trades if t['pnl'] < 0]
    
    # Trade frequency
    trading_days = len(equity_curve)
    trades_per_day = len(trades) / trading_days if trading_days > 0 else 0
    
    # Advanced risk metrics
    # Value at Risk (historical)
    var_95 = np.percentile(returns, 5)
    var_99 = np.percentile(returns, 1)
    
    # Conditional Value at Risk
    cvar_95 = np.mean([r for r in returns if r <= var_95])
    cvar_99 = np.mean([r for r in returns if r <= var_99])
    
    # Maximum adverse excursion and maximum favorable excursion
    if trades:
        adverse_excursions = [abs(t['pnl']) for t in losing_trades]
        favorable_excursions = [t['pnl'] for t in winning_trades]
        
        mae = np.mean(adverse_excursions) if adverse_excursions else 0
        mfe = np.mean(favorable_excursions) if favorable_excursions else 0
    else:
        mae = mfe = 0
    
    # Time in market
    time_in_market = 0.65  # Simplified - would need actual position data
    
    # Correlation metrics (would need market data)
    correlation = 0.3  # Placeholder
    
    # Drawdown duration analysis
    drawdown_duration = []
    in_drawdown = False
    current_dd_duration = 0
    
    for dd in drawdowns:
        if dd < -0.01:  # Consider drawdown if > 1%
            if not in_drawdown:
                in_drawdown = True
                current_dd_duration = 1
            else:
                current_dd_duration += 1
        else:
            if in_drawdown:
                drawdown_duration.append(current_dd_duration)
                in_drawdown = False
                current_dd_duration = 0
    
    avg_dd_duration = np.mean(drawdown_duration) if drawdown_duration else 0
    
    # Trade analysis
    trade_sizes = [abs(t['size']) for t in trades]
    avg_trade_size = np.mean(trade_sizes)
    
    # Consecutive wins/losses
    max_consecutive_wins = 0
    max_consecutive_losses = 0
    current_win_streak = 0
    current_loss_streak = 0
    
    for trade in trades:
        if trade['pnl'] > 0:
            current_win_streak += 1
            current_loss_streak = 0
            max_consecutive_wins = max(max_consecutive_wins, current_win_streak)
        elif trade['pnl'] < 0:
            current_loss_streak += 1
            current_win_streak = 0
            max_consecutive_losses = max(max_consecutive_losses, current_loss_streak)
    
    return {
        'advanced_return_metrics': {
            'geometric_return': backtest_result.total_return,
            'arithmetic_return': np.mean(returns) * len(returns) if returns else 0,
            'return_skewness': _calculate_skewness(np.array(returns)),
            'return_kurtosis': _calculate_kurtosis(np.array(returns)),
            'distribution_normality': _test_normality(returns)
        },
        
        'risk_metrics': {
            'ulcer_index': ulcer_index,
            'pain_index': pain_index,
            'var_95': var_95,
            'var_99': var_99,
            'cvar_95': cvar_95,
            'cvar_99': cvar_99,
            'maximum_drawdown': backtest_result.max_drawdown,
            'average_drawdown': np.mean(drawdowns),
            'drawdown_std': np.std(drawdowns),
            'downside_deviation': np.std([r for r in daily_returns if r < 0]),
            'upside_deviation': np.std([r for r in daily_returns if r > 0])
        },
        
        'trade_metrics': {
            'trades_per_day': trades_per_day,
            'avg_trade_size': avg_trade_size,
            'trade_size_std': np.std(trade_sizes),
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'largest_win': backtest_result.largest_win,
            'largest_loss': abs(backtest_result.largest_loss),
            'profit_factor': backtest_result.profit_factor,
            'recovery_factor': backtest_result.recovery_factor,
            'expectancy': backtest_result.expectancy,
            'edge': backtest_result.win_rate * backtest_result.avg_win - 
                   (1 - backtest_result.win_rate) * abs(backtest_result.avg_loss)
        },
        
        'risk_adjusted_metrics': {
            'sharpe_ratio': backtest_result.sharpe_ratio,
            'sortino_ratio': backtest_result.sortino_ratio,
            'calmar_ratio': backtest_result.calmar_ratio,
            'sterling_ratio': backtest_result.total_return / np.std(daily_returns) * np.sqrt(252) / 3,
            'burke_ratio': backtest_result.total_return / np.sqrt(np.sum(drawdowns ** 2)),
            'omega_ratio': _calculate_omega_ratio(daily_returns),
            'kappa_ratio': _calculate_kappa_ratio(daily_returns)
        },
        
        'market_metrics': {
            'correlation': correlation,
            'beta': correlation * np.std(daily_returns) / np.std(_get_market_returns()),
            'alpha': 0,  # Would need to calculate vs benchmark
            'information_ratio': 0,  # Would need benchmark returns
            'tracking_error': np.std(daily_returns) * np.sqrt(252)
        },
        
        'operational_metrics': {
            'time_in_market': time_in_market,
            'avg_drawdown_duration': avg_dd_duration,
            'max_drawdown_duration': max(drawdown_duration) if drawdown_duration else 0,
            'trading_frequency': len(trades) / max(1, (datetime.fromisoformat(equity_curve[-1]['date']) - datetime.fromisoformat(equity_curve[0]['date'])).days),
            'capacity': 'Unknown',  # Would need order book analysis
            'slippage_efficiency': 1 - (np.std(trade_sizes) / np.mean(trade_sizes))
        },
        
        'statistical_metrics': {
            'kelly_criterion': kelly_criterion,
            'optimal_kelly': kelly_criterion / 4,  # Conservative Kelly
            'win_rate': backtest_result.win_rate,
            'hit_rate': backtest_result.win_rate,
            'trade_intensity': len(trades) / len(equity_curve)
        },
        
        'score': _calculate_composite_score(backtest_result, {
            'sharpe': 0.25,
            'calmar': 0.20,
            'sortino': 0.15,
            'profit_factor': 0.15,
            'win_rate': 0.10,
            'max_drawdown': 0.15
        })
    }


def _test_normality(returns: List[float]) -> Dict[str, Any]:
    """Test if returns follow normal distribution"""
    if not returns:
        return {}
    
    returns_array = np.array(returns)
    skewness = float(_calculate_skewness(returns_array))
    kurtosis = float(_calculate_kurtosis(returns_array))
    
    # Simple normality test based on skewness and kurtosis
    # Jarque-Bera statistic approximation
    n = len(returns_array)
    jb_statistic = n * (skewness ** 2 / 6 + kurtosis ** 2 / 24)
    
    is_normal = jb_statistic < 5.99  # Chi-square critical value for alpha=0.05, df=2
    
    return {
        'is_normal': is_normal,
        'jarque_bera_statistic': jb_statistic,
        'skewness': skewness,
        'kurtosis': kurtosis,
        'interpretation': 'Normal' if is_normal else 'Non-normal'
    }


def _calculate_omega_ratio(returns: np.ndarray, threshold: float = 0) -> float:
    """Calculate Omega ratio"""
    gains = returns[returns > threshold] - threshold
    losses = returns[returns <= threshold] - threshold
    
    if len(losses) == 0 or len(gains) == 0:
        return 0
    
    return np.sum(gains) / abs(np.sum(losses))


def _calculate_kappa_ratio(returns: np.ndarray, threshold: float = 0) -> float:
    """Calculate Kappa ratio"""
    excess_returns = returns - threshold
    downside_returns = excess_returns[excess_returns < 0]
    
    if len(downside_returns) == 0:
        return np.inf
    
    return np.mean(excess_returns) / np.sqrt(np.mean(downside_returns ** 2))


def _get_market_returns() -> np.ndarray:
    """Get market benchmark returns (placeholder)"""
    # This would normally fetch actual market data
    return np.random.normal(0.0008, 0.015, 252)  # Daily market returns


def _calculate_composite_score(
    backtest_result: BacktestResult, 
    weights: Dict[str, float]
) -> Dict[str, Any]:
    """Calculate composite performance score"""
    score = 0
    score_components = {}
    
    # Normalize metrics to 0-1 scale
    if 'sharpe' in weights:
        sharpe_score = max(0, min(1, backtest_result.sharpe_ratio / 3))
        score_components['sharpe'] = sharpe_score
        score += weights['sharpe'] * sharpe_score
    
    if 'calmar' in weights:
        calmar_score = max(0, min(1, backtest_result.calmar_ratio / 2))
        score_components['calmar'] = calmar_score
        score += weights['calmar'] * calmar_score
    
    if 'sortino' in weights:
        sortino_score = max(0, min(1, backtest_result.sortino_ratio / 4))
        score_components['sortino'] = sortino_score
        score += weights['sortino'] * sortino_score
    
    if 'profit_factor' in weights:
        pf_score = max(0, min(1, (backtest_result.profit_factor - 1) / 2))
        score_components['profit_factor'] = pf_score
        score += weights['profit_factor'] * pf_score
    
    if 'win_rate' in weights:
        win_score = backtest_result.win_rate
        score_components['win_rate'] = win_score
        score += weights['win_rate'] * win_score
    
    if 'max_drawdown' in weights:
        dd_score = max(0, 1 - abs(backtest_result.max_drawdown))
        score_components['max_drawdown'] = dd_score
        score += weights['max_drawdown'] * dd_score
    
    # Grade
    if score >= 0.8:
        grade = 'A+'
    elif score >= 0.7:
        grade = 'A'
    elif score >= 0.6:
        grade = 'B+'
    elif score >= 0.5:
        grade = 'B'
    elif score >= 0.4:
        grade = 'C+'
    elif score >= 0.3:
        grade = 'C'
    else:
        grade = 'D'
    
    return {
        'composite_score': score,
        'score_components': score_components,
        'grade': grade,
        'interpretation': _get_score_interpretation(score)
    }


def _get_score_interpretation(score: float) -> str:
    """Get interpretation of composite score"""
    if score >= 0.8:
        return "A'joyib strategiya - yuqori xavfni boshqarish va foydali daromad"
    elif score >= 0.7:
        return "Yaxshi strategiya - yaxshi xavf-adashlash balansi"
    elif score >= 0.6:
        return "Qoniqarli strategiya - o'rtacha natijalar"
    elif score >= 0.5:
        return "O'rtacha strategiya - ba'zi muammolar mavjud"
    elif score >= 0.4:
        return "Qoniqarsiz strategiya - yaxshilanish kerak"
    else:
        return "Yomon strategiya - qayta ko'rib chiqish tavsiya etiladi"


# Global instance
backtesting_dashboard = BacktestingDashboard()


async def test_backtesting_dashboard():
    """Test backtesting dashboard"""
    config = BacktestConfig(
        strategy_name="MomentumStrategy",
        symbol="BTC/USDT",
        timeframe="1h",
        start_date=datetime.now() - timedelta(days=365),
        end_date=datetime.now(),
        initial_capital=10000.0,
        parameters={
            'period': 20,
            'threshold': 0.02
        }
    )
    
    # Run backtest
    print("=== Test backtest ===")
    result = await backtesting_dashboard.run_backtest(config)
    print(f"Backtest completed: {result.backtest_id}")
    print(f"Total Return: {result.total_return:.2%}")
    print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
    print(f"Max Drawdown: {result.max_drawdown:.2%}")
    
    # Optimize parameters
    print("\n=== Test parameter optimization ===")
    parameter_space = {
        'period': [10, 20, 30, 50],
        'threshold': [0.01, 0.02, 0.03, 0.05]
    }
    
    opt_result = await backtesting_dashboard.optimize_parameters(
        config,
        parameter_space,
        method=OptimizationMethod.GRID_SEARCH
    )
    
    print(f"Optimization completed: {opt_result.optimization_id}")
    print(f"Best parameters: {opt_result.best_parameters}")
    print(f"Best Sharpe: {opt_result.best_result.sharpe_ratio:.2f}")
    
    # Portfolio backtest
    print("\n=== Test portfolio backtest ===")
    portfolio_config = {
        'start_date': (datetime.now() - timedelta(days=180)).isoformat(),
        'end_date': datetime.now().isoformat(),
        'initial_capital': 50000.0,
        'rebalancing_frequency': 'weekly'
    }
    
    strategies = [
        {
            'name': 'Momentum',
            'weight': 0.4,
            'config': {
                'symbol': 'BTC/USDT',
                'timeframe': '1h',
                'parameters': {'period': 20, 'threshold': 0.02},
                'commission': 0.001
            }
        },
        {
            'name': 'MeanReversion',
            'weight': 0.6,
            'config': {
                'symbol': 'ETH/USDT',
                'timeframe': '1h',
                'parameters': {'period': 14, 'threshold': 0.015},
                'commission': 0.001
            }
        }
    ]
    
    portfolio_result = await backtesting_dashboard.portfolio_backtest(
        strategies, 
        portfolio_config
    )
    
    print(f"Portfolio backtest completed: {portfolio_result['portfolio_id']}")
    print(f"Portfolio Return: {portfolio_result['portfolio_metrics']['total_return']:.2%}")
    print(f"Portfolio Sharpe: {portfolio_result['portfolio_metrics']['sharpe_ratio']:.2f}")
    
    # Monte Carlo simulation
    print("\n=== Test Monte Carlo simulation ===")
    mc_result = await backtesting_dashboard.monte_carlo_simulation(
        config,
        num_simulations=100
    )
    
    print(f"Monte Carlo simulation completed: {mc_result['simulation_id']}")
    print(f"Successful simulations: {mc_result['successful_simulations']}/{mc_result['num_simulations']}")
    print(f"Mean return: {mc_result['statistics']['returns']['mean']:.2%}")
    print(f"VaR 95%: {mc_result['risk_metrics']['var_95']:.2%}")
    print(f"Prob positive Sharpe: {mc_result['risk_metrics']['prob_positive_sharpe']:.1%}")
    
    # Comprehensive metrics
    print("\n=== Test comprehensive metrics ===")
    comprehensive_metrics = calculate_comprehensive_metrics(result)
    print(f"Composite Score: {comprehensive_metrics['score']['composite_score']:.2f}")
    print(f"Grade: {comprehensive_metrics['score']['grade']}")
    print(f"Ulcer Index: {comprehensive_metrics['risk_metrics']['ulcer_index']:.4f}")
    print(f"Kelly Criterion: {comprehensive_metrics['statistical_metrics']['kelly_criterion']:.4f}")
    
    print("\n=== All tests completed successfully! ===")


if __name__ == "__main__":
    asyncio.run(test_backtesting_dashboard())
