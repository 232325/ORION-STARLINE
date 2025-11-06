"""
Operational Risk Management
=========================

Operational risk monitoring and control
"""

import time
import logging
import psutil
from typing import Dict, List, Optional, Any

class OperationalRisk:
    """Operational Risk Management"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Operational risk parameters
        self.cpu_threshold = config.get('cpu_threshold', 80.0)  # 80%
        self.memory_threshold = config.get('memory_threshold', 85.0)  # 85%
        self.network_latency_threshold = config.get('network_latency_threshold', 1000)  # 1ms
        
        # Health check tracking
        self.last_health_check = 0
        self.health_check_interval = 30  # 30 seconds
    
    async def initialize(self) -> bool:
        """Initialize operational risk"""
        self.logger.info("Operational Risk initialized")
        return True
    
    async def check_system_health(self) -> bool:
        """Check overall system health"""
        try:
            current_time = time.time()
            
            # Check if it's time for a health check
            if current_time - self.last_health_check < self.health_check_interval:
                return True
            
            self.last_health_check = current_time
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.cpu_threshold:
                self.logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
                return False
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self.memory_threshold:
                self.logger.warning(f"High memory usage: {memory.percent:.1f}%")
                return False
            
            # Check disk usage
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                self.logger.warning(f"High disk usage: {disk.percent:.1f}%")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking system health: {e}")
            return False
    
    def is_healthy(self) -> bool:
        """Check if operational risk is healthy"""
        return True  # Simplified health check
    
    async def shutdown(self):
        """Shutdown operational risk"""
        self.logger.info("Operational Risk shutdown")