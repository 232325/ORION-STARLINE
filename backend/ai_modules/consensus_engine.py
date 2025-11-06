"""
Consensus Engine - AI agentlarning konsensus yaratish mexanizmi
"""

import asyncio
import logging
import time
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
import json
from collections import defaultdict, deque
import math

from signal_voter import SignalVoter, VotingResult, SignalType, Vote
from agent_pool import AgentPool, AgentType, MarketRegime

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConsensusType(Enum):
    """Konsensus turlari"""
    IMMEDIATE = "immediate"  # Real-time consensus
    TIME_BASED = "time_based"  # Time window consensus
    THRESHOLD_BASED = "threshold_based"  # Confidence threshold consensus
    BATCHED = "batched"  # Batch processing consensus
    ADAPTIVE = "adaptive"  # Adaptive consensus based on market conditions

class ConsensusStatus(Enum):
    """Konsensus holatlari"""
    PENDING = "pending"
    COLLECTING = "collecting"
    CONSENSUS_REACHED = "consensus_reached"
    NO_CONSENSUS = "no_consensus"
    TIMEOUT = "timeout"
    EXPIRED = "expired"

class ConsensusMetric(Enum):
    """Konsensus metrikalari"""
    AGREEMENT_RATIO = "agreement_ratio"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    PERFORMANCE_ADJUSTED = "performance_adjusted"
    DIVERSITY_PENALTY = "diversity_penalty"
    TEMPORAL_STABILITY = "temporal_stability"

@dataclass
class ConsensusSignal:
    """Konsensus signal"""
    signal_id: str
    asset_symbol: str
    signal_type: SignalType
    confidence: float
    strength: float
    consensus_method: ConsensusType
    participating_agents: List[str]
    vote_distribution: Dict[SignalType, int]
    confidence_by_agent: Dict[str, float]
    performance_weights: Dict[str, float]
    temporal_factor: float
    market_regime: MarketRegime
    timestamp: datetime
    expiry_time: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Dict ga konvertatsiya"""
        return {
            "signal_id": self.signal_id,
            "asset_symbol": self.asset_symbol,
            "signal_type": self.signal_type.value,
            "confidence": self.confidence,
            "strength": self.strength,
            "consensus_method": self.consensus_method.value,
            "participating_agents": self.participating_agents,
            "vote_distribution": {k.value: v for k, v in self.vote_distribution.items()},
            "confidence_by_agent": self.confidence_by_agent,
            "performance_weights": self.performance_weights,
            "temporal_factor": self.temporal_factor,
            "timestamp": self.timestamp.isoformat(),
            "expiry_time": self.expiry_time.isoformat()
        }

@dataclass
class ConsensusSession:
    """Konsensus sessiya"""
    session_id: str
    consensus_type: ConsensusType
    asset_symbol: str
    status: ConsensusStatus
    created_at: datetime
    timeout_duration: timedelta
    min_participants: int
    confidence_threshold: float
    signals_collected: List[Vote] = field(default_factory=list)
    consensus_result: Optional[ConsensusSignal] = None
    
    def is_expired(self) -> bool:
        """Sessiya muddati o'tgan"""
        return datetime.now() > self.created_at + self.timeout_duration
    
    def add_signal(self, vote: Vote) -> bool:
        """Sessiyaga signal qo'shish"""
        if self.status in [ConsensusStatus.CONSENSUS_REACHED, ConsensusStatus.NO_CONSENSUS, ConsensusStatus.EXPIRED]:
            return False
        
        # Agent already participated check
        for existing_vote in self.signals_collected:
            if existing_vote.agent_id == vote.agent_id:
                return False
        
        self.signals_collected.append(vote)
        
        # Check if we can reach consensus
        if len(self.signals_collected) >= self.min_participants:
            self.status = ConsensusStatus.COLLECTING
        
        return True
    
    def can_reach_consensus(self) -> bool:
        """Konsensusga erishish imkoniyati"""
        if len(self.signals_collected) < self.min_participants:
            return False
        
        if self.confidence_threshold > 0:
            return self._calculate_estimated_confidence() >= self.confidence_threshold
        
        return True
    
    def _calculate_estimated_confidence(self) -> float:
        """Estimatsiyalash confidence"""
        if not self.signals_collected:
            return 0.0
        
        # Simple average confidence
        return np.mean([vote.confidence for vote in self.signals_collected])

