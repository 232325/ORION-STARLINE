"""
Security Utilities Moduli
=========================

Bu modul security tizimi uchun umumiy utility funksiyalarni ta'minlaydi:
- IP address manipulation
- User agent parsing
- Hashing va encoding utilities
- Security helpers
- Validation decorators

@author: Security Team
@version: 1.0.0
"""

import re
import ipaddress
import hashlib
import hmac
import secrets
import base64
import json
import time
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from functools import wraps
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class IPAddressUtils:
    """IP address utility moduli"""
    
    # Private IP ranges
    PRIVATE_IP_RANGES = [
        ('10.0.0.0', '10.255.255.255'),
        ('172.16.0.0', '172.31.255.255'),
        ('192.168.0.0', '192.168.255.255'),
        ('127.0.0.0', '127.255.255.255'),
        ('169.254.0.0', '169.254.255.255'),
        ('::1', '::1'),
        ('fc00::', 'fdff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'),
        ('fe80::', 'febf:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
    ]
    
    @staticmethod
    def is_private_ip(ip_address: str) -> bool:
        """Private IP manzilini tekshirish"""
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Check if it's a private IP
            if ip.is_private:
                return True
            
            # Check against known private ranges
            for start, end in IPAddressUtils.PRIVATE_IP_RANGES:
                try:
                    start_ip = ipaddress.ip_address(start)
                    end_ip = ipaddress.ip_address(end)
                    if start_ip <= ip <= end_ip:
                        return True
                except:
                    continue
            
            return False
        except ValueError:
            return False
    
    @staticmethod
    def is_public_ip(ip_address: str) -> bool:
        """Public IP manzilini tekshirish"""
        return not IPAddressUtils.is_private_ip(ip_address)
    
    @staticmethod
    def get_ip_info(ip_address: str) -> Dict[str, Any]:
        """IP manzil ma'lumotlarini olish"""
        info = {
            'ip': ip_address,
            'is_private': False,
            'is_public': False,
            'is_loopback': False,
            'is_multicast': False,
            'version': 4  # Default to IPv4
        }
        
        try:
            ip = ipaddress.ip_address(ip_address)
            info.update({
                'is_private': ip.is_private,
                'is_public': not ip.is_private,
                'is_loopback': ip.is_loopback,
                'is_multicast': ip.is_multicast,
                'version': ip.version,
                'is_link_local': getattr(ip, 'is_link_local', False),
                'is_reserved': getattr(ip, 'is_reserved', False)
            })
            
            # Additional information
            if ip.version == 4:
                info['is_global'] = not (ip.is_private or ip.is_loopback or 
                                       ip.is_multicast or getattr(ip, 'is_link_local', False))
            else:
                info['is_global'] = not (ip.is_private or ip.is_loopback or 
                                       ip.is_multicast or getattr(ip, 'is_link_local', False))
                
        except ValueError:
            info['error'] = 'Invalid IP address format'
        
        return info
    
    @staticmethod
    def normalize_ip(ip_address: str) -> Optional[str]:
        """IP manzilni normalize qilish"""
        try:
            ip = ipaddress.ip_address(ip_address)
            return str(ip)
        except ValueError:
            return None
    
    @staticmethod
    def extract_client_ip(headers: Dict[str, str]) -> str:
        """Client IP ni headers dan extract qilish"""
        # Check various proxy/load balancer headers
        ip_headers = [
            'X-Forwarded-For',
            'X-Real-IP',
            'X-Client-IP',
            'CF-Connecting-IP',  # Cloudflare
            'X-Originating-IP',
            'X-Remote-IP',
            'X-Remote-Addr'
        ]
        
        for header in ip_headers:
            if header in headers:
                ip_value = headers[header]
                # X-Forwarded-For can contain multiple IPs, take the first one
                if header == 'X-Forwarded-For':
                    ip_value = ip_value.split(',')[0].strip()
                
                # Clean and validate IP
                normalized_ip = IPAddressUtils.normalize_ip(ip_value)
                if normalized_ip:
                    return normalized_ip
        
        # If no headers found, return a default
        return '127.0.0.1'


class UserAgentParser:
    """User Agent parser"""
    
    # Common bot patterns
    BOT_PATTERNS = [
        r'bot', r'crawler', r'spider', r'scraper', r'crawl',
        r'googlebot', r'bingbot', r'slurp', r'duckduckbot',
        r'facebookexternalhit', r'twitterbot', r'linkedinbot',
        r'whatsapp', r'telegram', r'skype', r'python',
        r'curl', r'wget', r'postman', r'insomnia'
    ]
    
    # Mobile patterns
    MOBILE_PATTERNS = [
        r'mobile', r'android', r'iphone', r'ipad', r'ipod',
        r'blackberry', r'windows phone', r'opera mini',
        r'iemobile', r'mobile safari', r'chrome mobile'
    ]
    
    # Desktop patterns
    DESKTOP_PATTERNS = [
        r'windows nt', r'macintosh', r'linux', r'chrome',
        r'firefox', r'safari', r'edge', r'opera', r'ie'
    ]
    
    @staticmethod
    def parse_user_agent(user_agent: str) -> Dict[str, Any]:
        """User Agent ni parse qilish"""
        if not user_agent:
            return {
                'is_bot': True,
                'is_mobile': False,
                'is_desktop': False,
                'browser': 'Unknown',
                'os': 'Unknown',
                'device': 'Unknown'
            }
        
        user_agent_lower = user_agent.lower()
        
        # Detect if it's a bot
        is_bot = any(re.search(pattern, user_agent_lower) for pattern in UserAgentParser.BOT_PATTERNS)
        
        # Detect platform type
        is_mobile = any(re.search(pattern, user_agent_lower) for pattern in UserAgentParser.MOBILE_PATTERNS)
        is_desktop = any(re.search(pattern, user_agent_lower) for pattern in UserAgentParser.DESKTOP_PATTERNS)
        
        if not is_mobile and not is_desktop:
            is_desktop = True  # Default to desktop if unclear
        
        # Parse browser
        browser = UserAgentParser._parse_browser(user_agent)
        
        # Parse OS
        os = UserAgentParser._parse_os(user_agent)
        
        # Parse device
        device = UserAgentParser._parse_device(user_agent, is_mobile, is_desktop)
        
        return {
            'user_agent': user_agent,
            'is_bot': is_bot,
            'is_mobile': is_mobile,
            'is_desktop': is_desktop,
            'browser': browser,
            'os': os,
            'device': device,
            'raw_data': user_agent
        }
    
    @staticmethod
    def _parse_browser(user_agent: str) -> str:
        """Browser ni aniqlash"""
        browser_patterns = {
            r'chrome': 'Chrome',
            r'firefox': 'Firefox',
            r'safari': 'Safari',
            r'edge': 'Edge',
            r'opera': 'Opera',
            r'ie': 'Internet Explorer',
            r'vivaldi': 'Vivaldi',
            r'brave': 'Brave',
            r'tor': 'Tor Browser'
        }
        
        user_agent_lower = user_agent.lower()
        for pattern, name in browser_patterns.items():
            if re.search(pattern, user_agent_lower):
                # Extract version if possible
                if pattern in ['chrome', 'firefox', 'safari', 'edge']:
                    version_match = re.search(rf'{pattern}/([\d.]+)', user_agent_lower)
                    if version_match:
                        return f"{name} {version_match.group(1)}"
                return name
        
        return 'Unknown Browser'
    
    @staticmethod
    def _parse_os(user_agent: str) -> str:
        """OS ni aniqlash"""
        os_patterns = {
            r'windows nt': 'Windows',
            r'mac os x': 'macOS',
            r'macintosh': 'macOS',
            r'linux': 'Linux',
            r'android': 'Android',
            r'ios': 'iOS',
            r'iphone': 'iOS',
            r'ipad': 'iPadOS',
            r'cros': 'Chrome OS',
            r'blackberry': 'BlackBerry',
            r'windows phone': 'Windows Phone'
        }
        
        user_agent_lower = user_agent.lower()
        for pattern, name in os_patterns.items():
            if re.search(pattern, user_agent_lower):
                return name
        
        return 'Unknown OS'
    
    @staticmethod
    def _parse_device(user_agent: str, is_mobile: bool, is_desktop: bool) -> str:
        """Device ni aniqlash"""
        if is_mobile:
            device_patterns = {
                r'iphone': 'iPhone',
                r'ipad': 'iPad',
                r'android': 'Android Phone',
                r'blackberry': 'BlackBerry',
                r'windows phone': 'Windows Phone'
            }
            
            user_agent_lower = user_agent.lower()
            for pattern, name in device_patterns.items():
                if re.search(pattern, user_agent_lower):
                    return name
            
            return 'Mobile Device'
        
        elif is_desktop:
            return 'Desktop Computer'
        
        return 'Unknown Device'


class SecurityHelpers:
    """Security helper funksiyalari"""
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Xavfsiz token yaratish"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_api_key(prefix: str = "ak") -> str:
        """API key yaratish"""
        timestamp = int(time.time())
        random_part = secrets.token_hex(16)
        return f"{prefix}_{timestamp}_{random_part}"
    
    @staticmethod
    def create_hash(value: str, salt: str = None) -> str:
        """Salt bilan hash yaratish"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        hash_value = hashlib.pbkdf2_hmac('sha256', value.encode(), salt.encode(), 100000)
        return f"{hash_value.hex()}:{salt}"
    
    @staticmethod
    def verify_hash(value: str, hash_with_salt: str) -> bool:
        """Hashni tekshirish"""
        try:
            hash_part, salt = hash_with_salt.split(':')
            computed_hash = hashlib.pbkdf2_hmac('sha256', value.encode(), salt.encode(), 100000)
            return hmac.compare_digest(hash_part, computed_hash.hex())
        except (ValueError, Exception):
            return False
    
    @staticmethod
    def encrypt_data(data: str, key: str) -> str:
        """Ma'lumotlarni shifrlash (simple base64 - for demonstration)"""
        # In production, use proper encryption like AES
        combined = f"{key}:{data}"
        return base64.b64encode(combined.encode()).decode()
    
    @staticmethod
    def decrypt_data(encrypted_data: str, key: str) -> Optional[str]:
        """Ma'lumotlarni deshifrlash"""
        try:
            decoded = base64.b64decode(encrypted_data.encode()).decode()
            if ':' not in decoded:
                return None
            
            stored_key, data = decoded.split(':', 1)
            if stored_key == key:
                return data
            return None
        except Exception:
            return None
    
    @staticmethod
    def mask_sensitive_data(data: str, show_chars: int = 4) -> str:
        """Sensitive ma'lumotlarni maskalash"""
        if not data or len(data) <= show_chars:
            return '*' * len(data)
        
        return f"{data[:show_chars//2]}{'*' * (len(data) - show_chars)}{data[-show_chars//2:]}"
    
    @staticmethod
    def generate_session_id() -> str:
        """Session ID yaratish"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def calculate_entropy(data: str) -> float:
        """Ma'lumot entropiyasini hisoblash"""
        if not data:
            return 0.0
        
        # Calculate Shannon entropy
        char_counts = {}
        for char in data:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        entropy = 0.0
        data_len = len(data)
        for count in char_counts.values():
            probability = count / data_len
            entropy -= probability * (probability.bit_length() - 1)
        
        return entropy
    
    @staticmethod
    def is_strong_password(password: str) -> Dict[str, Any]:
        """Parol kuchlilik tekshiruvi"""
        result = {
            'is_strong': False,
            'score': 0,
            'issues': [],
            'suggestions': []
        }
        
        if not password:
            result['issues'].append('Password is required')
            return result
        
        score = 0
        
        # Length check
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1
        else:
            result['issues'].append('Password should be at least 8 characters long')
            result['suggestions'].append('Use a longer password (12+ characters recommended)')
        
        # Character variety checks
        if re.search(r'[a-z]', password):
            score += 1
        else:
            result['issues'].append('Password should contain lowercase letters')
        
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            result['issues'].append('Password should contain uppercase letters')
        
        if re.search(r'\d', password):
            score += 1
        else:
            result['issues'].append('Password should contain numbers')
        
        if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            score += 1
        else:
            result['issues'].append('Password should contain special characters')
        
        # Common password check
        common_passwords = ['password', '123456', 'qwerty', 'abc123', 'letmein']
        if password.lower() in common_passwords:
            score -= 3
            result['issues'].append('Password is too common')
            result['suggestions'].append('Use a unique password that is not commonly used')
        
        # Repetition check
        if re.search(r'(.)\1{2,}', password):
            score -= 1
            result['issues'].append('Password contains repeated characters')
        
        # Sequential characters check
        if re.search(r'(abc|bcd|cde|def|123|234|345|456|567|678|789)', password.lower()):
            score -= 1
            result['issues'].append('Password contains sequential characters')
        
        result['score'] = max(0, score)
        result['is_strong'] = result['score'] >= 4 and len(result['issues']) == 0
        
        return result


class SecurityValidators:
    """Security validation funksiyalari"""
    
    @staticmethod
    def validate_file_upload(filename: str, allowed_extensions: List[str] = None,
                           max_size: int = 10 * 1024 * 1024) -> Tuple[bool, Optional[str]]:
        """Fayl upload validation"""
        if not filename:
            return False, "Filename is required"
        
        if allowed_extensions is None:
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.doc', '.docx']
        
        # Check extension
        if not any(filename.lower().endswith(ext.lower()) for ext in allowed_extensions):
            return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        
        # Check for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return False, "Invalid filename"
        
        # Check for null bytes
        if '\x00' in filename:
            return False, "Invalid filename"
        
        # Check filename length
        if len(filename) > 255:
            return False, "Filename too long"
        
        return True, None
    
    @staticmethod
    def validate_url(url: str, allowed_schemes: List[str] = None) -> Tuple[bool, Optional[str]]:
        """URL validation"""
        if not url:
            return False, "URL is required"
        
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            
            if not parsed.scheme:
                return False, "URL must include scheme (http/https)"
            
            if parsed.scheme not in allowed_schemes:
                return False, f"URL scheme must be one of: {', '.join(allowed_schemes)}"
            
            if not parsed.netloc:
                return False, "URL must include domain"
            
            # Check for dangerous schemes
            dangerous_schemes = ['javascript', 'data', 'file', 'ftp']
            if parsed.scheme.lower() in dangerous_schemes:
                return False, "Dangerous URL scheme detected"
            
            return True, None
            
        except Exception as e:
            return False, f"Invalid URL format: {str(e)}"
    
    @staticmethod
    def validate_cors_origin(origin: str, allowed_origins: List[str]) -> bool:
        """CORS origin validation"""
        if not origin or not allowed_origins:
            return False
        
        origin = origin.lower().rstrip('/')
        
        # Exact match
        if origin in [o.lower().rstrip('/') for o in allowed_origins]:
            return True
        
        # Wildcard matching
        for allowed_origin in allowed_origins:
            if allowed_origin == '*':
                return True
            
            if allowed_origin.startswith('https://.'):
                domain = allowed_origin[12:]  # Remove 'https://.'
                if origin.endswith('.' + domain):
                    return True
            
            if allowed_origin.startswith('http://.'):
                domain = allowed_origin[11:]  # Remove 'http://.'
                if origin.endswith('.' + domain):
                    return True
        
        return False


def rate_limit(limit: int, window: int = 60):
    """Rate limiting decorator"""
    def decorator(func):
        func._rate_limit = {'limit': limit, 'window': window}
        return func
    return decorator


def require_auth(required_permissions: List[str] = None):
    """Authentication va authorization decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # In real implementation, check authentication token
            # and required permissions
            if required_permissions:
                # Check permissions logic here
                pass
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_input(validation_rules: Dict[str, Any]):
    """Input validation decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Apply validation rules
            # Implementation would validate input parameters
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_security_event(event_type: str, details: Dict[str, Any] = None):
    """Security event logging decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # Log security event
                logger.info(f"Security event: {event_type} - Function: {func.__name__}")
                if details:
                    logger.info(f"Event details: {details}")
                
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                raise
        return wrapper
    return decorator


class MetricsCollector:
    """Security metrics collector"""
    
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_blocked': 0,
            'authentication_failures': 0,
            'rate_limit_hits': 0,
            'sql_injection_attempts': 0,
            'xss_attempts': 0,
            'unique_ips': set(),
            'top_ips': {},
            'errors': 0
        }
        self._lock = False
    
    def increment(self, metric: str, value: int = 1):
        """Metrikni oshirish"""
        if metric in self.metrics:
            if isinstance(self.metrics[metric], set):
                # For sets (like unique IPs), just track that it was accessed
                pass
            else:
                self.metrics[metric] += value
    
    def add_ip(self, ip: str):
        """IP qo'shish"""
        self.metrics['unique_ips'].add(ip)
    
    def record_error(self, error_type: str = 'general'):
        """Xato qayd etish"""
        self.metrics['errors'] += 1
        if error_type not in self.metrics:
            self.metrics[error_type] = 0
        self.metrics[error_type] += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Metrikalar summary"""
        summary = self.metrics.copy()
        summary['unique_ips_count'] = len(summary['unique_ips'])
        del summary['unique_ips']  # Remove the set from the summary
        return summary


# Global metrics collector
metrics = MetricsCollector()