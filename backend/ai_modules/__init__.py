"""
AI Modules Package - Orion Starline AI Trading System
====================================================

Bu paket AI agentlarni va ularning boshqaruvchi tizimini o'z ichiga oladi.

Asosiy Modullar:
- agent_controller: Asosiy AI agent boshqaruvchi
- ai_signal_generator: AI signal generation va RL agents
- strategy_generator: AI-driven strategy generation
- backtester: Comprehensive backtesting system
- training_pipeline: Auto-learning va model training
- model_updater: Model yangilash va monitoring
- risk_manager: Comprehensive risk management
- strategy_evolution: Strategy evolution tracking
- historical_metrics: Historical analysis va seasonal patterns
- evolution_analytics: ML predictions va genetic algorithms
- visual_intelligence: Vizual ma'lumotlar tahlil tizimi - chart analysis, OCR, pattern detection
- chart_analysis: Chart va technical pattern tahlil moduli
- ocr_module: OCR va hujjat tahlil moduli

Foydalanish:
```python
from ai_modules import (
    AgentController, AISignalGenerator, StrategyEvolutionTracker,
    HistoricalMetricsEngine, EvolutionAnalyticsEngine
)

# Strategy Evolution Tracking
evolution_tracker = StrategyEvolutionTracker()
analysis = evolution_tracker.get_evolution_analysis("EURUSD_TREND_001")

# Historical Metrics Analysis
metrics_engine = HistoricalMetricsEngine()
report = metrics_engine.generate_historical_report("EURUSD_TREND_001")

# Evolution Analytics
analytics_engine = EvolutionAnalyticsEngine()
prediction = analytics_engine.predict_evolution("EURUSD_TREND_001")
best_params = analytics_engine.run_genetic_algorithm("EURUSD_TREND_001")
```

Author: Orion Starline AI Team
Version: 1.0.0
"""

from .agent_controller import (
    AgentController,
    BaseAgent,
    GPTAgent,
    RiskAgent,
    SignalAgent,
    EventBus,
    AgentRegistry,
    LoadBalancer,
    FailoverManager,
    AgentStatus,
    EventType,
    AgentState,
    Event
)

from .ai_signal_generator import (
    AISignalGenerator,
    FeatureEngineer,
    MarketRegimeDetector,
    TradingEnvironment,
    DQNAgent,
    PPOAgent,
    A2CAgent,
    DDPGAgent,
    TD3Agent,
    ReplayBuffer
)

from .strategy_generator import (
    StrategyGenerator,
    StrategyConfig,
    StrategyResult,
    StrategyType,
    GeneticOptimizer,
    WalkForwardAnalyzer,
    MonteCarloSimulator
)

from .backtester import (
    Backtester,
    BacktestConfig,
    BacktestResult,
    MarketData,
    Trade,
    PerformanceAnalyzer,
    RiskAnalyzer
)

from .training_pipeline import (
    TrainingPipeline,
    DataPipeline,
    ModelTrainer,
    RetrainingManager,
    ABTesting,
    ModelMonitoring,
    OnlineLearning,
    FederatedLearning,
    DataQualityMetrics,
    ModelPerformance,
    RetrainingTrigger
)

from .model_updater import (
    ModelUpdater,
    ModelVersionManager,
    PerformanceMonitor,
    DriftDetector,
    ABLayoutManager,
    NotificationManager,
    ModelUpdateEvent,
    DeploymentConfig,
    ModelMetrics
)

from .risk_manager import (
    RiskManager,
    Position,
    RiskMetrics,
    RiskAlert,
    RiskLevel,
    RiskModel,
    AlertType
)

from .strategy_evolution import (
    StrategyEvolutionTracker,
    StrategySnapshot,
    EvolutionEvent,
    EvolutionType,
    MarketRegime
)

from .historical_metrics import (
    HistoricalMetricsEngine,
    HistoricalMetric,
    SeasonalPattern,
    MarketCycle,
    TimeFrame,
    MetricType
)

from .evolution_analytics import (
    EvolutionAnalyticsEngine,
    EvolutionPrediction,
    GeneticIndividual,
    StrategyMutation,
    PredictionModel,
    EvolutionPhase
)

# Voice & Audio Features (yangilangan)
from .voice_features import (
    VoiceFeatures,
    Language,
    VoiceEmotion,
    VoiceCommand,
    VoiceCommandType,
    AudioFeatures,
    VoiceAnalysis,
    voice_features,
    process_voice_command,
    speech_to_text,
    text_to_speech,
    detect_language,
    analyze_voice_sentiment
)

from .stt_tts import (
    STTEngine,
    TTSEngine,
    STTProvider,
    TTSProvider,
    VoiceSettings,
    STTResult,
    TTSResult,
    StreamingSTT,
    StreamingTTS,
    stt_engine,
    tts_engine,
    transcribe_audio,
    synthesize_speech,
    get_streaming_stt,
    get_streaming_tts,
    create_voice_settings
)

