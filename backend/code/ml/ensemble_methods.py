"""
Ensemble Methods for Trading Predictions
=========================================

Bu modul ensemble learning texnikalarini o'z ichiga oladi:
- Model Aggregation - Combining multiple model predictions
- Stacking - Meta-learning on model outputs
- Boosting - Gradient boosting for trading signals
- Bagging - Bootstrap aggregating for robustness
- Weighted Voting - Dynamic weight assignment
- Prediction Diversity - Ensuring model diversity

Author: AI Trading Evolution
Date: 2025-11-04
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import logging
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class EnsembleConfig:
    """Ensemble konfiguratsiya"""
    num_base_models: int = 5
    diversity_threshold: float = 0.3
    min_correlation: float = -1.0
    max_correlation: float = 0.7
    aggregation_method: str = "weighted_avg"  # weighted_avg, voting, stacking
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


@dataclass
class PredictionResult:
    """Bashorat natijasi"""
    prediction: float
    confidence: float
    model_predictions: Dict[str, float]
    model_weights: Dict[str, float]
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        return {
            'prediction': self.prediction,
            'confidence': self.confidence,
            'model_predictions': self.model_predictions,
            'model_weights': self.model_weights,
            'timestamp': self.timestamp.isoformat()
        }


# ============================================================================
# Base Model Interface
# ============================================================================

class BasePredictor:
    """Base class for ensemble models"""
    
    def __init__(self, name: str):
        self.name = name
        self.performance_history = []
        
    def predict(self, x: np.ndarray) -> np.ndarray:
        """Bashorat qilish"""
        raise NotImplementedError
        
    def update_performance(self, accuracy: float):
        """Performance yangilash"""
        self.performance_history.append(accuracy)
        
    def get_recent_performance(self, window: int = 100) -> float:
        """So'nggi performance"""
        if not self.performance_history:
            return 0.5
        return np.mean(self.performance_history[-window:])


# ============================================================================
# Simple Weighted Ensemble
# ============================================================================

class WeightedEnsemble:
    """Weighted ensemble of models"""
    
    def __init__(self, config: EnsembleConfig):
        self.config = config
        self.models: Dict[str, BasePredictor] = {}
        self.weights: Dict[str, float] = {}
        
    def add_model(self, model: BasePredictor, initial_weight: float = 1.0):
        """Model qo'shish"""
        self.models[model.name] = model
        self.weights[model.name] = initial_weight
        logger.info(f"Added model: {model.name} with weight {initial_weight}")
        
    def normalize_weights(self):
        """Weightlarni normalize qilish"""
        total_weight = sum(self.weights.values())
        if total_weight > 0:
            for name in self.weights:
                self.weights[name] /= total_weight
                
    def predict(self, x: np.ndarray) -> PredictionResult:
        """Ensemble bashorat"""
        if not self.models:
            raise ValueError("No models in ensemble")
            
        # Get predictions from all models
        model_predictions = {}
        for name, model in self.models.items():
            pred = model.predict(x)
            model_predictions[name] = float(pred[0]) if isinstance(pred, np.ndarray) else float(pred)
            
        # Normalize weights
        self.normalize_weights()
        
        # Weighted average
        ensemble_pred = sum(model_predictions[name] * self.weights[name] 
                          for name in model_predictions)
        
        # Calculate confidence based on agreement
        predictions_array = np.array(list(model_predictions.values()))
        confidence = 1.0 - (np.std(predictions_array) / (np.mean(predictions_array) + 1e-6))
        confidence = max(0, min(1, confidence))
        
        return PredictionResult(
            prediction=ensemble_pred,
            confidence=confidence,
            model_predictions=model_predictions,
            model_weights=self.weights.copy(),
            timestamp=datetime.now()
        )
        
    def update_weights_by_performance(self, window: int = 100):
        """Performance asosida weightlarni yangilash"""
        for name, model in self.models.items():
            performance = model.get_recent_performance(window)
            self.weights[name] = max(0.01, performance)  # Minimum 0.01 weight
            
        self.normalize_weights()
        logger.info(f"Updated weights: {self.weights}")
        
    def update_weights_by_diversity(self, predictions_history: List[Dict[str, float]]):
        """Diversity asosida weightlarni yangilash"""
        if len(predictions_history) < 10:
            return
            
        # Calculate correlation matrix
        model_names = list(self.models.keys())
        n_models = len(model_names)
        
        # Extract prediction sequences
        pred_sequences = {name: [] for name in model_names}
        for pred_dict in predictions_history:
            for name in model_names:
                pred_sequences[name].append(pred_dict.get(name, 0))
                
        # Correlation matrix
        correlations = np.zeros((n_models, n_models))
        for i, name1 in enumerate(model_names):
            for j, name2 in enumerate(model_names):
                if i == j:
                    correlations[i, j] = 1.0
                else:
                    corr = np.corrcoef(pred_sequences[name1], pred_sequences[name2])[0, 1]
                    correlations[i, j] = corr
                    
        # Adjust weights to promote diversity
        for i, name in enumerate(model_names):
            avg_corr = np.mean(correlations[i, :])
            
            # Lower weight for highly correlated models
            if avg_corr > self.config.max_correlation:
                diversity_penalty = 0.5
            else:
                diversity_penalty = 1.0
                
            self.weights[name] *= diversity_penalty
            
        self.normalize_weights()


