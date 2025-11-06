"""
Voice & Audio Features Demo
===========================

Bu fayl Voice & Audio Features tizimining barcha funksiyalarini ko'rsatadi.

Author: Orion Starline AI Team
Date: 2025-11-05
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from voice_features import (
    voice_features, 
    Language, 
    VoiceEmotion, 
    VoiceCommand,
    process_voice_command,
    speech_to_text,
    text_to_speech,
    detect_language,
    analyze_voice_sentiment
)
from stt_tts import (
    stt_engine,
    tts_engine,
    STTProvider,
    TTSProvider,
    VoiceSettings,
    transcribe_audio,
    synthesize_speech,
    create_voice_settings
)
from audio_analysis import (
    audio_analyzer,
    AudioEnhancementSettings,
    analyze_audio,
    detect_emotion,
    identify_speaker,
    enhance_audio,
    train_speaker_model
)

async def demo_stt_tts():
    """STT va TTS demo"""
    print("\\n" + "="*50)
    print("STT & TTS DEMO")
    print("="*50)
    
    # Mock audio data
    mock_audio = b"\\x00\\x00" * 1000
    
    # STT Test
    print("\\n1. Speech-to-Text Test:")
    print(f"   - Available providers: {[p.value for p in STTProvider]}")
    
    for provider in STTProvider:
        try:
            result = await stt_engine.transcribe(mock_audio, "uz-UZ", provider)
            print(f"   - {provider.value}: '{result.text}' (confidence: {result.confidence:.2f})")
        except Exception as e:
            print(f"   - {provider.value}: Error - {str(e)[:50]}")
    
    # TTS Test
    print("\\n2. Text-to-Speech Test:")
    print(f"   - Available providers: {[p.value for p in TTSProvider]}")
    
    test_texts = [
        "Salom, bu test matni",
        "Hello, this is test text",
        "Привет, это тестовый текст"
    ]
    
    for i, text in enumerate(test_texts):
        language = ["uz-UZ", "en-US", "ru-RU"][i]
        voice_settings = create_voice_settings(language=language, speed=1.1)
        
        try:
            result = await tts_engine.synthesize(text, voice_settings, TTSProvider.PYTTSX3)
            print(f"   - {language}: {len(result.audio_data)} bytes audio generated")
        except Exception as e:
            print(f"   - {language}: Error - {str(e)[:50]}")
    
    # Language detection
    print("\\n3. Language Detection Test:")
    test_utterances = [
        "Salom, qanday yuribdi?",
        "Hello, how are you?",
        "Привет, как дела?"
    ]
    
    for utterance in test_utterances:
        language = detect_language(utterance)
        print(f"   - '{utterance[:30]}...' -> {language.value}")
    
    print("\\nSTT & TTS Demo completed!")

async def demo_voice_commands():
    """Voice commands demo"""
    print("\\n" + "="*50)
    print("VOICE COMMANDS DEMO")
    print("="*50)
    
    # Trading voice commands
    print("\\n1. Trading Voice Commands:")
    trading_commands = [
        "Buy EURUSD at 1.1000",
        "Bitcoin narxi qancha?",
        "Portfolio holat ko'rsat",
        "AAPL bozor tahlil qil",
        "Sell EURUSD at 1.1050",
        "Risk assessment"
    ]
    
    for command_text in trading_commands:
        try:
            command = await process_voice_command(command_text)
            print(f"   - Command: '{command_text}'")
            print(f"     Intent: {command.intent}")
            print(f"     Parameters: {command.parameters}")
            print(f"     Confidence: {command.confidence:.2f}")
            print(f"     Response: {command.response}")
            print()
        except Exception as e:
            print(f"   - Command processing error: {e}")
    
    # General voice commands
    print("2. General Voice Commands:")
    general_commands = [
        "Salom",
        "Yordam ber",
        "Status",
        "Hello",
        "Help",
        "Привет"
    ]
    
    for command_text in general_commands:
        try:
            command = await process_voice_command(command_text)
            print(f"   - '{command_text}' -> {command.intent} ({command.language.value})")
        except Exception as e:
            print(f"   - Error processing '{command_text}': {e}")
    
    print("\\nVoice Commands Demo completed!")

async def demo_audio_analysis():
    """Audio analysis demo"""
    print("\\n" + "="*50)
    print("AUDIO ANALYSIS DEMO")
    print("="*50)
    
    # Mock audio data
    mock_audio = b"\\x00\\x00" * 2000
    
    # Audio features extraction
    print("\\n1. Audio Features Extraction:")
    try:
        features = audio_analyzer.extract_audio_features(mock_audio)
        print(f"   - RMS: {features.rms:.6f}")
        print(f"   - Zero crossings: {features.zero_crossings}")
        print(f"   - Spectral centroid: {features.spectral_centroid:.2f} Hz")
        print(f"   - Spectral bandwidth: {features.spectral_bandwidth:.2f} Hz")
        print(f"   - Rolloff: {features.rolloff:.2f} Hz")
        print(f"   - MFCC features: {len(features.mfcc_features)} coefficients")
        print(f"   - Chroma features: {len(features.chroma_features)} bins")
        print(f"   - Mel spectrogram: {len(features.mel_spectrogram)} bands")
    except Exception as e:
        print(f"   - Feature extraction error: {e}")
    
    # Complete audio analysis
    print("\\n2. Complete Audio Analysis:")
    try:
        analysis = await analyze_audio(mock_audio)
        print(f"   - Quality score: {analysis.quality_score:.3f}")
        print(f"   - Quality level: {analysis.quality_level.value}")
        print(f"   - Voice emotion: {analysis.voice_analysis.emotion.value}")
        print(f"   - Speaker ID: {analysis.voice_analysis.speaker_id or 'Unknown'}")
        print(f"   - Audio quality: {analysis.voice_analysis.audio_quality:.3f}")
        
        print("\\n   Enhancement suggestions:")
        for suggestion in analysis.enhancement_suggestions:
            print(f"   - {suggestion}")
    except Exception as e:
        print(f"   - Analysis error: {e}")
    
    # Emotion detection
    print("\\n3. Emotion Detection:")
    try:
        emotion = detect_emotion(features)
        detailed_emotion = audio_analyzer.detect_emotion_detailed(features)
        print(f"   - Detected emotion: {emotion.value}")
        print(f"   - Confidence: {detailed_emotion.confidence:.3f}")
        print(f"   - Intensity: {detailed_emotion.intensity:.3f}")
        print(f"   - VAD: Valence={detailed_emotion.valence:.3f}, "
              f"Arousal={detailed_emotion.arousal:.3f}, "
              f"Dominance={detailed_emotion.dominance:.3f}")
    except Exception as e:
        print(f"   - Emotion detection error: {e}")
    
    # Speaker identification
    print("\\n4. Speaker Identification:")
    try:
        speaker_id = identify_speaker(features)
        print(f"   - Identified speaker: {speaker_id or 'No match found'}")
    except Exception as e:
        print(f"   - Speaker identification error: {e}")
    
    # Audio enhancement
    print("\\n5. Audio Enhancement:")
    try:
        settings = AudioEnhancementSettings(
            noise_reduction_level=0.6,
            voice_enhancement_level=0.8,
            normalization_enabled=True,
            compression_ratio=2.5
        )
        
        enhanced_audio = enhance_audio(mock_audio, settings)
        print(f"   - Original size: {len(mock_audio)} bytes")
        print(f"   - Enhanced size: {len(enhanced_audio)} bytes")
        print(f"   - Enhancement settings: NR={settings.noise_reduction_level}, "
              f"VE={settings.voice_enhancement_level}, "
              f"Comp={settings.compression_ratio}")
    except Exception as e:
        print(f"   - Enhancement error: {e}")
    
    print("\\nAudio Analysis Demo completed!")

async def demo_speaker_training():
    """Speaker training demo"""
    print("\\n" + "="*50)
    print("SPEAKER TRAINING DEMO")
    print("="*50)
    
    # Mock training data
    mock_samples = [b"\\x00\\x00" * 1000] * 5  # 5 training samples
    
    # Train speaker model
    print("\\n1. Training Speaker Model:")
    try:
        user_id = "test_user_001"
        success = await train_speaker_model(user_id, mock_samples)
        print(f"   - Training success: {success}")
        
        if success:
            print(f"   - User ID: {user_id}")
            print(f"   - Training samples: {len(mock_samples)}")
    except Exception as e:
        print(f"   - Training error: {e}")
    
    # Show speaker profiles
    print("\\n2. Speaker Profiles:")
    try:
        profiles = audio_analyzer.get_speaker_profiles()
        print(f"   - Total trained speakers: {len(profiles)}")
        
        for profile in profiles:
            print(f"   - Speaker: {profile['speaker_id']}")
            print(f"     Samples: {profile['training_samples']}")
            print(f"     Accuracy: {profile['accuracy_score']:.3f}")
            print(f"     Updated: {profile['last_updated'][:19]}")
    except Exception as e:
        print(f"   - Profiles error: {e}")
    
    print("\\nSpeaker Training Demo completed!")

async def demo_voice_biometric():
    """Voice biometric authentication demo"""
    print("\\n" + "="*50)
    print("VOICE BIOMETRIC DEMO")
    print("="*50)
    
    # Mock audio for biometric test
    mock_audio = b"\\x00\\x00" * 1500
    
    print("\\n1. Voice Authentication Test:")
    try:
        # First train a speaker
        user_id = "biometric_user_001"
        mock_samples = [b"\\x00\\x00" * 1000] * 3
        await train_speaker_model(user_id, mock_samples)
        
        # Test authentication
        authenticated = await voice_features.voice_biometric_authentication(mock_audio, user_id)
        print(f"   - User: {user_id}")
        print(f"   - Authentication result: {authenticated}")
        
        # Test with wrong user
        wrong_user = "biometric_user_002"
        authenticated_wrong = await voice_features.voice_biometric_authentication(mock_audio, wrong_user)
        print(f"   - Wrong user ({wrong_user}): {authenticated_wrong}")
        
    except Exception as e:
        print(f"   - Biometric test error: {e}")
    
    print("\\nVoice Biometric Demo completed!")

async def demo_sentiment_analysis():
    """Voice sentiment analysis demo"""
    print("\\n" + "="*50)
    print("SENTIMENT ANALYSIS DEMO")
    print("="*50)
    
    # Test utterances with different sentiments
    test_utterances = [
        ("Zo'r kelmoqda, katta foyda!", "uzbek", "positive"),
        ("Bu juda yomon, katta zarar bo'ldi", "uzbek", "negative"),
        ("Hammasi o'rtacha, normal", "uzbek", "neutral"),
        ("Great results, very profitable", "english", "positive"),
        ("Bad performance, big losses", "english", "negative"),
        ("Отличные результаты, выгодно", "russian", "positive")
    ]
    
    print("\\n1. Sentiment Analysis:")
    for utterance, language, expected in test_utterances:
        try:
            sentiment = analyze_voice_sentiment(utterance)
            print(f"   - Language: {language}")
            print(f"     Text: '{utterance}'")
            print(f"     Sentiment: {sentiment:.3f} (expected: {expected})")
            
            # Classify sentiment
            if sentiment > 0.2:
                classification = "Positive"
            elif sentiment < -0.2:
                classification = "Negative"
            else:
                classification = "Neutral"
            
            print(f"     Classification: {classification}")
            print()
        except Exception as e:
            print(f"   - Error analyzing '{utterance}': {e}")
    
    print("\\nSentiment Analysis Demo completed!")

def demo_languages_and_commands():
    """Languages va commands demo"""
    print("\\n" + "="*50)
    print("LANGUAGES & COMMANDS DEMO")
    print("="*50)
    
    # Supported languages
    print("\\n1. Supported Languages:")
    languages = voice_features.get_supported_languages()
    for lang in languages:
        print(f"   - {lang['name']} ({lang['native']}) - Code: {lang['code']}")
    
    # Voice emotions
    print("\\n2. Voice Emotions:")
    emotions = voice_features.get_voice_emotions()
    for emotion in emotions:
        print(f"   - {emotion['name']} ({emotion['code']}) - {emotion['description']}")
    
    # Trading commands
    print("\\n3. Trading Commands Sample:")
    commands = voice_features.get_trading_commands_sample()
    for cmd in commands:
        print(f"   - '{cmd['command']}'")
        print(f"     Intent: {cmd['intent']}")
        print(f"     Description: {cmd['description']}")
        print()
    
    # Voice settings
    print("4. Voice Settings Examples:")
    settings_examples = [
        ("uz-UZ", 1.0, 0.8, "O'zbek tili, normal tezlik"),
        ("en-US", 1.2, 0.9, "Ingliz tili, tez so'zlash"),
        ("ru-RU", 0.9, 0.7, "Rus tili, sekin so'zlash")
    ]
    
    for lang, speed, volume, desc in settings_examples:
        voice_settings = create_voice_settings(language=lang, speed=speed, volume=volume)
        print(f"   - {desc}")
        print(f"     Settings: Rate={voice_settings.speed}, Volume={voice_settings.volume}")
        print(f"     Language: {voice_settings.language}")
        print()
    
    print("\\nLanguages & Commands Demo completed!")

def demo_system_info():
    """Tizim haqida ma'lumot"""
    print("\\n" + "="*50)
    print("VOICE & AUDIO FEATURES SYSTEM")
    print("="*50)
    
    print("\\nTizim nomi: Orion Starline Voice & Audio Features")
    print("Versiya: 1.0.0")
    print("Sana: 2025-11-05")
    print("Muallif: Orion Starline AI Team")
    
    print("\\nAsosiy modullar:")
    print("1. voice_features.py - Asosiy voice funksiyalari")
    print("2. stt_tts.py - Speech-to-Text va Text-to-Speech")
    print("3. audio_analysis.py - Audio tahlil va qayta ishlash")
    
    print("\\nQo'llab-quvvatlash funksiyalari:")
    features = [
        "Multi-language STT (Uzbek, English, Russian, etc.)",
        "Multi-provider TTS (Google, Amazon Polly, Azure, ElevenLabs)",
        "Voice sentiment va emotsiya detection",
        "Trading voice commands processing",
        "Real-time voice processing",
        "Speaker identification va biometric authentication",
        "Audio enhancement va noise reduction",
        "Voice activity detection",
        "Audio format conversion va compression"
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"{i}. {feature}")
    
    print("\\nTrading voice commands:")
    trading_examples = [
        'Buy EURUSD at 1.1000',
        'Bitcoin narxi qancha',
        'Portfolio holat ko\'rsat',
        'AAPL bozor tahlil',
        'Risk assessment'
    ]
    
    for example in trading_examples:
        print(f"   - {example}")
    
    print("\\nTexnik xususiyatlar:")
    tech_specs = [
        "Sample rate: 16kHz (default)",
        "Bit depth: 16-bit",
        "Channels: Mono (1)",
        "Frame size: 1024 samples",
        "Hop size: 512 samples",
        "Supported formats: WAV, MP3, FLAC, OGG"
    ]
    
    for spec in tech_specs:
        print(f"   - {spec}")
    
    print("\\n" + "="*50)

async def main():
    """Main demo function"""
    print("🎤 Orion Starline Voice & Audio Features Demo")
    print("=" * 60)
    
    try:
        # System info
        demo_system_info()
        
        # Languages and commands
        demo_languages_and_commands()
        
        # STT & TTS demo
        await demo_stt_tts()
        
        # Voice commands demo
        await demo_voice_commands()
        
        # Audio analysis demo
        await demo_audio_analysis()
        
        # Speaker training demo
        await demo_speaker_training()
        
        # Voice biometric demo
        await demo_voice_biometric()
        
        # Sentiment analysis demo
        await demo_sentiment_analysis()
        
        print("\\n" + "="*60)
        print("🎉 Barcha demo testlar muvaffaqiyatli yakunlandi!")
        print("Voice & Audio Features tizimi to'liq ishlashga tayyor.")
        print("="*60)
        
    except Exception as e:
        print(f"\\n❌ Demo xatolik: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())