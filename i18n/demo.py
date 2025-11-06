#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orion Starline Multi-Language System Demo
=========================================

Complete demonstration of the multi-language and localization system
featuring 20+ languages, RTL support, cultural adaptation, and dynamic switching.

Author: Orion Starline Team
Version: 1.0.0
Created: 2025-11-05
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from multilang_system import MultiLanguageSystem
from translations import TranslationManager, TranslationStatus, TranslationType
from localization import LocalizationManager, LocaleFormat


class MultiLanguageDemo:
    """
    Comprehensive demonstration of multi-language and localization system
    """
    
    def __init__(self):
        """Initialize the demo system"""
        print("🌍 Orion Starline Multi-Language System Demo")
        print("=" * 50)
        
        # Initialize systems
        self.mls = MultiLanguageSystem()
        self.tm = TranslationManager()
        self.lm = LocalizationManager()
        
        # Setup demo data
        self.setup_demo_translations()
        self.setup_demo_data()
    
    def setup_demo_translations(self):
        """Setup demonstration translations"""
        print("\n📝 Setting up demo translations...")
        
        # Common UI translations
        translations_to_add = [
            ("welcome_message", "Welcome to Orion Starline", "Xush kelibsiz Orion Starline ga"),
            ("login_button", "Login", "Kirish"),
            ("logout_button", "Logout", "Chiqish"),
            ("dashboard_title", "Trading Dashboard", "Savdo Dashboard"),
            ("balance_title", "Account Balance", "Hisob Balans"),
            ("portfolio_title", "Portfolio", "Portfel"),
            ("settings_title", "Settings", "Sozlamalar"),
            ("language_selector", "Language", "Til"),
            ("currency_selector", "Currency", "Valyuta"),
            ("theme_selector", "Theme", "Mavzu"),
            ("notifications", "Notifications", "Xabarlar"),
            ("help", "Help", "Yordam"),
            ("about", "About", "Haqida"),
            ("contact", "Contact", "Bog'lanish"),
            ("privacy", "Privacy Policy", "Maxfiylik Siyosati"),
            ("terms", "Terms of Service", "Xizmat Shartlari"),
            ("profile", "Profile", "Profil"),
            ("security", "Security", "Xavfsizlik"),
            ("backup", "Backup", "Zahira"),
            ("restore", "Restore", "Tiklash")
        ]
        
        # Add to translation manager
        for key, english, uzbek in translations_to_add:
            # Add translation key
            self.tm.add_translation_key(
                key=key,
                namespace="ui",
                description=f"UI element: {key}",
                translation_type=TranslationType.UI,
                requires_review=True
            )
            
            # Add English translation
            self.tm.update_translation(
                language_code="en",
                key=key,
                value=english,
                status=TranslationStatus.APPROVED,
                translator="Demo System"
            )
            
            # Add Uzbek translation
            self.tm.update_translation(
                language_code="uz",
                key=key,
                value=uzbek,
                status=TranslationStatus.APPROVED,
                translator="Demo System"
            )
        
        print(f"✅ Added {len(translations_to_add)} translations")
    
    def setup_demo_data(self):
        """Setup additional demo data"""
        print("\n📊 Setting up demo data...")
        
        # Set up some additional language settings
        self.mls.set_language("en")
        self.lm.set_locale("en-US")
        
        print("✅ Demo data setup complete")
    
    def demo_basic_translation(self):
        """Demonstrate basic translation functionality"""
        print("\n🌐 Basic Translation Demo")
        print("-" * 30)
        
        # Test different languages
        languages = ["en", "uz", "ar", "zh"]
        
        for lang in languages:
            self.mls.set_language(lang)
            print(f"\n📍 Language: {lang.upper()}")
            
            # Get welcome message
            welcome = self.mls.translate("welcome_message")
            print(f"   Welcome: {welcome}")
            
            # Get login button
            login = self.mls.translate("login_button")
            print(f"   Login Button: {login}")
            
            # Check if RTL
            is_rtl = self.mls.is_rtl()
            print(f"   RTL Support: {'✅' if is_rtl else '❌'}")
    
    def demo_cultural_adaptation(self):
        """Demonstrate cultural adaptation"""
        print("\n🎭 Cultural Adaptation Demo")
        print("-" * 30)
        
        # Set to US locale
        self.lm.set_locale("en-US")
        print("🇺🇸 United States:")
        
        # Format currency
        usd_amount = 1234.56
        formatted_currency = self.lm.format_currency(usd_amount)
        print(f"   Currency: {formatted_currency}")
        
        # Format date
        now = datetime.now()
        formatted_date = self.lm.format_date(now)
        formatted_time = self.lm.format_time(now)
        print(f"   Date: {formatted_date}")
        print(f"   Time: {formatted_time}")
        
        # Format number
        formatted_number = self.lm.format_number(1234567.89)
        print(f"   Number: {formatted_number}")
        
        # Set to Uzbekistan locale
        self.lm.set_locale("uz-UZ")
        print("\n🇺🇿 Uzbekistan:")
        
        # Format currency
        uzs_amount = 1234567.89
        formatted_currency = self.lm.format_currency(uzs_amount, "UZS")
        print(f"   Currency: {formatted_currency}")
        
        # Format date
        formatted_date = self.lm.format_date(now)
        formatted_time = self.lm.format_time(now)
        print(f"   Date: {formatted_date}")
        print(f"   Time: {formatted_time}")
        
        # Format number
        formatted_number = self.lm.format_number(1234567.89)
        print(f"   Number: {formatted_number}")
        
        # Format address
        address_data = {
            "street": "Tashkent sh., Amir Temur ko'chasi",
            "house": "1-uy",
            "city": "Tashkent",
            "region": "Toshkent viloyati",
            "postal_code": "100000",
            "country": "O'zbekiston"
        }
        formatted_address = self.lm.format_address(address_data)
        print(f"   Address:\n   {formatted_address.replace(chr(10), chr(10) + '   ')}")
        
        # Format name
        name_data = {
            "salutation": "Mr.",
            "first_name": "Aziz",
            "last_name": "Karimov"
        }
        formatted_name = self.lm.format_name(name_data)
        print(f"   Name: {formatted_name}")
    
    def demo_rtl_support(self):
        """Demonstrate RTL (Right-to-Left) language support"""
        print("\n➡️ RTL Language Support Demo")
        print("-" * 30)
        
        rtl_languages = ["ar", "he", "fa"]
        
        for lang in rtl_languages:
            self.mls.set_language(lang)
            config = self.mls.get_language_config()
            
            print(f"\n📍 Language: {lang.upper()} ({config.native_name})")
            print(f"   Direction: {config.direction.upper()}")
            print(f"   RTL Support: {'✅' if config.rtl_support else '❌'}")
            
            # Test welcome message translation
            if lang in ["ar", "he"]:
                welcome = self.mls.translate("welcome_message")
                print(f"   Welcome: {welcome}")
    
    def demo_number_systems(self):
        """Demonstrate different number systems"""
        print("\n🔢 Number Systems Demo")
        print("-" * 30)
        
        number = 1234567.89
        
        # Test different locale formatting
        locales = ["en-US", "uz-UZ", "ar-SA", "zh-CN"]
        
        for locale_code in locales:
            self.lm.set_locale(locale_code)
            locale_info = self.lm.get_locale_info()
            
            print(f"\n📍 Locale: {locale_code}")
            print(f"   Number System: {locale_info.number_system}")
            print(f"   Decimal Separator: '{locale_info.decimal_separator}'")
            print(f"   Thousands Separator: '{locale_info.thousands_separator}'")
            
            formatted_number = self.lm.format_number(number)
            print(f"   Formatted Number: {formatted_number}")
    
    def demo_translation_quality(self):
        """Demonstrate translation quality management"""
        print("\n📊 Translation Quality Demo")
        print("-" * 30)
        
        # Calculate quality metrics for English-Uzbek pair
        quality_metrics = self.tm.calculate_translation_quality("en-uz")
        
        print("English-Uzbek Translation Quality:")
        print(f"   Completeness: {quality_metrics.completeness:.2%}")
        print(f"   Accuracy: {quality_metrics.accuracy:.2%}")
        print(f"   Consistency: {quality_metrics.consistency:.2%}")
        print(f"   Cultural Appropriateness: {quality_metrics.cultural_appropriateness:.2%}")
        print(f"   Readability: {quality_metrics.readability:.2%}")
        print(f"   Technical Correctness: {quality_metrics.technical_correctness:.2%}")
        print(f"   Overall Score: {quality_metrics.overall_score:.2%}")
        
        # Generate quality report
        quality_report = self.tm.get_quality_report(["en", "uz", "ar"])
        
        print(f"\n📋 Quality Report Summary:")
        print(f"   Average Quality: {quality_report['summary'].get('average_quality', 0):.2%}")
        print(f"   Languages Needing Attention: {len(quality_report['summary'].get('languages_needing_attention', []))}")
        
        if quality_report['recommendations']:
            print("   📝 Recommendations:")
            for rec in quality_report['recommendations'][:3]:  # Show first 3
                print(f"     - {rec}")
    
    def demo_dynamic_switching(self):
        """Demonstrate dynamic language switching"""
        print("\n🔄 Dynamic Language Switching Demo")
        print("-" * 30)
        
        # Start with English
        self.mls.set_language("en")
        print("Switching languages dynamically:")
        
        languages_sequence = ["en", "uz", "ar", "zh", "ru"]
        
        for lang in languages_sequence:
            self.mls.set_language(lang)
            config = self.mls.get_language_config()
            
            # Get key translations
            welcome = self.mls.translate("welcome_message")
            login = self.mls.translate("login_button")
            dashboard = self.mls.translate("dashboard_title")
            
            print(f"\n📍 {lang.upper()} ({config.native_name}):")
            print(f"   Welcome: {welcome}")
            print(f"   Login: {login}")
            print(f"   Dashboard: {dashboard}")
            print(f"   Direction: {config.direction.upper()}")
    
    def demo_translation_suggestions(self):
        """Demonstrate AI-powered translation suggestions"""
        print("\n🤖 Translation Suggestions Demo")
        print("-" * 30)
        
        # Get suggestions for a new translation key
        suggestions = self.tm.get_translation_suggestions("new_feature_button", "uz", count=5)
        
        print("Translation suggestions for 'new_feature_button' in Uzbek:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion.translation}")
            print(f"      Confidence: {suggestion.confidence:.2f}")
            print(f"      Source: {suggestion.source}")
            if suggestion.requires_human_review:
                print(f"      ⚠️ Requires human review")
    
    def demo_export_import(self):
        """Demonstrate export and import functionality"""
        print("\n📤📥 Export/Import Demo")
        print("-" * 30)
        
        # Export translations in different formats
        languages = ["en", "uz", "ar"]
        
        print("Exporting translations...")
        
        # JSON export
        json_export = self.tm.export_translations(languages, format="json", include_metadata=True)
        print(f"✅ JSON export ready ({len(json_export)} characters)")
        
        # CSV export
        csv_export = self.tm.export_translations(languages, format="csv")
        print(f"✅ CSV export ready ({len(csv_export)} characters)")
        
        # PO export
        po_export = self.tm.export_translations(languages, format="po")
        print(f"✅ PO export ready ({len(po_export)} characters)")
        
        # Show sample of JSON export
        print("\n📋 Sample JSON export:")
        sample = json_export[:300] + "..." if len(json_export) > 300 else json_export
        print(sample)
    
    def demo_statistics(self):
        """Demonstrate system statistics"""
        print("\n📈 System Statistics Demo")
        print("-" * 30)
        
        # Multi-language system stats
        mls_stats = self.mls.get_statistics()
        print("Multi-Language System Statistics:")
        print(f"   Total Languages: {mls_stats['total_languages']}")
        print(f"   RTL Languages: {mls_stats['rtl_languages']}")
        print(f"   Total Translations: {mls_stats['total_translations']}")
        print(f"   Cache Size: {mls_stats['cache_size']}")
        
        # Translation manager stats
        tm_stats = self.tm.get_statistics()
        print(f"\nTranslation Manager Statistics:")
        print(f"   Total Keys: {tm_stats['total_keys']}")
        print(f"   Active Keys: {tm_stats['active_keys']}")
        print(f"   Supported Languages: {len(tm_stats['languages'])}")
        print(f"   Translation Memory Entries: {tm_stats['translation_memory_entries']}")
        
        # Localization manager stats
        lm_stats = self.lm.get_statistics()
        print(f"\nLocalization Manager Statistics:")
        print(f"   Supported Locales: {lm_stats['total_locales']}")
        print(f"   Supported Countries: {lm_stats['supported_countries']}")
        print(f"   RTL Locales: {lm_stats['rtl_locales']}")
        print(f"   Current Locale: {lm_stats['current_locale']}")
        print(f"   Current Timezone: {lm_stats['current_timezone']}")
    
    def demo_cultural_adaptations(self):
        """Demonstrate cultural adaptation features"""
        print("\n🎨 Cultural Adaptations Demo")
        print("-" * 30)
        
        # Test cultural adaptations for different regions
        regions = ["uz-UZ", "en-US", "ar-SA"]
        
        for region in regions:
            self.lm.set_locale(region)
            adaptations = self.lm.get_cultural_adaptations("Welcome to our platform!")
            
            print(f"\n📍 Region: {region}")
            print(f"   Communication Style: {adaptations['communication_style']}")
            print(f"   Tone Adjustments: {adaptations['tone_adjustments']}")
            print(f"   Cultural Elements: {len(adaptations['cultural_elements'])}")
            print(f"   Visual Suggestions: {len(adaptations['visual_suggestions'])}")
            print(f"   Avoidance List: {len(adaptations['avoidance_list'])} items")
    
    def demo_performance_optimization(self):
        """Demonstrate performance optimization features"""
        print("\n⚡ Performance Optimization Demo")
        print("-" * 30)
        
        # Test translation performance
        start_time = datetime.now()
        
        # Perform multiple translations
        for i in range(100):
            self.mls.translate("welcome_message")
            self.mls.translate("login_button")
            self.mls.translate("dashboard_title")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"Translation Performance Test:")
        print(f"   300 translations completed in: {duration:.3f} seconds")
        print(f"   Average per translation: {duration/300*1000:.2f} ms")
        
        # Test caching
        start_time = datetime.now()
        for i in range(50):
            # Should hit cache
            self.mls.translate("welcome_message")
        end_time = datetime.now()
        cached_duration = (end_time - start_time).total_seconds()
        
        print(f"Caching Performance Test:")
        print(f"   50 cached translations in: {cached_duration:.3f} seconds")
        print(f"   Average per cached translation: {cached_duration/50*1000:.2f} ms")
        
        # Optimize system
        self.mls.optimize_performance()
        print("\n✅ System optimization completed")
    
    def run_complete_demo(self):
        """Run the complete demonstration"""
        print("🚀 Running Complete Multi-Language System Demo\n")
        
        try:
            # Basic features
            self.demo_basic_translation()
            
            # Cultural adaptation
            self.demo_cultural_adaptation()
            
            # RTL support
            self.demo_rtl_support()
            
            # Number systems
            self.demo_number_systems()
            
            # Translation quality
            self.demo_translation_quality()
            
            # Dynamic switching
            self.demo_dynamic_switching()
            
            # Translation suggestions
            self.demo_translation_suggestions()
            
            # Export/Import
            self.demo_export_import()
            
            # Statistics
            self.demo_statistics()
            
            # Cultural adaptations
            self.demo_cultural_adaptations()
            
            # Performance
            self.demo_performance_optimization()
            
            print("\n" + "=" * 50)
            print("✅ Demo completed successfully!")
            print("🌍 Orion Starline Multi-Language System is ready for use!")
            
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main demo function"""
    demo = MultiLanguageDemo()
    demo.run_complete_demo()


if __name__ == "__main__":
    main()