# ============================================================================
# Stacking Ensemble
# ============================================================================

class StackingEnsemble:
    """Stacking with meta-learner"""
    
    def __init__(self, config: EnsembleConfig):
        self.config = config
        self.base_models: List[BasePredictor] = []
        
        # Meta-learner (neural network)
        self.meta_learner = nn.Sequential(
            nn.Linear(config.num_base_models, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
        
        self.device = torch.device(config.device)
        self.meta_learner.to(self.device)
        
        self.optimizer = optim.Adam(self.meta_learner.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()
        
    def add_base_model(self, model: BasePredictor):
        """Base model qo'shish"""
        self.base_models.append(model)
        logger.info(f"Added base model: {model.name}")
        
    def train_meta_learner(self, X_train: np.ndarray, y_train: np.ndarray,
                          epochs: int = 100, batch_size: int = 32):
        """Meta-learner o'rgatish"""
        
        logger.info("Training meta-learner on base model predictions")
        
        # Get predictions from base models
        base_predictions = []
        for model in self.base_models:
            preds = model.predict(X_train)
            base_predictions.append(preds)
            
        # Stack predictions
        X_meta = np.column_stack(base_predictions)
        
        # Convert to tensors
        X_meta_tensor = torch.FloatTensor(X_meta).to(self.device)
        y_tensor = torch.FloatTensor(y_train).to(self.device)
        
        # Training loop
        for epoch in range(epochs):
            # Shuffle
            indices = np.random.permutation(len(X_meta))
            
            epoch_loss = 0.0
            num_batches = 0
            
            for i in range(0, len(indices), batch_size):
                batch_indices = indices[i:i+batch_size]
                
                batch_X = X_meta_tensor[batch_indices]
                batch_y = y_tensor[batch_indices]
                
                # Forward
                self.optimizer.zero_grad()
                predictions = self.meta_learner(batch_X).squeeze()
                loss = self.criterion(predictions, batch_y)
                
                # Backward
                loss.backward()
                self.optimizer.step()
                
                epoch_loss += loss.item()
                num_batches += 1
                
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs} - Loss: {epoch_loss/num_batches:.4f}")
                
    def predict(self, x: np.ndarray) -> PredictionResult:
        """Stacking bashorat"""
        
        # Get base model predictions
        base_predictions = []
        model_preds_dict = {}
        
        for model in self.base_models:
            pred = model.predict(x)
            pred_value = float(pred[0]) if isinstance(pred, np.ndarray) else float(pred)
            base_predictions.append(pred_value)
            model_preds_dict[model.name] = pred_value
            
        # Meta-learner prediction
        X_meta = torch.FloatTensor([base_predictions]).to(self.device)
        
        self.meta_learner.eval()
        with torch.no_grad():
            meta_pred = self.meta_learner(X_meta).item()
            
        # Confidence based on base model agreement
        confidence = 1.0 - (np.std(base_predictions) / (np.mean(base_predictions) + 1e-6))
        confidence = max(0, min(1, confidence))
        
        return PredictionResult(
            prediction=meta_pred,
            confidence=confidence,
            model_predictions=model_preds_dict,
            model_weights={m.name: 1.0/len(self.base_models) for m in self.base_models},
            timestamp=datetime.now()
        )


# ============================================================================
# Boosting Ensemble
# ============================================================================

class AdaptiveBoostingEnsemble:
    """Adaptive boosting for trading signals"""
    
    def __init__(self, config: EnsembleConfig):
        self.config = config
        self.weak_learners = []
        self.learner_weights = []
        
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
             num_iterations: int = 50):
        """AdaBoost training"""
        
        n_samples = len(X_train)
        
        # Initialize sample weights
        sample_weights = np.ones(n_samples) / n_samples
        
        logger.info(f"Training AdaBoost with {num_iterations} iterations")
        
        for iteration in range(num_iterations):
            # Train weak learner on weighted samples
            weak_learner = self._train_weak_learner(X_train, y_train, sample_weights)
            
            # Get predictions
            predictions = weak_learner.predict(X_train)
            
            # Calculate error
            errors = (predictions != y_train).astype(float)
            weighted_error = np.sum(sample_weights * errors) / np.sum(sample_weights)
            
            # Calculate learner weight
            if weighted_error >= 0.5:
                break
                
            learner_weight = 0.5 * np.log((1 - weighted_error) / (weighted_error + 1e-10))
            
            # Update sample weights
            sample_weights *= np.exp(learner_weight * errors)
            sample_weights /= np.sum(sample_weights)
            
            # Store learner
            self.weak_learners.append(weak_learner)
            self.learner_weights.append(learner_weight)
            
            if (iteration + 1) % 10 == 0:
                logger.info(f"Iteration {iteration+1}/{num_iterations} - "
                          f"Error: {weighted_error:.4f}, Weight: {learner_weight:.4f}")
                
    def _train_weak_learner(self, X: np.ndarray, y: np.ndarray, 
                           weights: np.ndarray):
        """Train a weak learner (decision stump)"""
        
        # Simple decision tree with max_depth=1
        from sklearn.tree import DecisionTreeClassifier
        
        weak_learner = DecisionTreeClassifier(max_depth=1)
        weak_learner.fit(X, y, sample_weight=weights)
        
        return weak_learner
        
    def predict(self, x: np.ndarray) -> float:
        """AdaBoost bashorat"""
        
        if not self.weak_learners:
            return 0.0
            
        # Weighted vote
        predictions = []
        for learner, weight in zip(self.weak_learners, self.learner_weights):
            pred = learner.predict(x.reshape(1, -1))[0]
            predictions.append(pred * weight)
            
        final_pred = np.sign(sum(predictions))
        
        return final_pred


# ============================================================================
# Bagging Ensemble
# ============================================================================

class BaggingEnsemble:
    """Bootstrap aggregating ensemble"""
    
    def __init__(self, config: EnsembleConfig, base_model_class: Any):
        self.config = config
        self.base_model_class = base_model_class
        self.models = []
        
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
             n_estimators: int = 10, sample_ratio: float = 0.8):
        """Bagging training"""
        
        n_samples = len(X_train)
        bootstrap_size = int(n_samples * sample_ratio)
        
        logger.info(f"Training {n_estimators} bagged models")
        
        for i in range(n_estimators):
            # Bootstrap sample
            indices = np.random.choice(n_samples, bootstrap_size, replace=True)
            X_bootstrap = X_train[indices]
            y_bootstrap = y_train[indices]
            
            # Train model
            model = self.base_model_class()
            model.fit(X_bootstrap, y_bootstrap)
            
            self.models.append(model)
            
            if (i + 1) % 5 == 0:
                logger.info(f"Trained {i+1}/{n_estimators} models")
                
    def predict(self, x: np.ndarray) -> PredictionResult:
        """Bagging bashorat"""
        
        predictions = []
        for model in self.models:
            pred = model.predict(x.reshape(1, -1))[0]
            predictions.append(pred)
            
        # Average prediction
        avg_pred = np.mean(predictions)
        
        # Confidence from variance
        confidence = 1.0 - (np.std(predictions) / (np.abs(avg_pred) + 1e-6))
        confidence = max(0, min(1, confidence))
        
        return PredictionResult(
            prediction=avg_pred,
            confidence=confidence,
            model_predictions={f"model_{i}": p for i, p in enumerate(predictions)},
            model_weights={f"model_{i}": 1.0/len(self.models) for i in range(len(self.models))},
            timestamp=datetime.now()
        )


