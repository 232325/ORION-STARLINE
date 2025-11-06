"""
AI Signal Marketplace - Asosiy marketplace tizimi

Premium AI signal marketplace tizimi. Signal creator va subscriber 
platformasi sifatida ishlaydi, signal almashinuvi va boshqarish 
imkoniyatlarini ta'minlaydi.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np
import pandas as pd
from decimal import Decimal
import hashlib
import jwt
from pathlib import Path

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalType(Enum):
    """Signal turlari"""
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"
    QUANTUM = "quantum"
    AI_ML = "ai_ml"
    HYBRID = "hybrid"
    ARBITRAGE = "arbitrage"
    SCALPING = "scalping"
    SWING = "swing"
    LONG_TERM = "long_term"

class SignalStatus(Enum):
    """Signal holatlari"""
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    ENDED = "ended"
    ARCHIVED = "archived"

class SignalQuality(Enum):
    """Signal sifat darajasi"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

class UserTier(Enum):
    """Foydalanuvchi darajasi"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ELITE = "elite"
    VIP = "vip"

@dataclass
class PerformanceMetrics:
    """Signal performans metrikalari"""
    win_rate: float = 0.0
    profit_factor: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    total_return: float = 0.0
    volatility: float = 0.0
    calmar_ratio: float = 0.0
    sortino_ratio: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RiskAssessment:
    """Risk baholashi"""
    risk_score: float = 0.0  # 0-100
    risk_level: str = "low"  # low, medium, high, extreme
    risk_factors: List[str] = field(default_factory=list)
    max_position_size: float = 1.0  # portfolio % da
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_adjusted_return: float = 0.0
    value_at_risk: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class SignalData:
    """Signal ma'lumotlari"""
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    title: str = ""
    description: str = ""
    signal_type: SignalType = SignalType.TECHNICAL
    symbols: List[str] = field(default_factory=list)
    timeframe: str = "1h"
    price: float = 0.0
    currency: str = "USD"
    status: SignalStatus = SignalStatus.PAUSED
    quality_rating: SignalQuality = SignalQuality.BRONZE
    total_subscribers: int = 0
    active_subscribers: int = 0
    rating: float = 0.0
    total_ratings: int = 0
    performance: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    risk_assessment: RiskAssessment = field(default_factory=RiskAssessment)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    documentation: Dict[str, Any] = field(default_factory=dict)
    verification_status: str = "pending"
    verification_date: Optional[datetime] = None
    community_score: float = 0.0
    ai_score: float = 0.0

@dataclass
class UserProfile:
    """Foydalanuvchi profili"""
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    tier: UserTier = UserTier.FREE
    created_at: datetime = field(default_factory=datetime.now)
    total_earned: float = 0.0
    total_spent: float = 0.0
    reputation_score: float = 0.0
    verification_level: str = "basic"
    preferred_language: str = "uz"
    timezone: str = "UTC"
    preferences: Dict[str, Any] = field(default_factory=dict)

