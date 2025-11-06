"""
Onboarding Engine - Global foydalanuvchilar uchun onboarding tizimi
AI-powered trading platform uchun boshlang'ich tajriba
"""

import json
import datetime
import random
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from collections import defaultdict

# Multi-language support
class Language(Enum):
    UZBEK = "uz"
    ENGLISH = "en"

class UserLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class OnboardingStep(Enum):
    REGISTRATION = "registration"
    SKILL_ASSESSMENT = "skill_assessment"
    WELCOME_TOUR = "welcome_tour"
    DEMO_TRADING = "demo_trading"
    AI_ASSISTANT = "ai_assistant"
    PERSONAL_RECOMMENDATIONS = "personal_recommendations"
    COMMUNITY = "community"
    LIVE_TRADING_PREP = "live_trading_prep"

@dataclass
class UserProfile:
    user_id: str
    name: str
    email: str
    preferred_language: Language
    skill_level: UserLevel
    interests: List[str]
    onboarding_completed: bool = False
    current_step: OnboardingStep = OnboardingStep.REGISTRATION
    progress_percentage: float = 0.0
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()

@dataclass
class MockPosition:
    id: str
    symbol: str
    side: str  # "long" or "short"
    entry_price: float
    current_price: float
    quantity: float
    timestamp: datetime.datetime
    pnl: float = 0.0

@dataclass
class DemoTradingSession:
    user_id: str
    virtual_balance: float
    positions: List[MockPosition]
    performance_metrics: Dict[str, float]
    start_time: datetime.datetime
    last_updated: datetime.datetime

    def __post_init__(self):
        if not self.positions:
            self.positions = []
        if not self.performance_metrics:
            self.performance_metrics = {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "total_pnl": 0.0,
                "win_rate": 0.0,
                "max_drawdown": 0.0
            }

