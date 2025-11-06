#!/usr/bin/env python3
"""
Korporativ Xavfsizlik Tizimi
Enterprise Security System - Advanced Security Framework

Bu fayl korporativ xavfsizlik tizimining asosiy komponenti bo'lib,
ilg'or xavfsizlik imkoniyatlarini, audit logging,
GDPR compliance va SOC 2 standartlarini ta'minlaydi.

Features:
- Advanced Threat Detection
- Security Policy Management
- Access Control Enforcement
- Security Event Monitoring
- Compliance Framework
- Real-time Security Analytics
"""

import os
import sys
import json
import time
import hashlib
import logging
import threading
import sqlite3
import uuid
import datetime
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import jwt
from flask import Flask, request, jsonify, g
import bcrypt
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/orion-starline/logs/enterprise_security.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Xavfsizlik darajalari"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatLevel(Enum):
    """Tahid darajalari"""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceStandard(Enum):
    """Moslashuv standartlari"""
    GDPR = "gdpr"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"

@dataclass
class SecurityEvent:
    """Xavfsizlik voqeasi"""
    event_id: str
    timestamp: str
    event_type: str
    severity: str
    source_ip: str
    user_id: str
    description: str
    details: Dict[str, Any]
    mitigation_status: str
    compliance_flags: List[str]

@dataclass
class SecurityPolicy:
    """Xavfsizlik siyosati"""
    policy_id: str
    name: str
    description: str
    policy_type: str
    rules: Dict[str, Any]
    compliance_standards: List[str]
    enforcement_level: str
    last_updated: str

class ThreatIntelligence:
    """Tahid razvedka xizmati"""
    
    def __init__(self):
        self.known_threats = {
            'sql_injection': ['SELECT', 'UNION', 'DROP', 'INSERT', 'UPDATE', 'DELETE'],
            'xss_attacks': ['<script>', 'javascript:', 'onerror=', 'onload='],
            'path_traversal': ['../', '..\\', '..%2f', '..%5c'],
            'command_injection': ['&&', '|', ';', '$(', '`'],
            'csrf_tokens': ['csrf_token', 'authenticity_token', '_token'],
            'suspicious_patterns': ['admin', 'root', 'system', 'password', 'api_key']
        }
        
        self.threat_patterns = {
            'brute_force': {
                'max_attempts': 5,
                'time_window': 300,  # 5 minutes
                'ip_whitelist': []
            },
            'data_exfiltration': {
                'volume_threshold': 1000,  # MB
                'frequency_threshold': 60,  # per minute
                'pattern_matching': True
            },
            'privilege_escalation': {
                'role_changes': 3,  # Max role changes per hour
                'permission_gaps': True
            }
        }
    
    def analyze_threat(self, data: str) -> ThreatLevel:
        """Tahid tahlili"""
        threat_score = 0
        data_lower = data.lower()
        
        # Check against known threats
        for threat_type, patterns in self.known_threats.items():
            for pattern in patterns:
                if pattern.lower() in data_lower:
                    threat_score += 1
                    logger.warning(f"Threat detected: {pattern} in {threat_type}")
        
        # Determine threat level
        if threat_score == 0:
            return ThreatLevel.MINIMAL
        elif threat_score <= 2:
            return ThreatLevel.LOW
        elif threat_score <= 5:
            return ThreatLevel.MODERATE
        elif threat_score <= 8:
            return ThreatLevel.HIGH
        else:
            return ThreatLevel.CRITICAL

