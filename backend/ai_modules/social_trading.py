"""
Social Trading Platform Module

Bu modul ijtimoiy savdo platformasi uchun barcha kerakli funksiyalarni ta'minlaydi.
Ushbu modul quyidagi imkoniyatlarni o'z ichiga oladi:

1. Copy Trading - Muvaffaqiyatli treyderlarni kuzatish
2. Signal almashish - Ommaviy/shaxsiy signal almashish
3. Reyting tizimi - Treyder obro'si va signal aniqligi
4. Eng yaxshi ijrochilar reytingi - Ranking tizimi
5. Foydalanuvchi profillari - Treyder profillari va statistika
6. Amalga oshirish kuzatuvi - Real vaqt copy trading natijalari
7. Komissiya boshqaruvi - Daromad taqsimoti
8. Ijtimoiy xususiyatlar - Izohlar, likes, obuna tizimi
9. Tasdiqlash tizimi - Treyder tasdiqlash va autentifikatsiya

Muallif: AI Team
Yaratilgan sana: 2025-11-05
"""

import json
import datetime
import sqlite3
import hashlib
import uuid
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time
import random
from collections import defaultdict, deque
import logging

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignalType(Enum):
    """Signal turlari"""
    BUY = "buy"
    SELL = "sell"
    CLOSE = "close"
    HOLD = "hold"

class SignalPrivacy(Enum):
    """Signal mashrurity darajasi"""
    PUBLIC = "public"
    PRIVATE = "private"
    SUBSCRIBERS_ONLY = "subscribers_only"

class VerificationStatus(Enum):
    """Tasdiqlash holatlari"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class UserRole(Enum):
    """Foydalanuvchi rollari"""
    TRADER = "trader"
    FOLLOWER = "follower"
    ADMIN = "admin"

@dataclass
class User:
    """Foydalanuvchi ma'lumotlari"""
    user_id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    verification_status: VerificationStatus
    created_at: datetime.datetime
    last_active: datetime.datetime
    bio: str = ""
    avatar_url: str = ""
    total_balance: float = 0.0
    is_active: bool = True
    verification_documents: List[str] = None

    def __post_init__(self):
        if self.verification_documents is None:
            self.verification_documents = []

@dataclass
class TraderProfile:
    """Treyder profili"""
    trader_id: str
    followers_count: int
    following_count: int
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_loss: float
    sharpe_ratio: float
    max_drawdown: float
    avg_trade_duration: float
    total_commission_earned: float
    rating: float
    verified: bool
    specialty_assets: List[str]
    risk_level: str  # "low", "medium", "high"
    performance_history: List[Dict] = None

    def __post_init__(self):
        if self.performance_history is None:
            self.performance_history = []

@dataclass
class TradingSignal:
    """Savdo signal"""
    signal_id: str
    trader_id: str
    symbol: str
    signal_type: SignalType
    price: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    privacy: SignalPrivacy
    confidence: float
    description: str
    created_at: datetime.datetime
    expires_at: Optional[datetime.datetime]
    status: str = "active"  # active, executed, expired, cancelled
    execution_price: Optional[float] = None
    profit_loss: Optional[float] = None
    accuracy: Optional[float] = None

@dataclass
class CopyTrade:
    """Copy trading"""
    copy_trade_id: str
    follower_id: str
    trader_id: str
    signal_id: str
    original_signal: Dict
    copied_at: datetime.datetime
    amount: float
    execution_price: float
    current_price: float
    profit_loss: float
    status: str = "active"  # active, closed
    closed_at: Optional[datetime.datetime] = None
    commission_paid: float = 0.0

@dataclass
class Comment:
    """Izoh"""
    comment_id: str
    user_id: str
    content: str
    created_at: datetime.datetime
    parent_id: Optional[str] = None
    likes_count: int = 0
    is_deleted: bool = False

@dataclass
class Notification:
    """Bildirishnoma"""
    notification_id: str
    user_id: str
    title: str
    message: str
    notification_type: str
    created_at: datetime.datetime
    read: bool = False
    action_url: Optional[str] = None

