"""
STT & TTS Module
================

Bu modul Speech-to-Text va Text-to-Speech funksiyalarini ta'minlaydi:
- Google STT
- OpenAI Whisper
- Web Speech API
- Google TTS
- Amazon Polly
- Azure Cognitive Services
- Multi-language support
- Real-time processing

Author: Orion Starline AI Team
Date: 2025-11-05
"""

import asyncio
import json
import logging
import requests
import tempfile
import os
import base64
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import time
import wave
import io
import numpy as np
import speech_recognition as sr
import pyttsx3
import pyaudio
from pathlib import Path

# Voice features import
from voice_features import Language, VoiceEmotion

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class STTProvider(Enum):
    """STT provider types"""
    GOOGLE = "google"
    WHISPER = "whisper"
    WEB_SPEECH = "web_speech"
    AZURE = "azure"
    AWS_TRANSCRIBE = "aws_transcribe"

class TTSProvider(Enum):
    """TTS provider types"""
    GOOGLE = "google"
    AMAZON_POLLY = "amazon_polly"
    AZURE = "azure"
    ELEVENLABS = "elevenlabs"
    PYTTSX3 = "pyttsx3"

class AudioFormat(Enum):
    """Audio format types"""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"
    WEBM = "webm"

@dataclass
class STTResult:
    """STT natija ma'lumotlari"""
    text: str
    confidence: float
    language: str
    provider: str
    duration: float
    timestamp: datetime
    alternatives: List[Dict[str, Any]]

@dataclass
class TTSResult:
    """TTS natija ma'lumotlari"""
    audio_data: bytes
    provider: str
    language: str
    voice_id: str
    duration: float
    timestamp: datetime
    format: AudioFormat

@dataclass
class VoiceSettings:
    """Voice sozlamalari"""
    speed: float = 1.0
    pitch: float = 0.0
    volume: float = 1.0
    language: str = "uz-UZ"
    voice_id: Optional[str] = None
    emotion: VoiceEmotion = VoiceEmotion.NEUTRAL

