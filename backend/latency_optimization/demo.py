#!/usr/bin/env python3
"""
Latency Optimization System Demo
This script demonstrates the key features of the latency optimization system.
"""

import time
import json
import logging
import threading
from typing import Dict, Any

# Import the latency optimization system
from latency_optimization import (
    LatencyOptimizer, LatencyConfig, NetworkConfig, HardwareConfig, SoftwareConfig,
    PerformanceProfileManager, LatencyUtils, BenchmarkRunner, SystemProfiler,
    MarketDataProcessor, MarketDataConfig, PerformanceTimer
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_system_readiness():
    """Demonstrate system readiness check"""
    logger.info("🔍 Checking System Readiness...")
    
    profiler = SystemProfiler()
    readiness = profiler.check_optimization_readiness()
    
    print(f"System Readiness Score: {readiness['readiness_percent']:.1f}%")
    print(f"All Requirements Passed: {readiness['all_passed']}")
    
    if readiness['recommendations']:
        print("📋 Recommendations:")
        for rec in readiness['recommendations']:
            print(f"  • {rec}")
    
    # Show system info
    system_info = profiler.get_detailed_system_info()
    print(f"🖥️ Platform: {system_info['platform']}")
    print(f"💾 Memory: {system_info['memory_total_gb']:.1f}GB")
    print(f"🖥️ CPU Cores: {system_info['cpu_count_logical']} logical, {system_info['cpu_count_physical']} physical")
    
    return readiness


def demo_performance_profiles():
    """Demonstrate performance profiles"""
    logger.info("⚡ Performance Profiles Demo...")
    
    profile_manager = PerformanceProfileManager()
    
    # Show available profiles
    profiles = profile_manager.list_profiles()
    print("Available Performance Profiles:")
    for name, desc in profiles.items():
        profile = profile_manager.get_profile(name)
        print(f"  • {name}: {desc}")
        print(f"    Target Latency: {profile.target_latency_us}μs")
    
    # Create custom profile
    custom_profile = profile_manager.create_custom_profile(
        name="demo_profile",
        description="Demo custom profile",
        base_profile="high",
        overrides={
            'target_latency_us': 5,
            'software_config': {
                'zero_copy_enabled': True,
                'lock_free_algorithms': True
            }
        }
    )
    
    print(f"\n🛠️ Created Custom Profile:")
    print(f"  Name: {custom_profile.name}")
    print(f"  Target Latency: {custom_profile.target_latency_us}μs")
    print(f"  Zero-copy: {custom_profile.software_config['zero_copy_enabled']}")
    print(f"  Lock-free: {custom_profile.software_config['lock_free_algorithms']}")
    
    return profile_manager


def demo_benchmarking():
    """Demonstrate benchmarking capabilities"""
    logger.info("🏁 Benchmarking Demo...")
    
    utils = LatencyUtils()
    runner = BenchmarkRunner(utils)
    
    print("Running Core Benchmarks...")
    
    # CPU benchmark
    print("\n🖥️ CPU Benchmark:")
    cpu_result = runner.run_benchmark('cpu_intensive', iterations=100000)
    if 'ops_per_second' in cpu_result:
        print(f"  Operations per second: {cpu_result['ops_per_second']:,.0f}")
        print(f"  Time: {cpu_result['time_seconds']:.3f}s")
    
    # Memory benchmark
    print("\n💾 Memory Benchmark:")
    memory_result = runner.run_benchmark('memory_bandwidth', size_mb=50)
    if 'read_write_bandwidth_mbps' in memory_result:
        print(f"  Read/Write Bandwidth: {memory_result['read_write_bandwidth_mbps']:.1f} MB/s")
        print(f"  Read Bandwidth: {memory_result['read_bandwidth_mbps']:.1f} MB/s")
    
    # Cache benchmark
    print("\n⚡ Cache Benchmark:")
    cache_result = runner.run_benchmark('cache_performance', iterations=1000000)
    if 'size_1024' in cache_result:
        size_1k = cache_result['size_1024']
        print(f"  1K array avg access: {size_1k['avg_access_time_ns']:.2f}ns")
    
    return runner


def demo_optimization():
    """Demonstrate optimization process"""
    logger.info("🚀 Optimization Demo...")
    
    # Create configuration
    config = LatencyConfig(
        target_latency_us=20,
        performance_mode="high",
        monitoring_interval_ms=100
    )
    
    # Initialize optimizer
    optimizer = LatencyOptimizer(config)
    
    print(f"Target Latency: {config.target_latency_us}μs")
    print(f"Performance Mode: {config.performance_mode}")
    
    # Apply performance profile
    print("\n📊 Applying Performance Profile...")
    result = optimizer.apply_performance_profile("high")
    
    if result.success:
        print(f"✅ Successfully applied {len(result.applied_optimizations)} optimizations:")
        for opt in result.applied_optimizations:
            print(f"  • {opt}")
        print(f"📈 Latency Improvement: {result.latency_improvement_percent:.1f}%")
    else:
        print("❌ Optimization failed")
        for issue in result.issues:
            print(f"  • {issue}")
    
    return optimizer


def demo_market_data():
    """Demonstrate market data processing"""
    logger.info("📈 Market Data Processing Demo...")
    
    config = MarketDataConfig(
        tick_buffer_size=10000,
        order_book_levels=10,
        max_symbols=100,
        batch_processing=True
    )
    
    processor = MarketDataProcessor(config)
    
    print(f"Tick Buffer Size: {config.tick_buffer_size}")
    print(f"Order Book Levels: {config.order_book_levels}")
    
    # Process sample tick data
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
    total_ticks = 0
    total_time_us = 0
    
    print("\n📊 Processing Market Data...")
    for i in range(20):
        symbol = symbols[i % len(symbols)]
        
        tick_data = {
            'symbol': symbol,
            'bid_price': 100.0 + i * 0.01,
            'ask_price': 100.01 + i * 0.01,
            'bid_size': 1000 + i * 10,
            'ask_size': 1000 + i * 10,
            'timestamp': time.time(),
            'volume': i * 100
        }
        
        result = processor.process_market_data(tick_data)
        
        if result['success']:
            total_ticks += 1
            total_time_us += result.get('processing_time_us', 0)
            
            if i % 5 == 0:
                print(f"  Tick {i}: {result.get('processing_time_us', 0):.2f}μs")
    
    avg_latency = total_time_us / total_ticks if total_ticks > 0 else 0
    print(f"\n📊 Processing Summary:")
    print(f"  Total Ticks: {total_ticks}")
    print(f"  Average Latency: {avg_latency:.2f}μs")
    print(f"  Throughput: {(total_ticks / (total_time_us / 1_000_000)):.0f} ticks/sec")
    
    # Market summary
    summary = processor.get_market_summary()
    print(f"  Symbols Tracked: {len(summary)}")
    
    return processor


def demo_monitoring():
    """Demonstrate monitoring capabilities"""
    logger.info("📊 Monitoring Demo...")
    
    config = LatencyConfig(
        target_latency_us=25,
        monitoring_interval_ms=50,
        alerting_enabled=True
    )
    
    monitor = LatencyMonitor(config)
    
    print(f"Monitoring Interval: {config.monitoring_interval_ms}ms")
    print(f"Target Latency: {config.target_latency_us}μs")
    
    # Start monitoring
    print("\n🎯 Starting Monitoring...")
    monitor.start()
    
    # Simulate some operations
    operations = [
        ('market_data', lambda: sum(range(1000))),
        ('order_processing', lambda: [x**2 for x in range(500)]),
        ('risk_check', lambda: {f'key_{i}': i**3 for i in range(200)})
    ]
    
    for i in range(15):
        op_name, op_func = operations[i % len(operations)]
        
        # Measure operation latency
        result = monitor.measure_latency(op_name, op_func)
        
        if i % 5 == 0:
            print(f"  Operation {i}: {result['latency_us']:.2f}μs ({op_name})")
        
        time.sleep(0.05)  # Small delay
    
    # Get monitoring status
    print("\n📊 Monitoring Status:")
    status = monitor.get_monitoring_status()
    print(f"  Is Monitoring: {status['is_monitoring']}")
    print(f"  Total Measurements: {status['stats']['total_measurements']}")
    
    # Get latency metrics
    latency_metrics = monitor.get_latency_metrics()
    if latency_metrics['measurement_count'] > 0:
        print(f"  Average Latency: {latency_metrics['avg_latency_us']:.2f}μs")
        print(f"  P95 Latency: {latency_metrics['p95_latency_us']:.2f}μs")
        print(f"  P99 Latency: {latency_metrics['p99_latency_us']:.2f}μs")
    
    # Stop monitoring
    monitor.stop()
    print("  Monitoring stopped")
    
    return monitor


def demo_real_time_optimization():
    """Demonstrate real-time optimization"""
    logger.info("⚡ Real-time Optimization Demo...")
    
    config = LatencyConfig(
        target_latency_us=15,
        performance_mode="ultra",
        monitoring_interval_ms=20
    )
    
    optimizer = LatencyOptimizer(config)
    
    print(f"Target Latency: {config.target_latency_us}μs")
    print(f"Mode: {config.performance_mode}")
    
    # Start optimization system
    optimizer.start_optimization(auto_optimize=True, interval_seconds=10)
    
    print("\n🚀 Starting Real-time Optimization...")
    
    # Simulate trading operations
    operation_latencies = []
    
    for i in range(30):
        start_time = time.perf_counter()
        
        # Simulate market operations
        operations = [
            lambda: sum(range(500)),
            lambda: [x**0.5 for x in range(300)],
            lambda: {'price': 100.0 + i * 0.01, 'volume': 1000 + i}
        ]
        
        operation = operations[i % len(operations)]
        result = operation()
        
        end_time = time.perf_counter()
        latency_us = (end_time - start_time) * 1_000_000
        operation_latencies.append(latency_us)
        
        # Use hot path optimization
        if hasattr(optimizer.software_optimizer, 'hot_path_optimizer'):
            hot_result = optimizer.software_optimizer.execute_hot_path(
                'price_update', 
                {'price': 100.0, 'volume': 1000}
            )
        
        # Log progress
        if i % 10 == 0:
            print(f"  Operation {i}: {latency_us:.2f}μs")
        
        time.sleep(0.02)  # 20ms intervals
    
    # Performance analysis
    import statistics
    avg_latency = statistics.mean(operation_latencies)
    p95_latency = statistics.quantiles(operation_latencies, n=20)[18]
    
    print(f"\n📊 Real-time Performance Results:")
    print(f"  Operations: {len(operation_latencies)}")
    print(f"  Average Latency: {avg_latency:.2f}μs")
    print(f"  P95 Latency: {p95_latency:.2f}μs")
    print(f"  Target Met: {avg_latency <= config.target_latency_us}")
    
    # Get system status
    status = optimizer.get_status()
    print(f"  System Health: {status['system_health']['status']}")
    
    # Stop optimization
    optimizer.stop_optimization()
    
    return optimizer, {
        'operation_latencies': operation_latencies,
        'avg_latency': avg_latency,
        'p95_latency': p95_latency
    }


def demo_comprehensive_benchmark():
    """Run comprehensive system benchmark"""
    logger.info("🏆 Comprehensive System Benchmark...")
    
    # Create optimizer
    config = LatencyConfig(
        target_latency_us=10,
        performance_mode="ultra"
    )
    
    optimizer = LatencyOptimizer(config)
    
    print("Running Complete System Benchmark...")
    print("This may take several minutes...")
    
    # Run benchmark
    start_time = time.time()
    benchmark_results = optimizer.benchmark_system()
    end_time = time.time()
    
    print(f"\n🏆 Benchmark Completed in {end_time - start_time:.1f}s")
    print(f"Overall Score: {benchmark_results['overall_score']:.1f}/100")
    
    # Show individual component scores
    components = ['network', 'hardware', 'software', 'market_data']
    for component in components:
        if component in benchmark_results and 'score' in benchmark_results[component]:
            score = benchmark_results[component]['score']
            print(f"  {component.title()} Score: {score:.1f}")
    
    return benchmark_results


def main():
    """Main demo function"""
    print("=" * 60)
    print("🚀 LATENCY OPTIMIZATION SYSTEM DEMO")
    print("=" * 60)
    print("This demo showcases the comprehensive features of the")
    print("Latency Optimization and Performance Tuning System.")
    print("=" * 60)
    
    try:
        # 1. System Readiness Check
        readiness = demo_system_readiness()
        
        # 2. Performance Profiles
        profile_manager = demo_performance_profiles()
        
        # 3. Benchmarking
        runner = demo_benchmarking()
        
        # 4. Optimization Process
        optimizer = demo_optimization()
        
        # 5. Market Data Processing
        market_processor = demo_market_data()
        
        # 6. Monitoring
        monitor = demo_monitoring()
        
        # 7. Real-time Optimization
        optimizer, real_time_results = demo_real_time_optimization()
        
        # 8. Comprehensive Benchmark (optional - takes longer)
        print("\n" + "=" * 60)
        print("Would you like to run the comprehensive benchmark? (y/n)")
        print("This will take several minutes but shows full system performance.")
        print("=" * 60)
        
        # For demo purposes, let's run it automatically
        benchmark_results = demo_comprehensive_benchmark()
        
        # Final Summary
        print("\n" + "=" * 60)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        print("\n📋 Demo Summary:")
        print(f"  ✅ System Readiness: {readiness['readiness_percent']:.1f}%")
        print(f"  ✅ Performance Profiles: {len(profile_manager.list_profiles())} available")
        print(f"  ✅ Benchmarks Run: {len(runner.benchmarks)} components")
        print(f"  ✅ Optimization Applied: {len(optimizer.get_optimization_stats().get('applied_optimizations', []))}")
        print(f"  ✅ Market Data Processed: Multiple symbols")
        print(f"  ✅ Real-time Latency: {real_time_results['avg_latency']:.2f}μs average")
        print(f"  ✅ Overall Benchmark Score: {benchmark_results.get('overall_score', 0):.1f}/100")
        
        print("\n🚀 The Latency Optimization System is ready for production use!")
        print("   Features demonstrated:")
        print("   • Ultra-low latency optimization")
        print("   • Real-time performance monitoring")
        print("   • Market data processing optimization")
        print("   • Hardware and software tuning")
        print("   • Comprehensive benchmarking")
        print("   • Automated optimization")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎯 Thank you for trying the Latency Optimization System!")
    print("   For more information, see the README.md file.")


if __name__ == "__main__":
    main()