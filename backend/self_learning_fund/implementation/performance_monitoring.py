"""
Performance Monitoring for Self-Learning Trading Fund
====================================================

Real-time performance monitoring va alerting tizimi.
Metriklarni yig'ish, tahlil qilish va hisobot tayyorlash.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Callable, Union
from datetime import datetime, timedelta
import warnings
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import deque, defaultdict
import threading
import queue
import time
import json
import psutil
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import matplotlib.pyplot as plt
import seaborn as sns

from ..core.base_algorithm import BaseAlgorithm
from ..core.adaptive_model import AdaptiveModel
from ..core.performance_tracker import PerformanceTracker

class MetricType(Enum):
    """Metrik turlari"""
    COUNTER = "Counter"
    GAUGE = "Gauge"
    HISTOGRAM = "Histogram"
    RATE = "Rate"
    TIMER = "Timer"
    PERCENTILE = "Percentile"

class AlertSeverity(Enum):
    """Ogohlantirish darajasi"""
    INFO = "Info"
    WARNING = "Warning"
    ERROR = "Error"
    CRITICAL = "Critical"

class MonitoringLevel(Enum):
    """Monitoring darajasi"""
    BASIC = "Basic"
    STANDARD = "Standard"
    COMPREHENSIVE = "Comprehensive"
    ENTERPRISE = "Enterprise"

@dataclass
class MetricValue:
    """Metrik qiymati"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    unit: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceThreshold:
    """Performance threshold"""
    metric_name: str
    warning_threshold: float
    error_threshold: float
    comparison_operator: str  # '>', '<', '>=', '<=', '=='
    time_window_minutes: int = 5
    consecutive_violations: int = 3

@dataclass
class Alert:
    """Ogohlantirish"""
    alert_id: str
    metric_name: str
    severity: AlertSeverity
    message: str
    threshold_value: float
    actual_value: float
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False
    resolution_time: Optional[datetime] = None

