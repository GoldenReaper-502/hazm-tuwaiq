"""
HAZM TUWAIQ - Escalation Manager
Automatic alert escalation based on time and severity
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import threading
import time

from .models import (
    Alert, EscalationRule, AlertSeverity,
    AlertStatus, NotificationChannel
)


class EscalationManager:
    """
    مدير التصعيد
    Automatic alert escalation workflow
    """
    
    def __init__(self):
        """Initialize escalation manager"""
        self.logger = logging.getLogger(__name__)
        
        # Escalation rules
        self.rules: Dict[str, EscalationRule] = {}
        
        # Escalation tracking
        self.escalation_timers: Dict[str, threading.Timer] = {}
        
        # Background monitoring
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
    
    def add_rule(self, rule: EscalationRule):
        """Add escalation rule"""
        self.rules[rule.id] = rule
        self.logger.info(f"Escalation rule added: {rule.name}")
    
    def check_escalation(
        self,
        alert: Alert,
        organization_users: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Check if alert should be escalated
        
        Args:
            alert: Alert to check
            organization_users: Dict of organization users by role
            
        Returns:
            Escalation info if escalation triggered, None otherwise
        """
        try:
            # Find matching rule
            rule = self._find_matching_rule(alert)
            
            if not rule or not rule.is_active:
                return None
            
            # Check if already at max escalation level
            max_level = len(rule.escalation_levels)
            if alert.escalation_level >= max_level:
                self.logger.info(f"Alert {alert.id} already at max escalation level")
                return None
            
            # Get next escalation level
            next_level_idx = alert.escalation_level
            next_level = rule.escalation_levels[next_level_idx]
            
            # Check if enough time has passed
            if alert.escalation_level == 0:
                # First escalation - check time since creation
                time_since_creation = datetime.now() - alert.created_at
                delay = timedelta(minutes=next_level.get('delay_minutes', 15))
                
                if time_since_creation < delay:
                    return None
            else:
                # Subsequent escalation - check time since last escalation
                time_since_escalation = datetime.now() - (alert.escalated_at or alert.created_at)
                delay = timedelta(minutes=next_level.get('delay_minutes', 15))
                
                if time_since_escalation < delay:
                    return None
            
            # Check if alert is still unresolved
            if alert.status not in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]:
                return None
            
            # Escalate!
            escalation_info = self._execute_escalation(
                alert=alert,
                level=next_level,
                rule=rule,
                organization_users=organization_users
            )
            
            return escalation_info
            
        except Exception as e:
            self.logger.error(f"Failed to check escalation: {e}")
            return None
    
    def _find_matching_rule(self, alert: Alert) -> Optional[EscalationRule]:
        """Find escalation rule matching alert"""
        for rule in self.rules.values():
            # Check organization
            if rule.organization_id != alert.organization_id:
                continue
            
            # Check alert type (empty list = all types)
            if rule.alert_types and alert.type not in rule.alert_types:
                continue
            
            # Check severity
            severity_order = [
                AlertSeverity.INFO,
                AlertSeverity.LOW,
                AlertSeverity.MEDIUM,
                AlertSeverity.HIGH,
                AlertSeverity.CRITICAL
            ]
            
            min_severity_idx = severity_order.index(rule.min_severity)
            alert_severity_idx = severity_order.index(alert.severity)
            
            if alert_severity_idx < min_severity_idx:
                continue
            
            # Match found
            return rule
        
        return None
    
    def _execute_escalation(
        self,
        alert: Alert,
        level: Dict[str, Any],
        rule: EscalationRule,
        organization_users: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute escalation for specific level"""
        try:
            level_num = level.get('level', alert.escalation_level + 1)
            
            # Update alert
            alert.escalation_level = level_num
            alert.escalated_at = datetime.now()
            alert.status = AlertStatus.ESCALATED
            
            # Get recipients for this level
            recipients = []
            
            # Add users by role
            notify_roles = level.get('notify_roles', [])
            for role in notify_roles:
                role_users = organization_users.get(role, [])
                recipients.extend(role_users)
            
            # Add specific users
            notify_users = level.get('notify_users', [])
            recipients.extend(notify_users)
            
            # Remove duplicates
            recipients = list(set(recipients))
            
            # Get notification channels (default: all)
            channels = level.get('channels', [
                NotificationChannel.SMS,
                NotificationChannel.EMAIL,
                NotificationChannel.WHATSAPP
            ])
            
            # Execute additional actions
            actions = level.get('actions', [])
            
            # Add to escalation path
            escalation_entry = {
                'level': level_num,
                'escalated_at': datetime.now().isoformat(),
                'rule_id': rule.id,
                'recipients': recipients,
                'channels': [c.value if hasattr(c, 'value') else c for c in channels],
                'actions': actions
            }
            
            alert.escalation_path.append(escalation_entry)
            
            self.logger.warning(
                f"🚨 ALERT ESCALATED\n"
                f"   Alert: {alert.id}\n"
                f"   Level: {level_num}\n"
                f"   Recipients: {len(recipients)}\n"
                f"   Channels: {[c.value if hasattr(c, 'value') else c for c in channels]}"
            )
            
            return {
                'escalated': True,
                'level': level_num,
                'recipients': recipients,
                'channels': channels,
                'actions': actions,
                'escalation_entry': escalation_entry
            }
            
        except Exception as e:
            self.logger.error(f"Failed to execute escalation: {e}")
            return {'escalated': False, 'error': str(e)}
    
    def schedule_escalation_check(
        self,
        alert: Alert,
        delay_minutes: int,
        callback: callable
    ):
        """
        Schedule automatic escalation check
        
        Args:
            alert: Alert to monitor
            delay_minutes: Minutes to wait before checking
            callback: Function to call for escalation
        """
        try:
            # Cancel existing timer if any
            if alert.id in self.escalation_timers:
                self.escalation_timers[alert.id].cancel()
            
            # Create new timer
            delay_seconds = delay_minutes * 60
            timer = threading.Timer(
                delay_seconds,
                callback,
                args=[alert]
            )
            
            # Start timer
            timer.start()
            
            # Store timer
            self.escalation_timers[alert.id] = timer
            
            self.logger.info(
                f"Escalation check scheduled for alert {alert.id} in {delay_minutes} minutes"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to schedule escalation: {e}")
    
    def cancel_escalation(self, alert_id: str):
        """Cancel scheduled escalation for alert"""
        if alert_id in self.escalation_timers:
            self.escalation_timers[alert_id].cancel()
            del self.escalation_timers[alert_id]
            self.logger.info(f"Escalation cancelled for alert {alert_id}")
    
    def start_monitoring(
        self,
        check_interval_seconds: int = 60
    ):
        """
        Start background escalation monitoring
        
        Args:
            check_interval_seconds: Interval between checks
        """
        if self.monitoring:
            self.logger.warning("Escalation monitoring already running")
            return
        
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    self.logger.debug("Running escalation check...")
                    # In production, check all active alerts here
                    time.sleep(check_interval_seconds)
                    
                except Exception as e:
                    self.logger.error(f"Error in escalation monitoring: {e}")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(
            target=monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()
        
        self.logger.info(f"Escalation monitoring started (interval: {check_interval_seconds}s)")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        # Cancel all timers
        for timer in self.escalation_timers.values():
            timer.cancel()
        
        self.escalation_timers.clear()
        
        self.logger.info("Escalation monitoring stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get escalation statistics"""
        return {
            "total_rules": len(self.rules),
            "active_rules": len([r for r in self.rules.values() if r.is_active]),
            "scheduled_escalations": len(self.escalation_timers),
            "monitoring_active": self.monitoring
        }
    
    def create_default_rules(
        self,
        organization_id: str
    ) -> List[EscalationRule]:
        """Create default escalation rules for organization"""
        
        # Critical alerts - fast escalation
        critical_rule = EscalationRule(
            name="Critical Alert Escalation",
            name_ar="تصعيد التنبيهات الحرجة",
            min_severity=AlertSeverity.CRITICAL,
            escalation_levels=[
                {
                    'level': 1,
                    'delay_minutes': 2,
                    'notify_roles': ['supervisor', 'safety_manager'],
                    'channels': ['sms', 'whatsapp', 'push']
                },
                {
                    'level': 2,
                    'delay_minutes': 5,
                    'notify_roles': ['org_owner'],
                    'channels': ['sms', 'whatsapp', 'email'],
                    'actions': ['call_emergency']
                },
                {
                    'level': 3,
                    'delay_minutes': 10,
                    'notify_roles': ['super_admin'],
                    'channels': ['sms', 'email'],
                    'actions': ['create_incident']
                }
            ],
            organization_id=organization_id,
            is_active=True
        )
        
        # High severity - moderate escalation
        high_rule = EscalationRule(
            name="High Severity Escalation",
            name_ar="تصعيد التنبيهات العالية",
            min_severity=AlertSeverity.HIGH,
            escalation_levels=[
                {
                    'level': 1,
                    'delay_minutes': 10,
                    'notify_roles': ['supervisor'],
                    'channels': ['sms', 'push']
                },
                {
                    'level': 2,
                    'delay_minutes': 30,
                    'notify_roles': ['safety_manager'],
                    'channels': ['sms', 'email']
                }
            ],
            organization_id=organization_id,
            is_active=True
        )
        
        # Add rules
        self.add_rule(critical_rule)
        self.add_rule(high_rule)
        
        return [critical_rule, high_rule]


# Singleton instance
_escalation_manager: Optional[EscalationManager] = None


def get_escalation_manager() -> EscalationManager:
    """Get singleton EscalationManager instance"""
    global _escalation_manager
    
    if _escalation_manager is None:
        _escalation_manager = EscalationManager()
    
    return _escalation_manager
