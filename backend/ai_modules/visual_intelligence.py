"""
Visual Intelligence Module - Orion Starline AI Trading System
============================================================

Bu modul vizual ma'lumotlarni tahlil qilish uchun mo'ljallangan AI tizimi.
Asosiy funksiyalar:
- Chart analysis - Technical patterns, candlestick patterns
- Technical pattern recognition - Head & Shoulders, Triangles, Flags
- Image-to-text (OCR) - Text extraction from charts, documents
- Visual signal detection - Chart signals, trend lines
- Diagram interpretation - Trading diagrams, flow charts
- PDF/document analysis - Financial reports, research papers
- Market microstructure analysis
- Volume profile analysis
- Support/resistance level detection

Author: Orion Starline AI Team
Version: 1.0.0
"""

import logging
import numpy as np
import cv2
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import base64
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy import ndimage, signal
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Import chart analysis and OCR modules
try:
    from .chart_analysis import (
        ChartAnalyzer, TechnicalPattern, CandlestickPattern,
        TrendLine, SupportResistance, VolumeProfile
    )
    from .ocr_module import (
        OCRProcessor, TextExtraction, DocumentAnalyzer,
        BatchProcessor
    )
except ImportError:
    # Fallback for direct execution
    from chart_analysis import (
        ChartAnalyzer, TechnicalPattern, CandlestickPattern,
        TrendLine, SupportResistance, VolumeProfile
    )
    from ocr_module import (
        OCRProcessor, TextExtraction, DocumentAnalyzer,
        BatchProcessor
    )

class VisualSignalType(Enum):
    """Vizual signal turlari"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    BREAKOUT = "breakout"
    REVERSAL = "reversal"
    CONTINUATION = "continuation"

class AnalysisConfidence(Enum):
    """Tahlil ishonchlilik darajasi"""
    VERY_HIGH = 95
    HIGH = 80
    MEDIUM = 65
    LOW = 50
    VERY_LOW = 25

@dataclass
class VisualAnalysisResult:
    """Vizual tahlil natijasi"""
    signal_type: VisualSignalType
    confidence: AnalysisConfidence
    patterns: List[Dict[str, Any]]
    price_targets: List[float]
    stop_loss: Optional[float]
    take_profit: List[float]
    time_horizon: str
    chart_type: str
    market_structure: Dict[str, Any]
    volume_analysis: Dict[str, Any]
    sentiment_score: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class MarketMicrostructureData:
    """Bozor mikrostruktura ma'lumotlari"""
    order_book: Dict[str, Any]
    volume_distribution: np.ndarray
    price_levels: np.ndarray
    liquidity_zones: List[Dict[str, Any]]
    market_depth: Dict[str, Any]
    bid_ask_spread: float
    volume_at_price: Dict[float, float]

@dataclass
class VisualSignal:
    """Vizual signal ma'lumotlari"""
    signal_id: str
    signal_type: VisualSignalType
    entry_price: float
    confidence: float
    pattern_name: str
    timeframe: str
    strength: float
    validity: datetime
    metadata: Dict[str, Any]

