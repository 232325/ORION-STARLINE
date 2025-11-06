"""
AI Trading System - Configuration Settings
Tizim konfiguratsiya fayli
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Trading System API"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://aitrading.com",
        "https://*.aitrading.com"
    ]
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./ai_trading.db",
        env="DATABASE_URL"
    )
    
    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # JWT Configuration
    SECRET_KEY: str = Field(
        default="your-super-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # API Key Authentication
    API_KEY_HEADER: str = "X-API-Key"
    
    # OAuth Configuration
    OAUTH2_SCHEME_NAME: str = "OAuth2"
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_PATH: str = "/workspace/code/api/uploads"
    ALLOWED_FILE_EXTENSIONS: List[str] = [
        ".csv", ".json", ".xlsx", ".txt", ".pdf", 
        ".png", ".jpg", ".jpeg", ".gif"
    ]
    
    # Pagination Settings
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Cache Settings
    CACHE_TTL: int = 3600  # 1 hour
    CACHE_MAX_SIZE: int = 10000
    
    # WebSocket Settings
    WEBSOCKET_PING_INTERVAL: int = 20
    WEBSOCKET_PING_TIMEOUT: int = 10
    MAX_WEBSOCKET_CONNECTIONS: int = 1000
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Background Tasks
    MAX_BACKGROUND_TASKS: int = 50
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Performance Settings
    WORKERS: int = 4
    WORKER_CONNECTIONS: int = 1000
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    COINBASE_API_KEY: Optional[str] = Field(default=None, env="COINBASE_API_KEY")
    COINBASE_API_SECRET: Optional[str] = Field(default=None, env="COINBASE_API_SECRET")
    BINANCE_API_KEY: Optional[str] = Field(default=None, env="BINANCE_API_KEY")
    BINANCE_API_SECRET: Optional[str] = Field(default=None, env="BINANCE_API_SECRET")
    
    # Quantum Computing Settings
    QUBITS_SIMULATOR_API: Optional[str] = Field(default=None, env="QUBITS_SIMULATOR_API")
    IBM_QUANTUM_API_KEY: Optional[str] = Field(default=None, env="IBM_QUANTUM_API_KEY")
    
    # Blockchain Settings
    WEB3_PROVIDER_URL: Optional[str] = Field(default=None, env="WEB3_PROVIDER_URL")
    ETHEREUM_RPC_URL: Optional[str] = Field(default=None, env="ETHEREUM_RPC_URL")
    POLYGON_RPC_URL: Optional[str] = Field(default=None, env="POLYGON_RPC_URL")
    
    # NFT Marketplace
    OPENSEA_API_KEY: Optional[str] = Field(default=None, env="OPENSEA_API_KEY")
    RARIBLE_API_KEY: Optional[str] = Field(default=None, env="RARIBLE_API_KEY")
    
    # Security Settings
    SSL_CERT_PATH: Optional[str] = Field(default=None, env="SSL_CERT_PATH")
    SSL_KEY_PATH: Optional[str] = Field(default=None, env="SSL_KEY_PATH")
    
    # Email Settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@aitrading.com"
    
    # OAuth Settings
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None, env="GOOGLE_CLIENT_SECRET")
    GITHUB_CLIENT_ID: Optional[str] = Field(default=None, env="GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: Optional[str] = Field(default=None, env="GITHUB_CLIENT_SECRET")
    LINKEDIN_CLIENT_ID: Optional[str] = Field(default=None, env="LINKEDIN_CLIENT_ID")
    LINKEDIN_CLIENT_SECRET: Optional[str] = Field(default=None, env="LINKEDIN_CLIENT_SECRET")
    BASE_URL: str = Field(default="http://localhost:8000", env="BASE_URL")
    
    # Notification Settings
    ENABLE_EMAIL_NOTIFICATIONS: bool = True
    ENABLE_SLACK_WEBHOOK: bool = False
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    
    # Monitoring
    ENABLE_METRICS: bool = True
    PROMETHEUS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings

def validate_settings() -> bool:
    """Validate critical settings"""
    required_env_vars = [
        "SECRET_KEY",
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Yo'qolgan muhit o'zgaruvchilari: {', '.join(missing_vars)}")
        return False
    
    # Create required directories
    Path(settings.UPLOAD_PATH).mkdir(parents=True, exist_ok=True)
    
    return True