#!/usr/bin/env python3
"""
Audit Logging Tizimi
Audit Logging System - Comprehensive Audit Trail

Bu fayl ilg'or audit logging tizimini ta'minlaydi,
barcha tizim faoliyatlari, ma'lumotlar kirishi, o'zgarishlar
va xavfsizlik voqealarini log qiladi.

Features:
- Real-time Audit Logging
- Immutable Audit Trail
- Compliance Reporting
- Forensic Analysis
- Data Integrity Verification
- Performance Monitoring
- Anomaly Detection
"""

import os
import sys
import json
import sqlite3
import hashlib
import datetime
import logging
import threading
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import queue
import gzip
import shutil
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/orion-starline/logs/audit.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AuditEventType(Enum):
    """Audit voqea turlari"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    DATA_CREATION = "data_creation"
    PERMISSION_CHANGE = "permission_change"
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    SECURITY_EVENT = "security_event"
    COMPLIANCE_CHECK = "compliance_check"
    REPORT_GENERATED = "report_generated"
    BACKUP_OPERATION = "backup_operation"
    RESTORE_OPERATION = "restore_operation"
    API_CALL = "api_call"
    FILE_OPERATION = "file_operation"
    DATABASE_OPERATION = "database_operation"

class EventSeverity(Enum):
    """Voqea og'irligi"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class DataClassification(Enum):
    """Ma'lumotlar tasnifi"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"

class AuditFilter:
    """Audit filtrlash"""
    
    def __init__(self, event_types: List[AuditEventType] = None,
                 severities: List[EventSeverity] = None,
                 user_ids: List[str] = None,
                 ip_addresses: List[str] = None,
                 start_date: str = None,
                 end_date: str = None):
        self.event_types = event_types or []
        self.severities = severities or []
        self.user_ids = user_ids or []
        self.ip_addresses = ip_addresses or []
        self.start_date = start_date
        self.end_date = end_date

@dataclass
class AuditLog:
    """Audit log yozuvi"""
    log_id: str
    timestamp: str
    event_type: str
    severity: str
    user_id: str
    session_id: str
    ip_address: str
    user_agent: str
    resource: str
    action: str
    details: Dict[str, Any]
    data_classification: str
    integrity_hash: str
    previous_hash: str
    metadata: Dict[str, Any]

@dataclass
class DataIntegrityRecord:
    """Ma'lumotlar yaxlitligi yozuvi"""
    record_id: str
    timestamp: str
    data_hash: str
    previous_hash: str
    operation_type: str
    user_id: str
    checksum_algorithm: str
    verification_status: str

class BlockchainAuditTrail:
    """Blockchainga asoslangan audit trail"""
    
    def __init__(self):
        self.chain = []
        self.difficulty = 4
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Genesis block yaratish"""
        genesis_block = {
            'index': 0,
            'timestamp': datetime.datetime.now().isoformat(),
            'data': 'Genesis Block',
            'previous_hash': '0',
            'hash': self.calculate_hash(0, 'Genesis Block', '0'),
            'nonce': 0
        }
        self.chain.append(genesis_block)
    
    def calculate_hash(self, index, data, previous_hash):
        """Hash hisoblash"""
        value = str(index) + data + previous_hash
        return hashlib.sha256(value.encode()).hexdigest()
    
    def add_audit_record(self, audit_log: AuditLog) -> Dict[str, Any]:
        """Audit yozuvini zanjirga qo'shish"""
        previous_block = self.chain[-1]
        block_data = json.dumps(asdict(audit_log), sort_keys=True)
        
        new_block = {
            'index': len(self.chain),
            'timestamp': datetime.datetime.now().isoformat(),
            'data': block_data,
            'previous_hash': previous_block['hash'],
            'hash': '',
            'nonce': 0
        }
        
        # Proof of work
        new_block['hash'] = self.proof_of_work(new_block)
        self.chain.append(new_block)
        
        return new_block
    
    def proof_of_work(self, block):
        """Proof of Work algoritmi"""
        computed_hash = self.calculate_hash(block['index'], block['data'], block['previous_hash'])
        
        while not computed_hash.startswith('0' * self.difficulty):
            block['nonce'] += 1
            computed_hash = self.calculate_hash(block['index'], block['data'], block['previous_hash'])
        
        return computed_hash
    
    def verify_chain_integrity(self) -> Tuple[bool, List[str]]:
        """Zanjir yaxlitligini tekshirish"""
        issues = []
        
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Verify current block hash
            expected_hash = self.calculate_hash(
                current_block['index'],
                current_block['data'],
                current_block['previous_hash']
            )
            
            if current_block['hash'] != expected_hash:
                issues.append(f"Block {i} hash mismatch")
            
            # Verify previous hash reference
            if current_block['previous_hash'] != previous_block['hash']:
                issues.append(f"Block {i} previous hash mismatch")
        
        return len(issues) == 0, issues

