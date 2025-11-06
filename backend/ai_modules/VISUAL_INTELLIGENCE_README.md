# Visual Intelligence System - Orion Starline AI Trading System

## 📋 Tavsif

Visual Intelligence tizimi - bu ilg'or vizual ma'lumotlar tahlil tizimi bo'lib, chart tahlili, OCR (Optical Character Recognition), hujjat tahlili va vizual signal detection funksiyalarini o'z ichiga oladi. Tizim financial trading, texnik tahlil va hujjat tahlili uchun mo'ljallangan.

## 🚀 Asosiy Imkoniyatlar

### 📈 Chart Analysis
- **Candlestick Pattern Recognition**: Doji, Hammer, Shooting Star, Engulfing pattern-larini aniqlash
- **Technical Pattern Detection**: Head & Shoulders, Triangles, Flags, Channels aniqlash
- **Trend Line Analysis**: Trend line-lar aniqlash va trend strength hisoblash
- **Support/Resistance Levels**: Muhim darajalar va pivot point hisoblash
- **Volume Profile Analysis**: Volume distribution va Point of Control (POC) tahlili
- **Price Action Analysis**: Market sentiment va momentum tahlili

### 🔤 OCR va Text Extraction
- **Multi-language Text Recognition**: Ingliz, O'zbek, Rus tillarida matn tanish
- **Chart Data Extraction**: Chart-dan narx va vaqt ma'lumotlarini extract qilish
- **Financial Document Analysis**: Moliyaviy hujjatlardan ma'lumot extract qilish
- **Handwriting Recognition**: Qo'lda yozilgan matnlarni tanish
- **Table Data Extraction**: Table ma'lumotlarini structured formatda olish
- **PDF Text Extraction**: PDF hujjatlardan matn va rasm extract qilish

### 🎯 Visual Signal Detection
- **Real-time Signal Generation**: Chart pattern-laridan vizual signallar yaratish
- **Multi-timeframe Analysis**: Turli vaqt oralig'larida tahlil
- **Signal Validation**: Signal ishonchliligini tekshirish
- **Sentiment Analysis**: Chart pattern-laridan market sentiment hisoblash
- **Performance Tracking**: Signal natijalarini kuzatib borish

### 📊 Advanced Analytics
- **Market Microstructure Analysis**: Order book va liquidity tahlili
- **Fibonacci Analysis**: Fibonacci retracement va extension darajalari
- **Elliott Wave Analysis**: Elliott Wave pattern tanish (kelgusida)
- **Gann Analysis**: Gann angle va square analysis (kelgusida)

## 🏗️ Modul Tuzilishi

```
ai_modules/
├── visual_intelligence.py      # Asosiy Visual Intelligence klassi
├── chart_analysis.py           # Chart va technical pattern tahlili
├── ocr_module.py               # OCR va hujjat tahlili
├── visual_intelligence_demo.py # Demo va test skripti
└── VISUAL_INTELLIGENCE_README.md # Ushbu fayl
```

## 📦 Asosiy Klasslar

### VisualIntelligence
Asosiy tizim klassi - barcha funksiyalarni boshqaradi.

```python
from ai_modules import VisualIntelligence

# Tizimni ishga tushirish
visual_ai = VisualIntelligence(config)

# Chart tahlili
result = visual_ai.analyze_chart_image(image_data, symbol="EURUSD", timeframe="1h")

# OCR extraction
text_result = visual_ai.extract_text_from_chart(image_data)

# Vizual signallar
signals = visual_ai.detect_visual_signals(image_data, min_confidence=70)
```

### ChartAnalyzer
Chart va technical pattern tahlili.

```python
from ai_modules import ChartAnalyzer

chart_analyzer = ChartAnalyzer()

# Candlestick patterns
patterns = chart_analyzer.detect_candlestick_patterns(image)

# Technical patterns
technical_patterns = chart_analyzer.detect_technical_patterns(image)

# Support/Resistance levels
sr_levels = chart_analyzer.identify_support_resistance(image)
```

### OCRProcessor
OCR va text extraction.

