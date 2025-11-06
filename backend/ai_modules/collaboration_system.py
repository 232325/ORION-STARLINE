"""
Real-time Collaboration System for Orion Starline Trading Platform

This module provides comprehensive real-time collaboration features including:
- Group chat rooms and private chats
- Community features (User profiles, reputation system)
- Signal sharing (Trade signal sharing, comments)
- Group trading discussions (Discussion threads, voting)
- Real-time messaging (WebSocket support)
- File sharing (Document, image, chart sharing)
- Voice calls integration (Voice chat functionality)
- Notifications system (Real-time alerts)
- Moderation tools (Content filtering, spam prevention)
- Supabase real-time integration
- Multi-language support (Uzbek, English, Russian)

Author: Orion Starline Development Team
Version: 1.0.0
Date: 2025-11-05
"""

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

# Supabase and WebSocket imports
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

import websockets
import aiofiles
from fastapi import WebSocket, HTTPException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatType(Enum):
    """Chat room types"""
    PUBLIC = "public"
    PRIVATE = "private"
    GROUP = "group"
    DIRECT = "direct"


class MessageType(Enum):
    """Message types"""
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    SIGNAL = "signal"
    SYSTEM = "system"


class UserRole(Enum):
    """User roles in chat"""
    MEMBER = "member"
    MODERATOR = "moderator"
    ADMIN = "admin"
    OWNER = "owner"


class NotificationType(Enum):
    """Notification types"""
    MESSAGE = "message"
    MENTION = "mention"
    SIGNAL = "signal"
    SYSTEM = "system"
    ALERT = "alert"


class Language(Enum):
    """Supported languages"""
    UZBEK = "uz"
    ENGLISH = "en"
    RUSSIAN = "ru"