class AuditLogger:
    """Asosiy audit logger klass"""
    
    def __init__(self, db_path: str = "/workspace/orion-starline/data/audit_logs.db",
                 blockchain_path: str = "/workspace/orion-starline/data/audit_blockchain.json"):
        self.db_path = db_path
        self.blockchain_path = blockchain_path
        self.blockchain = BlockchainAuditTrail()
        self.log_queue = queue.Queue()
        self.is_running = False
        self.worker_thread = None
        
        # Initialize encryption
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        self.init_database()
        self.load_blockchain()
        
        logger.info("Audit Logger initialized")
    
    def _generate_encryption_key(self) -> bytes:
        """Shifrlash kaliti yaratish"""
        password = os.environ.get('AUDIT_ENCRYPTION_KEY', 'default-audit-key').encode()
        salt = b'audit_logs_salt_2024'
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def init_database(self):
        """Ma'lumotlar bazasini ishga tushirish"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                user_agent TEXT NOT NULL,
                resource TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                data_classification TEXT NOT NULL,
                integrity_hash TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_logs(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_id ON audit_logs(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_event_type ON audit_logs(event_type)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_severity ON audit_logs(severity)
        ''')
        
        # Data integrity table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_integrity (
                record_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                data_hash TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                user_id TEXT NOT NULL,
                checksum_algorithm TEXT NOT NULL,
                verification_status TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_blockchain(self):
        """Blockchainga o'qish"""
        try:
            if os.path.exists(self.blockchain_path):
                with open(self.blockchain_path, 'r') as f:
                    blockchain_data = json.load(f)
                    self.chain = blockchain_data.get('chain', [])
        except Exception as e:
            logger.error(f"Failed to load blockchain: {e}")
    
    def save_blockchain(self):
        """Blockchainga yozish"""
        try:
            blockchain_data = {'chain': self.chain}
            with open(self.blockchain_path, 'w') as f:
                json.dump(blockchain_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save blockchain: {e}")
    
    def _calculate_integrity_hash(self, log_data: Dict[str, Any], previous_hash: str) -> str:
        """Yaxlitlik hashini hisoblash"""
        data_string = json.dumps(log_data, sort_keys=True) + previous_hash
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def _get_last_hash(self) -> str:
        """So'nggi hashni olish"""
        if len(self.blockchain.chain) == 0:
            return "0"
        return self.blockchain.chain[-1]['hash']
    
    def log_event(self, event_type: AuditEventType, severity: EventSeverity,
                  user_id: str, action: str, resource: str,
                  data_classification: DataClassification = DataClassification.INTERNAL,
                  details: Dict[str, Any] = None,
                  session_id: str = None,
                  ip_address: str = None,
                  user_agent: str = None) -> str:
        """Voqeani log qilish"""
        
        log_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()
        
        # Default values
        session_id = session_id or "unknown"
        ip_address = ip_address or "0.0.0.0"
        user_agent = user_agent or "unknown"
        details = details or {}
        
        # Calculate integrity hash
        log_data = {
            'log_id': log_id,
            'timestamp': timestamp,
            'event_type': event_type.value,
            'severity': severity.value,
            'user_id': user_id,
            'session_id': session_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'resource': resource,
            'action': action,
            'details': details,
            'data_classification': data_classification.value
        }
        
        previous_hash = self._get_last_hash()
        integrity_hash = self._calculate_integrity_hash(log_data, previous_hash)
        
        # Create audit log
        audit_log = AuditLog(
            log_id=log_id,
            timestamp=timestamp,
            event_type=event_type.value,
            severity=severity.value,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource=resource,
            action=action,
            details=details,
            data_classification=data_classification.value,
            integrity_hash=integrity_hash,
            previous_hash=previous_hash,
            metadata={'thread_id': threading.current_thread().ident}
        )
        
        # Add to queue for processing
        self.log_queue.put(audit_log)
        
        return log_id
    
    def _process_log_queue(self):
        """Log navbatini qayta ishlash"""
        while self.is_running:
            try:
                if not self.log_queue.empty():
                    audit_log = self.log_queue.get(timeout=1)
                    self._store_audit_log(audit_log)
                    self._add_to_blockchain(audit_log)
                else:
                    time.sleep(0.1)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing audit log: {e}")
    
    def _store_audit_log(self, audit_log: AuditLog):
        """Audit logni ma'lumotlar bazasiga saqlash"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO audit_logs 
                (log_id, timestamp, event_type, severity, user_id, session_id, ip_address, 
                 user_agent, resource, action, details, data_classification, integrity_hash, 
                 previous_hash, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                audit_log.log_id, audit_log.timestamp, audit_log.event_type, audit_log.severity,
                audit_log.user_id, audit_log.session_id, audit_log.ip_address, audit_log.user_agent,
                audit_log.resource, audit_log.action, json.dumps(audit_log.details),
                audit_log.data_classification, audit_log.integrity_hash, audit_log.previous_hash,
                json.dumps(audit_log.metadata)
            ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Audit log stored: {audit_log.log_id}")
            
        except Exception as e:
            logger.error(f"Failed to store audit log: {e}")
    
    def _add_to_blockchain(self, audit_log: AuditLog):
        """Blockchainga qo'shish"""
        try:
            self.blockchain.add_audit_record(audit_log)
            self.save_blockchain()
        except Exception as e:
            logger.error(f"Failed to add to blockchain: {e}")
    
    def start_logging(self):
        """Audit loglarni ishga tushirish"""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._process_log_queue)
            self.worker_thread.daemon = True
            self.worker_thread.start()
            logger.info("Audit logging started")
    
    def stop_logging(self):
        """Audit loglarni to'xtatish"""
        if self.is_running:
            self.is_running = False
            if self.worker_thread:
                self.worker_thread.join()
            logger.info("Audit logging stopped")
    
    def get_audit_logs(self, filters: AuditFilter = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """Audit loglarni olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        
        if filters:
            if filters.event_types:
                placeholders = ','.join(['?' for _ in filters.event_types])
                query += f" AND event_type IN ({placeholders})"
                params.extend([et.value for et in filters.event_types])
            
            if filters.severities:
                placeholders = ','.join(['?' for _ in filters.severities])
                query += f" AND severity IN ({placeholders})"
                params.extend([s.value for s in filters.severities])
            
            if filters.user_ids:
                placeholders = ','.join(['?' for _ in filters.user_ids])
                query += f" AND user_id IN ({placeholders})"
                params.extend(filters.user_ids)
            
            if filters.start_date:
                query += " AND timestamp >= ?"
                params.append(filters.start_date)
            
            if filters.end_date:
                query += " AND timestamp <= ?"
                params.append(filters.end_date)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        logs = []
        for row in rows:
            logs.append({
                'log_id': row[0],
                'timestamp': row[1],
                'event_type': row[2],
                'severity': row[3],
                'user_id': row[4],
                'session_id': row[5],
                'ip_address': row[6],
                'user_agent': row[7],
                'resource': row[8],
                'action': row[9],
                'details': json.loads(row[10]),
                'data_classification': row[11],
                'integrity_hash': row[12],
                'previous_hash': row[13],
                'metadata': json.loads(row[14])
            })
        
        return logs
    
    def verify_log_integrity(self, log_id: str) -> Dict[str, Any]:
        """Log yaxlitligini tekshirish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM audit_logs WHERE log_id = ?', (log_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {'status': 'not_found', 'log_id': log_id}
        
        # Recalculate hash
        log_data = {
            'log_id': row[0],
            'timestamp': row[1],
            'event_type': row[2],
            'severity': row[3],
            'user_id': row[4],
            'session_id': row[5],
            'ip_address': row[6],
            'user_agent': row[7],
            'resource': row[8],
            'action': row[9],
            'details': json.loads(row[10]),
            'data_classification': row[11]
        }
        
        expected_hash = self._calculate_integrity_hash(log_data, row[13])
        actual_hash = row[12]
        
        is_valid = expected_hash == actual_hash
        
        return {
            'status': 'valid' if is_valid else 'corrupted',
            'log_id': log_id,
            'expected_hash': expected_hash,
            'actual_hash': actual_hash,
            'verification_timestamp': datetime.datetime.now().isoformat()
        }
    
    def generate_compliance_report(self, start_date: str, end_date: str, 
                                 compliance_standard: str) -> Dict[str, Any]:
        """Moslashuv hisobotini yaratish"""
        filter_ = AuditFilter(
            start_date=start_date,
            end_date=end_date
        )
        
        logs = self.get_audit_logs(filter_, limit=10000)
        
        # Analyze logs for compliance
        report = {
            'report_id': str(uuid.uuid4()),
            'generation_date': datetime.datetime.now().isoformat(),
            'report_period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'compliance_standard': compliance_standard,
            'summary': {
                'total_events': len(logs),
                'unique_users': len(set(log['user_id'] for log in logs)),
                'critical_events': len([log for log in logs if log['severity'] == 'critical']),
                'security_events': len([log for log in logs if log['event_type'] == 'security_event'])
            },
            'event_breakdown': {},
            'user_activity': {},
            'compliance_violations': [],
            'integrity_verification': {}
        }
        
        # Event type breakdown
        for log in logs:
            event_type = log['event_type']
            if event_type not in report['event_breakdown']:
                report['event_breakdown'][event_type] = 0
            report['event_breakdown'][event_type] += 1
        
        # User activity analysis
        for log in logs:
            user_id = log['user_id']
            if user_id not in report['user_activity']:
                report['user_activity'][user_id] = {
                    'total_events': 0,
                    'last_activity': log['timestamp'],
                    'event_types': set()
                }
            report['user_activity'][user_id]['total_events'] += 1
            report['user_activity'][user_id]['event_types'].add(log['event_type'])
            if log['timestamp'] > report['user_activity'][user_id]['last_activity']:
                report['user_activity'][user_id]['last_activity'] = log['timestamp']
        
        # Convert sets to lists for JSON serialization
        for user_data in report['user_activity'].values():
            user_data['event_types'] = list(user_data['event_types'])
        
        # Check for compliance violations
        for log in logs:
            if log['severity'] == 'critical':
                report['compliance_violations'].append({
                    'log_id': log['log_id'],
                    'timestamp': log['timestamp'],
                    'violation_type': 'critical_security_event',
                    'description': f"Critical event: {log['event_type']} by user {log['user_id']}"
                })
        
        return report
    
    def archive_old_logs(self, days_to_keep: int = 365) -> Dict[str, Any]:
        """Eski loglarni arxivlash"""
        cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days_to_keep)).isoformat()
        
        # Get logs to archive
        filter_ = AuditFilter()
        logs_to_archive = self.get_audit_logs(filter_, limit=1000000)
        old_logs = [log for log in logs_to_archive if log['timestamp'] < cutoff_date]
        
        if not old_logs:
            return {'status': 'no_logs_to_archive', 'archived_count': 0}
        
        # Create archive
        archive_path = f"/workspace/orion-starline/logs/audit_archive_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json.gz"
        
        try:
            with gzip.open(archive_path, 'wt') as f:
                json.dump(old_logs, f, indent=2)
            
            # Delete old logs from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM audit_logs WHERE timestamp < ?', (cutoff_date,))
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Archived {deleted_count} audit logs to {archive_path}")
            
            return {
                'status': 'success',
                'archived_count': deleted_count,
                'archive_path': archive_path,
                'cutoff_date': cutoff_date
            }
            
        except Exception as e:
            logger.error(f"Failed to archive logs: {e}")
            return {'status': 'error', 'error': str(e)}

