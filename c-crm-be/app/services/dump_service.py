from sqlmodel import Session, select
from app.core.database import engine
from app.models.dump import EmailDumpTask, DumpStatus
from app.models.connection import GmailConnection
from app.services.gmail_service import GmailService
import logging

logger = logging.getLogger(__name__)

import uuid


def process_dump_task(dump_id: str):
    print(f"DEBUG: Starting dump task {dump_id}")
    logger.info(f"Starting dump task {dump_id}")
    with Session(engine) as session:
        # Convert str to UUID for sqlite if needed, though SQLModel usually handles it.
        # But the error 'str object has no attribute hex' suggests SQLAlchemy is trying to treat a string as a UUID object and failing.
        try:
            task_uuid = uuid.UUID(dump_id)
        except ValueError:
            logger.error(f"Invalid UUID: {dump_id}")
            return

        task = session.get(EmailDumpTask, task_uuid)
        if not task:
            logger.error(f"Task {dump_id} not found")
            return

        try:
            # Update status to Processing
            task.status = DumpStatus.PROCESSING
            session.add(task)
            session.commit()
            session.refresh(task)

            # Get Connection
            connection = session.get(GmailConnection, task.connection_id)
            if not connection or not connection.is_active:
                raise Exception("Connection invalid or inactive")

            # Init Service
            service = GmailService(connection)

            # Build Query
            query = ""
            if task.criteria_type == "RECIPIENT":
                # 'to:bob' OR 'from:bob' ? Usually recipient means emails TO that person?
                # Or emails INVOLVING that person?
                # User request said "Targeted Email Retrieval: ... based on added recipients"
                # Let's check Filter logic. Usually we want "to:target" or "from:target"?
                # Let's assume broad scope: involves user.
                # Actually, "Dump" implies I want to see emails sent to 'client@example.com'.
                # But if I am the user, I probably want emails FROM 'client@example.com' too.
                # Safest is loose search just by email address which searches to/from/cc
                query = task.criteria_value
            elif task.criteria_type == "LABEL":
                query = f"label:{task.criteria_value}"
            
            # Execute
            count = 0
            print(f"DEBUG: Executing query: {query}")
            for msg_summary in service.list_messages(query):
                # Check for max limit? For now let's do all (or limit to 100 for safety during dev)
                # if count > 50: break 
                
                try:
                    email_obj = service.get_message_detail(msg_summary['id'], task.id)
                    session.merge(email_obj) # Upsert
                    count += 1
                    print(f"DEBUG: Fetched {count} emails...")
                    
                    if count % 10 == 0:
                        session.commit() # batch commit
                except Exception as e:
                    print(f"DEBUG: Error processing msg {msg_summary.get('id')}: {e}")
                    logger.error(f"Failed to fetch msg {msg_summary['id']}: {e}")
            
            print(f"DEBUG: Finished loop. Total: {count}")
            session.commit()

            # Finish
            task.status = DumpStatus.COMPLETED
            task.total_emails = count
            task.completed_at = datetime.utcnow()
            session.add(task)
            session.commit()
            
        except Exception as e:
            logger.error(f"Dump task failed: {e}")
            task.status = DumpStatus.FAILED
            task.error_message = str(e)
            session.add(task)
            session.commit()

from datetime import datetime