class STTEngine:
    """
    Speech-to-Text Engine
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.providers = {
            STTProvider.GOOGLE: self._google_stt,
            STTProvider.WHISPER: self._whisper_stt,
            STTProvider.AZURE: self._azure_stt,
            STTProvider.AWS_TRANSCRIBE: self._aws_transcribe_stt
        }
        self.default_provider = STTProvider.GOOGLE
        self.language_models = {}
        
        # Provider settings
        self.google_api_key = None
        self.azure_key = None
        self.azure_region = None
        self.aws_access_key = None
        self.aws_secret_key = None
        
        logger.info("STT Engine initialized")
    
    def configure_provider(
        self, 
        provider: STTProvider, 
        settings: Dict[str, str]
    ):
        """Provider konfiguratsiyasi"""
        if provider == STTProvider.GOOGLE:
            self.google_api_key = settings.get('api_key')
        elif provider == STTProvider.AZURE:
            self.azure_key = settings.get('key')
            self.azure_region = settings.get('region', 'eastus')
        elif provider == STTProvider.AWS_TRANSCRIBE:
            self.aws_access_key = settings.get('access_key')
            self.aws_secret_key = settings.get('secret_key')
        
        logger.info(f"Provider {provider.value} configured")
    
    async def transcribe(
        self, 
        audio_data: bytes,
        language: str = "uz-UZ",
        provider: Optional[STTProvider] = None,
        **kwargs
    ) -> STTResult:
        """
        Audio ni matn ga o'tkazish
        
        Args:
            audio_data: Audio fayl ma'lumotlari
            language: Til kodi
            provider: STT provider
            **kwargs: Qo'shimcha parametrlar
            
        Returns:
            STTResult: Tanish natijasi
        """
        if provider is None:
            provider = self.default_provider
        
        if provider not in self.providers:
            raise ValueError(f"Provider {provider.value} not supported")
        
        start_time = time.time()
        try:
            result = await self.providers[provider](audio_data, language, **kwargs)
            
            duration = time.time() - start_time
            result.duration = duration
            result.timestamp = datetime.now()
            result.provider = provider.value
            
            logger.info(f"STT completed: {len(result.text)} chars, confidence: {result.confidence}")
            return result
            
        except Exception as e:
            logger.error(f"STT error: {e}")
            duration = time.time() - start_time
            return STTResult(
                text="",
                confidence=0.0,
                language=language,
                provider=provider.value,
                duration=duration,
                timestamp=datetime.now(),
                alternatives=[]
            )
    
    async def _google_stt(
        self, 
        audio_data: bytes, 
        language: str,
        **kwargs
    ) -> STTResult:
        """Google STT provider"""
        try:
            with sr.AudioFile(io.BytesIO(audio_data)) as source:
                audio = self.recognizer.record(source)
            
            # Offline recognition (pocketsphinx)
            text = self.recognizer.recognize_sphinx(audio, language=language)
            
            return STTResult(
                text=text,
                confidence=0.7,
                language=language,
                provider="google",
                duration=0.0,
                timestamp=datetime.now(),
                alternatives=[]
            )
            
        except sr.UnknownValueError:
            return STTResult(
                text="",
                confidence=0.0,
                language=language,
                provider="google",
                duration=0.0,
                timestamp=datetime.now(),
                alternatives=[]
            )
        except Exception as e:
            logger.error(f"Google STT error: {e}")
            return STTResult(
                text="",
                confidence=0.0,
                language=language,
                provider="google",
                duration=0.0,
                timestamp=datetime.now(),
                alternatives=[]
            )
    
    async def _whisper_stt(
        self, 
        audio_data: bytes, 
        language: str,
        **kwargs
    ) -> STTResult:
        """OpenAI Whisper STT"""
        try:
            # Hozircha placeholder implementatsiya
            # Real implementation would use OpenAI Whisper API
            
            # Faylni saqlash
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_file_path = tmp_file.name
            
            # Mock Whisper response
            text = "Whisper transcription result"
            
            # Cleanup
            os.unlink(tmp_file_path)
            
            return STTResult(
                text=text,
                confidence=0.9,
                language=language,
                provider="whisper",
                duration=0.0,
                timestamp=datetime.now(),
                alternatives=[]
            )
            
        except Exception as e:
            logger.error(f"Whisper STT error: {e}")
            return STTResult(
                text="",
                confidence=0.0,
                language=language,
                provider="whisper",
                duration=0.0,
                timestamp=datetime.now(),
                alternatives=[]
            )
    
    async def _azure_stt(
        self, 
        audio_data: bytes, 
        language: str,
        **kwargs
    ) -> STTResult:
        """Azure Speech-to-Text"""
        try:
            if not self.azure_key:
                raise ValueError("Azure key not configured")
            
            # Azure Speech API call (placeholder)
            text = "Azure STT transcription"
            
            return STTResult(
                text=text,
                confidence=0.85,
                language=language,
                provider="azure",
                duration=0.0,
                timestamp=datetime.now(),
                alternatives=[]
            )
            
        except Exception as e:
            logger.error(f"Azure STT error: {e}")
            return STTResult(
                text="",
                confidence=0.0,
                language=language,
                provider="azure",
                duration=0.0,
                timestamp=datetime.now(),
                alternatives=[]
            )
    
    async def _aws_transcribe_stt(
        self, 
        audio_data: bytes, 
        language: str,
        **kwargs
    ) -> STTResult:
        """AWS Transcribe STT"""
        try:
            if not self.aws_access_key:
                raise ValueError("AWS credentials not configured")
            
            # AWS Transcribe API call (placeholder)
            text = "AWS Transcribe transcription"
            
            return STTResult(
                text=text,
                confidence=0.8,
                language=language,
                provider="aws_transcribe",
                duration=0.0,
                timestamp=datetime.now(),
                alternatives=[]
            )
            
        except Exception as e:
            logger.error(f"AWS Transcribe STT error: {e}")
            return STTResult(
                text="",
                confidence=0.0,
                language=language,
                provider="aws_transcribe",
                duration=0.0,
                timestamp=datetime.now(),
                alternatives=[]
            )

class TTSEngine:
    """
    Text-to-Speech Engine
    """
    
    def __init__(self):
        self.pyttsx3_engine = pyttsx3.init()
        self.providers = {
            TTSProvider.GOOGLE: self._google_tts,
            TTSProvider.AMAZON_POLLY: self._amazon_polly_tts,
            TTSProvider.AZURE: self._azure_tts,
            TTSProvider.PYTTSX3: self._pyttsx3_tts,
            TTSProvider.ELEVENLABS: self._elevenlabs_tts
        }
        self.default_provider = TTSProvider.PYTTSX3
        
        # Provider settings
        self.google_api_key = None
        self.amazon_access_key = None
        self.amazon_secret_key = None
        self.azure_key = None
        self.azure_region = None
        self.elevenlabs_key = None
        
        # Voice settings
        self.voices = self._load_voices()
        self.default_voice = self.voices.get('uzbek', {}).get('id')
        
        logger.info("TTS Engine initialized")
    
    def _load_voices(self) -> Dict[str, Dict[str, Any]]:
        """Mavjud ovozlarni yuklash"""
        voices = {}
        
        try:
            voice_list = self.pyttsx3_engine.getProperty('voices')
            for voice in voice_list:
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': [voice.languages] if hasattr(voice, 'languages') else [],
                    'gender': 'unknown',
                    'age': 'unknown'
                }
                
                # Voice classification
                if 'russian' in voice.name.lower():
                    voices['russian'] = voice_info
                elif 'uzbek' in voice.name.lower():
                    voices['uzbek'] = voice_info
                else:
                    voices['default'] = voice_info
                    
        except Exception as e:
            logger.error(f"Voice loading error: {e}")
            voices['default'] = {'id': '', 'name': 'Default', 'gender': 'unknown'}
        
        return voices
    
    def configure_provider(
        self, 
        provider: TTSProvider, 
        settings: Dict[str, str]
    ):
        """Provider konfiguratsiyasi"""
        if provider == TTSProvider.GOOGLE:
            self.google_api_key = settings.get('api_key')
        elif provider == TTSProvider.AMAZON_POLLY:
            self.amazon_access_key = settings.get('access_key')
            self.amazon_secret_key = settings.get('secret_key')
        elif provider == TTSProvider.AZURE:
            self.azure_key = settings.get('key')
            self.azure_region = settings.get('region', 'eastus')
        elif provider == TTSProvider.ELEVENLABS:
            self.elevenlabs_key = settings.get('key')
        
        logger.info(f"TTS Provider {provider.value} configured")
    
    async def synthesize(
        self, 
        text: str,
        voice_settings: VoiceSettings,
        provider: Optional[TTSProvider] = None,
        **kwargs
    ) -> TTSResult:
        """
        Matnni audio ga o'tkazish
        
        Args:
            text: Matn
            voice_settings: Voice sozlamalari
            provider: TTS provider
            **kwargs: Qo'shimcha parametrlar
            
        Returns:
            TTSResult: Audio natijasi
        """
        if provider is None:
            provider = self.default_provider
        
        if provider not in self.providers:
            raise ValueError(f"Provider {provider.value} not supported")
        
        start_time = time.time()
        try:
            result = await self.providers[provider](text, voice_settings, **kwargs)
            
            duration = time.time() - start_time
            result.duration = duration
            result.timestamp = datetime.now()
            result.provider = provider.value
            
            logger.info(f"TTS completed: {len(result.audio_data)} bytes, duration: {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            duration = time.time() - start_time
            return TTSResult(
                audio_data=b"",
                provider=provider.value,
                language=voice_settings.language,
                voice_id=voice_settings.voice_id or "",
                duration=duration,
                timestamp=datetime.now(),
                format=AudioFormat.WAV
            )
    
    async def _google_tts(
        self, 
        text: str, 
        voice_settings: VoiceSettings,
        **kwargs
    ) -> TTSResult:
        """Google TTS"""
        try:
            # Google TTS API call (placeholder)
            # Real implementation would use Google Cloud TTS API
            
            # Fallback to pyttsx3
            return await self._pyttsx3_tts(text, voice_settings)
            
        except Exception as e:
            logger.error(f"Google TTS error: {e}")
            raise
    
    async def _amazon_polly_tts(
        self, 
        text: str, 
        voice_settings: VoiceSettings,
        **kwargs
    ) -> TTSResult:
        """Amazon Polly TTS"""
        try:
            if not self.amazon_access_key:
                raise ValueError("Amazon Polly credentials not configured")
            
            # Amazon Polly API call (placeholder)
            audio_data = b"Amazon Polly audio data"
            
            return TTSResult(
                audio_data=audio_data,
                provider="amazon_polly",
                language=voice_settings.language,
                voice_id=voice_settings.voice_id or "standard",
                duration=0.0,
                timestamp=datetime.now(),
                format=AudioFormat.MP3
            )
            
        except Exception as e:
            logger.error(f"Amazon Polly TTS error: {e}")
            raise
    
    async def _azure_tts(
        self, 
        text: str, 
        voice_settings: VoiceSettings,
        **kwargs
    ) -> TTSResult:
        """Azure TTS"""
        try:
            if not self.azure_key:
                raise ValueError("Azure TTS credentials not configured")
            
            # Azure TTS API call (placeholder)
            audio_data = b"Azure TTS audio data"
            
            return TTSResult(
                audio_data=audio_data,
                provider="azure",
                language=voice_settings.language,
                voice_id=voice_settings.voice_id or "standard",
                duration=0.0,
                timestamp=datetime.now(),
                format=AudioFormat.WAV
            )
            
        except Exception as e:
            logger.error(f"Azure TTS error: {e}")
            raise
    
    async def _elevenlabs_tts(
        self, 
        text: str, 
        voice_settings: VoiceSettings,
        **kwargs
    ) -> TTSResult:
        """ElevenLabs TTS"""
        try:
            if not self.elevenlabs_key:
                raise ValueError("ElevenLabs key not configured")
            
            # ElevenLabs API call (placeholder)
            audio_data = b"ElevenLabs TTS audio data"
            
            return TTSResult(
                audio_data=audio_data,
                provider="elevenlabs",
                language=voice_settings.language,
                voice_id=voice_settings.voice_id or "default",
                duration=0.0,
                timestamp=datetime.now(),
                format=AudioFormat.MP3
            )
            
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}")
            raise
    
    async def _pyttsx3_tts(
        self, 
        text: str, 
        voice_settings: VoiceSettings,
        **kwargs
    ) -> TTSResult:
        """PyTTSx3 TTS (offline)"""
        try:
            # Voice settings
            engine = self.pyttsx3_engine
            engine.setProperty('rate', int(150 * voice_settings.speed))
            engine.setProperty('volume', voice_settings.volume)
            
            # Voice selection
            if voice_settings.voice_id:
                engine.setProperty('voice', voice_settings.voice_id)
            elif self.default_voice:
                engine.setProperty('voice', self.default_voice)
            
            # Temporary file for audio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                engine.save_to_file(text, tmp_file.name)
                engine.runAndWait()
                
                # Audio data o'qish
                with open(tmp_file.name, 'rb') as audio_file:
                    audio_data = audio_file.read()
                
                os.unlink(tmp_file.name)
            
            return TTSResult(
                audio_data=audio_data,
                provider="pyttsx3",
                language=voice_settings.language,
                voice_id=voice_settings.voice_id or self.default_voice or "",
                duration=0.0,
                timestamp=datetime.now(),
                format=AudioFormat.WAV
            )
            
        except Exception as e:
            logger.error(f"PyTTSx3 TTS error: {e}")
            raise
    
    def get_available_voices(self, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Mavjud ovozlar ro'yxati"""
        voices = []
        
        for lang, voice_info in self.voices.items():
            if not language or lang == language:
                voices.append({
                    'id': voice_info['id'],
                    'name': voice_info['name'],
                    'language': lang,
                    'gender': voice_info['gender'],
                    'age': voice_info['age']
                })
        
        return voices
    
    def estimate_audio_duration(self, text: str, speed: float = 1.0) -> float:
        """Audio davomiyligini baholash"""
        # O'rtacha 150 so'z daqiqasiga
        words_per_minute = 150 * speed
        words_count = len(text.split())
        duration_minutes = words_count / words_per_minute
        return duration_minutes * 60  # seconds

