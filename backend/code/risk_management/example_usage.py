"""
Risk Management System - Example Usage
======================================

Comprehensive example demonstrating how to use the Advanced Risk Management System
for high-frequency trading with real-time monitoring, analytics, and compliance.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

# Import risk management components
from .core.risk_manager import RiskManager
from .monitoring.real_time_monitor import RealTimeMonitor
from .analytics.analytics_engine import AnalyticsEngine
from .compliance.compliance_engine import ComplianceEngine
from .integrations.integration_framework import IntegrationFramework
from .config import get_default_config, get_production_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RiskManagementDemo:
    """Demonstration class for risk management system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or get_default_config()
        
        # Initialize components
        self.risk_manager = None
        self.analytics_engine = None
        self.compliance_engine = None
        self.integration_framework = None
        
        # Demo state
        self.running = False
    
    async def initialize(self):
        """Initialize the risk management system"""
        try:
            logger.info("Initializing Risk Management System...")
            
            # Initialize core risk manager
            self.risk_manager = RiskManager(self.config)
            await self.risk_manager.initialize()
            
            # Initialize analytics engine
            self.analytics_engine = AnalyticsEngine(self.config.get('analytics_engine', {}))
            await self.analytics_engine.initialize()
            
            # Initialize compliance engine
            self.compliance_engine = ComplianceEngine(self.config.get('compliance_engine', {}))
            
            # Initialize integration framework
            self.integration_framework = IntegrationFramework(self.config.get('integration_framework', {}))
            await self.integration_framework.initialize()
            
            logger.info("Risk Management System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize risk management system: {e}")
            raise
    
    async def start_monitoring(self):
        """Start real-time risk monitoring"""
        try:
            logger.info("Starting risk monitoring...")
            
            # Start risk manager monitoring
            await self.risk_manager.start_monitoring()
            
            # Start integration framework
            await self.integration_framework.start()
            
            self.running = True
            
            logger.info("Risk monitoring started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start risk monitoring: {e}")
            raise
    
    async def run_comprehensive_demo(self):
        """Run comprehensive demonstration of risk management features"""
        try:
            logger.info("=" * 60)
            logger.info("ADVANCED RISK MANAGEMENT SYSTEM DEMO")
            logger.info("=" * 60)
            
            # 1. Initialize system
            await self.initialize()
            
            # 2. Start monitoring
            await self.start_monitoring()
            
            # 3. Demonstrate various features
            await self.demo_portfolio_assessment()
            await self.demo_analytics_features()
            await self.demo_compliance_monitoring()
            await self.demo_integration_features()
            await self.demo_risk_controls()
            
            # 4. Generate reports
            await self.demo_reporting()
            
            # 5. Cleanup
            await self.cleanup()
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
        finally:
            self.running = False
    
    async def demo_portfolio_assessment(self):
        """Demonstrate portfolio risk assessment"""
        logger.info("\n" + "="*50)
        logger.info("DEMO: Portfolio Risk Assessment")
        logger.info("="*50)
        
        # Create sample positions
        sample_positions = {
            'AAPL': {
                'symbol': 'AAPL',
                'asset_class': 'equity',
                'quantity': 1000,
                'avg_cost': 150.0,
                'current_price': 155.0,
                'market_value': 155000,
                'unrealized_pnl': 5000,
                'realized_pnl': 0,
                'timestamp': datetime.now(),
                'stop_loss': 140.0,
                'take_profit': 165.0,
                'position_limit': 500000.0,
                'liquidity_ratio': 0.9,
                'correlation': 0.7,
                'beta': 1.2
            },
            'GOOGL': {
                'symbol': 'GOOGL',
                'asset_class': 'equity',
                'quantity': 100,
                'avg_cost': 2800.0,
                'current_price': 2850.0,
                'market_value': 285000,
                'unrealized_pnl': 5000,
                'realized_pnl': 0,
                'timestamp': datetime.now(),
                'stop_loss': 2700.0,
                'take_profit': 2900.0,
                'position_limit': 1000000.0,
                'liquidity_ratio': 0.8,
                'correlation': 0.6,
                'beta': 1.1
            },
            'EURUSD': {
                'symbol': 'EURUSD',
                'asset_class': 'forex',
                'quantity': 1000000,
                'avg_cost': 1.1000,
                'current_price': 1.1025,
                'market_value': 1102500,
                'unrealized_pnl': 2500,
                'realized_pnl': 0,
                'timestamp': datetime.now(),
                'stop_loss': 1.0950,
                'take_profit': 1.1080,
                'position_limit': 50000000.0,
                'liquidity_ratio': 0.95,
                'correlation': 0.3,
                'beta': 0.8
            },
            'GC': {
                'symbol': 'GC',  # Gold futures
                'asset_class': 'commodity',
                'quantity': 50,
                'avg_cost': 1800.0,
                'current_price': 1820.0,
                'market_value': 91000,
                'unrealized_pnl': 1000,
                'realized_pnl': 0,
                'timestamp': datetime.now(),
                'stop_loss': 1775.0,
                'take_profit': 1850.0,
                'position_limit': 1000000.0,
                'liquidity_ratio': 0.7,
                'correlation': 0.2,
                'beta': 0.3
            }
        }
        
        # Create sample market data
        sample_market_data = {
            'AAPL': {
                'price': 155.0,
                'volume': 1000000,
                'bid': 154.9,
                'ask': 155.1,
                'spread': 0.2,
                'volatility': 0.25,
                'returns': self.generate_sample_returns(252)
            },
            'GOOGL': {
                'price': 2850.0,
                'volume': 500000,
                'bid': 2849.0,
                'ask': 2851.0,
                'spread': 2.0,
                'volatility': 0.30,
                'returns': self.generate_sample_returns(252)
            },
            'EURUSD': {
                'price': 1.1025,
                'volume': 5000000,
                'bid': 1.1024,
                'ask': 1.1026,
                'spread': 0.0002,
                'volatility': 0.12,
                'returns': self.generate_sample_returns(252)
            },
            'GC': {
                'price': 1820.0,
                'volume': 100000,
                'bid': 1819.5,
                'ask': 1820.5,
                'spread': 1.0,
                'volatility': 0.18,
                'returns': self.generate_sample_returns(252)
            }
        }
        
        # Perform portfolio risk assessment
        logger.info("Performing comprehensive portfolio risk assessment...")
        
        risk_report = await self.risk_manager.assess_portfolio_risk()
        
        logger.info(f"Portfolio Value: ${risk_report.portfolio_value:,.2f}")
        logger.info(f"Total VaR (1-day, 95%): ${risk_report.total_var:,.2f}")
        logger.info(f"Risk Level: {risk_report.risk_level.value}")
        logger.info(f"Active Alerts: {len(risk_report.alerts)}")
        logger.info(f"Recommendations: {len(risk_report.recommendations)}")
        
        if risk_report.recommendations:
            logger.info("Top Recommendations:")
            for i, rec in enumerate(risk_report.recommendations[:3], 1):
                logger.info(f"  {i}. {rec}")
        
        logger.info("Portfolio assessment completed")
    
    async def demo_analytics_features(self):
        """Demonstrate advanced analytics features"""
        logger.info("\n" + "="*50)
        logger.info("DEMO: Advanced Analytics Features")
        logger.info("="*50)
        
        # Get current data
        positions = await self.risk_manager.position_monitor.get_current_positions()
        market_data = await self.risk_manager.data_manager.get_current_market_data()
        
        # Run comprehensive analytics
        logger.info("Running comprehensive analytics...")
        
        analytics_result = await self.analytics_engine.run_comprehensive_analysis(
            positions, market_data
        )
        
        logger.info(f"Analytics completed in {analytics_result.analytics_duration:.2f} seconds")
        logger.info(f"Portfolio Value: ${analytics_result.portfolio_value:,.2f}")
        
        # VaR Analysis
        var_results = analytics_result.var_results
        logger.info("VaR Analysis:")
        if var_results:
            for key, value in var_results.items():
                if 'var_' in key:
                    logger.info(f"  {key}: ${value:,.2f}")
        
        # Stress Testing
        stress_results = analytics_result.stress_test_results
        logger.info("Stress Testing Results:")
        if stress_results:
            for scenario, loss in stress_results.items():
                logger.info(f"  {scenario}: {loss:.2%} loss")
        
        # Risk Attribution
        risk_attribution = analytics_result.risk_attribution
        logger.info("Risk Attribution:")
        if risk_attribution and 'component_var' in risk_attribution:
            for symbol, var_contrib in risk_attribution['component_var'].items():
                logger.info(f"  {symbol}: ${var_contrib:,.2f} VaR contribution")
        
        logger.info("Analytics demonstration completed")
    
    async def demo_compliance_monitoring(self):
        """Demonstrate compliance monitoring"""
        logger.info("\n" + "="*50)
        logger.info("DEMO: Compliance Monitoring")
        logger.info("="*50)
        
        # Get current positions and metrics
        positions = await self.risk_manager.position_monitor.get_current_positions()
        portfolio_metrics = {
            'total_capital': 2000000,
            'tier1_capital': 1500000,
            'risk_weighted_assets': 15000000,
            'total_exposure': 2500000,
            'hqla': 1000000,
            'net_cash_outflows': 1200000
        }
        
        # Check compliance
        logger.info("Checking regulatory compliance...")
        
        compliance_report = await self.compliance_engine.check_compliance(
            positions, portfolio_metrics
        )
        
        logger.info(f"Compliance Score: {compliance_report.compliance_score:.1f}%")
        logger.info(f"Overall Status: {compliance_report.overall_status.value}")
        logger.info(f"Violations Found: {compliance_report.violations_count}")
        logger.info(f"Critical Violations: {compliance_report.critical_violations}")
        
        if compliance_report.recommendations:
            logger.info("Compliance Recommendations:")
            for i, rec in enumerate(compliance_report.recommendations[:3], 1):
                logger.info(f"  {i}. {rec}")
        
        # Get compliance summary
        compliance_summary = await self.compliance_engine.get_compliance_summary()
        logger.info(f"Total Rules: {compliance_summary['total_rules']}")
        logger.info(f"Active Violations: {compliance_summary['active_violations']}")
        
        logger.info("Compliance demonstration completed")
    
    async def demo_integration_features(self):
        """Demonstrate integration features"""
        logger.info("\n" + "="*50)
        logger.info("DEMO: Integration Features")
        logger.info("="*50)
        
        # Get integration summary
        integration_summary = await self.integration_framework.get_integration_summary()
        
        logger.info("Integration Framework Status:")
        logger.info(f"Framework Running: {integration_summary['framework_running']}")
        
        # Check configured integrations
        configured = integration_summary['configured_integrations']
        for integration, enabled in configured.items():
            status = "enabled" if enabled else "disabled"
            logger.info(f"  {integration}: {status}")
        
        # Get external risk data
        logger.info("Fetching external risk data...")
        external_data = await self.integration_framework.get_external_risk_data()
        
        if external_data:
            logger.info("External Data Sources:")
            for source, data in external_data.items():
                logger.info(f"  {source}: {type(data)}")
        
        # Demonstrate risk control signals
        logger.info("Demonstrating risk control signals...")
        
        # Send position adjustment signal
        adjustment_result = await self.integration_framework.send_risk_control_signal(
            "position_adjustment",
            {
                "symbol": "AAPL",
                "target_position": 500,  # Reduce position
                "reason": "risk_management_demonstration"
            }
        )
        
        if adjustment_result:
            logger.info("✓ Position adjustment signal sent successfully")
        else:
            logger.warning("✗ Failed to send position adjustment signal")
        
        # Demonstrate emergency action
        emergency_result = await self.integration_framework.request_emergency_position_close(
            "GC",
            "demonstration_emergency_action"
        )
        
        if emergency_result:
            logger.info("✓ Emergency position close signal sent successfully")
        else:
            logger.warning("✗ Failed to send emergency position close signal")
        
        logger.info("Integration demonstration completed")
    
    async def demo_risk_controls(self):
        """Demonstrate automated risk controls"""
        logger.info("\n" + "="*50)
        logger.info("DEMO: Automated Risk Controls")
        logger.info("="*50)
        
        # Get current positions
        positions = await self.risk_manager.position_monitor.get_current_positions()
        
        logger.info("Executing automated risk controls...")
        
        # Execute risk controls
        control_actions = await self.risk_manager.execute_risk_controls(positions)
        
        if control_actions:
            logger.info("Risk Control Actions Executed:")
            for action_type, actions in control_actions.items():
                logger.info(f"  {action_type}: {len(actions)} actions")
                for action in actions:
                    logger.info(f"    - {action}")
        else:
            logger.info("No risk control actions required at this time")
        
        # Test limit violations
        logger.info("Testing limit violations...")
        
        # Create positions that exceed limits
        violating_positions = positions.copy()
        
        # Increase one position significantly to trigger limits
        if 'AAPL' in violating_positions:
            violating_positions['AAPL']['market_value'] = 2000000  # Exceeds typical limit
        
        # Check limits
        violations = await self.risk_manager.risk_limits.check_limits(violating_positions)
        
        if violations:
            logger.info(f"Found {len(violations)} limit violations:")
            for violation in violations[:3]:  # Show first 3
                logger.info(f"  - {violation.get('description', 'Unknown violation')}")
        else:
            logger.info("No limit violations detected")
        
        logger.info("Risk controls demonstration completed")
    
    async def demo_reporting(self):
        """Demonstrate reporting features"""
        logger.info("\n" + "="*50)
        logger.info("DEMO: Reporting Features")
        logger.info("="*50)
        
        # Generate JSON risk report
        logger.info("Generating comprehensive risk report...")
        
        json_report = await self.risk_manager.generate_risk_report('json')
        
        # Parse and display key metrics
        import json
        report_data = json.loads(json_report)
        
        logger.info("Risk Report Summary:")
        logger.info(f"  Timestamp: {report_data['timestamp']}")
        logger.info(f"  Risk Level: {report_data['summary']['risk_level']}")
        logger.info(f"  Portfolio Value: ${report_data['summary']['portfolio_value']:,.2f}")
        logger.info(f"  1-Day VaR: ${report_data['summary']['var_1d']:,.2f}")
        logger.info(f"  Active Alerts: {report_data['summary']['active_alerts']}")
        
        # Generate analytics report
        logger.info("Generating analytics report...")
        
        analytics_export = await self.analytics_engine.export_analytics_data(
            await self.risk_manager.position_monitor.get_current_positions(),
            await self.risk_manager.data_manager.get_current_market_data()
        )
        
        # Generate compliance report
        logger.info("Generating compliance report...")
        
        compliance_export = await self.compliance_engine.export_compliance_report()
        
        # Generate integration report
        logger.info("Generating integration report...")
        
        integration_export = await self.integration_framework.export_integration_data()
        
        logger.info("All reports generated successfully")
        logger.info("Reports include:")
        logger.info("  - Comprehensive risk assessment")
        logger.info("  - Analytics results and backtesting")
        logger.info("  - Compliance status and violations")
        logger.info("  - Integration status and events")
        
        logger.info("Reporting demonstration completed")
    
    async def cleanup(self):
        """Cleanup and shutdown"""
        logger.info("\n" + "="*50)
        logger.info("CLEANUP AND SHUTDOWN")
        logger.info("="*50)
        
        try:
            # Stop monitoring
            if self.risk_manager:
                await self.risk_manager.stop_monitoring()
                logger.info("Risk monitoring stopped")
            
            # Stop integration framework
            if self.integration_framework:
                await self.integration_framework.stop()
                logger.info("Integration framework stopped")
            
            # Close data connections
            if self.risk_manager and self.risk_manager.data_manager:
                await self.risk_manager.data_manager.close()
                logger.info("Data connections closed")
            
            logger.info("Risk management system shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def generate_sample_returns(self, length: int = 252):
        """Generate sample returns for demonstration"""
        import numpy as np
        np.random.seed(42)  # For reproducible results
        return np.random.normal(0.0002, 0.02, length)

async def run_basic_demo():
    """Run basic risk management demonstration"""
    logger.info("Starting Basic Risk Management Demo")
    
    try:
        demo = RiskManagementDemo()
        await demo.run_comprehensive_demo()
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise

async def run_production_demo():
    """Run production-optimized demonstration"""
    logger.info("Starting Production Risk Management Demo")
    
    config = get_production_config()
    
    try:
        demo = RiskManagementDemo(config)
        await demo.run_comprehensive_demo()
        
    except Exception as e:
        logger.error(f"Production demo failed: {e}")
        raise

async def run_individual_components_demo():
    """Demonstrate individual components"""
    logger.info("Starting Individual Components Demo")
    
    try:
        from .analytics.var_calculator import VaRCalculator
        from .analytics.stress_tester import StressTester
        from .monitoring.real_time_monitor import RealTimeMonitor
        
        # Demo VaR Calculator
        logger.info("Testing VaR Calculator...")
        var_calc = VaRCalculator({})
        positions = {
            'AAPL': {'market_value': 100000, 'returns': [0.01, -0.02, 0.005]}
        }
        market_data = {'AAPL': {'returns': [0.01, -0.02, 0.005]}}
        
        var_result = await var_calc.calculate_var(positions, market_data)
        logger.info(f"VaR Result: {var_result}")
        
        # Demo Stress Tester
        logger.info("Testing Stress Tester...")
        stress_tester = StressTester({})
        stress_results = await stress_tester.run_stress_tests(positions, market_data)
        logger.info(f"Stress Test Results: {stress_results}")
        
        # Demo Real-time Monitor
        logger.info("Testing Real-time Monitor...")
        monitor = RealTimeMonitor({})
        await monitor.start()
        
        # Add some sample market data
        from .monitoring.real_time_monitor import MarketUpdate
        market_update = MarketUpdate(
            symbol='AAPL',
            price=155.0,
            volume=1000000,
            timestamp=datetime.now()
        )
        await monitor.update_market_data(market_update)
        
        metrics = await monitor.get_risk_metrics()
        logger.info(f"Monitor Metrics: {metrics}")
        
        await monitor.stop()
        
        logger.info("Individual components demo completed")
        
    except Exception as e:
        logger.error(f"Individual components demo failed: {e}")
        raise

if __name__ == "__main__":
    """
    Main execution examples
    """
    import sys
    
    if len(sys.argv) > 1:
        demo_type = sys.argv[1].lower()
        
        if demo_type == "basic":
            asyncio.run(run_basic_demo())
        elif demo_type == "production":
            asyncio.run(run_production_demo())
        elif demo_type == "components":
            asyncio.run(run_individual_components_demo())
        else:
            print("Usage: python example_usage.py [basic|production|components]")
            sys.exit(1)
    else:
        # Run basic demo by default
        asyncio.run(run_basic_demo())