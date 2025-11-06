"""
Data Utilities
=============

Data processing and validation utilities
"""

import time
import json
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import statistics

@dataclass
class TimeSeriesData:
    """Time series data structure"""
    timestamp: float
    value: float
    metadata: Optional[Dict[str, Any]] = None

class DataValidator:
    """Data validation utility"""
    
    @staticmethod
    def validate_price_data(price: float, symbol: str) -> bool:
        """Validate price data"""
        if not isinstance(price, (int, float)) or price <= 0:
            return False
        
        # Symbol-specific validation
        if '/' in symbol:  # Forex pairs
            return price > 0 and price < 1000  # Reasonable range
        elif symbol.startswith('XAU'):  # Gold
            return price > 0 and price < 10000
        elif symbol.startswith('XAG'):  # Silver
            return price > 0 and price < 1000
        elif symbol in ['BTC/USD', 'ETH/USD']:  # Crypto
            return price > 0 and price < 1000000
        else:  # Stocks
            return price > 0 and price < 10000
    
    @staticmethod
    def validate_volume_data(volume: Union[int, float]) -> bool:
        """Validate volume data"""
        return isinstance(volume, (int, float)) and volume >= 0
    
    @staticmethod
    def validate_timestamp(timestamp: Union[float, int]) -> bool:
        """Validate timestamp"""
        if not isinstance(timestamp, (float, int)):
            return False
        
        # Check if timestamp is reasonable (not too far in past or future)
        current_time = time.time()
        one_year_ago = current_time - 365 * 24 * 3600
        one_year_future = current_time + 365 * 24 * 3600
        
        return one_year_ago <= timestamp <= one_year_future
    
    @staticmethod
    def validate_market_data(data: Dict[str, Any], symbol: str) -> bool:
        """Validate complete market data"""
        required_fields = ['timestamp', 'bid', 'ask', 'last', 'volume']
        
        for field in required_fields:
            if field not in data:
                return False
        
        # Validate individual fields
        if not DataValidator.validate_timestamp(data['timestamp']):
            return False
        
        if not DataValidator.validate_price_data(data['bid'], symbol):
            return False
        
        if not DataValidator.validate_price_data(data['ask'], symbol):
            return False
        
        if not DataValidator.validate_price_data(data['last'], symbol):
            return False
        
        if not DataValidator.validate_volume_data(data['volume']):
            return False
        
        # Check bid-ask spread reasonableness
        if data['bid'] >= data['ask']:
            return False
        
        spread_pct = (data['ask'] - data['bid']) / data['last']
        if spread_pct > 0.1:  # 10% spread is too wide
            return False
        
        return True

