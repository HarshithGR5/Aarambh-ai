from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date
from ..database import get_db
from ..schemas.milestone import (
    MilestoneLibraryResponse, MilestoneAssessmentCreate,
    MilestoneAssessmentResponse, ChildMilestoneStatus,
)
from ..models.milestone import DevelopmentalDomain, MilestoneLibrary, MilestoneAssessment, MilestoneResult
from ..middleware.auth_middleware import get_current_user
from ..models.user import User
from ..services.child_service import get_child, get_age_months
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/library", response_model=List[MilestoneLibraryResponse])
def get_milestone_library(
    domain_id: Optional[int] = Query(None),
    age_months: Optional[int] = Query(None, description="Filter by age in months"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all milestones in the library, optionally filtered by domain or age."""
    query = db.query(MilestoneLibrary).filter(MilestoneLibrary.is_active == True)
    if domain_id:
        query = query.filter(MilestoneLibrary.domain_id == domain_id)
    if age_months is not None:
        query = query.filter(
            MilestoneLibrary.age_min_months <= age_months + 6,
            MilestoneLibrary.age_max_months >= age_months - 6,
        )
    return query.order_by(MilestoneLibrary.domain_id, MilestoneLibrary.age_min_months).all()


@router.get("/child/{child_id}/due", response_model=List[ChildMilestoneStatus])
def get_due_milestones(
    child_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get milestones that are due for the child's age."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    age_months = get_age_months(child.date_of_birth)
    milestones = (
        db.query(MilestoneLibrary)
        .filter(
            MilestoneLibrary.is_active == True,
            MilestoneLibrary.age_min_months <= age_months + 3,
            MilestoneLibrary.age_max_months >= age_months - 12,
        )
        .order_by(MilestoneLibrary.age_min_months)
        .all()
    )

    results = []
    for milestone in milestones:
        latest = (
            db.query(MilestoneAssessment)
            .filter(
                MilestoneAssessment.child_id == child_id,
                MilestoneAssessment.milestone_id == milestone.id,
            )
            .order_by(MilestoneAssessment.assessment_date.desc())
            .first()
        )
        is_overdue = (
            milestone.age_max_months <= age_months
            and (not latest or latest.result == MilestoneResult.NOT_YET)
        )
        results.append(ChildMilestoneStatus(
            milestone=milestone,
            latest_result=latest.result if latest else None,
            latest_date=latest.assessment_date if latest else None,
            is_overdue=is_overdue,
        ))

    return results


@router.post("/assess/single", response_model=MilestoneAssessmentResponse, status_code=status.HTTP_201_CREATED)
def submit_single_milestone_assessment(
    child_id: UUID,
    milestone_id: int,
    result: MilestoneResult,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Convenience endpoint to submit a single milestone assessment (query params)."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    today = date.today()
    existing = db.query(MilestoneAssessment).filter(
        MilestoneAssessment.child_id == child_id,
        MilestoneAssessment.milestone_id == milestone_id,
        MilestoneAssessment.assessment_date == today,
    ).first()

    if existing:
        existing.result = result
        existing.notes = notes
        existing.assessed_by = current_user.id
        db.commit()
        db.refresh(existing)
        return existing
    else:
        assessment = MilestoneAssessment(
            child_id=child_id,
            milestone_id=milestone_id,
            result=result,
            assessed_by=current_user.id,
            assessment_date=today,
            notes=notes,
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        return assessment


@router.post("/assess", response_model=List[MilestoneAssessmentResponse], status_code=status.HTTP_201_CREATED)
def submit_milestone_assessment(
    data: MilestoneAssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit milestone assessments for a child."""
    child = get_child(data.child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    today = date.today()
    saved = []
    for item in data.assessments:
        existing = db.query(MilestoneAssessment).filter(
            MilestoneAssessment.child_id == data.child_id,
            MilestoneAssessment.milestone_id == item.milestone_id,
            MilestoneAssessment.assessment_date == today,
        ).first()

        if existing:
            existing.result = item.result
            existing.notes = item.notes
            existing.assessed_by = current_user.id
            saved.append(existing)
        else:
            assessment = MilestoneAssessment(
                child_id=data.child_id,
                milestone_id=item.milestone_id,
                result=item.result,
                assessed_by=current_user.id,
                assessment_date=today,
                notes=item.notes,
            )
            db.add(assessment)
            saved.append(assessment)

    db.commit()
    for s in saved:
        db.refresh(s)

    # Trigger PDRS recompute
    try:
        from ..services.pdrs_service import compute_pdrs, save_pdrs_score
        pdrs_result = compute_pdrs(data.child_id, db)
        save_pdrs_score(data.child_id, pdrs_result, db)
    except Exception as e:
        logger.warning(f"PDRS recompute after milestone assessment failed: {e}")

    return saved


@router.get("/child/{child_id}/status", response_model=List[ChildMilestoneStatus])
def get_child_milestone_status(
    child_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all milestone statuses for a child."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    age_months = get_age_months(child.date_of_birth)
    all_milestones = db.query(MilestoneLibrary).filter(MilestoneLibrary.is_active == True).all()

    results = []
    for milestone in all_milestones:
        latest = (
            db.query(MilestoneAssessment)
            .filter(
                MilestoneAssessment.child_id == child_id,
                MilestoneAssessment.milestone_id == milestone.id,
            )
            .order_by(MilestoneAssessment.assessment_date.desc())
            .first()
        )
        is_overdue = (
            milestone.age_max_months <= age_months
            and (not latest or latest.result == MilestoneResult.NOT_YET)
        )
        results.append(ChildMilestoneStatus(
            milestone=milestone,
            latest_result=latest.result if latest else None,
            latest_date=latest.assessment_date if latest else None,
            is_overdue=is_overdue,
        ))

    return results
