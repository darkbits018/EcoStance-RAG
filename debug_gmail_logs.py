from app.db.database import SessionLocal
from app.models.gmail import GmailExecutionLog

db = SessionLocal()
logs = db.query(GmailExecutionLog).order_by(GmailExecutionLog.start_time.desc()).limit(5).all()

print(f"Found {len(logs)} logs.")
for log in logs:
    print(f"--- Log ID: {log.id} ---")
    print(f"Status: {log.status}")
    print(f"Emails Processed: {log.emails_processed}")
    print(f"Errors: {log.errors}")
    print(f"Time: {log.start_time}")
    print("-------------------------")
