import json
import base64
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
                language = payload.get("language", "en")
                initial_bid = payload.get("beneficiary_id")
                session_record = ExtractedHealthcareRecord(beneficiary_id=initial_bid)
                await websocket.send_json({
                    "type": "session_initialized",
                    "language": language,
                    "record": session_record.model_dump()
                })

            elif msg_type == "reset":
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
                session_record = extraction_agent.process_utterance(
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

                # If status is Confirmed via voice ("yes, save it")
                if session_record.status == "Confirmed":
                    db: Session = SessionLocal()
                    try:
                        # Auto-save confirmed record to database
                        b_query = db.query(Beneficiary)
                        b = None
                        if session_record.beneficiary_id:
                            b = b_query.filter(Beneficiary.beneficiary_id.ilike(session_record.beneficiary_id)).first()
                        if not b and session_record.beneficiary_name:
                            b = b_query.filter(Beneficiary.name.ilike(f"%{session_record.beneficiary_name}%")).first()
                        if not b:
                            b = b_query.first()

                        asha = db.query(AshaWorker).first()
                        has_dangers = len(session_record.danger_signs) > 0

                        visit = HealthcareVisit(
                            beneficiary_id=b.id if b else 1,
                            asha_worker_id=asha.id if asha else None,
                            visit_type=session_record.visit_type or "Household Visit",
                            weight_kg=session_record.weight_kg,
                            vaccinations_given=session_record.vaccinations,
                            health_observations=", ".join(session_record.health_observations) if session_record.health_observations else "Voice recorded visit",
                            next_visit_date=session_record.next_visit_date,
                            danger_signs_detected=session_record.danger_signs,
                            referral_made=has_dangers,
                            status="CONFIRMED",
                            transcript_snippet=session_record.raw_transcript
                        )
                        db.add(visit)
                        db.flush()

                        if asha:
                            asha.total_visits = (asha.total_visits or 0) + 1

                        # Save danger sign alerts
                        if has_dangers and b:
                            b.danger_flag = True
                            for ds in session_record.danger_signs:
                                db.add(DangerSignAlert(
                                    visit_id=visit.id,
                                    beneficiary_id=b.id,
                                    danger_sign_name=ds.get("name", "Danger Sign"),
                                    severity=ds.get("severity", "EMERGENCY"),
                                    referral_action=ds.get("action_instruction", "Immediate referral to PHC."),
                                    guideline_citation=ds.get("guideline", "MoHFW Guidelines Section 4.1"),
                                    acknowledged=False,
                                    referred_to_phc=True
                                ))

                        # Save follow-up task
                        if session_record.next_visit_date and b:
                            db.add(FollowUpTask(
                                beneficiary_id=b.id,
                                visit_id=visit.id,
                                task_title=f"Next Visit Follow-up ({session_record.visit_type or 'General'})",
                                due_date=session_record.next_visit_date,
                                status="PENDING",
                                priority="NORMAL"
                            ))

                        db.commit()

                        await websocket.send_json({
                            "type": "record_saved_successfully",
                            "visit_id": visit.id,
                            "beneficiary_name": b.name if b else "Beneficiary",
                            "message": f"Record for {b.name if b else 'Beneficiary'} confirmed and saved to database."
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
