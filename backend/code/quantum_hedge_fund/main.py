#!/usr/bin/env python3
"""
Quantum AI Hedge Fund Platform - Main Entry Point
Comprehensive quantum-powered hedge fund management system
"""

import asyncio
import sys
import argparse
import logging
import signal
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.orchestrator import QuantumHedgeFundOrchestrator

def setup_signal_handlers(orchestrator):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logging.info(f"Signal {signum} received, shutting down gracefully...")
        asyncio.create_task(orchestrator.shutdown())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def validate_config(config_path):
    """Validate configuration file"""
    try:
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Basic validation
        required_sections = ['system', 'quantum', 'trading', 'risk', 'compliance']
        for section in required_sections:
            if section not in config:
                logging.warning(f"Configuration section '{section}' missing")
        
        return True
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        return False
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in configuration file: {e}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Quantum AI Hedge Fund Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Start with default config
  python main.py --config prod_config.json         # Use custom config
  python main.py --no-quantum                      # Disable quantum features
  python main.py --status                          # Check system status
  python main.py --test                            # Run system tests
        """
    )
    
    parser.add_argument(
        '--config', 
        default='config/config.json',
        help='Configuration file path (default: config/config.json)'
    )
    
    parser.add_argument(
        '--no-quantum',
        action='store_true',
        help='Disable quantum computing features'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Check system status and exit'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run system tests and exit'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress non-error output'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    if args.quiet:
        log_level = logging.ERROR
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/quantum_hedge_fund.log')
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Check system status
        if args.status:
            asyncio.run(check_system_status(args.config))
            return
        
        # Run tests
        if args.test:
            asyncio.run(run_system_tests(args.config))
            return
        
        # Validate configuration
        if not validate_config(args.config):
            logger.error("Configuration validation failed")
            sys.exit(1)
        
        # Create and run orchestrator
        logger.info("🚀 Quantum AI Hedge Fund Platform starting...")
        
        orchestrator = QuantumHedgeFundOrchestrator(args.config)
        
        # Disable quantum if requested
        if args.no_quantum:
            orchestrator.system_config.quantum_enabled = False
            logger.info("Quantum computing features disabled")
        
        # Setup signal handlers
        setup_signal_handlers(orchestrator)
        
        # Run the platform
        asyncio.run(orchestrator.run())
        
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

async def check_system_status(config_path):
    """Check system status without starting main platform"""
    try:
        logger = logging.getLogger(__name__)
        logger.info("Checking system status...")
        
        orchestrator = QuantumHedgeFundOrchOrchestrator(config_path)
        
        # Initialize components
        await orchestrator.initialize()
        
        # Get system status
        status = await orchestrator.get_system_status()
        
        print("\n" + "="*50)
        print("QUANTUM AI HEDGE FUND PLATFORM STATUS")
        print("="*50)
        print(f"Status: {status['status'].upper()}")
        print(f"Quantum Enabled: {status['quantum_enabled']}")
        print(f"Auto Trading: {status['auto_trading']}")
        print(f"Last Update: {status['last_update']}")
        
        if status['fund_metrics']:
            metrics = status['fund_metrics']
            print(f"Total Value: ${metrics.get('total_value', 0):,.2f}")
            print(f"Daily P&L: ${metrics.get('daily_pnl', 0):,.2f}")
            print(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
            print(f"Win Rate: {metrics.get('win_rate', 0):.1%}")
        
        print(f"Active Strategies: {len(status['active_strategies'])}")
        print(f"Risk Alerts: {status['risk_alerts']}")
        print(f"Compliance Violations: {status['compliance_violations']}")
        
        # Get component statistics
        if orchestrator.analytics_engine:
            analytics_stats = await orchestrator.analytics_engine.get_analytics_statistics()
            print(f"Analytics - Symbols Tracked: {analytics_stats['symbols_tracked']}")
        
        if orchestrator.risk_manager:
            risk_stats = await orchestrator.risk_manager.get_risk_statistics()
            print(f"Risk Manager - Assessments: {risk_stats['risk_assessments']}")
        
        if orchestrator.compliance_engine:
            compliance_stats = await orchestrator.compliance_engine.get_compliance_statistics()
            print(f"Compliance - Checks: {compliance_stats['compliance_checks']}")
        
        print("="*50)
        
        await orchestrator.shutdown()
        
    except Exception as e:
        logging.error(f"Status check failed: {e}")

async def run_system_tests(config_path):
    """Run system tests"""
    try:
        logger = logging.getLogger(__name__)
        logger.info("Running system tests...")
        
        orchestrator = QuantumHedgeFundOrchestrator(config_path)
        
        # Initialize system
        await orchestrator.initialize()
        
        print("\n" + "="*50)
        print("QUANTUM AI HEDGE FUND PLATFORM TESTS")
        print("="*50)
        
        # Test quantum optimization
        print("Testing Quantum Portfolio Optimization...")
        try:
            portfolio = {
                "assets": [
                    {"symbol": "AAPL", "expected_return": 0.07},
                    {"symbol": "GOOGL", "expected_return": 0.09}
                ]
            }
            result = await orchestrator.quantum_optimize_portfolio()
            if result and "expected_return" in result:
                print("✅ Quantum optimization: PASSED")
            else:
                print("❌ Quantum optimization: FAILED")
        except Exception as e:
            print(f"❌ Quantum optimization: ERROR - {e}")
        
        # Test market analysis
        print("Testing Market Analysis...")
        try:
            analysis = await orchestrator.run_market_analysis()
            if analysis and "confidence" in analysis:
                print("✅ Market analysis: PASSED")
            else:
                print("❌ Market analysis: FAILED")
        except Exception as e:
            print(f"❌ Market analysis: ERROR - {e}")
        
        # Test risk assessment
        print("Testing Risk Assessment...")
        try:
            risk_assessment = await orchestrator.risk_manager.assess_portfolio_risk()
            if risk_assessment and risk_assessment.risk_level:
                print("✅ Risk assessment: PASSED")
            else:
                print("❌ Risk assessment: FAILED")
        except Exception as e:
            print(f"❌ Risk assessment: ERROR - {e}")
        
        # Test compliance
        print("Testing Compliance...")
        try:
            is_compliant = await orchestrator.compliance_engine.check_compliance()
            if isinstance(is_compliant, bool):
                print("✅ Compliance check: PASSED")
            else:
                print("❌ Compliance check: FAILED")
        except Exception as e:
            print(f"❌ Compliance check: ERROR - {e}")
        
        # Test portfolio summary
        print("Testing Portfolio Summary...")
        try:
            summary = await orchestrator.trading_engine.get_portfolio_summary()
            if summary and "total_value" in summary:
                print("✅ Portfolio summary: PASSED")
            else:
                print("❌ Portfolio summary: FAILED")
        except Exception as e:
            print(f"❌ Portfolio summary: ERROR - {e}")
        
        print("="*50)
        print("Test execution completed.")
        
        await orchestrator.shutdown()
        
    except Exception as e:
        logging.error(f"Test execution failed: {e}")

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    # Run main function
    main()