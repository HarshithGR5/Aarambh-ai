from sqlalchemy import Column, Integer, Boolean, ForeignKey, TIMESTAMP, Date, Text, String, Enum as SAEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum


class MilestoneResult(str, enum.Enum):
    YES = "YES"
    SOMETIMES = "SOMETIMES"
    NOT_YET = "NOT_YET"
    NA = "NA"


class DevelopmentalDomain(Base):
    __tablename__ = "developmental_domains"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    name_hi = Column(String(100), nullable=True)
    name_kn = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=False)
    color_hex = Column(String(7), nullable=True)

    milestones = relationship("MilestoneLibrary", back_populates="domain")
    observation_markers = relationship("ObservationMarker", back_populates="domain")
    activity_recommendations = relationship("ActivityRecommendation", back_populates="domain")


class MilestoneLibrary(Base):
    __tablename__ = "milestone_library"

    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("developmental_domains.id"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    text_hi = Column(Text, nullable=True)
    text_kn = Column(Text, nullable=True)
    age_min_months = Column(Integer, nullable=False, index=True)
    age_max_months = Column(Integer, nullable=False, index=True)
    is_critical = Column(Boolean, default=False)
    source = Column(String(100), nullable=True)
    display_order = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)

    domain = relationship("DevelopmentalDomain", back_populates="milestones")
    assessments = relationship("MilestoneAssessment", back_populates="milestone")


class MilestoneAssessment(Base):
    __tablename__ = "milestone_assessments"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    milestone_id = Column(Integer, ForeignKey("milestone_library.id"), nullable=False)
    result = Column(SAEnum(MilestoneResult, name="milestone_result"), nullable=False)
    assessed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assessment_date = Column(Date, nullable=False, server_default=func.current_date())
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("child_id", "milestone_id", "assessment_date", name="uq_assessment_child_milestone_date"),
    )

    child = relationship("Child", back_populates="milestone_assessments")
    milestone = relationship("MilestoneLibrary", back_populates="assessments")
    assessed_by_user = relationship("User", back_populates="milestone_assessments")
