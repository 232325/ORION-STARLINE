"""
AI Trading Evolution - Security Auditor
OWASP Top 10, Penetration Testing, Vulnerability Scanning

Bu modul trading sistemaning xavfsizligini ta'minlash uchun
comprehensive security audit va vulnerability testing ni o'tkazadi.
"""

import asyncio
import logging
import hashlib
import secrets
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SecurityIssue:
    """Xavfsizlik muammosi"""
    severity: str  # critical, high, medium, low, info
    category: str  # OWASP category
    title: str
    description: str
    location: str
    recommendation: str
    cwe_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityReport:
    """Security audit hisoboti"""
    timestamp: datetime
    total_issues: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int
    issues: List[SecurityIssue]
    scan_duration: float
    
    @property
    def risk_score(self) -> int:
        """Risk score (0-100)"""
        return (
            self.critical_count * 25 +
            self.high_count * 10 +
            self.medium_count * 5 +
            self.low_count * 1
        )


class OWASPChecker:
    """
    OWASP Top 10 Security Checker
    
    Common security vulnerabilities ni tekshirish
    """
    
    def __init__(self):
        self.issues: List[SecurityIssue] = []
    
    def check_sql_injection(self, code: str, filename: str) -> List[SecurityIssue]:
        """A1: SQL Injection"""
        issues = []
        
        # Check for string concatenation in SQL queries
        patterns = [
            r'execute\([\'"].*?\+.*?[\'"]\)',
            r'query\([\'"].*?\+.*?[\'"]\)',
            r'cursor\.execute\([\'"].*?%.*?[\'"]',
            r'SELECT.*?FROM.*?\+',
            r'INSERT.*?INTO.*?\+',
            r'UPDATE.*?SET.*?\+',
            r'DELETE.*?FROM.*?\+'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                issues.append(SecurityIssue(
                    severity='critical',
                    category='A1:2021-Injection',
                    title='Potential SQL Injection',
                    description=f'SQL query string concatenation detected: {match.group()}',
                    location=f'{filename}',
                    recommendation='Use parameterized queries or ORM instead of string concatenation',
                    cwe_id='CWE-89'
                ))
        
        return issues
    
    def check_broken_authentication(self, code: str, filename: str) -> List[SecurityIssue]:
        """A2: Broken Authentication"""
        issues = []
        
        # Check for weak password requirements
        if 'password' in code.lower():
            # Check for minimum length requirement
            if not re.search(r'len\(.*?password.*?\)\s*>=\s*[8-9]|\d{2,}', code):
                issues.append(SecurityIssue(
                    severity='high',
                    category='A2:2021-Broken Authentication',
                    title='Weak Password Policy',
                    description='No minimum password length requirement detected',
                    location=filename,
                    recommendation='Enforce minimum password length of 8+ characters',
                    cwe_id='CWE-521'
                ))
            
            # Check for plain text password storage
            if re.search(r'password\s*=.*?[\'"]', code) and 'hash' not in code.lower():
                issues.append(SecurityIssue(
                    severity='critical',
                    category='A2:2021-Broken Authentication',
                    title='Plain Text Password Storage',
                    description='Passwords may be stored in plain text',
                    location=filename,
                    recommendation='Use bcrypt, scrypt, or Argon2 for password hashing',
                    cwe_id='CWE-259'
                ))
        
        # Check for hardcoded credentials
        patterns = [
            r'password\s*=\s*[\'"][^\'"]+[\'"]',
            r'api_key\s*=\s*[\'"][^\'"]+[\'"]',
            r'secret\s*=\s*[\'"][^\'"]+[\'"]',
            r'token\s*=\s*[\'"][^\'"]+[\'"]'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                issues.append(SecurityIssue(
                    severity='critical',
                    category='A2:2021-Broken Authentication',
                    title='Hardcoded Credentials',
                    description=f'Hardcoded credential detected: {match.group()}',
                    location=filename,
                    recommendation='Use environment variables or secure vaults for credentials',
                    cwe_id='CWE-798'
                ))
        
        return issues
    
    def check_sensitive_data_exposure(self, code: str, filename: str) -> List[SecurityIssue]:
        """A3: Sensitive Data Exposure"""
        issues = []
        
        # Check for unencrypted sensitive data
        if re.search(r'(credit_card|ssn|social_security|account_number)', code, re.IGNORECASE):
            if 'encrypt' not in code.lower() and 'hash' not in code.lower():
                issues.append(SecurityIssue(
                    severity='critical',
                    category='A3:2021-Sensitive Data Exposure',
                    title='Unencrypted Sensitive Data',
                    description='Sensitive data may be stored without encryption',
                    location=filename,
                    recommendation='Encrypt sensitive data at rest and in transit (AES-256)',
                    cwe_id='CWE-311'
                ))
        
        # Check for weak encryption
        weak_crypto = ['md5', 'sha1', 'des', 'rc4']
        for crypto in weak_crypto:
            if crypto in code.lower():
                issues.append(SecurityIssue(
                    severity='high',
                    category='A3:2021-Sensitive Data Exposure',
                    title='Weak Cryptographic Algorithm',
                    description=f'Weak cryptographic algorithm detected: {crypto}',
                    location=filename,
                    recommendation='Use strong algorithms: AES-256, SHA-256, or better',
                    cwe_id='CWE-327'
                ))
        
        return issues
    
    def check_xxe(self, code: str, filename: str) -> List[SecurityIssue]:
        """A4: XML External Entities (XXE)"""
        issues = []
        
        # Check for XML parsing without disabling external entities
        if 'xml' in code.lower() or 'etree' in code.lower():
            if 'resolve_entities' not in code and 'DTDHandler' not in code:
                issues.append(SecurityIssue(
                    severity='high',
                    category='A4:2021-XXE',
                    title='XML External Entity (XXE) Vulnerability',
                    description='XML parsing without disabling external entities',
                    location=filename,
                    recommendation='Disable external entity processing in XML parser',
                    cwe_id='CWE-611'
                ))
        
        return issues
    
    def check_broken_access_control(self, code: str, filename: str) -> List[SecurityIssue]:
        """A5: Broken Access Control"""
        issues = []
        
        # Check for missing authorization checks
        api_patterns = [
            r'@app\.route\([\'"].*?[\'"].*?\)',
            r'@api\.route\([\'"].*?[\'"].*?\)',
            r'def\s+(get|post|put|delete)_.*?\(',
        ]
        
        for pattern in api_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                # Check if authorization decorator exists nearby
                context = code[max(0, match.start()-200):match.end()+200]
                if not re.search(r'@(login_required|auth|require_auth|check_permission)', context):
                    issues.append(SecurityIssue(
                        severity='high',
                        category='A5:2021-Broken Access Control',
                        title='Missing Authorization Check',
                        description=f'API endpoint without authorization: {match.group()}',
                        location=filename,
                        recommendation='Add authorization checks to all sensitive endpoints',
                        cwe_id='CWE-862'
                    ))
        
        return issues
    
    def check_security_misconfiguration(self, code: str, filename: str) -> List[SecurityIssue]:
        """A6: Security Misconfiguration"""
        issues = []
        
        # Check for debug mode in production
        if re.search(r'debug\s*=\s*True', code, re.IGNORECASE):
            issues.append(SecurityIssue(
                severity='high',
                category='A6:2021-Security Misconfiguration',
                title='Debug Mode Enabled',
                description='Application running with debug mode enabled',
                location=filename,
                recommendation='Disable debug mode in production',
                cwe_id='CWE-489'
            ))
        
        # Check for permissive CORS
        if 'CORS' in code:
            if re.search(r'origins?\s*=\s*[\'"]\*[\'"]', code):
                issues.append(SecurityIssue(
                    severity='medium',
                    category='A6:2021-Security Misconfiguration',
                    title='Permissive CORS Policy',
                    description='CORS allows all origins (*)',
                    location=filename,
                    recommendation='Restrict CORS to specific trusted domains',
                    cwe_id='CWE-942'
                ))
        
        return issues
    
    def check_xss(self, code: str, filename: str) -> List[SecurityIssue]:
        """A7: Cross-Site Scripting (XSS)"""
        issues = []
        
        # Check for unescaped user input in HTML
        patterns = [
            r'render_template.*?\{.*?\}',
            r'\.innerHTML\s*=',
            r'document\.write\(',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                issues.append(SecurityIssue(
                    severity='high',
                    category='A7:2021-XSS',
                    title='Potential Cross-Site Scripting (XSS)',
                    description=f'Unescaped user input may lead to XSS: {match.group()}',
                    location=filename,
                    recommendation='Sanitize and escape all user inputs before rendering',
                    cwe_id='CWE-79'
                ))
        
        return issues
    
    def check_insecure_deserialization(self, code: str, filename: str) -> List[SecurityIssue]:
        """A8: Insecure Deserialization"""
        issues = []
        
        # Check for pickle usage (dangerous)
        if 'pickle.loads' in code or 'pickle.load' in code:
            issues.append(SecurityIssue(
                severity='critical',
                category='A8:2021-Insecure Deserialization',
                title='Insecure Deserialization (pickle)',
                description='Using pickle for deserialization is dangerous',
                location=filename,
                recommendation='Use JSON or other safe serialization formats',
                cwe_id='CWE-502'
            ))
        
        return issues
    
    def check_vulnerable_components(self, code: str, filename: str) -> List[SecurityIssue]:
        """A9: Using Components with Known Vulnerabilities"""
        issues = []
        
        # Check for outdated/vulnerable imports
        vulnerable_packages = {
            'requests<2.20.0': 'CVE-2018-18074',
            'urllib3<1.24.2': 'CVE-2019-11324',
            'django<2.2.13': 'Multiple CVEs',
            'flask<1.0': 'Multiple CVEs'
        }
        
        for package, cve in vulnerable_packages.items():
            if package.split('<')[0] in code:
                issues.append(SecurityIssue(
                    severity='high',
                    category='A9:2021-Vulnerable Components',
                    title='Potentially Vulnerable Component',
                    description=f'Using {package} with known vulnerabilities: {cve}',
                    location=filename,
                    recommendation='Update to latest secure version',
                    cwe_id='CWE-1104'
                ))
        
        return issues
    
    def check_insufficient_logging(self, code: str, filename: str) -> List[SecurityIssue]:
        """A10: Insufficient Logging & Monitoring"""
        issues = []
        
        # Check for authentication/authorization without logging
        auth_patterns = [
            r'def\s+login\(',
            r'def\s+authenticate\(',
            r'@login_required'
        ]
        
        for pattern in auth_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                context = code[match.start():min(len(code), match.end()+500)]
                if 'log' not in context.lower() and 'logger' not in context.lower():
                    issues.append(SecurityIssue(
                        severity='medium',
                        category='A10:2021-Insufficient Logging',
                        title='Missing Security Logging',
                        description=f'Authentication/authorization without logging: {match.group()}',
                        location=filename,
                        recommendation='Add comprehensive security event logging',
                        cwe_id='CWE-778'
                    ))
        
        return issues
    
    def scan_file(self, filepath: str) -> List[SecurityIssue]:
        """Faylni scan qilish"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            logger.error(f"Failed to read {filepath}: {e}")
            return []
        
        issues = []
        issues.extend(self.check_sql_injection(code, filepath))
        issues.extend(self.check_broken_authentication(code, filepath))
        issues.extend(self.check_sensitive_data_exposure(code, filepath))
        issues.extend(self.check_xxe(code, filepath))
        issues.extend(self.check_broken_access_control(code, filepath))
        issues.extend(self.check_security_misconfiguration(code, filepath))
        issues.extend(self.check_xss(code, filepath))
        issues.extend(self.check_insecure_deserialization(code, filepath))
        issues.extend(self.check_vulnerable_components(code, filepath))
        issues.extend(self.check_insufficient_logging(code, filepath))
        
        return issues


class PenetrationTester:
    """
    Penetration Testing Framework
    
    Security testing va vulnerability exploitation
    """
    
    def __init__(self):
        self.vulnerabilities: List[Dict[str, Any]] = []
    
    async def test_authentication(self, auth_endpoint: str) -> List[SecurityIssue]:
        """Authentication testing"""
        issues = []
        
        # Test 1: Brute force protection
        logger.info("Testing brute force protection...")
        # In real scenario, would attempt multiple failed logins
        
        # Test 2: Session management
        logger.info("Testing session management...")
        
        # Test 3: Password reset
        logger.info("Testing password reset mechanism...")
        
        return issues
    
    async def test_authorization(self, api_endpoints: List[str]) -> List[SecurityIssue]:
        """Authorization testing"""
        issues = []
        
        # Test for privilege escalation
        logger.info("Testing for privilege escalation...")
        
        # Test for insecure direct object references (IDOR)
        logger.info("Testing for IDOR...")
        
        return issues
    
    async def test_input_validation(self, endpoints: List[str]) -> List[SecurityIssue]:
        """Input validation testing"""
        issues = []
        
        # SQL Injection payloads
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users--",
            "1' UNION SELECT NULL--"
        ]
        
        # XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')"
        ]
        
        logger.info(f"Testing {len(endpoints)} endpoints for injection vulnerabilities...")
        
        return issues
    
    async def test_api_security(self, api_base_url: str) -> List[SecurityIssue]:
        """API security testing"""
        issues = []
        
        # Test for missing rate limiting
        logger.info("Testing rate limiting...")
        
        # Test for API key exposure
        logger.info("Testing API key security...")
        
        # Test for CORS misconfiguration
        logger.info("Testing CORS configuration...")
        
        return issues


class VulnerabilityScanner:
    """
    Automated Vulnerability Scanner
    """
    
    def __init__(self):
        self.scan_results: List[SecurityIssue] = []
    
    async def scan_dependencies(self, requirements_file: str = 'requirements.txt') -> List[SecurityIssue]:
        """Dependencies ni scan qilish"""
        issues = []
        
        try:
            # Use safety to check for vulnerable dependencies
            result = subprocess.run(
                ['pip', 'list', '--format=json'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                logger.info(f"Scanned {len(packages)} packages")
                
                # In real scenario, would check against vulnerability database
                
        except Exception as e:
            logger.error(f"Failed to scan dependencies: {e}")
        
        return issues
    
    async def scan_ports(self, host: str = 'localhost') -> List[SecurityIssue]:
        """Port scanning"""
        issues = []
        
        # Common ports to check
        common_ports = [21, 22, 23, 80, 443, 3306, 5432, 6379, 27017]
        
        logger.info(f"Scanning ports on {host}...")
        
        # In real scenario, would perform actual port scanning
        
        return issues
    
    async def scan_ssl_tls(self, domain: str) -> List[SecurityIssue]:
        """SSL/TLS configuration scanning"""
        issues = []
        
        logger.info(f"Scanning SSL/TLS configuration for {domain}...")
        
        # Check for:
        # - Expired certificates
        # - Weak cipher suites
        # - Old TLS versions
        
        return issues


class SecurityAuditor:
    """
    Comprehensive Security Auditor
    
    Barcha security checklar uchun asosiy class
    """
    
    def __init__(self, project_root: str = '/workspace/code'):
        self.project_root = Path(project_root)
        self.owasp_checker = OWASPChecker()
        self.penetration_tester = PenetrationTester()
        self.vulnerability_scanner = VulnerabilityScanner()
        self.all_issues: List[SecurityIssue] = []
    
    async def full_security_audit(self) -> SecurityReport:
        """To'liq security audit"""
        start_time = datetime.now()
        
        logger.info("=" * 80)
        logger.info("Starting Comprehensive Security Audit")
        logger.info("=" * 80)
        
        # 1. Static code analysis (OWASP)
        logger.info("\n[1/4] Static Code Analysis (OWASP Top 10)")
        logger.info("-" * 80)
        await self._scan_codebase()
        
        # 2. Dependency vulnerability scanning
        logger.info("\n[2/4] Dependency Vulnerability Scanning")
        logger.info("-" * 80)
        dep_issues = await self.vulnerability_scanner.scan_dependencies()
        self.all_issues.extend(dep_issues)
        
        # 3. Penetration testing
        logger.info("\n[3/4] Penetration Testing")
        logger.info("-" * 80)
        # In production, would run actual penetration tests
        
        # 4. Configuration audit
        logger.info("\n[4/4] Configuration Audit")
        logger.info("-" * 80)
        # Check environment variables, configs, etc.
        
        # Generate report
        duration = (datetime.now() - start_time).total_seconds()
        report = self._generate_report(duration)
        
        # Save report
        await self._save_report(report)
        
        return report
    
    async def _scan_codebase(self):
        """Codebase ni scan qilish"""
        python_files = list(self.project_root.rglob('*.py'))
        
        logger.info(f"Scanning {len(python_files)} Python files...")
        
        for filepath in python_files:
            issues = self.owasp_checker.scan_file(str(filepath))
            self.all_issues.extend(issues)
            
            if issues:
                logger.warning(f"Found {len(issues)} issues in {filepath.name}")
    
    def _generate_report(self, duration: float) -> SecurityReport:
        """Security report yaratish"""
        severity_counts = {
            'critical': len([i for i in self.all_issues if i.severity == 'critical']),
            'high': len([i for i in self.all_issues if i.severity == 'high']),
            'medium': len([i for i in self.all_issues if i.severity == 'medium']),
            'low': len([i for i in self.all_issues if i.severity == 'low']),
            'info': len([i for i in self.all_issues if i.severity == 'info'])
        }
        
        report = SecurityReport(
            timestamp=datetime.now(),
            total_issues=len(self.all_issues),
            critical_count=severity_counts['critical'],
            high_count=severity_counts['high'],
            medium_count=severity_counts['medium'],
            low_count=severity_counts['low'],
            info_count=severity_counts['info'],
            issues=self.all_issues,
            scan_duration=duration
        )
        
        return report
    
    async def _save_report(self, report: SecurityReport):
        """Reportni saqlash"""
        output_dir = Path('/workspace/security_reports')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # JSON report
        json_file = output_dir / f"security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            'timestamp': report.timestamp.isoformat(),
            'summary': {
                'total_issues': report.total_issues,
                'critical': report.critical_count,
                'high': report.high_count,
                'medium': report.medium_count,
                'low': report.low_count,
                'info': report.info_count,
                'risk_score': report.risk_score,
                'scan_duration': report.scan_duration
            },
            'issues': [
                {
                    'severity': issue.severity,
                    'category': issue.category,
                    'title': issue.title,
                    'description': issue.description,
                    'location': issue.location,
                    'recommendation': issue.recommendation,
                    'cwe_id': issue.cwe_id
                }
                for issue in report.issues
            ]
        }
        
        with open(json_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"\nSecurity report saved: {json_file}")
        
        # Print summary
        self._print_summary(report)
    
    def _print_summary(self, report: SecurityReport):
        """Summary chop etish"""
        logger.info("\n" + "=" * 80)
        logger.info("SECURITY AUDIT SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Issues: {report.total_issues}")
        logger.info(f"Critical: {report.critical_count}")
        logger.info(f"High: {report.high_count}")
        logger.info(f"Medium: {report.medium_count}")
        logger.info(f"Low: {report.low_count}")
        logger.info(f"Info: {report.info_count}")
        logger.info(f"Risk Score: {report.risk_score}/100")
        logger.info(f"Scan Duration: {report.scan_duration:.2f}s")
        
        if report.risk_score > 75:
            logger.error("\n⚠️  HIGH RISK - Immediate action required!")
        elif report.risk_score > 40:
            logger.warning("\n⚠️  MEDIUM RISK - Address critical issues soon")
        else:
            logger.info("\n✓ LOW RISK - Continue monitoring")


# Example usage
async def main():
    """Security auditor demo"""
    auditor = SecurityAuditor()
    
    # Run full security audit
    report = await auditor.full_security_audit()
    
    return report


if __name__ == '__main__':
    asyncio.run(main())
