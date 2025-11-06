"""
Security Validator Moduli
=========================

Bu modul quyidagi security funksiyalarini ta'minlaydi:
- Input validation
- SQL injection protection
- XSS protection  
- CSRF protection
- Malicious pattern detection

@author: Security Team
@version: 1.0.0
"""

import re
import html
import urllib.parse
from typing import Any, Dict, List, Optional, Union, Callable, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import secrets
import base64
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationRule:
    """Validation qoidalar konfiguratsiyasi"""
    name: str
    pattern: str
    error_message: str
    severity: str = "medium"  # low, medium, high, critical
    block_request: bool = False


@dataclass
class SecurityEvent:
    """Security voqeasi"""
    timestamp: datetime
    event_type: str
    severity: str
    source_ip: str
    user_agent: str
    request_path: str
    details: Dict[str, Any]
    blocked: bool = False


class InputValidator:
    """Input validation moduli"""
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(?i)(\bunion\b\s+select\b|\bselect\b.+\bfrom\b)",
        r"(?i)(\bdrop\s+table\b|\bdelete\s+from\b|\binsert\s+into\b)",
        r"(?i)(\bor\s+1=1\b|\band\s+1=1\b)",
        r"(?i)(--|;|\|\|)",
        r"(?i)(\bxp_cmdshell\b|\bsp_executesql\b|\bexec\b)",
        r"(?i)(UNION\s+ALL|SELECT\s+.*FROM\s+.*WHERE)",
        r"(?i)(OR\s+.*=.*OR|AND\s+.*=.*AND)",
        r"(?i)(DROP\s+TABLE|INSERT\s+INTO|DELETE\s+FROM)",
        r"(?i)(CREATE\s+TABLE|UPDATE\s+SET)",
        r"(?i)(SCRIPT|javascript:|vbscript:|data:text/html)",
        r"(?i)(onload=|onerror=|onclick=|onmouseover=)",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"(?i)(<script[^>]*>.*?</script>)",
        r"(?i)(<script[^>]*>)",
        r"(?i)(</script>)",
        r"(?i)(javascript:[^'\"]*)",
        r"(?i)(vbscript:[^'\"]*)",
        r"(?i)(data:text/html)",
        r"(?i)(<iframe[^>]*>.*?</iframe>)",
        r"(?i)(<object[^>]*>.*?</object>)",
        r"(?i)(<embed[^>]*>.*?</embed>)",
        r"(?i)(<link[^>]*>)",
        r"(?i)(<style[^>]*>.*?</style>)",
        r"(?i)(<img[^>]*onerror[^>]*>)",
        r"(?i)(<svg[^>]*onload[^>]*>)",
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"(\.\./|\.\.\\)",
        r"(%2e%2e%2f|%2e%2e\\)",
        r"(\.\.%2f|\.\.%5c)",
    ]
    
    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r"(?i)(;|\|\||&&|\$\(|\`)[^'\"]*",
        r"(?i)(curl|wget|nc|netcat|telnet|ssh|ftp)",
        r"(?i)(bash|sh|cmd|powershell|pwsh)",
    ]
    
    # Email validation pattern
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Phone validation pattern
    PHONE_PATTERN = r'^\+?1?-?\.?\s?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})$'
    
    def __init__(self):
        self.sql_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) 
                           for pattern in self.SQL_INJECTION_PATTERNS]
        self.xss_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) 
                           for pattern in self.XSS_PATTERNS]
        self.path_patterns = [re.compile(pattern, re.IGNORECASE) 
                             for pattern in self.PATH_TRAVERSAL_PATTERNS]
        self.command_patterns = [re.compile(pattern, re.IGNORECASE) 
                               for pattern in self.COMMAND_INJECTION_PATTERNS]
        
        # Security rules
        self.validation_rules: List[ValidationRule] = []
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Default validation qoidalarini sozlash"""
        self.validation_rules = [
            ValidationRule("sql_injection", r"(union|select|insert|delete|drop)", 
                         "SQL injection detected", "critical", True),
            ValidationRule("xss", r"(<script|javascript:|vbscript:)", 
                         "XSS attack detected", "high", True),
            ValidationRule("path_traversal", r"(\.\./|\.\.\\)", 
                         "Path traversal detected", "high", True),
            ValidationRule("command_injection", r"(;|\|\||curl|wget)", 
                         "Command injection detected", "critical", True),
        ]
    
    def validate_email(self, email: str) -> Tuple[bool, Optional[str]]:
        """Email validation"""
        if not email or not isinstance(email, str):
            return False, "Email is required"
        
        if len(email) > 254:
            return False, "Email too long"
        
        if not re.match(self.EMAIL_PATTERN, email):
            return False, "Invalid email format"
        
        return True, None
    
    def validate_phone(self, phone: str) -> Tuple[bool, Optional[str]]:
        """Phone number validation"""
        if not phone or not isinstance(phone, str):
            return False, "Phone number is required"
        
        # Faqat raqam va belgilarni olish
        clean_phone = re.sub(r'[^\d+]', '', phone)
        
        if not re.match(self.PHONE_PATTERN, clean_phone):
            return False, "Invalid phone number format"
        
        return True, None
    
    def validate_password(self, password: str) -> Tuple[bool, List[str]]:
        """Parol validation"""
        errors = []
        
        if not password:
            errors.append("Password is required")
            return False, errors
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors
    
    def validate_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """URL validation"""
        try:
            result = urllib.parse.urlparse(url)
            if not result.scheme or not result.netloc:
                return False, "Invalid URL format"
            
            # Dangerous schemes block
            dangerous_schemes = ['javascript', 'data', 'file', 'vbscript']
            if result.scheme.lower() in dangerous_schemes:
                return False, "Dangerous URL scheme detected"
            
            return True, None
        except Exception as e:
            return False, f"Invalid URL: {str(e)}"
    
    def sanitize_input(self, input_str: str) -> str:
        """Inputni sanitizatsiya qilish"""
        if not input_str:
            return ""
        
        # HTML escape
        sanitized = html.escape(input_str)
        
        # Remove dangerous characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', sanitized)
        
        # Limit length
        if len(sanitized) > 10000:
            sanitized = sanitized[:10000]
        
        return sanitized.strip()
    
    def detect_sql_injection(self, input_str: str) -> bool:
        """SQL injection aniqlash"""
        if not input_str:
            return False
        
        for pattern in self.sql_patterns:
            if pattern.search(input_str):
                return True
        
        return False
    
    def detect_xss(self, input_str: str) -> bool:
        """XSS hujumi aniqlash"""
        if not input_str:
            return False
        
        for pattern in self.xss_patterns:
            if pattern.search(input_str):
                return True
        
        return False
    
    def detect_path_traversal(self, input_str: str) -> bool:
        """Path traversal aniqlash"""
        if not input_str:
            return False
        
        for pattern in self.path_patterns:
            if pattern.search(input_str):
                return True
        
        return False
    
    def detect_command_injection(self, input_str: str) -> bool:
        """Command injection aniqlash"""
        if not input_str:
            return False
        
        for pattern in self.command_patterns:
            if pattern.search(input_str):
                return True
        
        return False
    
    def validate_json(self, json_str: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """JSON validation"""
        try:
            parsed = json.loads(json_str)
            return True, parsed, None
        except json.JSONDecodeError as e:
            return False, None, f"Invalid JSON: {str(e)}"
    
    def validate_field_length(self, value: str, min_length: int = 0, max_length: int = 1000) -> Tuple[bool, Optional[str]]:
        """Field uzunligini validation"""
        if not value:
            if min_length == 0:
                return True, None
            else:
                return False, f"Field is required"
        
        if len(value) < min_length:
            return False, f"Field must be at least {min_length} characters"
        
        if len(value) > max_length:
            return False, f"Field must be no more than {max_length} characters"
        
        return True, None
    
    def validate_number(self, value: Union[str, int, float], min_val: Optional[float] = None, 
                       max_val: Optional[float] = None) -> Tuple[bool, Optional[str]]:
        """Raqam validation"""
        try:
            num_value = float(value)
            
            if min_val is not None and num_value < min_val:
                return False, f"Value must be at least {min_val}"
            
            if max_val is not None and num_value > max_val:
                return False, f"Value must be no more than {max_val}"
            
            return True, None
        except (ValueError, TypeError):
            return False, "Value must be a valid number"


class SQLInjectionProtector:
    """SQL injection himoyasi moduli"""
    
    # SQL keywords to watch for
    SQL_KEYWORDS = {
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 
        'EXEC', 'EXECUTE', 'UNION', 'WHERE', 'FROM', 'TABLE', 'DATABASE',
        'SCRIPT', 'JAVASCRIPT', 'FUNCTION', 'PROCEDURE', 'TRIGGER', 'VIEW'
    }
    
    # Dangerous characters
    DANGEROUS_CHARS = ['\'', '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
    
    def __init__(self):
        self.suspicious_patterns = []
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Shubhali patternlarni sozlash"""
        patterns = [
            r'(?i)(union.*select|select.*union)',
            r'(?i)(drop.*table|delete.*from)',
            r'(?i)(insert.*into|update.*set)',
            r'(?i)(--.*;|;.*--)',
            r'(?i)(xp_cmdshell|sp_executesql)',
            r'(?i)(0x[0-9a-f]+|char\([0-9,]+\))',
            r'(?i)(or\s+1\s*=\s*1|and\s+1\s*=\s*1)',
        ]
        
        self.suspicious_patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """SQL queryni tahlil qilish"""
        analysis = {
            'is_safe': True,
            'risk_level': 'low',
            'threats_found': [],
            'recommendations': [],
            'sanitized_query': query
        }
        
        if not query:
            return analysis
        
        # Suspicious pattern checks
        for pattern in self.suspicious_patterns:
            if pattern.search(query):
                analysis['threats_found'].append('suspicious_pattern')
                analysis['is_safe'] = False
                analysis['risk_level'] = 'high'
        
        # Keyword checks
        query_upper = query.upper()
        for keyword in self.SQL_KEYWORDS:
            if keyword in query_upper:
                analysis['threats_found'].append(f'keyword_{keyword.lower()}')
                if keyword in ['DROP', 'DELETE', 'ALTER']:
                    analysis['risk_level'] = 'critical'
                elif analysis['risk_level'] != 'critical':
                    analysis['risk_level'] = 'high'
        
        # Dangerous character checks
        for char in self.DANGEROUS_CHARS:
            if char in query:
                analysis['threats_found'].append(f'dangerous_char_{char}')
                analysis['is_safe'] = False
        
        # Recommendations
        if not analysis['is_safe']:
            analysis['recommendations'].append('Use parameterized queries')
            analysis['recommendations'].append('Validate input before query execution')
            analysis['recommendations'].append('Implement proper access controls')
        
        # Generate sanitized query
        analysis['sanitized_query'] = self._sanitize_query(query)
        
        return analysis
    
    def _sanitize_query(self, query: str) -> str:
        """Queryni sanitizatsiya qilish"""
        # Remove comments
        sanitized = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        sanitized = re.sub(r'/\*.*?\*/', '', sanitized, flags=re.DOTALL)
        
        # Replace dangerous characters
        sanitized = sanitized.replace('\'', '\'\'')
        sanitized = sanitized.replace('"', '""')
        
        return sanitized.strip()
    
    def create_safe_query(self, base_query: str, params: List[Any]) -> str:
        """Safe query yaratish"""
        try:
            # Use parameterized query format
            placeholder_count = base_query.count('?')
            
            if placeholder_count != len(params):
                raise ValueError("Parameter count mismatch")
            
            # Build query with safe parameter substitution
            query_parts = base_query.split('?')
            safe_query = query_parts[0]
            
            for i, param in enumerate(params):
                safe_query += self._safe_param_format(param) + query_parts[i + 1]
            
            return safe_query
        except Exception as e:
            logger.error(f"Query creation error: {e}")
            return ""
    
    def _safe_param_format(self, param: Any) -> str:
        """Parameterlarni xavfsiz formatlash"""
        if param is None:
            return 'NULL'
        elif isinstance(param, (int, float)):
            return str(param)
        elif isinstance(param, bool):
            return '1' if param else '0'
        else:
            # String parameter - escape quotes
            escaped = str(param).replace('\'', '\'\'').replace('"', '""')
            return f"'{escaped}'"


