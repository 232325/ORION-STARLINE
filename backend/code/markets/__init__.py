"""
AI Trading Evolution - Markets Integration Module
================================================

Bozorlar bilan integratsiya moduli - Commodities, Stocks, Bonds, ETFs, Crypto Derivatives

Author: MiniMax Agent
Version: 1.0.0
Date: 2025-11-04
"""

# Commodities Trading
from .commodities_trading import (
    CommoditiesTrading,
    CommodityType,
    ContractSpec
)

# Stock Market Integration  
from .stock_market_integration import (
    StockMarketIntegration,
    StockExchange,
    StockOrderType,
    StockPosition
)

# Bonds & Treasury
from .bonds_treasury import (
    BondsTreasury,
    BondType,
    BondMaturity,
    TreasuryInstrument
)

# ETFs Trading
from .etfs_trading import (
    ETFsTrading,
    ETFType,
    ETFProvider,
    ETFPosition
)

# Crypto Derivatives
from .crypto_derivatives import (
    CryptoDerivatives,
    DerivativeType,
    OptionType,
    FutureContract
)

# Multi-Market Correlation
from .multi_market_correlation import (
    MultiMarketCorrelation,
    CorrelationMethod,
    MarketData
)

__all__ = [
    # Commodities
    "CommoditiesTrading",
    "CommodityType", 
    "ContractSpec",
    
    # Stocks
    "StockMarketIntegration",
    "StockExchange",
    "StockOrderType",
    "StockPosition",
    
    # Bonds
    "BondsTreasury",
    "BondType",
    "BondMaturity",
    "TreasuryInstrument",
    
    # ETFs
    "ETFsTrading",
    "ETFType",
    "ETFProvider",
    "ETFPosition",
    
    # Crypto Derivatives
    "CryptoDerivatives",
    "DerivativeType",
    "OptionType",
    "FutureContract",
    
    # Multi-Market
    "MultiMarketCorrelation",
    "CorrelationMethod",
    "MarketData"
]
