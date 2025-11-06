"""
Real-time Bozor Ma'lumotlari Moduli
Real-time Market Data Module

Bozor ma'lumotlarini real-time olish, qayta ishlash va analiz qilish uchun modul
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import numpy as np
import websockets
from abc import ABC, abstractmethod

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MarketDataPoint:
    """Bozor ma'lumot nuqtasi"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    spread: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    source: str = ""


@dataclass
class TechnicalIndicator:
    """Texnik indikator"""
    name: str
    value: float
    timestamp: datetime
    signal: str  # 'BUY', 'SELL', 'NEUTRAL'
    strength: float  # 0-1


@dataclass
class MarketMetrics:
    """Bozor metrikalari"""
    symbol: str
    volatility: float
    avg_volume: float
    price_momentum: float
    volume_momentum: float
    support_level: float
    resistance_level: float
    trend_direction: str


class DataStreamer(ABC):
    """Ma'lumot stream base class"""
    
    @abstractmethod
    async def connect(self) -> bool:
        pass
    
    @abstractmethod
    async def disconnect(self):
        pass
    
    @abstractmethod
    async def subscribe(self, symbols: List[str]):
        pass
    
    @abstractmethod
    async def get_data(self) -> Optional[MarketDataPoint]:
        pass


class WebSocketStreamer(DataStreamer):
    """WebSocket ma'lumot streamer"""
    
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.websocket = None
        self.subscribed_symbols = set()
        self.running = False
    
    async def connect(self) -> bool:
        try:
            self.websocket = await websockets.connect(self.ws_url)
            self.running = True
            logger.info(f"Connected to WebSocket: {self.ws_url}")
            return True
        except Exception as e:
            logger.error(f"WebSocket connection failed: {str(e)}")
            return False
    
    async def disconnect(self):
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        self.running = False
        logger.info("WebSocket disconnected")
    
    async def subscribe(self, symbols: List[str]):
        if not self.websocket:
            return
        
        self.subscribed_symbols.update(symbols)
        subscribe_message = {
            "action": "subscribe",
            "symbols": list(symbols)
        }
        await self.websocket.send(json.dumps(subscribe_message))
        logger.info(f"Subscribed to symbols: {symbols}")
    
    async def get_data(self) -> Optional[MarketDataPoint]:
        if not self.websocket or not self.running:
            return None
        
        try:
            message = await self.websocket.recv()
            data = json.loads(message)
            
            # Parse WebSocket data
            return MarketDataPoint(
                symbol=data.get('symbol', ''),
                timestamp=datetime.fromisoformat(data.get('timestamp', '')),
                open=float(data.get('open', 0)),
                high=float(data.get('high', 0)),
                low=float(data.get('low', 0)),
                close=float(data.get('close', 0)),
                volume=float(data.get('volume', 0)),
                source='websocket'
            )
        except Exception as e:
            logger.error(f"Error getting WebSocket data: {str(e)}")
            return None


