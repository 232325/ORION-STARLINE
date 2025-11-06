"""
AI Trading Evolution - Production API Server
===========================================
FastAPI asosiy server - Barcha trading modullarini REST API orqali taqdim etadi

Author: MiniMax Agent
Version: 1.0.0
Date: 2025-11-04
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
import uuid

# Internal imports
from integration.integration_hub import IntegrationHub
from integration.performance_optimizer import PerformanceOptimizer
from integration.security_auditor import SecurityAuditor
from api.websocket.websocket_manager import manager, handle_websocket_message

# UI Modules
from ui.backtesting_dashboard import backtesting_dashboard, BacktestConfig, OptimizationMethod
from ui.live_trading_dashboard import live_dashboard, PositionSide, OrderType
from ui.market_intelligence import market_intelligence, MarketSector, ScannerCondition
from ui.performance_analytics import performance_analytics
from ui.trade_journal import trade_journal, TradeSetup, TradeOutcome
from ui.advanced_charts import advanced_charts, Timeframe, IndicatorType

# Social Trading Modules
from social.copy_trading_engine import CopyTradingEngine, LeaderProfile, CopySettings, CopyMode
from social.signal_platform import SignalPlatform, TradingSignal, SignalProvider, SignalType, TimeFrame as SignalTimeFrame
from social.leaderboard_system import LeaderboardSystem, TraderRank, RankCategory
from social.automl_pipeline import AutoMLPipeline, ModelType, TaskType, OptimizationMethod as MLOptimization
from social.strategy_marketplace import StrategyMarketplace, Strategy, StrategyCategory, PricingModel
from social.reputation_system import ReputationSystem, Review, ReviewType, VerificationLevel

# Payment, Forex, REITs va Tax Modules
from payment.payment_gateway import PaymentGateway, SubscriptionPlan, PaymentMethod, Invoice, PaymentStatus
from payment.forex_integration import ForexIntegration, CurrencyPair, ForexQuote, ForexTrade
from payment.reits_trading import REITsTrading, REIT, REITCategory, REITPosition
from payment.multi_currency import MultiCurrencyWallet, Currency, CurrencyBalance, TransactionType as WalletTransactionType
from payment.tax_reporting import TaxReporting, TaxReport, TransactionType as TaxTransactionType, TaxLotMethod
from payment.webhook_manager import WebhookManager, WebhookEvent, WebhookSubscription, DeliveryStatus

# Environment variables yuklash
load_dotenv()

# Logging sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# GLOBAL STATE
# =============================================================================
integration_hub: Optional[IntegrationHub] = None
performance_optimizer: Optional[PerformanceOptimizer] = None
security_auditor: Optional[SecurityAuditor] = None

# Social Trading Modules
copy_trading_engine: Optional[CopyTradingEngine] = None
signal_platform: Optional[SignalPlatform] = None
leaderboard_system: Optional[LeaderboardSystem] = None
automl_pipeline: Optional[AutoMLPipeline] = None
strategy_marketplace: Optional[StrategyMarketplace] = None
reputation_system: Optional[ReputationSystem] = None

# Payment, Forex, REITs va Tax Modules
payment_gateway: Optional[PaymentGateway] = None
forex_integration: Optional[ForexIntegration] = None
reits_trading: Optional[REITsTrading] = None
multi_currency_wallet: Optional[MultiCurrencyWallet] = None
tax_reporting: Optional[TaxReporting] = None
webhook_manager: Optional[WebhookManager] = None


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status: healthy, degraded, unhealthy")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    version: str = Field(..., description="API version")
    uptime: float = Field(..., description="Server uptime in seconds")
    modules: Dict[str, Any] = Field(default_factory=dict, description="Module health status")


class StrategyRequest(BaseModel):
    """Trading strategiya so'rovi"""
    strategy_name: str = Field(..., description="Strategiya nomi (arbitrage, grid, dca, etc.)")
    symbol: str = Field(..., description="Trading pair (BTC/USDT, ETH/USDT, etc.)")
    timeframe: str = Field(default="1h", description="Timeframe (1m, 5m, 15m, 1h, 4h, 1d)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Strategiya parametrlari")


class StrategyResponse(BaseModel):
    """Trading strategiya javobi"""
    strategy_name: str
    symbol: str
    signal: str = Field(..., description="Trading signal: BUY, SELL, HOLD")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Signal confidence (0-1)")
    price: float = Field(..., description="Current price")
    entry_price: Optional[float] = Field(None, description="Suggested entry price")
    stop_loss: Optional[float] = Field(None, description="Stop loss price")
    take_profit: Optional[float] = Field(None, description="Take profit price")
    timestamp: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MarketDataRequest(BaseModel):
    """Market data so'rovi"""
    symbol: str = Field(..., description="Trading pair")
    market_type: str = Field(default="crypto", description="Market type: crypto, forex, stocks, commodities")
    timeframe: str = Field(default="1h", description="Timeframe")
    limit: int = Field(default=100, description="Number of candles", ge=1, le=1000)


class MarketDataResponse(BaseModel):
    """Market data javobi"""
    symbol: str
    market_type: str
    timeframe: str
    data: List[Dict[str, Any]]
    indicators: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str


class AnalyticsRequest(BaseModel):
    """Tahlil so'rovi"""
    analysis_type: str = Field(..., description="sentiment, whale_tracking, risk_scoring, etc.")
    symbol: Optional[str] = Field(None, description="Trading pair (optional)")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AnalyticsResponse(BaseModel):
    """Tahlil javobi"""
    analysis_type: str
    result: Dict[str, Any]
    timestamp: str


class PerformanceMetrics(BaseModel):
    """Performance metrics"""
    total_requests: int
    average_response_time: float
    cache_hit_rate: float
    active_connections: int
    cpu_usage: float
    memory_usage: float
    timestamp: str


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: str
    request_id: Optional[str] = None


# =============================================================================
# LIFECYCLE MANAGEMENT
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    global integration_hub, performance_optimizer, security_auditor
    global copy_trading_engine, signal_platform, leaderboard_system
    global automl_pipeline, strategy_marketplace, reputation_system
    global payment_gateway, forex_integration, reits_trading
    global multi_currency_wallet, tax_reporting, webhook_manager
    
    logger.info("🚀 AI Trading Evolution API ishga tushmoqda...")
    
    try:
        # Integration Hub'ni ishga tushirish
        integration_hub = IntegrationHub()
        await integration_hub.initialize()
        logger.info("✅ Integration Hub tayyor")
        
        # Performance Optimizer
        performance_optimizer = PerformanceOptimizer()
        await performance_optimizer.initialize()
        logger.info("✅ Performance Optimizer tayyor")
        
        # Security Auditor
        security_auditor = SecurityAuditor()
        logger.info("✅ Security Auditor tayyor")
        
        # Social Trading Modules
        copy_trading_engine = CopyTradingEngine()
        logger.info("✅ Copy Trading Engine tayyor")
        
        signal_platform = SignalPlatform()
        logger.info("✅ Signal Platform tayyor")
        
        leaderboard_system = LeaderboardSystem()
        logger.info("✅ Leaderboard System tayyor")
        
        automl_pipeline = AutoMLPipeline()
        logger.info("✅ AutoML Pipeline tayyor")
        
        strategy_marketplace = StrategyMarketplace()
        logger.info("✅ Strategy Marketplace tayyor")
        
        reputation_system = ReputationSystem()
        logger.info("✅ Reputation System tayyor")
        
        # Payment, Forex, REITs va Tax Modules
        payment_gateway = PaymentGateway()
        logger.info("✅ Payment Gateway tayyor")
        
        forex_integration = ForexIntegration()
        logger.info("✅ Forex Integration tayyor")
        
        reits_trading = REITsTrading()
        logger.info("✅ REITs Trading tayyor")
        
        multi_currency_wallet = MultiCurrencyWallet()
        logger.info("✅ Multi-Currency Wallet tayyor")
        
        tax_reporting = TaxReporting()
        logger.info("✅ Tax Reporting tayyor")
        
        webhook_manager = WebhookManager()
        logger.info("✅ Webhook Manager tayyor")
        
        logger.info("✅ Barcha modullar muvaffaqiyatli yuklandi")
        logger.info(f"📊 API URL: http://0.0.0.0:{os.getenv('PORT', 8000)}")
        logger.info(f"📚 Docs: http://0.0.0.0:{os.getenv('PORT', 8000)}/docs")
        
        yield
        
    finally:
        # Shutdown
        logger.info("🛑 Server to'xtayapti...")
        if integration_hub:
            await integration_hub.shutdown()
        if performance_optimizer:
            await performance_optimizer.shutdown()
        logger.info("✅ Barcha resurslar tozalandi")


# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(
    title="AI Trading Evolution API",
    description="""
    🚀 **AI Trading Evolution** - Professional Trading Bot Platform
    
    ## Imkoniyatlar
    
    ### 📊 Trading Strategies
    - **Arbitrage Bot**: CEX va DEX o'rtasida arbitraj
    - **Grid Trading**: Avtomatik grid strategiyasi
    - **DCA Bot**: Dollar Cost Averaging
    - **Futures & Options**: Leverage bilan ishlash
    - **Mean Reversion**: Statistik arbitraj
    - **Momentum Trading**: Trend following
    
    ### 📈 Analytics
    - **Sentiment Analysis**: Twitter, Reddit, News tahlili
    - **Whale Tracking**: Katta tranzaksiyalarni kuzatish
    - **Portfolio Analytics**: PnL, risk metriklari
    - **Risk Scoring**: VaR, CVaR, Sharpe ratio
    - **Market Manipulation**: Pump & dump detection
    - **Order Flow**: Level 2 data tahlili
    
    ### 🌍 Markets
    - **Crypto**: Bitcoin, Ethereum va 100+ coin
    - **Forex**: Major, minor va exotic pairs
    - **Stocks**: NASDAQ, NYSE real-time
    - **Commodities**: Oil, Gas, Gold, Silver
    - **Bonds & Treasury**: Government va corporate
    - **ETFs**: Index, sector, thematic
    
    ### 🤖 AI/ML Models
    - **Reinforcement Learning**: SAC, TD3, Rainbow DQN
    - **Deep Learning**: LSTM, Transformer, Attention
    - **Ensemble Methods**: Stacking, boosting, bagging
    - **Meta-Learning**: Few-shot learning, transfer learning
    - **Emotion AI**: Fear & Greed index
    
    ---
    **Version**: 1.0.0  
    **Author**: MiniMax Agent  
    **License**: Proprietary
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Umumiy exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else None,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )


# =============================================================================
# CORE ENDPOINTS
# =============================================================================

@app.get("/", tags=["Core"])
async def root():
    """Root endpoint"""
    return {
        "service": "AI Trading Evolution API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", response_model=HealthResponse, tags=["Core"])
async def health_check():
    """
    Health check endpoint
    
    Barcha modullarning holatini tekshiradi va umumiy health status qaytaradi.
    """
    try:
        start_time = datetime.utcnow()
        
        # Module health checks
        modules = {}
        if integration_hub:
            hub_status = await integration_hub.get_health_status()
            modules["integration_hub"] = hub_status
        
        if performance_optimizer:
            modules["performance_optimizer"] = "healthy"
        
        if security_auditor:
            modules["security_auditor"] = "healthy"
        
        # Overall status
        all_healthy = all(
            status == "healthy" 
            for status in modules.values() 
            if isinstance(status, str)
        )
        
        return HealthResponse(
            status="healthy" if all_healthy else "degraded",
            timestamp=datetime.utcnow().isoformat(),
            version="1.0.0",
            uptime=(datetime.utcnow() - start_time).total_seconds(),
            modules=modules
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )


@app.get("/metrics", response_model=PerformanceMetrics, tags=["Core"])
async def get_metrics():
    """
    Performance metrics endpoint
    
    Real-time performance ko'rsatkichlarini qaytaradi.
    """
    try:
        if not performance_optimizer:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Performance optimizer not available"
            )
        
        metrics = await performance_optimizer.get_metrics()
        
        return PerformanceMetrics(
            total_requests=metrics.get("total_requests", 0),
            average_response_time=metrics.get("avg_response_time", 0.0),
            cache_hit_rate=metrics.get("cache_hit_rate", 0.0),
            active_connections=metrics.get("active_connections", 0),
            cpu_usage=metrics.get("cpu_usage", 0.0),
            memory_usage=metrics.get("memory_usage", 0.0),
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =============================================================================
# TRADING STRATEGY ENDPOINTS
# =============================================================================

@app.post("/api/v1/strategy/execute", response_model=StrategyResponse, tags=["Trading Strategies"])
async def execute_strategy(request: StrategyRequest):
    """
    Trading strategiyani bajarish
    
    Berilgan parametrlar asosida trading signal generatsiya qiladi.
    
    **Qo'llab-quvvatlanadigan strategiyalar:**
    - `arbitrage`: CEX/DEX arbitraj
    - `grid`: Grid trading
    - `dca`: Dollar Cost Averaging
    - `futures`: Futures trading
    - `mean_reversion`: Mean reversion
    - `momentum`: Momentum trading
    """
    try:
        if not integration_hub:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Integration hub not available"
            )
        
        # Strategy execute
        result = await integration_hub.execute_strategy(
            strategy_name=request.strategy_name,
            symbol=request.symbol,
            timeframe=request.timeframe,
            parameters=request.parameters
        )
        
        return StrategyResponse(
            strategy_name=request.strategy_name,
            symbol=request.symbol,
            signal=result.get("signal", "HOLD"),
            confidence=result.get("confidence", 0.0),
            price=result.get("price", 0.0),
            entry_price=result.get("entry_price"),
            stop_loss=result.get("stop_loss"),
            take_profit=result.get("take_profit"),
            timestamp=datetime.utcnow().isoformat(),
            metadata=result.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Strategy execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Strategy execution failed: {str(e)}"
        )


@app.get("/api/v1/strategy/list", tags=["Trading Strategies"])
async def list_strategies():
    """
    Mavjud strategiyalar ro'yxati
    
    Barcha qo'llab-quvvatlanadigan trading strategiyalarni qaytaradi.
    """
    return {
        "strategies": [
            {
                "name": "arbitrage",
                "description": "CEX va DEX o'rtasida arbitraj imkoniyatlarini topish",
                "supported_markets": ["crypto"],
                "risk_level": "medium"
            },
            {
                "name": "grid",
                "description": "Avtomatik grid trading strategiyasi",
                "supported_markets": ["crypto", "forex", "stocks"],
                "risk_level": "low"
            },
            {
                "name": "dca",
                "description": "Dollar Cost Averaging bot",
                "supported_markets": ["crypto", "stocks"],
                "risk_level": "low"
            },
            {
                "name": "futures",
                "description": "Futures va options trading",
                "supported_markets": ["crypto", "forex"],
                "risk_level": "high"
            },
            {
                "name": "mean_reversion",
                "description": "Statistik arbitraj va mean reversion",
                "supported_markets": ["crypto", "forex", "stocks"],
                "risk_level": "medium"
            },
            {
                "name": "momentum",
                "description": "Momentum va trend following",
                "supported_markets": ["crypto", "forex", "stocks"],
                "risk_level": "medium"
            }
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


# =============================================================================
# MARKET DATA ENDPOINTS
# =============================================================================

@app.post("/api/v1/market/data", response_model=MarketDataResponse, tags=["Market Data"])
async def get_market_data(request: MarketDataRequest):
    """
    Market data olish
    
    Real-time yoki historical market datani qaytaradi.
    """
    try:
        if not integration_hub:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Integration hub not available"
            )
        
        # Market data fetch
        data = await integration_hub.get_market_data(
            symbol=request.symbol,
            market_type=request.market_type,
            timeframe=request.timeframe,
            limit=request.limit
        )
        
        return MarketDataResponse(
            symbol=request.symbol,
            market_type=request.market_type,
            timeframe=request.timeframe,
            data=data.get("candles", []),
            indicators=data.get("indicators", {}),
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Market data fetch failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Market data fetch failed: {str(e)}"
        )


@app.get("/api/v1/market/symbols", tags=["Market Data"])
async def list_symbols(market_type: str = "crypto"):
    """
    Mavjud symbollar ro'yxati
    
    Qo'llab-quvvatlanadigan barcha trading pairlarni qaytaradi.
    """
    symbols = {
        "crypto": ["BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", "SOL/USDT"],
        "forex": ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "USD/CHF"],
        "stocks": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META"],
        "commodities": ["GOLD", "SILVER", "OIL.WTI", "OIL.BRENT", "NATGAS", "WHEAT"]
    }
    
    return {
        "market_type": market_type,
        "symbols": symbols.get(market_type, []),
        "count": len(symbols.get(market_type, [])),
        "timestamp": datetime.utcnow().isoformat()
    }


# =============================================================================
# ANALYTICS ENDPOINTS
# =============================================================================

@app.post("/api/v1/analytics/analyze", response_model=AnalyticsResponse, tags=["Analytics"])
async def analyze(request: AnalyticsRequest):
    """
    Tahlil bajarish
    
    Turli xil tahlil turlarini qo'llab-quvvatlaydi:
    - sentiment: Sentiment tahlili (social media, news)
    - whale_tracking: Katta tranzaksiyalarni kuzatish
    - risk_scoring: Risk baholash
    - portfolio: Portfolio tahlili
    """
    try:
        if not integration_hub:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Integration hub not available"
            )
        
        # Analytics execute
        result = await integration_hub.execute_analytics(
            analysis_type=request.analysis_type,
            symbol=request.symbol,
            parameters=request.parameters
        )
        
        return AnalyticsResponse(
            analysis_type=request.analysis_type,
            result=result,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Analytics failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics failed: {str(e)}"
        )


@app.get("/api/v1/analytics/types", tags=["Analytics"])
async def list_analytics_types():
    """
    Mavjud tahlil turlari
    
    Barcha qo'llab-quvvatlanadigan analytics turlarini qaytaradi.
    """
    return {
        "types": [
            {
                "name": "sentiment",
                "description": "Social media va news sentiment tahlili",
                "sources": ["Twitter", "Reddit", "News APIs"]
            },
            {
                "name": "whale_tracking",
                "description": "Katta tranzaksiyalarni kuzatish va tahlil qilish",
                "sources": ["Blockchain explorers", "Exchange flows"]
            },
            {
                "name": "risk_scoring",
                "description": "Portfolio risk assessment",
                "metrics": ["VaR", "CVaR", "Sharpe Ratio", "Max Drawdown"]
            },
            {
                "name": "portfolio",
                "description": "Portfolio performance tahlili",
                "metrics": ["PnL", "ROI", "Win Rate", "Profit Factor"]
            },
            {
                "name": "manipulation",
                "description": "Market manipulation detection",
                "patterns": ["Pump & Dump", "Wash Trading", "Spoofing"]
            }
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


# =============================================================================
# WEBSOCKET ENDPOINTS
# =============================================================================

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str = None):
    """
    WebSocket endpoint - Real-time data streaming
    
    **Connection**: ws://localhost:8000/ws/{client_id}
    
    **Supported Channels:**
    - `market:{symbol}` - Real-time market data (e.g., market:BTC/USDT)
    - `signals:{strategy}` - Trading signals (e.g., signals:grid)
    - `portfolio:{user_id}` - Portfolio updates
    
    **Message Format:**
    ```json
    {
        "action": "subscribe",
        "channel": "market:BTC/USDT"
    }
    ```
    
    **Actions:**
    - `subscribe` - Channel'ga obuna
    - `unsubscribe` - Obunani bekor qilish
    - `ping` - Connection test
    - `get_stats` - Connection statistikasi
    """
    # Generate client ID if not provided
    if not client_id:
        client_id = str(uuid.uuid4())
    
    # Connect
    connected = await manager.connect(websocket, client_id)
    if not connected:
        return
    
    try:
        # Send welcome message
        await manager.send_personal_message(client_id, {
            "type": "welcome",
            "client_id": client_id,
            "message": "Connected to AI Trading Evolution WebSocket",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Message loop
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Handle message
            await handle_websocket_message(client_id, data)
            
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)


@app.get("/ws/stats", tags=["WebSocket"])
async def websocket_stats():
    """
    WebSocket connection statistikasi
    
    Aktiv connection'lar va obunalar haqida ma'lumot.
    """
    return manager.get_stats()


# =============================================================================
# UI DASHBOARD ENDPOINTS
# =============================================================================

# Backtesting Dashboard
@app.post("/api/v1/backtesting/run", tags=["Backtesting"])
async def run_backtest(config: Dict[str, Any]):
    """Run backtest with configuration"""
    try:
        from datetime import datetime
        backtest_config = BacktestConfig(
            strategy_name=config['strategy_name'],
            symbol=config['symbol'],
            timeframe=config['timeframe'],
            start_date=datetime.fromisoformat(config['start_date']),
            end_date=datetime.fromisoformat(config['end_date']),
            initial_capital=config['initial_capital'],
            parameters=config.get('parameters', {})
        )
        
        result = await backtesting_dashboard.run_backtest(backtest_config)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/backtesting/list", tags=["Backtesting"])
async def list_backtests(limit: int = 50):
    """List all backtests"""
    results = backtesting_dashboard.list_backtests(limit=limit)
    return [r.to_dict() for r in results]


@app.get("/api/v1/backtesting/{backtest_id}", tags=["Backtesting"])
async def get_backtest(backtest_id: str):
    """Get backtest by ID"""
    result = backtesting_dashboard.get_backtest(backtest_id)
    if not result:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return result.to_dict()


# Live Trading Dashboard
@app.get("/api/v1/dashboard/portfolio", tags=["Dashboard"])
async def get_portfolio_snapshot():
    """Get current portfolio snapshot"""
    snapshot = live_dashboard.get_portfolio_snapshot()
    return snapshot.to_dict()


@app.get("/api/v1/dashboard/positions", tags=["Dashboard"])
async def get_positions():
    """Get all open positions"""
    positions = live_dashboard.get_positions()
    return [p.to_dict() for p in positions]


@app.post("/api/v1/dashboard/position/open", tags=["Dashboard"])
async def open_position(data: Dict[str, Any]):
    """Open new position"""
    try:
        position = await live_dashboard.open_position(
            symbol=data['symbol'],
            side=PositionSide(data['side']),
            size=data['size'],
            leverage=data.get('leverage', 1.0),
            stop_loss=data.get('stop_loss'),
            take_profit=data.get('take_profit')
        )
        return position.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/dashboard/position/{position_id}/close", tags=["Dashboard"])
async def close_position(position_id: str):
    """Close position"""
    result = await live_dashboard.close_position(position_id)
    return result


# Market Intelligence
@app.get("/api/v1/market/heatmap", tags=["Market Intelligence"])
async def get_market_heatmap(sector: Optional[str] = None, metric: str = "change_24h"):
    """Get market heatmap"""
    sector_enum = MarketSector(sector) if sector else None
    heatmap = await market_intelligence.get_market_heatmap(sector_enum, metric)
    return heatmap


@app.get("/api/v1/market/correlation", tags=["Market Intelligence"])
async def get_correlation_matrix(symbols: str, period: str = "30d"):
    """Get correlation matrix"""
    symbol_list = symbols.split(',')
    correlation = await market_intelligence.calculate_correlation_matrix(symbol_list, period)
    return correlation.to_dict()


@app.post("/api/v1/market/scan", tags=["Market Intelligence"])
async def scan_market(conditions: List[str], sector: Optional[str] = None):
    """Scan market for opportunities"""
    condition_enums = [ScannerCondition(c) for c in conditions]
    sector_enum = MarketSector(sector) if sector else None
    results = await market_intelligence.scan_market(condition_enums, sector_enum)
    return [r.to_dict() for r in results]


@app.get("/api/v1/market/overview", tags=["Market Intelligence"])
async def get_market_overview():
    """Get market overview"""
    overview = await market_intelligence.get_market_overview()
    return overview


# Performance Analytics
@app.get("/api/v1/analytics/performance", tags=["Analytics"])
async def get_performance_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get performance metrics"""
    from datetime import datetime
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    metrics = await performance_analytics.calculate_performance_metrics(start, end)
    return metrics.to_dict()