class StreamingSTT:
    """
    Real-time Streaming STT
    """
    
    def __init__(self, stt_engine: STTEngine):
        self.stt_engine = stt_engine
        self.audio_queue = queue.Queue()
        self.is_streaming = False
        self.stream_thread = None
        self.callback = None
        
    def start_streaming(
        self, 
        callback,
        language: str = "uz-UZ",
        provider: Optional[STTProvider] = None
    ):
        """Streaming ni boshlash"""
        self.callback = callback
        self.is_streaming = True
        
        def stream_worker():
            while self.is_streaming:
                try:
                    audio_data = self.audio_queue.get(timeout=1)
                    if audio_data:
                        # Async STT processing
                        asyncio.create_task(
                            self._process_audio_stream(audio_data, language, provider)
                        )
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Stream processing error: {e}")
        
        self.stream_thread = threading.Thread(target=stream_worker, daemon=True)
        self.stream_thread.start()
        
        logger.info("Streaming STT started")
    
    def stop_streaming(self):
        """Streaming ni to'xtatish"""
        self.is_streaming = False
        if self.stream_thread:
            self.stream_thread.join()
        logger.info("Streaming STT stopped")
    
    def add_audio_data(self, audio_data: bytes):
        """Audio ma'lumotlarni qo'shish"""
        if self.is_streaming:
            self.audio_queue.put(audio_data)
    
    async def _process_audio_stream(
        self, 
        audio_data: bytes, 
        language: str,
        provider: Optional[STTProvider]
    ):
        """Audio stream qayta ishlash"""
        try:
            result = await self.stt_engine.transcribe(
                audio_data, 
                language=language, 
                provider=provider
            )
            
            if result.text and self.callback:
                self.callback(result)
                
        except Exception as e:
            logger.error(f"Stream processing error: {e}")

