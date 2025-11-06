"""
Real-time Monitor Module - Orion Starline AI Trading System
Author: AI Development Team
Description: Live performance monitoring, alerting, and anomaly detection
"""

import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import pandas as pd
from collections import deque, defaultdict
import statistics
import math
import warnings
warnings.filterwarnings('ignore')

# Import performance tracker
from performance_tracker import PerformanceTracker, PerformanceSnapshot


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MonitoringMode(Enum):
    """Monitoring modes"""
    PASSIVE = "passive"      # Monitoring only
    ACTIVE = "active"        # Active intervention
    PREDICTIVE = "predictive"  # AI-driven monitoring
    ADAPTIVE = "adaptive"     # Self-adjusting thresholds


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    metric: str
    condition: str  # 'gt', 'lt', 'eq', 'crosses_up', 'crosses_down'
    threshold: float
    severity: AlertSeverity
    enabled: bool = True
    cooldown_minutes: int = 60
    notification_channels: List[str] = None
    description: str = ""


@dataclass
class Alert:
    """Performance alert"""
    id: str
    timestamp: datetime
    rule_name: str
    metric: str
    current_value: float
    threshold: float
    severity: AlertSeverity
    message: str
    acknowledged: bool = False
    resolved: bool = False
    resolution_time: Optional[datetime] = None


@dataclass
class AnomalyDetection:
    """Anomaly detection result"""
    metric: str
    timestamp: datetime
    value: float
    expected_range: Tuple[float, float]
    deviation_score: float
    confidence: float
    anomaly_type: str
    recommendations: List[str]


@dataclass
class PredictiveAlert:
    """Predictive alert based on trends"""
    metric: str
    predicted_value: float
    prediction_confidence: float
    time_horizon_minutes: int
    alert_probability: float
    preventive_actions: List[str]


class TrendAnalyzer:
    """Real-time trend analysis and detection"""
    
    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.data_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
    
    def update_metric(self, metric_name: str, value: float, timestamp: datetime) -> None:
        """Update metric in trend window"""
        self.data_windows[metric_name].append((timestamp, value))
    
    def detect_trend(self, metric_name: str) -> Dict[str, Any]:
        """Detect trend direction and strength"""
        if len(self.data_windows[metric_name]) < 5:
            return {'trend': 'insufficient_data', 'strength': 0, 'confidence': 0}
        
        # Get recent data
        recent_data = list(self.data_windows[metric_name])
        values = [val for _, val in recent_data]
        
        if len(values) < 2:
            return {'trend': 'insufficient_data', 'strength': 0, 'confidence': 0}
        
        # Calculate trend metrics
        first_val, last_val = values[0], values[-1]
        mean_val = statistics.mean(values)
        stdev_val = statistics.stdev(values) if len(values) > 1 else 0
        
        # Trend direction
        change_pct = (last_val - first_val) / abs(first_val) if first_val != 0 else 0
        
        if change_pct > 0.01:  # 1% threshold
            trend = 'upward'
        elif change_pct < -0.01:
            trend = 'downward'
        else:
            trend = 'sideways'
        
        # Trend strength (correlation with time)
        time_indices = list(range(len(values)))
        if len(time_indices) > 1 and stdev_val > 0:
            correlation = np.corrcoef(time_indices, values)[0, 1] if not np.isnan(np.corrcoef(time_indices, values)[0, 1]) else 0
            strength = abs(correlation)
        else:
            strength = 0
        
        # Confidence based on data consistency
        if stdev_val > 0:
            confidence = min(1.0, stdev_val / abs(mean_val)) if mean_val != 0 else 0
        else:
            confidence = 1.0
        
        return {
            'trend': trend,
            'strength': strength,
            'confidence': confidence,
            'change_pct': change_pct,
            'last_value': last_val,
            'mean_value': mean_val
        }
    
    def detect_anomalies(self, metric_name: str, threshold_std: float = 2.0) -> List[AnomalyDetection]:
        """Detect statistical anomalies in metrics"""
        if len(self.data_windows[metric_name]) < 10:
            return []
        
        recent_data = list(self.data_windows[metric_name])
        values = [val for _, val in recent_data]
        
        if len(values) < 5:
            return []
        
        mean_val = statistics.mean(values)
        stdev_val = statistics.stdev(values)
        
        if stdev_val == 0:
            return []
        
        anomalies = []
        current_value = values[-1]
        z_score = abs(current_value - mean_val) / stdev_val
        
        if z_score > threshold_std:
            # Determine expected range
            expected_range = (mean_val - 2*stdev_val, mean_val + 2*stdev_val)
            
            # Generate recommendations
            recommendations = []
            if current_value > expected_range[1]:
                recommendations.append(f"Value significantly above normal range")
                recommendations.append("Review recent market conditions")
                recommendations.append("Check for system performance issues")
            else:
                recommendations.append(f"Value significantly below normal range")
                recommendations.append("Investigate potential technical issues")
                recommendations.append("Monitor for further deterioration")
            
            anomaly = AnomalyDetection(
                metric=metric_name,
                timestamp=recent_data[-1][0],
                value=current_value,
                expected_range=expected_range,
                deviation_score=z_score,
                confidence=min(1.0, z_score / 3.0),
                anomaly_type='statistical_outlier',
                recommendations=recommendations
            )
            anomalies.append(anomaly)
        
        return anomalies


