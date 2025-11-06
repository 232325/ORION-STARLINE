"""
AI Trading Bots - Demo Script
============================

Bu fayl AI Trading Bot tizimini ishlatish uchun oddiy demo misollar
va test kodlarini o'z ichiga oladi.

Ishlatish:
python demo_ai_trading_bots.py
"""

import asyncio
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from ai_trading_bots import (
    AITradingBot, BotManager, ConfigurationManager, 
    BotConfig, BotType, RiskParameters, PositionSide,
    BotStatus, DeploymentAutomation, create_demo_bot_configurations
)


async def demo_basic_bot():
    """Oddiy bot yaratish va ishga tushirish demo"""
    print("🤖 Basic Bot Demo")
    print("=" * 40)
    
    # 1. Risk parameters yaratish
    risk_params = RiskParameters(
        max_position_size=1000,
        stop_loss_percent=0.05,
        take_profit_percent=0.1,
        max_drawdown=2.0,
        daily_loss_limit=100,
        max_risk_per_trade=50
    )
    
    # 2. Bot konfiguratsiyasi
    config = BotConfig(
        bot_id="demo_scalping_001",
        name="Demo Scalping Bot",
        bot_type=BotType.SCALPING,
        strategy="price_momentum",
        symbols=["EURUSD"],
        initial_capital=5000,
        risk_params=risk_params,
        trading_hours=["09:30", "16:00"],
        max_concurrent_positions=2,
        auto_trading=True,
        notifications={"email": False, "sms": False, "telegram": False}
    )
    
    # 3. Bot yaratish
    bot = AITradingBot(config)
    
    # 4. Botni ishga tushirish
    print(f"Botni ishga tushirish: {config.name}")
    success = await bot.start()
    
    if success:
        print("✅ Bot muvaffaqiyatli ishga tushdi!")
        
        # 30 soniya kutish
        print("⏳ 30 soniya ishlashi uchun kutish...")
        await asyncio.sleep(30)
        
        # Performance ko'rsatish
        summary = bot.get_performance_summary()
        print(f"📊 Performance Summary:")
        print(f"   Status: {summary['status']}")
        print(f"   Total Trades: {summary['total_trades']}")
        print(f"   Win Rate: {summary['win_rate']:.2%}")
        print(f"   Total P&L: ${summary['total_pnl']:.2f}")
        
        # Botni to'xtatish
        await bot.stop()
        print("🛑 Bot to'xtatildi")
    else:
        print("❌ Bot ishga tushmadi")


async def demo_multiple_bots():
    """Bir nechta bot bilan ishlash demo"""
    print("\n🚀 Multiple Bots Demo")
    print("=" * 40)
    
    # Bot manager
    bot_manager = BotManager()
    
    # Configuration manager
    config_manager = ConfigurationManager()
    
    # Sample configurations
    configurations = config_manager.create_sample_configurations()
    
    print(f"📋 {len(configurations)} ta bot konfiguratsiyasi yaratildi:")
    
    # Botlarni yaratish va ishga tushirish
    for bot_id, config in configurations.items():
        print(f"\n🤖 Creating bot: {config.name}")
        
        bot = bot_manager.create_bot(config)
        print(f"   Bot ID: {bot_id}")
        print(f"   Strategy: {config.bot_type.value}")
        print(f"   Initial Capital: ${config.initial_capital:,}")
        
        # Botni ishga tushirish
        success = await bot_manager.start_bot(bot_id)
        if success:
            print(f"   ✅ Successfully started")
        else:
            print(f"   ❌ Failed to start")
    
    # 60 soniya kutish
    print(f"\n⏳ 60 soniya ishlashi uchun kutish...")
    await asyncio.sleep(60)
    
    # Portfolio summary
    print(f"\n💼 Portfolio Summary:")
    portfolio = bot_manager.get_portfolio_summary()
    
    print(f"   Total Bots: {portfolio['total_bots']}")
    print(f"   Running Bots: {portfolio['running_bots']}")
    print(f"   Portfolio Value: ${portfolio['total_portfolio_value']:,.2f}")
    
    # Individual bot performance
    print(f"\n📊 Individual Bot Performance:")
    for bot_summary in portfolio['bot_summaries']:
        print(f"   {bot_summary['name']}:")
        print(f"     Status: {bot_summary['status']}")
        print(f"     Trades: {bot_summary['total_trades']}")
        print(f"     Win Rate: {bot_summary['win_rate']:.2%}")
        print(f"     P&L: ${bot_summary['total_pnl']:.2f}")
    
    # Barcha botlarni to'xtatish
    print(f"\n🛑 Barcha botlarni to'xtatish...")
    await bot_manager.stop_all_bots()
    print("✅ Barcha botlar to'xtatildi")


