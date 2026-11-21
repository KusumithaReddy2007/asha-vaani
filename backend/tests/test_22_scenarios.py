import pytest
from app.agents.extraction_agent import extraction_agent, ExtractedHealthcareRecord, can_save_record

# Scenario 1 – Newborn, all normal
def test_scenario_01_newborn_all_normal():
    text = "Visit Lakshmi. Her baby is 5 days old and weighs 3.1 kg. The baby is feeding well and active. BCG is given. OPV is due. Next visit is 30 November 2026. No danger signs."
    r = extraction_agent.process_utterance(text)

    assert r.beneficiary_name == "Lakshmi Devi"
    assert r.beneficiary_id == "SYN-001"
    assert r.visit_type == "Newborn Visit"
    assert r.pregnancy_or_newborn_details == "5 days"
    assert r.weight_kg == 3.1
    assert r.next_visit_date == "30-11-2026"
    assert r.vaccinations == {"BCG": "Given", "OPV-0": "Due"}
    assert "Feeding well" in r.health_observations
    assert "Active" in r.health_observations
    assert len(r.danger_signs) == 0
    assert r.status == "Pending Confirmation"
    assert r.save_blocked is False

# Scenario 2 – Newborn, different vaccines
def test_scenario_02_newborn_different_vaccines():
    text = "Visit Priya. Her baby is 12 days old and weighs 3.5 kg. The baby is healthy. BCG is given, OPV is given, and Pentavalent 1 is due. Next visit is 5 December 2026."
    r = extraction_agent.process_utterance(text)

    assert r.beneficiary_name == "Priya Sharma"
    assert r.beneficiary_id == "SYN-002"
    assert r.visit_type == "Newborn Visit"
    assert r.pregnancy_or_newborn_details == "12 days"
    assert r.weight_kg == 3.5
    assert r.next_visit_date == "05-12-2026"
    assert "Healthy" in r.health_observations
    assert len(r.danger_signs) == 0
    assert r.vaccinations.get("BCG") == "Given"
    assert r.vaccinations.get("OPV-0") == "Given"
    assert r.vaccinations.get("Pentavalent-1") == "Due"

# Scenario 3 – ANC visit
def test_scenario_03_anc_visit():
    text = "Visit Sunita for her antenatal checkup. She is 6 months pregnant. She has taken her IFA tablets. Td 1 is given. She has no bleeding or abdominal pain. Next visit is 10 December 2026."
    r = extraction_agent.process_utterance(text)

    assert r.beneficiary_name == "Sunita Gowda"
    assert r.beneficiary_id == "SYN-003"
    assert r.visit_type == "ANC Checkup"
    assert r.pregnancy_or_newborn_details == "6 months pregnant"
    assert r.weight_kg is None  # Do not invent weight
    assert r.next_visit_date == "10-12-2026"
    assert len(r.danger_signs) == 0  # No danger signs from "no bleeding"
    assert "IFA tablets taken" in r.health_observations
    assert "No bleeding" in r.health_observations
    assert "No abdominal pain" in r.health_observations
    assert r.vaccinations.get("IFA Tablets") == "Given"
    assert r.vaccinations.get("Td-1") == "Given"

# Scenario 4 – Postnatal visit
def test_scenario_04_postnatal_visit():
    text = "Visit Kavita. She delivered 7 days ago. Mother and baby are doing well. The baby is breastfeeding properly. No fever or breathing difficulty. Next visit is 28 November 2026."
    r = extraction_agent.process_utterance(text)

    assert r.beneficiary_name == "Kavita Rao"
    assert r.beneficiary_id == "SYN-004"
    assert r.visit_type == "Postnatal Visit"
    assert r.pregnancy_or_newborn_details == "7 days ago"
    assert r.weight_kg is None
    assert r.next_visit_date == "28-11-2026"
    assert len(r.danger_signs) == 0
    assert "Mother and baby are doing well" in r.health_observations or "Mother and baby doing well" in r.health_observations
    assert "Breastfeeding properly" in r.health_observations
    assert "No fever" in r.health_observations
    assert "No breathing difficulty" in r.health_observations

