"""
AI Trading System - Authentication Handler
JWT token authentication va foydalanuvchi autentifikatsiyasi
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
import uuid
import secrets

from ..models.schemas import User, UserCreate, UserUpdate
from ..config.settings import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)

# HTTP Bearer scheme
security = HTTPBearer()

# In-memory user storage (in production, use database)
users_db: Dict[str, User] = {}
api_keys_db: Dict[str, Dict[str, Any]] = {}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Parolni tekshirish"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Parolni hash qilish"""
    return pwd_context.hash(password)

def create_api_key() -> str:
    """Yangi API kalit yaratish"""
    return secrets.token_urlsafe(32)

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Foydalanuvchini autentifikatsiya qilish"""
    # In production, query from database
    if username in users_db:
        user = users_db[username]
        if verify_password(password, user.password):
            return user
    return None

def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """Access token yaratish"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Refresh token yaratish"""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    
    return jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Tokenni tekshirish va dekodlash"""
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None

def generate_api_key(user_id: str, permissions: list = None) -> str:
    """API kalit yaratish"""
    api_key = create_api_key()
    
    api_keys_db[api_key] = {
        "user_id": user_id,
        "permissions": permissions or ["read"],
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=365),
        "is_active": True
    }
    
    return api_key

def verify_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """API kalitni tekshirish"""
    if api_key in api_keys_db:
        key_data = api_keys_db[api_key]
        if key_data["is_active"] and key_data["expires_at"] > datetime.utcnow():
            return key_data
    return None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Joriy foydalanuvchini olish"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Tokenni tasdiqlab bo'lmadi",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # Get user from database (simplified)
    if username not in users_db:
        raise credentials_exception
    
    return users_db[username]

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Faol foydalanuvchini olish"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Foydalanuvchi faol emas")
    return current_user

async def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Admin foydalanuvchini olish"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin huquqlari kerak"
        )
    return current_user

# Initialize default users
def init_default_users():
    """Standart foydalanuvchilarni yaratish"""
    if not users_db:
        # Admin user
        admin_user = User(
            id=uuid.uuid4(),
            username="admin",
            email="admin@aitrading.com",
            role="admin",
            password=get_password_hash("admin123"),
            is_active=True,
            created_at=datetime.utcnow()
        )
        users_db["admin"] = admin_user
        
        # Trader user
        trader_user = User(
            id=uuid.uuid4(),
            username="trader",
            email="trader@aitrading.com",
            role="trader",
            password=get_password_hash("trader123"),
            is_active=True,
            created_at=datetime.utcnow()
        )
        users_db["trader"] = trader_user
        
        # Viewer user
        viewer_user = User(
            id=uuid.uuid4(),
            username="viewer",
            email="viewer@aitrading.com",
            role="viewer",
            password=get_password_hash("viewer123"),
            is_active=True,
            created_at=datetime.utcnow()
        )
        users_db["viewer"] = viewer_user

# Initialize on module load
init_default_users()

class AuthenticationError(Exception):
    """Autentifikatsiya xatosi"""
    pass

class AuthorizationError(Exception):
    """Autorizatsiya xatosi"""
    pass