```python
from ai_modules import OCRProcessor

ocr_processor = OCRProcessor()

# Text extraction
text_result = ocr_processor.extract_text(image_data)

# Chart data extraction
chart_data = ocr_processor.extract_chart_data(image_data, include_prices=True)

# Table extraction
table_data = ocr_processor.extract_table_data(image_data)
```

## 🛠️ O'rnatish va Sozlanish

### Bog'liqliklar (Dependencies)
```bash
pip install opencv-python
pip install pytesseract
pip install pdf2image
pip install PyMuPDF
pip install Pillow
pip install scikit-learn
pip install scipy
pip install matplotlib
```

### Tesseract OCR
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-uzb tesseract-ocr-rus

# Windows
# Download tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
```

### Sozlanish Misoli
```python
config = {
    'chart_analysis': {
        'pattern_recognition': True,
        'trend_detection': True,
        'support_resistance': True,
        'fibonacci_levels': True,
        'min_confidence': 65
    },
    'ocr': {
        'languages': ['eng', 'uzb', 'rus'],
        'confidence_threshold': 80,
        'enhance_quality': True,
        'remove_noise': True
    },
    'visual_signals': {
        'min_confidence': 65,
        'signal_validation': True,
        'multi_timeframe': True
    },
    'performance': {
        'cache_enabled': True,
        'cache_ttl': 300,
        'batch_processing': True,
        'parallel_analysis': True
    }
}
```

## 📝 Foydalanish Misollari

### 1. Chart Image Tahlili
```python
import cv2
from ai_modules import VisualIntelligence

# Tizimni ishga tushirish
visual_ai = VisualIntelligence()

# Chart rasmi yuklash
image = cv2.imread('chart_screenshot.jpg')

# Tahlil qilish
result = visual_ai.analyze_chart_image(
    image_data=image,
    symbol="EURUSD",
    timeframe="1h"
)

print(f"Signal: {result.signal_type.value}")
print(f"Confidence: {result.confidence.value}")
print(f"Patterns: {len(result.patterns)} ta")
print(f"Sentiment: {result.sentiment_score:.2f}")
```

### 2. Batch Chart Processing
```python
# Ko'plab chart larni tahlil qilish
images = ['chart1.jpg', 'chart2.jpg', 'chart3.jpg']
symbols = ['EURUSD', 'GBPUSD', 'USDJPY']
timeframes = ['1h', '4h', '1d']

results = visual_ai.batch_analyze_charts(images, symbols, timeframes)

for i, result in enumerate(results):
    if result:
        print(f"{symbols[i]}: {result.signal_type.value} signal")
```

### 3. OCR va Text Extraction
```python
# Hujjat rasmidan matn extract qilish
document_image = cv2.imread('financial_report.jpg')

text_result = visual_ai.extract_text_from_chart(
    image_data=document_image,
    extract_price_data=True,
    extract_time_info=True
)

print(f"Extracted text: {text_result.text[:200]}...")
print(f"Confidence: {text_result.confidence:.1f}%")
```

### 4. PDF Hujjat Tahlili
```python
# PDF hujjat tahlili
from ai_modules import DocumentAnalyzer

doc_analyzer = DocumentAnalyzer()

with open('financial_report.pdf', 'rb') as f:
    pdf_data = f.read()

analysis = doc_analyzer.analyze_pdf_document(pdf_data)

print(f"Document type: {analysis.document_type.value}")
print(f"Summary: {analysis.summary[:200]}...")
print(f"Sentiment: {analysis.sentiment_score:.2f}")
```

### 5. Real-time Signal Detection
```python
# Real-time signal monitoring
import time

def monitor_signals():
    while True:
        # Latest chart screenshot
        current_chart = capture_latest_chart()
        
        # Signal detection
        signals = visual_ai.detect_visual_signals(current_chart, min_confidence=70)
        
        for signal in signals:
            print(f"New signal: {signal.signal_type.value}")
            print(f"Pattern: {signal.pattern_name}")
            print(f"Confidence: {signal.confidence:.1%}")
        
        time.sleep(60)  # Har daqiqa tekshirish