class AuditAnalyzer:
    """Audit loglarni tahlil qilish"""
    
    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger
    
    def detect_anomalies(self, time_window_hours: int = 24) -> List[Dict[str, Any]]:
        """Anomaliyalarni aniqlash"""
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(hours=time_window_hours)
        
        filter_ = AuditFilter(
            start_date=start_time.isoformat(),
            end_date=end_time.isoformat()
        )
        
        logs = self.audit_logger.get_audit_logs(filter_, limit=10000)
        anomalies = []
        
        # Analyze user behavior patterns
        user_activity = {}
        for log in logs:
            user_id = log['user_id']
            if user_id not in user_activity:
                user_activity[user_id] = []
            user_activity[user_id].append(log)
        
        # Detect unusual activity
        for user_id, user_logs in user_activity.items():
            # Check for too many failed login attempts
            failed_attempts = [log for log in user_logs if log['event_type'] == 'user_login' 
                             and 'success' in str(log['details']).lower()]
            if len(failed_attempts) > 10:
                anomalies.append({
                    'type': 'excessive_failed_logins',
                    'user_id': user_id,
                    'count': len(failed_attempts),
                    'time_window_hours': time_window_hours,
                    'severity': 'high'
                })
            
            # Check for unusual time activity
            login_times = [datetime.datetime.fromisoformat(log['timestamp']).hour 
                          for log in user_logs if log['event_type'] == 'user_login']
            if login_times:
                avg_hour = sum(login_times) / len(login_times)
                if avg_hour < 6 or avg_hour > 22:  # Outside normal business hours
                    anomalies.append({
                        'type': 'unusual_time_activity',
                        'user_id': user_id,
                        'avg_login_hour': avg_hour,
                        'severity': 'medium'
                    })
        
        return anomalies
    
    def generate_forensic_timeline(self, incident_id: str, 
                                 start_time: str, end_time: str) -> Dict[str, Any]:
        """Forensik vaqt chizig'ini yaratish"""
        filter_ = AuditFilter(
            start_date=start_time,
            end_date=end_time
        )
        
        logs = self.audit_logger.get_audit_logs(filter_, limit=10000)
        
        # Sort logs by timestamp
        logs.sort(key=lambda x: x['timestamp'])
        
        timeline = {
            'incident_id': incident_id,
            'timeline_period': {
                'start': start_time,
                'end': end_time
            },
            'events': [],
            'summary': {
                'total_events': len(logs),
                'unique_users': len(set(log['user_id'] for log in logs)),
                'unique_ips': len(set(log['ip_address'] for log in logs)),
                'critical_events': len([log for log in logs if log['severity'] == 'critical'])
            }
        }
        
        for log in logs:
            timeline['events'].append({
                'timestamp': log['timestamp'],
                'event_type': log['event_type'],
                'severity': log['severity'],
                'user_id': log['user_id'],
                'ip_address': log['ip_address'],
                'resource': log['resource'],
                'action': log['action'],
                'details': log['details']
            })
        
        return timeline

