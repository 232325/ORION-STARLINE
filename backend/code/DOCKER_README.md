# =============================================================================
# FastAPI Trading Application - Docker Setup Guide
# =============================================================================
# Production-ready Docker configuration for FastAPI Trading System
# Author: MiniMax Agent
# Version: 1.0.0
# =============================================================================

## 📋 OVERVIEW

Bu Docker konfiguratsiyasi FastAPI Trading Application ni production va development muhitlarda ishlatish uchun tayyorlangan.

### 🏗️ Arxitektura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │  FastAPI API    │    │     Redis       │
│  (Reverse Proxy)│◄──►│   (Port 8000)   │◄──►│    (Cache)      │
│  (Port 80/443)  │    │                 │    │   (Port 6379)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
    SSL/TLS               Application Logic         Data Storage
```

## 🚀 TEZ BOSHLASH

### 1. Environment faylini sozlang

```bash
# .env.example faylini nusxalash
cp .env.example .env

# .env faylini tahrirlash
nano .env
```

**Muhim konfiguratsiyalar:**

```bash
# Secret key ni o'zgartiring (PRODUCTION DA!)
SECRET_KEY=your-super-secret-key-change-in-production-12345

# Redis parolini o'zgartiring
REDIS_PASSWORD=secure_redis_password_123

# API keys (ixtiyoriy)
BINANCE_API_KEY=your_binance_key
BINANCE_API_SECRET=your_binance_secret
```

### 2. Docker Compose bilan ishga tushirish

**Production (standalone):**
```bash
docker-compose up -d
```

**Development (hot reload bilan):**
```bash
docker-compose -f docker-compose.simple.yml -f docker-compose.dev.yml up -d
```

### 3. Xizmatlar holatini tekshirish

```bash
# Containerlarni ko'rish
docker-compose ps

# Loglarni ko'rish
docker-compose logs api
docker-compose logs redis

# Health check
curl http://localhost:8000/health
```

## 🔧 DOCKER KONFIGURATSIYASI

### Dockerfile Xususiyatlari

- **Base Image:** Python 3.11-slim (minimal va xavfsiz)
- **Multi-stage build:** Optimallashtirilgan image hajmi
- **Non-root user:** Xavfsizlik uchun
- **Health check:** Automatic monitoring
- **Production ready:** Worker processes va logging

### Container Structure

```dockerfile
Stage 1: Builder
├── Dependencies installation
├── System packages (gcc, g++, libpq-dev)
└── Python packages from api/requirements.txt

Stage 2: Runtime
├── Minimal runtime environment
├── Redis client libraries
├── Application code
└── Non-root user (trader:trader)
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | JWT secret key | - | ✅ |
| `REDIS_PASSWORD` | Redis password | - | ✅ |
| `API_PORT` | FastAPI port | 8000 | ❌ |
| `ENVIRONMENT` | dev/prod | production | ❌ |
| `DATABASE_URL` | DB connection | - | ❌ |
| `CORS_ORIGINS` | Allowed origins | * | ❌ |

## 🏃‍♂️ DEVELOPMENT SETUP

### Hot Reload bilan ishga tushirish

```bash
# Development compose fayli bilan
docker-compose -f docker-compose.simple.yml -f docker-compose.dev.yml up -d

# Yoki manual
docker-compose up -d
```

### Local Development

```bash
# Container ichida bash
docker exec -it fastapi-trading-api bash

# Python package o'rnatish
pip install package_name

# Logs ko'rish
docker-compose logs -f api
```

## 📊 MONITORING & DEBUGGING

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Redis health
docker exec fastapi-trading-redis redis-cli ping

# Container logs
docker-compose logs api --tail=100
```

### Performance Monitoring

```bash
# Resource usage
docker stats

# Container logs
docker-compose logs -f --tail=50 api

# Redis monitoring
docker exec -it fastapi-trading-redis redis-cli monitor
```

## 🔒 SECURITY

### Production Security Checklist

- [ ] `SECRET_KEY` ni o'zgartiring
- [ ] `REDIS_PASSWORD` ni o'zgartiring
- [ ] `CORS_ORIGINS` ni cheklang
- [ ] SSL/TLS konfiguratsiyasini sozlang
- [ ] Firewall qoidalarini o'rnating
- [ ] Log monitoring o'rnating

### SSL/TLS Setup

```nginx
# nginx/nginx.conf faylida SSL konfiguratsiya
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🚢 DEPLOYMENT

### Production Deployment

1. **Server setup:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **Application deployment:**
```bash
# Repository ni clone qiling
git clone <your-repo>
cd <your-repo>

# Environment setup
cp .env.example .env
nano .env  # Configure production values

# Deploy
docker-compose up -d
```

3. **SSL Certificate (Let's Encrypt):**
```bash
# Certbot o'rnatish
sudo apt install certbot python3-certbot-nginx

# SSL certificate olish
sudo certbot --nginx -d your-domain.com
```

### Docker Commands

```bash
# Rebuild image
docker-compose build api --no-cache

# Restart services
docker-compose restart

# Scale services
docker-compose up -d --scale api=3

# Clean up
docker-compose down -v
docker system prune -a
```

## 🛠️ TROUBLESHOOTING

### Tez-tez uchraydigan muammolar

**1. Port already in use:**
```bash
# Portni tekshirish
sudo netstat -tulpn | grep :8000

# Container stop
docker-compose down
```

**2. Permission denied:**
```bash
# File permissions
sudo chown -R $USER:$USER ./api/uploads
chmod -R 755 ./api/uploads
```

**3. Redis connection failed:**
```bash
# Redis status
docker-compose logs redis

# Redis restart
docker-compose restart redis
```

**4. Health check failed:**
```bash
# Manual health check
docker exec fastapi-trading-api curl -f http://localhost:8000/health

# Container logs
docker-compose logs api
```

### Debug Commands

```bash
# Container ichiga kirish
docker exec -it fastapi-trading-api /bin/bash

# Python environment
docker exec -it fastapi-trading-api python

# Database connection
docker exec -it fastapi-trading-api python -c "
from sqlalchemy import create_engine
print('DB connection OK')
"

# Redis test
docker exec -it fastapi-trading-redis redis-cli ping
```

## 📈 SCALING

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  api:
    deploy:
      replicas: 3
    ports:
      - "8000-8002:8000"
```

### Load Balancer

```nginx
upstream api_backend {
    server api:8000;
    server api_2:8000;
    server api_3:8000;
}

server {
    location / {
        proxy_pass http://api_backend;
    }
}
```

## 🎯 API ENDPOINTS

Asosiy endpointlar:

- `GET /health` - Tizim sog'ligi
- `GET /api/docs` - Swagger UI
- `GET /api/redoc` - ReDoc
- `GET /api/v1/system/status` - Tizim holati
- `POST /api/v1/auth/login` - Foydalanuvchi login

**To'liq API dokumentatsiya:** http://localhost:8000/api/docs

---

**Dasturchi:** MiniMax Agent  
**Versiya:** 1.0.0  
**Oxirgi yangilanish:** 2025-11-04