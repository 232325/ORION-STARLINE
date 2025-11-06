"""
Orion Starline - Kuchaytirilgan Security Middleware
Advanced Security Layer for AI Trading Platform
"""

import jwt
import time
import hashlib
import hmac
import secrets
import logging
import json
import redis
import smtplib
from email.mime.text import MimeText
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from functools import wraps
from flask import request, jsonify, session, current_app
from werkzeug.security import check_password_hash, generate_password_hash
import pyotp
import qrcode
from io import BytesIO
import base64
import geocoder
import ipaddress
from collections import defaultdict, deque
import threading

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityConfig:
    """Security tizim konfiguratsiyasi"""
    SECRET_KEY = "orion-starline-2024-advanced-security"
    JWT_SECRET = "jwt-orion-starline-secret-2024"
    JWT_ALGORITHM = "HS256"
    
    # Token expiration
    ACCESS_TOKEN_EXPIRY = 15  # minutes
    REFRESH_TOKEN_EXPIRY = 7  # days
    RESET_TOKEN_EXPIRY = 10   # minutes
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 60  # seconds
    BURST_LIMIT = 10
    
    # IP blocking
    BLOCK_DURATION = 3600  # seconds
    MAX_FAILED_ATTEMPTS = 5
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }

class TokenManager:
    """JWT Token Management va rotation"""
    
    def __init__(self):
        self.secret_key = SecurityConfig.JWT_SECRET
        self.algorithm = SecurityConfig.JWT_ALGORITHM
        self.blacklisted_tokens = set()
        self.token_families = defaultdict(set)  # User token families
        self.revocation_list = set()
    
    def generate_access_token(self, user_id: str, role: str, permissions: List[str]) -> str:
        """Qisqa muddatli access token yaratish"""
        payload = {
            'user_id': user_id,
            'role': role,
            'permissions': permissions,
            'type': 'access',
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=SecurityConfig.ACCESS_TOKEN_EXPIRY),
            'jti': secrets.token_hex(16)  # JWT ID
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def generate_refresh_token(self, user_id: str, token_family: str) -> str:
        """Refresh token yaratish"""
        payload = {
            'user_id': user_id,
            'type': 'refresh',
            'family': token_family,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=SecurityConfig.REFRESH_TOKEN_EXPIRY),
            'jti': secrets.token_hex(16)
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        self.token_families[user_id].add(token_family)
        return token
    
    def verify_token(self, token: str, token_type: str = 'access') -> Optional[Dict]:
        """Token ni tekshirish va blacklistni tekshirish"""
        try:
            if token in self.blacklisted_tokens:
                logger.warning(f"Blacklisted token attempted: {token[:20]}...")
                return None
            
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Token type validation
            if payload.get('type') != token_type:
                logger.warning(f"Invalid token type: {payload.get('type')}")
                return None
            
            # Expiration check
            if payload.get('exp', 0) < time.time():
                logger.warning("Token expired")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token signature expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
    
    def revoke_token(self, token: str, user_id: str = None):
        """Token ni revokatsiya qilish"""
        self.blacklisted_tokens.add(token)
        
        # Token family revocation if user_id provided
        if user_id and user_id in self.token_families:
            try:
                payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
                family = payload.get('family')
                if family:
                    # Revoke all tokens in the same family
                    all_families = set(self.token_families[user_id])
                    for fam in all_families:
                        if fam == family:
                            # In a real implementation, you'd have a proper token store
                            logger.info(f"Revoked token family: {family} for user: {user_id}")
            except:
                pass
    
    def rotate_tokens(self, old_token: str, user_id: str) -> Dict[str, str]:
        """Token rotation - eski tokenlarni bekor qilish va yangi tokenlar yaratish"""
        try:
            payload = jwt.decode(old_token, self.secret_key, algorithms=[self.algorithm])
            if payload.get('type') == 'refresh':
                token_family = payload.get('family')
                role = 'user'  # You'd get this from database
                permissions = ['read']  # You'd get this from database
                
                # Revoke old family tokens
                self.token_families[user_id].discard(token_family)
                
                # Create new family
                new_family = secrets.token_hex(16)
                new_access = self.generate_access_token(user_id, role, permissions)
                new_refresh = self.generate_refresh_token(user_id, new_family)
                
                return {
                    'access_token': new_access,
                    'refresh_token': new_refresh
                }
        except:
            pass
        
        return None

