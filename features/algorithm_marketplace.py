"""
Algorithm Marketplace - AI Trading Algorithm Marketplace
Innovatsion AI trading algoritmlari marketplace tizimi

Bu modul quyidagi xususiyatlarni ta'minlaydi:
- AI trading algorithm marketplace
- Algorithm performance tracking
- Backtesting infrastructure
- Real-time algorithm deployment
- Algorithm subscription system
- Performance-based ranking
- Community algorithm sharing
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np
import pandas as pd
from pathlib import Path
import pickle
import hashlib
import uuid

# Configuration and constants
class AlgorithmType(Enum):
    """Algorithm types"""
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    ARBITRAGE = "arbitrage"
    MARKET_MAKING = "market_making"
    SCALPING = "scalping"
    SWING_TRADING = "swing_trading"
    MOMENTUM = "momentum"
    GRID_TRADING = "grid_trading"
    DCA_BOT = "dca_bot"
    AI_PATTERN_RECOGNITION = "ai_pattern_recognition"
    QUANTITATIVE = "quantitative"
    RISK_PARITY = "risk_parity"

class AlgorithmStatus(Enum):
    """Algorithm status"""
    DRAFT = "draft"
    TESTING = "testing"
    LIVE = "live"
    PAUSED = "paused"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class SubscriptionTier(Enum):
    """Subscription tiers"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class PerformanceMetric(Enum):
    """Performance metrics"""
    TOTAL_RETURN = "total_return"
    SHARPE_RATIO = "sharpe_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    WIN_RATE = "win_rate"
    PROFIT_FACTOR = "profit_factor"
    SORTINO_RATIO = "sortino_ratio"
    CALMAR_RATIO = "calmar_ratio"
    BETA = "beta"
    ALPHA = "alpha"
    INFORMATION_RATIO = "information_ratio"

@dataclass
class AlgorithmMetadata:
    """Algorithm metadata structure"""
    name: str
    description: str
    version: str
    algorithm_type: AlgorithmType
    author: str
    tags: List[str]
    min_capital: float
    max_capital: float
    supported_markets: List[str]
    risk_level: float
    expected_return: float
    created_at: datetime
    updated_at: datetime
    license: str = "MIT"
    documentation_url: Optional[str] = None
    source_code_url: Optional[str] = None

@dataclass
class AlgorithmPerformance:
    """Algorithm performance data structure"""
    algorithm_id: str
    time_period: str
    start_date: datetime
    end_date: datetime
    total_trades: int
    winning_trades: int
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    sortino_ratio: float
    calmar_ratio: float
    beta: float
    alpha: float
    var_95: float  # Value at Risk 95%
    cagr: float  # Compound Annual Growth Rate
    avg_trade_duration: float  # hours
    market_conditions: str

@dataclass
class AlgorithmSubscription:
    """Algorithm subscription structure"""
    subscription_id: str
    user_id: str
    algorithm_id: str
    tier: SubscriptionTier
    start_date: datetime
    end_date: datetime
    status: str
    monthly_fee: float
    performance_fee: float
    min_performance_fee: float

