"""
Latency Optimization System Tests
"""

import time
import pytest
import logging
from typing import Dict, Any

from latency_optimization import (
    LatencyOptimizer, LatencyConfig, NetworkConfig, HardwareConfig, SoftwareConfig,
    PerformanceProfileManager, LatencyUtils, BenchmarkRunner, SystemProfiler,
    MarketDataProcessor, MarketDataConfig, LatencyMonitor
)

# Configure logging for tests
logging.basicConfig(level=logging.INFO)


class TestLatencyOptimizer:
    """Test LatencyOptimizer class"""
    
    def test_basic_initialization(self):
        """Test basic optimizer initialization"""
        config = LatencyConfig(target_latency_us=50)
        optimizer = LatencyOptimizer(config)
        
        assert optimizer is not None
        assert optimizer.config.target_latency_us == 50
        assert not optimizer.is_running()
    
    def test_performance_profile_application(self):
        """Test performance profile application"""
        config = LatencyConfig(target_latency_us=100)
        optimizer = LatencyOptimizer(config)
        
        result = optimizer.apply_performance_profile("normal")
        
        assert result is not None
        assert isinstance(result.success, bool)
        assert isinstance(result.applied_optimizations, list)
    
    def test_optimization_stats(self):
        """Test optimization statistics"""
        config = LatencyConfig(target_latency_us=50)
        optimizer = LatencyOptimizer(config)
        
        stats = optimizer.get_optimization_stats()
        
        assert stats is not None
        assert 'total_optimizations' in stats
        assert 'success_rate' in stats
        assert isinstance(stats['total_optimizations'], int)


class TestConfiguration:
    """Test configuration management"""
    
    def test_latency_config_creation(self):
        """Test LatencyConfig creation"""
        config = LatencyConfig(
            target_latency_us=25,
            performance_mode="high"
        )
        
        assert config.target_latency_us == 25
        assert config.performance_mode == "high"
        assert config.network is not None
        assert config.hardware is not None
        assert config.software is not None
        assert config.market_data is not None
    
    def test_network_config(self):
        """Test NetworkConfig"""
        network_config = NetworkConfig(
            enable_kernel_bypass=True,
            buffer_size=65536
        )
        
        assert network_config.enable_kernel_bypass is True
        assert network_config.buffer_size == 65536
        assert 'critical' in network_config.traffic_priorities
    
    def test_hardware_config(self):
        """Test HardwareConfig"""
        hardware_config = HardwareConfig(
            cpu_affinity_enabled=True,
            numa_enabled=True,
            core_affinity_mask="0xFF"
        )
        
        assert hardware_config.cpu_affinity_enabled is True
        assert hardware_config.numa_enabled is True
        assert hardware_config.get_cpu_cores() == [0, 1, 2, 3, 4, 5, 6, 7]
    
    def test_software_config(self):
        """Test SoftwareConfig"""
        software_config = SoftwareConfig(
            zero_copy_enabled=True,
            memory_pools=True,
            hot_path_optimization=True
        )
        
        assert software_config.zero_copy_enabled is True
        assert software_config.memory_pools is True
        assert len(software_config.chunk_sizes) > 0


class TestPerformanceProfiles:
    """Test performance profiles"""
    
    def test_profile_manager_initialization(self):
        """Test PerformanceProfileManager initialization"""
        profile_manager = PerformanceProfileManager()
        profiles = profile_manager.list_profiles()
        
        assert isinstance(profiles, dict)
        assert len(profiles) > 0
        assert 'low' in profiles
        assert 'normal' in profiles
        assert 'high' in profiles
        assert 'ultra' in profiles
    
    def test_get_profile(self):
        """Test getting specific profile"""
        profile_manager = PerformanceProfileManager()
        profile = profile_manager.get_profile("ultra")
        
        assert profile is not None
        assert profile.name == "Ultra Performance"
        assert profile.target_latency_us == 10
    
    def test_custom_profile_creation(self):
        """Test custom profile creation"""
        profile_manager = PerformanceProfileManager()
        
        custom_profile = profile_manager.create_custom_profile(
            name="test_profile",
            description="Test custom profile",
            base_profile="normal",
            overrides={'target_latency_us': 15}
        )
        
        assert custom_profile is not None
        assert custom_profile.name == "test_profile"
        assert custom_profile.target_latency_us == 15
    
    def test_profile_validation(self):
        """Test profile validation"""
        profile_manager = PerformanceProfileManager()
        profile = profile_manager.get_profile("normal")
        
        validation = profile_manager.validate_profile(profile)
        
        assert 'valid' in validation
        assert 'issues' in validation
        assert isinstance(validation['issues'], list)


