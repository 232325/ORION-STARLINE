"""
Quantum Pricing va Portfolio Optimization Konfiguratsiya
"""
import os
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class QuantumBackendType(Enum):
    """Quantum backend turlari"""
    QISKIT_AER = "qiskit_aer"
    IBM_QUANTUM = "ibm_quantum"
    CIRQ_SIMULATOR = "cirq_simulator"
    PennyLane = "pennylane"

class MetalType(Enum):
    """Metall turlari"""
    GOLD = "gold"
    SILVER = "silver"
    PLATINUM = "platinum"
    PALLADIUM = "palladium"

class AssetType(Enum):
    """Aktiv turlari"""
    STOCKS = "stocks"
    FOREX = "forex"
    METALS = "metals"
    BONDS = "bonds"
    COMMODITIES = "commodities"

@dataclass
class QuantumConfig:
    """Quantum konfiguratsiya"""
    backend_type: QuantumBackendType = QuantumBackendType.QISKIT_AER
    max_qubits: int = 20
    shots: int = 1024
    optimization_level: int = 1
    error_mitigation: bool = True
    noise_model: bool = False
    transpilation: bool = True

@dataclass
class MetalFuturesConfig:
    """Metal Futures konfiguratsiya"""
    metals: List[MetalType] = None
    contract_months: List[int] = None
    initial_price: Dict[MetalType, float] = None
    volatility: Dict[MetalType, float] = None
    risk_free_rate: float = 0.02
    dividend_yield: float = 0.0

    def __post_init__(self):
        if self.metals is None:
            self.metals = [MetalType.GOLD, MetalType.SILVER, MetalType.PLATINUM, MetalType.PALLADIUM]
        
        if self.contract_months is None:
            self.contract_months = [3, 6, 9, 12]  # Quarterly contracts
        
        if self.initial_price is None:
            self.initial_price = {
                MetalType.GOLD: 2000.0,     # USD per troy oz
                MetalType.SILVER: 25.0,     # USD per troy oz
                MetalType.PLATINUM: 1000.0, # USD per troy oz
                MetalType.PALLADIUM: 2000.0 # USD per troy oz
            }
        
        if self.volatility is None:
            self.volatility = {
                MetalType.GOLD: 0.20,       # 20% annual volatility
                MetalType.SILVER: 0.25,     # 25% annual volatility
                MetalType.PLATINUM: 0.30,   # 30% annual volatility
                MetalType.PALLADIUM: 0.35   # 35% annual volatility
            }

@dataclass
class PortfolioConfig:
    """Portfolio optimizatsiya konfiguratsiyasi"""
    risk_tolerance: float = 0.15  # 15% maximum risk
    target_return: float = 0.12   # 12% target return
    max_weights: float = 0.40     # 40% maximum weight per asset
    rebalance_frequency: int = 30 # days
    min_assets: int = 3
    max_assets: int = 20
    correlation_threshold: float = 0.80  # 80% correlation threshold

@dataclass
class MarketConfig:
    """Bozor konfiguratsiyasi"""
    trading_hours: Dict[str, tuple] = None
    liquidity_thresholds: Dict[str, float] = None
    transaction_costs: Dict[str, float] = None
    market_impact: float = 0.001  # 0.1% market impact

    def __post_init__(self):
        if self.trading_hours is None:
            self.trading_hours = {
                "US": (9, 30, 16, 0),    # 9:30 AM - 4:00 PM EST
                "LONDON": (8, 0, 17, 0), # 8:00 AM - 5:00 PM GMT
                "TOKYO": (9, 0, 15, 0),  # 9:00 AM - 3:00 PM JST
                "HONG_KONG": (9, 30, 16, 0) # 9:30 AM - 4:00 PM HKT
            }
        
        if self.liquidity_thresholds is None:
            self.liquidity_thresholds = {
                "US": 1000000,    # $1M minimum liquidity
                "LONDON": 500000, # £500K minimum liquidity
                "TOKYO": 100000000, # ¥100M minimum liquidity
                "HONG_KONG": 8000000 # HK$8M minimum liquidity
            }
        
        if self.transaction_costs is None:
            self.transaction_costs = {
                "US": 0.001,      # 0.1% transaction cost
                "LONDON": 0.0015, # 0.15% transaction cost
                "TOKYO": 0.002,   # 0.2% transaction cost
                "HONG_KONG": 0.0015 # 0.15% transaction cost
            }

