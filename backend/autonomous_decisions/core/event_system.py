"""
Event System

Event-driven architecture uchun event bus
"""

from typing import Dict, List, Callable, Any, Optional
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
import threading
import asyncio

@dataclass
class Event:
    """Event data structure"""
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str = "system"
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = f"{self.event_type}_{self.timestamp.isoformat()}"

class EventSystem:
    """
    Event bus va subscription management
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._subscriptions: Dict[str, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history_size = 1000
        self._lock = threading.RLock()
        
        # Event types
        self.event_types = {
            "performance_update",
            "trade_executed", 
            "governance_vote",
            "decision_executed",
            "risk_alert",
            "system_error",
            "strategy_change"
        }
    
    def subscribe(self, event_type: str, callback: Callable[[Dict], None]):
        """Event ga subscribe qilish"""
        with self._lock:
            if event_type not in self._subscriptions:
                self._subscriptions[event_type] = []
            
            self._subscriptions[event_type].append(callback)
            self.logger.info(f"Subscribed to {event_type}: {callback.__name__}")
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Event dan unsubscribe qilish"""
        with self._lock:
            if event_type in self._subscriptions:
                try:
                    self._subscriptions[event_type].remove(callback)
                    self.logger.info(f"Unsubscribed from {event_type}: {callback.__name__}")
                except ValueError:
                    self.logger.warning(f"Callback not found for {event_type}")
    
    def publish(self, event_type: str, data: Dict[str, Any], source: str = "system"):
        """Event ni publish qilish"""
        event = Event(
            event_type=event_type,
            data=data,
            timestamp=datetime.now(),
            source=source
        )
        
        # Event history ga qo'shish
        with self._lock:
            self._event_history.append(event)
            
            # History size limit
            if len(self._event_history) > self._max_history_size:
                self._event_history = self._event_history[-self._max_history_size:]
        
        # Callback larni chaqirish
        self._notify_subscribers(event)
        
        self.logger.debug(f"Published event: {event_type}")
    
    def _notify_subscribers(self, event: Event):
        """Subscriber larni notification qilish"""
        with self._lock:
            callbacks = self._subscriptions.get(event.event_type, [])
        
        # Sync notification
        for callback in callbacks:
            try:
                callback(event.data)
            except Exception as e:
                self.logger.error(f"Event callback error: {str(e)}")
    
    async def publish_async(self, event_type: str, data: Dict[str, Any], source: str = "system"):
        """Async event publishing"""
        event = Event(
            event_type=event_type,
            data=data,
            timestamp=datetime.now(),
            source=source
        )
        
        # Event history ga qo'shish
        with self._lock:
            self._event_history.append(event)
            
            # History size limit
            if len(self._event_history) > self._max_history_size:
                self._event_history = self._event_history[-self._max_history_size:]
        
        # Async notification
        await self._notify_subscribers_async(event)
        
        self.logger.debug(f"Published async event: {event_type}")
    
    async def _notify_subscribers_async(self, event: Event):
        """Async subscriber notification"""
        with self._lock:
            callbacks = self._subscriptions.get(event.event_type, [])
        
        # Async callback execution
        tasks = []
        for callback in callbacks:
            if asyncio.iscoroutinefunction(callback):
                task = asyncio.create_task(self._safe_async_callback(callback, event.data))
                tasks.append(task)
            else:
                # Sync callback ni thread pool da ishlatish
                loop = asyncio.get_event_loop()
                task = loop.run_in_executor(None, self._safe_callback, callback, event.data)
                tasks.append(task)
        
        # Barcha task larni kutish
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _safe_async_callback(self, callback: Callable, data: Dict):
        """Safe async callback execution"""
        try:
            await callback(data)
        except Exception as e:
            self.logger.error(f"Async event callback error: {str(e)}")
    
    def _safe_callback(self, callback: Callable, data: Dict):
        """Safe sync callback execution"""
        try:
            callback(data)
        except Exception as e:
            self.logger.error(f"Sync event callback error: {str(e)}")
    
    def get_event_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Event history olish"""
        with self._lock:
            events = self._event_history
            
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            
            # Latest events
            events = events[-limit:]
            
            return [asdict(event) for event in events]
    
    def clear_history(self):
        """Event history ni tozalash"""
        with self._lock:
            self._event_history.clear()
            self.logger.info("Event history cleared")
    
    def get_subscription_count(self, event_type: str) -> int:
        """Event type uchun subscriber count"""
        with self._lock:
            return len(self._subscriptions.get(event_type, []))
    
    def get_all_subscriptions(self) -> Dict[str, int]:
        """Barcha subscription count larni olish"""
        with self._lock:
            return {event_type: len(callbacks) 
                   for event_type, callbacks in self._subscriptions.items()}
    
    # Convenience methods for common events
    def emit_performance_update(self, data: Dict[str, Any]):
        """Performance update event"""
        self.publish("performance_update", data, "performance_monitor")
    
    def emit_trade_executed(self, data: Dict[str, Any]):
        """Trade executed event"""
        self.publish("trade_executed", data, "trading_agent")
    
    def emit_governance_vote(self, data: Dict[str, Any]):
        """Governance vote event"""
        self.publish("governance_vote", data, "dao_governance")
    
    def emit_risk_alert(self, data: Dict[str, Any]):
        """Risk alert event"""
        self.publish("risk_alert", data, "risk_manager")
    
    def emit_strategy_change(self, data: Dict[str, Any]):
        """Strategy change event"""
        self.publish("strategy_change", data, "trading_agent")
    
    def emit_system_error(self, error: Exception, context: Dict = None):
        """System error event"""
        data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        self.publish("system_error", data, "event_system")