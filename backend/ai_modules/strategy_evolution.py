#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Strategy Evolution Tracker
==========================

Strategy evolution tracking tizimi:
- Performance over time
- Parameter changes
- Market adaptation
- Risk evolution
- Return patterns
- Drawdown progression
- Sharpe ratio trends
- Volatility changes

Author: Orion Starline AI Team
Date: 2025-11-04
"""

import numpy as np
import pandas as pd
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EvolutionType(Enum):
    """Strategy evolution turi"""
    PERFORMANCE_DECLINE = "performance_decline"
    MARKET_ADAPTATION = "market_adaptation"
    PARAMETER_CHANGE = "parameter_change"
    RISK_ESCALATION = "risk_escalation"
    VOLATILITY_SHIFT = "volatility_shift"

class MarketRegime(Enum):
    """Market rejim turlari"""
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"

@dataclass
class StrategySnapshot:
    """Strategy holati snapshot"""
    timestamp: datetime
    strategy_id: str
    performance: float
    sharpe_ratio: float
    max_drawdown: float
    volatility: float
    win_rate: float
    parameters: Dict[str, Any]
    market_regime: MarketRegime
    risk_level: float

@dataclass
class EvolutionEvent:
    """Evolution voqeasi"""
    timestamp: datetime
    event_type: EvolutionType
    strategy_id: str
    severity: float  # 0-1
    description: str
    metrics_before: Dict[str, float]
    metrics_after: Dict[str, float]
    recommendations: List[str]

class StrategyEvolutionTracker:
    """Strategy evolution tracking asosiy klassi"""
    
    def __init__(self, db_path: str = "strategy_evolution.db"):
        self.db_path = db_path
        self.init_database()
        self.current_snapshots: Dict[str, StrategySnapshot] = {}
        self.evolution_history: List[EvolutionEvent] = []
        self.performance_thresholds = {
            'performance_decline': -0.05,  # 5% pasayish
            'sharpe_decline': -0.1,       # 10% Sharpe ratio pasayish
            'drawdown_threshold': 0.15,   # 15% max drawdown
            'volatility_spike': 0.05      # 5% volatility increase
        }
        
    def init_database(self):
        """Ma'lumotlar bazasini ishga tushirish"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Strategy snapshots jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                strategy_id TEXT NOT NULL,
                performance REAL NOT NULL,
                sharpe_ratio REAL NOT NULL,
                max_drawdown REAL NOT NULL,
                volatility REAL NOT NULL,
                win_rate REAL NOT NULL,
                parameters TEXT NOT NULL,
                market_regime TEXT NOT NULL,
                risk_level REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Evolution events jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evolution_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                strategy_id TEXT NOT NULL,
                severity REAL NOT NULL,
                description TEXT NOT NULL,
                metrics_before TEXT NOT NULL,
                metrics_after TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance metrics jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                strategy_id TEXT NOT NULL,
                daily_return REAL,
                cumulative_return REAL,
                rolling_sharpe REAL,
                rolling_volatility REAL,
                rolling_max_drawdown REAL,
                win_rate REAL,
                profit_factor REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi")
    
    def record_snapshot(self, snapshot: StrategySnapshot):
        """Strategy holatini saqlash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO strategy_snapshots 
            (timestamp, strategy_id, performance, sharpe_ratio, max_drawdown, 
             volatility, win_rate, parameters, market_regime, risk_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            snapshot.timestamp.isoformat(),
            snapshot.strategy_id,
            snapshot.performance,
            snapshot.sharpe_ratio,
            snapshot.max_drawdown,
            snapshot.volatility,
            snapshot.win_rate,
            json.dumps(snapshot.parameters),
            snapshot.market_regime.value,
            snapshot.risk_level
        ))
        
        conn.commit()
        conn.close()
        
        # Joriy snapshot ni yangilash
        self.current_snapshots[snapshot.strategy_id] = snapshot
        
        # Evolution voqealarini tekshirish
        self._check_evolution_events(snapshot)
        
        logger.info(f"Strategy {snapshot.strategy_id} snapshot saqlandi")
    
    def _check_evolution_events(self, current_snapshot: StrategySnapshot):
        """Evolution voqealarini aniqlash"""
        strategy_id = current_snapshot.strategy_id
        
        # Oldingi snapshot mavjudligini tekshirish
        if strategy_id not in self.current_snapshots:
            return
            
        previous_snapshot = self.current_snapshots[strategy_id]
        
        # Performance decline tekshirish
        if self._detect_performance_decline(previous_snapshot, current_snapshot):
            event = self._create_evolution_event(
                EvolutionType.PERFORMANCE_DECLINE,
                strategy_id,
                previous_snapshot,
                current_snapshot
            )
            self._record_evolution_event(event)
        
        # Market adaptation tekshirish
        if self._detect_market_adaptation(previous_snapshot, current_snapshot):
            event = self._create_evolution_event(
                EvolutionType.MARKET_ADAPTATION,
                strategy_id,
                previous_snapshot,
                current_snapshot
            )
            self._record_evolution_event(event)
        
        # Risk escalation tekshirish
        if self._detect_risk_escalation(previous_snapshot, current_snapshot):
            event = self._create_evolution_event(
                EvolutionType.RISK_ESCALATION,
                strategy_id,
                previous_snapshot,
                current_snapshot
            )
            self._record_evolution_event(event)
        
        # Volatility shift tekshirish
        if self._detect_volatility_shift(previous_snapshot, current_snapshot):
            event = self._create_evolution_event(
                EvolutionType.VOLATILITY_SHIFT,
                strategy_id,
                previous_snapshot,
                current_snapshot
            )
            self._record_evolution_event(event)
    
    def _detect_performance_decline(self, before: StrategySnapshot, after: StrategySnapshot) -> bool:
        """Performance pasayishini aniqlash"""
        return (after.performance - before.performance) < self.performance_thresholds['performance_decline']
    
    def _detect_market_adaptation(self, before: StrategySnapshot, after: StrategySnapshot) -> bool:
        """Market moslashuvini aniqlash"""
        # Market rejim o'zgargan va performance yaxshilangan
        regime_change = before.market_regime != after.market_regime
        performance_improvement = after.performance > before.performance
        return regime_change and performance_improvement
    
    def _detect_risk_escalation(self, before: StrategySnapshot, after: StrategySnapshot) -> bool:
        """Risk ko'payishini aniqlash"""
        risk_increase = after.risk_level > before.risk_level
        drawdown_increase = after.max_drawdown > before.max_drawdown
        return risk_increase and drawdown_increase
    
    def _detect_volatility_shift(self, before: StrategySnapshot, after: StrategySnapshot) -> bool:
        """Volatility o'zgarishini aniqlash"""
        volatility_change = abs(after.volatility - before.volatility)
        return volatility_change > self.performance_thresholds['volatility_spike']
    
    def _create_evolution_event(self, event_type: EvolutionType, strategy_id: str, 
                              before: StrategySnapshot, after: StrategySnapshot) -> EvolutionEvent:
        """Evolution voqeasi yaratish"""
        severity = self._calculate_severity(event_type, before, after)
        description = self._generate_description(event_type, before, after)
        recommendations = self._generate_recommendations(event_type, before, after)
        
        metrics_before = {
            'performance': before.performance,
            'sharpe_ratio': before.sharpe_ratio,
            'max_drawdown': before.max_drawdown,
            'volatility': before.volatility,
            'risk_level': before.risk_level
        }
        
        metrics_after = {
            'performance': after.performance,
            'sharpe_ratio': after.sharpe_ratio,
            'max_drawdown': after.max_drawdown,
            'volatility': after.volatility,
            'risk_level': after.risk_level
        }
        
        return EvolutionEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            strategy_id=strategy_id,
            severity=severity,
            description=description,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            recommendations=recommendations
        )
    
    def _calculate_severity(self, event_type: EvolutionType, before: StrategySnapshot, 
                          after: StrategySnapshot) -> float:
        """Voqeaning og'irligini hisoblash"""
        if event_type == EvolutionType.PERFORMANCE_DECLINE:
            return min(1.0, abs(after.performance - before.performance) / 0.2)
        elif event_type == EvolutionType.RISK_ESCALATION:
            return min(1.0, (after.max_drawdown - before.max_drawdown) / 0.2)
        elif event_type == EvolutionType.VOLATILITY_SHIFT:
            return min(1.0, abs(after.volatility - before.volatility) / 0.1)
        else:
            return 0.5
    
    def _generate_description(self, event_type: EvolutionType, before: StrategySnapshot, 
                            after: StrategySnapshot) -> str:
        """Voqeaning tavsifini yaratish"""
        if event_type == EvolutionType.PERFORMANCE_DECLINE:
            return f"Performance {before.performance:.2%} dan {after.performance:.2%} ga pasaydi"
        elif event_type == EvolutionType.MARKET_ADAPTATION:
            return f"Market rejim o'zgargan: {before.market_regime.value} dan {after.market_regime.value} ga"
        elif event_type == EvolutionType.RISK_ESCALATION:
            return f"Risk darajasi oshdi: {before.risk_level:.2f} dan {after.risk_level:.2f} ga"
        elif event_type == EvolutionType.VOLATILITY_SHIFT:
            return f"Volatility o'zgardi: {before.volatility:.2%} dan {after.volatility:.2%} ga"
        else:
            return f"Strategy evolution voqeasi: {event_type.value}"
    
    def _generate_recommendations(self, event_type: EvolutionType, before: StrategySnapshot, 
                                after: StrategySnapshot) -> List[str]:
        """Tavsiyalar yaratish"""
        recommendations = []
        
        if event_type == EvolutionType.PERFORMANCE_DECLINE:
            recommendations.extend([
                "Parameterlarni qayta ko'rib chiqish",
                "Risk darajasini kamaytirish",
                "Backtest natijalarini tahlil qilish"
            ])
        elif event_type == EvolutionType.RISK_ESCALATION:
            recommendations.extend([
                "Position sizing ni qayta ko'rib chiqish",
                "Stop-loss darajalarini sozlash",
                "Diversifikatsiyani oshirish"
            ])
        elif event_type == EvolutionType.VOLATILITY_SHIFT:
            recommendations.extend([
                "Volatility-based position sizing",
                "Dynamic hedging strategiyalari",
                "Market rejimiga mos parametrlar"
            ])
        
        return recommendations
    
    def _record_evolution_event(self, event: EvolutionEvent):
        """Evolution voqeasini saqlash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO evolution_events 
            (timestamp, event_type, strategy_id, severity, description, 
             metrics_before, metrics_after, recommendations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.timestamp.isoformat(),
            event.event_type.value,
            event.strategy_id,
            event.severity,
            event.description,
            json.dumps(event.metrics_before),
            json.dumps(event.metrics_after),
            json.dumps(event.recommendations)
        ))
        
        conn.commit()
        conn.close()
        
        self.evolution_history.append(event)
        logger.info(f"Evolution voqeasi qayd etildi: {event.event_type.value} - {event.strategy_id}")
    
    def get_evolution_analysis(self, strategy_id: str, days: int = 30) -> Dict[str, Any]:
        """Strategy evolution tahlili"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        
        # Snapshots ma'lumotlari
        snapshots_df = pd.read_sql_query('''
            SELECT * FROM strategy_snapshots 
            WHERE strategy_id = ? AND timestamp >= ?
            ORDER BY timestamp
        ''', conn, params=(strategy_id, start_date.isoformat()))
        
        # Evolution events
        events_df = pd.read_sql_query('''
            SELECT * FROM evolution_events 
            WHERE strategy_id = ? AND timestamp >= ?
            ORDER BY timestamp
        ''', conn, params=(strategy_id, start_date.isoformat()))
        
        conn.close()
        
        if snapshots_df.empty:
            return {"error": "Ma'lumot topilmadi"}
        
        # Performance evolution
        performance_trend = self._calculate_performance_trend(snapshots_df)
        risk_evolution = self._calculate_risk_evolution(snapshots_df)
        parameter_changes = self._analyze_parameter_changes(snapshots_df)
        market_adaptation = self._analyze_market_adaptation(snapshots_df)
        
        analysis = {
            'strategy_id': strategy_id,
            'analysis_period': f"{days} kun",
            'performance_trend': performance_trend,
            'risk_evolution': risk_evolution,
            'parameter_changes': parameter_changes,
            'market_adaptation': market_adaptation,
            'evolution_events': events_df.to_dict('records') if not events_df.empty else [],
            'overall_score': self._calculate_overall_score(snapshots_df, events_df)
        }
        
        return analysis
    
    def _calculate_performance_trend(self, snapshots_df: pd.DataFrame) -> Dict[str, Any]:
        """Performance trend tahlili"""
        performance = snapshots_df['performance'].values
        
        if len(performance) < 2:
            return {"trend": "insufficient_data", "slope": 0, "volatility": 0}
        
        # Linear trend
        x = np.arange(len(performance))
        slope = np.polyfit(x, performance, 1)[0]
        
        # Volatility
        volatility = np.std(performance)
        
        # Trend direction
        if slope > 0.001:
            trend = "improving"
        elif slope < -0.001:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "slope": slope,
            "volatility": volatility,
            "current_performance": performance[-1],
            "performance_range": {"min": np.min(performance), "max": np.max(performance)}
        }
    
    def _calculate_risk_evolution(self, snapshots_df: pd.DataFrame) -> Dict[str, Any]:
        """Risk evolution tahlili"""
        max_drawdowns = snapshots_df['max_drawdown'].values
        volatilities = snapshots_df['volatility'].values
        risk_levels = snapshots_df['risk_level'].values
        
        if len(max_drawdowns) < 2:
            return {"risk_trend": "insufficient_data", "current_risk": 0}
        
        # Risk trend
        risk_slope = np.polyfit(np.arange(len(risk_levels)), risk_levels, 1)[0]
        
        if risk_slope > 0.01:
            risk_trend = "increasing"
        elif risk_slope < -0.01:
            risk_trend = "decreasing"
        else:
            risk_trend = "stable"
        
        return {
            "risk_trend": risk_trend,
            "current_risk": risk_levels[-1],
            "current_max_drawdown": max_drawdowns[-1],
            "current_volatility": volatilities[-1],
            "risk_metrics": {
                "max_drawdown_trend": "increasing" if np.polyfit(np.arange(len(max_drawdowns)), max_drawdowns, 1)[0] > 0 else "decreasing",
                "volatility_trend": "increasing" if np.polyfit(np.arange(len(volatilities)), volatilities, 1)[0] > 0 else "decreasing"
            }
        }
    
    def _analyze_parameter_changes(self, snapshots_df: pd.DataFrame) -> Dict[str, Any]:
        """Parameter o'zgarishlarini tahlil qilish"""
        if snapshots_df.empty:
            return {"parameter_stability": "no_data"}
        
        # Parameters extraction
        parameters_list = []
        for _, row in snapshots_df.iterrows():
            try:
                params = json.loads(row['parameters'])
                parameters_list.append(params)
            except:
                continue
        
        if not parameters_list:
            return {"parameter_stability": "no_valid_data"}
        
        # Parameter stability analysis
        all_params = set()
        for params in parameters_list:
            all_params.update(params.keys())
        
        stability_scores = {}
        for param in all_params:
            param_values = [p.get(param, 0) for p in parameters_list if param in p]
            if len(param_values) > 1:
                # Coefficient of variation
                cv = np.std(param_values) / np.mean(param_values) if np.mean(param_values) != 0 else float('inf')
                stability_scores[param] = 1 / (1 + cv) if cv != float('inf') else 0
        
        # Overall stability
        if stability_scores:
            overall_stability = np.mean(list(stability_scores.values()))
            if overall_stability > 0.8:
                stability = "very_stable"
            elif overall_stability > 0.6:
                stability = "stable"
            elif overall_stability > 0.4:
                stability = "moderate"
            else:
                stability = "unstable"
        else:
            stability = "insufficient_data"
        
        return {
            "parameter_stability": stability,
            "stability_scores": stability_scores,
            "total_parameters": len(all_params)
        }
    
    def _analyze_market_adaptation(self, snapshots_df: pd.DataFrame) -> Dict[str, Any]:
        """Market moslashuvini tahlil qilish"""
        if snapshots_df.empty:
            return {"adaptation_score": 0, "regime_changes": 0}
        
        # Regime changes count
        regimes = snapshots_df['market_regime'].values
        regime_changes = sum(1 for i in range(1, len(regimes)) if regimes[i] != regimes[i-1])
        
        # Performance vs regime correlation
        performance = snapshots_df['performance'].values
        
        # Adaptation score based on performance stability across regime changes
        adaptation_score = 1.0
        if regime_changes > 0:
            # Calculate performance variance in different regimes
            regime_performance = {}
            for i, regime in enumerate(regimes):
                if regime not in regime_performance:
                    regime_performance[regime] = []
                regime_performance[regime].append(performance[i])
            
            # Cross-regime variance
            if len(regime_performance) > 1:
                regime_means = [np.mean(perfs) for perfs in regime_performance.values()]
                cross_regime_variance = np.var(regime_means)
                adaptation_score = 1 / (1 + cross_regime_variance)
        
        return {
            "adaptation_score": adaptation_score,
            "regime_changes": regime_changes,
            "unique_regimes": len(set(regimes)),
            "dominant_regime": max(set(regimes), key=regimes.tolist().count) if len(regimes) > 0 else "none"
        }
    
    def _calculate_overall_score(self, snapshots_df: pd.DataFrame, events_df: pd.DataFrame) -> Dict[str, Any]:
        """Umumiy evolution bahosi"""
        if snapshots_df.empty:
            return {"overall_score": 0, "grade": "N/A"}
        
        # Component scores
        performance_score = self._calculate_performance_trend(snapshots_df)
        risk_score = self._calculate_risk_evolution(snapshots_df)
        adaptation_score = self._analyze_market_adaptation(snapshots_df)
        
        # Evolution events impact
        if not events_df.empty:
            event_penalty = np.mean(events_df['severity'].values)
        else:
            event_penalty = 0
        
        # Overall score calculation
        performance_component = 1 if performance_score.get("trend") == "improving" else 0.5
        risk_component = 1 if risk_score.get("risk_trend") == "decreasing" else 0.5
        adaptation_component = adaptation_score.get("adaptation_score", 0)
        
        overall_score = (performance_component + risk_component + adaptation_component) / 3
        overall_score = max(0, overall_score - event_penalty * 0.3)
        
        # Grade assignment
        if overall_score >= 0.8:
            grade = "A"
        elif overall_score >= 0.6:
            grade = "B"
        elif overall_score >= 0.4:
            grade = "C"
        elif overall_score >= 0.2:
            grade = "D"
        else:
            grade = "F"
        
        return {
            "overall_score": overall_score,
            "grade": grade,
            "components": {
                "performance": performance_component,
                "risk": risk_component,
                "adaptation": adaptation_component
            }
        }
    
    def get_evolution_summary(self, days: int = 30) -> Dict[str, Any]:
        """Umumiy evolution xulosasi"""
        conn = sqlite3.connect(self.db_path)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # All strategies performance
        strategies_df = pd.read_sql_query('''
            SELECT strategy_id, COUNT(*) as snapshot_count,
                   AVG(performance) as avg_performance,
                   AVG(sharpe_ratio) as avg_sharpe,
                   AVG(max_drawdown) as avg_max_drawdown
            FROM strategy_snapshots 
            WHERE timestamp >= ?
            GROUP BY strategy_id
        ''', conn, params=(start_date.isoformat(),))
        
        # Evolution events summary
        events_df = pd.read_sql_query('''
            SELECT event_type, COUNT(*) as count, AVG(severity) as avg_severity
            FROM evolution_events 
            WHERE timestamp >= ?
            GROUP BY event_type
        ''', conn, params=(start_date.isoformat(),))
        
        conn.close()
        
        summary = {
            'analysis_period': f"{days} kun",
            'total_strategies': len(strategies_df),
            'strategies_performance': strategies_df.to_dict('records') if not strategies_df.empty else [],
            'evolution_events': events_df.to_dict('records') if not events_df.empty else [],
            'active_strategies': len(strategies_df[strategies_df['snapshot_count'] >= 5]) if not strategies_df.empty else 0,
            'top_performer': strategies_df.loc[strategies_df['avg_performance'].idxmax()]['strategy_id'] if not strategies_df.empty and len(strategies_df) > 0 else "N/A"
        }
        
        return summary

# Usage example
if __name__ == "__main__":
    # Initialize tracker
    tracker = StrategyEvolutionTracker()
    
    # Example strategy snapshots
    snapshot1 = StrategySnapshot(
        timestamp=datetime.now(),
        strategy_id="EURUSD_TREND_001",
        performance=0.15,
        sharpe_ratio=1.2,
        max_drawdown=0.08,
        volatility=0.12,
        win_rate=0.65,
        parameters={"ma_period": 20, "risk_per_trade": 0.02},
        market_regime=MarketRegime.BULL,
        risk_level=0.3
    )
    
    # Record snapshot
    tracker.record_snapshot(snapshot1)
    
    # Get evolution analysis
    analysis = tracker.get_evolution_analysis("EURUSD_TREND_001")
    print("Evolution Analysis:", json.dumps(analysis, indent=2, default=str))
    
    # Get summary
    summary = tracker.get_evolution_summary()
    print("Evolution Summary:", json.dumps(summary, indent=2, default=str))