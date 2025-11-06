"""
Security Tizimi Demo
====================

Bu demo security va rate limiting tizimini ishlatishni ko'rsatadi.

@author: Security Team
@version: 1.0.0
"""

import time
import asyncio
from datetime import datetime
from security import (
    TokenBucket, SlidingWindowRateLimiter, RateLimiterManager,
    SecurityValidator, InputValidator, SQLInjectionProtector,
    APISecurityManager, RequestSigner, APIKeyRotator,
    DataProtector, PIIProtector, DataAnonymizer, ComplianceManager,
    SecurityMonitor, AnomalyDetector, IncidentResponse
)
from config import get_security_config, SecurityConfig
from utils import IPAddressUtils, UserAgentParser, SecurityHelpers, metrics

# Demo functions
def demo_rate_limiting():
    """Rate limiting demo"""
    print("\n" + "="*60)
    print("RATE LIMITING DEMO")
    print("="*60)
    
    # Create rate limiter manager
    rate_limiter = RateLimiterManager()
    
    # Add endpoint configuration
    from security.rate_limiter import EndpointConfig, RateLimitConfig
    
    login_config = EndpointConfig(
        endpoint="/api/v1/auth/login",
        config=RateLimitConfig(
            requests_per_minute=5,
            requests_per_hour=100,
            burst_limit=3
        )
    )
    rate_limiter.add_endpoint_config(login_config)
    
    # Test rate limiting
    print("\n1. Token Bucket Rate Limiting Test:")
    token_bucket = TokenBucket(capacity=10, refill_rate=1.0)  # 1 token per second
    
    for i in range(15):
        allowed = token_bucket.consume()
        tokens_remaining = token_bucket.get_tokens()
        print(f"Request {i+1}: Allowed={allowed}, Tokens={tokens_remaining}")
        time.sleep(0.1)
    
    print("\n2. Sliding Window Rate Limiting Test:")
    sliding_window = SlidingWindowRateLimiter(window_size=10, max_requests=5)
    
    for i in range(10):
        allowed = sliding_window.is_allowed("user123")
        count = sliding_window.get_request_count("user123")
        print(f"Request {i+1}: Allowed={allowed}, Count in window={count}")
    
    print("\n3. Complete Rate Limiting System Test:")
    test_user = "demo_user"
    
    for i in range(8):
        allowed, metrics_data = rate_limiter.check_rate_limit(test_user, "/api/v1/auth/login")
        print(f"Request {i+1}: Allowed={allowed}, Remaining={metrics_data['remaining']}")
        time.sleep(0.1)
    
    # Show final metrics
    final_metrics = rate_limiter.get_metrics(test_user)
    print(f"\nFinal Metrics: {final_metrics}")


def demo_security_validation():
    """Security validation demo"""
    print("\n" + "="*60)
    print("SECURITY VALIDATION DEMO")
    print("="*60)
    
    # Input validator
    validator = InputValidator()
    
    print("\n1. Email Validation:")
    test_emails = ["user@example.com", "invalid-email", "test.user@domain.co.uk", ""]
    for email in test_emails:
        is_valid, error = validator.validate_email(email)
        print(f"Email '{email}': Valid={is_valid}, Error={error}")
    
    print("\n2. Password Validation:")
    test_passwords = ["123", "password", "Password123!", "MyVerySecureP@ssw0rd!", ""]
    for password in test_passwords:
        is_valid, errors = validator.validate_password(password)
        print(f"Password strength: Valid={is_valid}, Issues={errors}")
    
    print("\n3. SQL Injection Detection:")
    sql_queries = [
        "SELECT * FROM users WHERE id = 1",
        "SELECT * FROM users WHERE id = '1' OR '1'='1'",
        "'; DROP TABLE users; --",
        "admin'--",
        "Normal query"
    ]
    for query in sql_queries:
        has_injection = validator.detect_sql_injection(query)
        print(f"Query: '{query}' -> SQL Injection: {has_injection}")
    
    print("\n4. XSS Detection:")
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "Normal text",
        "javascript:alert('XSS')",
        "<iframe src='javascript:alert(1)'></iframe>"
    ]
    for payload in xss_payloads:
        has_xss = validator.detect_xss(payload)
        print(f"Payload: '{payload}' -> XSS: {has_xss}")
    
    # SQL Injection Protector
    print("\n5. SQL Injection Protection:")
    protector = SQLInjectionProtector()
    
    dangerous_query = "SELECT * FROM users WHERE id = 1' OR '1'='1"
    analysis = protector.analyze_query(dangerous_query)
    print(f"Query Analysis: {analysis}")