class AlgorithmBacktester:
    """Advanced backtesting engine for trading algorithms"""
    
    def __init__(self):
        self.market_data = MarketDataProvider()
        self.performance_calculator = PerformanceCalculator()
    
    async def run_backtest(self, algorithm_code: str, parameters: Dict[str, Any], 
                          start_date: datetime, end_date: datetime, 
                          initial_capital: float = 10000) -> AlgorithmPerformance:
        """Run comprehensive backtest for algorithm"""
        try:
            # Load market data
            market_data = await self.market_data.get_historical_data(
                parameters.get("symbol", "BTCUSDT"), 
                start_date, 
                end_date
            )
            
            # Initialize backtest environment
            portfolio = {
                "cash": initial_capital,
                "positions": {},
                "trades": [],
                "equity_curve": []
            }
            
            # Execute algorithm
            trading_signals = await self._execute_algorithm(algorithm_code, market_data, parameters)
            
            # Process trades and calculate performance
            backtest_results = await self._process_trades(trading_signals, portfolio, market_data)
            
            # Calculate performance metrics
            performance = self.performance_calculator.calculate_performance_metrics(
                backtest_results, initial_capital
            )
            
            return performance
            
        except Exception as e:
            logging.error(f"Backtest error: {e}")
            raise
    
    async def _execute_algorithm(self, algorithm_code: str, market_data: pd.DataFrame, 
                               parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute trading algorithm logic"""
        # This would execute the actual algorithm code
        # For demo, we'll simulate algorithm logic
        
        signals = []
        
        # Simple moving average crossover logic
        short_window = parameters.get("short_window", 10)
        long_window = parameters.get("long_window", 30)
        
        market_data["MA_short"] = market_data["close"].rolling(window=short_window).mean()
        market_data["MA_long"] = market_data["close"].rolling(window=long_window).mean()
        
        for i in range(long_window, len(market_data)):
            current_price = market_data.iloc[i]["close"]
            ma_short = market_data.iloc[i]["MA_short"]
            ma_long = market_data.iloc[i]["MA_long"]
            
            signal = {
                "timestamp": market_data.iloc[i]["timestamp"],
                "price": current_price,
                "action": "hold",
                "confidence": 0.0
            }
            
            # Generate buy signal
            if ma_short > ma_long and market_data.iloc[i-1]["MA_short"] <= market_data.iloc[i-1]["MA_long"]:
                signal["action"] = "buy"
                signal["confidence"] = 0.7
                signal["amount"] = parameters.get("position_size", 0.1)
            
            # Generate sell signal
            elif ma_short < ma_long and market_data.iloc[i-1]["MA_short"] >= market_data.iloc[i-1]["MA_long"]:
                signal["action"] = "sell"
                signal["confidence"] = 0.7
                signal["amount"] = parameters.get("position_size", 0.1)
            
            signals.append(signal)
        
        return signals
    
    async def _process_trades(self, signals: List[Dict], portfolio: Dict, 
                            market_data: pd.DataFrame) -> Dict[str, Any]:
        """Process trading signals and update portfolio"""
        processed_data = {
            "trades": [],
            "equity_curve": [],
            "positions": portfolio["positions"]
        }
        
        for signal in signals:
            if signal["action"] in ["buy", "sell"]:
                # Process trade
                trade = {
                    "timestamp": signal["timestamp"],
                    "action": signal["action"],
                    "price": signal["price"],
                    "amount": signal.get("amount", 0.1),
                    "confidence": signal["confidence"]
                }
                
                # Execute trade simulation
                executed_trade = await self._execute_trade(trade, portfolio, market_data)
                
                if executed_trade:
                    processed_data["trades"].append(executed_trade)
                    processed_data["equity_curve"].append(self._calculate_portfolio_value(portfolio))
        
        return processed_data
    
    async def _execute_trade(self, trade: Dict, portfolio: Dict, market_data: pd.DataFrame) -> Optional[Dict]:
        """Execute individual trade"""
        try:
            price = trade["price"]
            amount = trade["amount"]
            action = trade["action"]
            
            if action == "buy":
                cost = price * amount
                if portfolio["cash"] >= cost:
                    portfolio["cash"] -= cost
                    if "BTC" not in portfolio["positions"]:
                        portfolio["positions"]["BTC"] = {"amount": 0, "avg_price": 0}
                    
                    current_amount = portfolio["positions"]["BTC"]["amount"]
                    current_avg_price = portfolio["positions"]["BTC"]["avg_price"]
                    
                    new_amount = current_amount + amount
                    new_avg_price = (current_avg_price * current_amount + price * amount) / new_amount
                    
                    portfolio["positions"]["BTC"]["amount"] = new_amount
                    portfolio["positions"]["BTC"]["avg_price"] = new_avg_price
                    
                    return {**trade, "success": True, "cost": cost}
            
            elif action == "sell":
                if "BTC" in portfolio["positions"] and portfolio["positions"]["BTC"]["amount"] >= amount:
                    proceeds = price * amount
                    portfolio["cash"] += proceeds
                    portfolio["positions"]["BTC"]["amount"] -= amount
                    
                    if portfolio["positions"]["BTC"]["amount"] == 0:
                        del portfolio["positions"]["BTC"]
                    
                    return {**trade, "success": True, "proceeds": proceeds}
            
            return {**trade, "success": False, "reason": "Insufficient funds or positions"}
            
        except Exception as e:
            return {**trade, "success": False, "error": str(e)}
    
    def _calculate_portfolio_value(self, portfolio: Dict) -> float:
        """Calculate current portfolio value"""
        total_value = portfolio["cash"]
        
        # Add position values (simplified - would need current prices)
        for symbol, position in portfolio["positions"].items():
            total_value += position["amount"] * position["avg_price"]  # Using avg price as proxy
        
        return total_value

class MarketDataProvider:
    """Market data provider for backtesting"""
    
    async def get_historical_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get historical market data"""
        # Simulate historical data for demo
        np.random.seed(42)  # For reproducible results
        
        # Generate date range
        date_range = pd.date_range(start=start_date, end=end_date, freq='H')
        
        # Generate price data (random walk)
        initial_price = 50000  # BTC starting price
        returns = np.random.normal(0.001, 0.02, len(date_range))  # 0.1% drift, 2% volatility
        prices = [initial_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        # Create OHLCV data
        data = []
        for i, (timestamp, price) in enumerate(zip(date_range, prices)):
            # Generate OHLC from price
            high = price * (1 + abs(np.random.normal(0, 0.005)))
            low = price * (1 - abs(np.random.normal(0, 0.005)))
            open_price = prices[i-1] if i > 0 else price
            close_price = price
            
            # Generate volume
            volume = np.random.uniform(100, 1000)
            
            data.append({
                "timestamp": timestamp,
                "open": open_price,
                "high": high,
                "low": low,
                "close": close_price,
                "volume": volume
            })
        
        return pd.DataFrame(data)

class PerformanceCalculator:
    """Calculate comprehensive performance metrics"""
    
    def calculate_performance_metrics(self, backtest_results: Dict, initial_capital: float) -> AlgorithmPerformance:
        """Calculate all performance metrics from backtest results"""
        trades = backtest_results["trades"]
        equity_curve = backtest_results["equity_curve"]
        
        if not equity_curve:
            raise ValueError("No equity curve data available")
        
        # Basic metrics
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t.get("proceeds", 0) > t.get("cost", 0)])
        
        # Calculate returns
        final_value = equity_curve[-1]
        total_return = (final_value - initial_capital) / initial_capital
        
        # Annualized return
        start_date = datetime.now() - timedelta(days=365)
        days = (datetime.now() - start_date).days
        annualized_return = (1 + total_return) ** (365 / days) - 1
        
        # Calculate equity series returns
        equity_returns = np.diff(equity_curve) / equity_curve[:-1]
        
        # Volatility (annualized)
        volatility = np.std(equity_returns) * np.sqrt(365 * 24)  # Assuming hourly data
        
        # Sharpe ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02
        sharpe_ratio = (annualized_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # Maximum drawdown
        cumulative_returns = np.array(equity_curve) / initial_capital
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = abs(np.min(drawdown))
        
        # Win rate
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Profit factor
        gross_profit = sum([t.get("proceeds", 0) - t.get("cost", 0) for t in trades if t.get("proceeds", 0) > t.get("cost", 0)])
        gross_loss = abs(sum([t.get("cost", 0) - t.get("proceeds", 0) for t in trades if t.get("proceeds", 0) < t.get("cost", 0)]))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Sortino ratio (downside deviation)
        downside_returns = equity_returns[equity_returns < 0]
        downside_deviation = np.std(downside_returns) * np.sqrt(365 * 24) if len(downside_returns) > 0 else 0
        sortino_ratio = (annualized_return - risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
        
        # Calmar ratio
        calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0
        
        # Beta and Alpha (simplified - would compare to market index)
        beta = 1.0  # Simplified
        alpha = annualized_return - risk_free_rate - beta * 0.1  # Simplified market premium
        
        # Value at Risk (95%)
        var_95 = np.percentile(equity_returns, 5)
        
        # CAGR
        cagr = annualized_return
        
        # Average trade duration (simplified)
        avg_trade_duration = 4.0  # hours
        
        return AlgorithmPerformance(
            algorithm_id="demo_algorithm",
            time_period="1Y",
            start_date=datetime.now() - timedelta(days=365),
            end_date=datetime.now(),
            total_trades=total_trades,
            winning_trades=winning_trades,
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            beta=beta,
            alpha=alpha,
            var_95=var_95,
            cagr=cagr,
            avg_trade_duration=avg_trade_duration,
            market_conditions="mixed"
        )

class AlgorithmRepository:
    """Algorithm storage and management"""
    
    def __init__(self):
        self.algorithms = {}
        self.performance_data = {}
        self.subscriptions = {}
        self._initialize_sample_algorithms()
    
    def _initialize_sample_algorithms(self):
        """Initialize sample algorithms for marketplace"""
        sample_algorithms = [
            {
                "id": "algo_001",
                "metadata": AlgorithmMetadata(
                    name="Golden Cross Momentum",
                    description="Simple moving average crossover strategy with momentum confirmation",
                    version="1.2.0",
                    algorithm_type=AlgorithmType.TREND_FOLLOWING,
                    author="AlgoMaster",
                    tags=["trend", "momentum", "moving_average"],
                    min_capital=1000,
                    max_capital=100000,
                    supported_markets=["BTCUSDT", "ETHUSDT", "BNBUSDT"],
                    risk_level=0.6,
                    expected_return=0.15,
                    created_at=datetime.now() - timedelta(days=30),
                    updated_at=datetime.now() - timedelta(days=5)
                )
            },
            {
                "id": "algo_002",
                "metadata": AlgorithmMetadata(
                    name="Mean Reversion Alpha",
                    description="Statistical arbitrage using Bollinger Bands and RSI",
                    version="2.1.0",
                    algorithm_type=AlgorithmType.MEAN_REVERSION,
                    author="QuantWizard",
                    tags=["mean_reversion", "bollinger", "rsi"],
                    min_capital=5000,
                    max_capital=500000,
                    supported_markets=["BTCUSDT", "ETHUSDT"],
                    risk_level=0.4,
                    expected_return=0.12,
                    created_at=datetime.now() - timedelta(days=45),
                    updated_at=datetime.now() - timedelta(days=10)
                )
            },
            {
                "id": "algo_003",
                "metadata": AlgorithmMetadata(
                    name="AI Pattern Recognition Pro",
                    description="Machine learning model for pattern recognition and signal generation",
                    version="3.0.1",
                    algorithm_type=AlgorithmType.AI_PATTERN_RECOGNITION,
                    author="ML_Trader",
                    tags=["ai", "ml", "pattern", "neural_network"],
                    min_capital=10000,
                    max_capital=1000000,
                    supported_markets=["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"],
                    risk_level=0.7,
                    expected_return=0.25,
                    created_at=datetime.now() - timedelta(days=60),
                    updated_at=datetime.now() - timedelta(days=2)
                )
            }
        ]
        
        for algo in sample_algorithms:
            self.algorithms[algo["id"]] = algo["metadata"]
    
    def store_algorithm(self, metadata: AlgorithmMetadata, code: str) -> str:
        """Store new algorithm in repository"""
        algorithm_id = f"algo_{len(self.algorithms) + 1:03d}"
        
        self.algorithms[algorithm_id] = metadata
        self.algorithms[algorithm_id].algorithm_id = algorithm_id
        
        return algorithm_id
    
    def get_algorithm(self, algorithm_id: str) -> Optional[AlgorithmMetadata]:
        """Get algorithm by ID"""
        return self.algorithms.get(algorithm_id)
    
    def update_algorithm(self, algorithm_id: str, updates: Dict[str, Any]) -> bool:
        """Update algorithm metadata"""
        if algorithm_id not in self.algorithms:
            return False
        
        algorithm = self.algorithms[algorithm_id]
        
        for key, value in updates.items():
            if hasattr(algorithm, key):
                setattr(algorithm, key, value)
        
        algorithm.updated_at = datetime.now()
        return True
    
    def delete_algorithm(self, algorithm_id: str) -> bool:
        """Delete algorithm from repository"""
        if algorithm_id in self.algorithms:
            del self.algorithms[algorithm_id]
            return True
        return False
    
    def search_algorithms(self, filters: Dict[str, Any]) -> List[AlgorithmMetadata]:
        """Search algorithms with filters"""
        results = []
        
        for algorithm in self.algorithms.values():
            match = True
            
            # Apply filters
            if "algorithm_type" in filters and algorithm.algorithm_type != filters["algorithm_type"]:
                match = False
            
            if "risk_level" in filters:
                if not (filters["risk_level"][0] <= algorithm.risk_level <= filters["risk_level"][1]):
                    match = False
            
            if "expected_return" in filters:
                if algorithm.expected_return < filters["expected_return"]:
                    match = False
            
            if "tags" in filters:
                if not any(tag.lower() in [t.lower() for t in algorithm.tags] for tag in filters["tags"]):
                    match = False
            
            if match:
                results.append(algorithm)
        
        return results

class AlgorithmMarketplace:
    """Main Algorithm Marketplace - Comprehensive trading algorithm platform"""
    
    def __init__(self):
        self.repository = AlgorithmRepository()
        self.backtester = AlgorithmBacktester()
        self.performance_calculator = PerformanceCalculator()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def publish_algorithm(self, metadata: AlgorithmMetadata, code: str, 
                              user_id: str) -> Dict[str, Any]:
        """Publish new algorithm to marketplace"""
        try:
            # Validate metadata
            validation_result = self._validate_algorithm_metadata(metadata)
            if not validation_result["valid"]:
                return {"success": False, "error": validation_result["error"]}
            
            # Store algorithm
            algorithm_id = self.repository.store_algorithm(metadata, code)
            
            # Run initial backtest
            try:
                backtest_performance = await self.backtester.run_backtest(
                    code, 
                    metadata.__dict__, 
                    datetime.now() - timedelta(days=365),
                    datetime.now(),
                    metadata.min_capital
                )
                
                # Store performance data
                self.repository.performance_data[algorithm_id] = backtest_performance
                
            except Exception as e:
                self.logger.warning(f"Backtest failed for {algorithm_id}: {e}")
            
            return {
                "success": True,
                "algorithm_id": algorithm_id,
                "message": "Algorithm successfully published to marketplace"
            }
            
        except Exception as e:
            self.logger.error(f"Algorithm publishing error: {e}")
            return {"success": False, "error": str(e)}
    
    def _validate_algorithm_metadata(self, metadata: AlgorithmMetadata) -> Dict[str, Any]:
        """Validate algorithm metadata"""
        # Check required fields
        if not metadata.name or len(metadata.name.strip()) < 3:
            return {"valid": False, "error": "Algorithm name must be at least 3 characters"}
        
        if not metadata.description or len(metadata.description.strip()) < 10:
            return {"valid": False, "error": "Description must be at least 10 characters"}
        
        if metadata.min_capital <= 0:
            return {"valid": False, "error": "Minimum capital must be positive"}
        
        if metadata.max_capital <= metadata.min_capital:
            return {"valid": False, "error": "Maximum capital must be greater than minimum"}
        
        if not (0 <= metadata.risk_level <= 1):
            return {"valid": False, "error": "Risk level must be between 0 and 1"}
        
        return {"valid": True}
    
    async def get_algorithm_details(self, algorithm_id: str) -> Dict[str, Any]:
        """Get comprehensive algorithm details"""
        try:
            algorithm = self.repository.get_algorithm(algorithm_id)
            if not algorithm:
                return {"success": False, "error": "Algorithm not found"}
            
            performance = self.repository.performance_data.get(algorithm_id)
            
            return {
                "success": True,
                "algorithm": {
                    "id": algorithm_id,
                    "metadata": algorithm,
                    "performance": performance,
                    "subscription_available": True,
                    "pricing": self._get_algorithm_pricing(algorithm)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Get algorithm details error: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_algorithm_pricing(self, metadata: AlgorithmMetadata) -> Dict[str, Any]:
        """Get algorithm pricing information"""
        base_price = max(50, metadata.expected_return * 1000)  # Dynamic pricing based on expected return
        
        return {
            "tiers": {
                "free": {
                    "monthly_fee": 0,
                    "performance_fee": 0,
                    "features": ["basic_backtest", "community_support"]
                },
                "basic": {
                    "monthly_fee": base_price,
                    "performance_fee": 0.10,
                    "features": ["live_trading", "email_support", "basic_analytics"]
                },
                "premium": {
                    "monthly_fee": base_price * 2,
                    "performance_fee": 0.15,
                    "features": ["priority_support", "advanced_analytics", "custom_parameters"]
                },
                "enterprise": {
                    "monthly_fee": base_price * 5,
                    "performance_fee": 0.20,
                    "features": ["white_label", "api_access", "dedicated_support"]
                }
            }
        }
    
    async def search_algorithms(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Search algorithms in marketplace"""
        try:
            # Parse search filters
            filters = {}
            
            if "algorithm_type" in query:
                filters["algorithm_type"] = AlgorithmType(query["algorithm_type"])
            
            if "risk_level" in query:
                filters["risk_level"] = query["risk_level"]
            
            if "min_return" in query:
                filters["expected_return"] = query["min_return"]
            
            if "tags" in query:
                filters["tags"] = query["tags"]
            
            if "min_rating" in query:
                filters["min_rating"] = query["min_rating"]
            
            # Search algorithms
            results = self.repository.search_algorithms(filters)
            
            # Add performance data and rankings
            enhanced_results = []
            for algorithm in results:
                algorithm_id = algorithm.algorithm_id if hasattr(algorithm, 'algorithm_id') else "unknown"
                performance = self.repository.performance_data.get(algorithm_id)
                
                # Calculate algorithm score
                score = self._calculate_algorithm_score(algorithm, performance)
                
                enhanced_results.append({
                    "algorithm": algorithm,
                    "performance": performance,
                    "score": score,
                    "pricing": self._get_algorithm_pricing(algorithm)
                })
            
            # Sort by score
            enhanced_results.sort(key=lambda x: x["score"], reverse=True)
            
            return {
                "success": True,
                "results_count": len(enhanced_results),
                "algorithms": enhanced_results[:50],  # Top 50 results
                "filters_applied": filters,
                "sort_criteria": "score"
            }
            
        except Exception as e:
            self.logger.error(f"Algorithm search error: {e}")
            return {"success": False, "error": str(e)}
    
    def _calculate_algorithm_score(self, metadata: AlgorithmMetadata, performance: Optional[AlgorithmPerformance]) -> float:
        """Calculate algorithm ranking score"""
        score = 0.0
        
        # Performance score (40%)
        if performance:
            # Sharpe ratio component (20%)
            sharpe_score = min(max(performance.sharpe_ratio / 3, 0), 1)  # Normalize to 0-1
            score += sharpe_score * 0.2
            
            # Win rate component (10%)
            win_rate_score = performance.win_rate
            score += win_rate_score * 0.1
            
            # Return component (10%)
            return_score = min(max(performance.total_return / 0.5, 0), 1)  # Normalize to 0-1
            score += return_score * 0.1
        
        # Metadata score (30%)
        # Expected return (15%)
        expected_return_score = min(max(metadata.expected_return / 0.3, 0), 1)
        score += expected_return_score * 0.15
        
        # Risk-adjusted return (15%)
        risk_adjusted_return = metadata.expected_return / metadata.risk_level if metadata.risk_level > 0 else 0
        risk_adjusted_score = min(max(risk_adjusted_return / 0.5, 0), 1)
        score += risk_adjusted_score * 0.15
        
        # Community score (20%)
        # Tags popularity (10%)
        popular_tags = {"ai", "ml", "neural_network", "quantitative", "arbitrage"}
        tag_score = len([tag for tag in metadata.tags if tag.lower() in popular_tags]) / len(metadata.tags)
        score += tag_score * 0.1
        
        # Recency score (10%)
        days_since_update = (datetime.now() - metadata.updated_at).days
        recency_score = max(0, 1 - (days_since_update / 365))  # Decay over year
        score += recency_score * 0.1
        
        # Subscription potential (10%)
        # Higher minimum capital indicates more serious users
        capital_score = min(max((metadata.min_capital - 1000) / 9000, 0), 1)
        score += capital_score * 0.1
        
        return min(score, 1.0)
    
    async def run_algorithm_backtest(self, algorithm_id: str, parameters: Dict[str, Any], 
                                   start_date: datetime, end_date: datetime, 
                                   initial_capital: float) -> Dict[str, Any]:
        """Run backtest for existing algorithm"""
        try:
            algorithm = self.repository.get_algorithm(algorithm_id)
            if not algorithm:
                return {"success": False, "error": "Algorithm not found"}
            
            # Run backtest
            performance = await self.backtester.run_backtest(
                "algorithm_code",  # Would load actual code
                {**algorithm.__dict__, **parameters},
                start_date,
                end_date,
                initial_capital
            )
            
            return {
                "success": True,
                "algorithm_id": algorithm_id,
                "performance": performance,
                "backtest_parameters": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "initial_capital": initial_capital
                }
            }
            
        except Exception as e:
            self.logger.error(f"Backtest execution error: {e}")
            return {"success": False, "error": str(e)}
    
    async def subscribe_to_algorithm(self, user_id: str, algorithm_id: str, 
                                   tier: SubscriptionTier) -> Dict[str, Any]:
        """Subscribe to algorithm"""
        try:
            algorithm = self.repository.get_algorithm(algorithm_id)
            if not algorithm:
                return {"success": False, "error": "Algorithm not found"}
            
            # Get pricing for tier
            pricing = self._get_algorithm_pricing(algorithm)
            tier_pricing = pricing["tiers"][tier.value]
            
            # Create subscription
            subscription_id = f"sub_{uuid.uuid4().hex[:8]}"
            subscription = AlgorithmSubscription(
                subscription_id=subscription_id,
                user_id=user_id,
                algorithm_id=algorithm_id,
                tier=tier,
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=30),  # Monthly subscription
                status="active",
                monthly_fee=tier_pricing["monthly_fee"],
                performance_fee=tier_pricing["performance_fee"],
                min_performance_fee=0
            )
            
            self.repository.subscriptions[subscription_id] = subscription
            
            return {
                "success": True,
                "subscription": subscription,
                "message": f"Successfully subscribed to {algorithm.name}"
            }
            
        except Exception as e:
            self.logger.error(f"Subscription error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_subscriptions(self, user_id: str) -> Dict[str, Any]:
        """Get user's algorithm subscriptions"""
        try:
            user_subscriptions = [
                sub for sub in self.repository.subscriptions.values()
                if sub.user_id == user_id
            ]
            
            # Add algorithm details
            enriched_subscriptions = []
            for sub in user_subscriptions:
                algorithm = self.repository.get_algorithm(sub.algorithm_id)
                if algorithm:
                    enriched_subscriptions.append({
                        "subscription": sub,
                        "algorithm": algorithm
                    })
            
            return {
                "success": True,
                "user_id": user_id,
                "subscriptions": enriched_subscriptions,
                "total_subscriptions": len(enriched_subscriptions),
                "active_subscriptions": len([s for s in user_subscriptions if s.status == "active"])
            }
            
        except Exception as e:
            self.logger.error(f"Get subscriptions error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_marketplace_statistics(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        try:
            total_algorithms = len(self.repository.algorithms)
            
            # Algorithm type distribution
            type_distribution = {}
            for algorithm in self.repository.algorithms.values():
                algo_type = algorithm.algorithm_type.value
                type_distribution[algo_type] = type_distribution.get(algo_type, 0) + 1
            
            # Performance statistics
            performances = list(self.repository.performance_data.values())
            if performances:
                avg_return = np.mean([p.total_return for p in performances])
                avg_sharpe = np.mean([p.sharpe_ratio for p in performances])
                avg_win_rate = np.mean([p.win_rate for p in performances])
            else:
                avg_return = avg_sharpe = avg_win_rate = 0
            
            # Subscription statistics
            total_subscriptions = len(self.repository.subscriptions)
            active_subscriptions = len([s for s in self.repository.subscriptions.values() if s.status == "active"])
            
            return {
                "success": True,
                "statistics": {
                    "total_algorithms": total_algorithms,
                    "algorithm_types": type_distribution,
                    "average_return": avg_return,
                    "average_sharpe_ratio": avg_sharpe,
                    "average_win_rate": avg_win_rate,
                    "total_subscriptions": total_subscriptions,
                    "active_subscriptions": active_subscriptions,
                    "subscription_rate": active_subscriptions / total_algorithms if total_algorithms > 0 else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Marketplace statistics error: {e}")
            return {"success": False, "error": str(e)}

# Demo function
async def demo_algorithm_marketplace():
    """Demo function for Algorithm Marketplace"""
    marketplace = AlgorithmMarketplace()
    
    print("=== Algorithm Marketplace Demo ===")
    
    # Demo 1: Search Algorithms
    print("\n1. Algorithm Search:")
    search_results = await marketplace.search_algorithms({
        "algorithm_type": "trend_following",
        "risk_level": [0.3, 0.8],
        "min_return": 0.10
    })
    print(json.dumps(search_results, indent=2, ensure_ascii=False))
    
    # Demo 2: Get Algorithm Details
    print("\n2. Algorithm Details:")
    algorithm_details = await marketplace.get_algorithm_details("algo_001")
    print(json.dumps(algorithm_details, indent=2, ensure_ascii=False))
    
    # Demo 3: Run Backtest
    print("\n3. Algorithm Backtest:")
    backtest = await marketplace.run_algorithm_backtest(
        "algo_001",
        {"short_window": 10, "long_window": 30, "position_size": 0.1},
        datetime.now() - timedelta(days=90),
        datetime.now(),
        10000
    )
    print(json.dumps(backtest, indent=2, ensure_ascii=False))
    
    # Demo 4: Subscribe to Algorithm
    print("\n4. Algorithm Subscription:")
    subscription = await marketplace.subscribe_to_algorithm(
        "user_123",
        "algo_001",
        SubscriptionTier.PREMIUM
    )
    print(json.dumps(subscription, indent=2, ensure_ascii=False))
    
    # Demo 5: Marketplace Statistics
    print("\n5. Marketplace Statistics:")
    statistics = await marketplace.get_marketplace_statistics()
    print(json.dumps(statistics, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_algorithm_marketplace())