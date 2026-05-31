from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..database import get_db
from ..schemas.pdrs import PDRSResponse, PDRSComputeResponse, DDTSnapshotResponse
from ..models.pdrs import PDRSScore
from ..services.pdrs_service import compute_pdrs, save_pdrs_score, get_latest_pdrs
from ..services.ddt_service import create_ddt_snapshot, get_latest_ddt
from ..middleware.auth_middleware import get_current_user
from ..models.user import User
from ..services.child_service import get_child
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/compute/{child_id}", response_model=PDRSComputeResponse)
def compute_pdrs_endpoint(
    child_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Recompute PDRS from all available data for a child."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    try:
        result = compute_pdrs(child_id, db)
        save_pdrs_score(child_id, result, db)
        return PDRSComputeResponse(**result)
    except Exception as e:
        logger.error(f"PDRS computation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/child/{child_id}/latest", response_model=PDRSResponse)
def get_latest_pdrs_endpoint(
    child_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the latest PDRS score for a child. Computes if none exists."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    pdrs = get_latest_pdrs(child_id, db)
    if not pdrs:
        result = compute_pdrs(child_id, db)
        pdrs = save_pdrs_score(child_id, result, db)
    return pdrs


@router.get("/child/{child_id}/history", response_model=List[PDRSResponse])
def get_pdrs_history(
    child_id: UUID,
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get PDRS score history (trend) for a child."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    return (
        db.query(PDRSScore)
        .filter(PDRSScore.child_id == child_id)
        .order_by(PDRSScore.computed_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/awc/{awc_id}/summary")
def get_awc_pdrs_summary(
    awc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get PDRS summary for all children in an AWC."""
    from ..models.child import Child
    children = db.query(Child).filter(Child.awc_id == awc_id, Child.is_active == True).all()

    summary = []
    for child in children:
        pdrs = get_latest_pdrs(child.id, db)
        summary.append({
            "child_id": str(child.id),
            "child_name": child.full_name,
            "pdrs_score": pdrs.overall_score if pdrs else None,
            "risk_level": pdrs.risk_level.value if pdrs else None,
            "domain_scores": pdrs.domain_scores if pdrs else {},
        })

    return {
        "awc_id": awc_id,
        "total_children": len(children),
        "red_count": sum(1 for s in summary if s["risk_level"] == "RED"),
        "amber_count": sum(1 for s in summary if s["risk_level"] == "AMBER"),
        "green_count": sum(1 for s in summary if s["risk_level"] == "GREEN"),
        "children": summary,
    }


# ── DDT Endpoints ─────────────────────────────────────────────────────────────

@router.get("/child/{child_id}/ddt", response_model=DDTSnapshotResponse)
def get_ddt_snapshot(
    child_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the latest Developmental Digital Twin snapshot for a child.
    Creates one if it does not exist."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    snapshot = get_latest_ddt(child_id, db)
    if not snapshot:
        try:
            snapshot = create_ddt_snapshot(child_id, db)
        except Exception as e:
            logger.error(f"DDT snapshot creation failed: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return snapshot


@router.post("/child/{child_id}/ddt/refresh", response_model=DDTSnapshotResponse)
def refresh_ddt_snapshot(
    child_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Force-create a fresh Developmental Digital Twin snapshot for a child."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    try:
        snapshot = create_ddt_snapshot(child_id, db)
        return snapshot
    except Exception as e:
        logger.error(f"DDT refresh failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
