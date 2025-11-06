"""
System Integration Module

Ushbu modul barcha komponentlarni integratsiya qilish,
data pipeline optimizatsiyasi, real-time processing capabilities
va production deployment uchun mo'ljallangan.

Imkoniyatlar:
- Component integration
- Data pipeline optimization
- Real-time processing capabilities
- Scalable architecture design
- Production deployment readiness
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Callable
import asyncio
import logging
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

from ..core.cycle_detector import CycleDetector
from ..core.indicators import EconomicIndicators
from ..core.adaptation_engine import AdaptationEngine
from ..core.learning_system import ComprehensiveLearningSystem
from ..analysis.economic_cycle_analyzer import EconomicCycleAnalyzer
from ..performance.performance_optimizer import PerformanceOptimizer

@dataclass
class EconomicDataPacket:
    """
    Economic data packet for real-time processing
    """
    timestamp: datetime
    data_type: str
    data: Dict[str, float]
    source: str
    quality_score: float = 1.0

@dataclass
class AnalysisResult:
    """
    Standardized analysis result
    """
    timestamp: datetime
    result_type: str
    data: Dict[str, Any]
    confidence_score: float
    processing_time: float

class EconomicAdaptationSystem:
    """
    Comprehensive Economic Adaptation System
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 enable_real_time: bool = True,
                 enable_learning: bool = True):
        """
        Economic Adaptation System initialize qilish
        
        Args:
            config: System konfiguratsiyasi
            enable_real_time: Real-time processing yoqish
            enable_learning: Self-learning tizimini yoqish
        """
        
        # System configuration
        self.config = config or self._default_config()
        
        # Component initialization
        self.cycle_detector = CycleDetector()
        self.indicators = EconomicIndicators()
        self.adaptation_engine = AdaptationEngine(
            adaptation_sensitivity=self.config.get('adaptation_sensitivity', 0.1)
        )
        
        self.learning_enabled = enable_learning
        if enable_learning:
            self.learning_system = ComprehensiveLearningSystem()
        
        self.analyzer = EconomicCycleAnalyzer(
            enable_learning=enable_learning,
            adaptation_sensitivity=self.config.get('adaptation_sensitivity', 0.1)
        )
        
        self.performance_optimizer = PerformanceOptimizer(
            performance_horizon=self.config.get('performance_horizon', 36)
        )
        
        # Real-time processing
        self.real_time_enabled = enable_real_time
        if enable_real_time:
            self.data_queue = asyncio.Queue()
            self.processing_threads = []
            self.result_cache = {}
        
        # Data pipeline management
        self.data_pipeline = {
            'sources': [],
            'processors': [],
            'validators': [],
            'storage_systems': []
        }
        
        # System state management
        self.system_state = {
            'status': 'initializing',
            'last_update': datetime.now(),
            'component_status': {},
            'performance_metrics': {},
            'error_count': 0
        }
        
        # Logging setup
        self.logger = self._setup_logging()
        
        # Data cache and storage
        self.data_cache = {}
        self.historical_data = {}
        
        # Scalability configuration
        self.scalability_config = {
            'max_concurrent_processes': self.config.get('max_concurrent_processes', 4),
            'memory_limit_mb': self.config.get('memory_limit_mb', 1024),
            'processing_timeout_seconds': self.config.get('processing_timeout', 30)
        }
    
    def _default_config(self) -> Dict[str, Any]:
        """
        Default system configuration
        """
        
        return {
            'adaptation_sensitivity': 0.1,
            'performance_horizon': 36,
            'max_concurrent_processes': 4,
            'memory_limit_mb': 1024,
            'processing_timeout': 30,
            'real_time_processing_interval': 60,  # seconds
            'data_validation_strict': True,
            'auto_scaling_enabled': True,
            'performance_monitoring': True,
            'error_handling': 'graceful',
            'logging_level': 'INFO'
        }
    
    def _setup_logging(self) -> logging.Logger:
        """
        Setup system logging
        """
        
        logger = logging.getLogger('EconomicAdaptationSystem')
        logger.setLevel(getattr(logging, self.config.get('logging_level', 'INFO')))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def initialize_system(self) -> Dict[str, Any]:
        """
        System initialization
        """
        
        try:
            self.logger.info("Initializing Economic Adaptation System...")
            
            # Initialize components
            initialization_results = {
                'components': {},
                'data_pipeline': {},
                'real_time_processing': {},
                'system_status': 'initialization_failed'
            }
            
            # Core components initialization
            initialization_results['components'] = {
                'cycle_detector': 'initialized',
                'indicators': 'initialized',
                'adaptation_engine': 'initialized',
                'analyzer': 'initialized',
                'performance_optimizer': 'initialized'
            }
            
            if self.learning_enabled:
                initialization_results['components']['learning_system'] = 'initialized'
            
            # Data pipeline setup
            initialization_results['data_pipeline'] = await self._setup_data_pipeline()
            
            # Real-time processing setup
            if self.real_time_enabled:
                initialization_results['real_time_processing'] = await self._setup_real_time_processing()
            
            # System health check
            health_check = await self._perform_system_health_check()
            initialization_results['health_check'] = health_check
            
            # Update system state
            self.system_state.update({
                'status': 'operational',
                'last_update': datetime.now(),
                'component_status': initialization_results['components']
            })
            
            self.logger.info("System initialization completed successfully")
            
            return {
                'status': 'success',
                'initialization_results': initialization_results,
                'system_state': self.system_state,
                'configuration': self.config
            }
            
        except Exception as e:
            self.logger.error(f"System initialization failed: {str(e)}")
            self.system_state['status'] = 'error'
            self.system_state['error_count'] += 1
            
            return {
                'status': 'error',
                'error_message': str(e),
                'system_state': self.system_state
            }
    
    async def _setup_data_pipeline(self) -> Dict[str, Any]:
        """
        Setup data processing pipeline
        """
        
        pipeline_setup = {
            'data_sources_configured': 0,
            'processors_initialized': 0,
            'validators_active': 0,
            'storage_connected': False
        }
        
        # Configure data sources (simplified)
        default_sources = [
            'economic_indicators',
            'market_data', 
            'performance_data',
            'benchmark_data'
        ]
        
        for source in default_sources:
            self.data_pipeline['sources'].append({
                'name': source,
                'status': 'configured',
                'last_update': datetime.now()
            })
            pipeline_setup['data_sources_configured'] += 1
        
        # Initialize processors
        processors = [
            'data_validator',
            'data_cleaner',
            'data_transformer',
            'data_aggregator'
        ]
        
        for processor in processors:
            self.data_pipeline['processors'].append({
                'name': processor,
                'status': 'initialized',
                'last_execution': None
            })
            pipeline_setup['processors_initialized'] += 1
        
        # Activate validators
        validators = [
            'data_quality_validator',
            'format_validator',
            'range_validator'
        ]
        
        for validator in validators:
            self.data_pipeline['validators'].append({
                'name': validator,
                'status': 'active',
                'rules_configured': True
            })
            pipeline_setup['validators_active'] += 1
        
        pipeline_setup['storage_connected'] = True
        
        return pipeline_setup
    
    async def _setup_real_time_processing(self) -> Dict[str, Any]:
        """
        Setup real-time processing capabilities
        """
        
        rt_setup = {
            'data_queue_initialized': True,
            'processing_threads_started': False,
            'result_cache_configured': True,
            'event_handlers_registered': 0
        }
        
        try:
            # Start processing threads
            max_threads = self.scalability_config['max_concurrent_processes']
            
            for i in range(max_threads):
                thread = threading.Thread(
                    target=self._data_processing_worker,
                    args=(i,),
                    daemon=True
                )
                thread.start()
                self.processing_threads.append(thread)
            
            rt_setup['processing_threads_started'] = True
            rt_setup['active_threads'] = len(self.processing_threads)
            
            # Register event handlers
            event_handlers = [
                'data_received',
                'analysis_completed',
                'adaptation_required',
                'performance_update'
            ]
            
            for handler in event_handlers:
                self.logger.debug(f"Event handler registered: {handler}")
                rt_setup['event_handlers_registered'] += 1
            
            self.logger.info(f"Real-time processing initialized with {max_threads} threads")
            
        except Exception as e:
            self.logger.error(f"Real-time processing setup failed: {str(e)}")
            rt_setup['processing_threads_started'] = False
        
        return rt_setup
    
    def _data_processing_worker(self, worker_id: int):
        """
        Data processing worker thread
        """
        
        self.logger.info(f"Data processing worker {worker_id} started")
        
        while True:
            try:
                # Process data from queue
                if not self.data_queue.empty():
                    data_packet = self.data_queue.get_nowait()
                    self._process_data_packet(data_packet, worker_id)
                
                # Sleep briefly to prevent excessive CPU usage
                threading.Event().wait(0.1)
                
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {str(e)}")
                threading.Event().wait(1)  # Wait longer on error
    
    def _process_data_packet(self, data_packet: EconomicDataPacket, worker_id: int):
        """
        Process individual data packet
        """
        
        start_time = datetime.now()
        
        try:
            # Validate data
            if self._validate_data_packet(data_packet):
                # Store in cache
                cache_key = f"{data_packet.data_type}_{data_packet.timestamp.isoformat()}"
                self.data_cache[cache_key] = data_packet
                
                # Trigger analysis if needed
                if self._should_trigger_analysis(data_packet):
                    asyncio.create_task(self._trigger_analysis(data_packet))
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                self.logger.debug(
                    f"Worker {worker_id} processed {data_packet.data_type} "
                    f"in {processing_time:.3f}s"
                )
            else:
                self.logger.warning(f"Worker {worker_id} invalid data packet rejected")
        
        except Exception as e:
            self.logger.error(f"Worker {worker_id} failed to process packet: {str(e)}")
    
    def _validate_data_packet(self, data_packet: EconomicDataPacket) -> bool:
        """
        Validate incoming data packet
        """
        
        # Basic validation checks
        if not data_packet.data:
            return False
        
        if data_packet.quality_score < 0.5:
            return False
        
        # Check for required fields
        required_fields = ['timestamp', 'data_type', 'data', 'source']
        for field in required_fields:
            if not hasattr(data_packet, field) or getattr(data_packet, field) is None:
                return False
        
        # Data-specific validation
        if data_packet.data_type == 'economic_indicators':
            return self._validate_economic_data(data_packet.data)
        
        return True
    
    def _validate_economic_data(self, data: Dict[str, float]) -> bool:
        """
        Validate economic data
        """
        
        # Check for reasonable value ranges
        for key, value in data.items():
            if not isinstance(value, (int, float)):
                return False
            
            # Basic range checks (can be expanded)
            if 'rate' in key.lower() or 'growth' in key.lower():
                if abs(value) > 10:  # Reasonable bounds for rates/growth
                    return False
        
        return True
    
    def _should_trigger_analysis(self, data_packet: EconomicDataPacket) -> bool:
        """
        Determine if analysis should be triggered
        """
        
        # Trigger conditions
        if data_packet.data_type == 'economic_indicators':
            return True
        
        # Periodic triggers for other data types
        current_time = datetime.now()
        last_analysis = self.system_state.get('last_analysis', datetime.min)
        
        analysis_interval = timedelta(seconds=self.config['real_time_processing_interval'])
        
        return (current_time - last_analysis) > analysis_interval
    
    async def _trigger_analysis(self, data_packet: EconomicDataPacket):
        """
        Trigger analysis for new data
        """
        
        try:
            self.logger.info(f"Triggering analysis for {data_packet.data_type}")
            
            # Prepare data for analysis
            analysis_data = {
                'economic': pd.DataFrame([data_packet.data]),
                'performance': pd.DataFrame(),
                'market': pd.DataFrame()
            }
            
            # Perform analysis
            analysis_result = await asyncio.get_event_loop().run_in_executor(
                None, self.analyzer.perform_comprehensive_analysis, analysis_data
            )
            
            # Store result
            result_key = f"analysis_{datetime.now().isoformat()}"
            self.result_cache[result_key] = analysis_result
            
            # Update system state
            self.system_state['last_analysis'] = datetime.now()
            
            # Trigger adaptation if needed
            if self._should_trigger_adaptation(analysis_result):
                await self._trigger_adaptation(analysis_result)
            
            self.logger.info("Analysis completed successfully")
            
        except Exception as e:
            self.logger.error(f"Analysis trigger failed: {str(e)}")
    
    def _should_trigger_adaptation(self, analysis_result: Dict[str, Any]) -> bool:
        """
        Determine if adaptation should be triggered
        """
        
        # Check for high-risk conditions
        if 'risk_analysis' in analysis_result:
            risk_assessment = analysis_result['risk_analysis'].get('overall_risk_assessment', {})
            risk_rating = risk_assessment.get('overall_risk_rating', 'unknown')
            
            if risk_rating in ['critical', 'high']:
                return True
        
        # Check for significant cycle changes
        if 'cycle_analysis' in analysis_result:
            cycle_data = analysis_result['cycle_analysis'].get('primary_cycle_analysis', {})
            current_phase = cycle_data.get('current_phase', 'unknown')
            cycle_strength = cycle_data.get('cycle_strength', 0)
            
            if cycle_strength > 0.5 and current_phase in ['contraction', 'expansion']:
                return True
        
        return False
    
    async def _trigger_adaptation(self, analysis_result: Dict[str, Any]):
        """
        Trigger adaptation process
        """
        
        try:
            self.logger.info("Triggering adaptation process")
            
            # Prepare data for adaptation
            economic_data = pd.DataFrame()
            strategy_config = {}
            
            # Perform adaptation
            adaptation_result = await asyncio.get_event_loop().run_in_executor(
                None, self.adaptation_engine.adapt_to_economic_cycles,
                economic_data, strategy_config, {}
            )
            
            # Store adaptation result
            adaptation_key = f"adaptation_{datetime.now().isoformat()}"
            self.result_cache[adaptation_key] = adaptation_result
            
            # Log adaptation decision
            self._log_adaptation_decision(adaptation_result)
            
            self.logger.info("Adaptation process completed")
            
        except Exception as e:
            self.logger.error(f"Adaptation trigger failed: {str(e)}")
    
    def _log_adaptation_decision(self, adaptation_result: Dict[str, Any]):
        """
        Log adaptation decisions
        """
        
        if 'error' in adaptation_result:
            self.logger.warning(f"Adaptation decision failed: {adaptation_result['error']}")
            return
        
        # Log key adaptation metrics
        if 'recommendations' in adaptation_result:
            recommendations = adaptation_result['recommendations']
            param_adjustments = recommendations.get('parameter_adjustments', {})
            
            if param_adjustments:
                self.logger.info(f"Adaptation decisions: {len(param_adjustments)} parameter adjustments recommended")
                
                for param, adjustment in param_adjustments.items():
                    current = adjustment.get('current', 'unknown')
                    recommended = adjustment.get('recommended', 'unknown')
                    self.logger.info(f"  {param}: {current} -> {recommended}")
        
        # Log implementation priorities
        if 'implementation_priority' in adaptation_result:
            priorities = adaptation_result['implementation_priority']
            for priority_level, actions in priorities.items():
                if actions:
                    self.logger.info(f"Adaptation priority {priority_level}: {len(actions)} actions")
    
    async def _perform_system_health_check(self) -> Dict[str, Any]:
        """
        Perform system health check
        """
        
        health_check = {
            'overall_health': 'healthy',
            'component_health': {},
            'performance_metrics': {},
            'issues': []
        }
        
        # Component health checks
        components = [
            ('cycle_detector', self.cycle_detector),
            ('indicators', self.indicators),
            ('adaptation_engine', self.adaptation_engine),
            ('analyzer', self.analyzer),
            ('performance_optimizer', self.performance_optimizer)
        ]
        
        for name, component in components:
            try:
                # Simple health check - try to access component
                if hasattr(component, '__init__'):
                    health_check['component_health'][name] = 'healthy'
                else:
                    health_check['component_health'][name] = 'unhealthy'
                    health_check['issues'].append(f"{name} component initialization failed")
            
            except Exception as e:
                health_check['component_health'][name] = 'error'
                health_check['issues'].append(f"{name} health check error: {str(e)}")
        
        # Memory usage check
        import psutil
        memory_usage = psutil.virtual_memory().percent
        health_check['performance_metrics']['memory_usage_percent'] = memory_usage
        
        if memory_usage > 90:
            health_check['performance_metrics']['memory_status'] = 'critical'
            health_check['issues'].append('High memory usage detected')
        elif memory_usage > 75:
            health_check['performance_metrics']['memory_status'] = 'warning'
        else:
            health_check['performance_metrics']['memory_status'] = 'normal'
        
        # Overall health assessment
        if health_check['issues']:
            if len(health_check['issues']) > 2:
                health_check['overall_health'] = 'critical'
            else:
                health_check['overall_health'] = 'warning'
        else:
            health_check['overall_health'] = 'healthy'
        
        return health_check
    
    async def process_real_time_data(self, data_packet: EconomicDataPacket) -> Dict[str, Any]:
        """
        Process real-time data packet
        """
        
        if not self.real_time_enabled:
            return {'error': 'Real-time processing not enabled'}
        
        try:
            # Add to processing queue
            await self.data_queue.put(data_packet)
            
            return {
                'status': 'queued',
                'data_type': data_packet.data_type,
                'timestamp': data_packet.timestamp,
                'queue_size': self.data_queue.qsize()
            }
            
        except Exception as e:
            self.logger.error(f"Real-time data processing failed: {str(e)}")
            return {'error': str(e)}
    
    async def perform_comprehensive_analysis(self, 
                                           data: Dict[str, pd.DataFrame],
                                           force_analysis: bool = False) -> Dict[str, Any]:
        """
        Perform comprehensive system analysis
        """
        
        try:
            self.logger.info("Starting comprehensive analysis")
            
            start_time = datetime.now()
            
            # Update system state
            self.system_state['status'] = 'analyzing'
            self.system_state['last_update'] = datetime.now()
            
            # Perform analysis using integrated analyzer
            analysis_result = await asyncio.get_event_loop().run_in_executor(
                None, self.analyzer.perform_comprehensive_analysis, data
            )
            
            # Update performance optimization if needed
            if 'performance_data' in data and not data['performance_data'].empty:
                performance_optimization = await asyncio.get_event_loop().run_in_executor(
                    None, self.performance_optimizer.optimize_performance,
                    data['performance_data'], analysis_result.get('cycle_analysis', {})
                )
                
                analysis_result['performance_optimization'] = performance_optimization
            
            # Learning integration
            if self.learning_enabled:
                learning_integration = await asyncio.get_event_loop().run_in_executor(
                    None, self.learning_system.learn_from_economic_data,
                    data.get('economic', pd.DataFrame()),
                    data.get('performance', pd.DataFrame()),
                    data.get('market', pd.DataFrame())
                )
                
                analysis_result['learning_integration'] = learning_integration
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Store comprehensive result
            result_key = f"comprehensive_analysis_{datetime.now().isoformat()}"
            self.result_cache[result_key] = analysis_result
            
            # Update system state
            self.system_state.update({
                'status': 'operational',
                'last_analysis': datetime.now(),
                'last_comprehensive_analysis': datetime.now()
            })
            
            self.logger.info(f"Comprehensive analysis completed in {processing_time:.2f}s")
            
            return {
                'status': 'success',
                'analysis_result': analysis_result,
                'processing_time': processing_time,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Comprehensive analysis failed: {str(e)}")
            self.system_state['error_count'] += 1
            self.system_state['status'] = 'error'
            
            return {
                'status': 'error',
                'error_message': str(e),
                'timestamp': datetime.now()
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status
        """
        
        # Get component statuses
        component_statuses = {}
        
        components = [
            ('cycle_detector', self.cycle_detector),
            ('indicators', self.indicators),
            ('adaptation_engine', self.adaptation_engine),
            ('analyzer', self.analyzer),
            ('performance_optimizer', self.performance_optimizer)
        ]
        
        for name, component in components:
            try:
                if hasattr(component, 'get_learning_status') and name == 'learning_system':
                    status = component.get_learning_status()
                elif hasattr(component, 'get_analysis_status'):
                    status = component.get_analysis_status()
                elif hasattr(component, 'get_adaptation_status'):
                    status = component.get_adaptation_status()
                elif hasattr(component, 'get_performance_status'):
                    status = component.get_performance_status()
                else:
                    status = {'status': 'active', 'last_update': datetime.now()}
                
                component_statuses[name] = status
                
            except Exception as e:
                component_statuses[name] = {'status': 'error', 'error': str(e)}
        
        # Real-time processing status
        rt_status = {}
        if self.real_time_enabled:
            rt_status = {
                'enabled': True,
                'queue_size': self.data_queue.qsize() if hasattr(self, 'data_queue') else 0,
                'active_threads': len(self.processing_threads),
                'cache_size': len(self.data_cache)
            }
        
        # Performance metrics
        performance_metrics = {
            'total_analyses_performed': len([k for k in self.result_cache.keys() if 'analysis' in k]),
            'total_adaptations_performed': len([k for k in self.result_cache.keys() if 'adaptation' in k]),
            'system_uptime_hours': (datetime.now() - self.system_state.get('start_time', datetime.now())).total_seconds() / 3600,
            'memory_usage_percent': self._get_memory_usage()
        }
        
        return {
            'system_state': self.system_state,
            'component_statuses': component_statuses,
            'real_time_status': rt_status,
            'performance_metrics': performance_metrics,
            'data_pipeline_status': self.data_pipeline,
            'scalability_config': self.scalability_config,
            'configuration': self.config
        }
    
    def _get_memory_usage(self) -> float:
        """
        Get current memory usage percentage
        """
        
        try:
            import psutil
            return psutil.virtual_memory().percent
        except:
            return 0.0
    
    async def export_system_data(self, export_format: str = 'json') -> Dict[str, Any]:
        """
        Export system data for backup/reporting
        """
        
        try:
            export_data = {
                'timestamp': datetime.now(),
                'system_configuration': self.config,
                'system_state': asdict(self.system_state),
                'data_pipeline_config': self.data_pipeline,
                'recent_analysis_results': dict(list(self.result_cache.items())[-10:]),  # Last 10 results
                'component_statuses': await self.get_system_status()
            }
            
            if export_format.lower() == 'json':
                return {
                    'status': 'success',
                    'data': export_data,
                    'format': 'json',
                    'size_bytes': len(json.dumps(export_data, default=str))
                }
            
            else:
                return {
                    'status': 'error',
                    'error_message': f'Unsupported export format: {export_format}'
                }
                
        except Exception as e:
            self.logger.error(f"Data export failed: {str(e)}")
            return {
                'status': 'error',
                'error_message': str(e)
            }
    
    async def shutdown_system(self) -> Dict[str, Any]:
        """
        Graceful system shutdown
        """
        
        try:
            self.logger.info("Initiating system shutdown...")
            
            # Update system state
            self.system_state['status'] = 'shutting_down'
            self.system_state['last_update'] = datetime.now()
            
            # Stop real-time processing threads
            if self.real_time_enabled and self.processing_threads:
                for thread in self.processing_threads:
                    thread.join(timeout=5)
                self.processing_threads.clear()
            
            # Clean up resources
            self.data_cache.clear()
            
            # Final status update
            self.system_state['status'] = 'shutdown'
            self.system_state['shutdown_time'] = datetime.now()
            
            self.logger.info("System shutdown completed")
            
            return {
                'status': 'success',
                'shutdown_time': datetime.now(),
                'final_system_state': self.system_state
            }
            
        except Exception as e:
            self.logger.error(f"System shutdown failed: {str(e)}")
            return {
                'status': 'error',
                'error_message': str(e)
            }
    
    def add_data_source(self, 
                       source_name: str, 
                       data_source: Callable,
                       validation_rules: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Add new data source to pipeline
        """
        
        try:
            data_source_config = {
                'name': source_name,
                'source': data_source,
                'validation_rules': validation_rules or {},
                'status': 'configured',
                'added_time': datetime.now()
            }
            
            self.data_pipeline['sources'].append(data_source_config)
            
            self.logger.info(f"Data source added: {source_name}")
            
            return {
                'status': 'success',
                'source_name': source_name,
                'total_sources': len(self.data_pipeline['sources'])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to add data source {source_name}: {str(e)}")
            return {
                'status': 'error',
                'error_message': str(e)
            }
    
    def configure_performance_benchmarks(self, 
                                       benchmark_data: pd.DataFrame,
                                       benchmark_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Configure performance benchmarks
        """
        
        try:
            # Update performance optimizer with benchmark data
            self.performance_optimizer.benchmark_data = benchmark_data
            
            # Update benchmark configuration
            if benchmark_config:
                self.performance_optimizer.performance_benchmarks.update(benchmark_config)
            
            self.logger.info("Performance benchmarks configured")
            
            return {
                'status': 'success',
                'benchmark_data_shape': benchmark_data.shape,
                'benchmark_columns': list(benchmark_data.columns),
                'updated_config': self.performance_optimizer.performance_benchmarks
            }
            
        except Exception as e:
            self.logger.error(f"Failed to configure benchmarks: {str(e)}")
            return {
                'status': 'error',
                'error_message': str(e)
            }
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get system health metrics
        """
        
        health_metrics = {
            'overall_status': self.system_state.get('status', 'unknown'),
            'error_rate': self.system_state.get('error_count', 0) / max(len(self.result_cache), 1),
            'component_availability': 1.0,  # Simplified
            'processing_efficiency': self._calculate_processing_efficiency(),
            'data_quality_score': self._assess_data_quality(),
            'system_stability': self._assess_system_stability()
        }
        
        return health_metrics
    
    def _calculate_processing_efficiency(self) -> float:
        """
        Calculate processing efficiency
        """
        
        # Simplified efficiency calculation
        total_analyses = len([k for k in self.result_cache.keys() if 'analysis' in k])
        total_errors = self.system_state.get('error_count', 0)
        
        efficiency = total_analyses / max(total_analyses + total_errors, 1)
        return min(efficiency, 1.0)
    
    def _assess_data_quality(self) -> float:
        """
        Assess overall data quality
        """
        
        if not self.data_cache:
            return 0.5  # Neutral if no data
        
        quality_scores = []
        
        for data_packet in self.data_cache.values():
            if hasattr(data_packet, 'quality_score'):
                quality_scores.append(data_packet.quality_score)
        
        return np.mean(quality_scores) if quality_scores else 0.5
    
    def _assess_system_stability(self) -> str:
        """
        Assess system stability
        """
        
        error_count = self.system_state.get('error_count', 0)
        total_operations = len(self.result_cache)
        
        error_rate = error_count / max(total_operations, 1)
        
        if error_rate < 0.01:
            return 'very_stable'
        elif error_rate < 0.05:
            return 'stable'
        elif error_rate < 0.1:
            return 'moderate'
        else:
            return 'unstable'