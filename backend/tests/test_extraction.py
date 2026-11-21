import pytest
from app.agents.extraction_agent import extraction_agent, ExtractedHealthcareRecord

def test_normal_newborn_visit_extraction():
    utterance = "Lakshmi, 10 days baby, weight 2.8 kilo, BCG given, next visit 20 November."
    record = extraction_agent.process_utterance(utterance)
    
    assert record.beneficiary_id == "SYN-001"
    assert "Lakshmi" in record.beneficiary_name
    assert record.visit_type == "Newborn Visit"
    assert record.weight_kg == 2.8
    assert record.vaccinations.get("BCG") == "Given"
    assert record.next_visit_date in {"20-11-2026", "2026-11-20"}
    assert record.status == "Pending Confirmation"
    assert len(record.danger_signs) == 0

def test_pregnancy_visit_with_ifa_tablets():
    utterance = "Priya, ANC checkup completed, weight 55 kg, IFA goli given, next visit 25 December."
    record = extraction_agent.process_utterance(utterance)

    assert record.beneficiary_id == "SYN-002"
    assert "Priya" in record.beneficiary_name
    assert record.visit_type == "ANC Checkup"
    assert record.weight_kg == 55.0
    assert "IFA Tablets" in record.vaccinations
    assert record.next_visit_date in {"25-12-2026", "2026-12-25"}

def test_voice_correction_of_weight():
    # Initial statement
    r1 = extraction_agent.process_utterance("Lakshmi, 10 days baby, weight 2.5 kilo, BCG given.")
    assert r1.weight_kg == 2.5

    # Correction utterance
    r2 = extraction_agent.process_utterance("No, weight is 2.8 kilo.", existing_record=r1)
    assert r2.weight_kg == 2.8
    # Beneficiary and vaccinations preserved!
    assert "Lakshmi" in r2.beneficiary_name
    assert r2.vaccinations.get("BCG") == "Given"

def test_voice_correction_of_vaccination():
    r1 = extraction_agent.process_utterance("Lakshmi, newborn visit, BCG given.")
    assert r1.vaccinations.get("BCG") == "Given"

    # Correction: BCG not given
    r2 = extraction_agent.process_utterance("Correction, BCG not given.", existing_record=r1)
    assert r2.vaccinations.get("BCG") == "Not Given"

def test_voice_confirmation_gate():
    r1 = extraction_agent.process_utterance("Lakshmi, newborn visit, weight 2.8 kilo, BCG given, next visit 20 November.")
    assert r1.status == "Pending Confirmation"

    # Worker says "Yes, save it"
    r2 = extraction_agent.process_utterance("Yes, save it.", existing_record=r1)
    assert r2.status == "Confirmed"
