"""
Configuration Manager

Tizim konfiguratsiyasini boshqarish uchun
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class SystemConfig:
    """Tizim konfiguratsiyasi"""
    # Performance monitoring
    performance_update_interval: int = 60  # sekund
    max_performance_history: int = 1000
    
    # Decision making
    decision_timeout: int = 30  # sekund
    confidence_threshold: float = 0.8
    
    # Trading
    min_trade_size: float = 100.0
    max_trade_size: float = 10000.0
    risk_tolerance: float = 0.02
    
    # Governance
    large_trade_threshold: float = 0.05  # Portfolio % ko'rinishida
    strategy_change_threshold: float = 0.05
    governance_timeout: int = 3600  # 1 soat
    
    # Risk management
    max_portfolio_risk: float = 0.10
    stop_loss_threshold: float = 0.05
    take_profit_threshold: float = 0.15

class ConfigManager:
    """Konfiguratsiya menedjeri"""
    
    def __init__(self, config: Optional[Dict] = None, config_file: Optional[str] = None):
        self._config = asdict(SystemConfig())
        
        # Fayl dan config yuklash
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
        
        # Runtime config update
        if config:
            self.update_config(config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Config qiymatini olish"""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Config qiymatini o'rnatish"""
        keys = key.split('.')
        config = self._config
        
        # Nested key yaratish
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def update_config(self, updates: Dict[str, Any]):
        """Config ni yangilash"""
        for key, value in updates.items():
            self.set(key, value)
    
    def save_to_file(self, file_path: str):
        """Config ni fayl ga saqlash"""
        with open(file_path, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def load_from_file(self, file_path: str):
        """Config ni fayl dan yuklash"""
        try:
            with open(file_path, 'r') as f:
                loaded_config = json.load(f)
            
            # Deep merge
            self._deep_update(self._config, loaded_config)
            
        except Exception as e:
            raise ValueError(f"Config faylini yuklash xatosi {file_path}: {str(e)}")
    
    def _deep_update(self, target: Dict, source: Dict):
        """Deep dictionary update"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Barcha config ni olish"""
        return self._config.copy()
    
    def reset_to_defaults(self):
        """Default config ga qayta tiklash"""
        self._config = asdict(SystemConfig())