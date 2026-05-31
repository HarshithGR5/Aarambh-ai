import uuid
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, Date, Text, Enum as SAEnum, Table, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum


class ReferralStatus(str, enum.Enum):
    GENERATED = "GENERATED"
    SENT_TO_PARENT = "SENT_TO_PARENT"
    APPOINTMENT_SCHEDULED = "APPOINTMENT_SCHEDULED"
    ASSESSED = "ASSESSED"
    FOLLOW_UP_NEEDED = "FOLLOW_UP_NEEDED"
    CLOSED = "CLOSED"


referral_schemes = Table(
    "referral_schemes",
    Base.metadata,
    Column("referral_id", UUID(as_uuid=True), ForeignKey("referrals.id"), primary_key=True),
    Column("scheme_id", Integer, ForeignKey("government_schemes.id"), primary_key=True),
)


class ReferralFacility(Base):
    __tablename__ = "referral_facilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    facility_type = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    phone = Column(String(20), nullable=True)
    available_days = Column(Text, nullable=True)
    available_time = Column(String(50), nullable=True)
    specialties = Column(ARRAY(Text), nullable=True)
    is_active = Column(Boolean, default=True)

    district = relationship("District", back_populates="referral_facilities")
    referrals = relationship("Referral", back_populates="facility")


class GovernmentScheme(Base):
    __tablename__ = "government_schemes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    description_hi = Column(Text, nullable=True)
    eligibility_criteria = Column(Text, nullable=True)
    apply_url = Column(Text, nullable=True)
    department = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)

    referrals = relationship("Referral", secondary=referral_schemes, back_populates="schemes")


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    facility_id = Column(Integer, ForeignKey("referral_facilities.id"), nullable=True)

    referral_date = Column(Date, nullable=False, server_default=func.current_date())
    status = Column(SAEnum(ReferralStatus, name="referral_status"), nullable=False, default=ReferralStatus.GENERATED)

    letter_text = Column(Text, nullable=False)
    letter_text_kn = Column(Text, nullable=True)
    letter_text_hi = Column(Text, nullable=True)
    letter_pdf_url = Column(Text, nullable=True)

    pdrs_at_referral = Column(Integer, nullable=True)
    domains_flagged = Column(ARRAY(Text), nullable=True)

    parent_notified_at = Column(TIMESTAMP(timezone=True), nullable=True)
    appointment_date = Column(Date, nullable=True)
    specialist_notes = Column(Text, nullable=True)
    resolved_at = Column(TIMESTAMP(timezone=True), nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    child = relationship("Child", back_populates="referrals")
    generated_by_user = relationship("User", back_populates="referrals_generated")
    facility = relationship("ReferralFacility", back_populates="referrals")
    schemes = relationship("GovernmentScheme", secondary=referral_schemes, back_populates="referrals")
