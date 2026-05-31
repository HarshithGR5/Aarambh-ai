from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import List
from ..database import get_db
from ..schemas.dashboard import (
    AWWDashboardResponse, CDPODashboardResponse, DistrictHeatmapResponse,
    AWCHeatmapPoint, AWWStats, Alert, TodayAction, AWCInfo,
)
from ..models.child import Child
from ..models.attendance import Attendance
from ..models.pdrs import PDRSScore, RiskLevel
from ..models.referral import Referral, ReferralStatus
from ..models.observation import Observation
from ..models.geography import AnganwadiCenter, Block, District
from ..middleware.auth_middleware import get_current_user, require_cdpo_or_above
from ..models.user import User, UserRole
from ..services.pdrs_service import get_latest_pdrs
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/aww", response_model=AWWDashboardResponse)
def get_aww_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """AWW home dashboard — today's tasks, alerts, and stats."""
    awc_id = current_user.awc_id
    today = date.today()

    children = db.query(Child).filter(Child.is_active == True)
    if awc_id:
        children = children.filter(Child.awc_id == awc_id)
    children = children.all()

    child_ids = [c.id for c in children]

    # Today's attendance
    present_today = (
        db.query(Attendance)
        .filter(Attendance.child_id.in_(child_ids), Attendance.date == today, Attendance.present == True)
        .count()
    )

    # PDRS risk levels
    red_count = amber_count = green_count = 0
    for child in children:
        pdrs = get_latest_pdrs(child.id, db)
        if pdrs:
            if pdrs.risk_level == RiskLevel.RED:
                red_count += 1
            elif pdrs.risk_level == RiskLevel.AMBER:
                amber_count += 1
            else:
                green_count += 1

    # Overdue referrals (> 30 days, not closed)
    thirty_days_ago = today - timedelta(days=30)
    overdue_referrals = (
        db.query(Referral)
        .filter(
            Referral.child_id.in_(child_ids),
            Referral.referral_date <= thirty_days_ago,
            Referral.status.notin_([ReferralStatus.CLOSED, ReferralStatus.ASSESSED]),
        )
        .count()
    )

    # Alerts: children with no observation in 9+ days
    nine_days_ago = today - timedelta(days=9)
    alerts = []
    for child in children[:5]:  # Limit for performance
        latest_obs = (
            db.query(Observation)
            .filter(Observation.child_id == child.id)
            .order_by(Observation.created_at.desc())
            .first()
        )
        if not latest_obs or latest_obs.created_at.date() < nine_days_ago:
            days_since = (today - (latest_obs.created_at.date() if latest_obs else child.registration_date)).days
            alerts.append(Alert(
                type="NO_OBSERVATION",
                child_id=str(child.id),
                child_name=child.full_name,
                days_ago=days_since,
            ))

    # High risk alerts
    for child in children:
        pdrs = get_latest_pdrs(child.id, db)
        if pdrs and pdrs.risk_level == RiskLevel.RED:
            alerts.append(Alert(
                type="HIGH_RISK_NEW",
                child_id=str(child.id),
                child_name=child.full_name,
                pdrs_score=pdrs.overall_score,
            ))

    # Today's actions
    today_actions = []
    priority = 1
    for child in children:
        pdrs = get_latest_pdrs(child.id, db)
        if pdrs and pdrs.risk_level in [RiskLevel.RED, RiskLevel.AMBER]:
            today_actions.append(TodayAction(
                priority=priority,
                action="CHECK_MILESTONES",
                child_id=str(child.id),
                child_name=child.full_name,
            ))
            priority += 1
        if priority > 10:
            break

    awc_info = None
    if awc_id:
        awc = db.query(AnganwadiCenter).filter(AnganwadiCenter.id == awc_id).first()
        if awc:
            awc_info = AWCInfo(id=awc.id, name=awc.name)

    return AWWDashboardResponse(
        today_date=today,
        awc=awc_info,
        stats=AWWStats(
            total_children=len(children),
            present_today=present_today,
            red_zone_children=red_count,
            amber_zone_children=amber_count,
            green_zone_children=green_count,
            pending_milestones=amber_count + red_count,
            overdue_referrals=overdue_referrals,
        ),
        alerts=alerts[:10],
        today_actions=today_actions[:5],
    )


