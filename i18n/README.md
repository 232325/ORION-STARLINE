# Orion Starline Multi-Language & Localization System

Professional multi-language and localization system supporting 20+ languages with advanced features including RTL support, cultural adaptation, dynamic language switching, and locale detection.

## 🚀 Features

### Core Features
- **20+ Languages Support** - Major global languages including English, Uzbek, Russian, Chinese, Arabic, Spanish, French, German, Japanese, Korean, and more
- **RTL Support** - Full Right-to-Left language support for Arabic, Hebrew, Persian, and other RTL languages
- **Cultural Adaptation** - Region-specific cultural preferences, color meanings, business culture, and communication styles
- **Dynamic Language Switching** - Real-time language switching without page reload
- **Automatic Locale Detection** - Smart detection of user location, language preferences, and system settings
- **Translation Memory** - Reusable translation suggestions with fuzzy matching
- **Quality Assurance** - Automated quality scoring and translation validation
- **Performance Optimized** - Caching, concurrent processing, and memory optimization

### Advanced Features
- **Multiple Number Systems** - Arabic-Indic, Eastern Arabic, Bengali, Thai, and Khmer number systems
- **Regional Formatting** - Country-specific date, time, currency, and number formatting
- **Address & Name Formatting** - Culturally appropriate address and name formatting
- **Holiday Calendars** - Region-specific holiday and calendar support
- **Business Culture Integration** - Communication style, decision-making preferences, and cultural taboos
- **Export/Import** - Multiple format support (JSON, CSV, PO, YAML)
- **Real-time Translation** - Dynamic translation updates and suggestions
- **Analytics & Reporting** - Translation quality metrics and system performance analytics

## 📁 Project Structure

```
/workspace/orion-starline/i18n/
├── multilang_system.py      # Core multi-language system
├── translations.py          # Translation management system
├── localization.py          # Advanced localization system
├── demo.py                  # Comprehensive demonstration
├── README.md               # This documentation
├── language_configs.yaml   # Language configurations
├── cultural_contexts.json  # Cultural context data
├── cultural_preferences.json # Cultural preferences
├── locales.json           # Locale definitions
├── format_specifications.json # Address/name formats
├── translations/          # Translation files
│   ├── en.json           # English translations
│   ├── uz.json           # Uzbek translations
│   ├── ar.json           # Arabic translations
│   └── ...
├── translation_memory.pkl # Translation memory cache
└── quality_metrics.json  # Quality metrics data
```

## 🌍 Supported Languages

| Language | Code | Native Name | RTL | Locale |
|----------|------|-------------|-----|--------|
| English | en | English | ❌ | en-US |
| Uzbek | uz | O'zbek | ❌ | uz-UZ |
| Russian | ru | Русский | ❌ | ru-RU |
| Chinese (Simplified) | zh | 中文 | ❌ | zh-CN |
| Spanish | es | Español | ❌ | es-ES |
| French | fr | Français | ❌ | fr-FR |
| German | de | Deutsch | ❌ | de-DE |
| Japanese | ja | 日本語 | ❌ | ja-JP |
| Korean | ko | 한국어 | ❌ | ko-KR |
| Arabic | ar | العربية | ✅ | ar-SA |
| Hindi | hi | हिन्दी | ❌ | hi-IN |
| Portuguese | pt | Português | ❌ | pt-PT |
| Italian | it | Italiano | ❌ | it-IT |
| Dutch | nl | Nederlands | ❌ | nl-NL |
| Swedish | sv | Svenska | ❌ | sv-SE |
| Norwegian | no | Norsk | ❌ | no-NO |
| Danish | da | Dansk | ❌ | da-DK |
| Finnish | fi | Suomi | ❌ | fi-FI |
| Polish | pl | Polski | ❌ | pl-PL |
| Turkish | tr | Türkçe | ❌ | tr-TR |
| Thai | th | ไทย | ❌ | th-TH |
| Vietnamese | vi | Tiếng Việt | ❌ | vi-VN |
| Indonesian | id | Bahasa Indonesia | ❌ | id-ID |
| Hebrew | he | עברית | ✅ | he-IL |
| Persian | fa | فارسی | ✅ | fa-IR |

