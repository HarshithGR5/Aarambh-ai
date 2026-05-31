from pydantic import BaseModel
from typing import Optional, Dict
from uuid import UUID
from datetime import date, datetime


class DrawingAnalysisResponse(BaseModel):
    fine_motor_score: Optional[int] = None
    cognitive_score: Optional[int] = None
    emotional_tone: Optional[str] = None
    spatial_org_score: Optional[int] = None
    figure_complexity: Optional[int] = None
    ai_summary: str
    domain_flags: Dict[str, str] = {}

    class Config:
        from_attributes = True


class DrawingResponse(BaseModel):
    id: UUID
    child_id: UUID
    image_url: str
    upload_date: date
    context: Optional[str] = None
    created_at: datetime
    analysis: Optional[DrawingAnalysisResponse] = None

    class Config:
        from_attributes = True


class DrawingUploadResponse(BaseModel):
    drawing_id: UUID
    analysis: DrawingAnalysisResponse
    message: str = "Drawing uploaded and analyzed"
