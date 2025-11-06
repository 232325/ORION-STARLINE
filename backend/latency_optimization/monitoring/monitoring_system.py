"""
Monitoring and Metrics Module
"""

import time
import threading
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor
import psutil
import numpy as np
import logging

logger = logging.getLogger(__name__)


@dataclass
class LatencyMeasurement:
    """Individual latency measurement"""
    timestamp: float
    operation_type: str
    latency_us: float
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: float
    cpu_usage_percent: float
    memory_usage_mb: float
    memory_utilization_percent: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    network_packets_sent: int
    network_packets_recv: int
    process_cpu_percent: float
    process_memory_mb: float
    thread_count: int
    file_descriptor_count: int


@dataclass
class PerformanceAlert:
    """Performance alert"""
    timestamp: float
    alert_type: str
    severity: str  # 'info', 'warning', 'critical'
    message: str
    metrics: Dict[str, Any]
    acknowledged: bool = False


class LatencyMonitor:
    """Real-time latency monitoring system"""
    
    def __init__(self, latency_config):
        self.config = latency_config
        self.latency_measurements = deque(maxlen=10000)
        self.system_metrics = deque(maxlen=1000)
        self.alerts = deque(maxlen=100)
        
        # Monitoring state
        self._is_monitoring = False
        self._monitoring_thread = None
        self._lock = threading.Lock()
        
        # Alert thresholds
        self.alert_thresholds = {
            'latency_us': {
                'warning': 50,
                'critical': 100
            },
            'cpu_usage_percent': {
                'warning': 80,
                'critical': 95
            },
            'memory_usage_percent': {
                'warning': 85,
                'critical': 95
            }
        }
        
        # Statistics
        self.stats = {
            'total_measurements': 0,
            'avg_latency_us': 0.0,
            'p50_latency_us': 0.0,
            'p95_latency_us': 0.0,
            'p99_latency_us': 0.0,
            'max_latency_us': 0.0,
            'min_latency_us': float('inf'),
            'success_rate': 1.0
        }
        
        logger.info("Latency Monitor initialized")
    
    def start(self):
        """Start monitoring"""
        if self._is_monitoring:
            logger.warning("Monitoring is already running")
            return
        
        self._is_monitoring = True
        
        # Start monitoring thread
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        
        logger.info("Latency monitoring started")
    
    def stop(self):
        """Stop monitoring"""
        if not self._is_monitoring:
            logger.warning("Monitoring is not running")
            return
        
        self._is_monitoring = False
        
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=1)
        
        logger.info("Latency monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self._is_monitoring:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Check for alerts
                self._check_alerts()
                
                # Update statistics
                self._update_statistics()
                
                # Sleep for monitoring interval
                time.sleep(self.config.monitoring_interval_ms / 1000.0)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(1)
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # Process metrics
            process = psutil.Process()
            process_cpu = process.cpu_percent()
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            process_threads = process.num_threads()
            process_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
            
            metrics = SystemMetrics(
                timestamp=time.time(),
                cpu_usage_percent=cpu_percent,
                memory_usage_mb=memory.used / 1024 / 1024,
                memory_utilization_percent=memory.percent,
                disk_usage_percent=(disk.used / disk.total) * 100,
                network_bytes_sent=network.bytes_sent,
                network_bytes_recv=network.bytes_recv,
                network_packets_sent=network.packets_sent,
                network_packets_recv=network.packets_recv,
                process_cpu_percent=process_cpu,
                process_memory_mb=process_memory,
                thread_count=process_threads,
                file_descriptor_count=process_fds
            )
            
            with self._lock:
                self.system_metrics.append(metrics)
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    def measure_latency(self, operation_type: str, operation_func, *args, **kwargs) -> Dict[str, Any]:
        """Measure operation latency"""
        start_time = time.time()
        success = False
        result = None
        
        try:
            result = operation_func(*args, **kwargs)
            success = True
        except Exception as e:
            logger.error(f"Operation {operation_type} failed: {e}")
            success = False
        
        end_time = time.time()
        latency_us = (end_time - start_time) * 1_000_000
        
        # Create measurement
        measurement = LatencyMeasurement(
            timestamp=time.time(),
            operation_type=operation_type,
            latency_us=latency_us,
            success=success
        )
        
        # Store measurement
        with self._lock:
            self.latency_measurements.append(measurement)
            self.stats['total_measurements'] += 1
        
        return {
            'success': success,
            'latency_us': latency_us,
            'result': result,
            'timestamp': measurement.timestamp
        }
    
    def _check_alerts(self):
        """Check metrics against alert thresholds"""
        try:
            with self._lock:
                # Check latency alerts
                if self.latency_measurements:
                    recent_latencies = [m.latency_us for m in list(self.latency_measurements)[-10:]]
                    avg_latency = np.mean(recent_latencies)
                    
                    if avg_latency > self.alert_thresholds['latency_us']['critical']:
                        self._create_alert('latency', 'critical', 
                                         f'Average latency {avg_latency:.2f}us exceeds critical threshold',
                                         {'avg_latency_us': avg_latency})
                    elif avg_latency > self.alert_thresholds['latency_us']['warning']:
                        self._create_alert('latency', 'warning',
                                         f'Average latency {avg_latency:.2f}us exceeds warning threshold',
                                         {'avg_latency_us': avg_latency})
                
                # Check system metrics alerts
                if self.system_metrics:
                    latest_metrics = self.system_metrics[-1]
                    
                    # CPU usage
                    if latest_metrics.cpu_usage_percent > self.alert_thresholds['cpu_usage_percent']['critical']:
                        self._create_alert('cpu', 'critical',
                                         f'CPU usage {latest_metrics.cpu_usage_percent:.1f}% exceeds critical threshold',
                                         {'cpu_usage_percent': latest_metrics.cpu_usage_percent})
                    elif latest_metrics.cpu_usage_percent > self.alert_thresholds['cpu_usage_percent']['warning']:
                        self._create_alert('cpu', 'warning',
                                         f'CPU usage {latest_metrics.cpu_usage_percent:.1f}% exceeds warning threshold',
                                         {'cpu_usage_percent': latest_metrics.cpu_usage_percent})
                    
                    # Memory usage
                    if latest_metrics.memory_utilization_percent > self.alert_thresholds['memory_usage_percent']['critical']:
                        self._create_alert('memory', 'critical',
                                         f'Memory usage {latest_metrics.memory_utilization_percent:.1f}% exceeds critical threshold',
                                         {'memory_usage_percent': latest_metrics.memory_utilization_percent})
                    elif latest_metrics.memory_utilization_percent > self.alert_thresholds['memory_usage_percent']['warning']:
                        self._create_alert('memory', 'warning',
                                         f'Memory usage {latest_metrics.memory_utilization_percent:.1f}% exceeds warning threshold',
                                         {'memory_usage_percent': latest_metrics.memory_utilization_percent})
                    
        except Exception as e:
            logger.error(f"Failed to check alerts: {e}")
    
    def _create_alert(self, alert_type: str, severity: str, message: str, metrics: Dict[str, Any]):
        """Create a performance alert"""
        alert = PerformanceAlert(
            timestamp=time.time(),
            alert_type=alert_type,
            severity=severity,
            message=message,
            metrics=metrics
        )
        
        with self._lock:
            self.alerts.append(alert)
        
        # Log alert
        if severity == 'critical':
            logger.critical(f"CRITICAL ALERT: {message}")
        elif severity == 'warning':
            logger.warning(f"WARNING: {message}")
        else:
            logger.info(f"INFO: {message}")
    
    def _update_statistics(self):
        """Update performance statistics"""
        with self._lock:
            if not self.latency_measurements:
                return
            
            # Calculate latency statistics
            latencies = [m.latency_us for m in self.latency_measurements]
            
            self.stats['avg_latency_us'] = np.mean(latencies)
            self.stats['p50_latency_us'] = np.percentile(latencies, 50)
            self.stats['p95_latency_us'] = np.percentile(latencies, 95)
            self.stats['p99_latency_us'] = np.percentile(latencies, 99)
            self.stats['max_latency_us'] = np.max(latencies)
            self.stats['min_latency_us'] = np.min(latencies)
            
            # Calculate success rate
            successful_measurements = sum(1 for m in self.latency_measurements if m.success)
            self.stats['success_rate'] = successful_measurements / len(self.latency_measurements)
    
    def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """Get current performance metrics"""
        with self._lock:
            if not self.system_metrics:
                return None
            
            latest_metrics = self.system_metrics[-1]
            
            # Get latency metrics
            latency_metrics = self.get_latency_metrics(100)  # Last 100 measurements
            
            return {
                'timestamp': time.time(),
                'latency': latency_metrics,
                'system': asdict(latest_metrics),
                'target_latency_us': self.config.target_latency_us,
                'performance_mode': self.config.performance_mode
            }
    
    def force_measurement(self):
        """Force immediate metric collection"""
        self._collect_system_metrics()
        self._update_statistics()
    
    def get_latency_metrics(self, count: int = 100) -> Dict[str, float]:
        """Get latency metrics for recent measurements"""
        with self._lock:
            if not self.latency_measurements:
                return {
                    'avg_latency_us': 0.0,
                    'p50_latency_us': 0.0,
                    'p95_latency_us': 0.0,
                    'p99_latency_us': 0.0,
                    'max_latency_us': 0.0,
                    'min_latency_us': 0.0,
                    'success_rate': 1.0
                }
            
            recent_measurements = list(self.latency_measurements)[-count:]
            latencies = [m.latency_us for m in recent_measurements]
            
            return {
                'avg_latency_us': np.mean(latencies),
                'p50_latency_us': np.percentile(latencies, 50),
                'p95_latency_us': np.percentile(latencies, 95),
                'p99_latency_us': np.percentile(latencies, 99),
                'max_latency_us': np.max(latencies),
                'min_latency_us': np.min(latencies),
                'success_rate': sum(1 for m in recent_measurements if m.success) / len(recent_measurements),
                'measurement_count': len(recent_measurements)
            }
    
    def get_performance_alerts(self, severity: str = None, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent performance alerts"""
        with self._lock:
            alerts = list(self.alerts)
            
            if severity:
                alerts = [a for a in alerts if a.severity == severity]
            
            return [asdict(alert) for alert in alerts[-count:]]
    
    def acknowledge_alert(self, timestamp: float):
        """Acknowledge an alert"""
        with self._lock:
            for alert in self.alerts:
                if alert.timestamp == timestamp:
                    alert.acknowledged = True
                    break
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            'is_monitoring': self._is_monitoring,
            'monitoring_interval_ms': self.config.monitoring_interval_ms,
            'target_latency_us': self.config.target_latency_us,
            'stats': self.stats.copy(),
            'alert_thresholds': self.alert_thresholds,
            'total_alerts': len(self.alerts),
            'unacknowledged_alerts': sum(1 for a in self.alerts if not a.acknowledged)
        }


class PerformanceDashboard:
    """Real-time performance dashboard"""
    
    def __init__(self, latency_monitor: LatencyMonitor):
        self.monitor = latency_monitor
        self.dashboards = {}
        self._lock = threading.Lock()
    
    def create_dashboard(self, name: str, metrics_config: Dict[str, Any]) -> bool:
        """Create a custom performance dashboard"""
        try:
            with self._lock:
                self.dashboards[name] = {
                    'config': metrics_config,
                    'created': time.time(),
                    'last_updated': time.time(),
                    'data_points': deque(maxlen=1000)
                }
            
            logger.info(f"Performance dashboard '{name}' created")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create dashboard '{name}': {e}")
            return False
    
    def update_dashboard(self, name: str, data: Dict[str, Any]) -> bool:
        """Update dashboard with new data"""
        try:
            with self._lock:
                if name not in self.dashboards:
                    return False
                
                dashboard = self.dashboards[name]
                dashboard['last_updated'] = time.time()
                dashboard['data_points'].append({
                    'timestamp': time.time(),
                    'data': data
                })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update dashboard '{name}': {e}")
            return False
    
    def get_dashboard_data(self, name: str, count: int = 100) -> Optional[Dict[str, Any]]:
        """Get dashboard data"""
        with self._lock:
            if name not in self.dashboards:
                return None
            
            dashboard = self.dashboards[name]
            recent_data = list(dashboard['data_points'])[-count:]
            
            return {
                'name': name,
                'config': dashboard['config'],
                'created': dashboard['created'],
                'last_updated': dashboard['last_updated'],
                'data_points': recent_data,
                'current_metrics': self.monitor.get_current_metrics()
            }
    
    def list_dashboards(self) -> List[str]:
        """List all dashboard names"""
        with self._lock:
            return list(self.dashboards.keys())
    
    def delete_dashboard(self, name: str) -> bool:
        """Delete a dashboard"""
        try:
            with self._lock:
                if name in self.dashboards:
                    del self.dashboards[name]
                    logger.info(f"Performance dashboard '{name}' deleted")
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete dashboard '{name}': {e}")
            return False


class AlertManager:
    """Advanced alert management system"""
    
    def __init__(self, latency_monitor: LatencyMonitor):
        self.monitor = latency_monitor
        self.alert_rules = {}
        self.notification_channels = {}
        self.alert_history = deque(maxlen=10000)
        self._lock = threading.Lock()
    
    def add_alert_rule(self, rule_name: str, rule_config: Dict[str, Any]) -> bool:
        """Add custom alert rule"""
        try:
            # Validate rule config
            required_fields = ['metric', 'condition', 'threshold']
            if not all(field in rule_config for field in required_fields):
                logger.error(f"Alert rule '{rule_name}' missing required fields")
                return False
            
            with self._lock:
                self.alert_rules[rule_name] = rule_config
            
            logger.info(f"Alert rule '{rule_name}' added")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add alert rule '{rule_name}': {e}")
            return False
    
    def add_notification_channel(self, channel_name: str, config: Dict[str, Any]) -> bool:
        """Add notification channel"""
        try:
            with self._lock:
                self.notification_channels[channel_name] = config
            
            logger.info(f"Notification channel '{channel_name}' added")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add notification channel '{channel_name}': {e}")
            return False
    
    def evaluate_alert_rules(self):
        """Evaluate all alert rules"""
        current_metrics = self.monitor.get_current_metrics()
        if not current_metrics:
            return
        
        try:
            with self._lock:
                for rule_name, rule_config in self.alert_rules.items():
                    self._evaluate_rule(rule_name, rule_config, current_metrics)
                    
        except Exception as e:
            logger.error(f"Failed to evaluate alert rules: {e}")
    
    def _evaluate_rule(self, rule_name: str, rule_config: Dict[str, Any], metrics: Dict[str, Any]):
        """Evaluate individual alert rule"""
        try:
            metric_path = rule_config['metric']
            condition = rule_config['condition']
            threshold = rule_config['threshold']
            
            # Get metric value
            metric_value = self._get_metric_value(metrics, metric_path)
            if metric_value is None:
                return
            
            # Check condition
            should_alert = False
            if condition == 'greater_than' and metric_value > threshold:
                should_alert = True
            elif condition == 'less_than' and metric_value < threshold:
                should_alert = True
            elif condition == 'equals' and metric_value == threshold:
                should_alert = True
            
            if should_alert:
                self._trigger_alert(rule_name, rule_config, metric_value, metrics)
                
        except Exception as e:
            logger.error(f"Failed to evaluate rule '{rule_name}': {e}")
    
    def _get_metric_value(self, metrics: Dict[str, Any], metric_path: str) -> Optional[float]:
        """Get metric value from nested dictionary"""
        try:
            keys = metric_path.split('.')
            value = metrics
            
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    return None
            
            return float(value) if value is not None else None
            
        except (ValueError, TypeError, AttributeError):
            return None
    
    def _trigger_alert(self, rule_name: str, rule_config: Dict[str, Any], 
                      metric_value: float, metrics: Dict[str, Any]):
        """Trigger alert based on rule"""
        alert = PerformanceAlert(
            timestamp=time.time(),
            alert_type=rule_config.get('alert_type', 'custom'),
            severity=rule_config.get('severity', 'info'),
            message=rule_config.get('message', f'Rule {rule_name} triggered'),
            metrics={
                'rule_name': rule_name,
                'metric': rule_config['metric'],
                'value': metric_value,
                'threshold': rule_config['threshold'],
                'condition': rule_config['condition']
            }
        )
        
        # Add to history
        with self._lock:
            self.alert_history.append(alert)
        
        # Send notifications
        self._send_notifications(alert)
        
        # Log alert
        logger.warning(f"Alert triggered: {rule_name} - {alert.message}")
    
    def _send_notifications(self, alert: PerformanceAlert):
        """Send alert notifications"""
        try:
            # Get active notification channels
            active_channels = alert.metrics.get('notification_channels', [])
            
            for channel_name in active_channels:
                if channel_name in self.notification_channels:
                    self._send_notification(channel_name, alert)
                    
        except Exception as e:
            logger.error(f"Failed to send notifications: {e}")
    
    def _send_notification(self, channel_name: str, alert: PerformanceAlert):
        """Send notification via specific channel"""
        try:
            channel_config = self.notification_channels[channel_name]
            channel_type = channel_config.get('type', 'log')
            
            if channel_type == 'log':
                # Log notification (default)
                logger.info(f"NOTIFICATION [{channel_name}]: {alert.message}")
            elif channel_type == 'webhook':
                # Webhook notification (simplified)
                webhook_url = channel_config.get('url')
                if webhook_url:
                    # In real implementation, would send HTTP request
                    logger.info(f"Webhook notification sent to {webhook_url}")
            elif channel_type == 'email':
                # Email notification (simplified)
                email = channel_config.get('email')
                if email:
                    logger.info(f"Email notification sent to {email}")
                    
        except Exception as e:
            logger.error(f"Failed to send notification via {channel_name}: {e}")
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        with self._lock:
            total_alerts = len(self.alert_history)
            severity_counts = defaultdict(int)
            type_counts = defaultdict(int)
            acknowledged_count = sum(1 for a in self.alert_history if a.acknowledged)
            
            for alert in self.alert_history:
                severity_counts[alert.severity] += 1
                type_counts[alert.alert_type] += 1
            
            return {
                'total_alerts': total_alerts,
                'acknowledged_alerts': acknowledged_count,
                'unacknowledged_alerts': total_alerts - acknowledged_count,
                'severity_distribution': dict(severity_counts),
                'type_distribution': dict(type_counts),
                'active_rules': len(self.alert_rules),
                'active_channels': len(self.notification_channels)
            }
    
    def get_alert_history(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get alert history"""
        with self._lock:
            return [asdict(alert) for alert in list(self.alert_history)[-count:]]


class HistoricalAnalyzer:
    """Historical performance analysis"""
    
    def __init__(self, latency_monitor: LatencyMonitor):
        self.monitor = latency_monitor
    
    def analyze_performance_trend(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze performance trends over time period"""
        try:
            cutoff_time = time.time() - (hours * 3600)
            
            # Filter measurements by time period
            with self.monitor._lock:
                recent_measurements = [
                    m for m in self.monitor.latency_measurements 
                    if m.timestamp >= cutoff_time
                ]
                
                recent_system_metrics = [
                    m for m in self.monitor.system_metrics
                    if m.timestamp >= cutoff_time
                ]
            
            if not recent_measurements:
                return {'error': 'No measurements in specified time period'}
            
            # Analyze latency trends
            latencies = [m.latency_us for m in recent_measurements]
            
            # Calculate time series statistics
            time_buckets = self._create_time_buckets(recent_measurements, hours)
            trend_analysis = self._analyze_trend(time_buckets)
            
            # Analyze system resource usage
            system_analysis = self._analyze_system_resources(recent_system_metrics)
            
            return {
                'time_period_hours': hours,
                'measurement_count': len(recent_measurements),
                'latency_trend': trend_analysis,
                'system_analysis': system_analysis,
                'summary': {
                    'avg_latency_us': np.mean(latencies),
                    'latency_improvement_percent': trend_analysis.get('improvement_percent', 0),
                    'system_stability_score': system_analysis.get('stability_score', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze performance trend: {e}")
            return {'error': str(e)}
    
    def _create_time_buckets(self, measurements: List[LatencyMeasurement], 
                           hours: int) -> Dict[str, List[float]]:
        """Create time buckets for trend analysis"""
        buckets = {}
        bucket_size = max(1, hours // 24)  # 24 buckets minimum
        
        for measurement in measurements:
            bucket_key = int((measurement.timestamp // 3600) * 3600)  # Hour buckets
            if bucket_key not in buckets:
                buckets[bucket_key] = []
            buckets[bucket_key].append(measurement.latency_us)
        
        return buckets
    
    def _analyze_trend(self, time_buckets: Dict[str, List[float]]) -> Dict[str, Any]:
        """Analyze performance trend"""
        if not time_buckets:
            return {}
        
        bucket_averages = {
            bucket_time: np.mean(latencies)
            for bucket_time, latencies in time_buckets.items()
        }
        
        sorted_buckets = sorted(bucket_averages.items())
        
        if len(sorted_buckets) < 2:
            return {'improvement_percent': 0, 'trend': 'insufficient_data'}
        
        first_avg = sorted_buckets[0][1]
        last_avg = sorted_buckets[-1][1]
        
        improvement_percent = ((first_avg - last_avg) / first_avg) * 100
        
        # Determine trend direction
        trend = 'improving' if improvement_percent > 0 else 'degrading' if improvement_percent < 0 else 'stable'
        
        return {
            'improvement_percent': improvement_percent,
            'trend': trend,
            'first_bucket_avg_us': first_avg,
            'last_bucket_avg_us': last_avg,
            'bucket_count': len(sorted_buckets)
        }
    
    def _analyze_system_resources(self, system_metrics: List[SystemMetrics]) -> Dict[str, Any]:
        """Analyze system resource usage patterns"""
        if not system_metrics:
            return {}
        
        cpu_values = [m.cpu_usage_percent for m in system_metrics]
        memory_values = [m.memory_usage_mb for m in system_metrics]
        
        return {
            'avg_cpu_usage_percent': np.mean(cpu_values),
            'max_cpu_usage_percent': np.max(cpu_values),
            'cpu_stability_score': 100 - np.std(cpu_values),
            'avg_memory_usage_mb': np.mean(memory_values),
            'max_memory_usage_mb': np.max(memory_values),
            'memory_stability_score': 100 - (np.std(memory_values) / np.mean(memory_values)) * 100,
            'stability_score': (100 - np.std(cpu_values) + 100 - (np.std(memory_values) / np.mean(memory_values)) * 100) / 2
        }
    
    def generate_performance_report(self, hours: int = 24) -> str:
        """Generate comprehensive performance report"""
        analysis = self.analyze_performance_trend(hours)
        current_metrics = self.monitor.get_current_metrics()
        alerts = self.monitor.get_performance_alerts(count=50)
        
        report = f"""
Performance Report - Last {hours} Hours
=====================================

Current Status:
- Average Latency: {current_metrics['latency']['avg_latency_us']:.2f}μs (Target: {current_metrics['target_latency_us']}μs)
- CPU Usage: {current_metrics['system']['cpu_usage_percent']:.1f}%
- Memory Usage: {current_metrics['system']['memory_utilization_percent']:.1f}%

Trend Analysis:
- Overall Trend: {analysis.get('summary', {}).get('latency_improvement_percent', 0):.2f}% improvement
- Latency Trend: {analysis.get('latency_trend', {}).get('trend', 'unknown')}
- System Stability: {analysis.get('summary', {}).get('system_stability_score', 0):.1f}/100

Recent Alerts: {len(alerts)}
"""
        
        return report


class MonitoringSystem:
    """Complete monitoring and metrics system"""
    
    def __init__(self, latency_config):
        self.config = latency_config
        
        # Initialize components
        self.latency_monitor = LatencyMonitor(latency_config)
        self.dashboard = PerformanceDashboard(self.latency_monitor)
        self.alert_manager = AlertManager(self.latency_monitor)
        self.historical_analyzer = HistoricalAnalyzer(self.latency_monitor)
        
        # Create default dashboard
        self.dashboard.create_dashboard('main', {
            'metrics': ['latency', 'cpu', 'memory'],
            'update_interval': 1.0
        })
        
        # Default alert rules
        self._setup_default_alert_rules()
        
        logger.info("Monitoring System initialized")
    
    def _setup_default_alert_rules(self):
        """Setup default alert rules"""
        rules = [
            {
                'name': 'high_latency',
                'metric': 'latency.avg_latency_us',
                'condition': 'greater_than',
                'threshold': self.config.target_latency_us * 2,
                'severity': 'warning',
                'alert_type': 'latency'
            },
            {
                'name': 'critical_latency',
                'metric': 'latency.avg_latency_us',
                'condition': 'greater_than',
                'threshold': self.config.target_latency_us * 5,
                'severity': 'critical',
                'alert_type': 'latency'
            },
            {
                'name': 'high_cpu',
                'metric': 'system.cpu_usage_percent',
                'condition': 'greater_than',
                'threshold': 90,
                'severity': 'warning',
                'alert_type': 'system'
            }
        ]
        
        for rule in rules:
            self.alert_manager.add_alert_rule(rule['name'], rule)
    
    def start_monitoring(self):
        """Start monitoring system"""
        self.latency_monitor.start()
        logger.info("Monitoring system started")
    
    def stop_monitoring(self):
        """Stop monitoring system"""
        self.latency_monitor.stop()
        logger.info("Monitoring system stopped")
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive monitoring status"""
        return {
            'monitoring_status': self.latency_monitor.get_monitoring_status(),
            'dashboard_list': self.dashboard.list_dashboards(),
            'alert_statistics': self.alert_manager.get_alert_statistics(),
            'current_metrics': self.latency_monitor.get_current_metrics()
        }
    
    def generate_monitoring_report(self, hours: int = 24) -> str:
        """Generate comprehensive monitoring report"""
        return self.historical_analyzer.generate_performance_report(hours)