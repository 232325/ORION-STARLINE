# Performance Monitoring va System Integration

## 🚀 Loyiha haqida

Bu repository **Performance Monitoring** va **System Integration** yechimini o'z ichiga oladi. Trading tizimlari va murakkab ilovalar uchun to'liq monitoring stack tizimi.

## ✨ Asosiy xususiyatlar

### 📊 Performance Monitoring
- ✅ Request/Response time tracking
- ✅ Database query performance monitoring
- ✅ Memory usage monitoring
- ✅ CPU utilization tracking
- ✅ Error rate monitoring

### 📈 Metrics Collection
- ✅ Prometheus integration
- ✅ Custom business va technical metrics
- ✅ Alert configuration
- ✅ Dashboard provisioning
- ✅ Real-time metric collection

### 📝 Logging System
- ✅ Structured logging (JSON format)
- ✅ ELK Stack integration (Elasticsearch, Logstash, Kibana)
- ✅ Centralized log aggregation
- ✅ Log retention policies
- ✅ Log parsing va filtering

### 🔍 Observability
- ✅ Distributed tracing (Jaeger, Zipkin)
- ✅ Health checks
- ✅ Service mesh integration
- ✅ Performance profiling
- ✅ Capacity planning

### 🧪 Integration Testing
- ✅ API integration tests
- ✅ End-to-end testing
- ✅ Performance testing
- ✅ Load testing
- ✅ Chaos engineering

## 🏗️ Arxitektura

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Trading Apps      │    │   Microservices     │    │   Frontend Apps     │
└──────────┬──────────┘    └──────────┬──────────┘    └──────────┬──────────┘
           │                        │                        │
           └────────────────────────┼────────────────────────┘
                                    │
           ┌────────────────────────▼────────────────────────┐
           │            Load Balancer (Nginx)                │
           └────────────────────────┬────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    │                                                       │
    ▼                                                       ▼
┌─────────┐                                           ┌─────────┐
│Metrics  │                                           │  Logs   │
│Storage  │                                           │ Storage │
│(Prometheus│                                           │(ELK Stack│
│ Grafana) │                                           │ Kibana) │
└─────────┘                                           └─────────┘
                                    │
                                   ▼
                       ┌─────────────────────┐
                       │  Alerting System    │
                       │ (Slack, Email, Web) │
                       └─────────────────────┘
```

## 📁 Loyiha struktura

```
code/monitoring/
├── 📂 core/                          # Asosiy monitoring tizimi
│   └── performance_monitor.py        # Core monitoring engine
├── 📂 prometheus/                    # Metrics collection
│   ├── prometheus.yml                # Main config
│   ├── alert_rules.yml               # Alert definitions
│   ├── recording_rules.yml           # Pre-computed metrics
│   └── custom_metrics.py             # Business metrics
├── 📂 grafana/                       # Visualization
│   └── provisioning/                 # Dashboard configs
├── 📂 elk_stack/                     # Log management
│   ├── elasticsearch/                # Log storage
│   ├── logstash/                     # Log processing
│   ├── kibana/                       # Log visualization
│   └── structured_logging.py         # Structured logging
├── 📂 observability/                 # Tracing
│   └── distributed_tracing.py        # Distributed tracing
├── 📂 testing/                       # Integration tests
│   └── integration_testing.py        # Test suite
├── 📂 docker_compose/                # Deployment
│   └── docker-compose.yml            # Full stack
├── 📂 configs/                       # Configuration files
│   ├── nginx/                        # Load balancer
│   ├── alertmanager/                 # Alert management
│   └── database/                     # Database setup
└── 📂 scripts/                       # Management tools
    └── monitorctl.sh                 # Control script
```

## 🚀 Tez ishga tushish

### 1. Barcha komponentlarni o'rnatish
```bash
# Repository ni clone qilish
git clone <repository-url>
cd code/monitoring

# Execution permission berish
chmod +x scripts/monitorctl.sh

# Barcha konfiguratsiyalarni yaratish
./scripts/monitorctl.sh setup
```

### 2. Monitoring stack ni ishga tushirish
```bash
# Full stack ni deploy qilish
./scripts/monitorctl.sh deploy

# Xizmatlar tayyor bo'lishini kutish
sleep 60
```

### 3. Test qilish
```bash
# Integration testlarni ishga tushirish
./scripts/monitorctl.sh test
```

### 4. Dashboard larni ochish
```bash
# URL larni ko'rsatish
./scripts/monitorctl.sh urls
```

## 🌐 Monitoring Dashboard lar

| Xizmat | URL | Login |
|--------|-----|-------|
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin/admin123 |
| **Kibana** | http://localhost:5601 | - |
| **Jaeger** | http://localhost:16686 | - |
| **Elasticsearch** | http://localhost:9200 | - |
| **Trading App** | http://localhost:8000 | - |
| **Nginx Proxy** | https://localhost | - |

## 🔧 API Endpoints

### Trading Application APIs
```bash
# Health check
GET /api/health

# Market data olish
GET /api/market/{symbol}

# Trade yaratish
POST /api/trades
{
  "symbol": "EURUSD",
  "side": "BUY",
  "quantity": 1000
}

# Portfolio olish
GET /api/portfolio

# Metriklarni ko'rish
GET /metrics
```

### Monitoring APIs
```bash
# Prometheus query
GET /api/v1/query?query=up

# Jaeger tracing
GET /api/services

# Elasticsearch cluster health
GET /cluster/health

