"""
Voice & Audio Features Module
============================

Bu modul voice/audio funksiyalarini ta'minlaydi:
- Speech-to-Text (STT) funksiyalari
- Text-to-Speech (TTS) funksiyalari
- Audio tahlil va sentiment
- Trading voice commands
- Ko'p tilli qo'llab-quvvatlash
- Real-time voice processing

Author: Orion Starline AI Team
Date: 2025-11-05
"""

import asyncio
import json
import logging
import numpy as np
import speech_recognition as sr
import pyttsx3
import pyaudio
import wave
import tempfile
import os
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import time
from collections import deque, defaultdict
import requests
import re
from pathlib import Path

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Language(Enum):
    """Tillar ro'yxati"""
    UZBEK = "uz-UZ"
    ENGLISH = "en-US" 
    RUSSIAN = "ru-RU"
    CHINESE = "zh-CN"
    JAPANESE = "ja-JP"

class VoiceEmotion(Enum):
    """Emotsiya turi"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    SURPRISED = "surprised"
    EXCITED = "excited"

class VoiceCommandType(Enum):
    """Voice command turlari"""
    TRADING = "trading"
    ANALYSIS = "analysis"
    PORTFOLIO = "portfolio"
    NEWS = "news"
    SETTINGS = "settings"
    HELP = "help"
    GENERAL = "general"

@dataclass
class VoiceCommand:
    """Voice command ma'lumotlari"""
    command: str
    intent: str
    parameters: Dict[str, Any]
    confidence: float
    timestamp: datetime
    language: Language
    emotion: VoiceEmotion
    response: str

@dataclass
class AudioFeatures:
    """Audio xususiyatlari"""
    rms: float
    zero_crossings: int
    spectral_centroid: float
    spectral_bandwidth: float
    rolloff: float
    mfcc_features: List[float]
    chroma_features: List[float]
    mel_spectrogram: List[float]

@dataclass
class VoiceAnalysis:
    """Voice tahlil natijalari"""
    text: str
    sentiment: float
    emotion: VoiceEmotion
    confidence: float
    language: Language
    speaker_id: Optional[str]
    audio_quality: float

