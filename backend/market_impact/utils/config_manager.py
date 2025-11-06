"""
Configuration Manager

Market Impact Modeling tizimi uchun configuration management.
"""

import json
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ModelConfig:
    """Price impact model configuration"""
    kyle: Dict[str, float]
    obizhaeva_wang: Dict[str, float]
    almgren_chriss: Dict[str, float]
    bertsimas_lo: Dict[str, float]


@dataclass
class LiquidityConfig:
    """Liquidity analysis configuration"""
    lookback_window: int
    min_size_threshold: float
    spread_window: int
    alert_thresholds: Dict[str, float]


@dataclass
class ExecutionConfig:
    """Execution optimization configuration"""
    default_participation_rate: float
    default_aggressiveness: float
    default_time_horizon: float
    optimization_objectives: list


@dataclass
class SystemConfig:
    """Main system configuration"""
    models: ModelConfig
    liquidity: LiquidityConfig
    execution: ExecutionConfig
    system: Dict[str, Any]


class ConfigManager:
    """
    Configuration Manager
    
    Market Impact Modeling tizimi uchun configuration management.
    """
    
    DEFAULT_CONFIG = {
        'models': {
            'kyle': {
                'lambda_param': 0.01,
                'sigma_v': 0.02,
                'sigma_u': 0.1,
                'theta': 0.5
            },
            'obizhaeva_wang': {
                'alpha': 0.001,
                'beta': 0.1,
                'gamma': 0.01,
                'delta': 0.001,
                'sigma': 0.02
            },
            'almgren_chriss': {
                'eta': 0.0001,
                'gamma': 0.01,
                'sigma': 0.02,
                'T': 1.0,
                'lambda_risk': 1e-6
            },
            'bertsimas_lo': {
                'kappa': 0.001,
                'phi': 0.1,
                'lambda_noise': 0.1,
                'theta_market': 0.01,
                'gamma_adapt': 0.5,
                'sigma_info': 0.02
            }
        },
        'liquidity': {
            'lookback_window': 100,
            'min_size_threshold': 100.0,
            'spread_window': 1000,
            'alert_thresholds': {
                'spread_widening': 0.001,
                'volume_spike': 2.0,
                'depth_deterioration': 0.5,
                'liquidity_score_low': 30.0,
                'volatility_spike': 0.05
            }
        },
        'execution': {
            'default_participation_rate': 0.1,
            'default_aggressiveness': 0.5,
            'default_time_horizon': 1.0,
            'optimization_objectives': [
                'minimize_cost',
                'minimize_impact',
                'maximize_completion'
            ]
        },
        'system': {
            'log_level': 'INFO',
            'data_cache_size': 1000,
            'performance_tracking': True,
            'real_time_monitoring': True
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> SystemConfig:
        """Load configuration from file or use defaults"""
        if self.config_file and Path(self.config_file).exists():
            return self._load_from_file(self.config_file)
        else:
            return self._create_from_dict(self.DEFAULT_CONFIG)
            
    def _load_from_file(self, file_path: str) -> SystemConfig:
        """Load configuration from file"""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'r') as f:
                config_dict = json.load(f)
        elif file_path.suffix.lower() in ['.yaml', '.yml']:
            with open(file_path, 'r') as f:
                config_dict = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported config file format: {file_path.suffix}")
            
        return self._create_from_dict(config_dict)
        
    def _create_from_dict(self, config_dict: Dict[str, Any]) -> SystemConfig:
        """Create SystemConfig from dictionary"""
        return SystemConfig(
            models=ModelConfig(**config_dict.get('models', {})),
            liquidity=LiquidityConfig(**config_dict.get('liquidity', {})),
            execution=ExecutionConfig(**config_dict.get('execution', {})),
            system=config_dict.get('system', {})
        )
        
    def save_config(self, file_path: str, format_type: str = 'json') -> None:
        """
        Save configuration to file
        
        Args:
            file_path: Output file path
            format_type: 'json' or 'yaml'
        """
        config_dict = asdict(self.config)
        
        file_path = Path(file_path)
        
        if format_type.lower() == 'json':
            with open(file_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
        elif format_type.lower() in ['yaml', 'yml']:
            with open(file_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
            
    def get_model_config(self, model_name: str) -> Dict[str, float]:
        """
        Get configuration for specific model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model configuration dictionary
        """
        model_configs = asdict(self.config.models)
        return model_configs.get(model_name, {})
        
    def update_model_config(self, model_name: str, config: Dict[str, float]) -> None:
        """
        Update configuration for specific model
        
        Args:
            model_name: Name of the model
            config: New configuration
        """
        if hasattr(self.config.models, model_name):
            current_config = getattr(self.config.models, model_name)
            updated_config = {**asdict(current_config), **config}
            setattr(self.config.models, model_name, type(current_config)(**updated_config))
        else:
            raise ValueError(f"Unknown model: {model_name}")
            
    def get_liquidity_config(self) -> Dict[str, Any]:
        """Get liquidity configuration"""
        return asdict(self.config.liquidity)
        
    def update_liquidity_config(self, config: Dict[str, Any]) -> None:
        """Update liquidity configuration"""
        current_config = asdict(self.config.liquidity)
        updated_config = {**current_config, **config}
        self.config.liquidity = type(self.config.liquidity)(**updated_config)
        
    def get_execution_config(self) -> Dict[str, Any]:
        """Get execution configuration"""
        return asdict(self.config.execution)
        
    def update_execution_config(self, config: Dict[str, Any]) -> None:
        """Update execution configuration"""
        current_config = asdict(self.config.execution)
        updated_config = {**current_config, **config}
        self.config.execution = type(self.config.execution)(**updated_config)
        
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration"""
        return self.config.system
        
    def update_system_config(self, config: Dict[str, Any]) -> None:
        """Update system configuration"""
        self.config.system.update(config)
        
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config = self._create_from_dict(self.DEFAULT_CONFIG)
        
    def validate_config(self) -> Dict[str, Any]:
        """
        Validate current configuration
        
        Returns:
            Validation results
        """
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Validate model configurations
        model_configs = asdict(self.config.models)
        for model_name, config in model_configs.items():
            # Check for required parameters
            if model_name == 'kyle':
                required = ['lambda_param', 'sigma_v', 'sigma_u', 'theta']
            elif model_name == 'obizhaeva_wang':
                required = ['alpha', 'beta', 'gamma', 'delta', 'sigma']
            elif model_name == 'almgren_chriss':
                required = ['eta', 'gamma', 'sigma', 'T', 'lambda_risk']
            elif model_name == 'bertsimas_lo':
                required = ['kappa', 'phi', 'lambda_noise', 'theta_market', 'gamma_adapt', 'sigma_info']
            else:
                required = []
                
            missing = [param for param in required if param not in config]
            if missing:
                validation_results['errors'].append(f"Model {model_name} missing parameters: {missing}")
                validation_results['valid'] = False
                
            # Check parameter ranges
            for param, value in config.items():
                if isinstance(value, (int, float)):
                    if value < 0:
                        validation_results['warnings'].append(f"Model {model_name} parameter {param} is negative: {value}")
                        
        # Validate liquidity configuration
        liq_config = asdict(self.config.liquidity)
        if liq_config.get('lookback_window', 0) < 10:
            validation_results['warnings'].append("Lookback window is very small")
        if liq_config.get('min_size_threshold', 0) <= 0:
            validation_results['errors'].append("Min size threshold must be positive")
            validation_results['valid'] = False
            
        # Validate execution configuration
        exec_config = asdict(self.config.execution)
        if exec_config.get('default_participation_rate', 0) > 1.0:
            validation_results['errors'].append("Default participation rate must be <= 1.0")
            validation_results['valid'] = False
        if exec_config.get('default_aggressiveness', 0) > 1.0:
            validation_results['errors'].append("Default aggressiveness must be <= 1.0")
            validation_results['valid'] = False
            
        return validation_results
        
    def create_template_config(self, output_file: str, format_type: str = 'json') -> None:
        """
        Create configuration template file
        
        Args:
            output_file: Output template file path
            format_type: 'json' or 'yaml'
        """
        template_config = {
            'models': {
                'kyle': {
                    'lambda_param': 0.01,
                    'sigma_v': 0.02,
                    'sigma_u': 0.1,
                    'theta': 0.5
                },
                'obizhaeva_wang': {
                    'alpha': 0.001,
                    'beta': 0.1,
                    'gamma': 0.01,
                    'delta': 0.001,
                    'sigma': 0.02
                },
                'almgren_chriss': {
                    'eta': 0.0001,
                    'gamma': 0.01,
                    'sigma': 0.02,
                    'T': 1.0,
                    'lambda_risk': 1e-6
                },
                'bertsimas_lo': {
                    'kappa': 0.001,
                    'phi': 0.1,
                    'lambda_noise': 0.1,
                    'theta_market': 0.01,
                    'gamma_adapt': 0.5,
                    'sigma_info': 0.02
                }
            },
            'liquidity': {
                'lookback_window': 100,
                'min_size_threshold': 100.0,
                'spread_window': 1000,
                'alert_thresholds': {
                    'spread_widening': 0.001,
                    'volume_spike': 2.0,
                    'depth_deterioration': 0.5,
                    'liquidity_score_low': 30.0,
                    'volatility_spike': 0.05
                }
            },
            'execution': {
                'default_participation_rate': 0.1,
                'default_aggressiveness': 0.5,
                'default_time_horizon': 1.0,
                'optimization_objectives': [
                    'minimize_cost',
                    'minimize_impact',
                    'maximize_completion'
                ]
            },
            'system': {
                'log_level': 'INFO',
                'data_cache_size': 1000,
                'performance_tracking': True,
                'real_time_monitoring': True
            }
        }
        
        self.save_config(output_file, format_type)
        
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get configuration summary
        
        Returns:
            Configuration summary
        """
        return {
            'total_models': len(asdict(self.config.models)),
            'model_names': list(asdict(self.config.models).keys()),
            'liquidity_window': self.config.liquidity.lookback_window,
            'default_participation': self.config.execution.default_participation_rate,
            'system_log_level': self.config.system.get('log_level', 'INFO'),
            'config_source': 'file' if self.config_file else 'default',
            'config_file': self.config_file
        }