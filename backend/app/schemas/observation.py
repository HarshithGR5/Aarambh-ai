from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from ..models.observation import ObservationType, MarkerType, MarkerSeverity


class TextObservationCreate(BaseModel):
    child_id: UUID
    raw_text: str = Field(..., min_length=5)
    language: str = "hi"
    observation_type: ObservationType = ObservationType.TEXT


class MarkerResponse(BaseModel):
    id: int
    domain_id: int
    domain_code: Optional[str] = None
    marker_type: MarkerType
    severity: Optional[MarkerSeverity] = None
    description: str
    ai_extracted: bool
    confidence: Optional[Decimal] = None

    class Config:
        from_attributes = True


class ObservationResponse(BaseModel):
    id: UUID
    child_id: UUID
    observation_type: ObservationType
    raw_text: Optional[str] = None
    transcript: Optional[str] = None
    transcript_lang: Optional[str] = None
    english_text: Optional[str] = None
    processing_status: str
    markers: List[MarkerResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


class VoiceObservationResponse(BaseModel):
    observation_id: UUID
    transcript: Optional[str] = None
    english_text: Optional[str] = None
    extracted_markers: List[dict] = []
    pdrs_updated: bool = False
    new_pdrs_score: Optional[int] = None
