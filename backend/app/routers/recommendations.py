from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from ..database import get_db
from ..models.recommendation import ActivityRecommendation
from ..models.milestone import DevelopmentalDomain
from ..middleware.auth_middleware import get_current_user
from ..models.user import User
from ..services.child_service import get_child, get_age_months
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class RecommendationRequest(BaseModel):
    child_id: UUID
    domain_code: str
    concern: str
    language: str = "hi"


class RecommendationResponse(BaseModel):
    id: UUID
    child_id: UUID
    domain_id: int
    activity_title: str
    activity_description: str
    duration_minutes: int
    parent_sent: bool

    class Config:
        from_attributes = True


@router.get("", response_model=List[RecommendationResponse])
@router.get("/", response_model=List[RecommendationResponse])
def list_recommendations(
    child_id: Optional[UUID] = Query(None),
    domain_code: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get recommendations filtered by child_id query param."""
    if not child_id:
        return []
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    query = db.query(ActivityRecommendation).filter(ActivityRecommendation.child_id == child_id)
    if domain_code:
        domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.code == domain_code).first()
        if domain:
            query = query.filter(ActivityRecommendation.domain_id == domain.id)
    return query.order_by(ActivityRecommendation.generated_at.desc()).limit(20).all()


@router.post("/generate/{child_id}", status_code=status.HTTP_201_CREATED)
async def generate_recommendations_for_child(
    child_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate activity recommendations for a child across all developmental domains."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    age_months = get_age_months(child.date_of_birth)

    from ..ai.recommendations import generate_activity_recommendations
    from ..services.pdrs_service import get_latest_pdrs

    latest_pdrs = get_latest_pdrs(child_id, db)
    concern = "general developmental support"
    if latest_pdrs:
        concern = f"Overall score: {latest_pdrs.overall_score}/100 ({latest_pdrs.risk_level.value} risk)"

    domain_codes = ["PHYSICAL_MOTOR", "LANGUAGE_LITERACY", "COGNITIVE", "SOCIAL_EMOTIONAL"]
    all_saved = []
    for domain_code in domain_codes:
        domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.code == domain_code).first()
        if not domain:
            continue
        try:
            activities = await generate_activity_recommendations(
                child.full_name, age_months, domain_code, concern, "hi"
            )
            for activity in activities[:2]:
                rec = ActivityRecommendation(
                    child_id=child_id,
                    domain_id=domain.id,
                    activity_title=activity.get("title", "Activity"),
                    activity_description=activity.get("description", ""),
                    duration_minutes=activity.get("duration_minutes", 5),
                )
                db.add(rec)
                all_saved.append(rec)
        except Exception as e:
            logger.warning(f"Recs for {domain_code} failed: {e}")

    db.commit()
    return {"count": len(all_saved), "child_name": child.full_name}


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_recommendations(
    data: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate AI-powered activity recommendations for a child's development."""
    child = get_child(data.child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.code == data.domain_code).first()
    if not domain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Domain '{data.domain_code}' not found")

    age_months = get_age_months(child.date_of_birth)

    from ..ai.recommendations import generate_activity_recommendations
    activities = await generate_activity_recommendations(
        child.full_name, age_months, data.domain_code, data.concern, data.language
    )

    saved_recs = []
    for activity in activities:
        rec = ActivityRecommendation(
            child_id=data.child_id,
            domain_id=domain.id,
            activity_title=activity.get("title", "Activity"),
            activity_description=activity.get("description", ""),
            duration_minutes=activity.get("duration_minutes", 5),
        )
        db.add(rec)
        saved_recs.append(activity)

    db.commit()
    return {"recommendations": saved_recs, "count": len(saved_recs), "child_name": child.full_name}


@router.get("/child/{child_id}", response_model=List[RecommendationResponse])
def get_child_recommendations(
    child_id: UUID,
    domain_code: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get activity recommendations for a child."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    query = db.query(ActivityRecommendation).filter(ActivityRecommendation.child_id == child_id)
    if domain_code:
        domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.code == domain_code).first()
        if domain:
            query = query.filter(ActivityRecommendation.domain_id == domain.id)

    return query.order_by(ActivityRecommendation.generated_at.desc()).limit(20).all()
