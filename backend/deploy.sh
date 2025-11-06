#!/bin/bash

# =============================================================================
# AI Trading Evolution - Production Deployment Script
# =============================================================================
# Automated deployment script for production environment
# Author: MiniMax Agent
# Version: 1.0.0
# Date: 2025-11-04
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
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

# =============================================================================
# Pre-flight checks
# =============================================================================
log_info "🚀 AI Trading Evolution - Production Deployment"
log_info "================================================"

# Check Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker topilmadi. Iltimos, Docker o'rnating: https://docs.docker.com/get-docker/"
    exit 1
fi
log_success "Docker topildi: $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose topilmadi. Iltimos, Docker Compose o'rnating."
    exit 1
fi
log_success "Docker Compose topildi: $(docker-compose --version)"

# Check .env file
if [ ! -f .env ]; then
    log_warning ".env fayli topilmadi. .env.example'dan nusxa olinmoqda..."
    cp .env.example .env
    log_warning "Iltimos, .env faylini to'ldiring va qayta ishga tushiring."
    exit 1
fi
log_success ".env fayli topildi"

# =============================================================================
# Create necessary directories
# =============================================================================
log_info "📁 Kerakli papkalar yaratilmoqda..."
mkdir -p logs/nginx
mkdir -p data
mkdir -p nginx/ssl
mkdir -p monitoring/grafana/{dashboards,datasources}
log_success "Papkalar yaratildi"

# =============================================================================
# Build Docker images
# =============================================================================
log_info "🏗️  Docker image'lar build qilinmoqda..."
docker-compose build --no-cache
log_success "Docker image'lar tayyor"

# =============================================================================
# Start services
# =============================================================================
log_info "🚀 Servislar ishga tushirilmoqda..."
docker-compose up -d
log_success "Servislar ishga tushdi"

# =============================================================================
# Wait for services to be healthy
# =============================================================================
log_info "⏳ Servislar tayyor bo'lishi kutilmoqda..."
sleep 10

# Check API health
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "API server tayyor!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    log_info "Kutilmoqda... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    log_error "API server ishga tushmadi. Loglarni tekshiring:"
    docker-compose logs api
    exit 1
fi

# =============================================================================
# Display information
# =============================================================================
echo ""
log_success "✅ Deployment muvaffaqiyatli yakunlandi!"
echo ""
log_info "📊 Servis URL'lari:"
echo "   • API Server:     http://localhost:8000"
echo "   • API Docs:       http://localhost:8000/docs"
echo "   • Health Check:   http://localhost:8000/health"
echo "   • Prometheus:     http://localhost:9090"
echo "   • Grafana:        http://localhost:3001 (admin/admin)"
echo ""
log_info "🔧 Boshqarish buyruqlari:"
echo "   • Loglarni ko'rish:       docker-compose logs -f"
echo "   • Statusni tekshirish:    docker-compose ps"
echo "   • To'xtatish:             docker-compose down"
echo "   • Qayta ishga tushirish:  docker-compose restart"
echo ""
log_info "📚 Qo'shimcha ma'lumot uchun README.md faylini o'qing"
echo ""

# =============================================================================
# Optional: Run health checks
# =============================================================================
log_info "🏥 Health check bajarilmoqda..."

# API Health
API_HEALTH=$(curl -s http://localhost:8000/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
if [ "$API_HEALTH" == "healthy" ]; then
    log_success "API Server: HEALTHY ✅"
else
    log_warning "API Server: $API_HEALTH ⚠️"
fi

# Redis Health
if docker-compose exec -T redis redis-cli ping &> /dev/null; then
    log_success "Redis Cache: HEALTHY ✅"
else
    log_warning "Redis Cache: UNHEALTHY ⚠️"
fi

echo ""
log_success "🎉 AI Trading Evolution ishga tushdi va ishlashga tayyor!"
