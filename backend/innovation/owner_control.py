"""
Owner Control Center - مركز التحكم المطلق للمالك
لوحة التحكم العليا لإدارة النظام بالكامل
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from .organization_graph import (
    organization_graph, Node, Role, Permission, 
    AuthorityLevel, RiskLevel
)


class OwnerControlCenter:
    """مركز التحكم الخاص بالمالك"""
    
    def __init__(self):
        self.audit_log: List[Dict] = []
        self.system_settings: Dict = {
            "ai_authority_level": "high",  # low, medium, high, supreme
            "auto_stop_enabled": True,
            "override_requires_reason": True,
            "multi_tenant_enabled": False,
            "data_retention_days": 365
        }
    
    def create_role(self, owner_id: str, role_data: Dict) -> tuple[bool, str]:
        """إنشاء دور جديد"""
        # التحقق من صلاحية المالك
        if not self._verify_owner(owner_id):
            return False, "Unauthorized: Only owner can create roles"
        
        try:
            role = Role(
                role_id=role_data["id"],
                name=role_data["name"],
                base_authority=AuthorityLevel[role_data["authority"]]
            )
            
            # إضافة الصلاحيات
            for perm in role_data.get("permissions", []):
                role.add_permission(Permission[perm])
            
            # إضافة القواعد الديناميكية
            for rule in role_data.get("dynamic_rules", []):
                role.add_dynamic_rule(rule)
            
            organization_graph.add_role(role)
            
            self._log_action(owner_id, "create_role", {
                "role_id": role.id,
                "role_name": role.name
            })
            
            return True, f"Role '{role.name}' created successfully"
        
        except Exception as e:
            return False, f"Failed to create role: {str(e)}"
    
    def modify_role(self, owner_id: str, role_id: str, modifications: Dict) -> tuple[bool, str]:
        """تعديل دور موجود"""
        if not self._verify_owner(owner_id):
            return False, "Unauthorized"
        
        if role_id not in organization_graph.roles:
            return False, f"Role '{role_id}' not found"
        
        role = organization_graph.roles[role_id]
        
        try:
            # تعديل الصلاحيات
            if "add_permissions" in modifications:
                for perm in modifications["add_permissions"]:
                    role.add_permission(Permission[perm])
            
            if "remove_permissions" in modifications:
                for perm in modifications["remove_permissions"]:
                    role.permissions.discard(Permission[perm])
            
            # تعديل القواعد الديناميكية
            if "dynamic_rules" in modifications:
                role.dynamic_rules = modifications["dynamic_rules"]
            
            self._log_action(owner_id, "modify_role", {
                "role_id": role_id,
                "modifications": modifications
            })
            
            return True, f"Role '{role_id}' modified successfully"
        
        except Exception as e:
            return False, f"Failed to modify role: {str(e)}"
    
    def delete_role(self, owner_id: str, role_id: str) -> tuple[bool, str]:
        """حذف دور"""
        if not self._verify_owner(owner_id):
            return False, "Unauthorized"
        
        # منع حذف دور Owner
        if role_id == "owner":
            return False, "Cannot delete owner role"
        
        if role_id not in organization_graph.roles:
            return False, f"Role '{role_id}' not found"
        
        # التحقق من عدم وجود مستخدمين بهذا الدور
        users_with_role = [
            n for n in organization_graph.nodes.values()
            if n.type == "person" and n.metadata.get("role_id") == role_id
        ]
        
        if users_with_role:
            return False, f"Cannot delete role: {len(users_with_role)} users still assigned"
        
        del organization_graph.roles[role_id]
        
        self._log_action(owner_id, "delete_role", {"role_id": role_id})
        
        return True, f"Role '{role_id}' deleted successfully"
    
    def set_constitutional_rule(self, owner_id: str, rule: Dict) -> tuple[bool, str]:
        """إضافة قاعدة دستورية"""
        if not self._verify_owner(owner_id):
            return False, "Unauthorized: Only owner can modify constitution"
        
        try:
            organization_graph.constitution.add_rule(rule, owner_id)
            
            self._log_action(owner_id, "add_constitutional_rule", {
                "rule": rule
            })
            
            return True, "Constitutional rule added successfully"
        
        except Exception as e:
            return False, f"Failed to add rule: {str(e)}"
    
    def configure_ai_authority(self, owner_id: str, level: str, settings: Dict) -> tuple[bool, str]:
        """تكوين مستوى سلطة الذكاء الاصطناعي"""
        if not self._verify_owner(owner_id):
            return False, "Unauthorized"
        
        valid_levels = ["low", "medium", "high", "supreme"]
        if level not in valid_levels:
            return False, f"Invalid level. Must be one of: {valid_levels}"
        
        self.system_settings["ai_authority_level"] = level
        self.system_settings.update(settings)
        
        self._log_action(owner_id, "configure_ai_authority", {
            "level": level,
            "settings": settings
        })
        
        return True, f"AI authority configured to '{level}'"
    
    def override_ai_decision(self, owner_id: str, decision_id: str, reason: str) -> tuple[bool, str]:
        """تجاوز قرار الذكاء الاصطناعي"""
        if not self._verify_owner(owner_id):
            return False, "Unauthorized"
        
        if self.system_settings["override_requires_reason"] and not reason:
            return False, "Override reason required"
        
        self._log_action(owner_id, "override_ai_decision", {
            "decision_id": decision_id,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        
        return True, "AI decision overridden"
    
    def create_person(self, owner_id: str, person_data: Dict) -> tuple[bool, str]:
        """إنشاء شخص في النظام"""
        if not self._verify_owner(owner_id):
            return False, "Unauthorized"
        
        try:
            person = Node(
                node_id=person_data["id"],
                node_type="person",
                name=person_data["name"],
                metadata={
                    "role_id": person_data.get("role_id"),
                    "contact": person_data.get("contact", {}),
                    "department": person_data.get("department"),
                    "employee_id": person_data.get("employee_id")
                }
            )
            
            # إضافة العلاقات
            if "manages_locations" in person_data:
                for loc in person_data["manages_locations"]:
                    person.add_relationship("manages_location", loc)
            
            organization_graph.add_node(person)
            
            self._log_action(owner_id, "create_person", {
                "person_id": person.id,
                "name": person.name
            })
            
            return True, f"Person '{person.name}' created successfully"
        
        except Exception as e:
            return False, f"Failed to create person: {str(e)}"
    
    def assign_role(self, owner_id: str, person_id: str, role_id: str) -> tuple[bool, str]:
        """تعيين دور لشخص"""
        if not self._verify_owner(owner_id):
            return False, "Unauthorized"
        
        if person_id not in organization_graph.nodes:
            return False, f"Person '{person_id}' not found"
        
        if role_id not in organization_graph.roles:
            return False, f"Role '{role_id}' not found"
        
        person = organization_graph.nodes[person_id]
        old_role = person.metadata.get("role_id")
        person.metadata["role_id"] = role_id
        
        self._log_action(owner_id, "assign_role", {
            "person_id": person_id,
            "old_role": old_role,
            "new_role": role_id
        })
        
        return True, f"Role '{role_id}' assigned to '{person.name}'"
    
    def get_audit_log(self, owner_id: str, filters: Dict = None) -> List[Dict]:
        """الحصول على سجل المراجعة"""
        if not self._verify_owner(owner_id):
            return []
        
        logs = self.audit_log
        
        # تطبيق الفلاتر
        if filters:
            if "action_type" in filters:
                logs = [l for l in logs if l["action"] == filters["action_type"]]
            if "start_date" in filters:
                start = datetime.fromisoformat(filters["start_date"])
                logs = [l for l in logs if datetime.fromisoformat(l["timestamp"]) >= start]
        
        return logs
    
    def get_system_overview(self, owner_id: str) -> Dict:
        """نظرة عامة على النظام"""
        if not self._verify_owner(owner_id):
            return {}
        
        # إحصائيات
        persons = [n for n in organization_graph.nodes.values() if n.type == "person"]
        locations = [n for n in organization_graph.nodes.values() if n.type == "location"]
        projects = [n for n in organization_graph.nodes.values() if n.type == "project"]
        
        # توزيع الأدوار
        role_distribution = {}
        for person in persons:
            role_id = person.metadata.get("role_id", "unassigned")
            role_distribution[role_id] = role_distribution.get(role_id, 0) + 1
        
        return {
            "statistics": {
                "total_persons": len(persons),
                "total_locations": len(locations),
                "total_projects": len(projects),
                "total_roles": len(organization_graph.roles),
                "constitutional_rules": len(organization_graph.constitution.rules)
            },
            "role_distribution": role_distribution,
            "system_settings": self.system_settings,
            "recent_actions": self.audit_log[-10:] if self.audit_log else []
        }
    
    def _verify_owner(self, owner_id: str) -> bool:
        """التحقق من أن الشخص هو المالك"""
        if owner_id not in organization_graph.nodes:
            return False
        
        person = organization_graph.nodes[owner_id]
        role_id = person.metadata.get("role_id")
        
        return role_id == "owner"
    
    def _log_action(self, owner_id: str, action: str, details: Dict):
        """تسجيل إجراء في سجل المراجعة"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "owner_id": owner_id,
            "action": action,
            "details": details
        }
        self.audit_log.append(log_entry)


# نموذج عالمي
owner_control = OwnerControlCenter()
