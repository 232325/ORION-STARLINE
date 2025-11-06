"""
AI Agent Pool - Multiple AI agentlarni boshqarish va monitoring
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import numpy as np
import json
import os

from ai_feedback_loop import AdaptiveLearningEngine

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentType(Enum):
    """AI Agent turlari"""
    TECHNICAL_ANALYSIS = "technical_analysis"
    FUNDAMENTAL_ANALYSIS = "fundamental_analysis"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    QUANTITATIVE = "quantitative"
    OPTIONS_FLOW = "options_flow"
    RISK_MANAGEMENT = "risk_management"
    MOMENTUM = "momentum"
    VALUE = "value"

class AgentStatus(Enum):
    """Agent holatlari"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"

@dataclass
class AgentPerformance:
    """Agent performance metrikalari"""
    total_signals: int = 0
    correct_predictions: int = 0
    accuracy: float = 0.0
    avg_confidence: float = 0.0
    profit_factor: float = 1.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)
    win_rate: float = 0.0
    avg_hold_time: float = 0.0
    risk_adjusted_return: float = 0.0
    
    def update(self, signal_outcome: Dict[str, Any]):
        """Performance ni yangilash"""
        self.total_signals += 1
        
        if signal_outcome.get('profit', 0) > 0:
            self.correct_predictions += 1
            
        self.accuracy = self.correct_predictions / self.total_signals
        self.win_rate = self.accuracy
        self.last_update = datetime.now()

@dataclass
class MarketRegime:
    """Bozor rejimi ma'lumotlari"""
    regime_type: str
    volatility: float
    trend: str
    volume: float
    sentiment: float
    timestamp: datetime

