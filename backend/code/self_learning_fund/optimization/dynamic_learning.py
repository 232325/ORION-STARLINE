"""
Dynamic Learning Rate and Performance Optimization
Real-time hyperparameter tuning, adaptive optimization, va performance tracking
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import warnings
from collections import deque, defaultdict
from abc import ABC, abstractmethod
from sklearn.base import BaseEstimator
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from scipy.optimize import minimize
import json
warnings.filterwarnings('ignore')

@dataclass
class DynamicLearningConfig:
    """Dynamic learning configuration"""
    # Learning rate adaptation
    initial_learning_rate: float = 0.001
    min_learning_rate: float = 1e-6
    max_learning_rate: float = 0.1
    adaptation_method: str = 'adaptive'  # 'adaptive', 'exponential', 'step', 'cosine'
    adaptation_frequency: int = 100
    
    # Performance-based adaptation
    performance_threshold: float = 0.05
    improvement_threshold: float = 0.02
    patience: int = 10
    min_delta: float = 1e-4
    
    # Hyperparameter optimization
    enable_hyperparameter_tuning: bool = True
    tuning_method: str = 'bayesian'  # 'random', 'grid', 'bayesian', 'genetic'
    max_tuning_iterations: int = 50
    tuning_frequency: int = 1000
    parameter_bounds: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        'learning_rate': (1e-6, 0.1),
        'batch_size': (16, 1024),
        'regularization': (1e-6, 1.0)
    })
    
    # Batch size adaptation
    enable_batch_size_adaptation: bool = True
    initial_batch_size: int = 32
    min_batch_size: int = 8
    max_batch_size: int = 1024
    
    # Gradient optimization
    gradient_clipping: bool = True
    gradient_clip_value: float = 1.0
    weight_decay: float = 1e-4
    
    # Performance tracking
    track_gradients: bool = True
    gradient_history_size: int = 1000
    performance_history_size: int = 500

class AdaptiveOptimizer:
    """Base class for adaptive optimizers"""
    
    def __init__(self, config: DynamicLearningConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.AdaptiveOptimizer")
        
        # Optimization state
        self.current_learning_rate = config.initial_learning_rate
        self.current_batch_size = config.initial_batch_size
        self.iteration = 0
        
        # Performance tracking
        self.performance_history = deque(maxlen=config.performance_history_size)
        self.learning_rate_history = deque(maxlen=config.performance_history_size)
        self.gradient_history = deque(maxlen=config.gradient_history_size)
        
        # Adaptation counters
        self.patience_counter = 0
        self.best_performance = float('-inf')
        
    def step(self, gradients: np.ndarray, loss: float, **kwargs) -> Dict[str, Any]:
        """Perform optimization step"""
        
        self.iteration += 1
        
        # Clip gradients if enabled
        if self.config.gradient_clipping:
            gradients = self._clip_gradients(gradients)
        
        # Record gradient information
        if self.config.track_gradients:
            self.gradient_history.append({
                'iteration': self.iteration,
                'gradient_norm': np.linalg.norm(gradients),
                'gradient_mean': np.mean(gradients),
                'loss': loss
            })
        
        # Check if adaptation is needed
        adaptation_result = self._check_adaptation_needed(loss)
        
        # Perform optimization step
        if hasattr(self, '_perform_step'):
            step_result = self._perform_step(gradients, loss, **kwargs)
        else:
            step_result = self._default_optimization_step(gradients, loss, **kwargs)
        
        # Update learning rate if needed
        if adaptation_result.get('adapt_learning_rate', False):
            self._adapt_learning_rate(adaptation_result['adaptation_direction'])
        
        if adaptation_result.get('adapt_batch_size', False):
            self._adapt_batch_size(adaptation_result['adaptation_direction'])
        
        # Record current state
        self.learning_rate_history.append(self.current_learning_rate)
        self.performance_history.append(loss)
        
        return {
            'step_result': step_result,
            'adaptation': adaptation_result,
            'learning_rate': self.current_learning_rate,
            'batch_size': self.current_batch_size,
            'iteration': self.iteration
        }
    
    def _clip_gradients(self, gradients: np.ndarray) -> np.ndarray:
        """Clip gradients to prevent explosion"""
        gradient_norm = np.linalg.norm(gradients)
        
        if gradient_norm > self.config.gradient_clip_value:
            gradients = gradients * (self.config.gradient_clip_value / gradient_norm)
        
        return gradients
    
    def _check_adaptation_needed(self, current_loss: float) -> Dict[str, Any]:
        """Check if adaptation is needed based on performance"""
        
        if len(self.performance_history) < self.config.patience:
            return {'adapt_learning_rate': False, 'adapt_batch_size': False}
        
        # Check for improvement
        recent_losses = list(self.performance_history)[-self.config.patience:]
        loss_trend = np.polyfit(range(len(recent_losses)), recent_losses, 1)[0]
        
        adaptation_result = {
            'adapt_learning_rate': False,
            'adapt_batch_size': False,
            'adaptation_direction': 0,
            'improvement_detected': loss_trend < -self.config.min_delta
        }
        
        # Performance-based adaptation
        if len(self.performance_history) > 1:
            recent_performance = current_loss
            previous_performance = self.performance_history[-2]
            
            improvement = previous_performance - recent_performance
            
            if improvement > self.config.improvement_threshold:
                # Good performance - increase learning rate
                adaptation_result['adapt_learning_rate'] = True
                adaptation_result['adaptation_direction'] = 1
                self.patience_counter = 0
                self.logger.debug(f"Performance improving: {improvement:.4f}, increasing learning rate")
                
            elif improvement < -self.config.performance_threshold:
                # Poor performance - decrease learning rate
                adaptation_result['adapt_learning_rate'] = True
                adaptation_result['adaptation_direction'] = -1
                self.patience_counter += 1
                self.logger.debug(f"Performance degrading: {-improvement:.4f}, decreasing learning rate")
                
                if self.patience_counter >= self.config.patience:
                    # Reset patience
                    self.patience_counter = 0
                    # Could trigger more aggressive adaptation here
        
        return adaptation_result
    
    def _adapt_learning_rate(self, direction: int) -> None:
        """Adapt learning rate based on performance"""
        
        if self.config.adaptation_method == 'adaptive':
            # Adaptive learning rate adjustment
            factor = 1.1 if direction > 0 else 0.9
            self.current_learning_rate *= factor
            
        elif self.config.adaptation_method == 'exponential':
            # Exponential decay
            decay_rate = 0.95
            self.current_learning_rate *= (decay_rate ** (self.iteration / 1000))
            
        elif self.config.adaptation_method == 'step':
            # Step decay
            if self.iteration % 1000 == 0:
                self.current_learning_rate *= 0.5
                
        elif self.config.adaptation_method == 'cosine':
            # Cosine annealing
            t = self.iteration / 10000
            self.current_learning_rate = self.config.min_learning_rate + (
                self.config.max_learning_rate - self.config.min_learning_rate
            ) * 0.5 * (1 + np.cos(np.pi * t))
        
        # Apply bounds
        self.current_learning_rate = np.clip(
            self.current_learning_rate,
            self.config.min_learning_rate,
            self.config.max_learning_rate
        )
        
        self.logger.debug(f"Adapted learning rate to {self.current_learning_rate:.6f}")
    
    def _adapt_batch_size(self, direction: int) -> None:
        """Adapt batch size based on performance"""
        
        if not self.config.enable_batch_size_adaptation:
            return
        
        if direction > 0:
            # Increase batch size for stability
            self.current_batch_size = min(
                int(self.current_batch_size * 1.1),
                self.config.max_batch_size
            )
        else:
            # Decrease batch size for exploration
            self.current_batch_size = max(
                int(self.current_batch_size * 0.9),
                self.config.min_batch_size
            )
    
    def _default_optimization_step(self, gradients: np.ndarray, loss: float, **kwargs) -> Dict[str, Any]:
        """Default optimization step implementation"""
        
        # This is a simplified implementation
        # In practice, would involve actual parameter updates
        
        return {
            'step_size': self.current_learning_rate * np.linalg.norm(gradients),
            'gradients_processed': True,
            'loss_reduction_estimate': self.current_learning_rate * np.sum(gradients**2)
        }
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization status"""
        
        return {
            'current_learning_rate': self.current_learning_rate,
            'current_batch_size': self.current_batch_size,
            'iteration': self.iteration,
            'patience_counter': self.patience_counter,
            'best_performance': self.best_performance,
            'recent_performance_trend': self._calculate_performance_trend(),
            'gradient_statistics': self._get_gradient_statistics(),
            'learning_rate_statistics': self._get_learning_rate_statistics()
        }
    
    def _calculate_performance_trend(self) -> str:
        """Calculate recent performance trend"""
        
        if len(self.performance_history) < 10:
            return 'insufficient_data'
        
        recent_performance = list(self.performance_history)[-10:]
        trend_coefficient = np.polyfit(range(len(recent_performance)), recent_performance, 1)[0]
        
        if trend_coefficient < -0.001:
            return 'improving'
        elif trend_coefficient > 0.001:
            return 'declining'
        else:
            return 'stable'
    
    def _get_gradient_statistics(self) -> Dict[str, float]:
        """Get gradient statistics"""
        
        if not self.gradient_history:
            return {}
        
        norms = [g['gradient_norm'] for g in self.gradient_history]
        means = [g['gradient_mean'] for g in self.gradient_history]
        
        return {
            'avg_gradient_norm': np.mean(norms),
            'std_gradient_norm': np.std(norms),
            'max_gradient_norm': np.max(norms),
            'avg_gradient_mean': np.mean(means),
            'gradient_explosion_risk': np.max(norms) > 10.0  # Threshold for explosion
        }
    
    def _get_learning_rate_statistics(self) -> Dict[str, float]:
        """Get learning rate statistics"""
        
        if not self.learning_rate_history:
            return {}
        
        rates = list(self.learning_rate_history)
        
        return {
            'current_learning_rate': rates[-1] if rates else self.config.initial_learning_rate,
            'avg_learning_rate': np.mean(rates),
            'learning_rate_range': np.max(rates) - np.min(rates),
            'adaptation_frequency': len(rates) / max(1, self.iteration / self.config.adaptation_frequency)
        }

