"""
Market Regime Detection Module
============================

Bozor rejimlarini aniqlash moduli.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import warnings
warnings.filterwarnings('ignore')


class MarketRegimeDetector:
    """Bozor rejimlarini aniqlash moduli"""
    
    def __init__(self):
        self.regime_thresholds = {
            'trending': {'adx_threshold': 25, 'volatility_threshold': 0.02},
            'ranging': {'adx_threshold': 20, 'volatility_threshold': 0.015},
            'high_volatility': {'volatility_percentile': 0.8},
            'low_volatility': {'volatility_percentile': 0.2},
            'high_liquidity': {'volume_percentile': 0.7},
            'low_liquidity': {'volume_percentile': 0.3}
        }
    
    def detect_trending_ranging_regime(self, data: pd.DataFrame, window: int = 20) -> pd.Series:
        """Trending va ranging rejimlarini aniqlash"""
        if data.empty or 'close' not in data.columns:
            return pd.Series()
        
        returns = data['close'].pct_change()
        
        # Calculate ADX (simplified version)
        high = data['high'] if 'high' in data.columns else data['close'] * 1.01
        low = data['low'] if 'low' in data.columns else data['close'] * 0.99
        
        # Simplified trend detection - handle NaN values properly
        trend_strength = returns.rolling(window).mean() / returns.rolling(window).std()
        volatility = returns.rolling(window).std()
        
        # Initialize regime array with NaN
        regime = np.full(len(data), np.nan, dtype=object)
        
        # Only compute regime for positions where we have enough data
        for i in range(window - 1, len(data)):
            if not pd.isna(trend_strength.iloc[i]) and not pd.isna(volatility.iloc[i]):
                if (volatility.iloc[i] > self.regime_thresholds['trending']['volatility_threshold'] and 
                    abs(trend_strength.iloc[i]) > 0.5):
                    regime[i] = 'trending'
                else:
                    regime[i] = 'ranging'
        
        # Create series with proper index
        return pd.Series(regime, index=data.index)
    
    def detect_volatility_regime(self, data: pd.DataFrame, window: int = 20) -> pd.Series:
        """Volatility rejimini aniqlash"""
        if data.empty or 'close' not in data.columns:
            return pd.Series()
        
        returns = data['close'].pct_change().dropna()
        volatility = returns.rolling(window).std()
        
        # Calculate volatility percentiles
        vol_rolling = volatility.rolling(window * 2).rank(pct=True)
        
        regime = np.where(vol_rolling > 0.8, 'high_volatility',
                         np.where(vol_rolling < 0.2, 'low_volatility', 'normal_volatility'))
        
        return pd.Series(regime, index=data.index)
    
    def detect_liquidity_regime(self, data: pd.DataFrame, window: int = 20) -> pd.Series:
        """Liquidity rejimini aniqlash"""
        if data.empty or 'volume' not in data.columns:
            return pd.Series()
        
        volume = data['volume']
        vol_ma = volume.rolling(window).mean()
        vol_zscore = (volume - vol_ma) / volume.rolling(window).std()
        
        regime = np.where(vol_zscore > 1, 'high_liquidity',
                         np.where(vol_zscore < -1, 'low_liquidity', 'normal_liquidity'))
        
        return pd.Series(regime, index=data.index)
    
    def analyze_regime_transitions(self, data: pd.DataFrame) -> Dict[str, List]:
        """Rejim o'tishlarini tahlil qilish"""
        trends = self.detect_trending_ranging_regime(data)
        volatility_regimes = self.detect_volatility_regime(data)
        
        transitions = {
            'trend_transitions': [],
            'volatility_transitions': [],
            'combined_regime_changes': []
        }
        
        # Trend transitions
        if not trends.empty:
            trend_changes = trends.ne(trends.shift()).cumsum()
            for change_id in trend_changes.unique():
                change_data = trend_changes[trend_changes == change_id]
                transitions['trend_transitions'].append({
                    'start_time': change_data.index[0],
                    'end_time': change_data.index[-1],
                    'regime': trends[change_data.index[0]],
                    'duration_hours': len(change_data)
                })
        
        # Volatility transitions
        if not volatility_regimes.empty:
            vol_changes = volatility_regimes.ne(volatility_regimes.shift()).cumsum()
            for change_id in vol_changes.unique():
                change_data = vol_changes[vol_changes == change_id]
                transitions['volatility_transitions'].append({
                    'start_time': change_data.index[0],
                    'end_time': change_data.index[-1],
                    'regime': volatility_regimes[change_data.index[0]],
                    'duration_hours': len(change_data)
                })
        
        return transitions