from .audio_analysis import (
    AudioAnalyzer,
    AudioAnalysisResult,
    EmotionDetectionResult,
    SpeakerProfile,
    AudioQuality,
    AudioEffect,
    AudioEnhancementSettings,
    audio_analyzer,
    analyze_audio,
    detect_emotion,
    identify_speaker,
    enhance_audio,
    train_speaker_model,
    get_speaker_profiles
)

# Visual Intelligence Modules
from .visual_intelligence import (
    VisualIntelligence,
    VisualAnalysisResult,
    VisualSignalType,
    AnalysisConfidence,
    MarketMicrostructureData,
    VisualSignal
)

from .chart_analysis import (
    ChartAnalyzer,
    PatternType,
    TrendDirection,
    CandlestickPattern,
    TechnicalPattern,
    TrendLine,
    SupportResistance,
    VolumeProfile
)

from .ocr_module import (
    OCRProcessor,
    TextAnalyzer,
    TableExtractor,
    DocumentAnalyzer,
    ImageEnhancer,
    BatchProcessor,
    TextExtraction,
    ChartTextData,
    DocumentAnalysis,
    TableData,
    TextType,
    DocumentType,
    ProcessingStatus
)

# Import existing A2C algorithm
try:
    from ..a2c_algorithm import AdvantageA2C, TradingConfig, A2CTrainer
    _a2c_available = True
except ImportError:
    _a2c_available = False
    logger = logging.getLogger(__name__)
    logger.warning("A2C algorithm not available - make sure a2c_algorithm.py is in the correct location")

# Performance Optimization Engine
from .performance_optimization import (
    PerformanceOptimizer,
    CacheManager,
    LoadBalancer,
    ModelManager,
    ResourceMonitor,
    CostTracker,
    AsyncProcessor,
    AutoScaler,
    MemoryCache,
    RedisCache,
    PerformanceMetrics,
    ResourceUsage,
    CostMetrics,
    CacheEntry,
    LoadBalancedNode,
    ModelPerformance,
    OptimizationLevel,
    CacheStrategy,
    LoadBalanceStrategy,
    ModelType,
    performance_monitor,
    cache_result,
    rate_limiter
)

__version__ = "1.0.0"
__author__ = "Orion Starline AI Team"

# Modul meta ma'lumotlari
__all__ = [
    # Agent Controller
    "AgentController",
    "BaseAgent", 
    "GPTAgent",
    "RiskAgent",
    "SignalAgent",
    "EventBus",
    "AgentRegistry",
    "LoadBalancer",
    "FailoverManager",
    "AgentStatus",
    "EventType",
    "AgentState",
    "Event",
    
    # AI Signal Generator
    "AISignalGenerator",
    "FeatureEngineer",
    "MarketRegimeDetector",
    "TradingEnvironment",
    "DQNAgent",
    "PPOAgent",
    "A2CAgent",
    "DDPGAgent",
    "TD3Agent",
    "ReplayBuffer",
    
    # Strategy Generator
    "StrategyGenerator",
    "StrategyConfig",
    "StrategyResult",
    "StrategyType",
    "GeneticOptimizer",
    "WalkForwardAnalyzer",
    "MonteCarloSimulator",
    
    # Backtester
    "Backtester",
    "BacktestConfig",
    "BacktestResult",
    "MarketData",
    "Trade",
    "PerformanceAnalyzer",
    "RiskAnalyzer",
    
    # Training Pipeline
    "TrainingPipeline",
    "DataPipeline",
    "ModelTrainer",
    "RetrainingManager",
    "ABTesting",
    "ModelMonitoring",
    "OnlineLearning",
    "FederatedLearning",
    "DataQualityMetrics",
    "ModelPerformance",
    "RetrainingTrigger",
    
    # Model Updater
    "ModelUpdater",
    "ModelVersionManager",
    "PerformanceMonitor",
    "DriftDetector",
    "ABLayoutManager",
    "NotificationManager",
    "ModelUpdateEvent",
    "DeploymentConfig",
    "ModelMetrics",
    
    # Risk Manager
    "RiskManager",
    "Position",
    "RiskMetrics",
    "RiskAlert",
    "RiskLevel",
    "RiskModel",
    "AlertType",
    
    # Strategy Evolution Tracking
    "StrategyEvolutionTracker",
    "StrategySnapshot",
    "EvolutionEvent",
    "EvolutionType",
    "MarketRegime",
    
    # Historical Metrics
    "HistoricalMetricsEngine",
    "HistoricalMetric",
    "SeasonalPattern",
    "MarketCycle",
    "TimeFrame",
    "MetricType",
    
    # Evolution Analytics
    "EvolutionAnalyticsEngine",
    "EvolutionPrediction",
    "GeneticIndividual",
    "StrategyMutation",
    "PredictionModel",
    "EvolutionPhase",
    
    # Voice & Audio Features
    "VoiceFeatures",
    "Language",
    "VoiceEmotion",
    "VoiceCommand",
    "VoiceCommandType",
    "AudioFeatures",
    "VoiceAnalysis",
    "voice_features",
    "process_voice_command",
    "speech_to_text",
    "text_to_speech",
    "detect_language",
    "analyze_voice_sentiment",
    
    # STT & TTS
    "STTEngine",
    "TTSEngine",
    "STTProvider",
    "TTSProvider",
    "VoiceSettings",
    "STTResult",
    "TTSResult",
    "StreamingSTT",
    "StreamingTTS",
    "stt_engine",
    "tts_engine",
    "transcribe_audio",
    "synthesize_speech",
    "get_streaming_stt",
    "get_streaming_tts",
    "create_voice_settings",
    
    # Audio Analysis
    "AudioAnalyzer",
    "AudioAnalysisResult",
    "EmotionDetectionResult",
    "SpeakerProfile",
    "AudioQuality",
    "AudioEffect",
    "AudioEnhancementSettings",
    "audio_analyzer",
    "analyze_audio",
    "detect_emotion",
    "identify_speaker",
    "enhance_audio",
    "train_speaker_model",
    "get_speaker_profiles",
    
    # A2C Algorithm (if available)
    "AdvantageA2C",
    "TradingConfig", 
    "A2CTrainer",
    
    # Visual Intelligence
    "VisualIntelligence",
    "VisualAnalysisResult",
    "VisualSignalType",
    "AnalysisConfidence",
    "MarketMicrostructureData",
    "VisualSignal",
    
    # Chart Analysis
    "ChartAnalyzer",
    "PatternType",
    "TrendDirection",
    "CandlestickPattern",
    "TechnicalPattern",
    "TrendLine",
    "SupportResistance",
    "VolumeProfile",
    
    # OCR Module
    "OCRProcessor",
    "TextAnalyzer",
    "TableExtractor",
    "DocumentAnalyzer",
    "ImageEnhancer",
    "BatchProcessor",
    "TextExtraction",
    "ChartTextData",
    "DocumentAnalysis",
    "TableData",
    "TextType",
    "DocumentType",
    "ProcessingStatus",
    
    # Performance Optimization Engine
    "PerformanceOptimizer",
    "CacheManager",
    "LoadBalancer",
    "ModelManager",
    "ResourceMonitor",
    "CostTracker",
    "AsyncProcessor",
    "AutoScaler",
    "MemoryCache",
    "RedisCache",
    "PerformanceMetrics",
    "ResourceUsage",
    "CostMetrics",
    "CacheEntry",
    "LoadBalancedNode",
    "ModelPerformance",
    "OptimizationLevel",
    "CacheStrategy",
    "LoadBalanceStrategy",
    "ModelType",
    "performance_monitor",
    "cache_result",
    "rate_limiter"
]

