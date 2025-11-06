"""
Forex NFT Hedge System - Monitoring va Analytics Tests
Monitoring va analytics tizimlari uchun testlar
"""

import asyncio
import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, List

from monitoring.real_time_monitor import (
    RealTimeMonitor, PerformanceCalculator, RiskMonitor, 
    PerformanceMetrics, RiskAlert
)
from monitoring.analytics_engine import (
    AnalyticsEngine, PerformanceAnalyzer, RiskAnalyzer, Dashboard
)
from optimization.performance_optimizer import (
    PerformanceOptimizer, LatencyOptimizer, MemoryOptimizer,
    QuantumOptimizer, AlgorithmOptimizer
)
from optimization.strategy_optimizer import (
    StrategyOptimizer, MarketRegimeDetector, PortfolioStrategyOptimizer
)
from config import HedgeType, ForexPair, QuantumStrategy
from core.forex_hedge_core import ForexHedgeManager, HedgePosition

class TestRealTimeMonitoring:
    """Real-time monitoring test klassi"""
    
    def __init__(self):
        self.hedge_manager = None
        self.monitor = None
    
    async def setup(self):
        """Test muhitini tayyorlash"""
        self.hedge_manager = ForexHedgeManager()
        self.monitor = RealTimeMonitor(self.hedge_manager)
    
    async def test_performance_calculator(self):
        """Performance calculator test"""
        print("🧪 Testing Performance Calculator...")
        
        calculator = PerformanceCalculator()
        
        # Create mock positions
        from core.forex_hedge_core import HedgePosition
        mock_positions = [
            HedgePosition(
                position_id="test1",
                nft_token_id="token1",
                pair=ForexPair.EURUSD,
                hedge_type=HedgeType.PAIR_HEDGE,
                notional_amount=100000,
                entry_price=1.0850,
                hedge_ratio=0.7,
                quantum_enhanced=True,
                performance_metrics={
                    "daily_return": 0.015,
                    "pnl": 1500.0,
                    "volatility": 0.12
                },
                created_at=int(datetime.now().timestamp()),
                last_rebalance=int(datetime.now().timestamp())
            ),
            HedgePosition(
                position_id="test2",
                nft_token_id="token2",
                pair=ForexPair.GBPUSD,
                hedge_type=HedgeType.VOLATILITY,
                notional_amount=80000,
                entry_price=1.2650,
                hedge_ratio=0.6,
                quantum_enhanced=False,
                performance_metrics={
                    "daily_return": -0.008,
                    "pnl": -640.0,
                    "volatility": 0.18
                },
                created_at=int(datetime.now().timestamp()),
                last_rebalance=int(datetime.now().timestamp())
            )
        ]
        
        # Test portfolio metrics calculation
        metrics = await calculator.calculate_portfolio_metrics(mock_positions)
        
        assert isinstance(metrics, PerformanceMetrics), "Should return PerformanceMetrics"
        assert metrics.timestamp > 0, "Should have valid timestamp"
        assert isinstance(metrics.total_pnl, float), "Total PnL should be numeric"
        assert isinstance(metrics.sharpe_ratio, float), "Sharpe ratio should be numeric"
        assert -1 <= metrics.max_drawdown <= 0, "Max drawdown should be negative"
        assert 0 <= metrics.hedge_effectiveness <= 1, "Hedge effectiveness should be between 0 and 1"
        
        print("✅ Performance Calculator tests passed")
        return True
    
    async def test_risk_monitor(self):
        """Risk monitor test"""
        print("🧪 Testing Risk Monitor...")
        
        risk_monitor = RiskMonitor()
        
        # Create mock positions
        mock_positions = [
            HedgePosition(
                position_id="test1",
                nft_token_id="token1",
                pair=ForexPair.EURUSD,
                hedge_type=HedgeType.PAIR_HEDGE,
                notional_amount=100000,
                entry_price=1.0850,
                hedge_ratio=0.7,
                quantum_enhanced=True,
                performance_metrics={"daily_return": 0.015, "pnl": 1500.0},
                created_at=int(datetime.now().timestamp()),
                last_rebalance=int(datetime.now().timestamp())
            ),
            HedgePosition(
                position_id="test2",
                nft_token_id="token2",
                pair=ForexPair.EURUSD,  # Same pair - concentration risk
                hedge_type=HedgeType.PAIR_HEDGE,
                notional_amount=90000,
                entry_price=1.0850,
                hedge_ratio=0.7,
                quantum_enhanced=True,
                performance_metrics={"daily_return": 0.015, "pnl": 1350.0},
                created_at=int(datetime.now().timestamp()),
                last_rebalance=int(datetime.now().timestamp())
            )
        ]
        
        # Mock performance metrics with high drawdown
        mock_performance = PerformanceMetrics(
            timestamp=int(datetime.now().timestamp()),
            total_pnl=2850.0,
            daily_return=0.015,
            cumulative_return=0.15,
            sharpe_ratio=1.2,
            sortino_ratio=1.0,
            calmar_ratio=1.5,
            max_drawdown=-0.30,  # High drawdown for testing
            var_95=-0.08,  # High VaR for testing
            var_99=-0.12,
            beta=1.1,
            alpha=0.02,
            information_ratio=0.8,
            volatility=0.15,
            hedge_effectiveness=0.75
        )
        
        # Test risk alerts
        alerts = await risk_monitor.check_risk_alerts(mock_positions, mock_performance)
        
        assert isinstance(alerts, list), "Should return list of alerts"
        
        # Should generate alerts for high drawdown and VaR
        alert_types = [alert.alert_type for alert in alerts]
        assert "DRAWDOWN" in alert_types, "Should generate drawdown alert"
        assert "VAR" in alert_types, "Should generate VaR alert"
        
        for alert in alerts:
            assert isinstance(alert, RiskAlert), "Should be RiskAlert instance"
            assert alert.alert_id, "Should have alert ID"
            assert alert.message, "Should have alert message"
            assert alert.current_value is not None, "Should have current value"
            assert alert.threshold_value is not None, "Should have threshold value"
        
        print("✅ Risk Monitor tests passed")
        return True
    
    async def test_real_time_monitor_lifecycle(self):
        """Real-time monitor lifecycle test"""
        print("🧪 Testing Real-Time Monitor Lifecycle...")
        
        # Test start/stop monitoring
        assert not self.monitor.monitoring_active, "Should not be active initially"
        
        # Start monitoring
        await self.monitor.start_monitoring()
        assert self.monitor.monitoring_active, "Should be active after start"
        
        # Let it run briefly
        await asyncio.sleep(0.1)
        
        # Test live metrics
        metrics = await self.monitor.get_live_metrics()
        assert isinstance(metrics, dict), "Should return metrics dict"
        assert "timestamp" in metrics, "Should have timestamp"
        
        # Stop monitoring
        await self.monitor.stop_monitoring()
        assert not self.monitor.monitoring_active, "Should not be active after stop"
        
        print("✅ Real-Time Monitor Lifecycle tests passed")
        return True
    
    async def test_monitoring_subscriptions(self):
        """Monitoring subscription test"""
        print("🧪 Testing Monitoring Subscriptions...")
        
        subscription_called = False
        received_data = None
        
        async def mock_subscriber(data):
            nonlocal subscription_called, received_data
            subscription_called = True
            received_data = data
        
        # Subscribe to updates
        self.monitor.subscribe_to_updates(mock_subscriber)
        
        # Start monitoring briefly
        await self.monitor.start_monitoring()
        await asyncio.sleep(0.05)  # Give time for updates
        
        # Check if subscriber was called
        assert subscription_called, "Subscriber should have been called"
        assert received_data, "Should have received data"
        assert "metrics" in received_data, "Should have metrics in data"
        
        # Test unsubscribe
        self.monitor.unsubscribe_from_updates(mock_subscriber)
        await self.monitor.stop_monitoring()
        
        print("✅ Monitoring Subscriptions tests passed")
        return True

