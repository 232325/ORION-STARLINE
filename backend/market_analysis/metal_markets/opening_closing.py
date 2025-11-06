"""
Metal Market Analyzer
====================

Asosiy metal market tahlil moduli.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')


class MetalMarketAnalyzer:
    """Metal bozor tahlil moduli"""
    
    def __init__(self):
        self.metal_characteristics = {
            'XAUUSD': {  # Gold
                'volatility_profile': 'medium',
                'liquidity_hours': [8, 9, 10, 13, 14, 15, 16],
                'correlation_assets': ['USD', 'Bonds', 'Equities'],
                'seasonal_patterns': {
                    'january': 'weak', 'february': 'strong', 'march': 'medium',
                    'april': 'medium', 'may': 'weak', 'june': 'medium',
                    'july': 'weak', 'august': 'strong', 'september': 'strong',
                    'october': 'medium', 'november': 'weak', 'december': 'weak'
                },
                'key_drivers': ['inflation', 'geopolitical_risk', 'currency_weakness']
            },
            'XAGUSD': {  # Silver
                'volatility_profile': 'high',
                'liquidity_hours': [9, 10, 13, 14, 15],
                'correlation_assets': ['Gold', 'Industrial_Metals', 'USD'],
                'seasonal_patterns': {
                    'january': 'medium', 'february': 'strong', 'march': 'medium',
                    'april': 'medium', 'may': 'weak', 'june': 'strong',
                    'july': 'weak', 'august': 'strong', 'september': 'strong',
                    'october': 'medium', 'november': 'weak', 'december': 'weak'
                },
                'key_drivers': ['industrial_demand', 'technology_sector', 'inflation_hedge']
            },
            'XPTUSD': {  # Platinum
                'volatility_profile': 'high',
                'liquidity_hours': [9, 10, 13, 14, 15],
                'correlation_assets': ['Gold', 'Auto_Industry', 'Industrial'],
                'seasonal_patterns': {
                    'january': 'medium', 'february': 'strong', 'march': 'weak',
                    'april': 'medium', 'may': 'strong', 'june': 'medium',
                    'july': 'weak', 'august': 'medium', 'september': 'strong',
                    'october': 'medium', 'november': 'weak', 'december': 'medium'
                },
                'key_drivers': ['auto_sales', 'industrial_demand', 'investment_demand']
            },
            'XPDUSD': {  # Palladium
                'volatility_profile': 'very_high',
                'liquidity_hours': [9, 10, 13, 14],
                'correlation_assets': ['Platinum', 'Auto_Industry', 'Industrial'],
                'seasonal_patterns': {
                    'january': 'strong', 'february': 'medium', 'march': 'weak',
                    'april': 'medium', 'may': 'strong', 'june': 'weak',
                    'july': 'medium', 'august': 'strong', 'september': 'weak',
                    'october': 'medium', 'november': 'strong', 'december': 'medium'
                },
                'key_drivers': ['auto_catalysts', 'supply_constraints', 'industrial_demand']
            }
        }
    
    def analyze_market_opening_patterns(self, symbol: str, data: pd.DataFrame) -> Dict[str, any]:
        """Bozor ochilish patternlarini tahlil qilish"""
        if data.empty or 'open' not in data.columns:
            return {}
        
        # Add time features
        df = data.copy()
        if isinstance(df.index, pd.DatetimeIndex):
            df['hour'] = df.index.hour
            df['day_of_week'] = df.index.dayofweek
            df['month'] = df.index.month
        
        # Opening gap analysis
        df['opening_gap'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1) * 100
        
        # Opening patterns by hour
        opening_stats = {}
        for hour in df['hour'].unique():
            hour_data = df[df['hour'] == hour]
            if len(hour_data) > 5:
                opening_stats[f'hour_{hour}'] = {
                    'avg_gap_pct': hour_data['opening_gap'].mean(),
                    'gap_std': hour_data['opening_gap'].std(),
                    'positive_gap_prob': (hour_data['opening_gap'] > 0).mean(),
                    'max_gap_pct': hour_data['opening_gap'].max(),
                    'min_gap_pct': hour_data['opening_gap'].min()
                }
        
        # Day of week patterns
        dow_stats = {}
        for dow in df['day_of_week'].unique():
            dow_data = df[df['day_of_week'] == dow]
            if len(dow_data) > 5:
                dow_stats[f'day_{dow}'] = {
                    'avg_gap_pct': dow_data['opening_gap'].mean(),
                    'gap_volatility': dow_data['opening_gap'].std(),
                    'trend_strength': self._calculate_trend_strength(dow_data['close'])
                }
        
        return {
            'opening_gap_analysis': opening_stats,
            'day_of_week_patterns': dow_stats,
            'overall_opening_characteristics': {
                'avg_opening_gap_pct': df['opening_gap'].mean(),
                'opening_volatility': df['opening_gap'].std(),
                'most_volatile_hour': max(opening_stats.keys(), 
                                        key=lambda x: opening_stats[x]['gap_std']) if opening_stats else None,
                'best_opening_hour': min(opening_stats.keys(), 
                                       key=lambda x: abs(opening_stats[x]['avg_gap_pct'])) if opening_stats else None
            }
        }
    
    def _calculate_trend_strength(self, prices: pd.Series) -> float:
        """Trend kuchini hisoblash"""
        if len(prices) < 2:
            return 0
        
        # Simple trend strength using linear regression
        x = np.arange(len(prices))
        slope, _, r_value, _, _ = np.polyfit(x, prices, 1, full=True)
        
        # Return absolute correlation as trend strength
        return abs(r_value[0]) if len(r_value) > 0 else 0
    
    def analyze_market_closing_patterns(self, symbol: str, data: pd.DataFrame) -> Dict[str, any]:
        """Bozor yopilish patternlarini tahlil qilish"""
        if data.empty or 'close' not in data.columns:
            return {}
        
        df = data.copy()
        if isinstance(df.index, pd.DatetimeIndex):
            df['hour'] = df.index.hour
            df['minute'] = df.index.minute
        
        # Closing patterns (last hour of trading)
        last_hour_data = df[df['hour'] == df['hour'].max()] if 'hour' in df.columns else df
        
        # Price movement in closing hour
        last_hour_data['hour_return'] = last_hour_data['close'].pct_change()
        
        # Closing patterns by minute
        closing_patterns = {}
        if 'minute' in last_hour_data.columns:
            for minute in sorted(last_hour_data['minute'].unique()):
                minute_data = last_hour_data[last_hour_data['minute'] == minute]
                if len(minute_data) > 3:
                    closing_patterns[f'minute_{minute}'] = {
                        'avg_return': minute_data['hour_return'].mean(),
                        'return_volatility': minute_data['hour_return'].std(),
                        'direction_bias': 'bullish' if minute_data['hour_return'].mean() > 0 else 'bearish'
                    }
        
        # Intraday momentum in closing
        if 'high' in df.columns and 'low' in df.columns:
            df['intraday_range'] = (df['high'] - df['low']) / df['close']
            df['closing_position'] = (df['close'] - df['low']) / df['intraday_range']
            
            closing_stats = {
                'avg_closing_position': df['closing_position'].mean(),
                'closing_bias': 'upper_half' if df['closing_position'].mean() > 0.5 else 'lower_half',
                'momentum_strength': df['closing_position'].std()
            }
        else:
            closing_stats = {}
        
        return {
            'closing_minute_patterns': closing_patterns,
            'intraday_closing_stats': closing_stats,
            'closing_hour_analysis': {
                'avg_hour_return': last_hour_data['hour_return'].mean(),
                'hour_volatility': last_hour_data['hour_return'].std(),
                'most_active_minutes': self._get_most_active_minutes(last_hour_data)
            }
        }
    
    def _get_most_active_minutes(self, data: pd.DataFrame) -> List[int]:
        """Eng faol daqiqalarni olish"""
        if 'minute' not in data.columns:
            return []
        
        minute_volatility = data.groupby('minute')['close'].std()
        return minute_volatility.nlargest(3).index.tolist()
    
    def get_optimal_trading_hours(self, symbol: str) -> Dict[str, any]:
        """Optimal trading soatlarini aniqlash"""
        metal_info = self.metal_characteristics.get(symbol.upper(), {})
        liquidity_hours = metal_info.get('liquidity_hours', [9, 10, 13, 14, 15])
        
        # Hour-based recommendations
        hour_recommendations = {}
        for hour in range(24):
            if hour in liquidity_hours:
                hour_recommendations[hour] = {
                    'liquidity_level': 'high',
                    'volatility_level': 'medium',
                    'trading_suitability': 'excellent',
                    'position_sizing_multiplier': 1.2
                }
            elif 8 <= hour <= 18:
                hour_recommendations[hour] = {
                    'liquidity_level': 'medium',
                    'volatility_level': 'medium',
                    'trading_suitability': 'good',
                    'position_sizing_multiplier': 1.0
                }
            else:
                hour_recommendations[hour] = {
                    'liquidity_level': 'low',
                    'volatility_level': 'low',
                    'trading_suitability': 'avoid',
                    'position_sizing_multiplier': 0.3
                }
        
        return {
            'symbol': symbol,
            'optimal_hours': liquidity_hours,
            'hour_recommendations': hour_recommendations,
            'session_overview': {
                'asian_session': {'hours': list(range(0, 9)), 'suitability': 'fair'},
                'european_session': {'hours': list(range(8, 17)), 'suitability': 'excellent'},
                'american_session': {'hours': list(range(13, 23)), 'suitability': 'excellent'},
                'overlap_periods': {'hours': [13, 14, 15, 16], 'suitability': 'optimal'}
            }
        }
    
    def analyze_seasonal_patterns(self, symbol: str, data: pd.DataFrame) -> Dict[str, any]:
        """Seasonal pattern tahlili"""
        if data.empty:
            return {}
        
        df = data.copy()
        if isinstance(df.index, pd.DatetimeIndex):
            df['month'] = df.index.month
            df['quarter'] = df.index.quarter
            df['year'] = df.index.year
        
        # Monthly patterns
        monthly_stats = {}
        for month in range(1, 13):
            month_data = df[df['month'] == month]
            if len(month_data) > 5:
                monthly_return = month_data['close'].pct_change().mean() * 100
                monthly_volatility = month_data['close'].pct_change().std() * 100
                
                monthly_stats[f'month_{month}'] = {
                    'avg_return_pct': monthly_return,
                    'volatility_pct': monthly_volatility,
                    'sample_size': len(month_data),
                    'direction': 'bullish' if monthly_return > 0 else 'bearish'
                }
        
        # Quarterly patterns
        quarterly_stats = {}
        for quarter in range(1, 5):
            quarter_data = df[df['quarter'] == quarter]
            if len(quarter_data) > 10:
                quarter_return = quarter_data['close'].pct_change().mean() * 100
                
                quarterly_stats[f'Q{quarter}'] = {
                    'avg_return_pct': quarter_return,
                    'best_months': self._get_quarter_best_months(quarter_data),
                    'performance_rank': self._rank_quarter_performance(quarter_return)
                }
        
        # Year-over-year analysis
        if 'year' in df.columns:
            yearly_returns = []
            for year in df['year'].unique():
                year_data = df[df['year'] == year]
                if len(year_data) > 100:  # Minimum data requirement
                    year_return = (year_data['close'].iloc[-1] / year_data['close'].iloc[0] - 1) * 100
                    yearly_returns.append({'year': year, 'return_pct': year_return})
        
        return {
            'monthly_patterns': monthly_stats,
            'quarterly_patterns': quarterly_stats,
            'yearly_performance': yearly_returns,
            'seasonal_recommendations': self._get_seasonal_recommendations(symbol, monthly_stats)
        }
    
    def _get_quarter_best_months(self, quarter_data: pd.DataFrame) -> List[int]:
        """Chorakning eng yaxshi oylarini olish"""
        if 'month' not in quarter_data.columns:
            return []
        
        monthly_returns = quarter_data.groupby('month')['close'].apply(
            lambda x: (x.iloc[-1] / x.iloc[0] - 1) * 100 if len(x) > 1 else 0
        )
        
        return monthly_returns.nlargest(2).index.tolist()
    
    def _rank_quarter_performance(self, return_value: float) -> str:
        """Chorak performance ranking"""
        if return_value > 5:
            return 'excellent'
        elif return_value > 2:
            return 'good'
        elif return_value > 0:
            return 'positive'
        elif return_value > -2:
            return 'neutral'
        else:
            return 'poor'
    
    def _get_seasonal_recommendations(self, symbol: str, monthly_stats: Dict) -> Dict[str, any]:
        """Seasonal tavsiyalar"""
        if not monthly_stats:
            return {}
        
        # Find best and worst months
        returns = {int(k.split('_')[1]): v['avg_return_pct'] for k, v in monthly_stats.items()}
        best_month = max(returns.keys(), key=lambda x: returns[x])
        worst_month = min(returns.keys(), key=lambda x: returns[x])
        
        recommendations = {
            'best_months': sorted(returns.keys(), key=lambda x: returns[x], reverse=True)[:3],
            'worst_months': sorted(returns.keys(), key=lambda x: returns[x])[:3],
            'seasonal_bias': 'positive' if sum(returns.values()) > 0 else 'negative',
            'trading_strategy': self._get_seasonal_strategy(symbol, best_month, worst_month)
        }
        
        return recommendations
    
    def _get_seasonal_strategy(self, symbol: str, best_month: int, worst_month: int) -> Dict[str, str]:
        """Seasonal strategiya tavsiyasi"""
        return {
            'institutional_building': f"Prepare for seasonal strength in month {best_month}",
            'profit_taking': f"Consider taking profits before month {worst_month}",
            'allocation_adjustment': f"Increase allocation in Q{best_month // 3 + 1}, decrease in Q{worst_month // 3 + 1}",
            'risk_management': "Adjust stop losses during seasonal transition periods"
        }
    
    def create_metal_market_report(self, symbol: str, data: pd.DataFrame) -> Dict[str, any]:
        """Metal bozor hisoboti"""
        opening_analysis = self.analyze_market_opening_patterns(symbol, data)
        closing_analysis = self.analyze_market_closing_patterns(symbol, data)
        seasonal_analysis = self.analyze_seasonal_patterns(symbol, data)
        trading_hours = self.get_optimal_trading_hours(symbol)
        
        # Market characteristics
        if not data.empty:
            returns = data['close'].pct_change().dropna()
            volatility = returns.std() * 100
            avg_return = returns.mean() * 100
            max_drawdown = self._calculate_max_drawdown(data['close'])
        else:
            volatility = avg_return = max_drawdown = 0
        
        return {
            'symbol': symbol,
            'market_characteristics': {
                'volatility_pct': volatility,
                'avg_daily_return_pct': avg_return,
                'max_drawdown_pct': max_drawdown,
                'trading_days_analyzed': len(data) if not data.empty else 0
            },
            'opening_patterns': opening_analysis,
            'closing_patterns': closing_analysis,
            'seasonal_patterns': seasonal_analysis,
            'optimal_trading_hours': trading_hours,
            'key_insights': self._generate_key_insights(symbol, data),
            'trading_recommendations': self._generate_trading_recommendations(symbol)
        }
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Maksimal drawdown hisoblash"""
        if len(prices) < 2:
            return 0
        
        peak = prices.expanding().max()
        drawdown = (prices - peak) / peak
        return drawdown.min() * 100
    
    def _generate_key_insights(self, symbol: str, data: pd.DataFrame) -> List[str]:
        """Asosiy insights yaratish"""
        insights = []
        
        # Add symbol-specific insights
        if symbol.upper() == 'XAUUSD':
            insights.extend([
                "Gold typically shows strength during geopolitical uncertainty",
                "Best trading hours overlap with European and US sessions",
                "Seasonal strength often seen in late summer/early fall"
            ])
        elif symbol.upper() == 'XAGUSD':
            insights.extend([
                "Silver shows higher volatility than gold due to industrial demand",
                "Technology sector performance affects silver prices",
                "Often leads gold during momentum phases"
            ])
        
        return insights
    
    def _generate_trading_recommendations(self, symbol: str) -> List[str]:
        """Trading tavsiyalar"""
        recommendations = [
            "Monitor economic calendar for inflation-related news",
            "Watch USD strength as primary driver for metal prices",
            "Use volatility-adjusted position sizing"
        ]
        
        if symbol.upper() in ['XPTUSD', 'XPDUSD']:
            recommendations.append("Auto industry data is particularly important for platinum group metals")
        
        return recommendations