class MarketDataProcessor:
    """Market data processing utility"""
    
    def __init__(self):
        self.price_history: Dict[str, List[TimeSeriesData]] = {}
        self.volume_history: Dict[str, List[TimeSeriesData]] = {}
    
    def add_price_data(self, symbol: str, timestamp: float, price: float, 
                      metadata: Optional[Dict[str, Any]] = None):
        """Add price data point"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        data_point = TimeSeriesData(timestamp, price, metadata)
        self.price_history[symbol].append(data_point)
        
        # Keep only recent data (e.g., last 1000 points)
        if len(self.price_history[symbol]) > 1000:
            self.price_history[symbol] = self.price_history[symbol][-500:]
    
    def add_volume_data(self, symbol: str, timestamp: float, volume: float,
                       metadata: Optional[Dict[str, Any]] = None):
        """Add volume data point"""
        if symbol not in self.volume_history:
            self.volume_history[symbol] = []
        
        data_point = TimeSeriesData(timestamp, volume, metadata)
        self.volume_history[symbol].append(data_point)
        
        # Keep only recent data
        if len(self.volume_history[symbol]) > 1000:
            self.volume_history[symbol] = self.volume_history[symbol][-500:]
    
    def get_price_statistics(self, symbol: str, window: Optional[int] = None) -> Dict[str, float]:
        """Get price statistics for symbol"""
        if symbol not in self.price_history:
            return {}
        
        data = self.price_history[symbol]
        if not data:
            return {}
        
        # Use window if specified
        if window and len(data) > window:
            data = data[-window:]
        
        prices = [d.value for d in data]
        
        if not prices:
            return {}
        
        return {
            'count': len(prices),
            'mean': statistics.mean(prices),
            'median': statistics.median(prices),
            'std_dev': statistics.stdev(prices) if len(prices) > 1 else 0.0,
            'min': min(prices),
            'max': max(prices),
            'latest': prices[-1],
            'change': prices[-1] - prices[0] if len(prices) > 1 else 0.0,
            'change_pct': ((prices[-1] - prices[0]) / prices[0] * 100) if len(prices) > 1 and prices[0] != 0 else 0.0
        }
    
    def get_volume_statistics(self, symbol: str, window: Optional[int] = None) -> Dict[str, float]:
        """Get volume statistics for symbol"""
        if symbol not in self.volume_history:
            return {}
        
        data = self.volume_history[symbol]
        if not data:
            return {}
        
        # Use window if specified
        if window and len(data) > window:
            data = data[-window:]
        
        volumes = [d.value for d in data]
        
        if not volumes:
            return {}
        
        return {
            'count': len(volumes),
            'total': sum(volumes),
            'mean': statistics.mean(volumes),
            'median': statistics.median(volumes),
            'std_dev': statistics.stdev(volumes) if len(volumes) > 1 else 0.0,
            'min': min(volumes),
            'max': max(volumes),
            'latest': volumes[-1]
        }
    
    def calculate_ohlc(self, symbol: str, timeframe: str = '1min') -> List[Dict[str, Any]]:
        """Calculate OHLC data"""
        if symbol not in self.price_history:
            return []
        
        data = self.price_history[symbol]
        if not data:
            return []
        
        # Group data by timeframe
        timeframe_seconds = {
            '1min': 60,
            '5min': 300,
            '15min': 900,
            '1hour': 3600,
            '1day': 86400
        }.get(timeframe, 60)
        
        buckets = {}
        
        for data_point in data:
            bucket_time = int(data_point.timestamp // timeframe_seconds) * timeframe_seconds
            
            if bucket_time not in buckets:
                buckets[bucket_time] = {
                    'timestamp': bucket_time,
                    'open': data_point.value,
                    'high': data_point.value,
                    'low': data_point.value,
                    'close': data_point.value,
                    'volume': 0
                }
            
            bucket = buckets[bucket_time]
            bucket['high'] = max(bucket['high'], data_point.value)
            bucket['low'] = min(bucket['low'], data_point.value)
            bucket['close'] = data_point.value
            
            # Add volume if available
            if data_point.metadata and 'volume' in data_point.metadata:
                bucket['volume'] += data_point.metadata['volume']
        
        # Convert to list and sort
        ohlc_bars = list(buckets.values())
        ohlc_bars.sort(key=lambda x: x['timestamp'])
        
        return ohlc_bars
    
    def detect_outliers(self, symbol: str, threshold: float = 2.0) -> List[TimeSeriesData]:
        """Detect outliers in price data"""
        if symbol not in self.price_history:
            return []
        
        data = self.price_history[symbol]
        if len(data) < 10:
            return []
        
        prices = [d.value for d in data]
        mean_price = statistics.mean(prices)
        std_dev = statistics.stdev(prices)
        
        outliers = []
        
        for data_point in data:
            z_score = abs(data_point.value - mean_price) / std_dev if std_dev > 0 else 0
            
            if z_score > threshold:
                outliers.append(data_point)
        
        return outliers
    
    def export_data(self, symbol: str, format: str = 'json') -> str:
        """Export data in specified format"""
        if symbol not in self.price_history:
            return ""
        
        data = {
            'symbol': symbol,
            'export_timestamp': time.time(),
            'price_data': [asdict(d) for d in self.price_history[symbol]],
            'volume_data': [asdict(d) for d in self.volume_history.get(symbol, [])]
        }
        
        if format.lower() == 'json':
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")