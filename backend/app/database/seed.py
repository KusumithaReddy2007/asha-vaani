import datetime
from sqlalchemy.orm import Session
from app.database.session import Base, engine, SessionLocal
from app.models.models import User, AshaWorker, Beneficiary, HealthcareVisit, DangerSignAlert, FollowUpTask, AuditEvent
from app.core.security import hash_password

def seed_database():
    """Seed synthetic beneficiaries, demo ASHA worker, and initial records."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(Beneficiary).first():
            return

        # 1. Create Demo ASHA Worker User
        demo_user = User(
            email="asha.shweta@karnataka.gov.in",
            hashed_password=hash_password("asha123"),
            full_name="Shweta Patil (ASHA Worker)",
            role="ASHA_WORKER"
        )
        db.add(demo_user)
        db.flush()

        asha_profile = AshaWorker(
            user_id=demo_user.id,
            worker_id="ASHA-BLR-042",
            assigned_area="Kadugodi Sub-Centre & Belathur",
            phc_name="Kadugodi Primary Health Centre",
            village="Belathur",
            phone="+91-9876543210",
            total_visits=24
        )
        db.add(asha_profile)
        db.flush()

        # 2. Create Synthetic Beneficiaries
        beneficiaries_data = [
            {
                "beneficiary_id": "SYN-001",
                "name": "Lakshmi Devi",
                "category": "NEWBORN",
                "age_or_details": "10 days newborn infant",
                "guardian_name": "Ramesh Devi (Father)",
                "village": "Belathur Ward 3",
                "contact_phone": "+91-9988112233",
                "danger_flag": False
            },
            {
                "beneficiary_id": "SYN-002",
                "name": "Priya Sharma",
                "category": "PREGNANT_WOMAN",
                "age_or_details": "7 months pregnant (ANC-3)",
                "guardian_name": "Anand Sharma (Husband)",
                "village": "Kadugodi Block B",
                "contact_phone": "+91-9988223344",
                "danger_flag": False
            },
            {
                "beneficiary_id": "SYN-003",
                "name": "Sunita Gowda",
                "category": "PREGNANT_WOMAN",
                "age_or_details": "8 months pregnant (ANC-4)",
                "guardian_name": "Manjunath Gowda (Husband)",
                "village": "Whitefield Village",
                "contact_phone": "+91-9988334455",
                "danger_flag": True
            },
            {
                "beneficiary_id": "SYN-004",
                "name": "Kavita Rao",
                "category": "NEWBORN",
                "age_or_details": "21 days newborn infant",
                "guardian_name": "Suresh Rao (Father)",
                "village": "Seegehalli",
                "contact_phone": "+91-9988445566",
                "danger_flag": False
            },
            {
                "beneficiary_id": "SYN-005",
                "name": "Ananya Patil",
                "category": "INFANT",
                "age_or_details": "6 months infant",
                "guardian_name": "Vijay Patil (Father)",
                "village": "Channasandra",
                "contact_phone": "+91-9988556677",
                "danger_flag": False
            }
        ]

        b_records = []
        for b_data in beneficiaries_data:
            b = Beneficiary(**b_data)
            db.add(b)
            db.flush()
            b_records.append(b)

        today_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        yesterday_str = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow_str = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        future_str = (datetime.datetime.utcnow() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")

        # 3. Create initial sample visits
        visit1 = HealthcareVisit(
            beneficiary_id=b_records[1].id, # Priya Sharma
            asha_worker_id=asha_profile.id,
            visit_type="ANC Checkup",
            visit_date=yesterday_str,
            weight_kg=56.5,
            vaccinations_given={"Td-1": "Given", "IFA Tablets": "Given (100 tablets)"},
            health_observations="Maternal vitals stable, fetal heart sound normal, IFA taken regularly",
            next_visit_date=future_str,
            danger_signs_detected=[],
            status="CONFIRMED",
            confidence_score=0.98,
            transcript_snippet="Priya Sharma, ANC checkup completed, weight 56.5 kg, Td-1 given, IFA goli given, next visit next week."
        )
        db.add(visit1)

        # 4. Create a sample danger sign alert for Sunita Gowda (SYN-003)
        visit2 = HealthcareVisit(
            beneficiary_id=b_records[2].id, # Sunita Gowda
            asha_worker_id=asha_profile.id,
            visit_type="ANC Emergency Visit",
            visit_date=today_str,
            weight_kg=58.0,
            vaccinations_given={},
            health_observations="Reported bleeding during pregnancy. Emergency referral initiated.",
            next_visit_date=tomorrow_str,
            danger_signs_detected=[{
                "id": "BLEEDING_DURING_PREGNANCY",
                "name": "Bleeding during pregnancy",
                "severity": "EMERGENCY",
                "action_instruction": "Immediate referral to Primary Health Centre (PHC) now."
            }],
            referral_made=True,
            referral_facility="Kadugodi PHC Emergency Unit",
            status="CONFIRMED",
            confidence_score=0.99,
            transcript_snippet="Sunita Gowda, bleeding during pregnancy reported. High risk case referred to PHC immediately."
        )
        db.add(visit2)
        db.flush()

        alert1 = DangerSignAlert(
            visit_id=visit2.id,
            beneficiary_id=b_records[2].id,
            danger_sign_name="Bleeding during pregnancy",
            severity="EMERGENCY",
            referral_action="Refer to nearest PHC now. 108 Ambulance notified.",
            guideline_citation="MoHFW Maternal Health Operational Guidelines Section 4.1",
            acknowledged=True,
            referred_to_phc=True
        )
        db.add(alert1)

        # 5. Create Follow-Up Tasks
        db.add(FollowUpTask(
            beneficiary_id=b_records[0].id, # Lakshmi
            task_title="Newborn 14-day Home Visit & Weight Check",
            due_date=today_str,
            status="PENDING",
            priority="HIGH",
            notes="Follow up on exclusive breastfeeding and cord hygiene."
        ))

        db.add(FollowUpTask(
            beneficiary_id=b_records[2].id, # Sunita Gowda
            visit_id=visit2.id,
            task_title="PHC Referral Follow-up for Bleeding",
            due_date=tomorrow_str,
            status="PENDING",
            priority="EMERGENCY",
            notes="Confirm hospital admission and specialist checkup at Kadugodi PHC."
        ))

        db.add(FollowUpTask(
            beneficiary_id=b_records[3].id, # Kavita Rao
            task_title="Newborn 28-day Immunization Reminder",
            due_date=future_str,
            status="PENDING",
            priority="NORMAL",
            notes="Pentavalent-1 and OPV-1 due at Anganwadi Centre."
        ))

        # 6. Audit Event
        db.add(AuditEvent(
            event_type="SYSTEM_INITIALIZED",
            description="Synthetic database initialized with MoHFW compliant benchmark beneficiaries.",
            user_id=demo_user.id
        ))

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()
