"""
Real-time Ma'lumotlar Integratsiya Tizimi
Real-time Data Integration System

Asosiy ma'lumotlar integratsiya moduli - turli API'lardan real-time ma'lumotlarni birlashtirish
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DataSource:
    """Ma'lumot manbai konfiguratsiyasi"""
    name: str
    api_key: str
    base_url: str
    rate_limit: int
    active: bool = True
    priority: int = 1
    data_types: List[str] = None


@dataclass
class DataPoint:
    """Ma'lumot nuqtasi struktura"""
    symbol: str
    timestamp: datetime
    data_type: str
    value: float
    volume: Optional[float] = None
    source: str = ""
    metadata: Dict[str, Any] = None


class DataProvider(ABC):
    """Ma'lumot provider base class"""
    
    @abstractmethod
    async def get_market_data(self, symbol: str, timeframe: str = "1m") -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def get_news_data(self, symbol: str = None) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def get_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        pass


class DataIntegrationEngine:
    """Real-time ma'lumotlar integratsiya dvijka"""
    
    def __init__(self):
        self.data_sources = {}
        self.data_providers = {}
        self.cache = {}
        self.data_streams = {}
        self.integrated_data = {}
        self.last_update = {}
        
        # Data quality settings
        self.quality_thresholds = {
            'min_data_points': 10,
            'max_data_age_minutes': 5,
            'required_sources': 2
        }
        
        # Performance monitoring
        self.performance_metrics = {
            'requests_per_second': 0,
            'data_freshness': {},
            'source_reliability': {}
        }
    
    def add_data_source(self, source: DataSource):
        """Ma'lumot manbaini qo'shish"""
        self.data_sources[source.name] = source
        logger.info(f"Data source added: {source.name}")
    
    def add_data_provider(self, name: str, provider: DataProvider):
        """Ma'lumot provider qo'shish"""
        self.data_providers[name] = provider
        logger.info(f"Data provider added: {name}")
    
    async def integrate_market_data(self, symbol: str, timeframe: str = "1m") -> Dict[str, Any]:
        """Bozor ma'lumotlarini integratsiya qilish"""
        try:
            integrated_data = {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': datetime.now(),
                'sources': {},
                'consensus': {},
                'quality_score': 0.0
            }
            
            # Get data from all available sources
            tasks = []
            for name, provider in self.data_providers.items():
                if asyncio.iscoroutinefunction(provider.get_market_data):
                    task = asyncio.create_task(
                        self._safe_provider_call(provider.get_market_data, symbol, timeframe)
                    )
                else:
                    task = asyncio.create_task(
                        self._safe_provider_call_sync(provider.get_market_data, symbol, timeframe)
                    )
                tasks.append((name, task))
            
            # Collect results with timeout
            timeout = 5.0
            for name, task in tasks:
                try:
                    result = await asyncio.wait_for(task, timeout=timeout)
                    integrated_data['sources'][name] = {
                        'data': result,
                        'timestamp': datetime.now(),
                        'success': True
                    }
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout for {name} data source")
                    integrated_data['sources'][name] = {
                        'error': 'timeout',
                        'success': False
                    }
                except Exception as e:
                    logger.error(f"Error from {name}: {str(e)}")
                    integrated_data['sources'][name] = {
                        'error': str(e),
                        'success': False
                    }
            
            # Calculate consensus values
            if integrated_data['sources']:
                integrated_data['consensus'] = self._calculate_consensus(integrated_data['sources'])
                integrated_data['quality_score'] = self._calculate_quality_score(integrated_data['sources'])
            
            # Cache the result
            cache_key = f"{symbol}_{timeframe}"
            self.cache[cache_key] = integrated_data
            self.last_update[cache_key] = datetime.now()
            
            return integrated_data
            
        except Exception as e:
            logger.error(f"Error integrating market data for {symbol}: {str(e)}")
            return {}
    
    async def _safe_provider_call(self, func, *args, **kwargs):
        """Xavfsiz provider chaqiruvi"""
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Provider call error: {str(e)}")
            raise
    
    async def _safe_provider_call_sync(self, func, *args, **kwargs):
        """Xavfsiz sync provider chaqiruvi"""
        try:
            return await asyncio.to_thread(func, *args, **kwargs)
        except Exception as e:
            logger.error(f"Sync provider call error: {str(e)}")
            raise
    
    def _calculate_consensus(self, sources_data: Dict[str, Any]) -> Dict[str, float]:
        """Barcha manbalardan konsensus qiymatlarni hisoblash"""
        consensus = {}
        price_data = []
        volume_data = []
        
        for source, data in sources_data.items():
            if data.get('success') and 'data' in data:
                source_data = data['data']
                
                # Extract price data
                if 'price' in source_data:
                    price_data.append(source_data['price'])
                elif 'close' in source_data:
                    price_data.append(source_data['close'])
                elif 'last_price' in source_data:
                    price_data.append(source_data['last_price'])
                
                # Extract volume data
                if 'volume' in source_data:
                    volume_data.append(source_data['volume'])
        
        # Calculate consensus values
        if price_data:
            consensus['price'] = {
                'mean': np.mean(price_data),
                'median': np.median(price_data),
                'std': np.std(price_data),
                'weighted_mean': np.average(price_data),
                'outlier_filtered': self._remove_outliers(price_data)
            }
        
        if volume_data:
            consensus['volume'] = {
                'mean': np.mean(volume_data),
                'median': np.median(volume_data),
                'std': np.std(volume_data)
            }
        
        return consensus
    
    def _remove_outliers(self, data: List[float]) -> List[float]:
        """Outlier'larni olib tashlash"""
        if len(data) < 3:
            return data
        
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        return [x for x in data if lower_bound <= x <= upper_bound]
    
    def _calculate_quality_score(self, sources_data: Dict[str, Any]) -> float:
        """Ma'lumotlar sifati ballini hisoblash"""
        total_sources = len(sources_data)
        successful_sources = sum(1 for data in sources_data.values() if data.get('success', False))
        
        if total_sources == 0:
            return 0.0
        
        # Base score from success rate
        success_score = successful_sources / total_sources
        
        # Penalty for missing critical data
        penalty = 0.0
        if successful_sources < self.quality_thresholds['required_sources']:
            penalty = 0.2
        
        return max(0.0, success_score - penalty)
    
    async def get_multi_timeframe_data(self, symbol: str) -> Dict[str, Dict[str, Any]]:
        """Ko'p vaqt intervali ma'lumotlarini olish"""
        timeframes = ['1m', '5m', '15m', '1h', '4h', '1d']
        multi_tf_data = {}
        
        # Use ThreadPoolExecutor for concurrent requests
        with ThreadPoolExecutor(max_workers=len(timeframes)) as executor:
            tasks = []
            for tf in timeframes:
                task = asyncio.create_task(
                    self.integrate_market_data(symbol, tf)
                )
                tasks.append((tf, task))
            
            for tf, task in tasks:
                try:
                    result = await task
                    multi_tf_data[tf] = result
                except Exception as e:
                    logger.error(f"Error getting {tf} data for {symbol}: {str(e)}")
                    multi_tf_data[tf] = {'error': str(e)}
        
        return multi_tf_data
    
    async def get_economic_calendar_data(self) -> List[Dict[str, Any]]:
        """Iqtisodiy kalendar ma'lumotlarini olish"""
        # Placeholder for economic calendar data
        calendar_data = [
            {
                'event': 'Federal Funds Rate Decision',
                'date': datetime.now() + timedelta(days=1),
                'impact': 'High',
                'currency': 'USD',
                'forecast': '5.25%',
                'previous': '5.00%'
            },
            {
                'event': 'Non-Farm Payrolls',
                'date': datetime.now() + timedelta(days=2),
                'impact': 'High',
                'currency': 'USD',
                'forecast': '200K',
                'previous': '150K'
            }
        ]
        
        return calendar_data
    
    async def get_sentiment_data(self, symbol: str) -> Dict[str, Any]:
        """Sentiment ma'lumotlarini olish"""
        # Placeholder for sentiment analysis
        sentiment_data = {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'social_sentiment': {
                'score': 0.75,
                'twitter_mentions': 1250,
                'reddit_posts': 85,
                'news_sentiment': 'Positive'
            },
            'news_sentiment': {
                'overall_score': 0.68,
                'positive_articles': 12,
                'negative_articles': 3,
                'neutral_articles': 8
            },
            'technical_sentiment': {
                'rsi': 65.5,
                'macd': 0.12,
                'bollinger_position': 0.45
            }
        }
        
        return sentiment_data
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Cache holatini olish"""
        status = {
            'cache_size': len(self.cache),
            'last_updates': self.last_update,
            'performance_metrics': self.performance_metrics
        }
        
        return status
    
    async def clear_cache(self, symbol: str = None):
        """Cache'ni tozalash"""
        if symbol:
            # Clear specific symbol cache
            keys_to_remove = [key for key in self.cache.keys() if key.startswith(symbol)]
            for key in keys_to_remove:
                del self.cache[key]
                if key in self.last_update:
                    del self.last_update[key]
        else:
            # Clear all cache
            self.cache.clear()
            self.last_update.clear()
        
        logger.info(f"Cache cleared for symbol: {symbol or 'all'}")
    
    async def validate_data_quality(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Ma'lumotlar sifati validatsiyasi"""
        cache_key = f"{symbol}_{timeframe}"
        
        if cache_key not in self.cache:
            return {'valid': False, 'reason': 'No data in cache'}
        
        data = self.cache[cache_key]
        last_update = self.last_update.get(cache_key)
        
        # Check data freshness
        if last_update:
            age_minutes = (datetime.now() - last_update).total_seconds() / 60
            if age_minutes > self.quality_thresholds['max_data_age_minutes']:
                return {'valid': False, 'reason': f'Data too old: {age_minutes:.1f} minutes'}
        
        # Check data completeness
        quality_score = data.get('quality_score', 0.0)
        if quality_score < 0.5:
            return {'valid': False, 'reason': f'Low quality score: {quality_score:.2f}'}
        
        return {
            'valid': True,
            'quality_score': quality_score,
            'age_minutes': age_minutes if last_update else None,
            'sources_count': len(data.get('sources', {}))
        }


# Yahoo Finance API Integration
class YahooFinanceProvider(DataProvider):
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://query1.finance.yahoo.com"
    
    async def get_market_data(self, symbol: str, timeframe: str = "1m") -> Dict[str, Any]:
        # Placeholder implementation
        await asyncio.sleep(0.1)  # Simulate API call
        return {
            'symbol': symbol,
            'price': np.random.uniform(100, 200),
            'volume': np.random.randint(10000, 100000),
            'timestamp': datetime.now(),
            'source': 'yahoo_finance'
        }
    
    async def get_news_data(self, symbol: str = None) -> List[Dict[str, Any]]:
        return []
    
    async def get_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        return {}


# Alpha Vantage Integration
class AlphaVantageProvider(DataProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
    
    async def get_market_data(self, symbol: str, timeframe: str = "1m") -> Dict[str, Any]:
        await asyncio.sleep(0.15)
        return {
            'symbol': symbol,
            'price': np.random.uniform(100, 200),
            'volume': np.random.randint(10000, 100000),
            'timestamp': datetime.now(),
            'source': 'alpha_vantage'
        }
    
    async def get_news_data(self, symbol: str = None) -> List[Dict[str, Any]]:
        return []
    
    async def get_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        return {}


# IEX Cloud Integration
class IEXCloudProvider(DataProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://cloud.iexapis.com"
    
    async def get_market_data(self, symbol: str, timeframe: str = "1m") -> Dict[str, Any]:
        await asyncio.sleep(0.1)
        return {
            'symbol': symbol,
            'price': np.random.uniform(100, 200),
            'volume': np.random.randint(10000, 100000),
            'timestamp': datetime.now(),
            'source': 'iex_cloud'
        }
    
    async def get_news_data(self, symbol: str = None) -> List[Dict[str, Any]]:
        return []
    
    async def get_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        return {}


class DataIntegrationManager:
    """Ma'lumotlar integratsiya boshqaruvchisi"""
    
    def __init__(self):
        self.engine = DataIntegrationEngine()
        self._setup_providers()
    
    def _setup_providers(self):
        """Ma'lumot provider'larni sozlash"""
        # Yahoo Finance
        yahoo_provider = YahooFinanceProvider()
        self.engine.add_data_provider("yahoo", yahoo_provider)
        
        # Alpha Vantage
        alpha_provider = AlphaVantageProvider("demo_key")
        self.engine.add_data_provider("alpha_vantage", alpha_provider)
        
        # IEX Cloud
        iex_provider = IEXCloudProvider("demo_key")
        self.engine.add_data_provider("iex_cloud", iex_provider)
    
    async def get_comprehensive_market_data(self, symbol: str) -> Dict[str, Any]:
        """Keng qamrovli bozor ma'lumotlari"""
        try:
            # Get multi-timeframe data
            multi_tf = await self.engine.get_multi_timeframe_data(symbol)
            
            # Get economic calendar
            economic_calendar = await self.engine.get_economic_calendar_data()
            
            # Get sentiment data
            sentiment = await self.engine.get_sentiment_data(symbol)
            
            # Get consensus data
            consensus = await self.engine.integrate_market_data(symbol)
            
            comprehensive_data = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'multi_timeframe': multi_tf,
                'consensus': consensus,
                'sentiment': sentiment,
                'economic_calendar': economic_calendar,
                'data_quality': await self.engine.validate_data_quality(symbol, "1m")
            }
            
            return comprehensive_data
            
        except Exception as e:
            logger.error(f"Error getting comprehensive data for {symbol}: {str(e)}")
            return {}
    
    async def start_real_time_stream(self, symbols: List[str]):
        """Real-time stream boshlash"""
        logger.info(f"Starting real-time stream for symbols: {symbols}")
        
        for symbol in symbols:
            self.engine.data_streams[symbol] = asyncio.create_task(
                self._stream_symbol_data(symbol)
            )
    
    async def _stream_symbol_data(self, symbol: str):
        """Symbol ma'lumotlarini stream qilish"""
        while symbol in self.engine.data_streams:
            try:
                data = await self.engine.integrate_market_data(symbol)
                # Here you would typically send data to clients via WebSocket
                logger.info(f"Streaming data for {symbol}")
                await asyncio.sleep(1)  # 1 second update interval
            except Exception as e:
                logger.error(f"Error streaming {symbol}: {str(e)}")
                await asyncio.sleep(5)  # Wait before retry
    
    async def stop_real_time_stream(self, symbol: str = None):
        """Real-time stream to'xtatish"""
        if symbol:
            if symbol in self.engine.data_streams:
                self.engine.data_streams[symbol].cancel()
                del self.engine.data_streams[symbol]
                logger.info(f"Stopped stream for {symbol}")
        else:
            # Stop all streams
            for symbol, task in self.engine.data_streams.items():
                task.cancel()
            self.engine.data_streams.clear()
            logger.info("Stopped all streams")


# Demo usage
async def demo_data_integration():
    """Ma'lumotlar integratsiya demo"""
    print("=== Real-time Ma'lumotlar Integratsiya Tizimi Demo ===")
    
    manager = DataIntegrationManager()
    
    # Single symbol comprehensive data
    symbol = "AAPL"
    print(f"\n=== {symbol} uchun keng qamrovli ma'lumotlar ===")
    comprehensive_data = await manager.get_comprehensive_market_data(symbol)
    print(json.dumps(comprehensive_data, indent=2, default=str))
    
    # Multi symbol data
    symbols = ["AAPL", "GOOGL", "MSFT"]
    print(f"\n=== Ko'p {symbols} uchun ma'lumotlar ===")
    for sym in symbols:
        data = await manager.engine.integrate_market_data(sym)
        print(f"{sym}: {data.get('quality_score', 0.0):.2f} quality score")
    
    # Real-time streaming
    print(f"\n=== Real-time streaming test ===")
    await manager.start_real_time_stream(["AAPL"])
    await asyncio.sleep(3)  # Stream for 3 seconds
    await manager.stop_real_time_stream("AAPL")
    
    # Cache status
    print(f"\n=== Cache holati ===")
    cache_status = manager.engine.get_cache_status()
    print(json.dumps(cache_status, indent=2, default=str))


# Signal Generation Integration
class SignalGenerator:
    """AI Signal Generation Integration"""
    
    def __init__(self, integration_engine: DataIntegrationEngine):
        self.engine = integration_engine
        self.signal_models = {}
        self.active_signals = {}
    
    async def generate_signals(self, symbol: str) -> Dict[str, Any]:
        """AI signals generatsiya qilish"""
        try:
            # Get comprehensive data
            data = await self.engine.integrate_market_data(symbol)
            multi_tf = await self.engine.get_multi_timeframe_data(symbol)
            sentiment = await self.engine.get_sentiment_data(symbol)
            
            signals = {
                'symbol': symbol,
                'timestamp': datetime.now(),
                'signals': {
                    'buy': [],
                    'sell': [],
                    'hold': []
                },
                'confidence': 0.0,
                'reasons': []
            }
            
            # Technical analysis signals
            for timeframe, tf_data in multi_tf.items():
                if tf_data.get('consensus', {}).get('price'):
                    price_data = tf_data['consensus']['price']
                    
                    if price_data.get('mean', 0) > 0:
                        # Simple signal logic
                        if 'rsi' in tf_data.get('indicators', {}):
                            rsi = tf_data['indicators']['rsi']
                            if rsi < 30:
                                signals['signals']['buy'].append({
                                    'type': 'technical',
                                    'timeframe': timeframe,
                                    'indicator': 'RSI',
                                    'signal': 'OVERSOLD',
                                    'strength': 0.7
                                })
                            elif rsi > 70:
                                signals['signals']['sell'].append({
                                    'type': 'technical',
                                    'timeframe': timeframe,
                                    'indicator': 'RSI',
                                    'signal': 'OVERBOUGHT',
                                    'strength': 0.7
                                })
            
            # Sentiment-based signals
            if sentiment.get('twitter_sentiment', {}).get('score', 0) > 0.6:
                signals['signals']['buy'].append({
                    'type': 'sentiment',
                    'source': 'social_media',
                    'signal': 'POSITIVE_MOMENTUM',
                    'strength': 0.6
                })
            
            # Calculate overall confidence
            all_signals = signals['signals']['buy'] + signals['signals']['sell']
            if all_signals:
                signals['confidence'] = np.mean([s['strength'] for s in all_signals])
            
            # Generate reasons
            if signals['signals']['buy']:
                signals['reasons'].append(f"Strong buy signals detected: {len(signals['signals']['buy'])}")
            if signals['signals']['sell']:
                signals['reasons'].append(f"Sell pressure identified: {len(signals['signals']['sell'])}")
            
            return signals
            
        except Exception as e:
            logger.error(f"Signal generation error: {e}")
            return {}


# Risk Analytics Integration
class RiskAnalyticsIntegration:
    """Portfolio Risk Analytics Integration"""
    
    def __init__(self, integration_engine: DataIntegrationEngine):
        self.engine = integration_engine
        self.risk_models = {}
        self.portfolio_cache = {}
    
    async def calculate_portfolio_risk(self, user_id: str, positions: List[Dict]) -> Dict[str, Any]:
        """Portfolio risk metrikalarini hisoblash"""
        try:
            # Get current market data for all positions
            symbols = [pos.get('symbol') for pos in positions if pos.get('symbol')]
            
            market_data = {}
            for symbol in symbols:
                data = await self.engine.integrate_market_data(symbol)
                market_data[symbol] = data
            
            # Calculate portfolio metrics
            total_value = 0
            total_risk = 0
            position_details = []
            
            for position in positions:
                symbol = position.get('symbol')
                if symbol not in market_data:
                    continue
                
                current_price = market_data[symbol].get('consensus', {}).get('price', {}).get('mean', 0)
                quantity = position.get('quantity', 0)
                position_value = current_price * quantity
                total_value += position_value
                
                # Calculate position risk (simplified)
                volatility = 0.2  # Default volatility
                if market_data[symbol].get('quality_score', 0) > 0.7:
                    # Get actual volatility from market data
                    pass
                
                position_risk = position_value * volatility
                total_risk += position_risk
                
                position_details.append({
                    'symbol': symbol,
                    'value': position_value,
                    'weight': position_value / total_value if total_value > 0 else 0,
                    'risk': position_risk,
                    'volatility': volatility
                })
            
            # Portfolio risk metrics
            risk_metrics = {
                'user_id': user_id,
                'timestamp': datetime.now(),
                'total_value': total_value,
                'total_risk': total_risk,
                'risk_value_ratio': total_risk / total_value if total_value > 0 else 0,
                'position_count': len(positions),
                'diversification_score': self._calculate_diversification(position_details),
                'var_95': total_risk * 1.65,  # 95% VaR approximation
                'var_99': total_risk * 2.33,  # 99% VaR approximation
                'max_drawdown_estimate': total_risk * 0.5,  # Conservative estimate
                'sharpe_ratio_estimate': total_value / total_risk if total_risk > 0 else 0,
                'position_details': position_details
            }
            
            return risk_metrics
            
        except Exception as e:
            logger.error(f"Portfolio risk calculation error: {e}")
            return {}
    
    def _calculate_diversification(self, positions: List[Dict]) -> float:
        """Diversifikatsiya ballini hisoblash"""
        if not positions:
            return 0.0
        
        # Calculate Herfindahl-Hirschman Index
        weights = [pos.get('weight', 0) for pos in positions]
        hhi = sum(w**2 for w in weights)
        
        # Convert to diversification score (0-1, where 1 is well diversified)
        return 1 - hhi


# API Rate Limiting
class RateLimiter:
    """API rate limiting management"""
    
    def __init__(self):
        self.request_counts = {}
        self.last_reset = {}
        self.limits = {
            'yahoo': {'requests': 100, 'window': 3600},  # 100 requests per hour
            'alpha_vantage': {'requests': 25, 'window': 86400},  # 25 requests per day
            'finnhub': {'requests': 60, 'window': 60}  # 60 requests per minute
        }
    
    def can_make_request(self, source: str) -> bool:
        """Request qilish mumkinligini tekshirish"""
        if source not in self.limits:
            return True
        
        current_time = time.time()
        window = self.limits[source]['window']
        limit = self.limits[source]['requests']
        
        # Reset counter if window has passed
        if source not in self.last_reset or current_time - self.last_reset[source] > window:
            self.request_counts[source] = 0
            self.last_reset[source] = current_time
        
        return self.request_counts[source] < limit
    
    def record_request(self, source: str) -> None:
        """Request ni ro'yxatga olish"""
        if source in self.request_counts:
            self.request_counts[source] += 1
        else:
            self.request_counts[source] = 1


# Anomaly Detection
class AnomalyDetector:
    """Market anomaly detection"""
    
    def __init__(self):
        self.thresholds = {
            'price_change': 0.05,  # 5% price change
            'volume_spike': 3.0,  # 3x average volume
            'volatility': 0.03,  # 3% volatility
            'correlation_breakdown': 0.7  # 70% correlation threshold
        }
    
    def detect_price_anomaly(self, current_price: float, historical_prices: List[float]) -> Dict[str, Any]:
        """Narx anomalisini aniqlash"""
        if len(historical_prices) < 10:
            return {'is_anomaly': False}
        
        # Calculate z-score
        mean_price = np.mean(historical_prices)
        std_price = np.std(historical_prices)
        
        if std_price == 0:
            return {'is_anomaly': False}
        
        z_score = abs((current_price - mean_price) / std_price)
        is_anomaly = z_score > 2.5  # 2.5 standard deviations
        
        return {
            'is_anomaly': is_anomaly,
            'z_score': z_score,
            'current_price': current_price,
            'mean_price': mean_price,
            'std_deviation': std_price,
            'threshold': 2.5,
            'severity': min(z_score / 5.0, 1.0)  # Normalize to 0-1
        }
    
    def detect_volume_anomaly(self, current_volume: float, historical_volumes: List[float]) -> Dict[str, Any]:
        """Hajm anomalisini aniqlash"""
        if len(historical_volumes) < 10:
            return {'is_anomaly': False}
        
        avg_volume = np.mean(historical_volumes)
        if avg_volume == 0:
            return {'is_anomaly': False}
        
        volume_ratio = current_volume / avg_volume
        is_anomaly = volume_ratio > 3.0  # 3x average
        
        return {
            'is_anomaly': is_anomaly,
            'current_volume': current_volume,
            'average_volume': avg_volume,
            'volume_ratio': volume_ratio,
            'threshold': 3.0,
            'severity': min((volume_ratio - 1) / 5.0, 1.0)
        }
    
    def detect_market_manipulation(self, symbol: str, price_data: List[Dict]) -> Dict[str, Any]:
        """Market manipulation aniqlash (soddalashtirilgan)"""
        if len(price_data) < 50:
            return {'is_manipulation': False}
        
        # Look for suspicious patterns
        anomalies = []
        
        # Check for wash trading patterns
        consecutive_same = 0
        max_consecutive_same = 0
        
        for i in range(1, len(price_data)):
            current = price_data[i].get('close', 0)
            previous = price_data[i-1].get('close', 0)
            
            if abs(current - previous) / previous < 0.001:  # Less than 0.1% change
                consecutive_same += 1
                max_consecutive_same = max(max_consecutive_same, consecutive_same)
            else:
                consecutive_same = 0
        
        if max_consecutive_same > 10:
            anomalies.append('high_frequency_wash_trading')
        
        # Check for price manipulation
        prices = [p.get('close', 0) for p in price_data[-30:]]
        if len(prices) >= 20:
            price_changes = [abs(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            large_moves = sum(1 for change in price_changes if change > 0.02)  # >2% moves
            
            if large_moves > 5:  # More than 5 large moves in 30 periods
                anomalies.append('excessive_volatility')
        
        return {
            'is_manipulation': len(anomalies) > 0,
            'anomalies': anomalies,
            'manipulation_score': min(len(anomalies) / 3.0, 1.0),
            'analysis_period': len(price_data)
        }


# Performance Optimization
class PerformanceOptimizer:
    """System performance optimization"""
    
    def __init__(self):
        self.metrics = {
            'response_times': [],
            'cache_hit_rates': {},
            'api_call_efficiency': {},
            'memory_usage': []
        }
    
    def record_response_time(self, operation: str, duration: float) -> None:
        """Response vaqtni qayd etish"""
        if operation not in self.metrics['response_times']:
            self.metrics['response_times'][operation] = []
        
        self.metrics['response_times'][operation].append(duration)
        
        # Keep only last 100 measurements
        if len(self.metrics['response_times'][operation]) > 100:
            self.metrics['response_times'][operation] = self.metrics['response_times'][operation][-100:]
    
    def calculate_cache_efficiency(self) -> Dict[str, float]:
        """Cache samaradorligini hisoblash"""
        efficiency = {}
        for cache_type, hits in self.metrics['cache_hit_rates'].items():
            if hits.get('total', 0) > 0:
                efficiency[cache_type] = hits.get('hits', 0) / hits['total']
            else:
                efficiency[cache_type] = 0.0
        
        return efficiency
    
    def get_optimization_recommendations(self) -> List[str]:
        """Optimizatsiya tavsiyalarini olish"""
        recommendations = []
        
        # Response time recommendations
        for operation, times in self.metrics['response_times'].items():
            if times:
                avg_time = np.mean(times)
                if avg_time > 1.0:  # More than 1 second
                    recommendations.append(f"Optimize {operation}: average response time {avg_time:.2f}s is high")
        
        # Cache recommendations
        cache_eff = self.calculate_cache_efficiency()
        for cache_type, efficiency in cache_eff.items():
            if efficiency < 0.7:  # Less than 70% hit rate
                recommendations.append(f"Improve {cache_type} cache: hit rate is {efficiency:.2%}")
        
        return recommendations


if __name__ == "__main__":
    # Original demo
    asyncio.run(demo_data_integration())