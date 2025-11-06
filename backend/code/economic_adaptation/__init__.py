"""
Economic Cycle Adaptation va Comprehensive Self-Learning System

Ushbu modul iqtisodiy sikl adaptation va o'z-o'zidan o'rganish tizimini
inobatga olgan holda yaratilgan bo'lib, quyidagi asosiy imkoniyatlarni ta'minlaydi:

- Iqtisodiy sikl tahlili
- Makro-iktisodiy adaptation  
- Comprehensive self-learning
- Performance optimization
- System integration

Author: Economic Adaptation System
Date: 2025-11-03
"""

__version__ = "1.0.0"
__author__ = "Economic Adaptation System"

from .core.cycle_detector import CycleDetector
from .core.indicators import EconomicIndicators
from .core.adaptation_engine import AdaptationEngine
from .core.learning_system import ComprehensiveLearningSystem

__all__ = [
    'CycleDetector',
    'EconomicIndicators', 
    'AdaptationEngine',
    'ComprehensiveLearningSystem'
]