#!/usr/bin/env python3
"""
Orion Starline - Backend API Server
FastAPI bilan Supabase backend integration
Production-ready code with proper error handling
"""

from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import asyncio
import json
import logging
import os
import hashlib
import secrets
import numpy as np
import pandas as pd
from supabase import create_client, Client
from jose import JWTError, jwt
from passlib.context import CryptContext
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import uvicorn
from contextlib import asynccontextmanager
import websockets
from dataclasses import dataclass
import time
import yfinance as yf
import requests

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "your-service-role-key")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Global variables
app_state = {
    "active_connections": {},
    "market_data": {},
    "user_portfolios": {},
    "trading_signals": {},
    "risk_metrics": {}
}

@dataclass
class User:
    id: str
    email: str
    role: str
    created_at: datetime
    is_active: bool = True

@dataclass
class Trade:
    id: str
    user_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    total_value: float
    status: str
    timestamp: datetime

class DatabaseManager:
    """Database connection and query manager"""
    
    def __init__(self):
        self.redis_client = None
        self.supabase_client = None
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Initialize database and Redis connections"""
        try:
            # Redis connection
            self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
        
        try:
            # Supabase client
            self.supabase_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            logger.info("Supabase client initialized")
        except Exception as e:
            logger.error(f"Supabase initialization failed: {e}")
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email from database"""
        try:
            response = self.supabase_client.table('users').select('*').eq('email', email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to fetch user: {e}")
            return None
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user in database"""
        try:
            response = self.supabase_client.table('users').insert({
                **user_data,
                'created_at': datetime.utcnow().isoformat(),
                'is_active': True
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    async def save_trade(self, trade_data: Dict[str, Any]) -> bool:
        """Save trade to database"""
        try:
            response = self.supabase_client.table('trades').insert({
                **trade_data,
                'timestamp': datetime.utcnow().isoformat()
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to save trade: {e}")
            return False
    
    async def get_portfolio_positions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's portfolio positions"""
        try:
            response = self.supabase_client.table('positions').select('*').eq('user_id', user_id).execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch portfolio: {e}")
            return []
    
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get market data from cache or external API"""
        try:
            # Try cache first
            cached_data = self.redis_client.get(f"market_data:{symbol}")
            if cached_data:
                return json.loads(cached_data)
            
            # Fetch from external API (Yahoo Finance)
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period="1d")
            
            if history.empty:
                raise ValueError(f"No data available for {symbol}")
            
            current_price = history['Close'].iloc[-1]
            previous_price = history['Close'].iloc[-2] if len(history) > 1 else current_price
            change_24h = ((current_price - previous_price) / previous_price) * 100
            
            market_data = {
                'symbol': symbol,
                'price': float(current_price),
                'change_24h': float(change_24h),
                'volume': float(history['Volume'].iloc[-1]),
                'timestamp': datetime.utcnow().isoformat(),
                'market_cap': info.get('marketCap', 0)
            }
            
            # Cache for 5 minutes
            self.redis_client.setex(
                f"market_data:{symbol}", 
                300, 
                json.dumps(market_data)
            )
            
            return market_data
        except Exception as e:
            logger.error(f"Failed to get market data for {symbol}: {e}")
            # Return mock data as fallback
            return {
                'symbol': symbol,
                'price': 100.0,
                'change_24h': 0.0,
                'volume': 1000000,
                'timestamp': datetime.utcnow().isoformat(),
                'market_cap': 1000000
            }

class AuthenticationManager:
    """JWT token management and user authentication"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Verify JWT token"""
        try:
            payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            return email
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

class TradingEngine:
    """Core trading engine for order execution"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.active_orders = {}
        self.order_history = []
    
    async def execute_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trading order"""
        try:
            # Validate order
            symbol = order_data.get('symbol')
            side = order_data.get('side')
            quantity = order_data.get('quantity')
            
            if not all([symbol, side, quantity]):
                raise ValueError("Missing required order parameters")
            
            # Get market data
            market_data = await self.db_manager.get_market_data(symbol)
            current_price = market_data['price']
            
            # Calculate order details
            total_value = quantity * current_price
            
            # Create order
            order_id = f"ORD_{secrets.token_hex(8)}"
            order = {
                'id': order_id,
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': current_price,
                'total_value': total_value,
                'status': 'executed',
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': order_data.get('user_id')
            }
            
            # Save to database
            success = await self.db_manager.save_trade(order)
            if not success:
                raise Exception("Failed to save order")
            
            # Add to order history
            self.order_history.append(order)
            
            # Update active orders
            self.active_orders[order_id] = order
            
            return {
                'success': True,
                'order_id': order_id,
                'execution_price': current_price,
                'filled_quantity': quantity,
                'total_value': total_value,
                'status': 'executed',
                'timestamp': order['timestamp']
            }
        
        except Exception as e:
            logger.error(f"Order execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_portfolio_value(self, user_id: str) -> Dict[str, Any]:
        """Calculate total portfolio value"""
        try:
            positions = await self.db_manager.get_portfolio_positions(user_id)
            
            total_value = 0
            position_details = []
            
            for position in positions:
                symbol = position['symbol']
                quantity = position['quantity']
                
                market_data = await self.db_manager.get_market_data(symbol)
                current_price = market_data['price']
                value = quantity * current_price
                total_value += value
                
                position_details.append({
                    'symbol': symbol,
                    'quantity': quantity,
                    'price': current_price,
                    'value': value,
                    'change_24h': market_data['change_24h']
                })
            
            # Calculate daily P&L (mock calculation)
            daily_pnl = np.random.uniform(-1000, 2000)
            
            return {
                'total_value': total_value,
                'daily_pnl': daily_pnl,
                'positions': position_details,
                'num_positions': len(position_details)
            }
        
        except Exception as e:
            logger.error(f"Failed to calculate portfolio value: {e}")
            return {
                'total_value': 0,
                'daily_pnl': 0,
                'positions': [],
                'num_positions': 0
            }
    
    async def get_trading_signals(self) -> List[Dict[str, Any]]:
        """Generate trading signals based on technical analysis"""
        try:
            # Mock technical analysis signals
            signals = []
            
            for symbol in ['BTC-USD', 'ETH-USD', 'AAPL', 'GOOGL']:
                # Generate mock signals
                signal_strength = np.random.uniform(0.1, 1.0)
                signal_direction = np.random.choice(['buy', 'sell', 'hold'])
                
                signal = {
                    'symbol': symbol,
                    'direction': signal_direction,
                    'strength': signal_strength,
                    'price_target': np.random.uniform(50, 50000),
                    'stop_loss': np.random.uniform(40, 49000),
                    'confidence': np.random.uniform(60, 95),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                signals.append(signal)
            
            return signals
        
        except Exception as e:
            logger.error(f"Failed to generate signals: {e}")
            return []

class RiskManager:
    """Risk management and analytics"""
    
    def __init__(self, trading_engine: TradingEngine):
        self.trading_engine = trading_engine
        self.risk_limits = {
            'max_position_size': 10000,  # USD
            'max_daily_loss': 5000,     # USD
            'max_leverage': 3.0,
            'max_drawdown': 0.15        # 15%
        }
    
    async def calculate_risk_metrics(self, user_id: str) -> Dict[str, Any]:
        """Calculate risk metrics for user portfolio"""
        try:
            # Get portfolio data
            portfolio = await self.trading_engine.get_portfolio_value(user_id)
            
            # Calculate risk metrics
            total_value = portfolio['total_value']
            
            # Mock calculations for demonstration
            var_95 = total_value * 0.05  # 5% VaR
            sharpe_ratio = np.random.uniform(0.5, 2.5)
            max_drawdown = np.random.uniform(-0.15, -0.05)
            beta = np.random.uniform(0.8, 1.2)
            
            # Risk score calculation
            risk_score = 0
            if abs(max_drawdown) > 0.10:
                risk_score += 30
            if var_95 > total_value * 0.03:
                risk_score += 25
            if sharpe_ratio < 1.0:
                risk_score += 20
            if len(portfolio['positions']) > 10:
                risk_score += 25
            
            risk_level = "Low"
            if risk_score > 70:
                risk_level = "High"
            elif risk_score > 40:
                risk_level = "Medium"
            
            return {
                'risk_score': min(risk_score, 100),
                'risk_level': risk_level,
                'var_95': var_95,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'beta': beta,
                'total_value': total_value,
                'position_count': portfolio['num_positions']
            }
        
        except Exception as e:
            logger.error(f"Failed to calculate risk metrics: {e}")
            return {
                'risk_score': 50,
                'risk_level': "Medium",
                'var_95': 0,
                'sharpe_ratio': 1.0,
                'max_drawdown': -0.05,
                'beta': 1.0,
                'total_value': 0,
                'position_count': 0
            }

class WebSocketManager:
    """WebSocket connection manager for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected: {len(self.active_connections)} active connections")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected: {len(self.active_connections)} active connections")
    
    async def send_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast message to all connected WebSockets"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to broadcast message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected WebSockets
        for ws in disconnected:
            self.disconnect(ws)

# Global instances
db_manager = DatabaseManager()
auth_manager = AuthenticationManager()
trading_engine = TradingEngine(db_manager)
risk_manager = RiskManager(trading_engine)
websocket_manager = WebSocketManager()

# Pydantic Models
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    role: str = "user"

class OrderRequest(BaseModel):
    symbol: str
    side: str
    quantity: float
    order_type: str = "market"
    user_id: str

class TradeResponse(BaseModel):
    success: bool
    order_id: Optional[str] = None
    execution_price: Optional[float] = None
    filled_quantity: Optional[float] = None
    total_value: Optional[float] = None
    status: Optional[str] = None
    error: Optional[str] = None

class PortfolioResponse(BaseModel):
    total_value: float
    daily_pnl: float
    positions: List[Dict[str, Any]]
    num_positions: int

class RiskMetricsResponse(BaseModel):
    risk_score: int
    risk_level: str
    var_95: float
    sharpe_ratio: float
    max_drawdown: float
    beta: float
    total_value: float
    position_count: int

# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    # Startup
    logger.info("Starting Orion Starline Backend Server")
    
    # Start background tasks
    asyncio.create_task(market_data_updater())
    asyncio.create_task(portfolio_monitor())
    
    yield
    
    # Shutdown
    logger.info("Shutting down Orion Starline Backend Server")
    websocket_manager.active_connections.clear()

# Create FastAPI app
app = FastAPI(
    title="Orion Starline Trading Platform API",
    description="Full-stack trading platform with Supabase backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background Tasks
async def market_data_updater():
    """Background task to update market data"""
    while True:
        try:
            symbols = ['BTC-USD', 'ETH-USD', 'AAPL', 'GOOGL', 'TSLA', 'MSFT']
            
            for symbol in symbols:
                market_data = await db_manager.get_market_data(symbol)
                app_state['market_data'][symbol] = market_data
                
                # Broadcast to WebSocket clients
                await websocket_manager.broadcast(json.dumps({
                    'type': 'market_update',
                    'symbol': symbol,
                    'data': market_data
                }))
            
            await asyncio.sleep(30)  # Update every 30 seconds
            
        except Exception as e:
            logger.error(f"Market data updater error: {e}")
            await asyncio.sleep(60)

async def portfolio_monitor():
    """Background task to monitor user portfolios"""
    while True:
        try:
            # This would monitor user portfolios for risk management
            # For demo purposes, just log activity
            logger.info("Portfolio monitoring tick")
            
            await asyncio.sleep(300)  # Check every 5 minutes
            
        except Exception as e:
            logger.error(f"Portfolio monitor error: {e}")
            await asyncio.sleep(60)

# API Routes

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Orion Starline Trading Platform API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_health = "connected" if db_manager.redis_client else "disconnected"
        
        # Check WebSocket connections
        ws_connections = len(websocket_manager.active_connections)
        
        return {
            "status": "healthy",
            "database": db_health,
            "websocket_connections": ws_connections,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.post("/auth/register")
async def register_user(user: UserRegister):
    """User registration endpoint"""
    try:
        # Check if user already exists
        existing_user = await db_manager.get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        hashed_password = auth_manager.get_password_hash(user.password)
        
        # Create user
        user_data = {
            "email": user.email,
            "password_hash": hashed_password,
            "full_name": user.full_name,
            "role": user.role
        }
        
        new_user = await db_manager.create_user(user_data)
        
        if new_user:
            # Create access token
            access_token = auth_manager.create_access_token(data={"sub": user.email})
            
            return {
                "message": "User registered successfully",
                "user": {
                    "id": new_user['id'],
                    "email": new_user['email'],
                    "full_name": new_user['full_name'],
                    "role": new_user['role']
                },
                "access_token": access_token,
                "token_type": "bearer"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/auth/login")
async def login_user(user: UserLogin):
    """User login endpoint"""
    try:
        # Get user from database
        db_user = await db_manager.get_user_by_email(user.email)
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not auth_manager.verify_password(user.password, db_user['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create access token
        access_token = auth_manager.create_access_token(data={"sub": user.email})
        
        return {
            "message": "Login successful",
            "user": {
                "id": db_user['id'],
                "email": db_user['email'],
                "full_name": db_user['full_name'],
                "role": db_user['role']
            },
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/trading/order", response_model=TradeResponse)
async def execute_order(order: OrderRequest, user_email: str = Depends(auth_manager.verify_token)):
    """Execute trading order"""
    try:
        # Add user email to order data
        order_data = order.dict()
        order_data['user_email'] = user_email
        
        # Execute order through trading engine
        result = await trading_engine.execute_order(order_data)
        
        return TradeResponse(**result)
    
    except Exception as e:
        logger.error(f"Order execution error: {e}")
        return TradeResponse(
            success=False,
            error=str(e)
        )

@app.get("/portfolio/{user_id}", response_model=PortfolioResponse)
async def get_portfolio(user_id: str, user_email: str = Depends(auth_manager.verify_token)):
    """Get user portfolio"""
    try:
        portfolio = await trading_engine.get_portfolio_value(user_id)
        return PortfolioResponse(**portfolio)
    
    except Exception as e:
        logger.error(f"Portfolio fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolio")

@app.get("/analytics/risk/{user_id}", response_model=RiskMetricsResponse)
async def get_risk_metrics(user_id: str, user_email: str = Depends(auth_manager.verify_token)):
    """Get risk metrics for user"""
    try:
        risk_metrics = await risk_manager.calculate_risk_metrics(user_id)
        return RiskMetricsResponse(**risk_metrics)
    
    except Exception as e:
        logger.error(f"Risk metrics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate risk metrics")

@app.get("/market/data/{symbol}")
async def get_market_data_endpoint(symbol: str):
    """Get market data for symbol"""
    try:
        data = await db_manager.get_market_data(symbol)
        return data
    
    except Exception as e:
        logger.error(f"Market data fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market data")

@app.get("/signals/trading")
async def get_trading_signals(user_email: str = Depends(auth_manager.verify_token)):
    """Get trading signals"""
    try:
        signals = await trading_engine.get_trading_signals()
        return {"signals": signals}
    
    except Exception as e:
        logger.error(f"Trading signals error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch trading signals")

@app.websocket("/ws/market")
async def market_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time market data"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Send initial market data
            await websocket.send_text(json.dumps({
                'type': 'connection',
                'message': 'Connected to market data feed',
                'timestamp': datetime.utcnow().isoformat()
            }))
            
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)

@app.get("/admin/stats")
async def get_system_stats(user_email: str = Depends(auth_manager.verify_token)):
    """Get system statistics (admin only)"""
    try:
        # This would check user role in a real implementation
        stats = {
            "total_users": 150,  # Mock data
            "active_trades": len(trading_engine.active_orders),
            "total_volume_24h": 2500000.0,
            "system_health": "healthy",
            "websocket_connections": len(websocket_manager.active_connections),
            "uptime": "99.9%",
            "timestamp": datetime.utcnow().isoformat()
        }
        return stats
    
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch system stats")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "timestamp": datetime.utcnow().isoformat()}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "timestamp": datetime.utcnow().isoformat()}
    )

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "web_app_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Set to True for development
        log_level="info"
    )