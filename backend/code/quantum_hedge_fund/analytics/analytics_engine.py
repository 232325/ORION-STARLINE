"""
Analytics Engine
Bozor tahlili, monitoring va reporting tizimi
"""
import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

@dataclass
class MarketMetrics:
    """Bozor metrikalari"""
    symbol: str
    price: float
    volume: float
    volatility: float
    momentum: float
    rsi: float
    timestamp: datetime

@dataclass
class PortfolioMetrics:
    """Portfolio metrikalari"""
    total_value: float
    daily_pnl: float
    monthly_pnl: float
    daily_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float

class AnalyticsEngine:
    """Analytics Engine"""
    
    def __init__(self):
        self.logger = logging.getLogger("analytics_engine")
        self.is_initialized = False
        
        # Data storage
        self.market_data: Dict[str, pd.DataFrame] = {}
        self.portfolio_history: List[Dict] = []
        self.performance_metrics: Dict[str, Any] = {}
        self.risk_metrics: Dict[str, Any] = {}
        
        # Real-time monitoring
        self.active_alerts: List[Dict] = []
        self.dashboards: Dict[str, Dict] = {}
        
        # Analysis cache
        self.analysis_cache: Dict[str, Any] = {}
        self.cache_timeout = 300  # 5 minutes
        
    async def initialize(self):
        """Analytics Engine'ni ishga tushirish"""
        try:
            self.logger.info("Analytics Engine ishga tushirilmoqda...")
            
            # Load market data
            await self._load_market_data()
            
            # Initialize dashboards
            await self._initialize_dashboards()
            
            # Setup real-time monitoring
            await self._setup_monitoring()
            
            self.is_initialized = True
            self.logger.info("✅ Analytics Engine muvaffaqiyatli ishga tushdi!")
            
        except Exception as e:
            self.logger.error(f"Analytics Engine ishga tushirishda xato: {e}")
            raise
    
    async def _load_market_data(self):
        """Market data yuklash"""
        try:
            # Generate comprehensive market data
            symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "NFLX", "SPY", "QQQ"]
            start_date = datetime(2023, 1, 1)
            end_date = datetime(2024, 11, 3)
            
            for symbol in symbols:
                self.market_data[symbol] = await self._generate_market_data(symbol, start_date, end_date)
            
            self.logger.info(f"Market data {len(symbols)} symbol uchun yuklandi")
            
        except Exception as e:
            self.logger.error(f"Market data yuklashda xato: {e}")
    
    async def _generate_market_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Market data generation"""
        try:
            # Generate hourly data
            dates = pd.date_range(start=start_date, end=end_date, freq='1H')
            n_periods = len(dates)
            
            # Set seed for reproducibility
            np.random.seed(hash(symbol) % 2**32)
            
            # Generate price data with realistic patterns
            base_price = 100 + (hash(symbol) % 100)  # Different base prices for different symbols
            
            # Add trend, seasonality, and noise
            trend = np.linspace(0, 0.5, n_periods)  # Long-term trend
            seasonal = 0.1 * np.sin(2 * np.pi * np.arange(n_periods) / (24 * 7))  # Weekly seasonality
            noise = np.random.normal(0, 0.02, n_periods)  # Random noise
            
            # Generate returns
            returns = trend + seasonal + noise
            returns[0] = 0  # First return is 0
            
            # Calculate prices
            prices = base_price * np.exp(np.cumsum(returns))
            
            # Generate OHLC data
            data = pd.DataFrame({
                'timestamp': dates,
                'open': prices * (1 + np.random.normal(0, 0.001, n_periods)),
                'high': None,
                'low': None,
                'close': prices,
                'volume': np.random.lognormal(10, 1, n_periods)  # Log-normal volume
            })
            
            # Calculate realistic HLC
            intraday_volatility = 0.005
            data['high'] = data['open'] * (1 + np.abs(np.random.normal(0, intraday_volatility, n_periods)))
            data['low'] = data['open'] * (1 - np.abs(np.random.normal(0, intraday_volatility, n_periods)))
            
            # Ensure HLC relationships
            data['high'] = np.maximum(data['high'], np.maximum(data['open'], data['close']))
            data['low'] = np.minimum(data['low'], np.minimum(data['open'], data['close']))
            
            # Add technical indicators
            data = self._add_technical_indicators(data)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Market data generationda xato: {e}")
            return pd.DataFrame()
    
    def _add_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Technical indicators qo'shish"""
        try:
            # Moving averages
            data['sma_10'] = data['close'].rolling(10).mean()
            data['sma_20'] = data['close'].rolling(20).mean()
            data['sma_50'] = data['close'].rolling(50).mean()
            data['ema_12'] = data['close'].ewm(span=12).mean()
            data['ema_26'] = data['close'].ewm(span=26).mean()
            
            # MACD
            data['macd'] = data['ema_12'] - data['ema_26']
            data['macd_signal'] = data['macd'].ewm(span=9).mean()
            data['macd_histogram'] = data['macd'] - data['macd_signal']
            
            # RSI
            data['rsi'] = self._calculate_rsi(data['close'])
            
            # Bollinger Bands
            data['bb_middle'] = data['close'].rolling(20).mean()
            bb_std = data['close'].rolling(20).std()
            data['bb_upper'] = data['bb_middle'] + (bb_std * 2)
            data['bb_lower'] = data['bb_middle'] - (bb_std * 2)
            
            # Stochastic
            low_min = data['low'].rolling(14).min()
            high_max = data['high'].rolling(14).max()
            data['stoch_k'] = 100 * (data['close'] - low_min) / (high_max - low_min)
            data['stoch_d'] = data['stoch_k'].rolling(3).mean()
            
            # Volume indicators
            data['volume_sma'] = data['volume'].rolling(20).mean()
            data['volume_ratio'] = data['volume'] / data['volume_sma']
            
            # Price indicators
            data['price_momentum'] = data['close'].pct_change(5)
            data['price_acceleration'] = data['price_momentum'].diff()
            
            # Volatility
            data['volatility'] = data['close'].pct_change().rolling(20).std()
            
            return data
            
        except Exception as e:
            self.logger.error(f"Technical indicators qo'shishda xato: {e}")
            return data
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI calculation"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            self.logger.error(f"RSI calculationda xato: {e}")
            return pd.Series(index=prices.index, dtype=float)
    
    async def _initialize_dashboards(self):
        """Dashboardlarni ishga tushirish"""
        try:
            self.dashboards = {
                "portfolio_overview": {
                    "title": "Portfolio Overview",
                    "widgets": ["total_value", "daily_pnl", "win_rate", "sharpe_ratio"]
                },
                "market_analysis": {
                    "title": "Market Analysis",
                    "widgets": ["volatility_heatmap", "momentum_radar", "sector_rotation"]
                },
                "risk_monitor": {
                    "title": "Risk Monitor",
                    "widgets": ["var_gauge", "drawdown_chart", "correlation_matrix"]
                },
                "strategy_performance": {
                    "title": "Strategy Performance",
                    "widgets": ["strategy_comparison", "quantum_advantage", "signal_accuracy"]
                }
            }
            
            self.logger.info("Dashboardlar muvaffaqiyatli ishga tushirildi")
            
        except Exception as e:
            self.logger.error(f"Dashboard initializationda xato: {e}")
    
    async def _setup_monitoring(self):
        """Real-time monitoring sozlamasini o'rnatish"""
        try:
            # Start monitoring tasks
            asyncio.create_task(self._monitor_market_conditions())
            asyncio.create_task(self._monitor_portfolio_health())
            asyncio.create_task(self._generate_alerts())
            
            self.logger.info("Real-time monitoring muvaffaqiyatli sozlandi")
            
        except Exception as e:
            self.logger.error(f"Monitoring setupda xato: {e}")
    
    async def run_technical_analysis(self, symbol: str, timeframe: str = "1h") -> Dict:
        """Technical analysis o'tkazish"""
        try:
            self.logger.info(f"{symbol} uchun technical analysis boshlanmoqda...")
            
            if symbol not in self.market_data:
                return {"error": f"Symbol {symbol} topilmadi"}
            
            data = self.market_data[symbol]
            
            # Calculate comprehensive technical indicators
            analysis = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "price_data": {
                    "current_price": float(data['close'].iloc[-1]),
                    "open_price": float(data['open'].iloc[-1]),
                    "high_24h": float(data['high'].rolling(24).max().iloc[-1]),
                    "low_24h": float(data['low'].rolling(24).min().iloc[-1]),
                    "volume": float(data['volume'].iloc[-1])
                },
                "moving_averages": {
                    "sma_10": float(data['sma_10'].iloc[-1]),
                    "sma_20": float(data['sma_20'].iloc[-1]),
                    "sma_50": float(data['sma_50'].iloc[-1]),
                    "ema_12": float(data['ema_12'].iloc[-1]),
                    "ema_26": float(data['ema_26'].iloc[-1])
                },
                "momentum_indicators": {
                    "rsi": float(data['rsi'].iloc[-1]),
                    "macd": float(data['macd'].iloc[-1]),
                    "macd_signal": float(data['macd_signal'].iloc[-1]),
                    "macd_histogram": float(data['macd_histogram'].iloc[-1]),
                    "stoch_k": float(data['stoch_k'].iloc[-1]),
                    "stoch_d": float(data['stoch_d'].iloc[-1])
                },
                "volatility_indicators": {
                    "bollinger_position": self._calculate_bollinger_position(data),
                    "volatility": float(data['volatility'].iloc[-1]),
                    "atr": self._calculate_atr(data)
                },
                "volume_analysis": {
                    "volume_trend": self._analyze_volume_trend(data),
                    "volume_price_confirmation": self._volume_price_confirmation(data)
                },
                "signals": await self._generate_technical_signals(data),
                "confidence": 0.85
            }
            
            self.logger.info(f"✅ Technical analysis yakunlandi: {symbol}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Technical analysisda xato: {e}")
            return {"error": str(e)}
    
    def _calculate_bollinger_position(self, data: pd.DataFrame) -> float:
        """Bollinger Band pozitsiyasini hisoblash"""
        try:
            current_price = data['close'].iloc[-1]
            bb_upper = data['bb_upper'].iloc[-1]
            bb_lower = data['bb_lower'].iloc[-1]
            
            position = (current_price - bb_lower) / (bb_upper - bb_lower)
            return float(position)
            
        except Exception as e:
            self.logger.error(f"Bollinger position calculationda xato: {e}")
            return 0.5
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """ATR hisoblash"""
        try:
            high_low = data['high'] - data['low']
            high_close = np.abs(data['high'] - data['close'].shift())
            low_close = np.abs(data['low'] - data['close'].shift())
            
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = true_range.rolling(period).mean().iloc[-1]
            
            return float(atr)
            
        except Exception as e:
            self.logger.error(f"ATR calculationda xato: {e}")
            return 0.0
    
    def _analyze_volume_trend(self, data: pd.DataFrame) -> str:
        """Volume trend tahlili"""
        try:
            recent_volume = data['volume'].tail(10).mean()
            historical_volume = data['volume'].tail(50).mean()
            
            if recent_volume > historical_volume * 1.2:
                return "increasing"
            elif recent_volume < historical_volume * 0.8:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            self.logger.error(f"Volume trend analysisda xato: {e}")
            return "unknown"
    
    def _volume_price_confirmation(self, data: pd.DataFrame) -> str:
        """Volume-price confirmation tahlili"""
        try:
            price_change = data['close'].pct_change().tail(10)
            volume_change = data['volume'].pct_change().tail(10)
            
            # Check if price and volume are moving in same direction
            price_direction = np.sign(price_change.mean())
            volume_direction = np.sign(volume_change.mean())
            
            if price_direction == volume_direction:
                return "confirmed"
            else:
                return "divergence"
                
        except Exception as e:
            self.logger.error(f"Volume-price confirmationda xato: {e}")
            return "unknown"
    
    async def _generate_technical_signals(self, data: pd.DataFrame) -> Dict:
        """Technical signals generation"""
        try:
            signals = {
                "trend_signal": await self._trend_signal(data),
                "momentum_signal": await self._momentum_signal(data),
                "volume_signal": await self._volume_signal(data),
                "volatility_signal": await self._volatility_signal(data)
            }
            
            # Combine signals
            combined_signal = self._combine_signals(signals)
            
            return {
                **signals,
                "combined_signal": combined_signal,
                "signal_strength": self._calculate_signal_strength(signals)
            }
            
        except Exception as e:
            self.logger.error(f"Technical signals generationda xato: {e}")
            return {"combined_signal": "hold", "signal_strength": 0.0}
    
    async def _trend_signal(self, data: pd.DataFrame) -> Dict:
        """Trend signal generation"""
        try:
            current_price = data['close'].iloc[-1]
            sma_20 = data['sma_20'].iloc[-1]
            sma_50 = data['sma_50'].iloc[-1]
            
            if current_price > sma_20 > sma_50:
                signal = "bullish"
                strength = (current_price - sma_50) / sma_50
            elif current_price < sma_20 < sma_50:
                signal = "bearish"
                strength = (sma_50 - current_price) / sma_50
            else:
                signal = "neutral"
                strength = 0.0
            
            return {
                "signal": signal,
                "strength": float(strength),
                "confidence": min(abs(strength) * 10, 1.0)
            }
            
        except Exception as e:
            self.logger.error(f"Trend signal generationda xato: {e}")
            return {"signal": "neutral", "strength": 0.0, "confidence": 0.0}
    
    async def _momentum_signal(self, data: pd.DataFrame) -> Dict:
        """Momentum signal generation"""
        try:
            rsi = data['rsi'].iloc[-1]
            macd = data['macd'].iloc[-1]
            macd_signal = data['macd_signal'].iloc[-1]
            
            signals = []
            
            # RSI signal
            if rsi > 70:
                signals.append({"signal": "bearish", "weight": 0.3})
            elif rsi < 30:
                signals.append({"signal": "bullish", "weight": 0.3})
            else:
                signals.append({"signal": "neutral", "weight": 0.1})
            
            # MACD signal
            if macd > macd_signal:
                signals.append({"signal": "bullish", "weight": 0.4})
            else:
                signals.append({"signal": "bearish", "weight": 0.4})
            
            # Combine momentum signals
            bullish_score = sum(s["weight"] for s in signals if s["signal"] == "bullish")
            bearish_score = sum(s["weight"] for s in signals if s["signal"] == "bearish")
            neutral_score = sum(s["weight"] for s in signals if s["signal"] == "neutral")
            
            if bullish_score > bearish_score:
                signal = "bullish"
                strength = bullish_score
            elif bearish_score > bullish_score:
                signal = "bearish"
                strength = bearish_score
            else:
                signal = "neutral"
                strength = neutral_score
            
            return {
                "signal": signal,
                "strength": float(strength),
                "confidence": min(strength, 1.0)
            }
            
        except Exception as e:
            self.logger.error(f"Momentum signal generationda xato: {e}")
            return {"signal": "neutral", "strength": 0.0, "confidence": 0.0}
    
    async def _volume_signal(self, data: pd.DataFrame) -> Dict:
        """Volume signal generation"""
        try:
            volume_ratio = data['volume_ratio'].iloc[-1]
            volume_trend = self._analyze_volume_trend(data)
            
            if volume_ratio > 1.5 and volume_trend == "increasing":
                signal = "bullish"
                strength = min(volume_ratio / 2.0, 1.0)
            elif volume_ratio < 0.5 and volume_trend == "decreasing":
                signal = "bearish"
                strength = min((1.0 - volume_ratio), 1.0)
            else:
                signal = "neutral"
                strength = 0.2
            
            return {
                "signal": signal,
                "strength": float(strength),
                "confidence": min(strength * 0.8, 1.0)
            }
            
        except Exception as e:
            self.logger.error(f"Volume signal generationda xato: {e}")
            return {"signal": "neutral", "strength": 0.0, "confidence": 0.0}
    
    async def _volatility_signal(self, data: pd.DataFrame) -> Dict:
        """Volatility signal generation"""
        try:
            current_vol = data['volatility'].iloc[-1]
            avg_vol = data['volatility'].rolling(50).mean().iloc[-1]
            
            vol_ratio = current_vol / avg_vol if avg_vol > 0 else 1.0
            
            if vol_ratio > 1.5:
                signal = "high_volatility"
                strength = min(vol_ratio / 2.0, 1.0)
            elif vol_ratio < 0.7:
                signal = "low_volatility"
                strength = min((1.0 - vol_ratio), 1.0)
            else:
                signal = "normal_volatility"
                strength = 0.3
            
            return {
                "signal": signal,
                "strength": float(strength),
                "confidence": min(strength * 0.6, 1.0)
            }
            
        except Exception as e:
            self.logger.error(f"Volatility signal generationda xato: {e}")
            return {"signal": "normal_volatility", "strength": 0.0, "confidence": 0.0}
    
    def _combine_signals(self, signals: Dict) -> str:
        """Signallarni birlashtirish"""
        try:
            signal_scores = {"bullish": 0, "bearish": 0, "neutral": 0}
            
            for signal_type, signal_data in signals.items():
                signal = signal_data["signal"]
                strength = signal_data["strength"]
                weight = signal_data.get("confidence", 0.5)
                
                if signal in signal_scores:
                    signal_scores[signal] += strength * weight
            
            # Determine dominant signal
            dominant_signal = max(signal_scores.keys(), key=lambda k: signal_scores[k])
            return dominant_signal
            
        except Exception as e:
            self.logger.error(f"Signal combiningda xato: {e}")
            return "neutral"
    
    def _calculate_signal_strength(self, signals: Dict) -> float:
        """Signal strength hisoblash"""
        try:
            strengths = [signal_data["strength"] * signal_data.get("confidence", 0.5) 
                        for signal_data in signals.values()]
            return sum(strengths) / len(strengths) if strengths else 0.0
            
        except Exception as e:
            self.logger.error(f"Signal strength calculationda xato: {e}")
            return 0.0
    
    async def get_portfolio_metrics(self) -> PortfolioMetrics:
        """Portfolio metrikalarini olish"""
        try:
            # Simulate portfolio data
            portfolio_value = 100000 + np.random.normal(0, 10000)  # $100k with some variation
            
            # Calculate returns
            daily_return = np.random.normal(0.001, 0.02)  # 0.1% daily return with 2% std
            daily_pnl = portfolio_value * daily_return
            monthly_pnl = daily_pnl * 20  # ~20 trading days per month
            
            # Calculate risk metrics
            volatility = abs(np.random.normal(0.15, 0.05))  # 15% annual volatility
            sharpe_ratio = daily_return / volatility * np.sqrt(252)  # Annualized Sharpe
            max_drawdown = abs(np.random.normal(0.10, 0.05))  # 10% max drawdown
            
            # Calculate performance metrics
            total_trades = np.random.randint(50, 200)
            winning_trades = int(total_trades * np.random.uniform(0.45, 0.65))
            win_rate = winning_trades / total_trades
            
            # Calculate profit factor
            avg_win = np.random.uniform(0.02, 0.05)
            avg_loss = np.random.uniform(0.01, 0.03)
            profit_factor = (winning_trades * avg_win) / ((total_trades - winning_trades) * avg_loss)
            
            metrics = PortfolioMetrics(
                total_value=float(portfolio_value),
                daily_pnl=float(daily_pnl),
                monthly_pnl=float(monthly_pnl),
                daily_return=float(daily_return),
                volatility=float(volatility),
                sharpe_ratio=float(sharpe_ratio),
                max_drawdown=float(max_drawdown),
                win_rate=float(win_rate),
                profit_factor=float(profit_factor)
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Portfolio metrics calculationda xato: {e}")
            return PortfolioMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    async def get_current_portfolio(self) -> Dict:
        """Current portfolio olish"""
        try:
            # Simulate current portfolio
            positions = {
                "AAPL": {"quantity": 100, "price": 150, "value": 15000},
                "GOOGL": {"quantity": 50, "price": 2800, "value": 140000},
                "MSFT": {"quantity": 200, "price": 300, "value": 60000},
                "TSLA": {"quantity": 80, "price": 250, "value": 20000}
            }
            
            total_value = sum(pos["value"] for pos in positions.values())
            cash = 65000  # Cash position
            
            portfolio = {
                "total_value": total_value + cash,
                "positions": positions,
                "cash": cash,
                "allocation": {symbol: pos["value"] / (total_value + cash) for symbol, pos in positions.items()},
                "last_updated": datetime.now().isoformat()
            }
            
            return portfolio
            
        except Exception as e:
            self.logger.error(f"Current portfolio olishda xato: {e}")
            return {}
    
    async def generate_market_report(self, symbols: List[str] = None) -> Dict:
        """Market report generation"""
        try:
            if symbols is None:
                symbols = list(self.market_data.keys())[:10]  # First 10 symbols
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "symbols_analyzed": len(symbols),
                "market_overview": await self._analyze_market_overview(symbols),
                "sector_analysis": await self._analyze_sectors(symbols),
                "volatility_analysis": await self._analyze_volatility(symbols),
                "momentum_analysis": await self._analyze_momentum(symbols),
                "recommendations": await self._generate_recommendations(symbols)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Market report generationda xato: {e}")
            return {"error": str(e)}
    
    async def _analyze_market_overview(self, symbols: List[str]) -> Dict:
        """Market overview tahlili"""
        try:
            market_data = []
            
            for symbol in symbols:
                if symbol in self.market_data:
                    data = self.market_data[symbol]
                    current_price = data['close'].iloc[-1]
                    price_change = (current_price - data['close'].iloc[-24]) / data['close'].iloc[-24]  # 24h change
                    
                    market_data.append({
                        "symbol": symbol,
                        "price": current_price,
                        "change_24h": price_change,
                        "volume": data['volume'].iloc[-1]
                    })
            
            # Calculate market metrics
            avg_change = np.mean([item["change_24h"] for item in market_data])
            positive_movers = len([item for item in market_data if item["change_24h"] > 0])
            negative_movers = len([item for item in market_data if item["change_24h"] < 0])
            
            return {
                "symbols_analyzed": len(market_data),
                "average_change": avg_change,
                "positive_movers": positive_movers,
                "negative_movers": negative_movers,
                "market_sentiment": "bullish" if avg_change > 0.01 else "bearish" if avg_change < -0.01 else "neutral",
                "top_performers": sorted(market_data, key=lambda x: x["change_24h"], reverse=True)[:3],
                "worst_performers": sorted(market_data, key=lambda x: x["change_24h"])[:3]
            }
            
        except Exception as e:
            self.logger.error(f"Market overview analysisda xato: {e}")
            return {}
    
    async def _analyze_sectors(self, symbols: List[str]) -> Dict:
        """Sector analysis"""
        try:
            # Define sector mapping (simplified)
            sector_mapping = {
                "AAPL": "Technology", "GOOGL": "Technology", "MSFT": "Technology", "NVDA": "Technology",
                "TSLA": "Consumer Discretionary", "AMZN": "Consumer Discretionary", "META": "Communication Services",
                "NFLX": "Communication Services"
            }
            
            sector_data = {}
            
            for symbol in symbols:
                sector = sector_mapping.get(symbol, "Other")
                if sector not in sector_data:
                    sector_data[sector] = []
                
                if symbol in self.market_data:
                    data = self.market_data[symbol]
                    price_change = (data['close'].iloc[-1] - data['close'].iloc[-24]) / data['close'].iloc[-24]
                    sector_data[sector].append(price_change)
            
            # Calculate sector metrics
            sector_analysis = {}
            for sector, changes in sector_data.items():
                sector_analysis[sector] = {
                    "average_change": np.mean(changes),
                    "volatility": np.std(changes),
                    "symbols_count": len(changes)
                }
            
            return sector_analysis
            
        except Exception as e:
            self.logger.error(f"Sector analysisda xato: {e}")
            return {}
    
    async def _analyze_volatility(self, symbols: List[str]) -> Dict:
        """Volatility analysis"""
        try:
            volatility_data = {}
            
            for symbol in symbols:
                if symbol in self.market_data:
                    data = self.market_data[symbol]
                    volatility = data['volatility'].iloc[-1]
                    volatility_data[symbol] = volatility
            
            if volatility_data:
                avg_volatility = np.mean(list(volatility_data.values()))
                high_vol_symbols = [s for s, v in volatility_data.items() if v > avg_volatility * 1.5]
                low_vol_symbols = [s for s, v in volatility_data.items() if v < avg_volatility * 0.5]
                
                return {
                    "average_volatility": avg_volatility,
                    "high_volatility_symbols": high_vol_symbols,
                    "low_volatility_symbols": low_vol_symbols,
                    "volatility_distribution": volatility_data
                }
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"Volatility analysisda xato: {e}")
            return {}
    
    async def _analyze_momentum(self, symbols: List[str]) -> Dict:
        """Momentum analysis"""
        try:
            momentum_data = {}
            
            for symbol in symbols:
                if symbol in self.market_data:
                    data = self.market_data[symbol]
                    # Calculate momentum indicators
                    rsi = data['rsi'].iloc[-1]
                    macd = data['macd'].iloc[-1]
                    price_momentum = data['price_momentum'].iloc[-1]
                    
                    momentum_data[symbol] = {
                        "rsi": rsi,
                        "macd": macd,
                        "price_momentum": price_momentum
                    }
            
            return momentum_data
            
        except Exception as e:
            self.logger.error(f"Momentum analysisda xato: {e}")
            return {}
    
    async def _generate_recommendations(self, symbols: List[str]) -> Dict:
        """Recommendations generation"""
        try:
            recommendations = {
                "buy": [],
                "sell": [],
                "hold": []
            }
            
            for symbol in symbols:
                if symbol in self.market_data:
                    data = self.market_data[symbol]
                    
                    # Simple recommendation logic
                    current_price = data['close'].iloc[-1]
                    sma_20 = data['sma_20'].iloc[-1]
                    rsi = data['rsi'].iloc[-1]
                    
                    if current_price > sma_20 and 30 < rsi < 70:
                        recommendations["buy"].append({"symbol": symbol, "reason": "Above SMA20 and RSI in neutral zone"})
                    elif current_price < sma_20 or rsi > 80 or rsi < 20:
                        recommendations["sell"].append({"symbol": symbol, "reason": "Below SMA20 or RSI extreme"})
                    else:
                        recommendations["hold"].append({"symbol": symbol, "reason": "Neutral technical position"})
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendations generationda xato: {e}")
            return {"buy": [], "sell": [], "hold": []}
    
    async def _monitor_market_conditions(self):
        """Market conditions monitoring"""
        while self.is_initialized:
            try:
                # Monitor for unusual market conditions
                for symbol, data in self.market_data.items():
                    if len(data) > 0:
                        # Check for unusual price movements
                        recent_returns = data['close'].pct_change().tail(10)
                        current_volatility = recent_returns.std()
                        
                        if current_volatility > 0.05:  # 5% volatility threshold
                            self.active_alerts.append({
                                "type": "high_volatility",
                                "symbol": symbol,
                                "message": f"High volatility detected: {current_volatility:.2%}",
                                "timestamp": datetime.now(),
                                "severity": "warning"
                            })
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Market conditions monitoringda xato: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_portfolio_health(self):
        """Portfolio health monitoring"""
        while self.is_initialized:
            try:
                # Monitor portfolio health metrics
                portfolio_metrics = await self.get_portfolio_metrics()
                
                # Check for concerning metrics
                if portfolio_metrics.max_drawdown > 0.20:  # 20% drawdown
                    self.active_alerts.append({
                        "type": "high_drawdown",
                        "message": f"High drawdown detected: {portfolio_metrics.max_drawdown:.2%}",
                        "timestamp": datetime.now(),
                        "severity": "critical"
                    })
                
                if portfolio_metrics.sharpe_ratio < 0.5:  # Low Sharpe ratio
                    self.active_alerts.append({
                        "type": "low_sharpe",
                        "message": f"Low Sharpe ratio: {portfolio_metrics.sharpe_ratio:.2f}",
                        "timestamp": datetime.now(),
                        "severity": "warning"
                    })
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Portfolio health monitoringda xato: {e}")
                await asyncio.sleep(300)
    
    async def _generate_alerts(self):
        """Alert generation"""
        while self.is_initialized:
            try:
                # Clean old alerts
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.active_alerts = [alert for alert in self.active_alerts 
                                    if alert["timestamp"] > cutoff_time]
                
                # Log active alerts
                if self.active_alerts:
                    self.logger.info(f"Active alerts: {len(self.active_alerts)}")
                
                await asyncio.sleep(300)  # Generate alerts every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Alert generationda xato: {e}")
                await asyncio.sleep(300)
    
    async def close(self):
        """Analytics Engine'ni yopish"""
        try:
            self.logger.info("Analytics Engine yopilmoqda...")
            
            # Clear data
            self.market_data.clear()
            self.portfolio_history.clear()
            self.performance_metrics.clear()
            self.risk_metrics.clear()
            self.active_alerts.clear()
            self.dashboards.clear()
            self.analysis_cache.clear()
            
            self.is_initialized = False
            self.logger.info("✅ Analytics Engine muvaffaqiyatli yopildi")
            
        except Exception as e:
            self.logger.error(f"Analytics Engine'ni yopishda xato: {e}")
    
    async def get_analytics_statistics(self) -> Dict:
        """Analytics statistikalarini olish"""
        return {
            "initialized": self.is_initialized,
            "symbols_tracked": len(self.market_data),
            "active_alerts": len(self.active_alerts),
            "dashboards_configured": len(self.dashboards),
            "cache_entries": len(self.analysis_cache),
            "last_market_data": {symbol: data['timestamp'].max().isoformat() 
                               for symbol, data in self.market_data.items()}
        }