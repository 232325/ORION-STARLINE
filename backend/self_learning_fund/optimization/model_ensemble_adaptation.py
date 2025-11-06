"""
Model Ensemble Adaptation for Self-Learning Trading Fund
=======================================================

Ensemble modelini dinamik moslashish va optimallashtirish.
Bir nechta modelni birlashtirib, ulardan eng yaxshi performance olish.
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
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from ..core.base_algorithm import BaseAlgorithm
from ..core.adaptive_model import AdaptiveModel
from ..core.performance_tracker import PerformanceTracker

class EnsembleMethod(Enum):
    """Ensemble usullari"""
    VOTING = "Voting"
    AVERAGING = "Averaging"
    WEIGHTED_AVERAGING = "Weighted_Averaging"
    STACKING = "Stacking"
    BOOSTING = "Boosting"
    BAGGING = "Bagging"
    BLENDING = "Blending"
    DYNAMIC_WEIGHTING = "Dynamic_Weighting"

class ModelType(Enum):
    """Model turlari"""
    NEURAL_NETWORK = "Neural_Network"
    RANDOM_FOREST = "Random_Forest"
    XGBOOST = "XGBoost"
    SVM = "SVM"
    LINEAR_REGRESSION = "Linear_Regression"
    DECISION_TREE = "Decision_Tree"
    KNN = "KNN"
    LSTM = "LSTM"
    CNN = "CNN"
    PROPHET = "Prophet"

class AdaptationStrategy(Enum):
    """Moslashish strategiyasi"""
    PERFORMANCE_BASED = "Performance_Based"
    DIVERSITY_BASED = "Diversity_Based"
    RECENCY_BASED = "Recency_Based"
    VOLATILITY_BASED = "Volatility_Based"
    CONFIDENCE_BASED = "Confidence_Based"
    HYBRID = "Hybrid"

@dataclass
class ModelInfo:
    """Model ma'lumotlari"""
    model_id: str
    model_type: ModelType
    model: Any
    performance_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    confidence_score: float = 0.0
    prediction_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EnsembleState:
    """Ensemble holati"""
    models: Dict[str, ModelInfo]
    current_weights: Dict[str, float]
    adaptation_history: List[Dict[str, Any]]
    performance_history: List[float]
    diversity_scores: Dict[str, float]
    last_adaptation: datetime
    convergence_state: str = "active"

