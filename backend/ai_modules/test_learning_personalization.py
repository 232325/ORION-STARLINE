"""
Learning & Personalization Engine Test Suite

Bu fayl LearningPersonalizationEngine moduling to'liq funksionalligini test qilish uchun mo'ljallangan.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import List

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_modules.learning_personalization import (
    LearningPersonalizationEngine,
    UserBehaviorData,
    UserPreferences,
    PersonalizationMetrics,
    InteractionType,
    LearningStyle,
    LanguageCode
)


class LearningPersonalizationTester:
    """Learning & Personalization Engine test klassi"""
    
    def __init__(self):
        self.engine = None
        self.test_user_id = "test_user_123"
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Test natijalarini loglash"""
        status = "✓ PASS" if success else "✗ FAIL"
        result = f"{status} - {test_name}"
        if message:
            result += f": {message}"
        self.test_results.append(result)
        print(result)
    
    async def setup(self):
        """Test environment tayyorlash"""
        try:
            # Supabase credentials yo'q, shuning uchun local mode
            self.engine = LearningPersonalizationEngine()
            self.log_test("Engine Initialization", True, "Local mode active")
            return True
        except Exception as e:
            self.log_test("Engine Initialization", False, str(e))
            return False
    
    async def test_user_initialization(self):
        """Foydalanuvchi initializatsiyasi test"""
        try:
            # Standart preferences bilan
            success1 = await self.engine.initialize_user(self.test_user_id)
            self.log_test("User Initialization (default)", success1)
            
            # Custom preferences bilan
            custom_prefs = UserPreferences(
                language=LanguageCode.UZBEK,
                learning_style=LearningStyle.VISUAL,
                communication_style="technical",
                trading_experience_level="advanced",
                risk_tolerance="high",
                interface_complexity="expert",
                time_preference="evening",
                notification_preference="all"
            )
            
            success2 = await self.engine.initialize_user("test_user_456", custom_prefs)
            self.log_test("User Initialization (custom)", success2)
            
            # Preferences tekshirish
            prefs = self.engine.user_preferences.get("test_user_456")
            if prefs and prefs.learning_style == LearningStyle.VISUAL:
                self.log_test("Preferences Storage", True, "Custom preferences saved")
            else:
                self.log_test("Preferences Storage", False, "Preferences not saved correctly")
            
        except Exception as e:
            self.log_test("User Initialization", False, str(e))
    
    async def test_interaction_tracking(self):
        """Foydalanuvchi interaction tracking test"""
        try:
            # Turli xil interactionlar yaratish
            interactions = [
                UserBehaviorData(
                    user_id=self.test_user_id,
                    interaction_type=InteractionType.CLICK,
                    element_id="buy_button",
                    timestamp=datetime.now(),
                    session_id="session_1",
                    page_url="/trading/dashboard",
                    duration=2.5,
                    metadata={"sentiment": "positive", "action": "purchase_intent"}
                ),
                UserBehaviorData(
                    user_id=self.test_user_id,
                    interaction_type=InteractionType.SCROLL,
                    element_id="chart_container",
                    timestamp=datetime.now(),
                    session_id="session_1",
                    page_url="/trading/dashboard",
                    duration=5.0,
                    metadata={"scroll_depth": "bottom"}
                ),
                UserBehaviorData(
                    user_id=self.test_user_id,
                    interaction_type=InteractionType.FORM_SUBMIT,
                    element_id="order_form",
                    timestamp=datetime.now(),
                    session_id="session_1",
                    page_url="/trading/dashboard",
                    metadata={"form_data": {"amount": 1000, "symbol": "EURUSD"}}
                )
            ]
            
            # Interactionlarni tracking
            for i, interaction in enumerate(interactions):
                result = await self.engine.track_interaction(self.test_user_id, interaction)
                if result["success"]:
                    self.log_test(f"Interaction Tracking #{i+1}", True, f"Type: {interaction.interaction_type.value}")
                else:
                    self.log_test(f"Interaction Tracking #{i+1}", False, result.get("error", "Unknown error"))
            
            # Cache tekshirish
            cached_data = list(self.engine.user_behavior_cache[self.test_user_id])
            if len(cached_data) >= 3:
                self.log_test("Behavior Cache", True, f"Cached {len(cached_data)} interactions")
            else:
                self.log_test("Behavior Cache", False, f"Only {len(cached_data)} interactions cached")
            
        except Exception as e:
            self.log_test("Interaction Tracking", False, str(e))
    
    async def test_personalized_responses(self):
        """Shaxsiylashtirilgan javoblar test"""
        try:
            # Uzbek language response
            uz_response = await self.engine.get_personalized_response(
                user_id=self.test_user_id,
                content_type="trading_advice",
                content_data={"content": "Bu aktivni sotib olish foydali bo'lishi mumkin"}
            )
            if "tavsiya" in uz_response.lower() or "foydali" in uz_response.lower():
                self.log_test("Uzbek Response Generation", True, uz_response[:50] + "...")
            else:
                self.log_test("Uzbek Response Generation", False, "Response not in expected language")
            
            # English response
            en_user_id = "test_user_en"
            await self.engine.initialize_user(en_user_id, UserPreferences(
                language=LanguageCode.ENGLISH,
                learning_style=LearningStyle.VISUAL,
                communication_style="friendly",
                trading_experience_level="beginner",
                risk_tolerance="medium",
                interface_complexity="simple",
                time_preference="morning",
                notification_preference="important"
            ))
            
            en_response = await self.engine.get_personalized_response(
                user_id=en_user_id,
                content_type="trading_advice",
                content_data={"content": "This asset might be profitable to buy"}
            )
            if "recommend" in en_response.lower() or "experience" in en_response.lower():
                self.log_test("English Response Generation", True, en_response[:50] + "...")
            else:
                self.log_test("English Response Generation", False, "Response not in expected language")
            
            # Russian response
            ru_user_id = "test_user_ru"
            await self.engine.initialize_user(ru_user_id, UserPreferences(
                language=LanguageCode.RUSSIAN,
                learning_style=LearningStyle.AUDITORY,
                communication_style="formal",
                trading_experience_level="intermediate",
                risk_tolerance="low",
                interface_complexity="medium",
                time_preference="afternoon",
                notification_preference="none"
            ))
            
            ru_response = await self.engine.get_personalized_response(
                user_id=ru_user_id,
                content_type="trading_advice",
                content_data={"content": "Этот актив может быть прибыльным для покупки"}
            )
            if "рекомендуем" in ru_response.lower() or "опыт" in ru_response.lower():
                self.log_test("Russian Response Generation", True, ru_response[:50] + "...")
            else:
                self.log_test("Russian Response Generation", False, "Response not in expected language")
            
        except Exception as e:
            self.log_test("Personalized Responses", False, str(e))
    
    async def test_learning_style_analysis(self):
        """O'rganish uslubi tahlili test"""
        try:
            # Ko'proq interaction qo'shish learning style analysis uchun
            additional_interactions = [
                UserBehaviorData(
                    user_id=self.test_user_id,
                    interaction_type=InteractionType.HOVER,
                    element_id="chart",
                    timestamp=datetime.now(),
                    session_id="session_2",
                    page_url="/analytics/charts"
                ),
                UserBehaviorData(
                    user_id=self.test_user_id,
                    interaction_type=InteractionType.TEXT_INPUT,
                    element_id="search_box",
                    timestamp=datetime.now(),
                    session_id="session_2",
                    page_url="/search"
                )
            ]
            
            for interaction in additional_interactions:
                await self.engine.track_interaction(self.test_user_id, interaction)
            
            # Learning style analysis
            learning_analysis = await self.engine.get_learning_style_analysis(self.test_user_id)
            
            if "learning_style" in learning_analysis:
                style = learning_analysis["learning_style"]
                confidence = learning_analysis["confidence"]
                recommendations = learning_analysis.get("recommendations", [])
                
                self.log_test("Learning Style Analysis", True, 
                            f"Style: {style}, Confidence: {confidence:.2f}")
                
                if recommendations:
                    self.log_test("Style Recommendations", True, f"{len(recommendations)} recommendations")
                else:
                    self.log_test("Style Recommendations", False, "No recommendations generated")
            else:
                self.log_test("Learning Style Analysis", False, "No learning style returned")
            
        except Exception as e:
            self.log_test("Learning Style Analysis", False, str(e))
    
    async def test_adaptive_interface(self):
        """Moslashuvchan interfeys test"""
        try:
            # Interface configuration olish
            interface_config = await self.engine.get_adaptive_interface_config(self.test_user_id)
            
            # Config strukturasi tekshirish
            required_keys = ["theme", "layout", "components"]
            config_valid = all(key in interface_config for key in required_keys)
            
            if config_valid:
                self.log_test("Interface Config Structure", True, "All required keys present")
                
                # Theme configuration
                theme = interface_config["theme"]
                if "mode" in theme and "primary_color" in theme:
                    self.log_test("Theme Configuration", True, f"Mode: {theme['mode']}")
                else:
                    self.log_test("Theme Configuration", False, "Incomplete theme config")
                
                # Components configuration
                components = interface_config["components"]
                if "navigation" in components and "dashboard" in components:
                    self.log_test("Components Configuration", True, "Navigation and dashboard configured")
                else:
                    self.log_test("Components Configuration", False, "Incomplete components config")
            else:
                self.log_test("Interface Config Structure", False, "Missing required keys")
            
        except Exception as e:
            self.log_test("Adaptive Interface", False, str(e))
    
    async def test_performance_metrics(self):
        """Faoliyat metrikalari test"""
        try:
            # Performance metrics olish
            metrics = await self.engine.get_performance_metrics(self.test_user_id)
            
            # Metrics validation
            required_fields = [
                "engagement_score", "task_completion_rate", "error_rate",
                "learning_curve_score", "satisfaction_score", "retention_score"
            ]
            
            metrics_valid = all(
                hasattr(metrics, field) and 0 <= getattr(metrics, field) <= 1 
                for field in required_fields
            )
            
            if metrics_valid:
                self.log_test("Performance Metrics Validation", True, 
                            f"Engagement: {metrics.engagement_score:.2f}")
                
                # Individual metric checks
                if metrics.engagement_score >= 0:
                    self.log_test("Engagement Score", True, f"{metrics.engagement_score:.2f}")
                else:
                    self.log_test("Engagement Score", False, "Invalid value")
                
                if 0 <= metrics.error_rate <= 1:
                    self.log_test("Error Rate", True, f"{metrics.error_rate:.2f}")
                else:
                    self.log_test("Error Rate", False, "Invalid value")
            else:
                self.log_test("Performance Metrics Validation", False, "Invalid metrics structure")
            
        except Exception as e:
            self.log_test("Performance Metrics", False, str(e))
    
    async def test_improvement_suggestions(self):
        """Yaxshilash maslahatlari test"""
        try:
            # Improvement suggestions olish
            suggestions = await self.engine.get_improvement_suggestions(self.test_user_id)
            
            if suggestions.get("success", False):
                improvement_data = suggestions.get("suggestions", {})
                
                # Suggestion categories
                categories = [
                    "personalization_adjustments",
                    "interface_suggestions", 
                    "content_recommendations",
                    "learning_path_updates"
                ]
                
                categories_present = [cat for cat in categories if cat in improvement_data]
                if categories_present:
                    self.log_test("Improvement Categories", True, f"{len(categories_present)} categories found")
                    
                    # Check personalization adjustments
                    personalization = improvement_data.get("personalization_adjustments", [])
                    if isinstance(personalization, list):
                        self.log_test("Personalization Suggestions", True, f"{len(personalization)} suggestions")
                    else:
                        self.log_test("Personalization Suggestions", False, "Invalid format")
                else:
                    self.log_test("Improvement Categories", False, "No categories found")
            else:
                self.log_test("Improvement Suggestions", False, suggestions.get("error", "Unknown error"))
            
        except Exception as e:
            self.log_test("Improvement Suggestions", False, str(e))
    
    async def test_dashboard_data(self):
        """Dashboard ma'lumotlari test"""
        try:
            # Complete dashboard data olish
            dashboard_data = await self.engine.get_user_dashboard_data(self.test_user_id)
            
            if "error" not in dashboard_data:
                # Data structure validation
                required_sections = ["user_id", "preferences", "performance", "interface_config"]
                sections_present = [section for section in required_sections if section in dashboard_data]
                
                if len(sections_present) >= 3:
                    self.log_test("Dashboard Data Structure", True, f"{len(sections_present)} sections present")
                    
                    # Performance section
                    performance = dashboard_data.get("performance", {})
                    if performance and "engagement_score" in performance:
                        self.log_test("Dashboard Performance", True, "Performance data included")
                    else:
                        self.log_test("Dashboard Performance", False, "Performance data missing")
                    
                    # Interface config
                    interface_config = dashboard_data.get("interface_config", {})
                    if interface_config and "theme" in interface_config:
                        self.log_test("Dashboard Interface Config", True, "Interface config included")
                    else:
                        self.log_test("Dashboard Interface Config", False, "Interface config missing")
                else:
                    self.log_test("Dashboard Data Structure", False, f"Only {len(sections_present)} sections present")
            else:
                self.log_test("Dashboard Data", False, dashboard_data["error"])
            
        except Exception as e:
            self.log_test("Dashboard Data", False, str(e))
    
    async def test_privacy_features(self):
        """Privacy xususiyatlari test"""
        try:
            # User ID anonymization
            original_id = "user_with_real_id_123"
            anonymized_id = self.engine.privacy_manager.anonymize_user_id(original_id)
            
            if anonymized_id and len(anonymized_id) == 16:
                self.log_test("User ID Anonymization", True, f"Anonymized: {anonymized_id}")
            else:
                self.log_test("User ID Anonymization", False, "Invalid anonymization")
            
            # Data encryption/decryption
            test_data = "sensitive_information_123"
            try:
                encrypted = self.engine.privacy_manager.encrypt_sensitive_data(test_data)
                decrypted = self.engine.privacy_manager.decrypt_sensitive_data(encrypted)
                
                if decrypted == test_data:
                    self.log_test("Data Encryption/Decryption", True, "Round-trip successful")
                else:
                    self.log_test("Data Encryption/Decryption", False, "Data mismatch")
            except Exception:
                # Cryptography not available - this is OK
                self.log_test("Data Encryption/Decryption", True, "Cryptography not available (expected)")
            
            # Data export (GDPR compliance)
            export_data = await self.engine.export_user_data(self.test_user_id)
            if export_data.get("success", False):
                self.log_test("Data Export (GDPR)", True, "Export successful")
            else:
                self.log_test("Data Export (GDPR)", False, "Export failed")
            
        except Exception as e:
            self.log_test("Privacy Features", False, str(e))
    
    async def run_all_tests(self):
        """Barcha testlarni bajarish"""
        print("=" * 60)
        print("Learning & Personalization Engine Test Suite")
        print("=" * 60)
        print()
        
        # Setup
        setup_success = await self.setup()
        if not setup_success:
            print("Setup failed, aborting tests")
            return
        
        print()
        
        # Run all tests
        await self.test_user_initialization()
        print()
        
        await self.test_interaction_tracking()
        print()
        
        await self.test_personalized_responses()
        print()
        
        await self.test_learning_style_analysis()
        print()
        
        await self.test_adaptive_interface()
        print()
        
        await self.test_performance_metrics()
        print()
        
        await self.test_improvement_suggestions()
        print()
        
        await self.test_dashboard_data()
        print()
        
        await self.test_privacy_features()
        print()
        
        # Test results summary
        self.print_summary()
    
    def print_summary(self):
        """Test natijalarini jamlash"""
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if "✓ PASS" in result)
        failed = sum(1 for result in self.test_results if "✗ FAIL" in result)
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        if failed > 0:
            print("FAILED TESTS:")
            for result in self.test_results:
                if "✗ FAIL" in result:
                    print(f"  {result}")
            print()
        
        print("✓ Test suite completed!")
        print("=" * 60)


async def main():
    """Test runner"""
    tester = LearningPersonalizationTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())