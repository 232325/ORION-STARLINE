"""
Oracle Integration System for Precious Metals
Real-time price feeds and market data for NFT hedge fund
"""

import asyncio
import aiohttp
import websockets
import json
import time
import logging
from typing import Dict, List, Tuple, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from abc import ABC, abstractmethod
import hashlib
import hmac
from datetime import datetime, timedelta

class OracleProvider(Enum):
    CHAINLINK = "chainlink"
    TRADINGVIEW = "tradingview"
    BLOOMBERG = "bloomberg"
    REUTERS = "reuters"
    COINGECKO = "coingecko"
    METALS_API = "metals_api"

class DataQuality(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"

@dataclass
class MetalPrice:
    """Metal price data structure"""
    symbol: str  # XAU, XAG, XPT, XPD
    price: float
    currency: str = "USD"
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume: Optional[float] = None
    open_interest: Optional[float] = None
    implied_volatility: Optional[float] = None
    timestamp: float = field(default_factory=time.time)
    source: str = ""
    confidence: float = 1.0
    data_quality: DataQuality = DataQuality.GOOD
    
@dataclass
class MarketData:
    """Comprehensive market data structure"""
    metal_price: MetalPrice
    technical_indicators: Dict[str, float] = field(default_factory=dict)
    sentiment_score: float = 0.0
    news_sentiment: float = 0.0
    liquidity_score: float = 0.5
    volatility_regime: str = "normal"
    correlation_matrix: Dict[Tuple[str, str], float] = field(default_factory=dict)

@dataclass
class OracleConfig:
    """Configuration for oracle provider"""
    provider: OracleProvider
    api_key: str = ""
    endpoint: str = ""
    timeout: float = 10.0
    update_frequency: float = 1.0  # seconds
    max_retries: int = 3
    failover_enabled: bool = True
    weight: float = 1.0

class BaseOracle(ABC):
    """Abstract base class for oracle providers"""
    
    def __init__(self, config: OracleConfig):
        self.config = config
        self.logger = logging.getLogger(f"Oracle.{config.provider.value}")
        self.last_update = 0.0
        self.update_callbacks: List[Callable] = []
        self.error_count = 0
        self.success_count = 0
        
    @abstractmethod
    async def fetch_price(self, symbol: str) -> Optional[MetalPrice]:
        """Fetch metal price from oracle"""
        pass
    
    @abstractmethod
    async def fetch_market_data(self, symbol: str) -> Optional[MarketData]:
        """Fetch comprehensive market data"""
        pass
    
    async def is_healthy(self) -> bool:
        """Check if oracle is healthy and responsive"""
        try:
            test_price = await self.fetch_price("XAU")  # Test with gold
            return test_price is not None
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return False
    
    def add_update_callback(self, callback: Callable):
        """Add callback for price updates"""
        self.update_callbacks.append(callback)
    
    async def notify_update(self, metal_price: MetalPrice):
        """Notify all callbacks of price update"""
        for callback in self.update_callbacks:
            try:
                await callback(metal_price)
            except Exception as e:
                self.logger.error(f"Callback error: {str(e)}")

class ChainlinkOracle(BaseOracle):
    """Chainlink Oracle implementation"""
    
    def __init__(self, config: OracleConfig):
        super().__init__(config)
        self.price_feeds: Dict[str, str] = {}  # symbol to feed address mapping
        
    async def fetch_price(self, symbol: str) -> Optional[MetalPrice]:
        """Fetch price from Chainlink price feed"""
        try:
            # Simulate Chainlink price feed call
            # In production, would use web3 to call Chainlink contract
            
            base_price = self._get_base_price(symbol)
            if base_price is None:
                return None
            
            # Add realistic bid/ask spread
            spread = base_price * 0.0005  # 5 basis points spread
            bid = base_price - spread/2
            ask = base_price + spread/2
            
            # Add some price volatility simulation
            volatility = np.random.normal(0, 0.001)  # 0.1% volatility
            current_price = base_price * (1 + volatility)
            
            price = MetalPrice(
                symbol=symbol,
                price=current_price,
                bid=bid,
                ask=ask,
                volume=np.random.uniform(100000, 1000000),
                timestamp=time.time(),
                source=f"Chainlink_{symbol}",
                confidence=0.95,
                data_quality=DataQuality.EXCELLENT
            )
            
            self.success_count += 1
            return price
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Failed to fetch price for {symbol}: {str(e)}")
            return None
    
    async def fetch_market_data(self, symbol: str) -> Optional[MarketData]:
        """Fetch comprehensive market data from Chainlink"""
        metal_price = await self.fetch_price(symbol)
        
        if metal_price is None:
            return None
        
        # Generate technical indicators
        technical_indicators = self._calculate_technical_indicators(symbol)
        
        market_data = MarketData(
            metal_price=metal_price,
            technical_indicators=technical_indicators,
            sentiment_score=np.random.uniform(-1, 1),
            news_sentiment=np.random.uniform(-1, 1),
            liquidity_score=np.random.uniform(0.3, 0.9),
            volatility_regime=self._determine_volatility_regime(symbol)
        )
        
        return market_data
    
    def _get_base_price(self, symbol: str) -> Optional[float]:
        """Get base price for symbol"""
        base_prices = {
            "XAU": 2000.0,    # Gold
            "XAG": 25.0,      # Silver
            "XPT": 1000.0,    # Platinum
            "XPD": 2000.0     # Palladium
        }
        return base_prices.get(symbol)
    
    def _calculate_technical_indicators(self, symbol: str) -> Dict[str, float]:
        """Calculate technical indicators"""
        # Simplified technical indicators
        return {
            "rsi": np.random.uniform(30, 70),
            "macd": np.random.uniform(-5, 5),
            "bollinger_position": np.random.uniform(0, 1),
            "volume_sma_ratio": np.random.uniform(0.5, 2.0),
            "price_momentum": np.random.uniform(-0.05, 0.05)
        }
    
    def _determine_volatility_regime(self, symbol: str) -> str:
        """Determine current volatility regime"""
        regimes = ["low", "normal", "high", "extreme"]
        weights = [0.2, 0.5, 0.25, 0.05]
        return np.random.choice(regimes, p=weights)

class TradingViewOracle(BaseOracle):
    """TradingView Oracle implementation"""
    
    def __init__(self, config: OracleConfig):
        super().__init__(config)
        self.ws_connection = None
        
    async def fetch_price(self, symbol: str) -> Optional[MetalPrice]:
        """Fetch price from TradingView"""
        try:
            # Simulate TradingView API call
            # In production, would use TradingView WebSocket or REST API
            
            base_price = self._get_base_price(symbol)
            if base_price is None:
                return None
            
            # Simulate real-time price updates
            timestamp = time.time()
            price_change = np.random.normal(0, 0.002)  # 0.2% price change
            
            current_price = base_price * (1 + price_change)
            
            price = MetalPrice(
                symbol=symbol,
                price=current_price,
                bid=current_price * 0.9998,
                ask=current_price * 1.0002,
                volume=np.random.uniform(500000, 2000000),
                open_interest=np.random.uniform(100000, 500000),
                implied_volatility=np.random.uniform(0.15, 0.35),
                timestamp=timestamp,
                source=f"TradingView_{symbol}",
                confidence=0.90,
                data_quality=DataQuality.GOOD
            )
            
            self.success_count += 1
            return price
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"TradingView fetch failed for {symbol}: {str(e)}")
            return None
    
    async def fetch_market_data(self, symbol: str) -> Optional[MarketData]:
        """Fetch comprehensive market data from TradingView"""
        metal_price = await self.fetch_price(symbol)
        
        if metal_price is None:
            return None
        
        # Enhanced technical indicators from TradingView
        technical_indicators = {
            "rsi": np.random.uniform(25, 75),
            "stochastic_k": np.random.uniform(0, 100),
            "stochastic_d": np.random.uniform(0, 100),
            "williams_r": np.random.uniform(-100, 0),
            "cci": np.random.uniform(-200, 200),
            "atr": np.random.uniform(0.01, 0.05),
            "volume_profile": np.random.uniform(0.5, 1.5)
        }
        
        market_data = MarketData(
            metal_price=metal_price,
            technical_indicators=technical_indicators,
            sentiment_score=np.random.uniform(-0.5, 0.5),
            news_sentiment=np.random.uniform(-0.3, 0.3),
            liquidity_score=np.random.uniform(0.4, 0.8),
            volatility_regime=np.random.choice(["low", "normal", "high"])
        )
        
        return market_data
    
    def _get_base_price(self, symbol: str) -> Optional[float]:
        """Get base price for symbol"""
        # Same as Chainlink for simulation
        base_prices = {
            "XAU": 2000.0,
            "XAG": 25.0,
            "XPT": 1000.0,
            "XPD": 2000.0
        }
        return base_prices.get(symbol)

