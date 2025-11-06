# 🚀 AI Trading Evolution - Production Deployment Yo'riqnomasi

## 📋 Mundarija

1. [Kirish](#kirish)
2. [Talablar](#talablar)
3. [O'rnatish](#ornatish)
4. [Konfiguratsiya](#konfiguratsiya)
5. [Deployment](#deployment)
6. [Monitoring](#monitoring)
7. [Xavfsizlik](#xavfsizlik)
8. [Troubleshooting](#troubleshooting)

---

## Kirish

**AI Trading Evolution** - bu professional trading bot platformasi bo'lib, quyidagi imkoniyatlarni taqdim etadi:

- ✅ **30+ Trading Strategiyalari**: Arbitrage, Grid, DCA, Futures, va boshqalar
- ✅ **6 Bozor Turi**: Crypto, Forex, Stocks, Commodities, Bonds, ETFs
- ✅ **AI/ML Models**: Reinforcement Learning, Deep Learning, Ensemble Methods
- ✅ **Real-time Analytics**: Sentiment, Whale Tracking, Risk Scoring
- ✅ **Production-ready**: Docker, Kubernetes, Monitoring, Security

---

## Talablar

### Minimal Talablar

- **OS**: Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disk**: 50 GB SSD
- **Docker**: 24.0+
- **Docker Compose**: 2.20+

### Tavsiya Etiladigan Talablar

- **OS**: Linux (Ubuntu 22.04 LTS)
- **CPU**: 8+ cores
- **RAM**: 16+ GB
- **Disk**: 100+ GB NVMe SSD
- **Docker**: Latest stable
- **Docker Compose**: Latest stable

### Dasturiy Ta'minot

```bash
# Docker o'rnatish (Ubuntu)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose o'rnatish
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

---

## O'rnatish

### 1. Repository Klonlash

```bash
git clone https://github.com/yourusername/ai-trading-evolution.git
cd ai-trading-evolution/code
```

### 2. Environment Variables Sozlash

```bash
# .env.example'dan nusxa olish
cp .env.example .env

# .env faylini tahrirlash
nano .env
```

**Muhim o'zgaruvchilar:**

```env
# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secret-key-here

# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# API Keys
BINANCE_API_KEY=your-binance-key
BINANCE_API_SECRET=your-binance-secret
```

### 3. SSL Sertifikatlari (HTTPS)

**Option 1: Let's Encrypt (Tavsiya)**

```bash
# Certbot o'rnatish
sudo apt install certbot

# Sertifikat olish
sudo certbot certonly --standalone -d api.yourdomain.com

# Sertifikatni Docker papkasiga ko'chirish
sudo cp /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/api.yourdomain.com/privkey.pem nginx/ssl/
```

**Option 2: Self-signed (Test uchun)**

```bash
# Self-signed sertifikat yaratish
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=api.yourdomain.com"
```

---

## Konfiguratsiya

### Database Setup

**PostgreSQL (tavsiya)**

```bash
# Docker bilan PostgreSQL
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=ai_trading \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15-alpine

# Database URL
# DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/ai_trading
```

**Supabase (cloud-hosted)**

1. https://supabase.com da account yarating
2. Yangi project yarating
3. Database URL va API keys'ni `.env` ga qo'shing

### Redis Setup

Redis avtomatik ravishda `docker-compose` orqali ishga tushadi.

Manual o'rnatish:

```bash
# Redis Docker
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine
```

---

## Deployment

### Quick Start (Development)

```bash
# Barcha servislarni ishga tushirish
docker-compose up -d

# Loglarni kuzatish
docker-compose logs -f api
```

### Production Deployment

```bash
# Deployment script'ni ishga tushirish
bash deploy.sh
```

Script quyidagilarni bajaradi:

1. ✅ Docker va Docker Compose'ni tekshiradi
2. ✅ `.env` faylini tekshiradi
3. ✅ Kerakli papkalarni yaratadi
4. ✅ Docker image'larni build qiladi
5. ✅ Servislarni ishga tushiradi
6. ✅ Health check'larni bajaradi

### Manual Deployment

```bash
# 1. Image'larni build qilish
docker-compose build --no-cache

# 2. Servislarni ishga tushirish
docker-compose up -d

# 3. Statusni tekshirish
docker-compose ps

# 4. Health check
curl http://localhost:8000/health
```

### Kubernetes Deployment (Advanced)

```bash
# Kubernetes manifest'larni generate qilish
# (Coming soon)

kubectl apply -f k8s/
kubectl get pods -n ai-trading
```

---

## Monitoring

### Servis URL'lari

| Servis | URL | Izoh |
|--------|-----|------|
| **API Server** | http://localhost:8000 | Main API |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Health Check** | http://localhost:8000/health | Status |
| **Prometheus** | http://localhost:9090 | Metrics |
| **Grafana** | http://localhost:3001 | Dashboards |

### Grafana Dashboard

1. Grafana'ga kiring: http://localhost:3001
2. Login: `admin` / Password: `admin`
3. Dashboards → AI Trading Evolution

**Monitoring Metrics:**

- Request rate va latency
- Error rate
- CPU va Memory usage
- Cache hit rate
- Database connections
- Trading performance

### Loglar

```bash
# Barcha loglar
docker-compose logs -f

# Faqat API logs
docker-compose logs -f api

# Real-time logs
tail -f logs/api.log

# Nginx logs
tail -f logs/nginx/access.log
```

---

## Xavfsizlik

### 1. Environment Variables

```bash
# .env faylini himoyalash
chmod 600 .env

# Git'dan chiqarish
echo ".env" >> .gitignore
```

### 2. Firewall

```bash
# UFW (Ubuntu Firewall)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 3. API Rate Limiting

`.env` faylida:

```env
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

### 4. JWT Authentication

```env
JWT_SECRET_KEY=your-very-strong-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### 5. SSL/TLS

- ✅ HTTPS'ni majburiy qiling
- ✅ Let's Encrypt sertifikatlarini ishlating
- ✅ TLS 1.2+ faqat

### 6. Security Audit

```bash
# Security scan
docker-compose exec api python -m integration.security_auditor

# Vulnerability check
docker scan ai-trading-api:latest
```

---

## Troubleshooting

### 1. Container ishga tushmayapti

```bash
# Container statusini tekshirish
docker-compose ps

# Loglarni ko'rish
docker-compose logs api

# Container ichiga kirish
docker-compose exec api bash
```

### 2. Database connection error

```bash
# PostgreSQL statusini tekshirish
docker-compose exec postgres psql -U postgres -c "SELECT 1"

# Connection test
python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('$DATABASE_URL'))"
```

### 3. Redis connection error

```bash
# Redis statusini tekshirish
docker-compose exec redis redis-cli ping

# Redis logs
docker-compose logs redis
```

### 4. Port already in use

```bash
# Port'ni band qilgan processni topish
sudo lsof -i :8000

# Processni to'xtatish
sudo kill -9 <PID>
```

### 5. Out of memory

```bash
# Memory usage
docker stats

# Container'larga memory limit qo'yish
# docker-compose.yml da:
services:
  api:
    mem_limit: 4g
    mem_reservation: 2g
```

### 6. Disk space full

```bash
# Disk usage
df -h

# Docker cleanup
docker system prune -a --volumes

# Log rotation
sudo logrotate -f /etc/logrotate.d/docker-container
```

---

## Boshqarish Buyruqlari

### Docker Compose

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Rebuild
docker-compose build --no-cache

# Logs
docker-compose logs -f

# Scale API servers
docker-compose up -d --scale api=3

# Remove everything
docker-compose down -v --remove-orphans
```

### Database Migrations

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Create migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Rollback
docker-compose exec api alembic downgrade -1
```

### Backup & Restore

```bash
# Database backup
docker-compose exec postgres pg_dump -U postgres ai_trading > backup.sql

# Restore
docker-compose exec -T postgres psql -U postgres ai_trading < backup.sql

# Redis backup
docker-compose exec redis redis-cli BGSAVE
```

---

## Performance Tuning

### 1. Workers Optimization

`.env` faylida:

```env
# CPU cores ga qarab
WORKERS=4  # 2 * CPU cores + 1
```

### 2. Database Pooling

```python
# sqlalchemy config
pool_size=20
max_overflow=10
pool_timeout=30
pool_recycle=3600
```

### 3. Redis Caching

```env
CACHE_TTL=300
CACHE_MAX_SIZE=1000
```

### 4. Nginx Tuning

`nginx/nginx.conf`:

```nginx
worker_connections 2048;
keepalive_timeout 65;
client_max_body_size 50M;
```

---

## Qo'shimcha Resurslar

- 📚 [API Documentation](http://localhost:8000/docs)
- 🔧 [Configuration Guide](./CONFIGURATION.md)
- 🔐 [Security Best Practices](./SECURITY.md)
- 📊 [Monitoring Guide](./MONITORING.md)
- 🐛 [Bug Reports](https://github.com/yourusername/ai-trading-evolution/issues)

---

## Support

Savollar yoki muammolar bo'lsa:

- 📧 Email: support@yourdomain.com
- 💬 Telegram: @yourtelegram
- 🐛 GitHub Issues: https://github.com/yourusername/ai-trading-evolution/issues

---

**Author**: MiniMax Agent  
**Version**: 1.0.0  
**Date**: 2025-11-04  
**License**: Proprietary
