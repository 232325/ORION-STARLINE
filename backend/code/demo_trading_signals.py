#!/usr/bin/env python3
"""
Trading Signal Generator - Working Demo
"""

from trading_signal_generator import TradingSignalGenerator, TechnicalIndicators, DataProvider
import json
from datetime import datetime

def demo_trading_signals():
    """Working demo of the trading signal generator"""
    print("🚀 Multi-Asset Trading Signal Generator Demo")
    print("=" * 60)
    
    # Initialize components
    generator = TradingSignalGenerator()
    print("✓ Signal generator initialized")
    
    # Supported assets
    assets = generator.get_supported_assets()
    print(f"\n📊 Supported Assets ({len(assets)}):")
    
    # Group by type
    stocks = [s for s, t in assets.items() if t.value == "STOCK"]
    forex = [s for s, t in assets.items() if t.value == "FOREX"]
    metals = [s for s, t in assets.items() if t.value == "METAL"]
    
    print(f"  Stocks: {', '.join(stocks)}")
    print(f"  Forex: {', '.join(forex)}")
    print(f"  Metals: {', '.join(metals)}")
    
    # Test data fetching
    print(f"\n📈 Testing Data Fetching...")
    test_symbols = ["AAPL", "EURUSD=X", "GC=F"]
    
    for symbol in test_symbols:
        print(f"\n  {symbol}:")
        try:
            # Get more data for indicators
            data = DataProvider.get_data(symbol, period="60d", interval="1d")  # Daily data
            if not data.empty:
                print(f"    ✓ Got {len(data)} data points")
                print(f"    ✓ Latest price: ${data['close'].iloc[-1]:.2f}")
                
                # Calculate indicators
                indicators = generator.signal_generator.calculate_indicators(data)
                if indicators:
                    rsi = indicators.get('rsi', 0)
                    sma20 = indicators.get('sma_20', 0)
                    current_price = data['close'].iloc[-1]
                    
                    print(f"    ✓ RSI: {rsi:.1f}")
                    print(f"    ✓ SMA20: ${sma20:.2f}")
                    print(f"    ✓ Price vs SMA20: {((current_price - sma20) / sma20 * 100):+.1f}%")
                    
                    # Simple signal based on indicators
                    if rsi < 30 and current_price < sma20:
                        signal_type = "STRONG_BUY"
                    elif rsi < 50 and current_price > sma20:
                        signal_type = "BUY"
                    elif rsi > 70:
                        signal_type = "SELL"
                    else:
                        signal_type = "HOLD"
                    
                    print(f"    ✓ Signal: {signal_type}")
                else:
                    print(f"    ✗ Could not calculate indicators")
            else:
                print(f"    ✗ No data available")
                
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    # Generate signals for all assets
    print(f"\n🎯 Generating Signals for All Assets...")
    all_signals = {}
    
    for symbol in list(assets.keys())[:5]:  # Test first 5 assets
        try:
            # Use daily data for more reliable signals
            data = DataProvider.get_data(symbol, period="60d", interval="1d")
            if len(data) >= 50:  # Minimum for indicators
                indicators = generator.signal_generator.calculate_indicators(data)
                
                if indicators:
                    # Calculate signal strength
                    strength = generator.signal_generator.calculate_signal_strength(indicators)
                    signal_type = generator.signal_generator.determine_signal_type(strength)
                    
                    current_price = data['close'].iloc[-1]
                    atr = indicators.get('atr', 0.02 * current_price)
                    
                    # Calculate trading levels
                    if signal_type.value in ['STRONG_BUY', 'BUY']:
                        entry_price = current_price
                        stop_loss = entry_price - (atr * 2)
                        take_profit = entry_price + (atr * 3)
                    elif signal_type.value in ['STRONG_SELL', 'SELL']:
                        entry_price = current_price
                        stop_loss = entry_price + (atr * 2)
                        take_profit = entry_price - (atr * 3)
                    else:
                        entry_price = current_price
                        stop_loss = current_price * 0.95
                        take_profit = current_price * 1.05
                    
                    # Calculate position size
                    position_size = generator.signal_generator.calculate_position_size(
                        signal_type, strength, 10000
                    )
                    
                    # Store signal
                    signal_data = {
                        'symbol': symbol,
                        'signal_type': signal_type.value,
                        'confidence': strength,
                        'current_price': current_price,
                        'entry_price': entry_price,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'position_size': position_size,
                        'rsi': indicators.get('rsi', 0),
                        'sma20': indicators.get('sma_20', 0),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    all_signals[symbol] = signal_data
                    
                    print(f"  {symbol:8} | {signal_type.value:10} | "
                          f"Conf: {strength:.2f} | "
                          f"Price: ${current_price:8.2f}")
                else:
                    print(f"  {symbol:8} | NO INDICATORS")
            else:
                print(f"  {symbol:8} | INSUFFICIENT DATA")
                
        except Exception as e:
            print(f"  {symbol:8} | ERROR: {e}")
    
    # Export results
    if all_signals:
        export_file = f"/workspace/code/demo_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(export_file, 'w') as f:
            json.dump(all_signals, f, indent=2)
        print(f"\n💾 Signals exported to: {export_file}")
        
        # Show summary
        print(f"\n📊 Signal Summary:")
        signal_counts = {}
        for signal in all_signals.values():
            signal_type = signal['signal_type']
            signal_counts[signal_type] = signal_counts.get(signal_type, 0) + 1
        
        for signal_type, count in signal_counts.items():
            print(f"  {signal_type}: {count} assets")
    
    print(f"\n✅ Demo completed successfully!")
    
    return all_signals

if __name__ == "__main__":
    demo_trading_signals()