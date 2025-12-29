"""
HAZM TUWAIQ - Notification System
Multi-channel notification delivery (SMS, Email, WhatsApp, Push)
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from abc import ABC, abstractmethod

from .models import (
    Alert, Notification, NotificationChannel,
    AlertSeverity
)


# ═══════════════════════════════════════════════════════════
# NOTIFICATION CHANNELS (Abstract Base)
# ═══════════════════════════════════════════════════════════

class NotificationChannelBase(ABC):
    """قناة إشعار - Base class for notification channels"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def send(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Send notification
        
        Args:
            recipient: Recipient contact (phone, email, etc.)
            subject: Message subject
            message: Message body
            metadata: Additional metadata
            
        Returns:
            Tuple of (success, provider_id, error_message)
        """
        pass
    
    @abstractmethod
    def get_channel_type(self) -> NotificationChannel:
        """Get channel type"""
        pass


# ═══════════════════════════════════════════════════════════
# SMS CHANNEL
# ═══════════════════════════════════════════════════════════

class SMSChannel(NotificationChannelBase):
    """
    قناة SMS - SMS notification channel
    Production implementation would use Twilio, AWS SNS, or similar
    """
    
    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None
    ):
        """
        Initialize SMS channel
        
        Args:
            account_sid: Twilio account SID
            auth_token: Twilio auth token
            from_number: Sender phone number
        """
        super().__init__()
        
        self.account_sid = account_sid or "DEMO_SID"
        self.auth_token = auth_token or "DEMO_TOKEN"
        self.from_number = from_number or "+966500000000"
        
        # In production, initialize Twilio client here
        # self.client = Client(account_sid, auth_token)
    
    def send(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Send SMS"""
        try:
            # Validate phone number
            if not recipient.startswith('+'):
                recipient = f"+{recipient}"
            
            # Truncate message if too long (SMS limit)
            max_length = 160
            if len(message) > max_length:
                message = message[:max_length-3] + "..."
            
            # PRODUCTION CODE (commented):
            # message_obj = self.client.messages.create(
            #     body=message,
            #     from_=self.from_number,
            #     to=recipient
            # )
            # return True, message_obj.sid, None
            
            # SIMULATION (for development):
            provider_id = f"SMS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            self.logger.info(
                f"📱 SMS SENT\n"
                f"   To: {recipient}\n"
                f"   Message: {message}\n"
                f"   Provider ID: {provider_id}"
            )
            
            return True, provider_id, None
            
        except Exception as e:
            self.logger.error(f"Failed to send SMS: {e}")
            return False, None, str(e)
    
    def get_channel_type(self) -> NotificationChannel:
        return NotificationChannel.SMS


# ═══════════════════════════════════════════════════════════
# EMAIL CHANNEL
# ═══════════════════════════════════════════════════════════

