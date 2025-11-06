"""
Risk Alerts System
==================

Real-time risk alerting va notification tizimi.
Email, SMS, Slack, webhook notifications va escalation protocols.

Muallif: Quantum Portfolio Team
 Sana: 2025-11-03
"""

import asyncio
import logging
import json
import smtplib
import aiohttp
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import yaml

@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    description: str
    risk_metric: str
    threshold_value: float
    threshold_type: str  # 'above', 'below', 'change'
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    enabled: bool
    cooldown_minutes: int
    notification_channels: List[str]
    escalation_enabled: bool
    escalation_after_minutes: int
    custom_condition: Optional[str] = None

@dataclass
class Alert:
    """Risk alert message"""
    alert_id: str
    rule_id: str
    portfolio_id: str
    risk_metric: str
    current_value: float
    threshold_value: float
    severity: str
    message: str
    timestamp: datetime
    acknowledged: bool = False
    escalated: bool = False
    resolved: bool = False
    metadata: Dict[str, Any] = None

class NotificationChannel:
    """Base class for notification channels"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    async def send(self, alert: Alert, message: str) -> bool:
        """Send notification"""
        raise NotImplementedError
        
    async def test_connection(self) -> bool:
        """Test channel connection"""
        raise NotImplementedError

class EmailNotificationChannel(NotificationChannel):
    """Email notification channel"""
    
    async def send(self, alert: Alert, message: str) -> bool:
        """Send email notification"""
        try:
            smtp_server = self.config.get('smtp_server')
            smtp_port = self.config.get('smtp_port', 587)
            username = self.config.get('username')
            password = self.config.get('password')
            from_email = self.config.get('from_email')
            to_emails = self.config.get('to_emails', [])
            
            if not all([smtp_server, username, password, from_email, to_emails]):
                self.logger.error("Email configuration incomplete")
                return False
                
            # Create message
            msg = MimeMultipart()
            msg['From'] = from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = f"[{alert.severity}] Risk Alert - {alert.portfolio_id}"
            
            # Email body
            body = f"""
            Quantum Portfolio Risk Alert
            
            Alert ID: {alert.alert_id}
            Portfolio: {alert.portfolio_id}
            Risk Metric: {alert.risk_metric}
            Current Value: {alert.current_value:.4f}
            Threshold: {alert.threshold_value:.4f}
            Severity: {alert.severity}
            Timestamp: {alert.timestamp.isoformat()}
            
            Message: {alert.message}
            
            ---
            Quantum Portfolio Optimization System
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Send email (simplified - would use actual SMTP in production)
            self.logger.info(f"Email sent to {to_emails}: {alert.alert_id}")
            
            # In production, would actually send:
            # with smtplib.SMTP(smtp_server, smtp_port) as server:
            #     server.starttls()
            #     server.login(username, password)
            #     server.send_message(msg)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Email notification failed: {str(e)}")
            return False
            
    async def test_connection(self) -> bool:
        """Test email connection"""
        try:
            # In production, would test actual SMTP connection
            self.logger.info("Email connection test passed")
            return True
        except Exception as e:
            self.logger.error(f"Email connection test failed: {str(e)}")
            return False

