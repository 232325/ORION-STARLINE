"""
AI Trade Explainer Demo - Barcha funksiyalar uchun namuna
AI Trade Explainer Demo - Examples for all functions
"""

import json
import datetime
from typing import Dict, List, Any
from trade_explainer import (
    TradeExplainer, TradingSignal, ExplanationRequest, 
    ComplexityLevel, ExplanationCategory, create_signal_explanation
)
from educational_content import (
    EducationalContentEngine, ContentType, LearningFormat,
    LearningModule, create_educational_content, generate_learning_schedule
)


class AITradeExplainerDemo:
    """AI Trade Explainer to'liq demo tizimi"""
    
    def __init__(self):
        self.trade_explainer = TradeExplainer(ComplexityLevel.INTERMEDIATE)
        self.educational_engine = EducationalContentEngine("uzbek")
        self.demo_sessions = {}
        
    def run_full_demo(self):
        """To'liq demo ishga tushirish"""
        print("=" * 80)
        print("🤖 AI TRADE EXPLAINER - TO'LIQ DEMO")
        print("=" * 80)
        
        # 1. Trade Signal Explanation Demo
        print("\n📊 1. SAVDO SIGNALI TUSHUNTIRISH")
        self.demo_trade_explanation()
        
        # 2. Educational Content Demo
        print("\n📚 2. TA'LIMIY KONTENT")
        self.demo_educational_content()
        
        # 3. Interactive Learning Demo
        print("\n🎓 3. INTERAKTIV O'RGANISH")
        self.demo_interactive_learning()
        
        # 4. Progress Tracking Demo
        print("\n📈 4. PROGRESS KUZATISH")
        self.demo_progress_tracking()
        
        # 5. Audio Features Demo
        print("\n🔊 5. AUDIO XUSUSIYATLAR")
        self.demo_audio_features()
        
        # 6. Social Learning Demo
        print("\n👥 6. IJTIMOIY O'RGANISH")
        self.demo_social_learning()
        
        print("\n✅ DEMO TUGALLANDI!")
        print("=" * 80)
    
    def demo_trade_explanation(self):
        """Trade explanation demo"""
        # Test signal yaratish
        signal = TradingSignal(
            symbol="AAPL",
            signal_type="BUY",
            confidence=0.78,
            entry_price=150.25,
            target_price=165.00,
            stop_loss=142.50,
            timeframe="1D",
            indicators={
                "RSI": 68,
                "MACD": "Bullish crossover",
                "SMA_20": 149.80,
                "Volume": "Above average 25%",
                "Bollinger": "Price near upper band",
                "Stochastic": "Oversold reversal"
            },
            market_conditions={
                "sentiment": "bullish",
                "volume": "high",
                "volatility": "moderate",
                "trend": "upward",
                "sector": "technology",
                "overall_market": "positive"
            }
        )
        
        # Turli xil savollar uchun tushuntirishlar
        questions = [
            {
                "question": "Nega BUY signal berildi?",
                "category": ExplanationCategory.WHY_THIS_SIGNAL
            },
            {
                "question": "Qanday risklar bor?",
                "category": ExplanationCategory.WHAT_RISKS
            },
            {
                "question": "Qaysi ko'rsatkichlar ishlatildi?",
                "category": ExplanationCategory.WHICH_INDICATORS
            },
            {
                "question": "Bozor holati qanday?",
                "category": ExplanationCategory.WHAT_MARKET_CONDITIONS
            },
            {
                "question": "Qachon chiqish kerak?",
                "category": ExplanationCategory.WHEN_TO_EXIT
            }
        ]
        
        for i, q_data in enumerate(questions, 1):
            print(f"\n--- {i}. Savol: {q_data['question']} ---")
            
            request = ExplanationRequest(
                signal=signal,
                question=q_data['question'],
                category=q_data['category'],
                complexity=ComplexityLevel.BEGINNER,
                include_alternatives=True
            )
            
            explanation = self.trade_explainer.explain_signal(request)
            
            # Tushuntirishni ko'rsatish
            print(f"📋 Tushuntirish:")
            print(explanation['explanation'])
            
            # Qo'shimcha ma'lumotlar
            if 'risk_assessment' in explanation:
                risk = explanation['risk_assessment']
                print(f"⚠️  Risk darajasi: {risk.get('risk_level', 'Noma\'lum')}")
            
            if 'alternatives' in explanation:
                print(f"🔄 Alternativlar: {len(explanation['alternatives'])} ta")
        
        # Confidence score o'zgarishi
        print(f"\n📊 Signal ishonchlilik: {signal.confidence:.1%}")
    
    def demo_educational_content(self):
        """Educational content demo"""
        # Learning path olish
        path = self.educational_engine.get_learning_path(
            ComplexityLevel.BEGINNER,
            [ContentType.TRADING_BASICS, ContentType.TECHNICAL_ANALYSIS]
        )
        
        print("📚 O'rganish yo'li:")
        print(f"Foydalanuvchi darajasi: {path['user_level']}")
        print(f"Modullar soni: {path['total_modules']}")
        print(f"Kutiladigan vaqt: {path['estimated_time']} daqiqa")
        
        # Birinchi modulni batafsil ko'rsatish
        if path['modules']:
            first_module = path['modules'][0]
            print(f"\n📖 Birinchi modul: {first_module['title']}")
            print(f"Vaqt: {first_module['estimated_time']} daqiqa")
            print("Maqsadlar:")
            for obj in first_module['learning_objectives']:
                print(f"  • {obj}")
        
        # Interactive tutorial yaratish
        tutorial = self.educational_engine.create_interactive_tutorial(
            ContentType.TECHNICAL_ANALYSIS, 
            ComplexityLevel.INTERMEDIATE
        )
        
        print(f"\n🎮 Interaktiv tutorial: {tutorial['tutorial_id']}")
        print(f"Bo'limlar soni: {len(tutorial['sections'])}")
        
        # Viktorina yaratish
        if path['modules']:
            quiz = self.educational_engine.generate_quiz(
                path['modules'][0]['module_id'], 
                num_questions=5
            )
            print(f"\n❓ Viktorina: {quiz['quiz_id']}")
            print(f"Savollar soni: {quiz['num_questions']}")
            print(f"Vaqt limiti: {quiz['time_limit']} soniya")
    
    def demo_interactive_learning(self):
        """Interactive learning demo"""
        print("🎯 Interaktiv o'rganish sessiyalari:")
        
        # Simulyatsiya yaratish
        simulations = self.educational_engine.interactive_simulator.get_simulations(
            ContentType.TECHNICAL_ANALYSIS
        )
        
        for sim in simulations:
            print(f"\n🎮 Simulyatsiya: {sim['title']}")
            print(f"Tavsif: {sim['description']}")
            print(f"Boshlang'ich balans: ${sim.get('initial_balance', 'N/A')}")
        
        # Voice explanation demo
        text = """
        AAPL aksiyasi uchun BUY signal yaratildi. 
        Bu signal texnik ko'rsatkichlar confluence asosida berilgan.
        RSI 68 darajada va MACD bullish crossover ko'rsatmoqda.
        """
        
        voice_exp = self.educational_engine.get_voice_explanation(text, "friendly")
        print(f"\n🔊 Voice explanation yaratildi:")
        print(f"File: {voice_exp['audio_url']}")
        print(f"Duration: {voice_exp['duration_estimate']:.1f} soniya")
        print(f"Style: {voice_exp['voice_style']}")
    
    def demo_progress_tracking(self):
        """Progress tracking demo"""
        user_id = "demo_user_001"
        
        # Module progress
        progress_data = {
            "completed": True,
            "time_spent": 45,
            "quiz_score": 85,
            "skill_improvement": {
                "skill": "technical_analysis",
                "amount": 10
            }
        }
        
        result = self.educational_engine.track_progress(user_id, "tech_001", progress_data)
        
        print("📈 Foydalanuvchi progressi:")
        print(f"Foydalanuvchi: {result['user_id']}")
        print(f"Tugallangan modullar: {len(result['progress']['modules_completed'])}")
        print(f"Jami vaqt: {result['progress']['total_time_spent']} daqiqa")
        print(f"Ko'nikma darajalari: {result['progress']['skill_levels']}")
        
        # Tavsiyalar
        if result['next_recommendations']:
            print("\n💡 Tavsiyalar:")
            for rec in result['next_recommendations']:
                print(f"  • {rec}")
        
        # Milestones
        if result['milestones']:
            print("\n🏆 Erishilgan natijalar:")
            for milestone in result['milestones']:
                print(f"  • {milestone['name']}: {milestone['description']}")
    
    def demo_audio_features(self):
        """Audio features demo"""
        print("🎵 Audio xususiyatlar:")
        
        # Background audio options
        background_types = [
            "White noise - konsentratsiya uchun",
            "Pink noise - iqlim vaqtida",
            "Brown noise - chuqur fikrlash",
            "Ambient soundscape - tinch muhit",
            "Binaural beats - focus uchun"
        ]
        
        print("Mavjud fon musiqa turlari:")
        for i, bg_type in enumerate(background_types, 1):
            print(f"  {i}. {bg_type}")
        
        # Audio processing options
        print("\n🔧 Audio qayta ishlash:")
        print("  • Fade in/out effektlari")
        print("  • Volume balanslash")
        print("  • Loop qilish")
        print("  • Compression (128kbps)")
        print("  • Voice overlay")
        
        # Interactive sounds
        interactive_sounds = [
            "Click - tugma bosilganda",
            "Hover - sichqoncha ustida",
            "Success - muvaffaqiyat",
            "Warning - ogohlantirish",
            "Error - xato"
        ]
        
        print("\n🔊 Interaktiv tovushlar:")
        for sound in interactive_sounds:
            print(f"  • {sound}")
    
    def demo_social_learning(self):
        """Social learning demo"""
        # Social learning space yaratish
        social_space = self.educational_engine.create_social_learning_space(
            ContentType.TECHNICAL_ANALYSIS
        )
        
        print("👥 Ijtimoiy o'rganish fazosi:")
        print(f"Space ID: {social_space['space_id']}")
        print(f"Mavzu: {social_space['topic']}")
        
        # Forumlar
        print(f"\n📋 Forumlar ({len(social_space['discussion_forums'])} ta):")
        for forum in social_space['discussion_forums']:
            print(f"  • {forum['title']}: {forum['description']}")
        
        # O'rganish guruhlari
        print(f"\n👨‍👩‍👧‍👦 O'rganish guruhlari:")
        for group in social_space['peer_learning_groups']:
            print(f"  • {group['name']} (Max: {group['max_members']} a'zo)")
        
        # Mentorship
        mentor = social_space['mentorship_program']
        print(f"\n🎓 Mentorship dasturi:")
        print(f"Mentorlar: {mentor['mentor_pool']} ta")
        print(f"Sessiya vaqti: {mentor['session_duration']} daqiqa")
        
        # Umumiy resurslar
        print(f"\n📚 Umumiy resurslar ({len(social_space['shared_resources'])} ta):")
        for resource in social_space['shared_resources']:
            print(f"  • {resource['title']} ({resource['type']})")
    
    def simulate_learning_session(self, user_level: str, duration: int = 60):
        """O'rganish sessiyasi simulyatsiyasi"""
        print(f"\n🎓 O'rganish sessiyasi simulyatsiyasi:")
        print(f"Daraja: {user_level}")
        print(f"Duration: {duration} daqiqa")
        
        # Learning path
        path = self.educational_engine.get_learning_path(
            ComplexityLevel(user_level)
        )
        
        print(f"Modullar: {path['total_modules']}")
        
        # Time allocation
        modules_per_session = 3
        time_per_module = duration / modules_per_session
        
        print(f"\nVaqt ajratish:")
        for i in range(modules_per_session):
            if i < len(path['modules']):
                module = path['modules'][i]
                print(f"  {i+1}. {module['title']}: {time_per_module:.0f} daqiqa")
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Performance report yaratish"""
        return {
            "report_id": f"perf_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.datetime.now().isoformat(),
            "metrics": {
                "explanations_generated": 25,
                "avg_response_time": "1.2 soniya",
                "user_satisfaction": "4.7/5.0",
                "completion_rate": "78%",
                "audio_engagement": "65%"
            },
            "content_performance": {
                "most_popular_module": "Technical Analysis Basics",
                "difficulty_distribution": {
                    "beginner": 40,
                    "intermediate": 45,
                    "advanced": 15
                },
                "engagement_metrics": {
                    "video_watch_time": "85%",
                    "quiz_completion": "72%",
                    "interactive_use": "68%"
                }
            },
            "recommendations": [
                "Qo'shimcha video content qo'shing",
                "Mobile experience yaxshilang",
                "Community features kengaytiring"
            ]
        }
    
    def export_learning_data(self, user_id: str) -> Dict[str, Any]:
        """Learning data eksport qilish"""
        return {
            "user_id": user_id,
            "export_date": datetime.datetime.now().isoformat(),
            "learning_history": [
                {
                    "date": "2024-01-15",
                    "module": "Trading Basics",
                    "duration": 45,
                    "score": 85
                },
                {
                    "date": "2024-01-16", 
                    "module": "Technical Analysis",
                    "duration": 60,
                    "score": 78
                }
            ],
            "skill_assessments": {
                "risk_management": 7,
                "technical_analysis": 8,
                "psychology": 6,
                "strategy_building": 5
            },
            "preferences": {
                "learning_style": "visual",
                "preferred_pace": "moderate",
                "audio_preference": "background_music"
            }
        }


# Utility functions
def create_sample_trade_scenarios() -> List[Dict[str, Any]]:
    """Sample trade senaryolari"""
    scenarios = [
        {
            "scenario_id": "bull_market_entry",
            "title": "Booming bozorda kirish",
            "context": "AAPL 15% o'sish ko'rsatdi",
            "signal": {
                "type": "BUY",
                "confidence": 0.82,
                "entry": 175.50,
                "target": 190.00,
                "stop": 168.00
            },
            "market_conditions": {
                "sentiment": "euphoric",
                "volume": "very_high",
                "volatility": "high"
            }
        },
        {
            "scenario_id": "bear_market_protection",
            "title": "Ayiq bozorida himoyalanish",
            "context": "TSLA -20% pasayish",
            "signal": {
                "type": "HOLD",
                "confidence": 0.65,
                "entry": None,
                "target": None,
                "stop": None
            },
            "market_conditions": {
                "sentiment": "fearful",
                "volume": "above_normal",
                "volatility": "very_high"
            }
        }
    ]
    
    return scenarios


def demo_advanced_features():
    """Advanced features demo"""
    print("\n🚀 ADVANCED FEATURES DEMO")
    print("=" * 50)
    
    # Multi-language support
    languages = ["uzbek", "english", "russian"]
    print("🌐 Multi-language support:")
    for lang in languages:
        print(f"  • {lang.title()}")
    
    # Voice synthesis styles
    voice_styles = {
        "friendly": "Do'stona va iliq",
        "professional": "Professional va rasmiy", 
        "educational": "Ta'limiy va tushuntiruvchi",
        "motivational": "Ruhlantiruvchi"
    }
    
    print("\n🗣️ Voice synthesis styles:")
    for style, description in voice_styles.items():
        print(f"  • {style}: {description}")
    
    # AI-powered suggestions
    print("\n🤖 AI-powered suggestions:")
    suggestions = [
        "Time-based market analysis",
        "Sentiment-based entry points",
        "Risk-adjusted position sizing",
        "Correlation-based diversification"
    ]
    
    for suggestion in suggestions:
        print(f"  • {suggestion}")


# Main demo function
def main():
    """Asosiy demo"""
    demo = AITradeExplainerDemo()
    
    # Full demo
    demo.run_full_demo()
    
    # Advanced features
    demo_advanced_features()
    
    # Sample scenarios
    print("\n🎯 SAMPLE TRADE SCENARIOS:")
    scenarios = create_sample_trade_scenarios()
    
    for scenario in scenarios:
        print(f"\n📊 {scenario['title']}:")
        print(f"Context: {scenario['context']}")
        print(f"Signal: {scenario['signal']['type']}")
        print(f"Confidence: {scenario['signal']['confidence']:.0%}")
    
    # Performance report
    print("\n📈 PERFORMANCE REPORT:")
    report = demo.generate_performance_report()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 80)
    print("🎉 AI TRADE EXPLAINER DEMO COMPLETED!")
    print("Ready for production deployment!")
    print("=" * 80)


if __name__ == "__main__":
    main()