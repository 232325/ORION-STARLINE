"""
Data Protection Moduli
=====================

Bu modul quyidagi data protection funksiyalarini ta'minlaydi:
- Data encryption
- PII protection
- Secure data transmission
- Data anonymization
- GDPR/CCPA compliance
- Data retention policies

@author: Security Team
@version: 1.0.0
"""

import os
import hashlib
import secrets
import json
import base64
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class PIIField:
    """PII field ma'lumotlari"""
    field_name: str
    field_type: str  # email, phone, ssn, etc.
    sensitivity_level: str  # low, medium, high, critical
    encryption_required: bool = True
    anonymization_required: bool = True
    retention_period: Optional[int] = None  # days
    compliance_regulations: List[str] = field(default_factory=list)


@dataclass
class DataRetentionPolicy:
    """Data retention policy"""
    data_type: str
    retention_period_days: int
    auto_delete: bool = True
    audit_required: bool = True
    legal_hold_exception: bool = False


@dataclass
class ComplianceRequirement:
    """Compliance talablar"""
    regulation: str  # GDPR, CCPA, HIPAA, etc.
    requirement_type: str  # consent, right_to_delete, data_portability, etc.
    description: str
    mandatory: bool = True


class DataProtector:
    """Data encryption va protection moduli"""
    
    def __init__(self, master_key: str = None):
        self.master_key = master_key or self._generate_master_key()
        self.cipher_suite = self._create_cipher()
        self.encryption_keys: Dict[str, bytes] = {}
    
    def _generate_master_key(self) -> str:
        """Master key yaratish"""
        return base64.urlsafe_b64encode(os.urandom(32)).decode()
    
    def _create_cipher(self) -> Fernet:
        """Cipher yaratish"""
        # Derive key from master key
        salt = b'security_salt_2025'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)
    
    def encrypt_data(self, data: str, key_id: str = None) -> str:
        """Ma'lumotlarni shifrlash"""
        if key_id and key_id in self.encryption_keys:
            # Use specific key
            cipher = Fernet(base64.urlsafe_b64encode(self.encryption_keys[key_id]))
            encrypted = cipher.encrypt(data.encode())
        else:
            # Use master key
            encrypted = self.cipher_suite.encrypt(data.encode())
        
        return base64.b64encode(encrypted).decode()
    
    def decrypt_data(self, encrypted_data: str, key_id: str = None) -> Optional[str]:
        """Shifrlangan ma'lumotlarni deshifrlash"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            
            if key_id and key_id in self.encryption_keys:
                # Use specific key
                cipher = Fernet(base64.urlsafe_b64encode(self.encryption_keys[key_id]))
                decrypted = cipher.decrypt(encrypted_bytes)
            else:
                # Use master key
                decrypted = self.cipher_suite.decrypt(encrypted_bytes)
            
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
    
    def encrypt_object(self, obj: Dict[str, Any], key_id: str = None) -> str:
        """Objectni shifrlash"""
        json_data = json.dumps(obj, default=str)
        return self.encrypt_data(json_data, key_id)
    
    def decrypt_object(self, encrypted_obj: str, key_id: str = None) -> Optional[Dict[str, Any]]:
        """Shifrlangan objectni deshifrlash"""
        decrypted_data = self.decrypt_data(encrypted_obj, key_id)
        if decrypted_data:
            try:
                return json.loads(decrypted_data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decryption error: {e}")
        return None
    
    def create_field_encryption_key(self, field_name: str) -> str:
        """Field uchun encryption key yaratish"""
        key = os.urandom(32)
        self.encryption_keys[field_name] = key
        return base64.urlsafe_b64encode(key).decode()
    
    def hash_sensitive_data(self, data: str, salt: str = None) -> str:
        """Sensitive ma'lumotlarni hash qilish"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # salted hash
        salted_data = data + salt
        hash_value = hashlib.sha256(salted_data.encode()).hexdigest()
        
        return f"{hash_value}:{salt}"


