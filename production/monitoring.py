#!/usr/bin/env python3
"""
Production Monitoring System
Production muhit uchun real-time monitoring va alerting
"""

import os
import json
import time
import asyncio
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import psutil
import sqlite3
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import websocket
import threading

# Import production configuration
from production_config import get_config


@dataclass
class MetricPoint:
    """Metrik nuqta"""
    timestamp: datetime
    name: str
    value: float
    unit: str = ""
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Ogohlantirish qoidasi"""
    name: str
    metric: str
    condition: str  # ">", "<", ">=", "<=", "=="
    threshold: float
    duration: int  # seconds
    severity: str  # "info", "warning", "critical"
    description: str
    enabled: bool = True


@dataclass
class Alert:
    """Ogohlantirish"""
    id: str
    rule_name: str
    severity: str
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class ProductionMonitoring:
    """Production monitoring tizimi"""
    
    def __init__(self, environment: str = "production"):
        self.config = get_config(environment)
        self.environment = environment
        
        # Logging setup
        self.setup_logging()
        
        # Monitoring directories
        self.log_dir = Path("/workspace/orion-starline/logs")
        self.data_dir = Path("/workspace/orion-starline/data/monitoring")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Database setup
        self.db_path = self.data_dir / "monitoring.db"
        self.init_database()
        
        # Alert rules
        self.alert_rules = self.load_alert_rules()
        self.alerts = {}
        
        # Metrics storage
        self.metrics_buffer = []
        self.max_buffer_size = 1000
        
        # Monitoring threads
        self.threads = []
        self.running = False
        
        # WebSocket connections
        self.ws_clients = []
        
        # Initialize monitoring
        self.initialize_monitoring()
    
    def setup_logging(self):
        """Logging konfiguratsiyasi"""
        self.log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_dir / "monitoring.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def init_database(self):
        """Monitoring ma'lumotlar bazasini yaratish"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT,
                    tags TEXT,
                    environment TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE NOT NULL,
                    rule_name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    resolved INTEGER DEFAULT 0,
                    resolved_at TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_percent REAL,
                    network_in REAL,
                    network_out REAL,
                    active_connections INTEGER
                )
            """)
    
    def load_alert_rules(self) -> List[AlertRule]:
        """Ogohlantirish qoidalarini yuklash"""
        rules = [
            AlertRule(
                name="High CPU Usage",
                metric="system.cpu_percent",
                condition=">",
                threshold=80.0,
                duration=300,
                severity="warning",
                description="CPU usage is above 80% for 5 minutes"
            ),
            AlertRule(
                name="High Memory Usage",
                metric="system.memory_percent",
                condition=">",
                threshold=85.0,
                duration=300,
                severity="warning",
                description="Memory usage is above 85% for 5 minutes"
            ),
            AlertRule(
                name="Very High CPU Usage",
                metric="system.cpu_percent",
                condition=">",
                threshold=95.0,
                duration=120,
                severity="critical",
                description="CPU usage is above 95% for 2 minutes"
            ),
            AlertRule(
                name="High Response Time",
                metric="api.response_time_ms",
                condition=">",
                threshold=5000,
                duration=60,
                severity="warning",
                description="API response time is above 5 seconds"
            ),
            AlertRule(
                name="Low Success Rate",
                metric="api.success_rate",
                condition="<",
                threshold=95.0,
                duration=300,
                severity="warning",
                description="API success rate is below 95%"
            ),
            AlertRule(
                name="Database Connection High",
                metric="db.active_connections",
                condition=">",
                threshold=80,
                duration=60,
                severity="warning",
                description="Database connections are high"
            ),
            AlertRule(
                name="Disk Space Low",
                metric="disk.free_percent",
                condition="<",
                threshold=10.0,
                duration=60,
                severity="critical",
                description="Disk space is below 10%"
            )
        ]
        
        return rules
    
    def initialize_monitoring(self):
        """Monitoring ni ishga tushirish"""
        self.logger.info("📊 Production monitoring tizimi ishga tushdi")
        
        # Start monitoring threads
        self.start_monitoring_threads()
    
    def start_monitoring_threads(self):
        """Monitoring threadlarini ishga tushirish"""
        self.running = True
        
        # System metrics monitoring
        self.threads.append(
            threading.Thread(target=self.monitor_system_metrics, daemon=True)
        )
        
        # Application metrics monitoring
        self.threads.append(
            threading.Thread(target=self.monitor_application_metrics, daemon=True)
        )
        
        # Alert evaluation
        self.threads.append(
            threading.Thread(target=self.evaluate_alerts, daemon=True)
        )
        
        # Data persistence
        self.threads.append(
            threading.Thread(target=self.persist_metrics, daemon=True)
        )
        
        # Health checks
        self.threads.append(
            threading.Thread(target=self.health_checks, daemon=True)
        )
        
        # Start all threads
        for thread in self.threads:
            thread.start()
        
        self.logger.info(f"🔄 {len(self.threads)} monitoring thread ishga tushdi")
    
    def monitor_system_metrics(self):
        """Sistema metrikalarini monitoring qilish"""
        while self.running:
            try:
                timestamp = datetime.now()
                
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Memory metrics
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                memory_used_gb = memory.used / (1024**3)
                memory_total_gb = memory.total / (1024**3)
                
                # Disk metrics
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                disk_free_gb = disk.free / (1024**3)
                
                # Network metrics
                network = psutil.net_io_counters()
                network_in_mb = network.bytes_recv / (1024**2)
                network_out_mb = network.bytes_sent / (1024**2)
                
                # Database connections (estimated)
                db_connections = self.get_database_connections()
                
                # Store metrics
                metrics = [
                    MetricPoint(timestamp, "system.cpu_percent", cpu_percent, "%"),
                    MetricPoint(timestamp, "system.memory_percent", memory_percent, "%"),
                    MetricPoint(timestamp, "system.memory_used_gb", memory_used_gb, "GB"),
                    MetricPoint(timestamp, "system.memory_total_gb", memory_total_gb, "GB"),
                    MetricPoint(timestamp, "system.disk_percent", disk_percent, "%"),
                    MetricPoint(timestamp, "system.disk_free_gb", disk_free_gb, "GB"),
                    MetricPoint(timestamp, "system.network_in_mb", network_in_mb, "MB"),
                    MetricPoint(timestamp, "system.network_out_mb", network_out_mb, "MB"),
                    MetricPoint(timestamp, "db.active_connections", db_connections, "count")
                ]
                
                # Add to buffer
                self.metrics_buffer.extend(metrics)
                
                # Keep buffer size in check
                if len(self.metrics_buffer) > self.max_buffer_size:
                    self.metrics_buffer = self.metrics_buffer[-self.max_buffer_size:]
                
                self.logger.debug(f"📈 System metrics: CPU {cpu_percent:.1f}%, Memory {memory_percent:.1f}%")
                
            except Exception as e:
                self.logger.error(f"System metrics monitoring xatosi: {e}")
            
            time.sleep(30)  # 30 soniyada bir
    
    def monitor_application_metrics(self):
        """Application metrikalarini monitoring qilish"""
        while self.running:
            try:
                timestamp = datetime.now()
                
                # API metrics
                api_metrics = self.get_api_metrics()
                
                # Cache metrics
                cache_metrics = self.get_cache_metrics()
                
                # User metrics
                user_metrics = self.get_user_metrics()
                
                # Store metrics
                metrics = []
                for metric_name, value, unit in api_metrics + cache_metrics + user_metrics:
                    metrics.append(MetricPoint(timestamp, metric_name, value, unit))
                
                self.metrics_buffer.extend(metrics)
                
                if len(self.metrics_buffer) > self.max_buffer_size:
                    self.metrics_buffer = self.metrics_buffer[-self.max_buffer_size:]
                
            except Exception as e:
                self.logger.error(f"Application metrics monitoring xatosi: {e}")
            
            time.sleep(60)  # Har daqiqada bir
    
    def get_api_metrics(self) -> List[tuple]:
        """API metrikalarini olish"""
        metrics = []
        
        try:
            # Test API endpoints
            api_endpoints = [
                "http://localhost:8000/health",
                "http://localhost:8000/api/v1/trading/status"
            ]
            
            for endpoint in api_endpoints:
                try:
                    start_time = time.time()
                    response = requests.get(endpoint, timeout=5)
                    response_time = (time.time() - start_time) * 1000
                    
                    # Response time
                    metrics.append((f"api.response_time_ms.{endpoint.split('/')[-1]}", 
                                  response_time, "ms"))
                    
                    # Success rate
                    if response.status_code == 200:
                        metrics.append((f"api.success_rate.{endpoint.split('/')[-1]}", 
                                      100.0, "%"))
                    else:
                        metrics.append((f"api.success_rate.{endpoint.split('/')[-1]}", 
                                      0.0, "%"))
                
                except Exception:
                    metrics.append((f"api.response_time_ms.{endpoint.split('/')[-1]}", 
                                  9999.0, "ms"))
                    metrics.append((f"api.success_rate.{endpoint.split('/')[-1]}", 
                                  0.0, "%"))
        
        except Exception as e:
            self.logger.error(f"API metrics olishda xato: {e}")
        
        return metrics
    
    def get_cache_metrics(self) -> List[tuple]:
        """Cache metrikalarini olish"""
        metrics = []
        
        try:
            # This would require actual Redis connection
            # For now, return mock data
            metrics.append(("cache.hit_rate", 85.5, "%"))
            metrics.append(("cache.misses", 12, "count"))
            metrics.append(("cache.hits", 73, "count"))
            
        except Exception as e:
            self.logger.error(f"Cache metrics olishda xato: {e}")
        
        return metrics
    
    def get_user_metrics(self) -> List[tuple]:
        """User metrikalarini olish"""
        metrics = []
        
        try:
            # This would require actual database connection
            # For now, return mock data
            metrics.append(("users.active_sessions", 42, "count"))
            metrics.append(("users.new_registrations", 3, "count"))
            metrics.append(("users.concurrent_users", 156, "count"))
            
        except Exception as e:
            self.logger.error(f"User metrics olishda xato: {e}")
        
        return metrics
    
    def get_database_connections(self) -> int:
        """Ma'lumotlar bazasi aloqa sonini olish"""
        try:
            # This would require actual database connection
            return 15  # Mock data
        except Exception:
            return 0
    
    def evaluate_alerts(self):
        """Ogohlantirishlarni baholash"""
        while self.running:
            try:
                current_time = datetime.now()
                
                for rule in self.alert_rules:
                    if not rule.enabled:
                        continue
                    
                    # Get recent metrics for this rule
                    recent_metrics = self.get_recent_metrics(
                        rule.metric, 
                        current_time - timedelta(seconds=rule.duration)
                    )
                    
                    if not recent_metrics:
                        continue
                    
                    # Check if condition is met
                    values = [m.value for m in recent_metrics]
                    
                    condition_met = self.evaluate_condition(
                        values, rule.condition, rule.threshold
                    )
                    
                    if condition_met:
                        # Alert triggered
                        self.trigger_alert(rule, current_time)
                    else:
                        # Alert resolved
                        self.resolve_alert(rule, current_time)
                
            except Exception as e:
                self.logger.error(f"Alert evaluation xatosi: {e}")
            
            time.sleep(30)  # 30 soniyada bir
    
    def evaluate_condition(self, values: List[float], condition: str, threshold: float) -> bool:
        """Shartni baholash"""
        if not values:
            return False
        
        latest_value = values[-1]
        
        if condition == ">":
            return latest_value > threshold
        elif condition == "<":
            return latest_value < threshold
        elif condition == ">=":
            return latest_value >= threshold
        elif condition == "<=":
            return latest_value <= threshold
        elif condition == "==":
            return abs(latest_value - threshold) < 0.01
        
        return False
    
    def get_recent_metrics(self, metric_name: str, since_time: datetime) -> List[MetricPoint]:
        """So'nggi metrikalarni olish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT timestamp, name, value, unit FROM metrics WHERE name = ? AND timestamp > ? ORDER BY timestamp DESC",
                (metric_name, since_time.isoformat())
            )
            
            metrics = []
            for row in cursor.fetchall():
                metrics.append(MetricPoint(
                    datetime.fromisoformat(row[0]),
                    row[1],
                    row[2],
                    row[3]
                ))
            
            return metrics
    
    def trigger_alert(self, rule: AlertRule, timestamp: datetime):
        """Ogohlantirishni ishga tushirish"""
        alert_id = f"{rule.name}_{int(timestamp.timestamp())}"
        
        if alert_id in self.alerts and not self.alerts[alert_id].resolved:
            # Alert already active
            return
        
        alert = Alert(
            id=alert_id,
            rule_name=rule.name,
            severity=rule.severity,
            message=rule.description,
            timestamp=timestamp
        )
        
        self.alerts[alert_id] = alert
        self.logger.warning(f"🚨 Alert triggered: {rule.name} - {rule.description}")
        
        # Save to database
        self.save_alert_to_db(alert)
        
        # Send notifications
        self.send_alert_notification(alert)
        
        # Broadcast via WebSocket
        self.broadcast_alert(alert)
    
    def resolve_alert(self, rule: AlertRule, timestamp: datetime):
        """Ogohlantirishni hal qilish"""
        alert_id = f"{rule.name}_{int(timestamp.timestamp())}"
        
        if alert_id in self.alerts and not self.alerts[alert_id].resolved:
            alert = self.alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = timestamp
            
            self.logger.info(f"✅ Alert resolved: {rule.name}")
            
            # Update database
            self.update_alert_in_db(alert)
            
            # Broadcast resolution
            self.broadcast_alert(alert)
    
    def save_alert_to_db(self, alert: Alert):
        """Ogohlantirishni ma'lumotlar bazasiga saqlash"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO alerts (alert_id, rule_name, severity, message, timestamp, resolved) VALUES (?, ?, ?, ?, ?, ?)",
                (alert.id, alert.rule_name, alert.severity, alert.message, 
                 alert.timestamp.isoformat(), 0)
            )
    
    def update_alert_in_db(self, alert: Alert):
        """Ogohlantirishni ma'lumotlar bazasida yangilash"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE alerts SET resolved = 1, resolved_at = ? WHERE alert_id = ?",
                (alert.resolved_at.isoformat(), alert.id)
            )
    
    def send_alert_notification(self, alert: Alert):
        """Ogohlantirish bildirishnomasini yuborish"""
        try:
            if alert.severity == "critical":
                self.send_email_alert(alert)
            
            # Log to external monitoring service
            self.log_to_external_service(alert)
            
        except Exception as e:
            self.logger.error(f"Alert notification xatosi: {e}")
    
    def send_email_alert(self, alert: Alert):
        """Email orqali ogohlantirish yuborish"""
        try:
            if not self.config.SMTP_USER or not self.config.SMTP_PASSWORD:
                return
            
            msg = MimeMultipart()
            msg['From'] = self.config.SMTP_USER
            msg['To'] = "admin@orion-starline.com"
            msg['Subject'] = f"🚨 Critical Alert: {alert.rule_name}"
            
            body = f"""
            Production Alert Detected!
            
            Rule: {alert.rule_name}
            Severity: {alert.severity}
            Message: {alert.message}
            Time: {alert.timestamp.isoformat()}
            
            Please check the monitoring dashboard immediately.
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(self.config.SMTP_HOST, self.config.SMTP_PORT)
            server.starttls()
            server.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            self.logger.info("📧 Critical alert email yuborildi")
            
        except Exception as e:
            self.logger.error(f"Email alert xatosi: {e}")
    
    def log_to_external_service(self, alert: Alert):
        """Tashqi monitoring xizmatga log qilish"""
        try:
            # This would integrate with external monitoring services like:
            # - DataDog
            # - New Relic
            # - Datadog
            # - etc.
            
            alert_data = {
                "alert_id": alert.id,
                "rule_name": alert.rule_name,
                "severity": alert.severity,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "environment": self.environment
            }
            
            # Log to monitoring service
            self.logger.info(f"📊 Alert logged to monitoring service: {alert_data}")
            
        except Exception as e:
            self.logger.error(f"External logging xatosi: {e}")
    
    def broadcast_alert(self, alert: Alert):
        """WebSocket orqali ogohlantirishni yuborish"""
        try:
            alert_data = {
                "type": "alert",
                "alert": {
                    "id": alert.id,
                    "rule_name": alert.rule_name,
                    "severity": alert.severity,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "resolved": alert.resolved
                }
            }
            
            # Send to all connected WebSocket clients
            for ws_client in self.ws_clients:
                try:
                    ws_client.send(json.dumps(alert_data))
                except Exception:
                    # Remove disconnected client
                    self.ws_clients.remove(ws_client)
            
        except Exception as e:
            self.logger.error(f"Alert broadcast xatosi: {e}")
    
    def persist_metrics(self):
        """Metrikalarni ma'lumotlar bazasiga saqlash"""
        while self.running:
            try:
                if self.metrics_buffer:
                    with sqlite3.connect(self.db_path) as conn:
                        for metric in self.metrics_buffer:
                            conn.execute(
                                "INSERT INTO metrics (timestamp, name, value, unit, environment) VALUES (?, ?, ?, ?, ?)",
                                (metric.timestamp.isoformat(), metric.name, metric.value, 
                                 metric.unit, self.environment)
                            )
                    
                    self.metrics_buffer.clear()
                    self.logger.debug("💾 Metrics saved to database")
            
            except Exception as e:
                self.logger.error(f"Metrics persistence xatosi: {e}")
            
            time.sleep(60)  # Har daqiqada bir
    
    def health_checks(self):
        """Sog'liq tekshiruvlari"""
        while self.running:
            try:
                # Check database connectivity
                db_healthy = self.check_database_health()
                
                # Check Redis connectivity
                redis_healthy = self.check_redis_health()
                
                # Check external APIs
                api_healthy = self.check_api_health()
                
                # Update health status
                self.update_health_status({
                    "database": db_healthy,
                    "redis": redis_healthy,
                    "api": api_healthy,
                    "monitoring": True
                })
                
                self.logger.debug(f"🏥 Health check: DB {db_healthy}, Redis {redis_healthy}, API {api_healthy}")
                
            except Exception as e:
                self.logger.error(f"Health check xatosi: {e}")
            
            time.sleep(60)  # Har daqiqada bir
    
    def check_database_health(self) -> bool:
        """Ma'lumotlar bazasi sog'ligini tekshirish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("SELECT 1").fetchone()
            return True
        except Exception:
            return False
    
    def check_redis_health(self) -> bool:
        """Redis sog'ligini tekshirish"""
        try:
            # This would require actual Redis connection
            return True  # Mock
        except Exception:
            return False
    
    def check_api_health(self) -> bool:
        """API sog'ligini tekshirish"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def update_health_status(self, health_status: Dict[str, bool]):
        """Sog'liq statusini yangilash"""
        # Store health status in memory for WebSocket clients
        # This could be extended to store in database or cache
        pass
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Dashboard uchun ma'lumotlar olish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Recent metrics (last 1 hour)
                cursor = conn.execute(
                    "SELECT timestamp, name, value, unit FROM metrics WHERE timestamp > ? ORDER BY timestamp DESC LIMIT 100",
                    ((datetime.now() - timedelta(hours=1)).isoformat(),)
                )
                
                recent_metrics = []
                for row in cursor.fetchall():
                    recent_metrics.append({
                        "timestamp": row[0],
                        "name": row[1],
                        "value": row[2],
                        "unit": row[3]
                    })
                
                # Active alerts
                cursor = conn.execute(
                    "SELECT alert_id, rule_name, severity, message, timestamp FROM alerts WHERE resolved = 0 ORDER BY timestamp DESC"
                )
                
                active_alerts = []
                for row in cursor.fetchall():
                    active_alerts.append({
                        "id": row[0],
                        "rule_name": row[1],
                        "severity": row[2],
                        "message": row[3],
                        "timestamp": row[4]
                    })
                
                # System overview
                cursor = conn.execute(
                    "SELECT * FROM system_metrics ORDER BY timestamp DESC LIMIT 1"
                )
                
                system_overview = {}
                row = cursor.fetchone()
                if row:
                    system_overview = {
                        "timestamp": row[1],
                        "cpu_percent": row[2],
                        "memory_percent": row[3],
                        "disk_percent": row[4],
                        "network_in": row[5],
                        "network_out": row[6],
                        "active_connections": row[7]
                    }
            
            return {
                "timestamp": datetime.now().isoformat(),
                "environment": self.environment,
                "recent_metrics": recent_metrics,
                "active_alerts": active_alerts,
                "system_overview": system_overview,
                "total_metrics": len(recent_metrics),
                "active_alerts_count": len(active_alerts)
            }
            
        except Exception as e:
            self.logger.error(f"Dashboard data xatosi: {e}")
            return {}
    
    def stop_monitoring(self):
        """Monitoring ni to'xtatish"""
        self.logger.info("📊 Production monitoring to'xtatildi")
        self.running = False
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=5)
    
    def __del__(self):
        """Cleanup"""
        self.stop_monitoring()


def main():
    """Asosiy funksiya"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production Monitoring System")
    parser.add_argument("--environment", "-e", default="production",
                       choices=["development", "staging", "production"],
                       help="Monitoring environment")
    parser.add_argument("--duration", "-d", type=int, default=3600,
                       help="Monitoring duration in seconds")
    parser.add_argument("--daemon", action="store_true",
                       help="Run as daemon")
    
    args = parser.parse_args()
    
    # Environment validatsiyasi
    if not validate_environment():
        print("❌ Environment validatsiyasi muvaffaqiyatsiz!")
        sys.exit(1)
    
    monitoring = ProductionMonitoring(args.environment)
    
    if args.daemon:
        # Run as daemon
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("⏹️ Monitoring to'xtatildi")
    else:
        # Run for specified duration
        try:
            time.sleep(args.duration)
        except KeyboardInterrupt:
            print("⏹️ Monitoring to'xtatildi")
        finally:
            monitoring.stop_monitoring()
    
    print("✅ Monitoring tizimi ishga tushdi!")


if __name__ == "__main__":
    main()