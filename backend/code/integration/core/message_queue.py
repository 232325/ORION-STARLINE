"""
Message Queue
=============

Modullar o'rtasida reliable message passing uchun Message Queue.
Async messaging, persistence, load balancing va dead letter queue ta'minlaydi.
"""

import asyncio
import logging
import time
import json
import pickle
import sqlite3
import threading
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import uuid
from pathlib import Path

class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class MessageStatus(Enum):
    """Message status"""
    PENDING = "pending"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"

class QueueType(Enum):
    """Queue type"""
    FIFO = "fifo"
    LIFO = "lifo"
    PRIORITY = "priority"

@dataclass
class Message:
    """Message ma'lumot"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    queue_name: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    ttl: float = 3600 * 24  # 24 soat
    max_retries: int = 3
    retry_count: int = 0
    status: MessageStatus = MessageStatus.PENDING
    source: str = ""
    target: str = ""
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    headers: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Message expiration check"""
        return time.time() - self.timestamp > self.ttl
    
    def to_dict(self) -> Dict[str, Any]:
        """Message-ni dict ga convert qilish"""
        return {
            'id': self.id,
            'queue_name': self.queue_name,
            'payload': self.payload,
            'priority': self.priority.value,
            'timestamp': self.timestamp,
            'ttl': self.ttl,
            'max_retries': self.max_retries,
            'retry_count': self.retry_count,
            'status': self.status.value,
            'source': self.source,
            'target': self.target,
            'correlation_id': self.correlation_id,
            'reply_to': self.reply_to,
            'headers': self.headers
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Dict dan Message yaratish"""
        message = cls()
        message.id = data.get('id', str(uuid.uuid4()))
        message.queue_name = data.get('queue_name', '')
        message.payload = data.get('payload', {})
        message.priority = MessagePriority(data.get('priority', MessagePriority.NORMAL.value))
        message.timestamp = data.get('timestamp', time.time())
        message.ttl = data.get('ttl', 3600 * 24)
        message.max_retries = data.get('max_retries', 3)
        message.retry_count = data.get('retry_count', 0)
        message.status = MessageStatus(data.get('status', MessageStatus.PENDING.value))
        message.source = data.get('source', '')
        message.target = data.get('target', '')
        message.correlation_id = data.get('correlation_id')
        message.reply_to = data.get('reply_to')
        message.headers = data.get('headers', {})
        return message

@dataclass
class QueueConfig:
    """Queue configuration"""
    name: str
    queue_type: QueueType = QueueType.FIFO
    max_size: int = 10000
    persistence: bool = True
    dead_letter_queue: Optional[str] = None
    ttl: float = 3600 * 24
    visibility_timeout: float = 300
    consumer_count: int = 1

class MessageQueue:
    """
    Message Queue
    
    Reliable message passing, persistence, load balancing
    va dead letter queue functionality ta'minlaydi.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.queues: Dict[str, List[Message]] = {}
        self.consumer_handlers: Dict[str, List[Callable]] = {}
        self.queue_configs: Dict[str, QueueConfig] = {}
        
        # Dead letter queues
        self.dead_letter_queues: Dict[str, List[Message]] = {}
        
        # In-memory message store for faster access
        self.message_index: Dict[str, Message] = {}
        
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Database for persistence
        self.db_path = self.config.get('db_path', '/workspace/code/integration/message_queue.db')
        self.db_connection = None
        
        # Configuration
        self.batch_size = self.config.get('batch_size', 50)
        self.processing_timeout = self.config.get('processing_timeout', 30)
        
        self.running = False
        self._lock = threading.RLock()
    
    async def initialize(self) -> bool:
        """Message Queue-ni ishga tushirish"""
        try:
            self.logger.info("Message Queue ishga tushirilmoqda...")
            
            # Database connection
            if self.config.get('persistence', True):
                await self._setup_persistence()
            
            # Default queues yaratish
            await self._create_default_queues()
            
            # Message processor
            self.running = True
            self._start_message_processor()
            self._start_cleanup_worker()
            
            self.logger.info("Message Queue muvaffaqiyatli ishga tushdi")
            return True
            
        except Exception as e:
            self.logger.error(f"Message Queue ishga tushishda xato: {e}")
            return False
    
    async def shutdown(self):
        """Message Queue-ni to'xtatish"""
        self.logger.info("Message Queue to'xtatilmoqda...")
        
        self.running = False
        
        # Barcha queued message-larni saqlash
        await self._persist_all_messages()
        
        # Resources cleanup
        if self.db_connection:
            self.db_connection.close()
        
        self.queues.clear()
        self.consumer_handlers.clear()
        self.queue_configs.clear()
        self.dead_letter_queues.clear()
        self.message_index.clear()
        
        self.executor.shutdown(wait=True)
        self.logger.info("Message Queue to'xtatildi")
    
    async def create_queue(self, queue_config: QueueConfig) -> bool:
        """Queue yaratish"""
        try:
            with self._lock:
                if queue_config.name in self.queues:
                    self.logger.warning(f"Queue allaqachon mavjud: {queue_config.name}")
                    return True
                
                self.queues[queue_config.name] = []
                self.consumer_handlers[queue_config.name] = []
                self.queue_configs[queue_config.name] = queue_config
                
                # Dead letter queue yaratish
                if queue_config.dead_letter_queue:
                    if queue_config.dead_letter_queue not in self.dead_letter_queues:
                        self.dead_letter_queues[queue_config.dead_letter_queue] = []
                
                # Database ga queue info saqlash
                if self.db_connection:
                    await self._persist_queue_config(queue_config)
                
                self.logger.info(f"Queue yaratildi: {queue_config.name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Queue yaratishda xato: {e}")
            return False
    
    async def delete_queue(self, queue_name: str) -> bool:
        """Queue-ni o'chirish"""
        try:
            with self._lock:
                if queue_name not in self.queues:
                    self.logger.warning(f"Queue topilmadi: {queue_name}")
                    return False
                
                # Queue-ni tozalash
                messages_to_move = self.queues[queue_name]
                
                # Dead letter queue ga o'tkazish
                queue_config = self.queue_configs.get(queue_name)
                if queue_config and queue_config.dead_letter_queue:
                    dlq_name = queue_config.dead_letter_queue
                    if dlq_name not in self.dead_letter_queues:
                        self.dead_letter_queues[dlq_name] = []
                    self.dead_letter_queues[dlq_name].extend(messages_to_move)
                
                # Queue-ni o'chirish
                del self.queues[queue_name]
                del self.consumer_handlers[queue_name]
                del self.queue_configs[queue_name]
                
                # Message index dan o'chirish
                for message in messages_to_move:
                    self.message_index.pop(message.id, None)
                
                # Database dan o'chirish
                if self.db_connection:
                    await self._delete_queue_from_db(queue_name)
                
                self.logger.info(f"Queue o'chirildi: {queue_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Queue o'chirishda xato: {e}")
            return False
    
    async def put(self, message: Union[Message, Dict[str, Any]], 
                 queue_name: str = None) -> bool:
        """Queue ga message qo'yish"""
        try:
            if isinstance(message, dict):
                message = Message.from_dict(message)
            
            if not queue_name:
                queue_name = message.queue_name
            
            if not queue_name:
                self.logger.error("Queue name berilmagan")
                return False
            
            # Queue mavjudligini tekshirish
            if queue_name not in self.queues:
                # Default configuration bilan queue yaratish
                default_config = QueueConfig(name=queue_name)
                await self.create_queue(default_config)
            
            # Message-ni validate qilish
            if not self._validate_message(message, queue_name):
                return False
            
            with self._lock:
                queue_config = self.queue_configs[queue_name]
                
                # Queue size limit check
                if len(self.queues[queue_name]) >= queue_config.max_size:
                    self.logger.warning(f"Queue to'liq: {queue_name}")
                    return False
                
                # TTL check
                if message.is_expired():
                    self.logger.warning(f"Expired message discarded: {message.id}")
                    return False
                
                # Queue ga message qo'shish
                self.queues[queue_name].append(message)
                
                # Message index ga qo'shish
                self.message_index[message.id] = message
                
                # Priority based insertion
                if queue_config.queue_type == QueueType.PRIORITY:
                    self.queues[queue_name].sort(
                        key=lambda m: m.priority.value, 
                        reverse=True
                    )
                
                # Persistence
                if queue_config.persistence and self.db_connection:
                    await self._persist_message(message, queue_name)
                
                self.logger.debug(f"Message queued: {message.id} in {queue_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Message put qilishda xato: {e}")
            return False
    
    async def get(self, queue_name: str, timeout: float = 5.0) -> Optional[Message]:
        """Queue dan message olish"""
        try:
            if queue_name not in self.queues:
                return None
            
            with self._lock:
                messages = self.queues[queue_name]
                
                if not messages:
                    return None
                
                # Queue type ga qarab message olish
                queue_config = self.queue_configs.get(queue_name)
                if queue_config.queue_type == QueueType.LIFO:
                    message = messages.pop()
                else:  # FIFO yoki PRIORITY
                    message = messages.pop(0)
                
                # Message status ni update qilish
                message.status = MessageStatus.DELIVERING
                
                # Message index dan o'chirish
                self.message_index.pop(message.id, None)
                
                # Database dan o'chirish
                if queue_config.persistence and self.db_connection:
                    await self._remove_message_from_db(message.id, queue_name)
                
                self.logger.debug(f"Message dequeued: {message.id} from {queue_name}")
                return message
                
        except Exception as e:
            self.logger.error(f"Message get qilishda xato: {e}")
            return None
    
    async def get_batch(self, queue_name: str, count: int = None, 
                       timeout: float = 5.0) -> List[Message]:
        """Batch message olish"""
        try:
            if not count:
                count = min(self.batch_size, len(self.queues.get(queue_name, [])))
            
            batch = []
            for _ in range(count):
                message = await self.get(queue_name, timeout=0.1)
                if not message:
                    break
                batch.append(message)
            
            return batch
            
        except Exception as e:
            self.logger.error(f"Batch message get qilishda xato: {e}")
            return []
    
    async def subscribe(self, callback: Callable, queue_name: str):
        """Queue subscriber"""
        try:
            if queue_name not in self.consumer_handlers:
                self.consumer_handlers[queue_name] = []
            
            self.consumer_handlers[queue_name].append(callback)
            
            self.logger.info(f"Consumer subscribed to queue: {queue_name}")
            
        except Exception as e:
            self.logger.error(f"Queue subscription da xato: {e}")
    
    async def acknowledge(self, message_id: str, queue_name: str, 
                        success: bool = True) -> bool:
        """Message acknowledgement"""
        try:
            message = self.message_index.get(message_id)
            if not message:
                self.logger.warning(f"Message not found for ack: {message_id}")
                return False
            
            if success:
                message.status = MessageStatus.DELIVERED
                self.logger.debug(f"Message acknowledged: {message_id}")
            else:
                message.status = MessageStatus.FAILED
                message.retry_count += 1
                
                if message.retry_count < message.max_retries:
                    # Retry uchun queue ga qayta qo'yish
                    message.status = MessageStatus.PENDING
                    await self.put(message, queue_name)
                else:
                    # Dead letter queue ga o'tkazish
                    await self._send_to_dead_letter_queue(message, queue_name)
                
                self.logger.warning(f"Message failed, retry {message.retry_count}/{message.max_retries}: {message_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Message acknowledgement da xato: {e}")
            return False
    
    async def purge_queue(self, queue_name: str) -> int:
        """Queue-ni tozalash"""
        try:
            if queue_name not in self.queues:
                return 0
            
            with self._lock:
                message_count = len(self.queues[queue_name])
                
                # Message index dan o'chirish
                for message in self.queues[queue_name]:
                    self.message_index.pop(message.id, None)
                
                # Queue-ni tozalash
                self.queues[queue_name].clear()
                
                # Database dan o'chirish
                if self.db_connection:
                    await self._purge_queue_from_db(queue_name)
                
                self.logger.info(f"Queue purged: {queue_name}, {message_count} messages removed")
                return message_count
                
        except Exception as e:
            self.logger.error(f"Queue purge da xato: {e}")
            return 0
    
    def get_queue_stats(self, queue_name: str) -> Dict[str, Any]:
        """Queue statistics"""
        try:
            if queue_name not in self.queues:
                return {}
            
            queue_messages = self.queues[queue_name]
            config = self.queue_configs.get(queue_name)
            
            # Status distribution
            status_counts = {}
            for message in queue_messages:
                status = message.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Priority distribution
            priority_counts = {}
            for message in queue_messages:
                priority = message.priority.name
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            return {
                'name': queue_name,
                'message_count': len(queue_messages),
                'max_size': config.max_size if config else 0,
                'utilization': len(queue_messages) / (config.max_size if config else 1),
                'queue_type': config.queue_type.value if config else 'unknown',
                'status_distribution': status_counts,
                'priority_distribution': priority_counts,
                'dead_letter_queue': config.dead_letter_queue if config else None
            }
            
        except Exception as e:
            self.logger.error(f"Queue stats olishda xato: {e}")
            return {}
    
    def list_queues(self) -> List[str]:
        """Queue-lar ro'yxati"""
        return list(self.queues.keys())
    
    def get_message(self, message_id: str) -> Optional[Message]:
        """Message-ni ID bo'yicha olish"""
        return self.message_index.get(message_id)
    
    def _validate_message(self, message: Message, queue_name: str) -> bool:
        """Message validation"""
        try:
            if not message.queue_name:
                message.queue_name = queue_name
            
            if not message.payload:
                self.logger.error("Empty message payload")
                return False
            
            # TTL validation
            if message.ttl <= 0:
                self.logger.error("Invalid TTL")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Message validation da xato: {e}")
            return False
    
    async def _send_to_dead_letter_queue(self, message: Message, original_queue: str):
        """Message-ni dead letter queue ga yuborish"""
        try:
            queue_config = self.queue_configs.get(original_queue)
            if not queue_config or not queue_config.dead_letter_queue:
                return
            
            dlq_name = queue_config.dead_letter_queue
            
            # DLQ yaratish (agar mavjud bo'lmasa)
            if dlq_name not in self.dead_letter_queues:
                self.dead_letter_queues[dlq_name] = []
            
            # DLQ ga message qo'shish
            message.status = MessageStatus.FAILED
            self.dead_letter_queues[dlq_name].append(message)
            
            self.logger.warning(f"Message sent to DLQ: {message.id} -> {dlq_name}")
            
        except Exception as e:
            self.logger.error(f"DLQ send da xato: {e}")
    
    def _start_message_processor(self):
        """Message processor ni boshlash"""
        def process_messages():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            while self.running:
                try:
                    # Har bir queue uchun consumer-lar invoke qilish
                    for queue_name, handlers in self.consumer_handlers.items():
                        if handlers and queue_name in self.queues:
                            loop.run_until_complete(
                                self._process_queue_messages(queue_name, handlers)
                            )
                    
                    time.sleep(0.1)  # 100ms interval
                    
                except Exception as e:
                    self.logger.error(f"Message processor da xato: {e}")
                    time.sleep(1)
            
            loop.close()
        
        self.executor.submit(process_messages)
    
    async def _process_queue_messages(self, queue_name: str, handlers: List[Callable]):
        """Queue message-larni process qilish"""
        try:
            messages = await self.get_batch(queue_name, timeout=0.1)
            
            if not messages:
                return
            
            for message in messages:
                try:
                    # Handlers invoke qilish
                    for handler in handlers:
                        if asyncio.iscoroutinefunction(handler):
                            result = await handler(message)
                        else:
                            loop = asyncio.get_event_loop()
                            result = await loop.run_in_executor(
                                self.executor, handler, message
                            )
                    
                    # Successful processing acknowledgment
                    await self.acknowledge(message.id, queue_name, True)
                    
                except Exception as e:
                    self.logger.error(f"Message processing da xato {message.id}: {e}")
                    # Failed processing acknowledgment
                    await self.acknowledge(message.id, queue_name, False)
                    
        except Exception as e:
            self.logger.error(f"Queue processing da xato {queue_name}: {e}")
    
    def _start_cleanup_worker(self):
        """Cleanup worker ni boshlash"""
        def cleanup():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            while self.running:
                try:
                    loop.run_until_complete(self._cleanup_expired_messages())
                    time.sleep(300)  # 5 daqiqa interval
                except Exception as e:
                    self.logger.error(f"Cleanup worker da xato: {e}")
                    time.sleep(300)
            
            loop.close()
        
        self.executor.submit(cleanup)
    
    async def _cleanup_expired_messages(self):
        """Expired message-larni tozalash"""
        try:
            current_time = time.time()
            expired_count = 0
            
            for queue_name, messages in list(self.queues.items()):
                expired_messages = [
                    msg for msg in messages 
                    if msg.is_expired()
                ]
                
                for message in expired_messages:
                    messages.remove(message)
                    self.message_index.pop(message.id, None)
                    expired_count += 1
            
            if expired_count > 0:
                self.logger.info(f"Cleaned up {expired_count} expired messages")
                
        except Exception as e:
            self.logger.error(f"Message cleanup da xato: {e}")
    
    async def _setup_persistence(self):
        """Database persistence setup"""
        try:
            # Create database directory
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self.db_connection = sqlite3.connect(self.db_path, check_same_thread=False)
            
            # Create tables
            await self._create_db_tables()
            
            self.logger.info("Database persistence setup completed")
            
        except Exception as e:
            self.logger.error(f"Database setup da xato: {e}")
            self.db_connection = None
    
    async def _create_db_tables(self):
        """Database tables yaratish"""
        try:
            cursor = self.db_connection.cursor()
            
            # Messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    queue_name TEXT,
                    payload TEXT,
                    priority INTEGER,
                    timestamp REAL,
                    ttl REAL,
                    max_retries INTEGER,
                    retry_count INTEGER,
                    status TEXT,
                    source TEXT,
                    target TEXT,
                    correlation_id TEXT,
                    reply_to TEXT,
                    headers TEXT
                )
            ''')
            
            # Queues table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS queues (
                    name TEXT PRIMARY KEY,
                    queue_type TEXT,
                    max_size INTEGER,
                    persistence BOOLEAN,
                    dead_letter_queue TEXT,
                    ttl REAL,
                    visibility_timeout REAL,
                    consumer_count INTEGER
                )
            ''')
            
            self.db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"DB table creation da xato: {e}")
            raise
    
    async def _persist_message(self, message: Message, queue_name: str):
        """Message-ni database ga saqlash"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO messages 
                (id, queue_name, payload, priority, timestamp, ttl, max_retries, 
                 retry_count, status, source, target, correlation_id, reply_to, headers)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                message.id, queue_name, json.dumps(message.payload),
                message.priority.value, message.timestamp, message.ttl,
                message.max_retries, message.retry_count, message.status.value,
                message.source, message.target, message.correlation_id,
                message.reply_to, json.dumps(message.headers)
            ))
            self.db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Message persistence da xato: {e}")
    
    async def _persist_queue_config(self, config: QueueConfig):
        """Queue config-ni database ga saqlash"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO queues 
                (name, queue_type, max_size, persistence, dead_letter_queue, 
                 ttl, visibility_timeout, consumer_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                config.name, config.queue_type.value, config.max_size,
                config.persistence, config.dead_letter_queue,
                config.ttl, config.visibility_timeout, config.consumer_count
            ))
            self.db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Queue config persistence da xato: {e}")
    
    async def _persist_all_messages(self):
        """Barcha message-larni database ga saqlash"""
        try:
            for queue_name, messages in self.queues.items():
                for message in messages:
                    await self._persist_message(message, queue_name)
            
            self.logger.info("All messages persisted")
            
        except Exception as e:
            self.logger.error(f"Messages persistence da xato: {e}")
    
    async def _remove_message_from_db(self, message_id: str, queue_name: str):
        """Message-ni database dan o'chirish"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('DELETE FROM messages WHERE id = ? AND queue_name = ?', 
                         (message_id, queue_name))
            self.db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Message DB removal da xato: {e}")
    
    async def _delete_queue_from_db(self, queue_name: str):
        """Queue-ni database dan o'chirish"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('DELETE FROM queues WHERE name = ?', (queue_name,))
            cursor.execute('DELETE FROM messages WHERE queue_name = ?', (queue_name,))
            self.db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Queue DB deletion da xato: {e}")
    
    async def _purge_queue_from_db(self, queue_name: str):
        """Queue-ni database dan tozalash"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('DELETE FROM messages WHERE queue_name = ?', (queue_name,))
            self.db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Queue DB purge da xato: {e}")
    
    async def _create_default_queues(self):
        """Default queues yaratish"""
        default_queues = [
            QueueConfig(name="default"),
            QueueConfig(name="events", queue_type=QueueType.PRIORITY),
            QueueConfig(name="notifications", priority=MessagePriority.HIGH),
            QueueConfig(name="errors", dead_letter_queue="dead_letter"),
            QueueConfig(name="dead_letter")
        ]
        
        for queue_config in default_queues:
            await self.create_queue(queue_config)