# ============================================================================
# Dynamic Ensemble with Online Learning
# ============================================================================

class DynamicEnsemble:
    """Dynamic ensemble with online weight adaptation"""
    
    def __init__(self, config: EnsembleConfig):
        self.config = config
        self.models: Dict[str, BasePredictor] = {}
        self.weights: Dict[str, float] = {}
        self.performance_window = 100
        self.predictions_history = []
        
    def add_model(self, model: BasePredictor):
        """Model qo'shish"""
        self.models[model.name] = model
        self.weights[model.name] = 1.0 / (len(self.models) + 1)
        
    def predict(self, x: np.ndarray) -> PredictionResult:
        """Dynamic ensemble bashorat"""
        
        # Get predictions
        model_predictions = {}
        for name, model in self.models.items():
            pred = model.predict(x)
            model_predictions[name] = float(pred[0]) if isinstance(pred, np.ndarray) else float(pred)
            
        # Normalize weights
        total_weight = sum(self.weights.values())
        normalized_weights = {k: v/total_weight for k, v in self.weights.items()}
        
        # Weighted prediction
        ensemble_pred = sum(model_predictions[name] * normalized_weights[name] 
                          for name in model_predictions)
        
        # Calculate confidence
        predictions_array = np.array(list(model_predictions.values()))
        confidence = 1.0 - (np.std(predictions_array) / (np.mean(predictions_array) + 1e-6))
        confidence = max(0, min(1, confidence))
        
        # Store history
        self.predictions_history.append(model_predictions)
        if len(self.predictions_history) > self.performance_window:
            self.predictions_history.pop(0)
            
        return PredictionResult(
            prediction=ensemble_pred,
            confidence=confidence,
            model_predictions=model_predictions,
            model_weights=normalized_weights,
            timestamp=datetime.now()
        )
        
    def update_weights(self, true_value: float):
        """Update weights based on prediction accuracy"""
        
        if not self.predictions_history:
            return
            
        # Get last predictions
        last_predictions = self.predictions_history[-1]
        
        # Calculate errors
        for name, pred in last_predictions.items():
            error = abs(pred - true_value)
            
            # Update weight (inverse of error)
            # Better predictions get higher weights
            if error < 1e-6:
                self.weights[name] *= 1.1  # Reward perfect prediction
            else:
                accuracy = 1.0 / (1.0 + error)
                self.weights[name] = 0.9 * self.weights[name] + 0.1 * accuracy
                
        # Ensure minimum weight
        for name in self.weights:
            self.weights[name] = max(0.01, self.weights[name])
            
        # Normalize
        total = sum(self.weights.values())
        for name in self.weights:
            self.weights[name] /= total


