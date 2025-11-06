"""
Core Risk Management Engine
===========================

Main risk management coordinator that manages all risk operations,
integrates monitoring, analytics, and compliance features.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import pandas as pd

from ..monitoring.real_time_monitor import RealTimeMonitor
from ..analytics.analytics_engine import AnalyticsEngine
from ..compliance.compliance_engine import ComplianceEngine
from ..core.position_monitor import PositionMonitor
from ..core.risk_limits import RiskLimits
from ..utils.risk_alerts import RiskAlertSystem
from ..utils.data_manager import RiskDataManager

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk severity levels"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class RiskReport:
    """Risk assessment report structure"""
    timestamp: datetime
    portfolio_value: float
    total_var: float
    stress_test_results: Dict[str, float]
    position_exposures: Dict[str, float]
    risk_level: RiskLevel
    alerts: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class RiskMetrics:
    """Current risk metrics snapshot"""
    timestamp: datetime
    var_1d_95: float
    var_1d_99: float
    expected_shortfall: float
    portfolio_beta: float
    sharpe_ratio: float
    max_drawdown: float
    volatility: float
    correlation_risk: float
    liquidity_risk: float

class RiskManager:
    """
    Main risk management coordinator
    
    Integrates all risk management components:
    - Real-time monitoring
    - Risk analytics
    - Compliance checking
    - Alert management
    - Reporting
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.running = False
        self.last_assessment = None
        
        # Initialize components
        self.data_manager = RiskDataManager(config.get('data_config', {}))
        self.position_monitor = PositionMonitor(config.get('position_config', {}))
        self.risk_limits = RiskLimits(config.get('limits_config', {}))
        self.real_time_monitor = RealTimeMonitor(config.get('monitor_config', {}))
        self.analytics_engine = AnalyticsEngine(config.get('analytics_config', {}))
        self.compliance_engine = ComplianceEngine(config.get('compliance_config', {}))
        self.alert_system = RiskAlertSystem(config.get('alert_config', {}))
        
        # Risk state
        self.current_positions = {}
        self.current_portfolio = {}
        self.risk_metrics = None
        self.active_alerts = []
        
        # Performance tracking
        self.assessment_history = []
        self.risk_violations = []
        
    async def initialize(self):
        """Initialize all risk management components"""
        try:
            logger.info("Risk Management System initializing...")
            
            # Initialize data connections
            await self.data_manager.initialize()
            
            # Setup monitoring callbacks
            self.real_time_monitor.add_position_callback(self._handle_position_update)
            self.real_time_monitor.add_portfolio_callback(self._handle_portfolio_update)
            
            # Setup alert handlers
            self.alert_system.add_alert_callback(self._handle_alert)
            
            # Load initial data
            await self._load_portfolio_data()
            
            logger.info("Risk Management System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Risk Management System: {e}")
            raise
    
    async def start_monitoring(self):
        """Start real-time risk monitoring"""
        if self.running:
            return
            
        self.running = True
        logger.info("Starting real-time risk monitoring...")
        
        # Start monitoring components
        await self.real_time_monitor.start()
        await self.position_monitor.start()
        
        # Start risk assessment loop
        asyncio.create_task(self._risk_assessment_loop())
        
    async def stop_monitoring(self):
        """Stop risk monitoring"""
        self.running = False
        logger.info("Stopping risk monitoring...")
        
        await self.real_time_monitor.stop()
        await self.position_monitor.stop()
        
    async def assess_portfolio_risk(self) -> RiskReport:
        """
        Perform comprehensive portfolio risk assessment
        
        Returns:
            RiskReport: Complete risk assessment
        """
        try:
            current_time = datetime.now()
            
            # Get current market data
            market_data = await self.data_manager.get_current_market_data()
            
            # Calculate risk metrics
            positions = await self.position_monitor.get_current_positions()
            portfolio_value = await self._calculate_portfolio_value()
            
            var_result = await self.analytics_engine.calculate_var(
                positions, 
                market_data,
                confidence_levels=[0.95, 0.99]
            )
            
            # Stress testing
            stress_results = await self.analytics_engine.run_stress_tests(
                positions,
                market_data,
                scenarios=['market_crash', 'volatility_spike', 'liquidity_crisis']
            )
            
            # Check limits and compliance
            limit_violations = await self.risk_limits.check_limits(positions)
            compliance_status = await self.compliance_engine.check_compliance()
            
            # Generate alerts for violations
            alerts = []
            if limit_violations:
                alerts.extend(self._create_limit_alerts(limit_violations))
                
            if compliance_status.violations:
                alerts.extend(self._create_compliance_alerts(compliance_status.violations))
            
            # Determine overall risk level
            risk_level = self._assess_overall_risk_level(
                var_result, stress_results, limit_violations, compliance_status
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                var_result, stress_results, limit_violations, alerts
            )
            
            # Create risk metrics snapshot
            self.risk_metrics = RiskMetrics(
                timestamp=current_time,
                var_1d_95=var_result.get('var_95', 0),
                var_1d_99=var_result.get('var_99', 0),
                expected_shortfall=var_result.get('expected_shortfall', 0),
                portfolio_beta=await self._calculate_portfolio_beta(positions, market_data),
                sharpe_ratio=await self._calculate_sharpe_ratio(positions, market_data),
                max_drawdown=await self._calculate_max_drawdown(positions),
                volatility=var_result.get('volatility', 0),
                correlation_risk=await self._calculate_correlation_risk(positions),
                liquidity_risk=await self._calculate_liquidity_risk(positions)
            )
            
            # Create risk report
            risk_report = RiskReport(
                timestamp=current_time,
                portfolio_value=portfolio_value,
                total_var=var_result.get('var_95', 0),
                stress_test_results=stress_results,
                position_exposures=self._calculate_position_exposures(positions),
                risk_level=risk_level,
                alerts=alerts,
                recommendations=recommendations
            )
            
            # Store assessment
            self.assessment_history.append(risk_report)
            self.last_assessment = risk_report
            
            # Send alerts if needed
            if alerts:
                await self.alert_system.send_alerts(alerts)
            
            logger.info(f"Risk assessment completed. Risk level: {risk_level.value}")
            
            return risk_report
            
        except Exception as e:
            logger.error(f"Error in portfolio risk assessment: {e}")
            raise
    
    async def execute_risk_controls(self, positions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute automated risk control actions
        
        Args:
            positions: Current position data
            
        Returns:
            Dict containing control actions taken
        """
        control_actions = {}
        
        try:
            # Check for position size violations
            size_violations = await self.risk_limits.check_position_sizes(positions)
            if size_violations:
                # Trigger position size reduction
                control_actions['position_reductions'] = await self._reduce_positions(
                    size_violations
                )
            
            # Check for stop-loss triggers
            stop_loss_triggers = await self._check_stop_losses(positions)
            if stop_loss_triggers:
                control_actions['stop_losses'] = await self._execute_stop_losses(
                    stop_loss_triggers
                )
            
            # Check for drawdown limits
            drawdown_violations = await self._check_drawdown_limits()
            if drawdown_violations:
                control_actions['drawdown_actions'] = await self._execute_drawdown_actions(
                    drawdown_violations
                )
            
            # Emergency controls for critical situations
            if self.risk_metrics and self.risk_metrics.risk_level == RiskLevel.CRITICAL:
                emergency_actions = await self._execute_emergency_controls(positions)
                control_actions.update(emergency_actions)
            
            logger.info(f"Risk controls executed: {list(control_actions.keys())}")
            
            return control_actions
            
        except Exception as e:
            logger.error(f"Error executing risk controls: {e}")
            return {}
    
    async def get_risk_metrics(self) -> Optional[RiskMetrics]:
        """Get current risk metrics"""
        return self.risk_metrics
    
    async def get_risk_history(self, hours: int = 24) -> List[RiskReport]:
        """Get risk assessment history for specified period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [report for report in self.assessment_history 
                if report.timestamp >= cutoff_time]
    
    async def generate_risk_report(self, format_type: str = 'json') -> str:
        """Generate formatted risk report"""
        if not self.last_assessment:
            await self.assess_portfolio_risk()
        
        report_data = {
            'timestamp': self.last_assessment.timestamp.isoformat(),
            'summary': {
                'risk_level': self.last_assessment.risk_level.value,
                'portfolio_value': self.last_assessment.portfolio_value,
                'var_1d': self.last_assessment.total_var,
                'active_alerts': len(self.last_assessment.alerts)
            },
            'risk_metrics': {
                'var_1d_95': self.risk_metrics.var_1d_95 if self.risk_metrics else 0,
                'var_1d_99': self.risk_metrics.var_1d_99 if self.risk_metrics else 0,
                'expected_shortfall': self.risk_metrics.expected_shortfall if self.risk_metrics else 0,
                'portfolio_beta': self.risk_metrics.portfolio_beta if self.risk_metrics else 0,
                'sharpe_ratio': self.risk_metrics.sharpe_ratio if self.risk_metrics else 0,
                'max_drawdown': self.risk_metrics.max_drawdown if self.risk_metrics else 0,
                'volatility': self.risk_metrics.volatility if self.risk_metrics else 0
            },
            'stress_tests': self.last_assessment.stress_test_results,
            'alerts': self.last_assessment.alerts,
            'recommendations': self.last_assessment.recommendations
        }
        
        if format_type.lower() == 'json':
            return json.dumps(report_data, indent=2, default=str)
        else:
            # Add HTML/other format generation here
            return str(report_data)
    
    # Private helper methods
    
    async def _risk_assessment_loop(self):
        """Continuous risk assessment loop"""
        while self.running:
            try:
                await self.assess_portfolio_risk()
                await asyncio.sleep(self.config.get('assessment_interval', 60))  # seconds
            except Exception as e:
                logger.error(f"Error in risk assessment loop: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def _load_portfolio_data(self):
        """Load initial portfolio data"""
        self.current_positions = await self.position_monitor.get_current_positions()
        self.current_portfolio = await self._calculate_portfolio_value()
    
    async def _calculate_portfolio_value(self) -> float:
        """Calculate total portfolio value"""
        total_value = 0
        positions = self.current_positions
        
        for symbol, position in positions.items():
            if 'quantity' in position and 'current_price' in position:
                quantity = position['quantity']
                price = position['current_price']
                total_value += quantity * price
        
        return total_value
    
    def _assess_overall_risk_level(self, var_result: Dict, stress_results: Dict,
                                 limit_violations: List, compliance_status) -> RiskLevel:
        """Determine overall risk level from all metrics"""
        risk_factors = []
        
        # VaR assessment
        if var_result.get('var_95', 0) > self.config.get('var_threshold', 1000000):
            risk_factors.append(RiskLevel.HIGH)
        
        # Stress test results
        if any(impact < -0.2 for impact in stress_results.values()):
            risk_factors.append(RiskLevel.HIGH)
        
        # Limit violations
        if len(limit_violations) > 0:
            risk_factors.append(RiskLevel.MEDIUM)
        
        # Compliance violations
        if compliance_status.violations:
            risk_factors.append(RiskLevel.HIGH)
        
        # Determine final level
        if RiskLevel.CRITICAL in risk_factors:
            return RiskLevel.CRITICAL
        elif RiskLevel.HIGH in risk_factors:
            return RiskLevel.HIGH
        elif RiskLevel.MEDIUM in risk_factors:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _create_limit_alerts(self, violations: List[Dict]) -> List[Dict]:
        """Create alerts for limit violations"""
        alerts = []
        for violation in violations:
            alert = {
                'type': 'limit_violation',
                'severity': AlertSeverity.WARNING.value,
                'timestamp': datetime.now().isoformat(),
                'message': f"Limit violation: {violation.get('description', 'Unknown')}",
                'details': violation
            }
            alerts.append(alert)
        return alerts
    
    def _create_compliance_alerts(self, violations: List[Dict]) -> List[Dict]:
        """Create alerts for compliance violations"""
        alerts = []
        for violation in violations:
            alert = {
                'type': 'compliance_violation',
                'severity': AlertSeverity.ERROR.value,
                'timestamp': datetime.now().isoformat(),
                'message': f"Compliance violation: {violation.get('description', 'Unknown')}",
                'details': violation
            }
            alerts.append(alert)
        return alerts
    
    def _generate_recommendations(self, var_result: Dict, stress_results: Dict,
                                limit_violations: List, alerts: List) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        # VaR-based recommendations
        if var_result.get('var_95', 0) > self.config.get('var_threshold', 1000000):
            recommendations.append("Portfolio VaR exceeded threshold. Consider reducing position sizes.")
        
        # Stress test recommendations
        if any(impact < -0.3 for impact in stress_results.values()):
            recommendations.append("High stress test losses detected. Implement additional risk controls.")
        
        # Limit recommendations
        if limit_violations:
            recommendations.append("Multiple limit violations detected. Review position sizing strategy.")
        
        # Correlation recommendations
        recommendations.append("Regularly review correlation matrix and diversify positions.")
        
        return recommendations
    
    async def _calculate_portfolio_beta(self, positions: Dict, market_data: Dict) -> float:
        """Calculate portfolio beta"""
        try:
            # Simplified beta calculation - would need actual market returns
            total_value = sum(pos.get('value', 0) for pos in positions.values())
            if total_value == 0:
                return 0
            
            # Weight positions by value
            weighted_betas = []
            for symbol, position in positions.items():
                if 'beta' in market_data.get(symbol, {}):
                    weight = position.get('value', 0) / total_value
                    beta = market_data[symbol]['beta']
                    weighted_betas.append(weight * beta)
            
            return sum(weighted_betas) if weighted_betas else 0
        except Exception:
            return 0
    
    async def _calculate_sharpe_ratio(self, positions: Dict, market_data: Dict) -> float:
        """Calculate portfolio Sharpe ratio"""
        try:
            # Simplified calculation
            total_returns = sum(pos.get('returns', 0) for pos in positions.values())
            total_risk = sum(pos.get('volatility', 0) for pos in positions.values())
            
            if total_risk == 0:
                return 0
                
            return total_returns / total_risk
        except Exception:
            return 0
    
    async def _calculate_max_drawdown(self, positions: Dict) -> float:
        """Calculate maximum drawdown"""
        # Simplified calculation
        peak = max(pos.get('peak_value', 0) for pos in positions.values())
        current = sum(pos.get('current_value', 0) for pos in positions.values())
        
        if peak == 0:
            return 0
            
        return (peak - current) / peak
    
    async def _calculate_correlation_risk(self, positions: Dict) -> float:
        """Calculate correlation-based risk"""
        # Simplified correlation risk metric
        correlations = []
        for pos in positions.values():
            if 'correlation' in pos:
                correlations.append(abs(pos['correlation']))
        
        return np.mean(correlations) if correlations else 0
    
    async def _calculate_liquidity_risk(self, positions: Dict) -> float:
        """Calculate liquidity risk"""
        liquidity_risks = []
        for pos in positions.values():
            if 'liquidity_ratio' in pos:
                liquidity_risks.append(1 / max(pos['liquidity_ratio'], 0.01))
        
        return np.mean(liquidity_risks) if liquidity_risks else 0
    
    def _calculate_position_exposures(self, positions: Dict) -> Dict[str, float]:
        """Calculate position exposures by asset class"""
        exposures = {}
        for symbol, position in positions.items():
            asset_class = position.get('asset_class', 'unknown')
            exposure = position.get('value', 0)
            
            if asset_class not in exposures:
                exposures[asset_class] = 0
            exposures[asset_class] += exposure
        
        return exposures
    
    # Event handlers
    
    async def _handle_position_update(self, position_data: Dict):
        """Handle real-time position updates"""
        self.current_positions.update(position_data)
    
    async def _handle_portfolio_update(self, portfolio_data: Dict):
        """Handle portfolio updates"""
        self.current_portfolio.update(portfolio_data)
    
    async def _handle_alert(self, alert: Dict):
        """Handle risk alerts"""
        self.active_alerts.append(alert)
        logger.warning(f"Risk Alert: {alert.get('message', 'Unknown alert')}")
    
    # Risk control methods (stub implementations)
    
    async def _check_stop_losses(self, positions: Dict) -> List[Dict]:
        """Check for stop-loss triggers"""
        triggers = []
        for symbol, position in positions.items():
            current_price = position.get('current_price', 0)
            stop_loss = position.get('stop_loss', 0)
            
            if stop_loss > 0 and current_price <= stop_loss:
                triggers.append({
                    'symbol': symbol,
                    'trigger_price': stop_loss,
                    'current_price': current_price,
                    'action': 'close_position'
                })
        
        return triggers
    
    async def _check_drawdown_limits(self) -> List[Dict]:
        """Check for drawdown limit violations"""
        violations = []
        
        # Current drawdown
        current_drawdown = await self._calculate_max_drawdown(self.current_positions)
        max_drawdown_limit = self.config.get('max_drawdown_limit', 0.15)
        
        if current_drawdown > max_drawdown_limit:
            violations.append({
                'type': 'drawdown_limit',
                'current_drawdown': current_drawdown,
                'limit': max_drawdown_limit,
                'excess': current_drawdown - max_drawdown_limit
            })
        
        return violations
    
    async def _reduce_positions(self, violations: List[Dict]) -> List[Dict]:
        """Execute position reductions"""
        actions = []
        # Implementation would depend on trading system integration
        return actions
    
    async def _execute_stop_losses(self, triggers: List[Dict]) -> List[Dict]:
        """Execute stop-loss orders"""
        actions = []
        # Implementation would depend on trading system integration
        return actions
    
    async def _execute_drawdown_actions(self, violations: List[Dict]) -> List[Dict]:
        """Execute drawdown control actions"""
        actions = []
        # Implementation would reduce positions across portfolio
        return actions
    
    async def _execute_emergency_controls(self, positions: Dict) -> List[Dict]:
        """Execute emergency risk controls"""
        actions = []
        # Implementation would close all or most positions
        return actions