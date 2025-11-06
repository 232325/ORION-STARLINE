"""
News Integration System
Economic calendar, central bank va market-moving events integration
"""

import pytz
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from config.market_config import NEWS_IMPACT_LEVELS, CENTRAL_BANK_EVENTS

class EventImpact(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class EventType(Enum):
    CENTRAL_BANK = "central_bank"
    ECONOMIC_DATA = "economic_data"
    CORPORATE_EARNINGS = "corporate_earnings"
    GEOPOLITICAL = "geopolitical"
    MARKET_NEWS = "market_news"

@dataclass
class NewsEvent:
    """Yangilik voqeasi ma'lumotlari"""
    title: str
    event_type: EventType
    country: str
    currency: str
    scheduled_time: datetime
    impact_level: EventImpact
    actual_value: Optional[str] = None
    forecast_value: Optional[str] = None
    previous_value: Optional[str] = None
    volatility_expected: float = 1.0
    affected_assets: List[str] = None
    time_until_event: Optional[timedelta] = None

@dataclass
class NewsImpactAnalysis:
    """Yangilik ta'sir tahlili"""
    event: NewsEvent
    expected_movement: Dict[str, float]  # asset: expected_move_pct
    confidence_level: float
    risk_factors: List[str]
    trading_opportunities: List[Dict[str, str]]
    optimal_entry_time: Optional[datetime]

class NewsIntegrationSystem:
    """Yangiliklar integration tizimi"""
    
    def __init__(self):
        self.impact_levels = NEWS_IMPACT_LEVELS
        self.central_banks = CENTRAL_BANK_EVENTS
        
        # Economic calendar data structure
        self.economic_calendar = {
            "USD": {
                "employment_report": {
                    "impact": "HIGH",
                    "frequency": "monthly",
                    "release_day": "first_friday",
                    "release_time": time(12, 30),  # 12:30 GMT (8:30 EST)
                    "affected_pairs": ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CAD"],
                    "volatility_multiplier": 2.5
                },
                "inflation_data": {
                    "impact": "HIGH", 
                    "frequency": "monthly",
                    "release_day": "middle_month",
                    "release_time": time(12, 30),
                    "affected_pairs": ["EUR/USD", "GBP/USD", "USD/JPY"],
                    "volatility_multiplier": 2.0
                },
                "gdp_release": {
                    "impact": "MEDIUM",
                    "frequency": "quarterly", 
                    "release_day": "month_end",
                    "release_time": time(12, 30),
                    "affected_pairs": ["EUR/USD", "GBP/USD"],
                    "volatility_multiplier": 1.8
                },
                "retail_sales": {
                    "impact": "MEDIUM",
                    "frequency": "monthly",
                    "release_day": "mid_month", 
                    "release_time": time(12, 30),
                    "affected_pairs": ["USD/CAD", "USD/JPY"],
                    "volatility_multiplier": 1.4
                }
            },
            "EUR": {
                "ecb_rate_decision": {
                    "impact": "HIGH",
                    "frequency": "every_6_weeks",
                    "release_time": time(12, 0),  # 12:00 GMT
                    "affected_pairs": ["EUR/USD", "EUR/GBP", "EUR/JPY"],
                    "volatility_multiplier": 2.2
                },
                "ecb_press_conference": {
                    "impact": "HIGH",
                    "frequency": "every_6_weeks",
                    "release_time": time(12, 30),  # 12:30 GMT
                    "affected_pairs": ["EUR/USD", "EUR/GBP", "EUR/JPY"],
                    "volatility_multiplier": 1.8
                },
                "german_cpi": {
                    "impact": "MEDIUM",
                    "frequency": "monthly",
                    "release_time": time(6, 0),  # 06:00 GMT
                    "affected_pairs": ["EUR/USD", "EUR/GBP"],
                    "volatility_multiplier": 1.5
                }
            },
            "GBP": {
                "boe_rate_decision": {
                    "impact": "HIGH",
                    "frequency": "monthly",
                    "release_time": time(12, 0),  # 12:00 GMT
                    "affected_pairs": ["GBP/USD", "GBP/EUR", "GBP/JPY"],
                    "volatility_multiplier": 2.0
                },
                "uk_cpi": {
                    "impact": "MEDIUM",
                    "frequency": "monthly", 
                    "release_time": time(8, 30),  # 08:30 GMT
                    "affected_pairs": ["GBP/USD", "GBP/EUR"],
                    "volatility_multiplier": 1.6
                }
            },
            "JPY": {
                "boj_rate_decision": {
                    "impact": "HIGH",
                    "frequency": "monthly",
                    "release_time": time(6, 0),  # 06:00 GMT
                    "affected_pairs": ["USD/JPY", "EUR/JPY", "GBP/JPY"],
                    "volatility_multiplier": 1.9
                }
            }
        }
        
        # Market-moving events database
        self.market_events = {
            "election_results": {
                "impact": "HIGH",
                "affected_markets": ["forex", "metals", "stocks"],
                "volatility_duration": timedelta(hours=6),
                "uncertainty_factor": 2.0
            },
            "war_conflicts": {
                "impact": "VERY_HIGH", 
                "affected_markets": ["gold", "oil", "safe_haven_currencies"],
                "volatility_duration": timedelta(hours=12),
                "uncertainty_factor": 3.0
            },
            "natural_disasters": {
                "impact": "MEDIUM",
                "affected_markets": ["local_currency", "regional_stocks"],
                "volatility_duration": timedelta(hours=3),
                "uncertainty_factor": 1.5
            }
        }
    
    def get_upcoming_news_events(self, current_time: datetime, hours_ahead: int = 24) -> List[NewsEvent]:
        """Berilgan soat ichidagi yangilik voqealarini olish"""
        
        events = []
        end_time = current_time + timedelta(hours=hours_ahead)
        
        # Economic calendar events
        events.extend(self._get_economic_events(current_time, end_time))
        
        # Central bank events  
        events.extend(self._get_central_bank_events(current_time, end_time))
        
        # Corporate earnings (simplified)
        earnings_events = self._get_earnings_events(current_time, end_time)
        if earnings_events:
            events.extend(earnings_events)
        
        # Time until event hisoblash
        for event in events:
            event.time_until_event = event.scheduled_time - current_time
        
        return sorted(events, key=lambda x: x.scheduled_time)
    
    def _get_economic_events(self, start_time: datetime, end_time: datetime) -> List[NewsEvent]:
        """Economic calendar events"""
        
        events = []
        current_utc = start_time.astimezone(pytz.UTC)
        
        # Har bir currency uchun
        for currency, data in self.economic_calendar.items():
            for event_name, event_info in data.items():
                
                # Next occurrence hisoblash
                next_occurrence = self._calculate_next_economic_event(
                    start_time, event_name, event_info, currency
                )
                
                if next_occurrence and next_occurrence <= end_time:
                    impact_level = EventImpact(event_info["impact"].lower())
                    
                    event = NewsEvent(
                        title=event_name.replace("_", " ").title(),
                        event_type=EventType.ECONOMIC_DATA,
                        country=self._get_country_from_currency(currency),
                        currency=currency,
                        scheduled_time=next_occurrence,
                        impact_level=impact_level,
                        volatility_expected=event_info["volatility_multiplier"],
                        affected_assets=event_info["affected_pairs"]
                    )
                    
                    events.append(event)
        
        return events
    
    def _calculate_next_economic_event(self, current_time: datetime, event_name: str, 
                                     event_info: Dict, currency: str) -> Optional[datetime]:
        """Economic event uchun keyingi occurrence hisoblash"""
        
        current_utc = current_time.astimezone(pytz.UTC)
        release_time = event_info["release_time"]
        frequency = event_info.get("frequency", "monthly")
        
        if frequency == "monthly":
            # Har oygi events
            next_month = current_utc.replace(day=1) + timedelta(days=32)
            next_month = next_month.replace(day=1)
            
            # Specific day logic
            if "first_friday" in event_info.get("release_day", ""):
                # Birinchi payshanba
                first_friday = next_month
                while first_friday.weekday() != 4:  # Friday = 4
                    first_friday += timedelta(days=1)
                
                event_datetime = first_friday.replace(
                    hour=release_time.hour,
                    minute=release_time.minute,
                    second=0,
                    microsecond=0
                )
                
                # Agar bu oygi voqea hali o'tmagan bo'lsa
                if event_datetime <= current_utc:
                    # Keyingi oygi voqea
                    next_month_2 = current_utc.replace(day=1) + timedelta(days=32)
                    next_month_2 = next_month_2.replace(day=1)
                    
                    # Calculate next first Friday for that month
                    temp_date = next_month_2
                    while temp_date.weekday() != 4:
                        temp_date += timedelta(days=1)
                    
                    event_datetime = temp_date.replace(
                        hour=release_time.hour,
                        minute=release_time.minute,
                        second=0,
                        microsecond=0
                    )
                
                return event_datetime
            
            elif "month_end" in event_info.get("release_day", ""):
                # Oyning oxiri
                month_end = next_month - timedelta(days=1)
                return month_end.replace(
                    hour=release_time.hour,
                    minute=release_time.minute,
                    second=0,
                    microsecond=0
                )
        
        elif frequency == "quarterly":
            # Quarterly events - qo'lda hisoblash
            current_quarter = (current_utc.month - 1) // 3 + 1
            next_quarter_month = current_quarter * 3 + 3
            if next_quarter_month > 12:
                next_quarter_month = next_quarter_month - 12
                next_year = current_utc.year + 1
            else:
                next_year = current_utc.year
            
            return datetime(next_year, next_quarter_month, 15, 12, 30, tzinfo=pytz.UTC)
        
        return None
    
    def _get_central_bank_events(self, start_time: datetime, end_time: datetime) -> List[NewsEvent]:
        """Central bank events"""
        
        events = []
        
        for bank_code, bank_data in self.central_banks.items():
            # Decision time
            decision_time = self._get_next_bank_decision(start_time, bank_code)
            
            if decision_time and decision_time <= end_time:
                event = NewsEvent(
                    title=f"{bank_data['name']} Rate Decision",
                    event_type=EventType.CENTRAL_BANK,
                    country=bank_data["name"],
                    currency=bank_code,
                    scheduled_time=decision_time,
                    impact_level=EventImpact.HIGH,
                    volatility_expected=2.5,
                    affected_assets=bank_data["impact_asset_classes"]
                )
                events.append(event)
            
            # Press conference
            if "press_conference_time" in bank_data:
                press_time = decision_time + timedelta(minutes=30)
                if press_time <= end_time:
                    press_event = NewsEvent(
                        title=f"{bank_data['name']} Press Conference",
                        event_type=EventType.CENTRAL_BANK,
                        country=bank_data["name"],
                        currency=bank_code,
                        scheduled_time=press_time,
                        impact_level=EventImpact.MEDIUM,
                        volatility_expected=1.8,
                        affected_assets=bank_data["impact_asset_classes"]
                    )
                    events.append(press_event)
        
        return events
    
    def _get_next_bank_decision(self, current_time: datetime, bank_code: str) -> Optional[datetime]:
        """Bank decision uchun keyingi sana"""
        
        current_utc = current_time.astimezone(pytz.UTC)
        
        if bank_code == "FED":
            # Fed - 8 marta yiliga
            fed_dates = [
                datetime(2025, 1, 29, 18, 0, tzinfo=pytz.UTC),
                datetime(2025, 3, 19, 18, 0, tzinfo=pytz.UTC),
                datetime(2025, 4, 30, 18, 0, tzinfo=pytz.UTC),
                datetime(2025, 6, 11, 18, 0, tzinfo=pytz.UTC),
                datetime(2025, 7, 30, 18, 0, tzinfo=pytz.UTC),
                datetime(2025, 9, 17, 18, 0, tzinfo=pytz.UTC),
                datetime(2025, 11, 5, 18, 0, tzinfo=pytz.UTC),
                datetime(2025, 12, 17, 18, 0, tzinfo=pytz.UTC)
            ]
            
            for date in fed_dates:
                if date > current_utc:
                    return date
        
        elif bank_code == "ECB":
            # ECB - har 6 haftada
            ecb_dates = [
                datetime(2025, 1, 30, 12, 0, tzinfo=pytz.UTC),
                datetime(2025, 3, 13, 12, 0, tzinfo=pytz.UTC),
                datetime(2025, 4, 24, 12, 0, tzinfo=pytz.UTC),
                datetime(2025, 6, 5, 12, 0, tzinfo=pytz.UTC),
                datetime(2025, 7, 17, 12, 0, tzinfo=pytz.UTC),
                datetime(2025, 9, 11, 12, 0, tzinfo=pytz.UTC),
                datetime(2025, 10, 23, 12, 0, tzinfo=pytz.UTC),
                datetime(2025, 12, 4, 12, 0, tzinfo=pytz.UTC)
            ]
            
            for date in ecb_dates:
                if date > current_utc:
                    return date
        
        # BOE, BOJ uchun ham o'xshash
        elif bank_code == "BOE":
            # Har oygi
            return current_utc.replace(day=1) + timedelta(days=30, hours=12)
        
        elif bank_code == "BOJ":
            # Har oygi
            return current_utc.replace(day=1) + timedelta(days=15, hours=6)
        
        return None
    
    def _get_earnings_events(self, start_time: datetime, end_time: datetime) -> List[NewsEvent]:
        """Corporate earnings events (simplified)"""
        
        # Bu real implementatsiyada API dan olinadi
        # Hozircha mock data
        earnings_events = [
            NewsEvent(
                title="Major Bank Q4 Earnings",
                event_type=EventType.CORPORATE_EARNINGS,
                country="US",
                currency="USD",
                scheduled_time=start_time + timedelta(hours=2),
                impact_level=EventImpact.MEDIUM,
                volatility_expected=1.5,
                affected_assets=["USD", "bank_stocks"]
            )
        ]
        
        return earnings_events
    
    def _get_country_from_currency(self, currency: str) -> str:
        """Currency dan country olish"""
        currency_countries = {
            "USD": "US",
            "EUR": "EU", 
            "GBP": "UK",
            "JPY": "JP",
            "AUD": "AU",
            "CAD": "CA",
            "CHF": "CH",
            "NZD": "NZ"
        }
        return currency_countries.get(currency, currency)
    
    def analyze_news_impact(self, event: NewsEvent, current_time: datetime) -> NewsImpactAnalysis:
        """Voqea ta'sirini tahlil qilish"""
        
        # Expected movement hisoblash
        expected_movement = self._calculate_expected_movement(event)
        
        # Confidence level
        confidence = self._calculate_confidence_level(event)
        
        # Risk factors
        risk_factors = self._identify_risk_factors(event)
        
        # Trading opportunities
        opportunities = self._identify_trading_opportunities(event)
        
        # Optimal entry time
        optimal_entry = self._calculate_optimal_entry_time(event, current_time)
        
        return NewsImpactAnalysis(
            event=event,
            expected_movement=expected_movement,
            confidence_level=confidence,
            risk_factors=risk_factors,
            trading_opportunities=opportunities,
            optimal_entry_time=optimal_entry
        )
    
    def _calculate_expected_movement(self, event: NewsEvent) -> Dict[str, float]:
        """Expected currency movement hisoblash"""
        
        movement = {}
        base_movement = 0.01  # 1% base movement
        
        # Impact level ga qarab
        if event.impact_level == EventImpact.HIGH:
            multiplier = event.volatility_expected
        elif event.impact_level == EventImpact.MEDIUM:
            multiplier = event.volatility_expected * 0.6
        else:
            multiplier = event.volatility_expected * 0.3
        
        for asset in event.affected_assets or []:
            if "/" in asset:  # Currency pair
                # Major pairs - higher movement
                if any(curr in asset for curr in ["USD", "EUR", "GBP", "JPY"]):
                    movement[asset] = base_movement * multiplier * 1.5
                else:
                    movement[asset] = base_movement * multiplier
            elif asset in ["gold", "silver"]:  # Precious metals
                movement[asset] = base_movement * multiplier * 1.2
        
        return movement
    
    def _calculate_confidence_level(self, event: NewsEvent) -> float:
        """Confidence level hisoblash"""
        
        base_confidence = 0.7
        
        # Event type ga qarab
        if event.event_type == EventType.CENTRAL_BANK:
            confidence = 0.9  # High confidence for bank decisions
        elif event.event_type == EventType.ECONOMIC_DATA:
            confidence = 0.8  # Good confidence for economic data
        else:
            confidence = 0.6  # Lower confidence for earnings
        
        # Impact level ga qarab
        if event.impact_level == EventImpact.HIGH:
            confidence *= 1.1  # Boost confidence for high impact events
        
        return min(confidence, 1.0)
    
    def _identify_risk_factors(self, event: NewsEvent) -> List[str]:
        """Risk factors aniqlash"""
        
        risks = []
        
        # Event type ga qarab
        if event.event_type == EventType.CENTRAL_BANK:
            risks.append("Unexpected_rate_decision")
            risks.append("Surprising_forward_guidance")
        
        elif event.event_type == EventType.ECONOMIC_DATA:
            risks.append("Data_revision_risk")
            risks.append("Seasonal_adjustment_issues")
        
        elif event.event_type == EventType.CORPORATE_EARNINGS:
            risks.append("Guidance_changes")
            risks.append("One_time_charges")
        
        # Time of day ga qarab
        if event.scheduled_time.hour < 8:
            risks.append("Asian_session_impact")
        elif event.scheduled_time.hour > 17:
            risks.append("After_hours_effect")
        
        return risks
    
    def _identify_trading_opportunities(self, event: NewsEvent) -> List[Dict[str, str]]:
        """Trading opportunities aniqlash"""
        
        opportunities = []
        
        # Pre-event positioning
        opportunities.append({
            "type": "pre_event_position",
            "strategy": "fade_bias",
            "reason": f"Position before {event.impact_level.value} impact event",
            "timeframe": "15-30 minutes before event"
        })
        
        # Event announcement
        if event.impact_level == EventImpact.HIGH:
            opportunities.append({
                "type": "event_trading",
                "strategy": "immediate_reaction",
                "reason": "Capture initial volatility",
                "timeframe": "0-5 minutes after release"
            })
        
        # Post-event consolidation
        opportunities.append({
            "type": "post_event",
            "strategy": "trend_continuation",
            "reason": "Follow established direction after initial spike",
            "timeframe": "1-4 hours after event"
        })
        
        return opportunities
    
    def _calculate_optimal_entry_time(self, event: NewsEvent, current_time: datetime) -> Optional[datetime]:
        """Optimal entry time hisoblash"""
        
        time_until_event = event.scheduled_time - current_time
        
        # High impact events - 30 minutes before
        if event.impact_level == EventImpact.HIGH and time_until_event > timedelta(minutes=30):
            return event.scheduled_time - timedelta(minutes=30)
        
        # Medium impact - 15 minutes before
        elif event.impact_level == EventImpact.MEDIUM and time_until_event > timedelta(minutes=15):
            return event.scheduled_time - timedelta(minutes=15)
        
        return None
    
    def get_news_calendar_summary(self, current_time: datetime, days_ahead: int = 7) -> Dict[str, any]:
        """Yangiliklar kalendari umumiy ko'rinishi"""
        
        start_time = current_time
        end_time = current_time + timedelta(days=days_ahead)
        
        upcoming_events = self.get_upcoming_news_events(start_time, hours_ahead=days_ahead * 24)
        
        # High impact events
        high_impact_events = [e for e in upcoming_events if e.impact_level == EventImpact.HIGH]
        
        # By currency breakdown
        by_currency = {}
        for event in upcoming_events:
            if event.currency not in by_currency:
                by_currency[event.currency] = []
            by_currency[event.currency].append({
                "title": event.title,
                "time": event.scheduled_time.isoformat(),
                "impact": event.impact_level.value
            })
        
        # By day breakdown
        by_day = {}
        for event in upcoming_events:
            day_key = event.scheduled_time.strftime("%Y-%m-%d")
            if day_key not in by_day:
                by_day[day_key] = []
            by_day[day_key].append({
                "title": event.title,
                "time": event.scheduled_time.strftime("%H:%M GMT"),
                "impact": event.impact_level.value,
                "currency": event.currency
            })
        
        return {
            "summary": {
                "total_events": len(upcoming_events),
                "high_impact_events": len(high_impact_events),
                "most_affected_currency": max(by_currency.keys(), key=lambda x: len(by_currency[x])) if by_currency else None
            },
            "upcoming_events": [
                {
                    "title": event.title,
                    "time": event.scheduled_time.isoformat(),
                    "impact": event.impact_level.value,
                    "currency": event.currency,
                    "time_until": str(event.time_until_event) if event.time_until_event else None
                }
                for event in upcoming_events[:10]  # Top 10 events
            ],
            "by_currency": by_currency,
            "by_day": by_day,
            "high_impact_dates": [
                {
                    "date": event.scheduled_time.strftime("%Y-%m-%d"),
                    "event": event.title,
                    "impact": event.impact_level.value
                }
                for event in high_impact_events
            ]
        }
    
    def optimize_news_trading_strategy(self, strategy_type: str, current_time: datetime) -> Dict[str, any]:
        """News trading strategy optimizatsiyasi"""
        
        upcoming_events = self.get_upcoming_news_events(current_time, hours_ahead=24)
        
        recommendations = []
        
        # Strategy type ga qarab
        if strategy_type.lower() == "event_driven":
            # Event-driven trading
            high_impact = [e for e in upcoming_events if e.impact_level == EventImpact.HIGH]
            
            if high_impact:
                for event in high_impact[:3]:  # Top 3 high impact events
                    analysis = self.analyze_news_impact(event, current_time)
                    recommendations.append({
                        "action": "EVENT_SETUP",
                        "event": event.title,
                        "time": event.scheduled_time.isoformat(),
                        "expected_movement": analysis.expected_movement,
                        "confidence": f"{analysis.confidence_level:.1%}",
                        "opportunities": len(analysis.trading_opportunities)
                    })
        
        elif strategy.lower() == "position_sizing":
            # Position sizing based on news
            for event in upcoming_events[:5]:
                if event.impact_level in [EventImpact.HIGH, EventImpact.MEDIUM]:
                    volatility = event.volatility_expected
                    position_size = min(1.0 / volatility, 0.5)  # Reduce size for high volatility
                    
                    recommendations.append({
                        "action": "ADJUST_POSITION_SIZE",
                        "event": event.title,
                        "time": event.scheduled_time.isoformat(),
                        "recommended_size": f"{position_size:.1%}",
                        "reason": f"High volatility event: {volatility:.1f}x"
                    })
        
        elif strategy.lower() == "risk_management":
            # Risk management
            for event in upcoming_events:
                if event.impact_level == EventImpact.HIGH and event.time_until_event and event.time_until_event.total_seconds() < 7200:  # 2 hours
                    recommendations.append({
                        "action": "REDUCE_EXPOSURE",
                        "event": event.title,
                        "time_remaining": str(event.time_until_event),
                        "reason": f"High impact event in {event.time_until_event}",
                        "recommendation": "Close positions or hedge exposure"
                    })
        
        return {
            "strategy_type": strategy_type,
            "current_time": current_time.isoformat(),
            "events_analyzed": len(upcoming_events),
            "high_impact_events": len([e for e in upcoming_events if e.impact_level == EventImpact.HIGH]),
            "recommendations": recommendations,
            "next_high_impact": upcoming_events[0].title if upcoming_events else None
        }