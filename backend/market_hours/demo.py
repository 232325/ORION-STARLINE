"""
Market Hours Timing System Demo
Barcha komponentlarni integratsiya qiluvchi demo tizim
"""

import pytz
from datetime import datetime, timedelta
import json
from typing import Dict, List

# Import all modules
from market_hours_manager import MarketHoursManager
from forex.forex_sessions import ForexSessionAnalyzer
from metals.metal_markets import MetalMarketsAnalyzer  
from news.news_integration import NewsIntegrationSystem
from analytics.optimization import MarketHoursAnalytics

class MarketTimingDemo:
    """Market Timing Demo System"""
    
    def __init__(self):
        # Initialize all components
        self.market_manager = MarketHoursManager()
        self.forex_analyzer = ForexSessionAnalyzer()
        self.metals_analyzer = MetalMarketsAnalyzer()
        self.news_system = NewsIntegrationSystem()
        self.analytics = MarketHoursAnalytics()
        
        # Set demo timezone
        self.demo_timezone = pytz.timezone("GMT")
        
    def run_comprehensive_demo(self, current_time: datetime = None):
        """Comprehensive demo barcha xususiyatlar bilan"""
        
        if current_time is None:
            current_time = datetime.now(pytz.UTC)
        
        print("=" * 80)
        print("🌍 MARKET HOURS TIMING OPTIMIZATION SYSTEM DEMO")
        print("=" * 80)
        print(f"⏰ Joriy vaqt: {current_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print()
        
        # 1. Market Status Overview
        self._demo_market_status(current_time)
        
        # 2. Forex Sessions Analysis
        self._demo_forex_analysis(current_time)
        
        # 3. Metal Markets Analysis
        self._demo_metals_analysis(current_time)
        
        # 4. News Integration
        self._demo_news_analysis(current_time)
        
        # 5. Session Overlap Analysis
        self._demo_overlap_analysis(current_time)
        
        # 6. Trading Strategy Optimization
        self._demo_strategy_optimization(current_time)
        
        # 7. Risk Management Recommendations
        self._demo_risk_management(current_time)
        
        # 8. Advanced Analytics
        self._demo_analytics(current_time)
        
        # 9. Portfolio Timing
        self._demo_portfolio_timing(current_time)
        
        # 10. Complete Trading Plan
        self._demo_complete_trading_plan(current_time)
        
        print("\n" + "=" * 80)
        print("✅ Demo tugallandi!")
        print("=" * 80)
    
    def _demo_market_status(self, current_time: datetime):
        """Bozor holati demo"""
        print("📊 1. JORIY BOZOR HOLATI")
        print("-" * 50)
        
        status = self.market_manager.get_current_market_status(current_time)
        summary = self.market_manager.get_market_hours_summary()
        
        is_open_text = "✅ Ha" if status.is_open else "❌ Yo'q"
        print(f"🚪 Bozor ochiqmi: {is_open_text}")
        print(f"📈 Joriy sessiya: {status.current_session.value if status.current_session else 'Hech qaysi'}")
        print(f"🎯 Volatil daraja: {status.volatility_level:.1f}x")
        print(f"⚡ Aktiv sessiyalar: {', '.join(summary['active_sessions']) if summary['active_sessions'] else 'Hech qaysi'}")
        print(f"🏭 Metal bozorlari: {', '.join(summary['active_metal_markets']) if summary['active_metal_markets'] else 'Hech qaysi'}")
        
        if status.time_to_next_event:
            hours_remaining = status.time_to_next_event.total_seconds() / 3600
            print(f"⏰ Keyingi voqea: {hours_remaining:.1f} soatdan keyin")
        
        print()
    
    def _demo_forex_analysis(self, current_time: datetime):
        """Forex sessiyalari tahlili"""
        print("💱 2. FOREX SESSIYA TAHLILI")
        print("-" * 50)
        
        # Current session analysis
        session_analysis = self.forex_analyzer.analyze_current_session(current_time)
        
        if session_analysis:
            print(f"📊 Aktv sessiya: {session_analysis.name}")
            print(f"🎯 Fazasi: {session_analysis.current_phase.value}")
            print(f"⚡ Volatil daraja: {session_analysis.volatility_level.value}")
            print(f"📈 Trading intensivlik: {session_analysis.trading_intensity:.1%}")
            print(f"💰 Eng yaxshi pairlar: {', '.join(session_analysis.best_currency_pairs)}")
            print(f"⏰ Qolgan vaqt: {session_analysis.time_remaining}")
        else:
            print("ℹ️ Joriy vaqtda aktiv forex sessiyasi yo'q")
        
        # Next session info
        next_session = self.forex_analyzer.get_next_session_info(current_time)
        if next_session:
            print(f"📅 Keyingi sessiya: {next_session['next_session']}")
            print(f"⏰ Boshlanish vaqti: {next_session['local_time']}")
            print(f"⏳ Gacha vaqt: {next_session['time_to_start']}")
        
        print()
    
    def _demo_metals_analysis(self, current_time: datetime):
        """Metal bozorlari tahlili"""
        print("🥇 3. METAL BOZORLARI TAHLILI")
        print("-" * 50)
        
        metal_analysis = self.metals_analyzer.analyze_current_metal_markets(current_time)
        
        for analysis in metal_analysis:
            status_icon = "✅" if analysis.is_open else "❌"
            print(f"{status_icon} {analysis.market_name}")
            
            if analysis.is_open:
                print(f"   📅 Fazasi: {analysis.current_phase.value}")
                print(f"   ⚡ Volatil trend: {analysis.volatility_trend}")
                print(f"   🏆 Trading metals: {', '.join(analysis.metals_trading[:3])}")
                print(f"   📦 Inventory impact: {analysis.inventory_impact:.1f}")
                
                if analysis.next_events:
                    next_event = analysis.next_events[0]
                    print(f"   📋 Keyingi voqea: {next_event['type']}")
            else:
                print(f"   📅 Yopiq")
        
        print()
    
    def _demo_news_analysis(self, current_time: datetime):
        """News integration tahlili"""
        print("📰 4. YANGILIKLAR INTEGRATSIYASI")
        print("-" * 50)
        
        # Upcoming events
        upcoming_events = self.news_system.get_upcoming_news_events(current_time, hours_ahead=24)
        
        print(f"📅 24 soat ichida voqealar: {len(upcoming_events)} ta")
        
        high_impact_events = [e for e in upcoming_events if e.impact_level.value == 'high']
        print(f"🔥 Yuqori ta'sirli voqealar: {len(high_impact_events)} ta")
        
        # Show top events
        for event in upcoming_events[:3]:
            time_until = event.scheduled_time - current_time
            hours_until = time_until.total_seconds() / 3600
            
            print(f"📊 {event.title}")
            print(f"   🕐 Vaqt: {event.scheduled_time.strftime('%m-%d %H:%M UTC')}")
            print(f"   ⚡ Ta'sir: {event.impact_level.value}")
            print(f"   ⏳ Gacha: {hours_until:.1f} soat")
            print(f"   💰 Ta'sir qiluvchi: {', '.join(event.affected_assets[:3])}")
            print()
        
        print()
    
    def _demo_overlap_analysis(self, current_time: datetime):
        """Session overlap tahlili"""
        print("🔄 5. SESSION OVERLAP TAHLILI")
        print("-" * 50)
        
        overlaps = self.forex_analyzer.get_session_overlap_analysis(current_time)
        
        for overlap in overlaps:
            status_icon = "🟢" if overlap["is_active"] else "🔴"
            print(f"{status_icon} {overlap['display_name']}")
            print(f"   ⏰ Vaqt: {overlap['start_time']} - {overlap['end_time']}")
            print(f"   📝 Xususiyat: {overlap['characteristics']}")
            print(f"   ⚡ Volatil boost: {overlap['volatility_multiplier']:.1f}x")
            print(f"   🎯 Optimal: {overlap['optimal_for']}")
            print()
        
        print()
    
    def _demo_strategy_optimization(self, current_time: datetime):
        """Strategiya optimizatsiyasi"""
        print("🎯 6. STRATEGIYA OPTIMIZATSIYASI")
        print("-" * 50)
        
        strategies = ["scalping", "swing", "breakout", "news_trading"]
        
        for strategy in strategies:
            print(f"📈 {strategy.title()}:")
            
            # Forex strategy optimization
            forex_rec = self.forex_analyzer.optimize_trading_strategy(strategy, current_time)
            if forex_rec["recommendations"]:
                rec = forex_rec["recommendations"][0]
                print(f"   💡 Tavsiya: {rec['action']}")
                print(f"   📝 Sabab: {rec['reason']}")
            
            # Metal strategy optimization
            metal_rec = self.metals_analyzer.optimize_metal_trading_timing("gold", strategy, current_time)
            if metal_rec.get("recommendations"):
                rec = metal_rec["recommendations"][0]
                print(f"   🥇 {rec.get('action', 'N/A')}: {rec.get('reason', 'N/A')}")
            
            print()
        
        print()
    
    def _demo_risk_management(self, current_time: datetime):
        """Risk management tavsiyalar"""
        print("⚠️ 7. RISK MANAGEMENT")
        print("-" * 50)
        
        # Generate recommendations
        recommendations = self.analytics.generate_trading_recommendations(current_time, "balanced")
        
        print("🚨 Joriy xavflar:")
        for warning in recommendations["risk_warnings"]:
            print(f"   ⚠️ {warning['warning']}: {warning['description']}")
        
        print("\n📋 Joriy harakatlar:")
        for action in recommendations["immediate_actions"]:
            print(f"   ✅ {action['action']}: {action['reason']}")
            print(f"      ⏰ Vaqt: {action['timeframe']}")
            print(f"      📊 Ishonchlilik: {action['confidence']:.0%}")
        
        print("\n📏 Position sizing:")
        for key, value in recommendations["position_sizing"].items():
            print(f"   📏 {key}: {value}")
        
        print()
    
    def _demo_analytics(self, current_time: datetime):
        """Advanced analytics"""
        print("📊 8. ADVANCED ANALYTICS")
        print("-" * 50)
        
        # Market efficiency
        efficiency = self.analytics.calculate_market_efficiency_metrics(current_time)
        print("🔧 Market efficiency:")
        for metric, value in list(efficiency.items())[:4]:
            print(f"   📊 {metric}: {value:.1%}")
        
        # Optimization results
        optimization = self.analytics.optimize_trading_schedule("balanced", risk_tolerance=0.5)
        print(f"\n🎯 Optimization confidence: {optimization.confidence_score:.1%}")
        
        print("📅 Optimal times:")
        for time_slot in optimization.optimal_times[:3]:
            print(f"   ⏰ {time_slot['time']}: {time_slot['reason']} (Score: {time_slot['score']})")
        
        print(f"\n📈 Expected performance:")
        perf = optimization.expected_performance
        print(f"   🏆 Success rate: {perf['success_rate']:.1%}")
        print(f"   💰 Avg return: {perf['avg_return']:.1%}")
        print(f"   📊 Sharpe ratio: {perf['sharpe_ratio']:.1f}")
        print(f"   ⚠️ Max drawdown: {perf['max_drawdown']:.1%}")
        
        print()
    
    def _demo_portfolio_timing(self, current_time: datetime):
        """Portfolio timing optimization"""
        print("💼 9. PORTFOLIO TIMING")
        print("-" * 50)
        
        # Sample portfolio
        portfolio = {
            "major_pairs": 0.4,
            "minor_pairs": 0.2,
            "precious_metals": 0.2,
            "industrial_metals": 0.1,
            "cash": 0.1
        }
        
        optimization = self.analytics.optimize_portfolio_timing(portfolio, current_time)
        
        print("🔄 Tavsiya etilgan o'zgarishlar:")
        for change in optimization["recommended_changes"]:
            change_pct = change["change"] * 100
            direction = "⬆️" if change_pct > 0 else "⬇️" if change_pct < 0 else "➡️"
            print(f"   {direction} {change['asset']}: {change['current']:.1%} → {change['optimal']:.1%} ({change_pct:+.1f}%)")
        
        print(f"\n🎯 Rebalance sababi: {optimization['timing_justification']}")
        
        print()
    
    def _demo_complete_trading_plan(self, current_time: datetime):
        """Complete trading plan"""
        print("📋 10. TO'LIQ TRADING REJA")
        print("-" * 50)
        
        # Get all recommendations
        market_status = self.market_manager.get_current_market_status(current_time)
        recommendations = self.analytics.generate_trading_recommendations(current_time)
        
        print("🎯 Hozirgi holat tahlili:")
        print(f"   📊 Bozor holati: {'Faol' if market_status.is_open else 'Sukunatli'}")
        print(f"   ⚡ Volatil daraja: {market_status.volatility_level:.1f}x")
        
        if market_status.current_session:
            print(f"   📅 Asosiy sessiya: {market_status.current_session.value}")
        
        print(f"\n📈 Trading tavsiyalari:")
        
        # Time-based recommendations
        current_hour = current_time.hour
        if 8 <= current_hour <= 12:
            print("   ✅ European session - trend following uchun optimal")
            print("   💡 Major pairs da pozitsiya ochish tavsiya etiladi")
        elif 13 <= current_hour <= 17:
            print("   ✅ European-American overlap - scalping uchun ideal")
            print("   💡 High-frequency trading strategiyasi")
        elif 0 <= current_hour <= 9:
            print("   ⚠️ Asian session - range-bound trading")
            print("   💡 Mean reversion strategiyasi")
        else:
            print("   ⚠️ Off-market hours - sabr kutish kerak")
        
        print(f"\n⏰ Optimal entry vaqtlari:")
        print("   📅 Pre-market: News voqealaridan 30 daqiqa oldin")
        print("   📅 Regular hours: Session boshlanishidan 15 daqiqa oldin")  
        print("   📅 Post-news: Voqeadan 1-3 soat keyin")
        
        print(f"\n🛡️ Risk management:")
        print("   📏 Position size: Capital ning 1-2%")
        print("   ⚠️ Stop loss: 1R (risk-reward ratio)")
        print("   💰 Take profit: 1.5-2R")
        print("   ⏰ Time exit: Major news dan 30 daqiqa oldin yopish")
        
        print(f"\n🎯 Keyingi 24 soat reja:")
        print("   📊 Monitor qilish: High-impact news voqealarini")
        print("   📈 Pozitsiya: Session overlap davrlarida kengaytirish")
        print("   🛡️ Hedging: Inventory report oldidan himoya")
        print("   📋 Review: Har kuni bozor yopilishidan keyin natijalarni tahlil qilish")
        
        print()
    
    def export_trading_dashboard(self, current_time: datetime, filename: str = "trading_dashboard.json"):
        """Trading dashboard export"""
        
        dashboard_data = {
            "timestamp": current_time.isoformat(),
            "market_status": self.market_manager.get_market_hours_summary(),
            "upcoming_events": [
                {
                    "title": event.title,
                    "time": event.scheduled_time.isoformat(),
                    "impact": event.impact_level.value,
                    "time_until": str(event.time_until_event) if event.time_until_event else None
                }
                for event in self.news_system.get_upcoming_news_events(current_time, hours_ahead=24)[:10]
            ],
            "session_recommendations": self.forex_analyzer.optimize_trading_strategy("balanced", current_time),
            "metal_opportunities": [
                self.metals_analyzer.optimize_metal_trading_timing(metal, "scalping", current_time)
                for metal in ["gold", "silver", "copper"]
            ],
            "risk_metrics": self.analytics.calculate_market_efficiency_metrics(current_time)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Dashboard export qilindi: {filename}")
        return filename

def main():
    """Main demo function"""
    
    # Create demo instance
    demo = MarketTimingDemo()
    
    # Run comprehensive demo
    demo.run_comprehensive_demo()
    
    # Export trading dashboard
    current_time = datetime.now(pytz.UTC)
    demo.export_trading_dashboard(current_time)
    
    print(f"\n🎉 Demo muvaffaqiyatli tugallandi!")
    print(f"📁 Barcha ma'lumotlar dashboard ga eksport qilindi.")

if __name__ == "__main__":
    main()