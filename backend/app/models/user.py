import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, TIMESTAMP, Enum as SAEnum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum


class UserRole(str, enum.Enum):
    AWW = "AWW"
    CDPO = "CDPO"
    HEALTH_WORKER = "HEALTH_WORKER"
    STATE_OFFICER = "STATE_OFFICER"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(15), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    role = Column(SAEnum(UserRole, name="user_role"), nullable=False, default=UserRole.AWW)
    awc_id = Column(Integer, ForeignKey("anganwadi_centers.id"), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    language = Column(String(10), nullable=False, default="hi")
    otp_hash = Column(String(255), nullable=True)
    otp_expires = Column(TIMESTAMP(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    awc = relationship("AnganwadiCenter", back_populates="users")
    district = relationship("District", back_populates="users")
    children_registered = relationship("Child", back_populates="registered_by_user", foreign_keys="Child.registered_by")
    observations = relationship("Observation", back_populates="observed_by_user")
    attendance_marked = relationship("Attendance", back_populates="marked_by_user")
    milestone_assessments = relationship("MilestoneAssessment", back_populates="assessed_by_user")
    referrals_generated = relationship("Referral", back_populates="generated_by_user")
    drawings_uploaded = relationship("Drawing", back_populates="uploaded_by_user")
