"""
Advanced Risk Management System
==============================

Comprehensive risk management platform for high-frequency trading systems
with real-time monitoring, advanced analytics, and compliance features.

Modules:
- core: Main risk management engine
- monitoring: Real-time risk monitoring
- analytics: Risk analytics and calculations
- compliance: Regulatory compliance
- integrations: External system integrations
"""

__version__ = "1.0.0"
__author__ = "Risk Management System"

from .core.risk_manager import RiskManager
from .core.position_monitor import PositionMonitor
from .core.risk_limits import RiskLimits
from .monitoring.real_time_monitor import RealTimeMonitor
from .analytics.var_calculator import VaRCalculator
from .analytics.stress_tester import StressTester
from .analytics.analytics_engine import AnalyticsEngine

__all__ = [
    "RiskManager",
    "PositionMonitor", 
    "RiskLimits",
    "RealTimeMonitor",
    "VaRCalculator",
    "StressTester",
    "AnalyticsEngine"
]