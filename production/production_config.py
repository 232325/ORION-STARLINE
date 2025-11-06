"""
Production Environment Configuration
Production muhit uchun konfiguratsiya fayli
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import timedelta


@dataclass
class ProductionConfig:
    """Production environment konfiguratsiyasi"""
    
    # === SUPABASE CONFIG ===
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_DB_HOST: str = os.getenv("SUPABASE_DB_HOST", "db.supabase.co")
    SUPABASE_DB_PORT: int = int(os.getenv("SUPABASE_DB_PORT", "5432"))
    SUPABASE_DB_NAME: str = os.getenv("SUPABASE_DB_NAME", "")
    SUPABASE_DB_USER: str = os.getenv("SUPABASE_DB_USER", "")
    SUPABASE_DB_PASSWORD: str = os.getenv("SUPABASE_DB_PASSWORD", "")
    
    # === SSL/TLS CONFIG ===
    SSL_CERT_PATH: str = "/etc/ssl/certs/orion-starline.crt"
    SSL_KEY_PATH: str = "/etc/ssl/private/orion-starline.key"
    SSL_CA_PATH: str = "/etc/ssl/certs/ca-certificates.crt"
    ENABLE_HTTPS: bool = True
    
    # === PAYMENT INTEGRATIONS ===
    # Stripe Configuration
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_API_VERSION: str = "2023-10-16"
    
    # PayPal Configuration
    PAYPAL_CLIENT_ID: str = os.getenv("PAYPAL_CLIENT_ID", "")
    PAYPAL_CLIENT_SECRET: str = os.getenv("PAYPAL_CLIENT_SECRET", "")
    PAYPAL_BASE_URL: str = os.getenv("PAYPAL_BASE_URL", "https://api-m.paypal.com")
    
    # === CDN CONFIGURATION ===
    CDN_URL: str = os.getenv("CDN_URL", "https://cdn.orion-starline.com")
    CLOUD_FLARE_ZONE_ID: str = os.getenv("CLOUD_FLARE_ZONE_ID", "")
    CLOUD_FLARE_API_KEY: str = os.getenv("CLOUD_FLARE_API_KEY", "")
    
    # === PRODUCTION METRICS ===
    PRODUCTION_ENV: bool = True
    DEBUG_MODE: bool = False
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # === KUBERNETES CONFIG ===
    KUBE_NAMESPACE: str = "orion-starline-prod"
    KUBE_CONFIG_PATH: str = os.getenv("KUBE_CONFIG_PATH", "~/.kube/config")
    DOCKER_REGISTRY: str = "ghcr.io/orion-starline"
    
    # === MONITORING CONFIG ===
    PROMETHEUS_URL: str = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
    GRAFANA_URL: str = os.getenv("GRAFANA_URL", "http://grafana:3000")
    ALERTMANAGER_URL: str = os.getenv("ALERTMANAGER_URL", "http://alertmanager:9093")
    
    # === RATE LIMITING ===
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # === SECURITY HEADERS ===
    SECURITY_HEADERS: Dict[str, str] = field(default_factory=lambda: {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self' https://*.stripe.com https://*.paypal.com",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    })
    
    # === BACKUP CONFIG ===
    BACKUP_SCHEDULE: str = "0 2 * * *"  # Har kuni 02:00
    BACKUP_RETENTION_DAYS: int = 30
    BACKUP_S3_BUCKET: str = os.getenv("BACKUP_S3_BUCKET", "orion-starline-backups")
    BACKUP_S3_REGION: str = os.getenv("BACKUP_S3_REGION", "us-east-1")
    
    # === DATABASE CONFIG ===
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "30"))
    DATABASE_TIMEOUT: int = 30
    DATABASE_SSL_MODE: str = "require"
    
    # === CACHE CONFIG ===
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))
    CACHE_PREFIX: str = "orion_prod_"
    
    # === SESSION CONFIG ===
    SESSION_TIMEOUT: int = int(os.getenv("SESSION_TIMEOUT", "86400"))  # 24 soat
    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", "")
    
    # === EMAIL CONFIG ===
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS: bool = True
    
    # === WEBHOOKS ===
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")
    WEBHOOK_TIMEOUT: int = 30
    
    # === REAL-TIME UPDATES ===
    WEBSOCKET_PING_INTERVAL: int = 30
    WEBSOCKET_PING_TIMEOUT: int = 10
    MAX_WEBSOCKET_CONNECTIONS: int = 1000
    
    # === LOAD BALANCING ===
    HEALTH_CHECK_PATH: str = "/health"
    HEALTH_CHECK_INTERVAL: int = 30
    MAX_RESPONSE_TIME: int = 5000  # millisekund
    ERROR_THRESHOLD: int = 5  # percent
    
    # === USER MANAGEMENT ===
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION: int = 900  # 15 daqiqa
    PASSWORD_MIN_LENGTH: int = 8
    REQUIRE_EMAIL_VERIFICATION: bool = True
    
    # === API RATE LIMITING ===
    API_RATE_LIMITS: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "trading_api": {"requests": 100, "window": 3600},
        "analytics_api": {"requests": 50, "window": 3600},
        "user_api": {"requests": 200, "window": 3600},
        "webhook_api": {"requests": 1000, "window": 3600}
    })
    
    # === DEPLOYMENT METRICS ===
    DEPLOYMENT_TIMEOUT: int = 600  # 10 daqiqa
    ROLLBACK_TIMEOUT: int = 300  # 5 daqiqa
    HEALTH_CHECK_TIMEOUT: int = 30
    READINESS_TIMEOUT: int = 60
    
    def validate_config(self) -> bool:
        """Konfiguratsiyani tekshirish"""
        required_fields = [
            self.SUPABASE_URL,
            self.SUPABASE_ANON_KEY,
            self.SUPABASE_SERVICE_ROLE_KEY,
            self.STRIPE_SECRET_KEY,
            self.PAYPAL_CLIENT_ID,
            self.PAYPAL_CLIENT_SECRET
        ]
        
        missing_fields = [field for field in required_fields if not field]
        
        if missing_fields:
            print(f"❌ Yo'qolgan konfiguratsiya maydonlari: {missing_fields}")
            return False
        
        print("✅ Barcha konfiguratsiya maydonlari mavjud")
        return True
    
    def get_database_url(self) -> str:
        """Ma'lumotlar bazasi URLini olish"""
        return f"postgresql://{self.SUPABASE_DB_USER}:{self.SUPABASE_DB_PASSWORD}@{self.SUPABASE_DB_HOST}:{self.SUPABASE_DB_PORT}/{self.SUPABASE_DB_NAME}?sslmode={self.DATABASE_SSL_MODE}"
    
    def get_redis_url(self) -> str:
        """Redis URLini olish"""
        return self.REDIS_URL
    
    def get_cors_origins(self) -> list:
        """CORS manbalarini olish"""
        return [
            "https://orion-starline.com",
            "https://www.orion-starline.com",
            "https://app.orion-starline.com",
            "https://admin.orion-starline.com"
        ]
    
    def get_sentry_dsn(self) -> Optional[str]:
        """Sentry DSN ni olish"""
        return os.getenv("SENTRY_DSN")
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Xususiyatlarni boshqarish bayroqlari"""
        return {
            "enable_premium_features": True,
            "enable_trading_bot": True,
            "enable_ai_analysis": True,
            "enable_personalization": True,
            "enable_notifications": True,
            "enable_real_trading": False,  # Development uchun o'chirilgan
            "enable_backtesting": True,
            "enable_social_features": False,
            "enable_mobile_app": True
        }


# Global production configuration instance
config = ProductionConfig()

# Environment-specific configurations
CONFIGS = {
    "development": {
        "DEBUG_MODE": True,
        "LOG_LEVEL": "DEBUG",
        "ENABLE_HTTPS": False
    },
    "staging": {
        "DEBUG_MODE": True,
        "LOG_LEVEL": "INFO",
        "ENABLE_HTTPS": True
    },
    "production": {
        "DEBUG_MODE": False,
        "LOG_LEVEL": "WARNING",
        "ENABLE_HTTPS": True
    }
}


def get_config(environment: str = "production") -> ProductionConfig:
    """Environment ga mos konfiguratsiyani olish"""
    global config
    
    if environment in CONFIGS:
        env_config = CONFIGS[environment]
        for key, value in env_config.items():
            if hasattr(config, key):
                setattr(config, key, value)
    
    return config


def validate_environment() -> bool:
    """Environment validatsiyasi"""
    env = os.getenv("ENVIRONMENT", "production")
    config = get_config(env)
    
    print(f"🌍 Environment: {env}")
    print(f"🔧 Production Mode: {config.PRODUCTION_ENV}")
    print(f"🔒 Security Mode: {config.ENABLE_HTTPS}")
    
    return config.validate_config()


if __name__ == "__main__":
    # Test configuration
    if validate_environment():
        print("✅ Production configuration tayyor!")
    else:
        print("❌ Production configuration xatosi!")
        exit(1)