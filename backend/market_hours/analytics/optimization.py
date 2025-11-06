"""
Market Hours Analytics
Market timing optimization uchun analytics va optimization
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

class OptimizationStrategy(Enum):
    MAX_VOLATILITY = "max_volatility"
    MIN_RISK = "min_risk"
    BALANCED = "balanced"
    NEWS_AWARE = "news_aware"
    SESSION_FOCUS = "session_focus"

@dataclass
class TimingOptimization:
    """Timing optimization natijasi"""
    strategy: OptimizationStrategy
    optimal_times: List[Dict[str, str]]
    expected_performance: Dict[str, float]
    risk_metrics: Dict[str, float]
    market_conditions: Dict[str, any]
    confidence_score: float

@dataclass
class SessionOverlapAnalysis:
    """Session overlap tahlili"""
    overlap_type: str
    start_time: str
    end_time: str
    volatility_multiplier: float
    liquidity_score: float
    best_strategies: List[str]
    risk_factors: List[str]
    optimal_instruments: List[str]

class MarketHoursAnalytics:
    """Market hours analytics va optimization"""
    
    def __init__(self):
        # Historical performance patterns (mock data)
        self.performance_patterns = {
            "forex_sessions": {
                "asian": {
                    "avg_volatility": 0.8,
                    "success_rate": 0.65,
                    "avg_spread": 1.2,
                    "optimal_strategies": ["range_trading", "mean_reversion"]
                },
                "european": {
                    "avg_volatility": 1.6,
                    "success_rate": 0.72,
                    "avg_spread": 1.1,
                    "optimal_strategies": ["trend_following", "breakout"]
                },
                "american": {
                    "avg_volatility": 1.4,
                    "success_rate": 0.70,
                    "avg_spread": 1.3,
                    "optimal_strategies": ["momentum", "news_trading"]
                }
            },
            "overlaps": {
                "european_american": {
                    "volatility_multiplier": 2.2,
                    "liquidity_score": 9.5,
                    "success_rate": 0.78,
                    "best_strategies": ["scalping", "high_frequency"]
                }
            },
            "metal_markets": {
                "lme": {
                    "ring_trading": {
                        "volatility": 1.8,
                        "liquidity": 8.5,
                        "optimal_metals": ["copper", "aluminum", "zinc"]
                    }
                },
                "comex": {
                    "regular_hours": {
                        "volatility": 1.6,
                        "liquidity": 9.0,
                        "optimal_metals": ["gold", "silver"]
                    }
                }
            }
        }
        
        # Risk models
        self.risk_models = {
            "session_risk": {
                "asian": 0.3,
                "european": 0.6,
                "american": 0.7,
                "overlap": 0.8
            },
            "news_risk": {
                "low": 0.2,
                "medium": 0.4,
                "high": 0.7,
                "very_high": 0.9
            },
            "volatility_risk": {
                "very_low": 0.1,
                "low": 0.2,
                "normal": 0.4,
                "high": 0.7,
                "very_high": 0.9
            }
        }
        
        # Correlation patterns
        self.correlation_patterns = {
            "session_correlations": {
                "asian_european": 0.3,
                "european_american": 0.7,
                "asian_american": 0.2
            },
            "metal_correlations": {
                "gold_silver": 0.8,
                "copper_aluminum": 0.6,
                "precious_industrial": 0.4
            }
        }
    
    def optimize_trading_schedule(self, strategy_type: str, risk_tolerance: float = 0.5, 
                                market_preference: str = "forex") -> TimingOptimization:
        """Trading schedule optimization"""
        
        strategy_enum = OptimizationStrategy(strategy_type.lower().replace(" ", "_"))
        
        # Optimal times hisoblash
        optimal_times = self._calculate_optimal_times(strategy_enum, risk_tolerance, market_preference)
        
        # Expected performance
        expected_performance = self._calculate_expected_performance(strategy_enum, market_preference)
        
        # Risk metrics
        risk_metrics = self._calculate_risk_metrics(strategy_enum, risk_tolerance)
        
        # Market conditions
        market_conditions = self._get_current_market_conditions()
        
        # Confidence score
        confidence_score = self._calculate_confidence_score(strategy_enum, market_preference)
        
        return TimingOptimization(
            strategy=strategy_enum,
            optimal_times=optimal_times,
            expected_performance=expected_performance,
            risk_metrics=risk_metrics,
            market_conditions=market_conditions,
            confidence_score=confidence_score
        )
    
    def _calculate_optimal_times(self, strategy: OptimizationStrategy, risk_tolerance: float, 
                               market_preference: str) -> List[Dict[str, str]]:
        """Optimal trading times hisoblash"""
        
        times = []
        
        if strategy == OptimizationStrategy.MAX_VOLATILITY:
            # Maximum volatility ga yo'naltirilgan
            if market_preference == "forex":
                times.extend([
                    {"time": "08:00-10:00 GMT", "reason": "European open - highest volatility", "score": 9.5},
                    {"time": "13:00-15:00 GMT", "reason": "European-American overlap", "score": 9.8},
                    {"time": "16:00-18:00 GMT", "reason": "American session peak", "score": 8.7}
                ])
            elif market_preference == "metals":
                times.extend([
                    {"time": "07:30-09:00 GMT", "reason": "LME morning ring", "score": 9.0},
                    {"time": "12:00-14:00 GMT", "reason": "LME afternoon ring", "score": 9.2},
                    {"time": "08:30-11:00 GMT", "reason": "COMEX regular hours", "score": 8.5}
                ])
        
        elif strategy == OptimizationStrategy.MIN_RISK:
            # Minimum risk
            if market_preference == "forex":
                times.extend([
                    {"time": "02:00-06:00 GMT", "reason": "Quiet Asian session", "score": 8.0},
                    {"time": "10:00-12:00 GMT", "reason": "Mid-European session", "score": 7.5},
                    {"time": "19:00-21:00 GMT", "reason": "Late American session", "score": 7.0}
                ])
            elif market_preference == "metals":
                times.extend([
                    {"time": "11:00-12:00 GMT", "reason": "LME lunch break", "score": 9.0},
                    {"time": "16:00-19:00 GMT", "reason": "LME Select electronic", "score": 8.5},
                    {"time": "17:30-18:00 GMT", "reason": "COMEX maintenance", "score": 8.0}
                ])
        
        elif strategy == OptimizationStrategy.BALANCED:
            # Balanced approach
            if market_preference == "forex":
                times.extend([
                    {"time": "09:00-11:00 GMT", "reason": "Active European session", "score": 8.5},
                    {"time": "14:00-16:00 GMT", "reason": "Stable overlap period", "score": 8.8},
                    {"time": "17:00-19:00 GMT", "reason": "American active hours", "score": 8.2}
                ])
        
        elif strategy == OptimizationStrategy.NEWS_AWARE:
            # News-aware timing
            times.extend([
                {"time": "30min_before_news", "reason": "Pre-positioning before news", "score": 9.0},
                {"time": "5min_after_news", "reason": "Immediate reaction window", "score": 8.5},
                {"time": "1-3hours_after_news", "reason": "Post-news trend continuation", "score": 8.0}
            ])
        
        elif strategy == OptimizationStrategy.SESSION_FOCUS:
            # Session-specific focus
            if market_preference == "forex":
                times.extend([
                    {"time": "Asian_session", "reason": "Range-bound opportunities", "score": 7.5},
                    {"time": "European_session", "reason": "Trend formation period", "score": 8.5},
                    {"time": "American_session", "reason": "News-driven moves", "score": 8.0}
                ])
        
        return sorted(times, key=lambda x: x["score"], reverse=True)
    
    def _calculate_expected_performance(self, strategy: OptimizationStrategy, market_preference: str) -> Dict[str, float]:
        """Expected performance hisoblash"""
        
        base_performance = {
            "success_rate": 0.65,
            "avg_return": 0.02,  # 2%
            "sharpe_ratio": 1.2,
            "max_drawdown": 0.08,  # 8%
            "profit_factor": 1.4
        }
        
        # Strategy ga qarab adjustment
        if strategy == OptimizationStrategy.MAX_VOLATILITY:
            base_performance.update({
                "success_rate": 0.68,
                "avg_return": 0.035,
                "sharpe_ratio": 1.5,
                "max_drawdown": 0.12,
                "profit_factor": 1.6
            })
        elif strategy == OptimizationStrategy.MIN_RISK:
            base_performance.update({
                "success_rate": 0.72,
                "avg_return": 0.015,
                "sharpe_ratio": 1.8,
                "max_drawdown": 0.05,
                "profit_factor": 1.8
            })
        elif strategy == OptimizationStrategy.BALANCED:
            base_performance.update({
                "success_rate": 0.70,
                "avg_return": 0.025,
                "sharpe_ratio": 1.6,
                "max_drawdown": 0.08,
                "profit_factor": 1.6
            })
        
        return base_performance
    
    def _calculate_risk_metrics(self, strategy: OptimizationStrategy, risk_tolerance: float) -> Dict[str, float]:
        """Risk metrics hisoblash"""
        
        base_risk = {
            "volatility_risk": risk_tolerance * 0.5,
            "timing_risk": 0.3,
            "liquidity_risk": 0.2,
            "news_risk": 0.4,
            "correlation_risk": 0.3
        }
        
        # Strategy ga qarab risk adjustment
        if strategy == OptimizationStrategy.MAX_VOLATILITY:
            base_risk.update({
                "volatility_risk": risk_tolerance * 0.8,
                "timing_risk": 0.4,
                "liquidity_risk": 0.1
            })
        elif strategy == OptimizationStrategy.MIN_RISK:
            base_risk.update({
                "volatility_risk": risk_tolerance * 0.2,
                "timing_risk": 0.2,
                "liquidity_risk": 0.4
            })
        
        return base_risk
    
    def _get_current_market_conditions(self) -> Dict[str, any]:
        """Current market conditions (mock data)"""
        
        return {
            "overall_market_sentiment": "neutral",
            "volatility_environment": "moderate",
            "liquidity_conditions": "adequate",
            "news_impact": "low_to_medium",
            "correlation_environment": "normal",
            "session_activity": "european_focus"
        }
    
    def _calculate_confidence_score(self, strategy: OptimizationStrategy, market_preference: str) -> float:
        """Confidence score hisoblash"""
        
        base_confidence = 0.7
        
        # Strategy effectiveness
        if strategy in [OptimizationStrategy.MIN_RISK, OptimizationStrategy.BALANCED]:
            confidence = 0.8
        elif strategy == OptimizationStrategy.MAX_VOLATILITY:
            confidence = 0.6
        else:
            confidence = 0.75
        
        return min(confidence, 1.0)
    
    def analyze_session_overlaps(self) -> List[SessionOverlapAnalysis]:
        """Session overlap tahlili"""
        
        overlaps = []
        
        # European-American overlap
        overlap = SessionOverlapAnalysis(
            overlap_type="european_american",
            start_time="13:00 GMT",
            end_time="17:00 GMT",
            volatility_multiplier=2.2,
            liquidity_score=9.5,
            best_strategies=["scalping", "high_frequency", "arbitrage"],
            risk_factors=["high_volatility", "news_sensitivity", "overlapping_positions"],
            optimal_instruments=["EUR/USD", "GBP/USD", "USD/JPY", "EUR/GBP"]
        )
        overlaps.append(overlap)
        
        # European-Asian overlap
        overlap = SessionOverlapAnalysis(
            overlap_type="european_asian",
            start_time="08:00 GMT",
            end_time="09:00 GMT", 
            volatility_multiplier=1.4,
            liquidity_score=7.5,
            best_strategies=["transition_trading", "early_positioning"],
            risk_factors=["low_liquidity", "gap_risk"],
            optimal_instruments=["EUR/JPY", "GBP/JPY", "AUD/USD"]
        )
        overlaps.append(overlap)
        
        return overlaps
    
    def calculate_market_efficiency_metrics(self, current_time: datetime) -> Dict[str, float]:
        """Market efficiency metrics hisoblash"""
        
        # Mock efficiency metrics
        metrics = {
            "price_discovery_efficiency": 0.75,
            "liquidity_efficiency": 0.82,
            "information_integration": 0.68,
            "volatility_prediction_accuracy": 0.71,
            "session_transition_efficiency": 0.79,
            "news_impact_anticipation": 0.65
        }
        
        # Time of day adjustments
        current_hour = current_time.hour
        
        if 8 <= current_hour <= 17:  # European hours
            metrics.update({
                "price_discovery_efficiency": 0.85,
                "liquidity_efficiency": 0.90
            })
        elif 13 <= current_hour <= 22:  # American hours
            metrics.update({
                "price_discovery_efficiency": 0.88,
                "information_integration": 0.75
            })
        elif 0 <= current_hour <= 9:  # Asian hours
            metrics.update({
                "price_discovery_efficiency": 0.65,
                "liquidity_efficiency": 0.70
            })
        
        return metrics
    
    def generate_trading_recommendations(self, current_time: datetime, strategy: str = "balanced") -> Dict[str, any]:
        """Trading recommendations generator"""
        
        recommendations = {
            "immediate_actions": [],
            "upcoming_opportunities": [],
            "risk_warnings": [],
            "position_sizing": {},
            "exit_strategy": {}
        }
        
        current_hour = current_time.hour
        current_day = current_time.weekday()
        
        # Immediate actions
        if 8 <= current_hour <= 10:  # European open
            recommendations["immediate_actions"].append({
                "action": "INCREASE_POSITION_SIZE",
                "reason": "European session open - high volatility expected",
                "timeframe": "next 2 hours",
                "confidence": 0.8
            })
        elif 13 <= current_hour <= 17:  # Overlap period
            recommendations["immediate_actions"].append({
                "action": "SCALPING_OPPORTUNITY",
                "reason": "European-American overlap - maximum liquidity",
                "timeframe": "next 4 hours",
                "confidence": 0.9
            })
        
        # Upcoming opportunities
        next_events = self._get_next_market_events(current_time)
        for event in next_events[:3]:
            recommendations["upcoming_opportunities"].append({
                "event": event["type"],
                "time": event["time"],
                "preparation": "pre_position_hedge",
                "expected_impact": event.get("impact", "medium")
            })
        
        # Risk warnings
        if current_day == 4:  # Friday
            recommendations["risk_warnings"].append({
                "warning": "FRIDAY_EFFECT",
                "description": "Reduced liquidity expected in late Friday session",
                "mitigation": "reduce_position_sizes"
            })
        
        # Position sizing
        recommendations["position_sizing"].update({
            "base_size": "1%",
            "volatility_adjustment": "reduce_by_50% if VIX > 20",
            "session_adjustment": "double_size_during_overlaps",
            "news_adjustment": "reduce_by_75% before high_impact_news"
        })
        
        # Exit strategy
        recommendations["exit_strategy"].update({
            "profit_targets": "1.5R (risk reward ratio)",
            "stop_loss": "1R maximum",
            "time_based_exit": "close_all_positions_30min_before_major_news",
            "trailing_stop": "activate_after_0.5R_profit"
        })
        
        return recommendations
    
    def _get_next_market_events(self, current_time: datetime) -> List[Dict[str, any]]:
        """Keyingi market events (mock data)"""
        
        return [
            {"type": "central_bank_decision", "time": "in 2 hours", "impact": "high"},
            {"type": "inventory_report", "time": "tomorrow", "impact": "medium"},
            {"type": "gdp_release", "time": "in 3 days", "impact": "high"}
        ]
    
    def backtest_timing_strategy(self, strategy: str, time_period: str = "1month") -> Dict[str, any]:
        """Backtest timing strategy"""
        
        # Mock backtest results
        results = {
            "strategy": strategy,
            "time_period": time_period,
            "total_trades": 156,
            "winning_trades": 102,
            "win_rate": 0.654,
            "total_return": 0.234,  # 23.4%
            "sharpe_ratio": 1.42,
            "max_drawdown": 0.087,  # 8.7%
            "profit_factor": 1.68,
            "avg_trade_duration": "2.3 hours",
            "best_performing_session": "European-American overlap",
            "worst_performing_session": "Late Asian session",
            "monthly_returns": [0.045, 0.032, 0.056, 0.041, 0.038, 0.022],
            "session_performance": {
                "asian": {"return": 0.018, "trades": 45, "win_rate": 0.62},
                "european": {"return": 0.089, "trades": 67, "win_rate": 0.71},
                "american": {"return": 0.076, "trades": 44, "win_rate": 0.68}
            }
        }
        
        return results
    
    def optimize_portfolio_timing(self, portfolio_allocation: Dict[str, float], 
                                current_time: datetime) -> Dict[str, any]:
        """Portfolio timing optimization"""
        
        allocation = portfolio_allocation
        
        # Session-based allocation optimization
        optimal_allocation = {}
        
        # High volatility sessions - aggressive instruments
        if 8 <= current_time.hour <= 17:  # European hours
            optimal_allocation.update({
                "major_pairs": allocation.get("major_pairs", 0.4) * 1.2,
                "precious_metals": allocation.get("precious_metals", 0.2) * 1.1,
                "commodities": allocation.get("commodities", 0.1) * 0.9
            })
        
        # Overlap periods - maximum allocation
        elif 13 <= current_time.hour <= 17:  # Overlap
            optimal_allocation.update({
                "major_pairs": allocation.get("major_pairs", 0.4) * 1.5,
                "precious_metals": allocation.get("precious_metals", 0.2) * 1.3,
                "minor_pairs": allocation.get("minor_pairs", 0.2) * 1.2
            })
        
        # Quiet periods - defensive allocation
        else:
            optimal_allocation.update({
                "major_pairs": allocation.get("major_pairs", 0.4) * 0.8,
                "precious_metals": allocation.get("precious_metals", 0.2) * 1.2,
                "cash": allocation.get("cash", 0.1) * 1.5
            })
        
        # Normalize to 100%
        total_allocation = sum(optimal_allocation.values())
        optimal_allocation = {k: v/total_allocation for k, v in optimal_allocation.items()}
        
        return {
            "current_allocation": allocation,
            "optimal_allocation": optimal_allocation,
            "recommended_changes": [
                {
                    "asset": asset,
                    "current": allocation.get(asset, 0),
                    "optimal": optimal_allocation.get(asset, 0),
                    "change": optimal_allocation.get(asset, 0) - allocation.get(asset, 0)
                }
                for asset in optimal_allocation.keys()
            ],
            "timing_justification": "allocation_adjusted_for_market_conditions",
            "rebalance_frequency": "daily_during_high_volatility_periods"
        }