async def demo_backtesting():
    """Strategy backtesting demo"""
    print("\n🧪 Backtesting Demo")
    print("=" * 40)
    
    # Sample historical data yaratish
    print("📊 Sample historical data yaratish...")
    
    dates = pd.date_range('2024-01-01', periods=1000, freq='1H')
    np.random.seed(42)  # Reproducible results
    
    # Realistic price data
    base_price = 1.1000
    returns = np.random.normal(0, 0.001, 1000)  # 0.1% hourly volatility
    prices = base_price * (1 + returns).cumprod()
    
    # OHLC data
    historical_data = pd.DataFrame({
        'timestamp': dates,
        'open': prices * np.random.uniform(0.999, 1.001, 1000),
        'high': prices * np.random.uniform(1.001, 1.005, 1000),
        'low': prices * np.random.uniform(0.995, 0.999, 1000),
        'close': prices,
        'volume': np.random.randint(1000, 10000, 1000)
    })
    
    print(f"   Data points: {len(historical_data)}")
    print(f"   Date range: {historical_data['timestamp'].min()} to {historical_data['timestamp'].max()}")
    print(f"   Price range: ${historical_data['low'].min():.4f} - ${historical_data['high'].max():.4f}")
    
    # Bot configuration
    config = BotConfig(
        bot_id="backtest_scalping_001",
        name="Backtest Scalping Bot",
        bot_type=BotType.SCALPING,
        strategy="backtest",
        symbols=["EURUSD"],
        initial_capital=10000,
        risk_params=RiskParameters(
            max_position_size=2000,
            stop_loss_percent=0.03,
            take_profit_percent=0.06,
            max_drawdown=2.0,
            daily_loss_limit=200,
            max_risk_per_trade=100
        ),
        trading_hours=["09:30", "16:00"],
        max_concurrent_positions=2,
        auto_trading=False,
        notifications={}
    )
    
    # Bot yaratish
    bot = AITradingBot(config)
    
    # Backtest
    print(f"\n🔍 Strategy backtesting...")
    results = await bot.backtest_strategy(historical_data)
    
    if "error" not in results:
        print(f"✅ Backtest Results:")
        print(f"   Total Trades: {results['total_trades']}")
        print(f"   Winning Trades: {results['winning_trades']}")
        print(f"   Win Rate: {results['win_rate']:.2%}")
        print(f"   Average Profit: {results['average_profit']:.2f}%")
        print(f"   Total Return: {results['total_return']:.2f}%")
        
        # Calculate additional metrics
        if results['total_trades'] > 0:
            max_profit = max([t['pnl'] for t in results['trades']]) if 'trades' in results else 0
            max_loss = min([t['pnl'] for t in results['trades']]) if 'trades' in results else 0
            
            print(f"   Max Profit: {max_profit:.2f}%")
            print(f"   Max Loss: {max_loss:.2f}%")
            
            # Risk metrics
            if results['total_return'] != 0:
                profit_factor = abs(sum([t['pnl'] for t in results['trades'] if t['pnl'] > 0]) / 
                                 sum([t['pnl'] for t in results['trades'] if t['pnl'] < 0]))
                print(f"   Profit Factor: {profit_factor:.2f}")
    else:
        print(f"❌ Backtest Error: {results['error']}")


