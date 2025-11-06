"""
Error Handling Module
Xatoliklarni boshqarish moduli
"""
import logging
import traceback
import sys
import asyncio
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone
import json
import threading
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Xatolik darajalari"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Xatolik kategoriyalari"""
    QUANTUM_COMPUTING = "quantum_computing"
    NETWORK = "network"
    DATA_PROCESSING = "data_processing"
    EXECUTION = "execution"
    SYSTEM = "system"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"

@dataclass
class ErrorRecord:
    """Xatolik yozuvi"""
    timestamp: datetime
    error_type: str
    message: str
    severity: ErrorSeverity
    category: ErrorCategory
    component: str
    context: Dict[str, Any]
    stack_trace: str
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    recovery_attempts: int = 0

class ErrorHandler:
    """
    Comprehensive Error Handling System
    Keng qamrovli xatolik boshqaruvchi tizim
    """
    
    def __init__(self):
        self.error_history = []
        self.error_counts = {}
        self.recovery_strategies = {}
        self.alert_callbacks = []
        self.error_callbacks = []
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Error tracking
        self.max_error_history = 1000
        self.error_rate_window = 3600  # 1 hour
        self.rate_limit_threshold = 100  # Max errors per window
        
        # Recovery settings
        self.max_retry_attempts = 3
        self.retry_backoff_factor = 2
        
        # Initialize error patterns
        self._initialize_error_patterns()
        
        # Setup logging
        self._setup_error_logging()
        
        logger.info("Error Handler initialized")
    
    def _initialize_error_patterns(self):
        """Initialize error patterns and recovery strategies"""
        self.error_patterns = {
            'quantum_backend_error': {
                'category': ErrorCategory.QUANTUM_COMPUTING,
                'severity': ErrorSeverity.HIGH,
                'recovery_strategy': self._recover_quantum_backend,
                'retry_count': 3
            },
            'network_timeout': {
                'category': ErrorCategory.NETWORK,
                'severity': ErrorSeverity.MEDIUM,
                'recovery_strategy': self._recover_network_connection,
                'retry_count': 5
            },
            'data_validation_error': {
                'category': ErrorCategory.VALIDATION,
                'severity': ErrorSeverity.LOW,
                'recovery_strategy': self._recover_data_validation,
                'retry_count': 1
            },
            'execution_timeout': {
                'category': ErrorCategory.EXECUTION,
                'severity': ErrorSeverity.MEDIUM,
                'recovery_strategy': self._recover_execution_timeout,
                'retry_count': 2
            },
            'system_resource_error': {
                'category': ErrorCategory.SYSTEM,
                'severity': ErrorSeverity.HIGH,
                'recovery_strategy': self._recover_system_resources,
                'retry_count': 1
            }
        }
    
    def _setup_error_logging(self):
        """Setup dedicated error logging"""
        self.error_logger = logging.getLogger('hybrid_quantum_forex.errors')
        
        # Create file handler for error logs
        error_handler = logging.FileHandler('error_log.txt')
        error_handler.setLevel(logging.ERROR)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        error_handler.setFormatter(formatter)
        
        self.error_logger.addHandler(error_handler)
    
    def handle_error(self, error: Exception, component: str = "unknown", context: Dict[str, Any] = None) -> bool:
        """
        Handle and process errors
        Xatoliklarni qayta ishlash va boshqarish
        """
        try:
            # Extract error information
            error_info = self._extract_error_info(error, component, context)
            
            # Record error
            with self._lock:
                self._record_error(error_info)
            
            # Log error
            self._log_error(error_info)
            
            # Check error rate
            if self._is_error_rate_high(component):
                self._trigger_high_error_rate_alert(component)
            
            # Attempt recovery
            recovery_success = self._attempt_recovery(error_info)
            
            # Trigger callbacks
            self._trigger_error_callbacks(error_info)
            
            return recovery_success
            
        except Exception as e:
            self.error_logger.error(f"Error handler failed: {e}")
            return False
    
    def _extract_error_info(self, error: Exception, component: str, context: Dict[str, Any] = None) -> ErrorRecord:
        """Extract detailed error information"""
        error_type = type(error).__name__
        message = str(error)
        
        # Determine error category and severity
        category, severity = self._classify_error(error_type)
        
        # Get stack trace
        stack_trace = traceback.format_exc()
        
        return ErrorRecord(
            timestamp=datetime.now(timezone.utc),
            error_type=error_type,
            message=message,
            severity=severity,
            category=category,
            component=component,
            context=context or {},
            stack_trace=stack_trace
        )
    
    def _classify_error(self, error_type: str) -> tuple[ErrorCategory, ErrorSeverity]:
        """Classify error into category and severity"""
        # Pattern matching for error classification
        if any(keyword in error_type.lower() for keyword in ['quantum', 'qiskit', 'circuit']):
            return ErrorCategory.QUANTUM_COMPUTING, ErrorSeverity.HIGH
        elif any(keyword in error_type.lower() for keyword in ['timeout', 'connection', 'network']):
            return ErrorCategory.NETWORK, ErrorSeverity.MEDIUM
        elif any(keyword in error_type.lower() for keyword in ['validation', 'parsing']):
            return ErrorCategory.VALIDATION, ErrorSeverity.LOW
        elif any(keyword in error_type.lower() for keyword in ['execution', 'trade']):
            return ErrorCategory.EXECUTION, ErrorSeverity.MEDIUM
        elif any(keyword in error_type.lower() for keyword in ['memory', 'cpu', 'disk']):
            return ErrorCategory.SYSTEM, ErrorSeverity.HIGH
        elif any(keyword in error_type.lower() for keyword in ['config', 'setting']):
            return ErrorCategory.CONFIGURATION, ErrorSeverity.MEDIUM
        else:
            return ErrorCategory.SYSTEM, ErrorSeverity.MEDIUM
    
    def _record_error(self, error_info: ErrorRecord):
        """Record error in history"""
        # Add to error history
        self.error_history.append(error_info)
        
        # Update error counts
        error_key = f"{error_info.component}_{error_info.error_type}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Maintain history size
        if len(self.error_history) > self.max_error_history:
            self.error_history = self.error_history[-self.max_error_history:]
    
    def _log_error(self, error_info: ErrorRecord):
        """Log error with appropriate level"""
        log_message = f"[{error_info.component}] {error_info.error_type}: {error_info.message}"
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.error_logger.critical(log_message)
            self.error_logger.critical(error_info.stack_trace)
        elif error_info.severity == ErrorSeverity.HIGH:
            self.error_logger.error(log_message)
            self.error_logger.error(error_info.stack_trace)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.error_logger.warning(log_message)
        else:
            self.error_logger.info(log_message)
    
    def _is_error_rate_high(self, component: str) -> bool:
        """Check if error rate is high for component"""
        try:
            current_time = datetime.now(timezone.utc)
            window_start = current_time.timestamp() - self.error_rate_window
            
            # Count errors in time window
            recent_errors = [
                error for error in self.error_history[-100:]  # Check last 100 errors
                if (error.component == component and 
                    error.timestamp.timestamp() > window_start)
            ]
            
            error_rate = len(recent_errors)
            return error_rate > self.rate_limit_threshold
            
        except Exception as e:
            self.error_logger.error(f"Error rate check failed: {e}")
            return False
    
    def _trigger_high_error_rate_alert(self, component: str):
        """Trigger alert for high error rate"""
        alert_message = f"High error rate detected in {component}: {self.rate_limit_threshold}+ errors/hour"
        
        self.error_logger.warning(alert_message)
        
        # Trigger alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback('HIGH_ERROR_RATE', alert_message, {'component': component})
            except Exception as e:
                self.error_logger.error(f"Alert callback failed: {e}")
    
    def _attempt_recovery(self, error_info: ErrorRecord) -> bool:
        """Attempt to recover from error"""
        try:
            # Find matching error pattern
            pattern = self._find_error_pattern(error_info)
            
            if pattern:
                recovery_strategy = pattern['recovery_strategy']
                max_retries = pattern['retry_count']
                
                # Check if already retried too many times
                if error_info.recovery_attempts >= max_retries:
                    self.error_logger.warning(f"Max recovery attempts reached for {error_info.error_type}")
                    return False
                
                # Execute recovery strategy
                recovery_success = recovery_strategy(error_info)
                
                if recovery_success:
                    error_info.resolved = True
                    error_info.resolution_time = datetime.now(timezone.utc)
                    self.error_logger.info(f"Successfully recovered from {error_info.error_type}")
                else:
                    error_info.recovery_attempts += 1
                    self.error_logger.warning(f"Recovery attempt {error_info.recovery_attempts} failed for {error_info.error_type}")
                
                return recovery_success
            
            return False
            
        except Exception as e:
            self.error_logger.error(f"Recovery attempt failed: {e}")
            return False
    
    def _find_error_pattern(self, error_info: ErrorRecord) -> Optional[Dict[str, Any]]:
        """Find matching error pattern"""
        for pattern_name, pattern in self.error_patterns.items():
            if (pattern_name in error_info.error_type.lower() or 
                any(keyword in error_info.error_type.lower() for keyword in pattern_name.split('_'))):
                return pattern
        
        return None
    
    def _trigger_error_callbacks(self, error_info: ErrorRecord):
        """Trigger registered error callbacks"""
        for callback in self.error_callbacks:
            try:
                callback(error_info)
            except Exception as e:
                self.error_logger.error(f"Error callback failed: {e}")
    
    def register_alert_callback(self, callback: Callable):
        """Register alert callback"""
        self.alert_callbacks.append(callback)
    
    def register_error_callback(self, callback: Callable):
        """Register error callback"""
        self.error_callbacks.append(callback)
    
    def setup_error_handling(self):
        """Setup global error handling"""
        # Setup unhandled exception handler
        def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            error = Exception(exc_value)
            self.handle_error(error, "unhandled_exception", {
                'exception_type': exc_type.__name__,
                'traceback': traceback.format_tb(exc_traceback)
            })
        
        sys.excepthook = handle_unhandled_exception
        
        # Setup async error handler
        def handle_async_exception(loop, context):
            error = Exception(context.get('message', 'Unknown async error'))
            self.handle_error(error, "async_context", context)
        
        # Note: This would be setup differently in actual asyncio environment
        # asyncio.get_event_loop().set_exception_handler(handle_async_exception)
        
        logger.info("Global error handling configured")
    
    # Recovery strategies
    def _recover_quantum_backend(self, error_info: ErrorRecord) -> bool:
        """Recover from quantum backend errors"""
        try:
            # Reset quantum backend connection
            self.error_logger.info("Attempting quantum backend recovery...")
            
            # Add delay before retry
            time.sleep(2 ** error_info.recovery_attempts)
            
            # Test quantum backend connection
            # In real implementation, would ping quantum backend
            return True  # Assume recovery successful for demo
            
        except Exception as e:
            self.error_logger.error(f"Quantum backend recovery failed: {e}")
            return False
    
    def _recover_network_connection(self, error_info: ErrorRecord) -> bool:
        """Recover from network connection errors"""
        try:
            # Exponential backoff
            delay = self.retry_backoff_factor ** error_info.recovery_attempts
            time.sleep(delay)
            
            # Test network connection
            # In real implementation, would test connection to external APIs
            return True  # Assume recovery successful for demo
            
        except Exception as e:
            self.error_logger.error(f"Network recovery failed: {e}")
            return False
    
    def _recover_data_validation(self, error_info: ErrorRecord) -> bool:
        """Recover from data validation errors"""
        try:
            # Try to clean or validate data
            self.error_logger.info("Attempting data validation recovery...")
            
            # Validate input data
            if 'data' in error_info.context:
                cleaned_data = self._clean_data(error_info.context['data'])
                if cleaned_data:
                    return True
            
            return False
            
        except Exception as e:
            self.error_logger.error(f"Data validation recovery failed: {e}")
            return False
    
    def _recover_execution_timeout(self, error_info: ErrorRecord) -> bool:
        """Recover from execution timeout errors"""
        try:
            # Increase timeout or optimize execution
            self.error_logger.info("Attempting execution timeout recovery...")
            
            # Could implement timeout extension logic here
            return False  # Timeouts typically need manual intervention
            
        except Exception as e:
            self.error_logger.error(f"Execution timeout recovery failed: {e}")
            return False
    
    def _recover_system_resources(self, error_info: ErrorRecord) -> bool:
        """Recover from system resource errors"""
        try:
            # Free up resources
            self.error_logger.info("Attempting system resource recovery...")
            
            # Clear caches
            import gc
            gc.collect()
            
            # Check memory usage
            import psutil
            memory_info = psutil.virtual_memory()
            
            if memory_info.percent > 90:
                self.error_logger.warning(f"High memory usage: {memory_info.percent:.1f}%")
                return False
            
            return True
            
        except Exception as e:
            self.error_logger.error(f"System resource recovery failed: {e}")
            return False
    
    def _clean_data(self, data: Any) -> Any:
        """Clean and validate data"""
        try:
            if isinstance(data, dict):
                # Remove None values and empty strings
                cleaned = {}
                for key, value in data.items():
                    if value is not None and value != "":
                        cleaned[key] = value
                return cleaned
            elif isinstance(data, str):
                return data.strip() if data.strip() else None
            else:
                return data
        except Exception:
            return data
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        with self._lock:
            total_errors = len(self.error_history)
            
            if total_errors == 0:
                return {
                    'total_errors': 0,
                    'error_rate': 0.0,
                    'top_components': [],
                    'error_categories': {},
                    'resolution_rate': 0.0
                }
            
            # Error rate (errors per hour)
            current_time = datetime.now(timezone.utc)
            oldest_error = min(error.timestamp for error in self.error_history)
            time_span_hours = (current_time - oldest_error).total_seconds() / 3600
            error_rate = total_errors / max(time_span_hours, 1)
            
            # Top error components
            component_counts = {}
            for error in self.error_history:
                component_counts[error.component] = component_counts.get(error.component, 0) + 1
            
            top_components = sorted(component_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Error categories
            category_counts = {}
            for error in self.error_history:
                category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
            
            # Resolution rate
            resolved_errors = sum(1 for error in self.error_history if error.resolved)
            resolution_rate = (resolved_errors / total_errors) * 100
            
            return {
                'total_errors': total_errors,
                'error_rate': error_rate,
                'top_components': top_components,
                'error_categories': category_counts,
                'resolution_rate': resolution_rate,
                'recent_errors': [
                    {
                        'timestamp': error.timestamp.isoformat(),
                        'component': error.component,
                        'error_type': error.error_type,
                        'severity': error.severity.value,
                        'resolved': error.resolved
                    }
                    for error in self.error_history[-10:]  # Last 10 errors
                ]
            }
    
    def clear_error_history(self):
        """Clear error history"""
        with self._lock:
            self.error_history.clear()
            self.error_counts.clear()
            logger.info("Error history cleared")
    
    def export_error_report(self, filename: str = None) -> str:
        """Export error report to file"""
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"error_report_{timestamp}.json"
            
            report = {
                'export_timestamp': datetime.now(timezone.utc).isoformat(),
                'statistics': self.get_error_statistics(),
                'error_history': [
                    {
                        'timestamp': error.timestamp.isoformat(),
                        'error_type': error.error_type,
                        'message': error.message,
                        'severity': error.severity.value,
                        'category': error.category.value,
                        'component': error.component,
                        'context': error.context,
                        'resolved': error.resolved,
                        'resolution_time': error.resolution_time.isoformat() if error.resolution_time else None
                    }
                    for error in self.error_history
                ]
            }
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Error report exported to {filename}")
            return filename
            
        except Exception as e:
            self.error_logger.error(f"Failed to export error report: {e}")
            return ""


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self._lock:
            if self.state == 'OPEN':
                if self._should_attempt_reset():
                    self.state = 'HALF_OPEN'
                else:
                    raise Exception("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time > self.recovery_timeout
        )
    
    def _on_success(self):
        """Handle successful execution"""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
    
    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state"""
        return {
            'state': self.state,
            'failure_count': self.failure_count,
            'failure_threshold': self.failure_threshold,
            'recovery_timeout': self.recovery_timeout,
            'last_failure_time': self.last_failure_time
        }