class SignalMarketplace:
    """AI Signal Marketplace asosiy klassi"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.signals: Dict[str, SignalData] = {}
        self.users: Dict[str, UserProfile] = {}
        self.subscriptions: Dict[str, Dict[str, Any]] = {}
        self.ratings: Dict[str, List[Dict[str, Any]]] = {}
        self.analytics: Dict[str, Any] = {}
        self.access_control = AccessControl()
        self.quality_verifier = QualityVerifier()
        self.performance_tracker = PerformanceTracker()
        self.community_manager = CommunityManager()
        self._initialize_system()
    
    def _initialize_system(self):
        """Tizimni boshlash"""
        logger.info("AI Signal Marketplace tizimi boshlanmoqda...")
        
        # Tizim sozlamalari
        self.commission_rate = 0.05  # 5% komissiya
        self.minimum_rating = 3.0
        self.subscription_discounts = {
            UserTier.FREE: 0.0,
            UserTier.BASIC: 0.1,
            UserTier.PREMIUM: 0.2,
            UserTier.ELITE: 0.3,
            UserTier.VIP: 0.4
        }
        
        # Cache
        self.cache = {
            "top_signals": [],
            "trending_signals": [],
            "featured_signals": [],
            "recent_signals": []
        }
        
        logger.info("AI Signal Marketplace tizimi tayyor!")
    
    async def create_signal(self, 
                          creator_id: str,
                          title: str,
                          description: str,
                          signal_type: SignalType,
                          symbols: List[str],
                          timeframe: str,
                          price: float,
                          **kwargs) -> str:
        """
        Yangi signal yaratish
        
        Args:
            creator_id: Signal yaratuvchi ID
            title: Signal nomi
            description: Signal tavsifi
            signal_type: Signal turi
            symbols: Savdo qilinadigan instrumentlar
            timeframe: Vaqt oralig'i
            price: Narx
        
        Returns:
            signal_id: Signal ID
        """
        try:
            # Foydalanuvchi tekshiruvi
            if creator_id not in self.users:
                raise ValueError("Foydalanuvchi topilmadi")
            
            # Signal ma'lumotlari
            signal_data = SignalData(
                creator_id=creator_id,
                title=title,
                description=description,
                signal_type=signal_type,
                symbols=symbols,
                timeframe=timeframe,
                price=price,
                **kwargs
            )
            
            # Risk baholash
            risk_assessment = await self._assess_signal_risk(signal_data)
            signal_data.risk_assessment = risk_assessment
            
            # Sifat baholash
            quality_score = await self._calculate_quality_score(signal_data)
            signal_data.quality_rating = self._get_quality_tier(quality_score)
            signal_data.ai_score = quality_score
            
            # Saqlash
            self.signals[signal_data.signal_id] = signal_data
            
            # Performance tracking
            await self.performance_tracker.initialize_signal(signal_data.signal_id)
            
            # Community score
            signal_data.community_score = await self._calculate_community_score(signal_data)
            
            logger.info(f"Signal yaratildi: {signal_data.signal_id}")
            return signal_data.signal_id
            
        except Exception as e:
            logger.error(f"Signal yaratish xatosi: {e}")
            raise
    
    async def subscribe_to_signal(self, 
                                user_id: str,
                                signal_id: str,
                                plan_type: str = "monthly") -> bool:
        """
        Signalga obuna bo'lish
        
        Args:
            user_id: Foydalanuvchi ID
            signal_id: Signal ID
            plan_type: Obuna rejasi
        
        Returns:
            bool: Muvaffaqiyat holati
        """
        try:
            # Foydalanuvchi va signal tekshiruvi
            if user_id not in self.users:
                raise ValueError("Foydalanuvchi topilmadi")
            
            if signal_id not in self.signals:
                raise ValueError("Signal topilmadi")
            
            signal = self.signals[signal_id]
            user = self.users[user_id]
            
            # Obuna narxini hisoblash
            base_price = signal.price
            discount = self.subscription_discounts.get(user.tier, 0.0)
            actual_price = base_price * (1 - discount)
            
            # Access control
            if not await self.access_control.can_access(user_id, signal):
                raise ValueError("Bu signalga kirish huquqi yo'q")
            
            # Obuna yaratish
            subscription_data = {
                "subscription_id": str(uuid.uuid4()),
                "user_id": user_id,
                "signal_id": signal_id,
                "plan_type": plan_type,
                "price": actual_price,
                "currency": signal.currency,
                "start_date": datetime.now(),
                "end_date": self._calculate_end_date(plan_type),
                "status": "active",
                "auto_renew": True,
                "created_at": datetime.now()
            }
            
            # Saqlash
            if user_id not in self.subscriptions:
                self.subscriptions[user_id] = {}
            
            self.subscriptions[user_id][signal_id] = subscription_data
            
            # Signal statistikasi yangilash
            signal.active_subscribers += 1
            signal.total_subscribers += 1
            signal.updated_at = datetime.now()
            
            logger.info(f"Obuna yaratildi: {subscription_data['subscription_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Obuna yaratish xatosi: {e}")
            return False
    
    async def rate_signal(self,
                         user_id: str,
                         signal_id: str,
                         rating: float,
                         review: str = "") -> bool:
        """
        Signalga baho berish
        
        Args:
            user_id: Foydalanuvchi ID
            signal_id: Signal ID
            rating: Baho (1-5)
            review: Sharh
        
        Returns:
            bool: Muvaffaqiyat holati
        """
        try:
            # Tekshiruv
            if user_id not in self.users or signal_id not in self.signals:
                return False
            
            # Obuna mavjudligini tekshirish
            if user_id not in self.subscriptions or signal_id not in self.subscriptions[user_id]:
                return False
            
            # Rating cheklovi
            rating = max(1.0, min(5.0, rating))
            
            # Rating saqlash
            if signal_id not in self.ratings:
                self.ratings[signal_id] = []
            
            self.ratings[signal_id].append({
                "user_id": user_id,
                "rating": rating,
                "review": review,
                "timestamp": datetime.now()
            })
            
            # O'rtacha hisoblash
            signal = self.signals[signal_id]
            total_rating = sum(r["rating"] for r in self.ratings[signal_id])
            total_count = len(self.ratings[signal_id])
            
            signal.rating = total_rating / total_count
            signal.total_ratings = total_count
            signal.updated_at = datetime.now()
            
            # Community score yangilash
            signal.community_score = await self._calculate_community_score(signal)
            
            logger.info(f"Baho berildi: {signal_id} - {rating}")
            return True
            
        except Exception as e:
            logger.error(f"Baho berish xatosi: {e}")
            return False
    
    async def get_signal_performance(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """
        Signal performansini olish
        
        Args:
            signal_id: Signal ID
        
        Returns:
            Dict: Performance ma'lumotlari
        """
        try:
            if signal_id not in self.signals:
                return None
            
            signal = self.signals[signal_id]
            
            # Performance metrics
            performance_data = {
                "signal_id": signal_id,
                "signal_title": signal.title,
                "creator_id": signal.creator_id,
                "signal_type": signal.signal_type.value,
                "performance": {
                    "win_rate": signal.performance.win_rate,
                    "profit_factor": signal.performance.profit_factor,
                    "max_drawdown": signal.performance.max_drawdown,
                    "sharpe_ratio": signal.performance.sharpe_ratio,
                    "total_trades": signal.performance.total_trades,
                    "winning_trades": signal.performance.winning_trades,
                    "losing_trades": signal.performance.losing_trades,
                    "total_return": signal.performance.total_return,
                    "volatility": signal.performance.volatility,
                    "calmar_ratio": signal.performance.calmar_ratio,
                    "sortino_ratio": signal.performance.sortino_ratio
                },
                "risk_assessment": {
                    "risk_score": signal.risk_assessment.risk_score,
                    "risk_level": signal.risk_assessment.risk_level,
                    "risk_factors": signal.risk_assessment.risk_factors,
                    "max_position_size": signal.risk_assessment.max_position_size,
                    "value_at_risk": signal.risk_assessment.value_at_risk
                },
                "quality_scores": {
                    "quality_rating": signal.quality_rating.value,
                    "community_score": signal.community_score,
                    "ai_score": signal.ai_score,
                    "overall_score": (signal.community_score + signal.ai_score) / 2
                },
                "subscription_stats": {
                    "total_subscribers": signal.total_subscribers,
                    "active_subscribers": signal.active_subscribers,
                    "rating": signal.rating,
                    "total_ratings": signal.total_ratings
                }
            }
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Performance olish xatosi: {e}")
            return None
    
    async def search_signals(self,
                           query: str = "",
                           signal_type: Optional[SignalType] = None,
                           min_rating: float = 0.0,
                           max_price: float = float('inf'),
                           sort_by: str = "rating",
                           limit: int = 20) -> List[Dict[str, Any]]:
        """
        Signal qidiruvi
        
        Args:
            query: Qidiruv so'rovi
            signal_type: Signal turi
            min_rating: Minimal baho
            max_price: Maksimal narx
            sort_by: Saralash mezoni
            limit: Limit
        
        Returns:
            List: Signal ro'yxati
        """
        try:
            results = []
            
            for signal in self.signals.values():
                # Filter criteria
                if signal_type and signal.signal_type != signal_type:
                    continue
                
                if signal.rating < min_rating:
                    continue
                
                if signal.price > max_price:
                    continue
                
                if query:
                    query_lower = query.lower()
                    if (query_lower not in signal.title.lower() and
                        query_lower not in signal.description.lower() and
                        not any(query_lower in tag.lower() for tag in signal.tags)):
                        continue
                
                # Result ma'lumotlari
                result = {
                    "signal_id": signal.signal_id,
                    "title": signal.title,
                    "description": signal.description[:200] + "..." if len(signal.description) > 200 else signal.description,
                    "signal_type": signal.signal_type.value,
                    "price": signal.price,
                    "currency": signal.currency,
                    "rating": signal.rating,
                    "total_ratings": signal.total_ratings,
                    "subscribers": signal.active_subscribers,
                    "quality_rating": signal.quality_rating.value,
                    "risk_level": signal.risk_assessment.risk_level,
                    "tags": signal.tags,
                    "created_at": signal.created_at.isoformat()
                }
                results.append(result)
            
            # Saralash
            if sort_by == "rating":
                results.sort(key=lambda x: x["rating"], reverse=True)
            elif sort_by == "price":
                results.sort(key=lambda x: x["price"])
            elif sort_by == "subscribers":
                results.sort(key=lambda x: x["subscribers"], reverse=True)
            elif sort_by == "newest":
                results.sort(key=lambda x: x["created_at"], reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Qidiruv xatosi: {e}")
            return []
    
    async def get_marketplace_statistics(self) -> Dict[str, Any]:
        """
        Marketplace statistikasi
        
        Returns:
            Dict: Statistika ma'lumotlari
        """
        try:
            stats = {
                "total_signals": len(self.signals),
                "active_signals": len([s for s in self.signals.values() if s.status == SignalStatus.ACTIVE]),
                "total_users": len(self.users),
                "total_subscriptions": sum(len(user_subs) for user_subs in self.subscriptions.values()),
                "total_revenue": 0.0,
                "average_rating": 0.0,
                "signals_by_type": {},
                "signals_by_quality": {},
                "top_performers": []
            }
            
            # Revenue hisoblash
            total_revenue = 0.0
            all_ratings = []
            
            for signal in self.signals.values():
                # Signal turi bo'yicha
                signal_type = signal.signal_type.value
                stats["signals_by_type"][signal_type] = stats["signals_by_type"].get(signal_type, 0) + 1
                
                # Sifat bo'yicha
                quality = signal.quality_rating.value
                stats["signals_by_quality"][quality] = stats["signals_by_quality"].get(quality, 0) + 1
                
                # Rating
                if signal.rating > 0:
                    all_ratings.append(signal.rating)
                
                # Revenue
                total_revenue += signal.price * signal.total_subscribers
            
            stats["total_revenue"] = total_revenue
            stats["average_rating"] = sum(all_ratings) / len(all_ratings) if all_ratings else 0.0
            
            # Top performers
            sorted_signals = sorted(self.signals.values(), 
                                  key=lambda x: x.performance.sharpe_ratio, 
                                  reverse=True)[:10]
            
            stats["top_performers"] = [
                {
                    "signal_id": s.signal_id,
                    "title": s.title,
                    "sharpe_ratio": s.performance.sharpe_ratio,
                    "win_rate": s.performance.win_rate
                }
                for s in sorted_signals
            ]
            
            return stats
            
        except Exception as e:
            logger.error(f"Statistika xatosi: {e}")
            return {}
    
    async def _assess_signal_risk(self, signal: SignalData) -> RiskAssessment:
        """Signal riskini baholash"""
        risk_score = 0.0
        risk_factors = []
        
        # Volatility based risk
        if signal.performance.volatility > 0.2:
            risk_score += 20
            risk_factors.append("Yuqori volatility")
        
        # Drawdown based risk
        if signal.performance.max_drawdown > 0.3:
            risk_score += 25
            risk_factors.append("Katta drawdown")
        
        # Win rate risk
        if signal.performance.win_rate < 0.4:
            risk_score += 15
            risk_factors.append("Past win rate")
        
        # Signal type risk
        type_risk_map = {
            SignalType.SCALPING: 15,
            SignalType.ARBITRAGE: 10,
            SignalType.AI_ML: 5,
            SignalType.QUANTUM: 8
        }
        risk_score += type_risk_map.get(signal.signal_type, 5)
        
        # Risk level
        if risk_score >= 80:
            risk_level = "extreme"
        elif risk_score >= 60:
            risk_level = "high"
        elif risk_score >= 40:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return RiskAssessment(
            risk_score=risk_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            value_at_risk=signal.performance.total_return * 0.05
        )
    
    async def _calculate_quality_score(self, signal: SignalData) -> float:
        """Signal sifatini hisoblash"""
        score = 0.0
        
        # Performance metriklari (40%)
        if signal.performance.total_trades > 0:
            performance_score = (
                signal.performance.win_rate * 20 +
                min(signal.performance.sharpe_ratio * 5, 20) +
                (1 - signal.performance.max_drawdown) * 20
            ) / 60
            score += performance_score * 0.4
        
        # Community metriklari (30%)
        if signal.total_ratings > 0:
            community_score = signal.rating / 5.0
            score += community_score * 0.3
        
        # Dokumentatsiya va testing (20%)
        doc_score = 0.0
        if signal.documentation.get("description"):
            doc_score += 0.3
        if signal.documentation.get("strategy_code"):
            doc_score += 0.4
        if signal.documentation.get("backtest_results"):
            doc_score += 0.3
        score += doc_score * 0.2
        
        # Verification (10%)
        verification_score = 1.0 if signal.verification_status == "verified" else 0.5
        score += verification_score * 0.1
        
        return score * 100
    
    def _get_quality_tier(self, score: float) -> SignalQuality:
        """Sifat tierini aniqlash"""
        if score >= 90:
            return SignalQuality.DIAMOND
        elif score >= 80:
            return SignalQuality.PLATINUM
        elif score >= 70:
            return SignalQuality.GOLD
        elif score >= 60:
            return SignalQuality.SILVER
        else:
            return SignalQuality.BRONZE
    
    async def _calculate_community_score(self, signal: SignalData) -> float:
        """Community score hisoblash"""
        if signal.total_ratings == 0:
            return 0.0
        
        # Base rating
        base_score = signal.rating * 20  # Max 100
        
        # Active subscribers factor
        sub_factor = min(signal.active_subscribers / 100, 1.0) * 10
        
        # Recent activity factor
        days_old = (datetime.now() - signal.created_at).days
        activity_factor = max(0, (30 - days_old) / 30) * 5
        
        # Reviews quality
        review_factor = min(signal.total_ratings / 10, 1.0) * 5
        
        return base_score + sub_factor + activity_factor + review_factor
    
    def _calculate_end_date(self, plan_type: str) -> datetime:
        """Obuna tugash vaqti"""
        now = datetime.now()
        if plan_type == "monthly":
            return now + timedelta(days=30)
        elif plan_type == "quarterly":
            return now + timedelta(days=90)
        elif plan_type == "yearly":
            return now + timedelta(days=365)
        else:
            return now + timedelta(days=30)

class AccessControl:
    """Kirish huquqlarini boshqarish"""
    
    def __init__(self):
        self.access_rules = {
            UserTier.FREE: {
                "max_signals": 3,
                "max_commodities": 1,
                "features": ["basic_signals", "basic_analytics"]
            },
            UserTier.BASIC: {
                "max_signals": 10,
                "max_commodities": 3,
                "features": ["basic_signals", "advanced_analytics", "alerts"]
            },
            UserTier.PREMIUM: {
                "max_signals": 50,
                "max_commodities": 10,
                "features": ["all_signals", "premium_analytics", "alerts", "api_access"]
            },
            UserTier.ELITE: {
                "max_signals": 200,
                "max_commodities": 50,
                "features": ["all_signals", "elite_analytics", "alerts", "api_access", "custom_strategies"]
            },
            UserTier.VIP: {
                "max_signals": -1,  # Unlimited
                "max_commodities": -1,
                "features": ["all_signals", "vip_analytics", "alerts", "api_access", "custom_strategies", "priority_support"]
            }
        }
    
    async def can_access(self, user_id: str, signal: SignalData) -> bool:
        """Foydalanuvchi signalga kirish huquqini tekshirish"""
        # Implement access logic here
        return True  # Simplified

class QualityVerifier:
    """Signal sifatini tekshirish"""
    
    async def verify_signal(self, signal: SignalData) -> bool:
        """Signalni tasdiqlash"""
        # Implement verification logic
        signal.verification_status = "verified"
        signal.verification_date = datetime.now()
        return True

class PerformanceTracker:
    """Signal performansini kuzatish"""
    
    def __init__(self):
        self.signal_data = {}
    
    async def initialize_signal(self, signal_id: str):
        """Signal performansini boshlash"""
        self.signal_data[signal_id] = {
            "trades": [],
            "equity_curve": [],
            "drawdown_curve": []
        }
    
    async def update_performance(self, signal_id: str, performance: PerformanceMetrics):
        """Performans ma'lumotlarini yangilash"""
        if signal_id in self.signal_data:
            self.signal_data[signal_id]["metrics"] = performance

