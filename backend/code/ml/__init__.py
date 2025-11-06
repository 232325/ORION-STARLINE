"""
AI Trading Evolution - Machine Learning Module
============================================

Advanced AI va ML modullari - Reinforcement Learning, Emotion AI, Predictive Models

Author: MiniMax Agent
Version: 1.0.0
Date: 2025-11-04
"""

# Advanced RL Models
from .advanced_rl_models import (
    AdvancedRLModels,
    RLModelType,
    TrainingConfig,
    EnvironmentType
)

# Emotion AI
from .emotion_ai import (
    EmotionAI,
    EmotionType,
    SentimentAnalyzer,
    FearGreedIndex
)

# Predictive Models
from .predictive_models import (
    PredictiveModels,
    ModelType,
    PredictionHorizon,
    LSTMConfig,
    TransformerConfig,
    TFTConfig
)

# Advanced Backtesting
from .advanced_backtesting import (
    AdvancedBacktesting,
    BacktestType,
    WalkForwardConfig,
    MonteCarloConfig,
    WalkForwardAnalysis
)

# Meta Learning
from .meta_learning import (
    MetaLearning,
    MetaAlgorithmType,
    TaskType,
    FewShotLearner,
    MAMLImplementation,
    ReptileImplementation
)

# Ensemble Methods
from .ensemble_methods import (
    EnsembleMethods,
    EnsembleType,
    StackingConfig,
    BoostingConfig,
    BaggingConfig
)

__all__ = [
    # Advanced RL Models
    "AdvancedRLModels",
    "RLModelType",
    "TrainingConfig", 
    "EnvironmentType",
    
    # Emotion AI
    "EmotionAI",
    "EmotionType",
    "SentimentAnalyzer",
    "FearGreedIndex",
    
    # Predictive Models
    "PredictiveModels",
    "ModelType",
    "PredictionHorizon",
    "LSTMConfig",
    "TransformerConfig",
    "TFTConfig",
    
    # Advanced Backtesting
    "AdvancedBacktesting",
    "BacktestType",
    "WalkForwardConfig",
    "MonteCarloConfig",
    "WalkForwardAnalysis",
    
    # Meta Learning
    "MetaLearning",
    "MetaAlgorithmType",
    "TaskType",
    "FewShotLearner",
    "MAMLImplementation",
    "ReptileImplementation",
    
    # Ensemble Methods
    "EnsembleMethods",
    "EnsembleType",
    "StackingConfig",
    "BoostingConfig",
    "BaggingConfig"
]
