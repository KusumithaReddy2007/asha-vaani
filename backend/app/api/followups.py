import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import FollowUpTask, Beneficiary
from app.schemas.schemas import FollowUpResponse, FollowUpStatusUpdate

router = APIRouter(prefix="/api/followups", tags=["Follow-up Management"])

@router.get("", response_model=List[FollowUpResponse])
def get_followups(
    status: Optional[str] = Query(None, description="Filter by status: PENDING, COMPLETED, OVERDUE"),
    db: Session = Depends(get_db)
):
    query = db.query(FollowUpTask)
    if status:
        query = query.filter(FollowUpTask.status == status.upper())
    
    tasks = query.order_by(FollowUpTask.due_date.asc()).all()
    results = []
    today_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    for t in tasks:
        b = db.query(Beneficiary).filter(Beneficiary.id == t.beneficiary_id).first()
        task_status = t.status
        # Dynamically flag overdue tasks
        if task_status == "PENDING" and t.due_date < today_str:
            task_status = "OVERDUE"

        results.append(FollowUpResponse(
            id=t.id,
            beneficiary_id=t.beneficiary_id,
            beneficiary_name=b.name if b else "Unknown",
            beneficiary_code=b.beneficiary_id if b else "SYN-000",
            visit_id=t.visit_id,
            task_title=t.task_title,
            due_date=t.due_date,
            status=task_status,
            priority=t.priority,
            notes=t.notes,
            completed_at=t.completed_at,
            created_at=t.created_at
        ))
    return results

@router.patch("/{id}/status")
def update_followup_status(id: int, payload: FollowUpStatusUpdate, db: Session = Depends(get_db)):
    task = db.query(FollowUpTask).filter(FollowUpTask.id == id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Follow-up task not found")
    
    task.status = payload.status.upper()
    if payload.notes:
        task.notes = payload.notes
    if task.status == "COMPLETED":
        task.completed_at = datetime.datetime.utcnow()
    db.commit()

    return {"status": "success", "message": f"Task {id} updated to {task.status}."}
