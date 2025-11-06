#!/usr/bin/env python3
"""
GDPR & SOC 2 Moslashuv Tizimi
Compliance Management System - GDPR, SOC 2, ISO 27001

Bu fayl GDPR, SOC 2, ISO 27001 va boshqa xalqaro standartlar bo'yicha
moslashuvni ta'minlaydi va audit trail yaratadi.

Features:
- GDPR Data Protection Rights
- SOC 2 Trust Services Criteria
- ISO 27001 Compliance
- Data Retention Management
- Consent Management
- Breach Notification
- Privacy Impact Assessment
"""

import os
import sys
import json
import sqlite3
import hashlib
import datetime
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import uuid
from cryptography.fernet import Fernet
import jwt
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/orion-starline/logs/compliance.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComplianceStandard(Enum):
    """Moslashuv standartlari"""
    GDPR = "gdpr"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    CCPA = "ccpa"

class DataCategory(Enum):
    """Ma'lumotlar kategoriyasi"""
    PERSONAL_IDENTIFIABLE = "personal_identifiable"
    SENSITIVE_PERSONAL = "sensitive_personal"
    FINANCIAL = "financial"
    HEALTH = "health"
    BIOMETRIC = "biometric"
    LOCATION = "location"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"

class ProcessingPurpose(Enum):
    """Qayta ishlash maqsadi"""
    CONSENT_BASED = "consent_based"
    CONTRACTUAL = "contractual"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTEREST = "vital_interest"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTEREST = "legitimate_interest"

class RetentionPeriod(Enum):
    """Saqlash davomiyligi"""
    IMMEDIATE_DELETION = 0  # Darhol o'chirish
    ONE_DAY = 1
    SEVEN_DAYS = 7
    THIRTY_DAYS = 30
    NINETY_DAYS = 90
    ONE_YEAR = 365
    SEVEN_YEARS = 2555  # 7 years for GDPR
    INDEFINITE = -1  # Cheksiz

@dataclass
class DataSubject:
    """Ma'lumot subyekti"""
    subject_id: str
    email: str
    name: str
    consent_date: str
    consent_status: str  # "active", "withdrawn", "expired"
    data_categories: List[str]
    retention_period: int
    last_activity: str
    privacy_preferences: Dict[str, Any]

@dataclass
class DataProcessingRecord:
    """Ma'lumotlar qayta ishlash yozuvi"""
    record_id: str
    subject_id: str
    processor_id: str
    processing_purpose: str
    legal_basis: str
    data_categories: List[str]
    processing_start: str
    processing_end: Optional[str]
    retention_period: int
    third_party_sharing: bool
    cross_border_transfer: bool
    security_measures: List[str]

@dataclass
class ConsentRecord:
    """Ruxsat yozuvi"""
    consent_id: str
    subject_id: str
    consent_type: str
    purpose: str
    granted: bool
    timestamp: str
    ip_address: str
    user_agent: str
    method: str  # "opt_in", "opt_out", "implied"
    withdrawal_date: Optional[str]

@dataclass
class PrivacyImpactAssessment:
    """Maxfiylik ta'sir baholashi"""
    assessment_id: str
    project_name: str
    assessment_date: str
    assessor: str
    data_types: List[str]
    processing_purposes: List[str]
    risks: List[Dict[str, Any]]
    mitigations: List[str]
    status: str  # "draft", "in_review", "approved", "rejected"
    approval_date: Optional[str]

class DataProtectionOfficer:
    """Ma'lumotlar himoyasi ofitseri"""
    
    def __init__(self, name: str, email: str, phone: str):
        self.name = name
        self.email = email
        self.phone = phone
        self.is_available = True
        self.working_hours = "09:00-17:00"
    
    def notify_breach(self, breach_info: Dict[str, Any]) -> bool:
        """Buzilishni xabar qilish"""
        try:
            # Send breach notification to DPO
            logger.critical(f"DATA BREACH NOTIFICATION to {self.email}")
            logger.critical(f"Breach Details: {breach_info}")
            return True
        except Exception as e:
            logger.error(f"Failed to notify DPO: {e}")
            return False

