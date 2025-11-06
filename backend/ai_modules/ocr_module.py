"""
OCR Module - Orion Starline AI Trading System
=============================================

Bu modul OCR (Optical Character Recognition) va hujjat tahlili uchun mo'ljallangan.
Asosiy funksiyalar:
- Chart screenshot text extraction
- Financial document text extraction
- Handwriting recognition
- Table data extraction
- Multi-language text recognition
- PDF text extraction
- Image quality enhancement
- Batch processing

Author: Orion Starline AI Team
Version: 1.0.0
"""

import numpy as np
import cv2
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pdf2image
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
import re
import pandas as pd
import json
from io import BytesIO
import base64
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import Queue
import time

class TextType(Enum):
    """Matn turlari"""
    CHART_DATA = "chart_data"
    FINANCIAL_DATA = "financial_data"
    NUMERIC_VALUE = "numeric_value"
    DATE_TIME = "date_time"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    TABLE_DATA = "table_data"
    HANDWRITTEN = "handwritten"
    FORMULA = "formula"
    METADATA = "metadata"

class DocumentType(Enum):
    """Hujjat turlari"""
    PDF_REPORT = "pdf_report"
    IMAGE_CHART = "image_chart"
    FINANCIAL_STATEMENT = "financial_statement"
    RESEARCH_PAPER = "research_paper"
    NEWS_ARTICLE = "news_article"
    TABLE_DATA = "table_data"
    HANDWRITTEN_NOTES = "handwritten_notes"
    SCREENSHOT = "screenshot"

class ProcessingStatus(Enum):
    """Processing holati"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TextExtraction:
    """Text extraction natijasi"""
    text: str
    confidence: float
    bounding_boxes: List[Dict[str, Any]]
    text_type: TextType
    metadata: Dict[str, Any]
    language: str
    processing_time: float

@dataclass
class ChartTextData:
    """Chart dan extract qilingan matn ma'lumotlari"""
    prices: List[Dict[str, Any]]
    time_stamps: List[str]
    indicators: List[Dict[str, Any]]
    volume_data: List[float]
    chart_type: str
    symbol: str
    timeframe: str
    confidence: float

@dataclass
class DocumentAnalysis:
    """Hujjat tahlil natijasi"""
    document_type: DocumentType
    extracted_text: str
    key_metrics: Dict[str, Any]
    financial_data: Dict[str, Any]
    sentiment_score: float
    summary: str
    structure: Dict[str, Any]
    confidence: float
    processing_time: float

@dataclass
class TableData:
    """Table ma'lumotlari"""
    headers: List[str]
    rows: List[List[Any]]
    data_type: str
    confidence: float
    row_count: int
    column_count: int

