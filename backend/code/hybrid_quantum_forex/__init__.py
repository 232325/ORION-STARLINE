"""
Hybrid Quantum-Classical Forex Arbitrage System
Tizimning asosiy paket fayli
"""

__version__ = "1.0.0"
__author__ = "Hybrid Quantum Forex Development Team"
__description__ = "Quantum-enhanced Forex arbitrage trading system"

# Main components
from .core.orchestrator import (
    HybridQuantumForexSystem,
    initialize_system,
    start_system,
    stop_system,
    get_system_status
)

from .classical.preprocessing import ClassicalPreprocessor
from .classical.postprocessing import ClassicalPostprocessor

from .quantum.core_processor import QuantumProcessor

from .arbitrage.detector import ArbitrageDetector
from .arbitrage.executor import ArbitrageExecutor

from .monitoring.performance_monitor import PerformanceMonitor

from .utils.error_handler import ErrorHandler
from .utils.database import DatabaseManager, setup_database, get_db_manager
from .utils.data_models import *

from .config.config import config, SystemConfig

# Public API
__all__ = [
    # Core system
    'HybridQuantumForexSystem',
    'initialize_system', 
    'start_system',
    'stop_system',
    'get_system_status',
    
    # Components
    'ClassicalPreprocessor',
    'ClassicalPostprocessor', 
    'QuantumProcessor',
    'ArbitrageDetector',
    'ArbitrageExecutor',
    'PerformanceMonitor',
    
    # Utilities
    'ErrorHandler',
    'DatabaseManager',
    'setup_database',
    'get_db_manager',
    
    # Configuration
    'config',
    'SystemConfig',
    
    # Data models
    'MarketData',
    'MarketPrice', 
    'ArbitrageOpportunity',
    'ArbitrageCalculation',
    'TradeExecution',
    'QuantumFeatures',
    'SystemMetrics',
    'AuditLogEntry',
    
    # Enums
    'SystemState',
    'TradeType',
    'ArbitrageType',
    'QuantumState',
    'ErrorSeverity',
    'ErrorCategory'
]

# Package metadata
__all__.extend([
    'CurrencyPair',
    'TIMEZONES', 
    'CURRENCY_PAIRS'
])

# Version info
VERSION_INFO = {
    'major': 1,
    'minor': 0,
    'patch': 0,
    'release': 'stable'
}

def get_version():
    """Get version string"""
    return __version__

def get_version_info():
    """Get detailed version information"""
    return VERSION_INFO.copy()

# Quick start function
async def quick_start(duration_minutes: int = 5):
    """
    Quick system start function
    
    Args:
        duration_minutes: How long to run the system in minutes
        
    Returns:
        bool: Success status
    """
    try:
        from .core.orchestrator import initialize_system, start_system, stop_system
        
        # Initialize
        if not initialize_system():
            return False
        
        # Start
        if not start_system():
            return False
        
        # Run for specified duration
        import asyncio
        await asyncio.sleep(duration_minutes * 60)
        
        # Stop
        stop_system()
        
        return True
        
    except Exception:
        return False

# Demo function
async def run_demo():
    """
    Run system demonstration
    
    Returns:
        bool: Success status
    """
    try:
        from .demo import quick_demo
        return await quick_demo()
    except Exception:
        return False

# Initialize package
def _initialize_package():
    """Package initialization"""
    try:
        # Setup database
        setup_database()
    except Exception:
        pass  # Database setup can fail in some environments

# Auto-initialize
_initialize_package()