#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orion Starline API Integrations Hub
====================================

Bu modul turli xil trading, ma'lumotlar va xizmatlar API-larini birlashtiruvchi
universal integratsiya markazi hisoblanadi.

Xususiyatlari:
- Trading platform integrations (MetaTrader, Interactive Brokers, Alpaca)
- Real-time market data va news feeds
- Broker APIs (order execution, account management)
- Portfolio management APIs
- Economic data APIs
- News va social sentiment APIs
- Payment processing (Stripe, PayPal)
- Communication APIs (Slack, Discord)
- Cloud storage APIs (AWS S3, Google Cloud)

Texnik xususiyatlari:
- Universal API client framework
- Rate limiting va retry mechanisms
- Authentication management
- Data transformation utilities
- Error handling va logging
- API monitoring va health checks

@author: Orion Starline Development Team
@version: 1.0.0
@date: 2025-11-05
"""

import asyncio
import aiohttp
import json
import time
import logging
import os
import ssl
import websockets
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from functools import wraps
import hashlib
import hmac
import jwt
import base64
import boto3
from botocore.exceptions import ClientError
import stripe
import paypalrestsdk
import tweepy
import praw
import schedule
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import backoff
from collections import defaultdict, deque
import socket
import ssl

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_integrations_hub.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# BASE CLASSES VA INTERFACES
# =============================================================================

class APIStatus(Enum):
    """API holat turlari"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"

class APICategory(Enum):
    """API kategoriyasi"""
    TRADING = "trading"
    DATA_FEED = "data_feed"
    BROKER = "broker"
    PORTFOLIO = "portfolio"
    ECONOMIC = "economic"
    NEWS = "news"
    SOCIAL = "social"
    PAYMENT = "payment"
    COMMUNICATION = "communication"
    STORAGE = "storage"

@dataclass
class APIConfig:
    """API konfiguratsiyasi"""
    name: str
    category: APICategory
    base_url: str
    auth_type: str  # 'api_key', 'oauth', 'basic', 'bearer'
    credentials: Dict[str, str]
    rate_limit: int = 100  # requests per minute
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    enabled: bool = True

@dataclass
class APIResponse:
    """API javob struktura"""
    status_code: int
    data: Any
    success: bool
    message: str
    timestamp: datetime
    execution_time: float
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[int] = None

@dataclass
class HealthCheckResult:
    """API health check natija"""
    api_name: str
    status: APIStatus
    response_time: float
    last_success: datetime
    error_count: int
    message: str

# =============================================================================
# BASE API CLIENT
# =============================================================================

class BaseAPIClient(ABC):
    """Barcha API clientlar uchun asosiy sinf"""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.status = APIStatus.INACTIVE
        self.last_success = None
        self.error_count = 0
        self.success_count = 0
        self.request_history = deque(maxlen=1000)
        self.rate_limiter = RateLimiter(config.rate_limit)
        self.session = None
        
    async def __aenter__(self):
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
        
    async def initialize(self):
        """API session initialize qilish"""
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=30,
            ssl=False
        )
        
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        self.status = APIStatus.ACTIVE
        logger.info(f"API client initialized: {self.config.name}")
        
    async def cleanup(self):
        """Resource cleanup"""
        if self.session:
            await self.session.close()
            
    @abstractmethod
    async def _authenticate(self, request: aiohttp.ClientRequest) -> aiohttp.ClientRequest:
        """Authentication qilish"""
        pass
        
    @abstractmethod
    async def make_request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Any = None,
        headers: Dict[str, str] = None,
        **kwargs
    ) -> APIResponse:
        """API request qilish"""
        pass
        
    def _log_request(self, method: str, endpoint: str, start_time: float, success: bool, message: str):
        """Request log qilish"""
        execution_time = time.time() - start_time
        
        self.request_history.append({
            'timestamp': datetime.now(),
            'method': method,
            'endpoint': endpoint,
            'execution_time': execution_time,
            'success': success,
            'message': message
        })
        
        if success:
            self.success_count += 1
            self.last_success = datetime.now()
            self.error_count = 0
        else:
            self.error_count += 1
            
        logger.info(f"{method} {endpoint} - {execution_time:.2f}s - {success}")

# =============================================================================
# RATE LIMITING VA RETRY MECHANISMS
# =============================================================================

class RateLimiter:
    """Rate limiting qilish uchun sinf"""
    
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.requests = deque()
        
    async def acquire(self):
        """Rate limit kontrol qilish"""
        now = time.time()
        
        # Bir daqiqa oldingi requestlarni o'chirish
        while self.requests and now - self.requests[0] >= 60:
            self.requests.popleft()
            
        # Limit tekshirish
        if len(self.requests) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.requests[0])
            if sleep_time > 0:
                logger.warning(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
                return await self.acquire()
                
        self.requests.append(now)

def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    exponential_base: float = 2.0,
    exceptions: Tuple = (Exception,)
):
    """Retry decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        break
                        
                    wait_time = delay * (exponential_base ** attempt)
                    logger.warning(f"Retry {attempt + 1}/{max_retries} after {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    
            raise last_exception
        return wrapper
    return decorator

# =============================================================================
# AUTHENTICATION MANAGERS
# =============================================================================

class AuthManager:
    """Authentication management uchun sinf"""
    
    def __init__(self):
        self.auth_cache = {}
        self.jwt_secrets = {}
        
    async def authenticate(self, auth_type: str, credentials: Dict[str, str]) -> Dict[str, str]:
        """Authentication qilish"""
        if auth_type == "api_key":
            return {"X-API-Key": credentials.get("api_key")}
        elif auth_type == "bearer":
            return {"Authorization": f"Bearer {credentials.get('token')}"}
        elif auth_type == "basic":
            import base64
            auth_string = f"{credentials.get('username')}:{credentials.get('password')}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            return {"Authorization": f"Basic {auth_b64}"}
        elif auth_type == "oauth2":
            return await self._get_oauth2_token(credentials)
        elif auth_type == "custom":
            return await self._custom_auth(credentials)
        else:
            raise ValueError(f"Unknown auth type: {auth_type}")
            
    async def _get_oauth2_token(self, credentials: Dict[str, str]) -> Dict[str, str]:
        """OAuth2 token olish"""
        # Bu yerda OAuth2 token olish logikasini yozish
        token = credentials.get("access_token")
        if not token:
            # Token yo'q bo'lsa, refresh qilish
            token = await self._refresh_oauth2_token(credentials)
        return {"Authorization": f"Bearer {token}"}
        
    async def _refresh_oauth2_token(self, credentials: Dict[str, str]) -> str:
        """OAuth2 token refresh qilish"""
        refresh_token = credentials.get("refresh_token")
        client_id = credentials.get("client_id")
        client_secret = credentials.get("client_secret")
        
        # Bu yerda actual OAuth2 refresh logic
        # Hozircha mock implementation
        return "refreshed_token_12345"
        
    async def _custom_auth(self, credentials: Dict[str, str]) -> Dict[str, str]:
        """Custom authentication"""
        # HMAC signature yaratish
        if "hmac_key" in credentials and "message" in credentials:
            signature = hmac.new(
                credentials["hmac_key"].encode(),
                credentials["message"].encode(),
                hashlib.sha256
            ).hexdigest()
            return {"X-HMAC-Signature": signature}
            
        return {}

# =============================================================================
# TRADING PLATFORM INTEGRATIONS
# =============================================================================

class MetaTraderClient(BaseAPIClient):
    """MetaTrader 4/5 integratsiyasi"""
    
    def __init__(self, config: APIConfig):
        super().__init__(config)
        self.terminal_path = config.credentials.get("terminal_path", "")
        self.expert_advisor = config.credentials.get("expert_advisor", "")
        
    async def _authenticate(self, request: aiohttp.ClientRequest) -> aiohttp.ClientRequest:
        """MT4/5 authentication"""
        # MetaTerminal API authentication
        headers = {"X-MT-Auth": self.config.credentials.get("terminal_auth")}
        request.headers.update(headers)
        return request
        
    async def make_request(self, endpoint: str, method: str = "GET", data: Any = None, headers: Dict[str, str] = None, **kwargs) -> APIResponse:
        """MetaTrader API request"""
        await self.rate_limiter.acquire()
        start_time = time.time()
        
        try:
            if not headers:
                headers = {}
            headers.update(await self._authenticate(aiohttp.ClientRequest(method, endpoint)))
            
            async with self.session.request(method, endpoint, json=data, headers=headers) as response:
                response_data = await response.json()
                
                success = response.status < 400
                message = "Success" if success else f"HTTP {response.status}"
                
                api_response = APIResponse(
                    status_code=response.status,
                    data=response_data,
                    success=success,
                    message=message,
                    timestamp=datetime.now(),
                    execution_time=time.time() - start_time,
                    rate_limit_remaining=response.headers.get('X-RateLimit-Remaining'),
                    rate_limit_reset=response.headers.get('X-RateLimit-Reset')
                )
                
                self._log_request(method, endpoint, start_time, success, message)
                return api_response
                
        except Exception as e:
            self._log_request(method, endpoint, start_time, False, str(e))
            return APIResponse(
                status_code=500,
                data=None,
                success=False,
                message=str(e),
                timestamp=datetime.now(),
                execution_time=time.time() - start_time
            )
            
    async def place_order(self, symbol: str, order_type: str, volume: float, price: float = 0, sl: float = 0, tp: float = 0) -> APIResponse:
        """Buyurtma qo'yish"""
        endpoint = f"{self.config.base_url}/orders"
        data = {
            "symbol": symbol,
            "type": order_type,
            "volume": volume,
            "price": price,
            "sl": sl,
            "tp": tp
        }
        return await self.make_request(endpoint, "POST", data)
        
    async def get_positions(self) -> APIResponse:
        """Pozitsiyalar olish"""
        endpoint = f"{self.config.base_url}/positions"
        return await self.make_request(endpoint)
        
    async def get_account_info(self) -> APIResponse:
        """Hisob ma'lumotlari"""
        endpoint = f"{self.config.base_url}/account"
        return await self.make_request(endpoint)

