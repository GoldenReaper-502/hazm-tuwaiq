"""
HAZM TUWAIQ - Alert Engine
Real-time alert generation and autonomous action execution
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from .models import (
    Alert, AlertRule, AlertAction, AlertSeverity,
    AlertStatus, AlertType, ActionType
)


class AlertEngine:
    """
    محرك التنبيهات
    Generate and manage real-time safety alerts
    """
    
    def __init__(self):
        """Initialize alert engine"""
        self.logger = logging.getLogger(__name__)
        
        # Alert counters per organization
        self.alert_counts = defaultdict(int)
        
        # Active alerts cache
        self.active_alerts: Dict[str, Alert] = {}
        
        # Alert rules cache
        self.alert_rules: Dict[str, AlertRule] = {}
    
    def create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        description: str,
        organization_id: str,
        source: str = "SYSTEM",
        **kwargs
    ) -> Alert:
        """
        Create new alert
        
        Args:
            alert_type: Type of alert
            severity: Severity level
            title: Alert title
            description: Alert description
            organization_id: Organization ID
            source: Alert source
            **kwargs: Additional alert fields
            
        Returns:
            Created alert
        """
        try:
            # Create alert
            alert = Alert(
                type=alert_type,
                severity=severity,
                title=title,
                description=description,
                organization_id=organization_id,
                source=source,
                **kwargs
            )
            
            # Cache alert
            self.active_alerts[alert.id] = alert
            
            # Increment counter
            self.alert_counts[organization_id] += 1
            
            self.logger.info(
                f"Alert created: {alert.id} - {alert.type.value} - {alert.severity.value}"
            )
            
            return alert
            
        except Exception as e:
            self.logger.error(f"Failed to create alert: {e}")
            raise
    
    def evaluate_detection(
        self,
        detection_result: Dict[str, Any],
        rules: List[AlertRule]
    ) -> List[Alert]:
        """
        Evaluate detection result against alert rules
        
        Args:
            detection_result: AI detection result
            rules: Active alert rules
            
        Returns:
            List of generated alerts
        """
        alerts = []
        
        try:
            # Extract detection info
            ppe_compliance = detection_result.get('ppe_compliance', {})
            pose_analysis = detection_result.get('pose_analysis', {})
            fatigue_status = detection_result.get('fatigue_status', {})
            intent_prediction = detection_result.get('intent_prediction', {})
            safety_assessment = detection_result.get('safety_assessment', {})
            
            # Check PPE violations
            if not ppe_compliance.get('compliant', True):
                for violation in ppe_compliance.get('violations', []):
                    # Find matching rules
                    for rule in rules:
                        if (rule.trigger_type == AlertType.PPE_VIOLATION and
                            rule.is_active and
                            violation.get('confidence', 0) >= rule.conditions.get('confidence_threshold', 0.8)):
                            
                            alert = self.create_alert(
                                alert_type=AlertType.PPE_VIOLATION,
                                severity=rule.severity,
                                title=f"PPE Violation: {violation['type']}",
                                title_ar=f"خرق معدات السلامة: {violation['type']}",
                                description=f"Worker detected without required PPE. Confidence: {violation['confidence']:.2f}",
                                organization_id=rule.organization_id,
                                source="AI_DETECTION",
                                source_id=detection_result.get('detection_id'),
                                camera_id=detection_result.get('camera_id'),
                                confidence=violation['confidence'],
                                metadata=violation
                            )
                            alerts.append(alert)
                            break
            
            # Check fall detection
            if pose_analysis:
                pose_risks = pose_analysis.get('posture_risks', [])
                for risk in pose_risks:
                    if risk['type'] == 'FALL_DETECTED':
                        alert = self.create_alert(
                            alert_type=AlertType.FALL_DETECTED,
                            severity=AlertSeverity.CRITICAL,
                            title="Worker Fall Detected",
                            title_ar="سقوط عامل مُكتشف",
                            description=f"Fall detected with {risk['severity']} severity",
                            organization_id=detection_result.get('organization_id', 'ORG-DEFAULT'),
                            source="AI_DETECTION",
                            camera_id=detection_result.get('camera_id'),
                            confidence=risk.get('confidence', 0.9),
                            metadata=risk
                        )
                        alerts.append(alert)
            
            # Check fatigue
            if fatigue_status.get('fatigue_detected', False):
                if fatigue_status.get('level_category') in ['HIGH', 'CRITICAL']:
                    alert = self.create_alert(
                        alert_type=AlertType.WORKER_FATIGUE,
                        severity=AlertSeverity.HIGH if fatigue_status['level_category'] == 'HIGH' else AlertSeverity.CRITICAL,
                        title="Worker Fatigue Detected",
                        title_ar="إرهاق عامل مُكتشف",
                        description=fatigue_status.get('message', ''),
                        organization_id=detection_result.get('organization_id', 'ORG-DEFAULT'),
                        source="AI_DETECTION",
                        camera_id=detection_result.get('camera_id'),
                        confidence=fatigue_status.get('fatigue_level', 0) / 100,
                        metadata=fatigue_status
                    )
                    alerts.append(alert)
            
            # Check collision risks
            if intent_prediction:
                collision_risks = intent_prediction.get('collision_risks', [])
                for collision in collision_risks:
                    if collision.get('time_to_collision', 999) < 3:  # Less than 3 seconds
                        alert = self.create_alert(
                            alert_type=AlertType.COLLISION_RISK,
                            severity=AlertSeverity.CRITICAL if collision['time_to_collision'] < 1 else AlertSeverity.HIGH,
                            title=f"Collision Risk: {collision['zone']}",
                            title_ar=f"خطر اصطدام: {collision['zone']}",
                            description=f"Worker approaching danger zone. Time to collision: {collision['time_to_collision']:.1f}s",
                            organization_id=detection_result.get('organization_id', 'ORG-DEFAULT'),
                            source="AI_DETECTION",
                            camera_id=detection_result.get('camera_id'),
                            confidence=0.95,
                            metadata=collision
                        )
                        alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate detection: {e}")
            return alerts
    
    def execute_autonomous_actions(
        self,
        alert: Alert,
        rule: AlertRule
    ) -> List[AlertAction]:
        """
        Execute autonomous actions for alert
        
        Args:
            alert: Alert object
            rule: Alert rule with actions
            
        Returns:
            List of executed actions
        """
        actions = []
        
        try:
            for action_type in rule.actions:
                action = AlertAction(
                    alert_id=alert.id,
                    action_type=action_type,
                    status="executing"
                )
                
                # Execute action
                success, result = self._execute_action(action_type, alert, rule)
                
                # Update action
                action.executed_at = datetime.now()
                action.success = success
                action.status = "completed" if success else "failed"
                action.result = result
                action.completed_at = datetime.now()
                
                actions.append(action)
                
                # Add to alert
                alert.autonomous_actions.append(action.id)
                
                self.logger.info(
                    f"Action executed: {action.action_type.value} - {'✅' if success else '❌'}"
                )
            
            return actions
            
        except Exception as e:
            self.logger.error(f"Failed to execute autonomous actions: {e}")
            return actions
    
    def _execute_action(
        self,
        action_type: ActionType,
        alert: Alert,
        rule: AlertRule
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute single action
        
        Args:
            action_type: Type of action
            alert: Alert object
            rule: Alert rule
            
        Returns:
            Tuple of (success, result)
        """
        try:
            if action_type == ActionType.SOUND_ALARM:
                # Simulate sounding alarm
                return True, {
                    "alarm_id": f"ALARM-{alert.id}",
                    "duration": 10,
                    "location": alert.zone or "Site-wide"
                }
            
            elif action_type == ActionType.ACTIVATE_LIGHT:
                # Simulate activating warning light
                return True, {
                    "light_id": f"LIGHT-{alert.camera_id}",
                    "color": "red" if alert.severity == AlertSeverity.CRITICAL else "yellow"
                }
            
            elif action_type == ActionType.STOP_EQUIPMENT:
                # Simulate stopping equipment
                return True, {
                    "equipment_stopped": True,
                    "zone": alert.zone,
                    "stopped_at": datetime.now().isoformat()
                }
            
            elif action_type == ActionType.LOCK_ZONE:
                # Simulate locking zone
                return True, {
                    "zone_locked": True,
                    "zone": alert.zone,
                    "locked_at": datetime.now().isoformat()
                }
            
            elif action_type == ActionType.CREATE_INCIDENT:
                # Simulate creating incident report
                return True, {
                    "incident_created": True,
                    "incident_id": f"INC-{alert.id}",
                    "severity": alert.severity.value
                }
            
            else:
                # Notification actions are handled by NotificationManager
                return True, {"queued": True}
                
        except Exception as e:
            self.logger.error(f"Action execution failed: {e}")
            return False, {"error": str(e)}
    
    def acknowledge_alert(
        self,
        alert_id: str,
        user_id: str,
        notes: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Acknowledge alert
        
        Args:
            alert_id: Alert ID
            user_id: User ID who acknowledged
            notes: Optional notes
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            alert = self.active_alerts.get(alert_id)
            
            if not alert:
                return False, "Alert not found"
            
            if alert.status == AlertStatus.ACKNOWLEDGED:
                return False, "Alert already acknowledged"
            
            # Update alert
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = user_id
            alert.acknowledged_at = datetime.now()
            alert.updated_at = datetime.now()
            
            if notes:
                if 'acknowledgment_notes' not in alert.metadata:
                    alert.metadata['acknowledgment_notes'] = []
                alert.metadata['acknowledgment_notes'].append({
                    'user_id': user_id,
                    'notes': notes,
                    'timestamp': datetime.now().isoformat()
                })
            
            self.logger.info(f"Alert acknowledged: {alert_id} by {user_id}")
            
            return True, None
            
        except Exception as e:
            self.logger.error(f"Failed to acknowledge alert: {e}")
            return False, str(e)
    
    def resolve_alert(
        self,
        alert_id: str,
        user_id: str,
        resolution_notes: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Resolve alert
        
        Args:
            alert_id: Alert ID
            user_id: User ID who resolved
            resolution_notes: Resolution notes
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            alert = self.active_alerts.get(alert_id)
            
            if not alert:
                return False, "Alert not found"
            
            if alert.status == AlertStatus.RESOLVED:
                return False, "Alert already resolved"
            
            # Update alert
            alert.status = AlertStatus.RESOLVED
            alert.resolved_by = user_id
            alert.resolved_at = datetime.now()
            alert.updated_at = datetime.now()
            
            alert.metadata['resolution'] = {
                'user_id': user_id,
                'notes': resolution_notes,
                'resolved_at': datetime.now().isoformat()
            }
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            
            self.logger.info(f"Alert resolved: {alert_id} by {user_id}")
            
            return True, None
            
        except Exception as e:
            self.logger.error(f"Failed to resolve alert: {e}")
            return False, str(e)
    
    def get_active_alerts(
        self,
        organization_id: str,
        severity: Optional[AlertSeverity] = None,
        alert_type: Optional[AlertType] = None
    ) -> List[Alert]:
        """Get active alerts with filters"""
        alerts = [
            alert for alert in self.active_alerts.values()
            if alert.organization_id == organization_id and
               alert.status in [AlertStatus.ACTIVE, AlertStatus.PENDING, AlertStatus.ACKNOWLEDGED]
        ]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if alert_type:
            alerts = [a for a in alerts if a.type == alert_type]
        
        return alerts
    
    def get_stats(self, organization_id: str) -> Dict[str, Any]:
        """Get alert statistics for organization"""
        active_alerts = self.get_active_alerts(organization_id)
        
        stats = {
            "total_alerts": self.alert_counts[organization_id],
            "active_alerts": len(active_alerts),
            "by_severity": {
                "critical": len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
                "high": len([a for a in active_alerts if a.severity == AlertSeverity.HIGH]),
                "medium": len([a for a in active_alerts if a.severity == AlertSeverity.MEDIUM]),
                "low": len([a for a in active_alerts if a.severity == AlertSeverity.LOW])
            },
            "by_status": {
                "pending": len([a for a in active_alerts if a.status == AlertStatus.PENDING]),
                "active": len([a for a in active_alerts if a.status == AlertStatus.ACTIVE]),
                "acknowledged": len([a for a in active_alerts if a.status == AlertStatus.ACKNOWLEDGED])
            }
        }
        
        return stats


# Singleton instance
_alert_engine: Optional[AlertEngine] = None


def get_alert_engine() -> AlertEngine:
    """Get singleton AlertEngine instance"""
    global _alert_engine
    
    if _alert_engine is None:
        _alert_engine = AlertEngine()
    
    return _alert_engine
