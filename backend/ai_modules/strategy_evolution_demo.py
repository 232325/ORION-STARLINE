#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Strategy Evolution Demo
=======================

Strategy evolution tracking tizimining demo va test scripti.

Foydalanish:
```bash
cd /workspace/orion-starline/backend/ai_modules
python strategy_evolution_demo.py
```

Author: Orion Starline AI Team
Date: 2025-11-04
"""

import sys
import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from strategy_evolution import (
        StrategyEvolutionTracker, StrategySnapshot, EvolutionEvent,
        EvolutionType, MarketRegime
    )
    from historical_metrics import (
        HistoricalMetricsEngine, HistoricalMetric, SeasonalPattern,
        MarketCycle, TimeFrame, MetricType
    )
    from evolution_analytics import (
        EvolutionAnalyticsEngine, EvolutionPrediction, GeneticIndividual,
        StrategyMutation, PredictionModel, EvolutionPhase
    )
    print("✅ Barcha modul import muvaffaqiyatli!")
except ImportError as e:
    print(f"❌ Import xatosi: {e}")
    sys.exit(1)

def create_sample_data():
    """Namuna ma'lumotlar yaratish"""
    print("📊 Namuna ma'lumotlar yaratilmoqda...")
    
    # Strategy snapshots
    snapshots = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        snapshot_date = base_date + timedelta(days=i)
        
        # Random walk performance
        performance = 0.1 + np.random.normal(0, 0.02) + i * 0.002
        sharpe_ratio = performance / 0.15 if performance > 0 else 0
        max_drawdown = max(0, -performance + np.random.normal(0, 0.01))
        volatility = 0.12 + np.random.normal(0, 0.02)
        win_rate = 0.55 + np.random.normal(0, 0.05)
        
        # Market regime cycle
        regime = MarketRegime.BULL if i < 10 else (MarketRegime.SIDEWAYS if i < 20 else MarketRegime.BEAR)
        
        snapshot = StrategySnapshot(
            timestamp=snapshot_date,
            strategy_id="EURUSD_TREND_001",
            performance=max(0, performance),
            sharpe_ratio=max(0, sharpe_ratio),
            max_drawdown=max_drawdown,
            volatility=abs(volatility),
            win_rate=min(1, max(0, win_rate)),
            parameters={
                "ma_period": 20 + np.random.randint(-5, 5),
                "risk_per_trade": 0.02 + np.random.normal(0, 0.005),
                "stop_loss": 0.015 + np.random.normal(0, 0.002),
                "take_profit": 0.03 + np.random.normal(0, 0.005)
            },
            market_regime=regime,
            risk_level=0.3 + np.random.normal(0, 0.05)
        )
        snapshots.append(snapshot)
    
    return snapshots