class ImageEnhancer:
    """Image quality enhancement"""
    
    @staticmethod
    def enhance_image_quality(image: np.ndarray) -> np.ndarray:
        """Image quality ni yaxshilash"""
        try:
            # Convert to PIL for enhancement
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(pil_image)
            enhanced = enhancer.enhance(1.2)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(enhanced)
            enhanced = enhancer.enhance(1.1)
            
            # Reduce noise
            enhanced = enhanced.filter(ImageFilter.MedianFilter())
            
            # Convert back to OpenCV format
            return cv2.cvtColor(np.array(enhanced), cv2.COLOR_RGB2BGR)
            
        except Exception as e:
            logging.error(f"Image enhancement error: {e}")
            return image

    @staticmethod
    def denoise_image(image: np.ndarray) -> np.ndarray:
        """Image noise ni kamaytirish"""
        try:
            # Apply Non-local Means Denoising
            denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
            return denoised
        except Exception as e:
            logging.error(f"Image denoising error: {e}")
            return image

    @staticmethod
    def binarize_image(image: np.ndarray) -> np.ndarray:
        """Image ni binary qilish"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            return binary
            
        except Exception as e:
            logging.error(f"Image binarization error: {e}")
            return image

class OCRProcessor:
    """
    OCR Processor - Asosiy OCR klassi
    
    Bu klass barcha OCR va text extraction funksiyalarini bajaradi:
    - Text extraction from images
    - Chart data extraction
    - Multi-language support
    - Handwriting recognition
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        OCR Processor ni ishga tushirish
        
        Args:
            config: Tizim konfiguratsiyasi
        """
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.image_enhancer = ImageEnhancer()
        self.text_analyzer = TextAnalyzer()
        self.table_extractor = TableExtractor()
        
        # Processing statistics
        self.stats = {
            'total_processed': 0,
            'successful_extractions': 0,
            'average_confidence': 0.0,
            'processing_times': []
        }
        
        # Thread lock for stats
        self.stats_lock = threading.Lock()
        
        self.logger.info("OCR Processor muvaffaqiyatli ishga tushirildi")

    def _default_config(self) -> Dict[str, Any]:
        """Standart konfiguratsiya"""
        return {
            'languages': ['eng', 'uzb', 'rus'],
            'confidence_threshold': 80,
            'enhance_quality': True,
            'remove_noise': True,
            'binarize': True,
            'deskew': True,
            'batch_processing': {
                'enabled': True,
                'max_workers': 4,
                'batch_size': 10
            },
            'tesseract_config': {
                'psm': 6,  # Page segmentation mode
                'oem': 3,  # OCR Engine Mode
                'tessdata_dir': None
            },
            'chart_extraction': {
                'detect_price_data': True,
                'extract_time_info': True,
                'identify_indicators': True,
                'validate_data': True
            },
            'table_extraction': {
                'enabled': True,
                'min_rows': 2,
                'min_columns': 2,
                'validate_structure': True
            }
        }

    def extract_text(self, image_data: Union[str, np.ndarray, Image.Image]) -> TextExtraction:
        """
        Rasmdan matn extract qilish
        
        Args:
            image_data: Image ma'lumotlari
            
        Returns:
            TextExtraction: Extract qilingan matn
        """
        start_time = time.time()
        
        try:
            # Image ni yuklash va preprocessing
            image = self._load_image(image_data)
            
            # Image enhancement
            if self.config.get('enhance_quality', True):
                image = self.image_enhancer.enhance_image_quality(image)
            
            if self.config.get('remove_noise', True):
                image = self.image_enhancer.denoise_image(image)
            
            # OCR processing
            text, confidence, bounding_boxes = self._run_ocr(image)
            
            # Text type classification
            text_type = self.text_analyzer.classify_text_type(text)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update statistics
            self._update_stats(confidence, processing_time)
            
            result = TextExtraction(
                text=text,
                confidence=confidence,
                bounding_boxes=bounding_boxes,
                text_type=text_type,
                metadata={
                    'image_size': image.shape,
                    'enhancement_applied': self.config.get('enhance_quality', True),
                    'languages': self.config.get('languages', ['eng'])
                },
                language=','.join(self.config.get('languages', ['eng'])),
                processing_time=processing_time
            )
            
            self.logger.info(f"Text extraction completed: {len(text)} characters, {confidence:.1f}% confidence")
            return result
            
        except Exception as e:
            self.logger.error(f"Text extraction error: {e}")
            processing_time = time.time() - start_time
            self._update_stats(0, processing_time)
            raise

    def extract_chart_data(self, 
                         image_data: Union[str, np.ndarray, Image.Image],
                         include_prices: bool = True,
                         include_timestamps: bool = True) -> ChartTextData:
        """
        Chart dan ma'lumot extract qilish
        
        Args:
            image_data: Chart rasmi
            include_prices: Narx ma'lumotlarini include qilish
            include_timestamps: Vaqt ma'lumotlarini include qilish
            
        Returns:
            ChartTextData: Chart ma'lumotlari
        """
        start_time = time.time()
        
        try:
            # Text extraction
            text_result = self.extract_text(image_data)
            
            # Chart-specific data extraction
            chart_data = {
                'prices': [],
                'time_stamps': [],
                'indicators': [],
                'volume_data': [],
                'chart_type': 'unknown',
                'symbol': '',
                'timeframe': 'unknown',
                'confidence': text_result.confidence
            }
            
            # Extract numeric values (potential prices)
            if include_prices:
                numeric_values = self.text_analyzer.extract_numeric_values(text_result.text)
                chart_data['prices'] = self._process_price_data(numeric_values)
            
            # Extract time information
            if include_timestamps:
                time_info = self.text_analyzer.extract_time_information(text_result.text)
                chart_data['time_stamps'] = time_info
            
            # Extract indicators and metadata
            chart_data['indicators'] = self._extract_chart_indicators(text_result.text)
            chart_data['chart_type'] = self._detect_chart_type(text_result.text)
            chart_data['symbol'] = self._extract_symbol(text_result.text)
            chart_data['timeframe'] = self._extract_timeframe(text_result.text)
            
            # Extract volume data if present
            volume_data = self.text_analyzer.extract_volume_data(text_result.text)
            chart_data['volume_data'] = volume_data
            
            processing_time = time.time() - start_time
            
            result = ChartTextData(
                **chart_data
            )
            
            self.logger.info(f"Chart data extraction completed: {len(chart_data['prices'])} prices, {len(chart_data['time_stamps'])} timestamps")
            return result
            
        except Exception as e:
            self.logger.error(f"Chart data extraction error: {e}")
            raise

    def extract_table_data(self, image_data: Union[str, np.ndarray, Image.Image]) -> TableData:
        """
        Table ma'lumotlarini extract qilish
        
        Args:
            image_data: Table rasmi
            
        Returns:
            TableData: Table ma'lumotlari
        """
        try:
            # Text extraction
            text_result = self.extract_text(image_data)
            
            # Table extraction
            table_data = self.table_extractor.extract_table(text_result.bounding_boxes, text_result.text)
            
            # Validate table structure
            if self.config.get('table_extraction', {}).get('validate_structure', True):
                table_data = self._validate_table_structure(table_data)
            
            self.logger.info(f"Table extraction completed: {table_data.row_count} rows, {table_data.column_count} columns")
            return table_data
            
        except Exception as e:
            self.logger.error(f"Table extraction error: {e}")
            raise

    def batch_extract_text(self, image_list: List[Union[str, np.ndarray, Image.Image]]) -> List[TextExtraction]:
        """
        Ko'plab rasmlardan matn extract qilish
        
        Args:
            image_list: Image ro'yxati
            
        Returns:
            List[TextExtraction]: Extract qilingan matnlar ro'yxati
        """
        try:
            if not self.config.get('batch_processing', {}).get('enabled', True):
                # Sequential processing
                results = []
                for image in image_list:
                    result = self.extract_text(image)
                    results.append(result)
                return results
            
            # Parallel processing
            max_workers = self.config.get('batch_processing', {}).get('max_workers', 4)
            batch_size = self.config.get('batch_processing', {}).get('batch_size', 10)
            
            results = []
            
            # Process in batches
            for i in range(0, len(image_list), batch_size):
                batch = image_list[i:i + batch_size]
                
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    batch_results = list(executor.map(self.extract_text, batch))
                
                results.extend(batch_results)
            
            self.logger.info(f"Batch text extraction completed: {len(results)} images")
            return results
            
        except Exception as e:
            self.logger.error(f"Batch text extraction error: {e}")
            raise

    def enhance_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        OCR uchun image ni enhance qilish
        
        Args:
            image: Input image
            
        Returns:
            np.ndarray: Enhanced image
        """
        try:
            # Apply all enhancement techniques
            enhanced = self.image_enhancer.enhance_image_quality(image)
            enhanced = self.image_enhancer.denoise_image(enhanced)
            
            if self.config.get('binarize', False):
                enhanced = self.image_enhancer.binarize_image(enhanced)
            
            return enhanced
            
        except Exception as e:
            self.logger.error(f"OCR enhancement error: {e}")
            return image

    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Processing statistikalarini olish
        
        Returns:
            Dict[str, Any]: Processing statistikalari
        """
        with self.stats_lock:
            stats = self.stats.copy()
            stats['success_rate'] = (
                stats['successful_extractions'] / stats['total_processed'] 
                if stats['total_processed'] > 0 else 0
            )
            stats['avg_processing_time'] = (
                sum(stats['processing_times']) / len(stats['processing_times'])
                if stats['processing_times'] else 0
            )
            return stats

    # Private methods
    def _load_image(self, image_data: Union[str, np.ndarray, Image.Image]) -> np.ndarray:
        """Image ni yuklash"""
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
        
        # Convert to OpenCV format
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    def _run_ocr(self, image: np.ndarray) -> Tuple[str, float, List[Dict[str, Any]]]:
        """OCR processing"""
        try:
            # Prepare Tesseract configuration
            languages = '+'.join(self.config.get('languages', ['eng']))
            tesseract_config = self.config.get('tesseract_config', {})
            
            config_str = f"--psm {tesseract_config.get('psm', 6)} --oem {tesseract_config.get('oem', 3)}"
            
            # Run OCR with bounding boxes
            data = pytesseract.image_to_data(image, lang=languages, config=config_str, output_type=pytesseract.Output.DICT)
            
            # Extract text and confidence
            text_parts = []
            bounding_boxes = []
            confidences = []
            
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                confidence = int(data['conf'][i]) if data['conf'][i] != '-1' else 0
                
                if text:
                    text_parts.append(text)
                    confidences.append(confidence)
                    
                    # Extract bounding box
                    bounding_boxes.append({
                        'text': text,
                        'confidence': confidence,
                        'bbox': {
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i]
                        }
                    })
            
            # Calculate average confidence
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Join text
            text = ' '.join(text_parts)
            
            return text, avg_confidence, bounding_boxes
            
        except Exception as e:
            self.logger.error(f"OCR processing error: {e}")
            return "", 0.0, []

    def _update_stats(self, confidence: float, processing_time: float):
        """Statistics yangilash"""
        with self.stats_lock:
            self.stats['total_processed'] += 1
            
            if confidence >= self.config.get('confidence_threshold', 80):
                self.stats['successful_extractions'] += 1
            
            # Update average confidence
            total_conf = self.stats['average_confidence'] * (self.stats['total_processed'] - 1) + confidence
            self.stats['average_confidence'] = total_conf / self.stats['total_processed']
            
            # Add processing time
            self.stats['processing_times'].append(processing_time)
            
            # Keep only last 100 processing times
            if len(self.stats['processing_times']) > 100:
                self.stats['processing_times'] = self.stats['processing_times'][-100:]

    def _process_price_data(self, numeric_values: List[float]) -> List[Dict[str, Any]]:
        """Price ma'lumotlarini process qilish"""
        processed_prices = []
        
        for price in numeric_values:
            if 0.0001 <= price <= 100000:  # Reasonable price range
                processed_prices.append({
                    'value': price,
                    'type': 'price',
                    'confidence': 0.8
                })
        
        return processed_prices

    def _extract_chart_indicators(self, text: str) -> List[Dict[str, Any]]:
        """Chart indicator larni extract qilish"""
        indicators = []
        
        # Common trading indicators
        indicator_patterns = {
            'MA': r'\b(MA|SMA|EMA|WMA)\s*(\d+)\b',
            'RSI': r'\bRSI\s*(\d+)?\b',
            'MACD': r'\bMACD\b',
            'Bollinger': r'\b(BB|BOLL)\b',
            'Stochastic': r'\b(STOCH|KDJ)\b',
            'ADX': r'\bADX\b',
            'Volume': r'\bVOLUME\b'
        }
        
        for indicator_name, pattern in indicator_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                indicators.append({
                    'name': indicator_name,
                    'matches': len(matches),
                    'pattern': pattern
                })
        
        return indicators

    def _detect_chart_type(self, text: str) -> str:
        """Chart type ni aniqlash"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['candlestick', 'candle', 'ohlc']):
            return 'candlestick'
        elif any(word in text_lower for word in ['line', 'line chart']):
            return 'line'
        elif any(word in text_lower for word in ['bar', 'ohlc bar']):
            return 'bar'
        elif any(word in text_lower for word in ['area', 'area chart']):
            return 'area'
        else:
            return 'unknown'

    def _extract_symbol(self, text: str) -> str:
        """Trading symbol ni extract qilish"""
        # Common currency pairs
        currency_patterns = [
            r'\b[A-Z]{3}/[A-Z]{3}\b',  # EUR/USD
            r'\b[A-Z]{6}\b',          # EURUSD
            r'\b[A-Z]{3}\s+[A-Z]{3}\b',  # EUR USD
        ]
        
        for pattern in currency_patterns:
            matches = re.findall(pattern, text.upper())
            if matches:
                return matches[0]
        
        return ''

    def _extract_timeframe(self, text: str) -> str:
        """Timeframe ni extract qilish"""
        timeframe_patterns = [
            r'\b(\d+)\s*(m|min|minutes?)\b',
            r'\b(\d+)\s*(h|hour|hours?)\b',
            r'\b(\d+)\s*(d|day|days?)\b',
            r'\b(1m|5m|15m|30m|1h|4h|1d|1w)\b'
        ]
        
        for pattern in timeframe_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                return matches[0] if isinstance(matches[0], str) else f"{matches[0][0]}{matches[0][1]}"
        
        return 'unknown'

    def _validate_table_structure(self, table_data: TableData) -> TableData:
        """Table strukturasini validation qilish"""
        min_rows = self.config.get('table_extraction', {}).get('min_rows', 2)
        min_columns = self.config.get('table_extraction', {}).get('min_columns', 2)
        
        # Filter out invalid rows
        valid_rows = []
        for row in table_data.rows:
            if len(row) >= min_columns and any(cell for cell in row):
                valid_rows.append(row)
        
        if len(valid_rows) >= min_rows:
            table_data.rows = valid_rows
            table_data.row_count = len(valid_rows)
            table_data.column_count = max(len(row) for row in valid_rows) if valid_rows else 0
        else:
            # Return empty table if invalid
            table_data.rows = []
            table_data.row_count = 0
            table_data.column_count = 0
        
        return table_data


class TextAnalyzer:
    """Text analysis and classification"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def classify_text_type(self, text: str) -> TextType:
        """Text type ni classification qilish"""
        text_lower = text.lower()
        
        # Check for different text types
        if any(word in text_lower for word in ['price', 'value', 'amount', 'cost']):
            return TextType.FINANCIAL_DATA
        elif re.search(r'\d+\.\d+%', text):
            return TextType.PERCENTAGE
        elif re.search(r'\$|€|£|₽', text):
            return TextType.CURRENCY
        elif re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}', text):
            return TextType.DATE_TIME
        elif re.search(r'\d+\.?\d*', text):
            return TextType.NUMERIC_VALUE
        elif any(word in text_lower for word in ['table', 'header', 'column']):
            return TextType.TABLE_DATA
        else:
            return TextType.CHART_DATA
    
    def extract_numeric_values(self, text: str) -> List[float]:
        """Numeric value larni extract qilish"""
        numbers = []
        
        # Find decimal numbers
        decimal_pattern = r'\d+\.?\d*'
        matches = re.findall(decimal_pattern, text)
        
        for match in matches:
            try:
                numbers.append(float(match))
            except ValueError:
                continue
        
        return numbers
    
    def extract_time_information(self, text: str) -> List[str]:
        """Vaqt ma'lumotlarini extract qilish"""
        time_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # MM/DD/YYYY or DD/MM/YYYY
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{1,2}:\d{2}(:\d{2})?',  # HH:MM:SS
            r'\d{1,2}\s*(am|pm)',  # 12-hour format
        ]
        
        time_info = []
        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            time_info.extend(matches)
        
        return time_info
    
    def extract_volume_data(self, text: str) -> List[float]:
        """Volume data ni extract qilish"""
        # Look for volume indicators
        volume_patterns = [
            r'volume[:\s]*(\d+(?:\.\d+)?(?:[kmb])?)',
            r'vol[:\s]*(\d+(?:\.\d+)?(?:[kmb])?)',
        ]
        
        volume_data = []
        for pattern in volume_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Convert k, m, b suffixes
                if match.lower().endswith('k'):
                    value = float(match[:-1]) * 1000
                elif match.lower().endswith('m'):
                    value = float(match[:-1]) * 1000000
                elif match.lower().endswith('b'):
                    value = float(match[:-1]) * 1000000000
                else:
                    value = float(match)
                volume_data.append(value)
        
        return volume_data


