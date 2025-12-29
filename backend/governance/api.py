"""
HAZM TUWAIQ - Governance API
Organization, User, and RBAC management endpoints
"""

from fastapi import APIRouter, HTTPException, Header, Body, Depends
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from .models import (
    Organization, User, Role, Permission,
    OrganizationCreate, UserCreate, UserLogin,
    TokenResponse, RoleCreate, PermissionCheck,
    UserStatus
)
from .auth import get_auth_manager, get_token_manager
from .rbac import get_rbac_manager

router = APIRouter()
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# IN-MEMORY DATABASES (سيتم استبدالها بقاعدة بيانات حقيقية)
# ═══════════════════════════════════════════════════════════

ORGANIZATIONS_DB: Dict[str, Organization] = {}
USERS_DB: Dict[str, User] = {}
ROLES_DB: Dict[str, Role] = {}
PERMISSIONS_DB: Dict[str, Permission] = {}

# Initialize with system roles and permissions
rbac_mgr = get_rbac_manager()
PERMISSIONS_DB.update(rbac_mgr.system_permissions)
ROLES_DB.update(rbac_mgr.system_roles)


# ═══════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════

def create_response(status: str, data: Any, message: str = "") -> Dict:
    """Create unified JSON response"""
    return {
        "status": status,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }


def get_current_user_from_token(authorization: Optional[str] = Header(None)) -> User:
    """Extract and validate user from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail=create_response("error", None, "Token مطلوب")
        )
    
    token = authorization.replace("Bearer ", "")
    token_mgr = get_token_manager()
    user, error = token_mgr.require_auth(token, USERS_DB)
    
    if error:
        raise HTTPException(
            status_code=401,
            detail=create_response("error", None, error)
        )
    
    return user


# ═══════════════════════════════════════════════════════════
# ORGANIZATION ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.post("/organizations")
def create_organization(org_data: OrganizationCreate):
    """
    إنشاء مؤسسة جديدة
    Create new organization
    """
    try:
        # Create organization
        org = Organization(
            name=org_data.name,
            name_ar=org_data.name_ar,
            type=org_data.type,
            email=org_data.email,
            phone=org_data.phone,
            plan=org_data.plan
        )
        
        # Save to database
        ORGANIZATIONS_DB[org.id] = org
        
        logger.info(f"Organization created: {org.id} - {org.name}")
        
        return create_response(
            status="success",
            data=org.model_dump(),
            message=f"تم إنشاء المؤسسة بنجاح: {org.name}"
        )
        
    except Exception as e:
        logger.error(f"Failed to create organization: {e}")
        raise HTTPException(
            status_code=500,
            detail=create_response("error", None, str(e))
        )


@router.get("/organizations")
def list_organizations(
    current_user: User = Depends(get_current_user_from_token)
):
    """
    قائمة المؤسسات
    List organizations (admin only)
    """
    try:
        # Check if user is admin
        rbac = get_rbac_manager()
        if not rbac.has_permission(
            current_user,
            "PERM-SYSTEM-ADMIN",
            ROLES_DB
        ):
            # Regular users see only their organization
            org = ORGANIZATIONS_DB.get(current_user.organization_id)
            orgs = [org.model_dump()] if org else []
        else:
            # Admins see all
            orgs = [org.model_dump() for org in ORGANIZATIONS_DB.values()]
        
        return create_response(
            status="success",
            data={
                "organizations": orgs,
                "total": len(orgs)
            },
            message=f"تم جلب {len(orgs)} مؤسسة"
        )
        
    except Exception as e:
        logger.error(f"Failed to list organizations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/organizations/{org_id}")
def get_organization(
    org_id: str,
    current_user: User = Depends(get_current_user_from_token)
):
    """
    تفاصيل مؤسسة
    Get organization details
    """
    try:
        org = ORGANIZATIONS_DB.get(org_id)
        
        if not org:
            raise HTTPException(
                status_code=404,
                detail=create_response("error", None, "المؤسسة غير موجودة")
            )
        
        # Check access
        if org_id != current_user.organization_id:
            rbac = get_rbac_manager()
            if not rbac.has_permission(current_user, "PERM-SYSTEM-ADMIN", ROLES_DB):
                raise HTTPException(
                    status_code=403,
                    detail=create_response("error", None, "غير مصرح لك بالوصول")
                )
        
        return create_response(
            status="success",
            data=org.model_dump(),
            message="تم جلب بيانات المؤسسة"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get organization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# USER ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.post("/users")
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user_from_token)
):
    """
    إنشاء مستخدم جديد
    Create new user (requires manage_users permission)
    """
    try:
        # Check permission
        rbac = get_rbac_manager()
        if not rbac.has_permission(current_user, "PERM-MANAGE-USERS", ROLES_DB):
            raise HTTPException(
                status_code=403,
                detail=create_response("error", None, "غير مصرح لك بإنشاء مستخدمين")
            )
        
        # Check if username exists
        for user in USERS_DB.values():
            if user.username == user_data.username:
                raise HTTPException(
                    status_code=400,
                    detail=create_response("error", None, "اسم المستخدم موجود مسبقاً")
                )
        
        # Hash password
        auth_mgr = get_auth_manager()
        password_hash = auth_mgr.hash_password(user_data.password)
        
        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            full_name_ar=user_data.full_name_ar,
            organization_id=user_data.organization_id,
            password_hash=password_hash,
            roles=user_data.roles,
            status=UserStatus.ACTIVE
        )
        
        # Save to database
        USERS_DB[user.id] = user
        
        logger.info(f"User created: {user.id} - {user.username}")
        
        # Return without password_hash
        user_dict = user.model_dump()
        user_dict.pop("password_hash", None)
        user_dict.pop("session_token", None)
        user_dict.pop("refresh_token", None)
        
        return create_response(
            status="success",
            data=user_dict,
            message=f"تم إنشاء المستخدم بنجاح: {user.username}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/login")
def login(login_data: UserLogin):
    """
    تسجيل دخول
    User login - returns JWT tokens
    """
    try:
        auth_mgr = get_auth_manager()
        
        # Login
        token_response, error = auth_mgr.login(login_data, USERS_DB)
        
        if error:
            raise HTTPException(
                status_code=401,
                detail=create_response("error", None, error)
            )
        
        logger.info(f"User logged in: {login_data.username}")
        
        return create_response(
            status="success",
            data=token_response.model_dump(),
            message="تم تسجيل الدخول بنجاح"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/auth/logout")
def logout(current_user: User = Depends(get_current_user_from_token)):
    """
    تسجيل خروج
    User logout
    """
    try:
        auth_mgr = get_auth_manager()
        auth_mgr.logout(current_user)
        
        logger.info(f"User logged out: {current_user.username}")
        
        return create_response(
            status="success",
            data=None,
            message="تم تسجيل الخروج بنجاح"
        )
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/me")
def get_current_user_info(
    current_user: User = Depends(get_current_user_from_token)
):
    """
    معلومات المستخدم الحالي
    Get current user info
    """
    try:
        user_dict = current_user.model_dump()
        user_dict.pop("password_hash", None)
        user_dict.pop("session_token", None)
        user_dict.pop("refresh_token", None)
        
        return create_response(
            status="success",
            data=user_dict,
            message="تم جلب بيانات المستخدم"
        )
        
    except Exception as e:
        logger.error(f"Failed to get user info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
def list_users(
    current_user: User = Depends(get_current_user_from_token)
):
    """
    قائمة المستخدمين
    List users in organization
    """
    try:
        # Check permission
        rbac = get_rbac_manager()
        if not rbac.has_permission(current_user, "PERM-VIEW-USERS", ROLES_DB):
            raise HTTPException(
                status_code=403,
                detail=create_response("error", None, "غير مصرح لك بعرض المستخدمين")
            )
        
        # Filter by organization
        users = [
            u for u in USERS_DB.values()
            if u.organization_id == current_user.organization_id
        ]
        
        # Remove sensitive data
        users_data = []
        for u in users:
            user_dict = u.model_dump()
            user_dict.pop("password_hash", None)
            user_dict.pop("session_token", None)
            user_dict.pop("refresh_token", None)
            users_data.append(user_dict)
        
        return create_response(
            status="success",
            data={
                "users": users_data,
                "total": len(users_data)
            },
            message=f"تم جلب {len(users_data)} مستخدم"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# ROLE ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.get("/roles")
def list_roles(
    current_user: User = Depends(get_current_user_from_token)
):
    """
    قائمة الأدوار
    List available roles
    """
    try:
        # Get system roles + organization roles
        roles = [
            r.model_dump() for r in ROLES_DB.values()
            if r.is_system_role or r.organization_id == current_user.organization_id
        ]
        
        return create_response(
            status="success",
            data={
                "roles": roles,
                "total": len(roles)
            },
            message=f"تم جلب {len(roles)} دور"
        )
        
    except Exception as e:
        logger.error(f"Failed to list roles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users/{user_id}/roles/{role_id}")
def assign_role_to_user(
    user_id: str,
    role_id: str,
    current_user: User = Depends(get_current_user_from_token)
):
    """
    تعيين دور لمستخدم
    Assign role to user
    """
    try:
        # Check permission
        rbac = get_rbac_manager()
        if not rbac.has_permission(current_user, "PERM-MANAGE-USERS", ROLES_DB):
            raise HTTPException(
                status_code=403,
                detail=create_response("error", None, "غير مصرح لك بتعيين الأدوار")
            )
        
        # Get user
        user = USERS_DB.get(user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=create_response("error", None, "المستخدم غير موجود")
            )
        
        # Assign role
        success, error = rbac.assign_role(user, role_id, ROLES_DB)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=create_response("error", None, error)
            )
        
        logger.info(f"Role {role_id} assigned to user {user_id}")
        
        return create_response(
            status="success",
            data={"user_id": user_id, "role_id": role_id},
            message="تم تعيين الدور بنجاح"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to assign role: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════
# PERMISSION ENDPOINTS
# ═══════════════════════════════════════════════════════════

@router.post("/permissions/check")
def check_permission(
    check: PermissionCheck,
    current_user: User = Depends(get_current_user_from_token)
):
    """
    فحص صلاحية
    Check if user has specific permission
    """
    try:
        rbac = get_rbac_manager()
        
        has_permission, reason = rbac.check_permission(
            check, USERS_DB, ROLES_DB, PERMISSIONS_DB
        )
        
        return create_response(
            status="success",
            data={
                "has_permission": has_permission,
                "reason": reason
            },
            message="تم فحص الصلاحية"
        )
        
    except Exception as e:
        logger.error(f"Failed to check permission: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/permissions")
def list_permissions(
    current_user: User = Depends(get_current_user_from_token)
):
    """
    قائمة الصلاحيات
    List all available permissions
    """
    try:
        permissions = [p.model_dump() for p in PERMISSIONS_DB.values()]
        
        return create_response(
            status="success",
            data={
                "permissions": permissions,
                "total": len(permissions)
            },
            message=f"تم جلب {len(permissions)} صلاحية"
        )
        
    except Exception as e:
        logger.error(f"Failed to list permissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
