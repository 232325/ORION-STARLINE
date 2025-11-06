"""
Security Konfiguratsiya Moduli
==============================

Bu modul security tizimining barcha konfiguratsiya ma'lumotlarini boshqaradi:
- Rate limiting sozlamalari
- Security headers
- API security sozlamalari
- Data protection qoidalari
- Monitoring konfiguratsiyasi

@author: Security Team
@version: 1.0.0
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import timedelta


@dataclass
class RateLimitingConfig:
    """Rate limiting konfiguratsiyasi"""
    enabled: bool = True
    default_requests_per_minute: int = 60
    default_requests_per_hour: int = 3600
    default_requests_per_day: int = 86400
    default_burst_limit: int = 10
    window_size: int = 60
    
    # Endpoint-specific limits
    endpoint_configs: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        '/api/v1/auth/login': {
            'requests_per_minute': 5,
            'requests_per_hour': 100,
            'burst_limit': 3,
            'exempt_users': []  # Admin users can be added here
        },
        '/api/v1/auth/register': {
            'requests_per_minute': 3,
            'requests_per_hour': 50,
            'burst_limit': 2
        },
        '/api/v1/auth/forgot-password': {
            'requests_per_minute': 2,
            'requests_per_hour': 30,
            'burst_limit': 1
        },
        '/api/v1/admin/*': {
            'requests_per_minute': 1000,
            'requests_per_hour': 50000,
            'burst_limit': 50,
            'exempt_users': ['admin']
        },
        '/api/v1/search': {
            'requests_per_minute': 100,
            'requests_per_hour': 5000,
            'burst_limit': 20
        },
        '/api/v1/upload': {
            'requests_per_minute': 10,
            'requests_per_hour': 500,
            'burst_limit': 5
        }
    })
    
    # User-specific limits
    user_role_limits: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'admin': {
            'requests_per_minute': 2000,
            'requests_per_hour': 100000,
            'requests_per_day': 1000000,
            'burst_limit': 100
        },
        'premium': {
            'requests_per_minute': 200,
            'requests_per_hour': 10000,
            'requests_per_day': 100000,
            'burst_limit': 20
        },
        'standard': {
            'requests_per_minute': 100,
            'requests_per_hour': 5000,
            'requests_per_day': 50000,
            'burst_limit': 10
        },
        'guest': {
            'requests_per_minute': 20,
            'requests_per_hour': 1000,
            'requests_per_day': 10000,
            'burst_limit': 5
        }
    })
    
    # IP-based limits
    ip_limits: Dict[str, int] = field(default_factory=lambda: {
        'private_networks': 1000,  # Higher limit for private networks
        'geographic_restrictions': 50,  # Lower limit for certain geographies
        'tor_exit_nodes': 1  # Very restrictive for potential Tor usage
    })


@dataclass
class SecurityHeadersConfig:
    """Security headers konfiguratsiyasi"""
    # Content Security Policy
    content_security_policy: str = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:; frame-src 'none'; object-src 'none'; media-src 'self'; worker-src 'none';"
    
    # Frame protection
    x_frame_options: str = "DENY"
    
    # MIME type sniffing protection
    x_content_type_options: str = "nosniff"
    
    # XSS protection
    x_xss_protection: str = "1; mode=block"
    
    # HSTS (HTTP Strict Transport Security)
    strict_transport_security: str = "max-age=31536000; includeSubDomains; preload"
    
    # Referrer policy
    referrer_policy: str = "strict-origin-when-cross-origin"
    
    # Permissions policy
    permissions_policy: str = "geolocation=(), microphone=(), camera=(), payment=(), usb=(), xr-spatial-tracking=()"
    
    # Additional headers
    additional_headers: Dict[str, str] = field(default_factory=lambda: {
        'X-Powered-By': '',  # Remove server information
        'Server': '',  # Remove server information
        'X-AspNet-Version': '',  # Remove framework version
        'X-AspNetMvc-Version': ''  # Remove framework version
    })


@dataclass
class InputValidationConfig:
    """Input validation konfiguratsiyasi"""
    enabled: bool = True
    strict_mode: bool = False
    
    # Field length limits
    max_field_length: int = 10000
    min_field_length: int = 0
    
    # Specific field limits
    field_limits: Dict[str, Dict[str, int]] = field(default_factory=lambda: {
        'username': {'min': 3, 'max': 50},
        'password': {'min': 8, 'max': 128},
        'email': {'max': 254},
        'phone': {'min': 10, 'max': 15},
        'name': {'max': 100},
        'description': {'max': 5000},
        'file_name': {'max': 255},
        'comment': {'max': 2000}
    })
    
    # Allowed characters per field
    allowed_characters: Dict[str, str] = field(default_factory=lambda: {
        'username': 'a-zA-Z0-9_-',
        'name': 'a-zA-Z\s\-\'\.',
        'email': 'a-zA-Z0-9._%+-@',
        'phone': '0-9+()\-\s\.',
        'text': 'a-zA-Z0-9\s\-\'\".,;:!?()[]{}@#$%^&*+=|\\/<>`~'
    })
    
    # Blocked patterns
    blocked_patterns: List[str] = field(default_factory=lambda: [
        r'(?i)(<script[^>]*>.*?</script>)',
        r'(?i)(javascript:|vbscript:|data:text/html)',
        r'(?i)(union\s+select|select\s+.*\s+from)',
        r'(?i)(drop\s+table|delete\s+from|insert\s+into)',
        r'(?i)(\.\./|\.\.\\)',
        r'(?i)(;|\|\||&&)',
        r'(?i)(exec|execute|eval)',
        r'(?i)(curl|wget|nc|telnet)',
    ])


@dataclass
class APIKeyConfig:
    """API key konfiguratsiyasi"""
    enabled: bool = True
    
    # Key settings
    key_expiration_days: int = 90
    max_keys_per_user: int = 5
    key_length: int = 32
    
    # Security settings
    require_https: bool = True
    require_signatures: bool = True
    max_key_age_days: int = 365
    
    # Rate limiting
    default_rate_limit: int = 1000
    rate_limit_tiers: Dict[str, int] = field(default_factory=lambda: {
        'bronze': 500,
        'silver': 2000,
        'gold': 10000,
        'platinum': 50000
    })
    
    # Permissions
    default_permissions: List[str] = field(default_factory=list)
    permission_levels: Dict[str, List[str]] = field(default_factory=lambda: {
        'read': ['GET'],
        'write': ['GET', 'POST', 'PUT'],
        'admin': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
        'full': ['*']
    })


@dataclass
class DataProtectionConfig:
    """Data protection konfiguratsiyasi"""
    # Encryption settings
    encryption_enabled: bool = True
    encryption_algorithm: str = 'AES-256'
    key_rotation_days: int = 90
    
    # PII protection
    pii_detection_enabled: bool = True
    auto_anonymization: bool = True
    pii_fields: List[str] = field(default_factory=lambda: [
        'email', 'phone', 'ssn', 'credit_card', 'passport',
        'first_name', 'last_name', 'date_of_birth', 'address'
    ])
    
    # Data retention
    retention_policies: Dict[str, int] = field(default_factory=lambda: {
        'user_data': 2555,  # 7 years
        'audit_logs': 2190,  # 6 years
        'security_logs': 1095,  # 3 years
        'session_data': 30,  # 30 days
        'temp_files': 7  # 7 days
    })
    
    # Compliance settings
    gdpr_compliance: bool = True
    ccpa_compliance: bool = True
    hipaa_compliance: bool = False  # Only if handling health data
    
    # Anonymization methods
    anonymization_methods: Dict[str, str] = field(default_factory=lambda: {
        'email': 'masking',
        'phone': 'masking',
        'ssn': 'masking',
        'name': 'pseudonymization',
        'address': 'generalization'
    })


@dataclass
class MonitoringConfig:
    """Security monitoring konfiguratsiyasi"""
    # Monitoring settings
    enabled: bool = True
    real_time_monitoring: bool = True
    
    # Event collection
    collect_all_events: bool = True
    event_retention_days: int = 90
    
    # Anomaly detection
    anomaly_detection_enabled: bool = True
    baseline_period_hours: int = 24
    anomaly_threshold: float = 2.0  # Standard deviations
    
    # Alert settings
    alerts_enabled: bool = True
    alert_channels: List[str] = field(default_factory=lambda: ['email', 'slack'])
    escalation_enabled: bool = True
    
    # Incident response
    auto_create_incidents: bool = True
    incident_assignment_rules: Dict[str, str] = field(default_factory=lambda: {
        'critical': 'security_team',
        'high': 'security_team',
        'medium': 'operations_team',
        'low': 'monitoring_team'
    })
    
    # Dashboard settings
    dashboard_refresh_interval: int = 30  # seconds
    metrics_history_retention: int = 1440  # 24 hours at 1-minute intervals


@dataclass
class SecurityConfig:
    """Asosiy Security konfiguratsiyasi"""
    # Component configurations
    rate_limiting: RateLimitingConfig = field(default_factory=RateLimitingConfig)
    security_headers: SecurityHeadersConfig = field(default_factory=SecurityHeadersConfig)
    input_validation: InputValidationConfig = field(default_factory=InputValidationConfig)
    api_keys: APIKeyConfig = field(default_factory=APIKeyConfig)
    data_protection: DataProtectionConfig = field(default_factory=DataProtectionConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Environment settings
    environment: str = 'development'  # development, staging, production
    
    # Logging settings
    log_level: str = 'INFO'
    log_to_file: bool = True
    log_to_console: bool = True
    log_file_path: str = 'logs/security.log'
    
    # Database settings (for persistent storage)
    database_url: str = ''
    
    # Redis settings (for caching and rate limiting)
    redis_url: str = ''
    
    # Notification settings
    email_config: Dict[str, str] = field(default_factory=lambda: {
        'smtp_server': '',
        'smtp_port': '587',
        'username': '',
        'password': '',
        'from_address': 'security@company.com',
        'to_addresses': 'admin@company.com,security@company.com'
    })
    
    slack_config: Dict[str, str] = field(default_factory=lambda: {
        'webhook_url': '',
        'channel': '#security-alerts',
        'bot_name': 'SecurityBot'
    })
    
    # Feature flags
    features: Dict[str, bool] = field(default_factory=lambda: {
        'rate_limiting': True,
        'input_validation': True,
        'api_key_auth': True,
        'jwt_auth': True,
        'security_headers': True,
        'data_encryption': True,
        'pii_protection': True,
        'anomaly_detection': True,
        'incident_response': True,
        'audit_logging': True
    })


# Global configuration instance
_config = None


def get_security_config() -> SecurityConfig:
    """Global security konfiguratsiyasini olish"""
    global _config
    if _config is None:
        _config = _load_config()
    return _config


def set_security_config(config: SecurityConfig):
    """Security konfiguratsiyasini o'rnatish"""
    global _config
    _config = config


