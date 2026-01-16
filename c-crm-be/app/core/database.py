from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

# Import models so they are registered in metadata
from app.models.connection import GmailConnection
from app.models.dump import EmailDumpTask
from app.models.email import Email


# Handle database connection arguments based on DB type
connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args["check_same_thread"] = False

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