class RateLimiter:
    """IP-based va user-based rate limiting"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.local_storage = defaultdict(lambda: {
            'requests': deque(),
            'failed_attempts': deque(),
            'blocked_until': 0,
            'violations': 0
        })
        self.geographic_restrictions = {
            'blocked_countries': [],  # Add country codes
            'allowed_countries': [],  # If not empty, only these are allowed
            'high_risk_countries': []  # Additional restrictions
        }
        self.whitelist_ips = set()
        self.blacklist_ips = set()
    
    def is_rate_limited(self, identifier: str, limit: int = None, window: int = None) -> Dict:
        """Rate limiting tekshirish"""
        limit = limit or SecurityConfig.RATE_LIMIT_REQUESTS
        window = window or SecurityConfig.RATE_LIMIT_WINDOW
        
        current_time = time.time()
        storage = self.local_storage[identifier]
        
        # IP whitelist check
        if identifier in self.whitelist_ips:
            return {'limited': False, 'remaining': limit, 'reset_time': current_time + window}
        
        # IP blacklist check
        if identifier in self.blacklist_ips:
            return {'limited': True, 'reason': 'IP blacklisted', 'blocked_until': current_time + SecurityConfig.BLOCK_DURATION}
        
        # Block duration check
        if storage['blocked_until'] > current_time:
            return {'limited': True, 'reason': 'Temporary block', 'blocked_until': storage['blocked_until']}
        
        # Clean old requests
        while storage['requests'] and storage['requests'][0] < current_time - window:
            storage['requests'].popleft()
        
        # Check rate limit
        if len(storage['requests']) >= limit:
            storage['violations'] += 1
            
            # Gradual ban system
            if storage['violations'] >= SecurityConfig.MAX_FAILED_ATTEMPTS:
                storage['blocked_until'] = current_time + SecurityConfig.BLOCK_DURATION
                logger.warning(f"IP {identifier} blocked for rate limit violations")
                return {'limited': True, 'reason': 'Rate limit exceeded', 'blocked_until': storage['blocked_until']}
        
        # Record request
        storage['requests'].append(current_time)
        
        return {
            'limited': False,
            'remaining': limit - len(storage['requests']),
            'reset_time': storage['requests'][0] + window if storage['requests'] else current_time + window
        }
    
    def record_failed_attempt(self, identifier: str):
        """Muvaffaqiyatsiz urinishlarni qayd etish"""
        current_time = time.time()
        storage = self.local_storage[identifier]
        
        # Clean old failed attempts
        while storage['failed_attempts'] and storage['failed_attempts'][0] < current_time - 3600:  # 1 hour window
            storage['failed_attempts'].popleft()
        
        storage['failed_attempts'].append(current_time)
        
        # Check for brute force pattern
        if len(storage['failed_attempts']) >= SecurityConfig.MAX_FAILED_ATTEMPTS:
            storage['blocked_until'] = current_time + SecurityConfig.BLOCK_DURATION
            logger.warning(f"IP {identifier} blocked for failed authentication attempts")
    
    def add_to_whitelist(self, ip: str):
        """IP ni whitelist ga qo'shish"""
        self.whitelist_ips.add(ip)
    
    def add_to_blacklist(self, ip: str):
        """IP ni blacklist ga qo'shish"""
        self.blacklist_ips.add(ip)
    
    def get_client_ip(self) -> str:
        """Client IP manzilini aniqlash"""
        # Forwarded headers check
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.remote_addr or '127.0.0.1'

