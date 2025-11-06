#!/usr/bin/env python3
"""
Production User Onboarding System
Production muhit uchun foydalanuvchi onboarding va kurs tizimi
"""

import os
import json
import logging
import hashlib
import secrets
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import aiohttp
import psycopg2
from psycopg2.extras import RealDictCursor
import jwt
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import smtplib

# Import production configuration
from production_config import get_config


@dataclass
class User:
    """Foydalanuvchi ma'lumotlari"""
    id: Optional[int] = None
    email: str = ""
    password_hash: str = ""
    first_name: str = ""
    last_name: str = ""
    phone: Optional[str] = None
    country: str = ""
    language: str = "uz"
    timezone: str = "Asia/Samarkand"
    trading_experience: str = "beginner"  # beginner, intermediate, advanced
    risk_tolerance: str = "moderate"  # conservative, moderate, aggressive
    investment_budget: float = 0.0
    is_verified: bool = False
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    onboarding_completed: bool = False
    subscription_tier: str = "free"  # free, basic, premium, vip
    preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OnboardingStep:
    """Onboarding qadami"""
    id: int
    title: str
    description: str
    step_type: str  # form, video, quiz, demo, payment
    content: Dict[str, Any] = field(default_factory=dict)
    required: bool = True
    order: int = 0
    estimated_time: int = 0  # minutes


@dataclass
class CourseProgress:
    """Kurs progressi"""
    user_id: int
    course_id: int
    current_step: int = 0
    completed_steps: List[int] = field(default_factory=list)
    quiz_scores: Dict[int, float] = field(default_factory=dict)
    time_spent: int = 0  # minutes
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    certificate_earned: bool = False


@dataclass
class DemoAccount:
    """Demo hisob"""
    id: Optional[int] = None
    user_id: int
    account_type: str = "demo"
    initial_balance: float = 10000.0
    current_balance: float = 10000.0
    currency: str = "USD"
    leverage: int = 100
    is_active: bool = True
    trades_count: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    created_at: Optional[datetime] = None


