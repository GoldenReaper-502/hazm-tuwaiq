"""
HAZM TUWAIQ - Alert API
Alert management, acknowledgment, and escalation endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from .models import (
    Alert, AlertRule, AlertCreate, AlertAcknowledge,
    AlertResolve, AlertEscalate, AlertSeverity,
    AlertStatus, AlertType, NotificationChannel
)
from .engine import get_alert_engine
from .notifications import get_notification_manager
from .escalation import get_escalation_manager


# ═══════════════════════════════════════════════════════════
# ROUTER SETUP
# ═══════════════════════════════════════════════════════════

router = APIRouter()

# Initialize managers
alert_engine = get_alert_engine()
notification_manager = get_notification_manager()
escalation_manager = get_escalation_manager()


# In-memory databases
ALERTS_DB: Dict[str, Alert] = {}
ALERT_RULES_DB: Dict[str, AlertRule] = {}


# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════

def create_response(
    success: bool,
    message: str,
    data: Any = None,
    error: Optional[str] = None
) -> Dict[str, Any]:
    """Create unified JSON response"""
    response = {
        "success": success,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    
    if error:
        response["error"] = error
    
    return response


# ═══════════════════════════════════════════════════════════
# ALERT ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.post("/alerts", summary="إنشاء تنبيه - Create Alert")
async def create_alert(
    alert_create: AlertCreate,
    organization_id: str = Query(..., description="Organization ID")
):
    """
    Create new safety alert
    
    - **Automatic**: Called by AI detection system
    - **Manual**: Can be created manually by users
    - **Notifications**: Automatically sent based on rules
    """
    try:
        # Create alert
        alert = alert_engine.create_alert(
            alert_type=alert_create.type,
            severity=alert_create.severity,
            title=alert_create.title,
            title_ar=alert_create.title_ar,
            description=alert_create.description,
            description_ar=alert_create.description_ar,
            organization_id=organization_id,
            source=alert_create.source,
            camera_id=alert_create.camera_id,
            site_id=alert_create.site_id,
            confidence=alert_create.confidence,
            metadata=alert_create.metadata
        )
        
        # Store in DB
        ALERTS_DB[alert.id] = alert
        
        # Find matching alert rules
        matching_rules = [
            rule for rule in ALERT_RULES_DB.values()
            if (rule.organization_id == organization_id and
                rule.is_active and
                rule.trigger_type == alert.type)
        ]
        
        # Execute autonomous actions
        if matching_rules:
            rule = matching_rules[0]  # Use first matching rule
            
            actions = alert_engine.execute_autonomous_actions(alert, rule)
            
            # Send notifications
            # In production, get actual users from governance module
            mock_recipients = [
                {
                    'id': 'USER-001',
                    'sms_contact': '+966501234567',
                    'email_contact': 'supervisor@example.com',
                    'whatsapp_contact': '+966501234567'
                }
            ]
            
            notifications = notification_manager.send_alert_notification(
                alert=alert,
                recipients=mock_recipients,
                channels=rule.notify_channels
            )
            
            # Schedule escalation if enabled
            if rule.enable_escalation:
                escalation_manager.schedule_escalation_check(
                    alert=alert,
                    delay_minutes=rule.escalation_delay_minutes,
                    callback=lambda a: escalation_manager.check_escalation(a, {})
                )
        
        return create_response(
            success=True,
            message="Alert created successfully",
            data={
                "alert": alert.dict(),
                "actions_executed": len(alert.autonomous_actions),
                "notifications_sent": len(alert.notifications_sent)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", summary="قائمة التنبيهات - List Alerts")
async def list_alerts(
    organization_id: str = Query(..., description="Organization ID"),
    status: Optional[AlertStatus] = None,
    severity: Optional[AlertSeverity] = None,
    alert_type: Optional[AlertType] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Get all alerts with optional filters
    
    - **status**: Filter by alert status
    - **severity**: Filter by severity level
    - **alert_type**: Filter by alert type
    """
    try:
        # Filter alerts
        alerts = [
            alert for alert in ALERTS_DB.values()
            if alert.organization_id == organization_id
        ]
        
        if status:
            alerts = [a for a in alerts if a.status == status]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if alert_type:
            alerts = [a for a in alerts if a.type == alert_type]
        
        # Sort by creation date (newest first)
        alerts = sorted(alerts, key=lambda x: x.created_at, reverse=True)
        
        # Limit results
        alerts = alerts[:limit]
        
        return create_response(
            success=True,
            message=f"Retrieved {len(alerts)} alerts",
            data={
                "alerts": [a.dict() for a in alerts],
                "total": len(alerts)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/{alert_id}", summary="تفاصيل التنبيه - Get Alert")
async def get_alert(alert_id: str):
    """Get alert details by ID"""
    try:
        alert = ALERTS_DB.get(alert_id)
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return create_response(
            success=True,
            message="Alert retrieved successfully",
            data={"alert": alert.dict()}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/acknowledge", summary="تأكيد استلام التنبيه - Acknowledge Alert")
async def acknowledge_alert(
    alert_id: str,
    user_id: str = Query(..., description="User ID"),
    notes: Optional[str] = None
):
    """
    Acknowledge alert (confirm receipt)
    
    - **Stops escalation**: Prevents automatic escalation
    - **Assigns responsibility**: Links alert to user
    - **Tracks response time**: Records acknowledgment time
    """
    try:
        success, error = alert_engine.acknowledge_alert(
            alert_id=alert_id,
            user_id=user_id,
            notes=notes
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=error)
        
        # Cancel escalation
        escalation_manager.cancel_escalation(alert_id)
        
        alert = ALERTS_DB.get(alert_id)
        
        return create_response(
            success=True,
            message="Alert acknowledged successfully",
            data={"alert": alert.dict() if alert else None}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/resolve", summary="حل التنبيه - Resolve Alert")
async def resolve_alert(
    alert_id: str,
    user_id: str = Query(..., description="User ID"),
    resolution_notes: str = Query(..., description="Resolution notes")
):
    """
    Resolve alert (mark as solved)
    
    - **Closes alert**: Marks alert as resolved
    - **Documents solution**: Records resolution notes
    - **Stops all actions**: Cancels escalation and notifications
    """
    try:
        success, error = alert_engine.resolve_alert(
            alert_id=alert_id,
            user_id=user_id,
            resolution_notes=resolution_notes
        )
        
        if not success:
            raise HTTPException(status_code=400, detail=error)
        
        # Cancel escalation
        escalation_manager.cancel_escalation(alert_id)
        
        return create_response(
            success=True,
            message="Alert resolved successfully",
            data={"alert_id": alert_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/escalate", summary="تصعيد التنبيه - Escalate Alert")
async def escalate_alert(
    alert_id: str,
    escalate_to: str = Query(..., description="User ID or Role to escalate to"),
    reason: str = Query(..., description="Escalation reason")
):
    """
    Manually escalate alert to higher authority
    
    - **Override automatic**: Can manually escalate before timer
    - **Custom recipient**: Escalate to specific user/role
    - **Documents reason**: Records why escalation was needed
    """
    try:
        alert = ALERTS_DB.get(alert_id)
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Update alert
        alert.escalation_level += 1
        alert.escalated_at = datetime.now()
        alert.status = AlertStatus.ESCALATED
        
        alert.escalation_path.append({
            'level': alert.escalation_level,
            'escalated_at': datetime.now().isoformat(),
            'escalate_to': escalate_to,
            'reason': reason,
            'type': 'manual'
        })
        
        return create_response(
            success=True,
            message="Alert escalated successfully",
            data={"alert": alert.dict()}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# ALERT RULES ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.post("/alert-rules", summary="إنشاء قاعدة تنبيه - Create Alert Rule")
async def create_alert_rule(
    rule: AlertRule,
    organization_id: str = Query(..., description="Organization ID")
):
    """
    Create alert rule
    
    - **Automation**: Define automatic responses to detections
    - **Notifications**: Configure who gets notified
    - **Actions**: Set autonomous actions to execute
    """
    try:
        rule.organization_id = organization_id
        
        # Store rule
        ALERT_RULES_DB[rule.id] = rule
        
        return create_response(
            success=True,
            message="Alert rule created successfully",
            data={"rule": rule.dict()}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alert-rules", summary="قائمة قواعد التنبيهات - List Alert Rules")
async def list_alert_rules(
    organization_id: str = Query(..., description="Organization ID")
):
    """Get all alert rules for organization"""
    try:
        rules = [
            rule for rule in ALERT_RULES_DB.values()
            if rule.organization_id == organization_id
        ]
        
        return create_response(
            success=True,
            message=f"Retrieved {len(rules)} rules",
            data={"rules": [r.dict() for r in rules]}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/alert-rules/{rule_id}", summary="حذف قاعدة - Delete Alert Rule")
async def delete_alert_rule(rule_id: str):
    """Delete alert rule"""
    try:
        if rule_id not in ALERT_RULES_DB:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        del ALERT_RULES_DB[rule_id]
        
        return create_response(
            success=True,
            message="Alert rule deleted successfully",
            data={"rule_id": rule_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# STATISTICS ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/alerts/stats/overview", summary="إحصائيات التنبيهات - Alert Statistics")
async def get_alert_stats(
    organization_id: str = Query(..., description="Organization ID")
):
    """
    Get comprehensive alert statistics
    
    - **Alert counts**: Total, active, resolved
    - **By severity**: Distribution across severity levels
    - **By type**: Most common alert types
    - **Response times**: Average acknowledgment and resolution times
    """
    try:
        # Get engine stats
        engine_stats = alert_engine.get_stats(organization_id)
        
        # Get notification stats
        notif_stats = notification_manager.get_notification_stats()
        
        # Get escalation stats
        escalation_stats = escalation_manager.get_stats()
        
        # Calculate additional metrics
        org_alerts = [
            a for a in ALERTS_DB.values()
            if a.organization_id == organization_id
        ]
        
        # Response times
        acknowledged = [a for a in org_alerts if a.acknowledged_at]
        response_times = [
            (a.acknowledged_at - a.created_at).total_seconds()
            for a in acknowledged
        ]
        
        avg_response_time = (
            sum(response_times) / len(response_times)
            if response_times else 0
        )
        
        return create_response(
            success=True,
            message="Alert statistics retrieved",
            data={
                "alert_stats": engine_stats,
                "notification_stats": notif_stats,
                "escalation_stats": escalation_stats,
                "metrics": {
                    "avg_response_time_seconds": round(avg_response_time, 2),
                    "total_alerts_all_time": len(org_alerts),
                    "alerts_today": len([
                        a for a in org_alerts
                        if a.created_at.date() == datetime.now().date()
                    ])
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/stats/timeline", summary="خط زمني للتنبيهات - Alert Timeline")
async def get_alert_timeline(
    organization_id: str = Query(..., description="Organization ID"),
    days: int = Query(7, ge=1, le=90, description="Number of days")
):
    """
    Get alert timeline for specified period
    
    - **Daily counts**: Alerts per day
    - **Trend analysis**: Increasing or decreasing
    - **Peak times**: Identify high-risk periods
    """
    try:
        # Get alerts for time period
        start_date = datetime.now() - timedelta(days=days)
        
        alerts = [
            a for a in ALERTS_DB.values()
            if (a.organization_id == organization_id and
                a.created_at >= start_date)
        ]
        
        # Group by day
        daily_counts = {}
        for alert in alerts:
            day = alert.created_at.date().isoformat()
            if day not in daily_counts:
                daily_counts[day] = {
                    'total': 0,
                    'by_severity': {},
                    'by_type': {}
                }
            
            daily_counts[day]['total'] += 1
            
            severity = alert.severity.value
            daily_counts[day]['by_severity'][severity] = \
                daily_counts[day]['by_severity'].get(severity, 0) + 1
            
            alert_type = alert.type.value
            daily_counts[day]['by_type'][alert_type] = \
                daily_counts[day]['by_type'].get(alert_type, 0) + 1
        
        return create_response(
            success=True,
            message=f"Timeline for last {days} days",
            data={
                "timeline": daily_counts,
                "total_alerts": len(alerts),
                "period_days": days
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
