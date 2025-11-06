"""
Core Latency Optimization Engine
"""

import time
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from .config.config_manager import ConfigManager, LatencyConfig
from .config.performance_profiles import PerformanceProfileManager
from .network import NetworkOptimizer
from .hardware import HardwareOptimizer
from .software import SoftwareOptimizer
from .market_data import MarketDataProcessor
from .monitoring import LatencyMonitor
from .utils import LatencyUtils

logger = logging.getLogger(__name__)


@dataclass
class LatencyMetrics:
    """Latency performance metrics"""
    current_latency_us: float
    average_latency_us: float
    p99_latency_us: float
    throughput_ops_per_sec: float
    packet_loss_rate: float
    cpu_usage_percent: float
    memory_usage_mb: float
    network_utilization_percent: float
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'current_latency_us': self.current_latency_us,
            'average_latency_us': self.average_latency_us,
            'p99_latency_us': self.p99_latency_us,
            'throughput_ops_per_sec': self.throughput_ops_per_sec,
            'packet_loss_rate': self.packet_loss_rate,
            'cpu_usage_percent': self.cpu_usage_percent,
            'memory_usage_mb': self.memory_usage_mb,
            'network_utilization_percent': self.network_utilization_percent
        }


@dataclass
class OptimizationResult:
    """Result of optimization process"""
    success: bool
    applied_optimizations: List[str]
    latency_improvement_percent: float
    performance_gain_score: float
    issues: List[str]
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'applied_optimizations': self.applied_optimizations,
            'latency_improvement_percent': self.latency_improvement_percent,
            'performance_gain_score': self.performance_gain_score,
            'issues': self.issues,
            'timestamp': self.timestamp
        }