class VisualIntelligence:
    """
    Visual Intelligence tizimi - Asosiy klass
    
    Bu klass barcha vizual tahlil funksiyalarini boshqaradi:
    - Chart tahlili
    - Pattern aniqlash
    - Signal generation
    - Volume tahlili
    - Market microstructure tahlili
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Visual Intelligence tizimini ishga tushirish
        
        Args:
            config: Tizim konfiguratsiyasi
        """
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Asosiy komponentlarni ishga tushirish
        self.chart_analyzer = ChartAnalyzer(self.config.get('chart_analysis', {}))
        self.ocr_processor = OCRProcessor(self.config.get('ocr', {}))
        self.document_analyzer = DocumentAnalyzer(self.config.get('document_analysis', {}))
        
        # Cache va history
        self.analysis_cache: Dict[str, VisualAnalysisResult] = {}
        self.signal_history: List[VisualSignal] = []
        
        # Performance monitoring
        self.analysis_stats = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'avg_processing_time': 0.0,
            'pattern_accuracy': {}
        }
        
        self.logger.info("Visual Intelligence tizimi muvaffaqiyatli ishga tushirildi")

    def _default_config(self) -> Dict[str, Any]:
        """Standart konfiguratsiya"""
        return {
            'chart_analysis': {
                'pattern_recognition': True,
                'trend_detection': True,
                'support_resistance': True,
                'fibonacci_levels': True,
                'elliott_wave': True,
                'gann_analysis': True
            },
            'ocr': {
                'languages': ['en', 'uz', 'ru'],
                'confidence_threshold': 0.8,
                'enhance_quality': True,
                'batch_processing': True
            },
            'document_analysis': {
                'extract_financial_data': True,
                'sentiment_analysis': True,
                'key_metrics_extraction': True,
                'report_summarization': True
            },
            'visual_signals': {
                'min_confidence': 65,
                'signal_validation': True,
                'multi_timeframe': True,
                'volume_confirmation': True
            },
            'performance': {
                'cache_enabled': True,
                'cache_ttl': 300,  # 5 minutes
                'batch_processing': True,
                'parallel_analysis': True
            }
        }

    def analyze_chart_image(self, 
                          image_data: Union[str, np.ndarray, Image.Image],
                          symbol: str = "",
                          timeframe: str = "1h") -> VisualAnalysisResult:
        """
        Chart rasmini tahlil qilish
        
        Args:
            image_data: Chart rasmi (path, base64 yoki numpy array)
            symbol: Trading pair symboli
            timeframe: Vaqt oralig'i
            
        Returns:
            VisualAnalysisResult: Tahlil natijasi
        """
        start_time = datetime.now()
        
        try:
            # Rasmi yuklash va preprocessing
            image = self._load_and_preprocess_image(image_data)
            
            # Chart type va format aniqlash
            chart_info = self._analyze_chart_format(image)
            
            # Candlestick pattern tahlili
            candlestick_patterns = self.chart_analyzer.detect_candlestick_patterns(image)
            
            # Technical pattern tahlili
            technical_patterns = self.chart_analyzer.detect_technical_patterns(image)
            
            # Trend line tahlili
            trend_analysis = self.chart_analyzer.analyze_trend_lines(image)
            
            # Support/Resistance darajalari
            support_resistance = self.chart_analyzer.identify_support_resistance(image)
            
            # Volume tahlili (agar mavjud bo'lsa)
            volume_analysis = self.chart_analyzer.analyze_volume_profile(image)
            
            # Price action tahlili
            price_action = self.chart_analyzer.analyze_price_action(image)
            
            # Market microstructure tahlili
            microstructure = self._analyze_market_microstructure(image, chart_info)
            
            # Vizual signal generation
            signals = self._generate_visual_signals(
                candlestick_patterns, technical_patterns, 
                trend_analysis, support_resistance, volume_analysis
            )
            
            # Sentiment score hisoblash
            sentiment = self._calculate_sentiment_score(
                candlestick_patterns, technical_patterns, 
                trend_analysis, volume_analysis
            )
            
            # Natijani yaratish
            result = VisualAnalysisResult(
                signal_type=self._determine_overall_signal_type(signals),
                confidence=self._calculate_overall_confidence(signals, candlestick_patterns),
                patterns=candlestick_patterns + technical_patterns,
                price_targets=self._calculate_price_targets(
                    support_resistance, price_action, signals
                ),
                stop_loss=self._calculate_stop_loss(support_resistance, price_action),
                take_profit=self._calculate_take_profit(support_resistance, price_action),
                time_horizon=self._determine_time_horizon(signals, timeframe),
                chart_type=chart_info.get('type', 'unknown'),
                market_structure={
                    'trend': trend_analysis.get('trend', 'unknown'),
                    'trend_strength': trend_analysis.get('strength', 0.0),
                    'support_levels': support_resistance.get('support', []),
                    'resistance_levels': support_resistance.get('resistance', []),
                    'key_levels': support_resistance.get('key_levels', [])
                },
                volume_analysis=volume_analysis,
                sentiment_score=sentiment,
                timestamp=start_time,
                metadata={
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'analysis_time': (datetime.now() - start_time).total_seconds(),
                    'chart_format': chart_info,
                    'patterns_detected': len(candlestick_patterns + technical_patterns),
                    'signals_generated': len(signals)
                }
            )
            
            # Cache ga saqlash
            cache_key = self._generate_cache_key(image_data, symbol, timeframe)
            self.analysis_cache[cache_key] = result
            
            # Statistics yangilash
            self._update_performance_stats(start_time, True)
            
            self.logger.info(f"Chart tahlili muvaffaqiyatli tugallandi: {symbol}")
            return result
            
        except Exception as e:
            self.logger.error(f"Chart tahlil xatosi: {e}")
            self._update_performance_stats(start_time, False)
            raise

    def extract_text_from_chart(self, 
                              image_data: Union[str, np.ndarray, Image.Image],
                              extract_price_data: bool = True,
                              extract_time_info: bool = True) -> TextExtraction:
        """
        Chart dan matnli ma'lumotlarni extract qilish
        
        Args:
            image_data: Chart rasmi
            extract_price_data: Narx ma'lumotlarini extract qilish
            extract_time_info: Vaqt ma'lumotlarini extract qilish
            
        Returns:
            TextExtraction: Extract qilingan matn ma'lumotlari
        """
        try:
            # OCR yordamida matn extract qilish
            text_result = self.ocr_processor.extract_text(image_data)
            
            # Chart-specific ma'lumotlarni extract qilish
            if extract_price_data or extract_time_info:
                chart_text = self.ocr_processor.extract_chart_data(
                    image_data, 
                    include_prices=extract_price_data,
                    include_timestamps=extract_time_info
                )
                
                # Ma'lumotlarni birlashtirish
                text_result.extracted_data.update(chart_text.extracted_data)
                text_result.confidence = max(text_result.confidence, chart_text.confidence)
            
            self.logger.info("Chart dan matn muvaffaqiyatli extract qilindi")
            return text_result
            
        except Exception as e:
            self.logger.error(f"Text extract xatosi: {e}")
            raise

    def analyze_document(self, 
                        document_data: Union[str, bytes],
                        document_type: str = "pdf") -> DocumentAnalyzer:
        """
        Hujjat tahlili (PDF, images, etc.)
        
        Args:
            document_data: Hujjat ma'lumotlari
            document_type: Hujjat turi
            
        Returns:
            DocumentAnalyzer: Hujjat tahlil natijasi
        """
        try:
            # Hujjat type ga qarab mos tahlil qilish
            if document_type.lower() == "pdf":
                analysis = self.document_analyzer.analyze_pdf_document(document_data)
            elif document_type.lower() in ["image", "img", "png", "jpg", "jpeg"]:
                analysis = self.document_analyzer.analyze_image_document(document_data)
            else:
                raise ValueError(f"Qo'llab-quvvatlanmayotgan hujjat turi: {document_type}")
            
            self.logger.info(f"Hujjat tahlili muvaffaqiyatli: {document_type}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Hujjat tahlil xatosi: {e}")
            raise

    def detect_visual_signals(self, 
                            image_data: Union[str, np.ndarray, Image.Image],
                            min_confidence: float = None) -> List[VisualSignal]:
        """
        Vizual signallarni aniqlash
        
        Args:
            image_data: Chart rasmi
            min_confidence: Minimal ishonchlilik darajasi
            
        Returns:
            List[VisualSignal]: Aniqlangan vizual signallar
        """
        try:
            # Minimal confidence ni olish
            if min_confidence is None:
                min_confidence = self.config['visual_signals']['min_confidence']
            
            # Chart tahlil qilish
            analysis_result = self.analyze_chart_image(image_data)
            
            # Signallarni extract qilish
            signals = self._extract_signals_from_analysis(analysis_result, min_confidence)
            
            # Signal validation
            if self.config['visual_signals']['signal_validation']:
                signals = self._validate_signals(signals)
            
            # History ga qo'shish
            self.signal_history.extend(signals)
            
            self.logger.info(f"Vizual signallar aniqlandi: {len(signals)} ta")
            return signals
            
        except Exception as e:
            self.logger.error(f"Signal detection xatosi: {e}")
            raise

    def batch_analyze_charts(self, 
                           image_list: List[Union[str, np.ndarray, Image.Image]],
                           symbols: List[str] = None,
                           timeframes: List[str] = None) -> List[VisualAnalysisResult]:
        """
        Ko'plab chart larni parallel tahlil qilish
        
        Args:
            image_list: Chart rasmlari ro'yxati
            symbols: Symbol ro'yxati
            timeframes: Timeframe ro'yxati
            
        Returns:
            List[VisualAnalysisResult]: Tahlil natijalari
        """
        try:
            # Batch processor dan foydalanish
            results = []
            batch_size = self.config['performance'].get('batch_size', 10)
            
            for i in range(0, len(image_list), batch_size):
                batch = image_list[i:i + batch_size]
                batch_symbols = symbols[i:i + batch_size] if symbols else [''] * len(batch)
                batch_timeframes = timeframes[i:i + batch_size] if timeframes else ['1h'] * len(batch)
                
                # Parallel tahlil
                batch_results = []
                for j, (image, symbol, timeframe) in enumerate(zip(batch, batch_symbols, batch_timeframes)):
                    try:
                        result = self.analyze_chart_image(image, symbol, timeframe)
                        batch_results.append(result)
                    except Exception as e:
                        self.logger.error(f"Batch element {i+j} xatosi: {e}")
                        batch_results.append(None)
                
                results.extend(batch_results)
            
            self.logger.info(f"Batch tahlil tugallandi: {len(results)} ta natija")
            return results
            
        except Exception as e:
            self.logger.error(f"Batch analysis xatosi: {e}")
            raise

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Performance metrikalarni olish
        
        Returns:
            Dict[str, Any]: Performance metrikalar
        """
        return {
            'analysis_stats': self.analysis_stats,
            'cache_size': len(self.analysis_cache),
            'signal_history_count': len(self.signal_history),
            'recent_signals': [
                {
                    'signal_id': s.signal_id,
                    'signal_type': s.signal_type.value,
                    'confidence': s.confidence,
                    'pattern_name': s.pattern_name,
                    'timestamp': s.timestamp.isoformat()
                }
                for s in self.signal_history[-10:]  # Oxirgi 10 ta signal
            ]
        }

    def clear_cache(self):
        """Analysis cache ni tozalash"""
        self.analysis_cache.clear()
        self.logger.info("Analysis cache tozalandi")

    # Private methods
    def _load_and_preprocess_image(self, image_data: Union[str, np.ndarray, Image.Image]) -> np.ndarray:
        """Rasmi yuklash va preprocessing"""
        if isinstance(image_data, str):
            if image_data.startswith('data:image'):
                # Base64 format
                header, data = image_data.split(',', 1)
                image_data = base64.b64decode(data)
                image = Image.open(BytesIO(image_data))
            else:
                # File path
                image = Image.open(image_data)
        elif isinstance(image_data, np.ndarray):
            image = Image.fromarray(image_data)
        elif isinstance(image_data, Image.Image):
            image = image_data
        else:
            raise ValueError("Noto'g'ri image format")
        
        # RGB ga convert qilish
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return np.array(image)

    def _analyze_chart_format(self, image: np.ndarray) -> Dict[str, Any]:
        """Chart format va turini aniqlash"""
        # Chart type detection logic
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Color analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # Chart type determination
        chart_type = "unknown"
        confidence = 0.0
        
        # Simple heuristic for chart type detection
        if np.mean(hsv[:, :, 1]) > 50:  # High saturation might indicate colored chart
            chart_type = "colored_chart"
            confidence = 0.7
        elif np.mean(gray) > 200:  # Light background
            chart_type = "light_background"
            confidence = 0.6
        else:
            chart_type = "dark_background"
            confidence = 0.6
        
        return {
            'type': chart_type,
            'confidence': confidence,
            'dimensions': image.shape,
            'color_profile': {
                'mean_brightness': float(np.mean(gray)),
                'std_brightness': float(np.std(gray)),
                'mean_saturation': float(np.mean(hsv[:, :, 1]))
            }
        }

    def _generate_cache_key(self, image_data: Union[str, np.ndarray, Image.Image], 
                          symbol: str, timeframe: str) -> str:
        """Cache key generation"""
        if isinstance(image_data, str):
            image_hash = hash(image_data)
        else:
            # For numpy arrays, create a simple hash
            image_hash = hash(image_data.tobytes()[:100])  # Use first 100 bytes for speed
        
        return f"{symbol}_{timeframe}_{image_hash}"

    def _update_performance_stats(self, start_time: datetime, success: bool):
        """Performance statistics yangilash"""
        self.analysis_stats['total_analyses'] += 1
        
        if success:
            self.analysis_stats['successful_analyses'] += 1
        
        # Average processing time
        current_time = (datetime.now() - start_time).total_seconds()
        total_time = (self.analysis_stats['avg_processing_time'] * 
                     (self.analysis_stats['total_analyses'] - 1) + current_time)
        self.analysis_stats['avg_processing_time'] = total_time / self.analysis_stats['total_analyses']

    def _analyze_market_microstructure(self, image: np.ndarray, chart_info: Dict[str, Any]) -> MarketMicrostructureData:
        """Market microstructure tahlili"""
        # Placeholder for market microstructure analysis
        # In real implementation, this would analyze order book patterns, volume distribution, etc.
        
        return MarketMicrostructureData(
            order_book={'bid_levels': [], 'ask_levels': []},
            volume_distribution=np.array([]),
            price_levels=np.array([]),
            liquidity_zones=[],
            market_depth={},
            bid_ask_spread=0.0,
            volume_at_price={}
        )

    def _generate_visual_signals(self, candlestick_patterns: List[Dict], 
                               technical_patterns: List[Dict], 
                               trend_analysis: Dict, 
                               support_resistance: Dict, 
                               volume_analysis: Dict) -> List[Dict]:
        """Vizual signallar yaratish"""
        signals = []
        
        # Candlestick pattern based signals
        for pattern in candlestick_patterns:
            if pattern.get('confidence', 0) > 60:
                signals.append({
                    'type': pattern.get('signal', 'neutral'),
                    'strength': pattern.get('confidence', 0) / 100,
                    'pattern': pattern.get('name', ''),
                    'source': 'candlestick'
                })
        
        # Technical pattern based signals
        for pattern in technical_patterns:
            if pattern.get('confidence', 0) > 65:
                signals.append({
                    'type': pattern.get('signal', 'neutral'),
                    'strength': pattern.get('confidence', 0) / 100,
                    'pattern': pattern.get('name', ''),
                    'source': 'technical'
                })
        
        # Trend based signals
        trend_signal = trend_analysis.get('signal')
        if trend_signal:
            signals.append({
                'type': trend_signal,
                'strength': trend_analysis.get('strength', 0) / 100,
                'pattern': 'trend_analysis',
                'source': 'trend'
            })
        
        return signals

    def _calculate_sentiment_score(self, candlestick_patterns: List[Dict], 
                                 technical_patterns: List[Dict], 
                                 trend_analysis: Dict, 
                                 volume_analysis: Dict) -> float:
        """Sentiment score hisoblash"""
        sentiment = 0.0
        weight_count = 0
        
        # Candlestick patterns contribution
        for pattern in candlestick_patterns:
            confidence = pattern.get('confidence', 0) / 100
            if pattern.get('signal') == 'bullish':
                sentiment += confidence
            elif pattern.get('signal') == 'bearish':
                sentiment -= confidence
            weight_count += 1
        
        # Technical patterns contribution
        for pattern in technical_patterns:
            confidence = pattern.get('confidence', 0) / 100
            if pattern.get('signal') == 'bullish':
                sentiment += confidence
            elif pattern.get('signal') == 'bearish':
                sentiment -= confidence
            weight_count += 1
        
        # Trend analysis contribution
        trend_signal = trend_analysis.get('signal')
        trend_strength = trend_analysis.get('strength', 0) / 100
        if trend_signal == 'bullish':
            sentiment += trend_strength
        elif trend_signal == 'bearish':
            sentiment -= trend_strength
        weight_count += 1
        
        # Normalize
        if weight_count > 0:
            sentiment = sentiment / weight_count
        
        return max(-1.0, min(1.0, sentiment))  # Clamp between -1 and 1

    def _determine_overall_signal_type(self, signals: List[Dict]) -> VisualSignalType:
        """Umumiy signal type aniqlash"""
        bullish_score = sum(s['strength'] for s in signals if s['type'] == 'bullish')
        bearish_score = sum(s['strength'] for s in signals if s['type'] == 'bearish')
        
        if bullish_score > bearish_score * 1.2:
            return VisualSignalType.BULLISH
        elif bearish_score > bullish_score * 1.2:
            return VisualSignalType.BEARISH
        else:
            return VisualSignalType.NEUTRAL

    def _calculate_overall_confidence(self, signals: List[Dict], 
                                    patterns: List[Dict]) -> AnalysisConfidence:
        """Umumiy ishonchlilik darajasini hisoblash"""
        if not signals and not patterns:
            return AnalysisConfidence.VERY_LOW
        
        # Signal confidence
        signal_confidences = [s['strength'] * 100 for s in signals]
        
        # Pattern confidence
        pattern_confidences = [p.get('confidence', 0) for p in patterns]
        
        all_confidences = signal_confidences + pattern_confidences
        avg_confidence = sum(all_confidences) / len(all_confidences)
        
        if avg_confidence >= 90:
            return AnalysisConfidence.VERY_HIGH
        elif avg_confidence >= 75:
            return AnalysisConfidence.HIGH
        elif avg_confidence >= 60:
            return AnalysisConfidence.MEDIUM
        elif avg_confidence >= 45:
            return AnalysisConfidence.LOW
        else:
            return AnalysisConfidence.VERY_LOW

    def _calculate_price_targets(self, support_resistance: Dict, 
                               price_action: Dict, signals: List[Dict]) -> List[float]:
        """Price target hisoblash"""
        targets = []
        
        # Support/Resistance based targets
        resistance_levels = support_resistance.get('resistance', [])
        for level in resistance_levels[:2]:  # Top 2 resistance levels
            targets.append(level)
        
        return targets

    def _calculate_stop_loss(self, support_resistance: Dict, price_action: Dict) -> Optional[float]:
        """Stop loss hisoblash"""
        support_levels = support_resistance.get('support', [])
        if support_levels:
            return support_levels[-1]  # Closest support level
        return None

    def _calculate_take_profit(self, support_resistance: Dict, price_action: Dict) -> List[float]:
        """Take profit hisoblash"""
        targets = []
        
        # Resistance levels as take profit targets
        resistance_levels = support_resistance.get('resistance', [])
        for level in resistance_levels[:3]:  # Top 3 resistance levels
            targets.append(level)
        
        return targets

    def _determine_time_horizon(self, signals: List[Dict], timeframe: str) -> str:
        """Time horizon aniqlash"""
        # Simple logic based on signal strength and pattern type
        strong_signals = [s for s in signals if s['strength'] > 0.7]
        
        if len(strong_signals) > 3:
            return "short_term"
        elif len(strong_signals) > 1:
            return "medium_term"
        else:
            return "long_term"

    def _extract_signals_from_analysis(self, analysis: VisualAnalysisResult, 
                                     min_confidence: float) -> List[VisualSignal]:
        """Analysis natijasidan signallar extract qilish"""
        signals = []
        
        for i, pattern in enumerate(analysis.patterns):
            if pattern.get('confidence', 0) >= min_confidence:
                signal = VisualSignal(
                    signal_id=f"visual_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}",
                    signal_type=VisualSignalType(pattern.get('signal', 'neutral')),
                    entry_price=0.0,  # Would be calculated from current price
                    confidence=pattern.get('confidence', 0) / 100,
                    pattern_name=pattern.get('name', ''),
                    timeframe=analysis.time_horizon,
                    strength=pattern.get('confidence', 0) / 100,
                    validity=datetime.now().timestamp() + 3600,  # 1 hour validity
                    metadata={
                        'pattern_type': pattern.get('type', ''),
                        'chart_type': analysis.chart_type,
                        'analysis_timestamp': analysis.timestamp.isoformat()
                    }
                )
                signals.append(signal)
        
        return signals

    def _validate_signals(self, signals: List[VisualSignal]) -> List[VisualSignal]:
        """Signallarni validation qilish"""
        validated_signals = []
        
        for signal in signals:
            # Basic validation rules
            if (signal.confidence > 0.5 and 
                signal.strength > 0.3 and
                signal.validity > datetime.now()):
                validated_signals.append(signal)
        
        return validated_signals


# Export all classes and functions
__all__ = [
    'VisualIntelligence',
    'VisualAnalysisResult',
    'VisualSignalType',
    'AnalysisConfidence',
    'MarketMicrostructureData',
    'VisualSignal'
]

# Modul versiyasi
__version__ = "1.0.0"
__author__ = "Orion Starline AI Team"