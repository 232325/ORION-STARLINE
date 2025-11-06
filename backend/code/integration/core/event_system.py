"""
Event System
============

Event-driven architecture uchun Event System.
Asynchronous event handling, pub/sub pattern va event routing ta'minlaydi.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import json
from concurrent.futures import ThreadPoolExecutor
import uuid

class EventPriority(Enum):
    """Event priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class EventStatus(Enum):
    """Event status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Event:
    """Event ma'lumot"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    source: str = ""
    target: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    ttl: float = 3600  # 1 soat
    status: EventStatus = EventStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    error: Optional[str] = None
    
    def is_expired(self) -> bool:
        """Event expiration check"""
        return time.time() - self.timestamp > self.ttl
    
    def to_dict(self) -> Dict[str, Any]:
        """Event-ni dict ga convert qilish"""
        return {
            'id': self.id,
            'type': self.type,
            'source': self.source,
            'target': self.target,
            'payload': self.payload,
            'priority': self.priority.value,
            'timestamp': self.timestamp,
            'ttl': self.ttl,
            'status': self.status.value,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'error': self.error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Dict dan Event yaratish"""
        event = cls()
        event.id = data.get('id', str(uuid.uuid4()))
        event.type = data.get('type', '')
        event.source = data.get('source', '')
        event.target = data.get('target', '')
        event.payload = data.get('payload', {})
        event.priority = EventPriority(data.get('priority', EventPriority.NORMAL.value))
        event.timestamp = data.get('timestamp', time.time())
        event.ttl = data.get('ttl', 3600)
        event.status = EventStatus(data.get('status', EventStatus.PENDING.value))
        event.retry_count = data.get('retry_count', 0)
        event.max_retries = data.get('max_retries', 3)
        event.error = data.get('error')
        return event

@dataclass
class EventSubscription:
    """Event subscription ma'lumot"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_pattern: str = ""
    callback: Callable = None
    filter_func: Optional[Callable] = None
    priority: int = 0
    active: bool = True
    subscriber_id: str = ""
    created_at: float = field(default_factory=time.time)
    
    def matches_event(self, event: Event) -> bool:
        """Event pattern ga mos kelishini tekshirish"""
        # Pattern matching (simple glob-like pattern)
        pattern_parts = self.event_pattern.split('.')
        event_parts = event.type.split('.')
        
        if len(pattern_parts) != len(event_parts):
            return False
        
        for pattern_part, event_part in zip(pattern_parts, event_parts):
            if pattern_part == '*':
                continue
            elif pattern_part.startswith('{') and pattern_part.endswith('}'):
                # Variable pattern
                continue
            elif pattern_part != event_part:
                return False
        
        return True
    
    def should_process_event(self, event: Event) -> bool:
        """Event-ni process qilish kerakligini tekshirish"""
        if not self.active:
            return False
        
        if not self.matches_event(event):
            return False
        
        if self.filter_func and not self.filter_func(event):
            return False
        
        return True

class EventSystem:
    """
    Event System
    
    Event-driven architecture uchun event handling, pub/sub pattern
    va asynchronous event processing ta'minlaydi.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.subscriptions: Dict[str, EventSubscription] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        self.pending_events: List[Event] = []
        self.processing_events: Set[str] = set()
        
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Configuration
        self.max_event_queue_size = self.config.get('max_event_queue_size', 10000)
        self.event_processing_timeout = self.config.get('event_processing_timeout', 30)
        self.batch_processing = self.config.get('batch_processing', True)
        self.batch_size = self.config.get('batch_size', 100)
        
        self.running = False
    
    async def initialize(self) -> bool:
        """Event System-ni ishga tushirish"""
        try:
            self.logger.info("Event System ishga tushirilmoqda...")
            
            # Event processing monitoring
            self.running = True
            self._start_event_processor()
            self._start_event_cleaner()
            
            self.logger.info("Event System muvaffaqiyatli ishga tushdi")
            return True
            
        except Exception as e:
            self.logger.error(f"Event System ishga tushishda xato: {e}")
            return False
    
    async def shutdown(self):
        """Event System-ni to'xtatish"""
        self.logger.info("Event System to'xtatilmoqda...")
        
        self.running = False
        
        # Event queue-ni tozalash
        self.pending_events.clear()
        self.processing_events.clear()
        
        # Subscriptions-ni tozalash
        self.subscriptions.clear()
        self.event_handlers.clear()
        
        self.executor.shutdown(wait=True)
        self.logger.info("Event System to'xtatildi")
    
    async def emit_event(self, event_type: str, payload: Dict[str, Any] = None,
                        source: str = "", target: str = "", 
                        priority: EventPriority = EventPriority.NORMAL,
                        ttl: float = 3600) -> str:
        """Event yuborish"""
        try:
            event = Event(
                type=event_type,
                source=source,
                target=target,
                payload=payload or {},
                priority=priority,
                ttl=ttl
            )
            
            # Event queue ga qo'shish
            if len(self.pending_events) >= self.max_event_queue_size:
                # Queue to'lganda eskirgan eventlarni o'chirish
                await self._cleanup_expired_events()
                
                if len(self.pending_events) >= self.max_event_queue_size:
                    # Hal ham to'liq bo'lsa, eng past priority eventlarni o'chirish
                    self.pending_events.sort(key=lambda e: e.priority.value)
                    self.pending_events = self.pending_events[-self.max_event_queue_size//2:]
            
            self.pending_events.append(event)
            
            # Event ni immediate processing uchun signal berish
            self._signal_event_available()
            
            self.logger.debug(f"Event yuborildi: {event_type} (ID: {event.id})")
            return event.id
            
        except Exception as e:
            self.logger.error(f"Event yuborishda xato: {e}")
            return ""
    
    async def subscribe_to_events(self, event_pattern: str, callback: Callable,
                                subscriber_id: str = "", filter_func: Callable = None,
                                priority: int = 0) -> str:
        """Event-subscribe qilish"""
        try:
            subscription = EventSubscription(
                event_pattern=event_pattern,
                callback=callback,
                filter_func=filter_func,
                priority=priority,
                subscriber_id=subscriber_id
            )
            
            self.subscriptions[subscription.id] = subscription
            
            # Event handlers ro'yxatiga qo'shish
            if event_pattern not in self.event_handlers:
                self.event_handlers[event_pattern] = []
            self.event_handlers[event_pattern].append(callback)
            
            self.logger.info(f"Event subscription yaratildi: {event_pattern} (ID: {subscription.id})")
            return subscription.id
            
        except Exception as e:
            self.logger.error(f"Event subscription da xato: {e}")
            return ""
    
    async def unsubscribe_from_events(self, event_pattern: str, callback: Callable):
        """Event-dan unsubscribe qilish"""
        try:
            # Subscription-larni o'chirish
            subscriptions_to_remove = [
                sub_id for sub_id, sub in self.subscriptions.items()
                if sub.event_pattern == event_pattern and sub.callback == callback
            ]
            
            for sub_id in subscriptions_to_remove:
                del self.subscriptions[sub_id]
            
            # Event handlers dan o'chirish
            if event_pattern in self.event_handlers:
                if callback in self.event_handlers[event_pattern]:
                    self.event_handlers[event_pattern].remove(callback)
                
                if not self.event_handlers[event_pattern]:
                    del self.event_handlers[event_pattern]
            
            self.logger.info(f"Event subscription o'chirildi: {event_pattern}")
            
        except Exception as e:
            self.logger.error(f"Event unsubscribe da xato: {e}")
    
    def get_subscription(self, subscription_id: str) -> Optional[EventSubscription]:
        """Subscription ma'lumotini olish"""
        return self.subscriptions.get(subscription_id)
    
    def list_subscriptions(self, event_pattern: str = None) -> List[Dict[str, Any]]:
        """Subscriptions ro'yxati"""
        subscriptions = list(self.subscriptions.values())
        
        if event_pattern:
            subscriptions = [
                sub for sub in subscriptions 
                if sub.event_pattern == event_pattern
            ]
        
        return [
            {
                'id': sub.id,
                'event_pattern': sub.event_pattern,
                'subscriber_id': sub.subscriber_id,
                'priority': sub.priority,
                'active': sub.active,
                'created_at': sub.created_at
            }
            for sub in subscriptions
        ]
    
    async def broadcast_event(self, event_type: str, payload: Dict[str, Any] = None,
                            source: str = "", exclude_subscribers: List[str] = None,
                            priority: EventPriority = EventPriority.NORMAL) -> List[str]:
        """Broadcast event"""
        try:
            # Event payloadiga broadcast ma'lumotlari qo'shish
            broadcast_payload = payload or {}
            broadcast_payload['_broadcast'] = True
            broadcast_payload['_exclude'] = exclude_subscribers or []
            
            # Event ni yuborish
            event_id = await self.emit_event(
                event_type=event_type,
                payload=broadcast_payload,
                source=source,
                priority=priority
            )
            
            return [event_id] if event_id else []
            
        except Exception as e:
            self.logger.error(f"Broadcast event da xato: {e}")
            return []
    
    async def replay_events(self, event_pattern: str, 
                          since_timestamp: float = None,
                          limit: int = 100) -> List[Event]:
        """Event-larni replay qilish"""
        try:
            replay_events = []
            
            # Pending events dan mos eventlarni topish
            for event in self.pending_events:
                if (event.matches_pattern(event_pattern) and
                    (since_timestamp is None or event.timestamp >= since_timestamp)):
                    replay_events.append(event)
                    
                    if len(replay_events) >= limit:
                        break
            
            # Replay events ni yuborish
            for event in replay_events:
                await self.emit_event(
                    event_type=f"replay.{event.type}",
                    payload={'original_event': event.to_dict()},
                    source="event_replay",
                    priority=EventPriority.LOW
                )
            
            self.logger.info(f"{len(replay_events)} events replay qilindi")
            return replay_events
            
        except Exception as e:
            self.logger.error(f"Event replay da xato: {e}")
            return []
    
    def get_event_stats(self) -> Dict[str, Any]:
        """Event statistics"""
        total_subscriptions = len(self.subscriptions)
        active_subscriptions = len([s for s in self.subscriptions.values() if s.active])
        
        # Event patterns distribution
        pattern_counts = {}
        for subscription in self.subscriptions.values():
            pattern = subscription.event_pattern
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # Event queue stats
        queue_size = len(self.pending_events)
        processing_count = len(self.processing_events)
        
        return {
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'inactive_subscriptions': total_subscriptions - active_subscriptions,
            'event_patterns': pattern_counts,
            'pending_events': queue_size,
            'processing_events': processing_count,
            'queue_utilization': queue_size / self.max_event_queue_size
        }
    
    def _signal_event_available(self):
        """Event mavjudligini signal qilish"""
        # Bu yerda asyncio event yoki queue signal ishlatish mumkin
        pass
    
    def _start_event_processor(self):
        """Event processor ni boshlash"""
        def process_events():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            while self.running:
                try:
                    loop.run_until_complete(self._process_pending_events())
                    time.sleep(0.1)  # 100ms interval
                except Exception as e:
                    self.logger.error(f"Event processor da xato: {e}")
                    time.sleep(1)  # Xato bo'lsa 1 soniya kutish
            
            loop.close()
        
        self.executor.submit(process_events)
    
    def _start_event_cleaner(self):
        """Event cleaner ni boshlash"""
        def clean_events():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            while self.running:
                try:
                    loop.run_until_complete(self._cleanup_expired_events())
                    time.sleep(60)  # 1 daqiqa interval
                except Exception as e:
                    self.logger.error(f"Event cleaner da xato: {e}")
                    time.sleep(60)
            
            loop.close()
        
        self.executor.submit(clean_events)
    
    async def _process_pending_events(self):
        """Pending event-larni process qilish"""
        if not self.pending_events:
            return
        
        # Priority bo'yicha sort
        self.pending_events.sort(key=lambda e: e.priority.value, reverse=True)
        
        # Batch processing yoki individual processing
        if self.batch_processing and len(self.pending_events) > self.batch_size:
            events_to_process = self.pending_events[:self.batch_size]
        else:
            events_to_process = [self.pending_events.pop(0)]
        
        for event in events_to_process:
            if event.id in self.processing_events:
                continue
            
            if event.is_expired():
                # Expired event-ni o'chirish
                if event in self.pending_events:
                    self.pending_events.remove(event)
                continue
            
            self.processing_events.add(event.id)
            event.status = EventStatus.PROCESSING
            
            try:
                await self._deliver_event(event)
                event.status = EventStatus.COMPLETED
            except Exception as e:
                event.status = EventStatus.FAILED
                event.error = str(e)
                event.retry_count += 1
                
                if event.retry_count < event.max_retries:
                    # Retry uchun event-ni qayta queue ga qo'shish
                    self.pending_events.append(event)
                else:
                    self.logger.error(f"Event processing failed after {event.max_retries} retries: {event.id}")
            finally:
                self.processing_events.discard(event.id)
                # Completed/failed event-ni queue dan o'chirish
                if event in self.pending_events:
                    self.pending_events.remove(event)
    
    async def _deliver_event(self, event: Event):
        """Event-ni delivery qilish"""
        # Mos subscriptions ni topish
        matching_subscriptions = [
            sub for sub in self.subscriptions.values()
            if sub.should_process_event(event)
        ]
        
        # Priority bo'yicha sort
        matching_subscriptions.sort(key=lambda s: s.priority, reverse=True)
        
        # Event-ni barcha matching subscribers ga yuborish
        for subscription in matching_subscriptions:
            try:
                if asyncio.iscoroutinefunction(subscription.callback):
                    await subscription.callback(event.type, event.to_dict())
                else:
                    # Sync callback uchun executor ishlatish
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        self.executor, 
                        subscription.callback, 
                        event.type, 
                        event.to_dict()
                    )
            except Exception as e:
                self.logger.error(f"Event delivery error: {e}")
                raise
    
    async def _cleanup_expired_events(self):
        """Expired event-larni tozalash"""
        current_time = time.time()
        expired_events = [
            event for event in self.pending_events
            if event.is_expired()
        ]
        
        for event in expired_events:
            self.pending_events.remove(event)
            self.logger.debug(f"Expired event removed: {event.id}")
        
        if expired_events:
            self.logger.info(f"Cleaned up {len(expired_events)} expired events")

# Event pattern matching utility
def match_event_pattern(event_type: str, pattern: str) -> bool:
    """Event pattern matching"""
    pattern_parts = pattern.split('.')
    event_parts = event_type.split('.')
    
    if len(pattern_parts) != len(event_parts):
        return False
    
    for pattern_part, event_part in zip(pattern_parts, event_parts):
        if pattern_part == '*':
            continue
        elif pattern_part.startswith('{') and pattern_part.endswith('}'):
            # Variable pattern
            continue
        elif pattern_part != event_part:
            return False
    
    return True