class TableExtractor:
    """Table extraction va processing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_table(self, bounding_boxes: List[Dict[str, Any]], text: str) -> TableData:
        """Table ni extract qilish"""
        try:
            if not bounding_boxes:
                return TableData([], [], 'empty', 0.0, 0, 0)
            
            # Sort bounding boxes by position
            sorted_boxes = sorted(bounding_boxes, key=lambda x: (x['bbox']['y'], x['bbox']['x']))
            
            # Group into rows
            rows = self._group_into_rows(sorted_boxes)
            
            # Extract headers (first row)
            headers = []
            if rows:
                headers = [box['text'] for box in rows[0]]
            
            # Process data rows
            data_rows = []
            for row in rows[1:]:  # Skip header row
                data_row = [box['text'] for box in row]
                data_rows.append(data_row)
            
            # Determine data type
            data_type = self._classify_table_data(data_rows)
            
            # Calculate confidence
            confidence = self._calculate_table_confidence(bounding_boxes)
            
            return TableData(
                headers=headers,
                rows=data_rows,
                data_type=data_type,
                confidence=confidence,
                row_count=len(data_rows),
                column_count=max(len(row) for row in data_rows) if data_rows else 0
            )
            
        except Exception as e:
            self.logger.error(f"Table extraction error: {e}")
            return TableData([], [], 'error', 0.0, 0, 0)
    
    def _group_into_rows(self, bounding_boxes: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Bounding box larni qatorlarga guruhlash"""
        rows = []
        current_row = []
        row_tolerance = 10  # pixels
        
        for box in bounding_boxes:
            y = box['bbox']['y']
            
            # Check if this box belongs to current row
            if not current_row:
                current_row.append(box)
            else:
                last_y = current_row[-1]['bbox']['y']
                if abs(y - last_y) <= row_tolerance:
                    # Same row
                    current_row.append(box)
                else:
                    # New row
                    if current_row:
                        # Sort current row by x position
                        current_row.sort(key=lambda x: x['bbox']['x'])
                        rows.append(current_row)
                    current_row = [box]
        
        # Add last row
        if current_row:
            current_row.sort(key=lambda x: x['bbox']['x'])
            rows.append(current_row)
        
        return rows
    
    def _classify_table_data(self, rows: List[List[str]]) -> str:
        """Table data type ni classification qilish"""
        if not rows:
            return 'empty'
        
        # Check if data contains numbers
        numeric_count = 0
        total_cells = 0
        
        for row in rows:
            for cell in row:
                total_cells += 1
                if re.match(r'^\d+\.?\d*$', cell.strip()):
                    numeric_count += 1
        
        if total_cells > 0:
            numeric_ratio = numeric_count / total_cells
            if numeric_ratio > 0.7:
                return 'numeric'
            elif numeric_ratio > 0.3:
                return 'mixed'
            else:
                return 'text'
        
        return 'text'
    
    def _calculate_table_confidence(self, bounding_boxes: List[Dict[str, Any]]) -> float:
        """Table confidence hisoblash"""
        if not bounding_boxes:
            return 0.0
        
        # Calculate based on average confidence and text density
        avg_confidence = sum(box.get('confidence', 0) for box in bounding_boxes) / len(bounding_boxes)
        
        # Reduce confidence if very few boxes
        density_factor = min(1.0, len(bounding_boxes) / 20)
        
        return avg_confidence * density_factor / 100


