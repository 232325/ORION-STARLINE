"""
Risk Limits Management System
============================

Defines, validates, and enforces various risk limits across the portfolio.
Includes position limits, exposure limits, correlation limits, and more.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

class LimitType(Enum):
    """Types of risk limits"""
    POSITION_SIZE = "position_size"
    SECTOR_EXPOSURE = "sector_exposure"
    CORRELATION_LIMIT = "correlation_limit"
    DRAWDOWN_LIMIT = "drawdown_limit"
    VAR_LIMIT = "var_limit"
    CONCENTRATION_LIMIT = "concentration_limit"
    LIQUIDITY_LIMIT = "liquidity_limit"
    LEVERAGE_LIMIT = "leverage_limit"

class LimitSeverity(Enum):
    """Limit violation severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class RiskLimit:
    """Individual risk limit definition"""
    name: str
    limit_type: LimitType
    value: float
    asset_class: str = "all"
    symbol: str = "all"
    description: str = ""
    severity: LimitSeverity = LimitSeverity.WARNING
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class LimitViolation:
    """Risk limit violation record"""
    limit_name: str
    limit_type: LimitType
    current_value: float
    limit_value: float
    violation_amount: float
    timestamp: datetime
    severity: LimitSeverity
    description: str
    action_required: bool = False

@dataclass
class LimitCheckResult:
    """Result of limit checking"""
    violations: List[LimitViolation]
    warnings: List[str]
    passed: bool
    timestamp: datetime

