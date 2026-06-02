from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from ..database import get_db
from ..schemas.child import ChildCreate, ChildUpdate, ChildResponse, ChildWithAgeResponse
from ..schemas.pdrs import DDTSnapshotResponse, PDRSResponse
from ..services.child_service import (
    create_child, get_child, get_all_children, update_child, enrich_child_with_age
)
from ..services.pdrs_service import get_latest_pdrs
from ..services.ddt_service import get_latest_ddt, create_ddt_snapshot, get_child_ddt_data
from ..middleware.auth_middleware import get_current_user
from ..models.user import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=ChildWithAgeResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ChildWithAgeResponse, status_code=status.HTTP_201_CREATED)
def create_child_endpoint(
    data: ChildCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Register a new child at the AWC."""
    child = create_child(data.model_dump(), current_user.id, db)
    result = enrich_child_with_age(child)
    latest_pdrs = get_latest_pdrs(child.id, db)
    if latest_pdrs:
        result["latest_pdrs_score"] = latest_pdrs.overall_score
        result["latest_risk_level"] = latest_pdrs.risk_level.value
    return result


@router.get("", response_model=List[ChildWithAgeResponse])
@router.get("/", response_model=List[ChildWithAgeResponse])
def list_children(
    awc_id: Optional[int] = Query(None, description="Filter by AWC ID"),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all children. AWW sees their AWC children only (unless admin/CDPO)."""
    from ..models.user import UserRole
    effective_awc_id = awc_id
    if current_user.role == UserRole.AWW and current_user.awc_id:
        effective_awc_id = current_user.awc_id

    children = get_all_children(db, awc_id=effective_awc_id, limit=limit, offset=offset)
    results = []
    for child in children:
        enriched = enrich_child_with_age(child)
        pdrs = get_latest_pdrs(child.id, db)
        if pdrs:
            enriched["latest_pdrs_score"] = pdrs.overall_score
            enriched["latest_risk_level"] = pdrs.risk_level.value
        results.append(enriched)
    return results


@router.get("/{child_id}", response_model=ChildWithAgeResponse)
def get_child_endpoint(
    child_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific child's profile."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")
    result = enrich_child_with_age(child)
    pdrs = get_latest_pdrs(child.id, db)
    if pdrs:
        result["latest_pdrs_score"] = pdrs.overall_score
        result["latest_risk_level"] = pdrs.risk_level.value
    return result


@router.put("/{child_id}", response_model=ChildWithAgeResponse)
def update_child_endpoint(
    child_id: UUID,
    data: ChildUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update child profile."""
    child = update_child(child_id, data.model_dump(exclude_unset=True), db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")
    return enrich_child_with_age(child)


@router.get("/{child_id}/ddt")
def get_child_ddt(
    child_id: UUID,
    refresh: bool = Query(False, description="Force regenerate DDT snapshot"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the Developmental Digital Twin snapshot for a child.
    Returns {child, ddt, pdrs, recent_observations} as expected by the frontend."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    if refresh:
        create_ddt_snapshot(child_id, db)

    return get_child_ddt_data(child_id, db)
