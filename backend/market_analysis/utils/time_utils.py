"""
Time Utilities for Market Analysis
=================================

Vaqt bilan bog'liq yordamchi funksiyalar.
"""

from datetime import datetime, time, timedelta, timezone
from typing import List, Dict, Optional, Tuple
import pytz
import pandas as pd
import numpy as np


class TimeUtils:
    """Vaqt yordamchi funksiyalari"""
    
    @staticmethod
    def get_current_utc_time() -> datetime:
        """Joriy UTC vaqtni olish"""
        return datetime.now(timezone.utc)
    
    @staticmethod
    def convert_timezone(dt: datetime, timezone_str: str) -> datetime:
        """Vaqtni boshqa timezone ga o'tkazish"""
        from_zone = pytz.timezone('UTC')
        to_zone = pytz.timezone(timezone_str)
        dt = dt.replace(tzinfo=from_zone)
        return dt.astimezone(to_zone)
    
    @staticmethod
    def is_market_open(current_time: datetime, 
                      market_open: time, 
                      market_close: time,
                      trading_days: List[int] = None) -> bool:
        """Bozor ochiq yoki yopiqligini tekshirish"""
        if trading_days is None:
            trading_days = list(range(0, 7))
        
        # Kun tekshirish
        current_day = current_time.weekday()
        if current_day not in trading_days:
            return False
        
        # Vaqt tekshirish
        current_time_only = current_time.time()
        
        # Agar market_close > market_open (odatdagi holat)
        if market_close > market_open:
            return market_open <= current_time_only <= market_close
        
        # Agar market_close < market_open (kelgusi kuni yopiladi)
        else:
            return current_time_only >= market_open or current_time_only <= market_close
    
    @staticmethod
    def get_session_info(current_time: datetime) -> Dict[str, any]:
        """Joriy session haqida ma'lumot olish"""
        utc_time = current_time.astimezone(pytz.UTC)
        
        # London time
        london_time = utc_time.astimezone(pytz.timezone('Europe/London'))
        
        # New York time
        ny_time = utc_time.astimezone(pytz.timezone('America/New_York'))
        
        # Tokyo time
        tokyo_time = utc_time.astimezone(pytz.timezone('Asia/Tokyo'))
        
        # Session determination
        hour = utc_time.hour
        
        if 0 <= hour < 8:  # Asian session (Tokyo)
            active_sessions = ['Asian']
            overlap = False
            next_session = 'European'
        elif 8 <= hour < 13:  # European session overlap
            active_sessions = ['European', 'Asian']
            overlap = True
            next_session = 'American'
        elif 13 <= hour < 17:  # American session overlap
            active_sessions = ['American', 'European']
            overlap = True
            next_session = 'Asian'
        elif 17 <= hour < 22:  # American only
            active_sessions = ['American']
            overlap = False
            next_session = 'Asian'
        else:  # Low activity
            active_sessions = []
            overlap = False
            next_session = 'Asian'
        
        return {
            'utc_time': utc_time,
            'london_time': london_time,
            'ny_time': ny_time,
            'tokyo_time': tokyo_time,
            'active_sessions': active_sessions,
            'is_overlap': overlap,
            'next_session': next_session,
            'session_hour': hour
        }
    
    @staticmethod
    def get_session_volatility_multiplier(session_name: str) -> float:
        """Session uchun volatility multiplier"""
        multipliers = {
            'Asian': 0.7,
            'European': 1.2,
            'American': 1.4,
            'Overlap': 1.8
        }
        return multipliers.get(session_name, 1.0)
    
    @staticmethod
    def get_next_session_time(current_time: datetime, session_name: str) -> datetime:
        """Keyingi session boshlanish vaqtini olish"""
        session_starts = {
            'Asian': time(0, 0),   # 00:00 UTC
            'European': time(8, 0),  # 08:00 UTC
            'American': time(13, 0)  # 13:00 UTC
        }
        
        start_time = session_starts.get(session_name)
        if start_time is None:
            return current_time
        
        # Joriy kuni session boshlanish vaqti
        session_start_today = current_time.replace(
            hour=start_time.hour, 
            minute=start_time.minute,
            second=0, 
            microsecond=0
        )
        
        # Agar session bugun o'tib ketgan bo'lsa, ertasiga o'tkazish
        if session_start_today <= current_time:
            session_start_today += timedelta(days=1)
        
        return session_start_today
    
    @staticmethod
    def calculate_session_duration(session_name: str) -> timedelta:
        """Session davomiyligini hisoblash"""
        durations = {
            'Asian': timedelta(hours=8),    # 00:00 - 08:00
            'European': timedelta(hours=9), # 08:00 - 17:00
            'American': timedelta(hours=9), # 13:00 - 22:00
        }
        return durations.get(session_name, timedelta(hours=8))
    
    @staticmethod
    def is_high_impact_news_time(current_time: datetime) -> bool:
        """Yuqori ta'sirli yangiliklar vaqti tekshirish"""
        # Asosiy makro-iqtisodiy yangiliklar odatda soat 8:30, 10:00, 14:00 UTC da chiqadi
        high_impact_hours = [8, 10, 14, 15]  # UTC
        
        return current_time.hour in high_impact_hours
    
    @staticmethod
    def get_forex_major_pairs() -> List[str]:
        """Asosiy Forex juftliklar ro'yxati"""
        return [
            'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF',
            'AUDUSD', 'USDCAD', 'NZDUSD'
        ]
    
    @staticmethod
    def get_metal_symbols() -> List[str]:
        """Metal symbollar ro'yxati"""
        return [
            'XAUUSD', 'XAGUSD', 'XPTUSD', 'XPDUSD'
        ]
    
    @staticmethod
    def convert_to_forex_timeframe(data: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """Ma'lumotlarni forex vaqt freymiga o'tkazish"""
        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data = data.set_index('timestamp')
        
        # Timeframe mapping
        timeframe_map = {
            '1m': '1T',
            '5m': '5T',
            '15m': '15T',
            '30m': '30T',
            '1h': '1H',
            '4h': '4H',
            '1d': '1D'
        }
        
        freq = timeframe_map.get(timeframe, '1H')
        
        # OHLCV data resampling
        if all(col in data.columns for col in ['open', 'high', 'low', 'close']):
            ohlc_dict = {
                'open': 'first',
                'high': 'max', 
                'low': 'min',
                'close': 'last'
            }
            
            # Add volume if exists
            if 'volume' in data.columns:
                ohlc_dict['volume'] = 'sum'
            
            # Add any other columns
            for col in data.columns:
                if col not in ohlc_dict:
                    ohlc_dict[col] = 'last'
            
            resampled = data.resample(freq).agg(ohlc_dict).dropna()
            return resampled
        
        return data.resample(freq).last().dropna()
    
    @staticmethod
    def add_session_info(df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame ga session ma'lumotlarini qo'shish"""
        df = df.copy()
        
        # Ensure timestamp index
        if 'timestamp' not in df.columns and df.index.name != 'timestamp':
            df = df.reset_index()
        
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
        
        # Session info
        df['hour'] = df.index.hour
        
        # Session assignment
        conditions = [
            (df['hour'] >= 0) & (df['hour'] < 8),
            (df['hour'] >= 8) & (df['hour'] < 13),
            (df['hour'] >= 13) & (df['hour'] < 17),
            (df['hour'] >= 17) & (df['hour'] < 24)
        ]
        
        choices = ['Asian', 'Europe_Asia_Overlap', 'America_Europe_Overlap', 'American']
        df['session'] = np.select(conditions, choices, default='Unknown')
        
        # Overlap indicator
        df['is_overlap'] = df['session'].str.contains('Overlap')
        
        # Volatility multiplier
        session_multipliers = {
            'Asian': 0.7,
            'Europe_Asia_Overlap': 1.8,
            'America_Europe_Overlap': 1.8,
            'American': 1.4
        }
        df['volatility_multiplier'] = df['session'].map(session_multipliers)
        
        return df
    
    @staticmethod
    def get_timezone_offsets() -> Dict[str, int]:
        """Timezone offsetlari (soatlarda)"""
        return {
            'UTC': 0,
            'EST': -5,   # Eastern Standard Time
            'EDT': -4,   # Eastern Daylight Time  
            'GMT': 0,    # Greenwich Mean Time
            'BST': 1,    # British Summer Time
            'CET': 1,    # Central European Time
            'CEST': 2,   # Central European Summer Time
            'JST': 9,    # Japan Standard Time
            'AEST': 10,  # Australian Eastern Standard Time
            'AEDT': 11   # Australian Eastern Daylight Time
        }
    
    @staticmethod
    def calculate_market_hours_overlap() -> Dict[str, Dict[str, any]]:
        """Bozor soatlari overlap tahlili"""
        return {
            'Europe_Asia': {
                'start': time(8, 0),    # 08:00 UTC
                'end': time(9, 0),      # 09:00 UTC  
                'duration': 60,         # minutes
                'description': 'London-Tokyo overlap'
            },
            'Europe_America': {
                'start': time(13, 0),   # 13:00 UTC
                'end': time(17, 0),     # 17:00 UTC
                'duration': 240,        # minutes
                'description': 'London-New York overlap'
            },
            'America_Asia': {
                'start': time(1, 0),    # 01:00 UTC
                'end': time(2, 0),      # 02:00 UTC
                'duration': 60,         # minutes
                'description': 'New York-Tokyo overlap (very brief)'
            }
        }
    
    @staticmethod
    def get_trading_holidays(year: int) -> List[datetime]:
        """Yil uchun trading bayramlari"""
        # Asosiy bayramlar ( приблизительно )
        holidays = []
        
        # New Year's Day
        holidays.append(datetime(year, 1, 1))
        
        # Christmas (December 25)
        holidays.append(datetime(year, 12, 25))
        
        # Boxing Day (December 26) - UK
        holidays.append(datetime(year, 12, 26))
        
        # Good Friday va Easter Monday (variable dates)
        # Bu yerda oddiy hisoblash, real dasturda precise calculations kerak
        easter_year = year
        holidays.extend([
            datetime(easter_year, 3, 21) + timedelta(days=60),  # Good Friday (approx)
            datetime(easter_year, 3, 21) + timedelta(days=63)   # Easter Monday (approx)
        ])
        
        return holidays
    
    @staticmethod
    def is_trading_day(current_time: datetime, trading_days: List[int] = None) -> bool:
        """Trading kuni yoki yo'qligini tekshirish"""
        if trading_days is None:
            trading_days = list(range(0, 7))  # Monday to Sunday
        
        # Bayram tekshirish
        holidays = TimeUtils.get_trading_holidays(current_time.year)
        if current_time.date() in [h.date() for h in holidays]:
            return False
        
        # Kun tekshirish
        return current_time.weekday() in trading_days