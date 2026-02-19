"""
HAZM TUWAIQ - Alert Engine Module
Real-time alerts with autonomous actions and multi-channel notifications
"""

from .engine import AlertEngine
from .escalation import EscalationManager
from .models import Alert, AlertAction, AlertRule, EscalationRule
from .notifications import (
    EmailChannel,
    NotificationManager,
    SMSChannel,
    WhatsAppChannel,
)

__all__ = [
    "Alert",
    "AlertRule",
    "AlertAction",
    "EscalationRule",
    "AlertEngine",
    "NotificationManager",
    "SMSChannel",
    "EmailChannel",
    "WhatsAppChannel",
    "EscalationManager",
]
