import re
import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from app.rules.danger_signs import danger_engine, DetectedDangerSign

class VaccinationInfo(BaseModel):
    name: str
    status: str # "Given", "Due", "Missed", "Refused"

class ExtractedHealthcareRecord(BaseModel):
    beneficiary_id: Optional[str] = None
    beneficiary_name: Optional[str] = None
    visit_type: Optional[str] = None # "Newborn Visit", "ANC Checkup", "Postnatal Visit", "Immunization"
    pregnancy_or_newborn_details: Optional[str] = None
    weight_kg: Optional[float] = None
    vaccinations: Dict[str, str] = Field(default_factory=dict)
    health_observations: List[str] = Field(default_factory=list)
    next_visit_date: Optional[str] = None
    danger_signs: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "Pending Confirmation"
    confidence: float = 0.95
    clarification_needed: Optional[str] = None
    raw_transcript: str = ""

# Demo synthetic beneficiary registry for instant lookup & resolution
SYNTHETIC_BENEFICIARIES = {
    "lakshmi": {"id": "SYN-001", "name": "Lakshmi Devi", "category": "NEWBORN", "details": "10 days newborn infant", "village": "Belathur Ward 3"},
    "priya": {"id": "SYN-002", "name": "Priya Sharma", "category": "PREGNANT_WOMAN", "details": "7 months pregnant (ANC-3)", "village": "Kadugodi Block B"},
    "sunita": {"id": "SYN-003", "name": "Sunita Gowda", "category": "PREGNANT_WOMAN", "details": "8 months pregnant (ANC-4)", "village": "Whitefield Village"},
    "kavita": {"id": "SYN-004", "name": "Kavita Rao", "category": "NEWBORN", "details": "21 days newborn infant", "village": "Seegehalli"},
    "ananya": {"id": "SYN-005", "name": "Ananya Patil", "category": "INFANT", "details": "6 months infant (Weaning & Measles)", "village": "Channasandra"}
}

