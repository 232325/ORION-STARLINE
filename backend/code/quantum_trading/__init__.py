"""
Quantum Advantage in Multi-asset Trading System
==============================================

Bu modul quyidagilarni o'z ichiga oladi:
1. Multi-Asset Quantum Trading algoritmlari
2. Quantum Advantage Metrics
3. Error Correction tizimlari
4. Quantum Optimization
5. Performance Benchmarks

Yaratuvchi: Quantum Trading Team
 Sana: 2025-11-03
"""

__version__ = "1.0.0"
__author__ = "Quantum Trading Team"

from .multi_asset import QuantumMultiAssetTrader
from .optimization import QuantumOptimizer
from .error_correction import QuantumErrorCorrection
from .metrics import QuantumAdvantageMetrics
from .benchmarks import QuantumBenchmarks

__all__ = [
    "QuantumMultiAssetTrader",
    "QuantumOptimizer", 
    "QuantumErrorCorrection",
    "QuantumAdvantageMetrics",
    "QuantumBenchmarks"
]