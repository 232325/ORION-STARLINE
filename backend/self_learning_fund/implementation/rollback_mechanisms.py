"""
Rollback Mechanisms for Self-Learning Trading Fund
=================================================

Model va strategiya rollback tizimi.
Xavfsiz rollback, versioning va recovery mechanisms.
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
import json
import pickle
import hashlib
import shutil
import os
from pathlib import Path
import sqlite3

from ..core.base_algorithm import BaseAlgorithm
from ..core.adaptive_model import AdaptiveModel
from ..core.performance_tracker import PerformanceTracker

class RollbackType(Enum):
    """Rollback turlari"""
    MODEL_ROLLBACK = "Model_Rollback"
    STRATEGY_ROLLBACK = "Strategy_Rollback"
    PARAMETER_ROLLBACK = "Parameter_Rollback"
    FULL_SYSTEM_ROLLBACK = "Full_System_Rollback"
    DATA_ROLLBACK = "Data_Rollback"
    CONFIGURATION_ROLLBACK = "Configuration_Rollback"

class RollbackStatus(Enum):
    """Rollback holati"""
    INITIATED = "Initiated"
    IN_PROGRESS = "In_Progress"
    SUCCESS = "Success"
    FAILED = "Failed"
    PARTIAL = "Partial"
    ROLLBACK = "Rollback"

class RollbackTrigger(Enum):
    """Rollback triggeri"""
    MANUAL = "Manual"
    PERFORMANCE_DEGRADATION = "Performance_Degradation"
    ERROR_THRESHOLD = "Error_Threshold"
    VALIDATION_FAILED = "Validation_Failed"
    SYSTEM_FAILURE = "System_Failure"
    SCHEDULED = "Scheduled"
    EMERGENCY = "Emergency"

class VersionStatus(Enum):
    """Versiya holati"""
    ACTIVE = "Active"
    STABLE = "Stable"
    TESTING = "Testing"
    DEPRECATED = "Deprecated"
    CORRUPTED = "Corrupted"

@dataclass
class ModelVersion:
    """Model versiyasi"""
    version_id: str
    model_id: str
    created_at: datetime
    model_data: bytes
    metadata: Dict[str, Any]
    checksum: str
    status: VersionStatus = VersionStatus.ACTIVE
    parent_version: Optional[str] = None
    size_bytes: int = 0

@dataclass
class RollbackOperation:
    """Rollback operatsiyasi"""
    operation_id: str
    rollback_type: RollbackType
    trigger: RollbackTrigger
    source_version: str
    target_version: str
    status: RollbackStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    affected_components: List[str] = field(default_factory=list)

@dataclass
class RollbackConfiguration:
    """Rollback konfiguratsiyasi"""
    max_versions_to_keep: int = 10
    auto_rollback_enabled: bool = True
    validation_required: bool = True
    backup_before_rollback: bool = True
    rollback_timeout_seconds: int = 300
    performance_threshold_degradation: float = 0.1
    error_rate_threshold: float = 0.05

@dataclass
class ValidationResult:
    """Validatsiya natijasi"""
    component_name: str
    validation_passed: bool
    checks_performed: List[str]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)

class RollbackManager(BaseAlgorithm):
    """Rollback boshqaruvchi"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        self.config = config or {}
        
        # Configuration
        self.rollback_config = RollbackConfiguration(
            max_versions_to_keep=self.config.get('max_versions_to_keep', 10),
            auto_rollback_enabled=self.config.get('auto_rollback_enabled', True),
            validation_required=self.config.get('validation_required', True),
            backup_before_rollback=self.config.get('backup_before_rollback', True),
            rollback_timeout_seconds=self.config.get('rollback_timeout_seconds', 300),
            performance_threshold_degradation=self.config.get('performance_threshold_degradation', 0.1),
            error_rate_threshold=self.config.get('error_rate_threshold', 0.05)
        )
        
        # Version management
        self.model_versions: Dict[str, List[ModelVersion]] = defaultdict(list)
        self.current_versions: Dict[str, str] = {}
        
        # Rollback operations
        self.rollback_operations: Dict[str, RollbackOperation] = {}
        self.operation_history: List[RollbackOperation] = []
        
        # Storage
        self.storage_path = Path(self.config.get('storage_path', './rollback_storage'))
        self.storage_path.mkdir(exist_ok=True)
        
        self.metadata_db = self.storage_path / 'metadata.db'
        self._init_metadata_db()
        
        # Performance tracking
        self.performance_tracker = PerformanceTracker()
        
        # Threading
        self.lock = threading.Lock()
        
    def _init_metadata_db(self):
        """Metadata database ni boshlash"""
        
        conn = sqlite3.connect(str(self.metadata_db))
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_versions (
                version_id TEXT PRIMARY KEY,
                model_id TEXT,
                created_at TIMESTAMP,
                file_path TEXT,
                checksum TEXT,
                status TEXT,
                parent_version TEXT,
                size_bytes INTEGER,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rollback_operations (
                operation_id TEXT PRIMARY KEY,
                rollback_type TEXT,
                trigger TEXT,
                source_version TEXT,
                target_version TEXT,
                status TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_model_version(self, model_id: str, model_data: Any,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """Model versiyasini yaratish"""
        
        version_id = f"{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{int(time.time())}"
        
        # Serialize model data
        serialized_data = pickle.dumps(model_data)
        checksum = hashlib.sha256(serialized_data).hexdigest()
        
        # Store model file
        model_file_path = self.storage_path / f"{version_id}.pkl"
        with open(model_file_path, 'wb') as f:
            f.write(serialized_data)
        
        # Create version record
        model_version = ModelVersion(
            version_id=version_id,
            model_id=model_id,
            created_at=datetime.now(),
            model_data=serialized_data,
            metadata=metadata or {},
            checksum=checksum,
            size_bytes=len(serialized_data)
        )
        
        # Store version
        with self.lock:
            self.model_versions[model_id].append(model_version)
            self.current_versions[model_id] = version_id
            
            # Clean old versions
            self._cleanup_old_versions(model_id)
        
        # Update database
        self._update_metadata_db(model_version)
        
        logging.info(f"Created model version {version_id} for model {model_id}")
        
        return version_id
    
    def initiate_rollback(self, model_id: str, target_version: str,
                         trigger: RollbackTrigger = RollbackTrigger.MANUAL,
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """Rollback boshlash"""
        
        if model_id not in self.model_versions:
            raise ValueError(f"Model {model_id} not found")
        
        # Find target version
        target_version_obj = None
        for version in self.model_versions[model_id]:
            if version.version_id == target_version:
                target_version_obj = version
                break
        
        if not target_version_obj:
            raise ValueError(f"Target version {target_version} not found")
        
        # Create rollback operation
        operation_id = f"rollback_{int(time.time())}_{model_id}"
        source_version = self.current_versions[model_id]
        
        operation = RollbackOperation(
            operation_id=operation_id,
            rollback_type=RollbackType.MODEL_ROLLBACK,
            trigger=trigger,
            source_version=source_version,
            target_version=target_version,
            status=RollbackStatus.INITIATED,
            started_at=datetime.now(),
            metadata=metadata or {}
        )
        
        # Store operation
        with self.lock:
            self.rollback_operations[operation_id] = operation
        
        # Start rollback in background thread
        rollback_thread = threading.Thread(
            target=self._execute_rollback,
            args=(operation, model_id, target_version_obj),
            daemon=True
        )
        rollback_thread.start()
        
        logging.info(f"Initiated rollback operation {operation_id} for model {model_id} to version {target_version}")
        
        return operation_id
    
    def _execute_rollback(self, operation: RollbackOperation, 
                         model_id: str, target_version: ModelVersion):
        """Rollback operatsiyasini bajarish"""
        
        operation.status = RollbackStatus.IN_PROGRESS
        
        try:
            # Create backup if enabled
            if self.rollback_config.backup_before_rollback:
                backup_id = self._create_backup(operation.source_version, model_id)
                operation.metadata['backup_id'] = backup_id
            
            # Validate target version
            if self.rollback_config.validation_required:
                validation_result = self._validate_version(target_version)
                if not validation_result.validation_passed:
                    raise ValueError(f"Target version validation failed: {validation_result.errors}")
                operation.metadata['validation_result'] = validation_result.__dict__
            
            # Load target model
            target_model = self._load_model_version(target_version)
            
            # Perform rollback
            self._perform_rollback(operation, model_id, target_model)
            
            # Verify rollback
            verification_result = self._verify_rollback(operation, model_id)
            
            if verification_result:
                operation.status = RollbackStatus.SUCCESS
                logging.info(f"Rollback operation {operation.operation_id} completed successfully")
            else:
                operation.status = RollbackStatus.FAILED
                operation.error_message = "Rollback verification failed"
                logging.error(f"Rollback operation {operation.operation_id} verification failed")
            
        except Exception as e:
            operation.status = RollbackStatus.FAILED
            operation.error_message = str(e)
            logging.error(f"Rollback operation {operation.operation_id} failed: {str(e)}")
            
            # Attempt automatic recovery if it's an emergency
            if operation.trigger == RollbackTrigger.EMERGENCY:
                self._attempt_emergency_recovery(operation, model_id)
        
        operation.completed_at = datetime.now()
        
        # Move to history
        with self.lock:
            self.operation_history.append(operation)
            del self.rollback_operations[operation.operation_id]
    
    def _create_backup(self, version_id: str, model_id: str) -> str:
        """Backup yaratish"""
        
        backup_id = f"backup_{version_id}_{int(time.time())}"
        backup_path = self.storage_path / f"{backup_id}.pkl"
        
        # Find and copy the current version
        for version in self.model_versions[model_id]:
            if version.version_id == version_id:
                with open(backup_path, 'wb') as f:
                    f.write(version.model_data)
                break
        
        logging.info(f"Created backup {backup_id}")
        return backup_id
    
    def _validate_version(self, version: ModelVersion) -> ValidationResult:
        """Versiyani validatsiya qilish"""
        
        result = ValidationResult(
            component_name=version.version_id,
            validation_passed=True,
            checks_performed=[]
        )
        
        # File integrity check
        try:
            # Verify checksum
            calculated_checksum = hashlib.sha256(version.model_data).hexdigest()
            if calculated_checksum != version.checksum:
                result.validation_passed = False
                result.errors.append("Checksum mismatch")
            result.checks_performed.append("checksum_validation")
        except Exception as e:
            result.validation_passed = False
            result.errors.append(f"Checksum validation failed: {str(e)}")
        
        # File size check
        if version.size_bytes == 0:
            result.validation_passed = False
            result.errors.append("Empty model file")
        result.checks_performed.append("file_size_check")
        
        # Model loading test
        try:
            test_model = pickle.loads(version.model_data)
            result.checks_performed.append("model_loading_test")
        except Exception as e:
            result.validation_passed = False
            result.errors.append(f"Model loading failed: {str(e)}")
        
        # Version status check
        if version.status == VersionStatus.CORRUPTED:
            result.validation_passed = False
            result.errors.append("Version marked as corrupted")
        result.checks_performed.append("status_check")
        
        return result
    
    def _load_model_version(self, version: ModelVersion) -> Any:
        """Model versiyasini yuklash"""
        
        try:
            return pickle.loads(version.model_data)
        except Exception as e:
            raise ValueError(f"Failed to load model version {version.version_id}: {str(e)}")
    
    def _perform_rollback(self, operation: RollbackOperation, 
                         model_id: str, target_model: Any):
        """Rollback operatsiyasini bajarish"""
        
        # Update current version
        self.current_versions[model_id] = operation.target_version
        
        # Update version status
        for version in self.model_versions[model_id]:
            version.status = VersionStatus.DEPRECATED
        
        target_version_obj = None
        for version in self.model_versions[model_id]:
            if version.version_id == operation.target_version:
                version.status = VersionStatus.ACTIVE
                target_version_obj = version
                break
        
        operation.affected_components.append(model_id)
        
        logging.info(f"Rolled back model {model_id} to version {operation.target_version}")
    
    def _verify_rollback(self, operation: RollbackOperation, model_id: str) -> bool:
        """Rollback ni verifikatsiya qilish"""
        
        try:
            # Check if current version matches target
            current_version = self.current_versions[model_id]
            if current_version != operation.target_version:
                return False
            
            # Verify model can be loaded and used
            for version in self.model_versions[model_id]:
                if version.version_id == current_version:
                    test_model = pickle.loads(version.model_data)
                    break
            else:
                return False
            
            # Basic functionality test
            if hasattr(test_model, 'predict'):
                # Test prediction functionality
                test_input = np.random.randn(1, 5)
                try:
                    prediction = test_model.predict(test_input)
                    return True
                except Exception:
                    return False
            else:
                return True  # No prediction method, consider successful
        
        except Exception as e:
            logging.error(f"Rollback verification failed: {str(e)}")
            return False
    
    def _attempt_emergency_recovery(self, operation: RollbackOperation, model_id: str):
        """Favqulodda recovery urinish"""
        
        try:
            # Find the most recent stable version
            stable_versions = [
                v for v in self.model_versions[model_id]
                if v.status == VersionStatus.STABLE
            ]
            
            if stable_versions:
                latest_stable = max(stable_versions, key=lambda x: x.created_at)
                
                # Attempt to rollback to stable version
                logging.info(f"Attempting emergency recovery to stable version {latest_stable.version_id}")
                
                recovery_model = self._load_model_version(latest_stable)
                self._perform_rollback(operation, model_id, recovery_model)
                
                operation.metadata['emergency_recovery'] = True
                operation.metadata['recovery_version'] = latest_stable.version_id
                
                logging.info(f"Emergency recovery successful to version {latest_stable.version_id}")
        
        except Exception as e:
            logging.error(f"Emergency recovery failed: {str(e)}")
            operation.metadata['emergency_recovery_failed'] = str(e)
    
    def _cleanup_old_versions(self, model_id: str):
        """Eski versiyalarni tozalash"""
        
        versions = self.model_versions[model_id]
        
        if len(versions) <= self.rollback_config.max_versions_to_keep:
            return
        
        # Sort by creation date (keep newest)
        versions.sort(key=lambda x: x.created_at, reverse=True)
        
        # Mark old versions as deprecated
        versions_to_mark = versions[self.rollback_config.max_versions_to_keep:]
        for version in versions_to_mark:
            version.status = VersionStatus.DEPRECATED
        
        # Optionally delete old files to save space
        if self.config.get('auto_delete_old_versions', False):
            for version in versions_to_mark:
                try:
                    version_file = self.storage_path / f"{version.version_id}.pkl"
                    if version_file.exists():
                        version_file.unlink()
                except Exception as e:
                    logging.warning(f"Failed to delete old version file {version.version_id}: {str(e)}")
    
    def _update_metadata_db(self, version: ModelVersion):
        """Metadata database ni yangilash"""
        
        conn = sqlite3.connect(str(self.metadata_db))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO model_versions
            (version_id, model_id, created_at, file_path, checksum, status, 
             parent_version, size_bytes, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            version.version_id,
            version.model_id,
            version.created_at.isoformat(),
            str(self.storage_path / f"{version.version_id}.pkl"),
            version.checksum,
            version.status.value,
            version.parent_version,
            version.size_bytes,
            json.dumps(version.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def get_rollback_status(self, operation_id: str) -> Dict[str, Any]:
        """Rollback status olish"""
        
        if operation_id in self.rollback_operations:
            operation = self.rollback_operations[operation_id]
        elif operation_id in [op.operation_id for op in self.operation_history]:
            operation = next(op for op in self.operation_history if op.operation_id == operation_id)
        else:
            raise ValueError(f"Rollback operation {operation_id} not found")
        
        return {
            'operation_id': operation.operation_id,
            'rollback_type': operation.rollback_type.value,
            'trigger': operation.trigger.value,
            'source_version': operation.source_version,
            'target_version': operation.target_version,
            'status': operation.status.value,
            'started_at': operation.started_at.isoformat(),
            'completed_at': operation.completed_at.isoformat() if operation.completed_at else None,
            'duration_seconds': (
                (operation.completed_at - operation.started_at).total_seconds() 
                if operation.completed_at else None
            ),
            'error_message': operation.error_message,
            'metadata': operation.metadata,
            'affected_components': operation.affected_components
        }
    
    def get_model_versions(self, model_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Model versiyalarini olish"""
        
        if model_id not in self.model_versions:
            return []
        
        versions = sorted(self.model_versions[model_id], key=lambda x: x.created_at, reverse=True)
        
        return [
            {
                'version_id': version.version_id,
                'created_at': version.created_at.isoformat(),
                'status': version.status.value,
                'size_bytes': version.size_bytes,
                'checksum': version.checksum,
                'is_current': version.version_id == self.current_versions.get(model_id),
                'metadata': version.metadata
            }
            for version in versions[:limit]
        ]
    
    def get_rollback_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Rollback tarixini olish"""
        
        return [
            {
                'operation_id': op.operation_id,
                'rollback_type': op.rollback_type.value,
                'trigger': op.trigger.value,
                'status': op.status.value,
                'started_at': op.started_at.isoformat(),
                'completed_at': op.completed_at.isoformat() if op.completed_at else None,
                'source_version': op.source_version,
                'target_version': op.target_version,
                'affected_components': op.affected_components
            }
            for op in sorted(self.operation_history, key=lambda x: x.started_at, reverse=True)[:limit]
        ]
    
    def auto_rollback_check(self, model_id: str, 
                          performance_metrics: Dict[str, float]) -> Optional[str]:
        """Avtomatik rollback tekshirish"""
        
        if not self.rollback_config.auto_rollback_enabled:
            return None
        
        # Check performance degradation
        if 'current_performance' in performance_metrics and 'baseline_performance' in performance_metrics:
            current_perf = performance_metrics['current_performance']
            baseline_perf = performance_metrics['baseline_performance']
            
            degradation = (baseline_perf - current_perf) / baseline_perf
            
            if degradation > self.rollback_config.performance_threshold_degradation:
                # Find best stable version
                stable_versions = [
                    v for v in self.model_versions[model_id]
                    if v.status in [VersionStatus.ACTIVE, VersionStatus.STABLE]
                ]
                
                if stable_versions:
                    # Sort by performance metadata if available
                    best_version = stable_versions[0]  # Default to first
                    
                    # Try to find version with best performance
                    for version in stable_versions:
                        if 'performance_score' in version.metadata:
                            if version.metadata['performance_score'] > best_version.metadata.get('performance_score', 0):
                                best_version = version
                    
                    # Trigger rollback
                    operation_id = self.initiate_rollback(
                        model_id, 
                        best_version.version_id,
                        RollbackTrigger.PERFORMANCE_DEGRADATION,
                        {'degradation': degradation, 'current_performance': current_perf}
                    )
                    
                    logging.warning(f"Auto rollback triggered for model {model_id}: performance degraded by {degradation:.2%}")
                    return operation_id
        
        # Check error rate
        if 'error_rate' in performance_metrics:
            error_rate = performance_metrics['error_rate']
            if error_rate > self.rollback_config.error_rate_threshold:
                logging.warning(f"High error rate detected: {error_rate:.3f}")
                # Could trigger rollback here as well
        
        return None
    
    def cleanup_storage(self, days_to_keep: int = 30):
        """Saqlashni tozalash"""
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Clean old backup files
        for file_path in self.storage_path.glob("backup_*.pkl"):
            try:
                # Extract timestamp from filename
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_date:
                    file_path.unlink()
                    logging.info(f"Deleted old backup file: {file_path.name}")
            except Exception as e:
                logging.warning(f"Failed to delete backup file {file_path}: {str(e)}")
        
        # Clean old operation records
        self.operation_history = [
            op for op in self.operation_history 
            if op.started_at > cutoff_date
        ]
        
        # Clean database records
        conn = sqlite3.connect(str(self.metadata_db))
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM rollback_operations 
            WHERE started_at < ?
        ''', (cutoff_date.isoformat(),))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Storage cleanup completed for files older than {cutoff_date}")

# Mock model for testing
class MockTradingModel:
    """Test uchun mock trading model"""
    
    def __init__(self, model_type="baseline", version=1):
        self.model_type = model_type
        self.version = version
        self.trained = False
        self.performance = np.random.uniform(0.6, 0.9)
        self.created_at = datetime.now()
    
    def fit(self, X, y):
        self.trained = True
        self.performance = np.random.uniform(0.65, 0.95)
        return self
    
    def predict(self, X):
        if not self.trained:
            return np.random.randint(0, 2, len(X) if hasattr(X, '__len__') else 1)
        return np.random.randint(0, 2, len(X) if hasattr(X, '__len__') else 1)
    
    def __getstate__(self):
        return {
            'model_type': self.model_type,
            'version': self.version,
            'trained': self.trained,
            'performance': self.performance,
            'created_at': self.created_at
        }
    
    def __setstate__(self, state):
        self.model_type = state['model_type']
        self.version = state['version']
        self.trained = state['trained']
        self.performance = state['performance']
        self.created_at = state['created_at']

# Demo va test
if __name__ == "__main__":
    # Rollback manager testi
    rollback_manager = RollbackManager({
        'storage_path': './test_rollback_storage',
        'max_versions_to_keep': 5,
        'auto_rollback_enabled': True,
        'backup_before_rollback': True
    })
    
    print("=== ROLLBACK MANAGER TEST ===")
    
    # Create mock models
    model1_v1 = MockTradingModel("baseline", 1)
    model1_v2 = MockTradingModel("improved", 2)
    model1_v3 = MockTradingModel("enhanced", 3)
    
    model_id = "trading_model_1"
    
    # Create versions
    version1_id = rollback_manager.create_model_version(model_id, model1_v1, {'performance_score': 0.75})
    version2_id = rollback_manager.create_model_version(model_id, model1_v2, {'performance_score': 0.80})
    version3_id = rollback_manager.create_model_version(model_id, model1_v3, {'performance_score': 0.70})  # Lower performance
    
    print(f"Created versions: {version1_id}, {version2_id}, {version3_id}")
    
    # Get model versions
    versions = rollback_manager.get_model_versions(model_id)
    print(f"\nModel versions:")
    for version in versions:
        print(f"  {version['version_id']}: {version['status']}, performance: {version['metadata'].get('performance_score', 'N/A')}")
    
    # Simulate performance degradation
    performance_metrics = {
        'current_performance': 0.65,  # Degraded from baseline
        'baseline_performance': 0.75,
        'error_rate': 0.02
    }
    
    # Test auto rollback
    auto_rollback_op = rollback_manager.auto_rollback_check(model_id, performance_metrics)
    print(f"\nAuto rollback operation: {auto_rollback_op}")
    
    # Manual rollback
    if auto_rollback_op:
        # Wait for rollback to complete
        time.sleep(2)
        
        rollback_status = rollback_manager.get_rollback_status(auto_rollback_op)
        print(f"Rollback status: {rollback_status['status']}")
    
    # Test manual rollback
    manual_rollback_op = rollback_manager.initiate_rollback(model_id, version2_id, RollbackTrigger.MANUAL)
    print(f"\nManual rollback operation: {manual_rollback_op}")
    
    # Wait for rollback to complete
    time.sleep(2)
    
    rollback_status = rollback_manager.get_rollback_status(manual_rollback_op)
    print(f"Manual rollback status: {rollback_status['status']}")
    print(f"Duration: {rollback_status['duration_seconds']:.2f} seconds")
    
    # Check current version
    current_version = rollback_manager.current_versions.get(model_id)
    print(f"Current version after rollback: {current_version}")
    
    # Get rollback history
    history = rollback_manager.get_rollback_history(10)
    print(f"\nRollback history: {len(history)} operations")
    for op in history:
        print(f"  {op['operation_id']}: {op['status']} ({op['trigger']})")
    
    # Test version validation
    for version in rollback_manager.model_versions[model_id]:
        if version.version_id == version2_id:
            validation_result = rollback_manager._validate_version(version)
            print(f"\nValidation for {version2_id}:")
            print(f"  Passed: {validation_result.validation_passed}")
            print(f"  Checks: {validation_result.checks_performed}")
            print(f"  Errors: {validation_result.errors}")
            break
    
    # Test cleanup
    rollback_manager.cleanup_storage(days_to_keep=1)
    print(f"\nStorage cleanup completed")
    
    # Clean up test storage
    try:
        shutil.rmtree('./test_rollback_storage')
        print("Test storage cleaned up")
    except Exception as e:
        print(f"Failed to clean test storage: {e}")
    
    print("\n=== ROLLBACK MANAGER TEST COMPLETED ===")