"""
Tizim konfiguratsiya fayli - Hybrid Quantum Forex Arbitrage
"""
import os
from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class QuantumConfig:
    """Quantum processor konfiguratsiyasi"""
    backend_name: str = "qasm_simulator"
    quantum_registers: int = 20
    classical_registers: int = 20
    shots: int = 1024
    max_circuits: int = 100
    circuit_timeout: int = 30

@dataclass
class ForexConfig:
    """Forex data konfiguratsiyasi"""
    api_base_url: str = "https://api.fxapi.com"
    api_key: str = os.getenv("FOREX_API_KEY", "demo_key")
    update_interval: float = 0.1  # 100ms
    max_history: int = 1000
    supported_currencies: List[str] = None
    min_arbitrage_threshold: float = 0.0001  # 0.01%
    
    def __post_init__(self):
        if self.supported_currencies is None:
            self.supported_currencies = [
                'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD',
                'CNY', 'HKD', 'SGD', 'KRW', 'INR', 'BRL', 'MXN', 'ZAR',
                'NOK', 'SEK', 'DKK', 'PLN', 'CZK', 'HUF', 'RON', 'BGN',
                'HRK', 'RSD', 'TRY', 'ILS', 'AED', 'SAR', 'QAR', 'KWD',
                'BHD', 'JOD', 'EGP', 'MAD', 'NGN', 'KES', 'GHS', 'XOF'
            ]

@dataclass
class ArbitrageConfig:
    """Arbitrage konfiguratsiyasi"""
    min_profit_threshold: float = 0.0005  # 0.05%
    max_execution_time: float = 0.5  # 500ms
    risk_limit: float = 0.1  # 10% of portfolio
    max_position_size: float = 1000000  # $1M
    leverage: float = 10.0
    stop_loss: float = 0.02  # 2%

@dataclass
class SystemConfig:
    """Tizim konfiguratsiyasi"""
    quantum_config: QuantumConfig = QuantumConfig()
    forex_config: ForexConfig = ForexConfig()
    arbitrage_config: ArbitrageConfig = ArbitrageConfig()
    
    # Performance settings
    max_workers: int = 8
    memory_limit_mb: int = 2048
    log_level: str = "INFO"
    enable_monitoring: bool = True
    enable_audit: bool = True
    
    # Database settings
    db_path: str = "data/hybrid_quantum_forex.db"
    
    class Config:
        arbitrary_types_allowed = True

# Global konfiguratsiya instance
config = SystemConfig()