class SGDOptimizer(AdaptiveOptimizer):
    """Stochastic Gradient Descent with adaptive learning rate"""
    
    def __init__(self, config: DynamicLearningConfig):
        super().__init__(config)
        self.momentum = 0.9
        self.velocity = None
        
    def _perform_step(self, gradients: np.ndarray, loss: float, **kwargs) -> Dict[str, Any]:
        """Perform SGD optimization step"""
        
        # Initialize velocity if needed
        if self.velocity is None:
            self.velocity = np.zeros_like(gradients)
        
        # Momentum update
        self.velocity = self.momentum * self.velocity - self.current_learning_rate * gradients
        
        # Parameter update would happen here
        # parameters += self.velocity
        
        return {
            'velocity_norm': np.linalg.norm(self.velocity),
            'update_magnitude': np.linalg.norm(self.current_learning_rate * gradients)
        }

class AdamOptimizer(AdaptiveOptimizer):
    """Adam optimizer with adaptive learning rate"""
    
    def __init__(self, config: DynamicLearningConfig):
        super().__init__(config)
        self.beta1 = 0.9
        self.beta2 = 0.999
        self.epsilon = 1e-8
        self.m = None
        self.v = None
        self.t = 0
        
    def _perform_step(self, gradients: np.ndarray, loss: float, **kwargs) -> Dict[str, Any]:
        """Perform Adam optimization step"""
        
        self.t += 1
        
        # Initialize moments
        if self.m is None:
            self.m = np.zeros_like(gradients)
        if self.v is None:
            self.v = np.zeros_like(gradients)
        
        # Update moments
        self.m = self.beta1 * self.m + (1 - self.beta1) * gradients
        self.v = self.beta2 * self.v + (1 - self.beta2) * gradients**2
        
        # Bias correction
        m_corrected = self.m / (1 - self.beta1**self.t)
        v_corrected = self.v / (1 - self.beta2**self.t)
        
        # Parameter update
        update = m_corrected / (np.sqrt(v_corrected) + self.epsilon)
        
        return {
            'm_norm': np.linalg.norm(m_corrected),
            'v_norm': np.linalg.norm(v_corrected),
            'update_norm': np.linalg.norm(update)
        }

