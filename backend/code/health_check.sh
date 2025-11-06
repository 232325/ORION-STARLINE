#!/bin/bash

# =============================================================================
# AI Trading Platform - Health Check Script
# =============================================================================
# This script checks the health status of all services in the Docker Compose setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "OK" ]; then
        echo -e "${GREEN}✓${NC} $message"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}✗${NC} $message"
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠${NC} $message"
    else
        echo -e "${BLUE}ℹ${NC} $message"
    fi
}

# Function to check if service is running
check_service() {
    local service_name=$1
    if docker-compose ps | grep -q "$service_name.*Up"; then
        return 0
    else
        return 1
    fi
}

# Function to check HTTP endpoint
check_http() {
    local url=$1
    local timeout=5
    if curl -s --max-time $timeout "$url" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check TCP port
check_port() {
    local port=$1
    local timeout=5
    if nc -z localhost $port > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

echo -e "${BLUE}===================================================================${NC}"
echo -e "${BLUE}AI Trading Platform - Health Check${NC}"
echo -e "${BLUE}===================================================================${NC}"
echo ""

# Check if docker-compose is running
echo -e "${BLUE}📋 Checking Docker Compose Status...${NC}"
if ! docker-compose ps > /dev/null 2>&1; then
    print_status "FAIL" "Docker Compose is not running"
    exit 1
fi
print_status "OK" "Docker Compose is running"
echo ""

# Check core services
echo -e "${BLUE}🏗️  Checking Core Services...${NC}"

# API Service
if check_service "ai-trading-api"; then
    print_status "OK" "FastAPI service is running"
    if check_http "http://localhost:8000/health"; then
        print_status "OK" "API health endpoint accessible"
    else
        print_status "WARN" "API health endpoint not accessible"
    fi
else
    print_status "FAIL" "FastAPI service is not running"
fi

# PostgreSQL
if check_service "ai-trading-postgres"; then
    print_status "OK" "PostgreSQL service is running"
    if check_port 5432; then
        print_status "OK" "PostgreSQL port 5432 is accessible"
    else
        print_status "WARN" "PostgreSQL port 5432 is not accessible"
    fi
else
    print_status "FAIL" "PostgreSQL service is not running"
fi

# Redis
if check_service "ai-trading-redis"; then
    print_status "OK" "Redis service is running"
    if check_port 6379; then
        print_status "OK" "Redis port 6379 is accessible"
    else
        print_status "WARN" "Redis port 6379 is not accessible"
    fi
else
    print_status "FAIL" "Redis service is not running"
fi

# RabbitMQ
if check_service "ai-trading-rabbitmq"; then
    print_status "OK" "RabbitMQ service is running"
    if check_port 5672; then
        print_status "OK" "RabbitMQ port 5672 is accessible"
    else
        print_status "WARN" "RabbitMQ port 5672 is not accessible"
    fi
    if check_port 15672; then
        print_status "OK" "RabbitMQ Management UI accessible"
    else
        print_status "WARN" "RabbitMQ Management UI not accessible"
    fi
else
    print_status "FAIL" "RabbitMQ service is not running"
fi

echo ""

# Check monitoring services
echo -e "${BLUE}📊 Checking Monitoring Services...${NC}"

# Prometheus
if check_service "ai-trading-prometheus"; then
    print_status "OK" "Prometheus service is running"
    if check_port 9090; then
        print_status "OK" "Prometheus port 9090 is accessible"
    else
        print_status "WARN" "Prometheus port 9090 is not accessible"
    fi
else
    print_status "FAIL" "Prometheus service is not running"
fi

# Grafana
if check_service "ai-trading-grafana"; then
    print_status "OK" "Grafana service is running"
    if check_port 3001; then
        print_status "OK" "Grafana port 3001 is accessible"
    else
        print_status "WARN" "Grafana port 3001 is not accessible"
    fi
else
    print_status "FAIL" "Grafana service is not running"
fi

# Elasticsearch
if check_service "ai-trading-elasticsearch"; then
    print_status "OK" "Elasticsearch service is running"
    if check_port 9200; then
        print_status "OK" "Elasticsearch port 9200 is accessible"
    else
        print_status "WARN" "Elasticsearch port 9200 is not accessible"
    fi
else
    print_status "FAIL" "Elasticsearch service is not running"
fi

# Kibana
if check_service "ai-trading-kibana"; then
    print_status "OK" "Kibana service is running"
    if check_port 5601; then
        print_status "OK" "Kibana port 5601 is accessible"
    else
        print_status "WARN" "Kibana port 5601 is not accessible"
    fi
else
    print_status "FAIL" "Kibana service is not running"
fi

echo ""

# Check worker services
echo -e "${BLUE}⚙️  Checking Worker Services...${NC}"

# Worker
if check_service "ai-trading-worker"; then
    print_status "OK" "Worker service is running"
else
    print_status "FAIL" "Worker service is not running"
fi

# Flower
if check_service "ai-trading-flower"; then
    print_status "OK" "Flower service is running"
    if check_port 5555; then
        print_status "OK" "Flower port 5555 is accessible"
    else
        print_status "WARN" "Flower port 5555 is not accessible"
    fi
else
    print_status "FAIL" "Flower service is not running"
fi

echo ""

# Check proxy service
echo -e "${BLUE}🔀 Checking Proxy Services...${NC}"

# Nginx
if check_service "ai-trading-nginx"; then
    print_status "OK" "Nginx service is running"
    if check_port 80; then
        print_status "OK" "Nginx HTTP port 80 is accessible"
    else
        print_status "WARN" "Nginx HTTP port 80 is not accessible"
    fi
else
    print_status "FAIL" "Nginx service is not running"
fi

echo ""

# Summary
echo -e "${BLUE}===================================================================${NC}"
echo -e "${BLUE}Health Check Summary${NC}"
echo -e "${BLUE}===================================================================${NC}"

# Count running services
total_services=$(docker-compose ps -q | wc -l)
running_services=$(docker-compose ps | grep "Up" | wc -l)

echo -e "${GREEN}Running Services: $running_services/$total_services${NC}"
echo ""

# Print service URLs
echo -e "${BLUE}🌐 Service URLs:${NC}"
echo -e "  API:           ${GREEN}http://localhost:8000${NC}"
echo -e "  API Docs:      ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  Grafana:       ${GREEN}http://localhost:3001${NC} (admin/admin)"
echo -e "  Prometheus:    ${GREEN}http://localhost:9090${NC}"
echo -e "  Kibana:        ${GREEN}http://localhost:5601${NC}"
echo -e "  RabbitMQ MGMT: ${GREEN}http://localhost:15672${NC}"
echo -e "  Flower:        ${GREEN}http://localhost:5555${NC}"
echo ""

# Check for any failed services
failed_services=$(docker-compose ps | grep "Exit\|error" | wc -l)
if [ $failed_services -gt 0 ]; then
    print_status "WARN" "Some services have failed. Check logs with: docker-compose logs [service-name]"
fi

echo -e "${BLUE}For detailed logs run: docker-compose logs -f${NC}"
echo -e "${BLUE}To restart services: docker-compose restart${NC}"
echo -e "${BLUE}===================================================================${NC}"