async def demo_risk_management():
    """Risk management demo"""
    print("\n🛡️ Risk Management Demo")
    print("=" * 40)
    
    # Risk manager
    risk_params = RiskParameters(
        max_position_size=5000,
        stop_loss_percent=0.05,
        take_profit_percent=0.10,
        max_drawdown=2.0,
        daily_loss_limit=500,
        max_risk_per_trade=250
    )
    
    from ai_trading_bots import RiskManager, TradeResult
    
    risk_manager = RiskManager(risk_params)
    
    print(f"📋 Risk Parameters:")
    print(f"   Max Position Size: ${risk_params.max_position_size:,}")
    print(f"   Stop Loss: {risk_params.stop_loss_percent}%")
    print(f"   Take Profit: {risk_params.take_profit_percent}%")
    print(f"   Max Drawdown: {risk_params.max_drawdown}%")
    print(f"   Daily Loss Limit: ${risk_params.daily_loss_limit:,}")
    print(f"   Max Risk per Trade: ${risk_params.max_risk_per_trade:,}")
    
    # Risk limit tests
    print(f"\n🔍 Risk Limit Tests:")
    
    # Test 1: Normal trade
    can_trade, message = risk_manager.check_risk_limits(
        "EURUSD", PositionSide.LONG, 1000, 1.1000
    )
    print(f"   Normal Trade (1000 units @ $1.1000): {can_trade} - {message}")
    
    # Test 2: Large position
    can_trade, message = risk_manager.check_risk_limits(
        "EURUSD", PositionSide.LONG, 10000, 1.1000
    )
    print(f"   Large Position (10000 units): {can_trade} - {message}")
    
    # Test 3: High risk trade
    can_trade, message = risk_manager.check_risk_limits(
        "EURUSD", PositionSide.LONG, 5000, 1.1000
    )
    print(f"   High Risk Trade (5000 units): {can_trade} - {message}")
    
    # Simulate trades
    print(f"\n📊 Simulated Trades:")
    for i in range(5):
        trade = TradeResult(
            trade_id=f"trade_{i+1}",
            symbol="EURUSD",
            side=PositionSide.LONG,
            quantity=1000,
            entry_price=1.1000,
            exit_price=1.1000 + np.random.uniform(-0.01, 0.02),
            pnl=np.random.uniform(-100, 200),
            status="closed",
            timestamp=datetime.now() - timedelta(hours=i),
            duration=timedelta(minutes=np.random.randint(5, 60))
        )
        
        risk_manager.update_position(trade)
        
        pnl_status = "✅" if trade.pnl > 0 else "❌"
        print(f"   {pnl_status} Trade {i+1}: P&L = ${trade.pnl:.2f}")
    
    # Final risk status
    print(f"\n📈 Final Risk Status:")
    print(f"   Daily P&L: ${risk_manager.daily_pnl:.2f}")
    print(f"   Current Drawdown: {risk_manager.get_current_drawdown(5000):.2f}%")
    print(f"   Active Positions: {len(risk_manager.positions)}")


async def demo_portfolio_management():
    """Portfolio management demo"""
    print("\n💼 Portfolio Management Demo")
    print("=" * 40)
    
    # Portfolio manager
    from ai_trading_bots import PortfolioManager
    
    portfolio_manager = PortfolioManager(initial_capital=100000)
    
    print(f"💰 Initial Portfolio Value: ${portfolio_manager.initial_capital:,}")
    
    # Create multiple bot configs
    configs = create_demo_bot_configurations()
    
    # Capital allocation
    print(f"\n📊 Capital Allocation:")
    allocation = portfolio_manager.allocate_capital(list(configs.values()))
    
    for bot_id, capital in allocation.items():
        config = configs[bot_id]
        percentage = (capital / portfolio_manager.initial_capital) * 100
        print(f"   {config.name}: ${capital:,.2f} ({percentage:.1f}%)")
    
    # Simulate portfolio performance
    print(f"\n📈 Simulated Performance:")
    
    import random
    for i in range(10):
        bot_id = random.choice(list(configs.keys()))
        config = configs[bot_id]
        
        # Simulate trade
        pnl = random.uniform(-500, 1000)
        
        from ai_trading_bots import TradeResult, PositionSide
        
        trade = TradeResult(
            trade_id=f"portfolio_trade_{i+1}",
            symbol=config.symbols[0],
            side=PositionSide.LONG,
            quantity=1000,
            entry_price=1.1000,
            exit_price=1.1000,
            pnl=pnl,
            status="closed",
            timestamp=datetime.now() - timedelta(days=i),
            duration=timedelta(hours=random.randint(1, 8))
        )
        
        portfolio_manager.update_portfolio(trade)
        
        pnl_status = "✅" if pnl > 0 else "❌"
        print(f"   {pnl_status} {config.name}: ${pnl:.2f}")
    
    # Final portfolio metrics
    print(f"\n💎 Final Portfolio Metrics:")
    metrics = portfolio_manager.get_performance_metrics()
    
    if "error" not in metrics:
        print(f"   Total Trades: {metrics['total_trades']}")
        print(f"   Winning Trades: {metrics['winning_trades']}")
        print(f"   Win Rate: {metrics['win_rate']:.2%}")
        print(f"   Total P&L: ${metrics['total_pnl']:.2f}")
        print(f"   Current Capital: ${metrics['current_capital']:,.2f}")
        print(f"   Total Return: {metrics['total_return']:.2f}%")
        print(f"   Open Positions: {metrics['open_positions']}")
    else:
        print(f"   Error: {metrics['error']}")