def demo_api_security():
    """API security demo"""
    print("\n" + "="*60)
    print("API SECURITY DEMO")
    print("="*60)
    
    # API Security Manager
    api_security = APISecurityManager()
    
    print("\n1. API Key Management:")
    # Create API key
    key_id, api_key = api_security.key_rotator.create_api_key(
        permissions=["read", "write"],
        expires_days=30,
        rate_limit=1000
    )
    print(f"Created API Key: {key_id}")
    
    # Validate API key
    is_valid, error, key_data = api_security.validate_api_key(key_id)
    print(f"API Key Validation: Valid={is_valid}, Key ID={key_data.key_id if key_data else None}")
    
    print("\n2. JWT Token Management:")
    # Create JWT token
    jwt_token = api_security.create_jwt_token(
        user_id="user123",
        permissions=["read", "write"],
        expires_in=3600
    )
    print(f"Created JWT Token: {jwt_token[:50]}...")
    
    # Validate JWT token
    is_valid, payload, error = api_security.validate_jwt_token(jwt_token)
    print(f"JWT Validation: Valid={is_valid}, User ID={payload.get('user_id') if payload else None}")
    
    print("\n3. Request Signing:")
    signer = RequestSigner()
    
    # Sign a request
    secret = "demo_secret_key"
    method = "POST"
    path = "/api/v1/data"
    timestamp = int(time.time())
    body = '{"data": "test"}'
    
    signature = signer.sign_request(secret, method, path, timestamp, body)
    print(f"Request Signature: {signature}")
    
    # Verify signature
    is_valid = signer.verify_signature(secret, signature, method, path, timestamp, body)
    print(f"Signature Verification: Valid={is_valid}")
    
    print("\n4. Security Headers:")
    headers = api_security.get_security_headers()
    print("Security Headers:")
    for header, value in headers.items():
        print(f"  {header}: {value}")


def demo_data_protection():
    """Data protection demo"""
    print("\n" + "="*60)
    print("DATA PROTECTION DEMO")
    print("="*60)
    
    # Data Protector
    data_protector = DataProtector()
    
    print("\n1. Data Encryption/Decryption:")
    sensitive_data = "Very sensitive information: SSN 123-45-6789"
    
    # Encrypt
    encrypted = data_protector.encrypt_data(sensitive_data)
    print(f"Original: {sensitive_data}")
    print(f"Encrypted: {encrypted[:50]}...")
    
    # Decrypt
    decrypted = data_protector.decrypt_data(encrypted)
    print(f"Decrypted: {decrypted}")
    
    print("\n2. PII Protection:")
    pii_protector = PIIProtector()
    
    test_data = {
        "email": "john.doe@example.com",
        "phone": "(555) 123-4567",
        "ssn": "123-45-6789",
        "name": "John Doe",
        "address": "123 Main St, Anytown, USA"
    }
    
    print("PII Detection:")
    for field, value in test_data.items():
        detected_pii = pii_protector.detect_pii(str(value))
        print(f"  {field}: {value} -> Detected: {detected_pii}")
    
    print("\n3. Data Anonymization:")
    anonymizer = DataAnonymizer()
    
    # Anonymize PII
    for field, value in test_data.items():
        if field in pii_protector.standard_pii_fields:
            anonymized = anonymizer._mask_anonymization(str(value))
            print(f"  {field}: {value} -> {anonymized}")
    
    print("\n4. GDPR Compliance:")
    compliance = ComplianceManager()
    
    # Record consent
    consent_id = compliance.record_consent(
        user_id="user123",
        purpose="data_processing",
        consent_given=True,
        regulation="GDPR"
    )
    print(f"Consent recorded: {consent_id}")
    
    # Validate consent
    has_consent = compliance.validate_consent("user123", "data_processing", "GDPR")
    print(f"Consent validation: {has_consent}")


