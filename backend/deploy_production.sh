#!/bin/bash
"""
AI Trading Evolution - Production Deployment Script
=================================================

Bu script AI Trading Evolution platformini production environmentga deploy qilish uchun

Author: MiniMax Agent
Version: 1.0.0
Date: 2025-11-04
"""

set -e

echo "🚀 AI Trading Evolution Platform - Production Deployment"
echo "========================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ai-trading-evolution"
DOCKER_IMAGE="${PROJECT_NAME}:latest"
PORT=8000
HEALTH_CHECK_PORT=8001

# Check if environment file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️ .env fayl topilmadi. .env.example dan nusxa olinmoqda...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Iltimos, .env faylini tahrirlang va kerakli API kalitlarni qo'shing${NC}"
    echo -e "${YELLOW}📖 Batafsil ma'lumot: .env.example faylini o'qib ko'ring${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Konfiguratsiya tekshiruvi...${NC}"

# Load environment variables
source .env

# Check critical environment variables
CRITICAL_VARS=("SUPABASE_URL" "SUPABASE_ANON_KEY")
for var in "${CRITICAL_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ ${var} environment variable topilmadi${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Environment variables tekshirildi${NC}"

# Install dependencies
echo -e "${BLUE}📦 Dependencies o'rnatilmoqda...${NC}"
if command -v pip &> /dev/null; then
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencies o'rnatildi${NC}"
else
    echo -e "${YELLOW}⚠️ pip topilmadi. Python dependencies o'rnatilmadi${NC}"
fi

# Build Docker image
echo -e "${BLUE}🐳 Docker image build qilinmoqda...${NC}"
docker build -t "${DOCKER_IMAGE}" .
echo -e "${GREEN}✅ Docker image tayyor${NC}"

# Stop existing containers
echo -e "${BLUE}🛑 Mavjud containerlarni tozalash...${NC}"
docker-compose down --remove-orphans || true
echo -e "${GREEN}✅ Containerlar tozalandi${NC}"

# Start services
echo -e "${BLUE}🚀 Services ishga tushirilmoqda...${NC}"
docker-compose up -d --build

# Wait for services to be ready
echo -e "${BLUE}⏳ Services tayyor bo'lishini kutish...${NC}"
sleep 10

# Health check
echo -e "${BLUE}🔍 Health check bajarilmoqda...${NC}"
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f -s http://localhost:${PORT}/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API server tayyor!${NC}"
        break
    else
        echo -e "${YELLOW}⏳ Health check (${attempt}/${max_attempts})...${NC}"
        sleep 5
        ((attempt++))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo -e "${RED}❌ Health check muvaffaqiyatsiz. Server ishlamayapti${NC}"
    echo -e "${BLUE}📋 Logs ko'rish:${NC}"
    docker-compose logs api
    exit 1
fi

# Get API information
echo -e "${BLUE}📊 API ma'lumotlari:${NC}"
API_URL="http://localhost:${PORT}"
DOCS_URL="${API_URL}/docs"
HEALTH_URL="${API_URL}/health"
METRICS_URL="${API_URL}/metrics"

echo -e "${GREEN}🌐 API URL: ${API_URL}${NC}"
echo -e "${GREEN}📚 API Docs: ${DOCS_URL}${NC}"
echo -e "${GREEN}💚 Health Check: ${HEALTH_URL}${NC}"
echo -e "${GREEN}📈 Metrics: ${METRICS_URL}${NC}"

# Display container status
echo -e "${BLUE}📋 Container Status:${NC}"
docker-compose ps

# Display resource usage
echo -e "${BLUE}💻 Resource Usage:${NC}"
docker stats --no-stream

# Final message
echo ""
echo -e "${GREEN}🎉 DEPLOYMENT MUVAFFAQIYATLI!${NC}"
echo "=================================="
echo -e "${GREEN}✅ AI Trading Evolution Platform production environmentga tayyor!${NC}"
echo ""
echo -e "${BLUE}📋 Foydali buyruqlar:${NC}"
echo "  - Logs ko'rish:     docker-compose logs -f"
echo "  - Restart qilish:   docker-compose restart"
echo "  - Tozalash:        docker-compose down"
echo "  - API test:        curl ${HEALTH_URL}"
echo ""
echo -e "${YELLOW}⚠️ Muhim eslatma:${NC}"
echo "  - Production uchun SSL sertifikatni sozlash kerak"
echo "  - Load balancer (nginx) qo'shish kerak"
echo "  - Monitoring va logging tizimlarini yo'lga qo'yish kerak"
echo ""

# Save deployment info
echo "${API_URL}" > deploy_url.txt
echo "${PROJECT_NAME}" > project_name.txt
date > deployment_timestamp.txt

echo -e "${GREEN}📄 Deployment ma'lumotlari saqlandi:${NC}"
echo "  - deploy_url.txt: API URL"
echo "  - project_name.txt: Project nomi"
echo "  - deployment_timestamp.txt: Deployment vaqti"