class InteractiveBrokersClient(BaseAPIClient):
    """Interactive Brokers API integratsiyasi"""
    
    def __init__(self, config: APIConfig):
        super().__init__(config)
        self.client_id = config.credentials.get("client_id", "")
        
    async def _authenticate(self, request: aiohttp.ClientRequest) -> aiohttp.ClientRequest:
        """IB authentication"""
        headers = {
            "X-IB-ClientId": self.client_id,
            "X-IB-AuthToken": self.config.credentials.get("auth_token")
        }
        request.headers.update(headers)
        return request
        
    @retry_on_failure(max_retries=3)
    async def make_request(self, endpoint: str, method: str = "GET", data: Any = None, headers: Dict[str, str] = None, **kwargs) -> APIResponse:
        """IB API request"""
        await self.rate_limiter.acquire()
        start_time = time.time()
        
        try:
            if not headers:
                headers = {}
            headers.update(await self._authenticate(aiohttp.ClientRequest(method, endpoint)))
            
            async with self.session.request(method, endpoint, json=data, headers=headers) as response:
                response_data = await response.json()
                
                success = response.status < 400
                message = "Success" if success else f"HTTP {response.status}"
                
                api_response = APIResponse(
                    status_code=response.status,
                    data=response_data,
                    success=success,
                    message=message,
                    timestamp=datetime.now(),
                    execution_time=time.time() - start_time
                )
                
                self._log_request(method, endpoint, start_time, success, message)
                return api_response
                
        except Exception as e:
            self._log_request(method, endpoint, start_time, False, str(e))
            raise e
            
    async def place_order(self, contract: Dict, order: Dict) -> APIResponse:
        """Buyurtma qo'yish"""
        endpoint = f"{self.config.base_url}/v1/api/iserver/account/{self.client_id}/orders"
        data = {
            "conids": [contract.get("conid")],
            "orders": [order]
        }
        return await self.make_request(endpoint, "POST", data)
        
    async def get_portfolio(self) -> APIResponse:
        """Portfolio ma'lumotlari"""
        endpoint = f"{self.config.base_url}/v1/api/portfolio/accounts"
        return await self.make_request(endpoint)

class AlpacaClient(BaseAPIClient):
    """Alpaca Trading API integratsiyasi"""
    
    def __init__(self, config: APIConfig):
        super().__init__(config)
        
    async def _authenticate(self, request: aiohttp.ClientRequest) -> aiohttp.ClientRequest:
        """Alpaca authentication"""
        headers = {
            "APCA-API-KEY-ID": self.config.credentials.get("api_key"),
            "APCA-API-SECRET-KEY": self.config.credentials.get("secret_key")
        }
        request.headers.update(headers)
        return request
        
    @retry_on_failure(max_retries=3)
    async def make_request(self, endpoint: str, method: str = "GET", data: Any = None, headers: Dict[str, str] = None, **kwargs) -> APIResponse:
        """Alpaca API request"""
        await self.rate_limiter.acquire()
        start_time = time.time()
        
        try:
            if not headers:
                headers = {}
            headers.update(await self._authenticate(aiohttp.ClientRequest(method, endpoint)))
            
            async with self.session.request(method, endpoint, json=data, headers=headers) as response:
                response_data = await response.json()
                
                success = response.status < 400
                message = "Success" if success else f"HTTP {response.status}"
                
                api_response = APIResponse(
                    status_code=response.status,
                    data=response_data,
                    success=success,
                    message=message,
                    timestamp=datetime.now(),
                    execution_time=time.time() - start_time,
                    rate_limit_remaining=response.headers.get('X-RateLimit-Remaining'),
                    rate_limit_reset=response.headers.get('X-RateLimit-Reset')
                )
                
                self._log_request(method, endpoint, start_time, success, message)
                return api_response
                
        except Exception as e:
            self._log_request(method, endpoint, start_time, False, str(e))
            raise e
            
    async def place_order(
        self, 
        symbol: str, 
        qty: float, 
        side: str, 
        type: str = "market", 
        time_in_force: str = "day",
        limit_price: float = None,
        stop_price: float = None
    ) -> APIResponse:
        """Buyurtma qo'yish"""
        endpoint = f"{self.config.base_url}/v2/orders"
        data = {
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": type,
            "time_in_force": time_in_force
        }
        
        if limit_price:
            data["limit_price"] = limit_price
        if stop_price:
            data["stop_price"] = stop_price
            
        return await self.make_request(endpoint, "POST", data)
        
    async def get_account(self) -> APIResponse:
        """Hisob ma'lumotlari"""
        endpoint = f"{self.config.base_url}/v2/account"
        return await self.make_request(endpoint)
        
    async def get_positions(self) -> APIResponse:
        """Pozitsiyalar"""
        endpoint = f"{self.config.base_url}/v2/positions"
        return await self.make_request(endpoint)

# =============================================================================
# DATA FEEDS INTEGRATIONS
# =============================================================================

class RealTimeMarketDataClient(BaseAPIClient):
    """Real-time market data API"""
    
    def __init__(self, config: APIConfig):
        super().__init__(config)
        self.websocket = None
        
    async def _authenticate(self, request: aiohttp.ClientRequest) -> aiohttp.ClientRequest:
        """Data feed authentication"""
        headers = {
            "X-API-Key": self.config.credentials.get("api_key"),
            "Authorization": f"Bearer {self.config.credentials.get('token')}"
        }
        request.headers.update(headers)
        return request
        
    async def make_request(self, endpoint: str, method: str = "GET", data: Any = None, headers: Dict[str, str] = None, **kwargs) -> APIResponse:
        """Market data API request"""
        await self.rate_limiter.acquire()
        start_time = time.time()
        
        try:
            if not headers:
                headers = {}
            headers.update(await self._authenticate(aiohttp.ClientRequest(method, endpoint)))
            
            async with self.session.request(method, endpoint, json=data, headers=headers) as response:
                response_data = await response.json()
                
                success = response.status < 400
                message = "Success" if success else f"HTTP {response.status}"
                
                api_response = APIResponse(
                    status_code=response.status,
                    data=response_data,
                    success=success,
                    message=message,
                    timestamp=datetime.now(),
                    execution_time=time.time() - start_time
                )
                
                self._log_request(method, endpoint, start_time, success, message)
                return api_response
                
        except Exception as e:
            self._log_request(method, endpoint, start_time, False, str(e))
            return APIResponse(
                status_code=500,
                data=None,
                success=False,
                message=str(e),
                timestamp=datetime.now(),
                execution_time=time.time() - start_time
            )
            
    async def get_live_quotes(self, symbols: List[str]) -> APIResponse:
        """Real-time narxlar"""
        symbols_str = ",".join(symbols)
        endpoint = f"{self.config.base_url}/quotes/live?symbols={symbols_str}"
        return await self.make_request(endpoint)
        
    async def get_historical_data(self, symbol: str, interval: str = "1d", limit: int = 100) -> APIResponse:
        """Tarixiy ma'lumotlar"""
        endpoint = f"{self.config.base_url}/historical/{symbol}?interval={interval}&limit={limit}"
        return await self.make_request(endpoint)
        
    async def connect_websocket(self, symbols: List[str], callback: Callable) -> None:
        """WebSocket orqali real-time ma'lumotlar"""
        ws_endpoint = self.config.base_url.replace("https://", "wss://") + "/websocket"
        
        try:
            async with websockets.connect(ws_endpoint) as websocket:
                self.websocket = websocket
                
                # Subscribe qilish
                subscribe_msg = {
                    "action": "subscribe",
                    "symbols": symbols
                }
                await websocket.send(json.dumps(subscribe_msg))
                
                # Ma'lumotlarni olish
                async for message in websocket:
                    data = json.loads(message)
                    await callback(data)
                    
        except Exception as e:
            logger.error(f"WebSocket error: {e}")