class ProductionOnboardingSystem:
    """Production onboarding tizimi"""
    
    def __init__(self, environment: str = "production"):
        self.config = get_config(environment)
        self.environment = environment
        
        # Logging setup
        self.setup_logging()
        
        # Database setup
        self.setup_database()
        
        # JWT setup
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
        self.jwt_algorithm = "HS256"
        
        # Initialize courses and steps
        self.initialize_courses()
        
        self.logger.info("👥 Production User Onboarding tizimi ishga tushdi")
    
    def setup_logging(self):
        """Logging konfiguratsiyasi"""
        log_dir = Path("/workspace/orion-starline/logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "onboarding.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_database(self):
        """Ma'lumotlar bazasi jadvallarini yaratish"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    # Users table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            email VARCHAR(255) UNIQUE NOT NULL,
                            password_hash VARCHAR(255) NOT NULL,
                            first_name VARCHAR(100) NOT NULL,
                            last_name VARCHAR(100) NOT NULL,
                            phone VARCHAR(20),
                            country VARCHAR(50) NOT NULL,
                            language VARCHAR(10) DEFAULT 'uz',
                            timezone VARCHAR(50) DEFAULT 'Asia/Samarkand',
                            trading_experience VARCHAR(20) DEFAULT 'beginner',
                            risk_tolerance VARCHAR(20) DEFAULT 'moderate',
                            investment_budget DECIMAL(15,2) DEFAULT 0.0,
                            is_verified BOOLEAN DEFAULT FALSE,
                            is_active BOOLEAN DEFAULT TRUE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_login TIMESTAMP,
                            onboarding_completed BOOLEAN DEFAULT FALSE,
                            subscription_tier VARCHAR(20) DEFAULT 'free',
                            preferences JSONB DEFAULT '{}'
                        )
                    """)
                    
                    # User sessions
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS user_sessions (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            session_token VARCHAR(255) UNIQUE NOT NULL,
                            expires_at TIMESTAMP NOT NULL,
                            ip_address INET,
                            user_agent TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Courses
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS courses (
                            id SERIAL PRIMARY KEY,
                            title VARCHAR(255) NOT NULL,
                            description TEXT,
                            level VARCHAR(20) DEFAULT 'beginner',
                            estimated_hours INTEGER DEFAULT 0,
                            is_free BOOLEAN DEFAULT TRUE,
                            is_premium BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Onboarding steps
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS onboarding_steps (
                            id SERIAL PRIMARY KEY,
                            course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                            title VARCHAR(255) NOT NULL,
                            description TEXT,
                            step_type VARCHAR(50) NOT NULL,
                            content JSONB DEFAULT '{}',
                            required BOOLEAN DEFAULT TRUE,
                            step_order INTEGER NOT NULL,
                            estimated_time INTEGER DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Course progress
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS course_progress (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                            current_step INTEGER DEFAULT 0,
                            completed_steps INTEGER[] DEFAULT '{}',
                            quiz_scores JSONB DEFAULT '{}',
                            time_spent INTEGER DEFAULT 0,
                            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            completed_at TIMESTAMP,
                            certificate_earned BOOLEAN DEFAULT FALSE,
                            UNIQUE(user_id, course_id)
                        )
                    """)
                    
                    # Demo accounts
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS demo_accounts (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            account_type VARCHAR(50) DEFAULT 'demo',
                            initial_balance DECIMAL(15,2) DEFAULT 10000.0,
                            current_balance DECIMAL(15,2) DEFAULT 10000.0,
                            currency VARCHAR(10) DEFAULT 'USD',
                            leverage INTEGER DEFAULT 100,
                            is_active BOOLEAN DEFAULT TRUE,
                            trades_count INTEGER DEFAULT 0,
                            win_rate DECIMAL(5,2) DEFAULT 0.0,
                            total_pnl DECIMAL(15,2) DEFAULT 0.0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # User preferences
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS user_preferences (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            key VARCHAR(100) NOT NULL,
                            value JSONB NOT NULL,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(user_id, key)
                        )
                    """)
                    
                    # Email verification
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS email_verifications (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            email VARCHAR(255) NOT NULL,
                            verification_token VARCHAR(255) UNIQUE NOT NULL,
                            is_verified BOOLEAN DEFAULT FALSE,
                            expires_at TIMESTAMP NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    conn.commit()
                    self.logger.info("✅ Onboarding ma'lumotlar bazasi jadvallari yaratildi")
                    
        except Exception as e:
            self.logger.error(f"Ma'lumotlar bazasi setup xatosi: {e}")
            raise
    
    def initialize_courses(self):
        """Kurslarni va qadamlarini boshlash"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    # Insert default courses
                    courses = [
                        {
                            "title": "Trading Asoslari",
                            "description": "Trading ga kirish va asosiy tushunchalar",
                            "level": "beginner",
                            "estimated_hours": 2,
                            "is_free": True
                        },
                        {
                            "title": "Texnik Tahlil",
                            "description": "Grafiklar va texnik ko'rsatkichlar",
                            "level": "intermediate",
                            "estimated_hours": 4,
                            "is_free": True
                        },
                        {
                            "title": "Risk Boshqaruvi",
                            "description": "Moliyaviy risklarni boshqarish",
                            "level": "intermediate",
                            "estimated_hours": 3,
                            "is_premium": True
                        },
                        {
                            "title": "Algoritm Trading",
                            "description": "Avtomatik trading tizimlari",
                            "level": "advanced",
                            "estimated_hours": 6,
                            "is_premium": True
                        }
                    ]
                    
                    for course_data in courses:
                        cur.execute("""
                            INSERT INTO courses (title, description, level, estimated_hours, is_free, is_premium)
                            VALUES (%(title)s, %(description)s, %(level)s, %(estimated_hours)s, %(is_free)s, %(is_premium)s)
                            ON CONFLICT DO NOTHING
                        """, course_data)
                    
                    # Get course IDs for adding steps
                    cur.execute("SELECT id, title FROM courses")
                    course_map = {row[1]: row[0] for row in cur.fetchall()}
                    
                    # Add onboarding steps for Trading Asoslari course
                    basic_course_id = course_map.get("Trading Asoslari")
                    if basic_course_id:
                        steps = [
                            {
                                "title": "Ro'yxatdan o'tish",
                                "description": "Shaxsiy ma'lumotlaringizni kiriting",
                                "step_type": "form",
                                "content": {"fields": ["email", "first_name", "last_name", "country"]},
                                "step_order": 1,
                                "estimated_time": 3
                            },
                            {
                                "title": "Trading tajribasi",
                                "description": "Trading tajribangizni baholang",
                                "step_type": "quiz",
                                "content": {"questions": [
                                    {"question": "Trading tajribangiz qanday?", "options": ["Boshlanish", "O'rta", "Ilgari"]}
                                ]},
                                "step_order": 2,
                                "estimated_time": 2
                            },
                            {
                                "title": "Demo hisob yaratish",
                                "description": "Real pul ishlashdan oldin demo hisobda mashq qiling",
                                "step_type": "demo",
                                "content": {"initial_balance": 10000, "currency": "USD"},
                                "step_order": 3,
                                "estimated_time": 5
                            },
                            {
                                "title": "Video darslik",
                                "description": "Asosiy trading tushunchalarini o'rganing",
                                "step_type": "video",
                                "content": {"video_url": "https://cdn.orion-starline.com/videos/basics-intro.mp4"},
                                "step_order": 4,
                                "estimated_time": 15
                            },
                            {
                                "title": "Birinchi trade",
                                "description": "Demo hisobda birinchi tradingizni amalga oshiring",
                                "step_type": "demo",
                                "content": {"min_trade_amount": 100, "max_trade_amount": 1000},
                                "step_order": 5,
                                "estimated_time": 10
                            },
                            {
                                "title": "Real account upgrade",
                                "description": "Real pul bilan trading uchun hisobingizni yangilang",
                                "step_type": "payment",
                                "content": {"min_deposit": 100},
                                "step_order": 6,
                                "estimated_time": 5
                            }
                        ]
                        
                        for step_data in steps:
                            step_data["course_id"] = basic_course_id
                            cur.execute("""
                                INSERT INTO onboarding_steps 
                                (course_id, title, description, step_type, content, step_order, estimated_time)
                                VALUES (%(course_id)s, %(title)s, %(description)s, %(step_type)s, 
                                        %(content)s::jsonb, %(step_order)s, %(estimated_time)s)
                                ON CONFLICT DO NOTHING
                            """, step_data)
                    
                    conn.commit()
                    self.logger.info("✅ Kurslar va qadamlar boshladi")
                    
        except Exception as e:
            self.logger.error(f"Kurslarni boshlashda xato: {e}")
    
    def hash_password(self, password: str) -> str:
        """Parolni hash qilish"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}:{pwd_hash.hex()}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Parolni tekshirish"""
        try:
            salt, stored_hash = password_hash.split(':')
            pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return pwd_hash.hex() == stored_hash
        except Exception:
            return False
    
    def generate_session_token(self) -> str:
        """Session token yaratish"""
        return secrets.token_urlsafe(32)
    
    def create_user(self, user_data: Dict[str, Any]) -> Tuple[bool, str, Optional[int]]:
        """Yangi foydalanuvchi yaratish"""
        try:
            # Validate required fields
            required_fields = ["email", "password", "first_name", "last_name", "country"]
            missing_fields = [field for field in required_fields if field not in user_data]
            
            if missing_fields:
                return False, f"Kerakli maydonlar to'ldirilmagan: {missing_fields}", None
            
            # Check if email already exists
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM users WHERE email = %s", (user_data["email"],))
                    if cur.fetchone():
                        return False, "Bu email allaqachon ro'yxatdan o'tgan", None
                    
                    # Hash password
                    password_hash = self.hash_password(user_data["password"])
                    
                    # Create user
                    cur.execute("""
                        INSERT INTO users (email, password_hash, first_name, last_name, phone, country, 
                                         language, timezone, trading_experience, risk_tolerance, investment_budget)
                        VALUES (%(email)s, %(password_hash)s, %(first_name)s, %(last_name)s, %(phone)s, 
                                %(country)s, %(language)s, %(timezone)s, %(trading_experience)s, 
                                %(risk_tolerance)s, %(investment_budget)s)
                        RETURNING id
                    """, {
                        "email": user_data["email"],
                        "password_hash": password_hash,
                        "first_name": user_data["first_name"],
                        "last_name": user_data["last_name"],
                        "phone": user_data.get("phone"),
                        "country": user_data["country"],
                        "language": user_data.get("language", "uz"),
                        "timezone": user_data.get("timezone", "Asia/Samarkand"),
                        "trading_experience": user_data.get("trading_experience", "beginner"),
                        "risk_tolerance": user_data.get("risk_tolerance", "moderate"),
                        "investment_budget": user_data.get("investment_budget", 0.0)
                    })
                    
                    user_id = cur.fetchone()[0]
                    conn.commit()
                    
                    # Send verification email
                    self.send_verification_email(user_id, user_data["email"])
                    
                    # Create demo account
                    self.create_demo_account(user_id)
                    
                    self.logger.info(f"✅ Yangi foydalanuvchi yaratildi: {user_data['email']}")
                    return True, "Foydalanuvchi muvaffaqiyatli yaratildi", user_id
                    
        except Exception as e:
            self.logger.error(f"Foydalanuvchi yaratishda xato: {e}")
            return False, "Foydalanuvchi yaratishda xato yuz berdi", None
    
    def send_verification_email(self, user_id: int, email: str):
        """Tasdiqlash emaili yuborish"""
        try:
            verification_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=24)
            
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO email_verifications (user_id, email, verification_token, expires_at)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, email, verification_token, expires_at))
                    conn.commit()
            
            # Send email (simplified - would use actual SMTP)
            verification_link = f"https://app.orion-starline.com/verify-email?token={verification_token}"
            email_body = f"""
            Salom {email},
            
            Orion Starline hisobingizni tasdiqlash uqugishingiz kerak.
            
            Tasdiqlash uchun ushbu havolaga o'ting:
            {verification_link}
            
            Bu havol 24 soat davomida amal qiladi.
            
            Muvaffaqiyatli trading!
            Orion Starline Team
            """
            
            self.logger.info(f"📧 Verification email yuborildi: {email}")
            
        except Exception as e:
            self.logger.error(f"Verification email yuborishda xato: {e}")
    
    def verify_email(self, token: str) -> Tuple[bool, str]:
        """Email tasdiqlash"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT user_id, email FROM email_verifications 
                        WHERE verification_token = %s AND expires_at > NOW() AND is_verified = FALSE
                    """, (token,))
                    
                    result = cur.fetchone()
                    if not result:
                        return False, "Noto'g'ri yoki muddati o'tgan token"
                    
                    user_id, email = result
                    
                    # Mark as verified
                    cur.execute("""
                        UPDATE email_verifications SET is_verified = TRUE
                        WHERE verification_token = %s
                    """, (token,))
                    
                    # Update user
                    cur.execute("""
                        UPDATE users SET is_verified = TRUE WHERE id = %s
                    """, (user_id,))
                    
                    conn.commit()
                    
                    self.logger.info(f"✅ Email tasdiqlandi: {email}")
                    return True, "Email muvaffaqiyatli tasdiqlandi"
                    
        except Exception as e:
            self.logger.error(f"Email tasdiqlashda xato: {e}")
            return False, "Email tasdiqlashda xato yuz berdi"
    
    def create_demo_account(self, user_id: int) -> bool:
        """Demo hisob yaratish"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO demo_accounts (user_id, account_type, initial_balance, current_balance)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, "demo", 10000.0, 10000.0))
                    conn.commit()
                    
            self.logger.info(f"✅ Demo hisob yaratildi: user_id {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Demo hisob yaratishda xato: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Foydalanuvchi ma'lumotlarini olish"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT * FROM users WHERE id = %s AND is_active = TRUE", (user_id,))
                    row = cur.fetchone()
                    
                    if row:
                        return User(
                            id=row["id"],
                            email=row["email"],
                            password_hash=row["password_hash"],
                            first_name=row["first_name"],
                            last_name=row["last_name"],
                            phone=row["phone"],
                            country=row["country"],
                            language=row["language"],
                            timezone=row["timezone"],
                            trading_experience=row["trading_experience"],
                            risk_tolerance=row["risk_tolerance"],
                            investment_budget=float(row["investment_budget"]),
                            is_verified=row["is_verified"],
                            is_active=row["is_active"],
                            created_at=row["created_at"],
                            last_login=row["last_login"],
                            onboarding_completed=row["onboarding_completed"],
                            subscription_tier=row["subscription_tier"],
                            preferences=row["preferences"]
                        )
                    return None
                    
        except Exception as e:
            self.logger.error(f"Foydalanuvchi olishda xato: {e}")
            return None
    
    def authenticate_user(self, email: str, password: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """Foydalanuvchi autentifikatsiyasi"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, password_hash FROM users 
                        WHERE email = %s AND is_active = TRUE
                    """, (email,))
                    
                    result = cur.fetchone()
                    if not result:
                        return False, "Email yoki parol noto'g'ri", None
                    
                    user_id, password_hash = result
                    
                    if not self.verify_password(password, password_hash):
                        return False, "Email yoki parol noto'g'ri", None
                    
                    # Update last login
                    cur.execute("""
                        UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s
                    """, (user_id,))
                    conn.commit()
                    
                    return True, "Muvaffaqiyatli kirish", user_id
                    
        except Exception as e:
            self.logger.error(f"Autentifikatsiya xatosi: {e}")
            return False, "Autentifikatsiya xatosi", None
    
    def create_session(self, user_id: int, ip_address: str = "", user_agent: str = "") -> str:
        """Session yaratish"""
        session_token = self.generate_session_token()
        expires_at = datetime.now() + timedelta(hours=24)
        
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO user_sessions (user_id, session_token, expires_at, ip_address, user_agent)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (user_id, session_token, expires_at, ip_address, user_agent))
                    conn.commit()
                    
            return session_token
            
        except Exception as e:
            self.logger.error(f"Session yaratishda xato: {e}")
            raise
    
    def get_onboarding_steps(self, user_id: int) -> List[Dict[str, Any]]:
        """Onboarding qadamlarini olish"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get user's trading experience level
                    cur.execute("SELECT trading_experience FROM users WHERE id = %s", (user_id,))
                    user = cur.fetchone()
                    
                    if not user:
                        return []
                    
                    experience_level = user["trading_experience"]
                    
                    # Get course ID for beginner level
                    cur.execute("SELECT id FROM courses WHERE level = %s AND is_free = TRUE LIMIT 1", (experience_level,))
                    course = cur.fetchone()
                    
                    if not course:
                        return []
                    
                    course_id = course["id"]
                    
                    # Get onboarding steps
                    cur.execute("""
                        SELECT * FROM onboarding_steps 
                        WHERE course_id = %s 
                        ORDER BY step_order
                    """, (course_id,))
                    
                    steps = []
                    for row in cur.fetchall():
                        steps.append({
                            "id": row["id"],
                            "title": row["title"],
                            "description": row["description"],
                            "step_type": row["step_type"],
                            "content": row["content"],
                            "required": row["required"],
                            "order": row["step_order"],
                            "estimated_time": row["estimated_time"]
                        })
                    
                    return steps
                    
        except Exception as e:
            self.logger.error(f"Onboarding qadamlar olishda xato: {e}")
            return []
    
    def update_onboarding_step(self, user_id: int, step_id: int, step_data: Dict[str, Any]) -> bool:
        """Onboarding qadamini yangilash"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    # Get course ID for the step
                    cur.execute("SELECT course_id FROM onboarding_steps WHERE id = %s", (step_id,))
                    step = cur.fetchone()
                    
                    if not step:
                        return False
                    
                    course_id = step[0]
                    
                    # Get current progress or create new
                    cur.execute("""
                        SELECT id, current_step, completed_steps FROM course_progress 
                        WHERE user_id = %s AND course_id = %s
                    """, (user_id, course_id))
                    
                    progress = cur.fetchone()
                    
                    if progress:
                        progress_id, current_step, completed_steps = progress
                        
                        # Update progress
                        if "current_step" in step_data:
                            current_step = step_data["current_step"]
                        
                        if "completed" in step_data and step_data["completed"]:
                            if completed_steps is None:
                                completed_steps = []
                            completed_steps.append(step_id)
                            completed_steps = list(set(completed_steps))  # Remove duplicates
                        
                        # Check if onboarding is complete
                        onboarding_complete = len(completed_steps) >= 5  # Assuming 5 main steps
                        
                        cur.execute("""
                            UPDATE course_progress 
                            SET current_step = %s, completed_steps = %s, onboarding_completed = %s
                            WHERE id = %s
                        """, (current_step, completed_steps, onboarding_complete, progress_id))
                        
                    else:
                        # Create new progress
                        completed_steps = [step_id] if step_data.get("completed", False) else []
                        
                        cur.execute("""
                            INSERT INTO course_progress (user_id, course_id, current_step, completed_steps)
                            VALUES (%s, %s, %s, %s)
                        """, (user_id, course_id, step_data.get("current_step", 1), completed_steps))
                    
                    conn.commit()
                    
                    # Update user onboarding status if completed
                    if step_data.get("completed", False):
                        self.complete_onboarding(user_id)
                    
                    return True
                    
        except Exception as e:
            self.logger.error(f"Onboarding qadam yangilashda xato: {e}")
            return False
    
    def complete_onboarding(self, user_id: int):
        """Onboarding jarayonini tugallash"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE users SET onboarding_completed = TRUE WHERE id = %s
                    """, (user_id,))
                    conn.commit()
                    
            self.logger.info(f"✅ Onboarding tugallandi: user_id {user_id}")
            
        except Exception as e:
            self.logger.error(f"Onboarding tugallashda xato: {e}")
    
    def get_user_dashboard_data(self, user_id: int) -> Dict[str, Any]:
        """Foydalanuvchi dashboard ma'lumotlari"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # User info
                    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                    user_data = cur.fetchone()
                    
                    if not user_data:
                        return {}
                    
                    # Demo account info
                    cur.execute("SELECT * FROM demo_accounts WHERE user_id = %s AND is_active = TRUE", (user_id,))
                    demo_account = cur.fetchone()
                    
                    # Course progress
                    cur.execute("""
                        SELECT cp.*, c.title as course_title, c.level as course_level
                        FROM course_progress cp
                        JOIN courses c ON cp.course_id = c.id
                        WHERE cp.user_id = %s
                    """, (user_id,))
                    course_progress = cur.fetchall()
                    
                    # Recent activity (simplified)
                    recent_activity = []
                    
                    dashboard_data = {
                        "user": dict(user_data),
                        "demo_account": dict(demo_account) if demo_account else None,
                        "course_progress": [dict(progress) for progress in course_progress],
                        "recent_activity": recent_activity,
                        "onboarding_complete": user_data["onboarding_completed"],
                        "next_steps": self.get_next_onboarding_steps(user_id)
                    }
                    
                    return dashboard_data
                    
        except Exception as e:
            self.logger.error(f"Dashboard ma'lumotlar olishda xato: {e}")
            return {}
    
    def get_next_onboarding_steps(self, user_id: int) -> List[str]:
        """Keyingi onboarding qadamlar"""
        steps = []
        
        if not self.is_email_verified(user_id):
            steps.append("Email tasdiqlash")
        elif not self.has_demo_account(user_id):
            steps.append("Demo hisob yaratish")
        elif not self.is_onboarding_complete(user_id):
            steps.append("Onboarding tugallash")
        
        return steps
    
    def is_email_verified(self, user_id: int) -> bool:
        """Email tasdiqlanganligini tekshirish"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT is_verified FROM users WHERE id = %s", (user_id,))
                    result = cur.fetchone()
                    return result[0] if result else False
        except Exception:
            return False
    
    def has_demo_account(self, user_id: int) -> bool:
        """Demo hisob mavjudligini tekshirish"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM demo_accounts WHERE user_id = %s AND is_active = TRUE", (user_id,))
                    return cur.fetchone() is not None
        except Exception:
            return False
    
    def is_onboarding_complete(self, user_id: int) -> bool:
        """Onboarding tugallanganligini tekshirish"""
        try:
            with psycopg2.connect(self.config.get_database_url()) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT onboarding_completed FROM users WHERE id = %s", (user_id,))
                    result = cur.fetchone()
                    return result[0] if result else False
        except Exception:
            return False


def main():
    """Asosiy funksiya"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production User Onboarding System")
    parser.add_argument("--environment", "-e", default="production",
                       choices=["development", "staging", "production"],
                       help="Onboarding environment")
    parser.add_argument("--action", "-a", default="initialize",
                       choices=["initialize", "test-user", "test-onboarding"],
                       help="Action to perform")
    
    args = parser.parse_args()
    
    # Environment validatsiyasi
    if not validate_environment():
        print("❌ Environment validatsiyasi muvaffaqiyatsiz!")
        sys.exit(1)
    
    onboarding_system = ProductionOnboardingSystem(args.environment)
    
    if args.action == "initialize":
        print("✅ Onboarding tizimi tayyor!")
    elif args.action == "test-user":
        # Test user creation
        test_user_data = {
            "email": "test@orion-starline.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "country": "Uzbekistan",
            "trading_experience": "beginner"
        }
        
        success, message, user_id = onboarding_system.create_user(test_user_data)
        if success:
            print(f"✅ Test user yaratildi: {user_id}")
        else:
            print(f"❌ Test user yaratishda xato: {message}")
    
    print("👥 User Onboarding tizimi ishga tushdi!")


if __name__ == "__main__":
    main()