async def demo_deployment_automation():
    """Deployment automation demo"""
    print("\n🚀 Deployment Automation Demo")
    print("=" * 40)
    
    # Bot manager
    bot_manager = BotManager()
    
    # Configuration manager
    config_manager = ConfigurationManager()
    
    # Create sample configurations
    configurations = config_manager.create_sample_configurations()
    
    # Deployment automation
    deployment = DeploymentAutomation(bot_manager)
    
    print(f"📦 Deploying {len(configurations)} bots...")
    
    # Deploy bots
    deployment_results = await deployment.deploy_bots(configurations)
    
    for bot_id, success in deployment_results.items():
        status = "✅" if success else "❌"
        print(f"   {status} {bot_id}")
    
    # Health check
    print(f"\n🔍 Health Check:")
    health = await deployment.health_check()
    
    print(f"   Overall Health: {'✅ Healthy' if health['overall_health'] else '❌ Unhealthy'}")
    
    for bot_id, bot_health in health['bots'].items():
        health_status = {
            "healthy": "✅",
            "warning": "⚠️",
            "unhealthy": "❌"
        }.get(bot_health['health'], "❓")
        
        print(f"   {health_status} {bot_id}: {bot_health['status']} - {bot_health['health']}")
    
    # Simulate monitoring for 30 seconds
    print(f"\n📊 Monitoring for 30 seconds...")
    
    # Start monitoring in background
    monitoring_task = asyncio.create_task(deployment.monitor_performance())
    
    await asyncio.sleep(30)
    
    # Cancel monitoring
    monitoring_task.cancel()
    
    # Stop all bots
    print(f"\n🛑 Stopping all bots...")
    await bot_manager.stop_all_bots()
    
    print("✅ Deployment demo completed")


async def main():
    """Asosiy demo funktsiyasi"""
    print("🚀 AI Trading Bots - Complete Demo")
    print("=" * 50)
    print("Bu demo barcha AI Trading Bot funksiyalarini namoyish etadi:")
    print("• Basic bot operations")
    print("• Multiple bot management")
    print("• Backtesting")
    print("• Risk management")
    print("• Portfolio management")
    print("• Deployment automation")
    print()
    
    try:
        # 1. Basic bot demo
        await demo_basic_bot()
        
        # 2. Multiple bots demo
        await demo_multiple_bots()
        
        # 3. Backtesting demo
        await demo_backtesting()
        
        # 4. Risk management demo
        await demo_risk_management()
        
        # 5. Portfolio management demo
        await demo_portfolio_management()
        
        # 6. Deployment automation demo
        await demo_deployment_automation()
        
        print(f"\n🎉 Barcha demolar muvaffaqiyatli yakunlandi!")
        print(f"✅ AI Trading Bots tizimi to'liq ishlayapti!")
        
    except Exception as e:
        print(f"\n❌ Demo xatosi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Demo ishga tushirish
    asyncio.run(main())