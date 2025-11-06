"""
Security Monitoring Moduli
==========================

Bu modul quyidagi monitoring funksiyalarini ta'minlaydi:
- Security event monitoring
- Intrusion detection
- Anomaly detection
- Security dashboards
- Incident response
- Real-time alerting

@author: Security Team
@version: 1.0.0
"""

import time
import json
import threading
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum
import queue
import logging

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security darajalar"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class IncidentStatus(Enum):
    """Incident holatlar"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class SecurityEvent:
    """Security event ma'lumotlari"""
    event_id: str
    timestamp: datetime
    event_type: str
    source_ip: str
    user_agent: str
    severity: SecurityLevel
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[str] = None


@dataclass
class Incident:
    """Incident ma'lumotlari"""
    incident_id: str
    title: str
    description: str
    severity: SecurityLevel
    status: IncidentStatus
    created_at: datetime
    events: List[str] = field(default_factory=list)  # Event IDs
    affected_systems: List[str] = field(default_factory=list)
    assigned_team: List[str] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    resolution: Optional[str] = None


@dataclass
class AlertRule:
    """Alert rule konfiguratsiyasi"""
    rule_id: str
    name: str
    condition: Dict[str, Any]
    severity: SecurityLevel
    enabled: bool = True
    cooldown_period: int = 300  # 5 minutes
    last_triggered: Optional[datetime] = None
    notification_channels: List[str] = field(default_factory=list)


