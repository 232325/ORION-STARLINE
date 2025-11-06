"""
Latency Optimization System Example Usage
Comprehensive example demonstrating all features of the latency optimization system.
"""

import time
import json
import logging
from typing import Dict, Any

# Import the latency optimization system
from latency_optimization import (
    LatencyOptimizer, LatencyConfig, NetworkConfig, HardwareConfig, SoftwareConfig,
    PerformanceProfileManager, LatencyUtils, BenchmarkRunner, SystemProfiler
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_basic_usage():
    """Basic usage example"""
    logger.info("=== Basic Usage Example ===")
    
    # 1. Create configuration
    config = LatencyConfig(
        target_latency_us=10,
        performance_mode="high"
    )
    
    # 2. Initialize optimizer
    optimizer = LatencyOptimizer(config)
    
    # 3. Start optimization
    optimizer.start_optimization(auto_optimize=True)
    
    # 4. Apply performance profile
    result = optimizer.apply_performance_profile("ultra")
    logger.info(f"Profile application result: {result.success}")
    
    # 5. Get current metrics
    metrics = optimizer.get_current_metrics()
    if metrics:
        logger.info(f"Current latency: {metrics.average_latency_us:.2f}μs")
        logger.info(f"Target latency: {config.target_latency_us}μs")
    
    # 6. Stop optimization
    optimizer.stop_optimization()
    
    return optimizer


def example_performance_profiles():
    """Performance profiles example"""
    logger.info("=== Performance Profiles Example ===")
    
    # Create profile manager
    profile_manager = PerformanceProfileManager()
    
    # List available profiles
    profiles = profile_manager.list_profiles()
    logger.info(f"Available profiles: {list(profiles.keys())}")
    
    # Create custom profile
    custom_profile = profile_manager.create_custom_profile(
        name="custom_trading",
        description="Custom profile for trading systems",
        base_profile="high",
        overrides={
            'target_latency_us': 5,
            'network_config': {
                'buffer_size': 262144,
                'tx_queue_count': 16,
                'rx_queue_count': 16
            },
            'software_config': {
                'memory_pool_size': 2 * 1024 * 1024 * 1024,  # 2GB
                'zero_copy_enabled': True,
                'lock_free_algorithms': True
            }
        }
    )
    
    logger.info(f"Created custom profile: {custom_profile.name}")
    
    # Validate profile
    validation = profile_manager.validate_profile(custom_profile)
    logger.info(f"Profile validation: {validation}")


def example_system_monitoring():
    """System monitoring example"""
    logger.info("=== System Monitoring Example ===")
    
    # Create configuration
    config = LatencyConfig(
        target_latency_us=25,
        monitoring_interval_ms=50,  # Monitor every 50ms
        alerting_enabled=True
    )
    
    # Initialize optimizer
    optimizer = LatencyOptimizer(config)
    
    # Start monitoring
    optimizer.start_optimization(auto_optimize=False)
    
    # Simulate some operations
    for i in range(10):
        # Simulate market data processing
        import random
        latency = random.uniform(10, 50)
        
        # Use optimizer's latency measurement
        result = optimizer.latency_monitor.measure_latency(
            'market_data_processing',
            lambda: time.sleep(latency / 1_000_000)
        )
        
        logger.info(f"Operation {i}: {result['latency_us']:.2f}μs")
        time.sleep(0.1)
    
    # Get monitoring status
    status = optimizer.latency_monitor.get_monitoring_status()
    logger.info(f"Monitoring status: {isinstance(status, dict)}")
    
    # Get performance alerts
    alerts = optimizer.latency_monitor.get_performance_alerts(count=5)
    logger.info(f"Active alerts: {len(alerts)}")
    
    # Stop monitoring
    optimizer.stop_optimization()


def example_benchmarking():
    """Benchmarking example"""
    logger.info("=== Benchmarking Example ===")
    
    # Create system profiler
    profiler = SystemProfiler()
    
    # Check system readiness
    readiness = profiler.check_optimization_readiness()
    logger.info(f"System readiness score: {readiness['readiness_percent']:.1f}%")
    
    # Get detailed system info
    system_info = profiler.get_detailed_system_info()
    logger.info(f"System info: {system_info['platform']}")
    
    # Create benchmark runner
    utils = LatencyUtils()
    runner = BenchmarkRunner(utils)
    
    # Run individual benchmarks
    logger.info("Running CPU benchmark...")
    cpu_result = runner.run_benchmark('cpu_intensive', iterations=100000)
    logger.info(f"CPU benchmark: {cpu_result.get('ops_per_second', 0):.0f} ops/sec")
    
    logger.info("Running memory benchmark...")
    memory_result = runner.run_benchmark('memory_bandwidth', size_mb=50)
    logger.info(f"Memory bandwidth: {memory_result.get('read_write_bandwidth_mbps', 0):.1f} MB/s")
    
    # Run all benchmarks
    logger.info("Running complete benchmark suite...")
    all_results = runner.run_all_benchmarks()
    
    # Save results
    runner.save_results('/tmp/latency_benchmark_results.json')
    
    return all_results


def example_market_data_processing():
    """Market data processing example"""
    logger.info("=== Market Data Processing Example ===")
    
    from latency_optimization import MarketDataProcessor, MarketDataConfig
    
    # Create market data config
    market_config = MarketDataConfig(
        tick_buffer_size=50000,
        order_book_levels=20,
        max_symbols=1000,
        batch_processing=True,
        batch_size=1000
    )
    
    # Initialize processor
    processor = MarketDataProcessor(market_config)
    
    # Simulate market data updates
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
    
    for i in range(100):
        symbol = symbols[i % len(symbols)]
        
        # Simulate tick data
        tick_data = {
            'symbol': symbol,
            'bid_price': 150.0 + i * 0.01,
            'ask_price': 150.01 + i * 0.01,
            'bid_size': 1000,
            'ask_size': 1000,
            'timestamp': time.time(),
            'volume': i * 100
        }
        
        # Process market data
        result = processor.process_market_data(tick_data)
        
        if i % 20 == 0:  # Log every 20th operation
            logger.info(f"Processed tick {i}: {result.get('processing_time_us', 0):.2f}μs")
    
    # Get market summary
    summary = processor.get_market_summary()
    logger.info(f"Market summary: {len(summary)} symbols tracked")
    
    # Run optimization
    optimization_result = processor.optimize()
    logger.info(f"Market data optimization: {optimization_result.get('applied_optimizations', [])}")
    
    return processor


def example_custom_configuration():
    """Custom configuration example"""
    logger.info("=== Custom Configuration Example ===")
    
    # Create custom network configuration
    network_config = NetworkConfig(
        enable_kernel_bypass=True,
        enable_user_space_tcp=True,
        network_interface="eth0",
        buffer_size=131072,
        tx_queue_count=8,
        rx_queue_count=8,
        qos_enabled=True,
        traffic_priorities={
            'critical': 1,
            'orders': 2,
            'market_data': 3,
            'heartbeat': 4,
            'info': 5
        }
    )
    
    # Create custom hardware configuration
    hardware_config = HardwareConfig(
        cpu_affinity_enabled=True,
        numa_enabled=True,
        core_affinity_mask="0xFF",  # Use first 8 cores
        memory_preallocation=True,
        cache_friendly_structures=True,
        simd_enabled=True,
        parallel_processing=True,
        memory_limit_gb=32
    )
    
    # Create custom software configuration
    software_config = SoftwareConfig(
        zero_copy_enabled=True,
        lock_free_algorithms=True,
        memory_pools=True,
        pre_allocation=True,
        hot_path_optimization=True,
        memory_pool_size=1024 * 1024 * 1024,  # 1GB
        atomic_operations=True,
        chunk_sizes=[64, 128, 256, 512, 1024, 2048, 4096, 8192]
    )
    
    # Combine into main configuration
    config = LatencyConfig(
        network=network_config,
        hardware=hardware_config,
        software=software_config,
        target_latency_us=10,
        performance_mode="ultra",
        monitoring_interval_ms=100
    )
    
    # Validate configuration
    from latency_optimization import ConfigManager
    config_manager = ConfigManager()
    config_manager.config = config
    
    validation = config_manager.validate_config()
    logger.info(f"Configuration validation: {validation}")
    
    # Save configuration
    config_manager.save_config('/tmp/latency_config.json')
    
    return config


def example_real_time_optimization():
    """Real-time optimization example"""
    logger.info("=== Real-time Optimization Example ===")
    
    # Create configuration for ultra-low latency
    config = LatencyConfig(
        target_latency_us=5,
        performance_mode="ultra",
        monitoring_interval_ms=10,  # Very frequent monitoring
        alerting_enabled=True
    )
    
    # Initialize optimizer
    optimizer = LatencyOptimizer(config)
    
    # Start optimization
    optimizer.start_optimization(auto_optimize=True, interval_seconds=30)
    
    # Simulate trading operations
    logger.info("Starting trading simulation...")
    
    for i in range(50):
        # Simulate market data processing
        start_time = time.perf_counter()
        
        # Simulate some processing
        market_data = {
            'symbol': f'SYM{i % 10}',
            'price': 100.0 + i * 0.001,
            'volume': 1000 + i
        }
        
        # Use hot path optimization
        result = optimizer.software_optimizer.execute_hot_path(
            'price_update', market_data
        )
        
        end_time = time.perf_counter()
        operation_latency = (end_time - start_time) * 1_000_000  # microseconds
        
        # Log performance
        if i % 10 == 0:
            current_metrics = optimizer.get_current_metrics()
            if current_metrics:
                logger.info(f"Operation {i}: {operation_latency:.2f}μs, "
                          f"Avg latency: {current_metrics.latency['avg_latency_us']:.2f}μs")
        
        # Small delay to simulate market timing
        time.sleep(0.01)
    
    # Get optimization statistics
    stats = optimizer.get_optimization_stats()
    logger.info(f"Optimization statistics: {stats['total_optimizations']} optimizations applied")
    
    # Get current status
    status = optimizer.get_status()
    logger.info(f"System health: {status['system_health']['status']}")
    
    # Stop optimization
    optimizer.stop_optimization()
    
    return optimizer


def example_performance_analysis():
    """Performance analysis example"""
    logger.info("=== Performance Analysis Example ===")
    
    # Create optimizer with monitoring
    config = LatencyConfig(
        target_latency_us=25,
        monitoring_interval_ms=100,
        alerting_enabled=True
    )
    
    optimizer = LatencyOptimizer(config)
    optimizer.start_optimization(auto_optimize=False)
    
    # Run performance test
    logger.info("Running performance test...")
    
    latencies = []
    for i in range(100):
        start_time = time.perf_counter()
        
        # Simulate various operations
        operations = [
            lambda: sum(range(1000)),
            lambda: [x**2 for x in range(100)],
            lambda: {f'key_{i}': i**2 for i in range(50)}
        ]
        
        operation = operations[i % len(operations)]
        operation()
        
        end_time = time.perf_counter()
        latency_us = (end_time - start_time) * 1_000_000
        latencies.append(latency_us)
    
    # Analyze results
    import statistics
    
    avg_latency = statistics.mean(latencies)
    p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
    p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
    
    logger.info(f"Performance Analysis Results:")
    logger.info(f"  Average latency: {avg_latency:.2f}μs")
    logger.info(f"  95th percentile: {p95_latency:.2f}μs")
    logger.info(f"  99th percentile: {p99_latency:.2f}μs")
    logger.info(f"  Target latency: {config.target_latency_us}μs")
    
    # Check if we meet targets
    if avg_latency <= config.target_latency_us:
        logger.info("✅ Performance target achieved!")
    else:
        logger.warning("⚠️ Performance target not met, optimization recommended")
    
    # Run system benchmark
    logger.info("Running comprehensive system benchmark...")
    benchmark_results = optimizer.benchmark_system()
    logger.info(f"Overall benchmark score: {benchmark_results['overall_score']:.1f}")
    
    optimizer.stop_optimization()
    
    return {
        'latencies': latencies,
        'avg_latency': avg_latency,
        'p95_latency': p95_latency,
        'p99_latency': p99_latency,
        'benchmark_results': benchmark_results
    }


def main():
    """Main example function demonstrating all features"""
    logger.info("Starting Latency Optimization System Examples")
    
    try:
        # Run all examples
        example_basic_usage()
        example_performance_profiles()
        example_system_monitoring()
        example_benchmarking()
        example_market_data_processing()
        example_custom_configuration()
        example_real_time_optimization()
        example_performance_analysis()
        
        logger.info("All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Example execution failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()