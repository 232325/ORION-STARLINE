"""
Cross-Chain Asset Management tizimi konfiguratsiyasi
Ko'p zanjirli asset boshqaruv tizimi uchun barcha sozlamalar
"""

import os
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class ChainType(Enum):
    """Zanjir turlari"""
    ETHEREUM = "ethereum"
    BSC = "bsc"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"

class BridgeType(Enum):
    """Ko'prik turlari"""
    LOCK_MINT = "lock_mint"
    BURN_MINT = "burn_mint"
    ATOMIC_SWAP = "atomic_swap"
    WRAPPED_ASSET = "wrapped_asset"

@dataclass
class ChainConfig:
    """Zanjir konfiguratsiyasi"""
    name: str
    chain_id: int
    rpc_url: str
    explorer_url: str
    native_token: str
    gas_limit: int
    confirmation_blocks: int
    block_time: float

@dataclass
class BridgeConfig:
    """Ko'prik konfiguratsiyasi"""
    source_chain: str
    target_chain: str
    bridge_type: BridgeType
    fee_percentage: float
    min_amount: int
    max_amount: int
    timeout_blocks: int

@dataclass
class SecurityConfig:
    """Xavfsizlik konfiguratsiyasi"""
    multi_sig_threshold: int
    oracle_count: int
    emergency_pause_duration: int
    slashing_threshold: float
    insurance_percentage: float

# Zanjir konfiguratsiyasi
CHAIN_CONFIGS = {
    ChainType.ETHEREUM: ChainConfig(
        name="Ethereum Mainnet",
        chain_id=1,
        rpc_url=os.getenv("ETHEREUM_RPC", "https://mainnet.infura.io/v3/"),
        explorer_url="https://etherscan.io",
        native_token="ETH",
        gas_limit=200000,
        confirmation_blocks=12,
        block_time=13.0
    ),
    ChainType.BSC: ChainConfig(
        name="Binance Smart Chain",
        chain_id=56,
        rpc_url=os.getenv("BSC_RPC", "https://bsc-dataseed.binance.org/"),
        explorer_url="https://bscscan.com",
        native_token="BNB",
        gas_limit=150000,
        confirmation_blocks=3,
        block_time=3.0
    ),
    ChainType.POLYGON: ChainConfig(
        name="Polygon",
        chain_id=137,
        rpc_url=os.getenv("POLYGON_RPC", "https://polygon-rpc.com/"),
        explorer_url="https://polygonscan.com",
        native_token="MATIC",
        gas_limit=200000,
        confirmation_blocks=200,
        block_time=2.1
    ),
    ChainType.ARBITRUM: ChainConfig(
        name="Arbitrum One",
        chain_id=42161,
        rpc_url=os.getenv("ARBITRUM_RPC", "https://arb1.arbitrum.io/rpc"),
        explorer_url="https://arbiscan.io",
        native_token="ETH",
        gas_limit=100000,
        confirmation_blocks=20,
        block_time=2.0
    ),
    ChainType.OPTIMISM: ChainConfig(
        name="Optimism",
        chain_id=10,
        rpc_url=os.getenv("OPTIMISM_RPC", "https://mainnet.optimism.io"),
        explorer_url="https://optimistic.etherscan.io",
        native_token="ETH",
        gas_limit=100000,
        confirmation_blocks=20,
        block_time=2.0
    )
}

