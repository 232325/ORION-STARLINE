"""
Market Regime Detection System Demo
Bozor rejimini aniqlash tizimi demo
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from market_regime_detector import MarketRegimeDetector, MarketRegime, RegimeConfig, create_sample_data
from strategy_switcher import StrategySwitcher, StrategyType
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_realistic_market_data(days=200):
    """Real bozor ma'lumotlariga o'xshash data yaratish"""
    np.random.seed(42)
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), periods=days, freq='D')
    
    # Trend patterns
    trend_periods = [
        (0, 50, 0.001),   # Bull trend
        (51, 100, -0.001), # Bear trend
        (101, 150, 0.0005), # Sideways
        (151, 200, 0.002)   # Strong bull
    ]
    
    prices = []
    current_price = 100
    
    for start, end, trend in trend_periods:
        for i in range(start, min(end, days)):
            # Trend + noise + volatility clusters
            daily_return = trend + np.random.normal(0, 0.02)
            if i in range(80, 90) or i in range(160, 170):  # High volatility periods
                daily_return += np.random.normal(0, 0.05)
            
            current_price *= (1 + daily_return)
            prices.append(current_price)
    
    # OHLCV data creation
    price_series = pd.Series(prices)
    data = pd.DataFrame({
        'timestamp': dates[:len(prices)],
        'open': price_series * (1 + np.random.normal(0, 0.002, len(prices))),
        'high': price_series * (1 + np.abs(np.random.normal(0, 0.01, len(prices)))),
        'low': price_series * (1 - np.abs(np.random.normal(0, 0.01, len(prices)))),
        'close': price_series,
        'volume': np.random.randint(1000000, 10000000, len(prices))
    })
    
    return data

def demonstrate_regime_detection():
    """Rejim aniqlash tizimini namoyish qilish"""
    print("="*60)
    print("BOZOR REJIMINI ANIQLASH TIZIMI DEMO")
    print("="*60)
    
    # Sample data
    data = create_realistic_market_data(200)
    print(f"Yaratilgan ma'lumot: {len(data)} kunlik OHLCV data")
    
    # Regime Detector yaratish
    config = RegimeConfig(
        trend_threshold=0.02,
        volatility_threshold=0.02,
        volume_threshold=1.5,
        ma_short_period=10,
        ma_long_period=50
    )
    
    detector = MarketRegimeDetector(config)
    print(f"Rejim detektori yaratildi")
    
    # Har bir hafta uchun rejim aniqlash
    regime_history = []
    weekly_data_points = []
    
    for week in range(4, len(data), 7):  # Har hafta
        weekly_data = data.iloc[:week+1]
        result = detector.detect_regime(weekly_data)
        regime_history.append(result)
        weekly_data_points.append(week)
        
        print(f"Kun {week+1:3d}: Rejim = {result.regime.value:20s} | "
              f"Ishonchlilik = {result.confidence:.2f} | "
              f"Signal kuchi = {result.signal_strength:.2f}")
    
    # Final statistika
    stats = detector.get_regime_statistics()
    print("\n" + "="*50)
    print("REJIM STATISTIKALARI:")
    print("="*50)
    print(f"Jami kuzatuvlar: {stats['total_observations']}")
    print(f"Joriy rejim: {stats['current_regime']}")
    print(f"O'rtacha ishonchlilik: {stats['average_confidence']:.2f}")
    print(f"O'rtacha barqarorlik: {stats['average_persistence']:.2f}")
    
    print("\nRejim tarqalishi:")
    for regime, percentage in stats['regime_percentages'].items():
        print(f"  {regime:20s}: {percentage:5.1f}%")
    
    return regime_history, detector

def demonstrate_strategy_switching():
    """Strategiya almashtirish tizimini namoyish qilish"""
    print("\n" + "="*60)
    print("STRATEGIYA ALMASHTIRISH TIZIMI DEMO")
    print("="*60)
    
    # Data
    data = create_realistic_market_data(200)
    
    # Strategy Switcher yaratish
    switcher = StrategySwitcher()
    print(f"Strategy Switcher yaratildi")
    print(f"Mavjud strategiyalar: {len(switcher.strategies)}")
    
    # Har hafta uchun strategiya tanlash
    strategy_history = []
    
    for week in range(50, len(data), 10):  # Har 10 kunda
        weekly_data = data.iloc[:week+1]
        strategy = switcher.select_strategy(weekly_data)
        
        if strategy:
            # Trade signals yaratish
            signals = switcher.generate_trade_signals(strategy, weekly_data)
            
            strategy_info = {
                'day': week+1,
                'strategy': strategy.name,
                'regime': switcher.current_regime.regime.value,
                'confidence': switcher.current_regime.confidence,
                'signals_count': len(signals)
            }
            
            strategy_history.append(strategy_info)
            
            print(f"Kun {week+1:3d}: {strategy.name:20s} | "
                  f"Rejim: {switcher.current_regime.regime.value:15s} | "
                  f"Signallar: {len(signals):2d} | "
                  f"Ishonchlilik: {switcher.current_regime.confidence:.2f}")
    
    # Performance summary
    print("\n" + "="*50)
    print("STRATEGIYA XULOSASI:")
    print("="*50)
    
    strategy_counts = {}
    for item in strategy_history:
        strategy_name = item['strategy']
        strategy_counts[strategy_name] = strategy_counts.get(strategy_name, 0) + 1
    
    print("Eng faol strategiyalar:")
    for strategy, count in sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        percentage = (count / len(strategy_history)) * 100
        print(f"  {strategy:20s}: {count:2d} marta ({percentage:5.1f}%)")
    
    return strategy_history, switcher

def demonstrate_risk_management():
    """Risk boshqaruv tizimini namoyish qilish"""
    print("\n" + "="*60)
    print("RISK BOSHQARUV TIZIMI DEMO")
    print("="*60)
    
    # Data
    data = create_realistic_market_data(100)
    switcher = StrategySwitcher()
    
    # Strategiya tanlash
    strategy = switcher.select_strategy(data)
    if strategy:
        print(f"Tanlangan strategiya: {strategy.name}")
        print(f"Maksimal pozitsiya hajmi: {strategy.max_position_size:.1%}")
        print(f"Stop Loss: {strategy.stop_loss_pct:.1%}")
        print(f"Take Profit: {strategy.take_profit_pct:.1%}")
        
        # Pozitsiya hajmi hisoblash
        account_value = 10000  # $10,000
        position_size = switcher.calculate_position_size(strategy, data, account_value)
        position_value = position_size * account_value
        
        print(f"\nKapital taqsimlash:")
        print(f"  Hisob qiymati: ${account_value:,}")
        print(f"Pozitsiya hajmi: {position_size:.1%}")
        print(f"Pozitsiya qiymati: ${position_value:,.2f}")
        
        # Risk calculation
        risk_value = position_value * strategy.stop_loss_pct
        risk_percentage = risk_value / account_value
        
        print(f"\nRisk hisoblash:")
        print(f"  Maksimal yo'qotish: ${risk_value:.2f}")
        print(f"  Risk foizi: {risk_percentage:.2%}")
        
        if risk_percentage <= switcher.risk_manager.max_portfolio_risk:
            print("  ✅ Risk limit ichida")
        else:
            print("  ❌ Risk limit oshdi")

def demonstrate_portfolio_management():
    """Portfolio boshqaruv tizimini namoyish qilish"""
    print("\n" + "="*60)
    print("PORTFOLIO BOSHQARUV TIZIMI DEMO")
    print("="*60)
    
    # Sample positions
    switcher = StrategySwitcher()
    
    # Simulate multiple positions
    sample_prices = {'BTCUSDT': 45000, 'ETHUSDT': 3000, 'ADAUSDT': 0.5}
    
    # Create some sample positions
    from strategy_switcher import Position
    from datetime import datetime
    
    positions_data = [
        {'symbol': 'BTCUSDT', 'side': 'long', 'size': 0.1, 'entry_price': 44000, 'current_price': 45000},
        {'symbol': 'ETHUSDT', 'side': 'long', 'size': 2.0, 'entry_price': 2950, 'current_price': 3000},
        {'symbol': 'ADAUSDT', 'side': 'short', 'size': 1000, 'entry_price': 0.52, 'current_price': 0.50}
    ]
    
    for pos_data in positions_data:
        position = Position(
            symbol=pos_data['symbol'],
            size=pos_data['size'],
            entry_price=pos_data['entry_price'],
            current_price=pos_data['current_price'],
            side=pos_data['side'],
            stop_loss=pos_data['entry_price'] * 0.95,
            take_profit=pos_data['entry_price'] * 1.05,
            timestamp=datetime.now(),
            strategy="Demo Strategy"
        )
        
        if position.side == 'long':
            position.pnl = (position.current_price - position.entry_price) * position.size
            position.pnl_pct = (position.current_price - position.entry_price) / position.entry_price
        else:
            position.pnl = (position.entry_price - position.current_price) * position.size
            position.pnl_pct = (position.entry_price - position.current_price) / position.entry_price
        
        position_id = f"{position.symbol}_{position.timestamp.strftime('%Y%m%d_%H%M%S')}"
        switcher.positions[position_id] = position
    
    # Portfolio metrics
    portfolio_metrics = switcher.calculate_portfolio_metrics()
    
    print("Aktiv pozitsiyalar:")
    for position_id, position in switcher.positions.items():
        print(f"  {position.symbol:10s}: {position.side:5s} | "
              f"Hajmi: {position.size:8.2f} | "
              f"PnL: ${position.pnl:8.2f} ({position.pnl_pct:+6.2%})")
    
    print(f"\nPortfolio metrikalari:")
    print(f"  Jami qiymat: ${portfolio_metrics['total_value']:,.2f}")
    print(f"  Jami PnL: ${portfolio_metrics['total_pnl']:+.2f} ({portfolio_metrics['total_pnl_pct']:+.2%})")
    print(f"  Ochiq pozitsiyalar: {portfolio_metrics['open_positions']}")
    print(f"  O'rtacha pozitsiya: ${portfolio_metrics['avg_position_size']:,.2f}")

def demonstrate_advanced_features():
    """Kengaytirilgan xususiyatlarni namoyish qilish"""
    print("\n" + "="*60)
    print("KENGAYTIRILGAN XUSUSIYATLAR DEMO")
    print("="*60)
    
    # Multi-timeframe analysis
    print("1. Ko'p vaqt doiralari tahlili:")
    data = create_realistic_market_data(100)
    detector = MarketRegimeDetector()
    
    # Create different timeframes (simulated)
    multi_timeframe_data = {
        '1h': data.iloc[-50:],    # Last 50 days as 1h data
        '4h': data.iloc[-30:],    # Last 30 days as 4h data  
        '1d': data.iloc[-20:],    # Last 20 days as 1d data
    }
    
    multi_results = detector.detect_regimes_multi_timeframe(multi_timeframe_data)
    for timeframe, result in multi_results.items():
        print(f"  {timeframe:3s}: {result.regime.value:15s} (ishonchlilik: {result.confidence:.2f})")
    
    # Regime transitions
    print(f"\n2. Rejim o'zgarishlari:")
    transitions = detector.get_regime_transitions(days=30)
    if transitions:
        for trans in transitions[-5:]:  # Last 5 transitions
            print(f"  {trans['from'].value} → {trans['to'].value} "
                  f"({trans['timestamp'].strftime('%Y-%m-%d %H:%M')})")
    else:
        print("  Rejim o'zgarishlari topilmadi")
    
    # Machine Learning prediction (skip if sklearn not available)
    print(f"\n3. Machine Learning bashorati:")
    try:
        # Create training data (simplified)
        historical_data = [data.iloc[:i+50] for i in range(50, min(len(data)-1, 100), 10)]
        historical_regimes = [detector.detect_regime(d).regime for d in historical_data]
        
        # Train ML model
        success = detector.train_ml_model(historical_data, historical_regimes)
        if success:
            print("  ✅ ML model muvaffaqiyatli o'qitildi")
            
            # Test prediction
            test_data = data.iloc[-50:]
            ml_result = detector.predict_regime_ml(test_data)
            if ml_result:
                print(f"  ML bashorat: {ml_result.regime.value} (ishonchlilik: {ml_result.confidence:.2f})")
        else:
            print("  ❌ ML model o'qitishda xatolik")
    except Exception as e:
        print(f"  ⚠️  ML funksiyalari mavjud emas: {str(e)[:50]}...")
    
    # Performance analytics
    print(f"\n4. Performance analitika:")
    # Simulate some performance data
    switcher = StrategySwitcher()
    demo_trades = [
        {'pnl_pct': 0.02}, {'pnl_pct': -0.01}, {'pnl_pct': 0.03},
        {'pnl_pct': -0.02}, {'pnl_pct': 0.01}, {'pnl_pct': 0.04}
    ]
    
    switcher.update_performance_history("Demo Strategy", demo_trades)
    performance = switcher.get_strategy_performance("Demo Strategy")
    
    if performance:
        print(f"  Jami return: {performance.total_return:+.2%}")
        print(f"  Sharpe ratio: {performance.sharpe_ratio:.2f}")
        print(f"  Win rate: {performance.win_rate:.1%}")
        print(f"  Max drawdown: {performance.max_drawdown:.2%}")
        print(f"  Profit factor: {performance.profit_factor:.2f}")

def main():
    """Asosiy demo funksiyasi"""
    print("🚀 BOZOR REJIMINI ANIQLASH VA STRATEGIYA ALMASHTIRISH TIZIMI")
    print("=" * 80)
    
    try:
        # 1. Rejim aniqlash
        regime_history, detector = demonstrate_regime_detection()
        
        # 2. Strategiya almashtirish
        strategy_history, switcher = demonstrate_strategy_switching()
        
        # 3. Risk boshqaruv
        demonstrate_risk_management()
        
        # 4. Portfolio boshqaruv
        demonstrate_portfolio_management()
        
        # 5. Kengaytirilgan xususiyatlar
        demonstrate_advanced_features()
        
        print("\n" + "="*80)
        print("✅ DEMO MUVAFFAQIYATLI YAKUNLANDI")
        print("="*80)
        
        # Export final report
        report = switcher.export_performance_report()
        print(f"\nYakuniy hisobot:")
        print(f"Joriy rejim: {report['current_regime']}")
        print(f"Aktiv strategiya: {report['active_strategy']}")
        print(f"Ochiq pozitsiyalar: {report['position_summary']}")
        
    except Exception as e:
        logger.error(f"Demo jarayonida xatolik: {e}")
        print(f"❌ Xatolik: {e}")

if __name__ == "__main__":
    main()