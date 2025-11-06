"""
Signal Aggregator
================

AI model signalarini aggregation qilish va ensemble predictions yaratish.
Multiple model signalarini combine qilish va consensus yaratish.
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import statistics
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor

from .model_integration import ModelIntegration, ModelPrediction, SignalType, TradingSignal

class AggregationMethod(Enum):
    """Signal aggregation methodlari"""
    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_AVERAGE = "weighted_average"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    ENSEMBLE_LEARNING = "ensemble_learning"
    DYNAMIC_WEIGHTING = "dynamic_weighting"
    VOTING_BASED = "voting_based"

class ConsensusStrategy(Enum):
    """Consensus strategylari"""
    SIMPLE_MAJORITY = "simple_majority"
    SUPER_MAJORITY = "super_majority"
    CONSENSUS_THRESHOLD = "consensus_threshold"
    WEIGHTED_CONSENSUS = "weighted_consensus"

@dataclass
class SignalVote:
    """Individual model vote"""
    model_name: str
    signal_type: SignalType
    confidence: float
    weight: float = 1.0
    timestamp: float = field(default_factory=time.time)
    features: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AggregationResult:
    """Signal aggregation result"""
    symbol: str
    final_signal: SignalType
    confidence: float
    consensus_score: float
    voting_details: List[SignalVote]
    aggregation_method: AggregationMethod
    timestamp: float
    model_agreement: float
    conflict_resolution: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class SignalAggregator:
    """
    Signal Aggregator
    
    AI model signalarini aggregation qilish va ensemble predictions yaratish.
    Multiple aggregation methods va consensus strategies qo'llab-quvvatlaydi.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.model_integration = ModelIntegration()
        self.signal_history: List[TradingSignal] = []
        self.model_performance: Dict[str, Dict[str, float]] = {}
        self.aggregation_cache: Dict[str, AggregationResult] = {}
        
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Configuration
        self.default_aggregation_method = AggregationMethod(
            self.config.get('default_method', 'confidence_weighted')
        )
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        self.consensus_threshold = self.config.get('consensus_threshold', 0.6)
        self.max_history_size = self.config.get('max_history_size', 1000)
        
        # Dynamic weighting parameters
        self.performance_window = self.config.get('performance_window', 50)
        self.adaptation_rate = self.config.get('adaptation_rate', 0.1)
        
        # Model weights (can be updated dynamically)
        self.model_weights: Dict[str, float] = {}
    
    async def initialize(self) -> bool:
        """Signal Aggregator-ni ishga tushirish"""
        try:
            self.logger.info("Signal Aggregator ishga tushirilmoqda...")
            
            # Model integration initialization
            await self.model_integration.initialize()
            
            # Default model weights setup
            await self._setup_default_weights()
            
            # Performance tracking start
            await self._start_performance_tracking()
            
            self.logger.info("Signal Aggregator muvaffaqiyatli ishga tushdi")
            return True
            
        except Exception as e:
            self.logger.error(f"Signal Aggregator ishga tushishda xato: {e}")
            return False
    
    async def _setup_default_weights(self):
        """Default model weights sozlash"""
        # Get available models
        models = self.model_integration.list_models()
        
        # Equal weights initially
        weight = 1.0 / len(models) if models else 1.0
        
        for model_info in models:
            model_name = model_info['name']
            self.model_weights[model_name] = weight
    
    async def _start_performance_tracking(self):
        """Performance tracking ni boshlash"""
        async def track_performance():
            while True:
                try:
                    await self._update_model_performance()
                    await asyncio.sleep(300)  # 5 daqiqa
                except Exception as e:
                    self.logger.error(f"Performance tracking da xato: {e}")
                    await asyncio.sleep(60)
        
        asyncio.create_task(track_performance())
    
    async def aggregate_signals(self, symbol: str, model_predictions: List[ModelPrediction],
                              aggregation_method: AggregationMethod = None) -> AggregationResult:
        """Model predictions ni aggregate qilish"""
        try:
            if not model_predictions:
                self.logger.warning(f"Model predictions topilmadi: {symbol}")
                return None
            
            # Default method
            if aggregation_method is None:
                aggregation_method = self.default_aggregation_method
            
            # Signal votes yaratish
            votes = await self._create_signal_votes(model_predictions)
            
            # Aggregation method ga qarab signal yaratish
            if aggregation_method == AggregationMethod.MAJORITY_VOTE:
                result = await self._majority_vote_aggregation(symbol, votes)
            elif aggregation_method == AggregationMethod.WEIGHTED_AVERAGE:
                result = await self._weighted_average_aggregation(symbol, votes)
            elif aggregation_method == AggregationMethod.CONFIDENCE_WEIGHTED:
                result = await self._confidence_weighted_aggregation(symbol, votes)
            elif aggregation_method == AggregationMethod.ENSEMBLE_LEARNING:
                result = await self._ensemble_learning_aggregation(symbol, votes)
            elif aggregation_method == AggregationMethod.DYNAMIC_WEIGHTING:
                result = await self._dynamic_weighting_aggregation(symbol, votes)
            elif aggregation_method == AggregationMethod.VOTING_BASED:
                result = await self._voting_based_aggregation(symbol, votes)
            else:
                result = await self._confidence_weighted_aggregation(symbol, votes)
            
            # Cache ga saqlash
            self.aggregation_cache[f"{symbol}_{int(time.time())}"] = result
            
            # Signal history ga qo'shish
            trading_signal = TradingSignal(
                symbol=symbol,
                signal_type=result.final_signal,
                confidence=result.confidence,
                model_name="ensemble",
                timestamp=result.timestamp,
                price=0.0,  # Should be provided externally
                metadata={
                    'aggregation_method': aggregation_method.value,
                    'consensus_score': result.consensus_score,
                    'model_agreement': result.model_agreement
                }
            )
            self.signal_history.append(trading_signal)
            
            # History size limit
            if len(self.signal_history) > self.max_history_size:
                self.signal_history = self.signal_history[-self.max_history_size//2:]
            
            self.logger.info(f"Signals aggregated for {symbol}: {result.final_signal.name} "
                           f"(confidence: {result.confidence:.3f})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Signal aggregation da xato: {e}")
            return None
    
    async def _create_signal_votes(self, model_predictions: List[ModelPrediction]) -> List[SignalVote]:
        """Model predictions dan signal votes yaratish"""
        votes = []
        
        for prediction in model_predictions:
            try:
                # Prediction dan signal type olish
                signal_data = prediction.prediction
                signal_type = SignalType(signal_data.get('signal_type', SignalType.HOLD.value))
                confidence = prediction.confidence
                
                # Model weight olish
                model_weight = self.model_weights.get(prediction.model_name, 1.0)
                
                vote = SignalVote(
                    model_name=prediction.model_name,
                    signal_type=signal_type,
                    confidence=confidence,
                    weight=model_weight,
                    features=prediction.features_used
                )
                
                votes.append(vote)
                
            except Exception as e:
                self.logger.error(f"Signal vote yaratishda xato {prediction.model_name}: {e}")
                continue
        
        return votes
    
    async def _majority_vote_aggregation(self, symbol: str, votes: List[SignalVote]) -> AggregationResult:
        """Majority vote aggregation"""
        # Signal counts
        signal_counts = Counter(vote.signal_type for vote in votes)
        total_votes = len(votes)
        
        # Majority signal
        if not signal_counts:
            final_signal = SignalType.HOLD
            confidence = 0.0
        else:
            final_signal = signal_counts.most_common(1)[0][0]
            confidence = signal_counts[final_signal] / total_votes
        
        # Consensus score
        consensus_score = confidence
        
        # Model agreement
        model_agreement = max(signal_counts.values()) / total_votes if total_votes > 0 else 0.0
        
        return AggregationResult(
            symbol=symbol,
            final_signal=final_signal,
            confidence=confidence,
            consensus_score=consensus_score,
            voting_details=votes,
            aggregation_method=AggregationMethod.MAJORITY_VOTE,
            timestamp=time.time(),
            model_agreement=model_agreement,
            conflict_resolution="majority_vote"
        )
    
    async def _weighted_average_aggregation(self, symbol: str, votes: List[SignalVote]) -> AggregationResult:
        """Weighted average aggregation"""
        if not votes:
            return await self._create_empty_result(symbol)
        
        # Calculate weighted signals
        signal_values = {
            SignalType.BUY: 1.0,
            SignalType.HOLD: 0.0,
            SignalType.SELL: -1.0
        }
        
        total_weight = sum(vote.weight for vote in votes)
        
        if total_weight == 0:
            final_signal = SignalType.HOLD
            weighted_score = 0.0
            confidence = 0.0
        else:
            # Weighted average calculation
            weighted_sum = sum(
                signal_values[vote.signal_type] * vote.confidence * vote.weight
                for vote in votes
            )
            weighted_score = weighted_sum / total_weight
            
            # Convert back to signal type
            if weighted_score > 0.1:
                final_signal = SignalType.BUY
            elif weighted_score < -0.1:
                final_signal = SignalType.SELL
            else:
                final_signal = SignalType.HOLD
            
            # Confidence calculation
            confidence = abs(weighted_score)
        
        # Consensus score
        consensus_score = confidence
        
        # Model agreement (average confidence)
        model_agreement = statistics.mean(vote.confidence for vote in votes)
        
        return AggregationResult(
            symbol=symbol,
            final_signal=final_signal,
            confidence=confidence,
            consensus_score=consensus_score,
            voting_details=votes,
            aggregation_method=AggregationMethod.WEIGHTED_AVERAGE,
            timestamp=time.time(),
            model_agreement=model_agreement,
            conflict_resolution="weighted_average",
            metadata={'weighted_score': weighted_score}
        )
    
    async def _confidence_weighted_aggregation(self, symbol: str, votes: List[SignalVote]) -> AggregationResult:
        """Confidence weighted aggregation"""
        if not votes:
            return await self._create_empty_result(symbol)
        
        # Confidence-based weighting
        total_weight = sum(vote.confidence * vote.weight for vote in votes)
        
        # Calculate confidence-weighted signals
        signal_confidences = {
            SignalType.BUY: 0.0,
            SignalType.HOLD: 0.0,
            SignalType.SELL: 0.0
        }
        
        for vote in votes:
            signal_confidences[vote.signal_type] += vote.confidence * vote.weight
        
        # Normalize
        for signal_type in signal_confidences:
            if total_weight > 0:
                signal_confidences[signal_type] /= total_weight
        
        # Find signal with highest confidence
        final_signal = max(signal_confidences, key=signal_confidences.get)
        confidence = signal_confidences[final_signal]
        
        # Consensus score
        consensus_score = confidence
        
        # Model agreement
        model_agreement = statistics.mean(vote.confidence for vote in votes)
        
        return AggregationResult(
            symbol=symbol,
            final_signal=final_signal,
            confidence=confidence,
            consensus_score=consensus_score,
            voting_details=votes,
            aggregation_method=AggregationMethod.CONFIDENCE_WEIGHTED,
            timestamp=time.time(),
            model_agreement=model_agreement,
            conflict_resolution="confidence_weighted",
            metadata={'signal_confidences': signal_confidences}
        )
    
    async def _ensemble_learning_aggregation(self, symbol: str, votes: List[SignalVote]) -> AggregationResult:
        """Ensemble learning aggregation"""
        # Complex ensemble method implementation
        # This would involve more sophisticated ML techniques
        
        # For now, use confidence weighted approach
        result = await self._confidence_weighted_aggregation(symbol, votes)
        result.aggregation_method = AggregationMethod.ENSEMBLE_LEARNING
        result.conflict_resolution = "ensemble_learning"
        
        return result
    
    async def _dynamic_weighting_aggregation(self, symbol: str, votes: List[SignalVote]) -> AggregationResult:
        """Dynamic weighting aggregation"""
        if not votes:
            return await self._create_empty_result(symbol)
        
        # Update model weights based on recent performance
        await self._update_dynamic_weights()
        
        # Use confidence weighted with updated weights
        result = await self._confidence_weighted_aggregation(symbol, votes)
        result.aggregation_method = AggregationMethod.DYNAMIC_WEIGHTING
        result.conflict_resolution = "dynamic_weighting"
        result.metadata['updated_weights'] = {
            vote.model_name: self.model_weights[vote.model_name] 
            for vote in votes
        }
        
        return result
    
    async def _voting_based_aggregation(self, symbol: str, votes: List[SignalVote]) -> AggregationResult:
        """Voting based aggregation"""
        if not votes:
            return await self._create_empty_result(symbol)
        
        # Threshold-based voting
        high_confidence_votes = [vote for vote in votes if vote.confidence > self.confidence_threshold]
        
        if len(high_confidence_votes) >= len(votes) * 0.6:  # 60% super majority
            # Use high confidence votes only
            result = await self._confidence_weighted_aggregation(symbol, high_confidence_votes)
            result.conflict_resolution = "super_majority_threshold"
        else:
            # Use all votes
            result = await self._confidence_weighted_aggregation(symbol, votes)
            result.conflict_resolution = "simple_majority_threshold"
        
        result.aggregation_method = AggregationMethod.VOTING_BASED
        result.metadata['high_confidence_votes_count'] = len(high_confidence_votes)
        
        return result
    
    async def _create_empty_result(self, symbol: str) -> AggregationResult:
        """Empty result yaratish"""
        return AggregationResult(
            symbol=symbol,
            final_signal=SignalType.HOLD,
            confidence=0.0,
            consensus_score=0.0,
            voting_details=[],
            aggregation_method=self.default_aggregation_method,
            timestamp=time.time(),
            model_agreement=0.0,
            conflict_resolution="no_votes"
        )
    
    async def _update_model_performance(self):
        """Model performance update"""
        try:
            # Recent signal history dan performance calculate qilish
            recent_signals = self.signal_history[-self.performance_window:]
            
            for model_name in self.model_weights.keys():
                # Model-specific signals topish
                model_signals = [signal for signal in recent_signals 
                               if signal.metadata.get('models_used', {}).get(model_name)]
                
                if not model_signals:
                    continue
                
                # Simple performance metric (can be enhanced)
                avg_confidence = statistics.mean(signal.confidence for signal in model_signals)
                self.model_performance[model_name] = {
                    'avg_confidence': avg_confidence,
                    'signal_count': len(model_signals),
                    'last_update': time.time()
                }
            
        except Exception as e:
            self.logger.error(f"Model performance update da xato: {e}")
    
    async def _update_dynamic_weights(self):
        """Dynamic weights update"""
        try:
            # Performance-based weight adjustment
            if not self.model_performance:
                return
            
            total_performance = sum(
                perf.get('avg_confidence', 0.5) 
                for perf in self.model_performance.values()
            )
            
            if total_performance == 0:
                return
            
            # Update weights based on performance
            for model_name, weight in self.model_weights.items():
                performance = self.model_performance.get(model_name, {}).get('avg_confidence', 0.5)
                target_weight = performance / total_performance
                
                # Smooth update
                updated_weight = (1 - self.adaptation_rate) * weight + self.adaptation_rate * target_weight
                self.model_weights[model_name] = max(0.01, updated_weight)  # Minimum weight
            
        except Exception as e:
            self.logger.error(f"Dynamic weight update da xato: {e}")
    
    async def predict_real_time(self, symbol: str, market_data: Dict[str, Any],
                              aggregation_method: AggregationMethod = None) -> Optional[AggregationResult]:
        """Real-time prediction"""
        try:
            # Market data dan state yaratish
            state = self._prepare_market_state(market_data)
            
            # Barcha available modellar bilan prediction
            model_predictions = []
            models = self.model_integration.list_models()
            
            for model_info in models:
                model_name = model_info['name']
                prediction = await self.model_integration.predict(model_name, state)
                if prediction:
                    model_predictions.append(prediction)
            
            if not model_predictions:
                self.logger.warning(f"No model predictions for {symbol}")
                return None
            
            # Aggregate signals
            result = await self.aggregate_signals(symbol, model_predictions, aggregation_method)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Real-time prediction da xato: {e}")
            return None
    
    def _prepare_market_state(self, market_data: Dict[str, Any]) -> np.ndarray:
        """Market datani model state ga convert qilish"""
        try:
            # Extract features
            features = []
            
            # Price features
            features.extend([
                market_data.get('price', 0.0),
                market_data.get('volume', 0.0),
                market_data.get('open', 0.0),
                market_data.get('high', 0.0),
                market_data.get('low', 0.0)
            ])
            
            # Technical indicators
            features.extend([
                market_data.get('rsi', 50.0),
                market_data.get('macd', 0.0),
                market_data.get('bollinger_position', 0.5),
                market_data.get('sma_ratio', 1.0),
                market_data.get('volume_sma_ratio', 1.0)
            ])
            
            # Pad to required dimension
            target_dim = 10  # Default state dimension
            while len(features) < target_dim:
                features.append(0.0)
            
            return np.array(features[:target_dim], dtype=np.float32)
            
        except Exception as e:
            self.logger.error(f"Market state preparation da xato: {e}")
            return np.zeros(10, dtype=np.float32)
    
    def get_aggregation_stats(self) -> Dict[str, Any]:
        """Aggregation statistics"""
        total_signals = len(self.signal_history)
        
        # Signal distribution
        signal_distribution = Counter(signal.signal_type for signal in self.signal_history)
        
        # Average confidence
        if self.signal_history:
            avg_confidence = statistics.mean(signal.confidence for signal in self.signal_history)
        else:
            avg_confidence = 0.0
        
        # Model performance summary
        performance_summary = {}
        for model_name, performance in self.model_performance.items():
            performance_summary[model_name] = {
                'avg_confidence': performance.get('avg_confidence', 0.0),
                'signal_count': performance.get('signal_count', 0)
            }
        
        return {
            'total_signals': total_signals,
            'signal_distribution': {sig.name: count for sig, count in signal_distribution.items()},
            'average_confidence': avg_confidence,
            'model_weights': self.model_weights,
            'model_performance': performance_summary,
            'aggregation_methods_used': list(set(
                signal.metadata.get('aggregation_method', 'unknown') 
                for signal in self.signal_history
            ))
        }
    
    def get_signal_history(self, symbol: str = None, limit: int = 100) -> List[TradingSignal]:
        """Signal history olish"""
        if symbol:
            filtered_signals = [signal for signal in self.signal_history if signal.symbol == symbol]
        else:
            filtered_signals = self.signal_history
        
        return filtered_signals[-limit:]
    
    async def update_model_weights(self, model_weights: Dict[str, float]):
        """Model weights update"""
        try:
            total_weight = sum(model_weights.values())
            if total_weight > 0:
                # Normalize weights
                normalized_weights = {
                    model: weight / total_weight 
                    for model, weight in model_weights.items()
                }
                self.model_weights.update(normalized_weights)
                self.logger.info(f"Model weights updated: {normalized_weights}")
            
        except Exception as e:
            self.logger.error(f"Model weights update da xato: {e}")