## 🛠 Installation & Setup

### Prerequisites
```bash
pip install babel requests
```

### Quick Start
```python
from i18n.multilang_system import MultiLanguageSystem
from i18n.localization import LocalizationManager

# Initialize systems
mls = MultiLanguageSystem()
lm = LocalizationManager()

# Set language
mls.set_language("uz")  # Uzbek
lm.set_locale("uz-UZ")  # Uzbekistan locale

# Get translations
welcome = mls.translate("welcome_message")
print(welcome)  # "Xush kelibsiz!"

# Format currency
amount = mls.format_currency(1234.56, "UZS")
print(amount)  # "1 234,56 so'm"

# Format date
from datetime import datetime
date = lm.format_date(datetime.now())
print(date)  # "05.11.2025"
```

### Advanced Usage

#### Translation Management
```python
from i18n.translations import TranslationManager, TranslationType

tm = TranslationManager()

# Add translation key
tm.add_translation_key(
    key="new_feature",
    namespace="ui",
    description="New feature button",
    translation_type=TranslationType.UI,
    character_limit=20
)

# Add translations
tm.update_translation("en", "new_feature", "New Feature")
tm.update_translation("uz", "new_feature", "Yangi Imkoniyat")

# Get quality metrics
quality = tm.calculate_translation_quality("en-uz")
print(f"Quality score: {quality.overall_score:.2%}")

# Get suggestions
suggestions = tm.get_translation_suggestions("user_profile", "uz")
```

#### Cultural Adaptation
```python
# Get cultural adaptations
adaptations = lm.get_cultural_adaptations(
    "Welcome to our platform!", 
    locale_code="uz-UZ"
)

print(adaptations["communication_style"])  # "polite_formal"
print(adaptations["cultural_elements"])   # List of cultural elements

# Format address
address_data = {
    "street": "Tashkent sh., Amir Temur ko'chasi",
    "house": "1-uy",
    "city": "Tashkent",
    "postal_code": "100000"
}
formatted_address = lm.format_address(address_data, "uz-UZ")
```

#### Number Systems
```python
# Arabic-Indic numbers
lm.set_locale("ar-SA")
arabic_number = lm.format_number(1234567.89)
print(arabic_number)  # "١٢٣٤٥٦٧٫٨٩"

# Eastern Arabic numbers (for Persian/Urdu)
lm.set_locale("fa-IR")
persian_number = lm.format_number(1234567.89)
print(persian_number)  # "۱۲۳۴۵۶۷٫۸۹"
```

#### Dynamic Switching
```python
# Dynamic language switching
languages = ["en", "uz", "ar", "zh"]

for lang in languages:
    mls.set_language(lang)
    welcome = mls.translate("welcome_message")
    print(f"{lang}: {welcome}")

# Check RTL support
is_rtl = mls.is_rtl("ar")  # True for Arabic
print(f"Arabic is RTL: {is_rtl}")
```

## 🎯 Usage Examples

### Basic Translation
```python
# Initialize
from i18n.multilang_system import _, _n

# Simple translation
greeting = _("hello", "Hello World")
print(greeting)  # "Hello World" (default)

# With variables
user_greeting = _("hello_user", "Hello, {name}!", name="Aziz")
print(user_greeting)  # "Hello, Aziz!"

# Plural forms
item_count = _n("item", "items", 5, count=5)
print(item_count)  # "5 items"
```

### Locale Detection
```python
# Auto-detect locale
lm._auto_detect_locale()
current_locale = lm.get_locale()
print(f"Detected locale: {current_locale}")  # e.g., "en-US"

# Manual locale setting
lm.set_locale("uz-UZ")
locale_info = lm.get_locale_info()
print(f"Currency: {locale_info.currency}")  # "UZS"
print(f"Timezone: {locale_info.timezone}")  # "Asia/Samarkand"
```