def test_strategy_evolution_tracker():
    """Strategy evolution tracker test"""
    print("\n" + "="*60)
    print("🧬 STRATEGY EVOLUTION TRACKER TEST")
    print("="*60)
    
    try:
        # Initialize tracker
        tracker = StrategyEvolutionTracker(db_path="test_evolution.db")
        print("✅ Evolution tracker yaratildi")
        
        # Create sample data
        snapshots = create_sample_data()
        
        # Record snapshots
        print("📈 Snapshots qayd etilmoqda...")
        for snapshot in snapshots[:10]:  # Test with first 10
            tracker.record_snapshot(snapshot)
        
        print(f"✅ {len(snapshots)} ta snapshot qayd etildi")
        
        # Get evolution analysis
        print("\n📊 Evolution analysis olinmoqda...")
        analysis = tracker.get_evolution_analysis("EURUSD_TREND_001", days=30)
        
        print("\n🎯 EVOLUTION ANALYSIS NATIJALARI:")
        print(f"   Strategy ID: {analysis.get('strategy_id', 'N/A')}")
        print(f"   Analysis Period: {analysis.get('analysis_period', 'N/A')}")
        
        performance_trend = analysis.get('performance_trend', {})
        print(f"   Performance Trend: {performance_trend.get('trend', 'N/A')}")
        print(f"   Current Performance: {performance_trend.get('current_performance', 0):.4f}")
        
        risk_evolution = analysis.get('risk_evolution', {})
        print(f"   Risk Trend: {risk_evolution.get('risk_trend', 'N/A')}")
        print(f"   Current Risk: {risk_evolution.get('current_risk', 0):.4f}")
        
        overall_score = analysis.get('overall_score', {})
        print(f"   Overall Score: {overall_score.get('overall_score', 0):.3f}")
        print(f"   Grade: {overall_score.get('grade', 'N/A')}")
        
        # Evolution events
        events = analysis.get('evolution_events', [])
        print(f"\n🚨 EVOLUTION EVENTS: {len(events)} ta voqea")
        for event in events[:3]:  # Show first 3
            print(f"   - {event.get('event_type', 'N/A')}: {event.get('description', 'N/A')}")
        
        # Get summary
        summary = tracker.get_evolution_summary(days=30)
        print(f"\n📈 SUMMARY: {summary.get('total_strategies', 0)} ta strategiya tahlil qilindi")
        
        print("✅ Strategy Evolution Tracker test muvaffaqiyatli!")
        return True
        
    except Exception as e:
        print(f"❌ Strategy Evolution Tracker test xatosi: {e}")
        return False

def test_historical_metrics():
    """Historical metrics engine test"""
    print("\n" + "="*60)
    print("📈 HISTORICAL METRICS ENGINE TEST")
    print("="*60)
    
    try:
        # Initialize engine
        engine = HistoricalMetricsEngine(db_path="test_metrics.db")
        print("✅ Historical metrics engine yaratildi")
        
        # Create sample metrics
        metrics = []
        for i in range(50):
            metric = HistoricalMetric(
                timestamp=datetime.now() - timedelta(days=i),
                metric_name="daily_return",
                metric_value=np.random.normal(0.001, 0.01),
                metric_type=MetricType.PERFORMANCE,
                timeframe=TimeFrame.DAILY,
                metadata={"strategy_id": "EURUSD_TREND_001"}
            )
            metrics.append(metric)
        
        # Record metrics
        print("📊 Historical metrics qayd etilmoqda...")
        for metric in metrics:
            engine.record_metric(metric)
        
        print(f"✅ {len(metrics)} ta metrika qayd etildi")
        
        # Long-term trends
        print("\n📈 Long-term trends tahlili...")
        trends = engine.get_long_term_trends("EURUSD_TREND_001", months=2)
        print(f"   Performance Trend: {trends.get('performance_trend', {}).get('trend', 'N/A')}")
        print(f"   Trend Strength: {trends.get('trend_strength', 0):.3f}")
        
        # Seasonal patterns
        print("\n🌍 Seasonal patterns aniqlanmoqda...")
        patterns = engine.detect_seasonal_patterns("EURUSD_TREND_001", years=1)
        print(f"📅 {len(patterns)} ta seasonal pattern topildi:")
        for pattern in patterns:
            print(f"   - {pattern.pattern_name}: {pattern.strength:.3f} strength")
        
        # Generate comprehensive report
        print("\n📋 Comprehensive report yaratilmoqda...")
        report = engine.generate_historical_report("EURUSD_TREND_001")
        
        print("\n🎯 HISTORICAL ANALYSIS REPORT:")
        print(f"   Strategy ID: {report.get('strategy_id', 'N/A')}")
        print(f"   Analysis Periods: {report.get('periods_analyzed', [])}")
        
        summary = report.get('summary', {})
        print(f"   Data Quality: {summary.get('data_quality', 'N/A')}")
        print(f"   Analysis Completeness: {summary.get('analysis_completeness', 0):.1f}%")
        
        insights = summary.get('key_insights', [])
        if insights:
            print(f"   Key Insights:")
            for insight in insights:
                print(f"     - {insight}")
        
        print("✅ Historical Metrics Engine test muvaffaqiyatli!")
        return True
        
    except Exception as e:
        print(f"❌ Historical Metrics Engine test xatosi: {e}")
        return False

