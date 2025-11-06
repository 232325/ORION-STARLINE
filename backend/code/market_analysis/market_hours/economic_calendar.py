"""
Economic Calendar Module
=======================

Iqtisodiy calendar ma'lumotlari moduli.
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
class EconomicEvent:
    """Iqtisodiy voqea"""
    event_id: str
    name: str
    country: str
    currency: str
    importance: str  # 'high', 'medium', 'low'
    scheduled_time: datetime
    actual_value: Optional[float]
    forecast_value: Optional[float]
    previous_value: Optional[float]
    frequency: str  # 'monthly', 'quarterly', 'annual', 'daily', 'weekly'
    category: str  # 'inflation', 'employment', 'growth', 'sentiment', 'trade'
    unit: str
    surprise_factor: float
    market_impact_bps: float


@dataclass
class EconomicCalendar:
    """Iqtisodiy calendar"""
    events: List[EconomicEvent]
    start_date: datetime
    end_date: datetime
    total_events: int
    high_impact_count: int
    most_important_currency: str


class EconomicCalendarLoader:
    """Iqtisodiy calendar loader va analyzer"""
    
    def __init__(self):
        self.event_categories = {
            'inflation': {
                'events': ['CPI', 'PPI', 'PCE Price Index', 'Core CPI', 'Inflation Rate'],
                'typical_impact_bps': 25,
                'volatility_multiplier': 2.0,
                'recovery_hours': 4
            },
            'employment': {
                'events': ['Non-Farm Payrolls', 'Unemployment Rate', 'Jobless Claims', 'Employment Change'],
                'typical_impact_bps': 40,
                'volatility_multiplier': 2.5,
                'recovery_hours': 6
            },
            'growth': {
                'events': ['GDP', 'Industrial Production', 'Retail Sales', 'Consumer Spending'],
                'typical_impact_bps': 30,
                'volatility_multiplier': 2.2,
                'recovery_hours': 5
            },
            'sentiment': {
                'events': ['Consumer Confidence', 'Business Confidence', 'Consumer Sentiment', 'PMI'],
                'typical_impact_bps': 15,
                'volatility_multiplier': 1.5,
                'recovery_hours': 2
            },
            'trade': {
                'events': ['Trade Balance', 'Current Account', 'Imports', 'Exports'],
                'typical_impact_bps': 10,
                'volatility_multiplier': 1.2,
                'recovery_hours': 1
            }
        }
        
        self.country_importance = {
            'US': {'weight': 1.0, 'primary_currency': 'USD', 'secondary_currencies': ['EUR', 'GBP', 'JPY']},
            'EU': {'weight': 0.9, 'primary_currency': 'EUR', 'secondary_currencies': ['USD', 'GBP', 'CHF']},
            'UK': {'weight': 0.7, 'primary_currency': 'GBP', 'secondary_currencies': ['EUR', 'USD']},
            'JP': {'weight': 0.6, 'primary_currency': 'JPY', 'secondary_currencies': ['USD', 'EUR']},
            'CN': {'weight': 0.8, 'primary_currency': 'CNY', 'secondary_currencies': ['USD', 'AUD']},
            'CA': {'weight': 0.4, 'primary_currency': 'CAD', 'secondary_currencies': ['USD']},
            'AU': {'weight': 0.5, 'primary_currency': 'AUD', 'secondary_currencies': ['USD', 'NZD']},
            'CH': {'weight': 0.3, 'primary_currency': 'CHF', 'secondary_currencies': ['EUR', 'USD']},
            'DE': {'weight': 0.6, 'primary_currency': 'EUR', 'secondary_currencies': ['USD', 'GBP']},
            'FR': {'weight': 0.5, 'primary_currency': 'EUR', 'secondary_currencies': ['USD', 'GBP']},
        }
        
        # US Economic Calendar (most important)
        self.us_events = {
            'Non-Farm Payrolls': {
                'frequency': 'monthly',
                'release_time': '13:30',  # 8:30 EST
                'importance': 'high',
                'category': 'employment'
            },
            'Unemployment Rate': {
                'frequency': 'monthly',
                'release_time': '13:30',
                'importance': 'high',
                'category': 'employment'
            },
            'Federal Funds Rate': {
                'frequency': '8_per_year',
                'release_time': '18:00',  # FOMC announcement
                'importance': 'high',
                'category': 'monetary_policy'
            },
            'CPI': {
                'frequency': 'monthly',
                'release_time': '13:30',
                'importance': 'high',
                'category': 'inflation'
            },
            'GDP': {
                'frequency': 'quarterly',
                'release_time': '13:30',
                'importance': 'high',
                'category': 'growth'
            },
            'Consumer Confidence': {
                'frequency': 'monthly',
                'release_time': '15:00',
                'importance': 'medium',
                'category': 'sentiment'
            },
            'Retail Sales': {
                'frequency': 'monthly',
                'release_time': '13:30',
                'importance': 'medium',
                'category': 'growth'
            },
            'Industrial Production': {
                'frequency': 'monthly',
                'release_time': '14:15',
                'importance': 'medium',
                'category': 'growth'
            },
            'Jobless Claims': {
                'frequency': 'weekly',
                'release_time': '13:30',
                'importance': 'medium',
                'category': 'employment'
            },
            'Consumer Price Index': {
                'frequency': 'monthly',
                'release_time': '13:30',
                'importance': 'high',
                'category': 'inflation'
            }
        }
        
        # European Events
        self.eu_events = {
            'ECB Interest Rate Decision': {
                'frequency': '8_per_year',
                'release_time': '11:45',
                'importance': 'high',
                'category': 'monetary_policy'
            },
            'Eurozone PMI': {
                'frequency': 'monthly',
                'release_time': '09:00',
                'importance': 'medium',
                'category': 'sentiment'
            },
            'German GDP': {
                'frequency': 'quarterly',
                'release_time': '07:00',
                'importance': 'high',
                'category': 'growth'
            },
            'EU CPI': {
                'frequency': 'monthly',
                'release_time': '10:00',
                'importance': 'high',
                'category': 'inflation'
            },
            'German IFO Business Climate': {
                'frequency': 'monthly',
                'release_time': '09:00',
                'importance': 'medium',
                'category': 'sentiment'
            },
            'Trade Balance': {
                'frequency': 'monthly',
                'release_time': '09:00',
                'importance': 'low',
                'category': 'trade'
            }
        }
        
        # UK Events
        self.uk_events = {
            'Bank of England Interest Rate Decision': {
                'frequency': '8_per_year',
                'release_time': '11:00',
                'importance': 'high',
                'category': 'monetary_policy'
            },
            'UK GDP': {
                'frequency': 'quarterly',
                'release_time': '09:30',
                'importance': 'high',
                'category': 'growth'
            },
            'UK CPI': {
                'frequency': 'monthly',
                'release_time': '09:30',
                'importance': 'high',
                'category': 'inflation'
            },
            'UK Employment Change': {
                'frequency': 'monthly',
                'release_time': '09:30',
                'importance': 'medium',
                'category': 'employment'
            },
            'UK Retail Sales': {
                'frequency': 'monthly',
                'release_time': '09:30',
                'importance': 'medium',
                'category': 'growth'
            }
        }
        
        # Japanese Events
        self.jp_events = {
            'Bank of Japan Interest Rate Decision': {
                'frequency': '8_per_year',
                'release_time': '03:00',
                'importance': 'high',
                'category': 'monetary_policy'
            },
            'Japan CPI': {
                'frequency': 'monthly',
                'release_time': '23:50',
                'importance': 'medium',
                'category': 'inflation'
            },
            'Japan GDP': {
                'frequency': 'quarterly',
                'release_time': '00:00',
                'importance': 'high',
                'category': 'growth'
            },
            'Trade Balance': {
                'frequency': 'monthly',
                'release_time': '23:50',
                'importance': 'low',
                'category': 'trade'
            }
        }
    
    def load_economic_calendar(self, start_date: datetime, end_date: datetime,
                             countries: List[str] = None) -> EconomicCalendar:
        """Iqtisodiy calendar yuklash"""
        if countries is None:
            countries = ['US', 'EU', 'UK', 'JP']
        
        events = []
        event_id_counter = 1
        
        # Generate events for each country
        for country in countries:
            country_events = self._generate_country_events(country, start_date, end_date)
            events.extend(country_events)
        
        # Sort events by time
        events.sort(key=lambda x: x.scheduled_time)
        
        # Calculate statistics
        total_events = len(events)
        high_impact_count = len([e for e in events if e.importance == 'high'])
        
        # Find most important currency
        currency_counts = {}
        for event in events:
            currency = event.currency
            currency_counts[currency] = currency_counts.get(currency, 0) + event.importance == 'high'
        
        most_important_currency = max(currency_counts.items(), key=lambda x: x[1])[0] if currency_counts else 'USD'
        
        return EconomicCalendar(
            events=events,
            start_date=start_date,
            end_date=end_date,
            total_events=total_events,
            high_impact_count=high_impact_count,
            most_important_currency=most_important_currency
        )
    
    def _generate_country_events(self, country: str, start_date: datetime, 
                               end_date: datetime) -> List[EconomicEvent]:
        """Biror mamlakat uchun voqealar yaratish"""
        events = []
        event_id_counter = 1
        country_info = self.country_importance.get(country.upper(), {})
        
        # Get country-specific events
        country_events = getattr(self, f"{country.lower()}_events", {})
        
        # Generate events for the date range
        current_date = start_date.date()
        
        while current_date <= end_date.date():
            weekday = current_date.weekday()
            
            for event_name, event_info in country_events.items():
                # Check if event should be released on this date
                if self._should_release_event(event_info, current_date, weekday):
                    # Create event
                    event = self._create_economic_event(
                        event_id=f"{country}_{event_name}_{current_date.strftime('%Y%m%d')}",
                        name=event_name,
                        country=country,
                        currency=country_info.get('primary_currency', 'USD'),
                        importance=event_info['importance'],
                        scheduled_time=self._get_event_time(current_date, event_info['release_time']),
                        frequency=event_info['frequency'],
                        category=event_info['category']
                    )
                    events.append(event)
                    event_id_counter += 1
            
            # Move to next day
            current_date += timedelta(days=1)
        
        return events
    
    def _should_release_event(self, event_info: Dict, release_date: datetime.date,
                            weekday: int) -> bool:
        """Voqea ushbu sanada chiqarilishi kerakmi tekshirish"""
        frequency = event_info['frequency']
        
        if frequency == 'monthly':
            # Most monthly US data releases on first Friday
            return weekday == 4 and release_date.day <= 7
        elif frequency == 'quarterly':
            # Quarterly data typically released quarterly
            return release_date.day <= 10 and release_date.month % 3 == 0
        elif frequency == '8_per_year':
            # Central bank meetings roughly every 6 weeks
            days_since_start = (release_date - datetime(2025, 1, 1).date()).days
            return days_since_start % 42 <= 5  # Released within 5-day window
        elif frequency == 'weekly':
            # Weekly data (like jobless claims) released Thursday
            return weekday == 3  # Thursday
        elif frequency == 'daily':
            # Daily data
            return True
        
        return False
    
    def _get_event_time(self, release_date: datetime.date, release_time_str: str) -> datetime:
        """Voqea vaqtini olish"""
        hour, minute = map(int, release_time_str.split(':'))
        return datetime.combine(release_date, time(hour, minute), tzinfo=pytz.UTC)
    
    def _create_economic_event(self, event_id: str, name: str, country: str, currency: str,
                             importance: str, scheduled_time: datetime, frequency: str,
                             category: str) -> EconomicEvent:
        """Iqtisodiy voqea yaratish"""
        # Assign importance weight
        importance_weights = {'high': 3, 'medium': 2, 'low': 1}
        weight = importance_weights.get(importance, 1)
        
        # Get category info
        category_info = self.event_categories.get(category, {
            'typical_impact_bps': 10,
            'volatility_multiplier': 1.0,
            'recovery_hours': 2
        })
        
        # Generate realistic values (in real implementation, these would be from actual data)
        actual_value = np.random.normal(0, weight * 0.5)  # Random actual value
        forecast_value = actual_value + np.random.normal(0, weight * 0.3)  # Forecast around actual
        previous_value = actual_value + np.random.normal(0, weight * 0.4)  # Previous value
        
        # Calculate surprise factor
        if forecast_value != 0:
            surprise_factor = (actual_value - forecast_value) / abs(forecast_value)
        else:
            surprise_factor = 0
        
        # Estimate market impact
        base_impact = category_info['typical_impact_bps']
        impact_multiplier = 1 + abs(surprise_factor)  # Larger surprises = larger impact
        market_impact_bps = base_impact * impact_multiplier
        
        return EconomicEvent(
            event_id=event_id,
            name=name,
            country=country,
            currency=currency,
            importance=importance,
            scheduled_time=scheduled_time,
            actual_value=actual_value,
            forecast_value=forecast_value,
            previous_value=previous_value,
            frequency=frequency,
            category=category,
            unit='%',  # Default unit
            surprise_factor=surprise_factor,
            market_impact_bps=market_impact_bps
        )
    
    def get_high_impact_events(self, calendar: EconomicCalendar,
                             hours_ahead: int = 24) -> List[EconomicEvent]:
        """Yuqori ta'sirli voqealarni olish"""
        current_time = TimeUtils.get_current_utc_time()
        end_time = current_time + timedelta(hours=hours_ahead)
        
        high_impact_events = [
            event for event in calendar.events
            if (event.importance == 'high' and
                current_time <= event.scheduled_time <= end_time)
        ]
        
        return sorted(high_impact_events, key=lambda x: x.scheduled_time)
    
    def analyze_market_impact_schedule(self, calendar: EconomicCalendar,
                                     trading_hours: Dict[str, List[int]] = None) -> Dict[str, any]:
        """Market impact schedule tahlili"""
        if trading_hours is None:
            trading_hours = {
                'Asian': list(range(0, 8)),
                'European': list(range(8, 17)),
                'American': list(range(13, 23)),
                'Overlap': list(range(8, 18))
            }
        
        impact_analysis = {
            'high_impact_periods': [],
            'trading_session_analysis': {},
            'risk_hours': [],
            'opportunity_hours': []
        }
        
        # Group events by impact level and time
        events_by_hour = {}
        for event in calendar.events:
            hour = event.scheduled_time.hour
            if hour not in events_by_hour:
                events_by_hour[hour] = []
            events_by_hour[hour].append(event)
        
        # Analyze each hour
        for hour, hour_events in events_by_hour.items():
            high_impact_count = len([e for e in hour_events if e.importance == 'high'])
            medium_impact_count = len([e for e in hour_events if e.importance == 'medium'])
            
            total_impact_score = high_impact_count * 3 + medium_impact_count * 1
            
            if total_impact_score >= 3:  # High risk threshold
                impact_analysis['risk_hours'].append({
                    'hour': hour,
                    'high_impact_events': high_impact_count,
                    'medium_impact_events': medium_impact_count,
                    'total_impact_score': total_impact_score,
                    'events': [e.name for e in hour_events]
                })
            elif total_impact_score >= 1:  # Opportunity threshold
                impact_analysis['opportunity_hours'].append({
                    'hour': hour,
                    'impact_score': total_impact_score,
                    'events': [e.name for e in hour_events]
                })
        
        # Session-based analysis
        for session_name, hours in trading_hours.items():
            session_events = []
            for hour in hours:
                if hour in events_by_hour:
                    session_events.extend(events_by_hour[hour])
            
            if session_events:
                high_impact_in_session = len([e for e in session_events if e.importance == 'high'])
                total_impact = sum(e.market_impact_bps for e in session_events)
                
                impact_analysis['trading_session_analysis'][session_name] = {
                    'total_events': len(session_events),
                    'high_impact_events': high_impact_in_session,
                    'total_expected_impact_bps': total_impact,
                    'avg_impact_per_event': total_impact / len(session_events),
                    'event_breakdown': {
                        category: len([e for e in session_events if e.category == category])
                        for category in self.event_categories.keys()
                    }
                }
        
        return impact_analysis
    
    def create_economic_calendar_trading_strategy(self, calendar: EconomicCalendar,
                                                risk_tolerance: str = 'medium') -> Dict[str, any]:
        """Iqtisodiy calendar asosida trading strategiyasi"""
        strategy = {
            'overall_approach': '',
            'avoid_periods': [],
            'optimal_periods': [],
            'position_sizing': {},
            'risk_management': {},
            'currency_strategy': {}
        }
        
        # Get high impact events
        high_impact_events = [e for e in calendar.events if e.importance == 'high']
        
        # Risk-based approach
        if risk_tolerance == 'low':
            strategy['overall_approach'] = 'avoid_economic_events'
            strategy['avoid_periods'] = [
                {
                    'event': e.name,
                    'time': e.scheduled_time,
                    'currency': e.currency,
                    'avoid_hours_before': 2,
                    'avoid_hours_after': 4
                } for e in high_impact_events
            ]
        elif risk_tolerance == 'high':
            strategy['overall_approach'] = 'economic_event_trading'
            strategy['optimal_periods'] = [
                {
                    'event': e.name,
                    'time': e.scheduled_time,
                    'currency': e.currency,
                    'expected_impact_bps': e.market_impact_bps,
                    'trading_opportunity': 'post_event_reversal'
                } for e in high_impact_events
            ]
        else:  # medium
            strategy['overall_approach'] = 'selective_economic_trading'
            strategy['optimal_periods'] = [
                {
                    'event': e.name,
                    'time': e.scheduled_time,
                    'currency': e.currency,
                    'expected_impact_bps': e.market_impact_bps,
                    'trading_opportunity': 'careful_scalping'
                } for e in high_impact_events if e.category in ['employment', 'growth']
            ]
        
        # Position sizing
        strategy['position_sizing'] = {
            'base_multiplier': 0.3 if risk_tolerance == 'low' else 0.6 if risk_tolerance == 'medium' else 0.8,
            'pre_event_reduction': 0.5,
            'post_event_adjustment': 'gradual_rebuild',
            'max_exposure_per_event': 0.05 if risk_tolerance == 'low' else 0.10
        }
        
        # Risk management
        strategy['risk_management'] = {
            'stop_loss_multiplier': 1.5 if risk_tolerance == 'low' else 2.0,
            'max_correlation_risk': 0.3,
            'volatility_adjustment': True,
            'emergency_close_threshold': 3,  # 3% maximum loss
            'economic_event_buffer_minutes': 60 if risk_tolerance == 'low' else 30
        }
        
        # Currency strategy
        currency_exposure = {}
        for event in high_impact_events:
            currency = event.currency
            if currency not in currency_exposure:
                currency_exposure[currency] = {'event_count': 0, 'total_impact': 0}
            currency_exposure[currency]['event_count'] += 1
            currency_exposure[currency]['total_impact'] += event.market_impact_bps
        
        strategy['currency_strategy'] = {
            'exposure_by_currency': currency_exposure,
            'recommended_max_exposure': {
                'USD': 0.40 if risk_tolerance == 'high' else 0.30,
                'EUR': 0.35 if risk_tolerance == 'high' else 0.25,
                'GBP': 0.30 if risk_tolerance == 'high' else 0.20,
                'JPY': 0.25 if risk_tolerance == 'high' else 0.15,
                'default': 0.10 if risk_tolerance == 'high' else 0.05
            },
            'correlation_awareness': True,
            'diversification_recommendation': 'focus_on_major_currencies'
        }
        
        return strategy
    
    def generate_economic_calendar_alerts(self, calendar: EconomicCalendar,
                                        alert_hours_ahead: int = 24) -> List[Dict]:
        """Iqtisodiy calendar ogohlantirishlari"""
        alerts = []
        current_time = TimeUtils.get_current_utc_time()
        alert_end_time = current_time + timedelta(hours=alert_hours_ahead)
        
        # Get events in the alert window
        alert_events = [
            event for event in calendar.events
            if current_time <= event.scheduled_time <= alert_end_time
        ]
        
        for event in alert_events:
            time_until = event.scheduled_time - current_time
            hours_until = time_until.total_seconds() / 3600
            
            # High impact event alerts
            if event.importance == 'high':
                if hours_until <= 1:  # Within 1 hour
                    alerts.append({
                        'type': 'high_impact_imminent',
                        'event': event.name,
                        'currency': event.currency,
                        'country': event.country,
                        'hours_until': round(hours_until, 1),
                        'expected_impact_bps': event.market_impact_bps,
                        'message': f"Yuqori ta'sirli {event.country} {event.name} {round(hours_until, 1)} soatdan keyin",
                        'action': 'Position sizes ni kamaytiring, stops adjust qiling'
                    })
                elif hours_until <= 6:  # Within 6 hours
                    alerts.append({
                        'type': 'high_impact_approaching',
                        'event': event.name,
                        'currency': event.currency,
                        'country': event.country,
                        'hours_until': round(hours_until, 1),
                        'expected_impact_bps': event.market_impact_bps,
                        'message': f"Yuqori ta'sirli {event.country} {event.name} {round(hours_until, 1)} soatdan keyin",
                        'action': 'Ehtiyotkorlik bilan trade qiling'
                    })
            
            # Multiple high impact events
            same_hour_events = [e for e in alert_events if 
                              e.scheduled_time.hour == event.scheduled_time.hour and
                              e.importance == 'high']
            
            if len(same_hour_events) > 1:
                alerts.append({
                    'type': 'multiple_high_impact_same_hour',
                    'hour': event.scheduled_time.hour,
                    'event_count': len(same_hour_events),
                    'events': [e.name for e in same_hour_events],
                    'message': f"{len(same_hour_events)} ta yuqori ta'sirli voqea shu soatda: {', '.join([e.name for e in same_hour_events[:2]])}...",
                    'action': 'Keng tarqalgan risk - positions ni kamaytiring'
                })
        
        # Cumulative risk assessment
        next_24h_high_impact = [e for e in alert_events if e.importance == 'high']
        total_impact_24h = sum(e.market_impact_bps for e in next_24h_high_impact)
        
        if total_impact_24h > 100:  # Very high cumulative impact
            alerts.append({
                'type': 'high_cumulative_impact',
                'period': 'next_24_hours',
                'total_high_impact_events': len(next_24h_high_impact),
                'total_expected_impact_bps': total_impact_24h,
                'message': f"Keyingi 24 soatda {len(next_24h_high_impact)} ta yuqori ta'sirli voqea (umumiy ta'sir: {total_impact_24h:.0f} bps)",
                'action': 'Risk ni kamaytiring, hedging consider qiling'
            })
        
        return alerts
    
    def optimize_trading_around_economic_events(self, upcoming_events: List[EconomicEvent],
                                              market_data: pd.DataFrame) -> Dict[str, any]:
        """Iqtisodiy voqealar atrofida trading optimizatsiyasi"""
        optimization = {
            'pre_event_strategy': {},
            'during_event_strategy': {},
            'post_event_strategy': {},
            'risk_adjusted_position_sizes': {},
            'expected_outcomes': {}
        }
        
        for event in upcoming_events:
            event_category = self.event_categories.get(event.category, {})
            
            # Pre-event strategy
            optimization['pre_event_strategy'][event.event_id] = {
                'reduce_position_size': 0.5 if event.importance == 'high' else 0.8,
                'tighten_stops': True,
                'close_certain_positions': event.importance == 'high',
                'avoid_new_positions': True,
                'minutes_before_event': 60 if event.importance == 'high' else 30
            }
            
            # During event strategy
            optimization['during_event_strategy'][event.event_id] = {
                'monitor_volatility': True,
                'adjust_stops_dynamically': True,
                'avoid_new_positions': True,
                'wait_for_clarity': True,
                'max_slippage_tolerance': 0.005 if event.importance == 'high' else 0.01
            }
            
            # Post-event strategy
            optimization['post_event_strategy'][event.event_id] = {
                'wait_time_minutes': event_category.get('recovery_hours', 2) * 60,
                'rebuild_positions_gradually': True,
                'watch_for_trend_continuation': True,
                'scalping_opportunities': event.importance == 'high',
                'mean_reversion_setup': event.importance != 'high'
            }
            
            # Risk-adjusted position sizing
            base_position = 1.0
            if event.importance == 'high':
                adjusted_position = base_position * 0.3  # 70% reduction
            elif event.importance == 'medium':
                adjusted_position = base_position * 0.6  # 40% reduction
            else:
                adjusted_position = base_position * 0.8  # 20% reduction
            
            optimization['risk_adjusted_position_sizes'][event.event_id] = {
                'position_size_multiplier': adjusted_position,
                'stop_loss_multiplier': 1.5 if event.importance == 'high' else 1.2,
                'take_profit_multiplier': 0.8 if event.importance == 'high' else 1.0
            }
            
            # Expected outcomes
            surprise_multiplier = 1 + abs(event.surprise_factor)
            expected_volatility = event_category.get('volatility_multiplier', 1.0) * surprise_multiplier
            
            optimization['expected_outcomes'][event.event_id] = {
                'expected_volatility_increase': expected_volatility,
                'probable_price_move_bps': event.market_impact_bps * surprise_multiplier,
                'volatility_duration_hours': event_category.get('recovery_hours', 2),
                'trading_opportunities': self._identify_trading_opportunities(event),
                'risk_factors': self._identify_risk_factors(event)
            }
        
        return optimization
    
    def _identify_trading_opportunities(self, event: EconomicEvent) -> List[str]:
        """Trading imkoniyatlarini aniqlash"""
        opportunities = []
        
        # Based on event type and surprise factor
        if abs(event.surprise_factor) > 0.5:  # Significant surprise
            if event.surprise_factor > 0:
                opportunities.append('positive_surprise_momentum_trade')
            else:
                opportunities.append('negative_surprise_momentum_trade')
        
        # Category-specific opportunities
        if event.category == 'employment':
            opportunities.append('employment_data_reversal_trade')
        elif event.category == 'inflation':
            opportunities.append('inflation_impact_currency_play')
        elif event.category == 'growth':
            opportunities.append('growth_data_momentum_trade')
        
        # Time-based opportunities
        hour = event.scheduled_time.hour
        if 8 <= hour <= 17:  # European session
            opportunities.append('european_session_breakout')
        elif 13 <= hour <= 22:  # American session
            opportunities.append('american_session_momentum')
        
        return opportunities
    
    def _identify_risk_factors(self, event: EconomicEvent) -> List[str]:
        """Risk factorlarni aniqlash"""
        risks = []
        
        # Based on surprise factor
        if abs(event.surprise_factor) > 1.0:  # Major surprise
            risks.append('extreme_price_movement')
            risks.append('whipsaw_risk')
        
        # Based on event importance
        if event.importance == 'high':
            risks.append('liquidity_evaporation')
            risks.append('spread_widening')
        
        # Based on timing
        hour = event.scheduled_time.hour
        if hour < 8 or hour > 22:  # Low liquidity hours
            risks.append('low_liquidity_execution_risk')
        
        # Based on currency
        if event.currency in ['USD', 'EUR', 'GBP', 'JPY']:
            risks.append('high_correlation_with_other_markets')
        
        return risks