class PIIProtector:
    """PII protection moduli"""
    
    # PII patterns
    PII_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        'passport': r'\b[A-Z]{1,2}[0-9]{6,9}\b',
        'driver_license': r'\b[A-Z]{1,2}[0-9]{6,8}\b'
    }
    
    def __init__(self):
        self.pii_patterns = {}
        for pii_type, pattern in self.PII_PATTERNS.items():
            self.pii_patterns[pii_type] = re.compile(pattern, re.IGNORECASE)
        
        # Define standard PII fields
        self.standard_pii_fields = {
            'email': PIIField('email', 'email', 'high', True, True, 2555, ['GDPR', 'CCPA']),  # 7 years
            'phone': PIIField('phone', 'phone', 'medium', True, True, 1095, ['GDPR', 'CCPA']),  # 3 years
            'ssn': PIIField('ssn', 'ssn', 'critical', True, True, None, ['GDPR', 'CCPA', 'HIPAA']),
            'first_name': PIIField('first_name', 'name', 'medium', True, True, 1095, ['GDPR', 'CCPA']),
            'last_name': PIIField('last_name', 'name', 'medium', True, True, 1095, ['GDPR', 'CCPA']),
            'date_of_birth': PIIField('date_of_birth', 'date', 'high', True, True, None, ['GDPR', 'CCPA']),
            'address': PIIField('address', 'address', 'medium', True, True, 1095, ['GDPR', 'CCPA']),
            'passport_number': PIIField('passport_number', 'passport', 'critical', True, True, None, ['GDPR']),
            'driver_license': PIIField('driver_license', 'id', 'high', True, True, None, ['GDPR', 'CCPA'])
        }
    
    def detect_pii(self, data: str) -> List[Dict[str, Any]]:
        """PII detection"""
        detected_pii = []
        
        if not data:
            return detected_pii
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = pattern.findall(data)
            for match in matches:
                detected_pii.append({
                    'type': pii_type,
                    'value': match,
                    'start_position': data.find(match),
                    'end_position': data.find(match) + len(match)
                })
        
        return detected_pii
    
    def mask_pii(self, data: str, mask_char: str = '*') -> str:
        """PII masking"""
        if not data:
            return data
        
        masked_data = data
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = list(pattern.finditer(data))
            for match in matches:
                start, end = match.span()
                masked_data = masked_data[:start] + mask_char * (end - start) + masked_data[end:]
        
        return masked_data
    
    def anonymize_pii(self, pii_type: str, value: str) -> str:
        """PII anonymization"""
        if pii_type == 'email':
            # Keep domain, mask local part
            if '@' in value:
                local, domain = value.split('@', 1)
                if len(local) <= 2:
                    return f"**@{domain}"
                else:
                    return f"{local[0]}**@{domain}"
        
        elif pii_type == 'phone':
            # Keep last 4 digits
            digits = re.sub(r'\D', '', value)
            if len(digits) >= 4:
                return f"***-***-{digits[-4:]}"
        
        elif pii_type == 'ssn':
            # Keep last 4 digits
            digits = re.sub(r'\D', '', value)
            if len(digits) >= 4:
                return f"***-**-{digits[-4:]}"
        
        elif pii_type == 'credit_card':
            # Keep last 4 digits
            digits = re.sub(r'\D', '', value)
            if len(digits) >= 4:
                return f"****-****-****-{digits[-4:]}"
        
        elif pii_type == 'name':
            # Mask middle of name
            parts = value.split()
            masked_parts = []
            for part in parts:
                if len(part) <= 2:
                    masked_parts.append(part)
                else:
                    masked_parts.append(f"{part[0]}{'*' * (len(part) - 2)}{part[-1]}")
            return ' '.join(masked_parts)
        
        # Default masking
        if len(value) <= 4:
            return '*' * len(value)
        else:
            return f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"
    
    def classify_data_sensitivity(self, data: str) -> Dict[str, Any]:
        """Data sensitivity classification"""
        classification = {
            'sensitivity_level': 'low',
            'pii_types': [],
            'confidence_score': 0.0
        }
        
        detected_pii = self.detect_pii(data)
        if not detected_pii:
            return classification
        
        # Calculate sensitivity score
        sensitivity_scores = {
            'email': 0.6,
            'phone': 0.5,
            'ssn': 1.0,
            'credit_card': 0.9,
            'passport': 0.95,
            'driver_license': 0.8
        }
        
        total_score = 0
        for pii in detected_pii:
            pii_type = pii['type']
            if pii_type in sensitivity_scores:
                total_score += sensitivity_scores[pii_type]
                classification['pii_types'].append(pii_type)
        
        classification['confidence_score'] = min(total_score, 1.0)
        
        # Determine overall sensitivity
        if total_score >= 0.8:
            classification['sensitivity_level'] = 'critical'
        elif total_score >= 0.5:
            classification['sensitivity_level'] = 'high'
        elif total_score >= 0.2:
            classification['sensitivity_level'] = 'medium'
        
        return classification
    
    def validate_pii_handling(self, data: Dict[str, Any], action: str) -> Tuple[bool, List[str]]:
        """PII handling validation"""
        violations = []
        
        for field_name, field_value in data.items():
            if isinstance(field_value, str):
                # Check if field contains PII
                detected_pii = self.detect_pii(field_value)
                
                for pii in detected_pii:
                    pii_type = pii['type']
                    
                    if field_name in self.standard_pii_fields:
                        pii_field = self.standard_pii_fields[field_name]
                        
                        # Check encryption requirement
                        if pii_field.encryption_required and action in ['store', 'transmit']:
                            # In real implementation, check if data is encrypted
                            pass
                        
                        # Check anonymization requirement
                        if pii_field.anonymization_required and action in ['display', 'log']:
                            if field_value == pii['value']:  # Not anonymized
                                violations.append(f"Field '{field_name}' must be anonymized for {action}")
        
        return len(violations) == 0, violations


