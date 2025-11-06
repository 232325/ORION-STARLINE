"""
ML Model Updates Main System
Machine Learning Model Updates va Real-time Model Management tizimi
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import argparse
import numpy as np

# Import all components
from config.config import (
    ModelConfig, UpdateConfig, MonitoringConfig, AutoMLConfig, GovernanceConfig,
    ConfigManager, create_default_configs
)

from versioning.registry import ModelRegistryManager
from updating.strategies import ModelUpdateManager
from monitoring.system import ModelMonitoringSystem
from automl.system import AutoMLSystem, AutoMLConfig as AutoMLConfigObj
from governance.system import ModelGovernance

class MLModelUpdateSystem:
    """Asosiy ML Model Update tizimi"""
    
    def __init__(self, system_config_path: str = "config"):
        self.config_path = Path(system_config_path)
        self.config_path.mkdir(exist_ok=True)
        
        # Logging setup
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Configuration manager
        self.config_manager = ConfigManager(str(self.config_path))
        
        # Core components
        self.registry = ModelRegistryManager("models/registry")
        self.update_manager = ModelUpdateManager({})
        self.monitoring_system = ModelMonitoringSystem({})
        self.governance_system = ModelGovernance({})
        
        # State
        self.registered_models = {}
        self.active_sessions = {}
        
    def _setup_logging(self):
        """Logging tizimini sozlash"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "ml_system.log"),
                logging.StreamHandler()
            ]
        )
        
    def initialize_model(self, model_name: str, model_type: str, 
                        framework: str = "sklearn") -> str:
        """Model ni tizimda initialize qilish"""
        
        try:
            # Default configurations yaratish
            configs = create_default_configs(model_name, model_type)
            
            # Model registry ga qo'shish
            version_id = self.registry.create_model(model_name, model_type, framework)
            
            # Registered models ga qo'shish
            self.registered_models[model_name] = {
                'model_type': model_type,
                'framework': framework,
                'version_id': version_id,
                'created_at': datetime.now(),
                'config_files': configs
            }
            
            # Governance ga register
            model_info = {
                'version_id': version_id,
                'framework': framework,
                'explainable': False,
                'data_quality_monitored': True,
                'drift_monitoring': True,
                'bias_detection': True,
                'fairness_monitoring': True,
                'documentation_complete': True,
                'audit_trail': True,
                'monitoring_enabled': True,
                'alert_system': True,
                'rollback_capability': True
            }
            
            governance_record = self.governance_system.register_model(
                model_name=model_name,
                model=None,  # Placeholder
                model_info=model_info,
                performed_by='system'
            )
            
            self.logger.info(f"Model initialized: {model_name} (version: {version_id})")
            return version_id
            
        except Exception as e:
            self.logger.error(f"Model initialization xatosi: {str(e)}")
            raise
            
    def update_model(self, model_name: str, new_data: Any, strategy: str = None,
                   target_column: str = None) -> Dict[str, Any]:
        """Model yangilash"""
        
        if model_name not in self.registered_models:
            raise ValueError(f"Model ro'yxatdan o'tmagan: {model_name}")
            
        try:
            # Model ma'lumotlarini olish
            model_record = self.registered_models[model_name]
            version_id = model_record['version_id']
            
            # Auto strategy selection agar berilmagan
            if strategy is None:
                strategy = 'full_retrain'  # Default
                
            # Model update
            update_metrics = self.update_manager.update_model(
                model_name=model_name,
                current_model=None,  # Placeholder
                new_data=new_data,
                target_column=target_column or 'target',
                strategy=strategy
            )
            
            # Audit log
            self.governance_system.audit_logger.log_action(
                model_name=model_name,
                version_id=version_id,
                action='updated',
                performed_by='user',
                details={
                    'strategy': strategy,
                    'update_metrics': {
                        'success': update_metrics.success,
                        'accuracy_improvement': update_metrics.accuracy_improvement,
                        'training_time': update_metrics.training_time_seconds
                    }
                }
            )
            
            result = {
                'status': 'success' if update_metrics.success else 'failed',
                'model_name': model_name,
                'strategy': strategy,
                'update_metrics': {
                    'old_accuracy': update_metrics.old_model_accuracy,
                    'new_accuracy': update_metrics.new_model_accuracy,
                    'improvement': update_metrics.accuracy_improvement,
                    'training_time_seconds': update_metrics.training_time_seconds,
                    'data_processed': update_metrics.data_processed,
                    'success': update_metrics.success,
                    'error': update_metrics.error_message
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Model updated: {model_name}, "
                           f"success: {update_metrics.success}")
            return result
            
        except Exception as e:
            self.logger.error(f"Model update xatosi: {str(e)}")
            return {
                'status': 'error',
                'model_name': model_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
    def start_monitoring(self, model_name: str):
        """Model monitoring boshlanishi"""
        
        if model_name not in self.registered_models:
            raise ValueError(f"Model ro'yxatdan o'tmagan: {model_name}")
            
        try:
            # Monitoring start
            self.monitoring_system.start_monitoring(model_name)
            
            # Audit log
            self.governance_system.audit_logger.log_action(
                model_name=model_name,
                version_id=self.registered_models[model_name]['version_id'],
                action='monitoring_started',
                performed_by='user'
            )
            
            self.logger.info(f"Monitoring started: {model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Monitoring start xatosi: {str(e)}")
            return False
            
    def get_model_status(self, model_name: str) -> Dict[str, Any]:
        """Model status olish"""
        
        if model_name not in self.registered_models:
            return {'error': 'Model topilmadi'}
            
        try:
            model_record = self.registered_models[model_name]
            version_id = model_record['version_id']
            
            # Monitoring summary
            monitoring_summary = self.monitoring_system.get_monitoring_summary(model_name)
            
            # Governance summary
            governance_summary = self.governance_system.get_governance_summary(model_name)
            
            # Registry summary
            registry_summary = self.registry.get_model_summary(model_name)
            
            return {
                'model_name': model_name,
                'status': 'active',
                'version_id': version_id,
                'model_type': model_record['model_type'],
                'framework': model_record['framework'],
                'created_at': model_record['created_at'].isoformat(),
                'monitoring': monitoring_summary,
                'governance': governance_summary,
                'registry': registry_summary,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Status olish xatosi: {str(e)}")
            return {
                'error': str(e),
                'model_name': model_name
            }
            
    def run_automl(self, model_name: str, training_data: Any, 
                  config: Dict[str, Any] = None) -> Dict[str, Any]:
        """AutoML pipeline ishga tushirish"""
        
        if model_name not in self.registered_models:
            raise ValueError(f"Model ro'yxatdan o'tmagan: {model_name}")
            
        try:
            # AutoML config
            if config is None:
                config = {
                    'task_type': 'classification',
                    'algorithms': ['random_forest', 'gradient_boosting', 'logistic_regression'],
                    'search_strategy': 'random',
                    'max_trials': 20,
                    'timeout_hours': 2.0,
                    'cv_folds': 5,
                    'validation_split': 0.2,
                    'random_state': 42,
                    'preprocessing_enabled': True,
                    'feature_selection_enabled': True,
                    'ensemble_enabled': False,
                    'optimization_metric': 'accuracy',
                    'optimization_direction': 'maximize'
                }
                
            automl_config = AutoMLConfigObj(**config)
            
            # AutoML system
            automl_system = AutoMLSystem(automl_config)
            
            # Pipeline ishga tushirish
            results = automl_system.run_automl(
                X=training_data.drop(columns=['target']),
                y=training_data['target'],
                model_output_path=f"models/automl_{model_name}.pkl"
            )
            
            # Audit log
            self.governance_system.audit_logger.log_action(
                model_name=model_name,
                version_id=self.registered_models[model_name]['version_id'],
                action='automl_completed',
                performed_by='user',
                details={
                    'status': results['status'],
                    'best_algorithm': results['best_trial']['algorithm'],
                    'best_score': results['best_trial']['cv_score']
                }
            )
            
            self.logger.info(f"AutoML completed: {model_name}, "
                           f"status: {results['status']}")
            return results
            
        except Exception as e:
            self.logger.error(f"AutoML xatosi: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'model_name': model_name
            }
            
    def analyze_bias(self, model_name: str, data: Any, protected_attributes: List[str]) -> Dict[str, Any]:
        """Model bias tahlili"""
        
        if model_name not in self.registered_models:
            raise ValueError(f"Model ro'yxatdan o'tmagan: {model_name}")
            
        try:
            # Placeholder data
            y_true = data['target'].values
            y_pred = np.random.randint(0, 2, len(y_true))  # Random predictions
            
            # Bias analysis
            bias_results = self.governance_system.perform_bias_analysis(
                model=None,  # Placeholder
                X=data.drop(columns=['target']),
                y_true=y_true,
                y_pred=y_pred,
                protected_attributes=protected_attributes
            )
            
            bias_summary = {
                'protected_attributes_tested': protected_attributes,
                'bias_detected_count': len([r for r in bias_results if r.bias_detected]),
                'high_severity_count': len([r for r in bias_results if r.bias_severity == 'high']),
                'results': [{
                    'attribute': result.protected_attribute,
                    'bias_detected': result.bias_detected,
                    'severity': result.bias_severity,
                    'fairness_metrics': result.fairness_metrics,
                    'recommendations': result.recommendations
                } for result in bias_results]
            }
            
            self.logger.info(f"Bias analysis completed: {model_name}")
            return bias_summary
            
        except Exception as e:
            self.logger.error(f"Bias analysis xatosi: {str(e)}")
            return {
                'error': str(e),
                'model_name': model_name
            }
            
    def get_system_overview(self) -> Dict[str, Any]:
        """Tizim overview olish"""
        
        try:
            # Update statistics
            update_stats = self.update_manager.get_update_statistics()
            
            # Registered models
            models_overview = []
            for model_name, record in self.registered_models.items():
                models_overview.append({
                    'name': model_name,
                    'type': record['model_type'],
                    'framework': record['framework'],
                    'version': record['version_id'],
                    'created_at': record['created_at'].isoformat()
                })
                
            # Monitoring status
            monitoring_status = {
                model: status for model, status in self.monitoring_system.monitoring_status.items()
            }
            
            return {
                'system_status': 'running',
                'registered_models_count': len(self.registered_models),
                'models': models_overview,
                'monitoring_status': monitoring_status,
                'update_statistics': update_stats,
                'system_version': '1.0.0',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Overview olish xatosi: {str(e)}")
            return {
                'error': str(e),
                'system_status': 'error'
            }

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="ML Model Updates System")
    parser.add_argument('--model-name', help='Model nomi')
    parser.add_argument('--action', choices=['init', 'update', 'monitor', 'status', 'automl', 'bias', 'overview'], 
                       help='Bajarish kerak bo\'lgan amal')
    parser.add_argument('--model-type', default='classification', help='Model turi')
    parser.add_argument('--framework', default='sklearn', help='ML framework')
    parser.add_argument('--strategy', help='Update strategy')
    parser.add_argument('--protected-attrs', nargs='+', help='Protected attributes for bias analysis')
    parser.add_argument('--config-path', default='config', help='Konfiguratsiya papka yo\'li')
    
    args = parser.parse_args()
    
    # Tizim yaratish
    system = MLModelUpdateSystem(args.config_path)
    
    if args.action == 'init':
        if not args.model_name:
            print("Model name talab qilinadi")
            return
            
        version_id = system.initialize_model(args.model_name, args.model_type, args.framework)
        print(f"Model initialized: {args.model_name}, version: {version_id}")
        
    elif args.action == 'status':
        if not args.model_name:
            print("Model name talab qilinadi")
            return
            
        status = system.get_model_status(args.model_name)
        print(json.dumps(status, indent=2, default=str))
        
    elif args.action == 'overview':
        overview = system.get_system_overview()
        print(json.dumps(overview, indent=2, default=str))
        
    elif args.action == 'monitor':
        if not args.model_name:
            print("Model name talab qilinadi")
            return
            
        success = system.start_monitoring(args.model_name)
        print(f"Monitoring {'started' if success else 'failed'}: {args.model_name}")
        
    elif args.action == 'automl':
        if not args.model_name:
            print("Model name talab qilinadi")
            return
            
        # Placeholder data
        import pandas as pd
        np.random.seed(42)
        sample_data = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'feature3': np.random.randn(100),
            'target': np.random.randint(0, 2, 100)
        })
        
        results = system.run_automl(args.model_name, sample_data)
        print(json.dumps(results, indent=2, default=str))
        
    elif args.action == 'bias':
        if not args.model_name:
            print("Model name talab qilinadi")
            return
            
        if not args.protected_attrs:
            print("Protected attributes talab qilinadi")
            return
            
        # Placeholder data
        import pandas as pd
        sample_data = pd.DataFrame({
            'feature1': np.random.randn(100),
            'feature2': np.random.randn(100),
            'protected_attr': np.random.choice(['A', 'B'], 100),
            'target': np.random.randint(0, 2, 100)
        })
        
        results = system.analyze_bias(args.model_name, sample_data, args.protected_attrs)
        print(json.dumps(results, indent=2, default=str))
        
    elif args.action == 'update':
        print("Model update functionality - placeholder")
        # Bu yerda real update logic qo'shilishi mumkin
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()