class BloombergOracle(BaseOracle):
    """Bloomberg Oracle implementation"""
    
    def __init__(self, config: OracleConfig):
        super().__init__(config)
        self.api_session = None
        
    async def fetch_price(self, symbol: str) -> Optional[MetalPrice]:
        """Fetch price from Bloomberg API"""
        try:
            # Simulate Bloomberg API call
            # In production, would use Bloomberg Terminal API or B-PIPE
            
            base_price = self._get_base_price(symbol)
            if base_price is None:
                return None
            
            # Bloomberg-style high precision pricing
            timestamp = time.time()
            
            # Simulate microstructure effects
            micro_price_move = np.random.normal(0, 0.0001)  # 1 basis point
            current_price = base_price * (1 + micro_price_move)
            
            price = MetalPrice(
                symbol=symbol,
                price=current_price,
                bid=current_price * 0.9999,
                ask=current_price * 1.0001,
                volume=np.random.uniform(2000000, 10000000),
                open_interest=np.random.uniform(500000, 2000000),
                implied_volatility=np.random.uniform(0.10, 0.40),
                timestamp=timestamp,
                source=f"Bloomberg_{symbol}",
                confidence=0.98,
                data_quality=DataQuality.EXCELLENT
            )
            
            self.success_count += 1
            return price
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Bloomberg fetch failed for {symbol}: {str(e)}")
            return None
    
    async def fetch_market_data(self, symbol: str) -> Optional[MarketData]:
        """Fetch comprehensive market data from Bloomberg"""
        metal_price = await self.fetch_price(symbol)
        
        if metal_price is None:
            return None
        
        # Bloomberg-style comprehensive market data
        technical_indicators = {
            "rsi": np.random.uniform(20, 80),
            "macd_signal": np.random.uniform(-10, 10),
            "fibonacci_retracement": np.random.uniform(0.236, 0.786),
            "ichimoku_tenkan": np.random.uniform(-20, 20),
            "ichimoku_kijun": np.random.uniform(-20, 20),
            "vwap_deviation": np.random.uniform(-0.02, 0.02),
            "order_flow": np.random.uniform(-100, 100)
        }
        
        market_data = MarketData(
            metal_price=metal_price,
            technical_indicators=technical_indicators,
            sentiment_score=np.random.uniform(-0.8, 0.8),
            news_sentiment=np.random.uniform(-0.6, 0.6),
            liquidity_score=np.random.uniform(0.6, 0.95),
            volatility_regime=np.random.choice(["low", "normal", "high", "stress"])
        )
        
        return market_data
    
    def _get_base_price(self, symbol: str) -> Optional[float]:
        """Get base price for symbol"""
        # Bloomberg-style base prices
        base_prices = {
            "XAU": 2000.0,
            "XAG": 25.0,
            "XPT": 1000.0,
            "XPD": 2000.0
        }
        return base_prices.get(symbol)

