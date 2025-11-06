"""
Signal almashish platformi - Trading signal providers va subscribers o'rtasida
signal almashish imkonini beruvchi platform.
"""

import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Callable, Any
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict
import threading
import logging

logger = logging.getLogger(__name__)


class SignalProvider(Enum):
    """Signal provider turlari"""
    GPT5_SENTIMENT = "gpt5_sentiment"
    QUANTUM_ALGO = "quantum_algo"
    CLASSICAL_AI = "classical_ai"
    HYBRID_SYSTEM = "hybrid_system"
    HUMAN_TRADERS = "human_traders"
    MARKET_DATA = "market_data"
    TECHNICAL_ANALYSIS = "technical_analysis"
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"
    ARBITRAGE_DETECTOR = "arbitrage_detector"


class SignalType(Enum):
    """Trading signal turlari"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    ENTRY = "entry"
    EXIT = "exit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    SCALPING = "scalping"
    SWING = "swing"
    POSITION = "position"


class TimeFrame(Enum):
    """Vaqt freymasi turlari"""
    M1 = "1m"  # 1 daqiqa
    M5 = "5m"  # 5 daqiqa
    M15 = "15m"  # 15 daqiqa
    M30 = "30m"  # 30 daqiqa
    H1 = "1h"  # 1 soat
    H4 = "4h"  # 4 soat
    D1 = "1d"  # 1 kun
    W1 = "1w"  # 1 hafta
    MN1 = "1M"  # 1 oy


class SignalStrength(Enum):
    """Signal kuchi turlari"""
    VERY_WEAK = 1
    WEAK = 2
    MODERATE = 3
    STRONG = 4
    VERY_STRONG = 5


class SignalStatus(Enum):
    """Signal status turlari"""
    ACTIVE = "active"
    EXECUTED = "executed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"


@dataclass
class TradingSignal:
    """Trading signal klassi"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    provider_id: str = ""
    provider_name: str = ""
    provider_type: SignalProvider = None
    symbol: str = ""
    signal_type: SignalType = None
    timeframe: TimeFrame = None
    entry_price: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    confidence: float = 0.0  # 0.0 - 1.0
    strength: SignalStrength = SignalStrength.MODERATE
    status: SignalStatus = SignalStatus.ACTIVE
    description: str = ""
    analysis: str = ""
    metadata: Dict = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    executed_at: Optional[float] = None
    profit_loss: float = 0.0
    risk_reward_ratio: float = 0.0
    views: int = 0
    likes: int = 0
    
    def __post_init__(self):
        """Narx hisoblar"""
        if self.stop_loss > 0 and self.entry_price > 0:
            if self.signal_type in [SignalType.BUY, SignalType.ENTRY]:
                self.risk_reward_ratio = abs(self.take_profit - self.entry_price) / abs(self.entry_price - self.stop_loss)
            else:
                self.risk_reward_ratio = abs(self.take_profit - self.entry_price) / abs(self.stop_loss - self.entry_price)
    
    def to_dict(self) -> Dict:
        """Signal obyektini dictionary ga aylantirish"""
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'provider_name': self.provider_name,
            'provider_type': self.provider_type.value if self.provider_type else None,
            'symbol': self.symbol,
            'signal_type': self.signal_type.value if self.signal_type else None,
            'timeframe': self.timeframe.value if self.timeframe else None,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'confidence': self.confidence,
            'strength': self.strength.value,
            'status': self.status.value,
            'description': self.description,
            'analysis': self.analysis,
            'metadata': self.metadata,
            'tags': self.tags,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'executed_at': self.executed_at,
            'profit_loss': self.profit_loss,
            'risk_reward_ratio': self.risk_reward_ratio,
            'views': self.views,
            'likes': self.likes
        }
    
    def is_expired(self) -> bool:
        """Signal muddati o'tganligini tekshirish"""
        if not self.expires_at:
            return False
        return time.time() > self.expires_at
    
    def is_profitable(self) -> bool:
        """Signal foydali bo'lganligini tekshirish"""
        return self.profit_loss > 0
    
    def get_duration_minutes(self) -> float:
        """Signal davomiyligini daqiqalarda olish"""
        if not self.executed_at:
            return 0.0
        return (self.executed_at - self.created_at) / 60