def demo_security_monitoring():
    """Security monitoring demo"""
    print("\n" + "="*60)
    print("SECURITY MONITORING DEMO")
    print("="*60)
    
    # Security Monitor
    monitor = SecurityMonitor()
    
    print("\n1. Logging Security Events:")
    # Start monitoring
    monitor.start_monitoring()
    
    # Log various security events
    monitor.log_event(
        event_type="failed_login",
        source_ip="192.168.1.100",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        severity=SecurityLevel.MEDIUM,
        description="Failed login attempt",
        attempts=3
    )
    
    monitor.log_event(
        event_type="security_violation",
        source_ip="10.0.0.50",
        user_agent="curl/7.68.0",
        severity=SecurityLevel.HIGH,
        description="SQL injection attempt detected",
        violation_type="sql_injection",
        query_attempted="SELECT * FROM users WHERE id = 1 OR 1=1"
    )
    
    monitor.log_event(
        event_type="rate_limit_exceeded",
        source_ip="203.0.113.1",
        user_agent="python-requests/2.25.1",
        severity=SecurityLevel.HIGH,
        description="API rate limit exceeded",
        endpoint="/api/v1/search",
        requests_made=150,
        limit=100
    )
    
    print("Security events logged successfully")
    
    print("\n2. Incident Management:")
    # Create incident
    incident_id = monitor.create_incident(
        title="Multiple Failed Login Attempts",
        description="Multiple failed login attempts detected from suspicious IP",
        severity=SecurityLevel.HIGH,
        affected_systems=["authentication_service"],
        assigned_team=["security_team"]
    )
    print(f"Incident created: {incident_id}")
    
    # Update incident
    time.sleep(1)
    monitor.update_incident_status(incident_id, IncidentStatus.INVESTIGATING, "Investigating IP address")
    
    print("\n3. Dashboard Data:")
    dashboard_data = monitor.get_dashboard_data()
    print("Dashboard Summary:")
    print(f"  Total Events: {dashboard_data['summary']['total_events']}")
    print(f"  Events Last Hour: {dashboard_data['summary']['events_last_hour']}")
    print(f"  Active Incidents: {dashboard_data['summary']['active_incidents']}")
    
    print("\n4. Anomaly Detection:")
    detector = AnomalyDetector()
    
    # Establish baseline
    baseline_data = [10, 12, 11, 13, 12, 14, 11, 13, 12, 15]  # Normal traffic
    detector.establish_baseline("request_rate", baseline_data)
    
    # Test anomaly detection
    normal_request = 13  # Normal
    anomaly_request = 45  # Unusual spike
    
    is_anomaly, confidence, message = detector.detect_anomalies("request_rate", normal_request)
    print(f"Normal request (13): Anomaly={is_anomaly}, Confidence={confidence:.2f}")
    
    is_anomaly, confidence, message = detector.detect_anomalies("request_rate", anomaly_request)
    print(f"Anomalous request (45): Anomaly={is_anomaly}, Confidence={confidence:.2f}, Message={message}")
    
    # Stop monitoring
    monitor.stop_monitoring()
    
    print("\n5. Security Report:")
    security_report = monitor.get_security_report()
    print("Security Report Summary:")
    print(f"  Total Security Events: {security_report['total_events']}")
    print(f"  Recent Events (24h): {security_report['recent_events_24h']}")
    print(f"  Events by Severity: {security_report['events_by_severity']}")