class NewsFeedClient(BaseAPIClient):
    """News feed API"""
    
    async def _authenticate(self, request: aiohttp.ClientRequest) -> aiohttp.ClientRequest:
        """News API authentication"""
        headers = {
            "X-API-Key": self.config.credentials.get("api_key")
        }
        request.headers.update(headers)
        return request
        
    @retry_on_failure(max_retries=3)
    async def make_request(self, endpoint: str, method: str = "GET", data: Any = None, headers: Dict[str, str] = None, **kwargs) -> APIResponse:
        """News API request"""
        await self.rate_limiter.acquire()
        start_time = time.time()
        
        try:
            if not headers:
                headers = {}
            headers.update(await self._authenticate(aiohttp.ClientRequest(method, endpoint)))
            
            async with self.session.request(method, endpoint, json=data, headers=headers) as response:
                response_data = await response.json()
                
                success = response.status < 400
                message = "Success" if success else f"HTTP {response.status}"
                
                api_response = APIResponse(
                    status_code=response.status,
                    data=response_data,
                    success=success,
                    message=message,
                    timestamp=datetime.now(),
                    execution_time=time.time() - start_time
                )
                
                self._log_request(method, endpoint, start_time, success, message)
                return api_response
                
        except Exception as e:
            self._log_request(method, endpoint, start_time, False, str(e))
            raise e
            
    async def get_market_news(self, category: str = "business", limit: int = 50) -> APIResponse:
        """Bozor yangiliklari"""
        endpoint = f"{self.config.base_url}/news?category={category}&limit={limit}"
        return await self.make_request(endpoint)
        
    async def get_stock_news(self, symbol: str) -> APIResponse:
        """Aksiya yangiliklari"""
        endpoint = f"{self.config.base_url}/stock-news/{symbol}"
        return await self.make_request(endpoint)

# =============================================================================
# ECONOMIC DATA INTEGRATIONS
# =============================================================================

class EconomicDataClient(BaseAPIClient):
    """Iqtisodiy ma'lumotlar API"""
    
    async def _authenticate(self, request: aiohttp.ClientRequest) -> aiohttp.ClientRequest:
        """Economic data authentication"""
        headers = {
            "X-API-Key": self.config.credentials.get("api_key")
        }
        request.headers.update(headers)
        return request
        
    async def make_request(self, endpoint: str, method: str = "GET", data: Any = None, headers: Dict[str, str] = None, **kwargs) -> APIResponse:
        """Economic data request"""
        await self.rate_limiter.acquire()
        start_time = time.time()
        
        try:
            if not headers:
                headers = {}
            headers.update(await self._authenticate(aiohttp.ClientRequest(method, endpoint)))
            
            async with self.session.request(method, endpoint, json=data, headers=headers) as response:
                response_data = await response.json()
                
                success = response.status < 400
                message = "Success" if success else f"HTTP {response.status}"
                
                api_response = APIResponse(
                    status_code=response.status,
                    data=response_data,
                    success=success,
                    message=message,
                    timestamp=datetime.now(),
                    execution_time=time.time() - start_time
                )
                
                self._log_request(method, endpoint, start_time, success, message)
                return api_response
                
        except Exception as e:
            self._log_request(method, endpoint, start_time, False, str(e))
            return APIResponse(
                status_code=500,
                data=None,
                success=False,
                message=str(e),
                timestamp=datetime.now(),
                execution_time=time.time() - start_time
            )
            
    async def get_central_bank_rates(self, country_code: str = "US") -> APIResponse:
        """Markaziy bank stavkalari"""
        endpoint = f"{self.config.base_url}/central-banks/{country_code}/rates"
        return await self.make_request(endpoint)
        
    async def get_economic_indicators(self, indicator: str, country: str = "US") -> APIResponse:
        """Iqtisodiy ko'rsatkichlar"""
        endpoint = f"{self.config.base_url}/indicators/{indicator}?country={country}"
        return await self.make_request(endpoint)
        
    async def get_gdp_data(self, country: str = "US", year: int = None) -> APIResponse:
        """YaIM ma'lumotlari"""
        year_param = f"&year={year}" if year else ""
        endpoint = f"{self.config.base_url}/gdp/{country}?{year_param}"
        return await self.make_request(endpoint)

# =============================================================================
# SOCIAL SENTIMENT INTEGRATIONS
# =============================================================================

class SocialSentimentClient(BaseAPIClient):
    """Social sentiment va mood tracking"""
    
    def __init__(self, config: APIConfig):
        super().__init__(config)
        self.platforms = {
            'twitter': None,
            'reddit': None
        }
        
    async def _authenticate(self, request: aiohttp.ClientRequest) -> aiohttp.ClientRequest:
        """Social API authentication"""
        headers = {
            "Authorization": f"Bearer {self.config.credentials.get('access_token')}"
        }
        request.headers.update(headers)
        return request
        
    async def initialize_platforms(self):
        """Social media platformlarni initialize qilish"""
        # Twitter
        try:
            twitter_auth = self.config.credentials.get('twitter', {})
            self.platforms['twitter'] = tweepy.API(
                tweepy.OAuth1UserHandler(
                    twitter_auth.get('consumer_key'),
                    twitter_auth.get('consumer_secret'),
                    twitter_auth.get('access_token'),
                    twitter_auth.get('access_token_secret')
                )
            )
        except Exception as e:
            logger.error(f"Twitter initialization error: {e}")
            
        # Reddit
        try:
            reddit_auth = self.config.credentials.get('reddit', {})
            self.platforms['reddit'] = praw.Reddit(
                client_id=reddit_auth.get('client_id'),
                client_secret=reddit_auth.get('client_secret'),
                user_agent=reddit_auth.get('user_agent')
            )
        except Exception as e:
            logger.error(f"Reddit initialization error: {e}")
            
    async def get_twitter_sentiment(self, symbol: str, limit: int = 100) -> APIResponse:
        """Twitter sentiment analysis"""
        endpoint = f"{self.config.base_url}/sentiment/twitter/{symbol}?limit={limit}"
        return await self.make_request(endpoint)
        
    async def get_reddit_sentiment(self, symbol: str, subreddit: str = "investing") -> APIResponse:
        """Reddit sentiment analysis"""
        endpoint = f"{self.config.base_url}/sentiment/reddit/{symbol}?subreddit={subreddit}"
        return await self.make_request(endpoint)
        
    async def analyze_market_mood(self, symbol: str) -> APIResponse:
        """Umumiy bozor kayfiyati"""
        endpoint = f"{self.config.base_url}/market-mood/{symbol}"
        return await self.make_request(endpoint)

# =============================================================================
# PAYMENT PROCESSING
# =============================================================================

