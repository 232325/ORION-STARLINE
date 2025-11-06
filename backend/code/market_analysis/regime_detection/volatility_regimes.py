"""
Volatility Regimes Module
========================

Volatility rejimlarini aniqlash moduli.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class VolatilityRegimeAnalyzer:
    """Volatility rejim tahlil moduli"""
    
    def __init__(self):
        self.volatility_thresholds = {
            'very_low': 0.005,
            'low': 0.010,
            'normal': 0.020,
            'high': 0.040,
            'very_high': 0.080
        }
    
    def detect_volatility_regimes(self, data: pd.DataFrame, window: int = 20) -> pd.Series:
        """Volatility rejimlarini aniqlash"""
        if data.empty or 'close' not in data.columns:
            return pd.Series()
        
        returns = data['close'].pct_change().dropna()
        volatility = returns.rolling(window).std()
        
        # Regime classification
        regimes = []
        for vol in volatility:
            if vol <= self.volatility_thresholds['very_low']:
                regimes.append('very_low_volatility')
            elif vol <= self.volatility_thresholds['low']:
                regimes.append('low_volatility')
            elif vol <= self.volatility_thresholds['normal']:
                regimes.append('normal_volatility')
            elif vol <= self.volatility_thresholds['high']:
                regimes.append('high_volatility')
            else:
                regimes.append('very_high_volatility')
        
        return pd.Series(regimes, index=data.index)
    
    def analyze_volatility_clusters(self, volatility_series: pd.Series) -> Dict[str, any]:
        """Volatility clustering tahlili"""
        # Find clusters of high/low volatility
        high_vol_periods = volatility_series > volatility_series.quantile(0.8)
        low_vol_periods = volatility_series < volatility_series.quantile(0.2)
        
        return {
            'high_volatility_periods': high_vol_periods.sum(),
            'low_volatility_periods': low_vol_periods.sum(),
            'volatility_persistence': self._calculate_persistence(volatility_series),
            'volatility_transition_frequency': self._calculate_transitions(volatility_series)
        }
    
    def _calculate_persistence(self, series: pd.Series) -> float:
        """Volatility persistence hisoblash"""
        if len(series) < 2:
            return 0
        
        # Count consecutive periods with same regime
        regime_changes = series.ne(series.shift()).sum()
        persistence = 1 - (regime_changes / len(series))
        return persistence
    
    def _calculate_transitions(self, series: pd.Series) -> int:
        """Rejim o'tishlar soni"""
        return series.ne(series.shift()).sum()