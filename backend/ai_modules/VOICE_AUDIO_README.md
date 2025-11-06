# Voice & Audio Features - Orion Starline AI Trading System

## 📖 Ma'lumot

Voice & Audio Features tizimi Orion Starline AI Trading System uchun yaratilgan keng qamrovli voice va audio qayta ishlash yechimini ta'minlaydi. Bu tizim trading voice commands, sentiment analysis, speaker identification, va ko'p tillli qo'llab-quvvatlashni o'z ichiga oladi.

## 🏗️ Tuzilish

### Asosiy Modullar

1. **voice_features.py** - Voice & Audio asosiy funksiyalari
2. **stt_tts.py** - Speech-to-Text va Text-to-Speech
3. **audio_analysis.py** - Audio tahlil va qayta ishlash
4. **voice_audio_demo.py** - To'liq demo va test fayl

### Texnik Xususiyatlar

- **Sample Rate**: 16kHz (default)
- **Bit Depth**: 16-bit
- **Channels**: Mono (1)
- **Frame Size**: 1024 samples
- **Hop Size**: 512 samples
- **Supported Formats**: WAV, MP3, FLAC, OGG

## 🚀 Asosiy Funksiyalar

### 1. Speech-to-Text (STT)

#### Qo'llab-quvvatlanadigan Providerlar

```python
from ai_modules import STTProvider, stt_engine

# Google STT
result = await stt_engine.transcribe(audio_data, "uz-UZ", STTProvider.GOOGLE)

# OpenAI Whisper
result = await stt_engine.transcribe(audio_data, "en-US", STTProvider.WHISPER)

# Azure Speech
result = await stt_engine.transcribe(audio_data, "ru-RU", STTProvider.AZURE)

# AWS Transcribe
result = await stt_engine.transcribe(audio_data, "en-US", STTProvider.AWS_TRANSCRIBE)
```

#### Multi-language Support

```python
from ai_modules import Language, voice_features

languages = voice_features.get_supported_languages()
# [
#     {'code': 'uz-UZ', 'name': 'O\'zbek', 'native': 'O\'zbek'},
#     {'code': 'en-US', 'name': 'English', 'native': 'English'},
#     {'code': 'ru-RU', 'name': 'Русский', 'native': 'Русский'},
#     # ...
# ]

# Auto language detection
language = voice_features.detect_language("Salom, qanday yuribdi?")
# Language.UZBEK
```

### 2. Text-to-Speech (TTS)

#### Qo'llab-quvvatlanadigan Providerlar

```python
from ai_modules import TTSProvider, VoiceSettings, tts_engine

# Google TTS
voice_settings = VoiceSettings(language="uz-UZ", speed=1.0, volume=0.8)
result = await tts_engine.synthesize(text, voice_settings, TTSProvider.GOOGLE)

# Amazon Polly
result = await tts_engine.synthesize(text, voice_settings, TTSProvider.AMAZON_POLLY)

# Azure TTS
result = await tts_engine.synthesize(text, voice_settings, TTSProvider.AZURE)

# ElevenLabs
result = await tts_engine.synthesize(text, voice_settings, TTSProvider.ELEVENLABS)

# Offline PyTTSx3
result = await tts_engine.synthesize(text, voice_settings, TTSProvider.PYTTSX3)
```

#### Voice Settings

```python
from ai_modules import create_voice_settings

# O'zbek tili settings
uzbek_settings = create_voice_settings(
    language="uz-UZ",
    speed=1.1,
    volume=0.8,
    voice_id=None  # Auto-select
)

# Ingliz tili settings
english_settings = create_voice_settings(
    language="en-US",
    speed=1.0,
    volume=0.9
)
```

### 3. Trading Voice Commands

#### Asosiy Trading Commands