class MarketDataProcessor:
    """Bozor ma'lumotlarini qayta ishlash moduli"""
    
    def __init__(self):
        self.data_history = {}
        self.current_prices = {}
        self.technical_indicators = {}
        self.market_metrics = {}
        self.streamers = {}
        
        # Performance tracking
        self.latency_tracker = {}
        self.update_frequency = {}
    
    def add_data_point(self, data_point: MarketDataPoint):
        """Ma'lumot nuqtasini qo'shish"""
        symbol = data_point.symbol
        
        # Update current price
        self.current_prices[symbol] = data_point
        
        # Store in history
        if symbol not in self.data_history:
            self.data_history[symbol] = []
        
        # Keep only last 1000 points to manage memory
        self.data_history[symbol].append(data_point)
        if len(self.data_history[symbol]) > 1000:
            self.data_history[symbol] = self.data_history[symbol][-1000:]
        
        # Update metrics
        self._update_market_metrics(symbol)
    
    def _update_market_metrics(self, symbol: str):
        """Bozor metrikalarini yangilash"""
        if symbol not in self.data_history or len(self.data_history[symbol]) < 20:
            return
        
        history = self.data_history[symbol]
        prices = [dp.close for dp in history]
        volumes = [dp.volume for dp in history]
        
        # Calculate metrics
        volatility = np.std(prices[-20:]) / np.mean(prices[-20:]) if len(prices) >= 20 else 0
        avg_volume = np.mean(volumes[-20:]) if len(volumes) >= 20 else 0
        
        # Price momentum (slope of last 20 points)
        if len(prices) >= 20:
            x = np.arange(20)
            y = prices[-20:]
            momentum = np.polyfit(x, y, 1)[0]
        else:
            momentum = 0
        
        # Support and resistance levels
        support = min(prices[-20:]) if len(prices) >= 20 else prices[-1]
        resistance = max(prices[-20:]) if len(prices) >= 20 else prices[-1]
        
        # Trend direction
        if momentum > 0.01:
            trend = "BULLISH"
        elif momentum < -0.01:
            trend = "BEARISH"
        else:
            trend = "SIDEWAYS"
        
        self.market_metrics[symbol] = MarketMetrics(
            symbol=symbol,
            volatility=volatility,
            avg_volume=avg_volume,
            price_momentum=momentum,
            volume_momentum=0,  # Calculate volume momentum if needed
            support_level=support,
            resistance_level=resistance,
            trend_direction=trend
        )
    
    def calculate_technical_indicators(self, symbol: str) -> Dict[str, TechnicalIndicator]:
        """Texnik indikatorlarni hisoblash"""
        if symbol not in self.data_history or len(self.data_history[symbol]) < 14:
            return {}
        
        history = self.data_history[symbol]
        closes = [dp.close for dp in history]
        volumes = [dp.volume for dp in history]
        highs = [dp.high for dp in history]
        lows = [dp.low for dp in history]
        
        indicators = {}
        
        # RSI (Relative Strength Index)
        if len(closes) >= 14:
            rsi = self._calculate_rsi(closes[-14:])
            indicators['rsi'] = TechnicalIndicator(
                name='RSI',
                value=rsi,
                timestamp=datetime.now(),
                signal='BUY' if rsi < 30 else 'SELL' if rsi > 70 else 'NEUTRAL',
                strength=min(abs(rsi - 50) / 50, 1.0)
            )
        
        # MACD
        if len(closes) >= 26:
            macd_line, signal_line, histogram = self._calculate_macd(closes[-26:])
            indicators['macd'] = TechnicalIndicator(
                name='MACD',
                value=macd_line,
                timestamp=datetime.now(),
                signal='BUY' if macd_line > signal_line else 'SELL',
                strength=min(abs(histogram), 1.0)
            )
        
        # Bollinger Bands
        if len(closes) >= 20:
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(closes[-20:])
            current_price = closes[-1]
            
            bb_signal = 'NEUTRAL'
            if current_price < bb_lower:
                bb_signal = 'BUY'
            elif current_price > bb_upper:
                bb_signal = 'SELL'
            
            indicators['bollinger'] = TechnicalIndicator(
                name='Bollinger Bands',
                value=(current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5,
                timestamp=datetime.now(),
                signal=bb_signal,
                strength=abs((current_price - bb_middle) / bb_middle) if bb_middle != 0 else 0
            )
        
        # Moving Averages
        if len(closes) >= 10:
            sma_10 = np.mean(closes[-10:])
            if len(closes) >= 20:
                sma_20 = np.mean(closes[-20:])
                ma_signal = 'BUY' if sma_10 > sma_20 else 'SELL'
                indicators['ma_cross'] = TechnicalIndicator(
                    name='MA Cross',
                    value=sma_10 / sma_20 - 1,
                    timestamp=datetime.now(),
                    signal=ma_signal,
                    strength=abs(sma_10 / sma_20 - 1)
                )
        
        self.technical_indicators[symbol] = indicators
        return indicators
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """RSI hisoblash"""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        if len(gains) < period:
            return 50.0  # Neutral RSI
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """MACD hisoblash"""
        if len(prices) < slow:
            return 0, 0, 0
        
        ema_fast = self._calculate_ema(prices, fast)
        ema_slow = self._calculate_ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        
        # For signal line, we'd need historical MACD values
        # Simplified for demo
        signal_line = macd_line * 0.9
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """EMA hisoblash"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        alpha = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
        
        return ema
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2) -> Tuple[float, float, float]:
        """Bollinger Bands hisoblash"""
        if len(prices) < period:
            price = prices[-1] if prices else 0
            return price * 1.02, price, price * 0.98
        
        sma = np.mean(prices)
        std = np.std(prices)
        
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        
        return upper, sma, lower
    
    def get_market_overview(self) -> Dict[str, Any]:
        """Bozor umumiy holatini olish"""
        overview = {
            'timestamp': datetime.now(),
            'active_symbols': len(self.current_prices),
            'symbols': []
        }
        
        for symbol, data_point in self.current_prices.items():
            indicators = self.calculate_technical_indicators(symbol)
            metrics = self.market_metrics.get(symbol)
            
            symbol_info = {
                'symbol': symbol,
                'current_price': data_point.close,
                'change': data_point.change_percent or 0,
                'volume': data_point.volume,
                'volatility': metrics.volatility if metrics else 0,
                'trend': metrics.trend_direction if metrics else 'UNKNOWN',
                'signals': {
                    'rsi': indicators.get('rsi').signal if 'rsi' in indicators else 'NEUTRAL',
                    'macd': indicators.get('macd').signal if 'macd' in indicators else 'NEUTRAL',
                    'bollinger': indicators.get('bollinger').signal if 'bollinger' in indicators else 'NEUTRAL'
                },
                'support': metrics.support_level if metrics else 0,
                'resistance': metrics.resistance_level if metrics else 0
            }
            
            overview['symbols'].append(symbol_info)
        
        return overview
    
    def get_symbol_data(self, symbol: str) -> Dict[str, Any]:
        """Belgilangan symbol uchun ma'lumotlar"""
        if symbol not in self.current_prices:
            return {'error': 'Symbol not found'}
        
        current_data = self.current_prices[symbol]
        indicators = self.calculate_technical_indicators(symbol)
        metrics = self.market_metrics.get(symbol)
        history = self.data_history.get(symbol, [])
        
        return {
            'symbol': symbol,
            'current': asdict(current_data),
            'indicators': {k: asdict(v) for k, v in indicators.items()},
            'metrics': asdict(metrics) if metrics else {},
            'history': [asdict(dp) for dp in history[-100:]],  # Last 100 points
            'last_update': datetime.now()
        }


class BinanceStreamer(DataStreamer):
    """Binance WebSocket streamer"""
    
    def __init__(self, api_key: str = "", secret: str = ""):
        self.ws_url = "wss://stream.binance.com:9443/ws"
        self.websocket = None
        self.running = False
        self.subscribed_symbols = set()
    
    async def connect(self) -> bool:
        try:
            # Add connection timeout
            self.websocket = await asyncio.wait_for(
                websockets.connect(self.ws_url, ping_interval=20, ping_timeout=10),
                timeout=10.0
            )
            self.running = True
            logger.info("Connected to Binance WebSocket")
            return True
        except asyncio.TimeoutError:
            logger.error("Binance WebSocket connection timeout")
            return False
        except Exception as e:
            logger.error(f"Binance connection failed: {str(e)}")
            return False
    
    async def disconnect(self):
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        self.running = False
        logger.info("Binance WebSocket disconnected")
    
    async def subscribe(self, symbols: List[str]):
        # Binance uses different format for symbols
        binance_symbols = [s.lower() + "@kline_1m" for s in symbols]
        
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": binance_symbols,
            "id": int(time.time())
        }
        
        if self.websocket:
            await self.websocket.send(json.dumps(subscribe_message))
            self.subscribed_symbols.update(symbols)
            logger.info(f"Subscribed to Binance: {symbols}")
    
    async def get_data(self) -> Optional[MarketDataPoint]:
        if not self.websocket or not self.running:
            return None
        
        try:
            # Add timeout to recv to prevent hanging
            message = await asyncio.wait_for(self.websocket.recv(), timeout=30.0)
            data = json.loads(message)
            
            if 'k' in data:
                kline = data['k']
                return MarketDataPoint(
                    symbol=kline.get('s', ''),
                    timestamp=datetime.fromtimestamp(kline.get('t', 0) / 1000),
                    open=float(kline.get('o', 0)),
                    high=float(kline.get('h', 0)),
                    low=float(kline.get('l', 0)),
                    close=float(kline.get('c', 0)),
                    volume=float(kline.get('v', 0)),
                    source='binance'
                )
            else:
                # Not a kline message, continue
                return None
                
        except asyncio.TimeoutError:
            # Timeout - connection might be stale
            logger.warning("Binance WebSocket timeout, connection may be stale")
            return None
            
        except (websockets.exceptions.ConnectionClosedOK, websockets.exceptions.ConnectionClosed) as e:
            # Normal closure (status 1000) - this is expected behavior, don't log as error
            if hasattr(e, 'code') and e.code == 1000:
                logger.info(f"Binance WebSocket connection closed normally (status 1000)")
            else:
                logger.info(f"Binance WebSocket connection closed: {e}")
            return None  # Return None instead of raising to break the loop
            
        except websockets.exceptions.ConnectionClosedError as e:
            # Connection error - log and handle
            logger.error(f"Binance WebSocket connection error: {e}")
            return None  # Return None to break the retry loop
            
        except Exception as e:
            logger.error(f"Error getting Binance data: {str(e)}")
            return None


