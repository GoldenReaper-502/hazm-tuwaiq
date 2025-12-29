"""
HAZM TUWAIQ - Report Builder
Custom report creation and data aggregation
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from .models import (
    ReportData, ReportMetrics, ReportChart, ReportTable,
    ReportType, ComplianceReport, BoardReport
)


class ReportBuilder:
    """Build comprehensive reports from raw data"""
    
    def __init__(self):
        self.data_sources = {}
    
    def build_safety_report(
        self,
        organization_id: str,
        organization_name: str,
        start_date: datetime,
        end_date: datetime,
        incidents: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]],
        violations: List[Dict[str, Any]],
        predictions: Optional[Dict[str, Any]] = None
    ) -> ReportData:
        """Build comprehensive safety report"""
        
        # Calculate metrics
        metrics = self._calculate_metrics(incidents, alerts, violations)
        
        # Generate executive summary
        exec_summary = self._generate_executive_summary(metrics, start_date, end_date)
        
        # Key findings
        key_findings = self._identify_key_findings(incidents, violations, metrics)
        
        # Recommendations
        recommendations = self._generate_recommendations(metrics, incidents)
        
        # Create charts
        charts = self._create_safety_charts(incidents, alerts, violations)
        
        # Create tables
        tables = self._create_safety_tables(incidents, violations)
        
        report = ReportData(
            report_type=ReportType.SAFETY_SUMMARY,
            format="pdf",
            title="Safety Performance Report",
            description=f"Comprehensive safety analysis for {organization_name}",
            organization_id=organization_id,
            organization_name=organization_name,
            period_start=start_date,
            period_end=end_date,
            generated_by="system",
            executive_summary=exec_summary,
            key_findings=key_findings,
            recommendations=recommendations,
            metrics=metrics,
            charts=charts,
            tables=tables,
            incidents=incidents,
            violations=violations,
            predictions=predictions
        )
        
        return report
    
    def build_compliance_report(
        self,
        organization_id: str,
        regulatory_body: str,
        standard: str,
        start_date: datetime,
        end_date: datetime,
        compliance_data: Dict[str, Any]
    ) -> ComplianceReport:
        """Build regulatory compliance report"""
        
        # Calculate compliance metrics
        total_items = compliance_data.get('total_items', 0)
        compliant = compliance_data.get('compliant_items', 0)
        non_compliant = compliance_data.get('non_compliant_items', 0)
        pending = compliance_data.get('pending_items', 0)
        
        overall_compliance = (compliant / total_items * 100) if total_items > 0 else 0
        
        # Extract violations
        violations = compliance_data.get('violations', [])
        
        # Generate corrective actions
        corrective_actions = self._generate_corrective_actions(violations)
        
        # Recommendations
        recommendations = self._generate_compliance_recommendations(overall_compliance, violations)
        
        report = ComplianceReport(
            organization_id=organization_id,
            regulatory_body=regulatory_body,
            standard=standard,
            period_start=start_date,
            period_end=end_date,
            overall_compliance=overall_compliance,
            compliant_items=compliant,
            non_compliant_items=non_compliant,
            pending_items=pending,
            violations=violations,
            corrective_actions=corrective_actions,
            recommendations=recommendations,
            generated_by="system"
        )
        
        return report
    
    def build_board_report(
        self,
        organization_id: str,
        start_date: datetime,
        end_date: datetime,
        metrics: ReportMetrics,
        financial_data: Dict[str, Any],
        initiatives: Dict[str, Any]
    ) -> BoardReport:
        """Build executive board report"""
        
        # Executive summary
        exec_summary = self._generate_board_summary(metrics, financial_data)
        
        # Strategic highlights
        highlights = self._identify_strategic_highlights(metrics, initiatives)
        
        # Calculate period-over-period changes
        prev_incidents = financial_data.get('previous_incidents', metrics.total_incidents)
        incident_reduction = ((prev_incidents - metrics.total_incidents) / prev_incidents * 100) if prev_incidents > 0 else 0
        
        # Financial impact
        incident_costs = financial_data.get('incident_costs', 0)
        savings = financial_data.get('prevention_savings', 0)
        insurance_impact = financial_data.get('insurance_impact', 0)
        
        # ROI calculation
        safety_investment = financial_data.get('safety_investment', 1)
        roi = ((savings - incident_costs) / safety_investment * 100) if safety_investment > 0 else 0
        
        # Top risks
        top_risks = self._identify_top_risks(metrics)
        
        # Recommendations
        board_recommendations = self._generate_board_recommendations(metrics, financial_data)
        
        report = BoardReport(
            organization_id=organization_id,
            period_start=start_date,
            period_end=end_date,
            executive_summary=exec_summary,
            strategic_highlights=highlights,
            safety_score=metrics.safety_score,
            incident_reduction=incident_reduction,
            compliance_rate=metrics.compliance_rate,
            roi_safety_investment=roi,
            incident_costs=incident_costs,
            savings_from_prevention=savings,
            insurance_impact=insurance_impact,
            completed_initiatives=initiatives.get('completed', []),
            ongoing_initiatives=initiatives.get('ongoing', []),
            planned_initiatives=initiatives.get('planned', []),
            top_risks=top_risks,
            mitigation_strategies=self._generate_mitigation_strategies(top_risks),
            board_recommendations=board_recommendations,
            resource_requests=financial_data.get('resource_requests', []),
            generated_by="system"
        )
        
        return report
    
    def _calculate_metrics(
        self,
        incidents: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]],
        violations: List[Dict[str, Any]]
    ) -> ReportMetrics:
        """Calculate safety metrics"""
        
        total_incidents = len(incidents)
        
        # Count near misses
        near_misses = sum(1 for i in incidents if i.get('severity') == 'near_miss')
        
        # Count by severity
        lost_time = sum(1 for i in incidents if i.get('type') == 'lost_time')
        medical = sum(1 for i in incidents if i.get('type') == 'medical_treatment')
        first_aid = sum(1 for i in incidents if i.get('type') == 'first_aid')
        fatalities = sum(1 for i in incidents if i.get('severity') == 'fatal')
        
        # Calculate safety score (0-100)
        base_score = 100
        incident_penalty = total_incidents * 5
        violation_penalty = len(violations) * 2
        near_miss_penalty = near_misses * 1
        
        safety_score = max(0, base_score - incident_penalty - violation_penalty - near_miss_penalty)
        
        # Compliance rate
        total_checks = len(violations) + 100  # Assume 100 compliant checks
        compliance_rate = (100 / total_checks * 100) if total_checks > 0 else 0
        
        # PPE compliance
        ppe_violations = sum(1 for v in violations if 'ppe' in v.get('type', '').lower() or 'helmet' in v.get('type', '').lower())
        total_ppe_checks = len(violations) + 50
        ppe_compliance = ((total_ppe_checks - ppe_violations) / total_ppe_checks * 100) if total_ppe_checks > 0 else 0
        
        # Incident rate (per 100 workers)
        workers = 100  # Default
        incident_rate = (total_incidents / workers * 100)
        
        # High risk areas
        location_counts = defaultdict(int)
        for incident in incidents:
            location = incident.get('location', 'Unknown')
            location_counts[location] += 1
        
        high_risk_areas = [loc for loc, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
        
        # Top violations
        violation_types = defaultdict(int)
        for violation in violations:
            vtype = violation.get('type', 'Unknown')
            violation_types[vtype] += 1
        
        top_violations = [
            {"type": vtype, "count": count}
            for vtype, count in sorted(violation_types.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Trend direction
        recent_incidents = sum(1 for i in incidents if self._is_recent(i.get('date')))
        older_incidents = total_incidents - recent_incidents
        
        if recent_incidents < older_incidents * 0.7:
            trend = "improving"
        elif recent_incidents > older_incidents * 1.3:
            trend = "degrading"
        else:
            trend = "stable"
        
        metrics = ReportMetrics(
            total_incidents=total_incidents,
            total_near_misses=near_misses,
            total_violations=len(violations),
            total_alerts=len(alerts),
            safety_score=safety_score,
            compliance_rate=compliance_rate,
            ppe_compliance=ppe_compliance,
            incident_rate=incident_rate,
            lost_time_incidents=lost_time,
            first_aid_cases=first_aid,
            medical_treatments=medical,
            fatalities=fatalities,
            high_risk_areas=high_risk_areas,
            top_violations=top_violations,
            trend_direction=trend
        )
        
        return metrics
    
    def _is_recent(self, date_str: Optional[str]) -> bool:
        """Check if date is in recent half of period"""
        if not date_str:
            return False
        try:
            date = datetime.fromisoformat(date_str)
            cutoff = datetime.now() - timedelta(days=7)
            return date >= cutoff
        except:
            return False
    
    def _generate_executive_summary(
        self,
        metrics: ReportMetrics,
        start_date: datetime,
        end_date: datetime
    ) -> str:
        """Generate executive summary text"""
        
        period_days = (end_date - start_date).days
        
        summary = f"""This report covers a {period_days}-day period of safety performance. """
        
        if metrics.safety_score >= 80:
            summary += f"The organization achieved a strong safety score of {metrics.safety_score:.1f}/100, indicating effective safety management. "
        elif metrics.safety_score >= 60:
            summary += f"The organization achieved a moderate safety score of {metrics.safety_score:.1f}/100, with room for improvement. "
        else:
            summary += f"The organization's safety score of {metrics.safety_score:.1f}/100 requires immediate attention and corrective action. "
        
        summary += f"During this period, {metrics.total_incidents} incidents were recorded, including {metrics.total_near_misses} near misses. "
        
        if metrics.trend_direction == "improving":
            summary += "Safety performance shows positive improvement trends. "
        elif metrics.trend_direction == "degrading":
            summary += "Safety performance shows concerning degradation that requires immediate intervention. "
        else:
            summary += "Safety performance remains relatively stable. "
        
        summary += f"Compliance rate stands at {metrics.compliance_rate:.1f}%, with PPE compliance at {metrics.ppe_compliance:.1f}%."
        
        return summary
    
    def _identify_key_findings(
        self,
        incidents: List[Dict[str, Any]],
        violations: List[Dict[str, Any]],
        metrics: ReportMetrics
    ) -> List[str]:
        """Identify key findings from data"""
        
        findings = []
        
        # Critical incidents
        if metrics.fatalities > 0:
            findings.append(f"CRITICAL: {metrics.fatalities} fatal incident(s) occurred during this period")
        
        if metrics.lost_time_incidents > 0:
            findings.append(f"{metrics.lost_time_incidents} lost-time incidents resulted in worker absence")
        
        # High risk areas
        if metrics.high_risk_areas:
            findings.append(f"High-risk areas identified: {', '.join(metrics.high_risk_areas[:3])}")
        
        # Top violations
        if metrics.top_violations:
            top_type = metrics.top_violations[0]['type']
            top_count = metrics.top_violations[0]['count']
            findings.append(f"Most common violation: {top_type} ({top_count} occurrences)")
        
        # Compliance
        if metrics.compliance_rate < 90:
            findings.append(f"Compliance rate of {metrics.compliance_rate:.1f}% is below target (90%)")
        
        if metrics.ppe_compliance < 95:
            findings.append(f"PPE compliance at {metrics.ppe_compliance:.1f}% requires attention")
        
        # Trends
        if metrics.trend_direction == "improving":
            findings.append("Positive safety trend observed with declining incident rates")
        elif metrics.trend_direction == "degrading":
            findings.append("WARNING: Increasing incident trend requires immediate action")
        
        return findings
    
    def _generate_recommendations(
        self,
        metrics: ReportMetrics,
        incidents: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Based on safety score
        if metrics.safety_score < 70:
            recommendations.append("Implement comprehensive safety review and corrective action plan")
            recommendations.append("Increase safety training frequency to weekly sessions")
        
        # Based on incidents
        if metrics.total_incidents > 10:
            recommendations.append("Conduct root cause analysis for all incidents to identify systemic issues")
        
        # Based on compliance
        if metrics.compliance_rate < 90:
            recommendations.append("Enhance compliance monitoring with more frequent audits")
            recommendations.append("Provide refresher training on safety protocols")
        
        # Based on PPE
        if metrics.ppe_compliance < 95:
            recommendations.append("Implement strict PPE enforcement policy with consequences")
            recommendations.append("Review PPE availability and comfort to improve adoption")
        
        # High risk areas
        if metrics.high_risk_areas:
            recommendations.append(f"Deploy additional safety measures in high-risk areas: {', '.join(metrics.high_risk_areas[:3])}")
        
        # General
        recommendations.append("Continue monitoring safety metrics with weekly reviews")
        recommendations.append("Recognize and reward teams with excellent safety records")
        
        return recommendations
    
    def _create_safety_charts(
        self,
        incidents: List[Dict[str, Any]],
        alerts: List[Dict[str, Any]],
        violations: List[Dict[str, Any]]
    ) -> List[ReportChart]:
        """Create visualization charts"""
        
        charts = []
        
        # Incident trend chart
        incident_dates = defaultdict(int)
        for incident in incidents:
            date = incident.get('date', '')[:10]  # YYYY-MM-DD
            incident_dates[date] += 1
        
        sorted_dates = sorted(incident_dates.keys())
        charts.append(ReportChart(
            chart_type='line',
            title='Incident Trend Over Time',
            labels=sorted_dates,
            datasets=[{
                'label': 'Incidents',
                'data': [incident_dates[d] for d in sorted_dates],
                'borderColor': '#ef4444'
            }]
        ))
        
        # Severity distribution
        severity_counts = defaultdict(int)
        for incident in incidents:
            sev = incident.get('severity', 'unknown')
            severity_counts[sev] += 1
        
        charts.append(ReportChart(
            chart_type='pie',
            title='Incidents by Severity',
            labels=list(severity_counts.keys()),
            datasets=[{
                'data': list(severity_counts.values()),
                'backgroundColor': ['#ef4444', '#f97316', '#f59e0b', '#3b82f6']
            }]
        ))
        
        return charts
    
    def _create_safety_tables(
        self,
        incidents: List[Dict[str, Any]],
        violations: List[Dict[str, Any]]
    ) -> List[ReportTable]:
        """Create data tables"""
        
        tables = []
        
        # Recent incidents table
        recent_incidents = sorted(incidents, key=lambda x: x.get('date', ''), reverse=True)[:10]
        
        incident_rows = []
        for inc in recent_incidents:
            incident_rows.append([
                inc.get('id', 'N/A'),
                inc.get('date', 'N/A')[:10],
                inc.get('type', 'N/A'),
                inc.get('severity', 'N/A'),
                inc.get('location', 'N/A')
            ])
        
        tables.append(ReportTable(
            title='Recent Incidents',
            headers=['ID', 'Date', 'Type', 'Severity', 'Location'],
            rows=incident_rows
        ))
        
        return tables
    
    def _generate_board_summary(
        self,
        metrics: ReportMetrics,
        financial_data: Dict[str, Any]
    ) -> str:
        """Generate executive board summary"""
        
        summary = f"""The organization's safety performance this period demonstrates """
        
        if metrics.safety_score >= 85:
            summary += "excellence in safety management. "
        elif metrics.safety_score >= 70:
            summary += "satisfactory safety management with opportunities for improvement. "
        else:
            summary += "significant challenges requiring board attention. "
        
        savings = financial_data.get('prevention_savings', 0)
        costs = financial_data.get('incident_costs', 0)
        
        summary += f"Safety investments generated ${savings:,.0f} in prevented losses, "
        summary += f"while incident costs totaled ${costs:,.0f}. "
        
        if savings > costs:
            summary += "This represents a positive return on safety investment, reinforcing the business case for continued safety focus."
        else:
            summary += "Additional investment in preventive measures is recommended to improve financial outcomes."
        
        return summary
    
    def _identify_strategic_highlights(
        self,
        metrics: ReportMetrics,
        initiatives: Dict[str, Any]
    ) -> List[str]:
        """Identify strategic highlights"""
        
        highlights = []
        
        if metrics.trend_direction == "improving":
            highlights.append(f"Safety performance improved with {metrics.trend_direction} incident trend")
        
        completed = len(initiatives.get('completed', []))
        if completed > 0:
            highlights.append(f"Successfully completed {completed} safety initiatives")
        
        if metrics.compliance_rate >= 95:
            highlights.append(f"Achieved excellent compliance rate of {metrics.compliance_rate:.1f}%")
        
        if metrics.fatalities == 0:
            highlights.append("Zero fatalities maintained throughout the period")
        
        return highlights
    
    def _identify_top_risks(self, metrics: ReportMetrics) -> List[Dict[str, Any]]:
        """Identify top strategic risks"""
        
        risks = []
        
        if metrics.trend_direction == "degrading":
            risks.append({
                'name': 'Increasing Incident Rate',
                'likelihood': 'High',
                'impact': 'Critical',
                'mitigation': 'Immediate safety review and intervention'
            })
        
        if metrics.compliance_rate < 90:
            risks.append({
                'name': 'Compliance Deterioration',
                'likelihood': 'Medium',
                'impact': 'High',
                'mitigation': 'Enhanced monitoring and training'
            })
        
        if metrics.high_risk_areas:
            risks.append({
                'name': f'High-Risk Areas: {", ".join(metrics.high_risk_areas[:2])}',
                'likelihood': 'Medium',
                'impact': 'High',
                'mitigation': 'Deploy additional controls'
            })
        
        return risks
    
    def _generate_mitigation_strategies(self, risks: List[Dict[str, Any]]) -> List[str]:
        """Generate mitigation strategies"""
        return [risk['mitigation'] for risk in risks]
    
    def _generate_board_recommendations(
        self,
        metrics: ReportMetrics,
        financial_data: Dict[str, Any]
    ) -> List[str]:
        """Generate board-level recommendations"""
        
        recommendations = []
        
        if metrics.safety_score < 80:
            recommendations.append("Approve additional budget allocation for safety improvements")
        
        savings_ratio = financial_data.get('prevention_savings', 0) / max(financial_data.get('incident_costs', 1), 1)
        
        if savings_ratio > 2:
            recommendations.append("Continue current safety investment levels - demonstrating strong ROI")
        else:
            recommendations.append("Increase preventive safety investments to improve cost-benefit ratio")
        
        if metrics.trend_direction == "degrading":
            recommendations.append("Authorize executive safety task force to address declining trends")
        
        recommendations.append("Review and approve updated safety policies for board adoption")
        
        return recommendations
    
    def _generate_corrective_actions(self, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate corrective actions for violations"""
        
        actions = []
        
        for violation in violations[:10]:
            actions.append({
                'violation_id': violation.get('id'),
                'action': f"Corrective training required for {violation.get('type')}",
                'responsible': 'Safety Manager',
                'due_date': (datetime.now() + timedelta(days=7)).isoformat(),
                'status': 'pending'
            })
        
        return actions
    
    def _generate_compliance_recommendations(
        self,
        compliance_rate: float,
        violations: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate compliance recommendations"""
        
        recommendations = []
        
        if compliance_rate < 90:
            recommendations.append("Implement comprehensive compliance improvement program")
            recommendations.append("Increase audit frequency to identify gaps earlier")
        
        if len(violations) > 10:
            recommendations.append("Conduct root cause analysis of systemic compliance failures")
        
        recommendations.append("Update compliance training materials with recent findings")
        recommendations.append("Establish compliance scorecard with monthly tracking")
        
        return recommendations
