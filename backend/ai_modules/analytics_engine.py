"""
Real-time Analytics Engine
==========================

Ushbu modul real-time market data, user activity, va system performance
monitoring uchun analitika tizimini ta'minlaydi.

Asosiy funksiyalar:
- Real-time market data processing
- User activity monitoring
- Signal performance tracking
- Risk metrics calculation
- System performance monitoring
- Business intelligence
- Predictive analytics
- Anomaly detection
"""

import asyncio
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import deque
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Logging setup
logger = logging.getLogger(__name__)


@dataclass
class MarketMetrics:
    """Market metrikalarining struktura"""
    symbol: str
    price: float
    volume: float
    volatility: float
    sma_20: float
    sma_50: float
    rsi: float
    macd: float
    timestamp: datetime


@dataclass
class UserMetrics:
    """User metrikalarining struktura"""
    user_id: str
    active_sessions: int
    trades_count: int
    profit_loss: float
    risk_score: float
    engagement_score: float
    last_activity: datetime


@dataclass
class SystemMetrics:
    """System metrikalarining struktura"""
    cpu_usage: float
    memory_usage: float
    api_response_time: float
    error_rate: float
    uptime: float
    throughput: float
    timestamp: datetime


@dataclass
class SignalMetrics:
    """Signal performance metrikalar"""
    signal_id: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    win_rate: float
    avg_return: float
    sharpe_ratio: float
    max_drawdown: float
    timestamp: datetime


