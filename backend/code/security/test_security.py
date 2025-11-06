#!/usr/bin/env python3
"""
Security Tizimi Test
====================

Bu test fayl security va rate limiting tizimining barcha funksiyalarini test qiladi.

@author: Security Team
@version: 1.0.0
"""

import sys
import os
import unittest
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from security import (
        TokenBucket, SlidingWindowRateLimiter, RateLimiterManager,
        SecurityValidator, InputValidator, SQLInjectionProtector,
        APISecurityManager, RequestSigner, APIKeyRotator,
        DataProtector, PIIProtector, DataAnonymizer, ComplianceManager,
        SecurityMonitor, AnomalyDetector, IncidentResponse
    )
    from security.security_monitor import SecurityLevel, IncidentStatus
    from security.rate_limiter import EndpointConfig, RateLimitConfig
    from security.config import get_security_config
    from security.utils import IPAddressUtils, UserAgentParser, SecurityHelpers
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


class TestRateLimiting(unittest.TestCase):
    """Rate limiting testlari"""
    
    def test_token_bucket(self):
        """Token Bucket test"""
        bucket = TokenBucket(capacity=5, refill_rate=2.0)
        
        # Should allow up to capacity
        for i in range(5):
            self.assertTrue(bucket.consume())
        
        # Should deny after capacity is exceeded
        self.assertFalse(bucket.consume())
        
        # Should allow after some time passes
        time.sleep(0.6)  # Should refill ~1 token
        self.assertTrue(bucket.consume())
    
    def test_sliding_window(self):
        """Sliding Window test"""
        limiter = SlidingWindowRateLimiter(window_size=10, max_requests=3)
        
        # Should allow first 3 requests
        for i in range(3):
            self.assertTrue(limiter.is_allowed("user1"))
        
        # Should deny 4th request
        self.assertFalse(limiter.is_allowed("user1"))
        
        # Should allow for different user
        self.assertTrue(limiter.is_allowed("user2"))
    
    def test_rate_limiter_manager(self):
        """Rate Limiter Manager test"""
        manager = RateLimiterManager()
        
        # Add endpoint config
        config = EndpointConfig(
            endpoint="/api/test",
            config=RateLimitConfig(requests_per_minute=10, burst_limit=5)
        )
        manager.add_endpoint_config(config)
        
        # Test rate limiting
        for i in range(5):
            allowed, metrics = manager.check_rate_limit("user1", "/api/test")
            self.assertTrue(allowed)
        
        # Should still allow due to burst limit
        allowed, metrics = manager.check_rate_limit("user1", "/api/test")
        self.assertTrue(allowed)


class TestSecurityValidation(unittest.TestCase):
    """Security validation testlari"""
    
    def test_input_validator(self):
        """Input Validator test"""
        validator = InputValidator()
        
        # Email validation
        self.assertTrue(validator.validate_email("test@example.com")[0])
        self.assertFalse(validator.validate_email("invalid-email")[0])
        
        # Password validation
        is_valid, errors = validator.validate_password("StrongPass123!")
        self.assertTrue(is_valid)
        
        is_valid, errors = validator.validate_password("weak")
        self.assertFalse(is_valid)
        
        # SQL injection detection
        self.assertTrue(validator.detect_sql_injection("SELECT * FROM users"))
        self.assertFalse(validator.detect_sql_injection("normal text"))
        
        # XSS detection
        self.assertTrue(validator.detect_xss("<script>alert('xss')</script>"))
        self.assertFalse(validator.detect_xss("normal text"))
    
    def test_sql_injection_protector(self):
        """SQL Injection Protector test"""
        protector = SQLInjectionProtector()
        
        dangerous_query = "SELECT * FROM users WHERE id = '1' OR '1'='1"
        analysis = protector.analyze_query(dangerous_query)
        
        self.assertFalse(analysis['is_safe'])
        self.assertGreater(len(analysis['threats_found']), 0)
        
        safe_query = "SELECT id, name FROM users WHERE id = 123"
        analysis = protector.analyze_query(safe_query)
        self.assertTrue(analysis['is_safe'])