class VoiceFeatures:
    """
    Voice & Audio Features asosiy klassi
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.voice_commands = {}
        self.command_patterns = {}
        self.language_models = {}
        self.user_profiles = {}
        self.voice_cache = {}
        
        # Audio processing settings
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.channels = 1
        
        # Trading command patterns
        self.trading_patterns = {
            'buy': [
                r'buy (.+) at (\d+\.?\d*)',
                r'purchase (.+) at (\d+\.?\d*)',
                r'xarid (.+) (\d+\.?\d*) narxda'
            ],
            'sell': [
                r'sell (.+) at (\d+\.?\d*)',
                r' Sotuv (.+) (\d+\.?\d*) narxda'
            ],
            'price': [
                r'show me (.+) price',
                r'(.+) narxi qancha',
                r'what is the price of (.+)'
            ],
            'analysis': [
                r'analyze (.+) market',
                r'(.+) bozor tahlil',
                r'technical analysis (.+)'
            ]
        }
        
        self._initialize_engines()
        self._load_command_patterns()
        logger.info("VoiceFeatures initialized successfully")
    
    def _initialize_engines(self):
        """TTS va STT motorlarni ishga tushirish"""
        try:
            # TTS engine settings
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # O'zbek uchun eng yaqin ovozni tanlash
                for voice in voices:
                    if 'russian' in voice.name.lower() or 'ru' in voice.id:
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                
            # TTS tezlik va ovoz balandligi
            self.tts_engine.setProperty('rate', 180)  # Tezlik
            self.tts_engine.setProperty('volume', 0.8)  # Balandlik
            
            logger.info("TTS engine initialized")
        except Exception as e:
            logger.error(f"Engine initialization error: {e}")
    
    def _load_command_patterns(self):
        """Command patternlarni yuklash"""
        patterns = {
            'uzbek': {
                'trading': [
                    r'(.+) sotib ol (\d+\.?\d*) narxda',
                    r'(.+) sotish (\d+\.?\d*) narxda',
                    r'(.+) narxi qancha',
                    r'(.+) bozor tahlil',
                    r'portfel holat',
                    r'risk baholash'
                ],
                'general': [
                    r'salom',
                    r'yordam ber',
                    r'status ko\'r',
                    r'xulosa'
                ]
            },
            'english': {
                'trading': [
                    r'buy (.+) at (\d+\.?\d*)',
                    r'sell (.+) at (\d+\.?\d*)',
                    r'show me (.+) price',
                    r'analyze (.+) market',
                    r'portfolio status',
                    r'risk assessment'
                ],
                'general': [
                    r'hello',
                    r'help',
                    r'status',
                    r'summary'
                ]
            },
            'russian': {
                'trading': [
                    r'купить (.+) по (\d+\.?\d*)',
                    r'продать (.+) по (\d+\.?\d*)',
                    r'цена (.+)',
                    r'анализ (.+) рынок',
                    r'статус портфель',
                    r'оценка риск'
                ],
                'general': [
                    r'привет',
                    r'помощь',
                    r'статус',
                    r'итоги'
                ]
            }
        }
        
        self.command_patterns = patterns
        logger.info("Command patterns loaded")
    
    async def speech_to_text(
        self, 
        audio_data: bytes, 
        language: Language = Language.UZBEK,
        use_google: bool = True,
        use_whisper: bool = False
    ) -> str:
        """
        Speech-to-Text funksiyasi
        
        Args:
            audio_data: Audio fayl ma'lumotlari
            language: Til tanlovi
            use_google: Google STT ishlatish
            use_whisper: OpenAI Whisper ishlatish
            
        Returns:
            str: Tanilgan matn
        """
        try:
            # Audio ma'lumotlarni saqlash
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_file_path = tmp_file.name
            
            # Audio faylni yuklash
            with sr.AudioFile(tmp_file_path) as source:
                audio = self.recognizer.record(source)
            
            # O'zbek tili uchun
            if language == Language.UZBEK:
                text = self._recognize_uzbek(audio)
            # Ingliz tili uchun
            elif language == Language.ENGLISH:
                if use_google:
                    text = self.recognizer.recognize_google(audio, language='en-US')
                elif use_whisper:
                    text = await self._recognize_whisper(audio_data)
                else:
                    text = self.recognizer.recognize_sphinx(audio, language='en-US')
            # Rus tili uchun
            elif language == Language.RUSSIAN:
                if use_google:
                    text = self.recognizer.recognize_google(audio, language='ru-RU')
                else:
                    text = self.recognizer.recognize_sphinx(audio, language='ru-RU')
            else:
                text = self.recognizer.recognize_google(audio, language='en-US')
            
            # Vaqtinchalik faylni o'chirish
            os.unlink(tmp_file_path)
            
            logger.info(f"STT result: {text}")
            return text
            
        except sr.UnknownValueError:
            logger.warning("Audio tanilmadi")
            return ""
        except sr.RequestError as e:
            logger.error(f"STT service error: {e}")
            return ""
        except Exception as e:
            logger.error(f"STT error: {e}")
            return ""
    
    def _recognize_uzbek(self, audio) -> str:
        """O'zbek tili uchun tanish"""
        try:
            # Google STT bilan o'zbek tili (ru-RU sifatida)
            return self.recognizer.recognize_google(audio, language='ru-RU')
        except:
            try:
                # Sphinx fallback
                return self.recognizer.recognize_sphinx(audio, language='ru-RU')
            except:
                return ""
    
    async def _recognize_whisper(self, audio_data: bytes) -> str:
        """OpenAI Whisper orqali tanish"""
        try:
            # Whisper API chaqirish (placeholder)
            # Hozircha mock implementatsiya
            return "Whisper text recognition"
        except Exception as e:
            logger.error(f"Whisper error: {e}")
            return ""
    
    def text_to_speech(
        self, 
        text: str, 
        language: Language = Language.UZBEK,
        speed: float = 1.0,
        volume: float = 1.0
    ) -> bytes:
        """
        Text-to-Speech funksiyasi
        
        Args:
            text: Matn
            language: Til
            speed: Tezlik (0.5-2.0)
            volume: Balandlik (0.0-1.0)
            
        Returns:
            bytes: Audio fayl ma'lumotlari
        """
        try:
            # TTS settings
            self.tts_engine.setProperty('rate', int(180 * speed))
            self.tts_engine.setProperty('volume', volume)
            
            # O'zbek tili uchun voice tanlashi
            if language == Language.UZBEK:
                self._set_voice_for_language('uzbek')
            elif language == Language.RUSSIAN:
                self._set_voice_for_language('russian')
            elif language == Language.ENGLISH:
                self._set_voice_for_language('english')
            
            # Matnni audio ga o'tkazish
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                self.tts_engine.save_to_file(text, tmp_file.name)
                self.tts_engine.runAndWait()
                
                # Audio faylni o'qish
                with open(tmp_file.name, 'rb') as audio_file:
                    audio_data = audio_file.read()
                
                os.unlink(tmp_file.name)
            
            logger.info(f"TTS completed for text: {text[:50]}...")
            return audio_data
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return b""
    
    def _set_voice_for_language(self, language: str):
        """Til uchun voice tanlash"""
        try:
            voices = self.tts_engine.getProperty('voices')
            if voices:
                for voice in voices:
                    if language.lower() in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        return
                
                # Default voice
                if voices:
                    self.tts_engine.setProperty('voice', voices[0].id)
        except Exception as e:
            logger.error(f"Voice setting error: {e}")
    
    def detect_language(self, text: str) -> Language:
        """Matndan tilni aniqlash"""
        try:
            # O'zbek so'zlari
            uzbek_words = ['salom', 'qanday', 'kim', 'qayerda', 'qachon', 'nima', 'qanday']
            # Rus so'zlari  
            russian_words = ['привет', 'как', 'кто', 'где', 'когда', 'что']
            # Ingliz so'zlari
            english_words = ['hello', 'how', 'who', 'where', 'when', 'what']
            
            text_lower = text.lower()
            
            uzbek_count = sum(1 for word in uzbek_words if word in text_lower)
            russian_count = sum(1 for word in russian_words if word in text_lower)
            english_count = sum(1 for word in english_words if word in text_lower)
            
            if uzbek_count > russian_count and uzbek_count > english_count:
                return Language.UZBEK
            elif russian_count > english_count:
                return Language.RUSSIAN
            else:
                return Language.ENGLISH
                
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return Language.ENGLISH
    
    def extract_trading_command(self, text: str) -> Optional[VoiceCommand]:
        """Trading command ni parse qilish"""
        try:
            language = self.detect_language(text)
            lang_key = language.value.split('-')[0]  # 'uz-UZ' -> 'uz'
            
            if lang_key not in self.command_patterns:
                return None
            
            patterns = self.command_patterns[lang_key].get('trading', [])
            
            for pattern in patterns:
                match = re.search(pattern, text.lower())
                if match:
                    groups = match.groups()
                    
                    if 'buy' in pattern:
                        return VoiceCommand(
                            command=text,
                            intent='buy',
                            parameters={
                                'symbol': groups[0].strip() if groups else '',
                                'price': float(groups[1]) if len(groups) > 1 and groups[1] else None
                            },
                            confidence=0.9,
                            timestamp=datetime.now(),
                            language=language,
                            emotion=VoiceEmotion.NEUTRAL,
                            response="Buy order olinmoqda..."
                        )
                    elif 'sell' in pattern:
                        return VoiceCommand(
                            command=text,
                            intent='sell',
                            parameters={
                                'symbol': groups[0].strip() if groups else '',
                                'price': float(groups[1]) if len(groups) > 1 and groups[1] else None
                            },
                            confidence=0.9,
                            timestamp=datetime.now(),
                            language=language,
                            emotion=VoiceEmotion.NEUTRAL,
                            response="Sell order olinmoqda..."
                        )
                    elif 'price' in pattern:
                        return VoiceCommand(
                            command=text,
                            intent='price_check',
                            parameters={'symbol': groups[0].strip() if groups else ''},
                            confidence=0.85,
                            timestamp=datetime.now(),
                            language=language,
                            emotion=VoiceEmotion.NEUTRAL,
                            response="Narx tekshirilmoqda..."
                        )
                    elif 'analysis' in pattern:
                        return VoiceCommand(
                            command=text,
                            intent='market_analysis',
                            parameters={'symbol': groups[0].strip() if groups else ''},
                            confidence=0.8,
                            timestamp=datetime.now(),
                            language=language,
                            emotion=VoiceEmotion.NEUTRAL,
                            response="Bozor tahlil qilinmoqda..."
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"Command extraction error: {e}")
            return None
    
    async def process_voice_command(self, text: str) -> VoiceCommand:
        """Voice command ni qayta ishlash"""
        try:
            # Tilni aniqlash
            language = self.detect_language(text)
            
            # Command ni parse qilish
            command = self.extract_trading_command(text)
            
            if not command:
                # Umumiy command
                command = VoiceCommand(
                    command=text,
                    intent='general',
                    parameters={},
                    confidence=0.5,
                    timestamp=datetime.now(),
                    language=language,
                    emotion=VoiceEmotion.NEUTRAL,
                    response="Buyruq tushunilmadi"
                )
            
            logger.info(f"Processed voice command: {command.intent}")
            return command
            
        except Exception as e:
            logger.error(f"Voice command processing error: {e}")
            return VoiceCommand(
                command=text,
                intent='error',
                parameters={},
                confidence=0.0,
                timestamp=datetime.now(),
                language=Language.ENGLISH,
                emotion=VoiceEmotion.NEUTRAL,
                response="Xatolik yuz berdi"
            )
    
    def get_trading_responses(self, intent: str, language: Language) -> str:
        """Trading responses"""
        responses = {
            'buy': {
                'uzbek': 'Buy order muvaffaqiyatli olinmoqda...',
                'english': 'Buy order is being placed...',
                'russian': 'Заявка на покупку обрабатывается...'
            },
            'sell': {
                'uzbek': 'Sell order muvaffaqiyatli olinmoqda...',
                'english': 'Sell order is being placed...',
                'russian': 'Заявка на продажу обрабатывается...'
            },
            'price_check': {
                'uzbek': 'Narx ma\'lumotlari olinmoqda...',
                'english': 'Price information is being retrieved...',
                'russian': 'Информация о цене запрашивается...'
            },
            'market_analysis': {
                'uzbek': 'Bozor tahlil qilinmoqda...',
                'english': 'Market analysis is being performed...',
                'russian': 'Анализ рынка проводится...'
            }
        }
        
        lang_key = language.value.split('-')[0]
        return responses.get(intent, {}).get(lang_key, 'Response not found')
    
    def analyze_voice_sentiment(self, text: str) -> float:
        """Voice sentiment tahlil"""
        try:
            # O'zbek sentiment
            positive_words = ['yaxshi', 'zo\'r', 'mukammal', 'great', 'good', 'excellent', 'хорошо', 'отлично']
            negative_words = ['yomon', 'yomonroq', 'bad', 'worse', 'terrible', 'плохо', 'ужасно']
            neutral_words = ['normal', 'ok', 'ordinary', 'обычно', 'нормально']
            
            text_lower = text.lower()
            pos_count = sum(1 for word in positive_words if word in text_lower)
            neg_count = sum(1 for word in negative_words if word in text_lower)
            
            if pos_count > neg_count:
                return min(0.8, 0.5 + (pos_count * 0.2))
            elif neg_count > pos_count:
                return max(-0.8, -0.5 - (neg_count * 0.2))
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return 0.0
    
    def real_time_voice_processing(
        self, 
        audio_stream: queue.Queue, 
        callback=None
    ):
        """Real-time voice processing"""
        try:
            def process_audio():
                while True:
                    try:
                        audio_data = audio_stream.get(timeout=1)
                        if audio_data is None:
                            break
                        
                        # STT processing
                        text = self.speech_to_text(audio_data)
                        
                        if text and callback:
                            asyncio.create_task(callback(text))
                            
                    except queue.Empty:
                        continue
                    except Exception as e:
                        logger.error(f"Real-time processing error: {e}")
            
            # Audio processing thread
            thread = threading.Thread(target=process_audio, daemon=True)
            thread.start()
            
            logger.info("Real-time voice processing started")
            return thread
            
        except Exception as e:
            logger.error(f"Real-time processing setup error: {e}")
            return None
    
    def voice_activity_detection(self, audio_data: bytes) -> bool:
        """Voice activity detection"""
        try:
            # Audio format
            if len(audio_data) < 1024:
                return False
            
            # RMS (Root Mean Square) hisoblash
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_array**2))
            
            # Threshold (0.01 = 1% of max volume)
            threshold = 1000  # Adjust based on hardware
            return rms > threshold
            
        except Exception as e:
            logger.error(f"VAD error: {e}")
            return True  # Default to True for safety
    
    def create_user_voice_profile(self, user_id: str, voice_samples: List[bytes]) -> Dict[str, Any]:
        """User uchun voice profile yaratish"""
        try:
            features = []
            for sample in voice_samples:
                audio_features = self.extract_audio_features(sample)
                features.append(audio_features)
            
            profile = {
                'user_id': user_id,
                'voice_features': features,
                'created_at': datetime.now(),
                'language_preference': 'uzbek',
                'voice_commands': [],
                'emotion_patterns': {}
            }
            
            self.user_profiles[user_id] = profile
            logger.info(f"Voice profile created for user: {user_id}")
            
            return profile
            
        except Exception as e:
            logger.error(f"Voice profile creation error: {e}")
            return {}
    
    def extract_audio_features(self, audio_data: bytes) -> AudioFeatures:
        """Audio xususiyatlarini extraction"""
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Basic features
            rms = np.sqrt(np.mean(audio_array**2))
            zero_crossings = np.sum(np.diff(np.sign(audio_array)) != 0)
            
            # Placeholder for advanced features
            # In real implementation, use librosa or similar
            spectral_centroid = 0.0
            spectral_bandwidth = 0.0
            rolloff = 0.0
            mfcc_features = [0.0] * 13
            chroma_features = [0.0] * 12
            mel_spectrogram = [0.0] * 128
            
            return AudioFeatures(
                rms=rms,
                zero_crossings=zero_crossings,
                spectral_centroid=spectral_centroid,
                spectral_bandwidth=spectral_bandwidth,
                rolloff=rolloff,
                mfcc_features=mfcc_features,
                chroma_features=chroma_features,
                mel_spectrogram=mel_spectrogram
            )
            
        except Exception as e:
            logger.error(f"Audio feature extraction error: {e}")
            return AudioFeatures(0, 0, 0, 0, 0, [], [], [])
    
    def speaker_identification(self, audio_data: bytes) -> Optional[str]:
        """Speaker identification"""
        try:
            # Audio features extraction
            features = self.extract_audio_features(audio_data)
            
            # Compare with user profiles
            min_distance = float('inf')
            identified_user = None
            
            for user_id, profile in self.user_profiles.items():
                if 'voice_features' in profile and profile['voice_features']:
                    # Simple distance calculation (placeholder)
                    distance = abs(features.rms - profile['voice_features'][0].rms)
                    
                    if distance < min_distance and distance < 1000:  # Threshold
                        min_distance = distance
                        identified_user = user_id
            
            return identified_user
            
        except Exception as e:
            logger.error(f"Speaker identification error: {e}")
            return None
    
    async def voice_biometric_authentication(
        self, 
        audio_data: bytes, 
        user_id: str
    ) -> bool:
        """Voice biometric authentication"""
        try:
            if user_id not in self.user_profiles:
                return False
            
            # Speaker identification
            identified_user = self.speaker_identification(audio_data)
            
            if identified_user == user_id:
                logger.info(f"Voice authentication successful for user: {user_id}")
                return True
            else:
                logger.warning(f"Voice authentication failed for user: {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Voice biometric error: {e}")
            return False
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Qo'llab-quvvatlanadigan tillar"""
        languages = [
            {'code': 'uz-UZ', 'name': 'O\'zbek', 'native': 'O\'zbek'},
            {'code': 'en-US', 'name': 'English', 'native': 'English'},
            {'code': 'ru-RU', 'name': 'Русский', 'native': 'Русский'},
            {'code': 'zh-CN', 'name': '中文', 'native': '中文'},
            {'code': 'ja-JP', 'name': '日本語', 'native': '日本語'}
        ]
        return languages
    
    def get_trading_commands_sample(self) -> List[Dict[str, str]]:
        """Trading voice command namunalari"""
        commands = [
            {
                'command': 'Buy EURUSD at 1.1000',
                'intent': 'buy',
                'description': 'EURUSD sotib olish'
            },
            {
                'command': 'Bitcoin narxi qancha',
                'intent': 'price_check',
                'description': 'Bitcoin narxini tekshirish'
            },
            {
                'command': 'Portfolio holat ko\'rsat',
                'intent': 'portfolio_status',
                'description': 'Portfolio holat ko\'rsatish'
            },
            {
                'command': 'AAPL bozor tahlil',
                'intent': 'market_analysis',
                'description': 'AAPL bozor tahlili'
            }
        ]
        return commands
    
    def get_voice_emotions(self) -> List[Dict[str, str]]:
        """Qo'llab-quvvatlanadigan emotsiyalar"""
        emotions = [
            {'code': 'neutral', 'name': 'Neytral', 'description': 'Normal holat'},
            {'code': 'happy', 'name': 'Xursand', 'description': 'Xursandlik'},
            {'code': 'sad', 'name': 'G\'amgin', 'description': 'G\'amginlik'},
            {'code': 'angry', 'name': 'G\'azablangan', 'description': 'G\'azab'},
            {'code': 'excited', 'name': 'Hayajonlangan', 'description': 'Hayajon'},
            {'code': 'fearful', 'name': 'Qo\'rqqan', 'description': 'Qo\'rquv'},
            {'code': 'disgusted', 'name': 'Jirkanchi', 'description': 'Jirkanish'},
            {'code': 'surprised', 'name': 'Ajablangan', 'description': 'Ajablanish'}
        ]
        return emotions
    
    async def cleanup(self):
        """Resources ni tozalash"""
        try:
            self.tts_engine.stop()
            self.voice_cache.clear()
            logger.info("VoiceFeatures cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

# Global instance
voice_features = VoiceFeatures()

# Helper functions
async def speech_to_text(audio_data: bytes, language: Language = Language.UZBEK) -> str:
    """Helper function for STT"""
    return await voice_features.speech_to_text(audio_data, language)

def text_to_speech(text: str, language: Language = Language.UZBEK) -> bytes:
    """Helper function for TTS"""
    return voice_features.text_to_speech(text, language)

async def process_voice_command(text: str) -> VoiceCommand:
    """Helper function for voice command processing"""
    return await voice_features.process_voice_command(text)

def detect_language(text: str) -> Language:
    """Helper function for language detection"""
    return voice_features.detect_language(text)

def analyze_voice_sentiment(text: str) -> float:
    """Helper function for sentiment analysis"""
    return voice_features.analyze_voice_sentiment(text)

if __name__ == "__main__":
    # Test functions
    print("Voice Features Test")
    print("===================")
    
    # Language support
    languages = voice_features.get_supported_languages()
    print(f"Supported languages: {len(languages)}")
    for lang in languages:
        print(f"- {lang['name']} ({lang['native']})")
    
    # Trading commands sample
    commands = voice_features.get_trading_commands_sample()
    print(f"\nTrading commands sample: {len(commands)}")
    for cmd in commands:
        print(f"- {cmd['command']} -> {cmd['intent']}")
    
    # Emotions
    emotions = voice_features.get_voice_emotions()
    print(f"\nVoice emotions: {len(emotions)}")
    for emotion in emotions:
        print(f"- {emotion['name']} ({emotion['code']})")
    
    print("\nVoice Features module loaded successfully!")