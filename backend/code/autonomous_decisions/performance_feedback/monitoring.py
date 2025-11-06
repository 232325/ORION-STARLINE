"""
Performance Monitor

Real-time performance monitoring va feedback signal generation
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import numpy as np
from collections import deque

@dataclass
class PerformanceMetrics:
    """Performance metrics"""
    timestamp: datetime
    total_return: float
    daily_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    var_1d: float
    sortino_ratio: float
    calmar_ratio: float

class PerformanceMonitor:
    """
    Real-time performance monitoring
    
    - Real-time performance tracking
    - Performance signal generation  
    - Risk metrics monitoring
    - Attribution analysis preparation
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Monitoring settings
        self.update_interval = config.get("performance_update_interval", 60)
        self.max_history_size = config.get("max_performance_history", 1000)
        
        # Performance tracking
        self.performance_history = deque(maxlen=self.max_history_size)
        self.current_metrics = None
        self.is_running = False
        
        # Performance baselines
        self.benchmarks = {
            "buy_hold": 0.08,  # 8% annual return
            "risk_free": 0.02,  # 2% risk-free rate
            "market_index": 0.10  # 10% market return
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            "drawdown_warning": 0.05,  # 5%
            "drawdown_critical": 0.10,  # 10%
            "volatility_high": 0.20,  # 20%
            "sharpe_low": 0.5,  # 0.5
            "var_high": 0.03  # 3%
        }
        
        # Data sources
        self.data_sources = {
            "portfolio": self._get_portfolio_data,
            "trades": self._get_trade_data,
            "market": self._get_market_data
        }
    
    async def _get_portfolio_data(self) -> Dict:
        """Portfolio data olish"""
        # Real implementation da actual portfolio API
        return {
            "total_value": 100000.0,
            "positions": [
                {"symbol": "EURUSD", "size": 50000, "pnl": 250.50},
                {"symbol": "GBPUSD", "size": 30000, "pnl": -120.75}
            ],
            "cash": 50000.0,
            "timestamp": datetime.now()
        }
    
    async def _get_trade_data(self) -> List[Dict]:
        """Trade data olish"""
        # Recent trades data
        return [
            {
                "timestamp": datetime.now() - timedelta(hours=1),
                "symbol": "EURUSD",
                "side": "buy",
                "size": 10000,
                "price": 1.0945,
                "pnl": 50.25
            },
            {
                "timestamp": datetime.now() - timedelta(hours=2),
                "symbol": "GBPUSD", 
                "side": "sell",
                "size": 8000,
                "price": 1.2750,
                "pnl": -80.30
            }
        ]
    
    async def _get_market_data(self) -> Dict:
        """Market data olish"""
        return {
            "EURUSD": {"price": 1.0945, "volatility": 0.012},
            "GBPUSD": {"price": 1.2750, "volatility": 0.015},
            "timestamp": datetime.now()
        }
    
    def start(self):
        """Monitoring ni boshlash"""
        if self.is_running:
            self.logger.warning("Performance monitor allaqachon ishlayapti")
            return
        
        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Performance monitoring started")
    
    def stop(self):
        """Monitoring ni to'xtatish"""
        if not self.is_running:
            return
        
        self.is_running = False
        if hasattr(self, 'monitoring_task'):
            self.monitoring_task.cancel()
        
        self.logger.info("Performance monitoring stopped")
    
    async def _monitoring_loop(self):
        """Asosiy monitoring loop"""
        while self.is_running:
            try:
                await self.update_performance()
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring loop xatosi: {str(e)}")
                await asyncio.sleep(5)  # Xato bo'lsa qisqa pauza
    
    async def update_performance(self):
        """Performance ni yangilash"""
        try:
            # Ma'lumotlarni to'plash
            data = await self._collect_data()
            
            # Performance metrics hisoblash
            metrics = await self._calculate_metrics(data)
            
            # History ga qo'shish
            self.performance_history.append(metrics)
            self.current_metrics = metrics
            
            # Alert check
            await self._check_alerts(metrics)
            
            # Event emit
            await self._emit_performance_update(metrics)
            
            self.logger.debug("Performance updated successfully")
            
        except Exception as e:
            self.logger.error(f"Performance update xatosi: {str(e)}")
    
    async def _collect_data(self) -> Dict:
        """Ma'lumotlarni to'plash"""
        tasks = []
        for source_name, source_func in self.data_sources.items():
            tasks.append(source_func())
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        data = {}
        for i, (source_name, result) in enumerate(zip(self.data_sources.keys(), results)):
            if isinstance(result, Exception):
                self.logger.error(f"Data source error ({source_name}): {str(result)}")
                data[source_name] = {"error": str(result)}
            else:
                data[source_name] = result
        
        return data
    
    async def _calculate_metrics(self, data: Dict) -> PerformanceMetrics:
        """Performance metrics hisoblash"""
        # Portfolio basic metrics
        portfolio_data = data.get("portfolio", {})
        current_value = portfolio_data.get("total_value", 100000.0)
        
        # Previous value (agar bor bo'lsa)
        previous_value = current_value
        if self.performance_history:
            previous_metrics = self.performance_history[-1]
            # Bu real implementation da current_value ni last value dan olish kerak
        
        daily_return = (current_value - previous_value) / previous_value if previous_value > 0 else 0.0
        
        # Calculate rolling metrics
        returns = self._get_recent_returns()
        if len(returns) < 2:
            volatility = 0.0
            sharpe_ratio = 0.0
            sortino_ratio = 0.0
        else:
            volatility = np.std(returns) * np.sqrt(252)  # Annualized
            excess_returns = returns - self.benchmarks["risk_free"] / 252
            sharpe_ratio = np.mean(excess_returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
            
            downside_returns = returns[returns < 0]
            downside_deviation = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0.001
            sortino_ratio = np.mean(excess_returns) / downside_deviation if downside_deviation > 0 else 0
        
        # Drawdown calculation
        max_drawdown = self._calculate_max_drawdown()
        
        # Win rate va profit factor
        trades_data = data.get("trades", [])
        win_rate, profit_factor = self._calculate_trade_metrics(trades_data)
        
        # VaR calculation
        var_1d = self._calculate_var_1d(returns)
        
        # Total return (cumulative)
        total_return = self._calculate_total_return()
        
        # Calmar ratio
        calmar_ratio = total_return / max_drawdown if max_drawdown > 0 else 0
        
        return PerformanceMetrics(
            timestamp=datetime.now(),
            total_return=total_return,
            daily_return=daily_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            var_1d=var_1d,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio
        )
    
    def _get_recent_returns(self) -> List[float]:
        """Recent returns olish"""
        if not self.performance_history:
            return []
        
        returns = []
        for i in range(1, len(self.performance_history)):
            prev_value = 100000.0  # Bu real implementation da portfolio value bo'lishi kerak
            curr_value = prev_value * (1 + self.performance_history[i].daily_return)
            daily_return = (curr_value - prev_value) / prev_value
            returns.append(daily_return)
        
        return returns
    
    def _calculate_max_drawdown(self) -> float:
        """Maximum drawdown hisoblash"""
        if len(self.performance_history) < 2:
            return 0.0
        
        # Simplified implementation
        peak = 100000.0  # Starting value
        max_dd = 0.0
        
        for metrics in self.performance_history:
            current_value = peak * (1 + metrics.total_return)
            drawdown = (peak - current_value) / peak
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
    
    def _calculate_trade_metrics(self, trades: List[Dict]) -> Tuple[float, float]:
        """Trade-based metrics hisoblash"""
        if not trades:
            return 0.0, 0.0
        
        winning_trades = [t for t in trades if t.get("pnl", 0) > 0]
        losing_trades = [t for t in trades if t.get("pnl", 0) < 0]
        
        win_rate = len(winning_trades) / len(trades) if trades else 0
        
        total_profit = sum(t.get("pnl", 0) for t in winning_trades)
        total_loss = abs(sum(t.get("pnl", 0) for t in losing_trades))
        
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        return win_rate, profit_factor
    
    def _calculate_var_1d(self, returns: List[float]) -> float:
        """1-day VaR hisoblash (95% confidence)"""
        if len(returns) < 30:
            return 0.03  # Default fallback
        
        # Historical VaR
        sorted_returns = sorted(returns)
        var_index = int(0.05 * len(sorted_returns))  # 5th percentile
        return abs(sorted_returns[var_index])
    
    def _calculate_total_return(self) -> float:
        """Total return hisoblash"""
        if not self.performance_history:
            return 0.0
        
        # Cumulative return
        return sum(m.daily_return for m in self.performance_history)
    
    async def _check_alerts(self, metrics: PerformanceMetrics):
        """Alert check"""
        alerts = []
        
        if metrics.max_drawdown > self.alert_thresholds["drawdown_critical"]:
            alerts.append(f"CRITICAL: Max drawdown {metrics.max_drawdown:.2%}")
        elif metrics.max_drawdown > self.alert_thresholds["drawdown_warning"]:
            alerts.append(f"WARNING: Max drawdown {metrics.max_drawdown:.2%}")
        
        if metrics.volatility > self.alert_thresholds["volatility_high"]:
            alerts.append(f"HIGH VOLATILITY: {metrics.volatility:.2%}")
        
        if metrics.sharpe_ratio < self.alert_thresholds["sharpe_low"]:
            alerts.append(f"LOW SHARPE: {metrics.sharpe_ratio:.2f}")
        
        if metrics.var_1d > self.alert_thresholds["var_high"]:
            alerts.append(f"HIGH VaR: {metrics.var_1d:.2%}")
        
        for alert in alerts:
            self.logger.warning(alert)
    
    async def _emit_performance_update(self, metrics: PerformanceMetrics):
        """Performance update event"""
        # Bu event system integration
        event_data = {
            "metrics": asdict(metrics),
            "score": self._calculate_performance_score(metrics)
        }
        
        # Event system ga emit qilish (implementation depends on context)
        # self.event_system.emit_performance_update(event_data)
        pass
    
    def _calculate_performance_score(self, metrics: PerformanceMetrics) -> float:
        """Performance score hisoblash (0-1)"""
        # Multi-factor performance score
        score = 0.0
        
        # Sharpe ratio contribution (weight: 0.3)
        sharpe_score = min(metrics.sharpe_ratio / 2.0, 1.0)  # Normalize to 0-1
        score += 0.3 * sharpe_score
        
        # Drawdown penalty (weight: 0.2)
        drawdown_score = max(0, 1 - metrics.max_drawdown / 0.2)
        score += 0.2 * drawdown_score
        
        # Win rate contribution (weight: 0.2)
        score += 0.2 * metrics.win_rate
        
        # Profit factor contribution (weight: 0.15)
        profit_score = min(metrics.profit_factor / 2.0, 1.0)
        score += 0.15 * profit_score
        
        # Volatility penalty (weight: 0.15)
        vol_score = max(0, 1 - metrics.volatility / 0.3)
        score += 0.15 * vol_score
        
        return min(max(score, 0.0), 1.0)
    
    async def get_current_performance(self) -> Dict[str, Any]:
        """Current performance olish"""
        if self.current_metrics is None:
            await self.update_performance()
        
        if self.current_metrics is None:
            return {}
        
        return {
            "metrics": asdict(self.current_metrics),
            "score": self._calculate_performance_score(self.current_metrics),
            "timestamp": self.current_metrics.timestamp.isoformat()
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Performance summary olish"""
        if not self.performance_history:
            return {"message": "No performance data available"}
        
        latest = self.performance_history[-1]
        
        # Recent performance trend
        recent_metrics = list(self.performance_history)[-10:]  # Last 10 points
        recent_returns = [m.daily_return for m in recent_metrics]
        
        return {
            "current": asdict(latest),
            "score": self._calculate_performance_score(latest),
            "recent_trend": {
                "avg_daily_return": np.mean(recent_returns),
                "volatility": np.std(recent_returns)
            },
            "alerts": self._get_active_alerts(),
            "history_size": len(self.performance_history)
        }
    
    def _get_active_alerts(self) -> List[str]:
        """Active alerts olish"""
        if not self.current_metrics:
            return []
        
        alerts = []
        
        if self.current_metrics.max_drawdown > self.alert_thresholds["drawdown_warning"]:
            alerts.append(f"Drawdown: {self.current_metrics.max_drawdown:.2%}")
        
        if self.current_metrics.volatility > self.alert_thresholds["volatility_high"]:
            alerts.append(f"High Volatility: {self.current_metrics.volatility:.2%}")
        
        return alerts