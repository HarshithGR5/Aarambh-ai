import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, TIMESTAMP, Date, Text, Enum as SAEnum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum


class GenderType(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class Child(Base):
    __tablename__ = "children"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(200), nullable=False)
    date_of_birth = Column(Date, nullable=False, index=True)
    gender = Column(SAEnum(GenderType, name="gender_type"), nullable=False)
    awc_id = Column(Integer, ForeignKey("anganwadi_centers.id"), nullable=False, index=True)

    parent_name = Column(String(200), nullable=True)
    parent_phone = Column(String(15), nullable=True, index=True)
    parent_language = Column(String(10), default="hi")

    registration_date = Column(Date, nullable=False, server_default=func.current_date())
    registered_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    photo_url = Column(Text, nullable=True)
    qr_code = Column(String(255), unique=True, nullable=True)

    is_active = Column(Boolean, default=True)
    school_entry_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    awc = relationship("AnganwadiCenter", back_populates="children")
    registered_by_user = relationship("User", back_populates="children_registered", foreign_keys=[registered_by])
    observations = relationship("Observation", back_populates="child")
    attendance = relationship("Attendance", back_populates="child")
    milestone_assessments = relationship("MilestoneAssessment", back_populates="child")
    pdrs_scores = relationship("PDRSScore", back_populates="child")
    ddt_snapshots = relationship("DDTSnapshot", back_populates="child")
    drawings = relationship("Drawing", back_populates="child")
    referrals = relationship("Referral", back_populates="child")
    activity_recommendations = relationship("ActivityRecommendation", back_populates="child")
    parent_interactions = relationship("ParentInteraction", back_populates="child")
