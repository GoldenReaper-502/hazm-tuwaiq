"""
AI Incident Storytelling - تحويل الحوادث إلى قصص تحليلية
Compliance Auto-Auditor - تدقيق تلقائي مستمر
"""
import json
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass


class AIIncidentStorytelling:
    """تحويل الحوادث إلى قصص"""
    
    def create_incident_story(self, incident_data: Dict) -> Dict:
        """إنشاء قصة من حادث"""
        
        # بناء القصة
        story = {
            "title": self._generate_title(incident_data),
            "timeline": self._create_timeline(incident_data),
            "narrative": self._generate_narrative(incident_data),
            "root_cause_analysis": self._analyze_root_causes(incident_data),
            "lessons_learned": self._extract_lessons(incident_data),
            "prevention_guide": self._create_prevention_guide(incident_data),
            "visual_elements": self._suggest_visuals(incident_data),
            "training_points": self._identify_training_points(incident_data)
        }
        
        return story
    
    def _generate_title(self, incident: Dict) -> str:
        """إنشاء عنوان"""
        incident_type = incident.get('type', 'حادث')
        location = incident.get('location', 'موقع العمل')
        return f"{incident_type} في {location} - دراسة حالة"
    
    def _create_timeline(self, incident: Dict) -> List[Dict]:
        """إنشاء تسلسل زمني"""
        return [
            {"time": "08:00", "event": "بداية الوردية", "type": "normal"},
            {"time": "10:30", "event": "بدء المهمة الخطرة", "type": "warning"},
            {"time": "11:15", "event": "وقوع الحادث", "type": "critical"},
            {"time": "11:16", "event": "الاستجابة الأولية", "type": "response"},
            {"time": "11:30", "event": "وصول الإسعاف", "type": "response"}
        ]
    
    def _generate_narrative(self, incident: Dict) -> str:
        """إنشاء سرد"""
        return f"""
في صباح {incident.get('date', 'غير محدد')}, وقع {incident.get('type', 'حادث')} في {incident.get('location', 'موقع العمل')}.

السياق:
كان العمال يقومون بـ {incident.get('activity', 'المهمة المعتادة')} عندما حدث الحادث.

ما حدث:
{incident.get('description', 'تفاصيل الحادث')}

الأسباب الجذرية:
تحليلنا أظهر أن الأسباب الرئيسية كانت:
{', '.join(incident.get('root_causes', ['غير محدد']))}

النتائج:
{incident.get('consequences', 'إصابات وأضرار')}

الدروس المستفادة:
هذا الحادث يعلمنا أهمية {incident.get('key_lesson', 'الالتزام بإجراءات السلامة')}.
"""
    
    def _analyze_root_causes(self, incident: Dict) -> Dict:
        """تحليل الأسباب الجذرية"""
        return {
            "primary_cause": incident.get('root_causes', [])[0] if incident.get('root_causes') else "غير محدد",
            "contributing_factors": incident.get('root_causes', [])[1:] if len(incident.get('root_causes', [])) > 1 else [],
            "why_it_happened": "تحليل متعمق يتطلب المزيد من البيانات",
            "preventability": "95%"
        }
    
    def _extract_lessons(self, incident: Dict) -> List[str]:
        """استخلاص الدروس"""
        return [
            "أهمية اتباع إجراءات السلامة",
            "التدريب المستمر ضروري",
            "الوقاية أفضل من العلاج",
            "ثقافة السلامة مسؤولية الجميع"
        ]
    
    def _create_prevention_guide(self, incident: Dict) -> Dict:
        """إنشاء دليل وقاية"""
        return {
            "immediate_actions": [
                "فحص جميع المعدات المماثلة",
                "تدريب طارئ للعمال",
                "مراجعة الإجراءات"
            ],
            "long_term_measures": [
                "تحديث بروتوكولات السلامة",
                "استثمار في معدات أحدث",
                "بناء ثقافة سلامة أقوى"
            ],
            "monitoring": [
                "تفتيش يومي",
                "تقارير أسبوعية",
                "مراجعة شهرية"
            ]
        }
    
    def _suggest_visuals(self, incident: Dict) -> List[str]:
        """اقتراح عناصر بصرية"""
        return [
            "مخطط الموقع مع تحديد نقطة الحادث",
            "تسلسل زمني تفاعلي",
            "رسم توضيحي للأسباب",
            "صور توضيحية للإجراءات الصحيحة"
        ]
    
    def _identify_training_points(self, incident: Dict) -> List[str]:
        """تحديد نقاط التدريب"""
        return [
            "استخدام معدات الحماية الشخصية",
            "التعرف على المخاطر",
            "إجراءات الطوارئ",
            "الإبلاغ عن المخاطر"
        ]


