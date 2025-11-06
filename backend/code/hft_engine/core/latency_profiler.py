"""
Latency Profiler System
======================

High-performance latency monitoring and profiling for HFT operations
Provides microsecond-level latency measurement and analysis
"""

import time
import logging
import statistics
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import defaultdict, deque
from threading import Lock
import json

@dataclass
class LatencyMeasurement:
    """Individual latency measurement"""
    operation: str
    latency_us: float
    timestamp: float
    additional_data: Optional[Dict] = None

@dataclass
class LatencyStats:
    """Latency statistics"""
    count: int
    mean_us: float
    median_us: float
    min_us: float
    max_us: float
    std_dev_us: float
    p95_us: float
    p99_us: float
    p99_9_us: float

class LatencyProfiler:
    """
    High-Performance Latency Profiler
    
    Monitors and analyzes system latency at microsecond level
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Latency storage
        self.measurements: Dict[str, List[LatencyMeasurement]] = defaultdict(lambda: deque(maxlen=10000))
        self.current_session_start = time.time()
        
        # System-wide metrics
        self.total_measurements = 0
        self.start_time = time.perf_counter()
        
        # Performance thresholds
        self.thresholds = {
            'critical': 100,    # 100 microseconds
            'warning': 500,     # 500 microseconds
            'target': 50,       # 50 microseconds
            'excellent': 20     # 20 microseconds
        }
        
        # Thread safety
        self.lock = Lock()
        
        # High-resolution timer (if available)
        try:
            import time as time_module
            if hasattr(time_module, 'perf_counter_ns'):
                self.timer = time_module.perf_counter_ns
                self.unit_factor = 1  # nanoseconds to microseconds
            else:
                self.timer = time_module.perf_counter
                self.unit_factor = 1_000_000  # seconds to microseconds
        except:
            self.timer = time.perf_counter
            self.unit_factor = 1_000_000
        
        self.logger = logging.getLogger(__name__)
        
    def start_timer(self) -> float:
        """Start timing operation"""
        return self.timer()
    
    def end_timer(self, start_time: float, operation: str, 
                  additional_data: Optional[Dict] = None) -> float:
        """End timing and record latency"""
        end_time = self.timer()
        latency_us = (end_time - start_time) * self.unit_factor
        
        self.record_latency(operation, latency_us, additional_data)
        return latency_us
    
    def record_latency(self, operation: str, latency_us: float, 
                      additional_data: Optional[Dict] = None):
        """Record latency measurement"""
        with self.lock:
            measurement = LatencyMeasurement(
                operation=operation,
                latency_us=latency_us,
                timestamp=time.time(),
                additional_data=additional_data
            )
            
            self.measurements[operation].append(measurement)
            self.total_measurements += 1
    
    def record_strategy_latency(self, strategy_name: str, latency_us: float):
        """Record strategy execution latency"""
        operation = f"strategy.{strategy_name}"
        additional_data = {'strategy': strategy_name}
        self.record_latency(operation, latency_us, additional_data)
    
    def record_trading_loop_latency(self, latency_us: float):
        """Record main trading loop latency"""
        self.record_latency("trading_loop", latency_us)
    
    def record_order_execution_latency(self, exchange: str, latency_us: float):
        """Record order execution latency"""
        operation = f"order_execution.{exchange}"
        additional_data = {'exchange': exchange}
        self.record_latency(operation, latency_us, additional_data)
    
    def record_market_data_latency(self, symbol: str, latency_us: float):
        """Record market data processing latency"""
        operation = f"market_data.{symbol}"
        additional_data = {'symbol': symbol}
        self.record_latency(operation, latency_us, additional_data)
    
    def get_operation_stats(self, operation: str) -> Optional[LatencyStats]:
        """Get statistics for specific operation"""
        with self.lock:
            measurements = self.measurements.get(operation, [])
            
            if not measurements:
                return None
            
            latencies = [m.latency_us for m in measurements]
            
            # Calculate statistics
            count = len(latencies)
            mean_us = statistics.mean(latencies)
            median_us = statistics.median(latencies)
            min_us = min(latencies)
            max_us = max(latencies)
            
            # Standard deviation
            try:
                std_dev_us = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
            except statistics.StatisticsError:
                std_dev_us = 0.0
            
            # Percentiles
            sorted_latencies = sorted(latencies)
            p95_idx = int(0.95 * count)
            p99_idx = int(0.99 * count)
            p99_9_idx = int(0.999 * count)
            
            p95_us = sorted_latencies[p95_idx] if p95_idx < count else sorted_latencies[-1]
            p99_us = sorted_latencies[p99_idx] if p99_idx < count else sorted_latencies[-1]
            p99_9_us = sorted_latencies[p99_9_idx] if p99_9_idx < count else sorted_latencies[-1]
            
            return LatencyStats(
                count=count,
                mean_us=mean_us,
                median_us=median_us,
                min_us=min_us,
                max_us=max_us,
                std_dev_us=std_dev_us,
                p95_us=p95_us,
                p99_us=p99_us,
                p99_9_us=p99_9_9_us if p99_9_idx < count else max_us
            )
    
    def get_all_stats(self) -> Dict[str, LatencyStats]:
        """Get statistics for all operations"""
        stats = {}
        
        for operation in self.measurements.keys():
            operation_stats = self.get_operation_stats(operation)
            if operation_stats:
                stats[operation] = operation_stats
        
        return stats
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        with self.lock:
            all_stats = self.get_all_stats()
            
            if not all_stats:
                return {
                    'total_measurements': self.total_measurements,
                    'operations_monitored': 0,
                    'overall_avg_latency': 0,
                    'critical_violations': 0
                }
            
            # Calculate overall metrics
            all_latencies = []
            for operation, stats in all_stats.items():
                all_latencies.extend([stats.mean_us] * min(stats.count, 10))  # Weight by sample size
            
            overall_avg = statistics.mean(all_latencies) if all_latencies else 0
            
            # Count threshold violations
            critical_violations = 0
            for stats in all_stats.values():
                if stats.mean_us > self.thresholds['critical']:
                    critical_violations += 1
            
            return {
                'total_measurements': self.total_measurements,
                'operations_monitored': len(all_stats),
                'overall_avg_latency_us': overall_avg,
                'critical_violations': critical_violations,
                'session_duration_s': time.perf_counter() - self.start_time,
                'operations': {
                    op: {
                        'mean_us': stats.mean_us,
                        'median_us': stats.median_us,
                        'min_us': stats.min_us,
                        'max_us': stats.max_us,
                        'p95_us': stats.p95_us,
                        'p99_us': stats.p99_us,
                        'count': stats.count
                    }
                    for op, stats in all_stats.items()
                }
            }
    
    def get_bottlenecks(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        all_stats = self.get_all_stats()
        
        # Sort operations by mean latency (descending)
        sorted_ops = sorted(
            all_stats.items(),
            key=lambda x: x[1].mean_us,
            reverse=True
        )
        
        bottlenecks = []
        for operation, stats in sorted_ops[:top_n]:
            bottlenecks.append({
                'operation': operation,
                'mean_latency_us': stats.mean_us,
                'max_latency_us': stats.max_latency_us,
                'count': stats.count,
                'threshold_violation': stats.mean_us > self.thresholds['critical'],
                'severity': self._calculate_severity(stats)
            })
        
        return bottlenecks
    
    def _calculate_severity(self, stats: LatencyStats) -> str:
        """Calculate severity of performance issue"""
        if stats.mean_us <= self.thresholds['excellent']:
            return 'excellent'
        elif stats.mean_us <= self.thresholds['target']:
            return 'good'
        elif stats.mean_us <= self.thresholds['warning']:
            return 'warning'
        else:
            return 'critical'
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time performance metrics"""
        with self.lock:
            recent_measurements = []
            
            # Get measurements from last 10 seconds
            cutoff_time = time.time() - 10
            
            for operation, measurements in self.measurements.items():
                recent = [m for m in measurements if m.timestamp > cutoff_time]
                recent_measurements.extend(recent)
            
            if not recent_measurements:
                return {
                    'measurements_per_second': 0,
                    'avg_latency_us': 0,
                    'current_load': 'low'
                }
            
            # Calculate rate and average
            recent_latencies = [m.latency_us for m in recent_measurements]
            avg_latency = statistics.mean(recent_latencies)
            rate = len(recent_measurements) / 10  # Per second
            
            # Determine load level
            if rate > 1000:
                load = 'high'
            elif rate > 500:
                load = 'medium'
            else:
                load = 'low'
            
            return {
                'measurements_per_second': rate,
                'avg_latency_us': avg_latency,
                'current_load': load,
                'operations_count': len(set(m.operation for m in recent_measurements))
            }
    
    def get_current_load(self) -> str:
        """Get current system load level"""
        metrics = self.get_real_time_metrics()
        return metrics.get('current_load', 'low')
    
    def export_latency_data(self, operation: str, output_file: str) -> bool:
        """Export latency data to file"""
        try:
            stats = self.get_operation_stats(operation)
            if not stats:
                return False
            
            export_data = {
                'operation': operation,
                'statistics': {
                    'count': stats.count,
                    'mean_us': stats.mean_us,
                    'median_us': stats.median_us,
                    'min_us': stats.min_us,
                    'max_us': stats.max_us,
                    'std_dev_us': stats.std_dev_us,
                    'p95_us': stats.p95_us,
                    'p99_us': stats.p99_us,
                    'p99_9_us': stats.p99_9_us
                },
                'measurements': [
                    {
                        'timestamp': m.timestamp,
                        'latency_us': m.latency_us,
                        'additional_data': m.additional_data
                    }
                    for m in self.measurements.get(operation, [])
                ]
            }
            
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export latency data: {e}")
            return False
    
    def get_latency_trends(self, operation: str, minutes: int = 60) -> List[Dict[str, float]]:
        """Get latency trends over time"""
        cutoff_time = time.time() - (minutes * 60)
        
        measurements = [
            m for m in self.measurements.get(operation, [])
            if m.timestamp > cutoff_time
        ]
        
        if not measurements:
            return []
        
        # Group measurements by minute
        trends = defaultdict(list)
        for measurement in measurements:
            minute = int(measurement.timestamp // 60) * 60
            trends[minute].append(measurement.latency_us)
        
        # Calculate average latency per minute
        trend_data = []
        for timestamp in sorted(trends.keys()):
            latencies = trends[timestamp]
            trend_data.append({
                'timestamp': timestamp,
                'avg_latency_us': statistics.mean(latencies),
                'min_latency_us': min(latencies),
                'max_latency_us': max(latencies),
                'count': len(latencies)
            })
        
        return trend_data
    
    def reset_stats(self):
        """Reset all statistics"""
        with self.lock:
            self.measurements.clear()
            self.total_measurements = 0
            self.current_session_start = time.time()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        return {
            'summary': self.get_performance_summary(),
            'real_time': self.get_real_time_metrics(),
            'bottlenecks': self.get_bottlenecks(5),
            'operations': self.get_all_stats()
        }
    
    def print_performance_report(self):
        """Print performance report to console"""
        summary = self.get_performance_summary()
        bottlenecks = self.get_bottlenecks(5)
        
        print("\n" + "="*60)
        print("HFT ENGINE PERFORMANCE REPORT")
        print("="*60)
        print(f"Total Measurements: {summary['total_measurements']:,}")
        print(f"Operations Monitored: {summary['operations_monitored']}")
        print(f"Overall Avg Latency: {summary['overall_avg_latency_us']:.2f} μs")
        print(f"Critical Violations: {summary['critical_violations']}")
        print(f"Session Duration: {summary['session_duration_s']:.2f}s")
        
        if bottlenecks:
            print("\nTOP PERFORMANCE BOTTLENECKS:")
            print("-" * 40)
            for i, bottleneck in enumerate(bottlenecks, 1):
                severity_icon = "🚨" if bottleneck['threshold_violation'] else "⚠️"
                print(f"{i:2d}. {severity_icon} {bottleneck['operation']}")
                print(f"    Mean: {bottleneck['mean_latency_us']:.2f} μs")
                print(f"    Max:  {bottleneck['max_latency_us']:.2f} μs")
                print(f"    Count: {bottleneck['count']}")
                print()
        
        print("="*60)