class TestUtilities:
    """Test utility functions"""
    
    def test_latency_utils_initialization(self):
        """Test LatencyUtils initialization"""
        utils = LatencyUtils()
        
        assert utils is not None
        assert utils._system_info is not None
        assert 'platform' in utils._system_info
    
    def test_cpu_affinity_mask_operations(self):
        """Test CPU affinity mask operations"""
        utils = LatencyUtils()
        
        # Test mask generation
        mask = utils.get_cpu_affinity_mask([0, 1, 2, 3])
        assert mask.startswith('0x')
        
        # Test mask parsing
        cpu_list = utils.parse_cpu_affinity_mask(mask)
        assert len(cpu_list) == 4
    
    def test_cache_line_alignment(self):
        """Test cache line alignment"""
        utils = LatencyUtils()
        
        aligned_size = utils.align_to_cache_line(100)
        assert aligned_size >= 100
        assert aligned_size % 64 == 0  # Default cache line size
    
    def test_function_latency_measurement(self):
        """Test function latency measurement"""
        utils = LatencyUtils()
        
        def test_function():
            return sum(range(1000))
        
        result = utils.measure_function_latency(test_function, iterations=10)
        
        assert 'avg_latency_us' in result
        assert result['avg_latency_us'] > 0
        assert result['success_rate'] > 0
    
    def test_system_requirements_check(self):
        """Test system requirements check"""
        utils = LatencyUtils()
        
        requirements = utils.check_system_requirements()
        
        assert 'checks' in requirements
        assert 'all_passed' in requirements
        assert 'recommendations' in requirements
        assert isinstance(requirements['checks'], dict)
    
    def test_benchmark_runner(self):
        """Test benchmark runner"""
        utils = LatencyUtils()
        runner = BenchmarkRunner(utils)
        
        # Test individual benchmark
        cpu_result = runner.run_benchmark('cpu_intensive', iterations=1000)
        
        assert 'time_seconds' in cpu_result or 'error' in cpu_result


class TestMarketDataProcessing:
    """Test market data processing"""
    
    def test_market_data_processor_initialization(self):
        """Test MarketDataProcessor initialization"""
        config = MarketDataConfig(tick_buffer_size=10000)
        processor = MarketDataProcessor(config)
        
        assert processor is not None
        assert processor.config.tick_buffer_size == 10000
    
    def test_tick_processing(self):
        """Test tick data processing"""
        config = MarketDataConfig()
        processor = MarketDataProcessor(config)
        
        tick_data = {
            'symbol': 'TEST',
            'bid_price': 100.0,
            'ask_price': 100.01,
            'bid_size': 1000,
            'ask_size': 1000,
            'timestamp': time.time()
        }
        
        result = processor.process_market_data(tick_data)
        
        assert result is not None
        assert 'success' in result
        assert 'processing_time_us' in result
    
    def test_batch_processing(self):
        """Test batch market data processing"""
        config = MarketDataConfig(batch_processing=True, batch_size=10)
        processor = MarketDataProcessor(config)
        
        tick_data_list = []
        for i in range(15):
            tick_data_list.append({
                'symbol': f'TEST{i}',
                'bid_price': 100.0 + i * 0.01,
                'ask_price': 100.01 + i * 0.01,
                'bid_size': 1000,
                'ask_size': 1000,
                'timestamp': time.time()
            })
        
        result = processor.batch_process_market_data(tick_data_list)
        
        assert result is not None
        assert 'total_input' in result
        assert 'total_processed' in result
    
    def test_market_summary(self):
        """Test market summary generation"""
        config = MarketDataConfig()
        processor = MarketDataProcessor(config)
        
        # Add some tick data first
        tick_data = {
            'symbol': 'TEST',
            'bid_price': 100.0,
            'ask_price': 100.01,
            'bid_size': 1000,
            'ask_size': 1000,
            'timestamp': time.time()
        }
        processor.process_market_data(tick_data)
        
        summary = processor.get_market_summary()
        
        assert summary is not None
        assert 'timestamp' in summary
        assert 'tick_statistics' in summary


