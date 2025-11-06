"""
Compliance Engine
================

Regulatory compliance monitoring and reporting system for risk management.
Ensures adherence to financial regulations, risk limits, and reporting requirements.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)

class ComplianceLevel(Enum):
    """Compliance severity levels"""
    INFO = "info"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"

class RegulationType(Enum):
    """Types of financial regulations"""
    CAPITAL_REQUIREMENTS = "capital_requirements"
    LEVERAGE_RATIO = "leverage_ratio"
    LIQUIDITY_COVERAGE = "liquidity_coverage"
    NET_STABLE_FUNDING = "net_stable_funding"
    CONCENTRATION_LIMITS = "concentration_limits"
    REPORTING_REQUIREMENTS = "reporting_requirements"
    RISK_DISCLOSURE = "risk_disclosure"

@dataclass
class ComplianceRule:
    """Individual compliance rule definition"""
    rule_id: str
    name: str
    regulation_type: RegulationType
    description: str
    threshold_value: float
    comparison_operator: str  # 'gt', 'lt', 'eq', 'gte', 'lte'
    measurement_period: str  # 'daily', 'weekly', 'monthly', 'quarterly'
    severity: ComplianceLevel
    auto_remediation: bool = False
    remediation_action: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ComplianceViolation:
    """Compliance violation record"""
    rule_id: str
    rule_name: str
    violation_type: RegulationType
    current_value: float
    threshold_value: float
    severity: ComplianceLevel
    timestamp: datetime
    description: str
    affected_positions: List[str] = field(default_factory=list)
    remediation_suggested: bool = False
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class ComplianceReport:
    """Compliance status report"""
    timestamp: datetime
    overall_status: ComplianceLevel
    violations: List[ComplianceViolation]
    warnings: List[str]
    compliance_score: float
    rules_checked: int
    violations_count: int
    critical_violations: int
    recommendations: List[str] = field(default_factory=list)

class ComplianceEngine:
    """
    Regulatory compliance monitoring and reporting engine
    
    Monitors compliance with:
    - Capital requirements (Basel III)
    - Leverage ratios
    - Liquidity coverage ratios
    - Concentration limits
    - Regulatory reporting requirements
    - Risk disclosure requirements
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.compliance_rules: List[ComplianceRule] = []
        self.violation_history: List[ComplianceViolation] = []
        
        # Initialize default compliance rules
        self._initialize_default_rules()
        
        # Compliance state
        self.last_compliance_check = None
        self.compliance_breaches = 0
        self.remediation_actions = []
        
    def _initialize_default_rules(self):
        """Initialize default regulatory compliance rules"""
        
        # Capital Requirements (Basel III)
        self.add_rule(ComplianceRule(
            rule_id="basel3_common_equity_ratio",
            name="Common Equity Tier 1 Ratio",
            regulation_type=RegulationType.CAPITAL_REQUIREMENTS,
            description="Minimum Common Equity Tier 1 capital ratio of 4.5%",
            threshold_value=0.045,
            comparison_operator="gte",
            measurement_period="quarterly",
            severity=ComplianceLevel.VIOLATION,
            auto_remediation=True,
            remediation_action="increase_capital_or_reduce_risky_assets"
        ))
        
        self.add_rule(ComplianceRule(
            rule_id="basel3_total_capital_ratio",
            name="Total Capital Ratio",
            regulation_type=RegulationType.CAPITAL_REQUIREMENTS,
            description="Minimum Total Capital ratio of 8%",
            threshold_value=0.08,
            comparison_operator="gte",
            measurement_period="quarterly",
            severity=ComplianceLevel.VIOLATION,
            auto_remediation=True,
            remediation_action="increase_capital_or_reduce_risky_assets"
        ))
        
        self.add_rule(ComplianceRule(
            rule_id="basel3_conservation_buffer",
            name="Capital Conservation Buffer",
            regulation_type=RegulationType.CAPITAL_REQUIREMENTS,
            description="Capital Conservation Buffer of 2.5%",
            threshold_value=0.025,
            comparison_operator="gte",
            measurement_period="quarterly",
            severity=ComplianceLevel.VIOLATION,
            auto_remediation=True,
            remediation_action="increase_capital"
        ))
        
        # Leverage Ratio
        self.add_rule(ComplianceRule(
            rule_id="basel3_leverage_ratio",
            name="Leverage Ratio",
            regulation_type=RegulationType.LEVERAGE_RATIO,
            description="Minimum leverage ratio of 3%",
            threshold_value=0.03,
            comparison_operator="gte",
            measurement_period="quarterly",
            severity=ComplianceLevel.VIOLATION,
            auto_remediation=True,
            remediation_action="reduce_leverage"
        ))
        
        # Liquidity Coverage Ratio (LCR)
        self.add_rule(ComplianceRule(
            rule_id="basel3_lcr",
            name="Liquidity Coverage Ratio",
            regulation_type=RegulationType.LIQUIDITY_COVERAGE,
            description="Minimum LCR of 100%",
            threshold_value=1.0,
            comparison_operator="gte",
            measurement_period="monthly",
            severity=ComplianceLevel.VIOLATION,
            auto_remediation=True,
            remediation_action="increase_high_quality_liquid_assets"
        ))
        
        # Net Stable Funding Ratio (NSFR)
        self.add_rule(ComplianceRule(
            rule_id="basel3_nsfr",
            name="Net Stable Funding Ratio",
            regulation_type=RegulationType.NET_STABLE_FUNDING,
            description="Minimum NSFR of 100%",
            threshold_value=1.0,
            comparison_operator="gte",
            measurement_period="quarterly",
            severity=ComplianceLevel.VIOLATION,
            auto_remediation=True,
            remediation_action="improve_funding_structure"
        ))
        
        # Concentration Limits
        self.add_rule(ComplianceRule(
            rule_id="single_counterparty_limit",
            name="Single Counterparty Exposure",
            regulation_type=RegulationType.CONCENTRATION_LIMITS,
            description="Maximum 25% exposure to single counterparty",
            threshold_value=0.25,
            comparison_operator="lte",
            measurement_period="daily",
            severity=ComplianceLevel.VIOLATION,
            auto_remediation=True,
            remediation_action="reduce_exposure_to_counterparty"
        ))
        
        self.add_rule(ComplianceRule(
            rule_id="sector_concentration_limit",
            name="Sector Concentration Limit",
            regulation_type=RegulationType.CONCENTRATION_LIMITS,
            description="Maximum 40% exposure to single sector",
            threshold_value=0.40,
            comparison_operator="lte",
            measurement_period="daily",
            severity=ComplianceLevel.WARNING,
            auto_remediation=False,
            remediation_action="diversify_sector_exposure"
        ))
        
        self.add_rule(ComplianceRule(
            rule_id="geographic_concentration_limit",
            name="Geographic Concentration Limit",
            regulation_type=RegulationType.CONCENTRATION_LIMITS,
            description="Maximum 50% exposure to single country",
            threshold_value=0.50,
            comparison_operator="lte",
            measurement_period="daily",
            severity=ComplianceLevel.WARNING,
            auto_remediation=False,
            remediation_action="diversify_geographic_exposure"
        ))
        
        # Risk Disclosure Requirements
        self.add_rule(ComplianceRule(
            rule_id="var_disclosure",
            name="VaR Disclosure",
            regulation_type=RegulationType.RISK_DISCLOSURE,
            description="Daily VaR must be disclosed to public",
            threshold_value=1,
            comparison_operator="gte",
            measurement_period="daily",
            severity=ComplianceLevel.INFO,
            auto_remediation=False,
            remediation_action="publish_var_disclosure"
        ))
        
        self.add_rule(ComplianceRule(
            rule_id="stress_test_disclosure",
            name="Stress Test Disclosure",
            regulation_type=RegulationType.RISK_DISCLOSURE,
            description="Stress test results must be disclosed annually",
            threshold_value=1,
            comparison_operator="gte",
            measurement_period="yearly",
            severity=ComplianceLevel.INFO,
            auto_remediation=False,
            remediation_action="publish_stress_test_results"
        ))
        
        logger.info(f"Initialized {len(self.compliance_rules)} default compliance rules")
    
    def add_rule(self, rule: ComplianceRule):
        """Add a new compliance rule"""
        self.compliance_rules.append(rule)
        logger.info(f"Added compliance rule: {rule.name}")
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a compliance rule"""
        original_count = len(self.compliance_rules)
        self.compliance_rules = [rule for rule in self.compliance_rules if rule.rule_id != rule_id]
        
        if len(self.compliance_rules) < original_count:
            logger.info(f"Removed compliance rule: {rule_id}")
            return True
        return False
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing compliance rule"""
        for rule in self.compliance_rules:
            if rule.rule_id == rule_id:
                for key, value in updates.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                logger.info(f"Updated compliance rule: {rule_id}")
                return True
        return False
    
    async def check_compliance(self, positions: Dict[str, Any],
                             portfolio_metrics: Dict[str, Any] = None,
                             market_data: Dict[str, Any] = None) -> ComplianceReport:
        """
        Check compliance against all rules
        
        Args:
            positions: Current position data
            portfolio_metrics: Current portfolio metrics
            market_data: Current market data
            
        Returns:
            Compliance report with violations and recommendations
        """
        try:
            start_time = datetime.now()
            
            violations = []
            warnings = []
            rules_checked = 0
            
            for rule in self.compliance_rules:
                if await self._check_single_rule(rule, positions, portfolio_metrics, market_data):
                    violation = await self._create_violation(rule, positions, portfolio_metrics)
                    violations.append(violation)
                else:
                    rules_checked += 1
            
            # Filter for active violations (not resolved)
            active_violations = [v for v in violations if not v.resolved]
            
            # Calculate compliance score
            compliance_score = await self._calculate_compliance_score(len(self.compliance_rules), active_violations)
            
            # Determine overall status
            overall_status = self._determine_overall_status(active_violations)
            
            # Count critical violations
            critical_violations = len([v for v in active_violations if v.severity == ComplianceLevel.CRITICAL])
            
            # Generate warnings and recommendations
            warnings = await self._generate_warnings(active_violations)
            recommendations = await self._generate_recommendations(active_violations)
            
            # Check for auto-remediation
            await self._check_auto_remediation(active_violations)
            
            # Add to violation history
            self.violation_history.extend(active_violations)
            
            report = ComplianceReport(
                timestamp=start_time,
                overall_status=overall_status,
                violations=active_violations,
                warnings=warnings,
                compliance_score=compliance_score,
                rules_checked=rules_checked,
                violations_count=len(active_violations),
                critical_violations=critical_violations,
                recommendations=recommendations
            )
            
            self.last_compliance_check = start_time
            
            logger.info(f"Compliance check completed: {len(active_violations)} violations, "
                       f"score: {compliance_score:.1f}%")
            
            return report
            
        except Exception as e:
            logger.error(f"Error checking compliance: {e}")
            raise
    
    async def _check_single_rule(self, rule: ComplianceRule,
                               positions: Dict[str, Any],
                               portfolio_metrics: Dict[str, Any] = None,
                               market_data: Dict[str, Any] = None) -> bool:
        """Check a single compliance rule"""
        try:
            current_value = await self._get_measurement_value(rule, positions, portfolio_metrics, market_data)
            
            return await self._evaluate_rule(current_value, rule)
            
        except Exception as e:
            logger.error(f"Error checking rule {rule.rule_id}: {e}")
            return False
    
    async def _get_measurement_value(self, rule: ComplianceRule,
                                   positions: Dict[str, Any],
                                   portfolio_metrics: Dict[str, Any] = None,
                                   market_data: Dict[str, Any] = None) -> float:
        """Get measurement value for a specific rule"""
        
        if rule.regulation_type == RegulationType.CAPITAL_REQUIREMENTS:
            # Simplified capital ratio calculation
            return self._calculate_capital_ratio(positions, portfolio_metrics)
        
        elif rule.regulation_type == RegulationType.LEVERAGE_RATIO:
            return self._calculate_leverage_ratio(positions, portfolio_metrics)
        
        elif rule.regulation_type == RegulationType.LIQUIDITY_COVERAGE:
            return self._calculate_lcr(positions, portfolio_metrics)
        
        elif rule.regulation_type == RegulationType.NET_STABLE_FUNDING:
            return self._calculate_nsfr(positions, portfolio_metrics)
        
        elif rule.regulation_type == RegulationType.CONCENTRATION_LIMITS:
            return self._calculate_concentration_ratio(rule, positions)
        
        elif rule.regulation_type == RegulationType.RISK_DISCLOSURE:
            # Check if disclosure has been made
            return 1.0 if self._check_disclosure_status(rule) else 0.0
        
        else:
            return 0.0
    
    async def _evaluate_rule(self, current_value: float, rule: ComplianceRule) -> bool:
        """Evaluate if rule threshold is violated"""
        threshold = rule.threshold_value
        
        if rule.comparison_operator == "gt":
            return current_value > threshold
        elif rule.comparison_operator == "gte":
            return current_value >= threshold
        elif rule.comparison_operator == "lt":
            return current_value < threshold
        elif rule.comparison_operator == "lte":
            return current_value <= threshold
        elif rule.comparison_operator == "eq":
            return abs(current_value - threshold) < 0.001
        else:
            return False
    
    async def _create_violation(self, rule: ComplianceRule,
                              positions: Dict[str, Any],
                              portfolio_metrics: Dict[str, Any] = None) -> ComplianceViolation:
        """Create violation record for rule breach"""
        current_value = await self._get_measurement_value(rule, positions, portfolio_metrics)
        
        # Find affected positions for concentration violations
        affected_positions = []
        if rule.regulation_type == RegulationType.CONCENTRATION_LIMITS:
            affected_positions = await self._identify_concentration_violations(rule, positions)
        
        return ComplianceViolation(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            violation_type=rule.regulation_type,
            current_value=current_value,
            threshold_value=rule.threshold_value,
            severity=rule.severity,
            timestamp=datetime.now(),
            description=f"{rule.name}: {current_value:.4f} vs threshold {rule.threshold_value:.4f}",
            affected_positions=affected_positions,
            remediation_suggested=rule.auto_remediation
        )
    
    # Simplified measurement calculations
    
    def _calculate_capital_ratio(self, positions: Dict[str, Any],
                               portfolio_metrics: Dict[str, Any] = None) -> float:
        """Calculate capital ratio (simplified)"""
        # This would use actual capital and risk-weighted assets
        # For demonstration, using portfolio metrics
        
        if portfolio_metrics and 'total_capital' in portfolio_metrics:
            capital = portfolio_metrics['total_capital']
            risk_weighted_assets = portfolio_metrics.get('risk_weighted_assets', capital * 10)
            return capital / risk_weighted_assets if risk_weighted_assets > 0 else 0
        
        # Simplified calculation
        total_value = sum(pos.get('market_value', 0) for pos in positions.values())
        assumed_capital = total_value * 0.12  # Assume 12% capital ratio
        risk_weighted_assets = total_value * 0.8  # Assume 80% risk weighting
        
        return assumed_capital / risk_weighted_assets if risk_weighted_assets > 0 else 0
    
    def _calculate_leverage_ratio(self, positions: Dict[str, Any],
                                portfolio_metrics: Dict[str, Any] = None) -> float:
        """Calculate leverage ratio (simplified)"""
        total_exposure = sum(abs(pos.get('market_value', 0)) for pos in positions.values())
        
        if portfolio_metrics and 'tier1_capital' in portfolio_metrics:
            tier1_capital = portfolio_metrics['tier1_capital']
            return tier1_capital / total_exposure if total_exposure > 0 else 0
        
        # Simplified calculation
        tier1_capital = total_exposure * 0.05  # Assume 5% Tier 1 capital
        return tier1_capital / total_exposure if total_exposure > 0 else 0
    
    def _calculate_lcr(self, positions: Dict[str, Any],
                      portfolio_metrics: Dict[str, Any] = None) -> float:
        """Calculate Liquidity Coverage Ratio (simplified)"""
        # Simplified HQLA calculation
        total_value = sum(pos.get('market_value', 0) for pos in positions.values())
        
        # Assume some portion is HQLA
        hqla = total_value * 0.3  # Assume 30% is HQLA
        
        # Assume some net cash outflows
        net_cash_outflows = total_value * 0.4  # Assume 40% net outflows
        
        return hqla / net_cash_outflows if net_cash_outflows > 0 else 0
    
    def _calculate_nsfr(self, positions: Dict[str, Any],
                       portfolio_metrics: Dict[str, Any] = None) -> float:
        """Calculate Net Stable Funding Ratio (simplified)"""
        total_value = sum(pos.get('market_value', 0) for pos in positions.values())
        
        # Simplified NSFR calculation
        available_stable_funding = total_value * 0.8  # Assume 80% stable funding
        required_stable_funding = total_value * 0.9  # Assume 90% requirement
        
        return available_stable_funding / required_stable_funding if required_stable_funding > 0 else 0
    
    def _calculate_concentration_ratio(self, rule: ComplianceRule,
                                     positions: Dict[str, Any]) -> float:
        """Calculate concentration ratio"""
        total_value = sum(abs(pos.get('market_value', 0)) for pos in positions.values())
        
        if total_value == 0:
            return 0
        
        if rule.rule_id == "single_counterparty_limit":
            # Find maximum single position
            max_position = max(abs(pos.get('market_value', 0)) for pos in positions.values())
            return max_position / total_value
        
        elif rule.rule_id == "sector_concentration_limit":
            # Calculate sector concentrations (simplified)
            sector_exposures = {}
            for position in positions.values():
                asset_class = position.get('asset_class', 'unknown')
                value = abs(position.get('market_value', 0))
                
                if asset_class not in sector_exposures:
                    sector_exposures[asset_class] = 0
                sector_exposures[asset_class] += value
            
            max_sector_exposure = max(sector_exposures.values()) if sector_exposures else 0
            return max_sector_exposure / total_value
        
        elif rule.rule_id == "geographic_concentration_limit":
            # Calculate geographic concentrations (simplified)
            # This would require geographic data
            return 0.3  # Placeholder
        
        return 0
    
    def _check_disclosure_status(self, rule: ComplianceRule) -> bool:
        """Check if required disclosure has been made"""
        # This would check actual disclosure status
        # For demonstration, assuming disclosures are made
        return True
    
    async def _identify_concentration_violations(self, rule: ComplianceRule,
                                               positions: Dict[str, Any]) -> List[str]:
        """Identify positions causing concentration violations"""
        affected_positions = []
        total_value = sum(abs(pos.get('market_value', 0)) for pos in positions.values())
        
        if total_value == 0:
            return affected_positions
        
        for symbol, position in positions.items():
            position_value = abs(position.get('market_value', 0))
            concentration = position_value / total_value
            
            if rule.rule_id == "single_counterparty_limit" and concentration > rule.threshold_value:
                affected_positions.append(symbol)
            elif rule.rule_id == "sector_concentration_limit":
                # This would check sector aggregation
                if concentration > 0.1:  # Simplified threshold
                    affected_positions.append(symbol)
        
        return affected_positions
    
    async def _calculate_compliance_score(self, total_rules: int, violations: List[ComplianceViolation]) -> float:
        """Calculate overall compliance score (0-100)"""
        if total_rules == 0:
            return 100.0
        
        # Weight violations by severity
        violation_weights = {
            ComplianceLevel.CRITICAL: 20,
            ComplianceLevel.VIOLATION: 15,
            ComplianceLevel.WARNING: 10,
            ComplianceLevel.INFO: 5
        }
        
        total_weight = sum(violation_weights.get(v.severity, 0) for v in violations)
        max_possible_weight = total_rules * 20  # Worst case: all rules have critical violations
        
        if max_possible_weight == 0:
            return 100.0
        
        compliance_score = max(0, 100 - (total_weight / max_possible_weight) * 100)
        return compliance_score
    
    def _determine_overall_status(self, violations: List[ComplianceViolation]) -> ComplianceLevel:
        """Determine overall compliance status"""
        if not violations:
            return ComplianceLevel.INFO
        
        # Check for critical violations
        critical_violations = [v for v in violations if v.severity == ComplianceLevel.CRITICAL]
        if critical_violations:
            return ComplianceLevel.CRITICAL
        
        # Check for violations
        regular_violations = [v for v in violations if v.severity == ComplianceLevel.VIOLATION]
        if regular_violations:
            return ComplianceLevel.VIOLATION
        
        # Check for warnings
        warnings = [v for v in violations if v.severity == ComplianceLevel.WARNING]
        if warnings:
            return ComplianceLevel.WARNING
        
        return ComplianceLevel.INFO
    
    async def _generate_warnings(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate compliance warnings"""
        warnings = []
        
        # Count violations by type
        violation_types = {}
        for violation in violations:
            violation_type = violation.violation_type.value
            violation_types[violation_type] = violation_types.get(violation_type, 0) + 1
        
        # Generate warnings based on violation patterns
        if violation_types.get('concentration_limits', 0) > 0:
            warnings.append("Multiple concentration limit violations detected. Review diversification strategy.")
        
        if violation_types.get('liquidity_coverage', 0) > 0:
            warnings.append("Liquidity coverage ratio below minimum. Consider increasing HQLA holdings.")
        
        if violation_types.get('capital_requirements', 0) > 0:
            warnings.append("Capital requirements not met. Review capital allocation and risk management.")
        
        return warnings
    
    async def _generate_recommendations(self, violations: List[ComplianceViolation]) -> List[str]:
        """Generate remediation recommendations"""
        recommendations = []
        
        # Group violations by regulation type
        by_regulation = {}
        for violation in violations:
            reg_type = violation.violation_type.value
            if reg_type not in by_regulation:
                by_regulation[reg_type] = []
            by_regulation[reg_type].append(violation)
        
        # Generate specific recommendations
        if 'capital_requirements' in by_regulation:
            recommendations.append("Increase capital buffers or reduce risk-weighted assets to meet capital requirements.")
        
        if 'leverage_ratio' in by_regulation:
            recommendations.append("Reduce leverage by decreasing position sizes or increasing capital.")
        
        if 'liquidity_coverage' in by_regulation:
            recommendations.append("Increase holdings of high-quality liquid assets to improve LCR.")
        
        if 'concentration_limits' in by_regulation:
            recommendations.append("Diversify portfolio to reduce concentration in single positions, sectors, or geographies.")
        
        return recommendations
    
    async def _check_auto_remediation(self, violations: List[ComplianceViolation]):
        """Check for violations that require auto-remediation"""
        auto_remediation_violations = [v for v in violations if v.remediation_suggested]
        
        for violation in auto_remediation_violations:
            rule = next((r for r in self.compliance_rules if r.rule_id == violation.rule_id), None)
            
            if rule and rule.auto_remediation:
                action = await self._execute_remediation_action(rule, violation)
                if action:
                    self.remediation_actions.append({
                        'violation_id': violation.rule_id,
                        'action': rule.remediation_action,
                        'timestamp': datetime.now(),
                        'status': 'executed'
                    })
    
    async def _execute_remediation_action(self, rule: ComplianceRule, violation: ComplianceViolation) -> bool:
        """Execute auto-remediation action (simplified)"""
        try:
            logger.info(f"Executing auto-remediation: {rule.remediation_action} for {rule.rule_id}")
            
            # This would implement actual remediation actions
            # For now, just log the action
            
            if "reduce_exposure" in rule.remediation_action.lower():
                # Would reduce position sizes
                pass
            elif "increase_capital" in rule.remediation_action.lower():
                # Would increase capital
                pass
            elif "increase_hqla" in rule.remediation_action.lower():
                # Would buy high-quality liquid assets
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing remediation action: {e}")
            return False
    
    async def resolve_violation(self, violation_id: str, resolution_notes: str = "") -> bool:
        """Mark a violation as resolved"""
        for violation in self.violation_history:
            if violation.rule_id == violation_id and not violation.resolved:
                violation.resolved = True
                violation.resolved_at = datetime.now()
                logger.info(f"Resolved violation: {violation_id} - {resolution_notes}")
                return True
        
        return False
    
    async def get_compliance_summary(self) -> Dict[str, Any]:
        """Get compliance engine summary"""
        active_violations = [v for v in self.violation_history if not v.resolved]
        recent_violations = [v for v in self.violation_history 
                           if v.timestamp >= datetime.now() - timedelta(days=30)]
        
        violations_by_type = {}
        for violation in active_violations:
            violation_type = violation.violation_type.value
            violations_by_type[violation_type] = violations_by_type.get(violation_type, 0) + 1
        
        return {
            'timestamp': datetime.now(),
            'total_rules': len(self.compliance_rules),
            'active_violations': len(active_violations),
            'recent_violations_30d': len(recent_violations),
            'violations_by_type': violations_by_type,
            'remediation_actions': len(self.remediation_actions),
            'last_compliance_check': self.last_compliance_check,
            'compliance_breaches': self.compliance_breaches
        }
    
    async def export_compliance_report(self, format_type: str = 'json') -> str:
        """Export comprehensive compliance report"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'compliance_rules': [
                {
                    'rule_id': rule.rule_id,
                    'name': rule.name,
                    'regulation_type': rule.regulation_type.value,
                    'threshold': rule.threshold_value,
                    'severity': rule.severity.value,
                    'auto_remediation': rule.auto_remediation
                }
                for rule in self.compliance_rules
            ],
            'violation_history': [
                {
                    'rule_id': v.rule_id,
                    'violation_type': v.violation_type.value,
                    'severity': v.severity.value,
                    'timestamp': v.timestamp.isoformat(),
                    'resolved': v.resolved,
                    'resolved_at': v.resolved_at.isoformat() if v.resolved_at else None
                }
                for v in self.violation_history
            ],
            'summary': await self.get_compliance_summary()
        }
        
        if format_type.lower() == 'json':
            return json.dumps(report_data, indent=2, default=str)
        else:
            return str(report_data)