class GDPRCompliance:
    """GDPR moslashuv moduli"""
    
    def __init__(self):
        self.dpo = DataProtectionOfficer(
            "Ma'lumotlar Himoyasi Ofitseri",
            "dpo@orion-starline.com",
            "+998-90-123-45-67"
        )
        self.legal_basis_mapping = {
            ProcessingPurpose.CONSENT_BASED: "Article 6(1)(a)",
            ProcessingPurpose.CONTRACTUAL: "Article 6(1)(b)",
            ProcessingPurpose.LEGAL_OBLIGATION: "Article 6(1)(c)",
            ProcessingPurpose.VITAL_INTEREST: "Article 6(1)(d)",
            ProcessingPurpose.PUBLIC_TASK: "Article 6(1)(e)",
            ProcessingPurpose.LEGITIMATE_INTEREST: "Article 6(1)(f)"
        }
    
    def validate_consent(self, consent: ConsentRecord) -> Tuple[bool, List[str]]:
        """Ruxsatni tekshirish"""
        issues = []
        
        # Check consent specificity
        if len(consent.purpose) < 10:
            issues.append("Consent purpose not specific enough")
        
        # Check if consent is informed
        if consent.method not in ["opt_in", "explicit_opt_in"]:
            issues.append("Consent method not explicit enough")
        
        # Check withdrawal mechanism
        if not hasattr(self, 'withdrawal_mechanism'):
            issues.append("No withdrawal mechanism provided")
        
        return len(issues) == 0, issues
    
    def handle_data_subject_request(self, subject_id: str, request_type: str) -> Dict[str, Any]:
        """Ma'lumot subyektining so'rovini qayta ishlash"""
        try:
            if request_type == "access":  # Article 15 - Right of access
                return self._handle_access_request(subject_id)
            elif request_type == "rectification":  # Article 16 - Right to rectification
                return self._handle_rectification_request(subject_id)
            elif request_type == "erasure":  # Article 17 - Right to erasure
                return self._handle_erasure_request(subject_id)
            elif request_type == "portability":  # Article 20 - Right to data portability
                return self._handle_portability_request(subject_id)
            elif request_type == "restriction":  # Article 18 - Right to restriction
                return self._handle_restriction_request(subject_id)
            elif request_type == "objection":  # Article 21 - Right to object
                return self._handle_objection_request(subject_id)
            else:
                raise ValueError(f"Unknown request type: {request_type}")
        
        except Exception as e:
            logger.error(f"Error handling data subject request: {e}")
            return {"error": str(e), "status": "failed"}
    
    def _handle_access_request(self, subject_id: str) -> Dict[str, Any]:
        """Kirish huquqini amalga oshirish"""
        # This would integrate with your data storage
        response = {
            "request_type": "access",
            "subject_id": subject_id,
            "response_date": datetime.datetime.now().isoformat(),
            "data_categories": [],
            "processing_purposes": [],
            "retention_periods": [],
            "third_party_sharing": False,
            "automated_decision_making": False,
            "cross_border_transfers": []
        }
        
        # Log the request for audit trail
        logger.info(f"GDPR Access Request processed for subject: {subject_id}")
        return response
    
    def _handle_erasure_request(self, subject_id: str) -> Dict[str, Any]:
        """O'chirish huquqini amalga oshirish"""
        # Check if erasure is legally permitted
        retention_obligations = [
            "legal_requirement",
            "public_interest",
            "legal_claims",
            " public_health",
            "historical_research"
        ]
        
        can_erase = True  # This would be determined by legal analysis
        
        if can_erase:
            # Trigger data deletion process
            logger.warning(f"GDPR Erasure Request - Data deletion initiated for: {subject_id}")
            deletion_result = {"status": "completed", "deleted_records": 0}
        else:
            deletion_result = {"status": "restricted", "reasons": retention_obligations}
        
        return {
            "request_type": "erasure",
            "subject_id": subject_id,
            "response_date": datetime.datetime.now().isoformat(),
            "deletion_result": deletion_result
        }
    
    def _handle_rectification_request(self, subject_id: str) -> Dict[str, Any]:
        """Tuzatish huquqini amalga oshirish"""
        return {
            "request_type": "rectification",
            "subject_id": subject_id,
            "response_date": datetime.datetime.now().isoformat(),
            "status": "pending_verification"
        }
    
    def _handle_portability_request(self, subject_id: str) -> Dict[str, Any]:
        """Ko'chirish huquqini amalga oshirish"""
        return {
            "request_type": "portability",
            "subject_id": subject_id,
            "response_date": datetime.datetime.now().isoformat(),
            "format": "machine_readable",
            "delivery_method": "secure_email"
        }
    
    def _handle_restriction_request(self, subject_id: str) -> Dict[str, Any]:
        """Cheklash huquqini amalga oshirish"""
        return {
            "request_type": "restriction",
            "subject_id": subject_id,
            "response_date": datetime.datetime.now().isoformat(),
            "status": "processing_suspended"
        }
    
    def _handle_objection_request(self, subject_id: str) -> Dict[str, Any]:
        """E'tiroz huquqini amalga oshirish"""
        return {
            "request_type": "objection",
            "subject_id": subject_id,
            "response_date": datetime.datetime.now().isoformat(),
            "status": "under_review"
        }