def _load_config() -> SecurityConfig:
    """Konfiguratsiyani yuklash (environment variables dan)"""
    config = SecurityConfig()
    
    # Environment-based settings
    config.environment = os.getenv('SECURITY_ENV', 'development')
    
    # Database and Redis
    config.database_url = os.getenv('DATABASE_URL', config.database_url)
    config.redis_url = os.getenv('REDIS_URL', config.redis_url)
    
    # Logging
    config.log_level = os.getenv('SECURITY_LOG_LEVEL', config.log_level)
    config.log_to_file = os.getenv('SECURITY_LOG_TO_FILE', 'true').lower() == 'true'
    config.log_to_console = os.getenv('SECURITY_LOG_TO_CONSOLE', 'true').lower() == 'true'
    
    # Email configuration
    config.email_config.update({
        'smtp_server': os.getenv('SMTP_SERVER', ''),
        'smtp_port': os.getenv('SMTP_PORT', '587'),
        'username': os.getenv('SMTP_USERNAME', ''),
        'password': os.getenv('SMTP_PASSWORD', ''),
        'from_address': os.getenv('SECURITY_EMAIL_FROM', 'security@company.com'),
        'to_addresses': os.getenv('SECURITY_EMAIL_TO', 'admin@company.com,security@company.com')
    })
    
    # Slack configuration
    config.slack_config.update({
        'webhook_url': os.getenv('SLACK_WEBHOOK_URL', ''),
        'channel': os.getenv('SLACK_CHANNEL', '#security-alerts'),
        'bot_name': os.getenv('SLACK_BOT_NAME', 'SecurityBot')
    })
    
    # Feature flags
    for feature in config.features:
        env_var = f'SECURITY_FEATURE_{feature.upper()}'
        config.features[feature] = os.getenv(env_var, 'true' if config.features[feature] else 'false').lower() == 'true'
    
    # Rate limiting specific settings
    if os.getenv('RATE_LIMIT_ENABLED'):
        config.rate_limiting.enabled = os.getenv('RATE_LIMIT_ENABLED').lower() == 'true'
    
    # Monitoring settings
    if os.getenv('SECURITY_MONITORING_ENABLED'):
        config.monitoring.enabled = os.getenv('SECURITY_MONITORING_ENABLED').lower() == 'true'
    
    return config