# Scenario 5 – Multiple vaccine statuses
def test_scenario_05_multiple_vaccine_statuses():
    text = "Visit Lakshmi's baby. BCG is given, OPV is due, Pentavalent 1 is missed, and IFA tablets are not given."
    r = extraction_agent.process_utterance(text)

    assert r.beneficiary_name == "Lakshmi Devi"
    assert r.beneficiary_id == "SYN-001"
    assert r.visit_type == "Newborn Visit"
    assert r.weight_kg is None
    assert r.next_visit_date is None
    assert len(r.danger_signs) == 0
    assert r.vaccinations == {
        "BCG": "Given",
        "OPV-0": "Due",
        "Pentavalent-1": "Missed",
        "IFA Tablets": "Not Given",
    }

# Scenario 6 – Refused vaccine
def test_scenario_06_refused_vaccine():
    text = "Visit Priya's baby. BCG is given. The mother refused OPV today. Pentavalent 1 is due."
    r = extraction_agent.process_utterance(text)

    assert r.beneficiary_name == "Priya Sharma"
    assert r.beneficiary_id == "SYN-002"
    assert r.visit_type == "Newborn Visit"
    assert len(r.danger_signs) == 0
    assert r.vaccinations.get("BCG") == "Given"
    assert r.vaccinations.get("OPV-0") == "Refused"
    assert r.vaccinations.get("Pentavalent-1") == "Due"

# Scenario 7 – Vaccine correction
def test_scenario_07_vaccine_correction():
    r1 = extraction_agent.process_utterance("Visit Lakshmi's baby. BCG is due and OPV is given.")
    assert r1.vaccinations.get("BCG") == "Due"
    assert r1.vaccinations.get("OPV-0") == "Given"

    r2 = extraction_agent.process_utterance("Correction: BCG was actually given, not due.", existing_record=r1)
    assert r2.vaccinations.get("BCG") == "Given"
    assert r2.vaccinations.get("OPV-0") == "Given"
    assert any(h["field"] == "vaccine_BCG" for h in r2.field_audit_history)
    assert len(r2.vaccine_conflicts) == 0

# Scenario 8 – Similar vaccine names
def test_scenario_08_similar_vaccine_names():
    text = "Visit Sunita. Td 1 is given, IFA tablets are due, and OPV is not given."
    r = extraction_agent.process_utterance(text)

    assert r.beneficiary_name == "Sunita Gowda"
    assert r.beneficiary_id == "SYN-003"
    assert r.vaccinations.get("Td-1") == "Given"
    assert r.vaccinations.get("IFA Tablets") == "Due"
    assert r.vaccinations.get("OPV-0") == "Not Given"

# Scenario 9 – Weight correction
def test_scenario_09_weight_correction():
    r1 = extraction_agent.process_utterance("Visit Lakshmi's baby. The baby's weight is 2.8 kg.")
    assert r1.weight_kg == 2.8

    r2 = extraction_agent.process_utterance("Correction: the weight is 3.8 kg.", existing_record=r1)
    assert r2.beneficiary_name == "Lakshmi Devi"
    assert r2.beneficiary_id == "SYN-001"
    assert r2.weight_kg == 3.8
    assert r2.previous_weight_kg == 2.8
    assert any(h["field"] == "weight_kg" for h in r2.field_audit_history)

# Scenario 10 – Date correction
def test_scenario_10_date_correction():
    r1 = extraction_agent.process_utterance("Next visit is 25 November 2026.")
    assert r1.next_visit_date == "25-11-2026"

    r2 = extraction_agent.process_utterance("Correction: make it 30 November 2026.", existing_record=r1)
    assert r2.next_visit_date == "30-11-2026"
    assert r2.previous_visit_date == "25-11-2026"

