from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import DangerSignAlert, Beneficiary
from app.schemas.schemas import DangerSignAlertResponse
from app.rules.danger_signs import danger_engine, DANGER_SIGN_CATALOG
from pydantic import BaseModel

router = APIRouter(prefix="/api/danger-signs", tags=["Danger Signs"])

class EvaluateRequest(BaseModel):
    text: str
    language: str = "en"

@router.get("/alerts", response_model=List[DangerSignAlertResponse])
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(DangerSignAlert).order_by(DangerSignAlert.created_at.desc()).all()
    results = []
    for a in alerts:
        b = db.query(Beneficiary).filter(Beneficiary.id == a.beneficiary_id).first()
        results.append(DangerSignAlertResponse(
            id=a.id,
            visit_id=a.visit_id,
            beneficiary_id=a.beneficiary_id,
            beneficiary_name=b.name if b else "Unknown",
            beneficiary_code=b.beneficiary_id if b else "SYN-000",
            danger_sign_name=a.danger_sign_name,
            severity=a.severity,
            referral_action=a.referral_action,
            guideline_citation=a.guideline_citation,
            acknowledged=a.acknowledged,
            referred_to_phc=a.referred_to_phc,
            created_at=a.created_at
        ))
    return results

@router.post("/alerts/{id}/acknowledge")
def acknowledge_alert(id: int, db: Session = Depends(get_db)):
    alert = db.query(DangerSignAlert).filter(DangerSignAlert.id == id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.acknowledged = True
    db.commit()
    return {"status": "success", "message": f"Alert {id} acknowledged."}

@router.get("/rules")
def get_configured_rules():
    """Returns official public-health guidelines and configured deterministic rules."""
    return {
        "guideline_sources": [
            "Ministry of Health & Family Welfare (MoHFW) Operational Guidelines for Maternal & Newborn Health at PHC",
            "WHO/UNICEF/MoHFW Integrated Management of Neonatal and Childhood Illness (IMNCI) Protocol"
        ],
        "zero_miss_policy": "Double penalty applies for missed danger signs in PS1 challenge. Engine runs deterministically.",
        "rules": [
            {
                "id": r.id,
                "name": r.name,
                "category": r.category,
                "severity": r.severity,
                "guideline_source": r.guideline_source,
                "action_instruction": r.action_instruction,
                "patterns_count": len(r.patterns)
            }
            for r in DANGER_SIGN_CATALOG
        ]
    }

@router.post("/evaluate")
def evaluate_text(req: EvaluateRequest):
    """Directly test evaluation of any text string."""
    results = danger_engine.detect_danger_signs(req.text, language=req.language)
    return {
        "text": req.text,
        "language": req.language,
        "danger_detected": len(results) > 0,
        "detections": results
    }
