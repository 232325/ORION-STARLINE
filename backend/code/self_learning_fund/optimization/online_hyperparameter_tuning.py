"""
Online Hyperparameter Tuning for Self-Learning Trading Fund
==========================================================

Real-time model hyperparameter optimallashtirish va tuning.
Model performance ni real vaqtda kuzatish va optimallashtirish.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Callable, Union
from datetime import datetime, timedelta
import warnings
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import deque, defaultdict
import json
import pickle
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..core.base_algorithm import BaseAlgorithm
from ..core.adaptive_model import AdaptiveModel
from ..core.performance_tracker import PerformanceTracker

class TuningStrategy(Enum):
    """Hyperparameter tuning strategiyasi"""
    GRID_SEARCH = "Grid_Search"
    RANDOM_SEARCH = "Random_Search"
    BAYESIAN_OPTIMIZATION = "Bayesian_Optimization"
    GENETIC_ALGORITHM = "Genetic_Algorithm"
    ADAPTIVE_SEARCH = "Adaptive_Search"
    ENSEMBLE_TUNING = "Ensemble_Tuning"

class SearchSpace(Enum):
    """Qidirish fazosi turi"""
    CONTINUOUS = "Continuous"
    DISCRETE = "Discrete"
    CATEGORICAL = "Categorical"
    LOGARITHMIC = "Logarithmic"

class ConvergenceState(Enum):
    """Konvergentsiya holati"""
    CONVERGING = "Converging"
    STAGNANT = "Stagnant"
    EXPLORING = "Exploring"
    CONVERGED = "Converged"

@dataclass
class HyperparameterRange:
    """Hyperparameter diapazoni"""
    name: str
    param_type: SearchSpace
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    discrete_values: Optional[List[Any]] = None
    categorical_values: Optional[List[str]] = None
    log_scale: bool = False
    step_size: Optional[float] = None

@dataclass
class HyperparameterSet:
    """Hyperparameter to'plami"""
    values: Dict[str, Any]
    performance_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    training_time: float = 0.0
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TuningConfiguration:
    """Tuning konfiguratsiyasi"""
    strategy: TuningStrategy
    search_space: Dict[str, HyperparameterRange]
    max_iterations: int = 100
    convergence_threshold: float = 0.01
    max_training_time: float = 3600.0  # 1 hour
    early_stopping_rounds: int = 10
    validation_split: float = 0.2
    cross_validation_folds: int = 5
    parallel_evaluations: int = 1

