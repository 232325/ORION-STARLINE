#!/usr/bin/env python3
"""
Structured Logging System
Centralized logging, aggregation, va retention policies
"""

import time
import json
import logging
import threading
import os
import gzip
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict, field
from contextlib import contextmanager
from functools import wraps
import queue
import weakref
from enum import Enum
import hashlib

class LogLevel(Enum):
    """Log darajasi"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class LogFormat(Enum):
    """Log formatlari"""
    JSON = "json"
    TEXT = "text"
    KEY_VALUE = "key_value"

@dataclass
class LogRecord:
    """Structured log record"""
    timestamp: str
    level: LogLevel
    service: str
    component: str
    message: str
    logger_name: str
    module: str
    function: str
    line_number: int
    thread_id: int
    process_id: int
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    exception_info: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Dictionary ga o'tkazish"""
        data = asdict(self)
        data['level'] = self.level.value
        return data
    
    def to_json(self) -> str:
        """JSON string ga o'tkazish"""
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)
    
    def to_text(self) -> str:
        """Text format ga o'tkazish"""
        base_msg = f"{self.timestamp} [{self.level.value.upper()}] {self.service}.{self.component} {self.message}"
        
        # Qo'shimcha fieldlarni qo'shish
        extras = []
        if self.trace_id:
            extras.append(f"trace_id={self.trace_id}")
        if self.span_id:
            extras.append(f"span_id={self.span_id}")
        if self.user_id:
            extras.append(f"user_id={self.user_id}")
        if self.request_id:
            extras.append(f"request_id={self.request_id}")
        
        if extras:
            base_msg += f" ({', '.join(extras)})"
        
        if self.stack_trace:
            base_msg += f"\n{self.stack_trace}"
        
        return base_msg

class LogFormatter:
    """Log formati"""
    
    def __init__(self, log_format: LogFormat = LogFormat.JSON):
        self.log_format = log_format
    
    def format_record(self, record: LogRecord) -> str:
        """Record ni format qilish"""
        if self.log_format == LogFormat.JSON:
            return record.to_json()
        elif self.log_format == LogFormat.TEXT:
            return record.to_text()
        else:  # KEY_VALUE
            return self._format_key_value(record)
    
    def _format_key_value(self, record: LogRecord) -> str:
        """Key-value format"""
        fields = [
            f"timestamp={record.timestamp}",
            f"level={record.level.value}",
            f"service={record.service}",
            f"component={record.component}",
            f"message={record.message}",
            f"logger={record.logger_name}",
            f"module={record.module}",
            f"function={record.function}",
            f"line={record.line_number}",
            f"thread={record.thread_id}",
            f"process={record.process_id}"
        ]
        
        if record.trace_id:
            fields.append(f"trace_id={record.trace_id}")
        if record.span_id:
            fields.append(f"span_id={record.span_id}")
        if record.user_id:
            fields.append(f"user_id={record.user_id}")
        if record.request_id:
            fields.append(f"request_id={record.request_id}")
        
        for key, value in record.custom_fields.items():
            fields.append(f"{key}={value}")
        
        return " ".join(fields)

