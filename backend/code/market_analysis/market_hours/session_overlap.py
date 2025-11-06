"""
Session Overlap Analysis Module
==============================

Session overlap tahlil moduli.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime, time, timedelta
from dataclasses import dataclass
import pytz
from ..utils.time_utils import TimeUtils
import warnings
warnings.filterwarnings('ignore')


@dataclass
class OverlapAnalysis:
    """Overlap tahlil ma'lumotlari"""
    overlap_type: str
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    volatility_score: float
    liquidity_score: float
    spread_score: float
    volume_multiplier: float
    trading_opportunities: List[str]
    risk_factors: List[str]


@dataclass
class OverlapPerformance:
    """Overlap performance metriklari"""
    overlap_name: str
    avg_volume: float
    avg_volatility: float
    avg_spread: float
    volume_consistency: float
    volatility_stability: float
    spread_tightness: float
    best_hours: List[int]
    worst_hours: List[int]


class SessionOverlapAnalyzer:
    """Session overlap analyzer"""
    
    def __init__(self):
        self.overlap_definitions = {
            'Europe_Asia': {
                'name': 'London-Tokyo Overlap',
                'start': time(8, 0),   # 08:00 UTC
                'end': time(9, 0),     # 09:00 UTC
                'duration_minutes': 60,
                'description': 'Brief overlap between European and Asian sessions',
                'characteristics': {
                    'volatility': 'medium',
                    'liquidity': 'medium_high',
                    'spread_conditions': 'moderate',
                    'volume_intensity': 'medium'
                },
                'best_pairs': ['EURJPY', 'GBPJPY', 'AUDJPY', 'EURUSD'],
                'trading_style': 'scalping_range',
                'risk_level': 'medium'
            },
            'Europe_America': {
                'name': 'London-New York Overlap',
                'start': time(13, 0),  # 13:00 UTC
                'end': time(17, 0),    # 17:00 UTC
                'duration_minutes': 240,
                'description': 'Major overlap between European and American sessions',
                'characteristics': {
                    'volatility': 'high',
                    'liquidity': 'excellent',
                    'spread_conditions': 'tight',
                    'volume_intensity': 'very_high'
                },
                'best_pairs': ['EURUSD', 'GBPUSD', 'USDCHF', 'USDCAD'],
                'trading_style': 'momentum_breakout',
                'risk_level': 'medium_high'
            },
            'America_Asia': {
                'name': 'New York-Tokyo Overlap',
                'start': time(1, 0),   # 01:00 UTC
                'end': time(2, 0),     # 02:00 UTC
                'duration_minutes': 60,
                'description': 'Very brief overlap between American and Asian sessions',
                'characteristics': {
                    'volatility': 'low',
                    'liquidity': 'low',
                    'spread_conditions': 'wide',
                    'volume_intensity': 'low'
                },
                'best_pairs': ['USDJPY', 'AUDUSD', 'NZDUSD'],
                'trading_style': 'breakout_confirmation',
                'risk_level': 'low'
            }
        }
        
        self.overlap_scoring = {
            'Europe_Asia': {
                'volatility_multiplier': 1.2,
                'liquidity_multiplier': 1.4,
                'spread_reduction': 0.85,
                'volume_boost': 1.5
            },
            'Europe_America': {
                'volatility_multiplier': 1.6,
                'liquidity_multiplier': 1.8,
                'spread_reduction': 0.75,
                'volume_boost': 2.2
            },
            'America_Asia': {
                'volatility_multiplier': 0.9,
                'liquidity_multiplier': 0.8,
                'spread_reduction': 1.15,
                'volume_boost': 0.9
            }
        }
    
    def identify_active_overlaps(self, current_time: datetime = None) -> List[OverlapAnalysis]:
        """Joriy vaqtda aktiv overlap larni aniqlash"""
        if current_time is None:
            current_time = TimeUtils.get_current_utc_time()
        
        active_overlaps = []
        
        for overlap_key, overlap_config in self.overlap_definitions.items():
            if self._is_overlap_active(current_time, overlap_config):
                analysis = self._create_overlap_analysis(overlap_key, overlap_config, current_time)
                active_overlaps.append(analysis)
        
        return active_overlaps
    
    def _is_overlap_active(self, current_time: datetime, overlap_config: Dict) -> bool:
        """Overlap aktiv yoki yo'qligini tekshirish"""
        current_time_only = current_time.time()
        start_time = overlap_config['start']
        end_time = overlap_config['end']
        
        # Handle overlaps that don't cross midnight (most common)
        if end_time > start_time:
            return start_time <= current_time_only <= end_time
        else:
            # Handle rare case of overlap crossing midnight
            return current_time_only >= start_time or current_time_only <= end_time
    
    def _create_overlap_analysis(self, overlap_key: str, overlap_config: Dict, 
                               current_time: datetime) -> OverlapAnalysis:
        """Overlap analysis yaratish"""
        scoring = self.overlap_scoring.get(overlap_key, {})
        
        # Calculate scores (simplified)
        volatility_score = scoring.get('volatility_multiplier', 1.0) * 10
        liquidity_score = scoring.get('liquidity_multiplier', 1.0) * 10
        spread_score = (1 / scoring.get('spread_reduction', 1.0)) * 10
        volume_multiplier = scoring.get('volume_boost', 1.0)
        
        # Generate trading opportunities
        trading_opportunities = self._generate_trading_opportunities(overlap_key, overlap_config)
        
        # Generate risk factors
        risk_factors = self._generate_risk_factors(overlap_key, overlap_config)
        
        return OverlapAnalysis(
            overlap_type=overlap_key,
            start_time=datetime.combine(current_time.date(), overlap_config['start'], tzinfo=pytz.UTC),
            end_time=datetime.combine(current_time.date(), overlap_config['end'], tzinfo=pytz.UTC),
            duration_minutes=overlap_config['duration_minutes'],
            volatility_score=volatility_score,
            liquidity_score=liquidity_score,
            spread_score=spread_score,
            volume_multiplier=volume_multiplier,
            trading_opportunities=trading_opportunities,
            risk_factors=risk_factors
        )
    
    def _generate_trading_opportunities(self, overlap_key: str, overlap_config: Dict) -> List[str]:
        """Trading imkoniyatlarini yaratish"""
        opportunities = []
        
        characteristics = overlap_config.get('characteristics', {})
        
        if characteristics.get('volatility') == 'high':
            opportunities.extend([
                'Momentum trading imkoniyatlari',
                'Breakout strategies',
                'News-driven price moves'
            ])
        
        if characteristics.get('liquidity') in ['excellent', 'medium_high']:
            opportunities.extend([
                'Large position sizes mumkin',
                'Better execution prices',
                'Minimal slippage'
            ])
        
        if characteristics.get('volume_intensity') in ['very_high', 'medium']:
            opportunities.extend([
                'Yaxshi volume movements',
                'Clear market direction',
                'Institutional activity'
            ])
        
        # Specific to overlap type
        if overlap_key == 'Europe_America':
            opportunities.extend([
                'US economic data releases',
                'Major news announcements',
                'Central bank communications'
            ])
        elif overlap_key == 'Europe_Asia':
            opportunities.extend([
                'JPY crosses movement',
                'Asian market openings',
                'Currency intervention news'
            ])
        
        return opportunities
    
    def _generate_risk_factors(self, overlap_key: str, overlap_config: Dict) -> List[str]:
        """Risk factorlarni yaratish"""
        risks = []
        
        characteristics = overlap_config.get('characteristics', {})
        risk_level = characteristics.get('risk_level', 'medium')
        
        if risk_level in ['high', 'medium_high']:
            risks.extend([
                'Yuqori volatilite - katta harakatlar',
                'Rapid price changes',
                'Wide intraday ranges'
            ])
        
        if characteristics.get('liquidity') == 'excellent':
            risks.extend([
                'Institutional competition',
                'Large order flow',
                'Potential whipsaws'
            ])
        
        # Overlap-specific risks
        if overlap_key == 'Europe_America':
            risks.extend([
                'US economic data impact',
                'Fed communications',
                'Major news releases'
            ])
        
        return risks
    
    def analyze_overlap_performance(self, data: pd.DataFrame) -> Dict[str, OverlapPerformance]:
        """Overlap performance tahlili"""
        if data.empty or 'close' not in data.columns:
            return {}
        
        # Add overlap information to data
        data_with_overlaps = self._add_overlap_info(data)
        
        performance_metrics = {}
        
        for overlap_type in data_with_overlaps['overlap_active'].unique():
            if overlap_type == 'None':
                continue
            
            overlap_data = data_with_overlaps[data_with_overlaps['overlap_active'] == overlap_type]
            
            if len(overlap_data) < 10:
                continue
            
            # Calculate metrics
            returns = overlap_data['close'].pct_change().dropna()
            
            avg_volume = overlap_data['volume'].mean() if 'volume' in overlap_data.columns else 0
            avg_volatility = returns.std() if not returns.empty else 0
            avg_spread = ((overlap_data['high'] - overlap_data['low']) / overlap_data['close'] * 10000).mean() if all(col in overlap_data.columns for col in ['high', 'low', 'close']) else 0
            
            # Consistency measures
            volume_cv = overlap_data['volume'].std() / overlap_data['volume'].mean() if overlap_data['volume'].mean() > 0 else 0
            volume_consistency = 1 / (1 + volume_cv)
            
            volatility_cv = returns.std() / returns.mean() if returns.mean() > 0 else 0
            volatility_stability = 1 / (1 + volatility_cv)
            
            spread_cv = ((overlap_data['high'] - overlap_data['low']) / overlap_data['close'] * 10000).std() / avg_spread if avg_spread > 0 else 0
            spread_tightness = 1 / (1 + spread_cv)
            
            # Best and worst hours within overlap
            if isinstance(overlap_data.index, pd.DatetimeIndex):
                hourly_performance = overlap_data.groupby(overlap_data.index.hour).agg({
                    'close': 'std',
                    'volume': 'mean' if 'volume' in overlap_data.columns else lambda x: 0
                })
                
                best_hours = hourly_performance['close'].nsmallest(3).index.tolist() if not hourly_performance.empty else []
                worst_hours = hourly_performance['close'].nlargest(3).index.tolist() if not hourly_performance.empty else []
            else:
                best_hours = []
                worst_hours = []
            
            performance_metrics[overlap_type] = OverlapPerformance(
                overlap_name=overlap_type,
                avg_volume=avg_volume,
                avg_volatility=avg_volatility,
                avg_spread=avg_spread,
                volume_consistency=volume_consistency,
                volatility_stability=volatility_stability,
                spread_tightness=spread_tightness,
                best_hours=best_hours,
                worst_hours=worst_hours
            )
        
        return performance_metrics
    
    def _add_overlap_info(self, data: pd.DataFrame) -> pd.DataFrame:
        """Overlap ma'lumotlarini data ga qo'shish"""
        df = data.copy()
        
        # Ensure timestamp index
        if not isinstance(df.index, pd.DatetimeIndex):
            if 'timestamp' in df.columns:
                df = df.set_index('timestamp')
            else:
                df['overlap_active'] = 'None'
                return df
        
        # Add hour for overlap detection
        df['hour'] = df.index.hour
        
        # Determine overlap periods
        def get_overlap_type(hour):
            if 1 <= hour < 2:  # America-Asia overlap
                return 'America_Asia'
            elif 8 <= hour < 9:  # Europe-Asia overlap
                return 'Europe_Asia'
            elif 13 <= hour < 17:  # Europe-America overlap
                return 'Europe_America'
            else:
                return 'None'
        
        df['overlap_active'] = df['hour'].apply(get_overlap_type)
        
        return df
    
    def calculate_overlap_trading_scores(self, symbol: str,
                                       overlap_type: str) -> Dict[str, float]:
        """Overlap trading score hisoblash"""
        if overlap_type not in self.overlap_definitions:
            return {}
        
        overlap_config = self.overlap_definitions[overlap_type]
        best_pairs = overlap_config.get('best_pairs', [])
        
        # Symbol compatibility score
        symbol_compatibility = 1.0 if symbol.upper() in best_pairs else 0.7
        
        # Overlap characteristics scoring
        characteristics = overlap_config.get('characteristics', {})
        
        volatility_score = {
            'low': 6, 'medium': 8, 'high': 9
        }.get(characteristics.get('volatility', 'medium'), 7)
        
        liquidity_score = {
            'low': 4, 'medium_high': 8, 'excellent': 10
        }.get(characteristics.get('liquidity', 'medium'), 7)
        
        spread_score = {
            'wide': 4, 'moderate': 7, 'tight': 9
        }.get(characteristics.get('spread_conditions', 'moderate'), 7)
        
        # Overall trading score
        overall_score = (symbol_compatibility * 0.3 + 
                        volatility_score * 0.25 + 
                        liquidity_score * 0.25 + 
                        spread_score * 0.2)
        
        return {
            'overall_trading_score': overall_score,
            'symbol_compatibility': symbol_compatibility * 10,
            'volatility_potential': volatility_score,
            'liquidity_availability': liquidity_score,
            'execution_quality': spread_score,
            'risk_level': overlap_config.get('risk_level', 'medium'),
            'recommended_style': overlap_config.get('trading_style', 'moderate'),
            'expected_spread_reduction': self.overlap_scoring.get(overlap_type, {}).get('spread_reduction', 1.0)
        }
    
    def optimize_overlap_trading_strategy(self, symbol: str,
                                        risk_tolerance: str = 'medium',
                                        overlap_type: str = 'Europe_America') -> Dict[str, any]:
        """Overlap trading strategiyasini optimallash"""
        overlap_config = self.overlap_definitions.get(overlap_type, {})
        trading_scores = self.calculate_overlap_trading_scores(symbol, overlap_type)
        
        if not trading_scores:
            return {'status': 'invalid_overlap_type'}
        
        # Risk-based adjustments
        risk_multipliers = {
            'low': {'position_size': 1.5, 'stop_loss': 0.7},
            'medium': {'position_size': 1.0, 'stop_loss': 1.0},
            'high': {'position_size': 0.7, 'stop_loss': 1.3}
        }
        
        risk_adj = risk_multipliers.get(risk_tolerance, risk_multipliers['medium'])
        
        # Trading style recommendations
        trading_styles = {
            'scalping_range': {
                'holding_period': 'minutes',
                'position_size_multiplier': 0.8,
                'stop_loss_pips': 10,
                'take_profit_pips': 15,
                'max_trades_per_hour': 5
            },
            'momentum_breakout': {
                'holding_period': 'hours',
                'position_size_multiplier': 1.2,
                'stop_loss_pips': 25,
                'take_profit_pips': 50,
                'max_trades_per_hour': 2
            },
            'breakout_confirmation': {
                'holding_period': 'minutes_hours',
                'position_size_multiplier': 1.0,
                'stop_loss_pips': 20,
                'take_profit_pips': 30,
                'max_trades_per_hour': 3
            }
        }
        
        style_config = trading_styles.get(
            overlap_config.get('trading_style', 'moderate'), 
            trading_styles['momentum_breakout']
        )
        
        # Calculate optimal parameters
        base_position_size = risk_adj['position_size'] * style_config['position_size_multiplier']
        adjusted_stop_loss = style_config['stop_loss_pips'] * risk_adj['stop_loss']
        
        strategy = {
            'overlap_type': overlap_type,
            'symbol': symbol,
            'trading_style': style_config,
            'position_size_recommendation': base_position_size,
            'stop_loss_pips': adjusted_stop_loss,
            'take_profit_pips': style_config['take_profit_pips'],
            'max_trades_per_hour': style_config['max_trades_per_hour'],
            'risk_factors': overlap_config.get('risk_level', 'medium'),
            'optimal_pairs': overlap_config.get('best_pairs', []),
            'time_window': f"{overlap_config['start'].strftime('%H:%M')} - {overlap_config['end'].strftime('%H:%M')} UTC",
            'expected_improvements': {
                'volume_increase': self.overlap_scoring.get(overlap_type, {}).get('volume_boost', 1.0),
                'spread_improvement': self.overlap_scoring.get(overlap_type, {}).get('spread_reduction', 1.0),
                'liquidity_boost': self.overlap_scoring.get(overlap_type, {}).get('liquidity_multiplier', 1.0)
            }
        }
        
        return strategy
    
    def get_overlap_schedule(self, date: datetime = None) -> Dict[str, Dict]:
        """Overlap schedule olish"""
        if date is None:
            date = datetime.now().date()
        
        schedule = {}
        
        for overlap_key, overlap_config in self.overlap_definitions.items():
            start_datetime = datetime.combine(date, overlap_config['start'], tzinfo=pytz.UTC)
            end_datetime = datetime.combine(date, overlap_config['end'], tzinfo=pytz.UTC)
            
            # Handle overlaps that cross midnight
            if overlap_config['end'] <= overlap_config['start']:
                end_datetime += timedelta(days=1)
            
            schedule[overlap_key] = {
                'name': overlap_config['name'],
                'start_time': start_datetime,
                'end_time': end_datetime,
                'duration_hours': overlap_config['duration_minutes'] / 60,
                'description': overlap_config['description'],
                'characteristics': overlap_config['characteristics'],
                'best_pairs': overlap_config['best_pairs'],
                'trading_style': overlap_config['trading_style'],
                'risk_level': overlap_config['risk_level']
            }
        
        return schedule
    
    def create_overlap_trading_calendar(self, start_date: datetime, 
                                      end_date: datetime) -> pd.DataFrame:
        """Overlap trading calendar yaratish"""
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        calendar_data = []
        
        for date in date_range:
            for overlap_key, overlap_config in self.overlap_definitions.items():
                # Calculate overlap start and end for this date
                overlap_start = datetime.combine(date, overlap_config['start'], tzinfo=pytz.UTC)
                overlap_end = datetime.combine(date, overlap_config['end'], tzinfo=pytz.UTC)
                
                # Handle overlaps crossing midnight
                if overlap_config['end'] <= overlap_config['start']:
                    overlap_end += timedelta(days=1)
                
                calendar_data.append({
                    'date': date.date(),
                    'overlap_type': overlap_key,
                    'overlap_name': overlap_config['name'],
                    'start_time': overlap_start,
                    'end_time': overlap_end,
                    'duration_hours': overlap_config['duration_minutes'] / 60,
                    'trading_score': self._calculate_trading_score(overlap_key),
                    'best_for': ', '.join(overlap_config.get('best_pairs', [])),
                    'risk_level': overlap_config.get('risk_level', 'medium'),
                    'characteristics_summary': f"{overlap_config['characteristics'].get('volatility', 'medium')} volatility, {overlap_config['characteristics'].get('liquidity', 'medium')} liquidity"
                })
        
        calendar_df = pd.DataFrame(calendar_data)
        return calendar_df
    
    def _calculate_trading_score(self, overlap_key: str) -> float:
        """Overlap trading score hisoblash"""
        scoring_config = self.overlap_scoring.get(overlap_key, {})
        
        # Composite score based on liquidity, volume, and spread improvements
        liquidity_score = scoring_config.get('liquidity_multiplier', 1.0) * 5
        volume_score = scoring_config.get('volume_boost', 1.0) * 3
        spread_score = (1 / scoring_config.get('spread_reduction', 1.0)) * 2
        
        return min(10, liquidity_score + volume_score + spread_score)
    
    def analyze_overlap_market_impact(self, overlap_type: str,
                                    trade_size: float) -> Dict[str, float]:
        """Overlap market impact tahlili"""
        if overlap_type not in self.overlap_scoring:
            return {}
        
        scoring = self.overlap_scoring[overlap_type]
        
        # Base market impact estimates
        base_impact_1M = 0.5  # 0.5% impact for $1M trade in normal conditions
        
        # Apply overlap adjustments
        liquidity_adjustment = 1 / scoring.get('liquidity_multiplier', 1.0)
        volume_adjustment = 1 / scoring.get('volume_boost', 1.0)
        spread_adjustment = 1 / (scoring.get('spread_reduction', 1.0) ** 0.5)
        
        adjusted_impact = base_impact_1M * liquidity_adjustment * volume_adjustment * spread_adjustment
        
        # Calculate for different trade sizes
        trade_sizes = [100000, 500000, 1000000, 5000000, 10000000]  # $100K to $10M
        impact_analysis = {}
        
        for size in trade_sizes:
            size_ratio = size / 1000000  # Normalize to $1M
            impact_for_size = adjusted_impact * (size_ratio ** 0.6)  # Square root scaling
            impact_analysis[f'{size//1000}K'] = impact_for_size
        
        return {
            'base_impact_1M_usd': adjusted_impact,
            'impact_by_size': impact_analysis,
            'liquidity_improvement': scoring.get('liquidity_multiplier', 1.0),
            'volume_improvement': scoring.get('volume_boost', 1.0),
            'spread_reduction': scoring.get('spread_reduction', 1.0),
            'trading_recommendation': self._get_trading_recommendation(overlap_type, trade_size)
        }
    
    def _get_trading_recommendation(self, overlap_type: str, trade_size: float) -> str:
        """Trading tavsiyasi"""
        if overlap_type == 'Europe_America':
            if trade_size >= 5000000:
                return 'Excellent conditions for large institutional trades'
            else:
                return 'Optimal for active retail trading'
        elif overlap_type == 'Europe_Asia':
            return 'Good for JPY pairs and range trading'
        else:
            return 'Conservative approach recommended'
    
    def generate_overlap_alerts(self, current_time: datetime = None) -> List[Dict]:
        """Overlap ogohlantirishlari"""
        if current_time is None:
            current_time = TimeUtils.get_current_utc_time()
        
        alerts = []
        
        # Check for upcoming overlaps
        overlaps = self.get_overlap_schedule(current_time.date())
        
        for overlap_key, overlap_info in overlaps.items():
            time_until = overlap_info['start_time'] - current_time
            
            # Alert if overlap starting soon (within 30 minutes)
            if 0 < time_until.total_seconds() < 1800:
                alerts.append({
                    'type': 'overlap_starting',
                    'overlap': overlap_key,
                    'time_until_minutes': int(time_until.total_seconds() / 60),
                    'message': f"{overlap_info['name']} boshlanishiga {int(time_until.total_seconds() / 60)} daqiqa qoldi",
                    'action': 'Prepare for increased volatility and liquidity'
                })
            
            # Alert if overlap ending soon (within 15 minutes)
            time_until_end = overlap_info['end_time'] - current_time
            if 0 < time_until_end.total_seconds() < 900:
                alerts.append({
                    'type': 'overlap_ending',
                    'overlap': overlap_key,
                    'time_until_minutes': int(time_until_end.total_seconds() / 60),
                    'message': f"{overlap_info['name']} tugashiga {int(time_until_end.total_seconds() / 60)} daqiqa qoldi",
                    'action': 'Consider reducing position sizes'
                })
        
        # Current overlap status
        active_overlaps = self.identify_active_overlaps(current_time)
        
        if active_overlaps:
            for overlap in active_overlaps:
                if overlap.volatility_score > 14:  # High volatility threshold
                    alerts.append({
                        'type': 'high_volatility',
                        'overlap': overlap.overlap_type,
                        'message': f"{overlap.overlap_type} overlap yuqori volatilite: {overlap.volatility_score:.1f}/20",
                        'action': 'Exercise caution with position sizing'
                    })
        
        return alerts