class OnlineHyperparameterTuner:
    """Online hyperparameter tuneri"""
    
    def __init__(self, config: TuningConfiguration):
        self.config = config
        self.search_history: List[HyperparameterSet] = []
        self.best_hyperparameters: Optional[HyperparameterSet] = None
        self.convergence_state = ConvergenceState.EXPLORING
        self.performance_tracker = PerformanceTracker()
        
        # Search tracking
        self.evaluated_combinations = set()
        self.iteration_count = 0
        self.stagnation_counter = 0
        self.last_improvement = 0
        
    def tune_hyperparameters(self, objective_function: Callable, 
                           initial_hyperparameters: Dict[str, Any]) -> HyperparameterSet:
        """Hyperparameter tuning"""
        
        logging.info(f"Starting hyperparameter tuning with {self.config.strategy.value}")
        
        # Initialize with provided hyperparameters
        initial_set = HyperparameterSet(values=initial_hyperparameters)
        self.search_history.append(initial_set)
        self.evaluated_combinations.add(self._hash_parameters(initial_hyperparameters))
        
        # Evaluate initial configuration
        initial_score = self._evaluate_configuration(initial_hyperparameters, objective_function)
        initial_set.performance_score = initial_score
        initial_set.training_time = 0
        initial_set.confidence = 1.0
        
        self.best_hyperparameters = initial_set
        
        # Main tuning loop
        for iteration in range(self.config.max_iterations):
            self.iteration_count = iteration
            
            # Check convergence
            if self._check_convergence():
                logging.info(f"Converged after {iteration} iterations")
                break
            
            # Generate next hyperparameter configuration
            next_config = self._generate_next_configuration()
            
            # Skip if already evaluated
            config_hash = self._hash_parameters(next_config)
            if config_hash in self.evaluated_combinations:
                continue
            
            self.evaluated_combinations.add(config_hash)
            
            # Evaluate configuration
            score, training_time = self._evaluate_configuration(next_config, objective_function)
            
            # Create hyperparameter set
            param_set = HyperparameterSet(
                values=next_config,
                performance_score=score,
                training_time=training_time,
                confidence=self._calculate_confidence(iteration)
            )
            
            self.search_history.append(param_set)
            
            # Update best configuration
            if score > (self.best_hyperparameters.performance_score if self.best_hyperparameters else 0):
                self.best_hyperparameters = param_set
                self.last_improvement = iteration
                self.stagnation_counter = 0
                logging.info(f"New best score: {score:.4f} at iteration {iteration}")
            else:
                self.stagnation_counter += 1
            
            # Update convergence state
            self._update_convergence_state(score)
            
            logging.info(f"Iteration {iteration}: Score = {score:.4f}, Best = {self.best_hyperparameters.performance_score:.4f}")
        
        return self.best_hyperparameters
    
    def _generate_next_configuration(self) -> Dict[str, Any]:
        """Keyingi konfiguratsiyani generatsiya qilish"""
        
        if self.config.strategy == TuningStrategy.GRID_SEARCH:
            return self._grid_search_next()
        elif self.config.strategy == TuningStrategy.RANDOM_SEARCH:
            return self._random_search_next()
        elif self.config.strategy == TuningStrategy.BAYESIAN_OPTIMIZATION:
            return self._bayesian_next()
        elif self.config.strategy == TuningStrategy.GENETIC_ALGORITHM:
            return self._genetic_next()
        else:
            return self._adaptive_search_next()
    
    def _grid_search_next(self) -> Dict[str, Any]:
        """Grid search keyingi qadami"""
        
        # Simple grid search implementation
        if not hasattr(self, '_grid_indices'):
            self._grid_indices = {name: 0 for name in self.config.search_space.keys()}
        
        config = {}
        for param_name, param_range in self.config.search_space.items():
            if param_range.param_type == SearchSpace.DISCRETE and param_range.discrete_values:
                idx = self._grid_indices[param_name]
                config[param_name] = param_range.discrete_values[idx]
            elif param_range.param_type == SearchSpace.CONTINUOUS:
                if param_range.log_scale:
                    # Logarithmic scale
                    config[param_name] = param_range.min_value * (param_range.max_value / param_range.min_value) ** (self.iteration_count / self.config.max_iterations)
                else:
                    # Linear scale
                    progress = self.iteration_count / self.config.max_iterations
                    config[param_name] = param_range.min_value + progress * (param_range.max_value - param_range.min_value)
        
        # Update indices for discrete parameters
        for param_name, param_range in self.config.search_space.items():
            if param_range.param_type == SearchSpace.DISCRETE:
                self._grid_indices[param_name] = (self._grid_indices[param_name] + 1) % len(param_range.discrete_values)
        
        return config
    
    def _random_search_next(self) -> Dict[str, Any]:
        """Random search keyingi qadami"""
        
        config = {}
        np.random.seed(self.iteration_count)  # Reproducible results
        
        for param_name, param_range in self.config.search_space.items():
            if param_range.param_type == SearchSpace.CONTINUOUS:
                if param_range.log_scale:
                    # Logarithmic uniform distribution
                    log_min = np.log(param_range.min_value) if param_range.min_value > 0 else -10
                    log_max = np.log(param_range.max_value)
                    log_value = np.random.uniform(log_min, log_max)
                    config[param_name] = np.exp(log_value)
                else:
                    # Uniform distribution
                    config[param_name] = np.random.uniform(param_range.min_value, param_range.max_value)
            
            elif param_range.param_type == SearchSpace.DISCRETE and param_range.discrete_values:
                config[param_name] = np.random.choice(param_range.discrete_values)
            
            elif param_range.param_type == SearchSpace.CATEGORICAL and param_range.categorical_values:
                config[param_name] = np.random.choice(param_range.categorical_values)
        
        return config
    
    def _bayesian_next(self) -> Dict[str, Any]:
        """Bayesian optimization keyingi qadami (soddalashtirilgan)"""
        
        # Simplified Bayesian optimization using Gaussian Process
        if len(self.search_history) < 2:
            return self._random_search_next()
        
        # Get recent configurations and scores
        recent_configs = [h.values for h in self.search_history[-10:]]
        recent_scores = [h.performance_score for h in self.search_history[-10:]]
        
        # Find promising region around best performing configurations
        best_config = max(self.search_history, key=lambda x: x.performance_score).values
        
        # Generate configuration near best with some exploration
        config = {}
        exploration_rate = 0.2 + 0.3 * (1 - self.iteration_count / self.config.max_iterations)
        
        for param_name, param_range in self.config.search_space.items():
            if np.random.random() < exploration_rate:
                # Explore - random value
                if param_range.param_type == SearchSpace.CONTINUOUS:
                    config[param_name] = np.random.uniform(param_range.min_value, param_range.max_value)
                elif param_range.param_type == SearchSpace.DISCRETE:
                    config[param_name] = np.random.choice(param_range.discrete_values)
                else:
                    config[param_name] = np.random.choice(param_range.categorical_values)
            else:
                # Exploit - near best value
                best_value = best_config.get(param_name, param_range.min_value)
                if isinstance(best_value, (int, float)):
                    # Add noise around best value
                    noise = np.random.normal(0, 0.1 * (param_range.max_value - param_range.min_value))
                    config[param_name] = np.clip(best_value + noise, param_range.min_value, param_range.max_value)
                else:
                    config[param_name] = best_value
        
        return config
    
    def _genetic_next(self) -> Dict[str, Any]:
        """Genetic algorithm keyingi qadami (soddalashtirilgan)"""
        
        # Simple genetic algorithm implementation
        if len(self.search_history) < 4:
            return self._random_search_next()
        
        # Tournament selection
        parent1 = self._tournament_selection()
        parent2 = self._tournament_selection()
        
        # Crossover
        child = self._crossover(parent1, parent2)
        
        # Mutation
        mutated_child = self._mutate(child)
        
        return mutated_child
    
    def _tournament_selection(self) -> Dict[str, Any]:
        """Tournament selection"""
        
        tournament_size = min(3, len(self.search_history))
        tournament = np.random.choice(self.search_history, tournament_size, replace=False)
        winner = max(tournament, key=lambda x: x.performance_score)
        return winner.values
    
    def _crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Dict[str, Any]:
        """Crossover operatsiyasi"""
        
        child = {}
        for param_name in parent1.keys():
            if np.random.random() < 0.5:
                child[param_name] = parent1[param_name]
            else:
                child[param_name] = parent2[param_name]
        
        return child
    
    def _mutate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Mutation operatsiyasi"""
        
        mutated = config.copy()
        mutation_rate = 0.1
        
        for param_name, param_range in self.config.search_space.items():
            if np.random.random() < mutation_rate:
                if param_range.param_type == SearchSpace.CONTINUOUS:
                    # Add Gaussian noise
                    value_range = param_range.max_value - param_range.min_value
                    noise = np.random.normal(0, 0.1 * value_range)
                    mutated[param_name] = np.clip(
                        mutated[param_name] + noise, 
                        param_range.min_value, 
                        param_range.max_value
                    )
                elif param_range.param_type == SearchSpace.DISCRETE:
                    mutated[param_name] = np.random.choice(param_range.discrete_values)
                else:
                    mutated[param_name] = np.random.choice(param_range.categorical_values)
        
        return mutated
    
    def _adaptive_search_next(self) -> Dict[str, Any]:
        """Adaptive search keyingi qadami"""
        
        # Adaptive search that adjusts based on recent performance
        recent_performances = [h.performance_score for h in self.search_history[-5:]]
        
        if len(recent_performances) < 3:
            return self._random_search_next()
        
        # Calculate improvement trend
        improvement_trend = recent_performances[-1] - recent_performances[0]
        
        if improvement_trend > self.config.convergence_threshold:
            # Good improvement - reduce exploration
            exploration_rate = 0.1
        elif improvement_trend < -self.config.convergence_threshold:
            # Poor performance - increase exploration
            exploration_rate = 0.4
        else:
            # No significant improvement - moderate exploration
            exploration_rate = 0.25
        
        config = {}
        for param_name, param_range in self.config.search_space.items():
            if np.random.random() < exploration_rate:
                # Explore
                if param_range.param_type == SearchSpace.CONTINUOUS:
                    config[param_name] = np.random.uniform(param_range.min_value, param_range.max_value)
                elif param_range.param_type == SearchSpace.DISCRETE:
                    config[param_name] = np.random.choice(param_range.discrete_values)
                else:
                    config[param_name] = np.random.choice(param_range.categorical_values)
            else:
                # Exploit - based on parameter importance (simplified)
                best_config = self.best_hyperparameters.values if self.best_hyperparameters else {}
                if param_name in best_config:
                    config[param_name] = best_config[param_name]
                else:
                    # Use midpoint
                    if param_range.param_type == SearchSpace.CONTINUOUS:
                        config[param_name] = (param_range.min_value + param_range.max_value) / 2
                    else:
                        config[param_name] = param_range.discrete_values[0] if param_range.discrete_values else None
        
        return config
    
    def _evaluate_configuration(self, hyperparameters: Dict[str, Any], 
                              objective_function: Callable) -> Tuple[float, float]:
        """Konfiguratsiyani baholash"""
        
        start_time = datetime.now()
        
        try:
            # Call objective function with hyperparameters
            if self.config.parallel_evaluations > 1:
                # Parallel evaluation
                scores = []
                with ThreadPoolExecutor(max_workers=self.config.parallel_evaluations) as executor:
                    futures = [executor.submit(objective_function, hyperparameters) 
                             for _ in range(self.config.cross_validation_folds)]
                    for future in as_completed(futures):
                        scores.append(future.result())
                
                score = np.mean(scores)
            else:
                # Single evaluation
                score = objective_function(hyperparameters)
            
            end_time = datetime.now()
            training_time = (end_time - start_time).total_seconds()
            
            return score, training_time
        
        except Exception as e:
            logging.error(f"Error evaluating configuration {hyperparameters}: {str(e)}")
            return 0.0, (datetime.now() - start_time).total_seconds()
    
    def _check_convergence(self) -> bool:
        """Konvergentsiyani tekshirish"""
        
        if len(self.search_history) < self.config.early_stopping_rounds:
            return False
        
        # Check stagnation
        if self.stagnation_counter >= self.config.early_stopping_rounds:
            logging.info(f"Early stopping triggered after {self.stagnation_counter} stagnant iterations")
            return True
        
        # Check improvement threshold
        if self.best_hyperparameters:
            recent_scores = [h.performance_score for h in self.search_history[-self.config.early_stopping_rounds:]]
            best_recent_score = max(recent_scores)
            
            if best_recent_score <= self.best_hyperparameters.performance_score:
                if self.stagnation_counter >= self.config.early_stopping_rounds:
                    return True
        
        # Check iteration limit
        if self.iteration_count >= self.config.max_iterations - 1:
            return True
        
        return False
    
    def _update_convergence_state(self, latest_score: float):
        """Konvergentsiya holatini yangilash"""
        
        if len(self.search_history) < 5:
            self.convergence_state = ConvergenceState.EXPLORING
            return
        
        recent_scores = [h.performance_score for h in self.search_history[-5:]]
        score_trend = recent_scores[-1] - recent_scores[0]
        
        if abs(score_trend) > self.config.convergence_threshold:
            if score_trend > 0:
                self.convergence_state = ConvergenceState.CONVERGING
            else:
                self.convergence_state = ConvergenceState.EXPLORING
        else:
            self.convergence_state = ConvergenceState.STAGNANT
    
    def _calculate_confidence(self, iteration: int) -> float:
        """Konfiguratsiya ishonchliligini hisoblash"""
        
        # More confidence with more evaluations
        base_confidence = min(1.0, len(self.search_history) / 10)
        
        # Reduce confidence if stagnant
        if self.stagnation_counter > 5:
            base_confidence *= 0.7
        
        # Increase confidence near convergence
        if self.convergence_state == ConvergenceState.CONVERGING:
            base_confidence *= 1.2
        
        return min(1.0, base_confidence)
    
    def _hash_parameters(self, parameters: Dict[str, Any]) -> str:
        """Parametrlarni hash qilish"""
        
        # Create deterministic hash
        param_str = json.dumps(parameters, sort_keys=True)
        return hashlib.md5(param_str.encode()).hexdigest()
    
    def get_tuning_summary(self) -> Dict[str, Any]:
        """Tuning natijalarini olish"""
        
        if not self.search_history:
            return {"error": "No tuning history available"}
        
        scores = [h.performance_score for h in self.search_history]
        
        return {
            "strategy": self.config.strategy.value,
            "total_iterations": len(self.search_history),
            "best_score": max(scores),
            "best_hyperparameters": self.best_hyperparameters.values if self.best_hyperparameters else None,
            "worst_score": min(scores),
            "average_score": np.mean(scores),
            "score_std": np.std(scores),
            "convergence_state": self.convergence_state.value,
            "stagnation_counter": self.stagnation_counter,
            "search_history": [
                {
                    "iteration": i,
                    "score": h.performance_score,
                    "hyperparameters": h.values,
                    "timestamp": h.timestamp.isoformat(),
                    "confidence": h.confidence
                }
                for i, h in enumerate(self.search_history)
            ]
        }

class RealTimeHyperparameterOptimizer(BaseAlgorithm):
    """Real-time hyperparameter optimallashtiruvchi"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        self.optimization_history = deque(maxlen=1000)
        self.current_best_params = {}
        self.performance_window = 50
        self.adaptation_frequency = 10  # Tune every N evaluations
        
        # Performance tracking
        self.baseline_performance = 0.0
        self.current_performance = 0.0
        self.performance_improvement = 0.0
        
    def optimize_online(self, model: Any, 
                      training_data: Any,
                      validation_data: Any,
                      hyperparameters: Dict[str, Any]) -> Dict[str, Any]:
        """Online optimallashtirish"""
        
        # Evaluate current performance
        current_score = self._evaluate_model(model, training_data, validation_data)
        self.current_performance = current_score
        
        if not self.baseline_performance:
            self.baseline_performance = current_score
        
        self.performance_improvement = (current_score - self.baseline_performance) / self.baseline_performance
        
        optimization_result = {
            'optimization_needed': False,
            'current_performance': current_score,
            'baseline_performance': self.baseline_performance,
            'improvement': self.performance_improvement,
            'current_hyperparameters': hyperparameters,
            'suggested_changes': {}
        }
        
        # Check if optimization is needed
        if len(self.optimization_history) >= self.adaptation_frequency:
            recent_performances = list(self.optimization_history)[-self.adaptation_frequency:]
            
            # Check for performance degradation
            if np.mean(recent_performances) < current_score * 0.95:
                optimization_result['optimization_needed'] = True
                optimization_result['suggested_changes'] = self._suggest_hyperparameter_changes(hyperparameters, recent_performances)
        
        # Add to history
        self.optimization_history.append(current_score)
        
        # Update current best parameters
        if current_score > max(list(self.optimization_history)[:-1]):
            self.current_best_params = hyperparameters.copy()
        
        return optimization_result
    
    def _evaluate_model(self, model: Any, training_data: Any, validation_data: Any) -> float:
        """Model performance baholash (soddalashtirilgan)"""
        
        # Simplified model evaluation
        # In real implementation, would run validation and calculate metrics
        
        # Simulate evaluation based on model complexity and data size
        base_score = 0.85
        model_complexity_factor = np.random.normal(1.0, 0.1)
        data_factor = 0.9 + np.random.random() * 0.2
        
        score = base_score * model_complexity_factor * data_factor
        return max(0.1, min(1.0, score))
    
    def _suggest_hyperparameter_changes(self, 
                                      current_params: Dict[str, Any],
                                      recent_performances: List[float]) -> Dict[str, Any]:
        """Hyperparameter o'zgarishlari taklif qilish"""
        
        suggestions = {}
        performance_trend = recent_performances[-1] - recent_performances[0]
        
        # Learning rate suggestions
        if 'learning_rate' in current_params:
            if performance_trend < -0.02:  # Performance degrading
                suggestions['learning_rate'] = current_params['learning_rate'] * 0.5  # Reduce
            elif performance_trend > 0.02:  # Performance improving
                suggestions['learning_rate'] = current_params['learning_rate'] * 1.1   # Slight increase
        
        # Batch size suggestions
        if 'batch_size' in current_params:
            if len(recent_performances) >= 5:
                recent_std = np.std(recent_performances)
                if recent_std > 0.1:  # High variance
                    suggestions['batch_size'] = min(current_params['batch_size'] * 2, 256)  # Increase for stability
                elif recent_std < 0.01:  # Low variance, might be stuck
                    suggestions['batch_size'] = max(current_params['batch_size'] // 2, 16)   # Decrease for exploration
        
        # Regularization suggestions
        if 'regularization' in current_params:
            if performance_trend < -0.01:  # Overfitting might be occurring
                suggestions['regularization'] = current_params['regularization'] * 1.2  # Increase
            elif performance_trend > 0.02 and len([p for p in recent_performances if p > np.mean(recent_performances)]) > len(recent_performances) * 0.7:
                suggestions['regularization'] = current_params['regularization'] * 0.9  # Decrease slightly
        
        return suggestions

class HyperparameterSpaceBuilder:
    """Hyperparameter fazosi quruvchi"""
    
    @staticmethod
    def create_neural_network_space() -> Dict[str, HyperparameterRange]:
        """Neural network uchun hyperparameter fazosi"""
        
        return {
            'learning_rate': HyperparameterRange(
                name='learning_rate',
                param_type=SearchSpace.LOGARITHMIC,
                min_value=1e-5,
                max_value=1e-1,
                log_scale=True
            ),
            'batch_size': HyperparameterRange(
                name='batch_size',
                param_type=SearchSpace.DISCRETE,
                discrete_values=[16, 32, 64, 128, 256]
            ),
            'hidden_layers': HyperparameterRange(
                name='hidden_layers',
                param_type=SearchSpace.DISCRETE,
                discrete_values=[1, 2, 3, 4, 5]
            ),
            'hidden_units': HyperparameterRange(
                name='hidden_units',
                param_type=SearchSpace.DISCRETE,
                discrete_values=[32, 64, 128, 256, 512]
            ),
            'dropout_rate': HyperparameterRange(
                name='dropout_rate',
                param_type=SearchSpace.CONTINUOUS,
                min_value=0.0,
                max_value=0.5
            ),
            'activation': HyperparameterRange(
                name='activation',
                param_type=SearchSpace.CATEGORICAL,
                categorical_values=['relu', 'tanh', 'sigmoid']
            ),
            'optimizer': HyperparameterRange(
                name='optimizer',
                param_type=SearchSpace.CATEGORICAL,
                categorical_values=['adam', 'sgd', 'rmsprop']
            )
        }
    
    @staticmethod
    def create_xgboost_space() -> Dict[str, HyperparameterRange]:
        """XGBoost uchun hyperparameter fazosi"""
        
        return {
            'learning_rate': HyperparameterRange(
                name='learning_rate',
                param_type=SearchSpace.CONTINUOUS,
                min_value=0.01,
                max_value=0.3
            ),
            'max_depth': HyperparameterRange(
                name='max_depth',
                param_type=SearchSpace.DISCRETE,
                discrete_values=[3, 4, 5, 6, 7, 8]
            ),
            'min_child_weight': HyperparameterRange(
                name='min_child_weight',
                param_type=SearchSpace.CONTINUOUS,
                min_value=1,
                max_value=10
            ),
            'subsample': HyperparameterRange(
                name='subsample',
                param_type=SearchSpace.CONTINUOUS,
                min_value=0.6,
                max_value=1.0
            ),
            'colsample_bytree': HyperparameterRange(
                name='colsample_bytree',
                param_type=SearchSpace.CONTINUOUS,
                min_value=0.6,
                max_value=1.0
            ),
            'n_estimators': HyperparameterRange(
                name='n_estimators',
                param_type=SearchSpace.DISCRETE,
                discrete_values=[100, 200, 300, 500, 1000]
            )
        }
    
    @staticmethod
    def create_trading_model_space() -> Dict[str, HyperparameterRange]:
        """Trading model uchun hyperparameter fazosi"""
        
        return {
            'lookback_period': HyperparameterRange(
                name='lookback_period',
                param_type=SearchSpace.DISCRETE,
                discrete_values=[5, 10, 20, 30, 50, 100]
            ),
            'risk_threshold': HyperparameterRange(
                name='risk_threshold',
                param_type=SearchSpace.CONTINUOUS,
                min_value=0.01,
                max_value=0.1
            ),
            'position_size': HyperparameterRange(
                name='position_size',
                param_type=SearchSpace.CONTINUOUS,
                min_value=0.01,
                max_value=0.2
            ),
            'stop_loss': HyperparameterRange(
                name='stop_loss',
                param_type=SearchSpace.CONTINUOUS,
                min_value=0.02,
                max_value=0.1
            ),
            'take_profit': HyperparameterRange(
                name='take_profit',
                param_type=SearchSpace.CONTINUOUS,
                min_value=0.03,
                max_value=0.2
            ),
            'volatility_threshold': HyperparameterRange(
                name='volatility_threshold',
                param_type=SearchSpace.CONTINUOUS,
                min_value=0.01,
                max_value=0.15
            )
        }

class EnsembleHyperparameterTuner:
    """Ensemble hyperparameter tuneri"""
    
    def __init__(self):
        self.tuners = {}
        self.tuner_weights = {}
        self.ensemble_results = []
        
    def add_tuner(self, name: str, tuner: OnlineHyperparameterTuner, weight: float = 1.0):
        """Tuner qo'shish"""
        self.tuners[name] = tuner
        self.tuner_weights[name] = weight
    
    def ensemble_tune(self, objective_function: Callable,
                    initial_hyperparameters: Dict[str, Any]) -> HyperparameterSet:
        """Ensemble tuning"""
        
        results = {}
        
        # Run parallel tuning with different strategies
        with ThreadPoolExecutor(max_workers=len(self.tuners)) as executor:
            futures = {
                name: executor.submit(tuner.tune_hyperparameters, objective_function, initial_hyperparameters)
                for name, tuner in self.tuners.items()
            }
            
            for name, future in futures.items():
                try:
                    result = future.result(timeout=300)  # 5 minute timeout
                    results[name] = result
                except Exception as e:
                    logging.error(f"Error in tuner {name}: {str(e)}")
                    results[name] = None
        
        # Combine results with weights
        weighted_scores = {}
        for name, result in results.items():
            if result and name in self.tuner_weights:
                weighted_scores[name] = result.performance_score * self.tuner_weights[name]
        
        # Select best result
        if weighted_scores:
            best_tuner_name = max(weighted_scores, key=weighted_scores.get)
            best_result = results[best_tuner_name]
            
            # Ensemble confidence
            ensemble_confidence = np.mean([r.confidence for r in results.values() if r]) if results else 0.5
            
            best_result.confidence = ensemble_confidence
            
            self.ensemble_results.append(best_result)
            return best_result
        else:
            return HyperparameterSet(values=initial_hyperparameters, performance_score=0.0)

# Demo va test
if __name__ == "__main__":
    # Hyperparameter tuning testi
    config = TuningConfiguration(
        strategy=TuningStrategy.RANDOM_SEARCH,
        search_space=HyperparameterSpaceBuilder.create_trading_model_space(),
        max_iterations=20,
        convergence_threshold=0.01,
        parallel_evaluations=2
    )
    
    tuner = OnlineHyperparameterTuner(config)
    
    # Objective function (simplified)
    def objective_function(hyperparams):
        """Simplified objective function"""
        # Simulate model training and evaluation
        lookback = hyperparams.get('lookback_period', 20)
        risk_threshold = hyperparams.get('risk_threshold', 0.02)
        
        # Simulate performance based on hyperparameters
        base_performance = 0.7
        
        # Lookback period effect
        if 20 <= lookback <= 50:
            lookback_bonus = 0.1
        else:
            lookback_bonus = -0.05
        
        # Risk threshold effect
        if 0.02 <= risk_threshold <= 0.05:
            risk_bonus = 0.1
        else:
            risk_bonus = -0.1
        
        performance = base_performance + lookback_bonus + risk_bonus + np.random.normal(0, 0.05)
        
        return max(0.1, min(1.0, performance))
    
    # Initial hyperparameters
    initial_params = {
        'lookback_period': 20,
        'risk_threshold': 0.02,
        'position_size': 0.05,
        'stop_loss': 0.05,
        'take_profit': 0.1,
        'volatility_threshold': 0.05
    }
    
    # Run tuning
    best_result = tuner.tune_hyperparameters(objective_function, initial_params)
    
    print("=== HYPERPARAMETER TUNING RESULTS ===")
    print(f"Strategy: {config.strategy.value}")
    print(f"Best Score: {best_result.performance_score:.4f}")
    print(f"Best Hyperparameters: {best_result.values}")
    print(f"Confidence: {best_result.confidence:.3f}")
    print(f"Total Evaluations: {len(tuner.search_history)}")
    
    # Get tuning summary
    summary = tuner.get_tuning_summary()
    print(f"\nTuning Summary:")
    print(f"Convergence State: {summary['convergence_state']}")
    print(f"Average Score: {summary['average_score']:.4f}")
    print(f"Score Std: {summary['score_std']:.4f}")
    
    # Real-time optimization test
    rt_optimizer = RealTimeHyperparameterOptimizer()
    
    mock_model = {"complexity": "medium"}
    mock_training_data = {"size": 10000}
    mock_validation_data = {"size": 2000}
    
    for iteration in range(30):
        optimization_result = rt_optimizer.optimize_online(
            mock_model, mock_training_data, mock_validation_data, initial_params
        )
        
        if iteration % 10 == 0:
            print(f"\n=== REAL-TIME OPTIMIZATION (Iteration {iteration}) ===")
            print(f"Current Performance: {optimization_result['current_performance']:.4f}")
            print(f"Baseline Performance: {optimization_result['baseline_performance']:.4f}")
            print(f"Improvement: {optimization_result['improvement']:.2%}")
            print(f"Optimization Needed: {optimization_result['optimization_needed']}")
            if optimization_result['suggested_changes']:
                print(f"Suggested Changes: {optimization_result['suggested_changes']}")
    
    # Ensemble tuner test
    ensemble_tuner = EnsembleHyperparameterTuner()
    
    # Add different tuners
    grid_config = TuningConfiguration(strategy=TuningStrategy.GRID_SEARCH, max_iterations=5)
    random_config = TuningConfiguration(strategy=TuningStrategy.RANDOM_SEARCH, max_iterations=5)
    
    ensemble_tuner.add_tuner("grid", OnlineHyperparameterTuner(grid_config), weight=0.4)
    ensemble_tuner.add_tuner("random", OnlineHyperparameterTuner(random_config), weight=0.6)
    
    ensemble_result = ensemble_tuner.ensemble_tune(objective_function, initial_params)
    
    print(f"\n=== ENSEMBLE TUNING RESULT ===")
    print(f"Ensemble Best Score: {ensemble_result.performance_score:.4f}")
    print(f"Ensemble Hyperparameters: {ensemble_result.values}")
    print(f"Ensemble Confidence: {ensemble_result.confidence:.3f}")