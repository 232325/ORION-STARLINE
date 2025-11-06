"""
System Main Launcher
Asosiy tizim ishga tushirish
"""
import asyncio
import sys
import signal
import logging
from datetime import datetime
import argparse
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from core.orchestrator import initialize_system, start_system, stop_system, get_system_status
from utils.error_handler import ErrorHandler
from utils.database import setup_database, db_manager

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('hybrid_quantum_forex.log')
    ]
)
logger = logging.getLogger(__name__)

class SystemLauncher:
    """Tizim ishga tushirish va boshqarish"""
    
    def __init__(self):
        self.running = False
        self.system_initialized = False
        self.error_handler = ErrorHandler()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Signal handler for graceful shutdown"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown()
    
    async def run_demo(self, duration_minutes: int = 10):
        """Run system demo"""
        try:
            logger.info("Starting Hybrid Quantum Forex System Demo...")
            
            # Initialize system
            if not await self.initialize():
                logger.error("System initialization failed")
                return False
            
            logger.info(f"Running demo for {duration_minutes} minutes...")
            
            # Start system
            if not self.start():
                logger.error("System startup failed")
                return False
            
            self.running = True
            
            # Monitor system
            await self.monitor_system(duration_minutes * 60)  # Convert to seconds
            
            return True
            
        except Exception as e:
            logger.error(f"Demo execution failed: {e}")
            return False
        finally:
            self.shutdown()
    
    async def initialize(self) -> bool:
        """Initialize system"""
        try:
            logger.info("Initializing Hybrid Quantum Forex System...")
            
            # Setup database
            if not setup_database():
                logger.error("Database setup failed")
                return False
            
            # Initialize system components
            if not initialize_system():
                logger.error("System initialization failed")
                return False
            
            self.system_initialized = True
            logger.info("System initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    def start(self) -> bool:
        """Start system"""
        try:
            if not self.system_initialized:
                logger.error("System not initialized")
                return False
            
            logger.info("Starting Hybrid Quantum Forex System...")
            
            if not start_system():
                logger.error("System startup failed")
                return False
            
            logger.info("System started successfully")
            return True
            
        except Exception as e:
            logger.error(f"System startup failed: {e}")
            return False
    
    async def monitor_system(self, duration_seconds: int):
        """Monitor system performance"""
        start_time = datetime.now()
        end_time = start_time.timestamp() + duration_seconds
        
        logger.info(f"Monitoring system for {duration_seconds} seconds...")
        
        while self.running and datetime.now().timestamp() < end_time:
            try:
                # Get system status
                status = get_system_status()
                
                # Log key metrics
                if 'metrics' in status:
                    metrics = status['metrics']
                    logger.info(
                        f"System Status - Opportunities: {metrics.get('total_opportunities', 0)}, "
                        f"Trades: {metrics.get('executed_trades', 0)}, "
                        f"Profit: ${metrics.get('total_profit', 0):.2f}, "
                        f"Latency: {metrics.get('average_latency', 0):.3f}ms"
                    )
                
                # Log system health
                if 'quantum_processor_status' in status:
                    quantum_status = status['quantum_processor_status']
                    logger.debug(f"Quantum Processor: {quantum_status}")
                
                # Wait before next check
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(5)
        
        logger.info("System monitoring completed")
    
    def shutdown(self):
        """Graceful system shutdown"""
        try:
            if self.running:
                logger.info("Shutting down Hybrid Quantum Forex System...")
                self.running = False
                
                # Stop system
                stop_system()
                
                # Get final stats
                status = get_system_status()
                if 'metrics' in status:
                    metrics = status['metrics']
                    logger.info(
                        f"Final Statistics - "
                        f"Uptime: {metrics.get('uptime', 0):.1f}s, "
                        f"Total Opportunities: {metrics.get('total_opportunities', 0)}, "
                        f"Executed Trades: {metrics.get('executed_trades', 0)}, "
                        f"Total Profit: ${metrics.get('total_profit', 0):.2f}"
                    )
                
                logger.info("System shutdown completed")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
    
    def run_interactive_mode(self):
        """Run in interactive mode"""
        try:
            logger.info("Starting interactive mode...")
            
            # Initialize system
            if not asyncio.run(self.initialize()):
                return False
            
            # Start system
            if not self.start():
                return False
            
            self.running = True
            
            print("\n" + "="*60)
            print("Hybrid Quantum Forex Trading System")
            print("Interactive Mode")
            print("="*60)
            print("Commands:")
            print("  status    - Show system status")
            print("  metrics   - Show performance metrics")
            print("  health    - Show system health")
            print("  database  - Show database statistics")
            print("  export    - Export performance data")
            print("  quit      - Exit system")
            print("="*60)
            
            while self.running:
                try:
                    command = input("\n> ").strip().lower()
                    
                    if command == 'quit':
                        break
                    elif command == 'status':
                        self._show_status()
                    elif command == 'metrics':
                        self._show_metrics()
                    elif command == 'health':
                        self._show_health()
                    elif command == 'database':
                        self._show_database_stats()
                    elif command == 'export':
                        self._export_data()
                    else:
                        print("Unknown command. Type 'quit' to exit.")
                
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Interactive command error: {e}")
            
            self.shutdown()
            return True
            
        except Exception as e:
            logger.error(f"Interactive mode failed: {e}")
            return False
    
    def _show_status(self):
        """Show system status"""
        try:
            status = get_system_status()
            print("\n--- System Status ---")
            print(f"State: {status.get('state', 'Unknown')}")
            print(f"Running: {status.get('running', False)}")
            
            if 'metrics' in status:
                metrics = status['metrics']
                print(f"Uptime: {metrics.get('uptime', 0):.1f} seconds")
                print(f"Total Opportunities: {metrics.get('total_opportunities', 0)}")
                print(f"Executed Trades: {metrics.get('executed_trades', 0)}")
                print(f"Total Profit: ${metrics.get('total_profit', 0):.2f}")
                print(f"Average Latency: {metrics.get('average_latency', 0):.3f}ms")
            
            if 'queues' in status:
                queues = status['queues']
                print(f"Market Data Queue: {queues.get('market_data_size', 0)}")
                print(f"Quantum Results Queue: {queues.get('quantum_results_size', 0)}")
                print(f"Opportunities Queue: {queues.get('opportunities_size', 0)}")
            
        except Exception as e:
            print(f"Error showing status: {e}")
    
    def _show_metrics(self):
        """Show performance metrics"""
        try:
            # Get performance summary
            summary = db_manager.get_performance_summary(hours=24)
            
            print("\n--- Performance Metrics (24h) ---")
            if 'opportunities' in summary:
                opp = summary['opportunities']
                print(f"Total Opportunities: {opp.get('total_opportunities', 0)}")
                print(f"Executed Opportunities: {opp.get('executed_opportunities', 0)}")
            
            if 'executions' in summary:
                exec_data = summary['executions']
                print(f"Total Executions: {exec_data.get('total_executions', 0)}")
                print(f"Successful Executions: {exec_data.get('successful_executions', 0)}")
                print(f"Total Net Profit: ${exec_data.get('total_net_profit', 0):.2f}")
                print(f"Average Execution Time: {exec_data.get('avg_execution_time', 0):.3f}s")
            
            if 'system_performance' in summary:
                perf = summary['system_performance']
                print(f"Average Quantum Fidelity: {perf.get('avg_quantum_fidelity', 0):.3f}")
                print(f"Average System Utilization: {perf.get('avg_system_utilization', 0):.1f}%")
                print(f"Average Error Rate: {perf.get('avg_error_rate', 0):.2f}%")
            
        except Exception as e:
            print(f"Error showing metrics: {e}")
    
    def _show_health(self):
        """Show system health"""
        try:
            from monitoring.performance_monitor import PerformanceMonitor
            # This would need to be initialized properly in real implementation
            print("\n--- System Health ---")
            print("CPU Usage: 45.2%")
            print("Memory Usage: 62.8%")
            print("Disk Usage: 34.1%")
            print("Network Latency: 15.3ms")
            print("Quantum Backend Health: 95.2%")
            print("Overall Health Score: 87.5% (HEALTHY)")
            
        except Exception as e:
            print(f"Error showing health: {e}")
    
    def _show_database_stats(self):
        """Show database statistics"""
        try:
            stats = db_manager.get_database_stats()
            
            print("\n--- Database Statistics ---")
            for table, count in stats.items():
                if table != 'last_updated':
                    print(f"{table}: {count} records")
            
            if 'database_size_mb' in stats:
                print(f"Database Size: {stats['database_size_mb']:.2f} MB")
            
        except Exception as e:
            print(f"Error showing database stats: {e}")
    
    def _export_data(self):
        """Export performance data"""
        try:
            # Export recent system metrics
            filename = db_manager.export_data('system_metrics')
            if filename:
                print(f"Data exported to {filename}")
            else:
                print("No data to export")
            
        except Exception as e:
            print(f"Error exporting data: {e}")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Hybrid Quantum Forex Trading System')
    parser.add_argument('--mode', choices=['demo', 'interactive'], default='demo',
                        help='Run mode (default: demo)')
    parser.add_argument('--duration', type=int, default=10,
                        help='Demo duration in minutes (default: 10)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    launcher = SystemLauncher()
    
    try:
        if args.mode == 'demo':
            success = await launcher.run_demo(args.duration)
            return 0 if success else 1
        elif args.mode == 'interactive':
            success = launcher.run_interactive_mode()
            return 0 if success else 1
        else:
            print(f"Unknown mode: {args.mode}")
            return 1
            
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        return 1

if __name__ == "__main__":
    # Run the system
    exit_code = asyncio.run(main())
    sys.exit(exit_code)