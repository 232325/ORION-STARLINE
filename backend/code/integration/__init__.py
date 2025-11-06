"""
Module Integration System
========================

Bu modul barcha AI trading, quantum computing, blockchain va boshqa
komponentlar o'rtasida integratsiya ta'minlaydi.

Asosiy Integration Komponentlar:
- IntegrationHub: Barcha komponentlar uchun birlashgan hub
- PerformanceOptimizer: Tizim performansini optimizatsiya qilish
- SecurityAuditor: Xavfsizlik auditini ta'minlash

Qo'shimcha komponentlar:
- Core Integration Framework
- AI Trading Integration  
- Quantum Integration
- Blockchain Integration
- System Integration
"""

__version__ = "1.0.0"
__author__ = "Module Integration Team"

# Import asosiy komponentlar
from .core.integration_manager import IntegrationManager
from .core.plugin_manager import PluginManager
from .core.service_discovery import ServiceDiscovery
from .core.event_system import EventSystem
from .core.message_queue import MessageQueue

# Import asosiy integration komponentlari
from .integration_hub import IntegrationHub
from .performance_optimizer import PerformanceOptimizer
from .security_auditor import SecurityAuditor

# Import AI trading integration
from .ai_trading.model_integration import ModelIntegration
from .ai_trading.signal_aggregator import SignalAggregator
from .ai_trading.performance_tracker import PerformanceTracker

# Import quantum integration
from .quantum.quantum_integration import QuantumIntegration
from .quantum.hybrid_system import HybridQuantumSystem
from .quantum.resource_manager import QuantumResourceManager

# Import blockchain integration
from .blockchain.chain_integration import ChainIntegration
from .blockchain.smart_contract import SmartContractIntegration
from .blockchain.cross_chain import CrossChainIntegration

# Import system integration
from .system.data_pipeline import DataPipeline
from .system.microservices import MicroserviceCommunication
from .system.event_streaming import EventStreaming

__all__ = [
    # Core
    'IntegrationManager', 'PluginManager', 'ServiceDiscovery', 'EventSystem', 'MessageQueue',
    
    # Asosiy Integration komponentlari
    'IntegrationHub', 'PerformanceOptimizer', 'SecurityAuditor',
    
    # AI Trading
    'ModelIntegration', 'SignalAggregator', 'PerformanceTracker',
    
    # Quantum
    'QuantumIntegration', 'HybridQuantumSystem', 'QuantumResourceManager',
    
    # Blockchain
    'ChainIntegration', 'SmartContractIntegration', 'CrossChainIntegration',
    
    # System
    'DataPipeline', 'MicroserviceCommunication', 'EventStreaming'
]