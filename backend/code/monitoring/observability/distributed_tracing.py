#!/usr/bin/env python3
"""
Distributed Tracing va Observability System
Microservislar orasida trace tracking va performance profiling
"""

import time
import threading
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from contextlib import contextmanager
from functools import wraps
import asyncio
import weakref
from enum import Enum

class TraceStatus(Enum):
    """Trace holati"""
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"

class SpanType(Enum):
    """Span turi"""
    HTTP = "http"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    FUNCTION = "function"
    EXTERNAL = "external"
    CRON_JOB = "cron_job"

@dataclass
class Span:
    """Distributed tracing span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    span_type: SpanType
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    tags: Dict[str, Any] = None
    logs: List[Dict[str, Any]] = None
    status: TraceStatus = TraceStatus.OK
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
        if self.logs is None:
            self.logs = []
    
    def finish(self, status: TraceStatus = TraceStatus.OK, error_message: Optional[str] = None):
        """Span ni yakunlash"""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.status = status
        if error_message:
            self.error_message = error_message
    
    def add_tag(self, key: str, value: Any):
        """Tag qo'shish"""
        self.tags[key] = value
    
    def add_log(self, message: str, level: str = "info", **kwargs):
        """Log qo'shish"""
        log_entry = {
            'timestamp': time.time(),
            'message': message,
            'level': level
        }
        log_entry.update(kwargs)
        self.logs.append(log_entry)
    
    def to_dict(self) -> Dict[str, Any]:
        """Dict ga o'tkazish"""
        data = asdict(self)
        data['span_type'] = self.span_type.value
        data['status'] = self.status.value
        return data

class TraceContext:
    """Trace konteksti"""
    
    def __init__(self, trace_id: str, span_id: str, parent_span_id: Optional[str] = None):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.created_at = time.time()