class AnomalyDetector:
    """Anomaly detection moduli"""
    
    def __init__(self):
        self.baselines: Dict[str, Dict[str, Any]] = {}
        self.anomaly_history: deque = deque(maxlen=10000)
        self.detection_models = {}
        self._setup_default_models()
    
    def _setup_default_models(self):
        """Default detection modellari"""
        self.detection_models = {
            'request_rate': self._detect_rate_anomaly,
            'failed_logins': self._detect_login_anomaly,
            'data_access': self._detect_access_anomaly,
            'api_usage': self._detect_api_anomaly,
            'traffic_pattern': self._detect_traffic_anomaly
        }
    
    def establish_baseline(self, metric_name: str, data: List[float], 
                          time_window: int = 3600) -> Dict[str, float]:
        """Baseline o'rnatish"""
        if not data:
            return {}
        
        # Calculate statistics
        sorted_data = sorted(data)
        n = len(sorted_data)
        
        baseline = {
            'mean': sum(data) / len(data),
            'std_dev': self._calculate_std_dev(data),
            'median': sorted_data[n // 2],
            'p95': sorted_data[int(0.95 * n)] if n > 0 else 0,
            'p99': sorted_data[int(0.99 * n)] if n > 0 else 0,
            'min': min(data),
            'max': max(data),
            'sample_size': len(data),
            'timestamp': datetime.now()
        }
        
        self.baselines[metric_name] = baseline
        logger.info(f"Established baseline for {metric_name}: mean={baseline['mean']:.2f}")
        
        return baseline
    
    def detect_anomalies(self, metric_name: str, current_value: float) -> Tuple[bool, float, str]:
        """Anomaly detection"""
        if metric_name not in self.baselines:
            # First data point - can't detect anomaly
            return False, 0.0, "No baseline established"
        
        baseline = self.baselines[metric_name]
        
        # Calculate z-score
        z_score = (current_value - baseline['mean']) / max(baseline['std_dev'], 1)
        
        # Anomaly thresholds
        if abs(z_score) > 4.0:  # Very high anomaly
            confidence = min(abs(z_score) / 6.0, 1.0)
            return True, confidence, f"Extreme anomaly detected (z-score: {z_score:.2f})"
        elif abs(z_score) > 3.0:  # High anomaly
            confidence = min(abs(z_score) / 4.0, 1.0)
            return True, confidence, f"High anomaly detected (z-score: {z_score:.2f})"
        elif abs(z_score) > 2.0:  # Medium anomaly
            confidence = min(abs(z_score) / 3.0, 1.0)
            return True, confidence, f"Medium anomaly detected (z-score: {z_score:.2f})"
        
        return False, 0.0, "Normal behavior"
    
    def _calculate_std_dev(self, data: List[float]) -> float:
        """Standard deviation hisoblash"""
        if len(data) < 2:
            return 1.0
        
        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / (len(data) - 1)
        return variance ** 0.5
    
    def _detect_rate_anomaly(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Request rate anomaly detection"""
        anomalies = []
        current_rate = data.get('requests_per_minute', 0)
        
        is_anomaly, confidence, message = self.detect_anomalies('request_rate', current_rate)
        
        if is_anomaly:
            anomalies.append({
                'type': 'rate_anomaly',
                'message': message,
                'confidence': confidence,
                'current_value': current_rate,
                'baseline': self.baselines.get('request_rate', {})
            })
        
        return anomalies
    
    def _detect_login_anomaly(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Login anomaly detection"""
        anomalies = []
        failed_logins = data.get('failed_logins', 0)
        
        is_anomaly, confidence, message = self.detect_anomalies('failed_logins', failed_logins)
        
        if is_anomaly:
            anomalies.append({
                'type': 'login_anomaly',
                'message': message,
                'confidence': confidence,
                'current_value': failed_logins,
                'baseline': self.baselines.get('failed_logins', {})
            })
        
        return anomalies
    
    def _detect_access_anomaly(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Data access anomaly detection"""
        anomalies = []
        unique_ips = len(data.get('accessing_ips', []))
        
        is_anomaly, confidence, message = self.detect_anomalies('data_access', unique_ips)
        
        if is_anomaly:
            anomalies.append({
                'type': 'access_anomaly',
                'message': message,
                'confidence': confidence,
                'current_value': unique_ips,
                'baseline': self.baselines.get('data_access', {})
            })
        
        return anomalies
    
    def _detect_api_anomaly(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """API usage anomaly detection"""
        anomalies = []
        error_rate = data.get('api_error_rate', 0.0)
        
        is_anomaly, confidence, message = self.detect_anomalies('api_error_rate', error_rate)
        
        if is_anomaly:
            anomalies.append({
                'type': 'api_anomaly',
                'message': message,
                'confidence': confidence,
                'current_value': error_rate,
                'baseline': self.baselines.get('api_error_rate', {})
            })
        
        return anomalies
    
    def _detect_traffic_anomaly(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Traffic pattern anomaly detection"""
        anomalies = []
        traffic_volume = data.get('bytes_per_minute', 0)
        
        is_anomaly, confidence, message = self.detect_anomalies('traffic_volume', traffic_volume)
        
        if is_anomaly:
            anomalies.append({
                'type': 'traffic_anomaly',
                'message': message,
                'confidence': confidence,
                'current_value': traffic_volume,
                'baseline': self.baselines.get('traffic_volume', {})
            })
        
        return anomalies


class SecurityMonitor:
    """Asosiy Security Monitor"""
    
    def __init__(self):
        self.events: Dict[str, SecurityEvent] = {}
        self.incidents: Dict[str, Incident] = {}
        self.alert_rules: Dict[str, AlertRule] = {}
        self.event_queue = queue.Queue()
        self.notification_handlers: Dict[str, Callable] = {}
        
        # Statistics
        self.event_stats = defaultdict(int)
        self.metrics_history = defaultdict(lambda: deque(maxlen=1440))  # 24 hours at 1-minute intervals
        
        # Threads
        self.monitoring_thread = None
        self.alert_thread = None
        self.running = False
        
        # Anomaly detector
        self.anomaly_detector = AnomalyDetector()
        
        # Setup default alert rules
        self._setup_default_alert_rules()
    
    def _setup_default_alert_rules(self):
        """Default alert qoidalari"""
        rules = [
            AlertRule(
                rule_id="multiple_failed_logins",
                name="Multiple Failed Login Attempts",
                condition={"event_type": "failed_login", "threshold": 5, "window": 300},
                severity=SecurityLevel.HIGH,
                notification_channels=["email", "slack"]
            ),
            AlertRule(
                rule_id="rate_limit_exceeded",
                name="Rate Limit Exceeded",
                condition={"event_type": "rate_limit_exceeded", "threshold": 3, "window": 60},
                severity=SecurityLevel.MEDIUM,
                notification_channels=["email"]
            ),
            AlertRule(
                rule_id="suspicious_file_upload",
                name="Suspicious File Upload",
                condition={"event_type": "file_upload", "threat_detected": True},
                severity=SecurityLevel.HIGH,
                notification_channels=["email", "slack", "sms"]
            ),
            AlertRule(
                rule_id="sql_injection_attempt",
                name="SQL Injection Attempt",
                condition={"event_type": "security_violation", "violation_type": "sql_injection"},
                severity=SecurityLevel.CRITICAL,
                notification_channels=["email", "slack", "sms"]
            )
        ]
        
        for rule in rules:
            self.alert_rules[rule.rule_id] = rule
    
    def start_monitoring(self):
        """Monitoring boshlanishi"""
        if self.running:
            return
        
        self.running = True
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # Start alert thread
        self.alert_thread = threading.Thread(target=self._alert_loop, daemon=True)
        self.alert_thread.start()
        
        logger.info("Security monitoring started")
    
    def stop_monitoring(self):
        """Monitoring to'xtashi"""
        self.running = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        if self.alert_thread:
            self.alert_thread.join(timeout=5)
        
        logger.info("Security monitoring stopped")
    
    def _monitoring_loop(self):
        """Asosiy monitoring loop"""
        while self.running:
            try:
                # Process events from queue
                while not self.event_queue.empty():
                    event_data = self.event_queue.get_nowait()
                    self._process_event(event_data)
                
                # Update metrics
                self._update_metrics()
                
                # Check for anomalies
                self._check_anomalies()
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(5)
    
    def _alert_loop(self):
        """Alert processing loop"""
        while self.running:
            try:
                # Check alert rules
                self._check_alert_rules()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Alert loop error: {e}")
                time.sleep(60)
    
    def log_event(self, event_type: str, source_ip: str, user_agent: str,
                 severity: SecurityLevel, description: str, **details):
        """Security event log qilish"""
        event_id = f"evt_{int(time.time())}_{secrets.token_hex(4)}"
        
        event = SecurityEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            event_type=event_type,
            source_ip=source_ip,
            user_agent=user_agent,
            severity=severity,
            description=description,
            details=details
        )
        
        self.events[event_id] = event
        
        # Add to queue for processing
        self.event_queue.put({
            'event_id': event_id,
            'event_type': event_type,
            'severity': severity.value,
            'details': details,
            'timestamp': event.timestamp
        })
        
        # Update statistics
        self.event_stats[event_type] += 1
        self.event_stats[f"severity_{severity.value}"] += 1
        
        logger.warning(f"Security event logged: {event_type} - {description}")
    
    def _process_event(self, event_data: Dict[str, Any]):
        """Event qayta ishlash"""
        # Auto-create incidents for critical events
        if event_data.get('severity') == 'critical':
            self._auto_create_incident(event_data)
        
        # Update metrics
        metric_name = f"{event_data['event_type']}_count"
        current_count = self.metrics_history[metric_name]
        current_count.append(current_count[-1] + 1 if current_count else 1)
    
    def _auto_create_incident(self, event_data: Dict[str, Any]):
        """Avtomatik incident yaratish"""
        # Check if similar incident exists recently
        recent_threshold = datetime.now() - timedelta(hours=1)
        
        for incident in self.incidents.values():
            if (incident.status in [IncidentStatus.OPEN, IncidentStatus.INVESTIGATING] and
                incident.created_at > recent_threshold and
                event_data.get('event_type') in [e.event_type for e in self.events.values() 
                                                if e.event_id in incident.events]):
                # Add event to existing incident
                incident.events.append(event_data['event_id'])
                incident.timeline.append({
                    'timestamp': datetime.now(),
                    'action': 'event_added',
                    'details': event_data
                })
                return
        
        # Create new incident
        incident_id = f"inc_{int(time.time())}_{secrets.token_hex(4)}"
        
        incident = Incident(
            incident_id=incident_id,
            title=f"Critical Security Event: {event_data['event_type']}",
            description=event_data.get('description', 'Critical security event detected'),
            severity=SecurityLevel.CRITICAL,
            status=IncidentStatus.OPEN,
            created_at=datetime.now(),
            events=[event_data['event_id']],
            timeline=[{
                'timestamp': datetime.now(),
                'action': 'incident_created',
                'details': event_data
            }]
        )
        
        self.incidents[incident_id] = incident
        
        logger.critical(f"Critical incident created: {incident_id}")
    
    def create_incident(self, title: str, description: str, severity: SecurityLevel,
                       affected_systems: List[str] = None, assigned_team: List[str] = None) -> str:
        """Incident yaratish"""
        incident_id = f"inc_{int(time.time())}_{secrets.token_hex(4)}"
        
        incident = Incident(
            incident_id=incident_id,
            title=title,
            description=description,
            severity=severity,
            status=IncidentStatus.OPEN,
            created_at=datetime.now(),
            affected_systems=affected_systems or [],
            assigned_team=assigned_team or [],
            timeline=[{
                'timestamp': datetime.now(),
                'action': 'incident_created',
                'details': {'title': title, 'description': description}
            }]
        )
        
        self.incidents[incident_id] = incident
        
        logger.info(f"Incident created: {incident_id} - {title}")
        
        return incident_id
    
    def update_incident_status(self, incident_id: str, status: IncidentStatus, 
                             notes: str = None):
        """Incident status yangilash"""
        if incident_id not in self.incidents:
            return False
        
        incident = self.incidents[incident_id]
        incident.status = status
        
        # Add timeline entry
        timeline_entry = {
            'timestamp': datetime.now(),
            'action': 'status_changed',
            'details': {'new_status': status.value}
        }
        
        if notes:
            timeline_entry['details']['notes'] = notes
        
        incident.timeline.append(timeline_entry)
        
        # If resolved, set resolved time
        if status == IncidentStatus.RESOLVED:
            incident.resolution = notes
        
        logger.info(f"Incident status updated: {incident_id} -> {status.value}")
        
        return True
    
    def add_alert_rule(self, rule: AlertRule):
        """Alert rule qo'shish"""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Alert rule added: {rule.rule_id}")
    
    def remove_alert_rule(self, rule_id: str):
        """Alert rule olib tashlash"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            logger.info(f"Alert rule removed: {rule_id}")
    
    def _check_alert_rules(self):
        """Alert qoidalarini tekshirish"""
        current_time = datetime.now()
        
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
            
            # Check cooldown period
            if (rule.last_triggered and 
                current_time - rule.last_triggered < timedelta(seconds=rule.cooldown_period)):
                continue
            
            # Evaluate rule condition
            if self._evaluate_rule_condition(rule):
                self._trigger_alert(rule)
                rule.last_triggered = current_time
    
    def _evaluate_rule_condition(self, rule: AlertRule) -> bool:
        """Rule shartini baholash"""
        condition = rule.condition
        
        if condition.get('event_type'):
            # Check recent events
            recent_threshold = datetime.now() - timedelta(seconds=condition.get('window', 300))
            recent_events = [
                event for event in self.events.values()
                if event.timestamp > recent_threshold and event.event_type == condition['event_type']
            ]
            
            threshold = condition.get('threshold', 1)
            if len(recent_events) >= threshold:
                return True
        
        return False
    
    def _trigger_alert(self, rule: AlertRule):
        """Alert jo'natish"""
        alert_data = {
            'rule_id': rule.rule_id,
            'rule_name': rule.name,
            'severity': rule.severity.value,
            'timestamp': datetime.now(),
            'channels': rule.notification_channels
        }
        
        # Log alert
        logger.warning(f"Alert triggered: {rule.name} (Severity: {rule.severity.value})")
        
        # Send notifications
        for channel in rule.notification_channels:
            if channel in self.notification_handlers:
                try:
                    self.notification_handlers[channel](alert_data)
                except Exception as e:
                    logger.error(f"Notification failed for {channel}: {e}")
    
    def _update_metrics(self):
        """Metriklarni yangilash"""
        # Update basic metrics
        now = datetime.now()
        
        # Events per minute
        minute_ago = now - timedelta(minutes=1)
        recent_events = [e for e in self.events.values() if e.timestamp > minute_ago]
        self.metrics_history['events_per_minute'].append(len(recent_events))
        
        # Critical events per hour
        hour_ago = now - timedelta(hours=1)
        critical_events = [e for e in self.events.values() 
                          if e.timestamp > hour_ago and e.severity == SecurityLevel.CRITICAL]
        self.metrics_history['critical_events_per_hour'].append(len(critical_events))
        
        # Active incidents
        active_incidents = [i for i in self.incidents.values() 
                           if i.status in [IncidentStatus.OPEN, IncidentStatus.INVESTIGATING]]
        self.metrics_history['active_incidents'].append(len(active_incidents))
    
    def _check_anomalies(self):
        """Anomalylarni tekshirish"""
        for metric_name, values in self.metrics_history.items():
            if values and len(values) > 10:  # Need enough data points
                current_value = values[-1]
                is_anomaly, confidence, message = self.anomaly_detector.detect_anomalies(
                    metric_name, current_value
                )
                
                if is_anomaly:
                    self.log_event(
                        event_type='anomaly_detected',
                        source_ip='127.0.0.1',
                        user_agent='security_monitor',
                        severity=SecurityLevel.MEDIUM,
                        description=f"Anomaly detected in {metric_name}: {message}",
                        metric_name=metric_name,
                        current_value=current_value,
                        confidence=confidence
                    )
    
    def add_notification_handler(self, channel: str, handler: Callable):
        """Notification handler qo'shish"""
        self.notification_handlers[channel] = handler
        logger.info(f"Notification handler added: {channel}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Dashboard ma'lumotlarini olish"""
        now = datetime.now()
        
        # Time ranges
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)
        last_week = now - timedelta(weeks=1)
        
        # Event counts
        events_last_hour = len([e for e in self.events.values() if e.timestamp > last_hour])
        events_last_day = len([e for e in self.events.values() if e.timestamp > last_day])
        events_last_week = len([e for e in self.events.values() if e.timestamp > last_week])
        
        # Severity breakdown
        severity_breakdown = defaultdict(int)
        for event in self.events.values():
            if event.timestamp > last_day:
                severity_breakdown[event.severity.value] += 1
        
        # Active incidents
        active_incidents = [
            incident for incident in self.incidents.values()
            if incident.status in [IncidentStatus.OPEN, IncidentStatus.INVESTIGATING]
        ]
        
        # Recent events
        recent_events = sorted(
            self.events.values(),
            key=lambda x: x.timestamp,
            reverse=True
        )[:10]
        
        return {
            'summary': {
                'total_events': len(self.events),
                'total_incidents': len(self.incidents),
                'active_incidents': len(active_incidents),
                'events_last_hour': events_last_hour,
                'events_last_day': events_last_day,
                'events_last_week': events_last_week
            },
            'severity_breakdown': dict(severity_breakdown),
            'recent_events': [
                {
                    'id': event.event_id,
                    'type': event.event_type,
                    'severity': event.severity.value,
                    'timestamp': event.timestamp.isoformat(),
                    'description': event.description
                }
                for event in recent_events
            ],
            'active_incidents': [
                {
                    'id': incident.incident_id,
                    'title': incident.title,
                    'severity': incident.severity.value,
                    'status': incident.status.value,
                    'created_at': incident.created_at.isoformat(),
                    'events_count': len(incident.events)
                }
                for incident in active_incidents
            ],
            'metrics': {
                metric_name: list(values)[-60:]  # Last 60 data points
                for metric_name, values in self.metrics_history.items()
            }
        }


class IncidentResponse:
    """Incident Response Manager"""
    
    def __init__(self, security_monitor: SecurityMonitor):
        self.security_monitor = security_monitor
        self.response_playbooks: Dict[str, Dict[str, Any]] = {}
        self.response_team_contacts: Dict[str, Dict[str, str]] = {}
        
        # Setup default playbooks
        self._setup_default_playbooks()
    
    def _setup_default_playbooks(self):
        """Default response playbooklari"""
        self.response_playbooks = {
            'sql_injection': {
                'name': 'SQL Injection Response',
                'severity': SecurityLevel.CRITICAL,
                'steps': [
                    '1. Immediately block the source IP address',
                    '2. Audit database for unauthorized changes',
                    '3. Review application logs for extent of breach',
                    '4. Apply emergency patches if available',
                    '5. Notify security team and legal department'
                ],
                'escalation_time': 15,  # minutes
                'auto_actions': ['block_ip', 'alert_team']
            },
            'data_breach': {
                'name': 'Data Breach Response',
                'severity': SecurityLevel.EMERGENCY,
                'steps': [
                    '1. Isolate affected systems immediately',
                    '2. Preserve evidence and logs',
                    '3. Assess scope of data accessed',
                    '4. Notify relevant stakeholders',
                    '5. Begin regulatory compliance procedures',
                    '6. Prepare incident report'
                ],
                'escalation_time': 5,
                'auto_actions': ['isolate_system', 'preserve_evidence', 'notify_executives']
            },
            'unauthorized_access': {
                'name': 'Unauthorized Access Response',
                'severity': SecurityLevel.HIGH,
                'steps': [
                    '1. Revoke access credentials immediately',
                    '2. Audit user activities and access patterns',
                    '3. Review security controls effectiveness',
                    '4. Implement additional monitoring',
                    '5. Update access policies if necessary'
                ],
                'escalation_time': 30,
                'auto_actions': ['revoke_access', 'increase_monitoring']
            }
        }
    
    def trigger_incident_response(self, incident_id: str, playbook_key: str) -> bool:
        """Incident response boshlash"""
        if playbook_key not in self.response_playbooks:
            logger.error(f"Playbook not found: {playbook_key}")
            return False
        
        playbook = self.response_playbooks[playbook_key]
        
        # Update incident with playbook
        incident = self.security_monitor.incidents.get(incident_id)
        if not incident:
            return False
        
        incident.timeline.append({
            'timestamp': datetime.now(),
            'action': 'response_initiated',
            'details': {
                'playbook': playbook_key,
                'playbook_name': playbook['name']
            }
        })
        
        # Execute auto actions
        for action in playbook.get('auto_actions', []):
            self._execute_auto_action(incident_id, action)
        
        # Schedule escalation
        escalation_time = datetime.now() + timedelta(minutes=playbook['escalation_time'])
        self._schedule_escalation(incident_id, escalation_time)
        
        logger.info(f"Incident response initiated: {incident_id} using playbook: {playbook_key}")
        
        return True
    
    def _execute_auto_action(self, incident_id: str, action: str):
        """Auto action bajarish"""
        try:
            if action == 'block_ip':
                # Implementation would block IP address
                logger.info(f"Auto action executed: block_ip for incident {incident_id}")
            
            elif action == 'alert_team':
                # Implementation would alert response team
                logger.info(f"Auto action executed: alert_team for incident {incident_id}")
            
            elif action == 'isolate_system':
                # Implementation would isolate affected systems
                logger.info(f"Auto action executed: isolate_system for incident {incident_id}")
            
            elif action == 'preserve_evidence':
                # Implementation would preserve logs and evidence
                logger.info(f"Auto action executed: preserve_evidence for incident {incident_id}")
            
            elif action == 'revoke_access':
                # Implementation would revoke user access
                logger.info(f"Auto action executed: revoke_access for incident {incident_id}")
            
            elif action == 'increase_monitoring':
                # Implementation would increase monitoring
                logger.info(f"Auto action executed: increase_monitoring for incident {incident_id}")
            
        except Exception as e:
            logger.error(f"Auto action failed ({action}): {e}")
    
    def _schedule_escalation(self, incident_id: str, escalation_time: datetime):
        """Escalation rejalashtirish"""
        # In real implementation, this would use a scheduler like Celery
        logger.info(f"Escalation scheduled for incident {incident_id} at {escalation_time}")
    
    def get_response_metrics(self) -> Dict[str, Any]:
        """Response metriklari"""
        resolved_incidents = [
            incident for incident in self.security_monitor.incidents.values()
            if incident.status == IncidentStatus.RESOLVED
        ]
        
        if not resolved_incidents:
            return {
                'total_incidents': 0,
                'avg_resolution_time': 0,
                'resolution_time_breakdown': {},
                'playbook_effectiveness': {}
            }
        
        # Calculate resolution times
        resolution_times = []
        for incident in resolved_incidents:
            resolution_time = incident.created_at
            for entry in incident.timeline:
                if entry['action'] == 'status_changed' and entry['details'].get('new_status') == 'resolved':
                    resolution_time = entry['timestamp']
                    break
            
            time_diff = resolution_time - incident.created_at
            resolution_times.append(time_diff.total_seconds() / 60)  # minutes
        
        avg_resolution_time = sum(resolution_times) / len(resolution_times)
        
        return {
            'total_incidents': len(resolved_incidents),
            'avg_resolution_time': round(avg_resolution_time, 2),
            'resolution_time_breakdown': {
                'min': round(min(resolution_times), 2),
                'max': round(max(resolution_times), 2),
                'median': round(sorted(resolution_times)[len(resolution_times)//2], 2)
            },
            'playbook_effectiveness': {
                # Would calculate effectiveness metrics per playbook
                'sql_injection': {'avg_time': 45, 'success_rate': 0.95},
                'data_breach': {'avg_time': 120, 'success_rate': 0.88},
                'unauthorized_access': {'avg_time': 30, 'success_rate': 0.92}
            }
        }