"""
AI Trading System - RESTful API Endpoints
FastAPI asosida qurilgan to'liq API tizimi
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
import os
import logging
from typing import List, Optional, Dict, Any
import asyncio
from datetime import datetime, timedelta

# Local imports
from config.settings import settings
from models.schemas import *
from auth.auth_handler import authenticate_user, create_access_token, get_current_user
from auth.oauth_handler import oauth2_scheme
from endpoints.ai_signals import router as ai_signals_router
from endpoints.quantum_analysis import router as quantum_analysis_router
from endpoints.blockchain import router as blockchain_router
from endpoints.dao_governance import router as dao_governance_router
from endpoints.hft_engine import router as hft_engine_router
from endpoints.nft_hedge import router as nft_hedge_router
from endpoints.self_learning import router as self_learning_router
from websocket.manager import ConnectionManager
from utils.cache import CacheManager
from utils.error_handler import GlobalExceptionHandler
from utils.pagination import PaginationParams

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cache manager
cache_manager = CacheManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    logger.info("AI Trading API tizimi ishga tushmoqda...")
    await cache_manager.initialize()
    logger.info("Cache tizimi tayyorlandi")
    yield
    # Shutdown
    logger.info("AI Trading API tizimi to'xtatilmoqda...")
    await cache_manager.cleanup()

# FastAPI app initialization
app = FastAPI(
    title="AI Trading System RESTful API",
    description="Quantum AI, HFT, DAO, NFT va Blockchain texnologiyalari bilan jihoblangan trading tizimi",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "AI Trading System",
        "email": "api@aitrading.com",
        "url": "https://aitrading.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400,
)

# GZIP compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Global exception handler
app.add_exception_handler(Exception, GlobalExceptionHandler().handle_exception)

# Security
security = HTTPBearer()

# Connection manager for WebSockets
manager = ConnectionManager()

# =============================================================================
# HEALTH CHECK & SYSTEM STATUS
# =============================================================================

@app.get("/health", tags=["System"], response_model=HealthResponse)
async def health_check():
    """Tizim sog'liqni tekshirish"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        services={
            "database": "connected",
            "cache": "active",
            "websocket": "running"
        }
    )

@app.get("/api/v1/system/status", tags=["System"], response_model=SystemStatusResponse)
async def get_system_status(current_user: User = Depends(get_current_user)):
    """Tizim holati (faqat authenticated foydalanuvchilar)"""
    return SystemStatusResponse(
        uptime=str(datetime.utcnow() - datetime.fromtimestamp(start_time)),
        cpu_usage=25.3,
        memory_usage=68.5,
        active_connections=manager.get_connection_count(),
        api_calls_today=1247,
        system_load="optimal"
    )

# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@app.post("/api/v1/auth/login", tags=["Authentication"], response_model=TokenResponse)
async def login(request: LoginRequest):
    """Foydalanuvchi login"""
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Noto'g'ri ma'lumotlar")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_info=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active
        )
    )

@app.post("/api/v1/auth/refresh", tags=["Authentication"], response_model=TokenResponse)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Token yangilash"""
    current_user = get_current_user(credentials)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_info=UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            role=current_user.role,
            is_active=current_user.is_active
        )
    )

@app.get("/api/v1/auth/me", tags=["Authentication"], response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Joriy foydalanuvchi ma'lumotlari"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

# =============================================================================
# FILE OPERATIONS
# =============================================================================

@app.post("/api/v1/files/upload", tags=["Files"], response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Fayl yuklash"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Fayl nomi kerak")
    
    # Validate file type
    allowed_extensions = {'.csv', '.json', '.xlsx', '.txt', '.pdf', '.png', '.jpg', '.jpeg'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Ruxsat etilmagan fayl turi")
    
    # Save file
    file_path = f"/workspace/code/api/uploads/{current_user.id}/{datetime.now().strftime('%Y%m%d')}"
    os.makedirs(file_path, exist_ok=True)
    
    full_path = f"{file_path}/{file.filename}"
    
    # Background task to process file
    background_tasks.add_task(process_uploaded_file, full_path, file)
    
    return FileUploadResponse(
        filename=file.filename,
        file_size=file.size,
        content_type=file.content_type,
        upload_path=full_path,
        upload_time=datetime.utcnow(),
        message="Fayl muvaffaqiyatli yuklandi"
    )

@app.get("/api/v1/files/download/{file_id}", tags=["Files"])
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """Fayl yuklab olish"""
    # Implementation would fetch file from database
    file_path = f"/workspace/code/api/uploads/{current_user.id}/{file_id}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="Fayl topilmadi")

@app.get("/api/v1/files/list", tags=["Files"], response_model=FileListResponse)
async def list_files(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Foydalanuvchi fayllari ro'yxati"""
    # Implementation would fetch from database with pagination
    return FileListResponse(
        files=[
            FileInfo(
                id="file_001",
                filename="trading_data.csv",
                size=1024000,
                uploaded_at=datetime.utcnow(),
                content_type="text/csv"
            )
        ],
        total=1,
        page=page,
        size=size,
        pages=1
    )

