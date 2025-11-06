# Real-time Collaboration System

## Tavsif

Bu modul Orion Starline Trading Platform uchun real-time collaboration tizimini ta'minlaydi. Trading jamoalari, signal almashish, guruh muhokamalari va boshqa collaboration funksiyalarini qo'llab-quvvatlaydi.

## Asosiy Xususiyatlar

### 1. Chat Guruhlari
- **Public guruhlar**: Ochiq guruhlar, har qanday foydalanuvchi qo'shilishi mumkin
- **Private guruhlar**: Faqat taklif orqali kirish mumkin
- **Group chats**: Guruh suhbatlari
- **Direct chats**: Shaxsiy xabarlar

### 2. Community Features
- **Foydalanuvchi profillari**: Avatar, bio, status
- **Reputation system**: Ball tizimi va reyting
- **User preferences**: Til tanlash, bildirishnoma sozlamalari
- **Activity tracking**: Faollik kuzatuvi

### 3. Signal Almashish
- **Trading signals**: Sotib olish/sotish signallarini ulashish
- **Signal comments**: Signal bo'yicha izohlar
- **Voting system**: Signal foydali/yordamsiz deb ovoz berish
- **Performance tracking**: Signal natijalarini kuzatish

### 4. Guruh Trading Muhokamalari
- **Discussion threads**: Muhokama mavzulari
- **Voting mechanisms**: Qaror qabul qilish uchun ovoz berish
- **Topic management**: Mavzularni boshqarish
- **Poll features**: So'rovnoma o'tkazish

