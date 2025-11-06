#!/usr/bin/env python3
"""
AI Trading System - API Server Runner
API server'ni ishga tushirish skripti
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from code.api.main import app

def main():
    """Main function to run the API server"""
    print("🚀 AI Trading System RESTful API ishga tushmoqda...")
    print("📚 API Documentation: http://localhost:8000/api/docs")
    print("🔍 ReDoc Documentation: http://localhost:8000/api/redoc")
    print("❤️  Health Check: http://localhost:8000/health")
    print("-" * 60)
    
    # Run the server
    uvicorn.run(
        "code.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()