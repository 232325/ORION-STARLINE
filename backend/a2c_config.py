"""
A2C Algorithm Configuration
===========================

Algoritm konfiguratsiyasi va turli trading strategiyalari uchun parametrlar.
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ConservativeConfig:
    """Konservativ trading uchun konfiguratsiya"""
    n_assets: int = 15
    max_position: float = 0.15  # Kam risk
    transaction_cost: float = 0.0005
    slippage: float = 0.0002
    max_drawdown: float = 0.08
    learning_rate: float = 0.00005
    gamma: float = 0.995
    beta_entropy: float = 0.005
    value_loss_coef: float = 0.6
    max_grad_norm: float = 0.3
    lookback_window: int = 90
    hidden_size: int = 384
    lstm_layers: int = 3
    risk_free_rate: float = 0.02
    n_steps: int = 5
    n_workers: int = 1
    batch_size: int = 32

@dataclass
class AggressiveConfig:
    """Agressiv trading uchun konfiguratsiya"""
    n_assets: int = 20
    max_position: float = 0.35  # Yuqori risk
    transaction_cost: float = 0.002
    slippage: float = 0.001
    max_drawdown: float = 0.25
    learning_rate: float = 0.0003
    gamma: float = 0.98
    beta_entropy: float = 0.02
    value_loss_coef: float = 0.4
    max_grad_norm: float = 0.7
    lookback_window: int = 30
    hidden_size: int = 512
    lstm_layers: int = 2
    risk_free_rate: float = 0.02
    n_steps: int = 5
    n_workers: int = 1
    batch_size: int = 32

@dataclass
class BalancedConfig:
    """Balansli trading uchun konfiguratsiya"""
    n_assets: int = 12
    max_position: float = 0.25
    transaction_cost: float = 0.001
    slippage: float = 0.0005
    max_drawdown: float = 0.15
    learning_rate: float = 0.0001
    gamma: float = 0.99
    beta_entropy: float = 0.01
    value_loss_coef: float = 0.5
    max_grad_norm: float = 0.5
    lookback_window: int = 60
    hidden_size: int = 256
    lstm_layers: int = 2
    risk_free_rate: float = 0.02
    n_steps: int = 5
    n_workers: int = 1
    batch_size: int = 32

@dataclass
class ScalpingConfig:
    """Scalping strategy uchun konfiguratsiya"""
    n_assets: int = 8
    max_position: float = 0.4
    transaction_cost: float = 0.0001
    slippage: float = 0.0001
    max_drawdown: float = 0.05
    learning_rate: float = 0.0005
    gamma: float = 0.92
    beta_entropy: float = 0.05
    value_loss_coef: float = 0.3
    max_grad_norm: float = 1.0
    lookback_window: int = 15
    hidden_size: int = 192
    lstm_layers: int = 1
    risk_free_rate: float = 0.02
    n_steps: int = 5
    n_workers: int = 1
    batch_size: int = 32

# Predefined configurations
PREDEFINED_CONFIGS = {
    'conservative': ConservativeConfig(),
    'aggressive': AggressiveConfig(),
    'balanced': BalancedConfig(),
    'scalping': ScalpingConfig()
}

def get_config(strategy: str = 'balanced') -> Any:
    """Strategy bo'yicha konfiguratsiya olish"""
    return PREDEFINED_CONFIGS.get(strategy, BalancedConfig())

def create_custom_config(**kwargs) -> Any:
    """Custom konfiguratsiya yaratish"""
    base_config = BalancedConfig()
    
    # Update with provided parameters
    for key, value in kwargs.items():
        if hasattr(base_config, key):
            setattr(base_config, key, value)
    
    return base_config

