"""
Risk Alert System
================

Comprehensive alert and notification system for risk management.
Manages alert generation, routing, escalation, and notification delivery.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertType(Enum):
    """Types of risk alerts"""
    RISK_LIMIT_VIOLATION = "risk_limit_violation"
    POSITION_LIMIT_BREACH = "position_limit_breach"
    VAR_THRESHOLD_EXCEEDED = "var_threshold_exceeded"
    STRESS_TEST_FAILURE = "stress_test_failure"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    COMPLIANCE_VIOLATION = "compliance_violation"
    SYSTEM_ERROR = "system_error"
    MARKET_ANOMALY = "market_anomaly"
    CORRELATION_SPIKE = "correlation_spike"
    VOLATILITY_SPIKE = "volatility_spike"

class AlertStatus(Enum):
    """Alert status"""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

@dataclass
class AlertRule:
    """Alert rule definition"""
    rule_id: str
    name: str
    alert_type: AlertType
    severity: AlertSeverity
    threshold_value: float
    comparison_operator: str  # 'gt', 'lt', 'eq'
    cooldown_period: int = 300  # seconds
    enabled: bool = True
    escalation_enabled: bool = True
    escalation_delay: int = 900  # 15 minutes
    notification_channels: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class RiskAlert:
    """Risk alert structure"""
    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    status: AlertStatus
    title: str
    message: str
    timestamp: datetime
    source: str
    details: Dict[str, Any] = field(default_factory=dict)
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    escalated_to: Optional[List[str]] = field(default_factory=list)
    escalation_count: int = 0
    notification_sent: bool = False

@dataclass
class NotificationConfig:
    """Notification channel configuration"""
    email_config: Dict[str, Any] = field(default_factory=dict)
    sms_config: Dict[str, Any] = field(default_factory=dict)
    webhook_config: Dict[str, Any] = field(default_factory=dict)
    slack_config: Dict[str, Any] = field(default_factory=dict)

class RiskAlertSystem:
    """
    Comprehensive risk alert and notification system
    
    Features:
    - Rule-based alert generation
    - Multiple notification channels
    - Alert escalation and routing
    - Alert acknowledgment and resolution tracking
    - Alert analytics and reporting
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, RiskAlert] = {}
        self.alert_history: List[RiskAlert] = []
        
        # Notification configuration
        self.notification_config = NotificationConfig(**config.get('notification_config', {}))
        
        # Alert statistics
        self.alert_stats = {
            'total_alerts_generated': 0,
            'alerts_by_severity': {severity.value: 0 for severity in AlertSeverity},
            'alerts_by_type': {alert_type.value: 0 for alert_type in AlertType},
            'average_response_time': 0.0,
            'last_alert_time': None
        }
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []
        
        # Initialize default alert rules
        self._initialize_default_rules()
        
        logger.info("Risk Alert System initialized")
    
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        
        # Risk Limit Violation
        self.add_rule(AlertRule(
            rule_id="risk_limit_violation",
            name="Risk Limit Violation",
            alert_type=AlertType.RISK_LIMIT_VIOLATION,
            severity=AlertSeverity.ERROR,
            threshold_value=1.0,  # Any violation
            comparison_operator="gte",
            cooldown_period=600,  # 10 minutes
            escalation_enabled=True,
            escalation_delay=1800,  # 30 minutes
            notification_channels=["email", "webhook"]
        ))
        
        # VaR Threshold Exceeded
        self.add_rule(AlertRule(
            rule_id="var_threshold_exceeded",
            name="VaR Threshold Exceeded",
            alert_type=AlertType.VAR_THRESHOLD_EXCEEDED,
            severity=AlertSeverity.WARNING,
            threshold_value=1000000,  # $1M VaR
            comparison_operator="gte",
            cooldown_period=1800,  # 30 minutes
            escalation_enabled=True,
            escalation_delay=3600,  # 1 hour
            notification_channels=["email"]
        ))
        
        # Position Limit Breach
        self.add_rule(AlertRule(
            rule_id="position_limit_breach",
            name="Position Limit Breach",
            alert_type=AlertType.POSITION_LIMIT_BREACH,
            severity=AlertSeverity.ERROR,
            threshold_value=1.0,  # Any breach
            comparison_operator="gte",
            cooldown_period=300,  # 5 minutes
            escalation_enabled=True,
            escalation_delay=900,  # 15 minutes
            notification_channels=["email", "sms", "webhook"]
        ))
        
        # Stress Test Failure
        self.add_rule(AlertRule(
            rule_id="stress_test_failure",
            name="Stress Test Failure",
            alert_type=AlertType.STRESS_TEST_FAILURE,
            severity=AlertSeverity.CRITICAL,
            threshold_value=0.2,  # 20% portfolio loss
            comparison_operator="gte",
            cooldown_period=3600,  # 1 hour
            escalation_enabled=True,
            escalation_delay=1800,  # 30 minutes
            notification_channels=["email", "sms", "webhook", "slack"]
        ))
        
        # Liquidity Crisis
        self.add_rule(AlertRule(
            rule_id="liquidity_crisis",
            name="Liquidity Crisis",
            alert_type=AlertType.LIQUIDITY_CRISIS,
            severity=AlertSeverity.CRITICAL,
            threshold_value=0.5,  # 50% liquidity reduction
            comparison_operator="gte",
            cooldown_period=1800,  # 30 minutes
            escalation_enabled=True,
            escalation_delay=900,  # 15 minutes
            notification_channels=["email", "sms", "webhook"]
        ))
        
        # Compliance Violation
        self.add_rule(AlertRule(
            rule_id="compliance_violation",
            name="Compliance Violation",
            alert_type=AlertType.COMPLIANCE_VIOLATION,
            severity=AlertSeverity.ERROR,
            threshold_value=1.0,  # Any violation
            comparison_operator="gte",
            cooldown_period=3600,  # 1 hour
            escalation_enabled=True,
            escalation_delay=7200,  # 2 hours
            notification_channels=["email"]
        ))
        
        # System Error
        self.add_rule(AlertRule(
            rule_id="system_error",
            name="System Error",
            alert_type=AlertType.SYSTEM_ERROR,
            severity=AlertSeverity.ERROR,
            threshold_value=1.0,  # Any error
            comparison_operator="gte",
            cooldown_period=600,  # 10 minutes
            escalation_enabled=True,
            escalation_delay=1800,  # 30 minutes
            notification_channels=["email", "webhook"]
        ))
        
        # Market Anomaly
        self.add_rule(AlertRule(
            rule_id="market_anomaly",
            name="Market Anomaly",
            alert_type=AlertType.MARKET_ANOMALY,
            severity=AlertSeverity.WARNING,
            threshold_value=0.05,  # 5% price movement
            comparison_operator="gte",
            cooldown_period=1200,  # 20 minutes
            escalation_enabled=False,
            notification_channels=["webhook"]
        ))
        
        # Volatility Spike
        self.add_rule(AlertRule(
            rule_id="volatility_spike",
            name="Volatility Spike",
            alert_type=AlertType.VOLATILITY_SPIKE,
            severity=AlertSeverity.WARNING,
            threshold_value=3.0,  # 3x normal volatility
            comparison_operator="gte",
            cooldown_period=1800,  # 30 minutes
            escalation_enabled=False,
            notification_channels=["webhook", "slack"]
        ))
        
        logger.info(f"Initialized {len(self.alert_rules)} default alert rules")
    
    def add_rule(self, rule: AlertRule):
        """Add a new alert rule"""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.name}")
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove an alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")
            return True
        return False
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing alert rule"""
        if rule_id in self.alert_rules:
            rule = self.alert_rules[rule_id]
            for key, value in updates.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            logger.info(f"Updated alert rule: {rule_id}")
            return True
        return False
    
    def add_alert_callback(self, callback: Callable):
        """Add callback for alert processing"""
        self.alert_callbacks.append(callback)
    
    async def generate_alert(self, alert_type: AlertType, severity: AlertSeverity,
                           title: str, message: str, source: str,
                           details: Dict[str, Any] = None) -> str:
        """
        Generate a new risk alert
        
        Args:
            alert_type: Type of alert
            severity: Alert severity
            title: Alert title
            message: Alert message
            source: Source of the alert
            details: Additional details
            
        Returns:
            Alert ID of generated alert
        """
        try:
            # Generate unique alert ID
            alert_id = f"{alert_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # Create alert
            alert = RiskAlert(
                alert_id=alert_id,
                alert_type=alert_type,
                severity=severity,
                status=AlertStatus.NEW,
                title=title,
                message=message,
                timestamp=datetime.now(),
                source=source,
                details=details or {}
            )
            
            # Check if alert should be suppressed by cooldown
            if await self._is_alert_suppressed(alert_type, source):
                logger.debug(f"Alert {alert_id} suppressed due to cooldown")
                return alert_id
            
            # Store alert
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            # Update statistics
            self._update_alert_stats(alert)
            
            # Send notifications
            await self._send_notifications(alert)
            
            # Process callbacks
            for callback in self.alert_callbacks:
                try:
                    await callback(alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")
            
            # Setup escalation if needed
            if alert.severity in [AlertSeverity.ERROR, AlertSeverity.CRITICAL]:
                asyncio.create_task(self._setup_alert_escalation(alert))
            
            logger.info(f"Generated alert: {alert_id} - {title}")
            
            return alert_id
            
        except Exception as e:
            logger.error(f"Error generating alert: {e}")
            raise
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now()
                
                logger.info(f"Acknowledged alert: {alert_id} by {acknowledged_by}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str, resolved_by: str, resolution_notes: str = "") -> bool:
        """Resolve an alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = AlertStatus.RESOLVED
                alert.resolved_by = resolved_by
                alert.resolved_at = datetime.now()
                
                if resolution_notes:
                    alert.details['resolution_notes'] = resolution_notes
                
                logger.info(f"Resolved alert: {alert_id} by {resolved_by}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error resolving alert {alert_id}: {e}")
            return False
    
    async def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[RiskAlert]:
        """Get active alerts, optionally filtered by severity"""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        # Sort by timestamp (newest first)
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        return alerts
    
    async def get_alert_history(self, hours: int = 24) -> List[RiskAlert]:
        """Get alert history for specified period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        history = [alert for alert in self.alert_history if alert.timestamp >= cutoff_time]
        
        # Sort by timestamp (newest first)
        history.sort(key=lambda x: x.timestamp, reverse=True)
        
        return history
    
    async def send_alerts(self, alerts: List[Dict[str, Any]]) -> bool:
        """Send batch of alerts"""
        try:
            for alert_data in alerts:
                await self.generate_alert(
                    alert_type=AlertType(alert_data.get('type', AlertType.SYSTEM_ERROR.value)),
                    severity=AlertSeverity(alert_data.get('severity', AlertSeverity.INFO.value)),
                    title=alert_data.get('title', 'Risk Alert'),
                    message=alert_data.get('message', 'Risk management alert'),
                    source=alert_data.get('source', 'risk_system'),
                    details=alert_data.get('details', {})
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending batch alerts: {e}")
            return False
    
    # Private Methods
    
    def _update_alert_stats(self, alert: RiskAlert):
        """Update alert statistics"""
        self.alert_stats['total_alerts_generated'] += 1
        self.alert_stats['alerts_by_severity'][alert.severity.value] += 1
        self.alert_stats['alerts_by_type'][alert.alert_type.value] += 1
        self.alert_stats['last_alert_time'] = alert.timestamp
        
        # Update average response time (simplified)
        if alert.acknowledged_at:
            response_time = (alert.acknowledged_at - alert.timestamp).total_seconds()
            self.alert_stats['average_response_time'] = (
                (self.alert_stats['average_response_time'] * 0.9) + (response_time * 0.1)
            )
    
    async def _is_alert_suppressed(self, alert_type: AlertType, source: str) -> bool:
        """Check if alert should be suppressed due to cooldown"""
        # Find related alerts in cooldown period
        cutoff_time = datetime.now() - timedelta(seconds=300)  # 5 minutes default cooldown
        
        recent_alerts = [
            alert for alert in self.alert_history
            if (alert.alert_type == alert_type and 
                alert.source == source and 
                alert.timestamp >= cutoff_time)
        ]
        
        return len(recent_alerts) > 0
    
    async def _send_notifications(self, alert: RiskAlert):
        """Send notifications for alert"""
        try:
            # Get applicable notification channels for this alert type
            channels = self._get_notification_channels(alert.alert_type, alert.severity)
            
            for channel in channels:
                if channel == "email":
                    await self._send_email_notification(alert)
                elif channel == "sms":
                    await self._send_sms_notification(alert)
                elif channel == "webhook":
                    await self._send_webhook_notification(alert)
                elif channel == "slack":
                    await self._send_slack_notification(alert)
            
            alert.notification_sent = True
            
        except Exception as e:
            logger.error(f"Error sending notifications for alert {alert.alert_id}: {e}")
    
    def _get_notification_channels(self, alert_type: AlertType, severity: AlertSeverity) -> List[str]:
        """Get applicable notification channels for alert"""
        channels = []
        
        # Find matching alert rule
        matching_rule = None
        for rule in self.alert_rules.values():
            if rule.alert_type == alert_type and rule.enabled:
                matching_rule = rule
                break
        
        if matching_rule:
            channels = matching_rule.notification_channels
        else:
            # Default channels based on severity
            if severity == AlertSeverity.CRITICAL:
                channels = ["email", "sms", "webhook"]
            elif severity == AlertSeverity.ERROR:
                channels = ["email", "webhook"]
            elif severity == AlertSeverity.WARNING:
                channels = ["webhook"]
            else:
                channels = ["webhook"]
        
        return channels
    
    async def _send_email_notification(self, alert: RiskAlert):
        """Send email notification"""
        try:
            if not self.notification_config.email_config:
                logger.debug("Email configuration not available")
                return
            
            smtp_server = self.notification_config.email_config.get('smtp_server', 'localhost')
            smtp_port = self.notification_config.email_config.get('smtp_port', 587)
            username = self.notification_config.email_config.get('username')
            password = self.notification_config.email_config.get('password')
            from_address = self.notification_config.email_config.get('from_address', 'risk@company.com')
            to_addresses = self.notification_config.email_config.get('to_addresses', ['admin@company.com'])
            
            # Create email message
            msg = MimeMultipart()
            msg['From'] = from_address
            msg['To'] = ', '.join(to_addresses)
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
            
            # Email body
            body = f"""