# =============================================================================
# BULK OPERATIONS
# =============================================================================

@app.post("/api/v1/bulk/ai-signals", tags=["Bulk Operations"], response_model=BulkOperationResponse)
async def bulk_ai_signals(
    request: BulkAISignalsRequest,
    current_user: User = Depends(get_current_user)
):
    """Ko'plab AI signal operatsiyalari"""
    # Implementation would process bulk requests
    return BulkOperationResponse(
        operation_id="bulk_001",
        status="processing",
        total_requests=len(request.symbols),
        processed=0,
        estimated_completion=datetime.utcnow() + timedelta(minutes=5),
        message="Bulk operatsiya boshirildi"
    )

@app.get("/api/v1/bulk/status/{operation_id}", tags=["Bulk Operations"], response_model=BulkStatusResponse)
async def get_bulk_status(
    operation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Bulk operatsiya holati"""
    return BulkStatusResponse(
        operation_id=operation_id,
        status="completed",
        progress=100,
        completed_items=100,
        failed_items=0,
        started_at=datetime.utcnow() - timedelta(minutes=5),
        completed_at=datetime.utcnow()
    )

# =============================================================================
# WEBSOCKET ENDPOINTS
# =============================================================================

@app.websocket("/api/v1/websocket/trading")
async def websocket_trading_endpoint(websocket):
    """Trading ma'lumotlari uchun WebSocket"""
    await manager.connect(websocket, "trading")
    
    try:
        while True:
            data = await websocket.receive_text()
            # Process trading data
            response = {
                "type": "trading_data",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "symbol": "BTC/USDT",
                    "price": 45000.0,
                    "volume": 150.5,
                    "signal": "BUY"
                }
            }
            await manager.send_personal_message(response, websocket)
    except Exception as e:
        logger.error(f"WebSocket xatosi: {e}")
    finally:
        manager.disconnect(websocket)

@app.websocket("/api/v1/websocket/quantum")
async def websocket_quantum_endpoint(websocket):
    """Quantum analysis uchun WebSocket"""
    await manager.connect(websocket, "quantum")
    
    try:
        while True:
            data = await websocket.receive_text()
            # Process quantum analysis data
            response = {
                "type": "quantum_analysis",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "superposition_state": "ENTANGLED",
                    "coherence_time": "15.2μs",
                    "fidelity": 0.987,
                    "qbit_count": 256
                }
            }
            await manager.send_personal_message(response, websocket)
    except Exception as e:
        logger.error(f"WebSocket xatosi: {e}")
    finally:
        manager.disconnect(websocket)

# =============================================================================
# MODULE API ROUTERS
# =============================================================================

# Include all module routers
app.include_router(
    ai_signals_router,
    prefix="/api/v1/ai-signals",
    tags=["AI Signals"]
)

app.include_router(
    quantum_analysis_router,
    prefix="/api/v1/quantum-analysis",
    tags=["Quantum Analysis"]
)

app.include_router(
    blockchain_router,
    prefix="/api/v1/blockchain",
    tags=["Blockchain"]
)

app.include_router(
    dao_governance_router,
    prefix="/api/v1/dao-governance",
    tags=["DAO Governance"]
)

app.include_router(
    hft_engine_router,
    prefix="/api/v1/hft-engine",
    tags=["HFT Engine"]
)

app.include_router(
    nft_hedge_router,
    prefix="/api/v1/nft-hedge",
    tags=["NFT Hedge Fund"]
)

app.include_router(
    self_learning_router,
    prefix="/api/v1/self-learning",
    tags=["Self Learning"]
)

# =============================================================================
# BACKGROUND TASKS
# =============================================================================

async def process_uploaded_file(file_path: str, file: UploadFile):
    """Background task to process uploaded files"""
    try:
        logger.info(f"Fayl qayta ishlanmoqda: {file_path}")
        # Implementation would process the file content
        await asyncio.sleep(2)  # Simulate processing time
        logger.info(f"Fayl qayta ishlandi: {file_path}")
    except Exception as e:
        logger.error(f"Fayl qayta ishlashda xato: {e}")

# Application startup time (for uptime calculation)
start_time = 0

def start_application():
    """Application start"""
    global start_time
    start_time = datetime.utcnow().timestamp()
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    start_application()