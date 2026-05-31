from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from ..models.child import GenderType


class ChildCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    date_of_birth: date
    gender: GenderType
    awc_id: int
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    parent_language: str = "hi"
    notes: Optional[str] = None


class ChildUpdate(BaseModel):
    full_name: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    parent_language: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    school_entry_date: Optional[date] = None


class AWCInfo(BaseModel):
    id: int
    name: str
    center_number: str

    class Config:
        from_attributes = True


class ChildResponse(BaseModel):
    id: UUID
    full_name: str
    date_of_birth: date
    gender: GenderType
    awc_id: int
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    parent_language: str
    registration_date: date
    photo_url: Optional[str] = None
    qr_code: Optional[str] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChildWithAgeResponse(ChildResponse):
    age_months: int
    age_years: int
    age_months_remainder: int
    latest_pdrs_score: Optional[int] = None
    latest_risk_level: Optional[str] = None