### 5. Real-time Messaging
- **WebSocket support**: Real-time xabar almashish
- **Typing indicators**: Yozayotgan ko'rsatkichlar
- **Message status**: Xabar statusi (yuborilgan, o'qilgan)
- **Message reactions**: Xabarlarga ta'sir ko'rsatish

### 6. File Sharing
- **Document sharing**: Hujjat ulashish
- **Image sharing**: Rasmlar ulashish
- **Chart sharing**: Grafik va chizmalar ulashish
- **File validation**: Fayl xavfsizligi tekshirish
- **Storage management**: Saqlash boshqaruvi

### 7. Voice Calls Integration
- **Group voice calls**: Guruh ovozli qo'ng'iroqlari
- **Voice chat functionality**: Ovozli chat
- **Call management**: Qo'ng'iroqni boshqarish
- **Audio quality controls**: Audio sifat nazorati

### 8. Notifications System
- **Real-time alerts**: Real-time bildirishnomalar
- **Customizable notifications**: Sozlangan bildirishnomalar
- **Mention notifications**: Eslatmalar bildirishnomalari
- **Signal alerts**: Signal bildirishnomalari

### 9. Moderation Tools
- **Content filtering**: Kontentni filtrlash
- **Spam prevention**: Spam oldini olish
- **User reporting**: Foydalanuvchi shikoyatlari
- **Admin controls**: Admin nazorati

## Qurilish

### Dependencies

```python
# Kerakli kutubxonalar
import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import hashlib
import mimetypes
import base64

# Supabase integration
from supabase import create_client, Client

# WebSocket support
import websockets
import aiofiles
from fastapi import WebSocket, HTTPException
```

### Asosiy Klasslar

#### 1. User
```python
@dataclass
class User:
    user_id: str
    username: str
    email: str
    avatar_url: Optional[str] = None
    status: str = "offline"
    last_seen: datetime
    reputation_score: int = 0
    language: Language = Language.ENGLISH
    timezone: str = "UTC"
    preferences: Dict[str, Any] = field(default_factory=dict)
```

#### 2. ChatRoom
```python
@dataclass
class ChatRoom:
    chat_id: str
    name: str
    description: Optional[str] = None
    chat_type: ChatType = ChatType.PUBLIC
    created_by: str
    created_at: datetime
    members: Set[str] = field(default_factory=set)
    moderators: Set[str] = field(default_factory=set)
    settings: Dict[str, Any] = field(default_factory=dict)
    topic: Optional[str] = None
```

#### 3. Message
```python
@dataclass
class Message:
    message_id: str
    chat_id: str
    user_id: str
    content: str
    message_type: MessageType = MessageType.TEXT
    timestamp: datetime
    edited: bool = False
    edited_at: Optional[datetime] = None
    reply_to: Optional[str] = None
    reactions: Dict[str, List[str]] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    is_deleted: bool = False
```

#### 4. TradingSignal
```python
@dataclass
class TradingSignal:
    signal_id: str
    user_id: str
    symbol: str
    signal_type: str  # BUY, SELL, HOLD
    entry_price: float
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    timeframe: str = "1D"
    analysis: str = ""
    confidence_score: float = 0.0
    created_at: datetime
    status: str = "active"
    comments: List[Dict[str, Any]] = field(default_factory=list)
```

## Foydalanish

### 1. Tizimni ishga tushirish

```python
from collaboration_system import CollaborationSystem, Language

# Tizimni yaratish
collab_system = CollaborationSystem(
    supabase_url="your_supabase_url",
    supabase_key="your_supabase_key"
)
```

### 2. Foydalanuvchi qo'shish

```python
from collaboration_system import User

# Foydalanuvchi yaratish
user = User(
    user_id="user123",
    username="trader_ali",
    email="ali@example.com",
    language=Language.UZBEK
)

await collab_system.create_user(user)
```

### 3. Chat guruh yaratish

```python
from collaboration_system import ChatType

# Chat guruhi yaratish
chat_id = await collab_system.create_chat_room(
    name="USD/EUR Trading Group",
    chat_type=ChatType.PUBLIC,
    created_by="user123",
    description="USD/EUR juftligi bo'yicha muhokama"
)

# Guruhga qo'shilish
await collab_system.join_chat_room(chat_id, "user123")
```

### 4. Xabar yuborish

```python
from collaboration_system import MessageType

# Oddiy xabar
await collab_system.send_message(
    chat_id, "user123", "Salom hammaga!", MessageType.TEXT
)

# Signal xabari
await collab_system.send_message(
    chat_id, "user123", "EUR/USD signalim bor!",
    MessageType.SIGNAL,
    attachments=[{
        "signal_id": "signal123",
        "symbol": "EURUSD",
        "action": "BUY"
    }]
)
```

### 5. Trading signal ulashish

```python
# Signal ulashish
signal_id = await collab_system.share_trading_signal(
    user_id="user123",
    symbol="EURUSD",
    signal_type="BUY",
    entry_price=1.0850,
    target_price=1.0900,
    stop_loss=1.0800,
    analysis="Kuchli bull trend"
)

# Signalga izoh qo'shish
await collab_system.comment_on_signal(
    signal_id, "user456", "Yaxshi tahlil!"
)

# Signalga ovoz berish
await collab_system.vote_on_signal(
    signal_id, "user456", "useful"
)
```

### 6. File sharing

```python
# Fayl yuklash
with open("chart.png", "rb") as f:
    file_data = f.read()

attachment = await collab_system.upload_file(
    file_data=file_data,
    filename="chart.png",
    user_id="user123",
    chat_id=chat_id,
    file_type="chart"
)
```

### 7. Voice call

```python
# Ovozli qo'ng'iroq boshlash
call_id = await collab_system.start_voice_call(
    chat_id=chat_id,
    initiator_id="user123",
    participant_ids=["user456", "user789"]
)

# Qo'ng'iroqni tugatish
await collab_system.end_voice_call(call_id)
```

### 8. WebSocket ulanishi

```python
from fastapi import WebSocket

# WebSocket handler
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await collab_system.connect_user(websocket, user_id)
```

## Supabase Integration

### Real-time Database

```sql
-- Users table
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    avatar_url TEXT,
    status VARCHAR(20) DEFAULT 'offline',
    reputation_score INTEGER DEFAULT 0,
    language VARCHAR(5) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Chat rooms table
CREATE TABLE chat_rooms (
    chat_id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    chat_type VARCHAR(20) DEFAULT 'public',
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW(),
    settings JSONB DEFAULT '{}',
    topic TEXT
);

-- Messages table
CREATE TABLE messages (
    message_id UUID PRIMARY KEY,
    chat_id UUID REFERENCES chat_rooms(chat_id),
    user_id UUID REFERENCES users(user_id),
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',
    timestamp TIMESTAMP DEFAULT NOW(),
    edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP,
    reply_to UUID REFERENCES messages(message_id),
    reactions JSONB DEFAULT '{}',
    attachments JSONB DEFAULT '[]',
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Trading signals table
CREATE TABLE trading_signals (
    signal_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    chat_id UUID REFERENCES chat_rooms(chat_id),
    symbol VARCHAR(10) NOT NULL,
    signal_type VARCHAR(10) NOT NULL,
    entry_price DECIMAL(10,5) NOT NULL,
    target_price DECIMAL(10,5),
    stop_loss DECIMAL(10,5),
    timeframe VARCHAR(10) DEFAULT '1D',
    analysis TEXT,
    confidence_score DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active',
    comments JSONB DEFAULT '[]',
    votes JSONB DEFAULT '{"useful": [], "not_useful": []}'
);
```

### Real-time Subscriptions

```javascript
// Subscribe to chat messages
supabase
  .channel('chat-messages')
  .on('postgres_changes', {
    event: 'INSERT',
    schema: 'public',
    table: 'messages',
    filter: `chat_id=eq.${chatId}`
  }, (payload) => {
    // Handle new message
    console.log('New message:', payload.new);
  })
  .subscribe();

// Subscribe to user status updates
supabase
  .channel('user-status')
  .on('postgres_changes', {
    event: 'UPDATE',
    schema: 'public',
    table: 'users',
    filter: `user_id=eq.${userId}`
  }, (payload) => {
    // Handle user status change
    console.log('User status changed:', payload.new);
  })
  .subscribe();
```

### Storage Setup

```sql
-- Create storage bucket for files
INSERT INTO storage.buckets (id, name, public)
VALUES ('chat-files', 'chat-files', true);

-- Set up RLS policies
CREATE POLICY "Users can upload files" ON storage.objects
FOR INSERT TO authenticated
WITH CHECK (bucket_id = 'chat-files');

CREATE POLICY "Users can view files" ON storage.objects
FOR SELECT TO authenticated
USING (bucket_id = 'chat-files');

CREATE POLICY "Users can delete their files" ON storage.objects
FOR DELETE TO authenticated
USING (bucket_id = 'chat-files');
```

## Multi-language Support

### Til qo'shish

```python
# Yangi til qo'shish
collab_system.translations[Language.SPANISH] = {
    "welcome": "¡Bienvenido!",
    "new_message": "Nuevo mensaje",
    "signal_shared": "Señal compartida",
    "user_joined": "Usuario se unió",
    "moderation_required": "El contenido requiere moderación"
}
```

### Foydalanuvchi tilini o'zgartirish

```python
# Foydalanuvchi tilini o'zgartirish
user = await collab_system.get_user("user123")
user.language = Language.SPANISH
await collab_system.create_user(user)  # Update user
```

## Moderatsiya

### Content Moderation

```python
# Kontentni moderatsiya qilish
result = await collab_system.content_moderator.moderate_content(
    content="This is a test message",
    user_id="user123"
)

print(result)
# Output: {
#     "approved": True,
#     "reasons": [],
#     "action": "allow"
# }
```

### Spam Prevention

```python
# Spam tekshirish
is_spam = collab_system.content_moderator._is_spam(
    "http://spam.com http://spam.com http://spam.com"
)
print(f"Is spam: {is_spam}")  # Output: True
```

## Analytics va Monitoring

### Chat Analytics

```python
# Chat analytics olish
analytics = await collab_system.get_chat_analytics(chat_id)

print(analytics)
# Output: {
#     "chat_id": "123",
#     "total_messages": 150,
#     "active_users": 5,
#     "user_message_counts": {
#         "user1": 50,
#         "user2": 40,
#         "user3": 35,
#         "user4": 20,
#         "user5": 5
#     },
#     "messages_per_day": {
#         "2025-11-01": 25,
#         "2025-11-02": 30,
#         "2025-11-03": 35,
#         "2025-11-04": 28,
#         "2025-11-05": 32
#     }
# }
```

### Data Export

```python
# Chat ma'lumotlarini eksport qilish
export_data = await collab_system.export_chat_data(chat_id, "json")

# Faylga yozish
with open("chat_export.json", "w", encoding="utf-8") as f:
    f.write(export_data)
```

## Xavfsizlik

### Authentication

```python
# Foydalanuvchi autentifikatsiyasi
async def authenticate_user(token: str) -> Optional[User]:
    # Token validation
    user_data = validate_jwt_token(token)
    if user_data:
        return await collab_system.get_user(user_data["user_id"])
    return None
```

### Authorization

```python
# Ruxsat tekshirish
async def check_chat_permission(user_id: str, chat_id: str) -> bool:
    chat_room = await collab_system.get_chat_room(chat_id)
    return user_id in chat_room.members
```

### Rate Limiting

```python
# Rate limiting
import asyncio
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_requests: int = 10, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    async def is_allowed(self, user_id: str) -> bool:
        now = datetime.now()
        user_requests = self.requests[user_id]
        
        # Remove old requests
        user_requests[:] = [
            req_time for req_time in user_requests
            if (now - req_time).total_seconds() < self.window
        ]
        
        if len(user_requests) < self.max_requests:
            user_requests.append(now)
            return True
        
        return False

rate_limiter = RateLimiter()
```

## Performance Optimization

### Caching

```python
import redis

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis()
    
    async def cache_chat_messages(self, chat_id: str, messages: List[Message]):
        key = f"chat:{chat_id}:messages"
        await self.redis_client.setex(
            key, 
            300,  # 5 minutes
            json.dumps([msg.__dict__ for msg in messages])
        )
    
    async def get_cached_messages(self, chat_id: str) -> Optional[List[Message]]:
        key = f"chat:{chat_id}:messages"
        cached_data = await self.redis_client.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None
```

### Database Optimization

```python
# Indexes
CREATE INDEX idx_messages_chat_id ON messages(chat_id, timestamp DESC);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_trading_signals_symbol ON trading_signals(symbol, created_at DESC);
CREATE INDEX idx_users_status ON users(status);
```

## Testing

### Unit Tests

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_create_chat_room():
    collab_system = CollaborationSystem()
    
    chat_id = await collab_system.create_chat_room(
        name="Test Chat",
        chat_type=ChatType.PUBLIC,
        created_by="user1"
    )
    
    assert chat_id is not None
    assert chat_id in collab_system.chat_rooms

@pytest.mark.asyncio
async def test_send_message():
    collab_system = CollaborationSystem()
    chat_id = await collab_system.create_chat_room("Test", ChatType.PUBLIC, "user1")
    await collab_system.join_chat_room(chat_id, "user1")
    
    message = await collab_system.send_message(
        chat_id, "user1", "Hello World!"
    )
    
    assert message is not None
    assert message.content == "Hello World!"

@pytest.mark.asyncio
async def test_content_moderation():
    moderator = ContentModerator()
    
    # Test approved content
    result = await moderator.moderate_content("Hello everyone!", "user1")
    assert result["approved"] is True
    
    # Test banned content
    result = await moderator.moderate_content("This is a scam!", "user1")
    assert result["approved"] is False
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_full_chat_workflow():
    collab_system = CollaborationSystem()
    
    # Create users
    user1 = User(user_id="user1", username="alice", email="alice@test.com")
    user2 = User(user_id="user2", username="bob", email="bob@test.com")
    
    await collab_system.create_user(user1)
    await collab_system.create_user(user2)
    
    # Create chat
    chat_id = await collab_system.create_chat_room(
        "Test Group", ChatType.PUBLIC, "user1"
    )
    
    # Users join
    await collab_system.join_chat_room(chat_id, "user1")
    await collab_system.join_chat_room(chat_id, "user2")
    
    # Send messages
    msg1 = await collab_system.send_message(chat_id, "user1", "Hello!")
    msg2 = await collab_system.send_message(chat_id, "user2", "Hi Alice!")
    
    # Share signal
    signal_id = await collab_system.share_trading_signal(
        "user1", "EURUSD", "BUY", 1.0850, 1.0900, 1.0800
    )
    
    # Comment on signal
    await collab_system.comment_on_signal(signal_id, "user2", "Good signal!")
    
    # Verify
    analytics = await collab_system.get_chat_analytics(chat_id)
    assert analytics["total_messages"] == 2
    assert analytics["active_users"] == 2
```

## Deployment

### Docker Configuration

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "collaboration_system.py"]
```

### Environment Variables

```bash
# .env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
REDIS_URL=redis://localhost:6379
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=52428800
LOG_LEVEL=INFO
```

### Health Check

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(collab_system.active_connections),
        "total_users": len(collab_system.users),
        "total_chat_rooms": len(collab_system.chat_rooms),
        "total_messages": len(collab_system.messages)
    }
```

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   ```python
   # WebSocket URL tekshirish
   ws_url = "ws://localhost:8000/ws/user123"
   ```

2. **Supabase Connection Error**
   ```python
   # URL va key tekshirish
   print(f"Supabase URL: {supabase_url}")
   print(f"Key exists: {bool(supabase_key)}")
   ```

3. **File Upload Failed**
   ```python
   # Fayl hajmi va turini tekshirish
   if file_size > 50 * 1024 * 1024:  # 50MB
       raise ValueError("File too large")
   ```

### Monitoring

```python
# Log monitoring
import logging

# Error logging
logger.error(f"Failed to send message: {error}")

# Performance monitoring
import time

start_time = time.time()
# Operation
end_time = time.time()
logger.info(f"Operation took {end_time - start_time:.2f} seconds")
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

MIT License - see LICENSE file for details.

## Changelog

### Version 1.0.0 (2025-11-05)
- Initial release
- Basic chat functionality
- Real-time messaging
- File sharing
- Voice calls
- Signal sharing
- Multi-language support
- Content moderation
- Analytics