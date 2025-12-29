"""
HAZM TUWAIQ - Governance Data Models
Organizations, Users, Roles, and Permissions
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════

class OrganizationType(str, Enum):
    """نوع المؤسسة"""
    ENTERPRISE = "enterprise"          # شركة كبيرة
    CONTRACTOR = "contractor"          # مقاول
    CONSULTANT = "consultant"          # استشاري
    GOVERNMENT = "government"          # جهة حكومية
    STANDALONE = "standalone"          # مستقل


class UserStatus(str, Enum):
    """حالة المستخدم"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class RoleType(str, Enum):
    """أنواع الأدوار"""
    SUPER_ADMIN = "super_admin"        # مدير النظام
    ORG_OWNER = "org_owner"            # مالك المؤسسة
    ORG_ADMIN = "org_admin"            # مدير المؤسسة
    SAFETY_MANAGER = "safety_manager"  # مدير السلامة
    SUPERVISOR = "supervisor"          # مشرف
    OPERATOR = "operator"              # مشغل
    VIEWER = "viewer"                  # مشاهد فقط
    AUDITOR = "auditor"                # مدقق


class PermissionScope(str, Enum):
    """نطاق الصلاحية"""
    SYSTEM = "system"          # على مستوى النظام
    ORGANIZATION = "organization"  # على مستوى المؤسسة
    PROJECT = "project"        # على مستوى المشروع
    SITE = "site"              # على مستوى الموقع
    CAMERA = "camera"          # على مستوى الكاميرا


