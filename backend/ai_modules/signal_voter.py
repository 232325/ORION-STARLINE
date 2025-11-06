"""
AI Signal Voting System - Multiple agentlarning signallarini birlashtirish
"""

import asyncio
import logging
import time
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
from collections import defaultdict, Counter

from agent_pool import AgentPool, AgentType, MarketRegime, BaseAIAgent

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VotingMethod(Enum):
    """Ovoz berish usullari"""
    SIMPLE_MAJORITY = "simple_majority"
    WEIGHTED_VOTING = "weighted_voting"
    CONFIDENCE_BASED = "confidence_based"
    PERFORMANCE_WEIGHTED = "performance_weighted"
    ENSEMBLE_METHODS = "ensemble_methods"
    BAYESIAN_AVERAGING = "bayesian_averaging"
    MACHINE_LEARNING = "machine_learning"
    DYNAMIC_WEIGHTS = "dynamic_weights"

class SignalType(Enum):
    """Signal turlari"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    REDUCE_RISK = "REDUCE_RISK"
    INCREASE_RISK = "INCREASE_RISK"
    MAINTAIN_RISK = "MAINTAIN_RISK"

@dataclass
class Vote:
    """Individual agent vote"""
    agent_id: str
    agent_type: str
    signal_type: SignalType
    strength: float
    confidence: float
    timestamp: datetime
    weights: Dict[str, float] = field(default_factory=dict)
    reasoning: str = ""
    individual_performance: float = 0.0
    
    def get_weighted_score(self, method: VotingMethod) -> float:
        """Ovozning og'irlik hisoblash"""
        base_score = self.strength * self.confidence
        
        if method == VotingMethod.SIMPLE_MAJORITY:
            return 1.0
        elif method == VotingMethod.CONFIDENCE_BASED:
            return self.confidence
        elif method == VotingMethod.PERFORMANCE_WEIGHTED:
            return base_score * (1 + self.individual_performance)
        elif method == VotingMethod.WEIGHTED_VOTING:
            # Base weight from agent
            base_weight = self.weights.get('base', 1.0)
            return base_score * base_weight
        elif method == VotingMethod.DYNAMIC_WEIGHTS:
            # Multi-factor weighting
            factors = []
            
            # Performance factor
            perf_factor = 1 + self.individual_performance
            factors.append(perf_factor)
            
            # Confidence factor
            conf_factor = 1 + (self.confidence - 0.5) * 0.2
            factors.append(conf_factor)
            
            # Time decay factor (newer signals get higher weight)
            time_diff = (datetime.now() - self.timestamp).total_seconds() / 3600
            time_factor = max(0.5, 1.0 - (time_diff / 24))
            factors.append(time_factor)
            
            return base_score * np.prod(factors)
        else:
            return base_score