```python
from ai_modules import process_voice_command

# Buy order
command = await process_voice_command("Buy EURUSD at 1.1000")
print(f"Intent: {command.intent}")  # "buy"
print(f"Parameters: {command.parameters}")  # {"symbol": "EURUSD", "price": 1.1000}

# Price check
command = await process_voice_command("Bitcoin narxi qancha?")
print(f"Intent: {command.intent}")  # "price_check"

# Market analysis
command = await process_voice_command("AAPL bozor tahlil qil")
print(f"Intent: {command.intent}")  # "market_analysis"

# Portfolio status
command = await process_voice_command("Portfolio holat ko'rsat")
print(f"Intent: {command.intent}")  # "portfolio_status"
```

#### Trading Commands Namunalari

| Command | Intent | Description |
|---------|--------|-------------|
| `Buy EURUSD at 1.1000` | buy | EURUSD sotib olish |
| `Sell EURUSD at 1.1050` | sell | EURUSD sotish |
| `Bitcoin narxi qancha` | price_check | Bitcoin narxini tekshirish |
| `Portfolio holat ko'rsat` | portfolio_status | Portfolio holat ko'rsatish |
| `AAPL bozor tahlil qil` | market_analysis | AAPL bozor tahlili |
| `Risk assessment` | risk_assessment | Risk baholash |

### 4. Voice Sentiment & Emotion Analysis

#### Sentiment Analysis

```python
from ai_modules import analyze_voice_sentiment

# O'zbek sentiment
text = "Zo'r kelmoqda, katta foyda!"
sentiment = analyze_voice_sentiment(text)
# 0.6 (positive)

text = "Bu juda yomon, katta zarar bo'ldi"
sentiment = analyze_voice_sentiment(text)
# -0.7 (negative)
```

#### Emotion Detection

```python
from ai_modules import VoiceEmotion, detect_emotion, audio_analyzer
from ai_modules import AudioFeatures

# Audio features extraction
features = audio_analyzer.extract_audio_features(audio_data)

# Simple emotion detection
emotion = detect_emotion(features)
# VoiceEmotion.HAPPY, VoiceEmotion.SAD, etc.

# Detailed emotion analysis
detailed = audio_analyzer.detect_emotion_detailed(features)
print(f"Emotion: {detailed.emotion.value}")
print(f"Confidence: {detailed.confidence:.2f}")
print(f"Intensity: {detailed.intensity:.2f}")
print(f"VAD: Valence={detailed.valence:.2f}, Arousal={detailed.arousal:.2f}, Dominance={detailed.dominance:.2f}")
```

### 5. Speaker Identification & Biometric Authentication

#### Speaker Training

```python
from ai_modules import train_speaker_model

# Speaker model train qilish
user_id = "trader_001"
audio_samples = [audio_data1, audio_data2, audio_data3, audio_data4, audio_data5]

success = await train_speaker_model(user_id, audio_samples)
if success:
    print(f"Speaker {user_id} muvaffaqiyatli train qilindi")
```

#### Speaker Identification

```python
from ai_modules import identify_speaker, audio_analyzer

# Audio features extraction
features = audio_analyzer.extract_audio_features(audio_data)

# Speaker identification
speaker_id = identify_speaker(features)
if speaker_id:
    print(f"Tanilgan speaker: {speaker_id}")
else:
    print("Speaker topilmadi")
```

#### Voice Biometric Authentication

```python
from ai_modules import voice_features

# Voice authentication
user_id = "trader_001"
audio_data = user_voice_audio

authenticated = await voice_features.voice_biometric_authentication(audio_data, user_id)
if authenticated:
    print(f"User {user_id} authentication muvaffaqiyatli")
else:
    print("Authentication muvaffaqiyatsiz")
```

### 6. Audio Analysis & Enhancement

#### Complete Audio Analysis

```python
from ai_modules import analyze_audio

# To'liq audio tahlil
result = await analyze_audio(audio_data)
print(f"Quality score: {result.quality_score:.3f}")
print(f"Quality level: {result.quality_level.value}")
print(f"Voice emotion: {result.voice_analysis.emotion.value}")
print(f"Sentiment: {result.voice_analysis.sentiment:.2f}")

# Enhancement takliflari
for suggestion in result.enhancement_suggestions:
    print(f"Taqdim: {suggestion}")
```