Risk Management Alert

Alert ID: {alert.alert_id}
Type: {alert.alert_type.value}
Severity: {alert.severity.value}
Status: {alert.status.value}
Timestamp: {alert.timestamp}

Message: {alert.message}

Source: {alert.source}

Details:
{json.dumps(alert.details, indent=2, default=str)}

Please take appropriate action.
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Send email (simplified - would use proper SMTP authentication)
            if username and password:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(username, password)
                server.send_message(msg)
                server.quit()
            else:
                # Local delivery
                server = smtplib.SMTP(smtp_server)
                server.send_message(msg)
                server.quit()
            
            logger.info(f"Email notification sent for alert: {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    async def _send_sms_notification(self, alert: RiskAlert):
        """Send SMS notification (placeholder)"""
        try:
            # This would integrate with SMS service like Twilio
            logger.info(f"SMS notification would be sent for alert: {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {e}")
    
    async def _send_webhook_notification(self, alert: RiskAlert):
        """Send webhook notification"""
        try:
            if not self.notification_config.webhook_config:
                return
            
            webhook_url = self.notification_config.webhook_config.get('url')
            if not webhook_url:
                return
            
            import aiohttp
            
            payload = {
                'alert_id': alert.alert_id,
                'type': alert.alert_type.value,
                'severity': alert.severity.value,
                'title': alert.title,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'source': alert.source,
                'details': alert.details
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Webhook notification sent for alert: {alert.alert_id}")
                    else:
                        logger.error(f"Webhook notification failed: {response.status}")
            
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")
    
    async def _send_slack_notification(self, alert: RiskAlert):
        """Send Slack notification (placeholder)"""
        try:
            # This would integrate with Slack API
            logger.info(f"Slack notification would be sent for alert: {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
    
    async def _setup_alert_escalation(self, alert: RiskAlert):
        """Setup alert escalation"""
        try:
            # Find matching rule for escalation settings
            matching_rule = None
            for rule in self.alert_rules.values():
                if rule.alert_type == alert.alert_type:
                    matching_rule = rule
                    break
            
            if matching_rule and matching_rule.escalation_enabled:
                await asyncio.sleep(matching_rule.escalation_delay)
                
                # Check if alert is still active
                if alert.alert_id in self.active_alerts and alert.status == AlertStatus.NEW:
                    # Escalate alert
                    alert.status = AlertStatus.ESCALATED
                    alert.escalation_count += 1
                    
                    # Send escalation notifications
                    await self._send_escalation_notifications(alert)
                    
                    logger.warning(f"Escalated alert: {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Error setting up alert escalation: {e}")
    
    async def _send_escalation_notifications(self, alert: RiskAlert):
        """Send escalation notifications"""
        try:
            # This would send notifications to escalation contacts
            logger.info(f"Escalation notifications would be sent for alert: {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Error sending escalation notifications: {e}")
    
    # Utility Methods
    
    async def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert system statistics"""
        active_alerts_count = len(self.active_alerts)
        unacknowledged_alerts = len([a for a in self.active_alerts.values() if a.status == AlertStatus.NEW])
        acknowledged_alerts = len([a for a in self.active_alerts.values() if a.status == AlertStatus.ACKNOWLEDGED])
        
        return {
            'timestamp': datetime.now(),
            'active_alerts': active_alerts_count,
            'unacknowledged_alerts': unacknowledged_alerts,
            'acknowledged_alerts': acknowledged_alerts,
            'total_alerts_generated': self.alert_stats['total_alerts_generated'],
            'alerts_by_severity': self.alert_stats['alerts_by_severity'].copy(),
            'alerts_by_type': self.alert_stats['alerts_by_type'].copy(),
            'average_response_time': self.alert_stats['average_response_time'],
            'last_alert_time': self.alert_stats['last_alert_time'],
            'configured_rules': len(self.alert_rules)
        }
    
    async def cleanup_resolved_alerts(self, days: int = 30):
        """Clean up old resolved alerts"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # Remove from active alerts
        resolved_alerts = [
            alert_id for alert_id, alert in self.active_alerts.items()
            if alert.status == AlertStatus.RESOLVED and alert.resolved_at and alert.resolved_at < cutoff_time
        ]
        
        for alert_id in resolved_alerts:
            del self.active_alerts[alert_id]
        
        # Limit history size
        if len(self.alert_history) > 10000:
            self.alert_history = self.alert_history[-5000:]  # Keep last 5000
        
        logger.info(f"Cleaned up {len(resolved_alerts)} old resolved alerts")
    
    async def export_alert_data(self, format_type: str = 'json') -> str:
        """Export alert data"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'statistics': await self.get_alert_statistics(),
            'alert_rules': [
                {
                    'rule_id': rule.rule_id,
                    'name': rule.name,
                    'alert_type': rule.alert_type.value,
                    'severity': rule.severity.value,
                    'enabled': rule.enabled,
                    'escalation_enabled': rule.escalation_enabled
                }
                for rule in self.alert_rules.values()
            ],
            'recent_alerts': [
                {
                    'alert_id': alert.alert_id,
                    'type': alert.alert_type.value,
                    'severity': alert.severity.value,
                    'status': alert.status.value,
                    'title': alert.title,
                    'timestamp': alert.timestamp.isoformat(),
                    'acknowledged': alert.acknowledged_at is not None,
                    'resolved': alert.resolved_at is not None
                }
                for alert in self.alert_history[-100:]  # Last 100 alerts
            ]
        }
        
        if format_type.lower() == 'json':
            return json.dumps(export_data, indent=2, default=str)
        else:
            return str(export_data)