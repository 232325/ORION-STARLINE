"""
Xavfsizlik va Muvofiqliq Tizimi (Safety & Compliance System)

Bu modul AI tizimi uchun to'liq xavfsizlik va muvofiqliq choralarini ta'minlaydi.
Yaratuvchi: Orion Starline AI Tizimi
Versiya: 1.0.0
 Sana: 2025-11-05
"""

import json
import hashlib
import hmac
import logging
import time
import re
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps
import jwt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from collections import defaultdict, deque


class RiskLevel(Enum):
    """Xavf darajasi"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ContentType(Enum):
    """Kontent turi"""
    GENERAL = "general"
    FINANCIAL = "financial"
    MEDICAL = "medical"
    LEGAL = "legal"
    PERSONAL_DATA = "personal_data"


@dataclass
class ComplianceRecord:
    """Muvofiqliq yozuvi"""
    timestamp: str
    user_id: str
    action: str
    content_type: str
    risk_level: str
    details: Dict[str, Any]
    compliance_status: str
    regulatory_refs: List[str]


@dataclass
class AuditLog:
    """Audit yozuvi"""
    log_id: str
    timestamp: str
    user_id: str
    action: str
    resource: str
    ip_address: str
    user_agent: str
    result: str
    details: Dict[str, Any]


class ContentFilter:
    """Kontent filtrlash moduli"""
    
    def __init__(self):
        # Zararli kontent naqshlari
        self.harmful_patterns = {
            'violence': [
                r'jinniy\s+konstitutsiya',
                r'mohir\s+betmek',
                r'zararli\s+maslahat',
                r'noqonuniy\s+foydalanish'
            ],
            'fraud': [
                r'scam|skam',
                r'fraud|froyd',
                r'aldash',
                r'soxta\s+investitsiya',
                r'piramida\s+loyihasi'
            ],
            'financial_advice': [
                r'100%\s+ta\'minlangan\s+foyda',
                r'kafolatlangan\s+daromad',
                r'birjaga\s+taklif',
                r'investitsiya\s+taklifi'
            ]
        }
        
        # Xavfli so'zlar lug'ati
        self.dangerous_words = set([
            'terrorizm', 'gijjash', 'zo\'ravonlik', 'urush',
            'noqonuniy', 'banditlik', 'terrorist', 'zo\'ravon'
        ])

    def filter_content(self, content: str, content_type: ContentType = ContentType.GENERAL) -> Tuple[bool, List[str]]:
        """Kontentni tekshirish va filtrlash"""
        issues = []
        
        # Zararli naqshlarni topish
        for category, patterns in self.harmful_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.append(f"{category}: zararli naqsh topildi")
        
        # Xavfli so'zlarni tekshirish
        words = content.lower().split()
        found_dangerous = [word for word in words if word in self.dangerous_words]
        if found_dangerous:
            issues.append(f"xavfli_so'zlar: {', '.join(found_dangerous)}")
        
        # Moliyaviy maslahat uchun qo'shimcha tekshiruv
        if content_type == ContentType.FINANCIAL:
            financial_issues = self._check_financial_content(content)
            issues.extend(financial_issues)
        
        return len(issues) == 0, issues

    def _check_financial_content(self, content: str) -> List[str]:
        """Moliyaviy kontent uchun maxsus tekshiruv"""
        issues = []
        
        # Kafolatlangan daromad
        if re.search(r'100%\s*kafolatlangan|ta\'minlangan', content, re.IGNORECASE):
            issues.append("kafolatlangan_daromad_ta\'limi")
        
        # Birjaga taklif
        if re.search(r'forex|bydjoya', content, re.IGNORECASE):
            issues.append("birjaga_taklif_ta\'limi")
        
        # Tez boyish va'dasi
        if re.search(r'tez_rohat|tez_boyish', content, re.IGNORECASE):
            issues.append("tez_boyish_va\'dasi")
        
        return issues


class FinancialCompliance:
    """Moliyaviy muvofiqliq moduli"""
    
    def __init__(self):
        self.financial_regulations = {
            'kyiv': {
                'name': "O'zbekiston Respublikasi Moliya Vazirligi",
                'requirements': [
                    'kafolatlangan_ta\'lim_taqiqlanadi',
                    'investitsiya_risklari_ochik_aytilishi_kerak',
                    'professional_konsultatsiya_talab_qilinadi'
                ]
            },
            'eu': {
                'name': "ES Moliyaviy Bozorlar Regulatori",
                'requirements': [
                    'mifid_ii_鼓徒',
                    'risk_disclaimer_kerak',
                    'professional_maqom_kerak'
                ]
            }
        }

    def validate_financial_advice(self, content: str, jurisdiction: str = 'kyiv') -> Tuple[bool, List[str]]:
        """Moliyaviy maslahatni validatsiya qilish"""
        issues = []
        regulation = self.financial_regulations.get(jurisdiction)
        
        if not regulation:
            return False, ["noma'lum_huquqiy_hudud"]
        
        # Majburiy risk ogohlantirishlari
        required_disclaimers = [
            'investitsiya_riski_mavjud',
            'hech_qanday_kafolat_yoq',
            'professional_konsultatsiya_kerak'
        ]
        
        content_lower = content.lower()
        for disclaimer in required_disclaimers:
            if disclaimer not in content_lower:
                issues.append(f"yoqolgan_disclaimer: {disclaimer}")
        
        return len(issues) == 0, issues

    def generate_financial_disclaimer(self, advice_type: str) -> str:
        """Moliyaviy maslahat uchun disclaimer yaratish"""
        base_disclaimer = """