class StripePaymentClient(BaseAPIClient):
    """Stripe payment integration"""
    
    def __init__(self, config: APIConfig):
        super().__init__(config)
        stripe.api_key = config.credentials.get("secret_key")
        
    async def _authenticate(self, request: aiohttp.ClientRequest) -> aiohttp.ClientRequest:
        """Stripe authentication"""
        headers = {
            "Authorization": f"Bearer {self.config.credentials.get('secret_key')}",
            "Stripe-Version": "2023-10-16"
        }
        request.headers.update(headers)
        return request
        
    async def make_request(self, endpoint: str, method: str = "GET", data: Any = None, headers: Dict[str, str] = None, **kwargs) -> APIResponse:
        """Stripe API request"""
        start_time = time.time()
        
        try:
            if method == "POST" and "payment-intent" in endpoint:
                # Stripe Payment Intent yaratish
                payment_intent = stripe.PaymentIntent.create(
                    amount=int(data.get("amount", 0)),
                    currency=data.get("currency", "usd"),
                    metadata=data.get("metadata", {})
                )
                
                response_data = payment_intent.to_dict()
                success = True
                message = "Payment Intent created"
                
            else:
                # Standart API request
                if not headers:
                    headers = {}
                headers.update(await self._authenticate(aiohttp.ClientRequest(method, endpoint)))
                
                async with self.session.request(method, endpoint, json=data, headers=headers) as response:
                    response_data = await response.json()
                    success = response.status < 400
                    message = "Success" if success else f"HTTP {response.status}"
            
            api_response = APIResponse(
                status_code=200,
                data=response_data,
                success=success,
                message=message,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time
            )
            
            self._log_request(method, endpoint, start_time, success, message)
            return api_response
            
        except Exception as e:
            self._log_request(method, endpoint, start_time, False, str(e))
            return APIResponse(
                status_code=500,
                data=None,
                success=False,
                message=str(e),
                timestamp=datetime.now(),
                execution_time=time.time() - start_time
            )
            
    async def create_subscription(self, customer_id: str, price_id: str, trial_days: int = 0) -> APIResponse:
        """Obuna yaratish"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                trial_period_days=trial_days
            )
            
            return APIResponse(
                status_code=200,
                data=subscription.to_dict(),
                success=True,
                message="Subscription created",
                timestamp=datetime.now(),
                execution_time=0
            )
        except Exception as e:
            return APIResponse(
                status_code=500,
                data=None,
                success=False,
                message=str(e),
                timestamp=datetime.now(),
                execution_time=0
            )
            
    async def create_payment_intent(self, amount: float, currency: str = "usd", metadata: Dict = None) -> APIResponse:
        """Payment Intent yaratish"""
        data = {
            "amount": amount,
            "currency": currency,
            "metadata": metadata or {}
        }
        
        endpoint = f"{self.config.base_url}/payment-intent"
        return await self.make_request(endpoint, "POST", data)

class PayPalClient(BaseAPIClient):
    """PayPal payment integration"""
    
    def __init__(self, config: APIConfig):
        super().__init__(config)
        paypalrestsdk.configure({
            "mode": config.credentials.get("mode", "sandbox"),
            "client_id": config.credentials.get("client_id"),
            "client_secret": config.credentials.get("client_secret")
        })
        
    async def _authenticate(self, request: aiohttp.ClientRequest) -> aiohttp.ClientRequest:
        """PayPal authentication"""
        headers = {
            "PayPal-Client-Id": self.config.credentials.get("client_id"),
            "PayPal-Request-Id": str(time.time())
        }
        request.headers.update(headers)
        return request
        
    async def make_request(self, endpoint: str, method: str = "GET", data: Any = None, headers: Dict[str, str] = None, **kwargs) -> APIResponse:
        """PayPal API request"""
        start_time = time.time()
        
        try:
            if method == "POST" and "payment" in endpoint:
                # PayPal payment yaratish
                payment = paypalrestsdk.Payment({
                    "intent": "sale",
                    "payer": {
                        "payment_method": "paypal"
                    },
                    "redirect_urls": {
                        "return_url": data.get("return_url"),
                        "cancel_url": data.get("cancel_url")
                    },
                    "transactions": [{
                        "item_list": {
                            "items": data.get("items", [])
                        },
                        "amount": {
                            "total": str(data.get("amount", 0)),
                            "currency": data.get("currency", "USD")
                        },
                        "description": data.get("description", "Payment")
                    }]
                })
                
                if payment.create():
                    response_data = payment.to_dict()
                    success = True
                    message = "Payment created"
                else:
                    response_data = {"error": payment.error}
                    success = False
                    message = "Payment creation failed"
                    
            else:
                # Standart API request
                if not headers:
                    headers = {}
                headers.update(await self._authenticate(aiohttp.ClientRequest(method, endpoint)))
                
                async with self.session.request(method, endpoint, json=data, headers=headers) as response:
                    response_data = await response.json()
                    success = response.status < 400
                    message = "Success" if success else f"HTTP {response.status}"
            
            api_response = APIResponse(
                status_code=200 if success else 500,
                data=response_data,
                success=success,
                message=message,
                timestamp=datetime.now(),
                execution_time=time.time() - start_time
            )
            
            self._log_request(method, endpoint, start_time, success, message)
            return api_response
            
        except Exception as e:
            self._log_request(method, endpoint, start_time, False, str(e))
            return APIResponse(
                status_code=500,
                data=None,
                success=False,
                message=str(e),
                timestamp=datetime.now(),
                execution_time=time.time() - start_time
            )
            
    async def create_payment(self, amount: float, currency: str = "USD", description: str = "Payment") -> APIResponse:
        """PayPal payment yaratish"""
        data = {
            "amount": amount,
            "currency": currency,
            "description": description
        }
        
        endpoint = f"{self.config.base_url}/payment"
        return await self.make_request(endpoint, "POST", data)

# =============================================================================
# COMMUNICATION INTEGRATIONS
# =============================================================================

class SlackClient(BaseAPIClient):
    """Slack notifications"""
    
    async def _authenticate(self, request: aiohttp.ClientRequest) -> aiohttp.ClientRequest:
        """Slack authentication"""
        headers = {
            "Authorization": f"Bearer {self.config.credentials.get('bot_token')}",
            "Content-Type": "application/json"
        }
        request.headers.update(headers)
        return request
        
    async def make_request(self, endpoint: str, method: str = "GET", data: Any = None, headers: Dict[str, str] = None, **kwargs) -> APIResponse:
        """Slack API request"""
        await self.rate_limiter.acquire()
        start_time = time.time()
        
        try:
            if not headers:
                headers = {}
            headers.update(await self._authenticate(aiohttp.ClientRequest(method, endpoint)))
            
            async with self.session.request(method, endpoint, json=data, headers=headers) as response:
                response_data = await response.json()
                
                success = response.status < 400 and response_data.get("ok", False)
                message = response_data.get("message", "Success" if success else "Slack API Error")
                
                api_response = APIResponse(
                    status_code=response.status,
                    data=response_data,
                    success=success,
                    message=message,
                    timestamp=datetime.now(),
                    execution_time=time.time() - start_time
                )
                
                self._log_request(method, endpoint, start_time, success, message)
                return api_response
                
        except Exception as e:
            self._log_request(method, endpoint, start_time, False, str(e))
            return APIResponse(
                status_code=500,
                data=None,
                success=False,
                message=str(e),
                timestamp=datetime.now(),
                execution_time=time.time() - start_time
            )
            
    async def send_message(self, channel: str, text: str, blocks: List[Dict] = None) -> APIResponse:
        """Xabar yuborish"""
        endpoint = f"{self.config.base_url}/chat.postMessage"
        data = {
            "channel": channel,
            "text": text
        }
        
        if blocks:
            data["blocks"] = blocks
            
        return await self.make_request(endpoint, "POST", data)
        
    async def send_trading_alert(self, symbol: str, action: str, price: float, channel: str = "#trading") -> APIResponse:
        """Trading alert yuborish"""
        message = f"🚨 Trading Alert:\n📊 Symbol: {symbol}\n🔄 Action: {action}\n💰 Price: ${price:.2f}\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return await self.send_message(channel, message)

class DiscordClient(BaseAPIClient):
    """Discord notifications"""
    
    async def _authenticate(self, request: aiohttp.ClientRequest) -> aiohttp.ClientRequest:
        """Discord authentication"""
        headers = {
            "Authorization": f"Bot {self.config.credentials.get('bot_token')}",
            "Content-Type": "application/json"
        }
        request.headers.update(headers)
        return request
        
    async def make_request(self, endpoint: str, method: str = "GET", data: Any = None, headers: Dict[str, str] = None, **kwargs) -> APIResponse:
        """Discord API request"""
        await self.rate_limiter.acquire()
        start_time = time.time()
        
        try:
            if not headers:
                headers = {}
            headers.update(await self._authenticate(aiohttp.ClientRequest(method, endpoint)))
            
            async with self.session.request(method, endpoint, json=data, headers=headers) as response:
                if response.status == 204:
                    response_data = {"message": "Message sent successfully"}
                    success = True
                else:
                    response_data = await response.json()
                    success = response.status < 400
                    
                message = "Success" if success else f"HTTP {response.status}"
                
                api_response = APIResponse(
                    status_code=response.status,
                    data=response_data,
                    success=success,
                    message=message,
                    timestamp=datetime.now(),
                    execution_time=time.time() - start_time
                )
                
                self._log_request(method, endpoint, start_time, success, message)
                return api_response
                
        except Exception as e:
            self._log_request(method, endpoint, start_time, False, str(e))
            return APIResponse(
                status_code=500,
                data=None,
                success=False,
                message=str(e),
                timestamp=datetime.now(),
                execution_time=time.time() - start_time
            )
            
    async def send_message(self, channel_id: str, content: str, embeds: List[Dict] = None) -> APIResponse:
        """Discord xabar yuborish"""
        endpoint = f"{self.config.base_url}/channels/{channel_id}/messages"
        data = {"content": content}
        
        if embeds:
            data["embeds"] = embeds
            
        return await self.make_request(endpoint, "POST", data)
        
    async def send_trading_signal(self, signal: Dict) -> APIResponse:
        """Trading signal yuborish"""
        embed = {
            "title": f"Trading Signal: {signal.get('symbol')}",
            "description": signal.get('description', 'No description'),
            "color": 0x00ff00 if signal.get('action') == 'BUY' else 0xff0000,
            "fields": [
                {"name": "Action", "value": signal.get('action', 'N/A'), "inline": True},
                {"name": "Price", "value": f"${signal.get('price', 0):.2f}", "inline": True},
                {"name": "Confidence", "value": f"{signal.get('confidence', 0):.1%}", "inline": True}
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        content = f"🎯 New trading signal for {signal.get('symbol')}!"
        return await self.send_message(signal.get('channel_id', '123456789'), content, [embed])

# =============================================================================
# CLOUD STORAGE INTEGRATIONS
# =============================================================================

class AWSStorageClient(BaseAPIClient):
    """AWS S3 storage integration"""
    
    def __init__(self, config: APIConfig):
        super().__init__(config)
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=config.credentials.get('access_key_id'),
            aws_secret_access_key=config.credentials.get('secret_access_key'),
            region_name=config.credentials.get('region', 'us-east-1')
        )
        
    async def _authenticate(self, request: aiohttp.ClientRequest) -> aiohttp.ClientRequest:
        """S3 authentication"""
        # Boto3 avtomatik authentication qiladi
        return request
        
    async def make_request(self, endpoint: str, method: str = "GET", data: Any = None, headers: Dict[str, str] = None, **kwargs) -> APIResponse:
        """S3 API request"""
        start_time = time.time()
        
        try:
            if method == "PUT":
                # Fayl yuklash
                bucket_name = kwargs.get('bucket_name')
                key = kwargs.get('key')
                body = data
                
                self.s3_client.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=body
                )
                
                response_data = {"message": "File uploaded successfully"}
                success = True
                
            elif method == "GET":
                # Fayl olish
                bucket_name = kwargs.get('bucket_name')
                key = kwargs.get('key')
                
                response = self.s3_client.get_object(
                    Bucket=bucket_name,
                    Key=key
                )
                
                response_data = response['Body'].read()
                success = True
                
            else:
                response_data = {"error": "Unsupported method"}
                success = False
                
            api_response = APIResponse(
                status_code=200 if success else 400,
                data=response_data,
                success=success,
                message="Success" if success else "S3 operation failed",
                timestamp=datetime.now(),
                execution_time=time.time() - start_time
            )
            
            self._log_request(method, endpoint, start_time, success, "S3 operation")
            return api_response
            
        except ClientError as e:
            self._log_request(method, endpoint, start_time, False, str(e))
            return APIResponse(
                status_code=500,
                data=None,
                success=False,
                message=str(e),
                timestamp=datetime.now(),
                execution_time=time.time() - start_time
            )
            
    async def upload_file(self, bucket_name: str, key: str, file_path: str) -> APIResponse:
        """Fayl yuklash"""
        try:
            with open(file_path, 'rb') as file:
                return await self.make_request("PUT", data=file, bucket_name=bucket_name, key=key)
        except Exception as e:
            return APIResponse(
                status_code=500,
                data=None,
                success=False,
                message=str(e),
                timestamp=datetime.now(),
                execution_time=0
            )
            
    async def download_file(self, bucket_name: str, key: str, local_path: str) -> APIResponse:
        """Fayl yuklab olish"""
        try:
            response = await self.make_request("GET", bucket_name=bucket_name, key=key)
            
            if response.success:
                with open(local_path, 'wb') as file:
                    file.write(response.data)
                    
            return response
            
        except Exception as e:
            return APIResponse(
                status_code=500,
                data=None,
                success=False,
                message=str(e),
                timestamp=datetime.now(),
                execution_time=0
            )

class GoogleCloudStorageClient(BaseAPIClient):
    """Google Cloud Storage integration"""
    
    def __init__(self, config: APIConfig):
        super().__init__(config)
        # Google Cloud Storage client ni bu yerda initialize qilish kerak
        # Bu oddiy demo uchun placeholder
        
    async def _authenticate(self, request: aiohttp.ClientRequest) -> aiohttp.ClientRequest:
        """Google Cloud authentication"""
        headers = {
            "Authorization": f"Bearer {self.config.credentials.get('access_token')}"
        }
        request.headers.update(headers)
        return request
        
    async def make_request(self, endpoint: str, method: str = "GET", data: Any = None, headers: Dict[str, str] = None, **kwargs) -> APIResponse:
        """GCS API request"""
        await self.rate_limiter.acquire()
        start_time = time.time()
        
        try:
            if not headers:
                headers = {}
            headers.update(await self._authenticate(aiohttp.ClientRequest(method, endpoint)))
            
            async with self.session.request(method, endpoint, json=data, headers=headers) as response:
                response_data = await response.json()
                
                success = response.status < 400
                message = "Success" if success else f"HTTP {response.status}"
                
                api_response = APIResponse(
                    status_code=response.status,
                    data=response_data,
                    success=success,
                    message=message,
                    timestamp=datetime.now(),
                    execution_time=time.time() - start_time
                )
                
                self._log_request(method, endpoint, start_time, success, message)
                return api_response
                
        except Exception as e:
            self._log_request(method, endpoint, start_time, False, str(e))
            return APIResponse(
                status_code=500,
                data=None,
                success=False,
                message=str(e),
                timestamp=datetime.now(),
                execution_time=time.time() - start_time
            )
            
    async def upload_file(self, bucket_name: str, object_name: str, file_data: bytes, content_type: str = "application/octet-stream") -> APIResponse:
        """GCS fayl yuklash"""
        endpoint = f"https://storage.googleapis.com/upload/storage/v1/b/{bucket_name}/o"
        headers = {"Content-Type": content_type}
        
        params = {
            "uploadType": "media",
            "name": object_name
        }
        
        return await self.make_request(endpoint, "POST", file_data, headers, **params)

# =============================================================================
# DATA TRANSFORMATION UTILITIES
# =============================================================================

class DataTransformer:
    """Ma'lumotlarni transformatsiya qilish uchun utility class"""
    
    @staticmethod
    def normalize_symbol(symbol: str) -> str:
        """Symbol nomini normalizatsiya qilish"""
        return symbol.upper().replace("-", "_").replace("/", "_")
    
    @staticmethod
    def format_price(price: float, currency: str = "USD") -> str:
        """Narxni formatlash"""
        if currency == "USD":
            return f"${price:.2f}"
        elif currency == "EUR":
            return f"€{price:.2f}"
        elif currency == "GBP":
            return f"£{price:.2f}"
        else:
            return f"{price:.2f} {currency}"
    
    @staticmethod
    def calculate_percentage_change(old_value: float, new_value: float) -> float:
        """Foiz o'zgarish hisoblash"""
        if old_value == 0:
            return 0.0
        return ((new_value - old_value) / old_value) * 100
    
    @staticmethod
    def normalize_news_sentiment(sentiment_score: float) -> Dict[str, Any]:
        """Yangilik kayfiyati normalizatsiya"""
        if sentiment_score > 0.6:
            return {"sentiment": "positive", "score": sentiment_score, "level": "high"}
        elif sentiment_score > 0.3:
            return {"sentiment": "positive", "score": sentiment_score, "level": "medium"}
        elif sentiment_score < -0.6:
            return {"sentiment": "negative", "score": sentiment_score, "level": "high"}
        elif sentiment_score < -0.3:
            return {"sentiment": "negative", "score": sentiment_score, "level": "medium"}
        else:
            return {"sentiment": "neutral", "score": sentiment_score, "level": "low"}
    
    @staticmethod
    def convert_timeframe(data: pd.DataFrame, from_tf: str, to_tf: str) -> pd.DataFrame:
        """Vaqt oralig'ini o'zgartirish"""
        if from_tf == to_tf:
            return data
            
        # Vaqt oralig'i mapping
        tf_mapping = {
            '1m': '1T',
            '5m': '5T', 
            '15m': '15T',
            '1h': '1H',
            '1d': '1D',
            '1w': '1W'
        }
        
        from_tf_grain = tf_mapping.get(from_tf, '1T')
        to_tf_grain = tf_mapping.get(to_tf, '1D')
        
        data.index = pd.to_datetime(data.index)
        
        if to_tf_grain > from_tf_grain:
            # Upsampling
            return data.resample(to_tf_grain).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min', 
                'close': 'last',
                'volume': 'sum'
            }).dropna()
        else:
            # Downsampling
            return data.resample(to_tf_grain).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last', 
                'volume': 'sum'
            }).dropna()
    
    @staticmethod
    def calculate_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
        """Texnik indikatorlar hisoblash"""
        result = data.copy()
        
        # Moving Averages
        result['sma_20'] = data['close'].rolling(window=20).mean()
        result['sma_50'] = data['close'].rolling(window=50).mean()
        result['ema_12'] = data['close'].ewm(span=12).mean()
        result['ema_26'] = data['close'].ewm(span=26).mean()
        
        # MACD
        result['macd'] = result['ema_12'] - result['ema_26']
        result['macd_signal'] = result['macd'].ewm(span=9).mean()
        result['macd_histogram'] = result['macd'] - result['macd_signal']
        
        # RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        result['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        result['bb_middle'] = data['close'].rolling(window=20).mean()
        bb_std = data['close'].rolling(window=20).std()
        result['bb_upper'] = result['bb_middle'] + (bb_std * 2)
        result['bb_lower'] = result['bb_middle'] - (bb_std * 2)
        
        return result

