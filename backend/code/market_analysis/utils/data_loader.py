"""
Data Loader for Market Analysis
==============================

Ma'lumotlarni yuklash va qayta ishlash uchun yordamchi funksiyalar.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple, Any
from datetime import datetime, timedelta
import os
import json
from pathlib import Path


class DataTypes:
    """Ma'lumot turlari"""
    OHLCV = "ohlcv"
    TICK = "tick"
    ORDER_BOOK = "order_book"
    NEWS = "news"
    ECONOMIC = "economic"
    FUNDAMENTAL = "fundamental"


class DataLoader:
    """Ma'lumot yuklash sinfi"""
    
    def __init__(self, data_directory: str = "/workspace/data"):
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(exist_ok=True)
        
        # Supported data formats
        self.supported_formats = ['.csv', '.json', '.xlsx', '.parquet', '.pkl']
        
        # Data cache
        self._cache = {}
        self._cache_timeout = 300  # 5 minutes
    
    def load_symbol_data(self, symbol: str, timeframe: str = "H1", 
                        start_date: datetime = None, end_date: datetime = None,
                        data_type: str = DataTypes.OHLCV) -> pd.DataFrame:
        """Symbol ma'lumotlarini yuklash"""
        cache_key = f"{symbol}_{timeframe}_{start_date}_{end_date}_{data_type}"
        
        # Check cache
        if cache_key in self._cache:
            cache_time, cached_data = self._cache[cache_key]
            if (datetime.now() - cache_time).seconds < self._cache_timeout:
                return cached_data
        
        # Load data
        file_path = self._get_data_path(symbol, timeframe, data_type)
        
        if not file_path.exists():
            # Generate sample data if file doesn't exist
            print(f"Ma'lumot fayli topilmadi: {file_path}")
            data = self._generate_sample_data(symbol, timeframe, start_date, end_date)
        else:
            data = self._load_file(file_path, start_date, end_date)
        
        # Cache data
        self._cache[cache_key] = (datetime.now(), data)
        
        return data
    
    def _get_data_path(self, symbol: str, timeframe: str, data_type: str) -> Path:
        """Ma'lumot fayl yo'lini aniqlash"""
        # Try different extensions
        for ext in self.supported_formats:
            path = self.data_directory / f"{symbol}_{timeframe}_{data_type}{ext}"
            if path.exists():
                return path
        
        # Return default path (.csv)
        return self.data_directory / f"{symbol}_{timeframe}_{data_type}.csv"
    
    def _load_file(self, file_path: Path, start_date: datetime = None, 
                  end_date: datetime = None) -> pd.DataFrame:
        """Faylni yuklash"""
        try:
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            elif file_path.suffix.lower() == '.json':
                df = pd.read_json(file_path)
            elif file_path.suffix.lower() == '.xlsx':
                df = pd.read_excel(file_path)
            elif file_path.suffix.lower() == '.parquet':
                df = pd.read_parquet(file_path)
            elif file_path.suffix.lower() == '.pkl':
                df = pd.read_pickle(file_path)
            else:
                raise ValueError(f"Qo'llab-quvvatlanmaydigan fayl formati: {file_path.suffix}")
            
            # Convert timestamp if exists
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.set_index('timestamp')
            elif df.index.name != 'timestamp':
                # Assume first column is timestamp
                first_col = df.columns[0]
                if 'time' in first_col.lower() or 'date' in first_col.lower():
                    df[first_col] = pd.to_datetime(df[first_col])
                    df = df.set_index(first_col)
            
            # Filter by date range
            if start_date is not None or end_date is not None:
                df = self._filter_by_date(df, start_date, end_date)
            
            return df
            
        except Exception as e:
            print(f"Faylni yuklashda xatolik: {e}")
            # Return empty DataFrame with standard columns
            return pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
    
    def _filter_by_date(self, df: pd.DataFrame, start_date: datetime, 
                       end_date: datetime) -> pd.DataFrame:
        """Sana bo'yicha filtrlash"""
        if start_date is not None and end_date is not None:
            return df[(df.index >= start_date) & (df.index <= end_date)]
        elif start_date is not None:
            return df[df.index >= start_date]
        elif end_date is not None:
            return df[df.index <= end_date]
        return df
    
    def _generate_sample_data(self, symbol: str, timeframe: str, 
                             start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Namuna ma'lumotlar yaratish"""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365)
        if end_date is None:
            end_date = datetime.now()
        
        # Generate datetime index
        freq = self._get_timeframe_frequency(timeframe)
        dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        
        # Base price based on symbol
        base_prices = {
            'EURUSD': 1.1000,
            'GBPUSD': 1.3000,
            'USDJPY': 110.00,
            'USDCHF': 0.9200,
            'AUDUSD': 0.7500,
            'USDCAD': 1.2500,
            'NZDUSD': 0.7000,
            'XAUUSD': 1800.00,
            'XAGUSD': 24.00,
            'XPTUSD': 1000.00,
            'XPDUSD': 2200.00
        }
        
        base_price = base_prices.get(symbol.upper(), 100.0)
        
        # Generate realistic price movements
        np.random.seed(42)  # Reproducible results
        
        n_periods = len(dates)
        returns = np.random.normal(0, 0.01, n_periods)  # 1% daily volatility
        
        # Add some trend and mean reversion
        trend_strength = 0.001
        for i in range(1, n_periods):
            # Mean reversion component
            mean_reversion = -0.1 * returns[i-1]
            # Trend component
            trend = trend_strength * (i / n_periods)
            # Random component
            random_component = np.random.normal(0, 0.008)
            
            returns[i] += mean_reversion + trend + random_component
        
        # Calculate prices
        prices = base_price * np.cumprod(1 + returns)
        
        # Create OHLCV data
        data = []
        for i, (date, close_price) in enumerate(zip(dates, prices)):
            # Generate realistic OHLC from close price
            volatility = abs(returns[i]) * close_price
            
            # Open is previous close with some gap
            if i == 0:
                open_price = close_price
            else:
                gap = np.random.normal(0, volatility * 0.1)
                open_price = prices[i-1] + gap
            
            # High and Low based on volatility
            range_size = volatility * (1 + abs(np.random.normal(0, 0.5)))
            high_price = max(open_price, close_price) + abs(np.random.normal(0, range_size * 0.6))
            low_price = min(open_price, close_price) - abs(np.random.normal(0, range_size * 0.6))
            
            # Volume (higher volume around news times)
            base_volume = 1000000
            volume_multiplier = 1 + 0.5 * abs(returns[i])
            volume = int(base_volume * volume_multiplier * np.random.uniform(0.5, 2.0))
            
            data.append({
                'open': round(open_price, 5 if 'JPY' not in symbol else 3),
                'high': round(high_price, 5 if 'JPY' not in symbol else 3),
                'low': round(low_price, 5 if 'JPY' not in symbol else 3),
                'close': round(close_price, 5 if 'JPY' not in symbol else 3),
                'volume': volume
            })
        
        df = pd.DataFrame(data, index=dates)
        return df
    
    def _get_timeframe_frequency(self, timeframe: str) -> str:
        """Timeframe ni pandas frequency ga o'tkazish"""
        timeframe_map = {
            'tick': '1S',
            '1s': '1S',
            '1m': '1T',
            '5m': '5T',
            '15m': '15T',
            '30m': '30T',
            '1h': '1H',
            '4h': '4H',
            '1d': '1D',
            '1w': '1W',
            '1M': '1M'
        }
        return timeframe_map.get(timeframe, '1H')
    
    def load_multiple_symbols(self, symbols: List[str], timeframe: str = "H1",
                             start_date: datetime = None, end_date: datetime = None) -> Dict[str, pd.DataFrame]:
        """Bir nechta symbol ma'lumotlarini yuklash"""
        data_dict = {}
        
        for symbol in symbols:
            try:
                data_dict[symbol] = self.load_symbol_data(symbol, timeframe, start_date, end_date)
            except Exception as e:
                print(f"{symbol} ma'lumotlarini yuklashda xatolik: {e}")
                data_dict[symbol] = pd.DataFrame()
        
        return data_dict
    
    def save_data(self, df: pd.DataFrame, symbol: str, timeframe: str, 
                  data_type: str = DataTypes.OHLCV, format: str = 'csv') -> str:
        """Ma'lumotlarni saqlash"""
        file_path = self._get_data_path(symbol, timeframe, data_type)
        file_path = file_path.with_suffix(f'.{format}')
        
        if format == 'csv':
            df.to_csv(file_path)
        elif format == 'json':
            df.to_json(file_path)
        elif format == 'xlsx':
            df.to_excel(file_path)
        elif format == 'parquet':
            df.to_parquet(file_path)
        elif format == 'pkl':
            df.to_pickle(file_path)
        
        return str(file_path)
    
    def get_available_symbols(self, data_type: str = DataTypes.OHLCV) -> List[str]:
        """Mavjud symbollar ro'yxati"""
        symbols = set()
        
        for file_path in self.data_directory.glob(f"*{data_type}*"):
            # Extract symbol from filename
            filename = file_path.stem
            parts = filename.split('_')
            if len(parts) >= 1:
                symbols.add(parts[0])
        
        return list(symbols)
    
    def get_data_info(self, symbol: str, timeframe: str = "H1") -> Dict[str, Any]:
        """Ma'lumotlar haqida ma'lumot olish"""
        try:
            data = self.load_symbol_data(symbol, timeframe)
            
            if data.empty:
                return {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'status': 'no_data',
                    'records': 0
                }
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'status': 'available',
                'records': len(data),
                'start_date': data.index.min(),
                'end_date': data.index.max(),
                'columns': list(data.columns),
                'data_types': data.dtypes.to_dict(),
                'missing_values': data.isnull().sum().to_dict()
            }
            
        except Exception as e:
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'status': 'error',
                'error': str(e)
            }


