"""
Online Learning - Real-time o'qitish va adaptation
Streaming data va incremental learning algorithms
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import warnings
from collections import deque
from sklearn.linear_model import SGDClassifier, SGDRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error
warnings.filterwarnings('ignore')

@dataclass
class OnlineLearningConfig:
    """Online learning konfiguratsiyasi"""
    learning_rate: float = 0.01
    batch_size: int = 32
    update_frequency: int = 10
    decay_rate: float = 0.95
    min_learning_rate: float = 1e-6
    buffer_size: int = 1000
    forget_factor: float = 0.1  # How much to forget old data
    adaptation_threshold: float = 0.02

@dataclass
class StreamData:
    """Streaming data ma'lumotlari"""
    features: np.ndarray
    labels: np.ndarray
    timestamp: datetime
    metadata: Dict[str, Any] = None

class DataStreamBuffer:
    """Streaming data buffer management"""
    
    def __init__(self, config: OnlineLearningConfig):
        self.config = config
        self.buffer = deque(maxlen=config.buffer_size)
        self.current_batch = []
        self.batch_count = 0
        
    def add_data(self, features: np.ndarray, labels: np.ndarray, metadata: Dict = None) -> bool:
        """Buffer ga ma'lumot qo'shish"""
        stream_data = StreamData(
            features=features,
            labels=labels,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.buffer.append(stream_data)
        self.current_batch.append(stream_data)
        
        # Check if batch is ready for processing
        return len(self.current_batch) >= self.config.batch_size
    
    def get_batch(self) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """Ready batch ni olish"""
        if len(self.current_batch) < self.config.batch_size:
            return None
        
        # Extract batch data
        features = np.array([data.features for data in self.current_batch])
        labels = np.array([data.labels for data in self.current_batch])
        
        # Clear current batch
        self.current_batch.clear()
        self.batch_count += 1
        
        return features, labels
    
    def get_streaming_window(self, window_size: int = 100) -> Iterator[StreamData]:
        """Recent window data ni olish"""
        recent_data = list(self.buffer)[-window_size:]
        for data in recent_data:
            yield data
    
    def apply_forgetting(self) -> None:
        """Eski ma'lumotlarni unutish (forgetting factor)"""
        if len(self.buffer) < self.config.buffer_size // 2:
            return
        
        # Randomly sample to apply forgetting
        keep_probability = 1 - self.config.forget_factor
        sampled_buffer = []
        
        for data in self.buffer:
            if np.random.random() < keep_probability:
                sampled_buffer.append(data)
        
        # Update buffer with sampled data
        self.buffer.clear()
        for data in sampled_buffer:
            if len(self.buffer) < self.config.buffer_size:
                self.buffer.append(data)

class AdaptiveSGD:
    """Adaptive Stochastic Gradient Descent"""
    
    def __init__(self, config: OnlineLearningConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.AdaptiveSGD")
        
        # Model components
        self.model = SGDClassifier(
            loss='log_loss',
            learning_rate='adaptive',
            eta0=config.learning_rate,
            random_state=42
        )
        self.scaler = StandardScaler()
        
        # Learning state
        self.current_learning_rate = config.learning_rate
        self.iteration_count = 0
        self.performance_history = deque(maxlen=100)
        self.adaptation_history = []
        
        # Training state
        self.is_fitted = False
        self.first_batch = True
        
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Initial fitting"""
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit model
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        self.first_batch = False
        
        self.logger.info(f"Model fitted with {X.shape[0]} samples")
    
    def partial_fit(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Incremental learning"""
        if not self.is_fitted:
            # First time fitting
            self.fit(X, y)
            return {'accuracy': 1.0, 'learning_rate': self.current_learning_rate}
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Calculate performance before update
        predictions_before = self.model.predict(X_scaled)
        accuracy_before = accuracy_score(y, predictions_before)
        
        # Apply forgetting if needed
        if self.iteration_count % 100 == 0:
            self._apply_forgetting(X_scaled, y)
        
        # Partial fit
        self.model.partial_fit(X_scaled, y, classes=np.unique(y))
        
        # Calculate performance after update
        predictions_after = self.model.predict(X_scaled)
        accuracy_after = accuracy_score(y, predictions_after)
        
        # Adapt learning rate
        improvement = accuracy_after - accuracy_before
        self._adapt_learning_rate(improvement)
        
        # Record performance
        self.performance_history.append(accuracy_after)
        
        # Update learning rate in model
        self.model.eta0 = self.current_learning_rate
        
        self.iteration_count += 1
        
        return {
            'accuracy_before': accuracy_before,
            'accuracy_after': accuracy_after,
            'improvement': improvement,
            'learning_rate': self.current_learning_rate
        }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Prediction qilish"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Prediction probabilities ni olish"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)
    
    def _adapt_learning_rate(self, improvement: float) -> None:
        """Learning rate ni adapt qilish"""
        # Adaptive learning rate based on performance
        if improvement > 0:
            # Performance improving - increase learning rate slightly
            self.current_learning_rate *= 1.01
        else:
            # Performance declining - decrease learning rate
            self.current_learning_rate *= 0.99
        
        # Apply bounds
        min_lr = self.config.min_learning_rate
        max_lr = self.config.learning_rate * 10
        self.current_learning_rate = np.clip(self.current_learning_rate, min_lr, max_lr)
        
        # Decay over time
        decay_factor = self.config.decay_rate ** (self.iteration_count / 1000)
        self.current_learning_rate *= decay_factor
        
        # Record adaptation
        self.adaptation_history.append({
            'iteration': self.iteration_count,
            'improvement': improvement,
            'learning_rate': self.current_learning_rate,
            'timestamp': datetime.now()
        })
    
    def _apply_forgetting(self, X: np.ndarray, y: np.ndarray) -> None:
        """Forgetting mechanism ni qo'llash"""
        # Simple forgetting: retrain on subset of data with decay
        if len(self.performance_history) < 10:
            return
        
        recent_performance = np.mean(list(self.performance_history)[-10:])
        if recent_performance < 0.7:  # Poor performance threshold
            # Apply forgetting by reducing model confidence
            self.logger.info("Applying forgetting mechanism due to poor performance")
            
            # Small retraining with weighted samples
            weights = np.ones(len(X)) * (1 - self.config.forget_factor)
            self.model.partial_fit(X, y, classes=np.unique(y), sample_weight=weights)

class OnlineRandomForest:
    """Online Random Forest for streaming data"""
    
    def __init__(self, config: OnlineLearningConfig, n_trees: int = 10):
        self.config = config
        self.n_trees = n_trees
        self.logger = logging.getLogger(f"{__name__}.OnlineRandomForest")
        
        self.forests = []
        self.tree_counters = []
        self.scaler = StandardScaler()
        self.is_fitted = False
        
        # Performance tracking
        self.performance_history = deque(maxlen=100)
        
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Initial fitting"""
        X_scaled = self.scaler.fit_transform(X)
        
        # Create multiple random forests with different parameters
        for i in range(self.n_trees):
            rf = RandomForestClassifier(
                n_estimators=1,  # Single tree per forest
                max_features='sqrt',
                random_state=42 + i,
                warm_start=True
            )
            rf.fit(X_scaled, y)
            self.forests.append(rf)
            self.tree_counters.append(1)
        
        self.is_fitted = True
        self.logger.info(f"Online Random Forest fitted with {self.n_trees} forests")
    
    def partial_fit(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Incremental learning"""
        if not self.is_fitted:
            self.fit(X, y)
            return {'accuracy': 1.0}
        
        X_scaled = self.scaler.transform(X)
        
        # Calculate ensemble prediction
        predictions_before = self.predict(X)
        accuracy_before = accuracy_score(y, predictions_before)
        
        # Update each forest
        for i, forest in enumerate(self.forests):
            # Progressive tree growth
            if self.tree_counters[i] < 10:  # Max 10 trees per forest
                forest.n_estimators += 1
                self.tree_counters[i] += 1
            
            # Partial fit with new data
            forest.partial_fit(X_scaled, y, classes=np.unique(y))
        
        # Evaluate performance
        predictions_after = self.predict(X)
        accuracy_after = accuracy_score(y, predictions_after)
        
        self.performance_history.append(accuracy_after)
        
        return {
            'accuracy_before': accuracy_before,
            'accuracy_after': accuracy_after,
            'improvement': accuracy_after - accuracy_before
        }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Ensemble prediction"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X_scaled = self.scaler.transform(X)
        
        # Get predictions from all forests
        forest_predictions = []
        for forest in self.forests:
            pred = forest.predict(X_scaled)
            forest_predictions.append(pred)
        
        # Majority voting
        predictions_array = np.array(forest_predictions)
        ensemble_pred = np.round(np.mean(predictions_array, axis=0)).astype(int)
        
        return ensemble_pred
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Ensemble prediction probabilities"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X_scaled = self.scaler.transform(X)
        
        # Get probabilities from all forests
        forest_probabilities = []
        for forest in self.forests:
            proba = forest.predict_proba(X_scaled)
            forest_probabilities.append(proba)
        
        # Average probabilities
        ensemble_proba = np.mean(forest_probabilities, axis=0)
        return ensemble_proba

class AdaptiveNeuralNetwork:
    """Adaptive Neural Network for online learning"""
    
    def __init__(self, config: OnlineLearningConfig, hidden_layer_sizes: Tuple = (100, 50)):
        self.config = config
        self.hidden_layer_sizes = hidden_layer_sizes
        self.logger = logging.getLogger(f"{__name__}.AdaptiveNN")
        
        # Model components
        self.model = MLPClassifier(
            hidden_layer_sizes=hidden_layer_sizes,
            learning_rate='adaptive',
            learning_rate_init=config.learning_rate,
            max_iter=1,  # Single epoch per update
            warm_start=True,
            random_state=42
        )
        
        self.scaler = StandardScaler()
        self.is_fitted = False
        
        # Adaptation state
        self.performance_history = deque(maxlen=100)
        self.adaptation_frequency = 50
        
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Initial fitting"""
        X_scaled = self.scaler.fit_transform(X)
        
        # Initial training
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        
        self.logger.info("Adaptive Neural Network fitted")
    
    def partial_fit(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Online learning with adaptation"""
        if not self.is_fitted:
            self.fit(X, y)
            return {'loss': 0.0, 'learning_rate': self.config.learning_rate}
        
        X_scaled = self.scaler.transform(X)
        
        # Calculate performance before
        predictions_before = self.model.predict(X_scaled)
        accuracy_before = accuracy_score(y, predictions_before)
        
        # Check if adaptation is needed
        if len(self.performance_history) >= self.adaptation_frequency:
            recent_performance = np.mean(list(self.performance_history)[-self.adaptation_frequency:])
            if recent_performance < accuracy_before - self.config.adaptation_threshold:
                self._adapt_architecture(X_scaled, y)
        
        # Incremental training
        self.model.partial_fit(X_scaled, y, classes=np.unique(y))
        
        # Calculate loss
        try:
            # Get loss score (if available)
            loss_score = self.model.score(X_scaled, y)
        except:
            loss_score = 1 - accuracy_before
        
        # Calculate performance after
        predictions_after = self.model.predict(X_scaled)
        accuracy_after = accuracy_score(y, predictions_after)
        
        self.performance_history.append(accuracy_after)
        
        return {
            'accuracy_before': accuracy_before,
            'accuracy_after': accuracy_after,
            'loss': loss_score,
            'learning_rate': self.model.learning_rate_init
        }
    
    def _adapt_architecture(self, X: np.ndarray, y: np.ndarray) -> None:
        """Network architecture adaptation"""
        current_performance = np.mean(list(self.performance_history)[-20:])
        
        if current_performance < 0.7:
            # Add neurons to hidden layers
            new_hidden_layer_sizes = tuple(
                max(10, size + 10) for size in self.hidden_layer_sizes
            )
            
            if new_hidden_layer_sizes != self.hidden_layer_sizes:
                self.logger.info(f"Adapting architecture: {self.hidden_layer_sizes} -> {new_hidden_layer_sizes}")
                
                # Create new model with adapted architecture
                self.model = MLPClassifier(
                    hidden_layer_sizes=new_hidden_layer_sizes,
                    learning_rate='adaptive',
                    learning_rate_init=self.config.learning_rate,
                    max_iter=1,
                    warm_start=True,
                    random_state=42
                )
                
                # Refit with current data
                self.model.fit(X, y)
                self.hidden_layer_sizes = new_hidden_layer_sizes
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Prediction"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Prediction probabilities"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)