class LatencyOptimizer:
    """Core latency optimization engine"""
    
    def __init__(self, config: Optional[LatencyConfig] = None, config_file: Optional[str] = None):
        """Initialize the latency optimizer"""
        self.config_manager = ConfigManager(config_file)
        if config:
            self.config_manager.config = config
        else:
            self.config = self.config_manager.config
        
        self.profile_manager = PerformanceProfileManager()
        self.utils = LatencyUtils()
        
        # Initialize optimization components
        self.network_optimizer = NetworkOptimizer(self.config.network)
        self.hardware_optimizer = HardwareOptimizer(self.config.hardware)
        self.software_optimizer = SoftwareOptimizer(self.config.software)
        self.market_data_processor = MarketDataProcessor(self.config.market_data)
        self.latency_monitor = LatencyMonitor(self.config)
        
        # State tracking
        self._is_running = False
        self._background_thread = None
        self._metrics_history: List[LatencyMetrics] = []
        self._optimization_lock = threading.Lock()
        self._optimization_stats = {
            'total_optimizations': 0,
            'successful_optimizations': 0,
            'last_optimization_time': 0.0,
            'total_latency_improvement': 0.0
        }
        
        logger.info("Latency Optimizer initialized")
    
    def start_optimization(self, auto_optimize: bool = True, interval_seconds: int = 60):
        """Start the optimization system"""
        if self._is_running:
            logger.warning("Optimization system is already running")
            return
        
        self._is_running = True
        
        # Start monitoring
        self.latency_monitor.start()
        
        # Start background optimization if enabled
        if auto_optimize:
            self._start_background_optimization(interval_seconds)
        
        logger.info("Latency optimization system started")
    
    def stop_optimization(self):
        """Stop the optimization system"""
        if not self._is_running:
            logger.warning("Optimization system is not running")
            return
        
        self._is_running = False
        
        # Stop monitoring
        self.latency_monitor.stop()
        
        # Stop background thread
        if self._background_thread and self._background_thread.is_alive():
            self._background_thread.join()
        
        logger.info("Latency optimization system stopped")
    
    def _start_background_optimization(self, interval_seconds: int):
        """Start background optimization thread"""
        def optimization_loop():
            while self._is_running:
                try:
                    time.sleep(interval_seconds)
                    if self._is_running:
                        self.auto_optimize()
                except Exception as e:
                    logger.error(f"Background optimization error: {e}")
        
        self._background_thread = threading.Thread(target=optimization_loop, daemon=True)
        self._background_thread.start()
    
    def apply_performance_profile(self, profile_name: str) -> OptimizationResult:
        """Apply a performance profile"""
        start_time = time.time()
        applied_optimizations = []
        issues = []
        
        try:
            with self._optimization_lock:
                # Apply profile to config
                self.config = self.profile_manager.apply_profile(self.config, profile_name)
                
                # Reinitialize components with new config
                self._reinitialize_components()
                
                applied_optimizations.append(f"profile_{profile_name}")
                
                # Measure improvement
                before_metrics = self.get_current_metrics()
                self.latency_monitor.force_measurement()
                time.sleep(1)  # Allow system to stabilize
                after_metrics = self.get_current_metrics()
                
                latency_improvement = 0.0
                if before_metrics and after_metrics:
                    if before_metrics.average_latency_us > 0:
                        latency_improvement = (
                            (before_metrics.average_latency_us - after_metrics.average_latency_us) 
                            / before_metrics.average_latency_us * 100
                        )
                
                success = len(issues) == 0
                
                # Update stats
                self._optimization_stats['total_optimizations'] += 1
                if success:
                    self._optimization_stats['successful_optimizations'] += 1
                    self._optimization_stats['total_latency_improvement'] += latency_improvement
                self._optimization_stats['last_optimization_time'] = time.time()
                
                return OptimizationResult(
                    success=success,
                    applied_optimizations=applied_optimizations,
                    latency_improvement_percent=latency_improvement,
                    performance_gain_score=self._calculate_performance_score(after_metrics),
                    issues=issues,
                    timestamp=time.time()
                )
                
        except Exception as e:
            logger.error(f"Error applying performance profile {profile_name}: {e}")
            issues.append(str(e))
            
            return OptimizationResult(
                success=False,
                applied_optimizations=[],
                latency_improvement_percent=0.0,
                performance_gain_score=0.0,
                issues=issues,
                timestamp=time.time()
            )
    
    def auto_optimize(self) -> OptimizationResult:
        """Perform automatic optimization based on current metrics"""
        with self._optimization_lock:
            # Get current metrics
            current_metrics = self.get_current_metrics()
            if not current_metrics:
                return OptimizationResult(
                    success=False,
                    applied_optimizations=[],
                    latency_improvement_percent=0.0,
                    performance_gain_score=0.0,
                    issues=["Could not obtain current metrics"],
                    timestamp=time.time()
                )
            
            # Check if optimization is needed
            if current_metrics.average_latency_us <= self.config.target_latency_us:
                logger.debug("Latency within target, no optimization needed")
                return OptimizationResult(
                    success=True,
                    applied_optimizations=[],
                    latency_improvement_percent=0.0,
                    performance_gain_score=100.0,
                    issues=[],
                    timestamp=time.time()
                )
            
            # Start optimization process
            start_time = time.time()
            applied_optimizations = []
            issues = []
            total_improvement = 0.0
            
            try:
                # 1. Network optimization
                if self.config.network.enable_kernel_bypass or self.config.network.enable_user_space_tcp:
                    network_result = self.network_optimizer.optimize()
                    if network_result['success']:
                        applied_optimizations.extend(network_result['applied_optimizations'])
                        total_improvement += network_result['improvement']
                
                # 2. Hardware optimization
                hardware_result = self.hardware_optimizer.optimize()
                if hardware_result['success']:
                    applied_optimizations.extend(hardware_result['applied_optimizations'])
                    total_improvement += hardware_result['improvement']
                
                # 3. Software optimization
                software_result = self.software_optimizer.optimize()
                if software_result['success']:
                    applied_optimizations.extend(software_result['applied_optimizations'])
                    total_improvement += software_result['improvement']
                
                # 4. Market data optimization
                market_data_result = self.market_data_processor.optimize()
                if market_data_result['success']:
                    applied_optimizations.extend(market_data_result['applied_optimizations'])
                    total_improvement += market_data_result['improvement']
                
                # Measure final improvement
                time.sleep(0.5)  # Allow system to stabilize
                final_metrics = self.get_current_metrics()
                
                latency_improvement = 0.0
                performance_score = 0.0
                
                if final_metrics:
                    if current_metrics.average_latency_us > 0:
                        latency_improvement = (
                            (current_metrics.average_latency_us - final_metrics.average_latency_us) 
                            / current_metrics.average_latency_us * 100
                        )
                    performance_score = self._calculate_performance_score(final_metrics)
                
                # Update stats
                self._optimization_stats['total_optimizations'] += 1
                if applied_optimizations:
                    self._optimization_stats['successful_optimizations'] += 1
                self._optimization_stats['total_latency_improvement'] += latency_improvement
                self._optimization_stats['last_optimization_time'] = time.time()
                
                logger.info(f"Auto optimization completed: {len(applied_optimizations)} optimizations applied, "
                          f"{latency_improvement:.2f}% improvement")
                
                return OptimizationResult(
                    success=len(applied_optimizations) > 0,
                    applied_optimizations=applied_optimizations,
                    latency_improvement_percent=latency_improvement,
                    performance_gain_score=performance_score,
                    issues=issues,
                    timestamp=time.time()
                )
                
            except Exception as e:
                logger.error(f"Auto optimization failed: {e}")
                issues.append(str(e))
                
                return OptimizationResult(
                    success=False,
                    applied_optimizations=[],
                    latency_improvement_percent=0.0,
                    performance_gain_score=0.0,
                    issues=issues,
                    timestamp=time.time()
                )
    
    def get_current_metrics(self) -> Optional[LatencyMetrics]:
        """Get current latency metrics"""
        try:
            metrics = self.latency_monitor.get_current_metrics()
            if metrics:
                self._metrics_history.append(metrics)
                # Keep only last 1000 metrics to prevent memory issues
                if len(self._metrics_history) > 1000:
                    self._metrics_history = self._metrics_history[-1000:]
                return metrics
            return None
        except Exception as e:
            logger.error(f"Failed to get current metrics: {e}")
            return None
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        stats = self._optimization_stats.copy()
        stats['success_rate'] = 0.0
        stats['average_improvement'] = 0.0
        
        if stats['total_optimizations'] > 0:
            stats['success_rate'] = (
                stats['successful_optimizations'] / stats['total_optimizations'] * 100
            )
            stats['average_improvement'] = stats['total_latency_improvement'] / stats['total_optimizations']
        
        return stats
    
    def get_metrics_history(self, limit: int = 100) -> List[LatencyMetrics]:
        """Get metrics history"""
        return self._metrics_history[-limit:]
    
    def benchmark_system(self) -> Dict[str, Any]:
        """Run comprehensive system benchmark"""
        logger.info("Starting comprehensive system benchmark...")
        
        # Record baseline
        baseline_metrics = self.get_current_metrics()
        
        # Run individual component benchmarks
        benchmark_results = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Network benchmark
            network_future = executor.submit(self._benchmark_network)
            # Hardware benchmark
            hardware_future = executor.submit(self._benchmark_hardware)
            # Software benchmark
            software_future = executor.submit(self._benchmark_software)
            # Market data benchmark
            market_data_future = executor.submit(self._benchmark_market_data)
            
            # Collect results
            benchmark_results['network'] = network_future.result()
            benchmark_results['hardware'] = hardware_future.result()
            benchmark_results['software'] = software_future.result()
            benchmark_results['market_data'] = market_data_future.result()
        
        # Calculate overall performance score
        overall_score = self._calculate_overall_benchmark_score(benchmark_results)
        
        # Final metrics
        final_metrics = self.get_current_metrics()
        
        benchmark_results.update({
            'baseline_metrics': baseline_metrics.to_dict() if baseline_metrics else None,
            'final_metrics': final_metrics.to_dict() if final_metrics else None,
            'overall_score': overall_score,
            'timestamp': time.time()
        })
        
        logger.info(f"Benchmark completed with overall score: {overall_score}")
        return benchmark_results
    
    def _benchmark_network(self) -> Dict[str, Any]:
        """Benchmark network optimization"""
        result = self.network_optimizer.benchmark()
        logger.info(f"Network benchmark completed: {result}")
        return result
    
    def _benchmark_hardware(self) -> Dict[str, Any]:
        """Benchmark hardware optimization"""
        result = self.hardware_optimizer.benchmark()
        logger.info(f"Hardware benchmark completed: {result}")
        return result
    
    def _benchmark_software(self) -> Dict[str, Any]:
        """Benchmark software optimization"""
        result = self.software_optimizer.benchmark()
        logger.info(f"Software benchmark completed: {result}")
        return result
    
    def _benchmark_market_data(self) -> Dict[str, Any]:
        """Benchmark market data processing"""
        result = self.market_data_processor.benchmark()
        logger.info(f"Market data benchmark completed: {result}")
        return result
    
    def _reinitialize_components(self):
        """Reinitialize all components with current config"""
        self.network_optimizer = NetworkOptimizer(self.config.network)
        self.hardware_optimizer = HardwareOptimizer(self.config.hardware)
        self.software_optimizer = SoftwareOptimizer(self.config.software)
        self.market_data_processor = MarketDataProcessor(self.config.market_data)
        self.latency_monitor = LatencyMonitor(self.config)
    
    def _calculate_performance_score(self, metrics: LatencyMetrics) -> float:
        """Calculate performance score from metrics"""
        if not metrics:
            return 0.0
        
        score = 0.0
        
        # Latency score (40% weight)
        target_latency = self.config.target_latency_us
        if metrics.average_latency_us <= target_latency:
            score += 40.0
        else:
            latency_score = max(0, 40 * (target_latency / metrics.average_latency_us))
            score += latency_score
        
        # Throughput score (30% weight)
        target_throughput = 100000  # 100K ops/sec baseline
        throughput_score = min(30.0, 30 * (metrics.throughput_ops_per_sec / target_throughput))
        score += throughput_score
        
        # Resource utilization (20% weight)
        resource_score = 20.0
        if metrics.cpu_usage_percent > 80:
            resource_score *= (100 - metrics.cpu_usage_percent) / 20
        if metrics.memory_usage_mb > self.config.hardware.memory_limit_gb * 1024 * 0.8:
            resource_score *= 0.5
        score += max(0, resource_score)
        
        # Network efficiency (10% weight)
        network_score = max(0, 10 * (1 - metrics.packet_loss_rate))
        score += network_score
        
        return min(100.0, max(0.0, score))
    
    def _calculate_overall_benchmark_score(self, benchmark_results: Dict[str, Any]) -> float:
        """Calculate overall benchmark score"""
        scores = []
        weights = {'network': 0.3, 'hardware': 0.3, 'software': 0.2, 'market_data': 0.2}
        
        for component, result in benchmark_results.items():
            if 'score' in result:
                scores.append(result['score'] * weights.get(component, 0.25))
        
        return sum(scores) if scores else 0.0
    
    def save_config(self, config_file: str):
        """Save current configuration"""
        self.config_manager.save_config(config_file)
    
    def load_config(self, config_file: str):
        """Load configuration from file"""
        self.config_manager.config_file = config_file
        self.config_manager._load_config()
        self.config = self.config_manager.config
        self._reinitialize_components()
    
    def is_running(self) -> bool:
        """Check if optimization system is running"""
        return self._is_running
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            'is_running': self._is_running,
            'target_latency_us': self.config.target_latency_us,
            'performance_mode': self.config.performance_mode,
            'current_metrics': self.get_current_metrics().to_dict() if self.get_current_metrics() else None,
            'optimization_stats': self.get_optimization_stats(),
            'system_health': self._get_system_health()
        }
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        metrics = self.get_current_metrics()
        if not metrics:
            return {'status': 'unknown', 'issues': ['Could not obtain metrics']}
        
        issues = []
        health_score = 100.0
        
        # Check latency
        if metrics.average_latency_us > self.config.target_latency_us * 2:
            issues.append('Latency significantly above target')
            health_score -= 20
        elif metrics.average_latency_us > self.config.target_latency_us:
            issues.append('Latency above target')
            health_score -= 10
        
        # Check packet loss
        if metrics.packet_loss_rate > 0.01:
            issues.append('High packet loss rate')
            health_score -= 15
        
        # Check CPU usage
        if metrics.cpu_usage_percent > 90:
            issues.append('High CPU usage')
            health_score -= 15
        
        # Check memory
        if metrics.memory_usage_mb > self.config.hardware.memory_limit_gb * 1024 * 0.9:
            issues.append('High memory usage')
            health_score -= 10
        
        return {
            'status': 'healthy' if health_score >= 80 else 'degraded' if health_score >= 60 else 'critical',
            'score': health_score,
            'issues': issues
        }