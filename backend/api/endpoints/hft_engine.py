"""
AI Trading System - HFT Engine Endpoints
High-Frequency Trading engine uchun RESTful API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import asyncio
import numpy as np
from decimal import Decimal

from ..models.schemas import *
from ..auth.auth_handler import get_current_active_user, get_current_admin_user
from ..utils.cache import cache_manager

router = APIRouter()

# HFT data storage
trades_db: Dict[str, Any] = {}
strategies_db: Dict[str, Any] = {}
performance_metrics_db: Dict[str, Any] = {}
market_data_db: Dict[str, Any] = {}

# HFT Configuration
hft_config = {
    "max_latency_microseconds": 50,
    "min_profit_threshold": Decimal("0.01"),
    "max_position_size": Decimal("100000"),
    "symbols_supported": ["BTC/USDT", "ETH/USDT", "ADA/USDT", "DOT/USDT", "LINK/USDT"],
    "execution_venues": ["BINANCE", "COINBASE", "KRAKEN"],
    "risk_limits": {
        "max_daily_loss": Decimal("10000"),
        "max_position_exposure": Decimal("50000"),
        "max_drawdown": Decimal("0.05")  # 5%
    }
}

# Current HFT status
hft_status = {
    "is_running": True,
    "active_strategies": 3,
    "total_trades_today": 1247,
    "profit_loss_today": Decimal("2347.50"),
    "average_latency": 12.3,
    "success_rate": 0.847,
    "last_updated": datetime.utcnow()
}

# =============================================================================
# HFT TRADING OPERATIONS
# =============================================================================

@router.get("/trades", response_model=HFTTradeListResponse)
async def get_hft_trades(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    symbol: Optional[str] = Query(None),
    status: Optional[TradeStatus] = Query(None),
    strategy: Optional[str] = Query(None),
    time_from: Optional[datetime] = Query(None),
    time_to: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_active_user)
):
    """HFT trade operatsiyalari ro'yxati"""
    
    # Filter trades
    filtered_trades = []
    for trade_id, trade in trades_db.items():
        if symbol and trade.symbol != symbol:
            continue
        if status and trade.status != status:
            continue
        if strategy and trade.get("strategy") != strategy:
            continue
        if time_from and trade.created_at < time_from:
            continue
        if time_to and trade.created_at > time_to:
            continue
        filtered_trades.append(trade)
    
    # Sort by created_at descending
    filtered_trades.sort(key=lambda x: x.created_at, reverse=True)
    
    # Paginate
    total = len(filtered_trades)
    start = (page - 1) * size
    end = start + size
    paginated_trades = filtered_trades[start:end]
    
    return HFTTradeListResponse(
        trades=paginated_trades,
        pagination=PaginationInfo(
            page=page,
            size=size,
            total=total,
            pages=(total + size - 1) // size
        )
    )