def validate_config(config: SecurityConfig) -> List[str]:
    """Konfiguratsiyani validate qilish"""
    errors = []
    
    # Environment validation
    if config.environment not in ['development', 'staging', 'production']:
        errors.append(f"Invalid environment: {config.environment}")
    
    # Email validation
    if not config.email_config.get('from_address'):
        errors.append("Email from address is required")
    
    # Rate limiting validation
    if config.rate_limiting.enabled:
        if config.rate_limiting.default_requests_per_minute <= 0:
            errors.append("Default requests per minute must be positive")
        
        if config.rate_limiting.default_burst_limit <= 0:
            errors.append("Default burst limit must be positive")
    
    # Monitoring validation
    if config.monitoring.enabled and config.monitoring.anomaly_detection_enabled:
        if config.monitoring.baseline_period_hours <= 0:
            errors.append("Baseline period must be positive")
        
        if config.monitoring.anomaly_threshold <= 0:
            errors.append("Anomaly threshold must be positive")
    
    # Data protection validation
    if config.data_protection.encryption_enabled:
        if config.data_protection.encryption_algorithm not in ['AES-256', 'AES-128']:
            errors.append(f"Unsupported encryption algorithm: {config.data_protection.encryption_algorithm}")
    
    return errors


def get_config_for_environment(env: str) -> SecurityConfig:
    """Environment uchun specific konfiguratsiya"""
    base_config = get_security_config()
    
    if env == 'development':
        # More permissive settings for development
        base_config.rate_limiting.default_requests_per_minute = 1000
        base_config.monitoring.log_level = 'DEBUG'
        base_config.input_validation.strict_mode = False
        base_config.security_headers.content_security_policy = "default-src 'self' 'unsafe-inline' 'unsafe-eval'"
        
    elif env == 'staging':
        # Production-like but with more relaxed settings
        base_config.rate_limiting.default_requests_per_minute = 200
        base_config.monitoring.log_level = 'INFO'
        
    elif env == 'production':
        # Strict security settings
        base_config.rate_limiting.default_requests_per_minute = 60
        base_config.monitoring.log_level = 'WARNING'
        base_config.input_validation.strict_mode = True
        base_config.security_headers.content_security_policy = "default-src 'self'"
        
        # Remove development features
        base_config.features.update({
            'debug_mode': False,
            'verbose_logging': False,
            'test_endpoints': False
        })
    
    return base_config


