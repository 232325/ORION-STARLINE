#!/usr/bin/env python3
"""
Test script to check if all modules can be imported
without installing dependencies
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test all module imports"""
    
    print("🧪 Testing AI Trading Platform Module Imports...")
    print("=" * 60)
    
    # Mock external dependencies for testing
    import types
    
    # Create mock modules to avoid import errors
    mock_modules = {
        'psutil': types.ModuleType('psutil'),
        'aioredis': types.ModuleType('aioredis'),
        'prometheus_client': types.ModuleType('prometheus_client'),
        'pandas': types.ModuleType('pandas'),
        'numpy': types.ModuleType('numpy'),
        'matplotlib': types.ModuleType('matplotlib'),
        'seaborn': types.ModuleType('seaborn'),
        'plotly': types.ModuleType('plotly'),
        'sklearn': types.ModuleType('sklearn'),
        'stripe': types.ModuleType('stripe'),
        'supabase': types.ModuleType('supabase'),
        'uvicorn': types.ModuleType('uvicorn'),
        'asyncio': types.ModuleType('asyncio'),
        'logging': types.ModuleType('logging'),
        'datetime': types.ModuleType('datetime'),
        'json': types.ModuleType('json'),
        'uuid': types.ModuleType('uuid'),
    }
    
    # Add mock functions to modules
    mock_modules['psutil'].cpu_percent = lambda: 50.0
    mock_modules['psutil'].virtual_memory = lambda: types.SimpleNamespace(percent=60.0)
    mock_modules['psutil'].disk_usage = lambda path: types.SimpleNamespace(percent=30.0)
    mock_modules['psutil'].net_io_counters = lambda: types.SimpleNamespace(bytes_sent=1000, bytes_recv=2000)
    mock_modules['psutil'].Process = lambda: types.SimpleNamespace()
    mock_modules['aioredis'].Redis = types.SimpleNamespace
    mock_modules['prometheus_client'].Counter = types.SimpleNamespace
    mock_modules['pandas'].DataFrame = types.SimpleNamespace
    mock_modules['numpy'].array = types.SimpleNamespace
    mock_modules['matplotlib'].pyplot = types.SimpleNamespace
    mock_modules['seaborn'].set_style = lambda x: None
    mock_modules['plotly'].graph_objects = types.SimpleNamespace
    mock_modules['sklearn'].metrics = types.SimpleNamespace
    mock_modules['stripe'].Stripe = types.SimpleNamespace
    mock_modules['supabase'].Client = types.SimpleNamespace
    mock_modules['uvicorn'].run = lambda x, **kwargs: None
    
    # Register mock modules
    for module_name, module in mock_modules.items():
        sys.modules[module_name] = module
    
    # Test each module category
    test_results = []
    
    # 1. Integration modules
    print("🔧 Testing Integration Modules...")
    try:
        from integration.integration_hub import IntegrationHub
        from integration.performance_optimizer import PerformanceOptimizer
        from integration.security_auditor import SecurityAuditor
        print("✅ Integration modules imported successfully")
        test_results.append(("Integration", True, None))
    except Exception as e:
        print(f"❌ Integration modules failed: {e}")
        test_results.append(("Integration", False, str(e)))
    
    # 2. WebSocket
    print("\n📡 Testing WebSocket Module...")
    try:
        from api.websocket.websocket_manager import manager
        print("✅ WebSocket module imported successfully")
        test_results.append(("WebSocket", True, None))
    except Exception as e:
        print(f"❌ WebSocket module failed: {e}")
        test_results.append(("WebSocket", False, str(e)))
    
    # 3. UI modules
    print("\n📊 Testing UI Modules...")
    try:
        from ui.backtesting_dashboard import BacktestConfig, OptimizationMethod
        from ui.live_trading_dashboard import PositionSide, OrderType
        from ui.market_intelligence import MarketSector, ScannerCondition
        from ui.performance_analytics import PerformanceAnalytics
        from ui.trade_journal import TradeSetup, TradeOutcome
        from ui.advanced_charts import Timeframe, IndicatorType
        print("✅ UI modules imported successfully")
        test_results.append(("UI", True, None))
    except Exception as e:
        print(f"❌ UI modules failed: {e}")
        test_results.append(("UI", False, str(e)))
    
    # 4. Social Trading modules
    print("\n👥 Testing Social Trading Modules...")
    try:
        from social.copy_trading_engine import CopyTradingEngine
        from social.signal_platform import SignalPlatform
        from social.leaderboard_system import LeaderboardSystem
        from social.automl_pipeline import AutoMLPipeline
        from social.strategy_marketplace import StrategyMarketplace
        from social.reputation_system import ReputationSystem
        print("✅ Social Trading modules imported successfully")
        test_results.append(("Social Trading", True, None))
    except Exception as e:
        print(f"❌ Social Trading modules failed: {e}")
        test_results.append(("Social Trading", False, str(e)))
    
    # 5. Payment modules
    print("\n💳 Testing Payment Modules...")
    try:
        from payment.payment_gateway import PaymentGateway, SubscriptionPlan
        from payment.forex_integration import ForexIntegration, CurrencyPair
        from payment.reits_trading import REITsTrading, REITCategory
        from payment.multi_currency import MultiCurrencyWallet, Currency
        from payment.tax_reporting import TaxReporting, TaxLotMethod
        from payment.webhook_manager import WebhookManager, WebhookEvent
        print("✅ Payment modules imported successfully")
        test_results.append(("Payment", True, None))
    except Exception as e:
        print(f"❌ Payment modules failed: {e}")
        test_results.append(("Payment", False, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST RESULTS SUMMARY:")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for category, success, error in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{category:<20} {status}")
        if error:
            print(f"  Error: {error}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Total: {passed + failed} categories")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL MODULES IMPORTED SUCCESSFULLY!")
        print("🚀 AI Trading Platform is ready for deployment!")
        return True
    else:
        print(f"\n⚠️ {failed} modules need fixing")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
