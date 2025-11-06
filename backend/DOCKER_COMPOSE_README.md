# AI Trading Platform - Docker Compose Setup

## 🏗️ Architecture

Bu Docker Compose konfiguratsiyasi quyidagi servislarni o'z ichiga oladi:

### Core Services
- **FastAPI Backend** - Asosiy API server (Port 8000)
- **PostgreSQL** - Ma'lumotlar bazasi (Port 5432)
- **Redis** - Cache va session management (Port 6379)
- **RabbitMQ** - Message queue va async task management (Port 5672)

### Monitoring & Observability
- **Prometheus** - Metrics collection (Port 9090)
- **Grafana** - Dashboard va visualization (Port 3001)
- **Elasticsearch** - Log storage (Port 9200)
- **Kibana** - Log analysis (Port 5601)
- **Logstash** - Log processing (Port 5044)

### Worker Services
- **Background Workers** - Celery workers (2 ta replica)
- **Scheduler** - Cron-like vazifalar uchun
- **Flower** - Task monitoring UI (Port 5555)

### Proxy & Load Balancing
- **Nginx** - Reverse proxy va load balancer (Port 80/443)

## 🚀 Quick Start

### 1. Environment Setup
```bash
# .env faylini yarating
cp .env.example .env

# Parollarni va konfiguratsiyalarni tahrirlang
nano .env
```

### 2. Service Start
```bash
# Barcha servislarni background'da ishga tushirish
docker-compose up -d

# Loglarni ko'rish
docker-compose logs -f

# Servislar holatini tekshirish
docker-compose ps
```

### 3. Access URLs
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Kibana**: http://localhost:5601
- **Flower**: http://localhost:5555
- **RabbitMQ Management**: http://localhost:15672

## 🔧 Service Management

### Restart Services
```bash
# Barcha servislarni qayta ishga tushirish
docker-compose restart

# Muayyan servisni qayta ishga tushirish
docker-compose restart api

# Barcha servislarni to'liq tozalash
docker-compose down -v
```

### Scaling Workers
```bash
# Worker replicalarini ko'paytirish
docker-compose up -d --scale worker=4
```

### Database Operations
```bash
# Database backup
docker-compose exec postgres pg_dump -U trading_user trading_platform > backup.sql

# Database restore
docker-compose exec -T postgres psql -U trading_user trading_platform < backup.sql
```

## 📊 Monitoring

### Health Checks
```bash
# Barcha servislar uchun health check
docker-compose ps

# Logs ni real-time ko'rish
docker-compose logs -f --tail=100
```

### Performance Monitoring
- **Prometheus**: http://localhost:9090
- **Grafana Dashboards**: http://localhost:3001
- **Custom Metrics**: `/metrics` endpoint

## 🔒 Security

### Database Security
- PostgreSQL user: `trading_user`
- Redis password: `redis_secure_password_2025`
- RabbitMQ credentials: `trading_user`/`rabbitmq_secure_password_2025`

### Recommended Security Steps
1. `.env` faylida barcha parollarni o'zgartiring
2. Production muhitida SSL sertifikalari qo'shing
3. Firewallda zaruriy portlarni oching
4. Regular backup rejalarini yarating

## 🗂️ Volume Structure

```
/workspace/code/
├── data/
│   ├── postgres/     # Database files
│   ├── redis/        # Redis persistence
│   ├── rabbitmq/     # RabbitMQ data
│   ├── prometheus/   # Prometheus metrics
│   ├── grafana/      # Grafana dashboards
│   ├── elasticsearch/ # Elasticsearch data
│   └── kibana/       # Kibana configuration
├── logs/
│   └── nginx/        # Nginx logs
├── strategies/       # Trading strategies
├── models/           # ML models
├── backups/          # Database backups
└── init-scripts/     # Database initialization scripts
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Portlarni tekshirish
   netstat -tulpn | grep :8000
   ```

2. **Database connection issues**
   ```bash
   # PostgreSQL loglarini tekshirish
   docker-compose logs postgres
   ```

3. **Redis connection issues**
   ```bash
   # Redis health check
   docker-compose exec redis redis-cli ping
   ```

4. **Memory issues**
   ```bash
   # Resource usage
   docker stats
   ```

### Log Locations
- **Application logs**: `./logs/`
- **Database logs**: `docker-compose logs postgres`
- **Nginx logs**: `./logs/nginx/`
- **Prometheus data**: `./data/prometheus/`

## 📋 Requirements

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM
- At least 20GB disk space
- Linux/macOS/Windows with Docker Desktop

## 🔄 Updates

```bash
# Images yangilash
docker-compose pull

# Services qayta yaratish
docker-compose up -d --force-recreate

# Barcha cleanup
docker system prune -a
```

## 📞 Support

Agar muammo yuz bersa:
1. Log fayllarni tekshiring
2. Service health check natijalarini ko'ring
3. Issue sababini aniqlang
4. Gerekli servislarni restart qiling