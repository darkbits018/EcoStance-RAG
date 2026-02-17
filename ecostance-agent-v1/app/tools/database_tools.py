"""
Shared Database Tools for agents.
Generic database utilities.
"""
import logging
from langchain.tools import tool
from sqlalchemy import text
from app.db.database import SessionLocal

logger = logging.getLogger(__name__)

def get_db():
    """Helper function to get database session"""
    return SessionLocal()

@tool
def query_database_generic(query: str) -> str:
    """
    Execute a generic SQL query against the connected database.
    Only use this if you are sure about the schema.
    """
    db = get_db()
    try:
        result_proxy = db.execute(text(query))
        if result_proxy.returns_rows:
            rows = result_proxy.mappings().all()
            if not rows:
                return "No results found."
            result = [dict(row) for row in rows]
            return str(result)
        else:
            db.commit()
            return f"Query executed successfully. Rows affected: {result_proxy.rowcount}"
    except Exception as e:
        logger.error(f"Error querying database: {str(e)}")
        return f"Error querying database: {str(e)}"
    finally:
        db.close()