class SocialTradingPlatform:
    """Social Trading Platform - Boshqaruvchi sinf"""

    def __init__(self, db_path: str = "social_trading.db"):
        """Platformani ishga tushirish"""
        self.db_path = db_path
        self.lock = threading.Lock()
        self.active_copy_trades: Dict[str, CopyTrade] = {}
        self.user_notifications: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.performance_cache: Dict[str, Dict] = {}
        
        self._init_database()
        self._start_background_tasks()

    def _init_database(self):
        """Ma'lumotlar bazasini yaratish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users jadvali
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    verification_status TEXT NOT NULL,
                    created_at TIMESTAMP,
                    last_active TIMESTAMP,
                    bio TEXT,
                    avatar_url TEXT,
                    total_balance REAL DEFAULT 0.0,
                    is_active BOOLEAN DEFAULT 1,
                    verification_documents TEXT
                )
            """)
            
            # Trader profiles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trader_profiles (
                    trader_id TEXT PRIMARY KEY,
                    followers_count INTEGER DEFAULT 0,
                    following_count INTEGER DEFAULT 0,
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    losing_trades INTEGER DEFAULT 0,
                    win_rate REAL DEFAULT 0.0,
                    profit_loss REAL DEFAULT 0.0,
                    sharpe_ratio REAL DEFAULT 0.0,
                    max_drawdown REAL DEFAULT 0.0,
                    avg_trade_duration REAL DEFAULT 0.0,
                    total_commission_earned REAL DEFAULT 0.0,
                    rating REAL DEFAULT 0.0,
                    verified BOOLEAN DEFAULT 0,
                    specialty_assets TEXT,
                    risk_level TEXT DEFAULT 'medium',
                    performance_history TEXT
                )
            """)
            
            # Trading signals
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trading_signals (
                    signal_id TEXT PRIMARY KEY,
                    trader_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    price REAL NOT NULL,
                    stop_loss REAL,
                    take_profit REAL,
                    privacy TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    execution_price REAL,
                    profit_loss REAL,
                    accuracy REAL,
                    FOREIGN KEY (trader_id) REFERENCES users (user_id)
                )
            """)
            
            # Copy trades
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS copy_trades (
                    copy_trade_id TEXT PRIMARY KEY,
                    follower_id TEXT NOT NULL,
                    trader_id TEXT NOT NULL,
                    signal_id TEXT NOT NULL,
                    original_signal TEXT NOT NULL,
                    copied_at TIMESTAMP,
                    amount REAL NOT NULL,
                    execution_price REAL NOT NULL,
                    current_price REAL NOT NULL,
                    profit_loss REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'active',
                    closed_at TIMESTAMP,
                    commission_paid REAL DEFAULT 0.0,
                    FOREIGN KEY (follower_id) REFERENCES users (user_id),
                    FOREIGN KEY (trader_id) REFERENCES users (user_id)
                )
            """)
            
            # Followers
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS followers (
                    follower_id TEXT NOT NULL,
                    trader_id TEXT NOT NULL,
                    followed_at TIMESTAMP,
                    copy_percentage REAL DEFAULT 100.0,
                    PRIMARY KEY (follower_id, trader_id)
                )
            """)
            
            # Comments
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    comment_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP,
                    parent_id TEXT,
                    likes_count INTEGER DEFAULT 0,
                    is_deleted BOOLEAN DEFAULT 0
                )
            """)
            
            # Likes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS likes (
                    user_id TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    liked_at TIMESTAMP,
                    PRIMARY KEY (user_id, entity_id)
                )
            """)
            
            # Notifications
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    notification_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    notification_type TEXT NOT NULL,
                    created_at TIMESTAMP,
                    read BOOLEAN DEFAULT 0,
                    action_url TEXT
                )
            """)
            
            # Performance metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    metric_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    calculated_at TIMESTAMP,
                    period_start TIMESTAMP,
                    period_end TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("Ma'lumotlar bazasi muvaffaqiyatli yaratildi")

    # ==================== AUTHENTICATION ====================
    
    def register_user(self, username: str, email: str, password: str, role: UserRole = UserRole.FOLLOWER) -> Dict[str, Any]:
        """Yangi foydalanuvchi ro'yxatdan o'tkazish"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Username va email mavjudligini tekshirish
                    cursor.execute("SELECT user_id FROM users WHERE username = ? OR email = ?", (username, email))
                    if cursor.fetchone():
                        return {"success": False, "message": "Username yoki email allaqachon mavjud"}
                    
                    # Yangi foydalanuvchi yaratish
                    user_id = str(uuid.uuid4())
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    now = datetime.datetime.now()
                    
                    user = User(
                        user_id=user_id,
                        username=username,
                        email=email,
                        password_hash=password_hash,
                        role=role,
                        verification_status=VerificationStatus.PENDING,
                        created_at=now,
                        last_active=now
                    )
                    
                    cursor.execute("""
                        INSERT INTO users (user_id, username, email, password_hash, role, verification_status,
                                         created_at, last_active, bio, avatar_url, total_balance, 
                                         is_active, verification_documents)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (user.user_id, user.username, user.email, user.password_hash,
                          user.role.value, user.verification_status.value, user.created_at,
                          user.last_active, user.bio, user.avatar_url, user.total_balance,
                          user.is_active, json.dumps(user.verification_documents)))
                    
                    # Agar treyder bo'lsa, profil yaratish
                    if role == UserRole.TRADER:
                        profile = TraderProfile(
                            trader_id=user_id,
                            followers_count=0,
                            following_count=0,
                            total_trades=0,
                            winning_trades=0,
                            losing_trades=0,
                            win_rate=0.0,
                            profit_loss=0.0,
                            sharpe_ratio=0.0,
                            max_drawdown=0.0,
                            avg_trade_duration=0.0,
                            total_commission_earned=0.0,
                            rating=0.0,
                            verified=False,
                            specialty_assets=[],
                            risk_level="medium"
                        )
                        
                        cursor.execute("""
                            INSERT INTO trader_profiles (trader_id, followers_count, following_count,
                                                       total_trades, winning_trades, losing_trades,
                                                       win_rate, profit_loss, sharpe_ratio, max_drawdown,
                                                       avg_trade_duration, total_commission_earned,
                                                       rating, verified, specialty_assets, risk_level,
                                                       performance_history)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (profile.trader_id, profile.followers_count, profile.following_count,
                              profile.total_trades, profile.winning_trades, profile.losing_trades,
                              profile.win_rate, profile.profit_loss, profile.sharpe_ratio,
                              profile.max_drawdown, profile.avg_trade_duration,
                              profile.total_commission_earned, profile.rating, profile.verified,
                              json.dumps(profile.specialty_assets), profile.risk_level,
                              json.dumps(profile.performance_history)))
                    
                    conn.commit()
                    
                    # Tabriknoma bildirishnoma yuborish
                    self._send_notification(
                        user_id, 
                        "Xush kelibsiz!", 
                        "Social Trading Platform ga muvaffaqiyatli ro'yxatdan o'tdingiz!",
                        "welcome"
                    )
                    
                    return {"success": True, "message": "Muvaffaqiyatli ro'yxatdan o'tdingiz", "user_id": user_id}
                    
        except Exception as e:
            logger.error(f"Foydalanuvchi ro'yxatdan o'tishida xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Foydalanuvchi tizimga kirish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute("""
                    SELECT user_id, username, email, role, verification_status, is_active, last_active
                    FROM users WHERE username = ? AND password_hash = ?
                """, (username, password_hash))
                
                user_data = cursor.fetchone()
                if not user_data:
                    return {"success": False, "message": "Noto'g'ri username yoki parol"}
                
                user_id, username, email, role, verification_status, is_active, last_active = user_data
                
                if not is_active:
                    return {"success": False, "message": "Akkauntingiz bloklangan"}
                
                # Oxirgi faollik vaqtini yangilash
                now = datetime.datetime.now()
                cursor.execute("UPDATE users SET last_active = ? WHERE user_id = ?", (now, user_id))
                conn.commit()
                
                # Aktivlik bildirishnoma
                self._send_notification(
                    user_id, 
                    "Tizimga kirdingiz", 
                    f"Siz muvaffaqiyatli tizimga kirdingiz, {username}!",
                    "login"
                )
                
                return {
                    "success": True, 
                    "message": "Muvaffaqiyatli tizimga kirdingiz",
                    "user_data": {
                        "user_id": user_id,
                        "username": username,
                        "email": email,
                        "role": role,
                        "verification_status": verification_status,
                        "last_active": last_active
                    }
                }
                
        except Exception as e:
            logger.error(f"Tizimga kirishda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    # ==================== USER PROFILES ====================
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Foydalanuvchi profili ma'lumotlarini olish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Asosiy ma'lumotlar
                cursor.execute("""
                    SELECT username, email, role, bio, avatar_url, created_at, verification_status
                    FROM users WHERE user_id = ?
                """, (user_id,))
                
                user_data = cursor.fetchone()
                if not user_data:
                    return {"success": False, "message": "Foydalanuvchi topilmadi"}
                
                username, email, role, bio, avatar_url, created_at, verification_status = user_data
                
                # Agar treyder bo'lsa, trader profilini ham olish
                trader_profile = None
                if role == "trader":
                    cursor.execute("""
                        SELECT followers_count, total_trades, winning_trades, win_rate,
                               profit_loss, rating, verified, specialty_assets, risk_level
                        FROM trader_profiles WHERE trader_id = ?
                    """, (user_id,))
                    
                    profile_data = cursor.fetchone()
                    if profile_data:
                        followers_count, total_trades, winning_trades, win_rate, profit_loss, rating, verified, specialty_assets, risk_level = profile_data
                        trader_profile = {
                            "followers_count": followers_count,
                            "total_trades": total_trades,
                            "winning_trades": winning_trades,
                            "win_rate": win_rate,
                            "profit_loss": profit_loss,
                            "rating": rating,
                            "verified": bool(verified),
                            "specialty_assets": json.loads(specialty_assets) if specialty_assets else [],
                            "risk_level": risk_level
                        }
                
                return {
                    "success": True,
                    "profile": {
                        "user_id": user_id,
                        "username": username,
                        "email": email,
                        "role": role,
                        "bio": bio,
                        "avatar_url": avatar_url,
                        "created_at": created_at,
                        "verification_status": verification_status,
                        "trader_profile": trader_profile
                    }
                }
                
        except Exception as e:
            logger.error(f"Profil ma'lumotlarini olishda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    def update_user_profile(self, user_id: str, bio: str = None, avatar_url: str = None) -> Dict[str, Any]:
        """Foydalanuvchi profilini yangilash"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                updates = []
                values = []
                
                if bio is not None:
                    updates.append("bio = ?")
                    values.append(bio)
                
                if avatar_url is not None:
                    updates.append("avatar_url = ?")
                    values.append(avatar_url)
                
                if updates:
                    values.append(user_id)
                    query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
                    cursor.execute(query, values)
                    conn.commit()
                
                return {"success": True, "message": "Profil muvaffaqiyatli yangilandi"}
                
        except Exception as e:
            logger.error(f"Profil yangilashda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    # ==================== SIGNAL SHARING ====================
    
    def create_signal(self, trader_id: str, symbol: str, signal_type: SignalType,
                     price: float, stop_loss: Optional[float] = None,
                     take_profit: Optional[float] = None, privacy: SignalPrivacy = SignalPrivacy.PUBLIC,
                     confidence: float = 0.8, description: str = "") -> Dict[str, Any]:
        """Yangi savdo signal yaratish"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Treyder profilini tekshirish
                    cursor.execute("SELECT verification_status FROM users WHERE user_id = ?", (trader_id,))
                    user_data = cursor.fetchone()
                    if not user_data:
                        return {"success": False, "message": "Treyder topilmadi"}
                    
                    if user_data[0] != "verified":
                        return {"success": False, "message": "Faqat tasdiqlangan treyderlar signal yarata oladi"}
                    
                    signal_id = str(uuid.uuid4())
                    now = datetime.datetime.now()
                    
                    signal = TradingSignal(
                        signal_id=signal_id,
                        trader_id=trader_id,
                        symbol=symbol,
                        signal_type=signal_type,
                        price=price,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        privacy=privacy,
                        confidence=confidence,
                        description=description,
                        created_at=now,
                        expires_at=None
                    )
                    
                    cursor.execute("""
                        INSERT INTO trading_signals (signal_id, trader_id, symbol, signal_type,
                                                   price, stop_loss, take_profit, privacy,
                                                   confidence, description, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (signal.signal_id, signal.trader_id, signal.symbol, signal.signal_type.value,
                          signal.price, signal.stop_loss, signal.take_profit, signal.privacy.value,
                          signal.confidence, signal.description, signal.created_at))
                    
                    conn.commit()
                    
                    # Obunachilarga bildirishnoma yuborish
                    self._notify_signal_to_followers(trader_id, signal)
                    
                    # Treder profilini yangilash
                    self._update_trader_stats(trader_id, "signal_created")
                    
                    return {"success": True, "message": "Signal muvaffaqiyatli yaratildi", "signal_id": signal_id}
                    
        except Exception as e:
            logger.error(f"Signal yaratishda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    def get_signals(self, trader_id: Optional[str] = None, privacy: Optional[SignalPrivacy] = None,
                   symbol: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Signallarni olish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT s.*, u.username, u.avatar_url, tp.rating, tp.verified
                    FROM trading_signals s
                    JOIN users u ON s.trader_id = u.user_id
                    LEFT JOIN trader_profiles tp ON s.trader_id = tp.trader_id
                    WHERE s.status = 'active'
                """
                
                params = []
                
                if trader_id:
                    query += " AND s.trader_id = ?"
                    params.append(trader_id)
                
                if privacy:
                    query += " AND s.privacy = ?"
                    params.append(privacy.value)
                
                if symbol:
                    query += " AND s.symbol = ?"
                    params.append(symbol)
                
                query += " ORDER BY s.created_at DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                signals = []
                for row in results:
                    signal = {
                        "signal_id": row[0],
                        "trader_id": row[1],
                        "symbol": row[2],
                        "signal_type": row[3],
                        "price": row[4],
                        "stop_loss": row[5],
                        "take_profit": row[6],
                        "privacy": row[7],
                        "confidence": row[8],
                        "description": row[9],
                        "created_at": row[10],
                        "expires_at": row[11],
                        "status": row[12],
                        "execution_price": row[13],
                        "profit_loss": row[14],
                        "accuracy": row[15],
                        "trader_name": row[16],
                        "trader_avatar": row[17],
                        "trader_rating": row[18] or 0.0,
                        "trader_verified": bool(row[19]) if row[19] else False
                    }
                    signals.append(signal)
                
                return {"success": True, "signals": signals}
                
        except Exception as e:
            logger.error(f"Signallarni olishda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    # ==================== COPY TRADING ====================
    
    def start_copy_trading(self, follower_id: str, trader_id: str, amount: float,
                          copy_percentage: float = 100.0) -> Dict[str, Any]:
        """Copy trading boshlash"""
        try:
            with self.lock:
                # Treyder mavjudligini tekshirish
                trader_profile = self.get_trader_profile(trader_id)
                if not trader_profile["success"]:
                    return {"success": False, "message": "Treyder topilmadi"}
                
                # Balansni tekshirish
                follower_balance = self._get_user_balance(follower_id)
                if follower_balance < amount:
                    return {"success": False, "message": "Yetarli balans yo'q"}
                
                copy_trade_id = str(uuid.uuid4())
                now = datetime.datetime.now()
                
                # Obuna ma'lumotlarini bazaga saqlash
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Mavjud obunani tekshirish
                    cursor.execute("""
                        SELECT copy_percentage FROM followers 
                        WHERE follower_id = ? AND trader_id = ?
                    """, (follower_id, trader_id))
                    
                    existing = cursor.fetchone()
                    if existing:
                        cursor.execute("""
                            UPDATE followers SET copy_percentage = ? 
                            WHERE follower_id = ? AND trader_id = ?
                        """, (copy_percentage, follower_id, trader_id))
                    else:
                        cursor.execute("""
                            INSERT INTO followers (follower_id, trader_id, followed_at, copy_percentage)
                            VALUES (?, ?, ?, ?)
                        """, (follower_id, trader_id, now, copy_percentage))
                    
                    conn.commit()
                
                # Copy trade obyektini yaratish
                copy_trade = CopyTrade(
                    copy_trade_id=copy_trade_id,
                    follower_id=follower_id,
                    trader_id=trader_id,
                    signal_id="",  # Signal hali tanlanmagan
                    original_signal={},
                    copied_at=now,
                    amount=amount,
                    execution_price=0.0,
                    current_price=0.0,
                    profit_loss=0.0,
                    status="active"
                )
                
                self.active_copy_trades[copy_trade_id] = copy_trade
                
                # Balansni yangilash
                self._update_user_balance(follower_id, -amount)
                
                # Treyder obunachilar sonini oshirish
                self._update_trader_stats(trader_id, "new_follower")
                
                # Bildirishnoma
                self._send_notification(
                    trader_id,
                    "Yangi obunachi",
                    f"Sizning obunachilar soningiz oshdi!",
                    "new_follower"
                )
                
                return {"success": True, "message": "Copy trading muvaffaqiyatli boshlandi", "copy_trade_id": copy_trade_id}
                
        except Exception as e:
            logger.error(f"Copy trading boshlashda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    def execute_copy_trade(self, signal_id: str, follower_id: str, amount: float) -> Dict[str, Any]:
        """Signal asosida copy trade bajarish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Signal ma'lumotlarini olish
                cursor.execute("""
                    SELECT * FROM trading_signals WHERE signal_id = ?
                """, (signal_id,))
                
                signal_data = cursor.fetchone()
                if not signal_data:
                    return {"success": False, "message": "Signal topilmadi"}
                
                # Copy trade obyektini yaratish
                copy_trade_id = str(uuid.uuid4())
                now = datetime.datetime.now()
                
                copy_trade = CopyTrade(
                    copy_trade_id=copy_trade_id,
                    follower_id=follower_id,
                    trader_id=signal_data[1],  # trader_id
                    signal_id=signal_id,
                    original_signal={
                        "symbol": signal_data[2],
                        "signal_type": signal_data[3],
                        "price": signal_data[4],
                        "stop_loss": signal_data[5],
                        "take_profit": signal_data[6]
                    },
                    copied_at=now,
                    amount=amount,
                    execution_price=signal_data[4],  # Signal narxi
                    current_price=signal_data[4],
                    profit_loss=0.0,
                    status="active"
                )
                
                # Copy trade ni bazaga saqlash
                cursor.execute("""
                    INSERT INTO copy_trades (copy_trade_id, follower_id, trader_id, signal_id,
                                           original_signal, copied_at, amount, execution_price,
                                           current_price, profit_loss, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (copy_trade.copy_trade_id, copy_trade.follower_id, copy_trade.trader_id,
                      copy_trade.signal_id, json.dumps(copy_trade.original_signal),
                      copy_trade.copied_at, copy_trade.amount, copy_trade.execution_price,
                      copy_trade.current_price, copy_trade.profit_loss, copy_trade.status))
                
                conn.commit()
                
                return {"success": True, "message": "Copy trade bajarildi", "copy_trade_id": copy_trade_id}
                
        except Exception as e:
            logger.error(f"Copy trade bajarishda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    # ==================== PERFORMANCE TRACKING ====================
    
    def track_performance(self, user_id: str) -> Dict[str, Any]:
        """Foydalanuvchi amalga oshirishini kuzatish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Copy trade natijalarini olish
                cursor.execute("""
                    SELECT status, profit_loss, amount, copied_at, closed_at
                    FROM copy_trades WHERE follower_id = ?
                """, (user_id,))
                
                trades = cursor.fetchall()
                
                if not trades:
                    return {"success": True, "performance": {
                        "total_trades": 0,
                        "total_profit_loss": 0.0,
                        "win_rate": 0.0,
                        "avg_trade_duration": 0.0,
                        "total_return": 0.0
                    }}
                
                # Statistikalarni hisoblash
                total_trades = len(trades)
                winning_trades = len([t for t in trades if t[1] > 0])  # profit_loss > 0
                total_profit_loss = sum(t[1] for t in trades if t[1] is not None)
                total_invested = sum(t[2] for t in trades)  # amount
                win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
                
                # O'rtacha trade davomiyligi
                durations = []
                for trade in trades:
                    if trade[4]:  # closed_at
                        start = datetime.datetime.fromisoformat(trade[3])
                        end = datetime.datetime.fromisoformat(trade[4])
                        duration = (end - start).total_seconds() / 3600  # soatlarda
                        durations.append(duration)
                
                avg_duration = sum(durations) / len(durations) if durations else 0
                
                # Jami qaytish foizi
                total_return = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
                
                performance = {
                    "total_trades": total_trades,
                    "winning_trades": winning_trades,
                    "losing_trades": total_trades - winning_trades,
                    "total_profit_loss": total_profit_loss,
                    "win_rate": win_rate,
                    "avg_trade_duration": avg_duration,
                    "total_return": total_return,
                    "total_invested": total_invested
                }
                
                return {"success": True, "performance": performance}
                
        except Exception as e:
            logger.error(f"Performance kuzatishda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    def calculate_signal_accuracy(self, signal_id: str) -> Dict[str, Any]:
        """Signal aniqligini hisoblash"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Signal ma'lumotlarini olish
                cursor.execute("""
                    SELECT signal_type, price, stop_loss, take_profit, created_at
                    FROM trading_signals WHERE signal_id = ?
                """, (signal_id,))
                
                signal_data = cursor.fetchone()
                if not signal_data:
                    return {"success": False, "message": "Signal topilmadi"}
                
                signal_type, entry_price, stop_loss, take_profit, created_at = signal_data
                
                # Bu signalga tegishli copy trade larni olish
                cursor.execute("""
                    SELECT profit_loss, amount FROM copy_trades WHERE signal_id = ?
                """, (signal_id,))
                
                copy_trades = cursor.fetchall()
                
                if not copy_trades:
                    return {"success": True, "accuracy": None, "message": "Copy trade topilmadi"}
                
                # Aniqligi hisoblash (profitable trades / total trades)
                profitable_trades = len([ct for ct in copy_trades if ct[0] > 0])
                total_trades = len(copy_trades)
                accuracy = (profitable_trades / total_trades) * 100 if total_trades > 0 else 0
                
                # Signal natijasini yangilash
                cursor.execute("""
                    UPDATE trading_signals SET accuracy = ? WHERE signal_id = ?
                """, (accuracy, signal_id))
                
                conn.commit()
                
                return {"success": True, "accuracy": accuracy, "total_trades": total_trades}
                
        except Exception as e:
            logger.error(f"Aniqlish hisoblashda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    # ==================== LEADERBOARD ====================
    
    def get_top_performers(self, period: str = "month", limit: int = 10) -> Dict[str, Any]:
        """Eng yaxshi ijrochilar reytingi"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Vaqt oralig'i belgilash
                now = datetime.datetime.now()
                if period == "week":
                    start_date = now - datetime.timedelta(weeks=1)
                elif period == "month":
                    start_date = now - datetime.timedelta(days=30)
                elif period == "quarter":
                    start_date = now - datetime.timedelta(days=90)
                else:
                    start_date = now - datetime.timedelta(days=365)
                
                # Top performer larni olish
                cursor.execute("""
                    SELECT tp.trader_id, u.username, u.avatar_url, tp.rating, tp.win_rate,
                           tp.profit_loss, tp.followers_count, tp.total_trades, tp.verified
                    FROM trader_profiles tp
                    JOIN users u ON tp.trader_id = u.user_id
                    WHERE tp.total_trades > 0 AND tp.verified = 1
                    ORDER BY tp.rating DESC, tp.win_rate DESC
                    LIMIT ?
                """, (limit,))
                
                results = cursor.fetchall()
                
                performers = []
                for i, row in enumerate(results, 1):
                    performer = {
                        "rank": i,
                        "trader_id": row[0],
                        "username": row[1],
                        "avatar_url": row[2],
                        "rating": row[3],
                        "win_rate": row[4],
                        "profit_loss": row[5],
                        "followers_count": row[6],
                        "total_trades": row[7],
                        "verified": bool(row[8])
                    }
                    performers.append(performer)
                
                return {"success": True, "performers": performers, "period": period}
                
        except Exception as e:
            logger.error(f"Top performers olishda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    # ==================== RATING SYSTEM ====================
    
    def rate_trader(self, user_id: str, trader_id: str, rating: float, comment: str = "") -> Dict[str, Any]:
        """Treyderga reyting berish"""
        try:
            if rating < 1.0 or rating > 5.0:
                return {"success": False, "message": "Reyting 1-5 oralig'ida bo'lishi kerak"}
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Treyder mavjudligini tekshirish
                cursor.execute("SELECT verification_status FROM users WHERE user_id = ?", (trader_id,))
                trader_data = cursor.fetchone()
                if not trader_data or trader_data[0] != "verified":
                    return {"success": False, "message": "Treyder topilmadi yoki tasdiqlanmagan"}
                
                # Izoh qo'shish (ixtiyoriy)
                if comment:
                    comment_id = str(uuid.uuid4())
                    now = datetime.datetime.now()
                    
                    comment_obj = Comment(
                        comment_id=comment_id,
                        user_id=user_id,
                        content=comment,
                        created_at=now
                    )
                    
                    cursor.execute("""
                        INSERT INTO comments (comment_id, user_id, content, created_at)
                        VALUES (?, ?, ?, ?)
                    """, (comment_obj.comment_id, comment_obj.user_id, comment_obj.content,
                          comment_obj.created_at))
                
                # Reytingni yangilash (bu soddalashtirilgan - real implementatsiyada o'rtacha hisoblanadi)
                cursor.execute("""
                    UPDATE trader_profiles 
                    SET rating = (rating + ?) / 2 
                    WHERE trader_id = ?
                """, (rating, trader_id))
                
                conn.commit()
                
                # Bildirishnoma
                self._send_notification(
                    trader_id,
                    "Yangi reyting",
                    f"Sizga {rating} yulduz reyting berildi!",
                    "new_rating"
                )
                
                return {"success": True, "message": "Reyting muvaffaqiyatli qo'shildi"}
                
        except Exception as e:
            logger.error(f"Reyting berishda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    # ==================== COMMISSION MANAGEMENT ====================
    
    def calculate_commission(self, trader_id: str, profit_loss: float, commission_rate: float = 0.05) -> float:
        """Komissiya hisoblash"""
        if profit_loss > 0:
            return profit_loss * commission_rate
        return 0.0

    def distribute_commission(self, copy_trade_id: str, profit_loss: float) -> Dict[str, Any]:
        """Komissiya taqsimoti"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Copy trade ma'lumotlarini olish
                cursor.execute("""
                    SELECT trader_id, follower_id, amount FROM copy_trades 
                    WHERE copy_trade_id = ?
                """, (copy_trade_id,))
                
                trade_data = cursor.fetchone()
                if not trade_data:
                    return {"success": False, "message": "Copy trade topilmadi"}
                
                trader_id, follower_id, amount = trade_data
                
                # Komissiya hisoblash
                commission = self.calculate_commission(trader_id, profit_loss)
                if commission > 0:
                    # Treyder balansini oshirish
                    cursor.execute("""
                        UPDATE users SET total_balance = total_balance + ? 
                        WHERE user_id = ?
                    """, (commission, trader_id))
                    
                    # Trader profil komissiya summa va amallarini yangilash
                    cursor.execute("""
                        UPDATE trader_profiles 
                        SET total_commission_earned = total_commission_earned + ?,
                            total_trades = total_trades + 1,
                            profit_loss = profit_loss + ?
                        WHERE trader_id = ?
                    """, (commission, profit_loss, trader_id))
                    
                    # Copy trade komissiyani yangilash
                    cursor.execute("""
                        UPDATE copy_trades 
                        SET commission_paid = ? 
                        WHERE copy_trade_id = ?
                    """, (commission, copy_trade_id))
                    
                    conn.commit()
                    
                    # Bildirishnoma
                    self._send_notification(
                        trader_id,
                        "Komissiya to'lovi",
                        f"Sizning hisobingizga ${commission:.2f} komissiya tushdi!",
                        "commission"
                    )
                    
                    return {"success": True, "commission": commission}
                
                return {"success": True, "commission": 0.0}
                
        except Exception as e:
            logger.error(f"Komissiya taqsimotida xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    # ==================== SOCIAL FEATURES ====================
    
    def follow_trader(self, follower_id: str, trader_id: str, copy_percentage: float = 100.0) -> Dict[str, Any]:
        """Treyderga obuna bo'lish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Mavjudligini tekshirish
                cursor.execute("""
                    SELECT copy_percentage FROM followers 
                    WHERE follower_id = ? AND trader_id = ?
                """, (follower_id, trader_id))
                
                existing = cursor.fetchone()
                now = datetime.datetime.now()
                
                if existing:
                    cursor.execute("""
                        UPDATE followers SET copy_percentage = ? 
                        WHERE follower_id = ? AND trader_id = ?
                    """, (copy_percentage, follower_id, trader_id))
                else:
                    cursor.execute("""
                        INSERT INTO followers (follower_id, trader_id, followed_at, copy_percentage)
                        VALUES (?, ?, ?, ?)
                    """, (follower_id, trader_id, now, copy_percentage))
                
                conn.commit()
                
                # Treyder statistikalarini yangilash
                self._update_trader_stats(trader_id, "new_follower")
                
                return {"success": True, "message": "Muvaffaqiyatli obuna bo'ldingiz"}
                
        except Exception as e:
            logger.error(f"Obuna bo'lishda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    def unfollow_trader(self, follower_id: str, trader_id: str) -> Dict[str, Any]:
        """Obunani bekor qilish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM followers 
                    WHERE follower_id = ? AND trader_id = ?
                """, (follower_id, trader_id))
                
                conn.commit()
                
                # Treyder statistikalarini yangilash
                self._update_trader_stats(trader_id, "unfollow")
                
                return {"success": True, "message": "Obuna bekor qilindi"}
                
        except Exception as e:
            logger.error(f"Obuna bekor qilishda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    def like_entity(self, user_id: str, entity_id: str, entity_type: str) -> Dict[str, Any]:
        """Like qilish (signal, comment, etc.)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Like mavjudligini tekshirish
                cursor.execute("""
                    SELECT 1 FROM likes WHERE user_id = ? AND entity_id = ? AND entity_type = ?
                """, (user_id, entity_id, entity_type))
                
                if cursor.fetchone():
                    # Unlike
                    cursor.execute("""
                        DELETE FROM likes WHERE user_id = ? AND entity_id = ? AND entity_type = ?
                    """, (user_id, entity_id, entity_type))
                    liked = False
                else:
                    # Like
                    now = datetime.datetime.now()
                    cursor.execute("""
                        INSERT INTO likes (user_id, entity_id, entity_type, liked_at)
                        VALUES (?, ?, ?, ?)
                    """, (user_id, entity_id, entity_type, now))
                    liked = True
                
                conn.commit()
                
                # Like sonini yangilash
                cursor.execute("""
                    SELECT COUNT(*) FROM likes WHERE entity_id = ? AND entity_type = ?
                """, (entity_id, entity_type))
                
                likes_count = cursor.fetchone()[0]
                
                # Comment bo'lsa, likes_count ni yangilash
                if entity_type == "comment":
                    cursor.execute("""
                        UPDATE comments SET likes_count = ? WHERE comment_id = ?
                    """, (likes_count, entity_id))
                    conn.commit()
                
                return {"success": True, "liked": liked, "likes_count": likes_count}
                
        except Exception as e:
            logger.error(f"Like qilishda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    # ==================== VERIFICATION SYSTEM ====================
    
    def request_verification(self, user_id: str, documents: List[str]) -> Dict[str, Any]:
        """Tasdiqlash so'rovi"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Hujjatlar ro'yxatini yangilash
                cursor.execute("""
                    UPDATE users SET verification_documents = ? 
                    WHERE user_id = ?
                """, (json.dumps(documents), user_id))
                
                # Tasdiqlash holatini "pending" ga o'zgartirish
                cursor.execute("""
                    UPDATE users SET verification_status = ? WHERE user_id = ?
                """, (VerificationStatus.PENDING.value, user_id))
                
                conn.commit()
                
                # Admin xabar
                self._send_notification(
                    user_id,
                    "Tasdiqlash so'rovi",
                    "Tasdiqlash so'rovingiz yuborildi. Tasdiqlash jarayoni 24-48 soat davom etadi.",
                    "verification_requested"
                )
                
                return {"success": True, "message": "Tasdiqlash so'rovingiz yuborildi"}
                
        except Exception as e:
            logger.error(f"Tasdiqlash so'rovida xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    def verify_trader(self, admin_id: str, user_id: str, approved: bool, reason: str = "") -> Dict[str, Any]:
        """Admin tomonidan treyder tasdiqlash"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Admin huquqlarini tekshirish (bu soddalashtirilgan)
                cursor.execute("SELECT role FROM users WHERE user_id = ?", (admin_id,))
                admin_data = cursor.fetchone()
                if not admin_data or admin_data[0] != UserRole.ADMIN.value:
                    return {"success": False, "message": "Bu amalni bajarish huquqingiz yo'q"}
                
                # Tasdiqlash holatini yangilash
                status = VerificationStatus.VERIFIED.value if approved else VerificationStatus.REJECTED.value
                cursor.execute("""
                    UPDATE users SET verification_status = ? WHERE user_id = ?
                """, (status, user_id))
                
                conn.commit()
                
                # Bildirishnoma
                message = "Tasdiqlashingiz tasdiqlandi!" if approved else f"Tasdiqlashingiz rad etildi: {reason}"
                self._send_notification(
                    user_id,
                    "Tasdiqlash natijasi",
                    message,
                    "verification_result"
                )
                
                return {"success": True, "message": "Tasdiqlash jarayoni yakunlandi"}
                
        except Exception as e:
            logger.error(f"Treyder tasdiqlashda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    # ==================== NOTIFICATIONS ====================
    
    def _send_notification(self, user_id: str, title: str, message: str, notification_type: str, action_url: str = None):
        """Bildirishnoma yuborish"""
        try:
            notification_id = str(uuid.uuid4())
            now = datetime.datetime.now()
            
            notification = Notification(
                notification_id=notification_id,
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                created_at=now,
                action_url=action_url
            )
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO notifications (notification_id, user_id, title, message, 
                                             notification_type, created_at, read, action_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (notification.notification_id, notification.user_id, notification.title,
                      notification.message, notification.notification_type, notification.created_at,
                      notification.read, notification.action_url))
                conn.commit()
            
            # Memory cache ga ham qo'shish
            self.user_notifications[user_id].append(notification)
            
        except Exception as e:
            logger.error(f"Bildirishnoma yuborishda xatolik: {str(e)}")

    def get_notifications(self, user_id: str, unread_only: bool = False) -> Dict[str, Any]:
        """Bildirishnomalarni olish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM notifications WHERE user_id = ?"
                params = [user_id]
                
                if unread_only:
                    query += " AND read = 0"
                
                query += " ORDER BY created_at DESC LIMIT 50"
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                notifications = []
                for row in results:
                    notification = {
                        "notification_id": row[0],
                        "user_id": row[1],
                        "title": row[2],
                        "message": row[3],
                        "notification_type": row[4],
                        "created_at": row[5],
                        "read": bool(row[6]),
                        "action_url": row[7]
                    }
                    notifications.append(notification)
                
                return {"success": True, "notifications": notifications}
                
        except Exception as e:
            logger.error(f"Bildirishnomalar olishda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    # ==================== UTILITY METHODS ====================
    
    def _notify_signal_to_followers(self, trader_id: str, signal: TradingSignal):
        """Obunachilarga signal haqida bildirishnoma"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT follower_id FROM followers WHERE trader_id = ?
                """, (trader_id,))
                
                followers = cursor.fetchall()
                
                for (follower_id,) in followers:
                    self._send_notification(
                        follower_id,
                        "Yangi Signal",
                        f"{signal.symbol} uchun yangi {signal.signal_type.value} signal!",
                        "new_signal",
                        f"/signal/{signal.signal_id}"
                    )
                    
        except Exception as e:
            logger.error(f"Obunachilarga bildirishnoma yuborishda xatolik: {str(e)}")

    def _update_trader_stats(self, trader_id: str, action: str):
        """Treyder statistikalarini yangilash"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if action == "new_follower":
                    cursor.execute("""
                        UPDATE trader_profiles SET followers_count = followers_count + 1 
                        WHERE trader_id = ?
                    """, (trader_id,))
                elif action == "unfollow":
                    cursor.execute("""
                        UPDATE trader_profiles SET followers_count = followers_count - 1 
                        WHERE trader_id = ?
                    """, (trader_id,))
                elif action == "signal_created":
                    cursor.execute("""
                        UPDATE trader_profiles SET total_trades = total_trades + 1 
                        WHERE trader_id = ?
                    """, (trader_id,))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Treyder statistikalarini yangilashda xatolik: {str(e)}")

    def _get_user_balance(self, user_id: str) -> float:
        """Foydalanuvchi balansini olish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT total_balance FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0.0

    def _update_user_balance(self, user_id: str, amount: float):
        """Foydalanuvchi balansini yangilash"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET total_balance = total_balance + ? WHERE user_id = ?
            """, (amount, user_id))
            conn.commit()

    def get_trader_profile(self, trader_id: str) -> Dict[str, Any]:
        """Treyder profilini olish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM trader_profiles WHERE trader_id = ?
                """, (trader_id,))
                
                result = cursor.fetchone()
                if not result:
                    return {"success": False, "message": "Treyder profili topilmadi"}
                
                profile_dict = {
                    "trader_id": result[0],
                    "followers_count": result[1],
                    "following_count": result[2],
                    "total_trades": result[3],
                    "winning_trades": result[4],
                    "losing_trades": result[5],
                    "win_rate": result[6],
                    "profit_loss": result[7],
                    "sharpe_ratio": result[8],
                    "max_drawdown": result[9],
                    "avg_trade_duration": result[10],
                    "total_commission_earned": result[11],
                    "rating": result[12],
                    "verified": bool(result[13]),
                    "specialty_assets": json.loads(result[14]) if result[14] else [],
                    "risk_level": result[15],
                    "performance_history": json.loads(result[16]) if result[16] else []
                }
                
                return {"success": True, "profile": profile_dict}
                
        except Exception as e:
            logger.error(f"Treyder profili olishda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

    def _start_background_tasks(self):
        """Fondoviy vazifalarni boshlash"""
        def update_prices():
            """Real vaqt narxlarni yangilash"""
            while True:
                try:
                    with self.lock:
                        for copy_trade_id, copy_trade in self.active_copy_trades.items():
                            # Bu yerda real narx API si chaqiriladi
                            # Hozircha tasodifiy narx o'zgarishi
                            current_price = copy_trade.current_price * (1 + random.uniform(-0.02, 0.02))
                            copy_trade.current_price = current_price
                            copy_trade.profit_loss = (current_price - copy_trade.execution_price) * (copy_trade.amount / copy_trade.execution_price)
                    
                    time.sleep(5)  # 5 soniyada bir yangilash
                    
                except Exception as e:
                    logger.error(f"Narx yangilashda xatolik: {str(e)}")
                    time.sleep(10)
        
        # Fon procesosni ishga tushirish
        price_thread = threading.Thread(target=update_prices, daemon=True)
        price_thread.start()
    
    def get_platform_stats(self) -> Dict[str, Any]:
        """Platform statistikalari"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Umumiy statistikalar
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
                total_users = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'trader' AND verification_status = 'verified'")
                verified_traders = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM trading_signals")
                total_signals = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM copy_trades")
                total_copy_trades = cursor.fetchone()[0]
                
                # Jami daromad
                cursor.execute("SELECT SUM(total_balance) FROM users")
                total_volume = cursor.fetchone()[0] or 0.0
                
                return {
                    "success": True,
                    "stats": {
                        "total_users": total_users,
                        "verified_traders": verified_traders,
                        "total_signals": total_signals,
                        "total_copy_trades": total_copy_trades,
                        "total_volume": total_volume,
                        "active_copy_trades": len(self.active_copy_trades)
                    }
                }
                
        except Exception as e:
            logger.error(f"Platform statistikalari olishda xatolik: {str(e)}")
            return {"success": False, "message": f"Xatolik yuz berdi: {str(e)}"}

# ==================== TEST VA NAMUNA FUNKSIYALAR ====================

def demo_social_trading():
    """Social Trading Platform demo"""
    print("🚀 Social Trading Platform Demo")
    print("=" * 50)
    
    # Platformani yaratish
    platform = SocialTradingPlatform()
    
    # Foydalanuvchilarni ro'yxatdan o'tkazish
    print("\n1. Foydalanuvchilarni ro'yxatdan o'tkazish...")
    
    # Treyder
    trader_result = platform.register_user("ali_trader", "ali@example.com", "secure123", UserRole.TRADER)
    trader_id = trader_result["user_id"]
    print(f"Treyder yaratildi: {trader_result['message']}")
    
    # Obunachi
    follower_result = platform.register_user("bob_investor", "bob@example.com", "secure123", UserRole.FOLLOWER)
    follower_id = follower_result["user_id"]
    print(f"Obunachi yaratildi: {follower_result['message']}")
    
    # Tasdiqlash so'rovi
    print("\n2. Treyder tasdiqlash so'rovi...")
    verification_result = platform.request_verification(trader_id, ["id_document.pdf", "proof_of_income.pdf"])
    print(f"Tasdiqlash: {verification_result['message']}")
    
    # Admin tasdiqlashi (demo)
    admin_result = platform.register_user("admin", "admin@example.com", "admin123", UserRole.ADMIN)
    admin_id = admin_result["user_id"]
    
    verification_approve = platform.verify_trader(admin_id, trader_id, True, "Hujjatlar to'g'ri")
    print(f"Tasdiqlash natijasi: {verification_approve['message']}")
    
    # Signal yaratish
    print("\n3. Trading signal yaratish...")
    signal_result = platform.create_signal(
        trader_id=trader_id,
        symbol="EURUSD",
        signal_type=SignalType.BUY,
        price=1.0950,
        stop_loss=1.0900,
        take_profit=1.1000,
        confidence=0.85,
        description="EUR/USD strong bullish signal"
    )
    print(f"Signal: {signal_result['message']}")
    
    # Copy trading boshlash
    print("\n4. Copy trading boshlash...")
    copy_result = platform.start_copy_trading(follower_id, trader_id, 1000.0)
    print(f"Copy trading: {copy_result['message']}")
    
    # Obuna bo'lish
    print("\n5. Treyderga obuna bo'lish...")
    follow_result = platform.follow_trader(follower_id, trader_id, 100.0)
    print(f"Obuna: {follow_result['message']}")
    
    # Signal bajarish
    print("\n6. Copy trade bajarish...")
    signal_id = signal_result["signal_id"]
    execute_result = platform.execute_copy_trade(signal_id, follower_id, 500.0)
    print(f"Copy trade: {execute_result['message']}")
    
    # Reyting berish
    print("\n7. Treyderga reyting berish...")
    rating_result = platform.rate_trader(follower_id, trader_id, 4.5, "Juda yaxshi treyder!")
    print(f"Reyting: {rating_result['message']}")
    
    # Leaderboard
    print("\n8. Top performers...")
    leaderboard = platform.get_top_performers(limit=5)
    if leaderboard["success"]:
        for performer in leaderboard["performers"]:
            print(f"#{performer['rank']}: {performer['username']} - Rating: {performer['rating']:.1f}")
    
    # Performance kuzatish
    print("\n9. Performance kuzatish...")
    performance = platform.track_performance(follower_id)
    if performance["success"]:
        perf = performance["performance"]
        print(f"Jami trade: {perf['total_trades']}")
        print(f"Win rate: {perf['win_rate']:.1f}%")
        print(f"Jami P&L: ${perf['total_profit_loss']:.2f}")
    
    # Bildirishnomalar
    print("\n10. Bildirishnomalar...")
    notifications = platform.get_notifications(follower_id)
    if notifications["success"]:
        for notif in notifications["notifications"][:3]:
            print(f"- {notif['title']}: {notif['message']}")
    
    # Platform statistikalari
    print("\n11. Platform statistikalari...")
    stats = platform.get_platform_stats()
    if stats["success"]:
        platform_stats = stats["stats"]
        print(f"Jami foydalanuvchilar: {platform_stats['total_users']}")
        print(f"Tasdiqlangan treyderlar: {platform_stats['verified_traders']}")
        print(f"Signallar soni: {platform_stats['total_signals']}")
        print(f"Aktiv copy trade: {platform_stats['active_copy_trades']}")
    
    print("\n✅ Demo muvaffaqiyatli tugallandi!")
    return platform

if __name__ == "__main__":
    # Demo ishga tushirish
    platform = demo_social_trading()