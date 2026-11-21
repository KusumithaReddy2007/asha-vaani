import pytest
from app.rules.danger_signs import danger_engine

def test_bleeding_during_pregnancy_english():
    text = "Lakshmi, 7 months pregnant, has bleeding during pregnancy since morning."
    results = danger_engine.detect_danger_signs(text, language="en")
    assert len(results) >= 1
    matched = next((r for r in results if r.id == "BLEEDING_DURING_PREGNANCY"), None)
    assert matched is not None
    assert matched.severity == "EMERGENCY"
    assert "PHC" in matched.action_instruction

def test_bleeding_during_pregnancy_hindi_codemix():
    text = "Sunita pregnant hai aur pet me dard aur khoon nikal raha hai."
    results = danger_engine.detect_danger_signs(text, language="hi")
    assert len(results) >= 1
    matched = next((r for r in results if r.id == "BLEEDING_DURING_PREGNANCY"), None)
    assert matched is not None

def test_bleeding_during_pregnancy_kannada():
    text = "Garbhavastha samayadalli raktasrava aaguttide."
    results = danger_engine.detect_danger_signs(text, language="kn")
    assert len(results) >= 1
    matched = next((r for r in results if r.id == "BLEEDING_DURING_PREGNANCY"), None)
    assert matched is not None

def test_high_fever_in_newborn_english():
    text = "Baby is 12 days old, high fever in newborn, temperature 102."
    results = danger_engine.detect_danger_signs(text, language="en")
    assert len(results) >= 1
    matched = next((r for r in results if r.id == "HIGH_FEVER_IN_NEWBORN"), None)
    assert matched is not None
    assert matched.severity == "EMERGENCY"
    assert "PHC" in matched.action_instruction

def test_high_fever_in_newborn_hindi():
    text = "10 din ka baccha hai aur bacche ko tez bukhar hai body bahut garam hai."
    results = danger_engine.detect_danger_signs(text, language="hi")
    assert len(results) >= 1
    matched = next((r for r in results if r.id == "HIGH_FEVER_IN_NEWBORN"), None)
    assert matched is not None

def test_high_fever_in_newborn_kannada():
    text = "Navajatha shishuvige tumba jwara ide."
    results = danger_engine.detect_danger_signs(text, language="kn")
    assert len(results) >= 1
    matched = next((r for r in results if r.id == "HIGH_FEVER_IN_NEWBORN"), None)
    assert matched is not None

def test_convulsions_fits():
    text = "Mother reported fits and convulsions in the evening."
    results = danger_engine.detect_danger_signs(text)
    assert any(r.id == "CONVULSIONS_OR_FITS" for r in results)

def test_severe_abdominal_pain():
    text = "Priya reported severe abdominal pain and cramps."
    results = danger_engine.detect_danger_signs(text)
    assert any(r.id == "SEVERE_ABDOMINAL_PAIN" for r in results)

def test_difficulty_breathing():
    text = "Infant has difficulty breathing and chest indrawing."
    results = danger_engine.detect_danger_signs(text)
    assert any(r.id == "DIFFICULTY_BREATHING" for r in results)

def test_normal_case_zero_false_positive():
    text = "Lakshmi, 10 days baby, weight 2.8 kilo, BCG given, feeding well, next visit 20 November."
    results = danger_engine.detect_danger_signs(text)
    assert len(results) == 0