class PermissionAction(str, Enum):
    """نوع الإجراء"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    EXPORT = "export"


# ═══════════════════════════════════════════════════════════
# CORE MODELS
# ═══════════════════════════════════════════════════════════

class Organization(BaseModel):
    """
    المؤسسة - Organization
    Multi-tenant isolation
    """
    id: str = Field(default_factory=lambda: f"ORG-{uuid.uuid4().hex[:8].upper()}")
    name: str = Field(..., min_length=2, max_length=200)
    name_ar: Optional[str] = None
    
    type: OrganizationType
    industry: Optional[str] = None
    
    # Contact Info
    email: EmailStr
    phone: str
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Saudi Arabia"
    
    # License & Compliance
    license_number: Optional[str] = None
    cr_number: Optional[str] = None  # Commercial Registration
    vat_number: Optional[str] = None
    
    # Subscription
    plan: str = "basic"  # basic, professional, enterprise
    max_users: int = 10
    max_cameras: int = 5
    max_sites: int = 1
    
    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    # Parent-Child Relationship
    parent_org_id: Optional[str] = None  # للشركات التابعة
    
    # Settings
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "ACME Construction Co.",
                "name_ar": "شركة أكمي للمقاولات",
                "type": "contractor",
                "email": "info@acme-construction.sa",
                "phone": "+966501234567",
                "plan": "enterprise",
                "max_users": 100,
                "max_cameras": 50
            }
        }


class User(BaseModel):
    """
    المستخدم - User
    Individual with specific roles and permissions
    """
    id: str = Field(default_factory=lambda: f"USR-{uuid.uuid4().hex[:8].upper()}")
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    
    # Personal Info
    full_name: str
    full_name_ar: Optional[str] = None
    phone: Optional[str] = None
    employee_id: Optional[str] = None
    
    # Organization
    organization_id: str
    department: Optional[str] = None
    position: Optional[str] = None
    
    # Authentication
    password_hash: str  # bcrypt hash
    must_change_password: bool = False
    two_factor_enabled: bool = False
    
    # Status
    status: UserStatus = UserStatus.PENDING
    is_verified: bool = False
    email_verified: bool = False
    phone_verified: bool = False
    
    # Roles
    roles: List[str] = Field(default_factory=list)  # Role IDs
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    
    # Session Management
    session_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    
    # Security
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    # Preferences
    language: str = "ar"
    timezone: str = "Asia/Riyadh"
    preferences: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "ahmed.saleh",
                "email": "ahmed.saleh@acme.sa",
                "full_name": "Ahmed Saleh Al-Otaibi",
                "full_name_ar": "أحمد صالح العتيبي",
                "organization_id": "ORG-12345678",
                "roles": ["ROLE-SUPERVISOR"],
                "status": "active"
            }
        }


class Role(BaseModel):
    """
    الدور - Role
    Collection of permissions
    """
    id: str = Field(default_factory=lambda: f"ROLE-{uuid.uuid4().hex[:8].upper()}")
    name: str = Field(..., min_length=2, max_length=100)
    name_ar: Optional[str] = None
    description: Optional[str] = None
    
    # Role Type
    role_type: RoleType
    
    # Organization
    organization_id: Optional[str] = None  # None = system role
    
    # Permissions
    permissions: List[str] = Field(default_factory=list)  # Permission IDs
    
    # Status
    is_active: bool = True
    is_system_role: bool = False  # System roles can't be deleted
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Safety Supervisor",
                "name_ar": "مشرف السلامة",
                "role_type": "supervisor",
                "permissions": ["PERM-VIEW-CAMERAS", "PERM-CREATE-INCIDENT"]
            }
        }


class Permission(BaseModel):
    """
    الصلاحية - Permission
    Granular access control
    """
    id: str = Field(default_factory=lambda: f"PERM-{uuid.uuid4().hex[:8].upper()}")
    name: str = Field(..., min_length=2, max_length=100)
    name_ar: Optional[str] = None
    description: Optional[str] = None
    
    # Permission Details
    resource: str  # e.g., "cameras", "incidents", "users"
    action: PermissionAction
    scope: PermissionScope
    
    # Conditions (optional)
    conditions: Optional[Dict[str, Any]] = None
    
    # System Permission
    is_system_permission: bool = False
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "View Live Cameras",
                "name_ar": "مشاهدة الكاميرات المباشرة",
                "resource": "cameras",
                "action": "read",
                "scope": "camera"
            }
        }


class Project(BaseModel):
    """
    المشروع - Project
    Construction project or site
    """
    id: str = Field(default_factory=lambda: f"PRJ-{uuid.uuid4().hex[:8].upper()}")
    name: str
    name_ar: Optional[str] = None
    description: Optional[str] = None
    
    # Organization
    organization_id: str
    
    # Location
    address: Optional[str] = None
    city: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None  # {"lat": 24.7136, "lng": 46.6753}
    
    # Timeline
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = "active"  # planning, active, completed, suspended
    
    # Resources
    assigned_cameras: List[str] = Field(default_factory=list)
    assigned_users: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Riyadh Metro Station - Phase 2",
                "name_ar": "محطة مترو الرياض - المرحلة الثانية",
                "organization_id": "ORG-12345678",
                "city": "Riyadh",
                "status": "active"
            }
        }


class Site(BaseModel):
    """
    الموقع - Site
    Physical location within a project
    """
    id: str = Field(default_factory=lambda: f"SITE-{uuid.uuid4().hex[:8].upper()}")
    name: str
    name_ar: Optional[str] = None
    
    # Project
    project_id: str
    organization_id: str
    
    # Location
    zone: Optional[str] = None  # e.g., "Zone A", "Building 1"
    floor: Optional[str] = None
    area: Optional[str] = None
    
    # Cameras
    cameras: List[str] = Field(default_factory=list)
    
    # Safety Info
    hazard_level: str = "medium"  # low, medium, high, critical
    restricted: bool = False
    requires_ppe: List[str] = Field(default_factory=list)  # ["helmet", "vest"]
    
    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Main Construction Area",
                "name_ar": "منطقة البناء الرئيسية",
                "project_id": "PRJ-12345678",
                "zone": "Zone A",
                "hazard_level": "high",
                "requires_ppe": ["helmet", "vest", "boots"]
            }
        }


# ═══════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════

class OrganizationCreate(BaseModel):
    """طلب إنشاء مؤسسة"""
    name: str
    name_ar: Optional[str] = None
    type: OrganizationType
    email: EmailStr
    phone: str
    plan: str = "basic"


class UserCreate(BaseModel):
    """طلب إنشاء مستخدم"""
    username: str
    email: EmailStr
    password: str
    full_name: str
    full_name_ar: Optional[str] = None
    organization_id: str
    roles: List[str] = Field(default_factory=list)


class UserLogin(BaseModel):
    """طلب تسجيل دخول"""
    username: str
    password: str
    organization_id: Optional[str] = None


class TokenResponse(BaseModel):
    """استجابة Token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


class RoleCreate(BaseModel):
    """طلب إنشاء دور"""
    name: str
    name_ar: Optional[str] = None
    role_type: RoleType
    permissions: List[str] = Field(default_factory=list)


class PermissionCheck(BaseModel):
    """فحص صلاحية"""
    user_id: str
    resource: str
    action: PermissionAction
    scope: PermissionScope
    resource_id: Optional[str] = None