@app.get("/api/v1/analytics/drawdown", tags=["Analytics"])
async def get_drawdown_analysis():
    """Get drawdown analysis"""
    analysis = await performance_analytics.analyze_drawdown()
    return analysis.to_dict()


@app.get("/api/v1/analytics/equity-curve", tags=["Analytics"])
async def get_equity_curve():
    """Get equity curve data"""
    data = performance_analytics.get_equity_curve_data()
    return data


# Trade Journal
@app.get("/api/v1/journal/entries", tags=["Journal"])
async def search_journal_entries(
    query: Optional[str] = None,
    symbol: Optional[str] = None,
    limit: int = 50
):
    """Search journal entries"""
    entries = await trade_journal.search_entries(
        query=query,
        symbol=symbol,
        limit=limit
    )
    return [e.to_dict() for e in entries]


@app.get("/api/v1/journal/{entry_id}", tags=["Journal"])
async def get_journal_entry(entry_id: str):
    """Get journal entry by ID"""
    entry = await trade_journal.get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry.to_dict()


@app.get("/api/v1/journal/statistics", tags=["Journal"])
async def get_journal_statistics():
    """Get journal statistics"""
    stats = await trade_journal.get_statistics()
    return stats.to_dict()


# Advanced Charts
@app.get("/api/v1/charts/data", tags=["Charts"])
async def get_chart_data(
    symbol: str,
    timeframe: str = "1h",
    limit: int = 100
):
    """Get chart OHLCV data"""
    tf = Timeframe(timeframe)
    candles = await advanced_charts.get_chart_data(symbol, tf, limit=limit)
    return [c.to_dict() for c in candles]


