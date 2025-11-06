"""
HFT Engine Integration Connector
===============================

Integration connector for High-Frequency Trading engines.
Handles real-time communication for position updates, risk controls,
and trading signals.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class HFTEngineConfig:
    """Configuration for HFT Engine integration"""
    engine_endpoint: str = "http://localhost:8080"
    api_key: str = ""
    timeout: int = 30
    max_retries: int = 3
    sync_interval: int = 1  # seconds
    position_buffer_size: int = 100

class HFTEngineConnector:
    """
    HFT Engine Integration Connector
    
    Provides interface to HFT trading engines for:
    - Real-time position monitoring
    - Position size adjustments
    - Emergency position closures
    - Risk control signal processing
    - Market order management
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = HFTEngineConfig(**config)
        self.connected = False
        self.last_position_sync = None
        self.position_buffer = []
        
        # Connection state
        self.session = None
        self.retry_count = 0
        
        # Position tracking
        self.current_positions = {}
        self.position_updates_callbacks = []
        
        logger.info("HFT Engine Connector initialized")
    
    async def initialize(self):
        """Initialize connection to HFT engine"""
        try:
            import aiohttp
            
            # Create HTTP session
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={'Authorization': f'Bearer {self.config.api_key}'} if self.config.api_key else {}
            )
            
            # Test connection
            connection_result = await self._test_connection()
            
            if connection_result:
                self.connected = True
                self.retry_count = 0
                logger.info("HFT Engine connection established")
            else:
                raise Exception("Failed to establish connection to HFT engine")
            
        except Exception as e:
            logger.error(f"Failed to initialize HFT Engine connector: {e}")
            raise
    
    async def _test_connection(self) -> bool:
        """Test connection to HFT engine"""
        try:
            if not self.session:
                return False
            
            async with self.session.get(f"{self.config.engine_endpoint}/health") as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Error testing HFT engine connection: {e}")
            return False
    
    async def get_current_positions(self) -> Dict[str, Any]:
        """Get current positions from HFT engine"""
        try:
            if not self.connected:
                logger.warning("HFT engine not connected")
                return {}
            
            async with self.session.get(f"{self.config.engine_endpoint}/positions") as response:
                if response.status == 200:
                    positions_data = await response.json()
                    
                    # Update current positions
                    self.current_positions = positions_data
                    self.last_position_sync = datetime.now()
                    
                    # Notify callbacks
                    for callback in self.position_updates_callbacks:
                        try:
                            await callback(positions_data)
                        except Exception as e:
                            logger.error(f"Error in position update callback: {e}")
                    
                    return positions_data
                else:
                    logger.error(f"Failed to get positions: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error getting positions from HFT engine: {e}")
            return {}
    
    async def adjust_position(self, symbol: str, target_position: float, 
                            reason: str = "risk_management") -> bool:
        """
        Request position adjustment from HFT engine
        
        Args:
            symbol: Trading symbol
            target_position: Target position size
            reason: Reason for adjustment
            
        Returns:
            Success status
        """
        try:
            if not self.connected:
                logger.warning("HFT engine not connected")
                return False
            
            adjustment_request = {
                'symbol': symbol,
                'target_position': target_position,
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'priority': 'high' if 'emergency' in reason.lower() else 'normal'
            }
            
            async with self.session.post(
                f"{self.config.engine_endpoint}/positions/adjust",
                json=adjustment_request
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    logger.info(f"Position adjustment requested for {symbol}: "
                              f"target {target_position}, reason: {reason}")
                    
                    return result.get('success', False)
                else:
                    logger.error(f"Failed to adjust position: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error adjusting position in HFT engine: {e}")
            return False
    
    async def close_position(self, symbol: str, reason: str = "risk_management") -> bool:
        """
        Request emergency position closure
        
        Args:
            symbol: Trading symbol
            reason: Reason for closure
            
        Returns:
            Success status
        """
        try:
            if not self.connected:
                logger.warning("HFT engine not connected")
                return False
            
            closure_request = {
                'symbol': symbol,
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'priority': 'emergency'
            }
            
            async with self.session.post(
                f"{self.config.engine_endpoint}/positions/close",
                json=closure_request
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    logger.warning(f"Emergency position closure requested for {symbol}: {reason}")
                    
                    return result.get('success', False)
                else:
                    logger.error(f"Failed to close position: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error closing position in HFT engine: {e}")
            return False
    
    async def submit_risk_control_signal(self, signal_type: str, 
                                       signal_data: Dict[str, Any]) -> bool:
        """Submit risk control signal to HFT engine"""
        try:
            if not self.connected:
                logger.warning("HFT engine not connected")
                return False
            
            risk_signal = {
                'signal_type': signal_type,
                'data': signal_data,
                'timestamp': datetime.now().isoformat(),
                'source': 'risk_management_system'
            }
            
            async with self.session.post(
                f"{self.config.engine_endpoint}/risk/control",
                json=risk_signal
            ) as response:
                if response.status == 200:
                    logger.info(f"Risk control signal sent: {signal_type}")
                    return True
                else:
                    logger.error(f"Failed to send risk control signal: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending risk control signal: {e}")
            return False
    
    async def get_market_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get active market orders"""
        try:
            if not self.connected:
                return []
            
            url = f"{self.config.engine_endpoint}/orders"
            if symbol:
                url += f"?symbol={symbol}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get orders: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting market orders: {e}")
            return []
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel market order"""
        try:
            if not self.connected:
                return False
            
            cancel_request = {
                'order_id': order_id,
                'timestamp': datetime.now().isoformat(),
                'reason': 'risk_management'
            }
            
            async with self.session.delete(
                f"{self.config.engine_endpoint}/orders/{order_id}",
                json=cancel_request
            ) as response:
                if response.status == 200:
                    logger.info(f"Order cancelled: {order_id}")
                    return True
                else:
                    logger.error(f"Failed to cancel order: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False
    
    async def get_trading_statistics(self) -> Dict[str, Any]:
        """Get trading statistics from HFT engine"""
        try:
            if not self.connected:
                return {}
            
            async with self.session.get(f"{self.config.engine_endpoint}/statistics") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get trading statistics: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error getting trading statistics: {e}")
            return {}
    
    async def set_position_limits(self, symbol: str, max_position: float,
                                max_loss: float) -> bool:
        """Set position limits for symbol"""
        try:
            if not self.connected:
                return False
            
            limits_request = {
                'symbol': symbol,
                'max_position': max_position,
                'max_loss': max_loss,
                'timestamp': datetime.now().isoformat()
            }
            
            async with self.session.post(
                f"{self.config.engine_endpoint}/limits/position",
                json=limits_request
            ) as response:
                if response.status == 200:
                    logger.info(f"Position limits set for {symbol}: max {max_position}, max loss {max_loss}")
                    return True
                else:
                    logger.error(f"Failed to set position limits: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error setting position limits: {e}")
            return False
    
    async def enable_emergency_mode(self, reason: str = "risk_management") -> bool:
        """Enable emergency trading mode"""
        try:
            if not self.connected:
                return False
            
            emergency_request = {
                'enabled': True,
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            }
            
            async with self.session.post(
                f"{self.config.engine_endpoint}/emergency/enable",
                json=emergency_request
            ) as response:
                if response.status == 200:
                    logger.warning(f"Emergency mode enabled: {reason}")
                    return True
                else:
                    logger.error(f"Failed to enable emergency mode: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error enabling emergency mode: {e}")
            return False
    
    async def disable_emergency_mode(self) -> bool:
        """Disable emergency trading mode"""
        try:
            if not self.connected:
                return False
            
            async with self.session.post(f"{self.config.engine_endpoint}/emergency/disable") as response:
                if response.status == 200:
                    logger.info("Emergency mode disabled")
                    return True
                else:
                    logger.error(f"Failed to disable emergency mode: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error disabling emergency mode: {e}")
            return False
    
    def add_position_update_callback(self, callback):
        """Add callback for position updates"""
        self.position_updates_callbacks.append(callback)
    
    # Background monitoring
    
    async def monitor_connection(self):
        """Monitor HFT engine connection"""
        while True:
            try:
                if not self.connected:
                    # Attempt to reconnect
                    await self._attempt_reconnect()
                else:
                    # Check connection health
                    health_ok = await self._check_connection_health()
                    if not health_ok:
                        self.connected = False
                        logger.error("HFT engine connection lost")
                
                await asyncio.sleep(self.config.sync_interval)
                
            except Exception as e:
                logger.error(f"Error in HFT connection monitoring: {e}")
                await asyncio.sleep(5)
    
    async def _attempt_reconnect(self):
        """Attempt to reconnect to HFT engine"""
        if self.retry_count >= self.config.max_retries:
            logger.error(f"Max reconnection attempts reached ({self.config.max_retries})")
            return
        
        self.retry_count += 1
        logger.info(f"Attempting to reconnect to HFT engine (attempt {self.retry_count})")
        
        try:
            await self.initialize()
            self.connected = True
            self.retry_count = 0
            logger.info("Successfully reconnected to HFT engine")
            
        except Exception as e:
            logger.error(f"Reconnection attempt failed: {e}")
    
    async def _check_connection_health(self) -> bool:
        """Check connection health"""
        try:
            if not self.session:
                return False
            
            async with self.session.get(f"{self.config.engine_endpoint}/ping") as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Connection health check failed: {e}")
            return False
    
    # Utility methods
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return {
            'component': 'hft_engine',
            'healthy': self.connected,
            'connected': self.connected,
            'last_sync': self.last_position_sync.isoformat() if self.last_position_sync else None,
            'retry_count': self.retry_count,
            'positions_count': len(self.current_positions),
            'buffer_size': len(self.position_buffer)
        }
    
    async def get_status_summary(self) -> Dict[str, Any]:
        """Get status summary"""
        positions = await self.get_current_positions()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'connection_status': 'connected' if self.connected else 'disconnected',
            'last_sync': self.last_position_sync.isoformat() if self.last_position_sync else None,
            'current_positions': len(positions),
            'position_buffer_size': len(self.position_buffer),
            'retry_count': self.retry_count
        }
    
    async def stop(self):
        """Stop HFT engine connector"""
        try:
            if self.session:
                await self.session.close()
            
            self.connected = False
            logger.info("HFT Engine connector stopped")
            
        except Exception as e:
            logger.error(f"Error stopping HFT engine connector: {e}")
    
    async def export_connection_data(self, format_type: str = 'json') -> str:
        """Export connection data"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'status_summary': await self.get_status_summary(),
            'current_positions': self.current_positions,
            'health_check': await self.health_check()
        }
        
        if format_type.lower() == 'json':
            return json.dumps(export_data, indent=2, default=str)
        else:
            return str(export_data)