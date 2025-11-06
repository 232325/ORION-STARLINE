"""
Risk Management System Configuration
===================================

Comprehensive configuration for the Advanced Risk Management System.
Allows customization of all components including monitoring, analytics,
compliance, and integrations.
"""

from typing import Dict, List, Any

def get_default_config() -> Dict[str, Any]:
    """Get default risk management system configuration"""
    
    return {
        # Core Risk Management Configuration
        "risk_manager": {
            "assessment_interval": 60,  # seconds
            "var_threshold": 1000000,   # $1M VaR threshold
            "max_drawdown_limit": 0.15,  # 15% max drawdown
            "emergency_shutdown_enabled": True
        },
        
        # Position Monitoring Configuration
        "position_monitor": {
            "update_interval": 1.0,  # seconds
            "history_retention": 24,  # hours
            "limit_check_interval": 5.0,  # seconds
            "position_change_threshold": 0.001,  # 0.1%
            "max_positions": 1000,
            "position_loss_limit": 0.1  # 10% loss limit per position
        },
        
        # Risk Limits Configuration
        "risk_limits": {
            "var_threshold": 1000000,  # $1M VaR limit
            "max_drawdown_limit": 0.15,  # 15% drawdown limit
            "max_concentration": 0.25,  # 25% max concentration
            "max_gross_exposure": 10000000  # $10M max exposure
        },
        
        # Real-time Monitoring Configuration
        "real_time_monitor": {
            "update_interval": 1.0,  # seconds
            "market_data_ttl": 60,  # seconds
            "max_events_per_minute": 100,
            "price_change_threshold": 0.05,  # 5% price change
            "volume_spike_threshold": 2.0,  # 2x normal volume
            "spread_threshold": 0.01,  # 1% spread
            "liquidity_threshold": 0.1  # Low liquidity threshold
        },
        
        # VaR Calculator Configuration
        "var_calculator": {
            "cache_ttl": 300,  # 5 minutes
            "monte_carlo_simulations": 10000,
            "historical_window": 252,  # days
            "confidence_levels": [0.95, 0.99],
            "calculation_methods": ["historical", "parametric", "monte_carlo"]
        },
        
        # Stress Testing Configuration
        "stress_tester": {
            "scenarios_enabled": [
                "market_crash",
                "volatility_spike", 
                "liquidity_crisis",
                "correlation_breakdown",
                "interest_rate_shock",
                "currency_devaluation",
                "commodity_price_shock"
            ],
            "custom_scenarios": [],
            "stress_test_frequency": 3600,  # 1 hour
            "scenario_probabilities": {
                "market_crash": 0.02,
                "volatility_spike": 0.05,
                "liquidity_crisis": 0.01
            }
        },
        
        # Analytics Engine Configuration
        "analytics_engine": {
            "enable_var": True,
            "enable_stress_testing": True,
            "enable_monte_carlo": True,
            "enable_risk_attribution": True,
            "enable_backtesting": True,
            "var_calculation_frequency": 900,  # 15 minutes
            "monte_carlo_simulations": 10000,
            "backtesting_periods": 100
        },
        
        # Compliance Engine Configuration
        "compliance_engine": {
            "basel3_compliance": True,
            "capital_requirements": {
                "common_equity_ratio": 0.045,  # 4.5%
                "total_capital_ratio": 0.08,   # 8%
                "conservation_buffer": 0.025   # 2.5%
            },
            "leverage_ratio": 0.03,  # 3%
            "liquidity_coverage_ratio": 1.0,  # 100%
            "net_stable_funding_ratio": 1.0,  # 100%
            "concentration_limits": {
                "single_counterparty": 0.25,  # 25%
                "sector_concentration": 0.40,  # 40%
                "geographic_concentration": 0.50  # 50%
            }
        },
        
        # Data Management Configuration
        "data_config": {
            "database_path": "risk_data.db",
            "data_retention_days": 365,
            "real_time_buffer_size": 1000,
            "data_validation_enabled": True,
            "backup_enabled": True,
            "backup_interval_hours": 24
        },
        
        # Alert System Configuration
        "alert_config": {
            "email_config": {
                "smtp_server": "localhost",
                "smtp_port": 587,
                "from_address": "risk@company.com",
                "to_addresses": ["admin@company.com", "risk-officer@company.com"]
            },
            "sms_config": {
                "provider": "twilio",
                "account_sid": "",
                "auth_token": "",
                "from_number": ""
            },
            "webhook_config": {
                "url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
            },
            "slack_config": {
                "token": "",
                "channel": "#risk-alerts"
            }
        },
        
        # Integration Framework Configuration
        "integration_framework": {
            "hft_engine_enabled": True,
            "dao_governance_enabled": True,
            "blockchain_enabled": True,
            "ml_models_enabled": True,
            "external_feeds_enabled": True,
            "integration_interval": 5,  # seconds
            "retry_attempts": 3,
            "timeout": 30
        },
        
        # HFT Engine Integration Configuration
        "hft_engine_config": {
            "engine_endpoint": "http://localhost:8080",
            "api_key": "",
            "timeout": 30,
            "max_retries": 3,
            "sync_interval": 1,  # seconds
            "position_buffer_size": 100
        },
        
        # DAO Governance Integration Configuration
        "dao_governance_config": {
            "governance_contract_address": "",
            "rpc_endpoint": "http://localhost:8545",
            "private_key": "",
            "chain_id": 1,
            "proposal_threshold": 100,
            "voting_period": 7,  # days
            "execution_delay": 2  # days
        },
        
        # Blockchain Integration Configuration
        "blockchain_config": {
            "network_rpc": "http://localhost:8545",
            "contract_address": "",
            "private_key": "",
            "chain_id": 1,
            "gas_limit": 200000,
            "gas_price": 20
        },
        
        # ML Models Integration Configuration
        "ml_models_config": {
            "models_endpoint": "http://localhost:5000",
            "api_key": "",
            "model_names": ["var_predictor", "stress_predictor", "liquidity_predictor"],
            "prediction_timeout": 30,
            "update_interval": 3600  # 1 hour
        },
        
        # External Data Feeds Configuration
        "external_feeds_config": {
            "feeds_enabled": ["market_data", "news", "economic_data", "sentiment"],
            "data_provider_apis": {
                "bloomberg": "",
                "reuters": "",
                "alpha_vantage": "",
                "news_api": ""
            },
            "update_frequency": 1,  # seconds
            "data_retention_hours": 24,
            "quality_checks": True
        },
        
        # Logging Configuration
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "risk_management.log",
            "max_file_size": "10MB",
            "backup_count": 5
        },
        
        # Performance Configuration
        "performance": {
            "max_concurrent_calculations": 10,
            "calculation_timeout": 300,  # seconds
            "cache_size_limit": 1000,
            "memory_limit_mb": 1024,
            "cpu_limit_percent": 80
        }
    }

