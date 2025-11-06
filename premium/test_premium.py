"""
Premium Xususiyatlar Test Skripti
=================================

Bu skript premium modulning barcha xususiyatlarini test qiladi.
VIP foydalanuvchilar uchun premium xizmatlarni tekshirish.

Test qilinadigan funksionallik:
- Premium feature access
- VIP system
- Premium analytics
- Exclusive signals
- Integration tests

Autor: AI Development Team
Versiya: 1.0.0
Sana: 2025-11-05
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import premium modules
from premium import (
    premium_manager,
    vip_system,
    premium_analytics,
    exclusive_signals,
    get_premium_summary,
    upgrade_to_premium,
    get_complete_analytics,
    get_premium_dashboard_data,
    health_check
)

class PremiumTestSuite:
    """Premium test paketi"""
    
    def __init__(self):
        self.test_results = []
        self.user_id = "test_vip_user"
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Test natijasini loglash"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now()
        })
    
    async def test_premium_features(self):
        """Premium xususiyatlar testi"""
        print("\n🔧 Premium Features Testi")
        print("-" * 40)
        
        try:
            # User feature access test
            access_result = premium_manager.check_feature_access(
                "vip001", 
                "advanced_analytics"
            )
            success = "access" in access_result
            self.log_test("Feature Access Check", success, 
                         f"Access: {access_result.get('access', False)}")
            
            # User features list test
            features = premium_manager.get_user_features("vip001")
            success = "features" in features
            self.log_test("User Features List", success, 
                         f"Features count: {len(features.get('features', {}))}")
            
            # Usage analytics test
            analytics = premium_manager.get_analytics_summary()
            success = "total_users" in analytics
            self.log_test("Premium Analytics", success, 
                         f"Total users: {analytics.get('total_users', 0)}")
            
        except Exception as e:
            self.log_test("Premium Features", False, f"Error: {str(e)}")
    
    async def test_vip_system(self):
        """VIP tizim testi"""
        print("\n👑 VIP System Testi")
        print("-" * 40)
        
        try:
            # Eligibility check test
            user_data = {
                "user_id": "test_user",
                "trading_volume": 15000.0,
                "total_earnings": 1500.0,
                "referral_count": 2
            }
            
            eligibility = vip_system.check_eligibility(user_data)
            success = "eligible" in eligibility
            self.log_test("VIP Eligibility Check", success, 
                         f"Eligible: {eligibility.get('eligible', False)}")
            
            # VIP upgrade test (simulation)
            upgrade_result = await vip_system.upgrade_to_vip(user_data, "VIP Bronze")
            success = upgrade_result.get("success", False)
            self.log_test("VIP Upgrade Simulation", success, 
                         f"Upgrade success: {upgrade_result.get('success', False)}")
            
            # Member profile test
            profile = vip_system.get_member_profile("vip001")
            success = "tier" in profile
            self.log_test("VIP Profile Access", success, 
                         f"Profile tier: {profile.get('tier', 'N/A')}")
            
            # VIP statistics test
            stats = vip_system.get_vip_statistics()
            success = "total_members" in stats
            self.log_test("VIP Statistics", success, 
                         f"Total members: {stats.get('total_members', 0)}")
            
        except Exception as e:
            self.log_test("VIP System", False, f"Error: {str(e)}")
    
    async def test_premium_analytics(self):
        """Premium analitika testi"""
        print("\n📊 Premium Analytics Testi")
        print("-" * 40)
        
        try:
            # Market analysis test
            from premium_analytics import AnalyticsRequest, AnalyticsType
            
            market_request = AnalyticsRequest(
                user_id="vip001",
                analysis_type=AnalyticsType.MARKET_ANALYSIS,
                symbol="EURUSD",
                timeframe="1h",
                start_date=datetime.now() - timedelta(days=30),
                end_date=datetime.now(),
                parameters={},
                include_indicators=["RSI", "MACD"],
                include_predictions=True
            )
            
            market_result = await premium_analytics.generate_analysis(market_request)
            success = market_result.data_points > 0
            self.log_test("Market Analysis Generation", success, 
                         f"Data points: {market_result.data_points}")
            
            # Portfolio analysis test
            portfolio_request = AnalyticsRequest(
                user_id="vip001",
                analysis_type=AnalyticsType.PORTFOLIO_ANALYSIS,
                symbol="PORTFOLIO",
                timeframe="1d",
                start_date=datetime.now() - timedelta(days=30),
                end_date=datetime.now(),
                parameters={},
                include_indicators=[],
                include_predictions=False
            )
            
            portfolio_result = await premium_analytics.generate_analysis(portfolio_request)
            success = portfolio_result.data_points > 0
            self.log_test("Portfolio Analysis Generation", success, 
                         f"Portfolio value: {portfolio_result.summary.get('total_value', 'N/A')}")
            
            # Cache test
            cache_stats = premium_analytics.get_cache_stats()
            success = "cached_analyses" in cache_stats
            self.log_test("Analytics Cache Stats", success, 
                         f"Cached: {cache_stats.get('cached_analyses', 0)}")
            
        except Exception as e:
            self.log_test("Premium Analytics", False, f"Error: {str(e)}")
    
    async def test_exclusive_signals(self):
        """Eksklyuziv signallar testi"""
        print("\n🚨 Exclusive Signals Testi")
        print("-" * 40)
        
        try:
            # Generate signal test
            signal_result = exclusive_signals.generate_signal("vip001", "EURUSD")
            success = signal_result.get("success", False)
            self.log_test("Signal Generation", success, 
                         f"Signal ID: {signal_result.get('signal', {}).get('signal_id', 'N/A')}")
            
            # User signals test
            user_signals = exclusive_signals.get_user_signals("vip001")
            success = "signals" in user_signals
            self.log_test("User Signals Retrieval", success, 
                         f"Active signals: {user_signals.get('active_count', 0)}")
            
            # Signal analytics test
            signal_analytics = exclusive_signals.get_signal_analytics("vip001")
            success = "total_signals" in signal_analytics
            self.log_test("Signal Analytics", success, 
                         f"Total signals: {signal_analytics.get('total_signals', 0)}")
            
            # System statistics test
            sys_stats = exclusive_signals.get_system_statistics()
            success = "total_signals_generated" in sys_stats
            self.log_test("Signal System Stats", success, 
                         f"Generated: {sys_stats.get('total_signals_generated', 0)}")
            
        except Exception as e:
            self.log_test("Exclusive Signals", False, f"Error: {str(e)}")
    
    async def test_integration_features(self):
        """Integratsiya xususiyatlari testi"""
        print("\n🔗 Integration Testi")
        print("-" * 40)
        
        try:
            # Premium summary test
            summary = get_premium_summary("vip001")
            success = "premium_features" in summary
            self.log_test("Premium Summary", success, 
                         f"Features count: {summary.get('premium_features_count', 0)}")
            
            # Dashboard data test
            dashboard = get_premium_dashboard_data("vip001")
            success = "vip_profile" in dashboard
            self.log_test("Premium Dashboard", success, 
                         f"VIP status: {dashboard.get('vip_profile', {}).get('status', 'N/A')}")
            
            # Complete analytics test
            analytics = get_complete_analytics("vip001", "EURUSD")
            success = analytics.get("success", False)
            self.log_test("Complete Analytics", success, 
                         f"Analysis generated: {analytics.get('success', False)}")
            
        except Exception as e:
            self.log_test("Integration Features", False, f"Error: {str(e)}")
    
    async def test_health_check(self):
        """Sog'lik tekshiruv testi"""
        print("\n🏥 Health Check Testi")
        print("-" * 40)
        
        try:
            health = health_check()
            success = "status" in health
            self.log_test("Health Check", success, 
                         f"Status: {health.get('status', 'unknown')}")
            
            # Service status test
            services = health.get("services", {})
            all_healthy = all(status == "healthy" for status in services.values())
            self.log_test("All Services Healthy", all_healthy, 
                         f"Services: {list(services.keys())}")
            
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
    
    async def test_signal_performance_tracking(self):
        """Signal performance kuzatuvi testi"""
        print("\n📈 Signal Performance Testi")
        print("-" * 40)
        
        try:
            # Auto-close expired signals
            exclusive_signals.update_signal_performance_tracking()
            
            # Check for expiring signals
            expiring = exclusive_signals.get_upcoming_expiring_signals(hours_ahead=1)
            self.log_test("Expiring Signals Check", True, 
                         f"Expiring signals: {len(expiring)}")
            
            # Signal filtering test
            filter_criteria = {
                "symbols": ["EURUSD", "GBPUSD"],
                "signal_types": ["buy"],
                "min_confidence": 0.7
            }
            
            filtered = exclusive_signals.apply_signal_filter("vip001", filter_criteria)
            success = "signals" in filtered
            self.log_test("Signal Filtering", success, 
                         f"Filtered count: {filtered.get('filtered_count', 0)}")
            
        except Exception as e:
            self.log_test("Signal Performance", False, f"Error: {str(e)}")
    
    def print_summary(self):
        """Test natijalari xulosasi"""
        print("\n" + "=" * 50)
        print("📋 TEST NATIJALARI XULOSASI")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Jami testlar: {total}")
        print(f"O'tgan: {passed} ✅")
        print(f"Xato: {total - passed} ❌")
        print(f"Muvaffaqiyat foizi: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 Barcha testlar muvaffaqiyatli o'tdi!")
            print("Premium xususiyatlar to'g'ri ishlayapti.")
        else:
            print("\n⚠️ Ba'zi testlar xato berdi!")
            print("Xatolarni tekshirib ko'ring.")
        
        # Failed tests detail
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("\n❌ Xato testlar:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        return passed == total

async def main():
    """Asosiy test funksiyasi"""
    print("🚀 Premium Xususiyatlar Test Paketi")
    print("=" * 50)
    print("Versiya: 1.0.0")
    print("Sana: 2025-11-05")
    print("=" * 50)
    
    test_suite = PremiumTestSuite()
    
    # Barcha testlarni bajarish
    await test_suite.test_premium_features()
    await test_suite.test_vip_system()
    await test_suite.test_premium_analytics()
    await test_suite.test_exclusive_signals()
    await test_suite.test_integration_features()
    await test_suite.test_health_check()
    await test_suite.test_signal_performance_tracking()
    
    # Natijalarni ko'rsatish
    all_passed = test_suite.print_summary()
    
    return all_passed

if __name__ == "__main__":
    # Asinxron testni bajarish
    success = asyncio.run(main())
    sys.exit(0 if success else 1)