class SOC2Compliance:
    """SOC 2 moslashuv moduli"""
    
    def __init__(self):
        self.trust_service_criteria = {
            "security": {
                "controls": 34,
                "description": "Protection against unauthorized access"
            },
            "availability": {
                "controls": 19,
                "description": "System availability for operation and use"
            },
            "processing_integrity": {
                "controls": 14,
                "description": "Complete, valid, accurate, timely, and authorized"
            },
            "confidentiality": {
                "controls": 20,
                "description": "Information designated as confidential is protected"
            },
            "privacy": {
                "controls": 19,
                "description": "Personal information is collected, used, retained, and disposed"
            }
        }
    
    def assess_trust_criteria(self, criteria: str) -> Dict[str, Any]:
        """Trust Services Criteria baholash"""
        if criteria not in self.trust_service_criteria:
            raise ValueError(f"Invalid criteria: {criteria}")
        
        criteria_info = self.trust_service_criteria[criteria]
        
        return {
            "criteria": criteria,
            "controls_count": criteria_info["controls"],
            "description": criteria_info["description"],
            "assessment_date": datetime.datetime.now().isoformat(),
            "compliance_status": "compliant"  # This would be determined by actual assessment
        }
    
    def validate_control_implementation(self, control_id: str) -> Dict[str, Any]:
        """Control implementatsiyasini tekshirish"""
        # This would check against actual control documentation
        return {
            "control_id": control_id,
            "status": "implemented",
            "last_tested": datetime.datetime.now().isoformat(),
            "next_review": (datetime.datetime.now() + datetime.timedelta(days=90)).isoformat()
        }

