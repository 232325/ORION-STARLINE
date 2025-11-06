"""
Forex Hedging NFT - Analytics Engine
Tizim analitikasi va hisobot tizimi
"""

import asyncio
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

from monitoring.real_time_monitor import RealTimeMonitor, PerformanceMetrics, RiskAlert

@dataclass
class AnalyticsReport:
    """Analytics report struktura"""
    report_id: str
    timestamp: int
    report_type: str  # daily, weekly, monthly, performance, risk
    period_start: int
    period_end: int
    data: Dict
    summary: Dict
    insights: List[str]
    recommendations: List[str]

class PerformanceAnalyzer:
    """Performance analitika klassi"""
    
    def __init__(self, monitor: RealTimeMonitor):
        self.monitor = monitor
        self.logger = logging.getLogger(__name__)
    
    async def analyze_hedge_performance(self, period_hours: int = 24) -> Dict:
        """Hedge performance tahlili"""
        
        # Period metrikalar
        performance_data = await self.monitor.get_performance_analytics(period_hours)
        
        # Individual position tahlil
        position_analysis = await self._analyze_positions()
        
        # Strategy performance
        strategy_performance = await self._analyze_strategies()
        
        # Quantum vs classical comparison
        quantum_analysis = await self._analyze_quantum_performance()
        
        return {
            "period_summary": performance_data,
            "position_analysis": position_analysis,
            "strategy_performance": strategy_performance,
            "quantum_analysis": quantum_analysis,
            "generated_at": int(time.time())
        }
    
    async def _analyze_positions(self) -> Dict:
        """Individual position tahlil"""
        positions = list(self.monitor.hedge_manager.positions.values())
        
        if not positions:
            return {"status": "no_positions"}
        
        # Position performance by pair
        pair_performance = defaultdict(lambda: {
            "count": 0, "total_pnl": 0.0, "total_notional": 0.0, "avg_return": 0.0
        })
        
        for position in positions:
            pair = position.pair.value
            pair_performance[pair]["count"] += 1
            pair_performance[pair]["total_pnl"] += position.performance_metrics.get("pnl", 0.0)
            pair_performance[pair]["total_notional"] += position.notional_amount
            pair_performance[pair]["avg_return"] += position.performance_metrics.get("daily_return", 0.0)
        
        # Calculate averages
        for pair_data in pair_performance.values():
            if pair_data["count"] > 0:
                pair_data["avg_return"] /= pair_data["count"]
                pair_data["avg_pnl_per_position"] = pair_data["total_pnl"] / pair_data["count"]
                pair_data["return_on_notional"] = pair_data["total_pnl"] / pair_data["total_notional"] if pair_data["total_notional"] > 0 else 0
        
        return {
            "total_positions": len(positions),
            "pairs_analysis": dict(pair_performance),
            "best_performing_pair": self._get_best_performing_pair(pair_performance),
            "worst_performing_pair": self._get_worst_performing_pair(pair_performance)
        }
    
    async def _analyze_strategies(self) -> Dict:
        """Strategy performance tahlil"""
        positions = list(self.monitor.hedge_manager.positions.values())
        
        if not positions:
            return {"status": "no_strategies"}
        
        # Strategy type analysis
        strategy_performance = defaultdict(lambda: {
            "count": 0, "total_pnl": 0.0, "success_rate": 0.0
        })
        
        for position in positions:
            strategy = position.hedge_type.value
            strategy_performance[strategy]["count"] += 1
            strategy_performance[strategy]["total_pnl"] += position.performance_metrics.get("pnl", 0.0)
            
            # Success rate calculation (positive PnL)
            if position.performance_metrics.get("pnl", 0.0) > 0:
                strategy_performance[strategy]["positive_count"] = strategy_performance[strategy].get("positive_count", 0) + 1
        
        # Calculate success rates
        for strategy, data in strategy_performance.items():
            if data["count"] > 0:
                data["success_rate"] = data.get("positive_count", 0) / data["count"]
                data["avg_pnl"] = data["total_pnl"] / data["count"]
        
        return {
            "strategies_analysis": dict(strategy_performance),
            "best_strategy": self._get_best_strategy(strategy_performance),
            "quantum_enhanced_count": sum(1 for p in positions if p.quantum_enhanced)
        }
    
    async def _analyze_quantum_performance(self) -> Dict:
        """Quantum vs classical performance tahlil"""
        positions = list(self.monitor.hedge_manager.positions.values())
        
        if not positions:
            return {"status": "no_data"}
        
        quantum_positions = [p for p in positions if p.quantum_enhanced]
        classical_positions = [p for p in positions if not p.quantum_enhanced]
        
        def analyze_group(group_positions, group_name):
            if not group_positions:
                return {"count": 0}
            
            total_pnl = sum(pos.performance_metrics.get("pnl", 0.0) for pos in group_positions)
            avg_return = np.mean([pos.performance_metrics.get("daily_return", 0.0) for pos in group_positions])
            
            return {
                "count": len(group_positions),
                "total_pnl": total_pnl,
                "avg_return": avg_return,
                "avg_pnl_per_position": total_pnl / len(group_positions)
            }
        
        return {
            "quantum_positions": analyze_group(quantum_positions, "quantum"),
            "classical_positions": analyze_group(classical_positions, "classical"),
            "quantum_advantage": self._calculate_quantum_advantage(quantum_positions, classical_positions)
        }
    
    def _get_best_performing_pair(self, pair_performance: Dict) -> str:
        """Eng yaxshi performer pair"""
        if not pair_performance:
            return "N/A"
        
        best_pair = max(pair_performance.items(), 
                       key=lambda x: x[1].get("return_on_notional", 0))
        return best_pair[0]
    
    def _get_worst_performing_pair(self, pair_performance: Dict) -> str:
        """Eng yomon performer pair"""
        if not pair_performance:
            return "N/A"
        
        worst_pair = min(pair_performance.items(), 
                        key=lambda x: x[1].get("return_on_notional", 0))
        return worst_pair[0]
    
    def _get_best_strategy(self, strategy_performance: Dict) -> str:
        """Eng yaxshi performer strategy"""
        if not strategy_performance:
            return "N/A"
        
        best_strategy = max(strategy_performance.items(),
                           key=lambda x: x[1].get("avg_pnl", 0))
        return best_strategy[0]
    
    def _calculate_quantum_advantage(self, quantum_positions: List, classical_positions: List) -> float:
        """Quantum ustunlik hisoblash"""
        if not quantum_positions or not classical_positions:
            return 0.0
        
        quantum_avg_pnl = np.mean([pos.performance_metrics.get("pnl", 0.0) for pos in quantum_positions])
        classical_avg_pnl = np.mean([pos.performance_metrics.get("pnl", 0.0) for pos in classical_positions])
        
        if classical_avg_pnl == 0:
            return 0.0
        
        return (quantum_avg_pnl - classical_avg_pnl) / abs(classical_avg_pnl)

