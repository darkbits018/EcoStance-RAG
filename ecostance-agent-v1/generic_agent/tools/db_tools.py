"""
Database Tools for Generic Agent
Using hosted PostgreSQL via SQLAlchemy.
"""
import logging
from langchain.tools import tool
from sqlalchemy import text
from app.db.database import SessionLocal

logger = logging.getLogger(__name__)

def create_db_query_tool(db_path: str = None):
    """
    Creates a tool to query the connected database.
    Note: db_path is kept for interface compatibility but use global PostgreSQL.
    """
    @tool
    def query_database(query: str) -> str:
        """
        Query the connected database using SQL. 
        Only use this if you are sure about the schema.
        Input should be a valid SQL query string.
        """
        db = SessionLocal()
        try:
            result_proxy = db.execute(text(query))
            
            if result_proxy.returns_rows:
                rows = result_proxy.mappings().all()
                if not rows:
                    return "No results found."
                
                # Convert to list of dicts for string representation
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
            
    return query_database
