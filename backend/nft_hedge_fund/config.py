"""
Configuration file for NFT Hedge Fund System
Centralized configuration for all system components
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

@dataclass
class OracleConfig:
    """Oracle provider configuration"""
    name: str
    provider_type: str
    api_key: str
    endpoint: str
    weight: float
    timeout: float
    retry_count: int
    enabled: bool

@dataclass
class StrategyConfig:
    """Hedging strategy configuration"""
    name: str
    enabled: bool
    weight: float
    parameters: Dict[str, any]

@dataclass
class RiskConfig:
    """Risk management configuration"""
    max_drawdown: float
    var_limit: float
    concentration_limit: float
    position_size_limit: float
    leverage_limit: float
    stop_loss_pct: float

@dataclass
class QuantumConfig:
    """Quantum algorithm configuration"""
    enabled: bool
    quantum_depth: int
    coherence_threshold: float
    entanglement_strength: float
    annealing_steps: int
    optimization_rounds: int

@dataclass
class GovernanceConfig:
    """Governance system configuration"""
    proposal_quorum: float
    proposal_pass_threshold: float
    voting_period_days: float
    emergency_pause_enabled: bool
    performance_fee_max: float
    management_fee_max: float

@dataclass
class SystemConfig:
    """Main system configuration"""
    environment: Environment
    fund_name: str
    initial_capital: float
    min_trade_size: float
    max_trade_size: float
    rebalancing_frequency: str  # daily, weekly, monthly
    auto_rebalance: bool
    risk_limit_enabled: bool
    quantum_enhancement: bool
    
    # Oracle configuration
    oracle_providers: List[OracleConfig]
    
    # Strategy configuration
    strategies: List[StrategyConfig]
    
    # Risk configuration
    risk_config: RiskConfig
    
    # Quantum configuration
    quantum_config: QuantumConfig
    
    # Governance configuration
    governance_config: GovernanceConfig
    
    # Logging configuration
    log_level: str
    log_file: str
    log_max_size: int  # MB
    log_backup_count: int
    
    # Database configuration
    database_url: str
    cache_enabled: bool
    cache_ttl: int  # seconds
    
    # API configuration
    api_host: str
    api_port: int
    api_rate_limit: int
    
class Config:
    """Configuration manager for NFT Hedge Fund System"""
    
    def __init__(self, env: str = "development"):
        self.environment = Environment(env)
        self.config = self._load_config()
    
    def _load_config(self) -> SystemConfig:
        """Load configuration based on environment"""
        
        if self.environment == Environment.DEVELOPMENT:
            return self._development_config()
        elif self.environment == Environment.TESTING:
            return self._testing_config()
        else:  # PRODUCTION
            return self._production_config()
    
    def _development_config(self) -> SystemConfig:
        """Development environment configuration"""
        
        return SystemConfig(
            environment=self.environment,
            fund_name="QuantumMetal NFT Fund (Dev)",
            initial_capital=1000000,  # $1M for development
            min_trade_size=1000.0,    # $1K minimum
            max_trade_size=100000.0,  # $100K maximum
            rebalancing_frequency="daily",
            auto_rebalance=True,
            risk_limit_enabled=True,
            quantum_enhancement=True,
            
            # Oracle providers
            oracle_providers=[
                OracleConfig(
                    name="ChainlinkDev",
                    provider_type="chainlink",
                    api_key="dev_chainlink_key",
                    endpoint="https://dev-chainlink.example.com",
                    weight=1.0,
                    timeout=5.0,
                    retry_count=3,
                    enabled=True
                ),
                OracleConfig(
                    name="TradingViewDev", 
                    provider_type="tradingview",
                    api_key="dev_tradingview_key",
                    endpoint="https://dev-tradingview.example.com",
                    weight=0.8,
                    timeout=10.0,
                    retry_count=2,
                    enabled=True
                )
            ],
            
            # Hedging strategies
            strategies=[
                StrategyConfig(
                    name="static_dynamic",
                    enabled=True,
                    weight=0.40,
                    parameters={
                        "base_hedge_ratio": 0.60,
                        "volatility_threshold": 0.25,
                        "trend_lookback": 20
                    }
                ),
                StrategyConfig(
                    name="volatility_targeting",
                    enabled=True,
                    weight=0.30,
                    parameters={
                        "target_volatility": 0.10,
                        "correlation_window": 60,
                        "rebalancing_frequency": 1
                    }
                ),
                StrategyConfig(
                    name="quantum_superposition",
                    enabled=True,
                    weight=0.20,
                    parameters={
                        "superposition_states": 4,
                        "coherence_decay": 0.95,
                        "measurement_threshold": 0.7
                    }
                ),
                StrategyConfig(
                    name="cross_metal_arbitrage",
                    enabled=True,
                    weight=0.10,
                    parameters={
                        "correlation_threshold": 0.7,
                        "arbitrage_threshold": 0.03
                    }
                )
            ],
            
            # Risk management
            risk_config=RiskConfig(
                max_drawdown=0.20,      # 20% max drawdown
                var_limit=0.05,         # 5% daily VaR limit
                concentration_limit=0.30, # 30% max concentration
                position_size_limit=0.10, # 10% max position size
                leverage_limit=2.0,     # 2x max leverage
                stop_loss_pct=0.05      # 5% stop loss
            ),
            
            # Quantum algorithms
            quantum_config=QuantumConfig(
                enabled=True,
                quantum_depth=10,
                coherence_threshold=0.85,
                entanglement_strength=0.1,
                annealing_steps=100,
                optimization_rounds=5
            ),
            
            # Governance system
            governance_config=GovernanceConfig(
                proposal_quorum=0.10,          # 10% quorum
                proposal_pass_threshold=0.60,  # 60% supermajority
                voting_period_days=7.0,
                emergency_pause_enabled=True,
                performance_fee_max=0.50,      # 50% max performance fee
                management_fee_max=0.10        # 10% max management fee
            ),
            
            # Logging
            log_level="INFO",
            log_file="logs/nft_hedge_fund_dev.log",
            log_max_size=100,  # 100MB
            log_backup_count=5,
            
            # Database
            database_url="sqlite:///nft_hedge_fund_dev.db",
            cache_enabled=True,
            cache_ttl=300,  # 5 minutes
            
            # API
            api_host="localhost",
            api_port=8000,
            api_rate_limit=1000  # requests per minute
        )
    
    def _testing_config(self) -> SystemConfig:
        """Testing environment configuration"""
        
        config = self._development_config()
        
        # Override for testing
        config.environment = Environment.TESTING
        config.fund_name = "QuantumMetal NFT Fund (Test)"
        config.initial_capital = 100000  # $100K for testing
        config.log_level = "DEBUG"
        config.database_url = "sqlite:///nft_hedge_fund_test.db"
        
        # Disable oracles for testing (use mock data)
        for oracle in config.oracle_providers:
            oracle.enabled = False
        
        # Disable real trading in tests
        config.min_trade_size = 0.01
        config.max_trade_size = 1000.0
        config.auto_rebalance = False
        
        return config
    
    def _production_config(self) -> SystemConfig:
        """Production environment configuration"""
        
        return SystemConfig(
            environment=self.environment,
            fund_name="QuantumMetal NFT Fund",
            initial_capital=100000000,  # $100M for production
            min_trade_size=10000.0,     # $10K minimum
            max_trade_size=10000000.0,  # $10M maximum
            rebalancing_frequency="daily",
            auto_rebalance=True,
            risk_limit_enabled=True,
            quantum_enhancement=True,
            
            # Oracle providers (production endpoints)
            oracle_providers=[
                OracleConfig(
                    name="ChainlinkProd",
                    provider_type="chainlink",
                    api_key=os.getenv("CHAINLINK_API_KEY", ""),
                    endpoint="https://prod-chainlink.example.com",
                    weight=1.2,
                    timeout=3.0,
                    retry_count=5,
                    enabled=True
                ),
                OracleConfig(
                    name="BloombergProd",
                    provider_type="bloomberg", 
                    api_key=os.getenv("BLOOMBERG_API_KEY", ""),
                    endpoint="https://prod-bloomberg.example.com",
                    weight=1.0,
                    timeout=2.0,
                    retry_count=3,
                    enabled=True
                ),
                OracleConfig(
                    name="TradingViewProd",
                    provider_type="tradingview",
                    api_key=os.getenv("TRADINGVIEW_API_KEY", ""),
                    endpoint="https://prod-tradingview.example.com",
                    weight=0.8,
                    timeout=5.0,
                    retry_count=3,
                    enabled=True
                )
            ],
            
            # Hedging strategies (optimized weights)
            strategies=[
                StrategyConfig(
                    name="static_dynamic",
                    enabled=True,
                    weight=0.35,
                    parameters={
                        "base_hedge_ratio": 0.65,
                        "volatility_threshold": 0.20,
                        "trend_lookback": 30
                    }
                ),
                StrategyConfig(
                    name="volatility_targeting",
                    enabled=True,
                    weight=0.35,
                    parameters={
                        "target_volatility": 0.08,
                        "correlation_window": 90,
                        "rebalancing_frequency": 1
                    }
                ),
                StrategyConfig(
                    name="quantum_superposition",
                    enabled=True,
                    weight=0.20,
                    parameters={
                        "superposition_states": 8,
                        "coherence_decay": 0.98,
                        "measurement_threshold": 0.8
                    }
                ),
                StrategyConfig(
                    name="cross_metal_arbitrage",
                    enabled=True,
                    weight=0.10,
                    parameters={
                        "correlation_threshold": 0.75,
                        "arbitrage_threshold": 0.02
                    }
                )
            ],
            
            # Risk management (conservative limits)
            risk_config=RiskConfig(
                max_drawdown=0.15,      # 15% max drawdown
                var_limit=0.03,         # 3% daily VaR limit
                concentration_limit=0.25, # 25% max concentration
                position_size_limit=0.05, # 5% max position size
                leverage_limit=1.5,     # 1.5x max leverage
                stop_loss_pct=0.03      # 3% stop loss
            ),
            
            # Quantum algorithms (enhanced)
            quantum_config=QuantumConfig(
                enabled=True,
                quantum_depth=20,
                coherence_threshold=0.90,
                entanglement_strength=0.15,
                annealing_steps=200,
                optimization_rounds=10
            ),
            
            # Governance system
            governance_config=GovernanceConfig(
                proposal_quorum=0.15,          # 15% quorum for production
                proposal_pass_threshold=0.67,  # 67% supermajority
                voting_period_days=14.0,       # 2 weeks voting
                emergency_pause_enabled=True,
                performance_fee_max=0.30,      # 30% max performance fee
                management_fee_max=0.05        # 5% max management fee
            ),
            
            # Logging (production settings)
            log_level="WARNING",
            log_file="logs/nft_hedge_fund_prod.log",
            log_max_size=500,  # 500MB
            log_backup_count=10,
            
            # Database (production database)
            database_url=os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/nft_hedge_fund"),
            cache_enabled=True,
            cache_ttl=60,  # 1 minute
            
            # API (production settings)
            api_host="0.0.0.0",  # Listen on all interfaces
            api_port=8080,
            api_rate_limit=10000  # Higher rate limit
        )
    
    def get_config(self) -> SystemConfig:
        """Get the loaded configuration"""
        return self.config
    
    def get_oracle_config(self, name: str) -> Optional[OracleConfig]:
        """Get configuration for specific oracle provider"""
        for oracle in self.config.oracle_providers:
            if oracle.name == name:
                return oracle
        return None
    
    def get_strategy_config(self, name: str) -> Optional[StrategyConfig]:
        """Get configuration for specific strategy"""
        for strategy in self.config.strategies:
            if strategy.name == name:
                return strategy
        return None
    
    def is_strategy_enabled(self, name: str) -> bool:
        """Check if strategy is enabled"""
        strategy = self.get_strategy_config(name)
        return strategy.enabled if strategy else False
    
    def get_strategy_weight(self, name: str) -> float:
        """Get strategy weight"""
        strategy = self.get_strategy_config(name)
        return strategy.weight if strategy else 0.0
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return any errors"""
        errors = []
        
        # Validate oracle configurations
        for oracle in self.config.oracle_providers:
            if oracle.enabled:
                if not oracle.api_key:
                    errors.append(f"Oracle {oracle.name} is enabled but no API key provided")
                if oracle.weight <= 0:
                    errors.append(f"Oracle {oracle.name} has invalid weight: {oracle.weight}")
        
        # Validate strategy configurations
        total_weight = sum(strategy.weight for strategy in self.config.strategies if strategy.enabled)
        if abs(total_weight - 1.0) > 0.01:
            errors.append(f"Strategy weights should sum to 1.0, got {total_weight}")
        
        # Validate risk parameters
        if self.config.risk_config.max_drawdown <= 0 or self.config.risk_config.max_drawdown >= 1:
            errors.append(f"Invalid max_drawdown: {self.config.risk_config.max_drawdown}")
        
        if self.config.risk_config.var_limit <= 0 or self.config.risk_config.var_limit >= 1:
            errors.append(f"Invalid var_limit: {self.config.risk_config.var_limit}")
        
        # Validate quantum parameters
        if self.config.quantum_config.enabled:
            if self.config.quantum_config.quantum_depth <= 0:
                errors.append(f"Invalid quantum_depth: {self.config.quantum_config.quantum_depth}")
        
        # Validate governance parameters
        if self.config.governance_config.proposal_quorum <= 0 or self.config.governance_config.proposal_quorum >= 1:
            errors.append(f"Invalid proposal_quorum: {self.config.governance_config.proposal_quorum}")
        
        return errors
    
    def save_config(self, filepath: str):
        """Save configuration to JSON file"""
        import json
        from dataclasses import asdict
        
        config_dict = asdict(self.config)
        
        # Convert enums to strings for JSON serialization
        config_dict["environment"] = self.config.environment.value
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)
    
    @classmethod
    def load_config(cls, filepath: str) -> 'Config':
        """Load configuration from JSON file"""
        import json
        from dataclasses import fromdict
        
        with open(filepath, 'r') as f:
            config_dict = json.load(f)
        
        # Create config instance
        env = Environment(config_dict["environment"])
        config = cls(env.value)
        
        # Load custom configuration (simplified for demo)
        # In production, would properly deserialize all fields
        
        return config