class DocumentAnalyzer:
    """
    Document Analysis - Hujjat tahlil klassi
    
    Bu klass PDF va boshqa hujjatlarni tahlil qiladi:
    - PDF text extraction
    - Financial statement analysis
    - Research paper summarization
    - Document structure analysis
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Document Analyzer ni ishga tushirish
        
        Args:
            config: Tizim konfiguratsiyasi
        """
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.ocr_processor = OCRProcessor(config.get('ocr', {}))
        self.text_analyzer = TextAnalyzer()
        
        self.logger.info("Document Analyzer muvaffaqiyatli ishga tushirildi")

    def _default_config(self) -> Dict[str, Any]:
        """Standart konfiguratsiya"""
        return {
            'pdf_processing': {
                'extract_images': True,
                'extract_tables': True,
                'ocr_fallback': True,
                'page_limit': 10
            },
            'financial_analysis': {
                'extract_metrics': True,
                'calculate_ratios': True,
                'sentiment_analysis': True
            },
            'document_summarization': {
                'max_summary_length': 500,
                'include_key_points': True,
                'extract_metadata': True
            }
        }

    def analyze_pdf_document(self, pdf_data: Union[str, bytes]) -> DocumentAnalysis:
        """
        PDF hujjat tahlili
        
        Args:
            pdf_data: PDF ma'lumotlari
            
        Returns:
            DocumentAnalysis: Hujjat tahlil natijasi
        """
        start_time = time.time()
        
        try:
            # Extract text from PDF
            text_content = self._extract_pdf_text(pdf_data)
            
            # Extract images if enabled
            images = []
            if self.config.get('pdf_processing', {}).get('extract_images', True):
                images = self._extract_pdf_images(pdf_data)
            
            # Document type detection
            document_type = self._detect_document_type(text_content)
            
            # Key metrics extraction
            key_metrics = self._extract_key_metrics(text_content, document_type)
            
            # Financial data analysis
            financial_data = {}
            if document_type == DocumentType.FINANCIAL_STATEMENT:
                financial_data = self._analyze_financial_data(text_content)
            
            # Sentiment analysis
            sentiment_score = self._analyze_sentiment(text_content)
            
            # Document summarization
            summary = self._generate_summary(text_content, document_type)
            
            # Document structure analysis
            structure = self._analyze_document_structure(text_content)
            
            processing_time = time.time() - start_time
            
            result = DocumentAnalysis(
                document_type=document_type,
                extracted_text=text_content,
                key_metrics=key_metrics,
                financial_data=financial_data,
                sentiment_score=sentiment_score,
                summary=summary,
                structure=structure,
                confidence=85.0,  # Based on PDF quality
                processing_time=processing_time
            )
            
            self.logger.info(f"PDF analysis completed: {document_type.value} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"PDF analysis error: {e}")
            raise

    def analyze_image_document(self, image_data: Union[str, np.ndarray, Image.Image]) -> DocumentAnalysis:
        """
        Image hujjat tahlili
        
        Args:
            image_data: Image ma'lumotlari
            
        Returns:
            DocumentAnalysis: Hujjat tahlil natijasi
        """
        start_time = time.time()
        
        try:
            # OCR processing
            text_result = self.ocr_processor.extract_text(image_data)
            
            # Document type detection
            document_type = self._detect_document_type(text_result.text)
            
            # Key metrics extraction
            key_metrics = self._extract_key_metrics(text_result.text, document_type)
            
            # Financial data analysis
            financial_data = {}
            if document_type == DocumentType.FINANCIAL_STATEMENT:
                financial_data = self._analyze_financial_data(text_result.text)
            
            # Sentiment analysis
            sentiment_score = self._analyze_sentiment(text_result.text)
            
            # Document summarization
            summary = self._generate_summary(text_result.text, document_type)
            
            # Document structure analysis
            structure = self._analyze_document_structure(text_result.text)
            
            processing_time = time.time() - start_time
            
            result = DocumentAnalysis(
                document_type=document_type,
                extracted_text=text_result.text,
                key_metrics=key_metrics,
                financial_data=financial_data,
                sentiment_score=sentiment_score,
                summary=summary,
                structure=structure,
                confidence=text_result.confidence,
                processing_time=processing_time
            )
            
            self.logger.info(f"Image document analysis completed: {document_type.value} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Image document analysis error: {e}")
            raise

    def _extract_pdf_text(self, pdf_data: Union[str, bytes]) -> str:
        """PDF dan matn extract qilish"""
        try:
            if isinstance(pdf_data, str):
                # File path
                doc = fitz.open(pdf_data)
            else:
                # Bytes data
                doc = fitz.open(stream=pdf_data, filetype="pdf")
            
            text_content = ""
            page_limit = self.config.get('pdf_processing', {}).get('page_limit', 10)
            
            for page_num in range(min(len(doc), page_limit)):
                page = doc[page_num]
                text_content += page.get_text()
                text_content += "\n" + "="*50 + "\n"
            
            doc.close()
            return text_content
            
        except Exception as e:
            self.logger.error(f"PDF text extraction error: {e}")
            return ""

    def _extract_pdf_images(self, pdf_data: Union[str, bytes]) -> List[np.ndarray]:
        """PDF dan rasm extract qilish"""
        try:
            images = []
            
            if isinstance(pdf_data, str):
                doc = fitz.open(pdf_data)
            else:
                doc = fitz.open(stream=pdf_data, filetype="pdf")
            
            page_limit = self.config.get('pdf_processing', {}).get('page_limit', 10)
            
            for page_num in range(min(len(doc), page_limit)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img in image_list:
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    if pix.n - pix.alpha < 4:  # GRAY or RGB
                        img_data = pix.tobytes("png")
                        img_array = np.frombuffer(img_data, np.uint8)
                        image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                        images.append(image)
                    
                    pix = None
            
            doc.close()
            return images
            
        except Exception as e:
            self.logger.error(f"PDF image extraction error: {e}")
            return []

    def _detect_document_type(self, text: str) -> DocumentType:
        """Hujjat type ni aniqlash"""
        text_lower = text.lower()
        
        # Financial statements
        if any(word in text_lower for word in ['balance sheet', 'income statement', 'cash flow', 'revenue', 'expenses']):
            return DocumentType.FINANCIAL_STATEMENT
        
        # Research papers
        elif any(word in text_lower for word in ['abstract', 'methodology', 'conclusion', 'references', 'doi']):
            return DocumentType.RESEARCH_PAPER
        
        # News articles
        elif any(word in text_lower for word in ['news', 'report', 'according to', 'statement said']):
            return DocumentType.NEWS_ARTICLE
        
        # Screenshots
        elif any(word in text_lower for word in ['screenshot', 'capture', 'image']):
            return DocumentType.SCREENSHOT
        
        else:
            return DocumentType.PDF_REPORT

    def _extract_key_metrics(self, text: str, document_type: DocumentType) -> Dict[str, Any]:
        """Kalit metrikalarni extract qilish"""
        metrics = {}
        
        try:
            # Common financial metrics
            financial_patterns = {
                'revenue': r'revenue[:\s]*\$?(\d+(?:\.\d+)?(?:[kmb])?)',
                'profit': r'profit[:\s]*\$?(\d+(?:\.\d+)?(?:[kmb])?)',
                'debt': r'debt[:\s]*\$?(\d+(?:\.\d+)?(?:[kmb])?)',
                'employees': r'(\d+(?:\.\d+)?)\s*(?:employees?|staff|workers?)',
                'growth_rate': r'(\d+(?:\.\d+)?)%\s*(?:growth|increase|decrease)',
            }
            
            for metric_name, pattern in financial_patterns.items():
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    metrics[metric_name] = matches[0]
            
            # Percentage values
            percentage_matches = re.findall(r'(\d+(?:\.\d+)?)%', text)
            if percentage_matches:
                metrics['percentages'] = percentage_matches[:10]  # First 10
            
            # Currency amounts
            currency_matches = re.findall(r'\$?(\d+(?:\.\d+)?(?:[kmb])?)', text)
            if currency_matches:
                metrics['amounts'] = currency_matches[:10]  # First 10
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Key metrics extraction error: {e}")
            return {}

    def _analyze_financial_data(self, text: str) -> Dict[str, Any]:
        """Financial data tahlili"""
        try:
            financial_data = {}
            
            # Extract financial statements sections
            sections = ['assets', 'liabilities', 'equity', 'revenue', 'expenses']
            
            for section in sections:
                pattern = rf'{section}[:\s]*([\d,]+\.?\d*|\w+)'
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    financial_data[section] = matches[0]
            
            # Calculate simple ratios
            if 'assets' in financial_data and 'liabilities' in financial_data:
                try:
                    assets = float(re.sub(r'[^\d.]', '', financial_data['assets']))
                    liabilities = float(re.sub(r'[^\d.]', '', financial_data['liabilities']))
                    if liabilities > 0:
                        financial_data['debt_to_assets'] = assets / liabilities
                except:
                    pass
            
            return financial_data
            
        except Exception as e:
            self.logger.error(f"Financial data analysis error: {e}")
            return {}

    def _analyze_sentiment(self, text: str) -> float:
        """Sentiment analysis"""
        try:
            # Simple sentiment analysis based on keywords
            positive_words = ['increase', 'growth', 'profit', 'gain', 'positive', 'improve', 'success']
            negative_words = ['decrease', 'loss', 'decline', 'negative', 'worse', 'problem', 'risk']
            
            text_lower = text.lower()
            
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            total_words = len(text.split())
            
            if total_words > 0:
                sentiment_score = (positive_count - negative_count) / total_words
                return max(-1.0, min(1.0, sentiment_score * 10))  # Scale to -1 to 1
            else:
                return 0.0
                
        except Exception as e:
            self.logger.error(f"Sentiment analysis error: {e}")
            return 0.0

    def _generate_summary(self, text: str, document_type: DocumentType) -> str:
        """Document summary yaratish"""
        try:
            max_length = self.config.get('document_summarization', {}).get('max_summary_length', 500)
            
            # Simple extraction-based summarization
            sentences = text.split('.')
            summary_sentences = []
            
            # Select most important sentences
            for sentence in sentences[:10]:  # First 10 sentences
                if len(' '.join(summary_sentences)) < max_length:
                    if len(sentence.strip()) > 20:  # Meaningful sentences
                        summary_sentences.append(sentence.strip())
                else:
                    break
            
            summary = '. '.join(summary_sentences)
            
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Summary generation error: {e}")
            return "Summary could not be generated."

    def _analyze_document_structure(self, text: str) -> Dict[str, Any]:
        """Document structure tahlili"""
        try:
            sentences = text.split('.')
            paragraphs = text.split('\n\n')
            words = text.split()
            
            # Find headings (lines that are short and title-case)
            potential_headings = []
            for paragraph in paragraphs:
                lines = paragraph.split('\n')
                for line in lines:
                    line = line.strip()
                    if (5 <= len(line) <= 50 and 
                        line.istitle() and 
                        not re.search(r'[.!?]$', line)):
                        potential_headings.append(line)
            
            structure = {
                'sentence_count': len(sentences),
                'paragraph_count': len(paragraphs),
                'word_count': len(words),
                'character_count': len(text),
                'headings': potential_headings[:10],  # First 10 headings
                'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
                'has_tables': bool(re.search(r'Table\s+\d+', text, re.IGNORECASE)),
                'has_figures': bool(re.search(r'Figure\s+\d+', text, re.IGNORECASE))
            }
            
            return structure
            
        except Exception as e:
            self.logger.error(f"Document structure analysis error: {e}")
            return {}


# Batch Processing Module
class BatchProcessor:
    """Batch processing qilish uchun klass"""
    
    def __init__(self, max_workers: int = 4, batch_size: int = 10):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.logger = logging.getLogger(__name__)
    
    def process_batch_images(self, 
                           images: List[Union[str, np.ndarray, Image.Image]], 
                           processor_func) -> List[Any]:
        """
        Ko'plab rasmlarni batch processing qilish
        
        Args:
            images: Image ro'yxati
            processor_func: Processing function
            
        Returns:
            List[Any]: Processing natijalari
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for i in range(0, len(images), self.batch_size):
                batch = images[i:i + self.batch_size]
                batch_results = list(executor.map(processor_func, batch))
                results.extend(batch_results)
        
        return results


# Export all classes and functions
__all__ = [
    'OCRProcessor',
    'TextAnalyzer',
    'TableExtractor',
    'DocumentAnalyzer',
    'ImageEnhancer',
    'BatchProcessor',
    'TextExtraction',
    'ChartTextData',
    'DocumentAnalysis',
    'TableData',
    'TextType',
    'DocumentType',
    'ProcessingStatus'
]

# Modul versiyasi
__version__ = "1.0.0"
__author__ = "Orion Starline AI Team"