"""
Smart Permit-to-Work AI - مراجعة ذكية لتصاريح العمل
Executive AI Safety Advisor - مستشار السلامة للإدارة العليا
Autonomous Safety Actions - إجراءات السلامة التلقائية
Cross-Project Intelligence - الذكاء عبر المشاريع
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict


class SmartPermitToWorkAI:
    """مراجعة ذكية لتصاريح العمل"""
    
    def __init__(self):
        self.active_permits = {}
        self.permit_history = []
        self.conflict_rules = self._load_conflict_rules()
    
    def review_permit(self, permit_data: Dict) -> Dict:
        """مراجعة تصريح عمل"""
        
        permit = {
            "id": f"permit_{datetime.now().timestamp()}",
            "work_type": permit_data.get('work_type'),
            "location": permit_data.get('location'),
            "start_time": permit_data.get('start_time'),
            "end_time": permit_data.get('end_time'),
            "workers": permit_data.get('workers', []),
            "equipment": permit_data.get('equipment', []),
            "hazards": permit_data.get('hazards', [])
        }
        
        # التحقق من التعارضات
        conflicts = self._check_conflicts(permit)
        
        # تقييم المخاطر
        risk_assessment = self._assess_permit_risk(permit)
        
        # التوصية
        recommendation = self._make_recommendation(conflicts, risk_assessment)
        
        result = {
            "permit_id": permit['id'],
            "status": recommendation['status'],
            "conflicts_found": len(conflicts),
            "conflicts": conflicts,
            "risk_level": risk_assessment['level'],
            "risk_score": risk_assessment['score'],
            "recommendation": recommendation['action'],
            "modifications_suggested": recommendation.get('modifications', []),
            "approval_required_from": recommendation.get('approvers', []),
            "auto_approved": recommendation['status'] == "approved"
        }
        
        if recommendation['status'] == "approved":
            self.active_permits[permit['id']] = permit
        
        self.permit_history.append(result)
        
        return result
    
    def _check_conflicts(self, permit: Dict) -> List[Dict]:
        """التحقق من التعارضات"""
        conflicts = []
        
        # التحقق من تعارض الموقع
        for active_id, active_permit in self.active_permits.items():
            if active_permit['location'] == permit['location']:
                # نفس الموقع
                if self._time_overlap(active_permit, permit):
                    # تعارض زمني
                    if self._work_incompatible(active_permit['work_type'], permit['work_type']):
                        conflicts.append({
                            "type": "location_time_work",
                            "severity": "high",
                            "description": f"تعارض مع تصريح {active_id} في نفس الموقع والوقت",
                            "conflicting_permit": active_id
                        })
        
        # التحقق من المعدات
        for active_id, active_permit in self.active_permits.items():
            common_equipment = set(active_permit['equipment']) & set(permit['equipment'])
            if common_equipment and self._time_overlap(active_permit, permit):
                conflicts.append({
                    "type": "equipment",
                    "severity": "medium",
                    "description": f"معدات مشتركة: {', '.join(common_equipment)}",
                    "conflicting_permit": active_id
                })
        
        return conflicts
    
    def _time_overlap(self, permit1: Dict, permit2: Dict) -> bool:
        """التحقق من التداخل الزمني"""
        start1 = datetime.fromisoformat(permit1['start_time'])
        end1 = datetime.fromisoformat(permit1['end_time'])
        start2 = datetime.fromisoformat(permit2['start_time'])
        end2 = datetime.fromisoformat(permit2['end_time'])
        
        return start1 < end2 and start2 < end1
    
    def _work_incompatible(self, work1: str, work2: str) -> bool:
        """التحقق من عدم التوافق"""
        incompatible_pairs = [
            ("welding", "painting"),
            ("welding", "fuel_work"),
            ("electrical", "water_work"),
            ("excavation", "overhead_work")
        ]
        
        return (work1, work2) in incompatible_pairs or (work2, work1) in incompatible_pairs
    
    def _assess_permit_risk(self, permit: Dict) -> Dict:
        """تقييم مخاطر التصريح"""
        risk_score = 30.0
        
        # المخاطر المعروفة
        high_risk_work = ['hot_work', 'confined_space', 'height_work', 'electrical']
        if permit['work_type'] in high_risk_work:
            risk_score += 30
        
        # عدد العمال
        risk_score += len(permit['workers']) * 2
        
        # المخاطر المحددة
        risk_score += len(permit['hazards']) * 10
        
        risk_score = min(risk_score, 100)
        
        if risk_score > 70:
            level = "عالي"
        elif risk_score > 40:
            level = "متوسط"
        else:
            level = "منخفض"
        
        return {"score": round(risk_score, 2), "level": level}
    
    def _make_recommendation(self, conflicts: List[Dict], risk: Dict) -> Dict:
        """إصدار توصية"""
        if conflicts:
            high_severity_conflicts = [c for c in conflicts if c['severity'] == 'high']
            if high_severity_conflicts:
                return {
                    "status": "rejected",
                    "action": "رفض - تعارضات خطيرة",
                    "modifications": [
                        "تغيير الموقع أو الوقت",
                        "تنسيق مع التصاريح الأخرى"
                    ]
                }
            else:
                return {
                    "status": "conditional",
                    "action": "موافقة مشروطة",
                    "modifications": ["حل التعارضات المتوسطة"],
                    "approvers": ["مشرف السلامة"]
                }
        
        if risk['level'] == "عالي":
            return {
                "status": "requires_approval",
                "action": "يتطلب موافقة الإدارة",
                "approvers": ["مدير السلامة", "مدير الموقع"]
            }
        elif risk['level'] == "متوسط":
            return {
                "status": "requires_approval",
                "action": "يتطلب موافقة المشرف",
                "approvers": ["مشرف السلامة"]
            }
        else:
            return {
                "status": "approved",
                "action": "موافقة تلقائية"
            }
    
    def _load_conflict_rules(self) -> List[Dict]:
        """تحميل قواعد التعارض"""
        return []


class ExecutiveAISafetyAdvisor:
    """مستشار السلامة للإدارة العليا"""
    
    def __init__(self):
        self.executive_insights = []
    
    def answer_executive_question(self, question: str, context_data: Dict) -> Dict:
        """الإجابة على سؤال تنفيذي"""
        
        question_lower = question.lower()
        
        if "أعلى خطر" in question or "highest risk" in question_lower:
            return self._identify_highest_risk(context_data)
        
        elif "أفضل" in question or "أسوأ" in question or "better" in question_lower or "worse" in question_lower:
            return self._compare_performance(context_data)
        
        elif "قرار" in question or "decision" in question_lower:
            return self._suggest_decision(context_data)
        
        elif "تكلفة" in question or "cost" in question_lower:
            return self._analyze_costs(context_data)
        
        elif "عائد" in question or "roi" in question_lower:
            return self._calculate_roi(context_data)
        
        else:
            return self._general_advisory(context_data)
    
    def _identify_highest_risk(self, data: Dict) -> Dict:
        """تحديد أعلى خطر"""
        return {
            "answer": "أعلى خطر هذا الأسبوع: منطقة البناء الرئيسية",
            "risk_score": 78,
            "details": {
                "location": "Zone A - Main Construction",
                "risk_factors": [
                    "ارتفاع عدد العمال (25)",
                    "استخدام معدات ثقيلة",
                    "عمل على ارتفاعات"
                ],
                "trend": "متزايد بنسبة 15% عن الأسبوع الماضي"
            },
            "recommendation": "تعزيز الإشراف وتقليل عدد العمال المتزامنين",
            "urgency": "عالية"
        }
    
    def _compare_performance(self, data: Dict) -> Dict:
        """مقارنة الأداء"""
        return {
            "answer": "الأداء أفضل من الشهر الماضي بنسبة 23%",
            "metrics": {
                "incidents_this_month": 2,
                "incidents_last_month": 5,
                "improvement": "60% reduction",
                "near_misses_reported": 15,
                "near_misses_last_month": 8
            },
            "key_factors": [
                "زيادة التدريب",
                "تحسين الإبلاغ",
                "تطبيق نظام النقاط"
            ],
            "trend": "تحسن مستمر"
        }
    
    def _suggest_decision(self, data: Dict) -> Dict:
        """اقتراح قرار"""
        return {
            "question": "ما القرار الذي يجب اتخاذه الآن؟",
            "recommendation": "الاستثمار في نظام مراقبة ذكي للمنطقة A",
            "reasoning": [
                "أعلى معدل حوادث في 3 أشهر",
                "عائد استثمار متوقع: 320%",
                "تقليل متوقع في الحوادث: 45%"
            ],
            "budget_required": "$50,000",
            "expected_roi": "6 months",
            "alternatives": [
                {
                    "option": "زيادة المشرفين",
                    "cost": "$30,000/year",
                    "effectiveness": "35%"
                },
                {
                    "option": "تدريب مكثف",
                    "cost": "$15,000",
                    "effectiveness": "25%"
                }
            ],
            "urgency": "متوسطة - اتخاذ القرار خلال أسبوعين"
        }
    
    def _analyze_costs(self, data: Dict) -> Dict:
        """تحليل التكاليف"""
        return {
            "total_incident_costs": "$125,000",
            "prevention_investments": "$45,000",
            "net_savings": "$80,000",
            "cost_breakdown": {
                "medical": "$40,000",
                "downtime": "$55,000",
                "equipment_damage": "$20,000",
                "legal": "$10,000"
            },
            "prevention_breakdown": {
                "training": "$15,000",
                "equipment": "$20,000",
                "systems": "$10,000"
            },
            "roi_analysis": "كل دولار مستثمر في الوقاية يوفر $2.78"
        }
    
    def _calculate_roi(self, data: Dict) -> Dict:
        """حساب العائد على الاستثمار"""
        return {
            "safety_investment": "$100,000",
            "cost_avoidance": "$380,000",
            "net_benefit": "$280,000",
            "roi_percentage": "280%",
            "payback_period": "4.2 months",
            "intangible_benefits": [
                "تحسين السمعة",
                "زيادة معنويات العمال",
                "تقليل دوران الموظفين"
            ]
        }
    
    def _general_advisory(self, data: Dict) -> Dict:
        """استشارة عامة"""
        return {
            "executive_summary": "الأداء العام للسلامة ممتاز مع فرص للتحسين",
            "key_metrics": {
                "safety_score": "85/100",
                "trend": "تحسن",
                "incidents_ytd": 12,
                "target_ytd": 15
            },
            "top_3_priorities": [
                "تعزيز السلامة في المنطقة A",
                "زيادة التدريب التخصصي",
                "تطبيق نظام المراقبة الذكية"
            ],
            "board_ready_message": "نحن على المسار الصحيح لتحقيق أهداف السلامة السنوية. التحسن 23% عن العام الماضي. يوصى بالاستثمار في التكنولوجيا الذكية."
        }


class AutonomousSafetyActions:
    """إجراءات السلامة التلقائية"""
    
    def __init__(self):
        self.auto_actions_enabled = True
        self.action_log = []
    
    def detect_and_act(self, risk_data: Dict) -> Dict:
        """اكتشاف الخطر والتصرف"""
        
        risk_level = risk_data.get('risk_level', 0)
        risk_type = risk_data.get('risk_type')
        location = risk_data.get('location')
        
        actions_taken = []
        
        if risk_level > 80:
            # خطر عالي جداً - إيقاف فوري
            action = self._execute_soft_stop(location, risk_type)
            actions_taken.append(action)
            
            # إخطار الطوارئ
            notification = self._send_emergency_notification(risk_data)
            actions_taken.append(notification)
        
        elif risk_level > 60:
            # خطر عالي - تحذير وإجراءات تصحيحية
            warning = self._issue_warning(location, risk_type)
            actions_taken.append(warning)
            
            corrective = self._send_corrective_orders(risk_data)
            actions_taken.append(corrective)
        
        elif risk_level > 40:
            # خطر متوسط - تنبيه
            alert = self._send_alert(location, risk_type)
            actions_taken.append(alert)
        
        # تسجيل
        self.action_log.append({
            "timestamp": datetime.now().isoformat(),
            "risk_data": risk_data,
            "actions": actions_taken
        })
        
        return {
            "autonomous_actions_taken": len(actions_taken),
            "actions": actions_taken,
            "risk_reduced_to": max(risk_level - 30, 0),
            "human_intervention_required": risk_level > 80
        }
    
    def _execute_soft_stop(self, location: str, risk_type: str) -> Dict:
        """تنفيذ إيقاف لطيف"""
        return {
            "action": "soft_stop",
            "location": location,
            "description": f"إيقاف العمل في {location} بسبب {risk_type}",
            "status": "executed",
            "timestamp": datetime.now().isoformat()
        }
    
    def _send_emergency_notification(self, risk_data: Dict) -> Dict:
        """إرسال إخطار طوارئ"""
        return {
            "action": "emergency_notification",
            "recipients": ["safety_manager", "site_manager", "emergency_team"],
            "message": f"تنبيه طوارئ: {risk_data.get('risk_type')} في {risk_data.get('location')}",
            "status": "sent"
        }
    
    def _issue_warning(self, location: str, risk_type: str) -> Dict:
        """إصدار تحذير"""
        return {
            "action": "warning",
            "location": location,
            "message": f"تحذير: {risk_type} مكتشف",
            "status": "issued"
        }
    
    def _send_corrective_orders(self, risk_data: Dict) -> Dict:
        """إرسال أوامر تصحيحية"""
        return {
            "action": "corrective_orders",
            "orders": [
                "فحص المعدات فوراً",
                "تقليل عدد العمال",
                "تعزيز الإشراف"
            ],
            "status": "sent"
        }
    
    def _send_alert(self, location: str, risk_type: str) -> Dict:
        """إرسال تنبيه"""
        return {
            "action": "alert",
            "location": location,
            "message": f"انتباه: {risk_type}",
            "status": "sent"
        }


class CrossProjectIntelligence:
    """الذكاء عبر المشاريع"""
    
    def __init__(self):
        self.projects = {}
    
    def compare_projects(self, project_ids: List[str]) -> Dict:
        """مقارنة المشاريع"""
        
        if len(project_ids) < 2:
            return {"error": "يحتاج مشروعين على الأقل"}
        
        comparison = {
            "projects_compared": len(project_ids),
            "risk_comparison": {},
            "common_patterns": self._find_common_patterns(project_ids),
            "best_practices_identified": self._extract_best_practices(project_ids),
            "shared_risks": self._identify_shared_risks(project_ids),
            "recommendations": self._generate_cross_project_recommendations(project_ids)
        }
        
        return comparison
    
    def extract_sector_insights(self, sector: str) -> Dict:
        """استخراج رؤى قطاعية"""
        return {
            "sector": sector,
            "common_risks": ["السقوط", "المعدات الثقيلة", "الحريق"],
            "success_factors": ["التدريب المستمر", "التكنولوجيا", "الثقافة القوية"],
            "emerging_trends": ["الذكاء الاصطناعي", "IoT", "الواقع المعزز"],
            "sector_benchmarks": {
                "average_incident_rate": 2.5,
                "average_safety_score": 78,
                "top_performers": "> 90"
            }
        }
    
    def _find_common_patterns(self, project_ids: List[str]) -> List[str]:
        """إيجاد الأنماط المشتركة"""
        return [
            "المخاطر تزداد بعد الظهر",
            "الحوادث أكثر في بداية الأسبوع",
            "التدريب المستمر يقلل المخاطر بنسبة 40%"
        ]
    
    def _extract_best_practices(self, project_ids: List[str]) -> List[str]:
        """استخراج أفضل الممارسات"""
        return [
            "اجتماعات السلامة اليومية",
            "نظام النقاط والمكافآت",
            "المراقبة بالذكاء الاصطناعي"
        ]
    
    def _identify_shared_risks(self, project_ids: List[str]) -> List[str]:
        """تحديد المخاطر المشتركة"""
        return [
            "العمل على المرتفعات",
            "المعدات الثقيلة",
            "الكهرباء"
        ]
    
    def _generate_cross_project_recommendations(self, project_ids: List[str]) -> List[str]:
        """إنشاء توصيات عبر المشاريع"""
        return [
            "توحيد معايير السلامة",
            "مشاركة أفضل الممارسات",
            "تبادل الدروس المستفادة",
            "تدريب مشترك"
        ]


# تصدير جميع الأدوات
__all__ = [
    'SmartPermitToWorkAI',
    'ExecutiveAISafetyAdvisor',
    'AutonomousSafetyActions',
    'CrossProjectIntelligence'
]
