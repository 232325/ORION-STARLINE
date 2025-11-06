"""
Metrics Collector - Real-time Metrics Collection System
=======================================================

Ushbu modul turli manbalardan real-time metrikalarni yig'ish va
qayta ishlash uchun mo'ljallangan.

Asosiy funksiyalar:
- Market data collection
- User activity metrics
- System performance metrics
- Signal performance metrics
- Risk assessment metrics
- Business intelligence metrics
- Custom metrics support
- Real-time aggregation
- Historical data management
- Alert generation
"""

import asyncio
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import numpy as np
import warnings
warnings.filterwarnings('ignore')

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Logging setup
logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Individual metric data point"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]
    source: str
    metadata: Dict[str, Any]


@dataclass
class MetricsBatch:
    """Batch of metrics for processing"""
    timestamp: datetime
    metrics: List[MetricPoint]
    processing_id: str


class MetricsCollector:
    """Real-time metrics collection engine"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        
        # Storage
        self.metrics_buffer = deque(maxlen=10000)
        self.processed_metrics = {}
        self.aggregated_metrics = {}
        
        # Collection control
        self.is_collecting = False
        self.collectors = {}
        self.aggregation_rules = {}
        
        # Performance tracking
        self.collection_stats = {
            'total_collected': 0,
            'total_processed': 0,
            'last_collection_time': None,
            'collection_rate': 0.0
        }
        
        # Alert thresholds
        self.thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time': 1000.0,
            'error_rate': 0.05,
            'latency': 100.0
        }
        
        # Custom collectors
        self.custom_collectors = {}
        
        # Data retention
        self.retention_policies = {
            'real_time': timedelta(hours=1),
            'aggregated_hourly': timedelta(days=7),
            'aggregated_daily': timedelta(days=30),
            'aggregated_monthly': timedelta(days=365)
        }
        
        # Threading
        self._collection_lock = threading.Lock()
        self._processing_task = None
        
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'collection_interval': 1.0,  # seconds
            'batch_size': 100,
            'aggregation_interval': 60,  # seconds
            'data_retention_days': 30,
            'max_buffer_size': 10000,
            'enable_system_metrics': True,
            'enable_market_metrics': True,
            'enable_user_metrics': True,
            'enable_custom_metrics': True
        }
    
    def start_collection(self):
        """Start metrics collection"""
        if self.is_collecting:
            logger.warning("Metrics collection is already running")
            return
        
        logger.info("Starting metrics collection...")
        self.is_collecting = True
        
        # Start built-in collectors
        if self.config['enable_system_metrics']:
            self._start_system_collector()
        
        if self.config['enable_market_metrics']:
            self._start_market_collector()
        
        if self.config['enable_user_metrics']:
            self._start_user_collector()
        
        # Start processing task
        self._processing_task = asyncio.create_task(self._process_metrics_batch())
        
        logger.info("Metrics collection started successfully")
    
    def stop_collection(self):
        """Stop metrics collection"""
        if not self.is_collecting:
            logger.warning("Metrics collection is not running")
            return
        
        logger.info("Stopping metrics collection...")
        self.is_collecting = False
        
        # Stop built-in collectors
        for collector in self.collectors.values():
            if hasattr(collector, 'stop'):
                collector.stop()
        
        self.collectors.clear()
        
        # Stop processing task
        if self._processing_task:
            self._processing_task.cancel()
            self._processing_task = None
        
        logger.info("Metrics collection stopped")
    
    def add_custom_collector(self, name: str, collector_func: Callable, interval: float = 5.0):
        """Add custom metrics collector"""
        if not self.config['enable_custom_metrics']:
            logger.warning("Custom metrics disabled in configuration")
            return
        
        self.custom_collectors[name] = {
            'function': collector_func,
            'interval': interval,
            'last_run': None,
            'enabled': True
        }
        
        logger.info(f"Custom collector '{name}' added with interval {interval}s")
    
    def collect_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None,
                      source: str = "custom", metadata: Optional[Dict[str, Any]] = None):
        """Manually add a metric point"""
        metric = MetricPoint(
            name=name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {},
            source=source,
            metadata=metadata or {}
        )
        
        with self._collection_lock:
            self.metrics_buffer.append(metric)
            self.collection_stats['total_collected'] += 1
            self.collection_stats['last_collection_time'] = datetime.now()
    
    def _start_system_collector(self):
        """Start system metrics collection"""
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available, system metrics disabled")
            return
        
        def system_collector():
            while self.is_collecting:
                try:
                    # CPU metrics
                    cpu_percent = psutil.cpu_percent(interval=None)
                    self.collect_metric('system.cpu.usage', cpu_percent, source='system')
                    
                    # Memory metrics
                    memory = psutil.virtual_memory()
                    self.collect_metric('system.memory.usage', memory.percent, source='system')
                    self.collect_metric('system.memory.available', memory.available, source='system')
                    
                    # Disk metrics
                    disk = psutil.disk_usage('/')
                    self.collect_metric('system.disk.usage', disk.used / disk.total * 100, source='system')
                    self.collect_metric('system.disk.free', disk.free, source='system')
                    
                    # Network metrics
                    net_io = psutil.net_io_counters()
                    self.collect_metric('system.network.bytes_sent', net_io.bytes_sent, source='system')
                    self.collect_metric('system.network.bytes_recv', net_io.bytes_recv, source='system')
                    
                    # Process metrics
                    process_count = len(psutil.pids())
                    self.collect_metric('system.processes.count', process_count, source='system')
                    
                    # Load average (Unix systems)
                    try:
                        load_avg = psutil.getloadavg()
                        self.collect_metric('system.load.1min', load_avg[0], source='system')
                        self.collect_metric('system.load.5min', load_avg[1], source='system')
                        self.collect_metric('system.load.15min', load_avg[2], source='system')
                    except AttributeError:
                        # Windows systems
                        pass
                    
                    time.sleep(self.config['collection_interval'])
                    
                except Exception as e:
                    logger.error(f"System collector error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=system_collector, daemon=True)
        thread.start()
        self.collectors['system'] = thread
        
        logger.info("System metrics collector started")
    
    def _start_market_collector(self):
        """Start market metrics collection"""
        def market_collector():
            while self.is_collecting:
                try:
                    # Simulated market data
                    import random
                    
                    # Price data
                    symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD']
                    for symbol in symbols:
                        price = 1.0000 + random.uniform(-0.05, 0.05)
                        volume = random.randint(100, 10000)
                        volatility = random.uniform(0.001, 0.05)
                        
                        self.collect_metric(f'market.{symbol}.price', price, 
                                          {'symbol': symbol}, 'market')
                        self.collect_metric(f'market.{symbol}.volume', volume, 
                                          {'symbol': symbol}, 'market')
                        self.collect_metric(f'market.{symbol}.volatility', volatility, 
                                          {'symbol': symbol}, 'market')
                    
                    # Market sentiment
                    market_sentiment = random.uniform(-1.0, 1.0)
                    self.collect_metric('market.sentiment', market_sentiment, source='market')
                    
                    # VIX-style volatility index
                    vix = random.uniform(10.0, 50.0)
                    self.collect_metric('market.volatility_index', vix, source='market')
                    
                    time.sleep(self.config['collection_interval'])
                    
                except Exception as e:
                    logger.error(f"Market collector error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=market_collector, daemon=True)
        thread.start()
        self.collectors['market'] = thread
        
        logger.info("Market metrics collector started")
    
    def _start_user_collector(self):
        """Start user activity metrics collection"""
        def user_collector():
            while self.is_collecting:
                try:
                    # Simulated user activity
                    import random
                    
                    # Active users
                    active_users = random.randint(50, 500)
                    self.collect_metric('users.active', active_users, source='users')
                    
                    # New registrations
                    new_users = random.randint(0, 20)
                    self.collect_metric('users.new_registrations', new_users, source='users')
                    
                    # Session metrics
                    avg_session_duration = random.uniform(60, 1800)  # seconds
                    self.collect_metric('users.session_duration.avg', avg_session_duration, source='users')
                    
                    # Trading activity
                    total_trades = random.randint(10, 100)
                    winning_trades = random.randint(0, total_trades)
                    win_rate = winning_trades / total_trades if total_trades > 0 else 0
                    
                    self.collect_metric('users.trades.total', total_trades, source='users')
                    self.collect_metric('users.trades.win_rate', win_rate, source='users')
                    
                    # API calls
                    api_calls = random.randint(1000, 10000)
                    self.collect_metric('api.calls.count', api_calls, source='api')
                    
                    # Error rate
                    error_rate = random.uniform(0, 0.1)
                    self.collect_metric('api.errors.rate', error_rate, source='api')
                    
                    time.sleep(self.config['collection_interval'])
                    
                except Exception as e:
                    logger.error(f"User collector error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=user_collector, daemon=True)
        thread.start()
        self.collectors['users'] = thread
        
        logger.info("User metrics collector started")
    
    async def _process_metrics_batch(self):
        """Process metrics in batches"""
        while self.is_collecting:
            try:
                with self._collection_lock:
                    # Get batch of metrics
                    batch_size = min(self.config['batch_size'], len(self.metrics_buffer))
                    if batch_size == 0:
                        await asyncio.sleep(0.1)
                        continue
                    
                    batch_metrics = [self.metrics_buffer.popleft() 
                                   for _ in range(batch_size)]
                
                # Process batch
                batch = MetricsBatch(
                    timestamp=datetime.now(),
                    metrics=batch_metrics,
                    processing_id=f"batch_{int(time.time())}"
                )
                
                await self._process_batch(batch)
                self.collection_stats['total_processed'] += len(batch_metrics)
                
                # Update collection rate
                self._update_collection_rate()
                
                await asyncio.sleep(self.config['aggregation_interval'])
                
            except Exception as e:
                logger.error(f"Metrics processing error: {e}")
                await asyncio.sleep(5)
    
    async def _process_batch(self, batch: MetricsBatch):
        """Process a batch of metrics"""
        # Group metrics by name
        metrics_by_name = defaultdict(list)
        for metric in batch.metrics:
            metrics_by_name[metric.name].append(metric)
        
        # Process each metric group
        for name, metrics in metrics_by_name.items():
            await self._aggregate_metrics(name, metrics)
        
        # Generate alerts
        await self._check_alerts(batch.metrics)
        
        # Clean up old data
        await self._cleanup_old_data()
    
    async def _aggregate_metrics(self, name: str, metrics: List[MetricPoint]):
        """Aggregate metrics"""
        if name not in self.aggregated_metrics:
            self.aggregated_metrics[name] = {
                'values': deque(maxlen=1000),
                'tags': {},
                'last_update': None
            }
        
        # Add new values
        values = [m.value for m in metrics]
        self.aggregated_metrics[name]['values'].extend(values)
        self.aggregated_metrics[name]['last_update'] = datetime.now()
        
        # Store tags from first metric
        if metrics and not self.aggregated_metrics[name]['tags']:
            self.aggregated_metrics[name]['tags'] = metrics[0].tags.copy()
        
        # Calculate aggregations
        if len(values) > 0:
            agg_data = {
                'count': len(values),
                'sum': sum(values),
                'min': min(values),
                'max': max(values),
                'avg': np.mean(values),
                'median': np.median(values),
                'std': np.std(values) if len(values) > 1 else 0,
                'last_value': values[-1],
                'timestamp': datetime.now()
            }
            
            # Store processed metrics
            if name not in self.processed_metrics:
                self.processed_metrics[name] = deque(maxlen=1000)
            
            self.processed_metrics[name].append(agg_data)
    
    async def _check_alerts(self, metrics: List[MetricPoint]):
        """Check metrics against thresholds"""
        for metric in metrics:
            # System alerts
            if metric.name in self.thresholds:
                threshold = self.thresholds[metric.name]
                if metric.value > threshold:
                    severity = self._get_alert_severity(metric.name, metric.value, threshold)
                    alert = {
                        'type': 'threshold_breach',
                        'metric': metric.name,
                        'value': metric.value,
                        'threshold': threshold,
                        'severity': severity,
                        'timestamp': metric.timestamp,
                        'source': metric.source
                    }
                    logger.warning(f"ALERT [{severity}]: {metric.name} = {metric.value} (threshold: {threshold})")
    
    def _get_alert_severity(self, metric_name: str, value: float, threshold: float) -> str:
        """Determine alert severity"""
        ratio = value / threshold
        
        if ratio > 1.5:
            return 'CRITICAL'
        elif ratio > 1.2:
            return 'HIGH'
        elif ratio > 1.0:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    async def _cleanup_old_data(self):
        """Clean up old metrics data"""
        current_time = datetime.now()
        
        # Clean up aggregated metrics
        retention_cutoff = current_time - timedelta(days=self.config['data_retention_days'])
        
        for name, data in self.aggregated_metrics.items():
            if data['last_update'] and data['last_update'] < retention_cutoff:
                del self.aggregated_metrics[name]
        
        # Clean up processed metrics
        for name, data in self.processed_metrics.items():
            if data and data[0].get('timestamp', current_time) < retention_cutoff:
                # Remove old entries while maintaining maxlen
                while data and data[0].get('timestamp', current_time) < retention_cutoff:
                    data.popleft()
    
    def _update_collection_rate(self):
        """Update metrics collection rate"""
        current_time = datetime.now()
        last_time = self.collection_stats.get('last_collection_time')
        
        if last_time:
            time_diff = (current_time - last_time).total_seconds()
            if time_diff > 0:
                self.collection_stats['collection_rate'] = 1.0 / time_diff
    
    def get_metric_value(self, name: str, aggregation: str = 'last') -> Optional[float]:
        """Get current metric value"""
        if name not in self.aggregated_metrics:
            return None
        
        values = list(self.aggregated_metrics[name]['values'])
        if not values:
            return None
        
        if aggregation == 'last':
            return values[-1]
        elif aggregation == 'avg':
            return np.mean(values)
        elif aggregation == 'min':
            return np.min(values)
        elif aggregation == 'max':
            return np.max(values)
        elif aggregation == 'sum':
            return np.sum(values)
        else:
            return values[-1]
    
    def get_metric_history(self, name: str, limit: int = 100) -> List[Dict]:
        """Get metric history"""
        if name not in self.processed_metrics:
            return []
        
        return [dict(item) for item in list(self.processed_metrics[name])[-limit:]]
    
    def get_all_metrics_summary(self) -> Dict:
        """Get summary of all collected metrics"""
        summary = {
            'collection_stats': self.collection_stats.copy(),
            'active_collectors': list(self.collectors.keys()),
            'total_metric_types': len(self.aggregated_metrics),
            'metric_names': list(self.aggregated_metrics.keys()),
            'custom_collectors': list(self.custom_collectors.keys()),
            'is_collecting': self.is_collecting
        }
        
        return summary
    
    def set_threshold(self, metric_name: str, threshold: float):
        """Set alert threshold for a metric"""
        self.thresholds[metric_name] = threshold
        logger.info(f"Threshold set for {metric_name}: {threshold}")
    
    def add_aggregation_rule(self, name: str, rule: Dict):
        """Add custom aggregation rule"""
        self.aggregation_rules[name] = rule
        logger.info(f"Aggregation rule added: {name}")
    
    def export_metrics_data(self, format_type: str = 'json', metric_names: Optional[List[str]] = None) -> str:
        """Export metrics data"""
        data = {
            'export_timestamp': datetime.now().isoformat(),
            'summary': self.get_all_metrics_summary(),
            'metrics': {}
        }
        
        # Filter by metric names if specified
        metrics_to_export = metric_names or list(self.aggregated_metrics.keys())
        
        for name in metrics_to_export:
            if name in self.aggregated_metrics:
                data['metrics'][name] = {
                    'values': list(self.aggregated_metrics[name]['values']),
                    'tags': self.aggregated_metrics[name]['tags'],
                    'last_update': self.aggregated_metrics[name]['last_update'].isoformat() if self.aggregated_metrics[name]['last_update'] else None
                }
        
        if format_type.lower() == 'json':
            return json.dumps(data, indent=2, default=str)
        else:
            return str(data)
    
    def get_real_time_metrics(self) -> Dict:
        """Get real-time metrics for dashboard"""
        real_time_data = {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': {},
            'market_metrics': {},
            'user_metrics': {},
            'api_metrics': {},
            'alerts': []
        }
        
        # System metrics
        system_keys = [k for k in self.aggregated_metrics.keys() if k.startswith('system.')]
        for key in system_keys:
            value = self.get_metric_value(key, 'last')
            if value is not None:
                metric_name = key.replace('system.', '')
                real_time_data['system_metrics'][metric_name] = value
        
        # Market metrics
        market_keys = [k for k in self.aggregated_metrics.keys() if k.startswith('market.')]
        for key in market_keys:
            value = self.get_metric_value(key, 'last')
            if value is not None:
                metric_name = key.replace('market.', '')
                real_time_data['market_metrics'][metric_name] = value
        
        # User metrics
        user_keys = [k for k in self.aggregated_metrics.keys() if k.startswith('users.')]
        for key in user_keys:
            value = self.get_metric_value(key, 'last')
            if value is not None:
                metric_name = key.replace('users.', '')
                real_time_data['user_metrics'][metric_name] = value
        
        # API metrics
        api_keys = [k for k in self.aggregated_metrics.keys() if k.startswith('api.')]
        for key in api_keys:
            value = self.get_metric_value(key, 'last')
            if value is not None:
                metric_name = key.replace('api.', '')
                real_time_data['api_metrics'][metric_name] = value
        
        return real_time_data


# Demo and testing functions
def create_metrics_collector(config: Optional[Dict] = None) -> MetricsCollector:
    """Factory function to create metrics collector"""
    return MetricsCollector(config)


async def run_metrics_demo():
    """Metrics collector demonstration"""
    print("Real-time Metrics Collector Demo boshlanmoqda...")
    
    # Create collector
    config = {
        'collection_interval': 0.5,
        'batch_size': 50,
        'aggregation_interval': 1.0
    }
    
    collector = create_metrics_collector(config)
    
    # Add custom collector
    def custom_metric_collector():
        import random
        custom_value = random.uniform(0, 100)
        collector.collect_metric('custom.metric', custom_value, source='custom_demo')
    
    collector.add_custom_collector('demo', custom_metric_collector, interval=2.0)
    
    # Start collection
    collector.start_collection()
    
    try:
        # Run for demo period
        await asyncio.sleep(10)
        
        # Add some manual metrics
        collector.collect_metric('manual.test', 42.0, {'test': 'value'}, 'demo')
        collector.collect_metric('manual.test2', 84.5, {'category': 'demo'}, 'demo')
        
        # Get summary
        print("\n=== METRICS COLLECTOR SUMMARY ===")
        summary = collector.get_all_metrics_summary()
        print(f"Total collected: {summary['collection_stats']['total_collected']}")
        print(f"Total processed: {summary['collection_stats']['total_processed']}")
        print(f"Active collectors: {summary['active_collectors']}")
        print(f"Total metric types: {summary['total_metric_types']}")
        
        # Get real-time data
        print("\n=== REAL-TIME METRICS ===")
        realtime = collector.get_real_time_metrics()
        
        print("System metrics:", len(realtime['system_metrics']))
        print("Market metrics:", len(realtime['market_metrics']))
        print("User metrics:", len(realtime['user_metrics']))
        print("API metrics:", len(realtime['api_metrics']))
        
        # Get specific metric
        cpu_usage = collector.get_metric_value('system.cpu.usage')
        if cpu_usage:
            print(f"\nCurrent CPU usage: {cpu_usage:.1f}%")
        
        # Export data
        print("\n=== EXPORT SAMPLE ===")
        exported = collector.export_metrics_data('json', ['system.cpu.usage'])
        print("Exported data (first 200 chars):", exported[:200] + "...")
        
    finally:
        # Stop collection
        collector.stop_collection()
        print("\nDemo tugallandi!")


if __name__ == "__main__":
    # Run demo
    asyncio.run(run_metrics_demo())