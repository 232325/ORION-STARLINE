"""
Streaming Data Processing for Self-Learning Trading Fund
======================================================

Real-time ma'lumotlarni qayta ishlash va streaming pipeline.
Ma'lumotlarni real vaqtda olish, filtrlash va qayta ishlash.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Callable, Iterator
from datetime import datetime, timedelta
import warnings
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import deque, defaultdict
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import json
import hashlib

from ..core.base_algorithm import BaseAlgorithm
from ..core.adaptive_model import AdaptiveModel

class DataSource(Enum):
    """Ma'lumot manbalari"""
    BINANCE = "Binance"
    YAHOO_FINANCE = "Yahoo_Finance"
    ALPHA_VANTAGE = "Alpha_Vantage"
    POLYGON = "Polygon"
    REALTIME_FEED = "Realtime_Feed"
    CSV_STREAM = "CSV_Stream"
    DATABASE_STREAM = "Database_Stream"
    WEB_SOCKET = "WebSocket"

class DataQuality(Enum):
    """Ma'lumot sifati"""
    EXCELLENT = "Excellent"
    GOOD = "Good"
    FAIR = "Fair"
    POOR = "Poor"
    CORRUPTED = "Corrupted"

class ProcessingStage(Enum):
    """Qayta ishlash bosqichlari"""
    INGESTION = "Ingestion"
    VALIDATION = "Validation"
    CLEANING = "Cleaning"
    ENRICHMENT = "Enrichment"
    FEATURE_EXTRACTION = "Feature_Extraction"
    AGGREGATION = "Aggregation"
    STORAGE = "Storage"

@dataclass
class StreamingConfig:
    """Streaming konfiguratsiyasi"""
    data_sources: List[DataSource]
    buffer_size: int = 10000
    processing_interval: float = 1.0  # seconds
    quality_threshold: float = 0.8
    parallel_processing: bool = True
    max_workers: int = 4
    retention_period: int = 3600  # seconds
    backpressure_threshold: float = 0.9

@dataclass
class DataRecord:
    """Ma'lumot yozuvi"""
    timestamp: datetime
    symbol: str
    data_type: str
    values: Dict[str, Any]
    source: DataSource
    quality_score: float = 1.0
    processing_stage: ProcessingStage = ProcessingStage.INGESTION
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProcessingResult:
    """Qayta ishlash natijasi"""
    original_record: DataRecord
    processed_data: Optional[Dict[str, Any]] = None
    features: Optional[Dict[str, float]] = None
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    processing_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None

