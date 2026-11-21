import pytest
from app.database.session import SessionLocal
from app.api import auth, beneficiaries, visits, danger_signs, analytics, followups
from app.schemas.schemas import HealthcareVisitCreate
from app.rules.danger_signs import danger_engine

@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_demo_login_direct(db):
    res = auth.demo_login(db=db)
    assert "access_token" in res
    assert res["user"]["email"] == "asha.shweta@karnataka.gov.in"
    assert res["user"]["role"] == "ASHA_WORKER"

def test_beneficiaries_list_direct(db):
    b_list = beneficiaries.get_all_beneficiaries(db=db)
    assert len(b_list) >= 5
    codes = [b.beneficiary_id for b in b_list]
    assert "SYN-001" in codes
    assert "SYN-002" in codes
    assert "SYN-003" in codes

def test_danger_sign_rules_catalog():
    rules_data = danger_signs.get_configured_rules()
    assert len(rules_data["rules"]) >= 5
    rule_ids = [r["id"] for r in rules_data["rules"]]
    assert "BLEEDING_DURING_PREGNANCY" in rule_ids
    assert "HIGH_FEVER_IN_NEWBORN" in rule_ids

def test_danger_sign_evaluate_api():
    req = danger_signs.EvaluateRequest(text="Newborn has high fever in baby", language="en")
    res = danger_signs.evaluate_text(req)
    assert res["danger_detected"] is True
    assert len(res["detections"]) > 0
    assert "PHC" in res["detections"][0].action_instruction

def test_create_visit_and_followup_direct(db):
    payload = HealthcareVisitCreate(
        beneficiary_id_str="SYN-001",
        visit_type="Newborn Visit",
        weight_kg=2.8,
        vaccinations_given={"BCG": "Given", "OPV-0": "Given"},
        health_observations="Active and breastfeeding well",
        next_visit_date="2026-11-20",
        danger_signs_detected=[],
        referral_made=False,
        transcript_snippet="Lakshmi, newborn visit, 2.8 kg, BCG given."
    )
    v_res = visits.create_confirmed_visit(payload=payload, db=db)
    assert v_res.beneficiary_code == "SYN-001"
    assert v_res.weight_kg == 2.8
    assert v_res.status == "CONFIRMED"

    # Check followups
    fu_list = followups.get_followups(status=None, db=db)
    assert any(f.beneficiary_code == "SYN-001" for f in fu_list)

def test_dashboard_analytics_direct(db):
    data = analytics.get_dashboard_data(db=db)
    assert "metrics" in data
    assert data["metrics"]["total_household_visits"] > 0
    assert "beneficiary_distribution" in data
    assert "vaccination_breakdown" in data

def test_system_status_direct():
    sys_status = analytics.get_system_status()
    assert sys_status["status"] == "HEALTHY"
    assert "gnani_platform" in sys_status
    assert sys_status["gnani_platform"]["provider"] == "Gnani API Platform"