#### Audio Enhancement

```python
from ai_modules import AudioEnhancementSettings, enhance_audio

# Enhancement settings
settings = AudioEnhancementSettings(
    noise_reduction_level=0.6,
    voice_enhancement_level=0.8,
    normalization_enabled=True,
    compression_ratio=2.5,
    eq_settings={
        "bass": 1.2,
        "mid": 1.0,
        "treble": 1.1
    }
)

# Audio enhancement
enhanced_audio = enhance_audio(original_audio, settings)
```

#### Audio Features Extraction

```python
from ai_modules import audio_analyzer

features = audio_analyzer.extract_audio_features(audio_data)
print(f"RMS: {features.rms:.6f}")
print(f"Zero crossings: {features.zero_crossings}")
print(f"Spectral centroid: {features.spectral_centroid:.2f} Hz")
print(f"Spectral bandwidth: {features.spectral_bandwidth:.2f} Hz")
print(f"MFCC: {len(features.mfcc_features)} coefficients")
print(f"Chroma: {len(features.chroma_features)} bins")
print(f"Mel spectrogram: {len(features.mel_spectrogram)} bands")
```

### 7. Real-time Voice Processing

#### Streaming STT

```python
from ai_modules import get_streaming_stt, STTProvider

def on_transcription(result):
    print(f"STT result: {result.text}")
    print(f"Confidence: {result.confidence:.2f}")

# Streaming STT
streaming_stt = get_streaming_stt()
streaming_stt.start_streaming(
    callback=on_transcription,
    language="uz-UZ",
    provider=STTProvider.GOOGLE
)

# Audio ma'lumotlarni qo'shish
streaming_stt.add_audio_data(audio_chunk)
```

#### Streaming TTS

```python
from ai_modules import get_streaming_tts, VoiceSettings

def on_synthesis(result):
    print(f"TTS completed: {len(result.audio_data)} bytes")

# Streaming TTS
streaming_tts = get_streaming_tts()
voice_settings = VoiceSettings(language="uz-UZ", speed=1.0)

streaming_tts.start_streaming(
    callback=on_synthesis,
    voice_settings=voice_settings
)

# Matn qo'shish
streaming_tts.add_text("Salom, bu test matni")
```

## 🔧 Sozlamalar va Konfiguratsiya

### Provider Konfiguratsiyasi

```python
from ai_modules import stt_engine, tts_engine, STTProvider, TTSProvider

# Google STT konfiguratsiyasi
stt_engine.configure_provider(STTProvider.GOOGLE, {
    'api_key': 'your_google_api_key'
})

# Azure TTS konfiguratsiyasi
tts_engine.configure_provider(TTSProvider.AZURE, {
    'key': 'your_azure_key',
    'region': 'eastus'
})
```

### Language Detection Customization

```python
# Til detection so'zlarini qo'shish
uzbek_words = ['salom', 'qanday', 'kim', 'qayerda', 'qachon', 'nima']
russian_words = ['привет', 'как', 'кто', 'где', 'когда', 'что']
english_words = ['hello', 'how', 'who', 'where', 'when', 'what']
```

### Trading Commands Customization

```python
from ai_modules import voice_features

# Custom trading patterns qo'shish
voice_features.trading_patterns['buy'].append(r'yangi buy order (.+)')
voice_features.trading_patterns['sell'].append(r'yangi sell order (.+)')
```

## 📊 Asosiy Ma'lumotlar

### Qo'llab-quvvatlanadigan Tillar

1. **O'zbek (uz-UZ)** - Asosiy til
2. **Ingliz (en-US)** - English
3. **Rus (ru-RU)** - Русский
4. **Xitoy (zh-CN)** - 中文
5. **Yapon (ja-JP)** - 日本語

### Voice Emotions

1. **NEUTRAL** - Neytral
2. **HAPPY** - Xursand
3. **SAD** - G'amgin
4. **ANGRY** - G'azablangan
5. **EXCITED** - Hayajonlangan
6. **FEARFUL** - Qo'rqqan
7. **DISGUSTED** - Jirkanchi
8. **SURPRISED** - Ajablangan

