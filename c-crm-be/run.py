import uvicorn
from app.core.database import create_db_and_tables

if __name__ == "__main__":
    create_db_and_tables()
    uvicorn.run("app.main:app", host="0.0.0.0", port=9001, reload=True)