class LogAggregator:
    """Log aggregation system"""
    
    def __init__(self, buffer_size: int = 10000, flush_interval: int = 30):
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.log_buffer: List[LogRecord] = []
        self.lock = threading.RLock()
        self.subscribers = []
        self.processors = []
        self.running = False
        self.flush_thread = None
        
        # Stats
        self.total_logs = 0
        self.logs_by_level = {level: 0 for level in LogLevel}
        self.logs_by_component = {}
        self.start_time = time.time()
    
    def start(self):
        """Aggregator ni ishga tushirish"""
        if self.running:
            return
        
        self.running = True
        self.flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self.flush_thread.start()
    
    def stop(self):
        """Aggregator ni to'xtatish"""
        self.running = False
        self.flush()
        if self.flush_thread:
            self.flush_thread.join(timeout=5)
    
    def add_log(self, record: LogRecord):
        """Log qo'shish"""
        with self.lock:
            self.log_buffer.append(record)
            self.total_logs += 1
            self.logs_by_level[record.level] += 1
            
            # Component stats
            component_key = f"{record.service}.{record.component}"
            self.logs_by_component[component_key] = self.logs_by_component.get(component_key, 0) + 1
            
            # Buffer overflow check
            if len(self.log_buffer) >= self.buffer_size:
                self.flush()
    
    def flush(self):
        """Loglarni flush qilish"""
        with self.lock:
            if not self.log_buffer:
                return
            
            logs_to_process = self.log_buffer.copy()
            self.log_buffer.clear()
        
        # Process va export
        for record in logs_to_process:
            self._process_record(record)
    
    def _process_record(self, record: LogRecord):
        """Record ni process qilish"""
        # Subscriberlarga yuborish
        for subscriber in self.subscribers:
            try:
                subscriber.process_log(record)
            except Exception as e:
                logging.error(f"Log subscriber error: {e}")
        
        # Processorchuga yuborish
        for processor in self.processors:
            try:
                processed = processor.process_log(record)
                if processed:
                    record = processed
            except Exception as e:
                logging.error(f"Log processor error: {e}")
    
    def _flush_loop(self):
        """Flush loop"""
        while self.running:
            try:
                time.sleep(self.flush_interval)
                if self.running:
                    self.flush()
            except Exception as e:
                logging.error(f"Flush loop error: {e}")
    
    def add_subscriber(self, subscriber):
        """Subscriber qo'shish"""
        self.subscribers.append(subscriber)
    
    def add_processor(self, processor):
        """Processor qo'shish"""
        self.processors.append(processor)
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistics olish"""
        runtime = time.time() - self.start_time
        return {
            'total_logs': self.total_logs,
            'logs_by_level': {k.value: v for k, v in self.logs_by_level.items()},
            'logs_by_component': self.logs_by_component,
            'buffer_size': len(self.log_buffer),
            'runtime_seconds': runtime,
            'logs_per_second': self.total_logs / runtime if runtime > 0 else 0,
            'active_subscribers': len(self.subscribers),
            'active_processors': len(self.processors)
        }

class LogSubscriber:
    """Log subscriber base class"""
    
    def process_log(self, record: LogRecord):
        """Log ni process qilish"""
        raise NotImplementedError

class FileSubscriber(LogSubscriber):
    """File ga log yozuvchi subscriber"""
    
    def __init__(self, file_path: str, rotation: bool = True, max_size_mb: int = 100,
                 compression: bool = True):
        self.file_path = file_path
        self.rotation = rotation
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.compression = compression
        self.current_file_size = 0
        self.file_lock = threading.Lock()
        
        # Directory yaratish
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    def process_log(self, record: LogRecord):
        """Log ni file ga yozish"""
        try:
            with self.file_lock:
                log_line = record.to_json() + '\n'
                
                # Rotation check
                if (self.rotation and 
                    self.current_file_size + len(log_line.encode('utf-8')) > self.max_size_bytes):
                    self._rotate_file()
                
                with open(self.file_path, 'a', encoding='utf-8') as f:
                    f.write(log_line)
                    self.current_file_size += len(log_line.encode('utf-8'))
        
        except Exception as e:
            logging.error(f"File subscriber error: {e}")
    
    def _rotate_file(self):
        """File rotation"""
        if os.path.exists(self.file_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if self.compression:
                compressed_path = f"{self.file_path}.{timestamp}.gz"
                with open(self.file_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(self.file_path)
            else:
                rotated_path = f"{self.file_path}.{timestamp}"
                shutil.move(self.file_path, rotated_path)
            
            self.current_file_size = 0

class ConsoleSubscriber(LogSubscriber):
    """Console ga log yozuvchi subscriber"""
    
    def __init__(self, min_level: LogLevel = LogLevel.INFO, formatter: LogFormatter = None):
        self.min_level = min_level
        self.formatter = formatter or LogFormatter(LogFormat.TEXT)
        self.lock = threading.Lock()
    
    def process_log(self, record: LogRecord):
        """Log ni console ga chiqarish"""
        if record.level.value < self.min_level.value:
            return
        
        try:
            with self.lock:
                log_line = self.formatter.format_record(record)
                print(log_line)
        except Exception as e:
            logging.error(f"Console subscriber error: {e}")

class SysLogSubscriber(LogSubscriber):
    """SysLog ga log yuboruvchi subscriber"""
    
    def __init__(self, host: str = "localhost", port: int = 514, facility: int = 1):
        import syslog
        self.syslog = syslog
        self.host = host
        self.port = port
        self.facility = facility
    
    def process_log(self, record: LogRecord):
        """Log ni syslog ga yuborish"""
        try:
            priority = self._map_level_to_priority(record.level)
            message = f"{record.service}.{record.component}: {record.message}"
            self.syslog.syslog(priority, message)
        except Exception as e:
            logging.error(f"SysLog subscriber error: {e}")
    
    def _map_level_to_priority(self, level: LogLevel) -> int:
        """Log level ni syslog priority ga o'tkazish"""
        mapping = {
            LogLevel.DEBUG: self.syslog.LOG_DEBUG,
            LogLevel.INFO: self.syslog.LOG_INFO,
            LogLevel.WARNING: self.syslog.LOG_WARNING,
            LogLevel.ERROR: self.syslog.LOG_ERR,
            LogLevel.CRITICAL: self.syslog.LOG_CRIT
        }
        return mapping.get(level, self.syslog.LOG_INFO)

