"""
Marketing Configuration Settings
Marketing modullari uchun konfiguratsiya fayli
"""

from typing import Dict, List, Optional
from pydantic import BaseSettings, Field
import os

class MarketingConfig(BaseSettings):
    """Marketing modullarining konfiguratsiya sozlamalari"""
    
    # Content Marketing
    CONTENT_API_ENDPOINT: str = Field(default="https://api.openai.com/v1/chat/completions", env="CONTENT_API_ENDPOINT")
    CONTENT_API_KEY: str = Field(default="", env="CONTENT_API_KEY")
    CONTENT_MODEL: str = Field(default="gpt-4", env="CONTENT_MODEL")
    CONTENT_MAX_TOKENS: int = Field(default=2048, env="CONTENT_MAX_TOKENS")
    
    # SEO Settings
    GOOGLE_API_KEY: str = Field(default="", env="GOOGLE_API_KEY")
    SEMRUSH_API_KEY: str = Field(default="", env="SEMRUSH_API_KEY")
    AHREFS_API_TOKEN: str = Field(default="", env="AHREFS_API_TOKEN")
    GOOGLE_SEARCH_CONSOLE_EMAIL: str = Field(default="", env="GOOGLE_SEARCH_CONSOLE_EMAIL")
    
    # Social Media APIs
    FACEBOOK_ACCESS_TOKEN: str = Field(default="", env="FACEBOOK_ACCESS_TOKEN")
    FACEBOOK_APP_ID: str = Field(default="", env="FACEBOOK_APP_ID")
    FACEBOOK_APP_SECRET: str = Field(default="", env="FACEBOOK_APP_SECRET")
    
    TWITTER_API_KEY: str = Field(default="", env="TWITTER_API_KEY")
    TWITTER_API_SECRET: str = Field(default="", env="TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN: str = Field(default="", env="TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_SECRET: str = Field(default="", env="TWITTER_ACCESS_SECRET")
    
    LINKEDIN_ACCESS_TOKEN: str = Field(default="", env="LINKEDIN_ACCESS_TOKEN")
    LINKEDIN_CLIENT_ID: str = Field(default="", env="LINKEDIN_CLIENT_ID")
    LINKEDIN_CLIENT_SECRET: str = Field(default="", env="LINKEDIN_CLIENT_SECRET")
    
    INSTAGRAM_ACCESS_TOKEN: str = Field(default="", env="INSTAGRAM_ACCESS_TOKEN")
    INSTAGRAM_CLIENT_ID: str = Field(default="", env="INSTAGRAM_CLIENT_ID")
    INSTAGRAM_CLIENT_SECRET: str = Field(default="", env="INSTAGRAM_CLIENT_SECRET")
    
    YOUTUBE_API_KEY: str = Field(default="", env="YOUTUBE_API_KEY")
    YOUTUBE_CLIENT_ID: str = Field(default="", env="YOUTUBE_CLIENT_ID")
    YOUTUBE_CLIENT_SECRET: str = Field(default="", env="YOUTUBE_CLIENT_SECRET")
    
    TIKTOK_CLIENT_KEY: str = Field(default="", env="TIKTOK_CLIENT_KEY")
    TIKTOK_CLIENT_SECRET: str = Field(default="", env="TIKTOK_CLIENT_SECRET")
    
    # Email Marketing
    SMTP_HOST: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: str = Field(default="", env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    SMTP_USE_TLS: bool = Field(default=True, env="SMTP_USE_TLS")
    
    SENDGRID_API_KEY: str = Field(default="", env="SENDGRID_API_KEY")
    MAILCHIMP_API_KEY: str = Field(default="", env="MAILCHIMP_API_KEY")
    MAILCHIMP_SERVER_PREFIX: str = Field(default="us1", env="MAILCHIMP_SERVER_PREFIX")
    
    # Analytics
    GOOGLE_ANALYTICS_ID: str = Field(default="", env="GOOGLE_ANALYTICS_ID")
    GOOGLE_ANALYTICS_SECRET: str = Field(default="", env="GOOGLE_ANALYTICS_SECRET")
    FACEBOOK_PIXEL_ID: str = Field(default="", env="FACEBOOK_PIXEL_ID")
    
    # Referral System
    REFERRAL_REWARD_TYPES: List[str] = Field(
        default=["cash", "credits", "commission", "discount"],
        env="REFERRAL_REWARD_TYPES"
    )
    DEFAULT_REFERRAL_TIERS: Dict[str, Dict] = Field(
        default={
            "bronze": {"min_referrals": 0, "commission_rate": 0.05},
            "silver": {"min_referrals": 11, "commission_rate": 0.08},
            "gold": {"min_referrals": 51, "commission_rate": 0.12},
            "platinum": {"min_referrals": 101, "commission_rate": 0.15}
        },
        env="DEFAULT_REFERRAL_TIERS"
    )
    
    # Conversion Optimization
    AB_TEST_CONFIDENCE_LEVEL: float = Field(default=0.95, env="AB_TEST_CONFIDENCE_LEVEL")
    AB_TEST_MIN_SAMPLE_SIZE: int = Field(default=100, env="AB_TEST_MIN_SAMPLE_SIZE")
    CONVERSION_TRACKING_ENABLED: bool = Field(default=True, env="CONVERSION_TRACKING_ENABLED")
    
    # Influencer Management
    INFLUENCER_PLATFORMS: List[str] = Field(
        default=["youtube", "instagram", "tiktok", "twitter", "linkedin"],
        env="INFLUENCER_PLATFORMS"
    )
    INFLUENCER_MIN_FOLLOWERS: int = Field(default=10000, env="INFLUENCER_MIN_FOLLOWERS")
    INFLUENCER_ENGAGEMENT_THRESHOLD: float = Field(default=0.03, env="INFLUENCER_ENGAGEMENT_THRESHOLD")
    
    # Community Management
    COMMUNITY_MODERATION_ENABLED: bool = Field(default=True, env="COMMUNITY_MODERATION_ENABLED")
    AUTO_MODERATION_KEYWORDS: List[str] = Field(
        default=["spam", "fake", "scam", "bot"],
        env="AUTO_MODERATION_KEYWORDS"
    )
    COMMUNITY_REPUTATION_WEIGHTS: Dict[str, float] = Field(
        default={
            "post_quality": 0.3,
            "helpfulness": 0.4,
            "engagement": 0.3
        },
        env="COMMUNITY_REPUTATION_WEIGHTS"
    )
    
    # Content Generation
    CONTENT_TEMPLATES: Dict[str, str] = Field(
        default={
            "blog_post": "You are a professional content writer. Write a comprehensive blog post about {topic} for {audience} audience.",
            "social_media": "Create engaging social media content about {topic} for {platform} platform.",
            "email_subject": "Write compelling email subject lines for {topic} that increase open rates.",
            "seo_title": "Create SEO-optimized titles for {keyword} that rank well in search results."
        },
        env="CONTENT_TEMPLATES"
    )
    
    # Performance Monitoring
    PERFORMANCE_MONITORING_ENABLED: bool = Field(default=True, env="PERFORMANCE_MONITORING_ENABLED")
    METRICS_RETENTION_DAYS: int = Field(default=90, env="METRICS_RETENTION_DAYS")
    ALERT_THRESHOLDS: Dict[str, float] = Field(
        default={
            "conversion_rate_drop": 0.2,
            "engagement_rate_drop": 0.3,
            "referral_rate_drop": 0.25
        },
        env="ALERT_THRESHOLDS"
    )
    
    # Security
    API_RATE_LIMITS: Dict[str, int] = Field(
        default={
            "content_generation": 100,  # per hour
            "social_posting": 50,       # per hour
            "email_sending": 500,       # per hour
            "analytics_api": 1000       # per hour
        },
        env="API_RATE_LIMITS"
    )
    
    # Feature Flags
    FEATURE_FLAGS: Dict[str, bool] = Field(
        default={
            "ai_content_generation": True,
            "social_automation": True,
            "email_campaigns": True,
            "referral_system": True,
            "ab_testing": True,
            "influencer_management": True,
            "community_features": True,
            "advanced_analytics": True
        },
        env="FEATURE_FLAGS"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global configuration instance
marketing_config = MarketingConfig()

# Helper functions
def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    return marketing_config.FEATURE_FLAGS.get(feature_name, False)

def get_api_credentials(service: str) -> Dict[str, str]:
    """Get API credentials for a specific service"""
    credentials = {}
    
    if service == "google":
        credentials = {
            "api_key": marketing_config.GOOGLE_API_KEY,
            "analytics_id": marketing_config.GOOGLE_ANALYTICS_ID,
            "analytics_secret": marketing_config.GOOGLE_ANALYTICS_SECRET
        }
    elif service == "facebook":
        credentials = {
            "access_token": marketing_config.FACEBOOK_ACCESS_TOKEN,
            "app_id": marketing_config.FACEBOOK_APP_ID,
            "app_secret": marketing_config.FACEBOOK_APP_SECRET
        }
    elif service == "twitter":
        credentials = {
            "api_key": marketing_config.TWITTER_API_KEY,
            "api_secret": marketing_config.TWITTER_API_SECRET,
            "access_token": marketing_config.TWITTER_ACCESS_TOKEN,
            "access_secret": marketing_config.TWITTER_ACCESS_SECRET
        }
    elif service == "linkedin":
        credentials = {
            "access_token": marketing_config.LINKEDIN_ACCESS_TOKEN,
            "client_id": marketing_config.LINKEDIN_CLIENT_ID,
            "client_secret": marketing_config.LINKEDIN_CLIENT_SECRET
        }
    elif service == "instagram":
        credentials = {
            "access_token": marketing_config.INSTAGRAM_ACCESS_TOKEN,
            "client_id": marketing_config.INSTAGRAM_CLIENT_ID,
            "client_secret": marketing_config.INSTAGRAM_CLIENT_SECRET
        }
    elif service == "youtube":
        credentials = {
            "api_key": marketing_config.YOUTUBE_API_KEY,
            "client_id": marketing_config.YOUTUBE_CLIENT_ID,
            "client_secret": marketing_config.YOUTUBE_CLIENT_SECRET
        }
    elif service == "email":
        credentials = {
            "smtp_host": marketing_config.SMTP_HOST,
            "smtp_port": marketing_config.SMTP_PORT,
            "smtp_username": marketing_config.SMTP_USERNAME,
            "smtp_password": marketing_config.SMTP_PASSWORD,
            "sendgrid_api_key": marketing_config.SENDGRID_API_KEY,
            "mailchimp_api_key": marketing_config.MAILCHIMP_API_KEY
        }
    
    return credentials

def get_rate_limit(service: str) -> int:
    """Get rate limit for a service"""
    return marketing_config.API_RATE_LIMITS.get(service, 60)

def get_template(template_name: str, **kwargs) -> str:
    """Get a content template with variables substituted"""
    template = marketing_config.CONTENT_TEMPLATES.get(template_name, "")
    return template.format(**kwargs)

# Validation
def validate_config():
    """Validate marketing configuration"""
    errors = []
    
    # Check required API keys based on enabled features
    if is_feature_enabled("ai_content_generation") and not marketing_config.CONTENT_API_KEY:
        errors.append("CONTENT_API_KEY is required when AI content generation is enabled")
    
    if is_feature_enabled("social_automation") and not any([
        marketing_config.FACEBOOK_ACCESS_TOKEN,
        marketing_config.TWITTER_API_KEY,
        marketing_config.LINKEDIN_ACCESS_TOKEN
    ]):
        errors.append("At least one social media API key is required when social automation is enabled")
    
    if is_feature_enabled("email_campaigns") and not any([
        marketing_config.SMTP_USERNAME,
        marketing_config.SENDGRID_API_KEY
    ]):
        errors.append("Email service credentials are required when email campaigns are enabled")
    
    if is_feature_enabled("advanced_analytics") and not marketing_config.GOOGLE_ANALYTICS_ID:
        errors.append("Google Analytics ID is required when advanced analytics is enabled")
    
    return errors

# Initialize validation on import
validation_errors = validate_config()
if validation_errors:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Marketing configuration validation warnings: {validation_errors}")