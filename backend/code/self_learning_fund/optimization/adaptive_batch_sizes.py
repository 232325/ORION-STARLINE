"""
Adaptive Batch Sizes Optimization for Self-Learning Trading Fund
==============================================================

Machine learning modellari uchun moslashuvchan batch size optimallashtirish.
Model o'rganish tezligi va performance ni optimallashtirish.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta
import warnings
from dataclasses import dataclass
from enum import Enum
import logging
from collections import deque, defaultdict
import math

from ..core.base_algorithm import BaseAlgorithm
from ..core.adaptive_model import AdaptiveModel
from ..core.performance_tracker import PerformanceTracker

class BatchSizeStrategy(Enum):
    """Batch size strategiyasi"""
    FIXED = "Fixed"
    ADAPTIVE = "Adaptive"
    SCHEDULED = "Scheduled"
    PERFORMANCE_BASED = "Performance_Based"
    VOLATILITY_BASED = "Volatility_Based"
    GRADIENT_BASED = "Gradient_Based"
    WARM_RESTART = "Warm_Restart"

class OptimizationPhase(Enum):
    """Optimallashtirish fazalari"""
    EXPLORATION = "Exploration"
    CONVERGENCE = "Convergence"
    FINE_TUNING = "Fine_Tuning"
    VALIDATION = "Validation"
    DEPLOYMENT = "Deployment"

@dataclass
class BatchSizeConfig:
    """Batch size konfiguratsiyasi"""
    base_batch_size: int
    min_batch_size: int
    max_batch_size: int
    adaptation_frequency: int  # after how many epochs
    performance_threshold: float
    volatility_threshold: float
    gradient_threshold: float

@dataclass
class TrainingContext:
    """Training konteksti"""
    current_epoch: int
    current_loss: float
    validation_loss: float
    learning_rate: float
    batch_size: int
    data_volatility: float
    gradient_norm: float
    training_time: float
    memory_usage: float

class AdaptiveBatchSizeOptimizer(BaseAlgorithm):
    """Moslashuvchan batch size optimallashtiruvchi"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        self.batch_config = BatchSizeConfig(
            base_batch_size=config.get('base_batch_size', 32) if config else 32,
            min_batch_size=config.get('min_batch_size', 8) if config else 8,
            max_batch_size=config.get('max_batch_size', 512) if config else 512,
            adaptation_frequency=config.get('adaptation_frequency', 10) if config else 10,
            performance_threshold=config.get('performance_threshold', 0.01) if config else 0.01,
            volatility_threshold=config.get('volatility_threshold', 0.05) if config else 0.05,
            gradient_threshold=config.get('gradient_threshold', 1.0) if config else 1.0
        )
        
        self.current_strategy = BatchSizeStrategy.ADAPTIVE
        self.optimization_history = []
        self.performance_metrics = deque(maxlen=100)
        self.batch_size_history = deque(maxlen=50)
        
    def adapt_batch_size(self, context: TrainingContext) -> Tuple[int, Dict[str, Any]]:
        """Batch size moslashish"""
        
        # Hozirgi batch size
        current_batch_size = context.batch_size
        
        # Performance-based adaptation
        performance_adapted_size = self._performance_based_adaptation(context)
        
        # Volatility-based adaptation
        volatility_adapted_size = self._volatility_based_adaptation(context)
        
        # Gradient-based adaptation
        gradient_adapted_size = self._gradient_based_adaptation(context)
        
        # Convergence-based adaptation
        convergence_adapted_size = self._convergence_based_adaptation(context)
        
        # Combine adaptations
        final_batch_size = self._combine_adaptations(
            current_batch_size, 
            [performance_adapted_size, volatility_adapted_size, 
             gradient_adapted_size, convergence_adapted_size],
            context
        )
        
        # Clamp to allowed range
        final_batch_size = max(
            self.batch_config.min_batch_size,
            min(self.batch_config.max_batch_size, final_batch_size)
        )
        
        # Save adaptation decision
        adaptation_result = {
            'current_batch_size': current_batch_size,
            'adapted_batch_size': final_batch_size,
            'performance_adaptation': performance_adapted_size,
            'volatility_adaptation': volatility_adapted_size,
            'gradient_adaptation': gradient_adapted_size,
            'convergence_adaptation': convergence_adapted_size,
            'adaptation_reason': self._get_adaptation_reason(context),
            'confidence': self._calculate_adaptation_confidence(context)
        }
        
        self.batch_size_history.append(final_batch_size)
        self.performance_metrics.append({
            'epoch': context.current_epoch,
            'batch_size': final_batch_size,
            'loss': context.current_loss,
            'validation_loss': context.validation_loss,
            'time': context.training_time
        })
        
        return final_batch_size, adaptation_result
    
    def _performance_based_adaptation(self, context: TrainingContext) -> int:
        """Performance asosida batch size moslashish"""
        
        if len(self.performance_metrics) < 5:
            return self.batch_config.base_batch_size
        
        # Recent performance trend
        recent_losses = [m['loss'] for m in list(self.performance_metrics)[-5:]]
        recent_val_losses = [m['validation_loss'] for m in list(self.performance_metrics)[-5:]]
        
        # Loss improvement rate
        loss_trend = recent_losses[-1] - recent_losses[0]
        val_loss_trend = recent_val_losses[-1] - recent_val_losses[0]
        
        # Overfitting detection
        validation_gap = recent_val_losses[-1] - recent_losses[-1]
        
        # Adaptation logic
        if loss_trend > self.batch_config.performance_threshold:
            # Loss not improving - try smaller batches for better convergence
            if validation_gap > 0.01:  # Overfitting detected
                return max(self.batch_config.min_batch_size, 
                          context.batch_size // 2)
            else:
                # Normal improvement, keep batch size
                return context.batch_size
        
        elif loss_trend < -self.batch_config.performance_threshold:
            # Good improvement - increase batch size for stability
            if context.batch_size < self.batch_config.max_batch_size // 2:
                return min(context.batch_size * 2, self.batch_config.max_batch_size)
        
        elif validation_gap > 0.02:
            # Significant overfitting - reduce batch size
            return max(self.batch_config.min_batch_size,
                      context.batch_size // 2)
        
        return context.batch_size
    
    def _volatility_based_adaptation(self, context: TrainingContext) -> int:
        """Volatillik asosida batch size moslashish"""
        
        volatility = context.data_volatility
        
        if volatility > 0.1:  # High volatility
            # Use smaller batches for better generalization
            return max(self.batch_config.min_batch_size,
                      context.batch_size // 2)
        
        elif volatility < 0.02:  # Low volatility
            # Use larger batches for efficiency
            return min(context.batch_size * 2, self.batch_config.max_batch_size)
        
        return context.batch_size
    
    def _gradient_based_adaptation(self, context: TrainingContext) -> int:
        """Gradient norm asosida batch size moslashish"""
        
        gradient_norm = context.gradient_norm
        
        if gradient_norm > self.batch_config.gradient_threshold:
            # Large gradients - reduce batch size for more stable updates
            return max(self.batch_config.min_batch_size,
                      context.batch_size // 2)
        
        elif gradient_norm < 0.1:  # Small gradients
            # Increase batch size to capture more signal
            return min(context.batch_size * 2, self.batch_config.max_batch_size)
        
        return context.batch_size
    
    def _convergence_based_adaptation(self, context: TrainingContext) -> int:
        """Konvergentsiya asosida batch size moslashish"""
        
        # Epoch-based convergence indicators
        epochs_since_improvement = 0
        if len(self.performance_metrics) >= 10:
            recent_losses = [m['loss'] for m in list(self.performance_metrics)[-10:]]
            best_loss = min(recent_losses)
            best_epoch = recent_losses.index(best_loss)
            epochs_since_improvement = len(recent_losses) - best_epoch - 1
        
        # Early training - use smaller batches for exploration
        if context.current_epoch < 10:
            return max(self.batch_config.min_batch_size,
                      context.batch_size // 2)
        
        # Stuck in local minimum - reduce batch size
        if epochs_since_improvement > 5:
            return max(self.batch_config.min_batch_size,
                      context.batch_size // 2)
        
        # Converging well - increase batch size
        if epochs_since_improvement == 0 and context.batch_size < self.batch_config.max_batch_size:
            return min(context.batch_size * 1.5, self.batch_config.max_batch_size)
        
        return context.batch_size
    
    def _combine_adaptations(self, current_size: int, 
                           adaptations: List[int], 
                           context: TrainingContext) -> int:
        """Adaptatsiyalarni birlashtirish"""
        
        # Weight different adaptation methods
        weights = {
            'performance': 0.4,
            'volatility': 0.2,
            'gradient': 0.2,
            'convergence': 0.2
        }
        
        # Calculate weighted average (but only consider significant changes)
        significant_changes = [size for size in adaptations if abs(size - current_size) > 2]
        
        if not significant_changes:
            return current_size
        
        # Use median of significant changes to avoid outliers
        return int(np.median(significant_changes))
    
    def _get_adaptation_reason(self, context: TrainingContext) -> str:
        """Adaptatsiya sababini aniqlash"""
        
        if len(self.performance_metrics) < 5:
            return "insufficient_history"
        
        recent_losses = [m['loss'] for m in list(self.performance_metrics)[-5:]]
        loss_trend = recent_losses[-1] - recent_losses[0]
        
        validation_gap = context.validation_loss - context.current_loss
        
        if abs(loss_trend) > self.batch_config.performance_threshold:
            return "performance_trend"
        elif validation_gap > 0.01:
            return "overfitting_prevention"
        elif context.data_volatility > 0.1:
            return "high_volatility"
        elif context.gradient_norm > self.batch_config.gradient_threshold:
            return "gradient_instability"
        else:
            return "maintenance"
    
    def _calculate_adaptation_confidence(self, context: TrainingContext) -> float:
        """Adaptatsiya ishonchliligini hisoblash"""
        
        confidence_factors = []
        
        # Data history
        if len(self.performance_metrics) > 10:
            confidence_factors.append(0.9)
        elif len(self.performance_metrics) > 5:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)
        
        # Performance stability
        if len(self.performance_metrics) >= 5:
            recent_losses = [m['loss'] for m in list(self.performance_metrics)[-5:]]
            loss_stability = 1.0 / (1.0 + np.std(recent_losses))
            confidence_factors.append(loss_stability)
        
        # Data quality
        if context.data_volatility > 0 and context.data_volatility < 1:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.5)
        
        return np.mean(confidence_factors)
    
    def get_optimal_batch_schedule(self, total_epochs: int) -> List[int]:
        """Optimal batch size jadvalini olish"""
        
        schedule = []
        
        # Warmup phase - small batches
        warmup_epochs = min(10, total_epochs // 4)
        warmup_batch_size = self.batch_config.min_batch_size
        
        for epoch in range(warmup_epochs):
            schedule.append(warmup_batch_size)
        
        # Training phase - adaptive batches
        remaining_epochs = total_epochs - warmup_epochs
        
        # Create context for simulation
        simulated_context = TrainingContext(
            current_epoch=warmup_epochs,
            current_loss=1.0,
            validation_loss=1.0,
            learning_rate=0.001,
            batch_size=warmup_batch_size,
            data_volatility=0.05,
            gradient_norm=0.5,
            training_time=100.0,
            memory_usage=0.5
        )
        
        for epoch in range(warmup_epochs, total_epochs):
            batch_size, _ = self.adapt_batch_size(simulated_context)
            schedule.append(batch_size)
            
            # Update context for next iteration
            simulated_context.current_epoch = epoch + 1
            simulated_context.batch_size = batch_size
            # Simulate improvement
            simulated_context.current_loss *= 0.99
            simulated_context.validation_loss *= 0.99
        
        return schedule

class ScheduledBatchSizeManager:
    """Dasturli batch size boshqaruvchi"""
    
    def __init__(self, schedule_config: Optional[Dict] = None):
        self.schedule_config = schedule_config or {}
        
    def create_cosine_schedule(self, total_epochs: int, 
                             min_batch: int = 16, max_batch: int = 256) -> List[int]:
        """Cosine annealing schedule"""
        
        schedule = []
        
        for epoch in range(total_epochs):
            # Cosine function from min to max
            progress = epoch / total_epochs
            batch_size = min_batch + (max_batch - min_batch) * (1 + math.cos(math.pi * progress)) / 2
            schedule.append(int(batch_size))
        
        return schedule
    
    def create_step_schedule(self, total_epochs: int, 
                           schedule: List[Tuple[int, int]]) -> List[int]:
        """Step schedule (epoch, batch_size pairs)"""
        
        result = []
        
        for epoch in range(total_epochs):
            # Find appropriate batch size for current epoch
            current_batch = schedule[0][1]  # Default
            
            for schedule_epoch, batch_size in schedule:
                if epoch < schedule_epoch:
                    break
                current_batch = batch_size
            
            result.append(current_batch)
        
        return result
    
    def create_exponential_schedule(self, total_epochs: int,
                                  start_batch: int = 16,
                                  growth_rate: float = 1.1) -> List[int]:
        """Exponential growth schedule"""
        
        schedule = []
        
        for epoch in range(total_epochs):
            # Exponential growth with saturation
            batch_size = start_batch * (growth_rate ** epoch)
            batch_size = min(batch_size, 512)  # Cap at max
            schedule.append(int(batch_size))
        
        return schedule

class PerformanceBasedBatchOptimizer:
    """Performance asosida batch size optimallashtiruvchi"""
    
    def __init__(self):
        self.performance_window = 20
        self.performance_history = deque(maxlen=self.performance_window)
        
    def optimize_batch_size(self, model: Any, 
                          train_loader: Any, 
                          validation_loader: Any,
                          current_batch_size: int) -> int:
        """Performance asosida optimal batch size topish"""
        
        # Train with current batch size
        current_performance = self._evaluate_performance(model, train_loader, validation_loader)
        self.performance_history.append({
            'batch_size': current_batch_size,
            'performance': current_performance,
            'timestamp': datetime.now()
        })
        
        if len(self.performance_history) < 3:
            return current_batch_size
        
        # Find best performing batch size
        best_entry = max(self.performance_history, key=lambda x: x['performance'])
        best_batch_size = best_entry['batch_size']
        
        # Propose new batch size based on performance trend
        recent_performances = [entry['performance'] for entry in list(self.performance_history)[-5:]]
        
        if len(recent_performances) >= 3:
            performance_trend = recent_performances[-1] - recent_performances[0]
            
            if performance_trend < 0:  # Performance degrading
                # Try smaller batch size
                return max(8, current_batch_size // 2)
            elif performance_trend > 0.01:  # Good improvement
                # Increase batch size for efficiency
                return min(512, current_batch_size * 2)
        
        return current_batch_size
    
    def _evaluate_performance(self, model: Any, train_loader: Any, 
                            validation_loader: Any) -> float:
        """Model performance baholash"""
        
        # Simplified performance evaluation
        # In real implementation, would train one epoch and measure
        
        # Simulate training performance
        base_performance = 0.85
        noise = np.random.normal(0, 0.05)
        
        return max(0, min(1, base_performance + noise))

class BatchSizeValidator:
    """Batch size validatori"""
    
    def __init__(self):
        self.validation_metrics = {}
        
    def validate_batch_size(self, batch_size: int, 
                          model_params: int,
                          memory_limit: float) -> Dict[str, Any]:
        """Batch size ni validatsiya qilish"""
        
        validation_result = {
            'batch_size': batch_size,
            'is_valid': True,
            'warnings': [],
            'recommendations': [],
            'estimated_memory': self._estimate_memory_usage(batch_size, model_params),
            'throughput_score': self._calculate_throughput_score(batch_size),
            'convergence_score': self._calculate_convergence_score(batch_size)
        }
        
        # Memory validation
        if validation_result['estimated_memory'] > memory_limit:
            validation_result['is_valid'] = False
            validation_result['warnings'].append(f"Memory usage {validation_result['estimated_memory']:.2f} exceeds limit {memory_limit}")
        
        # Throughput validation
        if validation_result['throughput_score'] < 0.5:
            validation_result['warnings'].append("Low throughput expected with this batch size")
        
        # Convergence validation
        if validation_result['convergence_score'] < 0.6:
            validation_result['recommendations'].append("Consider smaller batch size for better convergence")
        
        return validation_result
    
    def _estimate_memory_usage(self, batch_size: int, model_params: int) -> float:
        """Memory usage taxmin qilish"""
        
        # Simplified memory estimation
        # Assume 4 bytes per parameter and some overhead
        param_memory = (model_params * 4) / (1024 ** 2)  # MB
        batch_memory = (batch_size * 4 * 1000) / (1024 ** 2)  # MB (estimated 1000 features per sample)
        
        return param_memory + batch_memory
    
    def _calculate_throughput_score(self, batch_size: int) -> float:
        """Throughput ballini hisoblash"""
        
        # Optimal batch size around 32-64
        if 32 <= batch_size <= 64:
            return 1.0
        elif 16 <= batch_size < 32 or 64 < batch_size <= 128:
            return 0.8
        elif 8 <= batch_size < 16 or 128 < batch_size <= 256:
            return 0.6
        else:
            return 0.3
    
    def _calculate_convergence_score(self, batch_size: int) -> float:
        """Konvergentsiya ballini hisoblash"""
        
        # Smaller batches generally converge better
        if batch_size <= 16:
            return 1.0
        elif batch_size <= 32:
            return 0.9
        elif batch_size <= 64:
            return 0.8
        elif batch_size <= 128:
            return 0.7
        else:
            return 0.5

class BatchSizeOptimizerEnsemble:
    """Batch size optimallashtiruvchi ansambli"""
    
    def __init__(self):
        self.adaptive_optimizer = AdaptiveBatchSizeOptimizer()
        self.performance_optimizer = PerformanceBasedBatchOptimizer()
        self.scheduler = ScheduledBatchSizeManager()
        self.validator = BatchSizeValidator()
        
        self.optimizer_weights = {
            'adaptive': 0.4,
            'performance': 0.3,
            'scheduled': 0.2,
            'validator': 0.1
        }
    
    def optimize_ensemble(self, context: TrainingContext) -> Tuple[int, Dict[str, Any]]:
        """Ensemble optimallashtirish"""
        
        # Get recommendations from each optimizer
        adaptive_result = self.adaptive_optimizer.adapt_batch_size(context)
        performance_result = self.performance_optimizer.optimize_batch_size(
            None, None, None, context.batch_size
        )
        
        # Scheduled recommendation
        if hasattr(context, 'epoch_schedule'):
            scheduled_result = context.epoch_schedule.get(context.current_epoch, context.batch_size)
        else:
            scheduled_result = context.batch_size
        
        # Validation
        validation_result = self.validator.validate_batch_size(
            context.batch_size, 1000000, 1000  # Example model params and memory limit
        )
        
        # Combine recommendations
        recommendations = [adaptive_result[0], performance_result, scheduled_result]
        
        # Weighted average (discrete, so use median of valid recommendations)
        valid_recommendations = [r for r in recommendations if validation_result['is_valid']]
        
        if valid_recommendations:
            final_batch_size = int(np.median(valid_recommendations))
        else:
            final_batch_size = context.batch_size  # Fallback
        
        ensemble_result = {
            'final_batch_size': final_batch_size,
            'adaptive_recommendation': adaptive_result[0],
            'performance_recommendation': performance_result,
            'scheduled_recommendation': scheduled_result,
            'validation_result': validation_result,
            'confidence_scores': self._calculate_ensemble_confidence(context),
            'adaptation_reason': adaptive_result[1].get('adaptation_reason', 'ensemble_decision')
        }
        
        return final_batch_size, ensemble_result
    
    def _calculate_ensemble_confidence(self, context: TrainingContext) -> Dict[str, float]:
        """Ensemble ishonchliligi"""
        
        return {
            'adaptive_confidence': self.adaptive_optimizer._calculate_adaptation_confidence(context),
            'performance_confidence': 0.7,  # Simplified
            'scheduled_confidence': 0.8 if context.current_epoch < 50 else 0.6,
            'validation_confidence': 0.9 if context.data_volatility < 0.1 else 0.6
        }

# Trading-specific batch size optimizer
class TradingBatchSizeOptimizer(AdaptiveBatchSizeOptimizer):
    """Trading uchun maxsus batch size optimallashtiruvchi"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        # Trading-specific thresholds
        self.market_volatility_threshold = 0.1
        self.trade_frequency_threshold = 10
        
    def adapt_for_trading_conditions(self, trading_context: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """Trading shartlari uchun moslashish"""
        
        # Create training context from trading context
        context = TrainingContext(
            current_epoch=trading_context.get('epoch', 0),
            current_loss=trading_context.get('loss', 1.0),
            validation_loss=trading_context.get('val_loss', 1.0),
            learning_rate=trading_context.get('learning_rate', 0.001),
            batch_size=trading_context.get('batch_size', 32),
            data_volatility=trading_context.get('market_volatility', 0.05),
            gradient_norm=trading_context.get('gradient_norm', 0.5),
            training_time=trading_context.get('training_time', 100.0),
            memory_usage=trading_context.get('memory_usage', 0.5)
        )
        
        # Get standard adaptation
        batch_size, adaptation_result = self.adapt_batch_size(context)
        
        # Add trading-specific adjustments
        market_volatility = trading_context.get('market_volatility', 0.05)
        trade_frequency = trading_context.get('trade_frequency', 1)
        
        # High market volatility - more conservative
        if market_volatility > self.market_volatility_threshold:
            batch_size = max(self.batch_config.min_batch_size, batch_size // 2)
            adaptation_result['trading_adjustment'] = 'high_volatility_reduction'
        
        # High trade frequency - larger batches for stability
        elif trade_frequency > self.trade_frequency_threshold:
            batch_size = min(self.batch_config.max_batch_size, batch_size * 2)
            adaptation_result['trading_adjustment'] = 'high_frequency_increase'
        
        # Update adaptation result
        adaptation_result['final_batch_size'] = batch_size
        adaptation_result['trading_context'] = trading_context
        
        return batch_size, adaptation_result

# Demo va test
if __name__ == "__main__":
    # Adaptive batch size optimizer testi
    optimizer = AdaptiveBatchSizeOptimizer()
    
    # Training context simulation
    context = TrainingContext(
        current_epoch=25,
        current_loss=0.75,
        validation_loss=0.78,
        learning_rate=0.001,
        batch_size=32,
        data_volatility=0.08,
        gradient_norm=1.2,
        training_time=120.0,
        memory_usage=0.6
    )
    
    # Batch size adaptation
    new_batch_size, adaptation_result = optimizer.adapt_batch_size(context)
    
    print("=== ADAPTIVE BATCH SIZE OPTIMIZATION ===")
    print(f"Current Batch Size: {context.batch_size}")
    print(f"Adapted Batch Size: {new_batch_size}")
    print(f"Adaptation Reason: {adaptation_result['adaptation_reason']}")
    print(f"Confidence: {adaptation_result['confidence']:.3f}")
    print(f"Performance Adaptation: {adaptation_result['performance_adaptation']}")
    print(f"Volatility Adaptation: {adaptation_result['volatility_adaptation']}")
    
    # Batch schedule generation
    schedule = optimizer.get_optimal_batch_schedule(50)
    print(f"\nBatch Size Schedule (first 10 epochs): {schedule[:10]}")
    
    # Trading-specific optimizer
    trading_optimizer = TradingBatchSizeOptimizer()
    trading_context = {
        'epoch': 30,
        'loss': 0.65,
        'val_loss': 0.67,
        'learning_rate': 0.0005,
        'batch_size': 32,
        'market_volatility': 0.12,  # High volatility
        'gradient_norm': 0.8,
        'trade_frequency': 15
    }
    
    trading_batch_size, trading_result = trading_optimizer.adapt_for_trading_conditions(trading_context)
    
    print(f"\n=== TRADING BATCH SIZE OPTIMIZATION ===")
    print(f"Market Volatility: {trading_context['market_volatility']:.3f}")
    print(f"Trade Frequency: {trading_context['trade_frequency']}")
    print(f"Adapted Batch Size: {trading_batch_size}")
    print(f"Trading Adjustment: {trading_result.get('trading_adjustment', 'none')}")
    
    # Ensemble optimizer
    ensemble_optimizer = BatchSizeOptimizerEnsemble()
    ensemble_batch_size, ensemble_result = ensemble_optimizer.optimize_ensemble(context)
    
    print(f"\n=== ENSEMBLE BATCH SIZE OPTIMIZATION ===")
    print(f"Final Batch Size: {ensemble_batch_size}")
    print(f"Adaptive Recommendation: {ensemble_result['adaptive_recommendation']}")
    print(f"Performance Recommendation: {ensemble_result['performance_recommendation']}")
    print(f"Scheduled Recommendation: {ensemble_result['scheduled_recommendation']}")
    print(f"Validation Passed: {ensemble_result['validation_result']['is_valid']}")
    
    # Schedule examples
    scheduler = ScheduledBatchSizeManager()
    
    # Cosine schedule
    cosine_schedule = scheduler.create_cosine_schedule(20, 16, 128)
    print(f"\nCosine Schedule (first 5): {cosine_schedule[:5]}")
    
    # Step schedule
    step_schedule = scheduler.create_step_schedule(20, [(5, 16), (10, 32), (15, 64)])
    print(f"Step Schedule: {step_schedule}")