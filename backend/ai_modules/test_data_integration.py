"""
Real-time Data Integration System - Integration Tests
Real-time Ma'lumotlar Integratsiya Tizimi - Integration Testlari

Bu fayl Real-time Data Integration tizimining barcha komponentalarini test qilish uchun
unit va integration testlarni o'z ichiga oladi.
"""

import asyncio
import pytest
import time
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

# Test subject
from data_integration import (
    DataIntegrationManager,
    RealTimeDataIntegration,
    DataConfig,
    SignalGenerator,
    RiskAnalyticsIntegration,
    RateLimiter,
    AnomalyDetector
)

from market_data import MarketDataManager
from news_feed import NewsFeedManager


class TestDataIntegration:
    """Data Integration testlari"""
    
    @pytest.fixture
    def config(self):
        """Test konfiguratsiyasi"""
        return DataConfig(
            alpha_vantage_key="test_key",
            finnhub_key="test_finnhub_key",
            enabled_sources=['yahoo', 'alpha_vantage'],
            update_interval=1,
            cache_timeout=60
        )
    
    @pytest.mark.asyncio
    async def test_data_integration_manager_initialization(self, config):
        """Test DataIntegrationManager initialization"""
        manager = DataIntegrationManager()
        
        # Check that providers are set up
        assert len(manager.engine.data_providers) > 0
        
        # Check engine setup
        assert manager.engine is not None
        assert hasattr(manager.engine, 'data_sources')
        assert hasattr(manager.engine, 'data_providers')
    
    @pytest.mark.asyncio
    async def test_market_data_integration(self, config):
        """Test market data integration"""
        manager = DataIntegrationManager()
        
        # Test single symbol integration
        result = await manager.engine.integrate_market_data("AAPL", "1d")
        
        assert isinstance(result, dict)
        assert 'symbol' in result
        assert 'timestamp' in result
        assert 'consensus' in result
        assert 'quality_score' in result
    
    @pytest.mark.asyncio
    async def test_multi_timeframe_data(self, config):
        """Test multi-timeframe data"""
        manager = DataIntegrationManager()
        
        result = await manager.engine.get_multi_timeframe_data("AAPL")
        
        assert isinstance(result, dict)
        assert len(result) > 0
        
        # Check that we have different timeframes
        for tf, data in result.items():
            if isinstance(data, dict) and 'error' not in data:
                assert 'consensus' in data
                break
    
    @pytest.mark.asyncio
    async def test_sentiment_data(self, config):
        """Test sentiment data"""
        manager = DataIntegrationManager()
        
        result = await manager.engine.get_sentiment_data("AAPL")
        
        assert isinstance(result, dict)
        assert 'symbol' in result
        assert 'twitter_sentiment' in result
        assert 'news_sentiment' in result
        assert 'fear_greed_index' in result
    
    @pytest.mark.asyncio
    async def test_economic_calendar(self, config):
        """Test economic calendar"""
        manager = DataIntegrationManager()
        
        result = await manager.engine.get_economic_calendar_data()
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Check event structure
        event = result[0]
        required_fields = ['event', 'date', 'impact', 'currency']
        for field in required_fields:
            assert field in event


