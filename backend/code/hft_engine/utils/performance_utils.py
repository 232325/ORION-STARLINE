"""
Performance Utilities
====================

High-performance utilities for monitoring and optimization
"""

import time
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from collections import deque
import statistics

@dataclass
class PerformanceMetric:
    """Performance metric"""
    name: str
    value: float
    timestamp: float
    unit: str = ""
    category: str = "general"

class PerformanceProfiler:
    """High-performance profiling utility"""
    
    def __init__(self, max_samples: int = 1000):
        self.max_samples = max_samples
        self.metrics: Dict[str, deque] = {}
        self.lock = threading.RLock()
        self.start_time = time.perf_counter()
    
    def record_metric(self, name: str, value: float, unit: str = "", category: str = "general"):
        """Record a performance metric"""
        with self.lock:
            metric = PerformanceMetric(
                name=name,
                value=value,
                timestamp=time.time(),
                unit=unit,
                category=category
            )
            
            if name not in self.metrics:
                self.metrics[name] = deque(maxlen=self.max_samples)
            
            self.metrics[name].append(metric)
    
    def record_function_execution(self, func: Callable, *args, **kwargs):
        """Profile function execution"""
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.perf_counter() - start_time
            
            self.record_metric(
                f"{func.__name__}_execution_time",
                execution_time * 1_000_000,  # Convert to microseconds
                "μs",
                "execution"
            )
            
            return result
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            
            self.record_metric(
                f"{func.__name__}_execution_error",
                execution_time * 1_000_000,
                "μs",
                "error"
            )
            
            raise e
    
    def get_metric_statistics(self, name: str) -> Dict[str, float]:
        """Get statistics for a specific metric"""
        with self.lock:
            if name not in self.metrics or not self.metrics[name]:
                return {}
            
            values = [m.value for m in self.metrics[name]]
            
            return {
                'count': len(values),
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'min': min(values),
                'max': max(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
                'latest': values[-1],
                'first': values[0]
            }
    
    def get_all_statistics(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all metrics"""
        return {name: self.get_metric_statistics(name) for name in self.metrics}
    
    def get_system_performance(self) -> Dict[str, float]:
        """Get current system performance metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'network_io': dict(psutil.net_io_counters()._asdict()) if psutil.net_io_counters() else {},
            'process_memory_mb': psutil.Process().memory_info().rss / 1024 / 1024,
            'process_cpu_percent': psutil.Process().cpu_percent()
        }

class MemoryProfiler:
    """Memory usage profiling utility"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.start_memory = self.process.memory_info().rss
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage"""
        memory_info = self.process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': self.process.memory_percent(),
            'start_memory_mb': self.start_memory / 1024 / 1024,
            'delta_mb': (memory_info.rss - self.start_memory) / 1024 / 1024
        }
    
    def get_memory_breakdown(self) -> Dict[str, int]:
        """Get detailed memory breakdown"""
        try:
            with open(f'/proc/{self.process.pid}/status') as f:
                status = f.read()
            
            breakdown = {}
            for line in status.split('\n'):
                if line.startswith('Vm'):
                    parts = line.split(':')
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip().split()[0]  # Remove 'kB'
                        breakdown[key] = int(value) * 1024  # Convert to bytes
            
            return breakdown
        except:
            return {}

class BenchmarkTool:
    """Performance benchmarking utility"""
    
    def __init__(self):
        self.results = {}
    
    def benchmark_function(self, func: Callable, iterations: int = 1000, *args, **kwargs):
        """Benchmark a function"""
        # Warm-up run
        func(*args, **kwargs)
        
        # Actual benchmark
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            result = func(*args, **kwargs)
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        results = {
            'total_time_s': total_time,
            'avg_time_us': (total_time / iterations) * 1_000_000,
            'iterations': iterations,
            'throughput_per_sec': iterations / total_time,
            'function_name': func.__name__
        }
        
        self.results[func.__name__] = results
        return results
    
    def compare_benchmarks(self) -> Dict[str, Any]:
        """Compare all benchmark results"""
        if not self.results:
            return {}
        
        # Sort by throughput
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1]['throughput_per_sec'],
            reverse=True
        )
        
        fastest = sorted_results[0]
        slowest = sorted_results[-1]
        
        return {
            'results': self.results,
            'fastest': {
                'function': fastest[0],
                'throughput': fastest[1]['throughput_per_sec']
            },
            'slowest': {
                'function': slowest[0],
                'throughput': slowest[1]['throughput_per_sec']
            },
            'speedup_factor': slowest[1]['throughput_per_sec'] / fastest[1]['throughput_per_sec']
        }