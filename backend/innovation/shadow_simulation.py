"""
Shadow Safety Simulation - محاكاة الظل
محاكاة غير مرئية لسيناريوهات "ماذا لو"
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import json


class SimulationScenario(Enum):
    """سيناريوهات المحاكاة"""
    WHAT_IF_NO_ACTION = "what_if_no_action"
    WHAT_IF_IGNORED_WARNING = "what_if_ignored_warning"
    WHAT_IF_DELAYED_RESPONSE = "what_if_delayed_response"
    WHAT_IF_DIFFERENT_ACTION = "what_if_different_action"
    WHAT_IF_NO_PPE = "what_if_no_ppe"


class ShadowSimulator:
    """محاكي الظل - يعمل في الخلفية"""
    
    def __init__(self):
        self.simulations: List[Dict] = []
        self.scenario_models: Dict = self._load_scenario_models()
    
    def _load_scenario_models(self) -> Dict:
        """تحميل نماذج السيناريوهات"""
        return {
            "no_action": {
                "risk_multiplier": 3.0,
                "incident_probability": 0.85,
                "severity_increase": 2
            },
            "ignored_warning": {
                "risk_multiplier": 2.5,
                "incident_probability": 0.75,
                "severity_increase": 1.5
            },
            "delayed_response": {
                "risk_multiplier": 1.8,
                "incident_probability": 0.60,
                "severity_increase": 1.2
            },
            "no_ppe": {
                "risk_multiplier": 4.0,
                "incident_probability": 0.90,
                "severity_increase": 2.5
            }
        }
    
    def run_shadow_simulation(self, actual_event: Dict, alternative_scenarios: List[str]) -> Dict:
        """تشغيل محاكاة ظل"""
        simulation_id = f"SIM_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        results = {
            "simulation_id": simulation_id,
            "timestamp": datetime.now().isoformat(),
            "actual_event": actual_event,
            "actual_outcome": actual_event.get("outcome", "safe"),
            "alternative_scenarios": []
        }
        
        # محاكاة كل سيناريو بديل
        for scenario in alternative_scenarios:
            simulated = self._simulate_scenario(scenario, actual_event)
            results["alternative_scenarios"].append(simulated)
        
        # حساب "القيمة المحفوظة"
        results["value_saved"] = self._calculate_value_saved(
            actual_event, 
            results["alternative_scenarios"]
        )
        
        # حفظ المحاكاة
        self.simulations.append(results)
        
        return results
    
    def _simulate_scenario(self, scenario: str, actual_event: Dict) -> Dict:
        """محاكاة سيناريو واحد"""
        model = self.scenario_models.get(scenario.replace("what_if_", ""))
        
        if not model:
            return {"scenario": scenario, "error": "Unknown scenario"}
        
        # الحصول على الخطر الأصلي
        base_risk = actual_event.get("risk_level", 0.5)
        base_severity = actual_event.get("severity", 1)
        
        # تطبيق النموذج
        simulated_risk = min(base_risk * model["risk_multiplier"], 1.0)
        simulated_severity = base_severity * model["severity_increase"]
        incident_would_occur = model["incident_probability"]
        
        # تقدير العواقب
        consequences = self._estimate_consequences(
            simulated_risk, 
            simulated_severity, 
            incident_would_occur,
            actual_event
        )
        
        return {
            "scenario": scenario,
            "simulated_risk": simulated_risk,
            "simulated_severity": simulated_severity,
            "incident_probability": incident_would_occur,
            "estimated_consequences": consequences,
            "comparison_to_actual": {
                "risk_increase": f"+{((simulated_risk - base_risk) / base_risk * 100):.0f}%",
                "severity_increase": f"+{((simulated_severity - base_severity) / base_severity * 100):.0f}%"
            }
        }
    
    def _estimate_consequences(self, risk: float, severity: float, probability: float, context: Dict) -> Dict:
        """تقدير العواقب المحتملة"""
        consequences = {
            "human_cost": {},
            "financial_cost": {},
            "operational_impact": {},
            "legal_impact": {}
        }
        
        # التكلفة البشرية
        if probability > 0.7 and severity > 2:
            consequences["human_cost"] = {
                "injuries_likely": True,
                "severity": "major" if severity > 3 else "moderate",
                "estimated_victims": int(severity),
                "recovery_time_days": int(severity * 30)
            }
        else:
            consequences["human_cost"] = {
                "injuries_likely": False,
                "severity": "minor",
                "estimated_victims": 0
            }
        
        # التكلفة المالية (تقديرية بالريال السعودي)
        base_cost = 50000  # تكلفة أساسية
        injury_cost = severity * 100000  # 100 ألف لكل مستوى خطورة
        downtime_cost = severity * 50000  # تكلفة التوقف
        legal_cost = severity * 200000 if severity > 2 else 0
        
        total_cost = (base_cost + injury_cost + downtime_cost + legal_cost) * probability
        
        consequences["financial_cost"] = {
            "estimated_total_sar": int(total_cost),
            "breakdown": {
                "medical": int(injury_cost * probability),
                "downtime": int(downtime_cost * probability),
                "legal": int(legal_cost * probability),
                "insurance": int(base_cost * probability)
            }
        }
        
        # التأثير التشغيلي
        downtime_hours = int(severity * 8 * probability)
        consequences["operational_impact"] = {
            "estimated_downtime_hours": downtime_hours,
            "affected_operations": context.get("location", "unknown"),
            "cascading_delays": downtime_hours > 24
        }
        
        # التأثير القانوني
        if severity > 3 or probability > 0.8:
            consequences["legal_impact"] = {
                "investigation_required": True,
                "potential_violations": ["safety_breach", "negligence"],
                "regulatory_risk": "high"
            }
        else:
            consequences["legal_impact"] = {
                "investigation_required": False,
                "potential_violations": [],
                "regulatory_risk": "low"
            }
        
        return consequences
    
    def _calculate_value_saved(self, actual: Dict, alternatives: List[Dict]) -> Dict:
        """حساب القيمة المحفوظة من اتخاذ الإجراء الصحيح"""
        # أسوأ سيناريو
        worst_scenario = max(
            alternatives,
            key=lambda x: x.get("estimated_consequences", {}).get("financial_cost", {}).get("estimated_total_sar", 0)
        )
        
        worst_cost = worst_scenario.get("estimated_consequences", {}).get("financial_cost", {}).get("estimated_total_sar", 0)
        worst_injuries = worst_scenario.get("estimated_consequences", {}).get("human_cost", {}).get("estimated_victims", 0)
        
        return {
            "financial_value_saved_sar": worst_cost,
            "injuries_prevented": worst_injuries,
            "downtime_avoided_hours": worst_scenario.get("estimated_consequences", {}).get("operational_impact", {}).get("estimated_downtime_hours", 0),
            "worst_scenario": worst_scenario["scenario"],
            "summary_ar": f"تم تجنب خسائر تقدر بـ {worst_cost:,} ريال و{worst_injuries} إصابات محتملة"
        }
    
    def generate_what_if_report(self, simulation_id: str, language: str = "ar") -> Dict:
        """توليد تقرير "ماذا لو"""
        sim = next((s for s in self.simulations if s["simulation_id"] == simulation_id), None)
        
        if not sim:
            return {"error": "Simulation not found"}
        
        if language == "ar":
            return {
                "معرف_المحاكاة": simulation_id,
                "التاريخ": sim["timestamp"],
                "الحدث_الفعلي": sim["actual_event"],
                "النتيجة_الفعلية": sim["actual_outcome"],
                "السيناريوهات_البديلة": [
                    {
                        "السيناريو": s["scenario"],
                        "مستوى_الخطر_المحتمل": f"{s['simulated_risk']:.0%}",
                        "الخطورة": s["simulated_severity"],
                        "احتمالية_وقوع_حادث": f"{s['incident_probability']:.0%}",
                        "العواقب_المقدرة": s["estimated_consequences"]
                    }
                    for s in sim["alternative_scenarios"]
                ],
                "القيمة_المحفوظة": sim["value_saved"]
            }
        
        return sim
    
    def get_saved_value_summary(self, days: int = 30) -> Dict:
        """ملخص القيمة المحفوظة خلال فترة"""
        cutoff = datetime.now() - timedelta(days=days)
        
        recent_sims = [
            s for s in self.simulations
            if datetime.fromisoformat(s["timestamp"]) > cutoff
        ]
        
        total_financial = sum(
            s["value_saved"].get("financial_value_saved_sar", 0)
            for s in recent_sims
        )
        
        total_injuries = sum(
            s["value_saved"].get("injuries_prevented", 0)
            for s in recent_sims
        )
        
        total_downtime = sum(
            s["value_saved"].get("downtime_avoided_hours", 0)
            for s in recent_sims
        )
        
        return {
            "period_days": days,
            "total_simulations": len(recent_sims),
            "total_financial_value_saved_sar": total_financial,
            "total_injuries_prevented": total_injuries,
            "total_downtime_avoided_hours": total_downtime,
            "average_value_per_intervention": total_financial // len(recent_sims) if recent_sims else 0,
            "summary_ar": f"خلال {days} يوم: تم تجنب {total_financial:,} ريال و {total_injuries} إصابات و {total_downtime} ساعة توقف"
        }


