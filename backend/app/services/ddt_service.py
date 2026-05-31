"""
Developmental Digital Twin (DDT) synthesis service.
Builds the full child developmental portrait.
"""
from datetime import date, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ..models.child import Child
from ..models.pdrs import PDRSScore, DDTSnapshot, RiskLevel
from ..models.observation import Observation, ObservationMarker
from ..models.milestone import MilestoneAssessment, MilestoneLibrary, MilestoneResult, DevelopmentalDomain
from ..services.pdrs_service import get_age_months, get_latest_pdrs, compute_pdrs, save_pdrs_score
import logging

logger = logging.getLogger(__name__)


def get_child_ddt_data(child_id: UUID, db: Session) -> dict:
    """Gather all data needed for a DDT synthesis."""
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise ValueError(f"Child {child_id} not found")

    age_months = get_age_months(child.date_of_birth)

    # Latest PDRS
    latest_pdrs = get_latest_pdrs(child_id, db)
    if not latest_pdrs:
        pdrs_result = compute_pdrs(child_id, db)
        latest_pdrs = save_pdrs_score(child_id, pdrs_result, db)

    # Recent observations (last 30 days, max 10)
    cutoff = date.today() - timedelta(days=30)
    recent_obs = (
        db.query(ObservationMarker, DevelopmentalDomain.code)
        .join(Observation, ObservationMarker.observation_id == Observation.id)
        .join(DevelopmentalDomain, ObservationMarker.domain_id == DevelopmentalDomain.id)
        .filter(Observation.child_id == child_id, Observation.created_at >= cutoff)
        .limit(10)
        .all()
    )

    observations_summary = [
        {
            "domain": domain_code,
            "type": marker.marker_type.value,
            "description": marker.description,
        }
        for marker, domain_code in recent_obs
    ]

    # Missed critical milestones
    due_critical = (
        db.query(MilestoneLibrary, DevelopmentalDomain.code)
        .join(DevelopmentalDomain, MilestoneLibrary.domain_id == DevelopmentalDomain.id)
        .filter(
            MilestoneLibrary.is_critical == True,
            MilestoneLibrary.age_max_months <= age_months,
            MilestoneLibrary.is_active == True,
        )
        .all()
    )

    missed_milestones = []
    for milestone, domain_code in due_critical:
        latest_assessment = (
            db.query(MilestoneAssessment)
            .filter(
                MilestoneAssessment.child_id == child_id,
                MilestoneAssessment.milestone_id == milestone.id,
            )
            .order_by(MilestoneAssessment.assessment_date.desc())
            .first()
        )
        if not latest_assessment or latest_assessment.result == MilestoneResult.NOT_YET:
            missed_milestones.append({
                "domain": domain_code,
                "text": milestone.text,
                "age_min": milestone.age_min_months,
                "age_max": milestone.age_max_months,
            })

    # AWC info
    awc_name = child.awc.name if child.awc else "Anganwadi Center"
    district_name = child.awc.block.district.name if child.awc and child.awc.block else "District"
    state_name = child.awc.block.district.state.name if child.awc and child.awc.block else "State"

    return {
        "child": {
            "id": str(child.id),
            "name": child.full_name,
            "age_months": age_months,
            "gender": child.gender.value,
            "awc_name": awc_name,
            "district": district_name,
            "state": state_name,
        },
        "pdrs": latest_pdrs,
        "domain_scores": latest_pdrs.domain_scores if latest_pdrs else {},
        "observations_summary": observations_summary,
        "missed_milestones": missed_milestones,
    }


def get_school_readiness(overall_score: int) -> tuple:
    if overall_score <= 39:
        return "ON_TRACK", "Child is developing well and appears ready for primary school transition."
    elif overall_score <= 69:
        return "DEVELOPING", "Child is making progress but would benefit from additional support before school entry."
    else:
        return "NEEDS_SUPPORT", "Child requires significant developmental support and specialist assessment before school transition."


def get_latest_ddt(child_id: UUID, db: Session) -> Optional[DDTSnapshot]:
    return (
        db.query(DDTSnapshot)
        .filter(DDTSnapshot.child_id == child_id)
        .order_by(DDTSnapshot.created_at.desc())
        .first()
    )


def build_mock_portrait(child_name: str, age_months: int, domain_scores: dict, missed_milestones: list) -> str:
    age_years = age_months // 12
    age_rem = age_months % 12

    portrait = (
        f"{child_name} is a {age_years} year {age_rem} month old child enrolled at the Anganwadi Center. "
        f"Based on observations, assessments, and developmental data collected by the Anganwadi worker, "
        f"the following portrait has been compiled. "
    )

    # High concern domains
    high_domains = [d for d, s in domain_scores.items() if s >= 60]
    low_domains = [d for d, s in domain_scores.items() if s <= 40]

    if low_domains:
        portrait += f"Strengths have been noted in {', '.join(low_domains).replace('_', ' ').title()}. "

    if high_domains:
        portrait += (
            f"Areas that would benefit from additional support include "
            f"{', '.join(high_domains).replace('_', ' ').title()}. "
        )

    if missed_milestones:
        portrait += (
            f"{len(missed_milestones)} age-appropriate milestone(s) have not yet been observed. "
            f"Focused activities and monitoring are recommended. "
        )

    portrait += (
        "The Anganwadi worker is encouraged to continue regular observations and engage the family "
        "in play-based home activities to support developmental progress."
    )

    return portrait


def create_ddt_snapshot(child_id: UUID, db: Session, use_ai: bool = False) -> DDTSnapshot:
    """Create a new DDT snapshot for the child."""
    data = get_child_ddt_data(child_id, db)
    pdrs = data["pdrs"]
    domain_scores = data["domain_scores"]
    child_info = data["child"]

    school_flag, school_note = get_school_readiness(pdrs.overall_score if pdrs else 50)

    portrait_text = build_mock_portrait(
        child_info["name"],
        child_info["age_months"],
        domain_scores,
        data["missed_milestones"],
    )

    # Detect flags
    asd_flag = (
        domain_scores.get("SOCIAL_EMOTIONAL", 50) >= 70 and
        domain_scores.get("LANGUAGE_LITERACY", 50) >= 65
    )
    speech_delay_flag = domain_scores.get("LANGUAGE_LITERACY", 50) >= 70
    motor_delay_flag = domain_scores.get("PHYSICAL_MOTOR", 50) >= 70

    snapshot = DDTSnapshot(
        child_id=child_id,
        pdrs_score_id=pdrs.id if pdrs else None,
        portrait_text=portrait_text,
        school_readiness_flag=school_flag,
        school_readiness_note=school_note,
        asd_flag=asd_flag,
        speech_delay_flag=speech_delay_flag,
        motor_delay_flag=motor_delay_flag,
        snapshot_data={
            "domain_scores": domain_scores,
            "child": child_info,
            "missed_milestones": data["missed_milestones"],
            "observations_count": len(data["observations_summary"]),
        },
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot
