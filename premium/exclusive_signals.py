"""
Eksklyuziv Signallar Moduli
===========================

Bu modul Orion Starline platformasining eksklyuziv savdo signallari xususiyatini boshqaradi.
VIP foydalanuvchilar uchun yuqori sifatli va aniq savdo signallari taqdim etadi.

Asosiy xususiyatlar:
- AI-powered trading signals
- Real-time signal delivery
- Signal accuracy tracking
- Multiple strategy signals
- Risk-adjusted signals
- Signal performance analytics
- Custom signal filters
- Signal notification system

Autor: AI Development Team
Versiya: 1.0.0
Sana: 2025-11-05
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import numpy as np
import pandas as pd
from threading import Thread
import time
import queue

# Signal types
class SignalType(Enum):
    """Signal turlari"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    CLOSE_LONG = "close_long"
    CLOSE_SHORT = "close_short"

# Signal strength
class SignalStrength(Enum):
    """Signal kuchliligi"""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

# Signal source
class SignalSource(Enum):
    """Signal manbasi"""
    AI_ANALYSIS = "ai_analysis"
    TECHNICAL_INDICATORS = "technical_indicators"
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    PATTERN_RECOGNITION = "pattern_recognition"
    QUANTITATIVE_MODELS = "quantitative_models"

@dataclass
class TradingSignal:
    """Savdo signal"""
    signal_id: str
    user_id: str
    symbol: str
    signal_type: SignalType
    strength: SignalStrength
    source: SignalSource
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float  # 0-1
    risk_reward_ratio: float
    timeframe: str
    created_at: datetime
    expires_at: datetime
    status: str  # active, closed, expired
    notes: str
    metadata: Dict[str, Any]

@dataclass
class SignalPerformance:
    """Signal performance"""
    signal_id: str
    actual_entry: Optional[float]
    actual_exit: Optional[float]
    profit_loss: Optional[float]
    profit_loss_percent: Optional[float]
    duration_hours: Optional[float]
    accuracy: bool
    max_favorable_excursion: Optional[float]
    max_adverse_excursion: Optional[float]
    closed_at: Optional[datetime]

@dataclass
class SignalFilter:
    """Signal filtr"""
    filter_id: str
    user_id: str
    name: str
    criteria: Dict[str, Any]
    active: bool
    created_at: datetime

@dataclass
class SignalAlert:
    """Signal bildirish"""
    alert_id: str
    user_id: str
    signal_id: str
    alert_type: str  # new_signal, signal_update, signal_closed
    message: str
    sent_at: datetime
    delivered: bool
    channel: str  # email, sms, push, webhook

