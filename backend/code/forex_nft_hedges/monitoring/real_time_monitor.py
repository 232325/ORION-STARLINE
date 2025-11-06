"""
Forex Hedging NFT - Real-time Performance va Risk Monitoring Tizimi
Haqiqiy vaqtda performance va risklarni kuzatish
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import numpy as np
import logging

from config import ForexPair, HedgeType, MarketRegime, config
from core.forex_hedge_core import ForexHedgeManager, HedgePosition, QuantumPortfolio

@dataclass
class PerformanceMetrics:
    """Performance metrikalari"""
    timestamp: int
    total_pnl: float
    daily_return: float
    cumulative_return: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    var_95: float
    var_99: float
    beta: float
    alpha: float
    information_ratio: float
    volatility: float
    hedge_effectiveness: float

@dataclass
class RiskAlert:
    """Risk alert"""
    alert_id: str
    timestamp: int
    severity: str  # INFO, WARNING, CRITICAL
    alert_type: str  # DRAWDOWN, VAR, CONCENTRATION, QUANTUM_ERROR
    message: str
    current_value: float
    threshold_value: float
    affected_positions: List[str]
    resolved: bool = False

@dataclass
class SystemHealth:
    """Tizim sog'ligi ma'lumotlari"""
    timestamp: int
    cpu_usage: float
    memory_usage: float
    network_latency: float
    quantum_backend_health: str
    data_feed_status: str
    blockchain_connection: str
    alert_count: int

class PerformanceCalculator:
    """Performance hisoblash klassi"""
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% risk-free rate
        
    async def calculate_portfolio_metrics(
        self, 
        positions: List[HedgePosition],
        benchmark_returns: List[float] = None
    ) -> PerformanceMetrics:
        """Portfolio metrikalarini hisoblash"""
        
        if not positions:
            return self._empty_metrics()
        
        current_time = int(time.time())
        
        # PnL ma'lumotlari
        total_pnl = sum(pos.performance_metrics.get("pnl", 0.0) for pos in positions)
        total_notional = sum(pos.notional_amount for pos in positions)
        
        # Returns hisoblash
        returns = [pos.performance_metrics.get("daily_return", 0.0) for pos in positions]
        cumulative_return = np.cumprod(1 + np.array(returns))[-1] - 1
        
        # Risk metrikalari
        portfolio_volatility = np.std(returns) if returns else 0
        
        # Sharpe ratio
        mean_return = np.mean(returns) if returns else 0
        sharpe_ratio = (mean_return - self.risk_free_rate/252) / portfolio_volatility if portfolio_volatility > 0 else 0
        
        # Sortino ratio ( downside deviation )
        downside_returns = [r for r in returns if r < 0]
        downside_deviation = np.std(downside_returns) if downside_returns else 0
        sortino_ratio = (mean_return - self.risk_free_rate/252) / downside_deviation if downside_deviation > 0 else 0
        
        # Maximum drawdown
        max_drawdown = await self._calculate_max_drawdown(returns)
        
        # Calmar ratio
        calmar_ratio = cumulative_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # VaR (Value at Risk)
        var_95 = await self._calculate_var(returns, 0.05)
        var_99 = await self._calculate_var(returns, 0.01)
        
        # Alpha va Beta (benchmark bilan)
        alpha, beta = await self._calculate_alpha_beta(returns, benchmark_returns)
        
        # Information ratio
        information_ratio = await self._calculate_information_ratio(returns, benchmark_returns)
        
        # Hedge effectiveness
        hedge_effectiveness = await self._calculate_hedge_effectiveness(positions)
        
        return PerformanceMetrics(
            timestamp=current_time,
            total_pnl=total_pnl,
            daily_return=mean_return,
            cumulative_return=cumulative_return,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            max_drawdown=max_drawdown,
            var_95=var_95,
            var_99=var_99,
            beta=beta,
            alpha=alpha,
            information_ratio=information_ratio,
            volatility=portfolio_volatility,
            hedge_effectiveness=hedge_effectiveness
        )
    
    def _empty_metrics(self) -> PerformanceMetrics:
        """Bo'sh metrikalar"""
        return PerformanceMetrics(
            timestamp=int(time.time()),
            total_pnl=0.0,
            daily_return=0.0,
            cumulative_return=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            calmar_ratio=0.0,
            max_drawdown=0.0,
            var_95=0.0,
            var_99=0.0,
            beta=0.0,
            alpha=0.0,
            information_ratio=0.0,
            volatility=0.0,
            hedge_effectiveness=0.0
        )
    
    async def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Maximum drawdown hisoblash"""
        if not returns:
            return 0.0
        
        cumulative = np.cumprod(1 + np.array(returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        return float(np.min(drawdown))
    
    async def _calculate_var(self, returns: List[float], confidence_level: float) -> float:
        """VaR hisoblash"""
        if not returns:
            return 0.0
        
        return float(np.percentile(returns, confidence_level * 100))
    
    async def _calculate_alpha_beta(
        self, 
        portfolio_returns: List[float], 
        benchmark_returns: List[float]
    ) -> Tuple[float, float]:
        """Alpha va Beta hisoblash"""
        if not benchmark_returns or len(benchmark_returns) != len(portfolio_returns):
            return 0.0, 0.0
        
        portfolio_array = np.array(portfolio_returns)
        benchmark_array = np.array(benchmark_returns)
        
        # Beta = Covariance / Variance
        covariance = np.cov(portfolio_array, benchmark_array)[0, 1]
        benchmark_variance = np.var(benchmark_array)
        beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
        
        # Alpha = Mean(Portfolio) - Beta * Mean(Benchmark)
        portfolio_mean = np.mean(portfolio_array)
        benchmark_mean = np.mean(benchmark_array)
        alpha = portfolio_mean - beta * benchmark_mean
        
        return float(alpha), float(beta)
    
    async def _calculate_information_ratio(
        self, 
        portfolio_returns: List[float], 
        benchmark_returns: List[float]
    ) -> float:
        """Information ratio hisoblash"""
        if not benchmark_returns or len(benchmark_returns) != len(portfolio_returns):
            return 0.0
        
        excess_returns = np.array(portfolio_returns) - np.array(benchmark_returns)
        tracking_error = np.std(excess_returns)
        
        return np.mean(excess_returns) / tracking_error if tracking_error > 0 else 0.0
    
    async def _calculate_hedge_effectiveness(self, positions: List[HedgePosition]) -> float:
        """Hedge effectiveness hisoblash"""
        if not positions:
            return 0.0
        
        total_hedge_ratio = sum(pos.hedge_ratio for pos in positions)
        avg_hedge_ratio = total_hedge_ratio / len(positions)
        
        # Hedge effectiveness = 1 - (unhedged_variance / total_variance)
        hedge_effectiveness = min(avg_hedge_ratio, 0.95)  # Cap at 95%
        
        return hedge_effectiveness

class RiskMonitor:
    """Risk monitoring klassi"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.alert_thresholds = {
            "max_drawdown": config.risk_limits.get("max_forex_exposure", 0.25),
            "var_limit": config.risk_limits.get("var_limit", 0.05),
            "position_concentration": 0.4,
            "quantum_error_rate": 0.05
        }
        
    async def check_risk_alerts(
        self, 
        positions: List[HedgePosition], 
        performance: PerformanceMetrics
    ) -> List[RiskAlert]:
        """Risk alertlarni tekshirish"""
        alerts = []
        
        # Drawdown alert
        if abs(performance.max_drawdown) > self.alert_thresholds["max_drawdown"]:
            alert = RiskAlert(
                alert_id=f"DD_{int(time.time())}",
                timestamp=int(time.time()),
                severity="WARNING",
                alert_type="DRAWDOWN",
                message=f"Maximum drawdown {performance.max_drawdown:.2%} thresholddan yuqori",
                current_value=abs(performance.max_drawdown),
                threshold_value=self.alert_thresholds["max_drawdown"],
                affected_positions=[pos.position_id for pos in positions]
            )
            alerts.append(alert)
        
        # VaR alert
        if abs(performance.var_95) > self.alert_thresholds["var_limit"]:
            alert = RiskAlert(
                alert_id=f"VaR_{int(time.time())}",
                timestamp=int(time.time()),
                severity="CRITICAL",
                alert_type="VAR",
                message=f"VaR (95%) {performance.var_95:.2%} limitdan oshdi",
                current_value=abs(performance.var_95),
                threshold_value=self.alert_thresholds["var_limit"],
                affected_positions=[pos.position_id for pos in positions]
            )
            alerts.append(alert)
        
        # Position concentration alert
        concentration_alerts = await self._check_position_concentration(positions)
        alerts.extend(concentration_alerts)
        
        return alerts
    
    async def _check_position_concentration(self, positions: List[HedgePosition]) -> List[RiskAlert]:
        """Position konsentrasiyasini tekshirish"""
        alerts = []
        
        if not positions:
            return alerts
        
        # Juftlik bo'yicha konsentatsiya
        pair_concentration = defaultdict(float)
        total_notional = sum(pos.notional_amount for pos in positions)
        
        for position in positions:
            pair_concentration[position.pair.value] += position.notional_amount
        
        # Har bir juftlik uchun konsentatsiya tekshirish
        for pair, notional in pair_concentration.items():
            concentration_ratio = notional / total_notional if total_notional > 0 else 0
            
            if concentration_ratio > self.alert_thresholds["position_concentration"]:
                affected_positions = [
                    pos.position_id for pos in positions 
                    if pos.pair.value == pair
                ]
                
                alert = RiskAlert(
                    alert_id=f"CONC_{pair}_{int(time.time())}",
                    timestamp=int(time.time()),
                    severity="WARNING",
                    alert_type="CONCENTRATION",
                    message=f"Juftlik {pair} konsentatsiyasi {concentration_ratio:.2%} dan yuqori",
                    current_value=concentration_ratio,
                    threshold_value=self.alert_thresholds["position_concentration"],
                    affected_positions=affected_positions
                )
                alerts.append(alert)
        
        return alerts

