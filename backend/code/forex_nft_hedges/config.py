"""
Forex Hedging NFT va Quantum Portfolio Optimization
Konfiguratsiya va sozlamalar
"""

import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class ForexPair(Enum):
    """Asosiy valyuta juftliklari"""
    EURUSD = "EUR/USD"
    GBPUSD = "GBP/USD"
    USDJPY = "USD/JPY"
    USDCHF = "USD/CHF"
    AUDUSD = "AUD/USD"
    USDCAD = "USD/CAD"
    NZDUSD = "NZD/USD"
    EURJPY = "EUR/JPY"
    EURGBP = "EUR/GBP"
    GBPJPY = "GBP/JPY"

class HedgeType(Enum):
    """Hedge turlari"""
    PAIR_HEDGE = "pair_hedge"
    CROSS_CURRENCY = "cross_currency"
    VOLATILITY = "volatility_hedge"
    CARRY_TRADE = "carry_trade"
    CORRELATION = "correlation_hedge"

class MarketRegime(Enum):
    """Bozor rejimlari"""
    TRENDING = "trending"
    RANGING = "ranging"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    STRESS = "stress_regime"

class QuantumStrategy(Enum):
    """Quantum strategiya turlari"""
    QUANTUM_ARBITRAGE = "quantum_arbitrage"
    MULTI_CURRENCY_PORTFOLIO = "multi_currency_portfolio"
    VOLATILITY_MODELING = "quantum_volatility_modeling"
    SUPERPOSITION_STRATEGY = "superposition_strategy"
    QUANTUM_CORRELATION = "quantum_correlation"

@dataclass
class ForexHedgeConfig:
    """Forex hedge konfiguratsiyasi"""
    hedge_ratio: float = 0.7
    max_position_size: float = 1000000
    min_margin_requirement: float = 0.02
    volatility_threshold: float = 0.15
    correlation_threshold: float = 0.8
    rebalance_frequency: int = 24  # soat
    quantum_advantage: bool = True

@dataclass
class NFTMetadata:
    """NFT metadata struktura"""
    token_id: str
    hedge_type: HedgeType
    currency_pair: ForexPair
    creation_time: int
    performance_metrics: Dict
    quantum_enhanced: bool = False
    adaptive_features: bool = True

@dataclass
class QuantumOptimizationConfig:
    """Quantum optimallash konfiguratsiyasi"""
    qubits_used: int = 16
    max_iterations: int = 1000
    convergence_threshold: float = 0.001
    classical_mix_ratio: float = 0.3
    noise_mitigation: bool = True
    variational_ansatz: str = "hardware_efficient"

