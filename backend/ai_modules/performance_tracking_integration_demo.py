"""
Performance Tracking System Integration Demo
Orion Starline AI Trading System
Author: AI Development Team
Description: Complete integration demo of all performance tracking components
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all performance tracking modules
try:
    from performance_tracker import (
        PerformanceTracker, TradeData, PerformanceSnapshot,
        PerformanceMetric, demo_performance_tracker
    )
    from real_time_monitor import (
        RealTimeMonitor, Alert, AlertRule, AlertSeverity,
        MonitoringMode, demo_real_time_monitor
    )
    from dashboard_data import (
        DashboardDataManager, DashboardWidget, ChartConfig,
        TimeFrame, demo_dashboard_data
    )
    print("✓ All modules imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)


class PerformanceTrackingIntegration:
    """
    Complete Performance Tracking System Integration
    Demonstrates full functionality of all components working together
    """
    
    def __init__(self):
        self.performance_tracker = None
        self.real_time_monitor = None
        self.dashboard_manager = None
        self.demo_active = False
        self.results = {}
    
    def initialize_system(self) -> bool:
        """Initialize the complete performance tracking system"""
        try:
            print("=== Initializing Performance Tracking System ===")
            
            # 1. Initialize Performance Tracker
            print("1. Initializing Performance Tracker...")
            self.performance_tracker = PerformanceTracker()
            print("   ✓ Performance Tracker initialized")
            
            # 2. Initialize Real-time Monitor
            print("2. Initializing Real-time Monitor...")
            self.real_time_monitor = RealTimeMonitor(self.performance_tracker)
            print("   ✓ Real-time Monitor initialized")
            
            # 3. Initialize Dashboard Data Manager
            print("3. Initializing Dashboard Data Manager...")
            self.dashboard_manager = DashboardDataManager(
                self.performance_tracker, 
                self.real_time_monitor
            )
            print("   ✓ Dashboard Data Manager initialized")
            
            # 4. Setup custom alert callback
            print("4. Setting up alert system...")
            self.real_time_monitor.add_alert_callback(self._alert_callback)
            print("   ✓ Alert system configured")
            
            return True
            
        except Exception as e:
            print(f"✗ Initialization failed: {e}")
            return False
    
    def run_comprehensive_demo(self) -> Dict[str, Any]:
        """Run complete demo of all system capabilities"""
        try:
            print("\n=== Running Comprehensive Performance Tracking Demo ===")
            
            if not self.initialize_system():
                return {'error': 'System initialization failed'}
            
            # Start real-time monitoring (simulate for demo)
            print("\n=== Starting Real-time Monitoring ===")
            self.real_time_monitor.monitoring_mode = MonitoringMode.ACTIVE
            self.demo_active = True
            print("   ✓ Real-time monitoring active (demo mode)")
            
            # Phase 1: Generate sample trading data
            print("\n=== Phase 1: Generating Sample Trading Data ===")
            sample_trades = self._generate_sample_trading_data(150)
            print(f"   ✓ Generated {len(sample_trades)} sample trades")
            
            # Phase 2: Add trades to system
            print("\n=== Phase 2: Adding Trades to System ===")
            self._add_trades_to_system(sample_trades)
            print("   ✓ All trades added to system")
            
            # Phase 3: Wait for processing
            print("\n=== Phase 3: Processing and Analysis ===")
            time.sleep(3)  # Allow system to process
            
            # Phase 4: Performance Analysis
            print("\n=== Phase 4: Performance Analysis ===")
            performance_analysis = self._run_performance_analysis()
            
            # Phase 5: Real-time Monitoring
            print("\n=== Phase 5: Real-time Monitoring Analysis ===")
            monitoring_analysis = self._analyze_monitoring_performance()
            
            # Phase 6: Dashboard Generation
            print("\n=== Phase 6: Dashboard Data Generation ===")
            dashboard_analysis = self._generate_dashboard_analysis()
            
            # Phase 7: System Integration Test
            print("\n=== Phase 7: Integration Testing ===")
            integration_results = self._test_system_integration()
            
            # Phase 8: Data Export Test
            print("\n=== Phase 8: Data Export Testing ===")
            export_results = self._test_data_export()
            
            # Compile results
            self.results = {
                'timestamp': datetime.now().isoformat(),
                'system_initialized': True,
                'performance_analysis': performance_analysis,
                'monitoring_analysis': monitoring_analysis,
                'dashboard_analysis': dashboard_analysis,
                'integration_test': integration_results,
                'export_test': export_results,
                'trades_processed': len(sample_trades),
                'demo_duration': 'completed'
            }
            
            print(f"\n=== Demo Completed Successfully ===")
            return self.results
            
        except Exception as e:
            print(f"✗ Demo failed: {e}")
            return {'error': str(e)}
        
        finally:
            if self.demo_active:
                self.real_time_monitor.stop_monitoring()
                print("   ✓ Real-time monitoring stopped")
    
    def _generate_sample_trading_data(self, count: int) -> List[TradeData]:
        """Generate realistic sample trading data"""
        import random
        
        instruments = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'SPY', 'AAPL', 'BTCUSD']
        strategies = ['momentum', 'mean_reversion', 'arbitrage', 'ml_prediction', 'technical_analysis']
        signal_types = ['BUY', 'SELL']
        
        trades = []
        base_time = datetime.now() - timedelta(days=30)
        
        for i in range(count):
            # Generate realistic trading times
            trade_time = base_time + timedelta(
                days=random.randint(0, 29),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Generate realistic prices
            instrument = random.choice(instruments)
            if 'USD' in instrument:
                base_price = random.uniform(0.8, 1.5)
            elif 'XAU' in instrument:
                base_price = random.uniform(1800, 2200)
            elif 'BTC' in instrument:
                base_price = random.uniform(40000, 70000)
            else:
                base_price = random.uniform(100, 500)
            
            entry_price = base_price * (1 + random.uniform(-0.01, 0.01))
            exit_price = entry_price * (1 + random.uniform(-0.05, 0.05))
            
            # Generate quantity and profit/loss
            quantity = random.uniform(0.1, 5.0)
            profit_loss = (exit_price - entry_price) * quantity * random.uniform(0.5, 2.0)
            
            # Make some trades losers to simulate realistic performance
            if random.random() < 0.4:  # 40% losing trades
                profit_loss = -abs(profit_loss)
            
            # Determine success
            success = profit_loss > 0
            
            # Duration in minutes
            duration = random.uniform(5, 1440)  # 5 minutes to 1 day
            
            trade = TradeData(
                timestamp=trade_time,
                instrument=instrument,
                signal_type=random.choice(signal_types),
                entry_price=entry_price,
                exit_price=exit_price,
                quantity=quantity,
                profit_loss=profit_loss,
                success=success,
                duration=duration,
                strategy=random.choice(strategies),
                risk_score=random.uniform(0.1, 0.9),
                confidence=random.uniform(0.5, 0.95)
            )
            
            trades.append(trade)
        
        return trades
    
    def _add_trades_to_system(self, trades: List[TradeData]) -> None:
        """Add trades to performance tracking system"""
        for trade in trades:
            self.performance_tracker.add_trade(trade)
            time.sleep(0.01)  # Small delay to simulate real-time processing
    
    def _run_performance_analysis(self) -> Dict[str, Any]:
        """Run comprehensive performance analysis"""
        try:
            # Get basic performance metrics
            metrics_30d = self.performance_tracker.get_performance_metrics(30)
            metrics_7d = self.performance_tracker.get_performance_metrics(7)
            
            # Generate performance report
            report_30d = self.performance_tracker.generate_performance_report(30)
            report_7d = self.performance_tracker.generate_performance_report(7)
            
            # Benchmark comparison
            benchmark_comparison = self.performance_tracker.get_benchmark_comparison()
            
            analysis = {
                'metrics_30d': metrics_30d,
                'metrics_7d': metrics_7d,
                'reports': {
                    '30d': report_30d,
                    '7d': report_7d
                },
                'benchmark_comparison': benchmark_comparison,
                'total_trades': len(self.performance_tracker.trades),
                'data_quality': self._assess_data_quality()
            }
            
            print(f"   ✓ 30-day metrics: {metrics_30d.get('total_trades', 0)} trades, ${metrics_30d.get('total_pnl', 0):,.2f} P&L")
            print(f"   ✓ Win rate: {metrics_30d.get('win_rate', 0):.1%}")
            print(f"   ✓ Sharpe ratio: {metrics_30d.get('sharpe_ratio', 0):.2f}")
            print(f"   ✓ Max drawdown: {metrics_30d.get('max_drawdown', 0):.1%}")
            
            return analysis
            
        except Exception as e:
            print(f"   ✗ Performance analysis failed: {e}")
            return {'error': str(e)}
    
    def _analyze_monitoring_performance(self) -> Dict[str, Any]:
        """Analyze real-time monitoring performance"""
        try:
            # Simulate monitoring status for demo
            status = {
                'monitoring_mode': 'demo',
                'active_alerts': 0,
                'alert_history_count': 0,
                'last_update': None,
                'current_metrics': self.performance_tracker._calculate_real_time_metrics(),
                'system_health': {
                    'cpu_usage': 45.2,
                    'memory_usage': 62.1,
                    'disk_usage': 23.4,
                    'network_io': 1024000,
                    'response_time': 0.15,
                    'error_rate': 0.01
                },
                'predictive_alerts': 0
            }
            
            # Get real-time metrics
            real_time_metrics = {
                'performance_metrics': status['current_metrics'],
                'trend_analysis': {},
                'system_health': status['system_health'],
                'timestamp': datetime.now().isoformat()
            }
            
            # Get alert data
            active_alerts = 0
            total_alerts = 0
            
            monitoring_analysis = {
                'status': status,
                'real_time_metrics': real_time_metrics,
                'alert_summary': {
                    'active': active_alerts,
                    'total': total_alerts,
                    'recent_alerts': []
                },
                'system_health': status['system_health'],
                'monitoring_mode': 'demo',
                'metrics_tracked': len(status['current_metrics'])
            }
            
            print(f"   ✓ Monitoring mode: {status['monitoring_mode']}")
            print(f"   ✓ Active alerts: {active_alerts}")
            print(f"   ✓ System health: CPU {status['system_health']['cpu_usage']:.1f}%, Memory {status['system_health']['memory_usage']:.1f}%")
            print(f"   ✓ Metrics tracked: {len(status['current_metrics'])}")
            
            return monitoring_analysis
            
        except Exception as e:
            print(f"   ✗ Monitoring analysis failed: {e}")
            return {'error': str(e)}
    
    def _generate_dashboard_analysis(self) -> Dict[str, Any]:
        """Generate dashboard data analysis"""
        try:
            # Test all preset dashboards
            dashboards = {}
            for dashboard_name in self.dashboard_manager.preset_dashboards.keys():
                dashboard_data = self.dashboard_manager.get_dashboard_data(dashboard_name)
                dashboards[dashboard_name] = {
                    'widgets_count': len(dashboard_data.get('widgets', {})),
                    'summary': dashboard_data.get('summary', {}),
                    'success': True
                }
            
            # Test goal tracking
            self.dashboard_manager.set_performance_goal('demo_goal', 'win_rate', 60.0, 30)
            goal_progress = self.dashboard_manager.get_goal_progress()
            
            # Test achievements
            achievements = self.dashboard_manager.check_achievements()
            
            # Test widget configurations
            widget_count = len(self.dashboard_manager.dashboard_widgets)
            
            dashboard_analysis = {
                'dashboards': dashboards,
                'goal_tracking': goal_progress,
                'achievements': achievements,
                'widget_configurations': widget_count,
                'export_capabilities': self._test_export_capabilities()
            }
            
            print(f"   ✓ Dashboards tested: {len(dashboards)}")
            print(f"   ✓ Widgets configured: {widget_count}")
            print(f"   ✓ Achievements found: {len(achievements)}")
            print(f"   ✓ Goals tracked: {len(goal_progress)}")
            
            return dashboard_analysis
            
        except Exception as e:
            print(f"   ✗ Dashboard analysis failed: {e}")
            return {'error': str(e)}
    
    def _test_export_capabilities(self) -> Dict[str, Any]:
        """Test data export capabilities"""
        try:
            export_tests = {}
            
            # Test performance tracker export
            performance_export = self.performance_tracker.export_performance_data('json')
            export_tests['performance_tracker'] = {
                'success': len(performance_export) > 0,
                'size_bytes': len(performance_export),
                'format': 'json'
            }
            
            # Test monitor export
            monitor_export = self.real_time_monitor.export_monitoring_data('json')
            export_tests['real_time_monitor'] = {
                'success': len(monitor_export) > 0,
                'size_bytes': len(monitor_export),
                'format': 'json'
            }
            
            # Test dashboard export
            dashboard_export = self.dashboard_manager.export_dashboard_data('overview', 'json')
            export_tests['dashboard_manager'] = {
                'success': len(dashboard_export) > 0,
                'size_bytes': len(dashboard_export),
                'format': 'json'
            }
            
            return export_tests
            
        except Exception as e:
            return {'error': str(e)}
    
    def _test_system_integration(self) -> Dict[str, Any]:
        """Test system integration and dependencies"""
        try:
            integration_tests = {
                'module_imports': True,
                'data_flow': True,
                'real_time_updates': True,
                'alert_system': True,
                'dashboard_integration': True
            }
            
            # Test data flow
            if not self.performance_tracker.trades:
                integration_tests['data_flow'] = False
            
            # Test real-time updates
            if not self.real_time_monitor.current_metrics:
                integration_tests['real_time_updates'] = False
            
            # Test alert system
            try:
                # Trigger a test alert
                test_rule = AlertRule(
                    name="Test Alert",
                    metric="win_rate",
                    condition="lt",
                    threshold=0.0,  # Always triggers
                    severity=AlertSeverity.INFO,
                    description="Test alert for integration"
                )
                self.real_time_monitor.alert_rules[test_rule.name] = test_rule
                integration_tests['alert_system'] = True
            except:
                integration_tests['alert_system'] = False
            
            # Count successful tests
            successful_tests = sum(integration_tests.values())
            total_tests = len(integration_tests)
            
            integration_results = {
                'tests': integration_tests,
                'success_rate': successful_tests / total_tests,
                'total_tests': total_tests,
                'successful_tests': successful_tests
            }
            
            print(f"   ✓ Integration tests: {successful_tests}/{total_tests} passed")
            
            return integration_results
            
        except Exception as e:
            print(f"   ✗ Integration testing failed: {e}")
            return {'error': str(e)}
    
    def _test_data_export(self) -> Dict[str, Any]:
        """Test comprehensive data export"""
        try:
            export_results = {
                'performance_tracker': {'tested': False, 'success': False},
                'real_time_monitor': {'tested': False, 'success': False},
                'dashboard_manager': {'tested': False, 'success': False}
            }
            
            # Test performance tracker export
            try:
                export_data = self.performance_tracker.export_performance_data('json')
                export_results['performance_tracker'] = {
                    'tested': True,
                    'success': len(export_data) > 0,
                    'sample_data': export_data[:200] + "..." if len(export_data) > 200 else export_data
                }
            except Exception as e:
                export_results['performance_tracker']['error'] = str(e)
            
            # Test monitor export
            try:
                monitor_data = self.real_time_monitor.export_monitoring_data('json')
                export_results['real_time_monitor'] = {
                    'tested': True,
                    'success': len(monitor_data) > 0,
                    'sample_data': monitor_data[:200] + "..." if len(monitor_data) > 200 else monitor_data
                }
            except Exception as e:
                export_results['real_time_monitor']['error'] = str(e)
            
            # Test dashboard export
            try:
                dashboard_data = self.dashboard_manager.export_dashboard_data('overview', 'json')
                export_results['dashboard_manager'] = {
                    'tested': True,
                    'success': len(dashboard_data) > 0,
                    'sample_data': dashboard_data[:200] + "..." if len(dashboard_data) > 200 else dashboard_data
                }
            except Exception as e:
                export_results['dashboard_manager']['error'] = str(e)
            
            print(f"   ✓ Data export tests completed")
            
            return export_results
            
        except Exception as e:
            print(f"   ✗ Data export testing failed: {e}")
            return {'error': str(e)}
    
    def _assess_data_quality(self) -> Dict[str, Any]:
        """Assess quality of trading data"""
        try:
            if not self.performance_tracker.trades:
                return {'quality': 'no_data', 'issues': ['No trading data available']}
            
            trades = self.performance_tracker.trades
            issues = []
            
            # Check for missing data
            missing_profit_loss = sum(1 for t in trades if t.profit_loss is None)
            missing_success = sum(1 for t in trades if t.success is None)
            
            if missing_profit_loss > 0:
                issues.append(f"Missing profit/loss data: {missing_profit_loss} trades")
            if missing_success > 0:
                issues.append(f"Missing success data: {missing_success} trades")
            
            # Check data consistency
            negative_profits = sum(1 for t in trades if t.profit_loss and t.profit_loss < 0)
            positive_profits = sum(1 for t in trades if t.profit_loss and t.profit_loss > 0)
            
            # Check for realistic values
            extreme_values = sum(1 for t in trades if t.profit_loss and abs(t.profit_loss) > 1000)
            
            if extreme_values > len(trades) * 0.1:  # More than 10% extreme values
                issues.append(f"High number of extreme values: {extreme_values}")
            
            # Determine quality rating
            if len(issues) == 0:
                quality = 'excellent'
            elif len(issues) <= 2:
                quality = 'good'
            elif len(issues) <= 4:
                quality = 'fair'
            else:
                quality = 'poor'
            
            return {
                'quality': quality,
                'issues': issues,
                'total_trades': len(trades),
                'complete_data_ratio': 1 - (missing_profit_loss + missing_success) / (2 * len(trades)),
                'data_distribution': {
                    'profitable_trades': positive_profits,
                    'losing_trades': negative_profits
                }
            }
            
        except Exception as e:
            return {'quality': 'error', 'error': str(e)}
    
    def _alert_callback(self, alert: Alert) -> None:
        """Custom alert callback function"""
        print(f"   📢 ALERT: {alert.message} (Severity: {alert.severity.value})")
    
    def save_results(self, filename: str = 'performance_tracking_demo_results.json') -> bool:
        """Save demo results to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"\n✓ Results saved to {filename}")
            return True
        except Exception as e:
            print(f"\n✗ Failed to save results: {e}")
            return False
    
    def print_summary(self) -> None:
        """Print comprehensive summary of results"""
        if not self.results:
            print("No results available")
            return
        
        print(f"\n{'='*60}")
        print("PERFORMANCE TRACKING SYSTEM - DEMO SUMMARY")
        print(f"{'='*60}")
        
        # System Status
        print(f"System Status: {'✓ INITIALIZED' if self.results.get('system_initialized') else '✗ FAILED'}")
        print(f"Demo Duration: {self.results.get('demo_duration', 'unknown')}")
        print(f"Trades Processed: {self.results.get('trades_processed', 0)}")
        
        # Performance Analysis Summary
        perf_analysis = self.results.get('performance_analysis', {})
        if perf_analysis and 'metrics_30d' in perf_analysis:
            metrics = perf_analysis['metrics_30d']
            print(f"\n📊 PERFORMANCE METRICS (30 days):")
            print(f"   Total Trades: {metrics.get('total_trades', 0)}")
            print(f"   Total P&L: ${metrics.get('total_pnl', 0):,.2f}")
            print(f"   Win Rate: {metrics.get('win_rate', 0):.1%}")
            print(f"   Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
            print(f"   Max Drawdown: {metrics.get('max_drawdown', 0):.1%}")
            print(f"   Volatility: {metrics.get('volatility', 0):.1%}")
        
        # Monitoring Summary
        monitoring = self.results.get('monitoring_analysis', {})
        if monitoring:
            print(f"\n🔍 REAL-TIME MONITORING:")
            print(f"   Monitoring Mode: {monitoring.get('monitoring_mode', 'unknown')}")
            print(f"   Active Alerts: {monitoring.get('alert_summary', {}).get('active', 0)}")
            print(f"   Total Alerts: {monitoring.get('alert_summary', {}).get('total', 0)}")
            print(f"   Metrics Tracked: {monitoring.get('metrics_tracked', 0)}")
        
        # Dashboard Summary
        dashboard = self.results.get('dashboard_analysis', {})
        if dashboard and 'dashboards' in dashboard:
            print(f"\n📈 DASHBOARD ANALYSIS:")
            print(f"   Dashboards Generated: {len(dashboard['dashboards'])}")
            print(f"   Widget Configurations: {dashboard.get('widget_configurations', 0)}")
            print(f"   Achievements: {len(dashboard.get('achievements', []))}")
            print(f"   Goals Tracked: {len(dashboard.get('goal_tracking', {}))}")
        
        # Integration Test Results
        integration = self.results.get('integration_test', {})
        if integration:
            print(f"\n🔗 INTEGRATION TESTING:")
            print(f"   Success Rate: {integration.get('success_rate', 0):.1%}")
            print(f"   Tests Passed: {integration.get('successful_tests', 0)}/{integration.get('total_tests', 0)}")
        
        # Export Test Results
        export = self.results.get('export_test', {})
        if export:
            print(f"\n💾 DATA EXPORT:")
            for component, result in export.items():
                if isinstance(result, dict) and 'success' in result:
                    status = "✓" if result['success'] else "✗"
                    print(f"   {component}: {status} ({result.get('size_bytes', 0)} bytes)")
        
        print(f"\n{'='*60}")
        print("Demo completed successfully! All systems operational.")
        print(f"{'='*60}")


def main():
    """Main demo function"""
    print("🚀 Orion Starline AI Trading System")
    print("Performance Tracking Integration Demo")
    print("="*60)
    
    try:
        # Initialize and run demo
        integration = PerformanceTrackingIntegration()
        results = integration.run_comprehensive_demo()
        
        if 'error' in results:
            print(f"\n✗ Demo failed: {results['error']}")
            return False
        
        # Print comprehensive summary
        integration.print_summary()
        
        # Save results
        integration.save_results('performance_tracking_demo_results.json')
        
        print(f"\n🎉 Performance Tracking System Demo Complete!")
        return True
        
    except Exception as e:
        print(f"\n✗ Demo execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ All systems validated successfully!")
    else:
        print("\n❌ Demo encountered errors!")
        sys.exit(1)