class SpanCollector:
    """Spanni yig'ish va boshqarish"""
    
    def __init__(self, max_spans: int = 10000):
        self.spans: Dict[str, Span] = {}
        self.active_spans: Dict[str, Span] = {}
        self.lock = threading.RLock()
        self.max_spans = max_spans
        self.trace_count = 0
        self.span_count = 0
        
    def create_span(self, operation_name: str, span_type: SpanType, 
                   parent_span_id: Optional[str] = None,
                   trace_id: Optional[str] = None) -> Span:
        """Yangi span yaratish"""
        if trace_id is None:
            trace_id = str(uuid.uuid4())
        
        span_id = str(uuid.uuid4())
        
        span = Span(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            span_type=span_type,
            start_time=time.time()
        )
        
        with self.lock:
            self.active_spans[span_id] = span
            self.span_count += 1
            
            # Memory management
            if len(self.spans) + len(self.active_spans) > self.max_spans:
                self._cleanup_old_spans()
        
        return span
    
    def finish_span(self, span_id: str, status: TraceStatus = TraceStatus.OK, 
                   error_message: Optional[str] = None):
        """Spanni yakunlash"""
        with self.lock:
            if span_id in self.active_spans:
                span = self.active_spans.pop(span_id)
                span.finish(status, error_message)
                self.spans[span_id] = span
    
    def get_trace(self, trace_id: str) -> List[Span]:
        """Trace ni olish"""
        with self.lock:
            return [
                span for span in self.spans.values() 
                if span.trace_id == trace_id
            ]
    
    def get_recent_traces(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Oxirgi tracelarni olish"""
        with self.lock:
            recent_spans = sorted(
                self.spans.values(),
                key=lambda x: x.end_time or x.start_time,
                reverse=True
            )[:limit]
            
            traces_dict = {}
            for span in recent_spans:
                if span.trace_id not in traces_dict:
                    traces_dict[span.trace_id] = []
                traces_dict[span.trace_id].append(span.to_dict())
            
            return [
                {
                    'trace_id': trace_id,
                    'spans': spans,
                    'start_time': min(s['start_time'] for s in spans),
                    'end_time': max(s['end_time'] or s['start_time'] for s in spans),
                    'span_count': len(spans)
                }
                for trace_id, spans in traces_dict.items()
            ]
    
    def _cleanup_old_spans(self):
        """Eski spanni tozalash"""
        if len(self.spans) > self.max_spans // 2:
            # Eng eski spanni o'chirish
            oldest_spans = sorted(
                self.spans.items(),
                key=lambda x: x[1].end_time or x[1].start_time
            )
            
            remove_count = len(self.spans) - (self.max_spans // 2)
            for span_id, _ in oldest_spans[:remove_count]:
                del self.spans[span_id]

class Tracer:
    """Asosiy Tracer class"""
    
    def __init__(self, service_name: str, collector: Optional[SpanCollector] = None):
        self.service_name = service_name
        self.collector = collector or SpanCollector()
        self.running = False
        self._exporters = []
        self._context_stack = []
        
    def start_span(self, operation_name: str, span_type: SpanType = SpanType.FUNCTION,
                  parent_span_id: Optional[str] = None,
                  trace_id: Optional[str] = None) -> Span:
        """Span yaratish va avtomatik context management"""
        if self._context_stack:
            parent_context = self._context_stack[-1]
            if parent_span_id is None:
                parent_span_id = parent_context.span_id
            if trace_id is None:
                trace_id = parent_context.trace_id
        
        span = self.collector.create_span(operation_name, span_type, parent_span_id, trace_id)
        self._context_stack.append(TraceContext(span.trace_id, span.span_id, parent_span_id))
        
        # Span tags qo'shish
        span.add_tag('service.name', self.service_name)
        span.add_tag('service.version', '1.0.0')
        span.add_tag('span.type', span_type.value)
        span.add_tag('timestamp', datetime.now().isoformat())
        
        return span
    
    def finish_span(self, span: Span, status: TraceStatus = TraceStatus.OK,
                   error_message: Optional[str] = None):
        """Spanni yakunlash"""
        span.finish(status, error_message)
        self.collector.finish_span(span.span_id, status, error_message)
        
        # Context stack dan olib tashlash
        if self._context_stack:
            self._context_stack.pop()
        
        # Exporterlarga yuborish
        self._export_span(span)
    
    def _export_span(self, span: Span):
        """Spanni exporterlarga yuborish"""
        for exporter in self._exporters:
            try:
                exporter.export_span(span)
            except Exception as e:
                logging.error(f"Failed to export span: {e}")
    
    def add_exporter(self, exporter):
        """Exporter qo'shish"""
        self._exporters.append(exporter)
    
    @contextmanager
    def span(self, operation_name: str, span_type: SpanType = SpanType.FUNCTION):
        """Context manager span uchun"""
        span = self.start_span(operation_name, span_type)
        try:
            yield span
            self.finish_span(span, TraceStatus.OK)
        except Exception as e:
            self.finish_span(span, TraceStatus.ERROR, str(e))
            raise

# Decorator'lar
def trace_function(tracer: Tracer, operation_name: Optional[str] = None, 
                  span_type: SpanType = SpanType.FUNCTION):
    """Function tracing decorator"""
    def decorator(func: Callable) -> Callable:
        func_name = operation_name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.span(func_name, span_type) as span:
                start_time = time.time()
                try:
                    # Function arguments ni log qilish
                    if hasattr(func, '__annotations__'):
                        span.add_tag('function.args_count', len(args) + len(kwargs))
                        span.add_tag('function.args_types', str(func.__annotations__))
                    
                    result = func(*args, **kwargs)
                    
                    # Return value info
                    span.add_tag('function.execution_time_ms', (time.time() - start_time) * 1000)
                    if hasattr(result, '__len__'):
                        span.add_tag('function.result_size', len(result))
                    
                    return result
                    
                except Exception as e:
                    span.add_tag('function.error', str(e))
                    span.add_tag('function.error_type', type(e).__name__)
                    raise
        return wrapper
    return decorator

def trace_http_request(tracer: Tracer, method: str, url: str):
    """HTTP request tracing decorator"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with tracer.span(f"{method} {url}", SpanType.HTTP) as span:
                span.add_tag('http.method', method)
                span.add_tag('http.url', url)
                span.add_tag('http.request_id', str(uuid.uuid4()))
                
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    
                    # Response info
                    span.add_tag('http.status_code', getattr(result, 'status_code', 200))
                    span.add_tag('http.response_time_ms', (time.time() - start_time) * 1000)
                    
                    if hasattr(result, 'content_length'):
                        span.add_tag('http.response_size_bytes', result.content_length)
                    
                    return result
                    
                except Exception as e:
                    span.add_tag('http.error', str(e))
                    span.add_tag('http.status_code', 500)
                    raise
        return wrapper
    return decorator

def trace_database_query(tracer: Tracer, query_type: str, table: str):
    """Database query tracing decorator"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            operation_name = f"{query_type} {table}"
            with tracer.span(operation_name, SpanType.DATABASE) as span:
                span.add_tag('db.type', 'postgresql')
                span.add_tag('db.operation', query_type)
                span.add_tag('db.table', table)
                span.add_tag('db.statement', f"{query_type} {table}")
                
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    
                    # Query performance info
                    span.add_tag('db.execution_time_ms', (time.time() - start_time) * 1000)
                    if hasattr(result, 'rowcount'):
                        span.add_tag('db.rows_affected', result.rowcount)
                    
                    return result
                    
                except Exception as e:
                    span.add_tag('db.error', str(e))
                    span.add_tag('db.error_type', type(e).__name__)
                    raise
        return wrapper
    return decorator

# Exporter'lar
class SpanExporter:
    """Span exporter base class"""
    
    def export_span(self, span: Span):
        """Span ni export qilish"""
        raise NotImplementedError
    
    def export_batch(self, spans: List[Span]):
        """Batch span export"""
        for span in spans:
            self.export_span(span)

class JSONExporter(SpanExporter):
    """JSON file exporter"""
    
    def __init__(self, file_path: str = "traces.jsonl"):
        self.file_path = file_path
        self.lock = threading.Lock()
    
    def export_span(self, span: Span):
        """Span ni JSON file ga yozish"""
        with self.lock:
            try:
                with open(self.file_path, 'a', encoding='utf-8') as f:
                    json.dump(span.to_dict(), f, ensure_ascii=False, default=str)
                    f.write('\n')
            except Exception as e:
                logging.error(f"Failed to write span to file: {e}")

class JaegerExporter(SpanExporter):
    """Jaeger uchun exporter"""
    
    def __init__(self, jaeger_host: str = "localhost", jaeger_port: int = 14268):
        self.jaeger_host = jaeger_host
        self.jaeger_port = jaeger_port
        self.endpoint = f"http://{jaeger_host}:{jaeger_port}/api/traces"
        self.lock = threading.Lock()
    
    def export_span(self, span: Span):
        """Span ni Jaeger ga yuborish"""
        try:
            # Jaeger formatiga konversiya
            jaeger_span = self._convert_to_jaeger_format(span)
            
            # HTTP POST request yuborish
            # Real implementation da requests kutibxonasidan foydalanish kerak
            logging.info(f"Would send span to Jaeger: {jaeger_span}")
            
        except Exception as e:
            logging.error(f"Failed to export span to Jaeger: {e}")
    
    def _convert_to_jaeger_format(self, span: Span) -> Dict[str, Any]:
        """Jaeger formatiga konversiya"""
        return {
            'traceId': span.trace_id,
            'spanId': span.span_id,
            'parentSpanId': span.parent_span_id,
            'operationName': span.operation_name,
            'startTime': int(span.start_time * 1000000),  # microseconds
            'duration': int((span.duration_ms or 0) * 1000),  # microseconds
            'tags': list(span.tags.items()),
            'logs': span.logs,
            'references': []
        }

class ZipkinExporter(SpanExporter):
    """Zipkin uchun exporter"""
    
    def __init__(self, zipkin_host: str = "localhost", zipkin_port: int = 9411):
        self.zipkin_host = zipkin_host
        self.zipkin_port = zipkin_port
        self.endpoint = f"http://{zipkin_host}:{zipkin_port}/api/v2/spans"
        self.lock = threading.Lock()
    
    def export_span(self, span: Span):
        """Span ni Zipkin ga yuborish"""
        try:
            # Zipkin formatiga konversiya
            zipkin_span = self._convert_to_zipkin_format(span)
            
            # HTTP POST request yuborish
            # Real implementation da requests kutibxonasidan foydalanish kerak
            logging.info(f"Would send span to Zipkin: {zipkin_span}")
            
        except Exception as e:
            logging.error(f"Failed to export span to Zipkin: {e}")
    
    def _convert_to_zipkin_format(self, span: Span) -> Dict[str, Any]:
        """Zipkin formatiga konversiya"""
        return {
            'traceId': span.trace_id,
            'id': span.span_id,
            'parentId': span.parent_span_id,
            'name': span.operation_name,
            'timestamp': int(span.start_time * 1000000),  # microseconds
            'duration': int((span.duration_ms or 0) * 1000),  # microseconds
            'tags': span.tags,
            'annotations': [
                {
                    'timestamp': int(span.start_time * 1000000),
                    'value': 'cs'  # Client Send
                },
                {
                    'timestamp': int((span.end_time or span.start_time) * 1000000),
                    'value': 'cr'  # Client Receive
                }
            ]
        }

class ElasticSearchExporter(SpanExporter):
    """ElasticSearch uchun exporter"""
    
    def __init__(self, es_host: str = "localhost", es_port: int = 9200, 
                 index_name: str = "traces"):
        self.es_host = es_host
        self.es_port = es_port
        self.index_name = index_name
        self.endpoint = f"http://{es_host}:{es_port}/{index_name}/_doc"
        self.lock = threading.Lock()
    
    def export_span(self, span: Span):
        """Span ni ElasticSearch ga yuborish"""
        try:
            # ElasticSearch document format
            doc = {
                '@timestamp': datetime.fromtimestamp(span.start_time).isoformat(),
                'trace_id': span.trace_id,
                'span_id': span.span_id,
                'parent_span_id': span.parent_span_id,
                'operation_name': span.operation_name,
                'service_name': span.tags.get('service.name'),
                'span_type': span.span_type.value,
                'status': span.status.value,
                'start_time': span.start_time,
                'end_time': span.end_time,
                'duration_ms': span.duration_ms,
                'tags': span.tags,
                'logs': span.logs
            }
            
            # HTTP POST request yuborish
            # Real implementation da elasticsearch kutibxonasidan foydalanish kerak
            logging.info(f"Would send span to ElasticSearch: {doc}")
            
        except Exception as e:
            logging.error(f"Failed to export span to ElasticSearch: {e}")

# Health Check system
class HealthChecker:
    """Health check manager"""
    
    def __init__(self):
        self.checks = {}
        self.health_status = {}
        self.last_check = {}
    
    def register_check(self, name: str, check_func: Callable, 
                      timeout: float = 30.0):
        """Health check registratsiya qilish"""
        self.checks[name] = {
            'function': check_func,
            'timeout': timeout,
            'description': f"Health check for {name}"
        }
    
    def run_health_checks(self) -> Dict[str, Any]:
        """Barcha health checklarni ishga tushirish"""
        results = {}
        overall_status = "healthy"
        
        for name, config in self.checks.items():
            try:
                start_time = time.time()
                
                # Health check funksiyasini chaqirish
                check_result = config['function']()
                
                execution_time = time.time() - start_time
                
                if check_result.get('status') == 'healthy':
                    results[name] = {
                        'status': 'healthy',
                        'message': check_result.get('message', 'OK'),
                        'response_time_ms': execution_time * 1000,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    results[name] = {
                        'status': 'unhealthy',
                        'message': check_result.get('message', 'Check failed'),
                        'response_time_ms': execution_time * 1000,
                        'timestamp': datetime.now().isoformat()
                    }
                    if overall_status == "healthy":
                        overall_status = "degraded"
                
            except Exception as e:
                results[name] = {
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                overall_status = "unhealthy"
        
        self.health_status = {
            'status': overall_status,
            'checks': results,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        return self.health_status
    
    def get_status(self) -> Dict[str, Any]:
        """Joriy health status olish"""
        return self.health_status

# Performance Profiler
class PerformanceProfiler:
    """Performance profiling system"""
    
    def __init__(self, tracer: Tracer):
        self.tracer = tracer
        self.profiles = {}
        self.lock = threading.Lock()
    
    def profile_function(self, func: Callable, iterations: int = 1000) -> Dict[str, Any]:
        """Function performance profiling"""
        with self.tracer.span(f"profile_{func.__name__}", SpanType.FUNCTION) as span:
            execution_times = []
            memory_usage = []
            
            for i in range(iterations):
                start_time = time.time()
                try:
                    # Function call
                    result = func()
                    execution_time = time.time() - start_time
                    execution_times.append(execution_time)
                    
                    # Memory usage (agar psutil mavjud bo'lsa)
                    try:
                        import psutil
                        process = psutil.Process()
                        memory_usage.append(process.memory_info().rss)
                    except:
                        pass
                    
                except Exception as e:
                    span.add_log(f"Error in iteration {i}: {e}", "error")
            
            # Profiling results
            if execution_times:
                stats = {
                    'function': func.__name__,
                    'iterations': len(execution_times),
                    'total_time': sum(execution_times),
                    'avg_time': sum(execution_times) / len(execution_times),
                    'min_time': min(execution_times),
                    'max_time': max(execution_times),
                    'p50_time': self._percentile(execution_times, 50),
                    'p95_time': self._percentile(execution_times, 95),
                    'p99_time': self._percentile(execution_times, 99)
                }
                
                if memory_usage:
                    stats.update({
                        'avg_memory_bytes': sum(memory_usage) / len(memory_usage),
                        'min_memory_bytes': min(memory_usage),
                        'max_memory_bytes': max(memory_usage)
                    })
                
                self.profiles[func.__name__] = stats
                
                # Span tags
                span.add_tag('profile.iterations', len(execution_times))
                span.add_tag('profile.avg_time_ms', stats['avg_time'] * 1000)
                span.add_tag('profile.p95_time_ms', stats['p95_time'] * 1000)
                
                return stats
            else:
                return {'error': 'No successful executions'}
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Percentile hisoblash"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def get_profile(self, func_name: str) -> Optional[Dict[str, Any]]:
        """Function profiling natijasini olish"""
        return self.profiles.get(func_name)
    
    def get_all_profiles(self) -> Dict[str, Any]:
        """Barcha profiling natijalarini olish"""
        return self.profiles.copy()

# Observability Manager
class ObservabilityManager:
    """Barcha observability komponentlarni birlashtiruvchi manager"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.tracer = Tracer(service_name)
        self.health_checker = HealthChecker()
        self.profiler = PerformanceProfiler(self.tracer)
        self.collector = SpanCollector()
        
        # Standard exporters
        self.json_exporter = JSONExporter(f"traces_{service_name}.jsonl")
        self.tracer.add_exporter(self.json_exporter)
        
        # Monitoring integration
        self.monitoring_system = None
    
    def set_monitoring_system(self, monitoring_system):
        """Monitoring tizimni bog'lash"""
        self.monitoring_system = monitoring_system
    
    def start(self):
        """Observability tizimini ishga tushirish"""
        logging.info(f"Observability system started for {self.service_name}")
    
    def stop(self):
        """Observability tizimini to'xtatish"""
        logging.info(f"Observability system stopped for {self.service_name}")
    
    def get_observability_summary(self) -> Dict[str, Any]:
        """Observability summary olish"""
        traces_summary = self.tracer.collector.get_recent_traces(10)
        health_status = self.health_checker.get_status()
        profiles = self.profiler.get_all_profiles()
        
        return {
            'service_name': self.service_name,
            'timestamp': datetime.now().isoformat(),
            'health': health_status,
            'traces': {
                'recent_traces': traces_summary,
                'total_traces': len(traces_summary),
                'active_spans': len(self.tracer.collector.active_spans)
            },
            'profiles': profiles,
            'monitoring_connected': self.monitoring_system is not None
        }

# Utility functions
def create_observability_system(service_name: str) -> ObservabilityManager:
    """Observability tizimini yaratish uchun factory function"""
    return ObservabilityManager(service_name)

# Example usage
if __name__ == "__main__":
    # Observability tizimini yaratish
    observability = create_observability_system("trading_engine")
    
    try:
        # Tizimni ishga tushirish
        observability.start()
        
        # Health check registratsiya qilish
        def database_health():
            # Simulatsiya qilingan DB health check
            return {'status': 'healthy', 'message': 'Database connection OK'}
        
        def redis_health():
            # Simulatsiya qilingan Redis health check
            return {'status': 'healthy', 'message': 'Redis connection OK'}
        
        observability.health_checker.register_check("database", database_health)
        observability.health_checker.register_check("redis", redis_health)
        
        # Health checklarni ishga tushirish
        health_results = observability.health_checker.run_health_checks()
        print("=== HEALTH CHECK RESULTS ===")
        print(json.dumps(health_results, indent=2))
        
        # Tracing test
        @trace_function(observability.tracer, "sample_calculation", SpanType.FUNCTION)
        def sample_calculation(n: int) -> int:
            """Test calculation function"""
            result = 0
            for i in range(n):
                result += i ** 2
            return result
        
        # Function calling with tracing
        result = sample_calculation(1000)
        print(f"Calculation result: {result}")
        
        # HTTP request tracing
        @trace_http_request(observability.tracer, "GET", "/api/trades")
        def mock_http_request():
            time.sleep(0.1)  # Simulatsiya qilingan network delay
            class MockResponse:
                status_code = 200
                content_length = 1024
            return MockResponse()
        
        response = mock_http_request()
        print(f"HTTP response status: {response.status_code}")
        
        # Database query tracing
        @trace_database_query(observability.tracer, "SELECT", "trades")
        def mock_db_query():
            time.sleep(0.05)  # Simulatsiya qilingan DB delay
            class MockResult:
                rowcount = 100
            return MockResult()
        
        db_result = mock_db_query()
        print(f"DB query affected rows: {db_result.rowcount}")
        
        # Profiling
        def cpu_intensive_function():
            total = 0
            for i in range(10000):
                total += i ** 0.5
            return total
        
        profile_result = observability.profiler.profile_function(cpu_intensive_function, 100)
        print("\n=== PROFILING RESULTS ===")
        print(json.dumps(profile_result, indent=2, default=str))
        
        # Observability summary
        summary = observability.get_observability_summary()
        print("\n=== OBSERVABILITY SUMMARY ===")
        print(json.dumps(summary, indent=2, default=str))
        
    finally:
        observability.stop()