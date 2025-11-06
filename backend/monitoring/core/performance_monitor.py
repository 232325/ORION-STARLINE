#!/usr/bin/env python3
"""
Performance Monitoring va System Integration Tizimi
Asosiy monitoring tizimi - barcha metriklarni to'plash va kuzatib borish
"""

import time
import psutil
import threading
import json
import logging
import sqlite3
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from contextlib import contextmanager
from functools import wraps
import asyncio
from concurrent.futures import ThreadPoolExecutor
import statistics
import weakref

@dataclass
class PerformanceMetrics:
    """Performance metriklari"""
    timestamp: str
    cpu_usage: float
    memory_usage: float
    memory_available: float
    disk_usage: float
    network_io: Dict[str, int]
    request_count: int
    request_errors: int
    avg_response_time: float
    db_query_time: float
    error_rate: float
    throughput: float
    active_connections: int
    queue_size: int
    gc_collections: Dict[str, int]

class DatabaseMonitor:
    """Database so'rovlarni kuzatish"""
    
    def __init__(self, db_path: str = "monitoring.db"):
        self.db_path = db_path
        self.query_times = []
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Ma'lumotlar bazasini yaratish"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS db_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    query_type TEXT,
                    execution_time REAL,
                    query TEXT,
                    status TEXT,
                    row_count INTEGER
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    metric_type TEXT,
                    value REAL,
                    metadata TEXT
                )
            """)
    
    @contextmanager
    def monitor_query(self, query_type: str = "unknown", query: str = ""):
        """So'rov vaqtini o'lchash"""
        start_time = time.time()
        try:
            yield
            status = "success"
            row_count = 0
        except Exception as e:
            status = "error"
            row_count = 0
            raise
        finally:
            execution_time = time.time() - start_time
            with self.lock:
                self.query_times.append(execution_time)
                # Faqat oxirgi 1000 ta vaqtni saqlash
                if len(self.query_times) > 1000:
                    self.query_times = self.query_times[-1000:]
            
            # Ma'lumotlar bazasiga saqlash
            self._save_query_metric(query_type, execution_time, query, status, row_count)
    
    def _save_query_metric(self, query_type: str, execution_time: float, 
                          query: str, status: str, row_count: int):
        """So'rov metriqlarini saqlash"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO db_metrics 
                    (timestamp, query_type, execution_time, query, status, row_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (datetime.now().isoformat(), query_type, execution_time, 
                      query[:200], status, row_count))
        except Exception as e:
            logging.error(f"Failed to save query metric: {e}")
    
    def get_avg_query_time(self, window_minutes: int = 10) -> float:
        """O'rtacha so'rov vaqtini olish"""
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT AVG(execution_time) FROM db_metrics 
                WHERE timestamp > ?
            """, (cutoff_time.isoformat(),))
            result = cursor.fetchone()
            return result[0] if result[0] else 0.0

class SystemMonitor:
    """Sistema resurslarini kuzatish"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.initial_net_io = psutil.net_io_counters()
        self.initial_disk_io = psutil.disk_io_counters()
        self.last_timestamp = time.time()
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Sistema metriqlarini olish"""
        try:
            # CPU va Memory
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network IO
            net_io = psutil.net_io_counters()
            network_delta = net_io.bytes_sent - self.initial_net_io.bytes_sent
            
            # Disk IO
            disk_io = psutil.disk_io_counters()
            disk_delta = disk_io.read_bytes - self.initial_disk_io.read_bytes
            
            # GC statistics
            gc_stats = {}
            if hasattr(psutil, 'gc_stats'):
                gc_stats = {
                    'collections': dict(psutil.gc_stats().collections),
                    'collected': dict(psutil.gc_stats().collected)
                }
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available': memory.available,
                'memory_total': memory.total,
                'memory_used': memory.used,
                'disk_usage': (disk.used / disk.total) * 100,
                'disk_free': disk.free,
                'network_bytes_sent': net_io.bytes_sent,
                'network_bytes_recv': net_io.bytes_recv,
                'network_packets_sent': net_io.packets_sent,
                'network_packets_recv': net_io.packets_recv,
                'disk_read_bytes': disk_io.read_bytes,
                'disk_write_bytes': disk_io.write_bytes,
                'gc_collections': gc_stats,
                'process_memory': self.process.memory_info(),
                'process_cpu': self.process.cpu_percent(),
                'process_threads': self.process.num_threads(),
                'process_fds': self.process.num_fds() if hasattr(self.process, 'num_fds') else 0
            }
        except Exception as e:
            logging.error(f"Failed to get system metrics: {e}")
            return {}

class RequestTracker:
    """HTTP so'rovlarni kuzatish"""
    
    def __init__(self):
        self.request_times = []
        self.request_counts = {'total': 0, 'errors': 0}
        self.lock = threading.Lock()
        self.request_details = []
    
    def track_request(self, method: str, path: str, status_code: int, 
                     response_time: float, user_id: Optional[str] = None):
        """So'rovni kuzatish"""
        with self.lock:
            self.request_times.append(response_time)
            self.request_counts['total'] += 1
            
            if status_code >= 400:
                self.request_counts['errors'] += 1
            
            # Faqat oxirgi 1000 ta so'rovni saqlash
            if len(self.request_times) > 1000:
                self.request_times = self.request_times[-1000:]
                self.request_details = self.request_details[-1000:]
            
            self.request_details.append({
                'timestamp': datetime.now().isoformat(),
                'method': method,
                'path': path,
                'status_code': status_code,
                'response_time': response_time,
                'user_id': user_id
            })
    
    def get_metrics(self, window_minutes: int = 10) -> Dict[str, Any]:
        """So'rov metriqlarini olish"""
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        recent_requests = [
            req for req in self.request_details 
            if datetime.fromisoformat(req['timestamp']) > cutoff_time
        ]
        
        if not recent_requests:
            return {
                'request_count': 0,
                'error_count': 0,
                'avg_response_time': 0,
                'error_rate': 0,
                'throughput': 0
            }
        
        response_times = [req['response_time'] for req in recent_requests]
        error_count = sum(1 for req in recent_requests if req['status_code'] >= 400)
        
        return {
            'request_count': len(recent_requests),
            'error_count': error_count,
            'avg_response_time': statistics.mean(response_times),
            'p95_response_time': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times),
            'p99_response_time': statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else max(response_times),
            'error_rate': (error_count / len(recent_requests)) * 100,
            'throughput': len(recent_requests) / window_minutes,
            'slowest_requests': sorted(recent_requests, key=lambda x: x['response_time'], reverse=True)[:5]
        }

