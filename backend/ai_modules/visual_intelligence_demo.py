"""
Visual Intelligence Demo - Orion Starline AI Trading System
===========================================================

Bu demo skript Visual Intelligence tizimining barcha funksiyalarini test qiladi.

Author: Orion Starline AI Team
Version: 1.0.0
"""

import numpy as np
import cv2
import logging
import time
from PIL import Image, ImageDraw
from typing import List, Dict, Any
import json

# Visual Intelligence imports
from .visual_intelligence import (
    VisualIntelligence, 
    VisualAnalysisResult, 
    VisualSignalType, 
    AnalysisConfidence
)
from .chart_analysis import (
    ChartAnalyzer, 
    PatternType, 
    TrendDirection, 
    CandlestickPattern
)
from .ocr_module import (
    OCRProcessor, 
    DocumentAnalyzer, 
    TextType, 
    DocumentType
)

class VisualIntelligenceDemo:
    """
    Visual Intelligence tizimi demo klassi
    
    Bu klass barcha Visual Intelligence funksiyalarini test qiladi
    """

    def __init__(self):
        """Demo tizimini ishga tushirish"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Visual Intelligence tizimini ishga tushirish
        config = {
            'chart_analysis': {
                'pattern_recognition': True,
                'trend_detection': True,
                'support_resistance': True,
                'fibonacci_levels': True
            },
            'ocr': {
                'languages': ['en', 'uz', 'ru'],
                'confidence_threshold': 80,
                'enhance_quality': True
            },
            'visual_signals': {
                'min_confidence': 65,
                'signal_validation': True
            }
        }
        
        self.visual_intelligence = VisualIntelligence(config)
        self.chart_analyzer = ChartAnalyzer()
        self.ocr_processor = OCRProcessor()
        self.document_analyzer = DocumentAnalyzer()
        
        self.logger.info("Visual Intelligence Demo tizimi ishga tushirildi")

    def create_test_chart(self) -> np.ndarray:
        """Test uchun synthetic chart yaratish"""
        # Create a synthetic candlestick chart
        width, height = 800, 600
        image = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # Draw chart background
        cv2.rectangle(image, (50, 50), (750, 550), (240, 240, 240), -1)
        
        # Generate synthetic price data
        np.random.seed(42)
        n_candles = 30
        base_price = 1.1000
        
        prices = []
        for i in range(n_candles):
            change = np.random.normal(0, 0.002)
            price = base_price + change * i
            prices.append(price)
        
        # Draw candlesticks
        for i, price in enumerate(prices):
            x = 100 + i * 20
            y_center = int(550 - (price - 1.095) * 100000)
            
            # Candle body
            body_height = 15
            cv2.rectangle(image, (x-5, y_center-body_height//2), (x+5, y_center+body_height//2), (100, 100, 255), -1)
            
            # High/Low lines
            cv2.line(image, (x, y_center-30), (x, y_center+30), (150, 150, 150), 1)
        
        # Add some text
        cv2.putText(image, "EUR/USD H1", (60, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(image, "1.1000", (700, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        
        return image

    def create_test_document(self) -> np.ndarray:
        """Test uchun hujjat rasmi yaratish"""
        # Create a simple document with text
        width, height = 600, 800
        image = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # Add document text
        text_lines = [
            "FINANCIAL REPORT Q4 2023",
            "",
            "Revenue: $1,250,000",
            "Profit: $350,000",
            "Growth Rate: 12.5%",
            "",
            "Market Analysis:",
            "The company showed strong performance",
            "with increased market share.",
            "",
            "Date: December 31, 2023"
        ]
        
        y_offset = 100
        for line in text_lines:
            cv2.putText(image, line, (50, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
            y_offset += 40
        
        return image

    def test_chart_analysis(self) -> Dict[str, Any]:
        """Chart analysis funksiyasini test qilish"""
        self.logger.info("=== CHART ANALYSIS TEST ===")
        
        # Test chart yaratish
        chart_image = self.create_test_chart()
        
        start_time = time.time()
        
        try:
            # Chart analysis
            analysis_result = self.visual_intelligence.analyze_chart_image(
                chart_image, 
                symbol="EURUSD", 
                timeframe="1h"
            )
            
            processing_time = time.time() - start_time
            
            result = {
                'status': 'success',
                'processing_time': processing_time,
                'signal_type': analysis_result.signal_type.value,
                'confidence': analysis_result.confidence.value,
                'patterns_detected': len(analysis_result.patterns),
                'price_targets': analysis_result.price_targets,
                'stop_loss': analysis_result.stop_loss,
                'take_profit': analysis_result.take_profit,
                'time_horizon': analysis_result.time_horizon,
                'chart_type': analysis_result.chart_type,
                'market_structure': analysis_result.market_structure,
                'sentiment_score': analysis_result.sentiment_score,
                'metadata': analysis_result.metadata
            }
            
            self.logger.info(f"Chart analysis muvaffaqiyatli: {result['patterns_detected']} ta pattern")
            return result
            
        except Exception as e:
            self.logger.error(f"Chart analysis xatosi: {e}")
            return {'status': 'error', 'message': str(e)}

    def test_ocr_extraction(self) -> Dict[str, Any]:
        """OCR extraction funksiyasini test qilish"""
        self.logger.info("=== OCR EXTRACTION TEST ===")
        
        # Test document yaratish
        document_image = self.create_test_document()
        
        start_time = time.time()
        
        try:
            # Text extraction
            text_result = self.visual_intelligence.extract_text_from_chart(
                document_image,
                extract_price_data=True,
                extract_time_info=True
            )
            
            processing_time = time.time() - start_time
            
            result = {
                'status': 'success',
                'processing_time': processing_time,
                'extracted_text': text_result.text[:200] + "...",  # First 200 chars
                'confidence': text_result.confidence,
                'text_type': text_result.text_type.value,
                'language': text_result.language,
                'bounding_boxes_count': len(text_result.bounding_boxes)
            }
            
            self.logger.info(f"OCR extraction muvaffaqiyatli: {text_result.confidence:.1f}% ishonchlilik")
            return result
            
        except Exception as e:
            self.logger.error(f"OCR extraction xatosi: {e}")
            return {'status': 'error', 'message': str(e)}

    def test_visual_signals(self) -> Dict[str, Any]:
        """Visual signals detection funksiyasini test qilish"""
        self.logger.info("=== VISUAL SIGNALS TEST ===")
        
        # Test chart yaratish
        chart_image = self.create_test_chart()
        
        start_time = time.time()
        
        try:
            # Visual signals detection
            signals = self.visual_intelligence.detect_visual_signals(
                chart_image,
                min_confidence=50
            )
            
            processing_time = time.time() - start_time
            
            signal_data = []
            for signal in signals:
                signal_data.append({
                    'signal_id': signal.signal_id,
                    'signal_type': signal.signal_type.value,
                    'confidence': signal.confidence,
                    'pattern_name': signal.pattern_name,
                    'timeframe': signal.timeframe,
                    'strength': signal.strength
                })
            
            result = {
                'status': 'success',
                'processing_time': processing_time,
                'signals_detected': len(signals),
                'signals': signal_data
            }
            
            self.logger.info(f"Visual signals muvaffaqiyatli: {len(signals)} ta signal")
            return result
            
        except Exception as e:
            self.logger.error(f"Visual signals xatosi: {e}")
            return {'status': 'error', 'message': str(e)}

    def test_batch_processing(self) -> Dict[str, Any]:
        """Batch processing funksiyasini test qilish"""
        self.logger.info("=== BATCH PROCESSING TEST ===")
        
        # Test rasmlar yaratish
        test_images = [self.create_test_chart() for _ in range(3)]
        symbols = ['EURUSD', 'GBPUSD', 'USDJPY']
        timeframes = ['1h', '4h', '1d']
        
        start_time = time.time()
        
        try:
            # Batch analysis
            results = self.visual_intelligence.batch_analyze_charts(
                test_images,
                symbols,
                timeframes
            )
            
            processing_time = time.time() - start_time
            
            batch_data = []
            for i, result in enumerate(results):
                if result:
                    batch_data.append({
                        'symbol': symbols[i],
                        'timeframe': timeframes[i],
                        'signal_type': result.signal_type.value,
                        'confidence': result.confidence.value,
                        'patterns': len(result.patterns)
                    })
                else:
                    batch_data.append({
                        'symbol': symbols[i],
                        'status': 'failed'
                    })
            
            result = {
                'status': 'success',
                'processing_time': processing_time,
                'total_images': len(test_images),
                'successful_analyses': len([r for r in results if r is not None]),
                'batch_results': batch_data
            }
            
            self.logger.info(f"Batch processing muvaffaqiyatli: {result['successful_analyses']}/{result['total_images']} ta")
            return result
            
        except Exception as e:
            self.logger.error(f"Batch processing xatosi: {e}")
            return {'status': 'error', 'message': str(e)}

    def test_performance_metrics(self) -> Dict[str, Any]:
        """Performance metrics funksiyasini test qilish"""
        self.logger.info("=== PERFORMANCE METRICS TEST ===")
        
        try:
            # Performance metrics olish
            metrics = self.visual_intelligence.get_performance_metrics()
            
            result = {
                'status': 'success',
                'analysis_stats': metrics['analysis_stats'],
                'cache_size': metrics['cache_size'],
                'signal_history_count': metrics['signal_history_count'],
                'recent_signals': metrics['recent_signals']
            }
            
            self.logger.info("Performance metrics olindi")
            return result
            
        except Exception as e:
            self.logger.error(f"Performance metrics xatosi: {e}")
            return {'status': 'error', 'message': str(e)}

    def run_full_demo(self) -> Dict[str, Any]:
        """To'liq demo testni ishga tushirish"""
        self.logger.info("🚀 VISUAL INTELLIGENCE SYSTEM DEMO BOSHLANYAPTI...")
        
        demo_results = {
            'start_time': time.time(),
            'tests': {}
        }
        
        # Test 1: Chart Analysis
        self.logger.info("1️⃣ Chart Analysis test...")
        demo_results['tests']['chart_analysis'] = self.test_chart_analysis()
        
        # Test 2: OCR Extraction
        self.logger.info("2️⃣ OCR Extraction test...")
        demo_results['tests']['ocr_extraction'] = self.test_ocr_extraction()
        
        # Test 3: Visual Signals
        self.logger.info("3️⃣ Visual Signals test...")
        demo_results['tests']['visual_signals'] = self.test_visual_signals()
        
        # Test 4: Batch Processing
        self.logger.info("4️⃣ Batch Processing test...")
        demo_results['tests']['batch_processing'] = self.test_batch_processing()
        
        # Test 5: Performance Metrics
        self.logger.info("5️⃣ Performance Metrics test...")
        demo_results['tests']['performance_metrics'] = self.test_performance_metrics()
        
        # Summary
        demo_results['end_time'] = time.time()
        demo_results['total_time'] = demo_results['end_time'] - demo_results['start_time']
        
        # Calculate success rate
        successful_tests = sum(1 for test in demo_results['tests'].values() if test.get('status') == 'success')
        demo_results['success_rate'] = successful_tests / len(demo_results['tests']) * 100
        
        self.logger.info("✅ VISUAL INTELLIGENCE DEMO TUGALLANDI!")
        self.logger.info(f"📊 Muvaffaqiyat darajasi: {demo_results['success_rate']:.1f}%")
        self.logger.info(f"⏱️ Jami vaqt: {demo_results['total_time']:.2f} soniya")
        
        return demo_results

    def print_demo_report(self, results: Dict[str, Any]):
        """Demo natijasini print qilish"""
        print("\n" + "="*60)
        print("📋 VISUAL INTELLIGENCE SYSTEM TEST NATIJALARI")
        print("="*60)
        
        for test_name, test_result in results['tests'].items():
            status = "✅" if test_result.get('status') == 'success' else "❌"
            print(f"\n{status} {test_name.upper().replace('_', ' ')}")
            print("-" * 40)
            
            if test_result.get('status') == 'success':
                if 'processing_time' in test_result:
                    print(f"⏱️  Vaqt: {test_result['processing_time']:.2f}s")
                
                if 'chart_analysis' in test_name:
                    print(f"📈 Signal: {test_result.get('signal_type', 'N/A')}")
                    print(f"🎯 Ishonchlilik: {test_result.get('confidence', 'N/A')}")
                    print(f"🔍 Patternlar: {test_result.get('patterns_detected', 0)} ta")
                
                elif 'ocr_extraction' in test_name:
                    print(f"📝 Matn: {len(test_result.get('extracted_text', ''))} belgi")
                    print(f"🎯 Ishonchlilik: {test_result.get('confidence', 0):.1f}%")
                
                elif 'visual_signals' in test_name:
                    print(f"🚦 Signallar: {test_result.get('signals_detected', 0)} ta")
                
                elif 'batch_processing' in test_name:
                    print(f"🖼️  Rasmlar: {test_result.get('total_images', 0)} ta")
                    print(f"✅ Muvaffaqiyatli: {test_result.get('successful_analyses', 0)} ta")
                
                elif 'performance_metrics' in test_name:
                    print(f"📊 Tahlillar: {test_result.get('analysis_stats', {}).get('total_analyses', 0)} ta")
                    print(f"💾 Cache: {test_result.get('cache_size', 0)} ta")
            
            else:
                print(f"❌ Xato: {test_result.get('message', 'Noma\'lum xato')}")
        
        print(f"\n📊 UMUMIY NATIJA:")
        print(f"✅ Muvaffaqiyat darajasi: {results['success_rate']:.1f}%")
        print(f"⏱️  Jami vaqt: {results['total_time']:.2f} soniya")
        print("="*60)


def main():
    """Asosiy funksiya - Demo skriptni ishga tushirish"""
    print("🎯 Visual Intelligence System Demo")
    print("Orion Starline AI Trading System")
    print("="*50)
    
    # Demo yaratish va ishga tushirish
    demo = VisualIntelligenceDemo()
    results = demo.run_full_demo()
    
    # Natijani print qilish
    demo.print_demo_report(results)
    
    # JSON formatda saqlash
    with open('visual_intelligence_demo_results.json', 'w', encoding='utf-8') as f:
        # Datetime objektlarini string ga aylantirish
        json_results = results.copy()
        json_results['start_time'] = time.ctime(results['start_time'])
        json_results['end_time'] = time.ctime(results['end_time'])
        
        json.dump(json_results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Natijalar 'visual_intelligence_demo_results.json' fayliga saqlandi")
    
    return results


if __name__ == "__main__":
    main()