class NewsDataLoader:
    """Yangiliklar ma'lumotlarini yuklash"""
    
    def __init__(self, data_directory: str = "/workspace/data/news"):
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(exist_ok=True)
    
    def load_news_data(self, start_date: datetime, end_date: datetime,
                      currencies: List[str] = None) -> pd.DataFrame:
        """Yangiliklar ma'lumotlarini yuklash"""
        # This would integrate with news APIs in a real implementation
        # For now, return sample news data
        
        news_data = []
        
        # Sample news events
        sample_news = [
            {
                'timestamp': datetime.now() - timedelta(days=1),
                'currency': 'USD',
                'impact': 'High',
                'event': 'Federal Reserve Interest Rate Decision',
                'actual': '5.50%',
                'forecast': '5.25%',
                'previous': '5.25%'
            },
            {
                'timestamp': datetime.now() - timedelta(days=2),
                'currency': 'EUR',
                'impact': 'Medium',
                'event': 'ECB President Speech',
                'actual': ' hawkish tone',
                'forecast': 'neutral',
                'previous': 'neutral'
            }
        ]
        
        for news in sample_news:
            if start_date <= news['timestamp'] <= end_date:
                if currencies is None or news['currency'] in currencies:
                    news_data.append(news)
        
        if news_data:
            return pd.DataFrame(news_data)
        else:
            return pd.DataFrame(columns=['timestamp', 'currency', 'impact', 'event', 'actual', 'forecast', 'previous'])