class TestAnalyticsEngine:
    """Analytics engine test klassi"""
    
    def __init__(self):
        self.hedge_manager = None
        self.monitor = None
        self.analytics = None
    
    async def setup(self):
        """Test muhitini tayyorlash"""
        self.hedge_manager = ForexHedgeManager()
        self.monitor = RealTimeMonitor(self.hedge_manager)
        self.analytics = AnalyticsEngine(self.monitor)
    
    async def test_performance_analyzer(self):
        """Performance analyzer test"""
        print("🧪 Testing Performance Analyzer...")
        
        analyzer = PerformanceAnalyzer(self.monitor)
        
        # Test hedge performance analysis
        analysis = await analyzer.analyze_hedge_performance(1)  # 1 hour period
        
        assert isinstance(analysis, dict), "Should return analysis dict"
        assert "period_summary" in analysis, "Should have period summary"
        assert "position_analysis" in analysis, "Should have position analysis"
        assert "strategy_performance" in analysis, "Should have strategy performance"
        assert "quantum_analysis" in analysis, "Should have quantum analysis"
        
        # Check structure of each section
        period_summary = analysis["period_summary"]
        if period_summary:  # May be empty if no data
            assert "period_hours" in period_summary, "Should have period hours"
        
        print("✅ Performance Analyzer tests passed")
        return True
    
    async def test_risk_analyzer(self):
        """Risk analyzer test"""
        print("🧪 Testing Risk Analyzer...")
        
        analyzer = RiskAnalyzer(self.monitor)
        
        # Test risk exposure analysis
        analysis = await analyzer.analyze_risk_exposure(1)  # 1 hour period
        
        assert isinstance(analysis, dict), "Should return analysis dict"
        assert "risk_summary" in analysis, "Should have risk summary"
        assert "position_risks" in analysis, "Should have position risks"
        assert "correlation_risks" in analysis, "Should have correlation risks"
        assert "concentration_risks" in analysis, "Should have concentration risks"
        assert "recommendations" in analysis, "Should have recommendations"
        
        # Check risk summary structure
        risk_summary = analysis["risk_summary"]
        assert "status" in risk_summary, "Should have status"
        assert "total_alerts" in risk_summary, "Should have alert count"
        
        # Recommendations should be list
        recommendations = analysis["recommendations"]
        assert isinstance(recommendations, list), "Recommendations should be list"
        
        print("✅ Risk Analyzer tests passed")
        return True
    
    async def test_analytics_engine_integration(self):
        """Analytics engine integration test"""
        print("🧪 Testing Analytics Engine Integration...")
        
        # Test comprehensive report generation
        report = await self.analytics.generate_comprehensive_report(1)
        
        assert report.report_id, "Should have report ID"
        assert report.timestamp > 0, "Should have timestamp"
        assert report.report_type == "comprehensive", "Should be comprehensive report"
        assert report.data, "Should have data"
        assert report.summary, "Should have summary"
        assert isinstance(report.insights, list), "Should have insights list"
        assert isinstance(report.recommendations, list), "Should have recommendations list"
        
        # Test report export
        exported_data = await self.analytics.export_report(report)
        assert isinstance(exported_data, str), "Export should return string"
        assert len(exported_data) > 0, "Export should not be empty"
        
        print("✅ Analytics Engine Integration tests passed")
        return True
    
    async def test_dashboard(self):
        """Dashboard test"""
        print("🧪 Testing Dashboard...")
        
        dashboard = Dashboard(self.analytics)
        
        # Test dashboard data
        dashboard_data = await dashboard.get_dashboard_data()
        
        assert isinstance(dashboard_data, dict), "Should return dashboard data"
        assert "live_metrics" in dashboard_data, "Should have live metrics"
        assert "recent_report" in dashboard_data, "Should have recent report"
        assert "risk_status" in dashboard_data, "Should have risk status"
        assert "system_status" in dashboard_data, "Should have system status"
        assert "last_updated" in dashboard_data, "Should have last updated timestamp"
        
        print("✅ Dashboard tests passed")
        return True

