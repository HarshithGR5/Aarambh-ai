import uuid
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class ActivityRecommendation(Base):
    __tablename__ = "activity_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    domain_id = Column(Integer, ForeignKey("developmental_domains.id"), nullable=False)

    activity_title = Column(Text, nullable=False)
    activity_title_hi = Column(Text, nullable=True)
    activity_title_kn = Column(Text, nullable=True)
    activity_description = Column(Text, nullable=False)
    activity_desc_hi = Column(Text, nullable=True)
    activity_desc_kn = Column(Text, nullable=True)

    age_min_months = Column(Integer, nullable=True)
    age_max_months = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, default=5)

    generated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    parent_sent = Column(Boolean, default=False)
    parent_sent_at = Column(TIMESTAMP(timezone=True), nullable=True)

    child = relationship("Child", back_populates="activity_recommendations")
    domain = relationship("DevelopmentalDomain", back_populates="activity_recommendations")
    parent_interactions = relationship("ParentInteraction", back_populates="recommendation")


class ParentInteraction(Base):
    __tablename__ = "parent_interactions"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("activity_recommendations.id"), nullable=True)

    platform = Column(String(20), nullable=False, default="WHATSAPP")
    message_sent = Column(Text, nullable=True)
    parent_response = Column(Text, nullable=True)
    response_type = Column(String(20), nullable=True)

    interaction_date = Column(TIMESTAMP(timezone=True), server_default=func.now())

    child = relationship("Child", back_populates="parent_interactions")
    recommendation = relationship("ActivityRecommendation", back_populates="parent_interactions")
