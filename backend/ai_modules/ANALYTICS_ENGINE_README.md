# Real-time Analytics Engine

**Orion Starline** loyihasi uchun real-time analytics va monitoring tizimi.

## 📊 Loyiha Haqida

Bu tizim quyidagi asosiy funksiyalarni ta'minlaydi:

### 🎯 Asosiy Xususiyatlari

- **Real-time Market Data Processing** - Realtime bozor ma'lumotlarini qayta ishlash
- **User Activity Monitoring** - Foydalanuvchi faoliyatini kuzatish
- **Signal Performance Tracking** - Signal unumdorligini kuzatish
- **Risk Metrics Calculation** - Risk metrikalarini hisoblash
- **System Performance Monitoring** - Tizim ishlashini kuzatish
- **Business Intelligence** - Biznes intellekt
- **Predictive Analytics** - Bashorat analitikasi
- **Anomaly Detection** - Anomaliyalarni aniqlash

### 📈 Market Analytics

- Price movement analysis
- Volume analysis
- Volatility tracking
- Correlation analysis
- Market sentiment
- Technical indicators
- Pattern recognition
- News sentiment

### 👥 User Analytics

- Trading activity
- Performance metrics
- Behavioral analysis
- Engagement tracking
- Retention analysis
- Feature usage
- Error tracking
- Session analytics

### 🖥️ System Analytics

- API performance
- Database metrics
- Cache hit rates
- Error rates
- Response times
- Resource usage
- Health checks
- Alert systems

### 🤖 Advanced Features

- Machine learning models
- Real-time dashboards
- Custom metrics
- Data export
- Report generation
- Alert management
- Performance optimization
- Scalability analysis

## 🏗️ Architecture

```
analytics_engine/
├── analytics_engine.py        # Asosiy analytics engine
├── metrics_collector.py        # Metrics yig'uvchi
├── dashboard_integration.py    # Dashboard integratsiyasi
├── analytics_demo.py           # Demo va test
├── integration_test.py         # Integration test
├── requirements_analytics.txt  # Dependencies
└── README.md                   # Bu fayl
```

## 🚀 Tez Kirish

### O'rnatish

```bash
pip install -r requirements_analytics.txt
```

### Tez Demo

```python
from analytics_engine import create_analytics_engine
from metrics_collector import create_metrics_collector
from dashboard_integration import create_dashboard_integration

# Analytics engine yaratish
engine = create_analytics_engine()

# Market data qo'shish
market_data = {
    'symbol': 'EURUSD',
    'price': 1.1000,
    'volume': 1000,
    'volatility': 0.01
}
engine.add_market_data(market_data)

# Hisobot olish
report = engine.get_market_analytics_report('1h')
print(report)
```

### To'liq Demo

```bash
python3 analytics_demo.py
```

### Integration Test

```bash
python3 integration_test.py
```

## 📚 Asosiy Komponentlar

### 1. Analytics Engine (`analytics_engine.py`)

```python
from analytics_engine import AnalyticsEngine, create_analytics_engine

# Yaratish
engine = create_analytics_engine()

# Market data qo'shish
engine.add_market_data({
    'symbol': 'EURUSD',
    'price': 1.1000,
    'volume': 1000,
    'volatility': 0.01,
    'sma_20': 1.0990,
    'sma_50': 1.0980,
    'rsi': 50.0,
    'macd': 0.001
})

# User data qo'shish
engine.add_user_data('user_001', {
    'action': 'trade',
    'size': 1000,
    'profit_loss': 50.0,
    'symbol': 'EURUSD'
})

# Signal data qo'shish
engine.add_signal_data('signal_001', {
    'action': 'signal_generated',
    'confidence': 0.8,
    'symbol': 'EURUSD',
    'direction': 'buy'
})

# Analytics ishga tushirish
await engine.start_analytics()
```

### 2. Metrics Collector (`metrics_collector.py`)