@router.post("/trades", response_model=HFTTradeResponse, status_code=status.HTTP_201_CREATED)
async def create_hft_trade(
    trade_data: HFTTradeCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Yangi HFT trade yaratish"""
    
    # Validate symbol
    if trade_data.symbol not in hft_config["symbols_supported"]:
        raise HTTPException(
            status_code=400,
            detail=f"Qo'llab-quvvatlanmaydigan symbol: {trade_data.symbol}"
        )
    
    # Check risk limits
    total_exposure = get_current_position_exposure(trade_data.symbol)
    new_exposure = total_exposure + trade_data.quantity
    
    if new_exposure > hft_config["max_position_size"]:
        raise HTTPException(
            status_code=400,
            detail="Maksimal pozitsiya limiti oshib ketdi"
        )
    
    # Create HFT trade
    trade_id = str(uuid.uuid4())
    trade = HFTTrade(
        id=trade_id,
        symbol=trade_data.symbol,
        side=trade_data.side,
        quantity=trade_data.quantity,
        price=trade_data.price,
        execution_time=0,  # Will be updated after execution
        latency=0,  # Will be measured during execution
        status=TradeStatus.PENDING,
        created_at=datetime.utcnow(),
        strategy=get_best_strategy(trade_data.symbol, trade_data.quantity)
    )
    
    # Store trade
    trades_db[trade_id] = trade
    
    # Execute trade with minimal latency
    background_tasks.add_task(execute_hft_trade, trade_id, trade)
    
    return HFTTradeResponse(
        trade=trade,
        message="HFT trade muvaffaqiyatli yaratildi"
    )

@router.get("/trades/{trade_id}", response_model=Dict[str, Any])
async def get_hft_trade_details(
    trade_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Trade tafsilotlarini olish"""
    
    if trade_id not in trades_db:
        raise HTTPException(
            status_code=404,
            detail="Trade topilmadi"
        )
    
    trade = trades_db[trade_id]
    
    # Get additional trade details
    return {
        "trade": trade,
        "execution_details": {
            "venue": np.random.choice(hft_config["execution_venues"]),
            "order_book_depth": 15,
            "market_impact": "minimal",
            "slippage": Decimal("0.001"),
            "execution_quality": "excellent"
        },
        "strategy_info": {
            "strategy_name": trade.get("strategy", "default"),
            "algorithm": "ml_latency_optimized",
            "parameters": {
                "max_latency": hft_config["max_latency_microseconds"],
                "profit_target": hft_config["min_profit_threshold"],
                "stop_loss": trade.price * Decimal("0.99")
            }
        },
        "risk_metrics": {
            "var_95": Decimal("125.50"),
            "expected_shortfall": Decimal("187.30"),
            "sharpe_ratio": 2.34,
            "max_drawdown": Decimal("0.02")
        }
    }

@router.post("/trades/{trade_id}/cancel", response_model=BaseResponse)
async def cancel_hft_trade(
    trade_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """HFT tradeni bekor qilish"""
    
    if trade_id not in trades_db:
        raise HTTPException(
            status_code=404,
            detail="Trade topilmadi"
        )
    
    trade = trades_db[trade_id]
    
    if trade.status != TradeStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Faqat pending trade'lar bekor qilinishi mumkin"
        )
    
    # Cancel the trade
    trade.status = TradeStatus.CANCELLED
    
    return BaseResponse(
        message="Trade muvaffaqiyatli bekor qilindi"
    )

# =============================================================================
# HFT STRATEGIES
# =============================================================================

@router.get("/strategies", response_model=Dict[str, Any])
async def get_hft_strategies(
    active_only: bool = Query(False),
    current_user: User = Depends(get_current_active_user)
):
    """HFT strategialari ro'yxati"""
    
    # Filter strategies
    filtered_strategies = []
    for strategy_id, strategy in strategies_db.items():
        if active_only and not strategy.get("is_active", False):
            continue
        filtered_strategies.append(strategy)
    
    return {
        "strategies": filtered_strategies,
        "total": len(filtered_strategies),
        "active_count": len([s for s in filtered_strategies if s.get("is_active", False)])
    }

@router.post("/strategies", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_hft_strategy(
    strategy_data: Dict[str, Any],
    current_user: User = Depends(get_current_admin_user)
):
    """Yangi HFT strategiya yaratish"""
    
    strategy_id = str(uuid.uuid4())
    
    strategy = {
        "id": strategy_id,
        "name": strategy_data.get("name"),
        "description": strategy_data.get("description"),
        "parameters": strategy_data.get("parameters", {}),
        "is_active": False,
        "performance": {
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0
        },
        "created_at": datetime.utcnow(),
        "created_by": current_user.username
    }
    
    strategies_db[strategy_id] = strategy
    
    return {
        "strategy": strategy,
        "message": "HFT strategiya muvaffaqiyatli yaratildi"
    }

@router.put("/strategies/{strategy_id}/activate", response_model=BaseResponse)
async def activate_strategy(
    strategy_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Strategiyani aktivlash"""
    
    if strategy_id not in strategies_db:
        raise HTTPException(
            status_code=404,
            detail="Strategiya topilmadi"
        )
    
    strategy = strategies_db[strategy_id]
    strategy["is_active"] = True
    
    return BaseResponse(
        message="Strategiya muvaffaqiyatli aktivlashtirildi"
    )

# =============================================================================
# PERFORMANCE METRICS
# =============================================================================

@router.get("/metrics", response_model=HFTMetrics)
async def get_hft_metrics(
    time_period: str = Query("24h", description="Time period: 1h, 4h, 24h, 7d"),
    symbol: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user)
):
    """HFT performance metrikalar"""
    
    # Calculate metrics based on time period
    period_hours = {
        "1h": 1,
        "4h": 4,
        "24h": 24,
        "7d": 168
    }.get(time_period, 24)
    
    cutoff_time = datetime.utcnow() - timedelta(hours=period_hours)
    
    # Filter trades for the period
    period_trades = [
        trade for trade in trades_db.values()
        if trade.created_at > cutoff_time
        and (not symbol or trade.symbol == symbol)
    ]
    
    if not period_trades:
        return HFTMetrics(
            total_trades=0,
            successful_trades=0,
            failed_trades=0,
            average_latency=0.0,
            max_latency=0.0,
            min_latency=0.0,
            profit_loss=Decimal("0"),
            sharpe_ratio=0.0,
            win_rate=0.0
        )
    
    # Calculate metrics
    total_trades = len(period_trades)
    successful_trades = len([t for t in period_trades if t.status == TradeStatus.EXECUTED])
    failed_trades = total_trades - successful_trades
    
    latencies = [t.latency for t in period_trades if t.latency > 0]
    profit_losses = [t.profit_loss or Decimal("0") for t in period_trades if t.profit_loss is not None]
    
    avg_latency = np.mean(latencies) if latencies else 0.0
    max_latency = np.max(latencies) if latencies else 0.0
    min_latency = np.min(latencies) if latencies else 0.0
    
    total_pnl = sum(profit_losses)
    win_rate = successful_trades / total_trades if total_trades > 0 else 0.0
    
    # Mock Sharpe ratio calculation
    sharpe_ratio = np.random.uniform(1.5, 3.0)
    
    return HFTMetrics(
        total_trades=total_trades,
        successful_trades=successful_trades,
        failed_trades=failed_trades,
        average_latency=avg_latency,
        max_latency=max_latency,
        min_latency=min_latency,
        profit_loss=total_pnl,
        sharpe_ratio=sharpe_ratio,
        win_rate=win_rate
    )

@router.get("/metrics/detailed", response_model=Dict[str, Any])
async def get_detailed_metrics(
    time_period: str = Query("24h"),
    strategy: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user)
):
    """Batafsil performance metrikalar"""
    
    # Mock detailed metrics
    return {
        "period": time_period,
        "strategy_filter": strategy,
        "core_metrics": {
            "total_trades": 1247,
            "executed_trades": 1056,
            "cancelled_trades": 124,
            "failed_trades": 67,
            "success_rate": 0.847
        },
        "latency_metrics": {
            "average_latency_microseconds": 12.3,
            "median_latency_microseconds": 11.8,
            "p99_latency_microseconds": 25.4,
            "max_latency_microseconds": 47.2
        },
        "profit_metrics": {
            "gross_profit": "15,430.50",
            "gross_loss": "-8,245.20",
            "net_profit": "7,185.30",
            "profit_factor": 1.87,
            "return_on_capital": "14.37%"
        },
        "risk_metrics": {
            "max_drawdown": "2.34%",
            "var_95": "1,245.60",
            "expected_shortfall": "1,567.30",
            "sharpe_ratio": 2.34,
            "sortino_ratio": 3.21
        },
        "market_impact": {
            "average_slippage": "0.012%",
            "market_impact_cost": "234.50",
            "execution_quality_score": 9.2
        },
        "venue_performance": {
            "BINANCE": {"trades": 456, "latency": 11.2, "success_rate": 0.91},
            "COINBASE": {"trades": 321, "latency": 13.8, "success_rate": 0.83},
            "KRAKEN": {"trades": 279, "latency": 12.1, "success_rate": 0.87}
        }
    }

@router.get("/metrics/real-time", response_model=Dict[str, Any])
async def get_real_time_metrics(current_user: User = Depends(get_current_active_user)):
    """Real-time HFT metrikalar"""
    
    # Update current status
    hft_status.update({
        "active_strategies": len([s for s in strategies_db.values() if s.get("is_active", False)]),
        "total_trades_today": len([t for t in trades_db.values() if t.created_at.date() == datetime.utcnow().date()]),
        "average_latency": np.random.uniform(10, 15),
        "success_rate": np.random.uniform(0.83, 0.87),
        "last_updated": datetime.utcnow()
    })
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "hft_status": hft_status,
        "live_metrics": {
            "trades_per_second": 15.7,
            "orders_in_flight": 23,
            "average_queue_time": 0.003,  # seconds
            "cpu_utilization": 67.3,
            "memory_utilization": 45.8,
            "network_latency": 1.2  # milliseconds
        },
        "risk_exposure": {
            "total_exposure": "45,230.50",
            "per_symbol": {
                "BTC/USDT": "18,450.20",
                "ETH/USDT": "15,670.30",
                "ADA/USDT": "11,110.00"
            }
        },
        "venue_status": {
            "BINANCE": {"status": "connected", "latency": 11.2, "throughput": "high"},
            "COINBASE": {"status": "connected", "latency": 13.8, "throughput": "medium"},
            "KRAKEN": {"status": "connected", "latency": 12.1, "throughput": "medium"}
        }
    }

# =============================================================================
# MARKET DATA & ORDER BOOK
# =============================================================================

@router.get("/market-data/{symbol}", response_model=Dict[str, Any])
async def get_market_data(
    symbol: str,
    current_user: User = Depends(get_current_active_user)
):
    """Market data olish"""
    
    if symbol not in hft_config["symbols_supported"]:
        raise HTTPException(
            status_code=400,
            detail=f"Qo'llab-quvvatlanmaydigan symbol: {symbol}"
        )
    
    # Mock market data
    base_price = 45000.0 if symbol.startswith("BTC") else (2800.0 if symbol.startswith("ETH") else 1.5)
    price_variation = np.random.uniform(-0.01, 0.01)
    current_price = base_price * (1 + price_variation)
    
    return {
        "symbol": symbol,
        "timestamp": datetime.utcnow().isoformat(),
        "price": current_price,
        "price_change_24h": np.random.uniform(-2.5, 2.5),
        "volume_24h": np.random.uniform(1000000, 5000000),
        "order_book": {
            "bids": [
                {"price": current_price - 0.01 * i, "size": np.random.uniform(0.1, 10)}
                for i in range(1, 11)
            ],
            "asks": [
                {"price": current_price + 0.01 * i, "size": np.random.uniform(0.1, 10)}
                for i in range(1, 11)
            ]
        },
        "market_depth": {
            "bid_depth": np.random.uniform(50000, 200000),
            "ask_depth": np.random.uniform(50000, 200000),
            "spread": current_price * 0.0001
        },
        "volatility": {
            "1h": np.random.uniform(0.02, 0.05),
            "4h": np.random.uniform(0.03, 0.08),
            "1d": np.random.uniform(0.05, 0.15)
        }
    }

@router.get("/order-book/{symbol}", response_model=Dict[str, Any])
async def get_order_book(
    symbol: str,
    depth: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user)
):
    """Order book ma'lumotlari"""
    
    if symbol not in hft_config["symbols_supported"]:
        raise HTTPException(
            status_code=400,
            detail=f"Qo'llab-quvvatlanmaydigan symbol: {symbol}"
        )
    
    # Mock order book
    current_price = np.random.uniform(44000, 46000) if symbol.startswith("BTC") else np.random.uniform(2700, 2900)
    
    bids = []
    for i in range(depth):
        price = current_price - (i + 1) * current_price * 0.0001
        size = np.random.uniform(0.1, 50)
        total = price * size
        bids.append({
            "price": round(price, 8),
            "size": round(size, 6),
            "total": round(total, 2)
        })
    
    asks = []
    for i in range(depth):
        price = current_price + (i + 1) * current_price * 0.0001
        size = np.random.uniform(0.1, 50)
        total = price * size
        asks.append({
            "price": round(price, 8),
            "size": round(size, 6),
            "total": round(total, 2)
        })
    
    return {
        "symbol": symbol,
        "timestamp": datetime.utcnow().isoformat(),
        "bids": bids,
        "asks": asks,
        "spread": round(asks[0]["price"] - bids[0]["price"], 8),
        "mid_price": round((asks[0]["price"] + bids[0]["price"]) / 2, 8),
        "total_bid_volume": sum(bid["size"] for bid in bids),
        "total_ask_volume": sum(ask["size"] for ask in asks)
    }

# =============================================================================
# RISK MANAGEMENT
# =============================================================================

@router.get("/risk/limits", response_model=Dict[str, Any])
async def get_risk_limits(current_user: User = Depends(get_current_active_user)):
    """Risk limitlari ma'lumotlari"""
    
    return {
        "current_risk_exposure": {
            "daily_pnl": str(hft_status["profit_loss_today"]),
            "max_daily_loss_used": "23.4%",
            "position_exposure_used": "45.2%",
            "current_drawdown": "1.2%"
        },
        "risk_limits": {
            "max_daily_loss": str(hft_config["risk_limits"]["max_daily_loss"]),
            "max_position_exposure": str(hft_config["risk_limits"]["max_position_exposure"]),
            "max_drawdown": f"{hft_config['risk_limits']['max_drawdown'] * 100}%"
        },
        "alerts": {
            "active_alerts": 0,
            "warnings": [],
            "critical": []
        },
        "compliance_status": "COMPLIANT",
        "last_updated": datetime.utcnow().isoformat()
    }

@router.post("/risk/emergency-stop", response_model=BaseResponse)
async def emergency_stop(
    reason: str = Query(..., description="Emergency stop reason"),
    current_user: User = Depends(get_current_admin_user)
):
    """Favqulodda to'xtatish"""
    
    # Stop all HFT activities
    hft_status["is_running"] = False
    
    # Deactivate all strategies
    for strategy in strategies_db.values():
        strategy["is_active"] = False
    
    return BaseResponse(
        message=f"HFT tizimi favqulodda to'xtatildi. Sabab: {reason}"
    )

@router.post("/risk/resume", response_model=BaseResponse)
async def resume_hft_operations(
    current_user: User = Depends(get_current_admin_user)
):
    """HFT operatsiyalarni davom ettirish"""
    
    # Resume HFT activities
    hft_status["is_running"] = True
    
    return BaseResponse(
        message="HFT operatsiyalar qayta tiklandi"
    )

# =============================================================================
# BACKGROUND TASKS
# =============================================================================

async def execute_hft_trade(trade_id: str, trade: HFTTrade):
    """HFT trade bajariish"""
    try:
        logger.info(f"HFT trade bajarilmoqda: {trade_id}")
        
        # Simulate ultra-low latency execution
        start_time = datetime.utcnow()
        
        # Get best execution venue
        venue = get_best_execution_venue(trade.symbol, trade.quantity)
        
        # Simulate market order execution
        await asyncio.sleep(np.random.uniform(0.001, 0.005))  # 1-5 microseconds
        
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds() * 1000  # milliseconds
        latency = execution_time * 1000  # microseconds
        
        # Update trade with execution details
        trade.execution_time = execution_time
        trade.latency = latency
        trade.status = TradeStatus.EXECUTED
        
        # Calculate profit/loss (mock)
        if trade.side == "buy":
            trade.profit_loss = trade.quantity * Decimal(str(np.random.uniform(-0.1, 0.2)))
        else:
            trade.profit_loss = trade.quantity * Decimal(str(np.random.uniform(-0.2, 0.1)))
        
        trade.execution_venue = venue
        
        logger.info(f"HFT trade bajarildi: {trade_id}, Latency: {latency}μs")
        
    except Exception as e:
        logger.error(f"HFT trade bajarishda xato: {e}")
        trade.status = TradeStatus.FAILED

def get_best_strategy(symbol: str, quantity: Decimal) -> str:
    """Eng yaxshi strategiyani tanlash"""
    strategies = ["ml_mean_reversion", "momentum_following", "statistical_arbitrage"]
    return np.random.choice(strategies)

def get_best_execution_venue(symbol: str, quantity: Decimal) -> str:
    """Eng yaxshi bajarish maydonini tanlash"""
    return np.random.choice(hft_config["execution_venues"])

def get_current_position_exposure(symbol: str) -> Decimal:
    """Joriy pozitsiya ko'rsatkichini olish"""
    # Mock calculation
    return Decimal(str(np.random.uniform(0, 50000)))

# Initialize mock data
def init_mock_hft_data():
    """Mock HFT ma'lumotlarini yaratish"""
    if not trades_db:
        strategies = ["ml_mean_reversion", "momentum_following", "statistical_arbitrage"]
        
        for i in range(100):
            trade_id = str(uuid.uuid4())
            symbol = np.random.choice(hft_config["symbols_supported"])
            side = np.random.choice(["buy", "sell"])
            quantity = Decimal(str(np.random.uniform(0.1, 10)))
            price = Decimal(str(np.random.uniform(44000, 46000)))
            
            trade = HFTTrade(
                id=trade_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                execution_time=np.random.uniform(0.002, 0.010),  # 2-10ms
                latency=np.random.uniform(5, 25),  # 5-25 microseconds
                profit_loss=Decimal(str(np.random.uniform(-0.5, 1.0))),
                status=np.random.choice(list(TradeStatus)),
                created_at=datetime.utcnow() - timedelta(hours=i),
                strategy=np.random.choice(strategies)
            )
            
            trades_db[trade_id] = trade
        
        # Create mock strategies
        for i, strategy_name in enumerate(strategies):
            strategy_id = str(uuid.uuid4())
            strategy = {
                "id": strategy_id,
                "name": strategy_name.replace("_", " ").title(),
                "description": f"Advanced {strategy_name.replace('_', ' ')} strategy for HFT",
                "parameters": {
                    "lookback_period": 5,
                    "confidence_threshold": 0.8,
                    "max_positions": 10,
                    "rebalance_frequency": "1m"
                },
                "is_active": i < 2,  # First 2 strategies active
                "performance": {
                    "total_trades": np.random.randint(100, 500),
                    "win_rate": np.random.uniform(0.6, 0.9),
                    "profit_factor": np.random.uniform(1.2, 2.5),
                    "sharpe_ratio": np.random.uniform(1.5, 3.0),
                    "max_drawdown": np.random.uniform(0.01, 0.05)
                },
                "created_at": datetime.utcnow() - timedelta(days=i * 7)
            }
            
            strategies_db[strategy_id] = strategy

# Initialize mock data on module load
import logging
logger = logging.getLogger(__name__)
init_mock_hft_data()