class ExclusiveSignalManager:
    """
    Eksklyuziv signallar boshqaruvchisi
    
    VIP foydalanuvchilar uchun yuqori sifatli savdo signallarini yaratish va boshqarish.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_signals: Dict[str, TradingSignal] = {}
        self.signal_performance: Dict[str, SignalPerformance] = {}
        self.signal_filters: Dict[str, SignalFilter] = {}
        self.signal_history: List[TradingSignal] = []
        self.alert_queue: List[SignalAlert] = {}
        
        # Signal generation settings
        self.signal_generation_enabled = True
        self.max_signals_per_user = 50
        self.signal_timeout_hours = 24
        
        # Statistics
        self.total_signals_generated = 0
        self.accuracy_rate = 0.0
        self.avg_profit_per_signal = 0.0
        
        self._initialize_sample_signals()
        self._start_signal_generator()
    
    def _initialize_sample_signals(self):
        """Namuna signallarni boshlash"""
        sample_signals = [
            TradingSignal(
                signal_id="signal_001",
                user_id="vip001",
                symbol="EURUSD",
                signal_type=SignalType.BUY,
                strength=SignalStrength.STRONG,
                source=SignalSource.AI_ANALYSIS,
                entry_price=1.1050,
                stop_loss=1.1000,
                take_profit=1.1150,
                confidence=0.85,
                risk_reward_ratio=2.0,
                timeframe="1h",
                created_at=datetime.now() - timedelta(hours=2),
                expires_at=datetime.now() + timedelta(hours=22),
                status="active",
                notes="AI model bullish pattern aniqladi",
                metadata={"pattern": "ascending_triangle", "volume": "high"}
            ),
            TradingSignal(
                signal_id="signal_002",
                user_id="vip002",
                symbol="XAUUSD",
                signal_type=SignalType.BUY,
                strength=SignalStrength.MODERATE,
                source=SignalSource.TECHNICAL_INDICATORS,
                entry_price=1825.00,
                stop_loss=1810.00,
                take_profit=1855.00,
                confidence=0.72,
                risk_reward_ratio=2.0,
                timeframe="4h",
                created_at=datetime.now() - timedelta(hours=1),
                expires_at=datetime.now() + timedelta(hours=23),
                status="active",
                notes="RSI oversold va MACD bullish crossover",
                metadata={"rsi": 28, "macd_signal": "bullish"}
            )
        ]
        
        for signal in sample_signals:
            self.active_signals[signal.signal_id] = signal
            self.total_signals_generated += 1
    
    def _start_signal_generator(self):
        """Signal generator ni boshlash"""
        def signal_generator_thread():
            while self.signal_generation_enabled:
                try:
                    # Har 30 daqiqada yangi signal yaratish
                    self._generate_new_signals()
                    time.sleep(1800)  # 30 minutes
                except Exception as e:
                    self.logger.error(f"Error in signal generator: {str(e)}")
                    time.sleep(300)  # 5 minutes retry
        
        generator_thread = Thread(target=signal_generator_thread, daemon=True)
        generator_thread.start()
        self.logger.info("Signal generator started")
    
    def _generate_new_signals(self):
        """Yangi signallar yaratish"""
        # Avtomatik signal yaratish mantiqi
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]
        signal_types = [SignalType.BUY, SignalType.SELL]
        sources = [SignalSource.AI_ANALYSIS, SignalSource.TECHNICAL_INDICATORS, SignalSource.SENTIMENT_ANALYSIS]
        
        for _ in range(np.random.randint(1, 3)):  # 1-2 ta signal
            symbol = np.random.choice(symbols)
            signal_type = np.random.choice(signal_types)
            source = np.random.choice(sources)
            
            # Narx ma'lumotlarini simulatsiya qilish
            base_prices = {"EURUSD": 1.1000, "GBPUSD": 1.3000, "USDJPY": 110.00, 
                          "XAUUSD": 1800.00, "BTCUSD": 45000.00}
            
            entry_price = base_prices.get(symbol, 100.0) * (1 + np.random.uniform(-0.02, 0.02))
            
            # Stop loss va take profit hisoblash
            risk_pips = np.random.uniform(10, 50)
            reward_pips = risk_pips * np.random.uniform(1.5, 3.0)
            
            if signal_type == SignalType.BUY:
                stop_loss = entry_price - (risk_pips / 10000 if "USD" in symbol else risk_pips * 0.1)
                take_profit = entry_price + (reward_pips / 10000 if "USD" in symbol else reward_pips * 0.1)
            else:
                stop_loss = entry_price + (risk_pips / 10000 if "USD" in symbol else risk_pips * 0.1)
                take_profit = entry_price - (reward_pips / 10000 if "USD" in symbol else reward_pips * 0.1)
            
            # Signal kuchliligi
            confidence = np.random.uniform(0.6, 0.9)
            if confidence > 0.8:
                strength = SignalStrength.VERY_STRONG
            elif confidence > 0.7:
                strength = SignalStrength.STRONG
            elif confidence > 0.6:
                strength = SignalStrength.MODERATE
            else:
                strength = SignalStrength.WEAK
            
            signal_id = f"signal_{len(self.active_signals) + len(self.signal_history) + 1:03d}"
            
            # Birinchi VIP foydalanuvchilarga yuborish
            user_ids = ["vip001", "vip002", "elite001"]
            user_id = np.random.choice(user_ids)
            
            new_signal = TradingSignal(
                signal_id=signal_id,
                user_id=user_id,
                symbol=symbol,
                signal_type=signal_type,
                strength=strength,
                source=source,
                entry_price=round(entry_price, 4),
                stop_loss=round(stop_loss, 4),
                take_profit=round(take_profit, 4),
                confidence=round(confidence, 2),
                risk_reward_ratio=round(reward_pips / risk_pips, 2),
                timeframe=np.random.choice(["15m", "1h", "4h", "1d"]),
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=self.signal_timeout_hours),
                status="active",
                notes=self._generate_signal_notes(source, symbol),
                metadata={"auto_generated": True}
            )
            
            self.active_signals[signal_id] = new_signal
            self.total_signals_generated += 1
            
            # Alert yaratish
            self._create_signal_alert(user_id, signal_id, "new_signal", 
                                    f"Yangi {signal_type.value} signal: {symbol}")
            
            self.logger.info(f"Generated new signal: {signal_id} for {symbol}")
    
    def _generate_signal_notes(self, source: SignalSource, symbol: str) -> str:
        """Signal eslatmalari yaratish"""
        notes_map = {
            SignalSource.AI_ANALYSIS: f"AI tahlili {symbol} uchun {np.random.choice(['bullish', 'bearish'])} signal berdi",
            SignalSource.TECHNICAL_INDICATORS: f"Texnik indikatorlar {symbol} da {np.random.choice(['kuchli', 'o\'rtacha'])} signal ko'rsatmoqda",
            SignalSource.SENTIMENT_ANALYSIS: f"Sentiment tahlili {symbol} ga {np.random.choice(['ijobiy', 'salbiy'])} munosabat bildirmoqda",
            SignalSource.PATTERN_RECOGNITION: f"{symbol} da {np.random.choice(['triangle', 'flag', 'head_shoulders'])} pattern aniqlangan"
        }
        
        return notes_map.get(source, f"{symbol} uchun signal yaratildi")
    
    def generate_signal(self, user_id: str, symbol: str, criteria: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Foydalanuvchi uchun signal yaratish
        
        Args:
            user_id: Foydalanuvchi ID
            symbol: Trading symbol
            criteria: Signal mezonlari
            
        Returns:
            Yaratilgan signal ma'lumotlari
        """
        try:
            # Foydalanuvchining aktiv signal sonini tekshirish
            user_signals = [s for s in self.active_signals.values() if s.user_id == user_id]
            if len(user_signals) >= self.max_signals_per_user:
                return {
                    "success": False,
                    "message": f"Maksimal signal soniga yetdingiz ({self.max_signals_per_user})"
                }
            
            # AI model simulation
            signal_type, confidence, entry_price = self._simulate_ai_signal(symbol, criteria)
            
            # Stop loss va take profit hisoblash
            risk_reward_ratio = np.random.uniform(1.5, 3.0)
            risk_amount = criteria.get('risk_amount', 100) if criteria else 100
            
            if signal_type == SignalType.BUY:
                stop_loss = entry_price * (1 - risk_amount / 10000)
                take_profit = entry_price * (1 + (risk_amount * risk_reward_ratio) / 10000)
            else:
                stop_loss = entry_price * (1 + risk_amount / 10000)
                take_profit = entry_price * (1 - (risk_amount * risk_reward_ratio) / 10000)
            
            # Signal kuchliligi
            if confidence > 0.85:
                strength = SignalStrength.VERY_STRONG
            elif confidence > 0.75:
                strength = SignalStrength.STRONG
            elif confidence > 0.65:
                strength = SignalStrength.MODERATE
            else:
                strength = SignalStrength.WEAK
            
            signal_id = f"signal_{len(self.active_signals) + len(self.signal_history) + 1:03d}"
            
            new_signal = TradingSignal(
                signal_id=signal_id,
                user_id=user_id,
                symbol=symbol,
                signal_type=signal_type,
                strength=strength,
                source=SignalSource.AI_ANALYSIS,
                entry_price=round(entry_price, 4),
                stop_loss=round(stop_loss, 4),
                take_profit=round(take_profit, 4),
                confidence=round(confidence, 2),
                risk_reward_ratio=round(risk_reward_ratio, 2),
                timeframe=criteria.get('timeframe', '1h') if criteria else '1h',
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=self.signal_timeout_hours),
                status="active",
                notes="AI model tomonidan yaratilgan signal",
                metadata=criteria or {}
            )
            
            self.active_signals[signal_id] = new_signal
            self.total_signals_generated += 1
            
            # Alert yaratish
            self._create_signal_alert(user_id, signal_id, "new_signal", 
                                    f"Yangi {signal_type.value} signal: {symbol}")
            
            self.logger.info(f"Generated signal {signal_id} for user {user_id}")
            
            return {
                "success": True,
                "signal": asdict(new_signal),
                "message": f"{symbol} uchun {signal_type.value} signal yaratildi"
            }
            
        except Exception as e:
            self.logger.error(f"Error generating signal: {str(e)}")
            return {
                "success": False,
                "message": f"Signal yaratishda xatolik: {str(e)}"
            }
    
    def _simulate_ai_signal(self, symbol: str, criteria: Dict[str, Any] = None) -> Tuple[SignalType, float, float]:
        """AI signal simulatsiyasi"""
        # Namuna narx ma'lumotlari
        base_prices = {
            "EURUSD": 1.1000, "GBPUSD": 1.3000, "USDJPY": 110.00, 
            "XAUUSD": 1800.00, "BTCUSD": 45000.00, "ETHUSD": 3000.00
        }
        
        base_price = base_prices.get(symbol, 100.0)
        
        # Signal type determination (simplified AI logic)
        market_trend = np.random.choice(["bullish", "bearish", "sideways"], p=[0.4, 0.35, 0.25])
        
        if market_trend == "bullish":
            signal_type = SignalType.BUY
            confidence = np.random.uniform(0.7, 0.9)
            entry_price = base_price * (1 + np.random.uniform(0.001, 0.005))
        elif market_trend == "bearish":
            signal_type = SignalType.SELL
            confidence = np.random.uniform(0.7, 0.9)
            entry_price = base_price * (1 - np.random.uniform(0.001, 0.005))
        else:  # sideways
            signal_type = np.random.choice([SignalType.BUY, SignalType.SELL])
            confidence = np.random.uniform(0.6, 0.75)
            entry_price = base_price * (1 + np.random.uniform(-0.002, 0.002))
        
        return signal_type, confidence, entry_price
    
    def get_user_signals(self, user_id: str, status: str = "active") -> Dict[str, Any]:
        """Foydalanuvchining signallarini olish"""
        user_signals = []
        
        # Active signallar
        for signal in self.active_signals.values():
            if signal.user_id == user_id and (status == "all" or signal.status == status):
                user_signals.append(asdict(signal))
        
        # History signallari (agar so'ralgan bo'lsa)
        if status == "all":
            for signal in self.signal_history:
                if signal.user_id == user_id:
                    user_signals.append(asdict(signal))
        
        # Performance ma'lumotlarini qo'shish
        for i, signal_data in enumerate(user_signals):
            signal_id = signal_data["signal_id"]
            if signal_id in self.signal_performance:
                user_signals[i]["performance"] = asdict(self.signal_performance[signal_id])
        
        return {
            "user_id": user_id,
            "total_signals": len(user_signals),
            "active_count": len([s for s in user_signals if s["status"] == "active"]),
            "closed_count": len([s for s in user_signals if s["status"] == "closed"]),
            "signals": user_signals
        }
    
    def close_signal(self, signal_id: str, exit_price: float, exit_reason: str = "manual") -> Dict[str, Any]:
        """Signalni yopish"""
        if signal_id not in self.active_signals:
            return {
                "success": False,
                "message": "Signal topilmadi"
            }
        
        signal = self.active_signals[signal_id]
        
        # Performance hisoblash
        if signal.signal_type == SignalType.BUY:
            profit_loss = (exit_price - signal.entry_price) * 10000  # Pips
        else:
            profit_loss = (signal.entry_price - exit_price) * 10000
        
        profit_loss_percent = (profit_loss / signal.entry_price) * 100
        
        # Signal performance yaratish
        performance = SignalPerformance(
            signal_id=signal_id,
            actual_entry=signal.entry_price,
            actual_exit=exit_price,
            profit_loss=profit_loss,
            profit_loss_percent=profit_loss_percent,
            duration_hours=(datetime.now() - signal.created_at).total_seconds() / 3600,
            accuracy=(signal.signal_type == SignalType.BUY and exit_price > signal.entry_price) or 
                    (signal.signal_type == SignalType.SELL and exit_price < signal.entry_price),
            closed_at=datetime.now()
        )
        
        # Signal status yangilash
        signal.status = "closed"
        signal.metadata["exit_price"] = exit_price
        signal.metadata["exit_reason"] = exit_reason
        
        # Performance saqlash
        self.signal_performance[signal_id] = performance
        
        # Active signals dan history ga ko'chirish
        self.signal_history.append(signal)
        del self.active_signals[signal_id]
        
        # Alert yaratish
        self._create_signal_alert(signal.user_id, signal_id, "signal_closed", 
                                f"Signal yopildi: {signal.symbol}")
        
        self.logger.info(f"Signal {signal_id} closed with P&L: {profit_loss:.2f} pips")
        
        return {
            "success": True,
            "message": "Signal muvaffaqiyatli yopildi",
            "performance": asdict(performance)
        }
    
    def _create_signal_alert(self, user_id: str, signal_id: str, alert_type: str, message: str) -> None:
        """Signal bildirishni yaratish"""
        alert = SignalAlert(
            alert_id=f"alert_{len(self.alert_queue) + 1:03d}",
            user_id=user_id,
            signal_id=signal_id,
            alert_type=alert_type,
            message=message,
            sent_at=datetime.now(),
            delivered=False,
            channel="push"  # Default channel
        )
        
        if user_id not in self.alert_queue:
            self.alert_queue[user_id] = []
        
        self.alert_queue[user_id].append(alert)
    
    def get_signal_analytics(self, user_id: str = None) -> Dict[str, Any]:
        """Signal analitikasi"""
        # Barcha signallar (active + history)
        all_signals = list(self.active_signals.values()) + self.signal_history
        
        if user_id:
            all_signals = [s for s in all_signals if s.user_id == user_id]
        
        if not all_signals:
            return {"message": "Hech qanday signal topilmadi"}
        
        # Accuracy hisoblash
        closed_signals = [s for s in all_signals if s.status == "closed"]
        accurate_signals = 0
        
        for signal in closed_signals:
            if signal.signal_id in self.signal_performance:
                if self.signal_performance[signal.signal_id].accuracy:
                    accurate_signals += 1
        
        accuracy_rate = accurate_signals / len(closed_signals) if closed_signals else 0
        
        # Profit/Loss hisoblash
        total_pnl = 0
        for signal in closed_signals:
            if signal.signal_id in self.signal_performance:
                total_pnl += self.signal_performance[signal.signal_id].profit_loss_percent
        
        avg_pnl = total_pnl / len(closed_signals) if closed_signals else 0
        
        # Signal turi bo'yicha taqsimot
        signal_types = {}
        for signal in all_signals:
            signal_type = signal.signal_type.value
            signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
        
        # Signal manbasi bo'yicha taqsimot
        signal_sources = {}
        for signal in all_signals:
            source = signal.source.value
            signal_sources[source] = signal_sources.get(source, 0) + 1
        
        # Keyingi 24 soatdagi signallar
        last_24h = datetime.now() - timedelta(hours=24)
        recent_signals = [s for s in all_signals if s.created_at >= last_24h]
        
        return {
            "total_signals": len(all_signals),
            "active_signals": len([s for s in all_signals if s.status == "active"]),
            "closed_signals": len(closed_signals),
            "accuracy_rate": round(accuracy_rate * 100, 2),
            "average_profit_percent": round(avg_pnl, 2),
            "signal_type_distribution": signal_types,
            "signal_source_distribution": signal_sources,
            "recent_signals_24h": len(recent_signals),
            "success_rate_by_source": self._calculate_success_rate_by_source(all_signals),
            "best_performing_symbol": self._get_best_performing_symbol(all_signals),
            "signal_strength_distribution": self._get_strength_distribution(all_signals)
        }
    
    def _calculate_success_rate_by_source(self, signals: List[TradingSignal]) -> Dict[str, float]:
        """Manba bo'yicha muvaffaqiyat darajasi"""
        source_stats = {}
        
        for signal in signals:
            source = signal.source.value
            if source not in source_stats:
                source_stats[source] = {"total": 0, "accurate": 0}
            
            source_stats[source]["total"] += 1
            
            # Accurate tekshirish (faqat closed signals uchun)
            if signal.status == "closed" and signal.signal_id in self.signal_performance:
                if self.signal_performance[signal.signal_id].accuracy:
                    source_stats[source]["accurate"] += 1
        
        # Success rate hisoblash
        success_rates = {}
        for source, stats in source_stats.items():
            if stats["total"] > 0:
                success_rates[source] = round(stats["accurate"] / stats["total"] * 100, 2)
            else:
                success_rates[source] = 0.0
        
        return success_rates
    
    def _get_best_performing_symbol(self, signals: List[TradingSignal]) -> str:
        """Eng yaxshi performer symbol"""
        symbol_performance = {}
        
        for signal in signals:
            if signal.status == "closed" and signal.signal_id in self.signal_performance:
                symbol = signal.symbol
                pnl = self.signal_performance[signal.signal_id].profit_loss_percent
                
                if symbol not in symbol_performance:
                    symbol_performance[symbol] = []
                
                symbol_performance[symbol].append(pnl)
        
        # O'rtacha performance hisoblash
        avg_performance = {}
        for symbol, pnls in symbol_performance.items():
            avg_performance[symbol] = sum(pnls) / len(pnls)
        
        # Eng yaxshi performer
        if avg_performance:
            best_symbol = max(avg_performance, key=avg_performance.get)
            return best_symbol
        
        return "N/A"
    
    def _get_strength_distribution(self, signals: List[TradingSignal]) -> Dict[str, int]:
        """Signal kuchliligi taqsimoti"""
        distribution = {}
        
        for signal in signals:
            strength = signal.strength.value
            distribution[strength] = distribution.get(strength, 0) + 1
        
        return distribution
    
    def apply_signal_filter(self, user_id: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Signal filtrini qo'llash"""
        try:
            # Foydalanuvchi uchun mos signallarni topish
            filtered_signals = []
            
            for signal in self.active_signals.values():
                if signal.user_id != user_id:
                    continue
                
                # Filter criteria tekshirish
                if self._matches_criteria(signal, criteria):
                    filtered_signals.append(asdict(signal))
            
            return {
                "success": True,
                "filtered_count": len(filtered_signals),
                "signals": filtered_signals
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Filtrlashda xatolik: {str(e)}"
            }
    
    def _matches_criteria(self, signal: TradingSignal, criteria: Dict[str, Any]) -> bool:
        """Signalning criteria ga mosligini tekshirish"""
        # Symbol filter
        if "symbols" in criteria:
            if signal.symbol not in criteria["symbols"]:
                return False
        
        # Signal type filter
        if "signal_types" in criteria:
            if signal.signal_type.value not in criteria["signal_types"]:
                return False
        
        # Confidence filter
        if "min_confidence" in criteria:
            if signal.confidence < criteria["min_confidence"]:
                return False
        
        # Strength filter
        if "strength_levels" in criteria:
            if signal.strength.value not in criteria["strength_levels"]:
                return False
        
        # Timeframe filter
        if "timeframes" in criteria:
            if signal.timeframe not in criteria["timeframes"]:
                return False
        
        return True
    
    def get_upcoming_expiring_signals(self, hours_ahead: int = 2) -> List[Dict[str, Any]]:
        """Tugashga yaqin signallar"""
        cutoff_time = datetime.now() + timedelta(hours=hours_ahead)
        expiring_signals = []
        
        for signal in self.active_signals.values():
            if signal.expires_at <= cutoff_time:
                expiring_signals.append({
                    "signal_id": signal.signal_id,
                    "user_id": signal.user_id,
                    "symbol": signal.symbol,
                    "signal_type": signal.signal_type.value,
                    "expires_at": signal.expires_at.isoformat(),
                    "hours_remaining": (signal.expires_at - datetime.now()).total_seconds() / 3600
                })
        
        return expiring_signals
    
    def update_signal_performance_tracking(self):
        """Signal performance tracking yangilash"""
        # Expired signallarni yopish
        current_time = datetime.now()
        expired_signals = []
        
        for signal_id, signal in self.active_signals.items():
            if signal.expires_at <= current_time:
                expired_signals.append(signal_id)
        
        for signal_id in expired_signals:
            signal = self.active_signals[signal_id]
            
            # Auto close with market price (simulated)
            market_price = signal.entry_price * (1 + np.random.uniform(-0.01, 0.01))
            self.close_signal(signal_id, market_price, "expired")
            
            self.logger.info(f"Auto-closed expired signal {signal_id}")
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Tizim statistikasi"""
        self.update_signal_performance_tracking()
        
        total_signals = len(self.active_signals) + len(self.signal_history)
        
        # Overall accuracy
        closed_signals = [s for s in self.signal_history if s.status == "closed"]
        accurate_count = 0
        
        for signal in closed_signals:
            if signal.signal_id in self.signal_performance:
                if self.signal_performance[signal.signal_id].accuracy:
                    accurate_count += 1
        
        overall_accuracy = accurate_count / len(closed_signals) if closed_signals else 0
        
        # Top symbols
        symbol_counts = {}
        for signal in self.active_signals.values():
            symbol_counts[signal.symbol] = symbol_counts.get(signal.symbol, 0) + 1
        
        top_symbols = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_signals_generated": self.total_signals_generated,
            "active_signals": len(self.active_signals),
            "total_history_signals": len(self.signal_history),
            "overall_accuracy_rate": round(overall_accuracy * 100, 2),
            "average_confidence": round(np.mean([s.confidence for s in self.active_signals.values()]), 2),
            "top_trading_symbols": dict(top_symbols),
            "signal_generation_enabled": self.signal_generation_enabled,
            "max_signals_per_user": self.max_signals_per_user,
            "average_daily_signals": self.total_signals_generated / max(1, (datetime.now() - min((s.created_at for s in self.signal_history + list(self.active_signals.values())), key=lambda x: x.created_at)).days)
        }

# Global instance
exclusive_signals = ExclusiveSignalManager()

# Utility functions
def generate_trading_signal(user_id: str, symbol: str, **criteria) -> Dict[str, Any]:
    """Savdo signal yaratish (utility function)"""
    return exclusive_signals.generate_signal(user_id, symbol, criteria)

def get_user_trading_signals(user_id: str, status: str = "active") -> Dict[str, Any]:
    """Foydalanuvchi savdo signallari (utility function)"""
    return exclusive_signals.get_user_signals(user_id, status)

def close_trading_signal(signal_id: str, exit_price: float, reason: str = "manual") -> Dict[str, Any]:
    """Savdo signal yopish (utility function)"""
    return exclusive_signals.close_signal(signal_id, exit_price, reason)

def get_signal_analytics(user_id: str = None) -> Dict[str, Any]:
    """Signal analitikasi (utility function)"""
    return exclusive_signals.get_signal_analytics(user_id)

def apply_signal_filter(user_id: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
    """Signal filtrlash (utility function)"""
    return exclusive_signals.apply_signal_filter(user_id, criteria)

# Export main classes and functions
__all__ = [
    'SignalType',
    'SignalStrength', 
    'SignalSource',
    'TradingSignal',
    'SignalPerformance',
    'SignalFilter',
    'SignalAlert',
    'ExclusiveSignalManager',
    'exclusive_signals',
    'generate_trading_signal',
    'get_user_trading_signals',
    'close_trading_signal',
    'get_signal_analytics',
    'apply_signal_filter'
]