# Flask middleware for automatic audit logging
from flask import Flask, request, g

audit_logger = AuditLogger()

@app.before_request
def audit_middleware():
    """Har bir so'rovdan oldin audit log"""
    g.start_time = time.time()
    g.client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    g.user_agent = request.headers.get('User-Agent', 'unknown')
    g.session_id = request.headers.get('X-Session-ID', 'unknown')
    
    # Log API call
    audit_logger.log_event(
        event_type=AuditEventType.API_CALL,
        severity=EventSeverity.INFO,
        user_id="anonymous",
        action=f"{request.method} {request.path}",
        resource=request.endpoint or request.path,
        ip_address=g.client_ip,
        user_agent=g.user_agent,
        session_id=g.session_id,
        details={
            'method': request.method,
            'endpoint': request.endpoint,
            'content_type': request.content_type,
            'content_length': request.content_length
        }
    )

@app.after_request
def audit_response_middleware(response):
    """Har bir javobdan keyin audit log"""
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        
        # Log performance issues
        if duration > 5.0:  # Slow requests
            audit_logger.log_event(
                event_type=AuditEventType.API_CALL,
                severity=EventSeverity.WARNING,
                user_id="anonymous",
                action="slow_request",
                resource=request.endpoint or request.path,
                details={
                    'duration': duration,
                    'status_code': response.status_code,
                    'endpoint': request.endpoint
                }
            )
    
    return response

