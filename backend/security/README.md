# Security va Rate Limiting Tizimi

## Loyiha haqida

Bu loyiha keng qamrovli security va rate limiting tizimi bo'lib, zamonaviy veb ilovalar va API xizmatlari uchun xavfsizlikni ta'minlashga qaratilgan. Tizim turli xil xavfsizlik tahdidlariga qarshi himoya va traffic management imkoniyatlarini taqdim etadi.

## Xususiyatlar

### 🔒 Rate Limiting
- **Token Bucket Algorithm**: Burst so'rovlarni qayta ishlash
- **Sliding Window Rate Limiting**: Aniq so'rov cheklovlari
- **Per-user Rate Limits**: Foydalanuvchi asosida cheklovlar
- **API Endpoint Rate Limits**: Endpoint ga xos cheklovlar
- **Burst Handling**: Vaqtinchalik ko'p so'rovlarni boshqarish

### 🛡️ Security Features
- **Input Validation**: Kirish ma'lumotlarini tekshirish
- **SQL Injection Protection**: SQL injection hujumlaridan himoya
- **XSS Protection**: Cross-Site Scripting hujumlaridan himoya
- **CSRF Protection**: Cross-Site Request Forgery himoyasi
- **CORS Configuration**: Cross-Origin Resource Sharing sozlash

### 🔐 API Security
- **HTTPS Enforcement**: HTTPS majburiyatlari
- **Request Signing**: So'rovlarni imzolash
- **API Key Rotation**: API kalitlarni avtomatik rotatsiya
- **JWT Token Support**: JSON Web Token autentifikatsiya
- **Security Headers**: Xavfsizlik HTTP headerlari

### 🔐 Data Protection
- **Data Encryption**: Ma'lumotlarni shifrlash (AES-256)
- **PII Protection**: Shaxsiy ma'lumotlarni himoyalash
- **Secure Data Transmission**: Xavfsiz ma'lumot uzatish
- **Data Anonymization**: Ma'lumotlarni anonimizatsiya qilish
- **Compliance Support**: GDPR, CCPA, HIPAA moslashuvi

### 📊 Monitoring
- **Security Event Monitoring**: Xavfsizlik voqealarini kuzatish
- **Intrusion Detection**: Kirishni aniqlash
- **Anomaly Detection**: G'ayrioddiy faoliyatni aniqlash
- **Security Dashboards**: Xavfsizlik dashboardlari
- **Incident Response**: Incident javob choralari

## O'rnatish

```bash
# Repository ni clone qilish
git clone <repository-url>
cd code/security

# Virtual environment yaratish
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\\Scripts\\activate  # Windows

# Dependencies o'rnatish
pip install -r requirements.txt
```

## Tez boshlash

```python
from security import (
    RateLimiterManager, SecurityValidator, APISecurityManager,
    DataProtector, SecurityMonitor
)

# Rate Limiter sozlash
rate_limiter = RateLimiterManager()

# So'rovni tekshirish
allowed, metrics = rate_limiter.check_rate_limit("user123", "/api/v1/data")

# Security Validator
validator = SecurityValidator()
is_valid, violations = validator.validate_request(
    {"email": "user@example.com"}, 
    "192.168.1.1", 
    "Mozilla/5.0", 
    "/api/register"
)

# API Security Manager
api_security = APISecurityManager()
jwt_token = api_security.create_jwt_token("user123", ["read", "write"])

# Data Protection
data_protector = DataProtector()
encrypted = data_protector.encrypt_data("sensitive information")

# Monitoring
monitor = SecurityMonitor()
monitor.start_monitoring()
monitor.log_event("login_attempt", "192.168.1.1", "Mozilla/5.0", 
                 SecurityLevel.MEDIUM, "User login")
```

## Modullar tafsilotlari

### Rate Limiting (`rate_limiter.py`)

```python
from security.rate_limiter import TokenBucket, SlidingWindowRateLimiter

# Token Bucket
token_bucket = TokenBucket(capacity=10, refill_rate=1.0)
allowed = token_bucket.consume()

# Sliding Window
sliding_window = SlidingWindowRateLimiter(window_size=60, max_requests=100)
allowed = sliding_window.is_allowed("user123")
```

### Security Validation (`security_validator.py`)

```python
from security.security_validator import InputValidator

validator = InputValidator()

# Email validation
is_valid, error = validator.validate_email("user@example.com")

# Password validation
is_valid, errors = validator.validate_password("SecurePass123!")

# SQL injection detection
has_injection = validator.detect_sql_injection("SELECT * FROM users WHERE id = 1")
```

### API Security (`api_security.py`)

```python
from security.api_security import APISecurityManager

api_security = APISecurityManager()

# API Key yaratish
key_id, api_key = api_security.key_rotator.create_api_key(
    permissions=["read", "write"],
    expires_days=30
)

# JWT token
jwt_token = api_security.create_jwt_token("user123", ["read"])
```

### Data Protection (`data_protection.py`)

```python
from security.data_protection import DataProtector, PIIProtector

# Data encryption
data_protector = DataProtector()
encrypted = data_protector.encrypt_data("sensitive data")

# PII detection
pii_protector = PIIProtector()
pii_found = pii_protector.detect_pii("Email: user@example.com, Phone: 123-456-7890")
```

### Monitoring (`security_monitor.py`)

