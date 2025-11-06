"""
Uchinchi Tomon Integratsiya Modullari
Orion Starline Trading Platform

Bu paket uchinchi tomon xizmatlari bilan integratsiyani ta'minlaydi:
- MetaTrader 4/5
- Interactive Brokers
- TradingView
- Slack
- Discord
- Webhook tizimi
- Boshqa brokerlar

Muallif: Orion Starline Team
Sana: 2025-11-05
"""

from .third_party_integrations import (
    ThirdPartyIntegration,
    ThirdPartyIntegrationManager,
    IntegrationConfig,
    IntegrationType,
    IntegrationStatus,
    IntegrationEvent,
    create_integration_manager
)

from .metatrader_integration import (
    MetaTraderIntegration,
    MTOrderType,
    MTOrderStatus,
    MTPosition,
    MTOrder,
    MTAccount,
    MTQuote,
    create_metatrader_integration
)

from .brokers_integration import (
    BrokerIntegration,
    BrokerType,
    BrokerAccount,
    BrokerPosition,
    BrokerOrder,
    MarketData,
    OrderSide,
    OrderType,
    OrderStatus,
    BrokerAdapter,
    InteractiveBrokersAdapter,
    AlpacaAdapter,
    create_broker_integration
)

from .webhook_system import (
    WebhookSystemIntegration,
    TradingViewIntegration,
    SlackIntegration,
    DiscordIntegration,
    WebhookManager,
    WebhookType,
    WebhookStatus,
    WebhookEvent,
    WebhookEndpoint,
    WebhookSecurity,
    create_tradingview_integration,
    create_slack_integration,
    create_discord_integration,
    create_webhook_system_integration
)

__version__ = "1.0.0"
__author__ = "Orion Starline Team"

# All available integrations
AVAILABLE_INTEGRATIONS = {
    "metatrader": create_metatrader_integration,
    "interactive_brokers": create_broker_integration,
    "tradingview": create_tradingview_integration,
    "slack": create_slack_integration,
    "discord": create_discord_integration,
    "webhook_system": create_webhook_system_integration
}

# Integration types mapping
INTEGRATION_TYPES = {
    IntegrationType.METATRADER: "MetaTrader",
    IntegrationType.INTERACTIVE_BROKERS: "Interactive Brokers",
    IntegrationType.TRADINGVIEW: "TradingView",
    IntegrationType.SLACK: "Slack",
    IntegrationType.DISCORD: "Discord",
    IntegrationType.WEBHOOK: "Webhook System",
    IntegrationType.BROKER_API: "Broker API"
}

# Quick setup functions
async def quick_setup_mt5(name: str, server_url: str, port: int = 443) -> MetaTraderIntegration:
    """MetaTrader 5 ni tez sozlash"""
    config = IntegrationConfig(
        integration_type=IntegrationType.METATRADER,
        name=name,
        enabled=True,
        server_url=server_url,
        port=port
    )
    return create_metatrader_integration(config)

async def quick_setup_interactive_brokers(name: str, client_id: int = 1, 
                                        host: str = "localhost", port: int = 7497) -> BrokerIntegration:
    """Interactive Brokers ni tez sozlash"""
    config = IntegrationConfig(
        integration_type=IntegrationType.INTERACTIVE_BROKERS,
        name=name,
        enabled=True,
        metadata={
            "broker_type": "interactive_brokers",
            "client_id": client_id,
            "host": host,
            "port": port
        }
    )
    return create_broker_integration(config)

async def quick_setup_alpaca(name: str, api_key: str, secret_key: str, paper: bool = True) -> BrokerIntegration:
    """Alpaca Markets ni tez sozlash"""
    config = IntegrationConfig(
        integration_type=IntegrationType.BROKER_API,
        name=name,
        enabled=True,
        api_key=api_key,
        api_secret=secret_key,
        metadata={
            "broker_type": "alpaca",
            "paper": paper
        }
    )
    return create_broker_integration(config)

async def quick_setup_tradingview(name: str, webhook_url: str) -> TradingViewIntegration:
    """TradingView ni tez sozlash"""
    config = IntegrationConfig(
        integration_type=IntegrationType.TRADINGVIEW,
        name=name,
        enabled=True,
        metadata={
            "webhook_url": webhook_url
        }
    )
    return create_tradingview_integration(config)

async def quick_setup_slack(name: str, webhook_url: str) -> SlackIntegration:
    """Slack ni tez sozlash"""
    config = IntegrationConfig(
        integration_type=IntegrationType.SLACK,
        name=name,
        enabled=True,
        metadata={
            "webhook_url": webhook_url
        }
    )
    return create_slack_integration(config)

async def quick_setup_discord(name: str, webhook_url: str) -> DiscordIntegration:
    """Discord ni tez sozlash"""
    config = IntegrationConfig(
        integration_type=IntegrationType.DISCORD,
        name=name,
        enabled=True,
        metadata={
            "webhook_url": webhook_url
        }
    )
    return create_discord_integration(config)