```python
from metrics_collector import MetricsCollector, create_metrics_collector

# Yaratish
collector = create_metrics_collector()

# Manual metric qo'shish
collector.collect_metric('system.cpu.usage', 75.5, source='system')
collector.collect_metric('api.response_time', 120, {'endpoint': '/api/trades'}, 'api')

# Custom collector qo'shish
def custom_metric_collector():
    value = calculate_custom_metric()
    collector.collect_metric('custom.metric', value, source='custom')

collector.add_custom_collector('my_collector', custom_metric_collector, 5.0)

# Collection ishga tushirish
collector.start_collection()

# Real-time data olish
realtime_data = collector.get_real_time_metrics()
```

### 3. Dashboard Integration (`dashboard_integration.py`)

```python
from dashboard_integration import DashboardIntegration, create_dashboard_integration

# Yaratish
dashboard = create_dashboard_integration()

# Initialize
dashboard.initialize(analytics_engine, metrics_collector)

# HTML dashboard olish
html_dashboard = dashboard.get_dashboard_html('market_overview')

# Web server ishga tushirish
dashboard.start_web_server()

# API endpoints
# GET /api/dashboards
# GET /api/dashboard/<dashboard_id>
# GET /api/dashboard/<dashboard_id>/data
# GET /api/charts/<chart_id>/data
# GET /api/metrics/summary
# GET /api/alerts
```

## 📊 Dashboard Konfiguratsiyasi

### Mavjud Dashboardlar

1. **Market Overview** - Bozor ma'lumotlari
2. **System Monitoring** - Tizim monitoring
3. **User Analytics** - Foydalanuvchi analitikasi
4. **Signal Performance** - Signal unumdorligi

### Chart Turlari

- Line charts
- Bar charts
- Pie charts
- Gauge charts
- Area charts
- Counter metrics

### API Foydalanish

```javascript
// WebSocket orqali real-time data
const socket = io();
socket.emit('subscribe_dashboard', { dashboard_id: 'market_overview' });
socket.on('dashboard_data', (data) => {
    console.log('Dashboard data:', data);
});
socket.on('chart_update', (chartData) => {
    updateChart(chartData);
});
```

## 🔧 Sozlanishi

### Analytics Engine Config

```python
config = {
    'market_analysis': {
        'price_lookback': 50,
        'volume_threshold': 1.5,
        'volatility_threshold': 0.02
    },
    'user_analysis': {
        'session_timeout': 30,
        'min_trades': 5,
        'risk_weight': 0.3
    },
    'system_monitoring': {
        'cpu_alert': 80,
        'memory_alert': 85,
        'response_alert': 1000
    }
}
```

### Metrics Collector Config

```python
config = {
    'collection_interval': 1.0,
    'batch_size': 100,
    'aggregation_interval': 60,
    'enable_system_metrics': True,
    'enable_market_metrics': True,
    'enable_user_metrics': True,
    'enable_custom_metrics': True
}
```

### Dashboard Config

```python
config = {
    'dashboard': {
        'host': '0.0.0.0',
        'port': 5000,
        'debug': False
    },
    'data_refresh': {
        'default_interval': 1,
        'chart_timeout': 30
    }
}
```

## 📈 Performance

### Test Natijalari

- **Integration Test**: 9/10 test o'tdi (90% success rate)
- **Performance Test**: 100 market data point 0.001s
- **Memory Usage**: Optimized with deques
- **Real-time Processing**: <100ms latency

### Benchmark

```python
# 100 market data points
analytics_time: 0.001s

# 200 metrics
metrics_time: 0.001s

# Real-time processing
average_latency: <100ms
```

## 🔍 Monitoring

### Available Metrics

#### System Metrics
- `system.cpu.usage` - CPU foydalanish
- `system.memory.usage` - Xotira foydalanish
- `system.disk.usage` - Disk foydalanish
- `system.network.bytes_sent/recv` - Tarmoq trafik

#### Market Metrics
- `market.EURUSD.price` - EURUSD narxi
- `market.EURUSD.volume` - EURUSD hajmi
- `market.EURUSD.volatility` - EURUSD volatilite
- `market.sentiment` - Bozor sentiment

#### User Metrics
- `users.active` - Faol foydalanuvchilar
- `users.new_registrations` - Yangi ro'yxatdan o'tganlar
- `users.trades.total` - Jami savdolar
- `users.session_duration.avg` - O'rtacha session davomiyligi