class TestAPISecurity(unittest.TestCase):
    """API Security testlari"""
    
    def test_api_key_management(self):
        """API Key Management test"""
        rotator = APIKeyRotator()
        
        # Create API key
        key_id, api_key = rotator.create_api_key(
            permissions=["read", "write"],
            expires_days=30
        )
        
        self.assertIsNotNone(key_id)
        self.assertIsNotNone(api_key)
        
        # Get API key
        retrieved_key = rotator.get_api_key(key_id)
        self.assertIsNotNone(retrieved_key)
        self.assertEqual(retrieved_key.key_id, key_id)
        
        # Rotate API key
        new_key_id, new_api_key = rotator.rotate_api_key(key_id)
        self.assertIsNotNone(new_key_id)
        self.assertNotEqual(key_id, new_key_id)
    
    def test_jwt_token(self):
        """JWT Token test"""
        api_security = APISecurityManager()
        
        # Create token
        token = api_security.create_jwt_token("user123", ["read", "write"])
        self.assertIsNotNone(token)
        
        # Validate token
        is_valid, payload, error = api_security.validate_jwt_token(token)
        self.assertTrue(is_valid)
        self.assertEqual(payload['user_id'], "user123")
    
    def test_request_signing(self):
        """Request Signing test"""
        signer = RequestSigner()
        secret = "test_secret"
        
        # Sign request
        signature = signer.sign_request(secret, "POST", "/api/test", 1234567890, '{"data": "test"}')
        self.assertIsNotNone(signature)
        
        # Verify signature
        is_valid = signer.verify_signature(secret, signature, "POST", "/api/test", 1234567890, '{"data": "test"}')
        self.assertTrue(is_valid)
        
        # Wrong signature should fail
        is_valid = signer.verify_signature(secret, "wrong_signature", "POST", "/api/test", 1234567890, '{"data": "test"}')
        self.assertFalse(is_valid)


class TestDataProtection(unittest.TestCase):
    """Data Protection testlari"""
    
    def test_data_encryption(self):
        """Data Encryption test"""
        protector = DataProtector()
        
        sensitive_data = "Very sensitive information"
        
        # Encrypt
        encrypted = protector.encrypt_data(sensitive_data)
        self.assertNotEqual(encrypted, sensitive_data)
        
        # Decrypt
        decrypted = protector.decrypt_data(encrypted)
        self.assertEqual(decrypted, sensitive_data)
    
    def test_pii_protection(self):
        """PII Protection test"""
        protector = PIIProtector()
        
        # Detect PII
        test_data = "Email: user@example.com, Phone: (555) 123-4567, SSN: 123-45-6789"
        pii_detected = protector.detect_pii(test_data)
        
        self.assertGreater(len(pii_detected), 0)
        self.assertTrue(any(p['type'] == 'email' for p in pii_detected))
        self.assertTrue(any(p['type'] == 'phone' for p in pii_detected))
        self.assertTrue(any(p['type'] == 'ssn' for p in pii_detected))
        
        # Anonymize
        anonymized = protector.anonymize_pii('email', 'user@example.com')
        self.assertNotEqual(anonymized, 'user@example.com')
    
    def test_compliance_manager(self):
        """Compliance Manager test"""
        compliance = ComplianceManager()
        
        # Record consent
        consent_id = compliance.record_consent(
            user_id="user123",
            purpose="data_processing",
            consent_given=True,
            regulation="GDPR"
        )
        
        self.assertIsNotNone(consent_id)
        
        # Validate consent
        has_consent = compliance.validate_consent("user123", "data_processing", "GDPR")
        self.assertTrue(has_consent)


class TestSecurityMonitoring(unittest.TestCase):
    """Security Monitoring testlari"""
    
    def test_event_logging(self):
        """Event Logging test"""
        monitor = SecurityMonitor()
        
        # Start monitoring
        monitor.start_monitoring()
        
        # Log event
        monitor.log_event(
            event_type="test_event",
            source_ip="127.0.0.1",
            user_agent="Test Agent",
            severity=SecurityLevel.LOW,
            description="Test security event"
        )
        
        # Check if event was logged
        self.assertGreater(len(monitor.events), 0)
        
        # Stop monitoring
        monitor.stop_monitoring()
    
    def test_incident_creation(self):
        """Incident Creation test"""
        monitor = SecurityMonitor()
        
        # Create incident
        incident_id = monitor.create_incident(
            title="Test Incident",
            description="Test incident description",
            severity=SecurityLevel.HIGH
        )
        
        self.assertIsNotNone(incident_id)
        self.assertIn(incident_id, monitor.incidents)
        
        # Update incident
        success = monitor.update_incident_status(incident_id, IncidentStatus.INVESTIGATING, "Investigating")
        self.assertTrue(success)
    
    def test_anomaly_detection(self):
        """Anomaly Detection test"""
        detector = AnomalyDetector()
        
        # Establish baseline
        baseline_data = [10, 11, 10, 12, 11, 10, 12, 11, 10, 13]
        detector.establish_baseline("test_metric", baseline_data)
        
        # Test normal value
        is_anomaly, confidence, message = detector.detect_anomalies("test_metric", 11)
        self.assertFalse(is_anomaly)
        
        # Test anomalous value
        is_anomaly, confidence, message = detector.detect_anomalies("test_metric", 50)
        self.assertTrue(is_anomaly)
        self.assertGreater(confidence, 0.5)


