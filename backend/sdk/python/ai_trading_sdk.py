"""
AI Trading Evolution - Python SDK
==================================
Official Python client library for AI Trading Evolution API

Author: MiniMax Agent
Version: 1.0.0
Date: 2025-11-04

Installation:
    pip install ai-trading-sdk

Usage:
    from ai_trading_sdk import TradingClient
    
    client = TradingClient(api_key="your-api-key")
    
    # Get market data
    data = await client.market.get_data("BTC/USDT")
    
    # Execute strategy
    signal = await client.strategy.execute("grid", "BTC/USDT")
    
    # Run analytics
    sentiment = await client.analytics.sentiment("BTC/USDT")
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import websockets


class APIError(Exception):
    """API error exception"""
    pass


class BaseClient:
    """Base API client"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def connect(self):
        """Initialize HTTP session"""
        if not self.session:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=self.timeout
            )
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request"""
        if not self.session:
            await self.connect()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(
                method,
                url,
                json=data,
                params=params
            ) as response:
                if response.status >= 400:
                    error_data = await response.json()
                    raise APIError(f"API Error {response.status}: {error_data.get('error', 'Unknown error')}")
                
                return await response.json()
        
        except aiohttp.ClientError as e:
            raise APIError(f"Connection error: {e}")
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET request"""
        return await self._request("GET", endpoint, params=params)
    
    async def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """POST request"""
        return await self._request("POST", endpoint, data=data)


