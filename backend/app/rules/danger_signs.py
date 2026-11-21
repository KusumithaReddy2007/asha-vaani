import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class DangerSignConfig(BaseModel):
    id: str
    name: str
    category: str # "MATERNAL", "NEONATAL", "CHILD"
    severity: str # "EMERGENCY", "HIGH"
    guideline_source: str
    action_instruction: str
    spoken_prompt_en: str
    spoken_prompt_hi: str
    spoken_prompt_kn: str
    patterns: List[str]

# Configurable Deterministic Rule Catalog
# Guideline citations:
# 1. MoHFW Operational Guidelines: Maternal & Newborn Care at PHC (2014), Ch. 4 (Emergency Obstetric Care)
# 2. WHO / UNICEF / MoHFW IMNCI Protocol (2018): Assess & Classify Sick Young Infant (0-2 Months)
DANGER_SIGN_CATALOG: List[DangerSignConfig] = [
    DangerSignConfig(
        id="BLEEDING_DURING_PREGNANCY",
        name="Bleeding during pregnancy",
        category="MATERNAL",
        severity="EMERGENCY",
        guideline_source="MoHFW Maternal Health Operational Guidelines Section 4.1 (Antepartum / Postpartum Hemorrhage)",
        action_instruction="Refer to the nearest Primary Health Centre (PHC) immediately. Do not delay transit.",
        spoken_prompt_en="Emergency danger sign detected: Bleeding during pregnancy. Immediate action: Refer to the nearest PHC now.",
        spoken_prompt_hi="आपातकालीन खतरे का संकेत: गर्भावस्था में रक्तस्राव। तत्काल कार्रवाई: अभी नजदीकी पीएचसी रेफर करें।",
        spoken_prompt_kn="ತುರ್ತು ಅಪಾಯದ ಚಿಹ್ನೆ ಪತ್ತೆಯಾಗಿದೆ: ಗರ್ಭಾವಸ್ಥೆಯಲ್ಲಿ ರಕ್ತಸ್ರಾವ. ತಕ್ಷಣದ ಕ್ರಮ: ಈಗಲೇ ಹತ್ತಿರದ ಪಿಎಚ್‌ಸಿಗೆ ಕಳುಹಿಸಿ.",
        patterns=[
            r"\bbleed(ing)?\s+(during\s+)?pregnan(cy|t)\b",
            r"\bpregnan(cy|t).{0,20}\bbleed(ing)?\b",
            r"\b(vaginal|heavy|spotting)\s+bleed(ing)?\b",
            r"\bblood\s+(discharge|loss|spotted)\b",
            r"\bkhoon\s*(beh|nikal|aana|aa\s*raha)\b",
            r"\braktasrav(a)?\b",
            r"\braktha\s*(hog(ide|uttide))\b"
        ]
    ),
    DangerSignConfig(
        id="HIGH_FEVER_IN_NEWBORN",
        name="High fever in a newborn",
        category="NEONATAL",
        severity="EMERGENCY",
        guideline_source="WHO/UNICEF/MoHFW IMNCI Guidelines Section 2.1 (Possible Serious Bacterial Infection)",
        action_instruction="Refer to the nearest Primary Health Centre (PHC) immediately for sepsis evaluation.",
        spoken_prompt_en="Emergency danger sign detected: High fever in newborn. Immediate action: Refer to the nearest PHC now.",
        spoken_prompt_hi="आपातकालीन खतरे का संकेत: नवजात में तेज बुखार। तत्काल कार्रवाई: अभी नजदीकी पीएचसी रेफर करें।",
        spoken_prompt_kn="ತುರ್ತು ಅಪಾಯದ ಚಿಹ್ನೆ ಪತ್ತೆಯಾಗಿದೆ: ನವಜಾತ ಶಿಶುವಿನಲ್ಲಿ ಅಧಿಕ ಜ್ವರ. ತಕ್ಷಣದ ಕ್ರಮ: ಈಗಲೇ ಹತ್ತಿರದ ಪಿಎಚ್‌ಸಿಗೆ ಕಳುಹಿಸಿ.",
        patterns=[
            r"\bhigh\s+fever\s+(in\s+)?(a\s+)?(newborn|baby|infant|child)\b",
            r"\b(newborn|baby|infant).{0,25}\b(high\s+fever|temperature\s+over\s+100|hot\s+body)\b",
            r"\btez\s+bukhar\b",
            r"\bbacche\s+ko\s+tez\s+bukhar\b",
            r"\bnavjat\s+bukhar\b",
            r"\btumba\s+jwara\b",
            r"\bmakkala\s+jwara\b",
            r"\bbody\s+burning\s+hot\b"
        ]
    ),
    DangerSignConfig(
        id="CONVULSIONS_OR_FITS",
        name="Convulsions or fits (Eclampsia / Neonatal Seizures)",
        category="MATERNAL_AND_NEONATAL",
        severity="EMERGENCY",
        guideline_source="MoHFW Guidelines on Management of Eclampsia & IMNCI Convulsion Protocol",
        action_instruction="Refer immediately to First Referral Unit (FRU) / PHC with oxygen and safe positioning.",
        spoken_prompt_en="Emergency danger sign detected: Convulsions or fits. Immediate action: Refer to PHC immediately.",
        spoken_prompt_hi="आपातकालीन खतरे का संकेत: दौरे या झटके। तत्काल कार्रवाई: तुरंत अस्पताल रेफर करें।",
        spoken_prompt_kn="ತುರ್ತು ಅಪಾಯದ ಚಿಹ್ನೆ ಪತ್ತೆಯಾಗಿದೆ: ಫಿಟ್ಸ್ ಅಥವಾ ಸೆಳವು. ತಕ್ಷಣ ಆಸ್ಪತ್ರೆಗೆ ಕಳುಹಿಸಿ.",
        patterns=[
            r"\b(convulsion|convulsions|fits|seizure|seizures|eclampsia)\b",
            r"\bjhatk(a|e)\b",
            r"\bmirgi\b",
            r"\bfits\s*(banth|bandide|ide)\b"
        ]
    ),
    DangerSignConfig(
        id="DIFFICULTY_BREATHING",
        name="Difficulty breathing or chest indrawing",
        category="NEONATAL",
        severity="EMERGENCY",
        guideline_source="IMNCI Guidelines: Severe Pneumonia and Acute Respiratory Distress",
        action_instruction="Refer to PHC immediately. Keep airway clear.",
        spoken_prompt_en="Emergency danger sign detected: Breathing difficulty. Immediate action: Refer to PHC now.",
        spoken_prompt_hi="आपातकालीन खतरे का संकेत: सांस लेने में कठिनाई। तत्काल कार्रवाई: तुरंत पीएचसी रेफर करें।",
        spoken_prompt_kn="ತುರ್ತು ಅಪಾಯದ ಚಿಹ್ನೆ ಪತ್ತೆಯಾಗಿದೆ: ಉಸಿರಾಟದ ತೊಂದರೆ. ತಕ್ಷಣ ಪಿಎಚ್‌ಸಿಗೆ ಕಳುಹಿಸಿ.",
        patterns=[
            r"\b(difficulty\s+breathing|chest\s+indrawing|fast\s+breathing|gasping)\b",
            r"\bsaans\s+lene\s+me(in)?\s+takleef\b",
            r"\busirada\s+thondare\b"
        ]
    ),
    DangerSignConfig(
        id="SEVERE_ABDOMINAL_PAIN",
        name="Severe continuous abdominal pain",
        category="MATERNAL",
        severity="EMERGENCY",
        guideline_source="MoHFW Operational Guidelines: Acute Obstetric Complications",
        action_instruction="Refer to nearest PHC/FRU. Monitor vital signs.",
        spoken_prompt_en="Emergency danger sign detected: Severe abdominal pain. Immediate action: Refer to PHC now.",
        spoken_prompt_hi="खतरे का संकेत: पेट में अत्यधिक दर्द। तत्काल कार्रवाई: तुरंत पीएचसी रेफर करें।",
        spoken_prompt_kn="ಅಪಾಯದ ಚಿಹ್ನೆ: ತೀವ್ರ ಹೊಟ್ಟೆ ನೋವು. ತಕ್ಷಣ ಪಿಎಚ್‌ಸಿಗೆ ಕಳುಹಿಸಿ.",
        patterns=[
            r"\bsevere\s+(abdominal|stomach)\s+pain\b",
            r"\btez\s+pet\s+dard\b",
            r"\btivra\s+hotte\s+novu\b"
        ]
    )
]

