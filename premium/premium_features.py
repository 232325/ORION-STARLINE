"""
Premium Xususiyatlar Moduli
===========================

Bu modul Orion Starline platformasining premium xususiyatlarini boshqaradi.
VIP foydalanuvchilarning maxsus huquqlari va imtiyozlarini ta'minlaydi.

Asosiy xususiyatlar:
- Advanced Analytics
- Exclusive Signals 
- Priority Support
- Premium Dashboard
- Personalized Trading Recommendations
- Advanced Risk Management
- Custom Trading Strategies
- Real-time Market Insights

Autor: AI Development Team
Versiya: 1.0.0
Sana: 2025-11-05
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import hashlib
import time

# Premium tier levels
class PremiumTier(Enum):
    """Premium daraja turlari"""
    VIP = "vip"           # VIP daraja
    ELITE = "elite"       # Elite daraja
    PLATINUM = "platinum" # Platinum daraja
    DIAMOND = "diamond"   # Diamond daraja

# Feature permissions
class FeaturePermission(Enum):
    """Premium xususiyat huquqlari"""
    ADVANCED_ANALYTICS = "advanced_analytics"
    EXCLUSIVE_SIGNALS = "exclusive_signals"
    PRIORITY_SUPPORT = "priority_support"
    PREMIUM_DASHBOARD = "premium_dashboard"
    CUSTOM_STRATEGIES = "custom_strategies"
    REAL_TIME_INSIGHTS = "real_time_insights"
    ADVANCED_RISK_MGMT = "advanced_risk_mgmt"
    PERSONALIZED_RECS = "personalized_recommendations"

@dataclass
class UserProfile:
    """Foydalanuvchi profili"""
    user_id: str
    username: str
    email: str
    tier: PremiumTier
    subscription_start: datetime
    subscription_end: datetime
    features_enabled: List[FeaturePermission]
    trading_volume: float
    success_rate: float
    last_active: datetime
    referral_count: int
    total_earnings: float
    
@dataclass
class PremiumFeature:
    """Premium xususiyat"""
    name: str
    permission: FeaturePermission
    tier_required: PremiumTier
    description: str
    daily_limit: Optional[int] = None
    monthly_limit: Optional[int] = None
    rate_limit: Optional[int] = None  # seconds
    
@dataclass
class UsageRecord:
    """Foydalanish yozuvi"""
    user_id: str
    feature: FeaturePermission
    timestamp: datetime
    success: bool
    response_time: float
    data_size: int

class PremiumFeatureManager:
    """
    Premium xususiyatlar boshqaruvchisi
    
    VIP foydalanuvchilar uchun maxsus xususiyatlar va imtiyozlarni boshqaradi.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.users: Dict[str, UserProfile] = {}
        self.feature_catalog: Dict[FeaturePermission, PremiumFeature] = {}
        self.usage_records: List[UsageRecord] = []
        self.active_sessions: Dict[str, Dict] = {}
        
        self._initialize_feature_catalog()
        self._initialize_sample_users()
    
    def _initialize_feature_catalog(self):
        """Premium xususiyatlar katalogini boshlash"""
        features = [
            PremiumFeature(
                name="Advanced Analytics",
                permission=FeaturePermission.ADVANCED_ANALYTICS,
                tier_required=PremiumTier.VIP,
                description="Chuqur bozor tahlili va statistika",
                monthly_limit=1000
            ),
            PremiumFeature(
                name="Exclusive Signals", 
                permission=FeaturePermission.EXCLUSIVE_SIGNALS,
                tier_required=PremiumTier.VIP,
                description="Maxsus savdo signallari",
                daily_limit=50
            ),
            PremiumFeature(
                name="Priority Support",
                permission=FeaturePermission.PRIORITY_SUPPORT, 
                tier_required=PremiumTier.VIP,
                description="Birlamchi yordam xizmati"
            ),
            PremiumFeature(
                name="Premium Dashboard",
                permission=FeaturePermission.PREMIUM_DASHBOARD,
                tier_required=PremiumTier.VIP, 
                description="Kengaytirilgan boshqarish paneli"
            ),
            PremiumFeature(
                name="Custom Strategies",
                permission=FeaturePermission.CUSTOM_STRATEGIES,
                tier_required=PremiumTier.ELITE,
                description="Shaxsiy savdo strategiyalari",
                monthly_limit=10
            ),
            PremiumFeature(
                name="Real-time Insights",
                permission=FeaturePermission.REAL_TIME_INSIGHTS,
                tier_required=PremiumTier.ELITE,
                description="Real vaqtli bozor tushunchalari"
            ),
            PremiumFeature(
                name="Advanced Risk Management",
                permission=FeaturePermission.ADVANCED_RISK_MGMT,
                tier_required=PremiumTier.PLATINUM,
                description="Ilg'or risk boshqaruvi"
            ),
            PremiumFeature(
                name="Personalized Recommendations",
                permission=FeaturePermission.PERSONALIZED_RECS,
                tier_required=PremiumTier.DIAMOND,
                description="Shaxsiylashtirilgan tavsiyalar"
            )
        ]
        
        for feature in features:
            self.feature_catalog[feature.permission] = feature
    
    def _initialize_sample_users(self):
        """Namuna foydalanuvchilarni qo'shish"""
        sample_users = [
            UserProfile(
                user_id="vip001",
                username="vip_trader",
                email="vip@example.com", 
                tier=PremiumTier.VIP,
                subscription_start=datetime.now() - timedelta(days=30),
                subscription_end=datetime.now() + timedelta(days=365),
                features_enabled=[FeaturePermission.ADVANCED_ANALYTICS, 
                                FeaturePermission.EXCLUSIVE_SIGNALS,
                                FeaturePermission.PRIORITY_SUPPORT,
                                FeaturePermission.PREMIUM_DASHBOARD],
                trading_volume=100000.0,
                success_rate=0.75,
                last_active=datetime.now() - timedelta(hours=2),
                referral_count=5,
                total_earnings=15000.0
            ),
            UserProfile(
                user_id="elite001", 
                username="elite_trader",
                email="elite@example.com",
                tier=PremiumTier.ELITE,
                subscription_start=datetime.now() - timedelta(days=60),
                subscription_end=datetime.now() + timedelta(days=305),
                features_enabled=[FeaturePermission.ADVANCED_ANALYTICS,
                                FeaturePermission.EXCLUSIVE_SIGNALS,
                                FeaturePermission.PRIORITY_SUPPORT, 
                                FeaturePermission.PREMIUM_DASHBOARD,
                                FeaturePermission.CUSTOM_STRATEGIES,
                                FeaturePermission.REAL_TIME_INSIGHTS],
                trading_volume=500000.0,
                success_rate=0.82,
                last_active=datetime.now() - timedelta(minutes=30),
                referral_count=12,
                total_earnings=75000.0
            )
        ]
        
        for user in sample_users:
            self.users[user.user_id] = user
    
    def check_feature_access(self, user_id: str, feature: FeaturePermission) -> Dict[str, Any]:
        """
        Foydalanuvchining xususiyatga kirish huquqini tekshirish
        
        Args:
            user_id: Foydalanuvchi ID
            feature: Xususiyat ruxsati
            
        Returns:
            Kirish huquqi ma'lumotlari
        """
        if user_id not in self.users:
            return {
                "access": False,
                "reason": "Foydalanuvchi topilmadi",
                "tier_required": None,
                "current_tier": None
            }
        
        user = self.users[user_id]
        feature_def = self.feature_catalog.get(feature)
        
        if not feature_def:
            return {
                "access": False,
                "reason": "Xususiyat mavjud emas",
                "tier_required": None,
                "current_tier": user.tier.value
            }
        
        # Daraja tekshirish
        tier_hierarchy = {
            PremiumTier.VIP: 1,
            PremiumTier.ELITE: 2, 
            PremiumTier.PLATINUM: 3,
            PremiumTier.DIAMOND: 4
        }
        
        current_tier_level = tier_hierarchy.get(user.tier, 0)
        required_tier_level = tier_hierarchy.get(feature_def.tier_required, 0)
        
        # Abunelik muddati tekshirish
        subscription_valid = datetime.now() < user.subscription_end
        
        if not subscription_valid:
            return {
                "access": False,
                "reason": "Abunelik muddati tugagan",
                "tier_required": feature_def.tier_required.value,
                "current_tier": user.tier.value,
                "tier_level_ok": current_tier_level >= required_tier_level
            }
        
        if current_tier_level < required_tier_level:
            return {
                "access": False,
                "reason": f"Kerakli daraja: {feature_def.tier_required.value}",
                "tier_required": feature_def.tier_required.value,
                "current_tier": user.tier.value,
                "tier_level_ok": False
            }
        
        # Limitlar tekshirish
        limits_check = self._check_usage_limits(user_id, feature)
        
        return {
            "access": True,
            "reason": "Kirish ruxsat etilgan",
            "tier_required": feature_def.tier_required.value,
            "current_tier": user.tier.value,
            "feature_name": feature_def.name,
            "limits": limits_check
        }
    
    def _check_usage_limits(self, user_id: str, feature: FeaturePermission) -> Dict[str, Any]:
        """Foydalanish limitlarini tekshirish"""
        feature_def = self.feature_catalog.get(feature)
        if not feature_def:
            return {"status": "error", "message": "Xususiyat topilmadi"}
        
        # Bugungi foydalanishni olish
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        this_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        user_usage = [u for u in self.usage_records 
                     if u.user_id == user_id and u.feature == feature]
        
        daily_usage = [u for u in user_usage if u.timestamp >= today]
        monthly_usage = [u for u in user_usage if u.timestamp >= this_month]
        
        result = {
            "daily_used": len(daily_usage),
            "daily_limit": feature_def.daily_limit,
            "monthly_used": len(monthly_usage), 
            "monthly_limit": feature_def.monthly_limit
        }
        
        # Limitlar bajarilganligini tekshirish
        if feature_def.daily_limit and len(daily_usage) >= feature_def.daily_limit:
            result["daily_limit_reached"] = True
        else:
            result["daily_limit_reached"] = False
            
        if feature_def.monthly_limit and len(monthly_usage) >= feature_def.monthly_limit:
            result["monthly_limit_reached"] = True
        else:
            result["monthly_limit_reached"] = False
        
        return result
    
    async def record_usage(self, user_id: str, feature: FeaturePermission, 
                          success: bool = True, response_time: float = 0.0,
                          data_size: int = 0) -> None:
        """Foydalanish yozuvini saqlash"""
        usage_record = UsageRecord(
            user_id=user_id,
            feature=feature,
            timestamp=datetime.now(),
            success=success,
            response_time=response_time,
            data_size=data_size
        )
        
        self.usage_records.append(usage_record)
        
        self.logger.info(f"Usage recorded: {user_id} used {feature.value}, "
                        f"success: {success}, time: {response_time}ms")
    
    def get_user_features(self, user_id: str) -> Dict[str, Any]:
        """Foydalanuvchining barcha xususiyatlarini olish"""
        if user_id not in self.users:
            return {"error": "Foydalanuvchi topilmadi"}
        
        user = self.users[user_id]
        features_status = {}
        
        for permission in FeaturePermission:
            access_info = self.check_feature_access(user_id, permission)
            features_status[permission.value] = access_info
        
        return {
            "user_id": user_id,
            "username": user.username,
            "tier": user.tier.value,
            "subscription_end": user.subscription_end.isoformat(),
            "features": features_status,
            "stats": {
                "trading_volume": user.trading_volume,
                "success_rate": user.success_rate,
                "referral_count": user.referral_count,
                "total_earnings": user.total_earnings
            }
        }
    
    def upgrade_user_tier(self, user_id: str, new_tier: PremiumTier) -> Dict[str, Any]:
        """Foydalanuvchi darajasini oshirish"""
        if user_id not in self.users:
            return {"success": False, "message": "Foydalanuvchi topilmadi"}
        
        user = self.users[user_id]
        old_tier = user.tier
        
        # Daraja piramidasi
        tier_progression = {
            PremiumTier.VIP: [PremiumTier.ELITE],
            PremiumTier.ELITE: [PremiumTier.PLATINUM],
            PremiumTier.PLATINUM: [PremiumTier.DIAMOND],
            PremiumTier.DIAMOND: []
        }
        
        if new_tier not in tier_progression.get(old_tier, []):
            return {
                "success": False, 
                "message": f"{old_tier.value} dan {new_tier.value} ga o'tish mumkin emas"
            }
        
        # Yangi xususiyatlarni qo'shish
        for permission, feature_def in self.feature_catalog.items():
            if (feature_def.tier_required == new_tier and 
                permission not in user.features_enabled):
                user.features_enabled.append(permission)
        
        user.tier = new_tier
        user.subscription_end = datetime.now() + timedelta(days=365)
        
        self.logger.info(f"User {user_id} upgraded from {old_tier.value} to {new_tier.value}")
        
        return {
            "success": True,
            "message": f"{old_tier.value} dan {new_tier.value} ga muvaffaqiyatli o'tkazildi",
            "new_features": [f for f in self.feature_catalog.values() 
                           if f.tier_required == new_tier]
        }
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Premium xususiyatlar analitikasi"""
        total_users = len(self.users)
        tier_distribution = {}
        
        for user in self.users.values():
            tier = user.tier.value
            tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
        
        # So'nggi 30 kundagi faoliyat
        last_30_days = datetime.now() - timedelta(days=30)
        recent_usage = [u for u in self.usage_records if u.timestamp >= last_30_days]
        
        feature_usage = {}
        for permission in FeaturePermission:
            count = len([u for u in recent_usage if u.feature == permission])
            feature_usage[permission.value] = count
        
        return {
            "total_users": total_users,
            "tier_distribution": tier_distribution,
            "total_usage_last_30_days": len(recent_usage),
            "feature_usage": feature_usage,
            "success_rate": len([u for u in recent_usage if u.success]) / len(recent_usage) if recent_usage else 0,
            "average_response_time": sum(u.response_time for u in recent_usage) / len(recent_usage) if recent_usage else 0
        }

# Global instance
premium_manager = PremiumFeatureManager()

# Utility functions
def check_user_feature_access(user_id: str, feature: str) -> bool:
    """Foydalanuvchining xususiyatga kirish huquqini tekshirish (utility function)"""
    try:
        permission = FeaturePermission(feature)
        result = premium_manager.check_feature_access(user_id, permission)
        return result.get("access", False)
    except ValueError:
        return False

def get_user_premium_features(user_id: str) -> List[str]:
    """Foydalanuvchining premium xususiyatlar ro'yxati"""
    try:
        status = premium_manager.get_user_features(user_id)
        if "error" in status:
            return []
        
        features = []
        for feature_key, feature_info in status.get("features", {}).items():
            if feature_info.get("access", False):
                features.append(feature_key)
        
        return features
    except Exception:
        return []

# Export main classes and functions
__all__ = [
    'PremiumTier',
    'FeaturePermission', 
    'UserProfile',
    'PremiumFeature',
    'UsageRecord',
    'PremiumFeatureManager',
    'premium_manager',
    'check_user_feature_access',
    'get_user_premium_features'
]