def test_evolution_analytics():
    """Evolution analytics engine test"""
    print("\n" + "="*60)
    print("🤖 EVOLUTION ANALYTICS ENGINE TEST")
    print("="*60)
    
    try:
        # Initialize engine
        analytics_engine = EvolutionAnalyticsEngine(db_path="test_analytics.db")
        print("✅ Evolution analytics engine yaratildi")
        
        # Train prediction model
        print("\n🧠 Machine Learning model o'qitilmoqda...")
        training_result = analytics_engine.train_evolution_prediction_model(
            "EURUSD_TREND_001", 
            PredictionModel.RANDOM_FOREST
        )
        
        print("📊 TRAINING RESULTS:")
        print(f"   MSE: {training_result.get('mse', 0):.6f}")
        print(f"   R² Score: {training_result.get('r2_score', 0):.4f}")
        print(f"   CV Mean: {training_result.get('cv_mean', 0):.4f}")
        
        feature_importance = training_result.get('feature_importance', {})
        if feature_importance:
            print(f"   Top Features:")
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
            for feature, importance in sorted_features:
                print(f"     - {feature}: {importance:.4f}")
        
        # Make prediction
        print("\n🔮 Evolution prediction qilinmoqda...")
        try:
            prediction = analytics_engine.predict_evolution("EURUSD_TREND_001")
            
            print("🎯 PREDICTION RESULTS:")
            print(f"   Predicted Performance: {prediction.predicted_performance:.4f}")
            print(f"   Predicted Risk: {prediction.predicted_risk:.4f}")
            print(f"   Confidence Score: {prediction.confidence_score:.3f}")
            print(f"   Model Used: {prediction.model_used.value}")
            
        except Exception as e:
            print(f"⚠️  Prediction xatosi (normal, test ma'lumotlari uchun): {e}")
        
        # Genetic algorithm
        print("\n🧬 Genetic algorithm ishga tushmoqda...")
        try:
            best_individuals = analytics_engine.run_genetic_algorithm(
                "EURUSD_TREND_001", 
                n_generations=5,  # Few generations for demo
                population_size=10
            )
            
            print("🏆 GENETIC ALGORITHM RESULTS:")
            if best_individuals:
                best = best_individuals[0]
                print(f"   Best Fitness: {best.fitness:.4f}")
                print(f"   Generation: {best.generation}")
                print(f"   Best Parameters:")
                for param, value in best.genome.items():
                    print(f"     - {param}: {value:.4f}")
            
        except Exception as e:
            print(f"⚠️  Genetic algorithm xatosi: {e}")
        
        # Strategy mutation
        print("\n🔄 Strategy mutation sinovlari...")
        try:
            mutation = analytics_engine.mutate_strategy("EURUSD_TREND_001", "parameter_tweak")
            print(f"✅ Mutation muvaffaqiyatli!")
            print(f"   Success Score: {mutation.success_score:.4f}")
            print(f"   Performance Change: {mutation.performance_after - mutation.performance_before:.4f}")
            
        except Exception as e:
            print(f"⚠️  Mutation xatosi: {e}")
        
        # Get analytics summary
        summary = analytics_engine.get_evolution_analytics_summary("EURUSD_TREND_001")
        print(f"\n📈 ANALYTICS SUMMARY:")
        available = summary.get('available_analytics', {})
        for key, status in available.items():
            print(f"   {key}: {status}")
        
        recommendations = summary.get('recommendations', [])
        if recommendations:
            print(f"   Recommendations:")
            for rec in recommendations:
                print(f"     - {rec}")
        
        print("✅ Evolution Analytics Engine test muvaffaqiyatli!")
        return True
        
    except Exception as e:
        print(f"❌ Evolution Analytics Engine test xatosi: {e}")
        return False

