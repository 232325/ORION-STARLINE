"""
Performance Monitoring Module
Ishlab chiqishni kuzatish va monitoring moduli
"""
import sqlite3
import json
import time
import asyncio
import psutil
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import pandas as pd
from dataclasses import asdict
import os

from ..utils.data_models import SystemMetrics, AuditLogEntry
from ..config.config import config

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """
    Performance Monitoring and Analytics
    Tizim ishlashni kuzatish
    """
    
    def __init__(self, system_config):
        self.config = system_config
        self.db_path = config.db_path
        self.running = False
        self.monitoring_thread = None
        self.metrics_history = []
        
        # Real-time metrics
        self.current_metrics = SystemMetrics()
        self.system_health = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'disk_usage': 0.0,
            'network_latency': 0.0,
            'quantum_backend_health': 0.0
        }
        
        # Performance thresholds
        self.thresholds = {
            'max_cpu_usage': 80.0,
            'max_memory_usage': 85.0,
            'max_latency': 1000.0,  # 1 second
            'min_success_rate': 95.0,
            'max_error_rate': 5.0
        }
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Monitoring intervals
        self.monitoring_interval = 1.0  # 1 second
        self.metrics_retention_days = 30
        self.alert_cooldown = 300  # 5 minutes
        
        # Alerts
        self.last_alerts = {}
        self.active_alerts = []
        
        logger.info("Performance Monitor initialized")
    
    def start(self) -> bool:
        """Start monitoring service"""
        try:
            self.running = True
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            # Initialize database
            self._initialize_database()
            
            logger.info("Performance monitoring started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start performance monitoring: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop monitoring service"""
        try:
            self.running = False
            
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            
            # Save final metrics
            self._save_final_metrics()
            
            logger.info("Performance monitoring stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop performance monitoring: {e}")
            return False
    
    def update_metrics(self, metrics: SystemMetrics):
        """Update system metrics"""
        with self._lock:
            self.current_metrics = metrics
            self._check_performance_thresholds()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health"""
        try:
            # Get system resource usage
            self.system_health['cpu_usage'] = psutil.cpu_percent(interval=1)
            self.system_health['memory_usage'] = psutil.virtual_memory().percent
            self.system_health['disk_usage'] = psutil.disk_usage('/').percent
            
            # Network latency (simplified)
            self.system_health['network_latency'] = self._measure_network_latency()
            
            # Quantum backend health
            self.system_health['quantum_backend_health'] = self._check_quantum_backend_health()
            
            # Overall health score
            health_score = self._calculate_health_score()
            
            return {
                'health_score': health_score,
                'system_resources': self.system_health,
                'alerts': self.active_alerts,
                'status': self._get_health_status(health_score)
            }
            
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {'health_score': 0.0, 'status': 'ERROR', 'error': str(e)}
    
    def get_performance_analytics(self, time_range: str = '1h') -> Dict[str, Any]:
        """Get performance analytics"""
        try:
            # Parse time range
            end_time = datetime.now(timezone.utc)
            if time_range == '1h':
                start_time = end_time - timedelta(hours=1)
            elif time_range == '24h':
                start_time = end_time - timedelta(days=1)
            elif time_range == '7d':
                start_time = end_time - timedelta(days=7)
            elif time_range == '30d':
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(hours=1)
            
            # Get historical data
            historical_metrics = self._get_historical_metrics(start_time, end_time)
            
            # Calculate analytics
            analytics = self._calculate_performance_analytics(historical_metrics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get performance analytics: {e}")
            return {}
    
    def generate_report(self, report_type: str = 'daily') -> Dict[str, Any]:
        """Generate performance report"""
        try:
            if report_type == 'daily':
                return self._generate_daily_report()
            elif report_type == 'weekly':
                return self._generate_weekly_report()
            elif report_type == 'monthly':
                return self._generate_monthly_report()
            elif report_type == 'trading_session':
                return self._generate_trading_session_report()
            else:
                return self._generate_daily_report()
                
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return {'error': str(e)}
    
    def save_audit_log(self, audit_entry: Dict[str, Any]):
        """Save audit log entry"""
        try:
            self._save_audit_to_database(audit_entry)
        except Exception as e:
            logger.error(f"Failed to save audit log: {e}")
    
    def test_database_connection(self) -> bool:
        """Test database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitoring status"""
        return {
            'running': self.running,
            'monitoring_interval': self.monitoring_interval,
            'metrics_history_size': len(self.metrics_history),
            'database_path': self.db_path,
            'thresholds': self.thresholds,
            'active_alerts_count': len(self.active_alerts),
            'last_update': datetime.now(timezone.utc).isoformat()
        }
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Performance monitoring loop started")
        
        while self.running:
            try:
                start_time = time.time()
                
                # Update system health
                health_data = self.get_system_health()
                
                # Update metrics with health data
                self.current_metrics.system_utilization = health_data['health_score']
                
                # Save metrics to database
                self._save_metrics_to_database()
                
                # Clean old data
                self._cleanup_old_data()
                
                # Calculate monitoring time
                elapsed = time.time() - start_time
                sleep_time = max(0, self.monitoring_interval - elapsed)
                
                time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(self.monitoring_interval)
        
        logger.info("Performance monitoring loop stopped")
    
    def _initialize_database(self):
        """Initialize monitoring database"""
        try:
            # Create database directory if it doesn't exist
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    uptime REAL,
                    total_opportunities INTEGER,
                    executed_trades INTEGER,
                    total_profit REAL,
                    total_loss REAL,
                    avg_latency REAL,
                    error_rate REAL,
                    cpu_usage REAL,
                    memory_usage REAL,
                    quantum_fidelity REAL
                )
            ''')
            
            # Create audit log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    user_id TEXT,
                    session_id TEXT,
                    ip_address TEXT,
                    risk_level TEXT
                )
            ''')
            
            # Create alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_timestamp TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Monitoring database initialized")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    def _save_metrics_to_database(self):
        """Save current metrics to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_metrics (
                    timestamp, uptime, total_opportunities, executed_trades,
                    total_profit, total_loss, avg_latency, error_rate,
                    cpu_usage, memory_usage, quantum_fidelity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(timezone.utc).isoformat(),
                self.current_metrics.uptime,
                self.current_metrics.total_opportunities,
                self.current_metrics.executed_trades,
                self.current_metrics.total_profit,
                self.current_metrics.total_loss,
                self.current_metrics.total_latency / max(self.current_metrics.executed_trades, 1),
                self.current_metrics.error_rate,
                self.system_health['cpu_usage'],
                self.system_health['memory_usage'],
                self.current_metrics.quantum_fidelity
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save metrics to database: {e}")
    
    def _save_audit_to_database(self, audit_entry: Dict[str, Any]):
        """Save audit entry to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO audit_log (
                    timestamp, event_type, event_data, user_id,
                    session_id, ip_address, risk_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now(timezone.utc).isoformat(),
                audit_entry.get('event_type', ''),
                json.dumps(audit_entry.get('event_data', {})),
                audit_entry.get('user_id'),
                audit_entry.get('session_id'),
                audit_entry.get('ip_address'),
                audit_entry.get('risk_level', 'LOW')
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save audit log: {e}")
    
    def _check_performance_thresholds(self):
        """Check performance thresholds and generate alerts"""
        try:
            # Check CPU usage
            if self.system_health['cpu_usage'] > self.thresholds['max_cpu_usage']:
                self._create_alert('HIGH_CPU_USAGE', 'WARNING', f"CPU usage: {self.system_health['cpu_usage']:.1f}%")
            
            # Check memory usage
            if self.system_health['memory_usage'] > self.thresholds['max_memory_usage']:
                self._create_alert('HIGH_MEMORY_USAGE', 'WARNING', f"Memory usage: {self.system_health['memory_usage']:.1f}%")
            
            # Check success rate
            if self.current_metrics.executed_trades > 0:
                success_rate = (self.current_metrics.successful_trades / self.current_metrics.executed_trades) * 100
                if success_rate < self.thresholds['min_success_rate']:
                    self._create_alert('LOW_SUCCESS_RATE', 'CRITICAL', f"Success rate: {success_rate:.1f}%")
            
            # Check error rate
            if self.current_metrics.error_rate > self.thresholds['max_error_rate']:
                self._create_alert('HIGH_ERROR_RATE', 'CRITICAL', f"Error rate: {self.current_metrics.error_rate:.1f}%")
            
        except Exception as e:
            logger.error(f"Threshold check failed: {e}")
    
    def _create_alert(self, alert_type: str, severity: str, message: str):
        """Create alert"""
        try:
            current_time = time.time()
            alert_key = f"{alert_type}_{severity}"
            
            # Check cooldown
            if alert_key in self.last_alerts:
                if current_time - self.last_alerts[alert_key] < self.alert_cooldown:
                    return  # Still in cooldown
            
            # Create alert
            alert = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'alert_type': alert_type,
                'severity': severity,
                'message': message,
                'resolved': False
            }
            
            self.active_alerts.append(alert)
            self.last_alerts[alert_key] = current_time
            
            # Save to database
            self._save_alert_to_database(alert)
            
            logger.warning(f"Alert created: {alert_type} - {message}")
            
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
    
    def _save_alert_to_database(self, alert: Dict[str, Any]):
        """Save alert to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts (timestamp, alert_type, severity, message, resolved)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                alert['timestamp'],
                alert['alert_type'],
                alert['severity'],
                alert['message'],
                alert['resolved']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save alert: {e}")
    
    def _measure_network_latency(self) -> float:
        """Measure network latency (simplified)"""
        try:
            # Simple latency measurement
            start_time = time.time()
            # In real implementation, would ping a server
            time.sleep(0.001)  # Simulated latency
            return (time.time() - start_time) * 1000  # Convert to milliseconds
        except Exception:
            return 0.0
    
    def _check_quantum_backend_health(self) -> float:
        """Check quantum backend health"""
        try:
            # Simplified quantum backend health check
            # In real implementation, would check actual quantum backend status
            health = 0.95  # 95% health by default
            
            # Reduce health based on error rate
            if hasattr(self.current_metrics, 'error_rate'):
                health -= self.current_metrics.error_rate / 100
            
            return max(0.0, min(1.0, health))
        except Exception:
            return 0.5
    
    def _calculate_health_score(self) -> float:
        """Calculate overall system health score"""
        try:
            # Weight different health factors
            weights = {
                'cpu_usage': 0.2,
                'memory_usage': 0.2,
                'network_latency': 0.1,
                'quantum_backend_health': 0.3,
                'success_rate': 0.2
            }
            
            # Normalize metrics to 0-1 scale
            cpu_score = 1.0 - (self.system_health['cpu_usage'] / 100)
            memory_score = 1.0 - (self.system_health['memory_usage'] / 100)
            latency_score = max(0.0, 1.0 - (self.system_health['network_latency'] / 1000))  # 1s max
            quantum_score = self.system_health['quantum_backend_health']
            
            # Success rate
            success_rate = 0.0
            if self.current_metrics.executed_trades > 0:
                success_rate = self.current_metrics.successful_trades / self.current_metrics.executed_trades
            
            success_score = success_rate
            
            # Calculate weighted score
            health_score = (
                cpu_score * weights['cpu_usage'] +
                memory_score * weights['memory_usage'] +
                latency_score * weights['network_latency'] +
                quantum_score * weights['quantum_backend_health'] +
                success_score * weights['success_rate']
            )
            
            return max(0.0, min(1.0, health_score))
            
        except Exception as e:
            logger.error(f"Health score calculation failed: {e}")
            return 0.0
    
    def _get_health_status(self, health_score: float) -> str:
        """Get health status string"""
        if health_score >= 0.8:
            return "HEALTHY"
        elif health_score >= 0.6:
            return "WARNING"
        elif health_score >= 0.4:
            return "CRITICAL"
        else:
            return "EMERGENCY"
    
    def _get_historical_metrics(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get historical metrics from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, uptime, total_opportunities, executed_trades,
                       total_profit, total_loss, avg_latency, error_rate
                FROM system_metrics
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp
            ''', (start_time.isoformat(), end_time.isoformat()))
            
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Failed to get historical metrics: {e}")
            return []
    
    def _calculate_performance_analytics(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate performance analytics"""
        try:
            if not historical_data:
                return {}
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(historical_data)
            
            analytics = {
                'summary': {
                    'data_points': len(df),
                    'time_range': {
                        'start': df['timestamp'].min(),
                        'end': df['timestamp'].max()
                    },
                    'total_opportunities': df['total_opportunities'].sum(),
                    'total_executed_trades': df['executed_trades'].sum(),
                    'total_profit': df['total_profit'].sum(),
                    'total_loss': df['total_loss'].sum()
                },
                'performance_trends': {},
                'resource_utilization': {},
                'reliability_metrics': {}
            }
            
            # Performance trends
            if len(df) > 1:
                analytics['performance_trends'] = {
                    'opportunities_trend': self._calculate_trend(df['total_opportunities']),
                    'profit_trend': self._calculate_trend(df['total_profit']),
                    'execution_trend': self._calculate_trend(df['executed_trades']),
                    'latency_trend': self._calculate_trend(df['avg_latency'])
                }
            
            # Resource utilization
            if 'cpu_usage' in df.columns:
                analytics['resource_utilization'] = {
                    'avg_cpu_usage': df['cpu_usage'].mean(),
                    'max_cpu_usage': df['cpu_usage'].max(),
                    'avg_memory_usage': df['memory_usage'].mean(),
                    'max_memory_usage': df['memory_usage'].max(),
                    'avg_latency': df['avg_latency'].mean()
                }
            
            # Reliability metrics
            analytics['reliability_metrics'] = {
                'success_rate': (df['executed_trades'].sum() / max(df['total_opportunities'].sum(), 1)) * 100,
                'error_rate': df['error_rate'].mean(),
                'uptime_percentage': 100.0,  # Would calculate based on actual uptime data
                'system_availability': 100.0  # Would calculate based on downtime
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Performance analytics calculation failed: {e}")
            return {}
    
    def _calculate_trend(self, series: pd.Series) -> str:
        """Calculate trend direction"""
        if len(series) < 2:
            return "INSUFFICIENT_DATA"
        
        # Calculate linear trend
        x = np.arange(len(series))
        slope = np.polyfit(x, series.values, 1)[0]
        
        if abs(slope) < 0.01:
            return "STABLE"
        elif slope > 0:
            return "INCREASING"
        else:
            return "DECREASING"
    
    def _generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily performance report"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=1)
        
        historical_data = self._get_historical_metrics(start_time, end_time)
        analytics = self._calculate_performance_analytics(historical_data)
        
        # Add daily specific metrics
        analytics['report_type'] = 'daily'
        analytics['report_period'] = {
            'start': start_time.isoformat(),
            'end': end_time.isoformat()
        }
        
        # System health summary
        analytics['system_health'] = self.get_system_health()
        
        # Top alerts
        analytics['active_alerts'] = self.active_alerts[-10:]  # Last 10 alerts
        
        return analytics
    
    def _generate_weekly_report(self) -> Dict[str, Any]:
        """Generate weekly performance report"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(weeks=1)
        
        historical_data = self._get_historical_metrics(start_time, end_time)
        analytics = self._calculate_performance_analytics(historical_data)
        
        analytics['report_type'] = 'weekly'
        analytics['report_period'] = {
            'start': start_time.isoformat(),
            'end': end_time.isoformat()
        }
        
        return analytics
    
    def _generate_monthly_report(self) -> Dict[str, Any]:
        """Generate monthly performance report"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=30)
        
        historical_data = self._get_historical_metrics(start_time, end_time)
        analytics = self._calculate_performance_analytics(historical_data)
        
        analytics['report_type'] = 'monthly'
        analytics['report_period'] = {
            'start': start_time.isoformat(),
            'end': end_time.isoformat()
        }
        
        return analytics
    
    def _generate_trading_session_report(self) -> Dict[str, Any]:
        """Generate trading session report"""
        # Get current session data (simplified)
        current_time = datetime.now(timezone.utc)
        session_start = current_time.replace(hour=8, minute=0, second=0, microsecond=0)  # Start of trading day
        
        historical_data = self._get_historical_metrics(session_start, current_time)
        analytics = self._calculate_performance_analytics(historical_data)
        
        analytics['report_type'] = 'trading_session'
        analytics['report_period'] = {
            'start': session_start.isoformat(),
            'end': current_time.isoformat(),
            'session_name': self._get_current_session_name()
        }
        
        return analytics
    
    def _get_current_session_name(self) -> str:
        """Get current market session name"""
        current_hour = datetime.now(timezone.utc).hour
        
        if 21 <= current_hour or current_hour < 6:
            return "Sydney"
        elif 0 <= current_hour < 9:
            return "Tokyo"
        elif 8 <= current_hour < 17:
            return "London"
        elif 13 <= current_hour < 22:
            return "New_York"
        else:
            return "Weekend"
    
    def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=self.metrics_retention_days)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete old metrics
            cursor.execute('''
                DELETE FROM system_metrics
                WHERE timestamp < ?
            ''', (cutoff_time.isoformat(),))
            
            # Delete old audit logs (keep longer for compliance)
            audit_cutoff = datetime.now(timezone.utc) - timedelta(days=90)
            cursor.execute('''
                DELETE FROM audit_log
                WHERE timestamp < ?
            ''', (audit_cutoff.isoformat(),))
            
            # Delete old alerts
            cursor.execute('''
                DELETE FROM alerts
                WHERE timestamp < ? AND resolved = TRUE
            ''', (cutoff_time.isoformat(),))
            
            deleted_rows = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted_rows > 0:
                logger.info(f"Cleaned up {deleted_rows} old records")
                
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")
    
    def _save_final_metrics(self):
        """Save final metrics before shutdown"""
        try:
            self._save_metrics_to_database()
            
            # Create final report
            final_report = self.generate_report('daily')
            
            # Save to file
            report_file = f"final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(final_report, f, indent=2, default=str)
            
            logger.info(f"Final report saved to {report_file}")
            
        except Exception as e:
            logger.error(f"Failed to save final metrics: {e}")


class AlertManager:
    """Alert management system"""
    
    def __init__(self):
        self.alert_rules = {}
        self.notification_channels = []
    
    def add_alert_rule(self, rule_name: str, conditions: Dict[str, Any], actions: List[str]):
        """Add alert rule"""
        self.alert_rules[rule_name] = {
            'conditions': conditions,
            'actions': actions
        }
    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for alert conditions"""
        alerts = []
        
        for rule_name, rule in self.alert_rules.items():
            if self._check_rule_conditions(rule['conditions'], metrics):
                alert = {
                    'rule_name': rule_name,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'metrics': metrics,
                    'actions': rule['actions']
                }
                alerts.append(alert)
        
        return alerts
    
    def _check_rule_conditions(self, conditions: Dict[str, Any], metrics: Dict[str, Any]) -> bool:
        """Check if rule conditions are met"""
        for metric, threshold in conditions.items():
            if metric in metrics:
                value = metrics[metric]
                if isinstance(threshold, dict):
                    operator = threshold.get('operator', '>')
                    limit = threshold.get('value', 0)
                    
                    if operator == '>' and value <= limit:
                        return False
                    elif operator == '<' and value >= limit:
                        return False
                else:
                    if metric not in metrics or metrics[metric] > threshold:
                        return False
        
        return True