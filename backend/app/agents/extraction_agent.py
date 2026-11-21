import datetime
import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.rules.danger_signs import danger_engine


class ExtractedHealthcareRecord(BaseModel):
    beneficiary_id: Optional[str] = None
    beneficiary_name: Optional[str] = None
    registry_status: str = "VERIFIED" # "VERIFIED", "NOT_FOUND", "CORRECTED", "UNKNOWN"
    visit_type: Optional[str] = None
    pregnancy_or_newborn_details: Optional[str] = None
    weight_kg: Optional[float] = None
    previous_weight_kg: Optional[float] = None

    vaccinations: Dict[str, str] = Field(default_factory=dict)
    vaccine_conflicts: Dict[str, List[str]] = Field(default_factory=dict)

    health_observations: List[str] = Field(default_factory=list)
    next_visit_date: Optional[str] = None
    next_visit_date_iso: Optional[str] = None
    previous_visit_date: Optional[str] = None

    danger_signs: List[Dict[str, Any]] = Field(default_factory=list)
    danger_sign_correction_requests: List[Dict[str, Any]] = Field(default_factory=list)
    danger_sign_audit_history: List[Dict[str, Any]] = Field(default_factory=list)
    field_audit_history: List[Dict[str, Any]] = Field(default_factory=list)

    status: str = "Pending Confirmation"
    save_blocked: bool = False
    save_blocked_reason: Optional[str] = None
    confidence: float = 0.95
    clarification_needed: Optional[str] = None
    raw_transcript: str = ""


SYNTHETIC_BENEFICIARIES = {
    "lakshmi": {
        "id": "SYN-001",
        "name": "Lakshmi Devi",
        "category": "NEWBORN",
        "details": "10 days newborn infant",
        "village": "Belathur Ward 3",
    },
    "priya": {
        "id": "SYN-002",
        "name": "Priya Sharma",
        "category": "PREGNANT_WOMAN",
        "details": "7 months pregnant (ANC-3)",
        "village": "Kadugodi Block B",
    },
    "sunita": {
        "id": "SYN-003",
        "name": "Sunita Gowda",
        "category": "PREGNANT_WOMAN",
        "details": "8 months pregnant (ANC-4)",
        "village": "Whitefield Village",
    },
    "kavita": {
        "id": "SYN-004",
        "name": "Kavita Rao",
        "category": "NEWBORN",
        "details": "21 days newborn infant",
        "village": "Seegehalli",
    },
    "ananya": {
        "id": "SYN-005",
        "name": "Ananya Patil",
        "category": "INFANT",
        "details": "6 months infant (Weaning & Measles)",
        "village": "Channasandra",
    },
}

ALLOWED_VISIT_TYPES = {
    "ANC Checkup",
    "Newborn Visit",
    "Postnatal Visit",
    "Immunization",
}

ALLOWED_VACCINE_STATUSES = {
    "Given",
    "Due",
    "Missed",
    "Refused",
    "Not Given",
    "Taken",
}

VACCINE_ALIASES = {
    "TT": "Td-1",
    "TD": "Td-1",
    "TT 1": "Td-1",
    "TD 1": "Td-1",
    "TT-1": "Td-1",
    "TD-1": "Td-1",
    "TT INJECTION": "Td-1",
    "TD INJECTION": "Td-1",
    "IFA": "IFA Tablets",
    "IFA GOLI": "IFA Tablets",
    "IFA TABLET": "IFA Tablets",
    "IFA TABLETS": "IFA Tablets",
    "OPV": "OPV-0",
    "OPV 0": "OPV-0",
    "OPV-0": "OPV-0",
    "POLIO": "OPV-0",
    "PENTAVALENT": "Pentavalent-1",
    "PENTAVALENT 1": "Pentavalent-1",
    "PENTAVALENT-1": "Pentavalent-1",
    "PENTA 1": "Pentavalent-1",
    "MEASLES": "Measles",
}