# Scenario 11 – Observation correction
def test_scenario_11_observation_correction():
    r1 = extraction_agent.process_utterance("The baby is feeding well and active.")
    assert "Feeding well" in r1.health_observations
    assert "Active" in r1.health_observations

    r2 = extraction_agent.process_utterance("Correction: the baby is feeding poorly and needs a follow-up.", existing_record=r1)
    assert "Feeding poorly" in r2.health_observations
    assert "Follow-up required" in r2.health_observations
    assert "Feeding well" not in r2.health_observations
    assert "Active" not in r2.health_observations

# Scenario 12 – Beneficiary correction
def test_scenario_12_beneficiary_correction():
    r1 = extraction_agent.process_utterance("Visit Lakshmi.")
    assert r1.beneficiary_name == "Lakshmi Devi"
    assert r1.beneficiary_id == "SYN-001"

    r2 = extraction_agent.process_utterance("Correction: the beneficiary is Priya, not Lakshmi.", existing_record=r1)
    assert r2.beneficiary_name == "Priya Sharma"
    assert r2.beneficiary_id == "SYN-002"
    assert any(h["field"] == "beneficiary" for h in r2.field_audit_history)

# Scenario 13 – Pregnancy bleeding
def test_scenario_13_pregnancy_bleeding():
    text = "Visit Sunita. She is 7 months pregnant and reports vaginal bleeding today."
    r = extraction_agent.process_utterance(text)

    assert r.beneficiary_name == "Sunita Gowda"
    assert r.beneficiary_id == "SYN-003"
    assert r.visit_type == "ANC Checkup"
    assert r.pregnancy_or_newborn_details == "7 months pregnant"
    assert len(r.danger_signs) >= 1
    matched = next((d for d in r.danger_signs if "BLEED" in d["id"]), None)
    assert matched is not None
    assert matched["severity"] == "EMERGENCY"
    assert r.save_blocked is True
    can_save, reason = can_save_record(r)
    assert can_save is False

# Scenario 14 – Newborn fever
def test_scenario_14_newborn_fever():
    text = "Visit Priya's newborn. The baby has a high fever and is not feeding properly."
    r = extraction_agent.process_utterance(text)

    assert r.beneficiary_name == "Priya Sharma"
    assert r.beneficiary_id == "SYN-002"
    assert r.visit_type == "Newborn Visit"
    assert len(r.danger_signs) >= 1
    matched = next((d for d in r.danger_signs if "FEVER" in d["id"]), None)
    assert matched is not None
    assert r.save_blocked is True
    can_save, reason = can_save_record(r)
    assert can_save is False

# Scenario 15 – Breathing difficulty
def test_scenario_15_breathing_difficulty():
    text = "Visit Lakshmi's baby. The baby is having difficulty breathing."
    r = extraction_agent.process_utterance(text)

    assert r.beneficiary_name == "Lakshmi Devi"
    assert r.beneficiary_id == "SYN-001"
    assert r.visit_type == "Newborn Visit"
    assert len(r.danger_signs) >= 1
    matched = next((d for d in r.danger_signs if "BREATHING" in d["id"]), None)
    assert matched is not None
    assert r.save_blocked is True
    can_save, reason = can_save_record(r)
    assert can_save is False

# Scenario 16 – Convulsions
def test_scenario_16_convulsions():
    text = "Visit Kavita's newborn. The baby experienced convulsions today."
    r = extraction_agent.process_utterance(text)

    assert r.beneficiary_name == "Kavita Rao"
    assert r.beneficiary_id == "SYN-004"
    assert r.visit_type == "Newborn Visit"
    assert len(r.danger_signs) >= 1
    matched = next((d for d in r.danger_signs if "CONVULSION" in d["id"]), None)
    assert matched is not None
    assert r.save_blocked is True
    can_save, reason = can_save_record(r)
    assert can_save is False

