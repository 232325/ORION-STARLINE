"""
AI Feedback Loop - Automated insights and performance analysis
AI-powered trading analysis with feedback mechanisms
"""

import json
import sqlite3
import datetime
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import statistics
import logging
import re

from trading_journal import TradingJournal, TradeEntry, PerformanceMetrics, EmotionalState, MarketCondition

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIInsight:
    """AI insight ma'lumotlari"""
    id: str
    type: str  # performance, pattern, improvement, weakness, strength
    title: str
    description: str
    impact_score: float  # 0-100
    confidence: float  # 0-100
    related_trades: List[str]
    recommendations: List[str]
    created_at: datetime.datetime
    priority: str  # high, medium, low

@dataclass
class PatternAnalysis:
    """Pattern analysis natijalari"""
    pattern_type: str
    frequency: int
    success_rate: float
    average_pnl: float
    conditions: Dict[str, Any]
    recommendations: List[str]

@dataclass
class ImprovementArea:
    """Yaxshilash sohalari"""
    area: str
    current_score: float
    target_score: float
    actions: List[str]
    timeline: str
    priority: str

class AIFeedbackLoop:
    """AI-powered feedback loop tizimi"""
    
    def __init__(self, journal: TradingJournal):
        self.journal = journal
        self.db_path = journal.db_path
        
    def analyze_performance_patterns(self, days: int = 30) -> Dict[str, Any]:
        """Performance patternlarini tahlil qilish"""
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        trades = self.journal.get_trades_by_date_range(start_date, end_date)
        
        if not trades:
            return {"error": "No trades found for analysis"}
        
        patterns = {
            "emotional_bias_patterns": self._analyze_emotional_bias(trades),
            "time_patterns": self._analyze_time_patterns(trades),
            "strategy_patterns": self._analyze_strategy_patterns(trades),
            "market_condition_patterns": self._analyze_market_condition_patterns(trades),
            "risk_management_patterns": self._analyze_risk_management_patterns(trades),
            "symbol_patterns": self._analyze_symbol_patterns(trades)
        }
        
        return {
            "analysis_period": days,
            "total_trades_analyzed": len(trades),
            "patterns": patterns,
            "insights": self._generate_pattern_insights(patterns, trades)
        }
    
    def identify_improvement_areas(self, trades: List[TradeEntry] = None) -> List[ImprovementArea]:
        """Yaxshilash sohalarini aniqlash"""
        if trades is None:
            trades = self.journal.get_all_trades()
        
        if not trades:
            return []
        
        improvements = []
        
        # Win rate improvement
        metrics = self.journal.calculate_performance_metrics(trades)
        if metrics.win_rate < 50:
            improvements.append(ImprovementArea(
                area="Win Rate",
                current_score=metrics.win_rate,
                target_score=65.0,
                actions=[
                    "Risk-reward ratio qayta ko'rib chiqish",
                    "Entry signal sifatini yaxshilash",
                    "Market sharoitlarini yaxshiroq tahlil qilish"
                ],
                timeline="2-4 hafta",
                priority="high"
            ))
        
        # Risk management improvement
        avg_risk_reward = np.mean([t.risk_reward_ratio for t in trades])
        if avg_risk_reward < 1.5:
            improvements.append(ImprovementArea(
                area="Risk-Reward Management",
                current_score=avg_risk_reward,
                target_score=2.0,
                actions=[
                    "Stop loss va take profit darajasini optimallashtirish",
                    "Risk qoidalarini qat'iyroq qo'llash",
                    "Position sizing Strategiyasini qayta ko'rib chiqish"
                ],
                timeline="1-2 hafta",
                priority="high"
            ))
        
        # Emotional management
        emotional_performance = self._analyze_emotional_performance(trades)
        if emotional_performance:
            worst_emotion = min(emotional_performance.items(), key=lambda x: x[1]['avg_pnl'])
            if worst_emotion[1]['avg_pnl'] < 0:
                improvements.append(ImprovementArea(
                    area="Emotional Management",
                    current_score=50.0,
                    target_score=75.0,
                    actions=[
                        f"{worst_emotion[0]} holatida qaror qabul qilish qobiliyatini rivojlantirish",
                        "Meditation va stress management amaliyotlari",
                        "Trading journal da emotsional holatni aniqroq qayd etish"
                    ],
                    timeline="3-6 hafta",
                    priority="medium"
                ))
        
        # Strategy optimization
        strategy_performance = self._analyze_strategy_patterns(trades)
        underperforming_strategies = [
            strategy for strategy, perf in strategy_performance.items() 
            if perf['avg_pnl'] < 0 or perf['win_rate'] < 40
        ]
        
        if underperforming_strategies:
            improvements.append(ImprovementArea(
                area="Strategy Optimization",
                current_score=60.0,
                target_score=80.0,
                actions=[
                    "Underperforming strategiyarni tahlil qilish",
                    "Strategy parametrlarini optimallashtirish",
                    "Yangi, ishonchli strategiyalarni sinab ko'rish"
                ],
                timeline="2-3 hafta",
                priority="medium"
            ))
        
        return improvements
    
    def detect_trading_mistakes(self, trades: List[TradeEntry] = None) -> List[Dict[str, Any]]:
        """Trading xatolarni aniqlash"""
        if trades is None:
            trades = self.journal.get_all_trades()
        
        mistakes = []
        
        for trade in trades:
            trade_mistakes = []
            
            # Entry price mistake
            if trade.pnl < -100:  # Katta yo'qotish
                trade_mistakes.append({
                    "type": "Large Loss",
                    "description": f"Katta yo'qotish: ${trade.pnl:.2f}",
                    "impact": "high",
                    "suggestion": "Stop loss qoidalarini qat'iy qo'llash"
                })
            
            # Low confidence high loss
            if trade.confidence_level < 6 and trade.pnl < -50:
                trade_mistakes.append({
                    "type": "Low Confidence Trade",
                    "description": "Past ishonch darajasida katta yo'qotish",
                    "impact": "high",
                    "suggestion": "Past ishonch darajasida trade qilmaslik"
                })
            
            # Poor risk-reward ratio
            if trade.risk_reward_ratio < 1.0 and trade.pnl < 0:
                trade_mistakes.append({
                    "type": "Poor Risk-Reward",
                    "description": f"Yomon risk-reward ratio: {trade.risk_reward_ratio:.2f}",
                    "impact": "medium",
                    "suggestion": "Risk-reward ratio kamida 1:2 bo'lishi kerak"
                })
            
            # Emotional trading
            emotional_states_impacting_performance = [EmotionalState.FEARFUL, EmotionalState.NERVOUS, EmotionalState.FRUSTRATED]
            if trade.emotional_state in emotional_states_impacting_performance and trade.pnl < -20:
                trade_mistakes.append({
                    "type": "Emotional Trading",
                    "description": f"Emotsional holatda: {trade.emotional_state.value}",
                    "impact": "medium",
                    "suggestion": "Emotsional holatlarda trade qilmaslik"
                })
            
            # No stop loss
            if trade.stop_loss == 0:
                trade_mistakes.append({
                    "type": "No Stop Loss",
                    "description": "Stop loss belgilab olinmagan",
                    "impact": "high",
                    "suggestion": "Har doim stop loss belgilash"
                })
            
            # Poor timing (high volatility but no adjustment)
            if trade.market_condition == MarketCondition.VOLATILE and abs(trade.pnl_percentage) > 5:
                trade_mistakes.append({
                    "type": "Poor Timing",
                    "description": "Volatility holatida yomon timing",
                    "impact": "medium",
                    "suggestion": "Volatility holatlarida ehtiyotkor bo'lish"
                })
            
            if trade_mistakes:
                mistakes.append({
                    "trade_id": trade.id,
                    "symbol": trade.symbol,
                    "trade_mistakes": trade_mistakes,
                    "total_mistake_impact": sum(m["impact"] == "high" for m in trade_mistakes)
                })
        
        return sorted(mistakes, key=lambda x: x["total_mistake_impact"], reverse=True)
    
    def generate_ai_insights(self, days: int = 30) -> List[AIInsight]:
        """AI insights yaratish"""
        insights = []
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        trades = self.journal.get_trades_by_date_range(start_date, end_date)
        
        if not trades:
            return insights
        
        # Performance insights
        metrics = self.journal.calculate_performance_metrics(trades)
        
        if metrics.win_rate < 50:
            insights.append(AIInsight(
                id=f"insight_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_1",
                type="performance",
                title="Past Win Rate",
                description=f"Win rate {metrics.win_rate:.1f}% - bu o'rtacha ko'rsatkichdan past",
                impact_score=75.0,
                confidence=85.0,
                related_trades=[t.id for t in trades if t.pnl < 0][:5],
                recommendations=[
                    "Strategy qoidalarini qayta ko'rib chiqish",
                    "Entry signal sifati va timing ni yaxshilash",
                    "Risk management qoidalarini qat'iy qo'llash"
                ],
                created_at=datetime.datetime.now(),
                priority="high"
            ))
        
        # Pattern insights
        emotional_performance = self._analyze_emotional_performance(trades)
        if emotional_performance:
            best_emotion = max(emotional_performance.items(), key=lambda x: x[1]['avg_pnl'])
            worst_emotion = min(emotional_performance.items(), key=lambda x: x[1]['avg_pnl'])
            
            if best_emotion[1]['avg_pnl'] > worst_emotion[1]['avg_pnl'] * 2:
                insights.append(AIInsight(
                    id=f"insight_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_2",
                    type="pattern",
                    title="Emotsional Holat Ta'siri",
                    description=f"{best_emotion[0]} holatida natija {worst_emotion[0]} ga qaraganda {best_emotion[1]['avg_pnl'] - worst_emotion[1]['avg_pnl']:.2f}$ yaxshiroq",
                    impact_score=80.0,
                    confidence=90.0,
                    related_trades=[t.id for t in trades if t.emotional_state.value == best_emotion[0]][:3],
                    recommendations=[
                        f"{best_emotion[0]} holatini saqlab qolish strategiyasi",
                        f"{worst_emotion[0]} holatida trade qilmaslik",
                        "Emotsional holatni yaxshilash usullari"
                    ],
                    created_at=datetime.datetime.now(),
                    priority="high"
                ))
        
        # Strategy insights
        strategy_performance = self._analyze_strategy_patterns(trades)
        if len(strategy_performance) > 1:
            best_strategy = max(strategy_performance.items(), key=lambda x: x[1]['avg_pnl'])
            
            if best_strategy[1]['avg_pnl'] > 50 and best_strategy[1]['win_rate'] > 60:
                insights.append(AIInsight(
                    id=f"insight_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_3",
                    type="strength",
                    title="Top Strategy Performance",
                    description=f"{best_strategy[0]} strategiyasi eng yaxshi natija ko'rsatdi: ${best_strategy[1]['avg_pnl']:.2f} o'rtacha P&L, {best_strategy[1]['win_rate']:.1f}% win rate",
                    impact_score=85.0,
                    confidence=95.0,
                    related_trades=[t.id for t in trades if t.strategy == best_strategy[0]][:5],
                    recommendations=[
                        f"{best_strategy[0]} strategiyasini ko'proq qo'llash",
                        "Bu strategiyani boshqa instrumentlarda ham sinab ko'rish",
                        "Strategy parametrlarini yanada optimallashtirish"
                    ],
                    created_at=datetime.datetime.now(),
                    priority="medium"
                ))
        
        return insights
    
    def analyze_market_timing(self, trades: List[TradeEntry] = None) -> Dict[str, Any]:
        """Market timing tahlili"""
        if trades is None:
            trades = self.journal.get_all_trades()
        
        if not trades:
            return {"error": "No trades found"}
        
        # Time-based analysis
        hourly_performance = defaultdict(lambda: {"pnl": 0, "trades": 0})
        daily_performance = defaultdict(lambda: {"pnl": 0, "trades": 0})
        weekly_performance = defaultdict(lambda: {"pnl": 0, "trades": 0})
        
        for trade in trades:
            # Hourly analysis
            hour = trade.entry_time.hour
            hourly_performance[hour]["pnl"] += trade.pnl
            hourly_performance[hour]["trades"] += 1
            
            # Daily analysis
            day_name = trade.entry_time.strftime("%A")
            daily_performance[day_name]["pnl"] += trade.pnl
            daily_performance[day_name]["trades"] += 1
            
            # Weekly analysis
            week_num = trade.entry_time.isocalendar()[1]
            weekly_performance[week_num]["pnl"] += trade.pnl
            weekly_performance[week_num]["trades"] += 1
        
        # Best performing times
        best_hours = sorted(hourly_performance.items(), 
                           key=lambda x: x[1]["pnl"]/x[1]["trades"] if x[1]["trades"] > 0 else 0, 
                           reverse=True)[:3]
        
        best_days = sorted(daily_performance.items(),
                          key=lambda x: x[1]["pnl"]/x[1]["trades"] if x[1]["trades"] > 0 else 0,
                          reverse=True)[:3]
        
        return {
            "hourly_performance": dict(hourly_performance),
            "daily_performance": dict(daily_performance),
            "weekly_performance": dict(weekly_performance),
            "best_hours": [{"hour": h, "avg_pnl": data["pnl"]/data["trades"], "trades": data["trades"]} 
                          for h, data in best_hours if data["trades"] > 0],
            "best_days": [{"day": d, "avg_pnl": data["pnl"]/data["trades"], "trades": data["trades"]} 
                         for d, data in best_days if data["trades"] > 0],
            "recommendations": self._generate_timing_recommendations(hourly_performance, daily_performance)
        }
    
    def track_emotional_bias(self, trades: List[TradeEntry] = None) -> Dict[str, Any]:
        """Emotsional bias ni kuzatib borish"""
        if trades is None:
            trades = self.journal.get_all_trades()
        
        if not trades:
            return {"error": "No trades found"}
        
        # Emotional state analysis
        emotional_performance = self._analyze_emotional_performance(trades)
        
        # Bias detection
        bias_analysis = {}
        
        for emotion, performance in emotional_performance.items():
            if performance["trades"] >= 3:  # Minimum 3 trades
                bias_score = 0
                bias_type = ""
                
                # Fear/Greed bias
                if emotion in [EmotionalState.FEARFUL.value, EmotionalState.NERVOUS.value]:
                    if performance["win_rate"] < 40:
                        bias_score = 75
                        bias_type = "Fear-based trading bias"
                
                elif emotion == EmotionalState.GREEDY.value:
                    if performance["win_rate"] < 50:
                        bias_score = 60
                        bias_type = "Greed-driven decisions"
                
                # Overconfidence bias
                if emotion == EmotionalState.CONFIDENT.value:
                    high_confidence_losses = len([t for t in trades 
                                               if t.emotional_state.value == emotion and 
                                               t.confidence_level > 8 and t.pnl < -50])
                    if high_confidence_losses > 0:
                        bias_score = 80
                        bias_type = "Overconfidence bias"
                
                if bias_score > 0:
                    bias_analysis[emotion] = {
                        "bias_score": bias_score,
                        "bias_type": bias_type,
                        "affected_trades": performance["trades"],
                        "win_rate": performance["win_rate"],
                        "avg_pnl": performance["avg_pnl"]
                    }
        
        return {
            "emotional_performance": emotional_performance,
            "bias_analysis": bias_analysis,
            "recommendations": self._generate_bias_recommendations(bias_analysis)
        }
    
    def generate_coaching_recommendations(self) -> Dict[str, Any]:
        """Coaching tavsiyalari"""
        trades = self.journal.get_all_trades()
        improvements = self.identify_improvement_areas(trades)
        mistakes = self.detect_trading_mistakes(trades)
        insights = self.generate_ai_insights()
        
        recommendations = {
            "immediate_actions": [
                "Har kuni trading journal da emotsional holatni qayd etish",
                "Stop loss va take profit ni avval belgilash",
                "Past ishonch darajasida trade qilmaslik"
            ],
            "weekly_goals": [
                f"Win rate ni {improvements[0].target_score:.1f}% ga yetkazish" if improvements else "Win rate ni yaxshilash",
                "Risk-reward ratio ni 1:2 dan yuqori saqlash",
                "Har hafta strategy performance ni tahlil qilish"
            ],
            "long_term_improvements": [
                "Konsistent trading plan yaratish",
                "Psychological discipline rivojlantirish",
                "Multiple time frame analysis o'rganish"
            ],
            "common_mistakes_to_avoid": [
                mistake["trade_mistakes"][0]["suggestion"] for mistake in mistakes[:3]
            ],
            "strengths_to_leverage": [
                insight.recommendations[0] for insight in insights if insight.type == "strength"
            ]
        }
        
        return recommendations
    
    def _analyze_emotional_bias(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Emotsional bias tahlili"""
        emotional_performance = self._analyze_emotional_performance(trades)
        
        return {
            "emotional_performance": emotional_performance,
            "emotions_count": len(emotional_performance),
            "best_emotion": max(emotional_performance.items(), key=lambda x: x[1]['avg_pnl']) if emotional_performance else None,
            "worst_emotion": min(emotional_performance.items(), key=lambda x: x[1]['avg_pnl']) if emotional_performance else None
        }
    
    def _analyze_time_patterns(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Vaqt patternlari tahlili"""
        hourly_stats = defaultdict(lambda: {"pnl": 0, "trades": 0, "wins": 0})
        daily_stats = defaultdict(lambda: {"pnl": 0, "trades": 0, "wins": 0})
        
        for trade in trades:
            hour = trade.entry_time.hour
            day = trade.entry_time.strftime("%A")
            
            hourly_stats[hour]["pnl"] += trade.pnl
            hourly_stats[hour]["trades"] += 1
            if trade.pnl > 0:
                hourly_stats[hour]["wins"] += 1
            
            daily_stats[day]["pnl"] += trade.pnl
            daily_stats[day]["trades"] += 1
            if trade.pnl > 0:
                daily_stats[day]["wins"] += 1
        
        # Calculate win rates
        for hour_data in hourly_stats.values():
            if hour_data["trades"] > 0:
                hour_data["win_rate"] = (hour_data["wins"] / hour_data["trades"]) * 100
                hour_data["avg_pnl"] = hour_data["pnl"] / hour_data["trades"]
        
        for day_data in daily_stats.values():
            if day_data["trades"] > 0:
                day_data["win_rate"] = (day_data["wins"] / day_data["trades"]) * 100
                day_data["avg_pnl"] = day_data["pnl"] / day_data["trades"]
        
        return {
            "hourly_performance": dict(hourly_stats),
            "daily_performance": dict(daily_stats)
        }
    
    def _analyze_strategy_patterns(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Strategy patternlari tahlili"""
        strategy_stats = defaultdict(lambda: {"pnl": 0, "trades": 0, "wins": 0})
        
        for trade in trades:
            strategy_stats[trade.strategy]["pnl"] += trade.pnl
            strategy_stats[trade.strategy]["trades"] += 1
            if trade.pnl > 0:
                strategy_stats[trade.strategy]["wins"] += 1
        
        # Calculate metrics
        for strategy, stats in strategy_stats.items():
            if stats["trades"] > 0:
                stats["win_rate"] = (stats["wins"] / stats["trades"]) * 100
                stats["avg_pnl"] = stats["pnl"] / stats["trades"]
        
        return dict(strategy_stats)
    
    def _analyze_market_condition_patterns(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Bozor sharoitlari patternlari tahlili"""
        condition_stats = defaultdict(lambda: {"pnl": 0, "trades": 0, "wins": 0})
        
        for trade in trades:
            condition_stats[trade.market_condition.value]["pnl"] += trade.pnl
            condition_stats[trade.market_condition.value]["trades"] += 1
            if trade.pnl > 0:
                condition_stats[trade.market_condition.value]["wins"] += 1
        
        # Calculate metrics
        for condition, stats in condition_stats.items():
            if stats["trades"] > 0:
                stats["win_rate"] = (stats["wins"] / stats["trades"]) * 100
                stats["avg_pnl"] = stats["pnl"] / stats["trades"]
        
        return dict(condition_stats)
    
    def _analyze_risk_management_patterns(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Risk management patternlari tahlili"""
        risk_stats = {
            "avg_risk_reward": np.mean([t.risk_reward_ratio for t in trades]),
            "trades_with_stop_loss": len([t for t in trades if t.stop_loss > 0]),
            "avg_confidence": np.mean([t.confidence_level for t in trades]),
            "high_confidence_trades": len([t for t in trades if t.confidence_level > 7])
        }
        
        return risk_stats
    
    def _analyze_symbol_patterns(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Symbol patternlari tahlili"""
        symbol_stats = defaultdict(lambda: {"pnl": 0, "trades": 0, "wins": 0})
        
        for trade in trades:
            symbol_stats[trade.symbol]["pnl"] += trade.pnl
            symbol_stats[trade.symbol]["trades"] += 1
            if trade.pnl > 0:
                symbol_stats[trade.symbol]["wins"] += 1
        
        # Calculate metrics
        for symbol, stats in symbol_stats.items():
            if stats["trades"] > 0:
                stats["win_rate"] = (stats["wins"] / stats["trades"]) * 100
                stats["avg_pnl"] = stats["pnl"] / stats["trades"]
        
        return dict(symbol_stats)
    
    def _analyze_emotional_performance(self, trades: List[TradeEntry]) -> Dict[str, Any]:
        """Emotsional performance tahlili"""
        emotional_stats = defaultdict(lambda: {"pnl": 0, "trades": 0, "wins": 0})
        
        for trade in trades:
            emotion = trade.emotional_state.value
            emotional_stats[emotion]["pnl"] += trade.pnl
            emotional_stats[emotion]["trades"] += 1
            if trade.pnl > 0:
                emotional_stats[emotion]["wins"] += 1
        
        # Calculate metrics
        for emotion, stats in emotional_stats.items():
            if stats["trades"] > 0:
                stats["win_rate"] = (stats["wins"] / stats["trades"]) * 100
                stats["avg_pnl"] = stats["pnl"] / stats["trades"]
        
        return dict(emotional_stats)
    
    def _generate_pattern_insights(self, patterns: Dict[str, Any], trades: List[TradeEntry]) -> List[str]:
        """Pattern insights yaratish"""
        insights = []
        
        # Strategy insights
        if "strategy_patterns" in patterns:
            strategy_performance = patterns["strategy_patterns"]
            best_strategy = max(strategy_performance.items(), key=lambda x: x[1]["avg_pnl"] if x[1]["trades"] > 0 else -999)
            if best_strategy[1]["trades"] > 0:
                insights.append(f"{best_strategy[0]} eng yaxshi natija ko'rsatdi")
        
        # Emotional insights
        if "emotional_bias_patterns" in patterns:
            emotional_performance = patterns["emotional_bias_patterns"]["emotional_performance"]
            if emotional_performance:
                best_emotion = max(emotional_performance.items(), key=lambda x: x[1]["avg_pnl"] if x[1]["trades"] > 0 else -999)
                insights.append(f"{best_emotion[0]} holatida eng yaxshi natija")
        
        return insights
    
    def _generate_timing_recommendations(self, hourly_perf: Dict, daily_perf: Dict) -> List[str]:
        """Timing tavsiyalari"""
        recommendations = []
        
        # Best hour recommendation
        if hourly_perf:
            best_hours = sorted(hourly_perf.items(), 
                              key=lambda x: x[1]["pnl"]/x[1]["trades"] if x[1]["trades"] > 0 else 0, 
                              reverse=True)
            if best_hours and best_hours[0][1]["trades"] > 0:
                recommendations.append(f"Eng yaxshi vaqt: {best_hours[0][0]}:00")
        
        # Best day recommendation
        if daily_perf:
            best_days = sorted(daily_perf.items(),
                             key=lambda x: x[1]["pnl"]/x[1]["trades"] if x[1]["trades"] > 0 else 0,
                             reverse=True)
            if best_days and best_days[0][1]["trades"] > 0:
                recommendations.append(f"Eng yaxshi kun: {best_days[0][0]}")
        
        return recommendations
    
    def _generate_bias_recommendations(self, bias_analysis: Dict[str, Any]) -> List[str]:
        """Bias recommendations"""
        recommendations = []
        
        for emotion, bias_data in bias_analysis.items():
            if bias_data["bias_type"] == "Fear-based trading bias":
                recommendations.append("Qo'rqish holatida trade qilmaslik")
            elif bias_data["bias_type"] == "Greed-driven decisions":
                recommendations.append("Hirs holatida ehtiyotkor bo'lish")
            elif bias_data["bias_type"] == "Overconfidence bias":
                recommendations.append("Ishonch darajasi yuqori bo'lgan trade larda ham ehtiyotkorlik")
        
        return recommendations if recommendations else ["Emotsional bias aniqlanmadi"]