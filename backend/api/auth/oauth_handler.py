"""
AI Trading System - OAuth Handler
OAuth 2.0 integratsiya va tashqi autentifikatsiya xizmatlari
"""

from fastapi import HTTPException, Depends, status, Request
from fastapi.security import OAuth2, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import httpx
import secrets
import json
from datetime import datetime, timedelta

from ..config.settings import settings
from ..models.schemas import User
from .auth_handler import verify_token, verify_api_key, users_db

# OAuth2 scheme for password flow
oauth2_scheme = OAuth2(
    flows={
        "password": {
            "tokenUrl": "/api/v1/auth/login",
            "scopes": {
                "read": "Read access",
                "write": "Write access",
                "admin": "Admin access"
            }
        },
        "clientCredentials": {
            "tokenUrl": "/api/v1/auth/token",
            "scopes": {
                "api": "API access"
            }
        },
        "authorizationCode": {
            "authorizationUrl": "/api/v1/auth/authorize",
            "tokenUrl": "/api/v1/auth/token",
            "scopes": {
                "profile": "User profile access",
                "email": "Email access"
            }
        }
    }
)

# Session storage for OAuth flows
oauth_sessions: Dict[str, Dict[str, Any]] = {}
oauth_consents: Dict[str, List[str]] = {}

class OAuthUser(BaseModel):
    """OAuth foydalanuvchi ma'lumotlari"""
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    provider: str
    provider_id: str
    verified: bool = False
    created_at: datetime = datetime.utcnow()

class OAuthToken(BaseModel):
    """OAuth token ma'lumotlari"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: str
    created_at: datetime = datetime.utcnow()

class OAuthProviderConfig(BaseModel):
    """OAuth provider konfiguratsiyasi"""
    client_id: str
    client_secret: str
    auth_url: str
    token_url: str
    user_info_url: str
    scopes: List[str]
    redirect_uri: str

# Provider configurations
PROVIDERS = {
    "google": OAuthProviderConfig(
        client_id=settings.GOOGLE_CLIENT_ID or "",
        client_secret=settings.GOOGLE_CLIENT_SECRET or "",
        auth_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        user_info_url="https://www.googleapis.com/oauth2/v2/userinfo",
        scopes=["openid", "email", "profile"],
        redirect_uri=f"{settings.BASE_URL}/api/v1/auth/oauth/google/callback"
    ),
    "github": OAuthProviderConfig(
        client_id=settings.GITHUB_CLIENT_ID or "",
        client_secret=settings.GITHUB_CLIENT_SECRET or "",
        auth_url="https://github.com/login/oauth/authorize",
        token_url="https://github.com/login/oauth/access_token",
        user_info_url="https://api.github.com/user",
        scopes=["user:email"],
        redirect_uri=f"{settings.BASE_URL}/api/v1/auth/oauth/github/callback"
    ),
    "linkedin": OAuthProviderConfig(
        client_id=settings.LINKEDIN_CLIENT_ID or "",
        client_secret=settings.LINKEDIN_CLIENT_SECRET or "",
        auth_url="https://www.linkedin.com/oauth/v2/authorization",
        token_url="https://www.linkedin.com/oauth/v2/accessToken",
        user_info_url="https://api.linkedin.com/v2/me",
        scopes=["r_liteprofile", "r_emailaddress"],
        redirect_uri=f"{settings.BASE_URL}/api/v1/auth/oauth/linkedin/callback"
    )
}

def generate_oauth_state() -> str:
    """OAuth state parameterni yaratish"""
    return secrets.token_urlsafe(32)

def generate_pkce_challenge() -> tuple[str, str]:
    """PKCE challenge va verifier yaratish"""
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = secrets.token_urlsafe(32)  # Simplified
    return code_verifier, code_challenge

async def get_oauth_authorization_url(provider: str, state: str, redirect_uri: str) -> str:
    """OAuth authorization URL yaratish"""
    if provider not in PROVIDERS:
        raise ValueError(f"Qo'llab-quvvatlanmaydigan provider: {provider}")
    
    config = PROVIDERS[provider]
    
    params = {
        "client_id": config.client_id,
        "redirect_uri": redirect_uri or config.redirect_uri,
        "response_type": "code",
        "scope": " ".join(config.scopes),
        "state": state
    }
    
    return f"{config.auth_url}?{httpx.URL(params=params).query}"

async def exchange_code_for_token(provider: str, code: str, redirect_uri: str) -> Dict[str, Any]:
    """Kodni token bilan almashish"""
    if provider not in PROVIDERS:
        raise ValueError(f"Qo'llab-quvvatlanmaydigan provider: {provider}")
    
    config = PROVIDERS[provider]
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    if provider == "github":
        headers["Accept"] = "application/json"
    
    data = {
        "client_id": config.client_id,
        "client_secret": config.client_secret,
        "code": code,
        "redirect_uri": redirect_uri or config.redirect_uri,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(config.token_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

async def get_user_info(provider: str, access_token: str) -> Dict[str, Any]:
    """Foydalanuvchi ma'lumotlarini olish"""
    if provider not in PROVIDERS:
        raise ValueError(f"Qo'llab-quvvatlanmaydigan provider: {provider}")
    
    config = PROVIDERS[provider]
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(config.user_info_url, headers=headers)
        response.raise_for_status()
        return response.json()

