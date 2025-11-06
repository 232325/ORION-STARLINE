"""
AI Trading Evolution - WebSocket Manager
========================================
Real-time data streaming via WebSocket

Author: MiniMax Agent
Version: 1.0.0
Date: 2025-11-04
"""

import asyncio
import json
import logging
from typing import Dict, Set, Any, Optional, List
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        # Active connections: {client_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Subscriptions: {channel: Set[client_id]}
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)
        
        # Client metadata: {client_id: metadata}
        self.client_metadata: Dict[str, Dict[str, Any]] = {}
        
        logger.info("WebSocket Connection Manager initialized")
    
    async def connect(self, websocket: WebSocket, client_id: str) -> bool:
        """Yangi client ulanishi"""
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            self.client_metadata[client_id] = {
                "connected_at": datetime.utcnow().isoformat(),
                "subscriptions": []
            }
            logger.info(f"Client connected: {client_id}")
            return True
        except Exception as e:
            logger.error(f"Connection error for {client_id}: {e}")
            return False
    
    def disconnect(self, client_id: str):
        """Client uzilishi"""
        if client_id in self.active_connections:
            # Remove from all subscriptions
            for channel in list(self.subscriptions.keys()):
                self.subscriptions[channel].discard(client_id)
                if not self.subscriptions[channel]:
                    del self.subscriptions[channel]
            
            # Remove connection
            del self.active_connections[client_id]
            del self.client_metadata[client_id]
            logger.info(f"Client disconnected: {client_id}")
    
    async def subscribe(self, client_id: str, channel: str) -> bool:
        """Client'ni channelga obuna qilish"""
        if client_id not in self.active_connections:
            return False
        
        self.subscriptions[channel].add(client_id)
        self.client_metadata[client_id]["subscriptions"].append(channel)
        logger.info(f"Client {client_id} subscribed to {channel}")
        return True
    
    async def unsubscribe(self, client_id: str, channel: str) -> bool:
        """Client'ni channeldan obunani bekor qilish"""
        if client_id not in self.active_connections:
            return False
        
        self.subscriptions[channel].discard(client_id)
        if channel in self.client_metadata[client_id]["subscriptions"]:
            self.client_metadata[client_id]["subscriptions"].remove(channel)
        
        logger.info(f"Client {client_id} unsubscribed from {channel}")
        return True
    
    async def send_personal_message(self, client_id: str, message: Dict[str, Any]):
        """Bitta clientga xabar yuborish"""
        if client_id not in self.active_connections:
            return
        
        try:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message to {client_id}: {e}")
            self.disconnect(client_id)
    
    async def broadcast(self, channel: str, message: Dict[str, Any]):
        """Channel'ga obuna bo'lgan barcha clientlarga yuborish"""
        if channel not in self.subscriptions:
            return
        
        disconnected_clients = []
        
        for client_id in self.subscriptions[channel]:
            try:
                websocket = self.active_connections.get(client_id)
                if websocket:
                    await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Cleanup disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def broadcast_all(self, message: Dict[str, Any]):
        """Barcha clientlarga yuborish"""
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Cleanup disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Connection statistikasi"""
        return {
            "total_connections": len(self.active_connections),
            "total_channels": len(self.subscriptions),
            "channels": {
                channel: len(clients)
                for channel, clients in self.subscriptions.items()
            }
        }


class WebSocketStreamer:
    """Real-time data streaming"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
        self.streaming_tasks: Dict[str, asyncio.Task] = {}
        logger.info("WebSocket Streamer initialized")
    
    async def start_market_stream(self, symbol: str, interval: int = 1):
        """Market data streaming"""
        channel = f"market:{symbol}"
        
        async def stream():
            while True:
                try:
                    # Mock data - production'da real API'dan oling
                    data = {
                        "type": "market_data",
                        "channel": channel,
                        "data": {
                            "symbol": symbol,
                            "price": 45000.0,  # Mock price
                            "volume": 123.45,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }
                    await self.manager.broadcast(channel, data)
                    await asyncio.sleep(interval)
                except Exception as e:
                    logger.error(f"Market stream error for {symbol}: {e}")
                    break
        
        task = asyncio.create_task(stream())
        self.streaming_tasks[channel] = task
    
    async def start_signals_stream(self, strategy: str, interval: int = 5):
        """Trading signals streaming"""
        channel = f"signals:{strategy}"
        
        async def stream():
            while True:
                try:
                    # Mock data
                    data = {
                        "type": "trading_signal",
                        "channel": channel,
                        "data": {
                            "strategy": strategy,
                            "signal": "BUY",
                            "confidence": 0.85,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }
                    await self.manager.broadcast(channel, data)
                    await asyncio.sleep(interval)
                except Exception as e:
                    logger.error(f"Signals stream error for {strategy}: {e}")
                    break
        
        task = asyncio.create_task(stream())
        self.streaming_tasks[channel] = task
    
    async def start_portfolio_stream(self, user_id: str, interval: int = 2):
        """Portfolio updates streaming"""
        channel = f"portfolio:{user_id}"
        
        async def stream():
            while True:
                try:
                    # Mock data
                    data = {
                        "type": "portfolio_update",
                        "channel": channel,
                        "data": {
                            "user_id": user_id,
                            "total_value": 100000.0,
                            "pnl": 5000.0,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }
                    await self.manager.broadcast(channel, data)
                    await asyncio.sleep(interval)
                except Exception as e:
                    logger.error(f"Portfolio stream error for {user_id}: {e}")
                    break
        
        task = asyncio.create_task(stream())
        self.streaming_tasks[channel] = task
    
    def stop_stream(self, channel: str):
        """Stream'ni to'xtatish"""
        if channel in self.streaming_tasks:
            self.streaming_tasks[channel].cancel()
            del self.streaming_tasks[channel]
            logger.info(f"Stream stopped: {channel}")


# Global instance
manager = ConnectionManager()
streamer = WebSocketStreamer(manager)


async def handle_websocket_message(client_id: str, message: Dict[str, Any]):
    """WebSocket xabarlarini qayta ishlash"""
    
    action = message.get("action")
    
    if action == "subscribe":
        channel = message.get("channel")
        if channel:
            await manager.subscribe(client_id, channel)
            
            # Start streaming if needed
            if channel.startswith("market:"):
                symbol = channel.split(":")[1]
                await streamer.start_market_stream(symbol)
            elif channel.startswith("signals:"):
                strategy = channel.split(":")[1]
                await streamer.start_signals_stream(strategy)
            elif channel.startswith("portfolio:"):
                user_id = channel.split(":")[1]
                await streamer.start_portfolio_stream(user_id)
            
            await manager.send_personal_message(client_id, {
                "type": "subscription_success",
                "channel": channel,
                "message": f"Subscribed to {channel}"
            })
    
    elif action == "unsubscribe":
        channel = message.get("channel")
        if channel:
            await manager.unsubscribe(client_id, channel)
            await manager.send_personal_message(client_id, {
                "type": "unsubscription_success",
                "channel": channel,
                "message": f"Unsubscribed from {channel}"
            })
    
    elif action == "ping":
        await manager.send_personal_message(client_id, {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    elif action == "get_stats":
        stats = manager.get_stats()
        await manager.send_personal_message(client_id, {
            "type": "stats",
            "data": stats
        })
    
    else:
        await manager.send_personal_message(client_id, {
            "type": "error",
            "message": f"Unknown action: {action}"
        })
