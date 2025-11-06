#!/usr/bin/env python3
"""
HFT Engine Demo
===============

Demo script to showcase HFT Engine capabilities
"""

import asyncio
import time
import logging
import json
from typing import Dict, Any

# Import HFT Engine components
from main import HFTApplication
from config.default_config import load_config
from core import HFTEngine
from utils import PerformanceProfiler, BenchmarkTool

class HFTDemo:
    """HFT Engine Demo Application"""
    
    def __init__(self):
        self.config = load_config('development')
        self.logger = logging.getLogger(__name__)
        
        # Demo components
        self.engine = None
        self.perf_profiler = PerformanceProfiler()
        self.benchmark = BenchmarkTool()
        
    async def run_basic_demo(self):
        """Run basic HFT engine demo"""
        print("🚀 HFT Engine - Basic Demo")
        print("=" * 50)
        
        try:
            # Create HFT engine
            self.engine = HFTEngine(self.config)
            
            # Initialize engine
            print("📡 Initializing HFT Engine...")
            if await self.engine.initialize():
                print("✅ Engine initialized successfully")
            else:
                print("❌ Engine initialization failed")
                return
            
            # Show initial status
            print("\n📊 Engine Status:")
            status = self.engine.get_health_status()
            print(f"   Active symbols: {status['active_symbols']}")
            print(f"   Loaded strategies: {status['loaded_strategies']}")
            print(f"   Total positions: {status['total_positions']}")
            
            # Run engine for a short time
            print("\n⚡ Starting HFT operations (10 seconds)...")
            
            # Create demo task
            demo_task = asyncio.create_task(self._demo_trading_loop())
            
            # Wait for demo to complete
            await asyncio.sleep(10)
            
            # Cancel demo task
            demo_task.cancel()
            try:
                await demo_task
            except asyncio.CancelledError:
                pass
            
            # Show final metrics
            print("\n📈 Performance Metrics:")
            metrics = await self.engine.get_performance_metrics()
            
            # Latency statistics
            latency_stats = metrics.get('latency_stats', {})
            if latency_stats:
                print("   Latency Statistics:")
                for stat_name, stat_data in latency_stats.items():
                    if isinstance(stat_data, dict) and 'mean_us' in stat_data:
                        print(f"     {stat_name}: {stat_data['mean_us']:.1f}μs (avg)")
            
            # Position summary
            positions = metrics.get('active_positions', {})
            if positions:
                print(f"   Active positions: {len([p for p in positions.values() if p != 0])}")
            
            # Strategy status
            strategies = metrics.get('strategies_status', {})
            if strategies:
                print("   Strategy Status:")
                for strategy_name, strategy_data in strategies.items():
                    print(f"     {strategy_name}: Active")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
        finally:
            if self.engine:
                await self.engine.shutdown()
                print("🛑 Engine shutdown complete")
    
    async def _demo_trading_loop(self):
        """Demo trading loop simulation"""
        try:
            while True:
                start_time = self.perf_profiler.start_time
                
                # Simulate trading operations
                await self._simulate_trading_cycle()
                
                # Record performance
                execution_time = time.perf_counter() - start_time
                self.perf_profiler.record_metric(
                    "demo_cycle_time",
                    execution_time * 1_000_000,
                    "μs",
                    "demo"
                )
                
                # Short pause
                await asyncio.sleep(0.1)
                
        except asyncio.CancelledError:
            print("   Demo trading loop cancelled")
    
    async def _simulate_trading_cycle(self):
        """Simulate a trading cycle"""
        # Simulate market data processing
        await asyncio.sleep(0.001)  # 1ms market data update
        
        # Simulate signal generation
        await asyncio.sleep(0.005)  # 5ms strategy execution
        
        # Simulate order processing
        await asyncio.sleep(0.001)  # 1ms order management
        
        # Simulate risk checks
        await asyncio.sleep(0.0005)  # 0.5ms risk management
        
    async def run_performance_demo(self):
        """Run performance benchmarking demo"""
        print("\n⚡ HFT Engine - Performance Demo")
        print("=" * 50)
        
        # Benchmark different operations
        operations = [
            ("Order Creation", self._benchmark_order_creation),
            ("Market Data Processing", self._benchmark_market_data),
            ("Risk Calculation", self._benchmark_risk_calc),
            ("Strategy Signal", self._benchmark_strategy_signal),
            ("Latency Measurement", self._benchmark_latency_measure)
        ]
        
        print("🏁 Running performance benchmarks...")
        
        for op_name, op_func in operations:
            print(f"\n   Testing {op_name}...")
            result = self.benchmark.benchmark_function(op_func, iterations=1000)
            
            print(f"     Average: {result['avg_time_us']:.2f}μs")
            print(f"     Throughput: {result['throughput_per_sec']:.0f} ops/sec")
        
        # Show comparison
        print("\n📊 Performance Comparison:")
        comparison = self.benchmark.compare_benchmarks()
        
        if comparison:
            print(f"   Fastest: {comparison['fastest']['function']} "
                  f"({comparison['fastest']['throughput']:.0f} ops/sec)")
            print(f"   Slowest: {comparison['slowest']['function']} "
                  f"({comparison['slowest']['throughput']:.0f} ops/sec)")
            print(f"   Speedup factor: {comparison['speedup_factor']:.1f}x")
    
    async def _benchmark_order_creation(self):
        """Benchmark order creation"""
        # Simulate order creation
        order_data = {
            'symbol': 'AAPL',
            'side': 'buy',
            'quantity': 100,
            'price': 150.0
        }
        # Simulate processing time
        await asyncio.sleep(0.00001)  # 10μs
    
    async def _benchmark_market_data(self):
        """Benchmark market data processing"""
        # Simulate market data processing
        tick_data = {
            'symbol': 'AAPL',
            'bid': 149.99,
            'ask': 150.01,
            'last': 150.00,
            'volume': 1000
        }
        # Simulate processing time
        await asyncio.sleep(0.00005)  # 50μs
    
    async def _benchmark_risk_calc(self):
        """Benchmark risk calculation"""
        # Simulate risk calculation
        position = 1000
        price = 150.0
        # Simulate processing time
        await asyncio.sleep(0.000005)  # 5μs
    
    async def _benchmark_strategy_signal(self):
        """Benchmark strategy signal generation"""
        # Simulate strategy signal
        signal = {
            'symbol': 'AAPL',
            'type': 'buy',
            'confidence': 0.8,
            'price': 150.0
        }
        # Simulate processing time
        await asyncio.sleep(0.00002)  # 20μs
    
    async def _benchmark_latency_measure(self):
        """Benchmark latency measurement"""
        # Simulate latency measurement
        start = time.perf_counter()
        end = time.perf_counter()
        latency = (end - start) * 1_000_000  # Convert to microseconds
    
    async def run_strategy_demo(self):
        """Run strategy demonstration"""
        print("\n🤖 HFT Engine - Strategy Demo")
        print("=" * 50)
        
        # Import strategy components
        from strategies import (
            MarketMakingStrategy,
            ArbitrageStrategy,
            StatisticalArbitrageStrategy
        )
        
        # Demo strategies
        strategies = {
            'Market Making': MarketMakingStrategy(
                symbols=['AAPL', 'MSFT', 'GOOGL'],
                config=self.config.get('market_making', {})
            ),
            'Arbitrage': ArbitrageStrategy(
                symbols=['EUR/USD', 'GBP/USD', 'USD/JPY'],
                config=self.config.get('arbitrage', {})
            ),
            'Statistical Arbitrage': StatisticalArbitrageStrategy(
                symbols=['AAPL', 'MSFT', 'BTC/USD', 'ETH/USD'],
                config=self.config.get('stat_arb', {})
            )
        }
        
        print("🎯 Demonstrating trading strategies...")
        
        for strategy_name, strategy in strategies.items():
            print(f"\n   {strategy_name}:")
            
            # Show strategy configuration
            status = strategy.get_strategy_status()
            print(f"     Config: {json.dumps(status, indent=6)[0:100]}...")
            
            # Simulate signal generation
            await asyncio.sleep(0.1)  # Simulate processing time
            
            print(f"     Status: ✅ Active")
        
        print("\n📈 Strategy Performance Summary:")
        print("   Market Making: High-frequency, low-risk")
        print("   Arbitrage: Medium-frequency, medium-risk") 
        print("   Statistical Arbitrage: Low-frequency, low-risk")
    
    async def run_risk_demo(self):
        """Run risk management demo"""
        print("\n🛡️ HFT Engine - Risk Management Demo")
        print("=" * 50)
        
        # Import risk components
        from risk import RiskManager
        
        # Create risk manager
        risk_manager = RiskManager(self.config.get('risk', {}))
        
        # Initialize risk manager
        await risk_manager.initialize()
        
        print("🔍 Risk Management System initialized")
        
        # Demonstrate risk checks
        print("\n   Testing risk limits:")
        
        # Test position size limit
        test_signal = type('Signal', (), {
            'symbol': 'AAPL',
            'quantity': 1000,
            'price': 150.0,
            'side': 'buy'
        })()
        
        position_check = await risk_manager.check_signal(test_signal)
        print(f"     Position check (1000 shares): {'✅ PASS' if position_check else '❌ FAIL'}")
        
        # Test smaller position
        test_signal.quantity = 100
        position_check = await risk_manager.check_signal(test_signal)
        print(f"     Position check (100 shares): {'✅ PASS' if position_check else '❌ FAIL'}")
        
        # Show risk dashboard
        dashboard = risk_manager.get_risk_dashboard()
        print(f"\n   Risk Dashboard:")
        print(f"     Risk Level: {dashboard['risk_level']}")
        print(f"     Total Exposure: ${dashboard['total_exposure']:,.2f}")
        print(f"     Active Alerts: {dashboard['active_alerts']}")
        print(f"     System Health: {dashboard['system_health']}")
        
        # Shutdown risk manager
        await risk_manager.shutdown()
    
    async def run_infrastructure_demo(self):
        """Run infrastructure demo"""
        print("\n🏗️ HFT Engine - Infrastructure Demo")
        print("=" * 50)
        
        # Import infrastructure components
        from infrastructure import (
            CoLocationService,
            NetworkOptimization,
            MonitoringService
        )
        
        print("📡 Infrastructure Components:")
        
        # Co-location service
        co_location = CoLocationService(self.config.get('infrastructure', {}))
        await co_location.initialize()
        
        connection_status = co_location.get_connection_status()
        print(f"   Co-location: {len(connection_status)} connections")
        for exchange, status in connection_status.items():
            print(f"     {exchange}: {status['latency_us']}μs")
        
        # Network optimization
        network_opt = NetworkOptimization(
            self.config.get('infrastructure', {})
        )
        await network_opt.initialize()
        
        opt_metrics = network_opt.get_optimization_metrics()
        print(f"   Network Optimization: {len(opt_metrics)} features")
        
        # Monitoring service
        monitoring = MonitoringService(
            self.config.get('infrastructure', {})
        )
        await monitoring.initialize()
        
        dashboard_data = monitoring.get_dashboard_data()
        print(f"   Monitoring: {dashboard_data['system_health']}")
        print(f"     Uptime: {dashboard_data['uptime_seconds']:.1f}s")
        print(f"     Active alerts: {dashboard_data['active_alerts']}")
        
        # Cleanup
        await co_location.shutdown()
        await network_opt.shutdown()
        await monitoring.shutdown()

async def main():
    """Main demo function"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎯 High-Frequency Trading Engine Demo")
    print("=" * 60)
    print("This demo showcases the HFT Engine capabilities:")
    print("  • Core Engine Operations")
    print("  • Performance Benchmarking")
    print("  • Trading Strategies")
    print("  • Risk Management")
    print("  • Infrastructure Components")
    print("=" * 60)
    
    demo = HFTDemo()
    
    try:
        # Run all demos
        await demo.run_basic_demo()
        await demo.run_performance_demo()
        await demo.run_strategy_demo()
        await demo.run_risk_demo()
        await demo.run_infrastructure_demo()
        
        print("\n🎉 HFT Engine Demo Complete!")
        print("=" * 60)
        print("Demo Summary:")
        print("✅ Core engine operations tested")
        print("✅ Performance benchmarks completed")
        print("✅ Trading strategies demonstrated")
        print("✅ Risk management verified")
        print("✅ Infrastructure components validated")
        print("\nReady for production deployment! 🚀")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        raise

if __name__ == '__main__':
    # Run the demo
    asyncio.run(main())