class EconomicCalendarLoader:
    """Iqtisodiy calendar ma'lumotlarini yuklash"""
    
    def __init__(self, data_directory: str = "/workspace/data/economic"):
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(exist_ok=True)
    
    def load_economic_events(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Iqtisodiy voqealar ma'lumotlarini yuklash"""
        # Sample economic events
        events = []
        
        # Generate sample events for the date range
        current_date = start_date
        while current_date <= end_date:
            # Major economic releases (typical schedule)
            events.extend([
                {
                    'timestamp': current_date.replace(hour=8, minute=30),
                    'currency': 'USD',
                    'event': 'Non-Farm Payrolls',
                    'impact': 'High',
                    'frequency': 'Monthly'
                },
                {
                    'timestamp': current_date.replace(hour=14, minute=0),
                    'currency': 'USD',
                    'event': 'FOMC Minutes',
                    'impact': 'High',
                    'frequency': 'Monthly'
                },
                {
                    'timestamp': current_date.replace(hour=12, minute=30),
                    'currency': 'EUR',
                    'event': 'ECB Interest Rate Decision',
                    'impact': 'High',
                    'frequency': 'Monthly'
                }
            ])
            current_date += timedelta(days=1)
        
        df = pd.DataFrame(events)
        if not df.empty:
            df = df[df['timestamp'].between(start_date, end_date)]
        
        return df


# Global data loader instance
data_loader = DataLoader()
news_loader = NewsDataLoader()
economic_loader = EconomicCalendarLoader()