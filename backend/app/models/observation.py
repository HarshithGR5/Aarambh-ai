import uuid
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, Text, Numeric, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum


class ObservationType(str, enum.Enum):
    VOICE = "VOICE"
    TEXT = "TEXT"
    GUIDED_PLAY = "GUIDED_PLAY"
    PARENT_REPORT = "PARENT_REPORT"


class MarkerType(str, enum.Enum):
    POSITIVE = "POSITIVE"
    CONCERN = "CONCERN"
    FLAG = "FLAG"


class MarkerSeverity(str, enum.Enum):
    MILD = "MILD"
    MODERATE = "MODERATE"
    SIGNIFICANT = "SIGNIFICANT"


class Observation(Base):
    __tablename__ = "observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    observed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    observation_type = Column(SAEnum(ObservationType, name="observation_type"), nullable=False, default=ObservationType.VOICE)

    raw_text = Column(Text, nullable=True)
    audio_url = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)
    transcript_lang = Column(String(10), nullable=True)
    english_text = Column(Text, nullable=True)
    processing_status = Column(String(20), default="PENDING")

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)

    child = relationship("Child", back_populates="observations")
    observed_by_user = relationship("User", back_populates="observations")
    markers = relationship("ObservationMarker", back_populates="observation", cascade="all, delete-orphan")


class ObservationMarker(Base):
    __tablename__ = "observation_markers"

    id = Column(Integer, primary_key=True, index=True)
    observation_id = Column(UUID(as_uuid=True), ForeignKey("observations.id"), nullable=False, index=True)
    domain_id = Column(Integer, ForeignKey("developmental_domains.id"), nullable=False)
    marker_type = Column(SAEnum(MarkerType, name="marker_type"), nullable=False)
    severity = Column(SAEnum(MarkerSeverity, name="marker_severity"), nullable=True)
    description = Column(Text, nullable=False)
    description_hi = Column(Text, nullable=True)
    ai_extracted = Column(Boolean, default=True)
    confidence = Column(Numeric(3, 2), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    observation = relationship("Observation", back_populates="markers")
    domain = relationship("DevelopmentalDomain", back_populates="observation_markers")
