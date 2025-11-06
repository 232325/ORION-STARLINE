"""
AI Trading System - WebSocket Manager
Real-time WebSocket ulanishlari va xabar almashish
"""

import json
import asyncio
from typing import Dict, List, Optional, Set, Any
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect
import uuid
import logging

from ..models.schemas import WebSocketMessage, WebSocketConnection
from ..config.settings import settings

logger = logging.getLogger(__name__)

class ConnectionManager:
    """WebSocket ulanishlarini boshqarish"""
    
    def __init__(self):
        # Active connections storage
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {
            "trading": {},
            "quantum": {},
            "blockchain": {},
            "dao": {},
            "hft": {},
            "nft": {},
            "general": {}
        }
        
        # Connection metadata
        self.connection_info: Dict[str, WebSocketConnection] = {}
        
        # User sessions
        self.user_sessions: Dict[str, List[str]] = {}
        
        # Broadcasting queues
        self.broadcast_queues: Dict[str, List[str]] = {}
        
        # Heartbeat tracking
        self.last_ping: Dict[str, datetime] = {}
        
        # Statistics
        self.stats = {
            "total_connections": 0,
            "total_messages": 0,
            "peak_connections": 0
        }
    
    async def initialize(self):
        """WebSocket manager'ni boshlash"""
        logger.info("WebSocket Manager tayyorlandi")
        
        # Start background tasks
        asyncio.create_task(self._heartbeat_task())
        asyncio.create_task(self._cleanup_task())
        asyncio.create_task(self._broadcast_task())
    
    async def connect(self, websocket: WebSocket, connection_type: str, user_id: Optional[str] = None):
        """Yangi WebSocket ulanishni qabul qilish"""
        await websocket.accept()
        
        connection_id = str(uuid.uuid4())
        
        # Store connection
        if connection_type not in self.active_connections:
            self.active_connections[connection_type] = {}
        
        self.active_connections[connection_type][connection_id] = websocket
        
        # Store connection info
        self.connection_info[connection_id] = WebSocketConnection(
            websocket_id=connection_id,
            user_id=user_id,
            connection_type=connection_type,
            connected_at=datetime.utcnow(),
            last_activity=datetime.utcnow()
        )
        
        # Associate user session
        if user_id:
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = []
            self.user_sessions[user_id].append(connection_id)
        
        # Track last ping
        self.last_ping[connection_id] = datetime.utcnow()
        
        # Update statistics
        self.stats["total_connections"] += 1
        total_active = self.get_connection_count()
        if total_active > self.stats["peak_connections"]:
            self.stats["peak_connections"] = total_active
        
        logger.info(f"WebSocket ulanish: {connection_id} ({connection_type})")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "connection_id": connection_id,
            "connection_type": connection_type,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "WebSocket ulanish muvaffaqiyatli o'rnatildi"
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """WebSocket ulanishni uzish"""
        connection_id = None
        connection_type = None
        user_id = None
        
        # Find the connection
        for conn_type, connections in self.active_connections.items():
            for conn_id, ws in connections.items():
                if ws == websocket:
                    connection_id = conn_id
                    connection_type = conn_type
                    user_id = self.connection_info.get(conn_id, {}).user_id
                    break
            if connection_id:
                break
        
        if connection_id:
            # Remove from active connections
            if connection_type in self.active_connections:
                self.active_connections[connection_type].pop(connection_id, None)
            
            # Remove connection info
            self.connection_info.pop(connection_id, None)
            
            # Remove from user sessions
            if user_id and user_id in self.user_sessions:
                if connection_id in self.user_sessions[user_id]:
                    self.user_sessions[user_id].remove(connection_id)
                if not self.user_sessions[user_id]:
                    self.user_sessions[user_id] = []
            
            # Remove ping tracking
            self.last_ping.pop(connection_id, None)
            
            # Update statistics
            self.stats["total_connections"] = max(0, self.stats["total_connections"] - 1)
            
            logger.info(f"WebSocket ulanish uzildi: {connection_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Shaxsiy xabar yuborish"""
        try:
            await websocket.send_text(json.dumps(message))
            self.stats["total_messages"] += 1
        except Exception as e:
            logger.error(f"Xabar yuborishda xato: {e}")
            self.disconnect(websocket)
    
    async def send_message_to_user(self, user_id: str, message: Dict[str, Any]):
        """Foydalanuvchiga xabar yuborish"""
        if user_id in self.user_sessions:
            for connection_id in self.user_sessions[user_id]:
                for conn_type, connections in self.active_connections.items():
                    if connection_id in connections:
                        websocket = connections[connection_id]
                        try:
                            await self.send_personal_message(message, websocket)
                        except:
                            self.disconnect(websocket)
                        break
    
    async def broadcast_message(self, message: Dict[str, Any], connection_type: Optional[str] = None):
        """Barcha ulanishlarga xabar yuborish"""
        target_connections = (
            {connection_type: self.active_connections[connection_type]} 
            if connection_type 
            else self.active_connections
        )
        
        for conn_type, connections in target_connections.items():
            tasks = []
            for connection_id, websocket in connections.items():
                task = self.send_personal_message(message, websocket)
                tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast_to_type(self, connection_type: str, message: Dict[str, Any]):
        """Ma'lum turdagi ulanishlarga xabar yuborish"""
        if connection_type in self.active_connections:
            connections = self.active_connections[connection_type]
            tasks = []
            
            for connection_id, websocket in connections.items():
                task = self.send_personal_message(message, websocket)
                tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_connection_count(self, connection_type: Optional[str] = None) -> int:
        """Ulanishlar sonini olish"""
        if connection_type:
            if connection_type in self.active_connections:
                return len(self.active_connections[connection_type])
            return 0
        
        total = 0
        for connections in self.active_connections.values():
            total += len(connections)
        return total
    
    def get_user_connections(self, user_id: str) -> List[str]:
        """Foydalanuvchi ulanishlarini olish"""
        return self.user_sessions.get(user_id, [])
    
    def get_connection_info(self, connection_id: str) -> Optional[WebSocketConnection]:
        """Ulanish ma'lumotlarini olish"""
        return self.connection_info.get(connection_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistikani olish"""
        total_connections = self.get_connection_count()
        
        return {
            **self.stats,
            "active_connections": total_connections,
            "connections_by_type": {
                conn_type: len(connections)
                for conn_type, connections in self.active_connections.items()
            },
            "total_users": len(self.user_sessions),
            "uptime": datetime.utcnow().isoformat()
        }
    
    async def _heartbeat_task(self):
        """Heartbeat vazifasi - ulanishlarni tekshirish"""
        while True:
            try:
                await asyncio.sleep(settings.WEBSOCKET_PING_INTERVAL)
                
                current_time = datetime.utcnow()
                disconnected = []
                
                for connection_id, last_ping in self.last_ping.items():
                    if current_time - last_ping > timedelta(seconds=settings.WEBSOCKET_PING_TIMEOUT):
                        disconnected.append(connection_id)
                
                # Disconnect stale connections
                for connection_id in disconnected:
                    for conn_type, connections in self.active_connections.items():
                        if connection_id in connections:
                            websocket = connections[connection_id]
                            try:
                                await websocket.send_text(json.dumps({
                                    "type": "ping",
                                    "timestamp": current_time.isoformat()
                                }))
                            except:
                                self.disconnect(websocket)
                            break
                
                # Send broadcast ping
                await self.broadcast_message({
                    "type": "system_ping",
                    "timestamp": current_time.isoformat()
                })
                
            except Exception as e:
                logger.error(f"Heartbeat task xatosi: {e}")
    
    async def _cleanup_task(self):
        """Tozalash vazifasi - eski ma'lumotlarni o'chirish"""
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                
                current_time = datetime.utcnow()
                cutoff_time = current_time - timedelta(hours=24)
                
                # Clean up old connection info
                expired_connections = []
                for connection_id, info in self.connection_info.items():
                    if info.connected_at < cutoff_time:
                        expired_connections.append(connection_id)
                
                for connection_id in expired_connections:
                    self.connection_info.pop(connection_id, None)
                    self.last_ping.pop(connection_id, None)
                
                logger.info(f"Tozalash yakunlandi: {len(expired_connections)} eski ulanish")
                
            except Exception as e:
                logger.error(f"Cleanup task xatosi: {e}")
    
    async def _broadcast_task(self):
        """Broadcast vazifasi - ma'lumotlarni tarqatish"""
        while True:
            try:
                await asyncio.sleep(1)  # Check every second
                
                # Trading signals
                await self._broadcast_trading_data()
                await self._broadcast_quantum_data()
                await self._broadcast_blockchain_data()
                
            except Exception as e:
                logger.error(f"Broadcast task xatosi: {e}")
    
    async def _broadcast_trading_data(self):
        """Trading ma'lumotlarini tarqatish"""
        # Mock trading data - in production, get from real trading engine
        trading_data = {
            "type": "trading_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "BTC/USDT": {
                    "price": 45000.0 + (datetime.utcnow().microsecond / 1000000),
                    "volume": 150.5,
                    "signal": "BUY"
                },
                "ETH/USDT": {
                    "price": 2800.0 + (datetime.utcnow().microsecond / 1000000),
                    "volume": 75.2,
                    "signal": "HOLD"
                }
            }
        }
        
        await self.broadcast_to_type("trading", trading_data)
    
    async def _broadcast_quantum_data(self):
        """Quantum ma'lumotlarini tarqatish"""
        # Mock quantum data - in production, get from quantum simulator
        quantum_data = {
            "type": "quantum_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "superposition_state": "ENTANGLED",
                "coherence_time": 15.2,
                "fidelity": 0.987 + (datetime.utcnow().microsecond / 10000000),
                "qbit_count": 256
            }
        }
        
        await self.broadcast_to_type("quantum", quantum_data)
    
    async def _broadcast_blockchain_data(self):
        """Blockchain ma'lumotlarini tarqatish"""
        # Mock blockchain data - in production, get from blockchain nodes
        blockchain_data = {
            "type": "blockchain_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "latest_block": 18567492,
                "gas_price": 25.5,
                "pending_transactions": 47,
                "network_hashrate": "750 TH/s"
            }
        }
        
        await self.broadcast_to_type("blockchain", blockchain_data)

# Global connection manager instance
connection_manager = ConnectionManager()