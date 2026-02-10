"""
Scheduler Service - Handles background scheduled tasks.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
import threading
import time
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import SessionLocal
from app.services.quota_service import QuotaService
from app.services.metrics_service import MetricsService
from app.services.cleanup_service import CleanupService
from app.services.alerting_service import AlertingService
from app.config import QDRANT_URL, QDRANT_API_KEY
from qdrant_client import QdrantClient

from app.models.gmail import GmailSchedule, GmailRecipient, GmailExecutionLog
from app.services.gmail_auth_service import GmailAuthService
from app.services.gmail_fetch_service import GmailFetchService
from app.services.gmail_rag_service import GmailRAGService

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for running scheduled background tasks."""
    
    def __init__(self):
        """Initialize scheduler service."""
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    def start(self):
        """Start the scheduler in a background thread."""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop."""
        last_hourly = datetime.utcnow()
        last_daily = datetime.utcnow()
        last_monthly = datetime.utcnow()
        last_gmail_check = datetime.utcnow() - timedelta(minutes=1) # Run immediately on start
        
        while self.running:
            try:
                now = datetime.utcnow()
                
                # Run Gmail tasks (every minute)
                if (now - last_gmail_check).total_seconds() >= 60:
                    self._run_gmail_tasks()
                    last_gmail_check = now

                # Run hourly tasks (every hour)
                if (now - last_hourly).total_seconds() >= 3600:
                    self._run_hourly_tasks()
                    last_hourly = now
                
                # Run daily tasks (at 2 AM UTC)
                if now.hour == 2 and (now - last_daily).total_seconds() >= 86400:
                    self._run_daily_tasks()
                    last_daily = now
                
                # Run monthly tasks (1st of month at 3 AM UTC)
                if now.day == 1 and now.hour == 3 and (now - last_monthly).total_seconds() >= 86400:
                    self._run_monthly_tasks()
                    last_monthly = now
                
                # Sleep for small interval to prevent high CPU usage, but keep responsive
                time.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Wait a minute before retrying

    def _run_gmail_tasks(self):
        """Check for and execute due Gmail sync schedules."""
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            # Find enabled schedules that are due (next_run <= now OR next_run is null)
            # Default to running now if next_run is null (freshly created schedules usually set next_run, but safety check)
            due_schedules = db.query(GmailSchedule).filter(
                GmailSchedule.enabled == True,
                (GmailSchedule.next_run <= now) | (GmailSchedule.next_run == None)
            ).all()

            if due_schedules:
                logger.info(f"Found {len(due_schedules)} due Gmail schedules")

            for schedule in due_schedules:
                self._execute_gmail_schedule(db, schedule)

        except Exception as e:
            logger.error(f"Error checking Gmail tasks: {e}")
        finally:
            db.close()

    def execute_schedule_now(self, db: Session, schedule: GmailSchedule):
        """Manually trigger the execution of a Gmail schedule."""
        self._execute_gmail_schedule(db, schedule)

    def _execute_gmail_schedule(self, db: Session, schedule: GmailSchedule):
        """Execute a single Gmail sync schedule."""
        log = GmailExecutionLog(
            tenant_id=schedule.tenant_id,
            user_id=schedule.user_id,
            schedule_id=schedule.id,
            execution_type='scheduled',
            status='running',
            start_time=datetime.utcnow()
        )
        db.add(log)
        db.commit() # Save 'running' state
        
        try:
            logger.info(f"Executing Gmail schedule {schedule.name} ({schedule.id}) for tenant {schedule.tenant_id}")
            
            # 1. Authenticate
            auth_service = GmailAuthService(db)
            creds = auth_service.get_credentials(schedule.tenant_id, schedule.user_id)
            
            if not creds:
                raise ValueError("Gmail credentials not found or invalid for tenant")

            # 2. Setup Services
            fetch_service = GmailFetchService(creds)
            rag_service = GmailRAGService(db, schedule.tenant_id, schedule.user_id)
            
            total_processed = 0
            
            # 3. Process each recipient
            recipient_ids = schedule.recipient_ids or []
            for recipient_id in recipient_ids:
                recipient = db.query(GmailRecipient).filter(
                    GmailRecipient.id == recipient_id,
                    GmailRecipient.enabled == True
                ).first()
                
                if not recipient:
                    continue
                
                # Build query (e.g., "from:user@example.com is:unread")
                # Using simple filter for now. Can be enhanced with schedule config (e.g., newer_than:2d)
                query = f"from:{recipient.email_address}"
                if recipient.filters:
                    # Append custom filters if any
                    # This is rudimentary; implies filters dict has a 'query_string' or similar
                    # For MVP, let's just use email address
                    pass
                
                # Fetch
                emails = fetch_service.fetch_emails(query=query, max_results=20) # Limit for safety in MVP
                
                # RAG Process
                count = rag_service.process_emails_to_kb(emails)
                total_processed += count
                
            # 4. Update Log & Schedule
            log.status = 'success'
            log.emails_processed = total_processed
            
            # Update next_run based on schedule_type
            self._update_next_run(schedule)

        except Exception as e:
            logger.error(f"Gmail execution failed for schedule {schedule.id}: {e}")
            log.status = 'failed'
            log.errors = {"error": str(e)}
            # Still update next run to avoid infinite retry loop
            self._update_next_run(schedule)
            
        finally:
            log.end_time = datetime.utcnow()
            if log.start_time:
                 log.duration_ms = int((log.end_time - log.start_time).total_seconds() * 1000)
            db.commit()

    def _update_next_run(self, schedule: GmailSchedule):
        """Calculate and update the next run time for a schedule."""
        now = datetime.utcnow()
        if schedule.schedule_type == 'interval':
            minutes = int(schedule.schedule_config.get('minutes', 60))
            schedule.next_run = now + timedelta(minutes=minutes)
        elif schedule.schedule_type == 'daily':
            # Run same time tomorrow
            # Simplification: just add 24 hours to current execution time
            schedule.next_run = now + timedelta(days=1)
        # Add other types as needed
        else:
            # Default fallback
            schedule.next_run = now + timedelta(hours=1)
            
        schedule.last_run = now

    def _run_hourly_tasks(self):
        """Run tasks that should execute every hour."""
        logger.info("Running hourly tasks")
        db = SessionLocal()
        
        try:
            # 1. Aggregate hourly metrics for all tenants
            self._aggregate_hourly_metrics(db)
            
            # 2. Check for alerts
            self._check_tenant_alerts(db)
            
        except Exception as e:
            logger.error(f"Error in hourly tasks: {e}")
        finally:
            db.close()
    
    def _run_daily_tasks(self):
        """Run tasks that should execute daily."""
        logger.info("Running daily tasks")
        db = SessionLocal()
        
        try:
            # 1. Aggregate daily metrics
            self._aggregate_daily_metrics(db)
            
            # 2. Reset daily quotas
            self._reset_daily_quotas(db)
            
            # 3. Run cleanup tasks
            cleanup_service = CleanupService(db, self.qdrant_client)
            cleanup_results = cleanup_service.run_daily_cleanup()
            logger.info(f"Daily cleanup results: {cleanup_results}")
            
            # 4. Clean up old metrics (keep 90 days)
            metrics_service = MetricsService(db)
            deleted = metrics_service.cleanup_old_metrics(retention_days=90)
            logger.info(f"Cleaned up {deleted} old metric records")
            
        except Exception as e:
            logger.error(f"Error in daily tasks: {e}")
        finally:
            db.close()
    
    def _run_monthly_tasks(self):
        """Run tasks that should execute monthly."""
        logger.info("Running monthly tasks")
        db = SessionLocal()
        
        try:
            # 1. Reset monthly quotas
            self._reset_monthly_quotas(db)
            
            # 2. Generate monthly reports (if needed)
            # self._generate_monthly_reports(db)
            
        except Exception as e:
            logger.error(f"Error in monthly tasks: {e}")
        finally:
            db.close()
    
    def _aggregate_hourly_metrics(self, db: Session):
        """Aggregate hourly metrics for all active tenants."""
        try:
            from app.models.tenant import Tenant
            
            tenants = db.query(Tenant).filter(Tenant.is_active == True).all()
            metrics_service = MetricsService(db)
            
            now = datetime.utcnow()
            hour = now.replace(minute=0, second=0, microsecond=0)
            
            for tenant in tenants:
                try:
                    metrics_service.aggregate_hourly_metrics(tenant.id, hour)
                except Exception as e:
                    logger.error(f"Failed to aggregate hourly metrics for tenant {tenant.id}: {e}")
            
            logger.info(f"Aggregated hourly metrics for {len(tenants)} tenants")
            
        except Exception as e:
            logger.error(f"Error aggregating hourly metrics: {e}")
    
    def _aggregate_daily_metrics(self, db: Session):
        """Aggregate daily metrics for all active tenants."""
        try:
            from app.models.tenant import Tenant
            
            tenants = db.query(Tenant).filter(Tenant.is_active == True).all()
            metrics_service = MetricsService(db)
            
            yesterday = datetime.utcnow() - timedelta(days=1)
            date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            
            for tenant in tenants:
                try:
                    metrics_service.aggregate_daily_metrics(tenant.id, date)
                except Exception as e:
                    logger.error(f"Failed to aggregate daily metrics for tenant {tenant.id}: {e}")
            
            logger.info(f"Aggregated daily metrics for {len(tenants)} tenants")
            
        except Exception as e:
            logger.error(f"Error aggregating daily metrics: {e}")
    
    def _check_tenant_alerts(self, db: Session):
        """Check alerts for all active tenants."""
        try:
            from app.models.tenant import Tenant
            
            tenants = db.query(Tenant).filter(Tenant.is_active == True).all()
            alerting_service = AlertingService(db)
            
            total_alerts = 0
            for tenant in tenants:
                try:
                    alerts = alerting_service.check_all_alerts(tenant.id)
                    total_alerts += len(alerts)
                    
                    # Send notifications for critical alerts
                    for alert in alerts:
                        if alert["severity"] == "critical":
                            logger.warning(f"Critical alert for tenant {tenant.id}: {alert['message']}")
                            # Could send email/webhook here
                            
                except Exception as e:
                    logger.error(f"Failed to check alerts for tenant {tenant.id}: {e}")
            
            if total_alerts > 0:
                logger.info(f"Found {total_alerts} alerts across all tenants")
            
        except Exception as e:
            logger.error(f"Error checking tenant alerts: {e}")
    
    def _reset_daily_quotas(self, db: Session):
        """Reset daily quota counters for all tenants."""
        try:
            now = datetime.utcnow()
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Reset daily usage counters
            db.execute(
                """
                UPDATE tenant_quota_usage
                SET query_count = 0, api_calls_count = 0, updated_at = ?
                WHERE period_type = 'daily' AND period_start = ?
                """,
                (now, period_start)
            )
            db.commit()
            
            logger.info("Reset daily quotas for all tenants")
            
        except Exception as e:
            logger.error(f"Error resetting daily quotas: {e}")
            db.rollback()
    
    def _reset_monthly_quotas(self, db: Session):
        """Reset monthly quota counters for all tenants."""
        try:
            now = datetime.utcnow()
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Reset monthly usage counters
            db.execute(
                """
                UPDATE tenant_quota_usage
                SET query_count = 0, updated_at = ?
                WHERE period_type = 'monthly' AND period_start = ?
                """,
                (now, period_start)
            )
            db.commit()
            
            logger.info("Reset monthly quotas for all tenants")
            
        except Exception as e:
            logger.error(f"Error resetting monthly quotas: {e}")
            db.rollback()


# Global scheduler instance
_scheduler: Optional[SchedulerService] = None


def get_scheduler() -> SchedulerService:
    """Get or create scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = SchedulerService()
    return _scheduler


def start_scheduler():
    """Start the background scheduler."""
    scheduler = get_scheduler()
    scheduler.start()


def stop_scheduler():
    """Stop the background scheduler."""
    scheduler = get_scheduler()
    scheduler.stop()