@router.get("/cdpo", response_model=CDPODashboardResponse)
def get_cdpo_dashboard(
    current_user: User = Depends(require_cdpo_or_above),
    db: Session = Depends(get_db),
):
    """CDPO block overview dashboard."""
    district_id = current_user.district_id
    today = date.today()
    this_month_start = today.replace(day=1)

    query = db.query(AnganwadiCenter)
    if district_id:
        blocks = db.query(Block).filter(Block.district_id == district_id).all()
        block_ids = [b.id for b in blocks]
        query = query.filter(AnganwadiCenter.block_id.in_(block_ids))

    awcs = query.filter(AnganwadiCenter.is_active == True).all()
    awc_ids = [a.id for a in awcs]

    children = db.query(Child).filter(Child.awc_id.in_(awc_ids), Child.is_active == True).all()
    child_ids = [c.id for c in children]

    red_count = amber_count = green_count = 0
    for child in children:
        pdrs = get_latest_pdrs(child.id, db)
        if pdrs:
            if pdrs.risk_level == RiskLevel.RED:
                red_count += 1
            elif pdrs.risk_level == RiskLevel.AMBER:
                amber_count += 1
            else:
                green_count += 1

    referrals_this_month = (
        db.query(Referral)
        .filter(Referral.child_id.in_(child_ids), Referral.referral_date >= this_month_start)
        .count()
    )

    assessed_this_month = (
        db.query(Referral)
        .filter(
            Referral.child_id.in_(child_ids),
            Referral.referral_date >= this_month_start,
            Referral.status == ReferralStatus.ASSESSED,
        )
        .count()
    )

    completion_rate = (assessed_this_month / referrals_this_month * 100) if referrals_this_month > 0 else 0.0

    district_name = "Block"
    if district_id:
        district = db.query(District).filter(District.id == district_id).first()
        if district:
            district_name = district.name

    return CDPODashboardResponse(
        block_name=district_name,
        total_awcs=len(awcs),
        total_children=len(children),
        red_zone_children=red_count,
        amber_zone_children=amber_count,
        green_zone_children=green_count,
        referrals_this_month=referrals_this_month,
        referral_completion_rate=round(completion_rate, 1),
        inactive_awws=0,
    )


@router.get("/overview")
def get_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """General overview dashboard stats."""
    total_children = db.query(Child).filter(Child.is_active == True).count()
    total_awcs = db.query(AnganwadiCenter).filter(AnganwadiCenter.is_active == True).count()
    total_referrals = db.query(Referral).count()

    return {
        "total_children": total_children,
        "total_awcs": total_awcs,
        "total_referrals": total_referrals,
        "platform": "Aarambh AI",
        "version": "1.0.0",
    }


@router.get("/district/{district_id}/heatmap", response_model=DistrictHeatmapResponse)
def get_district_heatmap(
    district_id: int,
    current_user: User = Depends(require_cdpo_or_above),
    db: Session = Depends(get_db),
):
    """Get AWC risk heatmap data for a district."""
    district = db.query(District).filter(District.id == district_id).first()
    if not district:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="District not found")

    blocks = db.query(Block).filter(Block.district_id == district_id).all()
    block_ids = [b.id for b in blocks]
    awcs = db.query(AnganwadiCenter).filter(AnganwadiCenter.block_id.in_(block_ids), AnganwadiCenter.is_active == True).all()

    awc_points = []
    for awc in awcs:
        children = db.query(Child).filter(Child.awc_id == awc.id, Child.is_active == True).all()
        child_ids = [c.id for c in children]

        red_count = amber_count = green_count = 0
        scores = []
        for child in children:
            pdrs = get_latest_pdrs(child.id, db)
            if pdrs:
                scores.append(pdrs.overall_score)
                if pdrs.risk_level == RiskLevel.RED:
                    red_count += 1
                elif pdrs.risk_level == RiskLevel.AMBER:
                    amber_count += 1
                else:
                    green_count += 1

        avg_score = sum(scores) / len(scores) if scores else None
        risk_level = None
        if avg_score is not None:
            if avg_score >= 70:
                risk_level = "RED"
            elif avg_score >= 40:
                risk_level = "AMBER"
            else:
                risk_level = "GREEN"

        awc_points.append(AWCHeatmapPoint(
            awc_id=awc.id,
            awc_name=awc.name,
            latitude=float(awc.latitude) if awc.latitude else None,
            longitude=float(awc.longitude) if awc.longitude else None,
            total_children=len(children),
            avg_pdrs_score=round(avg_score, 1) if avg_score else None,
            risk_level=risk_level,
            red_count=red_count,
            amber_count=amber_count,
            green_count=green_count,
        ))

    return DistrictHeatmapResponse(
        district_id=district_id,
        district_name=district.name,
        awc_points=awc_points,
    )
