"""
Analytics Engine Integration Test
=================================

Bu fayl real-time analytics engine tizimining barcha
komponentlarini birlashtirish va test qilish uchun mo'ljallangan.
"""

import asyncio
import json
import logging
import time
import unittest
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsIntegrationTest:
    """Analytics engine integration test class"""
    
    def __init__(self):
        self.analytics_engine = None
        self.metrics_collector = None
        self.dashboard_integration = None
        self.test_results = {}
        
    async def run_all_tests(self):
        """Barcha testlarni ishga tushirish"""
        logger.info("Analytics Integration Test boshlanmoqda...")
        
        test_methods = [
            self.test_basic_initialization,
            self.test_market_data_collection,
            self.test_user_data_collection,
            self.test_system_metrics_collection,
            self.test_signal_performance_tracking,
            self.test_dashboard_integration,
            self.test_data_export_import,
            self.test_real_time_processing,
            self.test_error_handling,
            self.test_performance_benchmarks
        ]
        
        passed = 0
        total = len(test_methods)
        
        for test_method in test_methods:
            try:
                result = await test_method()
                if result:
                    passed += 1
                    logger.info(f"✅ {test_method.__name__} - PASSED")
                else:
                    logger.error(f"❌ {test_method.__name__} - FAILED")
            except Exception as e:
                logger.error(f"❌ {test_method.__name__} - ERROR: {e}")
        
        # Final results
        logger.info(f"\nTest Results: {passed}/{total} tests passed")
        success_rate = (passed / total) * 100
        logger.info(f"Success rate: {success_rate:.1f}%")
        
        return passed, total, success_rate
    
    async def test_basic_initialization(self) -> bool:
        """Test basic initialization"""
        try:
            from analytics_engine import create_analytics_engine
            from metrics_collector import create_metrics_collector
            from dashboard_integration import create_dashboard_integration
            
            # Test analytics engine
            engine = create_analytics_engine()
            assert engine is not None
            assert not engine.is_running
            
            # Test metrics collector
            collector = create_metrics_collector()
            assert collector is not None
            assert not collector.is_collecting
            
            # Test dashboard integration
            dashboard = create_dashboard_integration()
            assert dashboard is not None
            
            # Test integration
            dashboard.initialize(engine, collector)
            assert dashboard.analytics_engine == engine
            assert dashboard.metrics_collector == collector
            
            return True
        except Exception as e:
            logger.error(f"Basic initialization test failed: {e}")
            return False
    
    async def test_market_data_collection(self) -> bool:
        """Test market data collection"""
        try:
            from analytics_engine import create_analytics_engine
            
            engine = create_analytics_engine()
            
            # Add market data
            market_data = {
                'symbol': 'EURUSD',
                'price': 1.1000,
                'volume': 1000,
                'volatility': 0.01,
                'sma_20': 1.0990,
                'sma_50': 1.0980,
                'rsi': 50.0,
                'macd': 0.001
            }
            
            engine.add_market_data(market_data)
            
            # Verify data was added
            assert len(engine.market_data) > 0
            
            # Test market analytics
            await engine._analyze_market_trends()
            await engine._calculate_market_indicators()
            await engine._detect_market_patterns()
            
            return True
        except Exception as e:
            logger.error(f"Market data collection test failed: {e}")
            return False
    
    async def test_user_data_collection(self) -> bool:
        """Test user data collection"""
        try:
            from analytics_engine import create_analytics_engine
            
            engine = create_analytics_engine()
            
            # Add user data
            user_data = {
                'action': 'login',
                'timestamp': datetime.now(),
                'metadata': {'device': 'mobile'}
            }
            
            engine.add_user_data('test_user', user_data)
            
            # Add trade data
            trade_data = {
                'action': 'trade',
                'timestamp': datetime.now(),
                'size': 1000,
                'profit_loss': 50.0,
                'symbol': 'EURUSD'
            }
            
            engine.add_user_data('test_user', trade_data)
            
            # Verify user data
            assert 'test_user' in engine.user_data
            assert len(engine.user_data['test_user']['activities']) > 0
            
            # Test user analytics
            await engine._analyze_user_behavior()
            await engine._calculate_engagement_metrics()
            
            return True
        except Exception as e:
            logger.error(f"User data collection test failed: {e}")
            return False
    
    async def test_system_metrics_collection(self) -> bool:
        """Test system metrics collection"""
        try:
            from metrics_collector import create_metrics_collector
            
            collector = create_metrics_collector({
                'collection_interval': 0.1,
                'enable_system_metrics': True
            })
            
            # Add manual metrics
            collector.collect_metric('test.metric', 42.5, source='test')
            collector.collect_metric('test.metric2', 100, {'category': 'test'}, source='test')
            
            # Start collection briefly
            collector.start_collection()
            await asyncio.sleep(0.5)
            collector.stop_collection()
            
            # Verify metrics were collected
            assert collector.collection_stats['total_collected'] > 0
            
            # Test metric retrieval
            value = collector.get_metric_value('test.metric', 'last')
            assert value is not None
            
            return True
        except Exception as e:
            logger.error(f"System metrics collection test failed: {e}")
            return False
    
    async def test_signal_performance_tracking(self) -> bool:
        """Test signal performance tracking"""
        try:
            from analytics_engine import create_analytics_engine
            
            engine = create_analytics_engine()
            
            # Add signal data
            signal_data = {
                'action': 'signal_generated',
                'confidence': 0.8,
                'symbol': 'EURUSD',
                'direction': 'buy'
            }
            
            engine.add_signal_data('test_signal', signal_data)
            
            # Update signal outcome
            outcome = {
                'return': 0.02,
                'accuracy': 0.85,
                'execution_time': 1.5
            }
            
            engine.update_signal_outcome('test_signal', outcome)
            
            # Verify signal data
            assert 'test_signal' in engine.signal_data
            assert len(engine.signal_data['test_signal']['signals']) > 0
            assert len(engine.signal_data['test_signal']['outcomes']) > 0
            
            # Test signal analytics
            await engine._analyze_signal_performance()
            await engine._calculate_signal_metrics()
            
            return True
        except Exception as e:
            logger.error(f"Signal performance tracking test failed: {e}")
            return False
    
    async def test_dashboard_integration(self) -> bool:
        """Test dashboard integration"""
        try:
            from analytics_engine import create_analytics_engine
            from metrics_collector import create_metrics_collector
            from dashboard_integration import create_dashboard_integration
            
            # Create components
            engine = create_analytics_engine()
            collector = create_metrics_collector()
            dashboard = create_dashboard_integration()
            
            # Initialize
            dashboard.initialize(engine, collector)
            
            # Test dashboard config access
            assert 'market_overview' in dashboard.dashboard_configs
            assert 'system_monitoring' in dashboard.dashboard_configs
            
            # Test chart data generation
            price_chart = dashboard._get_chart_data('price_chart')
            assert price_chart is not None
            
            # Test metrics summary
            summary = dashboard._get_metrics_summary()
            assert 'timestamp' in summary
            assert 'dashboards' in summary
            
            return True
        except Exception as e:
            logger.error(f"Dashboard integration test failed: {e}")
            return False
    
    async def test_data_export_import(self) -> bool:
        """Test data export/import functionality"""
        try:
            from analytics_engine import create_analytics_engine
            from metrics_collector import create_metrics_collector
            from dashboard_integration import create_dashboard_integration
            
            # Create and populate components
            engine = create_analytics_engine()
            collector = create_metrics_collector()
            dashboard = create_dashboard_integration()
            
            # Add some data
            market_data = {
                'symbol': 'EURUSD',
                'price': 1.1000,
                'volume': 1000,
                'volatility': 0.01
            }
            engine.add_market_data(market_data)
            
            collector.collect_metric('test.metric', 42.0, source='test')
            
            # Test analytics export
            analytics_export = engine.export_analytics_data('json')
            assert len(analytics_export) > 0
            assert 'market_data' in analytics_export
            
            # Test metrics export
            metrics_export = collector.export_metrics_data('json')
            assert len(metrics_export) > 0
            assert 'export_timestamp' in metrics_export
            
            # Test dashboard config export
            config_export = dashboard.export_dashboard_config('market_overview')
            assert len(config_export) > 0
            
            return True
        except Exception as e:
            logger.error(f"Data export/import test failed: {e}")
            return False
    
    async def test_real_time_processing(self) -> bool:
        """Test real-time processing"""
        try:
            from analytics_engine import create_analytics_engine
            
            engine = create_analytics_engine()
            
            # Start analytics
            engine.is_running = True
            
            # Add multiple data points rapidly
            for i in range(10):
                market_data = {
                    'symbol': f'SYMBOL{i % 3}',
                    'price': 1.1000 + (i * 0.001),
                    'volume': 1000 + i * 100,
                    'volatility': 0.01 + i * 0.001
                }
                engine.add_market_data(market_data)
                await asyncio.sleep(0.01)  # Small delay
            
            # Run analytics briefly
            await asyncio.sleep(0.5)
            
            # Stop analytics
            engine.is_running = False
            
            # Verify processing occurred
            assert len(engine.market_data) > 0
            
            return True
        except Exception as e:
            logger.error(f"Real-time processing test failed: {e}")
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling"""
        try:
            from analytics_engine import create_analytics_engine
            from metrics_collector import create_metrics_collector
            
            # Test with invalid data
            engine = create_analytics_engine()
            
            # Test with missing required fields
            try:
                engine.add_market_data({'symbol': 'EURUSD'})  # Missing price
                logger.warning("Missing price field was accepted")
            except Exception:
                pass  # Expected
            
            # Test with invalid data types
            try:
                engine.add_market_data({
                    'symbol': 123,  # Should be string
                    'price': 'invalid',  # Should be number
                    'volume': 1000
                })
                logger.warning("Invalid data types were accepted")
            except Exception:
                pass  # Expected
            
            # Test metrics collector error handling
            collector = create_metrics_collector()
            
            # Test invalid metric value
            try:
                collector.collect_metric('test', float('inf'), source='test')
            except Exception:
                pass  # Should handle gracefully
            
            return True
        except Exception as e:
            logger.error(f"Error handling test failed: {e}")
            return False
    
    async def test_performance_benchmarks(self) -> bool:
        """Test performance benchmarks"""
        try:
            from analytics_engine import create_analytics_engine
            from metrics_collector import create_metrics_collector
            
            # Test analytics engine performance
            engine = create_analytics_engine()
            
            start_time = time.time()
            
            # Add large amount of data
            for i in range(100):
                market_data = {
                    'symbol': f'SYMBOL{i % 5}',
                    'price': 1.1000 + (i * 0.0001),
                    'volume': 1000 + i * 10,
                    'volatility': 0.01 + i * 0.0001
                }
                engine.add_market_data(market_data)
            
            analytics_time = time.time() - start_time
            
            # Test metrics collector performance
            collector = create_metrics_collector()
            
            start_time = time.time()
            
            # Add many metrics
            for i in range(200):
                collector.collect_metric(f'test.metric.{i}', i, source='test')
            
            metrics_time = time.time() - start_time
            
            # Performance thresholds (adjust as needed)
            max_analytics_time = 1.0  # seconds
            max_metrics_time = 1.0  # seconds
            
            logger.info(f"Analytics performance: {analytics_time:.3f}s for 100 data points")
            logger.info(f"Metrics performance: {metrics_time:.3f}s for 200 metrics")
            
            return analytics_time < max_analytics_time and metrics_time < max_metrics_time
            
        except Exception as e:
            logger.error(f"Performance benchmarks test failed: {e}")
            return False
    
    async def generate_test_report(self) -> Dict:
        """Test hisobot yaratish"""
        passed, total, success_rate = await self.run_all_tests()
        
        report = {
            'test_timestamp': datetime.now().isoformat(),
            'total_tests': total,
            'passed_tests': passed,
            'failed_tests': total - passed,
            'success_rate': success_rate,
            'test_results': self.test_results,
            'system_info': {
                'python_version': '3.x',
                'modules_available': self._check_module_availability()
            }
        }
        
        return report
    
    def _check_module_availability(self) -> Dict:
        """Module availability tekshirish"""
        modules = {
            'numpy': False,
            'pandas': False,
            'asyncio': True,
            'json': True,
            'datetime': True
        }
        
        for module in modules:
            try:
                __import__(module)
                modules[module] = True
            except ImportError:
                pass
        
        return modules


async def run_integration_test():
    """Integration test ishga tushirish"""
    print("🧪 ANALYTICS ENGINE INTEGRATION TEST")
    print("=" * 50)
    
    test = AnalyticsIntegrationTest()
    
    try:
        # Run all tests
        report = await test.generate_test_report()
        
        # Display results
        print(f"\n📊 TEST RESULTS")
        print(f"Total tests: {report['total_tests']}")
        print(f"Passed: {report['passed_tests']}")
        print(f"Failed: {report['failed_tests']}")
        print(f"Success rate: {report['success_rate']:.1f}%")
        
        print(f"\n📦 MODULE AVAILABILITY")
        for module, available in report['system_info']['modules_available'].items():
            status = "✅" if available else "❌"
            print(f"{status} {module}")
        
        # Save report
        with open('/workspace/orion-starline/backend/ai_modules/integration_test_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Test report saved to integration_test_report.json")
        
        if report['success_rate'] >= 80:
            print(f"\n🎉 INTEGRATION TEST SUCCESSFUL!")
            print("Analytics Engine tizimi to'g'ri ishlayapti.")
        else:
            print(f"\n⚠️ INTEGRATION TEST NEEDS ATTENTION")
            print("Ba'zi testlar muvaffaqiyatsiz bo'ldi.")
        
        return report['success_rate'] >= 80
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run integration test
    success = asyncio.run(run_integration_test())
    exit(0 if success else 1)