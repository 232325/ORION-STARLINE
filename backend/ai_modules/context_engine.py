"""
Context Engine - AI Prompt Optimizer uchun kontekst tahlil qilish tizimi
Foydalanuvchi profili, bozor konteksti va trading muhitini tahlil qilish
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import numpy as np
import math
import re

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillLevel(Enum):
    """Treyder malaka darajasi"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class MarketRegime(Enum):
    """Bozor rejimi"""
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    TRENDING = "trending"
    RANGING = "ranging"
    UNKNOWN = "unknown"

class RiskProfile(Enum):
    """Xavf profili"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    VERY_AGGRESSIVE = "very_aggressive"

class CommunicationStyle(Enum):
    """Muloqot uslubi"""
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    SIMPLE = "simple"
    DETAILED = "detailed"

class LearningPreference(Enum):
    """O'rganish uslubi"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"

@dataclass
class UserProfile:
    """Foydalanuvchi profili"""
    user_id: str
    name: str
    email: str
    skill_level: SkillLevel
    experience_years: float
    risk_profile: RiskProfile
    communication_style: CommunicationStyle
    learning_preference: LearningPreference
    trading_style: str
    preferred_markets: List[str]
    investment_goals: List[str]
    time_horizon: str
    current_portfolio_value: float
    yearly_income: float
    age: int
    location: str
    language: str = "uzbek"
    timezone: str = "UTC+5"
    created_date: datetime = None
    last_active: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Profile ni dict ga o'tkazish"""
        return asdict(self)

@dataclass
class MarketContext:
    """Bozor konteksti"""
    timestamp: datetime
    market_regime: MarketRegime
    volatility_level: float
    trend_strength: float
    volume_level: str
    sentiment_score: float
    key_events: List[str]
    economic_indicators: Dict[str, float]
    central_bank_status: str
    geopolitical_risk: str
    liquidity_conditions: str
    correlation_levels: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Context ni dict ga o'tkazish"""
        return asdict(self)

@dataclass
class PortfolioStatus:
    """Portfolio holati"""
    total_value: float
    daily_pnl: float
    daily_pnl_percent: float
    positions: List[Dict[str, Any]]
    cash_position: float
    margin_used: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    sharpe_ratio: float
    last_rebalanced: datetime
    risk_metrics: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Portfolio status ni dict ga o'tkazish"""
        return asdict(self)

@dataclass
class TradingHistory:
    """Trading tarixi"""
    user_id: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl: float
    average_win: float
    average_loss: float
    best_trade: float
    worst_trade: float
    longest_win_streak: int
    longest_loss_streak: int
    total_fees: float
    trading_days: int
    strategies_used: List[str]
    markets_traded: List[str]
    preferred_timeframes: List[str]
    common_mistakes: List[str]
    success_patterns: List[str]
    last_updated: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Trading history ni dict ga o'tkazish"""
        return asdict(self)

