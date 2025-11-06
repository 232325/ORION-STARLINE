#!/usr/bin/env python3
"""
Trading Signal Generator Test Script
"""

from trading_signal_generator import TradingSignalGenerator
import sys

def test_basic_functionality():
    """Test basic functionality"""
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
        
        # Test signal
        print("\nAAPL uchun signal generatsiyasi...")
        signal = generator.generate_signal("AAPL", timeframe="1h", account_balance=10000)
        
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
        quality = generator.validate_data_quality("AAPL")
        print(f"✓ Quality Score: {quality['quality_score']}/100")
        if quality['issues']:
            print("  Issues:")
            for issue in quality['issues']:
                print(f"    - {issue}")
        else:
            print("  No issues found")
        
        # Test multiple timeframes
        print("\nMulti-timeframe test...")
        mtf_signal = generator.generate_multi_timeframe_signal("GOOGL")
        if mtf_signal:
            print(f"✓ Multi-timeframe signal: {mtf_signal.signal_type.value}")
            print(f"  Timeframe: {mtf_signal.timeframe}")
            print(f"  Confidence: {mtf_signal.confidence:.2f}")
        else:
            print("✗ Multi-timeframe signal yaratilmadi")
        
        print("\n=== Test muvaffaqiyatli tugallandi ===")
        return True
        
    except Exception as e:
        print(f"✗ Xato: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)