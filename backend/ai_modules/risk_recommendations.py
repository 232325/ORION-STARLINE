"""
Risk Recommendations System
===========================

AI-powered risk management and investment recommendations system.
Provides personalized risk recommendations based on user profiles and market conditions.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Import related modules
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from risk_profile_generator import UserProfile, RiskProfileType, RiskAssessment
from user_behavior_analyzer import InvestmentBehaviorProfile, BehavioralPattern, BiasAnalysis

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommendationType(Enum):
    """Types of risk recommendations"""
    ASSET_ALLOCATION = "asset_allocation"
    POSITION_SIZING = "position_sizing"
    RISK_MANAGEMENT = "risk_management"
    BEHAVIORAL_CORRECTION = "behavioral_correction"
    PORTFOLIO_REBALANCING = "portfolio_rebalancing"
    DIVERSIFICATION = "diversification"
    STRESS_TESTING = "stress_testing"
    EMERGENCY_PLAN = "emergency_plan"

class UrgencyLevel(Enum):
    """Urgency levels for recommendations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskRecommendation:
    """Individual risk recommendation"""
    recommendation_id: str
    type: RecommendationType
    title: str
    description: str
    urgency: UrgencyLevel
    confidence: float
    priority_score: float
    expected_impact: str
    implementation_steps: List[str]
    success_metrics: List[str]
    risk_factors: List[str]
    market_conditions: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool = True

@dataclass
class PortfolioRecommendation:
    """Portfolio-level recommendations"""
    user_id: str
    current_allocation: Dict[str, float]
    recommended_allocation: Dict[str, float]
    rebalancing_actions: List[Dict[str, Any]]
    risk_metrics: Dict[str, float]
    expected_performance: Dict[str, Any]
    recommendations: List[RiskRecommendation]
    last_updated: datetime
    validity_period_days: int = 30

@dataclass
class BehavioralRecommendation:
    """Behavioral improvement recommendations"""
    bias_name: str
    current_score: float
    recommended_actions: List[str]
    progress_tracking: Dict[str, Any]
    milestones: List[Dict[str, Any]]
    intervention_strategies: List[str]
    success_indicators: List[str]