# ============================================================================
# Diversity Metrics
# ============================================================================

class DiversityAnalyzer:
    """Analyze ensemble diversity"""
    
    @staticmethod
    def calculate_disagreement(predictions: List[np.ndarray]) -> float:
        """Calculate pairwise disagreement"""
        
        n_models = len(predictions)
        if n_models < 2:
            return 0.0
            
        disagreements = []
        for i in range(n_models):
            for j in range(i+1, n_models):
                disagreement = np.mean(predictions[i] != predictions[j])
                disagreements.append(disagreement)
                
        return np.mean(disagreements)
        
    @staticmethod
    def calculate_q_statistic(predictions: List[np.ndarray], 
                             true_labels: np.ndarray) -> float:
        """Calculate Q-statistic for diversity"""
        
        n_models = len(predictions)
        if n_models < 2:
            return 0.0
            
        q_values = []
        for i in range(n_models):
            for j in range(i+1, n_models):
                # Confusion matrix elements
                n11 = np.sum((predictions[i] == true_labels) & (predictions[j] == true_labels))
                n00 = np.sum((predictions[i] != true_labels) & (predictions[j] != true_labels))
                n10 = np.sum((predictions[i] == true_labels) & (predictions[j] != true_labels))
                n01 = np.sum((predictions[i] != true_labels) & (predictions[j] == true_labels))
                
                # Q-statistic
                numerator = n11 * n00 - n01 * n10
                denominator = n11 * n00 + n01 * n10
                
                if denominator > 0:
                    q = numerator / denominator
                    q_values.append(q)
                    
        return np.mean(q_values) if q_values else 0.0
        
    @staticmethod
    def calculate_correlation_coefficient(predictions: List[np.ndarray]) -> float:
        """Calculate average correlation between models"""
        
        n_models = len(predictions)
        if n_models < 2:
            return 0.0
            
        correlations = []
        for i in range(n_models):
            for j in range(i+1, n_models):
                corr = np.corrcoef(predictions[i], predictions[j])[0, 1]
                correlations.append(corr)
                
        return np.mean(correlations)


if __name__ == "__main__":
    logger.info("Ensemble Methods moduli yuklandi!")
    logger.info("Weighted Ensemble, Stacking, Boosting, Bagging tayyor")
    logger.info("Dynamic weight adaptation va diversity analysis qo'llab-quvvatlanadi")