class LogProcessor:
    """Log processor base class"""
    
    def process_log(self, record: LogRecord) -> Optional[LogRecord]:
        """Log ni process qilish"""
        return record

class FilteringProcessor(LogProcessor):
    """Log filter qiluvchi processor"""
    
    def __init__(self, include_levels: Optional[List[LogLevel]] = None,
                 exclude_components: Optional[List[str]] = None,
                 include_components: Optional[List[str]] = None):
        self.include_levels = include_levels
        self.exclude_components = exclude_components or []
        self.include_components = include_components
    
    def process_log(self, record: LogRecord) -> Optional[LogRecord]:
        """Log ni filter qilish"""
        # Level filter
        if self.include_levels and record.level not in self.include_levels:
            return None
        
        # Component filter
        component_key = f"{record.service}.{record.component}"
        
        if self.exclude_components and component_key in self.exclude_components:
            return None
        
        if self.include_components and component_key not in self.include_components:
            return None
        
        return record

class EnrichmentProcessor(LogProcessor):
    """Log ni boyituvchi processor"""
    
    def __init__(self, environment_info: Optional[Dict[str, Any]] = None):
        self.environment_info = environment_info or {}
    
    def process_log(self, record: LogRecord) -> LogRecord:
        """Log ni environment info bilan boyitish"""
        record.custom_fields.update(self.environment_info)
        return record

class StructuredLogger:
    """Asosiy structured logger"""
    
    def __init__(self, service_name: str, component: str, aggregator: LogAggregator,
                 min_level: LogLevel = LogLevel.INFO):
        self.service_name = service_name
        self.component = component
        self.aggregator = aggregator
        self.min_level = min_level
        self.logger_name = f"{service_name}.{component}"
        
        # Context info
        self._context = {}
        self._context_stack = []
        
    def _create_log_record(self, level: LogLevel, message: str, 
                          extra_fields: Optional[Dict[str, Any]] = None,
                          exception: Optional[Exception] = None,
                          stack_info: Optional[str] = None) -> LogRecord:
        """LogRecord yaratish"""
        import inspect
        
        # Stack frame info
        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller_frame = frame.f_back
            caller_info = inspect.getframeinfo(caller_frame)
            module = caller_info.filename.split('/')[-1].replace('.py', '')
            function = caller_info.function
            line_number = caller_info.lineno
        else:
            module = "unknown"
            function = "unknown"
            line_number = 0
        
        record = LogRecord(
            timestamp=datetime.now().isoformat(),
            level=level,
            service=self.service_name,
            component=self.component,
            message=message,
            logger_name=self.logger_name,
            module=module,
            function=function,
            line_number=line_number,
            thread_id=threading.get_ident(),
            process_id=os.getpid(),
            trace_id=self._context.get('trace_id'),
            span_id=self._context.get('span_id'),
            user_id=self._context.get('user_id'),
            request_id=self._context.get('request_id'),
            correlation_id=self._context.get('correlation_id'),
            custom_fields=self._context.copy()
        )
        
        # Extra fields qo'shish
        if extra_fields:
            record.custom_fields.update(extra_fields)
        
        # Exception info
        if exception:
            record.exception_info = {
                'type': type(exception).__name__,
                'message': str(exception),
                'traceback': traceback.format_exc()
            }
            record.stack_trace = traceback.format_exc()
        
        if stack_info:
            record.stack_trace = stack_info
        
        return record
    
    def debug(self, message: str, **kwargs):
        """Debug log"""
        if self.min_level.value <= LogLevel.DEBUG.value:
            record = self._create_log_record(LogLevel.DEBUG, message, kwargs)
            self.aggregator.add_log(record)
    
    def info(self, message: str, **kwargs):
        """Info log"""
        if self.min_level.value <= LogLevel.INFO.value:
            record = self._create_log_record(LogLevel.INFO, message, kwargs)
            self.aggregator.add_log(record)
    
    def warning(self, message: str, **kwargs):
        """Warning log"""
        if self.min_level.value <= LogLevel.WARNING.value:
            record = self._create_log_record(LogLevel.WARNING, message, kwargs)
            self.aggregator.add_log(record)
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Error log"""
        if self.min_level.value <= LogLevel.ERROR.value:
            record = self._create_log_record(LogLevel.ERROR, message, kwargs, exception)
            self.aggregator.add_log(record)
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Critical log"""
        if self.min_level.value <= LogLevel.CRITICAL.value:
            record = self._create_log_record(LogLevel.CRITICAL, message, kwargs, exception)
            self.aggregator.add_log(record)
    
    def with_context(self, **context):
        """Context manager"""
        return ContextManager(self, context)
    
    def set_context(self, **context):
        """Context ni o'rnatish"""
        self._context.update(context)
    
    def clear_context(self):
        """Context ni tozalash"""
        self._context.clear()

