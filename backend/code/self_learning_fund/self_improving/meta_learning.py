"""
Meta-Learning - "Learning to Learn" approach
Model-agnostic meta-learning, few-shot learning, va hyperparameter optimization
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import json
from abc import ABC, abstractmethod
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
from sklearn.metrics import accuracy_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

@dataclass
class MetaLearningConfig:
    """Meta-learning konfiguratsiyasi"""
    meta_learning_rate: float = 0.001
    adaptation_steps: int = 5
    meta_batch_size: int = 4
    adaptation_batch_size: int = 10
    num_tasks: int = 100
    inner_loop_steps: int = 1
    meta_lr_decay: float = 0.95
    adaptation_lr: float = 0.1
    task_similarity_threshold: float = 0.7
    memory_size: int = 1000

@dataclass
class Task:
    """Learning task ma'lumotlari"""
    task_id: str
    support_set: Tuple[np.ndarray, np.ndarray]  # (X_support, y_support)
    query_set: Tuple[np.ndarray, np.ndarray]    # (X_query, y_query)
    task_metadata: Dict[str, Any] = field(default_factory=dict)
    task_difficulty: float = 0.0
    domain: str = "general"

class ModelAgnosticMetaLearner:
    """MAML (Model-Agnostic Meta-Learning) implementation"""
    
    def __init__(self, config: MetaLearningConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.MAML")
        
        # Meta-parameters
        self.meta_parameters = {}
        self.meta_gradients = {}
        self.task_performances = {}
        
        # Learning state
        self.iteration = 0
        self.meta_losses = []
        self.task_similarities = {}
        
        # Model templates
        self.base_models = {}
        self.adapted_models = {}
        
        # Task memory
        self.task_memory = []
        self.successful_tasks = []
        self.failed_tasks = []
    
    def register_base_model(self, model_name: str, model_class: type, 
                          default_params: Dict[str, Any] = None) -> None:
        """Base model ni ro'yxatga olish"""
        default_params = default_params or {}
        self.base_models[model_name] = {
            'class': model_class,
            'default_params': default_params,
            'meta_parameters': {}
        }
        
        self.logger.info(f"Registered base model: {model_name}")
    
    def meta_train(self, tasks: List[Task], validation_tasks: Optional[List[Task]] = None) -> Dict[str, Any]:
        """Meta-training process"""
        self.logger.info(f"Starting meta-training with {len(tasks)} tasks")
        
        meta_training_history = []
        
        for iteration in range(self.config.num_tasks):
            self.iteration = iteration
            
            # Sample meta-batch of tasks
            meta_batch = self._sample_meta_batch(tasks)
            
            # Meta-training step
            meta_loss = self._meta_training_step(meta_batch)
            meta_training_history.append({
                'iteration': iteration,
                'meta_loss': meta_loss,
                'task_count': len(meta_batch)
            })
            
            # Update meta-learning rate
            if iteration % 20 == 0:
                self.config.meta_learning_rate *= self.config.meta_lr_decay
            
            # Validation
            if validation_tasks and iteration % 50 == 0:
                val_performance = self._evaluate_meta_learning(validation_tasks)
                self.logger.info(f"Validation at iteration {iteration}: {val_performance:.4f}")
        
        # Final evaluation
        final_performance = self._evaluate_meta_learning(validation_tasks or tasks[:20])
        
        self.logger.info("Meta-training completed")
        return {
            'training_history': meta_training_history,
            'final_performance': final_performance,
            'meta_parameters': self.meta_parameters,
            'task_similarities': self.task_similarities
        }
    
    def _sample_meta_batch(self, tasks: List[Task]) -> List[Task]:
        """Meta-batch sampling"""
        batch_size = min(self.config.meta_batch_size, len(tasks))
        return np.random.choice(tasks, size=batch_size, replace=False).tolist()
    
    def _meta_training_step(self, meta_batch: List[Task]) -> float:
        """Single meta-training step"""
        total_meta_loss = 0.0
        
        for task in meta_batch:
            # Inner loop: adapt model to task
            adapted_model, task_loss = self._inner_loop_adaptation(task)
            
            # Outer loop: compute meta-loss on query set
            meta_loss = self._compute_meta_loss(adapted_model, task)
            total_meta_loss += meta_loss
        
        # Average meta-loss
        average_meta_loss = total_meta_loss / len(meta_batch)
        
        # Meta-gradient update
        self._meta_update(average_meta_loss)
        
        return average_meta_loss
    
    def _inner_loop_adaptation(self, task: Task) -> Tuple[Any, float]:
        """Inner loop adaptation (few-shot learning)"""
        X_support, y_support = task.support_set
        X_query, y_query = task.query_set
        
        # Initialize or adapt model
        model = self._initialize_task_model(task)
        
        # Adaptation steps
        for step in range(self.config.inner_loop_steps):
            # Gradient descent on support set
            model = self._gradient_descent_step(model, X_support, y_support)
            
            # Evaluate on query set for early stopping
            predictions = model.predict(X_query)
            task_loss = mean_squared_error(y_query, predictions) if len(np.unique(y_query)) > 2 else accuracy_score(y_query, predictions)
            
            # Store adapted model
            self.adapted_models[f"{task.task_id}_step_{step}"] = model
        
        return model, task_loss
    
    def _initialize_task_model(self, task: Task) -> Any:
        """Initialize model for specific task"""
        # Find similar previous tasks
        similar_tasks = self._find_similar_tasks(task)
        
        # Use best parameters from similar tasks if available
        if similar_tasks:
            best_task = max(similar_tasks, key=lambda t: t.task_difficulty)
            model_params = self._get_best_params_for_task(best_task)
        else:
            # Use meta-parameters or default
            model_params = self._get_default_params()
        
        # Create model instance
        model_class = list(self.base_models.values())[0]['class']  # Use first registered model
        model = model_class(**model_params)
        
        return model
    
    def _gradient_descent_step(self, model: Any, X: np.ndarray, y: np.ndarray) -> Any:
        """Single gradient descent step"""
        # Simple gradient approximation using parameter perturbation
        original_params = self._get_model_params(model)
        
        # Compute gradients (simplified)
        gradients = self._approximate_gradients(model, X, y)
        
        # Update parameters
        updated_params = {}
        for param_name, param_value in original_params.items():
            if param_name in gradients:
                updated_params[param_name] = param_value - self.config.adaptation_lr * gradients[param_name]
            else:
                updated_params[param_name] = param_value
        
        # Create new model with updated parameters
        new_model = self._create_model_with_params(model, updated_params)
        
        return new_model
    
    def _approximate_gradients(self, model: Any, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Approximate gradients using finite differences"""
        gradients = {}
        epsilon = 1e-7
        
        original_params = self._get_model_params(model)
        
        for param_name, param_value in original_params.items():
            if isinstance(param_value, (int, float)):
                # Perturb parameter
                perturbed_value = param_value + epsilon
                
                # Create perturbed model
                perturbed_params = original_params.copy()
                perturbed_params[param_name] = perturbed_value
                perturbed_model = self._create_model_with_params(model, perturbed_params)
                
                # Evaluate performance difference
                try:
                    original_loss = self._evaluate_model(model, X, y)
                    perturbed_loss = self._evaluate_model(perturbed_model, X, y)
                    
                    # Numerical gradient
                    gradient = (perturbed_loss - original_loss) / epsilon
                    gradients[param_name] = gradient
                except:
                    gradients[param_name] = 0.0
        
        return gradients
    
    def _compute_meta_loss(self, adapted_model: Any, task: Task) -> float:
        """Compute meta-loss on query set"""
        X_query, y_query = task.query_set
        
        try:
            predictions = adapted_model.predict(X_query)
            if len(np.unique(y_query)) > 2:
                # Regression task
                loss = mean_squared_error(y_query, predictions)
            else:
                # Classification task
                loss = 1 - accuracy_score(y_query, predictions)
            return loss
        except Exception as e:
            self.logger.warning(f"Meta-loss computation failed: {e}")
            return 1.0
    
    def _meta_update(self, meta_loss: float) -> None:
        """Meta-parameter update"""
        # Store meta-loss for history
        self.meta_losses.append(meta_loss)
        
        # Simplified meta-gradient update
        self.config.meta_learning_rate = max(1e-6, self.config.meta_learning_rate * 0.99)
    
    def _evaluate_model(self, model: Any, X: np.ndarray, y: np.ndarray) -> float:
        """Model performance evaluation"""
        try:
            predictions = model.predict(X)
            if len(np.unique(y)) > 2:
                return mean_squared_error(y, predictions)
            else:
                return 1 - accuracy_score(y, predictions)
        except:
            return 1.0
    
    def _get_model_params(self, model: Any) -> Dict[str, Any]:
        """Get model parameters"""
        if hasattr(model, 'get_params'):
            return model.get_params()
        elif hasattr(model, 'coef_') and hasattr(model, 'intercept_'):
            return {
                'coef_': getattr(model, 'coef_', None),
                'intercept_': getattr(model, 'intercept_', None)
            }
        else:
            return {}
    
    def _create_model_with_params(self, original_model: Any, params: Dict[str, Any]) -> Any:
        """Create model with updated parameters"""
        try:
            # Try to create new instance with updated params
            model_class = type(original_model)
            return model_class(**params)
        except:
            # Fallback: return original model
            return original_model
    
    def _find_similar_tasks(self, target_task: Task) -> List[Task]:
        """Find similar previous tasks"""
        similar_tasks = []
        
        for task in self.task_memory:
            similarity = self._calculate_task_similarity(target_task, task)
            if similarity > self.config.task_similarity_threshold:
                similar_tasks.append(task)
        
        return similar_tasks
    
    def _calculate_task_similarity(self, task1: Task, task2: Task) -> float:
        """Calculate similarity between two tasks"""
        # Simple similarity based on domain and metadata
        domain_similarity = 1.0 if task1.domain == task2.domain else 0.0
        
        # Feature similarity (if available)
        X1, _ = task1.support_set
        X2, _ = task2.support_set
        
        if X1.shape == X2.shape:
            feature_similarity = 1.0 - np.mean(np.abs(X1.mean(axis=0) - X2.mean(axis=0)))
            feature_similarity = max(0, min(1, feature_similarity))
        else:
            feature_similarity = 0.0
        
        # Weighted combination
        total_similarity = 0.7 * domain_similarity + 0.3 * feature_similarity
        
        # Store similarity for analysis
        similarity_key = f"{task1.task_id}_{task2.task_id}"
        self.task_similarities[similarity_key] = total_similarity
        
        return total_similarity
    
    def _get_best_params_for_task(self, task: Task) -> Dict[str, Any]:
        """Get best parameters for specific task"""
        # Use parameters from successful similar task
        return self._get_default_params()  # Simplified
    
    def _get_default_params(self) -> Dict[str, Any]:
        """Get default parameters"""
        if self.base_models:
            first_model = list(self.base_models.values())[0]
            return first_model['default_params']
        return {}
    
    def _evaluate_meta_learning(self, tasks: List[Task]) -> float:
        """Evaluate meta-learning performance"""
        total_performance = 0.0
        
        for task in tasks[:min(len(tasks), 10)]:  # Evaluate on subset
            # Adapt model to task
            adapted_model, _ = self._inner_loop_adaptation(task)
            
            # Evaluate on query set
            X_query, y_query = task.query_set
            predictions = adapted_model.predict(X_query)
            
            try:
                if len(np.unique(y_query)) > 2:
                    performance = 1 / (1 + mean_squared_error(y_query, predictions))  # Higher is better
                else:
                    performance = accuracy_score(y_query, predictions)
                total_performance += performance
            except:
                total_performance += 0.0
        
        return total_performance / min(len(tasks), 10)

class FewShotLearner:
    """Few-shot learning for trading scenarios"""
    
    def __init__(self, config: MetaLearningConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.FewShotLearner")
        
        # Support set memory
        self.support_sets = {}
        self.prototype_models = {}
        
        # Task-specific models
        self.task_models = {}
        
        # Performance tracking
        self.few_shot_performance = {}
    
    def learn_from_examples(self, task_id: str, support_set: Tuple[np.ndarray, np.ndarray],
                          query_features: np.ndarray) -> np.ndarray:
        """Learn from few examples"""
        X_support, y_support = support_set
        
        # Store support set
        self.support_sets[task_id] = (X_support, y_support)
        
        # Create prototype model
        prototype_model = self._create_prototype_model(X_support, y_support)
        self.prototype_models[task_id] = prototype_model
        
        # Predict on query
        predictions = prototype_model.predict(query_features.reshape(1, -1))
        
        return predictions
    
    def _create_prototype_model(self, X_support: np.ndarray, y_support: np.ndarray) -> Any:
        """Create prototype-based model"""
        # Simple nearest neighbor prototype
        class PrototypeClassifier:
            def __init__(self, X, y):
                self.X = X
                self.y = y
                self.classes = np.unique(y)
            
            def predict(self, X):
                distances = np.linalg.norm(X[:, np.newaxis] - self.X[np.newaxis, :], axis=2)
                nearest_indices = np.argmin(distances, axis=1)
                return self.y[nearest_indices]
        
        return PrototypeClassifier(X_support, y_support)
    
    def update_with_new_examples(self, task_id: str, new_X: np.ndarray, new_y: np.ndarray) -> None:
        """Update model with new examples"""
        if task_id in self.support_sets:
            X_old, y_old = self.support_sets[task_id]
            X_combined = np.vstack([X_old, new_X])
            y_combined = np.hstack([y_old, new_y])
            self.support_sets[task_id] = (X_combined, y_combined)
            
            # Update prototype
            self.prototype_models[task_id] = self._create_prototype_model(X_combined, y_combined)
        else:
            self.support_sets[task_id] = (new_X, new_y)
            self.prototype_models[task_id] = self._create_prototype_model(new_X, new_y)

class HyperparameterMetaLearner:
    """Meta-learning for hyperparameter optimization"""
    
    def __init__(self, config: MetaLearningConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.HyperparameterMetaLearner")
        
        # Hyperparameter recommendations
        self.hyperparameter_history = {}
        self.best_configurations = {}
        
        # Meta-features for tasks
        self.task_features = {}
        
        # Performance prediction
        self.performance_predictor = None
    
    def predict_best_hyperparameters(self, task_features: Dict[str, Any], 
                                   model_type: str) -> Dict[str, Any]:
        """Predict best hyperparameters for task"""
        
        # Extract task features
        features_vector = self._extract_task_features(task_features)
        
        # Find similar tasks
        similar_configs = self._find_similar_configurations(features_vector, model_type)
        
        if similar_configs:
            # Use best configuration from similar tasks
            best_config = self._select_best_configuration(similar_configs)
        else:
            # Use default or generate new configuration
            best_config = self._generate_configuration(model_type)
        
        return best_config
    
    def _extract_task_features(self, task_metadata: Dict[str, Any]) -> np.ndarray:
        """Extract features from task metadata"""
        features = []
        
        # Sample size
        features.append(task_metadata.get('sample_size', 1000))
        
        # Feature dimensions
        features.append(task_metadata.get('n_features', 10))
        
        # Target diversity
        features.append(task_metadata.get('target_unique_values', 2))
        
        # Data complexity indicators
        features.append(task_metadata.get('noise_level', 0.1))
        features.append(task_metadata.get('missing_percentage', 0.0))
        
        # Market-specific features
        features.append(task_metadata.get('volatility', 0.02))
        features.append(task_metadata.get('trend_strength', 0.5))
        
        return np.array(features)
    
    def _find_similar_configurations(self, features: np.ndarray, model_type: str) -> List[Dict[str, Any]]:
        """Find similar configurations for current task"""
        similar_configs = []
        
        for task_id, config_data in self.hyperparameter_history.items():
            if config_data['model_type'] == model_type:
                task_features = config_data['task_features']
                similarity = self._calculate_feature_similarity(features, task_features)
                
                if similarity > 0.7:
                    similar_configs.append({
                        'configuration': config_data['configuration'],
                        'performance': config_data['performance'],
                        'similarity': similarity
                    })
        
        return sorted(similar_configs, key=lambda x: x['similarity'], reverse=True)
    
    def _calculate_feature_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Calculate similarity between feature vectors"""
        try:
            # Cosine similarity
            dot_product = np.dot(features1, features2)
            norm1 = np.linalg.norm(features1)
            norm2 = np.linalg.norm(features2)
            
            if norm1 > 0 and norm2 > 0:
                similarity = dot_product / (norm1 * norm2)
                return max(0, min(1, similarity))
            return 0.0
        except:
            return 0.0
    
    def _select_best_configuration(self, similar_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select best configuration from similar tasks"""
        if not similar_configs:
            return {}
        
        # Weight configurations by similarity and performance
        weighted_score = 0.0
        total_weight = 0.0
        
        for config in similar_configs[:5]:  # Top 5 similar configurations
            weight = config['similarity'] * (config['performance'] + 1)  # Performance weighting
            weighted_score += weight * config['configuration']
            total_weight += weight
        
        if total_weight > 0:
            best_config = weighted_score / total_weight
        else:
            best_config = similar_configs[0]['configuration']
        
        return best_config
    
    def _generate_configuration(self, model_type: str) -> Dict[str, Any]:
        """Generate new configuration based on model type"""
        configurations = {
            'random_forest': {
                'n_estimators': 100,
                'max_depth': 10,
                'min_samples_split': 2,
                'min_samples_leaf': 1
            },
            'svm': {
                'C': 1.0,
                'kernel': 'rbf',
                'gamma': 'scale'
            },
            'neural_network': {
                'hidden_layer_sizes': (100, 50),
                'activation': 'relu',
                'solver': 'adam',
                'alpha': 0.0001
            }
        }
        
        return configurations.get(model_type, {})
    
    def record_configuration_performance(self, task_id: str, configuration: Dict[str, Any],
                                       performance: float, task_features: Dict[str, Any],
                                       model_type: str) -> None:
        """Record configuration performance"""
        features_vector = self._extract_task_features(task_features)
        
        self.hyperparameter_history[task_id] = {
            'configuration': configuration,
            'performance': performance,
            'task_features': features_vector,
            'model_type': model_type,
            'timestamp': datetime.now()
        }

class AdaptiveMetaLearningSystem:
    """Complete adaptive meta-learning system"""
    
    def __init__(self, config: MetaLearningConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.AdaptiveMetaLearning")
        
        # Meta-learning components
        self.maml = ModelAgnosticMetaLearner(config)
        self.few_shot_learner = FewShotLearner(config)
        self.hyperparameter_learner = HyperparameterMetaLearner(config)
        
        # System state
        self.is_trained = False
        self.current_tasks = {}
        self.performance_history = []
        
    def setup_base_models(self) -> None:
        """Setup base models for meta-learning"""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.svm import SVC
        from sklearn.neural_network import MLPClassifier
        
        self.maml.register_base_model('random_forest', RandomForestClassifier)
        self.maml.register_base_model('svm', SVC)
        self.maml.register_base_model('neural_network', MLPClassifier)
    
    def learn_from_trading_tasks(self, trading_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Learn from trading-related tasks"""
        
        # Convert trading tasks to meta-learning format
        meta_tasks = []
        for i, task_data in enumerate(trading_tasks):
            task = Task(
                task_id=f"trading_task_{i}",
                support_set=(task_data['support_features'], task_data['support_labels']),
                query_set=(task_data['query_features'], task_data['query_labels']),
                task_metadata=task_data.get('metadata', {}),
                domain=task_data.get('market_type', 'unknown')
            )
            meta_tasks.append(task)
        
        # Meta-training
        training_history = self.maml.meta_train(meta_tasks)
        
        # Few-shot learning setup
        for task in meta_tasks:
            self.few_shot_learner.learn_from_examples(
                task.task_id,
                task.support_set,
                task.query_set[0]  # Use first query sample
            )
        
        # Hyperparameter meta-learning
        for task in meta_tasks:
            task_features = task.task_metadata
            model_type = 'random_forest'  # Default
            
            best_config = self.hyperparameter_learner.predict_best_hyperparameters(
                task_features, model_type
            )
            
            self.hyperparameter_learner.record_configuration_performance(
                task.task_id,
                best_config,
                np.random.random(),  # Placeholder performance
                task_features,
                model_type
            )
        
        self.is_trained = True
        
        return {
            'meta_learning_results': training_history,
            'few_shot_performance': self.few_shot_learner.few_shot_performance,
            'hyperparameter_recommendations': self.hyperparameter_learner.best_configurations
        }
    
    def adapt_to_new_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt to new market conditions"""
        if not self.is_trained:
            return {'error': 'System must be trained first'}
        
        # Extract market features
        market_features = self._extract_market_features(market_data)
        
        # Predict best configuration for this market
        recommended_config = self.hyperparameter_learner.predict_best_hyperparameters(
            market_features, 'random_forest'
        )
        
        # Create adapted model
        adapted_model_info = {
            'recommended_configuration': recommended_config,
            'market_features': market_features,
            'adaptation_confidence': self._calculate_adaptation_confidence(market_features)
        }
        
        return adapted_model_info
    
    def _extract_market_features(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from market data"""
        return {
            'sample_size': len(market_data.get('prices', [])),
            'n_features': len(market_data.get('features', [])),
            'target_unique_values': 2,  # Binary trading decision
            'noise_level': market_data.get('noise_level', 0.1),
            'missing_percentage': market_data.get('missing_percentage', 0.0),
            'volatility': np.std(market_data.get('returns', [])),
            'trend_strength': market_data.get('trend_strength', 0.5)
        }
    
    def _calculate_adaptation_confidence(self, market_features: Dict[str, Any]) -> float:
        """Calculate confidence in adaptation"""
        # Simple confidence based on feature completeness and similarity
        completeness = 1.0 - (market_features.get('missing_percentage', 0.0))
        similarity_score = 0.8  # Placeholder
        
        return min(1.0, completeness * similarity_score)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and performance"""
        return {
            'is_trained': self.is_trained,
            'registered_models': len(self.maml.base_models),
            'task_memory_size': len(self.maml.task_memory),
            'meta_loss_trend': self.maml.meta_losses[-10:] if self.maml.meta_losses else [],
            'few_shot_tasks': len(self.few_shot_learner.support_sets),
            'hyperparameter_configs': len(self.hyperparameter_learner.hyperparameter_history)
        }