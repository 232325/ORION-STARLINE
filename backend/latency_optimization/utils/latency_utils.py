"""
Latency Optimization Utilities Module
"""

import time
import threading
import ctypes
import ctypes.util
import platform
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceTimer:
    """Performance timer for measuring execution time"""
    name: str
    start_time: float = 0.0
    end_time: float = 0.0
    duration_us: float = 0.0
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        self.duration_us = (self.end_time - self.start_time) * 1_000_000
        logger.debug(f"Timer '{self.name}': {self.duration_us:.2f}μs")


@dataclass
class CpuTime:
    """CPU time measurement"""
    user_time: float
    system_time: float
    total_time: float
    timestamp: float


class LatencyUtils:
    """Utility functions for latency optimization"""
    
    def __init__(self):
        self._system_info = self._detect_system_capabilities()
    
    def _detect_system_capabilities(self) -> Dict[str, Any]:
        """Detect system capabilities for optimization"""
        return {
            'platform': platform.system(),
            'architecture': platform.architecture(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'cpu_count': platform.cpu_count(),
            'available_optimizations': []
        }
    
    def get_cpu_affinity_mask(self, cpu_list: List[int]) -> str:
        """Generate CPU affinity mask from CPU list"""
        if not cpu_list:
            return "0x1"  # Default to first CPU
        
        mask = 0
        for cpu in cpu_list:
            if 0 <= cpu < 64:  # Support up to 64 CPUs
                mask |= (1 << cpu)
        
        return f"0x{mask:016x}"
    
    def parse_cpu_affinity_mask(self, mask_str: str) -> List[int]:
        """Parse CPU affinity mask to get CPU list"""
        try:
            if mask_str.startswith('0x'):
                mask = int(mask_str, 16)
                cpus = []
                for i in range(64):
                    if mask & (1 << i):
                        cpus.append(i)
                return cpus
            else:
                # Parse comma-separated or range format
                cpus = []
                for part in mask_str.split(','):
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        cpus.extend(range(start, end + 1))
                    else:
                        cpus.append(int(part))
                return cpus
        except Exception as e:
            logger.error(f"Failed to parse CPU affinity mask {mask_str}: {e}")
            return [0]  # Default to first CPU
    
    def align_to_cache_line(self, size: int, cache_line_size: int = 64) -> int:
        """Align size to cache line boundary"""
        return (size + cache_line_size - 1) & ~(cache_line_size - 1)
    
    def get_memory_alignment(self) -> int:
        """Get optimal memory alignment for current platform"""
        if self._system_info['platform'] == 'Windows':
            return 64  # Windows typically uses 64-byte alignment
        else:
            # Unix-like systems
            try:
                # Try to get page size
                import os
                return os.sysconf('SC_PAGESIZE')
            except:
                return 4096  # Default to 4KB pages
    
    def get_hardware_timestamp(self) -> int:
        """Get high-resolution hardware timestamp"""
        try:
            if self._system_info['platform'] == 'Windows':
                # Use Windows performance counter
                return int(time.perf_counter() * 1_000_000_000)  # Nanoseconds
            else:
                # Use Unix time with nanosecond precision
                return int(time.time_ns())  # Nanoseconds since epoch
        except AttributeError:
            # Fallback for older Python versions
            return int(time.time() * 1_000_000_000)
    
    def measure_function_latency(self, func: Callable, *args, iterations: int = 1000, **kwargs) -> Dict[str, float]:
        """Measure function execution latency over multiple iterations"""
        latencies = []
        results = []
        
        # Warm up
        for _ in range(min(10, iterations // 10)):
            try:
                func(*args, **kwargs)
            except:
                pass
        
        # Actual measurement
        for _ in range(iterations):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                
                latency_us = (end_time - start_time) * 1_000_000
                latencies.append(latency_us)
                results.append(result)
                
            except Exception as e:
                logger.error(f"Function measurement failed: {e}")
                continue
        
        if not latencies:
            return {'error': 'No successful measurements'}
        
        return {
            'iterations': len(latencies),
            'avg_latency_us': sum(latencies) / len(latencies),
            'min_latency_us': min(latencies),
            'max_latency_us': max(latencies),
            'p50_latency_us': sorted(latencies)[len(latencies) // 2],
            'p95_latency_us': sorted(latencies)[int(len(latencies) * 0.95)],
            'p99_latency_us': sorted(latencies)[int(len(latencies) * 0.99)],
            'success_rate': len(latencies) / iterations
        }
    
    def optimize_array_access(self, data: list, pattern: str = 'sequential') -> Any:
        """Optimize array access pattern"""
        import numpy as np
        
        if pattern == 'sequential':
            # Sequential access - good for cache
            return np.array(data)
        elif pattern == 'random':
            # Random access - consider alternative structures
            return np.array(data)
        else:
            # Default to sequential
            return np.array(data)
    
    def create_cache_friendly_structure(self, data_size: int, access_pattern: str = 'sequential') -> Dict[str, Any]:
        """Create cache-friendly data structures"""
        import numpy as np
        
        # Calculate optimal structure
        cache_line_size = 64
        element_size = 8  # Assuming 8-byte elements (float64)
        
        if access_pattern == 'sequential':
            # Use contiguous arrays
            aligned_size = self.align_to_cache_line(data_size * element_size)
            structure = {
                'type': 'contiguous_array',
                'size': aligned_size,
                'alignment': cache_line_size,
                'data': np.zeros(aligned_size // element_size)
            }
        else:
            # Use structure of arrays for better cache utilization
            structure = {
                'type': 'structure_of_arrays',
                'size': data_size,
                'data': [np.zeros(data_size) for _ in range(3)]  # Example: 3 fields
            }
        
        return structure
    
    def get_optimal_thread_pool_size(self, cpu_count: Optional[int] = None) -> int:
        """Get optimal thread pool size"""
        if cpu_count is None:
            cpu_count = platform.cpu_count()
        
        # For CPU-bound tasks: use CPU count
        # For I/O-bound tasks: use 2 * CPU count
        # For latency-critical tasks: use CPU count + a few extra
        
        if hasattr(self, 'task_type'):
            if self.task_type == 'cpu_bound':
                return cpu_count
            elif self.task_type == 'io_bound':
                return cpu_count * 2
            else:
                return cpu_count + 2
        else:
            return cpu_count  # Default to CPU count
    
    def set_process_priority(self, priority: str = 'high') -> bool:
        """Set process priority"""
        try:
            import psutil
            process = psutil.Process()
            
            if priority == 'high':
                process.nice(psutil.HIGH_PRIORITY_CLASS if hasattr(psutil, 'HIGH_PRIORITY_CLASS') else -10)
            elif priority == 'normal':
                process.nice(psutil.NORMAL_PRIORITY_CLASS if hasattr(psutil, 'NORMAL_PRIORITY_CLASS') else 0)
            elif priority == 'low':
                process.nice(psutil.IDLE_PRIORITY_CLASS if hasattr(psutil, 'IDLE_PRIORITY_CLASS') else 19)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set process priority: {e}")
            return False
    
    def get_system_load_average(self) -> Optional[tuple]:
        """Get system load average"""
        try:
            if hasattr(os, 'getloadavg'):
                return os.getloadavg()  # Unix systems
            else:
                # Windows doesn't have load average, return CPU usage instead
                import psutil
                return (psutil.cpu_percent(), psutil.cpu_percent(), psutil.cpu_percent())
        except:
            return None
    
    def benchmark_memory_access(self, size_mb: int = 100) -> Dict[str, float]:
        """Benchmark memory access patterns"""
        import numpy as np
        
        size_bytes = size_mb * 1024 * 1024
        array_size = size_bytes // 8  # float64
        
        # Sequential access benchmark
        data = np.random.random(array_size)
        start_time = time.perf_counter()
        
        sequential_sum = 0
        for i in range(array_size):
            sequential_sum += data[i]
        
        sequential_time = time.perf_counter() - start_time
        
        # Random access benchmark
        indices = np.random.choice(array_size, array_size // 10, replace=False)
        start_time = time.perf_counter()
        
        random_sum = 0
        for idx in indices:
            random_sum += data[idx]
        
        random_time = time.perf_counter() - start_time
        
        return {
            'size_mb': size_mb,
            'sequential_access_time': sequential_time,
            'random_access_time': random_time,
            'sequential_throughput_mbps': (size_mb / sequential_time),
            'random_throughput_mbps': (size_mb / random_time),
            'random_vs_sequential_ratio': random_time / sequential_time
        }
    
    def check_system_requirements(self) -> Dict[str, Any]:
        """Check if system meets requirements for latency optimization"""
        import psutil
        
        checks = {
            'cpu_count': psutil.cpu_count() >= 4,
            'memory_gb': psutil.virtual_memory().total / (1024**3) >= 8,
            'platform_support': self._system_info['platform'] in ['Linux', 'Windows', 'Darwin'],
            'python_version': platform.python_version() >= '3.7'
        }
        
        recommendations = []
        
        if not checks['cpu_count']:
            recommendations.append("Consider using a system with at least 4 CPU cores")
        
        if not checks['memory_gb']:
            recommendations.append("Consider using a system with at least 8GB RAM")
        
        if self._system_info['platform'] == 'Linux':
            recommendations.append("Linux provides best support for advanced optimizations")
        elif self._system_info['platform'] == 'Windows':
            recommendations.append("Windows may have limited support for some advanced optimizations")
        elif self._system_info['platform'] == 'Darwin':
            recommendations.append("macOS may have limited support for some advanced optimizations")
        
        return {
            'checks': checks,
            'all_passed': all(checks.values()),
            'recommendations': recommendations,
            'system_info': self._system_info
        }
    
    def create_benchmark_suite(self) -> Dict[str, Callable]:
        """Create a comprehensive benchmark suite"""
        benchmarks = {
            'cpu_intensive': self._benchmark_cpu_intensive,
            'memory_bandwidth': self._benchmark_memory_bandwidth,
            'cache_performance': self._benchmark_cache_performance,
            'network_latency': self._benchmark_network_latency,
            'disk_io': self._benchmark_disk_io
        }
        
        return benchmarks
    
    def _benchmark_cpu_intensive(self, iterations: int = 1000000) -> Dict[str, float]:
        """CPU-intensive benchmark"""
        import math
        
        start_time = time.perf_counter()
        
        result = 0
        for i in range(iterations):
            result += math.sqrt(i) * math.sin(i) * math.cos(i)
        
        end_time = time.perf_counter()
        
        return {
            'iterations': iterations,
            'time_seconds': end_time - start_time,
            'ops_per_second': iterations / (end_time - start_time),
            'result': result
        }
    
    def _benchmark_memory_bandwidth(self, size_mb: int = 100) -> Dict[str, float]:
        """Memory bandwidth benchmark"""
        import numpy as np
        
        size_bytes = size_mb * 1024 * 1024
        array_size = size_bytes // 8  # float64
        
        data = np.random.random(array_size)
        
        # Sequential read/write
        start_time = time.perf_counter()
        for i in range(array_size):
            data[i] = data[i] * 2.0
        
        read_write_time = time.perf_counter() - start_time
        
        # Just read
        start_time = time.perf_counter()
        read_sum = np.sum(data)
        read_time = time.perf_counter() - start_time
        
        return {
            'size_mb': size_mb,
            'read_write_time': read_write_time,
            'read_time': read_time,
            'read_write_bandwidth_mbps': size_mb / read_write_time,
            'read_bandwidth_mbps': size_mb / read_time,
            'read_sum': float(read_sum)
        }
    
    def _benchmark_cache_performance(self, iterations: int = 10000000) -> Dict[str, float]:
        """Cache performance benchmark"""
        import numpy as np
        
        # Test different array sizes for cache behavior
        sizes = [1024, 4096, 16384, 65536]
        results = {}
        
        for size in sizes:
            data = np.random.random(size)
            
            start_time = time.perf_counter()
            sum_result = 0
            for _ in range(iterations // size):
                for i in range(size):
                    sum_result += data[i]
            
            end_time = time.perf_counter()
            
            results[f'size_{size}'] = {
                'time_seconds': end_time - start_time,
                'iterations': iterations // size,
                'total_accesses': size * (iterations // size),
                'avg_access_time_ns': ((end_time - start_time) * 1_000_000_000) / (size * (iterations // size))
            }
        
        return results
    
    def _benchmark_network_latency(self, test_host: str = "8.8.8.8") -> Dict[str, float]:
        """Network latency benchmark"""
        import subprocess
        import statistics
        
        try:
            # Ping test
            if platform.system() == 'Windows':
                cmd = ['ping', '-n', '10', test_host]
            else:
                cmd = ['ping', '-c', '10', test_host]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse ping results
                lines = result.stdout.split('\n')
                times = []
                for line in lines:
                    if 'time=' in line or 'ms' in line:
                        # Extract time value
                        if 'time=' in line:
                            time_str = line.split('time=')[1].split()[0]
                        else:
                            time_str = line.split('ms')[0].split()[-1]
                        
                        try:
                            times.append(float(time_str))
                        except:
                            pass
                
                if times:
                    return {
                        'test_host': test_host,
                        'ping_count': len(times),
                        'avg_latency_ms': statistics.mean(times),
                        'min_latency_ms': min(times),
                        'max_latency_ms': max(times),
                        'std_latency_ms': statistics.stdev(times) if len(times) > 1 else 0
                    }
            
        except Exception as e:
            logger.error(f"Network benchmark failed: {e}")
        
        return {'error': 'Network benchmark failed'}
    
    def _benchmark_disk_io(self, size_mb: int = 100) -> Dict[str, float]:
        """Disk I/O benchmark"""
        import tempfile
        import os
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                file_path = tmp.name
            
            # Write test
            start_time = time.perf_counter()
            with open(file_path, 'wb') as f:
                data = b'0' * (size_mb * 1024 * 1024)
                f.write(data)
            
            write_time = time.perf_counter() - start_time
            
            # Read test
            start_time = time.perf_counter()
            with open(file_path, 'rb') as f:
                read_data = f.read()
            
            read_time = time.perf_counter() - start_time
            
            # Cleanup
            os.unlink(file_path)
            
            return {
                'size_mb': size_mb,
                'write_time': write_time,
                'read_time': read_time,
                'write_bandwidth_mbps': size_mb / write_time,
                'read_bandwidth_mbps': size_mb / read_time
            }
            
        except Exception as e:
            logger.error(f"Disk I/O benchmark failed: {e}")
            return {'error': 'Disk I/O benchmark failed'}


class BenchmarkRunner:
    """Benchmark runner utility"""
    
    def __init__(self, utils: LatencyUtils):
        self.utils = utils
        self.benchmarks = utils.create_benchmark_suite()
        self.results = {}
    
    def run_benchmark(self, benchmark_name: str, **kwargs) -> Dict[str, Any]:
        """Run a specific benchmark"""
        if benchmark_name not in self.benchmarks:
            raise ValueError(f"Unknown benchmark: {benchmark_name}")
        
        logger.info(f"Running benchmark: {benchmark_name}")
        
        try:
            result = self.benchmarks[benchmark_name](**kwargs)
            self.results[benchmark_name] = result
            logger.info(f"Benchmark {benchmark_name} completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Benchmark {benchmark_name} failed: {e}")
            return {'error': str(e)}
    
    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all available benchmarks"""
        logger.info("Running all benchmarks")
        
        all_results = {}
        for benchmark_name in self.benchmarks.keys():
            try:
                result = self.run_benchmark(benchmark_name)
                all_results[benchmark_name] = result
            except Exception as e:
                all_results[benchmark_name] = {'error': str(e)}
        
        return all_results
    
    def get_results(self) -> Dict[str, Any]:
        """Get all benchmark results"""
        return self.results.copy()
    
    def save_results(self, file_path: str):
        """Save benchmark results to file"""
        import json
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"Benchmark results saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save benchmark results: {e}")
    
    def load_results(self, file_path: str):
        """Load benchmark results from file"""
        import json
        
        try:
            with open(file_path, 'r') as f:
                self.results = json.load(f)
            logger.info(f"Benchmark results loaded from {file_path}")
        except Exception as e:
            logger.error(f"Failed to load benchmark results: {e}")


class SystemProfiler:
    """System profiling and analysis"""
    
    def __init__(self):
        self.utils = LatencyUtils()
    
    def get_detailed_system_info(self) -> Dict[str, Any]:
        """Get detailed system information"""
        import psutil
        import platform
        
        # Basic system info
        system_info = {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'python_version': platform.python_version(),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'cpu_count_physical': psutil.cpu_count(logical=False),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'memory_available_gb': psutil.virtual_memory().available / (1024**3)
        }
        
        # CPU information
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                system_info['cpu_frequency_mhz'] = {
                    'current': cpu_freq.current,
                    'min': cpu_freq.min,
                    'max': cpu_freq.max
                }
        except:
            pass
        
        # System load
        load_avg = self.utils.get_system_load_average()
        if load_avg:
            system_info['load_average'] = load_avg
        
        # Network interfaces
        try:
            network_interfaces = psutil.net_if_addrs()
            system_info['network_interfaces'] = list(network_interfaces.keys())
        except:
            pass
        
        # Disk information
        try:
            disk_usage = psutil.disk_usage('/')
            system_info['disk'] = {
                'total_gb': disk_usage.total / (1024**3),
                'used_gb': disk_usage.used / (1024**3),
                'free_gb': disk_usage.free / (1024**3),
                'usage_percent': (disk_usage.used / disk_usage.total) * 100
            }
        except:
            pass
        
        return system_info
    
    def check_optimization_readiness(self) -> Dict[str, Any]:
        """Check if system is ready for optimizations"""
        system_info = self.get_detailed_system_info()
        requirements = self.utils.check_system_requirements()
        
        readiness_score = 0
        max_score = 100
        
        # CPU score (30 points)
        if system_info['cpu_count_logical'] >= 8:
            readiness_score += 30
        elif system_info['cpu_count_logical'] >= 4:
            readiness_score += 20
        else:
            readiness_score += 10
        
        # Memory score (25 points)
        if system_info['memory_total_gb'] >= 32:
            readiness_score += 25
        elif system_info['memory_total_gb'] >= 16:
            readiness_score += 20
        elif system_info['memory_total_gb'] >= 8:
            readiness_score += 15
        else:
            readiness_score += 5
        
        # Platform score (20 points)
        if 'Linux' in system_info['platform']:
            readiness_score += 20
        elif 'Windows' in system_info['platform']:
            readiness_score += 15
        else:
            readiness_score += 10
        
        # Python version score (15 points)
        version = tuple(map(int, platform.python_version().split('.')))
        if version >= (3, 9):
            readiness_score += 15
        elif version >= (3, 7):
            readiness_score += 10
        else:
            readiness_score += 5
        
        # Additional resources score (10 points)
        if system_info['memory_available_gb'] >= 16:
            readiness_score += 10
        elif system_info['memory_available_gb'] >= 8:
            readiness_score += 7
        else:
            readiness_score += 3
        
        # Recommendations
        recommendations = []
        
        if system_info['cpu_count_logical'] < 4:
            recommendations.append("Consider using a system with more CPU cores for optimal performance")
        
        if system_info['memory_total_gb'] < 16:
            recommendations.append("Consider adding more RAM for better performance")
        
        if 'Linux' not in system_info['platform']:
            recommendations.append("Linux is recommended for advanced latency optimizations")
        
        if version < (3, 9):
            recommendations.append("Consider upgrading to Python 3.9+ for better performance")
        
        return {
            'readiness_score': readiness_score,
            'max_score': max_score,
            'readiness_percent': (readiness_score / max_score) * 100,
            'system_info': system_info,
            'requirements_check': requirements,
            'recommendations': recommendations
        }