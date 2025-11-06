"""
Analytics Engine Demo va Test
==============================

Bu fayl real-time analytics engine tizimining barcha komponentlarini
test qilish va demo qilish uchun mo'ljallangan.
"""

import asyncio
import json
import logging
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List

# Import analytics components
try:
    from analytics_engine import AnalyticsEngine, create_analytics_engine
    from metrics_collector import MetricsCollector, create_metrics_collector
    from dashboard_integration import DashboardIntegration, create_dashboard_integration
except ImportError:
    print("Error: Analytics modules not found. Make sure they are in the same directory.")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AnalyticsDemo:
    """Analytics engine demo va test class"""
    
    def __init__(self):
        self.analytics_engine = None
        self.metrics_collector = None
        self.dashboard_integration = None
        self.demo_running = False
        
    async def initialize(self):
        """Analytics tizimini initialize qilish"""
        logger.info("Analytics tizimini initialize qilish...")
        
        # Analytics engine
        analytics_config = {
            'market_analysis': {
                'price_lookback': 50,
                'volume_threshold': 1.5,
                'volatility_threshold': 0.02
            },
            'user_analysis': {
                'session_timeout': 30,
                'min_trades': 5,
                'risk_weight': 0.3
            },
            'system_monitoring': {
                'cpu_alert': 80,
                'memory_alert': 85,
                'response_alert': 1000
            }
        }
        self.analytics_engine = create_analytics_engine(analytics_config)
        
        # Metrics collector
        metrics_config = {
            'collection_interval': 0.5,
            'batch_size': 50,
            'aggregation_interval': 1.0,
            'enable_system_metrics': True,
            'enable_market_metrics': True,
            'enable_user_metrics': True,
            'enable_custom_metrics': True,
            'data_retention_days': 7
        }
        self.metrics_collector = create_metrics_collector(metrics_config)
        
        # Dashboard integration
        dashboard_config = {
            'dashboard': {
                'host': '0.0.0.0',
                'port': 5000,
                'debug': False,
                'auto_start': False
            },
            'data_refresh': {
                'default_interval': 1,
                'chart_timeout': 30
            }
        }
        self.dashboard_integration = create_dashboard_integration(dashboard_config)
        
        # Integrate components
        self.dashboard_integration.initialize(
            self.analytics_engine,
            self.metrics_collector
        )
        
        logger.info("Analytics tizimi muvaffaqiyatli initialize qilindi!")
    
    async def start_demo(self, duration: int = 30):
        """Demo start qilish"""
        logger.info(f"Analytics demo {duration} soniya davomida ishga tushadi...")
        
        self.demo_running = True
        
        # Start components
        await self._start_components()
        
        try:
            # Demo loop
            await self._run_demo_loop(duration)
            
        finally:
            # Stop components
            await self._stop_components()
            self.demo_running = False
        
        # Generate final report
        await self._generate_final_report()
    
    async def _start_components(self):
        """Components start qilish"""
        logger.info("Analytics components ishga tushirilmoqda...")
        
        # Start metrics collection
        self.metrics_collector.start_collection()
        logger.info("✓ Metrics Collector ishga tushdi")
        
        # Start analytics engine
        analytics_task = asyncio.create_task(self.analytics_engine.start_analytics())
        await asyncio.sleep(0.1)  # Let it start
        logger.info("✓ Analytics Engine ishga tushdi")
        
        # Add custom metrics
        self._setup_custom_metrics()
        logger.info("✓ Custom metrics sozlandi")
    
    def _setup_custom_metrics(self):
        """Custom metrics qo'shish"""
        def trading_volume_collector():
            volume = random.randint(100, 10000)
            self.metrics_collector.collect_metric('trading.volume', volume, source='custom')
        
        def signal_accuracy_collector():
            accuracy = random.uniform(0.6, 0.95)
            self.metrics_collector.collect_metric('signals.accuracy', accuracy, source='custom')
        
        def user_satisfaction_collector():
            satisfaction = random.uniform(3.0, 5.0)
            self.metrics_collector.collect_metric('users.satisfaction', satisfaction, source='custom')
        
        # Add custom collectors
        self.metrics_collector.add_custom_collector('trading_volume', trading_volume_collector, 3.0)
        self.metrics_collector.add_custom_collector('signal_accuracy', signal_accuracy_collector, 5.0)
        self.metrics_collector.add_custom_collector('user_satisfaction', user_satisfaction_collector, 10.0)
    
    async def _run_demo_loop(self, duration: int):
        """Demo asosiy loop"""
        logger.info(f"Demo loop boshlanmoqda ({duration} soniya)...")
        
        start_time = time.time()
        sample_count = 0
        
        while self.demo_running and (time.time() - start_time) < duration:
            sample_count += 1
            
            # Generate sample data
            await self._generate_sample_data()
            
            # Print progress
            if sample_count % 5 == 0:
                elapsed = time.time() - start_time
                logger.info(f"Demo running... {sample_count} samples, {elapsed:.1f}s elapsed")
            
            # Wait before next iteration
            await asyncio.sleep(1)
        
        logger.info(f"Demo loop tugadi. Jami {sample_count} sample yaratildi.")
    
    async def _generate_sample_data(self):
        """Sample data yaratish"""
        
        # Market data samples
        symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD']
        for symbol in symbols:
            market_data = {
                'symbol': symbol,
                'price': 1.0000 + random.uniform(-0.05, 0.05),
                'volume': random.randint(100, 10000),
                'volatility': random.uniform(0.001, 0.05),
                'sma_20': 1.0000 + random.uniform(-0.01, 0.01),
                'sma_50': 1.0000 + random.uniform(-0.02, 0.02),
                'rsi': random.uniform(20, 80),
                'macd': random.uniform(-0.001, 0.001)
            }
            self.analytics_engine.add_market_data(market_data)
        
        # User data samples
        user_actions = ['login', 'logout', 'trade', 'view_portfolio', 'update_settings', 'deposit']
        for i in range(3):  # 3 user samples per iteration
            user_id = f"user_{random.randint(1, 20):03d}"
            action = random.choice(user_actions)
            
            user_data = {
                'action': action,
                'timestamp': datetime.now(),
                'metadata': {
                    'device': random.choice(['mobile', 'desktop', 'tablet']),
                    'session_id': random.randint(1000, 9999),
                    'location': random.choice(['Tashkent', 'Samarkand', 'Bukhara', 'Fergana'])
                }
            }
            
            if action == 'trade':
                user_data['size'] = random.randint(100, 10000)
                user_data['profit_loss'] = random.uniform(-500, 500)
                user_data['symbol'] = random.choice(symbols)
            
            self.analytics_engine.add_user_data(user_id, user_data)
        
        # Signal data samples
        for i in range(2):  # 2 signal samples per iteration
            signal_id = f"signal_{random.randint(1, 10):03d}"
            signal_data = {
                'action': 'signal_generated',
                'confidence': random.uniform(0.6, 0.95),
                'symbol': random.choice(symbols),
                'direction': random.choice(['buy', 'sell']),
                'timestamp': datetime.now()
            }
            self.analytics_engine.add_signal_data(signal_id, signal_data)
            
            # Simulate signal outcome
            if random.random() > 0.7:  # 30% chance of completed signal
                outcome = {
                    'return': random.uniform(-0.1, 0.15),
                    'accuracy': random.uniform(0.5, 0.9),
                    'execution_time': random.uniform(0.1, 2.0)
                }
                self.analytics_engine.update_signal_outcome(signal_id, outcome)
    
    async def _stop_components(self):
        """Components to'xtatish"""
        logger.info("Analytics components to'xtatilmoqda...")
        
        # Stop analytics engine
        if self.analytics_engine:
            await self.analytics_engine.stop_analytics()
            logger.info("✓ Analytics Engine to'xtatildi")
        
        # Stop metrics collector
        if self.metrics_collector:
            self.metrics_collector.stop_collection()
            logger.info("✓ Metrics Collector to'xtatildi")
    
    async def _generate_final_report(self):
        """Final hisobot yaratish"""
        logger.info("Final hisobot yaratilmoqda...")
        
        print("\n" + "="*80)
        print("REAL-TIME ANALYTICS ENGINE - FINAL REPORT")
        print("="*80)
        
        # 1. Market Analytics Report
        print("\n📊 MARKET ANALYTICS REPORT")
        print("-" * 50)
        try:
            market_report = self.analytics_engine.get_market_analytics_report('1h')
            if 'error' not in market_report:
                print(f"Data points: {market_report['data_points']}")
                print(f"Price range: {market_report['price_stats']['min']:.4f} - {market_report['price_stats']['max']:.4f}")
                print(f"Average price: {market_report['price_stats']['avg']:.4f}")
                print(f"Volatility: {market_report['price_stats']['volatility']:.4f}")
            else:
                print(f"Error: {market_report['error']}")
        except Exception as e:
            print(f"Market report error: {e}")
        
        # 2. User Analytics Report
        print("\n👥 USER ANALYTICS REPORT")
        print("-" * 50)
        try:
            user_report = self.analytics_engine.get_user_analytics_report()
            if 'error' not in user_report:
                print(f"Total users: {user_report['total_users']}")
                print(f"Active users: {user_report['active_users']} ({user_report['active_rate']:.1%})")
                print(f"Total trades: {user_report['total_trades']}")
                print(f"Average engagement: {user_report['avg_engagement']:.2f}")
            else:
                print(f"Error: {user_report['error']}")
        except Exception as e:
            print(f"User report error: {e}")
        
        # 3. System Analytics Report
        print("\n🖥️  SYSTEM ANALYTICS REPORT")
        print("-" * 50)
        try:
            system_report = self.analytics_engine.get_system_analytics_report()
            if 'error' not in system_report:
                print(f"CPU usage: {system_report['cpu_usage']['current']:.1f}%")
                print(f"Memory usage: {system_report['memory_usage']['current']:.1f}%")
                print(f"Total alerts: {system_report['alerts']['total']}")
            else:
                print(f"Error: {system_report['error']}")
        except Exception as e:
            print(f"System report error: {e}")
        
        # 4. Signal Performance Report
        print("\n📈 SIGNAL PERFORMANCE REPORT")
        print("-" * 50)
        try:
            signal_report = self.analytics_engine.get_signal_performance_report()
            if 'error' not in signal_report:
                print(f"Total signals: {signal_report['total_signals']}")
                print(f"Average return: {signal_report['avg_return']:.2%}")
                print(f"Average accuracy: {signal_report['avg_accuracy']:.2%}")
                print(f"Win rate: {signal_report['win_rate']:.1%}")
            else:
                print(f"Error: {signal_report['error']}")
        except Exception as e:
            print(f"Signal report error: {e}")
        
        # 5. Metrics Summary
        print("\n📋 METRICS COLLECTOR SUMMARY")
        print("-" * 50)
        try:
            metrics_summary = self.metrics_collector.get_all_metrics_summary()
            print(f"Total collected: {metrics_summary['collection_stats']['total_collected']}")
            print(f"Total processed: {metrics_summary['collection_stats']['total_processed']}")
            print(f"Active collectors: {metrics_summary['active_collectors']}")
            print(f"Total metric types: {metrics_summary['total_metric_types']}")
        except Exception as e:
            print(f"Metrics summary error: {e}")
        
        # 6. Dashboard Data
        print("\n🎯 DASHBOARD DATA")
        print("-" * 50)
        try:
            dashboard_data = self.analytics_engine.get_dashboard_data()
            print(f"Active signals: {dashboard_data['active_signals']}")
            print(f"Total users: {dashboard_data['total_users']}")
            print(f"Recent alerts: {len(dashboard_data['recent_alerts'])}")
            print(f"Last update: {dashboard_data['last_update']}")
        except Exception as e:
            print(f"Dashboard data error: {e}")
        
        # 7. Performance Statistics
        print("\n⚡ PERFORMANCE STATISTICS")
        print("-" * 50)
        try:
            performance_stats = self.dashboard_integration.get_performance_stats()
            print(f"Update statistics: {performance_stats['update_stats']}")
            print(f"Active connections: {performance_stats['active_connections']}")
            print(f"Cached charts: {performance_stats['cached_charts']}")
            print(f"Server running: {performance_stats['server_running']}")
        except Exception as e:
            print(f"Performance stats error: {e}")
        
        # 8. Real-time Metrics Sample
        print("\n🔄 REAL-TIME METRICS SAMPLE")
        print("-" * 50)
        try:
            realtime_data = self.metrics_collector.get_real_time_metrics()
            print(f"System metrics: {list(realtime_data['system_metrics'].keys())[:5]}")
            print(f"Market metrics: {list(realtime_data['market_metrics'].keys())[:5]}")
            print(f"User metrics: {list(realtime_data['user_metrics'].keys())[:5]}")
        except Exception as e:
            print(f"Real-time metrics error: {e}")
        
        print("\n" + "="*80)
        print("✅ ANALYTICS ENGINE DEMO MUVAFFAQIYATLI TUGALLANDI!")
        print("="*80)
        
        # Export data samples
        await self._export_sample_data()
    
    async def _export_sample_data(self):
        """Sample ma'lumotlarni eksport qilish"""
        print("\n💾 EXPORTING SAMPLE DATA...")
        
        try:
            # Export analytics data
            analytics_export = self.analytics_engine.export_analytics_data('json')
            with open('/workspace/orion-starline/backend/ai_modules/demo_analytics_export.json', 'w') as f:
                f.write(analytics_export)
            print("✓ Analytics data exported to demo_analytics_export.json")
            
            # Export metrics data
            metrics_export = self.metrics_collector.export_metrics_data('json')
            with open('/workspace/orion-starline/backend/ai_modules/demo_metrics_export.json', 'w') as f:
                f.write(metrics_export)
            print("✓ Metrics data exported to demo_metrics_export.json")
            
            # Export dashboard config
            market_config = self.dashboard_integration.export_dashboard_config('market_overview')
            with open('/workspace/orion-starline/backend/ai_modules/demo_dashboard_config.json', 'w') as f:
                f.write(market_config)
            print("✓ Dashboard config exported to demo_dashboard_config.json")
            
        except Exception as e:
            print(f"Export error: {e}")
    
    def get_html_dashboard(self, dashboard_id: str = 'market_overview') -> str:
        """HTML dashboard olish"""
        if self.dashboard_integration:
            return self.dashboard_integration.get_dashboard_html(dashboard_id)
        return "Dashboard not available"


async def run_comprehensive_demo():
    """Comprehensive demo ishga tushirish"""
    print("🚀 REAL-TIME ANALYTICS ENGINE - COMPREHENSIVE DEMO")
    print("="*60)
    
    demo = AnalyticsDemo()
    
    try:
        # Initialize
        await demo.initialize()
        
        # Run demo
        await demo.start_demo(duration=20)  # 20 seconds demo
        
        # Show HTML dashboard sample
        print("\n📱 HTML DASHBOARD SAMPLE")
        print("-" * 40)
        html_sample = demo.get_html_dashboard()
        print("HTML dashboard generated successfully!")
        print(f"HTML length: {len(html_sample)} characters")
        
        print("\n🎉 Demo muvaffaqiyatli tugallandi!")
        print("\nKel'si qadamlar:")
        print("1. dashboard_integration.start_web_server() - Web dashboard ishga tushirish")
        print("2. http://localhost:5000 - Dashboard ko'rish")
        print("3. /api/dashboards - API endpoint test qilish")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run comprehensive demo
    asyncio.run(run_comprehensive_demo())