class MarketAPI:
    """Market data API"""
    
    def __init__(self, client: BaseClient):
        self.client = client
    
    async def get_data(
        self,
        symbol: str,
        market_type: str = "crypto",
        timeframe: str = "1h",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get market data
        
        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            market_type: Market type (crypto, forex, stocks, commodities)
            timeframe: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles (1-1000)
        
        Returns:
            Market data dict
        """
        return await self.client.post("/api/v1/market/data", {
            "symbol": symbol,
            "market_type": market_type,
            "timeframe": timeframe,
            "limit": limit
        })
    
    async def list_symbols(self, market_type: str = "crypto") -> Dict[str, Any]:
        """
        Get list of available symbols
        
        Args:
            market_type: Market type (crypto, forex, stocks, commodities)
        
        Returns:
            Symbols dict
        """
        return await self.client.get(f"/api/v1/market/symbols?market_type={market_type}")


class StrategyAPI:
    """Trading strategy API"""
    
    def __init__(self, client: BaseClient):
        self.client = client
    
    async def execute(
        self,
        strategy_name: str,
        symbol: str,
        timeframe: str = "1h",
        parameters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute trading strategy
        
        Args:
            strategy_name: Strategy name (arbitrage, grid, dca, futures, mean_reversion, momentum)
            symbol: Trading pair
            timeframe: Timeframe
            parameters: Strategy parameters
        
        Returns:
            Strategy response with signal
        """
        return await self.client.post("/api/v1/strategy/execute", {
            "strategy_name": strategy_name,
            "symbol": symbol,
            "timeframe": timeframe,
            "parameters": parameters or {}
        })
    
    async def list(self) -> Dict[str, Any]:
        """
        Get list of available strategies
        
        Returns:
            Strategies dict
        """
        return await self.client.get("/api/v1/strategy/list")


class AnalyticsAPI:
    """Analytics API"""
    
    def __init__(self, client: BaseClient):
        self.client = client
    
    async def analyze(
        self,
        analysis_type: str,
        symbol: Optional[str] = None,
        parameters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Run analytics
        
        Args:
            analysis_type: Analysis type (sentiment, whale_tracking, risk_scoring, portfolio)
            symbol: Trading pair (optional)
            parameters: Analysis parameters
        
        Returns:
            Analysis results
        """
        return await self.client.post("/api/v1/analytics/analyze", {
            "analysis_type": analysis_type,
            "symbol": symbol,
            "parameters": parameters or {}
        })
    
    async def sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Get sentiment analysis
        
        Args:
            symbol: Trading pair
        
        Returns:
            Sentiment data
        """
        return await self.analyze("sentiment", symbol)
    
    async def risk_scoring(self, symbol: str) -> Dict[str, Any]:
        """
        Get risk scoring
        
        Args:
            symbol: Trading pair
        
        Returns:
            Risk metrics
        """
        return await self.analyze("risk_scoring", symbol)
    
    async def list_types(self) -> Dict[str, Any]:
        """
        Get list of analytics types
        
        Returns:
            Analytics types dict
        """
        return await self.client.get("/api/v1/analytics/types")


class WebSocketClient:
    """WebSocket client for real-time data"""
    
    def __init__(self, base_url: str = "ws://localhost:8000"):
        self.base_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
        self.client_id = None
        self.websocket = None
        self.subscriptions: List[str] = []
    
    async def connect(self, client_id: Optional[str] = None):
        """Connect to WebSocket"""
        if client_id:
            self.client_id = client_id
        else:
            import uuid
            self.client_id = str(uuid.uuid4())
        
        url = f"{self.base_url}/ws/{self.client_id}"
        self.websocket = await websockets.connect(url)
        
        # Receive welcome message
        welcome = await self.websocket.recv()
        print(f"Connected: {welcome}")
    
    async def subscribe(self, channel: str):
        """Subscribe to channel"""
        if not self.websocket:
            raise RuntimeError("Not connected")
        
        await self.websocket.send(json.dumps({
            "action": "subscribe",
            "channel": channel
        }))
        
        self.subscriptions.append(channel)
        
        # Wait for confirmation
        response = await self.websocket.recv()
        print(f"Subscribed: {response}")
    
    async def unsubscribe(self, channel: str):
        """Unsubscribe from channel"""
        if not self.websocket:
            raise RuntimeError("Not connected")
        
        await self.websocket.send(json.dumps({
            "action": "unsubscribe",
            "channel": channel
        }))
        
        if channel in self.subscriptions:
            self.subscriptions.remove(channel)
        
        # Wait for confirmation
        response = await self.websocket.recv()
        print(f"Unsubscribed: {response}")
    
    async def receive(self) -> Dict[str, Any]:
        """Receive message"""
        if not self.websocket:
            raise RuntimeError("Not connected")
        
        message = await self.websocket.recv()
        return json.loads(message)
    
    async def ping(self):
        """Send ping"""
        if not self.websocket:
            raise RuntimeError("Not connected")
        
        await self.websocket.send(json.dumps({"action": "ping"}))
        return await self.receive()
    
    async def close(self):
        """Close connection"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None


class TradingClient:
    """
    Main AI Trading Evolution client
    
    Example:
        async with TradingClient(api_key="your-key") as client:
            # Get market data
            data = await client.market.get_data("BTC/USDT")
            
            # Execute strategy
            signal = await client.strategy.execute("grid", "BTC/USDT")
            
            # Run analytics
            sentiment = await client.analytics.sentiment("BTC/USDT")
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        self._base_client = BaseClient(base_url, api_key, timeout)
        
        # API endpoints
        self.market = MarketAPI(self._base_client)
        self.strategy = StrategyAPI(self._base_client)
        self.analytics = AnalyticsAPI(self._base_client)
    
    async def __aenter__(self):
        await self._base_client.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._base_client.close()
    
    async def connect(self):
        """Connect to API"""
        await self._base_client.connect()
    
    async def close(self):
        """Close connection"""
        await self._base_client.close()
    
    async def health(self) -> Dict[str, Any]:
        """Get API health status"""
        return await self._base_client.get("/health")
    
    async def metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return await self._base_client.get("/metrics")
    
    def websocket(self) -> WebSocketClient:
        """Get WebSocket client"""
        ws_url = self._base_client.base_url.replace("http://", "ws://").replace("https://", "wss://")
        return WebSocketClient(ws_url)


# =============================================================================
# Synchronous wrapper (optional)
# =============================================================================

class SyncTradingClient:
    """
    Synchronous wrapper for TradingClient
    
    Example:
        client = SyncTradingClient(api_key="your-key")
        data = client.market.get_data("BTC/USDT")
        client.close()
    """
    
    def __init__(self, *args, **kwargs):
        self._async_client = TradingClient(*args, **kwargs)
        self._loop = asyncio.get_event_loop()
    
    def _run(self, coro):
        """Run async coroutine"""
        return self._loop.run_until_complete(coro)
    
    def __enter__(self):
        self._run(self._async_client.connect())
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._run(self._async_client.close())
    
    @property
    def market(self):
        """Market API"""
        class SyncMarketAPI:
            def __init__(self, async_api, loop):
                self._async_api = async_api
                self._loop = loop
            
            def get_data(self, *args, **kwargs):
                return self._loop.run_until_complete(
                    self._async_api.get_data(*args, **kwargs)
                )
            
            def list_symbols(self, *args, **kwargs):
                return self._loop.run_until_complete(
                    self._async_api.list_symbols(*args, **kwargs)
                )
        
        return SyncMarketAPI(self._async_client.market, self._loop)
    
    @property
    def strategy(self):
        """Strategy API"""
        class SyncStrategyAPI:
            def __init__(self, async_api, loop):
                self._async_api = async_api
                self._loop = loop
            
            def execute(self, *args, **kwargs):
                return self._loop.run_until_complete(
                    self._async_api.execute(*args, **kwargs)
                )
            
            def list(self):
                return self._loop.run_until_complete(
                    self._async_api.list()
                )
        
        return SyncStrategyAPI(self._async_client.strategy, self._loop)
    
    @property
    def analytics(self):
        """Analytics API"""
        class SyncAnalyticsAPI:
            def __init__(self, async_api, loop):
                self._async_api = async_api
                self._loop = loop
            
            def analyze(self, *args, **kwargs):
                return self._loop.run_until_complete(
                    self._async_api.analyze(*args, **kwargs)
                )
            
            def sentiment(self, *args, **kwargs):
                return self._loop.run_until_complete(
                    self._async_api.sentiment(*args, **kwargs)
                )
            
            def risk_scoring(self, *args, **kwargs):
                return self._loop.run_until_complete(
                    self._async_api.risk_scoring(*args, **kwargs)
                )
            
            def list_types(self):
                return self._loop.run_until_complete(
                    self._async_api.list_types()
                )
        
        return SyncAnalyticsAPI(self._async_client.analytics, self._loop)
    
    def health(self):
        """Get health status"""
        return self._run(self._async_client.health())
    
    def metrics(self):
        """Get metrics"""
        return self._run(self._async_client.metrics())
    
    def close(self):
        """Close connection"""
        self._run(self._async_client.close())
