"""
Real-Time Model Updates for Self-Learning Trading Fund
====================================================

Model larni real vaqtda yangilash va qayta o'qitish.
Online learning va incremental model updates.
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
import threading
import queue
import time
import pickle
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

from ..core.base_algorithm import BaseAlgorithm
from ..core.adaptive_model import AdaptiveModel
from ..core.performance_tracker import PerformanceTracker

class UpdateStrategy(Enum):
    """Yangilash strategiyasi"""
    BATCH_UPDATE = "Batch_Update"
    INCREMENTAL_UPDATE = "Incremental_Update"
    HYBRID_UPDATE = "Hybrid_Update"
    ADAPTIVE_UPDATE = "Adaptive_Update"
    TRIGGER_BASED = "Trigger_Based"
    SCHEDULED_UPDATE = "Scheduled_Update"

class UpdateTrigger(Enum):
    """Yangilash triggeri"""
    PERFORMANCE_DROP = "Performance_Drop"
    CONCEPT_DRIFT = "Concept_Drift"
    SCHEDULE = "Schedule"
    DATA_ACCUMULATION = "Data_Accumulation"
    ERROR_THRESHOLD = "Error_Threshold"
    MANUAL_TRIGGER = "Manual_Trigger"

class ModelVersion(Enum):
    """Model versiyasi"""
    PRODUCTION = "Production"
    STAGING = "Staging"
    EXPERIMENTAL = "Experimental"
    RETIRED = "Retired"

@dataclass
class ModelUpdate:
    """Model yangilash"""
    model_id: str
    update_id: str
    timestamp: datetime
    update_type: UpdateTrigger
    old_version: ModelVersion
    new_version: ModelVersion
    performance_before: float
    performance_after: float
    training_data_size: int
    update_duration: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ModelState:
    """Model holati"""
    model_id: str
    current_version: ModelVersion
    performance_history: List[float]
    last_update: datetime
    training_data_count: int
    prediction_count: int
    error_rate: float
    is_active: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

class RealTimeModelUpdater(BaseAlgorithm):
    """Real-time model yangilash sistemasi"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        self.config = config or {}
        
        # Model management
        self.models: Dict[str, AdaptiveModel] = {}
        self.model_states: Dict[str, ModelState] = {}
        self.update_history: List[ModelUpdate] = []
        
        # Update scheduling
        self.update_triggers: Dict[UpdateTrigger, Callable] = {
            UpdateTrigger.PERFORMANCE_DROP: self._check_performance_drop,
            UpdateTrigger.CONCEPT_DRIFT: self._check_concept_drift,
            UpdateTrigger.SCHEDULE: self._check_schedule,
            UpdateTrigger.DATA_ACCUMULATION: self._check_data_accumulation,
            UpdateTrigger.ERROR_THRESHOLD: self._check_error_threshold
        }
        
        # Configuration
        self.performance_threshold = self.config.get('performance_threshold', 0.05)
        self.concept_drift_threshold = self.config.get('concept_drift_threshold', 0.1)
        self.update_frequency = self.config.get('update_frequency', 3600)  # seconds
        self.min_data_for_update = self.config.get('min_data_for_update', 100)
        self.max_concurrent_updates = self.config.get('max_concurrent_updates', 2)
        
        # Threading
        self.running = False
        self.update_queue = queue.Queue()
        self.lock = threading.Lock()
        
        # Performance tracking
        self.performance_tracker = PerformanceTracker()
        
    def register_model(self, model: AdaptiveModel, model_id: str) -> bool:
        """Model registratsiya"""
        
        with self.lock:
            self.models[model_id] = model
            
            # Initialize model state
            self.model_states[model_id] = ModelState(
                model_id=model_id,
                current_version=ModelVersion.PRODUCTION,
                performance_history=[],
                last_update=datetime.now(),
                training_data_count=0,
                prediction_count=0,
                error_rate=0.0,
                is_active=True
            )
            
            logging.info(f"Registered model {model_id}")
            return True
    
    def start_real_time_updates(self):
        """Real-time yangilashlarni boshlash"""
        
        if self.running:
            logging.warning("Real-time updates already running")
            return
        
        self.running = True
        
        # Start update scheduler
        scheduler_thread = threading.Thread(target=self._update_scheduler_worker, daemon=True)
        scheduler_thread.start()
        
        # Start update processor
        processor_thread = threading.Thread(target=self._update_processor_worker, daemon=True)
        processor_thread.start()
        
        logging.info("Real-time model updates started")
    
    def stop_real_time_updates(self):
        """Real-time yangilashlarni to'xtatish"""
        
        self.running = False
        logging.info("Real-time model updates stopped")
    
    def trigger_update(self, model_id: str, trigger_type: UpdateTrigger, 
                      data: Optional[Any] = None) -> str:
        """Yangilash trigger qilish"""
        
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not registered")
        
        update_id = f"{model_id}_{trigger_type.value}_{int(time.time())}"
        
        update_request = {
            'model_id': model_id,
            'update_id': update_id,
            'trigger_type': trigger_type,
            'data': data,
            'timestamp': datetime.now()
        }
        
        try:
            self.update_queue.put(update_request, block=False)
            logging.info(f"Update triggered for model {model_id} with trigger {trigger_type.value}")
            return update_id
        except queue.Full:
            logging.error("Update queue is full")
            raise RuntimeError("Update queue is full")
    
    def _update_scheduler_worker(self):
        """Yangilash rejalashtiruvchi worker"""
        
        logging.info("Update scheduler worker started")
        
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check each model for update triggers
                for model_id, model_state in self.model_states.items():
                    if not model_state.is_active:
                        continue
                    
                    # Check each trigger
                    for trigger_type, trigger_func in self.update_triggers.items():
                        try:
                            if trigger_func(model_id, model_state, current_time):
                                self.trigger_update(model_id, trigger_type)
                        except Exception as e:
                            logging.error(f"Error checking trigger {trigger_type.value} for model {model_id}: {str(e)}")
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logging.error(f"Update scheduler error: {str(e)}")
                time.sleep(60)
        
        logging.info("Update scheduler worker stopped")
    
    def _update_processor_worker(self):
        """Yangilash qayta ishlagichi worker"""
        
        logging.info("Update processor worker started")
        
        while self.running:
            try:
                # Get update request
                try:
                    update_request = self.update_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process update
                update_result = self._process_model_update(update_request)
                
                # Update history
                with self.lock:
                    self.update_history.append(update_result)
                
                # Clean old history
                if len(self.update_history) > 1000:
                    self.update_history = self.update_history[-500:]
                
            except Exception as e:
                logging.error(f"Update processor error: {str(e)}")
        
        logging.info("Update processor worker stopped")
    
    def _process_model_update(self, update_request: Dict[str, Any]) -> ModelUpdate:
        """Model yangilashni qayta ishlash"""
        
        model_id = update_request['model_id']
        trigger_type = update_request['trigger_type']
        update_id = update_request['update_id']
        start_time = time.time()
        
        # Get current model state
        model_state = self.model_states[model_id]
        model = self.models[model_id]
        
        # Record update start
        old_version = model_state.current_version
        performance_before = model_state.performance_history[-1] if model_state.performance_history else 0.0
        
        update_result = ModelUpdate(
            model_id=model_id,
            update_id=update_id,
            timestamp=datetime.now(),
            update_type=trigger_type,
            old_version=old_version,
            new_version=ModelVersion.STAGING,  # Will be updated after successful update
            performance_before=performance_before,
            performance_after=0.0,
            training_data_size=0,
            update_duration=0.0,
            success=False
        )
        
        try:
            # Prepare training data
            training_data = self._prepare_training_data(model_id, update_request.get('data'))
            update_result.training_data_size = len(training_data) if training_data else 0
            
            # Perform update based on strategy
            update_strategy = self._select_update_strategy(trigger_type, model_state)
            performance_after = self._execute_update(model, update_strategy, training_data)
            
            # Validate update
            if self._validate_update(model, performance_before, performance_after):
                # Promote to production
                model_state.current_version = ModelVersion.PRODUCTION
                update_result.new_version = ModelVersion.PRODUCTION
                update_result.success = True
                
                # Update model state
                model_state.performance_history.append(performance_after)
                model_state.last_update = datetime.now()
                model_state.training_data_count += update_result.training_data_size
                
                # Keep performance history bounded
                if len(model_state.performance_history) > 100:
                    model_state.performance_history = model_state.performance_history[-50:]
            else:
                # Rollback - keep old version
                update_result.new_version = old_version
                update_result.success = False
                update_result.error_message = "Update validation failed"
            
            update_result.performance_after = performance_after
            
        except Exception as e:
            update_result.success = False
            update_result.error_message = str(e)
            logging.error(f"Model update failed for {model_id}: {str(e)}")
        
        update_result.update_duration = time.time() - start_time
        
        return update_result
    
    def _prepare_training_data(self, model_id: str, additional_data: Any) -> Any:
        """Training ma'lumotlarini tayyorlash"""
        
        # Get recent data for the model
        # In real implementation, would fetch from data storage
        
        # Simulate training data preparation
        if additional_data is not None:
            # Use provided data
            return additional_data
        else:
            # Generate synthetic training data
            X = np.random.randn(100, 10)
            y = np.random.randint(0, 2, 100)
            return (X, y)
    
    def _select_update_strategy(self, trigger_type: UpdateTrigger, 
                              model_state: ModelState) -> UpdateStrategy:
        """Yangilash strategiyasini tanlash"""
        
        if trigger_type == UpdateTrigger.PERFORMANCE_DROP:
            return UpdateStrategy.BATCH_UPDATE
        elif trigger_type == UpdateTrigger.CONCEPT_DRIFT:
            return UpdateStrategy.ADAPTIVE_UPDATE
        elif trigger_type == UpdateTrigger.SCHEDULE:
            return UpdateStrategy.INCREMENTAL_UPDATE
        elif trigger_type == UpdateTrigger.DATA_ACCUMULATION:
            return UpdateStrategy.HYBRID_UPDATE
        else:
            return UpdateStrategy.INCREMENTAL_UPDATE
    
    def _execute_update(self, model: AdaptiveModel, strategy: UpdateStrategy, 
                      training_data: Any) -> float:
        """Yangilashni bajarish"""
        
        if strategy == UpdateStrategy.BATCH_UPDATE:
            return self._batch_update(model, training_data)
        elif strategy == UpdateStrategy.INCREMENTAL_UPDATE:
            return self._incremental_update(model, training_data)
        elif strategy == UpdateStrategy.ADAPTIVE_UPDATE:
            return self._adaptive_update(model, training_data)
        elif strategy == UpdateStrategy.HYBRID_UPDATE:
            return self._hybrid_update(model, training_data)
        else:
            return self._incremental_update(model, training_data)
    
    def _batch_update(self, model: AdaptiveModel, training_data: Any) -> float:
        """Batch yangilash"""
        
        # Simulate batch training
        X, y = training_data
        
        # Simulate training process
        time.sleep(0.1)  # Simulate training time
        
        # Simulate performance calculation
        performance = 0.75 + np.random.uniform(-0.1, 0.15)
        
        # Update model (simulated)
        if hasattr(model, 'fit'):
            model.fit(X, y)
        
        return min(1.0, max(0.0, performance))
    
    def _incremental_update(self, model: AdaptiveModel, training_data: Any) -> float:
        """Incrementall yangilash"""
        
        # Simulate incremental learning
        X, y = training_data
        
        # Smaller update
        time.sleep(0.05)
        
        performance = 0.8 + np.random.uniform(-0.05, 0.1)
        
        # Incremental update (simulated)
        if hasattr(model, 'partial_fit'):
            model.partial_fit(X, y)
        
        return min(1.0, max(0.0, performance))
    
    def _adaptive_update(self, model: AdaptiveModel, training_data: Any) -> float:
        """Adaptiv yangilash"""
        
        # More sophisticated update based on data characteristics
        X, y = training_data
        
        # Analyze data distribution
        class_distribution = np.bincount(y) / len(y)
        data_drift_score = np.std(class_distribution)
        
        # Adaptive strategy selection
        if data_drift_score > 0.3:
            # High drift - use batch update
            return self._batch_update(model, training_data)
        else:
            # Low drift - use incremental
            return self._incremental_update(model, training_data)
    
    def _hybrid_update(self, model: AdaptiveModel, training_data: Any) -> float:
        """Gibrid yangilash"""
        
        # Combine incremental and batch approaches
        X, y = training_data
        
        # First incremental update
        perf1 = self._incremental_update(model, training_data)
        
        # Then batch update with subset
        subset_size = min(len(X) // 2, 50)
        subset_data = (X[:subset_size], y[:subset_size])
        perf2 = self._batch_update(model, subset_data)
        
        # Combine performances
        return (perf1 + perf2) / 2
    
    def _validate_update(self, model: AdaptiveModel, performance_before: float, 
                        performance_after: float) -> bool:
        """Yangilanishni validatsiya qilish"""
        
        # Check if performance improved or stayed within threshold
        performance_improvement = performance_after - performance_before
        
        # Validation criteria
        if performance_improvement >= -self.performance_threshold:
            # Performance not significantly worse
            return True
        
        # Additional checks
        if performance_after < 0.3:  # Performance too low
            return False
        
        return True
    
    # Trigger checking methods
    def _check_performance_drop(self, model_id: str, model_state: ModelState, 
                               current_time: datetime) -> bool:
        """Performance pasayishini tekshirish"""
        
        if len(model_state.performance_history) < 5:
            return False
        
        recent_performance = np.mean(model_state.performance_history[-5:])
        historical_average = np.mean(model_state.performance_history[:-5])
        
        # Check for significant performance drop
        performance_drop = (historical_average - recent_performance) / historical_average
        
        return performance_drop > self.performance_threshold
    
    def _check_concept_drift(self, model_id: str, model_state: ModelState,
                           current_time: datetime) -> bool:
        """Concept drift ni tekshirish"""
        
        # Simplified concept drift detection
        # In real implementation, would use statistical tests
        
        if len(model_state.performance_history) < 10:
            return False
        
        # Compare recent vs older performance variance
        recent_perf = model_state.performance_history[-5:]
        older_perf = model_state.performance_history[-10:-5]
        
        recent_variance = np.var(recent_perf)
        older_variance = np.var(older_perf)
        
        # High variance increase indicates drift
        variance_ratio = recent_variance / max(older_variance, 0.01)
        
        return variance_ratio > (1 + self.concept_drift_threshold)
    
    def _check_schedule(self, model_id: str, model_state: ModelState,
                      current_time: datetime) -> bool:
        """Reja bo'yicha yangilanishni tekshirish"""
        
        time_since_update = (current_time - model_state.last_update).total_seconds()
        
        return time_since_update >= self.update_frequency
    
    def _check_data_accumulation(self, model_id: str, model_state: ModelState,
                               current_time: datetime) -> bool:
        """Ma'lumot to'planishini tekshirish"""
        
        # Check if enough new data has been accumulated
        return model_state.training_data_count >= self.min_data_for_update
    
    def _check_error_threshold(self, model_id: str, model_state: ModelState,
                             current_time: datetime) -> bool:
        """Xato threshold ni tekshirish"""
        
        return model_state.error_rate > 0.1  # 10% error threshold
    
    def predict_with_update_tracking(self, model_id: str, X: Any) -> Tuple[Any, Dict[str, Any]]:
        """Yangilashni kuzatib borib prediction qilish"""
        
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not registered")
        
        model = self.models[model_id]
        model_state = self.model_states[model_id]
        
        try:
            # Make prediction
            if hasattr(model, 'predict'):
                prediction = model.predict(X)
            else:
                # Simulate prediction
                prediction = np.random.randint(0, 2, len(X) if hasattr(X, '__len__') else 1)
            
            # Update prediction count
            model_state.prediction_count += 1
            
            # Track prediction for error monitoring
            prediction_metadata = {
                'model_id': model_id,
                'prediction_time': datetime.now(),
                'model_version': model_state.current_version.value,
                'prediction_count': model_state.prediction_count
            }
            
            return prediction, prediction_metadata
        
        except Exception as e:
            # Update error rate
            model_state.error_rate = (model_state.error_rate * 0.9) + (1 * 0.1)
            raise e
    
    def get_model_update_history(self, model_id: str, limit: int = 10) -> List[ModelUpdate]:
        """Model yangilanish tarixini olish"""
        
        model_updates = [update for update in self.update_history 
                        if update.model_id == model_id]
        
        return sorted(model_updates, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_updater_summary(self) -> Dict[str, Any]:
        """Updater xulosasini olish"""
        
        total_updates = len(self.update_history)
        successful_updates = len([u for u in self.update_history if u.success])
        
        # Model statistics
        model_stats = {}
        for model_id, model_state in self.model_states.items():
            model_stats[model_id] = {
                'version': model_state.current_version.value,
                'is_active': model_state.is_active,
                'last_update': model_state.last_update.isoformat(),
                'prediction_count': model_state.prediction_count,
                'error_rate': model_state.error_rate,
                'recent_performance': model_state.performance_history[-3:] if model_state.performance_history else []
            }
        
        return {
            'total_models': len(self.models),
            'total_updates': total_updates,
            'successful_updates': successful_updates,
            'success_rate': successful_updates / max(total_updates, 1),
            'running': self.running,
            'model_statistics': model_stats,
            'queue_size': self.update_queue.qsize(),
            'recent_updates': [
                {
                    'model_id': update.model_id,
                    'trigger': update.update_type.value,
                    'success': update.success,
                    'timestamp': update.timestamp.isoformat(),
                    'duration': update.update_duration
                }
                for update in self.update_history[-5:]
            ]
        }

class ModelUpdateValidator:
    """Model yangilash validatori"""
    
    def __init__(self):
        self.validation_rules = {
            'performance_threshold': 0.05,
            'minimum_training_samples': 50,
            'maximum_training_time': 300,  # 5 minutes
            'error_rate_threshold': 0.15
        }
    
    def validate_update(self, old_model: Any, new_model: Any,
                      training_data: Any, validation_data: Any) -> Dict[str, Any]:
        """Yangilanishni validatsiya qilish"""
        
        validation_result = {
            'valid': True,
            'checks_passed': 0,
            'total_checks': 0,
            'issues': [],
            'warnings': []
        }
        
        # Performance validation
        if not self._validate_performance(old_model, new_model, validation_data):
            validation_result['issues'].append('Performance validation failed')
            validation_result['valid'] = False
        
        validation_result['total_checks'] += 1
        if 'Performance validation failed' not in validation_result['issues']:
            validation_result['checks_passed'] += 1
        
        # Training data validation
        if not self._validate_training_data(training_data):
            validation_result['issues'].append('Training data validation failed')
            validation_result['valid'] = False
        
        validation_result['total_checks'] += 1
        if 'Training data validation failed' not in validation_result['issues']:
            validation_result['checks_passed'] += 1
        
        # Stability validation
        if not self._validate_stability(new_model, validation_data):
            validation_result['warnings'].append('Model stability could be improved')
        
        validation_result['total_checks'] += 1
        if 'Model stability could be improved' not in validation_result['warnings']:
            validation_result['checks_passed'] += 1
        
        return validation_result
    
    def _validate_performance(self, old_model: Any, new_model: Any, validation_data: Any) -> bool:
        """Performance validatsiya"""
        
        # Simplified performance comparison
        # In real implementation, would evaluate both models on validation set
        
        # Simulate evaluation
        old_performance = np.random.uniform(0.6, 0.8)
        new_performance = np.random.uniform(0.65, 0.85)
        
        performance_improvement = new_performance - old_performance
        
        return performance_improvement >= -self.validation_rules['performance_threshold']
    
    def _validate_training_data(self, training_data: Any) -> bool:
        """Training data validatsiya"""
        
        if training_data is None:
            return False
        
        # Check data size
        if isinstance(training_data, tuple):
            X, y = training_data
            if len(X) < self.validation_rules['minimum_training_samples']:
                return False
        
        return True
    
    def _validate_stability(self, model: Any, validation_data: Any) -> bool:
        """Model barqarorlik validatsiya"""
        
        # Simplified stability check
        # In real implementation, would test model consistency
        
        stability_score = np.random.uniform(0.7, 0.95)
        
        return stability_score > 0.6

class UpdateRollbackManager:
    """Yangilashni qayta tiklash boshqaruvchisi"""
    
    def __init__(self):
        self.model_snapshots = {}
        self.rollback_history = deque(maxlen=100)
    
    def create_snapshot(self, model_id: str, model: Any, version: str) -> bool:
        """Model snapshot yaratish"""
        
        try:
            # Serialize model for backup
            serialized_model = pickle.dumps(model)
            snapshot_hash = hashlib.md5(serialized_model).hexdigest()
            
            self.model_snapshots[f"{model_id}_{version}"] = {
                'model': serialized_model,
                'timestamp': datetime.now(),
                'version': version,
                'hash': snapshot_hash
            }
            
            logging.info(f"Created snapshot for model {model_id} version {version}")
            return True
        
        except Exception as e:
            logging.error(f"Failed to create snapshot: {str(e)}")
            return False
    
    def rollback_model(self, model_id: str, target_version: str) -> Tuple[bool, Any]:
        """Model ni qayta tiklash"""
        
        snapshot_key = f"{model_id}_{target_version}"
        
        if snapshot_key not in self.model_snapshots:
            return False, None
        
        try:
            # Restore from snapshot
            snapshot = self.model_snapshots[snapshot_key]
            model = pickle.loads(snapshot['model'])
            
            # Record rollback
            self.rollback_history.append({
                'model_id': model_id,
                'target_version': target_version,
                'timestamp': datetime.now(),
                'success': True
            })
            
            logging.info(f"Successfully rolled back model {model_id} to version {target_version}")
            return True, model
        
        except Exception as e:
            # Record failed rollback
            self.rollback_history.append({
                'model_id': model_id,
                'target_version': target_version,
                'timestamp': datetime.now(),
                'success': False,
                'error': str(e)
            })
            
            logging.error(f"Failed to rollback model {model_id}: {str(e)}")
            return False, None
    
    def get_rollback_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Qayta tiklash tarixini olish"""
        
        return list(self.rollback_history)[-limit:]

# Demo va test
if __name__ == "__main__":
    # Real-time model updater testi
    updater = RealTimeModelUpdater({
        'performance_threshold': 0.1,
        'concept_drift_threshold': 0.15,
        'update_frequency': 300,  # 5 minutes
        'min_data_for_update': 50
    })
    
    print("=== REAL-TIME MODEL UPDATER TEST ===")
    
    # Create mock models
    class MockAdaptiveModel:
        def __init__(self, model_type="neural_network"):
            self.model_type = model_type
            self.trained = False
        
        def fit(self, X, y):
            self.trained = True
            time.sleep(0.1)  # Simulate training
            return self
        
        def predict(self, X):
            return np.random.randint(0, 2, len(X) if hasattr(X, '__len__') else 1)
        
        def partial_fit(self, X, y):
            self.trained = True
            time.sleep(0.05)  # Simulate incremental training
            return self
    
    # Register models
    model1 = MockAdaptiveModel("neural_network")
    model2 = MockAdaptiveModel("random_forest")
    
    model1_id = updater.register_model(model1, "model1")
    model2_id = updater.register_model(model2, "model2")
    
    print(f"Registered models: {model1_id}, {model2_id}")
    
    # Start real-time updates
    updater.start_real_time_updates()
    
    try:
        # Test predictions
        test_data = np.random.randn(10, 5)
        
        for i in range(5):
            prediction1, metadata1 = updater.predict_with_update_tracking(model1_id, test_data)
            prediction2, metadata2 = updater.predict_with_update_tracking(model2_id, test_data)
            
            if i % 2 == 0:
                print(f"Predictions {i+1}: Model1={prediction1[:3]}, Model2={prediction2[:3]}")
        
        # Trigger manual updates
        print("\nTriggering manual updates...")
        
        trigger1_id = updater.trigger_update(model1_id, UpdateTrigger.MANUAL_TRIGGER)
        trigger2_id = updater.trigger_update(model2_id, UpdateTrigger.PERFORMANCE_DROP)
        
        print(f"Update triggers: {trigger1_id}, {trigger2_id}")
        
        # Wait for updates to process
        time.sleep(2)
        
        # Test rollback functionality
        rollback_manager = UpdateRollbackManager()
        
        # Create snapshots
        rollback_manager.create_snapshot(model1_id, model1, "v1.0")
        rollback_manager.create_snapshot(model2_id, model2, "v1.0")
        
        # Test rollback
        rollback_success, rolled_back_model = rollback_manager.rollback_model(model1_id, "v1.0")
        print(f"Rollback success: {rollback_success}")
        
        # Get updater summary
        summary = updater.get_updater_summary()
        
        print(f"\n=== UPDATER SUMMARY ===")
        print(f"Total models: {summary['total_models']}")
        print(f"Total updates: {summary['total_updates']}")
        print(f"Success rate: {summary['success_rate']:.2%}")
        print(f"Running: {summary['running']}")
        print(f"Queue size: {summary['queue_size']}")
        
        # Show model statistics
        for model_id, stats in summary['model_statistics'].items():
            print(f"\nModel {model_id}:")
            print(f"  Version: {stats['version']}")
            print(f"  Predictions: {stats['prediction_count']}")
            print(f"  Error rate: {stats['error_rate']:.3f}")
            print(f"  Last update: {stats['last_update']}")
        
        # Test model update history
        history1 = updater.get_model_update_history(model1_id, 5)
        print(f"\nModel 1 update history: {len(history1)} updates")
        
        if history1:
            latest_update = history1[0]
            print(f"Latest update: {latest_update.update_type.value}, Success: {latest_update.success}")
        
    finally:
        updater.stop_real_time_updates()
    
    # Test update validator
    validator = ModelUpdateValidator()
    validation_result = validator.validate_update(model1, model2, (np.random.randn(100, 5), np.random.randint(0, 2, 100)), (np.random.randn(20, 5), np.random.randint(0, 2, 20)))
    
    print(f"\n=== VALIDATION RESULT ===")
    print(f"Valid: {validation_result['valid']}")
    print(f"Checks passed: {validation_result['checks_passed']}/{validation_result['total_checks']}")
    print(f"Issues: {validation_result['issues']}")
    print(f"Warnings: {validation_result['warnings']}")
    
    print("\n=== REAL-TIME UPDATER TEST COMPLETED ===")