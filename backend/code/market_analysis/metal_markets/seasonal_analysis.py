"""
Seasonal Analysis Module
=======================

Seasonal pattern tahlili.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class SeasonalAnalyzer:
    """Seasonal pattern tahlil moduli"""
    
    def __init__(self):
        self.seasonal_patterns = {
            'XAUUSD': {
                1: 0.95, 2: 0.92, 3: 1.05, 4: 1.02, 5: 0.98, 6: 1.01,
                7: 0.97, 8: 1.04, 9: 1.06, 10: 1.08, 11: 1.03, 12: 0.98
            },
            'XAGUSD': {
                1: 0.90, 2: 0.88, 3: 1.08, 4: 1.05, 5: 0.95, 6: 1.02,
                7: 0.94, 8: 1.06, 9: 1.10, 10: 1.12, 11: 1.05, 12: 0.96
            }
        }
    
    def analyze_seasonal_trends(self, data, symbol):
        """Seasonal trend tahlil"""
        if 'close' not in data.columns and len(data.columns) == 4:
            data.columns = ['open', 'high', 'low', 'close']
        
        monthly_data = data.groupby(data.index.month).agg({
            'close': ['mean', 'std', 'count'],
            'high': 'max',
            'low': 'min'
        })
        
        monthly_returns = data.groupby(data.index.month)['close'].apply(
            lambda x: (x.iloc[-1] / x.iloc[0] - 1) if len(x) > 1 else 0
        )
        
        seasonal_factors = self.seasonal_patterns.get(symbol, 
            {i: 1.0 for i in range(1, 13)})
        
        return {
            'monthly_statistics': monthly_data.to_dict(),
            'seasonal_returns': monthly_returns.to_dict(),
            'seasonal_factors': seasonal_factors,
            'strongest_months': self._find_strongest_months(monthly_returns),
            'weakest_months': self._find_weakest_months(monthly_returns)
        }
    
    def get_seasonal_adjustments(self, symbol, month, market_condition='normal'):
        """Seasonal moslamalar"""
        seasonal_factors = self.seasonal_patterns.get(symbol, 
            {i: 1.0 for i in range(1, 13)})
        
        base_adjustment = seasonal_factors.get(month, 1.0)
        
        condition_multipliers = {
            'bull': 1.1, 'bear': 0.9, 'normal': 1.0, 'crisis': 1.2
        }
        
        condition_adj = condition_multipliers.get(market_condition, 1.0)
        
        return {
            'adjustment_factor': base_adjustment * condition_adj,
            'seasonal_strength': self._classify_seasonal_strength(base_adjustment),
            'market_condition': market_condition
        }
    
    def predict_seasonal_performance(self, symbol, time_horizon='3M'):
        """Seasonal performansni bashoratlash"""
        current_month = datetime.now().month
        seasonal_data = self.seasonal_patterns.get(symbol, {})
        
        if time_horizon == '3M':
            next_3_months = [(current_month + i - 1) % 12 + 1 for i in range(1, 4)]
            avg_seasonal = np.mean([seasonal_data.get(month, 1.0) for month in next_3_months])
        else:
            avg_seasonal = 1.0
        
        return {
            'forecast_adjustment': avg_seasonal,
            'confidence': 0.7,
            'outlook': 'positive' if avg_seasonal > 1.02 else 'negative' if avg_seasonal < 0.98 else 'neutral'
        }
    
    def _find_strongest_months(self, monthly_returns):
        return monthly_returns.nlargest(3).index.tolist()
    
    def _find_weakest_months(self, monthly_returns):
        return monthly_returns.nsmallest(3).index.tolist()
    
    def _classify_seasonal_strength(self, factor):
        if factor > 1.05:
            return 'strong_positive'
        elif factor < 0.95:
            return 'strong_negative'
        elif factor > 1.02:
            return 'moderate_positive'
        elif factor < 0.98:
            return 'moderate_negative'
        else:
            return 'neutral'