# Default configuration instance
default_config = Config(os.getenv("NFT_HEDGE_FUND_ENV", "development"))

def get_config() -> SystemConfig:
    """Get the default configuration"""
    return default_config.get_config()

def get_oracle_config(name: str) -> Optional[OracleConfig]:
    """Get oracle configuration by name"""
    return default_config.get_oracle_config(name)

def get_strategy_config(name: str) -> Optional[StrategyConfig]:
    """Get strategy configuration by name"""
    return default_config.get_strategy_config(name)

def is_strategy_enabled(name: str) -> bool:
    """Check if strategy is enabled"""
    return default_config.is_strategy_enabled(name)

def get_strategy_weight(name: str) -> float:
    """Get strategy weight"""
    return default_config.get_strategy_weight(name)

# Environment-specific configurations
def get_development_config() -> SystemConfig:
    """Get development configuration"""
    config = Config("development")
    return config.get_config()

def get_testing_config() -> SystemConfig:
    """Get testing configuration"""
    config = Config("testing")
    return config.get_config()

def get_production_config() -> SystemConfig:
    """Get production configuration"""
    config = Config("production")
    return config.get_config()

if __name__ == "__main__":
    # Example usage
    import sys
    
    env = sys.argv[1] if len(sys.argv) > 1 else "development"
    
    print(f"Loading {env} configuration...")
    
    config = Config(env)
    config_obj = config.get_config()
    
    print(f"Environment: {config_obj.environment.value}")
    print(f"Fund Name: {config_obj.fund_name}")
    print(f"Initial Capital: ${config_obj.initial_capital:,.2f}")
    
    # Validate configuration
    errors = config.validate_config()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration is valid!")
    
    # Save configuration to file
    config.save_config(f"config_{env}.json")
    print(f"Configuration saved to config_{env}.json")