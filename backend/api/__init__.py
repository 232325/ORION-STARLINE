"""
AI Trading System - RESTful API Package
FastAPI asosida qurilgan to'liq API tizimi
"""

__version__ = "1.0.0"
__author__ = "AI Trading System Team"
__description__ = "Quantum AI, HFT, DAO, NFT va Blockchain texnologiyalari bilan jihoblangan trading tizimi"

# Import main application
from .main import app

# Import models
from .models.schemas import *

# Import utilities
from .utils.cache import cache_manager
from .utils.pagination import *
from .utils.error_handler import *
from .utils.file_operations import file_manager

# Import endpoints
from .endpoints import (
    ai_signals,
    quantum_analysis, 
    blockchain,
    dao_governance,
    hft_engine,
    nft_hedge,
    self_learning
)

# Import auth
from .auth import auth_handler, oauth_handler

# Import websocket
from .websocket.manager import connection_manager

# Package metadata
__all__ = [
    "app",
    "cache_manager", 
    "file_manager",
    "connection_manager",
    "auth_handler",
    "oauth_handler"
]