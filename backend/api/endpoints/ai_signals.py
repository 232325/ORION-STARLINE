"""
AI Trading System - AI Signals Endpoints
AI trading signals uchun RESTful API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import asyncio
from decimal import Decimal

from ..models.schemas import *
from ..auth.auth_handler import get_current_active_user
from ..utils.cache import cache_manager
from ..utils.pagination import paginate_response

router = APIRouter()

# In-memory storage (in production, use database)
ai_signals_db: Dict[str, Any] = {}
signal_history_db: Dict[str, List[Any]] = {}

# =============================================================================
# AI SIGNALS ENDPOINTS
# =============================================================================

@router.get("", response_model=AISignalListResponse)
async def get_ai_signals(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    symbol: Optional[str] = Query(None, description="Currency pair (e.g., BTC/USDT)"),
    signal_type: Optional[SignalType] = Query(None, description="Signal type"),
    min_confidence: Optional[float] = Query(None, ge=0, le=1, description="Minimum confidence level"),
    timeframe: Optional[str] = Query(None, description="Time frame"),
    current_user: User = Depends(get_current_active_user)
):
    """AI trading signals ro'yxatini olish"""
    
    # Get cached results or compute
    cache_key = f"ai_signals:{symbol}:{signal_type}:{min_confidence}:{timeframe}:{page}:{size}"
    cached_result = await cache_manager.get(cache_key)
    
    if cached_result:
        return cached_result
    
    # Filter signals
    filtered_signals = []
    for signal_id, signal in ai_signals_db.items():
        if symbol and signal.symbol != symbol:
            continue
        if signal_type and signal.signal_type != signal_type:
            continue
        if min_confidence and signal.confidence < min_confidence:
            continue
        if timeframe and signal.timeframe != timeframe:
            continue
        filtered_signals.append(signal)
    
    # Sort by created_at descending
    filtered_signals.sort(key=lambda x: x.created_at, reverse=True)
    
    # Paginate
    total = len(filtered_signals)
    start = (page - 1) * size
    end = start + size
    paginated_signals = filtered_signals[start:end]
    
    response = AISignalListResponse(
        signals=paginated_signals,
        pagination=PaginationInfo(
            page=page,
            size=size,
            total=total,
            pages=(total + size - 1) // size
        )
    )
    
    # Cache results
    await cache_manager.set(cache_key, response, ttl=300)  # 5 minutes
    
    return response

