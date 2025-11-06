"""
Personality Analyzer Module
===========================

Ushbu modul murakkab shaxsiyat tahlilini, xulq-atvor naqshlarini aniqlashni
va machine learning asosida shaxsiyatni tasniflashni amalga oshiradi.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
import statistics
from collections import defaultdict, Counter

# Advanced personality analysis imports
try:
    from sklearn.cluster import KMeans
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("Machine learning kutubxonalari topilmadi. Ba'zi xususiyatlar cheklangan.")

from trading_personality import (
    TradingPersonalityType, RiskTolerance, PersonalityProfile, 
    TradingPersonalityEngine
)

class EmotionalState(Enum):
    """Emotional holatlar"""
    CALM = "calm"
    FOCUSED = "focused"
    EXCITED = "excited"
    ANXIOUS = "anxious"
    FRUSTRATED = "frustrated"
    CONFIDENT = "confident"

class SocialBehavior(Enum):
    """Ijtimoiy xulq-atvor"""
    INDIVIDUAL = "individual"
    LEARNER = "learner"
    COLLABORATOR = "collaborator"
    LEADER = "leader"
    FOLLOWER = "follower"

class LearningStyle(Enum):
    """O'rganish uslubi"""
    VISUAL = "visual"
    AUDITORY = "auditory" 
    KINESTHETIC = "kinesthetic"
    ANALYTICAL = "analytical"
    PRACTICAL = "practical"

@dataclass
class BehavioralPattern:
    """Xulq-atvor naqshi"""
    pattern_type: str
    frequency: float
    intensity: float
    duration: float  # kunlarda
    context: str
    correlation_score: float
    confidence: float

@dataclass
class SocialProfile:
    """Ijtimoiy profil"""
    trader_id: str
    social_behavior: SocialBehavior
    influence_score: float
    collaboration_preference: float
    learning_from_others: float
    leadership_ tendency: float
    network_size: int
    activity_level: float
    community_contribution: float

