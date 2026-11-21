# ASHA-VAANI REST & WebSocket API Documentation

## Base URL
- REST API: `http://localhost:8000/api`
- WebSocket: `ws://localhost:8000/ws/voice`
- Interactive Swagger UI: `http://localhost:8000/docs`

---

## 1. Authentication Endpoints (`/api/auth`)

### `POST /api/auth/demo-login`
Convenient 1-click login for hackathon judges and evaluation.
- **Response**:
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "asha.shweta@karnataka.gov.in",
    "full_name": "Shweta Patil (ASHA Worker)",
    "role": "ASHA_WORKER"
  }
}
```

### `POST /api/auth/login`
- **Request Body**: `{"email": "...", "password": "..."}`

---

## 2. Beneficiaries Endpoints (`/api/beneficiaries`)

### `GET /api/beneficiaries`
Lists synthetic beneficiaries (`SYN-001` through `SYN-005`).

---

## 3. Healthcare Visits Endpoints (`/api/visits`)

### `GET /api/visits`
Returns all recorded visits ordered chronologically.

### `POST /api/visits`
Creates and persists an explicitly confirmed visit.
- **Request Body**:
```json
{
  "beneficiary_id_str": "SYN-001",
  "visit_type": "Newborn Visit",
  "weight_kg": 2.8,
  "vaccinations_given": {
    "BCG": "Given",
    "OPV-0": "Given"
  },
  "health_observations": "Baby active and breastfeeding well",
  "next_visit_date": "2026-11-20",
  "danger_signs_detected": [],
  "referral_made": false,
  "transcript_snippet": "Lakshmi, 10 days baby, weight 2.8 kilo, BCG given, next visit 20 November."
}
```

---

## 4. Danger Sign Detection (`/api/danger-signs`)

### `GET /api/danger-signs/rules`
Returns the complete MoHFW / WHO IMNCI clinical catalog and regex rules.

### `POST /api/danger-signs/evaluate`
Directly evaluates any utterance string for danger signs.
- **Request Body**:
```json
{
  "text": "10 days baby has high fever in newborn",
  "language": "en"
}
```
- **Response**:
```json
{
  "text": "10 days baby has high fever in newborn",
  "danger_detected": true,
  "detections": [
    {
      "id": "HIGH_FEVER_IN_NEWBORN",
      "name": "High fever in a newborn",
      "severity": "EMERGENCY",
      "action_instruction": "Refer to the nearest Primary Health Centre (PHC) immediately for sepsis evaluation.",
      "spoken_instruction": "Emergency danger sign detected: High fever in newborn. Immediate action: Refer to the nearest PHC now."
    }
  ]
}
```

---

## 5. Follow-Up Calendar (`/api/followups`)

### `GET /api/followups?status=PENDING`
Fetch scheduled upcoming visits and emergency referral follow-up tasks.

### `PATCH /api/followups/{id}/status`
Update status to `COMPLETED` with visit verification notes.

---

## 6. Voice WebSocket (`/ws/voice`)

### Client Messages:
1. `{"type": "init", "language": "en"}`
2. `{"type": "text_utterance", "text": "Lakshmi, 10 days baby, weight 2.8 kilo, BCG given.", "language": "en"}`
3. `{"type": "reset"}`

### Server Messages:
1. `{"type": "connected", "gnani_status": {...}}`
2. `{"type": "record_updated", "record": {...}, "readback_summary": "..."}`
3. `{"type": "danger_sign_detected", "dangers": [...], "emergency": true}`
4. `{"type": "record_saved_successfully", "visit_id": 1, "message": "..."}`