class RiskAnalyzer:
    """Risk analitika klassi"""
    
    def __init__(self, monitor: RealTimeMonitor):
        self.monitor = monitor
        self.logger = logging.getLogger(__name__)
    
    async def analyze_risk_exposure(self, period_hours: int = 24) -> Dict:
        """Risk exposure tahlili"""
        
        # Joriy risk summary
        risk_summary = await self.monitor.get_risk_summary()
        
        # Position risk analysis
        position_risks = await self._analyze_position_risks()
        
        # Correlation risk analysis
        correlation_risks = await self._analyze_correlation_risks()
        
        # Concentration risk
        concentration_risks = await self._analyze_concentration_risks()
        
        return {
            "risk_summary": risk_summary,
            "position_risks": position_risks,
            "correlation_risks": correlation_risks,
            "concentration_risks": concentration_risks,
            "recommendations": await self._generate_risk_recommendations(risk_summary, position_risks)
        }
    
    async def _analyze_position_risks(self) -> Dict:
        """Position risk tahlil"""
        positions = list(self.monitor.hedge_manager.positions.values())
        
        if not positions:
            return {"status": "no_positions"}
        
        # VaR by position
        position_vars = []
        total_exposure = sum(pos.notional_amount for pos in positions)
        
        for position in positions:
            # Simple VaR calculation (1.65 * volatility * sqrt(1/252) * position_value)
            volatility = position.performance_metrics.get("volatility", 0.15)
            position_var = 1.65 * volatility * np.sqrt(1/252) * position.notional_amount
            position_vars.append({
                "position_id": position.position_id,
                "pair": position.pair.value,
                "var_95": position_var,
                "var_percentage": position_var / position.notional_amount if position.notional_amount > 0 else 0,
                "exposure_percentage": position.notional_amount / total_exposure if total_exposure > 0 else 0
            })
        
        # Sort by VaR
        position_vars.sort(key=lambda x: x["var_95"], reverse=True)
        
        return {
            "total_positions": len(positions),
            "total_exposure": total_exposure,
            "position_var_analysis": position_vars[:10],  # Top 10 by VaR
            "avg_var_percentage": np.mean([pv["var_percentage"] for pv in position_vars])
        }
    
    async def _analyze_correlation_risks(self) -> Dict:
        """Korrelatsiya risk tahlil"""
        positions = list(self.monitor.hedge_manager.positions.values())
        
        if len(positions) < 2:
            return {"status": "insufficient_positions"}
        
        # Group by currency pairs
        pairs = [pos.pair.value for pos in positions]
        unique_pairs = list(set(pairs))
        
        correlation_matrix = {}
        for pair1 in unique_pairs:
            correlation_matrix[pair1] = {}
            for pair2 in unique_pairs:
                if pair1 == pair2:
                    correlation_matrix[pair1][pair2] = 1.0
                else:
                    # Use config correlation values
                    correlation_matrix[pair1][pair2] = config.correlation_matrix.get((pair1, pair2), 0.3)
        
        # Find high correlation pairs
        high_correlations = []
        for i, pair1 in enumerate(unique_pairs):
            for j, pair2 in enumerate(unique_pairs):
                if i < j and correlation_matrix[pair1][pair2] > 0.8:
                    high_correlations.append({
                        "pair1": pair1,
                        "pair2": pair2,
                        "correlation": correlation_matrix[pair1][pair2]
                    })
        
        return {
            "correlation_matrix": correlation_matrix,
            "high_correlations": high_correlations,
            "correlation_risk_score": len(high_correlations) / len(unique_pairs) if unique_pairs else 0
        }
    
    async def _analyze_concentration_risks(self) -> Dict:
        """Konsentatsiya risk tahlil"""
        positions = list(self.monitor.hedge_manager.positions.values())
        
        if not positions:
            return {"status": "no_positions"}
        
        total_exposure = sum(pos.notional_amount for pos in positions)
        
        # By currency pair
        pair_concentration = defaultdict(float)
        for position in positions:
            pair_concentration[position.pair.value] += position.notional_amount
        
        # By hedge type
        type_concentration = defaultdict(float)
        for position in positions:
            type_concentration[position.hedge_type.value] += position.notional_amount
        
        # Calculate percentages
        pair_percentages = {pair: exposure/total_exposure for pair, exposure in pair_concentration.items()}
        type_percentages = {hedge_type: exposure/total_exposure for hedge_type, exposure in type_concentration.items()}
        
        # Check for concentration violations
        pair_violations = [(pair, pct) for pair, pct in pair_percentages.items() if pct > 0.4]
        type_violations = [(hedge_type, pct) for hedge_type, pct in type_percentages.items() if pct > 0.5]
        
        return {
            "pair_concentration": pair_percentages,
            "type_concentration": type_percentages,
            "pair_concentration_violations": pair_violations,
            "type_concentration_violations": type_violations,
            "concentration_score": max(pair_percentages.values()) if pair_percentages else 0
        }
    
    async def _generate_risk_recommendations(
        self, 
        risk_summary: Dict, 
        position_risks: Dict
    ) -> List[str]:
        """Risk bo'yicha tavsiyalar"""
        recommendations = []
        
        # Critical alerts
        if risk_summary.get("critical_count", 0) > 0:
            recommendations.append("Kritik risklar mavjud - darhol choralar ko'rilishi zarur")
        
        # Position concentration
        concentration_score = position_risks.get("concentration_score", 0)
        if concentration_score > 0.4:
            recommendations.append(f"Pozitsiya konsentatsiyasi yuqori ({concentration_score:.1%}) - diversifikatsiya zarur")
        
        # VaR limits
        avg_var = position_risks.get("avg_var_percentage", 0)
        if avg_var > 0.05:
            recommendations.append(f"O'rtacha VaR juda yuqori ({avg_var:.1%}) - position hajmini kamaytiring")
        
        # Correlation risk
        if risk_summary.get("status") == "warning":
            recommendations.append("Korrelatsiya risklari - juftliklar o'rtasidagi bog'liqlik tekshirilsin")
        
        return recommendations

