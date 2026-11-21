import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import HealthcareVisit, Beneficiary, DangerSignAlert, FollowUpTask, AshaWorker, AuditEvent
from app.schemas.schemas import HealthcareVisitCreate, HealthcareVisitResponse, HealthcareVisitUpdate

router = APIRouter(prefix="/api/visits", tags=["Visits"])

@router.get("", response_model=List[HealthcareVisitResponse])
def get_visits(db: Session = Depends(get_db)):
    visits = db.query(HealthcareVisit).order_by(HealthcareVisit.created_at.desc()).all()
    results = []
    for v in visits:
        b = db.query(Beneficiary).filter(Beneficiary.id == v.beneficiary_id).first()
        results.append(HealthcareVisitResponse(
            id=v.id,
            beneficiary_id=v.beneficiary_id,
            beneficiary_name=b.name if b else "Unknown",
            beneficiary_code=b.beneficiary_id if b else "SYN-000",
            visit_type=v.visit_type,
            visit_date=v.visit_date,
            weight_kg=v.weight_kg,
            vaccinations_given=v.vaccinations_given or {},
            health_observations=v.health_observations,
            next_visit_date=v.next_visit_date,
            danger_signs_detected=v.danger_signs_detected or [],
            referral_made=v.referral_made,
            referral_facility=v.referral_facility,
            house_number=v.house_number,
            location_lat=v.location_lat,
            location_lng=v.location_lng,
            location_address=v.location_address,
            status=v.status,
            confidence_score=v.confidence_score,
            transcript_snippet=v.transcript_snippet,
            created_at=v.created_at
        ))
    return results

@router.post("", response_model=HealthcareVisitResponse)
def create_confirmed_visit(payload: HealthcareVisitCreate, db: Session = Depends(get_db)):
    """
    Saves a structured visit AFTER explicit confirmation.
    Automatically generates follow-up tasks, danger sign alerts, and audit events.
    """
    # 1. Resolve Beneficiary safely
    search_value = (payload.beneficiary_id_str or "").strip()
    if not search_value:
        raise HTTPException(
            status_code=400,
            detail="Beneficiary ID or full name is required."
        )

    matches = db.query(Beneficiary).filter(
        (Beneficiary.beneficiary_id.ilike(search_value)) |
        (Beneficiary.name.ilike(search_value))
    ).all()

    if len(matches) == 0:
        raise HTTPException(
            status_code=400,
            detail=f"No beneficiary found for '{search_value}'. Use a registered beneficiary ID or exact full name."
        )

    if len(matches) > 1:
        raise HTTPException(
            status_code=400,
            detail="Multiple beneficiaries matched. Please use the unique beneficiary ID."
        )

    b = matches[0]

    # 2. Get first ASHA profile
    asha = db.query(AshaWorker).first()

    # 3. Create Visit Record
    has_dangers = len(payload.danger_signs_detected) > 0
    visit = HealthcareVisit(
        beneficiary_id=b.id,
        asha_worker_id=asha.id if asha else None,
        visit_type=payload.visit_type,
        visit_date=datetime.datetime.utcnow().strftime("%Y-%m-%d"),
        weight_kg=payload.weight_kg,
        vaccinations_given=payload.vaccinations_given,
        health_observations=payload.health_observations,
        next_visit_date=payload.next_visit_date,
        danger_signs_detected=payload.danger_signs_detected,
        referral_made=has_dangers or payload.referral_made,
        referral_facility="Kadugodi PHC Emergency Unit" if has_dangers else "Kadugodi PHC",
        house_number=payload.house_number,
        location_lat=payload.location_lat,
        location_lng=payload.location_lng,
        location_address=payload.location_address,
        status="CONFIRMED",
        confidence_score=0.98,
        transcript_snippet=payload.transcript_snippet
    )
    db.add(visit)
    db.flush()

    if asha:
        asha.total_visits = (asha.total_visits or 0) + 1

    # 4. If danger signs detected, trigger Emergency Referral & Alerts
    if has_dangers:
        b.danger_flag = True
        for ds in payload.danger_signs_detected:
            alert = DangerSignAlert(
                visit_id=visit.id,
                beneficiary_id=b.id,
                danger_sign_name=ds.get("name", "Unspecified Danger Sign"),
                severity="EMERGENCY",
                referral_action=ds.get("action_instruction", "Immediate referral to Primary Health Centre (PHC) now."),
                guideline_citation=ds.get("guideline", "MoHFW Operational Guidelines Section 4.1"),
                acknowledged=False,
                referred_to_phc=True
            )
            db.add(alert)

            # Create high-priority follow up for referral
            db.add(FollowUpTask(
                beneficiary_id=b.id,
                visit_id=visit.id,
                task_title=f"URGENT: Verify PHC Referral for {ds.get('name', 'Danger Sign')}",
                due_date=datetime.datetime.utcnow().strftime("%Y-%m-%d"),
                status="PENDING",
                priority="EMERGENCY",
                notes=f"Beneficiary referred to Kadugodi PHC. Verify emergency care delivery."
            ))

    # 5. Routine next visit follow-up task
    if payload.next_visit_date:
        db.add(FollowUpTask(
            beneficiary_id=b.id,
            visit_id=visit.id,
            task_title=f"Scheduled {payload.visit_type} Follow-up",
            due_date=payload.next_visit_date,
            status="PENDING",
            priority="NORMAL",
            notes=f"Vaccination & growth monitoring follow-up."
        ))

    # 6. Audit Event
    db.add(AuditEvent(
        event_type="VISIT_CONFIRMED_AND_SAVED",
        description=f"Visit confirmed for {b.name} ({b.beneficiary_id}). Danger signs: {len(payload.danger_signs_detected)}",
        metadata_json={
            "visit_id": visit.id,
            "beneficiary_id": b.beneficiary_id,
            "weight_kg": payload.weight_kg,
            "danger_signs": payload.danger_signs_detected
        }
    ))

    db.commit()

    return HealthcareVisitResponse(
        id=visit.id,
        beneficiary_id=b.id,
        beneficiary_name=b.name,
        beneficiary_code=b.beneficiary_id,
        visit_type=visit.visit_type,
        visit_date=visit.visit_date,
        weight_kg=visit.weight_kg,
        vaccinations_given=visit.vaccinations_given or {},
        health_observations=visit.health_observations,
        next_visit_date=visit.next_visit_date,
        danger_signs_detected=visit.danger_signs_detected or [],
        referral_made=visit.referral_made,
        referral_facility=visit.referral_facility,
        house_number=visit.house_number,
        location_lat=visit.location_lat,
        location_lng=visit.location_lng,
        location_address=visit.location_address,
        status=visit.status,
        confidence_score=visit.confidence_score,
        transcript_snippet=visit.transcript_snippet,
        created_at=visit.created_at
    )


