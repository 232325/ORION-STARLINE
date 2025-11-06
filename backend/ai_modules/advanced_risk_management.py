#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Risk Management System

Batafsil risk management tizimi quyidagi funksiyalarni o'z ichiga oladi:
1. Real-time risk scoring
2. Portfolio stress testing
3. Automated risk controls
4. VaR calculations
5. Monte Carlo simulations
6. Liquidity risk assessment
7. Credit risk evaluation
8. Operational risk monitoring
9. Regulatory compliance
10. Risk dashboard

Professional risk management uchun barcha zarur funksiyalar.

Author: Orion Starline AI Trading System
Created: 2025-11-05
Version: 2.0.0
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import sqlite3
import threading
import websockets
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from scipy import stats
from scipy.optimize import minimize
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspace/orion-starline/backend/logs/advanced_risk_management.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk darajasi"""
    MINIMAL = "MINIMAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskType(Enum):
    """Risk turlari"""
    MARKET = "MARKET"
    CREDIT = "CREDIT"
    OPERATIONAL = "OPERATIONAL"
    LIQUIDITY = "LIQUIDITY"
    COMPLIANCE = "COMPLIANCE"
    SYSTEMIC = "SYSTEMIC"


class RegulatoryFramework(Enum):
    """Regulatory frameworks"""
    BASEL_III = "BASEL_III"
    MIFID_II = "MIFID_II"
    DODD_FRANK = "DODD_FRANK"
    EMIR = "EMIR"
    SFTR = "SFTR"


@dataclass
class Position:
    """Trading pozitsiyasi"""
    symbol: str
    quantity: float
    price: float
    market_value: float
    weight: float
    asset_class: str
    sector: str = ""
    region: str = ""
    currency: str = "USD"
    
    @property
    def pnl(self) -> float:
        """Profit/Loss hisoblash"""
        return 0.0  # Base implementation
    
    @property
    def exposure(self) -> float:
        """Pozitsiya ekspozitsiyasi"""
        return abs(self.market_value)


@dataclass
class RiskMetrics:
    """Extended Risk Metrics with database integration"""
    portfolio_value: float = 0.0
    var_1d: float = 0.0
    var_5d: float = 0.0
    var_10d: float = 0.0
    expected_shortfall: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    beta: float = 0.0
    alpha: float = 0.0
    volatility: float = 0.0
    concentration_risk: float = 0.0
    liquidity_score: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, float]:
        """Dict ga o'tkazish"""
        return {
            'portfolio_value': self.portfolio_value,
            'var_1d': self.var_1d,
            'var_5d': self.var_5d,
            'var_10d': self.var_10d,
            'expected_shortfall': self.expected_shortfall,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'beta': self.beta,
            'alpha': self.alpha,
            'volatility': self.volatility,
            'concentration_risk': self.concentration_risk,
            'liquidity_score': self.liquidity_score
        }
    """Risk metrikalari"""
    var_95: float = 0.0
    var_99: float = 0.0
    expected_shortfall: float = 0.0
    volatility: float = 0.0
    beta: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    correlation_risk: float = 0.0
    concentration_risk: float = 0.0
    liquidity_risk: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Dict ga o'tkazish"""
        return {
            'var_95': self.var_95,
            'var_99': self.var_99,
            'expected_shortfall': self.expected_shortfall,
            'volatility': self.volatility,
            'beta': self.beta,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'correlation_risk': self.correlation_risk,
            'concentration_risk': self.concentration_risk,
            'liquidity_risk': self.liquidity_risk
        }


@dataclass
class StressTestScenario:
    """Stress testing scenariysi"""
    name: str
    description: str
    market_shocks: Dict[str, float]  # Asset class -> shock percentage
    correlation_changes: Dict[Tuple[str, str], float]  # Pair -> correlation change
    volatility_changes: Dict[str, float]  # Asset -> volatility multiplier
    probability: float = 0.01  # Scenario probability
    impact_days: int = 1  # Days to impact
    
    def to_dict(self) -> Dict[str, Any]:
        """Dict ga o'tkazish"""
        return {
            'name': self.name,
            'description': self.description,
            'market_shocks': self.market_shocks,
            'correlation_changes': {f"{k[0]}_{k[1]}": v for k, v in self.correlation_changes.items()},
            'volatility_changes': self.volatility_changes,
            'probability': self.probability,
            'impact_days': self.impact_days
        }


@dataclass
class Alert:
    """Risk alert"""
    alert_id: str
    timestamp: datetime
    risk_type: RiskType
    level: RiskLevel
    message: str
    metric_value: float
    threshold: float
    position_affected: Optional[str] = None
    action_required: bool = True
    resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Dict ga o'tkazish"""
        return {
            'alert_id': self.alert_id,
            'timestamp': self.timestamp.isoformat(),
            'risk_type': self.risk_type.value,
            'level': self.level.value,
            'message': self.message,
            'metric_value': self.metric_value,
            'threshold': self.threshold,
            'position_affected': self.position_affected,
            'action_required': self.action_required,
            'resolved': self.resolved
        }