class TestMarketDataManager:
    """Market Data Manager testlari"""
    
    @pytest.mark.asyncio
    async def test_market_data_manager_init(self):
        """Test MarketDataManager initialization"""
        manager = MarketDataManager()
        
        assert manager.processor is not None
        assert len(manager.streamers) > 0
        assert 'binance' in manager.streamers
        assert 'coinbase' in manager.streamers
    
    @pytest.mark.asyncio
    async def test_technical_indicators(self):
        """Test technical indicators calculation"""
        from market_data import MarketDataProcessor, MarketDataPoint
        
        processor = MarketDataProcessor()
        
        # Add some mock data
        for i in range(30):
            data_point = MarketDataPoint(
                symbol="AAPL",
                timestamp=datetime.now() - timedelta(minutes=i),
                open=100 + i,
                high=105 + i,
                low=95 + i,
                close=100 + i,
                volume=1000
            )
            processor.add_data_point(data_point)
        
        # Calculate indicators
        indicators = processor.calculate_technical_indicators("AAPL")
        
        assert isinstance(indicators, dict)
        assert 'rsi' in indicators
        assert 'macd' in indicators
        assert 'bollinger' in indicators
        
        # Check RSI
        rsi = indicators['rsi']
        assert 0 <= rsi.value <= 100
        assert rsi.signal in ['BUY', 'SELL', 'NEUTRAL']
    
    @pytest.mark.asyncio
    async def test_market_overview(self):
        """Test market overview"""
        from market_data import MarketDataProcessor, MarketDataPoint
        
        processor = MarketDataProcessor()
        
        # Add mock data
        for symbol in ["AAPL", "GOOGL", "MSFT"]:
            data_point = MarketDataPoint(
                symbol=symbol,
                timestamp=datetime.now(),
                open=100, high=105, low=95,
                close=102, volume=1000
            )
            processor.add_data_point(data_point)
        
        overview = processor.get_market_overview()
        
        assert 'timestamp' in overview
        assert 'active_symbols' in overview
        assert 'symbols' in overview
        assert overview['active_symbols'] == 3


class TestNewsFeedManager:
    """News Feed Manager testlari"""
    
    @pytest.mark.asyncio
    async def test_news_manager_init(self):
        """Test NewsFeedManager initialization"""
        manager = NewsFeedManager()
        
        assert manager.sentiment_analyzer is not None
        assert len(manager.news_providers) > 0
        assert len(manager.social_providers) > 0
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis(self):
        """Test sentiment analysis"""
        from news_feed import SentimentAnalyzer
        
        analyzer = SentimentAnalyzer()
        
        # Test positive sentiment
        positive_text = "AAPL looks great! Bullish trend, strong earnings"
        sentiment = analyzer.analyze_text(positive_text)
        assert sentiment > 0
        
        # Test negative sentiment  
        negative_text = "TSLA is bearish, bad earnings, sell signal"
        sentiment = analyzer.analyze_text(negative_text)
        assert sentiment < 0
        
        # Test neutral sentiment
        neutral_text = "The market is open for trading"
        sentiment = analyzer.analyze_text(neutral_text)
        assert abs(sentiment) < 0.5  # Should be close to neutral
    
    @pytest.mark.asyncio
    async def test_news_fetching(self):
        """Test news fetching"""
        manager = NewsFeedManager()
        
        # Mock data fetching (in real test, would use actual API keys)
        with patch.object(manager.news_providers['newsapi'], 'fetch_news') as mock_fetch:
            mock_fetch.return_value = []
            
            result = await manager.fetch_latest_news(["AAPL"], limit=10)
            
            assert isinstance(result, list)
            mock_fetch.assert_called_once()


