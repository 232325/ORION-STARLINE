"""
Slippage Calculation Module
==========================

Slippage hisoblash moduli.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


@dataclass
class SlippageResult:
    """Slippage natija"""
    expected_slippage: float
    slippage_bps: float
    confidence_interval: Tuple[float, float]
    market_impact_cost: float
    liquidity_score: float
    execution_difficulty: str


@dataclass
class TradeImpact:
    """Trade impact ma'lumotlari"""
    trade_size: float
    expected_price_move: float
    final_execution_price: float
    slippage_cost: float
    market_impact_levels: List[float]


class SlippageCalculator:
    """Slippage hisoblash moduli"""
    
    def __init__(self):
        self.models = {
            'forex_major': RandomForestRegressor(n_estimators=100, random_state=42),
            'forex_minor': RandomForestRegressor(n_estimators=100, random_state=42),
            'metals': RandomForestRegressor(n_estimators=100, random_state=42),
            'crypto': RandomForestRegressor(n_estimators=100, random_state=42)
        }
        
        self.scalers = {}
        self.is_fitted = False
        self.market_conditions = {}
        
    def calculate_base_slippage(self, trade_size: float, avg_volume: float,
                              volatility: float, spread_bps: float) -> float:
        """Asosiy slippage hisoblash"""
        if avg_volume <= 0:
            return 0.0
        
        # Volume pressure ratio
        volume_ratio = trade_size / avg_volume
        
        # Base slippage model components
        base_slippage = (
            spread_bps * 0.1 +  # Base spread contribution
            (volume_ratio ** 0.5) * spread_bps * 0.5 +  # Volume-based impact
            volatility * 100 * volume_ratio * 0.3  # Volatility contribution
        )
        
        return base_slippage
    
    def calculate_market_condition_adjustments(self, base_slippage: float,
                                             market_conditions: Dict[str, float]) -> float:
        """Market shartlariga qarab slippage moslashtirish"""
        adjustments = 1.0
        
        # Liquidity adjustment
        liquidity_score = market_conditions.get('liquidity_score', 1.0)
        if liquidity_score < 0.5:
            adjustments *= 1.5  # 50% more slippage in low liquidity
        elif liquidity_score > 1.5:
            adjustments *= 0.8  # 20% less slippage in high liquidity
        
        # Time of day adjustment
        hour = market_conditions.get('hour', 12)
        if 8 <= hour <= 17:  # European/American overlap
            adjustments *= 0.7  # Lower slippage
        elif 0 <= hour <= 8:  # Asian session
            adjustments *= 1.3  # Higher slippage
        else:
            adjustments *= 1.1  # Medium slippage
        
        # News event adjustment
        is_news_time = market_conditions.get('is_news_time', False)
        if is_news_time:
            adjustments *= 1.8  # High slippage during news
        
        # Market stress adjustment
        market_stress = market_conditions.get('market_stress', 0.0)
        adjustments *= (1 + market_stress * 0.5)
        
        return base_slippage * adjustments
    
    def calculate_implementation_shortfall(self, trade_size: float, 
                                         execution_time: float,
                                         benchmark_price: float,
                                         order_book_depth: float) -> float:
        """Implementation shortfall hisoblash"""
        if order_book_depth <= 0:
            return trade_size * 0.001  # Default 0.1%
        
        # Time decay component (longer execution = more slippage)
        time_component = np.log1p(execution_time / 60) * 0.1  # Normalize to minutes
        
        # Size component
        size_ratio = trade_size / order_book_depth
        size_component = (size_ratio ** 0.7) * 0.5
        
        # Market impact component
        impact_component = self.calculate_market_impact_component(trade_size, order_book_depth)
        
        total_shortfall = (time_component + size_component + impact_component) * benchmark_price
        
        return total_shortfall
    
    def calculate_market_impact_component(self, trade_size: float, 
                                        order_book_depth: float) -> float:
        """Market impact komponenti hisoblash"""
        if order_book_depth <= 0:
            return 0.01  # Default 1% impact
        
        # Square root model for market impact
        impact_ratio = trade_size / order_book_depth
        
        # Impact grows with square root of volume ratio
        market_impact = 0.01 * (impact_ratio ** 0.5)  # 1% base impact
        
        # Cap at reasonable levels
        return min(market_impact, 0.1)  # Max 10% impact
    
    def calculate_trader_specific_slippage(self, trade_size: float,
                                         trader_characteristics: Dict[str, float],
                                         market_data: pd.DataFrame) -> float:
        """Trader-specific slippage hisoblash"""
        base_slippage = self.calculate_base_slippage(
            trade_size=trade_size,
            avg_volume=market_data['volume'].mean(),
            volatility=market_data['close'].pct_change().std(),
            spread_bps=((market_data['high'] - market_data['low']) / market_data['close'] * 10000).mean()
        )
        
        # Trader skill factor
        trader_skill = trader_characteristics.get('avg_execution_quality', 1.0)
        
        # Historical slippage performance
        historical_avg = trader_characteristics.get('historical_slippage_bps', 0)
        if historical_avg > 0:
            trader_adjustment = historical_avg / base_slippage
        else:
            trader_adjustment = 1.0
        
        # Market familiarity (how often trader operates in this market)
        familiarity = trader_characteristics.get('market_familiarity', 0.5)
        trader_adjustment *= (2 - familiarity)  # Less familiar = more slippage
        
        return base_slippage * trader_adjustment
    
    def estimate_slippage_distribution(self, trade_size: float, 
                                     market_conditions: Dict[str, float],
                                     n_simulations: int = 1000) -> Dict[str, float]:
        """Slippage taqsimotini baholash (Monte Carlo)"""
        base_slippage = self.calculate_base_slippage(
            trade_size=trade_size,
            avg_volume=market_conditions.get('avg_volume', 1000000),
            volatility=market_conditions.get('volatility', 0.02),
            spread_bps=market_conditions.get('spread_bps', 1.5)
        )
        
        # Random variations for simulation
        np.random.seed(42)  # For reproducible results
        
        # Market condition variations
        volatility_var = market_conditions.get('volatility_var', 0.01)
        volume_var = market_conditions.get('volume_var', 0.2)
        spread_var = market_conditions.get('spread_var', 0.3)
        
        slippage_values = []
        
        for _ in range(n_simulations):
            # Add random variations
            varied_volatility = market_conditions['volatility'] * (1 + np.random.normal(0, volatility_var))
            varied_volume = market_conditions['avg_volume'] * (1 + np.random.normal(0, volume_var))
            varied_spread = market_conditions['spread_bps'] * (1 + np.random.normal(0, spread_var))
            
            varied_slippage = self.calculate_base_slippage(
                trade_size=trade_size,
                avg_volume=varied_volume,
                volatility=varied_volatility,
                spread_bps=varied_spread
            )
            
            # Apply market condition adjustments
            varied_conditions = market_conditions.copy()
            varied_conditions['volatility'] = varied_volatility
            varied_conditions['avg_volume'] = varied_volume
            varied_conditions['spread_bps'] = varied_spread
            
            adjusted_slippage = self.calculate_market_condition_adjustments(
                varied_slippage, varied_conditions
            )
            
            slippage_values.append(adjusted_slippage)
        
        slippage_array = np.array(slippage_values)
        
        return {
            'mean': float(np.mean(slippage_array)),
            'median': float(np.median(slippage_array)),
            'std': float(np.std(slippage_array)),
            'min': float(np.min(slippage_array)),
            'max': float(np.max(slippage_array)),
            'percentile_5': float(np.percentile(slippage_array, 5)),
            'percentile_95': float(np.percentile(slippage_array, 95)),
            'prob_exceed_1pct': float(np.mean(slippage_array > 1.0)),
            'prob_exceed_2pct': float(np.mean(slippage_array > 2.0)),
            'distribution': slippage_array.tolist()
        }
    
    def analyze_historical_slippage(self, trade_data: pd.DataFrame) -> Dict[str, float]:
        """Tarixiy slippage tahlili"""
        if trade_data.empty or 'slippage_bps' not in trade_data.columns:
            return {}
        
        slippage_values = trade_data['slippage_bps'].dropna()
        
        if slippage_values.empty:
            return {}
        
        analysis = {
            'mean_slippage_bps': slippage_values.mean(),
            'median_slippage_bps': slippage_values.median(),
            'std_slippage_bps': slippage_values.std(),
            'min_slippage_bps': slippage_values.min(),
            'max_slippage_bps': slippage_values.max(),
            'percentile_25': slippage_values.quantile(0.25),
            'percentile_75': slippage_values.quantile(0.75),
            'percentile_95': slippage_values.quantile(0.95),
            'percentile_99': slippage_values.quantile(0.99),
            'skewness': float(slippage_values.skew()),
            'kurtosis': float(slippage_values.kurtosis())
        }
        
        # Trade size correlation
        if 'trade_size' in trade_data.columns:
            size_correlation = slippage_values.corr(trade_data['trade_size'])
            analysis['size_correlation'] = float(size_correlation)
        
        # Volume correlation
        if 'volume' in trade_data.columns:
            volume_correlation = slippage_values.corr(trade_data['volume'])
            analysis['volume_correlation'] = float(volume_correlation)
        
        # Time-based patterns
        if 'timestamp' in trade_data.index or 'hour' in trade_data.columns:
            analysis['time_patterns'] = self._analyze_slippage_time_patterns(trade_data)
        
        return analysis
    
    def _analyze_slippage_time_patterns(self, trade_data: pd.DataFrame) -> Dict[str, any]:
        """Vaqt bo'yicha slippage patternlari"""
        if 'timestamp' in trade_data.index:
            trade_data['hour'] = trade_data.index.hour
        elif 'hour' not in trade_data.columns:
            return {}
        
        hourly_stats = trade_data.groupby('hour')['slippage_bps'].agg([
            'mean', 'std', 'count'
        ]).round(4)
        
        return {
            'hourly_statistics': hourly_stats.to_dict('index'),
            'best_hours': hourly_stats['mean'].nsmallest(3).index.tolist(),
            'worst_hours': hourly_stats['mean'].nlargest(3).index.tolist(),
            'most_variable_hours': hourly_stats['std'].nlargest(3).index.tolist()
        }
    
    def optimize_execution_size(self, target_slippage_bps: float,
                              max_trade_size: float,
                              market_conditions: Dict[str, float]) -> Dict[str, float]:
        """Optimal trade size ni topish"""
        def objective(size):
            slippage = self.calculate_base_slippage(
                trade_size=size,
                avg_volume=market_conditions.get('avg_volume', 1000000),
                volatility=market_conditions.get('volatility', 0.02),
                spread_bps=market_conditions.get('spread_bps', 1.5)
            )
            return abs(slippage - target_slippage_bps)
        
        # Binary search for optimal size
        low, high = 1, max_trade_size
        
        for _ in range(50):  # 50 iterations
            mid = (low + high) / 2
            mid_slippage = self.calculate_base_slippage(
                trade_size=mid,
                avg_volume=market_conditions.get('avg_volume', 1000000),
                volatility=market_conditions.get('volatility', 0.02),
                spread_bps=market_conditions.get('spread_bps', 1.5)
            )
            
            if mid_slippage < target_slippage_bps:
                low = mid
            else:
                high = mid
        
        optimal_size = mid
        
        return {
            'optimal_size': optimal_size,
            'expected_slippage_bps': mid_slippage,
            'target_slippage_bps': target_slippage_bps,
            'feasible': True,
            'size_as_pct_of_volume': optimal_size / market_conditions.get('avg_volume', 1000000) * 100
        }
    
    def calculate_cost_benefit_analysis(self, strategies: List[Dict],
                                      total_volume: float) -> Dict[str, any]:
        """Cost-benefit tahlili"""
        analysis = {}
        
        for strategy in strategies:
            strategy_name = strategy.get('name', 'unknown')
            execution_cost = strategy.get('execution_cost', 0)
            opportunity_cost = strategy.get('opportunity_cost', 0)
            risk_cost = strategy.get('risk_cost', 0)
            
            total_cost = execution_cost + opportunity_cost + risk_cost
            cost_per_unit = total_cost / total_volume if total_volume > 0 else 0
            
            analysis[strategy_name] = {
                'total_cost': total_cost,
                'cost_per_unit': cost_per_unit,
                'execution_cost': execution_cost,
                'opportunity_cost': opportunity_cost,
                'risk_cost': risk_cost,
                'cost_components': {
                    'execution_pct': (execution_cost / total_cost * 100) if total_cost > 0 else 0,
                    'opportunity_pct': (opportunity_cost / total_cost * 100) if total_cost > 0 else 0,
                    'risk_pct': (risk_cost / total_cost * 100) if total_cost > 0 else 0
                }
            }
        
        # Find most cost-effective strategy
        if analysis:
            best_strategy = min(analysis.items(), key=lambda x: x[1]['total_cost'])
            analysis['recommended_strategy'] = {
                'name': best_strategy[0],
                'total_cost': best_strategy[1]['total_cost']
            }
        
        return analysis
    
    def generate_slippage_alerts(self, current_slippage: float,
                               historical_avg: float,
                               thresholds: Dict[str, float]) -> List[Dict]:
        """Slippage ogohlantirishlari"""
        alerts = []
        
        # High slippage alert
        if current_slippage > thresholds.get('high_threshold', historical_avg * 2):
            alerts.append({
                'type': 'high_slippage',
                'level': 'warning',
                'message': f'Joriy slippage ({current_slippage:.2f} bps)历史iy ortacha ({historical_avg:.2f} bps) dan yuqori',
                'value': current_slippage,
                'threshold': thresholds.get('high_threshold', historical_avg * 2),
                'action': 'Consider reducing trade size or waiting for better conditions'
            })
        
        # Unusual slippage spike
        if current_slippage > historical_avg + 3 * thresholds.get('std_threshold', 1.0):
            alerts.append({
                'type': 'slippage_spike',
                'level': 'critical',
                'message': f'Slippage keskin ko\'tarildi: {current_slippage:.2f} bps',
                'value': current_slippage,
                'baseline': historical_avg,
                'action': 'Stop trading immediately, investigate market conditions'
            })
        
        # Session-based alert
        current_hour = thresholds.get('current_hour', 12)
        session_thresholds = thresholds.get('session_thresholds', {})
        
        if current_hour in session_thresholds:
            session_threshold = session_thresholds[current_hour]
            if current_slippage > session_threshold:
                alerts.append({
                    'type': 'session_slippage',
                    'level': 'info',
                    'message': f'Joriy session ({current_hour}:00) uchun slippage yuqori',
                    'value': current_slippage,
                    'session_threshold': session_threshold,
                    'action': 'Consider switching to different session or reducing size'
                })
        
        return alerts
    
    def create_slippage_monitoring_dashboard(self, real_time_data: Dict,
                                           historical_baseline: Dict) -> Dict[str, any]:
        """Slippage monitoring dashboard"""
        current_slippage = real_time_data.get('current_slippage_bps', 0)
        current_volume = real_time_data.get('current_volume', 0)
        current_volatility = real_time_data.get('current_volatility', 0)
        current_spread = real_time_data.get('current_spread_bps', 0)
        
        # Current status
        status = 'normal'
        if current_slippage > historical_baseline.get('mean_slippage', 0) * 2:
            status = 'high'
        elif current_slippage > historical_baseline.get('mean_slippage', 0) * 1.5:
            status = 'elevated'
        
        # Risk assessment
        risk_factors = []
        if current_volume < historical_baseline.get('avg_volume', 1000000) * 0.5:
            risk_factors.append('Low liquidity')
        if current_volatility > historical_baseline.get('avg_volatility', 0.02) * 2:
            risk_factors.append('High volatility')
        if current_spread > historical_baseline.get('avg_spread', 1.5) * 1.5:
            risk_factors.append('Wide spreads')
        
        # Recommendations
        recommendations = []
        if status == 'high':
            recommendations.append('Reduce trade sizes significantly')
            recommendations.append('Wait for better market conditions')
        elif status == 'elevated':
            recommendations.append('Exercise caution with trade sizing')
            recommendations.append('Monitor market conditions closely')
        else:
            recommendations.append('Normal trading conditions')
        
        # Predictive insights
        predicted_slippage = current_slippage  # Simplified prediction
        if risk_factors:
            predicted_slippage *= 1.5  # Increase prediction if risk factors present
        
        dashboard = {
            'status': status,
            'current_metrics': {
                'slippage_bps': current_slippage,
                'volume_ratio': current_volume / historical_baseline.get('avg_volume', 1000000),
                'volatility_ratio': current_volatility / historical_baseline.get('avg_volatility', 0.02),
                'spread_ratio': current_spread / historical_baseline.get('avg_spread', 1.5)
            },
            'risk_assessment': {
                'risk_level': 'high' if len(risk_factors) >= 2 else 'medium' if len(risk_factors) == 1 else 'low',
                'risk_factors': risk_factors,
                'risk_score': len(risk_factors) * 25  # 0-100 scale
            },
            'recommendations': recommendations,
            'predictions': {
                'slippage_trend': 'increasing' if risk_factors else 'stable',
                'next_5min_predicted': predicted_slippage,
                'confidence': 0.8 if not risk_factors else 0.6
            },
            'historical_comparison': {
                'vs_mean': (current_slippage - historical_baseline.get('mean_slippage', 0)) / historical_baseline.get('mean_slippage', 1) * 100,
                'vs_p95': current_slippage / historical_baseline.get('percentile_95', current_slippage) * 100,
                'percentile_rank': self._calculate_percentile_rank(current_slippage, historical_baseline)
            }
        }
        
        return dashboard
    
    def _calculate_percentile_rank(self, value: float, baseline: Dict) -> float:
        """Qiymat percentile rank hisoblash"""
        mean = baseline.get('mean_slippage', value)
        std = baseline.get('std_slippage', 0)
        
        if std == 0:
            return 50.0  # Default to 50th percentile
        
        # Z-score based percentile
        z_score = (value - mean) / std
        percentile = 50 + 50 * (1 + np.sign(z_score) * np.sqrt(1 - np.exp(-2 * z_score**2 / np.pi)))
        
        return max(0, min(100, percentile))