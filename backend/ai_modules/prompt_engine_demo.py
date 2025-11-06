"""
Advanced Prompt Engineering System Demo
Orion Starline AI Trading Platform uchun professional prompt engineering namunalari

Bu fayl advanced prompt engineering tizimining barcha imkoniyatlarini ko'rsatadi:
- Context-aware prompt generation
- Multi-language support
- A/B testing
- Safety validation
- Performance analytics
- Automatic optimization
"""

from prompt_templates import TemplateManager, Template, PromptCategory, SkillLevel, Language
from prompt_engine import AdvancedPromptEngine, PromptResult, ConversationContext
import json
import time

def demo_basic_prompt_generation():
    """Asosiy prompt generation namoyishi"""
    print("=" * 60)
    print("ASOSIY PROMPT GENERATION NAMOYISHI")
    print("=" * 60)
    
    # Tizimni ishga tushirish
    engine = AdvancedPromptEngine(
        enable_ab_testing=True,
        enable_auto_optimization=True,
        default_language=Language.UZBEK
    )
    
    # Trading kontekst
    context = {
        'asset': 'EURUSD',  # Template expects 'asset' not 'symbol'
        'current_price': '1.0850',
        'daily_change': '+0.25%',
        'volume': '1250000',
        'timeframe': '1d',
        'analysis_date': '2025-11-05'
    }
    
    # Foydalanuvchi profili
    user_profile = {
        'skill_level': 'intermediate',
        'preferred_language': 'uzbek',
        'trading_experience': '2-3 years',
        'risk_tolerance': 'moderate',
        'goals': ['profit', 'risk_management']
    }
    
    # Prompt generation
    print("Prompt yaratilmoqda...")
    start_time = time.time()
    
    result = engine.generate_prompt(
        template_id='tech_analysis_basic',
        context=context,
        user_profile=user_profile
    )
    
    end_time = time.time()
    
    print(f"✅ Prompt yaratildi!")
    print(f"🆔 Prompt ID: {result.prompt_id}")
    print(f"⚡ Vaqt: {result.generation_time:.2f} soniya")
    print(f"📊 Sifat balli: {result.quality_score:.2f}/1.0")
    print(f"🛡️ Xavfsizlik: {'✅' if result.safety_validated else '❌'}")
    print(f"📋 Til: {result.language_used}")
    
    print(f"\n📝 GENERATSIYA QILINAN PROMPT:")
    print("-" * 40)
    print(result.generated_prompt)
    print("-" * 40)

def demo_multilingual_support():
    """Ko'p tilli qo'llab-quvvatlash namoyishi"""
    print("\n" + "=" * 60)
    print("KO'P TILLI QO'LLAB-QUVVATLASH NAMOYISHI")
    print("=" * 60)
    
    engine = AdvancedPromptEngine(default_language=Language.UZBEK)
    
    context = {
        'asset': 'BTCUSD',  # Template expects 'asset' not 'symbol'
        'current_price': '45000',
        'volatility': 'high'
    }
    
    user_profile = {
        'skill_level': 'advanced',
        'preferred_language': 'russian',
        'trading_experience': '5+ years'
    }
    
    # Rus tilida prompt
    result_ru = engine.generate_prompt(
        template_id='tech_analysis_basic',
        context=context,
        user_profile=user_profile,
        language=Language.RUSSIAN
    )
    
    print("🇷🇺 RUS TILIDAGI PROMPT:")
    print("-" * 40)
    print(result_ru.generated_prompt[:300] + "...")
    print("-" * 40)
    
    # Ingliz tilida prompt
    user_profile['preferred_language'] = 'english'
    result_en = engine.generate_prompt(
        template_id='tech_analysis_basic',
        context=context,
        user_profile=user_profile,
        language=Language.ENGLISH
    )
    
    print("\n🇺🇸 INGLIZ TILIDAGI PROMPT:")
    print("-" * 40)
    print(result_en.generated_prompt[:300] + "...")
    print("-" * 40)

