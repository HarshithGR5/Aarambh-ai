from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime
from ..models.referral import ReferralStatus


class ReferralFacilityResponse(BaseModel):
    id: int
    name: str
    facility_type: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    available_days: Optional[str] = None
    available_time: Optional[str] = None
    specialties: Optional[List[str]] = None

    class Config:
        from_attributes = True


class GovernmentSchemeResponse(BaseModel):
    id: int
    name: str
    code: str
    description: str
    eligibility_criteria: Optional[str] = None
    department: Optional[str] = None

    class Config:
        from_attributes = True


class ReferralStatusUpdate(BaseModel):
    status: ReferralStatus
    specialist_notes: Optional[str] = None
    appointment_date: Optional[date] = None


class ReferralResponse(BaseModel):
    id: UUID
    child_id: UUID
    facility_id: Optional[int] = None
    referral_date: date
    status: ReferralStatus
    letter_text: str
    letter_text_hi: Optional[str] = None
    letter_text_kn: Optional[str] = None
    letter_pdf_url: Optional[str] = None
    pdrs_at_referral: Optional[int] = None
    domains_flagged: Optional[List[str]] = None
    appointment_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GenerateReferralResponse(BaseModel):
    referral_id: UUID
    facility: Optional[ReferralFacilityResponse] = None
    applicable_schemes: List[str] = []
    letter_preview: str
    letter_pdf_url: str
    whatsapp_message: str