class StreamingTTS:
    """
    Real-time Streaming TTS
    """
    
    def __init__(self, tts_engine: TTSEngine):
        self.tts_engine = tts_engine
        self.text_queue = queue.Queue()
        self.is_streaming = False
        self.stream_thread = None
        self.callback = None
        
    def start_streaming(
        self, 
        callback,
        voice_settings: VoiceSettings,
        provider: Optional[TTSProvider] = None
    ):
        """Streaming ni boshlash"""
        self.callback = callback
        self.is_streaming = True
        
        def stream_worker():
            while self.is_streaming:
                try:
                    text_data = self.text_queue.get(timeout=1)
                    if text_data:
                        # Async TTS processing
                        asyncio.create_task(
                            self._process_text_stream(text_data, voice_settings, provider)
                        )
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"TTS stream processing error: {e}")
        
        self.stream_thread = threading.Thread(target=stream_worker, daemon=True)
        self.stream_thread.start()
        
        logger.info("Streaming TTS started")
    
    def stop_streaming(self):
        """Streaming ni to'xtatish"""
        self.is_streaming = False
        if self.stream_thread:
            self.stream_thread.join()
        logger.info("Streaming TTS stopped")
    
    def add_text(self, text: str):
        """Matn qo'shish"""
        if self.is_streaming:
            self.text_queue.put(text)
    
    async def _process_text_stream(
        self, 
        text: str, 
        voice_settings: VoiceSettings,
        provider: Optional[TTSProvider]
    ):
        """Text stream qayta ishlash"""
        try:
            result = await self.tts_engine.synthesize(
                text, 
                voice_settings=voice_settings, 
                provider=provider
            )
            
            if result.audio_data and self.callback:
                self.callback(result)
                
        except Exception as e:
            logger.error(f"TTS stream processing error: {e}")

