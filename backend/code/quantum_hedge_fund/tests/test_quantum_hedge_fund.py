"""
Unit tests for Quantum AI Hedge Fund Platform
"""
import pytest
import asyncio
import json
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from core.orchestrator import QuantumHedgeFundOrchestrator, SystemConfig
from quantum.quantum_engine import QuantumEngine, QuantumResult
from quantum.quantum_ml import QuantumMLEngine
from trading.trading_engine import TradingEngine, Order, OrderType, OrderSide
from analytics.analytics_engine import AnalyticsEngine
from risk.risk_manager import RiskManager, RiskLevel
from compliance.compliance_engine import ComplianceEngine, ComplianceStatus

class TestQuantumHedgeFundOrchestrator:
    """Test Quantum Hedge Fund Orchestrator"""
    
    @pytest.fixture
    def config(self):
        """Test configuration"""
        return {
            "system": {
                "quantum_enabled": True,
                "auto_trading": False,
                "risk_level": "medium",
                "max_position_size": 0.1,
                "min_profit_threshold": 0.02,
                "compliance_mode": "strict"
            },
            "quantum": {
                "simulator_backend": "qiskit_aer",
                "shots": 1024,
                "optimization_iterations": 100
            }
        }
    
    @pytest.fixture
    def temp_config_file(self, config):
        """Temporary config file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            f.flush()
            yield f.name
        os.unlink(f.name)
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, temp_config_file):
        """Test orchestrator initialization"""
        orchestrator = QuantumHedgeFundOrchestrator(temp_config_file)
        
        # Test config loading
        assert orchestrator.system_config.quantum_enabled is True
        assert orchestrator.system_config.risk_level == "medium"
        
        # Mock initialization methods
        with patch.object(orchestrator.quantum_engine, 'initialize', new_callable=AsyncMock):
            with patch.object(orchestrator.trading_engine, 'initialize', new_callable=AsyncMock):
                with patch.object(orchestrator.analytics_engine, 'initialize', new_callable=AsyncMock):
                    with patch.object(orchestrator.risk_manager, 'initialize', new_callable=AsyncMock):
                        with patch.object(orchestrator.compliance_engine, 'initialize', new_callable=AsyncMock):
                            result = await orchestrator.initialize()
        
        assert result is True
        assert orchestrator.is_running is True
    
    @pytest.mark.asyncio
    async def test_quantum_portfolio_optimization(self, temp_config_file):
        """Test quantum portfolio optimization"""
        orchestrator = QuantumHedgeFundOrchestrator(temp_config_file)
        
        # Mock quantum engine
        orchestrator.quantum_engine = Mock()
        orchestrator.quantum_engine.optimize_portfolio = AsyncMock(return_value={
            "expected_return": 0.08,
            "sharpe_ratio": 1.2,
            "confidence": 0.85,
            "quantum_advantage": 0.15
        })
        
        # Mock portfolio data
        portfolio = {
            "assets": [
                {"symbol": "AAPL", "expected_return": 0.07},
                {"symbol": "GOOGL", "expected_return": 0.09}
            ],
            "covariance_matrix": [[0.01, 0.005], [0.005, 0.02]]
        }
        
        result = await orchestrator.quantum_optimize_portfolio()
        
        assert result["expected_return"] == 0.08
        assert result["sharpe_ratio"] == 1.2
        assert result["confidence"] == 0.85
        assert result["quantum_advantage"] == 0.15
    
    @pytest.mark.asyncio
    async def test_market_analysis(self, temp_config_file):
        """Test market analysis"""
        orchestrator = QuantumHedgeFundOrchestrator(temp_config_file)
        
        # Mock analytics engine
        orchestrator.analytics_engine = Mock()
        orchestrator.analytics_engine.run_technical_analysis = AsyncMock(return_value={
            "trend": "bullish",
            "confidence": 0.75
        })
        
        # Mock quantum ML engine
        orchestrator.quantum_ml_engine = Mock()
        orchestrator.quantum_ml_engine.analyze_market_patterns = AsyncMock(return_value={
            "pattern": "ascending_triangle",
            "confidence": 0.80
        })
        
        result = await orchestrator.run_market_analysis()
        
        assert "timestamp" in result
        assert "traditional" in result
        assert "quantum" in result
        assert "confidence" in result
        assert result["confidence"] > 0

class TestQuantumEngine:
    """Test Quantum Engine"""
    
    @pytest.fixture
    def quantum_config(self):
        """Quantum configuration"""
        return {
            "simulator_backend": "qiskit_aer",
            "shots": 1024,
            "optimization_iterations": 100
        }
    
    @pytest.mark.asyncio
    async def test_quantum_engine_initialization(self, quantum_config):
        """Test quantum engine initialization"""
        engine = QuantumEngine(quantum_config)
        await engine.initialize()
        
        assert engine.is_initialized is True
        assert len(engine.quantum_simulators) > 0
        assert len(engine.quantum_algorithms) > 0
    
    @pytest.mark.asyncio
    async def test_portfolio_optimization(self, quantum_config):
        """Test portfolio optimization"""
        engine = QuantumEngine(quantum_config)
        await engine.initialize()
        
        portfolio = {
            "assets": [
                {"symbol": "AAPL", "expected_return": 0.07},
                {"symbol": "GOOGL", "expected_return": 0.09}
            ]
        }
        
        result = await engine.optimize_portfolio(portfolio, "medium")
        
        assert result.success is True
        assert "expected_return" in result.data
        assert "sharpe_ratio" in result.data
        assert result.confidence > 0
        assert result.quantum_advantage > 0
    
    @pytest.mark.asyncio
    async def test_quantum_annealing_optimization(self, quantum_config):
        """Test quantum annealing optimization"""
        engine = QuantumEngine(quantum_config)
        await engine.initialize()
        
        portfolio = {
            "assets": [
                {"symbol": "AAPL", "expected_return": 0.05},
                {"symbol": "MSFT", "expected_return": 0.06}
            ]
        }
        
        result = await engine.optimize_portfolio(portfolio, "low")
        
        assert result.success is True
        assert "algorithm" in result.data
        assert result.data["algorithm"] == "quantum_annealing"

class TestTradingEngine:
    """Test Trading Engine"""
    
    @pytest.fixture
    def trading_config(self):
        """Trading configuration"""
        return {
            "max_trades_per_day": 100,
            "min_trade_size": 1000,
            "execution_delay": 0.1
        }
    
    @pytest.mark.asyncio
    async def test_trading_engine_initialization(self, trading_config):
        """Test trading engine initialization"""
        engine = TradingEngine(trading_config)
        await engine.initialize()
        
        assert engine.is_running is False
        assert engine.is_automated is False
        assert len(engine.strategies) > 0
    
    @pytest.mark.asyncio
    async def test_order_creation(self, trading_config):
        """Test order creation"""
        engine = TradingEngine(trading_config)
        await engine.initialize()
        
        # Mock market data
        engine.market_data = {"AAPL": {"price": 150.0}}
        
        order = await engine._create_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            order_type=OrderType.MARKET
        )
        
        assert order is not None
        assert order.symbol == "AAPL"
        assert order.side == OrderSide.BUY
        assert order.quantity == 100
        assert order.order_type == OrderType.MARKET
    
    @pytest.mark.asyncio
    async def test_risk_limit_check(self, trading_config):
        """Test risk limit checking"""
        engine = TradingEngine(trading_config)
        await engine.initialize()
        
        # Mock daily trades
        engine.filled_orders = [Mock() for _ in range(50)]  # 50 trades today
        
        can_trade = await engine._check_risk_limits("AAPL", "buy", 0.8)
        
        assert isinstance(can_trade, bool)

class TestRiskManager:
    """Test Risk Manager"""
    
    @pytest.fixture
    def risk_config(self):
        """Risk configuration"""
        return {
            "max_portfolio_var": 0.05,
            "max_position_var": 0.02,
            "confidence_levels": [0.95, 0.99]
        }
    
    @pytest.mark.asyncio
    async def test_risk_manager_initialization(self, risk_config):
        """Test risk manager initialization"""
        manager = RiskManager(risk_config)
        await manager.initialize()
        
        assert manager.is_initialized is True
        assert len(manager.risk_limits) > 0
        assert manager.current_risk_level == RiskLevel.MEDIUM
    
    @pytest.mark.asyncio
    async def test_portfolio_risk_assessment(self, risk_config):
        """Test portfolio risk assessment"""
        manager = RiskManager(risk_config)
        await manager.initialize()
        
        assessment = await manager.assess_portfolio_risk()
        
        assert assessment.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert 0 <= assessment.risk_score <= 1
        assert assessment.var_1d >= 0
        assert assessment.expected_shortfall >= assessment.var_1d

class TestComplianceEngine:
    """Test Compliance Engine"""
    
    @pytest.fixture
    def compliance_config(self):
        """Compliance configuration"""
        return {
            "compliance_mode": "strict",
            "audit_trail": True,
            "reporting_frequency": "daily"
        }
    
    @pytest.mark.asyncio
    async def test_compliance_engine_initialization(self, compliance_config):
        """Test compliance engine initialization"""
        engine = ComplianceEngine(compliance_config)
        await engine.initialize()
        
        assert engine.is_initialized is True
        assert engine.compliance_level.value == "strict"
        assert engine.audit_trail_enabled is True
        assert len(engine.compliance_rules) > 0
    
    @pytest.mark.asyncio
    async def test_compliance_check(self, compliance_config):
        """Test compliance checking"""
        engine = ComplianceEngine(compliance_config)
        await engine.initialize()
        
        # Mock portfolio data
        engine.position_data = {
            "total_value": 1000000,
            "positions": {
                "AAPL": {"quantity": 1000, "market_value": 150000},
                "GOOGL": {"quantity": 200, "market_value": 560000}
            }
        }
        engine.trade_data = []
        
        is_compliant = await engine.check_compliance()
        
        assert isinstance(is_compliant, bool)
        assert len(engine.compliance_checks) > 0
    
    @pytest.mark.asyncio
    async def test_audit_record_creation(self, compliance_config):
        """Test audit record creation"""
        engine = ComplianceEngine(compliance_config)
        await engine.initialize()
        
        await engine._create_audit_record(
            action="test_action",
            user="test_user",
            details={"test": "data"}
        )
        
        assert len(engine.audit_records) > 0
        audit_record = engine.audit_records[-1]
        assert audit_record.action == "test_action"
        assert audit_record.user == "test_user"

class TestAnalyticsEngine:
    """Test Analytics Engine"""
    
    @pytest.mark.asyncio
    async def test_analytics_engine_initialization(self):
        """Test analytics engine initialization"""
        engine = AnalyticsEngine()
        await engine.initialize()
        
        assert engine.is_initialized is True
        assert len(engine.market_data) > 0
        assert len(engine.dashboards) > 0
    
    @pytest.mark.asyncio
    async def test_technical_analysis(self):
        """Test technical analysis"""
        engine = AnalyticsEngine()
        await engine.initialize()
        
        # Add test market data
        engine.market_data = {
            "AAPL": Mock()
        }
        
        # Mock the market data DataFrame
        import pandas as pd
        dates = pd.date_range(start='2023-01-01', end='2024-11-03', freq='1H')
        mock_data = pd.DataFrame({
            'timestamp': dates,
            'open': range(len(dates)),
            'high': range(len(dates)),
            'low': range(len(dates)),
            'close': range(len(dates)),
            'volume': [1000] * len(dates),
            'sma_10': range(len(dates)),
            'sma_20': range(len(dates)),
            'rsi': [50] * len(dates),
            'macd': [0] * len(dates),
            'macd_signal': [0] * len(dates),
            'volatility': [0.02] * len(dates)
        })
        engine.market_data["AAPL"] = mock_data
        
        result = await engine.run_technical_analysis("AAPL")
        
        assert "symbol" in result
        assert result["symbol"] == "AAPL"
        assert "price_data" in result
        assert "signals" in result
        assert "confidence" in result

# Integration Tests
class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.asyncio
    async def test_full_system_initialization(self):
        """Test full system initialization"""
        config = {
            "system": {"quantum_enabled": True, "auto_trading": False},
            "quantum": {"shots": 512},
            "trading": {"max_trades_per_day": 50},
            "risk": {"max_portfolio_var": 0.05},
            "compliance": {"compliance_mode": "standard"}
        }
        
        orchestrator = QuantumHedgeFundOrchestrator()
        orchestrator.config = config
        
        # Mock all initialization methods
        with patch.multiple(orchestrator,
                          quantum_engine=Mock(initialize=AsyncMock()),
                          quantum_ml_engine=Mock(initialize=AsyncMock()),
                          trading_engine=Mock(initialize=AsyncMock()),
                          analytics_engine=Mock(initialize=AsyncMock()),
                          risk_manager=Mock(initialize=AsyncMock()),
                          compliance_engine=Mock(initialize=AsyncMock())):
            
            result = await orchestrator.initialize()
        
        assert result is True
        assert orchestrator.is_running is True

# Performance Tests
class TestPerformance:
    """Performance tests"""
    
    @pytest.mark.asyncio
    async def test_quantum_optimization_performance(self):
        """Test quantum optimization performance"""
        import time
        
        engine = QuantumEngine({"shots": 1024})
        await engine.initialize()
        
        portfolio = {
            "assets": [
                {"symbol": f"ASSET_{i}", "expected_return": 0.05}
                for i in range(10)
            ]
        }
        
        start_time = time.time()
        result = await engine.optimize_portfolio(portfolio)
        end_time = time.time()
        
        optimization_time = end_time - start_time
        
        assert result.success is True
        assert optimization_time < 10.0  # Should complete within 10 seconds
    
    @pytest.mark.asyncio
    async def test_risk_assessment_performance(self):
        """Test risk assessment performance"""
        import time
        
        manager = RiskManager({"max_portfolio_var": 0.05})
        await manager.initialize()
        
        start_time = time.time()
        assessment = await manager.assess_portfolio_risk()
        end_time = time.time()
        
        assessment_time = end_time - start_time
        
        assert assessment.risk_level is not None
        assert assessment_time < 5.0  # Should complete within 5 seconds

if __name__ == "__main__":
    pytest.main([__file__, "-v"])