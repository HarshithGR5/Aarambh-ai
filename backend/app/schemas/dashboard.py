from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date


class AWWStats(BaseModel):
    total_children: int
    present_today: int
    red_zone_children: int
    amber_zone_children: int
    green_zone_children: int
    pending_milestones: int
    overdue_referrals: int


class Alert(BaseModel):
    type: str
    child_id: Optional[str] = None
    child_name: Optional[str] = None
    days_ago: Optional[int] = None
    pdrs_score: Optional[int] = None
    referral_id: Optional[str] = None


class TodayAction(BaseModel):
    priority: int
    action: str
    child_id: Optional[str] = None
    child_name: Optional[str] = None
    referral_id: Optional[str] = None


class AWCInfo(BaseModel):
    id: int
    name: str


class AWWDashboardResponse(BaseModel):
    today_date: date
    awc: Optional[AWCInfo] = None
    stats: AWWStats
    alerts: List[Alert] = []
    today_actions: List[TodayAction] = []


class CDPODashboardResponse(BaseModel):
    block_name: str
    total_awcs: int
    total_children: int
    red_zone_children: int
    amber_zone_children: int
    green_zone_children: int
    referrals_this_month: int
    referral_completion_rate: float
    inactive_awws: int


class AWCHeatmapPoint(BaseModel):
    awc_id: int
    awc_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_children: int
    avg_pdrs_score: Optional[float] = None
    risk_level: Optional[str] = None
    red_count: int
    amber_count: int
    green_count: int


class DistrictHeatmapResponse(BaseModel):
    district_id: int
    district_name: str
    awc_points: List[AWCHeatmapPoint] = []
