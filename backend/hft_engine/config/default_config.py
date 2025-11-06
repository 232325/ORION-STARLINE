"""
Default Configuration for HFT Engine
===================================

Default configuration parameters for all HFT components
"""

import os
from typing import Dict, Any

def get_default_config() -> Dict[str, Any]:
    """Get default HFT configuration"""
    
    return {
        # Core Engine Configuration
        'engine': {
            'max_symbols': 20,
            'max_strategies': 10,
            'trading_loop_interval': 0.001,  # 1ms
            'max_concurrent_orders': 1000,
            'enable_performance_monitoring': True,
            'log_level': 'INFO'
        },
        
        # Market Data Configuration
        'market_data': {
            'update_frequency': 1000,  # Hz
            'compress_data': True,
            'batch_size': 100,
            'tick_buffer_size': 10000,
            'bar_generation_interval': 60,  # seconds
            'data_sources': {
                'NASDAQ': 'real_time',
                'NYSE': 'real_time', 
                'FOREX': 'real_time',
                'CRYPTO': 'real_time'
            }
        },
        
        # Order Management Configuration
        'order_manager': {
            'max_order_size': 100000,
            'order_timeout': 30,  # seconds
            'retry_attempts': 3,
            'enable_partial_fills': True,
            'commission_model': 'per_share',
            'max_commission_rate': 0.001,  # 0.1%
            'exchange_routing': 'optimal',
            'pre_trade_checks': True
        },
        
        # Market Making Strategy
        'market_making': {
            'spread_multiplier': 1.2,
            'inventory_target': 0.0,
            'max_inventory': 1000,
            'skew_factor': 0.5,
            'rebalance_threshold': 0.1,
            'enable_inventory_management': True,
            'min_spread_bps': 2.0,
            'max_spread_bps': 50.0
        },
        
        # Arbitrage Strategy
        'arbitrage': {
            'min_spread_bps': 5.0,
            'max_execution_time_us': 500,
            'max_position_size': 1000,
            'correlation_threshold': 0.8,
            'max_opportunities': 20,
            'execution_window': 1.0,  # seconds
            'enable_triangular_arb': True,
            'enable_stat_arb': True
        },
        
        # Statistical Arbitrage Strategy
        'stat_arb': {
            'lookback_period': 100,
            'entry_threshold': 2.0,  # Z-score
            'exit_threshold': 0.5,   # Z-score
            'max_hold_time': 3600,   # seconds
            'min_correlation': 0.7,
            'position_size': 100,
            'rebalance_frequency': 300  # seconds
        },
        
        # Risk Management Configuration
        'risk': {
            'max_position_size': 100000,
            'max_exposure_per_symbol': 10000,
            'max_portfolio_var': 5000,
            'max_leverage': 3.0,
            'max_concentration': 0.2,  # 20%
            'position_limits': {
                'AAPL': 1000,
                'GOOGL': 500,
                'MSFT': 800,
                'TSLA': 300,
                'NVDA': 400
            },
            'market_risk': {
                'volatility_threshold': 0.05,
                'spread_threshold': 0.02
            },
            'operational_risk': {
                'cpu_threshold': 80.0,
                'memory_threshold': 85.0,
                'network_latency_threshold': 1000
            }
        },
        
        # Infrastructure Configuration
        'infrastructure': {
            'co_location': {
                'enabled': True,
                'data_centers': {
                    'NASDAQ': {
                        'location': 'Carteret, NJ',
                        'latency_us': 15
                    },
                    'NYSE': {
                        'location': 'Mahwah, NJ',
                        'latency_us': 18
                    },
                    'FOREX': {
                        'location': 'London, UK',
                        'latency_us': 35
                    },
                    'CRYPTO': {
                        'location': 'Chicago, IL',
                        'latency_us': 25
                    }
                }
            },
            
            'network_optimization': {
                'kernel_bypass': True,
                'direct_memory_access': True,
                'thread_priorities': True,
                'cpu_affinity': True,
                'lock_free_queues': True,
                'cache_line_alignment': True
            },
            
            'redundancy': {
                'failover_enabled': True,
                'backup_systems': ['backup_engine_1', 'backup_engine_2'],
                'health_check_interval': 5,
                'failover_threshold': 3,
                'data_replication': True
            },
            
            'monitoring': {
                'enabled': True,
                'monitoring_interval': 1,
                'alert_thresholds': {
                    'cpu_usage': 80.0,
                    'memory_usage': 85.0,
                    'latency_us': 100.0,
                    'error_rate': 0.05,
                    'throughput': 1000
                },
                'dashboard_refresh': 1,
                'log_metrics': True
            }
        },
        
        # Performance Configuration
        'performance': {
            'latency_targets': {
                'market_data_us': 50,
                'order_execution_us': 100,
                'signal_generation_us': 200,
                'risk_check_us': 10
            },
            'throughput_targets': {
                'orders_per_second': 10000,
                'signals_per_second': 1000,
                'market_data_ticks_per_second': 50000
            },
            'optimization': {
                'use_fpga': False,  # Would be True in production
                'kernel_bypass': True,
                'memory_pools': True,
                'lock_free_structures': True
            }
        },
        
        # Asset Configuration
        'assets': {
            'stocks': {
                'AAPL': {'exchange': 'NASDAQ', 'tick_size': 0.01, 'lot_size': 1},
                'GOOGL': {'exchange': 'NYSE', 'tick_size': 0.01, 'lot_size': 1},
                'MSFT': {'exchange': 'NASDAQ', 'tick_size': 0.01, 'lot_size': 1},
                'TSLA': {'exchange': 'NASDAQ', 'tick_size': 0.01, 'lot_size': 1},
                'NVDA': {'exchange': 'NASDAQ', 'tick_size': 0.01, 'lot_size': 1}
            },
            'forex': {
                'EUR/USD': {'exchange': 'FOREX', 'tick_size': 0.00001, 'lot_size': 1000},
                'GBP/USD': {'exchange': 'FOREX', 'tick_size': 0.00001, 'lot_size': 1000},
                'USD/JPY': {'exchange': 'FOREX', 'tick_size': 0.001, 'lot_size': 1000},
                'USD/CHF': {'exchange': 'FOREX', 'tick_size': 0.00001, 'lot_size': 1000}
            },
            'metals': {
                'XAU/USD': {'exchange': 'METALS', 'tick_size': 0.01, 'lot_size': 1},
                'XAG/USD': {'exchange': 'METALS', 'tick_size': 0.001, 'lot_size': 1},
                'XPT/USD': {'exchange': 'METALS', 'tick_size': 0.01, 'lot_size': 1},
                'XPD/USD': {'exchange': 'METALS', 'tick_size': 0.01, 'lot_size': 1}
            },
            'crypto': {
                'BTC/USD': {'exchange': 'CRYPTO', 'tick_size': 0.01, 'lot_size': 0.001},
                'ETH/USD': {'exchange': 'CRYPTO', 'tick_size': 0.01, 'lot_size': 0.01}
            }
        },
        
        # Logging Configuration
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': '/tmp/hft_engine.log',
            'max_size_mb': 100,
            'backup_count': 5,
            'enable_structured_logging': True,
            'log_latency_measurements': True,
            'log_order_events': True,
            'log_risk_events': True
        },
        
        # Database Configuration
        'database': {
            'enabled': True,
            'type': 'sqlite',  # or 'postgresql', 'mysql'
            'connection_string': '/tmp/hft_engine.db',
            'connection_pool_size': 10,
            'query_timeout': 5,
            'backup_enabled': True,
            'backup_interval': 3600  # seconds
        },
        
        # API Configuration
        'api': {
            'enabled': False,  # Would be True for production
            'host': 'localhost',
            'port': 8080,
            'rate_limit': 1000,  # requests per minute
            'authentication': 'api_key',
            'cors_enabled': False,
            'ssl_enabled': True
        }
    }