### Audio Quality Levels

1. **EXCELLENT** (0.9-1.0) - A'lo
2. **GOOD** (0.7-0.9) - Yaxshi
3. **FAIR** (0.5-0.7) - O'rtacha
4. **POOR** (0.3-0.5) - Yomon
5. **VERY_POOR** (0.0-0.3) - juda yomon

## 🧪 Test va Demo

### Barcha funksiyalarni test qilish

```bash
cd /workspace/orion-starline/backend/ai_modules
python voice_audio_demo.py
```

### Demo Test Namunalari

```python
import asyncio
from voice_audio_demo import main

# Demo ishga tushirish
asyncio.run(main())
```

### Unit Test Misollari

```python
# STT test
import asyncio
from ai_modules import transcribe_audio, STTProvider

async def test_stt():
    audio_data = b"\\x00\\x00" * 1000  # Mock audio
    result = await transcribe_audio(audio_data, "uz-UZ", STTProvider.GOOGLE)
    print(f"STT result: {result.text}")

# TTS test
import asyncio
from ai_modules import synthesize_speech, VoiceSettings, TTSProvider

async def test_tts():
    text = "Salom, bu test"
    settings = VoiceSettings(language="uz-UZ")
    result = await synthesize_speech(text, settings, TTSProvider.PYTTSX3)
    print(f"TTS size: {len(result.audio_data)} bytes")

# Audio analysis test
import asyncio
from ai_modules import analyze_audio

async def test_audio_analysis():
    audio_data = b"\\x00\\x00" * 2000
    result = await analyze_audio(audio_data)
    print(f"Quality: {result.quality_level.value}")
    print(f"Emotion: {result.voice_analysis.emotion.value}")
```

## 🔄 Real-time Integration

### Trading System bilan integratsiya

```python
from ai_modules import voice_features, process_voice_command
import asyncio

class VoiceTradingInterface:
    def __init__(self):
        self.voice_engine = voice_features
    
    async def handle_voice_command(self, audio_data):
        # STT
        text = await self.voice_engine.speech_to_text(audio_data)
        
        if text:
            # Command processing
            command = await process_voice_command(text)
            
            # Trading system integratsiyasi
            if command.intent == "buy":
                return await self.execute_buy_order(command)
            elif command.intent == "sell":
                return await self.execute_sell_order(command)
            elif command.intent == "price_check":
                return await self.get_price_info(command)
    
    async def execute_buy_order(self, command):
        # Trading system buy order
        symbol = command.parameters.get('symbol')
        price = command.parameters.get('price')
        # ... buy order logic
        
        return f"Buy order executed: {symbol} at {price}"
    
    async def execute_sell_order(self, command):
        # Trading system sell order
        symbol = command.parameters.get('symbol')
        price = command.parameters.get('price')
        # ... sell order logic
        
        return f"Sell order executed: {symbol} at {price}"
```

### Voice Feedback System

```python
from ai_modules import tts_engine, VoiceSettings, TTSProvider

class VoiceFeedback:
    def __init__(self):
        self.tts_engine = tts_engine
        self.settings = VoiceSettings(language="uz-UZ", speed=1.0, volume=0.8)
    
    async def speak_feedback(self, message):
        # TTS synthesis
        result = await self.tts_engine.synthesize(message, self.settings, TTSProvider.PYTTSX3)
        
        # Audio playback
        if result.audio_data:
            self.play_audio(result.audio_data)
    
    def play_audio(self, audio_data):
        # Audio playback implementation
        # ... play audio data
        pass
    
    async def confirm_trade(self, symbol, action, price):
        message = f"{action} order confirmed for {symbol} at {price}"
        await self.speak_feedback(message)
```

## ⚡ Performance

### Tezlik Optimizatsiyasi