class RBACSystem:
    """Role-based Access Control system"""
    
    def __init__(self):
        self.roles = {
            'admin': {
                'permissions': ['*'],  # All permissions
                'level': 5,
                'description': 'Full system access'
            },
            'trader': {
                'permissions': ['trading.create', 'trading.read', 'trading.update', 'trading.delete', 
                              'portfolio.read', 'portfolio.update', 'signals.read', 'analytics.read'],
                'level': 3,
                'description': 'Trading operations access'
            },
            'viewer': {
                'permissions': ['portfolio.read', 'signals.read', 'analytics.read'],
                'level': 1,
                'description': 'Read-only access'
            }
        }
        
        self.user_roles = {}  # user_id -> role
        self.temporary_permissions = defaultdict(list)  # user_id -> [(permission, expires_at)]
        self.role_hierarchy = {
            'admin': ['trader', 'viewer'],
            'trader': ['viewer']
        }
    
    def assign_role(self, user_id: str, role: str):
        """Foydalanuvchiga role berish"""
        if role in self.roles:
            self.user_roles[user_id] = role
            logger.info(f"Role {role} assigned to user {user_id}")
            return True
        return False
    
    def has_permission(self, user_id: str, permission: str) -> bool:
        """Foydalanuvchining permission borligini tekshirish"""
        # Check user role
        role = self.user_roles.get(user_id)
        if not role:
            return False
        
        role_perms = self.roles[role]['permissions']
        
        # Admin has all permissions
        if '*' in role_perms:
            return True
        
        # Direct permission check
        if permission in role_perms:
            return True
        
        # Hierarchical permission check
        for inherited_role in self.role_hierarchy.get(role, []):
            if permission in self.roles[inherited_role]['permissions']:
                return True
        
        # Temporary permission check
        current_time = datetime.utcnow()
        for temp_perm, expires_at in self.temporary_permissions[user_id]:
            if permission == temp_perm and expires_at > current_time:
                return True
        
        return False
    
    def grant_temporary_permission(self, user_id: str, permission: str, duration_minutes: int):
        """Vaqtinchalik permission berish"""
        expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.temporary_permissions[user_id].append((permission, expires_at))
        logger.info(f"Temporary permission {permission} granted to user {user_id} for {duration_minutes} minutes")
    
    def revoke_user_role(self, user_id: str):
        """Foydalanuvchi role ni olish"""
        if user_id in self.user_roles:
            old_role = self.user_roles.pop(user_id)
            logger.info(f"Role {old_role} revoked from user {user_id}")

