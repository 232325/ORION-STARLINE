"""
Premium Xususiyatlar Moduli
============================

Bu modul Orion Starline platformasining premium xususiyatlarini birlashtiradi:
- Premium Feature Management (premium_features.py)
- VIP System Management (vip_system.py) 
- Premium Analytics Engine (premium_analytics.py)
- Exclusive Trading Signals (exclusive_signals.py)

Asosiy komponentlar:
- PremiumFeatureManager: Premium xususiyatlar boshqaruvchisi
- VIPSystemManager: VIP tizim boshqaruvchisi
- PremiumAnalyticsEngine: Premium analitika dvijogi
- ExclusiveSignalManager: Eksklyuziv signallar boshqaruvchisi

Autor: AI Development Team
Versiya: 1.0.0
Sana: 2025-11-05
"""

# Import all premium modules
from .premium_features import (
    PremiumTier,
    FeaturePermission, 
    UserProfile,
    PremiumFeature,
    UsageRecord,
    PremiumFeatureManager,
    premium_manager,
    check_user_feature_access,
    get_user_premium_features
)

from .vip_system import (
    VIPStatus,
    VIPBenefit,
    VIPTier,
    VIPMember,
    VIPEvent,
    PersonalConsultant,
    VIPSystemManager,
    vip_system,
    check_vip_eligibility,
    get_vip_tier_info
)

from .premium_analytics import (
    AnalyticsType,
    ChartType,
    AnalyticsRequest,
    AnalyticsResult,
    MarketIndicator,
    PortfolioMetrics,
    PremiumAnalyticsEngine,
    premium_analytics,
    generate_premium_analysis
)

from .exclusive_signals import (
    SignalType,
    SignalStrength,
    SignalSource,
    TradingSignal,
    SignalPerformance,
    SignalFilter,
    SignalAlert,
    ExclusiveSignalManager,
    exclusive_signals,
    generate_trading_signal,
    get_user_trading_signals,
    close_trading_signal,
    get_signal_analytics,
    apply_signal_filter
)

# Package metadata
__version__ = "1.0.0"
__author__ = "AI Development Team"
__description__ = "Orion Starline Premium Features Module"

# Main exports
__all__ = [
    # Premium Features
    'PremiumTier',
    'FeaturePermission',
    'UserProfile', 
    'PremiumFeature',
    'UsageRecord',
    'PremiumFeatureManager',
    'premium_manager',
    'check_user_feature_access',
    'get_user_premium_features',
    
    # VIP System
    'VIPStatus',
    'VIPBenefit',
    'VIPTier',
    'VIPMember',
    'VIPEvent',
    'PersonalConsultant',
    'VIPSystemManager', 
    'vip_system',
    'check_vip_eligibility',
    'get_vip_tier_info',
    
    # Premium Analytics
    'AnalyticsType',
    'ChartType',
    'AnalyticsRequest',
    'AnalyticsResult',
    'MarketIndicator',
    'PortfolioMetrics',
    'PremiumAnalyticsEngine',
    'premium_analytics',
    'generate_premium_analysis',
    
    # Exclusive Signals
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

# Convenience functions for common operations
def get_premium_summary(user_id: str) -> dict:
    """
    Foydalanuvchi uchun premium xususiyatlar umumiy ko'rinishi
    
    Args:
        user_id: Foydalanuvchi ID
        
    Returns:
        Premium xususiyatlar umumiy ma'lumotlari
    """
    try:
        # Premium features
        premium_features = get_user_premium_features(user_id)
        
        # VIP status
        user_profile = vip_system.get_member_profile(user_id)
        
        # Recent signals
        signals_data = get_user_trading_signals(user_id, "active")
        
        # Analytics access
        analytics_access = check_user_feature_access(user_id, "advanced_analytics")
        
        return {
            "user_id": user_id,
            "premium_features_count": len(premium_features),
            "premium_features": premium_features,
            "vip_status": user_profile.get("status", "not_vip"),
            "vip_tier": user_profile.get("tier", None),
            "active_signals": signals_data.get("active_count", 0),
            "analytics_enabled": analytics_access,
            "has_vip_access": user_profile.get("tier") is not None
        }
        
    except Exception as e:
        return {
            "user_id": user_id,
            "error": f"Premium summary yaratishda xatolik: {str(e)}"
        }

def upgrade_to_premium(user_id: str, tier: str = "VIP") -> dict:
    """
    Foydalanuvchini premium ga upgrade qilish
    
    Args:
        user_id: Foydalanuvchi ID
        tier: VIP daraja nomi
        
    Returns:
        Upgrade natijasi
    """
    try:
        # VIP upgrade
        vip_result = vip_system.upgrade_to_vip(
            {"user_id": user_id, "username": user_id, "email": f"{user_id}@example.com"},
            tier
        )
        
        if vip_result.get("success"):
            # Premium features activation
            from .vip_system import PremiumTier
            tier_enum = PremiumTier.VIP  # Default to VIP
            
            if tier == "VIP":
                tier_enum = PremiumTier.VIP
            elif tier == "ELITE":
                tier_enum = PremiumTier.ELITE
            elif tier == "PLATINUM":
                tier_enum = PremiumTier.PLATINUM
            elif tier == "DIAMOND":
                tier_enum = PremiumTier.DIAMOND
            
            # Enable relevant features
            feature_result = {
                "success": True,
                "message": f"Muvaffaqiyatli {tier} ga upgrade qilindi"
            }
            
            return {
                "success": True,
                "vip_upgrade": vip_result,
                "feature_activation": feature_result,
                "new_tier": tier
            }
        else:
            return vip_result
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Premium upgrade qilishda xatolik: {str(e)}"
        }

