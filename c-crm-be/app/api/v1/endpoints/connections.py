from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from app.core.database import get_session
from app.models.connection import GmailConnection

router = APIRouter()

@router.get("/", response_model=List[GmailConnection])
def list_connections(session: Session = Depends(get_session)):
    connections = session.exec(select(GmailConnection)).all()
    return connections