```python
from security.security_monitor import SecurityMonitor, SecurityLevel

monitor = SecurityMonitor()
monitor.start_monitoring()

# Event logging
monitor.log_event(
    event_type="failed_login",
    source_ip="192.168.1.100",
    user_agent="Mozilla/5.0",
    severity=SecurityLevel.HIGH,
    description="Multiple failed login attempts"
)
```

## Konfiguratsiya

Konfiguratsiya `config.py` faylida joylashgan:

```python
from security.config import get_security_config, SecurityConfig

config = get_security_config()

# Rate limiting konfiguratsiyasi
config.rate_limiting.default_requests_per_minute = 100

# Security headers
config.security_headers.content_security_policy = "default-src 'self'"

# Monitoring
config.monitoring.enabled = True
config.monitoring.anomaly_detection_enabled = True
```

### Environment Variables

```bash
# Database va Redis
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379

# Email konfiguratsiyasi
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SECURITY_EMAIL_TO=admin@company.com

# Slack integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SLACK_CHANNEL=#security-alerts

# Feature flags
SECURITY_FEATURE_RATE_LIMITING=true
SECURITY_FEATURE_MONITORING=true
```

## Demo

To'liq demo uchun:

```bash
cd code/security
python demo.py
```

Demo quyidagilarni ko'rsatadi:
- Barcha rate limiting algoritmlarini
- Security validation testlarini
- API security funksiyalarini
- Data protection xususiyatlarini
- Monitoring va anomaly detection
- Keng qamrovli workflow

## Production Deployment

### 1. Security Checklist

- [ ] HTTPS majburiy qilindi
- [ ] Environment variables sozlandi
- [ ] Database SSL connection
- [ ] Redis authentication
- [ ] Email/SMS notification konfiguratsiya qilindi
- [ ] Security headers to'g'ri sozlandi
- [ ] Rate limiting endpoint uchun sozlandi
- [ ] Monitoring va logging yoqildi

### 2. Environment Setup

```python
# Production konfiguratsiya
from security.config import get_config_for_environment

config = get_config_for_environment('production')

# Rate limiting qat'iy sozlar
config.rate_limiting.default_requests_per_minute = 60
config.input_validation.strict_mode = True
config.security_headers.content_security_policy = "default-src 'self'"

# Logging qat'iy
config.log_level = 'WARNING'
config.features['debug_mode'] = False
```

## Troubleshooting

### Tez-tez uchraydigan muammolar

1. **Redis connection error**
   ```bash
   # Redis ni ishga tushirish
   redis-server
   
   # Connection string tekshirish
   echo $REDIS_URL
   ```

2. **JWT token validation failed**
   ```python
   # Secret key tekshirish
   print(f"JWT Secret: {api_security.jwt_secret}")
   
   # Token expiration tekshirish
   import jwt
   payload = jwt.decode(token, secret, algorithms=['HS256'], options={"verify_exp": True})
   ```

3. **Rate limiting not working**
   ```python
   # Metriklarni tekshirish
   metrics = rate_limiter.get_metrics()
   print(f"Active buckets: {metrics['total_buckets']}")
   
   # Redis connection tekshirish
   print(rate_limiter.redis_client.ping())
   ```

4. **Email notifications not working**
   ```bash
   # SMTP settings
   export SMTP_SERVER=smtp.gmail.com
   export SMTP_USERNAME=your_email@gmail.com
   export SMTP_PASSWORD=your_app_password
   ```

## Best Practices

### 1. Rate Limiting
```python
# Per-user rate limits
rate_limiter.set_user_limit("user123", RateLimitConfig(
    requests_per_minute=100,
    burst_limit=10
))

# Admin users
config = EndpointConfig(
    endpoint="/api/v1/admin/*",
    config=RateLimitConfig(requests_per_minute=1000),
    exempt_users=["admin1", "admin2"]
)
```

### 2. Input Validation
```python
# Strict validation
validator = InputValidator()
sanitized = validator.sanitize_input(user_input)

# File upload validation
is_valid, error = SecurityValidators.validate_file_upload(
    filename="document.pdf",
    allowed_extensions=['.pdf', '.doc', '.docx'],
    max_size=10 * 1024 * 1024  # 10MB
)
```

### 3. Data Protection
```python
# PII anonymization
pii_protector = PIIProtector()
sensitive_data = {
    "email": "user@example.com",
    "phone": "123-456-7890"
}

for field, value in sensitive_data.items():
    anonymized = pii_protector.anonymize_pii(field, value)
    print(f"{field}: {anonymized}")
```

### 4. Monitoring
```python
# Real-time monitoring
monitor = SecurityMonitor()

# Custom alert rules
alert_rule = AlertRule(
    rule_id="custom_threat",
    name="Custom Threat Detection",
    condition={"event_type": "suspicious_activity", "threshold": 5},
    severity=SecurityLevel.CRITICAL
)
monitor.add_alert_rule(alert_rule)
```

---

**Eslatma**: Bu security tizimi production muhitida ishlatishdan oldin to'liq test qilinishi zarur. Barcha konfiguratsiya va security sozlamalari o'zingizning maxsus talablaringizga mos ravishda sozlanganligini tekshiring.

**Demo yakunlandi! ✅**
Security va Rate Limiting tizimi to'liq yaratildi va ishlatishga tayyor.