class EmailChannel(NotificationChannelBase):
    """
    قناة البريد الإلكتروني - Email notification channel
    Production implementation would use SendGrid, AWS SES, or SMTP
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ):
        """
        Initialize email channel
        
        Args:
            api_key: SendGrid API key
            from_email: Sender email address
            from_name: Sender name
        """
        super().__init__()
        
        self.api_key = api_key or "DEMO_API_KEY"
        self.from_email = from_email or "noreply@hazm-tuwaiq.sa"
        self.from_name = from_name or "HAZM TUWAIQ Safety System"
        
        # In production, initialize SendGrid client
        # self.client = SendGridAPIClient(api_key)
    
    def send(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Send email"""
        try:
            # Build HTML email
            html_message = self._build_html_email(subject, message, metadata)
            
            # PRODUCTION CODE (commented):
            # from sendgrid.helpers.mail import Mail
            # email = Mail(
            #     from_email=self.from_email,
            #     to_emails=recipient,
            #     subject=subject,
            #     html_content=html_message
            # )
            # response = self.client.send(email)
            # return True, response.headers.get('X-Message-Id'), None
            
            # SIMULATION (for development):
            provider_id = f"EMAIL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            self.logger.info(
                f"📧 EMAIL SENT\n"
                f"   To: {recipient}\n"
                f"   Subject: {subject}\n"
                f"   Provider ID: {provider_id}"
            )
            
            return True, provider_id, None
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False, None, str(e)
    
    def _build_html_email(
        self,
        subject: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build HTML email template"""
        severity_colors = {
            "critical": "#dc2626",
            "high": "#ea580c",
            "medium": "#d97706",
            "low": "#65a30d",
            "info": "#2563eb"
        }
        
        severity = metadata.get('severity', 'info') if metadata else 'info'
        color = severity_colors.get(severity, "#2563eb")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: {color}; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f9fafb; }}
                .footer {{ padding: 10px; text-align: center; font-size: 12px; color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🔔 {subject}</h2>
                </div>
                <div class="content">
                    <p>{message}</p>
                    {f'<p><strong>Alert ID:</strong> {metadata.get("alert_id")}</p>' if metadata and 'alert_id' in metadata else ''}
                    {f'<p><strong>Camera:</strong> {metadata.get("camera_id")}</p>' if metadata and 'camera_id' in metadata else ''}
                </div>
                <div class="footer">
                    <p>HAZM TUWAIQ Safety Platform | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def get_channel_type(self) -> NotificationChannel:
        return NotificationChannel.EMAIL


# ═══════════════════════════════════════════════════════════
# WHATSAPP CHANNEL
# ═══════════════════════════════════════════════════════════

class WhatsAppChannel(NotificationChannelBase):
    """
    قناة واتساب - WhatsApp notification channel
    Production implementation would use Twilio WhatsApp API
    """
    
    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None
    ):
        """
        Initialize WhatsApp channel
        
        Args:
            account_sid: Twilio account SID
            auth_token: Twilio auth token
            from_number: WhatsApp business number
        """
        super().__init__()
        
        self.account_sid = account_sid or "DEMO_SID"
        self.auth_token = auth_token or "DEMO_TOKEN"
        self.from_number = from_number or "whatsapp:+966500000000"
        
        # In production, initialize Twilio client
        # self.client = Client(account_sid, auth_token)
    
    def send(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Send WhatsApp message"""
        try:
            # Format recipient for WhatsApp
            if not recipient.startswith('whatsapp:'):
                if not recipient.startswith('+'):
                    recipient = f"+{recipient}"
                recipient = f"whatsapp:{recipient}"
            
            # Build message with subject
            full_message = f"*{subject}*\n\n{message}"
            
            # Add alert metadata if available
            if metadata:
                if 'alert_id' in metadata:
                    full_message += f"\n\n🆔 Alert: {metadata['alert_id']}"
                if 'camera_id' in metadata:
                    full_message += f"\n📹 Camera: {metadata['camera_id']}"
            
            # PRODUCTION CODE (commented):
            # message_obj = self.client.messages.create(
            #     body=full_message,
            #     from_=self.from_number,
            #     to=recipient
            # )
            # return True, message_obj.sid, None
            
            # SIMULATION (for development):
            provider_id = f"WHATSAPP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            self.logger.info(
                f"💬 WHATSAPP SENT\n"
                f"   To: {recipient}\n"
                f"   Message: {full_message[:100]}...\n"
                f"   Provider ID: {provider_id}"
            )
            
            return True, provider_id, None
            
        except Exception as e:
            self.logger.error(f"Failed to send WhatsApp: {e}")
            return False, None, str(e)
    
    def get_channel_type(self) -> NotificationChannel:
        return NotificationChannel.WHATSAPP


# ═══════════════════════════════════════════════════════════
# PUSH NOTIFICATION CHANNEL
# ═══════════════════════════════════════════════════════════