class RiskLimits:
    """
    Comprehensive risk limits management system
    
    Manages all types of risk limits, validates positions against limits,
    and triggers alerts when limits are exceeded.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.limits: List[RiskLimit] = []
        self.violation_history: List[LimitViolation] = []
        
        # Initialize default limits
        self._initialize_default_limits()
    
    def _initialize_default_limits(self):
        """Initialize default risk limits"""
        
        # Position size limits by asset class
        self.add_limit(RiskLimit(
            name="equity_position_limit",
            limit_type=LimitType.POSITION_SIZE,
            value=1000000,  # $1M max per equity position
            asset_class="equity",
            description="Maximum position size for individual equities",
            severity=LimitSeverity.WARNING
        ))
        
        self.add_limit(RiskLimit(
            name="forex_position_limit",
            limit_type=LimitType.POSITION_SIZE,
            value=10000000,  # $10M max per forex position
            asset_class="forex",
            description="Maximum position size for forex pairs",
            severity=LimitSeverity.WARNING
        ))
        
        self.add_limit(RiskLimit(
            name="commodity_position_limit",
            limit_type=LimitType.POSITION_SIZE,
            value=2000000,  # $2M max per commodity position
            asset_class="commodity",
            description="Maximum position size for commodities",
            severity=LimitSeverity.WARNING
        ))
        
        # Exposure limits
        self.add_limit(RiskLimit(
            name="total_equity_exposure",
            limit_type=LimitType.SECTOR_EXPOSURE,
            value=5000000,  # $5M max equity exposure
            asset_class="equity",
            description="Maximum total equity exposure",
            severity=LimitSeverity.ERROR
        ))
        
        self.add_limit(RiskLimit(
            name="total_forex_exposure",
            limit_type=LimitType.SECTOR_EXPOSURE,
            value=25000000,  # $25M max forex exposure
            asset_class="forex",
            description="Maximum total forex exposure",
            severity=LimitSeverity.ERROR
        ))
        
        # Concentration limits
        self.add_limit(RiskLimit(
            name="single_position_concentration",
            limit_type=LimitType.CONCENTRATION_LIMIT,
            value=0.20,  # 20% max concentration in single position
            description="Maximum concentration in single position",
            severity=LimitSeverity.ERROR
        ))
        
        self.add_limit(RiskLimit(
            name="sector_concentration",
            limit_type=LimitType.CONCENTRATION_LIMIT,
            value=0.50,  # 50% max concentration in single sector
            description="Maximum concentration in single sector",
            severity=LimitSeverity.ERROR
        ))
        
        # Drawdown limits
        self.add_limit(RiskLimit(
            name="daily_drawdown_limit",
            limit_type=LimitType.DRAWDOWN_LIMIT,
            value=0.05,  # 5% daily drawdown limit
            description="Maximum daily portfolio drawdown",
            severity=LimitSeverity.CRITICAL
        ))
        
        self.add_limit(RiskLimit(
            name="weekly_drawdown_limit",
            limit_type=LimitType.DRAWDOWN_LIMIT,
            value=0.10,  # 10% weekly drawdown limit
            description="Maximum weekly portfolio drawdown",
            severity=LimitSeverity.CRITICAL
        ))
        
        # VaR limits
        self.add_limit(RiskLimit(
            name="portfolio_var_limit",
            limit_type=LimitType.VAR_LIMIT,
            value=1000000,  # $1M VaR limit
            description="Maximum portfolio Value at Risk",
            severity=LimitSeverity.ERROR
        ))
        
        # Liquidity limits
        self.add_limit(RiskLimit(
            name="illiquid_position_limit",
            limit_type=LimitType.LIQUIDITY_LIMIT,
            value=0.10,  # 10% max in illiquid positions
            description="Maximum allocation to illiquid positions",
            severity=LimitSeverity.WARNING
        ))
        
        # Correlation limits
        self.add_limit(RiskLimit(
            name="correlation_threshold",
            limit_type=LimitType.CORRELATION_LIMIT,
            value=0.85,  # 85% correlation threshold
            description="Maximum correlation between positions",
            severity=LimitSeverity.WARNING
        ))
        
        logger.info(f"Initialized {len(self.limits)} default risk limits")
    
    def add_limit(self, limit: RiskLimit):
        """Add a new risk limit"""
        self.limits.append(limit)
        logger.info(f"Added risk limit: {limit.name}")
    
    def remove_limit(self, name: str) -> bool:
        """Remove a risk limit by name"""
        original_count = len(self.limits)
        self.limits = [limit for limit in self.limits if limit.name != name]
        
        if len(self.limits) < original_count:
            logger.info(f"Removed risk limit: {name}")
            return True
        return False
    
    def update_limit(self, name: str, value: float) -> bool:
        """Update an existing limit value"""
        for limit in self.limits:
            if limit.name == name:
                limit.value = value
                logger.info(f"Updated limit {name} to {value}")
                return True
        return False
    
    def get_limit(self, name: str) -> Optional[RiskLimit]:
        """Get a specific limit by name"""
        for limit in self.limits:
            if limit.name == name:
                return limit
        return None
    
    def get_limits_by_type(self, limit_type: LimitType) -> List[RiskLimit]:
        """Get all limits of a specific type"""
        return [limit for limit in self.limits if limit.limit_type == limit_type]
    
    def get_limits_by_asset_class(self, asset_class: str) -> List[RiskLimit]:
        """Get all limits for a specific asset class"""
        return [limit for limit in self.limits 
                if limit.asset_class == asset_class or limit.asset_class == "all"]
    
    async def check_limits(self, positions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check all positions against all active limits
        
        Args:
            positions: Current position data
            
        Returns:
            List of limit violations
        """
        violations = []
        
        for limit in self.limits:
            if not limit.enabled:
                continue
                
            violation = await self._check_single_limit(limit, positions)
            if violation:
                violations.append(violation)
                
                # Add to violation history
                self.violation_history.append(violation)
                
                logger.warning(f"Limit violation: {violation['description']}")
        
        return violations
    
    async def check_position_sizes(self, positions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check position size limits specifically"""
        violations = []
        
        size_limits = self.get_limits_by_type(LimitType.POSITION_SIZE)
        
        for symbol, position in positions.items():
            for limit in size_limits:
                if self._limit_applies_to_position(limit, position):
                    current_value = abs(position.get('market_value', 0))
                    
                    if current_value > limit.value:
                        violation = {
                            'limit_name': limit.name,
                            'limit_type': 'position_size',
                            'symbol': symbol,
                            'current_value': current_value,
                            'limit_value': limit.value,
                            'excess': current_value - limit.value,
                            'description': f"Position {symbol} exceeds size limit",
                            'severity': limit.severity.value,
                            'asset_class': position.get('asset_class', 'unknown')
                        }
                        violations.append(violation)
        
        return violations
    
    async def check_exposure_limits(self, positions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check sector/exposure limits"""
        violations = []
        
        exposure_limits = self.get_limits_by_type(LimitType.SECTOR_EXPOSURE)
        
        # Calculate exposures by asset class
        asset_exposures = self._calculate_asset_exposures(positions)
        
        for limit in exposure_limits:
            current_exposure = asset_exposures.get(limit.asset_class, 0)
            
            if current_exposure > limit.value:
                violation = {
                    'limit_name': limit.name,
                    'limit_type': 'exposure',
                    'asset_class': limit.asset_class,
                    'current_exposure': current_exposure,
                    'limit_value': limit.value,
                    'excess': current_exposure - limit.value,
                    'description': f"{limit.asset_class} exposure exceeds limit",
                    'severity': limit.severity.value
                }
                violations.append(violation)
        
        return violations
    
    async def check_concentration_limits(self, positions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check concentration limits"""
        violations = []
        
        if not positions:
            return violations
        
        total_portfolio_value = sum(pos.get('market_value', 0) for pos in positions.values())
        
        if total_portfolio_value <= 0:
            return violations
        
        concentration_limits = self.get_limits_by_type(LimitType.CONCENTRATION_LIMIT)
        
        for limit in concentration_limits:
            if limit.name == "single_position_concentration":
                # Check individual position concentrations
                for symbol, position in positions.items():
                    position_value = abs(position.get('market_value', 0))
                    concentration = position_value / total_portfolio_value
                    
                    if concentration > limit.value:
                        violation = {
                            'limit_name': limit.name,
                            'limit_type': 'concentration',
                            'symbol': symbol,
                            'current_concentration': concentration,
                            'limit_value': limit.value,
                            'excess': concentration - limit.value,
                            'description': f"Position {symbol} concentration exceeds limit",
                            'severity': limit.severity.value
                        }
                        violations.append(violation)
        
        return violations
    
    async def check_correlation_limits(self, positions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check correlation limits between positions"""
        violations = []
        
        if len(positions) < 2:
            return violations
        
        correlation_limits = self.get_limits_by_type(LimitType.CORRELATION_LIMIT)
        
        for limit in correlation_limits:
            correlation_matrix = await self._calculate_correlation_matrix(positions)
            
            # Check for high correlations
            high_correlations = []
            for i, symbol1 in enumerate(correlation_matrix.index):
                for j, symbol2 in enumerate(correlation_matrix.columns):
                    if i < j:  # Avoid duplicates and diagonal
                        correlation = correlation_matrix.loc[symbol1, symbol2]
                        if abs(correlation) > limit.value:
                            high_correlations.append((symbol1, symbol2, correlation))
            
            if high_correlations:
                violation = {
                    'limit_name': limit.name,
                    'limit_type': 'correlation',
                    'high_correlations': high_correlations,
                    'threshold': limit.value,
                    'description': f"Found {len(high_correlations)} highly correlated position pairs",
                    'severity': limit.severity.value
                }
                violations.append(violation)
        
        return violations
    
    def get_violation_history(self, hours: int = 24) -> List[LimitViolation]:
        """Get violation history for specified period"""
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        return [violation for violation in self.violation_history 
                if violation.timestamp.timestamp() >= cutoff_time]
    
    def get_limit_statistics(self) -> Dict[str, Any]:
        """Get statistics about limit violations"""
        total_limits = len(self.limits)
        enabled_limits = len([limit for limit in self.limits if limit.enabled])
        recent_violations = self.get_violation_history(24)
        
        violations_by_type = {}
        violations_by_severity = {}
        
        for violation in recent_violations:
            # By type
            type_key = violation.limit_type.value
            violations_by_type[type_key] = violations_by_type.get(type_key, 0) + 1
            
            # By severity
            severity_key = violation.severity.value
            violations_by_severity[severity_key] = violations_by_severity.get(severity_key, 0) + 1
        
        return {
            'total_limits': total_limits,
            'enabled_limits': enabled_limits,
            'disabled_limits': total_limits - enabled_limits,
            'recent_violations_24h': len(recent_violations),
            'violations_by_type': violations_by_type,
            'violations_by_severity': violations_by_severity
        }
    
    # Private helper methods
    
    async def _check_single_limit(self, limit: RiskLimit, positions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check a single limit against current positions"""
        try:
            if limit.limit_type == LimitType.POSITION_SIZE:
                return await self._check_position_size_limit(limit, positions)
            elif limit.limit_type == LimitType.SECTOR_EXPOSURE:
                return await self._check_exposure_limit(limit, positions)
            elif limit.limit_type == LimitType.CONCENTRATION_LIMIT:
                return await self._check_concentration_limit(limit, positions)
            elif limit.limit_type == LimitType.DRAWDOWN_LIMIT:
                return await self._check_drawdown_limit(limit, positions)
            elif limit.limit_type == LimitType.VAR_LIMIT:
                return await self._check_var_limit(limit, positions)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error checking limit {limit.name}: {e}")
            return None
    
    async def _check_position_size_limit(self, limit: RiskLimit, positions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check position size limit"""
        for symbol, position in positions.items():
            if self._limit_applies_to_position(limit, position):
                current_value = abs(position.get('market_value', 0))
                
                if current_value > limit.value:
                    return {
                        'limit_name': limit.name,
                        'limit_type': limit.limit_type.value,
                        'symbol': symbol,
                        'current_value': current_value,
                        'limit_value': limit.value,
                        'excess': current_value - limit.value,
                        'description': limit.description,
                        'severity': limit.severity.value,
                        'timestamp': datetime.now()
                    }
        return None
    
    async def _check_exposure_limit(self, limit: RiskLimit, positions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check sector exposure limit"""
        asset_exposures = self._calculate_asset_exposures(positions)
        current_exposure = asset_exposures.get(limit.asset_class, 0)
        
        if current_exposure > limit.value:
            return {
                'limit_name': limit.name,
                'limit_type': limit.limit_type.value,
                'asset_class': limit.asset_class,
                'current_exposure': current_exposure,
                'limit_value': limit.value,
                'excess': current_exposure - limit.value,
                'description': limit.description,
                'severity': limit.severity.value,
                'timestamp': datetime.now()
            }
        return None
    
    async def _check_concentration_limit(self, limit: RiskLimit, positions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check concentration limit"""
        if not positions:
            return None
        
        total_value = sum(abs(pos.get('market_value', 0)) for pos in positions.values())
        
        if limit.name == "single_position_concentration":
            for symbol, position in positions.items():
                position_value = abs(position.get('market_value', 0))
                concentration = position_value / max(total_value, 1)
                
                if concentration > limit.value:
                    return {
                        'limit_name': limit.name,
                        'limit_type': limit.limit_type.value,
                        'symbol': symbol,
                        'current_concentration': concentration,
                        'limit_value': limit.value,
                        'excess': concentration - limit.value,
                        'description': limit.description,
                        'severity': limit.severity.value,
                        'timestamp': datetime.now()
                    }
        
        return None
    
    async def _check_drawdown_limit(self, limit: RiskLimit, positions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check drawdown limit"""
        # This would typically check against historical portfolio values
        # For now, return None as it requires historical data
        
        # Simplified: calculate unrealized losses as proxy for drawdown
        total_unrealized_loss = sum(abs(pos.get('unrealized_pnl', 0)) 
                                   for pos in positions.values() 
                                   if pos.get('unrealized_pnl', 0) < 0)
        
        total_value = sum(abs(pos.get('market_value', 0)) for pos in positions.values())
        
        if total_value > 0:
            current_drawdown = total_unrealized_loss / total_value
            
            if current_drawdown > limit.value:
                return {
                    'limit_name': limit.name,
                    'limit_type': limit.limit_type.value,
                    'current_drawdown': current_drawdown,
                    'limit_value': limit.value,
                    'excess': current_drawdown - limit.value,
                    'description': limit.description,
                    'severity': limit.severity.value,
                    'timestamp': datetime.now()
                }
        
        return None
    
    async def _check_var_limit(self, limit: RiskLimit, positions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check VaR limit"""
        # Simplified VaR calculation
        total_var = sum(abs(pos.get('market_value', 0)) * 0.02 for pos in positions.values())  # 2% VaR
        
        if total_var > limit.value:
            return {
                'limit_name': limit.name,
                'limit_type': limit.limit_type.value,
                'current_var': total_var,
                'limit_value': limit.value,
                'excess': total_var - limit.value,
                'description': limit.description,
                'severity': limit.severity.value,
                'timestamp': datetime.now()
            }
        
        return None
    
    def _limit_applies_to_position(self, limit: RiskLimit, position: Dict[str, Any]) -> bool:
        """Check if limit applies to a specific position"""
        # Check asset class
        if (limit.asset_class != "all" and 
            position.get('asset_class') != limit.asset_class):
            return False
        
        # Check symbol
        if (limit.symbol != "all" and 
            position.get('symbol') != limit.symbol):
            return False
        
        return True
    
    def _calculate_asset_exposures(self, positions: Dict[str, Any]) -> Dict[str, float]:
        """Calculate total exposures by asset class"""
        exposures = {}
        
        for position in positions.values():
            asset_class = position.get('asset_class', 'unknown')
            value = abs(position.get('market_value', 0))
            
            if asset_class not in exposures:
                exposures[asset_class] = 0
            exposures[asset_class] += value
        
        return exposures
    
    async def _calculate_correlation_matrix(self, positions: Dict[str, Any]) -> Any:
        """Calculate correlation matrix between positions"""
        # Simplified correlation matrix - would use actual historical data
        symbols = list(positions.keys())
        n = len(symbols)
        
        # Create a simple correlation matrix with varying correlations
        import numpy as np
        correlation_matrix = np.eye(n)  # Identity matrix for now
        
        # This would be replaced with actual correlation calculations
        # using historical price data
        
        return pd.DataFrame(correlation_matrix, index=symbols, columns=symbols)
    
    async def validate_limit_configuration(self) -> Dict[str, Any]:
        """Validate current limit configuration"""
        issues = []
        warnings = []
        
        # Check for conflicting limits
        position_limits = self.get_limits_by_type(LimitType.POSITION_SIZE)
        for i, limit1 in enumerate(position_limits):
            for limit2 in position_limits[i+1:]:
                if (limit1.asset_class == limit2.asset_class and 
                    limit1.symbol == limit2.symbol):
                    warnings.append(f"Multiple position limits for {limit1.asset_class}")
        
        # Check for reasonable values
        for limit in self.limits:
            if limit.limit_type == LimitType.CONCENTRATION_LIMIT and limit.value > 1.0:
                issues.append(f"Concentration limit {limit.name} has value > 1.0")
            
            if limit.limit_type == LimitType.DRAWDOWN_LIMIT and limit.value > 0.5:
                issues.append(f"Drawdown limit {limit.name} has value > 50%")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'total_limits': len(self.limits),
            'enabled_limits': len([l for l in self.limits if l.enabled])
        }