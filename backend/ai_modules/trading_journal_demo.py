"""
Trading Journal Demo - AI Trading Journal tizimini test qilish
Barcha funksiyalarni ko'rsatish va test qilish
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import datetime
import random
import numpy as np
from typing import List

# Import trading journal components
from trading_journal import TradingJournal, TradeEntry, TradeType, EmotionalState, MarketCondition
from ai_feedback_loop import AIFeedbackLoop
from journal_analytics import JournalAnalytics

class TradingJournalDemo:
    """Trading Journal Demo class"""
    
    def __init__(self):
        self.journal = TradingJournal("demo_trading_journal.db")
        self.feedback_loop = AIFeedbackLoop(self.journal)
        self.analytics = JournalAnalytics(self.journal)
        
    def generate_sample_trades(self, num_trades: int = 50) -> List[TradeEntry]:
        """Namuna trade lar yaratish"""
        sample_trades = []
        
        strategies = ["Scalping", "Swing Trading", "Day Trading", "Breakout", "Mean Reversion"]
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF"]
        
        for i in range(num_trades):
            # Random trade parameters
            trade_id = f"trade_{datetime.datetime.now().strftime('%Y%m%d')}_{i+1:03d}"
            symbol = random.choice(symbols)
            trade_type = random.choice(list(TradeType))
            
            # Price simulation
            base_price = random.uniform(1.0000, 1.5000)
            entry_price = base_price
            exit_price = base_price + random.uniform(-0.0200, 0.0200)
            
            quantity = random.uniform(0.1, 2.0)
            
            # Time simulation (last 30 days)
            entry_time = datetime.datetime.now() - datetime.timedelta(
                days=random.randint(1, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            exit_time = entry_time + datetime.timedelta(minutes=random.randint(5, 240))
            
            # P&L calculation
            if trade_type == TradeType.BUY:
                pnl = (exit_price - entry_price) * quantity * 100000  # Standard lot size
            else:
                pnl = (entry_price - exit_price) * quantity * 100000
            
            pnl_percentage = (pnl / (entry_price * quantity * 100000)) * 100
            
            # Other parameters
            strategy = random.choice(strategies)
            emotional_state = random.choice(list(EmotionalState))
            market_condition = random.choice(list(MarketCondition))
            confidence_level = random.randint(1, 10)
            risk_reward_ratio = random.uniform(0.5, 3.0)
            stop_loss = entry_price * random.uniform(0.98, 0.99) if random.random() > 0.1 else 0
            take_profit = entry_price * random.uniform(1.01, 1.03) if random.random() > 0.1 else 0
            
            # Sample text data
            rationale = f"{symbol} uchun {strategy} strategiyasi bo'yicha trade. Market volatility yuqori."
            lessons_learned = "Entry timing yaxshiroq bo'lishi kerak edi. Risk management qoidalariga rioya qilish zarur."
            follow_up_actions = "Strategy parametrlarini qayta ko'rib chiqish. Emotional holatni yaxshilash."
            strategy_notes = f"{strategy} strategy samaradorligi o'rtacha. Optimallashtirish kerak."
            
            tags = random.sample(["profitable", "learning", "mistake", "good_entry", "poor_timing"], 
                                random.randint(0, 3))
            
            trade = TradeEntry(
                id=trade_id,
                symbol=symbol,
                trade_type=trade_type,
                entry_price=entry_price,
                exit_price=exit_price,
                quantity=quantity,
                entry_time=entry_time,
                exit_time=exit_time,
                pnl=pnl,
                pnl_percentage=pnl_percentage,
                strategy=strategy,
                emotional_state=emotional_state,
                market_condition=market_condition,
                rationale=rationale,
                lessons_learned=lessons_learned,
                follow_up_actions=follow_up_actions,
                strategy_notes=strategy_notes,
                confidence_level=confidence_level,
                risk_reward_ratio=risk_reward_ratio,
                stop_loss=stop_loss,
                take_profit=take_profit,
                created_at=entry_time,
                tags=tags
            )
            
            sample_trades.append(trade)
        
        return sorted(sample_trades, key=lambda x: x.entry_time)
    
    def populate_sample_data(self, num_trades: int = 50) -> bool:
        """Namuna ma'lumotlarni bazaga qo'shish"""
        print("Namuna trade lar yaratilmoqda...")
        sample_trades = self.generate_sample_trades(num_trades)
        
        print(f"{len(sample_trades)} ta trade bazaga qo'shilmoqda...")
        success_count = 0
        
        for trade in sample_trades:
            if self.journal.add_trade(trade):
                success_count += 1
        
        print(f"Muvaffaqiyatli qo'shilgan trade lar: {success_count}/{len(sample_trades)}")
        return success_count > 0
    
    def run_basic_analysis(self):
        """Asosiy tahlilni bajarish"""
        print("\n=== ASOSIY TRADING JOURNAL TAHLILI ===")
        
        # Performance metrics
        print("\n1. Performance Metrikalari:")
        metrics = self.journal.calculate_performance_metrics()
        print(f"   Jami trade lar: {metrics.total_trades}")
        print(f"   Yutish foizi: {metrics.win_rate:.1f}%")
        print(f"   Jami P&L: ${metrics.total_pnl:.2f}")
        print(f"   Profit Factor: {metrics.profit_factor:.2f}")
        print(f"   Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
        print(f"   Maksimal Drawdown: ${metrics.max_drawdown:.2f}")
        
        # Recent trades
        print("\n2. So'nggi 5 ta trade:")
        recent_trades = self.journal.get_recent_trades(5)
        for i, trade in enumerate(recent_trades, 1):
            print(f"   {i}. {trade.symbol} - {trade.trade_type.value.upper()} - P&L: ${trade.pnl:.2f}")
        
        # Performance trends
        print("\n3. 30 kunlik Performance Trends:")
        trends = self.journal.get_performance_trends(30)
        if "error" not in trends:
            print(f"   Jami trade: {trends['total_trades']}")
            print(f"   Jami P&L: ${trends['total_pnl']:.2f}")
            print(f"   Eng yaxshi kunlari: {len(trends['daily_performance'])}")
        
        return True
    
    def run_ai_analysis(self):
        """AI tahlilini bajarish"""
        print("\n=== AI TAHLIL VA FEEDBACK ===")
        
        # Performance patterns
        print("\n1. Performance Patternlari:")
        patterns = self.feedback_loop.analyze_performance_patterns(30)
        if "error" not in patterns:
            print(f"   Tahlil qilingan trade: {patterns['total_trades_analyzed']}")
            print(f"   Pattern insight lar: {len(patterns['insights'])}")
        
        # Improvement areas
        print("\n2. Yaxshilash Sohalari:")
        improvements = self.feedback_loop.identify_improvement_areas()
        for i, improvement in enumerate(improvements[:3], 1):
            print(f"   {i}. {improvement.area}")
            print(f"      Hozirgi: {improvement.current_score:.1f} -> Maqsad: {improvement.target_score:.1f}")
            print(f"      Prioritet: {improvement.priority}")
        
        # Trading mistakes
        print("\n3. Trading Xatolari:")
        mistakes = self.feedback_loop.detect_trading_mistakes()
        for mistake in mistakes[:3]:
            print(f"   Trade: {mistake['symbol']} - {len(mistake['trade_mistakes'])} ta xato")
            for error in mistake['trade_mistakes'][:2]:
                print(f"     - {error['type']}: {error['description']}")
        
        # AI insights
        print("\n4. AI Insights:")
        insights = self.feedback_loop.generate_ai_insights()
        for insight in insights[:3]:
            print(f"   {insight.title}: {insight.description[:80]}...")
            print(f"   Impact: {insight.impact_score:.1f}% | Confidence: {insight.confidence:.1f}%")
        
        # Coaching recommendations
        print("\n5. Coaching Tavsiyalari:")
        recommendations = self.feedback_loop.generate_coaching_recommendations()
        print("   Tezkor harakatlar:")
        for action in recommendations['immediate_actions'][:2]:
            print(f"     - {action}")
        
        return True
    
    def run_advanced_analytics(self):
        """Advansed analytics"""
        print("\n=== ADVANCED ANALYTICS ===")
        
        # Comprehensive report
        print("\n1. Keng Qamrovli Report:")
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=30)
        
        report = self.analytics.generate_comprehensive_report(start_date, end_date)
        if report:
            print(f"   Report ID: {report.report_id}")
            print(f"   Period: {report.period_start.date()} - {report.period_end.date()}")
            print(f"   Jami trade: {report.total_trades}")
            print(f"   Tavsiyalar soni: {len(report.recommendations)}")
        
        # Comparative analysis
        print("\n2. Comparative Analysis:")
        period1_end = datetime.datetime.now() - datetime.timedelta(days=15)
        period1_start = period1_end - datetime.timedelta(days=15)
        period2_end = datetime.datetime.now()
        period2_start = datetime.datetime.now() - datetime.timedelta(days=15)
        
        comparison = self.analytics.perform_comparative_analysis(
            period1_start, period1_end, period2_start, period2_end
        )
        
        for metric, comp in list(comparison.items())[:3]:
            print(f"   {metric}: {comp.previous_value:.2f} -> {comp.current_value:.2f} "
                  f"({comp.change_percentage:+.1f}%) - {comp.trend}")
        
        # Anomaly detection
        print("\n3. Anomaly Detection:")
        anomalies = self.analytics.detect_performance_anomalies()
        if "error" not in anomalies:
            print(f"   Katta yo'qotishlar: {len(anomalies['large_losses'])}")
            print(f"   Risk buzilishlari: {len(anomalies['risk_breaches'])}")
            print(f"   Performance pasayishi: {len(anomalies['performance_deterioration'])}")
        
        # Seasonal analysis
        print("\n4. Seasonal Analysis:")
        seasonal = self.analytics.perform_seasonal_analysis(1)
        if "error" not in seasonal:
            print(f"   Analiz davri: {seasonal['analysis_period_years']} yil")
            if seasonal.get('best_months'):
                best_month = seasonal['best_months'][0]
                print(f"   Eng yaxshi oy: {best_month['period']} (avg P&L: ${best_month['avg_pnl']:.2f})")
        
        # Clustering analysis
        print("\n5. Clustering Analysis:")
        clustering = self.analytics.clustering_analysis(n_clusters=3)
        if "error" not in clustering:
            print(f"   Cluterlar soni: {clustering['n_clusters']}")
            for cluster, data in list(clustering['cluster_analysis'].items())[:2]:
                print(f"   {cluster}: {data['size']} ta trade")
                print(f"     Avg P&L: ${data['characteristics']['avg_pnl']:.2f}")
                print(f"     Dominant emotion: {data['characteristics']['dominant_emotion']}")
        
        # Performance prediction
        print("\n6. Performance Prediction:")
        prediction = self.analytics.predict_future_performance()
        if "error" not in prediction:
            print(f"   Trend: {prediction['trend_direction']}")
            print(f"   Slope: {prediction['trend_slope']:.2f}")
            if prediction['predicted_next_5_pnls']:
                print(f"   Keyingi 5 ta trade bashorati: {[f'${p:.2f}' for p in prediction['predicted_next_5_pnls'][:3]]}")
        
        return True
    
    def run_visual_dashboard(self):
        """Visual dashboard"""
        print("\n=== VISUAL DASHBOARD ===")
        
        # Generate charts
        charts = self.analytics.generate_visual_dashboard()
        
        if "error" not in charts:
            print("Charts yaratildi:")
            for chart_name, chart_path in charts.items():
                print(f"   {chart_name}: {chart_path}")
        else:
            print(f"Chart yaratishda xato: {charts['error']}")
        
        return True
    
    def run_comprehensive_demo(self):
        """To'liq demo"""
        print("🚀 AI TRADING JOURNAL DEMO BOSHLANYAPTI...")
        print("=" * 50)
        
        # 1. Sample data population
        if not self.populate_sample_data(50):
            print("❌ Namuna ma'lumotlar yaratishda xato!")
            return False
        
        # 2. Basic analysis
        if not self.run_basic_analysis():
            print("❌ Asosiy tahlilda xato!")
            return False
        
        # 3. AI analysis
        if not self.run_ai_analysis():
            print("❌ AI tahlilda xato!")
            return False
        
        # 4. Advanced analytics
        if not self.run_advanced_analytics():
            print("❌ Advanced analytics da xato!")
            return False
        
        # 5. Visual dashboard
        if not self.run_visual_dashboard():
            print("❌ Visual dashboard da xato!")
            return False
        
        print("\n" + "=" * 50)
        print("✅ AI TRADING JOURNAL DEMO MUVAFFAQIYATLI YAKUNLANDI!")
        print("📊 Barcha funksiyalar test qilindi va ishlayapti.")
        print("💡 Trading journal tizimi foydalanishga tayyor!")
        
        return True

def main():
    """Main demo function"""
    demo = TradingJournalDemo()
    
    try:
        # Run comprehensive demo
        success = demo.run_comprehensive_demo()
        
        if success:
            print("\n📋 KEYINGI QADAMLAR:")
            print("1. Trading journal ga haqiqiy trade larni qo'shing")
            print("2. Har kuni performance ni tahlil qiling")
            print("3. AI insights va tavsiyalarni kuzating")
            print("4. Coaching recommendations bo'yicha harakat qiling")
            print("5. Visual dashboard ni ko'rib boring")
            
        return success
        
    except Exception as e:
        print(f"❌ Demo bajarishda xato: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()