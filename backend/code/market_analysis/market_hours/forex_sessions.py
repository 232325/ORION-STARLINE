"""
Forex Sessions Module
====================

Forex trading session management moduli.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime, time, timedelta
from dataclasses import dataclass
import pytz
from ..utils.time_utils import TimeUtils
from ..utils.config import FOREX_SESSIONS
import warnings
warnings.filterwarnings('ignore')


@dataclass
class SessionInfo:
    """Trading session ma'lumotlari"""
    name: str
    start_time: time
    end_time: time
    timezone: str
    is_active: bool
    volatility_multiplier: float
    liquidity_multiplier: float
    volume_expectation: float
    spread_expectation: float


@dataclass
class SessionMetrics:
    """Session performance metrics"""
    session_name: str
    avg_volume: float
    avg_volatility: float
    avg_spread: float
    volume_std: float
    volatility_std: float
    spread_std: float
    best_trading_hours: List[int]
    worst_trading_hours: List[int]


class ForexSessionManager:
    """Forex trading session manager"""
    
    def __init__(self):
        self.sessions = FOREX_SESSIONS
        self.timezone_offsets = {
            'UTC': 0,
            'Europe/London': 0,
            'Europe/Berlin': 1,
            'Europe/Paris': 1,
            'America/New_York': -5,
            'America/Chicago': -6,
            'America/Los_Angeles': -8,
            'Asia/Tokyo': 9,
            'Asia/Hong_Kong': 8,
            'Asia/Singapore': 8,
            'Australia/Sydney': 10,
            'Australia/Melbourne': 10
        }
        
        # Session characteristics
        self.session_characteristics = {
            'Asian': {
                'avg_spread_multiplier': 1.3,
                'volume_intensity': 0.6,
                'volatility_pattern': 'low_steady',
                'major_pairs_liquidity': 0.7,
                'cross_pairs_liquidity': 0.5,
                'exotic_pairs_liquidity': 0.3
            },
            'European': {
                'avg_spread_multiplier': 1.0,
                'volume_intensity': 1.2,
                'volatility_pattern': 'medium_high',
                'major_pairs_liquidity': 1.3,
                'cross_pairs_liquidity': 1.1,
                'exotic_pairs_liquidity': 0.8
            },
            'American': {
                'avg_spread_multiplier': 0.9,
                'volume_intensity': 1.4,
                'volatility_pattern': 'high_variable',
                'major_pairs_liquidity': 1.2,
                'cross_pairs_liquidity': 1.0,
                'exotic_pairs_liquidity': 0.7
            }
        }
    
    def get_current_session(self, current_time: datetime = None) -> SessionInfo:
        """Joriy active session ni olish"""
        if current_time is None:
            current_time = TimeUtils.get_current_utc_time()
        
        active_sessions = []
        
        for session_key, session_config in self.sessions.items():
            if self._is_session_active(current_time, session_config):
                active_sessions.append(session_key)
        
        # Determine primary session
        if len(active_sessions) == 0:
            # Low activity period
            return SessionInfo(
                name='Low_Activity',
                start_time=time(22, 0),  # 22:00 UTC
                end_time=time(0, 0),     # 00:00 UTC
                timezone='UTC',
                is_active=False,
                volatility_multiplier=0.5,
                liquidity_multiplier=0.4,
                volume_expectation=0.3,
                spread_expectation=1.5
            )
        elif len(active_sessions) == 1:
            # Single active session
            session_key = active_sessions[0]
            return self._create_session_info(session_key, self.sessions[session_key])
        else:
            # Overlap session
            return self._create_overlap_session_info(active_sessions)
    
    def _is_session_active(self, current_time: datetime, session_config) -> bool:
        """Session faol yoki yo'qligini tekshirish"""
        current_time_utc = current_time.astimezone(pytz.UTC)
        current_time_only = current_time_utc.time()
        
        start_time = session_config.start_time
        end_time = session_config.end_time
        
        # Handle sessions that cross midnight
        if end_time < start_time:
            return current_time_only >= start_time or current_time_only <= end_time
        else:
            return start_time <= current_time_only <= end_time
    
    def _create_session_info(self, session_name: str, session_config) -> SessionInfo:
        """Session info yaratish"""
        characteristics = self.session_characteristics.get(session_name, {})
        
        return SessionInfo(
            name=session_name,
            start_time=session_config.start_time,
            end_time=session_config.end_time,
            timezone=session_config.timezone,
            is_active=True,
            volatility_multiplier=session_config.volatility_multiplier,
            liquidity_multiplier=session_config.liquidity_multiplier,
            volume_expectation=characteristics.get('volume_intensity', 1.0),
            spread_expectation=characteristics.get('avg_spread_multiplier', 1.0)
        )
    
    def _create_overlap_session_info(self, active_sessions: List[str]) -> SessionInfo:
        """Overlap session info yaratish"""
        session_names = '_'.join(active_sessions) + '_Overlap'
        
        # Calculate combined metrics
        total_volatility = sum(self.session_characteristics.get(s, {}).get('volatility_multiplier', 1.0) 
                             for s in active_sessions)
        total_liquidity = sum(self.session_characteristics.get(s, {}).get('liquidity_multiplier', 1.0) 
                            for s in active_sessions)
        
        return SessionInfo(
            name=session_names,
            start_time=time(8, 0),   # Overlap start
            end_time=time(17, 0),    # Overlap end
            timezone='UTC',
            is_active=True,
            volatility_multiplier=total_volatility / len(active_sessions),
            liquidity_multiplier=total_liquidity / len(active_sessions),
            volume_expectation=1.8,  # High during overlap
            spread_expectation=0.8   # Tight during overlap
        )
    
    def get_session_schedule(self, target_date: datetime = None) -> Dict[str, Dict]:
        """Session schedule olish"""
        if target_date is None:
            target_date = datetime.now().date()
        
        schedule = {}
        
        for session_name, session_config in self.sessions.items():
            start_datetime = datetime.combine(
                target_date, session_config.start_time, tzinfo=pytz.UTC
            )
            
            # Handle sessions crossing midnight
            end_datetime = datetime.combine(
                target_date, session_config.end_time, tzinfo=pytz.UTC
            )
            
            if session_config.end_time <= session_config.start_time:
                end_datetime += timedelta(days=1)
            
            schedule[session_name] = {
                'start': start_datetime,
                'end': end_datetime,
                'duration_hours': (end_datetime - start_datetime).total_seconds() / 3600,
                'timezone': session_config.timezone,
                'volatility_multiplier': session_config.volatility_multiplier,
                'liquidity_multiplier': session_config.liquidity_multiplier
            }
        
        return schedule
    
    def analyze_session_performance(self, data: pd.DataFrame) -> Dict[str, SessionMetrics]:
        """Session performance tahlili"""
        if data.empty or 'close' not in data.columns:
            return {}
        
        # Ensure timestamp index
        if not isinstance(data.index, pd.DatetimeIndex):
            if 'timestamp' in data.columns:
                data = data.set_index('timestamp')
            else:
                return {}
        
        # Add session information
        data_with_sessions = TimeUtils.add_session_info(data)
        
        metrics = {}
        
        for session in data_with_sessions['session'].unique():
            session_data = data_with_sessions[data_with_sessions['session'] == session]
            
            if len(session_data) < 5:  # Need minimum data
                continue
            
            # Calculate session metrics
            returns = session_data['close'].pct_change().dropna()
            
            avg_volume = session_data['volume'].mean() if 'volume' in session_data.columns else 0
            avg_volatility = returns.std() if not returns.empty else 0
            avg_spread = ((session_data['high'] - session_data['low']) / session_data['close'] * 10000).mean() if all(col in session_data.columns for col in ['high', 'low', 'close']) else 0
            
            # Standard deviations
            volume_std = session_data['volume'].std() if 'volume' in session_data.columns else 0
            volatility_std = returns.rolling(20).std().std() if len(returns) > 20 else 0
            spread_std = ((session_data['high'] - session_data['low']) / session_data['close'] * 10000).std() if all(col in session_data.columns for col in ['high', 'low', 'close']) else 0
            
            # Best and worst trading hours (within session)
            if isinstance(session_data.index, pd.DatetimeIndex):
                hourly_volatility = session_data.groupby(session_data.index.hour)['close'].std()
                best_hours = hourly_volatility.nsmallest(3).index.tolist() if not hourly_volatility.empty else []
                worst_hours = hourly_volatility.nlargest(3).index.tolist() if not hourly_volatility.empty else []
            else:
                best_hours = []
                worst_hours = []
            
            metrics[session] = SessionMetrics(
                session_name=session,
                avg_volume=avg_volume,
                avg_volatility=avg_volatility,
                avg_spread=avg_spread,
                volume_std=volume_std,
                volatility_std=volatility_std,
                spread_std=spread_std,
                best_trading_hours=best_hours,
                worst_trading_hours=worst_hours
            )
        
        return metrics
    
    def get_optimal_trading_hours(self, symbol: str, 
                                analysis_period_days: int = 30) -> Dict[str, any]:
        """Optimal trading soatlarini aniqlash"""
        # This would use actual historical data in a real implementation
        # For now, return session-based recommendations
        
        major_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF']
        cross_pairs = ['EURJPY', 'EURGBP', 'GBPJPY', 'AUDJPY']
        
        if symbol.upper() in major_pairs:
            pair_type = 'major'
        elif symbol.upper() in cross_pairs:
            pair_type = 'cross'
        else:
            pair_type = 'exotic'
        
        # Base recommendations by pair type
        recommendations = {
            'major': {
                'optimal_sessions': ['European', 'American'],
                'optimal_hours': [9, 10, 13, 14, 15],  # UTC hours
                'avoid_hours': [1, 2, 3, 4, 5],       # Low activity
                'expected_spread_bps': 0.8,
                'expected_volume_ratio': 1.2
            },
            'cross': {
                'optimal_sessions': ['European'],
                'optimal_hours': [8, 9, 10, 11, 12],
                'avoid_hours': [0, 1, 2, 3, 22, 23],
                'expected_spread_bps': 1.2,
                'expected_volume_ratio': 0.8
            },
            'exotic': {
                'optimal_sessions': ['European'],
                'optimal_hours': [8, 9, 10],
                'avoid_hours': list(range(0, 8)) + list(range(18, 24)),
                'expected_spread_bps': 2.5,
                'expected_volume_ratio': 0.4
            }
        }
        
        # Get current session recommendations
        current_session = self.get_current_session()
        
        session_recommendation = {
            'current_session': current_session.name,
            'session_quality': 'excellent' if 'Overlap' in current_session.name else
                              'good' if current_session.name == 'European' else
                              'fair' if current_session.name == 'American' else
                              'poor',
            'trading_suitability': self._assess_session_suitability(current_session, pair_type),
            'expected_conditions': self._get_session_conditions(current_session, pair_type)
        }
        
        return {
            'pair_type': pair_type,
            'general_recommendations': recommendations[pair_type],
            'current_session': session_recommendation,
            'time_based_strategy': self._get_time_based_strategy(pair_type, current_session)
        }
    
    def _assess_session_suitability(self, session: SessionInfo, pair_type: str) -> str:
        """Session suitability assessment"""
        base_scores = {
            'Asian': {'major': 6, 'cross': 7, 'exotic': 5},
            'European': {'major': 9, 'cross': 9, 'exotic': 8},
            'American': {'major': 8, 'cross': 7, 'exotic': 6},
            'Overlap': {'major': 10, 'cross': 8, 'exotic': 7}
        }
        
        session_name = session.name.split('_')[0]  # Remove _Overlap suffix if present
        score = base_scores.get(session_name, {}).get(pair_type, 5)
        
        # Adjust based on session characteristics
        score *= session.liquidity_multiplier
        score /= session.volatility_multiplier
        
        if score >= 8:
            return 'excellent'
        elif score >= 6:
            return 'good'
        elif score >= 4:
            return 'fair'
        else:
            return 'poor'
    
    def _get_session_conditions(self, session: SessionInfo, pair_type: str) -> Dict[str, float]:
        """Session conditions estimation"""
        base_spreads = {'major': 1.0, 'cross': 1.5, 'exotic': 3.0}
        base_volume_ratios = {'major': 1.0, 'cross': 0.7, 'exotic': 0.4}
        
        return {
            'expected_spread_bps': base_spreads[pair_type] * session.spread_expectation,
            'expected_volume_ratio': base_volume_ratios[pair_type] * session.volume_expectation,
            'liquidity_score': session.liquidity_multiplier,
            'volatility_score': session.volatility_multiplier,
            'execution_quality': min(10, session.liquidity_multiplier * 8)
        }
    
    def _get_time_based_strategy(self, pair_type: str, session: SessionInfo) -> Dict[str, any]:
        """Time-based strategy recommendations"""
        strategies = {
            'major': {
                'European': {
                    'strategy': 'aggressive',
                    'position_size': 1.2,
                    'holding_period': 'medium',
                    'stop_loss_pips': 15
                },
                'American': {
                    'strategy': 'moderate_aggressive',
                    'position_size': 1.0,
                    'holding_period': 'short_medium',
                    'stop_loss_pips': 20
                },
                'Asian': {
                    'strategy': 'conservative',
                    'position_size': 0.7,
                    'holding_period': 'long',
                    'stop_loss_pips': 25
                }
            },
            'cross': {
                'European': {
                    'strategy': 'moderate',
                    'position_size': 0.8,
                    'holding_period': 'medium',
                    'stop_loss_pips': 25
                },
                'American': {
                    'strategy': 'conservative',
                    'position_size': 0.6,
                    'holding_period': 'medium_long',
                    'stop_loss_pips': 30
                }
            }
        }
        
        session_name = session.name.split('_')[0]  # Remove _Overlap suffix
        
        base_strategy = strategies[pair_type].get(session_name, {
            'strategy': 'conservative',
            'position_size': 0.5,
            'holding_period': 'long',
            'stop_loss_pips': 35
        })
        
        # Adjust for overlap periods
        if 'Overlap' in session.name:
            base_strategy['position_size'] *= 1.2
            base_strategy['stop_loss_pips'] *= 0.9
        
        return base_strategy
    
    def create_session_calendar(self, start_date: datetime, 
                              end_date: datetime) -> pd.DataFrame:
        """Session calendar yaratish"""
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        calendar_data = []
        
        for date in date_range:
            for session_name, session_config in self.sessions.items():
                # Calculate session start and end
                session_start = datetime.combine(date, session_config.start_time)
                session_end = datetime.combine(date, session_config.end_time)
                
                # Handle sessions crossing midnight
                if session_config.end_time <= session_config.start_time:
                    session_end += timedelta(days=1)
                
                # Convert to timezone
                session_start_tz = session_start.replace(tzinfo=pytz.UTC)
                session_end_tz = session_end.replace(tzinfo=pytz.UTC)
                
                calendar_data.append({
                    'date': date.date(),
                    'session': session_name,
                    'start_time': session_start_tz,
                    'end_time': session_end_tz,
                    'duration_hours': (session_end_tz - session_start_tz).total_seconds() / 3600,
                    'volatility_multiplier': session_config.volatility_multiplier,
                    'liquidity_multiplier': session_config.liquidity_multiplier
                })
        
        calendar_df = pd.DataFrame(calendar_data)
        return calendar_df
    
    def get_session_transition_times(self, date: datetime = None) -> Dict[str, datetime]:
        """Session o'tish vaqtlarini olish"""
        if date is None:
            date = datetime.now().date()
        
        transitions = {}
        
        # London open (European start)
        london_open = datetime.combine(date, time(8, 0), tzinfo=pytz.UTC)
        transitions['london_open'] = london_open
        
        # New York open (American start)  
        ny_open = datetime.combine(date, time(13, 0), tzinfo=pytz.UTC)
        transitions['ny_open'] = ny_open
        
        # London close
        london_close = datetime.combine(date, time(17, 0), tzinfo=pytz.UTC)
        transitions['london_close'] = london_close
        
        # New York close
        ny_close = datetime.combine(date, time(22, 0), tzinfo=pytz.UTC)
        transitions['ny_close'] = ny_close
        
        # Tokyo close (Asian end)
        tokyo_close = datetime.combine(date, time(9, 0), tzinfo=pytz.UTC)
        if tokyo_close < datetime.combine(date, time(0, 0), tzinfo=pytz.UTC):
            tokyo_close += timedelta(days=1)
        transitions['tokyo_close'] = tokyo_close
        
        # Calculate overlap periods
        europe_asia_overlap_start = max(london_open, datetime.combine(date, time(0, 0), tzinfo=pytz.UTC))
        europe_asia_overlap_end = tokyo_close
        transitions['europe_asia_overlap'] = (europe_asia_overlap_start, europe_asia_overlap_end)
        
        europe_america_overlap_start = max(london_open, ny_open)
        europe_america_overlap_end = min(london_close, ny_close)
        transitions['europe_america_overlap'] = (europe_america_overlap_start, europe_america_overlap_end)
        
        return transitions
    
    def analyze_session_overlap_opportunities(self, target_date: datetime = None) -> Dict[str, any]:
        """Session overlap trading imkoniyatlarini tahlil qilish"""
        if target_date is None:
            target_date = datetime.now()
        
        transitions = self.get_session_transition_times(target_date.date())
        
        opportunities = {
            'europe_asia_overlap': {
                'description': 'London-Tokyo overlap',
                'duration_minutes': 60,
                'characteristics': {
                    'volatility': 'medium',
                    'liquidity': 'medium_high',
                    'spread_conditions': 'moderate',
                    'best_for': 'JPY crosses, AUD pairs'
                },
                'time_window': '08:00-09:00 UTC',
                'trading_score': 7
            },
            'europe_america_overlap': {
                'description': 'London-New York overlap',
                'duration_minutes': 240,
                'characteristics': {
                    'volatility': 'high',
                    'liquidity': 'excellent',
                    'spread_conditions': 'tight',
                    'best_for': 'All major pairs, news trading'
                },
                'time_window': '13:00-17:00 UTC',
                'trading_score': 10
            }
        }
        
        # Add current time analysis
        current_time = TimeUtils.get_current_utc_time()
        current_session = self.get_current_session(current_time)
        
        current_opportunity = {
            'is_overlap_period': 'Overlap' in current_session.name,
            'current_session': current_session.name,
            'session_quality': self._assess_session_suitability(current_session, 'major'),
            'next_overlap': self._get_next_overlap(current_time),
            'recommended_activities': self._get_overlap_recommendations(current_session)
        }
        
        return {
            'overlap_opportunities': opportunities,
            'current_analysis': current_opportunity,
            'recommendations': self._get_overlap_trading_tips()
        }
    
    def _get_next_overlap(self, current_time: datetime) -> Dict[str, datetime]:
        """Keyingi overlap period vaqtini olish"""
        next_europe_asia = None
        next_europe_america = None
        
        # Next Europe-Asia overlap (brief, 1 hour)
        if current_time.hour < 8:
            next_europe_asia = current_time.replace(hour=8, minute=0, second=0, microsecond=0)
        else:
            next_europe_asia = current_time + timedelta(days=1)
            next_europe_asia = next_europe_asia.replace(hour=8, minute=0, second=0, microsecond=0)
        
        # Next Europe-America overlap (4 hours)
        if current_time.hour < 13:
            next_europe_america = current_time.replace(hour=13, minute=0, second=0, microsecond=0)
        else:
            next_europe_america = current_time + timedelta(days=1)
            next_europe_america = next_europe_america.replace(hour=13, minute=0, second=0, microsecond=0)
        
        return {
            'europe_asia_overlap': next_europe_asia,
            'europe_america_overlap': next_europe_america
        }
    
    def _get_overlap_recommendations(self, session: SessionInfo) -> List[str]:
        """Overlap trading tavsiyalari"""
        recommendations = []
        
        if 'Overlap' in session.name:
            recommendations.extend([
                'Yuqori likvidlik: Katta position lar ochish mumkin',
                'Tight spreads: Cost effektiv trading',
                'News monitoring: Tez yangiliklar ta\'siri',
                'Volatility preparation: Katta harakatlar kutish'
            ])
        elif session.name == 'European':
            recommendations.extend([
                'European session: Asosiy aktivlik davri',
                'Cross pair imkoniyatlari',
                'ECB va boshqa Yevropa banklari e\'lonlari'
            ])
        elif session.name == 'American':
            recommendations.extend([
                'American session: Yuqori volatilite',
                'Fed va boshqa amerika banklari e\'lonlari',
                'US economic data lar'
            ])
        
        return recommendations
    
    def _get_overlap_trading_tips(self) -> List[str]:
        """Overlap trading maslahatlari"""
        return [
            'Overlap davrida volatilite oshadi - stop-loss ni moslashtiring',
            'News event larni yaqindan kuzating',
            'Order book depth ni monitoring qiling',
            'Large institutional orders bo\'lishi mumkin',
            'Spread widening vaqti learning',
            'Quick scalping imkoniyatlari',
            'Risk management ni qat\'iylashtiring'
        ]
    
    def generate_session_report(self, data: pd.DataFrame = None,
                              target_date: datetime = None) -> Dict[str, any]:
        """Session tahlil hisoboti"""
        if target_date is None:
            target_date = datetime.now()
        
        # Current session status
        current_session = self.get_current_session(target_date)
        
        # Session schedule
        schedule = self.get_session_schedule(target_date.date())
        
        # Performance analysis
        performance_metrics = {}
        if data is not None:
            performance_metrics = self.analyze_session_performance(data)
        
        # Trading recommendations
        recommendations = self.get_optimal_trading_hours('EURUSD')  # Default to major pair
        
        report = {
            'timestamp': target_date,
            'current_session': {
                'name': current_session.name,
                'is_active': current_session.is_active,
                'volatility_multiplier': current_session.volatility_multiplier,
                'liquidity_multiplier': current_session.liquidity_multiplier,
                'expected_spread_bps': current_session.spread_expectation
            },
            'daily_schedule': schedule,
            'performance_metrics': {k: {
                'avg_volume': v.avg_volume,
                'avg_volatility': v.avg_volatility,
                'avg_spread': v.avg_spread
            } for k, v in performance_metrics.items()},
            'trading_recommendations': recommendations,
            'next_events': self._get_upcoming_session_events(target_date),
            'risk_factors': self._assess_session_risks(current_session)
        }
        
        return report
    
    def _get_upcoming_session_events(self, target_time: datetime) -> List[Dict]:
        """Kelgusi session voqealari"""
        events = []
        
        # Next session starts
        next_sessions = {
            'Asian': time(0, 0),
            'European': time(8, 0),
            'American': time(13, 0)
        }
        
        for session_name, start_time in next_sessions.items():
            next_start = target_time.replace(
                hour=start_time.hour, 
                minute=start_time.minute, 
                second=0, 
                microsecond=0
            )
            
            if next_start <= target_time:
                next_start += timedelta(days=1)
            
            events.append({
                'type': 'session_start',
                'session': session_name,
                'time': next_start,
                'hours_until': (next_start - target_time).total_seconds() / 3600
            })
        
        # Next overlap periods
        overlap_times = self.get_session_transition_times(target_time.date())
        
        if 'europe_asia_overlap' in overlap_times:
            events.append({
                'type': 'overlap_start',
                'overlap': 'Europe-Asia',
                'time': overlap_times['europe_asia_overlap'][0],
                'description': 'London-Tokyo overlap'
            })
        
        if 'europe_america_overlap' in overlap_times:
            events.append({
                'type': 'overlap_start',
                'overlap': 'Europe-America', 
                'time': overlap_times['europe_america_overlap'][0],
                'description': 'London-New York overlap'
            })
        
        return sorted(events, key=lambda x: x['time'])
    
    def _assess_session_risks(self, session: SessionInfo) -> List[str]:
        """Session risk assessment"""
        risks = []
        
        if session.volatility_multiplier > 1.2:
            risks.append('Yuqori volatilite - katta narx harakatlari')
        
        if session.liquidity_multiplier < 0.8:
            risks.append('Past likvidlik - execution qiyinchiligi')
        
        if session.spread_expectation > 1.2:
            risks.append('Keng spreads - yuqori trading cost')
        
        if not session.is_active:
            risks.append('Session yopiq - minimal aktivlik')
        
        return risks