def export_config(config: SecurityConfig) -> Dict[str, Any]:
    """Konfiguratsiyani export qilish (secrets olmagan holda)"""
    safe_config = {}
    
    # Create a safe version without sensitive data
    config_dict = config.__dict__.copy()
    
    # Remove sensitive fields
    safe_config['environment'] = config.environment
    safe_config['rate_limiting'] = config.rate_limiting.__dict__
    safe_config['security_headers'] = {k: v for k, v in config.security_headers.__dict__.items() 
                                     if not k.startswith('smtp') and k != 'password'}
    safe_config['input_validation'] = config.input_validation.__dict__
    safe_config['api_keys'] = {k: v for k, v in config.api_keys.__dict__.items() 
                              if k != 'secret'}
    safe_config['data_protection'] = config.data_protection.__dict__
    safe_config['monitoring'] = config.monitoring.__dict__
    safe_config['features'] = config.features
    
    return safe_config


def load_config_from_file(file_path: str) -> SecurityConfig:
    """Fayldan konfiguratsiyani yuklash"""
    import json
    try:
        with open(file_path, 'r') as f:
            config_data = json.load(f)
        
        # Create config from data
        config = SecurityConfig()
        
        # Apply configuration
        for section, data in config_data.items():
            if hasattr(config, section):
                section_config = getattr(config, section)
                for key, value in data.items():
                    if hasattr(section_config, key):
                        setattr(section_config, key, value)
        
        return config
        
    except Exception as e:
        logger.error(f"Failed to load config from {file_path}: {e}")
        return SecurityConfig()


def save_config_to_file(config: SecurityConfig, file_path: str):
    """Konfiguratsiyani faylga saqlash"""
    import json
    try:
        config_data = export_config(config)
        
        with open(file_path, 'w') as f:
            json.dump(config_data, f, indent=2, default=str)
        
        logger.info(f"Configuration saved to {file_path}")
        
    except Exception as e:
        logger.error(f"Failed to save config to {file_path}: {e}")


# Logging setup
import logging
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = get_security_config()