# Currency pairs and triangular arbitrage configuration
CURRENCY_PAIRS = {
    # Major pairs
    'EURUSD': {'base': 'EUR', 'quote': 'USD'},
    'GBPUSD': {'base': 'GBP', 'quote': 'USD'},
    'USDJPY': {'base': 'USD', 'quote': 'JPY'},
    'USDCHF': {'base': 'USD', 'quote': 'CHF'},
    'USDCAD': {'base': 'USD', 'quote': 'CAD'},
    'AUDUSD': {'base': 'AUD', 'quote': 'USD'},
    'NZDUSD': {'base': 'NZD', 'quote': 'USD'},
    
    # Cross pairs
    'EURJPY': {'base': 'EUR', 'quote': 'JPY'},
    'EURGBP': {'base': 'EUR', 'quote': 'GBP'},
    'EURCHF': {'base': 'EUR', 'quote': 'CHF'},
    'GBPJPY': {'base': 'GBP', 'quote': 'JPY'},
    'GBPCHF': {'base': 'GBP', 'quote': 'CHF'},
    'CHFJPY': {'base': 'CHF', 'quote': 'JPY'},
    
    # Minor pairs
    'AUDCAD': {'base': 'AUD', 'quote': 'CAD'},
    'AUDCHF': {'base': 'AUD', 'quote': 'CHF'},
    'AUDJPY': {'base': 'AUD', 'quote': 'JPY'},
    'AUDNZD': {'base': 'AUD', 'quote': 'NZD'},
    'CADCHF': {'base': 'CAD', 'quote': 'CHF'},
    'CADJPY': {'base': 'CAD', 'quote': 'JPY'},
    'CHFNOK': {'base': 'CHF', 'quote': 'NOK'},
    'CHFNZD': {'base': 'CHF', 'quote': 'NZD'},
    'EURAUD': {'base': 'EUR', 'quote': 'AUD'},
    'EURCAD': {'base': 'EUR', 'quote': 'CAD'},
    'EURCHF': {'base': 'EUR', 'quote': 'CHF'},
    'EURCZK': {'base': 'EUR', 'quote': 'CZK'},
    'EURDKK': {'base': 'EUR', 'quote': 'DKK'},
    'EURHUF': {'base': 'EUR', 'quote': 'HUF'},
    'EURMXN': {'base': 'EUR', 'quote': 'MXN'},
    'EURNOK': {'base': 'EUR', 'quote': 'NOK'},
    'EURNZD': {'base': 'EUR', 'quote': 'NZD'},
    'EURPLN': {'base': 'EUR', 'quote': 'PLN'},
    'EURRON': {'base': 'EUR', 'quote': 'RON'},
    'EURSEK': {'base': 'EUR', 'quote': 'SEK'},
    'EURSGD': {'base': 'EUR', 'quote': 'SGD'},
    'EURTRY': {'base': 'EUR', 'quote': 'TRY'},
    'EURZAR': {'base': 'EUR', 'quote': 'ZAR'},
    'GBPAUD': {'base': 'GBP', 'quote': 'AUD'},
    'GBPCAD': {'base': 'GBP', 'quote': 'CAD'},
    'GBPCZK': {'base': 'GBP', 'quote': 'CZK'},
    'GBPDKK': {'base': 'GBP', 'quote': 'DKK'},
    'GBPHUF': {'base': 'GBP', 'quote': 'HUF'},
    'GBPMXN': {'base': 'GBP', 'quote': 'MXN'},
    'GBPNOK': {'base': 'GBP', 'quote': 'NOK'},
    'GBPNZD': {'base': 'GBP', 'quote': 'NZD'},
    'GBPPLN': {'base': 'GBP', 'quote': 'PLN'},
    'GBPRON': {'base': 'GBP', 'quote': 'RON'},
    'GBPSEK': {'base': 'GBP', 'quote': 'SEK'},
    'GBPSGD': {'base': 'GBP', 'quote': 'SGD'},
    'GBPTRY': {'base': 'GBP', 'quote': 'TRY'},
    'GBPZAR': {'base': 'GBP', 'quote': 'ZAR'},
    'JPYCAD': {'base': 'JPY', 'quote': 'CAD'},
    'JPYCHF': {'base': 'JPY', 'quote': 'CHF'},
    'JPYNZD': {'base': 'JPY', 'quote': 'NZD'},
    'JPYSEK': {'base': 'JPY', 'quote': 'SEK'},
    'NOKSEK': {'base': 'NOK', 'quote': 'SEK'},
    'NZDCAD': {'base': 'NZD', 'quote': 'CAD'},
    'NZDCHF': {'base': 'NZD', 'quote': 'CHF'},
    'NZDJPY': {'base': 'NZD', 'quote': 'JPY'},
    'NZDNOK': {'base': 'NZD', 'quote': 'NOK'},
    'NZDSEK': {'base': 'NZD', 'quote': 'SEK'},
    'NZDSGD': {'base': 'NZD', 'quote': 'SGD'},
    'NZDTRY': {'base': 'NZD', 'quote': 'TRY'},
    'SEKCHF': {'base': 'SEK', 'quote': 'CHF'},
    'SGDJPY': {'base': 'SGD', 'quote': 'JPY'},
    'SGDCHF': {'base': 'SGD', 'quote': 'CHF'}
}

# Time zones for different markets
TIMEZONES = {
    'NEW_YORK': 'America/New_York',
    'LONDON': 'Europe/London',
    'TOKYO': 'Asia/Tokyo',
    'SYDNEY': 'Australia/Sydney',
    'AUCKLAND': 'Pacific/Auckland',
    'HONG_KONG': 'Asia/Hong_Kong',
    'SINGAPORE': 'Asia/Singapore',
    'SHANGHAI': 'Asia/Shanghai',
    'MUMBAI': 'Asia/Kolkata',
    'DUBAI': 'Asia/Dubai',
    'JERUSALEM': 'Asia/Jerusalem',
    'MOSCOW': 'Europe/Moscow',
    'ZURICH': 'Europe/Zurich',
    'STOCKHOLM': 'Europe/Stockholm',
    'OSLO': 'Europe/Oslo',
    'COPENHAGEN': 'Europe/Copenhagen',
    'PRAGUE': 'Europe/Prague',
    'BUDAPEST': 'Europe/Budapest',
    'WARSAW': 'Europe/Warsaw',
    'BUCHAREST': 'Europe/Bucharest'
}