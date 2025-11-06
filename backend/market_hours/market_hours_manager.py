"""
Market Hours Manager
Barcha bozor vaqtlari va sessiyalarni boshqaruvchi asosiy klass
"""

import pytz
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from config.market_config import (
    FOREX_SESSIONS, SESSION_OVERLAPS, METAL_MARKETS,
    CENTRAL_BANK_EVENTS, NEWS_IMPACT_LEVELS, VOLATILITY_PATTERNS,
    MarketType, SessionType, MetalMarket, TIMEZONES
)

@dataclass
class SessionInfo:
    """Sessiya haqida ma'lumot"""
    name: str
    start_time: time
    end_time: time
    timezone: str
    is_active: bool
    volatility_multiplier: float
    characteristics: str
    current_volatility: float = 1.0
    next_event_time: Optional[datetime] = None
    event_type: Optional[str] = None

@dataclass
class MarketStatus:
    """Bozor holati"""
    is_open: bool
    current_session: Optional[SessionType]
    next_session: Optional[SessionType]
    current_overlap: Optional[str]
    volatility_level: float
    next_event: Optional[Dict[str, Any]]
    time_to_next_event: Optional[timedelta]

class MarketHoursManager:
    """Bozor vaqtlari boshqaruvchi asosiy klass"""
    
    def __init__(self, reference_timezone: str = "GMT"):
        """
        Args:
            reference_timezone: Asosiy vaqt mintaqasi
        """
        self.reference_tz = pytz.timezone(reference_timezone)
        self.current_time: datetime = None
        self.session_cache: Dict[str, SessionInfo] = {}
        
        # Cache for performance
        self._cache_expiry = {}
        self._cache_duration = timedelta(seconds=60)  # 1 minute cache
        
    def get_current_market_status(self, current_time_utc: Optional[datetime] = None) -> MarketStatus:
        """Joriy bozor holatini aniqlash
        
        Args:
            current_time_utc: UTC vaqt (yo'q bo'lsa joriy vaqt)
            
        Returns:
            MarketStatus obyekt
        """
        if current_time_utc is None:
            current_time_utc = datetime.now(pytz.UTC)
            
        self.current_time = current_time_utc
        
        # Forex sessiyalari tekshirish
        current_session = self._get_current_forex_session()
        next_session = self._get_next_forex_session()
        current_overlap = self._get_current_overlap()
        
        # Volatil darajani hisoblash
        volatility_level = self._calculate_current_volatility()
        
        # Keyingi voqeani topish
        next_event = self._get_next_news_event()
        time_to_next_event = self._calculate_time_to_event(next_event)
        
        is_open = current_session is not None or len(self._get_active_metal_markets()) > 0
        
        return MarketStatus(
            is_open=is_open,
            current_session=current_session,
            next_session=next_session,
            current_overlap=current_overlap,
            volatility_level=volatility_level,
            next_event=next_event,
            time_to_next_event=time_to_next_event
        )
    
    def _get_current_forex_session(self) -> Optional[SessionType]:
        """Joriy forex sessiyasini aniqlash"""
        if not self.current_time:
            return None
            
        current_time = self.current_time.time()
        
        for session_type, session_data in FOREX_SESSIONS.items():
            start_time = session_data["start_time"]
            end_time = session_data["end_time"]
            
            # 24 soatlik davr ichida tekshirish
            if start_time <= end_time:
                # Oddiy holat (masalan, 08:00 - 17:00)
                if start_time <= current_time < end_time:
                    return session_type
            else:
                # O'zaro kechgan vaqt (masalan, 00:00 - 09:00)
                if current_time >= start_time or current_time < end_time:
                    return session_type
                    
        return None
    
    def _get_next_forex_session(self) -> Optional[SessionType]:
        """Keyingi forex sessiyasini aniqlash"""
        if not self.current_time:
            return None
            
        current_time = self.current_time.time()
        today = self.current_time.date()
        
        # Kelgusi sessiyalarni saralash
        upcoming_sessions = []
        
        for session_type, session_data in FOREX_SESSIONS.items():
            start_time = session_data["start_time"]
            
            # Agar sessiya bugun boshlangan bo'lsa
            if start_time > current_time:
                session_datetime = datetime.combine(today, start_time, tzinfo=pytz.UTC)
                upcoming_sessions.append((session_datetime, session_type))
        
        # Agar bugun sessiya qolmagan bo'lsa, ertasiga olish
        if not upcoming_sessions:
            tomorrow = today + timedelta(days=1)
            for session_type, session_data in FOREX_SESSIONS.items():
                start_time = session_data["start_time"]
                session_datetime = datetime.combine(tomorrow, start_time, tzinfo=pytz.UTC)
                upcoming_sessions.append((session_datetime, session_type))
        
        # Eng yaqin sessiyani qaytarish
        if upcoming_sessions:
            upcoming_sessions.sort(key=lambda x: x[0])
            return upcoming_sessions[0][1]
            
        return None
    
    def _get_current_overlap(self) -> Optional[str]:
        """Joriy overlap sessiyasini aniqlash"""
        if not self.current_time:
            return None
            
        current_time = self.current_time.time()
        
        for overlap_name, overlap_data in SESSION_OVERLAPS.items():
            start_time = overlap_data["start_time"]
            end_time = overlap_data["end_time"]
            
            if start_time <= current_time < end_time:
                return overlap_name
                
        return None
    
    def _get_active_metal_markets(self) -> List[MetalMarket]:
        """Faol metal bozorlarini aniqlash"""
        if not self.current_time:
            return []
            
        active_markets = []
        current_time = self.current_time.time()
        current_day = self.current_time.weekday()  # 0 = Monday
        
        for market_enum, market_data in METAL_MARKETS.items():
            if self._is_market_open(current_time, current_day, market_data):
                active_markets.append(market_enum)
                
        return active_markets
    
    def _is_market_open(self, current_time: time, current_day: int, market_data: Dict) -> bool:
        """Bozor ochiq yoki yopiqligini tekshirish"""
        # Dam olish kunlari tekshirish
        if not market_data.get("weekend_trading", False) and current_day >= 5:
            return False
        
        # Har bir trading session tekshirish
        for session_name, session_data in market_data["trading_hours"].items():
            start_time = session_data["start_time"]
            end_time = session_data["end_time"]
            
            if start_time <= current_time < end_time:
                # Lunch/break vaqtlari tekshirish
                if "lunch_break" in market_data:
                    lunch_start = market_data["lunch_break"]["start_time"]
                    lunch_end = market_data["lunch_break"]["end_time"]
                    if lunch_start <= current_time < lunch_end:
                        continue
                return True
                
        return False
    
    def _calculate_current_volatility(self) -> float:
        """Joriy volatil darajani hisoblash"""
        if not self.current_time:
            return 1.0
            
        current_time = self.current_time.time()
        base_volatility = 1.0
        
        # Forex volatil pattern
        current_minutes = current_time.hour * 60 + current_time.minute
        forex_patterns = VOLATILITY_PATTERNS["forex"]
        
        # Eng yaqin vaqt intervalini topish
        closest_range = min(forex_patterns.keys(), 
                           key=lambda x: self._time_range_distance(x, current_minutes))
        volatility_multiplier = forex_patterns[closest_range]
        
        # Session overlap qo'shish
        current_overlap = self._get_current_overlap()
        if current_overlap and current_overlap in SESSION_OVERLAPS:
            volatility_multiplier *= SESSION_OVERLAPS[current_overlap]["volatility_multiplier"] / 1.0
        
        # Joriy session qo'shish
        current_session = self._get_current_forex_session()
        if current_session:
            session_data = FOREX_SESSIONS[current_session]
            volatility_multiplier *= session_data["volatility_multiplier"] / 1.0
        
        # Metal bozorlarining ta'sirini qo'shish
        active_metals = self._get_active_metal_markets()
        if active_metals:
            volatility_multiplier *= 1.3  # 30% qo'shimcha volatil
        
        return round(volatility_multiplier, 2)
    
    def _time_to_minutes(self, time_str: str) -> int:
        """Vaqt stringini daqiqaga aylantirish"""
        hour, minute = map(int, time_str.split(":"))
        return hour * 60 + minute
    
    def _time_range_distance(self, time_range: str, current_minutes: int) -> int:
        """Vaqt intervalidan joriy vaqtgacha bo'lgan masofani hisoblash"""
        try:
            # Time range parse qilish (e.g., "00:00-02:00")
            start_str, end_str = time_range.split("-")
            start_minutes = self._time_to_minutes(start_str)
            end_minutes = self._time_to_minutes(end_str)
            
            # Agar interval 24 soat ichida bo'lsa
            if start_minutes <= end_minutes:
                # Oddiy interval
                if start_minutes <= current_minutes <= end_minutes:
                    return 0  # Joriy vaqt interval ichida
                else:
                    # Eng yaqin chekkaga masofa
                    return min(abs(current_minutes - start_minutes), 
                              abs(current_minutes - end_minutes))
            else:
                # 24 soatli interval (e.g., "22:00-02:00")
                if current_minutes >= start_minutes or current_minutes <= end_minutes:
                    return 0  # Joriy vaqt interval ichida
                else:
                    # Interval ichida emas, eng yaqin chekkaga masofa
                    dist_to_start = abs(current_minutes - start_minutes)
                    dist_to_end = abs(current_minutes - end_minutes)
                    return min(dist_to_start, dist_to_end)
        except (ValueError, IndexError):
            # Agar parse qila olmasam, default distance
            return 999
    
    def _get_next_news_event(self) -> Optional[Dict[str, Any]]:
        """Keyingi yangilik voqeasini aniqlash"""
        if not self.current_time:
            return None
            
        next_events = []
        
        # Central bank voqealarini tekshirish
        for bank_code, bank_data in CENTRAL_BANK_EVENTS.items():
            decision_time = bank_data["decision_time"]
            event_datetime = self._get_next_occurrence(decision_time)
            
            if event_datetime > self.current_time:
                next_events.append({
                    "type": "central_bank",
                    "bank": bank_code,
                    "name": bank_data["name"],
                    "time": event_datetime,
                    "impact_level": "HIGH"
                })
        
        # Keyingi voqeani qaytarish
        if next_events:
            next_events.sort(key=lambda x: x["time"])
            return next_events[0]
            
        return None
    
    def _get_next_occurrence(self, target_time: time) -> datetime:
        """Berilgan vaqtning keyingi paydo bo'lish vaqtini hisoblash"""
        if not self.current_time:
            return datetime.now(pytz.UTC)
            
        today = self.current_time.date()
        target_datetime = datetime.combine(today, target_time, tzinfo=pytz.UTC)
        
        # Agar bugungi voqea o'tgan bo'lsa, ertasiga qo'yish
        if target_datetime <= self.current_time:
            target_datetime += timedelta(days=1)
            
        return target_datetime
    
    def _calculate_time_to_event(self, next_event: Optional[Dict]) -> Optional[timedelta]:
        """Voqeagacha bo'lgan vaqtni hisoblash"""
        if not next_event or not self.current_time:
            return None
            
        event_time = next_event["time"]
        return event_time - self.current_time
    
    def get_session_info(self, session_type: SessionType) -> Optional[SessionInfo]:
        """Sessiya haqida batafsil ma'lumot olish"""
        if session_type not in FOREX_SESSIONS:
            return None
            
        session_data = FOREX_SESSIONS[session_type]
        is_active = self._get_current_forex_session() == session_type
        
        return SessionInfo(
            name=session_data["name"],
            start_time=session_data["start_time"],
            end_time=session_data["end_time"],
            timezone=session_data["timezone"],
            is_active=is_active,
            volatility_multiplier=session_data["volatility_multiplier"],
            characteristics=session_data["characteristics"],
            current_volatility=self._calculate_current_volatility()
        )
    
    def get_market_hours_summary(self) -> Dict[str, Any]:
        """Barcha bozor soatlarining umumiy ko'rinishi"""
        status = self.get_current_market_status()
        
        # Faol sessiyalar
        active_sessions = []
        if status.current_session:
            active_sessions.append(status.current_session.value)
        if status.current_overlap:
            active_sessions.append(f"overlap_{status.current_overlap}")
            
        # Metal bozorlari
        active_metals = [market.value for market in self._get_active_metal_markets()]
        
        # Kelgusi voqealar
        upcoming_events = []
        if status.next_event:
            upcoming_events.append({
                "type": status.next_event["type"],
                "time": status.next_event["time"].isoformat(),
                "impact": status.next_event.get("impact_level", "MEDIUM")
            })
        
        return {
            "current_time": self.current_time.isoformat() if self.current_time else None,
            "is_market_open": status.is_open,
            "active_sessions": active_sessions,
            "active_metal_markets": active_metals,
            "current_volatility": status.volatility_level,
            "upcoming_events": upcoming_events,
            "next_session": status.next_session.value if status.next_session else None,
            "time_to_next_event_hours": (
                status.time_to_next_event.total_seconds() / 3600 
                if status.time_to_next_event else None
            )
        }
    
    def optimize_trading_timing(self, strategy_type: str = "scalping") -> Dict[str, Any]:
        """Strategiya uchun optimal vaqtlarni aniqlash"""
        
        current_volatility = self._calculate_current_volatility()
        current_overlap = self._get_current_overlap()
        active_metals = self._get_active_metal_markets()
        
        recommendations = []
        
        # Scalping uchun eng yaxshi vaqtlar
        if strategy_type.lower() == "scalping":
            if current_overlap == "european_american":
                recommendations.append({
                    "action": "OPTIMAL_SCALPING",
                    "reason": "European-American overlap, highest volatility",
                    "volatility": current_volatility
                })
            elif current_volatility > 1.5:
                recommendations.append({
                    "action": "GOOD_SCALPING",
                    "reason": "High volatility session",
                    "volatility": current_volatility
                })
            else:
                recommendations.append({
                    "action": "AVOID_SCALPING",
                    "reason": "Low volatility period",
                    "volatility": current_volatility
                })
        
        # Swing trading uchun
        elif strategy_type.lower() == "swing":
            if len(active_metals) > 0:
                recommendations.append({
                    "action": "METALS_POSITION",
                    "reason": "Metal markets active, good for swing",
                    "markets": [m.value for m in active_metals]
                })
            
            if status := self.get_current_market_status():
                if status.time_to_next_event and status.time_to_next_event.total_seconds() > 4 * 3600:
                    recommendations.append({
                        "action": "STABLE_PERIOD",
                        "reason": "No major news in next 4 hours",
                        "time_to_event": "4+ hours"
                    })
        
        # News trading uchun
        elif strategy_type.lower() == "news":
            if next_event := self._get_next_news_event():
                time_to_event = self._calculate_time_to_event(next_event)
                if time_to_event and time_to_event.total_seconds() < 3600:  # 1 soatdan kam
                    recommendations.append({
                        "action": "PREPARE_NEWS",
                        "reason": "News event in less than 1 hour",
                        "event": next_event["name"],
                        "time_to_event": f"{int(time_to_event.total_seconds() / 60)} minutes"
                    })
        
        return {
            "strategy_type": strategy_type,
            "current_time": self.current_time.isoformat() if self.current_time else None,
            "current_volatility": current_volatility,
            "recommendations": recommendations,
            "optimal_times": self._get_optimal_times_by_strategy(strategy_type)
        }
    
    def _get_optimal_times_by_strategy(self, strategy_type: str) -> List[Dict[str, Any]]:
        """Strategiya uchun optimal vaqtlar ro'yxati"""
        optimal_times = []
        
        if strategy_type.lower() == "scalping":
            # Overlap vaqtlar - eng yuqori volatil
            for overlap_name, overlap_data in SESSION_OVERLAPS.items():
                optimal_times.append({
                    "time_range": f"{overlap_data['start_time'].strftime('%H:%M')}-{overlap_data['end_time'].strftime('%H:%M')} GMT",
                    "reason": overlap_data['characteristics'],
                    "volatility": overlap_data['volatility_multiplier']
                })
        
        elif strategy_type.lower() == "swing":
            # London va New York sessionlar - uzun muddatli harakatlar
            optimal_times.append({
                "time_range": "08:00-17:00 GMT",
                "reason": "European session - steady trends",
                "volatility": 1.8
            })
            optimal_times.append({
                "time_range": "13:00-22:00 GMT",
                "reason": "American session - fundamental moves",
                "volatility": 1.6
            })
        
        return optimal_times