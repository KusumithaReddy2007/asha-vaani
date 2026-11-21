import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="ASHA_WORKER")  # ASHA_WORKER, PHC_MO, ADMIN
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    asha_profile = relationship("AshaWorker", back_populates="user", uselist=False)

class AshaWorker(Base):
    __tablename__ = "asha_workers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    worker_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. ASHA-BLR-042
    assigned_area = Column(String(100), default="Whitefield Sector 4")
    phc_name = Column(String(100), default="Kadugodi Primary Health Centre")
    village = Column(String(100), default="Belathur")
    phone = Column(String(20), default="+91-9876543210")
    total_visits = Column(Integer, default=0)

    user = relationship("User", back_populates="asha_profile")
    visits = relationship("HealthcareVisit", back_populates="asha_worker")

class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id = Column(Integer, primary_key=True, index=True)
    beneficiary_id = Column(String(50), unique=True, index=True, nullable=False) # SYN-001, SYN-002
    name = Column(String(100), index=True, nullable=False)
    category = Column(String(50), nullable=False) # PREGNANT_WOMAN, NEWBORN, INFANT, CHILD
    age_or_details = Column(String(100), nullable=True) # e.g. "24 yrs, 7 months pregnant" or "10 days newborn"
    guardian_name = Column(String(100), nullable=True) # Husband or Mother's name
    village = Column(String(100), default="Belathur Ward 3")
    contact_phone = Column(String(20), default="+91-9988776655")
    danger_flag = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    visits = relationship("HealthcareVisit", back_populates="beneficiary")
    alerts = relationship("DangerSignAlert", back_populates="beneficiary")
    followups = relationship("FollowUpTask", back_populates="beneficiary")

class HealthcareVisit(Base):
    __tablename__ = "healthcare_visits"

    id = Column(Integer, primary_key=True, index=True)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"), nullable=False)
    asha_worker_id = Column(Integer, ForeignKey("asha_workers.id"), nullable=True)
    
    visit_type = Column(String(50), nullable=False) # Newborn Visit, ANC Checkup, Immunization, Postnatal
    visit_date = Column(String(20), default=lambda: datetime.datetime.utcnow().strftime("%Y-%m-%d"))
    weight_kg = Column(Float, nullable=True)
    vaccinations_given = Column(JSON, default=dict) # e.g. {"BCG": "Given", "OPV-0": "Given"}
    health_observations = Column(Text, nullable=True)
    next_visit_date = Column(String(20), nullable=True)
    
    danger_signs_detected = Column(JSON, default=list) # List of detected danger signs
    referral_made = Column(Boolean, default=False)
    referral_facility = Column(String(100), default="Kadugodi PHC")
    
    house_number = Column(String(50), nullable=True) # e.g. "42/B", "House #15"
    location_lat = Column(Float, nullable=True) # Captured live GPS latitude
    location_lng = Column(Float, nullable=True) # Captured live GPS longitude
    location_address = Column(String(255), nullable=True) # Geocoded/locality address tag

    status = Column(String(50), default="PENDING_CONFIRMATION") # PENDING_CONFIRMATION, CONFIRMED, CANCELLED
    confidence_score = Column(Float, default=0.95)
    transcript_snippet = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    beneficiary = relationship("Beneficiary", back_populates="visits")
    asha_worker = relationship("AshaWorker", back_populates="visits")
    alerts = relationship("DangerSignAlert", back_populates="visit")
    followup_task = relationship("FollowUpTask", back_populates="visit", uselist=False)

class DangerSignAlert(Base):
    __tablename__ = "danger_sign_alerts"

    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("healthcare_visits.id"), nullable=True)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"), nullable=False)
    
    danger_sign_name = Column(String(150), nullable=False)
    severity = Column(String(50), default="EMERGENCY") # EMERGENCY, HIGH
    referral_action = Column(String(255), default="Immediate referral to Primary Health Centre (PHC) now.")
    guideline_citation = Column(String(255), default="MoHFW Operational Guidelines & IMNCI Protocol Section 3.2")
    
    acknowledged = Column(Boolean, default=False)
    referred_to_phc = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    beneficiary = relationship("Beneficiary", back_populates="alerts")
    visit = relationship("HealthcareVisit", back_populates="alerts")

class FollowUpTask(Base):
    __tablename__ = "follow_up_tasks"

    id = Column(Integer, primary_key=True, index=True)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"), nullable=False)
    visit_id = Column(Integer, ForeignKey("healthcare_visits.id"), nullable=True)
    
    task_title = Column(String(150), nullable=False) # e.g. "Postnatal 14-day checkup", "PHC Referral Follow-up"
    due_date = Column(String(20), nullable=False) # YYYY-MM-DD
    status = Column(String(50), default="PENDING") # PENDING, COMPLETED, OVERDUE
    priority = Column(String(50), default="NORMAL") # NORMAL, HIGH, EMERGENCY
    notes = Column(Text, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    beneficiary = relationship("Beneficiary", back_populates="followups")
    visit = relationship("HealthcareVisit", back_populates="followup_task")

class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    beneficiary_id = Column(String(50), nullable=True)
    raw_transcript = Column(Text, default="")
    structured_data = Column(JSON, default=dict)
    audio_duration_seconds = Column(Float, default=0.0)
    status = Column(String(50), default="ACTIVE") # ACTIVE, COMPLETED, ABORTED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False) # RECORD_CONFIRMED, DANGER_SIGN_DETECTED, VOICE_EDIT
    description = Column(String(255), nullable=False)
    user_id = Column(Integer, nullable=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
