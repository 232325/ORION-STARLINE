#!/bin/bash
# Monitoring Stack Management Script
# Performance Monitoring va System Integration tizimini boshqarish

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
MONITORING_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log_success "Docker va Docker Compose topildi"
}

# Create necessary directories
setup_directories() {
    log_info "Papkalar yaratilmoqda..."
    
    # Create directory structure
    mkdir -p logs prometheus_data grafana_data elasticsearch_data
    mkdir -p configs/nginx configs/alertmanager configs/database
    mkdir -p custom_metrics exporter application
    
    # Set proper permissions
    chmod -R 755 logs prometheus_data grafana_data elasticsearch_data
    
    log_success "Papkalar tayyor"
}

# Generate self-signed SSL certificates
generate_ssl_certificates() {
    log_info "SSL sertifikatlari yaratilmoqda..."
    
    mkdir -p configs/nginx/ssl
    
    # Generate private key
    openssl genrsa -out configs/nginx/ssl/private.key 2048
    
    # Generate certificate signing request
    openssl req -new -key configs/nginx/ssl/private.key -out configs/nginx/ssl/cert.csr \
        -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=localhost"
    
    # Generate self-signed certificate
    openssl x509 -req -in configs/nginx/ssl/cert.csr -signkey configs/nginx/ssl/private.key \
        -out configs/nginx/ssl/certificate.crt -days 365
    
    # Remove CSR file
    rm configs/nginx/ssl/cert.csr
    
    # Create combined certificate
    cat configs/nginx/ssl/certificate.crt configs/nginx/ssl/private.key > configs/nginx/ssl/fullchain.pem
    
    log_success "SSL sertifikatlari yaratildi"
}