class AlertingSystem:
    """Ogohlantirish tizimi"""
    
    def __init__(self, alert_handlers: Optional[List[Callable]] = None):
        self.alert_handlers = alert_handlers or []
        self.alert_history = []
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'response_time': 5.0,
            'error_rate': 5.0,
            'disk_usage': 90.0
        }
        self.cooldown_period = 300  # 5 daqiqa
        self.last_alerts = {}
    
    def check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Ogohlantirishlarni tekshirish"""
        alerts = []
        current_time = time.time()
        
        for metric, threshold in self.thresholds.items():
            if metric in metrics:
                value = metrics[metric]
                if isinstance(value, (int, float)) and value > threshold:
                    # Cooldown tekshirish
                    last_alert_time = self.last_alerts.get(metric, 0)
                    if current_time - last_alert_time > self.cooldown_period:
                        alert = {
                            'timestamp': datetime.now().isoformat(),
                            'metric': metric,
                            'value': value,
                            'threshold': threshold,
                            'severity': 'high' if value > threshold * 1.5 else 'medium',
                            'message': f"{metric} {value} threshold ({threshold}) oshdi"
                        }
                        alerts.append(alert)
                        self.last_alerts[metric] = current_time
                        self.alert_history.append(alert)
        
        # Ogohlantirishlarni yuborish
        for alert in alerts:
            for handler in self.alert_handlers:
                try:
                    handler(alert)
                except Exception as e:
                    logging.error(f"Failed to send alert: {e}")
        
        return alerts

class PerformanceMonitoringSystem:
    """Asosiy Performance Monitoring Tizimi"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.running = False
        self.monitoring_interval = self.config.get('monitoring_interval', 30)
        
        # Komponentlar
        self.db_monitor = DatabaseMonitor()
        self.system_monitor = SystemMonitor()
        self.request_tracker = RequestTracker()
        self.alerting_system = AlertingSystem()
        
        # Storage
        self.metrics_history = []
        self.max_history_size = self.config.get('max_history_size', 10000)
        
        # Threading
        self.monitor_thread = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Metrics export
        self.prometheus_metrics = {}
        self.metrics_exporters = []
    
    def start(self):
        """Monitoring tizimini ishga tushirish"""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logging.info("Performance monitoring tizimi ishga tushdi")
    
    def stop(self):
        """Monitoring tizimini to'xtatish"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        self.executor.shutdown(wait=True)
        logging.info("Performance monitoring tizimi to'xtatildi")
    
    def _monitoring_loop(self):
        """Asosiy monitoring tsikli"""
        while self.running:
            try:
                # Sistema metriqlarini olish
                system_metrics = self.system_monitor.get_system_metrics()
                
                # So'rov metriqlarini olish
                request_metrics = self.request_tracker.get_metrics()
                
                # DB metriqlarini olish
                db_avg_time = self.db_monitor.get_avg_query_time()
                
                # Umumiy metriklarni yaratish
                combined_metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_usage': system_metrics.get('cpu_usage', 0),
                    'memory_usage': system_metrics.get('memory_usage', 0),
                    'memory_available': system_metrics.get('memory_available', 0),
                    'disk_usage': system_metrics.get('disk_usage', 0),
                    'network_io': {
                        'bytes_sent': system_metrics.get('network_bytes_sent', 0),
                        'bytes_recv': system_metrics.get('network_bytes_recv', 0),
                        'packets_sent': system_metrics.get('network_packets_sent', 0),
                        'packets_recv': system_metrics.get('network_packets_recv', 0)
                    },
                    'request_count': request_metrics.get('request_count', 0),
                    'request_errors': request_metrics.get('error_count', 0),
                    'avg_response_time': request_metrics.get('avg_response_time', 0),
                    'p95_response_time': request_metrics.get('p95_response_time', 0),
                    'db_query_time': db_avg_time,
                    'error_rate': request_metrics.get('error_rate', 0),
                    'throughput': request_metrics.get('throughput', 0),
                    'active_connections': self._get_active_connections(),
                    'queue_size': self._get_queue_size(),
                    'gc_collections': system_metrics.get('gc_collections', {})
                }
                
                # Ogohlantirishlarni tekshirish
                alerts = self.alerting_system.check_alerts(combined_metrics)
                
                # Metriqlarni saqlash
                self.metrics_history.append(combined_metrics)
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history = self.metrics_history[-self.max_history_size:]
                
                # Prometheus metrics ni yangilash
                self._update_prometheus_metrics(combined_metrics)
                
                # Exporterlarga yuborish
                self._export_metrics(combined_metrics)
                
            except Exception as e:
                logging.error(f"Monitoring loop error: {e}\n{traceback.format_exc()}")
            
            time.sleep(self.monitoring_interval)
    
    def _get_active_connections(self) -> int:
        """Faol ulanishlarni olish"""
        try:
            connections = len(psutil.net_connections())
            return connections
        except:
            return 0
    
    def _get_queue_size(self) -> int:
        """Navbat hajmini olish"""
        # Bu har bir application uchun maxsus bo'lishi mumkin
        return 0
    
    def _update_prometheus_metrics(self, metrics: Dict[str, Any]):
        """Prometheus metriqlarni yangilash"""
        # Bu Prometheus exporter bilan integratsiya uchun
        # Hozircha dictionary sifatida saqlaymiz
        self.prometheus_metrics.update({
            'cpu_usage': metrics.get('cpu_usage', 0),
            'memory_usage': metrics.get('memory_usage', 0),
            'response_time': metrics.get('avg_response_time', 0),
            'error_rate': metrics.get('error_rate', 0),
            'throughput': metrics.get('throughput', 0)
        })
    
    def _export_metrics(self, metrics: Dict[str, Any]):
        """Metriqlarni export qilish"""
        for exporter in self.metrics_exporters:
            try:
                exporter(metrics)
            except Exception as e:
                logging.error(f"Failed to export metrics: {e}")
    
    # Decorator'lar va yordamchi funksiyalar
    def monitor_function(self, func: Callable) -> Callable:
        """Funksiya performance ni kuzatish decorator"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                status = "success"
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                execution_time = time.time() - start_time
                with self.db_monitor.monitor_query("function", func.__name__):
                    pass  # Bu yerda real function execution bo'ladi
                
                # Response time ni request tracker ga qo'shish
                self.request_tracker.track_request(
                    method="FUNCTION",
                    path=f"func:{func.__name__}",
                    status_code=0 if status == "success" else 1,
                    response_time=execution_time
                )
        return wrapper
    
    def monitor_database_query(self, query_type: str = "unknown", query: str = ""):
        """Database so'rovni kuzatish decorator"""
        return self.db_monitor.monitor_query(query_type, query)
    
    def add_metric_exporter(self, exporter: Callable[[Dict[str, Any]], None]):
        """Metric exporter qo'shish"""
        self.metrics_exporters.append(exporter)
    
    def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """Joriy metriqlarni olish"""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_historical_metrics(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Tarixiy metriqlarni olish"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            metrics for metrics in self.metrics_history
            if datetime.fromisoformat(metrics['timestamp']) > cutoff_time
        ]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Performance summary olish"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = self.get_historical_metrics(1)  # Oxirgi soat
        
        if not recent_metrics:
            recent_metrics = self.metrics_history[-10:]  # Oxirgi 10 ta
        
        cpu_values = [m.get('cpu_usage', 0) for m in recent_metrics]
        memory_values = [m.get('memory_usage', 0) for m in recent_metrics]
        response_times = [m.get('avg_response_time', 0) for m in recent_metrics]
        error_rates = [m.get('error_rate', 0) for m in recent_metrics]
        
        return {
            'period': '1 hour' if recent_metrics == self.get_historical_metrics(1) else f'{len(recent_metrics)} samples',
            'cpu_usage': {
                'current': cpu_values[-1] if cpu_values else 0,
                'average': statistics.mean(cpu_values) if cpu_values else 0,
                'max': max(cpu_values) if cpu_values else 0,
                'min': min(cpu_values) if cpu_values else 0
            },
            'memory_usage': {
                'current': memory_values[-1] if memory_values else 0,
                'average': statistics.mean(memory_values) if memory_values else 0,
                'max': max(memory_values) if memory_values else 0,
                'min': min(memory_values) if memory_values else 0
            },
            'response_time': {
                'current': response_times[-1] if response_times else 0,
                'average': statistics.mean(response_times) if response_times else 0,
                'p95': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times),
                'p99': statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else max(response_times)
            },
            'error_rate': {
                'current': error_rates[-1] if error_rates else 0,
                'average': statistics.mean(error_rates) if error_rates else 0,
                'max': max(error_rates) if error_rates else 0
            },
            'total_requests': sum(m.get('request_count', 0) for m in recent_metrics),
            'total_errors': sum(m.get('request_errors', 0) for m in recent_metrics),
            'uptime_hours': len(recent_metrics) * self.monitoring_interval / 3600,
            'system_health': self._calculate_system_health(recent_metrics)
        }
    
    def _calculate_system_health(self, metrics: List[Dict[str, Any]]) -> str:
        """Sistema sog'lig'ini hisoblash"""
        if not metrics:
            return "unknown"
        
        latest = metrics[-1]
        cpu = latest.get('cpu_usage', 0)
        memory = latest.get('memory_usage', 0)
        error_rate = latest.get('error_rate', 0)
        response_time = latest.get('avg_response_time', 0)
        
        # Health scoring
        health_score = 100
        health_score -= min(cpu / 100 * 30, 30)  # CPU 30% penalty
        health_score -= min(memory / 100 * 25, 25)  # Memory 25% penalty
        health_score -= min(error_rate * 2, 20)  # Error rate 20% penalty
        health_score -= min(response_time / 10 * 15, 15)  # Response time 15% penalty
        
        if health_score >= 90:
            return "excellent"
        elif health_score >= 75:
            return "good"
        elif health_score >= 60:
            return "fair"
        elif health_score >= 40:
            return "poor"
        else:
            return "critical"