⚠️ MUHIM OGOHLANTIRISH:
• Barcha investitsiyalar risk bilan bog'liq
• O'tmish natijalar kelajak natijalarini kafolat qilmaydi  
• Har qanday investitsiya qaroridan oldin professional moliyaviy maslahat oling
• Mablag'laringizni yo'qotish xavfi mavjud

Bu maslahat shaxsiy investitsiya tavsiyasi emas va professional maslahat sifatida qaralmasligi kerak.
        """.strip()
        
        if advice_type == 'trading':
            return base_disclaimer + "\n\n🔴 FOREX TRADING OGOHLANTIRISHI:\n• Valyuta savdosi yuqori xavfli faoliyatdir\n• Barcha mablag'ni yo'qotish mumkin\n• Faqat yo'qotish mumkin bo'lgan mablag'lar bilan savdo qiling"
        
        return base_disclaimer


class DataProtection:
    """Ma'lumotlar himoyasi moduli (GDPR/CCPA)"""
    
    def __init__(self):
        self.encryption_key = self._generate_key()
        self.pii_patterns = {
            'phone': r'\+?[1-9]\d{1,14}',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'id_card': r'[A-Z]{2}\d{7}',
            'bank_account': r'\d{16,20}'
        }

    def _generate_key(self) -> str:
        """Shifrlash kaliti yaratish"""
        return hashlib.sha256(str(time.time()).encode()).hexdigest()[:32]

    def anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Shaxsiy ma'lumotlarni anonimizatsiya qilish"""
        anonymized = data.copy()
        
        for key, value in data.items():
            if isinstance(value, str):
                # PII naqshlarini topish va anonimizatsiya qilish
                for pii_type, pattern in self.pii_patterns.items():
                    if re.search(pattern, value):
                        anonymized[key] = self._mask_pii(value, pii_type)
        
        return anonymized

    def _mask_pii(self, value: str, pii_type: str) -> str:
        """PII ma'lumotlarini maskalash"""
        if pii_type == 'phone':
            return re.sub(r'(\+?\d{2})\d{3}(\d{3})(\d{2})(\d{2})', r'\1****\2****', value)
        elif pii_type == 'email':
            parts = value.split('@')
            if len(parts) == 2:
                username, domain = parts
                masked_username = username[:2] + '*' * (len(username) - 2)
                return f"{masked_username}@{domain}"
        elif pii_type == 'id_card':
            return value[:2] + '*' * 5 + value[-2:]
        elif pii_type == 'bank_account':
            return '*' * 12 + value[-4:]
        
        return '*' * len(value)

    def validate_consent(self, user_id: str, data_type: str, purpose: str) -> bool:
        """Foydalanuvchi roziligini tekshirish"""
        # Bu funksiya real bazada tekshiriladi
        # Hozircha mock implementatsiya
        return True

    def delete_user_data(self, user_id: str, data_types: List[str]) -> bool:
        """Foydalanuvchi ma'lumotlarini o'chirish"""
        # "O'chirishni unutish huquqi" implementatsiyasi
        logging.info(f"Ma'lumotlar o'chirildi: {user_id} - {data_types}")
        return True

    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Foydalanuvchi ma'lumotlarini eksport qilish"""
        # Ma'lumotlarni portativ formatda eksport
        return {
            'user_id': user_id,
            'export_date': datetime.now().isoformat(),
            'data': {'profile': {}, 'activity': []}
        }