class TwoFactorAuth:
    """Advanced 2FA tizimi"""
    
    def __init__(self):
        self.user_secrets = {}  # user_id -> TOTP secret
        self.backup_codes = {}  # user_id -> [backup_codes]
        self.enabled_users = set()
        self.biometric_enabled = set()
        self.hardware_tokens = {}  # user_id -> token_info
    
    def generate_totp_secret(self) -> str:
        """TOTP secret yaratish"""
        return pyotp.random_base32()
    
    def generate_qr_code(self, secret: str, user_email: str) -> str:
        """QR kod yaratish"""
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name="Orion Starline"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # Convert to base64
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def enable_2fa(self, user_id: str, secret: str, backup_codes: List[str]):
        """2FA ni yoqish"""
        self.user_secrets[user_id] = secret
        self.backup_codes[user_id] = backup_codes
        self.enabled_users.add(user_id)
        logger.info(f"2FA enabled for user {user_id}")
    
    def verify_totp(self, user_id: str, token: str) -> bool:
        """TOTP token ni tekshirish"""
        if user_id not in self.user_secrets:
            return False
        
        totp = pyotp.TOTP(self.user_secrets[user_id])
        return totp.verify(token, valid_window=1)
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Backup kodlar yaratish"""
        return [secrets.token_hex(4).upper() for _ in range(count)]
    
    def verify_backup_code(self, user_id: str, code: str) -> bool:
        """Backup kodni tekshirish"""
        if user_id not in self.backup_codes:
            return False
        
        code = code.upper()
        if code in self.backup_codes[user_id]:
            self.backup_codes[user_id].remove(code)
            return True
        return False
    
    def enable_biometric(self, user_id: str, biometric_data: str):
        """Biometric authentication yoqish"""
        self.biometric_enabled.add(user_id)
        logger.info(f"Biometric authentication enabled for user {user_id}")
    
    def verify_biometric(self, user_id: str, biometric_data: str) -> bool:
        """Biometric data ni tekshirish (simplified)"""
        if user_id not in self.biometric_enabled:
            return False
        
        # In a real implementation, this would use proper biometric verification
        # This is a simplified version
        return len(biometric_data) > 100  # Basic validation

class SessionManager:
    """Advanced Session Management"""
    
    def __init__(self):
        self.active_sessions = {}  # session_id -> session_data
        self.session_family = {}   # user_id -> set(session_ids)
        self.session_lock = threading.Lock()
    
    def create_session(self, user_id: str, additional_data: Dict = None) -> str:
        """Yangi session yaratish"""
        session_id = secrets.token_hex(32)
        current_time = datetime.utcnow()
        
        session_data = {
            'user_id': user_id,
            'created_at': current_time,
            'last_activity': current_time,
            'ip_address': None,  # Set by middleware
            'user_agent': None,  # Set by middleware
            'additional_data': additional_data or {},
            'security_score': 100
        }
        
        with self.session_lock:
            self.active_sessions[session_id] = session_data
            if user_id not in self.session_family:
                self.session_family[user_id] = set()
            self.session_family[user_id].add(session_id)
        
        logger.info(f"Session created for user {user_id}: {session_id[:16]}...")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Session ma'lumotlarini olish"""
        return self.active_sessions.get(session_id)
    
    def update_activity(self, session_id: str):
        """Session aktivligini yangilash"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['last_activity'] = datetime.utcnow()
    
    def invalidate_session(self, session_id: str):
        """Session ni bekor qilish"""
        with self.session_lock:
            if session_id in self.active_sessions:
                user_id = self.active_sessions[session_id]['user_id']
                del self.active_sessions[session_id]
                
                if user_id in self.session_family:
                    self.session_family[user_id].discard(session_id)
                    
                    # Clean up empty sets
                    if not self.session_family[user_id]:
                        del self.session_family[user_id]
    
    def invalidate_user_sessions(self, user_id: str, keep_session_id: str = None):
        """Foydalanuvchi barcha session larini bekor qilish"""
        with self.session_lock:
            if user_id in self.session_family:
                session_ids = list(self.session_family[user_id])
                for sid in session_ids:
                    if sid != keep_session_id:
                        if sid in self.active_sessions:
                            del self.active_sessions[sid]
                del self.session_family[user_id]
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24):
        """Muddati tugagan session larni tozalash"""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        with self.session_lock:
            for session_id, data in self.active_sessions.items():
                age = current_time - data['last_activity']
                if age.total_seconds() > max_age_hours * 3600:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                user_id = self.active_sessions[session_id]['user_id']
                del self.active_sessions[session_id]
                if user_id in self.session_family:
                    self.session_family[user_id].discard(session_id)
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")

class AuditLogger:
    """Comprehensive audit logging"""
    
    def __init__(self):
        self.log_buffer = []
        self.audit_rules = {
            'login_attempts': True,
            'permission_changes': True,
            'data_access': True,
            'trading_operations': True,
            'admin_actions': True,
            'security_events': True
        }
    
    def log_event(self, event_type: str, user_id: str, action: str, 
                  details: Dict = None, ip_address: str = None):
        """Audit event ni qayd etish"""
        if not self.audit_rules.get(event_type, False):
            return
        
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'action': action,
            'details': details or {},
            'ip_address': ip_address,
            'session_id': session.get('session_id') if hasattr(session, 'get') else None
        }
        
        # Log to buffer (in production, this would go to a proper logging system)
        self.log_buffer.append(event)
        
        # Log to file/database
        logger.info(f"AUDIT: {json.dumps(event, default=str)}")
        
        # Keep only last 1000 events in memory
        if len(self.log_buffer) > 1000:
            self.log_buffer = self.log_buffer[-500:]
    
    def get_user_events(self, user_id: str, hours: int = 24) -> List[Dict]:
        """Foydalanuvchi so'nggi eventlarini olish"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            event for event in self.log_buffer 
            if event['user_id'] == user_id and 
            datetime.fromisoformat(event['timestamp']) > cutoff_time
        ]
    
    def generate_compliance_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Compliance report yaratish"""
        report = {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_events': 0,
            'event_types': defaultdict(int),
            'user_activity': defaultdict(int),
            'security_incidents': [],
            'summary': {}
        }
        
        for event in self.log_buffer:
            event_time = datetime.fromisoformat(event['timestamp'])
            if start_date <= event_time <= end_date:
                report['total_events'] += 1
                report['event_types'][event['event_type']] += 1
                report['user_activity'][event['user_id']] += 1
                
                if event['event_type'] == 'security_events':
                    report['security_incidents'].append(event)
        
        return report

# Global instances
token_manager = TokenManager()
rate_limiter = RateLimiter()
rbac_system = RBACSystem()
two_factor_auth = TwoFactorAuth()
session_manager = SessionManager()
audit_logger = AuditLogger()

def security_middleware(f):
    """Main security middleware decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get client information
        client_ip = rate_limiter.get_client_ip()
        user_agent = request.headers.get('User-Agent', '')
        current_time = time.time()
        
        # Rate limiting check
        rate_check = rate_limiter.is_rate_limited(client_ip)
        if rate_check['limited']:
            audit_logger.log_event('security_events', 'unknown', 'rate_limit_exceeded', 
                                 {'ip': client_ip, 'reason': rate_check['reason']})
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests',
                'retry_after': rate_check.get('blocked_until', current_time + 60) - current_time
            }), 429
        
        # Add security headers
        for header, value in SecurityConfig.SECURITY_HEADERS.items():
            if hasattr(current_app, 'headers'):
                current_app.headers[header] = value
        
        # Update session activity
        session_id = session.get('session_id')
        if session_id:
            session_manager.update_activity(session_id)
        
        # Log request for audit
        audit_logger.log_event('data_access', session.get('user_id', 'anonymous'), 
                             f'API: {request.endpoint}', 
                             {'method': request.method, 'ip': client_ip, 'user_agent': user_agent})
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_auth(f):
    """Authentication talab qiluvchi decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        token = auth_header.split(' ')[1]
        payload = token_manager.verify_token(token, 'access')
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Check if user has 2FA enabled
        user_id = payload['user_id']
        if user_id in two_factor_auth.enabled_users:
            # In a real implementation, you'd check if 2FA was already verified for this session
            pass
        
        # Add user info to request context
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_permission(permission: str):
    """Permission talab qiluvchi decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = getattr(request, 'current_user', {}).get('user_id')
            if not user_id:
                return jsonify({'error': 'Authentication required'}), 401
            
            if not rbac_system.has_permission(user_id, permission):
                audit_logger.log_event('security_events', user_id, 'permission_denied', 
                                     {'required_permission': permission})
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def rate_limit(requests: int = None, window: int = None):
    """Custom rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = rate_limiter.get_client_ip()
            rate_check = rate_limiter.is_rate_limited(client_ip, requests, window)
            
            if rate_check['limited']:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# Helper functions
def generate_api_key(user_id: str, permissions: List[str]) -> str:
    """API key yaratish"""
    key_data = {
        'user_id': user_id,
        'permissions': permissions,
        'created_at': datetime.utcnow().isoformat(),
        'key_id': secrets.token_hex(8)
    }
    
    # In production, store in secure database
    api_key = f"os_api_{base64.b64encode(json.dumps(key_data).encode()).decode()}_{secrets.token_hex(16)}"
    return api_key

def verify_api_key(api_key: str) -> Optional[Dict]:
    """API key ni tekshirish"""
    try:
        if not api_key.startswith('os_api_'):
            return None
        
        # Parse and verify API key
        parts = api_key.split('_')
        if len(parts) < 4:
            return None
        
        encoded_data = '_'.join(parts[2:-1])
        key_data = json.loads(base64.b64decode(encoded_data).decode())
        
        # In production, verify against database
        return key_data
        
    except Exception as e:
        logger.warning(f"API key verification failed: {str(e)}")
        return None

def detect_anomalies(user_id: str, request_data: Dict) -> Dict:
    """Anomali detektsiya"""
    # Basic anomaly detection
    current_time = datetime.utcnow()
    recent_events = audit_logger.get_user_events(user_id, hours=1)
    
    # Check for unusual activity patterns
    anomaly_score = 0
    anomalies = []
    
    # Check request frequency
    if len(recent_events) > 50:  # More than 50 requests in last hour
        anomaly_score += 20
        anomalies.append('High request frequency')
    
    # Check for rapid fire requests
    for i in range(1, len(recent_events)):
        time_diff = (datetime.fromisoformat(recent_events[i]['timestamp']) - 
                    datetime.fromisoformat(recent_events[i-1]['timestamp'])).total_seconds()
        if time_diff < 1:  # Requests less than 1 second apart
            anomaly_score += 10
            anomalies.append('Rapid request pattern')
    
    # Check for different IP addresses
    ip_addresses = set(event.get('ip_address') for event in recent_events)
    if len(ip_addresses) > 3:  # More than 3 different IPs
        anomaly_score += 15
        anomalies.append('Multiple IP addresses')
    
    # Check for unusual hours
    current_hour = current_time.hour
    if current_hour < 6 or current_hour > 22:  # Unusual hours
        anomaly_score += 5
        anomalies.append('Unusual access time')
    
    return {
        'anomaly_score': anomaly_score,
        'anomalies': anomalies,
        'risk_level': 'high' if anomaly_score > 30 else 'medium' if anomaly_score > 15 else 'low'
    }

# Cleanup thread
def start_cleanup_scheduler():
    """Background cleanup scheduler"""
    def cleanup_worker():
        while True:
            try:
                session_manager.cleanup_expired_sessions()
                time.sleep(3600)  # Run every hour
            except Exception as e:
                logger.error(f"Cleanup worker error: {str(e)}")
                time.sleep(300)  # Wait 5 minutes before retry
    
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()

# Initialize
if __name__ == "__main__":
    start_cleanup_scheduler()
    print("Orion Starline Security Middleware initialized")