"""
AI Trading Bots - Test Suite
============================

Bu fayl AI Trading Bot tizimi uchun unit testlar va integration testlarni
o'z ichiga oladi.

Ishlatish:
python -m pytest test_ai_trading_bots.py -v
yoki
python test_ai_trading_bots.py
"""

import asyncio
import unittest
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from ai_trading_bots import (
    AITradingBot, BotManager, ConfigurationManager,
    BotConfig, BotType, RiskParameters, PositionSide,
    BotStatus, ScalpingStrategy, SwingTradingStrategy,
    MLTradingStrategy, RiskManager, PortfolioManager,
    MarketData, TradingSignal, TradeResult,
    DeploymentAutomation
)


class TestMarketData(unittest.TestCase):
    """MarketData class testlari"""
    
    def test_market_data_creation(self):
        """MarketData yaratish testi"""
        market_data = MarketData(
            symbol="EURUSD",
            price=1.1000,
            volume=1000.0,
            timestamp=datetime.now(),
            bid=1.0999,
            ask=1.1001,
            spread=0.0002
        )
        
        self.assertEqual(market_data.symbol, "EURUSD")
        self.assertEqual(market_data.price, 1.1000)
        self.assertEqual(market_data.volume, 1000.0)
    
    def test_market_data_to_dict(self):
        """MarketData to_dict testi"""
        market_data = MarketData(
            symbol="EURUSD",
            price=1.1000,
            volume=1000.0,
            timestamp=datetime.now(),
            bid=1.0999,
            ask=1.1001,
            spread=0.0002
        )
        
        data_dict = market_data.to_dict()
        self.assertIsInstance(data_dict, dict)
        self.assertEqual(data_dict['symbol'], "EURUSD")
        self.assertEqual(data_dict['price'], 1.1000)


class TestTradingSignal(unittest.TestCase):
    """TradingSignal class testlari"""
    
    def test_trading_signal_creation(self):
        """TradingSignal yaratish testi"""
        signal = TradingSignal(
            id="test_001",
            symbol="EURUSD",
            action="BUY",
            confidence=0.8,
            price=1.1000,
            timestamp=datetime.now(),
            strategy="test_strategy",
            metadata={"test": "data"}
        )
        
        self.assertEqual(signal.symbol, "EURUSD")
        self.assertEqual(signal.action, "BUY")
        self.assertEqual(signal.confidence, 0.8)
    
    def test_trading_signal_to_dict(self):
        """TradingSignal to_dict testi"""
        timestamp = datetime.now()
        signal = TradingSignal(
            id="test_001",
            symbol="EURUSD",
            action="BUY",
            confidence=0.8,
            price=1.1000,
            timestamp=timestamp,
            strategy="test_strategy",
            metadata={"test": "data"}
        )
        
        data_dict = signal.to_dict()
        self.assertIsInstance(data_dict, dict)
        self.assertEqual(data_dict['symbol'], "EURUSD")
        self.assertEqual(data_dict['action'], "BUY")


class TestRiskParameters(unittest.TestCase):
    """RiskParameters class testlari"""
    
    def test_risk_parameters_creation(self):
        """RiskParameters yaratish testi"""
        risk_params = RiskParameters(
            max_position_size=5000,
            stop_loss_percent=0.05,
            take_profit_percent=0.1,
            max_drawdown=2.0,
            daily_loss_limit=500,
            max_risk_per_trade=250
        )
        
        self.assertEqual(risk_params.max_position_size, 5000)
        self.assertEqual(risk_params.stop_loss_percent, 0.05)
        self.assertEqual(risk_params.take_profit_percent, 0.1)
    
    def test_risk_parameters_to_dict(self):
        """RiskParameters to_dict testi"""
        risk_params = RiskParameters(
            max_position_size=5000,
            stop_loss_percent=0.05,
            take_profit_percent=0.1,
            max_drawdown=2.0,
            daily_loss_limit=500,
            max_risk_per_trade=250
        )
        
        data_dict = risk_params.to_dict()
        self.assertIsInstance(data_dict, dict)
        self.assertEqual(data_dict['max_position_size'], 5000)