class QuantumPricingConfig:
    """Asosiy konfiguratsiya"""
    quantum: QuantumConfig = QuantumConfig()
    metals: MetalFuturesConfig = MetalFuturesConfig()
    portfolio: PortfolioConfig = PortfolioConfig()
    market: MarketConfig = MarketConfig()
    
    # API Konfiguratsiya
    data_provider_api_key: str = os.getenv("DATA_PROVIDER_API_KEY", "your_api_key_here")
    ibm_quantum_api_key: str = os.getenv("IBM_QUANTUM_API_KEY", "your_ibm_key_here")
    
    # Database Konfiguratsiya
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///quantum_portfolio.db")
    
    # Logging Konfiguratsiya
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "quantum_portfolio.log")
    
    # Performance Konfiguratsiya
    max_workers: int = int(os.getenv("MAX_WORKERS", "4"))
    cache_size: int = int(os.getenv("CACHE_SIZE", "1000"))
    timeout_seconds: int = int(os.getenv("TIMEOUT_SECONDS", "300"))
    
    @classmethod
    def load_from_env(cls):
        """Environment variables dan konfiguratsiyani yuklash"""
        config = cls()
        
        # Environment variables larni sozlash
        if os.getenv("QUANTUM_BACKEND"):
            config.quantum.backend_type = QuantumBackendType(os.getenv("QUANTUM_BACKEND"))
        
        if os.getenv("QUANTUM_SHOTS"):
            config.quantum.shots = int(os.getenv("QUANTUM_SHOTS"))
        
        if os.getenv("RISK_TOLERANCE"):
            config.portfolio.risk_tolerance = float(os.getenv("RISK_TOLERANCE"))
        
        return config
    
    @classmethod
    def get_config(cls, config_path: str = None):
        """Konfiguratsiyani yuklash"""
        if config_path and os.path.exists(config_path):
            # JSON config faylidan yuklash mumkin
            import json
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            # Bu qismda config_data ni processing qilish kerak
            pass
        
        # Environment variables dan yuklash
        return cls.load_from_env()

# Global konfiguratsiya instance
config = QuantumPricingConfig.get_config()

# Konfiguratsiya constantalari
QUANTUM_CIRCUIT_DEPTH = 5
MAX_PORTFOLIO_SIZE = 100
CACHE_TTL = 3600  # 1 hour cache
BATCH_SIZE = 100

# Risk management konstantalari
MAX_DAILY_LOSS = 0.05  # 5% maximum daily loss
MAX_POSITION_SIZE = 0.20  # 20% maximum position size
MIN_PF_VOLATILITY = 0.10  # 10% minimum portfolio volatility

# Performance monitoring
PERFORMANCE_METRICS = [
    'sharpe_ratio',
    'max_drawdown',
    'alpha',
    'beta',
    'var_95',
    'cvar_95',
    'information_ratio',
    'calmar_ratio'
]

# Metal correlation matrix (annual)
METAL_CORRELATIONS = {
    (MetalType.GOLD, MetalType.SILVER): 0.70,
    (MetalType.GOLD, MetalType.PLATINUM): 0.60,
    (MetalType.GOLD, MetalType.PALLADIUM): 0.50,
    (MetalType.SILVER, MetalType.PLATINUM): 0.80,
    (MetalType.SILVER, MetalType.PALLADIUM): 0.60,
    (MetalType.PLATINUM, MetalType.PALLADIUM): 0.75,
}

# Quantum algorithm parameters
QUANTUM_ALGORITHMS = {
    'vqe': {
        'max_iterations': 100,
        'tolerance': 1e-6,
        'initial_point': None,
        'ansatz_type': 'hardware_efficient'
    },
    'qaoa': {
        'max_layers': 10,
        'parameter_bounds': [[0, 2 * 3.14159] for _ in range(20)]
    },
    'quantum_annealing': {
        'num_reads': 1024,
        'annealing_time': 20,
        'chain_strength': None
    }
}