class ComplianceAutoAuditor:
    """مدقق الامتثال التلقائي"""
    
    def __init__(self):
        self.standards = {
            "ISO45001": self._load_iso45001_requirements(),
            "OSHA": self._load_osha_requirements()
        }
        self.audit_history = []
    
    def conduct_audit(self, site_data: Dict, standard: str = "ISO45001") -> Dict:
        """إجراء تدقيق"""
        
        if standard not in self.standards:
            return {"error": "معيار غير مدعوم"}
        
        requirements = self.standards[standard]
        
        # التدقيق
        audit_results = {
            "audit_id": f"audit_{datetime.now().timestamp()}",
            "standard": standard,
            "date": datetime.now().isoformat(),
            "overall_compliance": 0.0,
            "compliant_items": [],
            "non_compliant_items": [],
            "partial_compliance": [],
            "recommendations": []
        }
        
        total_requirements = len(requirements)
        compliant_count = 0
        
        for requirement in requirements:
            status = self._check_requirement(site_data, requirement)
            
            if status == "compliant":
                audit_results["compliant_items"].append(requirement)
                compliant_count += 1
            elif status == "non_compliant":
                audit_results["non_compliant_items"].append(requirement)
                audit_results["recommendations"].append(
                    f"تحتاج إلى تحسين: {requirement['name']}"
                )
            else:
                audit_results["partial_compliance"].append(requirement)
        
        audit_results["overall_compliance"] = round(
            compliant_count / total_requirements * 100, 2
        ) if total_requirements > 0 else 0
        
        # تصنيف الامتثال
        audit_results["compliance_grade"] = self._grade_compliance(
            audit_results["overall_compliance"]
        )
        
        self.audit_history.append(audit_results)
        
        return audit_results
    
    def detect_drift(self, current_audit: Dict, baseline_audit: Dict) -> Dict:
        """اكتشاف الانحراف"""
        
        current_compliance = current_audit.get('overall_compliance', 0)
        baseline_compliance = baseline_audit.get('overall_compliance', 0)
        
        drift = current_compliance - baseline_compliance
        
        return {
            "drift_detected": abs(drift) > 5,
            "drift_percentage": round(drift, 2),
            "trend": "تحسن" if drift > 0 else "تدهور" if drift < 0 else "ثابت",
            "severity": "عالي" if abs(drift) > 15 else "متوسط" if abs(drift) > 5 else "منخفض",
            "alert_required": abs(drift) > 10,
            "recommendations": self._get_drift_recommendations(drift)
        }
    
    def generate_compliance_report(self, audit_id: str = None) -> Dict:
        """إنشاء تقرير امتثال"""
        
        if audit_id:
            audit = next((a for a in self.audit_history if a['audit_id'] == audit_id), None)
            if not audit:
                return {"error": "التدقيق غير موجود"}
            audits_to_report = [audit]
        else:
            audits_to_report = self.audit_history
        
        if not audits_to_report:
            return {"message": "لا توجد عمليات تدقيق"}
        
        return {
            "total_audits": len(audits_to_report),
            "average_compliance": round(
                sum(a['overall_compliance'] for a in audits_to_report) / len(audits_to_report), 2
            ),
            "trend": self._analyze_compliance_trend(audits_to_report),
            "most_common_issues": self._identify_common_issues(audits_to_report),
            "improvement_areas": self._suggest_improvements(audits_to_report),
            "next_audit_date": self._suggest_next_audit_date(),
            "ready_for_external_review": all(a['overall_compliance'] >= 85 for a in audits_to_report)
        }
    
    def _load_iso45001_requirements(self) -> List[Dict]:
        """تحميل متطلبات ISO 45001"""
        return [
            {"id": "4.1", "name": "فهم المؤسسة وسياقها", "category": "context"},
            {"id": "5.1", "name": "القيادة والالتزام", "category": "leadership"},
            {"id": "6.1", "name": "الإجراءات لمعالجة المخاطر والفرص", "category": "planning"},
            {"id": "7.2", "name": "الكفاءة", "category": "support"},
            {"id": "8.1", "name": "التخطيط والسيطرة التشغيلية", "category": "operation"},
            {"id": "9.1", "name": "المراقبة والقياس والتحليل والتقييم", "category": "evaluation"},
            {"id": "10.1", "name": "عدم المطابقة والإجراء التصحيحي", "category": "improvement"}
        ]
    
    def _load_osha_requirements(self) -> List[Dict]:
        """تحميل متطلبات OSHA"""
        return [
            {"id": "1910.132", "name": "معدات الحماية الشخصية", "category": "ppe"},
            {"id": "1910.146", "name": "الأماكن المحصورة", "category": "confined_space"},
            {"id": "1910.147", "name": "التحكم في الطاقة الخطرة", "category": "lockout_tagout"},
            {"id": "1926.501", "name": "حماية من السقوط", "category": "fall_protection"}
        ]
    
    def _check_requirement(self, site_data: Dict, requirement: Dict) -> str:
        """التحقق من متطلب"""
        # محاكاة بسيطة
        import random
        statuses = ["compliant", "non_compliant", "partial"]
        return random.choice(statuses)
    
    def _grade_compliance(self, compliance_percent: float) -> str:
        """تصنيف الامتثال"""
        if compliance_percent >= 95:
            return "ممتاز A+"
        elif compliance_percent >= 85:
            return "جيد جداً A"
        elif compliance_percent >= 75:
            return "جيد B"
        elif compliance_percent >= 65:
            return "مقبول C"
        else:
            return "يحتاج تحسين D"
    
    def _get_drift_recommendations(self, drift: float) -> List[str]:
        """الحصول على توصيات الانحراف"""
        if drift < -10:
            return [
                "تدقيق فوري مطلوب",
                "مراجعة شاملة للإجراءات",
                "تدريب طارئ"
            ]
        elif drift < 0:
            return ["مراقبة مكثفة", "تحديد نقاط الضعف"]
        else:
            return ["الحفاظ على الأداء الحالي"]
    
    def _analyze_compliance_trend(self, audits: List[Dict]) -> str:
        """تحليل اتجاه الامتثال"""
        if len(audits) < 2:
            return "بيانات غير كافية"
        
        recent = audits[-1]['overall_compliance']
        previous = audits[-2]['overall_compliance']
        
        if recent > previous:
            return "تحسن"
        elif recent < previous:
            return "تدهور"
        else:
            return "ثابت"
    
    def _identify_common_issues(self, audits: List[Dict]) -> List[str]:
        """تحديد المشاكل الشائعة"""
        return [
            "نقص في التدريب",
            "معدات غير محدثة",
            "توثيق ناقص"
        ]
    
    def _suggest_improvements(self, audits: List[Dict]) -> List[str]:
        """اقتراح تحسينات"""
        return [
            "تحديث السياسات",
            "زيادة التدريب",
            "تحسين التوثيق",
            "استثمار في التكنولوجيا"
        ]
    
    def _suggest_next_audit_date(self) -> str:
        """اقتراح موعد التدقيق القادم"""
        next_date = datetime.now() + timedelta(days=90)
        return next_date.isoformat()