class HyperparameterTuner:
    """Real-time hyperparameter tuning system"""
    
    def __init__(self, config: DynamicLearningConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.HyperparameterTuner")
        
        # Tuning history
        self.tuning_history = []
        self.parameter_history = []
        self.performance_history = []
        
        # Current best parameters
        self.best_parameters = {}
        self.best_performance = float('-inf')
        
        # Tuning state
        self.last_tuning_iteration = 0
        
    def should_tune(self, current_iteration: int) -> bool:
        """Check if hyperparameter tuning should be performed"""
        
        if not self.config.enable_hyperparameter_tuning:
            return False
        
        return (
            current_iteration - self.last_tuning_iteration >= self.config.tuning_frequency
        )
    
    def tune_hyperparameters(self, model: BaseEstimator, training_data: Tuple[np.ndarray, np.ndarray],
                           validation_data: Tuple[np.ndarray, np.ndarray],
                           current_iteration: int) -> Dict[str, Any]:
        """Perform hyperparameter tuning"""
        
        X_train, y_train = training_data
        X_val, y_val = validation_data
        
        self.logger.info(f"Starting hyperparameter tuning at iteration {current_iteration}")
        
        tuning_result = None
        
        if self.config.tuning_method == 'random':
            tuning_result = self._random_search_tuning(model, X_train, y_train, X_val, y_val)
        elif self.config.tuning_method == 'grid':
            tuning_result = self._grid_search_tuning(model, X_train, y_train, X_val, y_val)
        elif self.config.tuning_method == 'bayesian':
            tuning_result = self._bayesian_tuning(model, X_train, y_train, X_val, y_val)
        elif self.config.tuning_method == 'genetic':
            tuning_result = self._genetic_tuning(model, X_train, y_train, X_val, y_val)
        
        if tuning_result and tuning_result.get('success', False):
            # Update best parameters
            new_params = tuning_result['best_parameters']
            new_performance = tuning_result['best_performance']
            
            self.best_parameters.update(new_params)
            self.best_performance = max(self.best_performance, new_performance)
            
            self.logger.info(f"Hyperparameter tuning completed. Best performance: {new_performance:.4f}")
        
        # Record tuning
        tuning_record = {
            'timestamp': datetime.now(),
            'iteration': current_iteration,
            'method': self.config.tuning_method,
            'result': tuning_result
        }
        
        self.tuning_history.append(tuning_record)
        self.last_tuning_iteration = current_iteration
        
        return tuning_result or {'success': False, 'reason': 'Tuning method not implemented'}
    
    def _random_search_tuning(self, model: BaseEstimator, X_train: np.ndarray, y_train: np.ndarray,
                            X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, Any]:
        """Random search hyperparameter tuning"""
        
        best_score = float('-inf')
        best_params = {}
        
        for i in range(self.config.max_tuning_iterations):
            # Generate random parameters
            params = self._generate_random_parameters()
            
            # Create and evaluate model
            try:
                test_model = type(model)(**{**model.get_params(), **params})
                test_model.fit(X_train, y_train)
                
                if hasattr(test_model, 'predict_proba'):
                    # Classification
                    predictions = test_model.predict(X_val)
                    score = accuracy_score(y_val, predictions)
                else:
                    # Regression
                    predictions = test_model.predict(X_val)
                    score = 1.0 / (1.0 + mean_squared_error(y_val, predictions))
                
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
                    
            except Exception as e:
                self.logger.warning(f"Random search trial {i} failed: {e}")
                continue
        
        return {
            'success': True,
            'best_parameters': best_params,
            'best_performance': best_score,
            'method': 'random_search'
        }
    
    def _grid_search_tuning(self, model: BaseEstimator, X_train: np.ndarray, y_train: np.ndarray,
                          X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, Any]:
        """Grid search hyperparameter tuning"""
        
        # Simplified grid search (would use actual GridSearchCV in practice)
        parameter_grid = self._create_parameter_grid()
        
        best_score = float('-inf')
        best_params = {}
        
        for param_combination in self._generate_parameter_combinations(parameter_grid):
            try:
                test_model = type(model)(**{**model.get_params(), **param_combination})
                test_model.fit(X_train, y_train)
                
                if hasattr(test_model, 'predict_proba'):
                    predictions = test_model.predict(X_val)
                    score = accuracy_score(y_val, predictions)
                else:
                    predictions = test_model.predict(X_val)
                    score = 1.0 / (1.0 + mean_squared_error(y_val, predictions))
                
                if score > best_score:
                    best_score = score
                    best_params = param_combination.copy()
                    
            except Exception as e:
                continue
        
        return {
            'success': True,
            'best_parameters': best_params,
            'best_performance': best_score,
            'method': 'grid_search'
        }
    
    def _bayesian_tuning(self, model: BaseEstimator, X_train: np.ndarray, y_train: np.ndarray,
                       X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, Any]:
        """Bayesian optimization hyperparameter tuning"""
        
        # Simplified Bayesian optimization (would use libraries like Optuna/Scikit-optimize in practice)
        from scipy.optimize import minimize
        
        def objective(params_dict):
            try:
                test_model = type(model)(**{**model.get_params(), **params_dict})
                test_model.fit(X_train, y_train)
                
                if hasattr(test_model, 'predict_proba'):
                    predictions = test_model.predict(X_val)
                    score = accuracy_score(y_val, predictions)
                else:
                    predictions = test_model.predict(X_val)
                    score = 1.0 / (1.0 + mean_squared_error(y_val, predictions))
                
                return -score  # Minimize negative score
                
            except Exception as e:
                return 1.0  # Return large penalty for failed trials
        
        # Convert parameter bounds to format expected by scipy.optimize
        bounds = list(self.config.parameter_bounds.values())
        
        try:
            result = minimize(objective, x0=[0.001], bounds=bounds, method='L-BFGS-B')
            
            return {
                'success': result.success,
                'best_parameters': dict(zip(self.config.parameter_bounds.keys(), result.x)),
                'best_performance': -result.fun,
                'method': 'bayesian_optimization'
            }
            
        except Exception as e:
            self.logger.warning(f"Bayesian optimization failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _genetic_tuning(self, model: BaseEstimator, X_train: np.ndarray, y_train: np.ndarray,
                      X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, Any]:
        """Genetic algorithm hyperparameter tuning"""
        
        # Simplified genetic algorithm
        population_size = 10
        generations = 5
        
        # Initialize population
        population = [self._generate_random_parameters() for _ in range(population_size)]
        
        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = []
            for params in population:
                try:
                    test_model = type(model)(**{**model.get_params(), **params})
                    test_model.fit(X_train, y_train)
                    
                    if hasattr(test_model, 'predict_proba'):
                        predictions = test_model.predict(X_val)
                        score = accuracy_score(y_val, predictions)
                    else:
                        predictions = test_model.predict(X_val)
                        score = 1.0 / (1.0 + mean_squared_error(y_val, predictions))
                    
                    fitness_scores.append(score)
                    
                except Exception as e:
                    fitness_scores.append(0.0)
            
            # Selection and reproduction
            best_idx = np.argmax(fitness_scores)
            best_params = population[best_idx].copy()
            best_score = fitness_scores[best_idx]
            
            # Create next generation (simplified)
            new_population = [best_params]  # Keep best
            
            for _ in range(population_size - 1):
                # Simple mutation of best parameters
                mutated_params = self._mutate_parameters(best_params)
                new_population.append(mutated_params)
            
            population = new_population
        
        return {
            'success': True,
            'best_parameters': best_params,
            'best_performance': best_score,
            'method': 'genetic_algorithm'
        }
    
    def _generate_random_parameters(self) -> Dict[str, float]:
        """Generate random parameters within bounds"""
        params = {}
        
        for param_name, (min_val, max_val) in self.config.parameter_bounds.items():
            if param_name == 'batch_size':
                # Special handling for batch size
                params[param_name] = np.random.randint(int(min_val), int(max_val) + 1)
            else:
                params[param_name] = np.random.uniform(min_val, max_val)
        
        return params
    
    def _create_parameter_grid(self) -> Dict[str, List[float]]:
        """Create parameter grid for grid search"""
        grid = {}
        
        for param_name, (min_val, max_val) in self.config.parameter_bounds.items():
            if param_name == 'batch_size':
                grid[param_name] = [16, 32, 64, 128, 256]
            else:
                # Create log-spaced values
                grid[param_name] = np.logspace(np.log10(min_val), np.log10(max_val), 5).tolist()
        
        return grid
    
    def _generate_parameter_combinations(self, parameter_grid: Dict[str, List[float]]) -> List[Dict[str, float]]:
        """Generate all parameter combinations"""
        from itertools import product
        
        param_names = list(parameter_grid.keys())
        param_values = [parameter_grid[name] for name in param_names]
        
        combinations = []
        for values in product(*param_values):
            combination = dict(zip(param_names, values))
            combinations.append(combination)
        
        return combinations
    
    def _mutate_parameters(self, params: Dict[str, float]) -> Dict[str, float]:
        """Mutate parameters for genetic algorithm"""
        mutated = params.copy()
        
        for param_name in mutated:
            min_val, max_val = self.config.parameter_bounds[param_name]
            mutation_range = (max_val - min_val) * 0.1  # 10% mutation
            
            if param_name == 'batch_size':
                mutated[param_name] = int(mutated[param_name] + np.random.randint(-mutation_range, mutation_range))
                mutated[param_name] = int(np.clip(mutated[param_name], min_val, max_val))
            else:
                mutated[param_name] += np.random.uniform(-mutation_range, mutation_range)
                mutated[param_name] = np.clip(mutated[param_name], min_val, max_val)
        
        return mutated
    
    def get_tuning_summary(self) -> Dict[str, Any]:
        """Get hyperparameter tuning summary"""
        
        return {
            'total_tuning_sessions': len(self.tuning_history),
            'successful_tunings': sum(1 for t in self.tuning_history if t['result'].get('success', False)),
            'best_parameters': self.best_parameters,
            'best_performance': self.best_performance,
            'tuning_frequency': self.config.tuning_frequency,
            'tuning_method': self.config.tuning_method,
            'recent_tunings': self.tuning_history[-5:] if self.tuning_history else []
        }

class DynamicLearningSystem:
    """Complete dynamic learning optimization system"""
    
    def __init__(self, config: DynamicLearningConfig = None):
        self.config = config or DynamicLearningConfig()
        self.logger = logging.getLogger(f"{__name__}.DynamicLearningSystem")
        
        # Core components
        self.optimizer = SGDOptimizer(self.config)  # Default to SGD
        self.hyperparameter_tuner = HyperparameterTuner(self.config)
        
        # System state
        self.model = None
        self.is_initialized = False
        self.iteration = 0
        
        # Performance tracking
        self.system_performance = deque(maxlen=self.config.performance_history_size)
        
    def initialize(self, model: BaseEstimator, initial_parameters: Dict[str, Any] = None) -> None:
        """Initialize the dynamic learning system"""
        
        self.model = model
        
        # Initialize optimizer
        optimizer_type = initial_parameters.get('optimizer_type', 'sgd') if initial_parameters else 'sgd'
        
        if optimizer_type == 'adam':
            self.optimizer = AdamOptimizer(self.config)
        else:
            self.optimizer = SGDOptimizer(self.config)
        
        self.is_initialized = True
        self.logger.info(f"Dynamic learning system initialized with {optimizer_type} optimizer")
    
    def optimize_step(self, gradients: np.ndarray, loss: float, 
                     training_data: Tuple[np.ndarray, np.ndarray] = None,
                     validation_data: Tuple[np.ndarray, np.ndarray] = None) -> Dict[str, Any]:
        """Perform optimization step with dynamic learning"""
        
        if not self.is_initialized:
            raise ValueError("System must be initialized before optimization")
        
        # Perform optimization step
        optimization_result = self.optimizer.step(gradients, loss)
        
        # Check for hyperparameter tuning
        if (self.config.enable_hyperparameter_tuning and 
            self.hyperparameter_tuner.should_tune(self.iteration) and
            training_data is not None and validation_data is not None):
            
            tuning_result = self.hyperparameter_tuner.tune_hyperparameters(
                self.model, training_data, validation_data, self.iteration
            )
            
            optimization_result['hyperparameter_tuning'] = tuning_result
        
        self.iteration += 1
        return optimization_result
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        return {
            'is_initialized': self.is_initialized,
            'iteration': self.iteration,
            'optimizer_status': self.optimizer.get_optimization_status(),
            'hyperparameter_tuning_summary': self.hyperparameter_tuner.get_tuning_summary(),
            'system_config': {
                'learning_rate': self.config.initial_learning_rate,
                'adaptation_method': self.config.adaptation_method,
                'tuning_method': self.config.tuning_method,
                'batch_size_adaptation': self.config.enable_batch_size_adaptation
            }
        }
    
    def save_system_state(self, filepath: str) -> None:
        """Save system state"""
        
        state = {
            'iteration': self.iteration,
            'optimizer_state': {
                'current_learning_rate': self.optimizer.current_learning_rate,
                'current_batch_size': self.optimizer.current_batch_size,
                'performance_history': list(self.optimizer.performance_history),
                'learning_rate_history': list(self.optimizer.learning_rate_history)
            },
            'hyperparameter_tuning_history': self.hyperparameter_tuner.tuning_history,
            'best_parameters': self.hyperparameter_tuner.best_parameters,
            'best_performance': self.hyperparameter_tuner.best_performance,
            'config': self.config.__dict__
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        
        self.logger.info(f"System state saved to {filepath}")

# Factory functions
def create_dynamic_learning_system(config: Optional[DynamicLearningConfig] = None) -> DynamicLearningSystem:
    """Create dynamic learning system"""
    
    if config is None:
        config = DynamicLearningConfig()
    
    return DynamicLearningSystem(config)

def create_adam_optimizer(config: DynamicLearningConfig) -> AdamOptimizer:
    """Create Adam optimizer"""
    
    return AdamOptimizer(config)

def create_sgd_optimizer(config: DynamicLearningConfig) -> SGDOptimizer:
    """Create SGD optimizer"""
    
    return SGDOptimizer(config)