# =============================================================================
# API MONITORING VA HEALTH CHECKS
# =============================================================================

class APIMonitor:
    """API health monitoring uchun"""
    
    def __init__(self):
        self.apis = {}
        self.health_history = defaultdict(list)
        self.alerts_enabled = True
        
    def register_api(self, name: str, client: BaseAPIClient, config: APIConfig):
        """API ni monitoring uchun ro'yxatga olish"""
        self.apis[name] = {
            'client': client,
            'config': config,
            'last_check': None,
            'consecutive_failures': 0
        }
        
    async def check_api_health(self, api_name: str) -> HealthCheckResult:
        """Bitta API health check"""
        if api_name not in self.apis:
            raise ValueError(f"API '{api_name}' not registered")
            
        api_info = self.apis[api_name]
        client = api_info['client']
        
        start_time = time.time()
        
        try:
            # Test request qilish
            test_response = await client.make_request(
                client.config.base_url + "/health",
                method="GET"
            )
            
            response_time = time.time() - start_time
            
            if test_response.success:
                status = APIStatus.ACTIVE
                message = "API is healthy"
                api_info['consecutive_failures'] = 0
            else:
                status = APIStatus.ERROR
                message = f"API returned status {test_response.status_code}"
                api_info['consecutive_failures'] += 1
                
        except Exception as e:
            response_time = time.time() - start_time
            status = APIStatus.ERROR
            message = f"Connection error: {str(e)}"
            api_info['consecutive_failures'] += 1
            
        # Rate limiting tekshirish
        if api_info['consecutive_failures'] > 3:
            status = APIStatus.RATE_LIMITED
            message = "API is rate limited"
            
        result = HealthCheckResult(
            api_name=api_name,
            status=status,
            response_time=response_time,
            last_success=datetime.now(),
            error_count=api_info['consecutive_failures'],
            message=message
        )
        
        # History ga saqlash
        self.health_history[api_name].append(result)
        
        # Oxirgi check ni update qilish
        api_info['last_check'] = result
        
        # Alert yuborish (agar kerak bo'lsa)
        if self.alerts_enabled and status in [APIStatus.ERROR, APIStatus.RATE_LIMITED]:
            await self._send_alert(result)
            
        return result
        
    async def check_all_apis(self) -> Dict[str, HealthCheckResult]:
        """Barcha API larni health check"""
        results = {}
        
        for api_name in self.apis.keys():
            try:
                result = await self.check_api_health(api_name)
                results[api_name] = result
            except Exception as e:
                logger.error(f"Health check failed for {api_name}: {e}")
                results[api_name] = HealthCheckResult(
                    api_name=api_name,
                    status=APIStatus.ERROR,
                    response_time=0,
                    last_success=datetime.now(),
                    error_count=0,
                    message=f"Health check error: {str(e)}"
                )
                
        return results
        
    async def _send_alert(self, result: HealthCheckResult):
        """Alert yuborish"""
        # Bu yerda Slack, Discord yoki email orqali alert yuborish
        # Hozircha log qilish
        logger.warning(f"API Alert: {result.api_name} - {result.message}")
        
    def get_health_summary(self) -> Dict[str, Any]:
        """Health summary olish"""
        total_apis = len(self.apis)
        active_apis = 0
        error_apis = 0
        rate_limited_apis = 0
        
        for api_name, api_info in self.apis.items():
            if api_info['last_check']:
                status = api_info['last_check'].status
                if status == APIStatus.ACTIVE:
                    active_apis += 1
                elif status == APIStatus.ERROR:
                    error_apis += 1
                elif status == APIStatus.RATE_LIMITED:
                    rate_limited_apis += 1
                    
        return {
            'total_apis': total_apis,
            'active_apis': active_apis,
            'error_apis': error_apis,
            'rate_limited_apis': rate_limited_apis,
            'health_percentage': (active_apis / total_apis * 100) if total_apis > 0 else 0
        }
        
    def get_api_performance_stats(self, api_name: str, hours: int = 24) -> Dict[str, Any]:
        """API performance statistikasi"""
        if api_name not in self.health_history:
            return {}
            
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_checks = [
            check for check in self.health_history[api_name]
            if check.last_success >= cutoff_time
        ]
        
        if not recent_checks:
            return {}
            
        successful_checks = [check for check in recent_checks if check.status == APIStatus.ACTIVE]
        avg_response_time = np.mean([check.response_time for check in successful_checks])
        
        return {
            'total_checks': len(recent_checks),
            'successful_checks': len(successful_checks),
            'success_rate': len(successful_checks) / len(recent_checks),
            'avg_response_time': avg_response_time,
            'last_check': recent_checks[-1] if recent_checks else None
        }

