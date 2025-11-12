from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db.database_connector import DatabaseConnector
from ..db.sql_query_generator import SQLQueryGenerator
import asyncio
from urllib.parse import urlparse

router = APIRouter()

class DBConnectionRequest(BaseModel):
    db_uri: str

class QueryRequest(BaseModel):
    question: str

class ExecuteRequest(BaseModel):
    query: str

db_connector: DatabaseConnector = None
query_generator: SQLQueryGenerator = None

def parse_db_uri(db_uri: str) -> dict:
    """Parse database URI into connection config dictionary"""
    parsed = urlparse(db_uri)
    
    if parsed.scheme == 'sqlite':
        # SQLite: sqlite:///path/to/db.db
        db_path = db_uri.replace('sqlite:///', '')
        return {
            'type': 'sqlite',
            'database': db_path
        }
    elif parsed.scheme in ['postgresql', 'postgres']:
        return {
            'type': 'postgresql',
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'username': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/')
        }
    elif parsed.scheme in ['mysql', 'mysql+pymysql', 'mysql+mysqlconnector']:
        return {
            'type': 'mysql',
            'host': parsed.hostname,
            'port': parsed.port or 3306,
            'username': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/')
        }
    elif parsed.scheme == 'mongodb':
        return {
            'type': 'mongodb',
            'host': parsed.hostname,
            'port': parsed.port or 27017,
            'database': parsed.path.lstrip('/')
        }
    else:
        raise ValueError(f"Unsupported database scheme: {parsed.scheme}")

@router.post("/db/connect")
async def connect_to_db(request: DBConnectionRequest):
    """
    Connects to a database using the provided connection details.
    """
    global db_connector, query_generator
    try:
        # Parse the URI into connection config
        connection_config = parse_db_uri(request.db_uri)
        
        # Initialize connector
        db_connector = DatabaseConnector()
        
        # The connect and get_schema_info methods in DatabaseConnector are synchronous,
        # so we run them in a thread pool to avoid blocking the event loop.
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, db_connector.connect, connection_config)
        
        schema = await loop.run_in_executor(None, db_connector.get_schema_info)
        if not isinstance(schema, dict):
            raise HTTPException(status_code=500, detail=f"Failed to retrieve schema: {schema}")
            
        query_generator = SQLQueryGenerator(schema)
        return {"message": "Database connection successful and schema loaded."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/db/generate-query")
async def generate_sql_query(request: QueryRequest):
    """
    Generates a SQL query from a natural language question.
    """
    if not query_generator:
        raise HTTPException(status_code=400, detail="Database not connected or schema not loaded.")
    
    result = await query_generator.generate_query(request.question)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@router.post("/db/execute-query")
async def execute_sql_query(request: ExecuteRequest):
    """
    Executes a SQL query against the connected database.
    """
    if not db_connector:
        raise HTTPException(status_code=400, detail="Database not connected.")
    
    # It's a good practice to re-verify the query's safety here.
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, db_connector.execute_query, request.query)
    
    if isinstance(results, dict):
        if not results.get('success', False):
            raise HTTPException(status_code=500, detail=results.get('error', 'Query execution failed'))
        
        # Return the rows if available
        if 'rows' in results:
            return results['rows']
        else:
            return {"message": results.get('message', 'Query executed successfully')}
    
    raise HTTPException(status_code=500, detail="Unexpected response format from database")