class TestBotConfig(unittest.TestCase):
    """BotConfig class testlari"""
    
    def test_bot_config_creation(self):
        """BotConfig yaratish testi"""
        risk_params = RiskParameters(
            max_position_size=5000,
            stop_loss_percent=0.05,
            take_profit_percent=0.1,
            max_drawdown=2.0,
            daily_loss_limit=500,
            max_risk_per_trade=250
        )
        
        config = BotConfig(
            bot_id="test_001",
            name="Test Bot",
            bot_type=BotType.SCALPING,
            strategy="test_strategy",
            symbols=["EURUSD"],
            initial_capital=10000,
            risk_params=risk_params,
            trading_hours=["09:30", "16:00"],
            max_concurrent_positions=3,
            auto_trading=True,
            notifications={"email": True}
        )
        
        self.assertEqual(config.bot_id, "test_001")
        self.assertEqual(config.bot_type, BotType.SCALPING)
        self.assertEqual(config.initial_capital, 10000)


class TestScalpingStrategy(unittest.TestCase):
    """ScalpingStrategy class testlari"""
    
    def setUp(self):
        """Test setup"""
        self.strategy = ScalpingStrategy()
    
    def test_strategy_initialization(self):
        """Strategy initialization testi"""
        self.assertEqual(self.strategy.timeframe, "1m")
        self.assertEqual(self.strategy.profit_target, 0.1)
        self.assertEqual(self.strategy.stop_loss, 0.05)
    
    def test_market_data_analysis(self):
        """Market data analysis testi"""
        market_data = MarketData(
            symbol="EURUSD",
            price=1.1000,
            volume=1000.0,
            timestamp=datetime.now(),
            bid=1.0999,
            ask=1.1001,
            spread=0.0002
        )
        
        # Sync call uchun
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            signal = loop.run_until_complete(self.strategy.analyze(market_data))
            self.assertIsInstance(signal, TradingSignal)
            self.assertEqual(signal.symbol, "EURUSD")
        finally:
            loop.close()


class TestSwingTradingStrategy(unittest.TestCase):
    """SwingTradingStrategy class testlari"""
    
    def setUp(self):
        """Test setup"""
        self.strategy = SwingTradingStrategy()
    
    def test_strategy_initialization(self):
        """Strategy initialization testi"""
        self.assertEqual(self.strategy.timeframe, "1h")
        self.assertEqual(self.strategy.rsi_period, 14)
        self.assertEqual(self.strategy.rsi_oversold, 30)


class TestRiskManager(unittest.TestCase):
    """RiskManager class testlari"""
    
    def setUp(self):
        """Test setup"""
        self.risk_params = RiskParameters(
            max_position_size=5000,
            stop_loss_percent=0.05,
            take_profit_percent=0.1,
            max_drawdown=2.0,
            daily_loss_limit=500,
            max_risk_per_trade=250
        )
        self.risk_manager = RiskManager(self.risk_params)
    
    def test_risk_manager_initialization(self):
        """RiskManager initialization testi"""
        self.assertEqual(self.risk_manager.daily_pnl, 0.0)
        self.assertFalse(self.risk_manager.max_daily_loss_reached)
    
    def test_risk_limits_check(self):
        """Risk limits check testi"""
        # Normal trade
        can_trade, message = self.risk_manager.check_risk_limits(
            "EURUSD", PositionSide.LONG, 1000, 1.1000
        )
        self.assertTrue(can_trade)
        
        # Large position
        can_trade, message = self.risk_manager.check_risk_limits(
            "EURUSD", PositionSide.LONG, 10000, 1.1000
        )
        self.assertFalse(can_trade)
    
    def test_position_update(self):
        """Position update testi"""
        trade = TradeResult(
            trade_id="test_001",
            symbol="EURUSD",
            side=PositionSide.LONG,
            quantity=1000,
            entry_price=1.1000,
            exit_price=1.1100,
            pnl=100.0,
            status="closed",
            timestamp=datetime.now(),
            duration=timedelta(minutes=30)
        )
        
        self.risk_manager.update_position(trade)
        self.assertEqual(self.risk_manager.daily_pnl, 100.0)
        self.assertEqual(len(self.risk_manager.positions), 1)