```python
# Async operations
import asyncio

# Parallel STT va TTS
async def parallel_processing(audio_data, text):
    stt_task = transcribe_audio(audio_data, "uz-UZ")
    tts_task = synthesize_speech(text, settings)
    
    stt_result, tts_result = await asyncio.gather(stt_task, tts_task)
    return stt_result, tts_result

# Caching
from ai_modules import voice_features

# Voice settings caching
cached_settings = voice_features.voice_cache.get("uzbek_default")
if not cached_settings:
    cached_settings = VoiceSettings(language="uz-UZ")
    voice_features.voice_cache["uzbek_default"] = cached_settings
```

## 🛠️ Xatoliklarni Boshqarish

### Error Handling

```python
import logging
from ai_modules import transcribe_audio, STTProvider

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def safe_stt(audio_data, language="uz-UZ"):
    try:
        result = await transcribe_audio(audio_data, language, STTProvider.GOOGLE)
        return result
    except sr.UnknownValueError:
        logger.warning("Audio tanilmadi")
        return None
    except sr.RequestError as e:
        logger.error(f"STT service error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None
```

### Fallback Mechanisms

```python
# Multiple providers fallback
async def robust_stt(audio_data, language="uz-UZ"):
    providers = [STTProvider.GOOGLE, STTProvider.WHISPER, STTProvider.AZURE]
    
    for provider in providers:
        try:
            result = await transcribe_audio(audio_data, language, provider)
            if result and result.confidence > 0.5:
                return result
        except Exception as e:
            logger.warning(f"Provider {provider.value} failed: {e}")
            continue
    
    return None  # All providers failed
```

## 📈 Monitoring va Analytics

### Performance Metrics

```python
from datetime import datetime
from ai_modules import voice_features

class VoiceMetrics:
    def __init__(self):
        self.metrics = {
            'stt_requests': 0,
            'tts_requests': 0,
            'success_rate': 0.0,
            'average_latency': 0.0,
            'language_distribution': {},
            'emotion_distribution': {}
        }
    
    def record_stt_request(self, latency, language, success):
        self.metrics['stt_requests'] += 1
        if success:
            # Update success rate
            # Update latency
            # Update language distribution
            pass
    
    def get_metrics_report(self):
        return {
            'total_stt_requests': self.metrics['stt_requests'],
            'total_tts_requests': self.metrics['tts_requests'],
            'success_rate': self.metrics['success_rate'],
            'average_latency': self.metrics['average_latency'],
            'language_distribution': self.metrics['language_distribution'],
            'emotion_distribution': self.metrics['emotion_distribution']
        }
```

## 🔒 Xavfsizlik

### Voice Biometric Security

```python
from ai_modules import voice_features

class SecureVoiceAuth:
    def __init__(self):
        self.auth_threshold = 0.85
        self.max_attempts = 3
    
    async def authenticate_user(self, user_id, voice_sample):
        attempts = 0
        while attempts < self.max_attempts:
            authenticated = await voice_features.voice_biometric_authentication(
                voice_sample, user_id
            )
            
            if authenticated:
                return True, "Authentication successful"
            else:
                attempts += 1
                if attempts < self.max_attempts:
                    voice_sample = await self.get_new_voice_sample()
        
        return False, "Authentication failed after maximum attempts"
```

## 📝 Log va Debug

### Detailed Logging

```python
import logging
from ai_modules import voice_features

# Voice system logging
voice_logger = logging.getLogger('voice_system')
voice_logger.setLevel(logging.DEBUG)

# Handler qo'shish
handler = logging.FileHandler('voice_system.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
voice_logger.addHandler(handler)

# Log usage
voice_logger.info(f"STT request: language={language}, provider={provider.value}")
voice_logger.debug(f"Voice features: RMS={features.rms}, Centroid={features.spectral_centroid}")
voice_logger.warning(f"Low confidence: {confidence:.2f}")
```

## 🎯 Best Practices

### 1. Performance