# Scenario 17 – Emergency denial
def test_scenario_17_emergency_denial():
    r1 = extraction_agent.process_utterance("Visit Sunita. She reports vaginal bleeding.")
    assert len(r1.danger_signs) >= 1
    assert r1.save_blocked is True

    r2 = extraction_agent.process_utterance("Actually, remove the bleeding alert. There is no danger sign.", existing_record=r1)
    assert len(r2.danger_signs) >= 1  # Alert preserved!
    assert len(r2.danger_sign_correction_requests) >= 1
    assert r2.danger_sign_correction_requests[0]["status"] == "CORRECTION_PENDING"
    assert r2.save_blocked is True
    can_save, reason = can_save_record(r2)
    assert can_save is False

# Scenario 18 – Unknown beneficiary
def test_scenario_18_unknown_beneficiary():
    text = "Visit Anjali. Her baby is 10 days old and weighs 3.2 kg. The baby is feeding well."
    r = extraction_agent.process_utterance(text)

    assert r.beneficiary_name == "Anjali"
    assert r.beneficiary_id is None
    assert r.registry_status == "NOT_FOUND"
    assert r.visit_type == "Newborn Visit"
    assert r.pregnancy_or_newborn_details == "10 days"
    assert r.weight_kg == 3.2
    assert "Feeding well" in r.health_observations
    assert len(r.danger_signs) == 0
    assert r.save_blocked is True
    can_save, reason = can_save_record(r)
    assert can_save is False
    assert "not found in the synthetic registry" in reason

# Scenario 19 – Missing weight
def test_scenario_19_missing_weight():
    text = "Visit Priya's newborn. The baby is 8 days old, feeding well, and active. BCG is given."
    r = extraction_agent.process_utterance(text)

    assert r.beneficiary_name == "Priya Sharma"
    assert r.beneficiary_id == "SYN-002"
    assert r.visit_type == "Newborn Visit"
    assert r.pregnancy_or_newborn_details == "8 days"
    assert r.weight_kg is None  # Do not invent 3.0 kg!
    assert r.vaccinations.get("BCG") == "Given"
    assert "Feeding well" in r.health_observations
    assert "Active" in r.health_observations
    assert "Weight not provided" in r.clarification_needed

# Scenario 20 – Conflicting vaccine status
def test_scenario_20_conflicting_vaccine_status():
    text = "Visit Lakshmi's baby. BCG is given and BCG is due."
    r = extraction_agent.process_utterance(text)

    assert "BCG" in r.vaccine_conflicts
    assert "Given" in r.vaccine_conflicts["BCG"]
    assert "Due" in r.vaccine_conflicts["BCG"]
    assert r.save_blocked is True
    can_save, reason = can_save_record(r)
    assert can_save is False
    assert "BCG has two different statuses" in reason

# Scenario 21 – New session
def test_scenario_21_new_session():
    # New session starts completely clean
    r = extraction_agent.process_utterance("Visit Sunita's newborn. The baby weighs 3.4 kg and OPV is due.")

    assert r.beneficiary_name == "Sunita Gowda"
    assert r.beneficiary_id == "SYN-003"
    assert r.visit_type == "Newborn Visit"
    assert r.weight_kg == 3.4
    assert r.vaccinations == {"OPV-0": "Due"}
    assert r.health_observations == []
    assert r.next_visit_date is None
    assert len(r.danger_signs) == 0

# Scenario 22 – Confirmation gate
def test_scenario_22_confirmation_gate():
    # Turn 1
    r1 = extraction_agent.process_utterance("Visit Lakshmi's baby. BCG is given and OPV is due. Next visit is 30 November 2026.")
    assert r1.status == "Pending Confirmation"

    # Turn 2: inspect before confirmation
    assert r1.status == "Pending Confirmation"

    # Turn 3: confirmation
    r2 = extraction_agent.process_utterance("Yes, the details are correct. Save it.", existing_record=r1)
    assert r2.status == "Confirmed"
    assert r2.save_blocked is False