# monitor_signals()
```

## 🧪 Test va Demo

### Demo Skriptini Ishga Tushirish
```bash
cd /workspace/orion-starline/backend/ai_modules
python visual_intelligence_demo.py
```

### Test Natijalari
Demo skript quyidagi testlarni o'tkazadi:
1. ✅ Chart Analysis Test
2. ✅ OCR Extraction Test  
3. ✅ Visual Signals Test
4. ✅ Batch Processing Test
5. ✅ Performance Metrics Test

### Performance Monitoring
```python
# Performance metrikalar
metrics = visual_ai.get_performance_metrics()

print(f"Total analyses: {metrics['analysis_stats']['total_analyses']}")
print(f"Success rate: {metrics['analysis_stats']['successful_analyses'] / metrics['analysis_stats']['total_analyses'] * 100:.1f}%")
print(f"Average processing time: {metrics['analysis_stats']['avg_processing_time']:.2f}s")
```

## 🔧 Performance Optimization

### Caching
```python
# Cache ni faollashtirish
config = {
    'performance': {
        'cache_enabled': True,
        'cache_ttl': 300  # 5 minutes
    }
}

# Cache ni tozalash
visual_ai.clear_cache()
```

### Batch Processing
```python
# Parallel processing
config = {
    'batch_processing': {
        'enabled': True,
        'max_workers': 4,
        'batch_size': 10
    }
}
```

### Image Enhancement
```python
# OCR uchun image enhancement
enhanced_image = ocr_processor.enhance_for_ocr(raw_image)
```

## 📊 Signal Types

| Signal Type | Tavsif | Confidence Range |
|-------------|--------|------------------|
| BULLISH | Bullish signal | 65-95% |
| BEARISH | Bearish signal | 65-95% |
| NEUTRAL | Neutral/Mixed signals | 50-70% |
| BREAKOUT | Price breakout | 70-90% |
| REVERSAL | Trend reversal | 75-95% |
| CONTINUATION | Trend continuation | 65-85% |

## 🎯 Use Cases

### 1. Trading Signals
- Chart pattern-based trading signals
- Real-time signal generation
- Multi-timeframe confirmation
- Signal strength analysis

### 2. Document Processing
- Financial report analysis
- PDF text extraction
- Chart data digitization
- Table data extraction

### 3. Research & Analysis
- Historical pattern analysis
- Market sentiment tracking
- Visual data mining
- Automated report generation

### 4. Quality Control
- Chart accuracy verification
- Document completeness check
- Data validation
- Anomaly detection

## 🐛 Debugging va Xatoliklarni Topish

### Logging
```python
import logging

# Debug level logging
logging.basicConfig(level=logging.DEBUG)

# Visual Intelligence logger
logger = logging.getLogger('ai_modules.visual_intelligence')
logger.setLevel(logging.INFO)
```

### Common Issues

1. **OCR Quality Issues**
   - Image quality enhancementni yoqish
   - Noise removal qilish
   - Binarization применять

2. **Pattern Detection Issues**
   - Confidence threshold pasaytirish
   - Min pattern size ni sozlash
   - Image resolution oshirish

3. **Performance Issues**
   - Caching yoqish
   - Batch processing ishlatish
   - Parallel processing sozlash

## 🔄 Changelog

### v1.0.0 (2025-11-05)
- ✅ Initial release
- ✅ Chart analysis funksiyalari
- ✅ OCR va text extraction
- ✅ Visual signal detection
- ✅ Document analysis
- ✅ Batch processing
- ✅ Performance monitoring
- ✅ Demo va test skriptlari

## 🤝 Contributing

Tizimga contribution qilish uchun:

1. Fork qilish
2. Feature branch yaratish
3. Changes qilish
4. Test qilish
5. Pull request yaratish

## 📜 License

MIT License - see LICENSE file for details.

## 👥 Authors

**Orion Starline AI Team**
- AI/ML Engineers
- Quantitative Analysts  
- Software Developers

## 📞 Support

Texnik yordam va savollar uchun:
- GitHub Issues
- Email: support@orion-starline.ai
- Documentation: https://docs.orion-starline.ai

---

**⚡ Visual Intelligence tizimi - Intelligent Trading uchun Vizual Tahqiqot!**
