"""
Market Connection Service
========================

Direct market access and connection management
"""

import time
import logging
import asyncio
from typing import Dict, List, Optional, Any

class MarketConnection:
    """Market Connection Management"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Exchange connections
        self.exchanges = config.get('exchanges', {
            'NASDAQ': {
                'protocol': 'FIX',
                'version': '4.4',
                'throughput': 10000,  # orders per second
                'max_message_size': 1024
            },
            'NYSE': {
                'protocol': 'FIX',
                'version': '4.4',
                'throughput': 10000,
                'max_message_size': 1024
            },
            'FOREX': {
                'protocol': 'FIX',
                'version': '4.2',
                'throughput': 20000,
                'max_message_size': 512
            },
            'CRYPTO': {
                'protocol': 'WebSocket',
                'version': '1.1',
                'throughput': 15000,
                'max_message_size': 2048
            }
        })
        
        self.connection_status = {}
        self.message_queue = {}
        self.message_count = 0
    
    async def initialize(self) -> bool:
        """Initialize market connections"""
        try:
            self.logger.info("Initializing Market Connections...")
            
            # Initialize connections to all exchanges
            for exchange, config in self.exchanges.items():
                await self._initialize_exchange(exchange, config)
            
            self.logger.info("Market Connections initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Market Connections: {e}")
            return False
    
    async def _initialize_exchange(self, exchange: str, config: Dict[str, Any]):
        """Initialize connection to specific exchange"""
        # Simulate connection establishment
        await asyncio.sleep(0.05)  # 50ms simulated setup
        
        self.connection_status[exchange] = {
            'status': 'connected',
            'protocol': config['protocol'],
            'version': config['version'],
            'throughput': config['throughput'],
            'connected_at': time.time(),
            'messages_sent': 0,
            'messages_received': 0
        }
        
        self.message_queue[exchange] = []
        
        self.logger.info(f"Connected to {exchange} via {config['protocol']}")
    
    async def send_order(self, exchange: str, order_data: Dict[str, Any]) -> bool:
        """Send order to exchange"""
        if exchange not in self.connection_status:
            self.logger.error(f"Exchange {exchange} not connected")
            return False
        
        if self.connection_status[exchange]['status'] != 'connected':
            self.logger.error(f"Exchange {exchange} not in connected state")
            return False
        
        try:
            # Simulate order sending
            await asyncio.sleep(0.00001)  # 10 microseconds
            
            self.message_queue[exchange].append(order_data)
            self.connection_status[exchange]['messages_sent'] += 1
            self.message_count += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending order to {exchange}: {e}")
            return False
    
    async def receive_messages(self, exchange: str) -> List[Dict[str, Any]]:
        """Receive messages from exchange"""
        if exchange not in self.message_queue:
            return []
        
        messages = self.message_queue[exchange].copy()
        self.message_queue[exchange].clear()
        
        if messages:
            self.connection_status[exchange]['messages_received'] += len(messages)
        
        return messages
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        stats = {}
        
        for exchange, status in self.connection_status.items():
            uptime = time.time() - status['connected_at']
            message_rate = (status['messages_sent'] + status['messages_received']) / max(uptime, 1)
            
            stats[exchange] = {
                'status': status['status'],
                'uptime_seconds': uptime,
                'messages_sent': status['messages_sent'],
                'messages_received': status['messages_received'],
                'message_rate_per_second': message_rate,
                'throughput_capacity': status['throughput']
            }
        
        return stats
    
    def get_total_throughput(self) -> int:
        """Get total system throughput"""
        return sum(config['throughput'] for config in self.exchanges.values())
    
    async def health_check(self) -> Dict[str, bool]:
        """Perform health check on all connections"""
        health_status = {}
        
        for exchange in self.connection_status:
            status = self.connection_status[exchange]['status']
            health_status[exchange] = status == 'connected'
        
        return health_status
    
    async def shutdown(self):
        """Shutdown market connections"""
        self.logger.info("Shutting down Market Connections")
        
        # Close connections to all exchanges
        for exchange in self.connection_status:
            self.connection_status[exchange]['status'] = 'disconnected'
            self.logger.info(f"Disconnected from {exchange}")
        
        self.connection_status.clear()
        self.message_queue.clear()