@dataclass
class VotingResult:
    """Ovoz berish natijasi"""
    final_signal: SignalType
    confidence: float
    vote_distribution: Dict[SignalType, int]
    confidence_by_type: Dict[SignalType, float]
    participating_agents: List[str]
    total_votes: int
    method_used: VotingMethod
    timestamp: datetime
    consensus_strength: float
    risk_adjusted_signal: Optional[SignalType] = None
    recommendation: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Dict ga konvertatsiya"""
        return {
            "final_signal": self.final_signal.value,
            "confidence": self.confidence,
            "vote_distribution": {k.value: v for k, v in self.vote_distribution.items()},
            "confidence_by_type": {k.value: v for k, v in self.confidence_by_type.items()},
            "participating_agents": self.participating_agents,
            "total_votes": self.total_votes,
            "method_used": self.method_used.value,
            "timestamp": self.timestamp.isoformat(),
            "consensus_strength": self.consensus_strength,
            "risk_adjusted_signal": self.risk_adjusted_signal.value if self.risk_adjusted_signal else None,
            "recommendation": self.recommendation
        }

class SignalVoter:
    """AI Signal Voting System"""
    
    def __init__(self, agent_pool: AgentPool, config: Dict[str, Any]):
        self.agent_pool = agent_pool
        self.config = config
        self.voting_history: List[VotingResult] = []
        self.performance_tracker = PerformanceTracker()
        self.market_regime_detector = MarketRegimeDetector()
        
        # Voting parameters
        self.min_consensus_threshold = config.get('min_consensus_threshold', 0.6)
        self.min_participants = config.get('min_participants', 3)
        self.confidence_threshold = config.get('confidence_threshold', 0.5)
        self.diversity_bonus = config.get('diversity_bonus', 0.1)
        
    async def process_voting(self, 
                           signals: List[Dict[str, Any]], 
                           market_data: Dict[str, Any],
                           market_regime: MarketRegime,
                           method: VotingMethod = VotingMethod.WEIGHTED_VOTING) -> VotingResult:
        """Ovoz berish jarayoni"""
        
        if not signals:
            logger.warning("No signals provided for voting")
            return self._create_empty_result()
        
        # Convert signals to Vote objects
        votes = self._convert_to_votes(signals)
        
        # Filter and validate votes
        valid_votes = self._filter_valid_votes(votes)
        
        if len(valid_votes) < self.min_participants:
            logger.warning(f"Insufficient participants: {len(valid_votes)} < {self.min_participants}")
            return self._create_insufficient_participants_result(valid_votes)
        
        # Apply voting method
        voting_result = self._apply_voting_method(valid_votes, method, market_regime)
        
        # Risk assessment and adjustment
        risk_adjusted_result = self._apply_risk_adjustment(voting_result, market_data)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(risk_adjusted_result, market_regime)
        risk_adjusted_result.recommendation = recommendation
        
        # Store in history
        self.voting_history.append(risk_adjusted_result)
        
        # Update performance tracking
        self.performance_tracker.record_voting_result(risk_adjusted_result)
        
        logger.info(f"Voting completed: {risk_adjusted_result.final_signal.value} "
                   f"with {risk_adjusted_result.confidence:.2f} confidence "
                   f"using {method.value}")
        
        return risk_adjusted_result
    
    def _convert_to_votes(self, signals: List[Dict[str, Any]]) -> List[Vote]:
        """Signalarni Vote obyektlariga konvertatsiya"""
        votes = []
        
        for signal in signals:
            try:
                agent = self.agent_pool.agents.get(signal['agent_id'])
                if not agent:
                    continue
                
                vote = Vote(
                    agent_id=signal['agent_id'],
                    agent_type=signal['agent_type'],
                    signal_type=SignalType(signal['signal_type']),
                    strength=signal['strength'],
                    confidence=signal['confidence'],
                    timestamp=datetime.fromisoformat(signal['timestamp']),
                    weights=signal.get('weights', {}),
                    reasoning=signal.get('reasoning', ''),
                    individual_performance=agent.performance.accuracy
                )
                
                votes.append(vote)
                
            except Exception as e:
                logger.error(f"Error converting signal to vote: {str(e)}")
                continue
        
        return votes
    
    def _filter_valid_votes(self, votes: List[Vote]) -> List[Vote]:
        """Valid vote larni filtrlash"""
        valid_votes = []
        
        for vote in votes:
            agent = self.agent_pool.agents.get(vote.agent_id)
            if not agent or not agent.is_healthy():
                continue
            
            # Minimum confidence check
            if vote.confidence < self.confidence_threshold * 0.5:
                continue
            
            # Recent signal check
            time_diff = (datetime.now() - vote.timestamp).total_seconds() / 3600
            if time_diff > 6:  # 6 hours max age
                continue
            
            valid_votes.append(vote)
        
        return valid_votes
    
    def _apply_voting_method(self, votes: List[Vote], method: VotingMethod, market_regime: MarketRegime) -> VotingResult:
        """Voting method ni qo'llash"""
        
        if method == VotingMethod.SIMPLE_MAJORITY:
            return self._simple_majority_voting(votes)
        elif method == VotingMethod.WEIGHTED_VOTING:
            return self._weighted_voting(votes, market_regime)
        elif method == VotingMethod.CONFIDENCE_BASED:
            return self._confidence_based_voting(votes)
        elif method == VotingMethod.PERFORMANCE_WEIGHTED:
            return self._performance_weighted_voting(votes)
        elif method == VotingMethod.ENSEMBLE_METHODS:
            return self._ensemble_voting(votes, market_regime)
        elif method == VotingMethod.BAYESIAN_AVERAGING:
            return self._bayesian_voting(votes, market_regime)
        elif method == VotingMethod.MACHINE_LEARNING:
            return self._ml_based_voting(votes, market_regime)
        elif method == VotingMethod.DYNAMIC_WEIGHTS:
            return self._dynamic_weights_voting(votes, market_regime)
        else:
            return self._simple_majority_voting(votes)
    
    def _simple_majority_voting(self, votes: List[Vote]) -> VotingResult:
        """Oddiy ko'pchilik ovoz berish"""
        signal_counts = Counter(vote.signal_type for vote in votes)
        
        final_signal = signal_counts.most_common(1)[0][0]
        total_votes = len(votes)
        
        # Consensus strength
        max_count = signal_counts[final_signal]
        consensus_strength = max_count / total_votes
        
        # Confidence calculation
        confidence = (consensus_strength + self.diversity_bonus * (len(signal_counts) - 1)) / 1.1
        
        return VotingResult(
            final_signal=final_signal,
            confidence=min(confidence, 1.0),
            vote_distribution=dict(signal_counts),
            confidence_by_type={sig: 1.0 for sig in signal_counts},
            participating_agents=[vote.agent_id for vote in votes],
            total_votes=total_votes,
            method_used=VotingMethod.SIMPLE_MAJORITY,
            timestamp=datetime.now(),
            consensus_strength=consensus_strength
        )
    
    def _weighted_voting(self, votes: List[Vote], market_regime: MarketRegime) -> VotingResult:
        """Og'irlik asoslangan ovoz berish"""
        signal_weights = defaultdict(float)
        signal_confidences = defaultdict(list)
        
        for vote in votes:
            weight = vote.get_weighted_score(VotingMethod.WEIGHTED_VOTING)
            signal_weights[vote.signal_type] += weight
            signal_confidences[vote.signal_type].append(vote.confidence)
        
        # Normalize weights
        total_weight = sum(signal_weights.values())
        if total_weight > 0:
            normalized_weights = {k: v / total_weight for k, v in signal_weights.items()}
        else:
            normalized_weights = signal_weights
        
        # Find winning signal
        final_signal = max(normalized_weights.items(), key=lambda x: x[1])[0]
        confidence = normalized_weights[final_signal]
        
        # Diversity bonus
        signal_count = len(signal_weights)
        if signal_count > 1:
            confidence = min(confidence + (self.diversity_bonus * (signal_count - 1) / signal_count), 1.0)
        
        # Average confidence by type
        confidence_by_type = {
            signal: np.mean(confs) if confs else 0.0
            for signal, confs in signal_confidences.items()
        }
        
        return VotingResult(
            final_signal=final_signal,
            confidence=confidence,
            vote_distribution=Counter(vote.signal_type for vote in votes),
            confidence_by_type=confidence_by_type,
            participating_agents=[vote.agent_id for vote in votes],
            total_votes=len(votes),
            method_used=VotingMethod.WEIGHTED_VOTING,
            timestamp=datetime.now(),
            consensus_strength=confidence
        )
    
    def _confidence_based_voting(self, votes: List[Vote]) -> VotingResult:
        """Confidence asoslangan ovoz berish"""
        signal_scores = defaultdict(float)
        signal_confidences = defaultdict(list)
        signal_counts = defaultdict(int)
        
        for vote in votes:
            score = vote.confidence * vote.strength
            signal_scores[vote.signal_type] += score
            signal_confidences[vote.signal_type].append(vote.confidence)
            signal_counts[vote.signal_type] += 1
        
        # Average confidence and normalize scores
        normalized_scores = {}
        for signal, score in signal_scores.items():
            count = signal_counts[signal]
            avg_confidence = np.mean(signal_confidences[signal])
            normalized_scores[signal] = score / count * avg_confidence
        
        final_signal = max(normalized_scores.items(), key=lambda x: x[1])[0]
        confidence = min(normalized_scores[final_signal], 1.0)
        
        return VotingResult(
            final_signal=final_signal,
            confidence=confidence,
            vote_distribution=Counter(vote.signal_type for vote in votes),
            confidence_by_type={sig: np.mean(confs) for sig, confs in signal_confidences.items()},
            participating_agents=[vote.agent_id for vote in votes],
            total_votes=len(votes),
            method_used=VotingMethod.CONFIDENCE_BASED,
            timestamp=datetime.now(),
            consensus_strength=confidence
        )
    
    def _performance_weighted_voting(self, votes: List[Vote]) -> VotingResult:
        """Performance og'irligi asoslangan ovoz berish"""
        signal_scores = defaultdict(float)
        signal_confidences = defaultdict(list)
        signal_counts = defaultdict(int)
        
        for vote in votes:
            score = vote.strength * vote.confidence * (1 + vote.individual_performance)
            signal_scores[vote.signal_type] += score
            signal_confidences[vote.signal_type].append(vote.confidence)
            signal_counts[vote.signal_type] += 1
        
        # Performance-adjusted confidence
        normalized_scores = {}
        for signal, score in signal_scores.items():
            avg_confidence = np.mean(signal_confidences[signal])
            count = signal_counts[signal]
            # More agents = higher confidence
            agent_diversity_bonus = 1.0 + (count - 1) * 0.1
            normalized_scores[signal] = (score / count) * avg_confidence * agent_diversity_bonus
        
        final_signal = max(normalized_scores.items(), key=lambda x: x[1])[0]
        confidence = min(normalized_scores[final_signal], 1.0)
        
        return VotingResult(
            final_signal=final_signal,
            confidence=confidence,
            vote_distribution=Counter(vote.signal_type for vote in votes),
            confidence_by_type={sig: np.mean(confs) for sig, confs in signal_confidences.items()},
            participating_agents=[vote.agent_id for vote in votes],
            total_votes=len(votes),
            method_used=VotingMethod.PERFORMANCE_WEIGHTED,
            timestamp=datetime.now(),
            consensus_strength=confidence
        )
    
    def _ensemble_voting(self, votes: List[Vote], market_regime: MarketRegime) -> VotingResult:
        """Ensemble methods kombinatsiyasi"""
        # Multiple voting approaches
        simple_result = self._simple_majority_voting(votes)
        weighted_result = self._weighted_voting(votes, market_regime)
        confidence_result = self._confidence_based_voting(votes)
        performance_result = self._performance_weighted_voting(votes)
        
        # Ensemble combination
        results = [simple_result, weighted_result, confidence_result, performance_result]
        
        # Weight ensemble methods
        weights = [0.2, 0.3, 0.3, 0.2]  # Balanced ensemble
        
        # Final scoring
        signal_scores = defaultdict(float)
        total_confidence = 0
        
        for result, weight in zip(results, weights):
            signal_scores[result.final_signal] += weight
            total_confidence += result.confidence * weight
        
        final_signal = max(signal_scores.items(), key=lambda x: x[1])[0]
        final_confidence = min(total_confidence, 1.0)
        
        # Combined vote distribution
        combined_distribution = Counter()
        for result in results:
            combined_distribution[result.final_signal] += 1
        
        return VotingResult(
            final_signal=final_signal,
            confidence=final_confidence,
            vote_distribution=combined_distribution,
            confidence_by_type={},
            participating_agents=[vote.agent_id for vote in votes],
            total_votes=len(votes),
            method_used=VotingMethod.ENSEMBLE_METHODS,
            timestamp=datetime.now(),
            consensus_strength=final_confidence
        )
    
    def _bayesian_voting(self, votes: List[Vote], market_regime: MarketRegime) -> VotingResult:
        """Bayesian averaging voting"""
        # Prior probabilities based on market regime
        prior_probs = self._get_bayesian_priors(market_regime)
        
        # Likelihood calculation
        signal_likelihoods = defaultdict(float)
        total_likelihood = 0
        
        for vote in votes:
            likelihood = vote.confidence * vote.strength
            signal_likelihoods[vote.signal_type] += likelihood
            total_likelihood += likelihood
        
        # Posterior probabilities
        posterior_scores = {}
        for signal in SignalType:
            prior = prior_probs.get(signal, 0.1)
            likelihood = signal_likelihoods[signal] / total_likelihood if total_likelihood > 0 else 0
            posterior = prior * likelihood
            posterior_scores[signal] = posterior
        
        # Normalize
        total_posterior = sum(posterior_scores.values())
        if total_posterior > 0:
            posterior_scores = {k: v / total_posterior for k, v in posterior_scores.items()}
        
        final_signal = max(posterior_scores.items(), key=lambda x: x[1])[0]
        confidence = posterior_scores[final_signal]
        
        return VotingResult(
            final_signal=final_signal,
            confidence=confidence,
            vote_distribution=Counter(vote.signal_type for vote in votes),
            confidence_by_type={},
            participating_agents=[vote.agent_id for vote in votes],
            total_votes=len(votes),
            method_used=VotingMethod.BAYESIAN_AVERAGING,
            timestamp=datetime.now(),
            consensus_strength=confidence
        )
    
    def _ml_based_voting(self, votes: List[ Vote], market_regime: MarketRegime) -> VotingResult:
        """Machine learning based voting"""
        # Simple ML features extraction
        features = self._extract_voting_features(votes, market_regime)
        
        # Feature-based signal scoring
        signal_scores = defaultdict(float)
        
        for vote in votes:
            # Feature-enhanced scoring
            base_score = vote.strength * vote.confidence
            
            # Agent type bonus
            type_bonus = self._get_agent_type_bonus(vote.agent_type)
            
            # Market regime adjustment
            regime_bonus = self._get_market_regime_bonus(vote.agent_type, market_regime)
            
            # Performance enhancement
            performance_enhancement = 1 + vote.individual_performance
            
            enhanced_score = base_score * type_bonus * regime_bonus * performance_enhancement
            signal_scores[vote.signal_type] += enhanced_score
        
        final_signal = max(signal_scores.items(), key=lambda x: x[1])[0]
        confidence = min(signal_scores[final_signal] / sum(signal_scores.values()), 1.0)
        
        return VotingResult(
            final_signal=final_signal,
            confidence=confidence,
            vote_distribution=Counter(vote.signal_type for vote in votes),
            confidence_by_type={},
            participating_agents=[vote.agent_id for vote in votes],
            total_votes=len(votes),
            method_used=VotingMethod.MACHINE_LEARNING,
            timestamp=datetime.now(),
            consensus_strength=confidence
        )
    
    def _dynamic_weights_voting(self, votes: List[Vote], market_regime: MarketRegime) -> VotingResult:
        """Dynamic weights based voting"""
        signal_scores = defaultdict(float)
        signal_confidences = defaultdict(list)
        signal_counts = defaultdict(int)
        
        # Calculate dynamic weights
        for vote in votes:
            dynamic_weight = vote.get_weighted_score(VotingMethod.DYNAMIC_WEIGHTS)
            
            # Additional factors
            recency_factor = self._calculate_recency_factor(vote.timestamp)
            specialization_factor = self._get_specialization_factor(vote.agent_type, market_regime)
            health_factor = self._get_agent_health_factor(vote.agent_id)
            
            final_weight = dynamic_weight * recency_factor * specialization_factor * health_factor
            signal_scores[vote.signal_type] += final_weight
            signal_confidences[vote.signal_type].append(vote.confidence)
            signal_counts[vote.signal_type] += 1
        
        final_signal = max(signal_scores.items(), key=lambda x: x[1])[0]
        confidence = min(signal_scores[final_signal], 1.0)
        
        return VotingResult(
            final_signal=final_signal,
            confidence=confidence,
            vote_distribution=Counter(vote.signal_type for vote in votes),
            confidence_by_type={sig: np.mean(confs) for sig, confs in signal_confidences.items()},
            participating_agents=[vote.agent_id for vote in votes],
            total_votes=len(votes),
            method_used=VotingMethod.DYNAMIC_WEIGHTS,
            timestamp=datetime.now(),
            consensus_strength=confidence
        )
    
    def _apply_risk_adjustment(self, result: VotingResult, market_data: Dict[str, Any]) -> VotingResult:
        """Risk adjustment qo'llash"""
        risk_data = market_data.get('risk_metrics', {})
        portfolio_risk = risk_data.get('portfolio_risk', 0.5)
        market_volatility = market_data.get('volatility', 0.2)
        
        # High risk adjustment
        if portfolio_risk > 0.8 or market_volatility > 0.3:
            if result.final_signal == SignalType.BUY:
                # Reduce BUY signal strength in high risk
                if result.confidence > 0.7:
                    result.risk_adjusted_signal = SignalType.HOLD
                else:
                    result.risk_adjusted_signal = result.final_signal
            elif result.final_signal == SignalType.SELL:
                # SELL signals get more strength in high risk
                result.risk_adjusted_signal = result.final_signal
            else:
                result.risk_adjusted_signal = result.final_signal
        
        # Low risk adjustment
        elif portfolio_risk < 0.3 and market_volatility < 0.15:
            if result.final_signal == SignalType.HOLD and result.confidence < 0.6:
                # In low risk, convert weak HOLD to BUY
                result.risk_adjusted_signal = SignalType.BUY
            else:
                result.risk_adjusted_signal = result.final_signal
        else:
            result.risk_adjusted_signal = result.final_signal
        
        return result
    
    def _generate_recommendation(self, result: VotingResult, market_regime: MarketRegime) -> str:
        """Tavsiya generatsiyasi"""
        signal = result.risk_adjusted_signal or result.final_signal
        confidence = result.confidence
        
        # Base recommendation
        if signal == SignalType.BUY:
            if confidence > 0.8:
                recommendation = "Strong BUY signal with high confidence. Consider full position size."
            elif confidence > 0.6:
                recommendation = "Moderate BUY signal. Consider partial position with risk management."
            else:
                recommendation = "Weak BUY signal. Small position with tight stops recommended."
        
        elif signal == SignalType.SELL:
            if confidence > 0.8:
                recommendation = "Strong SELL signal. Consider reducing position or taking profits."
            elif confidence > 0.6:
                recommendation = "Moderate SELL signal. Monitor for further deterioration."
            else:
                recommendation = "Weak SELL signal. Maintain position but watch closely."
        
        elif signal in [SignalType.REDUCE_RISK, SignalType.INCREASE_RISK, SignalType.MAINTAIN_RISK]:
            if signal == SignalType.REDUCE_RISK:
                recommendation = "Risk management signal: Reduce position sizes and tighten stops."
            elif signal == SignalType.INCREASE_RISK:
                recommendation = "Risk management signal: Safe to increase position sizes."
            else:
                recommendation = "Risk management signal: Maintain current risk levels."
        
        else:  # HOLD
            if confidence > 0.7:
                recommendation = "Strong HOLD signal. Market conditions uncertain, maintain current positions."
            else:
                recommendation = "Weak HOLD signal. Monitor closely for changes in market conditions."
        
        # Market regime adjustment
        if market_regime.volatility > 0.3:
            recommendation += " High volatility environment - consider additional risk management."
        elif market_regime.volatility < 0.1:
            recommendation += " Low volatility environment - stable trading conditions."
        
        if len(result.participating_agents) < 5:
            recommendation += " Limited agent participation - consider waiting for broader consensus."
        
        return recommendation
    
    def _create_empty_result(self) -> VotingResult:
        """Bo'sh result yaratish"""
        return VotingResult(
            final_signal=SignalType.HOLD,
            confidence=0.0,
            vote_distribution={},
            confidence_by_type={},
            participating_agents=[],
            total_votes=0,
            method_used=VotingMethod.SIMPLE_MAJORITY,
            timestamp=datetime.now(),
            consensus_strength=0.0,
            recommendation="No signals available for analysis."
        )
    
    def _create_insufficient_participants_result(self, votes: List[Vote]) -> VotingResult:
        """Yetarli ishtirokchi yo'q result yaratish"""
        return VotingResult(
            final_signal=SignalType.HOLD,
            confidence=0.2,
            vote_distribution=Counter(vote.signal_type for vote in votes),
            confidence_by_type={},
            participating_agents=[vote.agent_id for vote in votes],
            total_votes=len(votes),
            method_used=VotingMethod.SIMPLE_MAJORITY,
            timestamp=datetime.now(),
            consensus_strength=0.2,
            recommendation=f"Insufficient participants ({len(votes)} < {self.min_participants}). Wait for more agent signals."
        )
    
    def _get_bayesian_priors(self, market_regime: MarketRegime) -> Dict[SignalType, float]:
        """Bayesian prior probabilities"""
        priors = {
            SignalType.BUY: 0.3,
            SignalType.SELL: 0.3,
            SignalType.HOLD: 0.4
        }
        
        # Adjust based on market regime
        if market_regime.trend == "bullish":
            priors[SignalType.BUY] += 0.1
            priors[SignalType.SELL] -= 0.05
            priors[SignalType.HOLD] -= 0.05
        elif market_regime.trend == "bearish":
            priors[SignalType.SELL] += 0.1
            priors[SignalType.BUY] -= 0.05
            priors[SignalType.HOLD] -= 0.05
        
        # Normalize
        total = sum(priors.values())
        return {k: v / total for k, v in priors.items()}
    
    def _extract_voting_features(self, votes: List[Vote], market_regime: MarketRegime) -> Dict[str, float]:
        """ML uchun xususiyatlarni ajratib olish"""
        features = {}
        
        # Basic statistics
        features['num_votes'] = len(votes)
        features['avg_confidence'] = np.mean([v.confidence for v in votes])
        features['avg_strength'] = np.mean([v.strength for v in votes])
        features['confidence_std'] = np.std([v.confidence for v in votes])
        
        # Signal distribution
        signal_counts = Counter(vote.signal_type for vote in votes)
        features['buy_count'] = signal_counts.get(SignalType.BUY, 0)
        features['sell_count'] = signal_counts.get(SignalType.SELL, 0)
        features['hold_count'] = signal_counts.get(SignalType.HOLD, 0)
        
        # Market features
        features['volatility'] = market_regime.volatility
        features['sentiment'] = market_regime.sentiment
        
        return features
    
    def _get_agent_type_bonus(self, agent_type: str) -> float:
        """Agent type bo'yicha bonus"""
        bonuses = {
            'technical_analysis': 1.0,
            'fundamental_analysis': 1.1,
            'sentiment_analysis': 0.9,
            'quantitative': 1.0,
            'options_flow': 0.8,
            'risk_management': 1.2,  # Always important
            'momentum': 1.0,
            'value': 1.0
        }
        return bonuses.get(agent_type, 1.0)
    
    def _get_market_regime_bonus(self, agent_type: str, market_regime: MarketRegime) -> float:
        """Market regime bo'yicha agent bonus"""
        if market_regime.volatility > 0.3:
            # High volatility benefits
            if agent_type in ['sentiment_analysis', 'options_flow', 'risk_management']:
                return 1.2
            elif agent_type in ['technical_analysis', 'quantitative']:
                return 1.1
        elif market_regime.volatility < 0.1:
            # Low volatility
            if agent_type in ['fundamental_analysis', 'value']:
                return 1.1
            elif agent_type in ['sentiment_analysis', 'options_flow']:
                return 0.9
        
        if market_regime.trend == 'trending':
            if agent_type in ['momentum', 'technical_analysis']:
                return 1.2
        elif market_regime.trend == 'ranging':
            if agent_type in ['value', 'quantitative']:
                return 1.1
        
        return 1.0
    
    def _calculate_recency_factor(self, timestamp: datetime) -> float:
        """Recency factor hisoblash"""
        time_diff = (datetime.now() - timestamp).total_seconds() / 3600  # hours
        return max(0.5, 1.0 - (time_diff / 24))  # Decay over 24 hours
    
    def _get_specialization_factor(self, agent_type: str, market_regime: MarketRegime) -> float:
        """Specialization factor"""
        if agent_type == 'technical_analysis' and market_regime.regime_type == 'trending':
            return 1.2
        elif agent_type == 'fundamental_analysis' and 'earnings' in str(datetime.now().date()):
            return 1.3
        elif agent_type == 'sentiment_analysis' and market_regime.volatility > 0.25:
            return 1.2
        return 1.0
    
    def _get_agent_health_factor(self, agent_id: str) -> float:
        """Agent health factor"""
        agent = self.agent_pool.agents.get(agent_id)
        if not agent:
            return 0.0
        
        if agent.is_healthy():
            return 1.0
        else:
            return 0.5
    
    def get_voting_statistics(self) -> Dict[str, Any]:
        """Voting statistikasi"""
        if not self.voting_history:
            return {"message": "No voting history available"}
        
        recent_results = [r for r in self.voting_history if (datetime.now() - r.timestamp).days <= 30]
        
        stats = {
            "total_votes": len(self.voting_history),
            "recent_votes": len(recent_results),
            "method_usage": Counter(r.method_used.value for r in self.voting_history),
            "signal_distribution": Counter(r.final_signal.value for r in self.voting_history),
            "avg_confidence": np.mean([r.confidence for r in self.voting_history]),
            "consensus_strength": np.mean([r.consensus_strength for r in self.voting_history]),
            "agent_participation": Counter(
                agent for r in self.voting_history for agent in r.participating_agents
            )
        }
        
        return stats

