"""
Digital Safety Twin - التوأم الرقمي للسلامة
محاكاة ديناميكية للموقع لتوقع المخاطر قبل وقوعها
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import numpy as np


@dataclass
class WorksiteLocation:
    """موقع في موقع العمل"""
    id: str
    name: str
    coordinates: tuple  # (x, y) أو (lat, lng)
    zone_type: str  # خطر عالي، متوسط، آمن
    equipment: List[str]
    workers_count: int
    risk_level: float  # 0-100


@dataclass
class SafetyScenario:
    """سيناريو محاكاة"""
    id: str
    name: str
    description: str
    risk_factors: List[str]
    probability: float  # 0-1
    severity: float  # 0-10
    mitigation_steps: List[str]


class DigitalSafetyTwin:
    """التوأم الرقمي للسلامة"""
    
    def __init__(self):
        self.locations: Dict[str, WorksiteLocation] = {}
        self.scenarios: Dict[str, SafetyScenario] = {}
        self.historical_data = []
        self.risk_heatmap = {}
        
    def create_worksite(self, worksite_id: str, config: Dict[str, Any]) -> Dict:
        """إنشاء توأم رقمي لموقع عمل"""
        
        # تحليل التكوين
        locations = []
        for loc in config.get('locations', []):
            location = WorksiteLocation(
                id=loc['id'],
                name=loc['name'],
                coordinates=tuple(loc['coordinates']),
                zone_type=loc.get('zone_type', 'medium'),
                equipment=loc.get('equipment', []),
                workers_count=loc.get('workers_count', 0),
                risk_level=self._calculate_initial_risk(loc)
            )
            self.locations[location.id] = location
            locations.append(location)
        
        # بناء الـ Heatmap
        heatmap = self._generate_risk_heatmap(locations)
        
        return {
            "worksite_id": worksite_id,
            "status": "created",
            "locations_count": len(locations),
            "risk_heatmap": heatmap,
            "average_risk": np.mean([loc.risk_level for loc in locations]),
            "created_at": datetime.now().isoformat()
        }
    
    def simulate_scenario(self, scenario_config: Dict[str, Any]) -> Dict:
        """محاكاة سيناريو حادث"""
        
        scenario_type = scenario_config.get('type')
        location_id = scenario_config.get('location_id')
        changes = scenario_config.get('changes', {})
        
        # بناء السيناريو
        scenario = SafetyScenario(
            id=f"scenario_{datetime.now().timestamp()}",
            name=scenario_config.get('name', 'Unknown Scenario'),
            description=scenario_config.get('description', ''),
            risk_factors=scenario_config.get('risk_factors', []),
            probability=self._calculate_probability(scenario_config),
            severity=self._calculate_severity(scenario_config),
            mitigation_steps=self._suggest_mitigation(scenario_config)
        )
        
        # محاكاة التأثير
        impact = self._simulate_impact(scenario, location_id, changes)
        
        # تحليل النتائج
        results = {
            "scenario_id": scenario.id,
            "scenario_name": scenario.name,
            "probability": round(scenario.probability * 100, 2),
            "severity": round(scenario.severity, 2),
            "risk_score": round(scenario.probability * scenario.severity * 10, 2),
            "affected_locations": impact['affected_locations'],
            "estimated_casualties": impact['casualties'],
            "estimated_downtime_hours": impact['downtime'],
            "mitigation_steps": scenario.mitigation_steps,
            "prevention_cost": impact['prevention_cost'],
            "incident_cost": impact['incident_cost'],
            "roi_of_prevention": round(
                (impact['incident_cost'] - impact['prevention_cost']) / 
                impact['prevention_cost'] * 100, 2
            ) if impact['prevention_cost'] > 0 else 0
        }
        
        self.scenarios[scenario.id] = scenario
        
        return results
    
    def test_procedure_change(self, current_procedures: Dict, new_procedures: Dict) -> Dict:
        """اختبار تأثير تغيير الإجراءات"""
        
        # محاكاة الوضع الحالي
        current_risk = self._calculate_total_risk(current_procedures)
        
        # محاكاة الوضع الجديد
        new_risk = self._calculate_total_risk(new_procedures)
        
        # حساب التحسن
        improvement = current_risk - new_risk
        improvement_percent = (improvement / current_risk * 100) if current_risk > 0 else 0
        
        return {
            "current_risk_score": round(current_risk, 2),
            "new_risk_score": round(new_risk, 2),
            "improvement": round(improvement, 2),
            "improvement_percent": round(improvement_percent, 2),
            "recommendation": "ننصح بالتطبيق" if improvement > 0 else "لا ننصح بالتطبيق",
            "affected_areas": self._identify_affected_areas(current_procedures, new_procedures),
            "implementation_difficulty": self._assess_difficulty(new_procedures),
            "estimated_implementation_time": self._estimate_time(new_procedures)
        }
    
    def generate_virtual_heatmap(self, timeframe: str = "current") -> Dict:
        """إنشاء Heatmap افتراضية للمخاطر"""
        
        if not self.locations:
            return {"error": "لا توجد مواقع محددة"}
        
        heatmap_data = []
        
        for loc_id, location in self.locations.items():
            # حساب المخاطر بناءً على:
            # 1. نوع المنطقة
            # 2. عدد العمال
            # 3. المعدات المستخدمة
            # 4. البيانات التاريخية
            
            risk_value = self._calculate_heatmap_risk(location, timeframe)
            
            heatmap_data.append({
                "location_id": loc_id,
                "location_name": location.name,
                "coordinates": location.coordinates,
                "risk_level": risk_value,
                "color": self._get_risk_color(risk_value),
                "priority": self._get_priority(risk_value)
            })
        
        # ترتيب حسب الخطورة
        heatmap_data.sort(key=lambda x: x['risk_level'], reverse=True)
        
        return {
            "heatmap": heatmap_data,
            "timestamp": datetime.now().isoformat(),
            "timeframe": timeframe,
            "highest_risk_zone": heatmap_data[0] if heatmap_data else None,
            "average_risk": round(np.mean([d['risk_level'] for d in heatmap_data]), 2),
            "zones_requiring_attention": len([d for d in heatmap_data if d['risk_level'] > 70])
        }
    
    def predict_incident_hotspots(self, days_ahead: int = 7) -> Dict:
        """توقع نقاط الحوادث الساخنة"""
        
        predictions = []
        
        for loc_id, location in self.locations.items():
            # تحليل الاتجاهات
            trend = self._analyze_trend(location)
            
            # التنبؤ بالمخاطر المستقبلية
            future_risk = self._predict_future_risk(location, days_ahead)
            
            if future_risk > 60:  # عتبة الخطر
                predictions.append({
                    "location_id": loc_id,
                    "location_name": location.name,
                    "current_risk": round(location.risk_level, 2),
                    "predicted_risk": round(future_risk, 2),
                    "trend": trend,
                    "days_ahead": days_ahead,
                    "confidence": self._calculate_prediction_confidence(location),
                    "recommended_actions": self._recommend_preventive_actions(location, future_risk)
                })
        
        return {
            "predictions": predictions,
            "prediction_date": datetime.now().isoformat(),
            "forecast_period": f"{days_ahead} days",
            "hotspots_count": len(predictions)
        }
    
    # ===== وظائف مساعدة =====
    
    def _calculate_initial_risk(self, location_config: Dict) -> float:
        """حساب الخطر الأولي لموقع"""
        risk = 30.0  # قاعدة أساسية
        
        # عوامل الخطر
        if location_config.get('zone_type') == 'high':
            risk += 30
        elif location_config.get('zone_type') == 'medium':
            risk += 15
        
        # عدد العمال
        workers = location_config.get('workers_count', 0)
        risk += min(workers * 2, 20)
        
        # المعدات الخطرة
        dangerous_equipment = ['crane', 'excavator', 'scaffolding', 'chemicals']
        equipment = location_config.get('equipment', [])
        danger_count = sum(1 for eq in equipment if any(d in eq.lower() for d in dangerous_equipment))
        risk += danger_count * 10
        
        return min(risk, 100)
    
    def _generate_risk_heatmap(self, locations: List[WorksiteLocation]) -> List[Dict]:
        """إنشاء خريطة حرارية للمخاطر"""
        return [{
            "location": loc.name,
            "risk_level": round(loc.risk_level, 2),
            "color": self._get_risk_color(loc.risk_level)
        } for loc in locations]
    
    def _get_risk_color(self, risk_level: float) -> str:
        """الحصول على اللون حسب مستوى الخطر"""
        if risk_level >= 70:
            return "red"
        elif risk_level >= 40:
            return "orange"
        else:
            return "green"
    
    def _calculate_probability(self, scenario_config: Dict) -> float:
        """حساب احتمالية وقوع السيناريو"""
        base_prob = 0.3
        
        # زيادة الاحتمالية بناءً على عوامل الخطر
        risk_factors_count = len(scenario_config.get('risk_factors', []))
        base_prob += risk_factors_count * 0.1
        
        return min(base_prob, 0.95)
    
    def _calculate_severity(self, scenario_config: Dict) -> float:
        """حساب شدة السيناريو"""
        severity_map = {
            'fall': 8.0,
            'equipment_failure': 7.0,
            'fire': 9.0,
            'chemical_spill': 8.5,
            'collision': 6.5,
            'default': 5.0
        }
        
        scenario_type = scenario_config.get('type', 'default')
        return severity_map.get(scenario_type, severity_map['default'])
    
    def _suggest_mitigation(self, scenario_config: Dict) -> List[str]:
        """اقتراح خطوات التخفيف"""
        mitigation_db = {
            'fall': [
                "تركيب حواجز سلامة إضافية",
                "فحص معدات الحماية من السقوط",
                "تدريب العمال على السلامة على المرتفعات",
                "وضع شبكات أمان"
            ],
            'equipment_failure': [
                "جدولة صيانة دورية",
                "فحص المعدات قبل كل استخدام",
                "تدريب المشغلين",
                "توفير معدات احتياطية"
            ],
            'fire': [
                "تركيب أنظمة إنذار حريق",
                "توفير طفايات حريق",
                "تدريب على الإخلاء",
                "تخزين المواد القابلة للاشتعال بأمان"
            ],
            'default': [
                "تقييم شامل للمخاطر",
                "تطبيق إجراءات السلامة القياسية",
                "تدريب العمال",
                "المراقبة المستمرة"
            ]
        }
        
        scenario_type = scenario_config.get('type', 'default')
        return mitigation_db.get(scenario_type, mitigation_db['default'])
    
    def _simulate_impact(self, scenario: SafetyScenario, location_id: str, changes: Dict) -> Dict:
        """محاكاة تأثير الحادث"""
        severity = scenario.severity
        probability = scenario.probability
        
        # تقدير الخسائر
        casualties = int(severity * probability * 2)  # تقريبي
        downtime = severity * 4  # ساعات
        prevention_cost = severity * 1000  # دولار
        incident_cost = severity * probability * 10000  # دولار
        
        affected_locations = [location_id]
        if severity > 7:
            # الحادث الكبير يؤثر على مواقع مجاورة
            affected_locations.extend(self._get_nearby_locations(location_id))
        
        return {
            "affected_locations": affected_locations,
            "casualties": casualties,
            "downtime": round(downtime, 1),
            "prevention_cost": prevention_cost,
            "incident_cost": incident_cost
        }
    
    def _get_nearby_locations(self, location_id: str, radius: float = 50.0) -> List[str]:
        """الحصول على المواقع المجاورة"""
        if location_id not in self.locations:
            return []
        
        center = self.locations[location_id]
        nearby = []
        
        for loc_id, loc in self.locations.items():
            if loc_id != location_id:
                # حساب المسافة (مبسط)
                distance = np.sqrt(
                    (center.coordinates[0] - loc.coordinates[0])**2 +
                    (center.coordinates[1] - loc.coordinates[1])**2
                )
                if distance <= radius:
                    nearby.append(loc_id)
        
        return nearby
    
    def _calculate_total_risk(self, procedures: Dict) -> float:
        """حساب الخطر الإجمالي بناءً على الإجراءات"""
        base_risk = 50.0
        
        # تقييم الإجراءات
        safety_measures = procedures.get('safety_measures', [])
        training_hours = procedures.get('training_hours', 0)
        inspection_frequency = procedures.get('inspection_frequency', 'monthly')
        
        # تقليل الخطر
        risk_reduction = len(safety_measures) * 5
        risk_reduction += min(training_hours * 2, 20)
        
        if inspection_frequency == 'daily':
            risk_reduction += 15
        elif inspection_frequency == 'weekly':
            risk_reduction += 10
        elif inspection_frequency == 'monthly':
            risk_reduction += 5
        
        return max(base_risk - risk_reduction, 10)
    
    def _identify_affected_areas(self, current: Dict, new: Dict) -> List[str]:
        """تحديد المجالات المتأثرة"""
        areas = []
        
        if current.get('safety_measures') != new.get('safety_measures'):
            areas.append("إجراءات السلامة")
        if current.get('training_hours') != new.get('training_hours'):
            areas.append("التدريب")
        if current.get('inspection_frequency') != new.get('inspection_frequency'):
            areas.append("التفتيش")
        
        return areas if areas else ["لا توجد تغييرات"]
    
    def _assess_difficulty(self, procedures: Dict) -> str:
        """تقييم صعوبة التنفيذ"""
        changes_count = len(procedures.get('safety_measures', []))
        
        if changes_count > 10:
            return "صعب"
        elif changes_count > 5:
            return "متوسط"
        else:
            return "سهل"
    
    def _estimate_time(self, procedures: Dict) -> str:
        """تقدير وقت التنفيذ"""
        measures = len(procedures.get('safety_measures', []))
        training = procedures.get('training_hours', 0)
        
        total_days = (measures * 2) + (training / 8)
        
        if total_days > 30:
            return f"{int(total_days / 30)} شهر/أشهر"
        else:
            return f"{int(total_days)} يوم/أيام"
    
    def _calculate_heatmap_risk(self, location: WorksiteLocation, timeframe: str) -> float:
        """حساب الخطر لخريطة الحرارة"""
        return location.risk_level
    
    def _get_priority(self, risk_level: float) -> str:
        """تحديد الأولوية"""
        if risk_level >= 70:
            return "عاجل"
        elif risk_level >= 40:
            return "متوسط"
        else:
            return "منخفض"
    
    def _analyze_trend(self, location: WorksiteLocation) -> str:
        """تحليل الاتجاه"""
        # في التطبيق الفعلي، سيتم تحليل البيانات التاريخية
        trends = ["متزايد", "مستقر", "متناقص"]
        return np.random.choice(trends)
    
    def _predict_future_risk(self, location: WorksiteLocation, days: int) -> float:
        """التنبؤ بالخطر المستقبلي"""
        # نموذج تنبؤ بسيط
        current_risk = location.risk_level
        volatility = 0.1  # التقلب
        
        # إضافة عامل عشوائي للتنبؤ
        future_risk = current_risk + (np.random.random() - 0.5) * volatility * days
        
        return min(max(future_risk, 0), 100)
    
    def _calculate_prediction_confidence(self, location: WorksiteLocation) -> float:
        """حساب ثقة التنبؤ"""
        # في التطبيق الفعلي، يعتمد على كمية البيانات التاريخية
        return round(0.7 + np.random.random() * 0.2, 2)
    
    def _recommend_preventive_actions(self, location: WorksiteLocation, future_risk: float) -> List[str]:
        """التوصية بإجراءات وقائية"""
        actions = []
        
        if future_risk > 80:
            actions.append("إجراء فحص طارئ فوري")
            actions.append("تقليل عدد العمال")
            actions.append("مراجعة جميع إجراءات السلامة")
        elif future_risk > 60:
            actions.append("زيادة التفتيش الدوري")
            actions.append("تدريب إضافي للعمال")
            actions.append("فحص المعدات")
        else:
            actions.append("الحفاظ على الإجراءات الحالية")
            actions.append("المراقبة المستمرة")
        
        return actions


# مثال على الاستخدام
if __name__ == "__main__":
    twin = DigitalSafetyTwin()
    
    # إنشاء توأم رقمي
    worksite_config = {
        "locations": [
            {
                "id": "zone_a",
                "name": "منطقة البناء الرئيسية",
                "coordinates": [0, 0],
                "zone_type": "high",
                "equipment": ["crane", "scaffolding"],
                "workers_count": 25
            },
            {
                "id": "zone_b",
                "name": "منطقة التخزين",
                "coordinates": [50, 50],
                "zone_type": "medium",
                "equipment": ["forklift"],
                "workers_count": 10
            }
        ]
    }
    
    result = twin.create_worksite("site_001", worksite_config)
    print(json.dumps(result, indent=2, ensure_ascii=False))
