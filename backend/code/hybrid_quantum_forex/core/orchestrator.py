"""
Hybrid Quantum-Classical Forex Arbitrage System - Main Orchestrator
Asosiy tizim orkestratori
"""
import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import json

from ..classical.preprocessing import ClassicalPreprocessor
from ..quantum.core_processor import QuantumProcessor
from ..classical.postprocessing import ClassicalPostprocessor
from ..arbitrage.detector import ArbitrageDetector
from ..arbitrage.executor import ArbitrageExecutor
from ..monitoring.performance_monitor import PerformanceMonitor
from ..utils.error_handler import ErrorHandler
from ..utils.data_models import MarketData, ArbitrageOpportunity, SystemState
from ..config.config import config

# Logging konfiguratsiyasi
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """Tizim metrikalari"""
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_opportunities: int = 0
    executed_trades: int = 0
    total_profit: float = 0.0
    quantum_processing_time: float = 0.0
    classical_processing_time: float = 0.0
    total_latency: float = 0.0
    error_rate: float = 0.0
    uptime: float = 0.0

class HybridQuantumForexSystem:
    """
    Hybrid Quantum-Classical Forex Arbitrage System
    Asosiy tizim sinfi
    """
    
    def __init__(self):
        """Tizimni ishga tushirish"""
        self.state = SystemState.INITIALIZING
        self.running = False
        self.metrics = SystemMetrics()
        
        # Core komponentlar
        self.preprocessor = ClassicalPreprocessor(config.forex_config)
        self.quantum_processor = QuantumProcessor(config.quantum_config)
        self.postprocessor = ClassicalPostprocessor(config.arbitrage_config)
        self.detector = ArbitrageDetector(config.arbitrage_config)
        self.executor = ArbitrageExecutor(config.arbitrage_config)
        self.monitor = PerformanceMonitor(config)
        self.error_handler = ErrorHandler()
        
        # Data queues
        self.market_data_queue = queue.Queue(maxsize=1000)
        self.quantum_results_queue = queue.Queue(maxsize=500)
        self.opportunities_queue = queue.Queue(maxsize=100)
        
        # Workers
        self.executor_workers = ThreadPoolExecutor(max_workers=config.max_workers)
        self.quantum_workers = ThreadPoolExecutor(max_workers=2)
        
        # Threading
        self.threads = []
        self.stop_event = threading.Event()
        
        logger.info("Hybrid Quantum Forex System initialized")
    
    def initialize(self) -> bool:
        """Tizimni inicializatsiya qilish"""
        try:
            logger.info("System initialization started...")
            
            # Komponentlarni tekshirish
            if not self._validate_components():
                logger.error("Component validation failed")
                return False
            
            # Error handler konfiguratsiya
            self.error_handler.setup_error_handling()
            
            # Performance monitor ishga tushirish
            self.monitor.start()
            
            # Database va audit trail sozlash
            self._setup_audit_system()
            
            self.state = SystemState.READY
            logger.info("System initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"System initialization failed: {str(e)}")
            self.state = SystemState.ERROR
            return False
    
    def start(self) -> bool:
        """Tizimni ishga tushirish"""
        if self.state != SystemState.READY:
            logger.error(f"Cannot start system from state: {self.state}")
            return False
        
        try:
            self.running = True
            self.state = SystemState.RUNNING
            self.metrics.start_time = datetime.now(timezone.utc)
            
            # Main processing threads
            self.threads.extend([
                threading.Thread(target=self._market_data_processor, daemon=True),
                threading.Thread(target=self._quantum_processor_loop, daemon=True),
                threading.Thread(target=self._arbitrage_detector_loop, daemon=True),
                threading.Thread(target=self._arbitrage_executor_loop, daemon=True),
                threading.Thread(target=self._performance_tracker, daemon=True)
            ])
            
            # Threadlarni ishga tushirish
            for thread in self.threads:
                thread.start()
            
            logger.info("System started successfully")
            return True
            
        except Exception as e:
            logger.error(f"System start failed: {str(e)}")
            self.state = SystemState.ERROR
            return False
    
    def stop(self) -> bool:
        """Tizimni to'xtatish"""
        try:
            logger.info("System shutdown started...")
            
            self.running = False
            self.stop_event.set()
            
            # Queue'larni tozalash
            self._clear_queues()
            
            # Threadlarni kutish
            for thread in self.threads:
                thread.join(timeout=5)
            
            # Executorlarni yopish
            self.executor_workers.shutdown(wait=True)
            self.quantum_workers.shutdown(wait=True)
            
            # Performance monitor to'xtatish
            self.monitor.stop()
            
            # Final metrics save
            self._save_final_metrics()
            
            self.state = SystemState.SHUTDOWN
            logger.info("System shutdown completed")
            return True
            
        except Exception as e:
            logger.error(f"System shutdown error: {str(e)}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Tizim statusini olish"""
        return {
            'state': self.state.value,
            'running': self.running,
            'metrics': {
                'uptime': (datetime.now(timezone.utc) - self.metrics.start_time).total_seconds(),
                'total_opportunities': self.metrics.total_opportunities,
                'executed_trades': self.metrics.executed_trades,
                'total_profit': self.metrics.total_profit,
                'average_latency': self.metrics.total_latency / max(self.metrics.executed_trades, 1),
                'error_rate': self.metrics.error_rate
            },
            'queues': {
                'market_data_size': self.market_data_queue.qsize(),
                'quantum_results_size': self.quantum_results_queue.qsize(),
                'opportunities_size': self.opportunities_queue.qsize()
            },
            'quantum_processor_status': self.quantum_processor.get_status(),
            'monitor_status': self.monitor.get_status()
        }
    
    def _validate_components(self) -> bool:
        """Komponentlarni validatsiya qilish"""
        try:
            # Classical preprocessor test
            if not self.preprocessor.test_connection():
                return False
            
            # Quantum processor test
            if not self.quantum_processor.test_connection():
                return False
            
            # Database connection test
            if not self.monitor.test_database_connection():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Component validation error: {str(e)}")
            return False
    
    def _setup_audit_system(self):
        """Audit tizimini sozlash"""
        # Database create qilish
        from ..utils.database import setup_database
        setup_database()
        
        logger.info("Audit system setup completed")
    
    def _clear_queues(self):
        """Queue'larni tozalash"""
        queues = [self.market_data_queue, self.quantum_results_queue, self.opportunities_queue]
        for q in queues:
            while not q.empty():
                try:
                    q.get_nowait()
                except queue.Empty:
                    break
    
    def _market_data_processor(self):
        """Market data qayta ishlovchi thread"""
        logger.info("Market data processor started")
        
        while self.running and not self.stop_event.is_set():
            try:
                # Market data olish
                market_data = self.preprocessor.get_latest_data()
                
                if market_data:
                    # Classical preprocessing
                    processed_data = self.preprocessor.process_data(market_data)
                    
                    # Queue'ga qo'yish
                    if not self.market_data_queue.full():
                        self.market_data_queue.put_nowait(processed_data)
                
                time.sleep(config.forex_config.update_interval)
                
            except Exception as e:
                logger.error(f"Market data processor error: {str(e)}")
                self.error_handler.handle_error(e, "market_data_processor")
                time.sleep(1)
    
    def _quantum_processor_loop(self):
        """Quantum processor loop"""
        logger.info("Quantum processor loop started")
        
        while self.running and not self.stop_event.is_set():
            try:
                # Market data olish
                if not self.market_data_queue.empty():
                    market_data = self.market_data_queue.get_nowait()
                    
                    # Quantum processing
                    future = self.quantum_workers.submit(
                        self.quantum_processor.process_market_data,
                        market_data
                    )
                    
                    result = future.result(timeout=config.quantum_config.circuit_timeout)
                    
                    if result:
                        # Quantum results queue'ga qo'yish
                        if not self.quantum_results_queue.full():
                            self.quantum_results_queue.put_nowait(result)
                
                time.sleep(0.01)  # 10ms sleep
                
            except Exception as e:
                logger.error(f"Quantum processor error: {str(e)}")
                self.error_handler.handle_error(e, "quantum_processor_loop")
                time.sleep(1)
    
    def _arbitrage_detector_loop(self):
        """Arbitrage detector loop"""
        logger.info("Arbitrage detector loop started")
        
        while self.running and not self.stop_event.is_set():
            try:
                # Quantum results olish
                if not self.quantum_results_queue.empty():
                    quantum_results = self.quantum_results_queue.get_nowait()
                    
                    # Classical postprocessing
                    classical_results = self.postprocessor.process_quantum_results(quantum_results)
                    
                    # Arbitrage opportunities detection
                    opportunities = self.detector.detect_opportunities(classical_results)
                    
                    if opportunities:
                        # Opportunities queue'ga qo'yish
                        for opportunity in opportunities:
                            if not self.opportunities_queue.full():
                                self.opportunities_queue.put_nowait(opportunity)
                                self.metrics.total_opportunities += 1
                
                time.sleep(0.005)  # 5ms sleep
                
            except Exception as e:
                logger.error(f"Arbitrage detector error: {str(e)}")
                self.error_handler.handle_error(e, "arbitrage_detector_loop")
                time.sleep(1)
    
    def _arbitrage_executor_loop(self):
        """Arbitrage executor loop"""
        logger.info("Arbitrage executor loop started")
        
        while self.running and not self.stop_event.is_set():
            try:
                # Opportunity olish
                if not self.opportunities_queue.empty():
                    opportunity = self.opportunities_queue.get_nowait()
                    
                    # Execute trade
                    future = self.executor_workers.submit(
                        self.executor.execute_arbitrage,
                        opportunity
                    )
                    
                    result = future.result(timeout=config.arbitrage_config.max_execution_time)
                    
                    if result and result.success:
                        self.metrics.executed_trades += 1
                        self.metrics.total_profit += result.profit
                        
                        # Audit trail
                        self._log_execution(result)
                
                time.sleep(0.001)  # 1ms sleep
                
            except Exception as e:
                logger.error(f"Arbitrage executor error: {str(e)}")
                self.error_handler.handle_error(e, "arbitrage_executor_loop")
                time.sleep(0.5)
    
    def _performance_tracker(self):
        """Performance tracker thread"""
        logger.info("Performance tracker started")
        
        while self.running and not self.stop_event.is_set():
            try:
                # Metrics update
                self.metrics.last_update = datetime.now(timezone.utc)
                self.metrics.uptime = (datetime.now(timezone.utc) - self.metrics.start_time).total_seconds()
                
                # System status log
                status = self.get_status()
                logger.debug(f"System status: {json.dumps(status, indent=2, default=str)}")
                
                # Monitoring system update
                self.monitor.update_metrics(self.metrics)
                
                time.sleep(1)  # 1 second interval
                
            except Exception as e:
                logger.error(f"Performance tracker error: {str(e)}")
                time.sleep(1)
    
    def _log_execution(self, result):
        """Trade execution loglash"""
        try:
            audit_log = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'type': 'arbitrage_execution',
                'opportunity_id': result.opportunity_id,
                'profit': result.profit,
                'success': result.success,
                'execution_time': result.execution_time,
                'currencies': result.currencies
            }
            
            # Database'ga save qilish
            self.monitor.save_audit_log(audit_log)
            
        except Exception as e:
            logger.error(f"Audit logging error: {str(e)}")
    
    def _save_final_metrics(self):
        """Final metrics saqlash"""
        try:
            final_metrics = {
                'end_time': datetime.now(timezone.utc).isoformat(),
                'total_uptime': self.metrics.uptime,
                'total_opportunities': self.metrics.total_opportunities,
                'executed_trades': self.metrics.executed_trades,
                'total_profit': self.metrics.total_profit,
                'average_profit_per_trade': self.metrics.total_profit / max(self.metrics.executed_trades, 1)
            }
            
            with open('system_final_metrics.json', 'w') as f:
                json.dump(final_metrics, f, indent=2, default=str)
                
            logger.info(f"Final metrics saved: {final_metrics}")
            
        except Exception as e:
            logger.error(f"Failed to save final metrics: {str(e)}")


# Global tizim instance
system = None

def initialize_system() -> bool:
    """Global tizimni inicializatsiya qilish"""
    global system
    try:
        system = HybridQuantumForexSystem()
        return system.initialize()
    except Exception as e:
        logger.error(f"System initialization failed: {str(e)}")
        return False

def start_system() -> bool:
    """Global tizimni ishga tushirish"""
    global system
    if system is None:
        logger.error("System not initialized")
        return False
    return system.start()

def stop_system() -> bool:
    """Global tizimni to'xtatish"""
    global system
    if system is None:
        return False
    return system.stop()

def get_system_status() -> Dict[str, Any]:
    """Global tizim statusini olish"""
    global system
    if system is None:
        return {'error': 'System not initialized'}
    return system.get_status()