class StreamingDataProcessor(BaseAlgorithm):
    """Streaming ma'lumot qayta ishlagichi"""
    
    def __init__(self, config: StreamingConfig):
        super().__init__(config)
        self.config = config
        
        # Data structures
        self.data_buffer = deque(maxlen=config.buffer_size)
        self.processing_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.quality_metrics = defaultdict(list)
        
        # Processing pipeline
        self.processors = {
            ProcessingStage.VALIDATION: self._validate_data,
            ProcessingStage.CLEANING: self._clean_data,
            ProcessingStage.ENRICHMENT: self._enrich_data,
            ProcessingStage.FEATURE_EXTRACTION: self._extract_features,
            ProcessingStage.AGGREGATION: self._aggregate_data
        }
        
        # Threading
        self.running = False
        self.threads = []
        self.lock = threading.Lock()
        
    def start_streaming(self):
        """Streaming ni boshlash"""
        
        if self.running:
            logging.warning("Streaming is already running")
            return
        
        self.running = True
        
        # Start processing threads
        if self.config.parallel_processing:
            for i in range(self.config.max_workers):
                thread = threading.Thread(target=self._processing_worker, args=(i,))
                thread.daemon = True
                thread.start()
                self.threads.append(thread)
        
        # Start data ingestion
        ingestion_thread = threading.Thread(target=self._data_ingestion_worker)
        ingestion_thread.daemon = True
        ingestion_thread.start()
        self.threads.append(ingestion_thread)
        
        logging.info(f"Streaming started with {len(self.threads)} threads")
    
    def stop_streaming(self):
        """Streaming ni to'xtatish"""
        
        self.running = False
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=5.0)
        
        self.threads.clear()
        logging.info("Streaming stopped")
    
    def ingest_data(self, data: DataRecord):
        """Ma'lumot qabul qilish"""
        
        with self.lock:
            if len(self.data_buffer) >= self.config.buffer_size * self.config.backpressure_threshold:
                logging.warning("Buffer near capacity, applying backpressure")
                # Remove oldest records
                for _ in range(10):
                    if self.data_buffer:
                        self.data_buffer.popleft()
            
            self.data_buffer.append(data)
        
        # Put in processing queue
        try:
            self.processing_queue.put(data, block=False)
        except queue.Full:
            logging.error("Processing queue is full, dropping data")
    
    def _data_ingestion_worker(self):
        """Ma'lumot olish worker"""
        
        while self.running:
            try:
                # Simulate data ingestion from sources
                for source in self.config.data_sources:
                    data = self._simulate_data_ingestion(source)
                    if data:
                        self.ingest_data(data)
                
                time.sleep(self.config.processing_interval)
                
            except Exception as e:
                logging.error(f"Data ingestion error: {str(e)}")
                time.sleep(1)
    
    def _processing_worker(self, worker_id: int):
        """Qayta ishlash worker"""
        
        logging.info(f"Processing worker {worker_id} started")
        
        while self.running:
            try:
                # Get data from processing queue
                try:
                    data = self.processing_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process data through pipeline
                result = self._process_data_pipeline(data)
                
                # Put result in result queue
                try:
                    self.result_queue.put(result, block=False)
                except queue.Full:
                    logging.warning(f"Result queue full from worker {worker_id}")
                
                self.processing_queue.task_done()
                
            except Exception as e:
                logging.error(f"Processing worker {worker_id} error: {str(e)}")
        
        logging.info(f"Processing worker {worker_id} stopped")
    
    def _process_data_pipeline(self, data: DataRecord) -> ProcessingResult:
        """Ma'lumot qayta ishlash pipeline"""
        
        start_time = time.time()
        result = ProcessingResult(original_record=data)
        
        try:
            current_data = data
            
            # Process through each stage
            for stage in [ProcessingStage.VALIDATION, ProcessingStage.CLEANING, 
                         ProcessingStage.ENRICHMENT, ProcessingStage.FEATURE_EXTRACTION,
                         ProcessingStage.AGGREGATION]:
                
                if stage in self.processors:
                    processed_data, metrics = self.processors[stage](current_data)
                    result.quality_metrics.update(metrics)
                    
                    if processed_data:
                        if hasattr(processed_data, 'values'):
                            current_data.values.update(processed_data.values)
                        else:
                            current_data.values.update(processed_data)
                
                current_data.processing_stage = stage
            
            # Final processing time
            result.processing_time = time.time() - start_time
            result.processed_data = current_data.values
            
            # Store result for later retrieval
            with self.lock:
                if len(self.data_buffer) > self.config.buffer_size * 0.8:
                    # Clean old results if buffer is getting full
                    while len(self.data_buffer) > self.config.buffer_size * 0.7:
                        self.data_buffer.popleft()
            
            logging.debug(f"Processed data for {data.symbol} in {result.processing_time:.3f}s")
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
            logging.error(f"Data processing failed: {str(e)}")
        
        return result
    
    def _simulate_data_ingestion(self, source: DataSource) -> Optional[DataRecord]:
        """Ma'lumot olish simulyatsiyasi"""
        
        # Simulate different types of data
        symbols = ['BTCUSD', 'ETHUSD', 'AAPL', 'GOOGL', 'EURUSD']
        symbol = np.random.choice(symbols)
        
        # Create data based on source
        if source == DataSource.BINANCE:
            values = {
                'price': 45000 + np.random.randn() * 1000,
                'volume': np.random.randint(100, 10000),
                'high': 46000 + np.random.randn() * 1000,
                'low': 44000 + np.random.randn() * 1000,
                'bid': 44950 + np.random.randn() * 500,
                'ask': 45050 + np.random.randn() * 500
            }
            data_type = 'tick'
        elif source == DataSource.YAHOO_FINANCE:
            values = {
                'open': 100 + np.random.randn() * 5,
                'high': 105 + np.random.randn() * 5,
                'low': 95 + np.random.randn() * 5,
                'close': 100 + np.random.randn() * 5,
                'volume': np.random.randint(1000000, 10000000)
            }
            data_type = 'ohlcv'
        else:
            values = {
                'value': np.random.randn(),
                'timestamp': time.time(),
                'metadata': {'source': source.value}
            }
            data_type = 'generic'
        
        # Generate quality score
        quality_score = np.random.uniform(0.7, 1.0)
        
        return DataRecord(
            timestamp=datetime.now(),
            symbol=symbol,
            data_type=data_type,
            values=values,
            source=source,
            quality_score=quality_score
        )
    
    def _validate_data(self, data: DataRecord) -> Tuple[DataRecord, Dict[str, float]]:
        """Ma'lumot validatsiyasi"""
        
        metrics = {'validation_score': 1.0}
        
        # Check for missing values
        missing_values = sum(1 for v in data.values.values() if v is None or v == '')
        if missing_values > 0:
            metrics['missing_values'] = missing_values
            metrics['validation_score'] -= missing_values * 0.1
        
        # Check for outliers
        numeric_values = [v for v in data.values.values() if isinstance(v, (int, float))]
        if numeric_values:
            values_array = np.array(numeric_values)
            z_scores = np.abs((values_array - np.mean(values_array)) / np.std(values_array))
            outliers = np.sum(z_scores > 3)
            metrics['outliers'] = outliers
            if outliers > 0:
                metrics['validation_score'] -= outliers * 0.05
        
        # Check data freshness
        age = (datetime.now() - data.timestamp).total_seconds()
        if age > 300:  # 5 minutes
            metrics['data_age'] = age
            metrics['validation_score'] -= 0.2
        
        # Quality classification
        if metrics['validation_score'] >= 0.9:
            data.quality_score = 1.0
        elif metrics['validation_score'] >= 0.7:
            data.quality_score = 0.8
        else:
            data.quality_score = 0.6
        
        metrics['final_quality'] = data.quality_score
        
        return data, metrics
    
    def _clean_data(self, data: DataRecord) -> Tuple[DataRecord, Dict[str, float]]:
        """Ma'lumot tozalash"""
        
        metrics = {'cleaning_applied': False}
        
        # Handle missing values
        original_values = data.values.copy()
        
        for key, value in data.values.items():
            if value is None or value == '':
                if key in ['price', 'close', 'open', 'high', 'low']:
                    # Forward fill for price data
                    if 'previous_close' in data.metadata:
                        data.values[key] = data.metadata['previous_close']
                    else:
                        data.values[key] = np.random.uniform(90, 110)
                    metrics['cleaning_applied'] = True
                elif key == 'volume':
                    data.values[key] = np.random.randint(1000, 10000)
                    metrics['cleaning_applied'] = True
        
        # Remove extreme outliers
        for key, value in data.values.items():
            if isinstance(value, (int, float)):
                if key in ['price', 'close', 'open', 'high', 'low']:
                    if value < 0 or value > 1000000:
                        data.values[key] = 100  # Default value
                        metrics['cleaning_applied'] = True
        
        if metrics['cleaning_applied']:
            metrics['cleaning_score'] = 0.9
        
        return data, metrics
    
    def _enrich_data(self, data: DataRecord) -> Tuple[DataRecord, Dict[str, float]]:
        """Ma'lumotni boyitish"""
        
        metrics = {'enrichment_applied': False}
        
        # Add derived fields
        if 'price' in data.values and 'volume' in data.values:
            data.values['vwap_estimate'] = data.values['price']  # Simplified VWAP
            metrics['enrichment_applied'] = True
        
        if 'high' in data.values and 'low' in data.values:
            high_low_spread = (data.values['high'] - data.values['low']) / data.values['low']
            data.values['hl_spread'] = high_low_spread
            metrics['enrichment_applied'] = True
        
        # Add time-based features
        data.values['hour_of_day'] = data.timestamp.hour
        data.values['day_of_week'] = data.timestamp.weekday()
        
        # Add source reliability score
        source_scores = {
            DataSource.BINANCE: 0.95,
            DataSource.YAHOO_FINANCE: 0.90,
            DataSource.ALPHA_VANTAGE: 0.85
        }
        data.values['source_reliability'] = source_scores.get(data.source, 0.7)
        
        return data, metrics
    
    def _extract_features(self, data: DataRecord) -> Tuple[DataRecord, Dict[str, float]]:
        """Xususiyat chiqarish"""
        
        metrics = {'features_extracted': 0}
        features = {}
        
        # Price-based features
        if 'price' in data.values:
            features['log_return'] = np.log(data.values['price'] / (data.metadata.get('previous_price', data.values['price']) + 1e-8))
            features['price_change_pct'] = (data.values['price'] - data.metadata.get('previous_price', data.values['price'])) / data.metadata.get('previous_price', data.values['price']) * 100
        
        # Volume features
        if 'volume' in data.values:
            prev_volume = data.metadata.get('previous_volume', data.values['volume'])
            features['volume_change'] = data.values['volume'] - prev_volume
            features['volume_ratio'] = data.values['volume'] / max(prev_volume, 1)
        
        # Volatility features
        if 'high' in data.values and 'low' in data.values:
            features['intraday_range'] = (data.values['high'] - data.values['low']) / data.values.get('close', data.values.get('price', 100))
        
        # Technical indicators (simplified)
        if 'price' in data.values:
            # Simple moving average proxy
            prev_prices = data.metadata.get('recent_prices', [])
            if len(prev_prices) >= 5:
                sma_5 = np.mean(prev_prices[-5:])
                features['price_vs_sma5'] = data.values['price'] / sma_5 - 1
        
        # Store features in metadata
        data.metadata['features'] = features
        metrics['features_extracted'] = len(features)
        
        return data, metrics
    
    def _aggregate_data(self, data: DataRecord) -> Tuple[DataRecord, Dict[str, float]]:
        """Ma'lumot agregatsiyasi"""
        
        metrics = {'aggregation_applied': False}
        
        # Create aggregated summary
        data.values['data_summary'] = {
            'total_fields': len(data.values),
            'quality_weighted_score': data.quality_score,
            'processing_timestamp': time.time(),
            'data_age_minutes': (datetime.now() - data.timestamp).total_seconds() / 60
        }
        
        # Calculate aggregated metrics
        numeric_values = [v for v in data.values.values() if isinstance(v, (int, float))]
        if numeric_values:
            data.values['agg_mean'] = np.mean(numeric_values)
            data.values['agg_std'] = np.std(numeric_values)
            data.values['agg_min'] = np.min(numeric_values)
            data.values['agg_max'] = np.max(numeric_values)
            metrics['aggregation_applied'] = True
        
        return data, metrics
    
    def get_processed_data(self) -> Iterator[ProcessingResult]:
        """Qayta ishlangan ma'lumlarni olish"""
        
        while True:
            try:
                result = self.result_queue.get(timeout=1.0)
                yield result
            except queue.Empty:
                if not self.running:
                    break
                continue
    
    def get_streaming_stats(self) -> Dict[str, Any]:
        """Streaming statistikasini olish"""
        
        with self.lock:
            buffer_size = len(self.data_buffer)
        
        queue_sizes = {
            'processing_queue': self.processing_queue.qsize(),
            'result_queue': self.result_queue.qsize()
        }
        
        # Calculate quality metrics
        avg_quality = 0
        quality_count = 0
        
        for quality_list in self.quality_metrics.values():
            if quality_list:
                avg_quality += np.mean(quality_list)
                quality_count += 1
        
        avg_quality /= max(quality_count, 1)
        
        return {
            'running': self.running,
            'buffer_size': buffer_size,
            'buffer_utilization': buffer_size / self.config.buffer_size,
            'queue_sizes': queue_sizes,
            'average_quality': avg_quality,
            'thread_count': len(self.threads),
            'sources_active': len(self.config.data_sources)
        }