@app.get("/api/v1/charts/indicator", tags=["Charts"])
async def calculate_indicator(
    symbol: str,
    indicator: str,
    timeframe: str = "1h",
    **parameters
):
    """Calculate technical indicator"""
    tf = Timeframe(timeframe)
    ind_type = IndicatorType(indicator)
    
    result = await advanced_charts.calculate_indicator(symbol, tf, ind_type, parameters)
    return result.to_dict()


@app.get("/api/v1/charts/patterns", tags=["Charts"])
async def detect_patterns(symbol: str, timeframe: str = "1h"):
    """Detect chart patterns"""
    tf = Timeframe(timeframe)
    patterns = await advanced_charts.detect_patterns(symbol, tf)
    return [p.to_dict() for p in patterns]


@app.get("/api/v1/charts/mtf-analysis", tags=["Charts"])
async def get_multi_timeframe_analysis(symbol: str):
    """Get multi-timeframe analysis"""
    analysis = await advanced_charts.get_multi_timeframe_analysis(symbol)
    return analysis


# =============================================================================
# COPY TRADING ENDPOINTS
# =============================================================================

@app.post("/api/v1/copy-trading/leaders", tags=["Copy Trading"])
async def add_leader(profile: Dict[str, Any]):
    """Leader qo'shish"""
    from social.copy_trading_engine import LeaderProfile, RiskLevel
    
    leader = LeaderProfile(
        leader_id=profile.get('leader_id'),
        username=profile.get('username'),
        **{k: v for k, v in profile.items() if k not in ['leader_id', 'username']}
    )
    
    success = await copy_trading_engine.add_leader(leader)
    return {"success": success, "leader_id": leader.leader_id}


@app.get("/api/v1/copy-trading/leaders/top", tags=["Copy Trading"])
async def get_top_leaders(
    limit: int = 10,
    sort_by: str = "win_rate",
    min_trades: int = 10
):
    """Top leaderlar ro'yxati"""
    leaders = await copy_trading_engine.get_top_leaders(limit, sort_by, min_trades)
    return [leader.to_dict() for leader in leaders]


@app.get("/api/v1/copy-trading/leaders/{leader_id}", tags=["Copy Trading"])
async def get_leader(leader_id: str):
    """Leader ma'lumotlarini olish"""
    leader = await copy_trading_engine.get_leader(leader_id)
    if not leader:
        raise HTTPException(status_code=404, detail="Leader topilmadi")
    return leader.to_dict()


@app.post("/api/v1/copy-trading/start", tags=["Copy Trading"])
async def start_copying(
    follower_id: str,
    leader_id: str,
    settings: Dict[str, Any]
):
    """Copy tradingni boshlash"""
    from social.copy_trading_engine import CopySettings
    
    copy_settings = CopySettings(
        follower_id=follower_id,
        leader_id=leader_id,
        **settings
    )
    
    success = await copy_trading_engine.start_copying(follower_id, leader_id, copy_settings)
    return {"success": success}


@app.post("/api/v1/copy-trading/stop", tags=["Copy Trading"])
async def stop_copying(follower_id: str, leader_id: str):
    """Copy tradingni to'xtatish"""
    success = await copy_trading_engine.stop_copying(follower_id, leader_id)
    return {"success": success}


@app.get("/api/v1/copy-trading/statistics/{follower_id}", tags=["Copy Trading"])
async def get_follower_statistics(follower_id: str):
    """Follower statistikasi"""
    stats = await copy_trading_engine.get_follower_statistics(follower_id)
    return stats


@app.get("/api/v1/copy-trading/history/{follower_id}", tags=["Copy Trading"])
async def get_copy_history(follower_id: str, limit: int = 100):
    """Copy tradelar tarixi"""
    trades = await copy_trading_engine.get_copy_history(follower_id, limit)
    return [trade.to_dict() for trade in trades]


# =============================================================================
# SIGNAL PLATFORM ENDPOINTS
# =============================================================================

@app.post("/api/v1/signals/providers/register", tags=["Signals"])
async def register_signal_provider(provider: Dict[str, Any]):
    """Signal provider ro'yxatdan o'tkazish"""
    from social.signal_platform import SignalProvider
    
    provider_obj = SignalProvider(**provider)
    success = await signal_platform.register_provider(provider_obj)
    return {"success": success, "provider_id": provider_obj.provider_id}


@app.post("/api/v1/signals/publish", tags=["Signals"])
async def publish_signal(signal: Dict[str, Any]):
    """Signal e'lon qilish"""
    from social.signal_platform import TradingSignal
    
    signal_obj = TradingSignal(**signal)
    success = await signal_platform.publish_signal(signal_obj)
    return {"success": success, "signal_id": signal_obj.signal_id}


@app.post("/api/v1/signals/subscribe", tags=["Signals"])
async def subscribe_to_provider(
    subscriber_id: str,
    provider_id: str,
    settings: Optional[Dict[str, Any]] = None
):
    """Signal providerga obuna bo'lish"""
    success = await signal_platform.subscribe(subscriber_id, provider_id)
    return {"success": success}


@app.post("/api/v1/signals/unsubscribe", tags=["Signals"])
async def unsubscribe_from_provider(subscriber_id: str, provider_id: str):
    """Obunani bekor qilish"""
    success = await signal_platform.unsubscribe(subscriber_id, provider_id)
    return {"success": success}


@app.get("/api/v1/signals", tags=["Signals"])
async def get_signals(
    provider_id: Optional[str] = None,
    symbol: Optional[str] = None,
    active_only: bool = True,
    limit: int = 100
):
    """Signallar ro'yxati"""
    signals = await signal_platform.get_signals(
        provider_id=provider_id,
        symbol=symbol,
        active_only=active_only,
        limit=limit
    )
    return [signal.to_dict() for signal in signals]