class RiskRecommendations:
    """AI-powered risk recommendations system"""
    
    def __init__(self):
        """Initialize the risk recommendations system"""
        
        # Risk thresholds and parameters
        self.risk_thresholds = {
            'position_size_max': 25.0,  # Maximum single position size %
            'sector_concentration_max': 40.0,  # Maximum sector allocation %
            'volatility_threshold': 20.0,  # High volatility threshold %
            'drawdown_threshold': 15.0,  # Maximum acceptable drawdown %
            'correlation_threshold': 0.8  # High correlation threshold
        }
        
        # Market condition indicators
        self.market_indicators = {
            'vix_level': 20.0,  # Fear index
            'volatility_regime': 'normal',  # low, normal, high, crisis
            'correlation_increase': 1.5,  # Market correlation spike
            'liquidity_condition': 'normal'  # poor, normal, excellent
        }
        
        # Default asset allocation templates by risk profile
        self.allocation_templates = {
            RiskProfileType.CONSERVATIVE: {
                'cash': 20.0,
                'bonds': 50.0,
                'stocks': 20.0,
                'alternatives': 5.0,
                'commodities': 5.0
            },
            RiskProfileType.MODERATELY_CONSERVATIVE: {
                'cash': 15.0,
                'bonds': 40.0,
                'stocks': 35.0,
                'alternatives': 5.0,
                'commodities': 5.0
            },
            RiskProfileType.MODERATE: {
                'cash': 10.0,
                'bonds': 30.0,
                'stocks': 50.0,
                'alternatives': 5.0,
                'commodities': 5.0
            },
            RiskProfileType.MODERATELY_AGGRESSIVE: {
                'cash': 5.0,
                'bonds': 20.0,
                'stocks': 65.0,
                'alternatives': 7.0,
                'commodities': 3.0
            },
            RiskProfileType.AGGRESSIVE: {
                'cash': 3.0,
                'bonds': 10.0,
                'stocks': 77.0,
                'alternatives': 7.0,
                'commodities': 3.0
            },
            RiskProfileType.ULTRA_AGGRESSIVE: {
                'cash': 2.0,
                'bonds': 5.0,
                'stocks': 83.0,
                'alternatives': 8.0,
                'commodities': 2.0
            }
        }
        
        # Behavioral bias mitigation strategies
        self.bias_mitigation = {
            'overconfidence': {
                'position_size_reduction': 0.8,  # Reduce position sizes by 20%
                'research_requirement': True,
                'peer_review_needed': True,
                'cooldown_period_hours': 24
            },
            'loss_aversion': {
                'stop_loss_implementation': True,
                'profit_taking_rules': True,
                'position_size_limits': 0.9,  # Reduce by 10%
                'emotional_trading_cooldown': 48
            },
            'herding': {
                'independent_research_required': True,
                'sentiment_opposite_trades': True,
                'contrarian_strategy_weight': 0.3,
                'diversification_boost': 1.2
            },
            'recency_bias': {
                'lookback_period_months': 6,
                'historical_analysis_required': True,
                'trend_reversal_indicators': True,
                'momentum_opposite_weights': 0.2
            },
            'anchoring': {
                'reference_point_reset_frequency': 'monthly',
                'multiple_scenario_analysis': True,
                'flexible_position_sizing': True,
                'market_adaptation_required': True
            },
            'mental_accounting': {
                'unified_risk_budget': True,
                'total_portfolio_view': True,
                'goal_based_allocation': True,
                'cross_account_optimization': True
            }
        }
        
        # Risk management rules
        self.risk_rules = {
            'max_single_position': 0.25,  # 25% max
            'max_sector_exposure': 0.40,  # 40% max
            'max_correlation_exposure': 0.60,  # 60% max correlated assets
            'stop_loss_default': 0.10,  # 10% stop loss
            'profit_taking_threshold': 0.20,  # 20% profit taking
            'rebalancing_frequency': 'quarterly',
            'position_entry_timing': 'systematic'
        }
    
    def generate_portfolio_recommendations(
        self,
        user_profile: UserProfile,
        behavioral_profile: InvestmentBehaviorProfile,
        current_portfolio: Dict[str, Any],
        market_conditions: Optional[Dict[str, Any]] = None
    ) -> PortfolioRecommendation:
        """
        Generate comprehensive portfolio recommendations
        
        Args:
            user_profile: User's risk profile
            behavioral_profile: User's behavioral analysis
            current_portfolio: Current portfolio holdings
            market_conditions: Current market conditions
            
        Returns:
            PortfolioRecommendation with detailed recommendations
        """
        try:
            # Update market conditions
            if market_conditions:
                self.market_indicators.update(market_conditions)
            
            # Get recommended allocation based on risk profile
            recommended_allocation = self._get_recommended_allocation(user_profile)
            
            # Analyze current portfolio
            current_allocation = self._analyze_current_allocation(current_portfolio)
            
            # Generate rebalancing actions
            rebalancing_actions = self._generate_rebalancing_actions(
                current_allocation, recommended_allocation
            )
            
            # Calculate risk metrics
            risk_metrics = self._calculate_portfolio_risk_metrics(
                current_allocation, recommended_allocation, user_profile
            )
            
            # Generate specific recommendations
            recommendations = self._generate_specific_recommendations(
                user_profile, behavioral_profile, current_portfolio, market_conditions
            )
            
            # Calculate expected performance
            expected_performance = self._calculate_expected_performance(
                recommended_allocation, user_profile
            )
            
            # Create portfolio recommendation
            portfolio_rec = PortfolioRecommendation(
                user_id=user_profile.user_id,
                current_allocation=current_allocation,
                recommended_allocation=recommended_allocation,
                rebalancing_actions=rebalancing_actions,
                risk_metrics=risk_metrics,
                expected_performance=expected_performance,
                recommendations=recommendations,
                last_updated=datetime.now()
            )
            
            logger.info(f"Generated portfolio recommendations for user {user_profile.user_id}")
            return portfolio_rec
            
        except Exception as e:
            logger.error(f"Error generating portfolio recommendations: {e}")
            return self._create_default_recommendation(user_profile.user_id)
    
    def _get_recommended_allocation(self, user_profile: UserProfile) -> Dict[str, float]:
        """Get recommended asset allocation based on risk profile"""
        base_allocation = self.allocation_templates.get(
            user_profile.profile_type,
            self.allocation_templates[RiskProfileType.MODERATE]
        ).copy()
        
        # Adjust for investment goals
        for goal in user_profile.investment_goals:
            base_allocation = self._adjust_allocation_for_goals(base_allocation, goal, user_profile.risk_score)
        
        # Adjust for time horizon
        base_allocation = self._adjust_allocation_for_horizon(base_allocation, user_profile.time_horizon)
        
        # Adjust for liquidity needs
        base_allocation = self._adjust_allocation_for_liquidity(base_allocation, user_profile.liquidity_need)
        
        # Ensure allocation sums to 100%
        total = sum(base_allocation.values())
        if total > 0:
            base_allocation = {k: v/total*100 for k, v in base_allocation.items()}
        
        return base_allocation
    
    def _adjust_allocation_for_goals(self, allocation: Dict[str, float], goal: str, risk_score: float) -> Dict[str, float]:
        """Adjust allocation based on investment goals"""
        adjusted = allocation.copy()
        
        if goal == 'capital_preservation':
            # Increase defensive assets
            adjusted['cash'] = min(adjusted.get('cash', 0) + 10, 30)
            adjusted['bonds'] = min(adjusted.get('bonds', 0) + 10, 60)
            adjusted['stocks'] = max(adjusted.get('stocks', 0) - 20, 10)
        elif goal == 'income_generation':
            # Focus on income-generating assets
            adjusted['bonds'] = min(adjusted.get('bonds', 0) + 15, 50)
            adjusted['stocks'] = max(adjusted.get('stocks', 0) - 10, 20)
            adjusted['cash'] = max(adjusted.get('cash', 0) - 5, 5)
        elif goal == 'aggressive_growth':
            # Increase growth assets
            adjusted['stocks'] = min(adjusted.get('stocks', 0) + 15, 80)
            adjusted['bonds'] = max(adjusted.get('bonds', 0) - 10, 5)
            adjusted['cash'] = max(adjusted.get('cash', 0) - 5, 2)
        elif goal == 'speculation':
            # High-risk, high-reward allocation
            adjusted['alternatives'] = min(adjusted.get('alternatives', 0) + 10, 20)
            adjusted['commodities'] = min(adjusted.get('commodities', 0) + 5, 10)
            adjusted['stocks'] = min(adjusted.get('stocks', 0) + 10, 85)
        
        return adjusted
    
    def _adjust_allocation_for_horizon(self, allocation: Dict[str, float], time_horizon: int) -> Dict[str, float]:
        """Adjust allocation based on investment time horizon"""
        adjusted = allocation.copy()
        years = time_horizon / 12  # Convert months to years
        
        if years < 2:  # Short term
            adjusted['cash'] = min(adjusted.get('cash', 0) + 20, 40)
            adjusted['bonds'] = min(adjusted.get('bonds', 0) + 10, 50)
            adjusted['stocks'] = max(adjusted.get('stocks', 0) - 30, 10)
        elif years < 5:  # Medium term
            adjusted['cash'] = max(adjusted.get('cash', 0) - 5, 5)
            adjusted['bonds'] = max(adjusted.get('bonds', 0) - 5, 10)
            adjusted['stocks'] = min(adjusted.get('stocks', 0) + 10, 70)
        elif years > 10:  # Long term
            adjusted['cash'] = max(adjusted.get('cash', 0) - 5, 2)
            adjusted['bonds'] = max(adjusted.get('bonds', 0) - 10, 5)
            adjusted['stocks'] = min(adjusted.get('stocks', 0) + 15, 80)
        
        return adjusted
    
    def _adjust_allocation_for_liquidity(self, allocation: Dict[str, float], liquidity_need: str) -> Dict[str, float]:
        """Adjust allocation based on liquidity needs"""
        adjusted = allocation.copy()
        
        if liquidity_need == 'immediate':
            adjusted['cash'] = min(adjusted.get('cash', 0) + 30, 50)
            adjusted['bonds'] = max(adjusted.get('bonds', 0) - 20, 10)
            adjusted['stocks'] = max(adjusted.get('stocks', 0) - 10, 20)
        elif liquidity_need == 'short_term':
            adjusted['cash'] = min(adjusted.get('cash', 0) + 15, 30)
            adjusted['bonds'] = max(adjusted.get('bonds', 0) - 10, 15)
        elif liquidity_need == 'long_term' or liquidity_need == 'no_liquidity_need':
            adjusted['cash'] = max(adjusted.get('cash', 0) - 10, 2)
            adjusted['alternatives'] = min(adjusted.get('alternatives', 0) + 5, 15)
        
        return adjusted
    
    def _analyze_current_allocation(self, current_portfolio: Dict[str, Any]) -> Dict[str, float]:
        """Analyze current portfolio allocation"""
        allocation = {
            'cash': current_portfolio.get('cash_percentage', 0),
            'bonds': current_portfolio.get('bonds_percentage', 0),
            'stocks': current_portfolio.get('stocks_percentage', 0),
            'alternatives': current_portfolio.get('alternatives_percentage', 0),
            'commodities': current_portfolio.get('commodities_percentage', 0)
        }
        
        # If detailed breakdown not available, estimate from holdings
        if sum(allocation.values()) == 0:
            holdings = current_portfolio.get('holdings', [])
            total_value = sum(h.get('value', 0) for h in holdings)
            
            for holding in holdings:
                asset_type = holding.get('type', 'unknown').lower()
                value = holding.get('value', 0)
                if total_value > 0:
                    percentage = (value / total_value) * 100
                    if 'cash' in asset_type or 'money_market' in asset_type:
                        allocation['cash'] += percentage
                    elif 'bond' in asset_type or 'fixed_income' in asset_type:
                        allocation['bonds'] += percentage
                    elif 'stock' in asset_type or 'equity' in asset_type:
                        allocation['stocks'] += percentage
                    elif 'alternative' in asset_type:
                        allocation['alternatives'] += percentage
                    elif 'commodity' in asset_type or 'gold' in asset_type:
                        allocation['commodities'] += percentage
        
        return allocation
    
    def _generate_rebalancing_actions(
        self,
        current: Dict[str, float],
        recommended: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Generate specific rebalancing actions"""
        actions = []
        threshold = 5.0  # 5% threshold for rebalancing
        
        for asset_type in recommended.keys():
            current_pct = current.get(asset_type, 0)
            recommended_pct = recommended.get(asset_type, 0)
            difference = recommended_pct - current_pct
            
            if abs(difference) > threshold:
                action = {
                    'asset_type': asset_type,
                    'action': 'buy' if difference > 0 else 'sell',
                    'current_allocation': current_pct,
                    'target_allocation': recommended_pct,
                    'rebalance_amount': abs(difference),
                    'urgency': 'high' if abs(difference) > 15 else 'medium',
                    'reason': f"Current allocation {current_pct:.1f}% deviates from target {recommended_pct:.1f}%"
                }
                actions.append(action)
        
        return actions
    
    def _calculate_portfolio_risk_metrics(
        self,
        current: Dict[str, float],
        recommended: Dict[str, float],
        user_profile: UserProfile
    ) -> Dict[str, float]:
        """Calculate portfolio risk metrics"""
        metrics = {}
        
        # Expected volatility based on allocation
        volatility_weights = {
            'cash': 1.0,
            'bonds': 5.0,
            'stocks': 18.0,
            'alternatives': 15.0,
            'commodities': 20.0
        }
        
        # Calculate expected volatility
        current_volatility = sum(
            allocation * volatility_weights.get(asset, 10) 
            for asset, allocation in current.items()
        ) / 100
        
        recommended_volatility = sum(
            allocation * volatility_weights.get(asset, 10) 
            for asset, allocation in recommended.items()
        ) / 100
        
        metrics['current_expected_volatility'] = current_volatility
        metrics['recommended_expected_volatility'] = recommended_volatility
        
        # Risk score adjustment
        metrics['risk_score_reduction'] = max(0, current_volatility - recommended_volatility)
        
        # Diversification score
        metrics['diversification_score'] = self._calculate_diversification_score(recommended)
        
        # Risk-adjusted return potential
        risk_free_rate = 2.0  # 2% risk-free rate
        expected_return = self._calculate_expected_return(recommended)
        metrics['sharpe_ratio_estimate'] = (expected_return - risk_free_rate) / max(recommended_volatility, 1)
        
        # Maximum drawdown estimate
        metrics['max_drawdown_estimate'] = recommended_volatility * 2.5  # Rough estimate
        
        return metrics
    
    def _calculate_diversification_score(self, allocation: Dict[str, float]) -> float:
        """Calculate portfolio diversification score"""
        # Herfindahl-Hirschman Index (lower is more diversified)
        hhi = sum((pct/100)**2 for pct in allocation.values() if pct > 0)
        
        # Convert to diversification score (0-100, higher is more diversified)
        max_hhi = 1.0  # Maximum possible concentration
        diversification_score = (1 - hhi) * 100
        
        return max(0, min(100, diversification_score))
    
    def _calculate_expected_return(self, allocation: Dict[str, float]) -> float:
        """Calculate expected return based on allocation"""
        return_weights = {
            'cash': 2.0,  # 2% expected return
            'bonds': 4.0,  # 4% expected return
            'stocks': 8.0,  # 8% expected return
            'alternatives': 6.0,  # 6% expected return
            'commodities': 3.0   # 3% expected return (highly variable)
        }
        
        expected_return = sum(
            allocation.get(asset, 0) * return_weights.get(asset, 5) / 100
            for asset in allocation.keys()
        )
        
        return expected_return
    
    def _generate_specific_recommendations(
        self,
        user_profile: UserProfile,
        behavioral_profile: InvestmentBehaviorProfile,
        current_portfolio: Dict[str, Any],
        market_conditions: Optional[Dict[str, Any]] = None
    ) -> List[RiskRecommendation]:
        """Generate specific risk recommendations"""
        recommendations = []
        
        # Portfolio-level recommendations
        recommendations.extend(self._generate_portfolio_level_recs(user_profile, current_portfolio))
        
        # Risk management recommendations
        recommendations.extend(self._generate_risk_management_recs(user_profile, current_portfolio))
        
        # Behavioral bias recommendations
        recommendations.extend(self._generate_behavioral_recs(behavioral_profile))
        
        # Market condition recommendations
        if market_conditions:
            recommendations.extend(self._generate_market_condition_recs(market_conditions, user_profile))
        
        # Sort by priority score
        recommendations.sort(key=lambda x: x.priority_score, reverse=True)
        
        return recommendations
    
    def _generate_portfolio_level_recs(
        self,
        user_profile: UserProfile,
        current_portfolio: Dict[str, Any]
    ) -> List[RiskRecommendation]:
        """Generate portfolio-level recommendations"""
        recs = []
        
        # Concentration risk recommendation
        if user_profile.risk_score > 70:
            rec_id = f"concentration_check_{user_profile.user_id}_{datetime.now().strftime('%Y%m%d')}"
            rec = RiskRecommendation(
                recommendation_id=rec_id,
                type=RecommendationType.DIVERSIFICATION,
                title="Konsentratsiya xavfini kamaytirish",
                description="Yuqori xavf profili uchun portfel diversifikatsiyasini oshirish zarur",
                urgency=UrgencyLevel.HIGH,
                confidence=0.85,
                priority_score=90,
                expected_impact="Xavfni kamaytirish va barqarorlikni oshirish",
                implementation_steps=[
                    "Har bir pozitsiya hajmini 20% gacha cheklash",
                    "Turli sektorlarga investitsiya qilish",
                    "Turli geografik hududlarda diversifikatsiya",
                    "Aktiv turiga ko'ra taqsimot"
                ],
                success_metrics=[
                    "Pozitsiyalar o'rtacha hajmi < 20%",
                    "Sektor konsentratsiyasi < 30%",
                    "Sharpe nisbati yaxshilanishi"
                ],
                risk_factors=["Diversifikatsiya yo'qotish", "Kurs volatiliti"],
                market_conditions=self.market_indicators,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=90)
            )
            recs.append(rec)
        
        # Time horizon adjustment recommendation
        if user_profile.time_horizon < 24:  # Less than 2 years
            rec_id = f"time_horizon_adj_{user_profile.user_id}_{datetime.now().strftime('%Y%m%d')}"
            rec = RiskRecommendation(
                recommendation_id=rec_id,
                type=RecommendationType.ASSET_ALLOCATION,
                title="Qisqa muddat uchun allokatsiyani moslashtirish",
                description="Qisqa muddat uchun kam xavfli aktivlarga e'tibor qaratish",
                urgency=UrgencyLevel.MEDIUM,
                confidence=0.90,
                priority_score=80,
                expected_impact="Qisqa muddatli xavflarni kamaytirish",
                implementation_steps=[
                    "Naqd mablag'ni 20-30% gacha oshirish",
                    "Qisqa muddatli obligatsiyalarga fokus qilish",
                    "Yuqori volatil aktsiyalarni kamaytirish",
                    "Kichik, barqaror kompaniyalarni tanlash"
                ],
                success_metrics=[
                    "Kichik potentsial yo'qotish",
                    "Kutilayotgan daromad o'zgarmasdan",
                    "Xavf/volatil kamayishi"
                ],
                risk_factors=["Inflyatsiya xavfi", "Real daromad yo'qotish"],
                market_conditions=self.market_indicators,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=60)
            )
            recs.append(rec)
        
        return recs
    
    def _generate_risk_management_recs(
        self,
        user_profile: UserProfile,
        current_portfolio: Dict[str, Any]
    ) -> List[RiskRecommendation]:
        """Generate risk management recommendations"""
        recs = []
        
        # Stop-loss implementation
        if user_profile.risk_score > 50:
            rec_id = f"stop_loss_{user_profile.user_id}_{datetime.now().strftime('%Y%m%d')}"
            rec = RiskRecommendation(
                recommendation_id=rec_id,
                type=RecommendationType.RISK_MANAGEMENT,
                title="Stop-loss strategiyasini joriy etish",
                description="Xavflarni cheklash uchun stop-loss qoidalarini belgilash",
                urgency=UrgencyLevel.HIGH,
                confidence=0.95,
                priority_score=95,
                expected_impact="Katta yo'qotishlarni oldini olish",
                implementation_steps=[
                    "Har bir pozitsiya uchun stop-loss darajasini belgilash",
                    "5-10% standart stop-loss qoidalarini qo'llash",
                    "Trailing stop-loss strategiyasini ko'rib chiqish",
                    "Muntazam qayta ko'rib chiqish va yangilash"
                ],
                success_metrics=[
                    "Maksimal yo'qotish < 10%",
                    "O'rtacha yo'qotish < 5%",
                    "Foydali savdolar foizi > 60%"
                ],
                risk_factors=["Too early exits", "Market volatility impact"],
                market_conditions=self.market_indicators,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=30)
            )
            recs.append(rec)
        
        # Position sizing optimization
        if user_profile.behavioral_biases.get('overconfidence', 50) > 60:
            rec_id = f"position_sizing_{user_profile.user_id}_{datetime.now().strftime('%Y%m%d')}"
            rec = RiskRecommendation(
                recommendation_id=rec_id,
                type=RecommendationType.POSITION_SIZING,
                title="Pozitsiya hajmini optimallashtirish",
                description="O'ziga ishonch ortiqchligi xatosi sababli pozitsiya hajmini cheklash",
                urgency=UrgencyLevel.MEDIUM,
                confidence=0.80,
                priority_score=70,
                expected_impact="Xavfni kamaytirish va barqarorlikni oshirish",
                implementation_steps=[
                    "Maksimum pozitsiya hajmini 15% gacha cheklash",
                    "Kelly mezoni yoki 2% qoidani qo'llash",
                    "Pozitsiya hajmini portfel hajmiga nisbatan hisoblash",
                    "Kichik pozitsiyalardan boshlash"
                ],
                success_metrics=[
                    "O'rtacha pozitsiya hajmi < 10%",
                    "Maksimum pozitsiya hajmi < 15%",
                    "Xavf/yutuq nisbati yaxshilanishi"
                ],
                risk_factors=["Profit potential reduction", "Opportunity cost"],
                market_conditions=self.market_indicators,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=45)
            )
            recs.append(rec)
        
        return recs
    
    def _generate_behavioral_recs(
        self,
        behavioral_profile: InvestmentBehaviorProfile
    ) -> List[RiskRecommendation]:
        """Generate behavioral bias correction recommendations"""
        recs = []
        
        # Loss aversion bias
        if behavioral_profile.loss_aversion_score > 65:
            rec_id = f"loss_aversion_{behavioral_profile.user_id}_{datetime.now().strftime('%Y%m%d')}"
            rec = RiskRecommendation(
                recommendation_id=rec_id,
                type=RecommendationType.BEHAVIORAL_CORRECTION,
                title="Yo'qotishlardan qochish xatosini bartaraf etish",
                description="Yo'qotishlardan haddan tashqari qochish natijasida yutuqlarni qo'yib yuborishni oldini olish",
                urgency=UrgencyLevel.MEDIUM,
                confidence=0.85,
                priority_score=75,
                expected_impact="Mantiqli qaror qabul qilish va yutuq potensialini oshirish",
                implementation_steps=[
                    "Mantiqiy stop-loss va take-profit darajalarini belgilash",
                    "Emotsional savdolar uchun 24 soat kutish qoidasi",
                    "Tizimli yondashuvni rivojlantirish",
                    "Profit va loss nisbatlarini reja asosida boshqarish"
                ],
                success_metrics=[
                    "Mantiqiy qaror qabul qilish ko'payishi",
                    "Too early exits kamayishi",
                    "Overall profitability improvement"
                ],
                risk_factors=["Emotional resistance", "Temporary discomfort"],
                market_conditions=self.market_indicators,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=60)
            )
            recs.append(rec)
        
        # Herding behavior
        if behavioral_profile.herd_instinct_score > 60:
            rec_id = f"herding_{behavioral_profile.user_id}_{datetime.now().strftime('%Y%m%d')}"
            rec = RiskRecommendation(
                recommendation_id=rec_id,
                type=RecommendationType.BEHAVIORAL_CORRECTION,
                title="Ola quvish instinktini cheklash",
                description="Ommabop fikrga ergashish o'rniga mustaqil tadqiqot qilish",
                urgency=UrgencyLevel.MEDIUM,
                confidence=0.80,
                priority_score=65,
                expected_impact="Mustaqil va asoslangan qarorlar qabul qilish",
                implementation_steps=[
                    "Har bir investitsiya qarori uchun mustaqil tadqiqot o'tkazish",
                    "Ommabop investitsiyalarga qarshi pozitsiya egallash",
                    "Kontrarian strategiyalarni qo'llash",
                    "Keng turli manbalardan ma'lumot to'plash"
                ],
                success_metrics=[
                    "Ommabop investitsiyalardan qochish",
                    "Mustaqil tadqiqot vaqtini oshirish",
                    "Contrarian trades success rate"
                ],
                risk_factors=["Missing trends", "Social isolation"],
                market_conditions=self.market_indicators,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=90)
            )
            recs.append(rec)
        
        return recs
    
    def _generate_market_condition_recs(
        self,
        market_conditions: Dict[str, Any],
        user_profile: UserProfile
    ) -> List[RiskRecommendation]:
        """Generate recommendations based on current market conditions"""
        recs = []
        
        # High volatility environment
        vix_level = market_conditions.get('vix', 20.0)
        if vix_level > 25:
            rec_id = f"high_vol_{user_profile.user_id}_{datetime.now().strftime('%Y%m%d')}"
            rec = RiskRecommendation(
                recommendation_id=rec_id,
                type=RecommendationType.PORTFOLIO_REBALANCING,
                title="Yuqori volatil muhitda portfel moslashuvi",
                description="Yuqori VIX darajasi tufayli xavfni kamaytirish",
                urgency=UrgencyLevel.HIGH,
                confidence=0.90,
                priority_score=85,
                expected_impact="Volatil muhitda yo'qotishlarni kamaytirish",
                implementation_steps=[
                    "Naqd mablag' ulushini oshirish",
                    "Defensiv sektorning aktsiyalariga o'tish",
                    "Oltin va boshqa himoya aktivlariga investitsiya",
                    "Pozitsiya hajmini kamaytirish"
                ],
                success_metrics=[
                    "Portfolio volatility kamayishi",
                    "Maximum drawdown cheklanishi",
                    "Sharpe ratio yaxshilanishi"
                ],
                risk_factors=["Opportunity cost", "Inflation impact"],
                market_conditions=market_conditions,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=30)
            )
            recs.append(rec)
        
        # Low volatility environment
        if vix_level < 15:
            rec_id = f"low_vol_{user_profile.user_id}_{datetime.now().strftime('%Y%m%d')}"
            rec = RiskRecommendation(
                recommendation_id=rec_id,
                type=RecommendationType.ASSET_ALLOCATION,
                title="Past volatil muhitda foydalanish",
                description="Past volatil muhitda yuqori xavfli aktivlarga e'tibor qaratish",
                urgency=UrgencyLevel.MEDIUM,
                confidence=0.85,
                priority_score=60,
                expected_impact="Yuqori daromad potensialini oshirish",
                implementation_steps=[
                    "Growt-sektor aktsiyalariga investitsiya qilish",
                    "Alternativ aktivlarni ko'rib chiqish",
                    "Yuqori beta aktsiyalarni qo'shish",
                    "Pozitsiya hajmini sekin ko'paytirish"
                ],
                success_metrics=[
                    "Expected return oshirish",
                    "Alpha generation",
                    "Risk-adjusted performance"
                ],
                risk_factors=["Volatility spike risk", "Correlation increase"],
                market_conditions=market_conditions,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=60)
            )
            recs.append(rec)
        
        return recs
    
    def _calculate_expected_performance(
        self,
        recommended_allocation: Dict[str, float],
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """Calculate expected portfolio performance"""
        expected_return = self._calculate_expected_return(recommended_allocation)
        
        # Risk metrics
        volatility_weights = {
            'cash': 1.0, 'bonds': 5.0, 'stocks': 18.0,
            'alternatives': 15.0, 'commodities': 20.0
        }
        expected_volatility = sum(
            allocation * volatility_weights.get(asset, 10) 
            for asset, allocation in recommended_allocation.items()
        ) / 100
        
        # Risk-free rate
        risk_free_rate = 2.0
        
        # Performance metrics
        sharpe_ratio = (expected_return - risk_free_rate) / max(expected_volatility, 1)
        max_drawdown = expected_volatility * 2.5
        var_95 = expected_volatility * 1.65  # 95% VaR
        
        return {
            'expected_annual_return': expected_return,
            'expected_volatility': expected_volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_estimate': max_drawdown,
            'var_95_daily': var_95 / np.sqrt(252),  # Daily VaR
            'risk_adjusted_return': expected_return / max(expected_volatility, 1),
            'diversification_benefit': self._calculate_diversification_score(recommended_allocation),
            'alignment_with_profile': self._calculate_profile_alignment(recommended_allocation, user_profile)
        }
    
    def _calculate_profile_alignment(
        self,
        allocation: Dict[str, float],
        user_profile: UserProfile
    ) -> float:
        """Calculate how well the allocation aligns with user profile"""
        target_allocation = self.allocation_templates.get(
            user_profile.profile_type,
            self.allocation_templates[RiskProfileType.MODERATE]
        )
        
        # Calculate alignment score (0-100)
        total_diff = sum(
            abs(allocation.get(asset, 0) - target_allocation.get(asset, 0))
            for asset in target_allocation.keys()
        )
        
        alignment_score = max(0, 100 - total_diff)
        return alignment_score
    
    def _create_default_recommendation(self, user_id: str) -> PortfolioRecommendation:
        """Create default recommendation for error cases"""
        return PortfolioRecommendation(
            user_id=user_id,
            current_allocation={'cash': 20, 'bonds': 40, 'stocks': 30, 'alternatives': 5, 'commodities': 5},
            recommended_allocation={'cash': 20, 'bonds': 40, 'stocks': 30, 'alternatives': 5, 'commodities': 5},
            rebalancing_actions=[],
            risk_metrics={'expected_volatility': 12.0, 'sharpe_ratio': 0.5},
            expected_performance={'expected_annual_return': 6.0, 'max_drawdown_estimate': 15.0},
            recommendations=[],
            last_updated=datetime.now()
        )
    
    def generate_behavioral_recommendations(
        self,
        behavioral_profile: InvestmentBehaviorProfile
    ) -> List[BehavioralRecommendation]:
        """
        Generate specific behavioral improvement recommendations
        
        Args:
            behavioral_profile: User's behavioral analysis profile
            
        Returns:
            List of BehavioralRecommendation objects
        """
        recommendations = []
        
        # Process each behavioral bias
        bias_scores = {
            'overconfidence': behavioral_profile.overconfidence_score,
            'loss_aversion': behavioral_profile.loss_aversion_score,
            'herding': behavioral_profile.herd_instinct_score,
            'recency': behavioral_profile.recency_bias_score,
            'anchoring': behavioral_profile.anchoring_score,
            'mental': behavioral_profile.mental_accounting_score
        }
        
        for bias_name, score in bias_scores.items():
            if score > 50:  # Only recommend if above neutral
                bias_rec = self._create_behavioral_recommendation(bias_name, score, behavioral_profile)
                recommendations.append(bias_rec)
        
        return recommendations
    
    def _create_behavioral_recommendation(
        self,
        bias_name: str,
        current_score: float,
        behavioral_profile: InvestmentBehaviorProfile
    ) -> BehavioralRecommendation:
        """Create recommendation for specific behavioral bias"""
        
        mitigation_strategies = self.bias_mitigation.get(bias_name, {})
        
        # Generate progress tracking
        progress_tracking = {
            'baseline_score': current_score,
            'target_score': max(30, current_score - 20),  # 20 point reduction
            'timeframe_weeks': 12,
            'checkpoints': [
                {'week': 4, 'target': current_score - 7},
                {'week': 8, 'target': current_score - 14},
                {'week': 12, 'target': max(30, current_score - 20)}
            ]
        }
        
        # Generate milestones
        milestones = [
            {
                'week': 4,
                'description': 'First checkpoint - awareness and basic strategies',
                'success_criteria': ['Complete bias awareness training', 'Implement basic controls']
            },
            {
                'week': 8,
                'description': 'Midpoint - consistent application',
                'success_criteria': ['Consistent strategy application', 'Measurable improvement']
            },
            {
                'week': 12,
                'description': 'Final target - behavioral change',
                'success_criteria': ['Target score achieved', 'Sustainable behavior change']
            }
        ]
        
        # Generate intervention strategies based on bias type
        intervention_strategies = self._get_intervention_strategies(bias_name, current_score)
        
        # Generate success indicators
        success_indicators = self._get_success_indicators(bias_name, behavioral_profile)
        
        return BehavioralRecommendation(
            bias_name=bias_name,
            current_score=current_score,
            recommended_actions=self._get_recommended_actions(bias_name, current_score),
            progress_tracking=progress_tracking,
            milestones=milestones,
            intervention_strategies=intervention_strategies,
            success_indicators=success_indicators
        )
    
    def _get_intervention_strategies(self, bias_name: str, score: float) -> List[str]:
        """Get intervention strategies for specific bias"""
        strategies = []
        
        if bias_name == 'overconfidence':
            strategies = [
                "Savdo qarorlarini kechiktirish va qayta ko'rib chiqish",
                "Pozitsiya hajmini avtomatik cheklash",
                "Boshqa treyderlardan fikr olish",
                "Kichik test pozitsiyalaridan boshlash"
            ]
        elif bias_name == 'loss_aversion':
            strategies = [
                "Mantiqiy stop-loss va take-profit darajalarini belgilash",
                "Emotsional qarorlar uchun 24 soat kutish",
                "Yo'qotishlar va yutuqlar uchun tizimli yondashuv",
                "Risk-reward nisbatini avval hisoblash"
            ]
        elif bias_name == 'herding':
            strategies = [
                "Ommabop fikrga qarshi tadqiqot o'tkazish",
                "Kontrarian strategiyalarni sinab ko'rish",
                "Mustaqil ma'lumot manbalaridan foydalanish",
                "Shaxsiy investment thesis yaratish"
            ]
        elif bias_name == 'recency':
            strategies = [
                "Uzoq muddatli ma'lumotlarni tahlil qilish",
                "So'nggi natijalarni qadrlash",
                "Tarixiy ma'lumotlar asosida qaror qabul qilish",
                "Trend o'zgarishini kuzatish"
            ]
        else:
            strategies = [
                "Conscious bias awareness training",
                "Systematic decision-making process",
                "Regular portfolio review and adjustment",
                "Professional guidance consideration"
            ]
        
        return strategies
    
    def _get_success_indicators(self, bias_name: str, behavioral_profile: InvestmentBehaviorProfile) -> List[str]:
        """Get success indicators for bias improvement"""
        indicators = []
        
        if bias_name == 'overconfidence':
            indicators = [
                "Position sizes reduced by 20%",
                "Research time increased by 50%",
                "Quick trades decreased",
                "Performance consistency improved"
            ]
        elif bias_name == 'loss_aversion':
            indicators = [
                "Rational stop-loss implementation",
                "Reduced premature profit-taking",
                "Better risk-reward ratios",
                "Emotional trading frequency decreased"
            ]
        elif bias_name == 'herding':
            indicators = [
                "Independent research time increased",
                "Contrarian positions taken successfully",
                "Market sentiment ignored when appropriate",
                "Better timing on entries and exits"
            ]
        else:
            indicators = [
                "Bias score reduction of 20+ points",
                "Consistent strategy application",
                "Improved decision quality",
                "Better risk-adjusted returns"
            ]
        
        return indicators
    
    def _get_recommended_actions(self, bias_name: str, score: float) -> List[str]:
        """Get specific recommended actions for bias"""
        actions = []
        
        if score > 70:  # High severity
            actions = [
                "Bias haqida chuqur o'rganish va xabardorlikni oshirish",
                "Professional counseling consideration",
                "Strict position sizing limits",
                "Emotional trading cooldown periods"
            ]
        elif score > 50:  # Medium severity
            actions = [
                "Bias awareness training",
                "Gradual strategy implementation",
                "Regular self-assessment",
                "Peer feedback system"
            ]
        else:  # Low severity
            actions = [
                "Maintain current awareness level",
                "Periodic bias checking",
                "Stay updated with best practices",
                "Continue education"
            ]
        
        return actions
    
    def export_recommendations(
        self,
        portfolio_recommendation: PortfolioRecommendation,
        format: str = 'json'
    ) -> str:
        """Export recommendations to specified format"""
        try:
            if format == 'dict':
                return asdict(portfolio_recommendation)
            elif format == 'json':
                return json.dumps(
                    asdict(portfolio_recommendation), 
                    default=str, 
                    indent=2, 
                    ensure_ascii=False
                )
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting recommendations: {e}")
            return "{}"
    
    def simulate_portfolio_performance(
        self,
        allocation: Dict[str, float],
        years: int = 1,
        scenarios: int = 1000
    ) -> Dict[str, Any]:
        """
        Simulate portfolio performance using Monte Carlo
        
        Args:
            allocation: Portfolio allocation
            years: Simulation period
            scenarios: Number of simulation scenarios
            
        Returns:
            Simulation results
        """
        try:
            # Asset return assumptions
            return_assumptions = {
                'cash': (0.02, 0.01),      # (mean, std)
                'bonds': (0.04, 0.05),
                'stocks': (0.08, 0.18),
                'alternatives': (0.06, 0.12),
                'commodities': (0.03, 0.20)
            }
            
            # Run Monte Carlo simulation
            final_values = []
            max_drawdowns = []
            
            for _ in range(scenarios):
                portfolio_value = 1.0  # Start with 1 unit
                peak = 1.0
                current_max_drawdown = 0.0
                
                for year in range(years * 252):  # 252 trading days per year
                    annual_return = 0.0
                    
                    for asset, weight in allocation.items():
                        if asset in return_assumptions:
                            mean, std = return_assumptions[asset]
                            asset_return = np.random.normal(mean/252, std/np.sqrt(252))
                            annual_return += weight * asset_return
                    
                    portfolio_value *= (1 + annual_return)
                    peak = max(peak, portfolio_value)
                    drawdown = (peak - portfolio_value) / peak
                    current_max_drawdown = max(current_max_drawdown, drawdown)
                
                final_values.append(portfolio_value)
                max_drawdowns.append(current_max_drawdown)
            
            # Calculate statistics
            final_values = np.array(final_values)
            max_drawdowns = np.array(max_drawdowns)
            
            return {
                'mean_final_value': np.mean(final_values),
                'median_final_value': np.median(final_values),
                'percentile_5': np.percentile(final_values, 5),
                'percentile_95': np.percentile(final_values, 95),
                'probability_positive': (final_values > 1.0).mean(),
                'probability_loss_10': (final_values < 0.9).mean(),
                'expected_annual_return': (np.mean(final_values) ** (1/years) - 1) * 100,
                'volatility': np.std(final_values) * np.sqrt(252) / np.mean(final_values),
                'max_drawdown_mean': np.mean(max_drawdowns) * 100,
                'max_drawdown_95': np.percentile(max_drawdowns, 95) * 100,
                'worst_case': np.min(final_values),
                'best_case': np.max(final_values)
            }
            
        except Exception as e:
            logger.error(f"Error in portfolio simulation: {e}")
            return {
                'mean_final_value': 1.0,
                'volatility': 0.15,
                'probability_positive': 0.5,
                'max_drawdown_mean': 20.0
            }

# Example usage and testing
if __name__ == "__main__":
    from risk_profile_generator import RiskProfileGenerator, RiskProfileType
    from user_behavior_analyzer import UserBehaviorAnalyzer
    
    # Initialize systems
    recommender = RiskRecommendations()
    profile_generator = RiskProfileGenerator()
    behavior_analyzer = UserBehaviorAnalyzer()
    
    # Create sample user profile
    sample_user_profile = UserProfile(
        user_id="test_user_123",
        profile_type=RiskProfileType.MODERATE,
        risk_score=65.0,
        assessment=None,  # Would be filled in real usage
        investment_goals=['balanced_growth', 'retirement_planning'],
        time_horizon=120,  # 10 years
        liquidity_need='medium_term',
        risk_capacity=70.0,
        behavioral_biases={'overconfidence': 60, 'loss_aversion': 55},
        recommendations=['Diversified portfolio'],
        last_updated=datetime.now(),
        confidence_level=0.85
    )
    
    # Sample current portfolio
    current_portfolio = {
        'cash_percentage': 5,
        'bonds_percentage': 25,
        'stocks_percentage': 60,
        'alternatives_percentage': 5,
        'commodities_percentage': 5
    }
    
    # Sample market conditions
    market_conditions = {
        'vix': 22.5,
        'volatility_regime': 'high',
        'correlation_increase': 1.2,
        'liquidity_condition': 'normal'
    }
    
    # Generate recommendations
    recommendations = recommender.generate_portfolio_recommendations(
        sample_user_profile, None, current_portfolio, market_conditions
    )
    
    # Print results
    print(f"Portfolio Recommendations for {recommendations.user_id}:")
    print(f"Current Allocation: {recommendations.current_allocation}")
    print(f"Recommended Allocation: {recommendations.recommended_allocation}")
    print(f"Number of Recommendations: {len(recommendations.recommendations)}")
    
    for rec in recommendations.recommendations:
        print(f"\nRecommendation: {rec.title}")
        print(f"Type: {rec.type.value}")
        print(f"Urgency: {rec.urgency.value}")
        print(f"Description: {rec.description}")
        print(f"Expected Impact: {rec.expected_impact}")
    
    # Run portfolio simulation
    simulation = recommender.simulate_portfolio_performance(
        recommendations.recommended_allocation, years=5, scenarios=1000
    )
    
    print(f"\n5-Year Portfolio Simulation Results:")
    print(f"Expected Annual Return: {simulation['expected_annual_return']:.2f}%")
    print(f"Probability of Positive Return: {simulation['probability_positive']:.1%}")
    print(f"Mean Max Drawdown: {simulation['max_drawdown_mean']:.1f}%")
    print(f"95th Percentile Max Drawdown: {simulation['max_drawdown_95']:.1f}%")
    
    # Export recommendations
    json_export = recommender.export_recommendations(recommendations, 'json')
    print(f"\nJSON Export (first 300 chars): {json_export[:300]}...")