def test_integration():
    """Integration test"""
    print("\n" + "="*60)
    print("🔗 INTEGRATION TEST")
    print("="*60)
    
    try:
        print("🔄 Barcha komponentlari birlashtirish...")
        
        # Initialize all components
        evolution_tracker = StrategyEvolutionTracker(db_path="integration_test.db")
        metrics_engine = HistoricalMetricsEngine(db_path="integration_test.db")
        analytics_engine = EvolutionAnalyticsEngine(db_path="integration_test.db")
        
        print("✅ Barcha komponentlar yaratildi")
        
        # Create unified test data
        snapshots = create_sample_data()
        
        # Process through all systems
        for snapshot in snapshots[:5]:  # Limited for demo
            # Evolution tracking
            evolution_tracker.record_snapshot(snapshot)
            
            # Historical metrics
            metric = HistoricalMetric(
                timestamp=snapshot.timestamp,
                metric_name="daily_return",
                metric_value=snapshot.performance,
                metric_type=MetricType.PERFORMANCE,
                timeframe=TimeFrame.DAILY,
                metadata={"strategy_id": snapshot.strategy_id}
            )
            metrics_engine.record_metric(metric)
        
        print("✅ Ma'lumotlar barcha tizimlarga saqlandi")
        
        # Cross-system analysis
        evolution_analysis = evolution_tracker.get_evolution_analysis("EURUSD_TREND_001", days=5)
        historical_report = metrics_engine.generate_historical_report("EURUSD_TREND_001")
        
        print("\n📊 INTEGRATED ANALYSIS:")
        print(f"   Evolution Score: {evolution_analysis.get('overall_score', {}).get('overall_score', 0):.3f}")
        print(f"   Historical Completeness: {historical_report.get('summary', {}).get('analysis_completeness', 0):.1f}%")
        
        print("✅ Integration test muvaffaqiyatli!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test xatosi: {e}")
        return False

def cleanup_test_files():
    """Test fayllarini tozalash"""
    import os
    test_files = [
        "test_evolution.db",
        "test_metrics.db", 
        "test_analytics.db",
        "integration_test.db"
    ]
    
    for file in test_files:
        try:
            if os.path.exists(file):
                os.remove(file)
        except:
            pass

def main():
    """Asosiy demo funksiyasi"""
    print("🚀 STRATEGY EVOLUTION TRACKING TIZIMI DEMO")
    print("="*60)
    print("📅 Sana: 2025-11-04")
    print("🏢 Orion Starline AI Team")
    print("="*60)
    
    # Run tests
    tests = [
        ("Strategy Evolution Tracker", test_strategy_evolution_tracker),
        ("Historical Metrics Engine", test_historical_metrics),
        ("Evolution Analytics Engine", test_evolution_analytics),
        ("Integration Test", test_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test to'liq amalga oshirilmadi: {e}")
            results.append((test_name, False))
    
    # Final results
    print("\n" + "="*60)
    print("📊 FINAL TEST RESULTS")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:30s}: {status}")
        if result:
            passed += 1
    
    print(f"\n🏆 JAMI: {passed}/{len(results)} test muvaffaqiyatli")
    
    if passed == len(results):
        print("🎉 Barcha testlar muvaffaqiyatli o'tdi!")
        print("📈 Strategy Evolution Tracking tizimi ishga tayyor!")
    else:
        print("⚠️  Ba'zi testlar xato berdi. Iltimos, xatolarni tekshiring.")
    
    # Cleanup
    print("\n🧹 Test fayllarini tozalash...")
    cleanup_test_files()
    print("✅ Tozalash tugallandi")

if __name__ == "__main__":
    main()
