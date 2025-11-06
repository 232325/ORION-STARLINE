"""
Adaptive Strategies Module
=========================

Moslashuvchan strategiya moduli.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class AdaptiveStrategyManager:
    """Moslashuvchan strategiya boshqaruvchisi"""
    
    def __init__(self):
        self.strategies = {
            'trend_following': {
                'suitable_regimes': ['trending', 'high_volatility'],
                'position_sizing': 1.2,
                'stop_loss_pct': 0.03,
                'take_profit_pct': 0.06
            },
            'mean_reversion': {
                'suitable_regimes': ['ranging', 'low_volatility'],
                'position_sizing': 0.8,
                'stop_loss_pct': 0.02,
                'take_profit_pct': 0.04
            },
            'breakout': {
                'suitable_regimes': ['trending', 'high_volatility'],
                'position_sizing': 1.0,
                'stop_loss_pct': 0.025,
                'take_profit_pct': 0.05
            },
            'scalping': {
                'suitable_regimes': ['normal_volatility', 'high_liquidity'],
                'position_sizing': 1.5,
                'stop_loss_pct': 0.008,
                'take_profit_pct': 0.015
            }
        }
    
    def select_optimal_strategy(self, market_regime: str, liquidity_level: str,
                              volatility_level: str) -> Dict[str, any]:
        """Optimal strategiya tanlash"""
        suitable_strategies = []
        
        for strategy_name, strategy_config in self.strategies.items():
            if market_regime in strategy_config['suitable_regimes']:
                # Calculate suitability score
                score = self._calculate_strategy_score(
                    strategy_name, market_regime, liquidity_level, volatility_level
                )
                suitable_strategies.append((strategy_name, score))
        
        # Sort by score
        suitable_strategies.sort(key=lambda x: x[1], reverse=True)
        
        if not suitable_strategies:
            return {
                'selected_strategy': 'conservative',
                'score': 0,
                'reason': 'No suitable strategies found'
            }
        
        best_strategy = suitable_strategies[0]
        
        return {
            'selected_strategy': best_strategy[0],
            'score': best_strategy[1],
            'configuration': self.strategies[best_strategy[0]],
            'alternative_strategies': [s[0] for s in suitable_strategies[1:3]]
        }
    
    def _calculate_strategy_score(self, strategy_name: str, market_regime: str,
                                liquidity_level: str, volatility_level: str) -> float:
        """Strategiya moslik ballini hisoblash"""
        base_score = 1.0
        
        # Regime suitability
        if market_regime in self.strategies[strategy_name]['suitable_regimes']:
            base_score *= 1.5
        
        # Liquidity adjustments
        if liquidity_level == 'high_liquidity':
            if strategy_name in ['scalping', 'breakout']:
                base_score *= 1.3
        elif liquidity_level == 'low_liquidity':
            base_score *= 0.7
        
        # Volatility adjustments
        if volatility_level == 'high_volatility':
            if strategy_name in ['trend_following', 'breakout']:
                base_score *= 1.2
            elif strategy_name == 'mean_reversion':
                base_score *= 0.8
        elif volatility_level == 'low_volatility':
            if strategy_name == 'mean_reversion':
                base_score *= 1.2
            elif strategy_name == 'scalping':
                base_score *= 0.9
        
        return base_score
    
    def adapt_strategy_parameters(self, strategy_name: str, performance_metrics: Dict) -> Dict[str, float]:
        """Strategiya parametrlarini moslashtirish"""
        base_config = self.strategies[strategy_name].copy()
        
        # Performance-based adjustments
        if 'win_rate' in performance_metrics:
            win_rate = performance_metrics['win_rate']
            if win_rate < 0.4:  # Poor performance
                base_config['position_sizing'] *= 0.8
                base_config['stop_loss_pct'] *= 1.2
            elif win_rate > 0.7:  # Excellent performance
                base_config['position_sizing'] *= 1.1
                base_config['take_profit_pct'] *= 1.1
        
        if 'max_drawdown_pct' in performance_metrics:
            max_dd = performance_metrics['max_drawdown_pct']
            if max_dd > 15:  # High drawdown
                base_config['position_sizing'] *= 0.9
        
        return base_config
    
    def switch_strategy_conditions(self, current_performance: Dict, 
                                 market_conditions: Dict) -> Tuple[bool, str]:
        """Strategiya o'zgartirish shartlari"""
        # Performance-based switching
        if current_performance.get('recent_return_pct', 0) < -5:  # 5% loss
            return True, 'poor_performance'
        
        # Market condition changes
        if market_conditions.get('regime_changed', False):
            return True, 'regime_change'
        
        # Volatility spike
        if market_conditions.get('volatility_spike', False):
            return True, 'high_volatility'
        
        return False, 'no_change_needed'