class TestOptimizationEngine:
    """Optimization engine test klassi"""
    
    def __init__(self):
        self.hedge_manager = None
        self.performance_optimizer = None
        self.strategy_optimizer = None
    
    async def setup(self):
        """Test muhitini tayyorlash"""
        self.hedge_manager = ForexHedgeManager()
        self.performance_optimizer = PerformanceOptimizer()
        self.strategy_optimizer = StrategyOptimizer(self.hedge_manager)
    
    async def test_performance_optimizer(self):
        """Performance optimizer test"""
        print("🧪 Testing Performance Optimizer...")
        
        # Test comprehensive optimization
        results = await self.performance_optimizer.run_comprehensive_optimization()
        
        assert isinstance(results, dict), "Should return optimization results"
        assert "baseline_metrics" in results, "Should have baseline metrics"
        assert "latency_optimizations" in results, "Should have latency optimizations"
        assert "memory_optimizations" in results, "Should have memory optimizations"
        assert "quantum_optimizations" in results, "Should have quantum optimizations"
        assert "algorithm_optimizations" in results, "Should have algorithm optimizations"
        assert "total_improvements" in results, "Should have total improvements"
        
        # Check improvements structure
        improvements = results["total_improvements"]
        assert "latency_improvement_percentage" in improvements, "Should have latency improvement"
        assert "memory_savings_mb" in improvements, "Should have memory savings"
        assert "overall_speedup_factor" in improvements, "Should have speedup factor"
        
        print("✅ Performance Optimizer tests passed")
        return True
    
    async def test_latency_optimizer(self):
        """Latency optimizer test"""
        print("🧪 Testing Latency Optimizer...")
        
        optimizer = LatencyOptimizer()
        
        # Test bottleneck analysis
        bottlenecks = await optimizer.analyze_latency_bottlenecks()
        
        assert isinstance(bottlenecks, dict), "Should return bottlenecks dict"
        assert "bottlenecks" in bottlenecks, "Should have bottlenecks dict"
        assert "critical_bottlenecks" in bottlenecks, "Should have critical bottlenecks"
        assert "optimization_potential" in bottlenecks, "Should have optimization potential"
        
        # Apply optimizations
        optimizations = await optimizer.apply_latency_optimizations()
        
        assert isinstance(optimizations, dict), "Should return optimizations dict"
        assert "optimizations_applied" in optimizations, "Should have applied optimizations"
        assert "estimated_improvement" in optimizations, "Should have estimated improvement"
        
        print("✅ Latency Optimizer tests passed")
        return True
    
    async def test_memory_optimizer(self):
        """Memory optimizer test"""
        print("🧪 Testing Memory Optimizer...")
        
        optimizer = MemoryOptimizer()
        
        # Test memory analysis
        analysis = await optimizer.analyze_memory_usage()
        
        assert isinstance(analysis, dict), "Should return analysis dict"
        assert "system_memory" in analysis, "Should have system memory info"
        assert "process_memory" in analysis, "Should have process memory info"
        assert "memory_leaks" in analysis, "Should have memory leak info"
        assert "garbage_collection" in analysis, "Should have GC info"
        
        # Test optimization
        optimizations = await optimizer.optimize_memory_usage()
        
        assert isinstance(optimizations, dict), "Should return optimizations dict"
        assert "optimizations_applied" in optimizations, "Should have applied optimizations"
        assert "estimated_memory_savings" in optimizations, "Should have memory savings estimate"
        
        print("✅ Memory Optimizer tests passed")
        return True
    
    async def test_strategy_optimizer(self):
        """Strategy optimizer test"""
        print("🧪 Testing Strategy Optimizer...")
        
        # Test all strategies optimization
        results = await self.strategy_optimizer.optimize_all_strategies()
        
        assert isinstance(results, dict), "Should return results dict"
        assert "market_regime" in results, "Should have market regime"
        assert "strategy_optimizations" in results, "Should have strategy optimizations"
        assert "recommendations" in results, "Should have recommendations"
        
        # Test market regime detection
        regime_detector = MarketRegimeDetector()
        regime = await regime_detector.detect_current_regime()
        
        assert isinstance(regime, dict), "Should return regime dict"
        assert "regime" in regime, "Should have regime type"
        assert "trend_strength" in regime, "Should have trend strength"
        assert "volatility_level" in regime, "Should have volatility level"
        assert "recommended_strategies" in regime, "Should have recommended strategies"
        
        print("✅ Strategy Optimizer tests passed")
        return True
    
    async def test_portfolio_optimizer(self):
        """Portfolio optimizer test"""
        print("🧪 Testing Portfolio Optimizer...")
        
        portfolio_optimizer = PortfolioStrategyOptimizer(self.strategy_optimizer)
        
        # Test portfolio allocation optimization
        allocation_results = await portfolio_optimizer.optimize_portfolio_allocation(0.15)
        
        assert isinstance(allocation_results, dict), "Should return allocation results"
        assert "optimal_allocation" in allocation_results, "Should have optimal allocation"
        assert "diversification_analysis" in allocation_results, "Should have diversification analysis"
        assert "quantum_recommendation" in allocation_results, "Should have quantum recommendation"
        assert "portfolio_metrics" in allocation_results, "Should have portfolio metrics"
        
        # Test strategy comparison
        comparison = await self.strategy_optimizer.get_strategy_comparison()
        
        assert isinstance(comparison, dict), "Should return comparison dict"
        if comparison.get("status") != "no_performance_data":
            assert "best_return" in comparison, "Should have best return strategy"
            assert "best_sharpe" in comparison, "Should have best Sharpe strategy"
            assert "best_risk" in comparison, "Should have best risk strategy"
        
        print("✅ Portfolio Optimizer tests passed")
        return True

