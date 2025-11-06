#!/usr/bin/env python3
"""
Pro Backtesting Engine
=======================

Professional-grade backtesting engine with advanced features:
- Multiple strategy testing
- Historical data analysis (10+ years)
- Performance optimization
- Monte Carlo simulation
- Walk-forward analysis
- Multi-timeframe testing
- Transaction cost modeling
- Portfolio backtesting
- Risk-adjusted metrics
- Optimization algorithms

Author: Orion Starline AI Trading System
Version: 1.0.0
"""

import asyncio
import multiprocessing as mp
import warnings
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from pathlib import Path
import json
import pickle
import sqlite3
import logging
from copy import deepcopy
import hashlib
import inspect
import traceback
from collections import defaultdict, deque
from enum import Enum
import threading

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize, differential_evolution, brute
from sklearn.model_selection import ParameterGrid, ParameterSampler
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import joblib
from deap import base, creator, tools, algorithms

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TimeFrame(Enum):
    """Time frame enumerations"""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"
    MN1 = "1M"


class OrderType(Enum):
    """Order type enumerations"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderSide(Enum):
    """Order side enumerations"""
    BUY = "BUY"
    SELL = "SELL"


class PositionSide(Enum):
    """Position side enumerations"""
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"


class OptimizationMethod(Enum):
    """Optimization method enumerations"""
    GENETIC = "GENETIC"
    GRID_SEARCH = "GRID_SEARCH"
    RANDOM_SEARCH = "RANDOM_SEARCH"
    BAYESIAN = "BAYESIAN"


@dataclass
class StrategyConfig:
    """Strategy configuration class"""
    name: str
    strategy_function: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeframe: TimeFrame = TimeFrame.D1
    initial_capital: float = 100000.0
    commission: float = 0.001
    slippage: float = 0.0005
    max_position_size: float = 1.0
    risk_free_rate: float = 0.02
    benchmark: str = "SPY"


@dataclass
class BacktestResult:
    """Backtest result class"""
    strategy_name: str
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
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
    equity_curve: pd.Series
    trades: List[Dict] = field(default_factory=list)
    signals: pd.DataFrame = field(default_factory=pd.DataFrame)
    parameters: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    statistical_significance: float = 1.0


@dataclass
class MonteCarloResult:
    """Monte Carlo simulation result"""
    simulation_count: int
    final_returns: np.ndarray
    max_drawdowns: np.ndarray
    win_rates: np.ndarray
    sharpe_ratios: np.ndarray
    confidence_intervals: Dict[str, Tuple[float, float]]
    worst_case: float
    best_case: float
    median_case: float
    probability_of_loss: float
    var_95: float
    cvar_95: float


@dataclass
class WalkForwardResult:
    """Walk-forward analysis result"""
    periods: List[Tuple[datetime, datetime]]
    results: List[BacktestResult]
    out_of_sample_results: List[BacktestResult]
    performance_metrics: Dict[str, List[float]]
    stability_score: float
    robustness_score: float


class ProBacktestingEngine:
    """
    Professional Backtesting Engine
    
    A comprehensive backtesting system with advanced features:
    - Multiple strategy testing
    - Historical data analysis
    - Performance optimization
    - Monte Carlo simulation
    - Walk-forward analysis
    - Multi-timeframe support
    - Transaction cost modeling
    - Portfolio backtesting
    - Risk-adjusted metrics
    - Statistical significance testing
    """
    
    def __init__(self, 
                 data_manager=None,
                 max_workers: int = None,
                 cache_enabled: bool = True,
                 benchmark_data: pd.DataFrame = None):
        """
        Initialize the backtesting engine
        
        Args:
            data_manager: Data manager for loading historical data
            max_workers: Maximum number of worker processes
            cache_enabled: Enable result caching
            benchmark_data: Benchmark data for comparison
        """
        self.data_manager = data_manager
        self.max_workers = max_workers or mp.cpu_count()
        self.cache_enabled = cache_enabled
        self.benchmark_data = benchmark_data
        self.cache = {}
        self.results_cache = {}
        self.performance_metrics = {}
        self.commission_models = {}
        self.slippage_models = {}
        
        # Thread-local storage for parallel processing
        self._thread_local = threading.local()
        
        # Register default cost models
        self._register_default_cost_models()
        
        logger.info(f"Pro Backtesting Engine initialized with {self.max_workers} workers")
    
    def _register_default_cost_models(self):
        """Register default commission and slippage models"""
        self.commission_models = {
            'fixed': lambda size, price: size * price * 0.001,
            'percentage': lambda size, price: abs(size * price) * 0.001,
            'tiered': self._tiered_commission_model,
            'volume_weighted': self._volume_weighted_commission
        }
        
        self.slippage_models = {
            'constant': lambda size, price, volatility: abs(size * price) * 0.0005,
            'proportional': lambda size, price, volatility: abs(size * price) * 0.0001 * (1 + volatility),
            'market_impact': self._market_impact_slippage,
            'sqrt_impact': self._sqrt_impact_slippage
        }
    
    def _tiered_commission_model(self, size: float, price: float, volume: float = 0) -> float:
        """Tiered commission model based on volume"""
        commission_rate = 0.001
        if volume > 1000000:
            commission_rate = 0.0005
        elif volume > 100000:
            commission_rate = 0.0008
        return abs(size * price) * commission_rate
    
    def _volume_weighted_commission(self, size: float, price: float, volume: float) -> float:
        """Volume-weighted commission model"""
        base_rate = 0.001
        volume_factor = min(volume / 1000000, 1.0)  # Cap at 1.0
        return abs(size * price) * base_rate * (1 - 0.5 * volume_factor)
    
    def _market_impact_slippage(self, size: float, price: float, volatility: float, 
                              market_depth: float = 1000000) -> float:
        """Market impact-based slippage model"""
        normalized_size = abs(size * price) / market_depth
        return abs(size * price) * 0.0001 * (normalized_size ** 0.5) * (1 + volatility)
    
    def _sqrt_impact_slippage(self, size: float, price: float, volatility: float,
                            market_depth: float = 1000000) -> float:
        """Square root market impact slippage model"""
        normalized_size = abs(size * price) / market_depth
        return abs(size * price) * 0.0002 * np.sqrt(normalized_size) * (1 + volatility)
    
    def run_backtest(self,
                    strategy_config: StrategyConfig,
                    data: pd.DataFrame,
                    start_date: datetime = None,
                    end_date: datetime = None,
                    commission_model: str = 'percentage',
                    slippage_model: str = 'proportional') -> BacktestResult:
        """
        Run a single backtest
        
        Args:
            strategy_config: Strategy configuration
            data: Historical price data
            start_date: Backtest start date
            end_date: Backtest end date
            commission_model: Commission model name
            slippage_model: Slippage model name
            
        Returns:
            BacktestResult: Comprehensive backtest results
        """
        start_time = datetime.now()
        
        # Filter data by date range
        if start_date and end_date:
            data = data[(data.index >= start_date) & (data.index <= end_date)]
        
        if data.empty:
            raise ValueError("No data available for the specified date range")
        
        # Initialize strategy
        strategy_func = strategy_config.strategy_function
        params = strategy_config.parameters
        
        # Run strategy to generate signals
        try:
            signals = strategy_func(data, **params)
        except Exception as e:
            logger.error(f"Strategy execution failed: {e}")
            raise
        
        # Initialize backtesting variables
        portfolio = self._initialize_portfolio(strategy_config)
        trades = []
        equity_curve = []
        current_position = PositionSide.FLAT
        position_size = 0.0
        entry_price = 0.0
        
        # Process signals
        for i, (timestamp, signal_data) in enumerate(signals.iterrows()):
            current_price = data.loc[timestamp, 'close'] if 'close' in data.columns else data.iloc[i]['close']
            
            # Generate order based on signal
            order = self._process_signal(signal_data, current_position, position_size)
            
            # Execute order
            if order:
                executed_order = self._execute_order(
                    order, current_price, data.iloc[i], 
                    commission_model, slippage_model,
                    strategy_config
                )
                
                if executed_order:
                    # Update portfolio
                    portfolio, trades = self._update_portfolio(
                        portfolio, executed_order, trades, timestamp
                    )
                    
                    # Update position
                    current_position = executed_order['position_side']
                    position_size = executed_order['position_size']
                    entry_price = executed_order.get('entry_price', 0.0)
            
            # Calculate portfolio value
            portfolio_value = self._calculate_portfolio_value(portfolio, current_price, position_size)
            equity_curve.append({
                'timestamp': timestamp,
                'equity': portfolio_value,
                'position': current_position.value,
                'position_size': position_size
            })
        
        # Calculate performance metrics
        equity_df = pd.DataFrame(equity_curve).set_index('timestamp')
        performance = self._calculate_performance_metrics(
            equity_df['equity'], trades, strategy_config
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Create result
        result = BacktestResult(
            strategy_name=strategy_config.name,
            total_return=performance['total_return'],
            annualized_return=performance['annualized_return'],
            volatility=performance['volatility'],
            sharpe_ratio=performance['sharpe_ratio'],
            sortino_ratio=performance['sortino_ratio'],
            calmar_ratio=performance['calmar_ratio'],
            max_drawdown=performance['max_drawdown'],
            win_rate=performance['win_rate'],
            profit_factor=performance['profit_factor'],
            total_trades=performance['total_trades'],
            winning_trades=performance['winning_trades'],
            losing_trades=performance['losing_trades'],
            avg_win=performance['avg_win'],
            avg_loss=performance['avg_loss'],
            largest_win=performance['largest_win'],
            largest_loss=performance['largest_loss'],
            equity_curve=equity_df['equity'],
            trades=trades,
            signals=signals,
            parameters=params,
            execution_time=execution_time
        )
        
        # Cache result
        if self.cache_enabled:
            cache_key = self._generate_cache_key(strategy_config, data, start_date, end_date)
            self.cache[cache_key] = result
        
        return result
    
    def run_multiple_strategies(self,
                               strategies: List[StrategyConfig],
                               data: pd.DataFrame,
                               start_date: datetime = None,
                               end_date: datetime = None,
                               parallel: bool = True) -> List[BacktestResult]:
        """
        Run multiple strategies simultaneously
        
        Args:
            strategies: List of strategy configurations
            data: Historical price data
            start_date: Backtest start date
            end_date: Backtest end date
            parallel: Run strategies in parallel
            
        Returns:
            List[BacktestResult]: Results for all strategies
        """
        if parallel:
            return self._run_strategies_parallel(strategies, data, start_date, end_date)
        else:
            return self._run_strategies_sequential(strategies, data, start_date, end_date)
    
    def _run_strategies_parallel(self,
                                strategies: List[StrategyConfig],
                                data: pd.DataFrame,
                                start_date: datetime,
                                end_date: datetime) -> List[BacktestResult]:
        """Run strategies in parallel"""
        results = []
        
        with ThreadPoolExecutor(max_workers=min(len(strategies), self.max_workers)) as executor:
            futures = []
            for strategy in strategies:
                future = executor.submit(
                    self.run_backtest, strategy, data, start_date, end_date
                )
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Strategy execution failed: {e}")
        
        return results
    
    def _run_strategies_sequential(self,
                                  strategies: List[StrategyConfig],
                                  data: pd.DataFrame,
                                  start_date: datetime,
                                  end_date: datetime) -> List[BacktestResult]:
        """Run strategies sequentially"""
        results = []
        for strategy in strategies:
            try:
                result = self.run_backtest(strategy, data, start_date, end_date)
                results.append(result)
            except Exception as e:
                logger.error(f"Strategy execution failed for {strategy.name}: {e}")
        
        return results
    
    def optimize_strategy_parameters(self,
                                    strategy_config: StrategyConfig,
                                    data: pd.DataFrame,
                                    parameter_ranges: Dict[str, Any],
                                    optimization_method: OptimizationMethod = OptimizationMethod.GRID_SEARCH,
                                    max_iterations: int = 100,
                                    objective: str = 'sharpe_ratio') -> Tuple[Dict[str, Any], BacktestResult]:
        """
        Optimize strategy parameters using various optimization algorithms
        
        Args:
            strategy_config: Strategy configuration
            data: Historical price data
            parameter_ranges: Dictionary of parameter ranges
            optimization_method: Optimization algorithm to use
            max_iterations: Maximum number of iterations
            objective: Optimization objective function
            
        Returns:
            Tuple[Dict, BacktestResult]: Best parameters and result
        """
        logger.info(f"Starting parameter optimization using {optimization_method.value}")
        
        if optimization_method == OptimizationMethod.GRID_SEARCH:
            return self._grid_search_optimization(
                strategy_config, data, parameter_ranges, objective
            )
        elif optimization_method == OptimizationMethod.GENETIC:
            return self._genetic_optimization(
                strategy_config, data, parameter_ranges, objective, max_iterations
            )
        elif optimization_method == OptimizationMethod.RANDOM_SEARCH:
            return self._random_search_optimization(
                strategy_config, data, parameter_ranges, objective, max_iterations
            )
        else:
            raise ValueError(f"Unsupported optimization method: {optimization_method}")
    
    def _grid_search_optimization(self,
                                 strategy_config: StrategyConfig,
                                 data: pd.DataFrame,
                                 parameter_ranges: Dict[str, Any],
                                 objective: str) -> Tuple[Dict[str, Any], BacktestResult]:
        """Grid search optimization"""
        # Generate parameter grid
        param_grid = list(ParameterGrid(parameter_ranges))
        
        best_score = float('-inf')
        best_params = {}
        best_result = None
        
        # Create modified strategy configs for each parameter combination
        for params in param_grid:
            try:
                # Create new strategy config with these parameters
                modified_config = deepcopy(strategy_config)
                modified_config.parameters.update(params)
                
                # Run backtest
                result = self.run_backtest(modified_config, data)
                
                # Get objective score
                score = getattr(result, objective, 0)
                
                if score > best_score:
                    best_score = score
                    best_params = params
                    best_result = result
                    
            except Exception as e:
                logger.warning(f"Parameter combination {params} failed: {e}")
                continue
        
        logger.info(f"Grid search completed. Best {objective}: {best_score:.4f}")
        return best_params, best_result
    
    def _genetic_optimization(self,
                             strategy_config: StrategyConfig,
                             data: pd.DataFrame,
                             parameter_ranges: Dict[str, Any],
                             objective: str,
                             max_iterations: int) -> Tuple[Dict[str, Any], BacktestResult]:
        """Genetic algorithm optimization"""
        # Create DEAP types
        if not hasattr(creator, "FitnessMax"):
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        if not hasattr(creator, "Individual"):
            creator.create("Individual", list, fitness=creator.FitnessMax)
        
        # Initialize toolbox
        toolbox = base.Toolbox()
        
        # Define gene generators based on parameter types
        gene_generators = {}
        for param_name, param_range in parameter_ranges.items():
            if isinstance(param_range, list):
                gene_generators[param_name] = lambda: np.random.choice(param_range)
            elif isinstance(param_range, tuple) and len(param_range) == 2:
                if isinstance(param_range[0], int):
                    gene_generators[param_name] = lambda lr=param_range: np.random.randint(lr[0], lr[1] + 1)
                else:
                    gene_generators[param_name] = lambda lr=param_range: np.random.uniform(lr[0], lr[1])
        
        # Create individual
        def create_individual():
            individual = creator.Individual([])
            for param_name in parameter_ranges.keys():
                individual.append(gene_generators[param_name]())
            return individual
        
        toolbox.register("individual", create_individual)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        # Import partial function for proper parameter binding
        from functools import partial
        toolbox.register("evaluate", partial(self._evaluate_individual, strategy_config=strategy_config, data=data, objective=objective))
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.2)
        toolbox.register("select", tools.selTournament, tournsize=3)
        
        # Run genetic algorithm
        population = toolbox.population(n=50)
        
        # Evaluate initial population
        fitnesses = list(map(toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit
        
        for generation in range(max_iterations):
            # Select next generation
            offspring = toolbox.select(population, len(population))
            offspring = list(map(toolbox.clone, offspring))
            
            # Apply crossover and mutation
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if np.random.random() < 0.8:  # Crossover probability
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
            
            for mutant in offspring:
                if np.random.random() < 0.2:  # Mutation probability
                    toolbox.mutate(mutant)
                    del mutant.fitness.values
            
            # Evaluate offspring
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            
            # Replace population
            population[:] = offspring
            
            # Log progress
            fits = [ind.fitness.values[0] for ind in population]
            length = len(population)
            mean = np.mean(fits)
            std = np.std(fits)
            
            logger.info(f"Generation {generation}: Min {np.min(fits):.4f}, Max {np.max(fits):.4f}, "
                       f"Mean {mean:.4f}, Std {std:.4f}")
        
        # Get best individual
        best_individual = tools.selBest(population, k=1)[0]
        best_fitness = best_individual.fitness.values[0]
        
        # Convert to parameter dictionary
        best_params = {}
        for i, param_name in enumerate(parameter_ranges.keys()):
            best_params[param_name] = best_individual[i]
        
        # Run backtest with best parameters
        modified_config = deepcopy(strategy_config)
        modified_config.parameters.update(best_params)
        best_result = self.run_backtest(modified_config, data)
        
        logger.info(f"Genetic optimization completed. Best {objective}: {best_fitness:.4f}")
        return best_params, best_result
    
    def _random_search_optimization(self,
                                   strategy_config: StrategyConfig,
                                   data: pd.DataFrame,
                                   parameter_ranges: Dict[str, Any],
                                   objective: str,
                                   max_iterations: int) -> Tuple[Dict[str, Any], BacktestResult]:
        """Random search optimization"""
        # Generate random parameter combinations
        param_sampler = ParameterSampler(parameter_ranges, n_iterations=max_iterations)
        
        best_score = float('-inf')
        best_params = {}
        best_result = None
        
        for i, params in enumerate(param_sampler):
            try:
                # Create new strategy config
                modified_config = deepcopy(strategy_config)
                modified_config.parameters.update(params)
                
                # Run backtest
                result = self.run_backtest(modified_config, data)
                
                # Get objective score
                score = getattr(result, objective, 0)
                
                if score > best_score:
                    best_score = score
                    best_params = params
                    best_result = result
                    
                if (i + 1) % 10 == 0:
                    logger.info(f"Completed {i + 1}/{max_iterations} iterations. Best {objective}: {best_score:.4f}")
                    
            except Exception as e:
                logger.warning(f"Parameter combination {params} failed: {e}")
                continue
        
        logger.info(f"Random search completed. Best {objective}: {best_score:.4f}")
        return best_params, best_result
    
    def _evaluate_individual(self, individual, strategy_config, data, objective):
        """Evaluate individual for genetic algorithm"""
        try:
            # Convert individual to parameter dictionary
            params = {}
            for i, param_name in enumerate(strategy_config.parameters.keys()):
                params[param_name] = individual[i]
            
            # Create modified config
            modified_config = deepcopy(strategy_config)
            modified_config.parameters.update(params)
            
            # Run backtest
            result = self.run_backtest(modified_config, data)
            
            # Return objective score (for minimization, negate if needed)
            score = getattr(result, objective, 0)
            return (score,)
            
        except Exception as e:
            logger.warning(f"Individual evaluation failed: {e}")
            return (float('-inf'),)
    
    def run_monte_carlo_simulation(self,
                                  strategy_config: StrategyConfig,
                                  data: pd.DataFrame,
                                  num_simulations: int = 1000,
                                  bootstrap_method: str = 'block',
                                  confidence_level: float = 0.95) -> MonteCarloResult:
        """
        Run Monte Carlo simulation for risk analysis
        
        Args:
            strategy_config: Strategy configuration
            data: Historical price data
            num_simulations: Number of Monte Carlo simulations
            bootstrap_method: Bootstrap method ('block', 'random', 'circular')
            confidence_level: Confidence level for intervals
            
        Returns:
            MonteCarloResult: Monte Carlo simulation results
        """
        logger.info(f"Starting Monte Carlo simulation with {num_simulations} simulations")
        
        # Generate bootstrap samples
        if bootstrap_method == 'block':
            bootstrap_samples = self._block_bootstrap(data, num_simulations)
        elif bootstrap_method == 'random':
            bootstrap_samples = self._random_bootstrap(data, num_simulations)
        elif bootstrap_method == 'circular':
            bootstrap_samples = self._circular_bootstrap(data, num_simulations)
        else:
            raise ValueError(f"Unknown bootstrap method: {bootstrap_method}")
        
        # Run backtests on bootstrap samples
        final_returns = []
        max_drawdowns = []
        win_rates = []
        sharpe_ratios = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for sample_data in bootstrap_samples:
                future = executor.submit(
                    self.run_backtest, strategy_config, sample_data
                )
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    final_returns.append(result.total_return)
                    max_drawdowns.append(result.max_drawdown)
                    win_rates.append(result.win_rate)
                    sharpe_ratios.append(result.sharpe_ratio)
                except Exception as e:
                    logger.warning(f"Monte Carlo simulation iteration failed: {e}")
                    continue
        
        # Calculate statistics
        final_returns = np.array(final_returns)
        max_drawdowns = np.array(max_drawdowns)
        win_rates = np.array(win_rates)
        sharpe_ratios = np.array(sharpe_ratios)
        
        # Calculate confidence intervals
        alpha = 1 - confidence_level
        confidence_intervals = {}
        for metric_name, values in [
            ('total_return', final_returns),
            ('max_drawdown', max_drawdowns),
            ('win_rate', win_rates),
            ('sharpe_ratio', sharpe_ratios)
        ]:
            lower = np.percentile(values, 100 * alpha / 2)
            upper = np.percentile(values, 100 * (1 - alpha / 2))
            confidence_intervals[metric_name] = (lower, upper)
        
        # Calculate risk metrics
        worst_case = np.percentile(final_returns, 5)
        best_case = np.percentile(final_returns, 95)
        median_case = np.median(final_returns)
        probability_of_loss = np.mean(final_returns < 0)
        
        # Calculate VaR and CVaR
        var_95 = np.percentile(final_returns, 5)
        cvar_95 = np.mean(final_returns[final_returns <= var_95])
        
        result = MonteCarloResult(
            simulation_count=len(final_returns),
            final_returns=final_returns,
            max_drawdowns=max_drawdowns,
            win_rates=win_rates,
            sharpe_ratios=sharpe_ratios,
            confidence_intervals=confidence_intervals,
            worst_case=worst_case,
            best_case=best_case,
            median_case=median_case,
            probability_of_loss=probability_of_loss,
            var_95=var_95,
            cvar_95=cvar_95
        )
        
        logger.info(f"Monte Carlo simulation completed. "
                   f"Probability of loss: {probability_of_loss:.2%}, "
                   f"VaR (95%): {var_95:.2%}")
        
        return result
    
    def _block_bootstrap(self, data: pd.DataFrame, num_samples: int) -> List[pd.DataFrame]:
        """Block bootstrap method"""
        samples = []
        block_size = max(1, len(data) // 10)  # Use 10 blocks
        
        for _ in range(num_samples):
            # Random starting point
            start_idx = np.random.randint(0, len(data) - block_size + 1)
            
            # Create bootstrap sample by concatenating blocks
            sample_data = []
            while len(pd.concat(sample_data)) < len(data):
                block_start = np.random.randint(0, len(data) - block_size + 1)
                block = data.iloc[block_start:block_start + block_size]
                sample_data.append(block)
            
            # Combine blocks and trim to original length
            bootstrap_sample = pd.concat(sample_data).iloc[:len(data)]
            samples.append(bootstrap_sample)
        
        return samples
    
    def _random_bootstrap(self, data: pd.DataFrame, num_samples: int) -> List[pd.DataFrame]:
        """Random bootstrap method"""
        samples = []
        for _ in range(num_samples):
            # Random sample with replacement
            sample_indices = np.random.choice(len(data), size=len(data), replace=True)
            bootstrap_sample = data.iloc[sample_indices]
            samples.append(bootstrap_sample)
        
        return samples
    
    def _circular_bootstrap(self, data: pd.DataFrame, num_samples: int) -> List[pd.DataFrame]:
        """Circular bootstrap method"""
        samples = []
        for _ in range(num_samples):
            # Random starting point
            start_idx = np.random.randint(0, len(data))
            
            # Create circular sample
            sample_indices = []
            for i in range(len(data)):
                sample_indices.append((start_idx + i) % len(data))
            
            bootstrap_sample = data.iloc[sample_indices]
            samples.append(bootstrap_sample)
        
        return samples
    
    def run_walk_forward_analysis(self,
                                 strategy_config: StrategyConfig,
                                 data: pd.DataFrame,
                                 in_sample_period: int = 252,  # 1 year in trading days
                                 out_of_sample_period: int = 63,  # 3 months
                                 step_size: int = 21) -> WalkForwardResult:
        """
        Run walk-forward analysis for out-of-sample testing
        
        Args:
            strategy_config: Strategy configuration
            data: Historical price data
            in_sample_period: In-sample period length (trading days)
            out_of_sample_period: Out-of-sample period length
            step_size: Step size for rolling window
            
        Returns:
            WalkForwardResult: Walk-forward analysis results
        """
        logger.info("Starting walk-forward analysis")
        
        periods = []
        results = []
        out_of_sample_results = []
        
        start_idx = 0
        end_idx = len(data)
        
        while start_idx + in_sample_period + out_of_sample_period <= end_idx:
            # Define periods
            in_sample_end = start_idx + in_sample_period
            out_sample_end = in_sample_end + out_of_sample_period
            
            in_sample_data = data.iloc[start_idx:in_sample_end]
            out_sample_data = data.iloc[in_sample_end:out_sample_end]
            
            period_start = data.index[start_idx]
            period_end = data.index[out_sample_end - 1]
            periods.append((period_start, period_end))
            
            # In-sample optimization
            try:
                optimized_params, in_sample_result = self.optimize_strategy_parameters(
                    strategy_config, in_sample_data, 
                    strategy_config.parameters
                )
                results.append(in_sample_result)
            except Exception as e:
                logger.warning(f"In-sample optimization failed: {e}")
                results.append(None)
            
            # Out-of-sample testing with optimized parameters
            try:
                if optimized_params:
                    modified_config = deepcopy(strategy_config)
                    modified_config.parameters.update(optimized_params)
                    out_sample_result = self.run_backtest(modified_config, out_sample_data)
                    out_of_sample_results.append(out_sample_result)
                else:
                    out_of_sample_results.append(None)
            except Exception as e:
                logger.warning(f"Out-of-sample test failed: {e}")
                out_of_sample_results.append(None)
            
            # Move to next period
            start_idx += step_size
        
        # Calculate performance metrics across periods
        performance_metrics = self._calculate_walk_forward_metrics(results, out_of_sample_results)
        
        # Calculate stability and robustness scores
        stability_score = self._calculate_stability_score(results)
        robustness_score = self._calculate_robustness_score(results, out_of_sample_results)
        
        result = WalkForwardResult(
            periods=periods,
            results=results,
            out_of_sample_results=out_of_sample_results,
            performance_metrics=performance_metrics,
            stability_score=stability_score,
            robustness_score=robustness_score
        )
        
        logger.info(f"Walk-forward analysis completed. Stability: {stability_score:.2f}, "
                   f"Robustness: {robustness_score:.2f}")
        
        return result
    
    def run_multi_timeframe_analysis(self,
                                    strategy_configs: List[StrategyConfig],
                                    data_dict: Dict[TimeFrame, pd.DataFrame],
                                    start_date: datetime = None,
                                    end_date: datetime = None) -> Dict[str, BacktestResult]:
        """
        Run analysis across multiple timeframes
        
        Args:
            strategy_configs: Strategy configurations for each timeframe
            data_dict: Dictionary of timeframe -> data
            start_date: Analysis start date
            end_date: Analysis end date
            
        Returns:
            Dict[str, BacktestResult]: Results for each timeframe
        """
        logger.info("Starting multi-timeframe analysis")
        
        results = {}
        
        for timeframe, data in data_dict.items():
            # Find corresponding strategy config
            strategy_config = next(
                (sc for sc in strategy_configs if sc.timeframe == timeframe), None
            )
            
            if strategy_config is None:
                logger.warning(f"No strategy config found for timeframe {timeframe.value}")
                continue
            
            try:
                # Run backtest for this timeframe
                result = self.run_backtest(strategy_config, data, start_date, end_date)
                results[timeframe.value] = result
                
                logger.info(f"Completed analysis for {timeframe.value}: "
                           f"Return: {result.total_return:.2%}, "
                           f"Sharpe: {result.sharpe_ratio:.2f}")
                           
            except Exception as e:
                logger.error(f"Multi-timeframe analysis failed for {timeframe.value}: {e}")
                continue
        
        return results
    
    def run_portfolio_backtest(self,
                              strategies: List[StrategyConfig],
                              weights: List[float],
                              data_dict: Dict[str, pd.DataFrame],
                              rebalance_frequency: str = 'monthly',
                              start_date: datetime = None,
                              end_date: datetime = None) -> BacktestResult:
        """
        Run portfolio backtest with multiple strategies and assets
        
        Args:
            strategies: List of strategy configurations
            weights: Portfolio weights for each strategy
            data_dict: Dictionary of asset -> data
            rebalance_frequency: Portfolio rebalancing frequency
            start_date: Backtest start date
            end_date: Backtest end date
            
        Returns:
            BacktestResult: Portfolio backtest results
        """
        logger.info("Starting portfolio backtest")
        
        # Normalize weights
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        # Initialize portfolio tracking
        portfolio_values = []
        individual_strategies = {}
        
        # Run individual strategy backtests
        for i, (strategy, weight) in enumerate(zip(strategies, weights)):
            asset_name = f"strategy_{i}"
            try:
                result = self.run_backtest(strategy, list(data_dict.values())[0], start_date, end_date)
                individual_strategies[asset_name] = result
                logger.info(f"Completed strategy {i} backtest: Return {result.total_return:.2%}")
            except Exception as e:
                logger.error(f"Strategy {i} backtest failed: {e}")
                continue
        
        # Calculate portfolio equity curve
        portfolio_equity = self._calculate_portfolio_equity(
            individual_strategies, weights, rebalance_frequency
        )
        
        # Calculate portfolio performance metrics
        portfolio_performance = self._calculate_portfolio_metrics(
            portfolio_equity, individual_strategies
        )
        
        # Create portfolio result
        portfolio_result = BacktestResult(
            strategy_name="Portfolio",
            total_return=portfolio_performance['total_return'],
            annualized_return=portfolio_performance['annualized_return'],
            volatility=portfolio_performance['volatility'],
            sharpe_ratio=portfolio_performance['sharpe_ratio'],
            sortino_ratio=portfolio_performance['sortino_ratio'],
            calmar_ratio=portfolio_performance['calmar_ratio'],
            max_drawdown=portfolio_performance['max_drawdown'],
            win_rate=portfolio_performance['win_rate'],
            profit_factor=portfolio_performance['profit_factor'],
            total_trades=portfolio_performance['total_trades'],
            winning_trades=portfolio_performance['winning_trades'],
            losing_trades=portfolio_performance['losing_trades'],
            avg_win=portfolio_performance['avg_win'],
            avg_loss=portfolio_performance['avg_loss'],
            largest_win=portfolio_performance['largest_win'],
            largest_loss=portfolio_performance['largest_loss'],
            equity_curve=portfolio_equity,
            trades=[],  # Portfolio-level trades
            signals=pd.DataFrame(),
            parameters={'weights': weights.tolist()}
        )
        
        logger.info(f"Portfolio backtest completed. Return: {portfolio_result.total_return:.2%}, "
                   f"Sharpe: {portfolio_result.sharpe_ratio:.2f}")
        
        return portfolio_result
    
    def calculate_statistical_significance(self,
                                          strategy_results: List[BacktestResult],
                                          benchmark_results: List[BacktestResult],
                                          alpha: float = 0.05) -> Dict[str, Any]:
        """
        Calculate statistical significance of strategy performance
        
        Args:
            strategy_results: List of strategy backtest results
            benchmark_results: List of benchmark backtest results
            alpha: Significance level
            
        Returns:
            Dict with statistical test results
        """
        logger.info("Calculating statistical significance")
        
        # Extract returns
        strategy_returns = np.array([r.total_return for r in strategy_results])
        benchmark_returns = np.array([r.total_return for r in benchmark_results])
        
        # Extract Sharpe ratios
        strategy_sharpe = np.array([r.sharpe_ratio for r in strategy_results])
        benchmark_sharpe = np.array([r.sharpe_ratio for r in benchmark_results])
        
        # Perform t-tests
        return_test = stats.ttest_ind(strategy_returns, benchmark_returns)
        sharpe_test = stats.ttest_ind(strategy_sharpe, benchmark_sharpe)
        
        # Mann-Whitney U test (non-parametric)
        return_mw = stats.mannwhitneyu(strategy_returns, benchmark_returns, alternative='two-sided')
        sharpe_mw = stats.mannwhitneyu(strategy_sharpe, benchmark_sharpe, alternative='two-sided')
        
        # Effect sizes (Cohen's d)
        return_cohens_d = self._cohens_d(strategy_returns, benchmark_returns)
        sharpe_cohens_d = self._cohens_d(strategy_sharpe, benchmark_sharpe)
        
        # Bootstrap confidence intervals for difference in means
        return_ci = self._bootstrap_confidence_interval(strategy_returns, benchmark_returns)
        sharpe_ci = self._bootstrap_confidence_interval(strategy_sharpe, benchmark_sharpe)
        
        results = {
            'return_test': {
                't_statistic': return_test.statistic,
                'p_value': return_test.pvalue,
                'significant': return_test.pvalue < alpha,
                'cohens_d': return_cohens_d,
                'confidence_interval': return_ci
            },
            'sharpe_test': {
                't_statistic': sharpe_test.statistic,
                'p_value': sharpe_test.pvalue,
                'significant': sharpe_test.pvalue < alpha,
                'cohens_d': sharpe_cohens_d,
                'confidence_interval': sharpe_ci
            },
            'mann_whitney_return': {
                'u_statistic': return_mw.statistic,
                'p_value': return_mw.pvalue,
                'significant': return_mw.pvalue < alpha
            },
            'mann_whitney_sharpe': {
                'u_statistic': sharpe_mw.statistic,
                'p_value': sharpe_mw.pvalue,
                'significant': sharpe_mw.pvalue < alpha
            },
            'effect_sizes': {
                'return': return_cohens_d,
                'sharpe': sharpe_cohens_d
            }
        }
        
        logger.info(f"Statistical significance tests completed. "
                   f"Return p-value: {return_test.pvalue:.4f}, "
                   f"Sharpe p-value: {sharpe_test.pvalue:.4f}")
        
        return results
    
    def generate_comprehensive_report(self,
                                     results: Union[BacktestResult, List[BacktestResult]],
                                     benchmark_results: List[BacktestResult] = None,
                                     monte_carlo_results: MonteCarloResult = None,
                                     walk_forward_results: WalkForwardResult = None,
                                     save_path: str = None) -> str:
        """
        Generate comprehensive backtesting report
        
        Args:
            results: Backtest results (single or multiple)
            benchmark_results: Benchmark results for comparison
            monte_carlo_results: Monte Carlo simulation results
            walk_forward_results: Walk-forward analysis results
            save_path: Path to save the report
            
        Returns:
            str: HTML report content
        """
        logger.info("Generating comprehensive backtesting report")
        
        if not isinstance(results, list):
            results = [results]
        
        # Create subplots
        fig = make_subplots(
            rows=4, cols=2,
            subplot_titles=(
                'Equity Curves', 'Drawdown Analysis',
                'Returns Distribution', 'Performance Metrics',
                'Risk-Return Scatter', 'Monte Carlo Analysis',
                'Walk-Forward Results', 'Statistical Tests'
            ),
            specs=[
                [{"secondary_y": True}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}],
                [{"secondary_y": False}, {"secondary_y": False}]
            ]
        )
        
        # Plot equity curves
        colors = px.colors.qualitative.Set1
        for i, result in enumerate(results):
            color = colors[i % len(colors)]
            fig.add_trace(
                go.Scatter(
                    x=result.equity_curve.index,
                    y=result.equity_curve.values,
                    name=result.strategy_name,
                    line=dict(color=color)
                ),
                row=1, col=1
            )
        
        # Plot drawdown
        for i, result in enumerate(results):
            equity = result.equity_curve
            peak = equity.cummax()
            drawdown = (equity - peak) / peak * 100
            color = colors[i % len(colors)]
            fig.add_trace(
                go.Scatter(
                    x=drawdown.index,
                    y=drawdown.values,
                    name=f'{result.strategy_name} DD',
                    line=dict(color=color, dash='dash'),
                    showlegend=False
                ),
                row=1, col=2
            )
        
        # Add benchmark if available
        if benchmark_results:
            for i, result in enumerate(benchmark_results):
                fig.add_trace(
                    go.Scatter(
                        x=result.equity_curve.index,
                        y=result.equity_curve.values,
                        name=f'Benchmark {i+1}',
                        line=dict(color='gray', dash='dot')
                    ),
                    row=1, col=1
                )
        
        # Generate HTML report
        html_content = self._generate_html_report(
            results, benchmark_results, monte_carlo_results, walk_forward_results, fig
        )
        
        if save_path:
            Path(save_path).write_text(html_content, encoding='utf-8')
            logger.info(f"Report saved to {save_path}")
        
        return html_content
    
    # Helper methods for calculations
    
    def _initialize_portfolio(self, strategy_config: StrategyConfig) -> Dict:
        """Initialize portfolio tracking"""
        return {
            'cash': strategy_config.initial_capital,
            'positions': {},
            'total_value': strategy_config.initial_capital,
            'equity_curve': [],
            'trades': []
        }
    
    def _process_signal(self, signal_data, current_position: PositionSide, position_size: float) -> Optional[Dict]:
        """Process trading signal"""
        signal_value = signal_data.get('signal', 0)
        
        if abs(signal_value) < 0.1:  # No signal
            return None
        
        if signal_value > 0 and current_position != PositionSide.LONG:
            return {
                'order_type': OrderType.MARKET,
                'side': OrderSide.BUY,
                'position_side': PositionSide.LONG,
                'size': abs(signal_value),
                'timestamp': signal_data.name
            }
        elif signal_value < 0 and current_position != PositionSide.SHORT:
            return {
                'order_type': OrderType.MARKET,
                'side': OrderSide.SELL,
                'position_side': PositionSide.SHORT,
                'size': abs(signal_value),
                'timestamp': signal_data.name
            }
        
        return None
    
    def _execute_order(self, order: Dict, current_price: float, market_data: pd.Series,
                      commission_model: str, slippage_model: str, strategy_config: StrategyConfig) -> Optional[Dict]:
        """Execute order with cost modeling"""
        try:
            # Calculate slippage
            volatility = market_data.get('volatility', 0.01)
            volume = market_data.get('volume', 1000000)
            
            slippage_func = self.slippage_models.get(slippage_model, 
                                                   self.slippage_models['proportional'])
            slippage = slippage_func(order['size'], current_price, volatility)
            
            # Calculate commission
            commission_func = self.commission_models.get(commission_model,
                                                       self.commission_models['percentage'])
            commission = commission_func(order['size'], current_price)
            
            # Apply costs
            execution_price = current_price
            if order['side'] == OrderSide.BUY:
                execution_price += slippage
            else:
                execution_price -= slippage
            
            # Create executed order
            executed_order = {
                **order,
                'execution_price': execution_price,
                'commission': commission,
                'slippage': slippage,
                'total_cost': commission + abs(slippage * order['size']),
                'entry_price': execution_price,
                'position_size': order['size'] if order['position_side'] == PositionSide.LONG else -order['size']
            }
            
            return executed_order
            
        except Exception as e:
            logger.error(f"Order execution failed: {e}")
            return None
    
    def _update_portfolio(self, portfolio: Dict, executed_order: Dict, trades: List, timestamp: datetime) -> Tuple[Dict, List]:
        """Update portfolio after order execution"""
        try:
            # Calculate trade value
            trade_value = executed_order['position_size'] * executed_order['execution_price']
            
            # Update cash
            if executed_order['side'] == OrderSide.BUY:
                portfolio['cash'] -= trade_value + executed_order['total_cost']
            else:
                portfolio['cash'] += trade_value - executed_order['total_cost']
            
            # Add to trades
            trade_record = {
                'timestamp': timestamp,
                'side': executed_order['side'].value,
                'position_side': executed_order['position_side'].value,
                'size': executed_order['size'],
                'price': executed_order['execution_price'],
                'commission': executed_order['commission'],
                'slippage': executed_order['slippage'],
                'total_cost': executed_order['total_cost']
            }
            trades.append(trade_record)
            
            return portfolio, trades
            
        except Exception as e:
            logger.error(f"Portfolio update failed: {e}")
            return portfolio, trades
    
    def _calculate_portfolio_value(self, portfolio: Dict, current_price: float, position_size: float) -> float:
        """Calculate current portfolio value"""
        try:
            position_value = position_size * current_price
            total_value = portfolio['cash'] + position_value
            return total_value
        except Exception as e:
            logger.error(f"Portfolio value calculation failed: {e}")
            return 0.0
    
    def _calculate_performance_metrics(self, equity_curve: pd.Series, trades: List, strategy_config: StrategyConfig) -> Dict[str, float]:
        """Calculate comprehensive performance metrics"""
        try:
            # Basic metrics
            total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
            
            # Calculate daily returns
            daily_returns = equity_curve.pct_change().dropna()
            
            # Annualized metrics
            trading_days_per_year = 252
            annualized_return = (1 + total_return) ** (trading_days_per_year / len(equity_curve)) - 1
            volatility = daily_returns.std() * np.sqrt(trading_days_per_year)
            
            # Risk-adjusted metrics
            risk_free_rate = strategy_config.risk_free_rate
            sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility > 0 else 0
            
            # Sortino ratio (using downside deviation)
            downside_returns = daily_returns[daily_returns < 0]
            downside_deviation = downside_returns.std() * np.sqrt(trading_days_per_year) if len(downside_returns) > 0 else 0
            sortino_ratio = (annualized_return - risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
            
            # Maximum drawdown
            peak = equity_curve.cummax()
            drawdown = (equity_curve - peak) / peak
            max_drawdown = abs(drawdown.min())
            
            # Calmar ratio
            calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0
            
            # Trade analysis
            if trades:
                trade_returns = []
                winning_trades = []
                losing_trades = []
                
                for i in range(0, len(trades) - 1, 2):
                    if i + 1 < len(trades):
                        entry_trade = trades[i]
                        exit_trade = trades[i + 1]
                        
                        if entry_trade['side'] == 'BUY' and exit_trade['side'] == 'SELL':
                            trade_return = (exit_trade['price'] - entry_trade['price']) / entry_trade['price']
                        elif entry_trade['side'] == 'SELL' and exit_trade['side'] == 'BUY':
                            trade_return = (entry_trade['price'] - exit_trade['price']) / entry_trade['price']
                        else:
                            continue
                        
                        trade_returns.append(trade_return)
                        
                        if trade_return > 0:
                            winning_trades.append(trade_return)
                        else:
                            losing_trades.append(trade_return)
                
                # Trade metrics
                total_trades = len(trade_returns)
                winning_trades_count = len(winning_trades)
                losing_trades_count = len(losing_trades)
                win_rate = winning_trades_count / total_trades if total_trades > 0 else 0
                
                avg_win = np.mean(winning_trades) if winning_trades else 0
                avg_loss = np.mean(losing_trades) if losing_trades else 0
                largest_win = np.max(winning_trades) if winning_trades else 0
                largest_loss = np.min(losing_trades) if losing_trades else 0
                
                # Profit factor
                gross_profit = sum(winning_trades) if winning_trades else 0
                gross_loss = abs(sum(losing_trades)) if losing_trades else 0
                profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
                
            else:
                # No trades
                total_trades = winning_trades_count = losing_trades_count = 0
                win_rate = avg_win = avg_loss = largest_win = largest_loss = 0
                profit_factor = 0
            
            return {
                'total_return': total_return,
                'annualized_return': annualized_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'sortino_ratio': sortino_ratio,
                'calmar_ratio': calmar_ratio,
                'max_drawdown': max_drawdown,
                'win_rate': win_rate,
                'profit_factor': profit_factor,
                'total_trades': total_trades,
                'winning_trades': winning_trades_count,
                'losing_trades': losing_trades_count,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'largest_win': largest_win,
                'largest_loss': largest_loss
            }
            
        except Exception as e:
            logger.error(f"Performance metrics calculation failed: {e}")
            return {key: 0.0 for key in [
                'total_return', 'annualized_return', 'volatility', 'sharpe_ratio',
                'sortino_ratio', 'calmar_ratio', 'max_drawdown', 'win_rate',
                'profit_factor', 'total_trades', 'winning_trades', 'losing_trades',
                'avg_win', 'avg_loss', 'largest_win', 'largest_loss'
            ]}
    
    def _calculate_walk_forward_metrics(self, results: List[BacktestResult], 
                                       out_of_sample_results: List[BacktestResult]) -> Dict[str, List[float]]:
        """Calculate walk-forward performance metrics"""
        metrics = {
            'total_returns': [],
            'sharpe_ratios': [],
            'max_drawdowns': [],
            'win_rates': []
        }
        
        for result in results:
            if result:
                metrics['total_returns'].append(result.total_return)
                metrics['sharpe_ratios'].append(result.sharpe_ratio)
                metrics['max_drawdowns'].append(result.max_drawdown)
                metrics['win_rates'].append(result.win_rate)
        
        return metrics
    
    def _calculate_stability_score(self, results: List[BacktestResult]) -> float:
        """Calculate stability score based on performance consistency"""
        if len(results) < 2:
            return 0.0
        
        returns = [r.total_return for r in results if r]
        if len(returns) < 2:
            return 0.0
        
        # Calculate coefficient of variation
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if mean_return == 0:
            return 0.0
        
        cv = std_return / abs(mean_return)
        stability_score = max(0, 1 - cv)  # Lower CV = higher stability
        
        return stability_score
    
    def _calculate_robustness_score(self, results: List[BacktestResult], 
                                   out_of_sample_results: List[BacktestResult]) -> float:
        """Calculate robustness score based on in-sample vs out-of-sample performance"""
        in_sample_returns = [r.total_return for r in results if r]
        out_sample_returns = [r.total_return for r in out_of_sample_results if r]
        
        if len(in_sample_returns) < 2 or len(out_sample_returns) < 2:
            return 0.0
        
        in_sample_mean = np.mean(in_sample_returns)
        out_sample_mean = np.mean(out_sample_returns)
        
        # Robustness score based on out-of-sample performance relative to in-sample
        if in_sample_mean <= 0:
            return 0.0
        
        robustness_score = min(1.0, out_sample_mean / in_sample_mean)
        
        return robustness_score
    
    def _calculate_portfolio_equity(self, individual_strategies: Dict[str, BacktestResult], 
                                   weights: np.ndarray, rebalance_frequency: str) -> pd.Series:
        """Calculate portfolio equity curve"""
        # This is a simplified implementation
        # In practice, you'd need to align the equity curves and apply rebalancing
        
        all_equity_curves = []
        for result in individual_strategies.values():
            all_equity_curves.append(result.equity_curve)
        
        # Simple average for demonstration
        portfolio_equity = pd.concat(all_equity_curves, axis=1).mean(axis=1)
        
        return portfolio_equity
    
    def _calculate_portfolio_metrics(self, portfolio_equity: pd.Series, 
                                    individual_strategies: Dict[str, BacktestResult]) -> Dict[str, float]:
        """Calculate portfolio-level performance metrics"""
        # Use the same metrics as individual strategies
        return self._calculate_performance_metrics(portfolio_equity, [], StrategyConfig("portfolio", lambda x, y: None))
    
    def _cohens_d(self, group1: np.ndarray, group2: np.ndarray) -> float:
        """Calculate Cohen's d effect size"""
        n1, n2 = len(group1), len(group2)
        if n1 <= 1 or n2 <= 1:
            return 0.0
        
        mean1, mean2 = np.mean(group1), np.mean(group2)
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        
        if pooled_std == 0:
            return 0.0
        
        cohens_d = (mean1 - mean2) / pooled_std
        
        return cohens_d
    
    def _bootstrap_confidence_interval(self, group1: np.ndarray, group2: np.ndarray, 
                                     n_bootstrap: int = 1000, confidence: float = 0.95) -> Tuple[float, float]:
        """Bootstrap confidence interval for difference in means"""
        differences = []
        
        for _ in range(n_bootstrap):
            sample1 = np.random.choice(group1, size=len(group1), replace=True)
            sample2 = np.random.choice(group2, size=len(group2), replace=True)
            
            diff = np.mean(sample1) - np.mean(sample2)
            differences.append(diff)
        
        differences = np.array(differences)
        alpha = 1 - confidence
        
        lower = np.percentile(differences, 100 * alpha / 2)
        upper = np.percentile(differences, 100 * (1 - alpha / 2))
        
        return (lower, upper)
    
    def _generate_cache_key(self, strategy_config: StrategyConfig, data: pd.DataFrame, 
                           start_date: datetime, end_date: datetime) -> str:
        """Generate cache key for results"""
        # Create a unique key based on strategy config, data hash, and date range
        config_str = json.dumps({
            'name': strategy_config.name,
            'parameters': strategy_config.parameters,
            'timeframe': strategy_config.timeframe.value
        }, sort_keys=True)
        
        data_hash = hashlib.md5(data.values.tobytes()).hexdigest()
        
        date_str = f"{start_date}_{end_date}" if start_date and end_date else "all_dates"
        
        key_str = f"{config_str}_{data_hash}_{date_str}"
        
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _generate_html_report(self, results: List[BacktestResult], 
                             benchmark_results: List[BacktestResult],
                             monte_carlo_results: MonteCarloResult,
                             walk_forward_results: WalkForwardResult,
                             fig) -> str:
        """Generate HTML report content"""
        
        # Create summary table
        summary_rows = []
        for result in results:
            summary_rows.append(f"""
                <tr>
                    <td>{result.strategy_name}</td>
                    <td>{result.total_return:.2%}</td>
                    <td>{result.annualized_return:.2%}</td>
                    <td>{result.volatility:.2%}</td>
                    <td>{result.sharpe_ratio:.2f}</td>
                    <td>{result.max_drawdown:.2%}</td>
                    <td>{result.win_rate:.2%}</td>
                </tr>
            """)
        
        # Generate full HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pro Backtesting Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .summary-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .summary-table th, .summary-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .summary-table th {{ background-color: #f2f2f2; }}
                .chart-container {{ margin: 20px 0; }}
                .metric-section {{ margin: 30px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Pro Backtesting Engine - Comprehensive Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="metric-section">
                <h2>Performance Summary</h2>
                <table class="summary-table">
                    <thead>
                        <tr>
                            <th>Strategy</th>
                            <th>Total Return</th>
                            <th>Annualized Return</th>
                            <th>Volatility</th>
                            <th>Sharpe Ratio</th>
                            <th>Max Drawdown</th>
                            <th>Win Rate</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(summary_rows)}
                    </tbody>
                </table>
            </div>
            
            <div class="chart-container">
                {fig.to_html(include_plotlyjs='cdn', div_id="main-chart")}
            </div>
            
            <div class="metric-section">
                <h2>Monte Carlo Analysis</h2>
                {f'<p>Simulations: {monte_carlo_results.simulation_count}</p>' if monte_carlo_results else '<p>No Monte Carlo results available</p>'}
                {f'<p>Probability of Loss: {monte_carlo_results.probability_of_loss:.2%}</p>' if monte_carlo_results else ''}
                {f'<p>VaR (95%): {monte_carlo_results.var_95:.2%}</p>' if monte_carlo_results else ''}
            </div>
            
            <div class="metric-section">
                <h2>Walk-Forward Analysis</h2>
                {f'<p>Stability Score: {walk_forward_results.stability_score:.2f}</p>' if walk_forward_results else '<p>No walk-forward results available</p>'}
                {f'<p>Robustness Score: {walk_forward_results.robustness_score:.2f}</p>' if walk_forward_results else ''}
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    # Strategy examples
    
    @staticmethod
    def moving_average_strategy(data: pd.DataFrame, short_window: int = 20, long_window: int = 50) -> pd.DataFrame:
        """
        Simple moving average crossover strategy
        
        Args:
            data: Price data with OHLCV columns
            short_window: Short moving average period
            long_window: Long moving average period
            
        Returns:
            DataFrame with signals
        """
        signals = data.copy()
        
        # Calculate moving averages
        signals['short_ma'] = data['close'].rolling(window=short_window).mean()
        signals['long_ma'] = data['close'].rolling(window=long_window).mean()
        
        # Generate signals
        signals['signal'] = 0
        signals['signal'][short_window:] = np.where(
            signals['short_ma'][short_window:] > signals['long_ma'][short_window:], 1, -1
        )
        
        return signals[['signal']]
    
    @staticmethod
    def rsi_strategy(data: pd.DataFrame, rsi_period: int = 14, oversold: float = 30, 
                    overbought: float = 70) -> pd.DataFrame:
        """
        RSI-based mean reversion strategy
        
        Args:
            data: Price data
            rsi_period: RSI calculation period
            oversold: Oversold threshold
            overbought: Overbought threshold
            
        Returns:
            DataFrame with signals
        """
        signals = data.copy()
        
        # Calculate RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
        
        rs = gain / loss
        signals['rsi'] = 100 - (100 / (1 + rs))
        
        # Generate signals
        signals['signal'] = 0
        signals['signal'] = np.where(signals['rsi'] < oversold, 1, 
                                   np.where(signals['rsi'] > overbought, -1, 0))
        
        return signals[['signal']]
    
    @staticmethod
    def momentum_strategy(data: pd.DataFrame, lookback_period: int = 20) -> pd.DataFrame:
        """
        Simple momentum strategy based on price changes
        
        Args:
            data: Price data
            lookback_period: Period for momentum calculation
            
        Returns:
            DataFrame with signals
        """
        signals = data.copy()
        
        # Calculate momentum
        signals['momentum'] = data['close'].pct_change(lookback_period)
        
        # Generate signals
        signals['signal'] = 0
        signals['signal'] = np.where(signals['momentum'] > 0.05, 1, 
                                   np.where(signals['momentum'] < -0.05, -1, 0))
        
        return signals[['signal']]


# Example usage and testing functions

def create_sample_data(symbol: str = "AAPL", start_date: str = "2010-01-01", 
                      end_date: str = "2023-12-31", frequency: str = "D") -> pd.DataFrame:
    """
    Create sample price data for testing
    
    Args:
        symbol: Stock symbol
        start_date: Start date
        end_date: End date
        frequency: Data frequency
        
    Returns:
        DataFrame with OHLCV data
    """
    # Generate date range
    dates = pd.date_range(start=start_date, end=end_date, freq=frequency)
    
    # Generate synthetic price data
    np.random.seed(42)  # For reproducible results
    
    n_periods = len(dates)
    
    # Generate returns using random walk with drift
    returns = np.random.normal(0.0005, 0.02, n_periods)  # Daily returns
    
    # Calculate prices
    prices = [100.0]  # Starting price
    for return_rate in returns[1:]:
        prices.append(prices[-1] * (1 + return_rate))
    
    # Generate OHLC data
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        # Generate realistic OHLC based on close price
        high_offset = np.random.uniform(0.001, 0.03)
        low_offset = np.random.uniform(0.001, 0.03)
        
        high = close * (1 + high_offset)
        low = close * (1 - low_offset)
        
        # Open is previous close with some noise
        if i > 0:
            open_price = data[i-1]['close'] * np.random.uniform(0.99, 1.01)
        else:
            open_price = close
        
        # Volume
        volume = np.random.randint(1000000, 10000000)
        
        data.append({
            'timestamp': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    # Add volatility column
    df['volatility'] = df['close'].pct_change().rolling(window=20).std()
    
    return df


def demo_pro_backtesting():
    """
    Demonstrate Pro Backtesting Engine functionality
    """
    print("=== Pro Backtesting Engine Demo ===\n")
    
    # Create sample data
    print("1. Creating sample data...")
    data = create_sample_data()
    print(f"Data shape: {data.shape}")
    print(f"Date range: {data.index[0]} to {data.index[-1]}\n")
    
    # Initialize engine
    print("2. Initializing backtesting engine...")
    engine = ProBacktestingEngine()
    
    # Create strategy configurations
    print("3. Creating strategy configurations...")
    
    ma_strategy = StrategyConfig(
        name="Moving Average Strategy",
        strategy_function=ProBacktestingEngine.moving_average_strategy,
        parameters={'short_window': 20, 'long_window': 50},
        initial_capital=100000,
        commission=0.001,
        slippage=0.0005
    )
    
    rsi_strategy = StrategyConfig(
        name="RSI Strategy", 
        strategy_function=ProBacktestingEngine.rsi_strategy,
        parameters={'rsi_period': 14, 'oversold': 30, 'overbought': 70},
        initial_capital=100000,
        commission=0.001,
        slippage=0.0005
    )
    
    momentum_strategy = StrategyConfig(
        name="Momentum Strategy",
        strategy_function=ProBacktestingEngine.momentum_strategy,
        parameters={'lookback_period': 20},
        initial_capital=100000,
        commission=0.001,
        slippage=0.0005
    )
    
    strategies = [ma_strategy, rsi_strategy, momentum_strategy]
    
    # Run multiple strategies
    print("4. Running multiple strategies...")
    results = engine.run_multiple_strategies(strategies, data, parallel=True)
    
    print("\nStrategy Performance Summary:")
    print("-" * 80)
    for result in results:
        print(f"{result.strategy_name:20} | "
              f"Return: {result.total_return:8.2%} | "
              f"Sharpe: {result.sharpe_ratio:6.2f} | "
              f"Max DD: {result.max_drawdown:8.2%} | "
              f"Trades: {result.total_trades:4d}")
    
    # Parameter optimization
    print("\n5. Running parameter optimization...")
    ma_optimized_params, ma_optimized_result = engine.optimize_strategy_parameters(
        ma_strategy, data,
        parameter_ranges={'short_window': [10, 20, 30], 'long_window': [40, 50, 60]},
        optimization_method=OptimizationMethod.GRID_SEARCH,
        objective='sharpe_ratio'
    )
    
    print(f"Optimized parameters: {ma_optimized_params}")
    print(f"Optimized Sharpe ratio: {ma_optimized_result.sharpe_ratio:.2f}")
    
    # Monte Carlo simulation
    print("\n6. Running Monte Carlo simulation...")
    mc_result = engine.run_monte_carlo_simulation(
        ma_strategy, data, num_simulations=100, bootstrap_method='block'
    )
    
    print(f"Monte Carlo results:")
    print(f"  Probability of loss: {mc_result.probability_of_loss:.2%}")
    print(f"  VaR (95%): {mc_result.var_95:.2%}")
    print(f"  CVaR (95%): {mc_result.cvar_95:.2%}")
    
    # Walk-forward analysis
    print("\n7. Running walk-forward analysis...")
    wf_result = engine.run_walk_forward_analysis(
        ma_strategy, data, in_sample_period=252, out_of_sample_period=63
    )
    
    print(f"Walk-forward results:")
    print(f"  Stability score: {wf_result.stability_score:.2f}")
    print(f"  Robustness score: {wf_result.robustness_score:.2f}")
    
    # Generate comprehensive report
    print("\n8. Generating comprehensive report...")
    report_html = engine.generate_comprehensive_report(
        results, save_path="/tmp/backtest_report.html"
    )
    print(f"Report saved to: /tmp/backtest_report.html")
    
    # Multi-timeframe analysis demo
    print("\n9. Running multi-timeframe analysis...")
    data_dict = {
        TimeFrame.D1: data,
        TimeFrame.H4: data.resample('4H').last().dropna(),
        TimeFrame.H1: data.resample('1H').last().dropna()
    }
    
    # Adjust data for different timeframes (simplified)
    for tf in data_dict:
        if tf != TimeFrame.D1:
            data_dict[tf] = data_dict[TimeFrame.D1].copy()  # Simplified for demo
    
    tf_results = engine.run_multi_timeframe_analysis(
        [ma_strategy, rsi_strategy], data_dict
    )
    
    print("Multi-timeframe results:")
    for timeframe, result in tf_results.items():
        print(f"  {timeframe}: Return {result.total_return:.2%}, Sharpe {result.sharpe_ratio:.2f}")
    
    print("\n=== Demo completed successfully! ===")


if __name__ == "__main__":
    # Run demo
    demo_pro_backtesting()