class TestRateLimiter:
    """Rate Limiter testlari"""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter setup"""
        limiter = RateLimiter()
        
        assert len(limiter.limits) > 0
        assert 'yahoo' in limiter.limits
        assert 'alpha_vantage' in limiter.limits
        assert 'finnhub' in limiter.limits
    
    def test_can_make_request(self):
        """Test request permission"""
        limiter = RateLimiter()
        
        # Should allow initial requests
        assert limiter.can_make_request('yahoo') is True
        
        # Record some requests
        for i in range(5):
            limiter.record_request('yahoo')
        
        # Should still be allowed (limit is high for yahoo)
        assert limiter.can_make_request('yahoo') is True
    
    def test_rate_limit_exceeded(self):
        """Test rate limit exceeded"""
        limiter = RateLimiter()
        
        # Finnhub has low limit (60 per minute)
        # Simulate exceeding limit
        for i in range(65):
            limiter.record_request('finnhub')
        
        # Should be denied
        assert limiter.can_make_request('finnhub') is False


class TestAnomalyDetector:
    """Anomaly Detector testlari"""
    
    def test_anomaly_detector_initialization(self):
        """Test anomaly detector setup"""
        detector = AnomalyDetector()
        
        assert len(detector.thresholds) > 0
        assert 'price_change' in detector.thresholds
        assert 'volume_spike' in detector.thresholds
    
    def test_price_anomaly_detection(self):
        """Test price anomaly detection"""
        detector = AnomalyDetector()
        
        # Normal data
        normal_prices = [100, 101, 99, 102, 100, 101, 99, 100]
        current_price = 100.5
        
        result = detector.detect_price_anomaly(current_price, normal_prices)
        assert isinstance(result, dict)
        assert 'is_anomaly' in result
        assert 'z_score' in result
        
        # Should not be anomaly
        assert result['is_anomaly'] is False
    
    def test_volume_anomaly_detection(self):
        """Test volume anomaly detection"""
        detector = AnomalyDetector()
        
        # Normal volumes
        normal_volumes = [10000, 11000, 9000, 10500, 9500, 10000]
        current_volume = 12000
        
        result = detector.detect_volume_anomaly(current_volume, normal_volumes)
        assert isinstance(result, dict)
        assert 'is_anomaly' in result
        assert 'volume_ratio' in result
        
        # Should be anomaly (2.4x normal)
        assert result['is_anomaly'] is True
        assert result['volume_ratio'] > 2.0


class TestSignalGenerator:
    """Signal Generator testlari"""
    
    @pytest.mark.asyncio
    async def test_signal_generation(self):
        """Test signal generation"""
        from data_integration import DataIntegrationEngine
        
        engine = DataIntegrationEngine()
        signal_generator = SignalGenerator(engine)
        
        # Mock multi-timeframe and sentiment data
        with patch.object(signal_generator.engine, 'get_multi_timeframe_data') as mock_mtf:
            with patch.object(signal_generator.engine, 'get_sentiment_data') as mock_sentiment:
                mock_mtf.return_value = {
                    '1h': {
                        'consensus': {'price': {'mean': 150}},
                        'indicators': {'rsi': 25}  # Oversold
                    }
                }
                mock_sentiment.return_value = {
                    'twitter_sentiment': {'score': 0.8}
                }
                
                result = await signal_generator.generate_signals("AAPL")
                
                assert isinstance(result, dict)
                assert 'symbol' in result
                assert 'signals' in result
                assert 'confidence' in result
                
                # Should have buy signals due to low RSI
                buy_signals = result['signals']['buy']
                assert len(buy_signals) > 0


class TestRiskAnalytics:
    """Risk Analytics testlari"""
    
    @pytest.mark.asyncio
    async def test_portfolio_risk_calculation(self):
        """Test portfolio risk calculation"""
        from data_integration import DataIntegrationEngine
        
        engine = DataIntegrationEngine()
        risk_analytics = RiskAnalyticsIntegration(engine)
        
        # Mock positions
        positions = [
            {"symbol": "AAPL", "quantity": 100, "avg_price": 150},
            {"symbol": "GOOGL", "quantity": 50, "avg_price": 2800}
        ]
        
        # Mock market data
        with patch.object(risk_analytics.engine, 'integrate_market_data') as mock_market:
            mock_market.return_value = {
                'consensus': {
                    'price': {'mean': 160}
                },
                'quality_score': 0.8
            }
            
            result = await risk_analytics.calculate_portfolio_risk("user_123", positions)
            
            assert isinstance(result, dict)
            assert 'user_id' in result
            assert 'total_value' in result
            assert 'total_risk' in result
            assert 'var_95' in result
            assert 'diversification_score' in result
    
    def test_diversification_calculation(self):
        """Test diversification calculation"""
        from data_integration import RiskAnalyticsIntegration
        
        risk_analytics = RiskAnalyticsIntegration(None)  # Mock engine
        
        positions = [
            {"symbol": "AAPL", "weight": 0.5},
            {"symbol": "GOOGL", "weight": 0.3},
            {"symbol": "MSFT", "weight": 0.2}
        ]
        
        diversification = risk_analytics._calculate_diversification(positions)
        
        # Well diversified portfolio should have score > 0.5
        assert 0 < diversification < 1
        assert diversification > 0.5  # Multiple positions = good diversification


class TestIntegrationWorkflow:
    """Integration workflow testlari"""
    
    @pytest.mark.asyncio
    async def test_full_integration_workflow(self):
        """Test complete integration workflow"""
        config = DataConfig(
            enabled_sources=['yahoo'],
            update_interval=1,
            cache_timeout=60
        )
        
        integration = RealTimeDataIntegration(config)
        
        try:
            # 1. Get basic market data
            market_data = await integration.get_real_time_price("AAPL")
            assert market_data is not None
            
            # 2. Get portfolio data
            portfolio = await integration.get_portfolio_data("test_user")
            assert portfolio is not None
            assert 'user_id' in portfolio
            
            # 3. Get risk metrics
            risk = await integration.get_risk_metrics("test_user")
            assert risk is not None
            assert 'var_95' in risk
            
            # 4. Get economic calendar
            calendar = await integration.get_economic_calendar()
            assert isinstance(calendar, list)
            
            # 5. Get sentiment data
            sentiment = await integration.get_sentiment_data("AAPL")
            assert sentiment is not None
            assert 'symbol' in sentiment
            
        finally:
            integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self):
        """Test performance metrics"""
        config = DataConfig(enabled_sources=['yahoo'])
        integration = RealTimeDataIntegration(config)
        
        try:
            # Make some requests
            start_time = time.time()
            
            for i in range(3):
                await integration.get_real_time_price("AAPL")
                await asyncio.sleep(0.1)  # Small delay
            
            # Get health check
            health = await integration.health_check_advanced()
            assert health is not None
            assert 'status' in health
            
        finally:
            integration.cleanup()


# Benchmark tests
class TestPerformanceBenchmarks:
    """Performance benchmark testlari"""
    
    @pytest.mark.asyncio
    async def test_market_data_response_time(self):
        """Test market data response time"""
        config = DataConfig(enabled_sources=['yahoo'])
        integration = RealTimeDataIntegration(config)
        
        try:
            start_time = time.time()
            await integration.get_real_time_price("AAPL")
            response_time = time.time() - start_time
            
            # Should respond within 5 seconds
            assert response_time < 5.0
            
        finally:
            integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test cache performance"""
        config = DataConfig(
            enabled_sources=['yahoo'],
            cache_timeout=300
        )
        integration = RealTimeDataIntegration(config)
        
        try:
            # First request (cache miss)
            start_time = time.time()
            await integration.get_real_time_price("AAPL")
            first_time = time.time() - start_time
            
            # Second request (cache hit)
            start_time = time.time()
            await integration.get_real_time_price("AAPL")
            second_time = time.time() - start_time
            
            # Cache should be faster
            assert second_time < first_time
            assert first_time / second_time > 2  # At least 2x faster
            
        finally:
            integration.cleanup()


# Error handling tests
class TestErrorHandling:
    """Error handling testlari"""
    
    @pytest.mark.asyncio
    async def test_api_timeout_handling(self):
        """Test API timeout handling"""
        config = DataConfig(alpha_vantage_key="invalid_key")
        integration = RealTimeDataIntegration(config)
        
        try:
            # Should handle invalid API key gracefully
            result = await integration.get_real_time_price("AAPL")
            # Should return empty dict or partial data
            assert result is not None
        finally:
            integration.cleanup()
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test network error handling"""
        config = DataConfig(enabled_sources=['yahoo'])
        integration = RealTimeDataIntegration(config)
        
        # Mock network error
        with patch('aiohttp.ClientSession.get', side_effect=Exception("Network error")):
            try:
                result = await integration.get_real_time_price("AAPL")
                # Should not crash, might return empty data
                assert result is not None
            except Exception as e:
                # Exception should be handled gracefully
                assert "Network error" in str(e)
        
        integration.cleanup()


if __name__ == "__main__":
    # Run tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--asyncio-mode=auto"
    ])
