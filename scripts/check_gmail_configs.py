from app.db.database import SessionLocal
from app.models.tenant import Tenant

db = SessionLocal()
tenants = db.query(Tenant).all()
print(f"Total Tenants: {len(tenants)}")
for t in tenants:
    enabled = (t.gmail_config or {}).get("enabled", False)
    email = "N/A"
    if enabled and "oauth" in t.gmail_config:
        # Avoid printing full tokens for security, but check if they exist
        email = "Token Present"
    print(f"Name: {t.name:20} | ID: {t.id} | Gmail Enabled: {enabled} | OAuth: {email}")
db.close()
