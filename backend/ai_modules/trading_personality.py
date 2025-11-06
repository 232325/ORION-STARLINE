"""
Trading Personality Engine
=========================

Ushbu modul treyderlarning shaxsiy xarakteristikalarini aniqlaydi va 
ularga mos strategiyalar tavsiya qiladi.
"""

from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
import json
from pathlib import Path
import logging

# Personality turlar
class TradingPersonalityType(Enum):
    SCALPER = "scalper"
    DAY_TRADER = "day_trader"
    SWING_TRADER = "swing_trader"
    POSITION_TRADER = "position_trader"
    ALGORITHMIC_TRADER = "algorithmic_trader"
    VALUE_INVESTOR = "value_investor"
    GROWTH_INVESTOR = "growth_investor"
    CONTRARIAN = "contrarian"
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"

# Risk tolerance darajalar
class RiskTolerance(Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

# Timeframe preferences
class TimeframePreference(Enum):
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"

@dataclass
class PersonalityProfile:
    """Treyder shaxsiyat profili"""
    trader_id: str
    personality_type: TradingPersonalityType
    risk_tolerance: RiskTolerance
    timeframe_preference: TimeframePreference
    trading_frequency: float  # kunlik savdolar soni
    avg_holding_time: float   # o'rtacha pozitsiya vaqti (daqiqalarda)
    decision_speed: str       # "fast", "medium", "slow"
    emotional_score: float    # 0-1, emotional stability
    learning_style: str       # "visual", "analytical", "practical"
    information_sources: List[str]
    social_trading_score: float  # 0-1, social trading qiziqishi
    
    # Asosiy metrikalar
    win_rate: float
    avg_profit_per_trade: float
    max_drawdown: float
    sharpe_ratio: float
    
    # Kompensatsiya qilish uchun
    def to_dict(self) -> Dict[str, Any]:
        return {
            'trader_id': self.trader_id,
            'personality_type': self.personality_type.value,
            'risk_tolerance': self.risk_tolerance.value,
            'timeframe_preference': self.timeframe_preference.value,
            'trading_frequency': self.trading_frequency,
            'avg_holding_time': self.avg_holding_time,
            'decision_speed': self.decision_speed,
            'emotional_score': self.emotional_score,
            'learning_style': self.learning_style,
            'information_sources': self.information_sources,
            'social_trading_score': self.social_trading_score,
            'win_rate': self.win_rate,
            'avg_profit_per_trade': self.avg_profit_per_trade,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio
        }

class TradingPersonalityEngine:
    """
    Trading Personality Engine - treyderlarning shaxsiyatini aniqlash
    va mos strategiyalar tavsiya qilish
    """
    
    def __init__(self, data_dir: str = "/workspace/orion-starline/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Personality turlariga mos konfiguratsiyalar
        self.personality_configs = self._load_personality_configs()
        
        # Logging setup
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Profiles saqlash
        self.profiles_path = self.data_dir / "trading_profiles.json"
        self.profiles = self._load_profiles()
    
    def _load_personality_configs(self) -> Dict[str, Dict]:
        """Personality turlariga mos konfiguratsiyalar"""
        return {
            TradingPersonalityType.SCALPER.value: {
                "description": "Qisqa muddatli, yuqori chastotali savdolar",
                "typical_holding_time_min": 1,   # 1 daqiqa
                "typical_holding_time_max": 15,  # 15 daqiqa
                "trades_per_day_min": 20,
                "trades_per_day_max": 200,
                "risk_tolerance": [RiskTolerance.MEDIUM, RiskTolerance.HIGH],
                "timeframes": [TimeframePreference.SECONDS, TimeframePreference.MINUTES],
                "recommended_assets": ["Forex", "Crypto", "Futures"],
                "chart_types": ["Tick", "1m", "5m", "15m"],
                "alert_types": ["Price", "Volume", "Technical"],
                "ui_density": "high"
            },
            
            TradingPersonalityType.DAY_TRADER.value: {
                "description": "Kun ichi pozitsiyalar, o'rta muddat",
                "typical_holding_time_min": 60,   # 1 soat
                "typical_holding_time_max": 480,  # 8 soat
                "trades_per_day_min": 2,
                "trades_per_day_max": 20,
                "risk_tolerance": [RiskTolerance.MEDIUM, RiskTolerance.HIGH],
                "timeframes": [TimeframePreference.MINUTES, TimeframePreference.HOURS],
                "recommended_assets": ["Stocks", "Options", "Crypto"],
                "chart_types": ["1m", "5m", "15m", "1h", "4h"],
                "alert_types": ["Price", "News", "Technical", "Volume"],
                "ui_density": "medium"
            },
            
            TradingPersonalityType.SWING_TRADER.value: {
                "description": "Ko'p kunlik pozitsiyalar",
                "typical_holding_time_min": 1440,   # 1 kun
                "typical_holding_time_max": 10080,  # 1 hafta
                "trades_per_week_min": 1,
                "trades_per_week_max": 10,
                "risk_tolerance": [RiskTolerance.LOW, RiskTolerance.MEDIUM, RiskTolerance.HIGH],
                "timeframes": [TimeframePreference.HOURS, TimeframePreference.DAYS],
                "recommended_assets": ["Stocks", "Commodities", "Indices"],
                "chart_types": ["1h", "4h", "1d", "1w"],
                "alert_types": ["Price", "Technical", "Trend"],
                "ui_density": "medium"
            },
            
            TradingPersonalityType.POSITION_TRADER.value: {
                "description": "Uzun muddatli pozitsiyalar",
                "typical_holding_time_min": 10080,   # 1 hafta
                "typical_holding_time_max": 262980,  # 6 oy
                "trades_per_month_min": 1,
                "trades_per_month_max": 10,
                "risk_tolerance": [RiskTolerance.LOW, RiskTolerance.MEDIUM],
                "timeframes": [TimeframePreference.DAYS, TimeframePreference.WEEKS, TimeframePreference.MONTHS],
                "recommended_assets": ["Stocks", "Bonds", "Real Estate"],
                "chart_types": ["1d", "1w", "1M"],
                "alert_types": ["News", "Earnings", "Fundamental"],
                "ui_density": "low"
            },
            
            TradingPersonalityType.ALGORITHMIC_TRADER.value: {
                "description": "Tizimli, algoritmik savdolar",
                "typical_holding_time_min": 1,
                "typical_holding_time_max": 1440,
                "trades_per_day_min": 1,
                "trades_per_day_max": 1000,
                "risk_tolerance": [RiskTolerance.MEDIUM, RiskTolerance.HIGH],
                "timeframes": [TimeframePreference.SECONDS, TimeframePreference.MINUTES, TimeframePreference.HOURS],
                "recommended_assets": ["All"],
                "chart_types": ["All"],
                "alert_types": ["System", "Performance", "Risk"],
                "ui_density": "high"
            },
            
            TradingPersonalityType.VALUE_INVESTOR.value: {
                "description": "Asosiy tahlilga asoslangan qiymatli sarmoyasi",
                "typical_holding_time_min": 262980,   # 6 oy
                "typical_holding_time_max": 1576800,  # 5 yil
                "trades_per_year_min": 2,
                "trades_per_year_max": 20,
                "risk_tolerance": [RiskTolerance.VERY_LOW, RiskTolerance.LOW],
                "timeframes": [TimeframePreference.WEEKS, TimeframePreference.MONTHS],
                "recommended_assets": ["Stocks", "Bonds", "Real Estate"],
                "chart_types": ["1w", "1M", "1Y"],
                "alert_types": ["Earnings", "Financial", "News"],
                "ui_density": "low"
            },
            
            TradingPersonalityType.GROWTH_INVESTOR.value: {
                "description": "Momentum va o'sish potentsiali bo'yicha",
                "typical_holding_time_min": 262980,   # 6 oy
                "typical_holding_time_max": 525600,   # 1 yil
                "trades_per_year_min": 4,
                "trades_per_year_max": 30,
                "risk_tolerance": [RiskTolerance.MEDIUM, RiskTolerance.HIGH],
                "timeframes": [TimeframePreference.DAYS, TimeframePreference.WEEKS],
                "recommended_assets": ["Growth Stocks", "Tech", "Emerging Markets"],
                "chart_types": ["1d", "1w", "1M"],
                "alert_types": ["Price", "Momentum", "News"],
                "ui_density": "medium"
            },
            
            TradingPersonalityType.CONTRARIAN.value: {
                "description": "Qarshi sentiment bo'yicha savdolar",
                "typical_holding_time_min": 10080,   # 1 hafta
                "typical_holding_time_max": 52560,   # 1 oy
                "trades_per_month_min": 2,
                "trades_per_month_max": 15,
                "risk_tolerance": [RiskTolerance.MEDIUM, RiskTolerance.HIGH],
                "timeframes": [TimeframePreference.DAYS, TimeframePreference.WEEKS],
                "recommended_assets": ["All"],
                "chart_types": ["1d", "1w"],
                "alert_types": ["Sentiment", "News", "Fear/Greed"],
                "ui_density": "medium"
            },
            
            TradingPersonalityType.CONSERVATIVE.value: {
                "description": "Past risk, barqaror daromad",
                "typical_holding_time_min": 262980,   # 6 oy
                "typical_holding_time_max": 2629800,  # 10 yil
                "trades_per_year_min": 1,
                "trades_per_year_max": 8,
                "risk_tolerance": [RiskTolerance.VERY_LOW, RiskTolerance.LOW],
                "timeframes": [TimeframePreference.WEEKS, TimeframePreference.MONTHS],
                "recommended_assets": ["Bonds", "Dividend Stocks", "REITs"],
                "chart_types": ["1w", "1M", "1Y"],
                "alert_types": ["Dividend", "Interest Rate", "News"],
                "ui_density": "low"
            },
            
            TradingPersonalityType.AGGRESSIVE.value: {
                "description": "Yuqori risk, yuqori daromad",
                "typical_holding_time_min": 60,    # 1 soat
                "typical_holding_time_max": 10080, # 1 hafta
                "trades_per_day_min": 5,
                "trades_per_day_max": 50,
                "risk_tolerance": [RiskTolerance.HIGH, RiskTolerance.VERY_HIGH],
                "timeframes": [TimeframePreference.MINUTES, TimeframePreference.HOURS, TimeframePreference.DAYS],
                "recommended_assets": ["Crypto", "Options", "Forex", "Small Cap"],
                "chart_types": ["1m", "5m", "15m", "1h", "1d"],
                "alert_types": ["Price", "Volume", "Leverage", "Margin"],
                "ui_density": "high"
            }
        }
    
    def _load_profiles(self) -> Dict[str, PersonalityProfile]:
        """Mavjud profillarni yuklash"""
        if self.profiles_path.exists():
            try:
                with open(self.profiles_path, 'r') as f:
                    data = json.load(f)
                    profiles = {}
                    for trader_id, profile_data in data.items():
                        profile = PersonalityProfile(
                            trader_id=trader_id,
                            personality_type=TradingPersonalityType(profile_data['personality_type']),
                            risk_tolerance=RiskTolerance(profile_data['risk_tolerance']),
                            timeframe_preference=TimeframePreference(profile_data['timeframe_preference']),
                            trading_frequency=profile_data['trading_frequency'],
                            avg_holding_time=profile_data['avg_holding_time'],
                            decision_speed=profile_data['decision_speed'],
                            emotional_score=profile_data['emotional_score'],
                            learning_style=profile_data['learning_style'],
                            information_sources=profile_data['information_sources'],
                            social_trading_score=profile_data['social_trading_score'],
                            win_rate=profile_data['win_rate'],
                            avg_profit_per_trade=profile_data['avg_profit_per_trade'],
                            max_drawdown=profile_data['max_drawdown'],
                            sharpe_ratio=profile_data['sharpe_ratio']
                        )
                        profiles[trader_id] = profile
                    return profiles
            except Exception as e:
                self.logger.error(f"Profillarni yuklashda xato: {e}")
        return {}
    
    def _save_profiles(self):
        """Profillarni saqlash"""
        try:
            profiles_data = {trader_id: profile.to_dict() 
                           for trader_id, profile in self.profiles.items()}
            with open(self.profiles_path, 'w') as f:
                json.dump(profiles_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Profillarni saqlashda xato: {e}")
    
    def detect_personality(self, 
                          trading_data: Dict[str, Any],
                          behavioral_data: Optional[Dict[str, Any]] = None) -> PersonalityProfile:
        """
        Treyder shaxsiyatini aniqlash
        
        Args:
            trading_data: Savdo ma'lumotlari
            behavioral_data: Xulq-atvor ma'lumotlari
        
        Returns:
            PersonalityProfile: Treyder profili
        """
        try:
            # Asosiy metrikalarni hisoblash
            profile = self._analyze_trading_patterns(trading_data)
            
            # Xulq-atvor ma'lumotlarini qo'shish
            if behavioral_data:
                profile = self._incorporate_behavioral_data(profile, behavioral_data)
            
            # Personality turini aniqlash
            profile.personality_type = self._classify_personality_type(profile)
            
            # Profile saqlash
            self.profiles[profile.trader_id] = profile
            self._save_profiles()
            
            self.logger.info(f"Profile aniqlangan: {profile.trader_id} - {profile.personality_type.value}")
            return profile
            
        except Exception as e:
            self.logger.error(f"Shaxsiyat aniqlashda xato: {e}")
            raise
    
    def _analyze_trading_patterns(self, trading_data: Dict[str, Any]) -> PersonalityProfile:
        """Savdo naqshlarini tahlil qilish"""
        trader_id = trading_data.get('trader_id', 'unknown')
        
        # O'rtacha vaqt oralig'i
        trades = trading_data.get('trades', [])
        if not trades:
            raise ValueError("Savdo ma'lumotlari mavjud emas")
        
        # Holding time tahlili
        holding_times = []
        for trade in trades:
            if 'entry_time' in trade and 'exit_time' in trade:
                entry = datetime.fromisoformat(trade['entry_time'])
                exit_time = datetime.fromisoformat(trade['exit_time'])
                holding_time_min = (exit_time - entry).total_seconds() / 60
                holding_times.append(holding_time_min)
        
        avg_holding_time = np.mean(holding_times) if holding_times else 0
        
        # Trading frequency
        days_active = trading_data.get('days_active', 30)
        trades_per_day = len(trades) / days_active if days_active > 0 else 0
        
        # Performance metrikalar
        win_rate = trading_data.get('win_rate', 0.5)
        avg_profit = trading_data.get('avg_profit_per_trade', 0)
        max_drawdown = trading_data.get('max_drawdown', 0.1)
        sharpe_ratio = trading_data.get('sharpe_ratio', 0)
        
        # Risk tolerance tahlil
        risk_tolerance = self._assess_risk_tolerance(max_drawdown, sharpe_ratio, avg_profit)
        
        # Timeframe preference
        timeframe_pref = self._determine_timeframe_preference(avg_holding_time)
        
        # Decision speed
        decision_speed = self._assess_decision_speed(avg_holding_time, trades_per_day)
        
        return PersonalityProfile(
            trader_id=trader_id,
            personality_type=TradingPersonalityType.DAY_TRADER,  # Keyin aniqlanadi
            risk_tolerance=risk_tolerance,
            timeframe_preference=timeframe_pref,
            trading_frequency=trades_per_day,
            avg_holding_time=avg_holding_time,
            decision_speed=decision_speed,
            emotional_score=0.5,  # Keyin aniqlanadi
            learning_style="analytical",  # Keyin aniqlanadi
            information_sources=[],
            social_trading_score=0.5,  # Keyin aniqlanadi
            win_rate=win_rate,
            avg_profit_per_trade=avg_profit,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio
        )
    
    def _incorporate_behavioral_data(self, 
                                   profile: PersonalityProfile, 
                                   behavioral_data: Dict[str, Any]) -> PersonalityProfile:
        """Xulq-atvor ma'lumotlarini profile qo'shish"""
        # Emotional stability
        if 'emotional_stability' in behavioral_data:
            profile.emotional_score = behavioral_data['emotional_stability']
        
        # Learning style
        if 'learning_style' in behavioral_data:
            profile.learning_style = behavioral_data['learning_style']
        
        # Information sources
        if 'info_sources' in behavioral_data:
            profile.information_sources = behavioral_data['info_sources']
        
        # Social trading interest
        if 'social_trading_score' in behavioral_data:
            profile.social_trading_score = behavioral_data['social_trading_score']
        
        return profile
    
    def _assess_risk_tolerance(self, max_drawdown: float, sharpe_ratio: float, avg_profit: float) -> RiskTolerance:
        """Risk tolerance darajasini baholash"""
        # Yuqori drawdown va past Sharpe ratio - past risk tolerance
        if max_drawdown > 0.3 or sharpe_ratio < 0.5:
            return RiskTolerance.VERY_LOW
        elif max_drawdown > 0.2 or sharpe_ratio < 1.0:
            return RiskTolerance.LOW
        elif max_drawdown < 0.1 and sharpe_ratio > 1.5 and avg_profit > 0:
            return RiskTolerance.HIGH
        elif max_drawdown < 0.05 and sharpe_ratio > 2.0 and avg_profit > 0.05:
            return RiskTolerance.VERY_HIGH
        else:
            return RiskTolerance.MEDIUM
    
    def _determine_timeframe_preference(self, avg_holding_time: float) -> TimeframePreference:
        """Timeframe ustunligini aniqlash"""
        if avg_holding_time < 5:  # 5 daqiqadan kam
            return TimeframePreference.SECONDS
        elif avg_holding_time < 60:  # 1 soatdan kam
            return TimeframePreference.MINUTES
        elif avg_holding_time < 1440:  # 1 kundan kam
            return TimeframePreference.HOURS
        elif avg_holding_time < 10080:  # 1 haftadan kam
            return TimeframePreference.DAYS
        elif avg_holding_time < 262980:  # 6 oydan kam
            return TimeframePreference.WEEKS
        else:
            return TimeframePreference.MONTHS
    
    def _assess_decision_speed(self, avg_holding_time: float, trades_per_day: float) -> str:
        """Qaror qabul qilish tezligini baholash"""
        if avg_holding_time < 30 and trades_per_day > 20:
            return "fast"
        elif avg_holding_time > 1440 and trades_per_day < 1:
            return "slow"
        else:
            return "medium"
    
    def _classify_personality_type(self, profile: PersonalityProfile) -> TradingPersonalityType:
        """Shaxsiyat turini tasniflash"""
        # Holding time va frequency asosida
        if profile.avg_holding_time < 30 and profile.trading_frequency > 20:
            return TradingPersonalityType.SCALPER
        elif profile.avg_holding_time < 480 and profile.trading_frequency > 2:
            return TradingPersonalityType.DAY_TRADER
        elif profile.avg_holding_time < 10080 and profile.trading_frequency > 0.1:
            return TradingPersonalityType.SWING_TRADER
        elif profile.avg_holding_time > 10080:
            return TradingPersonalityType.POSITION_TRADER
        
        # Risk tolerance asosida
        if profile.risk_tolerance == RiskTolerance.VERY_HIGH:
            return TradingPersonalityType.AGGRESSIVE
        elif profile.risk_tolerance == RiskTolerance.VERY_LOW:
            return TradingPersonalityType.CONSERVATIVE
        
        # Decision speed asosida
        if profile.decision_speed == "fast":
            return TradingPersonalityType.ALGORITHMIC_TRADER
        
        # Default
        return TradingPersonalityType.DAY_TRADER
    
    def get_personality_config(self, personality_type: TradingPersonalityType) -> Dict:
        """Personality konfiguratsiyasini olish"""
        return self.personality_configs.get(personality_type.value, {})
    
    def get_recommended_strategies(self, profile: PersonalityProfile) -> List[Dict[str, Any]]:
        """Shaxsiyatga mos strategiyalar tavsiya qilish"""
        config = self.get_personality_config(profile.personality_type)
        
        strategies = []
        
        # Personality asosida strategiyalar
        if profile.personality_type == TradingPersonalityType.SCALPER:
            strategies.extend([
                {
                    "name": "Grid Trading",
                    "description": "Narx oralig'ida savdolar",
                    "timeframe": "1m-5m",
                    "risk_per_trade": 0.005,
                    "take_profit": 0.002,
                    "stop_loss": 0.003
                },
                {
                    "name": "Mean Reversion",
                    "description": "O'rtacha qiymatga qaytish",
                    "timeframe": "1m-15m",
                    "risk_per_trade": 0.01,
                    "take_profit": 0.005,
                    "stop_loss": 0.008
                }
            ])
        
        elif profile.personality_type == TradingPersonalityType.DAY_TRADER:
            strategies.extend([
                {
                    "name": "Breakout Trading",
                    "description": "Kuchli darajalarni buzish",
                    "timeframe": "15m-1h",
                    "risk_per_trade": 0.02,
                    "take_profit": 0.03,
                    "stop_loss": 0.015
                },
                {
                    "name": "Reversal Trading",
                    "description": "Trenlarning o'zgarishini ushlash",
                    "timeframe": "5m-30m",
                    "risk_per_trade": 0.015,
                    "stop_loss": 0.02
                }
            ])
        
        elif profile.personality_type == TradingPersonalityType.SWING_TRADER:
            strategies.extend([
                {
                    "name": "Trend Following",
                    "description": "Trenlarni kuzatish",
                    "timeframe": "4h-1d",
                    "risk_per_trade": 0.03,
                    "take_profit": 0.08,
                    "stop_loss": 0.05
                },
                {
                    "name": "Support/Resistance",
                    "description": "Kuchli darajalarni qo'llab-quvvatlash",
                    "timeframe": "1h-4h",
                    "risk_per_trade": 0.025,
                    "take_profit": 0.06
                }
            ])
        
        elif profile.personality_type == TradingPersonalityType.POSITION_TRADER:
            strategies.extend([
                {
                    "name": "Fundamental Analysis",
                    "description": "Kompaniya tahlili",
                    "timeframe": "1d-1w",
                    "risk_per_trade": 0.05,
                    "take_profit": 0.20,
                    "stop_loss": 0.10
                }
            ])
        
        # Risk tolerance asosida sozlash
        if profile.risk_tolerance == RiskTolerance.VERY_LOW:
            for strategy in strategies:
                strategy["risk_per_trade"] *= 0.5
                strategy["stop_loss"] *= 0.7
        elif profile.risk_tolerance == RiskTolerance.VERY_HIGH:
            for strategy in strategies:
                strategy["risk_per_trade"] *= 1.5
                strategy["take_profit"] *= 1.3
        
        return strategies
    
    def get_ui_customization(self, profile: PersonalityProfile) -> Dict[str, Any]:
        """UI customizatsiyasi tavsiyalari"""
        config = self.get_personality_config(profile.personality_type)
        
        return {
            "layout_style": config.get("ui_density", "medium"),
            "chart_timeframes": config.get("chart_types", ["1m", "5m", "1h"]),
            "alert_preferences": config.get("alert_types", ["Price", "Volume"]),
            "color_scheme": self._get_color_scheme(profile.personality_type),
            "information_density": config.get("ui_density", "medium"),
            "dashboard_widgets": self._get_dashboard_widgets(profile),
            "navigation_style": "quick" if profile.decision_speed == "fast" else "detailed"
        }
    
    def _get_color_scheme(self, personality_type: TradingPersonalityType) -> Dict[str, str]:
        """Shaxsiyatga mos rang sxemasi"""
        color_schemes = {
            TradingPersonalityType.SCALPER: {
                "primary": "#FF6B6B",  # Qizil
                "secondary": "#4ECDC4",  # Turquoise
                "background": "#1A1A1A",  # Qora
                "text": "#FFFFFF"  # Oq
            },
            TradingPersonalityType.DAY_TRADER: {
                "primary": "#4ECDC4",  # Turquoise
                "secondary": "#45B7D1",  # Ko'k
                "background": "#2C3E50",  # Ko'k-kulrang
                "text": "#FFFFFF"
            },
            TradingPersonalityType.SWING_TRADER: {
                "primary": "#96CEB4",  # Yashil
                "secondary": "#FFEAA7",  # Sariq
                "background": "#F8F9FA",  # Oq-kulrang
                "text": "#2D3436"  # Qora-kulrang
            },
            TradingPersonalityType.POSITION_TRADER: {
                "primary": "#6C5CE7",  # Binafsha
                "secondary": "#A29BFE",  # Och binafsha
                "background": "#FFFFFF",  # Oq
                "text": "#2D3436"
            }
        }
        
        return color_schemes.get(personality_type, {
            "primary": "#4ECDC4",
            "secondary": "#45B7D1", 
            "background": "#F8F9FA",
            "text": "#2D3436"
        })
    
    def _get_dashboard_widgets(self, profile: PersonalityProfile) -> List[str]:
        """Dashboard widget tavsiyalari"""
        base_widgets = ["Portfolio Overview", "P&L Chart"]
        
        if profile.personality_type == TradingPersonalityType.SCALPER:
            return base_widgets + [
                "Live Order Book", "Recent Trades", "Tick Chart", 
                "Position Sizing Calculator", "Risk Meter"
            ]
        elif profile.personality_type == TradingPersonalityType.DAY_TRADER:
            return base_widgets + [
                "Market Scanner", "Watchlist", "Time & Sales",
                "Economic Calendar", "Heat Map"
            ]
        elif profile.personality_type == TradingPersonalityType.SWING_TRADER:
            return base_widgets + [
                "Trend Analysis", "Technical Indicators",
                "News Feed", "Analysis Tools"
            ]
        elif profile.personality_type == TradingPersonalityType.POSITION_TRADER:
            return base_widgets + [
                "Fundamental Data", "Earnings Calendar",
                "Sector Performance", "Research Reports"
            ]
        
        return base_widgets
    
    def get_progress_tracking(self, profile: PersonalityProfile) -> Dict[str, Any]:
        """Progress kuzatish sozlamalari"""
        return {
            "key_metrics": [
                "win_rate", "sharpe_ratio", "max_drawdown", 
                "profit_factor", "avg_trade_duration"
            ],
            "milestone_goals": {
                "weekly": {
                    "trades": profile.trading_frequency * 7,
                    "win_rate_improvement": 0.02,
                    "risk_adherence": 0.95
                },
                "monthly": {
                    "profit_target": profile.avg_profit_per_trade * 20,
                    "drawdown_control": 0.1,
                    "consistency_score": 0.8
                }
            },
            "learning_goals": {
                "skill_development": [
                    f"{profile.learning_style.title()} Learning",
                    f"{profile.personality_type.value.title()} Strategies"
                ],
                "social_goals": [
                    "Community Participation" if profile.social_trading_score > 0.6 else None
                ]
            }
        }
    
    def analyze_personality_match(self, profile1: PersonalityProfile, profile2: PersonalityProfile) -> float:
        """Ikki profil o'rtasidagi moslik darajasi (0-1)"""
        score = 0.0
        total_factors = 6
        
        # Personality type
        if profile1.personality_type == profile2.personality_type:
            score += 0.25
        
        # Risk tolerance
        risk_diff = abs(list(RiskTolerance).index(profile1.risk_tolerance) - 
                       list(RiskTolerance).index(profile2.risk_tolerance))
        score += (5 - risk_diff) / 5 * 0.2
        
        # Timeframe preference
        time_diff = abs(list(TimeframePreference).index(profile1.timeframe_preference) - 
                       list(TimeframePreference).index(profile2.timeframe_preference))
        score += (5 - time_diff) / 5 * 0.15
        
        # Decision speed
        if profile1.decision_speed == profile2.decision_speed:
            score += 0.15
        
        # Learning style
        if profile1.learning_style == profile2.learning_style:
            score += 0.1
        
        # Information sources overlap
        sources1 = set(profile1.information_sources)
        sources2 = set(profile2.information_sources)
        if sources1 and sources2:
            overlap = len(sources1.intersection(sources2)) / len(sources1.union(sources2))
            score += overlap * 0.15
        
        return min(score, 1.0)
    
    def suggest_mentor_match(self, profile: PersonalityProfile, available_mentors: List[PersonalityProfile]) -> Optional[PersonalityProfile]:
        """Mentor mosligini topish"""
        if not available_mentors:
            return None
        
        best_match = None
        best_score = 0.0
        
        for mentor in available_mentors:
            # Mentor tajribasi va performance
            mentor_score = self.analyze_personality_match(profile, mentor)
            
            # Performance bonus
            performance_bonus = 0.0
            if mentor.win_rate > 0.6:
                performance_bonus += 0.1
            if mentor.sharpe_ratio > 1.0:
                performance_bonus += 0.1
            if mentor.max_drawdown < 0.1:
                performance_bonus += 0.1
            
            total_score = mentor_score + performance_bonus
            
            if total_score > best_score:
                best_score = total_score
                best_match = mentor
        
        return best_match if best_score > 0.5 else None
    
    def adaptive_personalization(self, profile: PersonalityProfile, new_trading_data: Dict[str, Any]) -> PersonalityProfile:
        """Adaptiv shaxsiyatsozlash - profilni yangilash"""
        try:
            # Yangilanish kerak bo'lgan sohalar
            if 'trades' in new_trading_data:
                trades = new_trading_data['trades']
                if trades:
                    # Holding time yangilash
                    holding_times = []
                    for trade in trades:
                        if 'entry_time' in trade and 'exit_time' in trade:
                            entry = datetime.fromisoformat(trade['entry_time'])
                            exit_time = datetime.fromisoformat(trade['exit_time'])
                            holding_time_min = (exit_time - entry).total_seconds() / 60
                            holding_times.append(holding_time_min)
                    
                    if holding_times:
                        new_avg_holding = np.mean(holding_times)
                        # Smooth update (EMA)
                        profile.avg_holding_time = 0.7 * profile.avg_holding_time + 0.3 * new_avg_holding
            
            # Performance metrikalar yangilash
            if 'performance' in new_trading_data:
                perf = new_trading_data['performance']
                if 'win_rate' in perf:
                    profile.win_rate = 0.8 * profile.win_rate + 0.2 * perf['win_rate']
                if 'avg_profit' in perf:
                    profile.avg_profit_per_trade = 0.8 * profile.avg_profit_per_trade + 0.2 * perf['avg_profit']
                if 'max_drawdown' in perf:
                    profile.max_drawdown = 0.9 * profile.max_drawdown + 0.1 * perf['max_drawdown']
            
            # Personality type re-evalutsiya qilish
            old_type = profile.personality_type
            new_type = self._classify_personality_type(profile)
            
            if new_type != old_type:
                profile.personality_type = new_type
                self.logger.info(f"Personality type yangilandi: {old_type.value} -> {new_type.value}")
            
            # Profile saqlash
            self.profiles[profile.trader_id] = profile
            self._save_profiles()
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Adaptiv personalization xatosi: {e}")
            return profile

# Utility functions
def create_sample_profile(trader_id: str, personality_type: str = "day_trader") -> PersonalityProfile:
    """Namuna profil yaratish"""
    return PersonalityProfile(
        trader_id=trader_id,
        personality_type=TradingPersonalityType(personality_type),
        risk_tolerance=RiskTolerance.MEDIUM,
        timeframe_preference=TimeframePreference.MINUTES,
        trading_frequency=5.0,
        avg_holding_time=120.0,
        decision_speed="medium",
        emotional_score=0.7,
        learning_style="analytical",
        information_sources=["news", "charts", "indicators"],
        social_trading_score=0.3,
        win_rate=0.6,
        avg_profit_per_trade=0.02,
        max_drawdown=0.15,
        sharpe_ratio=1.2
    )

# Test
if __name__ == "__main__":
    # Test
    engine = TradingPersonalityEngine()
    
    # Namuna ma'lumotlar
    trading_data = {
        "trader_id": "test_trader_001",
        "trades": [
            {
                "entry_time": "2025-11-04T10:00:00",
                "exit_time": "2025-11-04T10:30:00",
                "profit": 0.015
            },
            {
                "entry_time": "2025-11-04T11:00:00", 
                "exit_time": "2025-11-04T12:00:00",
                "profit": -0.01
            }
        ],
        "days_active": 30,
        "win_rate": 0.65,
        "avg_profit_per_trade": 0.012,
        "max_drawdown": 0.12,
        "sharpe_ratio": 1.4
    }
    
    # Profile aniqlash
    profile = engine.detect_personality(trading_data)
    print(f"Aniqlangan shaxsiyat: {profile.personality_type.value}")
    print(f"Risk tolerance: {profile.risk_tolerance.value}")
    print(f"UI customizatsiya: {engine.get_ui_customization(profile)}")
    
    # Strategiyalar
    strategies = engine.get_recommended_strategies(profile)
    print(f"Tavsiya qilingan strategiyalar: {len(strategies)} ta")
    for strategy in strategies:
        print(f"- {strategy['name']}: {strategy['description']}")