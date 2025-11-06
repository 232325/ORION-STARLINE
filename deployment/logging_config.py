"""
Production-grade logging configuration for Orion Starline
Centralized logging with ELK stack integration
"""

import logging
import logging.handlers
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import structlog
from pythonjsonlogger import jsonlogger

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
                          'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process', 'getMessage']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)

class ELKHandler(logging.Handler):
    """Custom handler for sending logs to Logstash/Elasticsearch"""
    
    def __init__(self, logstash_host: str = 'logstash', logstash_port: int = 5044):
        super().__init__()
        self.logstash_host = logstash_host
        self.logstash_port = logstash_port
        self.queue = []
    
    def emit(self, record):
        try:
            log_entry = self.format(record)
            
            # In production, this would send to Logstash via TCP/UDP
            # For now, we'll queue the log entry
            self.queue.append(log_entry)
            
            # Process queue periodically
            if len(self.queue) >= 100:
                self._process_queue()
                
        except Exception:
            self.handleError(record)
    
    def _process_queue(self):
        """Process the log queue - send to Logstash"""
        # This would send to Logstash
        # logstash_host: self.logstash_host
        # logstash_port: self.logstash_port
        # data: '\n'.join(self.queue)
        
        self.queue.clear()

class TradingContextFilter(logging.Filter):
    """Add trading-specific context to log records"""
    
    def filter(self, record):
        # Add trading-specific fields
        record.user_id = getattr(record, 'user_id', 'anonymous')
        record.session_id = getattr(record, 'session_id', 'unknown')
        record.trade_id = getattr(record, 'trade_id', None)
        record.strategy_name = getattr(record, 'strategy_name', None)
        record.signal_type = getattr(record, 'signal_type', None)
        record.portfolio_id = getattr(record, 'portfolio_id', None)
        return True

def setup_production_logging(config: Optional[Dict[str, Any]] = None) -> None:
    """Configure production logging"""
    
    if config is None:
        config = {
            'log_level': 'INFO',
            'log_format': 'json',
            'enable_console': True,
            'enable_file': True,
            'enable_elk': True,
            'log_file_path': '/app/logs/orion.log',
            'max_file_size': 100 * 1024 * 1024,  # 100MB
            'backup_count': 10,
            'logstash_host': 'logstash',
            'logstash_port': 5044
        }
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.get('log_level', 'INFO')))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    if config.get('enable_console', True):
        console_handler = logging.StreamHandler(sys.stdout)
        
        if config.get('log_format') == 'json':
            console_handler.setFormatter(StructuredFormatter())
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
        
        root_logger.addHandler(console_handler)
    
    # File handler
    if config.get('enable_file', True):
        file_handler = logging.handlers.RotatingFileHandler(
            config.get('log_file_path', '/app/logs/orion.log'),
            maxBytes=config.get('max_file_size', 100 * 1024 * 1024),
            backupCount=config.get('backup_count', 10)
        )
        
        if config.get('log_format') == 'json':
            file_handler.setFormatter(StructuredFormatter())
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
        
        root_logger.addHandler(file_handler)
    
    # ELK handler
    if config.get('enable_elk', True):
        elk_handler = ELKHandler(
            config.get('logstash_host', 'logstash'),
            config.get('logstash_port', 5044)
        )
        elk_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(elk_handler)
    
    # Trading context filter
    trading_filter = TradingContextFilter()
    root_logger.addFilter(trading_filter)
    
    # Configure third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    
    print("Production logging configured successfully")

def setup_structured_logging() -> None:
    """Setup structured logging with structlog"""
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

class TradingLogger:
    """Specialized logger for trading operations"""
    
    def __init__(self, name: str = 'orion.trading'):
        self.logger = structlog.get_logger(name)
        self.context = {}
    
    def set_context(self, **kwargs):
        """Set context for all subsequent log entries"""
        self.context.update(kwargs)
    
    def trade_signal(self, signal_type: str, symbol: str, action: str, confidence: float, **kwargs):
        """Log trading signal generation"""
        self.logger.info(
            "Trading signal generated",
            event_type="trade_signal",
            signal_type=signal_type,
            symbol=symbol,
            action=action,
            confidence=confidence,
            **self.context,
            **kwargs
        )
    
    def order_execution(self, order_id: str, symbol: str, side: str, quantity: float, 
                       price: float, status: str, **kwargs):
        """Log order execution"""
        self.logger.info(
            "Order executed",
            event_type="order_execution",
            order_id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            status=status,
            **self.context,
            **kwargs
        )
    
    def portfolio_update(self, portfolio_id: str, total_value: float, pnl: float, 
                        positions_count: int, **kwargs):
        """Log portfolio updates"""
        self.logger.info(
            "Portfolio updated",
            event_type="portfolio_update",
            portfolio_id=portfolio_id,
            total_value=total_value,
            pnl=pnl,
            positions_count=positions_count,
            **self.context,
            **kwargs
        )
    
    def risk_alert(self, alert_type: str, severity: str, message: str, **kwargs):
        """Log risk alerts"""
        level = "warning" if severity == "medium" else "error"
        getattr(self.logger, level)(
            "Risk alert triggered",
            event_type="risk_alert",
            alert_type=alert_type,
            severity=severity,
            message=message,
            **self.context,
            **kwargs
        )
    
    def strategy_performance(self, strategy_name: str, metrics: Dict[str, Any], **kwargs):
        """Log strategy performance metrics"""
        self.logger.info(
            "Strategy performance update",
            event_type="strategy_performance",
            strategy_name=strategy_name,
            metrics=metrics,
            **self.context,
            **kwargs
        )
    
    def market_data(self, symbol: str, data_type: str, value: Any, **kwargs):
        """Log market data updates"""
        self.logger.debug(
            "Market data updated",
            event_type="market_data",
            symbol=symbol,
            data_type=data_type,
            value=value,
            **self.context,
            **kwargs
        )

