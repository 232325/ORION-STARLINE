"""
Base Algorithm - Self-Learning Fund tizimining asosiy algoritmi
Barcha algoritmlar uchun asos sinflar va interfeyslar
"""

import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class AlgorithmConfig:
    """Algoritm konfiguratsiyasi"""
    name: str
    learning_rate: float = 0.001
    batch_size: int = 32
    update_frequency: int = 100
    performance_threshold: float = 0.05
    max_iterations: int = 10000
    adaptive_learning: bool = True
    performance_tracking: bool = True

@dataclass
class PerformanceMetrics:
    """Model performance metrikalar"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    sharpe_ratio: float
    max_drawdown: float
    total_return: float
    volatility: float
    timestamp: datetime

class BaseAlgorithm(ABC):
    """Barcha algoritmlar uchun asosiy sinf"""
    
    def __init__(self, config: AlgorithmConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.name}")
        self.is_trained = False
        self.iteration_count = 0
        self.performance_history = []
        self.model_weights = {}
        self.last_update = None
        
    @abstractmethod
    def predict(self, data: np.ndarray) -> np.ndarray:
        """Ma'lumotlar bo'yicha bashorat qilish"""
        pass
    
    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray) -> None:
        """Modelni o'qitish"""
        pass
    
    @abstractmethod
    def update(self, new_data: np.ndarray, new_labels: np.ndarray) -> bool:
        """Modelni yangilash (online learning)"""
        pass
    
    def should_update(self) -> bool:
        """Model yangilanishi kerakligini aniqlash"""
        if not self.config.adaptive_learning:
            return False
            
        if self.iteration_count % self.config.update_frequency == 0:
            return True
            
        # Performance drop ni tekshirish
        if len(self.performance_history) >= 2:
            recent_perf = self.performance_history[-1]
            previous_perf = self.performance_history[-2]
            
            if recent_perf.total_return < previous_perf.total_return * (1 - self.config.performance_threshold):
                self.logger.warning("Performance drop detected, triggering update")
                return True
                
        return False
    
    def track_performance(self, predictions: np.ndarray, actual: np.ndarray) -> PerformanceMetrics:
        """Performance ni kuzatib borish"""
        # Asosiy metrikalarni hisoblash
        accuracy = np.mean(predictions == actual)
        precision = np.mean(predictions[predictions == 1] == actual[predictions == 1])
        recall = np.mean(actual[actual == 1] == predictions[actual == 1])
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Trading metrikalari
        returns = np.diff(actual) / actual[:-1] if len(actual) > 1 else np.array([0])
        pred_returns = np.diff(predictions) / predictions[:-1] if len(predictions) > 1 else np.array([0])
        
        sharpe_ratio = np.mean(pred_returns) / np.std(pred_returns) if np.std(pred_returns) > 0 else 0
        total_return = np.prod(1 + pred_returns) - 1
        volatility = np.std(pred_returns)
        max_drawdown = self._calculate_max_drawdown(pred_returns)
        
        metrics = PerformanceMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            total_return=total_return,
            volatility=volatility,
            timestamp=datetime.now()
        )
        
        self.performance_history.append(metrics)
        return metrics
    
    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """Maximum drawdown ni hisoblash"""
        cumulative = np.cumprod(1 + returns)
        peak = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - peak) / peak
        return np.min(drawdown)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Performance tarixiy ma'lumotlari"""
        if not self.performance_history:
            return {}
            
        latest = self.performance_history[-1]
        return {
            "current_performance": {
                "accuracy": latest.accuracy,
                "total_return": latest.total_return,
                "sharpe_ratio": latest.sharpe_ratio,
                "max_drawdown": latest.max_drawdown
            },
            "improvement_trend": self._calculate_improvement_trend(),
            "iterations": self.iteration_count,
            "last_update": self.last_update
        }
    
    def _calculate_improvement_trend(self) -> str:
        """Yaxshilanish tendensiyasini aniqlash"""
        if len(self.performance_history) < 5:
            return "insufficient_data"
            
        recent_returns = [p.total_return for p in self.performance_history[-5:]]
        if recent_returns[-1] > recent_returns[0]:
            return "improving"
        elif recent_returns[-1] < recent_returns[0]:
            return "declining"
        else:
            return "stable"

class SelfImprovingAlgorithm(BaseAlgorithm):
    """Self-improving qobiliyatli algoritm"""
    
    def __init__(self, config: AlgorithmConfig):
        super().__init__(config)
        self.improvement_strategies = []
        self.best_weights = None
        self.best_performance = float('-inf')
        self.adaptation_rate = 0.01
        self.patience = 10
        
    def add_improvement_strategy(self, strategy) -> None:
        """Improvement strategiyasini qo'shish"""
        self.improvement_strategies.append(strategy)
    
    def improve(self, performance_metrics: PerformanceMetrics) -> bool:
        """Modelni yaxshilash"""
        current_performance = performance_metrics.total_return
        
        # Best performance ni yangilash
        if current_performance > self.best_performance:
            self.best_performance = current_performance
            self.best_weights = self.model_weights.copy()
            self.logger.info(f"New best performance: {current_performance:.4f}")
        
        # Improvement strategiyasini qo'llash
        improved = False
        for strategy in self.improvement_strategies:
            if strategy.should_improve(performance_metrics):
                self.logger.info(f"Applying improvement strategy: {strategy.__class__.__name__}")
                strategy.apply(self)
                improved = True
                
        return improved
    
    def rollback_to_best(self) -> None:
        """Best performance ga qaytish"""
        if self.best_weights is not None:
            self.model_weights = self.best_weights.copy()
            self.logger.info("Rolled back to best performing weights")

class EnsembleSelfImproving(SelfImprovingAlgorithm):
    """Ensemble self-improving algorithm"""
    
    def __init__(self, config: AlgorithmConfig, n_models: int = 5):
        super().__init__(config)
        self.n_models = n_models
        self.models = []
        self.weights = np.ones(n_models) / n_models
        
        # Multiple model instances yaratish
        for i in range(n_models):
            model_config = AlgorithmConfig(
                name=f"{config.name}_model_{i}",
                learning_rate=config.learning_rate * (1 + i * 0.1),
                batch_size=config.batch_size,
                update_frequency=config.update_frequency,
                performance_threshold=config.performance_threshold,
                adaptive_learning=config.adaptive_learning
            )
            self.models.append(SelfImprovingAlgorithm(model_config))
    
    def predict(self, data: np.ndarray) -> np.ndarray:
        """Ensemble prediction"""
        predictions = []
        for model in self.models:
            pred = model.predict(data)
            predictions.append(pred)
        
        # Weight-based aggregation
        ensemble_pred = np.average(predictions, axis=0, weights=self.weights)
        return ensemble_pred
    
    def update_weights(self, performance_scores: List[float]) -> None:
        """Ensemble weight larini yangilash"""
        # Performance-based weight allocation
        max_score = max(performance_scores) if performance_scores else 1
        normalized_scores = [score / max_score for score in performance_scores]
        
        # Softmax activation
        exp_scores = np.exp(normalized_scores)
        self.weights = exp_scores / np.sum(exp_scores)
        
        self.logger.info(f"Updated ensemble weights: {self.weights}")