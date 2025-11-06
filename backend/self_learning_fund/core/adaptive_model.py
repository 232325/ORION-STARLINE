"""
Adaptive Model - O'zini moslashtiruvchi model sinfi
Real-time model adaptation va performance optimization
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta
import copy
from sklearn.base import BaseEstimator
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

@dataclass
class AdaptationConfig:
    """Adaptation konfiguratsiyasi"""
    adaptation_frequency: int = 50  # Har 50 iteratsiyada adaptation
    adaptation_threshold: float = 0.02  # Performance drop threshold
    learning_rate_bounds: Tuple[float, float] = (1e-6, 1.0)
    batch_size_bounds: Tuple[int, int] = (16, 1024)
    patience: int = 20  # Early stopping patience
    min_data_points: int = 100
    drift_detection_window: int = 500
    concept_drift_threshold: float = 0.1

@dataclass
class AdaptationMetrics:
    """Adaptation performance metrikalari"""
    adaptation_count: int
    total_improvement: float
    avg_improvement_per_adaptation: float
    convergence_rate: float
    drift_detection_count: int
    rollback_count: int
    adaptation_time: float

class ConceptDriftDetector:
    """Concept drift ni aniqlash uchun class"""
    
    def __init__(self, config: AdaptationConfig):
        self.config = config
        self.reference_window = []
        self.current_window = []
        self.drift_score = 0.0
        self.drift_detected = False
        
    def update(self, new_data: np.ndarray, predictions: np.ndarray, actual: np.ndarray) -> bool:
        """Drift ni tekshirish va yangilash"""
        # Ma'lumotlarni window larga saqlash
        if len(self.current_window) >= self.config.drift_detection_window:
            self.reference_window = self.current_window[-self.config.drift_detection_window//2:].copy()
            self.current_window = self.current_window[-self.config.drift_detection_window:].copy()
        
        # Prediction accuracy ni hisoblash
        accuracy = np.mean(predictions == actual)
        
        self.current_window.append(accuracy)
        
        # Drift score hisoblash
        if len(self.reference_window) > 10:
            ref_mean = np.mean(self.reference_window)
            curr_mean = np.mean(self.current_window[-50:])  # Last 50 points
            self.drift_score = abs(curr_mean - ref_mean) / (ref_mean + 1e-8)
            
            # Drift detection
            self.drift_detected = self.drift_score > self.config.concept_drift_threshold
            
        return self.drift_detected
    
    def get_drift_score(self) -> float:
        return self.drift_score
    
    def is_drift_detected(self) -> bool:
        return self.drift_detected

class AdaptiveModel:
    """O'zini moslashtiruvchi model"""
    
    def __init__(self, base_model: BaseEstimator, config: AdaptationConfig):
        self.base_model = base_model
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{base_model.__class__.__name__}")
        
        # Adaptation state
        self.current_learning_rate = 0.001
        self.current_batch_size = 32
        self.adaptation_history = []
        self.performance_history = []
        self.best_performance = float('-inf')
        self.patience_counter = 0
        
        # Drift detection
        self.drift_detector = ConceptDriftDetector(config)
        
        # Scaler for preprocessing
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Modelni o'qitish"""
        # Data preprocessing
        X_scaled = self.scaler.fit_transform(X)
        
        # Model fitting
        self.base_model.fit(X_scaled, y)
        self.is_fitted = True
        
        # Baseline performance o'rnatish
        predictions = self.predict(X)
        accuracy = np.mean(predictions == y)
        self.best_performance = accuracy
        
        self.logger.info(f"Model fitted with baseline accuracy: {accuracy:.4f}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Prediction qilish"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X_scaled = self.scaler.transform(X)
        return self.base_model.predict(X_scaled)
    
    def update(self, new_X: np.ndarray, new_y: np.ndarray) -> bool:
        """Online model update"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before update")
        
        adaptation_performed = False
        
        # Performance evaluation
        predictions = self.predict(new_X)
        current_accuracy = np.mean(predictions == new_y)
        
        # Concept drift detection
        drift_detected = self.drift_detector.update(new_X, predictions, new_y)
        
        # Adaptation trigger conditions
        should_adapt = (
            drift_detected or
            current_accuracy < self.best_performance * (1 - self.config.adaptation_threshold) or
            len(self.performance_history) % self.config.adaptation_frequency == 0
        )
        
        if should_adapt:
            adaptation_performed = self._perform_adaptation(new_X, new_y, current_accuracy)
        
        # Performance history update
        self.performance_history.append(current_accuracy)
        
        # Track adaptation
        self.adaptation_history.append({
            'timestamp': datetime.now(),
            'drift_detected': drift_detected,
            'accuracy': current_accuracy,
            'adaptation_performed': adaptation_performed
        })
        
        return adaptation_performed
    
    def _perform_adaptation(self, X: np.ndarray, y: np.ndarray, current_accuracy: float) -> bool:
        """Adaptation strategiyasini qo'llash"""
        self.logger.info("Starting model adaptation...")
        
        best_config = self._optimize_hyperparameters(X, y)
        self.current_learning_rate = best_config['learning_rate']
        self.current_batch_size = best_config['batch_size']
        
        # Model retraining with new parameters
        X_scaled = self.scaler.transform(X)
        
        # Simulate learning rate adjustment
        if hasattr(self.base_model, 'learning_rate'):
            self.base_model.learning_rate = self.current_learning_rate
        
        # Incremental learning if supported
        if hasattr(self.base_model, 'partial_fit'):
            self.base_model.partial_fit(X_scaled, y)
        else:
            # For non-incremental models, use warm start or retrain
            if hasattr(self.base_model, 'warm_start'):
                self.base_model.warm_start = True
                self.base_model.fit(X_scaled, y)
        
        # Evaluate adaptation
        new_predictions = self.predict(X)
        new_accuracy = np.mean(new_predictions == y)
        
        # Accept or rollback adaptation
        if new_accuracy > current_accuracy or drift_detected:
            self.best_performance = max(self.best_performance, new_accuracy)
            self.patience_counter = 0
            self.logger.info(f"Adaptation successful: {new_accuracy:.4f} (improvement: {new_accuracy - current_accuracy:.4f})")
            return True
        else:
            self.patience_counter += 1
            self.logger.warning(f"Adaptation failed: {new_accuracy:.4f} vs {current_accuracy:.4f}")
            
            # Rollback if performance degraded significantly
            if new_accuracy < current_accuracy * (1 - self.config.adaptation_threshold * 2):
                self.logger.warning("Significant performance degradation detected, maintaining previous state")
            
            return False
    
    def _optimize_hyperparameters(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Hyperparameter optimization"""
        learning_rates = np.logspace(np.log10(self.config.learning_rate_bounds[0]), 
                                   np.log10(self.config.learning_rate_bounds[1]), 5)
        batch_sizes = np.linspace(self.config.batch_size_bounds[0], 
                                self.config.batch_size_bounds[1], 5, dtype=int)
        
        best_score = -np.inf
        best_config = {}
        
        # Grid search for best hyperparameters
        for lr in learning_rates:
            for bs in batch_sizes:
                # Create temporary model with test parameters
                temp_model = copy.deepcopy(self.base_model)
                if hasattr(temp_model, 'learning_rate'):
                    temp_model.learning_rate = lr
                
                # Quick validation
                try:
                    X_scaled = self.scaler.transform(X)
                    if hasattr(temp_model, 'partial_fit'):
                        temp_model.partial_fit(X_scaled[:bs], y[:bs])
                    else:
                        # Use small subset for testing
                        temp_model.fit(X_scaled[:min(bs, len(X))], y[:min(bs, len(y))])
                    
                    predictions = temp_model.predict(X_scaled[:min(100, len(X))])
                    score = np.mean(predictions == y[:min(100, len(y))])
                    
                    if score > best_score:
                        best_score = score
                        best_config = {
                            'learning_rate': lr,
                            'batch_size': bs
                        }
                except:
                    continue
        
        # Default configuration if no improvement found
        if not best_config:
            best_config = {
                'learning_rate': self.current_learning_rate,
                'batch_size': self.current_batch_size
            }
        
        return best_config
    
    def get_adaptation_metrics(self) -> AdaptationMetrics:
        """Adaptation metrics ni olish"""
        if not self.adaptation_history:
            return AdaptationMetrics(
                adaptation_count=0,
                total_improvement=0,
                avg_improvement_per_adaptation=0,
                convergence_rate=0,
                drift_detection_count=0,
                rollback_count=0,
                adaptation_time=0
            )
        
        # Metrics calculation
        adaptation_count = len(self.adaptation_history)
        drift_count = sum(1 for h in self.adaptation_history if h['drift_detected'])
        
        # Calculate improvement
        accuracies = [h['accuracy'] for h in self.adaptation_history]
        improvements = [acc - accuracies[0] for acc in accuracies]
        total_improvement = sum(improvements)
        
        # Convergence rate (improvement per adaptation)
        avg_improvement = total_improvement / adaptation_count if adaptation_count > 0 else 0
        
        # Adaptation time estimation
        avg_adaptation_time = 0.1  # Simulated adaptation time
        
        return AdaptationMetrics(
            adaptation_count=adaptation_count,
            total_improvement=total_improvement,
            avg_improvement_per_adaptation=avg_improvement,
            convergence_rate=avg_improvement,
            drift_detection_count=drift_count,
            rollback_count=0,  # Not tracking rollbacks explicitly
            adaptation_time=avg_adaptation_time * adaptation_count
        )
    
    def get_drift_summary(self) -> Dict[str, Any]:
        """Drift detection summary"""
        return {
            'drift_score': self.drift_detector.get_drift_score(),
            'drift_detected': self.drift_detector.is_drift_detected(),
            'window_size': self.config.drift_detection_window,
            'threshold': self.config.concept_drift_threshold
        }
    
    def should_stop_adaptation(self) -> bool:
        """Adaptation ni to'xtatish kerakligini aniqlash"""
        return self.patience_counter >= self.config.patience
    
    def reset_adaptation(self) -> None:
        """Adaptation state ni qayta o'rnatish"""
        self.patience_counter = 0
        self.best_performance = float('-inf')
        self.adaptation_history.clear()
        self.performance_history.clear()
        self.logger.info("Adaptation state reset")

class AdaptiveEnsemble:
    """Adaptive ensemble model"""
    
    def __init__(self, models: List[AdaptiveModel], voting_strategy: str = 'soft'):
        self.models = models
        self.voting_strategy = voting_strategy
        self.logger = logging.getLogger(f"{__name__}.AdaptiveEnsemble")
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Ensemble prediction"""
        predictions = [model.predict(X) for model in self.models]
        
        if self.voting_strategy == 'soft':
            # Soft voting (probability averaging)
            return np.round(np.mean(predictions, axis=0)).astype(int)
        else:
            # Hard voting (majority voting)
            stacked = np.stack(predictions, axis=1)
            return np.round(np.mean(stacked, axis=1)).astype(int)
    
    def update(self, new_X: np.ndarray, new_y: np.ndarray) -> Dict[str, Any]:
        """Update all models in ensemble"""
        update_results = {}
        
        for i, model in enumerate(self.models):
            try:
                updated = model.update(new_X, new_y)
                update_results[f'model_{i}'] = {
                    'updated': updated,
                    'adaptation_metrics': model.get_adaptation_metrics()
                }
            except Exception as e:
                self.logger.error(f"Error updating model {i}: {e}")
                update_results[f'model_{i}'] = {'updated': False, 'error': str(e)}
        
        return update_results
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Ensemble performance summary"""
        summary = {
            'n_models': len(self.models),
            'voting_strategy': self.voting_strategy,
            'individual_performance': []
        }
        
        for model in self.models:
            metrics = model.get_adaptation_metrics()
            drift_summary = model.get_drift_summary()
            
            summary['individual_performance'].append({
                'adaptation_count': metrics.adaptation_count,
                'total_improvement': metrics.total_improvement,
                'drift_detected': drift_summary['drift_detected'],
                'drift_score': drift_summary['drift_score']
            })
        
        return summary