"""
Metal Certification System for Physical Metal-backed NFT Authentication
"""

import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class MetalType(Enum):
    GOLD = "gold"
    SILVER = "silver"
    PLATINUM = "platinum"
    PALLADIUM = "palladium"
    RHODIUM = "rhodium"
    RUTHENIUM = "ruthenium"

class CertificationStatus(Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"

class StorageFacility(Enum):
    BRINK_S = "brink_s"
    MALCA_AMIT = "malca_amit"
    DELOITTE_VAULT = "deloitte_vault"
    CANTOR_VAULT = "cantor_vault"
    HSBC_VAULT = "hsbc_vault"
    CUSTOM = "custom"

@dataclass
class AssayCertificate:
    certificate_id: str
    laboratory_name: str
    assay_date: str
    metal_type: MetalType
    weight: float  # in grams
    purity: float  # percentage
    dimensions: Optional[Dict] = None
    serial_number: Optional[str] = None
    laboratory_signature: Optional[str] = None
    digital_hash: Optional[str] = None

@dataclass
class StorageCertificate:
    certificate_id: str
    facility_name: str
    facility_address: str
    vault_number: str
    storage_start_date: str
    storage_end_date: Optional[str] = None
    insurance_provider: str
    insurance_policy_number: str
    insurance_value: float
    facility_signature: Optional[str] = None

@dataclass
class AuditRecord:
    audit_id: str
    auditor_name: str
    audit_date: str
    audit_type: str  # "physical", "digital", "comprehensive"
    findings: str
    compliance_score: float  # 0-100
    recommendations: List[str]

@dataclass
class MetalCertification:
    certification_id: str
    token_id: str
    contract_address: str
    mint_date: str
    status: CertificationStatus
    
    # Core certificates
    assay_certificate: AssayCertificate
    storage_certificate: StorageCertificate
    
    # Additional verification
    audit_records: List[AuditRecord]
    insurance_documents: List[str]
    legal_compliance: Dict
    
    # Metadata
    created_at: str
    updated_at: str
    verifier_signature: Optional[str] = None

class MetalCertificationSystem:
    """Main class for managing metal certifications"""
    
    def __init__(self):
        self.certifications: Dict[str, MetalCertification] = {}
        self.authorized_laboratories: Dict[str, Dict] = {}
        self.authorized_facilities: Dict[str, Dict] = {}
        self.authorized_auditors: Dict[str, Dict] = {}
        self.load_authorized_entities()
    
    def load_authorized_entities(self):
        """Load authorized entities for certification"""
        
        # Authorized assay laboratories
        self.authorized_laboratories = {
            "assay_lab_1": {
                "name": "Metal Testing Laboratory Inc.",
                "accreditation": "ISO 17025",
                "address": "123 Metal St, Testing City, TC 12345",
                "contact": "+1-555-0123",
                "public_key": "0x1234567890abcdef",
                "capabilities": ["fire_assay", "xrf_testing", "density_testing"]
            },
            "assay_lab_2": {
                "name": "Precise Metallurgical Services",
                "accreditation": "NIST Traceable",
                "address": "456 Precision Ave, Metallurgy City, MC 67890",
                "contact": "+1-555-0456",
                "public_key": "0xabcdef1234567890",
                "capabilities": ["fire_assay", "icp_testing", "ultrasonic_testing"]
            }
        }
        
        # Authorized storage facilities
        self.authorized_facilities = {
            "brink_s": {
                "name": "Brink's Global Services",
                "type": StorageFacility.BRINK_S,
                "locations": ["New York", "London", "Singapore", "Hong Kong"],
                "insurance_limit": 1000000000,  # $1B
                "security_rating": "AAA",
                "audit_frequency": "monthly"
            },
            "malca_amit": {
                "name": "Malca-Amit Global",
                "type": StorageFacility.MALCA_AMIT,
                "locations": ["London", "New York", "Singapore", "Hong Kong"],
                "insurance_limit": 750000000,  # $750M
                "security_rating": "AAA",
                "audit_frequency": "monthly"
            },
            "deloitte_vault": {
                "name": "Deloitte Secure Vault",
                "type": StorageFacility.DELOITTE_VAULT,
                "locations": ["Zurich", "London", "New York"],
                "insurance_limit": 500000000,  # $500M
                "security_rating": "AA+",
                "audit_frequency": "quarterly"
            }
        }
        
        # Authorized auditors
        self.authorized_auditors = {
            "deloitte_audit": {
                "name": "Deloitte & Touche LLP",
                "specialization": "Precious Metals Auditing",
                "license": "CPA-123456",
                "contact": "audit@deloitte.com"
            },
            "pwc_audit": {
                "name": "PricewaterhouseCoopers LLP",
                "specialization": "Commodity Auditing",
                "license": "CPA-789012",
                "contact": "audit@pwc.com"
            }
        }
    
    def generate_certificate_hash(self, data: Dict) -> str:
        """Generate SHA-256 hash for certificate data"""
        data_string = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def create_assay_certificate(
        self,
        laboratory_id: str,
        metal_type: MetalType,
        weight: float,
        purity: float,
        dimensions: Optional[Dict] = None,
        serial_number: Optional[str] = None
    ) -> AssayCertificate:
        """Create assay certificate"""
        
        if laboratory_id not in self.authorized_laboratories:
            raise ValueError(f"Unauthorized laboratory: {laboratory_id}")
        
        certificate_id = f"ASSAY-{uuid.uuid4().hex[:8].upper()}"
        assay_date = datetime.now().isoformat()
        
        # Create certificate data
        cert_data = {
            "certificate_id": certificate_id,
            "laboratory_id": laboratory_id,
            "metal_type": metal_type.value,
            "weight": weight,
            "purity": purity,
            "assay_date": assay_date,
            "dimensions": dimensions,
            "serial_number": serial_number
        }
        
        # Generate digital hash
        digital_hash = self.generate_certificate_hash(cert_data)
        
        certificate = AssayCertificate(
            certificate_id=certificate_id,
            laboratory_name=self.authorized_laboratories[laboratory_id]["name"],
            assay_date=assay_date,
            metal_type=metal_type,
            weight=weight,
            purity=purity,
            dimensions=dimensions,
            serial_number=serial_number,
            digital_hash=digital_hash
        )
        
        return certificate
    
    def create_storage_certificate(
        self,
        facility_id: str,
        vault_number: str,
        storage_start_date: str,
        insurance_provider: str,
        insurance_policy_number: str,
        insurance_value: float
    ) -> StorageCertificate:
        """Create storage certificate"""
        
        if facility_id not in self.authorized_facilities:
            raise ValueError(f"Unauthorized storage facility: {facility_id}")
        
        facility = self.authorized_facilities[facility_id]
        certificate_id = f"STOR-{uuid.uuid4().hex[:8].upper()}"
        
        certificate = StorageCertificate(
            certificate_id=certificate_id,
            facility_name=facility["name"],
            facility_address=f"{facility['locations'][0]}, Main Vault",
            vault_number=vault_number,
            storage_start_date=storage_start_date,
            insurance_provider=insurance_provider,
            insurance_policy_number=insurance_policy_number,
            insurance_value=insurance_value
        )
        
        return certificate
    
    def create_metal_certification(
        self,
        token_id: str,
        contract_address: str,
        assay_certificate: AssayCertificate,
        storage_certificate: StorageCertificate,
        insurance_documents: List[str],
        legal_compliance: Dict
    ) -> MetalCertification:
        """Create complete metal certification"""
        
        certification_id = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        current_time = datetime.now().isoformat()
        
        certification = MetalCertification(
            certification_id=certification_id,
            token_id=token_id,
            contract_address=contract_address,
            mint_date=current_time,
            status=CertificationStatus.PENDING,
            assay_certificate=assay_certificate,
            storage_certificate=storage_certificate,
            audit_records=[],
            insurance_documents=insurance_documents,
            legal_compliance=legal_compliance,
            created_at=current_time,
            updated_at=current_time
        )
        
        self.certifications[certification_id] = certification
        return certification
    
    def verify_assay_certificate(self, certificate_id: str) -> Tuple[bool, str]:
        """Verify assay certificate authenticity"""
        for cert in self.certifications.values():
            if cert.assay_certificate.certificate_id == certificate_id:
                # Verify laboratory authorization
                lab_name = cert.assay_certificate.laboratory_name
                is_authorized = any(
                    lab["name"] == lab_name 
                    for lab in self.authorized_laboratories.values()
                )
                
                if is_authorized:
                    # Verify digital hash
                    cert_data = asdict(cert.assay_certificate)
                    calculated_hash = self.generate_certificate_hash(cert_data)
                    hash_match = cert.assay_certificate.digital_hash == calculated_hash
                    
                    if hash_match:
                        return True, "Certificate verified successfully"
                    else:
                        return False, "Digital hash verification failed"
                else:
                    return False, "Laboratory not authorized"
        
        return False, "Certificate not found"
    
    def verify_storage_certificate(self, certificate_id: str) -> Tuple[bool, str]:
        """Verify storage certificate authenticity"""
        for cert in self.certifications.values():
            if cert.storage_certificate.certificate_id == certificate_id:
                # Verify facility authorization
                facility_name = cert.storage_certificate.facility_name
                is_authorized = any(
                    facility["name"] == facility_name 
                    for facility in self.authorized_facilities.values()
                )
                
                if is_authorized:
                    # Verify insurance
                    has_insurance = (
                        cert.storage_certificate.insurance_provider and
                        cert.storage_certificate.insurance_policy_number and
                        cert.storage_certificate.insurance_value > 0
                    )
                    
                    if has_insurance:
                        return True, "Storage certificate verified successfully"
                    else:
                        return False, "Insurance verification failed"
                else:
                    return False, "Storage facility not authorized"
        
        return False, "Certificate not found"
    
    def add_audit_record(
        self,
        certification_id: str,
        auditor_id: str,
        audit_type: str,
        findings: str,
        compliance_score: float,
        recommendations: List[str]
    ) -> bool:
        """Add audit record to certification"""
        
        if certification_id not in self.certifications:
            return False
        
        if auditor_id not in self.authorized_auditors:
            return False
        
        audit_record = AuditRecord(
            audit_id=f"AUDIT-{uuid.uuid4().hex[:8].upper()}",
            auditor_name=self.authorized_auditors[auditor_id]["name"],
            audit_date=datetime.now().isoformat(),
            audit_type=audit_type,
            findings=findings,
            compliance_score=compliance_score,
            recommendations=recommendations
        )
        
        self.certifications[certification_id].audit_records.append(audit_record)
        self.certifications[certification_id].updated_at = datetime.now().isoformat()
        
        return True
    
    def update_certification_status(
        self,
        certification_id: str,
        new_status: CertificationStatus,
        verifier_signature: str = None
    ) -> bool:
        """Update certification status"""
        
        if certification_id not in self.certifications:
            return False
        
        certification = self.certifications[certification_id]
        
        # Validate status transition
        valid_transitions = {
            CertificationStatus.PENDING: [CertificationStatus.VERIFIED, CertificationStatus.REJECTED],
            CertificationStatus.VERIFIED: [CertificationStatus.EXPIRED],
            CertificationStatus.REJECTED: [CertificationStatus.PENDING],
            CertificationStatus.EXPIRED: []
        }
        
        if new_status not in valid_transitions[certification.status]:
            return False
        
        certification.status = new_status
        certification.verifier_signature = verifier_signature
        certification.updated_at = datetime.now().isoformat()
        
        return True
    
    def get_certification_summary(self, certification_id: str) -> Optional[Dict]:
        """Get certification summary"""
        
        if certification_id not in self.certifications:
            return None
        
        cert = self.certifications[certification_id]
        
        return {
            "certification_id": cert.certification_id,
            "token_id": cert.token_id,
            "status": cert.status.value,
            "metal_type": cert.assay_certificate.metal_type.value,
            "weight": cert.assay_certificate.weight,
            "purity": cert.assay_certificate.purity,
            "storage_facility": cert.storage_certificate.facility_name,
            "insurance_value": cert.storage_certificate.insurance_value,
            "audit_count": len(cert.audit_records),
            "created_at": cert.created_at,
            "updated_at": cert.updated_at
        }
    
    def get_all_certifications(self) -> List[Dict]:
        """Get all certifications summary"""
        return [
            self.get_certification_summary(cert_id) 
            for cert_id in self.certifications.keys()
        ]
    
    def search_certifications(
        self,
        metal_type: Optional[MetalType] = None,
        status: Optional[CertificationStatus] = None,
        facility: Optional[str] = None
    ) -> List[Dict]:
        """Search certifications by criteria"""
        
        results = []
        
        for cert in self.certifications.values():
            # Apply filters
            if metal_type and cert.assay_certificate.metal_type != metal_type:
                continue
            
            if status and cert.status != status:
                continue
            
            if facility and facility.lower() not in cert.storage_certificate.facility_name.lower():
                continue
            
            results.append(self.get_certification_summary(cert.certification_id))
        
        return results
    
    def generate_compliance_report(self, certification_id: str) -> Optional[Dict]:
        """Generate compliance report for certification"""
        
        if certification_id not in self.certifications:
            return None
        
        cert = self.certifications[certification_id]
        
        # Calculate compliance metrics
        assay_verified, assay_message = self.verify_assay_certificate(cert.assay_certificate.certificate_id)
        storage_verified, storage_message = self.verify_storage_certificate(cert.storage_certificate.certificate_id)
        
        audit_scores = [record.compliance_score for record in cert.audit_records]
        avg_audit_score = sum(audit_scores) / len(audit_scores) if audit_scores else 0
        
        # Overall compliance score
        compliance_factors = [
            30 if assay_verified else 0,  # Assay verification weight
            30 if storage_verified else 0,  # Storage verification weight
            40 * (avg_audit_score / 100)  # Audit score weight
        ]
        
        overall_score = sum(compliance_factors)
        
        return {
            "certification_id": certification_id,
            "overall_compliance_score": overall_score,
            "assay_verified": assay_verified,
            "assay_details": assay_message,
            "storage_verified": storage_verified,
            "storage_details": storage_message,
            "audit_summary": {
                "total_audits": len(cert.audit_records),
                "average_score": avg_audit_score,
                "latest_audit_date": cert.audit_records[-1].audit_date if cert.audit_records else None
            },
            "legal_compliance": cert.legal_compliance,
            "report_generated_at": datetime.now().isoformat()
        }

# Example usage
def main():
    """Example usage of Metal Certification System"""
    
    # Initialize certification system
    cert_system = MetalCertificationSystem()
    
    # Create assay certificate
    assay_cert = cert_system.create_assay_certificate(
        laboratory_id="assay_lab_1",
        metal_type=MetalType.GOLD,
        weight=31.1035,  # 1 troy ounce
        purity=99.99,
        dimensions={"length": 32.7, "width": 32.7, "height": 2.87},
        serial_number="GOLD-001-2024"
    )
    
    print(f"Created assay certificate: {assay_cert.certificate_id}")
    print(f"Digital hash: {assay_cert.digital_hash}")
    
    # Create storage certificate
    storage_cert = cert_system.create_storage_certificate(
        facility_id="brink_s",
        vault_number="BR-001-A",
        storage_start_date=datetime.now().isoformat(),
        insurance_provider="Lloyd's of London",
        insurance_policy_number="POL-2024-001",
        insurance_value=50000.0
    )
    
    print(f"Created storage certificate: {storage_cert.certificate_id}")
    
    # Create metal certification
    certification = cert_system.create_metal_certification(
        token_id="1",
        contract_address="0x1234567890abcdef",
        assay_certificate=assay_cert,
        storage_certificate=storage_cert,
        insurance_documents=["insurance_policy.pdf"],
        legal_compliance={
            "aml_compliant": True,
            "kyc_verified": True,
            "tax_reporting": "compliant"
        }
    )
    
    print(f"Created metal certification: {certification.certification_id}")
    
    # Add audit record
    cert_system.add_audit_record(
        certification_id=certification.certification_id,
        auditor_id="deloitte_audit",
        audit_type="comprehensive",
        findings="All standards met. Excellent storage conditions.",
        compliance_score=95.0,
        recommendations=["Continue current storage protocols"]
    )
    
    # Verify certificates
    assay_verified, assay_message = cert_system.verify_assay_certificate(assay_cert.certificate_id)
    print(f"Assay verification: {assay_message}")
    
    storage_verified, storage_message = cert_system.verify_storage_certificate(storage_cert.certificate_id)
    print(f"Storage verification: {storage_message}")
    
    # Update status to verified
    cert_system.update_certification_status(
        certification_id=certification.certification_id,
        new_status=CertificationStatus.VERIFIED,
        verifier_signature="0xsignature123"
    )
    
    # Generate compliance report
    compliance_report = cert_system.generate_compliance_report(certification.certification_id)
    print(f"Compliance report: {json.dumps(compliance_report, indent=2)}")

if __name__ == "__main__":
    main()