# Initialize database
init_database() {
    log_info "Ma'lumotlar bazasi tayyorlanmoqda..."
    
    cat > configs/database/init.sql << 'EOF'
-- Initialize monitoring database
CREATE DATABASE IF NOT EXISTS monitoring;
CREATE DATABASE IF NOT EXISTS trading;

-- Grant permissions
GRANT ALL PRIVILEGES ON monitoring.* TO 'user'@'%';
GRANT ALL PRIVILEGES ON trading.* TO 'user'@'%';

-- Create tables for monitoring
CREATE TABLE IF NOT EXISTS monitoring.metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metric_name VARCHAR(255) NOT NULL,
    metric_value DECIMAL,
    labels JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tables for trading
CREATE TABLE IF NOT EXISTS trading.trades (
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(255) UNIQUE NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    side VARCHAR(10) NOT NULL,
    quantity DECIMAL(15, 2) NOT NULL,
    price DECIMAL(10, 5) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trading.positions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    quantity DECIMAL(15, 2) NOT NULL,
    avg_price DECIMAL(10, 5) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO trading.trades (trade_id, symbol, side, quantity, price, status) VALUES
('T001', 'EURUSD', 'BUY', 1000, 1.09500, 'FILLED'),
('T002', 'GBPUSD', 'SELL', 500, 1.26500, 'FILLED'),
('T003', 'USDJPY', 'BUY', 10000, 149.500, 'PENDING')
ON CONFLICT (trade_id) DO NOTHING;
EOF
    
    log_success "Ma'lumotlar bazasi tayyorlandI"
}

# Create custom application
create_sample_application() {
    log_info "Namuna application yaratilmoqda..."
    
    # Create requirements.txt
    cat > custom_metrics/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
prometheus-client==0.19.0
psutil==5.9.6
requests==2.31.0
elasticsearch==8.11.0
jaeger-client==4.8.0
opentracing-instrumentation==3.1.1
structlog==23.2.0
asyncio==3.4.3
pyyaml==6.0.1
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
aioredis==2.0.1
EOF
    
    # Create main application file
    cat > custom_metrics/main.py << 'EOF'
#!/usr/bin/env python3
"""
Custom Business Metrics Exporter
Prometheus metrics uchun business metriklarni to'plash
"""

import time
import random
import asyncio
from datetime import datetime, timedelta
from prometheus_client import start_http_server, Gauge, Counter, Histogram
import psutil
import logging
import os

# Prometheus metrics
trading_volume = Gauge('business_trading_volume_total', 'Total trading volume', ['symbol'])
user_active_sessions = Gauge('business_user_active_sessions', 'Number of active user sessions', ['region'])
pnl_total = Gauge('business_pnl_total', 'Total P&L', ['symbol'])
risk_score = Gauge('business_risk_score', 'Current risk score', ['type'])
risk_alerts = Counter('business_risk_alerts_total', 'Number of risk alerts', ['type', 'severity'])
api_requests_total = Counter('business_api_requests_total', 'Total API requests', ['endpoint', 'method', 'status'])
response_time = Histogram('business_api_response_time_seconds', 'API response time', ['endpoint'])

class BusinessMetricsCollector:
    """Business metrics collector"""
    
    def __init__(self):
        self.running = False
        self.threads = []
    
    def collect_trading_metrics(self):
        """Trading metriqlarni to'plash"""
        symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD']
        
        while self.running:
            try:
                # Simulate trading volume
                for symbol in symbols:
                    volume = random.uniform(100000, 1000000)
                    trading_volume.labels(symbol=symbol).set(volume)
                
                # Simulate P&L
                for symbol in symbols:
                    pnl = random.uniform(-50000, 50000)
                    pnl_total.labels(symbol=symbol).set(pnl)
                
                time.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logging.error(f"Error collecting trading metrics: {e}")
                time.sleep(5)
    
    def collect_user_metrics(self):
        """User metriqlarni to'plash"""
        regions = ['US', 'EU', 'ASIA', 'AU']
        
        while self.running:
            try:
                # Simulate active user sessions
                for region in regions:
                    sessions = random.randint(10, 200)
                    user_active_sessions.labels(region=region).set(sessions)
                
                time.sleep(60)  # Update every minute
                
            except Exception as e:
                logging.error(f"Error collecting user metrics: {e}")
                time.sleep(10)
    
    def collect_risk_metrics(self):
        """Risk metriqlarni to'plash"""
        risk_types = ['market_risk', 'credit_risk', 'operational_risk']
        
        while self.running:
            try:
                # Simulate risk scores
                for risk_type in risk_types:
                    score = random.uniform(0, 100)
                    risk_score.labels(type=risk_type).set(score)
                    
                    # Simulate risk alerts
                    if score > 80:
                        severity = 'critical' if score > 95 else 'high'
                        risk_alerts.labels(type=risk_type, severity=severity).inc()
                
                time.sleep(45)  # Update every 45 seconds
                
            except Exception as e:
                logging.error(f"Error collecting risk metrics: {e}")
                time.sleep(10)
    
    def start(self):
        """Metrics collectorni ishga tushirish"""
        self.running = True
        
        import threading
        self.threads = [
            threading.Thread(target=self.collect_trading_metrics, daemon=True),
            threading.Thread(target=self.collect_user_metrics, daemon=True),
            threading.Thread(target=self.collect_risk_metrics, daemon=True)
        ]
        
        for thread in self.threads:
            thread.start()
    
    def stop(self):
        """Metrics collectorni to'xtatish"""
        self.running = False
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    # Get configuration from environment
    port = int(os.getenv('PROMETHEUS_PORT', 8080))
    
    logger.info(f"Starting business metrics collector on port {port}")
    
    # Start metrics collector
    collector = BusinessMetricsCollector()
    collector.start()
    
    # Start Prometheus HTTP server
    start_http_server(port)
    
    logger.info(f"Metrics available at http://localhost:{port}/metrics")
    
    try:
        # Keep the application running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down metrics collector...")
        collector.stop()

if __name__ == "__main__":
    main()
EOF
    
    # Create Dockerfile for custom metrics
    cat > custom_metrics/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/metrics || exit 1

# Run application
CMD ["python", "main.py"]
EOF
    
    # Create config file
    cat > custom_metrics/config.yml << 'EOF'
# Business Metrics Configuration

metrics:
  collection_interval: 30
  enable_trading_metrics: true
  enable_user_metrics: true
  enable_risk_metrics: true

trading:
  symbols:
    - EURUSD
    - GBPUSD
    - USDJPY
    - AUDUSD
    - USDCAD
  volume_range: [100000, 1000000]
  pnl_range: [-50000, 50000]

users:
  regions:
    - US
    - EU
    - ASIA
    - AU
  session_range: [10, 200]

risk:
  types:
    - market_risk
    - credit_risk
    - operational_risk
  alert_threshold: 80
  critical_threshold: 95

prometheus:
  port: 8080
  path: /metrics
EOF
    
    log_success "Namuna application yaratildi"
}

# Create application
create_application() {
    log_info "Asosiy application yaratilmoqda..."
    
    # Create requirements.txt
    cat > application/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
prometheus-client==0.19.0
opentracing-instrumentation==3.1.1
jaeger-client==4.8.0
structlog==23.2.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
elasticsearch==8.11.0
requests==2.31.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pyyaml==6.0.1
asyncio-mqtt==0.16.1
websockets==12.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
EOF
    
    # Create main application
    cat > application/main.py << 'EOF'
#!/usr/bin/env python3
"""
Trading Application - Monitoring Example
Performance monitoring va observability bilan trading application
"""

import time
import random
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import logging
import structlog

# Monitoring imports
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from opentracing_instrumentation.client_hooks import install_all_patches
from jaeger_client import Config as JaegerConfig

# Install OpenTracing patches
install_all_patches()

# Configure Jaeger
jaeger_config = JaegerConfig(
    config={
        'sampler': {
            'type': 'const',
            'param': 1,
        },
        'local_agent': {
            'reporting_host': 'jaeger',
            'reporting_port': 14268,
        },
        'logging': True,
    },
    service_name='trading_app',
    validate=True,
)

# Create tracer
tracer = jaeger_config.new_tracer()

# Prometheus metrics
api_requests_total = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
api_request_duration = Histogram('api_request_duration_seconds', 'API request duration', ['method', 'endpoint'])
active_trades = Gauge('trading_active_trades_total', 'Number of active trades')
system_cpu_usage = Gauge('system_cpu_usage_percent', 'System CPU usage percent')
system_memory_usage = Gauge('system_memory_usage_percent', 'System memory usage percent')

# Structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# FastAPI app
app = FastAPI(title="Trading Application", version="1.0.0")

# Pydantic models
class Trade(BaseModel):
    trade_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    status: str = "PENDING"

class MarketData(BaseModel):
    symbol: str
    price: float
    bid: float
    ask: float
    timestamp: datetime

# In-memory storage (in production, use proper database)
trades_db = {}
market_data_db = {}

@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {"message": "Trading Application", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    
    # System metrics
    import psutil
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    
    system_cpu_usage.set(cpu_percent)
    system_memory_usage.set(memory_percent)
    
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "cpu_usage": cpu_percent,
        "memory_usage": memory_percent,
        "active_trades": len(trades_db)
    }

@app.get("/api/market/{symbol}")
async def get_market_data(symbol: str):
    """Get market data for symbol"""
    start_time = time.time()
    
    try:
        # Simulate market data
        price = random.uniform(0.5, 2.0)
        bid = price - 0.001
        ask = price + 0.001
        
        market_data = MarketData(
            symbol=symbol,
            price=price,
            bid=bid,
            ask=ask,
            timestamp=datetime.now()
        )
        
        market_data_db[symbol] = market_data
        
        # Record metrics
        duration = time.time() - start_time
        api_requests_total.labels(method="GET", endpoint="market", status="200").inc()
        api_request_duration.labels(method="GET", endpoint="market").observe(duration)
        
        logger.info("Market data retrieved", symbol=symbol, price=price)
        
        return market_data.dict()
        
    except Exception as e:
        duration = time.time() - start_time
        api_requests_total.labels(method="GET", endpoint="market", status="500").inc()
        api_request_duration.labels(method="GET", endpoint="market").observe(duration)
        
        logger.error("Market data error", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trades")
async def create_trade(trade: Trade, background_tasks: BackgroundTasks):
    """Create a new trade"""
    start_time = time.time()
    
    try:
        # Validate trade
        if trade.symbol not in market_data_db:
            raise HTTPException(status_code=400, detail=f"Symbol {trade.symbol} not found")
        
        # Set trade ID if not provided
        if not trade.trade_id:
            trade.trade_id = f"T{len(trades_db):06d}"
        
        # Store trade
        trades_db[trade.trade_id] = trade
        active_trades.set(len(trades_db))
        
        # Background task to process trade
        background_tasks.add_task(process_trade, trade.trade_id)
        
        # Record metrics
        duration = time.time() - start_time
        api_requests_total.labels(method="POST", endpoint="trades", status="201").inc()
        api_request_duration.labels(method="POST", endpoint="trades").observe(duration)
        
        logger.info("Trade created", trade_id=trade.trade_id, symbol=trade.symbol)
        
        return {"message": "Trade created successfully", "trade_id": trade.trade_id}
        
    except Exception as e:
        duration = time.time() - start_time
        api_requests_total.labels(method="POST", endpoint="trades", status="500").inc()
        api_request_duration.labels(method="POST", endpoint="trades").observe(duration)
        
        logger.error("Trade creation error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

async def process_trade(trade_id: str):
    """Background task to process trade"""
    await asyncio.sleep(random.uniform(1, 5))  # Simulate processing time
    
    if trade_id in trades_db:
        trade = trades_db[trade_id]
        
        # Simulate trade execution
        if random.random() > 0.1:  # 90% success rate
            trade.status = "FILLED"
            logger.info("Trade filled", trade_id=trade_id)
        else:
            trade.status = "REJECTED"
            logger.warning("Trade rejected", trade_id=trade_id)

@app.get("/api/trades")
async def get_trades():
    """Get all trades"""
    start_time = time.time()
    
    try:
        trades = list(trades_db.values())
        
        # Record metrics
        duration = time.time() - start_time
        api_requests_total.labels(method="GET", endpoint="trades_list", status="200").inc()
        api_request_duration.labels(method="GET", endpoint="trades_list").observe(duration)
        
        logger.info("Trades retrieved", count=len(trades))
        
        return {"trades": [trade.dict() for trade in trades]}
        
    except Exception as e:
        duration = time.time() - start_time
        api_requests_total.labels(method="GET", endpoint="trades_list", status="500").inc()
        api_request_duration.labels(method="GET", endpoint="trades_list").observe(duration)
        
        logger.error("Trades retrieval error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return JSONResponse(content={})

@app.get("/api/portfolio")
async def get_portfolio():
    """Get portfolio summary"""
    start_time = time.time()
    
    try:
        # Calculate portfolio metrics
        total_trades = len(trades_db)
        filled_trades = sum(1 for t in trades_db.values() if t.status == "FILLED")
        
        portfolio = {
            "total_trades": total_trades,
            "filled_trades": filled_trades,
            "pending_trades": total_trades - filled_trades,
            "success_rate": (filled_trades / total_trades * 100) if total_trades > 0 else 0,
            "timestamp": datetime.now()
        }
        
        # Record metrics
        duration = time.time() - start_time
        api_requests_total.labels(method="GET", endpoint="portfolio", status="200").inc()
        api_request_duration.labels(method="GET", endpoint="portfolio").observe(duration)
        
        logger.info("Portfolio retrieved", total_trades=total_trades)
        
        return portfolio
        
    except Exception as e:
        duration = time.time() - start_time
        api_requests_total.labels(method="GET", endpoint="portfolio", status="500").inc()
        api_request_duration.labels(method="GET", endpoint="portfolio").observe(duration)
        
        logger.error("Portfolio error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Start Prometheus metrics server on port 8090
    start_http_server(8090)
    
    # Run FastAPI application
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
    
    # Create Dockerfile for application
    cat > application/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Expose ports
EXPOSE 8000 8090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run application
CMD ["python", "main.py"]
EOF
    
    log_success "Asosiy application yaratildi"
}

# Create Nginx configuration
create_nginx_config() {
    log_info "Nginx konfiguratsiya yaratilmoqda..."
    
    cat > configs/nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
    
    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=10r/s;
    
    # Upstream servers
    upstream trading_app {
        server trading_app:8000;
    }
    
    upstream prometheus {
        server prometheus:9090;
    }
    
    upstream grafana {
        server grafana:3000;
    }
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name localhost;
        return 301 https://$server_name$request_uri;
    }
    
    # Main server
    server {
        listen 443 ssl http2;
        server_name localhost;
        
        ssl_certificate /etc/nginx/ssl/certificate.crt;
        ssl_certificate_key /etc/nginx/ssl/private.key;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        
        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://trading_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
        
        # Metrics endpoints (restricted)
        location /metrics {
            allow 127.0.0.1;
            allow 172.16.0.0/12;  # Docker network
            deny all;
            
            proxy_pass http://trading_app/metrics;
        }
        
        # Prometheus (restricted)
        location /prometheus/ {
            auth_basic "Prometheus Monitoring";
            auth_basic_user_file /etc/nginx/.htpasswd;
            
            proxy_pass http://prometheus/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # Grafana (restricted)
        location /grafana/ {
            auth_basic "Grafana Dashboard";
            auth_basic_user_file /etc/nginx/.htpasswd;
            
            proxy_pass http://grafana/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # Health check
        location /nginx-health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF
    
    # Create password file for protected endpoints
    echo "admin:$(openssl passwd -apr1 admin123)" > configs/nginx/.htpasswd
    
    log_success "Nginx konfiguratsiya tayyor"
}

# Deploy monitoring stack
deploy_monitoring_stack() {
    log_info "Monitoring stack deploy qilinmoqda..."
    
    cd "$MONITORING_DIR"
    
    # Build and start services
    docker-compose up -d --build
    
    log_success "Monitoring stack deploy qilindi"
    
    # Wait for services to be ready
    log_info "Xizmatlar tayyor bo'lishini kutish (60 soniya)..."
    sleep 60
    
    # Check service health
    check_service_health
}

# Check service health
check_service_health() {
    log_info "Xizmatlar sog'lig'i tekshirilmoqda..."
    
    services=("prometheus:9090" "grafana:3000" "elasticsearch:9200" "kibana:5601" "jaeger:16686")
    
    for service in "${services[@]}"; do
        IFS=':' read -r name port <<< "$service"
        url="http://localhost:$port"
        
        if curl -f -s "$url" > /dev/null; then
            log_success "$name - OK ($url)"
        else
            log_warning "$name - NOK ($url)"
        fi
    done
}

# Run integration tests
run_integration_tests() {
    log_info "Integration testlar ishga tushirilmoqda..."
    
    cd "$MONITORING_DIR"
    
    # Install Python dependencies for testing
    pip3 install requests pytest > /dev/null 2>&1 || true
    
    # Create and run test script
    cat > test_monitoring.py << 'EOF'
#!/usr/bin/env python3
import requests
import time
import json

services = {
    'Prometheus': 'http://localhost:9090',
    'Grafana': 'http://localhost:3000/api/health',
    'Elasticsearch': 'http://localhost:9200/_cluster/health',
    'Kibana': 'http://localhost:5601/api/status',
    'Jaeger': 'http://localhost:16686',
    'Trading App': 'http://localhost:8000/api/health'
}

def test_services():
    results = {}
    
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=10)
            status = 'OK' if response.status_code == 200 else f'NOK ({response.status_code})'
            results[name] = status
            print(f"✓ {name}: {status}")
        except Exception as e:
            results[name] = f'ERROR: {str(e)}'
            print(f"✗ {name}: ERROR - {str(e)}')
    
    return results

if __name__ == "__main__":
    print("Monitoring Stack Integration Tests")
    print("=" * 50)
    
    results = test_services()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    for name, status in results.items():
        print(f"{name}: {status}")
    
    # Save results
    with open('test_results.json', 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'results': results
        }, f, indent=2)
    
    print(f"\nTest results saved to test_results.json")
EOF
    
    python3 test_monitoring.py
    
    log_success "Integration testlar tugadi"
}

# Show monitoring URLs
show_urls() {
    log_info "Monitoring tizimi URL manzillari:"
    echo ""
    echo -e "${BLUE}=== Monitoring URLs ===${NC}"
    echo -e "${GREEN}Prometheus:${NC}      http://localhost:9090"
    echo -e "${GREEN}Grafana:${NC}        http://localhost:3000 (admin/admin123)"
    echo -e "${GREEN}Kibana:${NC}         http://localhost:5601"
    echo -e "${GREEN}Jaeger:${NC}         http://localhost:16686"
    echo -e "${GREEN}Elasticsearch:${NC}  http://localhost:9200"
    echo -e "${GREEN}Zipkin:${NC}         http://localhost:9411"
    echo -e "${GREEN}Trading App:${NC}    http://localhost:8000"
    echo -e "${GREEN}Nginx:${NC}          https://localhost (HTTP redirect to HTTPS)"
    echo ""
    echo -e "${YELLOW}=== Quick Commands ===${NC}"
    echo -e "View logs:        docker-compose logs -f [service_name]"
    echo -e "Stop stack:       docker-compose down"
    echo -e "Restart service:  docker-compose restart [service_name]"
    echo -e "Update metrics:   curl http://localhost:8000/api/market/EURUSD"
}

# Show help
show_help() {
    echo "Monitoring Stack Management Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  setup       - Barcha konfiguratsiyalarni yaratish"
    echo "  deploy      - Monitoring stack ni deploy qilish"
    echo "  test        - Integration testlarni ishga tushirish"
    echo "  urls        - Monitoring URLs ko'rsatish"
    echo "  health      - Xizmatlar sog'lig'ini tekshirish"
    echo "  stop        - Monitoring stack ni to'xtatish"
    echo "  clean       - Barcha ma'lumotlarni o'chirish"
    echo "  help        - Bu yordamni ko'rsatish"
    echo ""
    echo "Examples:"
    echo "  $0 setup    # Barcha konfiguratsiyalarni yaratish"
    echo "  $0 deploy   # Stack ni deploy qilish"
    echo "  $0 test     # Testlarni ishga tushirish"
}

# Stop monitoring stack
stop_monitoring() {
    log_info "Monitoring stack to'xtatilmoqda..."
    cd "$MONITORING_DIR"
    docker-compose down
    log_success "Monitoring stack to'xtatildi"
}

# Clean up everything
clean_everything() {
    log_warning "Barcha ma'lumotlar o'chiriladi. Davom etishni xohlaysizmi? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        log_info "Hamma narsa tozalanmoqda..."
        cd "$MONITORING_DIR"
        docker-compose down -v --remove-orphans
        docker system prune -f
        rm -rf prometheus_data grafana_data elasticsearch_data
        log_success "Tozalash tugadi"
    else
        log_info "Tozalash bekor qilindi"
    fi
}

# Main script logic
main() {
    check_docker
    
    case "${1:-help}" in
        "setup")
            setup_directories
            generate_ssl_certificates
            init_database
            create_sample_application
            create_application
            create_nginx_config
            log_success "Setup tugadi! Keyingi qadam: $0 deploy"
            ;;
        "deploy")
            deploy_monitoring_stack
            show_urls
            ;;
        "test")
            run_integration_tests
            ;;
        "urls")
            show_urls
            ;;
        "health")
            check_service_health
            ;;
        "stop")
            stop_monitoring
            ;;
        "clean")
            clean_everything
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "Noma'lum buyruq: $1"
            show_help
            exit 1
            ;;
    esac
}

# Script execution
main "$@"