class CoinbaseStreamer(DataStreamer):
    """Coinbase WebSocket streamer"""
    
    def __init__(self):
        self.ws_url = "wss://ws-feed.exchange.coinbase.com"
        self.websocket = None
        self.running = False
        self.subscribed_symbols = set()
    
    async def connect(self) -> bool:
        try:
            # Add connection timeout
            self.websocket = await asyncio.wait_for(
                websockets.connect(self.ws_url, ping_interval=20, ping_timeout=10),
                timeout=10.0
            )
            self.running = True
            logger.info("Connected to Coinbase WebSocket")
            return True
        except asyncio.TimeoutError:
            logger.error("Coinbase WebSocket connection timeout")
            return False
        except Exception as e:
            logger.error(f"Coinbase connection failed: {str(e)}")
            return False
    
    async def disconnect(self):
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        self.running = False
        logger.info("Coinbase WebSocket disconnected")
    
    async def subscribe(self, symbols: List[str]):
        subscribe_message = {
            "type": "subscribe",
            "product_ids": symbols,
            "channels": ["ticker"]
        }
        
        if self.websocket:
            await self.websocket.send(json.dumps(subscribe_message))
            self.subscribed_symbols.update(symbols)
            logger.info(f"Subscribed to Coinbase: {symbols}")
    
    async def get_data(self) -> Optional[MarketDataPoint]:
        if not self.websocket or not self.running:
            return None
        
        try:
            # Add timeout to recv to prevent hanging
            message = await asyncio.wait_for(self.websocket.recv(), timeout=30.0)
            data = json.loads(message)
            
            if data.get('type') == 'ticker':
                return MarketDataPoint(
                    symbol=data.get('product_id', ''),
                    timestamp=datetime.fromisoformat(data.get('time', '').replace('Z', '+00:00')),
                    open=float(data.get('open_24h', 0)),
                    high=float(data.get('high_24h', 0)),
                    low=float(data.get('low_24h', 0)),
                    close=float(data.get('price', 0)),
                    volume=float(data.get('volume_24h', 0)),
                    source='coinbase'
                )
            else:
                # Not a ticker message, continue
                return None
                
        except asyncio.TimeoutError:
            # Timeout - connection might be stale
            logger.warning("Coinbase WebSocket timeout, connection may be stale")
            return None
            
        except (websockets.exceptions.ConnectionClosedOK, websockets.exceptions.ConnectionClosed) as e:
            # DEBUG: log the exact exception details
            logger.debug(f"DEBUG: Caught connection exception - Type: {type(e).__name__}, Code: {getattr(e, 'code', 'N/A')}, Args: {e.args}")
            # Normal closure (status 1000) - this is expected behavior, don't log as error
            if hasattr(e, 'code') and e.code == 1000:
                logger.info(f"Coinbase WebSocket connection closed normally (status 1000)")
            else:
                logger.info(f"Coinbase WebSocket connection closed: {e}")
            return None  # Return None instead of raising to break the loop
            
        except websockets.exceptions.ConnectionClosedError as e:
            # Connection error - log and handle
            logger.error(f"Coinbase WebSocket connection error: {e}")
            return None  # Return None to break the retry loop
            
        except Exception as e:
            # DEBUG: Check if this is actually a ConnectionClosedOK that should have been caught above
            if isinstance(e, (websockets.exceptions.ConnectionClosedOK, websockets.exceptions.ConnectionClosed)):
                logger.warning(f"DEBUG: ConnectionClosedOK fell through to general handler! Type: {type(e).__name__}, Code: {getattr(e, 'code', 'N/A')}")
            logger.error(f"Error getting Coinbase data: {str(e)}")
            return None