def demo_utility_functions():
    """Utility functions demo"""
    print("\n" + "="*60)
    print("UTILITY FUNCTIONS DEMO")
    print("="*60)
    
    print("\n1. IP Address Utilities:")
    test_ips = ["192.168.1.1", "10.0.0.1", "8.8.8.8", "203.0.113.1", "::1", "invalid-ip"]
    
    for ip in test_ips:
        is_private = IPAddressUtils.is_private_ip(ip)
        ip_info = IPAddressUtils.get_ip_info(ip)
        print(f"IP {ip}: Private={is_private}, Info={ip_info}")
    
    # Simulate headers with proxy IP
    headers = {
        'X-Forwarded-For': '203.0.113.1, 10.0.0.1, 192.168.1.1',
        'X-Real-IP': '203.0.113.1'
    }
    client_ip = IPAddressUtils.extract_client_ip(headers)
    print(f"Extracted Client IP: {client_ip}")
    
    print("\n2. User Agent Parsing:")
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Googlebot/2.1 (+http://www.google.com/bot.html)",
        "curl/7.68.0"
    ]
    
    for ua in user_agents:
        parsed = UserAgentParser.parse_user_agent(ua)
        print(f"UA: {parsed['browser']} on {parsed['os']} - Bot={parsed['is_bot']}, Mobile={parsed['is_mobile']}")
    
    print("\n3. Security Helpers:")
    helpers = SecurityHelpers()
    
    # Generate secure tokens
    token = helpers.generate_secure_token()
    api_key = helpers.generate_api_key()
    session_id = helpers.generate_session_id()
    
    print(f"Secure Token: {token[:50]}...")
    print(f"API Key: {api_key}")
    print(f"Session ID: {session_id}")
    
    # Password strength check
    test_passwords = ["123456", "password", "Password123!", "MyVerySecureP@ssw0rd2023!"]
    for password in test_passwords:
        result = helpers.is_strong_password(password)
        print(f"Password: {password[:20]}... -> Strong={result['is_strong']}, Score={result['score']}")
    
    # Hash verification
    password = "mypassword123"
    hashed = helpers.create_hash(password)
    verified = helpers.verify_hash(password, hashed)
    wrong_verified = helpers.verify_hash("wrongpassword", hashed)
    
    print(f"Hash verification: Original={verified}, Wrong={wrong_verified}")
    
    # Sensitive data masking
    sensitive_data = "1234567890123456"
    masked = helpers.mask_sensitive_data(sensitive_data, show_chars=4)
    print(f"Credit card: {sensitive_data} -> {masked}")