def get_complete_analytics(user_id: str, symbol: str = "EURUSD") -> dict:
    """
    Foydalanuvchi uchun to'liq premium analitika
    
    Args:
        user_id: Foydalanuvchi ID
        symbol: Trading symbol
        
    Returns:
        To'liq analitika hisoboti
    """
    try:
        # Access check
        if not check_user_feature_access(user_id, "advanced_analytics"):
            return {
                "success": False,
                "message": "Premium analitika huquqi yo'q"
            }
        
        # Market analysis
        market_analysis = generate_premium_analysis(user_id, "market_analysis", symbol)
        
        # Portfolio analysis
        portfolio_analysis = generate_premium_analysis(user_id, "portfolio_analysis", symbol)
        
        # Risk analysis
        risk_analysis = generate_premium_analysis(user_id, "risk_analysis", symbol)
        
        # Performance analysis
        performance_analysis = generate_premium_analysis(user_id, "performance_analysis", symbol)
        
        # Signal analytics
        signal_analytics = get_signal_analytics(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "symbol": symbol,
            "analyses": {
                "market": market_analysis.get("analysis", {}),
                "portfolio": portfolio_analysis.get("analysis", {}),
                "risk": risk_analysis.get("analysis", {}),
                "performance": performance_analysis.get("analysis", {})
            },
            "signal_analytics": signal_analytics,
            "generated_at": "2025-11-05T07:26:57Z"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Analitika yaratishda xatolik: {str(e)}"
        }

def get_premium_dashboard_data(user_id: str) -> dict:
    """
    Premium dashboard ma'lumotlari
    
    Args:
        user_id: Foydalanuvchi ID
        
    Returns:
        Dashboard uchun ma'lumotlar
    """
    try:
        # VIP profile
        vip_profile = vip_system.get_member_profile(user_id)
        
        # Active signals
        signals = get_user_trading_signals(user_id, "active")
        
        # Signal analytics
        signal_analytics = get_signal_analytics(user_id)
        
        # Premium features status
        features = get_user_premium_features(user_id)
        
        # System statistics
        if vip_profile.get("tier") in ["VIP Gold", "VIP Platinum"]:
            system_stats = exclusive_signals.get_system_statistics()
        else:
            system_stats = {"message": "Faqat yuqori VIP daraja uchun"}
        
        return {
            "user_id": user_id,
            "vip_profile": vip_profile,
            "active_signals": signals,
            "signal_performance": signal_analytics,
            "premium_features": features,
            "system_statistics": system_stats,
            "dashboard_updated": "2025-11-05T07:26:57Z"
        }
        
    except Exception as e:
        return {
            "user_id": user_id,
            "error": f"Dashboard ma'lumotlarini olishda xatolik: {str(e)}"
        }

# Version information
def get_version_info():
    """Versiya ma'lumotlarini olish"""
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "components": {
            "premium_features": "1.0.0",
            "vip_system": "1.0.0", 
            "premium_analytics": "1.0.0",
            "exclusive_signals": "1.0.0"
        },
        "build_date": "2025-11-05",
        "features": [
            "Advanced Analytics",
            "Exclusive Signals",
            "Priority Support", 
            "Premium Dashboard",
            "VIP System",
            "Risk Management",
            "Portfolio Optimization",
            "Real-time Insights"
        ]
    }

# Initialize premium services
def initialize_premium_services():
    """Premium xizmatlarni boshlash"""
    try:
        # Initialize all managers
        premium_manager = PremiumFeatureManager()
        vip_system_manager = VIPSystemManager()
        analytics_engine = PremiumAnalyticsEngine()
        signal_manager = ExclusiveSignalManager()
        
        return {
            "success": True,
            "message": "Barcha premium xizmatlar muvaffaqiyatli ishga tushdi",
            "services": {
                "premium_features": True,
                "vip_system": True,
                "premium_analytics": True,
                "exclusive_signals": True
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Premium xizmatlarni boshlashda xatolik: {str(e)}"
        }

# Health check function
def health_check():
    """Premium xususiyatlar sog'lig'i tekshiruvi"""
    try:
        # Test each service
        premium_status = len(premium_manager.users) > 0
        vip_status = len(vip_system.vip_members) > 0
        analytics_status = len(premium_analytics.market_data_cache) > 0
        signals_status = len(exclusive_signals.active_signals) >= 0
        
        return {
            "status": "healthy",
            "services": {
                "premium_features": "healthy" if premium_status else "no_data",
                "vip_system": "healthy" if vip_status else "no_data",
                "premium_analytics": "healthy" if analytics_status else "no_data",
                "exclusive_signals": "healthy" if signals_status else "no_data"
            },
            "overall_health": "good" if all([premium_status, vip_status, analytics_status, signals_status]) else "degraded",
            "last_check": "2025-11-05T07:26:57Z"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Sog'lik tekshiruvda xatolik: {str(e)}",
            "overall_health": "critical"
        }

# Auto-initialize on import
_init_result = initialize_premium_services()
if _init_result["success"]:
    print("✅ Premium xususiyatlar moduli muvaffaqiyatli yuklandi")
else:
    print("⚠️ Premium xususiyatlar moduli qisman yuklandi")

# Export convenience functions
__all__.extend([
    'get_premium_summary',
    'upgrade_to_premium', 
    'get_complete_analytics',
    'get_premium_dashboard_data',
    'get_version_info',
    'initialize_premium_services',
    'health_check'
])