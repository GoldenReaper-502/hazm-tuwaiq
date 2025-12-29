"""
Safety Organization Graph - خارطة السلطة الذكية
نظام متقدم لإدارة الهيكل التنظيمي وعلاقات المخاطر
"""
from typing import Dict, List, Set, Optional, Any
from datetime import datetime, time
from enum import Enum
import json


class RiskLevel(Enum):
    """مستويات الخطر"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuthorityLevel(Enum):
    """مستويات السلطة"""
    VIEWER = "viewer"
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    MANAGER = "manager"
    EXECUTIVE = "executive"
    OWNER = "owner"


class Permission(Enum):
    """الصلاحيات المتاحة"""
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_REPORTS = "view_reports"
    CREATE_ALERTS = "create_alerts"
    ACKNOWLEDGE_ALERTS = "acknowledge_alerts"
    STOP_WORK = "stop_work"
    OVERRIDE_AI = "override_ai"
    APPROVE_REPORTS = "approve_reports"
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    MANAGE_PERMISSIONS = "manage_permissions"
    MODIFY_CONSTITUTION = "modify_constitution"
    FULL_CONTROL = "full_control"


class Node:
    """عقدة في الرسم البياني التنظيمي"""
    def __init__(self, node_id: str, node_type: str, name: str, metadata: Dict = None):
        self.id = node_id
        self.type = node_type  # person, role, location, project
        self.name = name
        self.metadata = metadata or {}
        self.relationships: Dict[str, List[str]] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_relationship(self, rel_type: str, target_id: str):
        """إضافة علاقة"""
        if rel_type not in self.relationships:
            self.relationships[rel_type] = []
        if target_id not in self.relationships[rel_type]:
            self.relationships[rel_type].append(target_id)
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "metadata": self.metadata,
            "relationships": self.relationships,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class Role:
    """دور ديناميكي في النظام"""
    def __init__(self, role_id: str, name: str, base_authority: AuthorityLevel):
        self.id = role_id
        self.name = name
        self.base_authority = base_authority
        self.permissions: Set[Permission] = set()
        self.dynamic_rules: List[Dict] = []  # قواعد تغيير الصلاحيات
        self.created_at = datetime.now()
    
    def add_permission(self, permission: Permission):
        """إضافة صلاحية"""
        self.permissions.add(permission)
    
    def add_dynamic_rule(self, rule: Dict):
        """
        إضافة قاعدة ديناميكية
        مثال: {"condition": "risk_level == CRITICAL", "grant": ["STOP_WORK"], "authority": "EXECUTIVE"}
        """
        self.dynamic_rules.append(rule)
    
    def get_effective_permissions(self, context: Dict) -> Set[Permission]:
        """الحصول على الصلاحيات الفعلية حسب السياق"""
        effective = self.permissions.copy()
        
        # تطبيق القواعد الديناميكية
        for rule in self.dynamic_rules:
            if self._evaluate_condition(rule["condition"], context):
                for perm in rule.get("grant", []):
                    effective.add(Permission[perm])
                for perm in rule.get("revoke", []):
                    effective.discard(Permission[perm])
        
        return effective
    
    def _evaluate_condition(self, condition: str, context: Dict) -> bool:
        """تقييم شرط ديناميكي"""
        try:
            # تقييم بسيط وآمن للشروط
            risk_level = context.get("risk_level", "LOW")
            location = context.get("location", "")
            time_of_day = context.get("time_of_day", 12)
            
            # استبدال المتغيرات في الشرط
            condition = condition.replace("risk_level", f"'{risk_level}'")
            condition = condition.replace("location", f"'{location}'")
            condition = condition.replace("time_of_day", str(time_of_day))
            
            return eval(condition)
        except:
            return False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "base_authority": self.base_authority.value,
            "permissions": [p.value for p in self.permissions],
            "dynamic_rules": self.dynamic_rules,
            "created_at": self.created_at.isoformat()
        }


class SafetyConstitution:
    """دستور السلامة - قواعد عليا غير قابلة للتجاوز"""
    def __init__(self):
        self.rules: List[Dict] = []
        self.created_by: Optional[str] = None
        self.created_at = datetime.now()
        self.version = 1
    
    def add_rule(self, rule: Dict, created_by: str):
        """إضافة قاعدة دستورية"""
        rule["id"] = f"CONST_{len(self.rules) + 1}"
        rule["created_at"] = datetime.now().isoformat()
        rule["created_by"] = created_by
        rule["version"] = self.version
        self.rules.append(rule)
        self.version += 1
    
    def validate_action(self, action: str, context: Dict) -> tuple[bool, Optional[str]]:
        """التحقق من صحة إجراء ضد الدستور"""
        for rule in self.rules:
            if not rule.get("active", True):
                continue
            
            # التحقق من القاعدة
            if rule["type"] == "mandatory":
                if not self._check_mandatory(rule, context):
                    return False, rule.get("violation_message", "Constitutional violation")
            
            elif rule["type"] == "forbidden":
                if self._check_forbidden(rule, action, context):
                    return False, rule.get("violation_message", "Forbidden action")
        
        return True, None
    
    def _check_mandatory(self, rule: Dict, context: Dict) -> bool:
        """التحقق من قاعدة إلزامية"""
        requirement = rule.get("requirement", "")
        
        # مثال: PPE إلزامي
        if requirement == "ppe_required":
            return context.get("ppe_detected", False)
        
        # مثال: تصريح عمل مطلوب
        if requirement == "permit_required":
            return context.get("has_permit", False)
        
        return True
    
    def _check_forbidden(self, rule: Dict, action: str, context: Dict) -> bool:
        """التحقق من قاعدة محظورة"""
        forbidden = rule.get("forbidden_action", "")
        
        # التحقق من مطابقة الإجراء المحظور
        if action == forbidden:
            # التحقق من الشروط
            conditions = rule.get("conditions", {})
            for key, value in conditions.items():
                if context.get(key) != value:
                    return False
            return True
        
        return False
    
    def to_dict(self) -> Dict:
        return {
            "rules": self.rules,
            "version": self.version,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat()
        }


class OrganizationGraph:
    """الرسم البياني التنظيمي الذكي"""
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.roles: Dict[str, Role] = {}
        self.constitution = SafetyConstitution()
        self._init_default_roles()
    
    def _init_default_roles(self):
        """تهيئة الأدوار الافتراضية"""
        # Owner - السلطة المطلقة
        owner = Role("owner", "Owner", AuthorityLevel.OWNER)
        owner.permissions = set(Permission)  # جميع الصلاحيات
        self.roles["owner"] = owner
        
        # Executive
        executive = Role("executive", "Executive", AuthorityLevel.EXECUTIVE)
        executive.add_permission(Permission.VIEW_DASHBOARD)
        executive.add_permission(Permission.VIEW_REPORTS)
        executive.add_permission(Permission.APPROVE_REPORTS)
        executive.add_permission(Permission.OVERRIDE_AI)
        self.roles["executive"] = executive
        
        # Manager
        manager = Role("manager", "Manager", AuthorityLevel.MANAGER)
        manager.add_permission(Permission.VIEW_DASHBOARD)
        manager.add_permission(Permission.VIEW_REPORTS)
        manager.add_permission(Permission.CREATE_ALERTS)
        manager.add_permission(Permission.STOP_WORK)
        # قاعدة ديناميكية: صلاحية OVERRIDE_AI عند خطر CRITICAL
        manager.add_dynamic_rule({
            "condition": "risk_level == 'CRITICAL'",
            "grant": ["OVERRIDE_AI"]
        })
        self.roles["manager"] = manager
        
        # Supervisor
        supervisor = Role("supervisor", "Supervisor", AuthorityLevel.SUPERVISOR)
        supervisor.add_permission(Permission.VIEW_DASHBOARD)
        supervisor.add_permission(Permission.CREATE_ALERTS)
        supervisor.add_permission(Permission.ACKNOWLEDGE_ALERTS)
        supervisor.add_dynamic_rule({
            "condition": "risk_level == 'HIGH' or risk_level == 'CRITICAL'",
            "grant": ["STOP_WORK"]
        })
        self.roles["supervisor"] = supervisor
    
    def add_node(self, node: Node):
        """إضافة عقدة"""
        self.nodes[node.id] = node
    
    def add_role(self, role: Role):
        """إضافة دور"""
        self.roles[role.id] = role
    
    def find_responsible_persons(self, incident_location: str, risk_level: RiskLevel) -> List[Dict]:
        """
        إيجاد المسؤولين عن موقع حادث
        يعيد قائمة مرتبة حسب السلطة
        """
        responsible = []
        
        for node_id, node in self.nodes.items():
            if node.type != "person":
                continue
            
            # التحقق من العلاقات
            if "manages_location" in node.relationships:
                if incident_location in node.relationships["manages_location"]:
                    # الحصول على الدور
                    role_id = node.metadata.get("role_id")
                    if role_id and role_id in self.roles:
                        role = self.roles[role_id]
                        responsible.append({
                            "person_id": node.id,
                            "name": node.name,
                            "role": role.name,
                            "authority": role.base_authority.value,
                            "contact": node.metadata.get("contact", {})
                        })
        
        # ترتيب حسب مستوى السلطة
        authority_order = {
            "owner": 6,
            "executive": 5,
            "manager": 4,
            "supervisor": 3,
            "operator": 2,
            "viewer": 1
        }
        responsible.sort(key=lambda x: authority_order.get(x["authority"], 0), reverse=True)
        
        return responsible
    
    def get_alert_chain(self, location: str, risk_level: RiskLevel) -> List[str]:
        """
        الحصول على سلسلة التنبيهات حسب مستوى الخطر
        يعيد قائمة بمعرفات الأشخاص المطلوب تنبيههم
        """
        chain = []
        responsible = self.find_responsible_persons(location, risk_level)
        
        # مستوى الخطر يحدد مدى السلسلة
        if risk_level == RiskLevel.CRITICAL:
            # تنبيه الجميع
            chain = [p["person_id"] for p in responsible]
        elif risk_level == RiskLevel.HIGH:
            # تنبيه حتى المديرين
            chain = [p["person_id"] for p in responsible 
                    if p["authority"] in ["owner", "executive", "manager", "supervisor"]]
        elif risk_level == RiskLevel.MEDIUM:
            # تنبيه المشرفين والمديرين المباشرين
            chain = [p["person_id"] for p in responsible[:3]]
        else:
            # تنبيه المشرف المباشر فقط
            chain = [p["person_id"] for p in responsible[:1]]
        
        return chain
    
    def check_permission(self, person_id: str, permission: Permission, context: Dict) -> bool:
        """التحقق من صلاحية شخص"""
        # الحصول على العقدة
        if person_id not in self.nodes:
            return False
        
        person = self.nodes[person_id]
        role_id = person.metadata.get("role_id")
        
        if not role_id or role_id not in self.roles:
            return False
        
        role = self.roles[role_id]
        effective_permissions = role.get_effective_permissions(context)
        
        # Owner لديه صلاحيات مطلقة
        if Permission.FULL_CONTROL in effective_permissions:
            return True
        
        return permission in effective_permissions
    
    def validate_action(self, action: str, person_id: str, context: Dict) -> tuple[bool, Optional[str]]:
        """
        التحقق من صحة إجراء
        يتحقق من الدستور والصلاحيات
        """
        # التحقق من الدستور أولاً
        valid, msg = self.constitution.validate_action(action, context)
        if not valid:
            return False, f"Constitutional violation: {msg}"
        
        # التحقق من الصلاحيات
        # تحديد الصلاحية المطلوبة للإجراء
        required_permission = self._get_required_permission(action)
        if required_permission:
            if not self.check_permission(person_id, required_permission, context):
                return False, f"Insufficient permissions for action: {action}"
        
        return True, None
    
    def _get_required_permission(self, action: str) -> Optional[Permission]:
        """تحديد الصلاحية المطلوبة لإجراء معين"""
        action_permission_map = {
            "stop_work": Permission.STOP_WORK,
            "override_ai": Permission.OVERRIDE_AI,
            "approve_report": Permission.APPROVE_REPORTS,
            "create_alert": Permission.CREATE_ALERTS,
            "manage_user": Permission.MANAGE_USERS,
        }
        return action_permission_map.get(action)
    
    def export_graph(self) -> Dict:
        """تصدير الرسم البياني الكامل"""
        return {
            "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
            "roles": {rid: r.to_dict() for rid, r in self.roles.items()},
            "constitution": self.constitution.to_dict()
        }


# نموذج عالمي
organization_graph = OrganizationGraph()
