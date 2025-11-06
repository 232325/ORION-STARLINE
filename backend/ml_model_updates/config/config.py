"""
ML Model Updates System Configuration
Machine Learning Model Updates va Real-time Model Management tizimi
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
import json
import yaml

@dataclass
class ModelConfig:
    """Model yangilash konfiguratsiyasi"""
    model_name: str
    model_type: str
    version: str
    framework: str  # tensorflow, pytorch, sklearn, etc.
    architecture: str
    training_data_path: str
    model_path: str
    metadata_path: str
    auto_update: bool = False
    update_frequency: str = "weekly"  # daily, weekly, monthly
    rollback_enabled: bool = True
    monitoring_enabled: bool = True
    explainable_ai: bool = False
    bias_detection: bool = False

@dataclass
class UpdateConfig:
    """Model yangilash sozlamalari"""
    incremental_learning: bool = True
    full_retrain: bool = True
    ensemble_updates: bool = True
    transfer_learning: bool = True
    federated_learning: bool = False
    
    # Training parameters
    batch_size: int = 32
    learning_rate: float = 0.001
    epochs: int = 100
    validation_split: float = 0.2
    early_stopping: bool = True
    early_stopping_patience: int = 10
    
    # Update strategies
    min_performance_threshold: float = 0.95
    max_training_time_hours: int = 24
    resource_limits: Dict[str, Union[int, float]] = None
    
    def __post_init__(self):
        if self.resource_limits is None:
            self.resource_limits = {
                'cpu_cores': 8,
                'memory_gb': 16,
                'gpu_count': 1,
                'disk_gb': 100
            }

@dataclass
class MonitoringConfig:
    """Model monitoring konfiguratsiyasi"""
    drift_detection: bool = True
    performance_monitoring: bool = True
    feature_importance_tracking: bool = True
    data_quality_monitoring: bool = True
    prediction_accuracy_tracking: bool = True
    
    # Alert settings
    alert_thresholds: Dict[str, float] = None
    alert_channels: List[str] = None
    alert_frequencies: Dict[str, str] = None
    
    # Monitoring intervals
    prediction_check_interval: int = 100  # predictions
    drift_check_interval: int = 24  # hours
    performance_check_interval: int = 12  # hours
    
    def __post_init__(self):
        if self.alert_thresholds is None:
            self.alert_thresholds = {
                'model_drift': 0.1,
                'accuracy_drop': 0.05,
                'prediction_confidence': 0.8,
                'data_quality_score': 0.9
            }
        
        if self.alert_channels is None:
            self.alert_channels = ['email', 'webhook']
            
        if self.alert_frequencies is None:
            self.alert_frequencies = {
                'critical': 'immediate',
                'warning': 'hourly',
                'info': 'daily'
            }

@dataclass
class AutoMLConfig:
    """AutoML konfiguratsiyasi"""
    hyperparameter_tuning: bool = True
    feature_selection: bool = True
    model_selection: bool = True
    architecture_search: bool = False
    preprocessing_automation: bool = True
    
    # Search parameters
    search_space: Dict[str, List] = None
    optimization_metric: str = "accuracy"
    optimization_direction: str = "maximize"
    max_trials: int = 100
    timeout_hours: int = 24
    
    # Algorithms to consider
    algorithms: List[str] = None
    
    def __post_init__(self):
        if self.search_space is None:
            self.search_space = {
                'learning_rate': [0.001, 0.01, 0.1],
                'batch_size': [16, 32, 64, 128],
                'hidden_layers': [2, 3, 4, 5],
                'dropout': [0.1, 0.2, 0.3, 0.5]
            }
        
        if self.algorithms is None:
            self.algorithms = [
                'random_forest', 'xgboost', 'neural_network', 
                'svm', 'logistic_regression', 'decision_tree'
            ]

@dataclass
class GovernanceConfig:
    """Model governance konfiguratsiyasi"""
    audit_trails: bool = True
    bias_detection: bool = True
    regulatory_compliance: bool = True
    explainable_ai: bool = True
    risk_assessment: bool = True
    
    # Compliance requirements
    regulations: List[str] = None
    documentation_required: bool = True
    approval_workflow: bool = True
    
    # Bias detection
    fairness_metrics: List[str] = None
    protected_attributes: List[str] = None
    
    def __post_init__(self):
        if self.regulations is None:
            self.regulations = ['GDPR', 'CCPA', 'HIPAA', 'SOX']
            
        if self.fairness_metrics is None:
            self.fairness_metrics = [
                'demographic_parity', 'equalized_odds', 
                'calibration', 'individual_fairness'
            ]
            
        if self.protected_attributes is None:
            self.protected_attributes = ['age', 'gender', 'race', 'ethnicity']

class ConfigManager:
    """Konfiguratsiya boshqaruvchisi"""
    
    def __init__(self, config_path: str = "config"):
        self.config_path = config_path
        os.makedirs(config_path, exist_ok=True)
        
    def save_model_config(self, model_config: ModelConfig) -> str:
        """Model konfiguratsiyasini saqlash"""
        config_file = os.path.join(self.config_path, f"{model_config.model_name}_config.yaml")
        with open(config_file, 'w') as f:
            yaml.dump(model_config.__dict__, f, default_flow_style=False)
        return config_file
        
    def load_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """Model konfiguratsiyasini yuklash"""
        config_file = os.path.join(self.config_path, f"{model_name}_config.yaml")
        if not os.path.exists(config_file):
            return None
            
        with open(config_file, 'r') as f:
            config_dict = yaml.safe_load(f)
        return ModelConfig(**config_dict)
        
    def save_update_config(self, config: UpdateConfig, model_name: str) -> str:
        """Update konfiguratsiyasini saqlash"""
        config_file = os.path.join(self.config_path, f"{model_name}_update_config.yaml")
        with open(config_file, 'w') as f:
            yaml.dump(config.__dict__, f, default_flow_style=False)
        return config_file
        
    def load_update_config(self, model_name: str) -> Optional[UpdateConfig]:
        """Update konfiguratsiyasini yuklash"""
        config_file = os.path.join(self.config_path, f"{model_name}_update_config.yaml")
        if not os.path.exists(config_file):
            return None
            
        with open(config_file, 'r') as f:
            config_dict = yaml.safe_load(f)
        return UpdateConfig(**config_dict)
        
    def save_monitoring_config(self, config: MonitoringConfig, model_name: str) -> str:
        """Monitoring konfiguratsiyasini saqlash"""
        config_file = os.path.join(self.config_path, f"{model_name}_monitoring_config.yaml")
        with open(config_file, 'w') as f:
            yaml.dump(config.__dict__, f, default_flow_style=False)
        return config_file
        
    def load_monitoring_config(self, model_name: str) -> Optional[MonitoringConfig]:
        """Monitoring konfiguratsiyasini yuklash"""
        config_file = os.path.join(self.config_path, f"{model_name}_monitoring_config.yaml")
        if not os.path.exists(config_file):
            return None
            
        with open(config_file, 'r') as f:
            config_dict = yaml.safe_load(f)
        return MonitoringConfig(**config_dict)
        
    def save_automl_config(self, config: AutoMLConfig, model_name: str) -> str:
        """AutoML konfiguratsiyasini saqlash"""
        config_file = os.path.join(self.config_path, f"{model_name}_automl_config.yaml")
        with open(config_file, 'w') as f:
            yaml.dump(config.__dict__, f, default_flow_style=False)
        return config_file
        
    def load_automl_config(self, model_name: str) -> Optional[AutoMLConfig]:
        """AutoML konfiguratsiyasini yuklash"""
        config_file = os.path.join(self.config_path, f"{model_name}_automl_config.yaml")
        if not os.path.exists(config_file):
            return None
            
        with open(config_file, 'r') as f:
            config_dict = yaml.safe_load(f)
        return AutoMLConfig(**config_dict)
        
    def save_governance_config(self, config: GovernanceConfig, model_name: str) -> str:
        """Governance konfiguratsiyasini saqlash"""
        config_file = os.path.join(self.config_path, f"{model_name}_governance_config.yaml")
        with open(config_file, 'w') as f:
            yaml.dump(config.__dict__, f, default_flow_style=False)
        return config_file
        
    def load_governance_config(self, model_name: str) -> Optional[GovernanceConfig]:
        """Governance konfiguratsiyasini yuklash"""
        config_file = os.path.join(self.config_path, f"{model_name}_governance_config.yaml")
        if not os.path.exists(config_file):
            return None
            
        with open(config_file, 'r') as f:
            config_dict = yaml.safe_load(f)
        return GovernanceConfig(**config_dict)
        
    def get_system_config(self) -> Dict:
        """Umumiy tizim konfiguratsiyasini olish"""
        return {
            'version': '1.0.0',
            'framework_versions': {
                'tensorflow': '2.12.0',
                'pytorch': '2.0.0',
                'scikit_learn': '1.3.0',
                'xgboost': '1.7.0'
            },
            'deployment_environments': ['development', 'staging', 'production'],
            'security': {
                'encryption_enabled': True,
                'access_control': 'rbac',
                'audit_logging': True
            },
            'performance': {
                'max_model_size_mb': 1000,
                'max_prediction_latency_ms': 100,
                'max_concurrent_predictions': 1000
            }
        }

# Global konfiguratsiya
DEFAULT_CONFIG = {
    'model_defaults': {
        'framework': 'sklearn',
        'version': '1.0.0',
        'auto_update': False,
        'monitoring_enabled': True,
        'rollback_enabled': True
    },
    'update_defaults': {
        'incremental_learning': True,
        'full_retrain': False,
        'ensemble_updates': False,
        'min_performance_threshold': 0.95
    },
    'monitoring_defaults': {
        'drift_detection': True,
        'performance_monitoring': True,
        'alert_thresholds': {
            'model_drift': 0.1,
            'accuracy_drop': 0.05
        }
    }
}

def create_default_configs(model_name: str, model_type: str) -> Dict[str, str]:
    """Model uchun default konfiguratsiyalar yaratish"""
    config_manager = ConfigManager()
    
    # Model config
    model_config = ModelConfig(
        model_name=model_name,
        model_type=model_type,
        version="1.0.0",
        framework="sklearn",
        architecture="default",
        training_data_path=f"data/{model_name}_training.csv",
        model_path=f"models/{model_name}/",
        metadata_path=f"models/{model_name}/metadata/",
        auto_update=True,
        monitoring_enabled=True,
        rollback_enabled=True
    )
    
    # Update config
    update_config = UpdateConfig()
    
    # Monitoring config
    monitoring_config = MonitoringConfig()
    
    # AutoML config
    automl_config = AutoMLConfig()
    
    # Governance config
    governance_config = GovernanceConfig()
    
    configs = {}
    configs['model'] = config_manager.save_model_config(model_config)
    configs['update'] = config_manager.save_update_config(update_config, model_name)
    configs['monitoring'] = config_manager.save_monitoring_config(monitoring_config, model_name)
    configs['automl'] = config_manager.save_automl_config(automl_config, model_name)
    configs['governance'] = config_manager.save_governance_config(governance_config, model_name)
    
    return configs