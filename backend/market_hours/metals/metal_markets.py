"""
Metal Markets Analyzer
Metal bozorlari (LME, COMEX) tahlil va optimizatsiyasi
"""

import pytz
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from config.market_config import METAL_MARKETS, MetalMarket, INVENTORY_REPORTING

class TradingPhase(Enum):
    PRE_MARKET = "pre_market"
    REGULAR_HOURS = "regular_hours"
    LUNCH_BREAK = "lunch_break"
    OVERNIGHT = "overnight"
    CLOSING = "closing"
    CLOSED = "closed"

class MetalType(Enum):
    PRECIOUS = "precious"
    INDUSTRIAL = "industrial"
    BASE = "base"

class MarketSession(Enum):
    RING_TRADING = "ring_trading"
    ELECTRONIC = "electronic"
    CLOSING = "closing"

@dataclass
class MetalMarketAnalysis:
    """Metal bozori tahlil ma'lumotlari"""
    market_name: str
    market_code: MetalMarket
    is_open: bool
    current_phase: TradingPhase
    active_sessions: List[str]
    metals_trading: List[str]
    volatility_trend: str
    inventory_impact: float
    optimal_instruments: List[str]
    next_events: List[Dict[str, any]]

class MetalMarketsAnalyzer:
    """Metal bozorlarini tahlil qiluvchi klass"""
    
    def __init__(self):
        self.markets = METAL_MARKETS
        self.inventory_reports = INVENTORY_REPORTING
        
        # Metal classifications
        self.metal_classifications = {
            "gold": {"type": MetalType.PRECIOUS, "primary_market": MetalMarket.COMEX, "volatility": "medium"},
            "silver": {"type": MetalType.PRECIOUS, "primary_market": MetalMarket.COMEX, "volatility": "high"},
            "platinum": {"type": MetalType.PRECIOUS, "primary_market": MetalMarket.COMEX, "volatility": "high"},
            "palladium": {"type": MetalType.PRECIOUS, "primary_market": MetalMarket.COMEX, "volatility": "very_high"},
            "copper": {"type": MetalType.INDUSTRIAL, "primary_market": MetalMarket.LME, "volatility": "medium"},
            "aluminum": {"type": MetalType.INDUSTRIAL, "primary_market": MetalMarket.LME, "volatility": "low"},
            "lead": {"type": MetalType.BASE, "primary_market": MetalMarket.LME, "volatility": "medium"},
            "zinc": {"type": MetalType.BASE, "primary_market": MetalMarket.LME, "volatility": "high"},
            "nickel": {"type": MetalType.BASE, "primary_market": MetalMarket.LME, "volatility": "very_high"},
            "tin": {"type": MetalType.BASE, "primary_market": MetalMarket.LME, "volatility": "medium"}
        }
        
        # Seasonal patterns
        self.seasonal_patterns = {
            "gold": {
                "high_demand_months": [11, 12, 1, 2],  # Festival/traditional demand
                "low_demand_months": [6, 7, 8],       # Summer doldrums
                "volatility_peaks": [10, 11, 12]      # Year-end positioning
            },
            "copper": {
                "high_demand_months": [3, 4, 5, 9, 10], # Chinese manufacturing
                "low_demand_months": [1, 2, 8],         # Chinese New Year, summer
                "volatility_peaks": [3, 9]              # Supply disruptions
            }
        }
    
    def analyze_current_metal_markets(self, current_time: datetime) -> List[MetalMarketAnalysis]:
        """Barcha metal bozorlarini tahlil qilish"""
        
        analysis_results = []
        
        for market_enum in MetalMarket:
            market_data = self.markets[market_enum]
            analysis = self._analyze_individual_market(current_time, market_enum, market_data)
            if analysis:
                analysis_results.append(analysis)
        
        return analysis_results
    
    def _analyze_individual_market(self, current_time: datetime, market_enum: MetalMarket, market_data: Dict) -> Optional[MetalMarketAnalysis]:
        """Individual metal bozorini tahlil qilish"""
        
        current_utc = current_time.astimezone(pytz.UTC)
        current_time_only = current_utc.time()
        current_day = current_utc.weekday()  # 0 = Monday
        
        # Weekend trading check
        if not market_data.get("weekend_trading", False) and current_day >= 5:
            return MetalMarketAnalysis(
                market_name=market_data["name"],
                market_code=market_enum,
                is_open=False,
                current_phase=TradingPhase.CLOSED,
                active_sessions=[],
                metals_trading=[],
                volatility_trend="weekend_closed",
                inventory_impact=0.0,
                optimal_instruments=[],
                next_events=[]
            )
        
        # Active sessions
        active_sessions = []
        current_phase = TradingPhase.CLOSED
        metals_trading = []
        
        # Har bir session tekshirish
        for session_name, session_data in market_data["trading_hours"].items():
            start_time = session_data["start_time"]
            end_time = session_data["end_time"]
            
            if self._is_time_in_session(current_time_only, start_time, end_time):
                active_sessions.append(session_name)
                current_phase = self._determine_trading_phase(current_time_only, session_data, session_name)
                
                # Session uchun metals
                session_metals = self._get_metals_for_session(market_enum, session_name)
                metals_trading.extend(session_metals)
        
        # Break periods tekshirish
        if "lunch_break" in market_data:
            lunch_start = market_data["lunch_break"]["start_time"]
            lunch_end = market_data["lunch_break"]["end_time"]
            if lunch_start <= current_time_only < lunch_end:
                current_phase = TradingPhase.LUNCH_BREAK
        
        if "maintenance_break" in market_data:
            maintenance_start = market_data["maintenance_break"]["start_time"]
            maintenance_end = market_data["maintenance_break"]["end_time"]
            if maintenance_start <= current_time_only < maintenance_end:
                current_phase = TradingPhase.OVERNIGHT
        
        # Volatility trend
        volatility_trend = self._calculate_volatility_trend(current_time, market_enum, active_sessions)
        
        # Inventory impact
        inventory_impact = self._calculate_inventory_impact(current_time, market_enum)
        
        # Optimal instruments
        optimal_instruments = self._get_optimal_instruments(market_enum, active_sessions, current_phase)
        
        # Next events
        next_events = self._get_next_market_events(current_time, market_enum)
        
        return MetalMarketAnalysis(
            market_name=market_data["name"],
            market_code=market_enum,
            is_open=len(active_sessions) > 0,
            current_phase=current_phase,
            active_sessions=active_sessions,
            metals_trading=list(set(metals_trading)),  # Remove duplicates
            volatility_trend=volatility_trend,
            inventory_impact=inventory_impact,
            optimal_instruments=optimal_instruments,
            next_events=next_events
        )
    
    def _is_time_in_session(self, current_time: time, start_time: time, end_time: time) -> bool:
        """Vaqt sessiya ichida ekanligini tekshirish"""
        return start_time <= current_time < end_time
    
    def _determine_trading_phase(self, current_time: time, session_data: Dict, session_name: str) -> TradingPhase:
        """Trading fazasini aniqlash"""
        
        if "pre_market" in session_name.lower():
            return TradingPhase.PRE_MARKET
        elif "regular" in session_name.lower():
            return TradingPhase.REGULAR_HOURS
        elif "closing" in session_name.lower():
            return TradingPhase.CLOSING
        else:
            return TradingPhase.REGULAR_HOURS
    
    def _get_metals_for_session(self, market_enum: MetalMarket, session_name: str) -> List[str]:
        """Session uchun trade qilinuvchi metallar"""
        
        base_instruments = self.markets[market_enum]["instruments"]
        
        # Session turiga qarab filter
        if "ring_trading" in session_name:
            # Ring trading - fizik delivered metals
            return [metal for metal in base_instruments if metal != "tin"]  # Tin electronic only
        elif "electronic" in session_name:
            # Electronic trading - barcha metals
            return base_instruments
        else:
            return base_instruments
    
    def _calculate_volatility_trend(self, current_time: datetime, market_enum: MetalMarket, active_sessions: List[str]) -> str:
        """Volatil trendni hisoblash"""
        
        current_hour = current_time.hour
        
        # Ring trading hours - yuqori volatil
        if "morning" in active_sessions or "afternoon" in active_sessions:
            if current_hour in [8, 9, 10, 13, 14]:  # Peak hours
                return "very_high_volatility"
            elif current_hour in [11, 12, 15, 16]:  # Active hours
                return "high_volatility"
            else:
                return "moderate_volatility"
        
        # Electronic sessions - barqaror
        elif "lme_select" in active_sessions or "pre_market" in active_sessions:
            return "moderate_volatility"
        
        # Pre-market/After-hours
        else:
            return "low_volatility"
    
    def _calculate_inventory_impact(self, current_time: datetime, market_enum: MetalMarket) -> float:
        """Inventory reporting ta'sirini hisoblash"""
        
        current_utc = current_time.astimezone(pytz.UTC)
        current_time_only = current_utc.time()
        current_day = current_utc.weekday()
        
        # LME inventory reports
        if market_enum == MetalMarket.LME:
            # Daily stocks - har kuni 08:00 GMT
            if current_time_only.hour == 8 and current_time_only.minute <= 30:
                return 0.8  # High impact before release
            
            # Weekly position - juma 15:00 GMT
            elif current_day == 4 and current_time_only.hour == 15:  # Friday
                return 0.9  # Very high impact
        
        # COMEX inventory reports
        elif market_enum == MetalMarket.COMEX:
            # Commitment of traders - juma 14:30 GMT
            if current_day == 4 and 14 <= current_time_only.hour < 15:
                return 0.9
            
            # Gold/Silver inventories - seshanba va payshanba 21:00 GMT
            elif current_time_only.hour == 21:
                if current_day == 1 or current_day == 3:  # Tuesday or Thursday
                    return 0.7
        
        return 0.0  # Normal trading
    
    def _get_optimal_instruments(self, market_enum: MetalMarket, active_sessions: List[str], phase: TradingPhase) -> List[str]:
        """Optimal instruments tanlash"""
        
        instruments = self.markets[market_enum]["instruments"]
        optimal = []
        
        for instrument in instruments:
            classification = self.metal_classifications.get(instrument, {})
            metal_type = classification.get("type", MetalType.BASE)
            volatility = classification.get("volatility", "medium")
            
            # Session va fazaga qarab tanlash
            if "ring_trading" in str(active_sessions):
                # Ring trading - yuqori likvidlik
                if metal_type in [MetalType.PRECIOUS, MetalType.INDUSTRIAL]:
                    optimal.append(instrument)
            elif phase == TradingPhase.REGULAR_HOURS:
                # Regular hours - barcha instruments
                optimal.append(instrument)
            elif phase == TradingPhase.PRE_MARKET:
                # Pre-market - faqat electronic instruments
                if metal_type == MetalType.INDUSTRIAL:
                    optimal.append(instrument)
        
        return optimal[:5]  # Top 5 instruments
    
    def _get_next_market_events(self, current_time: datetime, market_enum: MetalMarket) -> List[Dict[str, any]]:
        """Keyingi bozor voqealarini olish"""
        
        events = []
        current_utc = current_time.astimezone(pytz.UTC)
        current_day = current_utc.weekday()
        
        # Inventory reports
        if market_enum in [MetalMarket.LME, MetalMarket.COMEX]:
            reports = self.inventory_reports.get(market_enum.value, {})
            
            for report_type, report_data in reports.items():
                if "time" in report_data:
                    event_time = report_data["time"]
                    event_datetime = self._get_next_occurrence(current_utc, event_time)
                    
                    events.append({
                        "type": "inventory_report",
                        "report_type": report_type,
                        "time": event_datetime,
                        "impact": "high"
                    })
        
        return events[:3]  # Next 3 events
    
    def _get_next_occurrence(self, current_time: datetime, target_time: time) -> datetime:
        """Keyingi occurrence vaqti"""
        
        event_datetime = current_time.replace(
            hour=target_time.hour,
            minute=target_time.minute,
            second=0,
            microsecond=0
        )
        
        # Days specification
        if "day" in target_time.strftime("%A").lower():
            # Specific day of week
            pass  # Implementation for specific days
        
        if event_datetime <= current_time:
            event_datetime += timedelta(days=1)
        
        return event_datetime
    
    def get_metal_inventory_impact(self, metal_name: str, current_time: datetime) -> Dict[str, any]:
        """Metal uchun inventory impact tahlili"""
        
        if metal_name not in self.metal_classifications:
            return {}
        
        classification = self.metal_classifications[metal_name]
        primary_market = classification["primary_market"]
        
        # Current inventory cycle position
        current_utc = current_time.astimezone(pytz.UTC)
        current_day = current_utc.weekday()
        current_hour = current_utc.hour
        
        impact_analysis = {
            "metal": metal_name,
            "primary_market": primary_market.value,
            "current_cycle": "normal",
            "next_release": None,
            "impact_level": "medium",
            "seasonal_factor": 1.0
        }
        
        # Seasonal patterns
        if metal_name in self.seasonal_patterns:
            patterns = self.seasonal_patterns[metal_name]
            current_month = current_utc.month
            
            if current_month in patterns.get("high_demand_months", []):
                impact_analysis["seasonal_factor"] = 1.3
                impact_analysis["demand_cycle"] = "high_demand"
            elif current_month in patterns.get("low_demand_months", []):
                impact_analysis["seasonal_factor"] = 0.8
                impact_analysis["demand_cycle"] = "low_demand"
            
            if current_month in patterns.get("volatility_peaks", []):
                impact_analysis["volatility_outlook"] = "elevated"
        
        # Next inventory release
        next_release = self._get_next_inventory_release(current_time, primary_market, metal_name)
        if next_release:
            impact_analysis["next_release"] = next_release["time"]
            impact_analysis["time_to_release"] = next_release["time_to_release"]
            impact_analysis["impact_level"] = next_release["impact_level"]
        
        return impact_analysis
    
    def _get_next_inventory_release(self, current_time: datetime, market: MetalMarket, metal: str) -> Optional[Dict]:
        """Keyingi inventory release ma'lumoti"""
        
        current_utc = current_time.astimezone(pytz.UTC)
        
        # LME daily stocks
        if market == MetalMarket.LME:
            tomorrow_stocks = current_utc + timedelta(days=1)
            if tomorrow_stocks.weekday() < 5:  # Weekday
                release_time = tomorrow_stocks.replace(hour=8, minute=0, second=0, microsecond=0)
                time_to_release = release_time - current_utc
                
                return {
                    "type": "LME_Daily_Stocks",
                    "time": release_time,
                    "time_to_release": f"{int(time_to_release.total_seconds() // 3600)} hours",
                    "impact_level": "medium",
                    "metals_affected": ["copper", "aluminum", "lead", "zinc", "nickel"]
                }
        
        # COMEX inventories
        elif market == MetalMarket.COMEX and metal in ["gold", "silver"]:
            # Next Tuesday or Thursday
            days_ahead = 1 - current_utc.weekday()  # Days until next Tuesday
            if days_ahead <= 0:
                days_ahead += 7
            
            if current_utc.weekday() in [2, 4]:  # Tuesday or Thursday
                days_ahead = 0 if current_utc.hour < 21 else 7  # Same day if before 21:00 GMT
            
            if current_utc.weekday() == 0:  # Monday
                days_ahead = 1  # Tuesday
            elif current_utc.weekday() == 1:  # Tuesday
                days_ahead = 2  # Next Thursday
            elif current_utc.weekday() == 3:  # Thursday
                days_ahead = 4  # Next Tuesday
            
            release_date = current_utc + timedelta(days=days_ahead)
            release_time = release_date.replace(hour=21, minute=0, second=0, microsecond=0)
            time_to_release = release_time - current_utc
            
            return {
                "type": "COMEX_Inventories",
                "time": release_time,
                "time_to_release": f"{int(time_to_release.total_seconds() // 3600)} hours",
                "impact_level": "medium",
                "metals_affected": [metal]
            }
        
        return None
    
    def optimize_metal_trading_timing(self, metal_name: str, strategy_type: str, current_time: datetime) -> Dict[str, any]:
        """Metal trading uchun optimal vaqt tanlash"""
        
        if metal_name not in self.metal_classifications:
            return {"error": f"Metal {metal_name} not supported"}
        
        classification = self.metal_classifications[metal_name]
        metal_type = classification["type"]
        primary_market = classification["primary_market"]
        
        # Current market analysis
        market_analysis = self._analyze_individual_market(current_time, primary_market, self.markets[primary_market])
        
        recommendations = []
        
        if strategy_type.lower() == "scalping":
            # Scalping uchun - yuqori volatil va electronic trading
            if market_analysis and market_analysis.is_open:
                if market_analysis.current_phase == TradingPhase.REGULAR_HOURS:
                    if "electronic" in market_analysis.active_sessions:
                        recommendations.append({
                            "action": "OPTIMAL_SCALPING",
                            "reason": "Electronic trading with good liquidity",
                            "market": primary_market.value,
                            "session": market_analysis.active_sessions
                        })
                elif "ring_trading" in market_analysis.active_sessions:
                    recommendations.append({
                        "action": "GOOD_SCALPING",
                        "reason": "Ring trading with price discovery",
                        "volatility_boost": "high"
                    })
        
        elif strategy_type.lower() == "swing":
            # Swing trading - inventory cycles va seasonal patterns
            inventory_impact = self._calculate_inventory_impact(current_time, primary_market)
            
            if inventory_impact > 0.5:
                recommendations.append({
                    "action": "INVENTORY_DRIVEN",
                    "reason": "High inventory impact period",
                    "impact_level": f"{inventory_impact:.1f}",
                    "metal": metal_name
                })
            
            # Seasonal factor
            seasonal_factor = self._get_seasonal_factor(current_time, metal_name)
            if seasonal_factor > 1.2:
                recommendations.append({
                    "action": "SEASONAL_OPPORTUNITY",
                    "reason": f"High demand season, factor: {seasonal_factor:.1f}",
                    "outlook": "positive"
                })
        
        elif strategy_type.lower() == "momentum":
            # Momentum trading - ring trading sessions
            if market_analysis and "ring_trading" in market_analysis.active_sessions:
                if market_analysis.volatility_trend == "very_high_volatility":
                    recommendations.append({
                        "action": "MOMENTUM_SETUP",
                        "reason": "Ring trading with very high volatility",
                        "optimal_for": "trend_following"
                    })
        
        return {
            "metal": metal_name,
            "strategy_type": strategy_type,
            "current_market_status": market_analysis.market_name if market_analysis else "closed",
            "recommendations": recommendations,
            "timing_factors": {
                "market_phase": market_analysis.current_phase.value if market_analysis else "closed",
                "inventory_cycle": self._get_inventory_cycle_position(current_time, metal_name),
                "seasonal_outlook": self._get_seasonal_factor(current_time, metal_name)
            }
        }
    
    def _get_seasonal_factor(self, current_time: datetime, metal: str) -> float:
        """Seasonal factor hisoblash"""
        
        if metal not in self.seasonal_patterns:
            return 1.0
        
        current_month = current_time.month
        patterns = self.seasonal_patterns[metal]
        
        if current_month in patterns.get("high_demand_months", []):
            return 1.3
        elif current_month in patterns.get("low_demand_months", []):
            return 0.8
        else:
            return 1.0
    
    def _get_inventory_cycle_position(self, current_time: datetime, metal: str) -> str:
        """Inventory cycle position"""
        
        # Simplified inventory cycle
        current_day = current_time.weekday()
        
        if current_day == 4:  # Friday
            return "pre_report"  # Before inventory reports
        elif current_day == 0:  # Monday
            return "post_report"  # After inventory reports
        else:
            return "normal_cycle"