### Cultural Adaptations
```python
# Get cultural preferences
cultural_pref = lm.cultural_preferences["uz-UZ"]
print(cultural_pref.preferred_greetings)  # Various greetings
print(cultural_pref.business_culture)     # Business culture info

# Color meanings
print(cultural_pref.color_preferences["green"])  # "blessing, Islam, good fortune"
print(cultural_pref.color_preferences["red"])    # "danger, passion, power"
```

### Export/Import
```python
# Export translations
export_data = tm.export_translations(["en", "uz"], format="json")
print("Exported JSON:", export_data[:200])

# Import translations
import_success = tm.import_translations(export_data, format="json")
print(f"Import successful: {import_success}")

# PO format export
po_data = tm.export_translations(["en", "uz"], format="po")
```

### Performance Monitoring
```python
# Get system statistics
stats = mls.get_statistics()
print(f"Languages: {stats['total_languages']}")
print(f"Translations: {stats['total_translations']}")
print(f"RTL Languages: {stats['rtl_languages']}")

# Translation performance
start = datetime.now()
mls.translate("welcome_message")  # First time (cache miss)
duration = (datetime.now() - start).total_seconds()
print(f"Translation time: {duration*1000:.2f}ms")
```

## 🧪 Running the Demo

```bash
cd /workspace/orion-starline/i18n
python demo.py
```

The demo includes:
- Basic translation functionality
- Cultural adaptation examples
- RTL language support
- Number system demonstrations
- Translation quality management
- Dynamic language switching
- Export/import functionality
- Performance optimization
- Statistics and analytics

## 📊 Quality Metrics

The system provides comprehensive quality metrics:

- **Completeness** - Percentage of translated keys
- **Accuracy** - Translation accuracy based on similarity
- **Consistency** - Consistency across translations
- **Cultural Appropriateness** - Cultural adaptation quality
- **Readability** - Text readability scores
- **Technical Correctness** - Technical accuracy and review status

## 🔧 Configuration

### Language Configuration
Edit `language_configs.yaml` to modify language settings:
```yaml
uz:
  name: "Uzbek"
  native_name: "O'zbek"
  direction: "ltr"
  locale: "uz_UZ"
  currency: "UZS"
  timezone: "Asia/Samarkand"
```

### Cultural Preferences
Edit `cultural_preferences.json` to modify cultural settings:
```json
{
  "uz-UZ": {
    "region": "Uzbekistan",
    "communication_style": "polite_formal",
    "decision_making_style": "consensus",
    "color_preferences": {
      "green": "blessing, Islam, good fortune",
      "red": "danger, passion, power"
    }
  }
}
```

## 🚀 Performance Tips

1. **Enable Caching** - Set `cache_enabled = True` for better performance
2. **Use Batch Operations** - Process multiple translations together
3. **Monitor Quality** - Regular quality checks improve translation accuracy
4. **Optimize Memory** - Use `optimize_performance()` periodically
5. **Monitor Statistics** - Track usage patterns and optimize accordingly

## 🔮 Future Enhancements

- Machine Learning integration for better translation suggestions
- Real-time collaborative translation
- Advanced cultural analysis
- Integration with external translation services
- Mobile app localization support
- Web dashboard for translation management
- Advanced analytics and reporting
- Voice-to-text translation support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add translations for new languages
4. Test thoroughly with the demo
5. Submit a pull request

## 📄 License

This project is part of Orion Starline Trading Platform and follows the same licensing terms.

## 📞 Support

For technical support or questions:
- Email: support@orion-starline.com
- Documentation: [Internal Wiki]
- Issues: [Internal Issue Tracker]

---

**Orion Starline Multi-Language System** - Professional localization for global reach! 🌍✨