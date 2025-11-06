"""
Safety & Compliance System - Demo Script

Bu script safety compliance tizimining asosiy funksiyalarini ko'rsatadi.
"""

import sys
import os
sys.path.append('/workspace/orion-starline/backend/ai_modules')

from safety_compliance import (
    SafetyCompliance, 
    ContentType, 
    RiskLevel,
    ContentFilter,
    FinancialCompliance,
    DataProtection
)
import json

def demo_content_filtering():
    """Kontent filtrlash demo"""
    print("=" * 50)
    print("1. KONTENT FILTRASH DEMO")
    print("=" * 50)
    
    content_filter = ContentFilter()
    
    # Test cases
    test_cases = [
        ("Bu oddiy matn", "Oddiy matn"),
        ("100% kafolatlangan foyda oling", "Kafolatlangan daromad"),
        ("Scam va fraud haqida", "Fraud kontent"),
        ("Terrorizm haqida gap", "Xavfli kontent")
    ]
    
    for content, description in test_cases:
        is_clean, issues = content_filter.filter_content(content)
        print(f"\n{description}:")
        print(f"  Matn: {content}")
        print(f"  Toza: {is_clean}")
        if issues:
            print(f"  Muammolar: {issues}")

def demo_financial_compliance():
    """Moliyaviy muvofiqlik demo"""
    print("\n" + "=" * 50)
    print("2. MOLIYAVIY MUVOFIQLIK DEMO")
    print("=" * 50)
    
    financial_compliance = FinancialCompliance()
    
    # Test cases
    advice_1 = "Bu investitsiya bo'yicha maslahat. Har doim risk bor."
    advice_2 = "100% kafolatlangan daromad oling!"
    advice_3 = "Tejash uchun birjaga kiring."
    
    test_cases = [
        (advice_1, "To'g'ri maslahat"),
        (advice_2, "Kafolatlangan daromad"),
        (advice_3, "Birjaga taklif")
    ]
    
    for advice, description in test_cases:
        print(f"\n{description}:")
        print(f"  Maslahat: {advice}")
        
        is_compliant, issues = financial_compliance.validate_financial_advice(advice)
        print(f"  Muvofiq: {is_compliant}")
        if issues:
            print(f"  Muammolar: {issues}")
        
        # Disclaimer yaratish
        disclaimer = financial_compliance.generate_financial_disclaimer("trading")
        print(f"  \nDisclaimer:\n{disclaimer}")

def demo_data_protection():
    """Ma'lumotlar himoyasi demo"""
    print("\n" + "=" * 50)
    print("3. MA'LUMOTLAR HIMOYASI DEMO")
    print("=" * 50)
    
    data_protection = DataProtection()
    
    # Test user data
    user_data = {
        "name": "Ali Valiyev",
        "phone": "+998901234567", 
        "email": "ali@example.com",
        "id_card": "AB1234567",
        "bank_account": "1234567890123456"
    }
    
    print("Asl ma'lumotlar:")
    for key, value in user_data.items():
        print(f"  {key}: {value}")
    
    # Anonymize
    anonymized = data_protection.anonymize_data(user_data)
    
    print("\nAnonimizatsiya qilingan ma'lumotlar:")
    for key, value in anonymized.items():
        print(f"  {key}: {value}")

def demo_rate_limiting():
    """Rate limiting demo"""
    print("\n" + "=" * 50)
    print("4. RATE LIMITING DEMO")
    print("=" * 50)
    
    from safety_compliance import RateLimiter
    
    rate_limiter = RateLimiter()
    user_id = "demo_user_123"
    
    # Simulate multiple requests
    print("So'rovlar simulyatsiyasi:")
    for i in range(15):
        is_limited = rate_limiter.is_rate_limited(user_id, "api")
        remaining = rate_limiter.get_remaining_requests(user_id, "api")
        
        print(f"  So'rov {i+1}: "
              f"Cheklangan={is_limited}, "
              f"Qolgan={remaining}")
        
        if is_limited:
            print(f"    ⚠️ User {user_id} bloklandi!")
            break

def demo_full_system():
    """To'liq tizim demo"""
    print("\n" + "=" * 50)
    print("5. TO'LIQ TIZIM DEMO")
    print("=" * 50)
    
    # Initialize safety system
    config = {
        'audit_db_path': '/workspace/orion-starline/backend/audit_logs.db',
        'notification_email': 'admin@orion-starline.com'
    }
    
    safety_system = SafetyCompliance(config)
    
    # Test user input validation
    print("\nFoydalanuvchi kiritish validatsiyasi:")
    test_input = "Salom, bu test xabari"
    result = safety_system.validate_user_input(
        user_input=test_input,
        content_type=ContentType.GENERAL,
        user_id="demo_user_123",
        ip_address="192.168.1.100",
        user_agent="DemoBot/1.0"
    )
    
    print(f"  Matn: {test_input}")
    print(f"  Natija: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # Test system health
    print("\nTizim salomatligi:")
    health = safety_system.check_system_health()
    print(json.dumps(health, indent=2, ensure_ascii=False))
    
    # Test compliance report
    print("\nMuvofiqliq hisoboti (oxirgi 30 kun):")
    from datetime import datetime, timedelta
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    report = safety_system.generate_compliance_report(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )
    
    print(f"  Hisobot ID: {report['report_id']}")
    print(f"  Davr: {report['period']['start']} - {report['period']['end']}")
    print(f"  Risk darajasi: {report['risk_assessment']['overall_risk_level']}")

def demo_threat_detection():
    """Xavf aniqlash demo"""
    print("\n" + "=" * 50)
    print("6. XAVF ANIQLASH DEMO")
    print("=" * 50)
    
    safety_system = SafetyCompliance()
    
    # Simulate suspicious activity
    threat_data = {
        'identifier': 'suspicious_user',
        'ip_address': '192.168.1.200',
        'reason': 'multiple_failed_attempts',
        'block_duration': 3600
    }
    
    print("G'ayrioddiy faollik simulyatsiyasi:")
    print(f"  Identifikator: {threat_data['identifier']}")
    print(f"  IP manzil: {threat_data['ip_address']}")
    print(f"  Sabab: {threat_data['reason']}")
    
    # Block suspicious activity
    safety_system.block_suspicious_activity(threat_data)
    
    print("  ✅ G'ayrioddiy faollik bloklandi")
    
    # Enable real-time monitoring
    safety_system.enable_threat_detection()
    print("  ✅ Real-time monitoring yoqildi")

if __name__ == "__main__":
    print("🛡️  XAVFSIZLIK VA MUVOFIQLIQ TIZIMI DEMO")
    print("=" * 60)
    
    try:
        # Run all demos
        demo_content_filtering()
        demo_financial_compliance()
        demo_data_protection()
        demo_rate_limiting()
        demo_full_system()
        demo_threat_detection()
        
        print("\n" + "=" * 60)
        print("✅ Barcha demo muvaffaqiyatli tugallandi!")
        print("📖 Batafsil ma'lumot uchun README.md faylini ko'ring")
        print("🔧 To'liq API uchun safety_compliance.py faylini o'qiting")
        
    except Exception as e:
        print(f"\n❌ Demo jarayonida xatolik yuz berdi: {e}")
        print("Tizim konfiguratsiyasini tekshiring.")