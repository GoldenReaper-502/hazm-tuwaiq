"""
HAZM TUWAIQ - Report Models
Data structures for comprehensive reporting system
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid


class ReportType(str, Enum):
    """Report types"""
    SAFETY_SUMMARY = "safety_summary"
    INCIDENT_ANALYSIS = "incident_analysis"
    COMPLIANCE_AUDIT = "compliance_audit"
    BOARD_EXECUTIVE = "board_executive"
    REGULATORY_SUBMISSION = "regulatory_submission"
    DAILY_OPERATIONS = "daily_operations"
    WEEKLY_SUMMARY = "weekly_summary"
    MONTHLY_REVIEW = "monthly_review"
    QUARTERLY_ASSESSMENT = "quarterly_assessment"
    ANNUAL_REPORT = "annual_report"
    CUSTOM = "custom"


class ReportFormat(str, Enum):
    """Output formats"""
    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"
    CSV = "csv"
    HTML = "html"


class ReportStatus(str, Enum):
    """Report generation status"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    SCHEDULED = "scheduled"


class ReportFrequency(str, Enum):
    """Scheduling frequency"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class ReportSection(BaseModel):
    """Report section configuration"""
    section_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    type: str  # chart, table, text, metrics, summary
    data_source: str
    filters: Optional[Dict[str, Any]] = None
    visualization: Optional[Dict[str, Any]] = None
    order: int = 0
    enabled: bool = True


class ReportTemplate(BaseModel):
    """Report template definition"""
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    report_type: ReportType
    description: Optional[str] = None
    sections: List[ReportSection] = []
    organization_id: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    is_public: bool = False
    metadata: Optional[Dict[str, Any]] = None


class ReportRequest(BaseModel):
    """Report generation request"""
    report_type: ReportType
    format: ReportFormat = ReportFormat.PDF
    title: str
    description: Optional[str] = None
    organization_id: str
    start_date: datetime
    end_date: datetime
    filters: Optional[Dict[str, Any]] = None
    template_id: Optional[str] = None
    sections: Optional[List[str]] = None  # Section IDs to include
    recipients: Optional[List[str]] = None  # Email recipients
    metadata: Optional[Dict[str, Any]] = None


class ReportMetrics(BaseModel):
    """Key metrics for reports"""
    total_incidents: int = 0
    total_near_misses: int = 0
    total_violations: int = 0
    total_alerts: int = 0
    safety_score: float = 0.0
    compliance_rate: float = 0.0
    ppe_compliance: float = 0.0
    incident_rate: float = 0.0  # per 100 workers
    lost_time_incidents: int = 0
    first_aid_cases: int = 0
    medical_treatments: int = 0
    fatalities: int = 0
    high_risk_areas: List[str] = []
    top_violations: List[Dict[str, Any]] = []
    trend_direction: str = "stable"  # improving, stable, degrading
    
    
class ReportChart(BaseModel):
    """Chart data for visualization"""
    chart_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chart_type: str  # line, bar, pie, scatter, heatmap
    title: str
    labels: List[str]
    datasets: List[Dict[str, Any]]
    options: Optional[Dict[str, Any]] = None


class ReportTable(BaseModel):
    """Table data for reports"""
    table_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    headers: List[str]
    rows: List[List[Any]]
    totals: Optional[List[Any]] = None
    formatting: Optional[Dict[str, Any]] = None


class ReportData(BaseModel):
    """Complete report data"""
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    report_type: ReportType
    format: ReportFormat
    title: str
    description: Optional[str] = None
    organization_id: str
    organization_name: str
    period_start: datetime
    period_end: datetime
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_by: str
    
    # Executive Summary
    executive_summary: str = ""
    key_findings: List[str] = []
    recommendations: List[str] = []
    
    # Metrics
    metrics: ReportMetrics = Field(default_factory=ReportMetrics)
    
    # Visualizations
    charts: List[ReportChart] = []
    tables: List[ReportTable] = []
    
    # Additional data
    incidents: List[Dict[str, Any]] = []
    violations: List[Dict[str, Any]] = []
    compliance_data: Dict[str, Any] = {}
    predictions: Optional[Dict[str, Any]] = None
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = None
    

class GeneratedReport(BaseModel):
    """Generated report record"""
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    report_type: ReportType
    format: ReportFormat
    title: str
    organization_id: str
    file_path: str
    file_size: int  # bytes
    status: ReportStatus = ReportStatus.COMPLETED
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_by: str
    download_url: str
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ScheduledReport(BaseModel):
    """Scheduled report configuration"""
    schedule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    report_type: ReportType
    format: ReportFormat
    organization_id: str
    frequency: ReportFrequency
    time: str  # HH:MM format
    day_of_week: Optional[int] = None  # 0-6 for weekly
    day_of_month: Optional[int] = None  # 1-31 for monthly
    recipients: List[str]  # Email addresses
    template_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    is_active: bool = True
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class ComplianceReport(BaseModel):
    """Regulatory compliance report"""
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    regulatory_body: str  # OSHA, ISO, etc.
    standard: str  # OSHA 1910, ISO 45001, etc.
    period_start: datetime
    period_end: datetime
    
    # Compliance metrics
    overall_compliance: float  # 0-100
    compliant_items: int
    non_compliant_items: int
    pending_items: int
    
    # Findings
    violations: List[Dict[str, Any]]
    corrective_actions: List[Dict[str, Any]]
    recommendations: List[str]
    
    # Certifications
    certifications: List[Dict[str, Any]] = []
    audits: List[Dict[str, Any]] = []
    
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_by: str
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    
    metadata: Optional[Dict[str, Any]] = None


class BoardReport(BaseModel):
    """Executive board report"""
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    organization_id: str
    period_start: datetime
    period_end: datetime
    
    # Executive Summary
    executive_summary: str
    strategic_highlights: List[str]
    
    # Key Metrics
    safety_score: float
    incident_reduction: float  # percentage
    compliance_rate: float
    roi_safety_investment: float
    
    # Financial Impact
    incident_costs: float
    savings_from_prevention: float
    insurance_impact: float
    
    # Strategic Initiatives
    completed_initiatives: List[Dict[str, Any]]
    ongoing_initiatives: List[Dict[str, Any]]
    planned_initiatives: List[Dict[str, Any]]
    
    # Risk Assessment
    top_risks: List[Dict[str, Any]]
    mitigation_strategies: List[str]
    
    # Recommendations
    board_recommendations: List[str]
    resource_requests: List[Dict[str, Any]]
    
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_by: str
    
    metadata: Optional[Dict[str, Any]] = None


class ReportAnalytics(BaseModel):
    """Report generation analytics"""
    total_reports: int = 0
    reports_by_type: Dict[str, int] = {}
    reports_by_format: Dict[str, int] = {}
    reports_this_month: int = 0
    reports_this_week: int = 0
    avg_generation_time: float = 0.0  # seconds
    most_requested_type: Optional[str] = None
    scheduled_reports: int = 0
    failed_reports: int = 0
    storage_used: int = 0  # bytes
