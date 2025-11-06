"""
Example Script: System Testing
Test skriptlari
"""
import asyncio
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.orchestrator import HybridQuantumForexSystem, initialize_system
from classical.preprocessing import ClassicalPreprocessor
from quantum.core_processor import QuantumProcessor
from arbitrage.detector import ArbitrageDetector
from arbitrage.executor import ArbitrageExecutor
from utils.data_models import MarketData, MarketPrice, CurrencyPair
from config.config import config

class SystemTester:
    """System test class"""
    
    def __init__(self):
        self.test_results = {}
        self.errors = []
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        self.test_results[test_name] = {
            'success': success,
            'message': message,
            'timestamp': datetime.now(timezone.utc)
        }
        
        status = "PASS" if success else "FAIL"
        print(f"[{status}] {test_name}: {message}")
    
    async def test_system_initialization(self):
        """Test system initialization"""
        try:
            # Test configuration
            assert config is not None, "Configuration not loaded"
            self.log_test("config_load", True, "Configuration loaded successfully")
            
            # Test database setup
            from utils.database import setup_database
            db_success = setup_database()
            self.log_test("database_setup", db_success, "Database setup completed")
            
            # Test system initialization
            init_success = initialize_system()
            self.log_test("system_init", init_success, "System initialization completed")
            
            return db_success and init_success
            
        except Exception as e:
            self.log_test("system_init", False, f"Initialization failed: {e}")
            return False
    
    async def test_classical_preprocessing(self):
        """Test classical preprocessing"""
        try:
            preprocessor = ClassicalPreprocessor(config.forex_config)
            
            # Test connection
            conn_success = preprocessor.test_connection()
            self.log_test("preprocessor_connection", conn_success, "Preprocessor connection test")
            
            # Test market data retrieval
            market_data = await preprocessor.get_latest_data()
            data_success = market_data is not None and len(market_data.prices) > 0
            self.log_test("market_data_retrieval", data_success, f"Retrieved {len(market_data.prices) if market_data else 0} prices")
            
            # Test data processing
            if market_data:
                processed_data = preprocessor.process_data(market_data)
                processing_success = processed_data is not None
                self.log_test("data_processing", processing_success, "Data processing completed")
            
            return conn_success and data_success
            
        except Exception as e:
            self.log_test("classical_preprocessing", False, f"Preprocessing test failed: {e}")
            return False
    
    async def test_quantum_processing(self):
        """Test quantum processing"""
        try:
            quantum_processor = QuantumProcessor(config.quantum_config)
            
            # Test quantum backend
            backend_success = quantum_processor.test_connection()
            self.log_test("quantum_backend", backend_success, "Quantum backend test")
            
            # Create test market data
            test_market_data = MarketData()
            test_market_data.add_price("EURUSD", 1.1000, 1.1002, "test")
            test_market_data.add_price("GBPUSD", 1.2500, 1.2502, "test")
            test_market_data.volatility = {"EURUSD": 0.01, "GBPUSD": 0.012}
            
            # Test quantum processing
            quantum_features = quantum_processor.process_market_data(test_market_data)
            quantum_success = quantum_features is not None
            self.log_test("quantum_processing", quantum_success, "Quantum processing completed")
            
            if quantum_success:
                self.log_test("quantum_correlation", 
                            quantum_features.correlation_entanglement >= 0,
                            f"Correlation entanglement: {quantum_features.correlation_entanglement:.3f}")
                self.log_test("quantum_volatility",
                            quantum_features.volatility_superposition >= 0,
                            f"Volatility superposition: {quantum_features.volatility_superposition:.3f}")
            
            return backend_success and quantum_success
            
        except Exception as e:
            self.log_test("quantum_processing", False, f"Quantum processing test failed: {e}")
            return False
    
    async def test_arbitrage_detection(self):
        """Test arbitrage detection"""
        try:
            detector = ArbitrageDetector(config.arbitrage_config)
            
            # Create test market data
            test_market_data = MarketData()
            test_market_data.add_price("EURUSD", 1.1000, 1.1002, "test")
            test_market_data.add_price("USDJPY", 110.00, 110.02, "test")
            test_market_data.add_price("EURJPY", 121.00, 121.02, "test")
            test_market_data.volatility = {"EURUSD": 0.01, "USDJPY": 0.008, "EURJPY": 0.009}
            test_market_data.volume = {"EURUSD": 1000000, "USDJPY": 800000, "EURJPY": 600000}
            
            # Test opportunity detection
            opportunities = detector.detect_opportunities(test_market_data)
            detection_success = len(opportunities) > 0
            self.log_test("arbitrage_detection", detection_success, f"Detected {len(opportunities)} opportunities")
            
            # Test opportunity validation
            if opportunities:
                valid_opportunities = [op for op in opportunities if op.is_valid]
                self.log_test("opportunity_validation", 
                            len(valid_opportunities) > 0,
                            f"Valid opportunities: {len(valid_opportunities)}")
            
            return detection_success
            
        except Exception as e:
            self.log_test("arbitrage_detection", False, f"Arbitrage detection test failed: {e}")
            return False
    
    async def test_arbitrage_execution(self):
        """Test arbitrage execution"""
        try:
            executor = ArbitrageExecutor(config.arbitrage_config)
            
            # Create test opportunity
            from utils.data_models import ArbitrageOpportunity, ArbitrageType, ArbitrageCalculation
            test_opportunity = ArbitrageOpportunity(
                arbitrage_type=ArbitrageType.TRIANGULAR,
                currencies=['EUR', 'USD', 'JPY'],
                pairs=['EURUSD', 'USDJPY', 'EURJPY'],
                calculations=ArbitrageCalculation(
                    direct_rate=121.00,
                    cross_rate=121.02,
                    arbitrage_spread=0.02,
                    profit_potential=0.016,
                    risk_score=0.3,
                    time_sensitivity=0.8,
                    market_depth=500000
                ),
                risk_level=0.3,
                execution_time_estimate=0.5
            )
            
            # Test execution
            execution_result = await executor.execute_arbitrage(test_opportunity)
            execution_success = execution_result is not None
            self.log_test("arbitrage_execution", execution_success, "Execution completed")
            
            if execution_success:
                self.log_test("execution_result", 
                            hasattr(execution_result, 'success'),
                            f"Execution success: {execution_result.success}")
                self.log_test("execution_profit",
                            hasattr(execution_result, 'net_profit'),
                            f"Net profit: {execution_result.net_profit:.4f}")
            
            return execution_success
            
        except Exception as e:
            self.log_test("arbitrage_execution", False, f"Arbitrage execution test failed: {e}")
            return False
    
    async def test_integration(self):
        """Test full system integration"""
        try:
            # Initialize system
            system = HybridQuantumForexSystem()
            init_success = system.initialize()
            self.log_test("integration_init", init_success, "System initialization for integration test")
            
            if init_success:
                # Start system briefly
                start_success = system.start()
                self.log_test("integration_start", start_success, "System started for integration test")
                
                if start_success:
                    # Let it run for a short time
                    await asyncio.sleep(5)
                    
                    # Get status
                    status = system.get_status()
                    status_success = status is not None
                    self.log_test("integration_status", status_success, "System status retrieved")
                    
                    # Stop system
                    stop_success = system.stop()
                    self.log_test("integration_stop", stop_success, "System stopped")
                    
                    return status_success and stop_success
            
            return False
            
        except Exception as e:
            self.log_test("integration", False, f"Integration test failed: {e}")
            return False
    
    def generate_test_report(self):
        """Generate test report"""
        try:
            total_tests = len(self.test_results)
            passed_tests = sum(1 for result in self.test_results.values() if result['success'])
            failed_tests = total_tests - passed_tests
            
            report = f"""
========================================
HYBRID QUANTUM FOREX SYSTEM TEST REPORT
========================================
Test Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY:
- Total Tests: {total_tests}
- Passed: {passed_tests}
- Failed: {failed_tests}
- Success Rate: {(passed_tests/total_tests)*100:.1f}%

DETAILED RESULTS:
"""
            
            for test_name, result in self.test_results.items():
                status = "PASS" if result['success'] else "FAIL"
                timestamp = result['timestamp'].strftime('%H:%M:%S')
                report += f"[{timestamp}] {status} - {test_name}: {result['message']}\n"
            
            report += "\n"
            
            if failed_tests > 0:
                report += "FAILED TESTS:\n"
                for test_name, result in self.test_results.items():
                    if not result['success']:
                        report += f"- {test_name}: {result['message']}\n"
            
            report += "\n" + "="*40 + "\n"
            
            # Save report
            with open('test_report.txt', 'w') as f:
                f.write(report)
            
            print(report)
            print("Test report saved to test_report.txt")
            
            return passed_tests == total_tests
            
        except Exception as e:
            print(f"Failed to generate test report: {e}")
            return False

async def run_all_tests():
    """Run all system tests"""
    print("Starting Hybrid Quantum Forex System Tests...")
    print("=" * 50)
    
    tester = SystemTester()
    
    # Run individual component tests
    print("\n1. Testing System Initialization...")
    await tester.test_system_initialization()
    
    print("\n2. Testing Classical Preprocessing...")
    await tester.test_classical_preprocessing()
    
    print("\n3. Testing Quantum Processing...")
    await tester.test_quantum_processing()
    
    print("\n4. Testing Arbitrage Detection...")
    await tester.test_arbitrage_detection()
    
    print("\n5. Testing Arbitrage Execution...")
    await tester.test_arbitrage_execution()
    
    print("\n6. Testing Full Integration...")
    await tester.test_integration()
    
    # Generate report
    print("\n" + "="*50)
    success = tester.generate_test_report()
    
    if success:
        print("\nAll tests passed! System is ready for deployment.")
    else:
        print("\nSome tests failed. Please review the results.")
    
    return success

if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)