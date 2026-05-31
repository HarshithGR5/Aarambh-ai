"""
PDRS (Predictive Development Risk Score) — Rule-based weighted model.
Score range: 0-100. Higher = more concern.
Risk levels: GREEN (0-39), AMBER (40-69), RED (70-100)
"""
from datetime import date, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ..models.child import Child
from ..models.observation import ObservationMarker, MarkerType, MarkerSeverity
from ..models.milestone import MilestoneAssessment, MilestoneLibrary, MilestoneResult
from ..models.attendance import Attendance
from ..models.drawing import DrawingAnalysis, Drawing
from ..models.pdrs import PDRSScore, RiskLevel
import logging

logger = logging.getLogger(__name__)

DOMAIN_WEIGHTS = {
    "PHYSICAL_MOTOR":    0.15,
    "LANGUAGE_LITERACY": 0.25,
    "COGNITIVE":         0.20,
    "SOCIAL_EMOTIONAL":  0.25,
    "AESTHETIC_CULTURAL":0.05,
    "LEARNING_HABITS":   0.10,
}

MARKER_TYPE_SCORES = {
    MarkerType.FLAG:     80,
    MarkerType.CONCERN:  50,
    MarkerType.POSITIVE: -20,
}

SEVERITY_MULTIPLIERS = {
    MarkerSeverity.SIGNIFICANT: 1.5,
    MarkerSeverity.MODERATE:    1.0,
    MarkerSeverity.MILD:        0.6,
}


def get_age_months(dob: date) -> int:
    today = date.today()
    months = (today.year - dob.year) * 12 + (today.month - dob.month)
    if today.day < dob.day:
        months -= 1
    return max(0, months)


def compute_pdrs(child_id: UUID, db: Session) -> dict:
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise ValueError(f"Child {child_id} not found")

    domain_risk_scores = {domain: 50 for domain in DOMAIN_WEIGHTS}
    input_snapshot = {}

    # 1. Observation markers (last 90 days)
    cutoff = date.today() - timedelta(days=90)
    from ..models.observation import Observation
    from ..models.milestone import DevelopmentalDomain

    markers = (
        db.query(ObservationMarker, DevelopmentalDomain.code)
        .join(Observation, ObservationMarker.observation_id == Observation.id)
        .join(DevelopmentalDomain, ObservationMarker.domain_id == DevelopmentalDomain.id)
        .filter(
            Observation.child_id == child_id,
            Observation.created_at >= cutoff,
        )
        .all()
    )

    marker_count = 0
    for marker, domain_code in markers:
        if domain_code in domain_risk_scores:
            base = MARKER_TYPE_SCORES.get(marker.marker_type, 0)
            multiplier = SEVERITY_MULTIPLIERS.get(marker.severity, 1.0) if marker.severity else 1.0
            domain_risk_scores[domain_code] += base * multiplier
            marker_count += 1

    input_snapshot["markers_analyzed"] = marker_count

    # 2. Missed critical milestones
    age_months = get_age_months(child.date_of_birth)
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

    missed_critical = 0
    for milestone, domain_code in due_critical:
        latest = (
            db.query(MilestoneAssessment)
            .filter(
                MilestoneAssessment.child_id == child_id,
                MilestoneAssessment.milestone_id == milestone.id,
            )
            .order_by(MilestoneAssessment.assessment_date.desc())
            .first()
        )
        if not latest or latest.result == MilestoneResult.NOT_YET:
            if domain_code in domain_risk_scores:
                domain_risk_scores[domain_code] += 15
                missed_critical += 1

    input_snapshot["missed_critical_milestones"] = missed_critical

    # 3. Attendance rate (last 30 days)
    thirty_days_ago = date.today() - timedelta(days=30)
    attendance_records = (
        db.query(Attendance)
        .filter(Attendance.child_id == child_id, Attendance.date >= thirty_days_ago)
        .all()
    )

    if attendance_records:
        attendance_rate = sum(1 for a in attendance_records if a.present) / len(attendance_records)
        if attendance_rate < 0.5:
            for domain in domain_risk_scores:
                domain_risk_scores[domain] += 10
        input_snapshot["attendance_rate"] = round(attendance_rate, 2)
    else:
        input_snapshot["attendance_rate"] = None

    # 4. Drawing analysis
    latest_drawing = (
        db.query(Drawing)
        .filter(Drawing.child_id == child_id)
        .order_by(Drawing.created_at.desc())
        .first()
    )

    if latest_drawing and latest_drawing.analysis:
        analysis = latest_drawing.analysis
        if analysis.fine_motor_score and analysis.fine_motor_score < 40:
            domain_risk_scores["PHYSICAL_MOTOR"] += 20
        if analysis.cognitive_score and analysis.cognitive_score < 40:
            domain_risk_scores["COGNITIVE"] += 20
        input_snapshot["drawing_analyzed"] = True
    else:
        input_snapshot["drawing_analyzed"] = False

    # Clamp all to 0-100
    domain_risk_scores = {k: max(0, min(100, round(v))) for k, v in domain_risk_scores.items()}

    # Weighted overall score
    overall = sum(
        domain_risk_scores.get(domain, 50) * weight
        for domain, weight in DOMAIN_WEIGHTS.items()
    )
    overall = round(max(0, min(100, overall)))

    # Risk level
    if overall <= 39:
        risk_level = RiskLevel.GREEN
    elif overall <= 69:
        risk_level = RiskLevel.AMBER
    else:
        risk_level = RiskLevel.RED

    input_snapshot["age_months"] = age_months

    return {
        "overall_score": overall,
        "risk_level": risk_level,
        "domain_scores": domain_risk_scores,
        "input_snapshot": input_snapshot,
    }


def save_pdrs_score(child_id: UUID, result: dict, db: Session) -> PDRSScore:
    score = PDRSScore(
        child_id=child_id,
        overall_score=result["overall_score"],
        risk_level=result["risk_level"],
        domain_scores=result["domain_scores"],
        input_snapshot=result.get("input_snapshot"),
    )
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


def get_latest_pdrs(child_id: UUID, db: Session) -> Optional[PDRSScore]:
    return (
        db.query(PDRSScore)
        .filter(PDRSScore.child_id == child_id)
        .order_by(PDRSScore.computed_at.desc())
        .first()
    )
