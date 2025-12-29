"""
Advanced Detection Systems - أنظمة الكشف المتقدمة
كشف السلوكيات الدقيقة، التوتر، والأنماط الخطرة
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from enum import Enum


class BehaviorAnomaly(Enum):
    """أنواع الشذوذ السلوكي"""
    HESITATION = "hesitation"                   # التردد
    ABNORMAL_MOVEMENT = "abnormal_movement"     # حركة غير طبيعية
    FATIGUE_SIGNS = "fatigue_signs"             # علامات التعب
    STRESS_INDICATORS = "stress_indicators"     # مؤشرات التوتر
    REPETITIVE_ERROR = "repetitive_error"       # خطأ متكرر
    UNSAFE_PATTERN = "unsafe_pattern"           # نمط غير آمن


class MicroBehaviorDetector:
    """كاشف السلوكيات الدقيقة"""
    
    def __init__(self):
        self.behavior_history: Dict[str, List[Dict]] = {}
        self.anomaly_patterns: Dict[str, Dict] = self._load_patterns()
    
    def _load_patterns(self) -> Dict:
        """تحميل أنماط الشذوذ المعروفة"""
        return {
            "hesitation": {
                "indicators": ["slow_movement", "repeated_starts", "pause_before_action"],
                "threshold": 3,
                "risk_weight": 0.6
            },
            "abnormal_movement": {
                "indicators": ["jerky_motion", "imbalance", "stumbling"],
                "threshold": 2,
                "risk_weight": 0.8
            },
            "fatigue_signs": {
                "indicators": ["slow_response", "reduced_coordination", "head_nodding"],
                "threshold": 2,
                "risk_weight": 0.7
            },
            "stress_indicators": {
                "indicators": ["rapid_movement", "erratic_behavior", "agitation"],
                "threshold": 2,
                "risk_weight": 0.65
            },
            "repetitive_error": {
                "indicators": ["same_mistake", "pattern_violation"],
                "threshold": 2,
                "risk_weight": 0.85
            }
        }
    
    def analyze_behavior(self, worker_id: str, video_data: Dict, context: Dict) -> Dict:
        """تحليل سلوك عامل من الفيديو"""
        # استخراج المؤشرات من بيانات الفيديو
        indicators = self._extract_indicators(video_data)
        
        # الكشف عن الأنماط الشاذة
        anomalies = self._detect_anomalies(worker_id, indicators, context)
        
        # حساب درجة الخطر
        risk_score = self._calculate_behavior_risk(anomalies)
        
        # حفظ في السجل
        self._log_behavior(worker_id, {
            "timestamp": datetime.now().isoformat(),
            "indicators": indicators,
            "anomalies": anomalies,
            "risk_score": risk_score,
            "context": context
        })
        
        return {
            "worker_id": worker_id,
            "timestamp": datetime.now().isoformat(),
            "detected_anomalies": anomalies,
            "risk_score": risk_score,
            "recommendation": self._get_recommendation(risk_score, anomalies),
            "alert_level": self._get_alert_level(risk_score)
        }
    
    def _extract_indicators(self, video_data: Dict) -> List[str]:
        """استخراج المؤشرات من بيانات الفيديو"""
        indicators = []
        
        # تحليل الحركة
        if video_data.get("movement_speed", 1.0) < 0.5:
            indicators.append("slow_movement")
        elif video_data.get("movement_speed", 1.0) > 2.0:
            indicators.append("rapid_movement")
        
        # تحليل الاستقرار
        if video_data.get("stability_score", 1.0) < 0.6:
            indicators.append("imbalance")
        
        # تحليل التردد
        if video_data.get("action_starts", 0) > 2:
            indicators.append("repeated_starts")
        
        # تحليل التوقف
        if video_data.get("pause_duration", 0) > 5:
            indicators.append("pause_before_action")
        
        # تحليل التنسيق
        if video_data.get("coordination_score", 1.0) < 0.7:
            indicators.append("reduced_coordination")
        
        return indicators
    
    def _detect_anomalies(self, worker_id: str, indicators: List[str], context: Dict) -> List[Dict]:
        """الكشف عن الأنماط الشاذة"""
        detected = []
        
        for anomaly_type, pattern in self.anomaly_patterns.items():
            # عد المؤشرات المطابقة
            matches = sum(1 for ind in indicators if ind in pattern["indicators"])
            
            if matches >= pattern["threshold"]:
                detected.append({
                    "type": anomaly_type,
                    "matches": matches,
                    "indicators": [ind for ind in indicators if ind in pattern["indicators"]],
                    "risk_weight": pattern["risk_weight"],
                    "severity": "high" if matches > pattern["threshold"] else "medium"
                })
        
        # التحقق من الأخطاء المتكررة
        repetitive = self._check_repetitive_errors(worker_id, context)
        if repetitive:
            detected.append(repetitive)
        
        return detected
    
    def _check_repetitive_errors(self, worker_id: str, context: Dict) -> Optional[Dict]:
        """التحقق من الأخطاء المتكررة"""
        if worker_id not in self.behavior_history:
            return None
        
        # الحصول على السجل الأخير (آخر ساعة)
        recent = [
            h for h in self.behavior_history[worker_id]
            if datetime.fromisoformat(h["timestamp"]) > datetime.now() - timedelta(hours=1)
        ]
        
        if len(recent) < 2:
            return None
        
        # البحث عن أنماط متكررة
        error_types = [a["type"] for h in recent for a in h.get("anomalies", [])]
        
        # إذا تكرر نفس الخطأ 3 مرات أو أكثر
        from collections import Counter
        counts = Counter(error_types)
        for error, count in counts.items():
            if count >= 3:
                return {
                    "type": "repetitive_error",
                    "error_type": error,
                    "occurrences": count,
                    "risk_weight": 0.85,
                    "severity": "high"
                }
        
        return None
    
    def _calculate_behavior_risk(self, anomalies: List[Dict]) -> float:
        """حساب درجة خطر السلوك"""
        if not anomalies:
            return 0.0
        
        # حساب متوسط مرجح
        total_weight = sum(a["risk_weight"] for a in anomalies)
        count = len(anomalies)
        
        base_risk = total_weight / count
        
        # تضخيم إذا كانت هناك أخطاء متعددة
        if count > 2:
            base_risk *= 1.2
        
        return min(base_risk, 1.0)
    
    def _get_recommendation(self, risk_score: float, anomalies: List[Dict]) -> str:
        """الحصول على توصية"""
        if risk_score > 0.8:
            return "إيقاف العمل فوراً وإجراء تقييم طبي"
        elif risk_score > 0.6:
            return "استراحة إلزامية وإعادة تقييم الحالة"
        elif risk_score > 0.4:
            return "مراقبة مكثفة وتنبيه المشرف"
        else:
            return "متابعة عادية"
    
    def _get_alert_level(self, risk_score: float) -> str:
        """تحديد مستوى التنبيه"""
        if risk_score > 0.8:
            return "critical"
        elif risk_score > 0.6:
            return "high"
        elif risk_score > 0.4:
            return "medium"
        else:
            return "low"
    
    def _log_behavior(self, worker_id: str, data: Dict):
        """تسجيل السلوك"""
        if worker_id not in self.behavior_history:
            self.behavior_history[worker_id] = []
        
        self.behavior_history[worker_id].append(data)
        
        # الاحتفاظ فقط بآخر 100 سجل لكل عامل
        if len(self.behavior_history[worker_id]) > 100:
            self.behavior_history[worker_id] = self.behavior_history[worker_id][-100:]
    
    def get_worker_profile(self, worker_id: str) -> Dict:
        """الحصول على ملف تعريف مخاطر العامل"""
        if worker_id not in self.behavior_history:
            return {"worker_id": worker_id, "profile": "new_worker", "risk_level": "unknown"}
        
        history = self.behavior_history[worker_id]
        
        # حساب الإحصائيات
        total_anomalies = sum(len(h.get("anomalies", [])) for h in history)
        avg_risk = sum(h.get("risk_score", 0) for h in history) / len(history)
        
        # تحديد الأنماط الشائعة
        all_anomalies = [a["type"] for h in history for a in h.get("anomalies", [])]
        from collections import Counter
        common_patterns = Counter(all_anomalies).most_common(3)
        
        # تصنيف المخاطر
        if avg_risk > 0.7:
            risk_level = "high_risk"
        elif avg_risk > 0.4:
            risk_level = "medium_risk"
        else:
            risk_level = "low_risk"
        
        return {
            "worker_id": worker_id,
            "total_observations": len(history),
            "total_anomalies": total_anomalies,
            "average_risk_score": round(avg_risk, 2),
            "risk_level": risk_level,
            "common_patterns": [{"type": p[0], "count": p[1]} for p in common_patterns],
            "last_observation": history[-1]["timestamp"] if history else None
        }


class StressDetector:
    """كاشف التوتر والضغط النفسي"""
    
    def __init__(self):
        self.stress_history: Dict[str, List[Dict]] = {}
    
    def analyze_stress_signals(self, worker_id: str, signals: Dict) -> Dict:
        """تحليل مؤشرات التوتر"""
        stress_score = 0.0
        indicators = []
        
        # تحليل السلوك
        if signals.get("movement_pattern") == "agitated":
            stress_score += 0.3
            indicators.append("حركة مضطربة")
        
        # تحليل سرعة الأداء
        if signals.get("task_speed", 1.0) > 1.5:
            stress_score += 0.2
            indicators.append("سرعة غير عادية في الأداء")
        
        # تحليل الأخطاء
        if signals.get("error_rate", 0) > 0.3:
            stress_score += 0.3
            indicators.append("معدل أخطاء مرتفع")
        
        # تحليل وقت العمل
        work_hours = signals.get("continuous_work_hours", 0)
        if work_hours > 8:
            stress_score += 0.2
            indicators.append(f"عمل متواصل لـ {work_hours} ساعات")
        
        # حفظ في السجل
        self._log_stress(worker_id, {
            "timestamp": datetime.now().isoformat(),
            "stress_score": stress_score,
            "indicators": indicators,
            "signals": signals
        })
        
        return {
            "worker_id": worker_id,
            "stress_score": stress_score,
            "stress_level": self._classify_stress(stress_score),
            "indicators": indicators,
            "recommendation": self._get_stress_recommendation(stress_score),
            "error_probability": self._estimate_error_probability(stress_score)
        }
    
    def _classify_stress(self, score: float) -> str:
        """تصنيف مستوى التوتر"""
        if score > 0.7:
            return "critical"
        elif score > 0.5:
            return "high"
        elif score > 0.3:
            return "moderate"
        else:
            return "normal"
    
    def _get_stress_recommendation(self, score: float) -> str:
        """الحصول على توصية"""
        if score > 0.7:
            return "إيقاف العمل فوراً - راحة إلزامية"
        elif score > 0.5:
            return "استراحة 15-30 دقيقة - إعادة تقييم"
        elif score > 0.3:
            return "مراقبة مستمرة - استراحة قصيرة موصى بها"
        else:
            return "متابعة عادية"
    
    def _estimate_error_probability(self, stress_score: float) -> float:
        """تقدير احتمالية وقوع خطأ"""
        # نموذج بسيط: كلما زاد التوتر زادت احتمالية الخطأ
        base_error = 0.05  # 5% احتمال أساسي
        stress_multiplier = 1 + (stress_score * 3)  # يمكن أن يصل إلى 4x
        
        return min(base_error * stress_multiplier, 0.95)
    
    def _log_stress(self, worker_id: str, data: Dict):
        """تسجيل حالة التوتر"""
        if worker_id not in self.stress_history:
            self.stress_history[worker_id] = []
        
        self.stress_history[worker_id].append(data)
        
        # الاحتفاظ بآخر 50 سجل
        if len(self.stress_history[worker_id]) > 50:
            self.stress_history[worker_id] = self.stress_history[worker_id][-50:]


# نماذج عالمية
micro_behavior_detector = MicroBehaviorDetector()
stress_detector = StressDetector()
