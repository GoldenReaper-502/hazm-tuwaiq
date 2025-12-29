"""
HAZM TUWAIQ - PDF Report Generator
Professional PDF reports with charts and tables using ReportLab
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from io import BytesIO
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

from .models import (
    ReportData, ReportChart, ReportTable, ReportMetrics,
    ComplianceReport, BoardReport
)


class PDFReportGenerator:
    """Generate professional PDF reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Create custom text styles"""
        # Arabic-friendly title
        self.styles.add(ParagraphStyle(
            name='ArabicTitle',
            parent=self.styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=24,
            textColor=colors.HexColor('#1e293b'),
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        # Arabic heading
        self.styles.add(ParagraphStyle(
            name='ArabicHeading',
            parent=self.styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=16,
            textColor=colors.HexColor('#3b82f6'),
            spaceAfter=12,
            spaceBefore=16
        ))
        
        # Arabic body
        self.styles.add(ParagraphStyle(
            name='ArabicBody',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            textColor=colors.HexColor('#334155'),
            alignment=TA_RIGHT,
            leading=16
        ))
        
        # Executive summary
        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=12,
            textColor=colors.HexColor('#475569'),
            alignment=TA_JUSTIFY,
            leading=18,
            spaceAfter=12
        ))
        
        # Metrics
        self.styles.add(ParagraphStyle(
            name='Metric',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=28,
            textColor=colors.HexColor('#10b981'),
            alignment=TA_CENTER
        ))
        
    def generate_safety_report(
        self,
        report_data: ReportData,
        output_path: str
    ) -> str:
        """Generate comprehensive safety report"""
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Cover Page
        story.extend(self._create_cover_page(report_data))
        story.append(PageBreak())
        
        # Executive Summary
        story.extend(self._create_executive_summary(report_data))
        story.append(PageBreak())
        
        # Key Metrics Dashboard
        story.extend(self._create_metrics_dashboard(report_data.metrics))
        story.append(Spacer(1, 0.5*inch))
        
        # Charts
        for chart in report_data.charts:
            story.extend(self._create_chart(chart))
            story.append(Spacer(1, 0.3*inch))
        
        # Tables
        for table in report_data.tables:
            story.extend(self._create_table(table))
            story.append(Spacer(1, 0.3*inch))
        
        # Incidents Analysis
        if report_data.incidents:
            story.append(PageBreak())
            story.extend(self._create_incidents_section(report_data.incidents))
        
        # Recommendations
        if report_data.recommendations:
            story.append(PageBreak())
            story.extend(self._create_recommendations(report_data.recommendations))
        
        # Footer with metadata
        story.extend(self._create_footer(report_data))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer,
                 onLaterPages=self._add_header_footer)
        
        return output_path
    
    def generate_compliance_report(
        self,
        compliance_data: ComplianceReport,
        output_path: str
    ) -> str:
        """Generate regulatory compliance report"""
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Title
        story.append(Paragraph(
            f"Compliance Report - {compliance_data.standard}",
            self.styles['ArabicTitle']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # Compliance Overview
        story.append(Paragraph("Compliance Overview", self.styles['ArabicHeading']))
        
        compliance_table = Table([
            ['Metric', 'Value'],
            ['Overall Compliance', f"{compliance_data.overall_compliance:.1f}%"],
            ['Compliant Items', str(compliance_data.compliant_items)],
            ['Non-Compliant Items', str(compliance_data.non_compliant_items)],
            ['Pending Items', str(compliance_data.pending_items)]
        ], colWidths=[3*inch, 2*inch])
        
        compliance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(compliance_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Violations
        if compliance_data.violations:
            story.append(Paragraph("Non-Compliance Items", self.styles['ArabicHeading']))
            
            violations_data = [['ID', 'Item', 'Severity', 'Status']]
            for v in compliance_data.violations[:10]:
                violations_data.append([
                    v.get('id', 'N/A'),
                    v.get('description', 'N/A')[:50],
                    v.get('severity', 'N/A'),
                    v.get('status', 'N/A')
                ])
            
            violations_table = Table(violations_data, colWidths=[1*inch, 3*inch, 1*inch, 1*inch])
            violations_table.setStyle(self._get_default_table_style())
            story.append(violations_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Recommendations
        if compliance_data.recommendations:
            story.append(PageBreak())
            story.append(Paragraph("Recommendations", self.styles['ArabicHeading']))
            for i, rec in enumerate(compliance_data.recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", self.styles['ArabicBody']))
                story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        return output_path
    
    def generate_board_report(
        self,
        board_data: BoardReport,
        output_path: str
    ) -> str:
        """Generate executive board report"""
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        
        # Executive Title Page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(
            "Executive Board Report",
            self.styles['ArabicTitle']
        ))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            f"Period: {board_data.period_start.strftime('%Y-%m-%d')} to {board_data.period_end.strftime('%Y-%m-%d')}",
            self.styles['ArabicBody']
        ))
        story.append(PageBreak())
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['ArabicHeading']))
        story.append(Paragraph(board_data.executive_summary, self.styles['ExecutiveSummary']))
        story.append(Spacer(1, 0.3*inch))
        
        # Strategic Highlights
        if board_data.strategic_highlights:
            story.append(Paragraph("Strategic Highlights", self.styles['ArabicHeading']))
            for highlight in board_data.strategic_highlights:
                story.append(Paragraph(f"• {highlight}", self.styles['ArabicBody']))
                story.append(Spacer(1, 0.1*inch))
            story.append(Spacer(1, 0.3*inch))
        
        # Key Performance Indicators
        story.append(Paragraph("Key Performance Indicators", self.styles['ArabicHeading']))
        
        kpi_table = Table([
            ['Metric', 'Value', 'Target', 'Status'],
            ['Safety Score', f"{board_data.safety_score:.1f}", '85.0', '✓' if board_data.safety_score >= 85 else '✗'],
            ['Incident Reduction', f"{board_data.incident_reduction:.1f}%", '10%', '✓' if board_data.incident_reduction >= 10 else '✗'],
            ['Compliance Rate', f"{board_data.compliance_rate:.1f}%", '95%', '✓' if board_data.compliance_rate >= 95 else '✗'],
        ], colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1*inch])
        
        kpi_table.setStyle(self._get_kpi_table_style())
        story.append(kpi_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Financial Impact
        story.append(Paragraph("Financial Impact", self.styles['ArabicHeading']))
        
        financial_table = Table([
            ['Item', 'Amount (USD)'],
            ['Incident Costs', f"${board_data.incident_costs:,.2f}"],
            ['Prevention Savings', f"${board_data.savings_from_prevention:,.2f}"],
            ['Insurance Impact', f"${board_data.insurance_impact:,.2f}"],
            ['Net Impact', f"${board_data.savings_from_prevention - board_data.incident_costs:,.2f}"]
        ], colWidths=[3*inch, 2*inch])
        
        financial_table.setStyle(self._get_default_table_style())
        story.append(financial_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Top Risks
        if board_data.top_risks:
            story.append(PageBreak())
            story.append(Paragraph("Top Strategic Risks", self.styles['ArabicHeading']))
            
            risks_data = [['Risk', 'Likelihood', 'Impact', 'Mitigation']]
            for risk in board_data.top_risks[:5]:
                risks_data.append([
                    risk.get('name', 'N/A'),
                    risk.get('likelihood', 'N/A'),
                    risk.get('impact', 'N/A'),
                    risk.get('mitigation', 'N/A')[:30]
                ])
            
            risks_table = Table(risks_data, colWidths=[2*inch, 1*inch, 1*inch, 2.5*inch])
            risks_table.setStyle(self._get_default_table_style())
            story.append(risks_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Board Recommendations
        if board_data.board_recommendations:
            story.append(Paragraph("Board Recommendations", self.styles['ArabicHeading']))
            for i, rec in enumerate(board_data.board_recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", self.styles['ArabicBody']))
                story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        return output_path
    
    def _create_cover_page(self, report_data: ReportData) -> List:
        """Create report cover page"""
        elements = []
        
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph(report_data.title, self.styles['ArabicTitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        if report_data.description:
            elements.append(Paragraph(report_data.description, self.styles['ArabicBody']))
            elements.append(Spacer(1, 0.5*inch))
        
        # Report details
        details = [
            ['Organization', report_data.organization_name],
            ['Period', f"{report_data.period_start.strftime('%Y-%m-%d')} to {report_data.period_end.strftime('%Y-%m-%d')}"],
            ['Generated', report_data.generated_at.strftime('%Y-%m-%d %H:%M')],
            ['Report ID', report_data.report_id]
        ]
        
        details_table = Table(details, colWidths=[2*inch, 3.5*inch])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#334155')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(details_table)
        
        return elements
    
    def _create_executive_summary(self, report_data: ReportData) -> List:
        """Create executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['ArabicHeading']))
        elements.append(Paragraph(report_data.executive_summary, self.styles['ExecutiveSummary']))
        elements.append(Spacer(1, 0.3*inch))
        
        if report_data.key_findings:
            elements.append(Paragraph("Key Findings", self.styles['ArabicHeading']))
            for finding in report_data.key_findings:
                elements.append(Paragraph(f"• {finding}", self.styles['ArabicBody']))
                elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_metrics_dashboard(self, metrics: ReportMetrics) -> List:
        """Create visual metrics dashboard"""
        elements = []
        
        elements.append(Paragraph("Key Safety Metrics", self.styles['ArabicHeading']))
        
        # Metrics grid
        metrics_data = [
            [
                Paragraph(f"<b>{metrics.safety_score:.1f}</b><br/>Safety Score", self.styles['ArabicBody']),
                Paragraph(f"<b>{metrics.total_incidents}</b><br/>Incidents", self.styles['ArabicBody']),
                Paragraph(f"<b>{metrics.compliance_rate:.1f}%</b><br/>Compliance", self.styles['ArabicBody'])
            ],
            [
                Paragraph(f"<b>{metrics.total_near_misses}</b><br/>Near Misses", self.styles['ArabicBody']),
                Paragraph(f"<b>{metrics.total_violations}</b><br/>Violations", self.styles['ArabicBody']),
                Paragraph(f"<b>{metrics.ppe_compliance:.1f}%</b><br/>PPE Compliance", self.styles['ArabicBody'])
            ]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 2*inch, 2*inch])
        metrics_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        elements.append(metrics_table)
        
        return elements
    
    def _create_chart(self, chart: ReportChart) -> List:
        """Create chart visualization"""
        elements = []
        
        elements.append(Paragraph(chart.title, self.styles['ArabicHeading']))
        
        # Create drawing
        drawing = Drawing(400, 200)
        
        if chart.chart_type == 'bar':
            bc = VerticalBarChart()
            bc.x = 50
            bc.y = 50
            bc.height = 125
            bc.width = 300
            bc.data = [chart.datasets[0]['data']]
            bc.categoryAxis.categoryNames = chart.labels
            bc.valueAxis.valueMin = 0
            bc.bars[0].fillColor = colors.HexColor('#3b82f6')
            drawing.add(bc)
        
        elif chart.chart_type == 'line':
            lc = HorizontalLineChart()
            lc.x = 50
            lc.y = 50
            lc.height = 125
            lc.width = 300
            lc.data = [chart.datasets[0]['data']]
            lc.categoryAxis.categoryNames = chart.labels
            lc.lines[0].strokeColor = colors.HexColor('#10b981')
            drawing.add(lc)
        
        elements.append(drawing)
        
        return elements
    
    def _create_table(self, table: ReportTable) -> List:
        """Create data table"""
        elements = []
        
        elements.append(Paragraph(table.title, self.styles['ArabicHeading']))
        
        # Prepare table data
        data = [table.headers] + table.rows
        
        if table.totals:
            data.append(['Total'] + table.totals[1:])
        
        pdf_table = Table(data)
        pdf_table.setStyle(self._get_default_table_style())
        
        elements.append(pdf_table)
        
        return elements
    
    def _create_incidents_section(self, incidents: List[Dict[str, Any]]) -> List:
        """Create incidents analysis section"""
        elements = []
        
        elements.append(Paragraph("Incident Analysis", self.styles['ArabicHeading']))
        
        incidents_data = [['Date', 'Type', 'Severity', 'Location', 'Status']]
        
        for incident in incidents[:20]:
            incidents_data.append([
                incident.get('date', 'N/A')[:10],
                incident.get('type', 'N/A'),
                incident.get('severity', 'N/A'),
                incident.get('location', 'N/A')[:20],
                incident.get('status', 'N/A')
            ])
        
        incidents_table = Table(incidents_data, colWidths=[1.2*inch, 1.5*inch, 1*inch, 1.5*inch, 1*inch])
        incidents_table.setStyle(self._get_default_table_style())
        
        elements.append(incidents_table)
        
        return elements
    
    def _create_recommendations(self, recommendations: List[str]) -> List:
        """Create recommendations section"""
        elements = []
        
        elements.append(Paragraph("Recommendations", self.styles['ArabicHeading']))
        
        for i, rec in enumerate(recommendations, 1):
            elements.append(Paragraph(f"{i}. {rec}", self.styles['ArabicBody']))
            elements.append(Spacer(1, 0.15*inch))
        
        return elements
    
    def _create_footer(self, report_data: ReportData) -> List:
        """Create report footer"""
        elements = []
        
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(
            f"<i>This report was automatically generated by HAZM TUWAIQ Safety Platform</i>",
            self.styles['ArabicBody']
        ))
        
        return elements
    
    def _get_default_table_style(self) -> TableStyle:
        """Get default table styling"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
        ])
    
    def _get_kpi_table_style(self) -> TableStyle:
        """Get KPI table styling"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ])
    
    def _add_header_footer(self, canvas, doc):
        """Add header and footer to pages"""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.HexColor('#3b82f6'))
        canvas.drawString(2*cm, A4[1] - 1.5*cm, "HAZM TUWAIQ Safety Platform")
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(2*cm, 1*cm, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        canvas.drawRightString(A4[0] - 2*cm, 1*cm, f"Page {doc.page}")
        
        canvas.restoreState()
