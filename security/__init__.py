"""
Korporativ Xavfsizlik Paketi
Enterprise Security Package

Bu paketa quyidagi xavfsizlik modullarini o'z ichiga oladi:

1. enterprise_security.py - Asosiy korporativ xavfsizlik tizimi
2. compliance.py - GDPR va SOC 2 moslashuv moduli  
3. audit_logging.py - Audit logging va forensik tahlil
4. encryption.py - End-to-end shifrlash tizimi
5. rbac.py - Role-based access control (RBAC)

Barcha modullar bir-biri bilan uyg'un ishlash uchun mo'ljallangan.
"""

from .enterprise_security import (
    EnterpriseSecuritySystem,
    SecurityEvent,
    SecurityPolicy,
    SecurityLevel,
    ThreatLevel,
    ComplianceStandard
)

from .compliance import (
    ComplianceManager,
    DataSubject,
    DataProcessingRecord,
    ConsentRecord,
    GDPRCompliance,
    SOC2Compliance,
    DataRetentionManager
)

from .audit_logging import (
    AuditLogger,
    AuditLog,
    AuditEventType,
    EventSeverity,
    BlockchainAuditTrail,
    AuditAnalyzer
)

from .encryption import (
    EncryptionSystem,
    EncryptionKey,
    EncryptedData,
    SymmetricEncryption,
    AsymmetricEncryption,
    HybridEncryption,
    KeyManager,
    MultiFactorAuthentication
)

from .rbac import (
    RBACSystem,
    User,
    Role,
    Permission,
    AccessControlEngine,
    PolicyEngine,
    EmergencyAccess
)

__version__ = "1.0.0"
__author__ = "Orion Starline Security Team"

# Barcha asosiy klasslarni eksport qilish
__all__ = [
    # Enterprise Security
    'EnterpriseSecuritySystem',
    'SecurityEvent',
    'SecurityPolicy',
    'SecurityLevel',
    'ThreatLevel',
    'ComplianceStandard',
    
    # Compliance
    'ComplianceManager',
    'DataSubject',
    'DataProcessingRecord',
    'ConsentRecord',
    'GDPRCompliance',
    'SOC2Compliance',
    'DataRetentionManager',
    
    # Audit Logging
    'AuditLogger',
    'AuditLog',
    'AuditEventType',
    'EventSeverity',
    'BlockchainAuditTrail',
    'AuditAnalyzer',
    
    # Encryption
    'EncryptionSystem',
    'EncryptionKey',
    'EncryptedData',
    'SymmetricEncryption',
    'AsymmetricEncryption',
    'HybridEncryption',
    'KeyManager',
    'MultiFactorAuthentication',
    
    # RBAC
    'RBACSystem',
    'User',
    'Role',
    'Permission',
    'AccessControlEngine',
    'PolicyEngine',
    'EmergencyAccess'
]
