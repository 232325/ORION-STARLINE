"""
Dashboard Integration - Real-time Dashboard & Visualization
===========================================================

Ushbu modul real-time analitika ma'lumotlarini dashboard va 
visualization tizimlari bilan integratsiya qilish uchun mo'ljallangan.

Asosiy funksiyalar:
- Real-time dashboard data
- Chart data generation
- WebSocket integration
- REST API endpoints
- Data export/import
- Custom visualizations
- Alert notifications
- Performance metrics
- User interface components
- Mobile responsiveness
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import deque
import numpy as np
from enum import Enum

try:
    from flask import Flask, jsonify, request
    from flask_socketio import SocketIO, emit
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Import local modules
try:
    from .analytics_engine import AnalyticsEngine
    from .metrics_collector import MetricsCollector
except ImportError:
    # For direct execution
    from analytics_engine import AnalyticsEngine
    from metrics_collector import MetricsCollector

# Logging setup
logger = logging.getLogger(__name__)


class ChartType(Enum):
    """Chart type options"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    CANDLESTICK = "candlestick"
    AREA = "area"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"


@dataclass
class DashboardConfig:
    """Dashboard configuration"""
    name: str
    refresh_interval: int  # seconds
    chart_configs: List[Dict]
    alert_configs: List[Dict]
    layout_config: Dict
    theme: str = "default"
    auto_refresh: bool = True


@dataclass
class ChartData:
    """Chart data structure"""
    chart_id: str
    chart_type: ChartType
    title: str
    data: Dict
    timestamp: datetime
    metadata: Dict