@dataclass
class SystemResource:
    """Tizim resurslari"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, float] = field(default_factory=dict)
    process_count: int
    load_average: Tuple[float, float, float]

class PerformanceMonitor(BaseAlgorithm):
    """Performance monitoring tizimi"""
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        
        self.config = config or {}
        
        # Metrics storage
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.current_metrics: Dict[str, float] = {}
        
        # Alerts
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.thresholds: List[PerformanceThreshold] = []
        
        # Monitoring configuration
        self.monitoring_interval = self.config.get('monitoring_interval', 10)  # seconds
        self.metric_retention_hours = self.config.get('metric_retention_hours', 24)
        self.max_alerts_per_hour = self.config.get('max_alerts_per_hour', 100)
        
        # Threading
        self.running = False
        self.monitoring_threads = []
        self.lock = threading.Lock()
        
        # Performance tracking
        self.performance_tracker = PerformanceTracker()
        
        # System monitoring
        self.system_monitor = SystemResourceMonitor()
        
        # Alert handling
        self.alert_handlers: List[Callable] = []
        
    def start_monitoring(self):
        """Monitoring ni boshlash"""
        
        if self.running:
            logging.warning("Performance monitoring already running")
            return
        
        self.running = True
        
        # Start metric collection thread
        metric_thread = threading.Thread(target=self._metric_collection_worker, daemon=True)
        metric_thread.start()
        self.monitoring_threads.append(metric_thread)
        
        # Start threshold checking thread
        threshold_thread = threading.Thread(target=self._threshold_checking_worker, daemon=True)
        threshold_thread.start()
        self.monitoring_threads.append(threshold_thread)
        
        # Start system monitoring thread
        system_thread = threading.Thread(target=self._system_monitoring_worker, daemon=True)
        system_thread.start()
        self.monitoring_threads.append(system_thread)
        
        # Start cleanup thread
        cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        cleanup_thread.start()
        self.monitoring_threads.append(cleanup_thread)
        
        logging.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Monitoring ni to'xtatish"""
        
        self.running = False
        
        # Wait for threads to finish
        for thread in self.monitoring_threads:
            thread.join(timeout=5.0)
        
        self.monitoring_threads.clear()
        logging.info("Performance monitoring stopped")
    
    def record_metric(self, metric_name: str, value: float, 
                     metric_type: MetricType = MetricType.GAUGE,
                     tags: Optional[Dict[str, str]] = None,
                     unit: Optional[str] = None):
        """Metrik qayd etish"""
        
        metric_value = MetricValue(
            name=metric_name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.now(),
            tags=tags or {},
            unit=unit
        )
        
        with self.lock:
            # Store in history
            self.metrics_history[metric_name].append(metric_value)
            
            # Update current metrics
            if metric_type == MetricType.COUNTER:
                self.current_metrics[metric_name] = self.current_metrics.get(metric_name, 0) + value
            else:
                self.current_metrics[metric_name] = value
    
    def set_threshold(self, metric_name: str, warning_threshold: float,
                     error_threshold: float, comparison_operator: str = '>',
                     time_window_minutes: int = 5):
        """Threshold o'rnatish"""
        
        threshold = PerformanceThreshold(
            metric_name=metric_name,
            warning_threshold=warning_threshold,
            error_threshold=error_threshold,
            comparison_operator=comparison_operator,
            time_window_minutes=time_window_minutes
        )
        
        # Remove existing threshold for this metric
        self.thresholds = [t for t in self.thresholds if t.metric_name != metric_name]
        self.thresholds.append(threshold)
        
        logging.info(f"Set threshold for {metric_name}: warning={warning_threshold}, error={error_threshold}")
    
    def get_metric_summary(self, metric_name: str, 
                          time_window_minutes: int = 60) -> Dict[str, Any]:
        """Metrik xulosasi olish"""
        
        if metric_name not in self.metrics_history:
            return {'error': f'Metric {metric_name} not found'}
        
        # Get recent values
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        recent_metrics = [
            m for m in self.metrics_history[metric_name] 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {'error': 'No data in time window'}
        
        values = [m.value for m in recent_metrics]
        
        return {
            'metric_name': metric_name,
            'sample_count': len(values),
            'time_window_minutes': time_window_minutes,
            'mean': np.mean(values),
            'median': np.median(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'percentiles': {
                'p25': np.percentile(values, 25),
                'p50': np.percentile(values, 50),
                'p75': np.percentile(values, 75),
                'p90': np.percentile(values, 90),
                'p95': np.percentile(values, 95),
                'p99': np.percentile(values, 99)
            },
            'latest_value': values[-1],
            'trend': self._calculate_trend(values[-10:]) if len(values) >= 10 else 'insufficient_data'
        }
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Performance dashboard ma'lumotlari"""
        
        dashboard_data = {
            'timestamp': datetime.now(),
            'current_metrics': self.current_metrics.copy(),
            'active_alerts': len(self.active_alerts),
            'system_health': self.system_monitor.get_current_health(),
            'top_metrics': self._get_top_metrics(),
            'alert_summary': self._get_alert_summary(),
            'performance_summary': self._get_performance_summary()
        }
        
        return dashboard_data
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Ogohlantirishni tasdiqlash"""
        
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            logging.info(f"Alert {alert_id} acknowledged")
            return True
        
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Ogohlantirishni hal qilish"""
        
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolution_time = datetime.now()
            
            # Move to history
            self.alert_history.append(alert)
            del self.active_alerts[alert_id]
            
            logging.info(f"Alert {alert_id} resolved")
            return True
        
        return False
    
    def generate_performance_report(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Performance hisobot yaratish"""
        
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        report = {
            'report_period': {
                'start_time': cutoff_time,
                'end_time': datetime.now(),
                'duration_hours': time_window_hours
            },
            'summary': self._generate_report_summary(cutoff_time),
            'metrics_analysis': self._analyze_metrics(cutoff_time),
            'alert_analysis': self._analyze_alerts(cutoff_time),
            'system_performance': self._analyze_system_performance(cutoff_time),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _metric_collection_worker(self):
        """Metrik yig'ish worker"""
        
        logging.info("Metric collection worker started")
        
        while self.running:
            try:
                # Collect custom metrics (these would be set by the application)
                # In a real implementation, this would interface with application metrics
                
                # Simulate some metrics collection
                self._simulate_metric_collection()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logging.error(f"Metric collection error: {str(e)}")
                time.sleep(self.monitoring_interval)
        
        logging.info("Metric collection worker stopped")
    
    def _threshold_checking_worker(self):
        """Threshold tekshirish worker"""
        
        logging.info("Threshold checking worker started")
        
        while self.running:
            try:
                # Check each threshold
                for threshold in self.thresholds:
                    self._check_threshold(threshold)
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logging.error(f"Threshold checking error: {str(e)}")
                time.sleep(30)
        
        logging.info("Threshold checking worker stopped")
    
    def _system_monitoring_worker(self):
        """Tizim monitoring worker"""
        
        logging.info("System monitoring worker started")
        
        while self.running:
            try:
                # Collect system metrics
                system_resource = self.system_monitor.collect_metrics()
                self._record_system_metrics(system_resource)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logging.error(f"System monitoring error: {str(e)}")
                time.sleep(self.monitoring_interval)
        
        logging.info("System monitoring worker stopped")
    
    def _cleanup_worker(self):
        """Tozalash worker"""
        
        logging.info("Cleanup worker started")
        
        while self.running:
            try:
                # Clean old metrics
                retention_time = datetime.now() - timedelta(hours=self.metric_retention_hours)
                
                with self.lock:
                    for metric_name in self.metrics_history:
                        # Remove old metrics
                        while (self.metrics_history[metric_name] and 
                               self.metrics_history[metric_name][0].timestamp < retention_time):
                            self.metrics_history[metric_name].popleft()
                
                # Clean old alerts from history
                if len(self.alert_history) > 1000:
                    self.alert_history = self.alert_history[-500:]
                
                time.sleep(3600)  # Clean every hour
                
            except Exception as e:
                logging.error(f"Cleanup error: {str(e)}")
                time.sleep(3600)
        
        logging.info("Cleanup worker stopped")
    
    def _simulate_metric_collection(self):
        """Metrik yig'ish simulyatsiya"""
        
        # Simulate application metrics
        self.record_metric('trading_model_accuracy', np.random.uniform(0.7, 0.9))
        self.record_metric('prediction_latency_ms', np.random.uniform(10, 50))
        self.record_metric('trade_execution_time_ms', np.random.uniform(100, 500))
        self.record_metric('portfolio_return_pct', np.random.uniform(-2, 3))
        self.record_metric('risk_score', np.random.uniform(0.1, 0.8))
        self.record_metric('data_quality_score', np.random.uniform(0.8, 1.0))
    
    def _check_threshold(self, threshold: PerformanceThreshold):
        """Threshold tekshirish"""
        
        metric_name = threshold.metric_name
        
        # Check if we have recent data
        if metric_name not in self.current_metrics:
            return
        
        current_value = self.current_metrics[metric_name]
        
        # Check threshold violation
        violation_detected = False
        severity = AlertSeverity.INFO
        
        if threshold.comparison_operator == '>':
            if current_value > threshold.error_threshold:
                violation_detected = True
                severity = AlertSeverity.ERROR
            elif current_value > threshold.warning_threshold:
                violation_detected = True
                severity = AlertSeverity.WARNING
        elif threshold.comparison_operator == '<':
            if current_value < threshold.error_threshold:
                violation_detected = True
                severity = AlertSeverity.ERROR
            elif current_value < threshold.warning_threshold:
                violation_detected = True
                severity = AlertSeverity.WARNING
        
        # Get time window data for confirmation
        if violation_detected:
            cutoff_time = datetime.now() - timedelta(minutes=threshold.time_window_minutes)
            recent_metrics = [
                m for m in self.metrics_history[metric_name]
                if m.timestamp >= cutoff_time
            ]
            
            # Check consecutive violations
            if len(recent_metrics) >= threshold.consecutive_violations:
                violations_in_window = sum(1 for m in recent_metrics[-threshold.consecutive_violations:])
                
                if violations_in_window >= threshold.consecutive_violations:
                    self._trigger_alert(metric_name, severity, current_value, threshold)
    
    def _trigger_alert(self, metric_name: str, severity: AlertSeverity,
                      actual_value: float, threshold: PerformanceThreshold):
        """Ogohlantirish yaratish"""
        
        # Check if similar alert already exists
        existing_alert_key = f"{metric_name}_{severity.value}"
        
        if existing_alert_key in self.active_alerts:
            # Update existing alert
            alert = self.active_alerts[existing_alert_key]
            alert.actual_value = actual_value
            alert.timestamp = datetime.now()
        else:
            # Create new alert
            alert_id = f"{metric_name}_{severity.value}_{int(time.time())}"
            
            message = self._generate_alert_message(metric_name, severity, actual_value, threshold)
            
            alert = Alert(
                alert_id=alert_id,
                metric_name=metric_name,
                severity=severity,
                message=message,
                threshold_value=threshold.error_threshold if severity == AlertSeverity.ERROR else threshold.warning_threshold,
                actual_value=actual_value,
                timestamp=datetime.now()
            )
            
            self.active_alerts[existing_alert_key] = alert
            logging.warning(f"Alert triggered: {message}")
            
            # Trigger alert handlers
            self._handle_alert(alert)
    
    def _generate_alert_message(self, metric_name: str, severity: AlertSeverity,
                              actual_value: float, threshold: PerformanceThreshold) -> str:
        """Ogohlantirish xabari yaratish"""
        
        if severity == AlertSeverity.ERROR:
            return f"CRITICAL: {metric_name} = {actual_value:.3f} exceeded error threshold {threshold.error_threshold:.3f}"
        elif severity == AlertSeverity.WARNING:
            return f"WARNING: {metric_name} = {actual_value:.3f} exceeded warning threshold {threshold.warning_threshold:.3f}"
        else:
            return f"INFO: {metric_name} = {actual_value:.3f}"
    
    def _handle_alert(self, alert: Alert):
        """Ogohlantirishni qayta ishlash"""
        
        # Execute alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logging.error(f"Alert handler error: {str(e)}")
    
    def _record_system_metrics(self, system_resource: SystemResource):
        """Tizim metriklarini qayd etish"""
        
        self.record_metric('system_cpu_percent', system_resource.cpu_percent)
        self.record_metric('system_memory_percent', system_resource.memory_percent)
        self.record_metric('system_disk_usage_percent', system_resource.disk_usage_percent)
        self.record_metric('system_process_count', system_resource.process_count)
        self.record_metric('system_load_avg_1min', system_resource.load_average[0])
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Trend hisoblash"""
        
        if len(values) < 2:
            return 'insufficient_data'
        
        # Simple linear trend
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if abs(slope) < 0.001:
            return 'stable'
        elif slope > 0:
            return 'increasing'
        else:
            return 'decreasing'
    
    def _get_top_metrics(self) -> List[Dict[str, Any]]:
        """Eng muhim metriklar"""
        
        top_metrics = [
            'trading_model_accuracy',
            'portfolio_return_pct',
            'risk_score',
            'prediction_latency_ms',
            'data_quality_score'
        ]
        
        results = []
        for metric in top_metrics:
            if metric in self.current_metrics:
                summary = self.get_metric_summary(metric, time_window_minutes=60)
                if 'error' not in summary:
                    results.append({
                        'name': metric,
                        'current_value': summary['latest_value'],
                        'mean': summary['mean'],
                        'trend': summary['trend']
                    })
        
        return results
    
    def _get_alert_summary(self) -> Dict[str, int]:
        """Ogohlantirish xulosasi"""
        
        summary = defaultdict(int)
        
        for alert in self.active_alerts.values():
            summary[alert.severity.value] += 1
        
        # Add resolved alerts from history (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        for alert in self.alert_history:
            if alert.timestamp >= cutoff_time:
                summary[f"{alert.severity.value}_resolved"] += 1
        
        return dict(summary)
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Performance xulosasi"""
        
        # Get key metrics summaries
        accuracy_summary = self.get_metric_summary('trading_model_accuracy', 60)
        latency_summary = self.get_metric_summary('prediction_latency_ms', 60)
        return_summary = self.get_metric_summary('portfolio_return_pct', 60)
        
        return {
            'model_accuracy': accuracy_summary.get('mean', 0),
            'avg_latency_ms': latency_summary.get('mean', 0),
            'portfolio_return_pct': return_summary.get('mean', 0),
            'system_health_score': self._calculate_system_health_score()
        }
    
    def _calculate_system_health_score(self) -> float:
        """Tizim sog'lik balli"""
        
        cpu = self.current_metrics.get('system_cpu_percent', 0)
        memory = self.current_metrics.get('system_memory_percent', 0)
        disk = self.current_metrics.get('system_disk_usage_percent', 0)
        
        # Higher is better health score
        cpu_score = max(0, 100 - cpu)
        memory_score = max(0, 100 - memory)
        disk_score = max(0, 100 - disk)
        
        return (cpu_score + memory_score + disk_score) / 3
    
    def _generate_report_summary(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Hisobot xulosasi"""
        
        total_metrics = sum(len(history) for history in self.metrics_history.values())
        total_alerts = len([a for a in self.alert_history if a.timestamp >= cutoff_time])
        active_alerts = len(self.active_alerts)
        
        return {
            'total_metric_observations': total_metrics,
            'time_window_hours': (datetime.now() - cutoff_time).total_seconds() / 3600,
            'total_alerts_generated': total_alerts,
            'active_alerts': active_alerts,
            'monitored_metrics': len(self.metrics_history),
            'system_uptime_hours': (datetime.now() - cutoff_time).total_seconds() / 3600
        }
    
    def _analyze_metrics(self, cutoff_time: datetime) -> Dict[str, Dict[str, Any]]:
        """Metrik tahlili"""
        
        analysis = {}
        
        for metric_name, history in self.metrics_history.items():
            recent_metrics = [m for m in history if m.timestamp >= cutoff_time]
            
            if recent_metrics:
                values = [m.value for m in recent_metrics]
                
                analysis[metric_name] = {
                    'observations': len(values),
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'trend': self._calculate_trend(values[-10:] if len(values) >= 10 else values),
                    'min_value': np.min(values),
                    'max_value': np.max(values),
                    'coefficient_of_variation': np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
                }
        
        return analysis
    
    def _analyze_alerts(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Ogohlantirish tahlili"""
        
        recent_alerts = [a for a in self.alert_history if a.timestamp >= cutoff_time]
        
        if not recent_alerts:
            return {'message': 'No alerts in time window'}
        
        severity_counts = defaultdict(int)
        metric_counts = defaultdict(int)
        resolution_times = []
        
        for alert in recent_alerts:
            severity_counts[alert.severity.value] += 1
            metric_counts[alert.metric_name] += 1
            
            if alert.resolved and alert.resolution_time:
                resolution_time = (alert.resolution_time - alert.timestamp).total_seconds() / 60
                resolution_times.append(resolution_time)
        
        return {
            'total_alerts': len(recent_alerts),
            'severity_distribution': dict(severity_counts),
            'most_frequent_metrics': dict(sorted(metric_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            'average_resolution_time_minutes': np.mean(resolution_times) if resolution_times else None,
            'resolution_rate': len([a for a in recent_alerts if a.resolved]) / len(recent_alerts)
        }
    
    def _analyze_system_performance(self, cutoff_time: datetime) -> Dict[str, Any]:
        """Tizim performance tahlili"""
        
        # This would analyze system resource metrics over time
        return {
            'average_cpu_usage': self.current_metrics.get('system_cpu_percent', 0),
            'average_memory_usage': self.current_metrics.get('system_memory_percent', 0),
            'average_disk_usage': self.current_metrics.get('system_disk_usage_percent', 0),
            'health_score': self._calculate_system_health_score()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Tavsiyalar"""
        
        recommendations = []
        
        # Check system health
        if self._calculate_system_health_score() < 70:
            recommendations.append("System health is low. Consider scaling resources or optimizing performance.")
        
        # Check alert frequency
        recent_alerts = [a for a in self.alert_history if a.timestamp >= datetime.now() - timedelta(hours=24)]
        if len(recent_alerts) > 50:
            recommendations.append("High alert frequency detected. Review thresholds and system stability.")
        
        # Check model performance
        accuracy = self.current_metrics.get('trading_model_accuracy', 0)
        if accuracy < 0.6:
            recommendations.append("Model accuracy is below acceptable threshold. Consider model retraining.")
        
        return recommendations

class SystemResourceMonitor:
    """Tizim resurslari monitoring"""
    
    def collect_metrics(self) -> SystemResource:
        """Tizim metriklarini yig'ish"""
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage_percent = (disk.used / disk.total) * 100
        
        # Network I/O
        network_io = psutil.net_io_counters()
        network_data = {
            'bytes_sent': network_io.bytes_sent,
            'bytes_recv': network_io.bytes_recv,
            'packets_sent': network_io.packets_sent,
            'packets_recv': network_io.packets_recv
        }
        
        # Process count
        process_count = len(psutil.pids())
        
        # Load average (Unix-like systems)
        try:
            load_avg = psutil.getloadavg()
        except AttributeError:
            load_avg = (0.0, 0.0, 0.0)  # Windows fallback
        
        return SystemResource(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_usage_percent=disk_usage_percent,
            network_io=network_data,
            process_count=process_count,
            load_average=load_avg
        )
    
    def get_current_health(self) -> Dict[str, Any]:
        """Joriy tizim sog'ligi"""
        
        resource = self.collect_metrics()
        
        return {
            'cpu_health': 'good' if resource.cpu_percent < 80 else 'warning' if resource.cpu_percent < 95 else 'critical',
            'memory_health': 'good' if resource.memory_percent < 85 else 'warning' if resource.memory_percent < 95 else 'critical',
            'disk_health': 'good' if resource.disk_usage_percent < 90 else 'warning' if resource.disk_usage_percent < 95 else 'critical',
            'overall_score': self._calculate_health_score(resource)
        }
    
    def _calculate_health_score(self, resource: SystemResource) -> float:
        """Sog'lik balli hisoblash"""
        
        cpu_score = max(0, 100 - resource.cpu_percent)
        memory_score = max(0, 100 - resource.memory_percent)
        disk_score = max(0, 100 - resource.disk_usage_percent)
        
        return (cpu_score + memory_score + disk_score) / 3

class AlertHandler:
    """Ogohlantirish boshqaruvchi"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.email_config = self.config.get('email', {})
        self.webhook_config = self.config.get('webhook', {})
    
    def email_alert(self, alert: Alert):
        """Email orqali ogohlantirish"""
        
        if not self.email_config.get('enabled', False):
            return
        
        try:
            msg = MimeMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = self.email_config['to_email']
            msg['Subject'] = f"[{alert.severity.value}] Performance Alert"
            
            body = f"""
            Performance Alert Details:
            
            Metric: {alert.metric_name}
            Severity: {alert.severity.value}
            Message: {alert.message}
            Threshold: {alert.threshold_value}
            Actual Value: {alert.actual_value}
            Time: {alert.timestamp}
            
            Please investigate the issue.
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Send email (simplified - would need proper SMTP setup)
            # server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            # server.starttls()
            # server.login(self.email_config['username'], self.email_config['password'])
            # server.send_message(msg)
            # server.quit()
            
            logging.info(f"Email alert sent for {alert.metric_name}")
            
        except Exception as e:
            logging.error(f"Failed to send email alert: {str(e)}")
    
    def log_alert(self, alert: Alert):
        """Log orqali ogohlantirish"""
        
        log_message = f"ALERT: {alert.severity.value} - {alert.message}"
        
        if alert.severity == AlertSeverity.CRITICAL:
            logging.critical(log_message)
        elif alert.severity == AlertSeverity.ERROR:
            logging.error(log_message)
        elif alert.severity == AlertSeverity.WARNING:
            logging.warning(log_message)
        else:
            logging.info(log_message)

# Demo va test
if __name__ == "__main__":
    # Performance monitor testi
    monitor = PerformanceMonitor({
        'monitoring_interval': 5,
        'metric_retention_hours': 2,
        'max_alerts_per_hour': 50
    })
    
    print("=== PERFORMANCE MONITOR TEST ===")
    
    # Add alert handlers
    alert_handler = AlertHandler()
    monitor.alert_handlers.append(alert_handler.log_alert)
    
    # Set thresholds
    monitor.set_threshold('trading_model_accuracy', 0.6, 0.5, '<')
    monitor.set_threshold('prediction_latency_ms', 100, 200, '>')
    monitor.set_threshold('system_cpu_percent', 80, 95, '>')
    
    # Start monitoring
    monitor.start_monitoring()
    
    try:
        # Simulate some activity
        for i in range(30):
            time.sleep(2)
            
            # Simulate some performance degradation
            if i == 15:
                # Simulate low accuracy
                monitor.record_metric('trading_model_accuracy', 0.45)
                monitor.record_metric('prediction_latency_ms', 150)
            
            # Get dashboard
            if i % 10 == 0:
                dashboard = monitor.get_performance_dashboard()
                print(f"\n=== DASHBOARD (Iteration {i}) ===")
                print(f"Current metrics: {len(dashboard['current_metrics'])}")
                print(f"Active alerts: {dashboard['active_alerts']}")
                print(f"System health: {dashboard['system_health']}")
                
                # Get metric summary
                accuracy_summary = monitor.get_metric_summary('trading_model_accuracy', 10)
                if 'error' not in accuracy_summary:
                    print(f"Model accuracy: {accuracy_summary['mean']:.3f} (trend: {accuracy_summary['trend']})")
        
        # Test alert acknowledgment
        if monitor.active_alerts:
            alert_id = list(monitor.active_alerts.keys())[0]
            success = monitor.acknowledge_alert(alert_id)
            print(f"Alert acknowledged: {success}")
        
        # Test alert resolution
        if monitor.active_alerts:
            alert_id = list(monitor.active_alerts.keys())[0]
            success = monitor.resolve_alert(alert_id)
            print(f"Alert resolved: {success}")
        
        # Generate performance report
        print("\n=== GENERATING PERFORMANCE REPORT ===")
        report = monitor.generate_performance_report(time_window_hours=1)
        
        print(f"Report period: {report['report_period']['start_time']} to {report['report_period']['end_time']}")
        print(f"Total observations: {report['summary']['total_metric_observations']}")
        print(f"Active alerts: {report['summary']['active_alerts']}")
        print(f"Recommendations: {len(report['recommendations'])}")
        
        for rec in report['recommendations']:
            print(f"  - {rec}")
        
    finally:
        monitor.stop_monitoring()
    
    print("\n=== PERFORMANCE MONITOR TEST COMPLETED ===")