# Modul konfiguratsiyasi
MODULE_CONFIG = {
    "version": __version__,
    "author": __author__,
    "description": "AI Agent Controller for Trading System with Voice & Audio Features",
    "components": {
        "agent_controller": "Asosiy agent boshqaruvchi tizim",
        "event_bus": "Event-driven communication",
        "load_balancer": "Load balancing",
        "failover_manager": "Failover management",
        "strategy_generator": "AI-driven strategy generation",
        "backtester": "Comprehensive backtesting system",
        "training_pipeline": "Auto-learning va model training pipeline",
        "model_updater": "Model yangilash va monitoring tizimi",
        "risk_manager": "Comprehensive risk management system",
        "strategy_evolution": "Strategy evolution tracking va monitoring tizimi",
        "historical_metrics": "Historical metrics analysis va seasonal patterns",
        "evolution_analytics": "Machine learning predictions va genetic algorithms",
        "visual_intelligence": "Vizual ma'lumotlar tahlil tizimi - chart analysis, OCR, pattern detection",
        "chart_analysis": "Chart va technical pattern tahlil moduli",
        "ocr_module": "OCR va hujjat tahlil moduli",
        "voice_features": "Voice & Audio Features tizimi",
        "stt_tts": "Speech-to-Text va Text-to-Speech funksiyalari",
        "audio_analysis": "Audio tahlil va qayta ishlash tizimi",
        "performance_optimization": "Performance optimization engine - response time, caching, load balancing, resource management"
    }
}

def get_module_info():
    """Modul haqida ma'lumot olish"""
    return MODULE_CONFIG

def validate_dependencies():
    """Modul bog'liqliklarini tekshirish"""
    try:
        import asyncio
        import json
        import logging
        import threading
        import queue
        import uuid
        from dataclasses import dataclass
        from datetime import datetime
        from enum import Enum
        from typing import Dict, List, Optional, Any, Callable
        from pathlib import Path
        from collections import defaultdict, deque
        from concurrent.futures import ThreadPoolExecutor
        return True
    except ImportError as e:
        print(f"❌ Dependency validation failed: {e}")
        return False

# Modul yuklanishida bog'liqliklarni tekshirish
if not validate_dependencies():
    raise ImportError("AI Modules uchun zarur kutubxonalar topilmadi")