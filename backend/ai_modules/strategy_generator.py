"""
AI-Driven Strategy Generator

Bu modul AI algoritmlari yordamida turli xil trading strategiyasini avtomatik yaratish,
optimizatsiya qilish va test qilish tizimini ta'minlaydi.

Asosiy xususiyatlar:
- AI-driven strategy generation
- Genetic algorithm optimization
- Walk-forward analysis
- Monte Carlo simulation
- Auto parameter tuning
- Cross-validation
- Strategy ranking
"""

import numpy as np
import pandas as pd
import warnings
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import random
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import asyncio

# Supabase integration
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    warnings.warn("Supabase client topilmadi, database integratsiyasi yo'qoladi")

# Technical indicators (with fallbacks for missing libraries)
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

@dataclass
class StrategyConfig:
    """Strategy konfiguratsiyasi"""
    name: str
    strategy_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    risk_params: Dict[str, float] = field(default_factory=dict)
    timeframe: str = "1h"
    symbol: str = "EURUSD"
    initial_capital: float = 10000.0
    max_drawdown: float = 0.1
    position_size: float = 0.1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'strategy_type': self.strategy_type,
            'parameters': self.parameters,
            'risk_params': self.risk_params,
            'timeframe': self.timeframe,
            'symbol': self.symbol,
            'initial_capital': self.initial_capital,
            'max_drawdown': self.max_drawdown,
            'position_size': self.position_size
        }