class HealthcareExtractionAgent:
    """
    Independent AI orchestration engine for speech understanding & healthcare record extraction.
    Supports conversational multi-turn context, field-level corrections, and deterministic danger sign safety gates.
    """

    def __init__(self):
        pass

    def process_utterance(
        self,
        current_text: str,
        existing_record: Optional[ExtractedHealthcareRecord] = None,
        language: str = "en"
    ) -> ExtractedHealthcareRecord:
        """
        Process speech utterance. Updates existing record if available (supporting conversational corrections).
        """
        record = existing_record.model_copy() if existing_record else ExtractedHealthcareRecord()
        text = current_text.strip()
        lower = text.lower()

        # Update full transcript
        if record.raw_transcript:
            record.raw_transcript += " | " + text
        else:
            record.raw_transcript = text

        # 1. EVALUATE DANGER SIGNS IMMEDIATELY (Highest Priority Deterministic Safety Gate)
        detected_dangers = danger_engine.detect_danger_signs(text, language=language)
        for ds in detected_dangers:
            existing_ids = [d["id"] for d in record.danger_signs]
            if ds.id not in existing_ids:
                record.danger_signs.append({
                    "id": ds.id,
                    "name": ds.name,
                    "severity": ds.severity,
                    "action_instruction": ds.action_instruction,
                    "spoken_instruction": ds.spoken_instruction,
                    "matched_term": ds.matched_term,
                    "guideline": ds.guideline_source
                })

        # 2. CHECK CONFIRMATION INTENT
        if re.search(r"\b(yes|save|save it|confirm|theek hai|sahi hai|ha save karo|ha|hogi|houdu)\b", lower):
            # Check if this is an explicit confirmation of an already populated record
            if record.beneficiary_name or record.weight_kg or record.vaccinations:
                record.status = "Confirmed"
                return record

        # 3. BENEFICIARY ID & NAME EXTRACTION
        # Check direct synthetic ID match (SYN-001, SYN-002, etc.)
        syn_match = re.search(r"\bSYN[-_ ]?00([1-9])\b", text, re.IGNORECASE)
        if syn_match:
            record.beneficiary_id = f"SYN-00{syn_match.group(1)}"

        # Match known synthetic names or general names
        for key, beneficiary in SYNTHETIC_BENEFICIARIES.items():
            if re.search(rf"\b{key}\b", lower):
                record.beneficiary_name = beneficiary["name"]
                if not record.beneficiary_id:
                    record.beneficiary_id = beneficiary["id"]
                if not record.visit_type:
                    if beneficiary["category"] == "NEWBORN":
                        record.visit_type = "Newborn Visit"
                    elif beneficiary["category"] == "PREGNANT_WOMAN":
                        record.visit_type = "ANC Checkup"
                break

        # Fallback name extraction if unknown name pattern
        if not record.beneficiary_name:
            name_match = re.search(r"^(beneficiary\s+)?([A-Z][a-z]+(\s+[A-Z][a-z]+)?)", text)
            if name_match and name_match.group(2).lower() not in ["weight", "next", "visit", "bcg", "ifa", "anc", "high", "bleeding"]:
                record.beneficiary_name = name_match.group(2)

        # 4. VISIT TYPE EXTRACTION
        if re.search(r"\b(newborn|baby\s+visit|navjat|shishu)\b", lower):
            record.visit_type = "Newborn Visit"
        elif re.search(r"\b(anc|antenatal|prenatal|pregnancy\s+checkup|garbhavastha)\b", lower):
            record.visit_type = "ANC Checkup"
        elif re.search(r"\b(postnatal|pnc|prasav\s+ke\s+baad)\b", lower):
            record.visit_type = "Postnatal Visit"
        elif re.search(r"\b(vaccination|immunization|teeka|teekakaran)\b", lower):
            record.visit_type = "Immunization"

        # 5. PREGNANCY OR NEWBORN DETAILS
        baby_match = re.search(r"\b(\d+)\s*(days?|weeks?|months?)\s*(baby|newborn|infant|ke\s+shishu)\b", lower)
        if baby_match:
            record.pregnancy_or_newborn_details = f"{baby_match.group(1)} {baby_match.group(2)} baby"

        gest_match = re.search(r"\b(\d+)\s*(months?|weeks?)\s*(pregnant|garbhavati)\b", lower)
        if gest_match:
            record.pregnancy_or_newborn_details = f"{gest_match.group(1)} {gest_match.group(2)} pregnant"

        # 6. WEIGHT EXTRACTION (with field level correction support)
        # Patterns like: "weight 2.8 kilo", "weight is 2.8 kg", "2.8 kilo", "weight 54 kg"
        weight_match = re.search(r"\b(?:weight|vajan|baravu)?\s*(?:is|equals)?\s*(\d{1,2}(?:\.\d{1,2})?)\s*(?:kilo|kg|kilos|kilogram|kilograms)\b", lower)
        if weight_match:
            try:
                wt = float(weight_match.group(1))
                # Validate reasonable weight ranges
                if 1.0 <= wt <= 150.0:
                    record.weight_kg = wt
            except ValueError:
                pass

        # 7. VACCINATIONS & MEDICATION STATUS (code-mixed support)
        # BCG
        if re.search(r"\bbcg\s+(given|lagaya|de\s*diya|done|kodalagide)\b", lower):
            record.vaccinations["BCG"] = "Given"
        elif re.search(r"\bbcg\s+(not\s+given|nahi\s+lagaya|baki|due|pending)\b", lower):
            record.vaccinations["BCG"] = "Not Given"

        # IFA (Iron Folic Acid)
        if re.search(r"\b(ifa|iron)\s*(goli|tablets?|medicine)?\s*(given|diya|done|kodalagide)\b", lower):
            record.vaccinations["IFA Tablets"] = "Given (100 tablets issued)"
        elif re.search(r"\b(ifa|iron)\s*(not\s+given|nahi\s+diya)\b", lower):
            record.vaccinations["IFA Tablets"] = "Not Given"

        # OPV / Polio
        if re.search(r"\b(opv|polio)\s*(given|pilaya|done|drops)\b", lower):
            record.vaccinations["OPV-0"] = "Given"

        # TT / Td
        if re.search(r"\b(tt|td)\s*(injection|given|lagaya)\b", lower):
            record.vaccinations["Td-1"] = "Given"

        # Pentavalent / Hepatitis B
        if re.search(r"\b(hepatitis\s*b|hep\s*b)\b", lower):
            record.vaccinations["Hepatitis-B"] = "Given"
        if re.search(r"\bpentavalent\b", lower):
            record.vaccinations["Pentavalent-1"] = "Given"

        # 8. OBSERVATIONS
        if "normal" in lower and "bp" in lower:
            if "BP Normal (120/80)" not in record.health_observations:
                record.health_observations.append("BP Normal (120/80)")
        if "feeding well" in lower or "dudh pi raha hai" in lower:
            if "Feeding well, active" not in record.health_observations:
                record.health_observations.append("Feeding well, active")

        # 9. NEXT VISIT DATE EXTRACTION
        # Handles "next visit 20 November", "next visit is 22 November", "next visit 2026-11-20"
        date_match = re.search(
            r"\b(?:next\s+visit|agla\s+visit|mundina\s+bheti)\s*(?:is|on)?\s*(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)(?:\s+(\d{4}))?\b",
            lower
        )
        if date_match:
            day = int(date_match.group(1))
            month_str = date_match.group(2).capitalize()
            year = int(date_match.group(3)) if date_match.group(3) else 2026
            
            month_map = {
                "January": 1, "Jan": 1, "February": 2, "Feb": 2, "March": 3, "Mar": 3,
                "April": 4, "Apr": 4, "May": 5, "June": 6, "Jun": 6, "July": 7, "Jul": 7,
                "August": 8, "Aug": 8, "September": 9, "Sep": 9, "October": 10, "Oct": 10,
                "November": 11, "Nov": 11, "December": 12, "Dec": 12
            }
            if month_str in month_map:
                month_num = month_map[month_str]
                record.next_visit_date = f"{year:04d}-{month_num:02d}-{day:02d}"

        # Direct ISO date pattern e.g. 2026-11-20
        iso_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
        if iso_match:
            record.next_visit_date = iso_match.group(1)

        # 10. GENERATE CONFIRMATION READ-BACK PHRASE
        record.clarification_needed = self.generate_readback_summary(record, language=language)

        return record

    def generate_readback_summary(self, record: ExtractedHealthcareRecord, language: str = "en") -> str:
        """
        Generates spoken confirmation phrase for Gnani Timbre v3.0 TTS read-back.
        """
        name = record.beneficiary_name or "the beneficiary"
        v_type = record.visit_type or "visit"
        weight_str = f"Weight is {record.weight_kg} kilograms." if record.weight_kg else ""
        
        vax_list = [f"{k} {v.lower()}" for k, v in record.vaccinations.items()]
        vax_str = f"{', '.join(vax_list)}." if vax_list else ""
        
        next_visit = f"Your next visit is scheduled on {record.next_visit_date}." if record.next_visit_date else ""
        
        danger_warning = ""
        if record.danger_signs:
            ds_names = ", ".join([d["name"] for d in record.danger_signs])
            danger_warning = f"ALERT: Danger sign detected: {ds_names}. Immediate referral to Primary Health Centre is required!"

        if language.startswith("hi"):
            return f"मैंने {name} का {v_type} दर्ज किया है। {weight_str} {vax_str} {next_visit} {danger_warning} क्या यह विवरण सही है? कृपया 'हाँ, सेव करो' बोलकर पुष्टि करें।"
        elif language.startswith("kn"):
            return f"ನಾನು {name} ಅವರ {v_type} ವಿವರಗಳನ್ನು ದಾಖಲಿಸಿದ್ದೇನೆ. {weight_str} {vax_str} {next_visit} {danger_warning} ಇದು ಸರಿಯಾಗಿದೆಯೇ? ದಯವಿಟ್ಟು ಖಚಿತಪಡಿಸಿ."
        else:
            return f"I have recorded {name}'s {v_type}. {weight_str} {vax_str} {next_visit} {danger_warning} Is this correct? Say 'Yes, save it' to confirm."

extraction_agent = HealthcareExtractionAgent()