class TestMonitoringAndOptimizationIntegration:
    """Monitoring va Optimization integration test klassi"""
    
    async def test_end_to_end_workflow(self):
        """End-to-end workflow test"""
        print("🧪 Testing End-to-End Monitoring & Optimization Workflow...")
        
        # Setup
        hedge_manager = ForexHedgeManager()
        monitor = RealTimeMonitor(hedge_manager)
        analytics = AnalyticsEngine(monitor)
        performance_optimizer = PerformanceOptimizer()
        strategy_optimizer = StrategyOptimizer(hedge_manager)
        
        # 1. Start monitoring
        await monitor.start_monitoring()
        
        # 2. Create some positions for testing
        metadata, position = await hedge_manager.create_hedge_strategy(
            hedge_type=HedgeType.PAIR_HEDGE,
            pair=ForexPair.EURUSD,
            notional_amount=100000,
            quantum_enhanced=True
        )
        
        # 3. Wait for some monitoring data
        await asyncio.sleep(0.1)
        
        # 4. Generate analytics
        report = await analytics.generate_comprehensive_report(1)
        assert report, "Should generate report"
        
        # 5. Run performance optimization
        optimization_results = await performance_optimizer.run_comprehensive_optimization()
        assert optimization_results, "Should complete optimization"
        
        # 6. Run strategy optimization
        strategy_results = await strategy_optimizer.optimize_all_strategies()
        assert strategy_results, "Should complete strategy optimization"
        
        # 7. Get dashboard data
        dashboard_data = await analytics.dashboard.get_dashboard_data()
        assert dashboard_data, "Should get dashboard data"
        
        # 8. Export data
        exported_data = await monitor.export_data()
        assert exported_data, "Should export data"
        
        # 9. Stop monitoring
        await monitor.stop_monitoring()
        
        print("✅ End-to-End Workflow tests passed")
        return True
    
    async def test_real_time_integration(self):
        """Real-time integration test"""
        print("🧪 Testing Real-Time Integration...")
        
        hedge_manager = ForexHedgeManager()
        monitor = RealTimeMonitor(hedge_manager)
        
        # Track real-time updates
        update_count = 0
        latest_metrics = None
        
        async def track_updates(data):
            nonlocal update_count, latest_metrics
            update_count += 1
            latest_metrics = data
        
        # Subscribe to updates
        monitor.subscribe_to_updates(track_updates)
        
        # Start monitoring
        await monitor.start_monitoring()
        
        # Wait for updates
        await asyncio.sleep(0.2)
        
        # Check that updates were received
        assert update_count > 0, "Should have received updates"
        assert latest_metrics, "Should have latest metrics"
        
        # Get analytics during monitoring
        analytics = AnalyticsEngine(monitor)
        live_metrics = await monitor.get_live_metrics()
        assert live_metrics, "Should get live metrics during monitoring"
        
        # Stop monitoring
        await monitor.stop_monitoring()
        
        print("✅ Real-Time Integration tests passed")
        return True