class DynamicEnsembleAdapter(BaseAlgorithm):
    """Dinamik ensemble moslashtiruvchi"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        self.config = config or {}
        self.ensemble_state = EnsembleState(
            models={},
            current_weights={},
            adaptation_history=[],
            performance_history=[],
            diversity_scores={},
            last_adaptation=datetime.now()
        )
        
        # Configuration
        self.adaptation_frequency = self.config.get('adaptation_frequency', 50)  # predictions
        self.performance_window = self.config.get('performance_window', 100)
        self.diversity_threshold = self.config.get('diversity_threshold', 0.3)
        self.weight_update_rate = self.config.get('weight_update_rate', 0.1)
        self.max_models = self.config.get('max_models', 10)
        self.min_models = self.config.get('min_models', 3)
        
        # Performance tracking
        self.performance_tracker = PerformanceTracker()
        
    def add_model(self, model: Any, model_type: ModelType, 
                initial_weight: float = 1.0,
                model_id: Optional[str] = None) -> str:
        """Model qo'shish"""
        
        if model_id is None:
            model_id = f"{model_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        model_info = ModelInfo(
            model_id=model_id,
            model_type=model_type,
            model=model,
            performance_score=initial_weight,
            confidence_score=1.0
        )
        
        self.ensemble_state.models[model_id] = model_info
        self.ensemble_state.current_weights[model_id] = initial_weight
        
        logging.info(f"Added model {model_id} with initial weight {initial_weight}")
        
        return model_id
    
    def predict(self, X: Any, prediction_type: str = 'classification') -> Tuple[Any, Dict[str, float]]:
        """Ensemble prediction"""
        
        if not self.ensemble_state.models:
            raise ValueError("No models in ensemble")
        
        predictions = {}
        model_confidences = {}
        
        # Get predictions from all models
        for model_id, model_info in self.ensemble_state.models.items():
            try:
                pred = self._get_model_prediction(model_info.model, X, prediction_type)
                predictions[model_id] = pred
                model_confidences[model_id] = model_info.confidence_score
            except Exception as e:
                logging.error(f"Error getting prediction from model {model_id}: {str(e)}")
                continue
        
        if not predictions:
            raise ValueError("No valid predictions available")
        
        # Combine predictions based on ensemble method
        ensemble_prediction, individual_predictions = self._combine_predictions(
            predictions, model_confidences, prediction_type
        )
        
        # Track prediction for adaptation
        self._track_prediction(individual_predictions, model_confidences)
        
        return ensemble_prediction, individual_predictions
    
    def _get_model_prediction(self, model: Any, X: Any, prediction_type: str) -> np.ndarray:
        """Model prediction olish"""
        
        # Simplified prediction logic
        # In real implementation, would call model.predict()
        
        if hasattr(model, 'predict'):
            return model.predict(X)
        elif isinstance(model, dict) and 'predictions' in model:
            return np.array(model['predictions'])
        else:
            # Generate synthetic prediction for demo
            n_samples = len(X) if hasattr(X, '__len__') else 1
            if prediction_type == 'classification':
                return np.random.randint(0, 2, n_samples)
            else:
                return np.random.randn(n_samples)
    
    def _combine_predictions(self, predictions: Dict[str, np.ndarray],
                           confidences: Dict[str, float],
                           prediction_type: str) -> Tuple[Any, Dict[str, float]]:
        """Prediction larni birlashtirish"""
        
        # Get current weights
        weights = self.ensemble_state.current_weights
        
        # Combine based on weighted averaging
        combined_prediction = None
        individual_results = {}
        
        for model_id, pred in predictions.items():
            weight = weights.get(model_id, 1.0) * confidences.get(model_id, 1.0)
            
            individual_results[model_id] = {
                'prediction': pred,
                'weight': weight,
                'confidence': confidences.get(model_id, 1.0)
            }
            
            if combined_prediction is None:
                combined_prediction = pred * weight
            else:
                combined_prediction += pred * weight
        
        # Normalize by total weight
        total_weight = sum(w['weight'] for w in individual_results.values())
        if total_weight > 0:
            combined_prediction = combined_prediction / total_weight
        
        # Apply ensemble method
        if prediction_type == 'classification':
            combined_prediction = np.round(combined_prediction).astype(int)
        
        return combined_prediction, individual_results
    
    def adapt_ensemble(self, performance_feedback: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Ensemble ni moslashish"""
        
        adaptation_result = {
            'adaptation_timestamp': datetime.now(),
            'adaptations_performed': [],
            'new_weights': {},
            'models_added': [],
            'models_removed': [],
            'performance_impact': 0.0
        }
        
        # Update model performances
        if performance_feedback:
            self._update_performance_scores(performance_feedback)
        
        # Calculate diversity scores
        self._calculate_diversity_scores()
        
        # Update weights based on performance
        weight_updates = self._update_model_weights()
        adaptation_result['new_weights'] = weight_updates
        
        # Perform adaptation based on strategy
        if self.config.get('adaptation_strategy') == AdaptationStrategy.PERFORMANCE_BASED:
            adaptations = self._performance_based_adaptation()
        elif self.config.get('adaptation_strategy') == AdaptationStrategy.DIVERSITY_BASED:
            adaptations = self._diversity_based_adaptation()
        elif self.config.get('adaptation_strategy') == AdaptationStrategy.HYBRID:
            adaptations = self._hybrid_adaptation()
        else:
            adaptations = self._default_adaptation()
        
        adaptation_result['adaptations_performed'] = adaptations
        adaptation_result['models_added'] = adaptations.get('added', [])
        adaptation_result['models_removed'] = adaptations.get('removed', [])
        
        # Update ensemble state
        self.ensemble_state.last_adaptation = datetime.now()
        self.ensemble_state.adaptation_history.append(adaptation_result)
        
        # Calculate performance impact
        if self.ensemble_state.performance_history:
            recent_performance = np.mean(self.ensemble_state.performance_history[-10:])
            previous_performance = np.mean(self.ensemble_state.performance_history[-20:-10]) if len(self.ensemble_state.performance_history) >= 20 else recent_performance
            adaptation_result['performance_impact'] = recent_performance - previous_performance
        
        logging.info(f"Ensemble adaptation completed: {len(adaptations)} changes made")
        
        return adaptation_result
    
    def _update_performance_scores(self, performance_feedback: Dict[str, float]):
        """Performance ballarni yangilash"""
        
        for model_id, score in performance_feedback.items():
            if model_id in self.ensemble_state.models:
                model_info = self.ensemble_state.models[model_id]
                
                # Update with exponential moving average
                alpha = 0.3
                model_info.performance_score = alpha * score + (1 - alpha) * model_info.performance_score
                model_info.last_updated = datetime.now()
    
    def _calculate_diversity_scores(self):
        """Diversity ballarni hisoblash"""
        
        if len(self.ensemble_state.models) < 2:
            return
        
        model_ids = list(self.ensemble_state.models.keys())
        
        for i, model_id1 in enumerate(model_ids):
            for model_id2 in model_ids[i+1:]:
                # Calculate prediction diversity
                diversity_score = self._calculate_pairwise_diversity(model_id1, model_id2)
                pair_key = f"{model_id1}_{model_id2}"
                self.ensemble_state.diversity_scores[pair_key] = diversity_score
    
    def _calculate_pairwise_diversity(self, model_id1: str, model_id2: str) -> float:
        """Juft model o'rtasidagi diversity"""
        
        # Simplified diversity calculation
        # In real implementation, would compare actual predictions
        
        model1 = self.ensemble_state.models[model_id1]
        model2 = self.ensemble_state.models[model_id2]
        
        # Diversity based on model types and performance differences
        type_diversity = 0.5 if model1.model_type != model2.model_type else 0.2
        perf_diversity = abs(model1.performance_score - model2.performance_score)
        
        diversity = type_diversity * 0.6 + perf_diversity * 0.4
        return min(1.0, diversity)
    
    def _update_model_weights(self) -> Dict[str, float]:
        """Model vaznlarini yangilash"""
        
        new_weights = {}
        total_weight = 0
        
        for model_id, model_info in self.ensemble_state.models.items():
            # Performance-based weight
            perf_weight = model_info.performance_score
            
            # Recency-based weight (newer models get slight boost)
            days_since_update = (datetime.now() - model_info.last_updated).days
            recency_weight = 1.0 / (1 + days_since_update * 0.1)
            
            # Confidence-based weight
            confidence_weight = model_info.confidence_score
            
            # Combined weight
            combined_weight = perf_weight * recency_weight * confidence_weight
            new_weights[model_id] = combined_weight
            total_weight += combined_weight
        
        # Normalize weights
        if total_weight > 0:
            new_weights = {k: v/total_weight for k, v in new_weights.items()}
        
        # Update ensemble state
        self.ensemble_state.current_weights = new_weights
        
        return new_weights
    
    def _performance_based_adaptation(self) -> Dict[str, List[str]]:
        """Performance asosida moslashish"""
        
        adaptations = {'added': [], 'removed': []}
        
        # Remove poor performing models
        poor_models = [
            model_id for model_id, model_info in self.ensemble_state.models.items()
            if model_info.performance_score < 0.3 and model_info.prediction_count > 20
        ]
        
        for model_id in poor_models[:2]:  # Remove up to 2 models
            del self.ensemble_state.models[model_id]
            del self.ensemble_state.current_weights[model_id]
            adaptations['removed'].append(model_id)
        
        # Ensure minimum number of models
        if len(self.ensemble_state.models) < self.min_models:
            logging.warning(f"Only {len(self.ensemble_state.models)} models remaining")
        
        return adaptations
    
    def _diversity_based_adaptation(self) -> Dict[str, List[str]]:
        """Diversity asosida moslashish"""
        
        adaptations = {'added': [], 'removed': []}
        
        # Check for similar models
        similar_pairs = [
            (pair, score) for pair, score in self.ensemble_state.diversity_scores.items()
            if score < self.diversity_threshold
        ]
        
        # Remove one from each similar pair (keep the better performer)
        for pair, diversity_score in similar_pairs:
            model_id1, model_id2 = pair.split('_')
            
            if model_id1 in self.ensemble_state.models and model_id2 in self.ensemble_state.models:
                model1 = self.ensemble_state.models[model_id1]
                model2 = self.ensemble_state.models[model_id2]
                
                # Keep the better performing model
                if model1.performance_score >= model2.performance_score:
                    removed_model = model_id2
                else:
                    removed_model = model_id1
                
                del self.ensemble_state.models[removed_model]
                del self.ensemble_state.current_weights[removed_model]
                adaptations['removed'].append(removed_model)
        
        return adaptations
    
    def _hybrid_adaptation(self) -> Dict[str, List[str]]:
        """Gibrid moslashish"""
        
        # Combine performance and diversity based adaptations
        perf_adaptations = self._performance_based_adaptation()
        div_adaptations = self._diversity_based_adaptation()
        
        adaptations = {
            'added': list(set(perf_adaptations.get('added', []) + div_adaptations.get('added', []))),
            'removed': list(set(perf_adaptations.get('removed', []) + div_adaptations.get('removed', [])))
        }
        
        # Additional hybrid logic
        if len(self.ensemble_state.models) > self.max_models:
            # Sort models by performance
            sorted_models = sorted(
                self.ensemble_state.models.items(),
                key=lambda x: x[1].performance_score,
                reverse=True
            )
            
            # Keep only top models
            models_to_remove = sorted_models[self.max_models:]
            for model_id, model_info in models_to_remove:
                if model_id not in adaptations['removed']:
                    del self.ensemble_state.models[model_id]
                    del self.ensemble_state.current_weights[model_id]
                    adaptations['removed'].append(model_id)
        
        return adaptations
    
    def _default_adaptation(self) -> Dict[str, List[str]]:
        """Default moslashish"""
        
        # Simple weight normalization
        self._update_model_weights()
        
        return {'added': [], 'removed': []}
    
    def _track_prediction(self, predictions: Dict[str, Any], confidences: Dict[str, float]):
        """Prediction larni kuzatish"""
        
        # Update prediction counts
        for model_id in predictions.keys():
            if model_id in self.ensemble_state.models:
                self.ensemble_state.models[model_id].prediction_count += 1
        
        # Calculate ensemble performance
        # Simplified performance calculation
        individual_scores = [confidences.get(mid, 0.5) for mid in predictions.keys()]
        ensemble_performance = np.mean(individual_scores)
        
        self.ensemble_state.performance_history.append(ensemble_performance)
        
        # Keep history bounded
        if len(self.ensemble_state.performance_history) > self.performance_window:
            self.ensemble_state.performance_history = self.ensemble_state.performance_history[-self.performance_window:]
    
    def get_ensemble_summary(self) -> Dict[str, Any]:
        """Ensemble holatini olish"""
        
        if not self.ensemble_state.models:
            return {"error": "No models in ensemble"}
        
        model_summaries = {}
        for model_id, model_info in self.ensemble_state.models.items():
            model_summaries[model_id] = {
                'model_type': model_info.model_type.value,
                'performance_score': model_info.performance_score,
                'confidence_score': model_info.confidence_score,
                'current_weight': self.ensemble_state.current_weights.get(model_id, 0.0),
                'prediction_count': model_info.prediction_count,
                'last_updated': model_info.last_updated.isoformat()
            }
        
        return {
            'total_models': len(self.ensemble_state.models),
            'model_summaries': model_summaries,
            'ensemble_weights': self.ensemble_state.current_weights,
            'recent_performance': np.mean(self.ensemble_state.performance_history[-10:]) if self.ensemble_state.performance_history else 0.0,
            'performance_trend': self._calculate_performance_trend(),
            'diversity_score': np.mean(list(self.ensemble_state.diversity_scores.values())) if self.ensemble_state.diversity_scores else 0.0,
            'adaptation_count': len(self.ensemble_state.adaptation_history),
            'last_adaptation': self.ensemble_state.last_adaptation.isoformat()
        }
    
    def _calculate_performance_trend(self) -> str:
        """Performance trend ni hisoblash"""
        
        if len(self.ensemble_state.performance_history) < 10:
            return "insufficient_data"
        
        recent_scores = self.ensemble_state.performance_history[-10:]
        trend_slope = np.polyfit(range(len(recent_scores)), recent_scores, 1)[0]
        
        if trend_slope > 0.01:
            return "improving"
        elif trend_slope < -0.01:
            return "declining"
        else:
            return "stable"

class AdaptiveEnsembleManager:
    """Moslashuvchan ensemble boshqaruvchi"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.ensemble_adapter = DynamicEnsembleAdapter(config)
        self.adaptation_scheduler = EnsembleAdaptationScheduler()
        
        # Model generation strategies
        self.model_strategies = {
            ModelType.NEURAL_NETWORK: self._generate_neural_network,
            ModelType.RANDOM_FOREST: self._generate_random_forest,
            ModelType.XGBOOST: self._generate_xgboost,
            ModelType.LINEAR_REGRESSION: self._generate_linear_model
        }
    
    def create_diverse_ensemble(self, base_data: Any, 
                              target_model_count: int = 5) -> List[str]:
        """Turli xil modellardan ensemble yaratish"""
        
        added_models = []
        model_types = list(self.model_strategies.keys())
        
        for i in range(min(target_model_count, len(model_types))):
            model_type = model_types[i % len(model_types)]
            
            # Generate model with different hyperparameters
            model = self._generate_model_with_variations(model_type, i)
            
            # Add to ensemble
            model_id = self.ensemble_adapter.add_model(
                model, model_type, initial_weight=1.0/target_model_count
            )
            added_models.append(model_id)
        
        logging.info(f"Created ensemble with {len(added_models)} diverse models")
        
        return added_models
    
    def _generate_model_with_variations(self, model_type: ModelType, variation_id: int) -> Any:
        """Turli xil konfiguratsiyali model generatsiya"""
        
        strategy = self.model_strategies.get(model_type)
        if strategy:
            return strategy(variation_id)
        else:
            return {"type": "placeholder", "variation": variation_id}
    
    def _generate_neural_network(self, variation_id: int) -> Dict[str, Any]:
        """Neural network generatsiya"""
        
        architectures = [
            {"layers": [50], "activation": "relu"},
            {"layers": [100], "activation": "tanh"},
            {"layers": [50, 25], "activation": "relu"},
            {"layers": [100, 50], "activation": "tanh"}
        ]
        
        arch = architectures[variation_id % len(architectures)]
        
        return {
            "type": "neural_network",
            "architecture": arch,
            "learning_rate": 0.001 * (1.5 ** variation_id),
            "variation_id": variation_id
        }
    
    def _generate_random_forest(self, variation_id: int) -> Dict[str, Any]:
        """Random Forest generatsiya"""
        
        n_estimators_options = [50, 100, 150, 200]
        max_depth_options = [5, 10, 15, None]
        
        return {
            "type": "random_forest",
            "n_estimators": n_estimators_options[variation_id % len(n_estimators_options)],
            "max_depth": max_depth_options[variation_id % len(max_depth_options)],
            "variation_id": variation_id
        }
    
    def _generate_xgboost(self, variation_id: int) -> Dict[str, Any]:
        """XGBoost generatsiya"""
        
        max_depth_options = [3, 4, 5, 6]
        learning_rate_options = [0.1, 0.2, 0.3, 0.01]
        
        return {
            "type": "xgboost",
            "max_depth": max_depth_options[variation_id % len(max_depth_options)],
            "learning_rate": learning_rate_options[variation_id % len(learning_rate_options)],
            "variation_id": variation_id
        }
    
    def _generate_linear_model(self, variation_id: int) -> Dict[str, Any]:
        """Linear model generatsiya"""
        
        regularization_options = [0.001, 0.01, 0.1, 1.0]
        
        return {
            "type": "linear_model",
            "regularization": regularization_options[variation_id % len(regularization_options)],
            "variation_id": variation_id
        }
    
    def auto_adapt_ensemble(self, performance_data: Dict[str, float],
                          adaptation_trigger: str = 'performance') -> Dict[str, Any]:
        """Avtomatik ensemble moslashish"""
        
        # Check if adaptation is needed
        should_adapt = self.adaptation_scheduler.should_adapt(
            self.ensemble_adapter, performance_data, adaptation_trigger
        )
        
        if should_adapt:
            return self.ensemble_adapter.adapt_ensemble(performance_data)
        else:
            return {"adaptation_performed": False, "reason": "adaptation_not_needed"}

class EnsembleAdaptationScheduler:
    """Ensemble moslashish rejalashtiruvchi"""
    
    def __init__(self):
        self.adaptation_history = deque(maxlen=50)
        self.performance_threshold = 0.05
        self.time_threshold = 3600  # 1 hour
        self.performance_count_threshold = 10
    
    def should_adapt(self, ensemble_adapter: DynamicEnsembleAdapter,
                   performance_data: Dict[str, float],
                   trigger_type: str) -> bool:
        """Moslashish kerakligini aniqlash"""
        
        current_time = datetime.now()
        
        # Time-based trigger
        if trigger_type == 'time':
            if not ensemble_adapter.ensemble_state.adaptation_history:
                return True
            
            last_adaptation = ensemble_adapter.ensemble_state.last_adaptation
            time_since_last = (current_time - last_adaptation).total_seconds()
            
            if time_since_last > self.time_threshold:
                return True
        
        # Performance-based trigger
        elif trigger_type == 'performance':
            recent_performance = np.mean(list(performance_data.values()))
            if ensemble_adapter.ensemble_state.performance_history:
                baseline_performance = np.mean(ensemble_adapter.ensemble_state.performance_history[-10:])
                if recent_performance < baseline_performance * (1 - self.performance_threshold):
                    return True
        
        # Count-based trigger
        elif trigger_type == 'prediction_count':
            for model_info in ensemble_adapter.ensemble_state.models.values():
                if model_info.prediction_count % ensemble_adapter.adaptation_frequency == 0:
                    return True
        
        return False

class EnsemblePerformanceEvaluator:
    """Ensemble performance baholovchi"""
    
    def __init__(self):
        self.evaluation_history = deque(maxlen=100)
        
    def evaluate_ensemble_performance(self, ensemble_adapter: DynamicEnsembleAdapter,
                                    test_data: Any, ground_truth: Any) -> Dict[str, float]:
        """Ensemble performance ni baholash"""
        
        # Get ensemble predictions
        predictions, individual_predictions = ensemble_adapter.predict(test_data)
        
        # Calculate various performance metrics
        metrics = {}
        
        # Accuracy (for classification)
        if isinstance(ground_truth, np.ndarray) and len(ground_truth.shape) == 1:
            accuracy = np.mean(predictions == ground_truth)
            metrics['accuracy'] = accuracy
            
            # Individual model accuracies
            individual_accuracies = {}
            for model_id, pred_info in individual_predictions.items():
                if 'prediction' in pred_info:
                    individual_acc = np.mean(pred_info['prediction'] == ground_truth)
                    individual_accuracies[model_id] = individual_acc
            
            metrics['individual_accuracies'] = individual_accuracies
        
        # Diversity metrics
        diversity_score = self._calculate_ensemble_diversity(individual_predictions)
        metrics['diversity_score'] = diversity_score
        
        # Confidence metrics
        confidence_scores = [pred_info.get('confidence', 0.5) for pred_info in individual_predictions.values()]
        metrics['average_confidence'] = np.mean(confidence_scores)
        metrics['confidence_std'] = np.std(confidence_scores)
        
        # Store evaluation
        evaluation_result = {
            'timestamp': datetime.now(),
            'metrics': metrics,
            'ensemble_prediction': predictions,
            'individual_predictions': individual_predictions
        }
        
        self.evaluation_history.append(evaluation_result)
        
        return metrics
    
    def _calculate_ensemble_diversity(self, predictions: Dict[str, Any]) -> float:
        """Ensemble diversity hisoblash"""
        
        if len(predictions) < 2:
            return 0.0
        
        # Calculate pairwise disagreement
        disagreement_scores = []
        pred_arrays = []
        
        for pred_info in predictions.values():
            if 'prediction' in pred_info:
                pred_arrays.append(pred_info['prediction'])
        
        for i in range(len(pred_arrays)):
            for j in range(i + 1, len(pred_arrays)):
                # Calculate disagreement ratio
                disagreement = np.mean(pred_arrays[i] != pred_arrays[j])
                disagreement_scores.append(disagreement)
        
        return np.mean(disagreement_scores) if disagreement_scores else 0.0

# Trading-specific ensemble adapter
class TradingEnsembleAdapter(DynamicEnsembleAdapter):
    """Trading uchun maxsus ensemble adapter"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        # Trading-specific configurations
        self.market_regime_adaptation = config.get('market_regime_adaptation', True)
        self.volatility_adjustment = config.get('volatility_adjustment', True)
        self.correlation_threshold = config.get('correlation_threshold', 0.8)
        
        # Market regime tracking
        self.current_market_regime = "normal"
        self.regime_performance_history = defaultdict(list)
    
    def adapt_for_market_regime(self, market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Bozor rejimi uchun moslashish"""
        
        adaptation_result = {
            'regime': market_conditions.get('regime', 'unknown'),
            'adaptations': [],
            'weight_adjustments': {}
        }
        
        new_regime = market_conditions.get('regime', 'normal')
        
        if new_regime != self.current_market_regime:
            self.current_market_regime = new_regime
            
            # Regime-specific adaptations
            if new_regime == 'high_volatility':
                adaptation_result['adaptations'] = self._adapt_for_high_volatility()
            elif new_regime == 'trending':
                adaptation_result['adaptations'] = self._adapt_for_trending_market()
            elif new_regime == 'ranging':
                adaptation_result['adaptations'] = self._adapt_for_ranging_market()
        
        return adaptation_result
    
    def _adapt_for_high_volatility(self) -> List[str]:
        """Yuqori volatillik uchun moslashish"""
        
        adaptations = []
        
        # Increase weight of stable models
        stable_models = [
            model_id for model_id, model_info in self.ensemble_state.models.items()
            if model_info.performance_score > 0.6
        ]
        
        if stable_models:
            weight_increase = 0.2 / len(stable_models)
            for model_id in stable_models:
                if model_id in self.ensemble_state.current_weights:
                    self.ensemble_state.current_weights[model_id] += weight_increase
                    adaptations.append(f"increased_weight_{model_id}")
        
        return adaptations
    
    def _adapt_for_trending_market(self) -> List[str]:
        """Trend bozor uchun moslashish"""
        
        adaptations = []
        
        # Boost models that perform well in trending conditions
        momentum_models = [
            model_id for model_id, model_info in self.ensemble_state.models.items()
            if 'momentum' in str(model_info.model_type).lower()
        ]
        
        if momentum_models:
            for model_id in momentum_models:
                if model_id in self.ensemble_state.current_weights:
                    self.ensemble_state.current_weights[model_id] *= 1.2
                    adaptations.append(f"boosted_momentum_model_{model_id}")
        
        return adaptations
    
    def _adapt_for_ranging_market(self) -> List[str]:
        """Ranging bozor uchun moslashish"""
        
        adaptations = []
        
        # Boost mean-reversion models
        reversion_models = [
            model_id for model_id, model_info in self.ensemble_state.models.items()
            if any(keyword in str(model_info.model).lower() 
                  for keyword in ['linear', 'regression', 'mean'])
        ]
        
        if reversion_models:
            for model_id in reversion_models:
                if model_id in self.ensemble_state.current_weights:
                    self.ensemble_state.current_weights[model_id] *= 1.15
                    adaptations.append(f"boosted_reversion_model_{model_id}")
        
        return adaptations

# Demo va test
if __name__ == "__main__":
    # Dynamic ensemble adapter testi
    ensemble_adapter = DynamicEnsembleAdapter({
        'adaptation_frequency': 5,
        'max_models': 5,
        'adaptation_strategy': AdaptationStrategy.HYBRID
    })
    
    # Add models
    model1 = {"type": "neural_network", "layers": [50, 25]}
    model2 = {"type": "random_forest", "n_estimators": 100}
    model3 = {"type": "xgboost", "max_depth": 5}
    
    model_ids = []
    model_ids.append(ensemble_adapter.add_model(model1, ModelType.NEURAL_NETWORK, 0.4))
    model_ids.append(ensemble_adapter.add_model(model2, ModelType.RANDOM_FOREST, 0.35))
    model_ids.append(ensemble_adapter.add_model(model3, ModelType.XGBOOST, 0.25))
    
    print("=== ENSEMBLE ADAPTER TEST ===")
    print(f"Added {len(model_ids)} models")
    print(f"Model IDs: {model_ids}")
    print(f"Initial weights: {ensemble_adapter.ensemble_state.current_weights}")
    
    # Make predictions
    test_data = np.random.randn(10, 5)
    
    for i in range(15):
        try:
            prediction, individual_preds = ensemble_adapter.predict(test_data, 'classification')
            
            if i % 5 == 0:
                print(f"\nPrediction {i+1}: {prediction[:3]}")  # Show first 3 predictions
                print(f"Individual predictions: {list(individual_preds.keys())}")
                
                # Simulate performance feedback
                performance_feedback = {
                    mid: np.random.uniform(0.6, 0.9) 
                    for mid in individual_preds.keys()
                }
                
                print(f"Performance feedback: {performance_feedback}")
        except Exception as e:
            print(f"Error in prediction {i+1}: {str(e)}")
    
    # Adapt ensemble
    adaptation_result = ensemble_adapter.adapt_ensemble()
    
    print(f"\n=== ENSEMBLE ADAPTATION ===")
    print(f"Adaptations performed: {adaptation_result['adaptations_performed']}")
    print(f"New weights: {adaptation_result['new_weights']}")
    print(f"Performance impact: {adaptation_result['performance_impact']:.4f}")
    
    # Get ensemble summary
    summary = ensemble_adapter.get_ensemble_summary()
    print(f"\n=== ENSEMBLE SUMMARY ===")
    print(f"Total models: {summary['total_models']}")
    print(f"Recent performance: {summary['recent_performance']:.4f}")
    print(f"Performance trend: {summary['performance_trend']}")
    print(f"Diversity score: {summary['diversity_score']:.4f}")
    
    # Trading-specific adapter test
    trading_ensemble = TradingEnsembleAdapter({
        'market_regime_adaptation': True,
        'volatility_adjustment': True
    })
    
    # Add trading models
    trading_model1 = {"type": "trend_model", "lookback": 20}
    trading_model2 = {"type": "mean_reversion", "window": 10}
    
    trading_ensemble.add_model(trading_model1, ModelType.NEURAL_NETWORK, 0.5)
    trading_ensemble.add_model(trading_model2, ModelType.RANDOM_FOREST, 0.5)
    
    # Test market regime adaptation
    market_conditions = {
        'regime': 'high_volatility',
        'volatility': 0.15,
        'trend_strength': 0.3
    }
    
    regime_adaptation = trading_ensemble.adapt_for_market_regime(market_conditions)
    
    print(f"\n=== TRADING ENSEMBLE REGIME ADAPTATION ===")
    print(f"Market regime: {regime_adaptation['regime']}")
    print(f"Adaptations: {regime_adaptation['adaptations']}")
    
    # Adaptive ensemble manager test
    manager = AdaptiveEnsembleManager({'target_model_count': 4})
    diverse_models = manager.create_diverse_ensemble(None, target_model_count=4)
    
    print(f"\n=== ADAPTIVE ENSEMBLE MANAGER ===")
    print(f"Created diverse ensemble: {diverse_models}")
    
    # Auto adaptation
    performance_data = {mid: np.random.uniform(0.6, 0.9) for mid in diverse_models}
    auto_adaptation = manager.auto_adapt_ensemble(performance_data, 'performance')
    
    print(f"Auto adaptation result: {auto_adaptation}")
    
    # Performance evaluator test
    evaluator = EnsemblePerformanceEvaluator()
    
    # Test with synthetic data
    test_X = np.random.randn(20, 5)
    test_y = np.random.randint(0, 2, 20)
    
    try:
        eval_metrics = evaluator.evaluate_ensemble_performance(
            ensemble_adapter, test_X, test_y
        )
        
        print(f"\n=== ENSEMBLE PERFORMANCE EVALUATION ===")
        print(f"Accuracy: {eval_metrics.get('accuracy', 'N/A'):.4f}")
        print(f"Diversity score: {eval_metrics.get('diversity_score', 'N/A'):.4f}")
        print(f"Average confidence: {eval_metrics.get('average_confidence', 'N/A'):.4f}")
        
        if 'individual_accuracies' in eval_metrics:
            print("Individual model accuracies:")
            for model_id, acc in eval_metrics['individual_accuracies'].items():
                print(f"  {model_id}: {acc:.4f}")
    
    except Exception as e:
        print(f"Error in evaluation: {str(e)}")
    
    print(f"\n=== ENSEMBLE TEST COMPLETED ===")