# Feature engineering configurations
FEATURE_CONFIGS = {
    'basic': {
        'price_features': True,
        'return_features': True,
        'volatility_features': True,
        'volume_features': False,
        'technical_indicators': False,
        'sentiment_features': False,
        'macroeconomic_features': False,
    },
    'advanced': {
        'price_features': True,
        'return_features': True,
        'volatility_features': True,
        'volume_features': True,
        'technical_indicators': True,
        'sentiment_features': False,
        'macroeconomic_features': False,
    },
    'comprehensive': {
        'price_features': True,
        'return_features': True,
        'volatility_features': True,
        'volume_features': True,
        'technical_indicators': True,
        'sentiment_features': True,
        'macroeconomic_features': True,
    }
}

# Reward shaping configurations
REWARD_CONFIGS = {
    'sharpe_focused': {
        'return_weight': 0.4,
        'risk_weight': 0.3,
        'transaction_cost_weight': 0.2,
        'drawdown_weight': 0.1,
        'sharpe_bonus': 0.05,
        'volatility_penalty': 0.02,
    },
    'return_focused': {
        'return_weight': 0.7,
        'risk_weight': 0.1,
        'transaction_cost_weight': 0.1,
        'drawdown_weight': 0.1,
        'sharpe_bonus': 0.02,
        'volatility_penalty': 0.01,
    },
    'risk_adjusted': {
        'return_weight': 0.3,
        'risk_weight': 0.4,
        'transaction_cost_weight': 0.2,
        'drawdown_weight': 0.1,
        'sharpe_bonus': 0.08,
        'volatility_penalty': 0.05,
    }
}

# Training configurations
TRAINING_CONFIGS = {
    'fast_training': {
        'learning_rate': 0.001,
        'batch_size': 128,
        'n_steps': 3,
        'n_workers': 4,
        'update_frequency': 3,
        'save_frequency': 100,
    },
    'stable_training': {
        'learning_rate': 0.0001,
        'batch_size': 64,
        'n_steps': 5,
        'n_workers': 2,
        'update_frequency': 1,
        'save_frequency': 50,
    },
    'high_frequency': {
        'learning_rate': 0.0005,
        'batch_size': 256,
        'n_steps': 2,
        'n_workers': 8,
        'update_frequency': 5,
        'save_frequency': 200,
    }
}

def get_feature_config(level: str = 'basic') -> Dict[str, bool]:
    """Feature engineering konfiguratsiyasini olish"""
    return FEATURE_CONFIGS.get(level, FEATURE_CONFIGS['basic'])

def get_reward_config(style: str = 'sharpe_focused') -> Dict[str, float]:
    """Reward shaping konfiguratsiyasini olish"""
    return REWARD_CONFIGS.get(style, REWARD_CONFIGS['sharpe_focused'])

def get_training_config(speed: str = 'stable_training') -> Dict[str, Any]:
    """Training konfiguratsiyasini olish"""
    return TRAINING_CONFIGS.get(speed, TRAINING_CONFIGS['stable_training'])

# Asset allocation presets
ASSET_PRESETS = {
    'equities_focus': {
        'stock_weight': 0.7,
        'bond_weight': 0.2,
        'commodity_weight': 0.05,
        'crypto_weight': 0.03,
        'cash_weight': 0.02,
    },
    'diversified': {
        'stock_weight': 0.4,
        'bond_weight': 0.3,
        'commodity_weight': 0.15,
        'crypto_weight': 0.1,
        'cash_weight': 0.05,
    },
    'alternatives_focus': {
        'stock_weight': 0.3,
        'bond_weight': 0.2,
        'commodity_weight': 0.25,
        'crypto_weight': 0.2,
        'cash_weight': 0.05,
    },
    'fixed_income_focus': {
        'stock_weight': 0.2,
        'bond_weight': 0.6,
        'commodity_weight': 0.1,
        'crypto_weight': 0.05,
        'cash_weight': 0.05,
    }
}

def get_asset_preset(name: str) -> Dict[str, float]:
    """Asset allocation presetini olish"""
    return ASSET_PRESETS.get(name, ASSET_PRESETS['diversified'])