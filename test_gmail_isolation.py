from app.db.database import SessionLocal
from app.routers.gmail_router import get_gmail_status
from app.auth.dependencies import get_current_user
import asyncio
import traceback

async def test_status():
    db = SessionLocal()
    
    tenants_to_test = [
        ("ecostance-demo", "e571fb6f-7980-40b5-a423-8ca28b5b3cd6"),
        ("CertifyDigital", "badcd123-6cc6-4011-b01b-d33d1153f10d")
    ]
    
    for name, tid in tenants_to_test:
        current_user = {
            "tenant_id": tid,
            "user_id": "test-user"
        }
        print(f"\n>>> Testing Gmail status for tenant: {name} ({tid})")
        try:
            result = await get_gmail_status(db=db, current_user=current_user)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error testing {name}: {type(e).__name__}: {str(e)}")
            # traceback.print_exc()
            
    db.close()

if __name__ == "__main__":
    asyncio.run(test_status())