# Global trading logger instance
trading_logger = TradingLogger()

def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a configured logger instance"""
    return structlog.get_logger(name)

# Audit logger for compliance
class AuditLogger:
    """Specialized logger for audit trails"""
    
    def __init__(self):
        self.logger = structlog.get_logger('orion.audit')
    
    def user_action(self, user_id: str, action: str, resource: str, 
                   result: str, details: Dict[str, Any] = None):
        """Log user actions for audit trail"""
        self.logger.info(
            "User action",
            event_type="user_action",
            user_id=user_id,
            action=action,
            resource=resource,
            result=result,
            details=details or {},
            timestamp=datetime.utcnow().isoformat()
        )
    
    def data_access(self, user_id: str, data_type: str, record_id: str, 
                   access_type: str = 'read'):
        """Log data access for compliance"""
        self.logger.info(
            "Data access",
            event_type="data_access",
            user_id=user_id,
            data_type=data_type,
            record_id=record_id,
            access_type=access_type,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def system_event(self, event_type: str, component: str, details: Dict[str, Any]):
        """Log system events for monitoring"""
        self.logger.info(
            "System event",
            event_type="system_event",
            event_type_name=event_type,
            component=component,
            details=details,
            timestamp=datetime.utcnow().isoformat()
        )

# Global audit logger instance
audit_logger = AuditLogger()

# Error tracking
class ErrorTracker:
    """Track and log errors with context"""
    
    def __init__(self):
        self.logger = structlog.get_logger('orion.errors')
        self.error_counts = {}
    
    def log_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """Log error with tracking"""
        # Increment error count
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Log error
        self.logger.error(
            "Application error",
            error_type=error_type,
            error_message=error_message,
            occurrence_count=self.error_counts[error_type],
            context=context or {},
            timestamp=datetime.utcnow().isoformat()
        )
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get summary of all tracked errors"""
        return self.error_counts.copy()

# Global error tracker instance
error_tracker = ErrorTracker()

# Performance logging
class PerformanceLogger:
    """Log performance metrics"""
    
    def __init__(self):
        self.logger = structlog.get_logger('orion.performance')
    
    def log_api_call(self, endpoint: str, method: str, duration: float, 
                    status_code: int, user_id: str = None):
        """Log API performance"""
        self.logger.info(
            "API call",
            event_type="api_call",
            endpoint=endpoint,
            method=method,
            duration=duration,
            status_code=status_code,
            user_id=user_id,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def log_database_query(self, query_type: str, table: str, duration: float, 
                          rows_affected: int = None):
        """Log database performance"""
        self.logger.info(
            "Database query",
            event_type="database_query",
            query_type=query_type,
            table=table,
            duration=duration,
            rows_affected=rows_affected,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def log_trade_execution(self, symbol: str, duration: float, slippage: float):
        """Log trading performance"""
        self.logger.info(
            "Trade execution",
            event_type="trade_execution",
            symbol=symbol,
            duration=duration,
            slippage=slippage,
            timestamp=datetime.utcnow().isoformat()
        )

# Global performance logger instance
performance_logger = PerformanceLogger()

if __name__ == "__main__":
    # Setup logging
    setup_production_logging()
    setup_structured_logging()
    
    # Test logging
    logger = get_logger('test')
    logger.info("Test log message", test_field="test_value")
    
    # Test trading logger
    trading_logger.trade_signal("BUY", "EURUSD", "MARKET", 0.85)
    trading_logger.order_execution("ORD123", "EURUSD", "BUY", 10000, 1.1234, "FILLED")
    
    # Test audit logger
    audit_logger.user_action("USER001", "LOGIN", "session", "success")
    
    # Test error tracker
    error_tracker.log_error("DATABASE_ERROR", "Connection timeout", {"retry_count": 3})
    
    # Test performance logger
    performance_logger.log_api_call("/api/trades", "GET", 0.125, 200)
    
    print("Logging test completed")