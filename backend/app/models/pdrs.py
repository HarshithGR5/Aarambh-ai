from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum


class RiskLevel(str, enum.Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"


class PDRSScore(Base):
    __tablename__ = "pdrs_scores"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    overall_score = Column(Integer, nullable=False)
    risk_level = Column(SAEnum(RiskLevel, name="risk_level"), nullable=False)
    domain_scores = Column(JSONB, nullable=False, default={})
    input_snapshot = Column(JSONB, nullable=True)
    computed_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    computed_by = Column(String(20), default="AUTO")

    child = relationship("Child", back_populates="pdrs_scores")
    ddt_snapshots = relationship("DDTSnapshot", back_populates="pdrs_score")


class DDTSnapshot(Base):
    __tablename__ = "ddt_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    pdrs_score_id = Column(Integer, ForeignKey("pdrs_scores.id"), nullable=True)

    portrait_text = Column(Text, nullable=False)
    portrait_text_hi = Column(Text, nullable=True)

    school_readiness_flag = Column(String(20), nullable=True)
    school_readiness_note = Column(Text, nullable=True)

    asd_flag = Column(Boolean, default=False)
    speech_delay_flag = Column(Boolean, default=False)
    motor_delay_flag = Column(Boolean, default=False)

    snapshot_data = Column(JSONB, nullable=False, default={})
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    child = relationship("Child", back_populates="ddt_snapshots")
    pdrs_score = relationship("PDRSScore", back_populates="ddt_snapshots")
