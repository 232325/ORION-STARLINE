#!/usr/bin/env python3
"""
Trading Signal Generator Test Script - Debug Version
"""

from trading_signal_generator import TradingSignalGenerator
import sys
import traceback

def test_basic_functionality():
    """Test basic functionality with detailed debugging"""
    print("=== Multi-Asset Trading Signal Generator Test ===")
    
    try:
        # Generator yaratish
        generator = TradingSignalGenerator()
        print("✓ Signal generator yaratildi")
        
        # Aktivlar ro'yxati
        assets = generator.get_supported_assets()
        print(f"✓ {len(assets)} ta aktiv qo'llab-quvvatlanadi:")
        for symbol, asset_type in list(assets.items())[:5]:
            print(f"  - {symbol}: {asset_type.value}")
        if len(assets) > 5:
            print(f"  ... va yana {len(assets) - 5} ta")
        
        # Test data fetching first
        print("\nData fetching test...")
        from trading_signal_generator import DataProvider
        
        test_symbol = "AAPL"
        data = DataProvider.get_data(test_symbol, period="30d", interval="1h")
        if not data.empty:
            print(f"✓ {test_symbol} uchun {len(data)} ta data point olindi")
            print(f"  Date range: {data.index[0]} to {data.index[-1]}")
            print(f"  Columns: {list(data.columns)}")
        else:
            print(f"✗ {test_symbol} uchun data olinmadi")
            return False
        
        # Test current price
        current_price = DataProvider.get_current_price(test_symbol)
        if current_price > 0:
            print(f"✓ Current price: ${current_price:.2f}")
        else:
            print("✗ Current price olinmadi")
            return False
        
        # Test indicator calculation
        print("\nIndicator calculation test...")
        if len(data) >= 50:  # Minimum data for indicators
            indicators = generator.signal_generator.calculate_indicators(data)
            if indicators:
                print(f"✓ {len(indicators)} ta indikator hisoblandi:")
                for key, value in list(indicators.items())[:5]:
                    print(f"  {key}: {value:.4f}")
            else:
                print("✗ Indikatorlar hisoblanmadi")
                return False
        else:
            print(f"✗ Yetarli ma'lumot yo'q ({len(data)} ta point, minimum 50 ta kerak)")
            return False
        
        # Test signal generation
        print("\nSignal generatsiyasi test...")
        signal = generator.generate_signal(test_symbol, timeframe="1h", account_balance=10000)
        
        if signal:
            print(f"✓ Signal yaratildi: {signal.signal_type.value}")
            print(f"  Current Price: ${signal.current_price:.2f}")
            print(f"  Confidence: {signal.confidence:.2f}")
            print(f"  Entry Price: ${signal.entry_price:.2f}")
            print(f"  Stop Loss: ${signal.stop_loss:.2f}")
            print(f"  Take Profit: ${signal.take_profit:.2f}")
            print(f"  Position Size: ${signal.position_size:.2f}")
            print(f"  Reasoning: {signal.reasoning[:100]}...")
            
            # Show some indicators
            print(f"  RSI: {signal.indicators.get('rsi', 'N/A')}")
            print(f"  MACD: {signal.indicators.get('macd', 'N/A')}")
            print(f"  SMA20: {signal.indicators.get('sma_20', 'N/A')}")
        else:
            print("✗ Signal yaratilmadi")
            return False
        
        # Ma'lumotlar sifati
        print("\nMa'lumotlar sifati tekshirish...")
        quality = generator.validate_data_quality(test_symbol)
        print(f"✓ Quality Score: {quality['quality_score']}/100")
        if quality['issues']:
            print("  Issues:")
            for issue in quality['issues']:
                print(f"    - {issue}")
        else:
            print("  No issues found")
        
        # Test with different assets
        print("\nBoshqa aktivlar test...")
        test_assets = ["GOOGL", "EURUSD=X", "GC=F"]
        for asset in test_assets[:2]:  # Test first 2
            try:
                signal = generator.generate_signal(asset, timeframe="1h", account_balance=10000)
                if signal:
                    print(f"✓ {asset}: {signal.signal_type.value} (${signal.current_price:.2f})")
                else:
                    print(f"- {asset}: Signal yaratilmadi")
            except Exception as e:
                print(f"✗ {asset}: Xato - {e}")
        
        print("\n=== Test muvaffaqiyatli tugallandi ===")
        return True
        
    except Exception as e:
        print(f"✗ Xato: {e}")
        print("\nDetailed traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    print(f"\nTest result: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)