class DataQualityMonitor:
    """Ma'lumot sifati monitoring"""
    
    def __init__(self, quality_threshold: float = 0.8):
        self.quality_threshold = quality_threshold
        self.quality_history = deque(maxlen=1000)
        self.alert_thresholds = {
            'low_quality': 0.6,
            'high_latency': 5.0,  # seconds
            'data_gap': 30.0,     # seconds
            'error_rate': 0.1     # 10%
        }
        
    def assess_data_quality(self, record: DataRecord) -> DataQuality:
        """Ma'lumot sifati baholash"""
        
        quality_score = record.quality_score
        
        # Check completeness
        total_fields = len(record.values)
        complete_fields = sum(1 for v in record.values.values() if v is not None)
        completeness = complete_fields / max(total_fields, 1)
        
        # Check timeliness
        age_seconds = (datetime.now() - record.timestamp).total_seconds()
        timeliness = max(0, 1 - age_seconds / 300)  # 5 minutes threshold
        
        # Check accuracy (simplified)
        accuracy = 1.0  # Assume good accuracy for valid data
        
        # Overall quality
        overall_quality = (completeness * 0.4 + timeliness * 0.3 + accuracy * 0.3) * quality_score
        
        quality_enum = DataQuality.EXCELLENT
        if overall_quality >= 0.9:
            quality_enum = DataQuality.EXCELLENT
        elif overall_quality >= 0.8:
            quality_enum = DataQuality.GOOD
        elif overall_quality >= 0.6:
            quality_enum = DataQuality.FAIR
        elif overall_quality >= 0.4:
            quality_enum = DataQuality.POOR
        else:
            quality_enum = DataQuality.CORRUPTED
        
        # Store for monitoring
        self.quality_history.append({
            'timestamp': datetime.now(),
            'quality': overall_quality,
            'completeness': completeness,
            'timeliness': timeliness,
            'source': record.source
        })
        
        return quality_enum
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Sifat metriklari"""
        
        if not self.quality_history:
            return {'error': 'No quality data available'}
        
        recent_quality = [q['quality'] for q in list(self.quality_history)[-100:]]
        
        return {
            'average_quality': np.mean(recent_quality),
            'quality_trend': 'improving' if recent_quality[-1] > recent_quality[0] else 'declining',
            'quality_volatility': np.std(recent_quality),
            'last_quality': recent_quality[-1],
            'samples_count': len(recent_quality),
            'quality_distribution': {
                'excellent': len([q for q in recent_quality if q >= 0.9]),
                'good': len([q for q in recent_quality if 0.8 <= q < 0.9]),
                'fair': len([q for q in recent_quality if 0.6 <= q < 0.8]),
                'poor': len([q for q in recent_quality if q < 0.6])
            }
        }
    
    def detect_quality_issues(self) -> List[Dict[str, Any]]:
        """Sifat muammolarini aniqlash"""
        
        issues = []
        
        if not self.quality_history:
            return issues
        
        recent_quality = [q['quality'] for q in list(self.quality_history)[-50:]]
        
        # Check for declining quality
        if len(recent_quality) >= 10:
            early_avg = np.mean(recent_quality[:5])
            late_avg = np.mean(recent_quality[-5:])
            
            if early_avg - late_avg > 0.1:
                issues.append({
                    'type': 'quality_decline',
                    'severity': 'high',
                    'description': f'Quality declined from {early_avg:.3f} to {late_avg:.3f}',
                    'timestamp': datetime.now()
                })
        
        # Check for consistently poor quality
        poor_quality_count = len([q for q in recent_quality[-10:] if q < self.alert_thresholds['low_quality']])
        if poor_quality_count > 5:
            issues.append({
                'type': 'consistently_poor',
                'severity': 'medium',
                'description': f'{poor_quality_count} poor quality samples in last 10',
                'timestamp': datetime.now()
            })
        
        return issues

class StreamingDataManager:
    """Streaming ma'lumotlar boshqaruvchisi"""
    
    def __init__(self, config: StreamingConfig):
        self.config = config
        self.processor = StreamingDataProcessor(config)
        self.quality_monitor = DataQualityMonitor(config.quality_threshold)
        
        # Data storage
        self.processed_data_storage = deque(maxlen=10000)
        self.feature_storage = defaultdict(list)
        
        # Statistics
        self.stats = {
            'total_records_processed': 0,
            'successful_processing': 0,
            'failed_processing': 0,
            'average_processing_time': 0.0
        }
        
    def start(self):
        """Manager ni ishga tushirish"""
        
        self.processor.start_streaming()
        
        # Start result processing
        threading.Thread(target=self._result_processor, daemon=True).start()
        
        logging.info("Streaming data manager started")
    
    def stop(self):
        """Manager ni to'xtatish"""
        
        self.processor.stop_streaming()
        logging.info("Streaming data manager stopped")
    
    def _result_processor(self):
        """Natijalarni qayta ishlash"""
        
        for result in self.processor.get_processed_data():
            self._handle_processing_result(result)
    
    def _handle_processing_result(self, result: ProcessingResult):
        """Processing natijasini boshqarish"""
        
        self.stats['total_records_processed'] += 1
        
        if result.success:
            self.stats['successful_processing'] += 1
            
            # Assess quality
            quality = self.quality_monitor.assess_data_quality(result.original_record)
            
            # Store processed data
            self.processed_data_storage.append(result)
            
            # Store features separately
            if result.original_record.metadata.get('features'):
                symbol = result.original_record.symbol
                self.feature_storage[symbol].append({
                    'timestamp': result.original_record.timestamp,
                    'features': result.original_record.metadata['features'],
                    'quality': quality.value
                })
            
            # Update processing time stats
            current_avg = self.stats['average_processing_time']
            count = self.stats['successful_processing']
            self.stats['average_processing_time'] = (current_avg * (count - 1) + result.processing_time) / count
        
        else:
            self.stats['failed_processing'] += 1
            logging.error(f"Processing failed: {result.error_message}")
    
    def get_recent_features(self, symbol: str, count: int = 10) -> List[Dict[str, Any]]:
        """So'nggi xususiyatlarni olish"""
        
        if symbol in self.feature_storage:
            return list(self.feature_storage[symbol])[-count:]
        return []
    
    def get_streaming_summary(self) -> Dict[str, Any]:
        """Streaming xulosasini olish"""
        
        processor_stats = self.processor.get_streaming_stats()
        quality_metrics = self.quality_monitor.get_quality_metrics()
        
        success_rate = self.stats['successful_processing'] / max(self.stats['total_records_processed'], 1)
        
        return {
            'streaming_stats': processor_stats,
            'quality_metrics': quality_metrics,
            'processing_stats': self.stats,
            'success_rate': success_rate,
            'feature_symbols': list(self.feature_storage.keys()),
            'recent_records_count': len(self.processed_data_storage)
        }