class ConsensusEngine:
    """Konsensus Engine"""
    
    def __init__(self, agent_pool: AgentPool, signal_voter: SignalVoter, config: Dict[str, Any]):
        self.agent_pool = agent_pool
        self.signal_voter = signal_voter
        self.config = config
        
        # Active sessions
        self.active_sessions: Dict[str, ConsensusSession] = {}
        self.completed_sessions: List[ConsensusSession] = []
        
        # Consensus tracking
        self.consensus_history: List[ConsensusSignal] = []
        self.performance_tracker = ConsensusPerformanceTracker()
        
        # Configuration
        self.default_timeout = config.get('default_timeout', timedelta(minutes=5))
        self.default_min_participants = config.get('default_min_participants', 3)
        self.default_confidence_threshold = config.get('default_confidence_threshold', 0.6)
        self.max_session_age = config.get('max_session_age', timedelta(hours=1))
        
        # Adaptive parameters
        self.adaptive_threshold = config.get('adaptive_threshold', True)
        self.temporal_smoothing = config.get('temporal_smoothing', True)
        self.diversity_bonus = config.get('diversity_bonus', 0.1)
        
    async def create_consensus_session(self, 
                                     asset_symbol: str,
                                     consensus_type: ConsensusType = ConsensusType.ADAPTIVE,
                                     timeout_duration: Optional[timedelta] = None,
                                     min_participants: Optional[int] = None,
                                     confidence_threshold: Optional[float] = None,
                                     market_data: Optional[Dict[str, Any]] = None) -> str:
        """Konsensus sessiya yaratish"""
        
        session_id = f"{asset_symbol}_{int(time.time())}_{len(self.active_sessions)}"
        
        # Adaptive parameter calculation
        if consensus_type == ConsensusType.ADAPTIVE:
            consensus_type = self._determine_optimal_consensus_type(market_data)
        
        # Adaptive timeout
        if timeout_duration is None:
            timeout_duration = self._calculate_adaptive_timeout(market_data)
        
        # Adaptive min participants
        if min_participants is None:
            min_participants = self._calculate_adaptive_min_participants(market_data)
        
        # Adaptive confidence threshold
        if confidence_threshold is None:
            confidence_threshold = self._calculate_adaptive_confidence_threshold(market_data)
        
        session = ConsensusSession(
            session_id=session_id,
            consensus_type=consensus_type,
            asset_symbol=asset_symbol,
            status=ConsensusStatus.PENDING,
            created_at=datetime.now(),
            timeout_duration=timeout_duration,
            min_participants=min_participants,
            confidence_threshold=confidence_threshold
        )
        
        self.active_sessions[session_id] = session
        
        logger.info(f"Created consensus session {session_id} for {asset_symbol} "
                   f"type: {consensus_type.value}, timeout: {timeout_duration}")
        
        return session_id
    
    async def submit_signal_to_session(self, session_id: str, vote: Vote) -> bool:
        """Sessiyaga signal jo'natish"""
        session = self.active_sessions.get(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return False
        
        success = session.add_signal(vote)
        if success:
            logger.info(f"Added signal from agent {vote.agent_id} to session {session_id}")
            
            # Check if we can finalize consensus
            if session.can_reach_consensus():
                await self._finalize_consensus(session_id)
        
        return success
    
    async def _finalize_consensus(self, session_id: str) -> Optional[ConsensusSignal]:
        """Konsensusni yakunlash"""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        try:
            # Use signal voter to process the votes
            market_data = self._get_market_data_for_session(session)
            market_regime = self._detect_market_regime(market_data)
            
            # Convert votes to signal format
            signals = [self._vote_to_signal(vote) for vote in session.signals_collected]
            
            # Process voting
            result = await self.signal_voter.process_voting(
                signals=signals,
                market_data=market_data,
                market_regime=market_regime,
                method=self._get_voting_method_for_consensus(session.consensus_type)
            )
            
            # Create consensus signal
            consensus_signal = await self._create_consensus_signal(session, result, market_regime)
            
            # Update session
            session.status = ConsensusStatus.CONSENSUS_REACHED
            session.consensus_result = consensus_signal
            session.expiry_time = datetime.now() + self._calculate_signal_expiry(session.consensus_type)
            
            # Move to completed
            self.completed_sessions.append(session)
            del self.active_sessions[session_id]
            
            # Add to history
            self.consensus_history.append(consensus_signal)
            
            # Performance tracking
            self.performance_tracker.record_consensus(consensus_signal)
            
            logger.info(f"Consensus finalized for session {session_id}: "
                       f"{consensus_signal.signal_type.value} with {consensus_signal.confidence:.2f} confidence")
            
            return consensus_signal
            
        except Exception as e:
            logger.error(f"Error finalizing consensus for session {session_id}: {str(e)}")
            session.status = ConsensusStatus.NO_CONSENSUS
            return None
    
    async def process_real_time_consensus(self, market_data: Dict[str, Any], asset_symbol: str) -> Optional[ConsensusSignal]:
        """Real-time konsensus qayta ishlash"""
        # Get all healthy agents
        healthy_agents = [agent for agent in self.agent_pool.agents.values() if agent.is_healthy()]
        
        if len(healthy_agents) < self.default_min_participants:
            logger.warning(f"Insufficient healthy agents for real-time consensus: {len(healthy_agents)}")
            return None
        
        # Collect signals from all agents
        market_regime = self._detect_market_regime(market_data)
        signals = await self.agent_pool.collect_signals(market_data, market_regime)
        
        if not signals:
            return None
        
        # Quick consensus processing
        return await self._quick_consensus(signals, market_data, market_regime, asset_symbol)
    
    async def _quick_consensus(self, signals: List[Dict[str, Any]], 
                             market_data: Dict[str, Any], 
                             market_regime: MarketRegime, 
                             asset_symbol: str) -> Optional[ConsensusSignal]:
        """Tezkor konsensus"""
        if len(signals) < 2:
            return None
        
        # Simple majority with confidence weighting
        signal_votes = defaultdict(float)
        total_weight = 0
        
        for signal in signals:
            agent = self.agent_pool.agents.get(signal['agent_id'])
            if not agent:
                continue
            
            # Weight by confidence and performance
            weight = signal['confidence'] * (1 + agent.performance.accuracy)
            signal_type = SignalType(signal['signal_type'])
            signal_votes[signal_type] += weight
            total_weight += weight
        
        if total_weight == 0:
            return None
        
        # Find winning signal
        winning_signal = max(signal_votes.items(), key=lambda x: x[1])
        signal_type = winning_signal[0]
        confidence = winning_signal[1] / total_weight
        
        # Create consensus signal
        consensus_signal = ConsensusSignal(
            signal_id=f"realtime_{asset_symbol}_{int(time.time())}",
            asset_symbol=asset_symbol,
            signal_type=signal_type,
            confidence=confidence,
            strength=confidence,
            consensus_method=ConsensusType.IMMEDIATE,
            participating_agents=[s['agent_id'] for s in signals],
            vote_distribution=Counter(SignalType(s['signal_type']) for s in signals),
            confidence_by_agent={s['agent_id']: s['confidence'] for s in signals},
            performance_weights={s['agent_id']: self.agent_pool.agents.get(s['agent_id']).performance.accuracy 
                               for s in signals if self.agent_pool.agents.get(s['agent_id'])},
            temporal_factor=1.0,
            market_regime=market_regime,
            timestamp=datetime.now(),
            expiry_time=datetime.now() + timedelta(minutes=5)
        )
        
        self.consensus_history.append(consensus_signal)
        return consensus_signal
    
    def _determine_optimal_consensus_type(self, market_data: Optional[Dict[str, Any]]) -> ConsensusType:
        """Optimal konsensus turini aniqlash"""
        if not market_data:
            return ConsensusType.THRESHOLD_BASED
        
        volatility = market_data.get('volatility', 0.2)
        urgency = market_data.get('urgency', 0.5)
        market_hours = self._is_market_hours()
        
        # High volatility -> Immediate consensus
        if volatility > 0.3:
            return ConsensusType.IMMEDIATE
        
        # High urgency -> Time-based
        if urgency > 0.8:
            return ConsensusType.TIME_BASED
        
        # Market hours -> Batched for efficiency
        if market_hours:
            return ConsensusType.BATCHED
        
        # Default adaptive
        return ConsensusType.ADAPTIVE
    
    def _calculate_adaptive_timeout(self, market_data: Optional[Dict[str, Any]]) -> timedelta:
        """Adaptiv timeout hisoblash"""
        base_timeout = self.default_timeout
        
        if not market_data:
            return base_timeout
        
        volatility = market_data.get('volatility', 0.2)
        urgency = market_data.get('urgency', 0.5)
        
        # High volatility requires faster decisions
        if volatility > 0.3:
            return timedelta(minutes=2)
        
        # High urgency
        if urgency > 0.8:
            return timedelta(minutes=3)
        
        return base_timeout
    
    def _calculate_adaptive_min_participants(self, market_data: Optional[Dict[str, Any]]) -> int:
        """Adaptiv minimum ishtirokchilar soni"""
        base_min = self.default_min_participants
        
        if not market_data:
            return base_min
        
        volatility = market_data.get('volatility', 0.2)
        importance = market_data.get('importance', 0.5)
        
        # High volatility or importance needs more consensus
        if volatility > 0.3 or importance > 0.8:
            return base_min + 1
        
        return base_min
    
    def _calculate_adaptive_confidence_threshold(self, market_data: Optional[Dict[str, Any]]) -> float:
        """Adaptiv confidence threshold"""
        base_threshold = self.default_confidence_threshold
        
        if not market_data:
            return base_threshold
        
        volatility = market_data.get('volatility', 0.2)
        risk_tolerance = market_data.get('risk_tolerance', 0.5)
        
        # High volatility requires higher confidence
        if volatility > 0.3:
            return min(base_threshold + 0.1, 0.9)
        
        # High risk tolerance allows lower confidence
        if risk_tolerance > 0.7:
            return max(base_threshold - 0.1, 0.4)
        
        return base_threshold
    
    def _is_market_hours(self) -> bool:
        """Market soatlari tekshirish (simplified)"""
        now = datetime.now()
        # Assume US market hours: 9:30 AM - 4:00 PM ET
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        return market_open <= now <= market_close
    
    def _get_market_data_for_session(self, session: ConsensusSession) -> Dict[str, Any]:
        """Sessiya uchun market data olish"""
        # In real implementation, this would fetch current market data
        # For demo, return mock data
        return {
            "volatility": 0.25,
            "sentiment": 0.7,
            "volume": 1.2,
            "urgency": 0.6,
            "risk_tolerance": 0.5
        }
    
    def _detect_market_regime(self, market_data: Dict[str, Any]) -> MarketRegime:
        """Market regime aniqlash"""
        return self.signal_voter.market_regime_detector.detect_current_regime(market_data)
    
    def _get_voting_method_for_consensus(self, consensus_type: ConsensusType):
        """Konsensus turiga mos voting method"""
        from signal_voter import VotingMethod
        
        if consensus_type == ConsensusType.IMMEDIATE:
            return VotingMethod.SIMPLE_MAJORITY
        elif consensus_type == ConsensusType.TIME_BASED:
            return VotingMethod.WEIGHTED_VOTING
        elif consensus_type == ConsensusType.THRESHOLD_BASED:
            return VotingMethod.CONFIDENCE_BASED
        elif consensus_type == ConsensusType.BATCHED:
            return VotingMethod.ENSEMBLE_METHODS
        else:  # ADAPTIVE
            return VotingMethod.DYNAMIC_WEIGHTS
    
    def _vote_to_signal(self, vote: Vote) -> Dict[str, Any]:
        """Vote ni signal format ga konvertatsiya"""
        return {
            "agent_id": vote.agent_id,
            "agent_type": vote.agent_type,
            "signal_type": vote.signal_type.value,
            "strength": vote.strength,
            "confidence": vote.confidence,
            "timestamp": vote.timestamp.isoformat(),
            "weights": vote.weights,
            "reasoning": vote.reasoning
        }
    
    async def _create_consensus_signal(self, session: ConsensusSession, 
                                     result: VotingResult, 
                                     market_regime: MarketRegime) -> ConsensusSignal:
        """Konsensus signal yaratish"""
        # Calculate temporal factor
        temporal_factor = self._calculate_temporal_factor(session)
        
        # Calculate performance weights
        performance_weights = {}
        for agent_id in result.participating_agents:
            agent = self.agent_pool.agents.get(agent_id)
            if agent:
                performance_weights[agent_id] = agent.performance.accuracy
        
        # Calculate confidence by agent
        confidence_by_agent = {}
        for vote in session.signals_collected:
            confidence_by_agent[vote.agent_id] = vote.confidence
        
        consensus_signal = ConsensusSignal(
            signal_id=f"consensus_{session.session_id}_{int(time.time())}",
            asset_symbol=session.asset_symbol,
            signal_type=result.final_signal,
            confidence=result.confidence,
            strength=result.consensus_strength,
            consensus_method=session.consensus_type,
            participating_agents=result.participating_agents,
            vote_distribution=result.vote_distribution,
            confidence_by_agent=confidence_by_agent,
            performance_weights=performance_weights,
            temporal_factor=temporal_factor,
            market_regime=market_regime,
            timestamp=datetime.now(),
            expiry_time=datetime.now() + self._calculate_signal_expiry(session.consensus_type)
        )
        
        return consensus_signal
    
    def _calculate_temporal_factor(self, session: ConsensusSession) -> float:
        """Vaqt omili hisoblash"""
        if not self.temporal_smoothing:
            return 1.0
        
        session_duration = datetime.now() - session.created_at
        max_duration = session.timeout_duration
        
        # Longer sessions get lower temporal factor
        time_ratio = session_duration.total_seconds() / max_duration.total_seconds()
        temporal_factor = max(0.5, 1.0 - (time_ratio * 0.3))
        
        return temporal_factor
    
    def _calculate_signal_expiry(self, consensus_type: ConsensusType) -> timedelta:
        """Signal muddati hisoblash"""
        if consensus_type == ConsensusType.IMMEDIATE:
            return timedelta(minutes=2)
        elif consensus_type == ConsensusType.TIME_BASED:
            return timedelta(minutes=10)
        elif consensus_type == ConsensusType.THRESHOLD_BASED:
            return timedelta(minutes=15)
        elif consensus_type == ConsensusType.BATCHED:
            return timedelta(minutes=30)
        else:  # ADAPTIVE
            return timedelta(minutes=10)
    
    async def cleanup_expired_sessions(self):
        """Muddati o'tgan sessiyalarni tozalash"""
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if session.is_expired():
                session.status = ConsensusStatus.TIMEOUT
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            session = self.active_sessions.pop(session_id)
            self.completed_sessions.append(session)
            logger.info(f"Expired session {session_id}")
    
    def get_active_consensus_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Faol konsensus sessiyalar"""
        return {
            session_id: {
                "session_id": session.session_id,
                "asset_symbol": session.asset_symbol,
                "consensus_type": session.consensus_type.value,
                "status": session.status.value,
                "signals_collected": len(session.signals_collected),
                "min_participants": session.min_participants,
                "created_at": session.created_at.isoformat(),
                "time_remaining": str(session.created_at + session.timeout_duration - datetime.now())
            }
            for session_id, session in self.active_sessions.items()
        }
    
    def get_recent_consensus_signals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Oxirgi konsensus signallar"""
        recent_signals = sorted(
            self.consensus_history,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]
        
        return [signal.to_dict() for signal in recent_signals]
    
    def get_consensus_statistics(self) -> Dict[str, Any]:
        """Konsensus statistikasi"""
        total_sessions = len(self.completed_sessions)
        active_sessions = len(self.active_sessions)
        
        if total_sessions == 0:
            return {
                "total_sessions": 0,
                "active_sessions": active_sessions,
                "message": "No completed sessions"
            }
        
        # Calculate success rate
        successful_sessions = len([s for s in self.completed_sessions 
                                 if s.status == ConsensusStatus.CONSENSUS_REACHED])
        success_rate = successful_sessions / total_sessions if total_sessions > 0 else 0
        
        # Consensus type distribution
        type_distribution = defaultdict(int)
        for session in self.completed_sessions:
            type_distribution[session.consensus_type.value] += 1
        
        # Average confidence
        avg_confidence = np.mean([s.consensus_result.confidence for s in self.completed_sessions 
                                 if s.consensus_result]) if self.completed_sessions else 0
        
        # Agent participation
        agent_participation = defaultdict(int)
        for session in self.completed_sessions:
            for vote in session.signals_collected:
                agent_participation[vote.agent_id] += 1
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "success_rate": success_rate,
            "consensus_type_distribution": dict(type_distribution),
            "average_confidence": avg_confidence,
            "agent_participation": dict(agent_participation),
            "performance_metrics": self.performance_tracker.get_metrics()
        }