class DetectedDangerSign(BaseModel):
    id: str
    name: str
    severity: str
    guideline_source: str
    action_instruction: str
    spoken_instruction: str
    matched_term: str

class DangerSignEngine:
    def __init__(self, catalog: Optional[List[DangerSignConfig]] = None):
        self.catalog = catalog or DANGER_SIGN_CATALOG

    def detect_danger_signs(self, text: str, language: str = "en") -> List[DetectedDangerSign]:
        """
        DETERMINISTIC EVALUATION:
        Zero-dependency, regex and pattern based. Never relies on LLM guessing.
        Strict adherence to MoHFW & IMNCI guidelines.
        """
        if not text:
            return []

        normalized_text = text.lower()
        detections: List[DetectedDangerSign] = []
        detected_ids = set()

        for config in self.catalog:
            for pattern in config.patterns:
                match = re.search(pattern, normalized_text, re.IGNORECASE)
                if match and config.id not in detected_ids:
                    detected_ids.add(config.id)
                    
                    # Select spoken prompt by requested language
                    if language.startswith("hi"):
                        prompt = config.spoken_prompt_hi
                    elif language.startswith("kn"):
                        prompt = config.spoken_prompt_kn
                    else:
                        prompt = config.spoken_prompt_en

                    detections.append(
                        DetectedDangerSign(
                            id=config.id,
                            name=config.name,
                            severity=config.severity,
                            guideline_source=config.guideline_source,
                            action_instruction=config.action_instruction,
                            spoken_instruction=prompt,
                            matched_term=match.group(0)
                        )
                    )
                    break # One pattern match is sufficient per rule
        return detections

danger_engine = DangerSignEngine()