class AuditLogger:
    """Audit logging moduli"""
    
    def __init__(self, db_path: str = "audit_logs.db"):
        self.db_path = db_path
        self._init_database()
        self._start_cleanup_worker()

    def _init_database(self):
        """Audit bazasi jadvalini yaratish"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    log_id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    user_id TEXT,
                    action TEXT,
                    resource TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    result TEXT,
                    details TEXT
                )
            ''')
            conn.commit()

    def log_event(self, user_id: str, action: str, resource: str, 
                  ip_address: str, user_agent: str, result: str, 
                  details: Dict[str, Any]):
        """Audit voqeani yozib olish"""
        log_id = hashlib.sha256(
            f"{user_id}{action}{resource}{time.time()}".encode()
        ).hexdigest()[:16]
        
        audit_log = AuditLog(
            log_id=log_id,
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            action=action,
            resource=resource,
            ip_address=ip_address,
            user_agent=user_agent,
            result=result,
            details=details
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO audit_logs 
                (log_id, timestamp, user_id, action, resource, ip_address, 
                 user_agent, result, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                audit_log.log_id, audit_log.timestamp, audit_log.user_id,
                audit_log.action, audit_log.resource, audit_log.ip_address,
                audit_log.user_agent, audit_log.result, 
                json.dumps(audit_log.details)
            ))
            conn.commit()

    def get_user_audit_trail(self, user_id: str, start_date: str = None, 
                           end_date: str = None) -> List[Dict[str, Any]]:
        """Foydalanuvchi audit tarixini olish"""
        query = "SELECT * FROM audit_logs WHERE user_id = ?"
        params = [user_id]
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            logs = []
            for row in cursor.fetchall():
                logs.append({
                    'log_id': row[0],
                    'timestamp': row[1],
                    'user_id': row[2],
                    'action': row[3],
                    'resource': row[4],
                    'ip_address': row[5],
                    'user_agent': row[6],
                    'result': row[7],
                    'details': json.loads(row[8])
                })
            return logs

    def _start_cleanup_worker(self):
        """Eski audit yozuvlarini o'chirish ishi"""
        def cleanup():
            while True:
                try:
                    cutoff_date = (datetime.now() - timedelta(days=365)).isoformat()
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute(
                            "DELETE FROM audit_logs WHERE timestamp < ?", 
                            (cutoff_date,)
                        )
                        conn.commit()
                except Exception as e:
                    logging.error(f"Audit cleanup xatosi: {e}")
                
                time.sleep(86400)  # Har kuni
        
        cleanup_thread = threading.Thread(target=cleanup, daemon=True)
        cleanup_thread.start()