class TestMonitoring:
    """Test monitoring system"""
    
    def test_latency_monitor_initialization(self):
        """Test LatencyMonitor initialization"""
        config = LatencyConfig(monitoring_interval_ms=100)
        monitor = LatencyMonitor(config)
        
        assert monitor is not None
        assert monitor.config.monitoring_interval_ms == 100
        assert not monitor._is_monitoring
    
    def test_latency_measurement(self):
        """Test latency measurement"""
        config = LatencyConfig()
        monitor = LatencyMonitor(config)
        
        def test_function():
            time.sleep(0.001)  # 1ms delay
        
        result = monitor.measure_latency('test_operation', test_function)
        
        assert result is not None
        assert 'success' in result
        assert 'latency_us' in result
        assert result['latency_us'] > 0
    
    def test_monitoring_start_stop(self):
        """Test monitoring start/stop"""
        config = LatencyConfig(monitoring_interval_ms=50)
        monitor = LatencyMonitor(config)
        
        # Start monitoring
        monitor.start()
        assert monitor._is_monitoring
        
        # Wait a bit for monitoring loop
        time.sleep(0.1)
        
        # Stop monitoring
        monitor.stop()
        assert not monitor._is_monitoring


class TestSystemProfiler:
    """Test system profiler"""
    
    def test_profiler_initialization(self):
        """Test SystemProfiler initialization"""
        profiler = SystemProfiler()
        
        assert profiler is not None
        assert profiler.utils is not None
    
    def test_system_info(self):
        """Test system info retrieval"""
        profiler = SystemProfiler()
        
        system_info = profiler.get_detailed_system_info()
        
        assert system_info is not None
        assert 'platform' in system_info
        assert 'cpu_count_logical' in system_info
        assert 'memory_total_gb' in system_info
    
    def test_optimization_readiness(self):
        """Test optimization readiness check"""
        profiler = SystemProfiler()
        
        readiness = profiler.check_optimization_readiness()
        
        assert readiness is not None
        assert 'readiness_score' in readiness
        assert 'max_score' in readiness
        assert 'readiness_percent' in readiness
        assert 0 <= readiness['readiness_percent'] <= 100


def test_integration():
    """Integration test for complete workflow"""
    # Create comprehensive configuration
    config = LatencyConfig(
        target_latency_us=25,
        performance_mode="high",
        monitoring_interval_ms=100,
        alerting_enabled=True
    )
    
    # Initialize optimizer
    optimizer = LatencyOptimizer(config)
    
    # Test basic functionality
    assert optimizer is not None
    
    # Apply performance profile
    result = optimizer.apply_performance_profile("normal")
    assert result is not None
    
    # Get status
    status = optimizer.get_status()
    assert status is not None
    assert 'is_running' in status
    
    print("Integration test passed!")


def test_performance_comparison():
    """Test performance comparison"""
    utils = LatencyUtils()
    
    # Create test functions with different characteristics
    def fast_function():
        return sum(range(100))
    
    def slow_function():
        result = 0
        for i in range(10000):
            result += i ** 0.5
        return result
    
    # Measure performance
    fast_result = utils.measure_function_latency(fast_function, iterations=100)
    slow_result = utils.measure_function_latency(slow_function, iterations=10)
    
    # Fast function should be faster
    assert fast_result['avg_latency_us'] < slow_result['avg_latency_us']
    
    print("Performance comparison test passed!")


if __name__ == "__main__":
    # Run basic tests
    print("Running Latency Optimization System Tests...")
    
    test_integration()
    test_performance_comparison()
    
    # Run specific test classes
    test_classes = [
        TestLatencyOptimizer,
        TestConfiguration,
        TestPerformanceProfiles,
        TestUtilities,
        TestMarketDataProcessing,
        TestMonitoring,
        TestSystemProfiler
    ]
    
    for test_class in test_classes:
        try:
            print(f"\nRunning {test_class.__name__} tests...")
            test_instance = test_class()
            
            # Run all test methods
            for method_name in dir(test_instance):
                if method_name.startswith('test_'):
                    method = getattr(test_instance, method_name)
                    method()
                    print(f"  ✓ {method_name}")
            
            print(f"All {test_class.__name__} tests passed!")
            
        except Exception as e:
            print(f"❌ {test_class.__name__} tests failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 All tests completed!")