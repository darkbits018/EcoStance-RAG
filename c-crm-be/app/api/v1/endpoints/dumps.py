from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from typing import List
from app.core.database import get_session
from app.schemas.dump import DumpCreate, DumpRead
from app.models.dump import EmailDumpTask
from app.models.email import Email
from app.services.dump_service import process_dump_task

router = APIRouter()

@router.post("/", response_model=DumpRead)
def create_dump(
    dump_in: DumpCreate, 
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    # Create DB Record
    dump_task = EmailDumpTask(
        connection_id=dump_in.connection_id,
        criteria_type=dump_in.criteria_type,
        criteria_value=dump_in.criteria_value,
        status="PENDING"
    )
    session.add(dump_task)
    session.commit()
    session.refresh(dump_task)
    
    # Trigger Background Processing
    # We pass only the ID, and let the service handle its own session
    background_tasks.add_task(process_dump_task, str(dump_task.id))
    
    return dump_task

@router.get("/", response_model=List[DumpRead])
def list_dumps(session: Session = Depends(get_session)):
    dumps = session.exec(select(EmailDumpTask).order_by(EmailDumpTask.started_at.desc())).all()
    return dumps

@router.get("/{id}", response_model=DumpRead)
def get_dump(id: str, session: Session = Depends(get_session)):
    dump = session.get(EmailDumpTask, id)
    if not dump:
        raise HTTPException(status_code=404, detail="Dump not found")
    return dump

@router.get("/{id}/export")
def export_dump(id: str, session: Session = Depends(get_session)):
    dump = session.get(EmailDumpTask, id)
    if not dump:
        raise HTTPException(status_code=404, detail="Dump not found")
    
    # Return simple JSON list of emails for now
    emails = session.exec(select(Email).where(Email.dump_task_id == id)).all()
    return emails

@router.post("/{id}/rerun", response_model=DumpRead)
def rerun_dump(
    id: str,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    try:
        dump_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    existing_task = session.get(EmailDumpTask, dump_uuid)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Original dump task not found")
    
    # Create new task based on existing one
    new_task = EmailDumpTask(
        connection_id=existing_task.connection_id,
        criteria_type=existing_task.criteria_type,
        criteria_value=existing_task.criteria_value,
        status="PENDING"
    )
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    
    background_tasks.add_task(process_dump_task, str(new_task.id))
    
    return new_task

import uuid

@router.delete("/{id}")
def delete_dump(id: str, session: Session = Depends(get_session)):
    try:
        dump_uuid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    dump = session.get(EmailDumpTask, dump_uuid)
    if not dump:
        raise HTTPException(status_code=404, detail="Dump not found")
    
    # Delete associated emails first
    emails = session.exec(select(Email).where(Email.dump_task_id == dump_uuid)).all()
    for email in emails:
        session.delete(email)
        
    session.delete(dump)
    session.commit()
    return {"message": "Dump deleted successfully"}