# Environment-specific configurations
def get_development_config() -> Dict[str, Any]:
    """Development environment configuration"""
    config = get_default_config()
    
    # Development-specific overrides
    config['engine']['log_level'] = 'DEBUG'
    config['infrastructure']['co_location']['enabled'] = False
    config['performance']['optimization']['kernel_bypass'] = False
    config['api']['enabled'] = True
    
    return config

def get_production_config() -> Dict[str, Any]:
    """Production environment configuration"""
    config = get_default_config()
    
    # Production-specific settings
    config['engine']['log_level'] = 'INFO'
    config['infrastructure']['co_location']['enabled'] = True
    config['performance']['optimization']['kernel_bypass'] = True
    config['infrastructure']['redundancy']['failover_enabled'] = True
    config['infrastructure']['monitoring']['enabled'] = True
    
    return config

def get_test_config() -> Dict[str, Any]:
    """Test environment configuration"""
    config = get_default_config()
    
    # Test-specific overrides
    config['engine']['max_symbols'] = 5
    config['performance']['latency_targets']['market_data_us'] = 1000  # More relaxed
    config['market_data']['update_frequency'] = 100  # Lower frequency for tests
    
    return config

# Configuration loader
def load_config(env: str = 'development') -> Dict[str, Any]:
    """Load configuration based on environment"""
    
    # Check for environment variable override
    env_from_var = os.getenv('HFT_ENV', 'development').lower()
    env = env_from_var if env_from_var in ['development', 'production', 'test'] else env
    
    if env == 'production':
        return get_production_config()
    elif env == 'test':
        return get_test_config()
    else:  # development
        return get_development_config()

# Validate configuration
def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration parameters"""
    
    required_sections = [
        'engine', 'market_data', 'order_manager', 'market_making',
        'arbitrage', 'risk', 'infrastructure', 'performance'
    ]
    
    for section in required_sections:
        if section not in config:
            print(f"Missing required configuration section: {section}")
            return False
    
    # Validate performance targets
    latency_targets = config['performance']['latency_targets']
    for target_name, target_value in latency_targets.items():
        if not isinstance(target_value, (int, float)) or target_value <= 0:
            print(f"Invalid latency target for {target_name}: {target_value}")
            return False
    
    return True