class AnalyticsEngine:
    """Real-time Analytics Engine - Asosiy analitika dvijogi"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        
        # Data storage
        self.market_data = deque(maxlen=1000)
        self.user_data = {}
        self.system_data = deque(maxlen=500)
        self.signal_data = {}
        
        # Performance tracking
        self.performance_cache = {}
        self.anomaly_detectors = {}
        
        # ML models (agar mavjud bo'lsa)
        if ML_AVAILABLE:
            self.scaler = StandardScaler()
            self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        
        # Alert system
        self.alert_thresholds = {
            'volatility': 0.5,
            'error_rate': 0.05,
            'response_time': 1000,
            'drawdown': 0.2
        }
        
        self.alerts = deque(maxlen=100)
        self.is_running = False
        
    def _default_config(self) -> Dict:
        """Default konfiguratsiya"""
        return {
            'market_analysis': {
                'price_lookback': 50,
                'volume_threshold': 1.5,
                'volatility_threshold': 0.02
            },
            'user_analysis': {
                'session_timeout': 30,
                'min_trades': 5,
                'risk_weight': 0.3
            },
            'system_monitoring': {
                'cpu_alert': 80,
                'memory_alert': 85,
                'response_alert': 1000
            },
            'ml_models': {
                'anomaly_detection': True,
                'predictive_analytics': True,
                'pattern_recognition': True
            }
        }
    
    async def start_analytics(self):
        """Analytics tizimini ishga tushirish"""
        logger.info("Real-time Analytics Engine ishga tushirilmoqda...")
        
        self.is_running = True
        
        # Concurrent analytics tasks
        await asyncio.gather(
            self._market_analytics_loop(),
            self._user_analytics_loop(),
            self._system_monitoring_loop(),
            self._signal_performance_loop(),
            self._anomaly_detection_loop(),
            self._predictive_analytics_loop()
        )
    
    async def stop_analytics(self):
        """Analytics tizimini to'xtatish"""
        self.is_running = False
        logger.info("Real-time Analytics Engine to'xtatildi")
    
    # Market Analytics
    async def _market_analytics_loop(self):
        """Market data analitikasi cikli"""
        while self.is_running:
            try:
                if len(self.market_data) > 0:
                    await self._analyze_market_trends()
                    await self._calculate_market_indicators()
                    await self._detect_market_patterns()
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Market analytics xatosi: {e}")
                await asyncio.sleep(5)
    
    def add_market_data(self, data: Dict):
        """Market data qo'shish"""
        metrics = MarketMetrics(
            symbol=data['symbol'],
            price=data['price'],
            volume=data['volume'],
            volatility=data.get('volatility', 0.0),
            sma_20=data.get('sma_20', 0.0),
            sma_50=data.get('sma_50', 0.0),
            rsi=data.get('rsi', 0.0),
            macd=data.get('macd', 0.0),
            timestamp=datetime.now()
        )
        self.market_data.append(metrics)
    
    async def _analyze_market_trends(self):
        """Market trendlari tahlili"""
        if len(self.market_data) < 20:
            return
        
        prices = [m.price for m in list(self.market_data)[-20:]]
        volumes = [m.volume for m in list(self.market_data)[-20:]]
        
        # Trend tahlili
        trend_score = self._calculate_trend_score(prices)
        
        # Volume analysis
        volume_spike = self._detect_volume_spike(volumes)
        
        # Volatility analysis
        volatility = np.std(prices) / np.mean(prices)
        
        # Market sentiment
        sentiment = self._calculate_market_sentiment(prices, volumes)
        
        logger.debug(f"Market trend: {trend_score:.3f}, Volatility: {volatility:.3f}, Sentiment: {sentiment:.3f}")
    
    def _calculate_trend_score(self, prices: List[float]) -> float:
        """Trend balandligini hisoblash"""
        if len(prices) < 2:
            return 0.0
        
        # Linear trend regression
        x = np.arange(len(prices))
        slope = np.polyfit(x, prices, 1)[0]
        
        # Normalize slope
        return slope / np.mean(prices)
    
    def _detect_volume_spike(self, volumes: List[float]) -> bool:
        """Volume spike aniqlash"""
        if len(volumes) < 10:
            return False
        
        avg_volume = np.mean(volumes[:-5])
        recent_volume = np.mean(volumes[-5:])
        
        return recent_volume > avg_volume * self.config['market_analysis']['volume_threshold']
    
    def _calculate_market_sentiment(self, prices: List[float], volumes: List[float]) -> float:
        """Market sentiment hisoblash"""
        if len(prices) < 10:
            return 0.0
        
        # Price momentum
        momentum = (prices[-1] - prices[-5]) / prices[-5]
        
        # Volume-weighted momentum
        vol_weighted_momentum = np.sum([p * v for p, v in zip(prices[-5:], volumes[-5:])]) / np.sum(volumes[-5:])
        
        return momentum * 0.7 + vol_weighted_momentum * 0.3
    
    async def _calculate_market_indicators(self):
        """Technical indicatorlarni hisoblash"""
        if len(self.market_data) < 50:
            return
        
        recent_data = list(self.market_data)[-50:]
        prices = [m.price for m in recent_data]
        volumes = [m.volume for m in recent_data]
        
        # SMA calculation
        sma_20 = np.mean(prices[-20:])
        sma_50 = np.mean(prices[-50:])
        
        # RSI calculation
        rsi = self._calculate_rsi(prices, 14)
        
        # MACD calculation
        macd, signal, histogram = self._calculate_macd(prices)
        
        # Bollinger Bands
        bb_upper, bb_lower = self._calculate_bollinger_bands(prices, 20, 2)
        
        # Volume indicators
        volume_sma = np.mean(volumes[-20:])
        volume_ratio = volumes[-1] / volume_sma if volume_sma > 0 else 0
        
        logger.debug(f"Indicators - SMA20: {sma_20:.2f}, RSI: {rsi:.2f}, MACD: {macd:.3f}")
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """RSI hisoblash"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, prices: List[float]) -> Tuple[float, float, float]:
        """MACD hisoblash"""
        if len(prices) < 26:
            return 0.0, 0.0, 0.0
        
        # EMA 12
        ema_12 = self._calculate_ema(prices, 12)
        # EMA 26
        ema_26 = self._calculate_ema(prices, 26)
        
        macd = ema_12 - ema_26
        
        # Signal line (EMA 9 of MACD)
        if hasattr(self, '_macd_history'):
            self._macd_history.append(macd)
            if len(self._macd_history) >= 9:
                signal = self._calculate_ema(self._macd_history, 9)
                histogram = macd - signal
                return macd, signal, histogram
        
        if not hasattr(self, '_macd_history'):
            self._macd_history = []
        
        return macd, 0.0, 0.0
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """EMA hisoblash"""
        if len(prices) < period:
            return np.mean(prices)
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int, std_dev: float) -> Tuple[float, float]:
        """Bollinger Bands hisoblash"""
        if len(prices) < period:
            return prices[-1], prices[-1]
        
        sma = np.mean(prices[-period:])
        std = np.std(prices[-period:])
        
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        
        return upper, lower
    
    async def _detect_market_patterns(self):
        """Market patternlarni aniqlash"""
        if len(self.market_data) < 30:
            return
        
        prices = [m.price for m in list(self.market_data)[-30:]]
        
        # Support/Resistance levels
        support_level = min(prices[-10:])
        resistance_level = max(prices[-10:])
        
        # Double top/bottom detection
        pattern = self._identify_chart_patterns(prices)
        
        # Trend pattern analysis
        trend_pattern = self._analyze_trend_pattern(prices)
        
        logger.debug(f"Pattern detected: {pattern}, Trend: {trend_pattern}")
    
    def _identify_chart_patterns(self, prices: List[float]) -> str:
        """Chart patternlarni aniqlash"""
        if len(prices) < 10:
            return "no_pattern"
        
        # Simple peak/valley detection
        peaks = []
        valleys = []
        
        for i in range(2, len(prices) - 2):
            if prices[i] > prices[i-1] and prices[i] > prices[i+1] and \
               prices[i] > prices[i-2] and prices[i] > prices[i+2]:
                peaks.append(i)
            elif prices[i] < prices[i-1] and prices[i] < prices[i+1] and \
                 prices[i] < prices[i-2] and prices[i] < prices[i+2]:
                valleys.append(i)
        
        # Pattern classification
        if len(peaks) >= 2:
            if abs(prices[peaks[-1]] - prices[peaks[-2]]) / prices[peaks[-2]] < 0.02:
                return "double_top"
        
        if len(valleys) >= 2:
            if abs(prices[valleys[-1]] - prices[valleys[-2]]) / prices[valleys[-2]] < 0.02:
                return "double_bottom"
        
        return "no_pattern"
    
    def _analyze_trend_pattern(self, prices: List[float]) -> str:
        """Trend pattern tahlili"""
        if len(prices) < 20:
            return "insufficient_data"
        
        # Multiple timeframe analysis
        short_trend = self._calculate_trend_score(prices[-10:])
        medium_trend = self._calculate_trend_score(prices[-20:])
        long_trend = self._calculate_trend_score(prices[-30:]) if len(prices) >= 30 else medium_trend
        
        # Trend strength assessment
        if all(t > 0.01 for t in [short_trend, medium_trend, long_trend]):
            return "strong_uptrend"
        elif all(t < -0.01 for t in [short_trend, medium_trend, long_trend]):
            return "strong_downtrend"
        elif short_trend > 0.005:
            return "weak_uptrend"
        elif short_trend < -0.005:
            return "weak_downtrend"
        else:
            return "sideways"
    
    # User Analytics
    async def _user_analytics_loop(self):
        """User activity analytics cikli"""
        while self.is_running:
            try:
                await self._analyze_user_behavior()
                await self._calculate_engagement_metrics()
                await self._track_user_retention()
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"User analytics xatosi: {e}")
                await asyncio.sleep(10)
    
    def add_user_data(self, user_id: str, data: Dict):
        """User data qo'shish"""
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'activities': deque(maxlen=100),
                'trades': [],
                'sessions': [],
                'last_activity': None,
                'total_trades': 0,
                'total_profit_loss': 0.0,
                'risk_score': 0.0
            }
        
        self.user_data[user_id]['activities'].append({
            'timestamp': datetime.now(),
            'action': data.get('action', 'unknown'),
            'metadata': data.get('metadata', {})
        })
        
        self.user_data[user_id]['last_activity'] = datetime.now()
        
        if data.get('action') == 'trade':
            self.user_data[user_id]['trades'].append(data)
            self.user_data[user_id]['total_trades'] += 1
            self.user_data[user_id]['total_profit_loss'] += data.get('profit_loss', 0.0)
    
    async def _analyze_user_behavior(self):
        """User behavior tahlili"""
        for user_id, user_data in self.user_data.items():
            if len(user_data['activities']) < 5:
                continue
            
            # Activity frequency
            recent_activities = [a for a in user_data['activities'] 
                               if a['timestamp'] > datetime.now() - timedelta(hours=24)]
            
            activity_frequency = len(recent_activities)
            
            # Trading patterns
            trading_patterns = self._analyze_trading_patterns(user_data['trades'])
            
            # Risk behavior
            risk_behavior = self._assess_risk_behavior(user_data)
            
            # Session analysis
            session_analysis = self._analyze_user_sessions(user_data)
            
            logger.debug(f"User {user_id}: Activity={activity_frequency}, Risk={risk_behavior:.2f}")
    
    def _analyze_trading_patterns(self, trades: List[Dict]) -> Dict:
        """Trading patternlarni tahlili"""
        if len(trades) < 2:
            return {'pattern': 'insufficient_data'}
        
        # Win rate
        winning_trades = len([t for t in trades if t.get('profit_loss', 0) > 0])
        win_rate = winning_trades / len(trades)
        
        # Average trade size
        trade_sizes = [t.get('size', 0) for t in trades]
        avg_trade_size = np.mean(trade_sizes)
        
        # Trading frequency
        if len(trades) >= 2:
            time_diffs = []
            for i in range(1, len(trades)):
                time1 = trades[i-1].get('timestamp')
                time2 = trades[i].get('timestamp')
                if time1 and time2:
                    diff = (time2 - time1).total_seconds() / 3600  # hours
                    time_diffs.append(diff)
            
            avg_frequency = np.mean(time_diffs) if time_diffs else 0
        else:
            avg_frequency = 0
        
        return {
            'win_rate': win_rate,
            'avg_trade_size': avg_trade_size,
            'avg_frequency_hours': avg_frequency
        }
    
    def _assess_risk_behavior(self, user_data: Dict) -> float:
        """Risk behavior baholash"""
        trades = user_data['trades']
        if len(trades) < 3:
            return 0.5
        
        # Risk factors
        risk_factors = []
        
        # Trade size variance
        trade_sizes = [t.get('size', 0) for t in trades]
        if np.mean(trade_sizes) > 0:
            size_variance = np.std(trade_sizes) / np.mean(trade_sizes)
            risk_factors.append(min(size_variance, 1.0))
        
        # Consecutive losses
        consecutive_losses = 0
        max_consecutive_losses = 0
        for trade in reversed(trades):
            if trade.get('profit_loss', 0) < 0:
                consecutive_losses += 1
                max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
            else:
                consecutive_losses = 0
        
        # Risk score (0-1, where 1 is highest risk)
        risk_score = min(max_consecutive_losses / 5, 1.0)
        if risk_factors:
            risk_score = (risk_score + np.mean(risk_factors)) / 2
        
        return risk_score
    
    def _analyze_user_sessions(self, user_data: Dict) -> Dict:
        """User session tahlili"""
        activities = user_data['activities']
        if len(activities) < 2:
            return {'session_count': 0, 'avg_duration': 0}
        
        # Session boundaries (30 minutes inactivity)
        sessions = []
        current_session = []
        
        for i, activity in enumerate(activities):
            if i == 0 or (activity['timestamp'] - activities[i-1]['timestamp']).total_seconds() > 1800:
                if current_session:
                    sessions.append(current_session)
                current_session = [activity]
            else:
                current_session.append(activity)
        
        if current_session:
            sessions.append(current_session)
        
        # Session metrics
        session_count = len(sessions)
        session_durations = []
        
        for session in sessions:
            if len(session) > 1:
                duration = (session[-1]['timestamp'] - session[0]['timestamp']).total_seconds() / 60  # minutes
                session_durations.append(duration)
        
        avg_duration = np.mean(session_durations) if session_durations else 0
        
        return {
            'session_count': session_count,
            'avg_duration_minutes': avg_duration,
            'total_sessions': session_count
        }
    
    async def _calculate_engagement_metrics(self):
        """Engagement metrikalarini hisoblash"""
        total_users = len(self.user_data)
        if total_users == 0:
            return
        
        # Active users (last 24 hours)
        active_users = 0
        high_engagement_users = 0
        
        for user_data in self.user_data.values():
            if user_data.get('last_activity'):
                if datetime.now() - user_data['last_activity'] < timedelta(hours=24):
                    active_users += 1
                    
                    # Engagement score
                    engagement = self._calculate_engagement_score(user_data)
                    if engagement > 0.7:
                        high_engagement_users += 1
        
        engagement_rate = active_users / total_users
        high_engagement_rate = high_engagement_users / total_users
        
        logger.debug(f"Engagement: {engagement_rate:.2%}, High engagement: {high_engagement_rate:.2%}")
    
    def _calculate_engagement_score(self, user_data: Dict) -> float:
        """Engagement score hisoblash"""
        activities = user_data.get('activities', [])
        if len(activities) < 1:
            return 0.0
        
        # Activity frequency (last 7 days)
        recent_activities = [a for a in activities 
                           if a['timestamp'] > datetime.now() - timedelta(days=7)]
        frequency_score = min(len(recent_activities) / 20, 1.0)  # Normalize to max 20 activities
        
        # Session duration
        session_analysis = self._analyze_user_sessions(user_data)
        duration_score = min(session_analysis.get('avg_duration_minutes', 0) / 60, 1.0)  # Max 1 hour
        
        # Trading activity
        trades = user_data.get('trades', [])
        trading_score = min(len(trades) / 10, 1.0)  # Max 10 trades
        
        # Engagement score
        engagement_score = (frequency_score * 0.3 + duration_score * 0.4 + trading_score * 0.3)
        
        return engagement_score
    
    async def _track_user_retention(self):
        """User retention tracking"""
        # This would typically integrate with your user database
        # For now, we'll simulate retention metrics
        
        logger.debug("User retention tracking executed")
    
    # System Monitoring
    async def _system_monitoring_loop(self):
        """System monitoring cikli"""
        while self.is_running:
            try:
                await self._collect_system_metrics()
                await self._monitor_api_performance()
                await self._check_system_health()
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"System monitoring xatosi: {e}")
                await asyncio.sleep(5)
    
    async def _collect_system_metrics(self):
        """System metrikalarini yig'ish"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            net_io = psutil.net_io_counters()
            
            metrics = SystemMetrics(
                cpu_usage=cpu_percent,
                memory_usage=memory.percent,
                api_response_time=0.0,  # Will be updated by API monitoring
                error_rate=0.0,  # Will be updated by error tracking
                uptime=0.0,  # Will be updated by uptime tracker
                throughput=net_io.bytes_sent + net_io.bytes_recv,
                timestamp=datetime.now()
            )
            
            self.system_data.append(metrics)
            
        except ImportError:
            # Fallback if psutil not available
            logger.warning("psutil topilmadi, tizim metrikalari cheklangan")
    
    async def _monitor_api_performance(self):
        """API performance monitoring"""
        # This would integrate with your API gateway
        # For now, simulate API metrics
        
        avg_response_time = np.mean([m.api_response_time for m in list(self.system_data)[-10:]]) if len(self.system_data) > 0 else 0
        
        if avg_response_time > self.config['system_monitoring']['response_alert']:
            self._create_alert('high_response_time', f"Average response time: {avg_response_time:.0f}ms")
    
    async def _check_system_health(self):
        """Tizim sog'liq tekshiruvi"""
        if len(self.system_data) < 5:
            return
        
        recent_metrics = list(self.system_data)[-5:]
        
        # Check thresholds
        avg_cpu = np.mean([m.cpu_usage for m in recent_metrics])
        avg_memory = np.mean([m.memory_usage for m in recent_metrics])
        
        if avg_cpu > self.config['system_monitoring']['cpu_alert']:
            self._create_alert('high_cpu', f"CPU usage: {avg_cpu:.1f}%")
        
        if avg_memory > self.config['system_monitoring']['memory_alert']:
            self._create_alert('high_memory', f"Memory usage: {avg_memory:.1f}%")
    
    def _create_alert(self, alert_type: str, message: str):
        """Alert yaratish"""
        alert = {
            'type': alert_type,
            'message': message,
            'timestamp': datetime.now(),
            'severity': self._get_alert_severity(alert_type)
        }
        
        self.alerts.append(alert)
        logger.warning(f"ALERT [{alert['severity']}]: {message}")
    
    def _get_alert_severity(self, alert_type: str) -> str:
        """Alert severity aniqlash"""
        high_severity = ['high_cpu', 'high_memory', 'system_down']
        medium_severity = ['high_response_time', 'disk_space', 'api_errors']
        
        if alert_type in high_severity:
            return 'HIGH'
        elif alert_type in medium_severity:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    # Signal Performance
    async def _signal_performance_loop(self):
        """Signal performance tracking cikli"""
        while self.is_running:
            try:
                await self._analyze_signal_performance()
                await self._calculate_signal_metrics()
                await self._track_signal_accuracy()
                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"Signal performance xatosi: {e}")
                await asyncio.sleep(15)
    
    def add_signal_data(self, signal_id: str, data: Dict):
        """Signal data qo'shish"""
        if signal_id not in self.signal_data:
            self.signal_data[signal_id] = {
                'signals': [],
                'outcomes': [],
                'performance_history': []
            }
        
        self.signal_data[signal_id]['signals'].append({
            'timestamp': datetime.now(),
            'signal': data,
            'status': 'pending'
        })
    
    def update_signal_outcome(self, signal_id: str, outcome: Dict):
        """Signal natijasini yangilash"""
        if signal_id in self.signal_data:
            self.signal_data[signal_id]['outcomes'].append({
                'timestamp': datetime.now(),
                'outcome': outcome
            })
    
    async def _analyze_signal_performance(self):
        """Signal performance tahlili"""
        for signal_id, data in self.signal_data.items():
            if len(data['outcomes']) < 5:
                continue
            
            # Calculate performance metrics
            outcomes = data['outcomes']
            returns = [o['outcome'].get('return', 0) for o in outcomes]
            accuracies = [o['outcome'].get('accuracy', 0) for o in outcomes]
            
            if not returns:
                continue
            
            # Performance metrics
            avg_return = np.mean(returns)
            win_rate = len([r for r in returns if r > 0]) / len(returns)
            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
            max_drawdown = self._calculate_max_drawdown(returns)
            
            metrics = SignalMetrics(
                signal_id=signal_id,
                accuracy=np.mean(accuracies),
                precision=np.mean(accuracies),  # Simplified
                recall=np.mean(accuracies),     # Simplified
                f1_score=np.mean(accuracies),   # Simplified
                win_rate=win_rate,
                avg_return=avg_return,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                timestamp=datetime.now()
            )
            
            # Store performance history
            data['performance_history'].append(metrics)
            
            # Keep only recent history
            if len(data['performance_history']) > 100:
                data['performance_history'] = data['performance_history'][-100:]
            
            logger.debug(f"Signal {signal_id}: Return={avg_return:.2%}, Win rate={win_rate:.2%}")
    
    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Maximum drawdown hisoblash"""
        if not returns:
            return 0.0
        
        cumulative = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        
        return abs(np.min(drawdown))
    
    async def _calculate_signal_metrics(self):
        """Signal metrikalarini hisoblash"""
        # Aggregate signal performance
        all_returns = []
        all_accuracies = []
        
        for data in self.signal_data.values():
            for outcome in data['outcomes']:
                all_returns.append(outcome['outcome'].get('return', 0))
                all_accuracies.append(outcome['outcome'].get('accuracy', 0))
        
        if not all_returns:
            return
        
        # Overall signal performance
        total_signals = len(all_returns)
        avg_return = np.mean(all_returns)
        avg_accuracy = np.mean(all_accuracies)
        
        self.performance_cache['total_signals'] = total_signals
        self.performance_cache['avg_return'] = avg_return
        self.performance_cache['avg_accuracy'] = avg_accuracy
        
        logger.debug(f"Overall signals: {total_signals}, Avg return: {avg_return:.2%}")
    
    async def _track_signal_accuracy(self):
        """Signal accuracy tracking"""
        # This would integrate with actual trading outcomes
        logger.debug("Signal accuracy tracking executed")
    
    # Anomaly Detection
    async def _anomaly_detection_loop(self):
        """Anomaly detection cikli"""
        while self.is_running:
            try:
                if ML_AVAILABLE and len(self.market_data) > 100:
                    await self._detect_market_anomalies()
                    await self._detect_user_anomalies()
                    await self._detect_system_anomalies()
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Anomaly detection xatosi: {e}")
                await asyncio.sleep(60)
    
    async def _detect_market_anomalies(self):
        """Market anomalylarni aniqlash"""
        if len(self.market_data) < 50:
            return
        
        # Prepare data for anomaly detection
        prices = np.array([m.price for m in list(self.market_data)[-100:]]).reshape(-1, 1)
        volumes = np.array([m.volume for m in list(self.market_data)[-100:]]).reshape(-1, 1)
        
        # Combine features
        features = np.hstack([prices, volumes])
        
        # Train anomaly detector if not trained
        if not hasattr(self.anomaly_detector, 'fitted_') or not self.anomaly_detector.fitted_:
            # Normalize features
            normalized_features = self.scaler.fit_transform(features)
            self.anomaly_detector.fit(normalized_features)
        
        # Detect anomalies
        normalized_features = self.scaler.transform(features)
        anomaly_scores = self.anomaly_detector.decision_function(normalized_features)
        anomalies = self.anomaly_detector.predict(normalized_features)
        
        # Recent anomalies
        recent_anomalies = np.where(anomalies == -1)[0]
        if len(recent_anomalies) > 0:
            latest_price = prices[-1][0]
            latest_volume = volumes[-1][0]
            self._create_alert('market_anomaly', 
                             f"Price: {latest_price}, Volume: {latest_volume:.0f}")
    
    async def _detect_user_anomalies(self):
        """User anomalylarni aniqlash"""
        # User behavior anomalies (unusual trading patterns, etc.)
        for user_id, user_data in self.user_data.items():
            if len(user_data.get('trades', [])) < 10:
                continue
            
            # Check for unusual trading frequency
            recent_trades = [t for t in user_data['trades'] 
                           if t.get('timestamp') and 
                           datetime.now() - t['timestamp'] < timedelta(hours=1)]
            
            if len(recent_trades) > 10:  # More than 10 trades in an hour
                self._create_alert('user_anomaly', 
                                 f"User {user_id}: High frequency trading detected")
    
    async def _detect_system_anomalies(self):
        """System anomalylarni aniqlash"""
        if len(self.system_data) < 20:
            return
        
        # Check for unusual system metrics
        recent_cpu = [m.cpu_usage for m in list(self.system_data)[-20:]]
        recent_memory = [m.memory_usage for m in list(self.system_data)[-20:]]
        
        # CPU spike detection
        cpu_mean = np.mean(recent_cpu)
        cpu_std = np.std(recent_cpu)
        current_cpu = recent_cpu[-1]
        
        if current_cpu > cpu_mean + 3 * cpu_std:  # 3-sigma rule
            self._create_alert('system_anomaly', 
                             f"CPU usage spike: {current_cpu:.1f}%")
    
    # Predictive Analytics
    async def _predictive_analytics_loop(self):
        """Predictive analytics cikli"""
        while self.is_running:
            try:
                if ML_AVAILABLE:
                    await self._predict_market_movements()
                    await self._predict_user_behavior()
                    await self._predict_system_issues()
                await asyncio.sleep(60)  # Less frequent for ML
            except Exception as e:
                logger.error(f"Predictive analytics xatosi: {e}")
                await asyncio.sleep(120)
    
    async def _predict_market_movements(self):
        """Market harakatlarini bashorat qilish"""
        if len(self.market_data) < 50:
            return
        
        # Simple price prediction using trend
        recent_prices = [m.price for m in list(self.market_data)[-20:]]
        
        # Linear trend extrapolation
        if len(recent_prices) > 5:
            x = np.arange(len(recent_prices))
            slope = np.polyfit(x, recent_prices, 1)[0]
            
            # Predict next 5 periods
            future_x = np.arange(len(recent_prices), len(recent_prices) + 5)
            predicted_prices = slope * future_x + recent_prices[-1]
            
            # Confidence interval (simplified)
            std_error = np.std(recent_prices)
            upper_bound = predicted_prices + 1.96 * std_error
            lower_bound = predicted_prices - 1.96 * std_error
            
            logger.debug(f"Market prediction: Next price range {lower_bound[-1]:.2f} - {upper_bound[-1]:.2f}")
    
    async def _predict_user_behavior(self):
        """User behavior bashorati"""
        # User churn prediction, engagement trends, etc.
        logger.debug("User behavior prediction executed")
    
    async def _predict_system_issues(self):
        """System muammolarini bashorat qilish"""
        # System resource predictions, error rate forecasting
        logger.debug("System issue prediction executed")
    
    # Data Export and Reporting
    def get_market_analytics_report(self, time_range: str = '1h') -> Dict:
        """Market analytics hisoboti"""
        end_time = datetime.now()
        
        if time_range == '1h':
            start_time = end_time - timedelta(hours=1)
        elif time_range == '1d':
            start_time = end_time - timedelta(days=1)
        elif time_range == '1w':
            start_time = end_time - timedelta(weeks=1)
        else:
            start_time = end_time - timedelta(hours=1)
        
        # Filter data by time range
        filtered_market_data = [m for m in self.market_data if m.timestamp >= start_time]
        
        if not filtered_market_data:
            return {'error': 'No data available for the specified time range'}
        
        # Generate report
        prices = [m.price for m in filtered_market_data]
        volumes = [m.volume for m in filtered_market_data]
        
        report = {
            'time_range': time_range,
            'data_points': len(filtered_market_data),
            'price_stats': {
                'current': prices[-1],
                'min': min(prices),
                'max': max(prices),
                'avg': np.mean(prices),
                'volatility': np.std(prices) / np.mean(prices)
            },
            'volume_stats': {
                'current': volumes[-1],
                'avg': np.mean(volumes),
                'total': sum(volumes)
            },
            'alerts': len([a for a in self.alerts if a['timestamp'] >= start_time])
        }
        
        return report
    
    def get_user_analytics_report(self) -> Dict:
        """User analytics hisoboti"""
        if not self.user_data:
            return {'error': 'No user data available'}
        
        total_users = len(self.user_data)
        active_users = 0
        total_trades = 0
        total_profit_loss = 0.0
        
        engagement_scores = []
        
        for user_data in self.user_data.values():
            # Active user (last 24 hours)
            if user_data.get('last_activity') and \
               datetime.now() - user_data['last_activity'] < timedelta(hours=24):
                active_users += 1
            
            # Trading metrics
            trades = user_data.get('trades', [])
            total_trades += len(trades)
            total_profit_loss += user_data.get('total_profit_loss', 0.0)
            
            # Engagement
            engagement = self._calculate_engagement_score(user_data)
            engagement_scores.append(engagement)
        
        report = {
            'total_users': total_users,
            'active_users': active_users,
            'active_rate': active_users / total_users if total_users > 0 else 0,
            'total_trades': total_trades,
            'total_profit_loss': total_profit_loss,
            'avg_engagement': np.mean(engagement_scores) if engagement_scores else 0,
            'high_engagement_users': len([s for s in engagement_scores if s > 0.7])
        }
        
        return report
    
    def get_system_analytics_report(self) -> Dict:
        """System analytics hisoboti"""
        if not self.system_data:
            return {'error': 'No system data available'}
        
        recent_data = list(self.system_data)[-10:]  # Last 10 records
        
        if not recent_data:
            return {'error': 'No recent system data available'}
        
        cpu_values = [m.cpu_usage for m in recent_data]
        memory_values = [m.memory_usage for m in recent_data]
        response_times = [m.api_response_time for m in recent_data if m.api_response_time > 0]
        
        report = {
            'cpu_usage': {
                'current': cpu_values[-1],
                'avg': np.mean(cpu_values),
                'max': max(cpu_values)
            },
            'memory_usage': {
                'current': memory_values[-1],
                'avg': np.mean(memory_values),
                'max': max(memory_values)
            },
            'api_performance': {
                'avg_response_time': np.mean(response_times) if response_times else 0,
                'max_response_time': max(response_times) if response_times else 0
            },
            'alerts': {
                'total': len(self.alerts),
                'recent': len([a for a in self.alerts if datetime.now() - a['timestamp'] < timedelta(hours=1)])
            }
        }
        
        return report
    
    def get_signal_performance_report(self) -> Dict:
        """Signal performance hisoboti"""
        if not self.signal_data:
            return {'error': 'No signal data available'}
        
        total_signals = sum(len(data['signals']) for data in self.signal_data.values())
        total_outcomes = sum(len(data['outcomes']) for data in self.signal_data.values())
        
        if total_outcomes == 0:
            return {'error': 'No signal outcomes available'}
        
        # Aggregate performance
        all_returns = []
        all_accuracies = []
        
        for data in self.signal_data.values():
            for outcome in data['outcomes']:
                all_returns.append(outcome['outcome'].get('return', 0))
                all_accuracies.append(outcome['outcome'].get('accuracy', 0))
        
        report = {
            'total_signals': total_signals,
            'total_outcomes': total_outcomes,
            'avg_return': np.mean(all_returns),
            'avg_accuracy': np.mean(all_accuracies),
            'win_rate': len([r for r in all_returns if r > 0]) / len(all_returns),
            'sharpe_ratio': np.mean(all_returns) / np.std(all_returns) if np.std(all_returns) > 0 else 0
        }
        
        return report
    
    def export_analytics_data(self, format_type: str = 'json') -> str:
        """Analytics ma'lumotlarini eksport qilish"""
        data = {
            'market_data': [asdict(m) for m in list(self.market_data)[-100:]],
            'user_data': {k: {
                'last_activity': v.get('last_activity').isoformat() if v.get('last_activity') else None,
                'total_trades': v.get('total_trades', 0),
                'total_profit_loss': v.get('total_profit_loss', 0.0),
                'recent_activities': len(v.get('activities', []))
            } for k, v in self.user_data.items()},
            'system_data': [asdict(m) for m in list(self.system_data)[-50:]],
            'alerts': [a for a in list(self.alerts)[-20:]],
            'export_timestamp': datetime.now().isoformat()
        }
        
        if format_type.lower() == 'json':
            return json.dumps(data, indent=2, default=str)
        else:
            return str(data)  # Simple string representation
    
    def get_dashboard_data(self) -> Dict:
        """Dashboard uchun real-time data"""
        return {
            'market_overview': self.get_market_analytics_report('1h'),
            'user_metrics': self.get_user_analytics_report(),
            'system_health': self.get_system_analytics_report(),
            'signal_performance': self.get_signal_performance_report(),
            'recent_alerts': [a for a in list(self.alerts)[-10:]],
            'active_signals': len(self.signal_data),
            'total_users': len(self.user_data),
            'last_update': datetime.now().isoformat()
        }