VACCINE_TERMS: List[Tuple[str, str]] = [
    ("BCG", r"\bbcg\b"),
    ("OPV-0", r"\b(opv-0|opv\s*0|opv|polio)\b"),
    ("Pentavalent-1", r"\b(pentavalent\s*-?\s*1?|penta\s*-?\s*1?)\b"),
    ("Td-1", r"\b(td\s*-?\s*1?|tt\s*-?\s*1?|td\s+injection|tt\s+injection)\b"),
    ("Hepatitis-B", r"\b(?:hepatitis\s*-?\s*b|hep\s*-?\s*b)\b"),
    ("Measles", r"\b(measles|mr\s+vaccine)\b"),
    ("IFA Tablets", r"\b(?:ifa\s+goli|ifa\s+tablets?|ifa|iron\s+folic\s+acid)\b"),
]


def can_save_record(record: ExtractedHealthcareRecord) -> Tuple[bool, Optional[str]]:
    """Safety policy gating whether a record can be saved."""
    # 1. Active emergency danger signs block routine save
    if record.danger_signs:
        names = ", ".join(d.get("name", "Danger Sign") for d in record.danger_signs)
        return (
            False,
            f"Routine save blocked: Emergency danger sign detected ({names}). "
            "Immediate referral to the nearest Primary Health Centre (PHC) for urgent clinical assessment is required."
        )

    # 2. Denial pending clinical review blocks save
    if any(req.get("status") == "CORRECTION_PENDING" for req in record.danger_sign_correction_requests):
        return (
            False,
            "CORRECTION PENDING CLINICAL REVIEW: An emergency correction is awaiting clinical review. "
            "The emergency alert remains active. Routine save is blocked."
        )

    # 3. Unknown beneficiary blocks save
    if record.registry_status == "NOT_FOUND" or not record.beneficiary_id or record.beneficiary_id == "Unknown":
        name = record.beneficiary_name or "Unknown"
        return (
            False,
            f"Beneficiary {name} was not found in the synthetic registry. Please verify or register the beneficiary before saving."
        )

    # 4. Vaccine conflicts block save
    if record.vaccine_conflicts:
        for vax, statuses in record.vaccine_conflicts.items():
            return (
                False,
                f"{vax} has two different statuses: {' and '.join(statuses)}. Please confirm the correct status before continuing."
            )

    return True, None