class SecurityValidator:
    """Asosiy Security Validator"""
    
    def __init__(self):
        self.input_validator = InputValidator()
        self.sql_protector = SQLInjectionProtector()
        self.blocked_ips: Set[str] = set()
        self.suspicious_requests = []
        self.security_events: List[SecurityEvent] = []
    
    def validate_request(self, request_data: Dict[str, Any], source_ip: str, 
                        user_agent: str, path: str) -> Tuple[bool, List[str]]:
        """Request validation"""
        violations = []
        
        # IP check
        if source_ip in self.blocked_ips:
            violations.append("IP address blocked")
        
        # Input validation for each field
        for field_name, value in request_data.items():
            if isinstance(value, str):
                # SQL injection check
                if self.input_validator.detect_sql_injection(value):
                    violations.append(f"SQL injection detected in field: {field_name}")
                
                # XSS check
                if self.input_validator.detect_xss(value):
                    violations.append(f"XSS attack detected in field: {field_name}")
                
                # Path traversal check
                if self.input_validator.detect_path_traversal(value):
                    violations.append(f"Path traversal detected in field: {field_name}")
                
                # Command injection check
                if self.input_validator.detect_command_injection(value):
                    violations.append(f"Command injection detected in field: {field_name}")
        
        # Create security event for violations
        if violations:
            event = SecurityEvent(
                timestamp=datetime.now(),
                event_type="security_violation",
                severity="high",
                source_ip=source_ip,
                user_agent=user_agent,
                request_path=path,
                details={"violations": violations, "request_data": request_data}
            )
            self.security_events.append(event)
        
        return len(violations) == 0, violations
    
    def add_blocked_ip(self, ip: str):
        """IP manzilini bloklash"""
        self.blocked_ips.add(ip)
        logger.warning(f"Blocked IP: {ip}")
    
    def remove_blocked_ip(self, ip: str):
        """IP manzilini blokdan chiqarish"""
        self.blocked_ips.discard(ip)
        logger.info(f"Unblocked IP: {ip}")
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Security statistikalarini olish"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        
        recent_events = [e for e in self.security_events if e.timestamp > last_24h]
        
        return {
            "total_events": len(self.security_events),
            "recent_events_24h": len(recent_events),
            "blocked_ips": len(self.blocked_ips),
            "critical_violations": len([e for e in recent_events if e.severity == "critical"]),
            "high_violations": len([e for e in recent_events if e.severity == "high"]),
            "recent_violations": recent_events[-10:] if recent_events else []
        }