# Utility functions
def create_monitoring_system(config: Optional[Dict[str, Any]] = None) -> PerformanceMonitoringSystem:
    """Monitoring tizimini yaratish uchun factory function"""
    default_config = {
        'monitoring_interval': 30,
        'max_history_size': 10000,
        'alert_thresholds': {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'response_time': 5.0,
            'error_rate': 5.0,
            'disk_usage': 90.0
        }
    }
    
    if config:
        default_config.update(config)
    
    return PerformanceMonitoringSystem(default_config)

# Example usage
if __name__ == "__main__":
    # Logging setup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Monitoring tizimini yaratish
    monitor = create_monitoring_system()
    
    # Alert handler
    def slack_alert_handler(alert):
        print(f"SLACK ALERT: {alert}")
    
    # Exporter - Prometheus uchun
    def prometheus_exporter(metrics):
        # Bu yerda Prometheus metricsni export qilish
        print(f"Exporting metrics: {metrics['timestamp']}")
    
    # Monitor konfiguratsiyasi
    monitor.alerting_system.alert_handlers.append(slack_alert_handler)
    monitor.add_metric_exporter(prometheus_exporter)
    
    # Tizimni ishga tushirish
    monitor.start()
    
    # Test so'rovlari
    import random
    
    try:
        for i in range(100):
            # Simulatsiya qilingan so'rovlar
            response_time = random.uniform(0.1, 2.0)
            status_code = 200 if random.random() > 0.05 else 500
            
            monitor.request_tracker.track_request(
                method="GET",
                path=f"/api/test/{i}",
                status_code=status_code,
                response_time=response_time
            )
            
            # Simulatsiya qilingan DB so'rovi
            with monitor.monitor_database_query("select", f"SELECT * FROM test WHERE id = {i}"):
                time.sleep(random.uniform(0.01, 0.1))
            
            time.sleep(1)
        
        # Performance summary olish
        summary = monitor.get_performance_summary()
        print("\n=== PERFORMANCE SUMMARY ===")
        print(json.dumps(summary, indent=2, default=str))
        
    finally:
        monitor.stop()