class CommunityManager:
    """Jamiyat boshqaruvi"""
    
    def __init__(self):
        self.community_metrics = {}
    
    async def get_community_insights(self, signal_id: str) -> Dict[str, Any]:
        """Jamiyat insights"""
        return {
            "popularity_score": 0.0,
            "trend_status": "stable",
            "community_recommendations": []
        }

# Demo va test
async def demo_signal_marketplace():
    """Signal marketplace demo"""
    print("=== AI Signal Marketplace Demo ===\n")
    
    # Marketplace yaratish
    marketplace = SignalMarketplace()
    
    # Demo foydalanuvchilar
    users = [
        {"username": "trader_ali", "email": "ali@example.com", "tier": UserTier.PREMIUM},
        {"username": "analyst_zara", "email": "zara@example.com", "tier": UserTier.ELITE},
        {"username": "newbie_hasan", "email": "hasan@example.com", "tier": UserTier.FREE}
    ]
    
    # Foydalanuvchilarni qo'shish
    for user_data in users:
        user = UserProfile(**user_data)
        marketplace.users[user.user_id] = user
        print(f"Foydalanuvchi yaratildi: {user.username} ({user.tier.value})")
    
    # Demo signal yaratish
    creator_id = list(marketplace.users.keys())[0]
    signal_types = [SignalType.TECHNICAL, SignalType.AI_ML, SignalType.HYBRID]
    
    for i, signal_type in enumerate(signal_types):
        signal_id = await marketplace.create_signal(
            creator_id=creator_id,
            title=f"AI Signal {i+1}: {signal_type.value.title()}",
            description=f"{signal_type.value.title()} trading signal with advanced AI analysis",
            signal_type=signal_type,
            symbols=["EURUSD", "GBPUSD", "USDJPY"],
            timeframe="1h",
            price=99.99 + i * 50,
            performance=PerformanceMetrics(
                win_rate=0.6 + i * 0.1,
                profit_factor=1.5 + i * 0.3,
                max_drawdown=0.1 + i * 0.05,
                sharpe_ratio=1.2 + i * 0.3,
                total_trades=100 + i * 50,
                total_return=0.15 + i * 0.05
            )
        )
        print(f"Signal yaratildi: {marketplace.signals[signal_id].title}")
    
    # Obuna yaratish
    user_ids = list(marketplace.users.keys())
    signal_ids = list(marketplace.signals.keys())
    
    for user_id in user_ids[1:]:  # Oxirgi foydalanuvchidan boshqa hamma
        for signal_id in signal_ids[:2]:  # Birinchi 2 ta signal
            success = await marketplace.subscribe_to_signal(user_id, signal_id)
            if success:
                print(f"Obuna yaratildi: {user_id} -> {signal_id}")
    
    # Baho berish
    for user_id in user_ids:
        for signal_id in signal_ids:
            rating = np.random.uniform(3.0, 5.0)
            review = "Excellent signal performance!" if rating > 4.0 else "Good results"
            await marketplace.rate_signal(user_id, signal_id, rating, review)
    
    # Qidiruv test
    print("\n=== Qidiruv Natijalari ===")
    results = await marketplace.search_signals(
        query="AI",
        min_rating=4.0,
        sort_by="rating",
        limit=5
    )
    
    for result in results:
        print(f"- {result['title']} (Rating: {result['rating']:.1f}, Narx: ${result['price']})")
    
    # Performance olish
    print("\n=== Signal Performance ===")
    for signal_id in signal_ids[:2]:
        performance = await marketplace.get_signal_performance(signal_id)
        if performance:
            signal = marketplace.signals[signal_id]
            print(f"\n{signal.title}:")
            print(f"  Win Rate: {signal.performance.win_rate:.1%}")
            print(f"  Sharpe Ratio: {signal.performance.sharpe_ratio:.2f}")
            print(f"  Max Drawdown: {signal.performance.max_drawdown:.1%}")
            print(f"  Community Score: {signal.community_score:.1f}/100")
            print(f"  AI Score: {signal.ai_score:.1f}/100")
    
    # Marketplace statistikasi
    print("\n=== Marketplace Statistikasi ===")
    stats = await marketplace.get_marketplace_statistics()
    print(f"Jami signallar: {stats['total_signals']}")
    print(f"Aktiv signallar: {stats['active_signals']}")
    print(f"Jami foydalanuvchilar: {stats['total_users']}")
    print(f"Jami obunalar: {stats['total_subscriptions']}")
    print(f"Jami daromad: ${stats['total_revenue']:.2f}")
    print(f"O'rtacha baho: {stats['average_rating']:.2f}")
    
    print("\n=== AI Signal Marketplace Demo Tugadi ===")

if __name__ == "__main__":
    asyncio.run(demo_signal_marketplace())