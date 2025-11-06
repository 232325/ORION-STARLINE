"""
Feedback Processor

Performance feedback signallarini qayta ishlash va optimization
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import numpy as np

@dataclass
class FeedbackSignal:
    """Feedback signal structure"""
    signal_type: str
    strength: float
    confidence: float
    timestamp: datetime
    source: str
    parameters: Dict[str, Any]
    suggested_action: str

@dataclass
class FeedbackAnalysis:
    """Feedback analysis result"""
    timestamp: datetime
    primary_signals: List[FeedbackSignal]
    consensus_strength: float
    risk_assessment: Dict[str, float]
    recommended_actions: List[str]
    confidence_level: float

class FeedbackProcessor:
    """
    Feedback Signal Processing
    
    - Multi-source feedback integration
    - Signal consensus building
    - Risk-adjusted feedback
    - Action recommendation
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Feedback sources
        self.feedback_sources = {
            "performance": self._process_performance_feedback,
            "market": self._process_market_feedback,
            "risk": self._process_risk_feedback,
            "technical": self._process_technical_feedback,
            "sentiment": self._process_sentiment_feedback,
            "governance": self._process_governance_feedback
        }
        
        # Signal processing parameters
        self.signal_weights = {
            "performance": 0.25,
            "market": 0.20,
            "risk": 0.20,
            "technical": 0.15,
            "sentiment": 0.10,
            "governance": 0.10
        }
        
        # Signal thresholds
        self.thresholds = {
            "strong_signal": 0.8,
            "moderate_signal": 0.6,
            "weak_signal": 0.4,
            "consensus_threshold": 0.7,
            "risk_threshold": 0.15
        }
        
        # Feedback history
        self.feedback_history = deque(maxlen=500)
        self.signal_history = defaultdict(lambda: deque(maxlen=100))
        
        # Processing state
        self.is_processing = False
        self.last_processing_time = None
        
        # Action mappings
        self.action_mapping = {
            "buy": ["increase_position", "add_to_position", "enter_long"],
            "sell": ["decrease_position", "reduce_position", "enter_short"],
            "hold": ["maintain_position", "wait", "do_nothing"],
            "rebalance": ["rebalance_portfolio", "adjust_weights", "optimize_allocation"],
            "hedge": ["add_hedge", "reduce_risk", "protect_downside"],
            "exit": ["close_position", "stop_loss", "realize_gains"]
        }
    
    async def process_feedback(self, feedback_data: Dict) -> FeedbackAnalysis:
        """
        Feedback signallarini qayta ishlash
        """
        try:
            self.is_processing = True
            self.last_processing_time = datetime.now()
            
            # 1. Individual signal processing
            individual_signals = await self._process_individual_sources(feedback_data)
            
            # 2. Signal consensus building
            consensus = await self._build_signal_consensus(individual_signals)
            
            # 3. Risk assessment
            risk_assessment = await self._assess_feedback_risk(feedback_data, consensus)
            
            # 4. Action recommendation
            recommended_actions = await self._generate_action_recommendations(
                consensus, risk_assessment
            )
            
            # 5. Confidence calculation
            confidence_level = self._calculate_confidence_level(
                individual_signals, consensus, risk_assessment
            )
            
            # 6. Build analysis result
            analysis = FeedbackAnalysis(
                timestamp=datetime.now(),
                primary_signals=list(consensus["consensus_signals"]),
                consensus_strength=consensus["consensus_strength"],
                risk_assessment=risk_assessment,
                recommended_actions=recommended_actions,
                confidence_level=confidence_level
            )
            
            # Store analysis
            self.feedback_history.append(analysis)
            
            self.logger.info(f"Feedback processed: {len(individual_signals)} signals, "
                           f"consensus: {consensus['consensus_strength']:.2f}")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Feedback processing xatosi: {str(e)}")
            return FeedbackAnalysis(
                timestamp=datetime.now(),
                primary_signals=[],
                consensus_strength=0.0,
                risk_assessment={},
                recommended_actions=["error_handling"],
                confidence_level=0.0
            )
        finally:
            self.is_processing = False
    
    async def _process_individual_sources(self, feedback_data: Dict) -> Dict[str, List[FeedbackSignal]]:
        """Individual feedback sources processing"""
        individual_signals = {}
        
        tasks = []
        for source_name in self.feedback_sources:
            if source_name in feedback_data:
                task = self._process_single_source(source_name, feedback_data[source_name])
                tasks.append((source_name, task))
        
        # Process all sources
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        for i, (source_name, result) in enumerate(zip([s[0] for s in tasks], results)):
            if isinstance(result, Exception):
                self.logger.error(f"Source processing error ({source_name}): {str(result)}")
                individual_signals[source_name] = []
            else:
                individual_signals[source_name] = result
        
        return individual_signals
    
    async def _process_single_source(self, source_name: str, source_data: Any) -> List[FeedbackSignal]:
        """Single source processing"""
        processor_func = self.feedback_sources[source_name]
        return await processor_func(source_data)
    
    async def _build_signal_consensus(self, individual_signals: Dict[str, List[FeedbackSignal]]) -> Dict[str, Any]:
        """Signal consensus building"""
        all_signals = []
        signal_directions = defaultdict(list)
        signal_strengths = []
        
        # Collect all signals with weights
        for source_name, signals in individual_signals.items():
            weight = self.signal_weights.get(source_name, 0.1)
            
            for signal in signals:
                weighted_signal = FeedbackSignal(
                    signal_type=signal.signal_type,
                    strength=signal.strength * weight,
                    confidence=signal.confidence,
                    timestamp=signal.timestamp,
                    source=source_name,
                    parameters=signal.parameters,
                    suggested_action=signal.suggested_action
                )
                all_signals.append(weighted_signal)
                
                # Track directions
                direction = self._extract_signal_direction(signal.signal_type, signal.parameters)
                signal_directions[direction].append(weighted_signal.strength)
                
                signal_strengths.append(weighted_signal.strength)
        
        # Calculate consensus strength
        if not signal_strengths:
            consensus_strength = 0.0
        else:
            # Average signal strength with direction bias
            positive_strength = sum(signal_directions.get("positive", []))
            negative_strength = sum(signal_directions.get("negative", []))
            total_positive = len(signal_directions.get("positive", []))
            total_negative = len(signal_directions.get("negative", []))
            
            # Direction consensus
            if total_positive > total_negative:
                consensus_strength = positive_strength / max(total_positive + total_negative, 1)
            elif total_negative > total_positive:
                consensus_strength = -negative_strength / max(total_positive + total_negative, 1)
            else:
                consensus_strength = np.mean(signal_strengths)
        
        # Consensus signals (strongest signals)
        consensus_signals = sorted(all_signals, key=lambda x: x.strength, reverse=True)[:5]
        
        return {
            "consensus_signals": consensus_signals,
            "consensus_strength": consensus_strength,
            "signal_distribution": dict(signal_directions),
            "total_signals": len(all_signals),
            "agreement_level": self._calculate_agreement_level(signal_directions)
        }
    
    def _extract_signal_direction(self, signal_type: str, parameters: Dict[str, Any]) -> str:
        """Signal direction extraction"""
        # Determine direction based on signal type and parameters
        if "buy" in signal_type.lower() or parameters.get("action") == "buy":
            return "positive"
        elif "sell" in signal_type.lower() or parameters.get("action") == "sell":
            return "negative"
        elif "hold" in signal_type.lower() or parameters.get("action") == "hold":
            return "neutral"
        else:
            # Default to direction in parameters
            return parameters.get("direction", "neutral")
    
    def _calculate_agreement_level(self, signal_directions: Dict[str, List[float]]) -> float:
        """Agreement level calculation"""
        direction_counts = {k: len(v) for k, v in signal_directions.items() if k != "neutral"}
        
        if not direction_counts:
            return 0.0
        
        total_directional = sum(direction_counts.values())
        max_direction_count = max(direction_counts.values())
        
        return max_direction_count / total_directional if total_directional > 0 else 0.0
    
    async def _assess_feedback_risk(self, feedback_data: Dict, consensus: Dict) -> Dict[str, float]:
        """Feedback risk assessment"""
        risk_scores = {}
        
        # Volatility risk
        volatility = feedback_data.get("market", {}).get("volatility", 0.15)
        risk_scores["volatility_risk"] = min(volatility / 0.30, 1.0)  # Normalize to 30% max
        
        # Drawdown risk
        current_drawdown = feedback_data.get("performance", {}).get("current_drawdown", 0.0)
        risk_scores["drawdown_risk"] = min(current_drawdown / 0.15, 1.0)  # Normalize to 15% max
        
        # Signal disagreement risk
        agreement_level = consensus["agreement_level"]
        risk_scores["disagreement_risk"] = 1.0 - agreement_level
        
        # Confidence risk
        avg_confidence = np.mean([s.confidence for s in consensus["consensus_signals"]])
        risk_scores["confidence_risk"] = 1.0 - avg_confidence
        
        # Market correlation risk
        market_stress = feedback_data.get("market", {}).get("stress_level", 0.0)
        risk_scores["market_risk"] = market_stress
        
        # Overall risk score
        risk_scores["overall_risk"] = np.mean(list(risk_scores.values()))
        
        return risk_scores
    
    async def _generate_action_recommendations(self, consensus: Dict, 
                                             risk_assessment: Dict) -> List[str]:
        """Action recommendations generation"""
        recommendations = []
        
        consensus_strength = consensus["consensus_strength"]
        overall_risk = risk_assessment.get("overall_risk", 0.5)
        
        # High consensus, low risk
        if consensus_strength > 0.7 and overall_risk < 0.3:
            strongest_signal = consensus["consensus_signals"][0] if consensus["consensus_signals"] else None
            
            if strongest_signal:
                # Strong action recommendation
                actions = self.action_mapping.get(strongest_signal.suggested_action.lower(), ["hold"])
                recommendations.extend(actions[:2])  # Top 2 actions
                
        # Moderate consensus
        elif consensus_strength > 0.5 and overall_risk < 0.5:
            recommendations.append("cautious_action")
            recommendations.append("monitor_closely")
            
        # High risk or low consensus
        elif overall_risk > 0.7 or consensus_strength < 0.3:
            recommendations.append("defensive_position")
            recommendations.append("wait_for_clarity")
            
        # Risk management recommendations
        if risk_assessment.get("drawdown_risk", 0) > 0.8:
            recommendations.append("reduce_position_size")
            
        if risk_assessment.get("volatility_risk", 0) > 0.8:
            recommendations.append("increase_hedging")
            
        # Default fallback
        if not recommendations:
            recommendations = ["hold_position", "continue_monitoring"]
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _calculate_confidence_level(self, individual_signals: Dict[str, List[FeedbackSignal]],
                                  consensus: Dict, risk_assessment: Dict) -> float:
        """Confidence level calculation"""
        # Signal quality confidence
        signal_confidences = []
        for signals in individual_signals.values():
            signal_confidences.extend([s.confidence for s in signals])
        
        avg_signal_confidence = np.mean(signal_confidences) if signal_confidences else 0.5
        
        # Consensus confidence
        consensus_confidence = consensus["agreement_level"]
        
        # Risk-adjusted confidence
        risk_penalty = risk_assessment.get("overall_risk", 0.5)
        risk_adjusted_confidence = 1.0 - (risk_penalty * 0.5)
        
        # Signal strength confidence
        signal_strengths = [s.strength for s in consensus["consensus_signals"]]
        strength_confidence = np.mean(signal_strengths) if signal_strengths else 0.0
        
        # Weighted combination
        confidence = (
            avg_signal_confidence * 0.3 +
            consensus_confidence * 0.3 +
            risk_adjusted_confidence * 0.2 +
            strength_confidence * 0.2
        )
        
        return max(0.0, min(1.0, confidence))
    
    # Individual feedback processors
    async def _process_performance_feedback(self, performance_data: Dict) -> List[FeedbackSignal]:
        """Performance feedback processing"""
        signals = []
        
        # Sharpe ratio signal
        sharpe = performance_data.get("sharpe_ratio", 0.0)
        if sharpe > 1.5:
            signals.append(FeedbackSignal(
                signal_type="high_performance",
                strength=min((sharpe - 1.5) / 1.0, 1.0),
                confidence=0.9,
                timestamp=datetime.now(),
                source="performance",
                parameters={"sharpe_ratio": sharpe},
                suggested_action="buy"
            ))
        elif sharpe < 0.5:
            signals.append(FeedbackSignal(
                signal_type="low_performance",
                strength=min((0.5 - sharpe) / 0.5, 1.0),
                confidence=0.8,
                timestamp=datetime.now(),
                source="performance",
                parameters={"sharpe_ratio": sharpe},
                suggested_action="rebalance"
            ))
        
        # Drawdown signal
        drawdown = performance_data.get("max_drawdown", 0.0)
        if drawdown > 0.10:
            signals.append(FeedbackSignal(
                signal_type="high_drawdown",
                strength=min((drawdown - 0.10) / 0.15, 1.0),
                confidence=0.85,
                timestamp=datetime.now(),
                source="performance",
                parameters={"drawdown": drawdown},
                suggested_action="hedge"
            ))
        
        # Win rate signal
        win_rate = performance_data.get("win_rate", 0.5)
        if win_rate > 0.70:
            signals.append(FeedbackSignal(
                signal_type="high_win_rate",
                strength=(win_rate - 0.70) / 0.30,
                confidence=0.75,
                timestamp=datetime.now(),
                source="performance",
                parameters={"win_rate": win_rate},
                suggested_action="buy"
            ))
        
        return signals
    
    async def _process_market_feedback(self, market_data: Dict) -> List[FeedbackSignal]:
        """Market feedback processing"""
        signals = []
        
        # Volatility signal
        volatility = market_data.get("overall_volatility", 0.15)
        if volatility > 0.25:
            signals.append(FeedbackSignal(
                signal_type="high_volatility",
                strength=min((volatility - 0.25) / 0.25, 1.0),
                confidence=0.8,
                timestamp=datetime.now(),
                source="market",
                parameters={"volatility": volatility},
                suggested_action="hedge"
            ))
        elif volatility < 0.10:
            signals.append(FeedbackSignal(
                signal_type="low_volatility",
                strength=min((0.10 - volatility) / 0.10, 1.0),
                confidence=0.7,
                timestamp=datetime.now(),
                source="market",
                parameters={"volatility": volatility},
                suggested_action="buy"
            ))
        
        # Trend signal
        trend = market_data.get("trend", "neutral")
        if trend == "strong_bullish":
            signals.append(FeedbackSignal(
                signal_type="bullish_trend",
                strength=0.9,
                confidence=0.8,
                timestamp=datetime.now(),
                source="market",
                parameters={"trend": trend},
                suggested_action="buy"
            ))
        elif trend == "strong_bearish":
            signals.append(FeedbackSignal(
                signal_type="bearish_trend",
                strength=0.9,
                confidence=0.8,
                timestamp=datetime.now(),
                source="market",
                parameters={"trend": trend},
                suggested_action="sell"
            ))
        
        return signals
    
    async def _process_risk_feedback(self, risk_data: Dict) -> List[FeedbackSignal]:
        """Risk feedback processing"""
        signals = []
        
        # VaR signal
        var_1d = risk_data.get("var_1d", 0.02)
        if var_1d > 0.05:
            signals.append(FeedbackSignal(
                signal_type="high_var",
                strength=min((var_1d - 0.05) / 0.10, 1.0),
                confidence=0.9,
                timestamp=datetime.now(),
                source="risk",
                parameters={"var_1d": var_1d},
                suggested_action="hedge"
            ))
        
        # Correlation signal
        correlation = risk_data.get("portfolio_correlation", 0.5)
        if correlation > 0.8:
            signals.append(FeedbackSignal(
                signal_type="high_correlation",
                strength=min((correlation - 0.8) / 0.2, 1.0),
                confidence=0.8,
                timestamp=datetime.now(),
                source="risk",
                parameters={"correlation": correlation},
                suggested_action="rebalance"
            ))
        
        return signals
    
    async def _process_technical_feedback(self, technical_data: Dict) -> List[FeedbackSignal]:
        """Technical analysis feedback processing"""
        signals = []
        
        # RSI signal
        rsi = technical_data.get("rsi", 50)
        if rsi > 70:
            signals.append(FeedbackSignal(
                signal_type="overbought",
                strength=(rsi - 70) / 30,
                confidence=0.75,
                timestamp=datetime.now(),
                source="technical",
                parameters={"rsi": rsi},
                suggested_action="sell"
            ))
        elif rsi < 30:
            signals.append(FeedbackSignal(
                signal_type="oversold",
                strength=(30 - rsi) / 30,
                confidence=0.75,
                timestamp=datetime.now(),
                source="technical",
                parameters={"rsi": rsi},
                suggested_action="buy"
            ))
        
        # Moving average signal
        ma_signal = technical_data.get("ma_signal", "neutral")
        if ma_signal == "bullish_crossover":
            signals.append(FeedbackSignal(
                signal_type="ma_bullish",
                strength=0.8,
                confidence=0.7,
                timestamp=datetime.now(),
                source="technical",
                parameters={"ma_signal": ma_signal},
                suggested_action="buy"
            ))
        
        return signals
    
    async def _process_sentiment_feedback(self, sentiment_data: Dict) -> List[FeedbackSignal]:
        """Sentiment feedback processing"""
        signals = []
        
        # Market sentiment
        sentiment_score = sentiment_data.get("market_sentiment", 0.5)
        if sentiment_score > 0.8:
            signals.append(FeedbackSignal(
                signal_type="euphoria",
                strength=(sentiment_score - 0.8) / 0.2,
                confidence=0.6,
                timestamp=datetime.now(),
                source="sentiment",
                parameters={"sentiment": sentiment_score},
                suggested_action="cautious"
            ))
        elif sentiment_score < 0.2:
            signals.append(FeedbackSignal(
                signal_type="extreme_fear",
                strength=(0.2 - sentiment_score) / 0.2,
                confidence=0.7,
                timestamp=datetime.now(),
                source="sentiment",
                parameters={"sentiment": sentiment_score},
                suggested_action="buy"
            ))
        
        return signals
    
    async def _process_governance_feedback(self, governance_data: Dict) -> List[FeedbackSignal]:
        """Governance feedback processing"""
        signals = []
        
        # Voting results
        voting_result = governance_data.get("voting_result", "pending")
        if voting_result == "approved":
            signals.append(FeedbackSignal(
                signal_type="governance_approval",
                strength=0.8,
                confidence=0.9,
                timestamp=datetime.now(),
                source="governance",
                parameters={"result": voting_result},
                suggested_action="execute"
            ))
        elif voting_result == "rejected":
            signals.append(FeedbackSignal(
                signal_type="governance_rejection",
                strength=0.8,
                confidence=0.9,
                timestamp=datetime.now(),
                source="governance",
                parameters={"result": voting_result},
                suggested_action="hold"
            ))
        
        return signals
    
    def get_feedback_history(self, hours: int = 24) -> List[FeedbackAnalysis]:
        """Feedback history olish"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            analysis for analysis in self.feedback_history
            if analysis.timestamp >= cutoff_time
        ]
    
    def get_signal_statistics(self) -> Dict[str, Any]:
        """Signal statistics"""
        if not self.feedback_history:
            return {"message": "No feedback history available"}
        
        recent_analyses = list(self.feedback_history)[-10:]  # Last 10 analyses
        
        # Signal type distribution
        signal_types = defaultdict(int)
        total_confidence = []
        
        for analysis in recent_analyses:
            for signal in analysis.primary_signals:
                signal_types[signal.signal_type] += 1
            total_confidence.append(analysis.confidence_level)
        
        return {
            "total_analyses": len(self.feedback_history),
            "recent_confidence": np.mean(total_confidence) if total_confidence else 0,
            "signal_type_distribution": dict(signal_types),
            "avg_consensus_strength": np.mean([a.consensus_strength for a in recent_analyses]),
            "avg_risk_level": np.mean([a.risk_assessment.get("overall_risk", 0) for a in recent_analyses])
        }