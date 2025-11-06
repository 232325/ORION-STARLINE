"""
Inventory Effects Module
========================

Metal bozorlaridagi inventory ta'sir tahlili.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class InventoryAnalyzer:
    """Inventory effects tahlil moduli"""
    
    def __init__(self):
        self.inventory_indicators = {
            'gold': {
                'etf_flows': True,
                'central_bank_purchases': True,
                'jewelry_demand': True,
                'technology_demand': False,
                'physical_supply': True
            },
            'silver': {
                'etf_flows': True,
                'central_bank_purchases': False,
                'jewelry_demand': True,
                'technology_demand': True,
                'physical_supply': True
            },
            'platinum': {
                'etf_flows': True,
                'central_bank_purchases': False,
                'jewelry_demand': False,
                'technology_demand': False,
                'physical_supply': True,
                'auto_catalyst_demand': True
            },
            'palladium': {
                'etf_flows': True,
                'central_bank_purchases': False,
                'jewelry_demand': False,
                'technology_demand': False,
                'physical_supply': True,
                'auto_catalyst_demand': True
            }
        }
    
    def analyze_inventory_impact(self, symbol: str, data: pd.DataFrame, 
                               inventory_data: pd.DataFrame = None) -> Dict[str, any]:
        """Inventory ta'sirini tahlil qilish"""
        if data.empty:
            return {}
        
        analysis = {
            'symbol': symbol,
            'inventory_sensitivity': self._assess_inventory_sensitivity(symbol),
            'supply_demand_balance': self._analyze_supply_demand(symbol, data),
            'inventory_trends': self._analyze_inventory_trends(data),
            'price_inventory_correlation': self._calculate_price_inventory_correlation(data),
            'seasonal_inventory_patterns': self._analyze_seasonal_inventory(data),
            'forward_curve_analysis': self._analyze_forward_curve(symbol, data)
        }
        
        return analysis
    
    def _assess_inventory_sensitivity(self, symbol: str) -> Dict[str, float]:
        """Inventory sezgirligini baholash"""
        metal_type = self._get_metal_type(symbol)
        indicators = self.inventory_indicators.get(metal_type, {})
        
        # Base sensitivity scores
        base_scores = {
            'etf_flows': 0.8 if indicators.get('etf_flows', False) else 0.3,
            'physical_demand': 0.7 if indicators.get('jewelry_demand', False) else 0.5,
            'industrial_demand': 0.6 if indicators.get('technology_demand', False) else 0.4,
            'central_bank_activity': 0.9 if indicators.get('central_bank_purchases', False) else 0.2,
            'supply_constraints': 0.8 if indicators.get('physical_supply', False) else 0.5
        }
        
        return base_scores
    
    def _get_metal_type(self, symbol: str) -> str:
        """Metal turini aniqlash"""
        symbol_upper = symbol.upper()
        if 'XAU' in symbol_upper or 'GOLD' in symbol_upper:
            return 'gold'
        elif 'XAG' in symbol_upper or 'SILVER' in symbol_upper:
            return 'silver'
        elif 'XPT' in symbol_upper or 'PLATINUM' in symbol_upper:
            return 'platinum'
        elif 'XPD' in symbol_upper or 'PALLADIUM' in symbol_upper:
            return 'palladium'
        else:
            return 'gold'  # Default
    
    def _analyze_supply_demand(self, symbol: str, data: pd.DataFrame) -> Dict[str, float]:
        """Supply/demand muvozanatini tahlil qilish"""
        if len(data) < 30:
            return {'status': 'insufficient_data'}
        
        # Price trend analysis
        price_change = (data['close'].iloc[-1] / data['close'].iloc[0] - 1) * 100
        volatility = data['close'].pct_change().std() * 100
        
        # Volume analysis
        avg_volume = data['volume'].mean()
        recent_volume = data['volume'].tail(10).mean()
        volume_trend = (recent_volume / avg_volume - 1) * 100
        
        # Simple supply/demand indicators
        demand_pressure = volume_trend * 0.5 + price_change * 0.3
        supply_pressure = -price_change * 0.2 + volatility * 0.1
        
        return {
            'demand_pressure': demand_pressure,
            'supply_pressure': supply_pressure,
            'net_supply_demand': demand_pressure - supply_pressure,
            'price_trend_pct': price_change,
            'volume_trend_pct': volume_trend,
            'volatility_level': volatility
        }
    
    def _analyze_inventory_trends(self, data: pd.DataFrame) -> Dict[str, float]:
        """Inventory trendlarini tahlil qilish"""
        if len(data) < 20:
            return {'status': 'insufficient_data'}
        
        # Rolling averages
        price_ma20 = data['close'].rolling(20).mean()
        volume_ma20 = data['volume'].rolling(20).mean()
        
        # Trend indicators
        price_trend = (price_ma20.iloc[-1] / price_ma20.iloc[0] - 1) * 100
        volume_trend = (volume_ma20.iloc[-1] / volume_ma20.iloc[0] - 1) * 100
        
        # Inventory build/drain indicators
        if 'close' in data.columns and 'volume' in data.columns:
            # Price increase with volume increase = demand-driven rally
            # Price increase with volume decrease = supply squeeze
            price_volume_correlation = data['close'].corr(data['volume'])
            
            inventory_signal = 'neutral'
            if price_volume_correlation > 0.3 and price_trend > 2:
                inventory_signal = 'demand_driven_rally'
            elif price_volume_correlation < -0.3 and price_trend > 2:
                inventory_signal = 'supply_squeeze'
            elif price_volume_correlation < -0.3 and price_trend < -2:
                inventory_signal = 'supply_overhang'
        else:
            inventory_signal = 'unknown'
        
        return {
            'price_trend_20d_pct': price_trend,
            'volume_trend_20d_pct': volume_trend,
            'price_volume_correlation': price_volume_correlation if 'price_volume_correlation' in locals() else 0,
            'inventory_signal': inventory_signal,
            'trend_strength': abs(price_trend) * 0.6 + abs(volume_trend) * 0.4
        }
    
    def _calculate_price_inventory_correlation(self, data: pd.DataFrame) -> Dict[str, float]:
        """Price va inventory o'rtasidagi korrelyatsiya"""
        if len(data) < 10:
            return {'status': 'insufficient_data'}
        
        correlations = {}
        
        # Price-volume correlation (proxy for inventory pressure)
        if 'volume' in data.columns:
            correlations['price_volume'] = data['close'].corr(data['volume'])
        
        # Price volatility correlation (supply/demand imbalance indicator)
        price_returns = data['close'].pct_change()
        correlations['price_volatility'] = price_returns.std()
        
        # Rolling correlations
        if len(data) >= 20:
            rolling_corr = data['close'].rolling(20).corr(data['volume'])
            correlations['rolling_price_volume'] = rolling_corr.iloc[-1]
        
        return correlations
    
    def _analyze_seasonal_inventory(self, data: pd.DataFrame) -> Dict[str, any]:
        """Seasonal inventory patternlari"""
        if not isinstance(data.index, pd.DatetimeIndex) or len(data) < 365:
            return {'status': 'insufficient_data_for_seasonal'}
        
        # Monthly patterns
        monthly_stats = {}
        for month in range(1, 13):
            month_data = data[data.index.month == month]
            if len(month_data) > 0:
                monthly_stats[f'month_{month}'] = {
                    'avg_volume': month_data['volume'].mean(),
                    'avg_price_change': month_data['close'].pct_change().mean() * 100,
                    'volatility': month_data['close'].pct_change().std() * 100,
                    'sample_size': len(month_data)
                }
        
        # Identify high inventory months
        if monthly_stats:
            volume_ranking = sorted(monthly_stats.items(), 
                                  key=lambda x: x[1]['avg_volume'], reverse=True)
            price_change_ranking = sorted(monthly_stats.items(),
                                        key=lambda x: x[1]['avg_price_change'], reverse=True)
            
            high_inventory_months = [month for month, _ in volume_ranking[:3]]
            strong_demand_months = [month for month, _ in price_change_ranking[:3]]
        else:
            high_inventory_months = []
            strong_demand_months = []
        
        return {
            'monthly_statistics': monthly_stats,
            'high_inventory_months': high_inventory_months,
            'strong_demand_months': strong_demand_months,
            'seasonal_pattern_strength': len(high_inventory_months) / 12
        }
    
    def _analyze_forward_curve(self, symbol: str, data: pd.DataFrame) -> Dict[str, any]:
        """Forward curve tahlili (simplified)"""
        if len(data) < 60:
            return {'status': 'insufficient_data_for_forward_curve'}
        
        # Use price momentum as proxy for forward curve
        short_term_momentum = (data['close'].tail(5).iloc[-1] / data['close'].tail(5).iloc[0] - 1) * 100
        medium_term_momentum = (data['close'].tail(20).iloc[-1] / data['close'].tail(20).iloc[0] - 1) * 100
        
        curve_signal = 'neutral'
        if short_term_momentum > 1 and medium_term_momentum > 2:
            curve_signal = 'steepening'
        elif short_term_momentum < -1 and medium_term_momentum < -2:
            curve_signal = 'flattening'
        
        return {
            'short_term_momentum_5d_pct': short_term_momentum,
            'medium_term_momentum_20d_pct': medium_term_momentum,
            'curve_signal': curve_signal,
            'contango_backwardation': curve_signal
        }
    
    def predict_inventory_impact(self, symbol: str, forecast_days: int = 30) -> Dict[str, any]:
        """Inventory ta'sirini bashoratlash"""
        base_prediction = {
            'forecast_period_days': forecast_days,
            'inventory_sensitivity': 'medium',
            'expected_price_impact': 'neutral',
            'key_catalysts': []
        }
        
        metal_type = self._get_metal_type(symbol)
        
        # Metal-specific predictions
        if metal_type == 'gold':
            base_prediction.update({
                'inventory_sensitivity': 'high',
                'expected_price_impact': 'positive',
                'key_catalysts': [
                    'Central bank gold purchases',
                    'ETF inflows',
                    'Geopolitical tensions',
                    'Inflation concerns'
                ]
            })
        elif metal_type == 'silver':
            base_prediction.update({
                'inventory_sensitivity': 'high',
                'expected_price_impact': 'positive',
                'key_catalysts': [
                    'Industrial demand growth',
                    'Technology sector strength',
                    'ETF activity',
                    'Solar panel demand'
                ]
            })
        elif metal_type == 'platinum':
            base_prediction.update({
                'inventory_sensitivity': 'medium',
                'expected_price_impact': 'neutral',
                'key_catalysts': [
                    'Auto sales data',
                    'Jewelry demand',
                    'Industrial consumption'
                ]
            })
        elif metal_type == 'palladium':
            base_prediction.update({
                'inventory_sensitivity': 'very_high',
                'expected_price_impact': 'volatile',
                'key_catalysts': [
                    'Auto catalyst demand',
                    'Supply disruptions',
                    'Inventory changes',
                    'Substitution with platinum'
                ]
            })
        
        return base_prediction
    
    def generate_inventory_report(self, symbol: str, data: pd.DataFrame) -> Dict[str, any]:
        """To'liq inventory hisoboti"""
        impact_analysis = self.analyze_inventory_impact(symbol, data)
        price_prediction = self.predict_inventory_impact(symbol, 30)
        
        report = {
            'symbol': symbol,
            'analysis_timestamp': datetime.now(),
            'inventory_analysis': impact_analysis,
            'forecast': price_prediction,
            'key_recommendations': self._generate_inventory_recommendations(symbol, impact_analysis)
        }
        
        return report
    
    def _generate_inventory_recommendations(self, symbol: str, analysis: Dict[str, any]) -> List[str]:
        """Inventory asosida tavsiyalar"""
        recommendations = []
        
        # Based on inventory sensitivity
        sensitivity = analysis.get('inventory_sensitivity', {})
        if sensitivity.get('central_bank_activity', 0) > 0.5:
            recommendations.append("Markaziy bank faoliyatini yaqindan kuzating")
        
        if sensitivity.get('etf_flows', 0) > 0.5:
            recommendations.append("ETF flow ma'lumotlarini kuzating")
        
        # Based on supply/demand analysis
        sd_balance = analysis.get('supply_demand_balance', {})
        if sd_balance.get('net_supply_demand', 0) > 1:
            recommendations.append("Talab bosimi yuqori - long pozitsiyalar uchun qulay")
        elif sd_balance.get('net_supply_demand', 0) < -1:
            recommendations.append("Taklif bosimi yuqori - ehtiyotkor bo'ling")
        
        # Based on inventory trends
        trends = analysis.get('inventory_trends', {})
        inventory_signal = trends.get('inventory_signal', 'neutral')
        
        if inventory_signal == 'supply_squeeze':
            recommendations.append("Taklif tanqisligi: Price rally kutish mumkin")
        elif inventory_signal == 'demand_driven_rally':
            recommendations.append("Talabga asoslangan rally: Davom etishi mumkin")
        elif inventory_signal == 'supply_overhang':
            recommendations.append("Taklif ortiqchaligi: Price pasayishi mumkin")
        
        return recommendations