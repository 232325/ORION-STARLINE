"""
Autonomous Decision System Demo

Performance Feedback Loops va Autonomous Decision Making tizimi
namoyishi
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autonomous_decisions import AutonomousDecisionSystem

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def demo_autonomous_decisions():
    """Asosiy demo"""
    print("=" * 60)
    print("🤖 AUTONOMOUS DECISION SYSTEM DEMO")
    print("=" * 60)
    
    # Tizim konfiguratsiyasi
    config = {
        "performance_update_interval": 10,  # 10 soniya
        "decision_timeout": 30,
        "confidence_threshold": 0.7,
        "min_trade_size": 1000.0,
        "max_trade_size": 50000.0,
        "risk_tolerance": 0.02,
        "large_trade_threshold": 0.1,
        "strategy_change_threshold": 0.05,
        "governance_timeout": 3600
    }
    
    try:
        # Tizim yaratish
        print("\n1️⃣ Tizim yaratish...")
        system = AutonomousDecisionSystem(config)
        
        # Tizimni ishga tushirish
        print("\n2️⃣ Tizimni ishga tushirish...")
        system.start()
        
        # System status
        print("\n3️⃣ Tizim holati:")
        status = system.get_system_status()
        print(f"   • Aktiv: {status['state']['is_active']}")
        print(f"   • Performance score: {status['state']['performance_score']:.2%}")
        print(f"   • Jami trade'lar: {status['state']['total_trades']}")
        
        # Market data yaratish
        print("\n4️⃣ Market data yaratish...")
        market_data = {
            "timestamp": datetime.now(),
            "symbols": ["EURUSD", "GBPUSD", "USDJPY"],
            "prices": {"EURUSD": 1.0945, "GBPUSD": 1.2750, "USDJPY": 149.85},
            "volumes": {"EURUSD": 1200, "GBPUSD": 800, "USDJPY": 600},
            "volatility": {"EURUSD": 0.012, "GBPUSD": 0.015, "USDJPY": 0.008},
            "trends": {"EURUSD": "bullish", "GBPUSD": "bearish", "USDJPY": "neutral"},
            "sentiment_score": 0.65
        }
        
        # Decision making
        print("\n5️⃣ Autonomous decision making...")
        decision = await system.make_decision(market_data)
        
        print(f"   • Qaror qabul qilish vaqti: {decision['timestamp']}")
        print(f"   • Generatsiya qilingan qarorlar: {len(decision['decisions'])}")
        print(f"   • Confidence score: {decision['confidence_score']:.2%}")
        
        # Performance summary
        print("\n6️⃣ Performance monitoring...")
        performance_summary = system.get_performance_summary()
        print(f"   • Performance data mavjud: {'✅' if 'current' in performance_summary else '❌'}")
        
        # Individual components demo
        print("\n7️⃣ Individual komponentlar:")
        
        # Performance Monitor
        print("   📊 Performance Monitor:")
        current_perf = await system.performance_monitor.get_current_performance()
        if 'metrics' in current_perf:
            metrics = current_perf['metrics']
            print(f"      • Daily return: {metrics.get('daily_return', 0):.3%}")
            print(f"      • Sharpe ratio: {metrics.get('sharpe_ratio', 0):.2f}")
            print(f"      • Max drawdown: {metrics.get('max_drawdown', 0):.3%}")
        
        # Trading Agent
        print("   🎯 Trading Agent:")
        trading_stats = system.trading_agent.get_decision_statistics()
        print(f"      • Jami qarorlar: {trading_stats.get('total_decisions', 0)}")
        print(f"      • Action distribution: {trading_stats.get('action_distribution', {})}")
        
        # Portfolio Manager
        print("   💼 Portfolio Manager:")
        portfolio_summary = system.portfolio_manager.get_portfolio_summary()
        print(f"      • Jami qiymat: ${portfolio_summary.get('total_value', 0):,.2f}")
        print(f"      • Pozitsiyalar soni: {portfolio_summary.get('positions_count', 0)}")
        print(f"      • Diversifikatsiya: {portfolio_summary.get('risk_metrics', {}).get('diversification_ratio', 0):.2f}")
        
        # Performance Attribution
        print("\n8️⃣ Performance Attribution Analysis:")
        attribution_result = await system.performance_attribution.analyze_performance(
            {"metrics": {"daily_return": 0.0025}}
        )
        if "attribution" in attribution_result:
            strategy_attrib = attribution_result["attribution"]["strategy_attribution"]
            print(f"      • Strategiya attribution: {list(strategy_attrib.keys())[:3]}")
        
        # Wait for some operations
        print("\n9️⃣ Sistem ishlashini kuzatish (5 soniya)...")
        await asyncio.sleep(5)
        
        # Final status
        print("\n🔟 Yakuniy holat:")
        final_status = system.get_system_status()
        print(f"   • Yangilangan vaqt: {final_status['state']['last_update']}")
        print(f"   • Jami trade'lar: {final_status['state']['total_trades']}")
        
        # Data export
        print("\n📊 Ma'lumotlarni eksport qilish:")
        export_data = await system.export_data("json")
        print(f"   • JSON export size: {len(export_data)} characters")
        
        print("\n" + "=" * 60)
        print("✅ DEMO MUVAFFAQIYATLI YAKUNLANDI!")
        print("=" * 60)
        
        # Tizimni to'xtatish
        print("\n🛑 Tizimni to'xtatish...")
        system.stop()
        print("   • Tizim muvaffaqiyatli to'xtatildi")
        
    except Exception as e:
        print(f"\n❌ Demo xatosi: {str(e)}")
        logging.error(f"Demo xatosi: {str(e)}", exc_info=True)

async def demo_performance_feedback():
    """Performance Feedback Loops demo"""
    print("\n" + "=" * 50)
    print("📈 PERFORMANCE FEEDBACK LOOPS DEMO")
    print("=" * 50)
    
    try:
        from autonomous_decisions.performance_feedback import PerformanceMonitor
        
        config = {
            "performance_update_interval": 5,
            "max_performance_history": 100
        }
        
        monitor = PerformanceMonitor(config)
        monitor.start()
        
        print("Performance monitoring started...")
        
        # Real-time performance updates
        for i in range(3):
            await asyncio.sleep(2)
            current = await monitor.get_current_performance()
            if 'metrics' in current:
                metrics = current['metrics']
                print(f"Update {i+1}: Return={metrics.get('daily_return', 0):.3%}, "
                      f"Sharpe={metrics.get('sharpe_ratio', 0):.2f}")
        
        # Performance summary
        summary = monitor.get_performance_summary()
        print(f"Performance summary: {len(summary)} data points")
        
        monitor.stop()
        print("Performance monitoring completed")
        
    except Exception as e:
        print(f"Performance feedback demo xatosi: {str(e)}")

async def demo_decision_making():
    """Decision Making demo"""
    print("\n" + "=" * 50)
    print("🎯 AUTONOMOUS DECISION MAKING DEMO")
    print("=" * 50)
    
    try:
        from autonomous_decisions.decision_making import TradingAgent
        
        config = {
            "base_position_size": 10000,
            "max_position_size": 50000,
            "min_confidence": 0.7,
            "max_risk_per_trade": 0.02
        }
        
        agent = TradingAgent(config)
        agent.start()
        
        print("Trading agent started...")
        
        # Mock market data
        market_data = {
            "prices": {"EURUSD": 1.0945, "GBPUSD": 1.2750},
            "volumes": {"EURUSD": 1000, "GBPUSD": 800},
            "volatility": {"EURUSD": 0.012, "GBPUSD": 0.015},
            "trends": {"EURUSD": "bullish", "GBPUSD": "bearish"},
            "sentiment_score": 0.65
        }
        
        performance_data = {
            "metrics": {"daily_return": 0.0025, "sharpe_ratio": 1.2, "max_drawdown": 0.05},
            "positions": [],
            "total_value": 100000
        }
        
        # Generate trading decision
        decision = await agent.make_decision(
            market_data, performance_data, {}, {}
        )
        
        print(f"Generated {len(decision['decisions'])} trading decisions")
        for i, d in enumerate(decision['decisions'][:2]):  # Show first 2
            print(f"  Decision {i+1}: {d['action_type']} {d['symbol']} "
                  f"(confidence: {d['confidence']:.2f})")
        
        # Get active positions
        positions = agent.get_active_positions()
        print(f"Active positions: {len(positions)}")
        
        agent.stop()
        print("Trading agent demo completed")
        
    except Exception as e:
        print(f"Decision making demo xatosi: {str(e)}")

async def main():
    """Main demo function"""
    try:
        # Asosiy demo
        await demo_autonomous_decisions()
        
        # Individual component demos
        await demo_performance_feedback()
        await demo_decision_making()
        
        print("\n🎉 BARCHA DEMO'LAR MUVAFFAQIYATLI YAKUNLANDI!")
        print("\nTizim xususiyatlari:")
        print("✅ Real-time performance monitoring")
        print("✅ Autonomous trading decisions")
        print("✅ Performance attribution analysis")
        print("✅ Portfolio rebalancing")
        print("✅ Risk-adjusted feedback mechanisms")
        print("✅ Multi-strategy decision making")
        print("✅ Governance integration ready")
        
    except Exception as e:
        print(f"\n❌ Umumiy demo xatosi: {str(e)}")
        logging.error(f"Umumiy demo xatosi: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())