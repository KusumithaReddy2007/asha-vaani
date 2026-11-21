from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Beneficiary
from app.schemas.schemas import BeneficiaryResponse

router = APIRouter(prefix="/api/beneficiaries", tags=["Beneficiaries"])

@router.get("", response_model=List[BeneficiaryResponse])
def get_all_beneficiaries(db: Session = Depends(get_db)):
    """Fetch all synthetic beneficiaries."""
    return db.query(Beneficiary).order_by(Beneficiary.beneficiary_id.asc()).all()

@router.get("/{id}", response_model=BeneficiaryResponse)
def get_beneficiary(id: int, db: Session = Depends(get_db)):
    b = db.query(Beneficiary).filter(Beneficiary.id == id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    return b

@router.get("/by-code/{code}", response_model=BeneficiaryResponse)
def get_beneficiary_by_code(code: str, db: Session = Depends(get_db)):
    b = db.query(Beneficiary).filter(Beneficiary.beneficiary_id.ilike(code)).first()
    if not b:
        raise HTTPException(status_code=404, detail=f"Beneficiary {code} not found")
    return b