class MarketDataManager:
    """Bozor ma'lumotlari boshqaruvchisi"""
    
    def __init__(self):
        self.processor = MarketDataProcessor()
        self.streamers = {}
        self.running = False
        self._setup_streamers()
    
    def _setup_streamers(self):
        """Streamer'larni sozlash"""
        # Binance streamer
        binance_streamer = BinanceStreamer()
        self.streamers['binance'] = binance_streamer
        
        # Coinbase streamer
        coinbase_streamer = CoinbaseStreamer()
        self.streamers['coinbase'] = coinbase_streamer
    
    async def start_streaming(self, symbols: List[str], providers: List[str] = None):
        """Streaming boshlash"""
        if providers is None:
            providers = list(self.streamers.keys())
        
        self.running = True
        
        # Connect to all providers with proper retry logic
        connection_tasks = []
        for provider in providers:
            if provider in self.streamers and self.running:
                streamer = self.streamers[provider]
                
                # Multiple connection attempts with limits
                max_connection_retries = 2
                connection_success = False
                
                for attempt in range(max_connection_retries):
                    if not self.running:  # Check if stopped
                        break
                        
                    try:
                        success = await asyncio.wait_for(streamer.connect(), timeout=10.0)
                        if success:
                            await asyncio.wait_for(streamer.subscribe(symbols), timeout=5.0)
                            logger.info(f"Started streaming {symbols} from {provider}")
                            
                            # Start data collection task
                            task = asyncio.create_task(self._collect_data(streamer, provider))
                            connection_tasks.append((provider, task))
                            connection_success = True
                            break  # Success, exit retry loop
                        else:
                            logger.warning(f"Connection attempt {attempt + 1} failed for {provider}")
                            
                    except asyncio.TimeoutError:
                        logger.warning(f"Connection timeout for {provider}, attempt {attempt + 1}")
                    except Exception as e:
                        logger.error(f"Connection error for {provider}, attempt {attempt + 1}: {str(e)}")
                    
                    # Wait before retry, but not on last attempt
                    if attempt < max_connection_retries - 1:
                        await asyncio.sleep(2)
                
                if not connection_success:
                    logger.error(f"Failed to connect to {provider} after {max_connection_retries} attempts")
        
        # Wait for all connection tasks to complete or until stopped
        if connection_tasks:
            try:
                # Wait for all tasks but don't propagate exceptions
                await asyncio.gather(*[task for _, task in connection_tasks], return_exceptions=True)
            except asyncio.CancelledError:
                logger.info("Streaming cancelled")
            except Exception as e:
                logger.error(f"Streaming error: {e}")
    
    async def _collect_data(self, streamer: DataStreamer, provider: str):
        """Ma'lumotlarni yig'ish - controlled loop bilan"""
        retry_count = 0
        max_retries = 3
        retry_delay = 2
        
        while self.running and streamer.running and retry_count < max_retries:
            try:
                data_point = await streamer.get_data()
                if data_point:
                    # Process the data
                    self.processor.add_data_point(data_point)
                    logger.debug(f"Received data from {provider}: {data_point.symbol}")
                    retry_count = 0  # Reset retry count on successful data
                else:
                    # No data received, small delay
                    await asyncio.sleep(0.5)
                    
            except websockets.exceptions.ConnectionClosedOK as e:
                # Normal closure (status 1000) - exit gracefully
                if hasattr(e, 'code') and e.code == 1000:
                    logger.info(f"WebSocket connection closed normally for {provider} (status 1000)")
                    break
                else:
                    logger.info(f"WebSocket connection closed for {provider} (status {getattr(e, 'code', 'unknown')})")
                    break
                
            except websockets.exceptions.ConnectionClosedError as e:
                # Connection error - log and retry
                logger.error(f"WebSocket connection error for {provider}: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    logger.info(f"Retrying {provider} connection ({retry_count}/{max_retries}) in {retry_delay}s")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Max retries reached for {provider}, giving up")
                    break
                    
            except Exception as e:
                # Other errors - log and retry
                logger.error(f"Error collecting data from {provider}: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(1)
                else:
                    logger.error(f"Max retries reached for {provider}, stopping")
                    break
        
        logger.info(f"Data collection stopped for {provider}")
        # Mark streamer as not running
        streamer.running = False
    
    async def stop_streaming(self, provider: str = None):
        """Streaming to'xtatish"""
        # Stop main running state
        self.running = False
        
        if provider:
            # Stop specific provider
            if provider in self.streamers:
                streamer = self.streamers[provider]
                streamer.running = False
                await streamer.disconnect()
                logger.info(f"Stopped streaming from {provider}")
        else:
            # Stop all streams
            stop_tasks = []
            for provider, streamer in self.streamers.items():
                streamer.running = False
                disconnect_task = asyncio.create_task(streamer.disconnect())
                stop_tasks.append(disconnect_task)
                logger.info(f"Stopping streaming from {provider}")
            
            # Wait for all disconnections to complete
            if stop_tasks:
                try:
                    await asyncio.gather(*stop_tasks, return_exceptions=True)
                except Exception as e:
                    logger.error(f"Error during stream shutdown: {e}")
            
            logger.info("Stopped all streams")
    
    def get_real_time_data(self, symbol: str) -> Dict[str, Any]:
        """Real-time ma'lumotlarni olish"""
        return self.processor.get_symbol_data(symbol)
    
    def get_market_overview(self) -> Dict[str, Any]:
        """Bozor umumiy holati"""
        return self.processor.get_market_overview()
    
    def get_historical_data(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Tarixiy ma'lumotlar"""
        if symbol not in self.processor.data_history:
            return []
        
        history = self.processor.data_history[symbol]
        return [asdict(dp) for dp in history[-limit:]]
    
    def get_technical_analysis(self, symbol: str) -> Dict[str, Any]:
        """Texnik analiz"""
        return self.processor.get_symbol_data(symbol)


# Multi-timeframe data fetcher
class MultiTimeframeFetcher:
    """Ko'p vaqt intervali ma'lumotlarini olish"""
    
    def __init__(self, market_manager: MarketDataManager):
        self.market_manager = market_manager
        self.timeframes = {
            '1m': 60,
            '5m': 300,
            '15m': 900,
            '1h': 3600,
            '4h': 14400,
            '1d': 86400
        }
    
    async def get_multi_timeframe_data(self, symbol: str) -> Dict[str, Any]:
        """Ko'p vaqt intervali ma'lumotlari"""
        # For demo, simulate different timeframes
        # In production, this would aggregate data from different sources
        
        multi_tf_data = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'timeframes': {}
        }
        
        # Simulate data for each timeframe
        for tf, _ in self.timeframes.items():
            tf_data = {
                'timeframe': tf,
                'price': np.random.uniform(100, 200),
                'volume': np.random.randint(10000, 100000),
                'change': np.random.uniform(-5, 5),
                'indicators': {
                    'rsi': np.random.uniform(20, 80),
                    'macd': np.random.uniform(-2, 2),
                    'ma20': np.random.uniform(90, 110)
                }
            }
            multi_tf_data['timeframes'][tf] = tf_data
        
        return multi_tf_data


# Demo usage
async def demo_market_data():
    """Bozor ma'lumotlari demo - timeout bilan"""
    print("=== Real-time Bozor Ma'lumotlari Demo ===")
    
    manager = MarketDataManager()
    fetcher = MultiTimeframeFetcher(manager)
    
    # Start streaming with timeout
    symbols = ["BTCUSDT", "ETHUSDT"]
    print(f"\n=== {symbols} uchun streaming boshlash ===")
    
    # Create streaming task with timeout
    streaming_task = asyncio.create_task(manager.start_streaming(symbols))
    
    try:
        # Wait for streaming to start (max 5 seconds)
        await asyncio.wait_for(streaming_task, timeout=5.0)
        print("✅ Streaming muvaffaqiyatli boshirildi")
    except asyncio.TimeoutError:
        print("❌ Streaming boshlanishda timeout")
        await manager.stop_streaming()
        return
    except Exception as e:
        print(f"❌ Streaming xatosi: {e}")
        await manager.stop_streaming()
        return
    
    # Wait for some data with timeout
    try:
        print("Ma'lumot kutish... (3 soniya)")
        await asyncio.sleep(3)
        
        # Get market overview
        print("\n=== Bozor umumiy holati ===")
        overview = manager.get_market_overview()
        print(json.dumps(overview, indent=2, default=str))
        
        # Get specific symbol data
        print(f"\n=== {symbols[0]} uchun batafsil ma'lumotlar ===")
        symbol_data = manager.get_real_time_data(symbols[0])
        print(json.dumps(symbol_data, indent=2, default=str))
        
        # Get multi-timeframe data
        print(f"\n=== {symbols[0]} uchun ko'p vaqt intervali ===")
        multi_tf = await fetcher.get_multi_timeframe_data(symbols[0])
        print(json.dumps(multi_tf, indent=2, default=str))
        
    except Exception as e:
        print(f"Ma'lumot olish xatosi: {e}")
    
    finally:
        # Stop streaming
        print("\n=== Streaming to'xtatilmoqda ===")
        await manager.stop_streaming()
        print("✅ Demo tugallandi")


if __name__ == "__main__":
    # Add overall timeout to prevent infinite running
    try:
        asyncio.run(asyncio.wait_for(demo_market_data(), timeout=30.0))
    except asyncio.TimeoutError:
        print("❌ Demo timeout - 30 soniyada tugallanishi kerak")
    except Exception as e:
        print(f"❌ Demo xatosi: {e}")