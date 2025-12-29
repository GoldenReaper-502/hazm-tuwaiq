"""
AI Safety Brain - العقل المركزي للسلامة
نظام ذكاء مركزي يتعلم من جميع الأحداث ويبني ذاكرة مؤسسية
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import numpy as np


@dataclass
class IncidentMemory:
    """ذاكرة حادث"""
    id: str
    timestamp: datetime
    incident_type: str
    location: str
    severity: float
    root_causes: List[str]
    consequences: List[str]
    lessons_learned: List[str]
    prevention_measures: List[str]


@dataclass
class NearMiss:
    """حادث كاد أن يقع"""
    id: str
    timestamp: datetime
    description: str
    potential_severity: float
    prevented_by: List[str]
    insights: List[str]


@dataclass
class BehaviorPattern:
    """نمط سلوكي"""
    pattern_id: str
    description: str
    risk_level: float
    frequency: int
    contexts: List[str]
    recommendations: List[str]


class AISafetyBrain:
    """العقل المركزي للسلامة"""
    
    def __init__(self):
        self.incident_memory: List[IncidentMemory] = []
        self.near_misses: List[NearMiss] = []
        self.behavior_patterns: Dict[str, BehaviorPattern] = {}
        self.organizational_memory = {
            "total_incidents": 0,
            "total_near_misses": 0,
            "patterns_identified": 0,
            "lives_saved": 0,
            "cost_prevented": 0
        }
        self.learning_insights = []
        self.project_knowledge = defaultdict(dict)
        
    def learn_from_incident(self, incident_data: Dict[str, Any]) -> Dict:
        """التعلم من حادث"""
        
        # إنشاء ذاكرة الحادث
        incident = IncidentMemory(
            id=incident_data.get('id', f"inc_{datetime.now().timestamp()}"),
            timestamp=datetime.fromisoformat(incident_data.get('timestamp', datetime.now().isoformat())),
            incident_type=incident_data.get('type'),
            location=incident_data.get('location'),
            severity=incident_data.get('severity', 5.0),
            root_causes=incident_data.get('root_causes', []),
            consequences=incident_data.get('consequences', []),
            lessons_learned=[],
            prevention_measures=[]
        )
        
        # تحليل الحادث باستخدام الذكاء الاصطناعي
        analysis = self._analyze_incident(incident)
        
        # استخلاص الدروس
        incident.lessons_learned = self._extract_lessons(incident, analysis)
        incident.prevention_measures = self._generate_preventions(incident, analysis)
        
        # حفظ في الذاكرة
        self.incident_memory.append(incident)
        self.organizational_memory["total_incidents"] += 1
        
        # البحث عن أنماط مشابهة
        similar_incidents = self._find_similar_incidents(incident)
        
        # تحديث المعرفة المؤسسية
        self._update_organizational_knowledge(incident)
        
        return {
            "incident_id": incident.id,
            "lessons_learned": incident.lessons_learned,
            "prevention_measures": incident.prevention_measures,
            "similar_incidents_count": len(similar_incidents),
            "similar_incidents": similar_incidents[:5],  # أول 5
            "pattern_detected": len(similar_incidents) >= 3,
            "recommendations": self._generate_smart_recommendations(incident, similar_incidents),
            "organizational_impact": self._assess_organizational_impact(incident)
        }
    
    def learn_from_near_miss(self, near_miss_data: Dict[str, Any]) -> Dict:
        """التعلم من حادث كاد أن يقع"""
        
        near_miss = NearMiss(
            id=near_miss_data.get('id', f"nm_{datetime.now().timestamp()}"),
            timestamp=datetime.fromisoformat(near_miss_data.get('timestamp', datetime.now().isoformat())),
            description=near_miss_data.get('description'),
            potential_severity=near_miss_data.get('potential_severity', 7.0),
            prevented_by=near_miss_data.get('prevented_by', []),
            insights=[]
        )
        
        # تحليل ما الذي منع وقوع الحادث
        prevention_analysis = self._analyze_prevention_success(near_miss)
        
        near_miss.insights = prevention_analysis['insights']
        
        self.near_misses.append(near_miss)
        self.organizational_memory["total_near_misses"] += 1
        self.organizational_memory["lives_saved"] += int(near_miss.potential_severity / 2)
        
        return {
            "near_miss_id": near_miss.id,
            "insights": near_miss.insights,
            "success_factors": prevention_analysis['success_factors'],
            "replication_guide": prevention_analysis['replication_guide'],
            "value": f"منع حادث محتمل بشدة {near_miss.potential_severity}/10"
        }
    
    def learn_from_behavior(self, behavior_data: Dict[str, Any]) -> Dict:
        """التعلم من سلوك العمال"""
        
        behavior_type = behavior_data.get('behavior_type')
        risk_level = behavior_data.get('risk_level', 0)
        context = behavior_data.get('context', 'unknown')
        
        # البحث عن نمط موجود أو إنشاء جديد
        pattern_key = f"{behavior_type}_{context}"
        
        if pattern_key in self.behavior_patterns:
            # تحديث النمط الموجود
            pattern = self.behavior_patterns[pattern_key]
            pattern.frequency += 1
            pattern.risk_level = (pattern.risk_level + risk_level) / 2  # متوسط متحرك
        else:
            # إنشاء نمط جديد
            pattern = BehaviorPattern(
                pattern_id=pattern_key,
                description=behavior_data.get('description', ''),
                risk_level=risk_level,
                frequency=1,
                contexts=[context],
                recommendations=self._generate_behavior_recommendations(behavior_type, risk_level)
            )
            self.behavior_patterns[pattern_key] = pattern
            self.organizational_memory["patterns_identified"] += 1
        
        # تحليل الاتجاه
        trend = self._analyze_behavior_trend(pattern)
        
        return {
            "pattern_id": pattern.pattern_id,
            "frequency": pattern.frequency,
            "risk_level": round(pattern.risk_level, 2),
            "trend": trend,
            "is_concerning": pattern.risk_level > 60 and pattern.frequency > 10,
            "recommendations": pattern.recommendations,
            "intervention_needed": self._assess_intervention_need(pattern)
        }
    
    def build_organizational_memory(self) -> Dict:
        """بناء الذاكرة المؤسسية"""
        
        if not self.incident_memory and not self.near_misses:
            return {
                "status": "insufficient_data",
                "message": "لا توجد بيانات كافية لبناء الذاكرة المؤسسية"
            }
        
        # تحليل شامل
        memory = {
            "total_learning_events": len(self.incident_memory) + len(self.near_misses),
            "incidents_analyzed": len(self.incident_memory),
            "near_misses_captured": len(self.near_misses),
            "patterns_identified": len(self.behavior_patterns),
            "lives_saved": self.organizational_memory["lives_saved"],
            
            # أكثر الأنواع شيوعاً
            "most_common_incident_types": self._get_most_common_incidents(),
            
            # أكثر الأسباب الجذرية
            "top_root_causes": self._get_top_root_causes(),
            
            # أكثر الإجراءات الوقائية فعالية
            "most_effective_preventions": self._get_effective_preventions(),
            
            # الدروس الرئيسية
            "key_lessons": self._compile_key_lessons(),
            
            # توصيات استراتيجية
            "strategic_recommendations": self._generate_strategic_recommendations(),
            
            # مقاييس الأداء
            "performance_metrics": self._calculate_performance_metrics(),
            
            # التحسن مع الوقت
            "improvement_over_time": self._track_improvement()
        }
        
        return memory
    
    def apply_learning_to_new_project(self, project_config: Dict) -> Dict:
        """تطبيق التعلم على مشروع جديد"""
        
        project_type = project_config.get('type')
        project_location = project_config.get('location')
        project_scale = project_config.get('scale')
        
        # البحث عن مشاريع مشابهة
        similar_projects = self._find_similar_projects(project_config)
        
        # استخراج الدروس المطبقة
        applicable_lessons = []
        for incident in self.incident_memory:
            if self._is_relevant_to_project(incident, project_config):
                applicable_lessons.extend(incident.lessons_learned)
        
        # بناء خطة سلامة ذكية
        safety_plan = self._generate_smart_safety_plan(project_config, applicable_lessons)
        
        # التنبؤ بالمخاطر المحتملة
        predicted_risks = self._predict_project_risks(project_config)
        
        # حفظ في ذاكرة المشروع
        project_id = project_config.get('id', f"proj_{datetime.now().timestamp()}")
        self.project_knowledge[project_id] = {
            "config": project_config,
            "safety_plan": safety_plan,
            "predicted_risks": predicted_risks,
            "start_date": datetime.now().isoformat()
        }
        
        return {
            "project_id": project_id,
            "similar_projects_analyzed": len(similar_projects),
            "lessons_applied": len(set(applicable_lessons)),
            "safety_plan": safety_plan,
            "predicted_risks": predicted_risks,
            "expected_safety_improvement": self._estimate_safety_improvement(
                project_config, applicable_lessons
            ),
            "message": "كل مشروع جديد يبدأ أكثر أمانًا من السابق 🎯"
        }
    
    def get_cross_project_insights(self) -> Dict:
        """الحصول على رؤى عبر المشاريع"""
        
        if len(self.project_knowledge) < 2:
            return {
                "status": "insufficient_projects",
                "message": "يجب وجود مشروعين على الأقل للمقارنة"
            }
        
        insights = {
            "total_projects": len(self.project_knowledge),
            "common_success_factors": self._identify_success_factors(),
            "common_failure_points": self._identify_failure_points(),
            "best_practices": self._extract_best_practices(),
            "risk_patterns_across_projects": self._analyze_cross_project_risks(),
            "recommendations_for_future": self._generate_future_recommendations()
        }
        
        return insights
    
    # ===== وظائف مساعدة =====
    
    def _analyze_incident(self, incident: IncidentMemory) -> Dict:
        """تحليل الحادث"""
        return {
            "severity_category": "critical" if incident.severity > 7 else "moderate" if incident.severity > 4 else "minor",
            "preventability": 0.8,  # تقدير
            "similar_count": len(self._find_similar_incidents(incident))
        }
    
    def _extract_lessons(self, incident: IncidentMemory, analysis: Dict) -> List[str]:
        """استخلاص الدروس"""
        lessons = []
        
        # دروس من الأسباب الجذرية
        for cause in incident.root_causes:
            if "تدريب" in cause or "training" in cause.lower():
                lessons.append("أهمية التدريب المستمر والشامل")
            if "معدات" in cause or "equipment" in cause.lower():
                lessons.append("ضرورة الصيانة الدورية للمعدات")
            if "إجراء" in cause or "procedure" in cause.lower():
                lessons.append("أهمية اتباع الإجراءات الموحدة")
        
        # دروس عامة
        if incident.severity > 7:
            lessons.append("الحوادث الخطيرة يمكن منعها بالإجراءات الاستباقية")
        
        return lessons if lessons else ["تحتاج المزيد من البيانات لاستخلاص الدروس"]
    
    def _generate_preventions(self, incident: IncidentMemory, analysis: Dict) -> List[str]:
        """إنشاء إجراءات وقائية"""
        preventions = []
        
        # بناءً على نوع الحادث
        incident_type_lower = incident.incident_type.lower()
        
        if "سقوط" in incident.incident_type or "fall" in incident_type_lower:
            preventions.extend([
                "تركيب حواجز سلامة",
                "فحص معدات الحماية يومياً",
                "تدريب السلامة على المرتفعات"
            ])
        elif "حريق" in incident.incident_type or "fire" in incident_type_lower:
            preventions.extend([
                "فحص أنظمة الإنذار",
                "تدريب الإخلاء الدوري",
                "تحديث خطط الطوارئ"
            ])
        else:
            preventions.extend([
                "مراجعة شاملة للإجراءات",
                "تعزيز التدريب",
                "زيادة التفتيش"
            ])
        
        return preventions
    
    def _find_similar_incidents(self, incident: IncidentMemory) -> List[Dict]:
        """البحث عن حوادث مشابهة"""
        similar = []
        
        for past_incident in self.incident_memory:
            if past_incident.id == incident.id:
                continue
            
            # مقارنة بناءً على النوع والموقع
            similarity_score = 0
            if past_incident.incident_type == incident.incident_type:
                similarity_score += 50
            if past_incident.location == incident.location:
                similarity_score += 30
            if abs(past_incident.severity - incident.severity) < 2:
                similarity_score += 20
            
            if similarity_score >= 50:
                similar.append({
                    "id": past_incident.id,
                    "type": past_incident.incident_type,
                    "date": past_incident.timestamp.isoformat(),
                    "similarity": similarity_score
                })
        
        return sorted(similar, key=lambda x: x['similarity'], reverse=True)
    
    def _generate_smart_recommendations(self, incident: IncidentMemory, similar: List[Dict]) -> List[str]:
        """إنشاء توصيات ذكية"""
        recommendations = []
        
        if len(similar) >= 3:
            recommendations.append("⚠️ نمط متكرر مكتشف - يتطلب إجراءات عاجلة")
            recommendations.append("مراجعة شاملة لإجراءات السلامة في هذا المجال")
        
        recommendations.extend(incident.prevention_measures[:3])
        
        return recommendations
    
    def _assess_organizational_impact(self, incident: IncidentMemory) -> Dict:
        """تقييم التأثير المؤسسي"""
        return {
            "safety_culture_impact": "high" if incident.severity > 7 else "medium",
            "learning_value": "high" if len(incident.lessons_learned) > 3 else "medium",
            "prevention_priority": "urgent" if incident.severity > 8 else "normal"
        }
    
    def _analyze_prevention_success(self, near_miss: NearMiss) -> Dict:
        """تحليل نجاح الوقاية"""
        return {
            "insights": [
                f"العامل الحاسم: {factor}" for factor in near_miss.prevented_by
            ],
            "success_factors": near_miss.prevented_by,
            "replication_guide": [
                f"تطبيق {factor} في جميع المواقع المشابهة" 
                for factor in near_miss.prevented_by
            ]
        }
    
    def _generate_behavior_recommendations(self, behavior_type: str, risk_level: float) -> List[str]:
        """إنشاء توصيات سلوكية"""
        recommendations = []
        
        if risk_level > 70:
            recommendations.append("تدخل فوري مطلوب")
            recommendations.append("تدريب تصحيحي")
        elif risk_level > 40:
            recommendations.append("مراقبة وتوجيه")
            recommendations.append("تذكير بالإجراءات")
        else:
            recommendations.append("استمرار المراقبة")
        
        return recommendations
    
    def _analyze_behavior_trend(self, pattern: BehaviorPattern) -> str:
        """تحليل اتجاه السلوك"""
        if pattern.frequency > 20:
            return "متزايد بشكل مقلق"
        elif pattern.frequency > 10:
            return "متزايد"
        else:
            return "مستقر"
    
    def _assess_intervention_need(self, pattern: BehaviorPattern) -> bool:
        """تقييم الحاجة للتدخل"""
        return pattern.risk_level > 60 and pattern.frequency > 10
    
    def _get_most_common_incidents(self) -> List[Dict]:
        """الحصول على أكثر الحوادث شيوعاً"""
        incident_types = defaultdict(int)
        for incident in self.incident_memory:
            incident_types[incident.incident_type] += 1
        
        return [
            {"type": itype, "count": count}
            for itype, count in sorted(incident_types.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
    
    def _get_top_root_causes(self) -> List[Dict]:
        """الحصول على أكثر الأسباب الجذرية"""
        causes = defaultdict(int)
        for incident in self.incident_memory:
            for cause in incident.root_causes:
                causes[cause] += 1
        
        return [
            {"cause": cause, "frequency": freq}
            for cause, freq in sorted(causes.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
    
    def _get_effective_preventions(self) -> List[str]:
        """الحصول على الإجراءات الوقائية الأكثر فعالية"""
        # بناءً على Near Misses
        effective = defaultdict(int)
        for nm in self.near_misses:
            for prevention in nm.prevented_by:
                effective[prevention] += 1
        
        return [
            f"{prev} (منع {count} حادث محتمل)"
            for prev, count in sorted(effective.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
    
    def _compile_key_lessons(self) -> List[str]:
        """تجميع الدروس الرئيسية"""
        all_lessons = []
        for incident in self.incident_memory:
            all_lessons.extend(incident.lessons_learned)
        
        # إزالة المكرر والحصول على الأكثر شيوعاً
        lesson_counts = defaultdict(int)
        for lesson in all_lessons:
            lesson_counts[lesson] += 1
        
        return [
            lesson for lesson, count in sorted(lesson_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
    
    def _generate_strategic_recommendations(self) -> List[str]:
        """إنشاء توصيات استراتيجية"""
        recommendations = [
            "التركيز على الوقاية بدلاً من رد الفعل",
            "بناء ثقافة السلامة من خلال التعلم المستمر",
            "الاستثمار في التدريب والتكنولوجيا"
        ]
        
        # إضافة توصيات بناءً على البيانات
        if self.organizational_memory["total_near_misses"] > self.organizational_memory["total_incidents"] * 2:
            recommendations.append("✓ ثقافة الإبلاغ ممتازة - استمروا")
        else:
            recommendations.append("تشجيع الإبلاغ عن الحوادث التي كادت أن تقع")
        
        return recommendations
    
    def _calculate_performance_metrics(self) -> Dict:
        """حساب مقاييس الأداء"""
        total_events = len(self.incident_memory) + len(self.near_misses)
        
        return {
            "near_miss_to_incident_ratio": round(
                len(self.near_misses) / len(self.incident_memory), 2
            ) if self.incident_memory else 0,
            "learning_rate": round(total_events / max(len(self.project_knowledge), 1), 2),
            "pattern_detection_rate": round(
                len(self.behavior_patterns) / max(total_events, 1) * 100, 2
            )
        }
    
    def _track_improvement(self) -> Dict:
        """تتبع التحسن"""
        if len(self.incident_memory) < 10:
            return {"status": "insufficient_data"}
        
        # تقسيم إلى فترتين
        mid_point = len(self.incident_memory) // 2
        old_incidents = self.incident_memory[:mid_point]
        recent_incidents = self.incident_memory[mid_point:]
        
        old_avg_severity = np.mean([inc.severity for inc in old_incidents])
        recent_avg_severity = np.mean([inc.severity for inc in recent_incidents])
        
        improvement = old_avg_severity - recent_avg_severity
        
        return {
            "old_average_severity": round(old_avg_severity, 2),
            "recent_average_severity": round(recent_avg_severity, 2),
            "improvement": round(improvement, 2),
            "improvement_percent": round(improvement / old_avg_severity * 100, 2) if old_avg_severity > 0 else 0,
            "trend": "تحسن" if improvement > 0 else "ثابت" if improvement == 0 else "تدهور"
        }
    
    def _find_similar_projects(self, project_config: Dict) -> List[Dict]:
        """البحث عن مشاريع مشابهة"""
        similar = []
        project_type = project_config.get('type')
        
        for proj_id, proj_data in self.project_knowledge.items():
            if proj_data['config'].get('type') == project_type:
                similar.append({
                    "project_id": proj_id,
                    "type": project_type
                })
        
        return similar
    
    def _is_relevant_to_project(self, incident: IncidentMemory, project_config: Dict) -> bool:
        """التحقق من صلة الحادث بالمشروع"""
        # بسيط: التحقق من التشابه في النوع
        return True  # في التطبيق الفعلي، سيكون أكثر تعقيداً
    
    def _generate_smart_safety_plan(self, project_config: Dict, lessons: List[str]) -> Dict:
        """إنشاء خطة سلامة ذكية"""
        return {
            "preventive_measures": list(set(lessons))[:10],
            "inspection_schedule": "يومي",
            "training_requirements": ["تدريب السلامة الأساسي", "تدريب خاص بالمعدات"],
            "emergency_procedures": ["إخلاء", "إسعافات أولية", "إخماد حريق"]
        }
    
    def _predict_project_risks(self, project_config: Dict) -> List[Dict]:
        """التنبؤ بمخاطر المشروع"""
        risks = []
        
        # بناءً على الحوادث السابقة
        incident_types = defaultdict(int)
        for incident in self.incident_memory:
            incident_types[incident.incident_type] += 1
        
        for itype, count in sorted(incident_types.items(), key=lambda x: x[1], reverse=True)[:5]:
            risks.append({
                "risk_type": itype,
                "probability": min(count / len(self.incident_memory) * 100, 90),
                "historical_occurrences": count
            })
        
        return risks
    
    def _estimate_safety_improvement(self, project_config: Dict, lessons: List[str]) -> str:
        """تقدير التحسن في السلامة"""
        improvement_percent = len(set(lessons)) * 5  # تقدير
        return f"{min(improvement_percent, 80)}% تحسن متوقع"
    
    def _identify_success_factors(self) -> List[str]:
        """تحديد عوامل النجاح"""
        return [
            "التدريب المستمر",
            "التفتيش الدوري",
            "ثقافة الإبلاغ المفتوحة",
            "التكنولوجيا الحديثة"
        ]
    
    def _identify_failure_points(self) -> List[str]:
        """تحديد نقاط الفشل"""
        return [
            "نقص التدريب",
            "إهمال الصيانة",
            "عدم اتباع الإجراءات"
        ]
    
    def _extract_best_practices(self) -> List[str]:
        """استخراج أفضل الممارسات"""
        return [
            "التخطيط الدقيق قبل البدء",
            "المراقبة المستمرة",
            "التعلم من الحوادث السابقة",
            "تمكين العمال من الإبلاغ"
        ]
    
    def _analyze_cross_project_risks(self) -> Dict:
        """تحليل المخاطر عبر المشاريع"""
        return {
            "common_risks": ["السقوط", "المعدات", "الحريق"],
            "emerging_risks": ["الإجهاد", "سوء التواصل"]
        }
    
    def _generate_future_recommendations(self) -> List[str]:
        """إنشاء توصيات للمستقبل"""
        return [
            "الاستثمار في التكنولوجيا الذكية",
            "بناء ثقافة السلامة القوية",
            "التدريب المستمر والمتطور"
        ]


# مثال على الاستخدام
if __name__ == "__main__":
    brain = AISafetyBrain()
    
    # التعلم من حادث
    incident_result = brain.learn_from_incident({
        "type": "سقوط من ارتفاع",
        "location": "الطابق الثالث",
        "severity": 8.5,
        "root_causes": ["عدم استخدام معدات الحماية", "نقص التدريب"],
        "consequences": ["إصابة خطيرة", "توقف العمل"]
    })
    
    print(json.dumps(incident_result, indent=2, ensure_ascii=False))
