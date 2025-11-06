"""
Multi-Asset Trading Signal Generator - Usage Examples
"""

import time
import json
from datetime import datetime
from trading_signal_generator import TradingSignalGenerator, SignalType
import config

def example_1_basic_signal_generation():
    """Example 1: Basic signal generation for a single asset"""
    print("=== Example 1: Basic Signal Generation ===")
    
    # Initialize the generator
    generator = TradingSignalGenerator()
    
    # Get current signal for Apple
    signal = generator.generate_signal("AAPL", timeframe="1h", account_balance=15000)
    
    if signal:
        print(f"Symbol: {signal.symbol}")
        print(f"Signal: {signal.signal_type.value}")
        print(f"Confidence: {signal.confidence:.2f}")
        print(f"Current Price: ${signal.current_price:.2f}")
        print(f"Entry Price: ${signal.entry_price:.2f}")
        print(f"Stop Loss: ${signal.stop_loss:.2f}")
        print(f"Take Profit: ${signal.take_profit:.2f}")
        print(f"Position Size: ${signal.position_size:.2f}")
        print(f"Reasoning: {signal.reasoning}")
    else:
        print("Failed to generate signal")
    
    print()

def example_2_multi_timeframe_analysis():
    """Example 2: Multi-timeframe signal analysis"""
    print("=== Example 2: Multi-Timeframe Analysis ===")
    
    generator = TradingSignalGenerator()
    
    # Get multi-timeframe signal for Tesla
    signal = generator.generate_multi_timeframe_signal("TSLA", account_balance=20000)
    
    if signal:
        print(f"Symbol: {signal.symbol}")
        print(f"Ensemble Signal: {signal.signal_type.value}")
        print(f"Timeframe: {signal.timeframe}")
        print(f"Confidence: {signal.confidence:.2f}")
        print(f"Entry Price: ${signal.entry_price:.2f}")
        print(f"Stop Loss: ${signal.stop_loss:.2f}")
        print(f"Take Profit: ${signal.take_profit:.2f}")
        print(f"Position Size: ${signal.position_size:.2f}")
    else:
        print("Failed to generate multi-timeframe signal")
    
    print()

def example_3_batch_signal_generation():
    """Example 3: Generate signals for multiple assets"""
    print("=== Example 3: Batch Signal Generation ===")
    
    generator = TradingSignalGenerator()
    
    # Generate signals for all supported assets
    signals = generator.generate_signals_for_all(account_balance=25000)
    
    # Display summary
    print(f"Generated signals for {len(signals)} assets:")
    print()
    
    for symbol, signal in signals.items():
        if signal:
            print(f"{symbol:8} | {signal.signal_type.value:10} | "
                  f"Conf: {signal.confidence:.2f} | "
                  f"Price: ${signal.current_price:8.2f}")
    
    # Export signals to file
    export_file = generator.export_signals(signals, "batch_signals.json")
    print(f"\nSignals exported to: {export_file}")
    
    print()

def example_4_real_time_monitoring():
    """Example 4: Real-time signal monitoring"""
    print("=== Example 4: Real-Time Signal Monitoring ===")
    
    generator = TradingSignalGenerator()
    
    # Start real-time generation for selected symbols
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "EURUSD=X", "GC=F"]
    generator.start_real_time_generation(symbols=symbols, interval=30, account_balance=30000)
    
    print("Started real-time monitoring for symbols:", symbols)
    print("Press Ctrl+C to stop monitoring...")
    
    try:
        signal_count = 0
        while signal_count < 10:  # Monitor for 10 signals
            try:
                # Get signal from queue (wait up to 5 seconds)
                signal_data = generator.signals_queue.get(timeout=5)
                signal = signal_data['signal']
                timestamp = signal_data['timestamp']
                
                print(f"[{timestamp.strftime('%H:%M:%S')}] {signal.symbol}: "
                      f"{signal.signal_type.value} (Conf: {signal.confidence:.2f})")
                
                signal_count += 1
                
            except Exception as e:
                print(f"Queue timeout or error: {e}")
                break
                
    except KeyboardInterrupt:
        print("\nStopping real-time monitoring...")
    finally:
        generator.stop_real_time_generation()
    
    print("Real-time monitoring stopped.")
    print()

