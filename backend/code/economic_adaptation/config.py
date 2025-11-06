"""
Economic Adaptation tizimi konfiguratsiyasi.
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

class LogLevel(Enum):
    """Log darajalar."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AdaptationStrategy(Enum):
    """Adaptatsiya strategiyalari."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    ADAPTIVE = "adaptive"

@dataclass
class CycleDetectionConfig:
    """Business cycle detection konfiguratsiyasi."""
    # Cycle detection parametrlari
    min_cycle_length: int = 12  # minimum cycle length in months
    smoothing_window: int = 3   # moving average window
    threshold_sensitivity: float = 0.5  # turning point detection sensitivity
    recession_threshold: float = -0.02  # GDP decline threshold for recession
    expansion_threshold: float = 0.02   # GDP growth threshold for expansion
    
    # Leading indicators weights
    leading_indicators_weights: Dict[str, float] = None
    
    def __post_init__(self):
        if self.leading_indicators_weights is None:
            self.leading_indicators_weights = {
                'yield_curve': 0.25,
                'consumer_confidence': 0.20,
                'industrial_production': 0.15,
                'manufacturing_pmi': 0.15,
                'unemployment_rate': 0.15,
                'consumer_expectations': 0.10
            }

@dataclass
class MacroEconomicConfig:
    """Makro-ekonomik adaptatsiya konfiguratsiyasi."""
    # Interest rate cycle
    rate_cycle_sensitivity: float = 0.7
    rate_threshold_high: float = 0.05
    rate_threshold_low: float = 0.02
    rate_cycle_history: int = 24  # months
    
    # Inflation cycle
    inflation_target: float = 0.02  # 2% target
    inflation_threshold: float = 0.01
    inflation_persistence: int = 6  # months
    
    # Credit cycle
    credit_volume_threshold: float = 0.15
    credit_growth_sensitivity: float = 0.8
    credit_stress_indicators: List[str] = None
    
    def __post_init__(self):
        if self.credit_stress_indicators is None:
            self.credit_stress_indicators = [
                'credit_to_gdp',
                'credit_growth',
                'default_rates',
                'bank_lending_survey'
            ]

@dataclass
class LearningSystemConfig:
    """Self-learning tizimi konfiguratsiyasi."""
    # Multi-scale learning
    intraday_learning_frequency: int = 60  # minutes
    daily_learning_frequency: int = 1      # daily
    weekly_learning_frequency: int = 1     # weekly
    monthly_learning_frequency: int = 1    # monthly
    
    # Meta-learning parameters
    meta_learning_window: int = 60  # days
    adaptation_rate: float = 0.1
    knowledge_decay_factor: float = 0.95
    
    # Model selection and hyperparameter tuning
    model_selection_strategy: str = "cross_validation"
    hyperparameter_optimization: str = "bayesian"
    ensemble_size: int = 5
    
    # Performance tracking
    performance_window: int = 252  # trading days
    benchmark_comparison: str = "market"
    
    # Learning rate scheduling
    initial_learning_rate: float = 0.001
    min_learning_rate: float = 0.0001
    decay_rate: float = 0.95
    decay_steps: int = 1000

@dataclass
class PerformanceConfig:
    """Performance optimization konfiguratsiyasi."""
    # Cycle-adjusted metrics
    cycle_adjusted_alpha: bool = True
    risk_free_rate: float = 0.02
    market_benchmark: str = "SP500"
    
    # Performance attribution
    attribution_period: int = 12  # months
    attribution_factors: List[str] = None
    
    # Benchmark settings
    primary_benchmark: str = "SP500"
    secondary_benchmarks: List[str] = None
    
    # Risk metrics
    var_confidence_levels: List[float] = None
    expected_shortfall_levels: List[float] = None
    
    def __post_init__(self):
        if self.attribution_factors is None:
            self.attribution_factors = [
                'market',
                'economic_cycle',
                'sector_rotation',
                'factor_exposure'
            ]
        
        if self.secondary_benchmarks is None:
            self.secondary_benchmarks = ['QQQ', 'IWM', 'EFA']
        
        if self.var_confidence_levels is None:
            self.var_confidence_levels = [0.95, 0.99]
        
        if self.expected_shortfall_levels is None:
            self.expected_shortfall_levels = [0.95, 0.99]

@dataclass
class DataConfig:
    """Ma'lumotlar konfiguratsiyasi."""
    # Data sources
    data_sources: Dict[str, Dict[str, str]] = None
    
    # Data quality thresholds
    missing_data_threshold: float = 0.05
    outlier_threshold: float = 3.0
    data_quality_score: float = 0.8
    
    # Update frequencies
    real_time_frequency: int = 1  # seconds
    batch_update_frequency: int = 3600  # seconds
    historical_data_lookback: int = 2520  # days
    
    # Data retention
    data_retention_days: int = 1825  # 5 years
    backup_frequency: int = 86400  # daily
    
    def __post_init__(self):
        if self.data_sources is None:
            self.data_sources = {
                'yahoo_finance': {
                    'api_key': os.getenv('YAHOO_API_KEY', ''),
                    'base_url': 'https://query1.finance.yahoo.com/v8/finance/chart/'
                },
                'fred': {
                    'api_key': os.getenv('FRED_API_KEY', ''),
                    'base_url': 'https://api.stlouisfed.org/fred/series/observations'
                },
                'bloomberg': {
                    'api_key': os.getenv('BLOOMBERG_API_KEY', ''),
                    'base_url': 'https://api.bloomberg.com/v1/'
                }
            }

