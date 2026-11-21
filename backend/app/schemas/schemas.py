from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

# Auth Schemas
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "ASHA_WORKER"
    worker_id: Optional[str] = "ASHA-BLR-042"
    assigned_area: Optional[str] = "Whitefield Sector 4"
    village: Optional[str] = "Belathur"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

# Beneficiary Schemas
class BeneficiaryResponse(BaseModel):
    id: int
    beneficiary_id: str
    name: str
    category: str
    age_or_details: Optional[str] = None
    guardian_name: Optional[str] = None
    village: str
    contact_phone: str
    danger_flag: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Visit Schemas
class HealthcareVisitCreate(BaseModel):
    beneficiary_id_str: str # SYN-001 or database id
    visit_type: str
    weight_kg: Optional[float] = None
    vaccinations_given: Dict[str, str] = {}
    health_observations: Optional[str] = None
    next_visit_date: Optional[str] = None
    danger_signs_detected: List[Dict[str, Any]] = []
    referral_made: bool = False
    house_number: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    location_address: Optional[str] = None
    status: str = "CONFIRMED" # Only submitted after explicit confirmation gate
    transcript_snippet: Optional[str] = None

class HealthcareVisitResponse(BaseModel):
    id: int
    beneficiary_id: int
    beneficiary_name: Optional[str] = None
    beneficiary_code: Optional[str] = None
    visit_type: str
    visit_date: str
    weight_kg: Optional[float] = None
    vaccinations_given: Dict[str, str] = {}
    health_observations: Optional[str] = None
    next_visit_date: Optional[str] = None
    danger_signs_detected: List[Dict[str, Any]] = []
    referral_made: bool = False
    referral_facility: Optional[str] = None
    house_number: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    location_address: Optional[str] = None
    status: str
    confidence_score: float
    transcript_snippet: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Danger Sign Alerts
class DangerSignAlertResponse(BaseModel):
    id: int
    visit_id: Optional[int] = None
    beneficiary_id: int
    beneficiary_name: Optional[str] = None
    beneficiary_code: Optional[str] = None
    danger_sign_name: str
    severity: str
    referral_action: str
    guideline_citation: str
    acknowledged: bool
    referred_to_phc: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Follow-up Schemas
class FollowUpResponse(BaseModel):
    id: int
    beneficiary_id: int
    beneficiary_name: Optional[str] = None
    beneficiary_code: Optional[str] = None
    visit_id: Optional[int] = None
    task_title: str
    due_date: str
    status: str
    priority: str
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class FollowUpStatusUpdate(BaseModel):
    status: str # "COMPLETED", "PENDING", "OVERDUE"
    notes: Optional[str] = None

# Analytics & Dashboard Metrics
class DashboardMetricsResponse(BaseModel):
    total_household_visits: int
    today_visits: int
    pending_followups: int
    completed_records: int
    active_danger_alerts: int
    total_beneficiaries: int
    vaccinations_delivered: int
    referrals_to_phc: int
