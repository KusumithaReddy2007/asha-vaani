# ASHA-VAANI Live Demo & Evaluation Guide

This guide enables judges and evaluators to test all core capabilities of **ASHA-VAANI** during the **Build Bengaluru 2.0 PS1 Healthcare** demonstration.

---

## Quick Launch
1. **Start Backend**:
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
3. Open browser at: **`http://localhost:5173`**
4. Click **"⚡ 1-Click Demo Login"** in the top navigation bar.

---

## 5 Test Scenarios for Hackathon Evaluation

### Scenario 1: Normal Newborn Visit
- **Goal**: Test multi-field extraction from conversational Indic code-mix.
- **Action**: In the Live Voice Assistant, click the **"1. Normal Newborn Visit"** button or speak:
  > *"Lakshmi, 10 days baby, weight 2.8 kilo, BCG given, next visit 20 November."*
- **Observed Behavior**:
  - Beneficiary recognized as `Lakshmi Devi (SYN-001)`.
  - Visit Type identified as `Newborn Visit`.
  - Weight accurately extracted as `2.8 kg`.
  - Vaccination logged: `BCG: Given`.
  - Next scheduled visit set to `2026-11-20`.
  - Agent speaks readback confirmation: *"I have recorded Lakshmi's newborn visit... Is this correct?"*

---

### Scenario 2: Pregnancy ANC Visit with Iron Supplementation
- **Goal**: Test pregnancy maternal care and IFA medicine extraction.
- **Action**: Click **"2. Pregnancy Visit (ANC)"** or speak:
  > *"Priya, ANC checkup completed, weight 55 kg, IFA goli given, next visit 25 December."*
- **Observed Behavior**:
  - Beneficiary matched to `Priya Sharma (SYN-002)`.
  - Visit Type: `ANC Checkup`.
  - Weight: `55.0 kg`.
  - Medication: `IFA Tablets: Given (100 tablets issued)`.
  - Next visit: `2026-12-25`.

---

### Scenario 3: Intelligent Voice Correction
- **Goal**: Verify that health worker can correct a single field without restarting the visit.
- **Action**: While Lakshmi's record is displayed, click **"3. Voice Correction (Weight)"** or speak:
  > *"No, weight is 2.8 kilo."*
- **Observed Behavior**:
  - Weight field updates to `2.8 kg`.
  - Beneficiary name (`Lakshmi Devi`), visit type, and vaccination records remain intact!

---

### Scenario 4: EMERGENCY ESCALATION — Bleeding During Pregnancy
- **Goal**: Test the deterministic danger-sign engine on maternal obstetric emergency (Zero-Miss Policy).
- **Action**: Click **"4. Danger Sign: Bleeding"** or speak:
  > *"Sunita Gowda, 8 months pregnant, has bleeding during pregnancy since morning!"*
- **Observed Behavior**:
  - Flashing red emergency alert banner appears.
  - Spoken referral instruction generated: *"Emergency danger sign detected: Bleeding during pregnancy. Immediate action: Refer to the nearest PHC now."*
  - Beneficiary `Sunita Gowda (SYN-003)` flagged as `HIGH RISK`.
  - Emergency referral alert created in Dashboard.

---

### Scenario 5: EMERGENCY ESCALATION — High Fever in a Newborn
- **Goal**: Test neonatal sepsis detection per WHO IMNCI protocols.
- **Action**: Click **"5. Danger Sign: Newborn High Fever"** or speak:
  > *"10 days baby has high fever in newborn, body burning hot, not feeding!"*
- **Observed Behavior**:
  - Detected: `HIGH_FEVER_IN_NEWBORN`.
  - Spoken prompt: *"Emergency danger sign detected: High fever in newborn. Immediate action: Refer to the nearest PHC now."*
  - Emergency follow-up created to confirm hospital admission at Kadugodi PHC.

---

### Scenario 6: Voice Confirmation Gate
- **Action**: Speak: *"Yes, save it"* or click **"Confirm & Save Record"**.
- **Observed Behavior**:
  - Record status transitions from `Pending Confirmation` to `Confirmed`.
  - Record committed to SQLite/PostgreSQL database.
  - Automatically creates scheduled task in Follow-up Calendar.