async def quick_setup_webhook_system(name: str, endpoints: dict = None) -> WebhookSystemIntegration:
    """Webhook tizimini tez sozlash"""
    config = IntegrationConfig(
        integration_type=IntegrationType.WEBHOOK,
        name=name,
        enabled=True
    )
    
    webhook_system = create_webhook_system_integration(config)
    
    if endpoints:
        for endpoint_name, endpoint_data in endpoints.items():
            endpoint = WebhookEndpoint(**endpoint_data)
            webhook_system.add_webhook_endpoint(endpoint_name, endpoint)
    
    return webhook_system

# Demo va test funksiyalari
async def run_integration_demo():
    """Barcha integratsiyalar uchun demo"""
    from .third_party_integrations import demo_integration_manager
    from .metatrader_integration import demo_metatrader_integration
    from .brokers_integration import demo_broker_integration
    from .webhook_system import demo_webhook_system
    
    print("=== Orion Starline Integration System Demo ===\n")
    
    # Run all demos
    demos = [
        ("Third-Party Integration Manager", demo_integration_manager),
        ("MetaTrader Integration", demo_metatrader_integration),
        ("Broker Integration", demo_broker_integration),
        ("Webhook System", demo_webhook_system)
    ]
    
    for name, demo_func in demos:
        print(f"\n{'='*50}")
        print(f"Running {name} Demo")
        print('='*50)
        try:
            await demo_func()
        except Exception as e:
            print(f"Demo failed: {e}")
    
    print("\n=== All Demos Complete ===")

async def test_integration_health(integrations: list) -> dict:
    """Integratsiyalar salomatligini test qilish"""
    results = {}
    
    for integration in integrations:
        try:
            health = await integration.health_check()
            results[integration.config.name] = {
                "status": "healthy",
                "details": health
            }
        except Exception as e:
            results[integration.config.name] = {
                "status": "unhealthy",
                "error": str(e)
            }
    
    return results

# Configuration templates
DEFAULT_CONFIGS = {
    "metatrader": {
        "integration_type": "metatrader",
        "name": "MT5_Default",
        "enabled": True,
        "server_url": "localhost",
        "port": 443,
        "timeout": 30,
        "retry_attempts": 3
    },
    
    "interactive_brokers": {
        "integration_type": "interactive_brokers",
        "name": "IB_Default",
        "enabled": True,
        "metadata": {
            "broker_type": "interactive_brokers",
            "client_id": 1,
            "host": "localhost",
            "port": 7497
        }
    },
    
    "tradingview": {
        "integration_type": "tradingview",
        "name": "TradingView_Default",
        "enabled": True,
        "metadata": {
            "webhook_url": "https://hooks.tradingview.com/hooks/your-webhook-url"
        }
    },
    
    "slack": {
        "integration_type": "slack",
        "name": "Slack_Default",
        "enabled": True,
        "metadata": {
            "webhook_url": "https://hooks.slack.com/services/your-webhook-url"
        }
    },
    
    "discord": {
        "integration_type": "discord",
        "name": "Discord_Default",
        "enabled": True,
        "metadata": {
            "webhook_url": "https://discord.com/api/webhooks/your-webhook-url"
        }
    }
}

def get_default_config(integration_type: str) -> dict:
    """Standart konfiguratsiya olish"""
    return DEFAULT_CONFIGS.get(integration_type, {})

# Export all main classes and functions
__all__ = [
    # Main classes
    "ThirdPartyIntegration",
    "ThirdPartyIntegrationManager",
    "MetaTraderIntegration",
    "BrokerIntegration",
    "TradingViewIntegration",
    "SlackIntegration",
    "DiscordIntegration",
    "WebhookSystemIntegration",
    
    # Configuration classes
    "IntegrationConfig",
    "WebhookEndpoint",
    "WebhookSecurity",
    
    # Enums
    "IntegrationType",
    "IntegrationStatus",
    "BrokerType",
    "WebhookType",
    "OrderSide",
    "OrderType",
    "OrderStatus",
    "MTOrderType",
    "MTOrderStatus",
    
    # Data classes
    "IntegrationEvent",
    "BrokerAccount",
    "BrokerPosition",
    "BrokerOrder",
    "MarketData",
    "MTPosition",
    "MTOrder",
    "MTAccount",
    "MTQuote",
    "WebhookEvent",
    
    # Factory functions
    "create_integration_manager",
    "create_metatrader_integration",
    "create_broker_integration",
    "create_tradingview_integration",
    "create_slack_integration",
    "create_discord_integration",
    "create_webhook_system_integration",
    
    # Quick setup functions
    "quick_setup_mt5",
    "quick_setup_interactive_brokers",
    "quick_setup_alpaca",
    "quick_setup_tradingview",
    "quick_setup_slack",
    "quick_setup_discord",
    "quick_setup_webhook_system",
    
    # Utility functions
    "run_integration_demo",
    "test_integration_health",
    "get_default_config",
    
    # Constants
    "AVAILABLE_INTEGRATIONS",
    "INTEGRATION_TYPES",
    "DEFAULT_CONFIGS"
]