# Demo va test
if __name__ == "__main__":
    # Streaming data processor testi
    config = StreamingConfig(
        data_sources=[DataSource.BINANCE, DataSource.YAHOO_FINANCE],
        buffer_size=1000,
        processing_interval=0.1,
        parallel_processing=True,
        max_workers=2
    )
    
    manager = StreamingDataManager(config)
    
    print("=== STREAMING DATA PROCESSOR TEST ===")
    
    # Start streaming
    manager.start()
    
    try:
        # Let it run for a few seconds
        time.sleep(3)
        
        # Get streaming summary
        summary = manager.get_streaming_summary()
        
        print(f"Total records processed: {summary['processing_stats']['total_records_processed']}")
        print(f"Success rate: {summary['success_rate']:.2%}")
        print(f"Average processing time: {summary['processing_stats']['average_processing_time']:.3f}s")
        print(f"Buffer utilization: {summary['streaming_stats']['buffer_utilization']:.2%}")
        print(f"Average quality: {summary['quality_metrics']['average_quality']:.3f}")
        
        # Test data quality
        issues = manager.quality_monitor.detect_quality_issues()
        print(f"Quality issues detected: {len(issues)}")
        
        # Test feature extraction
        recent_features = manager.get_recent_features('BTCUSD', 5)
        print(f"Recent BTCUSD features: {len(recent_features)}")
        
        if recent_features:
            print("Sample feature keys:", list(recent_features[0]['features'].keys())[:5])
        
        # Test manual data ingestion
        test_record = DataRecord(
            timestamp=datetime.now(),
            symbol='TESTUSD',
            data_type='test',
            values={
                'price': 100.5,
                'volume': 1000,
                'high': 105.0,
                'low': 98.0
            },
            source=DataSource.CSV_STREAM
        )
        
        manager.processor.ingest_data(test_record)
        print("Manual data ingested successfully")
        
    finally:
        manager.stop()
    
    print("=== STREAMING TEST COMPLETED ===")