# Utility functions
def create_analytics_engine(config: Optional[Dict] = None) -> AnalyticsEngine:
    """Analytics engine yaratish uchun factory funksiya"""
    return AnalyticsEngine(config)


async def run_analytics_demonstration():
    """Analytics engine demo"""
    engine = create_analytics_engine()
    
    # Add some sample data
    import random
    
    print("Real-time Analytics Engine Demo boshlanmoqda...")
    
    # Sample market data
    for i in range(20):
        market_data = {
            'symbol': 'EURUSD',
            'price': 1.1000 + random.uniform(-0.01, 0.01),
            'volume': random.uniform(1000, 5000),
            'volatility': random.uniform(0.001, 0.02),
            'sma_20': 1.1000 + random.uniform(-0.005, 0.005),
            'sma_50': 1.1000 + random.uniform(-0.01, 0.01),
            'rsi': random.uniform(20, 80),
            'macd': random.uniform(-0.001, 0.001)
        }
        engine.add_market_data(market_data)
        await asyncio.sleep(0.1)
    
    # Sample user data
    engine.add_user_data('user_001', {
        'action': 'login',
        'timestamp': datetime.now(),
        'metadata': {'device': 'mobile'}
    })
    
    engine.add_user_data('user_001', {
        'action': 'trade',
        'timestamp': datetime.now(),
        'size': 1000,
        'profit_loss': 50.0,
        'symbol': 'EURUSD'
    })
    
    # Generate reports
    print("\n=== MARKET ANALYTICS REPORT ===")
    market_report = engine.get_market_analytics_report('1h')
    print(json.dumps(market_report, indent=2, default=str))
    
    print("\n=== USER ANALYTICS REPORT ===")
    user_report = engine.get_user_analytics_report()
    print(json.dumps(user_report, indent=2, default=str))
    
    print("\n=== SYSTEM ANALYTICS REPORT ===")
    system_report = engine.get_system_analytics_report()
    print(json.dumps(system_report, indent=2, default=str))
    
    print("\n=== DASHBOARD DATA ===")
    dashboard_data = engine.get_dashboard_data()
    print(f"Active signals: {dashboard_data['active_signals']}")
    print(f"Total users: {dashboard_data['total_users']}")
    print(f"Recent alerts: {len(dashboard_data['recent_alerts'])}")
    
    print("\nDemo tugallandi!")


if __name__ == "__main__":
    # Demo ishga tushirish
    asyncio.run(run_analytics_demonstration())