class DashboardIntegration:
    """Real-time dashboard integration system"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        
        # Core components
        self.analytics_engine: Optional[AnalyticsEngine] = None
        self.metrics_collector: Optional[MetricsCollector] = None
        
        # Dashboard data
        self.dashboards = {}
        self.active_connections = set()
        self.chart_cache = {}
        
        # Web server
        self.app = None
        self.socketio = None
        self.is_server_running = False
        
        # Data streams
        self.data_streams = {}
        self.stream_handlers = {}
        
        # Alert system
        self.active_alerts = deque(maxlen=100)
        self.alert_handlers = []
        
        # Performance
        self.update_stats = {
            'total_updates': 0,
            'successful_updates': 0,
            'failed_updates': 0,
            'last_update_time': None,
            'average_update_time': 0.0
        }
        
        # Dashboard configurations
        self.dashboard_configs = {}
        
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            'dashboard': {
                'host': '0.0.0.0',
                'port': 5000,
                'debug': False,
                'auto_start': False
            },
            'web_socket': {
                'namespace': '/dashboard',
                'transports': ['websocket', 'polling'],
                'cors_allowed_origins': '*'
            },
            'data_refresh': {
                'default_interval': 1,  # seconds
                'chart_timeout': 30,   # seconds
                'max_data_points': 1000
            },
            'caching': {
                'cache_ttl': 30,  # seconds
                'max_cache_size': 100
            },
            'throttling': {
                'max_updates_per_second': 10,
                'burst_limit': 50
            }
        }
    
    def initialize(self, analytics_engine: AnalyticsEngine, metrics_collector: MetricsCollector):
        """Initialize with analytics engine and metrics collector"""
        self.analytics_engine = analytics_engine
        self.metrics_collector = metrics_collector
        
        # Set up data streams
        self._setup_data_streams()
        
        # Create default dashboards
        self._create_default_dashboards()
        
        logger.info("Dashboard integration initialized")
    
    def _setup_data_streams(self):
        """Set up data streams for real-time updates"""
        self.data_streams = {
            'market_data': {
                'source': 'analytics_engine.market_data',
                'handler': self._handle_market_data_stream,
                'interval': 1.0
            },
            'system_metrics': {
                'source': 'metrics_collector.real_time_metrics',
                'handler': self._handle_system_metrics_stream,
                'interval': 2.0
            },
            'user_metrics': {
                'source': 'analytics_engine.user_data',
                'handler': self._handle_user_metrics_stream,
                'interval': 5.0
            },
            'alerts': {
                'source': 'analytics_engine.alerts',
                'handler': self._handle_alerts_stream,
                'interval': 0.5
            },
            'signal_performance': {
                'source': 'analytics_engine.signal_data',
                'handler': self._handle_signal_performance_stream,
                'interval': 10.0
            }
        }
    
    def _create_default_dashboards(self):
        """Create default dashboard configurations"""
        
        # Market Overview Dashboard
        market_dashboard = DashboardConfig(
            name="market_overview",
            refresh_interval=1,
            chart_configs=[
                {
                    'id': 'price_chart',
                    'type': 'line',
                    'title': 'Price Movement',
                    'data_source': 'market_data',
                    'x_axis': 'timestamp',
                    'y_axis': 'price',
                    'config': {'colors': ['#3b82f6']}
                },
                {
                    'id': 'volume_chart',
                    'type': 'bar',
                    'title': 'Volume',
                    'data_source': 'market_data',
                    'x_axis': 'timestamp',
                    'y_axis': 'volume',
                    'config': {'colors': ['#10b981']}
                },
                {
                    'id': 'volatility_chart',
                    'type': 'line',
                    'title': 'Volatility',
                    'data_source': 'market_data',
                    'x_axis': 'timestamp',
                    'y_axis': 'volatility',
                    'config': {'colors': ['#f59e0b']}
                }
            ],
            alert_configs=[
                {
                    'metric': 'market.volatility',
                    'threshold': 0.05,
                    'severity': 'MEDIUM',
                    'action': 'show_alert'
                }
            ],
            layout_config={
                'columns': 3,
                'rows': 2,
                'responsive': True
            }
        )
        
        # System Monitoring Dashboard
        system_dashboard = DashboardConfig(
            name="system_monitoring",
            refresh_interval=2,
            chart_configs=[
                {
                    'id': 'cpu_usage',
                    'type': 'gauge',
                    'title': 'CPU Usage',
                    'data_source': 'system_metrics',
                    'config': {'max': 100, 'colors': ['#10b981', '#f59e0b', '#ef4444']}
                },
                {
                    'id': 'memory_usage',
                    'type': 'gauge',
                    'title': 'Memory Usage',
                    'data_source': 'system_metrics',
                    'config': {'max': 100, 'colors': ['#10b981', '#f59e0b', '#ef4444']}
                },
                {
                    'id': 'response_time',
                    'type': 'line',
                    'title': 'API Response Time',
                    'data_source': 'system_metrics',
                    'x_axis': 'timestamp',
                    'y_axis': 'response_time',
                    'config': {'colors': ['#8b5cf6']}
                }
            ],
            alert_configs=[
                {
                    'metric': 'system.cpu.usage',
                    'threshold': 80,
                    'severity': 'HIGH',
                    'action': 'show_alert'
                },
                {
                    'metric': 'system.memory.usage',
                    'threshold': 85,
                    'severity': 'HIGH',
                    'action': 'show_alert'
                }
            ],
            layout_config={
                'columns': 3,
                'rows': 2,
                'responsive': True
            }
        )
        
        # User Analytics Dashboard
        user_dashboard = DashboardConfig(
            name="user_analytics",
            refresh_interval=5,
            chart_configs=[
                {
                    'id': 'active_users',
                    'type': 'counter',
                    'title': 'Active Users',
                    'data_source': 'user_metrics',
                    'config': {'color': '#3b82f6'}
                },
                {
                    'id': 'engagement_chart',
                    'type': 'bar',
                    'title': 'User Engagement',
                    'data_source': 'user_metrics',
                    'x_axis': 'metric',
                    'y_axis': 'value',
                    'config': {'colors': ['#3b82f6']}
                },
                {
                    'id': 'retention_chart',
                    'type': 'line',
                    'title': 'User Retention',
                    'data_source': 'user_metrics',
                    'x_axis': 'timestamp',
                    'y_axis': 'retention_rate',
                    'config': {'colors': ['#10b981']}
                }
            ],
            alert_configs=[],
            layout_config={
                'columns': 2,
                'rows': 2,
                'responsive': True
            }
        )
        
        # Signal Performance Dashboard
        signal_dashboard = DashboardConfig(
            name="signal_performance",
            refresh_interval=10,
            chart_configs=[
                {
                    'id': 'accuracy_chart',
                    'type': 'gauge',
                    'title': 'Signal Accuracy',
                    'data_source': 'signal_performance',
                    'config': {'max': 100, 'colors': ['#ef4444', '#f59e0b', '#10b981']}
                },
                {
                    'id': 'return_chart',
                    'type': 'line',
                    'title': 'Returns',
                    'data_source': 'signal_performance',
                    'x_axis': 'timestamp',
                    'y_axis': 'return',
                    'config': {'colors': ['#8b5cf6']}
                },
                {
                    'id': 'drawdown_chart',
                    'type': 'area',
                    'title': 'Drawdown',
                    'data_source': 'signal_performance',
                    'x_axis': 'timestamp',
                    'y_axis': 'drawdown',
                    'config': {'colors': ['#f59e0b']}
                }
            ],
            alert_configs=[
                {
                    'metric': 'signal.drawdown',
                    'threshold': 0.2,
                    'severity': 'CRITICAL',
                    'action': 'show_alert'
                }
            ],
            layout_config={
                'columns': 3,
                'rows': 2,
                'responsive': True
            }
        )
        
        # Store configurations
        self.dashboard_configs = {
            'market_overview': market_dashboard,
            'system_monitoring': system_dashboard,
            'user_analytics': user_dashboard,
            'signal_performance': signal_dashboard
        }
    
    def create_dashboard(self, config: DashboardConfig) -> str:
        """Create a new dashboard"""
        dashboard_id = config.name.lower().replace(' ', '_')
        self.dashboard_configs[dashboard_id] = config
        
        logger.info(f"Dashboard created: {config.name}")
        return dashboard_id
    
    def start_web_server(self):
        """Start the web dashboard server"""
        if not FLASK_AVAILABLE:
            logger.error("Flask and Flask-SocketIO not available")
            return False
        
        if self.is_server_running:
            logger.warning("Web server is already running")
            return True
        
        # Create Flask app
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'dashboard-secret-key'
        
        # Create SocketIO
        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins=self.config['web_socket']['cors_allowed_origins'],
            transports=self.config['web_socket']['transports']
        )
        
        # Set up routes
        self._setup_routes()
        self._setup_websocket_handlers()
        
        # Start server
        host = self.config['dashboard']['host']
        port = self.config['dashboard']['port']
        debug = self.config['dashboard']['debug']
        
        try:
            self.socketio.run(
                self.app,
                host=host,
                port=port,
                debug=debug
            )
            self.is_server_running = True
            logger.info(f"Dashboard server started on {host}:{port}")
            return True
        except Exception as e:
            logger.error(f"Failed to start dashboard server: {e}")
            return False
    
    def _setup_routes(self):
        """Set up HTTP routes"""
        
        @self.app.route('/api/dashboards')
        def get_dashboards():
            """Get list of available dashboards"""
            return jsonify({
                'dashboards': list(self.dashboard_configs.keys()),
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/dashboard/<dashboard_id>')
        def get_dashboard(dashboard_id):
            """Get dashboard configuration"""
            if dashboard_id not in self.dashboard_configs:
                return jsonify({'error': 'Dashboard not found'}), 404
            
            config = self.dashboard_configs[dashboard_id]
            return jsonify({
                'config': asdict(config),
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/dashboard/<dashboard_id>/data')
        def get_dashboard_data(dashboard_id):
            """Get real-time dashboard data"""
            if dashboard_id not in self.dashboard_configs:
                return jsonify({'error': 'Dashboard not found'}), 404
            
            data = self._get_dashboard_data(dashboard_id)
            return jsonify(data)
        
        @self.app.route('/api/charts/<chart_id>/data')
        def get_chart_data(chart_id):
            """Get chart-specific data"""
            data = self._get_chart_data(chart_id)
            return jsonify(data)
        
        @self.app.route('/api/metrics/summary')
        def get_metrics_summary():
            """Get metrics summary"""
            summary = self._get_metrics_summary()
            return jsonify(summary)
        
        @self.app.route('/api/alerts')
        def get_alerts():
            """Get recent alerts"""
            alerts = list(self.active_alerts)[-50:]  # Last 50 alerts
            return jsonify({
                'alerts': alerts,
                'total': len(alerts),
                'timestamp': datetime.now().isoformat()
            })
        
        @self.app.route('/api/health')
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'uptime': time.time() - getattr(self, '_start_time', time.time()),
                'active_connections': len(self.active_connections)
            })
    
    def _setup_websocket_handlers(self):
        """Set up WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            self.active_connections.add(request.sid)
            logger.info(f"Client connected: {request.sid}")
            emit('connected', {'status': 'connected', 'timestamp': datetime.now().isoformat()})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            self.active_connections.discard(request.sid)
            logger.info(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('subscribe_dashboard')
        def handle_subscribe_dashboard(data):
            """Handle dashboard subscription"""
            dashboard_id = data.get('dashboard_id')
            if dashboard_id in self.dashboard_configs:
                # Join dashboard room
                self.socketio.server.enter_room(request.sid, f"dashboard_{dashboard_id}")
                
                # Send initial data
                dashboard_data = self._get_dashboard_data(dashboard_id)
                emit('dashboard_data', dashboard_data)
                
                logger.info(f"Client {request.sid} subscribed to {dashboard_id}")
            else:
                emit('error', {'message': 'Dashboard not found'})
        
        @self.socketio.on('unsubscribe_dashboard')
        def handle_unsubscribe_dashboard(data):
            """Handle dashboard unsubscription"""
            dashboard_id = data.get('dashboard_id')
            self.socketio.server.leave_room(request.sid, f"dashboard_{dashboard_id}")
            logger.info(f"Client {request.sid} unsubscribed from {dashboard_id}")
        
        @self.socketio.on('request_chart_data')
        def handle_chart_data_request(data):
            """Handle chart data request"""
            chart_id = data.get('chart_id')
            if chart_id:
                chart_data = self._get_chart_data(chart_id)
                emit('chart_data', chart_data)
    
    async def _handle_market_data_stream(self, data: Dict):
        """Handle market data stream"""
        chart_data = {
            'chart_id': 'price_chart',
            'type': 'line',
            'data': {
                'labels': [data.get('timestamp', datetime.now().isoformat())],
                'datasets': [{
                    'label': 'Price',
                    'data': [data.get('price', 0)],
                    'borderColor': '#3b82f6',
                    'backgroundColor': 'rgba(59, 130, 246, 0.1)'
                }]
            }
        }
        self._broadcast_to_dashboard('market_overview', 'chart_update', chart_data)
    
    async def _handle_system_metrics_stream(self, data: Dict):
        """Handle system metrics stream"""
        # CPU Usage
        cpu_data = {
            'chart_id': 'cpu_usage',
            'type': 'gauge',
            'data': {
                'value': data.get('cpu_usage', 0),
                'max': 100
            }
        }
        self._broadcast_to_dashboard('system_monitoring', 'chart_update', cpu_data)
        
        # Memory Usage
        memory_data = {
            'chart_id': 'memory_usage',
            'type': 'gauge',
            'data': {
                'value': data.get('memory_usage', 0),
                'max': 100
            }
        }
        self._broadcast_to_dashboard('system_monitoring', 'chart_update', memory_data)
    
    async def _handle_user_metrics_stream(self, data: Dict):
        """Handle user metrics stream"""
        active_users_data = {
            'chart_id': 'active_users',
            'type': 'counter',
            'data': {
                'value': data.get('active_users', 0),
                'label': 'Active Users'
            }
        }
        self._broadcast_to_dashboard('user_analytics', 'chart_update', active_users_data)
    
    async def _handle_alerts_stream(self, data: Dict):
        """Handle alerts stream"""
        alert_data = {
            'type': 'new_alert',
            'alert': data
        }
        
        # Add to active alerts
        self.active_alerts.append(data)
        
        # Broadcast to all connected clients
        if self.socketio:
            self.socketio.emit('new_alert', alert_data)
        
        logger.warning(f"New alert: {data.get('message', 'No message')}")
    
    async def _handle_signal_performance_stream(self, data: Dict):
        """Handle signal performance stream"""
        accuracy_data = {
            'chart_id': 'accuracy_chart',
            'type': 'gauge',
            'data': {
                'value': data.get('accuracy', 0) * 100,  # Convert to percentage
                'max': 100
            }
        }
        self._broadcast_to_dashboard('signal_performance', 'chart_update', accuracy_data)
    
    def _broadcast_to_dashboard(self, dashboard_id: str, event: str, data: Any):
        """Broadcast data to specific dashboard subscribers"""
        if self.socketio:
            self.socketio.emit(event, data, room=f"dashboard_{dashboard_id}")
    
    def _get_dashboard_data(self, dashboard_id: str) -> Dict:
        """Get complete dashboard data"""
        if dashboard_id not in self.dashboard_configs:
            return {'error': 'Dashboard not found'}
        
        config = self.dashboard_configs[dashboard_id]
        
        # Collect data for all charts
        charts_data = {}
        for chart_config in config.chart_configs:
            chart_data = self._get_chart_data(chart_config['id'])
            if chart_data:
                charts_data[chart_config['id']] = chart_data
        
        return {
            'dashboard_id': dashboard_id,
            'name': config.name,
            'charts': charts_data,
            'alerts': self._get_dashboard_alerts(dashboard_id),
            'last_update': datetime.now().isoformat()
        }
    
    def _get_chart_data(self, chart_id: str) -> Optional[Dict]:
        """Get data for specific chart"""
        # Check cache first
        if chart_id in self.chart_cache:
            cache_entry = self.chart_cache[chart_id]
            if datetime.now() - cache_entry['timestamp'] < timedelta(seconds=self.config['caching']['cache_ttl']):
                return cache_entry['data']
        
        # Generate chart data based on source
        if self._is_market_chart(chart_id):
            data = self._generate_market_chart_data(chart_id)
        elif self._is_system_chart(chart_id):
            data = self._generate_system_chart_data(chart_id)
        elif self._is_user_chart(chart_id):
            data = self._generate_user_chart_data(chart_id)
        elif self._is_signal_chart(chart_id):
            data = self._generate_signal_chart_data(chart_id)
        else:
            data = self._generate_generic_chart_data(chart_id)
        
        # Cache the result
        self.chart_cache[chart_id] = {
            'data': data,
            'timestamp': datetime.now()
        }
        
        # Limit cache size
        if len(self.chart_cache) > self.config['caching']['max_cache_size']:
            oldest_key = min(self.chart_cache.keys(), 
                           key=lambda k: self.chart_cache[k]['timestamp'])
            del self.chart_cache[oldest_key]
        
        return data
    
    def _is_market_chart(self, chart_id: str) -> bool:
        """Check if chart is market-related"""
        return chart_id in ['price_chart', 'volume_chart', 'volatility_chart', 'sentiment_chart']
    
    def _is_system_chart(self, chart_id: str) -> bool:
        """Check if chart is system-related"""
        return chart_id in ['cpu_usage', 'memory_usage', 'response_time', 'disk_usage']
    
    def _is_user_chart(self, chart_id: str) -> bool:
        """Check if chart is user-related"""
        return chart_id in ['active_users', 'engagement_chart', 'retention_chart', 'new_registrations']
    
    def _is_signal_chart(self, chart_id: str) -> bool:
        """Check if chart is signal-related"""
        return chart_id in ['accuracy_chart', 'return_chart', 'drawdown_chart', 'sharpe_ratio']
    
    def _generate_market_chart_data(self, chart_id: str) -> Dict:
        """Generate market chart data"""
        if not self.analytics_engine or not self.analytics_engine.market_data:
            return {'data': [], 'labels': []}
        
        # Get recent market data
        recent_data = list(self.analytics_engine.market_data)[-20:]
        
        if chart_id == 'price_chart':
            return {
                'type': 'line',
                'data': {
                    'labels': [m.timestamp.isoformat() for m in recent_data],
                    'datasets': [{
                        'label': 'Price',
                        'data': [m.price for m in recent_data],
                        'borderColor': '#3b82f6',
                        'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                        'fill': True
                    }]
                }
            }
        
        elif chart_id == 'volume_chart':
            return {
                'type': 'bar',
                'data': {
                    'labels': [m.timestamp.isoformat() for m in recent_data],
                    'datasets': [{
                        'label': 'Volume',
                        'data': [m.volume for m in recent_data],
                        'backgroundColor': '#10b981'
                    }]
                }
            }
        
        elif chart_id == 'volatility_chart':
            return {
                'type': 'line',
                'data': {
                    'labels': [m.timestamp.isoformat() for m in recent_data],
                    'datasets': [{
                        'label': 'Volatility',
                        'data': [m.volatility for m in recent_data],
                        'borderColor': '#f59e0b',
                        'backgroundColor': 'rgba(245, 158, 11, 0.1)'
                    }]
                }
            }
        
        return {}
    
    def _generate_system_chart_data(self, chart_id: str) -> Dict:
        """Generate system chart data"""
        if not self.metrics_collector:
            return {}
        
        if chart_id in ['cpu_usage', 'memory_usage']:
            metric_name = f'system.{chart_id.replace("_", ".")}'
            current_value = self.metrics_collector.get_metric_value(metric_name, 'last')
            
            return {
                'type': 'gauge',
                'data': {
                    'value': current_value or 0,
                    'max': 100,
                    'color': self._get_gauge_color(current_value or 0)
                }
            }
        
        elif chart_id == 'response_time':
            # Get recent response times
            history = self.metrics_collector.get_metric_history('api.response_time', 20)
            if history:
                return {
                    'type': 'line',
                    'data': {
                        'labels': [h['timestamp'].isoformat() for h in history],
                        'datasets': [{
                            'label': 'Response Time (ms)',
                            'data': [h.get('avg_value', 0) for h in history],
                            'borderColor': '#8b5cf6'
                        }]
                    }
                }
        
        return {}
    
    def _generate_user_chart_data(self, chart_id: str) -> Dict:
        """Generate user chart data"""
        if not self.analytics_engine:
            return {}
        
        if chart_id == 'active_users':
            active_count = len([u for u in self.analytics_engine.user_data.values() 
                              if u.get('last_activity') and 
                              datetime.now() - u['last_activity'] < timedelta(hours=24)])
            
            return {
                'type': 'counter',
                'data': {
                    'value': active_count,
                    'label': 'Active Users (24h)',
                    'color': '#3b82f6'
                }
            }
        
        elif chart_id == 'engagement_chart':
            # Generate engagement data
            engagement_data = {
                'labels': ['Login', 'Trading', 'Portfolio', 'Settings'],
                'datasets': [{
                    'data': [85, 70, 45, 30],  # Sample engagement percentages
                    'backgroundColor': ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
                }]
            }
            
            return {
                'type': 'pie',
                'data': engagement_data
            }
        
        return {}
    
    def _generate_signal_chart_data(self, chart_id: str) -> Dict:
        """Generate signal performance chart data"""
        if not self.analytics_engine:
            return {}
        
        if chart_id == 'accuracy_chart':
            # Get average signal accuracy
            total_accuracy = 0
            signal_count = 0
            
            for signal_data in self.analytics_engine.signal_data.values():
                if signal_data.get('outcomes'):
                    accuracies = [o['outcome'].get('accuracy', 0) for o in signal_data['outcomes']]
                    if accuracies:
                        total_accuracy += np.mean(accuracies)
                        signal_count += 1
            
            avg_accuracy = (total_accuracy / signal_count * 100) if signal_count > 0 else 0
            
            return {
                'type': 'gauge',
                'data': {
                    'value': avg_accuracy,
                    'max': 100,
                    'color': self._get_gauge_color(avg_accuracy)
                }
            }
        
        return {}
    
    def _generate_generic_chart_data(self, chart_id: str) -> Dict:
        """Generate generic chart data"""
        # Default data for unknown chart types
        return {
            'type': 'line',
            'data': {
                'labels': ['Sample 1', 'Sample 2', 'Sample 3'],
                'datasets': [{
                    'label': 'Data',
                    'data': [10, 20, 15],
                    'borderColor': '#6b7280'
                }]
            }
        }
    
    def _get_gauge_color(self, value: float) -> str:
        """Get color for gauge based on value"""
        if value < 50:
            return '#10b981'  # Green
        elif value < 80:
            return '#f59e0b'  # Yellow
        else:
            return '#ef4444'  # Red
    
    def _get_dashboard_alerts(self, dashboard_id: str) -> List[Dict]:
        """Get alerts for specific dashboard"""
        # Filter alerts by dashboard type
        dashboard_alerts = []
        for alert in list(self.active_alerts)[-10:]:  # Last 10 alerts
            if self._alert_belongs_to_dashboard(alert, dashboard_id):
                dashboard_alerts.append(alert)
        
        return dashboard_alerts
    
    def _alert_belongs_to_dashboard(self, alert: Dict, dashboard_id: str) -> bool:
        """Check if alert belongs to dashboard"""
        if dashboard_id == 'market_overview' and 'market' in alert.get('type', ''):
            return True
        elif dashboard_id == 'system_monitoring' and 'system' in alert.get('type', ''):
            return True
        elif dashboard_id == 'user_analytics' and 'user' in alert.get('type', ''):
            return True
        elif dashboard_id == 'signal_performance' and 'signal' in alert.get('type', ''):
            return True
        
        return False
    
    def _get_metrics_summary(self) -> Dict:
        """Get metrics summary for API"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'dashboards': {
                'total': len(self.dashboard_configs),
                'active': len([d for d in self.dashboard_configs.values() if d.auto_refresh])
            },
            'connections': {
                'active': len(self.active_connections),
                'total': self.update_stats['total_updates']
            },
            'performance': self.update_stats.copy(),
            'alerts': {
                'active': len(self.active_alerts),
                'recent': len([a for a in self.active_alerts if 
                              datetime.now() - a['timestamp'] < timedelta(hours=1)])
            }
        }
        
        # Add data source information
        if self.analytics_engine:
            summary['data_sources'] = {
                'analytics_engine': 'connected',
                'market_data_points': len(self.analytics_engine.market_data),
                'user_data_points': len(self.analytics_engine.user_data),
                'signal_data_points': sum(len(s.get('outcomes', [])) for s in self.analytics_engine.signal_data.values())
            }
        
        if self.metrics_collector:
            summary['metrics_collector'] = {
                'status': 'connected',
                'total_metrics': len(self.metrics_collector.aggregated_metrics)
            }
        
        return summary
    
    def get_dashboard_html(self, dashboard_id: str) -> str:
        """Generate HTML for dashboard"""
        if dashboard_id not in self.dashboard_configs:
            return "<h1>Dashboard not found</h1>"
        
        config = self.dashboard_configs[dashboard_id]
        
        # Generate HTML with Chart.js
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{config.name}</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .dashboard-header {{ text-align: center; margin-bottom: 30px; }}
                .chart-container {{ 
                    width: 100%; 
                    max-width: 800px; 
                    margin: 20px auto; 
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                }}
                .alerts {{ 
                    position: fixed; 
                    top: 20px; 
                    right: 20px; 
                    max-width: 300px;
                    z-index: 1000;
                }}
                .alert {{ 
                    background: #fef2f2; 
                    border: 1px solid #fecaca; 
                    color: #991b1b;
                    padding: 10px; 
                    margin-bottom: 10px; 
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="dashboard-header">
                <h1>{config.name}</h1>
                <p>Real-time Analytics Dashboard</p>
            </div>
        """
        
        # Add chart containers
        for chart_config in config.chart_configs:
            html += f"""
            <div class="chart-container">
                <h3>{chart_config['title']}</h3>
                <canvas id="{chart_config['id']}"></canvas>
            </div>
            """
        
        html += """
            <div class="alerts" id="alerts"></div>
            
            <script>
                // WebSocket connection
                const socket = io();
                
                // Chart instances
                const charts = {};
        """
        
        # Add chart initialization
        for chart_config in config.chart_configs:
            chart_id = chart_config['id']
            chart_type = chart_config.get('type', 'line')
            
            html += f"""
                // Initialize {chart_id}
                const ctx_{chart_id} = document.getElementById('{chart_id}').getContext('2d');
                charts['{chart_id}'] = new Chart(ctx_{chart_id}, {{
                    type: '{chart_type}',
                    data: {{ labels: [], datasets: [] }},
                    options: {{
                        responsive: true,
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            """
        
        html += """
                // WebSocket event handlers
                socket.on('connect', function() {
                    console.log('Connected to dashboard');
                    // Subscribe to dashboard
                    socket.emit('subscribe_dashboard', {
                        dashboard_id: '""" + dashboard_id + """'
                    });
                });
                
                socket.on('dashboard_data', function(data) {
                    console.log('Dashboard data received');
                    updateDashboard(data);
                });
                
                socket.on('chart_update', function(data) {
                    updateChart(data);
                });
                
                socket.on('new_alert', function(data) {
                    showAlert(data.alert);
                });
                
                function updateDashboard(data) {
                    // Update all charts with new data
                    Object.keys(data.charts || {}).forEach(chartId => {
                        updateChart(data.charts[chartId]);
                    });
                }
                
                function updateChart(chartData) {
                    const chartId = chartData.chart_id;
                    if (charts[chartId] && chartData.data) {
                        charts[chartId].data = chartData.data;
                        charts[chartId].update('none');
                    }
                }
                
                function showAlert(alert) {
                    const alertsContainer = document.getElementById('alerts');
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert';
                    alertDiv.innerHTML = `
                        <strong>${alert.severity || 'INFO'}</strong><br>
                        ${alert.message || alert.type}
                    `;
                    alertsContainer.appendChild(alertDiv);
                    
                    // Auto-remove after 5 seconds
                    setTimeout(() => {
                        if (alertDiv.parentNode) {
                            alertDiv.parentNode.removeChild(alertDiv);
                        }
                    }, 5000);
                }
            </script>
        </body>
        </html>
        """
        
        return html
    
    def export_dashboard_config(self, dashboard_id: str, format_type: str = 'json') -> str:
        """Export dashboard configuration"""
        if dashboard_id not in self.dashboard_configs:
            return json.dumps({'error': 'Dashboard not found'})
        
        config = self.dashboard_configs[dashboard_id]
        config_data = asdict(config)
        
        if format_type.lower() == 'json':
            return json.dumps(config_data, indent=2, default=str)
        else:
            return str(config_data)
    
    def import_dashboard_config(self, config_data: str, format_type: str = 'json') -> str:
        """Import dashboard configuration"""
        try:
            if format_type.lower() == 'json':
                config_dict = json.loads(config_data)
            else:
                # Assume it's a dict representation
                config_dict = config_data
            
            # Create dashboard config
            config = DashboardConfig(**config_dict)
            dashboard_id = self.create_dashboard(config)
            
            return json.dumps({
                'success': True,
                'dashboard_id': dashboard_id,
                'message': 'Dashboard imported successfully'
            })
        
        except Exception as e:
            return json.dumps({
                'success': False,
                'error': str(e)
            })
    
    def get_performance_stats(self) -> Dict:
        """Get dashboard performance statistics"""
        return {
            'update_stats': self.update_stats,
            'active_connections': len(self.active_connections),
            'cached_charts': len(self.chart_cache),
            'active_alerts': len(self.active_alerts),
            'dashboard_count': len(self.dashboard_configs),
            'server_running': self.is_server_running
        }


# Utility functions
def create_dashboard_integration(config: Optional[Dict] = None) -> DashboardIntegration:
    """Factory function to create dashboard integration"""
    return DashboardIntegration(config)


async def run_dashboard_demo():
    """Dashboard integration demonstration"""
    print("Dashboard Integration Demo boshlanmoqda...")
    
    # Create components
    from analytics_engine import create_analytics_engine
    from metrics_collector import create_metrics_collector
    
    analytics = create_analytics_engine()
    metrics = create_metrics_collector()
    dashboard = create_dashboard_integration()
    
    # Initialize
    dashboard.initialize(analytics, metrics)
    
    # Start components
    dashboard.metrics_collector.start_collection()
    dashboard.analytics_engine.start_analytics()
    
    try:
        # Add sample data
        import random
        from datetime import datetime
        
        # Market data
        market_data = {
            'symbol': 'EURUSD',
            'price': 1.1000 + random.uniform(-0.01, 0.01),
            'volume': random.uniform(1000, 5000),
            'volatility': random.uniform(0.001, 0.02)
        }
        dashboard.analytics_engine.add_market_data(market_data)
        
        # User data
        dashboard.analytics_engine.add_user_data('demo_user', {
            'action': 'login',
            'timestamp': datetime.now()
        })
        
        # System metrics
        dashboard.metrics_collector.collect_metric('system.cpu.usage', random.uniform(20, 80))
        
        # Wait a moment for data processing
        await asyncio.sleep(2)
        
        # Test dashboard functions
        print("\n=== DASHBOARD SUMMARY ===")
        summary = dashboard.get_performance_stats()
        print(f"Active connections: {summary['active_connections']}")
        print(f"Cached charts: {summary['cached_charts']}")
        print(f"Active alerts: {summary['active_alerts']}")
        print(f"Dashboard count: {summary['dashboard_count']}")
        
        # Test data export
        print("\n=== EXPORT TEST ===")
        market_config = dashboard.export_dashboard_config('market_overview')
        print(f"Market dashboard config length: {len(market_config)} chars")
        
        # Get sample chart data
        print("\n=== CHART DATA TEST ===")
        price_chart = dashboard._get_chart_data('price_chart')
        if price_chart:
            print(f"Price chart type: {price_chart.get('type')}")
            print(f"Chart data keys: {list(price_chart.keys())}")
        
        print("\nDemo tugallandi!")
        print("Web dashboard serverni ishga tushirish uchun: dashboard.start_web_server()")
        
    finally:
        # Clean up
        dashboard.analytics_engine.stop_analytics()
        dashboard.metrics_collector.stop_collection()


if __name__ == "__main__":
    # Run demo
    asyncio.run(run_dashboard_demo())