class RealTimeMonitor:
    """Asosiy real-time monitoring klassi"""
    
    def __init__(self, hedge_manager: ForexHedgeManager):
        self.hedge_manager = hedge_manager
        self.performance_calc = PerformanceCalculator()
        self.risk_monitor = RiskMonitor()
        self.logger = logging.getLogger(__name__)
        
        # Data structures
        self.metrics_history: deque = deque(maxlen=1000)
        self.current_alerts: List[RiskAlert] = []
        self.system_health: Optional[SystemHealth] = None
        self.subscribers: List[Callable] = []
        
        # Monitoring flags
        self.monitoring_active = False
        self.update_interval = 1  # soniya
        
    async def start_monitoring(self):
        """Monitoring ni boshlash"""
        self.monitoring_active = True
        self.logger.info("Real-time monitoring started")
        
        # Monitoring loop
        asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """Monitoring ni to'xtatish"""
        self.monitoring_active = False
        self.logger.info("Real-time monitoring stopped")
    
    async def _monitoring_loop(self):
        """Asosiy monitoring tsikli"""
        while self.monitoring_active:
            try:
                await self._update_metrics()
                await self._check_alerts()
                await self._update_system_health()
                await self._notify_subscribers()
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(1)
    
    async def _update_metrics(self):
        """Performance metrikalarni yangilash"""
        try:
            # Barcha portfolio'larni olish
            all_positions = []
            for portfolio in self.hedge_manager.portfolios.values():
                all_positions.extend(portfolio.hedge_positions)
            
            # Hamda individual positions
            for position in self.hedge_manager.positions.values():
                all_positions.append(position)
            
            # Metrikalarni hisoblash
            metrics = await self.performance_calc.calculate_portfolio_metrics(all_positions)
            self.metrics_history.append(metrics)
            
        except Exception as e:
            self.logger.error(f"Metrics update error: {e}")
    
    async def _check_alerts(self):
        """Alertlarni tekshirish"""
        try:
            if self.metrics_history:
                latest_metrics = self.metrics_history[-1]
                positions = []
                
                # Joriy positions
                for position in self.hedge_manager.positions.values():
                    positions.append(position)
                
                # Yangi alertlar
                new_alerts = await self.risk_monitor.check_risk_alerts(positions, latest_metrics)
                
                # Alertlarni qo'shish
                for alert in new_alerts:
                    if not any(a.alert_id == alert.alert_id for a in self.current_alerts):
                        self.current_alerts.append(alert)
                        self.logger.warning(f"New risk alert: {alert.message}")
            
        except Exception as e:
            self.logger.error(f"Alert check error: {e}")
    
    async def _update_system_health(self):
        """System sog'ligi ma'lumotlarini yangilash"""
        try:
            # Bu yerda real system metrics olinadi
            # Hozircha random data
            self.system_health = SystemHealth(
                timestamp=int(time.time()),
                cpu_usage=np.random.uniform(20, 80),
                memory_usage=np.random.uniform(30, 70),
                network_latency=np.random.uniform(10, 100),
                quantum_backend_health="healthy",
                data_feed_status="connected",
                blockchain_connection="synced",
                alert_count=len(self.current_alerts)
            )
            
        except Exception as e:
            self.logger.error(f"System health update error: {e}")
    
    async def _notify_subscribers(self):
        """Subscriber'larni bildirish"""
        try:
            if self.metrics_history:
                latest_metrics = self.metrics_history[-1]
                data = {
                    "metrics": latest_metrics,
                    "alerts": self.current_alerts,
                    "system_health": self.system_health,
                    "total_positions": len(self.hedge_manager.positions),
                    "total_portfolios": len(self.hedge_manager.portfolios)
                }
                
                for subscriber in self.subscribers:
                    try:
                        await subscriber(data)
                    except Exception as e:
                        self.logger.error(f"Subscriber notification error: {e}")
                        
        except Exception as e:
            self.logger.error(f"Notification error: {e}")
    
    async def get_live_metrics(self) -> Dict:
        """Joriy metrikalarni olish"""
        if not self.metrics_history:
            return {}
        
        latest = self.metrics_history[-1]
        return {
            "total_pnl": latest.total_pnl,
            "daily_return": latest.daily_return,
            "cumulative_return": latest.cumulative_return,
            "sharpe_ratio": latest.sharpe_ratio,
            "max_drawdown": latest.max_drawdown,
            "var_95": latest.var_95,
            "hedge_effectiveness": latest.hedge_effectiveness,
            "timestamp": latest.timestamp,
            "alerts_count": len(self.current_alerts),
            "active_positions": len(self.hedge_manager.positions),
            "active_portfolios": len(self.hedge_manager.portfolios)
        }
    
    async def get_performance_analytics(self, period_hours: int = 24) -> Dict:
        """Period bo'yicha performance analitika"""
        if not self.metrics_history:
            return {}
        
        cutoff_time = int(time.time()) - (period_hours * 3600)
        period_metrics = [
            m for m in self.metrics_history 
            if m.timestamp > cutoff_time
        ]
        
        if not period_metrics:
            return {}
        
        latest = period_metrics[-1]
        first = period_metrics[0]
        
        # Period return hisoblash
        period_return = latest.cumulative_return - first.cumulative_return
        
        # Average metrikalar
        avg_sharpe = np.mean([m.sharpe_ratio for m in period_metrics])
        avg_volatility = np.mean([m.volatility for m in period_metrics])
        max_dd = min([m.max_drawdown for m in period_metrics])
        
        return {
            "period_hours": period_hours,
            "period_return": period_return,
            "avg_daily_return": np.mean([m.daily_return for m in period_metrics]),
            "avg_sharpe_ratio": avg_sharpe,
            "avg_volatility": avg_volatility,
            "period_max_drawdown": max_dd,
            "total_alerts": len([a for a in self.current_alerts if a.timestamp > cutoff_time]),
            "data_points": len(period_metrics)
        }
    
    async def get_risk_summary(self) -> Dict:
        """Risk summary olish"""
        if not self.current_alerts:
            return {"status": "healthy", "alerts": 0, "critical_issues": 0}
        
        critical_alerts = [a for a in self.current_alerts if a.severity == "CRITICAL"]
        warning_alerts = [a for a in self.current_alerts if a.severity == "WARNING"]
        
        return {
            "status": "critical" if critical_alerts else "warning" if warning_alerts else "healthy",
            "total_alerts": len(self.current_alerts),
            "critical_count": len(critical_alerts),
            "warning_count": len(warning_alerts),
            "active_alerts": [
                {
                    "type": alert.alert_type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "timestamp": alert.timestamp
                }
                for alert in self.current_alerts if not alert.resolved
            ]
        }
    
    def subscribe_to_updates(self, callback: Callable):
        """Real-time updates uchun subscriber"""
        self.subscribers.append(callback)
    
    def unsubscribe_from_updates(self, callback: Callable):
        """Subscriber'dan chiqish"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    async def export_data(self, filename: str = None) -> str:
        """Data ni export qilish"""
        if not filename:
            filename = f"forex_hedge_data_{int(time.time())}.json"
        
        export_data = {
            "export_timestamp": int(time.time()),
            "metrics_history": [asdict(m) for m in list(self.metrics_history)],
            "current_alerts": [asdict(a) for a in self.current_alerts],
            "system_health": asdict(self.system_health) if self.system_health else None,
            "active_positions": len(self.hedge_manager.positions),
            "active_portfolios": len(self.hedge_manager.portfolios)
        }
        
        return json.dumps(export_data, indent=2, default=str)
