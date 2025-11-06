"""
Performance Feedback Loops va Autonomous Decision Making System

Ushbu modul quyidagilarni ta'minlaydi:
- Real-time performance monitoring
- Autonomous trading decisions
- Feedback-driven strategy optimization
- Governance-based decision approval
"""

from .core.system_orchestrator import AutonomousDecisionSystem
from .performance_feedback.monitoring import PerformanceMonitor
from .performance_feedback.attribution import PerformanceAttribution
from .decision_making.trading_agent import TradingAgent
from .decision_making.portfolio_manager import PortfolioManager
from .governance.dao_integration import DAOGovernance

__version__ = "1.0.0"
__author__ = "Autonomous Trading System"

__all__ = [
    "AutonomousDecisionSystem",
    "PerformanceMonitor", 
    "PerformanceAttribution",
    "TradingAgent",
    "PortfolioManager",
    "DAOGovernance"
]