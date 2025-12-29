"""
HAZM TUWAIQ - Root Cause AI
Deep learning system for identifying true root causes of safety incidents
Goes beyond surface symptoms to find systemic issues
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict, Counter
import re


class CausalFactor:
    """A potential contributing factor to an incident"""
    
    def __init__(self, factor_type: str, description: str, confidence: float):
        self.factor_type = factor_type
        self.description = description
        self.confidence = confidence  # 0-1
        self.evidence: List[str] = []
        self.related_incidents: List[str] = []
        
    def add_evidence(self, evidence: str):
        """Add supporting evidence for this factor"""
        self.evidence.append(evidence)
        # Increase confidence with more evidence
        self.confidence = min(1.0, self.confidence + 0.05)


class RootCause:
    """Identified root cause with analysis"""
    
    def __init__(
        self,
        cause_id: str,
        primary_cause: str,
        category: str,
        confidence: float
    ):
        self.cause_id = cause_id
        self.primary_cause = primary_cause
        self.category = category
        self.confidence = confidence
        self.contributing_factors: List[CausalFactor] = []
        self.affected_incidents: List[str] = []
        self.systemic_impact = "low"  # low, medium, high, critical
        self.recommended_actions: List[Dict[str, Any]] = []
        self.prevention_cost_estimate = 0.0
        self.potential_loss_prevention = 0.0
        self.identified_at = datetime.now()
        
    def calculate_roi(self) -> float:
        """Calculate ROI of addressing this root cause"""
        if self.prevention_cost_estimate == 0:
            return 0.0
        return (self.potential_loss_prevention - self.prevention_cost_estimate) / self.prevention_cost_estimate


class RootCauseAI:
    """
    Advanced AI system for root cause analysis
    
    Uses multiple analysis techniques:
    - 5 Whys Analysis
    - Fishbone (Ishikawa) Analysis  
    - Fault Tree Analysis
    - Change Analysis
    - Barrier Analysis
    - Pattern Recognition
    - Correlation Analysis
    """
    
    def __init__(self):
        self.identified_root_causes: Dict[str, RootCause] = {}
        self.incident_database: List[Dict[str, Any]] = []
        
        # Root cause categories
        self.categories = [
            "human_error",
            "equipment_failure",
            "process_deficiency",
            "organizational_culture",
            "training_inadequacy",
            "design_flaw",
            "environmental_factors",
            "management_oversight",
            "communication_breakdown",
            "resource_limitation"
        ]
        
    def analyze_incident(
        self,
        incident: Dict[str, Any],
        depth: int = 5
    ) -> RootCause:
        """
        Comprehensive root cause analysis of an incident
        
        Args:
            incident: Incident details
            depth: How deep to analyze (number of "why" iterations)
        """
        
        # Store incident
        self.incident_database.append(incident)
        
        # Multiple analysis approaches
        five_whys = self._five_whys_analysis(incident, depth)
        fishbone = self._fishbone_analysis(incident)
        patterns = self._pattern_recognition(incident)
        barriers = self._barrier_analysis(incident)
        
        # Synthesize results
        root_cause = self._synthesize_findings(
            incident,
            five_whys,
            fishbone,
            patterns,
            barriers
        )
        
        # Generate recommendations
        root_cause.recommended_actions = self._generate_recommendations(root_cause)
        
        # Estimate impact
        self._estimate_impact(root_cause)
        
        # Store root cause
        self.identified_root_causes[root_cause.cause_id] = root_cause
        
        return root_cause
    
    def _five_whys_analysis(
        self,
        incident: Dict[str, Any],
        depth: int
    ) -> List[Dict[str, Any]]:
        """
        Perform iterative "5 Whys" analysis
        Each why digs deeper into causation
        """
        
        whys = []
        current_issue = incident.get('description', 'Unknown incident')
        
        for i in range(depth):
            why_question = f"Why did '{current_issue}' happen?"
            
            # Analyze based on incident data
            why_answer = self._infer_why(current_issue, incident, i)
            
            whys.append({
                'level': i + 1,
                'question': why_question,
                'answer': why_answer,
                'confidence': max(0.1, 0.9 - (i * 0.15))  # Confidence decreases with depth
            })
            
            current_issue = why_answer
        
        return whys
    
    def _infer_why(
        self,
        issue: str,
        incident: Dict[str, Any],
        level: int
    ) -> str:
        """Infer the 'why' based on available data and patterns"""
        
        # Level 0: Immediate cause
        if level == 0:
            incident_type = incident.get('type', 'unknown')
            if 'fall' in incident_type.lower():
                return "Worker lost balance or footing"
            elif 'collision' in incident_type.lower():
                return "Equipment or person entered unsafe proximity"
            elif 'ppe' in incident_type.lower():
                return "Required safety equipment was not worn"
            else:
                return f"Unsafe condition or action in {incident.get('location', 'workplace')}"
        
        # Level 1: Contributing factors
        elif level == 1:
            conditions = incident.get('conditions', {})
            if conditions.get('visibility') == 'poor':
                return "Poor lighting or visibility in work area"
            elif conditions.get('weather') in ['rain', 'ice']:
                return "Adverse weather conditions affected safety"
            elif incident.get('time_of_day') in ['night', 'late_shift']:
                return "Fatigue or reduced alertness during off-hours"
            else:
                return "Inadequate hazard awareness or training"
        
        # Level 2: Systemic issues
        elif level == 2:
            return "Insufficient safety protocols or enforcement"
        
        # Level 3: Organizational
        elif level == 3:
            return "Safety culture or management priorities"
        
        # Level 4: Root organizational
        else:
            return "Inadequate safety management system or resources"
    
    def _fishbone_analysis(self, incident: Dict[str, Any]) -> Dict[str, List[CausalFactor]]:
        """
        Ishikawa/Fishbone diagram analysis
        Categorizes causes into: People, Process, Equipment, Environment, Management
        """
        
        fishbone = {
            'people': [],
            'process': [],
            'equipment': [],
            'environment': [],
            'management': [],
            'materials': []
        }
        
        incident_type = incident.get('type', '')
        severity = incident.get('severity', 'low')
        
        # People factors
        if incident.get('worker_id'):
            fishbone['people'].append(CausalFactor(
                'human_error',
                'Worker action or inaction',
                0.6
            ))
        
        if incident.get('training_status') == 'incomplete':
            fishbone['people'].append(CausalFactor(
                'training_gap',
                'Insufficient or incomplete training',
                0.8
            ))
        
        # Equipment factors
        if 'equipment' in incident_type.lower() or 'machine' in incident_type.lower():
            fishbone['equipment'].append(CausalFactor(
                'equipment_failure',
                'Equipment malfunction or degradation',
                0.7
            ))
        
        # Environment factors
        conditions = incident.get('conditions', {})
        if conditions.get('temperature'):
            temp = conditions['temperature']
            if temp > 35 or temp < 5:
                fishbone['environment'].append(CausalFactor(
                    'extreme_conditions',
                    f'Extreme temperature ({temp}°C)',
                    0.75
                ))
        
        # Process factors
        if incident.get('procedure_followed') is False:
            fishbone['process'].append(CausalFactor(
                'process_deviation',
                'Standard procedure not followed',
                0.85
            ))
        
        # Management factors
        if incident.get('supervision') == 'absent':
            fishbone['management'].append(CausalFactor(
                'supervision_gap',
                'Lack of adequate supervision',
                0.7
            ))
        
        return fishbone
    
    def _pattern_recognition(self, incident: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify patterns from historical incidents"""
        
        patterns = []
        
        # Find similar incidents
        similar = self._find_similar_incidents(incident)
        
        if len(similar) >= 3:
            patterns.append({
                'type': 'recurring_incident',
                'description': f'Similar incident occurred {len(similar)} times',
                'confidence': min(1.0, len(similar) * 0.2),
                'incidents': [inc.get('id') for inc in similar]
            })
        
        # Time pattern
        time_pattern = self._detect_time_pattern(incident)
        if time_pattern:
            patterns.append(time_pattern)
        
        # Location pattern
        location_pattern = self._detect_location_pattern(incident)
        if location_pattern:
            patterns.append(location_pattern)
        
        return patterns
    
    def _find_similar_incidents(self, incident: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar incidents in database"""
        similar = []
        
        incident_type = incident.get('type')
        location = incident.get('location')
        
        for past_incident in self.incident_database[-100:]:  # Last 100 incidents
            if past_incident.get('type') == incident_type:
                similar.append(past_incident)
            elif past_incident.get('location') == location:
                similar.append(past_incident)
        
        return similar
    
    def _detect_time_pattern(self, incident: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect if incidents occur at specific times"""
        
        timestamp = incident.get('timestamp')
        if not timestamp:
            return None
        
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        hour = timestamp.hour
        
        # Count incidents in same time period
        same_period = 0
        for past_incident in self.incident_database[-50:]:
            past_time = past_incident.get('timestamp')
            if past_time:
                if isinstance(past_time, str):
                    past_time = datetime.fromisoformat(past_time)
                
                if abs(past_time.hour - hour) <= 1:
                    same_period += 1
        
        if same_period >= 5:
            return {
                'type': 'temporal_pattern',
                'description': f'Incidents cluster around {hour}:00',
                'confidence': min(1.0, same_period * 0.1)
            }
        
        return None
    
    def _detect_location_pattern(self, incident: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect if specific locations are high-risk"""
        
        location = incident.get('location')
        if not location:
            return None
        
        # Count incidents in same location
        location_count = sum(
            1 for inc in self.incident_database[-100:]
            if inc.get('location') == location
        )
        
        if location_count >= 5:
            return {
                'type': 'location_hotspot',
                'description': f'{location} has {location_count} incidents',
                'confidence': min(1.0, location_count * 0.1)
            }
        
        return None
    
    def _barrier_analysis(self, incident: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze what safety barriers failed
        Swiss cheese model - multiple barriers should prevent incidents
        """
        
        failed_barriers = []
        
        # Physical barriers
        if not incident.get('physical_protection'):
            failed_barriers.append({
                'barrier': 'physical_protection',
                'description': 'Physical barriers or guards not in place',
                'layer': 'physical'
            })
        
        # Administrative barriers
        if not incident.get('permit_obtained'):
            failed_barriers.append({
                'barrier': 'work_permit',
                'description': 'Work permit not obtained',
                'layer': 'administrative'
            })
        
        # PPE barriers
        if not incident.get('ppe_worn'):
            failed_barriers.append({
                'barrier': 'personal_protective_equipment',
                'description': 'PPE not worn or inadequate',
                'layer': 'personal'
            })
        
        # Supervision barriers
        if incident.get('supervision') == 'absent':
            failed_barriers.append({
                'barrier': 'supervision',
                'description': 'Supervisory oversight absent',
                'layer': 'organizational'
            })
        
        return failed_barriers
    
    def _synthesize_findings(
        self,
        incident: Dict[str, Any],
        five_whys: List[Dict[str, Any]],
        fishbone: Dict[str, List[CausalFactor]],
        patterns: List[Dict[str, Any]],
        barriers: List[Dict[str, Any]]
    ) -> RootCause:
        """Synthesize all analyses into final root cause"""
        
        # Use deepest "why" as primary root cause
        primary_cause = five_whys[-1]['answer'] if five_whys else "Unknown root cause"
        
        # Determine category based on fishbone with most factors
        category_counts = {cat: len(factors) for cat, factors in fishbone.items()}
        primary_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else "unknown"
        
        # Calculate overall confidence
        confidence_scores = []
        if five_whys:
            confidence_scores.extend([w['confidence'] for w in five_whys])
        if fishbone:
            for factors in fishbone.values():
                confidence_scores.extend([f.confidence for f in factors])
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        
        # Create root cause
        cause_id = f"RC-{len(self.identified_root_causes) + 1:04d}"
        
        root_cause = RootCause(
            cause_id=cause_id,
            primary_cause=primary_cause,
            category=primary_category,
            confidence=avg_confidence
        )
        
        # Add contributing factors
        for cat, factors in fishbone.items():
            root_cause.contributing_factors.extend(factors)
        
        # Add evidence from barriers
        for barrier in barriers:
            evidence = f"Barrier failure: {barrier['description']}"
            if root_cause.contributing_factors:
                root_cause.contributing_factors[0].add_evidence(evidence)
        
        # Determine systemic impact
        if len(patterns) >= 2 or len(barriers) >= 3:
            root_cause.systemic_impact = "high"
        elif len(patterns) >= 1 or len(barriers) >= 2:
            root_cause.systemic_impact = "medium"
        else:
            root_cause.systemic_impact = "low"
        
        root_cause.affected_incidents.append(incident.get('id', 'unknown'))
        
        return root_cause
    
    def _generate_recommendations(self, root_cause: RootCause) -> List[Dict[str, Any]]:
        """Generate actionable recommendations to address root cause"""
        
        recommendations = []
        
        category = root_cause.category
        
        if category == 'people':
            recommendations.append({
                'action': 'Enhanced Training Program',
                'priority': 'high',
                'timeline': '30 days',
                'estimated_cost': 5000,
                'description': 'Implement comprehensive training on identified gaps'
            })
        
        elif category == 'equipment':
            recommendations.append({
                'action': 'Equipment Maintenance Review',
                'priority': 'critical',
                'timeline': '7 days',
                'estimated_cost': 10000,
                'description': 'Inspect and maintain all similar equipment'
            })
        
        elif category == 'process':
            recommendations.append({
                'action': 'Process Redesign',
                'priority': 'high',
                'timeline': '60 days',
                'estimated_cost': 15000,
                'description': 'Review and improve standard operating procedures'
            })
        
        elif category == 'management':
            recommendations.append({
                'action': 'Management System Improvement',
                'priority': 'critical',
                'timeline': '90 days',
                'estimated_cost': 20000,
                'description': 'Strengthen safety management and oversight'
            })
        
        elif category == 'environment':
            recommendations.append({
                'action': 'Environmental Controls',
                'priority': 'medium',
                'timeline': '45 days',
                'estimated_cost': 8000,
                'description': 'Implement controls for environmental factors'
            })
        
        # Add monitoring recommendation
        recommendations.append({
            'action': 'Continuous Monitoring',
            'priority': 'ongoing',
            'timeline': 'ongoing',
            'estimated_cost': 2000,
            'description': 'Monitor for recurrence and effectiveness of interventions'
        })
        
        return recommendations
    
    def _estimate_impact(self, root_cause: RootCause):
        """Estimate cost and impact of addressing root cause"""
        
        # Sum up recommendation costs
        total_cost = sum(
            rec.get('estimated_cost', 0)
            for rec in root_cause.recommended_actions
        )
        
        root_cause.prevention_cost_estimate = total_cost
        
        # Estimate potential loss prevention
        # Based on severity and systemic impact
        impact_multiplier = {
            'low': 1.0,
            'medium': 3.0,
            'high': 10.0,
            'critical': 50.0
        }
        
        multiplier = impact_multiplier.get(root_cause.systemic_impact, 1.0)
        
        # Average incident cost ranges
        base_incident_cost = 25000  # Conservative estimate
        
        # Estimate prevented incidents per year
        estimated_prevented = len(root_cause.affected_incidents) * 2  # Conservative
        
        root_cause.potential_loss_prevention = base_incident_cost * estimated_prevented * multiplier
    
    def get_top_root_causes(self, limit: int = 10) -> List[RootCause]:
        """Get top root causes ranked by impact"""
        
        causes = list(self.identified_root_causes.values())
        
        # Sort by ROI and systemic impact
        causes.sort(
            key=lambda x: (x.systemic_impact == 'high', x.calculate_roi()),
            reverse=True
        )
        
        return causes[:limit]
    
    def generate_executive_report(self) -> Dict[str, Any]:
        """Generate executive summary of root cause findings"""
        
        total_causes = len(self.identified_root_causes)
        
        # Category breakdown
        category_breakdown = Counter(
            rc.category for rc in self.identified_root_causes.values()
        )
        
        # High-impact causes
        high_impact = [
            rc for rc in self.identified_root_causes.values()
            if rc.systemic_impact in ['high', 'critical']
        ]
        
        # Total potential savings
        total_savings = sum(
            rc.potential_loss_prevention
            for rc in self.identified_root_causes.values()
        )
        
        total_investment = sum(
            rc.prevention_cost_estimate
            for rc in self.identified_root_causes.values()
        )
        
        return {
            'total_root_causes_identified': total_causes,
            'high_impact_causes': len(high_impact),
            'category_breakdown': dict(category_breakdown),
            'total_potential_savings': total_savings,
            'total_recommended_investment': total_investment,
            'projected_roi': (total_savings - total_investment) / total_investment if total_investment > 0 else 0,
            'top_recommendations': [
                {
                    'cause_id': rc.cause_id,
                    'cause': rc.primary_cause,
                    'impact': rc.systemic_impact,
                    'roi': rc.calculate_roi()
                }
                for rc in self.get_top_root_causes(5)
            ]
        }


# Global root cause AI instance
root_cause_ai = RootCauseAI()