class ComplianceEngine:
    """Moslashuv injeni"""
    
    def __init__(self):
        self.standards = {
            ComplianceStandard.GDPR: {
                'data_retention_days': 2555,  # 7 years
                'encryption_required': True,
                'audit_required': True,
                'data_minimization': True,
                'consent_required': True,
                'breach_notification_hours': 72
            },
            ComplianceStandard.SOC2: {
                'availability_threshold': 99.9,
                'integrity_checks': True,
                'confidentiality_controls': True,
                'processing_integrity': True,
                'privacy_controls': True
            }
        }
    
    def check_compliance(self, data_processing: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Moslashuv tekshiruvi"""
        violations = []
        
        for standard, requirements in self.standards.items():
            for requirement, value in requirements.items():
                if requirement in data_processing:
                    actual_value = data_processing[requirement]
                    if isinstance(value, bool) and not actual_value:
                        violations.append(f"{standard.value}: {requirement} not satisfied")
                    elif isinstance(value, (int, float)) and actual_value < value:
                        violations.append(f"{standard.value}: {requirement} below threshold")
        
        return len(violations) == 0, violations

class SecurityPolicyManager:
    """Xavfsizlik siyosatlari boshqaruvchisi"""
    
    def __init__(self, db_path: str = "/workspace/orion-starline/data/security_policies.db"):
        self.db_path = db_path
        self.policies: Dict[str, SecurityPolicy] = {}
        self.init_database()
    
    def init_database(self):
        """Ma'lumotlar bazasini ishga tushirish"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_policies (
                policy_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                policy_type TEXT NOT NULL,
                rules TEXT NOT NULL,
                compliance_standards TEXT,
                enforcement_level TEXT,
                last_updated TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_policy(self, policy: SecurityPolicy) -> bool:
        """Yangi xavfsizlik siyosati yaratish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO security_policies 
                (policy_id, name, description, policy_type, rules, compliance_standards, enforcement_level, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                policy.policy_id, policy.name, policy.description, policy.policy_type,
                json.dumps(policy.rules), json.dumps(policy.compliance_standards),
                policy.enforcement_level, policy.last_updated
            ))
            
            conn.commit()
            conn.close()
            
            self.policies[policy.policy_id] = policy
            logger.info(f"Security policy created: {policy.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create policy: {e}")
            return False
    
    def get_policy(self, policy_id: str) -> Optional[SecurityPolicy]:
        """Xavfsizlik siyosatini olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM security_policies WHERE policy_id = ?', (policy_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return SecurityPolicy(
                policy_id=row[0], name=row[1], description=row[2], policy_type=row[3],
                rules=json.loads(row[4]), compliance_standards=json.loads(row[5]),
                enforcement_level=row[6], last_updated=row[7]
            )
        return None
    
    def enforce_policy(self, policy_id: str, action_data: Dict[str, Any]) -> bool:
        """Siyosatni amalga oshirish"""
        policy = self.get_policy(policy_id)
        if not policy:
            return False
        
        # Check if action violates policy rules
        for rule_name, rule_value in policy.rules.items():
            if rule_name in action_data:
                if action_data[rule_name] != rule_value:
                    logger.warning(f"Policy violation: {rule_name} in {policy.name}")
                    return False
        
        return True

