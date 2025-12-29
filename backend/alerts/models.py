"""
HAZM TUWAIQ - Alert Models
Alert types, rules, and escalation definitions
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════

class AlertSeverity(str, Enum):
    """درجة خطورة التنبيه"""
    INFO = "info"              # معلوماتي
    LOW = "low"                # منخفض
    MEDIUM = "medium"          # متوسط
    HIGH = "high"              # عالي
    CRITICAL = "critical"      # حرج


class AlertStatus(str, Enum):
    """حالة التنبيه"""
    PENDING = "pending"        # معلق
    ACTIVE = "active"          # نشط
    ACKNOWLEDGED = "acknowledged"  # تم الاستلام
    IN_PROGRESS = "in_progress"   # قيد المعالجة
    RESOLVED = "resolved"      # تم الحل
    DISMISSED = "dismissed"    # تم الإهمال
    ESCALATED = "escalated"    # تم التصعيد


class AlertType(str, Enum):
    """نوع التنبيه"""
    PPE_VIOLATION = "ppe_violation"           # خرق معدات السلامة
    FALL_DETECTED = "fall_detected"           # سقوط مُكتشف
    UNSAFE_ACT = "unsafe_act"                 # تصرف غير آمن
    COLLISION_RISK = "collision_risk"         # خطر اصطدام
    WORKER_FATIGUE = "worker_fatigue"         # إرهاق عامل
    RESTRICTED_AREA = "restricted_area"       # منطقة محظورة
    EQUIPMENT_MALFUNCTION = "equipment_malfunction"  # عطل معدات
    ENVIRONMENTAL_HAZARD = "environmental_hazard"    # خطر بيئي
    NEAR_MISS = "near_miss"                   # شبه حادث
    INCIDENT = "incident"                     # حادث
    SYSTEM_ALERT = "system_alert"             # تنبيه نظام


class ActionType(str, Enum):
    """نوع الإجراء"""
    NOTIFY_WORKER = "notify_worker"           # إشعار العامل
    NOTIFY_SUPERVISOR = "notify_supervisor"   # إشعار المشرف
    STOP_EQUIPMENT = "stop_equipment"         # إيقاف المعدات
    SOUND_ALARM = "sound_alarm"               # إطلاق إنذار
    ACTIVATE_LIGHT = "activate_light"         # تفعيل ضوء تحذير
    LOCK_ZONE = "lock_zone"                   # قفل منطقة
    CALL_EMERGENCY = "call_emergency"         # اتصال طوارئ
    CREATE_INCIDENT = "create_incident"       # إنشاء حادث
    SEND_SMS = "send_sms"                     # إرسال SMS
    SEND_EMAIL = "send_email"                 # إرسال Email
    SEND_WHATSAPP = "send_whatsapp"          # إرسال WhatsApp


class NotificationChannel(str, Enum):
    """قناة الإشعار"""
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    PUSH = "push"              # Mobile app push notification
    IN_APP = "in_app"          # In-app notification
    WEBHOOK = "webhook"        # External webhook


# ═══════════════════════════════════════════════════════════
# CORE MODELS
# ═══════════════════════════════════════════════════════════

class Alert(BaseModel):
    """
    التنبيه - Alert
    Real-time safety alert
    """
    id: str = Field(default_factory=lambda: f"ALT-{uuid.uuid4().hex[:12].upper()}")
    
    # Basic Info
    type: AlertType
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.ACTIVE
    
    # Content
    title: str
    title_ar: Optional[str] = None
    description: str
    description_ar: Optional[str] = None
    
    # Source
    source: str  # e.g., "AI_DETECTION", "MANUAL", "SYSTEM"
    source_id: Optional[str] = None  # Detection ID, Incident ID, etc.
    
    # Location
    camera_id: Optional[str] = None
    site_id: Optional[str] = None
    zone: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    
    # Organization
    organization_id: str
    
    # Detection Details
    confidence: Optional[float] = None
    evidence: List[str] = Field(default_factory=list)  # URLs to images/videos
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Actions
    actions_taken: List[str] = Field(default_factory=list)
    autonomous_actions: List[str] = Field(default_factory=list)
    
    # Assignment
    assigned_to: Optional[str] = None  # User ID
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    # Escalation
    escalation_level: int = 0
    escalated_at: Optional[datetime] = None
    escalation_path: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Notifications
    notifications_sent: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "ppe_violation",
                "severity": "high",
                "title": "Worker without helmet detected",
                "title_ar": "عامل بدون خوذة",
                "description": "AI detected worker in Zone A without safety helmet",
                "source": "AI_DETECTION",
                "camera_id": "CAM-001",
                "confidence": 0.94,
                "organization_id": "ORG-12345678"
            }
        }


class AlertRule(BaseModel):
    """
    قاعدة التنبيه - Alert Rule
    Configuration for automatic alert generation
    """
    id: str = Field(default_factory=lambda: f"RULE-{uuid.uuid4().hex[:8].upper()}")
    
    # Basic Info
    name: str
    name_ar: Optional[str] = None
    description: Optional[str] = None
    
    # Trigger Conditions
    trigger_type: AlertType
    severity: AlertSeverity
    
    # Conditions (flexible JSON)
    conditions: Dict[str, Any] = Field(default_factory=dict)
    # Example: {"confidence_threshold": 0.8, "duration_seconds": 5}
    
    # Actions to Execute
    actions: List[ActionType] = Field(default_factory=list)
    
    # Notification Settings
    notify_channels: List[NotificationChannel] = Field(default_factory=list)
    notify_roles: List[str] = Field(default_factory=list)  # Role IDs
    notify_users: List[str] = Field(default_factory=list)  # User IDs
    
    # Escalation
    enable_escalation: bool = False
    escalation_delay_minutes: int = 15
    
    # Scope
    organization_id: str
    sites: List[str] = Field(default_factory=list)  # Empty = all sites
    cameras: List[str] = Field(default_factory=list)  # Empty = all cameras
    
    # Status
    is_active: bool = True
    priority: int = 1  # Higher number = higher priority
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "PPE Violation - Critical",
                "trigger_type": "ppe_violation",
                "severity": "critical",
                "conditions": {"confidence_threshold": 0.9},
                "actions": ["notify_supervisor", "sound_alarm", "send_sms"],
                "notify_channels": ["sms", "whatsapp"],
                "enable_escalation": True,
                "escalation_delay_minutes": 5
            }
        }


class AlertAction(BaseModel):
    """
    إجراء التنبيه - Alert Action
    Autonomous action executed by the system
    """
    id: str = Field(default_factory=lambda: f"ACT-{uuid.uuid4().hex[:8].upper()}")
    
    alert_id: str
    action_type: ActionType
    
    # Execution
    status: str = "pending"  # pending, executing, completed, failed
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    success: bool = False
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    # Target
    target: Optional[str] = None  # Equipment ID, Zone ID, User ID, etc.
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)


class EscalationRule(BaseModel):
    """
    قاعدة التصعيد - Escalation Rule
    Define escalation path for unresolved alerts
    """
    id: str = Field(default_factory=lambda: f"ESC-{uuid.uuid4().hex[:8].upper()}")
    
    # Basic Info
    name: str
    name_ar: Optional[str] = None
    
    # Trigger
    alert_types: List[AlertType] = Field(default_factory=list)  # Empty = all types
    min_severity: AlertSeverity = AlertSeverity.MEDIUM
    
    # Escalation Path (ordered list)
    escalation_levels: List[Dict[str, Any]] = Field(default_factory=list)
    # Example: [
    #   {"level": 1, "delay_minutes": 5, "notify_roles": ["supervisor"]},
    #   {"level": 2, "delay_minutes": 10, "notify_roles": ["safety_manager"]},
    #   {"level": 3, "delay_minutes": 15, "notify_roles": ["org_owner"], "actions": ["call_emergency"]}
    # ]
    
    # Scope
    organization_id: str
    
    # Status
    is_active: bool = True
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)


class Notification(BaseModel):
    """
    الإشعار - Notification
    Individual notification sent through a channel
    """
    id: str = Field(default_factory=lambda: f"NOT-{uuid.uuid4().hex[:8].upper()}")
    
    alert_id: str
    channel: NotificationChannel
    
    # Recipient
    recipient_id: Optional[str] = None  # User ID
    recipient_contact: str  # Phone number, email, etc.
    
    # Content
    subject: Optional[str] = None
    message: str
    
    # Status
    status: str = "pending"  # pending, sent, delivered, failed
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    # Provider Response
    provider: Optional[str] = None  # e.g., "Twilio", "SendGrid"
    provider_id: Optional[str] = None  # External message ID
    error: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)


# ═══════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════

class AlertCreate(BaseModel):
    """طلب إنشاء تنبيه"""
    type: AlertType
    severity: AlertSeverity
    title: str
    title_ar: Optional[str] = None
    description: str
    description_ar: Optional[str] = None
    source: str
    camera_id: Optional[str] = None
    site_id: Optional[str] = None
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AlertAcknowledge(BaseModel):
    """تأكيد استلام تنبيه"""
    alert_id: str
    acknowledged_by: str
    notes: Optional[str] = None


class AlertResolve(BaseModel):
    """حل تنبيه"""
    alert_id: str
    resolved_by: str
    resolution_notes: str
    resolution_actions: List[str] = Field(default_factory=list)


class AlertEscalate(BaseModel):
    """تصعيد تنبيه"""
    alert_id: str
    escalate_to: str  # User ID or Role
    reason: str