@dataclass
class User:
    """User profile"""
    user_id: str
    username: str
    email: str
    avatar_url: Optional[str] = None
    status: str = "offline"
    last_seen: datetime = field(default_factory=datetime.now)
    reputation_score: int = 0
    language: Language = Language.ENGLISH
    timezone: str = "UTC"
    preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Chat message"""
    message_id: str
    chat_id: str
    user_id: str
    content: str
    message_type: MessageType = MessageType.TEXT
    timestamp: datetime = field(default_factory=datetime.now)
    edited: bool = False
    edited_at: Optional[datetime] = None
    reply_to: Optional[str] = None
    reactions: Dict[str, List[str]] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    is_deleted: bool = False


@dataclass
class ChatRoom:
    """Chat room/group"""
    chat_id: str
    name: str
    description: Optional[str] = None
    chat_type: ChatType = ChatType.PUBLIC
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)
    members: Set[str] = field(default_factory=set)
    moderators: Set[str] = field(default_factory=set)
    settings: Dict[str, Any] = field(default_factory=dict)
    topic: Optional[str] = None


@dataclass
class TradingSignal:
    """Trading signal"""
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
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "active"  # active, closed, cancelled
    comments: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class FileAttachment:
    """File attachment"""
    file_id: str
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_by: str
    uploaded_at: datetime = field(default_factory=datetime.now)
    is_public: bool = False


@dataclass
class Notification:
    """Notification"""
    notification_id: str
    user_id: str
    title: str
    content: str
    notification_type: NotificationType
    read: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)


class ContentModerator:
    """Content moderation system"""
    
    def __init__(self):
        self.banned_words = [
            "spam", "scam", "fake", "fraud", 
            # Add more banned words
        ]
        self.spam_patterns = [
            r"(.)\1{5,}",  # Repeated characters
            r"https?://[^\s]+",  # URL spam
            r"[A-Z]{10,}",  # All caps
        ]
    
    async def moderate_content(self, content: str, user_id: str) -> Dict[str, Any]:
        """Moderate user content"""
        moderation_result = {
            "approved": True,
            "reasons": [],
            "action": "allow"
        }
        
        # Check for banned words
        content_lower = content.lower()
        for banned_word in self.banned_words:
            if banned_word in content_lower:
                moderation_result["approved"] = False
                moderation_result["reasons"].append(f"Banned word: {banned_word}")
                moderation_result["action"] = "block"
                break
        
        # Check spam patterns
        if not moderation_result["approved"]:
            return moderation_result
        
        # Check for spam indicators
        if self._is_spam(content):
            moderation_result["approved"] = False
            moderation_result["reasons"].append("Potential spam detected")
            moderation_result["action"] = "review"
        
        return moderation_result
    
    def _is_spam(self, content: str) -> bool:
        """Check if content is spam"""
        # Simple spam detection - can be enhanced
        return len(content.strip()) == 0 or content.count("http") > 3


class FileManager:
    """File sharing and storage management"""
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.allowed_extensions = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
            'document': ['.pdf', '.doc', '.docx', '.txt', '.csv', '.xlsx'],
            'chart': ['.png', '.jpg', '.svg'],
            'audio': ['.mp3', '.wav', '.m4a'],
            'video': ['.mp4', '.avi', '.mov']
        }
    
    async def upload_file(self, file_data: bytes, filename: str, 
                         user_id: str, file_type: str = "document") -> Optional[FileAttachment]:
        """Upload file to storage"""
        try:
            # Validate file
            file_extension = Path(filename).suffix.lower()
            if not self._is_allowed_file(file_extension, file_type):
                return None
            
            # Generate unique filename
            file_hash = hashlib.md5(file_data).hexdigest()
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = self.upload_dir / unique_filename
            
            # Check file size
            if len(file_data) > self.max_file_size:
                return None
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_data)
            
            # Create file attachment record
            attachment = FileAttachment(
                file_id=str(uuid.uuid4()),
                filename=filename,
                file_path=str(file_path),
                file_size=len(file_data),
                mime_type=mimetypes.guess_type(filename)[0] or 'application/octet-stream',
                uploaded_by=user_id
            )
            
            return attachment
            
        except Exception as e:
            logger.error(f"File upload error: {e}")
            return None
    
    def _is_allowed_file(self, extension: str, file_type: str) -> bool:
        """Check if file extension is allowed"""
        if file_type in self.allowed_extensions:
            return extension in self.allowed_extensions[file_type]
        return False


class VoiceCallManager:
    """Voice call management"""
    
    def __init__(self):
        self.active_calls: Dict[str, Dict[str, Any]] = {}
    
    async def initiate_call(self, chat_id: str, initiator_id: str, 
                           participant_ids: List[str]) -> str:
        """Initiate voice call"""
        call_id = str(uuid.uuid4())
        
        call_info = {
            "call_id": call_id,
            "chat_id": chat_id,
            "initiator_id": initiator_id,
            "participants": [initiator_id] + participant_ids,
            "status": "initiating",
            "started_at": datetime.now(),
            "duration": 0,
            "ended_at": None
        }
        
        self.active_calls[call_id] = call_info
        return call_id
    
    async def join_call(self, call_id: str, user_id: str) -> bool:
        """Join voice call"""
        if call_id not in self.active_calls:
            return False
        
        call_info = self.active_calls[call_id]
        if user_id not in call_info["participants"]:
            call_info["participants"].append(user_id)
        
        return True
    
    async def end_call(self, call_id: str) -> Optional[Dict[str, Any]]:
        """End voice call"""
        if call_id not in self.active_calls:
            return None
        
        call_info = self.active_calls[call_id]
        call_info["status"] = "ended"
        call_info["ended_at"] = datetime.now()
        call_info["duration"] = (
            call_info["ended_at"] - call_info["started_at"]
        ).total_seconds()
        
        ended_call = call_info.copy()
        del self.active_calls[call_id]
        return ended_call


class NotificationManager:
    """Real-time notification system"""
    
    def __init__(self):
        self.user_notifications: Dict[str, List[Notification]] = {}
        self.notification_callbacks: Dict[str, callable] = {}
    
    async def create_notification(self, notification: Notification) -> bool:
        """Create notification for user"""
        if notification.user_id not in self.user_notifications:
            self.user_notifications[notification.user_id] = []
        
        self.user_notifications[notification.user_id].append(notification)
        
        # Trigger callback if registered
        if notification.user_id in self.notification_callbacks:
            try:
                await self.notification_callbacks[notification.user_id](notification)
            except Exception as e:
                logger.error(f"Notification callback error: {e}")
        
        return True
    
    async def get_user_notifications(self, user_id: str, 
                                   unread_only: bool = False) -> List[Notification]:
        """Get user notifications"""
        notifications = self.user_notifications.get(user_id, [])
        
        if unread_only:
            notifications = [n for n in notifications if not n.read]
        
        return sorted(notifications, key=lambda x: x.created_at, reverse=True)
    
    async def mark_as_read(self, user_id: str, notification_id: str) -> bool:
        """Mark notification as read"""
        notifications = self.user_notifications.get(user_id, [])
        
        for notification in notifications:
            if notification.notification_id == notification_id:
                notification.read = True
                return True
        
        return False
    
    def register_callback(self, user_id: str, callback: callable):
        """Register notification callback"""
        self.notification_callbacks[user_id] = callback


class ReputationSystem:
    """User reputation system"""
    
    def __init__(self):
        self.user_reputations: Dict[str, int] = {}
        self.reputation_weights = {
            "message_likes": 1,
            "signal_accuracy": 5,
            "helpful_comment": 2,
            "quality_content": 3,
            "community_contribution": 4
        }
    
    async def update_reputation(self, user_id: str, action: str, delta: int = 1) -> int:
        """Update user reputation"""
        if user_id not in self.user_reputations:
            self.user_reputations[user_id] = 0
        
        weight = self.reputation_weights.get(action, 1)
        self.user_reputations[user_id] += delta * weight
        
        return self.user_reputations[user_id]
    
    def get_reputation(self, user_id: str) -> int:
        """Get user reputation score"""
        return self.user_reputations.get(user_id, 0)
    
    async def get_reputation_rank(self, user_id: str) -> Optional[int]:
        """Get user's reputation rank"""
        if user_id not in self.user_reputations:
            return None
        
        user_score = self.user_reputations[user_id]
        higher_scores = sum(1 for score in self.user_reputations.values() 
                           if score > user_score)
        return higher_scores + 1