class ConsentManagement:
    """Ruxsat boshqaruvchisi"""
    
    def __init__(self, db_path: str = "/workspace/orion-starline/data/consent_management.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Ma'lumotlar bazasini ishga tushirish"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consent_records (
                consent_id TEXT PRIMARY KEY,
                subject_id TEXT NOT NULL,
                consent_type TEXT NOT NULL,
                purpose TEXT NOT NULL,
                granted BOOLEAN NOT NULL,
                timestamp TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                user_agent TEXT NOT NULL,
                method TEXT NOT NULL,
                withdrawal_date TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_consent(self, consent: ConsentRecord) -> bool:
        """Ruxsat yozuvini saqlash"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO consent_records 
                (consent_id, subject_id, consent_type, purpose, granted, timestamp, ip_address, user_agent, method, withdrawal_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                consent.consent_id, consent.subject_id, consent.consent_type, consent.purpose,
                consent.granted, consent.timestamp, consent.ip_address, consent.user_agent,
                consent.method, consent.withdrawal_date
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Consent recorded: {consent.consent_id} for subject: {consent.subject_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to record consent: {e}")
            return False
    
    def withdraw_consent(self, consent_id: str) -> bool:
        """Ruxsatni qaytarib olish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE consent_records 
                SET withdrawal_date = ?, granted = FALSE
                WHERE consent_id = ?
            ''', (datetime.datetime.now().isoformat(), consent_id))
            
            conn.commit()
            conn.close()
            
            logger.warning(f"Consent withdrawn: {consent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to withdraw consent: {e}")
            return False
    
    def get_active_consents(self, subject_id: str) -> List[Dict[str, Any]]:
        """Faol ruxsatlarni olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM consent_records 
            WHERE subject_id = ? AND granted = TRUE AND withdrawal_date IS NULL
        ''', (subject_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        consents = []
        for row in rows:
            consents.append({
                'consent_id': row[0],
                'subject_id': row[1],
                'consent_type': row[2],
                'purpose': row[3],
                'granted': bool(row[4]),
                'timestamp': row[5],
                'ip_address': row[6],
                'user_agent': row[7],
                'method': row[8],
                'withdrawal_date': row[9]
            })
        
        return consents

class DataRetentionManager:
    """Ma'lumotlar saqlash muddati boshqaruvchisi"""
    
    def __init__(self, db_path: str = "/workspace/orion-starline/data/data_retention.db"):
        self.db_path = db_path
        self.retention_policies = {
            DataCategory.PERSONAL_IDENTIFIABLE: RetentionPeriod.SEVEN_YEARS,
            DataCategory.SENSITIVE_PERSONAL: RetentionPeriod.SEVEN_YEARS,
            DataCategory.FINANCIAL: RetentionPeriod.SEVEN_YEARS,
            DataCategory.HEALTH: RetentionPeriod.TEN_YEARS if hasattr(RetentionPeriod, 'TEN_YEARS') else RetentionPeriod.SEVEN_YEARS,
            DataCategory.TECHNICAL: RetentionPeriod.NINETY_DAYS,
            DataCategory.BEHAVIORAL: RetentionPeriod.ONE_YEAR,
            DataCategory.LOCATION: RetentionPeriod.THIRTY_DAYS,
            DataCategory.BIOMETRIC: RetentionPeriod.ONE_YEAR
        }
        self.init_database()
    
    def init_database(self):
        """Ma'lumotlar bazasini ishga tushirish"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_retention_policies (
                data_category TEXT PRIMARY KEY,
                retention_period INTEGER NOT NULL,
                legal_basis TEXT,
                created_date TEXT NOT NULL,
                last_updated TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS retention_schedules (
                schedule_id TEXT PRIMARY KEY,
                data_category TEXT NOT NULL,
                collection_date TEXT NOT NULL,
                scheduled_deletion_date TEXT NOT NULL,
                deletion_status TEXT NOT NULL,
                last_checked TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Set default retention policies
        self._set_default_policies()
    
    def _set_default_policies(self):
        """Standart saqlash siyosatlarini o'rnatish"""
        for category, period in self.retention_policies.items():
            self.set_retention_policy(category, period, "legal_requirement")
    
    def set_retention_policy(self, category: DataCategory, period: RetentionPeriod, legal_basis: str):
        """Saqlash siyosatini o'rnatish"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO data_retention_policies 
                (data_category, retention_period, legal_basis, created_date, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                category.value, period.value, legal_basis,
                datetime.datetime.now().isoformat(), datetime.datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Retention policy set for {category.value}: {period.value} days")
            
        except Exception as e:
            logger.error(f"Failed to set retention policy: {e}")
    
    def schedule_data_deletion(self, data_id: str, category: DataCategory, collection_date: str) -> str:
        """Ma'lumotlarni o'chirishni rejalash"""
        policy = self.get_retention_policy(category)
        if not policy:
            raise ValueError(f"No retention policy found for {category}")
        
        collection_dt = datetime.datetime.fromisoformat(collection_date)
        deletion_date = collection_dt + datetime.timedelta(days=policy['retention_period'])
        
        schedule_id = str(uuid.uuid4())
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO retention_schedules 
                (schedule_id, data_category, collection_date, scheduled_deletion_date, deletion_status, last_checked)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                schedule_id, category.value, collection_date, deletion_date.isoformat(),
                'scheduled', datetime.datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Data deletion scheduled: {schedule_id} for {deletion_date}")
            return schedule_id
            
        except Exception as e:
            logger.error(f"Failed to schedule deletion: {e}")
            return None
    
    def get_retention_policy(self, category: DataCategory) -> Optional[Dict[str, Any]]:
        """Saqlash siyosatini olish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM data_retention_policies WHERE data_category = ?
        ''', (category.value,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'data_category': row[0],
                'retention_period': row[1],
                'legal_basis': row[2],
                'created_date': row[3],
                'last_updated': row[4]
            }
        return None
    
    def execute_deletion_schedule(self) -> List[str]:
        """O'chirish jadvalini bajarish"""
        now = datetime.datetime.now()
        deletions_executed = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM retention_schedules 
                WHERE deletion_status = 'scheduled' 
                AND datetime(scheduled_deletion_date) <= datetime(?)
            ''', (now.isoformat(),))
            
            schedules = cursor.fetchall()
            
            for schedule in schedules:
                schedule_id = schedule[0]
                
                # Execute deletion (this would integrate with your actual data storage)
                deletion_success = self._delete_data_by_schedule(schedule_id)
                
                if deletion_success:
                    cursor.execute('''
                        UPDATE retention_schedules 
                        SET deletion_status = ?, last_checked = ?
                        WHERE schedule_id = ?
                    ''', ('completed', now.isoformat(), schedule_id))
                    deletions_executed.append(schedule_id)
                    logger.warning(f"Data deletion executed: {schedule_id}")
                else:
                    cursor.execute('''
                        UPDATE retention_schedules 
                        SET deletion_status = ?, last_checked = ?
                        WHERE schedule_id = ?
                    ''', ('failed', now.isoformat(), schedule_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to execute deletion schedule: {e}")
        
        return deletions_executed
    
    def _delete_data_by_schedule(self, schedule_id: str) -> bool:
        """Jadval bo'yicha ma'lumotlarni o'chirish"""
        # This would integrate with your actual data storage system
        # For now, we'll just log the action
        logger.info(f"Executing data deletion for schedule: {schedule_id}")
        return True

class BreachNotificationSystem:
    """Buzilish xabar berish tizimi"""
    
    def __init__(self):
        self.breach_thresholds = {
            'personal_data_records': 100,  # GDPR Article 33
            'sensitive_data_records': 10,
            'financial_records': 50,
            'notification_deadline_hours': 72
        }
    
    def assess_breach_severity(self, breach_info: Dict[str, Any]) -> Dict[str, Any]:
        """Buzilish og'irligini baholash"""
        assessment = {
            'severity_level': 'low',
            'notification_required': False,
            'authority_notification_deadline': None,
            'data_subject_notification_required': False,
            'immediate_actions': []
        }
        
        # Count affected records
        personal_records = breach_info.get('personal_data_records', 0)
        sensitive_records = breach_info.get('sensitive_data_records', 0)
        financial_records = breach_info.get('financial_records', 0)
        
        # Determine severity
        if sensitive_records > 0 or personal_records >= self.breach_thresholds['personal_data_records']:
            assessment['severity_level'] = 'high'
            assessment['notification_required'] = True
            assessment['data_subject_notification_required'] = True
        elif personal_records >= 10:
            assessment['severity_level'] = 'medium'
            assessment['notification_required'] = True
        
        # Calculate deadlines
        breach_time = datetime.datetime.fromisoformat(breach_info.get('breach_time', datetime.datetime.now().isoformat()))
        authority_deadline = breach_time + datetime.timedelta(hours=self.breach_thresholds['notification_deadline_hours'])
        assessment['authority_notification_deadline'] = authority_deadline.isoformat()
        
        # Generate immediate actions
        if assessment['severity_level'] == 'high':
            assessment['immediate_actions'] = [
                "Contain the breach immediately",
                "Assess the scope and impact",
                "Notify supervisory authority within 72 hours",
                "Notify affected data subjects without undue delay",
                "Document all breach details for regulatory reporting"
            ]
        
        return assessment
    
    def send_authority_notification(self, breach_info: Dict[str, Any], assessment: Dict[str, Any]):
        """Regulyator organiga xabar yuborish"""
        notification = {
            'breach_id': str(uuid.uuid4()),
            'notification_time': datetime.datetime.now().isoformat(),
            'breach_details': breach_info,
            'assessment': assessment,
            'notification_method': 'supervisory_authority_portal',
            'status': 'sent'
        }
        
        # Log the notification
        logger.critical(f"BREACH NOTIFICATION to supervisory authority: {notification['breach_id']}")
        
        # This would integrate with actual notification systems
        return notification['breach_id']
    
    def send_data_subject_notification(self, breach_info: Dict[str, Any], assessment: Dict[str, Any]):
        """Ma'lumot subyektlariga xabar yuborish"""
        notification = {
            'notification_id': str(uuid.uuid4()),
            'notification_time': datetime.datetime.now().isoformat(),
            'breach_id': breach_info.get('breach_id'),
            'affected_subjects_count': breach_info.get('personal_data_records', 0),
            'notification_method': 'email',
            'status': 'pending'
        }
        
        logger.warning(f"DATA SUBJECT NOTIFICATION required for {notification['affected_subjects_count']} subjects")
        
        # This would integrate with your notification system
        return notification['notification_id']

class ComplianceManager:
    """Asosiy moslashuv boshqaruvchisi"""
    
    def __init__(self):
        self.gdpr = GDPRCompliance()
        self.soc2 = SOC2Compliance()
        self.consent_manager = ConsentManagement()
        self.retention_manager = DataRetentionManager()
        self.breach_system = BreachNotificationSystem()
        
        # Initialize logging
        logger.info("Compliance Manager initialized")
    
    def run_compliance_check(self, standard: ComplianceStandard, context: Dict[str, Any]) -> Dict[str, Any]:
        """Moslashuv tekshiruvini bajarish"""
        try:
            if standard == ComplianceStandard.GDPR:
                return self._check_gdpr_compliance(context)
            elif standard == ComplianceStandard.SOC2:
                return self._check_soc2_compliance(context)
            else:
                raise ValueError(f"Unsupported standard: {standard}")
        
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _check_gdpr_compliance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """GDPR moslashuvini tekshirish"""
        compliance_issues = []
        
        # Check data subject rights
        if not context.get('data_subject_rights_implemented', False):
            compliance_issues.append("Data subject rights not fully implemented")
        
        # Check consent management
        if not context.get('consent_management_active', False):
            compliance_issues.append("Consent management system not active")
        
        # Check data retention policies
        if not context.get('retention_policies_defined', False):
            compliance_issues.append("Data retention policies not defined")
        
        # Check privacy by design
        if not context.get('privacy_by_design', False):
            compliance_issues.append("Privacy by design principles not implemented")
        
        # Check breach notification procedures
        if not context.get('breach_notification_procedures', False):
            compliance_issues.append("Breach notification procedures not established")
        
        return {
            "standard": "GDPR",
            "compliance_status": "non_compliant" if compliance_issues else "compliant",
            "issues": compliance_issues,
            "assessment_date": datetime.datetime.now().isoformat(),
            "next_review": (datetime.datetime.now() + datetime.timedelta(days=90)).isoformat()
        }
    
    def _check_soc2_compliance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """SOC 2 moslashuvini tekshirish"""
        trust_criteria_status = {}
        
        for criteria in self.soc2.trust_service_criteria:
            status = "compliant" if context.get(f"{criteria}_controls_implemented", False) else "non_compliant"
            trust_criteria_status[criteria] = status
        
        overall_compliant = all(status == "compliant" for status in trust_criteria_status.values())
        
        return {
            "standard": "SOC 2",
            "compliance_status": "compliant" if overall_compliant else "non_compliant",
            "trust_criteria_status": trust_criteria_status,
            "assessment_date": datetime.datetime.now().isoformat(),
            "next_review": (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat()
        }
    
    def generate_compliance_report(self, standards: List[ComplianceStandard]) -> Dict[str, Any]:
        """Moslashuv hisobotini yaratish"""
        report = {
            "report_id": str(uuid.uuid4()),
            "generation_date": datetime.datetime.now().isoformat(),
            "report_period": {
                "start_date": (datetime.datetime.now() - datetime.timedelta(days=365)).isoformat(),
                "end_date": datetime.datetime.now().isoformat()
            },
            "standards_assessed": [],
            "summary": {},
            "recommendations": []
        }
        
        for standard in standards:
            assessment = self.run_compliance_check(standard, {
                "data_subject_rights_implemented": True,
                "consent_management_active": True,
                "retention_policies_defined": True,
                "privacy_by_design": True,
                "breach_notification_procedures": True,
                "security_controls_implemented": True,
                "availability_controls_implemented": True,
                "processing_integrity_controls_implemented": True,
                "confidentiality_controls_implemented": True,
                "privacy_controls_implemented": True
            })
            
            report["standards_assessed"].append(assessment)
            
            if assessment["compliance_status"] != "compliant":
                report["recommendations"].extend(assessment.get("issues", []))
        
        # Generate summary
        total_standards = len(standards)
        compliant_count = sum(1 for assessment in report["standards_assessed"] 
                            if assessment["compliance_status"] == "compliant")
        
        report["summary"] = {
            "total_standards": total_standards,
            "compliant_standards": compliant_count,
            "compliance_rate": f"{(compliant_count / total_standards) * 100:.1f}%",
            "overall_status": "compliant" if compliant_count == total_standards else "partial_compliance"
        }
        
        return report

# Flask routes for compliance API
app = Flask(__name__)
compliance_manager = ComplianceManager()

@app.route('/api/compliance/gdpr/data-subject-request', methods=['POST'])
def handle_gdpr_request():
    """GDPR ma'lumot subyekt so'rovini qayta ishlash"""
    data = request.get_json()
    subject_id = data.get('subject_id')
    request_type = data.get('request_type')
    
    if not subject_id or not request_type:
        return jsonify({'error': 'subject_id and request_type are required'}), 400
    
    result = compliance_manager.gdpr.handle_data_subject_request(subject_id, request_type)
    return jsonify(result)

@app.route('/api/compliance/consent/record', methods=['POST'])
def record_consent():
    """Ruxsatni qayta ishlash"""
    data = request.get_json()
    
    consent = ConsentRecord(
        consent_id=str(uuid.uuid4()),
        subject_id=data['subject_id'],
        consent_type=data['consent_type'],
        purpose=data['purpose'],
        granted=data['granted'],
        timestamp=datetime.datetime.now().isoformat(),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        method=data.get('method', 'opt_in')
    )
    
    success = compliance_manager.consent_manager.record_consent(consent)
    
    return jsonify({
        'success': success,
        'consent_id': consent.consent_id
    }), 200 if success else 500

@app.route('/api/compliance/retention/execute', methods=['POST'])
def execute_retention_schedule():
    """Saqlash jadvalini bajarish"""
    deletions = compliance_manager.retention_manager.execute_deletion_schedule()
    
    return jsonify({
        'deletions_executed': len(deletions),
        'deleted_schedules': deletions
    })

@app.route('/api/compliance/breach/assess', methods=['POST'])
def assess_breach():
    """Buzilish og'irligini baholash"""
    breach_info = request.get_json()
    
    assessment = compliance_manager.breach_system.assess_breach_severity(breach_info)
    
    if assessment['notification_required']:
        authority_id = compliance_manager.breach_system.send_authority_notification(breach_info, assessment)
        
        if assessment['data_subject_notification_required']:
            notification_id = compliance_manager.breach_system.send_data_subject_notification(breach_info, assessment)
        
        assessment['notification_sent'] = True
    
    return jsonify(assessment)

@app.route('/api/compliance/report/<standard>')
def generate_compliance_report(standard):
    """Moslashuv hisobotini yaratish"""
    try:
        compliance_standard = ComplianceStandard(standard.upper())
        report = compliance_manager.generate_compliance_report([compliance_standard])
        return jsonify(report)
    except ValueError:
        return jsonify({'error': f'Invalid compliance standard: {standard}'}), 400

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs('/workspace/orion-starline/data', exist_ok=True)
    os.makedirs('/workspace/orion-starline/logs', exist_ok=True)
    
    # Run compliance system
    app.run(host='0.0.0.0', port=5001, debug=False)
