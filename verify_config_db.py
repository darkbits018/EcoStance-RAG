
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_tenant_config(tenant_id):
    from app.models.public_agent import PublicAgentConfig
    db = SessionLocal()
    try:
        config = db.query(PublicAgentConfig).filter(PublicAgentConfig.tenant_id == tenant_id).first()
        if config:
            print(f"Config found for {tenant_id}:")
            print(f"Agent Type: {config.agent_type}")
            print(f"Enabled: {config.enabled}")
        else:
            print(f"No config found for {tenant_id}")
    finally:
        db.close()

if __name__ == "__main__":
    tenant_id = "e571fb6f-7980-40b5-a423-8ca28b5b3cd6"
    check_tenant_config(tenant_id)