class OracleAggregator:
    """Aggregates data from multiple oracle providers"""
    
    def __init__(self):
        self.oracles: Dict[OracleProvider, BaseOracle] = {}
        self.data_cache: Dict[str, MetalPrice] = {}
        self.market_data_cache: Dict[str, MarketData] = {}
        self.update_interval = 1.0  # seconds
        self.last_update = 0.0
        self.logger = logging.getLogger("OracleAggregator")
        
    def add_oracle(self, oracle: BaseOracle):
        """Add oracle provider"""
        self.oracles[oracle.config.provider] = oracle
        self.logger.info(f"Added oracle: {oracle.config.provider.value}")
    
    async def fetch_aggregated_price(self, symbol: str) -> Optional[MetalPrice]:
        """Fetch and aggregate price from multiple oracles"""
        
        valid_prices = []
        
        # Fetch from all healthy oracles
        for provider, oracle in self.oracles.items():
            try:
                if await oracle.is_healthy():
                    price = await oracle.fetch_price(symbol)
                    if price and price.data_quality != DataQuality.INVALID:
                        # Weight by oracle confidence and quality
                        weight = self._calculate_price_weight(price, oracle.config.weight)
                        price.confidence = weight
                        valid_prices.append((price, weight))
                else:
                    self.logger.warning(f"Oracle {provider.value} is unhealthy")
            except Exception as e:
                self.logger.error(f"Error fetching from {provider.value}: {str(e)}")
        
        if not valid_prices:
            self.logger.error(f"No valid prices found for {symbol}")
            return None
        
        # Aggregate prices using weighted average
        total_weight = sum(weight for _, weight in valid_prices)
        if total_weight == 0:
            return None
        
        aggregated_price = self._calculate_weighted_average(valid_prices)
        
        # Cache the result
        self.data_cache[symbol] = aggregated_price
        self.last_update = time.time()
        
        return aggregated_price
    
    async def fetch_aggregated_market_data(self, symbol: str) -> Optional[MarketData]:
        """Fetch and aggregate comprehensive market data"""
        
        valid_data = []
        
        for provider, oracle in self.oracles.items():
            try:
                if await oracle.is_healthy():
                    data = await oracle.fetch_market_data(symbol)
                    if data and data.metal_price.data_quality != DataQuality.INVALID:
                        weight = self._calculate_data_weight(data, oracle.config.weight)
                        valid_data.append((data, weight))
            except Exception as e:
                self.logger.error(f"Error fetching market data from {provider.value}: {str(e)}")
        
        if not valid_data:
            return None
        
        # Aggregate market data
        aggregated_data = self._aggregate_market_data(valid_data)
        
        # Cache the result
        self.market_data_cache[symbol] = aggregated_data
        
        return aggregated_data
    
    def _calculate_price_weight(self, price: MetalPrice, base_weight: float) -> float:
        """Calculate weight for price based on data quality and confidence"""
        
        # Quality multiplier
        quality_multiplier = {
            DataQuality.EXCELLENT: 1.0,
            DataQuality.GOOD: 0.8,
            DataQuality.FAIR: 0.6,
            DataQuality.POOR: 0.3,
            DataQuality.INVALID: 0.0
        }
        
        quality_score = quality_multiplier.get(price.data_quality, 0.5)
        
        # Recency penalty (price should be recent)
        age_minutes = (time.time() - price.timestamp) / 60
        if age_minutes > 60:  # Older than 1 hour
            recency_score = max(0.1, 1.0 - (age_minutes - 60) / 240)  # Linear decay
        else:
            recency_score = 1.0
        
        # Overall weight
        weight = base_weight * price.confidence * quality_score * recency_score
        
        return max(0.0, weight)
    
    def _calculate_data_weight(self, data: MarketData, base_weight: float) -> float:
        """Calculate weight for market data"""
        
        # Weight based on metal price quality
        price_weight = self._calculate_price_weight(data.metal_price, 1.0)
        
        # Additional factors
        liquidity_score = data.liquidity_score
        sentiment_weight = (data.sentiment_score + 1) / 2  # Normalize to 0-1
        
        # Overall data weight
        weight = base_weight * price_weight * liquidity_score * sentiment_weight
        
        return max(0.0, weight)
    
    def _calculate_weighted_average(self, prices: List[Tuple[MetalPrice, float]]) -> MetalPrice:
        """Calculate weighted average of prices"""
        
        total_weight = sum(weight for _, weight in prices)
        
        if total_weight == 0:
            return prices[0][0]  # Fallback to first price
        
        # Calculate weighted averages
        weighted_price = sum(price.price * weight for price, weight in prices) / total_weight
        weighted_bid = sum((price.bid or price.price) * weight for price, weight in prices) / total_weight
        weighted_ask = sum((price.ask or price.price) * weight for price, weight in prices) / total_weight
        weighted_volume = sum((price.volume or 0) * weight for price, weight in prices) / total_weight
        
        # Determine overall data quality
        avg_confidence = sum(price.confidence * weight for price, weight in prices) / total_weight
        
        if avg_confidence >= 0.9:
            data_quality = DataQuality.EXCELLENT
        elif avg_confidence >= 0.7:
            data_quality = DataQuality.GOOD
        elif avg_confidence >= 0.5:
            data_quality = DataQuality.FAIR
        else:
            data_quality = DataQuality.POOR
        
        # Create aggregated price
        aggregated_price = MetalPrice(
            symbol=prices[0][0].symbol,
            price=weighted_price,
            bid=weighted_bid,
            ask=weighted_ask,
            volume=weighted_volume,
            timestamp=time.time(),
            source="aggregated",
            confidence=avg_confidence,
            data_quality=data_quality
        )
        
        return aggregated_price
    
    def _aggregate_market_data(self, data_list: List[Tuple[MarketData, float]]) -> MarketData:
        """Aggregate market data from multiple sources"""
        
        total_weight = sum(weight for _, weight in data_list)
        
        if total_weight == 0:
            return data_list[0][0]  # Fallback
        
        # Aggregate technical indicators
        all_indicators = {}
        for data, weight in data_list:
            for indicator, value in data.technical_indicators.items():
                if indicator not in all_indicators:
                    all_indicators[indicator] = []
                all_indicators[indicator].append((value, weight))
        
        aggregated_indicators = {}
        for indicator, values_weights in all_indicators.items():
            total_w = sum(w for _, w in values_weights)
            if total_w > 0:
                avg_value = sum(v * w for v, w in values_weights) / total_w
                aggregated_indicators[indicator] = avg_value
        
        # Aggregate other metrics
        avg_sentiment = sum(data.sentiment_score * weight for data, weight in data_list) / total_weight
        avg_news_sentiment = sum(data.news_sentiment * weight for data, weight in data_list) / total_weight
        avg_liquidity = sum(data.liquidity_score * weight for data, weight in data_list) / total_weight
        
        # Get the best metal price
        best_data = max(data_list, key=lambda x: x[0].metal_price.confidence)
        
        # Determine volatility regime (most common)
        regimes = [data.volatility_regime for data, _ in data_list]
        volatility_regime = max(set(regimes), key=regimes.count)
        
        return MarketData(
            metal_price=best_data[0].metal_price,
            technical_indicators=aggregated_indicators,
            sentiment_score=avg_sentiment,
            news_sentiment=avg_news_sentiment,
            liquidity_score=avg_liquidity,
            volatility_regime=volatility_regime
        )
    
    async def start_real_time_updates(self, symbols: List[str]):
        """Start real-time price updates"""
        
        async def update_loop():
            while True:
                try:
                    for symbol in symbols:
                        # Fetch aggregated price and market data
                        price = await self.fetch_aggregated_price(symbol)
                        market_data = await self.fetch_aggregated_market_data(symbol)
                        
                        if price:
                            # Notify all oracles of update
                            for oracle in self.oracles.values():
                                await oracle.notify_update(price)
                    
                    await asyncio.sleep(self.update_interval)
                    
                except Exception as e:
                    self.logger.error(f"Update loop error: {str(e)}")
                    await asyncio.sleep(5)  # Wait before retry
        
        # Start update loop
        asyncio.create_task(update_loop())
        self.logger.info("Started real-time price updates")
    
    def get_current_price(self, symbol: str) -> Optional[MetalPrice]:
        """Get cached current price for symbol"""
        return self.data_cache.get(symbol)
    
    def get_current_market_data(self, symbol: str) -> Optional[MarketData]:
        """Get cached current market data for symbol"""
        return self.market_data_cache.get(symbol)
    
    def get_oracle_status(self) -> Dict[str, Dict]:
        """Get status of all oracles"""
        status = {}
        
        for provider, oracle in self.oracles.items():
            status[provider.value] = {
                "healthy": asyncio.create_task(oracle.is_healthy()),
                "success_count": oracle.success_count,
                "error_count": oracle.error_count,
                "last_update": oracle.last_update
            }
        
        return status

