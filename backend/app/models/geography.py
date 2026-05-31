from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(5), nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    districts = relationship("District", back_populates="state")


class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    state = relationship("State", back_populates="districts")
    blocks = relationship("Block", back_populates="district")
    users = relationship("User", back_populates="district")
    referral_facilities = relationship("ReferralFacility", back_populates="district")


class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    district = relationship("District", back_populates="blocks")
    anganwadi_centers = relationship("AnganwadiCenter", back_populates="block")


class AnganwadiCenter(Base):
    __tablename__ = "anganwadi_centers"

    id = Column(Integer, primary_key=True, index=True)
    center_number = Column(String(20), nullable=False, unique=True)
    name = Column(String(200), nullable=False)
    village = Column(String(100), nullable=True)
    block_id = Column(Integer, ForeignKey("blocks.id"), nullable=False)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    block = relationship("Block", back_populates="anganwadi_centers")
    users = relationship("User", back_populates="awc")
    children = relationship("Child", back_populates="awc")
