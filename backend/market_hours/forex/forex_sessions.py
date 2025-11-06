"""
Forex Sessions Analyzer
Forex sessiyalari tahlili va optimizatsiyasi
"""

import pytz
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from config.market_config import FOREX_SESSIONS, SESSION_OVERLAPS, TIMEZONES, SessionType

class SessionPhase(Enum):
    OPENING = "opening"
    ACTIVE = "active"
    TRANSITION = "transition"
    CLOSING = "closing"
    BREAK = "break"

class VolatilityLevel(Enum):
    VERY_LOW = 0.5
    LOW = 0.8
    NORMAL = 1.0
    HIGH = 1.5
    VERY_HIGH = 2.0

@dataclass
class SessionAnalysis:
    """Sessiya tahlil ma'lumotlari"""
    session_type: str
    name: str
    is_active: bool
    current_phase: SessionPhase
    volatility_level: VolatilityLevel
    trading_intensity: float  # 0-1
    best_currency_pairs: List[str]
    time_remaining: timedelta
    characteristics: Dict[str, str]

class ForexSessionAnalyzer:
    """Forex sessiyalarini tahlil qiluvchi klass"""
    
    def __init__(self):
        self.sessions = FOREX_SESSIONS
        self.overlaps = SESSION_OVERLAPS
        
        # Session characteristics database
        self.session_characteristics = {
            "asian": {
                "volatility_pattern": "range_bound",
                "best_pairs": ["USD/JPY", "AUD/USD", "NZD/USD"],
                "news_impact": "low",
                "spread_behavior": "tight",
                "liquidity_pattern": "gradual_build"
            },
            "european": {
                "volatility_pattern": "trending",
                "best_pairs": ["EUR/USD", "GBP/USD", "EUR/GBP"],
                "news_impact": "high",
                "spread_behavior": "variable",
                "liquidity_pattern": "peak"
            },
            "american": {
                "volatility_pattern": "directional",
                "best_pairs": ["USD/CAD", "GBP/USD", "EUR/USD"],
                "news_impact": "very_high",
                "spread_behavior": "widening_on_news",
                "liquidity_pattern": "sustained"
            }
        }
    
    def analyze_current_session(self, current_time: datetime) -> Optional[SessionAnalysis]:
        """Joriy sessiyani tahlil qilish"""
        
        current_session = self._get_current_session(current_time)
        if not current_session:
            return None
            
        session_type = current_session["session"]
        session_data = self.sessions[SessionType(session_type)]
        
        # Session fazasini aniqlash
        current_phase = self._determine_session_phase(current_time, session_data)
        
        # Volatil darajani hisoblash
        volatility = self._calculate_session_volatility(current_time, session_data)
        
        # Trading intensivligi
        trading_intensity = self._calculate_trading_intensity(current_time, session_data)
        
        # Eng yaxshi currency pairlarni tanlash
        best_pairs = self._get_best_currency_pairs(session_type, current_phase)
        
        # Sessiyagacha qolgan vaqt
        time_remaining = self._calculate_time_remaining(current_time, session_data)
        
        # Xususiyatlarni yaratish
        characteristics = self._get_session_characteristics(session_type)
        characteristics.update({
            "current_phase": current_phase.value,
            "volatility_level": volatility.value,
            "trading_intensity": f"{trading_intensity:.1%}"
        })
        
        return SessionAnalysis(
            session_type=session_type,
            name=session_data["name"],
            is_active=True,
            current_phase=current_phase,
            volatility_level=volatility,
            trading_intensity=trading_intensity,
            best_currency_pairs=best_pairs,
            time_remaining=time_remaining,
            characteristics=characteristics
        )
    
    def _get_current_session(self, current_time: datetime) -> Optional[Dict[str, str]]:
        """Joriy sessiyani aniqlash"""
        current_time_utc = current_time.astimezone(pytz.UTC).time()
        
        for session_enum in SessionType:
            session_data = self.sessions[session_enum]
            start_time = session_data["start_time"]
            end_time = session_data["end_time"]
            
            if self._is_time_in_range(current_time_utc, start_time, end_time):
                return {
                    "session": session_enum.value,
                    "start_time": start_time,
                    "end_time": end_time,
                    "data": session_data
                }
        
        return None
    
    def _is_time_in_range(self, current_time: time, start_time: time, end_time: time) -> bool:
        """Vaqt interval ichida ekanligini tekshirish"""
        if start_time <= end_time:
            return start_time <= current_time < end_time
        else:
            # O'zaro kechgan vaqt (24 soatlik siklda)
            return current_time >= start_time or current_time < end_time
    
    def _determine_session_phase(self, current_time: datetime, session_data: Dict) -> SessionPhase:
        """Session fazasini aniqlash"""
        current_time_utc = current_time.astimezone(pytz.UTC).time()
        start_time = session_data["start_time"]
        end_time = session_data["end_time"]
        
        # Session davomiyligini hisoblash
        if start_time <= end_time:
            session_duration = (datetime.combine(datetime.today(), end_time) - 
                              datetime.combine(datetime.today(), start_time))
        else:
            session_duration = timedelta(hours=24 - start_time.hour + end_time.hour)
        
        # Joriy vaqtni foizlarda hisoblash
        if start_time <= end_time:
            elapsed = (datetime.combine(datetime.today(), current_time_utc) -
                      datetime.combine(datetime.today(), start_time))
        else:
            if current_time_utc >= start_time:
                elapsed = (datetime.combine(datetime.today(), current_time_utc) -
                          datetime.combine(datetime.today(), start_time))
            else:
                elapsed = (datetime.combine(datetime.today(), time(23, 59)) -
                          datetime.combine(datetime.today(), start_time) +
                          datetime.combine(datetime.today(), current_time_utc))
        
        elapsed_percentage = elapsed.total_seconds() / session_duration.total_seconds()
        
        # Fazani aniqlash
        if elapsed_percentage < 0.1:  # Birinchi 10%
            return SessionPhase.OPENING
        elif elapsed_percentage < 0.8:  # 10% - 80%
            return SessionPhase.ACTIVE
        elif elapsed_percentage < 0.95:  # 80% - 95%
            return SessionPhase.CLOSING
        else:  # Oxirgi 5%
            return SessionPhase.TRANSITION
    
    def _calculate_session_volatility(self, current_time: datetime, session_data: Dict) -> VolatilityLevel:
        """Session volatil darajasini hisoblash"""
        
        # Base volatility by session type
        base_volatility = session_data["volatility_multiplier"]
        
        # Time-based adjustments
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_minutes = current_hour * 60 + current_minute
        
        # Session start (highest volatility)
        start_minutes = session_data["start_time"].hour * 60 + session_data["start_time"].minute
        
        if abs(current_minutes - start_minutes) <= 60:  # Birinchi soat
            volatility_multiplier = 1.3
        elif start_minutes + 180 <= current_minutes <= start_minutes + 240:  # 3-4 soat
            volatility_multiplier = 1.1
        else:
            volatility_multiplier = 0.9
        
        # Overlap periods have higher volatility
        current_overlap = self._get_current_overlap(current_time)
        if current_overlap:
            volatility_multiplier *= 1.4
        
        final_volatility = base_volatility * volatility_multiplier
        
        # Volatility level kategoriyasini aniqlash
        if final_volatility >= 2.5:
            return VolatilityLevel.VERY_HIGH
        elif final_volatility >= 2.0:
            return VolatilityLevel.HIGH
        elif final_volatility >= 1.2:
            return VolatilityLevel.NORMAL
        elif final_volatility >= 0.8:
            return VolatilityLevel.LOW
        else:
            return VolatilityLevel.VERY_LOW
    
    def _calculate_trading_intensity(self, current_time: datetime, session_data: Dict) -> float:
        """Trading intensivligini hisoblash (0-1)"""
        
        current_hour = current_time.hour
        
        # Session boshida va oxirida yuqori aktivlik
        session_start = session_data["start_time"].hour
        session_end = session_data["end_time"].hour
        
        # Birinchi 30 daqiqa va oxirgi 30 daqiqa
        first_hour = session_start
        last_hour = session_end - 1 if session_end > 0 else 23
        
        if current_hour == first_hour or current_hour == last_hour:
            return 0.9
        elif first_hour < current_hour < last_hour:
            return 0.7
        else:
            return 0.3
    
    def _get_best_currency_pairs(self, session_type: str, phase: SessionPhase) -> List[str]:
        """Sessiya uchun eng yaxshi currency pairlarni tanlash"""
        
        base_pairs = self.session_characteristics[session_type]["best_pairs"]
        
        # Fazaga qarab pairlarni filtrlash
        if phase == SessionPhase.OPENING:
            # Session ochilishida - news sensitive pairs
            return [pair for pair in base_pairs if "USD" in pair or "EUR" in pair]
        elif phase == SessionPhase.ACTIVE:
            # Faol davr - barcha pairlar
            return base_pairs
        elif phase == SessionPhase.CLOSING:
            # Session yopilishi - major pairs only
            return [pair for pair in base_pairs if pair in ["EUR/USD", "GBP/USD", "USD/JPY"]]
        else:
            # Transition - stable pairs
            return ["EUR/USD", "GBP/USD"]
    
    def _calculate_time_remaining(self, current_time: datetime, session_data: Dict) -> timedelta:
        """Session tugashigacha qolgan vaqt"""
        
        current_time_utc = current_time.astimezone(pytz.UTC)
        end_time = session_data["end_time"]
        
        end_datetime = current_time_utc.replace(
            hour=end_time.hour, 
            minute=end_time.minute, 
            second=0, 
            microsecond=0
        )
        
        # Agar end time bugungi vaqtdan oldin bo'lsa, ertasiga qo'yish
        if end_datetime <= current_time_utc:
            end_datetime += timedelta(days=1)
        
        return end_datetime - current_time_utc
    
    def _get_session_characteristics(self, session_type: str) -> Dict[str, str]:
        """Session xususiyatlarini olish"""
        return self.session_characteristics.get(session_type, {})
    
    def _get_current_overlap(self, current_time: datetime) -> Optional[str]:
        """Joriy overlap sessiyasini aniqlash"""
        
        current_time_utc = current_time.astimezone(pytz.UTC).time()
        
        for overlap_name, overlap_data in self.overlaps.items():
            start_time = overlap_data["start_time"]
            end_time = overlap_data["end_time"]
            
            if start_time <= current_time_utc < end_time:
                return overlap_name
                
        return None
    
    def get_session_overlap_analysis(self, current_time: datetime) -> List[Dict[str, any]]:
        """Overlap sessiyalari tahlili"""
        
        current_overlap = self._get_current_overlap(current_time)
        analysis_results = []
        
        for overlap_name, overlap_data in self.overlaps.items():
            
            # Overlap aktiv yoki yo'qligini tekshirish
            start_time = overlap_data["start_time"]
            end_time = overlap_data["end_time"]
            
            is_active = self._is_time_in_range(current_time.astimezone(pytz.UTC).time(), start_time, end_time)
            
            # Session sessiyalari
            sessions = overlap_name.split("_")
            
            analysis = {
                "name": overlap_name,
                "display_name": f"{sessions[0].title()} - {sessions[1].title()} Overlap",
                "is_active": is_active,
                "start_time": start_time.strftime("%H:%M GMT"),
                "end_time": end_time.strftime("%H:%M GMT"),
                "characteristics": overlap_data["characteristics"],
                "volatility_multiplier": overlap_data["volatility_multiplier"],
                "sessions_involved": sessions,
                "optimal_for": "scalping, momentum_trading"
            }
            
            analysis_results.append(analysis)
        
        return analysis_results
    
    def optimize_trading_strategy(self, strategy_type: str, current_time: datetime) -> Dict[str, any]:
        """Strategiya uchun optimal sessiyani aniqlash"""
        
        current_session = self.analyze_current_session(current_time)
        overlap_analysis = self.get_session_overlap_analysis(current_time)
        
        recommendations = []
        
        if strategy_type.lower() == "scalping":
            # Scalping uchun - yuqori volatil va likvidlik
            if current_session:
                if current_session.volatility_level in [VolatilityLevel.HIGH, VolatilityLevel.VERY_HIGH]:
                    recommendations.append({
                        "action": "EXCELLENT_SCALPING_CONDITIONS",
                        "reason": f"High volatility {current_session.current_phase.value} phase",
                        "session": current_session.name,
                        "best_pairs": current_session.best_currency_pairs[:2]
                    })
            
            # Overlap vaqtlari
            for overlap in overlap_analysis:
                if overlap["is_active"]:
                    recommendations.append({
                        "action": "OVERLAP_SCALPING",
                        "reason": overlap["characteristics"],
                        "volatility_boost": f"{overlap['volatility_multiplier']:.1f}x"
                    })
        
        elif strategy_type.lower() == "swing":
            # Swing trading - barqaror trendlar
            if current_session:
                if current_session.current_phase == SessionPhase.ACTIVE:
                    recommendations.append({
                        "action": "SWING_TRADING_OPPORTUNITY",
                        "reason": "Active trading phase with steady trends",
                        "session": current_session.name,
                        "time_remaining_hours": current_session.time_remaining.total_seconds() / 3600
                    })
        
        elif strategy_type.lower() == "breakout":
            # Breakout - session ochilishi
            if current_session and current_session.current_phase == SessionPhase.OPENING:
                recommendations.append({
                    "action": "BREAKOUT_SETUP",
                    "reason": "Session opening with increased volatility",
                    "session": current_session.name,
                    "duration_minutes": 60
                })
        
        # Agar tavsiyalar bo'lmasa
        if not recommendations:
            recommendations.append({
                "action": "WAIT_FOR_BETTER_CONDITIONS",
                "reason": "Current market conditions not optimal for this strategy"
            })
        
        return {
            "strategy_type": strategy_type,
            "current_time": current_time.isoformat(),
            "current_session": current_session.session_type if current_session else None,
            "recommendations": recommendations,
            "market_sentiment": self._get_market_sentiment(current_time)
        }
    
    def _get_market_sentiment(self, current_time: datetime) -> Dict[str, str]:
        """Bozor kayfiyatini aniqlash"""
        
        current_hour = current_time.hour
        
        if 0 <= current_hour < 9:  # Asian session
            return {
                "sentiment": "cautious",
                "description": "Asian session characterized by range-bound trading"
            }
        elif 8 <= current_hour < 17:  # European session
            return {
                "sentiment": "active",
                "description": "European session with high news impact"
            }
        elif 13 <= current_hour < 22:  # American session
            return {
                "sentiment": "volatility_focused",
                "description": "American session with high impact news events"
            }
        else:
            return {
                "sentiment": "quiet",
                "description": "Off-market hours with reduced activity"
            }
    
    def get_next_session_info(self, current_time: datetime) -> Dict[str, any]:
        """Keyingi sessiya haqida ma'lumot"""
        
        # Barcha sessiyalarni saralash
        all_sessions = []
        current_utc = current_time.astimezone(pytz.UTC)
        
        for session_enum in SessionType:
            # Skip overlaps since they're not standalone sessions
            if session_enum == SessionType.OVERLAP:
                continue
                
            session_data = self.sessions[session_enum]
            start_time = session_data["start_time"]
            
            # Keyingi occurrence hisoblash
            next_occurrence = self._get_next_occurrence(current_utc, start_time)
            all_sessions.append({
                "session": session_enum.value,
                "name": session_data["name"],
                "next_start": next_occurrence,
                "timezone": session_data["timezone"]
            })
        
        # Eng yaqin sessiyani topish
        if all_sessions:
            next_session = min(all_sessions, key=lambda x: x["next_start"])
            time_to_next = next_session["next_start"] - current_utc
            
            return {
                "next_session": next_session["name"],
                "session_code": next_session["session"],
                "starts_at": next_session["next_start"].isoformat(),
                "time_to_start": f"{int(time_to_next.total_seconds() // 3600)}h {int((time_to_next.total_seconds() % 3600) // 60)}m",
                "local_time": next_session["next_start"].astimezone(
                    pytz.timezone(next_session["timezone"])
                ).strftime("%Y-%m-%d %H:%M %Z")
            }
        
        return {}
    
    def _get_next_occurrence(self, current_time: datetime, target_time: time) -> datetime:
        """Berilgan vaqtning keyingi paydo bo'lish vaqtini hisoblash"""
        
        target_datetime = current_time.replace(
            hour=target_time.hour,
            minute=target_time.minute,
            second=0,
            microsecond=0
        )
        
        # Agar bugungi voqea o'tgan bo'lsa, ertasiga qo'yish
        if target_datetime <= current_time:
            target_datetime += timedelta(days=1)
        
        return target_datetime