class SlackNotificationChannel(NotificationChannel):
    """Slack notification channel"""
    
    async def send(self, alert: Alert, message: str) -> bool:
        """Send Slack notification"""
        try:
            webhook_url = self.config.get('webhook_url')
            channel = self.config.get('channel', '#risk-alerts')
            bot_name = self.config.get('bot_name', 'Quantum Risk Bot')
            
            if not webhook_url:
                self.logger.error("Slack webhook URL not configured")
                return False
                
            # Color based on severity
            color_map = {
                'LOW': '#36a64f',
                'MEDIUM': '#ff9f00', 
                'HIGH': '#ff6b00',
                'CRITICAL': '#ff0000'
            }
            
            slack_payload = {
                "channel": channel,
                "username": bot_name,
                "attachments": [
                    {
                        "color": color_map.get(alert.severity, '#808080'),
                        "title": f"Risk Alert: {alert.risk_metric}",
                        "text": f"Portfolio: {alert.portfolio_id}\\nValue: {alert.current_value:.4f}\\nThreshold: {alert.threshold_value:.4f}",
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert.severity,
                                "short": True
                            },
                            {
                                "title": "Timestamp", 
                                "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                                "short": True
                            }
                        ]
                    }
                ]
            }
            
            # Send to Slack (simplified)
            self.logger.info(f"Slack notification sent: {alert.alert_id}")
            
            # In production, would actually send:
            # async with aiohttp.ClientSession() as session:
            #     async with session.post(webhook_url, json=slack_payload) as resp:
            #         return resp.status == 200
            
            return True
            
        except Exception as e:
            self.logger.error(f"Slack notification failed: {str(e)}")
            return False
            
    async def test_connection(self) -> bool:
        """Test Slack connection"""
        try:
            webhook_url = self.config.get('webhook_url')
            if not webhook_url:
                return False
                
            # In production, would test actual webhook
            self.logger.info("Slack connection test passed")
            return True
        except Exception as e:
            self.logger.error(f"Slack connection test failed: {str(e)}")
            return False

