#!/bin/bash
echo "=== AI TRADING EVOLUTION - TO'LIQ STATISTIKA ==="
echo ""
echo "BOSQICH 1: Trading Strategiyalari"
wc -l advanced_strategies/*.py 2>/dev/null | tail -1
echo ""
echo "BOSQICH 2: Analytics"
wc -l analytics/*.py 2>/dev/null | tail -1
echo ""
echo "BOSQICH 4: Markets"
wc -l markets/*.py 2>/dev/null | tail -1
echo ""
echo "BOSQICH 5: ML Models"
wc -l ml/*.py 2>/dev/null | tail -1
echo ""
echo "BOSQICH 6: Integration"
wc -l integration/*.py 2>/dev/null | tail -1
echo ""
echo "BOSQICH 7: Production Deployment"
wc -l main.py Dockerfile docker-compose.yml requirements-prod.txt .env.example nginx/nginx.conf deploy.sh monitoring/prometheus.yml DEPLOYMENT_README.md PRODUCTION_README.md test_api.py 2>/dev/null | tail -1