# Logstash pipeline stats
GET /_node/stats/pipelines
```

## 📊 Dashboards

### 1. Application Performance Dashboard
- Response time trends
- Error rate monitoring
- Throughput metrics
- User activity analytics

### 2. Infrastructure Monitoring
- CPU, Memory, Disk usage
- Network I/O metrics
- Service health status
- Resource utilization

### 3. Business Metrics
- Trading volume analysis
- P&L tracking
- User session metrics
- Risk assessment dashboard

### 4. Log Analysis
- Error log patterns
- Application flow tracking
- Performance bottleneck identification
- Security event monitoring

### 5. Distributed Tracing
- Request flow visualization
- Service dependency mapping
- Performance bottleneck identification
- Error propagation tracking

## 📈 Metrics va Alerts

### Performance Metrics
- **Response Time**: P50, P95, P99
- **Throughput**: Requests per second
- **Error Rate**: 4xx, 5xx error percentages
- **Availability**: Uptime percentage

### Business Metrics
- **Trading Volume**: Daily/hourly volume
- **User Sessions**: Active user count
- **P&L**: Profit/Loss tracking
- **Risk Score**: Risk assessment

### System Metrics
- **CPU Usage**: Per service breakdown
- **Memory Usage**: Heap vs non-heap
- **Disk I/O**: Read/write operations
- **Network**: Bandwidth utilization

### Alert Rules
- 🚨 High CPU Usage (>80%)
- 🚨 High Memory Usage (>85%)
- 🚨 Response Time P95 (>500ms)
- 🚨 Error Rate (>5%)
- 🚨 Service Down

## 🧪 Testing Framework

### API Integration Tests
```python
# Namuna test
api_test = APITest(
    name="trade_creation",
    method="POST",
    url="/api/trades",
    expected_status=201,
    expected_response_time_ms=1000
)
```

### Load Testing
```python
# Load test konfiguratsiya
load_test = LoadTest(
    name="api_health_load",
    endpoint="/api/health",
    concurrent_users=50,
    duration_seconds=300
)
```

### Chaos Engineering
```python
# Chaos test
chaos_test = ChaosTest(
    name="latency_injection",
    test_type="latency",
    target_service="trading_api",
    intensity=0.5,
    duration_seconds=60
)
```

## 🔍 Logging Examples

### Structured Logging
```python
from structured_logging import create_logging_system

# Logger yaratish
logging_system = create_logging_system("trading_engine")
logger = logging_system.get_logger("database")

# Context bilan logging
with logger.with_context(trace_id="12345", user_id="user123"):
    logger.info("Trade executed", 
                amount=1000.00, 
                currency="USD",
                trade_id="T12345")
```

### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General information about operations
- **WARNING**: Warning conditions
- **ERROR**: Error conditions
- **CRITICAL**: Critical conditions

## 🔗 Tracing Examples

### Function Tracing
```python
from distributed_tracing import trace_function

@trace_function(tracer, "trade_calculation", SpanType.FUNCTION)
def calculate_pnl(trades):
    # Calculation logic
    return pnl
```

### HTTP Request Tracing
```python
@trace_http_request(tracer, "POST", "/api/trades")
def create_trade():
    # API logic
    return response
```

### Database Tracing
```python
@trace_database_query(tracer, "INSERT", "trades")
def insert_trade(trade_data):
    # Database logic
    return result
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Service not starting
```bash
# Log larni ko'rish
docker-compose logs prometheus
docker-compose logs grafana

# Xizmatlarni restart qilish
docker-compose restart [service_name]
```

#### 2. Metrics not collecting
```bash
# Prometheus target larni tekshirish
curl http://localhost:9090/api/v1/targets

# Application metrics
curl http://localhost:8000/metrics
```

#### 3. Logs not appearing
```bash
# Elasticsearch health
curl http://localhost:9200/_cluster/health

# Logstash pipeline
curl http://localhost:9600/_node/stats/pipelines
```

#### 4. Tracing not working
```bash
# Jaeger services
curl http://localhost:16686/api/services

# Application tracer health
curl http://localhost:8000/api/health
```

## 🔒 Security Features

- **Authentication**: Grafana va protected endpoints
- **Authorization**: Role-based access control
- **Encryption**: TLS/SSL for all communications
- **Network Security**: Firewall rules va network isolation
- **Audit Logging**: Security event logging
- **Secret Management**: Environment variables

## 📚 Additional Resources

- [Complete Monitoring Guide](docs/PERFORMANCE_MONITORING_GUIDE.md)
- [Prometheus Configuration](prometheus/prometheus.yml)
- [Grafana Dashboards](grafana/dashboards/)
- [Log Processing Pipeline](elk_stack/logstash/pipeline/)
- [API Testing Suite](testing/integration_testing.py)

## 🤝 Contributing

Bu loyihaga hissa qo'shish uchun:

1. Fork repository
2. Feature branch yarating (`git checkout -b feature/amazing-feature`)
3. O'zgarishlaringizni commit qiling (`git commit -m 'Add amazing feature'`)
4. Branch ni push qiling (`git push origin feature/amazing-feature`)
5. Pull Request oching

## 📄 License

Bu loyiha MIT License ostida tarqatiladi.

## 📞 Support

Agar savollaringiz bo'lsa yoki yordam kerak bo'lsa:

- Issues yarating: GitHub Issues
- Documentation: [Complete Guide](docs/PERFORMANCE_MONITORING_GUIDE.md)
- Examples: Code samples in each directory

---

**Made with ❤️ for Trading Systems Monitoring**

*Bu tizim modern distributed applications uchun enterprise-level monitoring ta'minlaydi.*