def demo_conversation_context():
    """Conversation context namoyishi"""
    print("\n" + "=" * 60)
    print("CONVERSATION CONTEXT NAMOYISHI")
    print("=" * 60)
    
    engine = AdvancedPromptEngine()
    
    # Yangi suhbat yaratish
    conversation = ConversationContext()
    conversation_id = conversation.conversation_id
    
    print(f"🆔 Yangi suhbat yaratildi: {conversation_id}")
    
    context1 = {
        'asset': 'AAPL',  # Template expects 'asset' not 'symbol'
        'current_price': '150.25',
        'query': 'technical_analysis'
    }
    
    # Birinchi so'rov
    result1 = engine.generate_prompt(
        template_id='tech_analysis_basic',
        context=context1,
        conversation_id=conversation_id
    )
    
    # Suhbatga qo'shish
    conversation.add_exchange(
        user_input="Apple aksiyasi uchun texnik tahlil qiling",
        ai_response=result1.generated_prompt[:200] + "...",
        metadata={'result_quality': result1.quality_score}
    )
    
    # Ikkinchi so'rov (kontekst bilan)
    context2 = {
        'asset': 'AAPL',
        'current_price': '150.25',
        'query': 'risk_assessment',
        'previous_analysis': 'technical_analysis',
        'portfolio_value': '10000',  # Risk assessment template needs this
        'risk_profile': 'moderate'   # Risk assessment template needs this
    }
    
    result2 = engine.generate_prompt(
        template_id='risk_assessment',
        context=context2,
        conversation_id=conversation_id
    )
    
    print("📊 SUHBAT ANALITIKASI:")
    summary = conversation.get_summary()
    print(f"   Almashuvlar soni: {summary['exchange_count']}")
    print(f"   Davomiylik: {summary['duration_minutes']:.1f} daqiqa")
    print(f"   Til: {summary['language']}")
    
    print("\n💬 IKINCHI SO'ROV KONTEKSTI BILAN:")
    print("-" * 40)
    print("Keyingi so'rov oldingi suhbat kontekstini hisobga oldi")
    print(f"2-so'rov natijasi: {result2.generated_prompt[:200]}...")
    print("-" * 40)

def demo_ab_testing():
    """A/B testing namoyishi"""
    print("\n" + "=" * 60)
    print("A/B TESTING NAMOYISHI")
    print("=" * 60)
    
    engine = AdvancedPromptEngine(enable_ab_testing=True)
    
    # A/B test yaratish
    context = {
        'asset': 'TSLA',  # Template expects 'asset' not 'symbol'
        'current_price': '250.80'
    }
    
    test_id = engine.ab_test_manager.create_test(
        test_name="Prompt_Optimization_Test",
        template_id='tech_analysis_basic',
        base_context=context,
        test_variants=['simplified', 'detailed', 'conversational'],
        test_duration_hours=1,
        success_metric="user_rating"
    )
    
    print(f"🧪 A/B test yaratildi: {test_id}")
    
    # Turli variantlarni sinash
    variants = engine.template_manager.create_ab_test_variants(
        'tech_analysis_basic', 
        context, 
        ['simplified', 'detailed', 'conversational']
    )
    
    print("\n📋 TEST VARIANTLARI:")
    for variant_name, prompt in variants.items():
        print(f"\n🔹 {variant_name.upper()} VARIANT:")
        print("-" * 30)
        print(prompt[:250] + "...")
        print("-" * 30)