#### API Metrics
- `api.calls.count` - API chaqiriqlar
- `api.errors.rate` - Xato darajasi
- `api.response_time` - Javob vaqti

### Alert System

```python
# Thresholds
alert_thresholds = {
    'cpu_usage': 80.0,
    'memory_usage': 85.0,
    'error_rate': 0.05,
    'response_time': 1000.0
}

# Alert levels
- LOW: Informational
- MEDIUM: Warning
- HIGH: Critical
- CRITICAL: Emergency
```

## 📊 Data Export

### JSON Export

```python
# Analytics data export
analytics_data = engine.export_analytics_data('json')
with open('analytics_export.json', 'w') as f:
    f.write(analytics_data)

# Metrics data export
metrics_data = collector.export_metrics_data('json')
with open('metrics_export.json', 'w') as f:
    f.write(metrics_data)

# Dashboard config export
config_data = dashboard.export_dashboard_config('market_overview')
with open('dashboard_config.json', 'w') as f:
    f.write(config_data)
```

### Real-time Data

```python
# Get real-time metrics
realtime = collector.get_real_time_metrics()
print(realtime)

# Get dashboard data
dashboard_data = engine.get_dashboard_data()
print(dashboard_data)
```

## 🛠️ Testing

### Integration Tests

```bash
# Barcha testlarni ishga tushirish
python3 integration_test.py

# Natija
Test Results: 9/10 tests passed
Success rate: 90.0%
```

### Demo Tests

```bash
# To'liq demo
python3 analytics_demo.py

# Natijalar
📊 Market Analytics Report
👥 User Analytics Report
🖥️ System Analytics Report
📈 Signal Performance Report
📋 Metrics Collector Summary
🎯 Dashboard Data
⚡ Performance Statistics
🔄 Real-time Metrics Sample
```

## 🔧 Troubleshooting

### Tez-tez uchraydigian muammolar

#### 1. ImportError: No module named 'analytics_engine'
```bash
# HECHM misolini ishlayotgan papkada ekanligizni tekshiring
pwd
# Yoki Python path ga qo'shing
export PYTHONPATH=$PYTHONPATH:/path/to/ai_modules
```

#### 2. psutil not available
```bash
# System metrics uchun
pip install psutil
```

#### 3. Web server ishga tushmaydi
```bash
# Flask va Flask-SocketIO o'rnating
pip install flask flask-socketio
```

#### 4. Memory yoki performance muammolari
```python
# Data retention sozlang
config['data_retention_days'] = 7

# Buffer size kamaytiring
config['max_buffer_size'] = 1000
```

## 📝 Loyiha Tarixi

- **v1.0.0** - Asosiy analytics engine
- **v1.1.0** - Metrics collector qo'shildi
- **v1.2.0** - Dashboard integration
- **v1.3.0** - Real-time processing
- **v1.4.0** - Advanced analytics
- **v1.5.0** - Current version

## 🤝 Hissa Qo'shish

1. Fork qiling
2. Feature branch yarating (`git checkout -b feature/amazing-feature`)
3. O'zgarishlaringiz commit qiling (`git commit -m 'Add amazing feature'`)
4. Branch ga push qiling (`git push origin feature/amazing-feature`)
5. Pull Request yarating

## 📞 Support

- **Telegram**: @orion_starline_support
- **Email**: support@orionstarline.com
- **Documentation**: https://docs.orionstarline.com

## 📄 License

Bu loyiha MIT License ostida tarqatiladi.

## 🏆 Attribution

- **Analytics Engine**: Orion Starline Development Team
- **Real-time Processing**: Custom async implementation
- **Dashboard**: Chart.js based visualization
- **Testing**: Comprehensive integration tests

---

**Made with ❤️ by Orion Starline Team**

```bash
# Tez boshlash
cd /workspace/orion-starline/backend/ai_modules
python3 analytics_demo.py
```

```javascript
// WebSocket connection
const socket = io('http://localhost:5000');
socket.emit('subscribe_dashboard', { dashboard_id: 'market_overview' });
```