@app.get("/api/v1/signals/{signal_id}", tags=["Signals"])
async def get_signal(signal_id: str):
    """Bitta signalni olish"""
    signal = await signal_platform.get_signal(signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal topilmadi")
    return signal.to_dict()


@app.get("/api/v1/signals/providers/top", tags=["Signals"])
async def get_top_providers(
    limit: int = 10,
    sort_by: str = "success_rate",
    min_signals: int = 10
):
    """Top signal providerlar"""
    providers = await signal_platform.get_top_providers(limit, sort_by, min_signals)
    return [provider.to_dict() for provider in providers]


@app.get("/api/v1/signals/subscriber/{subscriber_id}", tags=["Signals"])
async def get_subscriber_signals(subscriber_id: str, limit: int = 50):
    """Obunachi signallari"""
    signals = await signal_platform.get_subscriber_signals(subscriber_id, limit)
    return [signal.to_dict() for signal in signals]


# =============================================================================
# LEADERBOARD ENDPOINTS
# =============================================================================

@app.post("/api/v1/leaderboard/update", tags=["Leaderboard"])
async def update_trader_rank(
    trader_id: str,
    username: str,
    performance_data: Dict[str, Any],
    category: str = "overall"
):
    """Trader reytingini yangilash"""
    from social.leaderboard_system import RankCategory
    
    cat = RankCategory(category)
    rank = await leaderboard_system.update_trader_rank(
        trader_id, username, performance_data, cat
    )
    return rank.to_dict()


@app.get("/api/v1/leaderboard", tags=["Leaderboard"])
async def get_leaderboard(
    category: str = "overall",
    limit: int = 100,
    tier: Optional[str] = None
):
    """Leaderboard ro'yxati"""
    from social.leaderboard_system import RankCategory, TraderTier
    
    cat = RankCategory(category)
    tier_obj = TraderTier(tier) if tier else None
    
    rankings = await leaderboard_system.get_leaderboard(cat, limit, tier_obj)
    return [rank.to_dict() for rank in rankings]


@app.get("/api/v1/leaderboard/trader/{trader_id}", tags=["Leaderboard"])
async def get_trader_rank(trader_id: str, category: str = "overall"):
    """Trader reytingini olish"""
    from social.leaderboard_system import RankCategory
    
    cat = RankCategory(category)
    rank = await leaderboard_system.get_trader_rank(trader_id, cat)
    if not rank:
        raise HTTPException(status_code=404, detail="Trader topilmadi")
    return rank.to_dict()


@app.get("/api/v1/leaderboard/nearby/{trader_id}", tags=["Leaderboard"])
async def get_nearby_ranks(
    trader_id: str,
    category: str = "overall",
    range_size: int = 5
):
    """Atrofdagi ranklarni olish"""
    from social.leaderboard_system import RankCategory
    
    cat = RankCategory(category)
    ranks = await leaderboard_system.get_nearby_ranks(trader_id, cat, range_size)
    return [rank.to_dict() for rank in ranks]


@app.get("/api/v1/leaderboard/rising-stars", tags=["Leaderboard"])
async def get_rising_stars(category: str = "overall", limit: int = 10):
    """Rising stars"""
    from social.leaderboard_system import RankCategory
    
    cat = RankCategory(category)
    stars = await leaderboard_system.get_rising_stars(cat, limit)
    return [star.to_dict() for star in stars]


@app.get("/api/v1/leaderboard/statistics", tags=["Leaderboard"])
async def get_leaderboard_statistics(category: str = "overall"):
    """Leaderboard statistikasi"""
    from social.leaderboard_system import RankCategory
    
    cat = RankCategory(category)
    stats = await leaderboard_system.get_statistics(cat)
    return stats


@app.get("/api/v1/leaderboard/achievements", tags=["Leaderboard"])
async def get_achievements():
    """Barcha yutuqlar"""
    achievements = await leaderboard_system.get_achievements_list()
    return [ach.to_dict() for ach in achievements]


@app.get("/api/v1/leaderboard/achievements/{trader_id}", tags=["Leaderboard"])
async def get_trader_achievements(trader_id: str):
    """Trader yutuqlari"""
    achievements = await leaderboard_system.get_trader_achievements(trader_id)
    return [ach.to_dict() for ach in achievements]


# =============================================================================
# AUTOML ENDPOINTS
# =============================================================================

@app.post("/api/v1/automl/train", tags=["AutoML"])
async def auto_train_models(
    data: Dict[str, Any],
    task_type: str = "classification",
    max_trials: int = 20
):
    """Avtomatik model training"""
    from social.automl_pipeline import TaskType
    import numpy as np
    
    # Mock data (real implementation da data yuklanishi kerak)
    X_train = np.random.rand(100, 10)
    y_train = np.random.randint(0, 2, 100)
    X_val = np.random.rand(20, 10)
    y_val = np.random.randint(0, 2, 20)
    
    task = TaskType(task_type)
    results = await automl_pipeline.auto_train(
        X_train, y_train, X_val, y_val,
        task_type=task,
        max_trials=max_trials
    )
    
    return [result.to_dict() for result in results]


@app.get("/api/v1/automl/best-model", tags=["AutoML"])
async def get_best_model(task_name: str = "classification_best"):
    """Eng yaxshi modelni olish"""
    model = await automl_pipeline.get_best_model(task_name)
    if not model:
        raise HTTPException(status_code=404, detail="Model topilmadi")
    return model.to_dict()


@app.get("/api/v1/automl/history", tags=["AutoML"])
async def get_training_history(limit: int = 100):
    """Training tarixi"""
    history = await automl_pipeline.get_training_history(limit)
    return [result.to_dict() for result in history]


@app.get("/api/v1/automl/feature-importance/{run_id}", tags=["AutoML"])
async def get_feature_importance(run_id: str, top_n: int = 10):
    """Feature importance"""
    importance = await automl_pipeline.get_feature_importance(run_id, top_n)
    return importance


@app.get("/api/v1/automl/recommendations", tags=["AutoML"])
async def get_automl_recommendations(
    task_type: str,
    dataset_size: int,
    features_count: int
):
    """Model recommendations"""
    from social.automl_pipeline import TaskType
    
    task = TaskType(task_type)
    recommendations = await automl_pipeline.get_recommendations(
        task, dataset_size, features_count
    )
    return recommendations


# =============================================================================
# STRATEGY MARKETPLACE ENDPOINTS
# =============================================================================

@app.post("/api/v1/marketplace/sellers/register", tags=["Marketplace"])
async def register_seller(seller: Dict[str, Any]):
    """Sotuvchi ro'yxatdan o'tkazish"""
    from social.strategy_marketplace import SellerProfile
    
    seller_obj = SellerProfile(**seller)
    success = await strategy_marketplace.register_seller(seller_obj)
    return {"success": success, "seller_id": seller_obj.seller_id}


@app.post("/api/v1/marketplace/strategies/submit", tags=["Marketplace"])
async def submit_strategy(strategy: Dict[str, Any]):
    """Strategiya yuborish"""
    from social.strategy_marketplace import Strategy
    
    strategy_obj = Strategy(**strategy)
    success = await strategy_marketplace.submit_strategy(strategy_obj)
    return {"success": success, "strategy_id": strategy_obj.strategy_id}


@app.post("/api/v1/marketplace/strategies/{strategy_id}/approve", tags=["Marketplace"])
async def approve_strategy(strategy_id: str, admin_notes: str = ""):
    """Strategiyani tasdiqlash"""
    success = await strategy_marketplace.approve_strategy(strategy_id, admin_notes)
    return {"success": success}


@app.post("/api/v1/marketplace/purchase", tags=["Marketplace"])
async def purchase_strategy(
    strategy_id: str,
    buyer_id: str,
    payment_info: Dict[str, Any]
):
    """Strategiya sotib olish"""
    purchase = await strategy_marketplace.purchase_strategy(
        strategy_id, buyer_id, payment_info
    )
    if not purchase:
        raise HTTPException(status_code=400, detail="Sotib olish amalga oshmadi")
    return purchase.to_dict()


@app.post("/api/v1/marketplace/ratings/add", tags=["Marketplace"])
async def add_strategy_rating(rating: Dict[str, Any]):
    """Strategiya reytingi qo'shish"""
    from social.strategy_marketplace import StrategyRating
    
    rating_obj = StrategyRating(**rating)
    success = await strategy_marketplace.add_rating(rating_obj)
    return {"success": success}


@app.get("/api/v1/marketplace/strategies", tags=["Marketplace"])
async def get_marketplace_strategies(
    category: Optional[str] = None,
    pricing_model: Optional[str] = None,
    min_rating: float = 0.0,
    max_price: Optional[float] = None,
    sort_by: str = "rating",
    limit: int = 50
):
    """Strategiyalar ro'yxati"""
    from social.strategy_marketplace import StrategyCategory, PricingModel
    
    cat = StrategyCategory(category) if category else None
    pricing = PricingModel(pricing_model) if pricing_model else None
    
    strategies = await strategy_marketplace.get_strategies(
        cat, pricing, min_rating, max_price, sort_by, limit
    )
    return [strategy.to_dict() for strategy in strategies]


@app.get("/api/v1/marketplace/strategies/{strategy_id}", tags=["Marketplace"])
async def get_strategy(strategy_id: str):
    """Strategiyani olish"""
    strategy = await strategy_marketplace.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategiya topilmadi")
    return strategy.to_dict()


@app.get("/api/v1/marketplace/strategies/{strategy_id}/ratings", tags=["Marketplace"])
async def get_strategy_ratings(strategy_id: str, limit: int = 50):
    """Strategiya reytinglari"""
    ratings = await strategy_marketplace.get_strategy_ratings(strategy_id, limit)
    return [rating.to_dict() for rating in ratings]


@app.get("/api/v1/marketplace/purchases/{buyer_id}", tags=["Marketplace"])
async def get_buyer_purchases(buyer_id: str):
    """Xaridor sotib olishlari"""
    purchases = await strategy_marketplace.get_buyer_purchases(buyer_id)
    return [purchase.to_dict() for purchase in purchases]


@app.get("/api/v1/marketplace/sellers/top", tags=["Marketplace"])
async def get_top_sellers(limit: int = 10, sort_by: str = "revenue"):
    """Top sotuvchilar"""
    sellers = await strategy_marketplace.get_top_sellers(limit, sort_by)
    return [seller.to_dict() for seller in sellers]


@app.get("/api/v1/marketplace/statistics", tags=["Marketplace"])
async def get_marketplace_stats():
    """Marketplace statistikasi"""
    stats = await strategy_marketplace.get_marketplace_stats()
    return stats


# =============================================================================
# REPUTATION SYSTEM ENDPOINTS
# =============================================================================

@app.post("/api/v1/reputation/reviews/submit", tags=["Reputation"])
async def submit_review(review: Dict[str, Any]):
    """Review yuborish"""
    from social.reputation_system import Review
    
    review_obj = Review(**review)
    success = await reputation_system.submit_review(review_obj)
    return {"success": success, "review_id": review_obj.review_id}


@app.get("/api/v1/reputation/reviews/{target_id}", tags=["Reputation"])
async def get_reviews(
    target_id: str,
    min_rating: int = 0,
    verified_only: bool = False,
    limit: int = 50
):
    """Reviewlarni olish"""
    reviews = await reputation_system.get_reviews(
        target_id, min_rating=min_rating, verified_only=verified_only, limit=limit
    )
    return [review.to_dict() for review in reviews]


@app.post("/api/v1/reputation/reviews/{review_id}/helpful", tags=["Reputation"])
async def mark_review_helpful(review_id: str, helpful: bool = True):
    """Reviewni foydali deb belgilash"""
    success = await reputation_system.mark_review_helpful(review_id, helpful)
    return {"success": success}


@app.post("/api/v1/reputation/trust-score/calculate", tags=["Reputation"])
async def calculate_trust_score(
    user_id: str,
    username: str,
    trading_data: Dict[str, Any]
):
    """Trust score hisoblash"""
    trust_score = await reputation_system.calculate_trust_score(
        user_id, username, trading_data
    )
    return trust_score.to_dict()


@app.get("/api/v1/reputation/trust-score/{user_id}", tags=["Reputation"])
async def get_trust_score(user_id: str):
    """Trust scoreni olish"""
    trust_score = await reputation_system.get_trust_score(user_id)
    if not trust_score:
        raise HTTPException(status_code=404, detail="Trust score topilmadi")
    return trust_score.to_dict()


@app.get("/api/v1/reputation/top-trusted", tags=["Reputation"])
async def get_top_trusted_users(limit: int = 50, min_tier: str = "medium"):
    """Eng ishonchli userlar"""
    from social.reputation_system import TrustTier
    
    tier = TrustTier(min_tier)
    users = await reputation_system.get_top_trusted_users(limit, tier)
    return [user.to_dict() for user in users]


@app.post("/api/v1/reputation/verification/submit", tags=["Reputation"])
async def submit_verification(
    user_id: str,
    verification_type: str,
    documents: List[str] = []
):
    """Verification so'rovi yuborish"""
    from social.reputation_system import VerificationLevel
    
    level = VerificationLevel(verification_type)
    request = await reputation_system.submit_verification(user_id, level, documents)
    return request.to_dict()


@app.post("/api/v1/reputation/verification/{request_id}/approve", tags=["Reputation"])
async def approve_verification(request_id: str, reviewer_notes: str = ""):
    """Verification so'rovini tasdiqlash"""
    success = await reputation_system.approve_verification(request_id, reviewer_notes)
    return {"success": success}


@app.get("/api/v1/reputation/verification/{user_id}", tags=["Reputation"])
async def get_verification_status(user_id: str):
    """Verification statusini olish"""
    status = await reputation_system.get_verification_status(user_id)
    return status


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("RELOAD", "false").lower() == "true",
        workers=int(os.getenv("WORKERS", 1)),
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )

