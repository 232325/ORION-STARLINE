"""
Monitoring Service
=================

System monitoring and alerting for HFT operations
"""

import time
import logging
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class Metric:
    """System metric"""
    name: str
    value: float
    timestamp: float
    unit: str = ""
    category: str = ""

@dataclass
class Alert:
    """Alert definition"""
    alert_id: str
    metric_name: str
    threshold: float
    current_value: float
    severity: str  # 'info', 'warning', 'error', 'critical'
    timestamp: float

class MonitoringService:
    """System Monitoring Service"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Monitoring settings
        self.monitoring_interval = config.get('monitoring_interval', 1)  # seconds
        self.alert_thresholds = config.get('alert_thresholds', {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'latency_us': 100.0,
            'error_rate': 0.05,
            'throughput': 1000
        })
        
        # Metrics storage
        self.metrics_history: Dict[str, List[Metric]] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_count = 0
        
        # System statistics
        self.start_time = time.time()
        self.total_operations = 0
        self.error_count = 0
        
    async def initialize(self) -> bool:
        """Initialize monitoring service"""
        try:
            self.logger.info("Initializing Monitoring Service...")
            
            # Start monitoring loop
            asyncio.create_task(self._monitoring_loop())
            
            self.logger.info("Monitoring Service initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Monitoring Service: {e}")
            return False
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                await self._collect_metrics()
                await self._check_alerts()
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
    
    async def _collect_metrics(self):
        """Collect system metrics"""
        import psutil
        import random
        
        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Add system metrics
        self._add_metric('cpu_usage', cpu_percent, '%', 'system')
        self._add_metric('memory_usage', memory.percent, '%', 'system')
        self._add_metric('disk_usage', disk.percent, '%', 'system')
        
        # Simulate trading metrics
        latency_us = random.uniform(10, 200)
        throughput = random.randint(800, 1200)
        error_rate = random.uniform(0, 0.1)
        
        self._add_metric('latency_us', latency_us, 'μs', 'trading')
        self._add_metric('throughput', throughput, 'ops/sec', 'trading')
        self._add_metric('error_rate', error_rate, '%', 'trading')
        
        # Update totals
        self.total_operations += throughput
    
    def _add_metric(self, name: str, value: float, unit: str, category: str):
        """Add metric to history"""
        metric = Metric(
            name=name,
            value=value,
            timestamp=time.time(),
            unit=unit,
            category=category
        )
        
        if name not in self.metrics_history:
            self.metrics_history[name] = []
        
        self.metrics_history[name].append(metric)
        
        # Keep only recent metrics
        if len(self.metrics_history[name]) > 1000:
            self.metrics_history[name] = self.metrics_history[name][-500:]
    
    async def _check_alerts(self):
        """Check metrics against thresholds"""
        current_time = time.time()
        
        for metric_name, metrics in self.metrics_history.items():
            if not metrics:
                continue
            
            latest_metric = metrics[-1]
            threshold = self.alert_thresholds.get(metric_name)
            
            if threshold is None:
                continue
            
            alert_key = f"{metric_name}_alert"
            
            # Check if metric exceeds threshold
            exceeds_threshold = self._check_threshold(latest_metric.value, threshold)
            
            if exceeds_threshold:
                # Create alert if not already active
                if alert_key not in self.active_alerts:
                    severity = self._determine_severity(latest_metric.value, threshold)
                    
                    alert = Alert(
                        alert_id=f"{alert_key}_{int(current_time * 1000000)}",
                        metric_name=metric_name,
                        threshold=threshold,
                        current_value=latest_metric.value,
                        severity=severity,
                        timestamp=current_time
                    )
                    
                    self.active_alerts[alert_key] = alert
                    self._handle_alert(alert)
                    
            else:
                # Remove alert if metric returns to normal
                if alert_key in self.active_alerts:
                    del self.active_alerts[alert_key]
    
    def _check_threshold(self, value: float, threshold: float) -> bool:
        """Check if value exceeds threshold"""
        # For most metrics, exceed threshold if value > threshold
        # For some metrics like throughput, it's the opposite
        if 'throughput' in str(value):
            return value < threshold  # Low throughput is bad
        else:
            return value > threshold  # High usage is bad
    
    def _determine_severity(self, value: float, threshold: float) -> str:
        """Determine alert severity"""
        ratio = value / threshold if threshold > 0 else 1.0
        
        if ratio < 1.1:
            return 'info'
        elif ratio < 1.5:
            return 'warning'
        elif ratio < 2.0:
            return 'error'
        else:
            return 'critical'
    
    def _handle_alert(self, alert: Alert):
        """Handle alert"""
        self.alert_count += 1
        
        # Log alert
        log_level = {
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }.get(alert.severity, logging.WARNING)
        
        self.logger.log(
            log_level,
            f"ALERT [{alert.severity.upper()}]: {alert.metric_name} = {alert.current_value:.2f} "
            f"(threshold: {alert.threshold:.2f})"
        )
        
        # Send alert notification (in real system, this would send to monitoring systems)
        if alert.severity in ['error', 'critical']:
            self._send_alert_notification(alert)
    
    def _send_alert_notification(self, alert: Alert):
        """Send alert notification"""
        # In real implementation, this would send notifications to:
        # - Email
        # - Slack/Teams
        # - PagerDuty
        # - SMS
        # - Dashboard alerts
        
        self.logger.info(f"Alert notification sent: {alert.alert_id}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get monitoring dashboard data"""
        uptime = time.time() - self.start_time
        
        # Calculate recent averages
        recent_metrics = {}
        for metric_name, metrics in self.metrics_history.items():
            if metrics:
                recent_values = [m.value for m in metrics[-10:]]
                recent_metrics[metric_name] = {
                    'current': metrics[-1].value,
                    'average': sum(recent_values) / len(recent_values),
                    'unit': metrics[-1].unit,
                    'category': metrics[-1].category
                }
        
        return {
            'uptime_seconds': uptime,
            'total_operations': self.total_operations,
            'total_alerts': self.alert_count,
            'active_alerts': len(self.active_alerts),
            'metrics': recent_metrics,
            'active_alerts_detail': [alert.__dict__ for alert in self.active_alerts.values()],
            'system_health': self._calculate_system_health()
        }
    
    def _calculate_system_health(self) -> str:
        """Calculate overall system health"""
        if not self.metrics_history:
            return 'unknown'
        
        # Check critical metrics
        cpu_usage = self.metrics_history.get('cpu_usage', [])
        memory_usage = self.metrics_history.get('memory_usage', [])
        
        if cpu_usage and memory_usage:
            latest_cpu = cpu_usage[-1].value
            latest_memory = memory_usage[-1].value
            
            if latest_cpu > 90 or latest_memory > 90:
                return 'critical'
            elif latest_cpu > 80 or latest_memory > 80:
                return 'warning'
            else:
                return 'healthy'
        
        return 'unknown'
    
    async def shutdown(self):
        """Shutdown monitoring service"""
        self.logger.info("Shutting down Monitoring Service")