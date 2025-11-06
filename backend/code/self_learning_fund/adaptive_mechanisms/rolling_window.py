"""
Rolling Window Optimization - Dynamic window-based model optimization
Adaptive window sizes, performance-based window selection, va online optimization
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import warnings
from collections import deque, defaultdict
from abc import ABC, abstractmethod
from sklearn.base import BaseEstimator
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, TimeSeriesSplit
from scipy import stats
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')

@dataclass
class RollingWindowConfig:
    """Rolling window optimization konfiguratsiyasi"""
    # Window sizes
    min_window_size: int = 50
    max_window_size: int = 1000
    initial_window_size: int = 200
    step_size: int = 10
    
    # Adaptive window selection
    enable_adaptive_windows: bool = True
    window_selection_method: str = 'performance'  # 'performance', 'statistical', 'hybrid'
    performance_threshold: float = 0.05
    window_shrink_factor: float = 0.9
    window_grow_factor: float = 1.1
    
    # Optimization strategies
    optimization_frequency: int = 100
    model_replacement_threshold: float = 0.1
    ensemble_size: int = 5
    
    # Performance tracking
    track_performance_history: bool = True
    performance_history_size: int = 1000
    validation_split: float = 0.2
    
    # Statistical tests for window selection
    statistical_test: str = 'ks'  # 'ks', 'chi2', 'anderson'
    significance_level: float = 0.05
    
    # Advanced features
    enable_model_ensemble: bool = True
    enable_performance_weighting: bool = True
    enable_cross_validation: bool = True
    cv_folds: int = 5
    
    # Online learning
    online_learning_rate: float = 0.01
    forgetting_factor: float = 0.95
    adaptation_rate: float = 0.1

@dataclass
class WindowMetrics:
    """Window performance metrics"""
    window_id: int
    start_time: datetime
    end_time: datetime
    window_size: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_score: float
    stability_score: float
    model_diversity: float
    computation_time: float
    
class WindowSelector:
    """Adaptive window selection algorithm"""
    
    def __init__(self, config: RollingWindowConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.WindowSelector")
        
        # Window performance history
        self.window_history = deque(maxlen=config.performance_history_size)
        self.current_window_id = 0
        
        # Adaptive parameters
        self.current_window_size = config.initial_window_size
        self.performance_baseline = None
        self.adaptation_counter = 0
        
        # Window quality metrics
        self.window_qualities = {}
        
    def select_optimal_window(self, recent_performance: List[float], 
                            data_characteristics: Dict[str, Any] = None) -> int:
        """Select optimal window size based on performance and data characteristics"""
        
        if not self.enable_adaptive_windows:
            return self.config.initial_window_size
        
        if len(recent_performance) < 10:
            return self.current_window_size
        
        # Calculate performance metrics
        mean_performance = np.mean(recent_performance)
        performance_stability = 1.0 / (1.0 + np.std(recent_performance))
        
        # Update baseline
        if self.performance_baseline is None:
            self.performance_baseline = mean_performance
        
        performance_change = (mean_performance - self.performance_baseline) / self.performance_baseline
        
        # Determine if window size should be adjusted
        should_adjust = False
        adjustment_direction = 0
        
        if self.config.window_selection_method == 'performance':
            should_adjust, adjustment_direction = self._performance_based_selection(
                performance_change, performance_stability
            )
        elif self.config.window_selection_method == 'statistical':
            should_adjust, adjustment_direction = self._statistical_based_selection(
                recent_performance, data_characteristics
            )
        else:  # hybrid
            should_adjust, adjustment_direction = self._hybrid_selection(
                performance_change, performance_stability, recent_performance
            )
        
        if should_adjust:
            self._adjust_window_size(adjustment_direction)
        
        return self.current_window_size
    
    def _performance_based_selection(self, performance_change: float, 
                                   stability_score: float) -> Tuple[bool, int]:
        """Select window size based on performance metrics"""
        
        # High performance and stability - can use larger window
        if performance_change > self.config.performance_threshold and stability_score > 0.8:
            return True, 1  # Grow window
        
        # Low performance or instability - use smaller window for faster adaptation
        elif performance_change < -self.config.performance_threshold or stability_score < 0.5:
            return True, -1  # Shrink window
        
        # Moderate performance - maintain current size
        else:
            return False, 0
    
    def _statistical_based_selection(self, recent_performance: List[float],
                                   data_characteristics: Dict[str, Any]) -> Tuple[bool, int]:
        """Select window size based on statistical tests"""
        
        if len(recent_performance) < 20:
            return False, 0
        
        # Recent vs older performance comparison
        recent_20 = recent_performance[-20:]
        older_20 = recent_performance[-40:-20] if len(recent_performance) >= 40 else recent_performance[:-20]
        
        if len(older_20) > 5:
            # Statistical test for difference
            try:
                statistic, p_value = stats.ks_2samp(recent_20, older_20)
                significant_difference = p_value < self.config.significance_level
                
                # If performance is significantly different, adjust window
                recent_mean = np.mean(recent_20)
                older_mean = np.mean(older_20)
                
                if significant_difference:
                    if recent_mean < older_mean:  # Performance declining
                        return True, -1  # Shrink for faster adaptation
                    else:  # Performance improving
                        return True, 1   # Grow for stability
                        
            except Exception as e:
                self.logger.warning(f"Statistical test failed: {e}")
        
        return False, 0
    
    def _hybrid_selection(self, performance_change: float, stability_score: float,
                        recent_performance: List[float]) -> Tuple[bool, int]:
        """Hybrid window selection combining performance and statistical approaches"""
        
        # Performance-based signal
        perf_signal = 0
        if performance_change > self.config.performance_threshold:
            perf_signal = 1
        elif performance_change < -self.config.performance_threshold:
            perf_signal = -1
        
        # Statistical signal
        stat_signal = 0
        if len(recent_performance) >= 30:
            try:
                recent_subset = recent_performance[-15:]
                older_subset = recent_performance[-30:-15]
                
                statistic, p_value = stats.ks_2samp(recent_subset, older_subset)
                if p_value < self.config.significance_level:
                    recent_mean = np.mean(recent_subset)
                    older_mean = np.mean(older_subset)
                    
                    if recent_mean < older_mean:
                        stat_signal = -1
                    else:
                        stat_signal = 1
            except:
                pass
        
        # Combine signals
        combined_signal = 0.6 * perf_signal + 0.4 * stat_signal
        
        if abs(combined_signal) > 0.3:  # Threshold for adjustment
            return True, 1 if combined_signal > 0 else -1
        
        return False, 0
    
    def _adjust_window_size(self, direction: int) -> None:
        """Adjust window size based on direction"""
        if direction > 0:  # Grow
            self.current_window_size = min(
                int(self.current_window_size * self.config.window_grow_factor),
                self.config.max_window_size
            )
        elif direction < 0:  # Shrink
            self.current_window_size = max(
                int(self.current_window_size * self.config.window_shrink_factor),
                self.config.min_window_size
            )
        
        self.adaptation_counter += 1
        
        self.logger.info(f"Window size adjusted to {self.current_window_size} "
                        f"(direction: {direction}, adaptations: {self.adaptation_counter})")

class RollingWindowOptimizer:
    """Main rolling window optimization engine"""
    
    def __init__(self, config: RollingWindowConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.RollingWindowOptimizer")
        
        # Core components
        self.window_selector = WindowSelector(config)
        self.window_selector.enable_adaptive_windows = config.enable_adaptive_windows
        
        # Data and model storage
        self.data_buffer = deque(maxlen=config.max_window_size)
        self.label_buffer = deque(maxlen=config.max_window_size)
        
        # Window models
        self.window_models = {}
        self.model_performance = {}
        self.model_weights = {}
        
        # Performance tracking
        self.performance_history = deque(maxlen=config.performance_history_size)
        self.window_metrics_history = []
        
        # State management
        self.is_initialized = False
        self.last_optimization = 0
        self.current_window_id = 0
        
    def add_data_point(self, features: np.ndarray, label: Union[int, float], 
                      timestamp: datetime = None) -> Dict[str, Any]:
        """Add new data point and trigger optimization if needed"""
        
        if timestamp is None:
            timestamp = datetime.now()
        
        # Add to buffers
        self.data_buffer.append(features)
        self.label_buffer.append(label)
        
        # Initialize if needed
        if not self.is_initialized and len(self.data_buffer) >= self.config.initial_window_size:
            self._initialize_system()
        
        # Check if optimization is needed
        optimization_result = None
        if self.is_initialized:
            optimization_result = self._check_and_perform_optimization()
        
        return optimization_result or {'status': 'data_added', 'window_size': len(self.data_buffer)}
    
    def _initialize_system(self) -> None:
        """Initialize the rolling window system"""
        self.logger.info("Initializing rolling window optimization system")
        
        # Create initial window
        initial_window_size = self.config.initial_window_size
        self._create_window(initial_window_size, is_initial=True)
        
        self.is_initialized = True
        self.logger.info(f"System initialized with window size: {initial_window_size}")
    
    def _check_and_perform_optimization(self) -> Optional[Dict[str, Any]]:
        """Check if optimization is needed and perform it"""
        
        # Check optimization frequency
        if len(self.performance_history) - self.last_optimization < self.config.optimization_frequency:
            return None
        
        # Check data requirements
        if len(self.data_buffer) < self.config.min_window_size:
            return None
        
        # Get recent performance
        recent_performance = list(self.performance_history)[-50:]  # Last 50 performances
        
        if len(recent_performance) < 10:
            return None
        
        # Select optimal window size
        optimal_window_size = self.window_selector.select_optimal_window(recent_performance)
        
        # Perform optimization
        optimization_result = self._perform_optimization(optimal_window_size)
        
        self.last_optimization = len(self.performance_history)
        
        return optimization_result
    
    def _perform_optimization(self, target_window_size: int) -> Dict[str, Any]:
        """Perform window optimization"""
        
        self.logger.info(f"Performing optimization with target window size: {target_window_size}")
        
        # Create new window
        new_window_id = self._create_window(target_window_size)
        
        # Train model for new window
        model_performance = self._train_and_evaluate_window_model(new_window_id)
        
        # Update model ensemble if enabled
        if self.config.enable_model_ensemble:
            self._update_model_ensemble(new_window_id, model_performance)
        
        # Record optimization
        optimization_result = {
            'status': 'optimization_completed',
            'new_window_id': new_window_id,
            'window_size': target_window_size,
            'model_performance': model_performance,
            'ensemble_size': len(self.window_models) if self.config.enable_model_ensemble else 1
        }
        
        return optimization_result
    
    def _create_window(self, window_size: int, is_initial: bool = False) -> int:
        """Create a new rolling window"""
        
        self.current_window_id += 1
        window_id = self.current_window_id
        
        # Extract window data
        if len(self.data_buffer) >= window_size:
            window_data = list(self.data_buffer)[-window_size:]
            window_labels = list(self.label_buffer)[-window_size:]
        else:
            window_data = list(self.data_buffer)
            window_labels = list(self.label_buffer)
        
        # Store window information
        window_info = {
            'window_id': window_id,
            'window_size': len(window_data),
            'start_index': len(self.data_buffer) - len(window_data),
            'end_index': len(self.data_buffer),
            'data': np.array(window_data),
            'labels': np.array(window_labels),
            'creation_time': datetime.now(),
            'is_initial': is_initial
        }
        
        self.window_models[window_id] = {
            'info': window_info,
            'model': None,
            'performance': {},
            'is_active': True
        }
        
        return window_id
    
    def _train_and_evaluate_window_model(self, window_id: int) -> Dict[str, Any]:
        """Train and evaluate model for specific window"""
        
        window_info = self.window_models[window_id]['info']
        X = window_info['data']
        y = window_info['labels']
        
        # Determine if classification or regression
        is_classification = len(np.unique(y)) <= 10 and y.dtype in ['object', 'int64']
        
        # Create model
        if is_classification:
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(n_estimators=50, random_state=42)
            scoring = 'accuracy'
        else:
            from sklearn.ensemble import RandomForestRegressor
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            scoring = 'r2'
        
        # Train model
        start_time = datetime.now()
        model.fit(X, y)
        training_time = (datetime.now() - start_time).total_seconds()
        
        # Evaluate model
        performance_metrics = self._calculate_performance_metrics(model, X, y, is_classification)
        
        # Cross-validation if enabled
        cv_score = None
        if self.config.enable_cross_validation and len(X) > self.config.cv_folds * 10:
            try:
                if is_classification:
                    cv = StratifiedKFold(n_splits=min(self.config.cv_folds, len(np.unique(y))))
                else:
                    cv = KFold(n_splits=self.config.cv_folds)
                
                cv_scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)
                cv_score = np.mean(cv_scores)
            except Exception as e:
                self.logger.warning(f"Cross-validation failed: {e}")
        
        # Store results
        self.window_models[window_id]['model'] = model
        self.window_models[window_id]['performance'] = {
            'training_accuracy': performance_metrics['accuracy'],
            'cv_score': cv_score,
            'training_time': training_time,
            'stability': performance_metrics['stability'],
            'timestamp': datetime.now()
        }
        
        # Update performance history
        perf_value = cv_score if cv_score is not None else performance_metrics['accuracy']
        self.performance_history.append(perf_value)
        
        return {
            'accuracy': performance_metrics['accuracy'],
            'cv_score': cv_score,
            'stability': performance_metrics['stability'],
            'training_time': training_time,
            'window_size': len(X)
        }
    
    def _calculate_performance_metrics(self, model: BaseEstimator, 
                                     X: np.ndarray, y: np.ndarray,
                                     is_classification: bool) -> Dict[str, float]:
        """Calculate comprehensive performance metrics"""
        
        predictions = model.predict(X)
        
        if is_classification:
            accuracy = accuracy_score(y, predictions)
            
            # Additional classification metrics
            from sklearn.metrics import precision_score, recall_score, f1_score
            
            precision = precision_score(y, predictions, average='weighted', zero_division=0)
            recall = recall_score(y, predictions, average='weighted', zero_division=0)
            f1 = f1_score(y, predictions, average='weighted', zero_division=0)
            
            # Stability score based on prediction confidence
            if hasattr(model, 'predict_proba'):
                probas = model.predict_proba(X)
                prediction_confidence = np.max(probas, axis=1)
                stability = np.mean(prediction_confidence)
            else:
                stability = 0.8  # Default stability
            
            metrics = {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'stability': stability
            }
        else:
            r2 = r2_score(y, predictions)
            mse = mean_squared_error(y, predictions)
            mae = np.mean(np.abs(y - predictions))
            
            # Stability score based on residual variance
            residuals = y - predictions
            stability = 1.0 / (1.0 + np.var(residuals))
            
            metrics = {
                'accuracy': r2,  # Using R² as main metric
                'mse': mse,
                'mae': mae,
                'stability': stability
            }
        
        return metrics
    
    def _update_model_ensemble(self, new_window_id: int, model_performance: Dict[str, Any]) -> None:
        """Update model ensemble with new model"""
        
        # Add new model to ensemble
        ensemble_weight = self._calculate_ensemble_weight(model_performance)
        self.model_weights[new_window_id] = ensemble_weight
        
        # Trim ensemble if too large
        if len(self.window_models) > self.config.ensemble_size:
            self._trim_ensemble()
        
        # Renormalize weights
        total_weight = sum(self.model_weights.values())
        if total_weight > 0:
            for window_id in self.model_weights:
                self.model_weights[window_id] /= total_weight
        
        self.logger.info(f"Updated ensemble weights: {self.model_weights}")
    
    def _calculate_ensemble_weight(self, model_performance: Dict[str, Any]) -> float:
        """Calculate ensemble weight for a model"""
        
        # Base weight on performance
        accuracy = model_performance.get('accuracy', 0)
        cv_score = model_performance.get('cv_score')
        stability = model_performance.get('stability', 0.5)
        
        # Combine metrics
        if cv_score is not None:
            base_weight = cv_score
        else:
            base_weight = accuracy
        
        # Adjust for stability
        weight = base_weight * stability
        
        # Apply performance weighting if enabled
        if self.config.enable_performance_weighting and len(self.performance_history) > 10:
            recent_performance = np.mean(list(self.performance_history)[-10:])
            performance_factor = weight / (recent_performance + 1e-8)
            weight *= performance_factor
        
        return max(0.01, weight)  # Minimum weight
    
    def _trim_ensemble(self) -> None:
        """Trim ensemble to maintain maximum size"""
        
        # Remove models with lowest weights
        sorted_models = sorted(self.model_weights.items(), key=lambda x: x[1])
        models_to_remove = len(self.window_models) - self.config.ensemble_size
        
        for i in range(models_to_remove):
            window_id_to_remove = sorted_models[i][0]
            if window_id_to_remove in self.window_models:
                del self.window_models[window_id_to_remove]
                del self.model_weights[window_id_to_remove]
    
    def predict(self, features: np.ndarray) -> Union[int, float, np.ndarray]:
        """Make prediction using ensemble of models"""
        
        if not self.window_models:
            raise ValueError("No trained models available")
        
        predictions = []
        weights = []
        
        for window_id, window_data in self.window_models.items():
            if window_data['is_active'] and window_data['model'] is not None:
                try:
                    pred = window_data['model'].predict(features.reshape(1, -1))[0]
                    predictions.append(pred)
                    weights.append(self.model_weights.get(window_id, 1.0 / len(self.window_models)))
                except Exception as e:
                    self.logger.warning(f"Prediction failed for window {window_id}: {e}")
        
        if not predictions:
            raise ValueError("No successful predictions from any model")
        
        # Weighted ensemble prediction
        if len(predictions) == 1:
            return predictions[0]
        else:
            weights = np.array(weights)
            weights = weights / np.sum(weights)  # Normalize
            
            # For classification, use weighted voting
            if isinstance(predictions[0], (int, np.integer)):
                return int(np.average(predictions, weights=weights))
            else:  # regression
                return float(np.average(predictions, weights=weights))
    
    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        """Get prediction probabilities from ensemble"""
        
        if not self.window_models:
            raise ValueError("No trained models available")
        
        all_probas = []
        weights = []
        
        for window_id, window_data in self.window_models.items():
            if (window_data['is_active'] and 
                window_data['model'] is not None and 
                hasattr(window_data['model'], 'predict_proba')):
                
                try:
                    probas = window_data['model'].predict_proba(features.reshape(1, -1))[0]
                    all_probas.append(probas)
                    weights.append(self.model_weights.get(window_id, 1.0 / len(self.window_models)))
                except Exception as e:
                    self.logger.warning(f"Probability prediction failed for window {window_id}: {e}")
        
        if not all_probas:
            raise ValueError("No probability predictions available")
        
        # Weighted average of probabilities
        weights = np.array(weights)
        weights = weights / np.sum(weights)
        
        ensemble_probas = np.average(all_probas, axis=0, weights=weights)
        return ensemble_probas
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        active_models = [wid for wid, wdata in self.window_models.items() if wdata['is_active']]
        
        return {
            'is_initialized': self.is_initialized,
            'data_buffer_size': len(self.data_buffer),
            'active_windows': len(active_models),
            'total_windows': len(self.window_models),
            'current_window_size': self.window_selector.current_window_size,
            'performance_history_size': len(self.performance_history),
            'recent_performance': np.mean(list(self.performance_history)[-10:]) if self.performance_history else None,
            'optimization_count': self.window_selector.adaptation_counter,
            'ensemble_weights': self.model_weights if self.config.enable_model_ensemble else None,
            'last_optimization': self.last_optimization
        }
    
    def get_window_analysis(self) -> Dict[str, Any]:
        """Get detailed window analysis"""
        
        window_analysis = {
            'windows': [],
            'performance_summary': {},
            'window_evolution': []
        }
        
        for window_id, window_data in self.window_models.items():
            if window_data['is_active']:
                window_info = window_data['info']
                performance = window_data['performance']
                
                window_analysis['windows'].append({
                    'window_id': window_id,
                    'size': window_info['window_size'],
                    'creation_time': window_info['creation_time'].isoformat(),
                    'is_initial': window_info['is_initial'],
                    'accuracy': performance.get('training_accuracy'),
                    'cv_score': performance.get('cv_score'),
                    'stability': performance.get('stability'),
                    'training_time': performance.get('training_time'),
                    'weight': self.model_weights.get(window_id, 0)
                })
        
        # Performance summary
        if window_analysis['windows']:
            accuracies = [w['accuracy'] for w in window_analysis['windows'] if w['accuracy'] is not None]
            cv_scores = [w['cv_score'] for w in window_analysis['windows'] if w['cv_score'] is not None]
            
            window_analysis['performance_summary'] = {
                'avg_accuracy': np.mean(accuracies) if accuracies else None,
                'max_accuracy': np.max(accuracies) if accuracies else None,
                'min_accuracy': np.min(accuracies) if accuracies else None,
                'accuracy_std': np.std(accuracies) if len(accuracies) > 1 else None,
                'avg_cv_score': np.mean(cv_scores) if cv_scores else None,
                'max_cv_score': np.max(cv_scores) if cv_scores else None
            }
        
        return window_analysis
    
    def visualize_window_performance(self, save_path: Optional[str] = None) -> Dict[str, str]:
        """Create window performance visualizations"""
        
        if not self.window_models:
            return {}
        
        plots = {}
        
        # Extract performance data
        window_data = []
        for window_id, window_info in self.window_models.items():
            if window_info['is_active'] and window_info['performance']:
                perf = window_info['performance']
                window_data.append({
                    'window_id': window_id,
                    'accuracy': perf.get('training_accuracy'),
                    'cv_score': perf.get('cv_score'),
                    'stability': perf.get('stability'),
                    'training_time': perf.get('training_time'),
                    'creation_time': window_info['info']['creation_time']
                })
        
        if not window_data:
            return plots
        
        # Create plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot 1: Accuracy over windows
        axes[0, 0].plot([w['window_id'] for w in window_data], 
                       [w['accuracy'] for w in window_data], 'b-', label='Training Accuracy')
        if any(w['cv_score'] is not None for w in window_data):
            cv_data = [(w['window_id'], w['cv_score']) for w in window_data if w['cv_score'] is not None]
            axes[0, 0].plot([d[0] for d in cv_data], [d[1] for d in cv_data], 'r-', label='CV Score')
        axes[0, 0].set_xlabel('Window ID')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].set_title('Model Accuracy Over Windows')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Plot 2: Stability over windows
        axes[0, 1].plot([w['window_id'] for w in window_data], 
                       [w['stability'] for w in window_data], 'g-')
        axes[0, 1].set_xlabel('Window ID')
        axes[0, 1].set_ylabel('Stability Score')
        axes[0, 1].set_title('Model Stability Over Windows')
        axes[0, 1].grid(True)
        
        # Plot 3: Training time over windows
        axes[1, 0].bar([w['window_id'] for w in window_data], 
                      [w['training_time'] for w in window_data], alpha=0.7)
        axes[1, 0].set_xlabel('Window ID')
        axes[1, 0].set_ylabel('Training Time (seconds)')
        axes[1, 0].set_title('Training Time Over Windows')
        axes[1, 0].grid(True)
        
        # Plot 4: Performance history
        if self.performance_history:
            recent_perf = list(self.performance_history)[-100:]  # Last 100
            axes[1, 1].plot(range(len(recent_perf)), recent_perf, 'purple')
            axes[1, 1].set_xlabel('Time Step')
            axes[1, 1].set_ylabel('Performance')
            axes[1, 1].set_title('Performance History')
            axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plot_path = f"{save_path}/rolling_window_performance.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plots['window_performance'] = plot_path
        
        plt.close()
        
        return plots

# Quick setup function
def create_rolling_window_optimizer(config: Optional[RollingWindowConfig] = None) -> RollingWindowOptimizer:
    """Create rolling window optimizer with default or custom config"""
    
    if config is None:
        config = RollingWindowConfig()
    
    optimizer = RollingWindowOptimizer(config)
    return optimizer