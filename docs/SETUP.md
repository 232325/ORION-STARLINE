# 🛠️ Orion Starline Setup Guide

Bu qo'llanma sizga Orion Starline platformasini turli muhitlarda qanday o'rnatish va sozlashni o'rgatadi.

## 📋 Mundarija

- [Talablar](#talablar)
- [Development Setup](#development-setup)
- [Production Setup](#production-setup)
- [Docker Setup](#docker-setup)
- [Cloud Deployment](#cloud-deployment)
- [Troubleshooting](#troubleshooting)

## 📋 Talablar

### Minimal tizim talablari
- **OS**: Ubuntu 20.04+, macOS 10.15+, Windows 10+
- **RAM**: 8GB minimum, 16GB tavsiya etiladi
- **Storage**: 20GB bo'sh joy
- **Internet**: Stable internet connection

### Dasturiy ta'minot
- **Node.js**: 18.0+ ([Download](https://nodejs.org/))
- **Python**: 3.11+ ([Download](https://python.org/))
- **Git**: 2.30+ ([Download](https://git-scm.com/))
- **Docker**: 20.10+ ([Download](https://docker.com/))

## 🚀 Development Setup

### 1. Repository-ni clone qilish
```bash
git clone https://github.com/your-username/orion-starline.git
cd orion-starline
```

### 2. Backend Setup
```bash
cd backend

# Python virtual environment yaratish
python -m venv venv

# Virtual environment faollashtirish
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Dependencies o'rnatish
pip install -r requirements.txt

# Environment variables sozlash
cp .env.example .env
# .env faylni muharrir bilan oching va credentials qo'shing
```

### 3. Frontend Setup
```bash
cd frontend

# Dependencies o'rnatish
npm install
# yoki
pnpm install
# yoki
yarn install

# Environment variables sozlash
cp .env.example .env
# .env faylni muharrir bilan oching va credentials qo'shing
```

### 4. Supabase Setup
```bash
cd supabase

# Supabase CLI o'rnatish
npm install -g supabase

# Project yaratish
supabase init

# Database migrate
supabase db push

# Edge Functions deploy
supabase functions deploy
```

### 5. Development server-lar ishga tushirish

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Supabase
cd supabase
supabase start
```

## 🌐 Production Setup

### Environment variables
```bash
# Backend (.env)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
DATABASE_URL=postgresql://user:password@host:port/db
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your-openai-key
STRIPE_SECRET_KEY=your-stripe-key

# Frontend (.env)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_APP_ENV=production
VITE_API_URL=https://your-api-url.com
```

### Database Setup
```sql
-- PostgreSQL database yaratish
CREATE DATABASE orion_starline;

-- User yaratish
CREATE USER orion_user WITH PASSWORD 'secure_password';

-- Ruxsatlar berish
GRANT ALL PRIVILEGES ON DATABASE orion_starline TO orion_user;
```

### Redis Setup
```bash
# Redis o'rnatish (Ubuntu)
sudo apt update
sudo apt install redis-server

# Redis start qilish
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Redis test qilish
redis-cli ping
# Should return: PONG
```

## 🐳 Docker Setup

### 1. Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: orion_starline
      POSTGRES_USER: orion_user
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # Backend
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://orion_user:secure_password@postgres:5432/orion_starline
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"

  # Frontend
  frontend:
    build: ./frontend
    environment:
      - VITE_SUPABASE_URL=${SUPABASE_URL}
      - VITE_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
    depends_on:
      - backend
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

### 2. Docker-ni ishga tushirish
```bash
# Barcha servislar
docker-compose up -d

# Faqat backend
docker-compose up -d backend

# Build va run
docker-compose up --build -d

# Logs ko'rish
docker-compose logs -f

# Stop
docker-compose down
```

## ☁️ Cloud Deployment

### Vercel (Frontend)
```bash
# Vercel CLI o'rnatish
npm install -g vercel

# Deploy
vercel

# Production deploy
vercel --prod
```

### Railway (Backend)
```bash
# Railway CLI o'rnatish
npm install -g @railway/cli

# Login
railway login

# Deploy
railway init
railway up
```

### Supabase Cloud
```bash
# Supabase project yaratish
supabase projects create your-project-name

# Deploy
supabase db push
supabase functions deploy
```

## 🛠️ Configuration Files

### Backend Config (`config.py`)
```python
import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # API Keys
    openai_api_key: Optional[str] = None
    stripe_secret_key: Optional[str] = None
    
    # Security
    secret_key: str = "your-secret-key"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Frontend Config (`vite.config.ts`)
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
```

## 🔍 Troubleshooting

### Tez-tez uchraydigan muammolar

#### 1. Node.js versiyasi muammosi
```bash
# NVM (Node Version Manager) o'rnatish
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Node.js 18 o'rnatish
nvm install 18
nvm use 18
```

#### 2. Python virtual environment muammosi
```bash
# Python 3.11 o'rnatish (Ubuntu)
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# Virtual environment yaratish
python3.11 -m venv venv
source venv/bin/activate
```

#### 3. Database connection muammosi
```bash
# PostgreSQL status tekshirish
sudo systemctl status postgresql

# Kema bir nechta uzunlik qal'a
# O'chib qolgan sohifni qo'lda o'lcham
```

#### 4. Supabase Edge Functions
```bash
# Supabase auth tekshirish
supabase status

# Funksiyalarni qayta deploy qilish
supabase functions deploy --no-verify-jwt
```

#### 5. Portlar band bo'lgan
```bash
# Qaysi portlar ishlatilayotganini ko'rish
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Portlarni o'chirish
kill -9 <PID>
```

### Log fayllar

#### Backend logs
```bash
# Development
tail -f logs/app.log

# Docker
docker-compose logs backend
```

#### Frontend logs
```bash
# Browser console
# Developer Tools > Console
```

#### Database logs
```bash
# PostgreSQL
tail -f /var/log/postgresql/postgresql-15-main.log

# Supabase
supabase logs db
```

## 📚 Batafsil ma'lumot

- [API Documentation](API_DOCUMENTATION.md)
- [Frontend Guide](FRONTEND_GUIDE.md)
- [Backend Guide](BACKEND_GUIDE.md)
- [Deployment Guide](DEPLOYMENT.md)

## 🆘 Yordam olish

Agar muammo yuz bersa:

1. **Logs tekshirish**: `/logs/` papkasidagi fayllarni ko'ring
2. **Google qidirish**: Muammoni qidiring
3. **Issues oching**: [GitHub Issues](https://github.com/your-username/orion-starline/issues)
4. **Discussions**: [GitHub Discussions](https://github.com/your-username/orion-starline/discussions)

---

**Platform muvaffaqiyatli ishlashini tilaymiz! 🚀**