# Test Runner
async def run_monitoring_optimization_tests():
    """Monitoring va optimization testlarini ishga tushirish"""
    
    print("🔬 FOREX NFT HEDGE - MONITORING & OPTIMIZATION TESTS")
    print("=" * 65)
    
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "test_categories": {},
        "summary": {}
    }
    
    # Test categories
    test_categories = [
        ("Real-Time Monitoring", TestRealTimeMonitoring),
        ("Analytics Engine", TestAnalyticsEngine),
        ("Optimization Engine", TestOptimizationEngine),
        ("Integration Tests", TestMonitoringAndOptimizationIntegration)
    ]
    
    total_passed = 0
    total_tests = 0
    
    for category_name, test_class in test_categories:
        print(f"\n🔬 {category_name.upper()} TESTS")
        print("-" * 50)
        
        category_results = {
            "tests": {},
            "passed": 0,
            "failed": 0
        }
        
        test_instance = test_class()
        
        try:
            # Setup
            await test_instance.setup()
            
            # Get test methods
            test_methods = [
                method for method in dir(test_instance) 
                if method.startswith('test_') and callable(getattr(test_instance, method))
            ]
            
            for test_method_name in test_methods:
                test_method = getattr(test_instance, test_method_name)
                test_name = test_method_name.replace('test_', '').replace('_', ' ').title()
                
                try:
                    print(f"🧪 Running {test_name}...")
                    result = await test_method()
                    if result:
                        category_results["tests"][test_name] = {"status": "PASSED"}
                        category_results["passed"] += 1
                        total_passed += 1
                        print(f"✅ {test_name} PASSED")
                    else:
                        category_results["tests"][test_name] = {"status": "FAILED"}
                        category_results["failed"] += 1
                        print(f"❌ {test_name} FAILED")
                except Exception as e:
                    category_results["tests"][test_name] = {"status": "FAILED", "error": str(e)}
                    category_results["failed"] += 1
                    print(f"❌ {test_name} FAILED: {e}")
                
                total_tests += 1
            
        except Exception as e:
            print(f"❌ {category_name} setup failed: {e}")
            category_results["error"] = str(e)
        
        test_results["test_categories"][category_name] = category_results
        
        print(f"📊 {category_name}: {category_results['passed']}/{category_results['passed'] + category_results['failed']} tests passed")
    
    # Summary
    test_results["summary"] = {
        "total_tests": total_tests,
        "total_passed": total_passed,
        "total_failed": total_tests - total_passed,
        "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
        "overall_status": "PASSED" if total_passed == total_tests else "FAILED"
    }
    
    # Display summary
    print("\n" + "=" * 65)
    print("📊 MONITORING & OPTIMIZATION TEST SUMMARY")
    print("=" * 65)
    print(f"📋 Total Tests: {total_tests}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_tests - total_passed}")
    print(f"📈 Success Rate: {test_results['summary']['success_rate']:.1f}%")
    print(f"🎯 Overall Status: {test_results['summary']['overall_status']}")
    
    # Save results
    with open('/workspace/code/forex_nft_hedges/tests/monitoring_optimization_results.json', 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: tests/monitoring_optimization_results.json")
    
    return test_results

if __name__ == "__main__":
    asyncio.run(run_monitoring_optimization_tests())
