"""
HAZM TUWAIQ - RBAC Manager
Role-Based Access Control with granular permissions
"""

from typing import Optional, List, Dict, Any, Set
import logging
from datetime import datetime

from .models import (
    User, Role, Permission, Organization,
    PermissionAction, PermissionScope, PermissionCheck
)


class RBACManager:
    """
    مدير التحكم بالوصول المبني على الأدوار
    Role-Based Access Control Manager
    """
    
    def __init__(self):
        """Initialize RBAC manager"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize system permissions
        self.system_permissions = self._create_system_permissions()
        self.system_roles = self._create_system_roles()
    
    def _create_system_permissions(self) -> Dict[str, Permission]:
        """Create default system permissions"""
        permissions = {}
        
        # Camera Permissions
        permissions["view_cameras"] = Permission(
            id="PERM-VIEW-CAMERAS",
            name="View Cameras",
            name_ar="مشاهدة الكاميرات",
            resource="cameras",
            action=PermissionAction.READ,
            scope=PermissionScope.CAMERA,
            is_system_permission=True
        )
        
        permissions["manage_cameras"] = Permission(
            id="PERM-MANAGE-CAMERAS",
            name="Manage Cameras",
            name_ar="إدارة الكاميرات",
            resource="cameras",
            action=PermissionAction.UPDATE,
            scope=PermissionScope.CAMERA,
            is_system_permission=True
        )
        
        # Incident Permissions
        permissions["view_incidents"] = Permission(
            id="PERM-VIEW-INCIDENTS",
            name="View Incidents",
            name_ar="مشاهدة الحوادث",
            resource="incidents",
            action=PermissionAction.READ,
            scope=PermissionScope.ORGANIZATION,
            is_system_permission=True
        )
        
        permissions["create_incident"] = Permission(
            id="PERM-CREATE-INCIDENT",
            name="Create Incident",
            name_ar="إنشاء حادث",
            resource="incidents",
            action=PermissionAction.CREATE,
            scope=PermissionScope.SITE,
            is_system_permission=True
        )
        
        permissions["approve_incident"] = Permission(
            id="PERM-APPROVE-INCIDENT",
            name="Approve Incident",
            name_ar="اعتماد حادث",
            resource="incidents",
            action=PermissionAction.APPROVE,
            scope=PermissionScope.ORGANIZATION,
            is_system_permission=True
        )
        
        # User Permissions
        permissions["view_users"] = Permission(
            id="PERM-VIEW-USERS",
            name="View Users",
            name_ar="مشاهدة المستخدمين",
            resource="users",
            action=PermissionAction.READ,
            scope=PermissionScope.ORGANIZATION,
            is_system_permission=True
        )
        
        permissions["manage_users"] = Permission(
            id="PERM-MANAGE-USERS",
            name="Manage Users",
            name_ar="إدارة المستخدمين",
            resource="users",
            action=PermissionAction.UPDATE,
            scope=PermissionScope.ORGANIZATION,
            is_system_permission=True
        )
        
        # Alert Permissions
        permissions["view_alerts"] = Permission(
            id="PERM-VIEW-ALERTS",
            name="View Alerts",
            name_ar="مشاهدة التنبيهات",
            resource="alerts",
            action=PermissionAction.READ,
            scope=PermissionScope.SITE,
            is_system_permission=True
        )
        
        permissions["acknowledge_alert"] = Permission(
            id="PERM-ACK-ALERT",
            name="Acknowledge Alert",
            name_ar="تأكيد تنبيه",
            resource="alerts",
            action=PermissionAction.UPDATE,
            scope=PermissionScope.SITE,
            is_system_permission=True
        )
        
        # Report Permissions
        permissions["view_reports"] = Permission(
            id="PERM-VIEW-REPORTS",
            name="View Reports",
            name_ar="مشاهدة التقارير",
            resource="reports",
            action=PermissionAction.READ,
            scope=PermissionScope.ORGANIZATION,
            is_system_permission=True
        )
        
        permissions["export_reports"] = Permission(
            id="PERM-EXPORT-REPORTS",
            name="Export Reports",
            name_ar="تصدير التقارير",
            resource="reports",
            action=PermissionAction.EXPORT,
            scope=PermissionScope.ORGANIZATION,
            is_system_permission=True
        )
        
        # System Permissions
        permissions["manage_organization"] = Permission(
            id="PERM-MANAGE-ORG",
            name="Manage Organization",
            name_ar="إدارة المؤسسة",
            resource="organization",
            action=PermissionAction.UPDATE,
            scope=PermissionScope.ORGANIZATION,
            is_system_permission=True
        )
        
        permissions["system_admin"] = Permission(
            id="PERM-SYSTEM-ADMIN",
            name="System Administration",
            name_ar="إدارة النظام",
            resource="system",
            action=PermissionAction.EXECUTE,
            scope=PermissionScope.SYSTEM,
            is_system_permission=True
        )
        
        return permissions
    
    def _create_system_roles(self) -> Dict[str, Role]:
        """Create default system roles"""
        roles = {}
        perms = self.system_permissions
        
        # Super Admin - Full Access
        roles["super_admin"] = Role(
            id="ROLE-SUPER-ADMIN",
            name="Super Administrator",
            name_ar="مدير النظام الأعلى",
            role_type="super_admin",
            permissions=[p.id for p in perms.values()],
            is_system_role=True
        )
        
        # Organization Owner
        roles["org_owner"] = Role(
            id="ROLE-ORG-OWNER",
            name="Organization Owner",
            name_ar="مالك المؤسسة",
            role_type="org_owner",
            permissions=[
                perms["manage_organization"].id,
                perms["manage_users"].id,
                perms["view_users"].id,
                perms["manage_cameras"].id,
                perms["view_cameras"].id,
                perms["view_incidents"].id,
                perms["approve_incident"].id,
                perms["view_reports"].id,
                perms["export_reports"].id,
            ],
            is_system_role=True
        )
        
        # Safety Manager
        roles["safety_manager"] = Role(
            id="ROLE-SAFETY-MGR",
            name="Safety Manager",
            name_ar="مدير السلامة",
            role_type="safety_manager",
            permissions=[
                perms["view_cameras"].id,
                perms["view_incidents"].id,
                perms["create_incident"].id,
                perms["approve_incident"].id,
                perms["view_alerts"].id,
                perms["acknowledge_alert"].id,
                perms["view_reports"].id,
                perms["export_reports"].id,
            ],
            is_system_role=True
        )
        
        # Supervisor
        roles["supervisor"] = Role(
            id="ROLE-SUPERVISOR",
            name="Supervisor",
            name_ar="مشرف",
            role_type="supervisor",
            permissions=[
                perms["view_cameras"].id,
                perms["view_incidents"].id,
                perms["create_incident"].id,
                perms["view_alerts"].id,
                perms["acknowledge_alert"].id,
                perms["view_reports"].id,
            ],
            is_system_role=True
        )
        
        # Operator
        roles["operator"] = Role(
            id="ROLE-OPERATOR",
            name="Operator",
            name_ar="مشغل",
            role_type="operator",
            permissions=[
                perms["view_cameras"].id,
                perms["view_incidents"].id,
                perms["view_alerts"].id,
            ],
            is_system_role=True
        )
        
        # Viewer
        roles["viewer"] = Role(
            id="ROLE-VIEWER",
            name="Viewer",
            name_ar="مشاهد",
            role_type="viewer",
            permissions=[
                perms["view_cameras"].id,
                perms["view_incidents"].id,
                perms["view_reports"].id,
            ],
            is_system_role=True
        )
        
        # Auditor
        roles["auditor"] = Role(
            id="ROLE-AUDITOR",
            name="Auditor",
            name_ar="مدقق",
            role_type="auditor",
            permissions=[
                perms["view_incidents"].id,
                perms["view_reports"].id,
                perms["export_reports"].id,
                perms["view_users"].id,
            ],
            is_system_role=True
        )
        
        return roles
    
    def get_user_permissions(
        self,
        user: User,
        roles_db: Dict[str, Role]
    ) -> Set[str]:
        """
        Get all permissions for a user
        
        Args:
            user: User object
            roles_db: Roles database
            
        Returns:
            Set of permission IDs
        """
        permissions = set()
        
        for role_id in user.roles:
            role = roles_db.get(role_id)
            if role and role.is_active:
                permissions.update(role.permissions)
        
        return permissions
    
    def has_permission(
        self,
        user: User,
        permission_id: str,
        roles_db: Dict[str, Role]
    ) -> bool:
        """
        Check if user has specific permission
        
        Args:
            user: User object
            permission_id: Permission ID to check
            roles_db: Roles database
            
        Returns:
            True if user has permission
        """
        user_permissions = self.get_user_permissions(user, roles_db)
        return permission_id in user_permissions
    
    def check_permission(
        self,
        check: PermissionCheck,
        users_db: Dict[str, User],
        roles_db: Dict[str, Role],
        permissions_db: Dict[str, Permission]
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if user has permission for specific action
        
        Args:
            check: Permission check request
            users_db: Users database
            roles_db: Roles database
            permissions_db: Permissions database
            
        Returns:
            Tuple of (has_permission, reason)
        """
        # Get user
        user = users_db.get(check.user_id)
        if not user:
            return False, "المستخدم غير موجود"
        
        # Get user permissions
        user_permissions = self.get_user_permissions(user, roles_db)
        
        # Find matching permission
        for perm_id in user_permissions:
            perm = permissions_db.get(perm_id)
            if not perm:
                continue
            
            # Check if permission matches
            if (perm.resource == check.resource and
                perm.action == check.action and
                perm.scope == check.scope):
                return True, None
        
        return False, f"ليس لديك صلاحية {check.action.value} على {check.resource}"
    
    def assign_role(
        self,
        user: User,
        role_id: str,
        roles_db: Dict[str, Role]
    ) -> Tuple[bool, Optional[str]]:
        """
        Assign role to user
        
        Args:
            user: User object
            role_id: Role ID to assign
            roles_db: Roles database
            
        Returns:
            Tuple of (success, error_message)
        """
        # Check if role exists
        role = roles_db.get(role_id)
        if not role:
            return False, "الدور غير موجود"
        
        # Check if role is active
        if not role.is_active:
            return False, "الدور غير نشط"
        
        # Check if already assigned
        if role_id in user.roles:
            return False, "الدور مُعيّن مسبقاً"
        
        # Assign role
        user.roles.append(role_id)
        user.updated_at = datetime.now()
        
        return True, None
    
    def remove_role(
        self,
        user: User,
        role_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Remove role from user
        
        Args:
            user: User object
            role_id: Role ID to remove
            
        Returns:
            Tuple of (success, error_message)
        """
        if role_id not in user.roles:
            return False, "الدور غير مُعيّن للمستخدم"
        
        user.roles.remove(role_id)
        user.updated_at = datetime.now()
        
        return True, None


class PermissionChecker:
    """
    فاحص الصلاحيات
    Helper class for checking permissions in routes
    """
    
    def __init__(self, rbac_manager: RBACManager):
        """Initialize permission checker"""
        self.rbac = rbac_manager
        self.logger = logging.getLogger(__name__)
    
    def require_permission(
        self,
        user: User,
        resource: str,
        action: PermissionAction,
        scope: PermissionScope,
        roles_db: Dict[str, Role],
        permissions_db: Dict[str, Permission]
    ) -> Tuple[bool, Optional[str]]:
        """
        Require specific permission
        
        Args:
            user: User object
            resource: Resource name
            action: Action type
            scope: Permission scope
            roles_db: Roles database
            permissions_db: Permissions database
            
        Returns:
            Tuple of (authorized, error_message)
        """
        check = PermissionCheck(
            user_id=user.id,
            resource=resource,
            action=action,
            scope=scope
        )
        
        users_db = {user.id: user}
        
        has_perm, reason = self.rbac.check_permission(
            check, users_db, roles_db, permissions_db
        )
        
        if not has_perm:
            self.logger.warning(
                f"Permission denied for user {user.username}: {reason}"
            )
        
        return has_perm, reason
    
    def is_admin(self, user: User, roles_db: Dict[str, Role]) -> bool:
        """Check if user is admin"""
        admin_roles = ["ROLE-SUPER-ADMIN", "ROLE-ORG-OWNER", "ROLE-ORG-ADMIN"]
        return any(role_id in admin_roles for role_id in user.roles)
    
    def is_safety_manager(self, user: User) -> bool:
        """Check if user is safety manager"""
        return "ROLE-SAFETY-MGR" in user.roles
    
    def can_view_resource(
        self,
        user: User,
        resource: str,
        roles_db: Dict[str, Role],
        permissions_db: Dict[str, Permission]
    ) -> bool:
        """Check if user can view resource"""
        has_perm, _ = self.require_permission(
            user, resource, PermissionAction.READ,
            PermissionScope.ORGANIZATION, roles_db, permissions_db
        )
        return has_perm
    
    def can_edit_resource(
        self,
        user: User,
        resource: str,
        roles_db: Dict[str, Role],
        permissions_db: Dict[str, Permission]
    ) -> bool:
        """Check if user can edit resource"""
        has_perm, _ = self.require_permission(
            user, resource, PermissionAction.UPDATE,
            PermissionScope.ORGANIZATION, roles_db, permissions_db
        )
        return has_perm


# Singleton instance
_rbac_manager: Optional[RBACManager] = None


def get_rbac_manager() -> RBACManager:
    """Get singleton RBACManager instance"""
    global _rbac_manager
    
    if _rbac_manager is None:
        _rbac_manager = RBACManager()
    
    return _rbac_manager