@dataclass
class AdvancedPersonality:
    """Kengaytirilgan shaxsiyat profili"""
    # Asosiy profil
    base_profile: PersonalityProfile
    
    # Qo'shimcha tahlillar
    emotional_patterns: List[BehavioralPattern]
    decision_patterns: List[BehavioralPattern]
    learning_patterns: List[BehavioralPattern]
    
    # Ijtimoiy profil
    social_profile: SocialProfile
    
    # Machine learning natijalari
    personality_vector: np.ndarray
    confidence_score: float
    cluster_id: Optional[int] = None
    
    # Adaptiv parametrlar
    adaptation_rate: float = 0.1
    last_updated: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'base_profile': self.base_profile.to_dict(),
            'emotional_patterns': [
                {
                    'pattern_type': p.pattern_type,
                    'frequency': p.frequency,
                    'intensity': p.intensity,
                    'duration': p.duration,
                    'context': p.context,
                    'correlation_score': p.correlation_score,
                    'confidence': p.confidence
                } for p in self.emotional_patterns
            ],
            'decision_patterns': [
                {
                    'pattern_type': p.pattern_type,
                    'frequency': p.frequency,
                    'intensity': p.intensity,
                    'duration': p.duration,
                    'context': p.context,
                    'correlation_score': p.correlation_score,
                    'confidence': p.confidence
                } for p in self.decision_patterns
            ],
            'learning_patterns': [
                {
                    'pattern_type': p.pattern_type,
                    'frequency': p.frequency,
                    'intensity': p.intensity,
                    'duration': p.duration,
                    'context': p.context,
                    'correlation_score': p.correlation_score,
                    'confidence': p.confidence
                } for p in self.learning_patterns
            ],
            'social_profile': {
                'trader_id': self.social_profile.trader_id,
                'social_behavior': self.social_profile.social_behavior.value,
                'influence_score': self.social_profile.influence_score,
                'collaboration_preference': self.social_profile.collaboration_preference,
                'learning_from_others': self.social_profile.learning_from_others,
                'leadership_tendency': self.social_profile.leadership_tendency,
                'network_size': self.social_profile.network_size,
                'activity_level': self.social_profile.activity_level,
                'community_contribution': self.social_profile.community_contribution
            },
            'personality_vector': self.personality_vector.tolist() if self.personality_vector is not None else None,
            'confidence_score': self.confidence_score,
            'cluster_id': self.cluster_id,
            'adaptation_rate': self.adaptation_rate,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class PersonalityAnalyzer:
    """
    Advanced Personality Analysis Engine
    ===================================
    
    Machine learning va behavioral analysis asosida
    murakkab shaxsiyat tahlili
    """
    
    def __init__(self, data_dir: str = "/workspace/orion-starline/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # ML models
        self.clustering_model = None
        self.classification_model = None
        self.scaler = None
        
        # Data storage
        self.advanced_profiles_path = self.data_dir / "advanced_profiles.json"
        self.behavioral_data_path = self.data_dir / "behavioral_data.json"
        self.advanced_profiles = self._load_advanced_profiles()
        
        # Feature dimensions
        self.feature_dimensions = 20
        self.personality_features = self._define_personality_features()
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # ML modellarni o'qitish
        if ML_AVAILABLE:
            self._initialize_ml_models()
    
    def _define_personality_features(self) -> List[str]:
        """Shaxsiyat xususiyatlari ro'yxati"""
        return [
            # Trading metrics (0-6)
            "trading_frequency", "avg_holding_time", "win_rate", 
            "sharpe_ratio", "max_drawdown", "profit_factor", "consistency",
            
            # Risk metrics (7-9)
            "risk_tolerance_score", "position_sizing", "leverage_usage",
            
            # Time preferences (10-12)
            "timeframe_preference", "trading_hours", "decision_speed",
            
            # Behavioral metrics (13-16)
            "emotional_stability", "stress_response", "learning_style_score", "adaptability",
            
            # Social metrics (17-19)
            "collaboration_score", "influence_score", "community_participation"
        ]
    
    def _load_advanced_profiles(self) -> Dict[str, AdvancedPersonality]:
        """Kengaytirilgan profillarni yuklash"""
        if self.advanced_profiles_path.exists():
            try:
                with open(self.advanced_profiles_path, 'r') as f:
                    data = json.load(f)
                    profiles = {}
                    for trader_id, profile_data in data.items():
                        # Base profile qurish
                        base_data = profile_data['base_profile']
                        from trading_personality import create_sample_profile
                        base_profile = create_sample_profile(
                            base_data['trader_id'], 
                            base_data['personality_type']
                        )
                        
                        # Qo'shimcha fieldlarni yangilash
                        base_profile.risk_tolerance = RiskTolerance(base_data['risk_tolerance'])
                        base_profile.avg_holding_time = base_data['avg_holding_time']
                        base_profile.emotional_score = base_data['emotional_score']
                        
                        # Behavioral patterns
                        emotional_patterns = []
                        for p in profile_data['emotional_patterns']:
                            emotional_patterns.append(BehavioralPattern(
                                pattern_type=p['pattern_type'],
                                frequency=p['frequency'],
                                intensity=p['intensity'],
                                duration=p['duration'],
                                context=p['context'],
                                correlation_score=p['correlation_score'],
                                confidence=p['confidence']
                            ))
                        
                        decision_patterns = []
                        for p in profile_data['decision_patterns']:
                            decision_patterns.append(BehavioralPattern(
                                pattern_type=p['pattern_type'],
                                frequency=p['frequency'],
                                intensity=p['intensity'],
                                duration=p['duration'],
                                context=p['context'],
                                correlation_score=p['correlation_score'],
                                confidence=p['confidence']
                            ))
                        
                        learning_patterns = []
                        for p in profile_data['learning_patterns']:
                            learning_patterns.append(BehavioralPattern(
                                pattern_type=p['pattern_type'],
                                frequency=p['frequency'],
                                intensity=p['intensity'],
                                duration=p['duration'],
                                context=p['context'],
                                correlation_score=p['correlation_score'],
                                confidence=p['confidence']
                            ))
                        
                        # Social profile
                        social_data = profile_data['social_profile']
                        social_profile = SocialProfile(
                            trader_id=trader_id,
                            social_behavior=SocialBehavior(social_data['social_behavior']),
                            influence_score=social_data['influence_score'],
                            collaboration_preference=social_data['collaboration_preference'],
                            learning_from_others=social_data['learning_from_others'],
                            leadership_tendency=social_data['leadership_tendency'],
                            network_size=social_data['network_size'],
                            activity_level=social_data['activity_level'],
                            community_contribution=social_data['community_contribution']
                        )
                        
                        # Advanced personality
                        personality_vector = np.array(profile_data['personality_vector']) if profile_data['personality_vector'] else None
                        last_updated = datetime.fromisoformat(profile_data['last_updated']) if profile_data['last_updated'] else None
                        
                        advanced_profile = AdvancedPersonality(
                            base_profile=base_profile,
                            emotional_patterns=emotional_patterns,
                            decision_patterns=decision_patterns,
                            learning_patterns=learning_patterns,
                            social_profile=social_profile,
                            personality_vector=personality_vector,
                            confidence_score=profile_data['confidence_score'],
                            cluster_id=profile_data.get('cluster_id'),
                            adaptation_rate=profile_data.get('adaptation_rate', 0.1),
                            last_updated=last_updated
                        )
                        
                        profiles[trader_id] = advanced_profile
                    
                    return profiles
            except Exception as e:
                self.logger.error(f"Kengaytirilgan profillarni yuklashda xato: {e}")
        return {}
    
    def _save_advanced_profiles(self):
        """Kengaytirilgan profillarni saqlash"""
        try:
            profiles_data = {trader_id: profile.to_dict() 
                           for trader_id, profile in self.advanced_profiles.items()}
            with open(self.advanced_profiles_path, 'w') as f:
                json.dump(profiles_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Kengaytirilgan profillarni saqlashda xato: {e}")
    
    def _initialize_ml_models(self):
        """Machine learning modellarni sozlash"""
        try:
            # Scaler
            self.scaler = StandardScaler()
            
            # Clustering model
            self.clustering_model = KMeans(n_clusters=5, random_state=42, n_init=10)
            
            # Classification model
            self.classification_model = RandomForestClassifier(
                n_estimators=100, 
                random_state=42, 
                max_depth=10
            )
            
            self.logger.info("ML modellari muvaffaqiyatli sozlangan")
        except Exception as e:
            self.logger.error(f"ML modellari sozlanishida xato: {e}")
    
    def analyze_advanced_personality(self, 
                                   base_profile: PersonalityProfile,
                                   detailed_trading_data: Dict[str, Any],
                                   behavioral_observations: Optional[Dict[str, Any]] = None,
                                   social_data: Optional[Dict[str, Any]] = None) -> AdvancedPersonality:
        """
        Kengaytirilgan shaxsiyat tahlili
        
        Args:
            base_profile: Asosiy personality profile
            detailed_trading_data: Batafsil savdo ma'lumotlari
            behavioral_observations: Xulq-atvor kuzatuvlari
            social_data: Ijtimoiy ma'lumotlar
        
        Returns:
            AdvancedPersonality: Kengaytirilgan shaxsiyat profili
        """
        try:
            # 1. Xulq-atvor naqshlarini aniqlash
            emotional_patterns = self._analyze_emotional_patterns(
                base_profile, detailed_trading_data
            )
            
            decision_patterns = self._analyze_decision_patterns(
                base_profile, detailed_trading_data
            )
            
            learning_patterns = self._analyze_learning_patterns(
                base_profile, detailed_trading_data, behavioral_observations
            )
            
            # 2. Ijtimoiy profil
            social_profile = self._analyze_social_profile(
                base_profile, social_data
            )
            
            # 3. Personality vector yaratish
            personality_vector = self._create_personality_vector(
                base_profile, emotional_patterns, decision_patterns, 
                learning_patterns, social_profile
            )
            
            # 4. Machine learning analysis
            if ML_AVAILABLE and len(self.advanced_profiles) > 10:
                cluster_id, confidence_score = self._ml_classification(
                    personality_vector, base_profile.personality_type
                )
            else:
                cluster_id = None
                confidence_score = 0.7  # Default
            
            # 5. Advanced profile yaratish
            advanced_profile = AdvancedPersonality(
                base_profile=base_profile,
                emotional_patterns=emotional_patterns,
                decision_patterns=decision_patterns,
                learning_patterns=learning_patterns,
                social_profile=social_profile,
                personality_vector=personality_vector,
                confidence_score=confidence_score,
                cluster_id=cluster_id,
                last_updated=datetime.now()
            )
            
            # Saqlash
            self.advanced_profiles[base_profile.trader_id] = advanced_profile
            self._save_advanced_profiles()
            
            self.logger.info(f"Kengaytirilgan tahlil yakunlandi: {base_profile.trader_id}")
            return advanced_profile
            
        except Exception as e:
            self.logger.error(f"Kengaytirilgan shaxsiyat tahlilida xato: {e}")
            raise
    
    def _analyze_emotional_patterns(self, 
                                  profile: PersonalityProfile, 
                                  trading_data: Dict[str, Any]) -> List[BehavioralPattern]:
        """Emotional naqshlarni tahlil qilish"""
        patterns = []
        
        # Profit/loss pattern analysis
        trades = trading_data.get('trades', [])
        if not trades:
            return patterns
        
        # Time-based emotional analysis
        profits = [t.get('profit', 0) for t in trades]
        if profits:
            profit_sequence = self._analyze_profit_sequence(profits)
            if profit_sequence:
                patterns.append(BehavioralPattern(
                    pattern_type="profit_momentum",
                    frequency=profit_sequence['frequency'],
                    intensity=profit_sequence['intensity'],
                    duration=profit_sequence['duration'],
                    context="profit_streak",
                    correlation_score=profit_sequence['correlation'],
                    confidence=0.8
                ))
        
        # Loss recovery pattern
        losses = [t.get('profit', 0) for t in trades if t.get('profit', 0) < 0]
        if losses:
            recovery_pattern = self._analyze_loss_recovery(losses)
            if recovery_pattern:
                patterns.append(recovery_pattern)
        
        # Risk escalation during stress
        risk_escalation = self._analyze_risk_escalation(trades)
        if risk_escalation:
            patterns.append(risk_escalation)
        
        return patterns
    
    def _analyze_profit_sequence(self, profits: List[float]) -> Optional[Dict]:
        """Foyda ketma-ketliklari tahlili"""
        if len(profits) < 3:
            return None
        
        streaks = []
        current_streak = 0
        
        for profit in profits:
            if profit > 0:
                current_streak += 1
            else:
                if current_streak > 0:
                    streaks.append(current_streak)
                current_streak = 0
        
        if current_streak > 0:
            streaks.append(current_streak)
        
        if not streaks:
            return None
        
        return {
            'frequency': len(streaks) / len(profits),
            'intensity': np.mean(streaks),
            'duration': np.mean(streaks),
            'correlation': self._calculate_streak_correlation(profits)
        }
    
    def _analyze_loss_recovery(self, losses: List[float]) -> Optional[BehavioralPattern]:
        """Yo'qotishdan keyingi tiklanish naqshi"""
        if len(losses) < 2:
            return None
        
        recovery_strength = self._calculate_recovery_strength(losses)
        
        return BehavioralPattern(
            pattern_type="loss_recovery",
            frequency=len(losses) / len(losses),  # 100% of loss events
            intensity=recovery_strength['intensity'],
            duration=recovery_strength['avg_recovery_time'],
            context="after_loss",
            correlation_score=recovery_strength['correlation'],
            confidence=0.75
        )
    
    def _analyze_risk_escalation(self, trades: List[Dict]) -> Optional[BehavioralPattern]:
        """Risk kuchaytirish naqshi"""
        if len(trades) < 5:
            return None
        
        position_sizes = []
        for trade in trades:
            if 'position_size' in trade:
                position_sizes.append(trade['position_size'])
        
        if len(position_sizes) < 5:
            return None
        
        # Rising position sizes after losses
        escalation_score = 0.0
        for i in range(1, len(position_sizes)):
            if i < len(trades):
                current_trade = trades[i]
                prev_trade = trades[i-1]
                
                if (prev_trade.get('profit', 0) < 0 and 
                    position_sizes[i] > position_sizes[i-1]):
                    escalation_score += 1
        
        if escalation_score > 0:
            return BehavioralPattern(
                pattern_type="risk_escalation",
                frequency=escalation_score / len(position_sizes),
                intensity=escalation_score / len(position_sizes),
                duration=len(position_sizes),
                context="after_loss",
                correlation_score=0.6,
                confidence=0.7
            )
        
        return None
    
    def _analyze_decision_patterns(self, 
                                 profile: PersonalityProfile, 
                                 trading_data: Dict[str, Any]) -> List[BehavioralPattern]:
        """Qaror qabul qilish naqshlari tahlili"""
        patterns = []
        
        # Speed vs Accuracy analysis
        trades = trading_data.get('trades', [])
        if trades:
            decision_speed_pattern = self._analyze_decision_speed_pattern(trades)
            if decision_speed_pattern:
                patterns.append(decision_speed_pattern)
        
        # Consistency in decision making
        consistency_pattern = self._analyze_decision_consistency(trades)
        if consistency_pattern:
            patterns.append(consistency_pattern)
        
        # Information gathering behavior
        info_gathering = self._analyze_information_gathering(
            trading_data, profile
        )
        if info_gathering:
            patterns.append(info_gathering)
        
        return patterns
    
    def _analyze_decision_speed_pattern(self, trades: List[Dict]) -> Optional[BehavioralPattern]:
        """Qaror tezligi naqshi"""
        if len(trades) < 3:
            return None
        
        # Time from analysis to execution
        execution_times = []
        for trade in trades:
            if 'analysis_time' in trade and 'execution_time' in trade:
                analysis = datetime.fromisoformat(trade['analysis_time'])
                execution = datetime.fromisoformat(trade['execution_time'])
                time_diff = (execution - analysis).total_seconds()
                execution_times.append(time_diff)
        
        if execution_times:
            avg_time = np.mean(execution_times)
            
            return BehavioralPattern(
                pattern_type="decision_speed",
                frequency=len(execution_times) / len(trades),
                intensity=1.0 / (avg_time + 1),  # Inverse of time
                duration=len(trades),
                context="analysis_to_execution",
                correlation_score=0.8,
                confidence=0.85
            )
        
        return None
    
    def _analyze_decision_consistency(self, trades: List[Dict]) -> Optional[BehavioralPattern]:
        """Qaror barqarorligi tahlili"""
        if len(trades) < 5:
            return None
        
        # Similar positions/strategies
        strategies = []
        for trade in trades:
            if 'strategy' in trade:
                strategies.append(trade['strategy'])
        
        if len(strategies) > 0:
            strategy_counts = Counter(str strategies)
            most_common_strategy = strategy_counts.most_common(1)[0]
            consistency_score = most_common_strategy[1] / len(strategies)
            
            return BehavioralPattern(
                pattern_type="decision_consistency",
                frequency=consistency_score,
                intensity=consistency_score,
                duration=len(trades),
                context="strategy_selection",
                correlation_score=0.7,
                confidence=0.9
            )
        
        return None
    
    def _analyze_information_gathering(self, 
                                     trading_data: Dict, 
                                     profile: PersonalityProfile) -> Optional[BehavioralPattern]:
        """Ma'lumot to'plash xulq-atvori"""
        # Info sources frequency
        info_sources = profile.information_sources
        if not info_sources:
            return None
        
        return BehavioralPattern(
            pattern_type="information_gathering",
            frequency=len(info_sources),
            intensity=profile.emotional_score,
            duration=30,  # days
            context="pre_trading",
            correlation_score=0.6,
            confidence=0.7
        )
    
    def _analyze_learning_patterns(self, 
                                 profile: PersonalityProfile,
                                 trading_data: Dict[str, Any],
                                 behavioral_obs: Optional[Dict[str, Any]] = None) -> List[BehavioralPattern]:
        """O'rganish naqshlari tahlili"""
        patterns = []
        
        # Strategy adaptation
        adaptation_pattern = self._analyze_strategy_adaptation(
            trading_data, profile
        )
        if adaptation_pattern:
            patterns.append(adaptation_pattern)
        
        # Knowledge seeking behavior
        knowledge_pattern = self._analyze_knowledge_seeking(
            profile, behavioral_obs
        )
        if knowledge_pattern:
            patterns.append(knowledge_pattern)
        
        return patterns
    
    def _analyze_strategy_adaptation(self, 
                                   trading_data: Dict, 
                                   profile: PersonalityProfile) -> Optional[BehavioralPattern]:
        """Strategiya adaptatsiyasi naqshi"""
        trades = trading_data.get('trades', [])
        if len(trades) < 5:
            return None
        
        # Track strategy changes and performance
        strategy_performance = defaultdict(list)
        
        for trade in trades:
            if 'strategy' in trade and 'profit' in trade:
                strategy = trade['strategy']
                profit = trade['profit']
                strategy_performance[strategy].append(profit)
        
        if len(strategy_performance) > 1:
            # Check if switching to better performing strategies
            best_strategy = max(strategy_performance, 
                              key=lambda x: np.mean(strategy_performance[x]))
            
            return BehavioralPattern(
                pattern_type="strategy_adaptation",
                frequency=len(strategy_performance) / len(trades),
                intensity=len(strategy_performance),
                duration=len(trades),
                context="performance_based",
                correlation_score=0.75,
                confidence=0.8
            )
        
        return None
    
    def _analyze_knowledge_seeking(self, 
                                 profile: PersonalityProfile,
                                 behavioral_obs: Optional[Dict] = None) -> Optional[BehavioralPattern]:
        """Bilim izlash xulq-atvori"""
        learning_activities = 0
        
        if behavioral_obs:
            learning_activities += behavioral_obs.get('research_hours', 0)
            learning_activities += behavioral_obs.get('tutorial_completion', 0) * 10
            learning_activities += behavioral_obs.get('strategy_reading', 0) * 5
        
        if learning_activities > 0:
            return BehavioralPattern(
                pattern_type="knowledge_seeking",
                frequency=learning_activities / 30,  # Per month
                intensity=min(learning_activities / 100, 1.0),
                duration=30,
                context="continuous_learning",
                correlation_score=0.6,
                confidence=0.7
            )
        
        return None
    
    def _analyze_social_profile(self, 
                              profile: PersonalityProfile,
                              social_data: Optional[Dict[str, Any]] = None) -> SocialProfile:
        """Ijtimoiy profil tahlili"""
        if not social_data:
            # Default social profile based on personality
            return self._create_default_social_profile(profile)
        
        return SocialProfile(
            trader_id=profile.trader_id,
            social_behavior=SocialBehavior(social_data.get('behavior_type', 'individual')),
            influence_score=social_data.get('influence_score', 0.3),
            collaboration_preference=social_data.get('collaboration_preference', 0.3),
            learning_from_others=social_data.get('learning_preference', 0.4),
            leadership_tendency=social_data.get('leadership_score', 0.2),
            network_size=social_data.get('network_size', 5),
            activity_level=social_data.get('activity_level', 0.3),
            community_contribution=social_data.get('contribution_score', 0.2)
        )
    
    def _create_default_social_profile(self, profile: PersonalityProfile) -> SocialProfile:
        """Shaxsiyat asosida default ijtimoiy profil yaratish"""
        base_social = 0.3
        
        # Personality type based defaults
        if profile.personality_type == TradingPersonalityType.CONSERVATIVE:
            behavior = SocialBehavior.LEARNER
            collaboration = 0.4
        elif profile.personality_type == TradingPersonalityType.AGGRESSIVE:
            behavior = SocialBehavior.INDIVIDUAL
            collaboration = 0.2
        elif profile.personality_type == TradingPersonalityType.ALGORITHMIC_TRADER:
            behavior = SocialBehavior.INDIVIDUAL
            collaboration = 0.1
        elif profile.social_trading_score > 0.6:
            behavior = SocialBehavior.COLLABORATOR
            collaboration = 0.7
        else:
            behavior = SocialBehavior.INDIVIDUAL
            collaboration = 0.3
        
        return SocialProfile(
            trader_id=profile.trader_id,
            social_behavior=behavior,
            influence_score=max(0.1, profile.social_trading_score),
            collaboration_preference=collaboration,
            learning_from_others=base_social + profile.emotional_score * 0.3,
            leadership_tendency=base_social,
            network_size=int(5 + profile.social_trading_score * 20),
            activity_level=profile.social_trading_score,
            community_contribution=profile.social_trading_score * 0.5
        )
    
    def _create_personality_vector(self, 
                                 base_profile: PersonalityProfile,
                                 emotional_patterns: List[BehavioralPattern],
                                 decision_patterns: List[BehavioralPattern],
                                 learning_patterns: List[BehavioralPattern],
                                 social_profile: SocialProfile) -> np.ndarray:
        """Shaxsiyat vektori yaratish"""
        vector = np.zeros(self.feature_dimensions)
        
        # Trading metrics (0-6)
        vector[0] = min(base_profile.trading_frequency / 50.0, 1.0)  # Frequency normalized
        vector[1] = min(base_profile.avg_holding_time / 1440.0, 1.0)  # Holding time (days)
        vector[2] = base_profile.win_rate
        vector[3] = min(base_profile.sharpe_ratio / 3.0, 1.0)  # Sharpe normalized
        vector[4] = 1.0 - min(base_profile.max_drawdown / 0.5, 1.0)  # Inverted drawdown
        vector[5] = min(abs(base_profile.avg_profit_per_trade) / 0.1, 1.0)  # Profit factor proxy
        vector[6] = 1.0 - abs(vector[2] - 0.5) * 2  # Consistency measure
        
        # Risk metrics (7-9)
        risk_map = {RiskTolerance.VERY_LOW: 0.1, RiskTolerance.LOW: 0.3, 
                   RiskTolerance.MEDIUM: 0.5, RiskTolerance.HIGH: 0.8, 
                   RiskTolerance.VERY_HIGH: 1.0}
        vector[7] = risk_map.get(base_profile.risk_tolerance, 0.5)
        vector[8] = vector[7] * 0.8  # Position sizing proxy
        vector[9] = vector[7] * 1.2  # Leverage proxy
        
        # Time preferences (10-12)
        time_map = {"fast": 1.0, "medium": 0.6, "slow": 0.2}
        vector[10] = time_map.get(base_profile.decision_speed, 0.6)
        vector[11] = vector[10]  # Trading hours proxy
        vector[12] = vector[10]  # Decision speed
        
        # Behavioral metrics (13-16)
        vector[13] = base_profile.emotional_score
        vector[14] = 1.0 - base_profile.emotional_score  # Stress response proxy
        learning_map = {"visual": 0.8, "analytical": 0.9, "practical": 0.7}
        vector[15] = learning_map.get(base_profile.learning_style, 0.5)
        vector[16] = 0.7  # Adaptability proxy
        
        # Social metrics (17-19)
        vector[17] = social_profile.collaboration_preference
        vector[18] = social_profile.influence_score
        vector[19] = social_profile.community_contribution
        
        return vector
    
    def _ml_classification(self, 
                         personality_vector: np.ndarray, 
                         true_type: TradingPersonalityType) -> Tuple[Optional[int], float]:
        """Machine learning asosida tasniflash"""
        try:
            if not self.advanced_profiles or len(self.advanced_profiles) < 10:
                return None, 0.7
            
            # Prepare training data
            X_train = []
            y_train = []
            
            for trader_id, advanced_profile in self.advanced_profiles.items():
                if advanced_profile.personality_vector is not None:
                    X_train.append(advanced_profile.personality_vector)
                    y_train.append(advanced_profile.base_profile.personality_type.value)
            
            if len(X_train) < 5:
                return None, 0.7
            
            X_train = np.array(X_train)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X_train)
            
            # Clustering
            if len(X_scaled) > 5:
                cluster_labels = self.clustering_model.fit_predict(X_scaled)
                
                # Find cluster for this personality type
                type_to_cluster = {}
                for i, label in enumerate(cluster_labels):
                    type_to_cluster[y_train[i]] = label
                
                predicted_cluster = type_to_cluster.get(true_type.value)
                
                # Calculate confidence based on silhouette score
                if len(X_scaled) > 2:
                    silhouette_avg = silhouette_score(X_scaled, cluster_labels)
                    confidence = max(0.5, min(0.95, (silhouette_avg + 1) / 2))
                else:
                    confidence = 0.7
                
                return predicted_cluster, confidence
            
            return None, 0.7
            
        except Exception as e:
            self.logger.error(f"ML tasniflashda xato: {e}")
            return None, 0.7
    
    def _calculate_streak_correlation(self, profits: List[float]) -> float:
        """Streak korrelyatsiyasini hisoblash"""
        if len(profits) < 3:
            return 0.0
        
        positive_profits = [1 if p > 0 else 0 for p in profits]
        
        # Simple autocorrelation
        if len(positive_profits) > 1:
            correlation = np.corrcoef(positive_profits[:-1], positive_profits[1:])[0, 1]
            return correlation if not np.isnan(correlation) else 0.0
        
        return 0.0
    
    def _calculate_recovery_strength(self, losses: List[float]) -> Dict:
        """Tiklanish kuchini hisoblash"""
        if not losses:
            return {'intensity': 0, 'avg_recovery_time': 0, 'correlation': 0}
        
        # Recovery strength based on loss magnitude
        avg_loss = np.mean([abs(l) for l in losses])
        intensity = min(avg_loss / 0.1, 1.0)  # Normalized by 10% loss
        
        return {
            'intensity': intensity,
            'avg_recovery_time': len(losses),  # Simplified
            'correlation': 0.6  # Default
        }
    
    def find_similar_traders(self, 
                           target_profile: AdvancedPersonality, 
                           top_k: int = 5) -> List[Tuple[str, float]]:
        """O'xshash treyderlarni topish"""
        if not self.advanced_profiles:
            return []
        
        similarities = []
        target_vector = target_profile.personality_vector
        
        if target_vector is None:
            return []
        
        for trader_id, profile in self.advanced_profiles.items():
            if (trader_id != target_profile.base_profile.trader_id and 
                profile.personality_vector is not None):
                
                # Cosine similarity
                similarity = np.dot(target_vector, profile.personality_vector) / (
                    np.linalg.norm(target_vector) * np.linalg.norm(profile.personality_vector)
                )
                
                similarities.append((trader_id, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def suggest_learning_opportunities(self, 
                                     profile: AdvancedPersonality) -> List[Dict[str, Any]]:
        """O'rganish imkoniyatlari tavsiyalari"""
        opportunities = []
        
        # Based on learning patterns
        for pattern in profile.learning_patterns:
            if pattern.pattern_type == "knowledge_seeking":
                opportunities.append({
                    "type": "advanced_course",
                    "topic": "Advanced Technical Analysis",
                    "priority": "high" if pattern.intensity > 0.7 else "medium",
                    "estimated_time": "40 hours"
                })
        
        # Based on performance gaps
        if profile.base_profile.win_rate < 0.5:
            opportunities.append({
                "type": "skill_improvement",
                "topic": "Risk Management",
                "priority": "critical",
                "estimated_time": "20 hours"
            })
        
        if profile.base_profile.max_drawdown > 0.2:
            opportunities.append({
                "type": "psychology",
                "topic": "Trading Psychology",
                "priority": "high",
                "estimated_time": "30 hours"
            })
        
        # Based on social profile
        if profile.social_profile.collaboration_preference > 0.6:
            opportunities.append({
                "type": "social_learning",
                "topic": "Join Trading Community",
                "priority": "medium",
                "estimated_time": "ongoing"
            })
        
        return opportunities
    
    def adaptive_learning_recommendation(self, 
                                       profile: AdvancedPersonality,
                                       recent_performance: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptiv o'rganish tavsiyalari"""
        recommendations = {
            "immediate_actions": [],
            "long_term_goals": [],
            "skill_focus": [],
            "community_engagement": []
        }
        
        # Performance-based recommendations
        win_rate = profile.base_profile.win_rate
        drawdown = profile.base_profile.max_drawdown
        
        if win_rate < 0.4:
            recommendations["immediate_actions"].append({
                "action": "Focus on entry timing",
                "description": "Work on identifying better entry points",
                "urgency": "high"
            })
        
        if drawdown > 0.25:
            recommendations["immediate_actions"].append({
                "action": "Implement stricter stop losses",
                "description": "Reduce position sizes and improve risk management",
                "urgency": "critical"
            })
        
        # Personality-based recommendations
        if profile.base_profile.decision_speed == "fast":
            recommendations["skill_focus"].append({
                "skill": "Pattern Recognition",
                "reason": "Matches your fast decision-making style",
                "priority": "high"
            })
        
        if profile.social_profile.learning_from_others > 0.6:
            recommendations["community_engagement"].append({
                "activity": "Mentor matching",
                "description": "Connect with experienced traders",
                "impact": "high"
            })
        
        return recommendations
    
    def export_personality_insights(self, 
                                  profile: AdvancedPersonality,
                                  format: str = "json") -> str:
        """Shaxsiyat insights ni export qilish"""
        if format == "json":
            return json.dumps(profile.to_dict(), indent=2)
        
        elif format == "summary":
            summary = f"""
            Shaxsiyat Tahlili Hisoboti
            ========================
            
            Asosiy profil: {profile.base_profile.personality_type.value}
            Ishonchlilik: {profile.confidence_score:.1%}
            
            Xulq-atvor naqshlari:
            - Emotional patterns: {len(profile.emotional_patterns)} ta
            - Decision patterns: {len(profile.decision_patterns)} ta
            - Learning patterns: {len(profile.learning_patterns)} ta
            
            Ijtimoiy profil:
            - Xulq-atvor: {profile.social_profile.social_behavior.value}
            - Collaboration: {profile.social_profile.collaboration_preference:.1%}
            - Influence: {profile.social_profile.influence_score:.1%}
            
            {f"Klaster: {profile.cluster_id}" if profile.cluster_id is not None else "Klaster: aniqlanmagan"}
            """
            return summary
        
        else:
            raise ValueError(f"Qo'llab-quvvatlanmagan format: {format}")

# Utility functions
def create_sample_advanced_profile(trader_id: str) -> AdvancedPersonality:
    """Namuna kengaytirilgan profil yaratish"""
    from trading_personality import create_sample_profile
    
    base = create_sample_profile(trader_id, "day_trader")
    
    # Sample patterns
    emotional_patterns = [
        BehavioralPattern(
            pattern_type="profit_momentum",
            frequency=0.3,
            intensity=0.8,
            duration=5.0,
            context="profit_streak",
            correlation_score=0.7,
            confidence=0.8
        )
    ]
    
    social_profile = SocialProfile(
        trader_id=trader_id,
        social_behavior=SocialBehavior.LEARNER,
        influence_score=0.3,
        collaboration_preference=0.6,
        learning_from_others=0.7,
        leadership_tendency=0.2,
        network_size=15,
        activity_level=0.4,
        community_contribution=0.3
    )
    
    return AdvancedPersonality(
        base_profile=base,
        emotional_patterns=emotional_patterns,
        decision_patterns=[],
        learning_patterns=[],
        social_profile=social_profile,
        personality_vector=np.random.random(20),
        confidence_score=0.8,
        last_updated=datetime.now()
    )

# Test
if __name__ == "__main__":
    # Test
    analyzer = PersonalityAnalyzer()
    
    # Sample profile
    advanced_profile = create_sample_advanced_profile("test_advanced_001")
    
    print(f"Advanced Profile created for: {advanced_profile.base_profile.trader_id}")
    print(f"Confidence: {advanced_profile.confidence_score:.1%}")
    print(f"Social behavior: {advanced_profile.social_profile.social_behavior.value}")
    
    # Similar traders
    similar = analyzer.find_similar_traders(advanced_profile, 3)
    print(f"Similar traders found: {len(similar)}")
    
    # Learning opportunities
    opportunities = analyzer.suggest_learning_opportunities(advanced_profile)
    print(f"Learning opportunities: {len(opportunities)}")
    
    # Export
    insights = analyzer.export_personality_insights(advanced_profile, "summary")
    print(f"\n{insights}")