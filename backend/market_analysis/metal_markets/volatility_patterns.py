"""
Metal Markets Volatility Patterns Module
========================================

Metallarning o'zgaruvchanlik namunalarini tahlil qilish moduli.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class VolatilityPatternAnalyzer:
    """Metallarning o'zgaruvchanlik namunalarini tahlil qiluvchi"""
    
    def __init__(self):
        self.metal_volatilities = {
            'XAUUSD': 0.15,  # Oltin (yillik o'zgaruvchanlik)
            'XAGUSD': 0.22,  # Kumush
            'XPTUSD': 0.25,  # Platinum
            'XPDUSD': 0.28   # Palladium
        }
        
        # Maked soatlari bo'yicha o'zgaruvchanlik
        self.session_volatility_multipliers = {
            'Asian': 0.8,
            'European': 1.1, 
            'American': 1.0,
            'Overlap': 1.3
        }
    
    def calculate_realized_volatility(self, price_data: pd.Series, 
                                    window: int = 20) -> pd.Series:
        """Realized volatility hisoblash"""
        returns = price_data.pct_change().dropna()
        realized_vol = returns.rolling(window=window).std() * np.sqrt(252)
        return realized_vol
    
    def analyze_intraday_volatility_pattern(self, data: pd.DataFrame) -> Dict:
        """Kun ichidagi o'zgaruvchanlik namunalarini tahlil qilish"""
        if 'close' not in data.columns and len(data.columns) == 4:
            data.columns = ['open', 'high', 'low', 'close']
        
        hourly_vol = {}
        for hour in range(24):
            hour_data = data[data.index.hour == hour]
            if len(hour_data) > 0:
                returns = hour_data['close'].pct_change().dropna()
                hourly_vol[hour] = returns.std() * np.sqrt(252 * 24)
        
        return {
            'hourly_volatility': hourly_vol,
            'peak_volatility_hours': self._find_peak_hours(hourly_vol),
            'low_volatility_hours': self._find_low_hours(hourly_vol),
            'avg_daily_volatility': np.mean(list(hourly_vol.values()))
        }
    
    def analyze_session_volatility(self, data: pd.DataFrame) -> Dict:
        """Seans bo'yicha o'zgaruvchanlik tahlili"""
        if 'close' not in data.columns and len(data.columns) == 4:
            data.columns = ['open', 'high', 'low', 'close']
        
        session_vols = {}
        
        # Asian session (00:00-08:00 UTC)
        asian_data = data[(data.index.hour >= 0) & (data.index.hour < 8)]
        if len(asian_data) > 10:
            asian_returns = asian_data['close'].pct_change().dropna()
            session_vols['Asian'] = asian_returns.std() * np.sqrt(252)
        
        # European session (08:00-16:00 UTC)
        european_data = data[(data.index.hour >= 8) & (data.index.hour < 16)]
        if len(european_data) > 10:
            european_returns = european_data['close'].pct_change().dropna()
            session_vols['European'] = european_returns.std() * np.sqrt(252)
        
        # American session (16:00-00:00 UTC)
        american_data = data[(data.index.hour >= 16) | (data.index.hour == 0)]
        if len(american_data) > 10:
            american_returns = american_data['close'].pct_change().dropna()
            session_vols['American'] = american_returns.std() * np.sqrt(252)
        
        # Overlap periods
        eu_us_overlap = data[(data.index.hour >= 13) & (data.index.hour < 16)]
        if len(eu_us_overlap) > 5:
            overlap_returns = eu_us_overlap['close'].pct_change().dropna()
            session_vols['EU-US_Overlap'] = overlap_returns.std() * np.sqrt(252)
        
        return {
            'session_volatilities': session_vols,
            'highest_volatility_session': max(session_vols.items(), key=lambda x: x[1])[0] if session_vols else None,
            'volatility_ratios': self._calculate_vol_ratios(session_vols)
        }
    
    def forecast_volatility(self, symbol: str, time_horizon: str = '1M') -> Dict:
        """Volatilni bashoratlash"""
        base_volatility = self.metal_volatilities.get(symbol, 0.20)
        
        # Makroekonomik omillarga ko'ra tuzatishlar
        adjustments = self._get_economic_adjustments(symbol, time_horizon)
        
        forecast_vol = base_volatility * adjustments['multiplier']
        
        return {
            'base_volatility': base_volatility,
            'forecasted_volatility': forecast_vol,
            'confidence_interval': [forecast_vol * 0.8, forecast_vol * 1.2],
            'adjustment_factors': adjustments
        }
    
    def detect_volatility_regime_changes(self, data: pd.DataFrame, 
                                       lookback: int = 50) -> Dict:
        """Volatil rejim o'zgarishlarini aniqlash"""
        if 'close' not in data.columns and len(data.columns) == 4:
            data.columns = ['open', 'high', 'low', 'close']
        
        returns = data['close'].pct_change().dropna()
        rolling_vol = returns.rolling(window=lookback).std() * np.sqrt(252)
        
        # Volatil rejimlarni aniqlash (past, o'rta, yuqori)
        vol_percentiles = rolling_vol.quantile([0.33, 0.67]).dropna()
        
        regime_changes = []
        current_regime = self._classify_volatility(rolling_vol.iloc[-1], vol_percentiles)
        
        for i in range(lookback, len(rolling_vol)):
            vol_level = rolling_vol.iloc[i]
            regime = self._classify_volatility(vol_level, vol_percentiles)
            
            if regime != current_regime:
                regime_changes.append({
                    'date': rolling_vol.index[i],
                    'old_regime': current_regime,
                    'new_regime': regime,
                    'volatility_level': vol_level
                })
                current_regime = regime
        
        return {
            'current_regime': current_regime,
            'regime_changes': regime_changes,
            'volatility_percentiles': vol_percentiles.to_dict(),
            'recent_volatility': rolling_vol.iloc[-lookback:].tolist()
        }
    
    def _find_peak_hours(self, hourly_vol: Dict) -> List[int]:
        """Eng yuqori o'zgaruvchanlik soatlarini topish"""
        if not hourly_vol:
            return []
        
        avg_vol = np.mean(list(hourly_vol.values()))
        peak_hours = [hour for hour, vol in hourly_vol.items() 
                     if vol > avg_vol * 1.2]
        return sorted(peak_hours)
    
    def _find_low_hours(self, hourly_vol: Dict) -> List[int]:
        """Eng past o'zgaruvchanlik soatlarini topish"""
        if not hourly_vol:
            return []
        
        avg_vol = np.mean(list(hourly_vol.values()))
        low_hours = [hour for hour, vol in hourly_vol.items() 
                    if vol < avg_vol * 0.8]
        return sorted(low_hours)
    
    def _calculate_vol_ratios(self, session_vols: Dict) -> Dict:
        """Seans volatil nisbatlarini hisoblash"""
        if not session_vols:
            return {}
        
        avg_vol = np.mean(list(session_vols.values()))
        return {session: vol / avg_vol for session, vol in session_vols.items()}
    
    def _get_economic_adjustments(self, symbol: str, time_horizon: str) -> Dict:
        """Iqtisodiy omillarga ko'ra tuzatishlar"""
        # Oddiy logika - real dasturda makroekonomik ma'lumotlar kerak
        base_multiplier = 1.0
        
        if symbol == 'XAUUSD':  # Oltin
            if time_horizon == '1D':
                base_multiplier *= 1.1  # Kunlik volatil ortadi
            elif time_horizon == '3M':
                base_multiplier *= 0.9  # Uzoq muddatda kamayadi
        
        elif symbol in ['XAGUSD', 'XPTUSD', 'XPDUSD']:  # Boshqa metallar
            if time_horizon == '1D':
                base_multiplier *= 1.2  # Yuqori volatil
            elif time_horizon == '3M':
                base_multiplier *= 0.85
        
        return {
            'multiplier': base_multiplier,
            'risk_level': 'medium' if base_multiplier < 1.1 else 'high'
        }
    
    def _classify_volatility(self, volatility: float, 
                           percentiles: pd.Series) -> str:
        """Volatilni rejimga tasniflash"""
        if pd.isna(volatility):
            return 'unknown'
        
        low_thresh = percentiles.iloc[0]
        high_thresh = percentiles.iloc[1]
        
        if volatility <= low_thresh:
            return 'low'
        elif volatility >= high_thresh:
            return 'high'
        else:
            return 'medium'