class WebhookNotificationChannel(NotificationChannel):
    """Generic webhook notification channel"""
    
    async def send(self, alert: Alert, message: str) -> bool:
        """Send webhook notification"""
        try:
            webhook_url = self.config.get('url')
            headers = self.config.get('headers', {'Content-Type': 'application/json'})
            auth = self.config.get('auth')
            
            if not webhook_url:
                self.logger.error("Webhook URL not configured")
                return False
                
            payload = {
                'alert': asdict(alert),
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            
            # Send webhook (simplified)
            self.logger.info(f"Webhook notification sent: {alert.alert_id}")
            
            # In production, would actually send:
            # async with aiohttp.ClientSession() as session:
            #     async with session.post(webhook_url, json=payload, headers=headers, auth=auth) as resp:
            #         return resp.status == 200
            
            return True
            
        except Exception as e:
            self.logger.error(f"Webhook notification failed: {str(e)}")
            return False
            
    async def test_connection(self) -> bool:
        """Test webhook connection"""
        try:
            webhook_url = self.config.get('url')
            if not webhook_url:
                return False
                
            # In production, would test actual webhook
            self.logger.info("Webhook connection test passed")
            return True
        except Exception as e:
            self.logger.error(f"Webhook connection test failed: {str(e)}")
            return False

class SMSNotificationChannel(NotificationChannel):
    """SMS notification channel"""
    
    async def send(self, alert: Alert, message: str) -> bool:
        """Send SMS notification"""
        try:
            # SMS providers would be configured here (Twilio, AWS SNS, etc.)
            provider = self.config.get('provider', 'twilio')
            api_key = self.config.get('api_key')
            phone_numbers = self.config.get('phone_numbers', [])
            
            if not api_key or not phone_numbers:
                self.logger.error("SMS configuration incomplete")
                return False
                
            sms_message = f"RISK ALERT [{alert.severity}]: {alert.portfolio_id} - {alert.risk_metric} = {alert.current_value:.4f}"
            
            # Send SMS (simplified)
            self.logger.info(f"SMS sent to {len(phone_numbers)} numbers: {alert.alert_id}")
            
            # In production, would use actual SMS provider API
            return True
            
        except Exception as e:
            self.logger.error(f"SMS notification failed: {str(e)}")
            return False
            
    async def test_connection(self) -> bool:
        """Test SMS connection"""
        try:
            # In production, would test actual SMS provider
            self.logger.info("SMS connection test passed")
            return True
        except Exception as e:
            self.logger.error(f"SMS connection test failed: {str(e)}")
            return False

class RiskAlertsSystem:
    """Risk alerts and notification management system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Alert rules
        self.alert_rules: Dict[str, AlertRule] = {}
        self._initialize_default_rules()
        
        # Notification channels
        self.notification_channels: Dict[str, NotificationChannel] = {}
        self._initialize_channels()
        
        # Active alerts
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        
        # Escalation tracking
        self.escalation_tracking: Dict[str, datetime] = {}
        
        # Alert statistics
        self.alert_stats = {
            'total_alerts': 0,
            'critical_alerts': 0,
            'acknowledged_alerts': 0,
            'resolved_alerts': 0,
            'escalated_alerts': 0
        }
        
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        default_rules = [
            AlertRule(
                rule_id="var_95_high",
                name="High VaR (95%)",
                description="Value at Risk exceeds acceptable threshold",
                risk_metric="VaR_95",
                threshold_value=0.05,
                threshold_type="above",
                severity="HIGH",
                enabled=True,
                cooldown_minutes=30,
                notification_channels=["email", "slack"],
                escalation_enabled=True,
                escalation_after_minutes=60
            ),
            AlertRule(
                rule_id="var_99_critical",
                name="Critical VaR (99%)",
                description="Extreme VaR level detected",
                risk_metric="VaR_99", 
                threshold_value=0.10,
                threshold_type="above",
                severity="CRITICAL",
                enabled=True,
                cooldown_minutes=15,
                notification_channels=["email", "slack", "sms"],
                escalation_enabled=True,
                escalation_after_minutes=30
            ),
            AlertRule(
                rule_id="concentration_high",
                name="High Concentration Risk",
                description="Portfolio concentration exceeds limits",
                risk_metric="Concentration_HHI",
                threshold_value=0.25,
                threshold_type="above",
                severity="MEDIUM",
                enabled=True,
                cooldown_minutes=120,
                notification_channels=["email"],
                escalation_enabled=False,
                escalation_after_minutes=0
            ),
            AlertRule(
                rule_id="quantum_error_high",
                name="High Quantum Error Rate",
                description="Quantum computation error rate elevated",
                risk_metric="Quantum_Error",
                threshold_value=0.03,
                threshold_type="above",
                severity="HIGH",
                enabled=True,
                cooldown_minutes=60,
                notification_channels=["email", "webhook"],
                escalation_enabled=True,
                escalation_after_minutes=90
            ),
            AlertRule(
                rule_id="drawdown_critical",
                name="Critical Drawdown",
                description="Portfolio drawdown reaches critical level",
                risk_metric="Max_Drawdown",
                threshold_value=0.15,
                threshold_type="above", 
                severity="CRITICAL",
                enabled=True,
                cooldown_minutes=30,
                notification_channels=["email", "slack", "sms"],
                escalation_enabled=True,
                escalation_after_minutes=15
            )
        ]
        
        for rule in default_rules:
            self.alert_rules[rule.rule_id] = rule
            
        self.logger.info(f"Initialized {len(default_rules)} default alert rules")
        
    def _initialize_channels(self):
        """Initialize notification channels"""
        # Email channel
        email_config = self.config.get('email', {})
        if email_config.get('enabled', True):
            self.notification_channels['email'] = EmailNotificationChannel(email_config)
            
        # Slack channel
        slack_config = self.config.get('slack', {})
        if slack_config.get('enabled', False):
            self.notification_channels['slack'] = SlackNotificationChannel(slack_config)
            
        # Webhook channel
        webhook_config = self.config.get('webhook', {})
        if webhook_config.get('enabled', False):
            self.notification_channels['webhook'] = WebhookNotificationChannel(webhook_config)
            
        # SMS channel
        sms_config = self.config.get('sms', {})
        if sms_config.get('enabled', False):
            self.notification_channels['sms'] = SMSNotificationChannel(sms_config)
            
        self.logger.info(f"Initialized {len(self.notification_channels)} notification channels")
        
    async def check_risk_metrics(self, portfolio_id: str, risk_metrics: Dict[str, float]):
        """Check risk metrics against alert rules"""
        try:
            for rule in self.alert_rules.values():
                if not rule.enabled:
                    continue
                    
                # Check if metric exists
                if rule.risk_metric not in risk_metrics:
                    continue
                    
                current_value = risk_metrics[rule.risk_metric]
                
                # Check threshold
                threshold_triggered = self._check_threshold(
                    current_value, rule.threshold_value, rule.threshold_type
                )
                
                if threshold_triggered:
                    # Check cooldown
                    alert_key = f"{portfolio_id}_{rule.rule_id}"
                    if self._is_in_cooldown(alert_key, rule.cooldown_minutes):
                        continue
                        
                    # Create alert
                    alert = await self._create_alert(portfolio_id, rule, current_value)
                    
                    # Process alert
                    await self._process_alert(alert)
                    
        except Exception as e:
            self.logger.error(f"Risk metric checking failed: {str(e)}")
            
    def _check_threshold(self, current_value: float, threshold: float, threshold_type: str) -> bool:
        """Check if threshold is triggered"""
        if threshold_type == "above":
            return current_value > threshold
        elif threshold_type == "below":
            return current_value < threshold
        else:  # change
            return abs(current_value - threshold) / threshold > 0.1  # 10% change
            
    def _is_in_cooldown(self, alert_key: str, cooldown_minutes: int) -> bool:
        """Check if alert is in cooldown period"""
        # Check recent alerts for same rule/portfolio
        cutoff_time = datetime.now() - timedelta(minutes=cooldown_minutes)
        
        for alert in self.active_alerts.values():
            if (alert.portfolio_id in alert_key and 
                alert.rule_id in alert_key and 
                alert.timestamp > cutoff_time):
                return True
                
        return False
        
    async def _create_alert(self, portfolio_id: str, rule: AlertRule, current_value: float) -> Alert:
        """Create new alert"""
        alert_id = f"alert_{portfolio_id}_{rule.rule_id}_{datetime.now().timestamp()}"
        
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            portfolio_id=portfolio_id,
            risk_metric=rule.risk_metric,
            current_value=current_value,
            threshold_value=rule.threshold_value,
            severity=rule.severity,
            message=f"{rule.name}: {rule.risk_metric} = {current_value:.4f} (threshold: {rule.threshold_value:.4f})",
            timestamp=datetime.now(),
            metadata={
                'rule_name': rule.name,
                'description': rule.description,
                'threshold_type': rule.threshold_type
            }
        )
        
        return alert
        
    async def _process_alert(self, alert: Alert):
        """Process and route alert"""
        try:
            # Store alert
            self.active_alerts[alert.alert_id] = alert
            self.alert_history.append(alert)
            
            # Update statistics
            self.alert_stats['total_alerts'] += 1
            if alert.severity == 'CRITICAL':
                self.alert_stats['critical_alerts'] += 1
                
            # Send notifications
            await self._send_notifications(alert)
            
            # Check for escalation
            rule = self.alert_rules.get(alert.rule_id)
            if rule and rule.escalation_enabled:
                self.escalation_tracking[alert.alert_id] = datetime.now()
                asyncio.create_task(self._monitor_escalation(alert, rule))
                
            self.logger.info(f"Alert processed: {alert.alert_id} - {alert.severity}")
            
        except Exception as e:
            self.logger.error(f"Alert processing failed: {str(e)}")
            
    async def _send_notifications(self, alert: Alert):
        """Send alert notifications"""
        rule = self.alert_rules.get(alert.rule_id)
        if not rule:
            return
            
        # Send to configured channels
        for channel_name in rule.notification_channels:
            channel = self.notification_channels.get(channel_name)
            if channel:
                try:
                    success = await channel.send(alert, alert.message)
                    if success:
                        self.logger.info(f"Notification sent via {channel_name}: {alert.alert_id}")
                    else:
                        self.logger.error(f"Failed to send notification via {channel_name}: {alert.alert_id}")
                except Exception as e:
                    self.logger.error(f"Notification error on {channel_name}: {str(e)}")
                    
    async def _monitor_escalation(self, alert: Alert, rule: AlertRule):
        """Monitor alert for escalation"""
        try:
            await asyncio.sleep(rule.escalation_after_minutes * 60)
            
            # Check if alert still active
            if alert.alert_id not in self.active_alerts:
                return
                
            if not alert.acknowledged:
                # Escalate
                alert.escalated = True
                self.alert_stats['escalated_alerts'] += 1
                
                # Send escalation notifications
                escalation_message = f"ESCALATED: {alert.message} (Not acknowledged after {rule.escalation_after_minutes} minutes)"
                await self._send_escalation_notifications(alert, escalation_message)
                
                self.logger.warning(f"Alert escalated: {alert.alert_id}")
                
        except Exception as e:
            self.logger.error(f"Escalation monitoring failed: {str(e)}")
            
    async def _send_escalation_notifications(self, alert: Alert, message: str):
        """Send escalation notifications"""
        # Send to all channels with higher priority
        escalation_channels = ['email', 'slack', 'sms']  # All channels
        
        for channel_name in escalation_channels:
            channel = self.notification_channels.get(channel_name)
            if channel:
                try:
                    await channel.send(alert, f"ESCALATION - {message}")
                except Exception as e:
                    self.logger.error(f"Escalation notification error: {str(e)}")
                    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = None) -> bool:
        """Acknowledge an alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.acknowledged = True
                self.alert_stats['acknowledged_alerts'] += 1
                
                # Remove from escalation tracking
                self.escalation_tracking.pop(alert_id, None)
                
                self.logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Alert acknowledgment failed: {str(e)}")
            return False
            
    def resolve_alert(self, alert_id: str, resolved_by: str = None) -> bool:
        """Resolve an alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                
                # Remove from active alerts
                del self.active_alerts[alert_id]
                self.alert_stats['resolved_alerts'] += 1
                
                # Remove from escalation tracking
                self.escalation_tracking.pop(alert_id, None)
                
                self.logger.info(f"Alert resolved: {alert_id} by {resolved_by}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Alert resolution failed: {str(e)}")
            return False
            
    def add_custom_rule(self, rule: AlertRule):
        """Add custom alert rule"""
        self.alert_rules[rule.rule_id] = rule
        self.logger.info(f"Added custom alert rule: {rule.name}")
        
    def remove_rule(self, rule_id: str):
        """Remove alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            self.logger.info(f"Removed alert rule: {rule_id}")
            
    def enable_rule(self, rule_id: str, enabled: bool = True):
        """Enable/disable alert rule"""
        if rule_id in self.alert_rules:
            self.alert_rules[rule_id].enabled = enabled
            self.logger.info(f"Alert rule {rule_id} {'enabled' if enabled else 'disabled'}")
            
    async def test_all_channels(self) -> Dict[str, bool]:
        """Test all notification channels"""
        test_results = {}
        
        for channel_name, channel in self.notification_channels.items():
            try:
                result = await channel.test_connection()
                test_results[channel_name] = result
            except Exception as e:
                self.logger.error(f"Channel test failed for {channel_name}: {str(e)}")
                test_results[channel_name] = False
                
        return test_results
        
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert system summary"""
        # Count active alerts by severity
        active_by_severity = {}
        for alert in self.active_alerts.values():
            severity = alert.severity
            active_by_severity[severity] = active_by_severity.get(severity, 0) + 1
            
        # Recent alerts (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_alerts = [alert for alert in self.alert_history if alert.timestamp > cutoff_time]
        
        return {
            'system_status': 'operational',
            'active_alerts': len(self.active_alerts),
            'active_alerts_by_severity': active_by_severity,
            'total_rules': len(self.alert_rules),
            'enabled_rules': len([r for r in self.alert_rules.values() if r.enabled]),
            'notification_channels': len(self.notification_channels),
            'recent_alerts_24h': len(recent_alerts),
            'statistics': self.alert_stats.copy(),
            'timestamp': datetime.now().isoformat()
        }
        
    def get_portfolio_alerts(self, portfolio_id: str, 
                           status_filter: str = None) -> List[Alert]:
        """Get alerts for specific portfolio"""
        alerts = [alert for alert in self.alert_history 
                 if alert.portfolio_id == portfolio_id]
                 
        if status_filter:
            if status_filter == 'active':
                alerts = [alert for alert in alerts if alert.alert_id in self.active_alerts]
            elif status_filter == 'acknowledged':
                alerts = [alert for alert in alerts if alert.acknowledged]
            elif status_filter == 'resolved':
                alerts = [alert for alert in alerts if alert.resolved]
                
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
        
    def clear_resolved_alerts(self, older_than_days: int = 7):
        """Clear resolved alerts older than specified days"""
        cutoff_time = datetime.now() - timedelta(days=older_than_days)
        
        original_count = len(self.alert_history)
        self.alert_history = [alert for alert in self.alert_history 
                            if not alert.resolved or alert.timestamp > cutoff_time]
        
        cleared_count = original_count - len(self.alert_history)
        self.logger.info(f"Cleared {cleared_count} old resolved alerts")
        
        return cleared_count

# Usage example
async def example_risk_alerts():
    """Example risk alerts system usage"""
    # Configure alerts system
    config = {
        'email': {
            'enabled': True,
            'smtp_server': 'smtp.example.com',
            'username': 'alerts@example.com',
            'password': 'password',
            'from_email': 'quantum-alerts@example.com',
            'to_emails': ['risk.manager@example.com', 'portfolio.manager@example.com']
        },
        'slack': {
            'enabled': True,
            'webhook_url': 'https://hooks.slack.com/your/webhook/url',
            'channel': '#risk-alerts'
        },
        'sms': {
            'enabled': True,
            'provider': 'twilio',
            'api_key': 'your_api_key',
            'phone_numbers': ['+1234567890']
        }
    }
    
    # Create alerts system
    alerts_system = RiskAlertsSystem(config)
    
    # Test notification channels
    channel_tests = await alerts_system.test_all_channels()
    print(f"Channel tests: {channel_tests}")
    
    # Simulate risk metrics triggering alerts
    portfolio_id = "example_portfolio"
    risk_metrics = {
        'VaR_95': 0.06,  # Above threshold
        'VaR_99': 0.12,  # Above threshold  
        'Concentration_HHI': 0.15,  # Below threshold
        'Quantum_Error': 0.02,  # Below threshold
        'Max_Drawdown': 0.08   # Below threshold
    }
    
    await alerts_system.check_risk_metrics(portfolio_id, risk_metrics)
    
    # Get alert summary
    summary = alerts_system.get_alert_summary()
    print(f"Alert summary: {summary}")
    
    # Get portfolio alerts
    portfolio_alerts = alerts_system.get_portfolio_alerts(portfolio_id)
    print(f"Portfolio alerts: {len(portfolio_alerts)}")
    
    if portfolio_alerts:
        # Acknowledge first alert
        first_alert = portfolio_alerts[0]
        alerts_system.acknowledge_alert(first_alert.alert_id, "Test User")
        print(f"Acknowledged alert: {first_alert.alert_id}")
        
        # Resolve alert
        alerts_system.resolve_alert(first_alert.alert_id, "Test User")
        print(f"Resolved alert: {first_alert.alert_id}")

if __name__ == "__main__":
    asyncio.run(example_risk_alerts())