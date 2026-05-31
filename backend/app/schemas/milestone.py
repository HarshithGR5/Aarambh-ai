from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from ..models.milestone import MilestoneResult


class MilestoneLibraryResponse(BaseModel):
    id: int
    domain_id: int
    text: str
    text_hi: Optional[str] = None
    text_kn: Optional[str] = None
    age_min_months: int
    age_max_months: int
    is_critical: bool
    source: Optional[str] = None

    class Config:
        from_attributes = True


class SingleAssessment(BaseModel):
    milestone_id: int
    result: MilestoneResult
    notes: Optional[str] = None


class MilestoneAssessmentCreate(BaseModel):
    child_id: UUID
    assessments: List[SingleAssessment] = Field(..., min_length=1)


class MilestoneAssessmentResponse(BaseModel):
    id: int
    child_id: UUID
    milestone_id: int
    result: MilestoneResult
    assessment_date: date
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class ChildMilestoneStatus(BaseModel):
    milestone: MilestoneLibraryResponse
    latest_result: Optional[MilestoneResult] = None
    latest_date: Optional[date] = None
    is_overdue: bool = False
