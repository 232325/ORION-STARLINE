#!/bin/bash

# AI Trading Backend - Render.com Deploy Script
# Bu script backend'ni Render.com'ga deploy qiladi

set -e

echo "================================================"
echo "AI Trading Backend - Render.com Deployment"
echo "================================================"

# Check if render CLI installed
if ! command -v render &> /dev/null; then
    echo "Render CLI topilmadi. O'rnatilmoqda..."
    curl -fsSL https://render.com/install-cli.sh | bash
fi

echo ""
echo "1. Render.com'ga kirish..."
echo "   render login"
echo ""

echo "2. Yangi web service yaratish..."
echo "   render create web --name ai-trading-backend \\"
echo "     --env python \\"
echo "     --build-command 'pip install -r requirements.txt' \\"
echo "     --start-command 'uvicorn main:app --host 0.0.0.0 --port \$PORT'"
echo ""

echo "3. Environment variables sozlash..."
echo "   render env set DEBUG=False"
echo "   render env set SECRET_KEY=<generate-random-key>"
echo "   render env set ALLOWED_ORIGINS='[\"https://096l9ute938z.space.minimax.io\"]'"
echo ""

echo "4. Deploy qilish..."
echo "   render deploy"
echo ""

echo "================================================"
echo "Manual Deploy (Recommended):"
echo "================================================"
echo ""
echo "1. https://render.com'ga kiring"
echo "2. 'New +' > 'Web Service'"
echo "3. GitHub repo'ni ulang yoki Manual deploy:"
echo "   - Name: ai-trading-backend"
echo "   - Environment: Docker"
echo "   - Branch: main"
echo "   - Dockerfile path: Dockerfile"
echo ""
echo "4. Environment variables qo'shing:"
echo "   DEBUG=False"
echo "   SECRET_KEY=<random-secret>"
echo "   ALLOWED_ORIGINS=[\"https://096l9ute938z.space.minimax.io\"]"
echo ""
echo "5. 'Create Web Service' tugmasini bosing"
echo ""
echo "6. Deploy tugallanganidan keyin URL oling:"
echo "   https://ai-trading-backend.onrender.com"
echo ""

echo "================================================"
echo "Railway.app Alternative:"
echo "================================================"
echo ""
echo "1. https://railway.app'ga kiring"
echo "2. 'New Project' > 'Deploy from GitHub repo'"
echo "3. Repo'ni tanlang"
echo "4. railway.json automatik o'qiladi"
echo "5. Environment variables sozlang"
echo "6. Deploy!"
echo ""

echo "================================================"
echo "Files ready:"
echo "================================================"
ls -la Dockerfile render.yaml railway.json .env.production 2>/dev/null || true
echo ""

echo "Next step: Deploy backend to Render.com or Railway.app"
echo "Then update frontend with backend URL"
