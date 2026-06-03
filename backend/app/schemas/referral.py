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
    ministry: Optional[str] = None  # alias for department — frontend uses ministry

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj, **kwargs):
        instance = super().model_validate(obj, **kwargs)
        if instance.ministry is None and instance.department:
            instance.ministry = instance.department
        return instance


class ReferralStatusUpdate(BaseModel):
    status: ReferralStatus
    specialist_notes: Optional[str] = None
    appointment_date: Optional[date] = None


class ReferralCreateRequest(BaseModel):
    child_id: UUID
    primary_concern: str
    domains_of_concern: List[str] = []


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
    letter_url: Optional[str] = None  # frontend-friendly alias
    pdrs_at_referral: Optional[int] = None
    domains_flagged: Optional[List[str]] = None
    domains_of_concern: Optional[List[str]] = None  # alias for domains_flagged
    primary_concern: Optional[str] = None  # stored in specialist_notes
    appointment_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj, **kwargs):
        instance = super().model_validate(obj, **kwargs)
        # Map specialist_notes → primary_concern for frontend
        if instance.primary_concern is None:
            raw = getattr(obj, 'specialist_notes', None)
            if raw and not raw.startswith('APPOINTMENT:'):
                instance.primary_concern = raw
        # Map domains_flagged → domains_of_concern
        if instance.domains_of_concern is None:
            instance.domains_of_concern = instance.domains_flagged or []
        # Build letter_url from id
        if instance.letter_url is None:
            instance.letter_url = f"/api/v1/referrals/{instance.id}/letter"
        return instance


class GenerateReferralResponse(BaseModel):
    referral_id: UUID
    facility: Optional[ReferralFacilityResponse] = None
    applicable_schemes: List[str] = []
    letter_preview: str
    letter_pdf_url: str
    whatsapp_message: str
