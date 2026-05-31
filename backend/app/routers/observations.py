import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from ..database import get_db
from ..schemas.observation import TextObservationCreate, ObservationResponse, VoiceObservationResponse
from ..models.observation import Observation, ObservationMarker, ObservationType
from ..models.milestone import DevelopmentalDomain
from ..middleware.auth_middleware import get_current_user
from ..models.user import User
from ..services.child_service import get_child, get_age_months
from ..services.pdrs_service import compute_pdrs, save_pdrs_score
from ..config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/text", response_model=ObservationResponse, status_code=status.HTTP_201_CREATED)
async def submit_text_observation(
    data: TextObservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit a text-based observation and extract developmental markers via AI."""
    child = get_child(data.child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    observation = Observation(
        child_id=data.child_id,
        observed_by=current_user.id,
        observation_type=ObservationType.TEXT,
        raw_text=data.raw_text,
        english_text=data.raw_text,
        processing_status="PROCESSING",
    )
    db.add(observation)
    db.flush()

    try:
        age_months = get_age_months(child.date_of_birth)
        text_to_process = data.raw_text

        if data.language != "en":
            from ..ai.observation_nlp import translate_to_english
            text_to_process = await translate_to_english(data.raw_text, data.language)
            observation.english_text = text_to_process

        from ..ai.observation_nlp import extract_observation_markers
        markers_data = await extract_observation_markers(text_to_process, age_months)

        for m in markers_data:
            domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.code == m.get("domain")).first()
            if not domain:
                continue
            marker = ObservationMarker(
                observation_id=observation.id,
                domain_id=domain.id,
                marker_type=m.get("type", "CONCERN"),
                severity=m.get("severity"),
                description=m.get("description", ""),
                ai_extracted=True,
                confidence=m.get("confidence"),
            )
            db.add(marker)

        observation.processing_status = "DONE"
        db.commit()
        db.refresh(observation)

        # Trigger PDRS recompute
        try:
            pdrs_result = compute_pdrs(data.child_id, db)
            save_pdrs_score(data.child_id, pdrs_result, db)
        except Exception as pdrs_err:
            logger.warning(f"PDRS recompute failed: {pdrs_err}")

    except Exception as e:
        observation.processing_status = "FAILED"
        db.commit()
        logger.error(f"Observation processing failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return observation


@router.post("/voice", response_model=VoiceObservationResponse, status_code=status.HTTP_201_CREATED)
async def submit_voice_observation(
    child_id: UUID = Form(...),
    language: str = Form("hi"),
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit a voice observation. Transcribes with Whisper, extracts markers with GPT-4o."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    audio_bytes = await audio.read()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    audio_path = os.path.join(settings.UPLOAD_DIR, f"obs_{child_id}_{audio.filename}")
    with open(audio_path, "wb") as f:
        f.write(audio_bytes)

    observation = Observation(
        child_id=child_id,
        observed_by=current_user.id,
        observation_type=ObservationType.VOICE,
        audio_url=audio_path,
        processing_status="PROCESSING",
    )
    db.add(observation)
    db.flush()

    try:
        from ..ai.transcription import transcribe_audio
        transcription = await transcribe_audio(audio_bytes, audio.filename, language_hint=language)
        transcript = transcription.get("transcript", "")
        detected_lang = transcription.get("detected_language", language)

        observation.transcript = transcript
        observation.transcript_lang = detected_lang
        observation.raw_text = transcript

        english_text = transcript
        if detected_lang not in ("en", "english"):
            from ..ai.observation_nlp import translate_to_english
            english_text = await translate_to_english(transcript, detected_lang)
        observation.english_text = english_text

        age_months = get_age_months(child.date_of_birth)
        from ..ai.observation_nlp import extract_observation_markers
        markers_data = await extract_observation_markers(english_text, age_months)

        extracted_markers_response = []
        for m in markers_data:
            domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.code == m.get("domain")).first()
            if not domain:
                continue
            marker = ObservationMarker(
                observation_id=observation.id,
                domain_id=domain.id,
                marker_type=m.get("type", "CONCERN"),
                severity=m.get("severity"),
                description=m.get("description", ""),
                ai_extracted=True,
                confidence=m.get("confidence"),
            )
            db.add(marker)
            extracted_markers_response.append({
                "domain": m.get("domain"),
                "type": m.get("type"),
                "severity": m.get("severity"),
                "description": m.get("description"),
                "confidence": m.get("confidence"),
            })

        observation.processing_status = "DONE"
        db.commit()

        pdrs_updated = False
        new_pdrs_score = None
        try:
            pdrs_result = compute_pdrs(child_id, db)
            saved_pdrs = save_pdrs_score(child_id, pdrs_result, db)
            pdrs_updated = True
            new_pdrs_score = saved_pdrs.overall_score
        except Exception as pdrs_err:
            logger.warning(f"PDRS recompute failed: {pdrs_err}")

        return VoiceObservationResponse(
            observation_id=observation.id,
            transcript=transcript,
            english_text=english_text,
            extracted_markers=extracted_markers_response,
            pdrs_updated=pdrs_updated,
            new_pdrs_score=new_pdrs_score,
        )

    except Exception as e:
        observation.processing_status = "FAILED"
        db.commit()
        logger.error(f"Voice observation processing failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{child_id}", response_model=List[ObservationResponse])
def get_child_observations(
    child_id: UUID,
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all observations for a child."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    observations = (
        db.query(Observation)
        .filter(Observation.child_id == child_id)
        .order_by(Observation.created_at.desc())
        .limit(limit)
        .all()
    )
    return observations