class CollaborationSystem:
    """Main real-time collaboration system"""
    
    def __init__(self, supabase_url: Optional[str] = None, 
                 supabase_key: Optional[str] = None):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase_client: Optional[Client] = None
        
        if SUPABASE_AVAILABLE and supabase_url and supabase_key:
            try:
                self.supabase_client = create_client(supabase_url, supabase_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase: {e}")
        
        # Initialize managers
        self.content_moderator = ContentModerator()
        self.file_manager = FileManager()
        self.voice_call_manager = VoiceCallManager()
        self.notification_manager = NotificationManager()
        self.reputation_system = ReputationSystem()
        
        # Data storage
        self.users: Dict[str, User] = {}
        self.chat_rooms: Dict[str, ChatRoom] = {}
        self.messages: Dict[str, Message] = {}
        self.trading_signals: Dict[str, TradingSignal] = {}
        self.active_connections: Dict[str, WebSocket] = {}
        self.chat_participants: Dict[str, Set[str]] = {}
        
        # Language translations
        self.translations = {
            Language.UZBEK: {
                "welcome": "Xush kelibsiz!",
                "new_message": "Yangi xabar",
                "signal_shared": "Signal ulashildi",
                "user_joined": "Foydalanuvchi qo'shildi",
                "moderation_required": "Kontent moderatsiyani talab qiladi"
            },
            Language.ENGLISH: {
                "welcome": "Welcome!",
                "new_message": "New message",
                "signal_shared": "Signal shared",
                "user_joined": "User joined",
                "moderation_required": "Content requires moderation"
            },
            Language.RUSSIAN: {
                "welcome": "Добро пожаловать!",
                "new_message": "Новое сообщение",
                "signal_shared": "Сигнал отправлен",
                "user_joined": "Пользователь присоединился",
                "moderation_required": "Контент требует модерации"
            }
        }
    
    def get_text(self, key: str, language: Language) -> str:
        """Get translated text"""
        return self.translations.get(language, {}).get(key, key)
    
    # User Management
    async def create_user(self, user: User) -> bool:
        """Create new user"""
        self.users[user.user_id] = user
        return True
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    async def update_user_status(self, user_id: str, status: str) -> bool:
        """Update user online status"""
        if user_id in self.users:
            self.users[user_id].status = status
            self.users[user_id].last_seen = datetime.now()
            return True
        return False
    
    # Chat Room Management
    async def create_chat_room(self, name: str, chat_type: ChatType, 
                              created_by: str, description: str = "") -> str:
        """Create new chat room"""
        chat_id = str(uuid.uuid4())
        
        chat_room = ChatRoom(
            chat_id=chat_id,
            name=name,
            description=description,
            chat_type=chat_type,
            created_by=created_by,
            members={created_by},
            moderators={created_by}
        )
        
        self.chat_rooms[chat_id] = chat_room
        self.chat_participants[chat_id] = set([created_by])
        
        return chat_id
    
    async def join_chat_room(self, chat_id: str, user_id: str) -> bool:
        """Join chat room"""
        if chat_id in self.chat_rooms:
            self.chat_rooms[chat_id].members.add(user_id)
            self.chat_participants[chat_id].add(user_id)
            
            # Send system message
            await self._send_system_message(
                chat_id, 
                f"User {user_id} joined the chat",
                MessageType.SYSTEM
            )
            return True
        return False
    
    async def leave_chat_room(self, chat_id: str, user_id: str) -> bool:
        """Leave chat room"""
        if chat_id in self.chat_rooms and user_id in self.chat_rooms[chat_id].members:
            self.chat_rooms[chat_id].members.discard(user_id)
            self.chat_participants[chat_id].discard(user_id)
            return True
        return False
    
    async def get_chat_rooms(self, user_id: str) -> List[ChatRoom]:
        """Get user's chat rooms"""
        user_rooms = []
        for chat_room in self.chat_rooms.values():
            if user_id in chat_room.members:
                user_rooms.append(chat_room)
        return user_rooms
    
    # Message Management
    async def send_message(self, chat_id: str, user_id: str, content: str,
                          message_type: MessageType = MessageType.TEXT,
                          reply_to: Optional[str] = None,
                          attachments: List[Dict[str, Any]] = None) -> Optional[Message]:
        """Send message to chat room"""
        
        # Check if user is member of chat room
        if chat_id not in self.chat_rooms or user_id not in self.chat_rooms[chat_id].members:
            return None
        
        # Moderate content
        moderation_result = await self.content_moderator.moderate_content(content, user_id)
        
        if not moderation_result["approved"]:
            logger.warning(f"Message blocked for user {user_id}: {moderation_result['reasons']}")
            return None
        
        # Create message
        message = Message(
            message_id=str(uuid.uuid4()),
            chat_id=chat_id,
            user_id=user_id,
            content=content,
            message_type=message_type,
            reply_to=reply_to,
            attachments=attachments or []
        )
        
        # Store message
        self.messages[message.message_id] = message
        
        # Broadcast to chat participants
        await self._broadcast_to_chat(chat_id, {
            "type": "message",
            "message": message.__dict__
        })
        
        # Update reputation
        await self.reputation_system.update_reputation(user_id, "message_sent")
        
        return message
    
    async def edit_message(self, message_id: str, user_id: str, 
                          new_content: str) -> bool:
        """Edit message"""
        if message_id in self.messages:
            message = self.messages[message_id]
            if message.user_id == user_id and not message.is_deleted:
                # Moderate new content
                moderation_result = await self.content_moderator.moderate_content(
                    new_content, user_id
                )
                
                if moderation_result["approved"]:
                    message.content = new_content
                    message.edited = True
                    message.edited_at = datetime.now()
                    
                    # Broadcast edit
                    await self._broadcast_to_chat(message.chat_id, {
                        "type": "message_edited",
                        "message_id": message_id,
                        "new_content": new_content,
                        "edited_at": message.edited_at.isoformat()
                    })
                    return True
        return False
    
    async def delete_message(self, message_id: str, user_id: str) -> bool:
        """Delete message"""
        if message_id in self.messages:
            message = self.messages[message_id]
            chat_room = self.chat_rooms.get(message.chat_id)
            
            # Check permissions
            if (message.user_id == user_id or 
                (chat_room and user_id in chat_room.moderators)):
                
                message.is_deleted = True
                
                # Broadcast deletion
                await self._broadcast_to_chat(message.chat_id, {
                    "type": "message_deleted",
                    "message_id": message_id
                })
                return True
        return False
    
    async def add_reaction(self, message_id: str, user_id: str, 
                          reaction: str) -> bool:
        """Add reaction to message"""
        if message_id in self.messages:
            message = self.messages[message_id]
            if reaction not in message.reactions:
                message.reactions[reaction] = []
            
            if user_id not in message.reactions[reaction]:
                message.reactions[reaction].append(user_id)
                
                # Broadcast reaction
                await self._broadcast_to_chat(message.chat_id, {
                    "type": "message_reaction",
                    "message_id": message_id,
                    "user_id": user_id,
                    "reaction": reaction,
                    "action": "add"
                })
                return True
        return False
    
    # Trading Signal Management
    async def share_trading_signal(self, user_id: str, symbol: str, 
                                  signal_type: str, entry_price: float,
                                  target_price: Optional[float] = None,
                                  stop_loss: Optional[float] = None,
                                  timeframe: str = "1D",
                                  analysis: str = "") -> str:
        """Share trading signal"""
        signal = TradingSignal(
            signal_id=str(uuid.uuid4()),
            user_id=user_id,
            symbol=symbol,
            signal_type=signal_type,
            entry_price=entry_price,
            target_price=target_price,
            stop_loss=stop_loss,
            timeframe=timeframe,
            analysis=analysis
        )
        
        self.trading_signals[signal.signal_id] = signal
        
        # Send notification to followers
        await self._notify_signal_share(signal)
        
        return signal.signal_id
    
    async def comment_on_signal(self, signal_id: str, user_id: str,
                               comment: str) -> bool:
        """Add comment to trading signal"""
        if signal_id in self.trading_signals:
            comment_data = {
                "comment_id": str(uuid.uuid4()),
                "user_id": user_id,
                "comment": comment,
                "timestamp": datetime.now().isoformat()
            }
            
            self.trading_signals[signal_id]["comments"].append(comment_data)
            
            # Update reputation for helpful comment
            await self.reputation_system.update_reputation(user_id, "helpful_comment")
            
            return True
        return False
    
    async def vote_on_signal(self, signal_id: str, user_id: str, 
                           vote: str) -> bool:
        """Vote on trading signal (useful/not useful)"""
        if signal_id in self.trading_signals:
            signal = self.trading_signals[signal_id]
            
            # Add vote tracking (simplified)
            if "votes" not in signal:
                signal["votes"] = {"useful": [], "not_useful": []}
            
            # Remove from both lists first
            for vote_type in ["useful", "not_useful"]:
                if user_id in signal["votes"][vote_type]:
                    signal["votes"][vote_type].remove(user_id)
            
            # Add to new vote
            if vote in ["useful", "not_useful"]:
                signal["votes"][vote].append(user_id)
                
                # Update reputation
                if vote == "useful":
                    await self.reputation_system.update_reputation(
                        signal["user_id"], "signal_accuracy"
                    )
                
                return True
        return False
    
    # File Sharing
    async def upload_file(self, file_data: bytes, filename: str, 
                         user_id: str, chat_id: str,
                         file_type: str = "document") -> Optional[FileAttachment]:
        """Upload file to chat"""
        attachment = await self.file_manager.upload_file(
            file_data, filename, user_id, file_type
        )
        
        if attachment:
            # Send file message
            await self.send_message(
                chat_id, user_id, f"Shared file: {filename}",
                MessageType.DOCUMENT,
                attachments=[attachment.__dict__]
            )
        
        return attachment
    
    # Voice Call Management
    async def start_voice_call(self, chat_id: str, initiator_id: str,
                              participant_ids: List[str]) -> str:
        """Start voice call in chat"""
        call_id = await self.voice_call_manager.initiate_call(
            chat_id, initiator_id, participant_ids
        )
        
        # Notify participants
        await self._broadcast_to_chat(chat_id, {
            "type": "voice_call_started",
            "call_id": call_id,
            "initiator_id": initiator_id
        })
        
        return call_id
    
    async def end_voice_call(self, call_id: str) -> Optional[Dict[str, Any]]:
        """End voice call"""
        ended_call = await self.voice_call_manager.end_call(call_id)
        
        if ended_call:
            await self._broadcast_to_chat(ended_call["chat_id"], {
                "type": "voice_call_ended",
                "call_id": call_id,
                "duration": ended_call["duration"]
            })
        
        return ended_call
    
    # WebSocket Management
    async def connect_user(self, websocket: WebSocket, user_id: str):
        """Connect user via WebSocket"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        
        # Update user status
        await self.update_user_status(user_id, "online")
        
        try:
            # Send welcome message
            user = await self.get_user(user_id)
            if user:
                welcome_text = self.get_text("welcome", user.language)
                await websocket.send_json({
                    "type": "welcome",
                    "message": welcome_text,
                    "user_id": user_id
                })
            
            # Keep connection alive
            while True:
                try:
                    data = await websocket.receive_text()
                    await self._handle_message(user_id, data)
                except websockets.exceptions.ConnectionClosed:
                    break
                    
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            await self.disconnect_user(user_id)
    
    async def disconnect_user(self, user_id: str):
        """Disconnect user"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        await self.update_user_status(user_id, "offline")
    
    async def _handle_message(self, user_id: str, data: str):
        """Handle incoming WebSocket message"""
        try:
            message_data = json.loads(data)
            message_type = message_data.get("type")
            
            if message_type == "ping":
                await self._send_to_user(user_id, {"type": "pong"})
            elif message_type == "typing":
                await self._broadcast_to_user_chats(user_id, {
                    "type": "user_typing",
                    "user_id": user_id,
                    "chat_id": message_data.get("chat_id")
                })
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from user {user_id}")
    
    async def _send_to_user(self, user_id: str, data: Dict[str, Any]):
        """Send data to specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(data)
            except Exception as e:
                logger.error(f"Failed to send to user {user_id}: {e}")
    
    async def _broadcast_to_chat(self, chat_id: str, data: Dict[str, Any]):
        """Broadcast data to all chat participants"""
        if chat_id in self.chat_participants:
            for user_id in self.chat_participants[chat_id]:
                await self._send_to_user(user_id, data)
    
    async def _broadcast_to_user_chats(self, user_id: str, data: Dict[str, Any]):
        """Broadcast data to all chats user is in"""
        for chat_id, participants in self.chat_participants.items():
            if user_id in participants:
                await self._broadcast_to_chat(chat_id, data)
    
    async def _send_system_message(self, chat_id: str, content: str,
                                  message_type: MessageType = MessageType.SYSTEM):
        """Send system message to chat"""
        system_message = Message(
            message_id=str(uuid.uuid4()),
            chat_id=chat_id,
            user_id="system",
            content=content,
            message_type=message_type
        )
        
        self.messages[system_message.message_id] = system_message
        await self._broadcast_to_chat(chat_id, {
            "type": "system_message",
            "message": system_message.__dict__
        })
    
    async def _notify_signal_share(self, signal: TradingSignal):
        """Notify users about signal share"""
        # This would typically notify followers or relevant users
        # For now, we'll just log it
        logger.info(f"Signal shared: {signal.signal_id} by {signal.user_id}")
    
    # Analytics and Reporting
    async def get_chat_analytics(self, chat_id: str) -> Dict[str, Any]:
        """Get chat room analytics"""
        if chat_id not in self.chat_rooms:
            return {}
        
        chat_messages = [
            msg for msg in self.messages.values() 
            if msg.chat_id == chat_id and not msg.is_deleted
        ]
        
        user_messages = {}
        for message in chat_messages:
            user_id = message.user_id
            if user_id not in user_messages:
                user_messages[user_id] = 0
            user_messages[user_id] += 1
        
        return {
            "chat_id": chat_id,
            "total_messages": len(chat_messages),
            "active_users": len(user_messages),
            "user_message_counts": user_messages,
            "messages_per_day": self._calculate_messages_per_day(chat_messages)
        }
    
    def _calculate_messages_per_day(self, messages: List[Message]) -> Dict[str, int]:
        """Calculate messages per day"""
        messages_per_day = {}
        for message in messages:
            day = message.timestamp.strftime("%Y-%m-%d")
            messages_per_day[day] = messages_per_day.get(day, 0) + 1
        return messages_per_day
    
    # Data Export/Import
    async def export_chat_data(self, chat_id: str, format: str = "json") -> str:
        """Export chat data"""
        if chat_id not in self.chat_rooms:
            return ""
        
        chat_data = {
            "chat_info": self.chat_rooms[chat_id].__dict__,
            "messages": [
                msg.__dict__ for msg in self.messages.values()
                if msg.chat_id == chat_id
            ],
            "signals": [
                signal.__dict__ for signal in self.trading_signals.values()
                if signal.get("chat_id") == chat_id
            ]
        }
        
        if format == "json":
            return json.dumps(chat_data, default=str, indent=2)
        
        return str(chat_data)
    
    # Cleanup and Maintenance
    async def cleanup_old_data(self, days: int = 30):
        """Clean up old messages and data"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Clean old messages
        old_messages = [
            msg_id for msg_id, msg in self.messages.items()
            if msg.timestamp < cutoff_date and msg.is_deleted
        ]
        
        for msg_id in old_messages:
            del self.messages[msg_id]
        
        logger.info(f"Cleaned up {len(old_messages)} old messages")


# Example usage and testing
async def main():
    """Example usage of the collaboration system"""
    
    # Initialize system
    collab_system = CollaborationSystem(
        supabase_url="your_supabase_url",
        supabase_key="your_supabase_key"
    )
    
    # Create test users
    user1 = User(
        user_id="user1",
        username="trader_ali",
        email="ali@example.com",
        language=Language.UZBEK
    )
    
    user2 = User(
        user_id="user2",
        username="trader_maria",
        email="maria@example.com",
        language=Language.ENGLISH
    )
    
    await collab_system.create_user(user1)
    await collab_system.create_user(user2)
    
    # Create chat room
    chat_id = await collab_system.create_chat_room(
        name="USD/EUR Trading Group",
        chat_type=ChatType.PUBLIC,
        created_by="user1",
        description="Discussion and analysis of USD/EUR pair"
    )
    
    # Join users to chat
    await collab_system.join_chat_room(chat_id, "user1")
    await collab_system.join_chat_room(chat_id, "user2")
    
    # Send messages
    await collab_system.send_message(
        chat_id, "user1", "Welcome to our trading group!", MessageType.TEXT
    )
    
    await collab_system.send_message(
        chat_id, "user2", "Hello everyone! Ready to trade?", MessageType.TEXT
    )
    
    # Share trading signal
    signal_id = await collab_system.share_trading_signal(
        user_id="user1",
        symbol="EURUSD",
        signal_type="BUY",
        entry_price=1.0850,
        target_price=1.0900,
        stop_loss=1.0800,
        analysis="Strong bullish momentum on EUR"
    )
    
    # Comment on signal
    await collab_system.comment_on_signal(
        signal_id, "user2", "I agree with this analysis. EUR looks strong."
    )
    
    # Get analytics
    analytics = await collab_system.get_chat_analytics(chat_id)
    print("Chat Analytics:", json.dumps(analytics, indent=2))
    
    # Export data
    export_data = await collab_system.export_chat_data(chat_id)
    print("Exported Data:", export_data)


if __name__ == "__main__":
    # Run example
    asyncio.run(main())