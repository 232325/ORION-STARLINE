"""
Smart Alert System - Demo va Test Fayli

Ushbu fayl Smart Alert System moduling funksionalligini
sinab ko'rish va demo qilish uchun mo'ljallangan.

Foydalanish:
python smart_alerts_demo.py
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from smart_alerts import (
    SmartAlertSystem, AlertType, NotificationChannel, 
    AlertStatus, AlertRule
)

# Logging sozlamasi
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class SmartAlertsDemo:
    """Smart Alert System Demo Klasi"""
    
    def __init__(self):
        self.alerts = SmartAlertSystem()
        self.logger = logging.getLogger(__name__)
    
    async def run_comprehensive_demo(self):
        """Keng qamrovli demo ishga tushirish"""
        print("=" * 80)
        print("🎯 SMART ALERT SYSTEM - Comprehensive Demo")
        print("=" * 80)
        
        # 1. Konfiguratsiyani ko'rsatish
        self.demo_configuration()
        
        # 2. Price Alerts
        await self.demo_price_alerts()
        
        # 3. Technical Indicator Alerts
        await self.demo_technical_alerts()
        
        # 4. Volume Alerts
        await self.demo_volume_alerts()
        
        # 5. News Alerts
        await self.demo_news_alerts()
        
        # 6. Portfolio Alerts
        await self.demo_portfolio_alerts()
        
        # 7. Risk Alerts
        await self.demo_risk_alerts()
        
        # 8. Calendar Alerts
        await self.demo_calendar_alerts()
        
        # 9. Watchlists
        await self.demo_watchlists()
        
        # 10. Real-time Monitoring
        await self.demo_monitoring()
        
        # 11. Statistics va Analytics
        await self.demo_statistics()
        
        # 12. Alert Management
        await self.demo_alert_management()
        
        print("\n" + "=" * 80)
        print("✅ Demo tugadi!")
        print("=" * 80)
    
    def demo_configuration(self):
        """Demo: Konfiguratsiya"""
        print("\n📋 1. KONFIGURATSIYA")
        print("-" * 50)
        
        config = self.alerts.get_config()
        print(f"Twilio configured: {'twilio' in self.alerts.notification_providers}")
        print(f"SendGrid configured: {'sendgrid' in self.alerts.notification_providers}")
        print(f"Telegram configured: {'telegram' in self.alerts.notification_providers}")
        print(f"Firebase configured: {'firebase' in self.alerts.notification_providers}")
        print(f"News API configured: {bool(config.get('news', {}).get('news_api_key'))}")
        
        # Test configuration update
        test_config = {
            "monitoring": {
                "interval": 30,
                "max_alerts_per_hour": 50
            }
        }
        self.alerts.update_config(test_config)
        print("✅ Konfiguratsiya yangilandi")
    
    async def demo_price_alerts(self):
        """Demo: Narx Ogohlantirishlari"""
        print("\n💰 2. NARX OGOHLANTIRISHLARI")
        print("-" * 50)
        
        # BTC yuqori narx
        btc_high = self.alerts.add_price_alert(
            symbol="BTC",
            condition="above",
            threshold=45000,
            channel="telegram",
            name="BTC High Price Alert"
        )
        print(f"✅ BTC > $45,000 alert yaratildi: {btc_high}")
        
        # AAPL past narx
        aapl_low = self.alerts.add_price_alert(
            symbol="AAPL",
            condition="below",
            threshold=140,
            channel="email",
            name="AAPL Low Price Alert"
        )
        print(f"✅ AAPL < $140 alert yaratildi: {aapl_low}")
        
        # ETH aniq narx
        eth_exact = self.alerts.add_price_alert(
            symbol="ETH",
            condition="equal",
            threshold=3000,
            channel="push",
            name="ETH Exact Price Alert"
        )
        print(f"✅ ETH = $3,000 alert yaratildi: {eth_exact}")
        
        # Manual trigger test
        await self.trigger_test_alert("BTC", AlertType.PRICE, "BTC narx $45,000 dan yuqori!")
    
    async def demo_technical_alerts(self):
        """Demo: Texnik Indikator Ogohlantirishlari"""
        print("\n📈 3. TEXNIK INDikator OGOHLANTIRISHLARI")
        print("-" * 50)
        
        # RSI alerts
        btc_rsi_overbought = self.alerts.add_technical_alert(
            symbol="BTC",
            indicator="RSI",
            condition="rsi_overbought",
            threshold=70,
            channel="telegram",
            name="BTC RSI Overbought"
        )
        print(f"✅ BTC RSI > 70 alert yaratildi: {btc_rsi_overbought}")
        
        btc_rsi_oversold = self.alerts.add_technical_alert(
            symbol="BTC",
            indicator="RSI",
            condition="rsi_oversold",
            threshold=30,
            channel="email",
            name="BTC RSI Oversold"
        )
        print(f"✅ BTC RSI < 30 alert yaratildi: {btc_rsi_oversold}")
        
        # Moving Average alerts
        eth_ma20 = self.alerts.add_technical_alert(
            symbol="ETH",
            indicator="MA20",
            condition="price_above_ma",
            threshold=0,
            channel="push",
            name="ETH Above MA20"
        )
        print(f"✅ ETH > MA20 alert yaratildi: {eth_ma20}")
        
        # Manual trigger test
        await self.trigger_test_alert("BTC", AlertType.TECHNICAL, "BTC RSI overbought: 75.2")
    
    async def demo_volume_alerts(self):
        """Demo: Volume Ogohlantirishlari"""
        print("\n📊 4. VOLUME OGOHLANTIRISHLARI")
        print("-" * 50)
        
        # TSLA unusual volume
        tsla_volume = self.alerts.add_volume_alert(
            symbol="TSLA",
            volume_multiplier=2.5,
            channel="push",
            name="TSLA Unusual Volume"
        )
        print(f"✅ TSLA 2.5x volume alert yaratildi: {tsla_volume}")
        
        # NVDA high volume
        nvda_volume = self.alerts.add_volume_alert(
            symbol="NVDA",
            volume_multiplier=3.0,
            channel="telegram",
            name="NVDA High Volume"
        )
        print(f"✅ NVDA 3.0x volume alert yaratildi: {nvda_volume}")
        
        # Manual trigger test
        await self.trigger_test_alert("TSLA", AlertType.VOLUME, "TSLA volume g'ayrioddiy yuqori: 5.2M")
    
    async def demo_news_alerts(self):
        """Demo: Yangiliklar Ogohlantirishlari"""
        print("\n📰 5. YANGILIKLAR OGOHLANTIRISHLARI")
        print("-" * 50)
        
        # Bitcoin news
        btc_news = self.alerts.add_news_alert(
            keywords=["bitcoin", "btc", "crypto"],
            sentiment="positive",
            channel="telegram",
            name="Bitcoin Positive News"
        )
        print(f"✅ Bitcoin news alert yaratildi: {btc_news}")
        
        # Fed news
        fed_news = self.alerts.add_news_alert(
            keywords=["fed", "federal reserve", "interest rate"],
            sentiment="any",
            channel="email",
            name="Fed News"
        )
        print(f"✅ Fed news alert yaratildi: {fed_news}")
        
        # Manual trigger test
        await self.trigger_test_alert("GLOBAL", AlertType.NEWS, "Bitcoin reaches new all-time high above $50,000")
    
    async def demo_portfolio_alerts(self):
        """Demo: Portfolio Ogohlantirishlari"""
        print("\n💼 6. PORTFOLIO OGOHLANTIRISHLARI")
        print("-" * 50)
        
        # Main portfolio
        main_portfolio = self.alerts.add_portfolio_alert(
            portfolio_name="Main Portfolio",
            change_threshold=5.0,
            channel="email",
            name="Main Portfolio 5% Change"
        )
        print(f"✅ Main portfolio 5% alert yaratildi: {main_portfolio}")
        
        # Crypto portfolio
        crypto_portfolio = self.alerts.add_portfolio_alert(
            portfolio_name="Crypto Portfolio",
            change_threshold=10.0,
            channel="telegram",
            name="Crypto Portfolio 10% Change"
        )
        print(f"✅ Crypto portfolio 10% alert yaratildi: {crypto_portfolio}")
        
        # Manual trigger test
        await self.trigger_test_alert("Main Portfolio", AlertType.PORTFOLIO, "Portfolio qiymati 5.2% ga oshdi")
    
    async def demo_risk_alerts(self):
        """Demo: Risk Ogohlantirishlari"""
        print("\n⚠️  7. RISK OGOHLANTIRISHLARI")
        print("-" * 50)
        
        # BTC risk
        btc_risk = self.alerts.add_risk_alert(
            symbol="BTC",
            risk_threshold=0.8,
            channel="push",
            name="BTC High Risk"
        )
        print(f"✅ BTC risk alert yaratildi: {btc_risk}")
        
        # ETH risk
        eth_risk = self.alerts.add_risk_alert(
            symbol="ETH",
            risk_threshold=0.7,
            channel="email",
            name="ETH Risk Alert"
        )
        print(f"✅ ETH risk alert yaratildi: {eth_risk}")
        
        # Manual trigger test
        await self.trigger_test_alert("BTC", AlertType.RISK, "BTC risk level yuqori: 0.85")
    
    async def demo_calendar_alerts(self):
        """Demo: Taqvim Ogohlantirishlari"""
        print("\n📅 8. TAQVIM OGOHLANTIRISHLARI")
        print("-" * 50)
        
        # Fed meeting
        fed_meeting = self.alerts.add_calendar_alert(
            event_name="Fed Meeting",
            importance="high",
            channel="telegram",
            name="Federal Reserve Meeting"
        )
        print(f"✅ Fed meeting alert yaratildi: {fed_meeting}")
        
        # Earnings report
        earnings = self.alerts.add_calendar_alert(
            event_name="AAPL Earnings",
            importance="medium",
            channel="email",
            name="Apple Earnings Report"
        )
        print(f"✅ Apple earnings alert yaratildi: {earnings}")
        
        # Manual trigger test
        await self.trigger_test_alert("CALENDAR", AlertType.CALENDAR, "Fed meeting 2 soatdan keyin boshlanadi")
    
    async def demo_watchlists(self):
        """Demo: Watchlists"""
        print("\n📝 9. WATCHLISTS")
        print("-" * 50)
        
        # Tech stocks watchlist
        tech_watchlist = self.alerts.create_watchlist(
            name="Tech Stocks",
            symbols=["AAPL", "GOOGL", "MSFT", "NVDA", "TSLA"]
        )
        print(f"✅ Tech Stocks watchlist yaratildi: {tech_watchlist}")
        
        # Crypto watchlist
        crypto_watchlist = self.alerts.create_watchlist(
            name="Crypto Portfolio",
            symbols=["BTC", "ETH", "ADA", "DOT", "LINK"]
        )
        print(f"✅ Crypto watchlist yaratildi: {crypto_watchlist}")
        
        # Forex watchlist
        forex_watchlist = self.alerts.create_watchlist(
            name="Major Forex",
            symbols=["EURUSD", "GBPUSD", "USDJPY", "USDCHF"]
        )
        print(f"✅ Forex watchlist yaratildi: {forex_watchlist}")
        
        # Add symbols to watchlist
        self.alerts.add_to_watchlist(tech_watchlist, "AMZN")
        self.alerts.add_to_watchlist(crypto_watchlist, "SOL")
        print("✅ Symbol qo'shildi watchlistlarga")
        
        # Get all watchlists
        watchlists = self.alerts.get_watchlists()
        print(f"✅ Jami {len(watchlists)} watchlist yaratildi")
    
    async def demo_monitoring(self):
        """Demo: Real-time Monitoring"""
        print("\n🔍 10. REAL-TIME MONITORING")
        print("-" * 50)
        
        print("📊 Monitoring statistikasi:")
        active_rules = self.alerts.get_active_rules()
        print(f"   Faol qoidalar soni: {len(active_rules)}")
        print(f"   Monitoring holati: {self.alerts.monitoring_active}")
        
        # Start monitoring
        print("🚀 Monitoring boshlanyapti...")
        self.alerts.start_monitoring()
        
        # Wait and show monitoring in action
        print("⏰ 15 soniya monitoring ishlaydi...")
        for i in range(15):
            print(f"   Monitoring active... {i+1}/15", end='\r')
            await asyncio.sleep(1)
        
        print("\n🛑 Monitoring to'xtatilmoqda...")
        self.alerts.stop_monitoring()
        print("✅ Monitoring to'xtatildi")
    
    async def demo_statistics(self):
        """Demo: Statistics va Analytics"""
        print("\n📈 11. STATISTICS VA ANALYTICS")
        print("-" * 50)
        
        # Alert statistics
        stats = self.alerts.get_alert_statistics()
        print("📊 Alert Statistics:")
        print(f"   Total alerts: {stats.get('total_alerts', 0)}")
        print(f"   Today alerts: {stats.get('today_alerts', 0)}")
        print(f"   Active rules: {stats.get('active_rules', 0)}")
        print(f"   Triggered rules: {stats.get('triggered_rules', 0)}")
        
        print("\n📈 Alert Type Distribution:")
        type_dist = stats.get('type_distribution', {})
        for alert_type, count in type_dist.items():
            print(f"   {alert_type}: {count}")
        
        print("\n📱 Channel Distribution:")
        channel_dist = stats.get('channel_distribution', {})
        for channel, count in channel_dist.items():
            print(f"   {channel}: {count}")
        
        # Performance metrics
        performance = self.alerts.get_performance_metrics()
        print("\n⚡ Performance Metrics:")
        print(f"   Alert frequency per rule: {performance.get('alert_frequency_per_rule', 0):.2f}")
        print(f"   System uptime: {performance.get('system_uptime', 0):.0f}")
        print(f"   Monitoring active: {performance.get('monitoring_active', False)}")
        print(f"   Total rules: {performance.get('total_rules', 0)}")
        print(f"   Total providers: {performance.get('total_providers', 0)}")
    
    async def demo_alert_management(self):
        """Demo: Alert Management"""
        print("\n🛠️  12. ALERT MANAGEMENT")
        print("-" * 50)
        
        # Get active rules
        active_rules = self.alerts.get_active_rules()
        print(f"📋 Faol qoidalar: {len(active_rules)}")
        
        if active_rules:
            # Pause first rule
            first_rule = active_rules[0]
            print(f"⏸️  Rule to'xtatilmoqda: {first_rule.name}")
            self.alerts.pause_rule(first_rule.id)
            print("✅ Rule to'xtatildi")
            
            # Resume rule
            print(f"▶️  Rule davom ettirilmoqda: {first_rule.name}")
            self.alerts.resume_rule(first_rule.id)
            print("✅ Rule davom ettirildi")
        
        # Get alert history
        print("\n📜 Alert History (oxirgi 5 ta):")
        history = self.alerts.get_alert_history(limit=5)
        for i, alert in enumerate(history, 1):
            print(f"   {i}. {alert.symbol} - {alert.alert_type.value} - {alert.message[:50]}...")
        
        print("\n✅ Alert management demo tugadi")
    
    async def trigger_test_alert(self, symbol: str, alert_type: AlertType, message: str):
        """Test uchun ogohlantirish triggerman"""
        # Create a test alert
        from smart_alerts import Alert, AlertStatus
        import uuid
        
        test_alert = Alert(
            id=str(uuid.uuid4()),
            rule_id="test-rule",
            alert_type=alert_type,
            symbol=symbol,
            message=message,
            severity="medium",
            channel=NotificationChannel.TELEGRAM,
            status=AlertStatus.TRIGGERED,
            triggered_at=datetime.now()
        )
        
        # Trigger the alert
        self.alerts._trigger_alert(test_alert)
        print(f"   🧪 Test alert triggered: {symbol} - {message}")
    
    def show_banner(self):
        """Demo banner ko'rsatish"""
        banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                   SMART ALERT SYSTEM                        ║
    ║                   Comprehensive Demo                        ║
    ║                                                              ║
    ║  🎯 Price Alerts       📈 Technical Indicators              ║
    ║  📊 Volume Alerts      📰 News-Based Alerts                 ║
    ║  💼 Portfolio Alerts   ⚠️  Risk Alerts                      ║
    ║  📅 Calendar Alerts    📝 Custom Watchlists                 ║
    ║                                                              ║
    ║  📧 Multi-Channel: Email, SMS, Push, Telegram               ║
    ║  🔄 Real-time Monitoring & Analytics                        ║
    ╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)


async def main():
    """Asosiy demo funksiya"""
    demo = SmartAlertsDemo()
    demo.show_banner()
    await demo.run_comprehensive_demo()


if __name__ == "__main__":
    # Demo ni ishga tushirish
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Demo to'xtatildi (Ctrl+C)")
    except Exception as e:
        print(f"\n\n💥 Demo xatoligi: {e}")
        import traceback
        traceback.print_exc()