"""
API Security Moduli
===================

Bu modul quyidagi API security funksiyalarini ta'minlaydi:
- HTTPS enforcement
- Request signing
- API key rotation
- Audit logging
- Security headers
- JWT token validation

@author: Security Team
@version: 1.0.0
"""

import time
import hashlib
import hmac
import base64
import json
import secrets
import jwt
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)


@dataclass
class APIKey:
    """API Key ma'lumotlari"""
    key_id: str
    secret: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    permissions: List[str] = field(default_factory=list)
    rate_limit: int = 1000
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityHeaders:
    """Security headers konfiguratsiyasi"""
    content_security_policy: str = "default-src 'self'"
    x_frame_options: str = "DENY"
    x_content_type_options: str = "nosniff"
    x_xss_protection: str = "1; mode=block"
    strict_transport_security: str = "max-age=31536000; includeSubDomains"
    referrer_policy: str = "strict-origin-when-cross-origin"
    permissions_policy: str = "geolocation=(), microphone=(), camera=()"


class RequestSigner:
    """Request signing moduli"""
    
    def __init__(self):
        self.algorithms = ['sha256', 'sha512']
        self.default_algorithm = 'sha256'
    
    def sign_request(self, secret: str, method: str, path: str, 
                    timestamp: int, body: str = "", 
                    algorithm: str = None) -> str:
        """Request imzolash"""
        if algorithm is None:
            algorithm = self.default_algorithm
        
        # Request string yaratish
        request_string = f"{method.upper()}\n{path}\n{timestamp}\n{body}"
        
        # HMAC signing
        if algorithm == 'sha256':
            signature = hmac.new(
                secret.encode('utf-8'),
                request_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
        elif algorithm == 'sha512':
            signature = hmac.new(
                secret.encode('utf-8'),
                request_string.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        return signature
    
    def verify_signature(self, secret: str, signature: str, method: str, 
                        path: str, timestamp: int, body: str = "", 
                        algorithm: str = None) -> bool:
        """Request imzosini tekshirish"""
        try:
            expected_signature = self.sign_request(
                secret, method, path, timestamp, body, algorithm
            )
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    def create_signature_header(self, key_id: str, signature: str, 
                              timestamp: int, algorithm: str = None) -> str:
        """Signature header yaratish"""
        if algorithm is None:
            algorithm = self.default_algorithm
        
        return f"key_id={key_id},timestamp={timestamp},signature={signature},algorithm={algorithm}"


class APIKeyRotator:
    """API Key rotatsiya moduli"""
    
    def __init__(self):
        self.api_keys: Dict[str, APIKey] = {}
        self.key_cache: Dict[str, APIKey] = {}
        self.rotation_schedule: Dict[str, datetime] = {}
        self.lock_keys = True
        self._generate_master_key()
    
    def _generate_master_key(self):
        """Master key yaratish"""
        self.master_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.master_key)
    
    def create_api_key(self, permissions: List[str] = None, 
                      expires_days: int = 90, rate_limit: int = 1000) -> Tuple[str, APIKey]:
        """Yangi API key yaratish"""
        key_id = self._generate_key_id()
        secret = secrets.token_urlsafe(32)
        
        created_at = datetime.now()
        expires_at = created_at + timedelta(days=expires_days) if expires_days > 0 else None
        
        api_key = APIKey(
            key_id=key_id,
            secret=secret,
            created_at=created_at,
            expires_at=expires_at,
            permissions=permissions or [],
            rate_limit=rate_limit
        )
        
        # Store encrypted
        encrypted_secret = self.cipher_suite.encrypt(secret.encode()).decode()
        api_key.secret = encrypted_secret
        
        self.api_keys[key_id] = api_key
        logger.info(f"Created API key: {key_id}")
        
        return key_id, api_key
    
    def _generate_key_id(self) -> str:
        """Key ID yaratish"""
        return f"ak_{secrets.token_hex(8)}"
    
    def get_api_key(self, key_id: str) -> Optional[APIKey]:
        """API key olish"""
        # Check cache first
        if key_id in self.key_cache:
            return self.key_cache[key_id]
        
        # Get from storage
        api_key = self.api_keys.get(key_id)
        if api_key and api_key.is_active and not self._is_expired(api_key):
            # Decrypt secret
            try:
                api_key.secret = self.cipher_suite.decrypt(api_key.secret.encode()).decode()
                self.key_cache[key_id] = api_key
                return api_key
            except Exception as e:
                logger.error(f"API key decryption error: {e}")
        
        return None
    
    def _is_expired(self, api_key: APIKey) -> bool:
        """API key muddati tugaganligini tekshirish"""
        if api_key.expires_at is None:
            return False
        return datetime.now() > api_key.expires_at
    
    def rotate_api_key(self, key_id: str) -> Optional[Tuple[str, APIKey]]:
        """API keyni rotatsiya qilish"""
        old_key = self.get_api_key(key_id)
        if not old_key:
            return None
        
        # Yangi key yaratish
        new_key_id, new_api_key = self.create_api_key(
            permissions=old_key.permissions,
            expires_days=90,
            rate_limit=old_key.rate_limit
        )
        
        # Eski keyni deaktiv qilish
        old_key.is_active = False
        old_key.metadata['rotated_at'] = datetime.now()
        old_key.metadata['replaced_by'] = new_key_id
        
        # Yangi keyni eski key ma'lumotlari bilan yangilash
        new_api_key.metadata['replaces'] = key_id
        
        logger.info(f"Rotated API key: {key_id} -> {new_key_id}")
        
        return new_key_id, new_api_key
    
    def revoke_api_key(self, key_id: str, reason: str = "manual_revocation"):
        """API keyni bekor qilish"""
        api_key = self.api_keys.get(key_id)
        if api_key:
            api_key.is_active = False
            api_key.metadata['revoked_at'] = datetime.now()
            api_key.metadata['revocation_reason'] = reason
            
            # Cache'dan o'chirish
            if key_id in self.key_cache:
                del self.key_cache[key_id]
            
            logger.warning(f"Revoked API key: {key_id} - Reason: {reason}")
    
    def update_usage(self, key_id: str):
        """Usage statistikani yangilash"""
        api_key = self.api_keys.get(key_id)
        if api_key:
            api_key.usage_count += 1
            api_key.last_used = datetime.now()
    
    def get_keys_expiring_soon(self, days_ahead: int = 30) -> List[APIKey]:
        """Tez orada muddati tugaydigan keylarni olish"""
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        
        expiring_keys = []
        for api_key in self.api_keys.values():
            if (api_key.is_active and 
                api_key.expires_at and 
                api_key.expires_at <= cutoff_date):
                expiring_keys.append(api_key)
        
        return expiring_keys
    
    def cleanup_expired_keys(self):
        """Muddat tugagan keylarni tozalash"""
        now = datetime.now()
        expired_count = 0
        
        for key_id, api_key in list(self.api_keys.items()):
            if api_key.expires_at and now > api_key.expires_at:
                api_key.is_active = False
                expired_count += 1
        
        if expired_count > 0:
            logger.info(f"Cleaned up {expired_count} expired API keys")


class APISecurityManager:
    """Asosiy API Security Manager"""
    
    def __init__(self, jwt_secret: str = None):
        self.request_signer = RequestSigner()
        self.key_rotator = APIKeyRotator()
        self.security_headers = SecurityHeaders()
        
        # JWT settings
        self.jwt_secret = jwt_secret or secrets.token_urlsafe(32)
        self.jwt_algorithm = 'HS256'
        self.jwt_expiration = 3600  # 1 hour
        
        # Rate limiting
        self.request_counts: Dict[str, Dict[str, int]] = {}
        
        # Audit logging
        self.audit_log: List[Dict[str, Any]] = []
        
        # Security events
        self.security_events: List[Dict[str, Any]] = []
    
    def validate_api_key(self, api_key: str, endpoint: str = "") -> Tuple[bool, Optional[str], Optional[APIKey]]:
        """API key validation"""
        key_data = self.key_rotator.get_api_key(api_key)
        
        if not key_data:
            self._log_security_event("invalid_api_key", "high", {"api_key": api_key[:10] + "..."})
            return False, "Invalid API key", None
        
        if not key_data.is_active:
            self._log_security_event("inactive_api_key", "medium", {"api_key": key_data.key_id})
            return False, "API key is inactive", None
        
        if key_data.expires_at and datetime.now() > key_data.expires_at:
            self._log_security_event("expired_api_key", "high", {"api_key": key_data.key_id})
            return False, "API key has expired", None
        
        # Endpoint permission check
        if endpoint and key_data.permissions:
            endpoint_prefix = endpoint.split('/')[0] if '/' in endpoint else endpoint
            if not any(perm.startswith(endpoint_prefix) or endpoint.startswith(perm) 
                      for perm in key_data.permissions):
                return False, f"Insufficient permissions for {endpoint}", None
        
        # Update usage
        self.key_rotator.update_usage(key_data.key_id)
        
        # Log audit
        self._log_audit_event("api_key_used", {
            "key_id": key_data.key_id,
            "endpoint": endpoint,
            "permissions": key_data.permissions
        })
        
        return True, None, key_data
    
    def validate_jwt_token(self, token: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """JWT token validation"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Check expiration
            if 'exp' in payload and payload['exp'] < time.time():
                return False, None, "Token expired"
            
            # Log audit
            self._log_audit_event("jwt_validated", {
                "user_id": payload.get('user_id'),
                "permissions": payload.get('permissions', [])
            })
            
            return True, payload, None
        except jwt.InvalidTokenError as e:
            self._log_security_event("invalid_jwt", "medium", {"error": str(e)})
            return False, None, f"Invalid token: {str(e)}"
    
    def create_jwt_token(self, user_id: str, permissions: List[str] = None, 
                        expires_in: int = None) -> str:
        """JWT token yaratish"""
        if expires_in is None:
            expires_in = self.jwt_expiration
        
        payload = {
            'user_id': user_id,
            'permissions': permissions or [],
            'iat': time.time(),
            'exp': time.time() + expires_in,
            'iss': 'api_security'
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        self._log_audit_event("jwt_created", {
            "user_id": user_id,
            "permissions": permissions,
            "expires_in": expires_in
        })
        
        return token
    
    def validate_signature(self, signature_header: str, method: str, 
                          path: str, body: str = "", 
                          timestamp_skew: int = 300) -> Tuple[bool, Optional[str]]:
        """Request signature validation"""
        try:
            # Parse signature header
            parts = {}
            for part in signature_header.split(','):
                if '=' in part:
                    key, value = part.split('=', 1)
                    parts[key.strip()] = value.strip()
            
            required_parts = ['key_id', 'timestamp', 'signature']
            if not all(part in parts for part in required_parts):
                return False, "Missing signature components"
            
            # Get API key
            api_key_obj = self.key_rotator.get_api_key(parts['key_id'])
            if not api_key_obj:
                return False, "Invalid API key in signature"
            
            # Check timestamp skew
            try:
                signature_timestamp = int(parts['timestamp'])
                current_time = int(time.time())
                if abs(current_time - signature_timestamp) > timestamp_skew:
                    self._log_security_event("signature_timestamp_skew", "medium", {
                        "key_id": parts['key_id'],
                        "skew": abs(current_time - signature_timestamp)
                    })
                    return False, "Request timestamp too old or too new"
            except ValueError:
                return False, "Invalid timestamp format"
            
            # Verify signature
            algorithm = parts.get('algorithm', 'sha256')
            is_valid = self.request_signer.verify_signature(
                api_key_obj.secret,
                parts['signature'],
                method,
                path,
                signature_timestamp,
                body,
                algorithm
            )
            
            if not is_valid:
                self._log_security_event("invalid_signature", "high", {
                    "key_id": parts['key_id'],
                    "method": method,
                    "path": path
                })
                return False, "Invalid signature"
            
            return True, parts['key_id']
        
        except Exception as e:
            logger.error(f"Signature validation error: {e}")
            return False, "Signature validation failed"
    
    def enforce_https(self, request_headers: Dict[str, str], 
                     force_https: bool = True) -> Tuple[bool, Optional[str]]:
        """HTTPS enforcement"""
        if force_https:
            # Check for HTTPS
            is_https = request_headers.get('X-Forwarded-Proto') == 'https' or \
                      request_headers.get('X-Forwarded-SSL') == 'on' or \
                      request_headers.get('X-Forwarded-HTTPS') == '1'
            
            if not is_https:
                self._log_security_event("insecure_http_request", "medium", {
                    "headers": dict(request_headers)
                })
                return False, "HTTPS required for this request"
        
        return True, None
    
    def get_security_headers(self) -> Dict[str, str]:
        """Security headers olish"""
        return {
            'Content-Security-Policy': self.security_headers.content_security_policy,
            'X-Frame-Options': self.security_headers.x_frame_options,
            'X-Content-Type-Options': self.security_headers.x_content_type_options,
            'X-XSS-Protection': self.security_headers.x_xss_protection,
            'Strict-Transport-Security': self.security_headers.strict_transport_security,
            'Referrer-Policy': self.security_headers.referrer_policy,
            'Permissions-Policy': self.security_headers.permissions_policy,
            'X-Content-Type-Options': 'nosniff'
        }
    
    def _log_audit_event(self, event_type: str, details: Dict[str, Any]):
        """Audit event logging"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details
        }
        self.audit_log.append(event)
        
        # Keep only last 10000 events
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-10000:]
        
        logger.info(f"Audit: {event_type} - {details}")
    
    def _log_security_event(self, event_type: str, severity: str, details: Dict[str, Any]):
        """Security event logging"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'details': details
        }
        self.security_events.append(event)
        
        # Keep only last 5000 events
        if len(self.security_events) > 5000:
            self.security_events = self.security_events[-5000:]
        
        logger.warning(f"Security: {event_type} ({severity}) - {details}")
    
    def get_audit_report(self, start_date: datetime = None, 
                        end_date: datetime = None) -> Dict[str, Any]:
        """Audit report olish"""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=7)
        if end_date is None:
            end_date = datetime.now()
        
        filtered_events = [
            event for event in self.audit_log
            if start_date <= datetime.fromisoformat(event['timestamp']) <= end_date
        ]
        
        return {
            'total_events': len(filtered_events),
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'events_by_type': self._count_events_by_type(filtered_events),
            'recent_events': filtered_events[-100:]  # Last 100 events
        }
    
    def get_security_report(self) -> Dict[str, Any]:
        """Security report olish"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        
        recent_security_events = [
            event for event in self.security_events
            if datetime.fromisoformat(event['timestamp']) > last_24h
        ]
        
        return {
            'total_events': len(self.security_events),
            'recent_events_24h': len(recent_security_events),
            'events_by_severity': self._count_events_by_severity(recent_security_events),
            'events_by_type': self._count_events_by_type(recent_security_events),
            'recent_events': recent_security_events[-50:]  # Last 50 events
        }
    
    def _count_events_by_type(self, events: List[Dict]) -> Dict[str, int]:
        """Eventlarni type bo'yicha hisoblash"""
        counts = {}
        for event in events:
            event_type = event.get('event_type', 'unknown')
            counts[event_type] = counts.get(event_type, 0) + 1
        return counts
    
    def _count_events_by_severity(self, events: List[Dict]) -> Dict[str, int]:
        """Eventlarni severity bo'yicha hisoblash"""
        counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        for event in events:
            severity = event.get('severity', 'low')
            if severity in counts:
                counts[severity] += 1
        return counts