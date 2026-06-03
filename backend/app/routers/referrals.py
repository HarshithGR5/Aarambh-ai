from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from ..database import get_db
from ..schemas.referral import (
    ReferralResponse, GenerateReferralResponse, ReferralStatusUpdate,
    ReferralFacilityResponse, GovernmentSchemeResponse, ReferralCreateRequest,
)
from ..models.referral import Referral, ReferralFacility, GovernmentScheme
from ..services.referral_service import create_referral
from ..middleware.auth_middleware import get_current_user
from ..models.user import User
from ..services.child_service import get_child
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", status_code=201)
@router.post("/", status_code=201)
def create_referral_post(
    data: ReferralCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a referral with primary concern and domains of concern.
    Calls the referral generation service and stores primary_concern in specialist_notes."""
    child = get_child(data.child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    try:
        result = create_referral(data.child_id, current_user.id, db)
        referral = result["referral"]

        # Store primary_concern in specialist_notes; store domains in domains_flagged
        referral.specialist_notes = data.primary_concern
        if data.domains_of_concern:
            referral.domains_flagged = data.domains_of_concern
        db.commit()
        db.refresh(referral)

        return {
            "id": str(referral.id),
            "child_id": str(referral.child_id),
            "primary_concern": data.primary_concern,
            "domains_of_concern": data.domains_of_concern or referral.domains_flagged or [],
            "referral_date": str(referral.referral_date),
            "status": referral.status.value if hasattr(referral.status, "value") else str(referral.status),
            "letter_url": f"/api/v1/referrals/{referral.id}/letter",
            "letter_text": referral.letter_text,
        }
    except Exception as e:
        logger.error(f"Referral creation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("", response_model=List[ReferralResponse])
@router.get("/", response_model=List[ReferralResponse])
def list_referrals(
    child_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List referrals. AWW sees their AWC's children; HEALTH_WORKER/CDPO/ADMIN see all."""
    from ..models.user import UserRole
    query = db.query(Referral)

    if child_id:
        query = query.filter(Referral.child_id == child_id)

    if status and status not in ("ALL", ""):
        query = query.filter(Referral.status == status)

    if current_user.role == UserRole.AWW and current_user.awc_id:
        from ..models.child import Child
        awc_child_ids = db.query(Child.id).filter(Child.awc_id == current_user.awc_id).subquery()
        query = query.filter(Referral.child_id.in_(awc_child_ids))

    return query.order_by(Referral.created_at.desc()).offset(offset).limit(limit).all()


@router.post("/generate/{child_id}", response_model=GenerateReferralResponse)
def generate_referral(
    child_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a referral letter and identify applicable government schemes."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    try:
        result = create_referral(child_id, current_user.id, db)
        referral = result["referral"]
        facility = result["facility"]

        return GenerateReferralResponse(
            referral_id=referral.id,
            facility=facility,
            applicable_schemes=result["scheme_codes"],
            letter_preview=result["letter_text"][:500] + "..." if len(result["letter_text"]) > 500 else result["letter_text"],
            letter_pdf_url=f"/api/v1/referrals/{referral.id}/letter",
            whatsapp_message=result["whatsapp_message"],
        )
    except Exception as e:
        logger.error(f"Referral generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/child/{child_id}", response_model=List[ReferralResponse])
def get_child_referrals(
    child_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all referrals for a child."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    return (
        db.query(Referral)
        .filter(Referral.child_id == child_id)
        .order_by(Referral.created_at.desc())
        .all()
    )


@router.put("/{referral_id}/status", response_model=ReferralResponse)
def update_referral_status(
    referral_id: UUID,
    data: ReferralStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update referral status (e.g., APPOINTMENT_SCHEDULED → ASSESSED)."""
    referral = db.query(Referral).filter(Referral.id == referral_id).first()
    if not referral:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referral not found")

    referral.status = data.status
    if data.specialist_notes:
        referral.specialist_notes = data.specialist_notes
    if data.appointment_date:
        referral.appointment_date = data.appointment_date

    db.commit()
    db.refresh(referral)
    return referral


@router.get("/{referral_id}/letter")
def get_referral_letter(
    referral_id: UUID,
    format: str = Query("text", description="Response format: 'text' or 'pdf'"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the referral letter text or PDF."""
    referral = db.query(Referral).filter(Referral.id == referral_id).first()
    if not referral:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referral not found")

    if format == "pdf":
        from fastapi.responses import Response
        from ..utils.pdf_generator import generate_referral_pdf
        child = get_child(referral.child_id, db)
        pdf_bytes = generate_referral_pdf(str(referral_id), child.full_name if child else "Child", referral.letter_text)
        return Response(content=pdf_bytes, media_type="application/pdf",
                       headers={"Content-Disposition": f'attachment; filename="referral_{referral_id}.pdf"'})

    return {"letter_text": referral.letter_text, "letter_text_hi": referral.letter_text_hi}


@router.post("/{referral_id}/notify-parent")
def notify_parent(
    referral_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark referral as sent to parent (mock WhatsApp notification)."""
    referral = db.query(Referral).filter(Referral.id == referral_id).first()
    if not referral:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Referral not found")

    referral.parent_notified_at = datetime.now(timezone.utc)
    referral.status = "SENT_TO_PARENT"
    db.commit()

    child = get_child(referral.child_id, db)
    whatsapp_msg = (
        f"Dear Parent/Guardian, {child.full_name if child else 'your child'} has been referred for "
        f"a developmental assessment. Please visit your Anganwadi Worker for details and the referral letter."
    )

    return {
        "message": "Parent notification sent successfully",
        "whatsapp_message": whatsapp_msg,
        "notified_at": referral.parent_notified_at,
        "note": "In production, this would send via WhatsApp Business API",
    }


@router.get("/schemes/{child_id}", response_model=List[GovernmentSchemeResponse])
def get_schemes_for_child(
    child_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all active government schemes applicable to Anganwadi children."""
    return db.query(GovernmentScheme).all()


@router.get("/schemes", response_model=List[GovernmentSchemeResponse])
def get_all_schemes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all active government schemes."""
    return db.query(GovernmentScheme).all()


@router.get("/facilities", response_model=List[ReferralFacilityResponse])
def get_referral_facilities(
    district_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get available referral facilities."""
    query = db.query(ReferralFacility).filter(ReferralFacility.is_active == True)
    if district_id:
        query = query.filter(ReferralFacility.district_id == district_id)
    return query.all()