def get_production_config() -> Dict[str, Any]:
    """Get production-optimized configuration"""
    
    config = get_default_config()
    
    # Production-specific adjustments
    config["logging"]["level"] = "WARNING"
    config["risk_manager"]["assessment_interval"] = 30  # Faster assessment
    config["position_monitor"]["update_interval"] = 0.5  # More frequent updates
    config["analytics_engine"]["monte_carlo_simulations"] = 50000  # Higher precision
    config["integration_framework"]["retry_attempts"] = 5  # More resilient
    
    return config

def get_development_config() -> Dict[str, Any]:
    """Get development-optimized configuration"""
    
    config = get_default_config()
    
    # Development-specific adjustments
    config["logging"]["level"] = "DEBUG"
    config["risk_manager"]["assessment_interval"] = 300  # Slower for development
    config["position_monitor"]["update_interval"] = 5.0  # Less frequent updates
    config["analytics_engine"]["monte_carlo_simulations"] = 1000  # Faster calculations
    config["data_config"]["data_retention_days"] = 7  # Shorter retention
    
    return config

def get_testing_config() -> Dict[str, Any]:
    """Get testing configuration"""
    
    config = get_default_config()
    
    # Testing-specific adjustments
    config["logging"]["level"] = "ERROR"
    config["risk_manager"]["assessment_interval"] = 600  # Very slow for testing
    config["position_monitor"]["update_interval"] = 10.0  # Very infrequent updates
    config["analytics_engine"]["monte_carlo_simulations"] = 100  # Minimal simulations
    config["data_config"]["data_retention_days"] = 1  # Minimal retention
    config["integration_framework"]["hft_engine_enabled"] = False  # Disable real integrations
    
    return config

