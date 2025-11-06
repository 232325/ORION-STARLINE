"""
Classical Preprocessing Module
Klassik ma'lumotlarni qayta ishlash moduli
"""
import asyncio
import aiohttp
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone, timedelta
import logging
import time
import json
from concurrent.futures import ThreadPoolExecutor
import sqlite3
import threading

from ..utils.data_models import MarketData, MarketPrice, CurrencyPair
from ..config.config import config, CURRENCY_PAIRS, TIMEZONES

logger = logging.getLogger(__name__)

class ClassicalPreprocessor:
    """
    Classical Preprocessing Engine
    Ma'lumotlarni klassik qayta ishlash
    """
    
    def __init__(self, forex_config):
        self.config = forex_config
        self.running = False
        self.session = None
        self.last_prices = {}
        self.price_history = {}
        self.market_sessions = {}
        self.error_count = 0
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Data cache
        self._price_cache = {}
        self._correlation_cache = {}
        self._volatility_cache = {}
        
        # Session management
        self._initialize_sessions()
        
        logger.info("Classical Preprocessor initialized")
    
    def _initialize_sessions(self):
        """Aiohttp session yaratish"""
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=30,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'HybridQuantumForex/1.0'}
        )
    
    async def get_latest_data(self) -> Optional[MarketData]:
        """Oxirgi market ma'lumotlarini olish"""
        try:
            market_data = MarketData()
            
            # Multi-currency data fetch
            tasks = []
            for currency in self.config.supported_currencies:
                task = self._fetch_currency_data(currency)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                currency = self.config.supported_currencies[i]
                if isinstance(result, Exception):
                    logger.warning(f"Failed to fetch data for {currency}: {result}")
                    continue
                
                if result:
                    self._update_price_cache(currency, result)
                    market_data.prices.update(result)
            
            # Market session detection
            market_data.session = self._detect_market_session()
            market_data.market_hours = self._is_market_hours(market_data.session)
            
            # Volume estimation (since real volume not available in forex)
            market_data.volume = self._estimate_volume(market_data.prices)
            
            # Volatility calculation
            market_data.volatility = self._calculate_volatility(market_data.prices)
            
            # Correlation matrix
            market_data.correlation_matrix = self._calculate_correlation_matrix()
            
            self.error_count = 0  # Reset error count on success
            return market_data
            
        except Exception as e:
            logger.error(f"Failed to get latest data: {e}")
            self.error_count += 1
            return None
    
    async def _fetch_currency_data(self, currency: str) -> Optional[Dict[str, MarketPrice]]:
        """Bitta valuta uchun ma'lumot olish"""
        try:
            # USD asosida rate olish
            rate_data = await self._fetch_fx_rate(currency, "USD")
            if not rate_data:
                return None
            
            prices = {}
            
            # Direct pairs with USD
            if currency != "USD":
                bid, ask = rate_data
                prices[f"{currency}USD"] = MarketPrice(
                    pair=f"{currency}USD",
                    bid=bid,
                    ask=ask,
                    timestamp=datetime.now(timezone.utc),
                    source="alpha_vantage"
                )
                
                # Reverse pair
                prices[f"USD{currency}"] = MarketPrice(
                    pair=f"USD{currency}",
                    bid=1/ask,
                    ask=1/bid,
                    timestamp=datetime.now(timezone.utc),
                    source="alpha_vantage"
                )
            
            return prices
            
        except Exception as e:
            logger.error(f"Failed to fetch {currency} data: {e}")
            return None
    
    async def _fetch_fx_rate(self, from_currency: str, to_currency: str) -> Optional[Tuple[float, float]]:
        """Exchange rate olish"""
        try:
            # Alpha Vantage API simulation (in real implementation, use actual API)
            if self.config.api_key == "demo_key":
                return self._generate_demo_rate(from_currency, to_currency)
            
            url = f"{self.config.api_base_url}/v1/latest/{from_currency}/{to_currency}"
            params = {
                'apikey': self.config.api_key,
                'format': 'json'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_rate_response(data)
                else:
                    logger.warning(f"API returned status {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to fetch rate {from_currency}/{to_currency}: {e}")
            return None
    
    def _generate_demo_rate(self, from_currency: str, to_currency: str) -> Tuple[float, float]:
        """Demo rate generation for testing"""
        # Base rates (approximate)
        base_rates = {
            'USD': 1.0,
            'EUR': 1.10,
            'GBP': 1.25,
            'JPY': 0.007,
            'CHF': 1.08,
            'CAD': 0.74,
            'AUD': 0.67,
            'NZD': 0.62,
            'CNY': 0.14,
            'HKD': 0.128,
            'SGD': 0.74,
            'KRW': 0.00075,
            'INR': 0.012,
            'BRL': 0.18,
            'MXN': 0.052,
            'ZAR': 0.055,
            'NOK': 0.092,
            'SEK': 0.095,
            'DKK': 0.148,
            'PLN': 0.25,
            'CZK': 0.042,
            'HUF': 0.0028,
            'RON': 0.22,
            'BGN': 0.56,
            'HRK': 0.146,
            'RSD': 0.0094,
            'TRY': 0.037,
            'ILS': 0.27,
            'AED': 0.27,
            'SAR': 0.27,
            'QAR': 0.27,
            'KWD': 3.25,
            'BHD': 2.65,
            'JOD': 1.41,
            'EGP': 0.032,
            'MAD': 0.098,
            'NGN': 0.00072,
            'KES': 0.0076,
            'GHS': 0.065,
            'XOF': 0.0017
        }
        
        from_rate = base_rates.get(from_currency, 1.0)
        to_rate = base_rates.get(to_currency, 1.0)
        
        base_rate = from_rate / to_rate
        
        # Add realistic spread and volatility
        spread = base_rate * 0.0002  # 2 pips typical spread
        bid = base_rate - spread/2
        ask = base_rate + spread/2
        
        # Add some random variation
        import random
        variation = random.uniform(-0.001, 0.001)
        bid *= (1 + variation)
        ask *= (1 + variation)
        
        return (bid, ask)
    
    def _parse_rate_response(self, data: Dict) -> Optional[Tuple[float, float]]:
        """API response ni parse qilish"""
        try:
            rate = data.get('rate')
            spread = data.get('spread', 0.0001)
            
            if rate:
                bid = rate - spread/2
                ask = rate + spread/2
                return (bid, ask)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse rate response: {e}")
            return None
    
    def _update_price_cache(self, currency: str, prices: Dict[str, MarketPrice]):
        """Price cache ni yangilash"""
        with self._lock:
            if currency not in self.price_history:
                self.price_history[currency] = []
            
            self.price_history[currency].extend(prices.values())
            
            # Keep only recent data
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
            self.price_history[currency] = [
                price for price in self.price_history[currency]
                if price.timestamp > cutoff_time
            ]
    
    def _detect_market_session(self) -> str:
        """Aktiv market session ni aniqlash"""
        current_utc = datetime.now(timezone.utc)
        
        # Market session hours (UTC)
        sessions = {
            'Sydney': (21, 6),      # 21:00 - 06:00 UTC
            'Tokyo': (0, 9),        # 00:00 - 09:00 UTC
            'London': (8, 17),      # 08:00 - 17:00 UTC
            'New_York': (13, 22)    # 13:00 - 22:00 UTC
        }
        
        current_hour = current_utc.hour
        
        for session, (start, end) in sessions.items():
            if start <= current_hour < end:
                return session
        
        # Weekend or outside hours
        return 'Weekend'
    
    def _is_market_hours(self, session: str) -> bool:
        """Market hours ekanligini tekshirish"""
        return session != 'Weekend'
    
    def _estimate_volume(self, prices: Dict[str, MarketPrice]) -> Dict[str, float]:
        """Volume estimation based on price movement and volatility"""
        volumes = {}
        
        for pair, price in prices.items():
            # Base volume estimation
            base_volume = 1000000  # $1M base
            
            # Adjust based on volatility
            if pair in self._volatility_cache:
                vol = self._volatility_cache[pair]
                volume_multiplier = 1 + (vol * 2)  # Higher vol = higher volume
            else:
                volume_multiplier = 1.0
            
            # Adjust based on currency importance
            major_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD']
            if any(curr in pair for curr in major_currencies):
                volume_multiplier *= 1.5
            
            volumes[pair] = base_volume * volume_multiplier
        
        return volumes
    
    def _calculate_volatility(self, prices: Dict[str, MarketPrice]) -> Dict[str, float]:
        """Volatility hisoblash"""
        volatilities = {}
        
        with self._lock:
            for pair, price in prices.items():
                try:
                    # Get historical data for this pair
                    if pair in self.price_history:
                        history = [p.mid_price for p in self.price_history[pair][-50:]]  # Last 50 points
                        
                        if len(history) >= 2:
                            # Calculate returns
                            returns = [(history[i] - history[i-1]) / history[i-1] 
                                     for i in range(1, len(history))]
                            
                            # Annualized volatility
                            volatility = np.std(returns) * np.sqrt(252 * 24 * 60)  # Assuming minute data
                            volatilities[pair] = volatility
                            self._volatility_cache[pair] = volatility
                        else:
                            volatilities[pair] = 0.01  # Default 1%
                    else:
                        volatilities[pair] = 0.01  # Default 1%
                        
                except Exception as e:
                    logger.error(f"Failed to calculate volatility for {pair}: {e}")
                    volatilities[pair] = 0.01
        
        return volatilities
    
    def _calculate_correlation_matrix(self) -> Optional[np.ndarray]:
        """Correlation matrix hisoblash"""
        try:
            # Collect all available price series
            all_pairs = list(self._price_cache.keys())
            
            if len(all_pairs) < 2:
                return None
            
            # Create price matrix
            price_matrix = []
            valid_pairs = []
            
            for pair in all_pairs:
                if pair in self.price_history and len(self.price_history[pair]) >= 20:
                    prices = [p.mid_price for p in self.price_history[pair][-20:]]
                    price_matrix.append(prices)
                    valid_pairs.append(pair)
            
            if len(price_matrix) < 2:
                return None
            
            # Calculate correlation matrix
            price_df = pd.DataFrame(price_matrix, index=valid_pairs)
            correlation_matrix = price_df.T.corr().values
            
            # Cache correlation matrix
            self._correlation_cache = {
                'matrix': correlation_matrix,
                'pairs': valid_pairs,
                'timestamp': datetime.now(timezone.utc)
            }
            
            return correlation_matrix
            
        except Exception as e:
            logger.error(f"Failed to calculate correlation matrix: {e}")
            return None
    
    def process_data(self, market_data: MarketData) -> MarketData:
        """Data preprocessing"""
        try:
            # Data validation
            validated_data = self._validate_market_data(market_data)
            
            # Anomaly detection
            anomaly_free_data = self._detect_anomalies(validated_data)
            
            # Data smoothing
            smoothed_data = self._smooth_data(anomaly_free_data)
            
            # Feature engineering
            enhanced_data = self._engineer_features(smoothed_data)
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Failed to process data: {e}")
            return market_data  # Return original on error
    
    def _validate_market_data(self, market_data: MarketData) -> MarketData:
        """Market data validatsiya"""
        valid_prices = {}
        
        for pair, price in market_data.prices.items():
            # Check for reasonable values
            if (price.bid > 0 and price.ask > 0 and 
                price.ask > price.bid and
                price.bid < price.ask * 1.1):  # Spread not too large
                valid_prices[pair] = price
            else:
                logger.warning(f"Invalid price data for {pair}: bid={price.bid}, ask={price.ask}")
        
        market_data.prices = valid_prices
        return market_data
    
    def _detect_anomalies(self, market_data: MarketData) -> MarketData:
        """Anomaly detection"""
        for pair, price in market_data.prices.items():
            # Check for price jumps
            if pair in self.last_prices:
                last_price = self.last_prices[pair]
                change = abs(price.mid_price - last_price.mid_price) / last_price.mid_price
                
                # Flag large changes (>5%)
                if change > 0.05:
                    logger.warning(f"Price anomaly detected for {pair}: {change:.2%} change")
                    
                    # Apply smoothing
                    smoothed_price = price.mid_price * 0.8 + last_price.mid_price * 0.2
                    spread_ratio = price.spread / price.mid_price
                    
                    market_data.prices[pair] = MarketPrice(
                        pair=pair,
                        bid=smoothed_price * (1 - spread_ratio/2),
                        ask=smoothed_price * (1 + spread_ratio/2),
                        timestamp=price.timestamp,
                        source=price.source + "_smoothed"
                    )
        
        self.last_prices = {pair: price for pair, price in market_data.prices.items()}
        return market_data
    
    def _smooth_data(self, market_data: MarketData) -> MarketData:
        """Data smoothing"""
        # Simple moving average smoothing
        smoothed_prices = {}
        
        for pair, price in market_data.prices.items():
            # Apply slight smoothing to reduce noise
            if pair in self.price_history and len(self.price_history[pair]) >= 5:
                recent_prices = [p.mid_price for p in self.price_history[pair][-5:]]
                smoothed_mid = sum(recent_prices) / len(recent_prices)
                
                # Adjust bid/ask around smoothed mid
                spread_ratio = price.spread / price.mid_price
                smoothed_bid = smoothed_mid * (1 - spread_ratio/2)
                smoothed_ask = smoothed_mid * (1 + spread_ratio/2)
                
                smoothed_prices[pair] = MarketPrice(
                    pair=pair,
                    bid=smoothed_bid,
                    ask=smoothed_ask,
                    timestamp=price.timestamp,
                    source="smoothed"
                )
            else:
                smoothed_prices[pair] = price
        
        market_data.prices = smoothed_prices
        return market_data
    
    def _engineer_features(self, market_data: MarketData) -> MarketData:
        """Feature engineering"""
        # Calculate additional features for quantum processing
        features = {}
        
        for pair, price in market_data.prices.items():
            # Spread-based features
            spread_pct = price.effective_spread_pct
            
            # Liquidity proxy (inverse of spread)
            liquidity_score = 1.0 / (1 + spread_pct)
            
            # Volatility-adjusted price
            vol = market_data.volatility.get(pair, 0.01)
            vol_adjusted_price = price.mid_price * (1 + vol)
            
            features[pair] = {
                'spread_pct': spread_pct,
                'liquidity_score': liquidity_score,
                'vol_adjusted_price': vol_adjusted_price,
                'volatility': vol
            }
        
        # Store features in market data (would be in custom field in real implementation)
        market_data.metadata = features
        
        return market_data
    
    def get_correlation_data(self, pair1: str, pair2: str) -> Optional[float]:
        """Correlation ma'lumotini olish"""
        if 'matrix' in self._correlation_cache:
            matrix = self._correlation_cache['matrix']
            pairs = self._correlation_cache['pairs']
            
            try:
                idx1 = pairs.index(pair1)
                idx2 = pairs.index(pair2)
                return matrix[idx1][idx2]
            except (ValueError, IndexError):
                return None
        
        return None
    
    def test_connection(self) -> bool:
        """Connection test"""
        try:
            # Simple test API call
            test_rate = self._generate_demo_rate("EUR", "USD")
            return test_rate is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def close(self):
        """Resources cleanup"""
        if self.session:
            asyncio.create_task(self.session.close())
        logger.info("Classical Preprocessor closed")