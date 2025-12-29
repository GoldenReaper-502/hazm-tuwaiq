"""
Explainable AI - ذكاء اصطناعي قابل للتفسير والمساءلة
كل قرار يأتي مع سبب واضح وبيانات داعمة
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json


class DecisionType(Enum):
    """أنواع القرارات"""
    RISK_ASSESSMENT = "risk_assessment"
    ALERT_CREATION = "alert_creation"
    WORK_STOP = "work_stop"
    PPE_VIOLATION = "ppe_violation"
    BEHAVIOR_ANOMALY = "behavior_anomaly"
    RECOMMENDATION = "recommendation"


class ConfidenceLevel(Enum):
    """مستويات الثقة"""
    VERY_LOW = "very_low"    # < 40%
    LOW = "low"              # 40-60%
    MEDIUM = "medium"        # 60-80%
    HIGH = "high"            # 80-95%
    VERY_HIGH = "very_high"  # > 95%


class ExplainableDecision:
    """قرار AI قابل للتفسير"""
    
    def __init__(self, decision_type: DecisionType, result: Any):
        self.id = f"DEC_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        self.type = decision_type
        self.result = result
        self.timestamp = datetime.now()
        
        # مكونات التفسير
        self.reasoning: List[str] = []
        self.evidence: List[Dict] = []
        self.confidence: Optional[ConfidenceLevel] = None
        self.alternatives: List[Dict] = []
        self.risk_factors: Dict[str, float] = {}
        self.data_sources: List[str] = []
        self.model_version: Optional[str] = None
        
        # معلومات المساءلة
        self.can_be_overridden: bool = True
        self.override_authority: Optional[str] = None
        self.liability_notes: List[str] = []
    
    def add_reasoning(self, reason: str):
        """إضافة سبب للقرار"""
        self.reasoning.append(reason)
    
    def add_evidence(self, evidence_type: str, data: Any, weight: float = 1.0):
        """إضافة دليل"""
        self.evidence.append({
            "type": evidence_type,
            "data": data,
            "weight": weight,
            "timestamp": datetime.now().isoformat()
        })
    
    def set_confidence(self, confidence: float):
        """تعيين مستوى الثقة"""
        if confidence < 0.4:
            self.confidence = ConfidenceLevel.VERY_LOW
        elif confidence < 0.6:
            self.confidence = ConfidenceLevel.LOW
        elif confidence < 0.8:
            self.confidence = ConfidenceLevel.MEDIUM
        elif confidence < 0.95:
            self.confidence = ConfidenceLevel.HIGH
        else:
            self.confidence = ConfidenceLevel.VERY_HIGH
    
    def add_alternative(self, alternative: str, pros: List[str], cons: List[str], score: float):
        """إضافة بديل للقرار"""
        self.alternatives.append({
            "option": alternative,
            "pros": pros,
            "cons": cons,
            "score": score
        })
    
    def add_risk_factor(self, factor: str, weight: float):
        """إضافة عامل خطر"""
        self.risk_factors[factor] = weight
    
    def add_data_source(self, source: str):
        """إضافة مصدر بيانات"""
        if source not in self.data_sources:
            self.data_sources.append(source)
    
    def add_liability_note(self, note: str):
        """إضافة ملاحظة مسؤولية"""
        self.liability_notes.append(note)
    
    def generate_explanation(self, language: str = "ar") -> Dict:
        """توليد تفسير كامل للقرار"""
        if language == "ar":
            return self._generate_arabic_explanation()
        else:
            return self._generate_english_explanation()
    
    def _generate_arabic_explanation(self) -> Dict:
        """توليد تفسير بالعربية"""
        return {
            "معرف_القرار": self.id,
            "نوع_القرار": self.type.value,
            "النتيجة": self.result,
            "الوقت": self.timestamp.isoformat(),
            "مستوى_الثقة": self.confidence.value if self.confidence else "غير محدد",
            
            "الأسباب": self.reasoning,
            
            "الأدلة": [
                {
                    "النوع": e["type"],
                    "البيانات": e["data"],
                    "الوزن": f"{e['weight']:.2%}"
                }
                for e in self.evidence
            ],
            
            "البدائل_المقترحة": [
                {
                    "الخيار": a["option"],
                    "المزايا": a["pros"],
                    "العيوب": a["cons"],
                    "التقييم": f"{a['score']:.1%}"
                }
                for a in self.alternatives
            ],
            
            "عوامل_الخطر": {
                factor: f"{weight:.2%}"
                for factor, weight in self.risk_factors.items()
            },
            
            "مصادر_البيانات": self.data_sources,
            
            "معلومات_المساءلة": {
                "قابل_للتجاوز": self.can_be_overridden,
                "سلطة_التجاوز": self.override_authority,
                "ملاحظات_المسؤولية": self.liability_notes
            }
        }
    
    def _generate_english_explanation(self) -> Dict:
        """توليد تفسير بالإنجليزية"""
        return {
            "decision_id": self.id,
            "decision_type": self.type.value,
            "result": self.result,
            "timestamp": self.timestamp.isoformat(),
            "confidence_level": self.confidence.value if self.confidence else "undefined",
            "reasoning": self.reasoning,
            "evidence": self.evidence,
            "alternatives": self.alternatives,
            "risk_factors": self.risk_factors,
            "data_sources": self.data_sources,
            "liability_info": {
                "can_be_overridden": self.can_be_overridden,
                "override_authority": self.override_authority,
                "liability_notes": self.liability_notes
            }
        }
    
    def generate_summary(self, language: str = "ar") -> str:
        """توليد ملخص نصي للقرار"""
        if language == "ar":
            summary = f"🤖 قرار AI: {self.type.value}\n"
            summary += f"📊 النتيجة: {self.result}\n"
            summary += f"⏰ الوقت: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if self.confidence:
                summary += f"✨ مستوى الثقة: {self.confidence.value}\n"
            
            summary += "\n📝 الأسباب:\n"
            for i, reason in enumerate(self.reasoning, 1):
                summary += f"  {i}. {reason}\n"
            
            if self.alternatives:
                summary += "\n🔄 البدائل المتاحة:\n"
                for alt in self.alternatives:
                    summary += f"  • {alt['option']} (تقييم: {alt['score']:.0%})\n"
            
            return summary
        
        return str(self.generate_explanation("en"))
    
    def to_dict(self) -> Dict:
        """تحويل إلى قاموس"""
        return {
            "id": self.id,
            "type": self.type.value,
            "result": self.result,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence.value if self.confidence else None,
            "reasoning": self.reasoning,
            "evidence": self.evidence,
            "alternatives": self.alternatives,
            "risk_factors": self.risk_factors,
            "data_sources": self.data_sources,
            "model_version": self.model_version,
            "can_be_overridden": self.can_be_overridden,
            "override_authority": self.override_authority,
            "liability_notes": self.liability_notes
        }


class SafetyLiabilityShield:
    """درع المسؤولية القانونية - حماية من المسائلة القانونية"""
    
    def __init__(self):
        self.liability_log: List[Dict] = []
    
    def log_incident(self, incident_id: str, details: Dict):
        """تسجيل حادث في سجل المسؤولية"""
        entry = {
            "incident_id": incident_id,
            "timestamp": datetime.now().isoformat(),
            "timeline": [],
            "observers": [],
            "actors": [],
            "decisions": [],
            "evidence": []
        }
        
        entry.update(details)
        self.liability_log.append(entry)
    
    def log_observation(self, incident_id: str, observer: Dict, observation: str):
        """تسجيل من رأى الخطر"""
        entry = self._find_incident(incident_id)
        if entry:
            entry["observers"].append({
                "timestamp": datetime.now().isoformat(),
                "observer": observer,
                "observation": observation,
                "action_taken": observer.get("action_taken", "none")
            })
    
    def log_action(self, incident_id: str, actor: Dict, action: str, result: str):
        """تسجيل من اتخذ إجراء"""
        entry = self._find_incident(incident_id)
        if entry:
            entry["actors"].append({
                "timestamp": datetime.now().isoformat(),
                "actor": actor,
                "action": action,
                "result": result
            })
    
    def log_decision(self, incident_id: str, decision: ExplainableDecision):
        """تسجيل قرار AI"""
        entry = self._find_incident(incident_id)
        if entry:
            entry["decisions"].append(decision.to_dict())
    
    def generate_liability_report(self, incident_id: str, language: str = "ar") -> Dict:
        """توليد تقرير مسؤولية قانوني"""
        entry = self._find_incident(incident_id)
        if not entry:
            return {"error": "Incident not found"}
        
        if language == "ar":
            return {
                "معرف_الحادث": incident_id,
                "التاريخ_الزمني": self._generate_timeline(entry),
                "الشهود": self._summarize_observers(entry),
                "الإجراءات_المتخذة": self._summarize_actions(entry),
                "قرارات_النظام": self._summarize_decisions(entry),
                "المسؤولية_القانونية": self._assess_liability(entry)
            }
        
        return entry
    
    def _find_incident(self, incident_id: str) -> Optional[Dict]:
        """إيجاد حادث في السجل"""
        for entry in self.liability_log:
            if entry["incident_id"] == incident_id:
                return entry
        return None
    
    def _generate_timeline(self, entry: Dict) -> List[Dict]:
        """توليد خط زمني للأحداث"""
        timeline = []
        
        # إضافة الملاحظات
        for obs in entry.get("observers", []):
            timeline.append({
                "time": obs["timestamp"],
                "type": "observation",
                "actor": obs["observer"]["name"],
                "details": obs["observation"]
            })
        
        # إضافة الإجراءات
        for act in entry.get("actors", []):
            timeline.append({
                "time": act["timestamp"],
                "type": "action",
                "actor": act["actor"]["name"],
                "details": f"{act['action']} → {act['result']}"
            })
        
        # ترتيب زمني
        timeline.sort(key=lambda x: x["time"])
        
        return timeline
    
    def _summarize_observers(self, entry: Dict) -> List[Dict]:
        """تلخيص الشهود"""
        return [
            {
                "name": obs["observer"]["name"],
                "role": obs["observer"].get("role", "unknown"),
                "saw_at": obs["timestamp"],
                "action": obs["action_taken"]
            }
            for obs in entry.get("observers", [])
        ]
    
    def _summarize_actions(self, entry: Dict) -> List[Dict]:
        """تلخيص الإجراءات"""
        return [
            {
                "actor": act["actor"]["name"],
                "role": act["actor"].get("role", "unknown"),
                "action": act["action"],
                "result": act["result"],
                "time": act["timestamp"]
            }
            for act in entry.get("actors", [])
        ]
    
    def _summarize_decisions(self, entry: Dict) -> List[Dict]:
        """تلخيص قرارات AI"""
        return [
            {
                "decision_id": dec["id"],
                "type": dec["type"],
                "result": dec["result"],
                "confidence": dec.get("confidence"),
                "reasoning": dec.get("reasoning", [])[:3]  # أول 3 أسباب
            }
            for dec in entry.get("decisions", [])
        ]
    
    def _assess_liability(self, entry: Dict) -> Dict:
        """تقييم المسؤولية القانونية"""
        assessment = {
            "system_compliant": True,
            "warnings_issued": len(entry.get("observers", [])),
            "actions_taken": len(entry.get("actors", [])),
            "ai_recommendations_followed": 0,
            "liability_notes": []
        }
        
        # التحقق من متابعة توصيات AI
        for decision in entry.get("decisions", []):
            if decision.get("result") == "stop_work":
                # هل تم إيقاف العمل فعلياً؟
                stop_actions = [
                    a for a in entry.get("actors", [])
                    if "stop" in a["action"].lower()
                ]
                if stop_actions:
                    assessment["ai_recommendations_followed"] += 1
                else:
                    assessment["liability_notes"].append(
                        "AI recommended work stop but action was not taken"
                    )
        
        # التحقق من رؤية الخطر وعدم التصرف
        if entry.get("observers") and not entry.get("actors"):
            assessment["liability_notes"].append(
                "Hazard was observed but no action was taken"
            )
            assessment["system_compliant"] = False
        
        return assessment


# نماذج عالمية
liability_shield = SafetyLiabilityShield()
