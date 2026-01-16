from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, col
from typing import List, Optional
from app.core.database import get_session
from app.schemas.email import EmailRead
from app.models.email import Email

router = APIRouter()

@router.get("/", response_model=List[EmailRead])
def get_emails(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    session: Session = Depends(get_session)
):
    skip = (page - 1) * limit
    query = select(Email)
    
    if search:
        # Basic search on subject or sender or snippet
        # SQLite usage: basic LIKE. PostgreSQL: ILIKE
        search_fmt = f"%{search}%"
        query = query.where(
            (col(Email.subject).contains(search)) | 
            (col(Email.sender).contains(search)) |
            (col(Email.snippet).contains(search))
        )
    
    query = query.order_by(Email.received_at.desc())
    query = query.offset(skip).limit(limit)
    
    emails = session.exec(query).all()
    return emails

@router.get("/{id}", response_model=EmailRead)
def get_email(id: str, session: Session = Depends(get_session)):
    email = session.get(Email, id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    return email
