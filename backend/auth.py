"""
HAZM TUWAIQ - Authentication & Authorization System
Complete authentication with JWT tokens and role-based access control
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import secrets
import hashlib
from dataclasses import dataclass, field


class UserRole(str, Enum):
    """User roles with hierarchical permissions"""
    OWNER = "owner"  # Full system access
    MANAGER = "manager"  # Multi-site management
    SUPERVISOR = "supervisor"  # Site supervision
    WORKER = "worker"  # Basic worker access
    VIEWER = "viewer"  # Read-only access


class Permission(str, Enum):
    """Granular permissions"""
    # Dashboard
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_ANALYTICS = "view_analytics"
    
    # Workers
    VIEW_WORKERS = "view_workers"
    MANAGE_WORKERS = "manage_workers"
    
    # Sites & Cameras
    VIEW_SITES = "view_sites"
    MANAGE_SITES = "manage_sites"
    VIEW_CAMERAS = "view_cameras"
    MANAGE_CAMERAS = "manage_cameras"
    
    # Alerts & Incidents
    VIEW_ALERTS = "view_alerts"
    MANAGE_ALERTS = "manage_alerts"
    RESPOND_INCIDENTS = "respond_incidents"
    
    # Reports
    VIEW_REPORTS = "view_reports"
    GENERATE_REPORTS = "generate_reports"
    EXPORT_REPORTS = "export_reports"
    
    # AI & Predictions
    VIEW_PREDICTIONS = "view_predictions"
    CONFIGURE_AI = "configure_ai"
    
    # System
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    MANAGE_ORGANIZATION = "manage_organization"
    VIEW_AUDIT_LOGS = "view_audit_logs"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[UserRole, List[Permission]] = {
    UserRole.OWNER: [p for p in Permission],  # All permissions
    
    UserRole.MANAGER: [
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_WORKERS,
        Permission.MANAGE_WORKERS,
        Permission.VIEW_SITES,
        Permission.MANAGE_SITES,
        Permission.VIEW_CAMERAS,
        Permission.MANAGE_CAMERAS,
        Permission.VIEW_ALERTS,
        Permission.MANAGE_ALERTS,
        Permission.RESPOND_INCIDENTS,
        Permission.VIEW_REPORTS,
        Permission.GENERATE_REPORTS,
        Permission.EXPORT_REPORTS,
        Permission.VIEW_PREDICTIONS,
        Permission.CONFIGURE_AI,
        Permission.VIEW_AUDIT_LOGS,
    ],
    
    UserRole.SUPERVISOR: [
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_WORKERS,
        Permission.VIEW_SITES,
        Permission.VIEW_CAMERAS,
        Permission.VIEW_ALERTS,
        Permission.RESPOND_INCIDENTS,
        Permission.VIEW_REPORTS,
        Permission.GENERATE_REPORTS,
        Permission.VIEW_PREDICTIONS,
    ],
    
    UserRole.WORKER: [
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_ALERTS,
        Permission.VIEW_REPORTS,
    ],
    
    UserRole.VIEWER: [
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_REPORTS,
    ],
}


@dataclass
class User:
    """User model with authentication and role info"""
    id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    full_name: str
    organization_id: str
    site_ids: List[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    def check_password(self, password: str) -> bool:
        """Verify password"""
        return self.password_hash == self._hash_password(password)
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password with SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission"""
        return permission in ROLE_PERMISSIONS.get(self.role, [])
    
    def has_any_permission(self, permissions: List[Permission]) -> bool:
        """Check if user has any of the listed permissions"""
        return any(self.has_permission(p) for p in permissions)
    
    def has_all_permissions(self, permissions: List[Permission]) -> bool:
        """Check if user has all listed permissions"""
        return all(self.has_permission(p) for p in permissions)
    
    def get_permissions(self) -> List[Permission]:
        """Get all permissions for user's role"""
        return ROLE_PERMISSIONS.get(self.role, [])
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "full_name": self.full_name,
            "organization_id": self.organization_id,
            "site_ids": self.site_ids,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "permissions": [p.value for p in self.get_permissions()],
        }
        
        if include_sensitive:
            data["password_hash"] = self.password_hash
            data["preferences"] = self.preferences
        
        return data


