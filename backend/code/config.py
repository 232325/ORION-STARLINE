"""
Trading Signal Generator Configuration
"""

# Trading parameters
DEFAULT_ACCOUNT_BALANCE = 10000.0
DEFAULT_RISK_PERCENT = 0.02  # 2% risk per trade
MAX_POSITION_SIZE = 0.1  # Maximum 10% of account per trade

# Signal generation parameters
MIN_DATA_POINTS = 50  # Minimum data points required for analysis
CONFIDENCE_THRESHOLD = {
    'STRONG_BUY': 0.8,
    'BUY': 0.65,
    'HOLD': 0.35,
    'SELL': 0.2,
    'STRONG_SELL': 0.0
}

# Timeframe configurations
TIMEFRAMES = {
    '1m': '1 minute',
    '5m': '5 minutes',
    '15m': '15 minutes',
    '30m': '30 minutes',
    '1h': '1 hour',
    '4h': '4 hours',
    '1d': '1 day',
    '1w': '1 week'
}

# Real-time generation settings
DEFAULT_GENERATION_INTERVAL = 60  # seconds
MAX_SYMBOLS_PER_BATCH = 20

# Technical indicator parameters
INDICATOR_PARAMS = {
    'sma_periods': [10, 20, 50],
    'ema_periods': [12, 26],
    'rsi_period': 14,
    'macd_params': {'fast': 12, 'slow': 26, 'signal': 9},
    'bollinger_params': {'period': 20, 'std': 2},
    'stochastic_params': {'k_period': 14, 'd_period': 3},
    'atr_period': 14
}

# Risk management parameters
RISK_MULTIPLIERS = {
    'stop_loss': 2.0,  # ATR multiplier for stop loss
    'take_profit': 1.5  # ATR multiplier for take profit (relative to stop loss)
}

# Model integration settings
MODEL_WEIGHTS = {
    'dqn': 0.3,
    'ppo': 0.3,
    'a2c': 0.2,
    'technical': 0.2  # Traditional technical analysis
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'file': 'trading_signals.log'
}

# Data source settings
DATA_PROVIDER_CONFIG = {
    'yahoo_finance': {
        'timeout': 30,
        'retry_attempts': 3,
        'retry_delay': 1  # seconds
    }
}

# Signal filtering parameters
SIGNAL_FILTERS = {
    'min_confidence': 0.3,
    'max_daily_signals': 5,
    'min_time_between_signals': 300  # 5 minutes in seconds
}

# Export settings
EXPORT_CONFIG = {
    'default_format': 'json',
    'include_indicators': True,
    'include_reasoning': True
}

# GPT-5 Sentiment Analysis Configuration
SENTIMENT_CONFIG = {
    # API settings
    'openai_api_key': 'YOUR_OPENAI_API_KEY',
    'gpt5_model': 'gpt-5',
    'rate_limit': 60,  # requests per minute
    'max_tokens': 500,
    'temperature': 0.3,
    
    # Cache settings
    'enable_cache': True,
    'max_cache_size': 1000,
    'cache_ttl': 3600,  # 1 hour in seconds
    
    # Processing settings
    'batch_size': 10,
    'max_workers': 10,
    'timeout': 30,  # seconds
    
    # Asset symbols
    'stocks': ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA'],
    'forex_pairs': ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF'],
    'metals': ['XAU/USD', 'XAG/USD', 'XPT/USD', 'XPD/USD'],
    
    # Sentiment weights
    'source_weights': {
        'news': 0.4,
        'twitter': 0.2,
        'reddit': 0.1,
        'earnings': 0.2,
        'analyst_report': 0.1
    },
    
    # Database settings
    'db_path': 'sentiment_data.db',
    'retention_days': 30,
    
    # WebSocket settings
    'ws_ping_interval': 30,
    'ws_ping_timeout': 10,
    
    # Cost tracking
    'track_costs': True,
    'cost_alert_threshold': 100.0  # USD
}