def demo_comprehensive_workflow():
    """Keng qamrovli workflow demo"""
    print("\n" + "="*60)
    print("COMPREHENSIVE SECURITY WORKFLOW DEMO")
    print("="*60)
    
    # Initialize all components
    config = get_security_config()
    rate_limiter = RateLimiterManager()
    security_validator = SecurityValidator()
    api_security = APISecurityManager()
    data_protector = DataProtector()
    pii_protector = PIIProtector()
    monitor = SecurityMonitor()
    
    # Start monitoring
    monitor.start_monitoring()
    
    print("\n1. Simulating Complete API Request:")
    # Simulate incoming request
    request_data = {
        "user_id": "user123",
        "email": "user@example.com",
        "action": "update_profile"
    }
    
    # Headers simulation
    headers = {
        "X-Forwarded-For": "192.168.1.100",
        "User-Agent": "Mozilla/5.0 (compatible; MyApp/1.0)",
        "Authorization": "Bearer dummy_jwt_token"
    }
    
    client_ip = IPAddressUtils.extract_client_ip(headers)
    user_agent = headers.get("User-Agent", "")
    path = "/api/v1/user/profile"
    
    print(f"Request from IP: {client_ip}")
    print(f"User Agent: {user_agent}")
    print(f"Path: {path}")
    
    # Step 1: Rate limiting check
    print("\n2. Rate Limiting Check:")
    allowed, rate_metrics = rate_limiter.check_rate_limit(client_ip, path)
    print(f"Rate limit allowed: {allowed}")
    if not allowed:
        print("Request blocked by rate limiter")
        return
    
    # Step 2: Input validation
    print("\n3. Input Validation:")
    is_valid, violations = security_validator.validate_request(request_data, client_ip, user_agent, path)
    print(f"Input validation: {is_valid}")
    if violations:
        print(f"Violations: {violations}")
        monitor.log_event(
            event_type="input_violation",
            source_ip=client_ip,
            user_agent=user_agent,
            severity=SecurityLevel.HIGH,
            description="Input validation failed",
            violations=violations,
            request_path=path
        )
    
    # Step 3: JWT token validation
    print("\n4. Authentication:")
    auth_header = headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        is_valid, payload, error = api_security.validate_jwt_token(token)
        print(f"JWT validation: {is_valid}")
        if not is_valid:
            print(f"Authentication failed: {error}")
    
    # Step 4: PII detection and protection
    print("\n5. PII Protection:")
    for field, value in request_data.items():
        if isinstance(value, str):
            pii_detected = pii_protector.detect_pii(value)
            if pii_detected:
                print(f"PII detected in {field}: {pii_detected}")
                # Mask PII
                masked_value = pii_protector.mask_pii(value)
                request_data[field] = masked_value
    
    # Step 5: Data encryption for storage
    print("\n6. Data Encryption:")
    for field, value in request_data.items():
        if field in ["email", "user_id"]:
            encrypted = data_protector.encrypt_data(str(value))
            print(f"Encrypted {field}: {encrypted[:30]}...")
    
    # Step 6: Log security event
    print("\n7. Security Logging:")
    monitor.log_event(
        event_type="api_request",
        source_ip=client_ip,
        user_agent=user_agent,
        severity=SecurityLevel.LOW,
        description="Successful API request",
        path=path,
        user_id=request_data.get("user_id")
    )
    
    # Step 7: Generate security report
    print("\n8. Security Dashboard:")
    dashboard_data = monitor.get_dashboard_data()
    print(f"Total events processed: {dashboard_data['summary']['total_events']}")
    print(f"Recent events: {dashboard_data['summary']['events_last_hour']}")
    
    # Stop monitoring
    monitor.stop_monitoring()
    
    print("\n" + "="*60)
    print("WORKFLOW COMPLETED SUCCESSFULLY")
    print("="*60)


def main():
    """Asosiy demo funksiyasi"""
    print("SECURITY VA RATE LIMITING TIZIMI DEMO")
    print("=" * 80)
    print(f"Demo started at: {datetime.now()}")
    print("Features demonstration:")
    print("- Rate Limiting (Token Bucket, Sliding Window)")
    print("- Security Validation (Input, SQL Injection, XSS)")
    print("- API Security (JWT, API Keys, Request Signing)")
    print("- Data Protection (Encryption, PII Protection)")
    print("- Security Monitoring (Anomaly Detection, Incidents)")
    print("- Utility Functions (IP parsing, User Agent parsing)")
    
    try:
        # Run individual demos
        demo_rate_limiting()
        demo_security_validation()
        demo_api_security()
        demo_data_protection()
        demo_security_monitoring()
        demo_utility_functions()
        
        # Run comprehensive workflow
        demo_comprehensive_workflow()
        
        print("\n" + "="*80)
        print("BARCHA DEMOLAR MUVAFFAQIYATLI YAKUNLANDI!")
        print("="*80)
        print(f"Demo completed at: {datetime.now()}")
        print("\nSecurity tizimi to'liq ishlash holatida va ishlatishga tayyor.")
        
    except Exception as e:
        print(f"\nXato yuz berdi: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()