@router.patch("/{visit_id}", response_model=HealthcareVisitResponse)
def update_visit(
    visit_id: int,
    payload: HealthcareVisitUpdate,
    db: Session = Depends(get_db)
):
    """Update editable fields of an existing visit without changing its beneficiary or visit date."""
    visit = db.query(HealthcareVisit).filter(
        HealthcareVisit.id == visit_id
    ).first()

    if not visit:
        raise HTTPException(status_code=404, detail="Visit report not found.")

    changes = payload.dict(exclude_unset=True)

    if not changes:
        raise HTTPException(status_code=400, detail="No changes supplied.")

    for field, value in changes.items():
        setattr(visit, field, value)

    beneficiary = db.query(Beneficiary).filter(
        Beneficiary.id == visit.beneficiary_id
    ).first()

    db.add(AuditEvent(
        event_type="VISIT_REPORT_EDITED",
        description=f"Visit report {visit.id} edited for {beneficiary.name if beneficiary else 'Unknown'}",
        metadata_json={
            "visit_id": visit.id,
            "beneficiary_id": beneficiary.beneficiary_id if beneficiary else None,
            "updated_fields": list(changes.keys())
        }
    ))

    db.commit()
    db.refresh(visit)

    return HealthcareVisitResponse(
        id=visit.id,
        beneficiary_id=visit.beneficiary_id,
        beneficiary_name=beneficiary.name if beneficiary else "Unknown",
        beneficiary_code=beneficiary.beneficiary_id if beneficiary else "SYN-000",
        visit_type=visit.visit_type,
        visit_date=visit.visit_date,
        weight_kg=visit.weight_kg,
        vaccinations_given=visit.vaccinations_given or {},
        health_observations=visit.health_observations,
        next_visit_date=visit.next_visit_date,
        danger_signs_detected=visit.danger_signs_detected or [],
        referral_made=visit.referral_made,
        referral_facility=visit.referral_facility,
        house_number=visit.house_number,
        location_lat=visit.location_lat,
        location_lng=visit.location_lng,
        location_address=visit.location_address,
        status=visit.status,
        confidence_score=visit.confidence_score,
        transcript_snippet=visit.transcript_snippet,
        created_at=visit.created_at
    )