@dataclass
class Provider:
    """Signal provider klassi"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    provider_type: SignalProvider = None
    description: str = ""
    rating: float = 0.0
    total_signals: int = 0
    successful_signals: int = 0
    failed_signals: int = 0
    pending_signals: int = 0
    success_rate: float = 0.0
    avg_profit: float = 0.0
    total_subscribers: int = 0
    verified: bool = False
    premium: bool = False
    subscription_fee: float = 0.0
    specialization: List[str] = field(default_factory=list)
    contact_info: Dict = field(default_factory=dict)
    performance_metrics: Dict = field(default_factory=dict)
    is_active: bool = True
    subscribers: Set[str] = field(default_factory=set)
    created_at: float = field(default_factory=time.time)
    last_signal_at: Optional[float] = None
    
    def update_success_rate(self):
        """Success rate ni yangilash"""
        total_evaluated = self.successful_signals + self.failed_signals
        if total_evaluated > 0:
            self.success_rate = (self.successful_signals / total_evaluated) * 100
    
    def get_recent_performance(self, days: int = 30) -> Dict:
        """So'nggi performance ma'lumotlari"""
        # Bu yerda bazadan so'nggi performance olish kerak
        return {
            'signals_count': self.total_signals,
            'success_rate': self.success_rate,
            'avg_profit': self.avg_profit,
            'rating': self.rating,
            'subscribers': self.total_subscribers
        }


@dataclass
class Subscription:
    """Subscriber obuna klassi"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subscriber_id: str = ""
    provider_id: str = ""
    provider_name: str = ""
    auto_trade: bool = False
    notification_enabled: bool = True
    symbols_filter: List[str] = field(default_factory=list)
    min_confidence: float = 0.0
    min_strength: SignalStrength = SignalStrength.WEAK
    max_risk: float = 0.05  # Portfolio % si
    active: bool = True
    created_at: float = field(default_factory=time.time)
    
    def matches_filter(self, signal: TradingSignal) -> bool:
        """Signal obuna filtriga mos kelishini tekshirish"""
        # Symbol filter
        if self.symbols_filter and signal.symbol not in self.symbols_filter:
            return False
        
        # Confidence filter
        if signal.confidence < self.min_confidence:
            return False
        
        # Strength filter
        if signal.strength.value < self.min_strength.value:
            return False
        
        return True


