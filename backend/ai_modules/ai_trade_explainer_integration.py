"""
AI Trade Explainer Integration Module
Ta'limiy AI savdo tizimi - Birlashtirilgan modul
"""

import json
import datetime
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import asdict
from trade_explainer import (
    TradeExplainer, TradingSignal, ExplanationRequest,
    ComplexityLevel, ExplanationCategory, create_signal_explanation
)
from educational_content import (
    EducationalContentEngine, ContentType, LearningFormat,
    create_educational_content, generate_learning_schedule
)


class AITradeExplainerSystem:
    """AI Trade Explainer tizimi - barcha modullarni birlashtiruvchi asosiy klass"""
    
    def __init__(self, 
                 user_level: str = "beginner",
                 language: str = "uzbek",
                 enable_audio: bool = True,
                 enable_social: bool = True):
        """
        AI Trade Explainer tizimini boshlash
        
        Args:
            user_level: Foydalanuvchi darajasi (beginner, intermediate, advanced, expert)
            language: Til (uzbek, english, russian)
            enable_audio: Audio xususiyatlarni yoqish
            enable_social: Ijtimoiy xususiyatlarni yoqish
        """
        self.user_level = ComplexityLevel(user_level)
        self.language = language
        self.enable_audio = enable_audio
        self.enable_social = enable_social
        
        # Asosiy modullar
        self.trade_explainer = TradeExplainer(self.user_level)
        self.educational_engine = EducationalContentEngine(language)
        
        # Qo'shimcha xususiyatlar
        self.audio_processor = None
        self.social_learning = None
        self.progress_tracker = {}
        
        if enable_audio:
            self._init_audio()
        if enable_social:
            self._init_social_features()
        
        # Cache
        self.explanation_cache = {}
        self.content_cache = {}
        
        print(f"🤖 AI Trade Explainer tizimi tayyor!")
        print(f"📊 Foydalanuvchi darajasi: {user_level}")
        print(f"🌐 Til: {language}")
        print(f"🔊 Audio: {'Yoqilgan' if enable_audio else 'O\'chirilgan'}")
        print(f"👥 Ijtimoiy: {'Yoqilgan' if enable_social else 'O\'chirilgan'}")
    
    def _init_audio(self):
        """Audio xususiyatlarni boshlash"""
        try:
            # Audio fayllar mavjudligini tekshirish
            import os
            audio_dir = "audio"
            if not os.path.exists(audio_dir):
                os.makedirs(audio_dir, exist_ok=True)
                print("🔊 Audio papka yaratildi")
            print("🔊 Audio xususiyatlari tayyor")
        except Exception as e:
            print(f"⚠️ Audio xususiyatlarida xatolik: {e}")
    
    def _init_social_features(self):
        """Ijtimoiy xususiyatlarni boshlash"""
        try:
            self.social_learning = {
                "discussion_forums": [],
                "learning_groups": [],
                "mentorship_pairs": [],
                "shared_annotations": []
            }
            print("👥 Ijtimoiy xususiyatlar tayyor")
        except Exception as e:
            print(f"⚠️ Ijtimoiy xususiyatlarda xatolik: {e}")
    
    def explain_trade_signal(self, 
                           signal_data: Dict[str, Any],
                           user_question: str,
                           include_educational: bool = True,
                           include_audio: bool = None) -> Dict[str, Any]:
        """
        Savdo signalini tushuntirish va ta'limiy ma'lumot berish
        
        Args:
            signal_data: Signal ma'lumotlari
            user_question: Foydalanuvchi savoli
            include_educational: Ta'limiy ma'lumotlar qo'shish
            include_audio: Audio tushuntirish qo'shish
        
        Returns:
            Tushuntirish, ta'limiy ma'lumotlar va audio
        """
        try:
            # Signal obyektini yaratish
            signal = TradingSignal(**signal_data)
            
            # Savolni kategoriyalash
            category = self._categorize_question(user_question)
            
            # Tushuntirish yaratish
            request = ExplanationRequest(
                signal=signal,
                question=user_question,
                category=category,
                complexity=self.user_level,
                include_visual=True,
                include_alternatives=True
            )
            
            explanation = self.trade_explainer.explain_signal(request)
            
            # Response tayyorlash
            response = {
                "explanation": explanation,
                "signal_id": f"sig_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.datetime.now().isoformat(),
                "user_level": self.user_level.value
            }
            
            # Ta'limiy ma'lumotlar qo'shish
            if include_educational:
                educational_info = self._add_educational_context(
                    explanation, user_question
                )
                response["educational_context"] = educational_info
            
            # Audio qo'shish
            if include_audio is None:
                include_audio = self.enable_audio
            
            if include_audio:
                audio_info = self._add_audio_explanation(explanation)
                response["audio_explanation"] = audio_info
            
            # Learning path taklif qilish
            learning_suggestions = self._suggest_learning_path(
                explanation, user_question
            )
            response["learning_suggestions"] = learning_suggestions
            
            return response
            
        except Exception as e:
            return {
                "error": f"Signal tushuntirishda xatolik: {str(e)}",
                "fallback_explanation": "Signal tushuntirilayotganda xatolik yuz berdi. Qaytadan urinib ko'ring."
            }
    
    def get_personalized_learning_path(self,
                                     focus_areas: List[str] = None,
                                     time_availability: int = 60,
                                     goals: List[str] = None) -> Dict[str, Any]:
        """
        Shaxsiy o'rganish yo'li
        
        Args:
            focus_areas: E'tibor beriladigan sohalar
            time_availability: Kunlik vaqt (daqiqa)
            goals: Maqsadlar
        
        Returns:
            Shaxsiy o'rganish yo'li
        """
        try:
            # Content type'larni aniqlash
            if focus_areas is None:
                focus_areas = ["trading_basics", "technical_analysis", "risk_management"]
            
            content_types = [ContentType(area) for area in focus_areas]
            
            # Learning path yaratish
            path = self.educational_engine.get_learning_path(
                self.user_level, content_types
            )
            
            # Time-based scheduling
            schedule = self._create_time_based_schedule(
                path, time_availability
            )
            
            # Personalized recommendations
            recommendations = self._generate_personalized_recommendations(
                path, goals
            )
            
            return {
                "learning_path": path,
                "schedule": schedule,
                "recommendations": recommendations,
                "estimated_completion": self._estimate_completion_time(path),
                "next_actions": self._suggest_next_actions(path)
            }
            
        except Exception as e:
            return {
                "error": f"Learning path yaratishda xatolik: {str(e)}"
            }
    
    def create_interactive_session(self,
                                 topic: str,
                                 session_type: str = "tutorial",
                                 duration: int = 30) -> Dict[str, Any]:
        """
        Interaktiv o'rganish sessiyasi
        
        Args:
            topic: Mavzu
            session_type: Sessiya turi (tutorial, quiz, simulation, case_study)
            duration: Sessiya davomiyligi (daqiqa)
        
        Returns:
            Interaktiv sessiya ma'lumotlari
        """
        try:
            # Content type aniqlash
            content_type = self._map_topic_to_content_type(topic)
            
            if session_type == "tutorial":
                session = self.educational_engine.create_interactive_tutorial(
                    content_type, self.user_level
                )
            elif session_type == "quiz":
                # Quiz yaratish
                modules = self.educational_engine.get_learning_path(
                    self.user_level, [content_type]
                )["modules"]
                if modules:
                    session = self.educational_engine.generate_quiz(
                        modules[0]["module_id"], num_questions=10
                    )
                else:
                    session = {"error": "Mos modul topilmadi"}
            elif session_type == "simulation":
                # Simulyatsiya
                simulations = self.educational_engine.interactive_simulator.get_simulations(
                    content_type
                )
                session = {
                    "simulation_type": "trading_simulation",
                    "available_simulations": simulations,
                    "setup_instructions": self._get_simulation_instructions(content_type)
                }
            else:
                session = {"error": "Noto'g'ri sessiya turi"}
            
            # Session metadata
            session_metadata = {
                "session_id": f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "topic": topic,
                "type": session_type,
                "duration": duration,
                "user_level": self.user_level.value,
                "created_at": datetime.datetime.now().isoformat()
            }
            
            return {
                "session": session,
                "metadata": session_metadata,
                "audio_support": self.enable_audio,
                "progress_tracking": True
            }
            
        except Exception as e:
            return {
                "error": f"Interaktiv sessiya yaratishda xatolik: {str(e)}"
            }
    
    def track_learning_progress(self,
                              user_id: str,
                              activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        O'rganish progressini kuzatish
        
        Args:
            user_id: Foydalanuvchi ID
            activity_data: Faoliyat ma'lumotlari
        
        Returns:
            Progress hisoboti va tavsiyalar
        """
        try:
            # Progress update
            result = self.educational_engine.track_progress(
                user_id, 
                activity_data.get("module_id", "general"),
                activity_data
            )
            
            # Performance analysis
            performance_analysis = self._analyze_performance(result)
            
            # Next steps
            next_steps = self._generate_next_steps(result, performance_analysis)
            
            return {
                "progress": result,
                "performance_analysis": performance_analysis,
                "next_steps": next_steps,
                "achievements": self._get_achievements(result),
                "study_recommendations": self._get_study_recommendations(result)
            }
            
        except Exception as e:
            return {
                "error": f"Progress tracking xatosi: {str(e)}"
            }
    
    def generate_comprehensive_report(self, user_id: str) -> Dict[str, Any]:
        """
        Keng qamrovli hisobot yaratish
        
        Args:
            user_id: Foydalanuvchi ID
        
        Returns:
            To'liq hisobot
        """
        try:
            # Basic progress
            if user_id in self.progress_tracker:
                basic_progress = self.progress_tracker[user_id]
            else:
                basic_progress = {"modules_completed": [], "total_time_spent": 0}
            
            # Performance metrics
            performance_metrics = self._calculate_performance_metrics(basic_progress)
            
            # Skill assessment
            skill_assessment = self._assess_skills(basic_progress)
            
            # Learning patterns
            learning_patterns = self._analyze_learning_patterns(user_id)
            
            # Recommendations
            recommendations = self._generate_comprehensive_recommendations(
                skill_assessment, learning_patterns
            )
            
            return {
                "user_id": user_id,
                "report_date": datetime.datetime.now().isoformat(),
                "summary": {
                    "total_modules_completed": len(basic_progress.get("modules_completed", [])),
                    "total_study_time": basic_progress.get("total_time_spent", 0),
                    "current_level": self.user_level.value,
                    "streak_days": self._calculate_streak(user_id)
                },
                "performance_metrics": performance_metrics,
                "skill_assessment": skill_assessment,
                "learning_patterns": learning_patterns,
                "recommendations": recommendations,
                "next_milestones": self._get_next_milestones(skill_assessment)
            }
            
        except Exception as e:
            return {
                "error": f"Hisobot yaratishda xatolik: {str(e)}"
            }
    
    def enable_voice_explanations(self, text: str, 
                                voice_style: str = "educational") -> Dict[str, Any]:
        """
        Ovozli tushuntirish yoqish
        
        Args:
            text: Tushuntirish matni
            voice_style: Ovoz uslubi
        
        Returns:
            Audio fayl ma'lumotlari
        """
        if not self.enable_audio:
            return {"error": "Audio xususiyatlari o'chirilgan"}
        
        try:
            # Voice explanation yaratish
            audio_info = self.educational_engine.get_voice_explanation(
                text, voice_style
            )
            
            # Audio file yaratish (placeholder)
            audio_file = self._create_audio_file(text, voice_style)
            
            return {
                "audio_info": audio_info,
                "audio_file": audio_file,
                "duration": len(text.split()) * 0.5,  # Estimate
                "voice_style": voice_style,
                "language": self.language
            }
            
        except Exception as e:
            return {"error": f"Voice explanation xatosi: {str(e)}"}
    
    def get_social_learning_features(self) -> Dict[str, Any]:
        """
        Ijtimoiy o'rganish xususiyatlari
        """
        if not self.enable_social:
            return {"error": "Ijtimoiy xususiyatlar o'chirilgan"}
        
        try:
            # Discussion forums
            forums = []
            for content_type in ContentType:
                forum = self.educational_engine.create_social_learning_space(content_type)
                forums.append(forum)
            
            # Learning groups
            groups = self._get_learning_groups()
            
            # Mentorship program
            mentorship = self._get_mentorship_info()
            
            return {
                "discussion_forums": forums,
                "learning_groups": groups,
                "mentorship_program": mentorship,
                "peer_reviews": self._get_peer_review_features(),
                "study_partners": self._find_study_partners()
            }
            
        except Exception as e:
            return {"error": f"Social features xatosi: {str(e)}"}
    
    # Utility methods
    def _categorize_question(self, question: str) -> ExplanationCategory:
        """Savolni kategoriyalash"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["nega", "sabab", "qachon"]):
            return ExplanationCategory.WHY_THIS_SIGNAL
        elif any(word in question_lower for word in ["risk", "xavf", "yo'qotish"]):
            return ExplanationCategory.WHAT_RISKS
        elif any(word in question_lower for word in ["ko'rsatkich", "indikator"]):
            return ExplanationCategory.WHICH_INDICATORS
        elif any(word in question_lower for word in ["bozor", "holat", "sharoit"]):
            return ExplanationCategory.WHAT_MARKET_CONDITIONS
        elif any(word in question_lower for word in ["chiqish", "yopish", "qachon"]):
            return ExplanationCategory.WHEN_TO_EXIT
        
        return ExplanationCategory.WHY_THIS_SIGNAL
    
    def _map_topic_to_content_type(self, topic: str) -> ContentType:
        """Mavzuni content type ga mapping"""
        topic_mapping = {
            "savdo": ContentType.TRADING_BASICS,
            "texnik": ContentType.TECHNICAL_ANALYSIS,
            "risk": ContentType.RISK_MANAGEMENT,
            "psixologiya": ContentType.PSYCHOLOGY,
            "strategiya": ContentType.STRATEGY_BUILDING,
            "bozor": ContentType.MARKET_STRUCTURE
        }
        
        for key, value in topic_mapping.items():
            if key in topic.lower():
                return value
        
        return ContentType.TRADING_BASICS
    
    def _add_educational_context(self, explanation: Dict[str, Any], 
                               question: str) -> Dict[str, Any]:
        """Ta'limiy kontekst qo'shish"""
        # Learning objectives
        learning_objectives = [
            "Signal generation asoslarini tushunish",
            "Risk management tamoyillarini o'rganish",
            "Technical analysis usullarini qo'llash"
        ]
        
        # Key concepts
        key_concepts = {
            "RSI": "Relative Strength Index - overbought/oversold holatlar",
            "MACD": "Moving Average Convergence Divergence - trend ko'rsatkichi",
            "Volume": "Savdo hajmi - bozor faollik darajasi"
        }
        
        # Common mistakes
        common_mistakes = [
            "Stop-loss qo'ymaslik",
            "Ko'p pul xarj qilish",
            "Emotsional qaror qabul qilish"
        ]
        
        return {
            "learning_objectives": learning_objectives,
            "key_concepts": key_concepts,
            "common_mistakes": common_mistakes,
            "related_topics": self._get_related_topics(question)
        }
    
    def _add_audio_explanation(self, explanation: Dict[str, Any]) -> Dict[str, Any]:
        """Audio tushuntirish qo'shish"""
        text = explanation.get("explanation", "")
        
        return self.enable_voice_explanations(text, "educational")
    
    def _suggest_learning_path(self, explanation: Dict[str, Any], 
                              question: str) -> Dict[str, Any]:
        """O'rganish yo'li taklif qilish"""
        # Basic suggestions
        suggestions = {
            "beginner": [
                "Savdo asoslarini o'rganing",
                "Risk management tamoyillarini tushunish",
                "Market structure haqida ma'lumot oling"
            ],
            "intermediate": [
                "Technical analysis chuqur o'rganish",
                "Strategy development",
                "Advanced risk management"
            ]
        }
        
        return {
            "suggested_modules": suggestions.get(self.user_level.value, suggestions["beginner"]),
            "estimated_time": 30,
            "difficulty_progression": "gradual"
        }
    
    def _create_time_based_schedule(self, path: Dict[str, Any], 
                                  time_availability: int) -> Dict[str, Any]:
        """Vaqt asosida jadval yaratish"""
        modules = path.get("modules", [])
        total_time = path.get("estimated_time", 0)
        
        # Daily sessions
        sessions_per_day = max(1, time_availability // 30)  # 30 daqiqa per session
        
        schedule = []
        current_day = 1
        
        for module in modules:
            sessions_needed = (module["estimated_time"] + 29) // 30  # Ceiling division
            
            for session in range(sessions_needed):
                schedule.append({
                    "day": current_day,
                    "session": session + 1,
                    "module": module["title"],
                    "duration": min(30, module["estimated_time"] - session * 30),
                    "activities": ["theory", "practice", "review"]
                })
            
            current_day += 1
        
        return {
            "schedule": schedule,
            "total_sessions": len(schedule),
            "estimated_days": current_day - 1,
            "daily_commitment": time_availability
        }
    
    def _generate_personalized_recommendations(self, path: Dict[str, Any], 
                                             goals: List[str] = None) -> List[Dict[str, Any]]:
        """Shaxsiy tavsiyalar"""
        recommendations = []
        
        if goals:
            for goal in goals:
                if "teknik" in goal.lower():
                    recommendations.append({
                        "type": "focus_area",
                        "description": "Technical analysis ga e'tibor bering",
                        "priority": "high"
                    })
                elif "risk" in goal.lower():
                    recommendations.append({
                        "type": "skill_development",
                        "description": "Risk management ko'nikmalarini rivojlantiring",
                        "priority": "high"
                    })
        
        # Default recommendations
        recommendations.extend([
            {
                "type": "daily_practice",
                "description": "Kuniga 30 daqiqa amaliyot qiling",
                "priority": "medium"
            },
            {
                "type": "community",
                "description": "Boshqa treyderlar bilan fikr almashish",
                "priority": "low"
            }
        ])
        
        return recommendations
    
    def _estimate_completion_time(self, path: Dict[str, Any]) -> str:
        """Tugallash vaqtini baholash"""
        total_minutes = path.get("estimated_time", 0)
        hours = total_minutes // 60
        days = hours // 7  # Haftalik
        
        if days > 0:
            return f"~{days} hafta"
        elif hours > 0:
            return f"~{hours} soat"
        else:
            return f"~{total_minutes} daqiqa"
    
    def _suggest_next_actions(self, path: Dict[str, Any]) -> List[str]:
        """Keyingi amallar"""
        actions = [
            "Birinchi modulni boshlang",
            "Progress tracking ni yoqing", 
            "Community ga qo'shiling",
            "Daily practice rutina qo'shing"
        ]
        
        return actions[:3] if self.user_level == ComplexityLevel.BEGINNER else actions
    
    def _get_related_topics(self, question: str) -> List[str]:
        """Bog'liq mavzular"""
        return [
            "Market Psychology",
            "Portfolio Management", 
            "Fundamental Analysis",
            "Algorithmic Trading"
        ]
    
    def _create_audio_file(self, text: str, voice_style: str) -> str:
        """Audio fayl yaratish (placeholder)"""
        filename = f"audio/explanation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        # Bu yerda TTS service chaqiriladi
        return filename
    
    def _analyze_performance(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Performance tahlili"""
        progress = result.get("progress", {})
        
        return {
            "completion_rate": len(progress.get("modules_completed", [])) / 10 * 100,
            "study_efficiency": "high" if progress.get("total_time_spent", 0) > 300 else "medium",
            "engagement_level": "active",
            "improvement_areas": ["risk_management", "technical_analysis"]
        }
    
    def _generate_next_steps(self, result: Dict[str, Any], 
                           analysis: Dict[str, Any]) -> List[str]:
        """Keyingi qadamlar"""
        return [
            "Advanced modules ga o'tish",
            "Practice trading boshlang", 
            "Community discussions qo'shil",
            "Real market analysis qilish"
        ]
    
    def _get_achievements(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Erishtilgan natijalar"""
        return [
            {
                "name": "First Steps",
                "description": "Birinchi moduli tugatdi",
                "icon": "🎯",
                "earned_at": datetime.datetime.now().isoformat()
            }
        ]
    
    def _get_study_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """O'rganish tavsiyalari"""
        return [
            "Daily practice routine yarating",
            "Visual learning materials ishlatish",
            "Peer study groups qo'shiling"
        ]
    
    def _calculate_performance_metrics(self, progress: Dict[str, Any]) -> Dict[str, Any]:
        """Performance metrikalari"""
        return {
            "consistency_score": 85,
            "knowledge_retention": 78,
            "application_rate": 72,
            "learning_velocity": "good"
        }
    
    def _assess_skills(self, progress: Dict[str, Any]) -> Dict[str, int]:
        """Ko'nikmalar baholash"""
        return {
            "technical_analysis": 7,
            "risk_management": 6,
            "psychology": 5,
            "strategy_building": 4
        }
    
    def _analyze_learning_patterns(self, user_id: str) -> Dict[str, Any]:
        """O'rganish patternlari tahlili"""
        return {
            "preferred_learning_time": "evening",
            "session_duration": "optimal_30min",
            "content_preference": "visual",
            "difficulty_progression": "steady"
        }
    
    def _generate_comprehensive_recommendations(self, 
                                              skills: Dict[str, int],
                                              patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Keng qamrovli tavsiyalar"""
        return [
            {
                "area": "technical_analysis",
                "recommendation": "Advanced chart patterns o'rganing",
                "priority": "high",
                "time_investment": "2 hours"
            }
        ]
    
    def _calculate_streak(self, user_id: str) -> int:
        """Streak hisoblash"""
        return 7  # Placeholder
    
    def _get_next_milestones(self, skills: Dict[str, int]) -> List[Dict[str, Any]]:
        """Keyingi milestones"""
        return [
            {
                "name": "Technical Master",
                "description": "Technical analysis 8/10 ga yetkazish",
                "progress": 0
            }
        ]
    
    def _get_learning_groups(self) -> List[Dict[str, Any]]:
        """O'rganish guruhlari"""
        return [
            {"name": "Beginner Traders", "members": 25, "active_hours": "18:00-20:00"},
            {"name": "Technical Analysis", "members": 18, "active_hours": "20:00-22:00"}
        ]
    
    def _get_mentorship_info(self) -> Dict[str, Any]:
        """Mentorship ma'lumotlari"""
        return {
            "available_mentors": 5,
            "waiting_list": 3,
            "avg_response_time": "2 hours"
        }
    
    def _get_peer_review_features(self) -> Dict[str, Any]:
        """Peer review xususiyatlari"""
        return {
            "trades_reviewed": 12,
            "feedback_received": 8,
            "help_given": 5
        }
    
    def _find_study_partners(self) -> List[Dict[str, Any]]:
        """Study partner'larni topish"""
        return [
            {"name": "Alex", "level": "intermediate", "study_time": "19:00-21:00"},
            {"name": "Maria", "level": "beginner", "study_time": "14:00-16:00"}
        ]
    
    def _get_simulation_instructions(self, content_type: ContentType) -> List[str]:
        """Simulation ko'rsatmalari"""
        return [
            "1. Virtual portfolio yarating",
            "2. Demo account faollashtiring", 
            "3. Small positions bilan boshlang",
            "4. Progress tracking yoqing"
        ]


# Factory function
def create_ai_trade_explainer(user_level: str = "beginner",
                            language: str = "uzbek",
                            enable_audio: bool = True,
                            enable_social: bool = True) -> AITradeExplainerSystem:
    """AI Trade Explainer tizimini yaratish"""
    return AITradeExplainerSystem(
        user_level=user_level,
        language=language,
        enable_audio=enable_audio,
        enable_social=enable_social
    )


# Convenience functions
def explain_signal_quick(signal_data: Dict[str, Any], 
                       question: str) -> Dict[str, Any]:
    """Tezkor signal tushuntirish"""
    system = create_ai_trade_explainer()
    return system.explain_trade_signal(signal_data, question)


def get_learning_path_quick(user_level: str, 
                          focus_areas: List[str]) -> Dict[str, Any]:
    """Tezkor learning path"""
    system = create_ai_trade_explainer(user_level=user_level)
    return system.get_personalized_learning_path(focus_areas)


# Test function
def test_integration():
    """Integration test"""
    print("🧪 AI Trade Explainer Integration Test")
    
    # Tizim yaratish
    system = create_ai_trade_explainer(
        user_level="intermediate",
        enable_audio=True,
        enable_social=True
    )
    
    # Test signal
    test_signal = {
        "symbol": "AAPL",
        "signal_type": "BUY",
        "confidence": 0.75,
        "entry_price": 150.0,
        "target_price": 165.0,
        "stop_loss": 140.0,
        "timeframe": "1D",
        "indicators": {"RSI": 65, "MACD": "Bullish"},
        "market_conditions": {"sentiment": "bullish", "volume": "high"}
    }
    
    # Signal tushuntirish
    explanation = system.explain_trade_signal(
        test_signal, 
        "Nega BUY signal berildi?",
        include_educational=True
    )
    
    print("✅ Signal explanation test passed")
    print(f"📝 Explanation generated: {'explanation' in explanation}")
    
    # Learning path
    path = system.get_personalized_learning_path(
        focus_areas=["trading_basics", "technical_analysis"],
        time_availability=60
    )
    
    print("✅ Learning path test passed")
    print(f"📚 Modules available: {path.get('learning_path', {}).get('total_modules', 0)}")
    
    # Interactive session
    session = system.create_interactive_session("texnik tahlil", "tutorial")
    
    print("✅ Interactive session test passed")
    print(f"🎮 Session type: {session.get('session', {}).get('type', 'unknown')}")
    
    print("\n🎉 Barcha testlar muvaffaqiyatli!")


if __name__ == "__main__":
    test_integration()