class ContextManager:
    """Context manager for logging"""
    
    def __init__(self, logger: StructuredLogger, context: Dict[str, Any]):
        self.logger = logger
        self.context = context
        self.saved_context = None
    
    def __enter__(self):
        self.saved_context = self.logger._context.copy()
        self.logger._context.update(self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger._context = self.saved_context

# Log Retention Policy
class LogRetentionPolicy:
    """Log retention policies"""
    
    def __init__(self, retention_days: int = 30, max_size_gb: float = 10.0):
        self.retention_days = retention_days
        self.max_size_bytes = int(max_size_gb * 1024 * 1024 * 1024)
    
    def should_retain_file(self, file_path: str, modification_time: float) -> bool:
        """File retention check"""
        age_days = (time.time() - modification_time) / 86400
        return age_days <= self.retention_days
    
    def get_retention_delete_files(self, log_directory: str) -> List[str]:
        """Retention uchun o'chirilishi kerak file larni topish"""
        files_to_delete = []
        
        for root, dirs, files in os.walk(log_directory):
            total_size = 0
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    stat = os.stat(file_path)
                    size = stat.st_size
                    modification_time = stat.st_mtime
                    
                    total_size += size
                    
                    if not self.should_retain_file(file_path, modification_time):
                        files_to_delete.append(file_path)
            
            # Size limit check
            if total_size > self.max_size_bytes:
                # Eng katta file larni o'chirish
                files_with_size = [
                    (os.path.join(root, f), os.path.getsize(os.path.join(root, f)))
                    for f in files
                ]
                files_with_size.sort(key=lambda x: x[1], reverse=True)
                
                # Size limit oshguncha o'chirish
                current_size = total_size
                for file_path, size in files_with_size:
                    if current_size <= self.max_size_bytes:
                        break
                    files_to_delete.append(file_path)
                    current_size -= size
        
        return files_to_delete
    
    def cleanup_logs(self, log_directory: str) -> Dict[str, Any]:
        """Log cleanup"""
        files_to_delete = self.get_retention_delete_files(log_directory)
        deleted_files = []
        total_freed_bytes = 0
        
        for file_path in files_to_delete:
            try:
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    os.remove(file_path)
                    deleted_files.append({
                        'file': file_path,
                        'size_bytes': size,
                        'deleted_at': datetime.now().isoformat()
                    })
                    total_freed_bytes += size
            except Exception as e:
                logging.error(f"Failed to delete log file {file_path}: {e}")
        
        return {
            'deleted_files_count': len(deleted_files),
            'total_freed_bytes': total_freed_bytes,
            'deleted_files': deleted_files
        }

# Centralized Logging System
class CentralizedLoggingSystem:
    """Centralized logging system manager"""
    
    def __init__(self, service_name: str, log_directory: str = "logs",
                 log_format: LogFormat = LogFormat.JSON,
                 retention_days: int = 30):
        self.service_name = service_name
        self.log_directory = log_directory
        self.log_format = log_format
        self.retention_policy = LogRetentionPolicy(retention_days)
        
        # Aggregator
        self.aggregator = LogAggregator()
        
        # Logger instances
        self.loggers: Dict[str, StructuredLogger] = {}
        
        # Setup
        os.makedirs(log_directory, exist_ok=True)
        self._setup_default_subscribers()
        self.aggregator.start()
    
    def _setup_default_subscribers(self):
        """Default subscriber larni o'rnatish"""
        # File subscriber
        log_file = os.path.join(self.log_directory, f"{self.service_name}.log")
        file_subscriber = FileSubscriber(log_file)
        self.aggregator.add_subscriber(file_subscriber)
        
        # Console subscriber
        console_subscriber = ConsoleSubscriber()
        self.aggregator.add_subscriber(console_subscriber)
        
        # Filtering processor
        filter_processor = FilteringProcessor()
        self.aggregator.add_processor(filter_processor)
        
        # Enrichment processor
        environment_info = {
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'hostname': os.getenv('HOSTNAME', 'unknown'),
            'version': os.getenv('APP_VERSION', '1.0.0')
        }
        enrichment_processor = EnrichmentProcessor(environment_info)
        self.aggregator.add_processor(enrichment_processor)
    
    def get_logger(self, component: str, min_level: LogLevel = LogLevel.INFO) -> StructuredLogger:
        """Logger olish"""
        if component not in self.loggers:
            self.loggers[component] = StructuredLogger(
                self.service_name, component, self.aggregator, min_level
            )
        return self.loggers[component]
    
    def cleanup_logs(self) -> Dict[str, Any]:
        """Log cleanup"""
        return self.retention_policy.cleanup_logs(self.log_directory)
    
    def get_stats(self) -> Dict[str, Any]:
        """System statistics"""
        return {
            'service_name': self.service_name,
            'log_directory': self.log_directory,
            'active_loggers': list(self.loggers.keys()),
            'aggregator_stats': self.aggregator.get_stats(),
            'retention_policy': {
                'retention_days': self.retention_policy.retention_days,
                'max_size_gb': self.retention_policy.max_size_bytes / (1024**3)
            }
        }
    
    def stop(self):
        """System ni to'xtatish"""
        self.aggregator.stop()

# Decorators
def logged_function(logger: StructuredLogger, level: LogLevel = LogLevel.INFO):
    """Function logging decorator"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"
            
            # Function call log
            logger.debug(f"Calling {func_name}", 
                        function=func_name,
                        args_count=len(args),
                        kwargs_keys=list(kwargs.keys()))
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(f"Function {func_name} completed",
                           function=func_name,
                           execution_time_ms=execution_time * 1000,
                           success=True)
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Function {func_name} failed",
                            function=func_name,
                            execution_time_ms=execution_time * 1000,
                            exception=e,
                            success=False)
                raise
        
        return wrapper
    return decorator

# Factory function
def create_logging_system(service_name: str, log_directory: str = "logs",
                         log_format: LogFormat = LogFormat.JSON,
                         retention_days: int = 30) -> CentralizedLoggingSystem:
    """Logging system yaratish uchun factory function"""
    return CentralizedLoggingSystem(service_name, log_directory, log_format, retention_days)

# Example usage
if __name__ == "__main__":
    # Logging system yaratish
    logging_system = create_logging_system("trading_engine", "logs", LogFormat.JSON, 7)
    
    try:
        # Logger olish
        logger = logging_system.get_logger("database")
        api_logger = logging_system.get_logger("api_gateway")
        
        # Basic logging
        logger.info("Database connection established", 
                   host="localhost", port=5432, database="trading")
        
        logger.debug("Executing query", 
                    query="SELECT * FROM trades", 
                    parameters={"limit": 100})
        
        logger.warning("Slow query detected", 
                      query="SELECT * FROM large_table", 
                      execution_time_ms=2500)
        
        logger.error("Database connection failed", 
                    host="localhost", port=5432, 
                    error="Connection timeout")
        
        # Context manager bilan logging
        with logger.with_context(trace_id="12345", user_id="user123"):
            api_logger.info("Processing trade request", 
                           trade_id="T12345", 
                           amount=1000.00, 
                           currency="USD")
        
        # Function decorator bilan logging
        @logged_function(logger, LogLevel.INFO)
        def sample_calculation(x: int, y: int) -> int:
            """Sample calculation function"""
            time.sleep(0.1)  # Simulatsiya qilingan ishlov
            return x + y
        
        result = sample_calculation(10, 20)
        print(f"Calculation result: {result}")
        
        # Exception logging
        try:
            raise ValueError("Sample error")
        except Exception as e:
            logger.error("Exception occurred in processing", exception=e)
        
        # Stats olish
        time.sleep(2)  # Aggregator flush uchun kutish
        stats = logging_system.get_stats()
        print("\n=== LOGGING SYSTEM STATS ===")
        print(json.dumps(stats, indent=2, default=str))
        
        # Log cleanup
        cleanup_result = logging_system.cleanup_logs()
        print("\n=== LOG CLEANUP ===")
        print(json.dumps(cleanup_result, indent=2, default=str))
        
    finally:
        logging_system.stop()