class RealTimeMonitor:
    """
    Real-time Performance Monitoring System
    Advanced live monitoring with AI-driven predictions and alerts
    """
    
    def __init__(self, performance_tracker: PerformanceTracker, config: Dict[str, Any] = None):
        self.performance_tracker = performance_tracker
        self.config = config or self._default_config()
        self.logger = self._setup_logging()
        
        # Core monitoring components
        self.monitoring_mode = MonitoringMode.PASSIVE
        self.active_monitors: Dict[str, Callable] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        
        # Real-time data
        self.metric_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.current_metrics: Dict[str, float] = {}
        self.trend_analyzer = TrendAnalyzer()
        self.last_update: Dict[str, datetime] = {}
        
        # Alert management
        self.alert_callbacks: List[Callable] = []
        self.alert_thresholds: Dict[str, Tuple[float, float]] = {}
        self.cooldown_tracker: Dict[str, datetime] = {}
        
        # Anomaly detection
        self.anomaly_detector = TrendAnalyzer()
        self.baseline_metrics: Dict[str, float] = {}
        self.learning_period_hours: int = 24
        self.learning_data: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)
        
        # Predictive analytics
        self.prediction_models: Dict[str, Any] = {}
        self.trend_predictions: Dict[str, PredictiveAlert] = {}
        self.prediction_confidence_threshold: float = 0.7
        
        # System health monitoring
        self.system_health_metrics: Dict[str, float] = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'response_time': 0.0,
            'error_rate': 0.0,
            'throughput': 0.0
        }
        
        self._initialize_alert_rules()
        self._initialize_baseline_metrics()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            'update_frequency_seconds': 1,
            'max_alerts_per_hour': 10,
            'alert_cooldown_minutes': 15,
            'enable_predictive_alerts': True,
            'enable_anomaly_detection': True,
            'enable_performance_predictions': True,
            'learning_period_hours': 24,
            'alert_thresholds': {
                'win_rate_min': 0.3,
                'win_rate_max': 0.9,
                'drawdown_max': 0.15,
                'var_max': 0.1,
                'response_time_max': 5.0,
                'error_rate_max': 0.05
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('RealTimeMonitor')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_alert_rules(self) -> None:
        """Initialize default alert rules"""
        rules = [
            AlertRule(
                name="Low Win Rate",
                metric="win_rate",
                condition="lt",
                threshold=self.config['alert_thresholds']['win_rate_min'],
                severity=AlertSeverity.WARNING,
                description="Win rate below minimum threshold"
            ),
            AlertRule(
                name="High Drawdown",
                metric="max_drawdown",
                condition="gt",
                threshold=self.config['alert_thresholds']['drawdown_max'],
                severity=AlertSeverity.CRITICAL,
                description="Drawdown exceeds risk limits"
            ),
            AlertRule(
                name="High VaR",
                metric="var_95",
                condition="gt",
                threshold=self.config['alert_thresholds']['var_max'],
                severity=AlertSeverity.WARNING,
                description="Value at Risk above threshold"
            ),
            AlertRule(
                name="Slow Response",
                metric="response_time",
                condition="gt",
                threshold=self.config['alert_thresholds']['response_time_max'],
                severity=AlertSeverity.WARNING,
                description="System response time degraded"
            ),
            AlertRule(
                name="High Error Rate",
                metric="error_rate",
                condition="gt",
                threshold=self.config['alert_thresholds']['error_rate_max'],
                severity=AlertSeverity.CRITICAL,
                description="High error rate detected"
            )
        ]
        
        for rule in rules:
            self.alert_rules[rule.name] = rule
    
    def _initialize_baseline_metrics(self) -> None:
        """Initialize baseline performance metrics"""
        self.baseline_metrics = {
            'win_rate': 0.55,
            'sharpe_ratio': 1.2,
            'max_drawdown': 0.05,
            'volatility': 0.15,
            'response_time': 1.0,
            'trades_per_day': 20,
            'avg_profit_per_trade': 50.0
        }
    
    def start_monitoring(self) -> None:
        """Start real-time monitoring"""
        self.logger.info("Starting real-time monitoring system")
        self.monitoring_mode = MonitoringMode.ACTIVE
        
        # Start monitoring tasks
        self._start_monitoring_loop()
        self._start_performance_analysis()
        self._start_anomaly_detection()
        
        if self.config['enable_predictive_alerts']:
            self._start_predictive_analysis()
        
        self.logger.info("Real-time monitoring active")
    
    def stop_monitoring(self) -> None:
        """Stop monitoring"""
        self.logger.info("Stopping real-time monitoring")
        self.monitoring_mode = MonitoringMode.PASSIVE
    
    def _start_monitoring_loop(self) -> None:
        """Start main monitoring loop"""
        async def monitoring_task():
            while self.monitoring_mode in [MonitoringMode.ACTIVE, MonitoringMode.PREDICTIVE]:
                try:
                    self._update_current_metrics()
                    self._check_alert_rules()
                    self._update_trend_analysis()
                    await asyncio.sleep(self.config['update_frequency_seconds'])
                except Exception as e:
                    self.logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(5)
        
        asyncio.create_task(monitoring_task())
    
    def _start_performance_analysis(self) -> None:
        """Start performance analysis tasks"""
        async def analysis_task():
            while self.monitoring_mode in [MonitoringMode.ACTIVE, MonitoringMode.PREDICTIVE]:
                try:
                    self._analyze_performance_trends()
                    self._update_dashboards()
                    await asyncio.sleep(60)  # Every minute
                except Exception as e:
                    self.logger.error(f"Error in performance analysis: {e}")
                    await asyncio.sleep(60)
        
        asyncio.create_task(analysis_task())
    
    def _start_anomaly_detection(self) -> None:
        """Start anomaly detection"""
        async def anomaly_task():
            while self.monitoring_mode in [MonitoringMode.ACTIVE, MonitoringMode.PREDICTIVE]:
                try:
                    self._detect_performance_anomalies()
                    await asyncio.sleep(30)  # Every 30 seconds
                except Exception as e:
                    self.logger.error(f"Error in anomaly detection: {e}")
                    await asyncio.sleep(30)
        
        asyncio.create_task(anomaly_task())
    
    def _start_predictive_analysis(self) -> None:
        """Start predictive analysis"""
        async def prediction_task():
            while self.monitoring_mode in [MonitoringMode.PREDICTIVE, MonitoringMode.ADAPTIVE]:
                try:
                    self._generate_performance_predictions()
                    await asyncio.sleep(300)  # Every 5 minutes
                except Exception as e:
                    self.logger.error(f"Error in predictive analysis: {e}")
                    await asyncio.sleep(300)
        
        asyncio.create_task(prediction_task())
    
    def _update_current_metrics(self) -> None:
        """Update current performance metrics"""
        try:
            # Get real-time metrics from performance tracker
            real_time_data = self.performance_tracker._calculate_real_time_metrics()
            
            # Add system metrics
            real_time_data.update(self._get_system_metrics())
            
            # Update buffer and current metrics
            current_time = datetime.now()
            for metric, value in real_time_data.items():
                if isinstance(value, (int, float)):
                    self.current_metrics[metric] = value
                    self.metric_buffer[metric].append((current_time, value))
                    self.trend_analyzer.update_metric(metric, value, current_time)
                    self.last_update[metric] = current_time
            
            # Learning period update
            self._update_learning_data(real_time_data, current_time)
            
        except Exception as e:
            self.logger.error(f"Error updating current metrics: {e}")
    
    def _get_system_metrics(self) -> Dict[str, float]:
        """Get current system performance metrics"""
        import psutil
        
        try:
            return {
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_io': psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv,
                'response_time': self._measure_response_time(),
                'error_rate': self._calculate_error_rate()
            }
        except Exception as e:
            self.logger.error(f"Error getting system metrics: {e}")
            return {}
    
    def _measure_response_time(self) -> float:
        """Measure system response time"""
        start_time = time.time()
        try:
            # Simple response time test
            _ = len(self.current_metrics)
            return time.time() - start_time
        except:
            return 0.0
    
    def _calculate_error_rate(self) -> float:
        """Calculate current error rate"""
        # This would track actual errors in a production system
        # For now, return a simulated value
        return 0.01
    
    def _update_learning_data(self, metrics: Dict[str, float], timestamp: datetime) -> None:
        """Update learning data for baseline calculation"""
        for metric, value in metrics.items():
            if isinstance(value, (int, float)):
                self.learning_data[metric].append((timestamp, value))
                
                # Keep only recent data
                cutoff_time = timestamp - timedelta(hours=self.learning_period_hours)
                self.learning_data[metric] = [
                    (ts, val) for ts, val in self.learning_data[metric] 
                    if ts >= cutoff_time
                ]
    
    def _check_alert_rules(self) -> None:
        """Check all alert rules against current metrics"""
        current_time = datetime.now()
        
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
            
            # Check cooldown
            if rule.name in self.cooldown_tracker:
                if current_time - self.cooldown_tracker[rule.name] < timedelta(minutes=rule.cooldown_minutes):
                    continue
            
            # Get current value
            current_value = self.current_metrics.get(rule.metric, 0.0)
            
            # Check condition
            if self._check_rule_condition(rule, current_value):
                alert = self._create_alert(rule, current_value, current_time)
                if self._should_send_alert(alert):
                    self._send_alert(alert)
                    self.cooldown_tracker[rule.name] = current_time
    
    def _check_rule_condition(self, rule: AlertRule, current_value: float) -> bool:
        """Check if alert rule condition is met"""
        if rule.condition == "gt":
            return current_value > rule.threshold
        elif rule.condition == "lt":
            return current_value < rule.threshold
        elif rule.condition == "eq":
            return abs(current_value - rule.threshold) < 0.001
        elif rule.condition == "crosses_up":
            # This would need previous value tracking
            return current_value > rule.threshold
        elif rule.condition == "crosses_down":
            return current_value < rule.threshold
        else:
            return False
    
    def _create_alert(self, rule: AlertRule, current_value: float, timestamp: datetime) -> Alert:
        """Create alert from rule violation"""
        alert_id = f"{rule.name}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        return Alert(
            id=alert_id,
            timestamp=timestamp,
            rule_name=rule.name,
            metric=rule.metric,
            current_value=current_value,
            threshold=rule.threshold,
            severity=rule.severity,
            message=f"{rule.name}: {rule.metric} = {current_value:.4f} (threshold: {rule.threshold})"
        )
    
    def _should_send_alert(self, alert: Alert) -> bool:
        """Determine if alert should be sent based on rate limits"""
        # Check hourly alert limit
        current_time = datetime.now()
        hour_ago = current_time - timedelta(hours=1)
        
        recent_alerts = [
            a for a in self.alert_history 
            if a.timestamp >= hour_ago and a.severity == alert.severity
        ]
        
        if len(recent_alerts) >= self.config['max_alerts_per_hour']:
            return False
        
        return True
    
    def _send_alert(self, alert: Alert) -> None:
        """Send alert to all configured channels"""
        self.active_alerts[alert.id] = alert
        self.alert_history.append(alert)
        
        self.logger.warning(f"ALERT: {alert.message}")
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")
    
    def add_alert_callback(self, callback: Callable[[Alert], None]) -> None:
        """Add alert callback function"""
        self.alert_callbacks.append(callback)
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolution_time = datetime.now()
            del self.active_alerts[alert_id]
            return True
        return False
    
    def _update_trend_analysis(self) -> None:
        """Update trend analysis for all metrics"""
        for metric in self.current_metrics.keys():
            try:
                trend = self.trend_analyzer.detect_trend(metric)
                
                # Store trend if significant
                if trend['confidence'] > 0.7:
                    self.logger.info(f"Trend detected in {metric}: {trend['trend']} (confidence: {trend['confidence']:.2f})")
                    
            except Exception as e:
                self.logger.error(f"Error in trend analysis for {metric}: {e}")
    
    def _analyze_performance_trends(self) -> None:
        """Analyze performance trends and patterns"""
        try:
            # Analyze win rate trend
            win_rate_trend = self.trend_analyzer.detect_trend('win_rate')
            if win_rate_trend['trend'] == 'downward' and win_rate_trend['confidence'] > 0.8:
                self._create_predictive_alert(
                    'win_rate', 
                    win_rate_trend['change_pct'], 
                    'Win rate declining - consider strategy review',
                    ['Review signal quality', 'Check market conditions', 'Adjust position sizing']
                )
            
            # Analyze drawdown trend
            drawdown_trend = self.trend_analyzer.detect_trend('max_drawdown')
            if drawdown_trend['trend'] == 'upward' and drawdown_trend['confidence'] > 0.8:
                self._create_predictive_alert(
                    'max_drawdown',
                    drawdown_trend['change_pct'],
                    'Drawdown increasing - risk management needed',
                    ['Reduce position sizes', 'Tighten stop losses', 'Review risk exposure']
                )
                
        except Exception as e:
            self.logger.error(f"Error in performance trend analysis: {e}")
    
    def _create_predictive_alert(self, metric: str, predicted_change: float, 
                                message: str, actions: List[str]) -> None:
        """Create predictive alert"""
        current_time = datetime.now()
        alert_id = f"PRED_{metric}_{current_time.strftime('%Y%m%d_%H%M%S')}"
        
        predicted_alert = PredictiveAlert(
            metric=metric,
            predicted_value=predicted_change,
            prediction_confidence=0.75,  # Would be calculated by ML model
            time_horizon_minutes=60,
            alert_probability=0.8,
            preventive_actions=actions
        )
        
        self.trend_predictions[alert_id] = predicted_alert
        
        self.logger.info(f"PREDICTIVE ALERT: {message}")
    
    def _detect_performance_anomalies(self) -> None:
        """Detect performance anomalies"""
        if not self.config['enable_anomaly_detection']:
            return
        
        key_metrics = ['win_rate', 'sharpe_ratio', 'max_drawdown', 'response_time']
        
        for metric in key_metrics:
            if metric in self.current_metrics:
                try:
                    anomalies = self.anomaly_detector.detect_anomalies(metric)
                    
                    for anomaly in anomalies:
                        if anomaly.confidence > 0.7:
                            self.logger.warning(
                                f"ANOMALY DETECTED: {anomaly.metric} = {anomaly.value:.4f} "
                                f"(expected: {anomaly.expected_range[0]:.4f} - {anomaly.expected_range[1]:.4f})"
                            )
                            
                            # Create anomaly alert
                            rule = AlertRule(
                                name=f"Anomaly: {anomaly.metric}",
                                metric=anomaly.metric,
                                condition="gt",
                                threshold=anomaly.expected_range[1],
                                severity=AlertSeverity.WARNING,
                                description=f"Anomaly detected: {anomaly.anomaly_type}"
                            )
                            
                            alert = self._create_alert(rule, anomaly.value, anomaly.timestamp)
                            if self._should_send_alert(alert):
                                self._send_alert(alert)
                                
                except Exception as e:
                    self.logger.error(f"Error detecting anomalies for {metric}: {e}")
    
    def _generate_performance_predictions(self) -> None:
        """Generate performance predictions using ML"""
        if not self.config['enable_performance_predictions']:
            return
        
        try:
            # Simple prediction using trend analysis
            for metric, data_points in self.learning_data.items():
                if len(data_points) >= 10:  # Minimum data points
                    # Calculate trend and predict next value
                    recent_values = [val for _, val in data_points[-20:]]  # Last 20 points
                    
                    if len(recent_values) >= 10:
                        # Linear trend prediction
                        x = list(range(len(recent_values)))
                        y = recent_values
                        
                        if len(x) > 1:
                            # Simple linear regression
                            n = len(x)
                            sum_x = sum(x)
                            sum_y = sum(y)
                            sum_xy = sum(xi * yi for xi, yi in zip(x, y))
                            sum_x2 = sum(xi * xi for xi in x)
                            
                            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                            intercept = (sum_y - slope * sum_x) / n
                            
                            # Predict next value
                            next_x = len(recent_values)
                            predicted_value = slope * next_x + intercept
                            
                            # Store prediction
                            self.logger.info(f"PREDICTION: {metric} predicted to be {predicted_value:.4f}")
                            
        except Exception as e:
            self.logger.error(f"Error generating predictions: {e}")
    
    def _update_dashboards(self) -> None:
        """Update dashboard data"""
        # This would integrate with dashboard system
        # For now, just log the update
        self.logger.debug("Dashboard data updated")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            'monitoring_mode': self.monitoring_mode.value,
            'active_alerts': len(self.active_alerts),
            'alert_history_count': len(self.alert_history),
            'last_update': max(self.last_update.values()) if self.last_update else None,
            'current_metrics': self.current_metrics,
            'system_health': self.system_health_metrics,
            'predictive_alerts': len(self.trend_predictions)
        }
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get all real-time metrics"""
        return {
            'timestamp': datetime.now().isoformat(),
            'performance_metrics': self.current_metrics,
            'trend_analysis': {
                metric: self.trend_analyzer.detect_trend(metric) 
                for metric in self.current_metrics.keys()
            },
            'active_alerts': [asdict(alert) for alert in self.active_alerts.values()],
            'system_health': self.system_health_metrics
        }
    
    def export_monitoring_data(self, format_type: str = 'json') -> str:
        """Export monitoring data"""
        try:
            data = {
                'export_timestamp': datetime.now().isoformat(),
                'monitoring_status': self.get_monitoring_status(),
                'current_metrics': self.current_metrics,
                'alert_history': [asdict(alert) for alert in self.alert_history],
                'baseline_metrics': self.baseline_metrics,
                'trends': {
                    metric: self.trend_analyzer.detect_trend(metric) 
                    for metric in self.current_metrics.keys()
                }
            }
            
            if format_type.lower() == 'json':
                return json.dumps(data, indent=2, default=str)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
        except Exception as e:
            self.logger.error(f"Error exporting monitoring data: {e}")
            return ""


# Demo function
def demo_real_time_monitor():
    """Demonstrate real-time monitor capabilities"""
    print("=== Real-time Monitor Demo ===\n")
    
    from performance_tracker import demo_performance_tracker
    
    # Initialize performance tracker
    performance_tracker = demo_performance_tracker()
    
    # Initialize monitor
    monitor = RealTimeMonitor(performance_tracker)
    
    # Add custom alert callback
    def custom_alert_handler(alert: Alert):
        print(f"CUSTOM ALERT: {alert.message} (Severity: {alert.severity.value})")
    
    monitor.add_alert_callback(custom_alert_handler)
    
    # Start monitoring
    print("Starting monitoring system...")
    monitor.start_monitoring()
    
    # Simulate some trading activity
    import random
    from performance_tracker import TradeData
    from datetime import timedelta
    
    print("Simulating trading activity...")
    for i in range(50):
        trade = TradeData(
            timestamp=datetime.now() - timedelta(minutes=i*5),
            instrument=random.choice(['EURUSD', 'GBPUSD', 'USDJPY']),
            signal_type=random.choice(['BUY', 'SELL']),
            entry_price=random.uniform(1.0, 2.0),
            exit_price=random.uniform(1.0, 2.0),
            quantity=random.uniform(0.1, 1.0),
            profit_loss=random.uniform(-20, 40),
            success=random.choice([True, False]),
            duration=random.uniform(1, 30),
            strategy=random.choice(['momentum', 'mean_reversion']),
            risk_score=random.uniform(0.1, 0.8),
            confidence=random.uniform(0.5, 0.95)
        )
        performance_tracker.add_trade(trade)
        time.sleep(0.1)  # Small delay
    
    # Wait for monitoring to process
    time.sleep(2)
    
    # Get monitoring status
    status = monitor.get_monitoring_status()
    print(f"\nMonitoring Status:")
    print(f"Mode: {status['monitoring_mode']}")
    print(f"Active Alerts: {status['active_alerts']}")
    print(f"Current Metrics: {len(status['current_metrics'])} tracked")
    
    # Get real-time metrics
    real_time = monitor.get_real_time_metrics()
    print(f"\nReal-time Metrics:")
    for metric, value in real_time['performance_metrics'].items():
        print(f"  {metric}: {value:.4f}")
    
    # Show trends
    print(f"\nTrend Analysis:")
    for metric, trend in real_time['trend_analysis'].items():
        print(f"  {metric}: {trend['trend']} (confidence: {trend['confidence']:.2f})")
    
    # Stop monitoring
    monitor.stop_monitoring()
    print("\n=== Real-time Monitor Demo Complete ===")
    
    return monitor


if __name__ == "__main__":
    demo_real_time_monitor()