class SafetyBudgetOptimizer:
    """محسّن ميزانية السلامة - ربط المخاطر بالتكلفة"""
    
    def __init__(self):
        self.budget_allocations: List[Dict] = []
    
    def optimize_budget(self, total_budget: float, risk_areas: List[Dict]) -> Dict:
        """تحسين توزيع ميزانية السلامة"""
        # حساب الأولويات
        prioritized = self._prioritize_areas(risk_areas)
        
        # توزيع الميزانية
        allocations = self._allocate_budget(total_budget, prioritized)
        
        # حساب ROI المتوقع
        roi = self._calculate_safety_roi(allocations)
        
        result = {
            "total_budget_sar": total_budget,
            "allocations": allocations,
            "expected_roi": roi,
            "recommendations": self._generate_recommendations(allocations)
        }
        
        self.budget_allocations.append({
            "timestamp": datetime.now().isoformat(),
            "result": result
        })
        
        return result
    
    def _prioritize_areas(self, risk_areas: List[Dict]) -> List[Dict]:
        """ترتيب المناطق حسب الأولوية"""
        for area in risk_areas:
            # حساب نقاط الأولوية
            risk_score = area.get("risk_level", 0.5)
            incident_history = area.get("past_incidents", 0)
            worker_count = area.get("worker_count", 1)
            
            priority_score = (risk_score * 0.5) + (incident_history * 0.3) + (worker_count / 100 * 0.2)
            area["priority_score"] = priority_score
        
        # ترتيب تنازلي
        return sorted(risk_areas, key=lambda x: x["priority_score"], reverse=True)
    
    def _allocate_budget(self, total: float, areas: List[Dict]) -> List[Dict]:
        """توزيع الميزانية"""
        total_priority = sum(a["priority_score"] for a in areas)
        
        allocations = []
        for area in areas:
            # توزيع تناسبي مع الأولوية
            allocation = (area["priority_score"] / total_priority) * total
            
            allocations.append({
                "area": area["name"],
                "current_risk": area["risk_level"],
                "priority_score": area["priority_score"],
                "allocated_budget_sar": int(allocation),
                "recommended_actions": self._suggest_actions(area, allocation)
            })
        
        return allocations
    
    def _suggest_actions(self, area: Dict, budget: float) -> List[Dict]:
        """اقتراح إجراءات حسب الميزانية"""
        actions = []
        
        # إجراءات أساسية (أقل من 50 ألف)
        if budget >= 10000:
            actions.append({
                "action": "تدريب إضافي للعمال",
                "cost": 10000,
                "risk_reduction": 0.15
            })
        
        if budget >= 20000:
            actions.append({
                "action": "تحديث معدات السلامة",
                "cost": 20000,
                "risk_reduction": 0.25
            })
        
        # إجراءات متوسطة (50-100 ألف)
        if budget >= 50000:
            actions.append({
                "action": "نظام مراقبة متقدم",
                "cost": 50000,
                "risk_reduction": 0.35
            })
        
        # إجراءات كبيرة (أكثر من 100 ألف)
        if budget >= 100000:
            actions.append({
                "action": "إعادة تصميم منطقة العمل",
                "cost": 100000,
                "risk_reduction": 0.50
            })
        
        return actions
    
    def _calculate_safety_roi(self, allocations: List[Dict]) -> Dict:
        """حساب العائد على الاستثمار في السلامة"""
        total_invested = sum(a["allocated_budget_sar"] for a in allocations)
        
        # تقدير العائد (الخسائر المتجنبة)
        expected_savings = 0
        for allocation in allocations:
            actions = allocation.get("recommended_actions", [])
            risk_reduction = sum(a["risk_reduction"] for a in actions)
            
            # تقدير الخسائر المحتملة
            potential_loss = allocation["current_risk"] * 500000  # تقدير
            savings = potential_loss * risk_reduction
            expected_savings += savings
        
        roi_ratio = (expected_savings / total_invested) if total_invested > 0 else 0
        
        return {
            "total_investment_sar": total_invested,
            "expected_savings_sar": int(expected_savings),
            "roi_ratio": round(roi_ratio, 2),
            "roi_percentage": f"{roi_ratio * 100:.0f}%",
            "payback_period_months": int(12 / roi_ratio) if roi_ratio > 0 else 999,
            "summary_ar": f"استثمار {total_invested:,} ريال يمكن أن يوفر {int(expected_savings):,} ريال (عائد {roi_ratio * 100:.0f}%)"
        }
    
    def _generate_recommendations(self, allocations: List[Dict]) -> List[str]:
        """توليد توصيات"""
        recommendations = []
        
        # التركيز على المناطق عالية الخطورة
        high_risk_areas = [a for a in allocations if a["current_risk"] > 0.7]
        if high_risk_areas:
            recommendations.append(f"الأولوية القصوى: {len(high_risk_areas)} منطقة عالية الخطورة تحتاج تدخل فوري")
        
        # توصيات الميزانية
        total_budget = sum(a["allocated_budget_sar"] for a in allocations)
        if total_budget < 100000:
            recommendations.append("ميزانية السلامة منخفضة - يُنصح بالزيادة لتحقيق معايير أعلى")
        
        recommendations.append("التركيز على الإجراءات الوقائية يوفر 4-5x مقارنة بالعلاج")
        
        return recommendations


# نماذج عالمية
shadow_simulator = ShadowSimulator()
budget_optimizer = SafetyBudgetOptimizer()