class AnalyticsEngine:
    """Asosiy analytics engine"""
    
    def __init__(self, monitor: RealTimeMonitor):
        self.monitor = monitor
        self.performance_analyzer = PerformanceAnalyzer(monitor)
        self.risk_analyzer = RiskAnalyzer(monitor)
        self.logger = logging.getLogger(__name__)
    
    async def generate_comprehensive_report(self, period_hours: int = 24) -> AnalyticsReport:
        """Comprehensive analytics report"""
        
        report_id = f"RPT_{int(time.time())}"
        period_end = int(time.time())
        period_start = period_end - (period_hours * 3600)
        
        # Performance analysis
        performance_data = await self.performance_analyzer.analyze_hedge_performance(period_hours)
        
        # Risk analysis
        risk_data = await self.risk_analyzer.analyze_risk_exposure(period_hours)
        
        # Generate insights
        insights = await self._generate_insights(performance_data, risk_data)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(performance_data, risk_data)
        
        report = AnalyticsReport(
            report_id=report_id,
            timestamp=int(time.time()),
            report_type="comprehensive",
            period_start=period_start,
            period_end=period_end,
            data={
                "performance": performance_data,
                "risk": risk_data
            },
            summary={
                "total_positions": len(self.monitor.hedge_manager.positions),
                "total_pnl": performance_data.get("period_summary", {}).get("period_return", 0),
                "risk_status": risk_data.get("risk_summary", {}).get("status", "unknown"),
                "alerts_count": risk_data.get("risk_summary", {}).get("total_alerts", 0)
            },
            insights=insights,
            recommendations=recommendations
        )
        
        return report
    
    async def _generate_insights(self, performance_data: Dict, risk_data: Dict) -> List[str]:
        """Insights yaratish"""
        insights = []
        
        # Performance insights
        period_summary = performance_data.get("period_summary", {})
        if period_summary.get("period_return", 0) > 0.05:
            insights.append(f"Yaxshi performance: {period_summary['period_return']:.2%} daromad")
        
        # Risk insights
        risk_summary = risk_data.get("risk_summary", {})
        if risk_summary.get("status") == "critical":
            insights.append("Kritik risk holati - attention zarur")
        elif risk_summary.get("status") == "warning":
            insights.append("Ogohlantirish risklari mavjud")
        
        # Strategy insights
        strategy_perf = performance_data.get("strategy_performance", {})
        if strategy_perf.get("quantum_enhanced_count", 0) > 0:
            insights.append("Quantum-enhanced strategiyalar faol")
        
        return insights
    
    async def _generate_recommendations(self, performance_data: Dict, risk_data: Dict) -> List[str]:
        """Tavsiyalar yaratish"""
        recommendations = risk_data.get("recommendations", [])
        
        # Strategy recommendations
        strategy_perf = performance_data.get("strategy_performance", {})
        best_strategy = strategy_perf.get("best_strategy")
        if best_strategy and best_strategy != "N/A":
            recommendations.append(f"Eng muvaffaqiyatli strategiya: {best_strategy}")
        
        # Quantum recommendations
        quantum_analysis = performance_data.get("quantum_analysis", {})
        quantum_advantage = quantum_analysis.get("quantum_advantage", 0)
        if quantum_advantage > 0.1:
            recommendations.append("Quantum optimallash sezilarli ustunlik ko'rsatdi")
        elif quantum_advantage < -0.1:
            recommendations.append("Classical strategiyalar afzalroq")
        
        return recommendations
    
    async def export_report(self, report: AnalyticsReport, filename: str = None) -> str:
        """Report ni export qilish"""
        if not filename:
            filename = f"analytics_report_{report.report_id}.json"
        
        report_data = asdict(report)
        
        return json.dumps(report_data, indent=2, default=str)
    
    async def create_performance_chart(self, report: AnalyticsReport) -> str:
        """Performance chart yaratish"""
        try:
            # Bu yerda real chart creation
            # Hozircha placeholder
            chart_filename = f"performance_chart_{report.report_id}.png"
            
            # Mock chart data
            plt.figure(figsize=(12, 8))
            plt.title(f"Forex Hedge Performance - {report.report_id}")
            plt.xlabel("Time")
            plt.ylabel("Return")
            plt.grid(True)
            
            # Save chart
            plt.savefig(chart_filename)
            plt.close()
            
            return chart_filename
            
        except Exception as e:
            self.logger.error(f"Chart creation error: {e}")
            return ""

class Dashboard:
    """Real-time dashboard"""
    
    def __init__(self, analytics_engine: AnalyticsEngine):
        self.analytics_engine = analytics_engine
        self.logger = logging.getLogger(__name__)
    
    async def get_dashboard_data(self) -> Dict:
        """Dashboard uchun ma'lumot"""
        
        # Live metrics
        live_metrics = await self.analytics_engine.monitor.get_live_metrics()
        
        # Recent analytics
        recent_report = await self.analytics_engine.generate_comprehensive_report(1)  # Last hour
        
        # Risk status
        risk_summary = await self.analytics_engine.monitor.get_risk_summary()
        
        return {
            "live_metrics": live_metrics,
            "recent_report": {
                "summary": recent_report.summary,
                "insights": recent_report.insights,
                "recommendations": recent_report.recommendations
            },
            "risk_status": risk_summary,
            "system_status": "operational",
            "last_updated": int(time.time())
        }
