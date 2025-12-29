"""
HAZM TUWAIQ - Reports API
Comprehensive reporting endpoints with PDF/Excel export
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os
import uuid

from .models import (
    ReportRequest, ReportType, ReportFormat, ReportStatus,
    GeneratedReport, ScheduledReport, ReportFrequency,
    ReportTemplate, ReportSection, ReportAnalytics,
    ComplianceReport, BoardReport
)
from .report_builder import ReportBuilder
from .pdf_generator import PDFReportGenerator
from .excel_exporter import ExcelReportExporter
from .scheduler import report_scheduler


router = APIRouter()

# In-memory databases
GENERATED_REPORTS_DB: Dict[str, GeneratedReport] = {}
SCHEDULED_REPORTS_DB: Dict[str, ScheduledReport] = {}
TEMPLATES_DB: Dict[str, ReportTemplate] = {}

# Report generators
report_builder = ReportBuilder()
pdf_generator = PDFReportGenerator()
excel_exporter = ExcelReportExporter()

# Ensure reports directory exists
REPORTS_DIR = "/tmp/reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


def create_response(success: bool, message: str, data: Any = None) -> Dict:
    """Create unified API response"""
    response = {
        "success": success,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    if data is not None:
        response["data"] = data
    return response


# ═══════════════════════════════════════════════════════════════
# REPORT GENERATION
# ═══════════════════════════════════════════════════════════════

@router.post("/generate")
async def generate_report(request: ReportRequest):
    """
    Generate a new report (PDF/Excel)
    
    Supports multiple report types:
    - safety_summary: Comprehensive safety performance
    - incident_analysis: Detailed incident breakdown
    - compliance_audit: Regulatory compliance status
    - board_executive: Executive board summary
    - daily/weekly/monthly/quarterly/annual: Period reports
    """
    
    try:
        # TODO: Fetch real data from databases
        # Mock data for demonstration
        incidents = []
        alerts = []
        violations = []
        
        # Build report data
        report_data = report_builder.build_safety_report(
            organization_id=request.organization_id,
            organization_name="Sample Organization",
            start_date=request.start_date,
            end_date=request.end_date,
            incidents=incidents,
            alerts=alerts,
            violations=violations
        )
        
        # Generate filename
        filename = f"{request.report_type.value}_{request.organization_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate file based on format
        if request.format == ReportFormat.PDF:
            filepath = os.path.join(REPORTS_DIR, f"{filename}.pdf")
            pdf_generator.generate_safety_report(report_data, filepath)
        
        elif request.format == ReportFormat.EXCEL:
            filepath = os.path.join(REPORTS_DIR, f"{filename}.xlsx")
            excel_exporter.generate_safety_report(report_data, filepath)
        
        elif request.format == ReportFormat.JSON:
            import json
            filepath = os.path.join(REPORTS_DIR, f"{filename}.json")
            with open(filepath, 'w') as f:
                json.dump(report_data.dict(), f, default=str, indent=2)
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
        
        # Get file size
        file_size = os.path.getsize(filepath)
        
        # Create generated report record
        generated = GeneratedReport(
            report_id=str(uuid.uuid4()),
            report_type=request.report_type,
            format=request.format,
            title=request.title,
            organization_id=request.organization_id,
            file_path=filepath,
            file_size=file_size,
            generated_by="system",
            download_url=f"/api/reports/download/{os.path.basename(filepath)}",
            expires_at=datetime.now() + timedelta(days=30)
        )
        
        GENERATED_REPORTS_DB[generated.report_id] = generated
        
        return create_response(
            success=True,
            message="Report generated successfully",
            data=generated.dict()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/reports")
async def list_reports(
    organization_id: Optional[str] = Query(None),
    report_type: Optional[ReportType] = Query(None),
    format: Optional[ReportFormat] = Query(None),
    limit: int = Query(50, ge=1, le=100)
):
    """List all generated reports with filters"""
    
    reports = list(GENERATED_REPORTS_DB.values())
    
    # Apply filters
    if organization_id:
        reports = [r for r in reports if r.organization_id == organization_id]
    
    if report_type:
        reports = [r for r in reports if r.report_type == report_type]
    
    if format:
        reports = [r for r in reports if r.format == format]
    
    # Sort by generation time (newest first)
    reports = sorted(reports, key=lambda x: x.generated_at, reverse=True)
    
    # Limit results
    reports = reports[:limit]
    
    return create_response(
        success=True,
        message=f"Retrieved {len(reports)} reports",
        data=[r.dict() for r in reports]
    )


@router.get("/reports/{report_id}")
async def get_report(report_id: str):
    """Get report details by ID"""
    
    report = GENERATED_REPORTS_DB.get(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return create_response(
        success=True,
        message="Report retrieved successfully",
        data=report.dict()
    )


@router.delete("/reports/{report_id}")
async def delete_report(report_id: str):
    """Delete a generated report"""
    
    report = GENERATED_REPORTS_DB.get(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Delete file
    if os.path.exists(report.file_path):
        os.remove(report.file_path)
    
    # Delete record
    del GENERATED_REPORTS_DB[report_id]
    
    return create_response(
        success=True,
        message="Report deleted successfully"
    )


# ═══════════════════════════════════════════════════════════════
# SCHEDULED REPORTS
# ═══════════════════════════════════════════════════════════════

@router.post("/schedules")
async def create_schedule(schedule: ScheduledReport):
    """Create a new scheduled report"""
    
    try:
        # Add to scheduler
        schedule_id = report_scheduler.add_schedule(schedule)
        
        # Store in database
        SCHEDULED_REPORTS_DB[schedule_id] = schedule
        
        return create_response(
            success=True,
            message="Report schedule created successfully",
            data=schedule.dict()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create schedule: {str(e)}")


@router.get("/schedules")
async def list_schedules(organization_id: Optional[str] = Query(None)):
    """List all scheduled reports"""
    
    schedules = report_scheduler.list_schedules(organization_id)
    
    return create_response(
        success=True,
        message=f"Retrieved {len(schedules)} schedules",
        data=[s.dict() for s in schedules]
    )


@router.get("/schedules/{schedule_id}")
async def get_schedule(schedule_id: str):
    """Get schedule details"""
    
    schedule = report_scheduler.get_schedule(schedule_id)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return create_response(
        success=True,
        message="Schedule retrieved successfully",
        data=schedule.dict()
    )


@router.put("/schedules/{schedule_id}")
async def update_schedule(schedule_id: str, schedule: ScheduledReport):
    """Update existing schedule"""
    
    schedule.schedule_id = schedule_id
    
    success = report_scheduler.update_schedule(schedule)
    
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    SCHEDULED_REPORTS_DB[schedule_id] = schedule
    
    return create_response(
        success=True,
        message="Schedule updated successfully",
        data=schedule.dict()
    )


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: str):
    """Delete a scheduled report"""
    
    success = report_scheduler.remove_schedule(schedule_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    if schedule_id in SCHEDULED_REPORTS_DB:
        del SCHEDULED_REPORTS_DB[schedule_id]
    
    return create_response(
        success=True,
        message="Schedule deleted successfully"
    )


@router.post("/schedules/{schedule_id}/run")
async def run_schedule_now(schedule_id: str):
    """Manually trigger a scheduled report"""
    
    success = report_scheduler.run_now(schedule_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return create_response(
        success=True,
        message="Report generation triggered successfully"
    )


# ═══════════════════════════════════════════════════════════════
# REPORT TEMPLATES
# ═══════════════════════════════════════════════════════════════

@router.post("/templates")
async def create_template(template: ReportTemplate):
    """Create custom report template"""
    
    TEMPLATES_DB[template.template_id] = template
    
    return create_response(
        success=True,
        message="Template created successfully",
        data=template.dict()
    )


@router.get("/templates")
async def list_templates(
    organization_id: Optional[str] = Query(None),
    report_type: Optional[ReportType] = Query(None)
):
    """List report templates"""
    
    templates = list(TEMPLATES_DB.values())
    
    if organization_id:
        templates = [t for t in templates if t.organization_id == organization_id or t.is_public]
    
    if report_type:
        templates = [t for t in templates if t.report_type == report_type]
    
    return create_response(
        success=True,
        message=f"Retrieved {len(templates)} templates",
        data=[t.dict() for t in templates]
    )


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get template by ID"""
    
    template = TEMPLATES_DB.get(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return create_response(
        success=True,
        message="Template retrieved successfully",
        data=template.dict()
    )


@router.delete("/templates/{template_id}")
async def delete_template(template_id: str):
    """Delete a template"""
    
    if template_id not in TEMPLATES_DB:
        raise HTTPException(status_code=404, detail="Template not found")
    
    del TEMPLATES_DB[template_id]
    
    return create_response(
        success=True,
        message="Template deleted successfully"
    )


# ═══════════════════════════════════════════════════════════════
# SPECIALIZED REPORTS
# ═══════════════════════════════════════════════════════════════

@router.post("/compliance")
async def generate_compliance_report(
    organization_id: str,
    regulatory_body: str,
    standard: str,
    start_date: datetime,
    end_date: datetime
):
    """Generate regulatory compliance report"""
    
    try:
        # TODO: Fetch compliance data
        compliance_data = {
            'total_items': 100,
            'compliant_items': 85,
            'non_compliant_items': 10,
            'pending_items': 5,
            'violations': []
        }
        
        compliance_report = report_builder.build_compliance_report(
            organization_id=organization_id,
            regulatory_body=regulatory_body,
            standard=standard,
            start_date=start_date,
            end_date=end_date,
            compliance_data=compliance_data
        )
        
        # Generate PDF
        filename = f"compliance_{organization_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(REPORTS_DIR, filename)
        
        pdf_generator.generate_compliance_report(compliance_report, filepath)
        
        return create_response(
            success=True,
            message="Compliance report generated successfully",
            data={
                'report_id': str(uuid.uuid4()),
                'file_path': filepath,
                'download_url': f"/api/reports/download/{filename}"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate compliance report: {str(e)}")


@router.post("/board")
async def generate_board_report(
    organization_id: str,
    start_date: datetime,
    end_date: datetime
):
    """Generate executive board report"""
    
    try:
        # TODO: Fetch actual data
        # Mock metrics
        from .models import ReportMetrics
        metrics = ReportMetrics(
            total_incidents=15,
            safety_score=87.5,
            compliance_rate=94.2
        )
        
        financial_data = {
            'incident_costs': 50000,
            'prevention_savings': 150000,
            'insurance_impact': -20000,
            'safety_investment': 100000,
            'previous_incidents': 25
        }
        
        initiatives = {
            'completed': [
                {'name': 'New Safety Training Program', 'impact': 'High'},
                {'name': 'PPE Equipment Upgrade', 'impact': 'Medium'}
            ],
            'ongoing': [
                {'name': 'AI Safety Monitoring Deployment', 'progress': '75%'}
            ],
            'planned': [
                {'name': 'Predictive Maintenance System', 'start_date': '2025-Q2'}
            ]
        }
        
        board_report = report_builder.build_board_report(
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date,
            metrics=metrics,
            financial_data=financial_data,
            initiatives=initiatives
        )
        
        # Generate PDF
        filename = f"board_report_{organization_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(REPORTS_DIR, filename)
        
        pdf_generator.generate_board_report(board_report, filepath)
        
        return create_response(
            success=True,
            message="Board report generated successfully",
            data={
                'report_id': str(uuid.uuid4()),
                'file_path': filepath,
                'download_url': f"/api/reports/download/{filename}"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate board report: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# ANALYTICS & STATISTICS
# ═══════════════════════════════════════════════════════════════

@router.get("/analytics")
async def get_report_analytics():
    """Get reporting analytics and statistics"""
    
    reports = list(GENERATED_REPORTS_DB.values())
    
    # Calculate statistics
    total_reports = len(reports)
    
    reports_by_type = {}
    for report in reports:
        rtype = report.report_type.value
        reports_by_type[rtype] = reports_by_type.get(rtype, 0) + 1
    
    reports_by_format = {}
    for report in reports:
        fmt = report.format.value
        reports_by_format[fmt] = reports_by_format.get(fmt, 0) + 1
    
    # Recent reports
    now = datetime.now()
    reports_this_week = sum(1 for r in reports if (now - r.generated_at).days <= 7)
    reports_this_month = sum(1 for r in reports if (now - r.generated_at).days <= 30)
    
    # Storage
    total_storage = sum(r.file_size for r in reports)
    
    analytics = ReportAnalytics(
        total_reports=total_reports,
        reports_by_type=reports_by_type,
        reports_by_format=reports_by_format,
        reports_this_month=reports_this_month,
        reports_this_week=reports_this_week,
        scheduled_reports=len(SCHEDULED_REPORTS_DB),
        storage_used=total_storage,
        most_requested_type=max(reports_by_type.items(), key=lambda x: x[1])[0] if reports_by_type else None
    )
    
    return create_response(
        success=True,
        message="Analytics retrieved successfully",
        data=analytics.dict()
    )


@router.get("/scheduler/status")
async def get_scheduler_status():
    """Get report scheduler status"""
    
    status = report_scheduler.get_scheduler_status()
    
    return create_response(
        success=True,
        message="Scheduler status retrieved successfully",
        data=status
    )


# ═══════════════════════════════════════════════════════════════
# QUICK EXPORTS
# ═══════════════════════════════════════════════════════════════

@router.post("/export/excel")
async def quick_excel_export(
    data: List[Dict[str, Any]],
    headers: List[str],
    filename: str = "export"
):
    """Quick data export to Excel"""
    
    try:
        filepath = os.path.join(REPORTS_DIR, f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        
        excel_exporter.generate_quick_export(data, headers, filepath)
        
        return create_response(
            success=True,
            message="Excel export completed successfully",
            data={
                'file_path': filepath,
                'download_url': f"/api/reports/download/{os.path.basename(filepath)}"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel export failed: {str(e)}")


# Initialize scheduler on module load
report_scheduler.start()