```python
# Audio chunking for real-time processing
CHUNK_SIZE = 1024
SAMPLE_RATE = 16000

def process_audio_stream(audio_stream):
    buffer = []
    for chunk in audio_stream:
        buffer.append(chunk)
        if len(buffer) * CHUNK_SIZE >= SAMPLE_RATE:  # 1 second
            combined_audio = b''.join(buffer)
            yield process_audio_chunk(combined_audio)
            buffer = []
```

### 2. Resource Management

```python
import contextlib

@contextlib.asynccontextmanager
async def voice_session():
    # Session setup
    stt_engine = STTEngine()
    tts_engine = TTSEngine()
    
    try:
        yield stt_engine, tts_engine
    finally:
        # Cleanup
        await stt_engine.cleanup()
        await tts_engine.cleanup()

# Usage
async with voice_session() as (stt, tts):
    result = await stt.transcribe(audio_data)
    await tts.synthesize("Hello", settings)
```

### 3. Error Recovery

```python
import asyncio
from ai_modules import voice_features

async def resilient_voice_processing(audio_data):
    max_retries = 3
    backoff_delay = 1.0
    
    for attempt in range(max_retries):
        try:
            # Voice processing
            text = await voice_features.speech_to_text(audio_data)
            return text
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(backoff_delay * (2 ** attempt))
```

## 🚀 Deployment

### Production Setup

```python
# Production configuration
PRODUCTION_CONFIG = {
    "stt_providers": {
        "primary": "google",
        "fallback": ["whisper", "azure"]
    },
    "tts_providers": {
        "primary": "amazon_polly",
        "fallback": ["azure", "pyttsx3"]
    },
    "audio_settings": {
        "sample_rate": 16000,
        "channels": 1,
        "chunk_size": 1024
    },
    "voice_biometric": {
        "enabled": True,
        "threshold": 0.85,
        "max_attempts": 3
    },
    "caching": {
        "enabled": True,
        "max_size": 1000
    }
}
```

### Health Check

```python
async def health_check():
    try:
        # STT health check
        test_audio = b"\\x00\\x00" * 1000
        stt_result = await stt_engine.transcribe(test_audio, "en-US")
        
        # TTS health check
        tts_result = await tts_engine.synthesize("test", settings)
        
        # Audio analysis health check
        analysis_result = await audio_analyzer.analyze_audio(test_audio)
        
        return {
            "status": "healthy",
            "stt": "ok" if stt_result else "failed",
            "tts": "ok" if tts_result else "failed",
            "audio_analysis": "ok" if analysis_result else "failed"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

## 📞 Yordam va Qo'llab-quvvatlash

### Debug Information

```python
def get_system_info():
    import platform
    import sys
    
    return {
        "platform": platform.platform(),
        "python_version": sys.version,
        "voice_features_version": "1.0.0",
        "supported_providers": {
            "stt": [p.value for p in STTProvider],
            "tts": [p.value for p in TTSProvider]
        },
        "supported_languages": voice_features.get_supported_languages(),
        "available_voices": tts_engine.get_available_voices()
    }
```

### Troubleshooting

#### Muammolari hal qilish

1. **STT tanimaslik xatoligi**:
   - Audio quality tekshirish
   - Language code to'g'riligini tekshirish
   - Provider key validatsiyasini tekshirish

2. **TTS audio chiqmasligi**:
   - Voice settings tekshirish
   - Text encoding tekshirish
   - Audio device tekshirish

3. **Speaker identification xatosi**:
   - Training samples sonini tekshirish (minimum 5 ta)
   - Audio quality tekshirish
   - User profile mavjudligini tekshirish

4. **Performance muammolari**:
   - Audio chunk size ni kamaytirish
   - Async operations ishlatish
   - Caching yoqish

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| VF001 | STT service unavailable | Provider key tekshirish |
| VF002 | TTS service unavailable | Audio device tekshirish |
| VF003 | Audio format not supported | Format conversion qilish |
| VF004 | Speaker not found | User profile train qilish |
| VF005 | Low audio quality | Enhancement qilish |

---

**Orion Starline AI Team**  
**Version**: 1.0.0  
**Date**: 2025-11-05  
**License**: Proprietary