class OnlineEnsembleLearning:
    """Online ensemble learning combining multiple models"""
    
    def __init__(self, config: OnlineLearningConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.OnlineEnsemble")
        
        # Initialize individual models
        self.sgd_model = AdaptiveSGD(config)
        self.rf_model = OnlineRandomForest(config)
        self.nn_model = AdaptiveNeuralNetwork(config)
        
        # Ensemble weights
        self.ensemble_weights = {
            'sgd': 0.33,
            'rf': 0.34,
            'nn': 0.33
        }
        
        # Performance tracking
        self.individual_performance = {
            'sgd': deque(maxlen=50),
            'rf': deque(maxlen=50),
            'nn': deque(maxlen=50)
        }
        
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit all models"""
        self.sgd_model.fit(X, y)
        self.rf_model.fit(X, y)
        self.nn_model.fit(X, y)
        
        self.logger.info("Online ensemble fitted")
    
    def partial_fit(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Update all models"""
        # Update individual models
        sgd_metrics = self.sgd_model.partial_fit(X, y)
        rf_metrics = self.rf_model.partial_fit(X, y)
        nn_metrics = self.nn_model.partial_fit(X, y)
        
        # Track individual performance
        self.individual_performance['sgd'].append(sgd_metrics['accuracy_after'])
        self.individual_performance['rf'].append(rf_metrics['accuracy_after'])
        self.individual_performance['nn'].append(nn_metrics['accuracy_after'])
        
        # Update ensemble weights based on recent performance
        self._update_ensemble_weights()
        
        return {
            'sgd_metrics': sgd_metrics,
            'rf_metrics': rf_metrics,
            'nn_metrics': nn_metrics,
            'ensemble_weights': self.ensemble_weights
        }
    
    def _update_ensemble_weights(self) -> None:
        """Ensemble weight larni yangilash"""
        if all(len(perf) >= 10 for perf in self.individual_performance.values()):
            # Calculate recent average performance
            recent_performance = {
                model: np.mean(list(perf)[-10:]) 
                for model, perf in self.individual_performance.items()
            }
            
            # Normalize weights based on performance
            total_performance = sum(recent_performance.values())
            if total_performance > 0:
                self.ensemble_weights = {
                    model: perf / total_performance 
                    for model, perf in recent_performance.items()
                }
                
                self.logger.info(f"Updated ensemble weights: {self.ensemble_weights}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Ensemble prediction"""
        # Get individual predictions
        sgd_pred = self.sgd_model.predict(X)
        rf_pred = self.rf_model.predict(X)
        nn_pred = self.nn_model.predict(X)
        
        # Weighted ensemble voting
        ensemble_pred = (
            self.ensemble_weights['sgd'] * sgd_pred +
            self.ensemble_weights['rf'] * rf_pred +
            self.ensemble_weights['nn'] * nn_pred
        )
        
        return np.round(ensemble_pred).astype(int)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Ensemble prediction probabilities"""
        # Get individual probabilities
        sgd_proba = self.sgd_model.predict_proba(X)
        rf_proba = self.rf_model.predict_proba(X)
        nn_proba = self.nn_model.predict_proba(X)
        
        # Weighted ensemble averaging
        ensemble_proba = (
            self.ensemble_weights['sgd'] * sgd_proba +
            self.ensemble_weights['rf'] * rf_proba +
            self.ensemble_weights['nn'] * nn_proba
        )
        
        return ensemble_proba
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Individual model performance summary"""
        return {
            'sgd_performance': {
                'recent_accuracy': np.mean(list(self.individual_performance['sgd'])[-10:]) if self.individual_performance['sgd'] else 0,
                'history_length': len(self.individual_performance['sgd'])
            },
            'rf_performance': {
                'recent_accuracy': np.mean(list(self.individual_performance['rf'])[-10:]) if self.individual_performance['rf'] else 0,
                'history_length': len(self.individual_performance['rf'])
            },
            'nn_performance': {
                'recent_accuracy': np.mean(list(self.individual_performance['nn'])[-10:]) if self.individual_performance['nn'] else 0,
                'history_length': len(self.individual_performance['nn'])
            },
            'ensemble_weights': self.ensemble_weights
        }

class StreamProcessor:
    """Real-time stream processing pipeline"""
    
    def __init__(self, config: OnlineLearningConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.StreamProcessor")
        
        # Data buffer
        self.buffer = DataStreamBuffer(config)
        
        # Model
        self.model = OnlineEnsembleLearning(config)
        
        # Processing statistics
        self.stats = {
            'total_samples_processed': 0,
            'total_batches_processed': 0,
            'average_batch_accuracy': 0,
            'last_update_time': None
        }
        
    def process_stream(self, data_stream: Iterator[Tuple[np.ndarray, np.ndarray]]) -> Iterator[Dict[str, Any]]:
        """Process streaming data"""
        for features, labels in data_stream:
            # Add to buffer
            batch_ready = self.buffer.add_data(features, labels)
            
            # Get batch if ready
            batch_data = self.buffer.get_batch()
            
            if batch_data:
                X_batch, y_batch = batch_data
                
                # Update model
                update_metrics = self.model.partial_fit(X_batch, y_batch)
                
                # Generate prediction for next batch
                prediction = self.model.predict(X_batch)
                accuracy = np.mean(prediction == y_batch)
                
                # Update statistics
                self._update_statistics(accuracy)
                
                yield {
                    'prediction': prediction,
                    'accuracy': accuracy,
                    'update_metrics': update_metrics,
                    'model_performance': self.model.get_model_performance(),
                    'batch_size': len(X_batch),
                    'total_samples': self.stats['total_samples_processed']
                }
                
                # Apply forgetting periodically
                if self.stats['total_batches_processed'] % 100 == 0:
                    self.buffer.apply_forgetting()
    
    def predict_single(self, features: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Single prediction"""
        return self.model.predict(features.reshape(1, -1))[0], self.model.predict_proba(features.reshape(1, -1))[0]
    
    def _update_statistics(self, accuracy: float) -> None:
        """Statistics ni yangilash"""
        self.stats['total_samples_processed'] += 1
        self.stats['total_batches_processed'] += 1
        self.stats['average_batch_accuracy'] = (
            (self.stats['average_batch_accuracy'] * (self.stats['total_batches_processed'] - 1) + accuracy) /
            self.stats['total_batches_processed']
        )
        self.stats['last_update_time'] = datetime.now()
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Processing statistics"""
        return {
            **self.stats,
            'buffer_size': len(self.buffer.buffer),
            'current_batch_size': len(self.buffer.current_batch),
            'model_info': self.model.get_model_performance()
        }