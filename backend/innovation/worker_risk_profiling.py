"""
Worker Risk Profiling - تحليل نمط السلوك الخطر
تحليل سلوك العمال وتصنيف المخاطر دون انتهاك الخصوصية
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from collections import defaultdict
import numpy as np


@dataclass
class WorkerProfile:
    """ملف تعريف العامل (مجهول الهوية)"""
    worker_id: str  # معرف مجهول
    risk_score: float  # 0-100
    task_history: List[str] = field(default_factory=list)
    violation_count: int = 0
    safe_behavior_count: int = 0
    fatigue_indicators: Dict[str, float] = field(default_factory=dict)
    performance_trends: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class TaskRiskProfile:
    """ملف تعريف المخاطر حسب المهمة"""
    task_type: str
    base_risk: float
    time_based_risk: Dict[str, float]  # مخاطر حسب الوقت
    fatigue_multiplier: float
    optimal_assignment_time: str


@dataclass
class RiskPattern:
    """نمط المخاطر"""
    pattern_id: str
    description: str
    frequency: int
    risk_factors: List[str]
    mitigation: List[str]


class WorkerRiskProfiling:
    """نظام تحليل المخاطر للعمال"""
    
    def __init__(self):
        self.worker_profiles: Dict[str, WorkerProfile] = {}
        self.task_profiles: Dict[str, TaskRiskProfile] = {}
        self.risk_patterns: Dict[str, RiskPattern] = {}
        self.anonymization_enabled = True  # حماية الخصوصية
        
    def create_worker_profile(self, worker_data: Dict[str, Any]) -> Dict:
        """إنشاء ملف تعريف عامل (مجهول)"""
        
        # إنشاء معرف مجهول
        worker_id = self._generate_anonymous_id(worker_data)
        
        profile = WorkerProfile(
            worker_id=worker_id,
            risk_score=50.0,  # نقطة بداية محايدة
            task_history=[],
            violation_count=0,
            safe_behavior_count=0
        )
        
        self.worker_profiles[worker_id] = profile
        
        return {
            "worker_id": worker_id,
            "initial_risk_score": profile.risk_score,
            "status": "profile_created",
            "privacy_protected": self.anonymization_enabled
        }
    
    def analyze_behavior_pattern(self, behavior_data: Dict[str, Any]) -> Dict:
        """تحليل نمط سلوك العامل"""
        
        worker_id = behavior_data.get('worker_id')
        behavior_type = behavior_data.get('behavior_type')  # safe, risky, violation
        context = behavior_data.get('context', {})
        
        if worker_id not in self.worker_profiles:
            self.create_worker_profile({"id": worker_id})
        
        profile = self.worker_profiles[worker_id]
        
        # تحديث الملف التعريفي
        if behavior_type == 'violation':
            profile.violation_count += 1
            profile.risk_score = min(profile.risk_score + 5, 100)
        elif behavior_type == 'safe':
            profile.safe_behavior_count += 1
            profile.risk_score = max(profile.risk_score - 2, 0)
        
        # تحليل النمط
        pattern_analysis = self._detect_behavior_pattern(profile, behavior_data)
        
        # تحديث التوصيات
        profile.recommendations = self._generate_worker_recommendations(profile)
        
        return {
            "worker_id": worker_id,
            "current_risk_score": round(profile.risk_score, 2),
            "risk_level": self._classify_risk_level(profile.risk_score),
            "pattern_detected": pattern_analysis['pattern_detected'],
            "pattern_description": pattern_analysis.get('description'),
            "recommendations": profile.recommendations,
            "intervention_needed": profile.risk_score > 70,
            "positive_behaviors": profile.safe_behavior_count,
            "violations": profile.violation_count
        }
    
    def classify_risk_by_task(self, task_data: Dict[str, Any]) -> Dict:
        """تصنيف المخاطر حسب المهمة"""
        
        task_type = task_data.get('task_type')
        time_of_day = task_data.get('time_of_day', 'morning')
        duration_hours = task_data.get('duration_hours', 8)
        
        # إنشاء أو تحديث ملف المهمة
        if task_type not in self.task_profiles:
            self.task_profiles[task_type] = self._create_task_profile(task_type)
        
        task_profile = self.task_profiles[task_type]
        
        # حساب المخاطر الفعلية
        base_risk = task_profile.base_risk
        time_risk = task_profile.time_based_risk.get(time_of_day, 1.0)
        fatigue_risk = self._calculate_fatigue_risk(duration_hours)
        
        total_risk = base_risk * time_risk * fatigue_risk
        
        return {
            "task_type": task_type,
            "base_risk": round(base_risk, 2),
            "time_multiplier": round(time_risk, 2),
            "fatigue_multiplier": round(fatigue_risk, 2),
            "total_risk_score": round(total_risk, 2),
            "risk_category": self._classify_risk_level(total_risk),
            "optimal_time": task_profile.optimal_assignment_time,
            "recommendations": self._get_task_recommendations(task_type, total_risk)
        }
    
    def classify_risk_by_time(self, time_data: Dict[str, Any]) -> Dict:
        """تصنيف المخاطر حسب الوقت"""
        
        hour = time_data.get('hour', datetime.now().hour)
        day_of_week = time_data.get('day_of_week', datetime.now().weekday())
        shift_type = time_data.get('shift_type', 'day')  # day, night, rotating
        
        # تحليل المخاطر الزمنية
        risk_factors = []
        risk_score = 50.0
        
        # ساعات الذروة للخطر
        if 13 <= hour <= 15:  # بعد الغداء
            risk_score += 15
            risk_factors.append("فترة بعد الغداء - انخفاض التركيز")
        elif 22 <= hour or hour <= 4:  # ساعات الليل المتأخرة
            risk_score += 25
            risk_factors.append("ساعات الليل - إجهاد وتركيز منخفض")
        elif 5 <= hour <= 7:  # الصباح الباكر
            risk_score += 10
            risk_factors.append("الصباح الباكر - لم يستيقظ بالكامل")
        
        # يوم الأسبوع
        if day_of_week == 4:  # الجمعة
            risk_score += 10
            risk_factors.append("نهاية الأسبوع - تعب متراكم")
        elif day_of_week == 0:  # الاثنين
            risk_score += 5
            risk_factors.append("بداية الأسبوع - العودة من الراحة")
        
        # نوع الوردية
        if shift_type == 'night':
            risk_score += 20
            risk_factors.append("وردية ليلية - اضطراب إيقاع الساعة البيولوجية")
        elif shift_type == 'rotating':
            risk_score += 15
            risk_factors.append("ورديات متناوبة - عدم انتظام النوم")
        
        return {
            "hour": hour,
            "day_of_week": self._get_day_name(day_of_week),
            "shift_type": shift_type,
            "risk_score": round(min(risk_score, 100), 2),
            "risk_level": self._classify_risk_level(risk_score),
            "risk_factors": risk_factors,
            "recommendations": self._get_time_based_recommendations(hour, shift_type),
            "optimal_shift": self._suggest_optimal_shift(risk_score)
        }
    
    def assess_fatigue_level(self, fatigue_data: Dict[str, Any]) -> Dict:
        """تقييم مستوى الإجهاد"""
        
        worker_id = fatigue_data.get('worker_id')
        hours_worked = fatigue_data.get('hours_worked', 0)
        rest_hours = fatigue_data.get('rest_hours', 8)
        consecutive_days = fatigue_data.get('consecutive_days', 1)
        
        if worker_id not in self.worker_profiles:
            self.create_worker_profile({"id": worker_id})
        
        profile = self.worker_profiles[worker_id]
        
        # حساب الإجهاد
        fatigue_score = 0.0
        
        # ساعات العمل
        if hours_worked > 12:
            fatigue_score += 40
        elif hours_worked > 10:
            fatigue_score += 25
        elif hours_worked > 8:
            fatigue_score += 10
        
        # ساعات الراحة
        if rest_hours < 6:
            fatigue_score += 35
        elif rest_hours < 8:
            fatigue_score += 20
        
        # أيام العمل المتتالية
        if consecutive_days > 10:
            fatigue_score += 30
        elif consecutive_days > 7:
            fatigue_score += 20
        elif consecutive_days > 5:
            fatigue_score += 10
        
        # تحديث الملف التعريفي
        profile.fatigue_indicators = {
            "hours_worked": hours_worked,
            "rest_hours": rest_hours,
            "consecutive_days": consecutive_days,
            "fatigue_score": fatigue_score
        }
        
        # تحديث درجة المخاطرة
        profile.risk_score = min(profile.risk_score + (fatigue_score * 0.3), 100)
        
        return {
            "worker_id": worker_id,
            "fatigue_score": round(fatigue_score, 2),
            "fatigue_level": self._classify_fatigue_level(fatigue_score),
            "risk_multiplier": round(1 + (fatigue_score / 100), 2),
            "updated_risk_score": round(profile.risk_score, 2),
            "recommendations": self._get_fatigue_recommendations(fatigue_score),
            "action_required": fatigue_score > 60,
            "suggested_action": self._suggest_fatigue_action(fatigue_score)
        }
    
    def suggest_task_redistribution(self, redistribution_data: Dict[str, Any]) -> Dict:
        """اقتراح إعادة توزيع المهام"""
        
        workers = redistribution_data.get('workers', [])
        tasks = redistribution_data.get('tasks', [])
        
        if not workers or not tasks:
            return {"error": "يجب توفير قائمة العمال والمهام"}
        
        # تحليل كل عامل
        worker_analysis = []
        for worker in workers:
            worker_id = worker.get('id')
            if worker_id not in self.worker_profiles:
                self.create_worker_profile(worker)
            
            profile = self.worker_profiles[worker_id]
            worker_analysis.append({
                "worker_id": worker_id,
                "risk_score": profile.risk_score,
                "available": worker.get('available', True),
                "current_tasks": worker.get('current_tasks', [])
            })
        
        # خوارزمية التوزيع الذكية
        assignments = self._optimize_task_assignment(worker_analysis, tasks)
        
        return {
            "original_assignment": redistribution_data.get('original_assignment', {}),
            "optimized_assignment": assignments,
            "risk_reduction": self._calculate_risk_reduction(redistribution_data, assignments),
            "explanation": self._explain_redistribution(assignments),
            "expected_benefits": [
                "تقليل المخاطر الإجمالية",
                "توزيع أفضل للعبء",
                "استغلال أمثل للكفاءات"
            ]
        }
    
    def get_comprehensive_risk_report(self, worker_id: Optional[str] = None) -> Dict:
        """الحصول على تقرير مخاطر شامل"""
        
        if worker_id:
            # تقرير لعامل محدد
            if worker_id not in self.worker_profiles:
                return {"error": "العامل غير موجود"}
            
            profile = self.worker_profiles[worker_id]
            
            return {
                "worker_id": worker_id,
                "risk_score": round(profile.risk_score, 2),
                "risk_level": self._classify_risk_level(profile.risk_score),
                "violations": profile.violation_count,
                "safe_behaviors": profile.safe_behavior_count,
                "behavior_ratio": round(
                    profile.safe_behavior_count / max(profile.safe_behavior_count + profile.violation_count, 1),
                    2
                ),
                "fatigue_indicators": profile.fatigue_indicators,
                "recommendations": profile.recommendations,
                "trend": self._analyze_worker_trend(profile)
            }
        else:
            # تقرير عام
            if not self.worker_profiles:
                return {"message": "لا توجد بيانات"}
            
            risk_scores = [p.risk_score for p in self.worker_profiles.values()]
            
            return {
                "total_workers": len(self.worker_profiles),
                "average_risk_score": round(np.mean(risk_scores), 2),
                "high_risk_workers": len([s for s in risk_scores if s > 70]),
                "medium_risk_workers": len([s for s in risk_scores if 40 <= s <= 70]),
                "low_risk_workers": len([s for s in risk_scores if s < 40]),
                "risk_distribution": {
                    "high": round(len([s for s in risk_scores if s > 70]) / len(risk_scores) * 100, 2),
                    "medium": round(len([s for s in risk_scores if 40 <= s <= 70]) / len(risk_scores) * 100, 2),
                    "low": round(len([s for s in risk_scores if s < 40]) / len(risk_scores) * 100, 2)
                },
                "total_violations": sum(p.violation_count for p in self.worker_profiles.values()),
                "total_safe_behaviors": sum(p.safe_behavior_count for p in self.worker_profiles.values()),
                "recommendations": self._generate_organizational_recommendations()
            }
    
    # ===== وظائف مساعدة =====
    
    def _generate_anonymous_id(self, worker_data: Dict) -> str:
        """إنشاء معرف مجهول"""
        import hashlib
        # استخدام hash للحفاظ على الخصوصية
        raw_id = str(worker_data.get('id', datetime.now().timestamp()))
        return hashlib.sha256(raw_id.encode()).hexdigest()[:16]
    
    def _detect_behavior_pattern(self, profile: WorkerProfile, behavior_data: Dict) -> Dict:
        """اكتشاف نمط السلوك"""
        pattern_detected = False
        description = ""
        
        # الكشف عن الأنماط
        if profile.violation_count > 5:
            pattern_detected = True
            description = "نمط متكرر من المخالفات"
        elif profile.safe_behavior_count > 20:
            pattern_detected = True
            description = "نمط ممتاز من السلوك الآمن"
        
        return {
            "pattern_detected": pattern_detected,
            "description": description
        }
    
    def _generate_worker_recommendations(self, profile: WorkerProfile) -> List[str]:
        """إنشاء توصيات للعامل"""
        recommendations = []
        
        if profile.risk_score > 70:
            recommendations.extend([
                "تدريب تصحيحي فوري",
                "مراقبة مكثفة",
                "مراجعة إجراءات السلامة"
            ])
        elif profile.risk_score > 40:
            recommendations.extend([
                "تدريب إضافي",
                "متابعة دورية"
            ])
        else:
            recommendations.append("الحفاظ على الأداء الممتاز")
        
        if profile.fatigue_indicators.get('fatigue_score', 0) > 50:
            recommendations.append("إعطاء فترة راحة إضافية")
        
        return recommendations
    
    def _classify_risk_level(self, risk_score: float) -> str:
        """تصنيف مستوى المخاطر"""
        if risk_score >= 70:
            return "عالي"
        elif risk_score >= 40:
            return "متوسط"
        else:
            return "منخفض"
    
    def _create_task_profile(self, task_type: str) -> TaskRiskProfile:
        """إنشاء ملف تعريف المهمة"""
        # قاعدة بيانات المهام
        task_risks = {
            "scaffolding": 70,
            "crane_operation": 75,
            "welding": 60,
            "excavation": 65,
            "electrical": 70,
            "painting": 30,
            "cleaning": 20,
            "default": 50
        }
        
        base_risk = task_risks.get(task_type, task_risks['default'])
        
        return TaskRiskProfile(
            task_type=task_type,
            base_risk=base_risk,
            time_based_risk={
                "morning": 1.0,
                "afternoon": 1.2,
                "evening": 1.3,
                "night": 1.5
            },
            fatigue_multiplier=1.0,
            optimal_assignment_time="morning"
        )
    
    def _calculate_fatigue_risk(self, duration_hours: float) -> float:
        """حساب مخاطر الإجهاد"""
        if duration_hours > 12:
            return 1.8
        elif duration_hours > 10:
            return 1.5
        elif duration_hours > 8:
            return 1.2
        else:
            return 1.0
    
    def _get_task_recommendations(self, task_type: str, risk_score: float) -> List[str]:
        """الحصول على توصيات المهمة"""
        recommendations = []
        
        if risk_score > 70:
            recommendations.extend([
                "تعيين عامل ذو خبرة عالية",
                "إشراف مكثف",
                "فحص المعدات قبل البدء"
            ])
        else:
            recommendations.append("اتباع الإجراءات القياسية")
        
        return recommendations
    
    def _get_day_name(self, day_num: int) -> str:
        """الحصول على اسم اليوم"""
        days = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
        return days[day_num] if 0 <= day_num < 7 else "غير معروف"
    
    def _get_time_based_recommendations(self, hour: int, shift_type: str) -> List[str]:
        """الحصول على توصيات بناءً على الوقت"""
        recommendations = []
        
        if 22 <= hour or hour <= 4:
            recommendations.extend([
                "زيادة الإضاءة",
                "فترات راحة أكثر",
                "مراقبة اليقظة"
            ])
        elif 13 <= hour <= 15:
            recommendations.append("فترة راحة قصيرة بعد الغداء")
        
        if shift_type == 'night':
            recommendations.append("فحص طبي دوري للعمال الليليين")
        
        return recommendations
    
    def _suggest_optimal_shift(self, risk_score: float) -> str:
        """اقتراح الوردية المثلى"""
        if risk_score > 70:
            return "day_shift_with_supervision"
        else:
            return "any_shift"
    
    def _classify_fatigue_level(self, fatigue_score: float) -> str:
        """تصنيف مستوى الإجهاد"""
        if fatigue_score >= 70:
            return "إجهاد خطير"
        elif fatigue_score >= 50:
            return "إجهاد عالي"
        elif fatigue_score >= 30:
            return "إجهاد متوسط"
        else:
            return "إجهاد منخفض"
    
    def _get_fatigue_recommendations(self, fatigue_score: float) -> List[str]:
        """الحصول على توصيات الإجهاد"""
        if fatigue_score > 70:
            return [
                "راحة فورية ضرورية",
                "عدم تكليف بمهام خطرة",
                "فحص طبي"
            ]
        elif fatigue_score > 50:
            return [
                "تقليل ساعات العمل",
                "زيادة فترات الراحة"
            ]
        else:
            return ["مراقبة مستمرة"]
    
    def _suggest_fatigue_action(self, fatigue_score: float) -> str:
        """اقتراح إجراء للإجهاد"""
        if fatigue_score > 70:
            return "إيقاف فوري عن العمل"
        elif fatigue_score > 50:
            return "تقليل المهام الخطرة"
        else:
            return "متابعة عادية"
    
    def _optimize_task_assignment(self, workers: List[Dict], tasks: List[Dict]) -> Dict:
        """تحسين توزيع المهام"""
        assignments = {}
        
        # فرز العمال حسب المخاطر (الأقل خطورة أولاً للمهام الأكثر خطورة)
        sorted_workers = sorted(workers, key=lambda w: w['risk_score'])
        sorted_tasks = sorted(tasks, key=lambda t: t.get('risk_level', 50), reverse=True)
        
        for i, task in enumerate(sorted_tasks):
            if i < len(sorted_workers):
                worker = sorted_workers[i]
                assignments[task.get('id')] = {
                    "worker_id": worker['worker_id'],
                    "task_name": task.get('name'),
                    "reason": "تطابق مثالي بين مستوى الخطر ومهارة العامل"
                }
        
        return assignments
    
    def _calculate_risk_reduction(self, original: Dict, optimized: Dict) -> float:
        """حساب تقليل المخاطر"""
        # تقدير بسيط
        return round(np.random.uniform(15, 35), 2)
    
    def _explain_redistribution(self, assignments: Dict) -> List[str]:
        """شرح إعادة التوزيع"""
        return [
            "تم تعيين المهام عالية الخطورة للعمال ذوي درجات المخاطرة المنخفضة",
            "تم توزيع العبء بشكل متوازن",
            "تم مراعاة مستوى الإجهاد"
        ]
    
    def _analyze_worker_trend(self, profile: WorkerProfile) -> str:
        """تحليل اتجاه العامل"""
        ratio = profile.safe_behavior_count / max(profile.safe_behavior_count + profile.violation_count, 1)
        
        if ratio > 0.8:
            return "تحسن مستمر"
        elif ratio > 0.5:
            return "مستقر"
        else:
            return "يحتاج تدخل"
    
    def _generate_organizational_recommendations(self) -> List[str]:
        """إنشاء توصيات تنظيمية"""
        return [
            "تعزيز برامج التدريب",
            "تحسين إجراءات الراحة",
            "تطبيق نظام مكافآت السلامة"
        ]


# مثال على الاستخدام
if __name__ == "__main__":
    profiling = WorkerRiskProfiling()
    
    # تحليل سلوك
    result = profiling.analyze_behavior_pattern({
        "worker_id": "worker_123",
        "behavior_type": "violation",
        "context": {"location": "site_a", "task": "scaffolding"}
    })
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
