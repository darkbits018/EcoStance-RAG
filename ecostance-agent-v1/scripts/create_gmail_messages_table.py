from app.db.database import engine, Base
from app.models.gmail import GmailMessage

print("Creating gmail_messages table...")
GmailMessage.__table__.create(bind=engine)
print("Table created successfully.")