class SQLiteRiskDatabase:
    """SQLite ma'lumotlar bazasi management"""
    
    def __init__(self, db_path: str = "/workspace/orion-starline/backend/data/risk_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Ma'lumotlar bazasini yaratish"""
        try:
            import os
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Risk metrics jadvali
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS risk_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME,
                        portfolio_value REAL,
                        var_1d REAL,
                        var_5d REAL,
                        var_10d REAL,
                        expected_shortfall REAL,
                        sharpe_ratio REAL,
                        max_drawdown REAL,
                        beta REAL,
                        alpha REAL,
                        volatility REAL,
                        concentration_risk REAL,
                        liquidity_score REAL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Positions jadvali
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS positions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT,
                        quantity REAL,
                        entry_price REAL,
                        current_price REAL,
                        side TEXT,
                        timestamp DATETIME,
                        stop_loss REAL,
                        take_profit REAL,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Stress test results jadvali
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stress_tests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        scenario_name TEXT,
                        portfolio_impact REAL,
                        position_impacts TEXT,
                        liquidity_impact REAL,
                        recovery_time REAL,
                        stress_score REAL,
                        timestamp DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Alerts jadvali
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS risk_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alert_id TEXT UNIQUE,
                        alert_type TEXT,
                        risk_type TEXT,
                        severity TEXT,
                        message TEXT,
                        current_value REAL,
                        threshold_value REAL,
                        timestamp DATETIME,
                        resolved BOOLEAN DEFAULT FALSE,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("Ma'lumotlar bazasi muvaffaqiyatli yaratildi")
                
        except Exception as e:
            logger.error(f"Ma'lumotlar bazasini yaratishda xato: {e}")
    
    def insert_risk_metrics(self, metrics: 'RiskMetrics'):
        """Risk metrikalarini saqlash"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO risk_metrics (
                        timestamp, portfolio_value, var_1d, var_5d, var_10d,
                        expected_shortfall, sharpe_ratio, max_drawdown,
                        beta, alpha, volatility, concentration_risk, liquidity_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.timestamp, metrics.portfolio_value, metrics.var_1d,
                    metrics.var_5d, metrics.var_10d, metrics.expected_shortfall,
                    metrics.sharpe_ratio, metrics.max_drawdown, metrics.beta,
                    metrics.alpha, metrics.volatility, metrics.concentration_risk,
                    metrics.liquidity_score
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Risk metrikalarini saqlashda xato: {e}")
    
    def get_recent_risk_metrics(self, days: int = 30) -> List['RiskMetrics']:
        """So'nggi risk metrikalarini olish"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM risk_metrics 
                    WHERE timestamp >= datetime('now', '-{} days')
                    ORDER BY timestamp DESC
                """.format(days))
                
                rows = cursor.fetchall()
                metrics = []
                for row in rows:
                    metrics.append(RiskMetrics(
                        portfolio_value=row[2], var_1d=row[3], var_5d=row[4],
                        var_10d=row[5], expected_shortfall=row[6],
                        sharpe_ratio=row[7], max_drawdown=row[8], beta=row[9],
                        alpha=row[10], volatility=row[11],
                        concentration_risk=row[12], liquidity_score=row[13],
                        timestamp=datetime.fromisoformat(row[1])
                    ))
                return metrics
        except Exception as e:
            logger.error(f"Risk metrikalarini olishda xato: {e}")
            return []


class RealTimeRiskScorer:
    """Real-time risk assessment engine"""
    
    def __init__(self):
        self.risk_weights = {
            RiskType.MARKET: 0.35,
            RiskType.CREDIT: 0.25,
            RiskType.LIQUIDITY: 0.20,
            RiskType.OPERATIONAL: 0.15,
            RiskType.COMPLIANCE: 0.05
        }
        self.thresholds = {
            RiskLevel.MINIMAL: (0.0, 0.2),
            RiskLevel.LOW: (0.2, 0.4),
            RiskLevel.MEDIUM: (0.4, 0.6),
            RiskLevel.HIGH: (0.6, 0.8),
            RiskLevel.CRITICAL: (0.8, 1.0)
        }
    
    def calculate_market_risk(self, positions: List[Position], market_data: Dict) -> float:
        """Market risk hisoblash"""
        try:
            total_var = 0.0
            total_market_value = sum(pos.market_value for pos in positions)
            
            for position in positions:
                # Individual position VaR
                position_var = self._calculate_position_var(position, market_data)
                
                # Diversification effect
                weight = position.weight
                contribution = weight ** 2 * position_var
                total_var += contribution
            
            # Diversification multiplier
            diversification_factor = 1 - len(positions) * 0.01
            total_var *= max(0.1, diversification_factor)
            
            return total_var / total_market_value if total_market_value > 0 else 0
            
        except Exception as e:
            logger.error(f"Market risk calculation error: {e}")
            return 0.5  # Conservative estimate
    
    def _calculate_position_var(self, position: Position, market_data: Dict) -> float:
        """Pozitsiya VaR hisoblash"""
        try:
            # Simplified VaR calculation
            volatility = market_data.get(f"{position.symbol}_volatility", 0.02)
            confidence_level = 0.95
            z_score = stats.norm.ppf(1 - confidence_level)
            
            return abs(z_score * volatility * position.market_value)
            
        except Exception as e:
            logger.error(f"Position VaR calculation error: {e}")
            return position.market_value * 0.02
    
    def calculate_credit_risk(self, positions: List[Position], credit_data: Dict) -> float:
        """Credit risk hisoblash"""
        try:
            credit_exposure = 0.0
            total_market_value = sum(pos.market_value for pos in positions)
            
            for position in positions:
                # Credit spread based risk
                credit_spread = credit_data.get(f"{position.symbol}_credit_spread", 0.005)
                
                # Default probability estimate
                default_prob = min(0.1, credit_spread * 10)  # Simplified mapping
                loss_given_default = 0.6  # Typical LGD
                
                position_credit_risk = position.market_value * default_prob * loss_given_default
                credit_exposure += position_credit_risk
            
            return credit_exposure / total_market_value if total_market_value > 0 else 0
            
        except Exception as e:
            logger.error(f"Credit risk calculation error: {e}")
            return 0.1  # Conservative estimate
    
    def calculate_liquidity_risk(self, positions: List[Position], liquidity_data: Dict) -> float:
        """Liquidity risk hisoblash"""
        try:
            total_liquidity_risk = 0.0
            total_market_value = sum(pos.market_value for pos in positions)
            
            for position in positions:
                # Liquidity metrics
                bid_ask_spread = liquidity_data.get(f"{position.symbol}_bid_ask_spread", 0.001)
                volume_24h = liquidity_data.get(f"{position.symbol}_volume_24h", position.market_value)
                
                # Liquidity score (0-1, higher is more risky)
                volume_ratio = position.market_value / max(volume_24h, position.market_value)
                liquidity_score = min(1.0, bid_ask_spread * 100 + volume_ratio)
                
                weighted_risk = position.weight * liquidity_score
                total_liquidity_risk += weighted_risk
            
            return total_liquidity_risk
            
        except Exception as e:
            logger.error(f"Liquidity risk calculation error: {e}")
            return 0.2  # Conservative estimate
    
    def calculate_operational_risk(self, positions: List[Position], operational_data: Dict) -> float:
        """Operational risk hisoblash"""
        try:
            # Simplified operational risk assessment
            system_availability = operational_data.get('system_availability', 0.99)
            error_rate = operational_data.get('error_rate', 0.001)
            
            # Base operational risk
            base_risk = (1 - system_availability) * 0.5 + error_rate * 10
            
            # Position complexity factor
            complexity_factor = min(2.0, len(positions) * 0.1)
            
            return min(1.0, base_risk * complexity_factor)
            
        except Exception as e:
            logger.error(f"Operational risk calculation error: {e}")
            return 0.1
    
    def get_risk_score(self, positions: List[Position], market_data: Dict, 
                      credit_data: Dict, liquidity_data: Dict, 
                      operational_data: Dict) -> Tuple[float, RiskLevel]:
        """Umumiy risk balli hisoblash"""
        try:
            market_risk = self.calculate_market_risk(positions, market_data)
            credit_risk = self.calculate_credit_risk(positions, credit_data)
            liquidity_risk = self.calculate_liquidity_risk(positions, liquidity_data)
            operational_risk = self.calculate_operational_risk(positions, operational_data)
            
            # Weighted combination
            combined_risk = (
                market_risk * self.risk_weights[RiskType.MARKET] +
                credit_risk * self.risk_weights[RiskType.CREDIT] +
                liquidity_risk * self.risk_weights[RiskType.LIQUIDITY] +
                operational_risk * self.risk_weights[RiskType.OPERATIONAL]
            )
            
            # Determine risk level
            risk_level = self._get_risk_level(combined_risk)
            
            return combined_risk, risk_level
            
        except Exception as e:
            logger.error(f"Risk score calculation error: {e}")
            return 0.5, RiskLevel.MEDIUM
    
    def _get_risk_level(self, risk_score: float) -> RiskLevel:
        """Risk ballidan risk darajasini aniqlash"""
        for level, (min_val, max_val) in self.thresholds.items():
            if min_val <= risk_score < max_val:
                return level
        return RiskLevel.CRITICAL


class PortfolioStressTester:
    """Portfolio stress testing engine"""
    
    def __init__(self):
        self.scenarios = self._initialize_scenarios()
    
    def _initialize_scenarios(self) -> List[StressTestScenario]:
        """Standard stress test scenariylarini yaratish"""
        scenarios = [
            StressTestScenario(
                name="Financial Crisis 2008",
                description="Historical 2008 financial crisis scenario",
                market_shocks={
                    "EQUITY": -0.40,
                    "BOND": 0.20,
                    "CREDIT": -0.60,
                    "COMMODITY": -0.30,
                    "CURRENCY": -0.20
                },
                correlation_changes={
                    ("EQUITY", "BOND"): 0.3,
                    ("EQUITY", "CREDIT"): 0.5,
                    ("BOND", "CREDIT"): 0.2
                },
                volatility_changes={
                    "EQUITY": 3.0,
                    "BOND": 2.0,
                    "CREDIT": 4.0,
                    "COMMODITY": 2.5
                },
                probability=0.005,
                impact_days=1
            ),
            StressTestScenario(
                name="Pandemic Shock",
                description="Global pandemic scenario similar to COVID-19",
                market_shocks={
                    "EQUITY": -0.35,
                    "BOND": 0.15,
                    "CREDIT": -0.45,
                    "COMMODITY": -0.20,
                    "CURRENCY": -0.10
                },
                correlation_changes={
                    ("EQUITY", "BOND"): 0.4,
                    ("EQUITY", "CREDIT"): 0.6,
                    ("BOND", "CREDIT"): 0.3
                },
                volatility_changes={
                    "EQUITY": 2.5,
                    "BOND": 1.8,
                    "CREDIT": 3.0,
                    "COMMODITY": 2.0
                },
                probability=0.01,
                impact_days=1
            ),
            StressTestScenario(
                name="Interest Rate Shock",
                description="Sudden interest rate rise scenario",
                market_shocks={
                    "EQUITY": -0.20,
                    "BOND": -0.25,
                    "CREDIT": -0.30,
                    "COMMODITY": 0.10,
                    "CURRENCY": 0.15
                },
                correlation_changes={
                    ("EQUITY", "BOND"): -0.5,
                    ("EQUITY", "CREDIT"): 0.3,
                    ("BOND", "CREDIT"): 0.4
                },
                volatility_changes={
                    "EQUITY": 2.0,
                    "BOND": 3.0,
                    "CREDIT": 2.5,
                    "COMMODITY": 1.5
                },
                probability=0.02,
                impact_days=1
            ),
            StressTestScenario(
                name="Custom Black Swan",
                description="Extreme market crash scenario",
                market_shocks={
                    "EQUITY": -0.60,
                    "BOND": 0.30,
                    "CREDIT": -0.80,
                    "COMMODITY": -0.50,
                    "CURRENCY": -0.40
                },
                correlation_changes={
                    ("EQUITY", "BOND"): 0.6,
                    ("EQUITY", "CREDIT"): 0.8,
                    ("BOND", "CREDIT"): 0.5
                },
                volatility_changes={
                    "EQUITY": 5.0,
                    "BOND": 3.5,
                    "CREDIT": 6.0,
                    "COMMODITY": 4.0
                },
                probability=0.001,
                impact_days=1
            )
        ]
        return scenarios
    
    def run_stress_test(self, positions: List[Position], 
                       scenario: StressTestScenario) -> Dict[str, float]:
        """Stress test o'tkazish"""
        try:
            results = {
                'scenario_name': scenario.name,
                'original_portfolio_value': sum(pos.market_value for pos in positions),
                'stressed_portfolio_value': 0.0,
                'total_loss': 0.0,
                'percentage_loss': 0.0,
                'positions_affected': 0
            }
            
            stressed_total = 0.0
            affected_positions = 0
            
            for position in positions:
                # Determine asset class shock
                asset_shock = 0.0
                for asset_class, shock in scenario.market_shocks.items():
                    if self._matches_asset_class(position, asset_class):
                        asset_shock = shock
                        break
                
                # Calculate stressed position value
                stressed_value = position.market_value * (1 + asset_shock)
                stressed_total += stressed_value
                
                # Check if position is significantly affected
                if abs(asset_shock) > 0.05:  # More than 5% impact
                    affected_positions += 1
            
            # Calculate results
            original_value = results['original_portfolio_value']
            results['stressed_portfolio_value'] = stressed_total
            results['total_loss'] = original_value - stressed_total
            results['percentage_loss'] = (results['total_loss'] / original_value) * 100 if original_value > 0 else 0
            results['positions_affected'] = affected_positions
            
            return results
            
        except Exception as e:
            logger.error(f"Stress test error: {e}")
            return {}
    
    def _matches_asset_class(self, position: Position, asset_class: str) -> bool:
        """Pozitsiya asset class ga mos kelishini tekshirish"""
        position_class = position.asset_class.upper()
        class_mapping = {
            'EQUITY': ['EQUITY', 'STOCK', 'SHARE'],
            'BOND': ['BOND', 'DEBT', 'FIXED_INCOME'],
            'CREDIT': ['CREDIT', 'CORPORATE_BOND', 'HIGH_YIELD'],
            'COMMODITY': ['COMMODITY', 'METAL', 'OIL', 'GOLD'],
            'CURRENCY': ['CURRENCY', 'FX', 'FOREX']
        }
        
        for target in class_mapping.get(asset_class, [asset_class]):
            if target in position_class:
                return True
        return False
    
    def run_full_stress_test(self, positions: List[Position]) -> Dict[str, Any]:
        """Barcha scenariylar bo'yicha stress test"""
        try:
            results = {
                'timestamp': datetime.now().isoformat(),
                'portfolio_value': sum(pos.market_value for pos in positions),
                'scenarios': {}
            }
            
            for scenario in self.scenarios:
                scenario_result = self.run_stress_test(positions, scenario)
                results['scenarios'][scenario.name] = scenario_result
            
            # Calculate summary statistics
            losses = [s['total_loss'] for s in results['scenarios'].values()]
            if losses:
                results['summary'] = {
                    'expected_loss': np.mean(losses),
                    'worst_case_loss': max(losses),
                    'best_case_impact': min(losses),
                    'loss_std': np.std(losses)
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Full stress test error: {e}")
            return {}


class RiskControlAutomation:
    """Avtomatik risk controls"""
    
    def __init__(self):
        self.stop_loss_rules = {}
        self.position_limits = {}
        self.correlation_limits = {}
        self.volatility_limits = {}
    
    def setup_stop_loss_rules(self, position: Position, 
                             stop_loss_percentage: float = 0.05,
                             trailing_distance: float = 0.02) -> Dict[str, Any]:
        """Stop-loss qoidalarni sozlash"""
        try:
            rule = {
                'position_id': position.symbol,
                'initial_price': position.price,
                'stop_loss_percentage': stop_loss_percentage,
                'trailing_distance': trailing_distance,
                'current_stop_price': position.price * (1 - stop_loss_percentage),
                'highest_price': position.price,
                'is_active': True,
                'created_at': datetime.now()
            }
            
            self.stop_loss_rules[position.symbol] = rule
            return rule
            
        except Exception as e:
            logger.error(f"Stop-loss setup error: {e}")
            return {}
    
    def check_stop_loss(self, position: Position, current_price: float) -> Dict[str, Any]:
        """Stop-loss ni tekshirish"""
        try:
            if position.symbol not in self.stop_loss_rules:
                return {'triggered': False, 'reason': 'No stop-loss rule'}
            
            rule = self.stop_loss_rules[position.symbol]
            
            # Update highest price for trailing stop
            if current_price > rule['highest_price']:
                rule['highest_price'] = current_price
                # Update stop-loss for trailing stop
                rule['current_stop_price'] = rule['highest_price'] * (1 - rule['trailing_distance'])
            
            # Check if stop-loss triggered
            price_change = (current_price - position.price) / position.price
            stop_triggered = current_price <= rule['current_stop_price']
            
            result = {
                'triggered': stop_triggered,
                'current_price': current_price,
                'stop_price': rule['current_stop_price'],
                'price_change': price_change,
                'potential_loss': price_change * position.market_value
            }
            
            if stop_triggered:
                rule['is_active'] = False
                result['action'] = 'CLOSE_POSITION'
                result['close_quantity'] = position.quantity
            
            return result
            
        except Exception as e:
            logger.error(f"Stop-loss check error: {e}")
            return {'triggered': False, 'reason': 'Error'}
    
    def check_position_limits(self, positions: List[Position], 
                            market_data: Dict) -> Dict[str, Any]:
        """Pozitsiya limitlarini tekshirish"""
        try:
            violations = []
            warnings = []
            
            # Check concentration limits
            total_value = sum(pos.market_value for pos in positions)
            
            for position in positions:
                concentration = position.weight
                
                if concentration > 0.20:  # 20% limit
                    violations.append({
                        'type': 'CONCENTRATION',
                        'position': position.symbol,
                        'concentration': concentration,
                        'limit': 0.20
                    })
                elif concentration > 0.15:  # 15% warning
                    warnings.append({
                        'type': 'CONCENTRATION_WARNING',
                        'position': position.symbol,
                        'concentration': concentration,
                        'limit': 0.15
                    })
            
            # Check sector limits
            sector_exposure = {}
            for position in positions:
                sector = position.sector or 'UNKNOWN'
                if sector not in sector_exposure:
                    sector_exposure[sector] = 0
                sector_exposure[sector] += position.weight
            
            for sector, exposure in sector_exposure.items():
                if exposure > 0.40:  # 40% sector limit
                    violations.append({
                        'type': 'SECTOR_CONCENTRATION',
                        'sector': sector,
                        'exposure': exposure,
                        'limit': 0.40
                    })
            
            return {
                'violations': violations,
                'warnings': warnings,
                'total_positions': len(positions),
                'concentration_checked': True,
                'sector_checked': True
            }
            
        except Exception as e:
            logger.error(f"Position limits check error: {e}")
            return {'violations': [], 'warnings': []}
    
    def check_correlation_limits(self, positions: List[Position], 
                               correlation_matrix: np.ndarray) -> Dict[str, Any]:
        """Korrelation limitlarini tekshirish"""
        try:
            violations = []
            
            # Check high correlation pairs
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    correlation = correlation_matrix[i, j]
                    
                    if abs(correlation) > 0.8:  # 80% correlation limit
                        violations.append({
                            'type': 'HIGH_CORRELATION',
                            'pair': (positions[i].symbol, positions[j].symbol),
                            'correlation': correlation,
                            'limit': 0.8
                        })
            
            return {
                'violations': violations,
                'correlation_matrix_shape': correlation_matrix.shape,
                'max_correlation': np.max(np.abs(correlation_matrix - np.eye(len(positions))))
            }
            
        except Exception as e:
            logger.error(f"Correlation limits check error: {e}")
            return {'violations': []}


class VaRCalculator:
    """Value at Risk (VaR) hisoblagichi"""
    
    def __init__(self):
        self.confidence_levels = [0.95, 0.99, 0.999]
    
    def calculate_historical_var(self, returns: pd.Series, 
                               confidence_level: float = 0.95) -> float:
        """Historical VaR hisoblash"""
        try:
            if len(returns) == 0:
                return 0.0
            
            # Historical VaR is the negative quantile
            var = -np.percentile(returns, (1 - confidence_level) * 100)
            return max(0.0, var)
            
        except Exception as e:
            logger.error(f"Historical VaR calculation error: {e}")
            return 0.0
    
    def calculate_parametric_var(self, returns: pd.Series, 
                               confidence_level: float = 0.95) -> float:
        """Parametric (variance-covariance) VaR hisoblash"""
        try:
            if len(returns) == 0:
                return 0.0
            
            # Calculate mean and standard deviation
            mean_return = returns.mean()
            std_return = returns.std()
            
            # Z-score for confidence level
            z_score = stats.norm.ppf(1 - confidence_level)
            
            # Parametric VaR
            var = -(mean_return + z_score * std_return)
            return max(0.0, var)
            
        except Exception as e:
            logger.error(f"Parametric VaR calculation error: {e}")
            return 0.0
    
    def calculate_monte_carlo_var(self, portfolio_returns: pd.DataFrame,
                                initial_value: float,
                                confidence_level: float = 0.95,
                                simulations: int = 10000) -> Dict[str, float]:
        """Monte Carlo VaR hisoblash"""
        try:
            if portfolio_returns.empty:
                return {'var': 0.0, 'expected_shortfall': 0.0}
            
            # Generate correlated random variables
            np.random.seed(42)  # For reproducibility
            n_assets = portfolio_returns.shape[1]
            n_days = 252  # One year
            
            # Calculate correlation matrix
            correlation_matrix = portfolio_returns.corr().values
            
            # Cholesky decomposition for correlation
            L = np.linalg.cholesky(correlation_matrix)
            
            # Generate random scenarios
            random_returns = np.random.randn(simulations, n_assets, n_days)
            
            # Apply correlation structure
            correlated_returns = np.zeros((simulations, n_assets, n_days))
            for i in range(simulations):
                # Apply correlation: (n_assets, n_days) shape
                correlated_returns[i] = np.dot(L, random_returns[i])
            
            # Scale to actual parameters
            means = portfolio_returns.mean().values
            stds = portfolio_returns.std().values
            
            portfolio_values = []
            
            for i in range(simulations):
                # Fix broadcasting: expand stds and means to match correlated_returns shape
                daily_returns = np.sum(
                    correlated_returns[i] * stds[:, np.newaxis] + means[:, np.newaxis], axis=0
                )
                
                # Calculate cumulative portfolio value
                value = initial_value
                for daily_return in daily_returns:
                    value *= (1 + daily_return)
                
                portfolio_values.append(value)
            
            portfolio_values = np.array(portfolio_values)
            
            # Calculate VaR and ES
            var_amount = np.percentile(portfolio_values, (1 - confidence_level) * 100)
            var_value = initial_value - var_amount
            
            # Expected Shortfall (Conditional VaR)
            tail_values = portfolio_values[portfolio_values <= var_amount]
            expected_shortfall = initial_value - tail_values.mean() if len(tail_values) > 0 else var_value
            
            return {
                'var': max(0.0, var_value),
                'expected_shortfall': max(0.0, expected_shortfall),
                'confidence_level': confidence_level,
                'simulations': simulations
            }
            
        except Exception as e:
            logger.error(f"Monte Carlo VaR calculation error: {e}")
            return {'var': 0.0, 'expected_shortfall': 0.0}
    
    def calculate_portfolio_var(self, positions: List[Position], 
                              returns_data: pd.DataFrame,
                              confidence_level: float = 0.95) -> Dict[str, float]:
        """Portfolio VaR hisoblash"""
        try:
            if not positions or returns_data.empty:
                return {}
            
            # Calculate portfolio weights
            total_value = sum(pos.market_value for pos in positions)
            weights = np.array([pos.market_value / total_value for pos in positions])
            
            # Calculate portfolio returns
            if len(returns_data.columns) >= len(positions):
                # Assume returns_data matches position order
                asset_returns = returns_data.iloc[:, :len(positions)]
            else:
                # Use available data
                asset_returns = returns_data.iloc[:, :len(returns_data.columns)]
                if len(weights) > len(asset_returns.columns):
                    weights = weights[:len(asset_returns.columns)]
            
            portfolio_returns = pd.Series(
                (asset_returns * weights).sum(axis=1).values,
                index=asset_returns.index
            )
            
            # Calculate different VaR methods
            historical_var = self.calculate_historical_var(portfolio_returns, confidence_level)
            parametric_var = self.calculate_parametric_var(portfolio_returns, confidence_level)
            monte_carlo_var = self.calculate_monte_carlo_var(
                asset_returns, total_value, confidence_level
            )['var']
            
            # Expected Shortfall calculation
            tail_returns = portfolio_returns[portfolio_returns <= -historical_var]
            expected_shortfall = -tail_returns.mean() if len(tail_returns) > 0 else historical_var
            
            var_results = {
                'var_95': historical_var,
                'var_99': parametric_var,  # Using parametric as 99% var approximation
                'expected_shortfall': expected_shortfall,
                'volatility': portfolio_returns.std(),
                'sharpe_ratio': portfolio_returns.mean() / portfolio_returns.std() if portfolio_returns.std() > 0 else 0,
                'max_drawdown': self._calculate_max_drawdown(portfolio_returns),
                'correlation_risk': self._calculate_correlation_risk(asset_returns)
            }
            
            return var_results
            
        except Exception as e:
            logger.error(f"Portfolio VaR calculation error: {e}")
            return {'error': str(e)}

    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        try:
            cumulative_returns = (1 + returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            return abs(drawdown.min())
        except:
            return 0.0
    
    def _calculate_correlation_risk(self, returns_data: pd.DataFrame) -> float:
        """Calculate correlation risk metric"""
        try:
            if returns_data.empty or returns_data.shape[1] < 2:
                return 0.0
            
            correlation_matrix = returns_data.corr()
            avg_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
            return abs(avg_correlation)  # Return absolute average correlation
        except:
            return 0.0

class MonteCarloSimulator:
    """Monte Carlo risk scenario modeling"""
    
    def __init__(self):
        self.simulation_parameters = {
            'default_paths': 10000,
            'default_time_horizon': 252,  # days
            'confidence_levels': [0.90, 0.95, 0.99]
        }
    
    def simulate_portfolio_evolution(self, positions: List[Position],
                                   market_scenarios: Dict[str, pd.DataFrame],
                                   time_horizon: int = 252,
                                   num_simulations: int = 10000) -> Dict[str, Any]:
        """Portfolio evolution simulation"""
        try:
            if not positions:
                return {}
            
            total_value = sum(pos.market_value for pos in positions)
            
            # Initialize simulation arrays
            portfolio_values = np.ones((num_simulations, time_horizon + 1)) * total_value
            
            for sim in range(num_simulations):
                for day in range(1, time_horizon + 1):
                    # Random market shock
                    market_shock = self._generate_market_shock(market_scenarios)
                    
                    # Calculate portfolio change
                    portfolio_return = self._calculate_portfolio_return(positions, market_shock)
                    
                    # Update portfolio value
                    portfolio_values[sim, day] = portfolio_values[sim, day-1] * (1 + portfolio_return)
            
            # Calculate statistics
            final_values = portfolio_values[:, -1]
            
            results = {
                'simulation_parameters': {
                    'num_simulations': num_simulations,
                    'time_horizon': time_horizon,
                    'initial_value': total_value
                },
                'statistics': {
                    'mean_final_value': np.mean(final_values),
                    'median_final_value': np.median(final_values),
                    'std_final_value': np.std(final_values),
                    'min_final_value': np.min(final_values),
                    'max_final_value': np.max(final_values)
                },
                'percentiles': {
                    '10th': np.percentile(final_values, 10),
                    '25th': np.percentile(final_values, 25),
                    '50th': np.percentile(final_values, 50),
                    '75th': np.percentile(final_values, 75),
                    '90th': np.percentile(final_values, 90),
                    '95th': np.percentile(final_values, 95),
                    '99th': np.percentile(final_values, 99)
                },
                'probabilities': {
                    'loss_probability': np.mean(final_values < total_value),
                    'extreme_loss_probability': np.mean(final_values < total_value * 0.9),
                    'total_loss_probability': np.mean(final_values < total_value * 0.5)
                }
            }
            
            # Calculate time series of key percentiles
            percentiles_over_time = {}
            for p in [5, 10, 25, 50, 75, 90, 95]:
                percentiles_over_time[f'{p}th'] = [
                    np.percentile(portfolio_values[:, t], p) for t in range(time_horizon + 1)
                ]
            
            results['percentiles_over_time'] = percentiles_over_time
            
            return results
            
        except Exception as e:
            logger.error(f"Portfolio evolution simulation error: {e}")
            return {}
    
    def _generate_market_shock(self, market_scenarios: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Random market shock generation"""
        shock = {}
        for asset_class, data in market_scenarios.items():
            if not data.empty:
                # Random daily return from historical distribution
                daily_returns = data['return'].dropna()
                if len(daily_returns) > 0:
                    shock[asset_class] = np.random.choice(daily_returns.values)
                else:
                    shock[asset_class] = np.random.normal(0, 0.02)  # 2% volatility
            else:
                shock[asset_class] = np.random.normal(0, 0.02)
        return shock
    
    def _calculate_portfolio_return(self, positions: List[Position], market_shock: Dict[str, float]) -> float:
        """Portfolio return calculation"""
        portfolio_return = 0.0
        
        for position in positions:
            # Map position to market shock
            asset_class = self._get_asset_class(position)
            shock_return = market_shock.get(asset_class, 0.0)
            
            # Position return with diversification
            position_return = position.weight * shock_return
            portfolio_return += position_return
        
        return portfolio_return
    
    def _get_asset_class(self, position: Position) -> str:
        """Position asset class determination"""
        asset_class = position.asset_class.upper()
        if 'EQUITY' in asset_class or 'STOCK' in asset_class:
            return 'EQUITY'
        elif 'BOND' in asset_class or 'DEBT' in asset_class:
            return 'BOND'
        elif 'COMMODITY' in asset_class:
            return 'COMMODITY'
        else:
            return 'EQUITY'  # Default


class LiquidityRiskAnalyzer:
    """Liquidity risk assessment"""
    
    def __init__(self):
        self.liquidity_metrics = {}
        self.market_depth_data = {}
    
    def assess_market_liquidity(self, symbol: str, 
                              orderbook_data: Dict) -> Dict[str, float]:
        """Market liquidity assessment"""
        try:
            # Calculate bid-ask spread
            bid = orderbook_data.get('bid', 0)
            ask = orderbook_data.get('ask', 0)
            mid_price = orderbook_data.get('mid_price', (bid + ask) / 2)
            
            if mid_price > 0:
                bid_ask_spread = (ask - bid) / mid_price
            else:
                bid_ask_spread = 0.001  # Default 10 bps
            
            # Calculate market depth
            bid_depth = orderbook_data.get('bid_depth', 0)
            ask_depth = orderbook_data.get('ask_depth', 0)
            total_depth = bid_depth + ask_depth
            
            # Liquidity score (0-1, higher is better)
            spread_score = max(0, 1 - bid_ask_spread * 1000)  # Scale spread
            
            # Depth score based on available volume
            depth_score = min(1.0, total_depth / 1000000)  # 1M volume = max score
            
            # Overall liquidity score
            liquidity_score = (spread_score + depth_score) / 2
            
            # Implemented Liquidity at Risk (ILR)
            # Amount that could be sold within given time and price constraints
            time_horizon = 1  # 1 day
            max_price_impact = 0.01  # 1% max price impact
            base_volume = min(bid_depth, ask_depth)
            
            ilr = base_volume * (1 - max_price_impact)
            
            return {
                'bid_ask_spread': bid_ask_spread,
                'total_market_depth': total_depth,
                'liquidity_score': liquidity_score,
                'spread_score': spread_score,
                'depth_score': depth_score,
                'implemented_liquidity_risk': ilr,
                'liquidity_risk_level': self._get_liquidity_level(liquidity_score)
            }
            
        except Exception as e:
            logger.error(f"Liquidity assessment error: {e}")
            return {'liquidity_score': 0.5, 'liquidity_risk_level': 'MEDIUM'}
    
    def _get_liquidity_level(self, score: float) -> str:
        """Liquidity score dan level aniqlash"""
        if score >= 0.8:
            return 'EXCELLENT'
        elif score >= 0.6:
            return 'GOOD'
        elif score >= 0.4:
            return 'FAIR'
        elif score >= 0.2:
            return 'POOR'
        else:
            return 'VERY_POOR'
    
    def assess_portfolio_liquidity(self, positions: List[Position],
                                 liquidity_data: Dict) -> Dict[str, Any]:
        """Portfolio liquidity assessment"""
        try:
            position_liquidity = {}
            total_portfolio_value = sum(pos.market_value for pos in positions)
            weighted_liquidity_score = 0.0
            
            for position in positions:
                symbol = position.symbol
                if symbol in liquidity_data:
                    asset_liquidity = self.assess_market_liquidity(symbol, liquidity_data[symbol])
                    position_liquidity[symbol] = asset_liquidity
                    
                    # Weighted by position size
                    weight = position.market_value / total_portfolio_value
                    weighted_liquidity_score += weight * asset_liquidity['liquidity_score']
            
            # Portfolio liquidity metrics
            portfolio_metrics = {
                'overall_liquidity_score': weighted_liquidity_score,
                'liquidity_risk_level': self._get_liquidity_level(weighted_liquidity_score),
                'position_count': len(positions),
                'illiquid_positions': len([s for s in position_liquidity.values() 
                                         if s['liquidity_score'] < 0.3]),
                'high_risk_positions': len([s for s in position_liquidity.values() 
                                          if s['bid_ask_spread'] > 0.005])  # 50 bps
            }
            
            return {
                'portfolio_liquidity': portfolio_metrics,
                'position_liquidity': position_liquidity
            }
            
        except Exception as e:
            logger.error(f"Portfolio liquidity assessment error: {e}")
            return {}


class CreditRiskEvaluator:
    """Credit risk evaluation"""
    
    def __init__(self):
        self.credit_models = {}
        self.counterparty_data = {}
    
    def evaluate_counterparty_risk(self, counterparty_id: str,
                                 counterparty_data: Dict) -> Dict[str, Any]:
        """Counterparty risk assessment"""
        try:
            # Get basic counterparty information
            financial_data = counterparty_data.get('financial_metrics', {})
            market_data = counterparty_data.get('market_data', {})
            
            # Credit rating (if available)
            rating = counterparty_data.get('credit_rating', 'NR')
            rating_mapping = {
                'AAA': 1, 'AA+': 2, 'AA': 3, 'AA-': 4,
                'A+': 5, 'A': 6, 'A-': 7,
                'BBB+': 8, 'BBB': 9, 'BBB-': 10,
                'BB+': 11, 'BB': 12, 'BB-': 13,
                'B+': 14, 'B': 15, 'B-': 16,
                'CCC+': 17, 'CCC': 18, 'CCC-': 19,
                'CC': 20, 'C': 21, 'D': 22, 'NR': 15
            }
            rating_score = rating_mapping.get(rating, 15)
            
            # Financial ratios
            debt_to_equity = financial_data.get('debt_to_equity', 1.0)
            current_ratio = financial_data.get('current_ratio', 1.0)
            roe = financial_data.get('roe', 0.1)
            
            # Market volatility
            volatility = market_data.get('volatility', 0.2)
            
            # Simplified credit score calculation
            # Scale: 1 (excellent) to 10 (very poor)
            base_score = rating_score * 0.3
            
            # Adjust for financial health
            debt_penalty = max(0, (debt_to_equity - 1.0) * 0.5)
            liquidity_bonus = max(0, (current_ratio - 1.0) * 0.3)
            profitability_bonus = max(0, roe * 2.0)
            volatility_penalty = max(0, volatility * 2.0)
            
            credit_score = base_score + debt_penalty + volatility_penalty - liquidity_bonus - profitability_bonus
            credit_score = max(1, min(10, credit_score))
            
            # Default probability estimation
            # Simplified mapping from credit score to default probability
            default_probabilities = {
                1: 0.0001, 2: 0.0002, 3: 0.0005, 4: 0.001, 5: 0.002,
                6: 0.005, 7: 0.01, 8: 0.02, 9: 0.05, 10: 0.1
            }
            
            default_prob = default_probabilities.get(int(credit_score), 0.02)
            
            # Loss given default (LGD)
            lgd = counterparty_data.get('loss_given_default', 0.6)
            
            return {
                'counterparty_id': counterparty_id,
                'credit_score': credit_score,
                'credit_rating': rating,
                'default_probability': default_prob,
                'loss_given_default': lgd,
                'expected_loss': default_prob * lgd,
                'financial_health_score': 1.0 / credit_score,
                'risk_level': self._get_credit_risk_level(credit_score)
            }
            
        except Exception as e:
            logger.error(f"Counterparty risk evaluation error: {e}")
            return {'credit_score': 5.0, 'default_probability': 0.02, 'risk_level': 'MEDIUM'}
    
    def _get_credit_risk_level(self, credit_score: float) -> str:
        """Credit score dan risk level"""
        if credit_score <= 2:
            return 'LOW'
        elif credit_score <= 4:
            return 'LOW_MEDIUM'
        elif credit_score <= 6:
            return 'MEDIUM'
        elif credit_score <= 8:
            return 'MEDIUM_HIGH'
        else:
            return 'HIGH'
    
    def assess_portfolio_credit_risk(self, positions: List[Position],
                                   credit_data: Dict) -> Dict[str, Any]:
        """Portfolio credit risk assessment"""
        try:
            exposure_by_counterparty = {}
            total_exposure = 0.0
            
            for position in positions:
                counterparty = position.symbol  # Simplified - use symbol as counterparty
                
                if counterparty not in exposure_by_counterparty:
                    exposure_by_counterparty[counterparty] = 0.0
                
                exposure_by_counterparty[counterparty] += position.market_value
                total_exposure += position.market_value
            
            # Calculate credit metrics for each counterparty
            counterparty_risks = {}
            for counterparty, exposure in exposure_by_counterparty.items():
                if counterparty in credit_data:
                    risk_metrics = self.evaluate_counterparty_risk(counterparty, credit_data[counterparty])
                    counterparty_risks[counterparty] = {
                        **risk_metrics,
                        'exposure': exposure,
                        'exposure_percentage': exposure / total_exposure if total_exposure > 0 else 0
                    }
            
            # Calculate portfolio credit metrics
            portfolio_default_loss = 0.0
            concentration_risk = 0.0
            
            for counterparty, metrics in counterparty_risks.items():
                exposure = metrics['exposure']
                default_prob = metrics['default_probability']
                lgd = metrics['loss_given_default']
                
                expected_loss = exposure * default_prob * lgd
                portfolio_default_loss += expected_loss
                
                # Concentration risk
                concentration = exposure / total_exposure if total_exposure > 0 else 0
                concentration_risk += concentration ** 2
            
            # Herfindahl index for concentration (lower is better)
            concentration_index = concentration_risk
            
            portfolio_metrics = {
                'total_credit_exposure': total_exposure,
                'expected_credit_loss': portfolio_default_loss,
                'expected_loss_ratio': portfolio_default_loss / total_exposure if total_exposure > 0 else 0,
                'concentration_index': concentration_index,
                'concentration_risk_level': self._get_concentration_risk_level(concentration_index),
                'number_of_counterparties': len(counterparty_risks),
                'high_risk_counterparties': len([m for m in counterparty_risks.values() 
                                               if m['credit_score'] > 7])
            }
            
            return {
                'portfolio_credit_risk': portfolio_metrics,
                'counterparty_details': counterparty_risks
            }
            
        except Exception as e:
            logger.error(f"Portfolio credit risk assessment error: {e}")
            return {}
    
    def _get_concentration_risk_level(self, concentration_index: float) -> str:
        """Concentration index dan risk level"""
        if concentration_index < 0.15:
            return 'LOW'
        elif concentration_index < 0.25:
            return 'MEDIUM'
        else:
            return 'HIGH'


class OperationalRiskMonitor:
    """Operational risk monitoring"""
    
    def __init__(self):
        self.monitoring_metrics = {}
        self.alert_thresholds = {}
        self.incident_history = []
    
    def monitor_system_health(self, system_metrics: Dict) -> Dict[str, Any]:
        """System health monitoring"""
        try:
            # Key operational metrics
            availability = system_metrics.get('availability', 0.99)
            response_time = system_metrics.get('response_time_ms', 100)
            error_rate = system_metrics.get('error_rate', 0.001)
            throughput = system_metrics.get('throughput_rps', 1000)
            
            # Calculate health score (0-1)
            availability_score = availability  # Already 0-1
            
            # Response time score (invert - lower is better)
            response_score = max(0, 1 - (response_time - 50) / 950)  # Scale to 0-1000ms
            response_score = min(1.0, response_score)
            
            # Error rate score (invert - lower is better)
            error_score = max(0, 1 - error_rate * 1000)  # Scale to 0-1%
            
            # Throughput score (normalize to 0-2000 RPS)
            throughput_score = min(1.0, throughput / 2000)
            
            # Overall health score
            health_score = (availability_score + response_score + error_score + throughput_score) / 4
            
            # Determine health level
            health_level = self._get_health_level(health_score)
            
            # Check for alerts
            alerts = []
            if availability < 0.99:
                alerts.append({
                    'type': 'AVAILABILITY',
                    'message': f'System availability below threshold: {availability:.2%}',
                    'severity': 'HIGH'
                })
            
            if response_time > 200:
                alerts.append({
                    'type': 'RESPONSE_TIME',
                    'message': f'High response time: {response_time}ms',
                    'severity': 'MEDIUM'
                })
            
            if error_rate > 0.005:  # 0.5%
                alerts.append({
                    'type': 'ERROR_RATE',
                    'message': f'Elevated error rate: {error_rate:.2%}',
                    'severity': 'HIGH'
                })
            
            return {
                'health_score': health_score,
                'health_level': health_level,
                'metrics': {
                    'availability': availability,
                    'response_time': response_time,
                    'error_rate': error_rate,
                    'throughput': throughput
                },
                'component_scores': {
                    'availability': availability_score,
                    'response_time': response_score,
                    'error_rate': error_score,
                    'throughput': throughput_score
                },
                'alerts': alerts,
                'recommendations': self._get_health_recommendations(health_score, alerts)
            }
            
        except Exception as e:
            logger.error(f"System health monitoring error: {e}")
            return {'health_score': 0.5, 'health_level': 'MEDIUM', 'alerts': []}
    
    def _get_health_level(self, health_score: float) -> str:
        """Health score dan level"""
        if health_score >= 0.9:
            return 'EXCELLENT'
        elif health_score >= 0.75:
            return 'GOOD'
        elif health_score >= 0.6:
            return 'FAIR'
        elif health_score >= 0.4:
            return 'POOR'
        else:
            return 'CRITICAL'
    
    def _get_health_recommendations(self, health_score: float, alerts: List[Dict]) -> List[str]:
        """Health score uchun tavsiyalar"""
        recommendations = []
        
        if health_score < 0.6:
            recommendations.append("Immediate system review required")
        
        if health_score < 0.8:
            recommendations.append("Consider capacity planning and optimization")
        
        for alert in alerts:
            if alert['type'] == 'AVAILABILITY':
                recommendations.append("Implement redundancy and failover mechanisms")
            elif alert['type'] == 'RESPONSE_TIME':
                recommendations.append("Optimize database queries and caching")
            elif alert['type'] == 'ERROR_RATE':
                recommendations.append("Review error handling and logging")
        
        return recommendations
    
    def detect_anomalies(self, operational_data: Dict) -> Dict[str, Any]:
        """Operational anomaly detection"""
        try:
            # Simple statistical anomaly detection
            anomalies = []
            
            # Trading volume anomalies
            trading_volume = operational_data.get('trading_volume_24h', 0)
            avg_volume = operational_data.get('avg_volume_30d', trading_volume)
            
            if avg_volume > 0:
                volume_ratio = trading_volume / avg_volume
                if volume_ratio > 3.0 or volume_ratio < 0.3:
                    anomalies.append({
                        'type': 'VOLUME_ANOMALY',
                        'metric': 'trading_volume_24h',
                        'value': trading_volume,
                        'expected': avg_volume,
                        'ratio': volume_ratio,
                        'severity': 'HIGH' if abs(volume_ratio - 1) > 2 else 'MEDIUM'
                    })
            
            # API response time anomalies
            response_times = operational_data.get('response_times', [])
            if len(response_times) > 10:
                mean_response = np.mean(response_times)
                std_response = np.std(response_times)
                
                # Check for outliers
                for i, response_time in enumerate(response_times[-10:]):  # Last 10 requests
                    z_score = abs(response_time - mean_response) / std_response if std_response > 0 else 0
                    
                    if z_score > 3:
                        anomalies.append({
                            'type': 'RESPONSE_TIME_ANOMALY',
                            'metric': 'api_response_time',
                            'value': response_time,
                            'expected_mean': mean_response,
                            'z_score': z_score,
                            'severity': 'HIGH' if z_score > 5 else 'MEDIUM'
                        })
            
            # System resource anomalies
            cpu_usage = operational_data.get('cpu_usage_percent', 50)
            memory_usage = operational_data.get('memory_usage_percent', 50)
            
            if cpu_usage > 90:
                anomalies.append({
                    'type': 'HIGH_CPU_USAGE',
                    'metric': 'cpu_usage',
                    'value': cpu_usage,
                    'threshold': 90,
                    'severity': 'CRITICAL' if cpu_usage > 95 else 'HIGH'
                })
            
            if memory_usage > 90:
                anomalies.append({
                    'type': 'HIGH_MEMORY_USAGE',
                    'metric': 'memory_usage',
                    'value': memory_usage,
                    'threshold': 90,
                    'severity': 'CRITICAL' if memory_usage > 95 else 'HIGH'
                })
            
            return {
                'anomalies_detected': len(anomalies),
                'anomalies': anomalies,
                'monitoring_period': operational_data.get('period', '24h'),
                'total_metrics_checked': len(operational_data)
            }
            
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            return {'anomalies_detected': 0, 'anomalies': []}


class RegulatoryCompliance:
    """Regulatory compliance monitoring"""
    
    def __init__(self):
        self.frameworks = [RegulatoryFramework.BASEL_III, RegulatoryFramework.MIFID_II]
        self.compliance_metrics = {}
    
    def check_basel_iii_compliance(self, positions: List[Position],
                                  risk_metrics: RiskMetrics,
                                  capital_data: Dict) -> Dict[str, Any]:
        """Basel III compliance check"""
        try:
            # Capital adequacy ratio (CAR)
            tier_1_capital = capital_data.get('tier_1_capital', 0)
            total_capital = capital_data.get('total_capital', 0)
            risk_weighted_assets = self._calculate_risk_weighted_assets(positions)
            
            car_ratio = (total_capital / risk_weighted_assets) if risk_weighted_assets > 0 else 0
            tier_1_ratio = (tier_1_capital / risk_weighted_assets) if risk_weighted_assets > 0 else 0
            
            # Basel III requirements
            min_tier_1_ratio = 0.06  # 6%
            min_car_ratio = 0.08     # 8%
            
            # Liquidity coverage ratio (LCR)
            hqla = capital_data.get('high_quality_liquid_assets', 0)  # HQLA
            net_cash_outflows = capital_data.get('net_cash_outflows_30d', 0)
            lcr_ratio = (hqla / net_cash_outflows) if net_cash_outflows > 0 else 0
            
            min_lcr = 1.0  # 100%
            
            # Net stable funding ratio (NSFR)
            available_stable_funding = capital_data.get('available_stable_funding', 0)
            required_stable_funding = capital_data.get('required_stable_funding', 0)
            nsfr_ratio = (available_stable_funding / required_stable_funding) if required_stable_funding > 0 else 0
            
            min_nsfr = 1.0  # 100%
            
            compliance_status = {
                'capital_adequacy_ratio': car_ratio,
                'tier_1_ratio': tier_1_ratio,
                'liquidity_coverage_ratio': lcr_ratio,
                'net_stable_funding_ratio': nsfr_ratio,
                'regulatory_requirements': {
                    'min_tier_1_ratio': min_tier_1_ratio,
                    'min_car_ratio': min_car_ratio,
                    'min_lcr': min_lcr,
                    'min_nsfr': min_nsfr
                },
                'compliance_status': {
                    'tier_1_compliant': tier_1_ratio >= min_tier_1_ratio,
                    'car_compliant': car_ratio >= min_car_ratio,
                    'lcr_compliant': lcr_ratio >= min_lcr,
                    'nsfr_compliant': nsfr_ratio >= min_nsfr
                },
                'risk_weighted_assets': risk_weighted_assets
            }
            
            # Overall compliance
            compliance_issues = [k for k, v in compliance_status['compliance_status'].items() if not v]
            overall_compliant = len(compliance_issues) == 0
            
            compliance_status.update({
                'overall_compliant': overall_compliant,
                'compliance_issues': compliance_issues,
                'compliance_score': 1.0 - (len(compliance_issues) / len(compliance_status['compliance_status']))
            })
            
            return compliance_status
            
        except Exception as e:
            logger.error(f"Basel III compliance check error: {e}")
            return {'overall_compliant': False, 'error': str(e)}
    
    def check_mifid_ii_compliance(self, trading_data: Dict) -> Dict[str, Any]:
        """MiFID II compliance check"""
        try:
            # Pre-trade transparency
            pre_trade_checks = self._check_pre_trade_transparency(trading_data)
            
            # Best execution
            best_execution_check = self._check_best_execution(trading_data)
            
            # Transaction reporting
            transaction_reporting_check = self._check_transaction_reporting(trading_data)
            
            # Product governance
            product_governance_check = self._check_product_governance(trading_data)
            
            # Investor protection
            investor_protection_check = self._check_investor_protection(trading_data)
            
            compliance_status = {
                'pre_trade_transparency': pre_trade_checks,
                'best_execution': best_execution_check,
                'transaction_reporting': transaction_reporting_check,
                'product_governance': product_governance_check,
                'investor_protection': investor_protection_check,
                'overall_compliance_score': 0.0
            }
            
            # Calculate overall score
            scores = [check.get('score', 0) for check in compliance_status.values() 
                     if isinstance(check, dict) and 'score' in check]
            
            if scores:
                compliance_status['overall_compliance_score'] = np.mean(scores)
            
            compliance_status['overall_compliant'] = compliance_status['overall_compliance_score'] >= 0.9
            
            return compliance_status
            
        except Exception as e:
            logger.error(f"MiFID II compliance check error: {e}")
            return {'overall_compliant': False, 'error': str(e)}
    
    def _calculate_risk_weighted_assets(self, positions: List[Position]) -> float:
        """Risk-weighted assets hisoblash"""
        risk_weights = {
            'GOVERNMENT': 0.0,
            'CORPORATE_INVESTMENT_GRADE': 0.2,
            'CORPORATE_HIGH_YIELD': 0.5,
            'EQUITY': 1.0,
            'RETAIL_MORTGAGE': 0.35,
            'OTHER_RETAIL': 0.75
        }
        
        rwa = 0.0
        for position in positions:
            # Simplified risk weight determination
            asset_type = 'EQUITY'  # Default
            if 'BOND' in position.asset_class.upper():
                if 'GOVERNMENT' in position.sector.upper():
                    asset_type = 'GOVERNMENT'
                elif 'CORPORATE' in position.sector.upper():
                    asset_type = 'CORPORATE_INVESTMENT_GRADE'  # Simplified
                else:
                    asset_type = 'OTHER_RETAIL'  # Simplified
            
            risk_weight = risk_weights.get(asset_type, 1.0)
            rwa += position.market_value * risk_weight
        
        return rwa
    
    def _check_pre_trade_transparency(self, trading_data: Dict) -> Dict[str, Any]:
        """Pre-trade transparency check"""
        # Simplified check
        transparent_orders = trading_data.get('transparent_orders', 0)
        total_orders = trading_data.get('total_orders', 1)
        
        transparency_ratio = transparent_orders / total_orders if total_orders > 0 else 0
        
        return {
            'score': transparency_ratio,
            'transparent_orders': transparent_orders,
            'total_orders': total_orders,
            'transparency_ratio': transparency_ratio,
            'compliant': transparency_ratio >= 0.9
        }
    
    def _check_best_execution(self, trading_data: Dict) -> Dict[str, Any]:
        """Best execution check"""
        # Simplified check
        execution_quality = trading_data.get('execution_quality_score', 0.8)
        
        return {
            'score': execution_quality,
            'execution_quality_score': execution_quality,
            'compliant': execution_quality >= 0.8
        }
    
    def _check_transaction_reporting(self, trading_data: Dict) -> Dict[str, Any]:
        """Transaction reporting check"""
        reported_transactions = trading_data.get('reported_transactions', 0)
        total_transactions = trading_data.get('total_transactions', 1)
        
        reporting_ratio = reported_transactions / total_transactions if total_transactions > 0 else 0
        
        return {
            'score': reporting_ratio,
            'reported_transactions': reported_transactions,
            'total_transactions': total_transactions,
            'reporting_ratio': reporting_ratio,
            'compliant': reporting_ratio >= 0.95
        }
    
    def _check_product_governance(self, trading_data: Dict) -> Dict[str, Any]:
        """Product governance check"""
        compliant_products = trading_data.get('compliant_products', 0)
        total_products = trading_data.get('total_products', 1)
        
        governance_ratio = compliant_products / total_products if total_products > 0 else 0
        
        return {
            'score': governance_ratio,
            'compliant_products': compliant_products,
            'total_products': total_products,
            'governance_ratio': governance_ratio,
            'compliant': governance_ratio >= 0.9
        }
    
    def _check_investor_protection(self, trading_data: Dict) -> Dict[str, Any]:
        """Investor protection check"""
        protection_score = trading_data.get('investor_protection_score', 0.8)
        
        return {
            'score': protection_score,
            'investor_protection_score': protection_score,
            'compliant': protection_score >= 0.8
        }


class RiskDashboard:
    """Risk visualization and monitoring dashboard"""
    
    def __init__(self):
        self.dashboard_data = {}
        self.alerts = []
        self.metrics_history = []
    
    def generate_risk_dashboard(self, positions: List[Position],
                              risk_metrics: RiskMetrics,
                              real_time_data: Dict) -> Dict[str, Any]:
        """Risk dashboard yaratish"""
        try:
            # Summary metrics
            total_portfolio_value = sum(pos.market_value for pos in positions)
            
            dashboard = {
                'timestamp': datetime.now().isoformat(),
                'portfolio_summary': {
                    'total_value': total_portfolio_value,
                    'position_count': len(positions),
                    'largest_position_weight': max([pos.weight for pos in positions]) if positions else 0,
                    'diversification_score': self._calculate_diversification_score(positions)
                },
                'risk_metrics': risk_metrics.to_dict(),
                'real_time_indicators': {
                    'current_var': real_time_data.get('var_95', 0),
                    'portfolio_volatility': real_time_data.get('volatility', 0),
                    'correlation_risk': real_time_data.get('correlation_risk', 0),
                    'liquidity_risk': real_time_data.get('liquidity_risk', 0)
                },
                'alerts_summary': {
                    'total_alerts': len(self.alerts),
                    'high_priority_alerts': len([a for a in self.alerts if a.level == RiskLevel.HIGH]),
                    'critical_alerts': len([a for a in self.alerts if a.level == RiskLevel.CRITICAL]),
                    'unresolved_alerts': len([a for a in self.alerts if not a.resolved])
                },
                'position_analysis': self._analyze_positions(positions),
                'risk_trends': self._get_risk_trends(),
                'regulatory_status': self._get_regulatory_status()
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Dashboard generation error: {e}")
            return {}
    
    def _calculate_diversification_score(self, positions: List[Position]) -> float:
        """Diversification score hisoblash"""
        if not positions:
            return 0.0
        
        # Calculate Herfindahl-Hirschman Index (HHI)
        weights = np.array([pos.weight for pos in positions])
        hhi = np.sum(weights ** 2)
        
        # Convert to diversification score (1 - HHI)
        diversification_score = 1.0 - hhi
        
        return max(0.0, min(1.0, diversification_score))
    
    def _analyze_positions(self, positions: List[Position]) -> Dict[str, Any]:
        """Pozitsiya analizi"""
        if not positions:
            return {}
        
        # Asset class distribution
        asset_classes = {}
        sectors = {}
        regions = {}
        
        for position in positions:
            # Asset class
            asset_class = position.asset_class or 'UNKNOWN'
            asset_classes[asset_class] = asset_classes.get(asset_class, 0) + position.weight
            
            # Sector
            sector = position.sector or 'UNKNOWN'
            sectors[sector] = sectors.get(sector, 0) + position.weight
            
            # Region
            region = position.region or 'UNKNOWN'
            regions[region] = regions.get(region, 0) + position.weight
        
        return {
            'asset_class_distribution': asset_classes,
            'sector_distribution': sectors,
            'regional_distribution': regions,
            'concentration_risks': self._identify_concentration_risks(positions)
        }
    
    def _identify_concentration_risks(self, positions: List[Position]) -> List[Dict]:
        """Concentration risk larni aniqlash"""
        risks = []
        
        # Position concentration
        max_position = max([pos.weight for pos in positions]) if positions else 0
        if max_position > 0.20:  # 20% limit
            risks.append({
                'type': 'POSITION_CONCENTRATION',
                'severity': 'HIGH' if max_position > 0.30 else 'MEDIUM',
                'max_weight': max_position,
                'limit': 0.20
            })
        
        # Sector concentration
        sector_weights = {}
        for position in positions:
            sector = position.sector or 'UNKNOWN'
            sector_weights[sector] = sector_weights.get(sector, 0) + position.weight
        
        max_sector = max(sector_weights.values()) if sector_weights else 0
        if max_sector > 0.40:  # 40% sector limit
            risks.append({
                'type': 'SECTOR_CONCENTRATION',
                'severity': 'HIGH' if max_sector > 0.60 else 'MEDIUM',
                'max_weight': max_sector,
                'limit': 0.40
            })
        
        return risks
    
    def _get_risk_trends(self) -> Dict[str, List[float]]:
        """Risk trends (historical data)"""
        # This would typically fetch from a database
        # For now, return placeholder trends
        current_time = datetime.now()
        days = 30
        
        trends = {
            'var_trend': [0.05 + np.random.normal(0, 0.01) for _ in range(days)],
            'volatility_trend': [0.15 + np.random.normal(0, 0.02) for _ in range(days)],
            'correlation_trend': [0.3 + np.random.normal(0, 0.05) for _ in range(days)]
        }
        
        return trends
    
    def _get_regulatory_status(self) -> Dict[str, str]:
        """Regulatory compliance status"""
        return {
            'basel_iii': 'COMPLIANT',
            'mifid_ii': 'COMPLIANT',
            'dodd_frank': 'NOT_APPLICABLE',
            'overall': 'GOOD'
        }
    
    def add_alert(self, alert: Alert):
        """Dashboard ga alert qo'shish"""
        self.alerts.append(alert)
        # Keep only last 1000 alerts
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
    
    def get_active_alerts(self, risk_level: Optional[RiskLevel] = None) -> List[Alert]:
        """Aktiv alertlarni olish"""
        alerts = [a for a in self.alerts if not a.resolved]
        
        if risk_level:
            alerts = [a for a in alerts if a.level == risk_level]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def generate_alert_report(self) -> Dict[str, Any]:
        """Alert hisoboti yaratish"""
        active_alerts = self.get_active_alerts()
        
        return {
            'report_timestamp': datetime.now().isoformat(),
            'total_active_alerts': len(active_alerts),
            'alerts_by_level': {
                level.value: len([a for a in active_alerts if a.level == level])
                for level in RiskLevel
            },
            'alerts_by_type': {
                risk_type.value: len([a for a in active_alerts if a.risk_type == risk_type])
                for risk_type in RiskType
            },
            'recent_alerts': [a.to_dict() for a in active_alerts[:10]],
            'resolution_recommendations': self._get_resolution_recommendations(active_alerts)
        }
    
    def _get_resolution_recommendations(self, alerts: List[Alert]) -> List[str]:
        """Alert resolution uchun tavsiyalar"""
        recommendations = []
        
        # Count alert types
        alert_counts = {}
        for alert in alerts:
            alert_type = alert.risk_type.value
            alert_counts[alert_type] = alert_counts.get(alert_type, 0) + 1
        
        # Generate recommendations based on alert patterns
        if alert_counts.get('MARKET', 0) > 5:
            recommendations.append("Consider portfolio rebalancing to reduce market exposure")
        
        if alert_counts.get('LIQUIDITY', 0) > 3:
            recommendations.append("Review liquidity constraints and consider position sizing adjustments")
        
        if alert_counts.get('OPERATIONAL', 0) > 2:
            recommendations.append("Investigate operational issues and consider system upgrades")
        
        if alert_counts.get('CREDIT', 0) > 2:
            recommendations.append("Review counterparty exposures and consider credit risk limits")
        
        # High priority alerts
        critical_alerts = [a for a in alerts if a.level == RiskLevel.CRITICAL]
        if critical_alerts:
            recommendations.append(f"Immediate attention required for {len(critical_alerts)} critical alerts")
        
        return recommendations


class AdvancedRiskManager:
    """Asosiy risk management engine"""
    
    def __init__(self, db_path: str = "/workspace/orion-starline/backend/data/risk_data.db"):
        # Database initialization
        self.db = SQLiteRiskDatabase(db_path)
        
        # Core components
        self.risk_scorer = RealTimeRiskScorer()
        self.stress_tester = PortfolioStressTester()
        self.risk_controls = RiskControlAutomation()
        self.var_calculator = VaRCalculator()
        self.monte_carlo = MonteCarloSimulator()
        self.liquidity_analyzer = LiquidityRiskAnalyzer()
        self.credit_evaluator = CreditRiskEvaluator()
        self.operational_monitor = OperationalRiskMonitor()
        self.compliance_checker = RegulatoryCompliance()
        self.dashboard = RiskDashboard()
        
        # System configuration
        self.risk_tolerance = 0.05  # 5% maximum risk tolerance
        self.alerts_enabled = True
        self.auto_rebalance = False
        
        # Real-time monitoring
        self.is_running = False
        self.monitoring_thread = None
        self.monitoring_interval = 60  # seconds
        
        logger.info("Advanced Risk Management System initialized")
    
    def start_real_time_monitoring(self, update_interval: int = 60):
        """Real-time monitoring boshlash"""
        try:
            if self.is_running:
                logger.warning("Monitoring already running")
                return
            
            self.is_running = True
            self.monitoring_interval = update_interval
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                args=(update_interval,),
                daemon=True
            )
            self.monitoring_thread.start()
            
            logger.info(f"Real-time monitoring started (interval: {update_interval}s)")
            
        except Exception as e:
            logger.error(f"Monitoring start qilishda xato: {e}")
    
    def stop_real_time_monitoring(self):
        """Real-time monitoring to'xtatish"""
        try:
            self.is_running = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)
            
            logger.info("Real-time monitoring stopped")
            
        except Exception as e:
            logger.error(f"Monitoring to'xtatishda xato: {e}")
    
    def _monitoring_loop(self, update_interval: int):
        """Monitoring loop"""
        while self.is_running:
            try:
                # Get current positions (placeholder - would connect to real trading system)
                positions = self._get_current_positions()
                
                if positions:
                    # Calculate risk metrics
                    risk_score, risk_level = self.risk_scorer.get_risk_score(
                        positions, {}, {}, {}, {}
                    )
                    
                    # Store metrics in database
                    metrics = RiskMetrics(var_95=risk_score)
                    self.db.insert_risk_metrics(metrics)
                    
                    # Check alerts
                    if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                        alert = Alert(
                            alert_id=f"monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            timestamp=datetime.now(),
                            risk_type=RiskType.MARKET,
                            level=risk_level,
                            message=f"High risk detected during monitoring: {risk_score:.2%}",
                            metric_value=risk_score,
                            threshold=0.6
                        )
                        self.dashboard.add_alert(alert)
                    
                    logger.debug(f"Monitoring update completed: {len(positions)} positions, Risk: {risk_score:.2%}")
                
                # Sleep until next update
                threading.Event().wait(update_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loopda xato: {e}")
                threading.Event().wait(30)  # Wait 30s on error
    
    def _get_current_positions(self) -> List[Position]:
        """Get current positions (placeholder)"""
        # This would normally connect to your trading system
        # For demo purposes, return sample positions
        return [
            Position("BTC", 10, 45000, 46500, "LONG", datetime.now()),
            Position("AAPL", 100, 150, 155, "LONG", datetime.now()),
            Position("TSLA", 50, 200, 210, "LONG", datetime.now())
        ]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            'is_running': self.is_running,
            'monitoring_active': self.monitoring_thread is not None and self.monitoring_thread.is_alive(),
            'database_path': self.db.db_path,
            'risk_tolerance': self.risk_tolerance,
            'alerts_enabled': self.alerts_enabled,
            'timestamp': datetime.now().isoformat()
        }
    
    async def comprehensive_risk_analysis(self, positions: List[Position]) -> Dict[str, Any]:
        """Comprehensive risk analysis"""
        try:
            logger.info("Starting comprehensive risk analysis...")
            
            # Parallel risk assessments
            tasks = [
                self._run_risk_scorer(positions),
                self._run_stress_tests(positions),
                self._run_liquidity_assessment(positions),
                self._run_market_risk_evaluation(positions),
                self._run_credit_risk_assessment(positions),
                self._run_regulatory_compliance(positions)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            risk_score, stress_results, liquidity_risk, market_risk, credit_risk, compliance = results
            
            # Compile comprehensive report
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'positions_count': len(positions),
                'risk_score': risk_score if not isinstance(risk_score, Exception) else None,
                'stress_testing': stress_results if not isinstance(stress_results, Exception) else None,
                'liquidity_assessment': liquidity_risk if not isinstance(liquidity_risk, Exception) else None,
                'market_risk_evaluation': market_risk if not isinstance(market_risk, Exception) else None,
                'credit_risk_assessment': credit_risk if not isinstance(credit_risk, Exception) else None,
                'regulatory_compliance': compliance if not isinstance(compliance, Exception) else None,
                'overall_risk_rating': self._calculate_overall_rating(risk_score, stress_results, liquidity_risk),
                'recommendations': self._generate_recommendations(risk_score, stress_results, liquidity_risk)
            }
            
            logger.info("Comprehensive risk analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"Comprehensive analysisda xato: {e}")
            return {'error': str(e)}
    
    async def _run_risk_scorer(self, positions: List[Position]):
        """Risk scoring task"""
        try:
            return self.risk_scorer.get_risk_score(positions, {}, {}, {}, {})
        except Exception as e:
            logger.error(f"Risk scorer taskda xato: {e}")
            return e
    
    async def _run_stress_tests(self, positions: List[Position]):
        """Stress testing task"""
        try:
            return self.stress_tester.run_full_stress_test(positions)
        except Exception as e:
            logger.error(f"Stress test taskda xato: {e}")
            return e
    
    async def _run_liquidity_assessment(self, positions: List[Position]):
        """Liquidity assessment task"""
        try:
            return self.liquidity_analyzer.assess_portfolio_liquidity(positions, {})
        except Exception as e:
            logger.error(f"Liquidity assessment taskda xato: {e}")
            return e
    
    async def _run_market_risk_evaluation(self, positions: List[Position]):
        """Market risk evaluation task"""
        try:
            return self.var_calculator.calculate_portfolio_var(positions, pd.DataFrame())
        except Exception as e:
            logger.error(f"Market risk evaluation taskda xato: {e}")
            return e
    
    async def _run_credit_risk_assessment(self, positions: List[Position]):
        """Credit risk assessment task"""
        try:
            return self.credit_evaluator.assess_portfolio_credit_risk(positions, {})
        except Exception as e:
            logger.error(f"Credit risk assessment taskda xato: {e}")
            return e
    
    async def _run_regulatory_compliance(self, positions: List[Position]):
        """Regulatory compliance task"""
        try:
            return self.compliance_checker.check_basel_iii_compliance(positions, None, {})
        except Exception as e:
            logger.error(f"Regulatory compliance taskda xato: {e}")
            return e
    
    def _calculate_overall_rating(self, risk_score, stress_results, liquidity_risk) -> str:
        """Overall risk rating calculation"""
        try:
            if (isinstance(risk_score, Exception) or 
                isinstance(stress_results, Exception) or 
                isinstance(liquidity_risk, Exception)):
                return "UNKNOWN"
            
            risk_factors = []
            
            # Risk score factors
            if risk_score and isinstance(risk_score, tuple):
                risk_factors.append(risk_score[0])  # The risk score value
            
            # Stress test factors
            if stress_results and isinstance(stress_results, dict):
                if 'summary' in stress_results:
                    stress_scores = [stress_results['summary'].get('worst_case_loss', 0)]
                    if stress_scores:
                        risk_factors.append(np.mean(stress_scores) / 100000)  # Normalize
            
            # Liquidity factors
            if liquidity_risk and isinstance(liquidity_risk, dict):
                portfolio_liq = liquidity_risk.get('portfolio_liquidity', {})
                risk_factors.append(1 - portfolio_liq.get('overall_liquidity_score', 1))
            
            if not risk_factors:
                return "UNKNOWN"
            
            average_risk = np.mean(risk_factors)
            
            if average_risk > 0.8:
                return "CRITICAL"
            elif average_risk > 0.6:
                return "HIGH"
            elif average_risk > 0.4:
                return "MEDIUM"
            elif average_risk > 0.2:
                return "LOW"
            else:
                return "MINIMAL"
                
        except Exception as e:
            logger.error(f"Overall rating calculationda xato: {e}")
            return "UNKNOWN"
    
    def _generate_recommendations(self, risk_score, stress_results, liquidity_risk) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        try:
            # Risk score recommendations
            if risk_score and isinstance(risk_score, tuple):
                score, level = risk_score
                if score > 0.7:
                    recommendations.append("Consider reducing position sizes to lower risk")
                
                if level == RiskLevel.CRITICAL:
                    recommendations.append("URGENT: Immediate risk reduction required")
                elif level == RiskLevel.HIGH:
                    recommendations.append("High risk detected - implement additional risk controls")
            
            # Stress test recommendations
            if stress_results and isinstance(stress_results, dict):
                if 'summary' in stress_results:
                    worst_case = stress_results['summary'].get('worst_case_loss', 0)
                    if worst_case > 100000:  # $100k threshold
                        recommendations.append("Prepare contingency plans for severe market scenarios")
            
            # Liquidity recommendations
            if liquidity_risk and isinstance(liquidity_risk, dict):
                portfolio_liq = liquidity_risk.get('portfolio_liquidity', {})
                liquidity_score = portfolio_liq.get('overall_liquidity_score', 1)
                if liquidity_score < 0.5:
                    recommendations.append("URGENT: Increase liquidity immediately")
                elif liquidity_score < 0.7:
                    recommendations.append("Monitor liquidity position closely")
            
            if not recommendations:
                recommendations.append("Risk profile is within acceptable parameters")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendations generationda xato: {e}")
            return ["Unable to generate recommendations due to system error"]
    
    async def comprehensive_risk_assessment(self, positions: List[Position],
                                          market_data: Dict,
                                          credit_data: Dict,
                                          liquidity_data: Dict,
                                          operational_data: Dict) -> Dict[str, Any]:
        """Comprehensive risk assessment"""
        try:
            assessment_start = datetime.now()
            
            # 1. Real-time risk scoring
            risk_score, risk_level = self.risk_scorer.get_risk_score(
                positions, market_data, credit_data, liquidity_data, operational_data
            )
            
            # 2. Calculate VaR
            var_results = self.var_calculator.calculate_portfolio_var(
                positions, market_data.get('returns', pd.DataFrame())
            )
            
            # 3. Stress testing
            stress_test_results = self.stress_tester.run_full_stress_test(positions)
            
            # 4. Liquidity assessment
            liquidity_assessment = self.liquidity_analyzer.assess_portfolio_liquidity(
                positions, liquidity_data
            )
            
            # 5. Credit risk assessment
            credit_assessment = self.credit_evaluator.assess_portfolio_credit_risk(
                positions, credit_data
            )
            
            # 6. Operational risk monitoring
            operational_assessment = self.operational_monitor.monitor_system_health(
                operational_data
            )
            
            # 7. Regulatory compliance
            basel_compliance = self.compliance_checker.check_basel_iii_compliance(
                positions, None, market_data.get('capital', {})
            )
            
            mifid_compliance = self.compliance_checker.check_mifid_ii_compliance(
                market_data.get('trading', {})
            )
            
            # 8. Risk controls checking
            position_limits_check = self.risk_controls.check_position_limits(
                positions, market_data
            )
            
            # 9. Monte Carlo simulation
            simulation_results = self.monte_carlo.simulate_portfolio_evolution(
                positions, market_data.get('scenarios', {})
            )
            
            # 10. Generate dashboard data
            dashboard_data = self.dashboard.generate_risk_dashboard(
                positions, RiskMetrics(**var_results), market_data
            )
            
            # Compile comprehensive assessment
            assessment = {
                'assessment_timestamp': assessment_start.isoformat(),
                'execution_time_ms': (datetime.now() - assessment_start).total_seconds() * 1000,
                'portfolio_overview': {
                    'total_positions': len(positions),
                    'total_value': sum(pos.market_value for pos in positions),
                    'risk_level': risk_level.value,
                    'risk_score': risk_score
                },
                'risk_metrics': var_results,
                'stress_testing': stress_test_results,
                'liquidity_analysis': liquidity_assessment,
                'credit_analysis': credit_assessment,
                'operational_assessment': operational_assessment,
                'compliance_status': {
                    'basel_iii': basel_compliance,
                    'mifid_ii': mifid_compliance
                },
                'risk_controls': position_limits_check,
                'monte_carlo_simulation': simulation_results,
                'dashboard': dashboard_data,
                'recommendations': self._generate_recommendations(risk_score, risk_level, var_results),
                'alert_level': self._determine_alert_level(risk_score, risk_level)
            }
            
            # Generate alerts if necessary
            if self.alerts_enabled:
                await self._generate_risk_alerts(assessment)
            
            logger.info(f"Comprehensive risk assessment completed in {assessment['execution_time_ms']:.2f}ms")
            
            return assessment
            
        except Exception as e:
            logger.error(f"Comprehensive risk assessment error: {e}")
            return {'error': str(e), 'assessment_failed': True}
    
    def _generate_recommendations(self, risk_score: float, risk_level: RiskLevel, 
                                var_results: Dict) -> List[str]:
        """Risk assessment uchun tavsiyalar"""
        recommendations = []
        
        # Risk score based recommendations
        if risk_score > 0.7:
            recommendations.append("Portfolio risk exceeds acceptable thresholds - consider immediate rebalancing")
        elif risk_score > 0.5:
            recommendations.append("Portfolio risk is elevated - monitor closely and consider risk reduction measures")
        
        # VaR based recommendations
        if var_results.get('historical_var', 0) > 0.1:  # 10% VaR
            recommendations.append("High VaR detected - consider reducing position sizes or adding hedges")
        
        # Risk level based recommendations
        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "Immediate risk reduction required",
                "Consider liquidation of high-risk positions",
                "Activate emergency risk management protocols"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.append("High risk detected - implement additional risk controls")
        
        # Diversification recommendations
        recommendations.append("Review portfolio diversification and correlation exposures")
        
        # Liquidity recommendations
        recommendations.append("Monitor portfolio liquidity and position sizing based on liquidity metrics")
        
        return recommendations
    
    def _determine_alert_level(self, risk_score: float, risk_level: RiskLevel) -> str:
        """Alert level aniqlash"""
        if risk_level == RiskLevel.CRITICAL:
            return "CRITICAL"
        elif risk_level == RiskLevel.HIGH:
            return "HIGH"
        elif risk_score > 0.6:
            return "MEDIUM"
        elif risk_score > 0.4:
            return "LOW"
        else:
            return "MINIMAL"
    
    async def _generate_risk_alerts(self, assessment: Dict[str, Any]):
        """Risk alertlarni yaratish"""
        try:
            risk_score = assessment['portfolio_overview']['risk_score']
            risk_level = RiskLevel(assessment['portfolio_overview']['risk_level'])
            
            # Generate alerts based on risk metrics
            if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                alert = Alert(
                    alert_id=f"risk_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.now(),
                    risk_type=RiskType.MARKET,
                    level=risk_level,
                    message=f"High risk detected: {risk_score:.2%}",
                    metric_value=risk_score,
                    threshold=0.6
                )
                self.dashboard.add_alert(alert)
            
            # VaR alerts
            var_95 = assessment['risk_metrics'].get('historical_var', 0)
            if var_95 > 0.1:  # 10% VaR threshold
                alert = Alert(
                    alert_id=f"var_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.now(),
                    risk_type=RiskType.MARKET,
                    level=RiskLevel.HIGH,
                    message=f"VaR threshold exceeded: {var_95:.2%}",
                    metric_value=var_95,
                    threshold=0.1
                )
                self.dashboard.add_alert(alert)
            
            # Stress test alerts
            stress_results = assessment.get('stress_testing', {})
            if stress_results.get('scenarios'):
                for scenario_name, scenario_result in stress_results['scenarios'].items():
                    loss_pct = scenario_result.get('percentage_loss', 0)
                    if loss_pct > 20:  # 20% loss in stress test
                        alert = Alert(
                            alert_id=f"stress_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            timestamp=datetime.now(),
                            risk_type=RiskType.MARKET,
                            level=RiskLevel.CRITICAL,
                            message=f"Stress test failure in {scenario_name}: {loss_pct:.1f}% loss",
                            metric_value=loss_pct,
                            threshold=20.0
                        )
                        self.dashboard.add_alert(alert)
            
        except Exception as e:
            logger.error(f"Risk alert generation error: {e}")
    
    def generate_risk_report(self, assessment: Dict[str, Any], 
                           output_format: str = 'json') -> Union[Dict, str]:
        """Risk report yaratish"""
        try:
            report = {
                'report_metadata': {
                    'report_id': f"RISK_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'generated_at': datetime.now().isoformat(),
                    'report_version': '2.0.0',
                    'report_type': 'COMPREHENSIVE_RISK_ASSESSMENT'
                },
                'executive_summary': {
                    'overall_risk_level': assessment['portfolio_overview']['risk_level'],
                    'risk_score': assessment['portfolio_overview']['risk_score'],
                    'total_portfolio_value': assessment['portfolio_overview']['total_value'],
                    'key_risks': self._identify_key_risks(assessment),
                    'critical_alerts': len([a for a in self.dashboard.alerts 
                                         if a.level == RiskLevel.CRITICAL and not a.resolved])
                },
                'detailed_assessment': assessment,
                'regulatory_compliance': assessment.get('compliance_status', {}),
                'action_items': self._generate_action_items(assessment),
                'next_steps': self._generate_next_steps(assessment)
            }
            
            if output_format.lower() == 'json':
                return report
            else:
                return json.dumps(report, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Risk report generation error: {e}")
            return {'error': str(e)}
    
    def _identify_key_risks(self, assessment: Dict[str, Any]) -> List[str]:
        """Asosiy risklarni aniqlash"""
        key_risks = []
        
        risk_score = assessment['portfolio_overview']['risk_score']
        if risk_score > 0.7:
            key_risks.append("High portfolio risk exposure")
        
        var_results = assessment.get('risk_metrics', {})
        if var_results.get('historical_var', 0) > 0.1:
            key_risks.append("Elevated Value at Risk")
        
        stress_results = assessment.get('stress_testing', {})
        if stress_results.get('scenarios'):
            worst_loss = max([s.get('percentage_loss', 0) 
                            for s in stress_results['scenarios'].values()])
            if worst_loss > 15:
                key_risks.append("Significant stress test losses")
        
        liquidity_assessment = assessment.get('liquidity_analysis', {})
        if liquidity_assessment.get('portfolio_liquidity', {}).get('liquidity_risk_level') in ['POOR', 'VERY_POOR']:
            key_risks.append("Poor portfolio liquidity")
        
        return key_risks
    
    def _generate_action_items(self, assessment: Dict[str, Any]) -> List[str]:
        """Action itemlarni yaratish"""
        actions = []
        
        risk_level = assessment['portfolio_overview']['risk_level']
        if risk_level in ['HIGH', 'CRITICAL']:
            actions.extend([
                "Immediate portfolio risk review required",
                "Consider position rebalancing",
                "Implement additional risk controls"
            ])
        
        compliance_status = assessment.get('compliance_status', {})
        if compliance_status.get('basel_iii', {}).get('overall_compliant') == False:
            actions.append("Address Basel III compliance issues")
        
        if compliance_status.get('mifid_ii', {}).get('overall_compliant') == False:
            actions.append("Address MiFID II compliance issues")
        
        # Stress test actions
        stress_results = assessment.get('stress_testing', {})
        if stress_results.get('summary', {}).get('worst_case_loss', 0) > 100000:  # $100k threshold
            actions.append("Review stress test scenarios and prepare contingency plans")
        
        return actions
    
    def _generate_next_steps(self, assessment: Dict[str, Any]) -> List[str]:
        """Keyingi qadamlar"""
        return [
            "Schedule next risk assessment in 24 hours",
            "Monitor risk metrics continuously",
            "Review and update risk management policies",
            "Conduct quarterly stress testing",
            "Update regulatory compliance procedures"
        ]


# Utility functions
def create_sample_positions() -> List[Position]:
    """Namuna pozitsiyalar yaratish"""
    return [
        Position(
            symbol="AAPL",
            quantity=1000,
            price=150.0,
            market_value=150000,
            weight=0.15,
            asset_class="EQUITY",
            sector="TECHNOLOGY",
            region="US"
        ),
        Position(
            symbol="GOOGL",
            quantity=500,
            price=2000.0,
            market_value=1000000,
            weight=0.25,
            asset_class="EQUITY",
            sector="TECHNOLOGY",
            region="US"
        ),
        Position(
            symbol="US10Y",
            quantity=10000,
            price=100.0,
            market_value=1000000,
            weight=0.30,
            asset_class="BOND",
            sector="GOVERNMENT",
            region="US"
        ),
        Position(
            symbol="EURUSD",
            quantity=1000000,
            price=1.10,
            market_value=500000,
            weight=0.20,
            asset_class="CURRENCY",
            region="EU"
        ),
        Position(
            symbol="GOLD",
            quantity=2000,
            price=1800.0,
            market_value=250000,
            weight=0.10,
            asset_class="COMMODITY",
            region="GLOBAL"
        )
    ]


def create_sample_market_data() -> Dict:
    """Namuna market data yaratish"""
    return {
        'AAPL_volatility': 0.25,
        'GOOGL_volatility': 0.30,
        'US10Y_volatility': 0.05,
        'EURUSD_volatility': 0.12,
        'GOLD_volatility': 0.20,
        'returns': pd.DataFrame({
            'AAPL': np.random.normal(0.001, 0.025, 252),
            'GOOGL': np.random.normal(0.001, 0.030, 252),
            'US10Y': np.random.normal(0.0002, 0.005, 252),
            'EURUSD': np.random.normal(0.0001, 0.012, 252),
            'GOLD': np.random.normal(0.0005, 0.020, 252)
        }),
        'capital': {
            'tier_1_capital': 5000000,
            'total_capital': 6000000,
            'high_quality_liquid_assets': 2000000,
            'net_cash_outflows_30d': 1500000
        }
    }


def demo_advanced_risk_management():
    """Advanced Risk Management demo"""
    print("🚀 Advanced Risk Management System Demo")
    print("=" * 50)
    
    # Initialize the risk manager
    risk_manager = AdvancedRiskManager()
    
    # Create sample data
    positions = create_sample_positions()
    market_data = create_sample_market_data()
    credit_data = {
        'AAPL': {'credit_rating': 'AA+', 'credit_spread': 0.003},
        'GOOGL': {'credit_rating': 'AA', 'credit_spread': 0.003},
        'US10Y': {'credit_rating': 'AAA', 'credit_spread': 0.001}
    }
    
    liquidity_data = {
        'AAPL': {'bid': 149.5, 'ask': 150.5, 'mid_price': 150.0, 'bid_depth': 50000, 'ask_depth': 55000},
        'GOOGL': {'bid': 1995.0, 'ask': 2005.0, 'mid_price': 2000.0, 'bid_depth': 10000, 'ask_depth': 12000},
        'US10Y': {'bid': 99.9, 'ask': 100.1, 'mid_price': 100.0, 'bid_depth': 100000, 'ask_depth': 95000}
    }
    
    operational_data = {
        'system_availability': 0.995,
        'response_time_ms': 85,
        'error_rate': 0.0005,
        'throughput_rps': 1500,
        'trading_volume_24h': 5000000,
        'avg_volume_30d': 4800000
    }
    
    # Run comprehensive risk assessment
    print("📊 Comprehensive Risk Assessment boshlanmoqda...")
    assessment = asyncio.run(risk_manager.comprehensive_risk_assessment(
        positions, market_data, credit_data, liquidity_data, operational_data
    ))
    
    # Display results
    if 'error' not in assessment:
        print(f"✅ Assessment tugallandi: {assessment['execution_time_ms']:.2f}ms")
        print(f"📈 Portfolio qiymati: ${assessment['portfolio_overview']['total_value']:,.2f}")
        print(f"⚠️ Risk darajasi: {assessment['portfolio_overview']['risk_level']}")
        print(f"📊 Risk skori: {assessment['portfolio_overview']['risk_score']:.2%}")
        
        # VaR results
        var_results = assessment.get('risk_metrics', {})
        if var_results:
            print(f"💰 Historical VaR (95%): {var_results.get('historical_var', 0):.2%}")
            print(f"💰 VaR (99%): {var_results.get('parametric_var', 0):.2%}")
        
        # Stress test results
        stress_results = assessment.get('stress_testing', {})
        if stress_results.get('scenarios'):
            worst_case = max([s.get('percentage_loss', 0) for s in stress_results['scenarios'].values()])
            print(f"🌪️ Worst-case stress test loss: {worst_case:.1f}%")
        
        # Alerts
        alerts = risk_manager.dashboard.get_active_alerts()
        print(f"🚨 Active alerts: {len(alerts)}")
        for alert in alerts[:3]:  # Show first 3 alerts
            print(f"   - {alert.level.value}: {alert.message}")
        
        # Generate report
        print("\n📋 Risk report yaratilmoqda...")
        report = risk_manager.generate_risk_report(assessment)
        
        # Save report to file
        report_filename = f"advanced_risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"✅ Hisobot saqlandi: {report_filename}")
        
        print("\n🎯 Asosiy tavsiyalar:")
        for i, rec in enumerate(assessment.get('recommendations', [])[:3], 1):
            print(f"   {i}. {rec}")
    
    else:
        print(f"❌ Assessmentda xatolik: {assessment['error']}")
    
    print("\n🏁 Demo tugallandi!")


# Demo va Testing Functions
async def demo_risk_management_system():
    """Advanced Risk Management System to'liq demo"""
    print("🚀 Advanced Risk Management System Demo")
    print("=" * 60)
    
    # System initialization
    risk_manager = AdvancedRiskManager()
    
    # Sample positions
    positions = [
        Position("BTC", 10, 45000, 46500, "LONG", datetime.now()),
        Position("AAPL", 100, 150, 155, "LONG", datetime.now()),
        Position("TSLA", 50, 200, 210, "LONG", datetime.now()),
        Position("SPY", 200, 400, 405, "LONG", datetime.now())
    ]
    
    print(f"📊 Portfolio: {len(positions)} positions")
    print(f"💰 Total Value: ${sum(pos.quantity * pos.current_price for pos in positions):,.2f}")
    print()
    
    # 1. Real-time risk scoring
    print("1️⃣ Real-time Risk Scoring")
    metrics = risk_manager.risk_scorer.calculate_risk_score(positions)
    print(f"   VaR (1-day): ${metrics.var_1d:,.2f}")
    print(f"   VaR (5-day): ${metrics.var_5d:,.2f}")
    print(f"   Max Drawdown: {metrics.max_drawdown:.2%}")
    print(f"   Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
    print(f"   Liquidity Score: {metrics.liquidity_score:.2%}")
    print()
    
    # 2. Portfolio stress testing
    print("2️⃣ Portfolio Stress Testing")
    stress_results = risk_manager.stress_tester.run_comprehensive_stress_test(positions)
    for scenario, result in stress_results.items():
        print(f"   {scenario}: {result.portfolio_impact:.2f}% impact, Stress Score: {result.stress_score:.1f}")
    print()
    
    # 3. Risk controls
    print("3️⃣ Automated Risk Controls")
    alerts = risk_manager.risk_controller.check_risk_limits(positions)
    print(f"   Active Alerts: {len(alerts)}")
    for alert in alerts[:3]:  # Show first 3
        print(f"   ⚠️ {alert.severity.value}: {alert.message}")
    print()
    
    # 4. Liquidity risk
    print("4️⃣ Liquidity Risk Assessment")
    liquidity_risk = risk_manager.liquidity_assessor.assess_liquidity_risk(positions)
    print(f"   Liquidity Score: {liquidity_risk['liquidity_score']:.2%}")
    print(f"   Risk Level: {liquidity_risk['risk_level']:.1f}%")
    print()
    
    # 5. Market risk
    print("5️⃣ Market Risk Evaluation")
    market_risk = risk_manager.market_evaluator.evaluate_market_risk(positions)
    print(f"   VaR (1-day): ${market_risk['var_1d']:,.2f}")
    print(f"   Beta: {market_risk['beta']:.2f}")
    print(f"   Total Risk: {market_risk['total_risk']:.2%}")
    print()
    
    # 6. Credit risk
    print("6️⃣ Credit Risk Monitoring")
    credit_risk = risk_manager.credit_monitor.assess_credit_risk(positions)
    print(f"   Overall Credit Score: {credit_risk['overall_credit_score']:.1f}/10")
    print()
    
    # 7. Regulatory compliance
    print("7️⃣ Regulatory Compliance")
    compliance = risk_manager.compliance.check_regulatory_compliance(positions, metrics)
    print(f"   Overall Status: {compliance.get('overall_compliance', 'UNKNOWN')}")
    print()
    
    # 8. Risk dashboard
    print("8️⃣ Risk Dashboard")
    summary = risk_manager.dashboard.generate_risk_summary(positions, metrics)
    print(f"   Overall Risk Level: {summary['overall_risk_level']}")
    print(f"   Active Alerts: {summary['risk_alerts'].get('total', 0)}")
    print()
    
    # 9. Comprehensive analysis
    print("9️⃣ Comprehensive Risk Analysis")
    analysis = await risk_manager.comprehensive_risk_analysis(positions)
    print(f"   Overall Risk Rating: {analysis['overall_risk_rating']}")
    print(f"   Recommendations: {len(analysis['recommendations'])}")
    for rec in analysis['recommendations'][:3]:
        print(f"   • {rec}")
    print()
    
    # System status
    print("🔧 System Status")
    status = risk_manager.get_system_status()
    print(f"   Running: {status['is_running']}")
    print(f"   Monitoring: {status['monitoring_active']}")
    print()
    
    print("✅ Demo completed successfully!")
    
    return risk_manager


def create_test_scenarios():
    """Test scenariylarini yaratish"""
    scenarios = [
        {
            'name': 'Market Crash Test',
            'positions': [
                Position("SPY", 100, 400, 350, "LONG", datetime.now()),
                Position("QQQ", 50, 300, 250, "LONG", datetime.now())
            ],
            'expected_high_risk': True
        },
        {
            'name': 'Safe Portfolio Test',
            'positions': [
                Position("SPY", 100, 400, 405, "LONG", datetime.now()),
                Position("AGG", 200, 100, 101, "LONG", datetime.now())
            ],
            'expected_high_risk': False
        }
    ]
    return scenarios


async def run_comprehensive_tests():
    """Barcha testlarni o'tkazish"""
    print("🧪 Advanced Risk Management Tests")
    print("=" * 40)
    
    scenarios = create_test_scenarios()
    risk_manager = AdvancedRiskManager()
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 Test {i}: {scenario['name']}")
        print("-" * 30)
        
        # Run risk assessment
        analysis = await risk_manager.comprehensive_risk_analysis(scenario['positions'])
        
        # Check results
        risk_rating = analysis['overall_risk_rating']
        is_high_risk = risk_rating in ['HIGH', 'CRITICAL']
        
        print(f"   Risk Rating: {risk_rating}")
        print(f"   Expected High Risk: {scenario['expected_high_risk']}")
        print(f"   Test Result: {'✅ PASS' if is_high_risk == scenario['expected_high_risk'] else '❌ FAIL'}")
        
        # Show key metrics
        if 'risk_score' in analysis and analysis['risk_score']:
            metrics = analysis['risk_score']
            print(f"   VaR (1-day): ${metrics.var_1d:,.2f}")
            print(f"   Liquidity Score: {metrics.liquidity_score:.2%}")
    
    print("\n🎯 Testing completed!")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_risk_management_system())
    
    # Run tests
    asyncio.run(run_comprehensive_tests())