class PerformanceTracker:
    """Voting performance tracker"""
    
    def __init__(self):
        self.results_history: List[VotingResult] = []
        self.outcome_tracking: Dict[str, Dict[str, Any]] = {}
    
    def record_voting_result(self, result: VotingResult):
        """Voting result ni saqlash"""
        self.results_history.append(result)
    
    def track_signal_outcome(self, signal_id: str, outcome: Dict[str, Any]):
        """Signal natijasi monitoring"""
        self.outcome_tracking[signal_id] = outcome
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Performance metrikalari"""
        if not self.results_history:
            return {}
        
        recent_results = [r for r in self.results_history if (datetime.now() - r.timestamp).days <= 30]
        
        return {
            "total_votes": len(self.results_history),
            "recent_votes": len(recent_results),
            "accuracy": self._calculate_accuracy(recent_results),
            "confidence_calibration": self._calculate_confidence_calibration(recent_results),
            "consistency": self._calculate_consistency(recent_results)
        }
    
    def _calculate_accuracy(self, results: List[VotingResult]) -> float:
        """Aniqlik hisoblash"""
        correct_predictions = 0
        total_predictions = 0
        
        for result in results:
            outcome = self.outcome_tracking.get(result.timestamp.isoformat())
            if outcome:
                total_predictions += 1
                # Simplified accuracy calculation
                if outcome.get('profit', 0) > 0:
                    correct_predictions += 1
        
        return correct_predictions / total_predictions if total_predictions > 0 else 0
    
    def _calculate_confidence_calibration(self, results: List[VotingResult]) -> float:
        """Confidence calibration"""
        if not results:
            return 0
        
        # Brier score like calculation
        squared_errors = []
        for result in results:
            outcome = self.outcome_tracking.get(result.timestamp.isoformat())
            if outcome:
                actual = 1 if outcome.get('profit', 0) > 0 else 0
                predicted_confidence = result.confidence
                squared_errors.append((actual - predicted_confidence) ** 2)
        
        return 1 - np.mean(squared_errors) if squared_errors else 0
    
    def _calculate_consistency(self, results: List[VotingResult]) -> float:
        """Konsistentlik hisoblash"""
        if len(results) < 2:
            return 0
        
        # Signal type changes over time
        signal_changes = sum(
            1 for i in range(1, len(results))
            if results[i].final_signal != results[i-1].final_signal
        )
        
        return 1 - (signal_changes / (len(results) - 1))

class MarketRegimeDetector:
    """Market regime detector"""
    
    def __init__(self):
        self.regime_history: List[MarketRegime] = []
    
    def detect_current_regime(self, market_data: Dict[str, Any]) -> MarketRegime:
        """Joriy market regime ni aniqlash"""
        try:
            # Simple regime detection logic
            volatility = market_data.get('volatility', 0.2)
            price_data = market_data.get('price_data', {})
            sentiment = market_data.get('sentiment', 0.5)
            
            # Determine regime type
            if volatility > 0.3:
                regime_type = "high_volatility"
            elif volatility < 0.1:
                regime_type = "low_volatility"
            else:
                regime_type = "normal"
            
            # Determine trend
            close_prices = price_data.get('close', [])
            if len(close_prices) > 20:
                recent_trend = np.mean(np.diff(close_prices[-20:]))
                if recent_trend > 0.02:
                    trend = "bullish"
                elif recent_trend < -0.02:
                    trend = "bearish"
                else:
                    trend = "sideways"
            else:
                trend = "unknown"
            
            # Volume and sentiment
            volume = market_data.get('volume', 1.0)
            
            current_regime = MarketRegime(
                regime_type=regime_type,
                volatility=volatility,
                trend=trend,
                volume=volume,
                sentiment=sentiment,
                timestamp=datetime.now()
            )
            
            self.regime_history.append(current_regime)
            return current_regime
            
        except Exception as e:
            logger.error(f"Error detecting market regime: {str(e)}")
            return MarketRegime(
                regime_type="unknown",
                volatility=0.2,
                trend="unknown",
                volume=1.0,
                sentiment=0.5,
                timestamp=datetime.now()
            )

# Test va demo funksiyalar
async def demo_signal_voting():
    """Signal voting demo"""
    from agent_pool import demo_agent_pool
    
    print("\n=== AI Signal Voting System Demo ===")
    
    # Agent pool yaratish
    agent_pool, signals = await demo_agent_pool()
    
    # Signal voter yaratish
    voter_config = {
        "min_consensus_threshold": 0.6,
        "min_participants": 3,
        "confidence_threshold": 0.5,
        "diversity_bonus": 0.1
    }
    
    voter = SignalVoter(agent_pool, voter_config)
    
    # Market data
    market_data = {
        "volatility": 0.25,
        "sentiment": 0.7,
        "price_data": {"close": [100, 101, 102, 103, 104]},
        "volume": 1.2,
        "risk_metrics": {"portfolio_risk": 0.6}
    }
    
    market_regime = voter.market_regime_detector.detect_current_regime(market_data)
    
    # Different voting methods test
    methods = [
        VotingMethod.SIMPLE_MAJORITY,
        VotingMethod.WEIGHTED_VOTING,
        VotingMethod.CONFIDENCE_BASED,
        VotingMethod.ENSEMBLE_METHODS
    ]
    
    for method in methods:
        print(f"\n--- {method.value.upper()} ---")
        result = await voter.process_voting(signals, market_data, market_regime, method)
        
        print(f"Final Signal: {result.final_signal.value}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Consensus: {result.consensus_strength:.2f}")
        print(f"Participants: {result.total_votes}")
        print(f"Recommendation: {result.recommendation}")
        
        if result.risk_adjusted_signal:
            print(f"Risk Adjusted: {result.risk_adjusted_signal.value}")
    
    # Statistics
    stats = voter.get_voting_statistics()
    print(f"\n=== Voting Statistics ===")
    print(json.dumps(stats, indent=2, default=str))
    
    return voter

if __name__ == "__main__":
    # Demo run
    asyncio.run(demo_signal_voting())