"""
HAZM TUWAIQ - Report Scheduler
Automated report generation and distribution
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from .models import ScheduledReport, ReportFrequency, GeneratedReport
from .report_builder import ReportBuilder
from .pdf_generator import PDFReportGenerator
from .excel_exporter import ExcelReportExporter


logger = logging.getLogger(__name__)


class ReportScheduler:
    """Schedule and automate report generation"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.builder = ReportBuilder()
        self.pdf_gen = PDFReportGenerator()
        self.excel_exp = ExcelReportExporter()
        self.scheduled_reports: Dict[str, ScheduledReport] = {}
    
    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        logger.info("📅 Report Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("📅 Report Scheduler stopped")
    
    def add_schedule(self, schedule: ScheduledReport) -> str:
        """Add a new scheduled report"""
        
        # Store schedule
        self.scheduled_reports[schedule.schedule_id] = schedule
        
        # Create trigger based on frequency
        trigger = self._create_trigger(schedule)
        
        # Add job to scheduler
        self.scheduler.add_job(
            func=self._generate_scheduled_report,
            trigger=trigger,
            id=schedule.schedule_id,
            args=[schedule.schedule_id],
            name=schedule.name,
            replace_existing=True
        )
        
        # Calculate next run
        next_run = self.scheduler.get_job(schedule.schedule_id).next_run_time
        schedule.next_run = next_run
        
        logger.info(f"📅 Scheduled report '{schedule.name}' - Next run: {next_run}")
        
        return schedule.schedule_id
    
    def remove_schedule(self, schedule_id: str) -> bool:
        """Remove a scheduled report"""
        
        if schedule_id in self.scheduled_reports:
            self.scheduler.remove_job(schedule_id)
            del self.scheduled_reports[schedule_id]
            logger.info(f"📅 Removed scheduled report: {schedule_id}")
            return True
        
        return False
    
    def update_schedule(self, schedule: ScheduledReport) -> bool:
        """Update existing schedule"""
        
        if schedule.schedule_id in self.scheduled_reports:
            # Remove old schedule
            self.remove_schedule(schedule.schedule_id)
            # Add new schedule
            self.add_schedule(schedule)
            return True
        
        return False
    
    def get_schedule(self, schedule_id: str) -> Optional[ScheduledReport]:
        """Get schedule by ID"""
        return self.scheduled_reports.get(schedule_id)
    
    def list_schedules(self, organization_id: Optional[str] = None) -> List[ScheduledReport]:
        """List all schedules, optionally filtered by organization"""
        
        schedules = list(self.scheduled_reports.values())
        
        if organization_id:
            schedules = [s for s in schedules if s.organization_id == organization_id]
        
        return schedules
    
    def _create_trigger(self, schedule: ScheduledReport) -> CronTrigger:
        """Create cron trigger from schedule"""
        
        hour, minute = map(int, schedule.time.split(':'))
        
        if schedule.frequency == ReportFrequency.DAILY:
            return CronTrigger(hour=hour, minute=minute)
        
        elif schedule.frequency == ReportFrequency.WEEKLY:
            day_of_week = schedule.day_of_week if schedule.day_of_week is not None else 0
            return CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute)
        
        elif schedule.frequency == ReportFrequency.MONTHLY:
            day = schedule.day_of_month if schedule.day_of_month is not None else 1
            return CronTrigger(day=day, hour=hour, minute=minute)
        
        elif schedule.frequency == ReportFrequency.QUARTERLY:
            # First day of quarter months (Jan, Apr, Jul, Oct)
            day = schedule.day_of_month if schedule.day_of_month is not None else 1
            return CronTrigger(month='1,4,7,10', day=day, hour=hour, minute=minute)
        
        elif schedule.frequency == ReportFrequency.ANNUAL:
            # January 1st
            return CronTrigger(month=1, day=1, hour=hour, minute=minute)
        
        else:
            # Default to daily
            return CronTrigger(hour=hour, minute=minute)
    
    def _generate_scheduled_report(self, schedule_id: str):
        """Generate report from schedule"""
        
        schedule = self.scheduled_reports.get(schedule_id)
        
        if not schedule or not schedule.is_active:
            logger.warning(f"⚠️ Schedule {schedule_id} not found or inactive")
            return
        
        try:
            logger.info(f"🔄 Generating scheduled report: {schedule.name}")
            
            # Calculate report period based on frequency
            end_date = datetime.now()
            
            if schedule.frequency == ReportFrequency.DAILY:
                start_date = end_date - timedelta(days=1)
            elif schedule.frequency == ReportFrequency.WEEKLY:
                start_date = end_date - timedelta(days=7)
            elif schedule.frequency == ReportFrequency.MONTHLY:
                start_date = end_date - timedelta(days=30)
            elif schedule.frequency == ReportFrequency.QUARTERLY:
                start_date = end_date - timedelta(days=90)
            elif schedule.frequency == ReportFrequency.ANNUAL:
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=1)
            
            # TODO: Fetch actual data from database
            # For now, use mock data
            incidents = []
            alerts = []
            violations = []
            
            # Build report
            report_data = self.builder.build_safety_report(
                organization_id=schedule.organization_id,
                organization_name="Organization Name",  # TODO: Fetch from DB
                start_date=start_date,
                end_date=end_date,
                incidents=incidents,
                alerts=alerts,
                violations=violations
            )
            
            # Generate file
            output_path = f"/tmp/reports/{schedule.report_type}_{schedule.organization_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if schedule.format.value == 'pdf':
                output_path += ".pdf"
                self.pdf_gen.generate_safety_report(report_data, output_path)
            elif schedule.format.value == 'excel':
                output_path += ".xlsx"
                self.excel_exp.generate_safety_report(report_data, output_path)
            
            # TODO: Send to recipients via email
            logger.info(f"✅ Generated report: {output_path}")
            
            # Update schedule
            schedule.last_run = datetime.now()
            next_job = self.scheduler.get_job(schedule_id)
            if next_job:
                schedule.next_run = next_job.next_run_time
            
        except Exception as e:
            logger.error(f"❌ Failed to generate scheduled report {schedule_id}: {e}")
    
    def run_now(self, schedule_id: str) -> bool:
        """Manually trigger a scheduled report"""
        
        if schedule_id in self.scheduled_reports:
            self._generate_scheduled_report(schedule_id)
            return True
        
        return False
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status and statistics"""
        
        running_jobs = self.scheduler.get_jobs()
        
        return {
            'running': self.scheduler.running,
            'total_schedules': len(self.scheduled_reports),
            'active_schedules': sum(1 for s in self.scheduled_reports.values() if s.is_active),
            'pending_jobs': len(running_jobs),
            'next_runs': [
                {
                    'schedule_id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in running_jobs
            ]
        }


# Global scheduler instance
report_scheduler = ReportScheduler()