# Ko'prik konfiguratsiyasi
BRIDGE_CONFIGS = [
    BridgeConfig(
        source_chain="ethereum",
        target_chain="bsc",
        bridge_type=BridgeType.LOCK_MINT,
        fee_percentage=0.003,  # 0.3%
        min_amount=10**15,     # 0.001 ETH
        max_amount=10**22,     # 10000 ETH
        timeout_blocks=720     # ~3 soat
    ),
    BridgeConfig(
        source_chain="ethereum",
        target_chain="polygon",
        bridge_type=BridgeType.LOCK_MINT,
        fee_percentage=0.002,  # 0.2%
        min_amount=10**15,
        max_amount=10**22,
        timeout_blocks=720
    ),
    BridgeConfig(
        source_chain="ethereum",
        target_chain="arbitrum",
        bridge_type=BridgeType.WRAPPED_ASSET,
        fee_percentage=0.001,  # 0.1%
        min_amount=10**15,
        max_amount=10**22,
        timeout_blocks=144     # ~12 daqiqa
    ),
    BridgeConfig(
        source_chain="ethereum",
        target_chain="optimism",
        bridge_type=BridgeType.WRAPPED_ASSET,
        fee_percentage=0.001,
        min_amount=10**15,
        max_amount=10**22,
        timeout_blocks=144
    )
]

# Xavfsizlik konfiguratsiyasi
SECURITY_CONFIG = SecurityConfig(
    multi_sig_threshold=3,
    oracle_count=7,
    emergency_pause_duration=86400,  # 24 soat
    slashing_threshold=0.01,  # 1%
    insurance_percentage=0.005  # 0.5%
)

# Asset konfiguratsiyasi
ASSET_CONFIGS = {
    "ETH": {
        "decimals": 18,
        "wrappers": {
            "bsc": "0x...",  # WETH
            "polygon": "0x...",  # WETH
            "arbitrum": "0x...",  # WETH
            "optimism": "0x..."   # WETH
        }
    },
    "USDC": {
        "decimals": 6,
        "wrappers": {
            "bsc": "0x...",  # USDC BSC
            "polygon": "0x...",  # USDC Polygon
            "arbitrum": "0x...",  # USDC Arbitrum
            "optimism": "0x..."   # USDC Optimism
        }
    },
    "USDT": {
        "decimals": 6,
        "wrappers": {
            "bsc": "0x...",  # USDT BSC
            "polygon": "0x...",  # USDT Polygon
            "arbitrum": "0x...",  # USDT Arbitrum
            "optimism": "0x..."   # USDT Optimism
        }
    }
}

# Oracle manbahlari
ORACLE_SOURCES = [
    "chainlink",
    "band_protocol",
    "api3",
    "tellor",
    "dia_data"
]

# Multi-sig valiyatorlar
MULTI_SIG_SIGNERS = [
    "0x742d35Cc6a12F8C71EdBD49E1a5d3f76E32C2c7d",
    "0x8ba1f109551bD432803012645Hac136c23E3d441",
    "0x7B8F0579Cc7A9cD4c0A1C8d4E1C3a2B4d5E6F7A8",
    "0x9c4F5D2B8e4A3F6d9A1C7e3F5B2d8A9E6F3c7B2A5",
    "0x2d8E4a6F3b9c7D5E1A8b3F6c2D5E9A4F7b8C3D6E9"
]

# Relay network tugunlari
RELAY_NODES = [
    "https://relay1.cross-chain.io",
    "https://relay2.cross-chain.io",
    "https://relay3.cross-chain.io"
]

# Gas narxlari (wei)
GAS_PRICES = {
    ChainType.ETHEREUM: 20000000000,    # 20 gwei
    ChainType.BSC: 5000000000,          # 5 gwei
    ChainType.POLYGON: 30000000000,     # 30 gwei
    ChainType.ARBITRUM: 1000000000,     # 1 gwei
    ChainType.OPTIMISM: 1000000000      # 1 gwei
}

# Rate limiting
RATE_LIMITS = {
    "transactions_per_hour": 100,
    "max_amount_per_hour": 10**20,  # 100 ETH
    "max_bridges_per_user": 50
}

# Monitoring sozlamalari
MONITORING_CONFIG = {
    "health_check_interval": 30,  # soniya
    "metrics_retention_days": 30,
    "alert_thresholds": {
        "gas_price_spike": 5.0,
        "congestion_threshold": 0.8,
        "bridge_failure_rate": 0.05
    }
}