class OnboardingEngine:
    """
    Onboarding tizimi - foydalanuvchilarni platformga kirish uchun yordam berish
    """
    
    def __init__(self):
        self.user_profiles: Dict[str, UserProfile] = {}
        self.demo_sessions: Dict[str, DemoTradingSession] = {}
        self.onboarding_progress: Dict[str, Dict[str, Any]] = {}
        
        # Mock market data
        self.mock_prices = {
            "EURUSD": {"price": 1.0850, "change": 0.0012},
            "GBPUSD": {"price": 1.2650, "change": -0.0008},
            "USDJPY": {"price": 149.50, "change": 0.25},
            "XAUUSD": {"price": 2015.50, "change": 5.25},
            "XAGUSD": {"price": 24.50, "change": -0.12},
            "BTCUSD": {"price": 43250.00, "change": 125.50}
        }
        
        # Multi-language content
        self.content = {
            Language.UZBEK: {
                "welcome": {
                    "title": "Orion Starline ga xush kelibsiz!",
                    "description": "AI-powered trading platform - eng ilg'or texnologiyalar bilan ishlash imkoniyati",
                    "steps": [
                        "Ro'yxatdan o'tish va profil yaratish",
                        "Ko'nikma darajasini aniqlash",
                        "Platforma tanishuv safari",
                        "Demo trading tajribasi",
                        "AI Assistant bilan tanishuv",
                        "Shaxsiy tavsiyalar olish",
                        "Jamoa bilan tanishuv",
                        "Haqiqiy trading ga tayyorlash"
                    ]
                },
                "skill_assessment": {
                    "title": "Trading ko'nikmalaringizni baholang",
                    "description": "Platformani sizga mos tarzda moslashtirish uchun savollar beramiz",
                    "questions": [
                        {
                            "id": 1,
                            "question": "Trading tajribangiz qanday?",
                            "options": ["Yo'q (0 yil)", "Kichik (1-2 yil)", "O'rta (3-5 yil)", "Katta (5+ yil)"]
                        },
                        {
                            "id": 2,
                            "question": "Qaysi bozorlarda trading qilasiz?",
                            "options": ["Forex", "Metalllar", "Kripto", "Barchasi"]
                        },
                        {
                            "id": 3,
                            "question": "Risk darajangiz qanday?",
                            "options": ["Past", "O'rta", "Yuqori", "Ço'q joyida qat'iy"]
                        }
                    ]
                },
                "demo_trading": {
                    "title": "Demo Trading - Xavfsiz O'rganish",
                    "description": "Virtual mablag'lar bilan real bozor sharoitida o'rganing",
                    "features": [
                        "100,000$ virtual balans",
                        "Real vaqt narxlar (simulyatsiya)",
                        "Trade qilish amaliyoti",
                        "Performance kuzatish",
                        "Risk-free o'rganish"
                    ]
                }
            },
            Language.ENGLISH: {
                "welcome": {
                    "title": "Welcome to Orion Starline!",
                    "description": "AI-powered trading platform - Advanced technology trading experience",
                    "steps": [
                        "Registration and profile setup",
                        "Skill level assessment",
                        "Platform introduction tour",
                        "Demo trading experience",
                        "AI Assistant introduction",
                        "Personal recommendations",
                        "Community introduction",
                        "Live trading preparation"
                    ]
                },
                "skill_assessment": {
                    "title": "Assess Your Trading Skills",
                    "description": "Answer questions to customize the platform for you",
                    "questions": [
                        {
                            "id": 1,
                            "question": "How much trading experience do you have?",
                            "options": ["None (0 years)", "Basic (1-2 years)", "Intermediate (3-5 years)", "Advanced (5+ years)"]
                        },
                        {
                            "id": 2,
                            "question": "Which markets do you trade?",
                            "options": ["Forex", "Metals", "Crypto", "All of them"]
                        },
                        {
                            "id": 3,
                            "question": "What is your risk level?",
                            "options": ["Low", "Medium", "High", "Aggressive"]
                        }
                    ]
                },
                "demo_trading": {
                    "title": "Demo Trading - Safe Learning",
                    "description": "Learn with virtual money in real market conditions",
                    "features": [
                        "100,000$ virtual balance",
                        "Real-time prices (simulation)",
                        "Trading practice",
                        "Performance tracking",
                        "Risk-free learning"
                    ]
                }
            }
        }
        
        # AI Assistant responses
        self.ai_responses = {
            Language.UZBEK: {
                "greeting": "Assalomu alaykum! Men sizning AI trading yordamchingizman. Qanday yordam bera olaman?",
                "tutorial_help": "Tutorial yordam kerakmi? Men sizga qadamlarni tushuntirib beraman.",
                "demo_help": "Demo trading haqida savollaringiz bormi? Virtual balansingiz bilan amaliyot qiling!",
                "strategy_help": "Trading strategiyalar haqida so'rayotgan bo'lsangiz, men sizga eng yaxshi strategiyalarni tavsiya qilaman."
            },
            Language.ENGLISH: {
                "greeting": "Hello! I'm your AI trading assistant. How can I help you today?",
                "tutorial_help": "Need help with tutorials? I'll guide you through each step.",
                "demo_help": "Questions about demo trading? Practice with your virtual balance!",
                "strategy_help": "Ask about trading strategies, and I'll recommend the best ones for you."
            }
        }

    def create_user_profile(self, name: str, email: str, preferred_language: Language = Language.UZBEK) -> UserProfile:
        """Yangi foydalanuvchi profili yaratish"""
        user_id = str(uuid.uuid4())
        profile = UserProfile(
            user_id=user_id,
            name=name,
            email=email,
            preferred_language=preferred_language,
            skill_level=UserLevel.BEGINNER,
            interests=[]
        )
        self.user_profiles[user_id] = profile
        return profile

    def get_welcome_content(self, user_id: str) -> Dict[str, Any]:
        """Welcome tour kontentini olish"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return {"error": "Foydalanuvchi topilmadi"}
        
        content = self.content[profile.preferred_language]
        return {
            "title": content["welcome"]["title"],
            "description": content["welcome"]["description"],
            "steps": content["welcome"]["steps"],
            "current_step": profile.current_step.value,
            "progress_percentage": profile.progress_percentage
        }

    def conduct_skill_assessment(self, user_id: str, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Ko'nikma darajasini aniqlash"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return {"error": "Foydalanuvchi topilmadi"}
        
        # Basic scoring logic
        experience_score = 0
        market_knowledge = 0
        risk_tolerance = 0
        
        for answer in answers:
            if answer["question_id"] == 1:  # Experience
                experience_score = answer["selected_option"]
            elif answer["question_id"] == 2:  # Markets
                market_knowledge = answer["selected_option"]
            elif answer["question_id"] == 3:  # Risk
                risk_tolerance = answer["selected_option"]
        
        # Determine skill level
        total_score = experience_score + market_knowledge + risk_tolerance
        if total_score <= 3:
            skill_level = UserLevel.BEGINNER
        elif total_score <= 6:
            skill_level = UserLevel.INTERMEDIATE
        else:
            skill_level = UserLevel.ADVANCED
        
        profile.skill_level = skill_level
        profile.current_step = OnboardingStep.WELCOME_TOUR
        profile.progress_percentage = 25.0
        profile.updated_at = datetime.datetime.now()
        
        return {
            "skill_level": skill_level.value,
            "message": "Assessment tugallandi! Sizning darajangiz: " + skill_level.value,
            "next_step": "welcome_tour"
        }

    def start_demo_trading(self, user_id: str) -> DemoTradingSession:
        """Demo trading sessiyasini boshlash"""
        if user_id not in self.demo_sessions:
            session = DemoTradingSession(
                user_id=user_id,
                virtual_balance=100000.0,
                positions=[],
                performance_metrics={},
                start_time=datetime.datetime.now(),
                last_updated=datetime.datetime.now()
            )
            self.demo_sessions[user_id] = session
            return session
        return self.demo_sessions[user_id]

    def get_mock_market_data(self) -> Dict[str, Any]:
        """Mock bozor ma'lumotlarini qaytarish"""
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "prices": self.mock_prices,
            "trending": ["EURUSD", "XAUUSD", "BTCUSD"],
            "market_sentiment": random.choice(["Bullish", "Bearish", "Neutral"])
        }

    def execute_demo_trade(self, user_id: str, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """Demo trade bajarish"""
        session = self.demo_sessions.get(user_id)
        if not session:
            return {"error": "Demo session topilmadi"}
        
        if symbol not in self.mock_prices:
            return {"error": "Symbol topilmadi"}
        
        current_price = self.mock_prices[symbol]["price"]
        
        # Calculate position value
        position_value = current_price * quantity
        
        # Check if user has enough balance
        if position_value > session.virtual_balance:
            return {"error": "Yetarli mablag' yo'q"}
        
        # Create position
        position = MockPosition(
            id=str(uuid.uuid4()),
            symbol=symbol,
            side=side,
            entry_price=current_price,
            current_price=current_price,
            quantity=quantity,
            timestamp=datetime.datetime.now()
        )
        
        session.positions.append(position)
        session.virtual_balance -= position_value
        
        # Update performance metrics
        session.performance_metrics["total_trades"] += 1
        session.last_updated = datetime.datetime.now()
        
        return {
            "success": True,
            "position": asdict(position),
            "remaining_balance": session.virtual_balance,
            "message": "Trade muvaffaqiyatli bajarildi!"
        }

    def update_demo_positions(self, user_id: str) -> Dict[str, Any]:
        """Demo pozitsiyalarni yangilash (simulyatsiya)"""
        session = self.demo_sessions.get(user_id)
        if not session:
            return {"error": "Demo session topilmadi"}
        
        total_pnl = 0.0
        
        for position in session.positions:
            # Simulate price changes
            price_change = random.uniform(-0.02, 0.02)  # ±2% change
            new_price = position.current_price * (1 + price_change)
            position.current_price = new_price
            
            # Calculate PnL
            if position.side == "long":
                position.pnl = (new_price - position.entry_price) * position.quantity
            else:
                position.pnl = (position.entry_price - new_price) * position.quantity
            
            total_pnl += position.pnl
        
        # Update session metrics
        session.performance_metrics["total_pnl"] = total_pnl
        if session.performance_metrics["total_trades"] > 0:
            winning_trades = sum(1 for p in session.positions if p.pnl > 0)
            session.performance_metrics["winning_trades"] = winning_trades
            session.performance_metrics["losing_trades"] = len(session.positions) - winning_trades
            session.performance_metrics["win_rate"] = (winning_trades / len(session.positions)) * 100
        
        session.last_updated = datetime.datetime.now()
        
        return {
            "positions": [asdict(p) for p in session.positions],
            "total_pnl": total_pnl,
            "performance_metrics": session.performance_metrics
        }

    def get_ai_assistant_response(self, user_id: str, message: str) -> Dict[str, Any]:
        """AI Assistant javobini olish"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return {"error": "Foydalanuvchi topilmadi"}
        
        lang = profile.preferred_language
        responses = self.ai_responses[lang]
        
        # Simple keyword-based responses
        message_lower = message.lower()
        
        if any(greeting in message_lower for greeting in ["hello", "hi", "assalom", "salom"]):
            response = responses["greeting"]
        elif "tutorial" in message_lower or "tutorial" in message_lower:
            response = responses["tutorial_help"]
        elif "demo" in message_lower:
            response = responses["demo_help"]
        elif "strategy" in message_lower or "strategiya" in message_lower:
            response = responses["strategy_help"]
        else:
            # Default response based on user's current step
            if profile.current_step == OnboardingStep.DEMO_TRADING:
                response = "Demo tradingda yordam kerakmi? Pozitsiyalarni kuzatib boring!"
            elif profile.current_step == OnboardingStep.AI_ASSISTANT:
                response = "Savollaringizni bering, men sizga yordam beraman!"
            else:
                response = "Onboarding jarayonida yordam kerakmi?"
        
        return {
            "response": response,
            "timestamp": datetime.datetime.now().isoformat(),
            "context": profile.current_step.value
        }

    def get_personalized_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Shaxsiy tavsiyalar olish"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return {"error": "Foydalanuvchi topilmadi"}
        
        lang = profile.preferred_language
        
        # Based on skill level
        if profile.skill_level == UserLevel.BEGINNER:
            recommendations = {
                "strategies": ["Trend Following", "Support/Resistance", "Moving Averages"],
                "markets": ["EURUSD", "GBPUSD", "XAUUSD"],
                "risk_level": "Low to Medium",
                "learning_path": "Basic trading concepts"
            }
        elif profile.skill_level == UserLevel.INTERMEDIATE:
            recommendations = {
                "strategies": ["Price Action", "Fibonacci", "Chart Patterns"],
                "markets": ["EURUSD", "GBPUSD", "XAUUSD", "XAGUSD"],
                "risk_level": "Medium",
                "learning_path": "Advanced technical analysis"
            }
        else:
            recommendations = {
                "strategies": ["Algorithmic Trading", "Multi-timeframe", "Portfolio Management"],
                "markets": ["All available markets"],
                "risk_level": "Medium to High",
                "learning_path": "Professional trading strategies"
            }
        
        return {
            "recommendations": recommendations,
            "user_level": profile.skill_level.value,
            "message": "Sizga mos tavsiyalar tayyorlandi!"
        }

    def complete_onboarding_step(self, user_id: str, current_step: OnboardingStep) -> Dict[str, Any]:
        """Onboarding qadamini yakunlash"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return {"error": "Foydalanuvchi topilmadi"}
        
        step_order = [
            OnboardingStep.REGISTRATION,
            OnboardingStep.SKILL_ASSESSMENT,
            OnboardingStep.WELCOME_TOUR,
            OnboardingStep.DEMO_TRADING,
            OnboardingStep.AI_ASSISTANT,
            OnboardingStep.PERSONAL_RECOMMENDATIONS,
            OnboardingStep.COMMUNITY,
            OnboardingStep.LIVE_TRADING_PREP
        ]
        
        # Ensure current step matches profile
        if profile.current_step != current_step:
            # Auto-update if there's a mismatch
            pass
        
        # Find current step index
        try:
            current_index = step_order.index(profile.current_step)
        except ValueError:
            current_index = 0
        
        # Move to next step
        next_index = min(current_index + 1, len(step_order) - 1)
        next_step = step_order[next_index]
        
        # Update profile
        profile.current_step = next_step
        profile.progress_percentage = ((next_index + 1) / len(step_order)) * 100
        profile.updated_at = datetime.datetime.now()
        
        if next_index == len(step_order) - 1:
            profile.onboarding_completed = True
        
        return {
            "completed_step": current_step.value,
            "current_step": profile.current_step.value,
            "progress_percentage": profile.progress_percentage,
            "onboarding_completed": profile.onboarding_completed,
            "message": f"{current_step.value} qadami yakunlandi! Keyingi: {profile.current_step.value}"
        }

    def get_onboarding_status(self, user_id: str) -> Dict[str, Any]:
        """Onboarding holatini olish"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return {"error": "Foydalanuvchi topilmadi"}
        
        session = self.demo_sessions.get(user_id)
        
        return {
            "user_id": user_id,
            "current_step": profile.current_step.value,
            "progress_percentage": profile.progress_percentage,
            "onboarding_completed": profile.onboarding_completed,
            "skill_level": profile.skill_level.value,
            "demo_balance": session.virtual_balance if session else 0,
            "total_trades": session.performance_metrics["total_trades"] if session else 0,
            "last_updated": profile.updated_at.isoformat()
        }

    def get_gamification_data(self, user_id: str) -> Dict[str, Any]:
        """Gamification ma'lumotlari"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return {"error": "Foydalanuvchi topilmadi"}
        
        session = self.demo_sessions.get(user_id)
        
        # Calculate badges/achievements
        badges = []
        if profile.progress_percentage >= 25:
            badges.append("First Steps")
        if profile.progress_percentage >= 50:
            badges.append("Halfway There")
        if profile.progress_percentage >= 75:
            badges.append("Almost Ready")
        if profile.progress_percentage >= 100:
            badges.append("Onboarding Complete")
        
        if session and session.performance_metrics["total_trades"] >= 5:
            badges.append("Active Trader")
        if session and session.performance_metrics.get("win_rate", 0) >= 60:
            badges.append("Winning Streak")
        
        return {
            "badges": badges,
            "points": int(profile.progress_percentage * 10),
            "level": f"Level {int(profile.progress_percentage // 25) + 1}",
            "achievements": badges
        }

    def close_demo_position(self, user_id: str, position_id: str) -> Dict[str, Any]:
        """Demo pozitsiyani yopish"""
        session = self.demo_sessions.get(user_id)
        if not session:
            return {"error": "Demo session topilmadi"}
        
        position = next((p for p in session.positions if p.id == position_id), None)
        if not position:
            return {"error": "Pozitsiya topilmadi"}
        
        # Calculate final PnL
        final_pnl = position.pnl
        
        # Add PnL to balance
        session.virtual_balance += position.current_price * position.quantity + final_pnl
        
        # Remove position
        session.positions.remove(position)
        
        # Update metrics
        session.last_updated = datetime.datetime.now()
        
        return {
            "success": True,
            "final_pnl": final_pnl,
            "remaining_balance": session.virtual_balance,
            "message": f"Pozitsiya yopildi! PnL: ${final_pnl:.2f}"
        }

# Demo usage
def demo_onboarding_engine():
    """Onboarding engine demo"""
    engine = OnboardingEngine()
    
    print("=== Orion Starline Onboarding System Demo ===\n")
    
    # 1. Create user profile
    user = engine.create_user_profile("Aziz Ahmed", "aziz@example.com", Language.UZBEK)
    print(f"1. Foydalanuvchi profili yaratildi: {user.name}")
    print(f"   User ID: {user.user_id}")
    print(f"   Hozirgi qadam: {user.current_step.value}")
    print()
    
    # 2. Welcome content
    welcome = engine.get_welcome_content(user.user_id)
    print("2. Welcome kontenti:")
    print(f"   {welcome['title']}")
    print(f"   Progress: {welcome['progress_percentage']}%")
    print()
    
    # 3. Skill assessment
    answers = [
        {"question_id": 1, "selected_option": 2},  # 1-2 years experience
        {"question_id": 2, "selected_option": 1},  # Forex
        {"question_id": 3, "selected_option": 1}   # Low risk
    ]
    assessment = engine.conduct_skill_assessment(user.user_id, answers)
    print("3. Skill assessment natijasi:")
    print(f"   {assessment['message']}")
    print()
    
    # 4. Start demo trading
    demo_session = engine.start_demo_trading(user.user_id)
    print("4. Demo trading boshladi:")
    print(f"   Virtual balans: ${demo_session.virtual_balance:,.2f}")
    print()
    
    # 5. Execute some demo trades
    trade1 = engine.execute_demo_trade(user.user_id, "EURUSD", "long", 1000)
    print(f"5. Trade 1 natijasi: {trade1.get('message', trade1.get('error'))}")
    
    trade2 = engine.execute_demo_trade(user.user_id, "XAUUSD", "long", 10)
    print(f"   Trade 2 natijasi: {trade2.get('message', trade2.get('error'))}")
    print()
    
    # 6. Update positions
    updated = engine.update_demo_positions(user.user_id)
    print("6. Pozitsiyalar yangilandi:")
    print(f"   Umumiy PnL: ${updated['total_pnl']:.2f}")
    print(f"   G'olib trade'lar: {updated['performance_metrics']['winning_trades']}")
    print()
    
    # 7. AI Assistant interaction
    ai_response = engine.get_ai_assistant_response(user.user_id, "Demo trading yordam kerak")
    print("7. AI Assistant javobi:")
    print(f"   {ai_response['response']}")
    print()
    
    # 8. Personalized recommendations
    recommendations = engine.get_personalized_recommendations(user.user_id)
    print("8. Shaxsiy tavsiyalar:")
    print(f"   Strategiyalar: {', '.join(recommendations['recommendations']['strategies'])}")
    print(f"   Bozorlar: {', '.join(recommendations['recommendations']['markets'])}")
    print()
    
    # 9. Complete onboarding step
    completed = engine.complete_onboarding_step(user.user_id, OnboardingStep.DEMO_TRADING)
    print("9. Onboarding qadam yakunlandi:")
    print(f"   {completed['message']}")
    print(f"   Progress: {completed['progress_percentage']:.1f}%")
    print()
    
    # 10. Final status
    status = engine.get_onboarding_status(user.user_id)
    print("10. Yakuniy holat:")
    print(f"   Joriy qadam: {status['current_step']}")
    print(f"   Progress: {status['progress_percentage']:.1f}%")
    print(f"   Demo balans: ${status['demo_balance']:,.2f}")
    print(f"   Trade'lar soni: {status['total_trades']}")
    print()
    
    # 11. Gamification
    gamification = engine.get_gamification_data(user.user_id)
    print("11. Gamification:")
    print(f"   Daraja: {gamification['level']}")
    print(f"   Ballar: {gamification['points']}")
    print(f"   Badge'lar: {', '.join(gamification['badges'])}")
    
    return engine

if __name__ == "__main__":
    demo_onboarding_engine()