# Global instances
stt_engine = STTEngine()
tts_engine = TTSEngine()

# Helper functions
async def transcribe_audio(
    audio_data: bytes, 
    language: str = "uz-UZ", 
    provider: STTProvider = STTProvider.GOOGLE
) -> STTResult:
    """STT helper function"""
    return await stt_engine.transcribe(audio_data, language, provider)

async def synthesize_speech(
    text: str, 
    voice_settings: VoiceSettings,
    provider: TTSProvider = TTSProvider.PYTTSX3
) -> TTSResult:
    """TTS helper function"""
    return await tts_engine.synthesize(text, voice_settings, provider)

def get_streaming_stt() -> StreamingSTT:
    """Streaming STT instance"""
    return StreamingSTT(stt_engine)

def get_streaming_tts() -> StreamingTTS:
    """Streaming TTS instance"""
    return StreamingTTS(tts_engine)

def create_voice_settings(
    language: str = "uz-UZ",
    speed: float = 1.0,
    volume: float = 1.0,
    voice_id: Optional[str] = None
) -> VoiceSettings:
    """Voice settings yaratish"""
    return VoiceSettings(
        language=language,
        speed=speed,
        volume=volume,
        voice_id=voice_id
    )

if __name__ == "__main__":
    # Test functions
    print("STT & TTS Engine Test")
    print("======================")
    
    # STT Test
    print("STT Provider Test:")
    providers = [p.value for p in STTProvider]
    for provider in providers:
        print(f"- {provider}")
    
    # TTS Test
    print("\nTTS Provider Test:")
    tts_providers = [p.value for p in TTSProvider]
    for provider in tts_providers:
        print(f"- {provider}")
    
    # Voices Test
    print("\nAvailable Voices Test:")
    voices = tts_engine.get_available_voices()
    for voice in voices:
        print(f"- {voice['name']} ({voice['language']}) - {voice['id']}")
    
    # Voice Settings Test
    print("\nVoice Settings Test:")
    settings = create_voice_settings(language="uz-UZ", speed=1.2, volume=0.8)
    print(f"- Language: {settings.language}")
    print(f"- Speed: {settings.speed}")
    print(f"- Volume: {settings.volume}")
    
    # Duration estimation
    sample_text = "Salom, bu test matni"
    duration = tts_engine.estimate_audio_duration(sample_text, settings.speed)
    print(f"- Estimated duration: {duration:.2f} seconds")
    
    print("\nSTT & TTS module loaded successfully!")