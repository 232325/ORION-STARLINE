"""
Demo Script: Hybrid Quantum Forex System
Namuna skript tizimni ishlatish
"""
import asyncio
import sys
from pathlib import Path

# Add path for imports
sys.path.append(str(Path(__file__).parent))

async def quick_demo():
    """Quick system demonstration"""
    print("🚀 Hybrid Quantum Forex System - Quick Demo")
    print("=" * 50)
    
    try:
        # 1. Import system components
        print("📦 Importing system components...")
        from core.orchestrator import initialize_system, start_system, stop_system, get_system_status
        from classical.preprocessing import ClassicalPreprocessor
        from quantum.core_processor import QuantumProcessor
        from arbitrage.detector import ArbitrageDetector
        from utils.data_models import MarketData, ArbitrageOpportunity, ArbitrageType
        from config.config import config
        
        print("✅ Components imported successfully")
        
        # 2. Initialize system
        print("\n🔧 Initializing system...")
        success = initialize_system()
        if not success:
            print("❌ System initialization failed")
            return False
        
        print("✅ System initialized")
        
        # 3. Start system
        print("\n▶️  Starting system...")
        success = start_system()
        if not success:
            print("❌ System startup failed")
            return False
        
        print("✅ System started")
        
        # 4. Show initial status
        print("\n📊 System Status:")
        status = get_system_status()
        print(f"   State: {status.get('state', 'Unknown')}")
        print(f"   Running: {status.get('running', False)}")
        
        # 5. Demonstrate market data processing
        print("\n📈 Processing market data...")
        
        # Create sample market data
        market_data = MarketData()
        market_data.add_price("EURUSD", 1.1000, 1.1002, "demo_feed")
        market_data.add_price("GBPUSD", 1.2500, 1.2502, "demo_feed")  
        market_data.add_price("USDJPY", 110.00, 110.02, "demo_feed")
        market_data.add_price("EURJPY", 121.00, 121.02, "demo_feed")
        
        market_data.volatility = {
            "EURUSD": 0.01,
            "GBPUSD": 0.012,
            "USDJPY": 0.008,
            "EURJPY": 0.009
        }
        
        market_data.volume = {
            "EURUSD": 1000000,
            "GBPUSD": 800000,
            "USDJPY": 900000,
            "EURJPY": 600000
        }
        
        print(f"   Processed {len(market_data.prices)} currency pairs")
        
        # 6. Demonstrate quantum processing
        print("\n⚛️  Running quantum processing...")
        quantum_processor = QuantumProcessor(config.quantum_config)
        quantum_features = quantum_processor.process_market_data(market_data)
        
        if quantum_features:
            print(f"   Correlation Entanglement: {quantum_features.correlation_entanglement:.3f}")
            print(f"   Volatility Superposition: {quantum_features.volatility_superposition:.3f}")
            print(f"   Momentum Entanglement: {quantum_features.momentum_entanglement:.3f}")
            print(f"   Quantum Fidelity: {quantum_features.error_rate:.3f}")
        
        # 7. Demonstrate arbitrage detection
        print("\n💱 Detecting arbitrage opportunities...")
        detector = ArbitrageDetector(config.arbitrage_config)
        opportunities = detector.detect_opportunities(market_data, {
            'correlation_analysis': {'entanglement_strength': quantum_features.correlation_entanglement},
            'volatility_analysis': {'superposition_coherence': quantum_features.volatility_superposition},
            'momentum_analysis': {'entanglement_strength': quantum_features.momentum_entanglement}
        })
        
        print(f"   Detected {len(opportunities)} opportunities")
        
        for i, opp in enumerate(opportunities[:3]):  # Show first 3
            print(f"   Opportunity {i+1}:")
            print(f"     Type: {opp.arbitrage_type.value}")
            print(f"     Profit Potential: {opp.calculations.profit_potential:.3f}%" if opp.calculations else "N/A")
            print(f"     Risk Level: {opp.risk_level:.3f}")
            print(f"     Pairs: {', '.join(opp.pairs)}")
        
        # 8. Show system metrics after demo
        print("\n📊 Final System Status:")
        final_status = get_system_status()
        if 'metrics' in final_status:
            metrics = final_status['metrics']
            print(f"   Uptime: {metrics.get('uptime', 0):.1f} seconds")
            print(f"   Total Opportunities: {metrics.get('total_opportunities', 0)}")
            print(f"   Executed Trades: {metrics.get('executed_trades', 0)}")
            print(f"   Total Profit: ${metrics.get('total_profit', 0):.2f}")
            print(f"   Average Latency: {metrics.get('average_latency', 0):.3f}ms")
        
        # 9. Stop system
        print("\n⏹️  Stopping system...")
        stop_system()
        print("✅ System stopped")
        
        print("\n🎉 Demo completed successfully!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_system_info():
    """Show system information"""
    print("ℹ️  System Information:")
    print("=" * 30)
    
    try:
        from config.config import config
        print(f"Quantum Backend: {config.quantum_config.backend_name}")
        print(f"Update Interval: {config.forex_config.update_interval}s")
        print(f"Min Profit Threshold: {config.arbitrage_config.min_profit_threshold:.3f}%")
        print(f"Max Position Size: ${config.arbitrage_config.max_position_size:,}")
        print(f"Supported Currencies: {len(config.forex_config.supported_currencies)}")
        print(f"Database Path: {config.db_path}")
        
    except Exception as e:
        print(f"Error loading configuration: {e}")

def show_features():
    """Show system features"""
    print("🌟 System Features:")
    print("=" * 30)
    
    features = [
        "⚛️  Quantum Correlation Analysis",
        "📊 Real-time Market Data Processing", 
        "💱 Triangular Arbitrage Detection",
        "🌍 Cross-currency Arbitrage",
        "⏰ Time-zone Based Trading",
        "📈 Volatility Quantum Modeling",
        "🔍 High-frequency Opportunity Detection",
        "🛡️  Advanced Risk Management",
        "📊 Performance Monitoring",
        "🔧 Error Recovery System",
        "💾 Comprehensive Audit Trails",
        "🚀 Low-latency Execution"
    ]
    
    for feature in features:
        print(f"   {feature}")

def interactive_demo():
    """Interactive demo mode"""
    print("\n🎮 Interactive Demo Mode")
    print("=" * 30)
    print("Commands:")
    print("  demo    - Run full demo")
    print("  info    - Show system info")  
    print("  features - Show features")
    print("  quit    - Exit")
    print("-" * 30)
    
    while True:
        try:
            command = input("\n> ").strip().lower()
            
            if command == 'quit':
                break
            elif command == 'demo':
                asyncio.run(quick_demo())
            elif command == 'info':
                show_system_info()
            elif command == 'features':
                show_features()
            else:
                print("Unknown command. Type 'quit' to exit.")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

async def main():
    """Main demo function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hybrid Quantum Forex Demo')
    parser.add_argument('--mode', choices=['auto', 'interactive', 'info', 'features'], 
                       default='auto', help='Demo mode')
    parser.add_argument('--quick', action='store_true', help='Run quick demo')
    
    args = parser.parse_args()
    
    if args.mode == 'info':
        show_system_info()
    elif args.mode == 'features':
        show_features()
    elif args.mode == 'interactive':
        interactive_demo()
    else:  # auto mode
        print("🔬 Hybrid Quantum-Classical Forex Arbitrage System")
        print("⚡ High-Performance Quantum-Enhanced Trading")
        print("")
        
        if args.quick:
            success = await quick_demo()
        else:
            print("Choose demo mode:")
            print("1. Full Demo (recommended)")
            print("2. Interactive Mode")  
            print("3. System Information")
            print("4. Features Overview")
            
            try:
                choice = input("\nSelect option (1-4): ").strip()
                
                if choice == '1':
                    success = await quick_demo()
                elif choice == '2':
                    interactive_demo()
                    success = True
                elif choice == '3':
                    show_system_info()
                    success = True
                elif choice == '4':
                    show_features()
                    success = True
                else:
                    print("Running default demo...")
                    success = await quick_demo()
                    
            except KeyboardInterrupt:
                print("\nDemo cancelled by user")
                return
        
        if success:
            print("\n✅ Demo completed successfully!")
            print("📚 For more information, see README.md")
        else:
            print("\n❌ Demo failed. Check logs for details.")

if __name__ == "__main__":
    asyncio.run(main())