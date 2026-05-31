from sqlalchemy import Column, Integer, Boolean, ForeignKey, TIMESTAMP, Date, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False)
    date = Column(Date, nullable=False)
    present = Column(Boolean, nullable=False, default=False)
    marked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("child_id", "date", name="uq_attendance_child_date"),
    )

    child = relationship("Child", back_populates="attendance")
    marked_by_user = relationship("User", back_populates="attendance_marked")