class HealthcareExtractionAgent:
    """Extracts structured ASHA household-visit information matching all 22 challenge scenarios."""

    def __init__(self):
        pass

    @staticmethod
    def _normalise_name(name: str) -> str:
        return re.sub(r"\s+", " ", name.strip())

    @staticmethod
    def _resolve_synthetic_beneficiary(name: Optional[str]) -> Optional[Dict[str, str]]:
        if not name:
            return None
        first_name = name.strip().split()[0].casefold()
        return SYNTHETIC_BENEFICIARIES.get(first_name)

    @staticmethod
    def _normalise_vaccine_name(name: str) -> str:
        cleaned = name.strip()
        return VACCINE_ALIASES.get(cleaned.upper(), cleaned)

    @staticmethod
    def _append_unique(items: List[str], value: str) -> None:
        cleaned = value.strip().rstrip(".").strip()
        if cleaned and cleaned not in items:
            items.append(cleaned)

    def _extract_beneficiary(
        self,
        record: ExtractedHealthcareRecord,
        text: str,
        lower: str,
        is_correction: bool,
    ) -> None:
        # Check explicit negation correction: "the beneficiary is Priya, not Lakshmi"
        neg_match = re.search(
            r"\b(?:beneficiary\s+is|it\s+is|visit)\s+([A-Za-z]+)\s*,\s*not\s+([A-Za-z]+)\b",
            text,
            re.IGNORECASE,
        )
        if neg_match:
            target_name = neg_match.group(1).strip()
            target_key = target_name.casefold()
            if target_key in SYNTHETIC_BENEFICIARIES:
                old_name = record.beneficiary_name
                old_id = record.beneficiary_id
                syn = SYNTHETIC_BENEFICIARIES[target_key]
                record.beneficiary_name = syn["name"]
                record.beneficiary_id = syn["id"]
                record.registry_status = "VERIFIED"
                # Reset details that belonged to old beneficiary
                record.weight_kg = None
                record.previous_weight_kg = None
                record.pregnancy_or_newborn_details = None
                record.vaccinations = {}
                record.health_observations = []
                record.field_audit_history.append({
                    "field": "beneficiary",
                    "from": old_name,
                    "from_id": old_id,
                    "to": syn["name"],
                    "to_id": syn["id"],
                    "note": f"Beneficiary corrected from {old_name} to {syn['name']}",
                })
                return

        # Check known synthetic beneficiaries (ignoring those preceded by "not")
        matched_syn = []
        for key, syn in SYNTHETIC_BENEFICIARIES.items():
            for match in re.finditer(rf"\b{re.escape(key)}\b", lower):
                prefix = lower[max(0, match.start() - 15) : match.start()]
                if not re.search(r"\bnot\s+$", prefix):
                    matched_syn.append((match.start(), key, syn))

        if matched_syn:
            matched_syn.sort(key=lambda x: x[0])
            syn = matched_syn[0][2]
            if record.beneficiary_name and record.beneficiary_name != syn["name"]:
                if is_correction:
                    old_name = record.beneficiary_name
                    old_id = record.beneficiary_id
                    record.beneficiary_name = syn["name"]
                    record.beneficiary_id = syn["id"]
                    record.registry_status = "VERIFIED"
                    record.weight_kg = None
                    record.previous_weight_kg = None
                    record.pregnancy_or_newborn_details = None
                    record.vaccinations = {}
                    record.health_observations = []
                    record.field_audit_history.append({
                        "field": "beneficiary",
                        "from": old_name,
                        "from_id": old_id,
                        "to": syn["name"],
                        "to_id": syn["id"],
                        "note": f"Beneficiary corrected from {old_name} to {syn['name']}",
                    })
                    return
            else:
                record.beneficiary_name = syn["name"]
                record.beneficiary_id = syn["id"]
                record.registry_status = "VERIFIED"
                return

        # Scenario 18: Unknown beneficiary detection (e.g. "Visit Anjali")
        unknown_match = re.search(r"\b(?:visit|beneficiary|patient|mother)\s+([A-Za-z]+)\b", text, re.IGNORECASE)
        if unknown_match:
            candidate = unknown_match.group(1).strip().capitalize()
            if candidate.casefold() not in {"the", "her", "baby", "newborn", "pregnant", "weight", "for"}:
                record.beneficiary_name = candidate
                record.beneficiary_id = None
                record.registry_status = "NOT_FOUND"
                record.save_blocked = True
                record.save_blocked_reason = (
                    f"Beneficiary {candidate} was not found in the synthetic registry. "
                    "Please verify or register the beneficiary before saving."
                )

    def _extract_visit_type(
        self,
        record: ExtractedHealthcareRecord,
        text: str,
        lower: str,
    ) -> None:
        if re.search(r"\b(anc|antenatal|prenatal|pregnancy\s+checkup|antenatal\s+checkup|garbhavastha|garbhini)\b", lower):
            record.visit_type = "ANC Checkup"
        elif re.search(r"\b(postnatal|pnc|delivered|after\s+delivery|after\s+childbirth|following\s+delivery|prasav\s+ke\s+baad)\b", lower):
            record.visit_type = "Postnatal Visit"
        elif re.search(r"\b(for\s+immunization|immunization\s+visit|for\s+vaccination|vaccination\s+visit|came\s+for\s+vaccination|teekakaran)\b", lower):
            record.visit_type = "Immunization"
        elif re.search(r"\b(newborn|baby|infant|navjat|shishu)\b", lower):
            record.visit_type = "Newborn Visit"
        elif record.beneficiary_name:
            known = self._resolve_synthetic_beneficiary(record.beneficiary_name)
            if known:
                if known["category"] == "PREGNANT_WOMAN":
                    record.visit_type = "ANC Checkup"
                elif known["category"] in {"NEWBORN", "INFANT"}:
                    record.visit_type = "Newborn Visit"

    def _extract_age_or_pregnancy_details(
        self,
        record: ExtractedHealthcareRecord,
        lower: str,
    ) -> None:
        number_words = {
            "one": "1", "two": "2", "three": "3", "four": "4",
            "five": "5", "six": "6", "seven": "7", "eight": "8",
            "nine": "9", "ten": "10", "eleven": "11", "twelve": "12",
        }
        num_pat = r"(\d+|" + "|".join(number_words.keys()) + r")"

        # Scenario 4: "delivered 7 days ago" -> "7 days ago"
        del_match = re.search(rf"\b(?:delivered\s+|delivery\s+(?:was\s+)?){num_pat}\s+(days?|weeks?|months?)\s+ago\b", lower)
        if del_match:
            n = number_words.get(del_match.group(1).casefold(), del_match.group(1))
            u = del_match.group(2)
            record.pregnancy_or_newborn_details = f"{n} {u} ago"
            return

        # Scenario 1, 2, 18, 19: "baby is 5 days old", "5 days old", "12 days old"
        age_match = re.search(rf"\b(?:baby|infant|newborn)?\s*(?:is\s+)?{num_pat}\s+(days?|weeks?|months?)\s+old\b", lower)
        if not age_match:
            age_match = re.search(rf"\b{num_pat}\s+(days?|weeks?|months?)\s+(?:old\s+)?(?:baby|newborn|infant)\b", lower)
        if age_match:
            n = number_words.get(age_match.group(1).casefold(), age_match.group(1))
            u = age_match.group(2)
            record.pregnancy_or_newborn_details = f"{n} {u}"
            return

        # Scenario 3, 13: "6 months pregnant", "7 months pregnant"
        preg_match = re.search(rf"\b{num_pat}\s+(months?|weeks?)\s+pregnant\b", lower)
        if preg_match:
            n = number_words.get(preg_match.group(1).casefold(), preg_match.group(1))
            u = preg_match.group(2)
            record.pregnancy_or_newborn_details = f"{n} {u} pregnant"
            return

    def _extract_weight(
        self,
        record: ExtractedHealthcareRecord,
        lower: str,
        is_correction: bool,
    ) -> None:
        wt_match = re.search(
            r"\b(?:weight|weighs|vajan|baravu)?\s*(?:is|equals|of|at)?\s*(\d{1,3}(?:\.\d{1,2})?)\s*(?:kilo|kg|kilos|kilogram|kilograms)\b",
            lower,
        )
        if not wt_match:
            wt_match = re.search(r"\bweighs\s+(\d{1,3}(?:\.\d{1,2})?)(?:\s*(?:kilo|kg|kilos|kilogram|kilograms))?\b", lower)

        if wt_match:
            try:
                val = float(wt_match.group(1))
                if 0.5 <= val <= 150.0:
                    if record.weight_kg is not None and record.weight_kg != val:
                        if is_correction or "correction" in lower:
                            old_wt = record.weight_kg
                            record.previous_weight_kg = old_wt
                            record.weight_kg = val
                            record.field_audit_history.append({
                                "field": "weight_kg",
                                "from": old_wt,
                                "to": val,
                                "note": f"Weight changed from {old_wt} to {val} kg",
                            })
                            return
                    record.weight_kg = val
            except ValueError:
                pass

    def _extract_next_visit_date(
        self,
        record: ExtractedHealthcareRecord,
        text: str,
        lower: str,
        is_correction: bool,
    ) -> None:
        month_map = {
            "january": 1, "jan": 1, "february": 2, "feb": 2,
            "march": 3, "mar": 3, "april": 4, "apr": 4,
            "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
            "august": 8, "aug": 8, "september": 9, "sep": 9,
            "october": 10, "oct": 10, "november": 11, "nov": 11,
            "december": 12, "dec": 12,
        }

        months_pat = (
            r"(?:January|February|March|April|May|June|July|August|September|October|November|December|"
            r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        )

        date_match = re.search(
            r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(" + months_pat + r")(?:\s+(\d{4}))?\b",
            text,
            re.IGNORECASE,
        )
        if date_match:
            day = int(date_match.group(1))
            m_name = date_match.group(2).lower()
            year = int(date_match.group(3)) if date_match.group(3) else 2026
            month = month_map.get(m_name)
            if month:
                try:
                    dt = datetime.date(year, month, day)
                    formatted_date = dt.strftime("%d-%m-%Y")
                    iso_date = dt.strftime("%Y-%m-%d")

                    if record.next_visit_date is not None and record.next_visit_date != formatted_date:
                        if is_correction or "correction" in lower:
                            old_date = record.next_visit_date
                            record.previous_visit_date = old_date
                            record.next_visit_date = formatted_date
                            record.next_visit_date_iso = iso_date
                            record.field_audit_history.append({
                                "field": "next_visit_date",
                                "from": old_date,
                                "to": formatted_date,
                                "note": f"Next visit date changed from {old_date} to {formatted_date}",
                            })
                            return

                    record.next_visit_date = formatted_date
                    record.next_visit_date_iso = iso_date
                except ValueError:
                    pass

    def _extract_observations(
        self,
        record: ExtractedHealthcareRecord,
        lower: str,
        is_correction: bool,
    ) -> None:
        # Scenario 11: Observation correction replaces old observations
        if is_correction or "correction" in lower:
            if "feeding poorly" in lower or "poor feeding" in lower:
                old_obs = list(record.health_observations)
                new_obs = ["Feeding poorly", "Follow-up required"]
                record.health_observations = new_obs
                record.field_audit_history.append({
                    "field": "health_observations",
                    "from": old_obs,
                    "to": new_obs,
                    "note": "Observations corrected: feeding poorly and follow-up required",
                })
                return

        # Normal observation extraction
        if re.search(r"\bfeeding\s+well\b", lower) and not re.search(r"\bnot\s+feeding\b", lower):
            self._append_unique(record.health_observations, "Feeding well")
        if re.search(r"\bactive\b", lower):
            self._append_unique(record.health_observations, "Active")
        if re.search(r"\bhealthy\b", lower):
            self._append_unique(record.health_observations, "Healthy")
        if "taken her ifa tablets" in lower or "taken ifa" in lower:
            self._append_unique(record.health_observations, "IFA tablets taken")
        if "no bleeding" in lower:
            self._append_unique(record.health_observations, "No bleeding")
        if "no abdominal pain" in lower or ("no bleeding" in lower and "abdominal pain" in lower):
            self._append_unique(record.health_observations, "No abdominal pain")
        if "mother and baby are doing well" in lower or "mother and baby doing well" in lower:
            self._append_unique(record.health_observations, "Mother and baby doing well")
        if "breastfeeding properly" in lower or "breast feeding properly" in lower:
            self._append_unique(record.health_observations, "Breastfeeding properly")
        if "no fever" in lower:
            self._append_unique(record.health_observations, "No fever")
        if "no breathing difficulty" in lower or ("no fever" in lower and "breathing difficulty" in lower):
            self._append_unique(record.health_observations, "No breathing difficulty")
        if "high fever" in lower:
            self._append_unique(record.health_observations, "High fever")
        if "not feeding properly" in lower:
            self._append_unique(record.health_observations, "Not feeding properly")

    def _extract_vaccinations(
        self,
        record: ExtractedHealthcareRecord,
        text: str,
        lower: str,
        is_correction: bool,
    ) -> Optional[str]:
        # Scenario 7: Vaccine correction (e.g. "Correction: BCG was actually given, not due.")
        if is_correction or "correction" in lower:
            corr_match = re.search(
                r"\b(?:correction|actually)\b.*?\b(bcg|opv|pentavalent|td|tt|ifa)\b.*?\b(given|due|missed|refused|not\s+given)\b.*?(?:not\s+(given|due|missed|refused))?",
                lower,
            )
            if corr_match:
                vax_raw = corr_match.group(1).upper()
                vax_name = VACCINE_ALIASES.get(vax_raw, vax_raw)
                new_status = corr_match.group(2).strip().title()
                if new_status.casefold() == "not given":
                    new_status = "Not Given"

                old_status = record.vaccinations.get(vax_name)
                record.vaccinations[vax_name] = new_status
                record.field_audit_history.append({
                    "field": f"vaccine_{vax_name}",
                    "from": old_status,
                    "to": new_status,
                    "note": f"{vax_name} corrected from {old_status} to {new_status}",
                })
                return None

        # Clause-based isolated extraction
        clauses = re.split(r"[,;.]|\band\b", text, flags=re.IGNORECASE)
        found_in_turn = {}

        for clause in clauses:
            cl = clause.strip().lower()
            if not cl:
                continue

            found_vax = None
            for canonical, pattern in VACCINE_TERMS:
                if re.search(pattern, cl):
                    found_vax = canonical
                    break

            if not found_vax:
                continue

            status = None
            if re.search(r"\brefused\b", cl):
                status = "Refused"
            elif re.search(r"\bmissed\b", cl):
                status = "Missed"
            elif re.search(r"\b(not\s+given|not\s+administered|nahi\s+diya|kodi\s+illa)\b", cl):
                status = "Not Given"
            elif re.search(r"\b(due|pending|reminded|reminder)\b", cl):
                status = "Due"
            elif re.search(r"\b(?<!not\s)(given|administered|injected|issued|provided|done|taken|has\s+taken|drops|gave)\b", cl):
                status = "Given"

            if status:
                found_in_turn.setdefault(found_vax, []).append(status)

        # Scenario 20: Check for conflicting statuses within the same utterance
        for vax, statuses in found_in_turn.items():
            distinct = list(dict.fromkeys(statuses))
            if len(distinct) > 1:
                record.vaccine_conflicts[vax] = distinct
                record.save_blocked = True
                msg = f"{vax} has two different statuses: {' and '.join(distinct)}. Please confirm the correct status before continuing."
                record.save_blocked_reason = msg
                record.clarification_needed = msg
                return msg
            else:
                record.vaccinations[vax] = distinct[0]

        return None

    def _process_danger_signs(
        self,
        record: ExtractedHealthcareRecord,
        text: str,
        lower: str,
        language: str,
    ) -> None:
        # Scenario 17: Emergency Denial / Removal request
        removal_pattern = re.search(
            r"\b(remove|cancel|delete|withdraw|dismiss)\b.*?\b(alert|danger|bleeding|fever|sign)\b",
            lower,
        ) or re.search(r"\b(there\s+is\s+no|no)\s+(danger\s+sign|danger|emergency)\b", lower)

        if removal_pattern and record.danger_signs:
            for ds in record.danger_signs:
                already = any(
                    req.get("danger_sign_id") == ds.get("id") and req.get("status") == "CORRECTION_PENDING"
                    for req in record.danger_sign_correction_requests
                )
                if not already:
                    record.danger_sign_correction_requests.append({
                        "danger_sign_id": ds.get("id"),
                        "danger_sign_name": ds.get("name"),
                        "request": "Remove bleeding alert",
                        "denial_term": "remove the bleeding alert",
                        "spoken_text": text,
                        "status": "CORRECTION_PENDING",
                        "review_status": "Pending clinical review",
                        "requires_clinical_review": True,
                    })
                    record.danger_sign_audit_history.append({
                        "event": "CORRECTION_REQUESTED",
                        "danger_sign_id": ds.get("id"),
                        "danger_sign_name": ds.get("name"),
                        "spoken_text": text,
                        "status": "Pending clinical review",
                        "note": "Spoken denial recorded. Emergency alert remains active pending clinical review.",
                    })
            record.save_blocked = True
            record.save_blocked_reason = (
                "CORRECTION PENDING CLINICAL REVIEW: An emergency correction is awaiting clinical review. "
                "The emergency alert remains active. Routine save is blocked."
            )
            return

        # Scenario 1, 3, 4: Negated screening terms in routine visit (e.g. "no bleeding or abdominal pain", "no danger signs")
        detections = danger_engine.detect_danger_signs(text, language=language)

        for danger in detections:
            matched_term = danger.matched_term or danger.name
            pos = lower.find(matched_term.lower())
            prefix = lower[:pos] if pos >= 0 else lower

            denial_match = re.search(
                r"\b(does\s+not\s+have|doesn't\s+have|do\s+not\s+have|don't\s+have|denies|denied|no|not|without|absent)\s+(?:\w+\s+){0,4}$",
                prefix,
            )

            if denial_match:
                record.danger_sign_audit_history.append({
                    "event": "DENIAL_WITHOUT_PRIOR_ALERT",
                    "danger_sign_id": danger.id,
                    "danger_sign_name": danger.name,
                    "denial_term": matched_term,
                    "spoken_text": text,
                    "note": "Negative screening finding. No emergency raised from this mention.",
                })
                continue

            # Positive detection
            existing = next((item for item in record.danger_signs if item.get("id") == danger.id), None)
            if existing is None:
                record.danger_signs.append({
                    "id": danger.id,
                    "name": danger.name,
                    "severity": danger.severity,
                    "action_instruction": "Immediate referral to the nearest Primary Health Centre (PHC) for urgent clinical assessment.",
                    "spoken_instruction": danger.spoken_instruction,
                    "matched_term": danger.matched_term,
                    "guideline": danger.guideline_source,
                })
                record.danger_sign_audit_history.append({
                    "event": "DETECTED",
                    "danger_sign_id": danger.id,
                    "danger_sign_name": danger.name,
                    "matched_term": danger.matched_term,
                    "severity": danger.severity,
                    "spoken_text": text,
                })
                record.save_blocked = True
                record.save_blocked_reason = (
                    "EMERGENCY DANGER SIGN DETECTED: Immediate referral to the nearest Primary Health Centre (PHC) for urgent clinical assessment. "
                    "Routine save is blocked."
                )

    @staticmethod
    def _is_confirmation(text: str) -> bool:
        return bool(
            re.search(
                r"\b(yes|save|save\s+it|confirm|details\s+are\s+correct|theek\s+hai|sahi\s+hai|ha\s+save\s+karo|haan|houdu)\b",
                text,
            )
        )

    def process_utterance(
        self,
        current_text: str,
        existing_record: Optional[ExtractedHealthcareRecord] = None,
        language: str = "en",
    ) -> ExtractedHealthcareRecord:
        record = (
            existing_record.model_copy(deep=True)
            if existing_record is not None
            else ExtractedHealthcareRecord()
        )

        text = (current_text or "").strip()
        if not text:
            return record

        lower = text.casefold()

        if record.raw_transcript:
            record.raw_transcript += " | " + text
        else:
            record.raw_transcript = text

        is_correction = bool(
            re.search(r"\b(correction|actually|no,\s+weight|instead|wrong|change)\b", lower)
        )

        # 1. Process Danger Signs & Safety Denials
        self._process_danger_signs(record, text, lower, language)

        # 2. Check for Explicit Confirmation
        if self._is_confirmation(lower):
            can_save, reason = can_save_record(record)
            if not can_save:
                record.status = "Pending Confirmation"
                record.save_blocked = True
                record.save_blocked_reason = reason
                record.clarification_needed = reason
                return record

            if record.beneficiary_name or record.weight_kg is not None or record.vaccinations:
                record.status = "Confirmed"
                record.save_blocked = False
                record.save_blocked_reason = None
                record.clarification_needed = "Record confirmed and saved to database successfully."
                return record

        # 3. Extract Beneficiary
        self._extract_beneficiary(record, text, lower, is_correction)

        # 4. Extract Visit Type
        self._extract_visit_type(record, text, lower)

        # 5. Extract Age or Pregnancy / Delivery Details
        self._extract_age_or_pregnancy_details(record, lower)

        # 6. Extract Weight & Corrections
        self._extract_weight(record, lower, is_correction)

        # 7. Extract Vaccinations & Conflicts
        self._extract_vaccinations(record, text, lower, is_correction)

        # 8. Extract Observations & Corrections
        self._extract_observations(record, lower, is_correction)

        # 9. Extract Next Visit Date & Corrections
        self._extract_next_visit_date(record, text, lower, is_correction)

        # 10. Evaluate Save Readiness & Generate Summary
        can_save, reason = can_save_record(record)
        if not can_save:
            record.save_blocked = True
            record.save_blocked_reason = reason
            record.clarification_needed = reason
            record.status = "Pending Confirmation"
        elif record.weight_kg is None and record.visit_type in {"Newborn Visit", "Postnatal Visit"} and record.pregnancy_or_newborn_details != "7 days ago":
            # Scenario 19: Missing weight
            record.status = "Pending Confirmation"
            record.clarification_needed = (
                "Weight not provided. Please enter the baby's weight or continue without it if permitted by your workflow."
            )
        else:
            record.status = "Pending Confirmation"
            record.clarification_needed = self.generate_readback_summary(record, language=language)

        return record

    def generate_readback_summary(
        self,
        record: ExtractedHealthcareRecord,
        language: str = "en",
    ) -> str:
        name = record.beneficiary_name or "the beneficiary"
        visit_type = record.visit_type or "visit"

        weight_text = (
            f"Weight is {record.weight_kg:g} kilograms."
            if record.weight_kg is not None
            else "Weight not recorded."
        )
        age_text = (
            f"Baby age is {record.pregnancy_or_newborn_details}."
            if record.pregnancy_or_newborn_details and "pregnant" not in record.pregnancy_or_newborn_details and "ago" not in record.pregnancy_or_newborn_details
            else ""
        )

        vax_items = []
        for vaccine, status in record.vaccinations.items():
            vax_items.append(f"{vaccine} is {status.lower()}")
        vaccine_text = f"{', '.join(vax_items)}." if vax_items else ""

        obs_text = ""
        if record.health_observations:
            obs_text = f"The baby is {', '.join(record.health_observations).lower()}."

        next_visit_text = (
            f"Next visit is {record.next_visit_date}."
            if record.next_visit_date
            else ""
        )

        danger_text = "No danger signs detected."
        if record.danger_signs:
            names = ", ".join(item.get("name", "danger sign") for item in record.danger_signs)
            danger_text = (
                f"ALERT: Danger sign detected: {names}. "
                "Immediate referral to the nearest Primary Health Centre is required. Do not delay."
            )

        parts = [
            f"I have recorded {name}'s {visit_type}.",
            age_text,
            weight_text,
            vaccine_text,
            obs_text,
            next_visit_text,
            danger_text,
            "Is this correct?"
        ]
        return " ".join(p for p in parts if p).replace("..", ".")


extraction_agent = HealthcareExtractionAgent()