def example_5_data_quality_validation():
    """Example 5: Data quality validation"""
    print("=== Example 5: Data Quality Validation ===")
    
    generator = TradingSignalGenerator()
    
    # Test data quality for various assets
    test_symbols = ["AAPL", "GOOGL", "EURUSD=X", "GC=F"]
    
    for symbol in test_symbols:
        quality = generator.validate_data_quality(symbol, timeframe="1h")
        print(f"{symbol:10} | Quality Score: {quality['quality_score']:3}/100")
        
        if quality['issues']:
            for issue in quality['issues']:
                print(f"           | Issue: {issue}")
        else:
            print(f"           | No issues found")
        
        print()
    
    print()

def example_6_custom_account_management():
    """Example 6: Custom account management and risk calculation"""
    print("=== Example 6: Custom Account Management ===")
    
    generator = TradingSignalGenerator()
    
    # Different account sizes
    account_sizes = [5000, 10000, 50000, 100000]
    
    for balance in account_sizes:
        signal = generator.generate_signal("NVDA", timeframe="4h", account_balance=balance)
        
        if signal:
            risk_percent = signal.position_size / balance * 100
            
            print(f"Account Balance: ${balance:,}")
            print(f"Position Size: ${signal.position_size:.2f} ({risk_percent:.1f}%)")
            print(f"Risk Amount: ${balance * config.DEFAULT_RISK_PERCENT:.2f}")
            print(f"Risk-Reward Ratio: {(signal.take_profit - signal.entry_price) / (signal.entry_price - signal.stop_loss):.2f}")
            print()
    
    print()

def example_7_technical_indicator_analysis():
    """Example 7: Deep technical indicator analysis"""
    print("=== Example 7: Technical Indicator Analysis ===")
    
    generator = TradingSignalGenerator()
    
    # Get signal with detailed indicators
    signal = generator.generate_signal("MSFT", timeframe="1h", account_balance=15000)
    
    if signal:
        print(f"Symbol: {signal.symbol}")
        print(f"Current Price: ${signal.current_price:.2f}")
        print(f"Signal: {signal.signal_type.value} (Confidence: {signal.confidence:.2f})")
        print()
        
        print("Technical Indicators:")
        print("-" * 40)
        for indicator, value in signal.indicators.items():
            print(f"{indicator:15}: {value:8.4f}")
        
        print()
        print(f"Reasoning: {signal.reasoning}")
    else:
        print("Failed to generate signal")
    
    print()

def run_all_examples():
    """Run all examples"""
    print("Multi-Asset Trading Signal Generator - Examples")
    print("=" * 60)
    print()
    
    try:
        example_1_basic_signal_generation()
        time.sleep(2)
        
        example_2_multi_timeframe_analysis()
        time.sleep(2)
        
        example_3_batch_signal_generation()
        time.sleep(2)
        
        example_4_real_time_monitoring()
        time.sleep(2)
        
        example_5_data_quality_validation()
        time.sleep(2)
        
        example_6_custom_account_management()
        time.sleep(2)
        
        example_7_technical_indicator_analysis()
        
    except Exception as e:
        print(f"Error running examples: {e}")
    
    print("All examples completed!")

if __name__ == "__main__":
    # Run a specific example
    print("Select example to run:")
    print("1. Basic Signal Generation")
    print("2. Multi-Timeframe Analysis")
    print("3. Batch Signal Generation")
    print("4. Real-Time Monitoring")
    print("5. Data Quality Validation")
    print("6. Custom Account Management")
    print("7. Technical Indicator Analysis")
    print("8. Run All Examples")
    print()
    
    choice = input("Enter your choice (1-8): ").strip()
    
    if choice == "1":
        example_1_basic_signal_generation()
    elif choice == "2":
        example_2_multi_timeframe_analysis()
    elif choice == "3":
        example_3_batch_signal_generation()
    elif choice == "4":
        example_4_real_time_monitoring()
    elif choice == "5":
        example_5_data_quality_validation()
    elif choice == "6":
        example_6_custom_account_management()
    elif choice == "7":
        example_7_technical_indicator_analysis()
    elif choice == "8":
        run_all_examples()
    else:
        print("Invalid choice. Running basic example.")
        example_1_basic_signal_generation()