class ConsensusPerformanceTracker:
    """Konsensus performance tracker"""
    
    def __init__(self):
        self.accuracy_history: List[float] = []
        self.confidence_calibration: List[float] = []
        self.response_times: List[float] = []
        self.participant_counts: List[int] = []
    
    def record_consensus(self, consensus_signal: ConsensusSignal):
        """Konsensus result ni saqlash"""
        # In real implementation, these would be calculated based on actual outcomes
        # For demo, add some mock data
        self.accuracy_history.append(consensus_signal.confidence)  # Simplified
        self.confidence_calibration.append(consensus_signal.confidence)
        self.response_times.append(2.5)  # Mock response time
        self.participant_counts.append(len(consensus_signal.participating_agents))
        
        # Keep only last 100 entries
        max_history = 100
        for history_list in [self.accuracy_history, self.confidence_calibration, 
                           self.response_times, self.participant_counts]:
            if len(history_list) > max_history:
                del history_list[0]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Performance metrikalari"""
        if not self.accuracy_history:
            return {}
        
        return {
            "average_accuracy": np.mean(self.accuracy_history),
            "accuracy_std": np.std(self.accuracy_history),
            "average_confidence": np.mean(self.confidence_calibration),
            "confidence_calibration": 1 - np.mean([abs(c - 0.8)**2 for c in self.confidence_calibration]),  # Simplified
            "average_response_time": np.mean(self.response_times),
            "avg_participants": np.mean(self.participant_counts),
            "consensus_rate": len([c for c in self.confidence_calibration if c > 0.6]) / len(self.confidence_calibration)
        }

from collections import Counter

# Test va demo funksiyalar
async def demo_consensus_engine():
    """Consensus engine demo"""
    from agent_pool import demo_agent_pool
    from signal_voter import demo_signal_voting
    
    print("\n=== Consensus Engine Demo ===")
    
    # Setup components
    agent_pool, signals = await demo_agent_pool()
    
    voter_config = {"min_consensus_threshold": 0.6, "min_participants": 3}
    signal_voter = await demo_signal_voting()
    
    # Create consensus engine
    consensus_config = {
        "default_timeout": timedelta(minutes=2),
        "default_min_participants": 3,
        "default_confidence_threshold": 0.6,
        "adaptive_threshold": True,
        "temporal_smoothing": True
    }
    
    engine = ConsensusEngine(agent_pool, signal_voter, consensus_config)
    
    # Demo different consensus types
    market_data = {
        "volatility": 0.25,
        "sentiment": 0.7,
        "volume": 1.2,
        "urgency": 0.6,
        "risk_tolerance": 0.5
    }
    
    # 1. Real-time consensus
    print("\n--- Real-time Consensus ---")
    realtime_signal = await engine.process_real_time_consensus(market_data, "AAPL")
    if realtime_signal:
        print(f"Real-time signal: {realtime_signal.signal_type.value} "
              f"({realtime_signal.confidence:.2f} confidence)")
    
    # 2. Session-based consensus
    print("\n--- Session-based Consensus ---")
    session_id = await engine.create_consensus_session(
        asset_symbol="GOOGL",
        consensus_type=ConsensusType.THRESHOLD_BASED,
        confidence_threshold=0.7
    )
    
    # Submit signals to session
    for signal in signals[:3]:  # Take first 3 signals
        vote = Vote(
            agent_id=signal['agent_id'],
            agent_type=signal['agent_type'],
            signal_type=SignalType(signal['signal_type']),
            strength=signal['strength'],
            confidence=signal['confidence'],
            timestamp=datetime.fromisoformat(signal['timestamp']),
            weights=signal.get('weights', {}),
            reasoning=signal.get('reasoning', ''),
            individual_performance=0.8  # Mock performance
        )
        engine.submit_signal_to_session(session_id, vote)
    
    # Wait a bit for consensus to finalize
    await asyncio.sleep(0.1)
    
    # Check for final consensus
    session = engine.active_sessions.get(session_id)
    if session and session.consensus_result:
        result = session.consensus_result
        print(f"Session consensus: {result.signal_type.value} "
              f"({result.confidence:.2f} confidence)")
        print(f"Participants: {len(result.participating_agents)}")
    
    # 3. Statistics
    print("\n--- Consensus Statistics ---")
    stats = engine.get_consensus_statistics()
    print(json.dumps(stats, indent=2, default=str))
    
    # 4. Active sessions
    print("\n--- Active Sessions ---")
    active_sessions = engine.get_active_consensus_sessions()
    print(json.dumps(active_sessions, indent=2, default=str))
    
    return engine

if __name__ == "__main__":
    # Demo run
    asyncio.run(demo_consensus_engine())