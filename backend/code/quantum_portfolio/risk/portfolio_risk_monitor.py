"""
Portfolio Risk Monitor
=====================

Real-time portfolio risk monitoring va alerting tizimi.
Continuous risk tracking va automatic notifications.

Muallif: Quantum Portfolio Team
 Sana: 2025-11-03
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

@dataclass
class RiskThreshold:
    """Risk threshold configuration"""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    action_required: bool
    notification_enabled: bool

@dataclass
class MonitoringSession:
    """Active monitoring session"""
    session_id: str
    portfolio_id: str
    start_time: datetime
    last_update: datetime
    alert_count: int
    status: str  # 'active', 'paused', 'stopped'

class PortfolioRiskMonitor:
    """Real-time portfolio risk monitoring system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Monitoring configuration
        self.monitoring_interval = self.config.get('monitoring_interval', 60)  # seconds
        self.alert_cooldown = self.config.get('alert_cooldown', 300)  # 5 minutes
        
        # Risk thresholds
        self.risk_thresholds = self._initialize_thresholds()
        
        # Active monitoring sessions
        self.active_sessions: Dict[str, MonitoringSession] = {}
        
        # Alert tracking
        self.last_alerts: Dict[str, datetime] = {}
        self.notification_callbacks: List[Callable] = []
        
        # Email configuration for alerts
        self.email_config = {
            'smtp_server': self.config.get('smtp_server', 'localhost'),
            'smtp_port': self.config.get('smtp_port', 587),
            'username': self.config.get('smtp_username', ''),
            'password': self.config.get('smtp_password', ''),
            'from_email': self.config.get('from_email', 'quantum-portfolio@company.com'),
            'to_emails': self.config.get('to_emails', ['admin@company.com'])
        }
        
        # Data storage for historical monitoring
        self.monitoring_history = []
        
    def _initialize_thresholds(self) -> List[RiskThreshold]:
        """Initialize risk monitoring thresholds"""
        return [
            RiskThreshold("VaR_95", 0.04, 0.06, True, True),
            RiskThreshold("VaR_99", 0.08, 0.12, True, True),
            RiskThreshold("CVaR_95", 0.06, 0.10, True, True),
            RiskThreshold("Concentration_HHI", 0.20, 0.30, True, True),
            RiskThreshold("Max_Weight", 0.25, 0.35, True, True),
            RiskThreshold("Quantum_Error", 0.03, 0.05, True, True),
            RiskThreshold("Drawdown", 0.10, 0.15, True, True),
            RiskThreshold("Volatility", 0.25, 0.40, True, True),
            RiskThreshold("Liquidity_Risk", 0.08, 0.12, True, True),
            RiskThreshold("Correlation_Risk", 0.70, 0.85, True, True)
        ]
        
    async def start_monitoring(self, portfolio_id: str, session_name: str = None) -> str:
        """Start monitoring a portfolio"""
        try:
            session_id = f"session_{portfolio_id}_{datetime.now().timestamp()}"
            
            session = MonitoringSession(
                session_id=session_id,
                portfolio_id=portfolio_id,
                start_time=datetime.now(),
                last_update=datetime.now(),
                alert_count=0,
                status='active'
            )
            
            self.active_sessions[session_id] = session
            self.logger.info(f"Started monitoring session {session_id} for portfolio {portfolio_id}")
            
            # Start monitoring loop
            asyncio.create_task(self._monitoring_loop(session_id))
            
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {str(e)}")
            raise
            
    async def stop_monitoring(self, session_id: str) -> bool:
        """Stop monitoring session"""
        try:
            if session_id in self.active_sessions:
                self.active_sessions[session_id].status = 'stopped'
                self.logger.info(f"Stopped monitoring session {session_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {str(e)}")
            return False
            
    async def pause_monitoring(self, session_id: str) -> bool:
        """Pause monitoring session"""
        try:
            if session_id in self.active_sessions:
                self.active_sessions[session_id].status = 'paused'
                self.logger.info(f"Paused monitoring session {session_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to pause monitoring: {str(e)}")
            return False
            
    async def resume_monitoring(self, session_id: str) -> bool:
        """Resume monitoring session"""
        try:
            if session_id in self.active_sessions:
                self.active_sessions[session_id].status = 'active'
                self.logger.info(f"Resumed monitoring session {session_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to resume monitoring: {str(e)}")
            return False
            
    async def _monitoring_loop(self, session_id: str):
        """Main monitoring loop for a session"""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return
                
            while session.status in ['active', 'paused']:
                if session.status == 'active':
                    # Perform risk checks
                    await self._perform_risk_checks(session)
                    
                # Sleep for monitoring interval
                await asyncio.sleep(self.monitoring_interval)
                
                # Update last update time
                session.last_update = datetime.now()
                
                # Clean up stopped sessions
                if session.status == 'stopped':
                    break
                    
        except Exception as e:
            self.logger.error(f"Monitoring loop error for {session_id}: {str(e)}")
            session.status = 'stopped'
            
    async def _perform_risk_checks(self, session: MonitoringSession):
        """Perform risk checks for monitoring session"""
        try:
            portfolio_id = session.portfolio_id
            
            # Get current risk metrics (would be real data in production)
            risk_metrics = await self._get_current_risk_metrics(portfolio_id)
            
            # Check against thresholds
            threshold_violations = await self._check_thresholds(risk_metrics, portfolio_id)
            
            # Process violations
            for violation in threshold_violations:
                await self._handle_threshold_violation(session, violation, risk_metrics)
                
            # Update monitoring history
            await self._update_monitoring_history(session, risk_metrics, threshold_violations)
            
        except Exception as e:
            self.logger.error(f"Risk checks failed for {session.session_id}: {str(e)}")
            
    async def _get_current_risk_metrics(self, portfolio_id: str) -> Dict[str, float]:
        """Get current risk metrics for portfolio"""
        try:
            # In production, this would fetch real portfolio data
            # For demo, generate mock metrics
            
            # Mock VaR and CVaR
            var_95 = np.random.uniform(0.02, 0.08)
            var_99 = var_95 * np.random.uniform(1.2, 1.8)
            cvar_95 = var_95 * np.random.uniform(1.2, 1.5)
            
            # Mock concentration metrics
            hhi = np.random.uniform(0.15, 0.35)
            max_weight = np.random.uniform(0.20, 0.40)
            
            # Mock other metrics
            quantum_error = np.random.uniform(0.01, 0.04)
            drawdown = np.random.uniform(0.05, 0.12)
            volatility = np.random.uniform(0.15, 0.35)
            liquidity_risk = np.random.uniform(0.05, 0.15)
            correlation_risk = np.random.uniform(0.60, 0.90)
            
            metrics = {
                'VaR_95': var_95,
                'VaR_99': var_99,
                'CVaR_95': cvar_95,
                'Concentration_HHI': hhi,
                'Max_Weight': max_weight,
                'Quantum_Error': quantum_error,
                'Drawdown': drawdown,
                'Volatility': volatility,
                'Liquidity_Risk': liquidity_risk,
                'Correlation_Risk': correlation_risk
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get risk metrics: {str(e)}")
            return {}
            
    async def _check_thresholds(self, metrics: Dict[str, float], 
                              portfolio_id: str) -> List[Dict[str, Any]]:
        """Check metrics against thresholds"""
        violations = []
        
        try:
            for threshold in self.risk_thresholds:
                metric_value = metrics.get(threshold.metric_name, 0)
                
                # Check for critical violation
                if metric_value > threshold.critical_threshold:
                    severity = 'CRITICAL'
                    threshold_exceeded = metric_value - threshold.critical_threshold
                    
                # Check for warning
                elif metric_value > threshold.warning_threshold:
                    severity = 'WARNING'
                    threshold_exceeded = metric_value - threshold.warning_threshold
                    
                else:
                    continue  # No violation
                    
                violation = {
                    'metric_name': threshold.metric_name,
                    'current_value': metric_value,
                    'warning_threshold': threshold.warning_threshold,
                    'critical_threshold': threshold.critical_threshold,
                    'threshold_exceeded': threshold_exceeded,
                    'severity': severity,
                    'action_required': threshold.action_required,
                    'notification_enabled': threshold.notification_enabled
                }
                
                violations.append(violation)
                
        except Exception as e:
            self.logger.error(f"Threshold check failed: {str(e)}")
            
        return violations
        
    async def _handle_threshold_violation(self, session: MonitoringSession, 
                                        violation: Dict[str, Any], 
                                        all_metrics: Dict[str, float]):
        """Handle threshold violation"""
        try:
            portfolio_id = session.portfolio_id
            metric_name = violation['metric_name']
            
            # Check cooldown period
            alert_key = f"{portfolio_id}_{metric_name}"
            if self._is_in_cooldown(alert_key):
                return
                
            # Create alert
            alert = {
                'session_id': session.session_id,
                'portfolio_id': portfolio_id,
                'metric_name': metric_name,
                'current_value': violation['current_value'],
                'threshold_exceeded': violation['threshold_exceeded'],
                'severity': violation['severity'],
                'timestamp': datetime.now().isoformat(),
                'all_metrics': all_metrics
            }
            
            # Update cooldown
            self.last_alerts[alert_key] = datetime.now()
            
            # Update session alert count
            session.alert_count += 1
            
            # Log alert
            self.logger.warning(f"Risk threshold violation - {portfolio_id}: {metric_name} = {violation['current_value']:.3f}")
            
            # Send notifications if enabled
            if violation['notification_enabled']:
                await self._send_notifications(alert)
                
            # Execute callbacks
            for callback in self.notification_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    self.logger.error(f"Notification callback failed: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Threshold violation handling failed: {str(e)}")
            
    def _is_in_cooldown(self, alert_key: str) -> bool:
        """Check if alert is in cooldown period"""
        if alert_key not in self.last_alerts:
            return False
            
        time_since_last = datetime.now() - self.last_alerts[alert_key]
        return time_since_last.total_seconds() < self.alert_cooldown
        
    async def _send_notifications(self, alert: Dict[str, Any]):
        """Send notifications for alerts"""
        try:
            # Email notification
            if self.email_config['to_emails']:
                await self._send_email_notification(alert)
                
            # Log notification
            self.logger.info(f"Alert notification sent: {alert['metric_name']} for {alert['portfolio_id']}")
            
        except Exception as e:
            self.logger.error(f"Notification sending failed: {str(e)}")
            
    async def _send_email_notification(self, alert: Dict[str, Any]):
        """Send email notification for alert"""
        try:
            subject = f"[{alert['severity']}] Quantum Portfolio Risk Alert - {alert['portfolio_id']}"
            
            body = f"""
            Quantum Portfolio Risk Alert
            
            Portfolio: {alert['portfolio_id']}
            Metric: {alert['metric_name']}
            Current Value: {alert['current_value']:.4f}
            Threshold Exceeded: {alert['threshold_exceeded']:.4f}
            Severity: {alert['severity']}
            Timestamp: {alert['timestamp']}
            
            All Risk Metrics:
            {json.dumps(alert['all_metrics'], indent=2)}
            
            Please review portfolio risk settings immediately.
            
            Quantum Portfolio Optimization System
            """
            
            # In production, would send actual email
            self.logger.info(f"Email alert: {subject}")
            
        except Exception as e:
            self.logger.error(f"Email notification failed: {str(e)}")
            
    async def _update_monitoring_history(self, session: MonitoringSession, 
                                       metrics: Dict[str, float],
                                       violations: List[Dict[str, Any]]):
        """Update monitoring history"""
        try:
            history_entry = {
                'session_id': session.session_id,
                'portfolio_id': session.portfolio_id,
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics.copy(),
                'violations': violations.copy(),
                'alert_count': session.alert_count
            }
            
            self.monitoring_history.append(history_entry)
            
            # Keep only last 1000 entries
            if len(self.monitoring_history) > 1000:
                self.monitoring_history = self.monitoring_history[-1000:]
                
        except Exception as e:
            self.logger.error(f"History update failed: {str(e)}")
            
    def add_notification_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add custom notification callback"""
        self.notification_callbacks.append(callback)
        self.logger.info("Added notification callback")
        
    def remove_notification_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Remove notification callback"""
        if callback in self.notification_callbacks:
            self.notification_callbacks.remove(callback)
            self.logger.info("Removed notification callback")
            
    def add_custom_threshold(self, threshold: RiskThreshold):
        """Add custom risk threshold"""
        self.risk_thresholds.append(threshold)
        self.logger.info(f"Added custom threshold: {threshold.metric_name}")
        
    def remove_threshold(self, metric_name: str):
        """Remove risk threshold"""
        self.risk_thresholds = [t for t in self.risk_thresholds if t.metric_name != metric_name]
        self.logger.info(f"Removed threshold: {metric_name}")
        
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        active_count = sum(1 for s in self.active_sessions.values() if s.status == 'active')
        paused_count = sum(1 for s in self.active_sessions.values() if s.status == 'paused')
        
        return {
            'total_sessions': len(self.active_sessions),
            'active_sessions': active_count,
            'paused_sessions': paused_count,
            'stopped_sessions': len(self.active_sessions) - active_count - paused_count,
            'thresholds_configured': len(self.risk_thresholds),
            'recent_alerts': len([a for a in self.last_alerts.values() 
                                if (datetime.now() - a).total_seconds() < 3600]),  # Last hour
            'monitoring_history_entries': len(self.monitoring_history),
            'timestamp': datetime.now().isoformat()
        }
        
    def get_portfolio_monitoring_history(self, portfolio_id: str, 
                                       hours: int = 24) -> List[Dict[str, Any]]:
        """Get monitoring history for specific portfolio"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            history = [
                entry for entry in self.monitoring_history
                if entry['portfolio_id'] == portfolio_id 
                and datetime.fromisoformat(entry['timestamp']) > cutoff_time
            ]
            
            return sorted(history, key=lambda x: x['timestamp'])
            
        except Exception as e:
            self.logger.error(f"History retrieval failed: {str(e)}")
            return []
        
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active monitoring sessions"""
        return [
            {
                'session_id': session.session_id,
                'portfolio_id': session.portfolio_id,
                'start_time': session.start_time.isoformat(),
                'last_update': session.last_update.isoformat(),
                'alert_count': session.alert_count,
                'status': session.status,
                'uptime_hours': (datetime.now() - session.start_time).total_seconds() / 3600
            }
            for session in self.active_sessions.values()
        ]
        
    def update_monitoring_interval(self, interval_seconds: int):
        """Update monitoring interval"""
        if interval_seconds >= 10:  # Minimum 10 seconds
            self.monitoring_interval = interval_seconds
            self.logger.info(f"Monitoring interval updated to {interval_seconds} seconds")
        else:
            self.logger.warning(f"Invalid monitoring interval: {interval_seconds}")
            
    def clear_alert_cooldown(self, alert_key: str = None):
        """Clear alert cooldown for specific alert or all"""
        if alert_key:
            self.last_alerts.pop(alert_key, None)
            self.logger.info(f"Cleared cooldown for {alert_key}")
        else:
            self.last_alerts.clear()
            self.logger.info("Cleared all alert cooldowns")

# Usage example
async def example_risk_monitoring():
    """Example risk monitoring usage"""
    # Create monitor
    monitor = PortfolioRiskMonitor({
        'monitoring_interval': 30,  # 30 seconds
        'alert_cooldown': 120,      # 2 minutes
        'smtp_server': 'smtp.example.com',
        'to_emails': ['risk.manager@example.com']
    })
    
    # Add custom notification callback
    async def slack_notification(alert: Dict[str, Any]):
        print(f"Slack notification: {alert['metric_name']} violation for {alert['portfolio_id']}")
    
    monitor.add_notification_callback(slack_notification)
    
    # Start monitoring
    session_id = await monitor.start_monitoring("example_portfolio", "Example Monitoring")
    
    print(f"Started monitoring session: {session_id}")
    
    # Run for a short time to demonstrate
    await asyncio.sleep(10)
    
    # Get status
    status = monitor.get_monitoring_status()
    print(f"Monitoring status: {status}")
    
    # Stop monitoring
    await monitor.stop_monitoring(session_id)
    print("Monitoring stopped")

if __name__ == "__main__":
    asyncio.run(example_risk_monitoring())