# =============================================================================
# MAIN API INTEGRATIONS HUB CLASS
# =============================================================================

class APIIntegrationsHub:
    """
    Barcha API integratsiyalarini boshqaruvchi asosiy sinf
    
    Bu sinf barcha trading, ma'lumot va xizmat API larini
    birlashtiradi va universal interface ta'minlaydi.
    """
    
    def __init__(self, config_file: str = "api_config.json"):
        self.config_file = config_file
        self.clients = {}
        self.api_configs = {}
        self.monitor = APIMonitor()
        self.auth_manager = AuthManager()
        self.transformer = DataTransformer()
        self.background_tasks = []
        
        # Configuration faylni yuklash
        self._load_configs()
        
        # API larni initialize qilish
        self._initialize_apis()
        
    def _load_configs(self):
        """Configuration faylni yuklash"""
        try:
            with open(self.config_file, 'r') as f:
                configs = json.load(f)
                
            for api_name, config_data in configs.items():
                self.api_configs[api_name] = APIConfig(**config_data)
                
            logger.info(f"Loaded {len(self.api_configs)} API configurations")
            
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_file} not found, using defaults")
            self._create_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._create_default_config()
            
    def _create_default_config(self):
        """Default konfiguratsiya yaratish"""
        default_configs = {
            "alpaca": APIConfig(
                name="Alpaca Trading",
                category=APICategory.TRADING,
                base_url="https://paper-api.alpaca.markets",
                auth_type="custom",
                credentials={
                    "api_key": "your_api_key",
                    "secret_key": "your_secret_key"
                },
                rate_limit=200
            ),
            "news_feed": APIConfig(
                name="Market News Feed",
                category=APICategory.NEWS,
                base_url="https://newsapi.org/v2",
                auth_type="api_key",
                credentials={
                    "api_key": "your_news_api_key"
                },
                rate_limit=1000
            ),
            "stripe": APIConfig(
                name="Stripe Payments",
                category=APICategory.PAYMENT,
                base_url="https://api.stripe.com",
                auth_type="bearer",
                credentials={
                    "secret_key": "sk_test_..."
                },
                rate_limit=100
            )
        }
        
        self.api_configs.update(default_configs)
        
        # Configuration faylni saqlash
        with open(self.config_file, 'w') as f:
            config_dict = {}
            for name, config in default_configs.items():
                config_dict[name] = {
                    'name': config.name,
                    'category': config.category.value,
                    'base_url': config.base_url,
                    'auth_type': config.auth_type,
                    'credentials': config.credentials,
                    'rate_limit': config.rate_limit,
                    'enabled': config.enabled
                }
            json.dump(config_dict, f, indent=2)
            
    def _initialize_apis(self):
        """API clientlarni initialize qilish"""
        for api_name, config in self.api_configs.items():
            if not config.enabled:
                continue
                
            try:
                if config.category == APICategory.TRADING:
                    if "alpaca" in api_name.lower():
                        client = AlpacaClient(config)
                    elif "interactive" in api_name.lower():
                        client = InteractiveBrokersClient(config)
                    elif "metatrader" in api_name.lower():
                        client = MetaTraderClient(config)
                    else:
                        client = BaseAPIClient(config)
                        
                elif config.category == APICategory.NEWS:
                    client = NewsFeedClient(config)
                    
                elif config.category == APICategory.ECONOMIC:
                    client = EconomicDataClient(config)
                    
                elif config.category == APICategory.SOCIAL:
                    client = SocialSentimentClient(config)
                    
                elif config.category == APICategory.PAYMENT:
                    if "stripe" in api_name.lower():
                        client = StripePaymentClient(config)
                    elif "paypal" in api_name.lower():
                        client = PayPalClient(config)
                    else:
                        client = BaseAPIClient(config)
                        
                elif config.category == APICategory.COMMUNICATION:
                    if "slack" in api_name.lower():
                        client = SlackClient(config)
                    elif "discord" in api_name.lower():
                        client = DiscordClient(config)
                    else:
                        client = BaseAPIClient(config)
                        
                elif config.category == APICategory.STORAGE:
                    if "aws" in api_name.lower() or "s3" in api_name.lower():
                        client = AWSStorageClient(config)
                    elif "google" in api_name.lower():
                        client = GoogleCloudStorageClient(config)
                    else:
                        client = BaseAPIClient(config)
                        
                else:
                    client = BaseAPIClient(config)
                    
                self.clients[api_name] = client
                
                # Monitor ga ro'yxatga olish
                self.monitor.register_api(api_name, client, config)
                
                logger.info(f"Initialized API client: {api_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize {api_name}: {e}")
                
    async def start_monitoring(self, interval_minutes: int = 5):
        """Background monitoring ishga tushirish"""
        async def monitor_loop():
            while True:
                try:
                    await self.monitor.check_all_apis()
                    await asyncio.sleep(interval_minutes * 60)
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    await asyncio.sleep(60)
                    
        task = asyncio.create_task(monitor_loop())
        self.background_tasks.append(task)
        logger.info(f"Started API monitoring with {interval_minutes} minute intervals")
        
    async def stop_monitoring(self):
        """Monitoring to'xtatish"""
        for task in self.background_tasks:
            task.cancel()
        self.background_tasks.clear()
        logger.info("Stopped API monitoring")
        
    # =============================================================================
    # TRADING APIs
    # =============================================================================
    
    async def place_trading_order(
        self, 
        symbol: str, 
        side: str, 
        qty: float, 
        order_type: str = "market",
        api_provider: str = "alpaca"
    ) -> APIResponse:
        """Trading buyurtma qo'yish"""
        if api_provider not in self.clients:
            raise ValueError(f"Trading API {api_provider} not available")
            
        client = self.clients[api_provider]
        
        if hasattr(client, 'place_order'):
            return await client.place_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type
            )
        else:
            return APIResponse(
                status_code=501,
                data=None,
                success=False,
                message="Trading not supported for this API",
                timestamp=datetime.now(),
                execution_time=0
            )
            
    async def get_account_info(self, api_provider: str = "alpaca") -> APIResponse:
        """Hisob ma'lumotlari olish"""
        if api_provider not in self.clients:
            raise ValueError(f"Trading API {api_provider} not available")
            
        client = self.clients[api_provider]
        
        if hasattr(client, 'get_account'):
            return await client.get_account()
        else:
            return APIResponse(
                status_code=501,
                data=None,
                success=False,
                message="Account info not supported for this API",
                timestamp=datetime.now(),
                execution_time=0
            )
            
    async def get_positions(self, api_provider: str = "alpaca") -> APIResponse:
        """Pozitsiyalar olish"""
        if api_provider not in self.clients:
            raise ValueError(f"Trading API {api_provider} not available")
            
        client = self.clients[api_provider]
        
        if hasattr(client, 'get_positions'):
            return await client.get_positions()
        else:
            return APIResponse(
                status_code=501,
                data=None,
                success=False,
                message="Positions not supported for this API",
                timestamp=datetime.now(),
                execution_time=0
            )
            
    # =============================================================================
    # DATA APIs
    # =============================================================================
    
    async def get_market_data(self, symbols: List[str], data_type: str = "quotes") -> Dict[str, APIResponse]:
        """Bozor ma'lumotlari olish"""
        results = {}
        
        for api_name, client in self.clients.items():
            if client.config.category == APICategory.DATA_FEED:
                try:
                    if hasattr(client, 'get_live_quotes'):
                        result = await client.get_live_quotes(symbols)
                        results[api_name] = result
                except Exception as e:
                    logger.error(f"Error getting market data from {api_name}: {e}")
                    results[api_name] = APIResponse(
                        status_code=500,
                        data=None,
                        success=False,
                        message=str(e),
                        timestamp=datetime.now(),
                        execution_time=0
                    )
                    
        return results
        
    async def get_news(self, symbol: str = None, category: str = "business", limit: int = 50) -> Dict[str, APIResponse]:
        """Yangiliklar olish"""
        results = {}
        
        for api_name, client in self.clients.items():
            if client.config.category == APICategory.NEWS:
                try:
                    if symbol and hasattr(client, 'get_stock_news'):
                        result = await client.get_stock_news(symbol)
                    elif hasattr(client, 'get_market_news'):
                        result = await client.get_market_news(category, limit)
                    else:
                        continue
                        
                    results[api_name] = result
                    
                except Exception as e:
                    logger.error(f"Error getting news from {api_name}: {e}")
                    results[api_name] = APIResponse(
                        status_code=500,
                        data=None,
                        success=False,
                        message=str(e),
                        timestamp=datetime.now(),
                        execution_time=0
                    )
                    
        return results
        
    # =============================================================================
    # PAYMENT APIs
    # =============================================================================
    
    async def process_payment(
        self, 
        amount: float, 
        currency: str = "usd", 
        payment_method: str = "stripe",
        metadata: Dict = None
    ) -> APIResponse:
        """To'lovni qayta ishlash"""
        if payment_method not in self.clients:
            raise ValueError(f"Payment method {payment_method} not available")
            
        client = self.clients[payment_method]
        
        if hasattr(client, 'create_payment_intent'):
            return await client.create_payment_intent(amount, currency, metadata)
        elif hasattr(client, 'create_payment'):
            return await client.create_payment(amount, currency)
        else:
            return APIResponse(
                status_code=501,
                data=None,
                success=False,
                message="Payment processing not supported for this provider",
                timestamp=datetime.now(),
                execution_time=0
            )
            
    async def create_subscription(
        self, 
        customer_id: str, 
        price_id: str, 
        trial_days: int = 0,
        provider: str = "stripe"
    ) -> APIResponse:
        """Obuna yaratish"""
        if provider not in self.clients:
            raise ValueError(f"Subscription provider {provider} not available")
            
        client = self.clients[provider]
        
        if hasattr(client, 'create_subscription'):
            return await client.create_subscription(customer_id, price_id, trial_days)
        else:
            return APIResponse(
                status_code=501,
                data=None,
                success=False,
                message="Subscription not supported for this provider",
                timestamp=datetime.now(),
                execution_time=0
            )
            
    # =============================================================================
    # COMMUNICATION APIs
    # =============================================================================
    
    async def send_notification(
        self, 
        message: str, 
        channel: str = None,
        provider: str = "slack",
        notification_type: str = "general"
    ) -> Dict[str, APIResponse]:
        """Xabar yuborish"""
        results = {}
        
        for api_name, client in self.clients.items():
            if client.config.category == APICategory.COMMUNICATION:
                try:
                    if "slack" in api_name.lower() and hasattr(client, 'send_message'):
                        result = await client.send_message(channel or "#general", message)
                        results[api_name] = result
                    elif "discord" in api_name.lower() and hasattr(client, 'send_message'):
                        result = await client.send_message(channel or "123456789", message)
                        results[api_name] = result
                        
                except Exception as e:
                    logger.error(f"Error sending notification via {api_name}: {e}")
                    results[api_name] = APIResponse(
                        status_code=500,
                        data=None,
                        success=False,
                        message=str(e),
                        timestamp=datetime.now(),
                        execution_time=0
                    )
                    
        return results
        
    async def send_trading_alert(self, symbol: str, action: str, price: float, channel: str = None) -> Dict[str, APIResponse]:
        """Trading alert yuborish"""
        results = {}
        
        for api_name, client in self.clients.items():
            if client.config.category == APICategory.COMMUNICATION:
                try:
                    if "slack" in api_name.lower() and hasattr(client, 'send_trading_alert'):
                        result = await client.send_trading_alert(symbol, action, price, channel or "#trading")
                        results[api_name] = result
                    elif "discord" in api_name.lower() and hasattr(client, 'send_trading_signal'):
                        signal = {
                            'symbol': symbol,
                            'action': action,
                            'price': price,
                            'description': f"Trading {action} signal",
                            'confidence': 0.8
                        }
                        result = await client.send_trading_signal(signal)
                        results[api_name] = result
                        
                except Exception as e:
                    logger.error(f"Error sending trading alert via {api_name}: {e}")
                    results[api_name] = APIResponse(
                        status_code=500,
                        data=None,
                        success=False,
                        message=str(e),
                        timestamp=datetime.now(),
                        execution_time=0
                    )
                    
        return results
        
    # =============================================================================
    # CLOUD STORAGE APIs
    # =============================================================================
    
    async def upload_data(
        self, 
        data: Any, 
        filename: str, 
        bucket_name: str,
        storage_provider: str = "aws",
        content_type: str = "application/json"
    ) -> APIResponse:
        """Ma'lumotlarni bulutli xotiraga yuklash"""
        if storage_provider not in self.clients:
            raise ValueError(f"Storage provider {storage_provider} not available")
            
        client = self.clients[storage_provider]
        
        # Ma'lumotlarni JSON formatga o'tkazish
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, ensure_ascii=False, indent=2)
            data_bytes = data_str.encode('utf-8')
        else:
            data_bytes = str(data).encode('utf-8')
            
        if hasattr(client, 'upload_file'):
            if "aws" in storage_provider.lower():
                return await client.upload_file(bucket_name, filename, "/tmp/temp_file")
            else:
                return await client.upload_file(bucket_name, filename, data_bytes, content_type)
        else:
            return APIResponse(
                status_code=501,
                data=None,
                success=False,
                message="File upload not supported for this provider",
                timestamp=datetime.now(),
                execution_time=0
            )
            
    async def download_data(
        self, 
        filename: str, 
        bucket_name: str,
        storage_provider: str = "aws",
        local_path: str = None
    ) -> APIResponse:
        """Ma'lumotlarni bulutli xotiradan yuklab olish"""
        if storage_provider not in self.clients:
            raise ValueError(f"Storage provider {storage_provider} not available")
            
        client = self.clients[storage_provider]
        
        if hasattr(client, 'download_file'):
            if not local_path:
                local_path = f"/tmp/{filename}"
                
            if "aws" in storage_provider.lower():
                return await client.download_file(bucket_name, filename, local_path)
            else:
                # Google Cloud uchun placeholder
                return APIResponse(
                    status_code=501,
                    data=None,
                    success=False,
                    message="Google Cloud download not implemented",
                    timestamp=datetime.now(),
                    execution_time=0
                )
        else:
            return APIResponse(
                status_code=501,
                data=None,
                success=False,
                message="File download not supported for this provider",
                timestamp=datetime.now(),
                execution_time=0
            )
            
    # =============================================================================
    # MONITORING VA UTILITY METHODS
    # =============================================================================
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Barcha API larning holati"""
        return self.monitor.get_health_summary()
        
    async def get_api_performance(self, api_name: str, hours: int = 24) -> Dict[str, Any]:
        """API performance statistikasi"""
        return self.monitor.get_api_performance_stats(api_name, hours)
        
    def get_available_apis(self) -> Dict[str, Dict[str, Any]]:
        """Mavjud API lar ro'yxati"""
        available = {}
        
        for api_name, config in self.api_configs.items():
            available[api_name] = {
                'name': config.name,
                'category': config.category.value,
                'base_url': config.base_url,
                'enabled': config.enabled,
                'available': api_name in self.clients
            }
            
        return available
        
    def add_api_config(self, name: str, config: APIConfig):
        """Yangi API konfiguratsiya qo'shish"""
        self.api_configs[name] = config
        
        # Client yaratish
        try:
            if config.category == APICategory.TRADING:
                client = AlpacaClient(config)
            elif config.category == APICategory.NEWS:
                client = NewsFeedClient(config)
            elif config.category == APICategory.PAYMENT:
                if "stripe" in name.lower():
                    client = StripePaymentClient(config)
                else:
                    client = BaseAPIClient(config)
            else:
                client = BaseAPIClient(config)
                
            self.clients[name] = client
            self.monitor.register_api(name, client, config)
            
            logger.info(f"Added new API configuration: {name}")
            
        except Exception as e:
            logger.error(f"Failed to add API {name}: {e}")
            
    def remove_api_config(self, name: str):
        """API konfiguratsiyasini o'chirish"""
        if name in self.api_configs:
            del self.api_configs[name]
            
        if name in self.clients:
            del self.clients[name]
            
        logger.info(f"Removed API configuration: {name}")
        
    def update_api_config(self, name: str, config: APIConfig):
        """API konfiguratsiyasini yangilash"""
        self.remove_api_config(name)
        self.add_api_config(name, config)
        
        logger.info(f"Updated API configuration: {name}")
        
    async def cleanup(self):
        """Resource cleanup"""
        # Background tasklarni to'xtatish
        await self.stop_monitoring()
        
        # Client sessionlarni yopish
        for client in self.clients.values():
            await client.cleanup()
            
        logger.info("API Integrations Hub cleaned up")

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