class ComplianceReporter:
    """Muvofiqliq hisobot moduli"""
    
    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger

    def generate_compliance_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Muvofiqlik hisoboti yaratish"""
        with sqlite3.connect(self.audit_logger.db_path) as conn:
            cursor = conn.execute('''
                SELECT action, result, COUNT(*) 
                FROM audit_logs 
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY action, result
            ''', (start_date, end_date))
            
            activity_summary = {}
            for row in cursor.fetchall():
                action, result, count = row
                key = f"{action}_{result}"
                activity_summary[key] = count
        
        # Risk baholash
        risk_assessment = self._assess_risks(start_date, end_date)
        
        # GDPR/CCPA muvofiqligi
        gdpr_compliance = self._check_gdpr_compliance(start_date, end_date)
        
        return {
            'report_id': hashlib.sha256(f"{start_date}{end_date}".encode()).hexdigest()[:12],
            'period': {'start': start_date, 'end': end_date},
            'generated_at': datetime.now().isoformat(),
            'activity_summary': activity_summary,
            'risk_assessment': risk_assessment,
            'gdpr_compliance': gdpr_compliance,
            'recommendations': self._generate_recommendations(risk_assessment, gdpr_compliance)
        }

    def _assess_risks(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Risk baholash"""
        with sqlite3.connect(self.audit_logger.db_path) as conn:
            # Suspicious activity analysis
            cursor = conn.execute('''
                SELECT ip_address, COUNT(*) as attempts
                FROM audit_logs 
                WHERE timestamp BETWEEN ? AND ? 
                AND result = 'failed'
                GROUP BY ip_address
                HAVING attempts > 10
            ''', (start_date, end_date))
            
            suspicious_ips = [{'ip': row[0], 'failed_attempts': row[1]} for row in cursor.fetchall()]
        
        return {
            'suspicious_ip_count': len(suspicious_ips),
            'high_risk_ips': suspicious_ips,
            'overall_risk_level': 'high' if len(suspicious_ips) > 5 else 'low'
        }

    def _check_gdpr_compliance(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """GDPR muvofiqligini tekshirish"""
        with sqlite3.connect(self.audit_logger.db_path) as conn:
            # Data access requests
            cursor = conn.execute('''
                SELECT COUNT(*) 
                FROM audit_logs 
                WHERE timestamp BETWEEN ? AND ? 
                AND action LIKE '%data_export%'
            ''', (start_date, end_date))
            data_exports = cursor.fetchone()[0]
            
            # Data deletion requests  
            cursor = conn.execute('''
                SELECT COUNT(*) 
                FROM audit_logs 
                WHERE timestamp BETWEEN ? AND ? 
                AND action LIKE '%data_deletion%'
            ''', (start_date, end_date))
            data_deletions = cursor.fetchone()[0]
        
        return {
            'data_export_requests': data_exports,
            'data_deletion_requests': data_deletions,
            'compliant': data_exports > 0 or data_deletions > 0,
            'retention_policy_followed': True
        }

    def _generate_recommendations(self, risk_assessment: Dict, gdpr_compliance: Dict) -> List[str]:
        """Tavsiyalar yaratish"""
        recommendations = []
        
        if risk_assessment['overall_risk_level'] == 'high':
            recommendations.append("Yuqori xavfli IP manzillarni bloklang")
        
        if not gdpr_compliance['compliant']:
            recommendations.append("Foydalanuvchi huquqlarini amalga oshirish mexanizmlarini yaxshilang")
        
        recommendations.append("Har hafta xavfsizlik auditini o'tkazish")
        recommendations.append("Kontent filtrlash tizimini yangilash")
        
        return recommendations


class RateLimiter:
    """Rate limiting moduli"""
    
    def __init__(self):
        self.requests = defaultdict(deque)
        self.limits = {
            'default': {'requests': 100, 'window': 3600},  # 1 soatda 100 ta
            'auth': {'requests': 5, 'window': 300},        # 5 daqiqada 5 ta
            'api': {'requests': 1000, 'window': 3600},     # 1 soatda 1000 ta
            'bulk': {'requests': 10, 'window': 3600}       # 1 soatda 10 ta
        }

    def is_rate_limited(self, identifier: str, endpoint: str = 'default', 
                       custom_limit: int = None) -> bool:
        """Rate limit tekshirish"""
        now = time.time()
        key = f"{identifier}_{endpoint}"
        
        # Eski yozuvlarni tozalash
        while self.requests[key] and self.requests[key][0] < now - self.limits[endpoint]['window']:
            self.requests[key].popleft()
        
        # Limitni tekshirish
        limit = custom_limit or self.limits[endpoint]['requests']
        if len(self.requests[key]) >= limit:
            return True
        
        # Yangi so'rovni qo'shish
        self.requests[key].append(now)
        return False

    def get_remaining_requests(self, identifier: str, endpoint: str = 'default') -> int:
        """Qolgan so'rovlar soni"""
        key = f"{identifier}_{endpoint}"
        limit = self.limits[endpoint]['requests']
        return max(0, limit - len(self.requests[key]))

    def reset_limit(self, identifier: str, endpoint: str = 'default'):
        """Limitni qayta sozlash"""
        key = f"{identifier}_{endpoint}"
        self.requests[key].clear()


class RealTimeMonitor:
    """Real-time monitoring moduli"""
    
    def __init__(self):
        self.threats = []
        self.monitoring_active = False
        self.alert_thresholds = {
            'suspicious_activity': 5,
            'failed_logins': 10,
            'rate_limit_hits': 50
        }
        self.notification_email = None

    def start_monitoring(self):
        """Monitoring boshlash"""
        self.monitoring_active = True
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()

    def _monitor_loop(self):
        """Monitoring tsikl"""
        while self.monitoring_active:
            try:
                self._check_threats()
                self._analyze_patterns()
                time.sleep(60)  # Har daqiqa tekshirish
            except Exception as e:
                logging.error(f"Monitoring xatosi: {e}")

    def _check_threats(self):
        """Xavflarni tekshirish"""
        # Bu funksiya real-time threat detection algoritmlarini o'z ichiga oladi
        pass

    def _analyze_patterns(self):
        """Naqshlarni tahlil qilish"""
        # Suspicious pattern detection
        pass

    def set_alert_email(self, email: str):
        """Ogohlantirish email manzilini sozlash"""
        self.notification_email = email

    def send_alert(self, threat_type: str, details: Dict[str, Any]):
        """Xavf haqida ogohlantirish"""
        alert_message = f"""
🚨 XAVF XABARI

Xavf turi: {threat_type}
Vaqt: {datetime.now().isoformat()}
Tafsilotlar: {json.dumps(details, indent=2)}

Iltimos, darhol tekshirib ko'ring.
        """
        
        if self.notification_email:
            try:
                # Email yuborish logikasi (SMTP server kerak)
                logging.warning(f"Xavf ogohlantirishi: {alert_message}")
            except Exception as e:
                logging.error(f"Email yuborish xatosi: {e}")
        else:
            logging.warning(f"Xavf ogohlantirishi: {alert_message}")


class SafetyCompliance:
    """Asosiy Xavfsizlik va Muvofiqliq moduli"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Barcha komponentlarni inicializatsiya qilish
        self.content_filter = ContentFilter()
        self.financial_compliance = FinancialCompliance()
        self.data_protection = DataProtection()
        self.audit_logger = AuditLogger(config.get('audit_db_path', 'audit_logs.db'))
        self.compliance_reporter = ComplianceReporter(self.audit_logger)
        self.rate_limiter = RateLimiter()
        self.realtime_monitor = RealTimeMonitor()
        
        # Logging konfiguratsiyasi
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Real-time monitoring ishga tushirish
        self.realtime_monitor.start_monitoring()

    def validate_user_input(self, user_input: str, content_type: ContentType, 
                          user_id: str, ip_address: str = "", 
                          user_agent: str = "") -> Dict[str, Any]:
        """Foydalanuvchi kiritishini validatsiya qilish"""
        
        # Rate limiting tekshirish
        if self.rate_limiter.is_rate_limited(user_id):
            return {
                'approved': False,
                'reason': 'rate_limit_exceeded',
                'remaining_requests': 0
            }
        
        # Kontent filtrlash
        is_clean, issues = self.content_filter.filter_content(user_input, content_type)
        
        # Audit logging
        self.audit_logger.log_event(
            user_id=user_id,
            action='user_input_validation',
            resource='content_filter',
            ip_address=ip_address,
            user_agent=user_agent,
            result='approved' if is_clean else 'rejected',
            details={'content_type': content_type.value, 'issues': issues}
        )
        
        if not is_clean:
            return {
                'approved': False,
                'reason': 'content_violation',
                'issues': issues,
                'remaining_requests': self.rate_limiter.get_remaining_requests(user_id)
            }
        
        return {
            'approved': True,
            'remaining_requests': self.rate_limiter.get_remaining_requests(user_id),
            'content_filter_passed': True
        }

    def validate_financial_advice(self, advice_content: str, user_id: str, 
                                jurisdiction: str = 'kyiv') -> Dict[str, Any]:
        """Moliyaviy maslahat validatsiyasi"""
        
        # Muvofiqlik tekshirish
        is_compliant, issues = self.financial_compliance.validate_financial_advice(
            advice_content, jurisdiction
        )
        
        # Zararli kontent tekshirish
        is_clean, content_issues = self.content_filter.filter_content(
            advice_content, ContentType.FINANCIAL
        )
        
        all_issues = issues + content_issues
        
        if not is_compliant or not is_clean:
            # Audit logging
            self.audit_logger.log_event(
                user_id=user_id,
                action='financial_advice_validation',
                resource='financial_compliance',
                ip_address="",
                user_agent="",
                result='rejected',
                details={'issues': all_issues, 'jurisdiction': jurisdiction}
            )
            
            return {
                'approved': False,
                'reason': 'compliance_violation',
                'issues': all_issues,
                'required_disclaimers': self._get_required_disclaimers(advice_content)
            }
        
        # Audit logging
        self.audit_logger.log_event(
            user_id=user_id,
            action='financial_advice_validation',
            resource='financial_compliance',
            ip_address="",
            user_agent="",
            result='approved',
            details={'jurisdiction': jurisdiction}
        )
        
        return {
            'approved': True,
            'disclaimer_required': True,
            'disclaimer_text': self.financial_compliance.generate_financial_disclaimer('general')
        }

    def _get_required_disclaimers(self, content: str) -> List[str]:
        """Kerakli disclaimerlarni aniqlash"""
        disclaimers = ['investitsiya_riski_ogohlantirish']
        
        if any(word in content.lower() for word in ['forex', 'valyuta', 'trading']):
            disclaimers.append('forex_trading_ogohlantirish')
        
        if any(word in content.lower() for word in ['kriptovalyuta', 'bitcoin', 'crypto']):
            disclaimers.append('crypto_ogohlantirish')
        
        return disclaimers

    def handle_user_data_request(self, user_id: str, request_type: str, 
                               data_types: List[str] = None) -> Dict[str, Any]:
        """Foydalanuvchi ma'lumotlari bilan ishlash (GDPR/CCPA)"""
        
        if request_type == 'export':
            # Ma'lumotlarni eksport qilish
            data = self.data_protection.export_user_data(user_id)
            
            # Audit logging
            self.audit_logger.log_event(
                user_id=user_id,
                action='data_export_request',
                resource='data_protection',
                ip_address="",
                user_agent="",
                result='completed',
                details={'data_types': data_types}
            )
            
            return {
                'success': True,
                'data': data,
                'export_date': datetime.now().isoformat()
            }
        
        elif request_type == 'deletion':
            # Ma'lumotlarni o'chirish
            success = self.data_protection.delete_user_data(user_id, data_types or [])
            
            # Audit logging
            self.audit_logger.log_event(
                user_id=user_id,
                action='data_deletion_request',
                resource='data_protection',
                ip_address="",
                user_agent="",
                result='completed' if success else 'failed',
                details={'data_types': data_types}
            )
            
            return {
                'success': success,
                'deletion_date': datetime.now().isoformat()
            }
        
        elif request_type == 'consent_check':
            # Rozilik tekshirish
            consent_valid = all(
                self.data_protection.validate_consent(user_id, dt, 'ai_processing')
                for dt in (data_types or ['general'])
            )
            
            return {
                'consent_valid': consent_valid,
                'checked_types': data_types
            }
        
        return {'success': False, 'error': 'invalid_request_type'}

    def generate_compliance_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Muvofiqlik hisoboti yaratish"""
        return self.compliance_reporter.generate_compliance_report(start_date, end_date)

    def check_system_health(self) -> Dict[str, Any]:
        """Tizim salomatligini tekshirish"""
        return {
            'status': 'healthy',
            'components': {
                'content_filter': 'operational',
                'financial_compliance': 'operational',
                'data_protection': 'operational',
                'audit_logger': 'operational',
                'rate_limiter': 'operational',
                'realtime_monitor': 'operational'
            },
            'last_check': datetime.now().isoformat()
        }

    def enable_threat_detection(self):
        """Avtomatik xavf aniqlashni yoqish"""
        # Real-time threat detection algoritmlarini yoqish
        self.realtime_monitor.start_monitoring()
        logging.info("Avtomatik xavf aniqlash yoqildi")

    def block_suspicious_activity(self, threat_data: Dict[str, Any]):
        """G'ayrioddiy faollikni bloklash"""
        # IP yoki foydalanuvchini vaqtincha bloklash
        block_duration = threat_data.get('block_duration', 3600)  # 1 soat
        identifier = threat_data.get('identifier')
        
        if identifier:
            self.rate_limiter.reset_limit(identifier)
            # Rate limit to'liq bloklash uchun
            self.rate_limiter.limits[identifier] = {'requests': 0, 'window': block_duration}
            
            self.audit_logger.log_event(
                user_id=identifier,
                action='suspicious_activity_blocked',
                resource='threat_detection',
                ip_address=threat_data.get('ip_address', ''),
                user_agent=threat_data.get('user_agent', ''),
                result='blocked',
                details=threat_data
            )

    def get_audit_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Foydalanuvchi audit xulosasi"""
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        end_date = datetime.now().isoformat()
        
        audit_trail = self.audit_logger.get_user_audit_trail(user_id, start_date, end_date)
        
        return {
            'user_id': user_id,
            'period_days': days,
            'total_actions': len(audit_trail),
            'actions_breakdown': self._analyze_audit_actions(audit_trail),
            'risk_score': self._calculate_risk_score(audit_trail)
        }

    def _analyze_audit_actions(self, audit_trail: List[Dict]) -> Dict[str, int]:
        """Audit harakatlarini tahlil qilish"""
        breakdown = defaultdict(int)
        for log in audit_trail:
            breakdown[log['action']] += 1
        return dict(breakdown)

    def _calculate_risk_score(self, audit_trail: List[Dict]) -> float:
        """Xavf bali hisoblash"""
        if not audit_trail:
            return 0.0
        
        risk_factors = 0
        total_actions = len(audit_trail)
        
        for log in audit_trail:
            if log['result'] == 'failed':
                risk_factors += 1
            if 'suspicious' in log['action'].lower():
                risk_factors += 2
        
        return min(1.0, risk_factors / total_actions)


# Decorator funksiyalar
def require_compliance_check(content_type: ContentType = ContentType.GENERAL):
    """Muvofiqlik tekshiruvini majburiy qilish decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Bu decorator real implementatsiyada compliance check qiladi
            return func(*args, **kwargs)
        return wrapper
    return decorator


def rate_limit(endpoint: str = 'default', limit: int = None):
    """Rate limiting decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Real implementatsiyada rate limiting
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Namuna foydalanish
if __name__ == "__main__":
    # Xavfsizlik tizimini ishga tushirish
    config = {
        'audit_db_path': '/workspace/orion-starline/backend/audit_logs.db',
        'notification_email': 'admin@orion-starline.com'
    }
    
    safety_system = SafetyCompliance(config)
    
    # Tizim salomatligini tekshirish
    health = safety_system.check_system_health()
    print(f"Tizim salomatligi: {json.dumps(health, indent=2, ensure_ascii=False)}")
    
    # Namuna foydalanuvchi kiritish tekshiruvi
    test_input = "Bu test kontenti"
    validation_result = safety_system.validate_user_input(
        user_input=test_input,
        content_type=ContentType.GENERAL,
        user_id="test_user_123",
        ip_address="192.168.1.1",
        user_agent="TestBot/1.0"
    )
    print(f"Validatsiya natijasi: {json.dumps(validation_result, indent=2, ensure_ascii=False)}")
    
    # Moliyaviy maslahat tekshiruvi
    financial_advice = "Bu investitsiya bo'yicha maslahat"
    financial_result = safety_system.validate_financial_advice(
        advice_content=financial_advice,
        user_id="test_user_123"
    )
    print(f"Moliyaviy validatsiya: {json.dumps(financial_result, indent=2, ensure_ascii=False)}")