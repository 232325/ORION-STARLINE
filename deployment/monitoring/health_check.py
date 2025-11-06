"""
Advanced monitoring and health check system for Orion Starline
Production-grade monitoring with real-time alerts and metrics collection
"""

import asyncio
import logging
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import aiohttp
import asyncpg
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('orion_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('orion_request_duration_seconds', 'Request latency in seconds')
ACTIVE_CONNECTIONS = Gauge('orion_active_connections', 'Active connections')
CPU_USAGE = Gauge('orion_cpu_usage_percent', 'CPU usage percentage')
MEMORY_USAGE = Gauge('orion_memory_usage_percent', 'Memory usage percentage')
DISK_USAGE = Gauge('orion_disk_usage_percent', 'Disk usage percentage')
DATABASE_CONNECTIONS = Gauge('orion_database_connections', 'Database connections')
CACHE_HIT_RATE = Gauge('orion_cache_hit_rate', 'Cache hit rate')
TRADING_SIGNALS = Counter('orion_trading_signals_total', 'Trading signals generated', ['signal_type'])
ERROR_COUNT = Counter('orion_errors_total', 'Total errors', ['error_type'])

class SystemMonitor:
    """System-level monitoring and metrics collection"""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'disk_usage': [],
            'network_io': [],
            'process_count': []
        }
    
    async def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            CPU_USAGE.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            MEMORY_USAGE.set(memory_percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            DISK_USAGE.set(disk_percent)
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            # Process count
            process_count = len(psutil.pids())
            
            # Store metrics for trend analysis
            self.metrics['cpu_usage'].append(cpu_percent)
            self.metrics['memory_usage'].append(memory_percent)
            self.metrics['disk_usage'].append(disk_percent)
            self.metrics['network_io'].append(network_io)
            self.metrics['process_count'].append(process_count)
            
            # Keep only last 100 data points
            for key in self.metrics:
                if len(self.metrics[key]) > 100:
                    self.metrics[key] = self.metrics[key][-100:]
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'network_io': network_io,
                'process_count': process_count,
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            }
            
        except Exception as e:
            logger.error("Error collecting system metrics", error=str(e))
            ERROR_COUNT.labels(error_type='system_metrics').inc()
            return {}
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check system health and return status"""
        health = {
            'status': 'healthy',
            'checks': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # CPU check
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                health['checks']['cpu'] = {'status': 'critical', 'value': cpu_percent}
                health['status'] = 'critical'
            elif cpu_percent > 80:
                health['checks']['cpu'] = {'status': 'warning', 'value': cpu_percent}
                if health['status'] == 'healthy':
                    health['status'] = 'warning'
            else:
                health['checks']['cpu'] = {'status': 'healthy', 'value': cpu_percent}
            
            # Memory check
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                health['checks']['memory'] = {'status': 'critical', 'value': memory.percent}
                health['status'] = 'critical'
            elif memory.percent > 80:
                health['checks']['memory'] = {'status': 'warning', 'value': memory.percent}
                if health['status'] == 'healthy':
                    health['status'] = 'warning'
            else:
                health['checks']['memory'] = {'status': 'healthy', 'value': memory.percent}
            
            # Disk check
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > 90:
                health['checks']['disk'] = {'status': 'critical', 'value': disk_percent}
                health['status'] = 'critical'
            elif disk_percent > 80:
                health['checks']['disk'] = {'status': 'warning', 'value': disk_percent}
                if health['status'] == 'healthy':
                    health['status'] = 'warning'
            else:
                health['checks']['disk'] = {'status': 'healthy', 'value': disk_percent}
            
        except Exception as e:
            logger.error("Error checking system health", error=str(e))
            health['checks']['system_check'] = {'status': 'error', 'error': str(e)}
            health['status'] = 'error'
        
        return health

class DatabaseMonitor:
    """Database connection and performance monitoring"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection_count = 0
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database health and connectivity"""
        health = {
            'status': 'healthy',
            'checks': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Test database connection
            conn = await asyncpg.connect(self.database_url)
            
            # Check connection
            await conn.execute('SELECT 1')
            self.connection_count = await conn.fetchval(
                'SELECT count(*) FROM pg_stat_activity WHERE state = $1', 
                'active'
            )
            
            DATABASE_CONNECTIONS.set(self.connection_count)
            
            # Get database stats
            stats = await conn.fetchrow("""
                SELECT 
                    xact_commit,
                    xact_rollback,
                    blks_read,
                    blks_hit,
                    tup_returned,
                    tup_fetched
                FROM pg_stat_database 
                WHERE datname = current_database()
            """)
            
            await conn.close()
            
            health['checks']['connection'] = {'status': 'healthy', 'value': 'connected'}
            health['checks']['active_connections'] = {
                'status': 'healthy' if self.connection_count < 80 else 'warning',
                'value': self.connection_count
            }
            
            if self.connection_count > 90:
                health['status'] = 'critical'
            elif self.connection_count > 80:
                health['status'] = 'warning'
            
            health['stats'] = dict(stats) if stats else {}
            
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            ERROR_COUNT.labels(error_type='database').inc()
            health['checks']['connection'] = {'status': 'critical', 'error': str(e)}
            health['status'] = 'critical'
        
        return health
    
    async def get_database_metrics(self) -> Dict[str, Any]:
        """Get detailed database metrics"""
        try:
            conn = await asyncpg.connect(self.database_url)
            
            # Get database size
            db_size = await conn.fetchval("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """)
            
            # Get table sizes
            table_sizes = await conn.fetch("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                FROM pg_tables 
                WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                LIMIT 10
            """)
            
            # Get slow queries
            slow_queries = await conn.fetch("""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    max_time
                FROM pg_stat_statements 
                ORDER BY mean_time DESC 
                LIMIT 5
            """)
            
            await conn.close()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'database_size': db_size,
                'table_sizes': [dict(row) for row in table_sizes],
                'slow_queries': [dict(row) for row in slow_queries],
                'connection_count': self.connection_count
            }
            
        except Exception as e:
            logger.error("Error getting database metrics", error=str(e))
            return {'error': str(e)}

class CacheMonitor:
    """Redis cache monitoring"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
    
    async def connect_redis(self):
        """Connect to Redis"""
        if not self.redis_client:
            self.redis_client = redis.from_url(self.redis_url)
    
    async def check_cache_health(self) -> Dict[str, Any]:
        """Check Redis cache health"""
        health = {
            'status': 'healthy',
            'checks': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            await self.connect_redis()
            
            # Test connection
            await self.redis_client.ping()
            
            # Get Redis info
            info = await self.redis_client.info()
            
            # Calculate cache hit rate
            keyspace_hits = info.get('keyspace_hits', 0)
            keyspace_misses = info.get('keyspace_misses', 0)
            total_requests = keyspace_hits + keyspace_misses
            
            if total_requests > 0:
                hit_rate = keyspace_hits / total_requests * 100
                CACHE_HIT_RATE.set(hit_rate)
            else:
                hit_rate = 0
            
            health['checks']['connection'] = {'status': 'healthy', 'value': 'connected'}
            health['checks']['hit_rate'] = {
                'status': 'healthy' if hit_rate > 80 else 'warning',
                'value': round(hit_rate, 2)
            }
            health['checks']['memory_usage'] = {
                'status': 'healthy' if info.get('used_memory_percentage', 0) < 80 else 'warning',
                'value': info.get('used_memory_percentage', 0)
            }
            
            health['info'] = {
                'used_memory_human': info.get('used_memory_human', '0B'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'keyspace_hits': keyspace_hits,
                'keyspace_misses': keyspace_misses
            }
            
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            ERROR_COUNT.labels(error_type='redis').inc()
            health['checks']['connection'] = {'status': 'critical', 'error': str(e)}
            health['status'] = 'critical'
        
        return health

class TradingSystemMonitor:
    """Trading system specific monitoring"""
    
    def __init__(self):
        self.signal_counts = {}
        self.error_counts = {}
    
    async def monitor_trading_signals(self) -> Dict[str, Any]:
        """Monitor trading signal generation and processing"""
        try:
            # This would integrate with your trading signal system
            # For now, we'll simulate monitoring
            
            signal_metrics = {
                'timestamp': datetime.now().isoformat(),
                'signals_generated_today': 0,
                'signals_processed': 0,
                'signals_failed': 0,
                'avg_processing_time': 0,
                'signal_types': {}
            }
            
            # Update Prometheus metrics
            for signal_type, count in self.signal_counts.items():
                TRADING_SIGNALS.labels(signal_type=signal_type).inc()
                signal_metrics['signal_types'][signal_type] = count
            
            return signal_metrics
            
        except Exception as e:
            logger.error("Error monitoring trading signals", error=str(e))
            return {'error': str(e)}
    
    def record_signal(self, signal_type: str):
        """Record a trading signal"""
        self.signal_counts[signal_type] = self.signal_counts.get(signal_type, 0) + 1
        TRADING_SIGNALS.labels(signal_type=signal_type).inc()
    
    def record_error(self, error_type: str):
        """Record an error"""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        ERROR_COUNT.labels(error_type=error_type).inc()

class HealthCheckAPI:
    """HTTP API for health checks and monitoring"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.system_monitor = SystemMonitor()
        self.db_monitor = DatabaseMonitor(config.get('database_url', ''))
        self.cache_monitor = CacheMonitor(config.get('redis_url', ''))
        self.trading_monitor = TradingSystemMonitor()
        
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        try:
            # Run all health checks concurrently
            system_health = self.system_monitor.check_system_health()
            db_health = await self.db_monitor.check_database_health()
            cache_health = await self.cache_monitor.check_cache_health()
            
            # Combine results
            overall_status = 'healthy'
            if system_health['status'] == 'critical' or db_health['status'] == 'critical' or cache_health['status'] == 'critical':
                overall_status = 'critical'
            elif system_health['status'] == 'warning' or db_health['status'] == 'warning' or cache_health['status'] == 'warning':
                overall_status = 'warning'
            
            return {
                'status': overall_status,
                'timestamp': datetime.now().isoformat(),
                'uptime': time.time() - self.system_monitor.start_time,
                'services': {
                    'system': system_health,
                    'database': db_health,
                    'cache': cache_health
                },
                'version': '1.0.0'
            }
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get detailed metrics"""
        try:
            system_metrics = await self.system_monitor.collect_system_metrics()
            db_metrics = await self.db_monitor.get_database_metrics()
            trading_metrics = await self.trading_monitor.monitor_trading_signals()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'system': system_metrics,
                'database': db_metrics,
                'trading': trading_metrics,
                'prometheus_ready': True
            }
            
        except Exception as e:
            logger.error("Error getting metrics", error=str(e))
            return {'error': str(e)}

async def main():
    """Main monitoring function"""
    # Load configuration
    config = {
        'database_url': 'postgresql://orion:secure_password@localhost:5432/orion_db',
        'redis_url': 'redis://localhost:6379/0'
    }
    
    # Start Prometheus metrics server
    start_http_server(8001)
    
    # Create health check API
    health_api = HealthCheckAPI(config)
    
    # Start monitoring loop
    logger.info("Starting monitoring system")
    
    while True:
        try:
            # Collect metrics every 30 seconds
            await asyncio.sleep(30)
            
            # Collect system metrics
            metrics = await health_api.get_metrics()
            
            # Log metrics
            logger.info("Metrics collected", metrics=metrics)
            
            # Check health every 5 minutes
            if int(time.time()) % 300 == 0:
                health_status = await health_api.health_check()
                logger.info("Health check completed", status=health_status)
                
                # Alert if unhealthy
                if health_status['status'] in ['critical', 'error']:
                    logger.error("System health critical", status=health_status)
        
        except Exception as e:
            logger.error("Monitoring loop error", error=str(e))
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())