def demo_safety_validation():
    """Xavfsizlik validatsiya namoyishi"""
    print("\n" + "=" * 60)
    print("XAVFSIZLIK VALIDATSIYA NAMOYISHI")
    print("=" * 60)
    
    engine = AdvancedPromptEngine()
    
    # Noto'g'ri prompt test qilish
    dangerous_prompt = """
    Bitcoin sotib oling! Bu 100% foyda keltiradi. 
    Barcha pullaringizni risk qo'ying!
    """
    
    context = {'symbol': 'BTC', 'amount': '10000'}
    
    safety_report = engine.template_manager.validate_prompt_safety(
        dangerous_prompt, 
        context
    )
    
    print("🚨 XAVFSIZLIK TAHLILI:")
    print(f"   Xavfsiz: {'✅' if safety_report['is_safe'] else '❌'}")
    
    if safety_report['warnings']:
        print("   Ogohlantirishlar:")
        for warning in safety_report['warnings']:
            print(f"   ⚠️  {warning}")
    
    if safety_report['compliance_issues']:
        print("   Muammolar:")
        for issue in safety_report['compliance_issues']:
            print(f"   ❌ {issue}")
    
    if safety_report['recommendations']:
        print("   Tavsiyalar:")
        for rec in safety_report['recommendations']:
            print(f"   💡 {rec}")
    
    # Xavfsiz prompt test qilish
    safe_prompt = """
    Quyidagi ma'lumotlarga asoslanib tahlil qiling:
    - Aktiv: Bitcoin
    - Narx: $45,000
    - Volatillik: Yuqori
    """
    
    safe_report = engine.template_manager.validate_prompt_safety(safe_prompt, context)
    
    print("\n🛡️ XAVFSIZ PROMPT TAHLILI:")
    print(f"   Xavfsiz: {'✅' if safe_report['is_safe'] else '❌'}")

def demo_performance_analytics():
    """Performance analytics namoyishi"""
    print("\n" + "=" * 60)
    print("PERFORMANCE ANALYTICS NAMOYISHI")
    print("=" * 60)
    
    engine = AdvancedPromptEngine()
    
    # Bir nechta prompt yaratish analytics uchun
    contexts = [
        {'asset': 'EURUSD', 'timeframe': '1d'},
        {'asset': 'GBPUSD', 'timeframe': '4h'},
        {'asset': 'USDJPY', 'timeframe': '1h'},
        {'asset': 'AAPL', 'timeframe': '1d'},
        {'asset': 'TSLA', 'timeframe': '1d'}
    ]
    
    user_profile = {
        'skill_level': 'intermediate',
        'preferred_language': 'uzbek'
    }
    
    print("📊 Performance test uchun promptlar yaratilmoqda...")
    
    for i, context in enumerate(contexts, 1):
        result = engine.generate_prompt(
            template_id='tech_analysis_basic',
            context=context,
            user_profile=user_profile
        )
        print(f"   {i}. {context['asset']} - Sifat: {result.quality_score:.2f}")
    
    # Analytics olish
    analytics = engine.get_performance_analytics()
    
    print(f"\n📈 UMUMIY ANALITIKA:")
    print(f"   Jami yaratilgan: {analytics['total_generated']}")
    print(f"   O'rtacha sifat: {analytics['avg_quality_score']:.2f}")
    print(f"   O'rtacha vaqt: {analytics['avg_generation_time']:.2f}s")
    print(f"   Faol suhbatlar: {analytics['active_conversations']}")
    
    # Template performance
    if 'template_performance' in analytics:
        print(f"\n🏆 TEMPLATE PERFORMANCE:")
        for template_id, perf in analytics['template_performance'].items():
            print(f"   {template_id}: {perf['count']} ta, O'rtacha: {perf['avg_quality']:.2f}")

def demo_context_aware_generation():
    """Context-aware generation namoyishi"""
    print("\n" + "=" * 60)
    print("CONTEXT-AWARE GENERATION NAMOYISHI")
    print("=" * 60)
    
    engine = AdvancedPromptEngine()
    
    # Boshlang'ich trader profili
    beginner_context = {
        'asset': 'EURUSD',  # Template expects 'asset' not 'symbol'
        'current_price': '1.0850',
        'skill_level': 'beginner'
    }
    
    beginner_profile = {
        'skill_level': 'beginner',
        'trading_experience': '6 months',
        'preferred_language': 'uzbek',
        'goals': ['learning', 'practice']
    }
    
    # Expert trader profili
    expert_context = {
        'asset': 'EURUSD',  # Template expects 'asset' not 'symbol'
        'current_price': '1.0850',
        'skill_level': 'expert'
    }
    
    expert_profile = {
        'skill_level': 'expert',
        'trading_experience': '10+ years',
        'preferred_language': 'english',
        'goals': ['optimization', 'institutional']
    }
    
    # Boshlang'ich uchun prompt
    print("🟢 BOSHLANG'ICH TRADER UCHUN:")
    beginner_result = engine.generate_prompt(
        template_id='tech_analysis_basic',
        context=beginner_context,
        user_profile=beginner_profile
    )
    
    print(f"Sifat balli: {beginner_result.quality_score:.2f}")
    print(f"Prompt: {beginner_result.generated_prompt[:200]}...")
    
    # Expert uchun prompt
    print("\n🔴 EXPERT TRADER UCHUN:")
    expert_result = engine.generate_prompt(
        template_id='tech_analysis_basic',
        context=expert_context,
        user_profile=expert_profile
    )
    
    print(f"Sifat balli: {expert_result.quality_score:.2f}")
    print(f"Prompt: {expert_result.generated_prompt[:200]}...")