@dataclass
class Session:
    """User session with JWT token"""
    token: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    def is_valid(self) -> bool:
        """Check if session is still valid"""
        return datetime.now() < self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "token": self.token,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_valid": self.is_valid(),
        }


class AuthenticationSystem:
    """Complete authentication and authorization system"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.token_to_user: Dict[str, str] = {}
        
        # Create default admin user
        self._create_default_users()
    
    def _create_default_users(self):
        """Create default users for testing"""
        default_users = [
            {
                "id": "user_owner_001",
                "username": "owner",
                "email": "owner@hazm-tuwaiq.sa",
                "password": "owner123",
                "role": UserRole.OWNER,
                "full_name": "صاحب المنصة",
                "organization_id": "org_001",
            },
            {
                "id": "user_manager_001",
                "username": "manager",
                "email": "manager@hazm-tuwaiq.sa",
                "password": "manager123",
                "role": UserRole.MANAGER,
                "full_name": "مدير العمليات",
                "organization_id": "org_001",
                "site_ids": ["site_001", "site_002"],
            },
            {
                "id": "user_supervisor_001",
                "username": "supervisor",
                "email": "supervisor@hazm-tuwaiq.sa",
                "password": "supervisor123",
                "role": UserRole.SUPERVISOR,
                "full_name": "مشرف الموقع",
                "organization_id": "org_001",
                "site_ids": ["site_001"],
            },
            {
                "id": "user_worker_001",
                "username": "worker",
                "email": "worker@hazm-tuwaiq.sa",
                "password": "worker123",
                "role": UserRole.WORKER,
                "full_name": "عامل الموقع",
                "organization_id": "org_001",
                "site_ids": ["site_001"],
            },
        ]
        
        for user_data in default_users:
            password = user_data.pop("password")
            user = User(
                **user_data,
                password_hash=User._hash_password(password),
            )
            self.users[user.id] = user
    
    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        role: UserRole,
        full_name: str,
        organization_id: str,
        site_ids: List[str] = None,
    ) -> User:
        """Register new user"""
        # Check if username exists
        if any(u.username == username for u in self.users.values()):
            raise ValueError(f"Username '{username}' already exists")
        
        # Check if email exists
        if any(u.email == email for u in self.users.values()):
            raise ValueError(f"Email '{email}' already exists")
        
        user_id = f"user_{secrets.token_hex(8)}"
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=User._hash_password(password),
            role=role,
            full_name=full_name,
            organization_id=organization_id,
            site_ids=site_ids or [],
        )
        
        self.users[user_id] = user
        return user
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return token"""
        # Find user
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break
        
        if not user:
            return None
        
        if not user.is_active:
            raise ValueError("User account is disabled")
        
        if not user.check_password(password):
            return None
        
        # Update last login
        user.last_login = datetime.now()
        
        # Create session
        token = secrets.token_urlsafe(32)
        session = Session(
            token=token,
            user_id=user.id,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=7),
        )
        
        self.sessions[token] = session
        self.token_to_user[token] = user.id
        
        return token
    
    def get_user_by_token(self, token: str) -> Optional[User]:
        """Get user by session token"""
        session = self.sessions.get(token)
        if not session or not session.is_valid():
            return None
        
        user_id = self.token_to_user.get(token)
        return self.users.get(user_id)
    
    def logout(self, token: str) -> bool:
        """Logout user by invalidating token"""
        if token in self.sessions:
            del self.sessions[token]
            del self.token_to_user[token]
            return True
        return False
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_all_users(self, organization_id: Optional[str] = None) -> List[User]:
        """Get all users, optionally filtered by organization"""
        users = list(self.users.values())
        if organization_id:
            users = [u for u in users if u.organization_id == organization_id]
        return users
    
    def update_user(self, user_id: str, **updates) -> User:
        """Update user information"""
        user = self.users.get(user_id)
        if not user:
            raise ValueError(f"User '{user_id}' not found")
        
        # Update allowed fields
        allowed_fields = [
            "email", "full_name", "role", "site_ids", 
            "is_active", "preferences"
        ]
        
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(user, field, value)
        
        # Handle password update separately
        if "password" in updates:
            user.password_hash = User._hash_password(updates["password"])
        
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        if user_id in self.users:
            # Invalidate all sessions
            tokens_to_remove = [
                token for token, uid in self.token_to_user.items() 
                if uid == user_id
            ]
            for token in tokens_to_remove:
                self.logout(token)
            
            del self.users[user_id]
            return True
        return False
    
    def check_permission(self, token: str, permission: Permission) -> bool:
        """Check if token has specific permission"""
        user = self.get_user_by_token(token)
        if not user:
            return False
        return user.has_permission(permission)
    
    def get_user_dashboard_data(self, token: str) -> Dict[str, Any]:
        """Get personalized dashboard data based on user role"""
        user = self.get_user_by_token(token)
        if not user:
            return {"error": "Invalid token"}
        
        # Base data
        data = {
            "user": user.to_dict(),
            "role": user.role.value,
            "permissions": [p.value for p in user.get_permissions()],
        }
        
        # Role-specific priorities and messages
        if user.role == UserRole.OWNER:
            data.update({
                "welcome_message": f"مرحباً {user.full_name}، أنت تدير المنصة بالكامل",
                "priority": "مراجعة أداء جميع المواقع والمؤشرات الاستراتيجية",
                "quick_actions": [
                    "عرض تقرير الأداء الشامل",
                    "إدارة المستخدمين والصلاحيات",
                    "مراجعة التنبيهات الحرجة",
                    "تحليل البيانات التنبؤية",
                ],
            })
        
        elif user.role == UserRole.MANAGER:
            data.update({
                "welcome_message": f"مرحباً {user.full_name}، أنت مسؤول عن {len(user.site_ids)} موقع",
                "priority": "متابعة سلامة العمال والتأكد من الامتثال في جميع المواقع",
                "quick_actions": [
                    "مراجعة حالة المواقع",
                    "متابعة التنبيهات النشطة",
                    "توليد تقرير يومي",
                    "إدارة فرق العمل",
                ],
            })
        
        elif user.role == UserRole.SUPERVISOR:
            data.update({
                "welcome_message": f"مرحباً {user.full_name}، أنت مشرف على الموقع",
                "priority": "التأكد من سلامة العمال والاستجابة للحوادث",
                "quick_actions": [
                    "عرض كاميرات المراقبة",
                    "متابعة التنبيهات الحالية",
                    "فحص حالة المعدات",
                    "تسجيل ملاحظات السلامة",
                ],
            })
        
        elif user.role == UserRole.WORKER:
            data.update({
                "welcome_message": f"مرحباً {user.full_name}، ابق آمناً في العمل",
                "priority": "الالتزام بإجراءات السلامة والإبلاغ عن المخاطر",
                "quick_actions": [
                    "عرض تنبيهات السلامة الخاصة بي",
                    "الإبلاغ عن خطر",
                    "عرض تعليمات السلامة",
                    "حالة تدريباتي",
                ],
            })
        
        else:  # VIEWER
            data.update({
                "welcome_message": f"مرحباً {user.full_name}",
                "priority": "مراقبة الأداء والتقارير",
                "quick_actions": [
                    "عرض لوحة المعلومات",
                    "تصفح التقارير",
                    "مراجعة المؤشرات",
                ],
            })
        
        return data


# Global authentication system instance
auth_system = AuthenticationSystem()


# Helper functions for FastAPI dependency injection
def get_current_user(token: str) -> Optional[User]:
    """Get current user from token"""
    return auth_system.get_user_by_token(token)


def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    def decorator(func):
        def wrapper(token: str, *args, **kwargs):
            if not auth_system.check_permission(token, permission):
                raise PermissionError(f"Permission '{permission.value}' required")
            return func(token, *args, **kwargs)
        return wrapper
    return decorator
