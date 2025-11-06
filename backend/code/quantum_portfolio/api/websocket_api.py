"""
Quantum Portfolio WebSocket API
==============================

Real-time WebSocket API for quantum portfolio optimization.
Live progress updates va instant notifications.

Muallif: Quantum Portfolio Team
 Sana: 2025-11-03
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
import uuid

logger = logging.getLogger(__name__)

class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.portfolio_subscriptions: Dict[str, Set[str]] = {}  # portfolio_id -> set of connection_ids
        
    async def connect(self, websocket: WebSocket, portfolio_id: str):
        """Accept WebSocket connection and subscribe to portfolio updates"""
        await websocket.accept()
        
        if portfolio_id not in self.active_connections:
            self.active_connections[portfolio_id] = set()
        
        self.active_connections[portfolio_id].add(websocket)
        
        logger.info(f"WebSocket connected to portfolio {portfolio_id}")
        
    def disconnect(self, websocket: WebSocket, portfolio_id: str):
        """Remove WebSocket connection"""
        if portfolio_id in self.active_connections:
            self.active_connections[portfolio_id].discard(websocket)
            
            # Clean up empty connections
            if not self.active_connections[portfolio_id]:
                del self.active_connections[portfolio_id]
                
        logger.info(f"WebSocket disconnected from portfolio {portfolio_id}")
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {str(e)}")
            
    async def broadcast_to_portfolio(self, portfolio_id: str, message: str):
        """Broadcast message to all connections for a portfolio"""
        if portfolio_id in self.active_connections:
            disconnected = set()
            
            for connection in self.active_connections[portfolio_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Failed to send message to connection: {str(e)}")
                    disconnected.add(connection)
                    
            # Remove disconnected connections
            for conn in disconnected:
                self.active_connections[portfolio_id].discard(conn)

class QuantumPortfolioWebSocketAPI:
    """WebSocket API for real-time quantum portfolio updates"""
    
    def __init__(self, quantum_api=None):
        self.quantum_api = quantum_api
        self.connection_manager = ConnectionManager()
        self.logger = logging.getLogger(__name__)
        
    async def connect_websocket(self, websocket: WebSocket, portfolio_id: str):
        """Connect WebSocket for portfolio updates"""
        await self.connection_manager.connect(websocket, portfolio_id)
        
        try:
            # Send welcome message
            welcome_message = {
                "type": "connection_established",
                "portfolio_id": portfolio_id,
                "timestamp": datetime.now().isoformat(),
                "message": f"Connected to portfolio {portfolio_id} updates"
            }
            await websocket.send_text(json.dumps(welcome_message))
            
            # Send current status if available
            await self._send_current_status(websocket, portfolio_id)
            
            # Keep connection alive
            while True:
                try:
                    # Wait for messages from client
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                    
                    # Process client messages
                    await self._process_client_message(websocket, portfolio_id, data)
                    
                except asyncio.TimeoutError:
                    # Send keep-alive ping
                    ping_message = {
                        "type": "ping",
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_text(json.dumps(ping_message))
                    
                except WebSocketDisconnect:
                    break
                    
        except WebSocketDisconnect:
            pass
        except Exception as e:
            self.logger.error(f"WebSocket error: {str(e)}")
        finally:
            self.connection_manager.disconnect(websocket, portfolio_id)
            
    async def _process_client_message(self, websocket: WebSocket, portfolio_id: str, data: str):
        """Process incoming client messages"""
        try:
            message = json.loads(data)
            
            if message.get("type") == "ping":
                # Respond to ping
                pong_message = {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_text(json.dumps(pong_message))
                
            elif message.get("type") == "get_status":
                # Send current portfolio status
                await self._send_current_status(websocket, portfolio_id)
                
            elif message.get("type") == "subscribe_metric":
                # Subscribe to specific metric updates
                metric = message.get("metric")
                await self._send_metric_subscription(websocket, portfolio_id, metric)
                
            else:
                # Unknown message type
                error_message = {
                    "type": "error",
                    "message": f"Unknown message type: {message.get('type')}"
                }
                await websocket.send_text(json.dumps(error_message))
                
        except json.JSONDecodeError:
            error_message = {
                "type": "error",
                "message": "Invalid JSON message"
            }
            await websocket.send_text(json.dumps(error_message))
            
    async def _send_current_status(self, websocket: WebSocket, portfolio_id: str):
        """Send current portfolio status"""
        try:
            if self.quantum_api and portfolio_id in self.quantum_api.optimization_history:
                result = self.quantum_api.optimization_history[portfolio_id]
                
                status_message = {
                    "type": "portfolio_status",
                    "portfolio_id": portfolio_id,
                    "status": "completed",
                    "data": {
                        "expected_return": result.expected_return,
                        "risk": result.risk,
                        "sharpe_ratio": result.sharpe_ratio,
                        "algorithm_used": result.algorithm_used,
                        "computation_time": result.computation_time,
                        "timestamp": result.timestamp.isoformat()
                    }
                }
                
                await websocket.send_text(json.dumps(status_message))
            else:
                # Portfolio not found or still processing
                status_message = {
                    "type": "portfolio_status",
                    "portfolio_id": portfolio_id,
                    "status": "not_found_or_processing",
                    "message": "Portfolio optimization in progress or not found"
                }
                
                await websocket.send_text(json.dumps(status_message))
                
        except Exception as e:
            self.logger.error(f"Failed to send current status: {str(e)}")
            
    async def _send_metric_subscription(self, websocket: WebSocket, portfolio_id: str, metric: str):
        """Send metric subscription confirmation"""
        message = {
            "type": "metric_subscription",
            "portfolio_id": portfolio_id,
            "metric": metric,
            "status": "subscribed",
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(message))
        
    async def notify_optimization_start(self, portfolio_id: str, assets: List[str], 
                                      algorithm: str):
        """Notify clients that optimization has started"""
        message = {
            "type": "optimization_started",
            "portfolio_id": portfolio_id,
            "assets": assets,
            "algorithm": algorithm,
            "timestamp": datetime.now().isoformat(),
            "message": f"Portfolio optimization started with {algorithm} algorithm"
        }
        
        await self.connection_manager.broadcast_to_portfolio(
            portfolio_id, 
            json.dumps(message)
        )
        
    async def notify_optimization_progress(self, portfolio_id: str, progress: float, 
                                         iteration: int, total_iterations: int):
        """Notify clients of optimization progress"""
        message = {
            "type": "optimization_progress",
            "portfolio_id": portfolio_id,
            "progress": progress,
            "iteration": iteration,
            "total_iterations": total_iterations,
            "timestamp": datetime.now().isoformat(),
            "message": f"Optimization {progress:.1%} complete"
        }
        
        await self.connection_manager.broadcast_to_portfolio(
            portfolio_id, 
            json.dumps(message)
        )
        
    async def notify_optimization_complete(self, portfolio_id: str, expected_return: float, 
                                         risk: float):
        """Notify clients that optimization is complete"""
        message = {
            "type": "optimization_completed",
            "portfolio_id": portfolio_id,
            "results": {
                "expected_return": expected_return,
                "risk": risk,
                "sharpe_ratio": (expected_return - 0.02) / risk if risk > 0 else 0
            },
            "timestamp": datetime.now().isoformat(),
            "message": "Portfolio optimization completed successfully"
        }
        
        await self.connection_manager.broadcast_to_portfolio(
            portfolio_id, 
            json.dumps(message)
        )
            
    async def notify_efficient_frontier_ready(self, portfolio_id: str, n_points: int):
        """Notify clients that efficient frontier is ready"""
        message = {
            "type": "efficient_frontier_ready",
            "portfolio_id": portfolio_id,
            "n_points": n_points,
            "timestamp": datetime.now().isoformat(),
            "message": "Efficient frontier computation completed"
        }
        
        await self.connection_manager.broadcast_to_portfolio(
            portfolio_id, 
            json.dumps(message)
        )
        
    async def notify_quantum_metrics_update(self, portfolio_id: str, quantum_metrics: Dict[str, Any]):
        """Notify clients of quantum metrics updates"""
        message = {
            "type": "quantum_metrics_update",
            "portfolio_id": portfolio_id,
            "quantum_metrics": quantum_metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.connection_manager.broadcast_to_portfolio(
            portfolio_id, 
            json.dumps(message)
        )
        
    async def notify_system_status(self, status: str, details: Dict[str, Any] = None):
        """Notify all connected clients of system status changes"""
        message = {
            "type": "system_status",
            "status": status,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Broadcast to all portfolios
        for portfolio_id in self.connection_manager.active_connections:
            await self.connection_manager.broadcast_to_portfolio(
                portfolio_id, 
                json.dumps(message)
            )
            
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        total_connections = sum(len(connections) for connections in 
                              self.connection_manager.active_connections.values())
        
        return {
            "total_connections": total_connections,
            "active_portfolios": list(self.connection_manager.active_connections.keys()),
            "connections_per_portfolio": {
                pid: len(connections) 
                for pid, connections in self.connection_manager.active_connections.items()
            },
            "timestamp": datetime.now().isoformat()
        }
        
    async def broadcast_optimization_alert(self, portfolio_id: str, alert_type: str, 
                                         message: str, details: Dict[str, Any] = None):
        """Broadcast optimization alerts to clients"""
        alert_message = {
            "type": "optimization_alert",
            "portfolio_id": portfolio_id,
            "alert_type": alert_type,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        
        await self.connection_manager.broadcast_to_portfolio(
            portfolio_id, 
            json.dumps(alert_message)
        )
        
    async def send_real_time_metrics(self, portfolio_id: str, metrics: Dict[str, Any]):
        """Send real-time portfolio metrics"""
        metrics_message = {
            "type": "real_time_metrics",
            "portfolio_id": portfolio_id,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.connection_manager.broadcast_to_portfolio(
            portfolio_id, 
            json.dumps(metrics_message)
        )

# Example WebSocket client handler
class QuantumPortfolioWebSocketClient:
    """WebSocket client for testing real-time updates"""
    
    def __init__(self, websocket_url: str):
        self.websocket_url = websocket_url
        self.websocket: Optional[WebSocket] = None
        
    async def connect(self, portfolio_id: str):
        """Connect to WebSocket"""
        # This would typically use websockets library
        # For demo purposes, showing structure
        self.logger = logging.getLogger(__name__)
        
        try:
            # Create WebSocket connection
            # self.websocket = await websockets.connect(f"{self.websocket_url}/ws/portfolio/{portfolio_id}")
            
            self.logger.info(f"Connected to portfolio {portfolio_id}")
            
            # Start listening for messages
            await self._listen_for_messages(portfolio_id)
            
        except Exception as e:
            self.logger.error(f"WebSocket connection failed: {str(e)}")
            
    async def _listen_for_messages(self, portfolio_id: str):
        """Listen for WebSocket messages"""
        try:
            while True:
                # Receive message
                # message = await self.websocket.recv()
                message = "{}"  # Placeholder
                
                # Parse message
                data = json.loads(message)
                await self._handle_message(data, portfolio_id)
                
        except Exception as e:
            self.logger.error(f"WebSocket listening error: {str(e)}")
            
    async def _handle_message(self, message: Dict[str, Any], portfolio_id: str):
        """Handle incoming WebSocket messages"""
        message_type = message.get("type")
        
        if message_type == "optimization_started":
            print(f"Optimization started for portfolio {portfolio_id}")
            
        elif message_type == "optimization_progress":
            progress = message.get("progress", 0)
            print(f"Optimization progress: {progress:.1%}")
            
        elif message_type == "optimization_completed":
            results = message.get("results", {})
            print(f"Optimization completed! Expected return: {results.get('expected_return', 0):.2%}")
            
        elif message_type == "real_time_metrics":
            metrics = message.get("metrics", {})
            print(f"Real-time metrics update: {metrics}")
            
        else:
            print(f"Received message: {message}")
            
    async def send_message(self, message: Dict[str, Any]):
        """Send message to WebSocket"""
        if self.websocket:
            await self.websocket.send_text(json.dumps(message))

# Usage example
async def example_websocket_usage():
    """Example WebSocket usage"""
    # Create WebSocket API
    websocket_api = QuantumPortfolioWebSocketAPI()
    
    # Simulate optimization notifications
    portfolio_id = "example_portfolio"
    
    # Notify start
    await websocket_api.notify_optimization_start(
        portfolio_id, 
        ["AAPL", "GOOGL", "MSFT"], 
        "VQE"
    )
    
    # Simulate progress updates
    for i in range(10):
        await websocket_api.notify_optimization_progress(
            portfolio_id, 
            (i + 1) * 0.1,  # 10% increments
            i + 1,
            10
        )
        await asyncio.sleep(1)
    
    # Notify completion
    await websocket_api.notify_optimization_complete(
        portfolio_id, 
        0.12,  # 12% expected return
        0.18   # 18% risk
    )
    
    # Get connection statistics
    stats = await websocket_api.get_connection_stats()
    print(f"WebSocket statistics: {stats}")

if __name__ == "__main__":
    asyncio.run(example_websocket_usage())