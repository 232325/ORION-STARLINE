"""
Condition Adaptation Module
===========================

Market condition adaptation.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


class ConditionAdapter:
    """Market condition adapter"""
    
    def __init__(self):
        self.condition_thresholds = {
            'volatility_high': 0.25,
            'trend_strength': 0.6,
            'liquidity_low': 0.5,
            'correlation_extreme': 0.8
        }
    
    def adapt_to_market_conditions(self, strategy, conditions):
        """Strategiyani market shartlariga moslashtirish"""
        adapted_strategy = strategy.copy()
        
        if conditions.get('volatility_regime') == 'high':
            adapted_strategy['position_size'] *= 0.7
            adapted_strategy['stop_loss_pct'] *= 1.5
        
        elif conditions.get('volatility_regime') == 'low':
            adapted_strategy['position_size'] *= 1.2
            adapted_strategy['stop_loss_pct'] *= 0.8
        
        return adapted_strategy
    
    def get_adaptation_recommendations(self, current_conditions):
        """Moslashtirish tavsiyalari"""
        recommendations = {
            'position_size_adjustment': 1.0,
            'stop_loss_adjustment': 1.0,
            'entry_timing_adjustment': 1.0,
            'risk_management_level': 'normal'
        }
        
        volatility = current_conditions.get('current_volatility', 0)
        if volatility > self.condition_thresholds['volatility_high']:
            recommendations['position_size_adjustment'] = 0.7
            recommendations['stop_loss_adjustment'] = 1.5
            recommendations['risk_management_level'] = 'high'
        
        return recommendations
    
    def analyze_market_regime(self, data, market_data=None):
        """Market rejimini tahlil qilish"""
        if 'close' not in data.columns and len(data.columns) == 4:
            data.columns = ['open', 'high', 'low', 'close']
        
        returns = data['close'].pct_change().dropna()
        
        volatility_regime = self._detect_volatility_regime(returns)
        trend_regime = self._detect_trend_regime(data)
        liquidity_regime = self._estimate_liquidity_regime(data)
        
        current_conditions = {
            'volatility_regime': volatility_regime,
            'trend_regime': trend_regime,
            'current_volatility': returns.std() * np.sqrt(252),
            'liquidity_regime': liquidity_regime
        }
        
        return {
            'current_conditions': current_conditions,
            'adaptation_recommendations': self.get_adaptation_recommendations(current_conditions),
            'risk_level': self._assess_overall_risk(current_conditions)
        }
    
    def _detect_volatility_regime(self, returns):
        vol_percentiles = returns.rolling(window=30).std().quantile([0.33, 0.67])
        current_vol = returns.std()
        
        if current_vol <= vol_percentiles.iloc[0]:
            return 'low'
        elif current_vol >= vol_percentiles.iloc[1]:
            return 'high'
        else:
            return 'normal'
    
    def _detect_trend_regime(self, data):
        if 'close' not in data.columns and len(data.columns) == 4:
            data.columns = ['open', 'high', 'low', 'close']
        
        short_ma = data['close'].rolling(20).mean()
        long_ma = data['close'].rolling(50).mean()
        
        current_trend = short_ma.iloc[-1] - long_ma.iloc[-1]
        trend_strength = abs(current_trend) / long_ma.iloc[-1]
        
        if trend_strength > 0.02:
            return 'strong_trend'
        elif trend_strength > 0.01:
            return 'moderate_trend'
        else:
            return 'sideways'
    
    def _estimate_liquidity_regime(self, data):
        if 'volume' in data.columns:
            volume_volatility = data['volume'].std() / data['volume'].mean()
            if volume_volatility > 1.0:
                return 'low'
            elif volume_volatility < 0.5:
                return 'high'
            else:
                return 'normal'
        
        returns = data['close'].pct_change().dropna()
        if returns.std() > 0.02:
            return 'low'
        elif returns.std() < 0.01:
            return 'high'
        else:
            return 'normal'
    
    def _assess_overall_risk(self, conditions):
        risk_score = 0
        
        if conditions['volatility_regime'] == 'high':
            risk_score += 3
        elif conditions['volatility_regime'] == 'normal':
            risk_score += 2
        else:
            risk_score += 1
        
        if conditions['trend_regime'] == 'sideways':
            risk_score += 2
        else:
            risk_score += 1
        
        if conditions['liquidity_regime'] == 'low':
            risk_score += 2
        else:
            risk_score += 1
        
        if risk_score >= 6:
            return 'high'
        elif risk_score >= 4:
            return 'medium'
        else:
            return 'low'