def normalize_oauth_user_info(provider: str, user_info: Dict[str, Any]) -> OAuthUser:
    """OAuth ma'lumotlarini normalizatsiya qilish"""
    if provider == "google":
        return OAuthUser(
            id=user_info.get("id"),
            email=user_info.get("email"),
            name=user_info.get("name"),
            picture=user_info.get("picture"),
            provider=provider,
            provider_id=user_info.get("id"),
            verified=user_info.get("verified_email", False)
        )
    elif provider == "github":
        emails = user_info.get("emails", [])
        primary_email = None
        verified_email = False
        
        for email in emails:
            if email.get("primary"):
                primary_email = email.get("email")
                verified_email = email.get("verified", False)
                break
        
        return OAuthUser(
            id=str(user_info.get("id")),
            email=primary_email or "",
            name=user_info.get("name") or user_info.get("login"),
            provider=provider,
            provider_id=str(user_info.get("id")),
            verified=verified_email
        )
    elif provider == "linkedin":
        return OAuthUser(
            id=user_info.get("id"),
            email="",  # LinkedIn doesn't provide email in basic API
            name=f"{user_info.get('localizedFirstName', '')} {user_info.get('localizedLastName', '')}",
            provider=provider,
            provider_id=user_info.get("id"),
            verified=False
        )
    else:
        raise ValueError(f"Noma'lum provider: {provider}")

async def oauth_login(provider: str, redirect_uri: Optional[str] = None) -> Dict[str, Any]:
    """OAuth login boshlash"""
    if provider not in PROVIDERS:
        raise HTTPException(
            status_code=400, 
            detail=f"Qo'llab-quvvatlanmaydigan provider: {provider}"
        )
    
    # Generate state and PKCE
    state = generate_oauth_state()
    code_verifier, code_challenge = generate_pkce_challenge()
    
    # Store session
    session_id = secrets.token_urlsafe(32)
    oauth_sessions[session_id] = {
        "provider": provider,
        "state": state,
        "code_verifier": code_verifier,
        "redirect_uri": redirect_uri,
        "created_at": datetime.utcnow()
    }
    
    # Get authorization URL
    auth_url = await get_oauth_authorization_url(provider, state, redirect_uri)
    
    return {
        "auth_url": auth_url,
        "session_id": session_id,
        "state": state,
        "code_challenge": code_challenge
    }

async def oauth_callback(provider: str, code: str, state: str, session_id: str) -> OAuthToken:
    """OAuth callback"""
    if session_id not in oauth_sessions:
        raise HTTPException(status_code=400, detail="Noto'g'ri session")
    
    session = oauth_sessions[session_id]
    if session["state"] != state:
        raise HTTPException(status_code=400, detail="Noto'g'ri state")
    
    # Exchange code for token
    token_data = await exchange_code_for_token(
        provider, code, session["redirect_uri"]
    )
    
    # Get user info
    user_info = await get_user_info(provider, token_data["access_token"])
    
    # Normalize user info
    oauth_user = normalize_oauth_user_info(provider, user_info)
    
    # Create or update user in system
    user_id = oauth_user.id
    user = users_db.get(user_id)
    
    if not user:
        # Create new user
        user = User(
            id=uuid.uuid4(),
            username=oauth_user.email.split("@")[0],
            email=oauth_user.email,
            role="viewer",
            password=get_password_hash(secrets.token_urlsafe(16)),
            is_active=True,
            created_at=datetime.utcnow()
        )
        users_db[user_id] = user
    
    # Generate access token
    from .auth_handler import create_access_token
    access_token = create_access_token(
        data={"sub": user.username, "oauth_provider": provider}
    )
    
    # Clean up session
    del oauth_sessions[session_id]
    
    return OAuthToken(
        access_token=access_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        scope="read write",
        refresh_token=None
    )

async def verify_oauth_token(token: str) -> Optional[Dict[str, Any]]:
    """OAuth tokenni tekshirish"""
    return verify_token(token)

def has_permission(user_role: str, required_permission: str) -> bool:
    """Foydalanuvchi huquqlarini tekshirish"""
    permissions_map = {
        "admin": ["read", "write", "delete", "admin"],
        "trader": ["read", "write"],
        "analyst": ["read", "write"],
        "viewer": ["read"]
    }
    
    user_permissions = permissions_map.get(user_role, [])
    return required_permission in user_permissions

# Add missing imports
import uuid
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Parolni hash qilish"""
    return pwd_context.hash(password)