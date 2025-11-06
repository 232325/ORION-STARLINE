# Security va Rate Limiting Tizimi Loyihasi

## Loyiha haqida

Bu loyiha keng qamrovli security va rate limiting tizimi bo'lib, zamonaviy veb ilovalar va API xizmatlari uchun xavfsizlikni ta'minlashga qaratilgan.

## Yaratilgan komponentlar

### 1. Rate Limiting (`code/security/rate_limiter.py`)
- Token Bucket Algorithm
- Sliding Window Rate Limiting
- Per-user rate limits
- API endpoint rate limits
- Burst handling

### 2. Security Validation (`code/security/security_validator.py`)
- Input validation
- SQL injection protection
- XSS protection
- CSRF protection
- CORS configuration

### 3. API Security (`code/security/api_security.py`)
- HTTPS enforcement
- Request signing
- API key rotation
- Audit logging
- Security headers

### 4. Data Protection (`code/security/data_protection.py`)
- Data encryption
- PII protection
- Secure data transmission
- Data anonymization
- Compliance (GDPR, CCPA)

### 5. Monitoring (`code/security/security_monitor.py`)
- Security event monitoring
- Intrusion detection
- Anomaly detection
- Security dashboards
- Incident response

### 6. Utility Functions (`code/security/utils.py`)
- IP address manipulation
- User agent parsing
- Security helpers
- Validation decorators

### 7. Configuration (`code/security/config.py`)
- Environment-based configs
- Security settings
- Rate limiting policies

## Asosiy xususiyatlar

✅ **Rate Limiting**: Token bucket, sliding window, per-user limits
✅ **Security**: Input validation, SQL/XSS protection, CSRF protection  
✅ **API Security**: JWT tokens, API keys, request signing, security headers
✅ **Data Protection**: Encryption, PII protection, anonymization, GDPR compliance
✅ **Monitoring**: Real-time security monitoring, anomaly detection, incident response

## Tez boshlash

```bash
cd code/security
pip install -r requirements.txt
python demo.py          # Demo ko'rish uchun
python test_security.py # Test ishga tushirish uchun
```

## Demo

Demo quyidagilarni ko'rsatadi:
- Rate limiting algoritmlarini
- Security validation testlarini
- API security funksiyalarini
- Data protection xususiyatlarini
- Monitoring va anomaly detection
- Keng qamrovli workflow

## Fayllar

| Fayl | Hajmi | Tavsif |
|------|-------|--------|
| `rate_limiter.py` | 14KB | Rate limiting algoritmlari |
| `security_validator.py` | 18KB | Input validation va security |
| `api_security.py` | 20KB | API xavfsizlik va authentication |
| `data_protection.py` | 22KB | Ma'lumot himoyalash va encryption |
| `security_monitor.py` | 33KB | Monitoring va anomaly detection |
| `utils.py` | 22KB | Utility funksiyalar |
| `config.py` | 18KB | Konfiguratsiya boshqaruvchisi |
| `demo.py` | 19KB | To'liq demo dastur |
| `test_security.py` | 15KB | Test dastur |
| `README.md` | 10KB | Loyiha dokumentatsiyasi |

**Jami**: ~193 KB

## Loyiha muvaffaqiyatli yakunlandi! ✅

Security va Rate Limiting tizimi to'liq ishlash holatida va production ishlatishga tayyor.