class ContextAnalyzer:
    """Kontekst tahlil qilish tizimi"""
    
    def __init__(self):
        """Context Analyzer ni ishga tushirish"""
        self.user_profiles: Dict[str, UserProfile] = {}
        self.market_contexts: Dict[str, MarketContext] = {}
        self.portfolio_statuses: Dict[str, PortfolioStatus] = {}
        self.trading_histories: Dict[str, TradingHistory] = {}
        self.performance_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
        # Analytics data
        self.analysis_cache: Dict[str, Any] = {}
        self.trend_analysis: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        logger.info("Context Analyzer initialized successfully")
    
    def analyze_user_context(self, user_profile: UserProfile) -> Dict[str, Any]:
        """
        Foydalanuvchi kontekstini tahlil qilish
        
        Args:
            user_profile: Foydalanuvchi profili
            
        Returns:
            Dict[str, Any]: Kontekst tahlili natijasi
        """
        try:
            context = {
                'user_profile_summary': self._create_user_profile_summary(user_profile),
                'skill_assessment': self._assess_skill_level(user_profile),
                'risk_tolerance': self._analyze_risk_tolerance(user_profile),
                'learning_style': self._analyze_learning_preference(user_profile),
                'communication_preference': self._analyze_communication_style(user_profile),
                'market_preferences': self._analyze_market_preferences(user_profile),
                'behavioral_patterns': self._analyze_behavioral_patterns(user_profile),
                'optimization_recommendations': self._generate_optimization_recommendations(user_profile)
            }
            
            # Cache the analysis
            cache_key = f"user_context_{user_profile.user_id}"
            self.analysis_cache[cache_key] = context
            
            logger.info(f"User context analysis completed for user: {user_profile.user_id}")
            return context
            
        except Exception as e:
            logger.error(f"Error analyzing user context: {str(e)}")
            return self._create_default_user_context()
    
    def analyze_market_context(self, market_context: MarketContext) -> Dict[str, Any]:
        """
        Bozor kontekstini tahlil qilish
        
        Args:
            market_context: Bozor konteksti
            
        Returns:
            Dict[str, Any]: Bozor tahlili natijasi
        """
        try:
            context = {
                'market_regime_analysis': self._analyze_market_regime(market_context),
                'volatility_assessment': self._assess_volatility(market_context),
                'trend_analysis': self._analyze_trends(market_context),
                'sentiment_analysis': self._analyze_market_sentiment(market_context),
                'risk_factors': self._identify_risk_factors(market_context),
                'opportunities': self._identify_opportunities(market_context),
                'market_timing': self._assess_market_timing(market_context),
                'sector_analysis': self._analyze_sectors(market_context)
            }
            
            # Update trend analysis history
            self.trend_analysis['volatility'].append(market_context.volatility_level)
            self.trend_analysis['sentiment'].append(market_context.sentiment_score)
            
            logger.info("Market context analysis completed")
            return context
            
        except Exception as e:
            logger.error(f"Error analyzing market context: {str(e)}")
            return self._create_default_market_context()
    
    def _create_user_profile_summary(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Foydalanuvchi profili xulosasini yaratish"""
        return {
            'user_id': user_profile.user_id,
            'experience_level': user_profile.skill_level.value,
            'experience_years': user_profile.experience_years,
            'risk_tolerance': user_profile.risk_profile.value,
            'primary_markets': user_profile.preferred_markets[:3],  # Top 3
            'investment_horizon': user_profile.time_horizon,
            'communication_style': user_profile.communication_style.value,
            'learning_preference': user_profile.learning_preference.value
        }
    
    def _assess_skill_level(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Malaka darajasini baholash"""
        experience_score = min(1.0, user_profile.experience_years / 10.0)  # Normalize to 0-1
        
        # Skill indicators from portfolio
        portfolio_complexity = self._assess_portfolio_complexity(user_profile.user_id)
        
        # Knowledge depth from trading history
        knowledge_depth = self._assess_knowledge_depth(user_profile.user_id)
        
        # Overall skill score
        skill_score = (experience_score * 0.4 + portfolio_complexity * 0.3 + knowledge_depth * 0.3)
        
        # Determine skill level
        if skill_score < 0.3:
            assessed_level = SkillLevel.BEGINNER
        elif skill_score < 0.6:
            assessed_level = SkillLevel.INTERMEDIATE
        elif skill_score < 0.8:
            assessed_level = SkillLevel.ADVANCED
        else:
            assessed_level = SkillLevel.EXPERT
        
        return {
            'assessed_level': assessed_level.value,
            'skill_score': skill_score,
            'confidence': 0.8 if user_profile.experience_years > 2 else 0.6,
            'key_strengths': self._identify_user_strengths(user_profile),
            'development_areas': self._identify_development_areas(user_profile)
        }
    
    def _assess_portfolio_complexity(self, user_id: str) -> float:
        """Portfolio murakkabligini baholash"""
        if user_id not in self.portfolio_statuses:
            return 0.3  # Default for new users
        
        portfolio = self.portfolio_statuses[user_id]
        complexity_indicators = [
            len(portfolio.positions) / 20.0,  # Number of positions
            abs(portfolio.daily_pnl_percent) / 10.0,  # Volatility
            1.0 if portfolio.margin_used > 0 else 0.0,  # Margin usage
            min(1.0, portfolio.total_fees / 1000.0)  # Fee complexity
        ]
        
        return sum(complexity_indicators) / len(complexity_indicators)
    
    def _assess_knowledge_depth(self, user_id: str) -> float:
        """Bilim chuqurligini baholash"""
        if user_id not in self.trading_histories:
            return 0.2  # Default for new users
        
        history = self.trading_histories[user_id]
        
        # Knowledge depth indicators
        knowledge_indicators = [
            min(1.0, history.total_trades / 100.0),  # Experience
            1.0 if history.win_rate > 0.5 else 0.5,  # Success indicator
            len(history.strategies_used) / 5.0,  # Strategy diversity
            1.0 if len(history.markets_traded) > 3 else 0.5,  # Market diversity
            1.0 if history.profit_factor > 1.0 else 0.3  # Profitability
        ]
        
        return sum(knowledge_indicators) / len(knowledge_indicators)
    
    def _identify_user_strengths(self, user_profile: UserProfile) -> List[str]:
        """Foydalanuvchi kuchli tomonlarini aniqlash"""
        strengths = []
        
        if user_profile.experience_years > 5:
            strengths.append("Keng tajriba")
        
        if user_profile.skill_level in [SkillLevel.ADVANCED, SkillLevel.EXPERT]:
            strengths.append("Chuqur bilim")
        
        if user_profile.risk_profile in [RiskProfile.AGGRESSIVE, RiskProfile.VERY_AGGRESSIVE]:
            strengths.append("Yuqori risk tolerance")
        
        if len(user_profile.preferred_markets) > 2:
            strengths.append("Keng bozor tajribasi")
        
        if user_profile.communication_style == CommunicationStyle.TECHNICAL:
            strengths.append("Texnik ko'nikmalar")
        
        return strengths
    
    def _identify_development_areas(self, user_profile: UserProfile) -> List[str]:
        """Rivojlanish sohalarini aniqlash"""
        areas = []
        
        if user_profile.experience_years < 2:
            areas.append("Tajriba oshirish")
        
        if user_profile.skill_level == SkillLevel.BEGINNER:
            areas.append("Asosiy bilimlar")
        
        if user_profile.risk_profile == RiskProfile.CONSERVATIVE:
            areas.append("Risk management")
        
        if len(user_profile.preferred_markets) == 1:
            areas.append("Bozer diversifikatsiyasi")
        
        if user_profile.communication_style == CommunicationStyle.SIMPLE:
            areas.append("Texnik bilimlar")
        
        return areas
    
    def _analyze_risk_tolerance(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Risk tolerance ni tahlil qilish"""
        # Base risk tolerance from profile
        base_tolerance = {
            RiskProfile.CONSERVATIVE: 0.2,
            RiskProfile.MODERATE: 0.5,
            RiskProfile.AGGRESSIVE: 0.8,
            RiskProfile.VERY_AGGRESSIVE: 0.9
        }[user_profile.risk_profile]
        
        # Adjust based on experience
        experience_multiplier = 1.0 + (user_profile.experience_years / 10.0) * 0.2
        adjusted_tolerance = min(1.0, base_tolerance * experience_multiplier)
        
        # Portfolio-based adjustment
        portfolio_risk = self._calculate_portfolio_risk(user_profile.user_id)
        
        return {
            'base_tolerance': base_tolerance,
            'adjusted_tolerance': adjusted_tolerance,
            'portfolio_risk': portfolio_risk,
            'recommended_allocation': self._calculate_risk_allocation(adjusted_tolerance),
            'risk_management_style': self._determine_risk_style(user_profile)
        }
    
    def _calculate_portfolio_risk(self, user_id: str) -> float:
        """Portfolio risk hisoblash"""
        if user_id not in self.portfolio_statuses:
            return 0.3
        
        portfolio = self.portfolio_statuses[user_id]
        
        # Risk indicators
        volatility_risk = abs(portfolio.daily_pnl_percent) / 5.0  # Normalize volatility
        drawdown_risk = portfolio.max_drawdown / 20.0  # Normalize drawdown
        margin_risk = portfolio.margin_used / portfolio.total_value if portfolio.total_value > 0 else 0
        
        return (volatility_risk + drawdown_risk + margin_risk) / 3.0
    
    def _calculate_risk_allocation(self, risk_tolerance: float) -> Dict[str, float]:
        """Risk allocation hisoblash"""
        if risk_tolerance < 0.3:
            return {
                'stocks': 0.3,
                'bonds': 0.5,
                'cash': 0.2
            }
        elif risk_tolerance < 0.6:
            return {
                'stocks': 0.6,
                'bonds': 0.3,
                'cash': 0.1
            }
        else:
            return {
                'stocks': 0.8,
                'bonds': 0.1,
                'cash': 0.1
            }
    
    def _determine_risk_style(self, user_profile: UserProfile) -> str:
        """Risk style ni aniqlash"""
        if user_profile.skill_level in [SkillLevel.ADVANCED, SkillLevel.EXPERT] and user_profile.experience_years > 5:
            return "Professional"
        elif user_profile.risk_profile in [RiskProfile.AGGRESSIVE, RiskProfile.VERY_AGGRESSIVE]:
            return "Aggressive"
        elif user_profile.risk_profile == RiskProfile.MODERATE:
            return "Balanced"
        else:
            return "Conservative"
    
    def _analyze_learning_preference(self, user_profile: UserProfile) -> Dict[str, Any]:
        """O'rganish uslubini tahlil qilish"""
        preference = user_profile.learning_preference
        
        learning_analysis = {
            LearningPreference.VISUAL: {
                'style': 'visual',
                'recommended_formats': ['charts', 'diagrams', 'infographics', 'videos'],
                'presentation_approach': 'Grafiklar va vizual elementlar bilan',
                'complexity_handling': 'Murakkab ma\'lumotlarni vizual formatda taqdim etish'
            },
            LearningPreference.AUDITORY: {
                'style': 'auditory',
                'recommended_formats': ['podcasts', 'webinars', 'discussions', 'presentations'],
                'presentation_approach': 'Tushuntirishlarni ovozli formatda',
                'complexity_handling': 'Audio tushuntirishlar va munozaralar'
            },
            LearningPreference.KINESTHETIC: {
                'style': 'kinesthetic',
                'recommended_formats': ['practical exercises', 'simulations', 'case studies', 'hands-on'],
                'presentation_approach': 'Amaliy mashqlar va real case study\'lar',
                'complexity_handling': 'Qadamlarni bajarish orqali o\'rganish'
            },
            LearningPreference.READING_WRITING: {
                'style': 'reading_writing',
                'recommended_formats': ['articles', 'reports', 'documentation', 'written exercises'],
                'presentation_approach': 'Matnli materiallar va yozma mashqlar',
                'complexity_handling': 'Batafsil yozma tushuntirishlar'
            }
        }
        
        base_analysis = learning_analysis.get(preference, learning_analysis[LearningPreference.VISUAL])
        
        # Adjust based on experience
        if user_profile.skill_level == SkillLevel.BEGINNER:
            base_analysis['complexity_level'] = 'simple'
            base_analysis['detail_level'] = 'basic'
        elif user_profile.skill_level == SkillLevel.EXPERT:
            base_analysis['complexity_level'] = 'advanced'
            base_analysis['detail_level'] = 'detailed'
        else:
            base_analysis['complexity_level'] = 'intermediate'
            base_analysis['detail_level'] = 'moderate'
        
        return base_analysis
    
    def _analyze_communication_style(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Muloqot uslubini tahlil qilish"""
        style = user_profile.communication_style
        
        style_analysis = {
            CommunicationStyle.FORMAL: {
                'tone': 'Rasmiy',
                'language_level': 'professional',
                'structure': 'Tizimli va tartibli',
                'detail_level': 'Batafsil',
                'presentation_approach': 'Rasmiy format va professional atamalar'
            },
            CommunicationStyle.CASUAL: {
                'tone': 'Rasmiy bo\'lmagan',
                'language_level': 'oddiy',
                'structure': 'Erkin',
                'detail_level': 'qisqacha',
                'presentation_approach': 'Suhbat uslubi va oddiy tilda'
            },
            CommunicationStyle.TECHNICAL: {
                'tone': 'Texnik',
                'language_level': 'specialized',
                'structure': 'Aniq va batafsil',
                'detail_level': 'chuqur',
                'presentation_approach': 'Texnik terminologiya va batafsil tahlil'
            },
            CommunicationStyle.SIMPLE: {
                'tone': 'Sodda',
                'language_level': 'basic',
                'structure': 'Qisqa va ravshan',
                'detail_level': 'minimal',
                'presentation_approach': 'Sodda tilda va tushunarli formatda'
            }
        }
        
        base_analysis = style_analysis.get(style, style_analysis[CommunicationStyle.FORMAL])
        
        # Adjust based on skill level
        if user_profile.skill_level == SkillLevel.BEGINNER:
            base_analysis['technical_level'] = 'basic'
            base_analysis['complexity_reduction'] = True
        else:
            base_analysis['technical_level'] = 'advanced'
            base_analysis['complexity_reduction'] = False
        
        return base_analysis
    
    def _analyze_market_preferences(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Bozor uslubini tahlil qilish"""
        markets = user_profile.preferred_markets
        trading_style = user_profile.trading_style.lower()
        
        # Analyze market preferences
        market_analysis = {
            'primary_markets': markets[:3] if len(markets) >= 3 else markets,
            'market_diversity': len(markets),
            'trading_style': trading_style,
            'expertise_areas': self._identify_market_expertise(markets, user_profile),
            'recommended_areas': self._recommend_market_areas(user_profile),
            'risk_profile_by_market': self._assess_market_risk_profile(markets)
        }
        
        return market_analysis
    
    def _identify_market_expertise(self, markets: List[str], user_profile: UserProfile) -> List[str]:
        """Bozor sohasidagi ekspertlikni aniqlash"""
        expertise = []
        
        if user_profile.experience_years > 3:
            if 'forex' in [m.lower() for m in markets]:
                expertise.append('forex')
            if 'stocks' in [m.lower() for m in markets]:
                expertise.append('equity')
            if 'crypto' in [m.lower() for m in markets]:
                expertise.append('cryptocurrency')
        
        return expertise
    
    def _recommend_market_areas(self, user_profile: UserProfile) -> List[str]:
        """Bozor sohalarini tavsiya qilish"""
        recommendations = []
        
        if user_profile.skill_level == SkillLevel.BEGINNER:
            if 'stocks' not in [m.lower() for m in user_profile.preferred_markets]:
                recommendations.append('stocks')
        elif user_profile.skill_level in [SkillLevel.ADVANCED, SkillLevel.EXPERT]:
            if 'derivatives' not in [m.lower() for m in user_profile.preferred_markets]:
                recommendations.append('derivatives')
        
        return recommendations
    
    def _assess_market_risk_profile(self, markets: List[str]) -> Dict[str, float]:
        """Bozor bo'yicha risk profilini baholash"""
        risk_profiles = {
            'forex': 0.6,
            'stocks': 0.7,
            'crypto': 0.9,
            'commodities': 0.8,
            'bonds': 0.3,
            'etf': 0.5
        }
        
        market_risks = {}
        for market in markets:
            for known_market, risk in risk_profiles.items():
                if known_market in market.lower():
                    market_risks[market] = risk
                    break
            else:
                market_risks[market] = 0.6  # Default risk
        
        return market_risks
    
    def _analyze_behavioral_patterns(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Xulq-atvor patternlarini tahlil qilish"""
        if user_profile.user_id not in self.trading_histories:
            return self._create_default_behavioral_patterns()
        
        history = self.trading_histories[user_profile.user_id]
        
        patterns = {
            'trading_frequency': self._analyze_trading_frequency(history),
            'risk_taking_behavior': self._analyze_risk_behavior(history),
            'performance_consistency': self._analyze_consistency(history),
            'learning_patterns': self._analyze_learning_patterns(user_profile, history),
            'decision_making_style': self._analyze_decision_making(history),
            'improvement_areas': self._identify_behavioral_improvements(history)
        }
        
        return patterns
    
    def _analyze_trading_frequency(self, history: TradingHistory) -> Dict[str, Any]:
        """Trading chastotasini tahlil qilish"""
        if history.trading_days == 0:
            return {'frequency': 'no_data', 'consistency': 0}
        
        trades_per_day = history.total_trades / history.trading_days
        
        if trades_per_day > 10:
            frequency = 'high_frequency'
        elif trades_per_day > 2:
            frequency = 'medium_frequency'
        elif trades_per_day > 0.2:
            frequency = 'low_frequency'
        else:
            frequency = 'very_low_frequency'
        
        return {
            'frequency': frequency,
            'trades_per_day': trades_per_day,
            'consistency': self._calculate_frequency_consistency(history)
        }
    
    def _calculate_frequency_consistency(self, history: TradingHistory) -> float:
        """Chastota barqarorligini hisoblash"""
        # Simplified calculation - in practice, would analyze daily trading patterns
        consistency_indicators = [
            1.0 if history.win_rate > 0.4 else 0.5,  # Consistent profitability
            1.0 if history.profit_factor > 1.0 else 0.5,  # Positive expectancy
            1.0 if abs(history.best_trade / history.worst_trade) < 5 else 0.5  # Risk control
        ]
        
        return sum(consistency_indicators) / len(consistency_indicators)
    
    def _analyze_risk_behavior(self, history: TradingHistory) -> Dict[str, Any]:
        """Risk qabul qilish xulq-atvorini tahlil qilish"""
        return {
            'risk_tolerance': 'high' if history.profit_factor > 1.5 else 'moderate' if history.profit_factor > 1.0 else 'low',
            'position_sizing': self._assess_position_sizing(history),
            'stop_loss_usage': self._assess_stop_loss_usage(history),
            'risk_reward_focus': 'good' if history.average_win > abs(history.average_loss) * 1.5 else 'poor'
        }
    
    def _assess_position_sizing(self, history: TradingHistory) -> str:
        """Pozitsiya hajmini baholash"""
        if history.worst_trade < -10.0:  # Large losses suggest poor position sizing
            return 'poor'
        elif history.worst_trade > -5.0:  # Controlled losses suggest good position sizing
            return 'good'
        else:
            return 'moderate'
    
    def _assess_stop_loss_usage(self, history: TradingHistory) -> str:
        """Stop loss foydalanishini baholash"""
        if history.longest_loss_streak > 5 and history.worst_trade < -15.0:
            return 'poor'
        elif history.longest_loss_streak < 3 and history.worst_trade > -8.0:
            return 'good'
        else:
            return 'moderate'
    
    def _analyze_consistency(self, history: TradingHistory) -> Dict[str, Any]:
        """Barqarorlikni tahlil qilish"""
        return {
            'consistency_score': self._calculate_consistency_score(history),
            'variance_analysis': self._analyze_variance(history),
            'trend_analysis': self._analyze_performance_trend(history)
        }
    
    def _calculate_consistency_score(self, history: TradingHistory) -> float:
        """Barqarorlik ballini hisoblash"""
        consistency_indicators = [
            min(1.0, history.win_rate),  # Win rate consistency
            min(1.0, history.profit_factor),  # Profit consistency
            1.0 if history.longest_loss_streak < 5 else 0.5,  # Loss control
            1.0 if abs(history.best_trade) < history.total_pnl * 3 else 0.5  # Risk balance
        ]
        
        return sum(consistency_indicators) / len(consistency_indicators)
    
    def _analyze_variance(self, history: TradingHistory) -> Dict[str, float]:
        """Variansni tahlil qilish"""
        return {
            'return_variance': abs(history.average_win - history.average_loss) if history.average_win and history.average_loss else 0,
            'streak_variance': abs(history.longest_win_streak - history.longest_loss_streak),
            'trade_size_variance': abs(history.best_trade - history.worst_trade) if history.best_trade and history.worst_trade else 0
        }
    
    def _analyze_performance_trend(self, history: TradingHistory) -> str:
        """Performance trendini tahlil qilish"""
        if history.profit_factor > 1.5 and history.win_rate > 0.6:
            return 'improving'
        elif history.profit_factor > 1.0 and history.win_rate > 0.4:
            return 'stable'
        else:
            return 'declining'
    
    def _analyze_learning_patterns(self, user_profile: UserProfile, history: TradingHistory) -> Dict[str, Any]:
        """O'rganish patternlarini tahlil qilish"""
        return {
            'adaptation_speed': self._assess_adaptation_speed(history),
            'knowledge_application': self._assess_knowledge_application(user_profile, history),
            'continuous_improvement': self._assess_improvement_trend(history),
            'strategy_evolution': self._analyze_strategy_evolution(history)
        }
    
    def _assess_adaptation_speed(self, history: TradingHistory) -> str:
        """Moslashish tezligini baholash"""
        if history.experience_years > 3 and history.win_rate > 0.5:
            return 'fast'
        elif history.experience_years > 1 and history.profit_factor > 1.0:
            return 'moderate'
        else:
            return 'slow'
    
    def _assess_knowledge_application(self, user_profile: UserProfile, history: TradingHistory) -> str:
        """Bilim qo'llashini baholash"""
        if user_profile.skill_level in [SkillLevel.ADVANCED, SkillLevel.EXPERT] and history.profit_factor > 1.2:
            return 'excellent'
        elif user_profile.skill_level == SkillLevel.INTERMEDIATE and history.profit_factor > 1.0:
            return 'good'
        else:
            return 'developing'
    
    def _assess_improvement_trend(self, history: TradingHistory) -> str:
        """Yaxshilash trendini baholash"""
        if history.profit_factor > 1.5:
            return 'strong_improvement'
        elif history.profit_factor > 1.0:
            return 'steady_improvement'
        else:
            return 'needs_attention'
    
    def _analyze_strategy_evolution(self, history: TradingHistory) -> Dict[str, Any]:
        """Strategy evolyutsiyasini tahlil qilish"""
        return {
            'diversity': len(history.strategies_used),
            'effectiveness': 'high' if history.profit_factor > 1.5 else 'moderate' if history.profit_factor > 1.0 else 'low',
            'adaptation': 'good' if len(history.strategies_used) > 2 else 'limited'
        }
    
    def _analyze_decision_making(self, history: TradingHistory) -> Dict[str, Any]:
        """Qaror qabul qilishni tahlil qilish"""
        return {
            'decision_quality': self._assess_decision_quality(history),
            'impulsiveness': self._assess_impulsiveness(history),
            'analysis_depth': self._assess_analysis_depth(history),
            'risk_consideration': self._assess_risk_consideration(history)
        }
    
    def _assess_decision_quality(self, history: TradingHistory) -> str:
        """Qaror sifatini baholash"""
        if history.win_rate > 0.6 and history.profit_factor > 1.5:
            return 'excellent'
        elif history.win_rate > 0.4 and history.profit_factor > 1.0:
            return 'good'
        else:
            return 'needs_improvement'
    
    def _assess_impulsiveness(self, history: TradingHistory) -> str:
        """Impulsiveness baholash"""
        if history.longest_loss_streak > 5:
            return 'high'
        elif history.longest_loss_streak > 2:
            return 'moderate'
        else:
            return 'low'
    
    def _assess_analysis_depth(self, history: TradingHistory) -> str:
        """Tahlil chuqurligini baholash"""
        if len(history.strategies_used) > 3 and history.win_rate > 0.5:
            return 'deep'
        elif len(history.strategies_used) > 1:
            return 'moderate'
        else:
            return 'shallow'
    
    def _assess_risk_consideration(self, history: TradingHistory) -> str:
        """Risk hisobga olishni baholash"""
        if history.worst_trade > -5.0:
            return 'excellent'
        elif history.worst_trade > -10.0:
            return 'good'
        else:
            return 'poor'
    
    def _identify_behavioral_improvements(self, history: TradingHistory) -> List[str]:
        """Xulq-atvor yaxshilanish sohalarini aniqlash"""
        improvements = []
        
        if history.win_rate < 0.4:
            improvements.append("Win rate yaxshilash")
        
        if history.longest_loss_streak > 5:
            improvements.append("Loss streak boshqarish")
        
        if history.profit_factor < 1.0:
            improvements.append("Risk-reward nisbatini yaxshilash")
        
        if history.worst_trade < -15.0:
            improvements.append("Position sizing")
        
        if len(history.strategies_used) == 1:
            improvements.append("Strategy diversifikatsiyasi")
        
        return improvements
    
    def _generate_optimization_recommendations(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Optimallashtirish tavsiyalarini yaratish"""
        recommendations = {
            'prompt_complexity': self._recommend_prompt_complexity(user_profile),
            'detail_level': self._recommend_detail_level(user_profile),
            'presentation_style': self._recommend_presentation_style(user_profile),
            'learning_approach': self._recommend_learning_approach(user_profile),
            'focus_areas': self._recommend_focus_areas(user_profile)
        }
        
        return recommendations
    
    def _recommend_prompt_complexity(self, user_profile: UserProfile) -> str:
        """Prompt murakkabligini tavsiya qilish"""
        if user_profile.skill_level == SkillLevel.BEGINNER:
            return 'simple'
        elif user_profile.skill_level == SkillLevel.EXPERT:
            return 'advanced'
        else:
            return 'intermediate'
    
    def _recommend_detail_level(self, user_profile: UserProfile) -> str:
        """Detail darajasini tavsiya qilish"""
        if user_profile.skill_level == SkillLevel.BEGINNER:
            return 'basic'
        elif user_profile.skill_level == SkillLevel.EXPERT:
            return 'detailed'
        else:
            return 'moderate'
    
    def _recommend_presentation_style(self, user_profile: UserProfile) -> str:
        """Presentation uslubini tavsiya qilish"""
        style_map = {
            CommunicationStyle.FORMAL: 'structured',
            CommunicationStyle.CASUAL: 'conversational',
            CommunicationStyle.TECHNICAL: 'analytical',
            CommunicationStyle.SIMPLE: 'simplified'
        }
        
        return style_map.get(user_profile.communication_style, 'structured')
    
    def _recommend_learning_approach(self, user_profile: UserProfile) -> str:
        """O'rganish yondashuvini tavsiya qilish"""
        preference_map = {
            LearningPreference.VISUAL: 'visual_learning',
            LearningPreference.AUDITORY: 'audio_learning',
            LearningPreference.KINESTHETIC: 'hands_on',
            LearningPreference.READING_WRITING: 'text_based'
        }
        
        return preference_map.get(user_profile.learning_preference, 'mixed')
    
    def _recommend_focus_areas(self, user_profile: UserProfile) -> List[str]:
        """E'tibor sohalarini tavsiya qilish"""
        focus_areas = []
        
        if user_profile.skill_level == SkillLevel.BEGINNER:
            focus_areas.extend(['Basics', 'Risk Management', 'Practice'])
        elif user_profile.skill_level == SkillLevel.EXPERT:
            focus_areas.extend(['Advanced Strategies', 'Market Microstructure', 'Professional Techniques'])
        
        if user_profile.risk_profile == RiskProfile.CONSERVATIVE:
            focus_areas.append('Conservative Strategies')
        elif user_profile.risk_profile == RiskProfile.AGGRESSIVE:
            focus_areas.append('Aggressive Strategies')
        
        return focus_areas
    
    # Market context analysis methods
    def _analyze_market_regime(self, market_context: MarketContext) -> Dict[str, Any]:
        """Bozor rejimini tahlil qilish"""
        return {
            'current_regime': market_context.market_regime.value,
            'regime_strength': self._calculate_regime_strength(market_context),
            'stability_score': self._calculate_regime_stability(market_context),
            'transition_probability': self._calculate_transition_probability(market_context),
            'recommended_strategies': self._get_regime_strategies(market_context.market_regime)
        }
    
    def _calculate_regime_strength(self, market_context: MarketContext) -> float:
        """Rehim kuchini hisoblash"""
        base_strength = {
            MarketRegime.BULL_MARKET: 0.8,
            MarketRegime.BEAR_MARKET: 0.7,
            MarketRegime.SIDEWAYS: 0.6,
            MarketRegime.HIGH_VOLATILITY: 0.9,
            MarketRegime.LOW_VOLATILITY: 0.4
        }.get(market_context.market_regime, 0.5)
        
        # Adjust by trend strength
        adjusted_strength = base_strength * (0.5 + market_context.trend_strength * 0.5)
        
        return min(1.0, adjusted_strength)
    
    def _calculate_regime_stability(self, market_context: MarketContext) -> float:
        """Regim barqarorligini hisoblash"""
        volatility_factor = 1.0 - market_context.volatility_level
        
        # Regime stability is inverse of volatility
        stability = volatility_factor * 0.8 + 0.2
        
        return min(1.0, max(0.0, stability))
    
    def _calculate_transition_probability(self, market_context: MarketContext) -> float:
        """Regim o'tish ehtimolini hisoblash"""
        # High volatility increases transition probability
        volatility_factor = market_context.volatility_level
        
        # Low stability increases transition probability
        stability = self._calculate_regime_stability(market_context)
        stability_factor = 1.0 - stability
        
        transition_prob = (volatility_factor * 0.6 + stability_factor * 0.4)
        
        return min(1.0, transition_prob)
    
    def _get_regime_strategies(self, regime: MarketRegime) -> List[str]:
        """Regim bo'yicha strategiyalarni olish"""
        strategy_map = {
            MarketRegime.BULL_MARKET: ['Momentum', 'Breakout', 'Growth'],
            MarketRegime.BEAR_MARKET: ['Defensive', 'Short', 'Safe Haven'],
            MarketRegime.SIDEWAYS: ['Range Trading', 'Mean Reversion'],
            MarketRegime.HIGH_VOLATILITY: ['Volatility Trading', 'Risk Management'],
            MarketRegime.LOW_VOLATILITY: ['Trend Following', 'Momentum']
        }
        
        return strategy_map.get(regime, ['Diversified'])
    
    def _assess_volatility(self, market_context: MarketContext) -> Dict[str, Any]:
        """Volatillikni baholash"""
        volatility_level = market_context.volatility_level
        
        if volatility_level > 0.8:
            level = 'extremely_high'
        elif volatility_level > 0.6:
            level = 'high'
        elif volatility_level > 0.4:
            level = 'moderate'
        elif volatility_level > 0.2:
            level = 'low'
        else:
            level = 'extremely_low'
        
        return {
            'volatility_level': level,
            'volatility_score': volatility_level,
            'trend': self._analyze_volatility_trend(),
            'market_impact': self._assess_volatility_impact(volatility_level)
        }
    
    def _analyze_volatility_trend(self) -> str:
        """Volatillik trendini tahlil qilish"""
        if len(self.trend_analysis['volatility']) < 2:
            return 'stable'
        
        recent_volatility = list(self.trend_analysis['volatility'])[-5:]
        if len(recent_volatility) < 3:
            return 'stable'
        
        # Simple trend analysis
        if recent_volatility[-1] > recent_volatility[-2] > recent_volatility[-3]:
            return 'increasing'
        elif recent_volatility[-1] < recent_volatility[-2] < recent_volatility[-3]:
            return 'decreasing'
        else:
            return 'stable'
    
    def _assess_volatility_impact(self, volatility_level: float) -> str:
        """Volatillik ta'sirini baholash"""
        if volatility_level > 0.8:
            return 'severe'
        elif volatility_level > 0.6:
            return 'high'
        elif volatility_level > 0.4:
            return 'moderate'
        elif volatility_level > 0.2:
            return 'low'
        else:
            return 'minimal'
    
    def _analyze_trends(self, market_context: MarketContext) -> Dict[str, Any]:
        """Trend tahlili"""
        return {
            'trend_strength': market_context.trend_strength,
            'trend_direction': 'bullish' if market_context.trend_strength > 0.6 else 'bearish' if market_context.trend_strength < 0.4 else 'sideways',
            'trend_consistency': self._calculate_trend_consistency(market_context),
            'momentum_indicators': self._analyze_momentum_indicators(market_context)
        }
    
    def _calculate_trend_consistency(self, market_context: MarketContext) -> float:
        """Trend barqarorligini hisoblash"""
        # Simplified calculation based on volatility
        consistency = 1.0 - market_context.volatility_level
        return max(0.0, consistency)
    
    def _analyze_momentum_indicators(self, market_context: MarketContext) -> Dict[str, float]:
        """Momentum indikatorlarini tahlil qilish"""
        return {
            'trend_momentum': market_context.trend_strength,
            'sentiment_momentum': market_context.sentiment_score,
            'volume_momentum': self._analyze_volume_momentum(market_context)
        }
    
    def _analyze_volume_momentum(self, market_context: MarketContext) -> float:
        """Volume momentum tahlili"""
        # Simplified volume analysis
        volume_factor = 1.0 if market_context.volume_level == 'high' else 0.5
        return volume_factor
    
    def _analyze_market_sentiment(self, market_context: MarketContext) -> Dict[str, Any]:
        """Bozor kayfiyatini tahlil qilish"""
        sentiment_score = market_context.sentiment_score
        
        if sentiment_score > 0.7:
            sentiment = 'extremely_positive'
        elif sentiment_score > 0.5:
            sentiment = 'positive'
        elif sentiment_score > 0.3:
            sentiment = 'neutral'
        elif sentiment_score > 0.1:
            sentiment = 'negative'
        else:
            sentiment = 'extremely_negative'
        
        return {
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'confidence': self._calculate_sentiment_confidence(market_context),
            'contrarian_signals': self._identify_contrarian_signals(sentiment_score)
        }
    
    def _calculate_sentiment_confidence(self, market_context: MarketContext) -> float:
        """Sentiment ishonchlilikni hisoblash"""
        # Confidence based on sentiment strength and market stability
        sentiment_strength = abs(market_context.sentiment_score - 0.5) * 2
        stability = self._calculate_regime_stability(market_context)
        
        confidence = (sentiment_strength + stability) / 2
        return confidence
    
    def _identify_contrarian_signals(self, sentiment_score: float) -> List[str]:
        """Kontra-indikator signallarni aniqlash"""
        signals = []
        
        if sentiment_score > 0.8:
            signals.append("Extreme optimism - potential reversal")
        elif sentiment_score < 0.2:
            signals.append("Extreme pessimism - potential bottom")
        
        return signals
    
    def _identify_risk_factors(self, market_context: MarketContext) -> List[str]:
        """Xavf omillarini aniqlash"""
        risk_factors = []
        
        if market_context.volatility_level > 0.7:
            risk_factors.append("High volatility")
        
        if market_context.geopolitical_risk == 'high':
            risk_factors.append("Geopolitical tensions")
        
        if market_context.central_bank_status == 'uncertain':
            risk_factors.append("Central bank uncertainty")
        
        if market_context.liquidity_conditions == 'tight':
            risk_factors.append("Tight liquidity")
        
        return risk_factors
    
    def _identify_opportunities(self, market_context: MarketContext) -> List[str]:
        """Imkoniyatlarni aniqlash"""
        opportunities = []
        
        if market_context.trend_strength > 0.7:
            opportunities.append("Strong trend opportunities")
        
        if market_context.volatility_level > 0.6 and market_context.volatility_level < 0.9:
            opportunities.append("Volatility trading")
        
        if market_context.sentiment_score < 0.3:
            opportunities.append("Contrarian opportunities")
        
        return opportunities
    
    def _assess_market_timing(self, market_context: MarketContext) -> Dict[str, Any]:
        """Bozor timing ni baholash"""
        return {
            'timing_score': self._calculate_timing_score(market_context),
            'market_phase': self._identify_market_phase(market_context),
            'entry_readiness': self._assess_entry_readiness(market_context),
            'exit_considerations': self._assess_exit_considerations(market_context)
        }
    
    def _calculate_timing_score(self, market_context: MarketContext) -> float:
        """Timing ballini hisoblash"""
        # Combine multiple factors for timing assessment
        trend_factor = market_context.trend_strength
        volatility_factor = 1.0 - abs(market_context.volatility_level - 0.5) * 2  # Optimal volatility around 0.5
        sentiment_factor = abs(market_context.sentiment_score - 0.5) * 2  # Balanced sentiment
        
        timing_score = (trend_factor * 0.4 + volatility_factor * 0.3 + sentiment_factor * 0.3)
        return min(1.0, timing_score)
    
    def _identify_market_phase(self, market_context: MarketContext) -> str:
        """Bozor fazasini aniqlash"""
        if market_context.trend_strength > 0.7:
            return 'trending'
        elif market_context.volatility_level < 0.3:
            return 'consolidation'
        elif market_context.volatility_level > 0.8:
            return 'chaos'
        else:
            return 'transition'
    
    def _assess_entry_readiness(self, market_context: MarketContext) -> str:
        """Kirish readiness ni baholash"""
        timing_score = self._calculate_timing_score(market_context)
        
        if timing_score > 0.7:
            return 'high'
        elif timing_score > 0.4:
            return 'moderate'
        else:
            return 'low'
    
    def _assess_exit_considerations(self, market_context: MarketContext) -> List[str]:
        """Chiqish mulohazalarini baholash"""
        considerations = []
        
        if market_context.volatility_level > 0.8:
            considerations.append("Consider profit protection due to high volatility")
        
        if market_context.sentiment_score > 0.8:
            considerations.append("Extreme optimism - consider taking profits")
        
        if market_context.trend_strength < 0.3:
            considerations.append("Weak trend - reassess positions")
        
        return considerations
    
    def _analyze_sectors(self, market_context: MarketContext) -> Dict[str, Any]:
        """Sektor tahlili"""
        return {
            'sector_performance': self._assess_sector_performance(market_context),
            'rotation_signals': self._identify_rotation_signals(market_context),
            'sector_correlation': self._analyze_sector_correlation(market_context)
        }
    
    def _assess_sector_performance(self, market_context: MarketContext) -> Dict[str, str]:
        """Sektor ishlamasini baholash"""
        # Simplified sector assessment based on market conditions
        if market_context.trend_strength > 0.6:
            return {
                'technology': 'outperforming',
                'consumer': 'stable',
                'energy': 'mixed'
            }
        else:
            return {
                'technology': 'mixed',
                'consumer': 'defensive',
                'energy': 'volatile'
            }
    
    def _identify_rotation_signals(self, market_context: MarketContext) -> List[str]:
        """Sektor rotatsiya signallarini aniqlash"""
        signals = []
        
        if market_context.volatility_level > 0.7:
            signals.append("High volatility - sector rotation likely")
        
        if market_context.trend_strength < 0.4:
            signals.append("Sideways market - defensive rotation")
        
        return signals
    
    def _analyze_sector_correlation(self, market_context: MarketContext) -> Dict[str, float]:
        """Sektor korrelatsiyasini tahlil qilish"""
        # Simplified correlation analysis
        base_correlation = 0.7 if market_context.volatility_level < 0.5 else 0.9
        
        return {
            'tech_consumer': base_correlation,
            'tech_energy': base_correlation * 0.8,
            'consumer_energy': base_correlation * 0.6
        }
    
    # Default and utility methods
    def _create_default_user_context(self) -> Dict[str, Any]:
        """Default foydalanuvchi kontekstini yaratish"""
        return {
            'user_profile_summary': {'user_id': 'default', 'experience_level': 'intermediate'},
            'skill_assessment': {'assessed_level': 'intermediate', 'skill_score': 0.5},
            'risk_tolerance': {'adjusted_tolerance': 0.5, 'recommended_allocation': {}},
            'learning_style': {'style': 'visual', 'recommended_formats': ['charts', 'diagrams']},
            'communication_preference': {'tone': 'formal', 'language_level': 'professional'},
            'market_preferences': {'primary_markets': [], 'market_diversity': 0},
            'behavioral_patterns': {'trading_frequency': 'moderate', 'risk_taking_behavior': 'moderate'},
            'optimization_recommendations': {'prompt_complexity': 'intermediate', 'detail_level': 'moderate'}
        }
    
    def _create_default_market_context(self) -> Dict[str, Any]:
        """Default bozor kontekstini yaratish"""
        return {
            'market_regime_analysis': {'current_regime': 'unknown', 'regime_strength': 0.5},
            'volatility_assessment': {'volatility_level': 'moderate', 'volatility_score': 0.5},
            'trend_analysis': {'trend_strength': 0.5, 'trend_direction': 'sideways'},
            'sentiment_analysis': {'sentiment': 'neutral', 'sentiment_score': 0.5},
            'risk_factors': [],
            'opportunities': [],
            'market_timing': {'timing_score': 0.5, 'market_phase': 'unknown'},
            'sector_analysis': {'sector_performance': {}, 'rotation_signals': []}
        }
    
    def _create_default_behavioral_patterns(self) -> Dict[str, Any]:
        """Default xulq-atvor patternlarini yaratish"""
        return {
            'trading_frequency': {'frequency': 'moderate', 'consistency': 0.5},
            'risk_taking_behavior': {'risk_tolerance': 'moderate', 'position_sizing': 'moderate'},
            'performance_consistency': {'consistency_score': 0.5, 'trend_analysis': 'stable'},
            'learning_patterns': {'adaptation_speed': 'moderate', 'continuous_improvement': 'steady'},
            'decision_making_style': {'decision_quality': 'good', 'impulsiveness': 'low'},
            'improvement_areas': ['Practice', 'Risk Management']
        }
    
    # Data management methods
    def store_user_profile(self, profile: UserProfile):
        """Foydalanuvchi profilini saqlash"""
        self.user_profiles[profile.user_id] = profile
        logger.info(f"Stored user profile for: {profile.user_id}")
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Foydalanuvchi profilini olish"""
        return self.user_profiles.get(user_id)
    
    def store_market_context(self, context: MarketContext):
        """Bozor kontekstini saqlash"""
        context_id = f"market_{context.timestamp.strftime('%Y%m%d_%H%M')}"
        self.market_contexts[context_id] = context
        logger.info(f"Stored market context: {context_id}")
    
    def get_market_context(self, timestamp: datetime) -> Optional[MarketContext]:
        """Bozor kontekstini olish"""
        context_id = f"market_{timestamp.strftime('%Y%m%d_%H%M')}"
        return self.market_contexts.get(context_id)
    
    def store_portfolio_status(self, user_id: str, status: PortfolioStatus):
        """Portfolio holatini saqlash"""
        self.portfolio_statuses[user_id] = status
        logger.info(f"Stored portfolio status for: {user_id}")
    
    def get_portfolio_status(self, user_id: str) -> Optional[PortfolioStatus]:
        """Portfolio holatini olish"""
        return self.portfolio_statuses.get(user_id)
    
    def store_trading_history(self, user_id: str, history: TradingHistory):
        """Trading tarixini saqlash"""
        self.trading_histories[user_id] = history
        logger.info(f"Stored trading history for: {user_id}")
    
    def get_trading_history(self, user_id: str) -> Optional[TradingHistory]:
        """Trading tarixini olish"""
        return self.trading_histories.get(user_id)
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Tahlil xulosasini olish"""
        return {
            'user_profiles_count': len(self.user_profiles),
            'market_contexts_count': len(self.market_contexts),
            'portfolio_statuses_count': len(self.portfolio_statuses),
            'trading_histories_count': len(self.trading_histories),
            'cached_analyses': len(self.analysis_cache),
            'trend_data_points': {
                'volatility': len(self.trend_analysis['volatility']),
                'sentiment': len(self.trend_analysis['sentiment'])
            }
        }

# Sample data generator for testing
class SampleDataGenerator:
    """Test uchun namuna ma'lumotlar yaratuvchi"""
    
    @staticmethod
    def create_sample_user_profile(user_id: str = "user_123") -> UserProfile:
        """Namuna foydalanuvchi profili yaratish"""
        return UserProfile(
            user_id=user_id,
            name="Sample User",
            email="user@example.com",
            skill_level=SkillLevel.INTERMEDIATE,
            experience_years=3.5,
            risk_profile=RiskProfile.MODERATE,
            communication_style=CommunicationStyle.FORMAL,
            learning_preference=LearningPreference.VISUAL,
            trading_style="swing_trading",
            preferred_markets=["stocks", "forex", "crypto"],
            investment_goals=["capital_growth", "income", "diversification"],
            time_horizon="medium_term",
            current_portfolio_value=50000.0,
            yearly_income=75000.0,
            age=35,
            location="Tashkent",
            language="uzbek",
            timezone="UTC+5",
            created_date=datetime.now() - timedelta(days=365),
            last_active=datetime.now()
        )
    
    @staticmethod
    def create_sample_market_context() -> MarketContext:
        """Namuna bozor konteksti yaratish"""
        return MarketContext(
            timestamp=datetime.now(),
            market_regime=MarketRegime.TRENDING,
            volatility_level=0.65,
            trend_strength=0.75,
            volume_level="high",
            sentiment_score=0.68,
            key_events=["Fed meeting", "Earnings season", "Geopolitical developments"],
            economic_indicators={
                "GDP_growth": 2.1,
                "unemployment": 3.8,
                "inflation": 2.4,
                "interest_rate": 5.25
            },
            central_bank_status="hawkish",
            geopolitical_risk="moderate",
            liquidity_conditions="normal",
            correlation_levels={
                "S&P_500_bonds": -0.3,
                "USD_gold": 0.1,
                "oil_stocks": 0.7
            }
        )
    
    @staticmethod
    def create_sample_portfolio_status(user_id: str = "user_123") -> PortfolioStatus:
        """Namuna portfolio holati yaratish"""
        return PortfolioStatus(
            total_value=50000.0,
            daily_pnl=250.0,
            daily_pnl_percent=0.5,
            positions=[
                {"symbol": "AAPL", "value": 15000, "pnl": 300},
                {"symbol": "MSFT", "value": 12000, "pnl": -150},
                {"symbol": "EURUSD", "value": 8000, "pnl": 100}
            ],
            cash_position=15000.0,
            margin_used=2000.0,
            max_drawdown=8.5,
            win_rate=0.62,
            profit_factor=1.35,
            sharpe_ratio=1.2,
            last_rebalanced=datetime.now() - timedelta(days=7),
            risk_metrics={
                "VaR_95": 1200.0,
                "beta": 0.95,
                "correlation": 0.75
            }
        )
    
    @staticmethod
    def create_sample_trading_history(user_id: str = "user_123") -> TradingHistory:
        """Namuna trading tarixi yaratish"""
        return TradingHistory(
            user_id=user_id,
            total_trades=156,
            winning_trades=97,
            losing_trades=59,
            total_pnl=8750.0,
            average_win=185.0,
            average_loss=-125.0,
            best_trade=1200.0,
            worst_trade=-850.0,
            longest_win_streak=8,
            longest_loss_streak=3,
            total_fees=234.0,
            trading_days=180,
            strategies_used=["momentum", "mean_reversion", "breakout"],
            markets_traded=["stocks", "forex", "crypto"],
            preferred_timeframes=["1d", "4h", "1h"],
            common_mistakes=["overtrading", "emotional_decisions"],
            success_patterns=["trend_following", "risk_management"],
            last_updated=datetime.now()
        )

# Usage example
if __name__ == "__main__":
    # Initialize context analyzer
    analyzer = ContextAnalyzer()
    
    # Create sample data
    user_profile = SampleDataGenerator.create_sample_user_profile()
    market_context = SampleDataGenerator.create_sample_market_context()
    portfolio_status = SampleDataGenerator.create_sample_portfolio_status()
    trading_history = SampleDataGenerator.create_sample_trading_history()
    
    # Store data
    analyzer.store_user_profile(user_profile)
    analyzer.store_market_context(market_context)
    analyzer.store_portfolio_status(user_profile.user_id, portfolio_status)
    analyzer.store_trading_history(user_profile.user_id, trading_history)
    
    # Perform analysis
    user_analysis = analyzer.analyze_user_context(user_profile)
    market_analysis = analyzer.analyze_market_context(market_context)
    
    print("User Context Analysis:")
    print(json.dumps(user_analysis, indent=2, default=str))
    
    print("\nMarket Context Analysis:")
    print(json.dumps(market_analysis, indent=2, default=str))
    
    # Get analysis summary
    summary = analyzer.get_analysis_summary()
    print(f"\nAnalysis Summary: {summary}")