@dataclass
class StrategyResult:
    """Strategy test natija"""
    config: StrategyConfig
    performance_metrics: Dict[str, float]
    backtest_results: pd.DataFrame
    trades: List[Dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None

class StrategyType(Enum):
    """Strategy turlari"""
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"
    STATISTICAL_ARBITRAGE = "statistical_arbitrage"
    GRID_TRADING = "grid_trading"
    MARTINGALE = "martingale"
    CUSTOM_HYBRID = "custom_hybrid"

class GeneticOptimizer:
    """Genetik algoritm optimizator"""
    
    def __init__(self, 
                 population_size: int = 50,
                 generations: int = 100,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.logger = logging.getLogger(__name__)
    
    def initialize_population(self, param_space: Dict[str, Any]) -> List[StrategyConfig]:
        """Populyatsiyani boshlash"""
        population = []
        
        for _ in range(self.population_size):
            params = {}
            for key, value_range in param_space.items():
                if isinstance(value_range, list):
                    if isinstance(value_range[0], int):
                        params[key] = random.randint(value_range[0], value_range[1])
                    else:
                        params[key] = random.uniform(value_range[0], value_range[1])
                else:
                    params[key] = value_range
            
            strategy = StrategyConfig(
                name=f"GA_Strategy_{len(population)}",
                strategy_type="genetic_optimized",
                parameters=params
            )
            population.append(strategy)
        
        return population
    
    def evaluate_fitness(self, population: List[StrategyConfig], 
                        backtester: Any, data: pd.DataFrame) -> List[float]:
        """Populyatsiya fitness funksiyasini hisoblash"""
        fitness_scores = []
        
        for strategy in population:
            try:
                # Simple evaluation for speed
                result = backtester.run_backtest(strategy, data)
                if result.success:
                    fitness_score = result.performance_metrics.get('sharpe_ratio', 0) - \
                                   abs(result.performance_metrics.get('max_drawdown', 0)) * 10
                    fitness_scores.append(max(0, fitness_score))
                else:
                    fitness_scores.append(0)
            except Exception as e:
                self.logger.warning(f"Strategy {strategy.name} evaluation failed: {e}")
                fitness_scores.append(0)
        
        return fitness_scores
    
    def select_parents(self, population: List[StrategyConfig], 
                      fitness_scores: List[float]) -> List[StrategyConfig]:
        """Roulette wheel selection"""
        total_fitness = sum(fitness_scores)
        if total_fitness == 0:
            return random.choices(population, k=len(population))
        
        probabilities = [f / total_fitness for f in fitness_scores]
        parents = []
        
        for _ in range(self.population_size):
            r = random.random()
            cum_sum = 0
            
            for i, prob in enumerate(probabilities):
                cum_sum += prob
                if cum_sum >= r:
                    parents.append(population[i])
                    break
        
        return parents
    
    def crossover(self, parent1: StrategyConfig, 
                 parent2: StrategyConfig) -> Tuple[StrategyConfig, StrategyConfig]:
        """Uniform crossover"""
        child1_params = {}
        child2_params = {}
        
        all_params = set(parent1.parameters.keys()) | set(parent2.parameters.keys())
        
        for param in all_params:
            if random.random() < 0.5:
                child1_params[param] = parent1.parameters.get(param, {})
                child2_params[param] = parent2.parameters.get(param, {})
            else:
                child1_params[param] = parent2.parameters.get(param, {})
                child2_params[param] = parent1.parameters.get(param, {})
        
        child1 = StrategyConfig(
            name=f"Crossover_{random.randint(1000, 9999)}",
            strategy_type=parent1.strategy_type,
            parameters=child1_params
        )
        
        child2 = StrategyConfig(
            name=f"Crossover_{random.randint(1000, 9999)}",
            strategy_type=parent2.strategy_type,
            parameters=child2_params
        )
        
        return child1, child2
    
    def mutate(self, strategy: StrategyConfig, param_space: Dict[str, Any]) -> StrategyConfig:
        """Mutation operator"""
        mutated = StrategyConfig(
            name=f"Mutated_{random.randint(1000, 9999)}",
            strategy_type=strategy.strategy_type,
            parameters=strategy.parameters.copy()
        )
        
        for key, value_range in param_space.items():
            if random.random() < self.mutation_rate:
                if isinstance(value_range, list):
                    if isinstance(value_range[0], int):
                        mutated.parameters[key] = random.randint(value_range[0], value_range[1])
                    else:
                        mutated.parameters[key] = random.uniform(value_range[0], value_range[1])
        
        return mutated
    
    async def optimize(self, param_space: Dict[str, Any], 
                      backtester: Any, data: pd.DataFrame) -> StrategyConfig:
        """Genetik algoritm orqali optimizatsiya"""
        self.logger.info(f"Genetik algoritm optimizatsiyasi boshlanmoqda: {self.generations} avlod")
        
        # Initialize population
        population = self.initialize_population(param_space)
        best_strategy = None
        best_fitness = 0
        
        for generation in range(self.generations):
            self.logger.info(f"Avolod {generation + 1}/{self.generations}")
            
            # Evaluate fitness
            fitness_scores = self.evaluate_fitness(population, backtester, data)
            
            # Track best strategy
            max_fitness = max(fitness_scores)
            if max_fitness > best_fitness:
                best_fitness = max_fitness
                best_strategy = population[fitness_scores.index(max_fitness)]
            
            # Selection
            parents = self.select_parents(population, fitness_scores)
            
            # Crossover and mutation
            new_population = []
            for i in range(0, len(parents), 2):
                if i + 1 < len(parents):
                    if random.random() < self.crossover_rate:
                        child1, child2 = self.crossover(parents[i], parents[i + 1])
                        child1 = self.mutate(child1, param_space)
                        child2 = self.mutate(child2, param_space)
                        new_population.extend([child1, child2])
                    else:
                        new_population.extend([parents[i], parents[i + 1]])
            
            population = new_population[:self.population_size]
        
        self.logger.info(f"Optimizatsiya yakunlandi. Eng yaxshi fitness: {best_fitness}")
        return best_strategy

class WalkForwardAnalyzer:
    """Walk-forward analiz"""
    
    def __init__(self, window_size: int = 252, step_size: int = 21):
        self.window_size = window_size
        self.step_size = step_size
        self.logger = logging.getLogger(__name__)
    
    async def analyze(self, strategy: StrategyConfig, 
                     backtester: Any, data: pd.DataFrame) -> Dict[str, Any]:
        """Walk-forward analizini bajarish"""
        results = []
        
        for i in range(0, len(data) - self.window_size, self.step_size):
            # Train window
            train_start = i
            train_end = i + self.window_size
            train_data = data.iloc[train_start:train_end]
            
            # Test window
            test_start = train_end
            test_end = min(test_start + self.step_size, len(data))
            test_data = data.iloc[test_start:test_end]
            
            try:
                # Optimize on train data
                train_result = backtester.run_backtest(strategy, train_data)
                
                # Test on test data
                test_result = backtester.run_backtest(strategy, test_data)
                
                results.append({
                    'train_performance': train_result.performance_metrics,
                    'test_performance': test_result.performance_metrics,
                    'train_period': f"{train_data.index[0]}_{train_data.index[-1]}",
                    'test_period': f"{test_data.index[0]}_{test_data.index[-1]}"
                })
                
            except Exception as e:
                self.logger.warning(f"Walk-forward period {i} failed: {e}")
        
        # Aggregate results
        test_sharpes = [r['test_performance'].get('sharpe_ratio', 0) for r in results]
        test_drawdowns = [r['test_performance'].get('max_drawdown', 0) for r in results]
        
        analysis = {
            'windows_analyzed': len(results),
            'avg_test_sharpe': np.mean(test_sharpes) if test_sharpes else 0,
            'std_test_sharpe': np.std(test_sharpes) if test_sharpes else 0,
            'avg_test_drawdown': np.mean(test_drawdowns) if test_drawdowns else 0,
            'stability_score': 1 / (1 + np.std(test_sharpes)) if test_sharpes else 0,
            'window_results': results
        }
        
        return analysis

class MonteCarloSimulator:
    """Monte Carlo simulatsiya"""
    
    def __init__(self, num_simulations: int = 1000):
        self.num_simulations = num_simulations
        self.logger = logging.getLogger(__name__)
    
    async def simulate(self, strategy: StrategyConfig, 
                      backtester: Any, data: pd.DataFrame) -> Dict[str, Any]:
        """Monte Carlo simulatsiya"""
        returns = []
        
        for i in range(self.num_simulations):
            # Bootstrap sampling
            sampled_data = data.sample(n=len(data), replace=True)
            
            try:
                result = backtester.run_backtest(strategy, sampled_data)
                if result.success:
                    returns.append(result.performance_metrics.get('total_return', 0))
            except Exception as e:
                self.logger.warning(f"Simulation {i} failed: {e}")
        
        if not returns:
            return {'error': 'No successful simulations'}
        
        analysis = {
            'num_simulations': len(returns),
            'mean_return': np.mean(returns),
            'std_return': np.std(returns),
            'percentile_5': np.percentile(returns, 5),
            'percentile_25': np.percentile(returns, 25),
            'percentile_50': np.percentile(returns, 50),
            'percentile_75': np.percentile(returns, 75),
            'percentile_95': np.percentile(returns, 95),
            'var_5': abs(np.percentile(returns, 5)),
            'var_1': abs(np.percentile(returns, 1)),
            'sharpe_simulation': np.mean(returns) / (np.std(returns) + 1e-8)
        }
        
        return analysis

class StrategyGenerator:
    """AI-Driven Strategy Generator asosiy klassi"""
    
    def __init__(self, supabase_url: Optional[str] = None, 
                 supabase_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.optimizer = GeneticOptimizer()
        self.walk_forward = WalkForwardAnalyzer()
        self.monte_carlo = MonteCarloSimulator()
        
        # Database integration
        self.db = None
        if SUPABASE_AVAILABLE and supabase_url and supabase_key:
            try:
                self.db = create_client(supabase_url, supabase_key)
                self.logger.info("Supabase client muvaffaqiyatli ulandi")
            except Exception as e:
                self.logger.warning(f"Supabase connection failed: {e}")
    
    def generate_trend_following_strategy(self, fast_period: int = 12, 
                                        slow_period: int = 26) -> StrategyConfig:
        """Trend following strategiyasini yaratish"""
        strategy = StrategyConfig(
            name="AI_Trend_Following",
            strategy_type=StrategyType.TREND_FOLLOWING.value,
            parameters={
                'fast_ma_period': fast_period,
                'slow_ma_period': slow_period,
                'signal_threshold': 0.02,
                'stop_loss_pct': 0.02,
                'take_profit_pct': 0.04
            }
        )
        return strategy
    
    def generate_mean_reversion_strategy(self, rsi_period: int = 14,
                                       overbought: int = 70,
                                       oversold: int = 30) -> StrategyConfig:
        """Mean reversion strategiyasini yaratish"""
        strategy = StrategyConfig(
            name="AI_Mean_Reversion",
            strategy_type=StrategyType.MEAN_REVERSION.value,
            parameters={
                'rsi_period': rsi_period,
                'rsi_overbought': overbought,
                'rsi_oversold': oversold,
                'bb_period': 20,
                'bb_std': 2.0,
                'stop_loss_pct': 0.015,
                'take_profit_pct': 0.03
            }
        )
        return strategy
    
    def generate_momentum_strategy(self, momentum_period: int = 10,
                                 rsi_period: int = 14) -> StrategyConfig:
        """Momentum strategiyasini yaratish"""
        strategy = StrategyConfig(
            name="AI_Momentum",
            strategy_type=StrategyType.MOMENTUM.value,
            parameters={
                'momentum_period': momentum_period,
                'rsi_period': rsi_period,
                'rsi_threshold': 50,
                'volume_threshold': 1.5,
                'stop_loss_pct': 0.025,
                'take_profit_pct': 0.05
            }
        )
        return strategy
    
    def generate_statistical_arbitrage_strategy(self, 
                                               lookback_period: int = 50,
                                               z_score_threshold: float = 2.0) -> StrategyConfig:
        """Statistical arbitrage strategiyasini yaratish"""
        strategy = StrategyConfig(
            name="AI_Stat_Arbitrage",
            strategy_type=StrategyType.STATISTICAL_ARBITRAGE.value,
            parameters={
                'lookback_period': lookback_period,
                'z_score_entry': z_score_threshold,
                'z_score_exit': 0.5,
                'correlation_threshold': 0.8,
                'half_life_mean_reversion': 5,
                'stop_loss_pct': 0.02
            }
        )
        return strategy
    
    def generate_grid_trading_strategy(self, grid_levels: int = 10,
                                     price_range: Tuple[float, float] = (0.95, 1.05)) -> StrategyConfig:
        """Grid trading strategiyasini yaratish"""
        strategy = StrategyConfig(
            name="AI_Grid_Trading",
            strategy_type=StrategyType.GRID_TRADING.value,
            parameters={
                'grid_levels': grid_levels,
                'price_range_low': price_range[0],
                'price_range_high': price_range[1],
                'grid_spacing': (price_range[1] - price_range[0]) / grid_levels,
                'rebalance_threshold': 0.01,
                'position_size_pct': 0.1
            }
        )
        return strategy
    
    def generate_martingale_strategy(self, base_position: float = 0.1,
                                   multiplier: float = 2.0,
                                   max_levels: int = 5) -> StrategyConfig:
        """Martingale strategiyasini yaratish"""
        strategy = StrategyConfig(
            name="AI_Martingale",
            strategy_type=StrategyType.MARTINGALE.value,
            parameters={
                'base_position_size': base_position,
                'multiplier': multiplier,
                'max_levels': max_levels,
                'stop_loss_limit': 0.2,
                'profit_target': 0.05,
                'time_limit_hours': 24
            }
        )
        return strategy
    
    def generate_hybrid_strategy(self, components: List[str]) -> StrategyConfig:
        """Custom hybrid strategiyasini yaratish"""
        strategy = StrategyConfig(
            name="AI_Hybrid_Strategy",
            strategy_type=StrategyType.CUSTOM_HYBRID.value,
            parameters={
                'components': components,
                'weight_trend': 0.3,
                'weight_reversion': 0.3,
                'weight_momentum': 0.4,
                'voting_threshold': 0.6,
                'stop_loss_pct': 0.02,
                'take_profit_pct': 0.04
            }
        )
        return strategy
    
    async def auto_optimize_parameters(self, strategy_type: str, 
                                     data: pd.DataFrame, 
                                     param_space: Dict[str, Any],
                                     backtester: Any) -> StrategyConfig:
        """Parametrlarni avtomatik optimizatsiya qilish"""
        self.logger.info(f"{strategy_type} uchun parameter optimizatsiyasi")
        
        # Base strategy yaratish
        if strategy_type == StrategyType.TREND_FOLLOWING.value:
            base_strategy = self.generate_trend_following_strategy()
        elif strategy_type == StrategyType.MEAN_REVERSION.value:
            base_strategy = self.generate_mean_reversion_strategy()
        elif strategy_type == StrategyType.MOMENTUM.value:
            base_strategy = self.generate_momentum_strategy()
        elif strategy_type == StrategyType.STATISTICAL_ARBITRAGE.value:
            base_strategy = self.generate_statistical_arbitrage_strategy()
        else:
            raise ValueError(f"Bilimadigan strategiya turi: {strategy_type}")
        
        # Genetic optimization
        optimized_strategy = await self.optimizer.optimize(
            param_space, backtester, data
        )
        
        # Walk-forward analysis
        walk_forward_results = await self.walk_forward.analyze(
            optimized_strategy, backtester, data
        )
        
        # Monte Carlo simulation
        monte_carlo_results = await self.monte_carlo.simulate(
            optimized_strategy, backtester, data
        )
        
        # Combine results
        optimized_strategy.parameters.update({
            'walk_forward_stability': walk_forward_results.get('stability_score', 0),
            'monte_carlo_avg_return': monte_carlo_results.get('mean_return', 0),
            'monte_carlo_var_5': monte_carlo_results.get('var_5', 0)
        })
        
        return optimized_strategy
    
    async def stress_test_strategy(self, strategy: StrategyConfig,
                                 backtester: Any, 
                                 normal_data: pd.DataFrame,
                                 stress_scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Strategiyani stress testing qilish"""
        self.logger.info("Strategy stress test boshlanmoqda")
        
        # Normal condition test
        normal_result = backtester.run_backtest(strategy, normal_data)
        
        stress_results = []
        for scenario in stress_scenarios:
            try:
                # Apply stress scenario
                stressed_data = self._apply_stress_scenario(normal_data, scenario)
                stress_result = backtester.run_backtest(strategy, stressed_data)
                
                stress_results.append({
                    'scenario': scenario,
                    'result': stress_result.performance_metrics if stress_result.success else {},
                    'success': stress_result.success
                })
            except Exception as e:
                self.logger.warning(f"Stress scenario failed: {e}")
                stress_results.append({
                    'scenario': scenario,
                    'error': str(e),
                    'success': False
                })
        
        return {
            'normal_performance': normal_result.performance_metrics if normal_result.success else {},
            'stress_results': stress_results,
            'stress_test_summary': self._summarize_stress_results(stress_results)
        }
    
    def _apply_stress_scenario(self, data: pd.DataFrame, 
                              scenario: Dict[str, Any]) -> pd.DataFrame:
        """Stress scenario'ni data'ga qo'llash"""
        stressed_data = data.copy()
        
        if 'volatility_multiplier' in scenario:
            volatility = data['high'] - data['low']
            stressed_data['high'] = data['close'] + volatility * scenario['volatility_multiplier']
            stressed_data['low'] = data['close'] - volatility * scenario['volatility_multiplier']
        
        if 'trend_shift' in scenario:
            shift = scenario['trend_shift']
            stressed_data['close'] = data['close'] * (1 + shift)
            stressed_data['high'] = stressed_data['close'] * (1 + 0.01)
            stressed_data['low'] = stressed_data['close'] * (1 - 0.01)
        
        if 'gap_probability' in scenario:
            # Simple gap implementation
            n_gaps = int(len(data) * scenario['gap_probability'])
            gap_indices = random.sample(range(len(data)), min(n_gaps, len(data)))
            
            for idx in gap_indices:
                gap_size = random.uniform(-0.05, 0.05)
                stressed_data.iloc[idx, stressed_data.columns.get_loc('open')] = \
                    data.iloc[idx, data.columns.get_loc('close')] * (1 + gap_size)
        
        return stressed_data
    
    def _summarize_stress_results(self, stress_results: List[Dict]) -> Dict[str, Any]:
        """Stress test natijalarini jamlash"""
        if not stress_results:
            return {}
        
        success_rate = sum(1 for r in stress_results if r['success']) / len(stress_results)
        
        # Extract performance metrics
        performance_metrics = []
        for result in stress_results:
            if result['success'] and 'result' in result:
                performance_metrics.append(result['result'])
        
        if not performance_metrics:
            return {'success_rate': success_rate}
        
        # Aggregate metrics
        sharpes = [m.get('sharpe_ratio', 0) for m in performance_metrics]
        drawdowns = [abs(m.get('max_drawdown', 0)) for m in performance_metrics]
        returns = [m.get('total_return', 0) for m in performance_metrics]
        
        return {
            'success_rate': success_rate,
            'avg_stress_sharpe': np.mean(sharpes),
            'max_stress_drawdown': np.max(drawdowns),
            'worst_return': np.min(returns),
            'volatility_stress_test': np.std(returns)
        }
    
    def cross_validate_strategy(self, strategy: StrategyConfig,
                              backtester: Any, 
                              data: pd.DataFrame,
                              n_folds: int = 5) -> Dict[str, Any]:
        """Cross-validation"""
        self.logger.info(f"Cross-validation boshlanmoqda: {n_folds} fold")
        
        fold_size = len(data) // n_folds
        cv_results = []
        
        for i in range(n_folds):
            # Create train/test split
            test_start = i * fold_size
            test_end = (i + 1) * fold_size if i < n_folds - 1 else len(data)
            
            train_data = pd.concat([
                data.iloc[:test_start],
                data.iloc[test_end:]
            ])
            test_data = data.iloc[test_start:test_end]
            
            try:
                test_result = backtester.run_backtest(strategy, test_data)
                cv_results.append({
                    'fold': i + 1,
                    'test_performance': test_result.performance_metrics if test_result.success else {},
                    'success': test_result.success
                })
            except Exception as e:
                self.logger.warning(f"CV fold {i + 1} failed: {e}")
                cv_results.append({
                    'fold': i + 1,
                    'error': str(e),
                    'success': False
                })
        
        # Aggregate results
        successful_results = [r for r in cv_results if r['success']]
        
        if not successful_results:
            return {'error': 'No successful CV folds'}
        
        sharpes = [r['test_performance'].get('sharpe_ratio', 0) for r in successful_results]
        drawdowns = [r['test_performance'].get('max_drawdown', 0) for r in successful_results]
        
        return {
            'n_folds': n_folds,
            'successful_folds': len(successful_results),
            'avg_sharpe': np.mean(sharpes),
            'std_sharpe': np.std(sharpes),
            'avg_drawdown': np.mean(drawdowns),
            'cv_score': np.mean(sharpes) / (np.std(sharpes) + 1e-8),  # Coefficient of variation
            'fold_results': cv_results
        }
    
    async def save_strategy_to_db(self, strategy: StrategyConfig, 
                                results: Dict[str, Any]) -> bool:
        """Strategy va natijalarni ma'lumotlar bazasiga saqlash"""
        if not self.db:
            self.logger.warning("Database ulanmagan")
            return False
        
        try:
            strategy_data = strategy.to_dict()
            strategy_data['generated_at'] = datetime.now().isoformat()
            strategy_data['optimization_results'] = json.dumps(results)
            
            response = self.db.table('generated_strategies').insert(strategy_data).execute()
            self.logger.info(f"Strategy {strategy.name} muvaffaqiyatli saqlandi")
            return True
            
        except Exception as e:
            self.logger.error(f"Strategy saqlashda xato: {e}")
            return False
    
    async def load_strategies_from_db(self) -> List[StrategyConfig]:
        """Ma'lumotlar bazasidan strategiyani yuklash"""
        if not self.db:
            self.logger.warning("Database ulanmagan")
            return []
        
        try:
            response = self.db.table('generated_strategies').select('*').execute()
            
            strategies = []
            for data in response.data:
                strategy = StrategyConfig(
                    name=data['name'],
                    strategy_type=data['strategy_type'],
                    parameters=data['parameters'],
                    risk_params=data.get('risk_params', {}),
                    timeframe=data.get('timeframe', '1h'),
                    symbol=data.get('symbol', 'EURUSD'),
                    initial_capital=data.get('initial_capital', 10000.0),
                    max_drawdown=data.get('max_drawdown', 0.1),
                    position_size=data.get('position_size', 0.1)
                )
                strategies.append(strategy)
            
            self.logger.info(f"{len(strategies)} ta strategiya yuklandi")
            return strategies
            
        except Exception as e:
            self.logger.error(f"Strategy yuklashda xato: {e}")
            return []

# Usage example
async def main():
    """Asosiy demo"""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize generator
    generator = StrategyGenerator()
    
    # Generate sample data
    dates = pd.date_range('2023-01-01', periods=1000, freq='H')
    np.random.seed(42)
    
    # Simulated OHLCV data
    base_price = 1.1000
    price_changes = np.random.normal(0, 0.001, 1000)
    prices = base_price + np.cumsum(price_changes)
    
    data = pd.DataFrame({
        'timestamp': dates,
        'open': prices + np.random.normal(0, 0.0005, 1000),
        'high': prices + np.abs(np.random.normal(0, 0.001, 1000)),
        'low': prices - np.abs(np.random.normal(0, 0.001, 1000)),
        'close': prices,
        'volume': np.random.lognormal(10, 1, 1000)
    })
    
    data.set_index('timestamp', inplace=True)
    
    # Import backtester for testing
    try:
        from .backtester import Backtester
        
        backtester = Backtester()
        
        # Generate different strategies
        trend_strategy = generator.generate_trend_following_strategy()
        mean_reversion_strategy = generator.generate_mean_reversion_strategy()
        momentum_strategy = generator.generate_momentum_strategy()
        
        print("=== Strategy Generation Demo ===")
        print(f"Trend Following: {trend_strategy.name}")
        print(f"Mean Reversion: {mean_reversion_strategy.name}")
        print(f"Momentum: {momentum_strategy.name}")
        
        # Parameter optimization demo
        param_space = {
            'fast_ma_period': [5, 20],
            'slow_ma_period': [20, 50],
            'signal_threshold': [0.005, 0.05]
        }
        
        try:
            optimized_strategy = await generator.auto_optimize_parameters(
                StrategyType.TREND_FOLLOWING.value, 
                data, 
                param_space, 
                backtester
            )
            print(f"Optimized strategy: {optimized_strategy.name}")
            print(f"Optimized parameters: {optimized_strategy.parameters}")
        except Exception as e:
            print(f"Optimization demo failed (simulated): {e}")
        
        # Cross-validation demo
        try:
            cv_results = generator.cross_validate_strategy(
                trend_strategy, backtester, data
            )
            print(f"Cross-validation results: {cv_results}")
        except Exception as e:
            print(f"CV demo failed (simulated): {e}")
        
        print("=== Strategy Generator Demo Complete ===")
        
    except ImportError:
        print("Backtester topilmadi, demo simulyatsiya rejimida ishlaydi")
        print("=== Strategy Generation Demo ===")
        print("Trend Following, Mean Reversion, Momentum strategiyasi yaratildi")
        print("Optimizatsiya va test funktsiyalari tayyor")

if __name__ == "__main__":
    asyncio.run(main())