class OracleSecurity:
    """Security features for oracle integration"""
    
    @staticmethod
    def verify_data_integrity(price: MetalPrice, expected_hash: str) -> bool:
        """Verify data integrity using hash"""
        data_string = f"{price.symbol}{price.price}{price.timestamp}"
        actual_hash = hashlib.sha256(data_string.encode()).hexdigest()
        return actual_hash == expected_hash
    
    @staticmethod
    def sign_request(api_key: str, secret: str, data: str) -> str:
        """Sign API request"""
        return hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
    
    @staticmethod
    def detect_anomalies(price_history: List[MetalPrice], current_price: MetalPrice) -> bool:
        """Detect price anomalies"""
        if len(price_history) < 2:
            return False
        
        # Calculate recent price changes
        recent_prices = [p.price for p in price_history[-10:]]  # Last 10 prices
        
        if len(recent_prices) > 1:
            # Simple anomaly detection based on standard deviation
            mean_price = np.mean(recent_prices)
            std_price = np.std(recent_prices)
            
            if std_price > 0:
                z_score = abs(current_price.price - mean_price) / std_price
                return z_score > 3.0  # More than 3 standard deviations
        
        return False


# Example usage
async def main():
    """Example usage of the oracle system"""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize oracle aggregator
    aggregator = OracleAggregator()
    
    # Setup oracle configurations
    chainlink_config = OracleConfig(
        provider=OracleProvider.CHAINLINK,
        api_key="chainlink_key",
        weight=1.0,
        update_frequency=1.0
    )
    
    tradingview_config = OracleConfig(
        provider=OracleProvider.TRADINGVIEW,
        api_key="tradingview_key",
        weight=0.8,
        update_frequency=2.0
    )
    
    bloomberg_config = OracleConfig(
        provider=OracleProvider.BLOOMBERG,
        api_key="bloomberg_key",
        weight=1.2,
        update_frequency=0.5
    )
    
    # Initialize oracles
    chainlink_oracle = ChainlinkOracle(chainlink_config)
    tradingview_oracle = TradingViewOracle(tradingview_config)
    bloomberg_oracle = BloombergOracle(bloomberg_config)
    
    # Add oracles to aggregator
    aggregator.add_oracle(chainlink_oracle)
    aggregator.add_oracle(tradingview_oracle)
    aggregator.add_oracle(bloomberg_oracle)
    
    # Test symbols
    symbols = ["XAU", "XAG", "XPT", "XPD"]
    
    # Fetch prices
    print("Fetching aggregated metal prices...")
    for symbol in symbols:
        price = await aggregator.fetch_aggregated_price(symbol)
        if price:
            print(f"{symbol}: ${price.price:.2f} (Quality: {price.data_quality.value}, Confidence: {price.confidence:.2f})")
        else:
            print(f"{symbol}: Failed to fetch price")
    
    print("\nFetching aggregated market data...")
    for symbol in symbols:
        market_data = await aggregator.fetch_aggregated_market_data(symbol)
        if market_data:
            print(f"{symbol} Market Data:")
            print(f"  Sentiment: {market_data.sentiment_score:.2f}")
            print(f"  Liquidity: {market_data.liquidity_score:.2f}")
            print(f"  Volatility Regime: {market_data.volatility_regime}")
            print(f"  RSI: {market_data.technical_indicators.get('rsi', 'N/A'):.1f}")
        else:
            print(f"{symbol}: Failed to fetch market data")
    
    # Get oracle status
    print("\nOracle Status:")
    status = aggregator.get_oracle_status()
    for provider, info in status.items():
        print(f"{provider}: Healthy={info['healthy']}, Success={info['success_count']}, Errors={info['error_count']}")
    
    # Start real-time updates
    print("\nStarting real-time updates...")
    await aggregator.start_real_time_updates(symbols)
    
    # Keep running for a while
    await asyncio.sleep(10)
    
    print("Oracle system demo completed!")

if __name__ == "__main__":
    asyncio.run(main())