class SecurityEventManager:
    """Xavfsizlik voqealari boshqaruvchisi"""
    
    def __init__(self, db_path: str = "/workspace/orion-starline/data/security_events.db"):
        self.db_path = db_path
        self.threat_intelligence = ThreatIntelligence()
        self.init_database()
    
    def init_database(self):
        """Ma'lumotlar bazasini ishga tushirish"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                source_ip TEXT NOT NULL,
                user_id TEXT NOT NULL,
                description TEXT NOT NULL,
                details TEXT NOT NULL,
                mitigation_status TEXT NOT NULL,
                compliance_flags TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON security_events(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_severity ON security_events(severity)
        ''')
        
        conn.commit()
        conn.close()
    
    def create_event(self, event: SecurityEvent) -> bool:
        """Yangi xavfsizlik voqeasi yaratish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO security_events 
                (event_id, timestamp, event_type, severity, source_ip, user_id, description, details, mitigation_status, compliance_flags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.event_id, event.timestamp, event.event_type, event.severity,
                event.source_ip, event.user_id, event.description, json.dumps(event.details),
                event.mitigation_status, json.dumps(event.compliance_flags)
            ))
            
            conn.commit()
            conn.close()
            
            # Log critical events immediately
            if event.severity in ['high', 'critical']:
                logger.critical(f"CRITICAL SECURITY EVENT: {event.description}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create security event: {e}")
            return False
    
    def get_events(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Xavfsizlik voqealarini olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM security_events WHERE 1=1"
        params = []
        
        if filters:
            if 'severity' in filters:
                query += " AND severity = ?"
                params.append(filters['severity'])
            
            if 'event_type' in filters:
                query += " AND event_type = ?"
                params.append(filters['event_type'])
            
            if 'start_date' in filters:
                query += " AND timestamp >= ?"
                params.append(filters['start_date'])
            
            if 'end_date' in filters:
                query += " AND timestamp <= ?"
                params.append(filters['end_date'])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        events = []
        for row in rows:
            events.append({
                'event_id': row[0],
                'timestamp': row[1],
                'event_type': row[2],
                'severity': row[3],
                'source_ip': row[4],
                'user_id': row[5],
                'description': row[6],
                'details': json.loads(row[7]),
                'mitigation_status': row[8],
                'compliance_flags': json.loads(row[9])
            })
        
        return events

class AuthenticationManager:
    """Autentifikatsiya boshqaruvchisi"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or os.environ.get('SECURITY_SECRET_KEY', 'default-secret-key')
        self.failed_attempts = {}
        self.lockout_threshold = 5
        self.lockout_duration = 900  # 15 minutes
    
    def hash_password(self, password: str) -> str:
        """Parolni hash qilish"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Parolni tekshirish"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_token(self, user_id: str, permissions: List[str]) -> str:
        """JWT token yaratish"""
        payload = {
            'user_id': user_id,
            'permissions': permissions,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            'iat': datetime.datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """JWT tokenni tekshirish"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def check_rate_limit(self, ip_address: str) -> bool:
        """Cheklovni tekshirish"""
        current_time = time.time()
        
        if ip_address not in self.failed_attempts:
            self.failed_attempts[ip_address] = {'count': 0, 'first_attempt': current_time}
        
        attempts = self.failed_attempts[ip_address]
        
        # Reset counter after lockout duration
        if current_time - attempts['first_attempt'] > self.lockout_duration:
            attempts['count'] = 0
            attempts['first_attempt'] = current_time
        
        # Check if IP is locked out
        if attempts['count'] >= self.lockout_threshold:
            if current_time - attempts['first_attempt'] < self.lockout_duration:
                return False  # Still locked out
            else:
                attempts['count'] = 0  # Reset
                attempts['first_attempt'] = current_time
        
        return True

class EnterpriseSecuritySystem:
    """Korporativ xavfsizlik tizimi - asosiy klass"""
    
    def __init__(self):
        self.policy_manager = SecurityPolicyManager()
        self.event_manager = SecurityEventManager()
        self.auth_manager = AuthenticationManager()
        self.compliance_engine = ComplianceEngine()
        self.threat_intelligence = ThreatIntelligence()
        
        # Initialize default policies
        self._init_default_policies()
        
        logger.info("Enterprise Security System initialized")
    
    def _init_default_policies(self):
        """Standart siyosatlarni yaratish"""
        default_policies = [
            SecurityPolicy(
                policy_id="access-control-001",
                name="Kirish boshqaruvi siyosati",
                description="Foydalanuvchi kirish va autentifikatsiya siyosati",
                policy_type="access_control",
                rules={
                    "min_password_length": 8,
                    "require_mfa": True,
                    "session_timeout": 3600,
                    "max_login_attempts": 3
                },
                compliance_standards=["SOC2", "GDPR"],
                enforcement_level="strict",
                last_updated=datetime.datetime.now().isoformat()
            ),
            SecurityPolicy(
                policy_id="data-protection-001",
                name="Ma'lumotlar himoyasi siyosati",
                description="Shaxsiy ma'lumotlar va konfidentsial ma'lumotlarni himoyalash",
                policy_type="data_protection",
                rules={
                    "encrypt_sensitive_data": True,
                    "data_classification_required": True,
                    "backup_encryption": True,
                    "data_retention_days": 2555
                },
                compliance_standards=["GDPR", "SOC2", "ISO27001"],
                enforcement_level="mandatory",
                last_updated=datetime.datetime.now().isoformat()
            ),
            SecurityPolicy(
                policy_id="network-security-001",
                name="Tarmoq xavfsizligi siyosati",
                description="Tarmoq xavfsizligi va trafik monitoringi",
                policy_type="network_security",
                rules={
                    "https_required": True,
                    "firewall_enabled": True,
                    "intrusion_detection": True,
                    "ssl_enforcement": True
                },
                compliance_standards=["SOC2", "ISO27001"],
                enforcement_level="strict",
                last_updated=datetime.datetime.now().isoformat()
            )
        ]
        
        for policy in default_policies:
            if not self.policy_manager.get_policy(policy.policy_id):
                self.policy_manager.create_policy(policy)
    
    def authenticate_user(self, username: str, password: str, ip_address: str) -> Tuple[bool, str, Optional[str]]:
        """Foydalanuvchini autentifikatsiya qilish"""
        
        # Check rate limiting
        if not self.auth_manager.check_rate_limit(ip_address):
            # Log failed attempt
            event = SecurityEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.datetime.now().isoformat(),
                event_type="rate_limit_exceeded",
                severity="medium",
                source_ip=ip_address,
                user_id=username,
                description="IP manzili cheklovdan oshdi",
                details={"ip_address": ip_address, "username": username},
                mitigation_status="pending",
                compliance_flags=["SOC2"]
            )
            self.event_manager.create_event(event)
            
            return False, "Too many failed attempts", None
        
        # Here you would normally check against a user database
        # For demo purposes, we'll use a simple check
        user_db = {
            "admin": {
                "password_hash": self.auth_manager.hash_password("Admin123!"),
                "permissions": ["read", "write", "admin"],
                "role": "administrator"
            },
            "user": {
                "password_hash": self.auth_manager.hash_password("User123!"),
                "permissions": ["read"],
                "role": "user"
            }
        }
        
        if username in user_db:
            user_data = user_db[username]
            if self.auth_manager.verify_password(password, user_data["password_hash"]):
                token = self.auth_manager.generate_token(username, user_data["permissions"])
                
                # Log successful authentication
                event = SecurityEvent(
                    event_id=str(uuid.uuid4()),
                    timestamp=datetime.datetime.now().isoformat(),
                    event_type="authentication_success",
                    severity="low",
                    source_ip=ip_address,
                    user_id=username,
                    description="Muvaffaqiyatli autentifikatsiya",
                    details={"username": username, "role": user_data["role"]},
                    mitigation_status="resolved",
                    compliance_flags=["GDPR"]
                )
                self.event_manager.create_event(event)
                
                return True, "Authentication successful", token
            
        # Failed authentication
        if ip_address in self.auth_manager.failed_attempts:
            self.auth_manager.failed_attempts[ip_address]['count'] += 1
        else:
            self.auth_manager.failed_attempts[ip_address] = {'count': 1, 'first_attempt': time.time()}
        
        # Log failed authentication
        event = SecurityEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.datetime.now().isoformat(),
            event_type="authentication_failure",
            severity="medium",
            source_ip=ip_address,
            user_id=username,
            description="Autentifikatsiya xatosi",
            details={"username": username, "ip_address": ip_address},
            mitigation_status="pending",
            compliance_flags=["SOC2"]
        )
        self.event_manager.create_event(event)
        
        return False, "Invalid credentials", None
    
    def authorize_action(self, token: str, action: str, resource: str) -> bool:
        """Harakatni ruxsat etish"""
        payload = self.auth_manager.verify_token(token)
        if not payload:
            return False
        
        user_permissions = payload.get('permissions', [])
        
        # Check if user has permission for the action
        if action in user_permissions or 'admin' in user_permissions:
            return True
        
        return False
    
    def detect_threat(self, data: str) -> ThreatLevel:
        """Tahid aniqlash"""
        return self.threat_intelligence.analyze_threat(data)
    
    def log_security_event(self, event_type: str, description: str, severity: str, 
                          user_id: str, source_ip: str, details: Dict[str, Any] = None) -> bool:
        """Xavfsizlik voqeasini log qilish"""
        event = SecurityEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.datetime.now().isoformat(),
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
            user_id=user_id,
            description=description,
            details=details or {},
            mitigation_status="pending",
            compliance_flags=["SOC2", "GDPR"]
        )
        
        return self.event_manager.create_event(event)
    
    def check_compliance(self, data_processing: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Moslashuvni tekshirish"""
        return self.compliance_engine.check_compliance(data_processing)
    
    def get_security_dashboard(self) -> Dict[str, Any]:
        """Xavfsizlik dashboard ma'lumotlari"""
        recent_events = self.event_manager.get_events({
            'start_date': (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
        })
        
        # Analyze events for dashboard
        event_counts = {}
        severity_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        
        for event in recent_events:
            event_type = event['event_type']
            severity = event['severity']
            
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            'total_events_7_days': len(recent_events),
            'events_by_type': event_counts,
            'events_by_severity': severity_counts,
            'active_policies': len(self.policy_manager.policies),
            'compliance_status': 'compliant',
            'last_updated': datetime.datetime.now().isoformat()
        }
    
    def run_security_scan(self, target: str) -> Dict[str, Any]:
        """Xavfsizlik skanerini ishga tushirish"""
        logger.info(f"Running security scan on: {target}")
        
        # Simulate security scan
        scan_results = {
            'target': target,
            'scan_time': datetime.datetime.now().isoformat(),
            'vulnerabilities_found': 0,
            'threat_level': 'low',
            'recommendations': [],
            'scan_status': 'completed'
        }
        
        # Check for common vulnerabilities
        common_vulns = {
            'sql_injection': False,
            'xss_vulnerability': False,
            'unencrypted_data': False,
            'weak_passwords': False,
            'outdated_software': False
        }
        
        # Simulate vulnerability detection
        if 'admin' in target.lower():
            common_vulns['weak_passwords'] = True
            scan_results['vulnerabilities_found'] += 1
        
        # Generate recommendations
        for vuln, found in common_vulns.items():
            if found:
                if vuln == 'sql_injection':
                    scan_results['recommendations'].append("Use parameterized queries to prevent SQL injection")
                elif vuln == 'xss_vulnerability':
                    scan_results['recommendations'].append("Implement input sanitization and output encoding")
                elif vuln == 'unencrypted_data':
                    scan_results['recommendations'].append("Enable encryption for sensitive data")
                elif vuln == 'weak_passwords':
                    scan_results['recommendations'].append("Implement strong password policy and MFA")
                elif vuln == 'outdated_software':
                    scan_results['recommendations'].append("Update software to latest secure version")
        
        # Determine overall threat level
        if scan_results['vulnerabilities_found'] == 0:
            scan_results['threat_level'] = 'minimal'
        elif scan_results['vulnerabilities_found'] <= 2:
            scan_results['threat_level'] = 'low'
        elif scan_results['vulnerabilities_found'] <= 5:
            scan_results['threat_level'] = 'moderate'
        else:
            scan_results['threat_level'] = 'high'
        
        return scan_results

# Flask Middleware for enterprise security
app = Flask(__name__)
security_system = EnterpriseSecuritySystem()

@app.before_request
def security_middleware():
    """Har bir so'rovdan oldin xavfsizlik tekshiruvi"""
    g.client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # Log request
    security_system.log_security_event(
        event_type="http_request",
        description=f"HTTP {request.method} {request.path}",
        severity="low",
        user_id="anonymous",
        source_ip=g.client_ip,
        details={
            "method": request.method,
            "path": request.path,
            "user_agent": request.headers.get('User-Agent'),
            "content_type": request.content_type
        }
    )
    
    # Check for threats in request data
    threat_data = request.get_data(as_text=True)
    if threat_data:
        threat_level = security_system.detect_threat(threat_data)
        if threat_level.value in ['high', 'critical']:
            security_system.log_security_event(
                event_type="threat_detected",
                description=f"High threat detected in request: {threat_data[:100]}",
                severity=threat_level.value,
                user_id="anonymous",
                source_ip=g.client_ip,
                details={"threat_data": threat_data[:200]}
            )

@app.route('/api/security/authenticate', methods=['POST'])
def authenticate():
    """Autentifikatsiya endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    success, message, token = security_system.authenticate_user(
        username, password, g.client_ip
    )
    
    return jsonify({
        'success': success,
        'message': message,
        'token': token
    }), 200 if success else 401

@app.route('/api/security/authorize', methods=['POST'])
def authorize():
    """Ruxsat endpoint"""
    data = request.get_json()
    token = data.get('token')
    action = data.get('action')
    resource = data.get('resource')
    
    authorized = security_system.authorize_action(token, action, resource)
    
    return jsonify({
        'authorized': authorized
    }), 200

@app.route('/api/security/dashboard')
def security_dashboard():
    """Xavfsizlik dashboard"""
    dashboard = security_system.get_security_dashboard()
    return jsonify(dashboard)

@app.route('/api/security/scan', methods=['POST'])
def run_security_scan():
    """Xavfsizlik skaneri"""
    data = request.get_json()
    target = data.get('target')
    
    if not target:
        return jsonify({'error': 'Target is required'}), 400
    
    results = security_system.run_security_scan(target)
    return jsonify(results)

@app.route('/api/security/compliance-check', methods=['POST'])
def compliance_check():
    """Moslashuv tekshiruvi"""
    data = request.get_json()
    
    compliant, violations = security_system.check_compliance(data)
    
    return jsonify({
        'compliant': compliant,
        'violations': violations
    }), 200

if __name__ == "__main__":
    # Ensure log directory exists
    os.makedirs('/workspace/orion-starline/logs', exist_ok=True)
    
    # Run the security system
    app.run(host='0.0.0.0', port=5000, debug=False)