class DataAnonymizer:
    """Data anonymization moduli"""
    
    def __init__(self):
        self.anonymization_methods = {
            'masking': self._mask_anonymization,
            'pseudonymization': self._pseudonymize,
            'generalization': self._generalize,
            'noise': self._add_noise,
            'shuffling': self._shuffle
        }
    
    def anonymize_dataset(self, dataset: List[Dict[str, Any]], 
                         anonymization_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Dataset anonymization"""
        anonymized_data = []
        
        for record in dataset:
            anonymized_record = self.anonymize_record(record, anonymization_config)
            anonymized_data.append(anonymized_record)
        
        return anonymized_data
    
    def anonymize_record(self, record: Dict[str, Any], 
                        config: Dict[str, Any]) -> Dict[str, Any]:
        """Record anonymization"""
        anonymized = {}
        
        for field_name, field_value in record.items():
            if field_name in config:
                method = config[field_name]['method']
                params = config[field_name].get('params', {})
                
                if method in self.anonymization_methods:
                    anonymized[field_name] = self.anonymization_methods[method](
                        field_value, **params
                    )
                else:
                    anonymized[field_name] = field_value
            else:
                # Default to masking for unmapped fields
                anonymized[field_name] = self._mask_anonymization(field_value)
        
        return anonymized
    
    def _mask_anonymization(self, value: Any, mask_char: str = '*', 
                           keep_start: int = 2, keep_end: int = 2) -> Any:
        """Masking-based anonymization"""
        if not isinstance(value, str):
            return value
        
        if len(value) <= keep_start + keep_end:
            return mask_char * len(value)
        
        return f"{value[:keep_start]}{mask_char * (len(value) - keep_start - keep_end)}{value[-keep_end:]}"
    
    def _pseudonymize(self, value: Any, salt: str = None) -> str:
        """Pseudonymization"""
        if not isinstance(value, str):
            value = str(value)
        
        if salt is None:
            salt = secrets.token_hex(16)
        
        hash_obj = hashlib.sha256((value + salt).encode())
        return hash_obj.hexdigest()[:16]
    
    def _generalize(self, value: Any, level: int = 1) -> Any:
        """Generalization-based anonymization"""
        if isinstance(value, datetime):
            if level == 1:
                return value.strftime('%Y-%m')
            elif level == 2:
                return value.strftime('%Y')
            elif level >= 3:
                return str(value.year // 10 * 10) + 's'
        
        elif isinstance(value, (int, float)):
            if level == 1:
                return round(value, -1)  # Round to nearest 10
            elif level == 2:
                return round(value, -2)  # Round to nearest 100
        
        elif isinstance(value, str) and re.match(r'\d', value):
            # Numeric string generalization
            digits = re.sub(r'\D', '', value)
            if len(digits) > level:
                return value[:len(value)-level] + '*' * level
        
        return value
    
    def _add_noise(self, value: Any, noise_level: float = 0.1) -> Any:
        """Noise-based anonymization"""
        if isinstance(value, (int, float)):
            noise = secrets.randbelow(int(noise_level * abs(value) * 100)) / 100
            if secrets.randbelow(2):
                return value + noise
            else:
                return value - noise
        
        return value
    
    def _shuffle(self, value: Any) -> Any:
        """Shuffle-based anonymization for lists"""
        if isinstance(value, list):
            shuffled = value.copy()
            secrets.SystemRandom().shuffle(shuffled)
            return shuffled
        
        return value


class ComplianceManager:
    """GDPR/CCPA Compliance Manager"""
    
    def __init__(self):
        self.compliance_requirements = {
            'GDPR': {
                'consent': ComplianceRequirement('GDPR', 'consent', 'Explicit consent required for data processing', True),
                'right_to_delete': ComplianceRequirement('GDPR', 'right_to_delete', 'Right to be forgotten', True),
                'data_portability': ComplianceRequirement('GDPR', 'data_portability', 'Data portability right', True),
                'data_minimization': ComplianceRequirement('GDPR', 'data_minimization', 'Only collect necessary data', True),
                'purpose_limitation': ComplianceRequirement('GDPR', 'purpose_limitation', 'Data used only for stated purposes', True)
            },
            'CCPA': {
                'right_to_know': ComplianceRequirement('CCPA', 'right_to_know', 'Right to know what data is collected', True),
                'right_to_delete': ComplianceRequirement('CCPA', 'right_to_delete', 'Right to delete personal information', True),
                'right_to_opt_out': ComplianceRequirement('CCPA', 'right_to_opt_out', 'Right to opt out of data sale', True),
                'non_discrimination': ComplianceRequirement('CCPA', 'non_discrimination', 'No discrimination for exercising rights', True)
            },
            'HIPAA': {
                'data_encryption': ComplianceRequirement('HIPAA', 'data_encryption', 'PHI must be encrypted', True),
                'access_controls': ComplianceRequirement('HIPAA', 'access_controls', 'Strict access controls required', True),
                'audit_logs': ComplianceRequirement('HIPAA', 'audit_logs', 'Comprehensive audit logging required', True)
            }
        }
        
        self.data_subject_requests: List[Dict[str, Any]] = []
        self.consent_records: List[Dict[str, Any]] = []
    
    def validate_consent(self, user_id: str, purpose: str, 
                        regulation: str = 'GDPR') -> bool:
        """Consent validation"""
        # Check if valid consent exists
        for record in self.consent_records:
            if (record['user_id'] == user_id and 
                record['purpose'] == purpose and
                record['regulation'] == regulation and
                record['consented'] and
                record['expires_at'] > datetime.now()):
                return True
        
        return False
    
    def record_consent(self, user_id: str, purpose: str, 
                      consent_given: bool, regulation: str = 'GDPR',
                      additional_info: Dict[str, Any] = None) -> str:
        """Consent record qilish"""
        request_id = f"consent_{secrets.token_hex(8)}"
        
        consent_record = {
            'request_id': request_id,
            'user_id': user_id,
            'purpose': purpose,
            'regulation': regulation,
            'consented': consent_given,
            'timestamp': datetime.now(),
            'expires_at': datetime.now() + timedelta(days=365),  # 1 year
            'additional_info': additional_info or {}
        }
        
        self.consent_records.append(consent_record)
        
        logger.info(f"Consent recorded: {request_id} - {user_id} - {purpose}")
        
        return request_id
    
    def process_data_subject_request(self, user_id: str, request_type: str,
                                   regulation: str = 'GDPR') -> str:
        """Data subject request processing"""
        request_id = f"dsr_{secrets.token_hex(8)}"
        
        dsr = {
            'request_id': request_id,
            'user_id': user_id,
            'request_type': request_type,
            'regulation': regulation,
            'status': 'pending',
            'timestamp': datetime.now(),
            'processed_at': None,
            'completion_deadline': datetime.now() + timedelta(days=30),
            'result': None
        }
        
        self.data_subject_requests.append(dsr)
        
        logger.info(f"DSR initiated: {request_id} - {user_id} - {request_type}")
        
        return request_id
    
    def get_compliance_report(self, regulation: str = None) -> Dict[str, Any]:
        """Compliance report olish"""
        total_records = len(self.consent_records)
        active_consents = len([r for r in self.consent_records if r['expires_at'] > datetime.now()])
        
        dsr_by_type = {}
        for dsr in self.data_subject_requests:
            request_type = dsr['request_type']
            dsr_by_type[request_type] = dsr_by_type.get(request_type, 0) + 1
        
        return {
            'compliance_summary': {
                'regulation': regulation or 'All',
                'total_consents': total_records,
                'active_consents': active_consents,
                'total_dsr_requests': len(self.data_subject_requests)
            },
            'consent_statistics': {
                'by_purpose': self._count_by_field('purpose', self.consent_records),
                'by_regulation': self._count_by_field('regulation', self.consent_records),
                'consent_rate': active_consents / max(total_records, 1)
            },
            'dsr_statistics': {
                'by_type': dsr_by_type,
                'pending_requests': len([dsr for dsr in self.data_subject_requests if dsr['status'] == 'pending']),
                'overdue_requests': len([dsr for dsr in self.data_subject_requests 
                                       if dsr['status'] == 'pending' and dsr['completion_deadline'] < datetime.now()])
            }
        }
    
    def _count_by_field(self, field: str, records: List[Dict]) -> Dict[str, int]:
        """Field bo'yicha hisoblash"""
        counts = {}
        for record in records:
            value = record.get(field, 'unknown')
            counts[value] = counts.get(value, 0) + 1
        return counts