def get_environment_config(env: str = "development") -> Dict[str, Any]:
    """Get configuration based on environment"""
    
    environment_configs = {
        "development": get_development_config(),
        "production": get_production_config(),
        "testing": get_testing_config(),
        "default": get_default_config()
    }
    
    return environment_configs.get(env, environment_configs["default"])

def validate_config(config: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate configuration and return any issues"""
    
    issues = {}
    
    # Check required sections
    required_sections = [
        "risk_manager", "position_monitor", "risk_limits", 
        "real_time_monitor", "analytics_engine", "compliance_engine",
        "data_config", "alert_config"
    ]
    
    for section in required_sections:
        if section not in config:
            issues[section] = [f"Missing required configuration section: {section}"]
    
    # Validate specific values
    if "risk_manager" in config:
        risk_config = config["risk_manager"]
        
        if "assessment_interval" in risk_config:
            if risk_config["assessment_interval"] <= 0:
                issues.setdefault("risk_manager", []).append("assessment_interval must be positive")
        
        if "var_threshold" in risk_config:
            if risk_config["var_threshold"] <= 0:
                issues.setdefault("risk_manager", []).append("var_threshold must be positive")
    
    if "data_config" in config:
        data_config = config["data_config"]
        
        if "data_retention_days" in data_config:
            if data_config["data_retention_days"] <= 0:
                issues.setdefault("data_config", []).append("data_retention_days must be positive")
    
    return issues

# Configuration presets for different use cases

HIGH_FREQUENCY_CONFIG = {
    **get_default_config(),
    "risk_manager": {
        **get_default_config()["risk_manager"],
        "assessment_interval": 10,  # 10 seconds for HFT
        "emergency_shutdown_enabled": True
    },
    "position_monitor": {
        **get_default_config()["position_monitor"],
        "update_interval": 0.5,  # 0.5 seconds for HFT
        "limit_check_interval": 1.0
    },
    "real_time_monitor": {
        **get_default_config()["real_time_monitor"],
        "update_interval": 0.5  # High frequency monitoring
    }
}

INSTITUTIONAL_CONFIG = {
    **get_default_config(),
    "compliance_engine": {
        **get_default_config()["compliance_engine"],
        "basel3_compliance": True,
        "strict_limits": True
    },
    "analytics_engine": {
        **get_default_config()["analytics_engine"],
        "monte_carlo_simulations": 100000,  # High precision
        "comprehensive_backtesting": True
    },
    "integration_framework": {
        **get_default_config()["integration_framework"],
        "blockchain_enabled": True,
        "dao_governance_enabled": True
    }
}

STARTUP_CONFIG = {
    **get_default_config(),
    "risk_manager": {
        **get_default_config()["risk_manager"],
        "assessment_interval": 300,  # 5 minutes for startups
        "var_threshold": 100000  # Lower threshold
    },
    "position_monitor": {
        **get_default_config()["position_monitor"],
        "max_positions": 100,  # Lower limit
        "position_loss_limit": 0.05  # Tighter 5% loss limit
    },
    "analytics_engine": {
        **get_default_config()["analytics_engine"],
        "monte_carlo_simulations": 5000,  # Lower precision for speed
        "comprehensive_backtesting": False
    }
}