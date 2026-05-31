from pydantic import BaseModel
from typing import Optional, Dict, List
from uuid import UUID
from datetime import datetime
from ..models.pdrs import RiskLevel


class PDRSResponse(BaseModel):
    id: int
    child_id: UUID
    overall_score: int
    risk_level: RiskLevel
    domain_scores: Dict[str, float]
    computed_at: datetime
    computed_by: str

    class Config:
        from_attributes = True


class PDRSComputeResponse(BaseModel):
    overall_score: int
    risk_level: RiskLevel
    domain_scores: Dict[str, float]
    input_snapshot: Optional[dict] = None
    message: str = "PDRS computed successfully"


class DDTSnapshotResponse(BaseModel):
    id: int
    child_id: UUID
    portrait_text: str
    portrait_text_hi: Optional[str] = None
    school_readiness_flag: Optional[str] = None
    school_readiness_note: Optional[str] = None
    asd_flag: bool
    speech_delay_flag: bool
    motor_delay_flag: bool
    snapshot_data: dict
    created_at: datetime
    pdrs_score: Optional[PDRSResponse] = None

    class Config:
        from_attributes = True