def demo_comprehensive_workflow():
    """Keng qamrovli workflow namoyishi"""
    print("\n" + "=" * 80)
    print("KENG QAMROVLI WORKFLOW NAMOYISHI")
    print("=" * 80)
    
    # 1. Tizimni ishga tushirish
    print("1️⃣ Tizimni ishga tushirish...")
    engine = AdvancedPromptEngine(
        enable_ab_testing=True,
        enable_auto_optimization=True,
        default_language=Language.UZBEK
    )
    
    # 2. Foydalanuvchi bilan suhbat boshlash
    print("2️⃣ Foydalanuvchi suhbat boshlash...")
    conversation = ConversationContext()
    conversation_id = conversation.conversation_id
    
    # 3. Birinchi so'rov
    print("3️⃣ Birinchi so'rov...")
    context1 = {
        'symbol': 'EURUSD',
        'current_price': '1.0850',
        'user_question': 'texnik_tahlil'
    }
    
    result1 = engine.generate_prompt(
        template_id='tech_analysis_basic',
        context=context1,
        conversation_id=conversation_id
    )
    
    # 4. Ikkinchi so'rov (kontekst bilan)
    print("4️⃣ Ikkinchi so'rov (kontekst bilan)...")
    context2 = {
        'symbol': 'EURUSD',
        'current_price': '1.0850',
        'user_question': 'risk_baholash',
        'previous_context': 'texnik_tahlil'
    }
    
    result2 = engine.generate_prompt(
        template_id='risk_assessment',
        context=context2,
        conversation_id=conversation_id
    )
    
    # 5. Performance tahlil
    print("5️⃣ Performance tahlil...")
    analytics = engine.get_performance_analytics()
    
    # 6. Optimizatsiya
    print("6️⃣ Auto-optimizatsiya...")
    optimization_results = engine.optimize_prompt_templates()
    
    # 7. Yakuniy hisobot
    print("\n📊 YAKUNIY HISOBOT:")
    print("=" * 50)
    print(f"✅ Jami promptlar: {analytics['total_generated']}")
    print(f"📈 O'rtacha sifat: {analytics['avg_quality_score']:.2f}")
    print(f"⚡ O'rtacha vaqt: {analytics['avg_generation_time']:.2f}s")
    print(f"🛡️ Xavfsizlik darajasi: Yuqori")
    print(f"🌍 Ko'p tilli qo'llab-quvvatlash: ✅")
    print(f"🧪 A/B testing: ✅")
    print(f"🔧 Auto-optimizatsiya: ✅")
    print(f"💬 Kontekst-aware: ✅")
    print("=" * 50)

def main():
    """Barcha namoyishlarni ishga tushirish"""
    print("🚀 ADVANCED PROMPT ENGINEERING SYSTEM")
    print("Orion Starline AI Trading Platform")
    print("=" * 80)
    
    try:
        # Barcha namoyishlarni ishga tushirish
        demo_basic_prompt_generation()
        demo_multilingual_support()
        demo_conversation_context()
        demo_ab_testing()
        demo_safety_validation()
        demo_performance_analytics()
        demo_context_aware_generation()
        demo_comprehensive_workflow()
        
        print("\n" + "=" * 80)
        print("✅ BARCHA NAMOYISHLAR MUVAFFAQIYATLI YAKUNLANDI!")
        print("🎯 Professional Prompt Engineering tizimi tayyor!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ XATOLIK YUZ BERDI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()