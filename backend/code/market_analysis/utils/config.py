"""
Market Analysis Configuration
==========================

Tizim konfiguratsiyasi va sozlamalari.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from enum import Enum
import pandas as pd
import numpy as np
from datetime import datetime, time


class MarketType(Enum):
    """Bozor turlari"""
    FOREX = "forex"
    METALS = "metals"
    CRYPTO = "crypto"
    EQUITIES = "equities"
    COMMODITIES = "commodities"


class TimeFrame(Enum):
    """Vaqt freymlari"""
    TICK = "tick"
    S1 = "1s"
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"
    MN1 = "1M"


class DataQuality(Enum):
    """Ma'lumotlar sifati"""
    EXCELLENT = 5
    GOOD = 4
    FAIR = 3
    POOR = 2
    VERY_POOR = 1


@dataclass
class MarketConfig:
    """Bozor konfiguratsiyasi"""
    
    # Umumiy sozlamalar
    market_type: MarketType
    symbol: str
    base_currency: str
    quote_currency: str
    tick_size: float
    min_size: float
    max_size: float
    maker_fee: float = 0.0001
    taker_fee: float = 0.0003
    
    # Liquidity sozlamalari
    max_slippage: float = 0.01  # 1%
    min_liquidity: float = 10000
    price_impact_threshold: float = 0.005  # 0.5%
    
    # Market hours (UTC)
    market_open: time = time(0, 0)
    market_close: time = time(23, 59)
    trading_days: List[int] = None  # 0=Monday, 6=Sunday
    
    # Volatility sozlamalari
    volatility_lookback: int = 20
    high_volatility_threshold: float = 2.0
    low_volatility_threshold: float = 0.5
    
    def __post_init__(self):
        if self.trading_days is None:
            self.trading_days = list(range(0, 7))  # Barcha kunlar


@dataclass
class SessionConfig:
    """Trading session konfiguratsiyasi"""
    
    name: str
    start_time: time
    end_time: time
    timezone: str
    volatility_multiplier: float = 1.0
    liquidity_multiplier: float = 1.0


# FOREX session configurations
FOREX_SESSIONS = {
    'asian': SessionConfig(
        name='Asian',
        start_time=time(0, 0),  # 00:00 UTC (Tokyo open)
        end_time=time(9, 0),    # 09:00 UTC
        timezone='Asia/Tokyo',
        volatility_multiplier=0.7,
        liquidity_multiplier=0.8
    ),
    'european': SessionConfig(
        name='European', 
        start_time=time(8, 0),  # 08:00 UTC (London open)
        end_time=time(17, 0),   # 17:00 UTC
        timezone='Europe/London',
        volatility_multiplier=1.2,
        liquidity_multiplier=1.3
    ),
    'american': SessionConfig(
        name='American',
        start_time=time(13, 0), # 13:00 UTC (NY open)
        end_time=time(22, 0),   # 22:00 UTC
        timezone='America/New_York',
        volatility_multiplier=1.4,
        liquidity_multiplier=1.2
    )
}


@dataclass
class RiskConfig:
    """Risk management konfiguratsiyasi"""
    
    max_position_size: float = 0.1  # 10% of capital
    stop_loss_pct: float = 0.02     # 2%
    take_profit_pct: float = 0.04   # 4%
    max_drawdown: float = 0.15      # 15%
    var_confidence: float = 0.95    # 95% VaR
    sharpe_target: float = 1.5
    max_correlation: float = 0.7


@dataclass
class StrategyConfig:
    """Strategy konfiguratsiyasi"""
    
    name: str
    enabled: bool = True
    min_trades: int = 10
    performance_threshold: float = 0.05  # 5% required return
    max_drawdown: float = 0.20          # 20% max drawdown
    sharpe_ratio: float = 1.0
    win_rate: float = 0.55              # 55% minimum win rate
    risk_reward_ratio: float = 1.5      # 1:1.5 risk/reward


# Standard configurations
STANDARD_CONFIGS = {
    'EURUSD': MarketConfig(
        market_type=MarketType.FOREX,
        symbol='EURUSD',
        base_currency='EUR',
        quote_currency='USD',
        tick_size=0.0001,
        min_size=0.01,
        max_size=1000000,
        volatility_lookback=20,
        max_slippage=0.002  # 0.2%
    ),
    
    'GBPUSD': MarketConfig(
        market_type=MarketType.FOREX,
        symbol='GBPUSD',
        base_currency='GBP',
        quote_currency='USD',
        tick_size=0.0001,
        min_size=0.01,
        max_size=1000000,
        volatility_lookback=20,
        max_slippage=0.002
    ),
    
    'XAUUSD': MarketConfig(
        market_type=MarketType.METALS,
        symbol='XAUUSD',
        base_currency='XAU',
        quote_currency='USD',
        tick_size=0.01,
        min_size=0.01,
        max_size=100,
        volatility_lookback=30,
        max_slippage=0.003  # 0.3% - gold can be more volatile
    ),
    
    'XAGUSD': MarketConfig(
        market_type=MarketType.METALS,
        symbol='XAGUSD',
        base_currency='XAG',
        quote_currency='USD',
        tick_size=0.001,
        min_size=0.1,
        max_size=1000,
        volatility_lookback=30,
        max_slippage=0.004  # 0.4% - silver more volatile
    )
}


class ConfigManager:
    """Configuration management class"""
    
    def __init__(self):
        self.configs = {}
        self.sessions = FOREX_SESSIONS
        self.default_risk = RiskConfig()
        self.load_standard_configs()
    
    def load_standard_configs(self):
        """Standard konfiguratsiyalarni yuklash"""
        self.configs.update(STANDARD_CONFIGS)
    
    def get_config(self, symbol: str) -> Optional[MarketConfig]:
        """Symbol uchun konfiguratsiyani olish"""
        return self.configs.get(symbol.upper())
    
    def add_config(self, config: MarketConfig):
        """Yangi konfiguratsiya qo'shish"""
        self.configs[config.symbol.upper()] = config
    
    def get_session(self, session_name: str) -> Optional[SessionConfig]:
        """Session konfiguratsiyasini olish"""
        return self.sessions.get(session_name.lower())
    
    def get_active_sessions(self, current_time: datetime) -> List[SessionConfig]:
        """Joriy vaqtda faol sessiyalarni aniqlash"""
        active = []
        for session in self.sessions.values():
            if self._is_session_active(current_time, session):
                active.append(session)
        return active
    
    def _is_session_active(self, current_time: datetime, session: SessionConfig) -> bool:
        """Session faol yoki yo'qligini tekshirish"""
        current_time_only = current_time.time()
        return session.start_time <= current_time_only <= session.end_time


# Global instance
config_manager = ConfigManager()