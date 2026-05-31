import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Date, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Drawing(Base):
    __tablename__ = "drawings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    image_url = Column(Text, nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    upload_date = Column(Date, nullable=False, server_default=func.current_date())
    context = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    child = relationship("Child", back_populates="drawings")
    uploaded_by_user = relationship("User", back_populates="drawings_uploaded")
    analysis = relationship("DrawingAnalysis", back_populates="drawing", uselist=False)


class DrawingAnalysis(Base):
    __tablename__ = "drawing_analyses"

    id = Column(Integer, primary_key=True, index=True)
    drawing_id = Column(UUID(as_uuid=True), ForeignKey("drawings.id"), nullable=False, unique=True)

    fine_motor_score = Column(Integer, nullable=True)
    cognitive_score = Column(Integer, nullable=True)
    emotional_tone = Column(String(50), nullable=True)
    spatial_org_score = Column(Integer, nullable=True)
    figure_complexity = Column(Integer, nullable=True)

    ai_summary = Column(Text, nullable=False)
    ai_summary_hi = Column(Text, nullable=True)

    domain_flags = Column(JSONB, default={})
    analyzed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    model_used = Column(String(50), nullable=True)

    drawing = relationship("Drawing", back_populates="analysis")
