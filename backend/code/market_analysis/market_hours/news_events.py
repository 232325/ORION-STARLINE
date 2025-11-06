"""
News Events Module
=================

News events va impact tahlili moduli.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import pytz
from ..utils.time_utils import TimeUtils
import warnings
warnings.filterwarnings('ignore')


@dataclass
class NewsEvent:
    """Yangilik voqeasi"""
    timestamp: datetime
    currency: str
    event_name: str
    impact_level: str  # 'High', 'Medium', 'Low'
    actual_value: Optional[float]
    forecast_value: Optional[float]
    previous_value: Optional[float]
    surprise_factor: float
    market_reaction: str


@dataclass
class NewsImpact:
    """Yangilik ta'siri"""
    event_id: str
    volatility_spike: float
    volume_spike: float
    price_movement_bps: float
    recovery_time_minutes: int
    sustained_effect: bool


class NewsEventAnalyzer:
    """Yangilik voqealarini tahlil qiluvchi"""
    
    def __init__(self):
        self.news_calendar = self._initialize_news_calendar()
        self.impact_thresholds = {
            'high': {'volatility_multiplier': 3.0, 'volume_multiplier': 2.5},
            'medium': {'volatility_multiplier': 1.8, 'volume_multiplier': 1.5},
            'low': {'volatility_multiplier': 1.2, 'volume_multiplier': 1.1}
        }
        
        # High impact news events
        self.high_impact_events = [
            'Non-Farm Payrolls',
            'Federal Funds Rate Decision',
            'ECB Interest Rate Decision',
            'Bank of Japan Interest Rate Decision',
            'Bank of England Interest Rate Decision',
            'US CPI',
            'US GDP',
            'Employment Change',
            'Inflation Rate',
            'Central Bank Speeches'
        ]
        
        # Medium impact events
        self.medium_impact_events = [
            'Retail Sales',
            'Industrial Production',
            'Manufacturing PMI',
            'Services PMI',
            'Consumer Confidence',
            'Trade Balance',
            'Unemployment Rate',
            'Average Earnings',
            'Business Confidence',
            'Consumer Price Index'
        ]
    
    def _initialize_news_calendar(self) -> pd.DataFrame:
        """Yangilik calendarini boshlang'ichlash"""
        # Sample news events (in real implementation, this would come from data feeds)
        events = [
            {
                'timestamp': datetime(2025, 1, 3, 13, 30, tzinfo=pytz.UTC),  # 8:30 EST
                'currency': 'USD',
                'event_name': 'Non-Farm Payrolls',
                'impact_level': 'High',
                'frequency': 'Monthly'
            },
            {
                'timestamp': datetime(2025, 1, 3, 14, 0, tzinfo=pytz.UTC),   # 9:00 EST
                'currency': 'USD', 
                'event_name': 'Federal Funds Rate Decision',
                'impact_level': 'High',
                'frequency': 'Monthly'
            },
            {
                'timestamp': datetime(2025, 1, 3, 12, 30, tzinfo=pytz.UTC),  # 7:30 EST
                'currency': 'USD',
                'event_name': 'Unemployment Rate',
                'impact_level': 'Medium',
                'frequency': 'Monthly'
            },
            {
                'timestamp': datetime(2025, 1, 3, 11, 0, tzinfo=pytz.UTC),   # 6:00 EST
                'currency': 'EUR',
                'event_name': 'ECB Interest Rate Decision',
                'impact_level': 'High',
                'frequency': 'Monthly'
            },
            {
                'timestamp': datetime(2025, 1, 3, 8, 30, tzinfo=pytz.UTC),   # 3:30 EST
                'currency': 'GBP',
                'event_name': 'Bank of England Interest Rate Decision',
                'impact_level': 'High',
                'frequency': 'Monthly'
            }
        ]
        
        return pd.DataFrame(events)
    
    def get_upcoming_news_events(self, hours_ahead: int = 24) -> List[Dict]:
        """Kelgusi yangilik voqealarini olish"""
        current_time = TimeUtils.get_current_utc_time()
        end_time = current_time + timedelta(hours=hours_ahead)
        
        upcoming_events = self.news_calendar[
            (self.news_calendar['timestamp'] >= current_time) & 
            (self.news_calendar['timestamp'] <= end_time)
        ]
        
        events_list = []
        for _, event in upcoming_events.iterrows():
            events_list.append({
                'timestamp': event['timestamp'],
                'currency': event['currency'],
                'event_name': event['event_name'],
                'impact_level': event['impact_level'],
                'time_until': event['timestamp'] - current_time,
                'minutes_until': int((event['timestamp'] - current_time).total_seconds() / 60),
                'frequency': event['frequency']
            })
        
        return events_list
    
    def calculate_news_impact_potential(self, event: Dict) -> Dict[str, float]:
        """Yangilik ta'sir potensialini hisoblash"""
        impact_level = event['impact_level'].lower()
        thresholds = self.impact_thresholds.get(impact_level, self.impact_thresholds['medium'])
        
        # Base volatility increase
        base_volatility_spike = thresholds['volatility_multiplier']
        base_volume_spike = thresholds['volume_multiplier']
        
        # Time of day adjustments
        event_hour = event['timestamp'].hour
        time_adjustment = self._get_time_of_day_adjustment(event_hour)
        
        # Currency importance adjustment
        currency_importance = self._get_currency_importance(event['currency'])
        
        volatility_spike = base_volatility_spike * time_adjustment * currency_importance
        volume_spike = base_volume_spike * time_adjustment * currency_importance
        
        return {
            'expected_volatility_increase': volatility_spike,
            'expected_volume_increase': volume_spike,
            'price_movement_expectation_bps': volatility_spike * 5,  # Rough estimate
            'trading_risk_level': self._assess_trading_risk(impact_level, event_hour),
            'recommended_actions': self._get_recommended_actions(event)
        }
    
    def _get_time_of_day_adjustment(self, hour: int) -> float:
        """Vaqt bo'yicha sozlamani olish"""
        # European session (8-17 UTC) - high activity
        if 8 <= hour <= 17:
            return 1.2
        # American session (13-22 UTC) - very high activity
        elif 13 <= hour <= 22:
            return 1.3
        # Asian session (0-8 UTC) - low activity
        elif 0 <= hour <= 8:
            return 0.8
        # Low activity hours
        else:
            return 0.7
    
    def _get_currency_importance(self, currency: str) -> float:
        """Valyuta muhimligini olish"""
        importance_ranking = {
            'USD': 1.3,  # Most important
            'EUR': 1.2,
            'GBP': 1.1,
            'JPY': 1.1,
            'CHF': 1.0,
            'CAD': 0.9,
            'AUD': 0.9,
            'NZD': 0.8
        }
        return importance_ranking.get(currency.upper(), 0.8)
    
    def _assess_trading_risk(self, impact_level: str, hour: int) -> str:
        """Trading risk darajasini baholash"""
        if impact_level == 'high':
            if 8 <= hour <= 17 or 13 <= hour <= 22:
                return 'very_high'
            else:
                return 'high'
        elif impact_level == 'medium':
            return 'medium'
        else:
            return 'low'
    
    def _get_recommended_actions(self, event: Dict) -> List[str]:
        """Tavsiya qilingan harakatlar"""
        actions = []
        impact_level = event['impact_level'].lower()
        
        if impact_level == 'high':
            actions.extend([
                'Position larni yoping yoki hajmni kamaytiring',
                'Stop-loss ni qat\'iylashtiring',
                'Yangilik chiqishidan 30 daqiqa oldin trade qilmang',
                'News event ni yaqindan kuzating'
            ])
        elif impact_level == 'medium':
            actions.extend([
                'Ehtiyotkorlik bilan trade qiling',
                'Stop-loss ni sekinroq qo\'ying',
                'Spreading watch qiling'
            ])
        
        # Currency specific actions
        currency = event['currency'].upper()
        if currency == 'USD':
            actions.append('USD events - Fed communications ga e\'tibor')
        elif currency == 'EUR':
            actions.append('EUR events - ECB policy ga e\'tibor')
        elif currency == 'GBP':
            actions.append('GBP events - BoE decisions ga e\'tibor')
        
        return actions
    
    def simulate_news_impact(self, event: Dict, market_data: pd.DataFrame) -> NewsImpact:
        """Yangilik ta'sirini simulatsiya qilish"""
        # Calculate impact based on event characteristics
        impact_potential = self.calculate_news_impact_potential(event)
        
        # Estimate volatility spike
        current_volatility = market_data['close'].pct_change().std()
        expected_volatility = current_volatility * impact_potential['expected_volatility_increase']
        volatility_spike = (expected_volatility - current_volatility) / current_volatility
        
        # Estimate volume spike
        current_volume = market_data['volume'].mean() if 'volume' in market_data.columns else 1
        expected_volume = current_volume * impact_potential['expected_volume_increase']
        volume_spike = (expected_volume - current_volume) / current_volume
        
        # Estimate price movement
        price_movement_bps = impact_potential['price_movement_expectation_bps']
        
        # Recovery time (simplified)
        if event['impact_level'] == 'High':
            recovery_time = np.random.randint(60, 240)  # 1-4 hours
            sustained_effect = True
        elif event['impact_level'] == 'Medium':
            recovery_time = np.random.randint(30, 120)  # 30min-2 hours
            sustained_effect = False
        else:
            recovery_time = np.random.randint(15, 60)  # 15min-1 hour
            sustained_effect = False
        
        return NewsImpact(
            event_id=f"{event['currency']}_{event['event_name']}_{event['timestamp'].strftime('%Y%m%d_%H%M')}",
            volatility_spike=volatility_spike,
            volume_spike=volume_spike,
            price_movement_bps=price_movement_bps,
            recovery_time_minutes=recovery_time,
            sustained_effect=sustained_effect
        )
    
    def analyze_historical_news_impact(self, news_events: List[NewsEvent], 
                                     market_data: pd.DataFrame) -> Dict[str, any]:
        """Tarixiy yangilik ta'sirini tahlil qilish"""
        if market_data.empty:
            return {}
        
        # Analyze impact by impact level
        impact_analysis = {}
        
        for impact_level in ['High', 'Medium', 'Low']:
            level_events = [e for e in news_events if e.impact_level == impact_level]
            
            if not level_events:
                continue
            
            # Calculate average metrics for this impact level
            avg_volatility_before = []
            avg_volatility_after = []
            avg_price_movement = []
            
            for event in level_events:
                # Get data before and after event
                event_time = event.timestamp
                
                before_data = market_data[
                    (market_data.index >= event_time - timedelta(hours=2)) &
                    (market_data.index < event_time)
                ]
                
                after_data = market_data[
                    (market_data.index >= event_time) &
                    (market_data.index <= event_time + timedelta(hours=2))
                ]
                
                if len(before_data) > 0 and len(after_data) > 0:
                    vol_before = before_data['close'].pct_change().std()
                    vol_after = after_data['close'].pct_change().std()
                    
                    avg_volatility_before.append(vol_before)
                    avg_volatility_after.append(vol_after)
                    
                    # Price movement
                    price_change = ((after_data['close'].iloc[-1] - before_data['close'].iloc[-1]) / 
                                  before_data['close'].iloc[-1] * 10000)  # bps
                    avg_price_movement.append(abs(price_change))
            
            if avg_volatility_before and avg_volatility_after:
                impact_analysis[impact_level] = {
                    'avg_volatility_before': np.mean(avg_volatility_before),
                    'avg_volatility_after': np.mean(avg_volatility_after),
                    'avg_volatility_increase': (np.mean(avg_volatility_after) - np.mean(avg_volatility_before)) / np.mean(avg_volatility_before),
                    'avg_price_movement_bps': np.mean(avg_price_movement),
                    'max_price_movement_bps': np.max(avg_price_movement),
                    'event_count': len(level_events)
                }
        
        return impact_analysis
    
    def create_news_trading_strategy(self, upcoming_events: List[Dict],
                                   risk_tolerance: str = 'medium') -> Dict[str, any]:
        """Yangilik asosida trading strategiyasi"""
        strategy = {
            'trading_approach': '',
            'position_sizing': {},
            'risk_management': {},
            'timing': {},
            'avoid_periods': [],
            'optimal_events': []
        }
        
        # Risk-based approach
        if risk_tolerance == 'low':
            strategy['trading_approach'] = 'avoid_news'
            strategy['avoid_periods'] = [event['event_name'] for event in upcoming_events 
                                       if event['impact_level'] == 'High']
        elif risk_tolerance == 'high':
            strategy['trading_approach'] = 'news_trading'
            strategy['optimal_events'] = [event for event in upcoming_events 
                                        if event['impact_level'] in ['High', 'Medium']]
        else:  # medium
            strategy['trading_approach'] = 'selective_news'
            strategy['optimal_events'] = [event for event in upcoming_events 
                                        if event['impact_level'] == 'Medium']
        
        # Position sizing recommendations
        position_multipliers = {
            'low': 0.5, 'medium': 0.75, 'high': 1.0
        }
        
        strategy['position_sizing'] = {
            'base_multiplier': position_multipliers[risk_tolerance],
            'adjustment_news_period': 0.3,
            'adjustment_high_impact': 0.2
        }
        
        # Risk management
        strategy['risk_management'] = {
            'stop_loss_multiplier': 1.5 if risk_tolerance == 'high' else 2.0,
            'max_open_positions': 3 if risk_tolerance == 'high' else 1,
            'avoid_trading_minutes_before': 30 if risk_tolerance == 'low' else 15,
            'avoid_trading_minutes_after': 60 if risk_tolerance == 'low' else 30
        }
        
        # Timing strategy
        strategy['timing'] = {
            'pre_news': 'Avoid new positions',
            'during_news': 'Monitor closely, adjust stops',
            'post_news': 'Wait for volatility to settle',
            'optimal_entry_delay_minutes': 30 if risk_tolerance == 'low' else 15
        }
        
        return strategy
    
    def get_news_market_hours_intersection(self, upcoming_events: List[Dict]) -> Dict[str, List]:
        """Yangilik va market soatlari kesishmasi"""
        from ..market_hours.forex_sessions import ForexSessionManager
        session_manager = ForexSessionManager()
        
        intersections = {
            'high_impact_during_overlap': [],
            'high_impact_during_major_session': [],
            'optimal_news_timing': [],
            'avoid_timing': []
        }
        
        for event in upcoming_events:
            event_time = event['timestamp']
            impact_level = event['impact_level']
            
            # Check if event coincides with trading sessions
            session = session_manager.get_current_session(event_time)
            active_sessions = session_manager.get_session_schedule(event_time.date())
            
            # Overlap timing
            if 'Overlap' in session.name:
                if impact_level == 'High':
                    intersections['high_impact_during_overlap'].append({
                        'event': event,
                        'session': session.name,
                        'opportunity': 'Maximum volatility and liquidity'
                    })
            
            # Major session timing
            if session.name in ['European', 'American'] and impact_level == 'High':
                intersections['high_impact_during_major_session'].append({
                    'event': event,
                    'session': session.name,
                    'opportunity': 'Good volatility with decent liquidity'
                })
            
            # Optimal timing (European session for USD events, etc.)
            if self._is_optimal_news_timing(event, session):
                intersections['optimal_news_timing'].append({
                    'event': event,
                    'session': session.name,
                    'reason': 'Good session overlap for currency'
                })
        
        return intersections
    
    def _is_optimal_news_timing(self, event: Dict, session) -> bool:
        """Optimal yangilik vaqtini aniqlash"""
        currency = event['currency'].upper()
        
        # USD events during American session overlap
        if currency == 'USD' and 'American' in session.name:
            return True
        
        # EUR events during European session
        if currency == 'EUR' and session.name == 'European':
            return True
        
        # GBP events during European session
        if currency == 'GBP' and session.name == 'European':
            return True
        
        # JPY events during Asian session
        if currency == 'JPY' and session.name == 'Asian':
            return True
        
        return False
    
    def generate_news_alerts(self, upcoming_events: List[Dict]) -> List[Dict]:
        """Yangilik ogohlantirishlari"""
        alerts = []
        current_time = TimeUtils.get_current_utc_time()
        
        for event in upcoming_events:
            time_until = event['timestamp'] - current_time
            minutes_until = time_until.total_seconds() / 60
            
            # High impact event warnings
            if event['impact_level'] == 'High':
                if minutes_until <= 60:  # Within 1 hour
                    alerts.append({
                        'type': 'high_impact_approaching',
                        'currency': event['currency'],
                        'event': event['event_name'],
                        'minutes_until': int(minutes_until),
                        'message': f"Yuqori ta'sirli {event['currency']} yangiligi {int(minutes_until)} daqiqadan keyin",
                        'action': 'Position sizes ni kamaytiring'
                    })
                
                elif minutes_until <= 30:  # Within 30 minutes
                    alerts.append({
                        'type': 'high_impact_imminent',
                        'currency': event['currency'],
                        'event': event['event_name'],
                        'minutes_until': int(minutes_until),
                        'message': f"Yuqori ta'sirli {event['currency']} yangiligi {int(minutes_until)} daqiqadan keyin",
                        'action': 'Yangi positions ochmang, stops adjust qiling'
                    })
            
            # Multiple high impact events warning
            high_impact_count = len([e for e in upcoming_events 
                                   if e['impact_level'] == 'High' and 
                                   0 <= (e['timestamp'] - current_time).total_seconds() / 3600 <= 2])
            
            if high_impact_count > 1 and minutes_until <= 120:  # 2 hours window
                alerts.append({
                    'type': 'multiple_high_impact',
                    'count': high_impact_count,
                    'time_window': '2 hours',
                    'message': f"{high_impact_count} ta yuqori ta'sirli yangilik 2 soat ichida",
                    'action': 'Keng tarqalgan risk - positions ni kamaytiring'
                })
        
        return alerts
    
    def create_news_impact_model(self, historical_events: List[NewsEvent],
                               market_data: pd.DataFrame) -> Dict[str, any]:
        """Yangilik ta'sir modelini yaratish"""
        if not historical_events or market_data.empty:
            return {'status': 'insufficient_data'}
        
        # Extract features and targets
        features = []
        targets = []
        
        for event in historical_events:
            # Event features
            impact_encoding = {'High': 3, 'Medium': 2, 'Low': 1}
            
            event_features = [
                impact_encoding.get(event.impact_level, 1),
                event.timestamp.hour,
                1 if event.timestamp.weekday() < 5 else 0,  # weekday
                1 if event.currency in ['USD', 'EUR', 'GBP', 'JPY'] else 0,  # major currency
                abs(event.surprise_factor) if event.surprise_factor else 0
            ]
            
            features.append(event_features)
            
            # Find market reaction around event time
            event_time = event.timestamp
            
            before_data = market_data[
                (market_data.index >= event_time - timedelta(minutes=30)) &
                (market_data.index < event_time)
            ]
            
            after_data = market_data[
                (market_data.index >= event_time) &
                (market_data.index <= event_time + timedelta(hours=2))
            ]
            
            if len(before_data) > 0 and len(after_data) > 0:
                # Calculate volatility increase
                vol_before = before_data['close'].pct_change().std()
                vol_after = after_data['close'].pct_change().std()
                volatility_impact = (vol_after - vol_before) / vol_before if vol_before > 0 else 0
                
                # Calculate price movement
                price_change = ((after_data['close'].iloc[-1] - before_data['close'].iloc[-1]) / 
                              before_data['close'].iloc[-1] * 10000)  # bps
                
                targets.append([volatility_impact, price_change])
            else:
                targets.append([0, 0])
        
        if not features or not targets:
            return {'status': 'no_valid_events'}
        
        # Simple linear model (in practice, would use more sophisticated ML)
        from sklearn.linear_model import LinearRegression
        
        X = np.array(features)
        y = np.array(targets)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Model evaluation
        score = model.score(X, y)
        
        return {
            'status': 'success',
            'model_type': 'linear_regression',
            'score': score,
            'coefficients': {
                'volatility_impact': model.coef_[0].tolist(),
                'price_movement': model.coef_[1].tolist()
            },
            'feature_names': [
                'impact_level', 'hour', 'weekday', 'major_currency', 'surprise_factor'
            ],
            'intercepts': {
                'volatility_impact': float(model.intercept_[0]),
                'price_movement': float(model.intercept_[1])
            }
        }