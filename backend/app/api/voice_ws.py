import json
import base64
import asyncio
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.agents.extraction_agent import extraction_agent, ExtractedHealthcareRecord
from app.rules.danger_signs import danger_engine
from app.gnani.service import gnani_service
from app.models.models import HealthcareVisit, Beneficiary, DangerSignAlert, FollowUpTask, AshaWorker, AuditEvent

logger = logging.getLogger("voice_ws")
router = APIRouter(tags=["Voice WebSocket"])

@router.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_record: Optional[ExtractedHealthcareRecord] = None
    language = "en"
    # Track emergency events already persisted during this WebSocket session.
    persisted_danger_sign_ids = set()
    persisted_correction_events = set()
    
    # Send connection greeting
    await websocket.send_json({
        "type": "connected",
        "message": "Connected to ASHA-VAANI Voice Gateway.",
        "gnani_status": gnani_service.get_status()
    })

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                payload = json.loads(raw_data)
            except Exception:
                continue

            msg_type = payload.get("type")

            if msg_type == "init":
                persisted_danger_sign_ids.clear()
                persisted_correction_events.clear()
                language = payload.get("language", "en")
                initial_bid = payload.get("beneficiary_id")
                session_record = ExtractedHealthcareRecord(beneficiary_id=initial_bid)
                await websocket.send_json({
                    "type": "session_initialized",
                    "language": language,
                    "record": session_record.model_dump()
                })

            elif msg_type == "reset":
                persisted_danger_sign_ids.clear()
                persisted_correction_events.clear()
                session_record = ExtractedHealthcareRecord()
                await websocket.send_json({
                    "type": "session_reset",
                    "record": session_record.model_dump()
                })

            elif msg_type in ["text_utterance", "speech_transcript"]:
                text = payload.get("text", "").strip()
                if not text:
                    continue
                
                lang = payload.get("language", language)

                # Process through AI Extraction Agent & Deterministic Rule Engine
                session_record = await asyncio.to_thread(
                    extraction_agent.process_utterance,
                    current_text=text,
                    existing_record=session_record,
                    language=lang
                )

                # Check if danger sign detected
                danger_signs = session_record.danger_signs
                if danger_signs:
                    await websocket.send_json({
                        "type": "danger_sign_detected",
                        "dangers": danger_signs,
                        "emergency": True,
                        "spoken_alert": danger_signs[-1]["spoken_instruction"]
                    })

                    # Step 3: Immediate emergency database persistence.
                    # Saves danger alerts as soon as a beneficiary can be
                    # resolved, without waiting for visit confirmation.
                    emergency_db: Session = SessionLocal()
                    try:
                        b_query = emergency_db.query(Beneficiary)
                        emergency_beneficiary = None
                        if session_record.beneficiary_id:
                            emergency_beneficiary = b_query.filter(
                                Beneficiary.beneficiary_id.ilike(
                                    session_record.beneficiary_id
                                )
                            ).first()
                        if not emergency_beneficiary and session_record.beneficiary_name:
                            emergency_beneficiary = b_query.filter(
                                Beneficiary.name.ilike(
                                    f"%{session_record.beneficiary_name}%"
                                )
                            ).first()

                        if emergency_beneficiary:
                            new_danger_ids = []
                            for ds in danger_signs:
                                danger_id = ds.get("id")
                                if not danger_id or danger_id in persisted_danger_sign_ids:
                                    continue

                                danger_name = ds.get("name", "Danger Sign")
                                # Check whether an unresolved alert already exists.
                                existing_active_alert = emergency_db.query(
                                    DangerSignAlert
                                ).filter(
                                    DangerSignAlert.beneficiary_id == emergency_beneficiary.id,
                                    DangerSignAlert.danger_sign_name == danger_name,
                                    DangerSignAlert.acknowledged.is_(False)
                                ).first()

                                # Create an alert only if no unresolved alert exists.
                                if not existing_active_alert:
                                    emergency_db.add(DangerSignAlert(
                                        visit_id=None,
                                        beneficiary_id=emergency_beneficiary.id,
                                        danger_sign_name=danger_name,
                                        severity=ds.get("severity", "EMERGENCY"),
                                        referral_action=ds.get(
                                            "action_instruction",
                                            "Immediate referral to PHC."
                                        ),
                                        guideline_citation=ds.get(
                                            "guideline",
                                            "MoHFW Guidelines"
                                        ),
                                        acknowledged=False,
                                        referred_to_phc=False
                                    ))

                                emergency_db.add(AuditEvent(
                                    event_type="DANGER_SIGN_DETECTED",
                                    description=(
                                        f"Emergency danger sign detected for "
                                        f"{emergency_beneficiary.name}: "
                                        f"{danger_name}"
                                    )[:255],
                                    metadata_json={
                                        "danger_sign_id": danger_id,
                                        "beneficiary_id": emergency_beneficiary.beneficiary_id,
                                        "beneficiary_name": emergency_beneficiary.name,
                                        "severity": ds.get("severity", "EMERGENCY"),
                                        "matched_term": ds.get("matched_term"),
                                        "spoken_text": text,
                                        "referral_advised": True,
                                        "referral_completed": False,
                                        "duplicate_alert_suppressed": bool(existing_active_alert),
                                        "performed_by": "ASHA_VOICE_AGENT"
                                    }
                                ))

                                new_danger_ids.append(danger_id)

                            # Persist correction requests (audit only for now).
                            new_correction_keys = []
                            for correction in session_record.danger_sign_correction_requests:
                                corr_key = (
                                    correction.get("danger_sign_id"),
                                    correction.get("status"),
                                )
                                if corr_key in persisted_correction_events:
                                    continue

                                emergency_db.add(AuditEvent(
                                    event_type="CORRECTION_REQUESTED",
                                    description=(
                                        f"Correction requested for "
                                        f"{emergency_beneficiary.name}: "
                                        f"{correction.get('danger_sign_name', 'Danger Sign')} "
                                        f"(status: {correction.get('status')})"
                                    )[:255],
                                    metadata_json={
                                        "danger_sign_id": correction.get("danger_sign_id"),
                                        "danger_sign_name": correction.get("danger_sign_name"),
                                        "denial_term": correction.get("denial_term"),
                                        "status": correction.get("status"),
                                        "requires_clinical_review": correction.get(
                                            "requires_clinical_review", True
                                        ),
                                        "beneficiary_id": emergency_beneficiary.beneficiary_id,
                                        "performed_by": "ASHA_VOICE_AGENT"
                                    }
                                ))
                                new_correction_keys.append(corr_key)

                            emergency_db.commit()

                            for did in new_danger_ids:
                                persisted_danger_sign_ids.add(did)
                            for ck in new_correction_keys:
                                persisted_correction_events.add(ck)
                    except Exception as e:
                        emergency_db.rollback()
                        logger.error(f"Error persisting emergency alerts: {e}")
                    finally:
                        emergency_db.close()

                # If status is Confirmed via voice ("yes, save it")
                if session_record.status == "Confirmed":
                    db: Session = SessionLocal()
                    try:
                        # Resolve beneficiary — no arbitrary fallback.
                        b_query = db.query(Beneficiary)
                        b = None
                        if session_record.beneficiary_id:
                            b = b_query.filter(Beneficiary.beneficiary_id.ilike(session_record.beneficiary_id)).first()
                        if not b and session_record.beneficiary_name:
                            b = b_query.filter(Beneficiary.name.ilike(f"%{session_record.beneficiary_name}%")).first()

                        # SAFETY: refuse to save if beneficiary cannot be matched.
                        if not b:
                            await websocket.send_json({
                                "type": "beneficiary_unresolved",
                                "message": (
                                    "Beneficiary could not be matched to a registered "
                                    "person. Please identify the beneficiary before saving."
                                ),
                                "record": session_record.model_dump()
                            })
                            continue

                        asha = db.query(AshaWorker).first()
                        has_dangers = len(session_record.danger_signs) > 0

                        # Referral is ADVISED, not COMPLETED, at confirmation time.
                        visit = HealthcareVisit(
                            beneficiary_id=b.id,
                            asha_worker_id=asha.id if asha else None,
                            visit_type=session_record.visit_type or "Household Visit",
                            weight_kg=session_record.weight_kg,
                            vaccinations_given=session_record.vaccinations,
                            health_observations=", ".join(session_record.health_observations) if session_record.health_observations else "Voice recorded visit",
                            next_visit_date=session_record.next_visit_date,
                            danger_signs_detected=session_record.danger_signs,
                            referral_made=False,
                            status="CONFIRMED",
                            transcript_snippet=session_record.raw_transcript
                        )
                        db.add(visit)
                        db.flush()

                        if asha:
                            asha.total_visits = (asha.total_visits or 0) + 1

                        # Link previously persisted emergency alerts to this visit.
                        if has_dangers:
                            b.danger_flag = True
                            for ds in session_record.danger_signs:
                                existing_alert = db.query(DangerSignAlert).filter(
                                    DangerSignAlert.beneficiary_id == b.id,
                                    DangerSignAlert.danger_sign_name == ds.get("name", "Danger Sign"),
                                    DangerSignAlert.visit_id.is_(None),
                                    DangerSignAlert.acknowledged.is_(False)
                                ).order_by(DangerSignAlert.created_at.desc()).first()
                                if existing_alert:
                                    existing_alert.visit_id = visit.id

                        # Save follow-up task
                        if session_record.next_visit_date:
                            db.add(FollowUpTask(
                                beneficiary_id=b.id,
                                visit_id=visit.id,
                                task_title=f"Next Visit Follow-up ({session_record.visit_type or 'General'})",
                                due_date=session_record.next_visit_date,
                                status="PENDING",
                                priority="NORMAL"
                            ))

                        # Audit event for visit confirmation
                        db.add(AuditEvent(
                            event_type="VISIT_CONFIRMED",
                            description=(
                                f"Visit for {b.name} confirmed via voice. "
                                f"Danger signs detected: {len(session_record.danger_signs)}. "
                                f"Referral advised: {has_dangers}."
                            ),
                            metadata_json={
                                "entity_type": "HealthcareVisit",
                                "entity_id": visit.id,
                                "beneficiary_id": b.beneficiary_id,
                                "danger_sign_count": len(session_record.danger_signs),
                                "referral_advised": has_dangers,
                                "performed_by": "ASHA_VOICE_AGENT"
                            }
                        ))

                        db.commit()

                        await websocket.send_json({
                            "type": "record_saved_successfully",
                            "visit_id": visit.id,
                            "beneficiary_name": b.name,
                            "referral_advised": has_dangers,
                            "referral_completed": False,
                            "message": (
                                f"Record for {b.name} confirmed and saved. "
                                + (
                                    "Danger sign alert raised. Referral to PHC is ADVISED "
                                    "but not yet confirmed as completed."
                                    if has_dangers else ""
                                )
                            )
                        })
                    except Exception as e:
                        db.rollback()
                        logger.error(f"Error persisting confirmed record: {e}")
                    finally:
                        db.close()

                # Dispatch updated record state
                await websocket.send_json({
                    "type": "record_updated",
                    "text": text,
                    "record": session_record.model_dump(),
                    "readback_summary": session_record.clarification_needed
                })

            elif msg_type == "request_tts":
                # Request TTS for confirmation readback
                text_to_speak = payload.get("text", "")
                lang_code = payload.get("language_code", "en-IN")
                
                audio_bytes = await gnani_service.synthesize_speech_gnani_timbre(
                    text=text_to_speak,
                    language_code=lang_code
                )
                
                if audio_bytes:
                    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                    await websocket.send_json({
                        "type": "tts_audio_ready",
                        "audio_base64": audio_b64,
                        "format": "audio/wav"
                    })
                else:
                    await websocket.send_json({
                        "type": "tts_fallback",
                        "text": text_to_speak,
                        "message": "Using browser Web Speech API for readback (Gnani Timbre API Key awaiting in .env)"
                    })

    except WebSocketDisconnect:
        logger.info("Voice WebSocket disconnected.")
    except Exception as e:
        logger.error(f"WebSocket Exception: {e}")