class TestPortfolioManager(unittest.TestCase):
    """PortfolioManager class testlari"""
    
    def setUp(self):
        """Test setup"""
        self.portfolio_manager = PortfolioManager(initial_capital=100000)
    
    def test_portfolio_initialization(self):
        """Portfolio initialization testi"""
        self.assertEqual(self.portfolio_manager.initial_capital, 100000)
        self.assertEqual(self.portfolio_manager.current_capital, 100000)
    
    def test_capital_allocation(self):
        """Capital allocation testi"""
        risk_params = RiskParameters(
            max_position_size=5000,
            stop_loss_percent=0.05,
            take_profit_percent=0.1,
            max_drawdown=2.0,
            daily_loss_limit=500,
            max_risk_per_trade=250
        )
        
        config = BotConfig(
            bot_id="test_001",
            name="Test Bot",
            bot_type=BotType.SCALPING,
            strategy="test",
            symbols=["EURUSD"],
            initial_capital=10000,
            risk_params=risk_params,
            trading_hours=["09:30", "16:00"],
            max_concurrent_positions=3,
            auto_trading=True,
            notifications={}
        )
        
        allocation = self.portfolio_manager.allocate_capital([config])
        self.assertIn("test_001", allocation)
        self.assertEqual(allocation["test_001"], 100000)  # Equal allocation
    
    def test_portfolio_update(self):
        """Portfolio update testi"""
        trade = TradeResult(
            trade_id="test_001",
            symbol="EURUSD",
            side=PositionSide.LONG,
            quantity=1000,
            entry_price=1.1000,
            exit_price=1.1100,
            pnl=100.0,
            status="closed",
            timestamp=datetime.now(),
            duration=timedelta(minutes=30)
        )
        
        self.portfolio_manager.update_portfolio(trade)
        self.assertEqual(self.portfolio_manager.current_capital, 100100)
        self.assertEqual(len(self.portfolio_manager.closed_positions), 1)


class TestAITradingBot(unittest.TestCase):
    """AITradingBot class testlari"""
    
    def setUp(self):
        """Test setup"""
        risk_params = RiskParameters(
            max_position_size=5000,
            stop_loss_percent=0.05,
            take_profit_percent=0.1,
            max_drawdown=2.0,
            daily_loss_limit=500,
            max_risk_per_trade=250
        )
        
        self.config = BotConfig(
            bot_id="test_bot_001",
            name="Test Trading Bot",
            bot_type=BotType.SCALPING,
            strategy="test_strategy",
            symbols=["EURUSD"],
            initial_capital=10000,
            risk_params=risk_params,
            trading_hours=["09:30", "16:00"],
            max_concurrent_positions=2,
            auto_trading=True,
            notifications={"email": False, "sms": False, "telegram": False}
        )
        
        self.bot = AITradingBot(self.config)
    
    def test_bot_initialization(self):
        """Bot initialization testi"""
        self.assertEqual(self.bot.bot_id, "test_bot_001")
        self.assertEqual(self.bot.status, BotStatus.STOPPED)
        self.assertIsNotNone(self.bot.strategy)
        self.assertIsNotNone(self.bot.risk_manager)
    
    def test_strategy_initialization(self):
        """Strategy initialization testi"""
        self.assertIsInstance(self.bot.strategy, ScalpingStrategy)


class TestBotManager(unittest.TestCase):
    """BotManager class testlari"""
    
    def setUp(self):
        """Test setup"""
        self.bot_manager = BotManager()
    
    def test_bot_manager_initialization(self):
        """BotManager initialization testi"""
        self.assertEqual(len(self.bot_manager.bots), 0)
        self.assertIsNotNone(self.bot_manager.portfolio_manager)
    
    def test_create_bot(self):
        """Bot yaratish testi"""
        risk_params = RiskParameters(
            max_position_size=5000,
            stop_loss_percent=0.05,
            take_profit_percent=0.1,
            max_drawdown=2.0,
            daily_loss_limit=500,
            max_risk_per_trade=250
        )
        
        config = BotConfig(
            bot_id="test_bot_001",
            name="Test Bot",
            bot_type=BotType.SCALPING,
            strategy="test",
            symbols=["EURUSD"],
            initial_capital=10000,
            risk_params=risk_params,
            trading_hours=["09:30", "16:00"],
            max_concurrent_positions=2,
            auto_trading=True,
            notifications={}
        )
        
        bot = self.bot_manager.create_bot(config)
        self.assertIsInstance(bot, AITradingBot)
        self.assertEqual(len(self.bot_manager.bots), 1)