class ConfigManager:
    """Konfiguratsiya boshqaruvchisi"""
    
    def __init__(self):
        self.forex_pairs = list(ForexPair)
        self.hedge_types = list(HedgeType)
        self.quantum_strategies = list(QuantumStrategy)
        
        # Forex volatility va korrelatsiya ma'lumotlari
        self.volatility_matrix = self._init_volatility_matrix()
        self.correlation_matrix = self._init_correlation_matrix()
        
        # Economic calendar events
        self.economic_events = {
            "central_bank_meetings": 0.5,
            "gdp_releases": 0.3,
            "inflation_data": 0.4,
            "employment_data": 0.35,
            "geopolitical_events": 0.6
        }
        
        # Risk limits
        self.risk_limits = {
            "max_forex_exposure": 0.25,
            "max_quantum_risk": 0.15,
            "max_leverage": 10.0,
            "var_limit": 0.05
        }
    
    def _init_volatility_matrix(self) -> Dict:
        """Volatillik matritsani inicializatsiya qilish"""
        return {
            "EUR/USD": 0.12,
            "GBP/USD": 0.15,
            "USD/JPY": 0.10,
            "USD/CHF": 0.11,
            "AUD/USD": 0.14,
            "USD/CAD": 0.13,
            "NZD/USD": 0.16,
            "EUR/JPY": 0.14,
            "EUR/GBP": 0.11,
            "GBP/JPY": 0.17
        }
    
    def _init_correlation_matrix(self) -> Dict:
        """Korrelatsiya matritsani inicializatsiya qilish"""
        correlations = {}
        for pair1 in self.forex_pairs:
            for pair2 in self.forex_pairs:
                if pair1 == pair2:
                    correlations[pair1.value, pair2.value] = 1.0
                else:
                    # Birlamchi korrelatsiya qiymatlari
                    correlations[pair1.value, pair2.value] = self._get_correlation_value(pair1, pair2)
        return correlations
    
    def _get_correlation_value(self, pair1: ForexPair, pair2: ForexPair) -> float:
        """Valyuta juftliklari orasidagi korrelatsiyani olish"""
        # Asosiy korrelatsiya patternlari
        correlation_patterns = {
            (ForexPair.EURUSD, ForexPair.GBPUSD): 0.75,
            (ForexPair.EURUSD, ForexPair.AUDUSD): 0.70,
            (ForexPair.GBPUSD, ForexPair.AUDUSD): 0.68,
            (ForexPair.USDJPY, ForexPair.USDCHF): 0.65,
            (ForexPair.EURUSD, ForexPair.EURGBP): 0.80,
        }
        
        key = (pair1, pair2)
        reverse_key = (pair2, pair1)
        
        if key in correlation_patterns:
            return correlation_patterns[key]
        elif reverse_key in correlation_patterns:
            return correlation_patterns[reverse_key]
        else:
            return 0.30  # Default korrelatsiya
    
    def get_hedge_config(self, hedge_type: HedgeType) -> ForexHedgeConfig:
        """Hedge turi bo'yicha konfiguratsiya olish"""
        base_config = ForexHedgeConfig()
        
        if hedge_type == HedgeType.PAIR_HEDGE:
            base_config.hedge_ratio = 0.8
            base_config.volatility_threshold = 0.12
        elif hedge_type == HedgeType.CROSS_CURRENCY:
            base_config.hedge_ratio = 0.75
            base_config.correlation_threshold = 0.7
        elif hedge_type == HedgeType.VOLATILITY:
            base_config.hedge_ratio = 0.6
            base_config.volatility_threshold = 0.20
        elif hedge_type == HedgeType.CARRY_TRADE:
            base_config.hedge_ratio = 0.85
            base_config.min_margin_requirement = 0.025
        elif hedge_type == HedgeType.CORRELATION:
            base_config.hedge_ratio = 0.7
            base_config.correlation_threshold = 0.9
        
        return base_config
    
    def get_quantum_config(self, strategy: QuantumStrategy) -> QuantumOptimizationConfig:
        """Quantum strategy bo'yicha konfiguratsiya olish"""
        base_config = QuantumOptimizationConfig()
        
        if strategy == QuantumStrategy.QUANTUM_ARBITRAGE:
            base_config.qubits_used = 8
            base_config.max_iterations = 500
        elif strategy == QuantumStrategy.MULTI_CURRENCY_PORTFOLIO:
            base_config.qubits_used = 16
            base_config.classical_mix_ratio = 0.4
        elif strategy == QuantumStrategy.VOLATILITY_MODELING:
            base_config.qubits_used = 12
            base_config.convergence_threshold = 0.0001
        elif strategy == QuantumStrategy.SUPERPOSITION_STRATEGY:
            base_config.qubits_used = 20
            base_config.noise_mitigation = True
        elif strategy == QuantumStrategy.QUANTUM_CORRELATION:
            base_config.qubits_used = 10
            base_config.variational_ansatz = "two_local"
        
        return base_config

# Global konfiguratsiya instansiyasi
config = ConfigManager()

# Environment variables
ENV = {
    "DATA_FEED_URL": os.getenv("FOREX_DATA_FEED_URL", "wss://api.example.com/forex"),
    "QUANTUM_BACKEND": os.getenv("QUANTUM_BACKEND", "qasm_simulator"),
    "HEDGE_API_KEY": os.getenv("HEDGE_API_KEY", ""),
    "BLOCKCHAIN_RPC": os.getenv("BLOCKCHAIN_RPC", "https://mainnet.infura.io/v3/"),
    "IPFS_GATEWAY": os.getenv("IPFS_GATEWAY", "https://ipfs.io/ipfs/"),
    "DEVELOPMENT_MODE": os.getenv("DEVELOPMENT_MODE", "true").lower() == "true"
}