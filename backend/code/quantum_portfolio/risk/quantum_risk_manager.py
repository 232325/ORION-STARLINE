"""
Quantum Risk Manager
===================

Asosiy quantum portfolio risk management tizimi.
Real-time risk monitoring, VaR/CVaR calculation, portfolio limits.

Muallif: Quantum Portfolio Team
 Sana: 2025-11-03
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

@dataclass
class RiskLimit:
    """Risk limit configuration"""
    name: str
    limit_type: str  # 'VaR', 'CVaR', 'concentration', 'drawdown'
    threshold: float
    warning_level: float
    action_required: bool
    description: str

@dataclass
class RiskAlert:
    """Risk alert message"""
    alert_id: str
    portfolio_id: str
    risk_type: str
    current_value: float
    threshold: float
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    message: str
    timestamp: datetime
    acknowledged: bool = False

class QuantumRiskManager:
    """Quantum portfolio risk management system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Risk parameters
        self.var_confidence_levels = [0.95, 0.99]
        self.cvar_confidence_levels = [0.95, 0.99]
        self.stress_scenarios = [
            'market_crash_2008',
            'covid_pandemic_2020',
            'financial_crisis_2001',
            'custom_scenario'
        ]
        
        # Risk limits configuration
        self.risk_limits = self._initialize_risk_limits()
        
        # Portfolio risk data
        self.portfolio_risks = {}
        self.risk_alerts = []
        self.monitoring_active = False
        
    def _initialize_risk_limits(self) -> List[RiskLimit]:
        """Initialize risk limits"""
        return [
            RiskLimit("VaR_95", "VaR", 0.05, 0.04, True, "Value at Risk (95% confidence)"),
            RiskLimit("VaR_99", "VaR", 0.10, 0.08, True, "Value at Risk (99% confidence)"),
            RiskLimit("CVaR_95", "CVaR", 0.08, 0.06, True, "Conditional Value at Risk (95%)"),
            RiskLimit("Concentration", "concentration", 0.25, 0.20, True, "Maximum asset concentration"),
            RiskLimit("Max_Drawdown", "drawdown", 0.15, 0.12, True, "Maximum drawdown"),
            RiskLimit("Leverage", "leverage", 2.0, 1.5, True, "Maximum portfolio leverage"),
            RiskLimit("Liquidity_Risk", "liquidity", 0.10, 0.08, True, "Liquidity risk threshold"),
            RiskLimit("Quantum_Error", "quantum_error", 0.05, 0.03, True, "Quantum computation error rate")
        ]
        
    async def calculate_portfolio_var(self, portfolio_id: str, returns: np.ndarray,
                                    weights: np.ndarray, confidence_level: float = 0.95,
                                    method: str = 'historical') -> float:
        """Calculate Value at Risk (VaR)"""
        try:
            # Portfolio returns
            portfolio_returns = np.dot(returns, weights)
            
            if method == 'historical':
                # Historical VaR
                var = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
                
            elif method == 'parametric':
                # Parametric VaR (assuming normal distribution)
                mean_return = np.mean(portfolio_returns)
                std_return = np.std(portfolio_returns)
                var = mean_return + stats.norm.ppf(1 - confidence_level) * std_return
                
            elif method == 'monte_carlo':
                # Monte Carlo VaR
                var = await self._monte_carlo_var(portfolio_returns, confidence_level)
                
            else:
                raise ValueError(f"Unknown VaR method: {method}")
                
            self.logger.info(f"VaR calculated for {portfolio_id}: {var:.4f}")
            return abs(var)  # VaR is typically positive
            
        except Exception as e:
            self.logger.error(f"VaR calculation failed for {portfolio_id}: {str(e)}")
            return 0.0
            
    async def _monte_carlo_var(self, returns: np.ndarray, confidence_level: float, 
                              n_simulations: int = 10000) -> float:
        """Monte Carlo VaR calculation"""
        # Fit distribution to returns
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        # Generate random returns
        np.random.seed(42)  # For reproducibility
        simulated_returns = np.random.normal(mean_return, std_return, n_simulations)
        
        # Calculate VaR
        var = np.percentile(simulated_returns, (1 - confidence_level) * 100)
        return abs(var)
        
    async def calculate_portfolio_cvar(self, portfolio_id: str, returns: np.ndarray,
                                     weights: np.ndarray, confidence_level: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (CVaR)"""
        try:
            # Portfolio returns
            portfolio_returns = np.dot(returns, weights)
            
            # Calculate VaR first
            var = await self.calculate_portfolio_var(portfolio_id, returns, weights, confidence_level)
            
            # CVaR is the expected loss given that loss exceeds VaR
            tail_returns = portfolio_returns[portfolio_returns <= -var]
            
            if len(tail_returns) == 0:
                return var
                
            cvar = abs(np.mean(tail_returns))
            
            self.logger.info(f"CVaR calculated for {portfolio_id}: {cvar:.4f}")
            return cvar
            
        except Exception as e:
            self.logger.error(f"CVaR calculation failed for {portfolio_id}: {str(e)}")
            return 0.0
            
    async def calculate_concentration_risk(self, portfolio_id: str, 
                                        weights: np.ndarray) -> Dict[str, float]:
        """Calculate concentration risk metrics"""
        try:
            # Sort weights
            sorted_weights = np.sort(weights)[::-1]
            
            concentration_metrics = {
                'hhi': np.sum(sorted_weights ** 2),  # Herfindahl-Hirschman Index
                'largest_weight': np.max(weights),
                'top_5_concentration': np.sum(sorted_weights[:5]),
                'top_10_concentration': np.sum(sorted_weights[:min(10, len(weights))]),
                'effective_positions': 1 / np.sum(weights ** 2),  # Effective number of positions
                'gini_coefficient': self._calculate_gini_coefficient(weights)
            }
            
            self.logger.info(f"Concentration risk for {portfolio_id}: {concentration_metrics['hhi']:.3f}")
            return concentration_metrics
            
        except Exception as e:
            self.logger.error(f"Concentration risk calculation failed: {str(e)}")
            return {}
            
    def _calculate_gini_coefficient(self, weights: np.ndarray) -> float:
        """Calculate Gini coefficient for wealth distribution"""
        sorted_weights = np.sort(weights)
        n = len(weights)
        index = np.arange(1, n + 1)
        
        gini = (2 * np.sum(index * sorted_weights)) / (n * np.sum(sorted_weights)) - (n + 1) / n
        return gini
        
    async def calculate_quantum_risk_adjustment(self, portfolio_id: str,
                                              quantum_metrics: Dict[str, Any]) -> float:
        """Calculate risk adjustment for quantum computation uncertainty"""
        try:
            # Extract quantum error metrics
            error_rate = quantum_metrics.get('error_rate', 0.01)
            fidelity = quantum_metrics.get('fidelity', 0.99)
            coherence_time = quantum_metrics.get('coherence_time', 100e-6)
            
            # Quantum risk factors
            error_risk = error_rate * 2.0  # Error propagation factor
            fidelity_risk = (1 - fidelity) * 1.5  # Fidelity degradation
            coherence_risk = max(0, (100e-6 - coherence_time) / 100e-6) * 1.0
            
            # Total quantum risk adjustment
            quantum_risk_adjustment = error_risk + fidelity_risk + coherence_risk
            
            self.logger.info(f"Quantum risk adjustment for {portfolio_id}: {quantum_risk_adjustment:.4f}")
            return quantum_risk_adjustment
            
        except Exception as e:
            self.logger.error(f"Quantum risk adjustment failed: {str(e)}")
            return 0.01  # Default 1% adjustment
            
    async def perform_stress_test(self, portfolio_id: str, weights: np.ndarray,
                                scenario: str = 'market_crash_2008') -> Dict[str, float]:
        """Perform portfolio stress testing"""
        try:
            # Define stress scenarios
            stress_scenarios = {
                'market_crash_2008': {
                    'equity_shock': -0.40,
                    'bond_lift': 0.10,
                    'commodity_drop': -0.30,
                    'volatility_spike': 3.0
                },
                'covid_pandemic_2020': {
                    'equity_shock': -0.30,
                    'bond_lift': 0.05,
                    'commodity_drop': -0.20,
                    'volatility_spike': 2.5
                },
                'financial_crisis_2001': {
                    'equity_shock': -0.35,
                    'bond_lift': 0.15,
                    'commodity_drop': -0.25,
                    'volatility_spike': 2.0
                }
            }
            
            # Get scenario parameters
            scenario_params = stress_scenarios.get(scenario, stress_scenarios['market_crash_2008'])
            
            # Apply stress to portfolio (simplified)
            base_return = np.random.uniform(0.05, 0.15)  # Normal expected return
            stressed_return = base_return * scenario_params['equity_shock']
            stressed_volatility = base_return * scenario_params['volatility_spike']
            
            # Stress test metrics
            stress_results = {
                'stressed_return': stressed_return,
                'stressed_volatility': stressed_volatility,
                'worst_case_loss': stressed_return - 2 * stressed_volatility,
                'scenario': scenario,
                'impact_score': abs(stressed_return) + stressed_volatility
            }
            
            self.logger.info(f"Stress test for {portfolio_id} - {scenario}: {stress_results['impact_score']:.3f}")
            return stress_results
            
        except Exception as e:
            self.logger.error(f"Stress test failed for {portfolio_id}: {str(e)}")
            return {}
            
    async def monitor_portfolio_risk(self, portfolio_id: str, returns: np.ndarray,
                                   weights: np.ndarray, quantum_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive portfolio risk monitoring"""
        try:
            self.logger.info(f"Starting risk monitoring for portfolio {portfolio_id}")
            
            risk_assessment = {}
            
            # Calculate VaR and CVaR
            for confidence in self.var_confidence_levels:
                var = await self.calculate_portfolio_var(portfolio_id, returns, weights, confidence)
                cvar = await self.calculate_portfolio_cvar(portfolio_id, returns, weights, confidence)
                
                risk_assessment[f'VaR_{int(confidence * 100)}'] = var
                risk_assessment[f'CVaR_{int(confidence * 100)}'] = cvar
                
            # Concentration risk
            concentration_metrics = await self.calculate_concentration_risk(portfolio_id, weights)
            risk_assessment['concentration_metrics'] = concentration_metrics
            
            # Quantum risk adjustment
            quantum_risk_adjustment = await self.calculate_quantum_risk_adjustment(
                portfolio_id, quantum_metrics
            )
            risk_assessment['quantum_risk_adjustment'] = quantum_risk_adjustment
            
            # Stress testing
            stress_results = await self.perform_stress_test(portfolio_id, weights)
            risk_assessment['stress_test'] = stress_results
            
            # Risk limits check
            limit_violations = await self.check_risk_limits(portfolio_id, risk_assessment)
            risk_assessment['limit_violations'] = limit_violations
            
            # Overall risk score
            risk_score = self._calculate_overall_risk_score(risk_assessment)
            risk_assessment['overall_risk_score'] = risk_score
            
            # Store assessment
            self.portfolio_risks[portfolio_id] = {
                'assessment': risk_assessment,
                'timestamp': datetime.now(),
                'status': 'monitored'
            }
            
            # Generate alerts if necessary
            await self._generate_risk_alerts(portfolio_id, risk_assessment, limit_violations)
            
            return risk_assessment
            
        except Exception as e:
            self.logger.error(f"Risk monitoring failed for {portfolio_id}: {str(e)}")
            return {}
            
    async def check_risk_limits(self, portfolio_id: str, 
                              risk_assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check portfolio against risk limits"""
        violations = []
        
        try:
            for limit in self.risk_limits:
                violation = False
                current_value = 0.0
                
                if limit.limit_type == "VaR":
                    current_value = risk_assessment.get(f'VaR_{int(limit.threshold * 100)}', 0)
                elif limit.limit_type == "CVaR":
                    current_value = risk_assessment.get(f'CVaR_{int(limit.threshold * 100)}', 0)
                elif limit.limit_type == "concentration":
                    current_value = risk_assessment.get('concentration_metrics', {}).get('hhi', 0)
                elif limit.limit_type == "quantum_error":
                    current_value = risk_assessment.get('quantum_risk_adjustment', 0)
                    
                # Check for violations
                if current_value > limit.threshold:
                    violation = True
                elif current_value > limit.warning_level:
                    # Warning level
                    pass
                    
                if violation:
                    violation_info = {
                        'limit_name': limit.name,
                        'limit_type': limit.limit_type,
                        'current_value': current_value,
                        'threshold': limit.threshold,
                        'exceeded_by': current_value - limit.threshold,
                        'severity': 'CRITICAL' if current_value > limit.threshold * 1.2 else 'HIGH'
                    }
                    violations.append(violation_info)
                    
        except Exception as e:
            self.logger.error(f"Risk limit check failed: {str(e)}")
            
        return violations
        
    def _calculate_overall_risk_score(self, risk_assessment: Dict[str, Any]) -> float:
        """Calculate overall portfolio risk score (0-100)"""
        try:
            risk_factors = []
            
            # VaR factor
            var_95 = risk_assessment.get('VaR_95', 0)
            risk_factors.append(min(100, var_95 * 1000))  # Scale factor
            
            # CVaR factor
            cvar_95 = risk_assessment.get('CVaR_95', 0)
            risk_factors.append(min(100, cvar_95 * 800))
            
            # Concentration factor
            hhi = risk_assessment.get('concentration_metrics', {}).get('hhi', 0)
            risk_factors.append(min(100, hhi * 400))
            
            # Quantum risk factor
            quantum_risk = risk_assessment.get('quantum_risk_adjustment', 0)
            risk_factors.append(min(100, quantum_risk * 1000))
            
            # Weighted average
            if risk_factors:
                overall_score = np.mean(risk_factors)
            else:
                overall_score = 0.0
                
            return min(100, max(0, overall_score))
            
        except Exception as e:
            self.logger.error(f"Risk score calculation failed: {str(e)}")
            return 50.0  # Default moderate risk
            
    async def _generate_risk_alerts(self, portfolio_id: str, risk_assessment: Dict[str, Any],
                                  violations: List[Dict[str, Any]]):
        """Generate risk alerts for violations"""
        try:
            for violation in violations:
                alert = RiskAlert(
                    alert_id=f"alert_{portfolio_id}_{datetime.now().timestamp()}",
                    portfolio_id=portfolio_id,
                    risk_type=violation['limit_type'],
                    current_value=violation['current_value'],
                    threshold=violation['threshold'],
                    severity=violation['severity'],
                    message=f"Risk limit violated: {violation['limit_name']} = {violation['current_value']:.4f} > {violation['threshold']:.4f}",
                    timestamp=datetime.now()
                )
                
                self.risk_alerts.append(alert)
                self.logger.warning(f"Risk alert generated: {alert.message}")
                
        except Exception as e:
            self.logger.error(f"Alert generation failed: {str(e)}")
            
    async def get_portfolio_risk_report(self, portfolio_id: str) -> Dict[str, Any]:
        """Generate comprehensive risk report"""
        try:
            if portfolio_id not in self.portfolio_risks:
                return {"error": "Portfolio not found"}
                
            risk_data = self.portfolio_risks[portfolio_id]
            
            report = {
                'portfolio_id': portfolio_id,
                'report_timestamp': datetime.now().isoformat(),
                'risk_assessment': risk_data['assessment'],
                'risk_score': risk_data['assessment'].get('overall_risk_score', 0),
                'risk_level': self._categorize_risk_level(risk_data['assessment'].get('overall_risk_score', 0)),
                'recommendations': self._generate_risk_recommendations(risk_data['assessment']),
                'alerts': [alert for alert in self.risk_alerts if alert.portfolio_id == portfolio_id]
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Risk report generation failed: {str(e)}")
            return {}
            
    def _categorize_risk_level(self, risk_score: float) -> str:
        """Categorize risk level based on score"""
        if risk_score <= 20:
            return "LOW"
        elif risk_score <= 50:
            return "MEDIUM"
        elif risk_score <= 75:
            return "HIGH"
        else:
            return "CRITICAL"
            
    def _generate_risk_recommendations(self, risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        try:
            # VaR recommendations
            var_95 = risk_assessment.get('VaR_95', 0)
            if var_95 > 0.05:
                recommendations.append("Consider reducing portfolio size or adding lower-risk assets to reduce VaR")
                
            # Concentration recommendations
            hhi = risk_assessment.get('concentration_metrics', {}).get('hhi', 0)
            if hhi > 0.25:
                recommendations.append("Portfolio is too concentrated - diversify across more assets")
                
            # Quantum risk recommendations
            quantum_risk = risk_assessment.get('quantum_risk_adjustment', 0)
            if quantum_risk > 0.03:
                recommendations.append("High quantum computation uncertainty - consider hybrid approach")
                
            # Stress test recommendations
            stress_result = risk_assessment.get('stress_test', {})
            if stress_result.get('impact_score', 0) > 0.5:
                recommendations.append("Portfolio vulnerable to stress scenarios - consider hedging strategies")
                
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {str(e)}")
            
        return recommendations
        
    async def start_monitoring(self, portfolio_ids: List[str]):
        """Start continuous risk monitoring"""
        self.monitoring_active = True
        self.logger.info(f"Started risk monitoring for portfolios: {portfolio_ids}")
        
        # In a real implementation, this would run continuously
        # For demo, we'll simulate periodic monitoring
        while self.monitoring_active:
            try:
                # Simulate monitoring loop
                await asyncio.sleep(60)  # Check every minute
                
                for portfolio_id in portfolio_ids:
                    # This would typically pull live data
                    # For demo, generate mock data
                    returns = np.random.normal(0.001, 0.02, 252)  # Mock daily returns
                    weights = np.random.dirichlet(np.ones(10))  # Mock weights
                    quantum_metrics = {'error_rate': 0.01, 'fidelity': 0.99}
                    
                    await self.monitor_portfolio_risk(portfolio_id, returns, weights, quantum_metrics)
                    
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {str(e)}")
                await asyncio.sleep(10)
                
    def stop_monitoring(self):
        """Stop risk monitoring"""
        self.monitoring_active = False
        self.logger.info("Risk monitoring stopped")
        
    def get_risk_alerts(self, portfolio_id: str = None, severity: str = None) -> List[RiskAlert]:
        """Get risk alerts"""
        alerts = self.risk_alerts
        
        if portfolio_id:
            alerts = [alert for alert in alerts if alert.portfolio_id == portfolio_id]
            
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
            
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
        
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge a risk alert"""
        try:
            for alert in self.risk_alerts:
                if alert.alert_id == alert_id:
                    alert.acknowledged = True
                    self.logger.info(f"Alert acknowledged: {alert_id}")
                    return True
            return False
            
        except Exception as e:
            self.logger.error(f"Alert acknowledgment failed: {str(e)}")
            return False

# Usage example
async def example_risk_management():
    """Example risk management usage"""
    # Create risk manager
    risk_manager = QuantumRiskManager()
    
    # Generate mock portfolio data
    portfolio_id = "example_portfolio"
    weights = np.array([0.3, 0.25, 0.2, 0.15, 0.1])  # 5 assets
    returns = np.random.normal(0.001, 0.02, 252)  # Daily returns
    quantum_metrics = {'error_rate': 0.01, 'fidelity': 0.99, 'coherence_time': 100e-6}
    
    # Perform risk monitoring
    risk_assessment = await risk_manager.monitor_portfolio_risk(
        portfolio_id, returns, weights, quantum_metrics
    )
    
    print(f"Risk Assessment for {portfolio_id}:")
    print(f"- VaR (95%): {risk_assessment.get('VaR_95', 0):.4f}")
    print(f"- CVaR (95%): {risk_assessment.get('CVaR_95', 0):.4f}")
    print(f"- Risk Score: {risk_assessment.get('overall_risk_score', 0):.2f}")
    print(f"- Risk Level: {risk_manager._categorize_risk_level(risk_assessment.get('overall_risk_score', 0))}")
    
    # Generate risk report
    report = await risk_manager.get_portfolio_risk_report(portfolio_id)
    print(f"\\nRecommendations: {report.get('recommendations', [])}")
    
    # Start monitoring (demo - would run continuously)
    # await risk_manager.start_monitoring([portfolio_id])

if __name__ == "__main__":
    asyncio.run(example_risk_management())