class PushChannel(NotificationChannelBase):
    """
    قناة الإشعارات الفورية - Push notification channel
    Production implementation would use Firebase Cloud Messaging (FCM)
    """
    
    def __init__(
        self,
        server_key: Optional[str] = None
    ):
        """
        Initialize push notification channel
        
        Args:
            server_key: FCM server key
        """
        super().__init__()
        
        self.server_key = server_key or "DEMO_FCM_KEY"
        
        # In production, initialize FCM client
        # import firebase_admin
        # from firebase_admin import credentials, messaging
        # cred = credentials.Certificate('path/to/serviceAccount.json')
        # firebase_admin.initialize_app(cred)
    
    def send(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Send push notification"""
        try:
            # recipient should be FCM token
            
            # PRODUCTION CODE (commented):
            # from firebase_admin import messaging
            # notification = messaging.Message(
            #     notification=messaging.Notification(
            #         title=subject,
            #         body=message
            #     ),
            #     token=recipient,
            #     data=metadata or {}
            # )
            # response = messaging.send(notification)
            # return True, response, None
            
            # SIMULATION (for development):
            provider_id = f"PUSH-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            self.logger.info(
                f"🔔 PUSH NOTIFICATION SENT\n"
                f"   Token: {recipient[:20]}...\n"
                f"   Title: {subject}\n"
                f"   Body: {message[:100]}...\n"
                f"   Provider ID: {provider_id}"
            )
            
            return True, provider_id, None
            
        except Exception as e:
            self.logger.error(f"Failed to send push notification: {e}")
            return False, None, str(e)
    
    def get_channel_type(self) -> NotificationChannel:
        return NotificationChannel.PUSH


# ═══════════════════════════════════════════════════════════
# NOTIFICATION MANAGER
# ═══════════════════════════════════════════════════════════

class NotificationManager:
    """
    مدير الإشعارات
    Centralized notification management and delivery
    """
    
    def __init__(self):
        """Initialize notification manager"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize channels
        self.channels: Dict[NotificationChannel, NotificationChannelBase] = {
            NotificationChannel.SMS: SMSChannel(),
            NotificationChannel.EMAIL: EmailChannel(),
            NotificationChannel.WHATSAPP: WhatsAppChannel(),
            NotificationChannel.PUSH: PushChannel()
        }
        
        # Notification history
        self.notifications: Dict[str, Notification] = {}
    
    def send_alert_notification(
        self,
        alert: Alert,
        recipients: List[Dict[str, str]],
        channels: List[NotificationChannel]
    ) -> List[Notification]:
        """
        Send alert notification to multiple recipients via multiple channels
        
        Args:
            alert: Alert object
            recipients: List of recipient dicts with 'id', 'contact', 'channel'
            channels: Channels to use
            
        Returns:
            List of created notifications
        """
        notifications = []
        
        try:
            # Build message
            subject = self._build_subject(alert)
            message = self._build_message(alert)
            
            # Send to each recipient via each channel
            for recipient_info in recipients:
                for channel in channels:
                    # Get recipient contact for this channel
                    contact = recipient_info.get(f'{channel.value}_contact')
                    
                    if not contact:
                        continue
                    
                    # Send notification
                    notification = self._send_notification(
                        alert=alert,
                        channel=channel,
                        recipient_id=recipient_info.get('id'),
                        recipient_contact=contact,
                        subject=subject,
                        message=message
                    )
                    
                    if notification:
                        notifications.append(notification)
                        
                        # Add to alert
                        alert.notifications_sent.append({
                            'notification_id': notification.id,
                            'channel': channel.value,
                            'sent_at': notification.sent_at.isoformat() if notification.sent_at else None
                        })
            
            return notifications
            
        except Exception as e:
            self.logger.error(f"Failed to send alert notifications: {e}")
            return notifications
    
    def _send_notification(
        self,
        alert: Alert,
        channel: NotificationChannel,
        recipient_id: str,
        recipient_contact: str,
        subject: str,
        message: str
    ) -> Optional[Notification]:
        """Send single notification"""
        try:
            # Create notification record
            notification = Notification(
                alert_id=alert.id,
                channel=channel,
                recipient_id=recipient_id,
                recipient_contact=recipient_contact,
                subject=subject,
                message=message,
                status="pending"
            )
            
            # Get channel handler
            channel_handler = self.channels.get(channel)
            
            if not channel_handler:
                notification.status = "failed"
                notification.error = f"Channel {channel.value} not configured"
                return notification
            
            # Send via channel
            success, provider_id, error = channel_handler.send(
                recipient=recipient_contact,
                subject=subject,
                message=message,
                metadata={
                    'alert_id': alert.id,
                    'severity': alert.severity.value,
                    'camera_id': alert.camera_id
                }
            )
            
            # Update notification
            notification.sent_at = datetime.now()
            
            if success:
                notification.status = "sent"
                notification.provider_id = provider_id
                # Simulate delivery
                notification.delivered_at = datetime.now()
            else:
                notification.status = "failed"
                notification.error = error
            
            # Store notification
            self.notifications[notification.id] = notification
            
            return notification
            
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
            return None
    
    def _build_subject(self, alert: Alert) -> str:
        """Build notification subject"""
        severity_emoji = {
            AlertSeverity.CRITICAL: "🚨",
            AlertSeverity.HIGH: "⚠️",
            AlertSeverity.MEDIUM: "⚡",
            AlertSeverity.LOW: "ℹ️",
            AlertSeverity.INFO: "📢"
        }
        
        emoji = severity_emoji.get(alert.severity, "🔔")
        
        return f"{emoji} {alert.severity.value.upper()}: {alert.title}"
    
    def _build_message(self, alert: Alert) -> str:
        """Build notification message"""
        message = f"{alert.description}\n\n"
        
        if alert.camera_id:
            message += f"📹 Camera: {alert.camera_id}\n"
        
        if alert.zone:
            message += f"📍 Zone: {alert.zone}\n"
        
        if alert.confidence:
            message += f"🎯 Confidence: {alert.confidence:.1%}\n"
        
        message += f"⏰ Time: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += f"🆔 Alert ID: {alert.id}"
        
        return message
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        total = len(self.notifications)
        
        if total == 0:
            return {
                "total": 0,
                "by_status": {},
                "by_channel": {}
            }
        
        by_status = {}
        by_channel = {}
        
        for notif in self.notifications.values():
            # By status
            by_status[notif.status] = by_status.get(notif.status, 0) + 1
            
            # By channel
            channel = notif.channel.value
            by_channel[channel] = by_channel.get(channel, 0) + 1
        
        return {
            "total": total,
            "by_status": by_status,
            "by_channel": by_channel,
            "delivery_rate": by_status.get('sent', 0) / total if total > 0 else 0
        }


# Singleton instance
_notification_manager: Optional[NotificationManager] = None


def get_notification_manager() -> NotificationManager:
    """Get singleton NotificationManager instance"""
    global _notification_manager
    
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    
    return _notification_manager