async def main():
    """Foydalanish namunasi"""
    # Hub yaratish
    hub = APIIntegrationsHub()
    
    try:
        # Monitoring ishga tushirish
        await hub.start_monitoring(interval_minutes=5)
        
        # Health check
        health = await hub.get_health_status()
        print(f"API Health Status: {json.dumps(health, indent=2, default=str)}")
        
        # Trading example
        if "alpaca" in hub.clients:
            print("Testing Alpaca trading...")
            
            # Account info
            account = await hub.get_account_info("alpaca")
            print(f"Account: {json.dumps(account.data, indent=2) if account.success else account.message}")
            
            # Place order (paper trading)
            order = await hub.place_trading_order(
                symbol="AAPL",
                side="buy",
                qty=1,
                order_type="market"
            )
            print(f"Order: {json.dumps(order.data, indent=2) if order.success else order.message}")
        
        # News example
        print("Getting market news...")
        news = await hub.get_news(category="business", limit=10)
        for api_name, news_response in news.items():
            if news_response.success:
                print(f"News from {api_name}: {len(news_response.data.get('articles', []))} articles")
            else:
                print(f"News failed from {api_name}: {news_response.message}")
        
        # Notification example
        print("Sending test notification...")
        notifications = await hub.send_notification(
            "🚀 API Integrations Hub is working!",
            provider="slack",
            notification_type="test"
        )
        
        # Payment example (stripe)
        if "stripe" in hub.clients:
            print("Testing Stripe payment...")
            payment = await hub.process_payment(
                amount=99.99,
                currency="usd",
                metadata={"plan": "premium", "user": "test_user"}
            )
            print(f"Payment: {json.dumps(payment.data, indent=2) if payment.success else payment.message}")
        
        # Data storage example
        print("Testing data storage...")
        test_data = {
            "timestamp": datetime.now().isoformat(),
            "trades": [
                {"symbol": "AAPL", "action": "BUY", "price": 150.00, "quantity": 10}
            ],
            "status": "success"
        }
        
        storage_result = await hub.upload_data(
            data=test_data,
            filename="test_trades.json",
            bucket_name="orion-trading-data",
            storage_provider="aws"
        )
        print(f"Storage: {storage_result.message}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        
    finally:
        # Cleanup
        await hub.cleanup()

if __name__ == "__main__":
    # Event loop ishga tushirish
    asyncio.run(main())