class BaseAIAgent(ABC):
    """Base AI Agent class"""
    
    def __init__(self, agent_id: str, agent_type: AgentType, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.config = config
        self.status = AgentStatus.ACTIVE
        self.performance = AgentPerformance()
        self.last_signal_time = None
        self.signal_count = 0
        self.specialization = self._define_specialization()
        self.learning_engine = AdaptiveLearningEngine()
        
    @abstractmethod
    def _define_specialization(self) -> Dict[str, Any]:
        """Agent specialization ni aniqlash"""
        pass
    
    @abstractmethod
    async def generate_signal(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Signal generatsiyasi"""
        pass
    
    @abstractmethod
    def get_agent_weights(self, market_regime: MarketRegime) -> Dict[str, float]:
        """Agent og'irliklari (market regime ga asoslangan)"""
        pass
    
    def update_performance(self, signal_outcome: Dict[str, Any]):
        """Performance ni yangilash"""
        self.performance.update(signal_outcome)
        
        # Learning engine ga o'rganish uchun ma'lumot berish
        self.learning_engine.process_feedback(
            agent_id=self.agent_id,
            signal_data=signal_outcome
        )
    
    def get_current_confidence(self) -> float:
        """Joriy confidence level"""
        base_confidence = self.performance.accuracy
        
        # Vaqt factori (eski ma'lumotlar kamroq ishonchli)
        if self.last_signal_time:
            time_diff = (datetime.now() - self.last_signal_time).total_seconds() / 3600
            time_decay = max(0.1, 1.0 - (time_diff / 24))  # 24 soat ichida
        else:
            time_decay = 1.0
            
        return base_confidence * time_decay
    
    def is_healthy(self) -> bool:
        """Agent holatini tekshirish"""
        if self.status != AgentStatus.ACTIVE:
            return False
            
        # Signal tezligi tekshirish
        if self.last_signal_time:
            time_diff = (datetime.now() - self.last_signal_time).total_seconds() / 3600
            if time_diff > self.config.get('max_inactive_hours', 24):
                self.status = AgentStatus.INACTIVE
                return False
                
        return True

class TechnicalAnalysisAgent(BaseAIAgent):
    """Technical Analysis Agent"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, AgentType.TECHNICAL_ANALYSIS, config)
        
    def _define_specialization(self) -> Dict[str, Any]:
        return {
            "indicators": ["RSI", "MACD", "Bollinger Bands", "Stochastic", "Williams %R"],
            "timeframes": ["1m", "5m", "15m", "1h", "4h", "1d"],
            "patterns": ["Support/Resistance", "Trend Lines", "Chart Patterns", "Volume Analysis"],
            "market_conditions": ["trending", "ranging", "breakout", "reversal"]
        }
    
    async def generate_signal(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            # Technical analysis logic
            indicators = market_data.get('indicators', {})
            price_data = market_data.get('price_data', {})
            
            # RSI signal
            rsi = indicators.get('RSI', 50)
            if rsi < 30:
                signal_strength = 0.8
                signal_type = "BUY"
            elif rsi > 70:
                signal_strength = 0.8
                signal_type = "SELL"
            else:
                signal_strength = 0.3
                signal_type = "HOLD"
            
            # MACD confirmation
            macd = indicators.get('MACD', {})
            if macd.get('signal', 0) > 0 and signal_type == "BUY":
                signal_strength += 0.2
            elif macd.get('signal', 0) < 0 and signal_type == "SELL":
                signal_strength += 0.2
            
            signal = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "signal_type": signal_type,
                "strength": min(signal_strength, 1.0),
                "confidence": self.get_current_confidence() * signal_strength,
                "timestamp": datetime.now().isoformat(),
                "indicators_used": list(indicators.keys()),
                "reasoning": f"RSI: {rsi}, MACD: {macd.get('signal', 'N/A')}"
            }
            
            self.last_signal_time = datetime.now()
            self.signal_count += 1
            return signal
            
        except Exception as e:
            logger.error(f"Technical analysis agent {self.agent_id} error: {str(e)}")
            return None
    
    def get_agent_weights(self, market_regime: MarketRegime) -> Dict[str, float]:
        """Technical analysis weights based on market regime"""
        base_weights = {
            "trending": 0.9,
            "ranging": 0.6,
            "breakout": 0.8,
            "reversal": 0.7
        }
        
        # Volatility adjustment
        vol_multiplier = 1.0 + (market_regime.volatility * 0.1)
        
        return {
            "base": base_weights.get(market_regime.regime_type, 0.7),
            "volatility": vol_multiplier,
            "trend": 1.0 if market_regime.trend in ["bullish", "bearish"] else 0.8
        }

class FundamentalAnalysisAgent(BaseAIAgent):
    """Fundamental Analysis Agent"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, AgentType.FUNDAMENTAL_ANALYSIS, config)
        
    def _define_specialization(self) -> Dict[str, Any]:
        return {
            "metrics": ["P/E Ratio", "P/B Ratio", "ROE", "ROA", "Debt/Equity", "Revenue Growth"],
            "sectors": ["Technology", "Healthcare", "Finance", "Energy", "Consumer", "Industrial"],
            "timeframes": ["quarterly", "annual", "ttm"],
            "data_sources": ["earnings", "news", "economic_indicators", "industry_reports"]
        }
    
    async def generate_signal(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            fundamentals = market_data.get('fundamentals', {})
            earnings = market_data.get('earnings', {})
            news = market_data.get('news', [])
            
            # P/E Ratio analysis
            pe_ratio = fundamentals.get('pe_ratio', 15)
            if pe_ratio < 12:
                fundamental_score = 0.8
            elif pe_ratio > 25:
                fundamental_score = 0.3
            else:
                fundamental_score = 0.6
            
            # Earnings surprise
            surprise = earnings.get('eps_surprise_percent', 0)
            if surprise > 5:
                fundamental_score += 0.2
            elif surprise < -5:
                fundamental_score -= 0.2
            
            # News sentiment
            news_sentiment = np.mean([article.get('sentiment', 0) for article in news[:5]])
            fundamental_score += (news_sentiment * 0.1)
            
            signal_type = "BUY" if fundamental_score > 0.7 else "SELL" if fundamental_score < 0.4 else "HOLD"
            
            signal = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "signal_type": signal_type,
                "strength": abs(fundamental_score - 0.5) * 2,
                "confidence": self.get_current_confidence() * min(fundamental_score, 1.0),
                "timestamp": datetime.now().isoformat(),
                "metrics_used": ["pe_ratio", "eps_surprise", "news_sentiment"],
                "reasoning": f"P/E: {pe_ratio}, EPS Surprise: {surprise}%, News Sent: {news_sentiment:.2f}"
            }
            
            self.last_signal_time = datetime.now()
            self.signal_count += 1
            return signal
            
        except Exception as e:
            logger.error(f"Fundamental analysis agent {self.agent_id} error: {str(e)}")
            return None
    
    def get_agent_weights(self, market_regime: MarketRegime) -> Dict[str, float]:
        return {
            "base": 0.8,  # High weight for fundamentals
            "earnings_season": 1.2,
            "news_sensitivity": 1.0 + (market_regime.sentiment * 0.1)
        }

class SentimentAnalysisAgent(BaseAIAgent):
    """Sentiment Analysis Agent"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, AgentType.SENTIMENT_ANALYSIS, config)
        
    def _define_specialization(self) -> Dict[str, Any]:
        return {
            "sources": ["social_media", "news", "earnings_calls", "analyst_reports"],
            "sentiment_types": ["fear_greed", "bullish_bearish", "optimism_pessimism"],
            "timeframes": ["real_time", "daily", "weekly", "monthly"],
            "indicators": ["VIX", "put_call_ratio", "insider_trading", "short_interest"]
        }
    
    async def generate_signal(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            sentiment_data = market_data.get('sentiment', {})
            social_data = market_data.get('social_media', {})
            news_sentiment = market_data.get('news_sentiment', 0)
            
            # VIX levels
            vix = market_data.get('vix', 20)
            if vix > 30:
                fear_factor = 0.8
            elif vix < 15:
                fear_factor = 0.2
            else:
                fear_factor = 0.5
            
            # Social media sentiment
            social_sentiment = social_data.get('overall_sentiment', 0)
            
            # News sentiment integration
            combined_sentiment = (fear_factor + social_sentiment + news_sentiment) / 3
            
            signal_type = "BUY" if combined_sentiment > 0.6 else "SELL" if combined_sentiment < 0.4 else "HOLD"
            
            signal = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "signal_type": signal_type,
                "strength": abs(combined_sentiment - 0.5) * 2,
                "confidence": self.get_current_confidence() * (1.0 - abs(combined_sentiment - 0.5)),
                "timestamp": datetime.now().isoformat(),
                "sentiment_score": combined_sentiment,
                "reasoning": f"VIX: {vix}, Social: {social_sentiment:.2f}, News: {news_sentiment:.2f}"
            }
            
            self.last_signal_time = datetime.now()
            self.signal_count += 1
            return signal
            
        except Exception as e:
            logger.error(f"Sentiment analysis agent {self.agent_id} error: {str(e)}")
            return None
    
    def get_agent_weights(self, market_regime: MarketRegime) -> Dict[str, float]:
        return {
            "base": 0.7,
            "high_volatility": 1.3,  # Sentiment matters more in volatile markets
            "news_drive": 1.1
        }

class QuantitativeAgent(BaseAIAgent):
    """Quantitative Analysis Agent"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, AgentType.QUANTITATIVE, config)
        
    def _define_specialization(self) -> Dict[str, Any]:
        return {
            "models": ["mean_reversion", "momentum", "pairs_trading", "statistical_arbitrage"],
            "timeframes": ["intraday", "daily", "weekly", "monthly"],
            "indicators": ["correlation", "cointegration", "volatility_clustering", " regime_detection"],
            "risk_metrics": ["var", "cvar", "drawdown", "sharpe_ratio"]
        }
    
    async def generate_signal(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            price_data = market_data.get('price_data', {})
            volume_data = market_data.get('volume_data', {})
            
            # Simple momentum calculation
            returns = np.diff(price_data.get('close', [])) if len(price_data.get('close', [])) > 1 else [0]
            momentum = np.mean(returns[-5:]) if len(returns) >= 5 else returns[-1] if returns else 0
            
            # Volatility-based signal
            volatility = np.std(returns) if len(returns) > 1 else 0.02
            volatility_adjusted_signal = momentum / volatility if volatility > 0 else 0
            
            # Signal strength based on statistical significance
            if abs(volatility_adjusted_signal) > 1.5:
                signal_strength = 0.8
            elif abs(volatility_adjusted_signal) > 1.0:
                signal_strength = 0.6
            else:
                signal_strength = 0.3
            
            signal_type = "BUY" if volatility_adjusted_signal > 0.5 else "SELL" if volatility_adjusted_signal < -0.5 else "HOLD"
            
            signal = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "signal_type": signal_type,
                "strength": signal_strength,
                "confidence": self.get_current_confidence() * signal_strength,
                "timestamp": datetime.now().isoformat(),
                "volatility_adjusted_signal": volatility_adjusted_signal,
                "reasoning": f"Momentum: {momentum:.4f}, Volatility: {volatility:.4f}, Z-score: {volatility_adjusted_signal:.2f}"
            }
            
            self.last_signal_time = datetime.now()
            self.signal_count += 1
            return signal
            
        except Exception as e:
            logger.error(f"Quantitative agent {self.agent_id} error: {str(e)}")
            return None
    
    def get_agent_weights(self, market_regime: MarketRegime) -> Dict[str, float]:
        return {
            "base": 0.75,
            "mean_reversion": 1.2 if market_regime.regime_type == "ranging" else 0.8,
            "momentum": 1.2 if market_regime.regime_type == "trending" else 0.8
        }

class OptionsFlowAgent(BaseAIAgent):
    """Options Flow Analysis Agent"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, AgentType.OPTIONS_FLOW, config)
        
    def _define_specialization(self) -> Dict[str, Any]:
        return {
            "indicators": ["put_call_ratio", "open_interest", "volume_spike", "unusual_options"],
            "strategies": ["covered_calls", "protective_puts", "spreads", "synthetic_positions"],
            "timeframes": ["daily", "weekly", "monthly"],
            "market_data": ["whale_activity", "insider_trading", "dark_pool", "sweeps"]
        }
    
    async def generate_signal(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            options_data = market_data.get('options', {})
            put_call_ratio = options_data.get('put_call_ratio', 1.0)
            unusual_activity = options_data.get('unusual_activity', False)
            whale_activity = options_data.get('whale_activity', False)
            
            # Put/Call ratio analysis
            if put_call_ratio > 1.2:
                ratio_signal = 0.7  # Bearish
            elif put_call_ratio < 0.8:
                ratio_signal = 0.3  # Bullish
            else:
                ratio_signal = 0.5  # Neutral
            
            # Unusual activity boost
            if unusual_activity:
                ratio_signal += 0.2
            if whale_activity:
                ratio_signal += 0.1
            
            signal_type = "BUY" if ratio_signal < 0.4 else "SELL" if ratio_signal > 0.6 else "HOLD"
            
            signal = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "signal_type": signal_type,
                "strength": abs(ratio_signal - 0.5) * 2,
                "confidence": self.get_current_confidence() * (1.0 - abs(ratio_signal - 0.5)),
                "timestamp": datetime.now().isoformat(),
                "put_call_ratio": put_call_ratio,
                "unusual_activity": unusual_activity,
                "whale_activity": whale_activity,
                "reasoning": f"P/C Ratio: {put_call_ratio}, Unusual: {unusual_activity}, Whale: {whale_activity}"
            }
            
            self.last_signal_time = datetime.now()
            self.signal_count += 1
            return signal
            
        except Exception as e:
            logger.error(f"Options flow agent {self.agent_id} error: {str(e)}")
            return None
    
    def get_agent_weights(self, market_regime: MarketRegime) -> Dict[str, float]:
        return {
            "base": 0.6,
            "high_volatility": 1.4,  # Options data more valuable in volatile markets
            "earnings_season": 1.2
        }

class RiskManagementAgent(BaseAIAgent):
    """Risk Management Agent"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, AgentType.RISK_MANAGEMENT, config)
        
    def _define_specialization(self) -> Dict[str, Any]:
        return {
            "risk_metrics": ["var", "cvar", "max_drawdown", "concentration", "correlation"],
            "position_sizing": ["kelly_criterion", "equal_weight", "risk_parity", "volatility_targeting"],
            "hedging": ["stops", "trailing_stops", "options_hedging", "portfolio_hedging"],
            "monitoring": ["real_time_risk", "scenario_analysis", "stress_testing", "risk_attribution"]
        }
    
    async def generate_signal(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            portfolio_data = market_data.get('portfolio', {})
            risk_metrics = portfolio_data.get('risk_metrics', {})
            
            var_95 = risk_metrics.get('var_95', 0.05)
            max_drawdown = risk_metrics.get('max_drawdown', 0.1)
            concentration_risk = risk_metrics.get('concentration', 0.3)
            
            # Risk assessment
            risk_score = 0
            if var_95 > 0.08:  # High VaR
                risk_score += 0.3
            if max_drawdown > 0.15:  # High drawdown
                risk_score += 0.3
            if concentration_risk > 0.4:  # High concentration
                risk_score += 0.2
            
            # Risk management signal
            if risk_score > 0.6:
                signal_type = "REDUCE_RISK"
                signal_strength = risk_score
            elif risk_score < 0.3:
                signal_type = "INCREASE_RISK"
                signal_strength = 1.0 - risk_score
            else:
                signal_type = "MAINTAIN_RISK"
                signal_strength = 0.5
            
            signal = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "signal_type": signal_type,
                "strength": signal_strength,
                "confidence": self.get_current_confidence() * signal_strength,
                "timestamp": datetime.now().isoformat(),
                "risk_score": risk_score,
                "var_95": var_95,
                "max_drawdown": max_drawdown,
                "reasoning": f"VaR: {var_95:.3f}, MDD: {max_drawdown:.3f}, Concentration: {concentration_risk:.2f}"
            }
            
            self.last_signal_time = datetime.now()
            self.signal_count += 1
            return signal
            
        except Exception as e:
            logger.error(f"Risk management agent {self.agent_id} error: {str(e)}")
            return None
    
    def get_agent_weights(self, market_regime: MarketRegime) -> Dict[str, float]:
        return {
            "base": 0.9,  # Always important
            "high_volatility": 1.5,  # Critical in volatile markets
            "crisis_mode": 2.0  # Override others in crisis
        }

class MomentumAgent(BaseMomentumAgent):  # Intentional error for testing
    pass

class ValueAgent(BaseAIAgent):
    """Value Analysis Agent"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, AgentType.VALUE, config)
        
    def _define_specialization(self) -> Dict[str, Any]:
        return {
            "metrics": ["dcf", "comparable_analysis", "asset_valuation", "earnings_power"],
            "discount_rates": ["wacc", "capm", "multi_factor", "bond_yield_plus"],
            "growth_assumptions": ["earnings_growth", "revenue_growth", "free_cash_flow"],
            "quality_factors": ["roe", "roic", "profit_margins", "debt_levels"]
        }
    
    async def generate_signal(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            valuation_data = market_data.get('valuation', {})
            fundamentals = market_data.get('fundamentals', {})
            
            # DCF-based valuation
            dcf_value = valuation_data.get('dcf_estimate', 0)
            current_price = market_data.get('current_price', 0)
            margin_of_safety = (dcf_value - current_price) / dcf_value if dcf_value > 0 else 0
            
            # Price to intrinsic value ratio
            if current_price > 0 and dcf_value > 0:
                p_to_dcf = current_price / dcf_value
            else:
                p_to_dcf = 1.0
            
            # Value signal strength
            if margin_of_safety > 0.2:  # 20% margin of safety
                signal_strength = 0.8
                signal_type = "BUY"
            elif margin_of_safety < -0.2:  # Overvalued
                signal_strength = 0.8
                signal_type = "SELL"
            else:
                signal_strength = 0.4
                signal_type = "HOLD"
            
            signal = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "signal_type": signal_type,
                "strength": signal_strength,
                "confidence": self.get_current_confidence() * signal_strength,
                "timestamp": datetime.now().isoformat(),
                "dcf_value": dcf_value,
                "current_price": current_price,
                "margin_of_safety": margin_of_safety,
                "reasoning": f"DCF: ${dcf_value:.2f}, Price: ${current_price:.2f}, MOS: {margin_of_safety:.1%}"
            }
            
            self.last_signal_time = datetime.now()
            self.signal_count += 1
            return signal
            
        except Exception as e:
            logger.error(f"Value agent {self.agent_id} error: {str(e)}")
            return None
    
    def get_agent_weights(self, market_regime: MarketRegime) -> Dict[str, float]:
        return {
            "base": 0.8,
            "bear_market": 1.3,  # Value outperforms in bear markets
            "growth_market": 0.9
        }

# Missing MomentumAgent class definition
class MomentumAgent(BaseAIAgent):
    """Momentum Analysis Agent"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, AgentType.MOMENTUM, config)
        
    def _define_specialization(self) -> Dict[str, Any]:
        return {
            "indicators": ["price_momentum", "volume_momentum", "earnings_momentum", "sector_momentum"],
            "timeframes": ["short_term", "medium_term", "long_term"],
            "strengths": ["breakout", "trend_continuation", "acceleration", "sector_rotation"],
            "weaknesses": ["overbought", "momentum_stall", "reversal_signs", "distribution"]
        }
    
    async def generate_signal(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            price_data = market_data.get('price_data', {})
            volume_data = market_data.get('volume_data', {})
            
            # Price momentum
            returns = np.diff(price_data.get('close', [])) if len(price_data.get('close', [])) > 1 else [0]
            if len(returns) >= 20:
                short_momentum = np.mean(returns[-5:])  # 5-day momentum
                long_momentum = np.mean(returns[-20:])  # 20-day momentum
                momentum_diff = short_momentum - long_momentum
            else:
                momentum_diff = returns[-1] if returns else 0
            
            # Volume confirmation
            volume_trend = volume_data.get('trend', 'neutral')
            volume_multiplier = 1.2 if volume_trend == 'increasing' else 1.0
            
            # Signal strength
            if abs(momentum_diff) > 0.03:  # 3% momentum threshold
                signal_strength = 0.8
            elif abs(momentum_diff) > 0.01:  # 1% momentum threshold
                signal_strength = 0.6
            else:
                signal_strength = 0.3
            
            signal_type = "BUY" if momentum_diff > 0.01 else "SELL" if momentum_diff < -0.01 else "HOLD"
            
            signal = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "signal_type": signal_type,
                "strength": signal_strength * volume_multiplier,
                "confidence": self.get_current_confidence() * signal_strength,
                "timestamp": datetime.now().isoformat(),
                "momentum_diff": momentum_diff,
                "volume_trend": volume_trend,
                "reasoning": f"Momentum diff: {momentum_diff:.4f}, Volume: {volume_trend}"
            }
            
            self.last_signal_time = datetime.now()
            self.signal_count += 1
            return signal
            
        except Exception as e:
            logger.error(f"Momentum agent {self.agent_id} error: {str(e)}")
            return None
    
    def get_agent_weights(self, market_regime: MarketRegime) -> Dict[str, float]:
        return {
            "base": 0.7,
            "trending_market": 1.3,  # Stronger in trending markets
            "bull_market": 1.2
        }

class AgentPool:
    """AI Agent Pool Manager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents: Dict[str, BaseAIAgent] = {}
        self.agent_types = {
            AgentType.TECHNICAL_ANALYSIS: TechnicalAnalysisAgent,
            AgentType.FUNDAMENTAL_ANALYSIS: FundamentalAnalysisAgent,
            AgentType.SENTIMENT_ANALYSIS: SentimentAnalysisAgent,
            AgentType.QUANTITATIVE: QuantitativeAgent,
            AgentType.OPTIONS_FLOW: OptionsFlowAgent,
            AgentType.RISK_MANAGEMENT: RiskManagementAgent,
            AgentType.MOMENTUM: MomentumAgent,
            AgentType.VALUE: ValueAgent
        }
        self.performance_history: List[Dict[str, Any]] = []
        
    def add_agent(self, agent_type: AgentType, agent_id: str, config: Dict[str, Any]) -> bool:
        """Agent qo'shish"""
        try:
            if agent_id in self.agents:
                logger.warning(f"Agent {agent_id} already exists")
                return False
            
            agent_class = self.agent_types.get(agent_type)
            if not agent_class:
                logger.error(f"Unknown agent type: {agent_type}")
                return False
            
            agent = agent_class(agent_id, config)
            self.agents[agent_id] = agent
            
            logger.info(f"Added agent {agent_id} of type {agent_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding agent {agent_id}: {str(e)}")
            return False
    
    def remove_agent(self, agent_id: str) -> bool:
        """Agent olib tashlash"""
        try:
            if agent_id in self.agents:
                del self.agents[agent_id]
                logger.info(f"Removed agent {agent_id}")
                return True
            else:
                logger.warning(f"Agent {agent_id} not found")
                return False
        except Exception as e:
            logger.error(f"Error removing agent {agent_id}: {str(e)}")
            return False
    
    async def collect_signals(self, market_data: Dict[str, Any], market_regime: MarketRegime) -> List[Dict[str, Any]]:
        """Barcha agentlardan signal to'plash"""
        signals = []
        
        # Parallel signal collection
        tasks = []
        for agent in self.agents.values():
            if agent.is_healthy():
                tasks.append(agent.generate_signal(market_data))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            agent = list(self.agents.values())[i]
            if isinstance(result, Exception):
                logger.error(f"Agent {agent.agent_id} signal error: {str(result)}")
                continue
            elif result:
                # Agent weight ni qo'shish
                weights = agent.get_agent_weights(market_regime)
                result['weights'] = weights
                signals.append(result)
        
        return signals
    
    def get_agent_performance(self, agent_id: str) -> Optional[AgentPerformance]:
        """Agent performance ma'lumotlari"""
        agent = self.agents.get(agent_id)
        return agent.performance if agent else None
    
    def get_all_agent_performances(self) -> Dict[str, AgentPerformance]:
        """Barcha agentlarning performance ma'lumotlari"""
        return {agent_id: agent.performance for agent_id, agent in self.agents.items()}
    
    def update_agent_performance(self, agent_id: str, signal_outcome: Dict[str, Any]):
        """Agent performance ni yangilash"""
        agent = self.agents.get(agent_id)
        if agent:
            agent.update_performance(signal_outcome)
    
    def get_active_agents(self) -> List[str]:
        """Faol agentlarning ro'yxati"""
        return [agent_id for agent_id, agent in self.agents.items() if agent.is_healthy()]
    
    def get_agents_by_type(self, agent_type: AgentType) -> List[str]:
        """Agent type bo'yicha filtrlash"""
        return [agent_id for agent_id, agent in self.agents.items() if agent.agent_type == agent_type]
    
    def get_pool_statistics(self) -> Dict[str, Any]:
        """Pool statistikasi"""
        active_agents = [agent for agent in self.agents.values() if agent.is_healthy()]
        
        total_signals = sum(agent.performance.total_signals for agent in active_agents)
        avg_accuracy = np.mean([agent.performance.accuracy for agent in active_agents]) if active_agents else 0
        avg_confidence = np.mean([agent.get_current_confidence() for agent in active_agents]) if active_agents else 0
        
        return {
            "total_agents": len(self.agents),
            "active_agents": len(active_agents),
            "inactive_agents": len(self.agents) - len(active_agents),
            "total_signals": total_signals,
            "avg_accuracy": avg_accuracy,
            "avg_confidence": avg_confidence,
            "agent_types": {agent_type.value: len(self.get_agents_by_type(agent_type)) for agent_type in AgentType}
        }
    
    def save_pool_state(self, filepath: str):
        """Pool holatini saqlash"""
        try:
            state = {
                "agents": {
                    agent_id: {
                        "agent_id": agent.agent_id,
                        "agent_type": agent.agent_type.value,
                        "config": agent.config,
                        "performance": {
                            "total_signals": agent.performance.total_signals,
                            "correct_predictions": agent.performance.correct_predictions,
                            "accuracy": agent.performance.accuracy,
                            "win_rate": agent.performance.win_rate,
                            "sharpe_ratio": agent.performance.sharpe_ratio,
                            "last_update": agent.performance.last_update.isoformat()
                        }
                    }
                    for agent_id, agent in self.agents.items()
                },
                "config": self.config,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.info(f"Pool state saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving pool state: {str(e)}")
    
    def load_pool_state(self, filepath: str) -> bool:
        """Pool holatini yuklash"""
        try:
            if not os.path.exists(filepath):
                logger.warning(f"Pool state file {filepath} not found")
                return False
            
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            # Agents qayta yaratish
            self.agents.clear()
            for agent_id, agent_data in state.get("agents", {}).items():
                agent_type = AgentType(agent_data["agent_type"])
                if agent_type in self.agent_types:
                    self.add_agent(agent_type, agent_id, agent_data["config"])
                    
                    # Performance ni tiklash
                    if agent_id in self.agents:
                        perf_data = agent_data.get("performance", {})
                        self.agents[agent_id].performance.total_signals = perf_data.get("total_signals", 0)
                        self.agents[agent_id].performance.correct_predictions = perf_data.get("correct_predictions", 0)
                        self.agents[agent_id].performance.accuracy = perf_data.get("accuracy", 0.0)
                        self.agents[agent_id].performance.win_rate = perf_data.get("win_rate", 0.0)
                        self.agents[agent_id].performance.sharpe_ratio = perf_data.get("sharpe_ratio", 0.0)
                        
                        if "last_update" in perf_data:
                            self.agents[agent_id].performance.last_update = datetime.fromisoformat(perf_data["last_update"])
            
            logger.info(f"Pool state loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading pool state: {str(e)}")
            return False

# Test va demo funksiyalari
async def demo_agent_pool():
    """Agent pool demo"""
    config = {
        "max_agents_per_type": 3,
        "performance_window": 100,
        "adaptive_learning": True
    }
    
    pool = AgentPool(config)
    
    # Agentlar qo'shish
    agent_configs = {
        "tech_1": {"timeframes": ["1h", "4h"], "indicators": ["RSI", "MACD"]},
        "fundamental_1": {"sectors": ["tech", "healthcare"], "metrics": ["pe_ratio", "roe"]},
        "sentiment_1": {"sources": ["twitter", "news"], "indicators": ["vix", "fear_greed"]},
        "quant_1": {"models": ["momentum", "mean_reversion"], "timeframes": ["daily"]},
        "options_1": {"strategies": ["covered_calls"], "data_sources": ["unusual_options"]},
        "risk_1": {"metrics": ["var", "cvar"], "hedging": True},
        "momentum_1": {"timeframes": ["short_term", "medium_term"], "indicators": ["price_momentum"]},
        "value_1": {"methods": ["dcf", "comps"], "growth_rate": 0.05}
    }
    
    for agent_id, agent_config in agent_configs.items():
        if "tech" in agent_id:
            pool.add_agent(AgentType.TECHNICAL_ANALYSIS, agent_id, agent_config)
        elif "fundamental" in agent_id:
            pool.add_agent(AgentType.FUNDAMENTAL_ANALYSIS, agent_id, agent_config)
        elif "sentiment" in agent_id:
            pool.add_agent(AgentType.SENTIMENT_ANALYSIS, agent_id, agent_config)
        elif "quant" in agent_id:
            pool.add_agent(AgentType.QUANTITATIVE, agent_id, agent_config)
        elif "options" in agent_id:
            pool.add_agent(AgentType.OPTIONS_FLOW, agent_id, agent_config)
        elif "risk" in agent_id:
            pool.add_agent(AgentType.RISK_MANAGEMENT, agent_id, agent_config)
        elif "momentum" in agent_id:
            pool.add_agent(AgentType.MOMENTUM, agent_id, agent_config)
        elif "value" in agent_id:
            pool.add_agent(AgentType.VALUE, agent_id, agent_config)
    
    # Market data mock
    market_data = {
        "price_data": {
            "close": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120]
        },
        "indicators": {
            "RSI": 65,
            "MACD": {"signal": 0.5, "histogram": 0.3}
        },
        "fundamentals": {
            "pe_ratio": 18.5,
            "roe": 0.15
        },
        "sentiment": {
            "fear_greed": 60,
            "vix": 22.5
        },
        "volume_data": {
            "trend": "increasing"
        }
    }
    
    market_regime = MarketRegime(
        regime_type="trending",
        volatility=0.25,
        trend="bullish",
        volume=1.2,
        sentiment=0.7,
        timestamp=datetime.now()
    )
    
    # Signal collection demo
    signals = await pool.collect_signals(market_data, market_regime)
    
    print(f"\n=== Agent Pool Demo ===")
    print(f"Total agents: {len(pool.agents)}")
    print(f"Active agents: {len(pool.get_active_agents())}")
    print(f"Collected signals: {len(signals)}")
    
    for signal in signals:
        print(f"\nAgent: {signal['agent_id']} ({signal['agent_type']})")
        print(f"Signal: {signal['signal_type']} (Strength: {signal['strength']:.2f})")
        print(f"Confidence: {signal['confidence']:.2f}")
        print(f"Reasoning: {signal['reasoning']}")
    
    # Pool statistics
    stats = pool.get_pool_statistics()
    print(f"\n=== Pool Statistics ===")
    print(json.dumps(stats, indent=2, default=str))
    
    return pool, signals

if __name__ == "__main__":
    # Demo run
    asyncio.run(demo_agent_pool())