# =============================================================================
# PAYMENT GATEWAY ENDPOINTS
# =============================================================================

@app.post("/api/v1/payment/subscriptions/create", tags=["Payment"])
async def create_subscription(user_id: str, plan: str, payment_method: str = None, trial_days: int = 0):
    """Yangi subscription yaratish"""
    from payment.payment_gateway import SubscriptionPlan, PaymentMethod
    
    plan_enum = SubscriptionPlan(plan)
    method_enum = PaymentMethod(payment_method) if payment_method else None
    
    subscription = await payment_gateway.create_subscription(
        user_id, plan_enum, method_enum, trial_days
    )
    return subscription.to_dict()


@app.get("/api/v1/payment/subscriptions/{subscription_id}", tags=["Payment"])
async def get_subscription(subscription_id: str):
    """Subscription ma'lumotlarini olish"""
    subscription = await payment_gateway.get_subscription(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription topilmadi")
    return subscription.to_dict()


@app.get("/api/v1/payment/subscriptions/user/{user_id}", tags=["Payment"])
async def get_user_subscriptions(user_id: str):
    """Foydalanuvchi subscriptionlari"""
    subscriptions = await payment_gateway.get_user_subscriptions(user_id)
    return [sub.to_dict() for sub in subscriptions]


@app.post("/api/v1/payment/subscriptions/{subscription_id}/cancel", tags=["Payment"])
async def cancel_subscription(subscription_id: str, immediately: bool = False):
    """Subscription bekor qilish"""
    subscription = await payment_gateway.cancel_subscription(subscription_id, immediately)
    return subscription.to_dict()


@app.post("/api/v1/payment/subscriptions/{subscription_id}/upgrade", tags=["Payment"])
async def upgrade_subscription(subscription_id: str, new_plan: str):
    """Subscription upgrade qilish"""
    from payment.payment_gateway import SubscriptionPlan
    
    plan_enum = SubscriptionPlan(new_plan)
    subscription = await payment_gateway.upgrade_subscription(subscription_id, plan_enum)
    return subscription.to_dict()


@app.post("/api/v1/payment/process", tags=["Payment"])
async def process_payment(invoice_id: str, payment_method: str, metadata: Dict[str, Any] = None):
    """To'lovni qayta ishlash"""
    from payment.payment_gateway import PaymentMethod
    
    method_enum = PaymentMethod(payment_method)
    payment = await payment_gateway.process_payment(invoice_id, method_enum, metadata)
    return payment.to_dict()


@app.post("/api/v1/payment/refund/{payment_id}", tags=["Payment"])
async def refund_payment(payment_id: str, amount: float = None, reason: str = None):
    """To'lovni qaytarish"""
    from decimal import Decimal
    
    amount_decimal = Decimal(str(amount)) if amount else None
    refund = await payment_gateway.refund_payment(payment_id, amount_decimal, reason)
    return refund


@app.get("/api/v1/payment/invoices/user/{user_id}", tags=["Payment"])
async def get_user_invoices(user_id: str, status: str = None):
    """Foydalanuvchi invoicelari"""
    from payment.payment_gateway import InvoiceStatus
    
    status_enum = InvoiceStatus(status) if status else None
    invoices = await payment_gateway.get_user_invoices(user_id, status_enum)
    return [inv.to_dict() for inv in invoices]


@app.get("/api/v1/payment/plans", tags=["Payment"])
async def get_all_plans():
    """Barcha mavjud planlar"""
    plans = await payment_gateway.get_all_plans()
    return plans


@app.get("/api/v1/payment/billing-history/{user_id}", tags=["Payment"])
async def get_billing_history(user_id: str, limit: int = 50):
    """Billing tarixi"""
    history = await payment_gateway.get_billing_history(user_id, limit)
    return history


@app.get("/api/v1/payment/statistics", tags=["Payment"])
async def get_payment_statistics():
    """Payment gateway statistikasi"""
    stats = payment_gateway.get_statistics()
    return stats


# =============================================================================
# FOREX INTEGRATION ENDPOINTS
# =============================================================================

@app.get("/api/v1/forex/quote/{pair}", tags=["Forex"])
async def get_forex_quote(pair: str):
    """Real-time forex quote"""
    from payment.forex_integration import CurrencyPair
    
    pair_enum = CurrencyPair(pair)
    quote = await forex_integration.get_quote(pair_enum)
    return quote.to_dict()


@app.post("/api/v1/forex/quotes/multiple", tags=["Forex"])
async def get_multiple_quotes(pairs: List[str]):
    """Ko'p pairlar uchun quotes"""
    from payment.forex_integration import CurrencyPair
    
    pair_enums = [CurrencyPair(p) for p in pairs]
    quotes = await forex_integration.get_multiple_quotes(pair_enums)
    return [q.to_dict() for q in quotes]


@app.get("/api/v1/forex/historical/{pair}", tags=["Forex"])
async def get_forex_historical(pair: str, timeframe: str = "1h", limit: int = 100):
    """Historical forex data"""
    from payment.forex_integration import CurrencyPair
    
    pair_enum = CurrencyPair(pair)
    data = await forex_integration.get_historical_data(pair_enum, timeframe, limit)
    return data


@app.post("/api/v1/forex/convert", tags=["Forex"])
async def convert_currency(amount: float, from_currency: str, to_currency: str):
    """Valyuta konvertatsiyasi"""
    from decimal import Decimal
    
    result = await forex_integration.convert_currency(
        Decimal(str(amount)), from_currency, to_currency
    )
    return result


@app.post("/api/v1/forex/orders/place", tags=["Forex"])
async def place_forex_order(
    pair: str,
    direction: str,
    size: float,
    order_type: str = "market",
    limit_price: float = None,
    stop_loss: float = None,
    take_profit: float = None
):
    """Forex order berish"""
    from payment.forex_integration import CurrencyPair, OrderType
    from decimal import Decimal
    
    pair_enum = CurrencyPair(pair)
    order_type_enum = OrderType(order_type)
    
    trade = await forex_integration.place_order(
        pair_enum,
        direction,
        Decimal(str(size)),
        order_type_enum,
        Decimal(str(limit_price)) if limit_price else None,
        Decimal(str(stop_loss)) if stop_loss else None,
        Decimal(str(take_profit)) if take_profit else None
    )
    return trade.to_dict()


@app.post("/api/v1/forex/trades/{trade_id}/close", tags=["Forex"])
async def close_forex_trade(trade_id: str):
    """Forex trade yopish"""
    trade = await forex_integration.close_trade(trade_id)
    return trade.to_dict()


@app.get("/api/v1/forex/trades/open", tags=["Forex"])
async def get_open_forex_trades():
    """Ochiq forex tradelar"""
    trades = await forex_integration.get_open_trades()
    return [t.to_dict() for t in trades]


@app.get("/api/v1/forex/trades/history", tags=["Forex"])
async def get_forex_trade_history(limit: int = 100):
    """Forex trade tarixi"""
    trades = await forex_integration.get_trade_history(limit)
    return [t.to_dict() for t in trades]


@app.get("/api/v1/forex/economic-calendar", tags=["Forex"])
async def get_economic_calendar(days_ahead: int = 7, impact: str = None):
    """Economic calendar"""
    events = await forex_integration.get_economic_calendar(days_ahead, impact)
    return [e.to_dict() for e in events]


@app.get("/api/v1/forex/market-session", tags=["Forex"])
async def get_market_session():
    """Joriy market session"""
    session = await forex_integration.get_market_session()
    return session


@app.get("/api/v1/forex/statistics", tags=["Forex"])
async def get_forex_statistics():
    """Forex integration statistikasi"""
    stats = forex_integration.get_statistics()
    return stats


# =============================================================================
# REITS TRADING ENDPOINTS
# =============================================================================

@app.get("/api/v1/reits/all", tags=["REITs"])
async def get_all_reits(category: str = None, min_yield: float = None):
    """Barcha REITlar"""
    from payment.reits_trading import REITCategory
    from decimal import Decimal
    
    category_enum = REITCategory(category) if category else None
    min_yield_decimal = Decimal(str(min_yield)) if min_yield else None
    
    reits = await reits_trading.get_all_reits(category_enum, min_yield_decimal)
    return [r.to_dict() for r in reits]


@app.get("/api/v1/reits/ticker/{ticker}", tags=["REITs"])
async def get_reit_by_ticker(ticker: str):
    """Ticker bo'yicha REIT"""
    reit = await reits_trading.get_reit_by_ticker(ticker)
    if not reit:
        raise HTTPException(status_code=404, detail="REIT topilmadi")
    return reit.to_dict()


@app.post("/api/v1/reits/buy", tags=["REITs"])
async def buy_reit(reit_id: str, shares: float, price: float = None):
    """REIT sotib olish"""
    from decimal import Decimal
    
    position = await reits_trading.buy_reit(
        reit_id,
        Decimal(str(shares)),
        Decimal(str(price)) if price else None
    )
    return position.to_dict()


@app.post("/api/v1/reits/sell/{position_id}", tags=["REITs"])
async def sell_reit(position_id: str, shares: float = None):
    """REIT sotish"""
    from decimal import Decimal
    
    sale = await reits_trading.sell_reit(
        position_id,
        Decimal(str(shares)) if shares else None
    )
    return sale


@app.get("/api/v1/reits/positions", tags=["REITs"])
async def get_reit_positions():
    """Barcha REIT pozitsiyalari"""
    positions = await reits_trading.get_positions()
    return [p.to_dict() for p in positions]


@app.post("/api/v1/reits/dividends/process", tags=["REITs"])
async def process_dividends():
    """Dividendlarni qayta ishlash"""
    payments = await reits_trading.process_dividends()
    return [p.to_dict() for p in payments]


@app.get("/api/v1/reits/dividends/history", tags=["REITs"])
async def get_dividend_history(position_id: str = None, limit: int = 50):
    """Dividend tarixi"""
    payments = await reits_trading.get_dividend_history(position_id, limit)
    return [p.to_dict() for p in payments]


@app.get("/api/v1/reits/portfolio/summary", tags=["REITs"])
async def get_reits_portfolio_summary():
    """Portfolio xulosasi"""
    summary = await reits_trading.get_portfolio_summary()
    return summary


@app.get("/api/v1/reits/top/yield", tags=["REITs"])
async def get_top_reits_by_yield(limit: int = 10):
    """Top REITs by yield"""
    reits = await reits_trading.get_top_reits_by_yield(limit)
    return [r.to_dict() for r in reits]


@app.get("/api/v1/reits/top/performance", tags=["REITs"])
async def get_top_reits_by_performance(limit: int = 10):
    """Top REITs by performance"""
    reits = await reits_trading.get_top_reits_by_performance(limit)
    return reits


@app.get("/api/v1/reits/statistics", tags=["REITs"])
async def get_reits_statistics():
    """REITs trading statistikasi"""
    stats = reits_trading.get_statistics()
    return stats


# =============================================================================
# MULTI-CURRENCY WALLET ENDPOINTS
# =============================================================================

@app.post("/api/v1/wallet/create", tags=["Wallet"])
async def create_wallet(user_id: str, name: str, initial_balances: Dict[str, float] = None):
    """Yangi wallet yaratish"""
    from payment.multi_currency import Currency
    from decimal import Decimal
    
    balances = None
    if initial_balances:
        balances = {
            Currency(currency): Decimal(str(amount))
            for currency, amount in initial_balances.items()
        }
    
    wallet = await multi_currency_wallet.create_wallet(user_id, name, balances)
    return wallet.to_dict()


@app.get("/api/v1/wallet/{wallet_id}", tags=["Wallet"])
async def get_wallet(wallet_id: str):
    """Wallet ma'lumotlari"""
    wallet = await multi_currency_wallet.get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet topilmadi")
    return wallet.to_dict()


@app.get("/api/v1/wallet/user/{user_id}", tags=["Wallet"])
async def get_user_wallets(user_id: str):
    """Foydalanuvchi walletlari"""
    wallets = await multi_currency_wallet.get_user_wallets(user_id)
    return [w.to_dict() for w in wallets]


@app.post("/api/v1/wallet/deposit", tags=["Wallet"])
async def deposit_to_wallet(wallet_id: str, currency: str, amount: float, description: str = None):
    """Depozit qo'shish"""
    from payment.multi_currency import Currency
    from decimal import Decimal
    
    transaction = await multi_currency_wallet.deposit(
        wallet_id,
        Currency(currency),
        Decimal(str(amount)),
        description
    )
    return transaction.to_dict()


@app.post("/api/v1/wallet/withdraw", tags=["Wallet"])
async def withdraw_from_wallet(wallet_id: str, currency: str, amount: float, description: str = None):
    """Pul yechish"""
    from payment.multi_currency import Currency
    from decimal import Decimal
    
    transaction = await multi_currency_wallet.withdraw(
        wallet_id,
        Currency(currency),
        Decimal(str(amount)),
        description
    )
    return transaction.to_dict()


@app.post("/api/v1/wallet/exchange", tags=["Wallet"])
async def exchange_currency(
    wallet_id: str,
    from_currency: str,
    to_currency: str,
    amount: float,
    fee_percentage: float = 0.001
):
    """Valyuta almashish"""
    from payment.multi_currency import Currency
    from decimal import Decimal
    
    transaction = await multi_currency_wallet.exchange(
        wallet_id,
        Currency(from_currency),
        Currency(to_currency),
        Decimal(str(amount)),
        Decimal(str(fee_percentage))
    )
    return transaction.to_dict()


@app.post("/api/v1/wallet/transfer", tags=["Wallet"])
async def transfer_between_wallets(
    from_wallet_id: str,
    to_wallet_id: str,
    currency: str,
    amount: float,
    description: str = None
):
    """Walletlar o'rtasida transfer"""
    from payment.multi_currency import Currency
    from decimal import Decimal
    
    transaction = await multi_currency_wallet.transfer(
        from_wallet_id,
        to_wallet_id,
        Currency(currency),
        Decimal(str(amount)),
        description
    )
    return transaction.to_dict()


@app.get("/api/v1/wallet/{wallet_id}/balance/{currency}", tags=["Wallet"])
async def get_wallet_balance(wallet_id: str, currency: str):
    """Wallet balansi"""
    from payment.multi_currency import Currency
    
    balance = await multi_currency_wallet.get_balance(wallet_id, Currency(currency))
    return balance.to_dict()


@app.get("/api/v1/wallet/{wallet_id}/balances/all", tags=["Wallet"])
async def get_all_wallet_balances(wallet_id: str):
    """Barcha balanslar"""
    balances = await multi_currency_wallet.get_all_balances(wallet_id)
    return balances


@app.get("/api/v1/wallet/{wallet_id}/transactions", tags=["Wallet"])
async def get_wallet_transactions(
    wallet_id: str,
    transaction_type: str = None,
    currency: str = None,
    limit: int = 100
):
    """Transaction tarixi"""
    from payment.multi_currency import TransactionType as WalletTransactionType, Currency
    
    txn_type = WalletTransactionType(transaction_type) if transaction_type else None
    curr = Currency(currency) if currency else None
    
    transactions = await multi_currency_wallet.get_transaction_history(
        wallet_id, txn_type, curr, limit
    )
    return [t.to_dict() for t in transactions]


@app.get("/api/v1/wallet/exchange-rate/{from_currency}/{to_currency}", tags=["Wallet"])
async def get_exchange_rate(from_currency: str, to_currency: str):
    """Exchange rate"""
    from payment.multi_currency import Currency
    
    rate = await multi_currency_wallet.get_exchange_rate(
        Currency(from_currency),
        Currency(to_currency)
    )
    return rate


@app.get("/api/v1/wallet/portfolio/{user_id}", tags=["Wallet"])
async def get_portfolio_summary(user_id: str):
    """Portfolio xulosasi"""
    summary = await multi_currency_wallet.get_portfolio_summary(user_id)
    return summary


@app.get("/api/v1/wallet/statistics", tags=["Wallet"])
async def get_wallet_statistics():
    """Wallet statistikasi"""
    stats = multi_currency_wallet.get_statistics()
    return stats


# =============================================================================
# TAX REPORTING ENDPOINTS
# =============================================================================

@app.post("/api/v1/tax/transactions/record", tags=["Tax"])
async def record_tax_transaction(
    user_id: str,
    date: str,
    transaction_type: str,
    asset: str,
    quantity: float,
    price: float,
    fee: float = 0,
    currency: str = "USD",
    description: str = None
):
    """Tax tranzaksiyasini yozish"""
    from payment.tax_reporting import TransactionType as TaxTransactionType
    from decimal import Decimal
    from datetime import datetime
    
    transaction = await tax_reporting.record_transaction(
        user_id,
        datetime.fromisoformat(date),
        TaxTransactionType(transaction_type),
        asset,
        Decimal(str(quantity)),
        Decimal(str(price)),
        Decimal(str(fee)),
        currency,
        description
    )
    return transaction.to_dict()


@app.post("/api/v1/tax/reports/annual", tags=["Tax"])
async def generate_annual_tax_report(user_id: str, year: int):
    """Yillik soliq hisoboti"""
    report = await tax_reporting.generate_annual_report(user_id, year)
    return report.to_dict()


@app.get("/api/v1/tax/reports/{report_id}", tags=["Tax"])
async def get_tax_report(report_id: str):
    """Tax report olish"""
    report = await tax_reporting.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report topilmadi")
    return report.to_dict()


@app.get("/api/v1/tax/reports/user/{user_id}", tags=["Tax"])
async def get_user_tax_reports(user_id: str):
    """Foydalanuvchi tax reportlari"""
    reports = await tax_reporting.get_user_reports(user_id)
    return [r.to_dict() for r in reports]


@app.post("/api/v1/tax/pnl-statement", tags=["Tax"])
async def generate_pnl_statement(user_id: str, start_date: str, end_date: str):
    """PnL statement yaratish"""
    from datetime import datetime
    
    statement = await tax_reporting.generate_pnl_statement(
        user_id,
        datetime.fromisoformat(start_date),
        datetime.fromisoformat(end_date)
    )
    return statement


@app.get("/api/v1/tax/reports/{report_id}/export/csv", tags=["Tax"])
async def export_tax_report_csv(report_id: str):
    """Tax reportni CSV ga export qilish"""
    from fastapi.responses import PlainTextResponse
    
    csv_content = await tax_reporting.export_to_csv(report_id)
    return PlainTextResponse(content=csv_content, media_type="text/csv")


@app.get("/api/v1/tax/tax-lots/{asset}", tags=["Tax"])
async def get_tax_lots(asset: str):
    """Asset uchun tax lots"""
    lots = await tax_reporting.get_tax_lots(asset)
    return [lot.to_dict() for lot in lots]


@app.get("/api/v1/tax/unrealized-gains/{user_id}", tags=["Tax"])
async def get_unrealized_gains(user_id: str):
    """Unrealized gains"""
    gains = await tax_reporting.get_unrealized_gains(user_id)
    return gains


@app.get("/api/v1/tax/statistics", tags=["Tax"])
async def get_tax_statistics():
    """Tax reporting statistikasi"""
    stats = tax_reporting.get_statistics()
    return stats


# =============================================================================
# WEBHOOK MANAGER ENDPOINTS
# =============================================================================

@app.post("/api/v1/webhooks/create", tags=["Webhooks"])
async def create_webhook(
    user_id: str,
    url: str,
    events: List[str],
    description: str = None,
    headers: Dict[str, str] = None
):
    """Webhook subscription yaratish"""
    from payment.webhook_manager import WebhookEvent as WHEvent
    
    event_enums = [WHEvent(e) for e in events]
    
    subscription = await webhook_manager.create_subscription(
        user_id, url, event_enums, description, headers
    )
    return subscription.to_dict()


@app.get("/api/v1/webhooks/{subscription_id}", tags=["Webhooks"])
async def get_webhook_subscription(subscription_id: str):
    """Webhook subscription ma'lumotlari"""
    subscription = await webhook_manager.get_subscription(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription topilmadi")
    return subscription.to_dict()


@app.get("/api/v1/webhooks/user/{user_id}", tags=["Webhooks"])
async def get_user_webhooks(user_id: str):
    """Foydalanuvchi webhook subscriptionlari"""
    subscriptions = await webhook_manager.get_user_subscriptions(user_id)
    return [s.to_dict() for s in subscriptions]


@app.put("/api/v1/webhooks/{subscription_id}", tags=["Webhooks"])
async def update_webhook(
    subscription_id: str,
    url: str = None,
    events: List[str] = None,
    status: str = None,
    headers: Dict[str, str] = None
):
    """Webhook subscriptionni yangilash"""
    from payment.webhook_manager import WebhookEvent as WHEvent, WebhookStatus
    
    event_enums = [WHEvent(e) for e in events] if events else None
    status_enum = WebhookStatus(status) if status else None
    
    subscription = await webhook_manager.update_subscription(
        subscription_id, url, event_enums, status_enum, headers
    )
    return subscription.to_dict()


@app.delete("/api/v1/webhooks/{subscription_id}", tags=["Webhooks"])
async def delete_webhook(subscription_id: str):
    """Webhook subscriptionni o'chirish"""
    success = await webhook_manager.delete_subscription(subscription_id)
    return {"success": success}


@app.post("/api/v1/webhooks/trigger", tags=["Webhooks"])
async def trigger_webhook_event(event_type: str, data: Dict[str, Any], user_id: str = None):
    """Webhook event trigger qilish"""
    from payment.webhook_manager import WebhookEvent as WHEvent
    
    event_enum = WHEvent(event_type)
    deliveries = await webhook_manager.trigger_event(event_enum, data, user_id)
    return [d.to_dict() for d in deliveries]


@app.get("/api/v1/webhooks/{subscription_id}/deliveries", tags=["Webhooks"])
async def get_webhook_deliveries(subscription_id: str, status: str = None, limit: int = 100):
    """Webhook delivery tarixi"""
    from payment.webhook_manager import DeliveryStatus
    
    status_enum = DeliveryStatus(status) if status else None
    deliveries = await webhook_manager.get_subscription_deliveries(
        subscription_id, status_enum, limit
    )
    return [d.to_dict() for d in deliveries]


@app.post("/api/v1/webhooks/{subscription_id}/test", tags=["Webhooks"])
async def test_webhook(subscription_id: str):
    """Webhook test qilish"""
    delivery = await webhook_manager.test_webhook(subscription_id)
    return delivery.to_dict()


@app.get("/api/v1/webhooks/events/history", tags=["Webhooks"])
async def get_event_history(user_id: str = None, event_type: str = None, limit: int = 100):
    """Event tarixi"""
    from payment.webhook_manager import WebhookEvent as WHEvent
    
    event_enum = WHEvent(event_type) if event_type else None
    events = await webhook_manager.get_event_history(user_id, event_enum, limit)
    return [e.to_dict() for e in events]


@app.post("/api/v1/webhooks/retry-failed", tags=["Webhooks"])
async def retry_failed_deliveries(subscription_id: str = None):
    """Failed deliverylarni retry qilish"""
    deliveries = await webhook_manager.retry_failed_deliveries(subscription_id)
    return [d.to_dict() for d in deliveries]


@app.get("/api/v1/webhooks/statistics", tags=["Webhooks"])
async def get_webhook_statistics():
    """Webhook statistikasi"""
    stats = webhook_manager.get_statistics()
    return stats


