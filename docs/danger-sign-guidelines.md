# Danger Sign Detection Protocol & Clinical Guidelines

## 1. Zero Miss Strategy
In the Build Bengaluru 2.0 Challenge (PS1 – Healthcare), missing a danger sign incurs a **double penalty**. 
Therefore, ASHA-VAANI enforces a **100% deterministic rule engine** that:
- Never relies on an LLM alone for danger-sign classification.
- Never allows an AI hallucination to suppress or downgrade an emergency alert.
- Scans every interim and final transcript chunk deterministically using validated regex patterns and multi-lingual clinical terms (English, Hindi, Kannada).

---

## 2. Documented Public Health Guidelines

### Guideline A: MoHFW Maternal Health Operational Guidelines
- **Source**: Ministry of Health and Family Welfare (MoHFW), Government of India.
- **Document**: *Operational Guidelines for Maternal and Newborn Health Services at Primary Health Centres (PHCs) and Community Health Centres (CHCs)*.
- **Section**: Chapter 4, "Identification and Management of High-Risk Pregnancies and Obstetric Emergencies."
- **Key Indicators**:
  - Antepartum / Postpartum Hemorrhage (Vaginal bleeding during pregnancy).
  - Severe pre-eclampsia and eclampsia (Convulsions, fits, persistent severe headache).
  - Severe continuous abdominal pain (Placental abruption / ectopic / uterine rupture).

### Guideline B: WHO / UNICEF / MoHFW IMNCI Protocol
- **Source**: Integrated Management of Neonatal and Childhood Illness (IMNCI).
- **Document**: *Module 2: Assess and Classify the Sick Young Infant (Age 0 up to 2 Months)*.
- **Key Indicators**:
  - Possible Serious Bacterial Infection (PSBI): High fever (>38°C / >100.4°F) or hypothermia in a newborn.
  - Severe Respiratory Distress: Fast breathing, chest indrawing, stridor, or grunting.
  - Inability to feed or lethargy/unconsciousness.

---

## 3. Configured Danger Signs Catalog

| ID | Name | Category | Severity | Spoken Action Instruction | Guideline Ref |
|---|---|---|---|---|---|
| `BLEEDING_DURING_PREGNANCY` | Bleeding during pregnancy | MATERNAL | EMERGENCY | "Emergency danger sign detected: Bleeding during pregnancy. Immediate action: Refer to the nearest PHC now." | MoHFW MCH Ch. 4.1 |
| `HIGH_FEVER_IN_NEWBORN` | High fever in a newborn | NEONATAL | EMERGENCY | "Emergency danger sign detected: High fever in newborn. Immediate action: Refer to the nearest PHC now." | IMNCI Module 2.1 |
| `CONVULSIONS_OR_FITS` | Convulsions or fits (Eclampsia / Seizures) | MATERNAL & NEONATAL | EMERGENCY | "Emergency danger sign detected: Convulsions or fits. Immediate action: Refer to PHC immediately." | MoHFW Eclampsia Protocol |
| `DIFFICULTY_BREATHING` | Difficulty breathing or chest indrawing | NEONATAL | EMERGENCY | "Emergency danger sign detected: Breathing difficulty. Immediate action: Refer to PHC now." | IMNCI Module 2.3 |
| `SEVERE_ABDOMINAL_PAIN` | Severe continuous abdominal pain | MATERNAL | EMERGENCY | "Emergency danger sign detected: Severe abdominal pain. Immediate action: Refer to PHC now." | MoHFW Obstetric Triage |

---

## 4. Multi-lingual Spoken Referral Prompts
When a danger sign is triggered, ASHA-VAANI immediately synthesizes and speaks localized emergency instructions:

- **English**: *"Emergency danger sign detected: [Danger Sign]. Immediate action: Refer to the nearest PHC now."*
- **Hindi (हिन्दी)**: *"आपातकालीन खतरे का संकेत मिला: [Danger Sign]। तत्काल कार्रवाई: अभी नजदीकी प्राथमिक स्वास्थ्य केंद्र (PHC) रेफर करें।"*
- **Kannada (ಕನ್ನಡ)**: *"ತುರ್ತು ಅಪಾಯದ ಚಿಹ್ನೆ ಪತ್ತೆಯಾಗಿದೆ: [Danger Sign]. ತಕ್ಷಣದ ಕ್ರಮ: ಈಗಲೇ ಹತ್ತಿರದ ಪ್ರಾಥಮಿಕ ಆರೋಗ್ಯ ಕೇಂದ್ರಕ್ಕೆ (PHC) ಕಳುಹಿಸಿ."*