@router.post("", response_model=AISignalResponse, status_code=status.HTTP_201_CREATED)
async def create_ai_signal(
    signal_data: AISignalCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Yangi AI signal yaratish"""
    
    # Validate symbol format
    if not signal_data.symbol or "/" not in signal_data.symbol:
        raise HTTPException(
            status_code=400,
            detail="Symbol formati noto'g'ri (e.g., BTC/USDT)"
        )
    
    # Generate signal ID
    signal_id = str(uuid.uuid4())
    
    # Create AI signal
    signal = AISignal(
        id=signal_id,
        symbol=signal_data.symbol,
        signal_type=signal_data.signal_type,
        confidence=signal_data.confidence,
        price=signal_data.price,
        target_price=signal_data.target_price,
        stop_loss=signal_data.stop_loss,
        timeframe=signal_data.timeframe,
        model_version="v1.2.3",
        features={
            "rsi": 0.65,
            "macd": 0.78,
            "bollinger": 0.72,
            "volume": 0.85,
            "momentum": 0.69
        },
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    
    # Store in database
    ai_signals_db[signal_id] = signal
    
    # Add to history
    if signal.symbol not in signal_history_db:
        signal_history_db[signal.symbol] = []
    signal_history_db[signal.symbol].append(signal)
    
    # Background task to notify other systems
    background_tasks.add_task(process_ai_signal, signal)
    
    return AISignalResponse(
        signal=signal,
        message="AI signal muvaffaqiyatli yaratildi"
    )

@router.get("/{signal_id}", response_model=AISignalResponse)
async def get_ai_signal(
    signal_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """AI signalni ID bo'yicha olish"""
    
    if signal_id not in ai_signals_db:
        raise HTTPException(
            status_code=404,
            detail="AI signal topilmadi"
        )
    
    signal = ai_signals_db[signal_id]
    
    return AISignalResponse(signal=signal)

@router.put("/{signal_id}", response_model=AISignalResponse)
async def update_ai_signal(
    signal_id: str,
    signal_data: AISignalCreate,
    current_user: User = Depends(get_current_active_user)
):
    """AI signalni yangilash"""
    
    if signal_id not in ai_signals_db:
        raise HTTPException(
            status_code=404,
            detail="AI signal topilmadi"
        )
    
    existing_signal = ai_signals_db[signal_id]
    
    # Update fields
    existing_signal.signal_type = signal_data.signal_type
    existing_signal.confidence = signal_data.confidence
    existing_signal.price = signal_data.price
    existing_signal.target_price = signal_data.target_price
    existing_signal.stop_loss = signal_data.stop_loss
    existing_signal.timeframe = signal_data.timeframe
    
    return AISignalResponse(
        signal=existing_signal,
        message="AI signal muvaffaqiyatli yangilandi"
    )

@router.delete("/{signal_id}", response_model=BaseResponse)
async def delete_ai_signal(
    signal_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """AI signalni o'chirish"""
    
    if signal_id not in ai_signals_db:
        raise HTTPException(
            status_code=404,
            detail="AI signal topilmadi"
        )
    
    # Only admins can delete signals
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Faqat admin foydalanuvchilar signalni o'chira oladi"
        )
    
    # Remove from database
    signal = ai_signals_db.pop(signal_id)
    
    # Remove from history
    if signal.symbol in signal_history_db:
        signal_history_db[signal.symbol] = [
            s for s in signal_history_db[signal.symbol] 
            if s.id != signal_id
        ]
    
    return BaseResponse(
        message="AI signal muvaffaqiyatli o'chirildi"
    )

# =============================================================================
# BULK OPERATIONS
# =============================================================================

@router.post("/bulk", response_model=BulkOperationResponse)
async def create_bulk_ai_signals(
    request: BulkAISignalsRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Ko'plab AI signals yaratish"""
    
    operation_id = str(uuid.uuid4())
    
    # Background task to process bulk request
    background_tasks.add_task(process_bulk_ai_signals, operation_id, request)
    
    return BulkOperationResponse(
        operation_id=operation_id,
        status="processing",
        total_requests=len(request.symbols) * len(request.timeframes),
        processed=0,
        estimated_completion=datetime.utcnow() + timedelta(minutes=10),
        message="Bulk AI signals yaratish boshlandi"
    )

@router.get("/bulk/status/{operation_id}", response_model=BulkStatusResponse)
async def get_bulk_operation_status(
    operation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Bulk operatsiya holatini olish"""
    
    # In production, get from database
    return BulkStatusResponse(
        operation_id=operation_id,
        status="completed",
        progress=100,
        completed_items=10,
        failed_items=0,
        started_at=datetime.utcnow() - timedelta(minutes=5),
        completed_at=datetime.utcnow()
    )

# =============================================================================
# SIGNAL ANALYSIS & STATISTICS
# =============================================================================

@router.get("/analysis/symbol/{symbol}", response_model=Dict[str, Any])
async def get_symbol_analysis(
    symbol: str,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user)
):
    """Symbol bo'yicha tahlil ma'lumotlari"""
    
    if symbol not in signal_history_db:
        raise HTTPException(
            status_code=404,
            detail=f"{symbol} bo'yicha signal topilmadi"
        )
    
    signals = signal_history_db[symbol]
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Filter recent signals
    recent_signals = [
        s for s in signals 
        if s.created_at > cutoff_date
    ]
    
    if not recent_signals:
        return {
            "symbol": symbol,
            "total_signals": 0,
            "message": "Berilgan davrda signal topilmadi"
        }
    
    # Calculate statistics
    total_signals = len(recent_signals)
    buy_signals = len([s for s in recent_signals if s.signal_type == SignalType.BUY])
    sell_signals = len([s for s in recent_signals if s.signal_type == SignalType.SELL])
    hold_signals = len([s for s in recent_signals if s.signal_type == SignalType.HOLD])
    
    avg_confidence = sum(s.confidence for s in recent_signals) / total_signals
    
    # Success rate calculation (simplified)
    successful_signals = total_signals * 0.75  # Mock 75% success rate
    
    return {
        "symbol": symbol,
        "analysis_period_days": days,
        "total_signals": total_signals,
        "signal_distribution": {
            "buy": buy_signals,
            "sell": sell_signals,
            "hold": hold_signals
        },
        "average_confidence": round(avg_confidence, 3),
        "success_rate": round(successful_signals / total_signals, 3),
        "most_recent_signal": recent_signals[0].created_at.isoformat(),
        "most_active_timeframe": "1h" if total_signals > 5 else recent_signals[0].timeframe
    }

@router.get("/statistics/performance", response_model=Dict[str, Any])
async def get_performance_statistics(
    current_user: User = Depends(get_current_active_user)
):
    """AI signals umumiy statistikasi"""
    
    total_signals = len(ai_signals_db)
    
    if total_signals == 0:
        return {
            "total_signals": 0,
            "message": "Hali signal yaratilmagan"
        }
    
    # Calculate overall statistics
    total_confidence = sum(s.confidence for s in ai_signals_db.values())
    avg_confidence = total_confidence / total_signals
    
    signal_types = {}
    timeframes = {}
    
    for signal in ai_signals_db.values():
        # Count signal types
        signal_type = signal.signal_type.value
        signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
        
        # Count timeframes
        timeframe = signal.timeframe
        timeframes[timeframe] = timeframes.get(timeframe, 0) + 1
    
    return {
        "total_signals": total_signals,
        "average_confidence": round(avg_confidence, 3),
        "signal_types_distribution": signal_types,
        "timeframes_distribution": timeframes,
        "active_symbols": len(set(s.symbol for s in ai_signals_db.values())),
        "last_updated": datetime.utcnow().isoformat()
    }

# =============================================================================
# SIGNAL VALIDATION & FORECASTING
# =============================================================================

@router.post("/validate/{signal_id}", response_model=Dict[str, Any])
async def validate_signal(
    signal_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """AI signalni validatsiya qilish"""
    
    if signal_id not in ai_signals_db:
        raise HTTPException(
            status_code=404,
            detail="AI signal topilmadi"
        )
    
    signal = ai_signals_db[signal_id]
    
    # Mock validation logic
    validation_result = {
        "signal_id": signal_id,
        "is_valid": True,
        "confidence_score": signal.confidence,
        "validation_details": {
            "price_range_valid": True,
            "technical_indicators_aligned": signal.confidence > 0.7,
            "market_conditions_favorable": signal.confidence > 0.6,
            "risk_assessment": "LOW" if signal.confidence > 0.8 else "MEDIUM"
        },
        "recommendations": [
            "Signal is sufficiently confident for execution" if signal.confidence > 0.7 else "Monitor for higher confidence signals",
            f"Target: {signal.target_price}" if signal.target_price else "Set appropriate targets",
            f"Stop Loss: {signal.stop_loss}" if signal.stop_loss else "Consider setting stop loss"
        ],
        "validated_at": datetime.utcnow().isoformat()
    }
    
    return validation_result

# =============================================================================
# BACKGROUND TASKS
# =============================================================================

async def process_ai_signal(signal: AISignal):
    """AI signalni qayta ishlash (background task)"""
    try:
        logger.info(f"AI signal qayta ishlanmoqda: {signal.id}")
        
        # Send to trading engine
        await send_to_trading_engine(signal)
        
        # Update cache
        await cache_manager.invalidate_pattern("ai_signals:*")
        
        logger.info(f"AI signal qayta ishlandi: {signal.id}")
    except Exception as e:
        logger.error(f"AI signal qayta ishlanganda xato: {e}")

async def process_bulk_ai_signals(operation_id: str, request: BulkAISignalsRequest):
    """Bulk AI signals qayta ishlash"""
    try:
        logger.info(f"Bulk operatsiya boshlandi: {operation_id}")
        
        total_operations = len(request.symbols) * len(request.timeframes)
        completed = 0
        
        for symbol in request.symbols:
            for timeframe in request.timeframes:
                # Generate signal for symbol/timeframe combination
                signal_data = AISignalCreate(
                    symbol=symbol,
                    signal_type=SignalType.BUY,  # Mock signal type
                    confidence=0.75 + (completed / total_operations) * 0.2,
                    price=Decimal("45000.00"),
                    timeframe=timeframe
                )
                
                # Create signal (simplified)
                signal_id = str(uuid.uuid4())
                signal = AISignal(
                    id=signal_id,
                    symbol=symbol,
                    signal_type=signal_data.signal_type,
                    confidence=signal_data.confidence,
                    price=signal_data.price,
                    timeframe=signal_data.timeframe,
                    model_version="v1.2.3",
                    features={"source": "bulk_operation"},
                    created_at=datetime.utcnow()
                )
                
                ai_signals_db[signal_id] = signal
                completed += 1
        
        logger.info(f"Bulk operatsiya yakunlandi: {operation_id}")
        
    except Exception as e:
        logger.error(f"Bulk operatsiya xatosi: {e}")

async def send_to_trading_engine(signal: AISignal):
    """Trading engine'ga signal yuborish"""
    # Mock implementation - in production, send to real trading system
    await asyncio.sleep(0.1)  # Simulate network delay

# Initialize with mock data
def init_mock_ai_signals():
    """Mock AI signals ma'lumotlarini yaratish"""
    if not ai_signals_db:
        symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT", "DOT/USDT", "LINK/USDT"]
        signal_types = list(SignalType)
        
        for i in range(20):
            symbol = symbols[i % len(symbols)]
            signal_id = str(uuid.uuid4())
            
            signal = AISignal(
                id=signal_id,
                symbol=symbol,
                signal_type=signal_types[i % len(signal_types)],
                confidence=0.6 + (i % 10) * 0.04,
                price=Decimal(str(45000 + i * 100)),
                target_price=Decimal(str(47000 + i * 100)),
                timeframe="1h" if i % 2 == 0 else "4h",
                model_version="v1.2.3",
                features={
                    "rsi": 0.5 + i * 0.05,
                    "macd": 0.6 + i * 0.04,
                    "volume": 0.7 + i * 0.03
                },
                created_at=datetime.utcnow() - timedelta(hours=i)
            )
            
            ai_signals_db[signal_id] = signal
            
            # Add to history
            if symbol not in signal_history_db:
                signal_history_db[symbol] = []
            signal_history_db[symbol].append(signal)

# Initialize mock data on module load
import logging
logger = logging.getLogger(__name__)
init_mock_ai_signals()