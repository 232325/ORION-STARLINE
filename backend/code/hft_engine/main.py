"""
HFT Engine Main Entry Point
==========================

Main application entry point for the High-Frequency Trading Engine
"""

import asyncio
import logging
import sys
import signal
from typing import Dict, Any

from .core import HFTEngine
from .config.default_config import load_config, validate_config

class HFTApplication:
    """HFT Engine Application"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.engine: HFTEngine = None
        self.logger = logging.getLogger(__name__)
        self.running = False
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging_config = self.config.get('logging', {})
        
        # Configure logging
        log_level = getattr(logging, logging_config.get('level', 'INFO').upper())
        
        # Create formatter
        formatter = logging.Formatter(
            logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler (if specified)
        log_file = logging_config.get('file')
        if log_file:
            from logging.handlers import RotatingFileHandler
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=logging_config.get('max_size_mb', 100) * 1024 * 1024,
                backupCount=logging_config.get('backup_count', 5)
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        self.logger.info("Logging configured successfully")
    
    async def initialize(self) -> bool:
        """Initialize the HFT application"""
        try:
            self.logger.info("Initializing HFT Application...")
            
            # Setup logging
            self.setup_logging()
            
            # Validate configuration
            if not validate_config(self.config):
                self.logger.error("Configuration validation failed")
                return False
            
            # Initialize engine
            self.engine = HFTEngine(self.config)
            
            # Initialize engine components
            if not await self.engine.initialize():
                self.logger.error("Failed to initialize HFT Engine")
                return False
            
            self.logger.info("HFT Application initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize HFT Application: {e}")
            return False
    
    async def start(self):
        """Start the HFT application"""
        try:
            self.logger.info("Starting HFT Application...")
            self.running = True
            
            # Start the engine
            await self.engine.start()
            
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Error in HFT Application: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown the HFT application"""
        if not self.running:
            return
        
        self.logger.info("Shutting down HFT Application...")
        self.running = False
        
        try:
            # Shutdown engine
            if self.engine:
                await self.engine.shutdown()
            
            self.logger.info("HFT Application shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get application status"""
        if self.engine:
            return {
                'running': self.running,
                'engine_status': self.engine.get_health_status()
            }
        else:
            return {
                'running': False,
                'engine_status': 'not_initialized'
            }

async def main():
    """Main application entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='High-Frequency Trading Engine')
    parser.add_argument('--env', choices=['development', 'production', 'test'], 
                       default='development', help='Environment to run in')
    parser.add_argument('--config-file', help='Path to custom configuration file')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode')
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config_file:
        import json
        with open(args.config_file, 'r') as f:
            config = json.load(f)
    else:
        config = load_config(args.env)
    
    # Create and run application
    app = HFTApplication(config)
    
    # Handle signals for graceful shutdown
    def signal_handler(signum, frame):
        """Handle system signals"""
        print(f"\nReceived signal {signum}, shutting down...")
        asyncio.create_task(app.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize and start application
    if await app.initialize():
        if args.dry_run:
            print("Dry run mode - running initialization only")
            status = app.get_status()
            print(f"Application status: {status}")
            await app.shutdown()
        else:
            await app.start()
    else:
        print("Failed to initialize application")
        sys.exit(1)

if __name__ == '__main__':
    # Set up event loop policy for Windows if needed
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)