class TestConfigurationManager(unittest.TestCase):
    """ConfigurationManager class testlari"""
    
    def setUp(self):
        """Test setup"""
        self.config_manager = ConfigurationManager("test_configs.json")
    
    def test_create_sample_configurations(self):
        """Sample configurations yaratish testi"""
        configs = self.config_manager.create_sample_configurations()
        
        self.assertGreater(len(configs), 0)
        
        for bot_id, config in configs.items():
            self.assertIsInstance(config, BotConfig)
            self.assertIsNotNone(config.bot_id)
            self.assertIsNotNone(config.name)
    
    def test_save_and_load_configurations(self):
        """Save va load configurations testi"""
        # Sample configs yaratish
        configs = self.config_manager.create_sample_configurations()
        
        # Save qilish
        result = self.config_manager.save_configurations(configs)
        self.assertTrue(result)
        
        # Load qilish
        loaded_configs = self.config_manager.load_configurations()
        self.assertEqual(len(loaded_configs), len(configs))


class TestDeploymentAutomation(unittest.TestCase):
    """DeploymentAutomation class testlari"""
    
    def setUp(self):
        """Test setup"""
        self.bot_manager = BotManager()
        self.deployment = DeploymentAutomation(self.bot_manager)
    
    def test_deployment_initialization(self):
        """Deployment initialization testi"""
        self.assertIsNotNone(self.deployment.bot_manager)
        self.assertTrue(self.deployment.monitoring_enabled)
        self.assertTrue(self.deployment.alerts_enabled)


class TestIntegration(unittest.TestCase):
    """Integration testlar"""
    
    def test_full_workflow(self):
        """To'liq workflow testi"""
        # Configuration yaratish
        config_manager = ConfigurationManager("integration_test.json")
        configs = config_manager.create_sample_configurations()
        
        # Bot manager yaratish
        bot_manager = BotManager()
        
        # Bot yaratish
        bot_id = list(configs.keys())[0]
        config = configs[bot_id]
        bot = bot_manager.create_bot(config)
        
        # Bot summary olish
        summary = bot.get_performance_summary()
        
        self.assertIsInstance(summary, dict)
        self.assertIn('bot_id', summary)
        self.assertEqual(summary['bot_id'], bot_id)


async def run_async_test(test_func):
    """Async test ishga tushirish uchun helper"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return await test_func()
    finally:
        loop.close()


def create_test_data():
    """Test data yaratish"""
    # Market data
    market_data = MarketData(
        symbol="EURUSD",
        price=1.1000,
        volume=1000.0,
        timestamp=datetime.now(),
        bid=1.0999,
        ask=1.1001,
        spread=0.0002
    )
    
    # Historical data
    dates = pd.date_range('2024-01-01', periods=100, freq='1H')
    np.random.seed(42)
    
    historical_data = pd.DataFrame({
        'timestamp': dates,
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 102,
        'low': np.random.randn(100).cumsum() + 98,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    return market_data, historical_data


def main():
    """Testlarni ishga tushirish"""
    print("🧪 AI Trading Bots - Test Suite")
    print("=" * 40)
    
    # Test data yaratish
    market_data, historical_data = create_test_data()
    
    print(f"📊 Test data yaratildi:")
    print(f"   Market Data: {market_data.symbol}")
    print(f"   Historical Data: {len(historical_data)} points")
    
    # Unit testlarni ishga tushirish
    print(f"\n🔬 Unit Testlarni ishga tushirish...")
    
    # Test classes
    test_classes = [
        TestMarketData,
        TestTradingSignal,
        TestRiskParameters,
        TestBotConfig,
        TestScalpingStrategy,
        TestSwingTradingStrategy,
        TestRiskManager,
        TestPortfolioManager,
        TestAITradingBot,
        TestBotManager,
        TestConfigurationManager,
        TestDeploymentAutomation,
        TestIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 {test_class.__name__}:")
        
        # Test instance yaratish
        test_instance = test_class()
        
        # setUp metodini chaqirish
        if hasattr(test_instance, 'setUp'):
            test_instance.setUp()
        
        # Test methods
        test_methods = [method for method in dir(test_instance) 
                       if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            
            try:
                method = getattr(test_instance, method_name)
                method()
                print(f"   ✅ {method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"   ❌ {method_name}: {e}")
    
    # Natijalar
    print(f"\n📊 Test Natijalari:")
    print(f"   Jami testlar: {total_tests}")
    print(f"   Muvaffaqiyatli: {passed_tests}")
    print(f"   Xato: {total_tests - passed_tests}")
    print(f"   Muvaffaqiyatlik foizi: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print(f"\n🎉 Barcha testlar muvaffaqiyatli o'tdi!")
    else:
        print(f"\n⚠️ Ba'zi testlar xato berdi")


if __name__ == "__main__":
    main()