@dataclass
class IntegrationConfig:
    """System integration konfiguratsiyasi."""
    # Integration settings
    quantum_portfolio_enabled: bool = True
    risk_management_enabled: bool = True
    market_analysis_enabled: bool = True
    hft_engine_enabled: bool = True
    
    # API endpoints
    api_endpoints: Dict[str, str] = None
    
    # Real-time processing
    real_time_enabled: bool = True
    processing_latency_ms: int = 10
    batch_size: int = 1000
    
    # Cache settings
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    cache_size_mb: int = 512
    
    def __post_init__(self):
        if self.api_endpoints is None:
            self.api_endpoints = {
                'quantum_portfolio': 'http://localhost:8001/api/v1/',
                'risk_management': 'http://localhost:8002/api/v1/',
                'market_analysis': 'http://localhost:8003/api/v1/',
                'hft_engine': 'http://localhost:8004/api/v1/'
            }

@dataclass
class SystemConfig:
    """Asosiy tizim konfiguratsiyasi."""
    # Environment
    environment: str = os.getenv('ENVIRONMENT', 'development')
    debug_mode: bool = False
    log_level: LogLevel = LogLevel.INFO
    
    # Tizim nomlari
    system_name: str = "Economic Adaptation System"
    version: str = "1.0.0"
    
    # Component configurations
    cycle_detection: CycleDetectionConfig = None
    macro_economic: MacroEconomicConfig = None
    learning_system: LearningSystemConfig = None
    performance: PerformanceConfig = None
    data: DataConfig = None
    integration: IntegrationConfig = None
    
    # Strategy settings
    adaptation_strategy: AdaptationStrategy = AdaptationStrategy.MODERATE
    risk_tolerance: float = 0.15  # 15% max drawdown
    max_position_size: float = 0.20  # 20% max per position
    
    # File paths
    data_path: str = "./data"
    logs_path: str = "./logs"
    models_path: str = "./models"
    output_path: str = "./output"
    
    def __post_init__(self):
        if self.cycle_detection is None:
            self.cycle_detection = CycleDetectionConfig()
        
        if self.macro_economic is None:
            self.macro_economic = MacroEconomicConfig()
        
        if self.learning_system is None:
            self.learning_system = LearningSystemConfig()
        
        if self.performance is None:
            self.performance = PerformanceConfig()
        
        if self.data is None:
            self.data = DataConfig()
        
        if self.integration is None:
            self.integration = IntegrationConfig()
        
        # Create directories if they don't exist
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.logs_path, exist_ok=True)
        os.makedirs(self.models_path, exist_ok=True)
        os.makedirs(self.output_path, exist_ok=True)

# Global konfiguratsiya obyekti
config = SystemConfig()

def get_config() -> SystemConfig:
    """Global konfiguratsiya obyektini qaytaradi."""
    return config

def update_config(**kwargs) -> None:
    """Global konfiguratsiyani yangilaydi."""
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)

def get_section_config(section: str) -> Optional[Any]:
    """Ma'lum bo'lim konfiguratsiyasini qaytaradi."""
    if hasattr(config, section):
        return getattr(config, section)
    return None