class TestUtils(unittest.TestCase):
    """Utility functions testlari"""
    
    def test_ip_utils(self):
        """IP Utilities test"""
        # Test private IP detection
        self.assertTrue(IPAddressUtils.is_private_ip("192.168.1.1"))
        self.assertTrue(IPAddressUtils.is_private_ip("10.0.0.1"))
        self.assertFalse(IPAddressUtils.is_private_ip("8.8.8.8"))
        
        # Test IP info
        ip_info = IPAddressUtils.get_ip_info("192.168.1.1")
        self.assertTrue(ip_info['is_private'])
        
        # Test client IP extraction
        headers = {'X-Forwarded-For': '203.0.113.1, 10.0.0.1'}
        client_ip = IPAddressUtils.extract_client_ip(headers)
        self.assertEqual(client_ip, "203.0.113.1")
    
    def test_user_agent_parser(self):
        """User Agent Parser test"""
        # Test Chrome UA
        chrome_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        parsed = UserAgentParser.parse_user_agent(chrome_ua)
        
        self.assertEqual(parsed['browser'], 'Chrome')
        self.assertEqual(parsed['os'], 'Windows')
        self.assertFalse(parsed['is_bot'])
        
        # Test bot UA
        bot_ua = "Googlebot/2.1 (+http://www.google.com/bot.html)"
        parsed = UserAgentParser.parse_user_agent(bot_ua)
        
        self.assertTrue(parsed['is_bot'])
    
    def test_security_helpers(self):
        """Security Helpers test"""
        helpers = SecurityHelpers()
        
        # Test token generation
        token = helpers.generate_secure_token()
        self.assertIsNotNone(token)
        self.assertGreater(len(token), 0)
        
        # Test password strength
        result = helpers.is_strong_password("StrongPass123!")
        self.assertTrue(result['is_strong'])
        
        result = helpers.is_strong_password("weak")
        self.assertFalse(result['is_strong'])
        
        # Test hashing
        hashed = helpers.create_hash("password123")
        verified = helpers.verify_hash("password123", hashed)
        self.assertTrue(verified)
        
        wrong_verified = helpers.verify_hash("wrongpassword", hashed)
        self.assertFalse(wrong_verified)


class TestConfiguration(unittest.TestCase):
    """Configuration testlari"""
    
    def test_config_loading(self):
        """Configuration Loading test"""
        config = get_security_config()
        
        self.assertIsNotNone(config)
        self.assertIsNotNone(config.rate_limiting)
        self.assertIsNotNone(config.security_headers)
        self.assertIsNotNone(config.input_validation)
        
        # Test default values
        self.assertGreater(config.rate_limiting.default_requests_per_minute, 0)
        self.assertGreater(config.input_validation.max_field_length, 0)
    
    def test_config_validation(self):
        """Configuration Validation test"""
        from security.config import validate_config, SecurityConfig
        
        config = SecurityConfig()
        errors = validate_config(config)
        
        # Should have no errors for default config
        self.assertEqual(len(errors), 0)


def run_all_tests():
    """Barcha testlarni ishga tushirish"""
    print("SECURITY VA RATE LIMITING TIZIMI TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()
    
    # Create test suite
    test_classes = [
        TestRateLimiting,
        TestSecurityValidation,
        TestAPISecurity,
        TestDataProtection,
        TestSecurityMonitoring,
        TestUtils,
        TestConfiguration
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 60)
    
    if result.wasSuccessful():
        print("✅ BARCHA TESTLAR MUVAFFAQIYATLI O'TDI!")
        print(f"✅ Jami testlar: {result.testsRun}")
        print(f"✅ Xatolar: {len(result.failures)}")
        print(f"✅ Muvaffaqiyatsizliklar: {len(result.errors)}")
    else:
        print("❌ BA'ZI TESTLAR MUVAFFAQIYATSIZ!")
        print(f"❌ Jami testlar: {result.testsRun}")
        print(f"❌ Xatolar: {len(result.failures)}")
        print(f"❌ Muvaffaqiyatsizliklar: {len(result.errors)}")
        
        if result.failures:
            print("\nXatolar:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\nMuvaffaqiyatsizliklar:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
    
    print(f"Test completed at: {datetime.now()}")
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)