# API endpoints for audit system
@app.route('/api/audit/logs')
def get_audit_logs():
    """Audit loglarni olish"""
    try:
        event_types = request.args.getlist('event_type')
        severities = request.args.getlist('severity')
        user_ids = request.args.getlist('user_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 1000))
        
        # Convert strings to enums
        event_type_enums = [AuditEventType(et) for et in event_types if et in [e.value for e in AuditEventType]]
        severity_enums = [EventSeverity(s) for s in severities if s in [e.value for e in EventSeverity]]
        
        filter_ = AuditFilter(
            event_types=event_type_enums,
            severities=severity_enums,
            user_ids=user_ids,
            start_date=start_date,
            end_date=end_date
        )
        
        logs = audit_logger.get_audit_logs(filter_, limit)
        return jsonify(logs)
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/audit/integrity/<log_id>')
def verify_log_integrity(log_id):
    """Log yaxlitligini tekshirish"""
    try:
        result = audit_logger.verify_log_integrity(log_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error verifying log integrity: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/audit/compliance-report')
def generate_compliance_report():
    """Moslashuv hisobotini yaratish"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        standard = request.args.get('standard', 'SOC2')
        
        if not start_date or not end_date:
            return jsonify({'error': 'start_date and end_date are required'}), 400
        
        report = audit_logger.generate_compliance_report(start_date, end_date, standard)
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Error generating compliance report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/audit/anomalies')
def detect_anomalies():
    """Anomaliyalarni aniqlash"""
    try:
        time_window = int(request.args.get('hours', 24))
        analyzer = AuditAnalyzer(audit_logger)
        anomalies = analyzer.detect_anomalies(time_window)
        return jsonify(anomalies)
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/audit/archive', methods=['POST'])
def archive_logs():
    """Loglarni arxivlash"""
    try:
        data = request.get_json() or {}
        days_to_keep = data.get('days_to_keep', 365)
        
        result = audit_logger.archive_old_logs(days_to_keep)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error archiving logs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/audit/blockchain/verify')
def verify_blockchain():
    """Blockchainga yaxlitligini tekshirish"""
    try:
        is_valid, issues = audit_logger.blockchain.verify_chain_integrity()
        return jsonify({
            'valid': is_valid,
            'issues': issues,
            'chain_length': len(audit_logger.blockchain.chain),
            'verification_time': datetime.datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error verifying blockchain: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs('/workspace/orion-starline/data', exist_ok=True)
    os.makedirs('/workspace/orion-starline/logs', exist_ok=True)
    
    # Start audit logging
    audit_logger.start_logging()
    
    # Run audit system
    app.run(host='0.0.0.0', port=5002, debug=False)