class SignalPlatform:
    """Signal almashish platformasi asosiy klassi"""
    
    def __init__(self):
        self.providers: Dict[str, Provider] = {}
        self.signals: Dict[str, TradingSignal] = {}
        self.subscriptions: Dict[str, List[Subscription]] = defaultdict(list)
        self.subscribers_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self.signal_notifications: List[Callable] = []
        self.lock = threading.RLock()  # Thread-safe operatsiyalar uchun
        
        # Performance metrics
        self.platform_stats = {
            'total_signals': 0,
            'active_providers': 0,
            'total_subscribers': 0,
            'total_profit': 0.0
        }
    
    def register_provider(
        self,
        name: str,
        provider_type: SignalProvider,
        description: str = "",
        rating: float = 0.0,
        verified: bool = False,
        premium: bool = False,
        subscription_fee: float = 0.0,
        specialization: List[str] = None
    ) -> str:
        """Yangi signal provider ro'yxatdan o'tkazish
        
        Args:
            name: Provider nomi
            provider_type: Provider turi
            description: Tavsif
            rating: Reyting (0.0 - 5.0)
            verified: Tasdiqlangan provider
            premium: Premium provider
            subscription_fee: Oylik to'lov
            specialization: Ixtisoslashgan sohalar
            
        Returns:
            provider_id: Yaratilgan provider ID
        """
        with self.lock:
            provider = Provider(
                name=name,
                provider_type=provider_type,
                description=description,
                rating=max(0.0, min(5.0, rating)),
                verified=verified,
                premium=premium,
                subscription_fee=subscription_fee,
                specialization=specialization or []
            )
            
            self.providers[provider.id] = provider
            self.platform_stats['active_providers'] += 1
            
            logger.info(f"Provider ro'yxatdan o'tdi: {name} ({provider_type.value})")
            return provider.id
    
    def publish_signal(
        self,
        provider_id: str,
        symbol: str,
        signal_type: SignalType,
        timeframe: TimeFrame,
        entry_price: float = 0.0,
        stop_loss: float = 0.0,
        take_profit: float = 0.0,
        confidence: float = 0.5,
        strength: SignalStrength = SignalStrength.MODERATE,
        description: str = "",
        analysis: str = "",
        tags: List[str] = None,
        expires_in_minutes: int = 60,
        metadata: Dict = None
    ) -> str:
        """Yangi signal chop etish
        
        Args:
            provider_id: Provider ID
            symbol: Trader instrument simboli (masalan: EURUSD)
            signal_type: Signal turi (BUY, SELL, etc.)
            timeframe: Vaqt freymasi
            entry_price: Kirish narxi
            stop_loss: Zarar to'xtatish
            take_profit: Foyda olish
            confidence: Ishonchlilik darajasi (0.0 - 1.0)
            strength: Signal kuchi
            description: Signal tavsifi
            analysis: Batafsil tahlil
            tags: Teglar
            expires_in_minutes: Muddat (daqiqalarda)
            metadata: Qo'shimcha ma'lumotlar
            
        Returns:
            signal_id: Yaratilgan signal ID
        """
        with self.lock:
            # Provider mavjudligini tekshirish
            if provider_id not in self.providers:
                raise ValueError(f"Provider topilmadi: {provider_id}")
            
            provider = self.providers[provider_id]
            if not provider.is_active:
                raise ValueError(f"Provider faol emas: {provider_id}")
            
            # Signal yaratish
            expires_at = None
            if expires_in_minutes > 0:
                expires_at = time.time() + (expires_in_minutes * 60)
            
            signal = TradingSignal(
                provider_id=provider_id,
                provider_name=provider.name,
                provider_type=provider.provider_type,
                symbol=symbol,
                signal_type=signal_type,
                timeframe=timeframe,
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=max(0.0, min(1.0, confidence)),
                strength=strength,
                description=description,
                analysis=analysis,
                tags=tags or [],
                metadata=metadata or {},
                expires_at=expires_at
            )
            
            self.signals[signal.id] = signal
            
            # Provider statistikasini yangilash
            provider.total_signals += 1
            provider.pending_signals += 1
            provider.last_signal_at = time.time()
            
            # Platform statistikasini yangilash
            self.platform_stats['total_signals'] += 1
            
            # Subscriber'larni xabardor qilish
            self._notify_subscribers(provider_id, signal)
            
            # Notification callbacks
            for callback in self.signal_notifications:
                try:
                    callback(signal)
                except Exception as e:
                    logger.error(f"Signal notification callback xatosi: {e}")
            
            logger.info(f"Yangi signal: {provider.name} - {symbol} {signal_type.value}")
            return signal.id
    
    def subscribe(
        self,
        subscriber_id: str,
        provider_id: str,
        auto_trade: bool = False,
        notification_enabled: bool = True,
        symbols_filter: List[str] = None,
        min_confidence: float = 0.0,
        min_strength: SignalStrength = SignalStrength.WEAK,
        max_risk: float = 0.05,
        callback: Callable = None
    ) -> bool:
        """Provider ga obuna bo'lish
        
        Args:
            subscriber_id: Subscriber ID
            provider_id: Provider ID
            auto_trade: Avtomatik trade qilish
            notification_enabled: Bildirishnoma yoqish
            symbols_filter: Symbollar filtri
            min_confidence: Minimal ishonchlilik
            min_strength: Minimal kuch
            max_risk: Maksimal risk
            callback: Yangi signal callback
            
        Returns:
            bool: Muvaffaqiyatli obuna bo'lganligi
        """
        with self.lock:
            # Provider mavjudligini tekshirish
            if provider_id not in self.providers:
                logger.error(f"Provider topilmadi: {provider_id}")
                return False
            
            provider = self.providers[provider_id]
            if not provider.is_active:
                logger.error(f"Provider faol emas: {provider_id}")
                return False
            
            # Obuna yaratish
            subscription = Subscription(
                subscriber_id=subscriber_id,
                provider_id=provider_id,
                provider_name=provider.name,
                auto_trade=auto_trade,
                notification_enabled=notification_enabled,
                symbols_filter=symbols_filter or [],
                min_confidence=min_confidence,
                min_strength=min_strength,
                max_risk=max_risk
            )
            
            # Mavjud obunani tekshirish
            existing_subscription = next(
                (sub for sub in self.subscriptions[subscriber_id] 
                 if sub.provider_id == provider_id),
                None
            )
            
            if existing_subscription:
                logger.warning(f"Allaqachon obuna mavjud: {provider_id}")
                return False
            
            self.subscriptions[subscriber_id].append(subscription)
            
            # Provider obunachilari sonini yangilash
            provider.subscribers.add(subscriber_id)
            provider.total_subscribers = len(provider.subscribers)
            
            # Callback qo'shish
            if callback:
                self.subscribers_callbacks[subscriber_id].append(callback)
            
            # Platform statistikasi
            self.platform_stats['total_subscribers'] += 1
            
            logger.info(f"Obuna yaratildi: {subscriber_id} -> {provider.name}")
            return True
    
    def unsubscribe(self, subscriber_id: str, provider_id: str) -> bool:
        """Provider dan obuna bo'lishni bekor qilish
        
        Args:
            subscriber_id: Subscriber ID
            provider_id: Provider ID
            
        Returns:
            bool: Muvaffaqiyatli obuna bekor qilinganligi
        """
        with self.lock:
            initial_count = len(self.subscriptions[subscriber_id])
            
            # Obunani olib tashlash
            self.subscriptions[subscriber_id] = [
                sub for sub in self.subscriptions[subscriber_id]
                if sub.provider_id != provider_id
            ]
            
            removed = initial_count - len(self.subscriptions[subscriber_id])
            
            if removed > 0:
                # Provider obunachilari sonini kamaytirish
                if provider_id in self.providers:
                    provider = self.providers[provider_id]
                    provider.subscribers.discard(subscriber_id)
                    provider.total_subscribers = len(provider.subscribers)
                
                # Callback'ları o'chirish
                if subscriber_id in self.subscribers_callbacks:
                    del self.subscribers_callbacks[subscriber_id]
                
                logger.info(f"Obuna bekor qilindi: {subscriber_id} -> {provider_id}")
                return True
            
            return False
    
    def get_signals(
        self,
        provider_id: Optional[str] = None,
        symbol: Optional[str] = None,
        signal_type: Optional[SignalType] = None,
        timeframe: Optional[TimeFrame] = None,
        min_confidence: float = 0.0,
        min_strength: Optional[SignalStrength] = None,
        status: Optional[SignalStatus] = None,
        active_only: bool = True,
        limit: int = 100,
        sort_by: str = "created_at",
        ascending: bool = False
    ) -> List[TradingSignal]:
        """Signal'larni filterlash va olish
        
        Args:
            provider_id: Provider filteri
            symbol: Instrument simbol filteri
            signal_type: Signal turi filteri
            timeframe: Vaqt freymasi filteri
            min_confidence: Minimal ishonchlilik
            min_strength: Minimal kuch
            status: Status filteri
            active_only: Faqat faol signal'larni olish
            limit: Natija limiti
            sort_by: Saralash usuli
            ascending: O'sish tartibida
            
        Returns:
            List[TradingSignal]: Filterlangan signal'lar ro'yxati
        """
        with self.lock:
            filtered_signals = []
            
            for signal in self.signals.values():
                # Faollik tekshiruvi
                if active_only and signal.status != SignalStatus.ACTIVE:
                    continue
                    
                if signal.is_expired() and active_only:
                    continue
                
                # Filterlar
                if provider_id and signal.provider_id != provider_id:
                    continue
                    
                if symbol and signal.symbol.upper() != symbol.upper():
                    continue
                    
                if signal_type and signal.signal_type != signal_type:
                    continue
                    
                if timeframe and signal.timeframe != timeframe:
                    continue
                    
                if signal.confidence < min_confidence:
                    continue
                
                if min_strength and signal.strength.value < min_strength.value:
                    continue
                
                if status and signal.status != status:
                    continue
                
                filtered_signals.append(signal)
            
            # Saralash
            if sort_by == "created_at":
                filtered_signals.sort(key=lambda x: x.created_at, reverse=not ascending)
            elif sort_by == "confidence":
                filtered_signals.sort(key=lambda x: x.confidence, reverse=not ascending)
            elif sort_by == "strength":
                filtered_signals.sort(key=lambda x: x.strength.value, reverse=not ascending)
            elif sort_by == "profit_loss":
                filtered_signals.sort(key=lambda x: x.profit_loss, reverse=not ascending)
            elif sort_by == "provider_rating":
                filtered_signals.sort(
                    key=lambda x: self.providers.get(x.provider_id, Provider()).rating,
                    reverse=not ascending
                )
            
            return filtered_signals[:limit]
    
    def get_top_providers(
        self,
        limit: int = 10,
        sort_by: str = "rating",
        min_signals: int = 0,
        verified_only: bool = False,
        premium_only: bool = False
    ) -> List[Dict]:
        """Eng yaxshi provider'larni olish
        
        Args:
            limit: Natija limiti
            sort_by: Tartiblash usuli ("rating", "success_rate", "total_signals", "subscribers")
            min_signals: Minimal signal soni
            verified_only: Faqat tasdiqlangan provider'lar
            premium_only: Faqat premium provider'lar
            
        Returns:
            List[Dict]: Provider ma'lumotlari ro'yxati
        """
        with self.lock:
            candidates = []
            
            for provider in self.providers.values():
                # Filtrlar
                if not provider.is_active:
                    continue
                
                if provider.total_signals < min_signals:
                    continue
                
                if verified_only and not provider.verified:
                    continue
                
                if premium_only and not provider.premium:
                    continue
                
                # Performance hisoblash
                performance = provider.get_recent_performance()
                
                candidates.append({
                    'id': provider.id,
                    'name': provider.name,
                    'provider_type': provider.provider_type.value,
                    'rating': provider.rating,
                    'total_signals': provider.total_signals,
                    'successful_signals': provider.successful_signals,
                    'failed_signals': provider.failed_signals,
                    'success_rate': provider.success_rate,
                    'avg_profit': provider.avg_profit,
                    'subscribers': provider.total_subscribers,
                    'verified': provider.verified,
                    'premium': provider.premium,
                    'subscription_fee': provider.subscription_fee,
                    'specialization': provider.specialization,
                    'last_signal_at': provider.last_signal_at,
                    'created_at': provider.created_at
                })
            
            # Saralash
            if sort_by == "rating":
                candidates.sort(key=lambda x: x['rating'], reverse=True)
            elif sort_by == "success_rate":
                candidates.sort(key=lambda x: x['success_rate'], reverse=True)
            elif sort_by == "total_signals":
                candidates.sort(key=lambda x: x['total_signals'], reverse=True)
            elif sort_by == "subscribers":
                candidates.sort(key=lambda x: x['subscribers'], reverse=True)
            elif sort_by == "avg_profit":
                candidates.sort(key=lambda x: x['avg_profit'], reverse=True)
            elif sort_by == "recent":
                candidates.sort(key=lambda x: x['last_signal_at'], reverse=True)
            
            return candidates[:limit]
    
    def get_provider_stats(self, provider_id: str) -> Optional[Dict]:
        """Provider statistikasini olish
        
        Args:
            provider_id: Provider ID
            
        Returns:
            Dict: Provider statistikasi yoki None
        """
        with self.lock:
            if provider_id not in self.providers:
                return None
            
            provider = self.providers[provider_id]
            
            # So'nggi 30 kundagi signallar
            cutoff_time = time.time() - (30 * 24 * 3600)
            recent_signals = [
                s for s in self.signals.values()
                if s.provider_id == provider_id and s.created_at >= cutoff_time
            ]
            
            active_signals = sum(1 for s in recent_signals if s.status == SignalStatus.ACTIVE)
            executed_signals = sum(1 for s in recent_signals if s.status == SignalStatus.EXECUTED)
            
            # Profit stats
            total_profit = sum(s.profit_loss for s in recent_signals if s.status == SignalStatus.EXECUTED)
            avg_signal_profit = total_profit / len(recent_signals) if recent_signals else 0
            
            return {
                'provider_info': {
                    'id': provider.id,
                    'name': provider.name,
                    'type': provider.provider_type.value,
                    'rating': provider.rating,
                    'verified': provider.verified,
                    'premium': provider.premium,
                    'subscription_fee': provider.subscription_fee,
                    'specialization': provider.specialization,
                    'subscribers': provider.total_subscribers,
                    'created_at': provider.created_at,
                    'last_signal_at': provider.last_signal_at
                },
                'performance': {
                    'total_signals': provider.total_signals,
                    'successful_signals': provider.successful_signals,
                    'failed_signals': provider.failed_signals,
                    'pending_signals': provider.pending_signals,
                    'success_rate': provider.success_rate,
                    'avg_profit': provider.avg_profit,
                    'total_profit': total_profit,
                    'avg_signal_profit': avg_signal_profit,
                    'recent_active_signals': active_signals,
                    'recent_executed_signals': executed_signals
                },
                'recent_signals_count': len(recent_signals),
                'monthly_stats': {
                    'signals_per_day': len(recent_signals) / 30,
                    'success_rate_monthly': provider.success_rate,
                    'avg_profit_monthly': avg_signal_profit
                }
            }
    
    def update_signal_status(
        self,
        signal_id: str,
        status: SignalStatus,
        profit_loss: float = 0.0,
        executed_at: float = None
    ) -> bool:
        """Signal statusini yangilash
        
        Args:
            signal_id: Signal ID
            status: Yangi status
            profit_loss: Foyda/zarar miqdori
            executed_at: Bajarilgan vaqt
            
        Returns:
            bool: Yangilash muvaffaqiyatli yoki yo'q
        """
        with self.lock:
            if signal_id not in self.signals:
                return False
            
            signal = self.signals[signal_id]
            old_status = signal.status
            
            signal.status = status
            signal.profit_loss = profit_loss
            if executed_at:
                signal.executed_at = executed_at
            
            # Provider stats yangilash
            if signal.provider_id in self.providers:
                provider = self.providers[signal.provider_id]
                
                if old_status == SignalStatus.PENDING and status == SignalStatus.EXECUTED:
                    provider.pending_signals -= 1
                
                if status == SignalStatus.EXECUTED:
                    if profit_loss > 0:
                        provider.successful_signals += 1
                    else:
                        provider.failed_signals += 1
                    
                    provider.update_success_rate()
                    
                    # Avg profit yangilash
                    executed_count = provider.successful_signals + provider.failed_signals
                    if executed_count > 0:
                        provider.avg_profit = (
                            (provider.avg_profit * (executed_count - 1) + profit_loss) / executed_count
                        )
            
            logger.info(f"Signal status yangilandi: {signal_id} -> {status.value}")
            return True
    
    def get_subscriber_signals(self, subscriber_id: str, limit: int = 50) -> List[TradingSignal]:
        """Obunachi uchun signallar
        
        Args:
            subscriber_id: Subscriber ID
            limit: Natija limiti
            
        Returns:
            List[TradingSignal]: Obunachi uchun signallar
        """
        if subscriber_id not in self.subscriptions:
            return []
        
        provider_ids = [sub.provider_id for sub in self.subscriptions[subscriber_id] if sub.active]
        
        signals = [
            signal for signal in self.signals.values()
            if signal.provider_id in provider_ids
            and signal.status == SignalStatus.ACTIVE
            and not signal.is_expired()
        ]
        
        # Subscription filterlarini qo'llash
        filtered_signals = []
        for signal in signals:
            subscription = next(
                (sub for sub in self.subscriptions[subscriber_id]
                 if sub.provider_id == signal.provider_id and sub.active),
                None
            )
            
            if subscription and subscription.matches_filter(signal):
                filtered_signals.append(signal)
        
        # Vaqt bo'yicha saralash
        filtered_signals.sort(key=lambda x: x.created_at, reverse=True)
        return filtered_signals[:limit]
    
    def search_signals(
        self,
        query: str,
        search_fields: List[str] = None,
        case_sensitive: bool = False
    ) -> List[TradingSignal]:
        """Signal'larni qidirish
        
        Args:
            query: Qidiruv so'zi
            search_fields: Qidirish maydonlari
            case_sensitive: Katta-kichik harf sezgir
            
        Returns:
            List[TradingSignal]: Topilgan signallar
        """
        if search_fields is None:
            search_fields = ['description', 'analysis', 'tags', 'symbol']
        
        if not case_sensitive:
            query = query.lower()
        
        results = []
        for signal in self.signals.values():
            match = False
            
            for field in search_fields:
                if field == 'description' and query in (signal.description.lower() if not case_sensitive else signal.description):
                    match = True
                    break
                elif field == 'analysis' and query in (signal.analysis.lower() if not case_sensitive else signal.analysis):
                    match = True
                    break
                elif field == 'symbol' and query in (signal.symbol.lower() if not case_sensitive else signal.symbol):
                    match = True
                    break
                elif field == 'tags' and any(query in tag.lower() if not case_sensitive else query in tag for tag in signal.tags):
                    match = True
                    break
            
            if match:
                results.append(signal)
        
        # Vaqt bo'yicha saralash
        results.sort(key=lambda x: x.created_at, reverse=True)
        return results
    
    def get_signal_performance_analysis(self, days: int = 30) -> Dict:
        """Platform performance tahlili
        
        Args:
            days: Analiz davri (kunlar)
            
        Returns:
            Dict: Performance ma'lumotlari
        """
        cutoff_time = time.time() - (days * 24 * 3600)
        
        # Bu davrdagi signallar
        period_signals = [
            signal for signal in self.signals.values()
            if signal.created_at >= cutoff_time
        ]
        
        # Provider performance
        provider_performance = {}
        for provider in self.providers.values():
            provider_signals = [
                s for s in period_signals if s.provider_id == provider.id
            ]
            
            if provider_signals:
                profitable = sum(1 for s in provider_signals if s.profit_loss > 0)
                total_profit = sum(s.profit_loss for s in provider_signals)
                avg_confidence = sum(s.confidence for s in provider_signals) / len(provider_signals)
                
                provider_performance[provider.id] = {
                    'name': provider.name,
                    'signals_count': len(provider_signals),
                    'profitable_signals': profitable,
                    'profitability_rate': (profitable / len(provider_signals)) * 100,
                    'total_profit': total_profit,
                    'avg_confidence': avg_confidence,
                    'rating': provider.rating
                }
        
        return {
            'period_days': days,
            'total_signals': len(period_signals),
            'active_signals': sum(1 for s in period_signals if s.status == SignalStatus.ACTIVE),
            'executed_signals': sum(1 for s in period_signals if s.status == SignalStatus.EXECUTED),
            'total_profit': sum(s.profit_loss for s in period_signals),
            'avg_signal_confidence': sum(s.confidence for s in period_signals) / len(period_signals) if period_signals else 0,
            'provider_performance': provider_performance,
            'platform_stats': self.platform_stats.copy()
        }
    
    def _notify_subscribers(self, provider_id: str, signal: TradingSignal):
        """Obunachilarni yangi signal haqida xabardor qilish"""
        provider = self.providers.get(provider_id)
        if not provider:
            return
        
        notified_count = 0
        for subscriber_id in provider.subscribers:
            subscription = next(
                (sub for sub in self.subscriptions.get(subscriber_id, [])
                 if sub.provider_id == provider_id and sub.active),
                None
            )
            
            if not subscription or not subscription.notification_enabled:
                continue
            
            if not subscription.matches_filter(signal):
                continue
            
            # Callback'larni chaqirish
            callbacks = self.subscribers_callbacks.get(subscriber_id, [])
            for callback in callbacks:
                try:
                    callback(signal, subscription)
                except Exception as e:
                    logger.error(f"Callback xatosi {subscriber_id} uchun: {e}")
            
            notified_count += 1
        
        # Signal ko'rishlar sonini yangilash
        signal.views += 1
    
    def add_signal_callback(self, callback: Callable[[TradingSignal, Subscription], None]):
        """Signal notification callback qo'shish"""
        self.signal_notifications.append(callback)
    
    def remove_provider(self, provider_id: str) -> bool:
        """Provider ni o'chirish (deaktivatsiya qilish)
        
        Args:
            provider_id: Provider ID
            
        Returns:
            bool: Muvaffaqiyatli o'chirilganligi
        """
        with self.lock:
            if provider_id not in self.providers:
                return False
            
            provider = self.providers[provider_id]
            provider.is_active = False
            
            # Provider signallarini deaktiv qilish
            for signal in self.signals.values():
                if signal.provider_id == provider_id and signal.status == SignalStatus.ACTIVE:
                    signal.status = SignalStatus.CANCELLED
            
            # Obunachilarni xabardor qilish
            for subscriber_id in list(provider.subscribers):
                self.unsubscribe(subscriber_id, provider_id)
            
            self.platform_stats['active_providers'] -= 1
            
            logger.info(f"Provider olib tashlandi: {provider.name}")
            return True
    
    def get_platform_stats(self) -> Dict:
        """Platform umumiy statistikasi"""
        with self.lock:
            # Active providers
            active_providers = len([p for p in self.providers.values() if p.is_active])
            
            # Recent signals (oxirgi 24 soat)
            cutoff_24h = time.time() - (24 * 3600)
            recent_signals = [s for s in self.signals.values() if s.created_at >= cutoff_24h]
            
            # Top symbols
            symbol_counts = defaultdict(int)
            for signal in recent_signals:
                symbol_counts[signal.symbol] += 1
            
            top_symbols = sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Success rate by provider type
            provider_type_success = {}
            for provider_type in SignalProvider:
                signals = [s for s in recent_signals if s.provider_type == provider_type]
                if signals:
                    successful = sum(1 for s in signals if s.profit_loss > 0)
                    provider_type_success[provider_type.value] = {
                        'signals': len(signals),
                        'success_rate': (successful / len(signals)) * 100,
                        'avg_confidence': sum(s.confidence for s in signals) / len(signals)
                    }
            
            return {
                'total_providers': len(self.providers),
                'active_providers': active_providers,
                'total_subscribers': sum(len(sub_list) for sub_list in self.subscriptions.values()),
                'total_signals': len(self.signals),
                'recent_signals_24h': len(recent_signals),
                'active_signals': sum(1 for s in self.signals.values() if s.status == SignalStatus.ACTIVE),
                'avg_provider_rating': sum(p.rating for p in self.providers.values()) / max(1, len(self.providers)),
                'top_symbols': top_symbols,
                'provider_type_performance': provider_type_success,
                'platform_uptime': time.time() - min(p.created_at for p in self.providers.values()) if self.providers else 0
            }
    
    def export_data(self, filename: str = "signal_platform_export.json"):
        """Platform ma'lumotlarini eksport qilish
        
        Args:
            filename: Fayl nomi
        """
        with self.lock:
            data = {
                'export_timestamp': datetime.now().isoformat(),
                'platform_stats': self.get_platform_stats(),
                'providers': {
                    pid: {
                        'info': {
                            'id': p.id,
                            'name': p.name,
                            'type': p.provider_type.value,
                            'rating': p.rating,
                            'total_signals': p.total_signals,
                            'success_rate': p.success_rate,
                            'verified': p.verified,
                            'premium': p.premium
                        },
                        'stats': self.get_provider_stats(pid)
                    }
                    for pid, p in self.providers.items()
                },
                'signals': {
                    sid: signal.to_dict()
                    for sid, signal in self.signals.items()
                },
                'subscriptions_count': len(self.subscriptions)
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Ma'lumotlar eksport qilindi: {filename}")


# Misol foydalanish
async def example_usage():
    """Platform dan foydalanish misoli"""
    platform = SignalPlatform()
    
    # Providers ro'yxatdan o'tkazish
    quantum_id = platform.register_provider(
        name="Quantum AI Trading",
        provider_type=SignalProvider.QUANTUM_ALGO,
        description="Quantum algoritmlari asosida trading signals",
        rating=4.8,
        verified=True,
        premium=True,
        specialization=["Forex", "Crypto"]
    )
    
    gpt5_id = platform.register_provider(
        name="GPT5 Sentiment Analysis",
        provider_type=SignalProvider.GPT5_SENTIMENT,
        description="Sentiment tahlil asosida signals",
        rating=4.5,
        specialization=["Stocks", "Commodities"]
    )
    
    # Signal callback
    def signal_callback(signal: TradingSignal, subscription: Subscription):
        print(f"🟢 Yangi signal: {signal.provider_name} - {signal.symbol} {signal.signal_type.value}")
        print(f"   💰 Kirish: {signal.entry_price}, SL: {signal.stop_loss}, TP: {signal.take_profit}")
        print(f"   📊 Ishonchlilik: {signal.confidence:.2f}, Kuch: {signal.strength.name}")
        
        if subscription.auto_trade:
            print(f"   🤖 Avtomatik trade bajariladi...")
    
    # Obuna bo'lish
    platform.subscribe(
        subscriber_id="user_123",
        provider_id=quantum_id,
        auto_trade=False,
        min_confidence=0.7,
        min_strength=SignalStrength.STRONG,
        callback=signal_callback
    )
    
    # Signal chop etish
    signal1_id = platform.publish_signal(
        provider_id=quantum_id,
        symbol="EURUSD",
        signal_type=SignalType.BUY,
        timeframe=TimeFrame.H1,
        entry_price=1.0950,
        stop_loss=1.0900,
        take_profit=1.1000,
        confidence=0.85,
        strength=SignalStrength.STRONG,
        description="Quantum algorithm buy signal",
        analysis="Strong bullish momentum detected with high confidence",
        tags=["EUR", "USD", "forex", "bullish"]
    )
    
    signal2_id = platform.publish_signal(
        provider_id=gpt5_id,
        symbol="BTCUSD",
        signal_type=SignalType.SELL,
        timeframe=TimeFrame.M15,
        entry_price=45000,
        stop_loss=47000,
        take_profit=42000,
        confidence=0.72,
        strength=SignalStrength.MODERATE,
        description="GPT5 sentiment sell signal",
        analysis="Negative sentiment detected in crypto markets"
    )
    
    # Signal'larni olish
    eur_signals = platform.get_signals(
        symbol="EURUSD",
        min_confidence=0.7,
        limit=10
    )
    print(f"\n📈 EURUSD signallari: {len(eur_signals)} ta")
    
    # Top provider'lar
    top_providers = platform.get_top_providers(limit=5, sort_by="rating")
    print(f"\n🏆 Top provider'lar:")
    for i, provider in enumerate(top_providers, 1):
        print(f"   {i}. {provider['name']} - Rating: {provider['rating']:.1f}")
    
    # Platform statistikasi
    stats = platform.get_platform_stats()
    print(f"\n📊 Platform statistikasi:")
    print(f"   Provider'lar: {stats['active_providers']}")
    print(f"   Subscriber'lar: {stats['total_subscribers']}")
    print(f"   Faol signallar: {stats['active_signals']}")
    
    # Provider performance
    provider_stats = platform.get_provider_stats(quantum_id)
    if provider_stats:
        print(f"\n🎯 {provider_stats['provider_info']['name']} performance:")
        print(f"   Signallar: {provider_stats['performance']['total_signals']}")
        print(f"   Success rate: {provider_stats['performance']['success_rate']:.1f}%")
    
    # Signal status yangilash
    platform.update_signal_status(
        signal1_id,
        SignalStatus.EXECUTED,
        profit_loss=50.0
    )
    
    # Platform performance tahlili
    analysis = platform.get_signal_performance_analysis(days=7)
    print(f"\n📈 7 kunlik tahlil:")
    print(f"   Jami signallar: {analysis['total_signals']}")
    print(f"   Jami foyda: {analysis['total_profit']:.2f}")


if __name__ == "__main__":
    import asyncio
    
    # Logging setup
    logging.basicConfig(level=logging.INFO)
    
    # Misol ishga tushirish
    asyncio.run(example_usage())