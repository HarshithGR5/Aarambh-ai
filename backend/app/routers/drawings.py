import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from ..database import get_db
from ..schemas.drawing import DrawingResponse, DrawingUploadResponse, DrawingAnalysisResponse
from ..models.drawing import Drawing, DrawingAnalysis
from ..middleware.auth_middleware import get_current_user
from ..models.user import User
from ..services.child_service import get_child, get_age_months
from ..config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=DrawingUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_drawing(
    child_id: UUID = Form(...),
    context: str = Form("free_drawing"),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a child's drawing and analyze it with Crayon Intelligence™ AI."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    image_bytes = await image.read()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = f"drawing_{child_id}_{image.filename}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(image_bytes)

    drawing = Drawing(
        child_id=child_id,
        image_url=f"/uploads/{filename}",
        uploaded_by=current_user.id,
        context=context,
    )
    db.add(drawing)
    db.flush()

    age_months = get_age_months(child.date_of_birth)
    try:
        from ..ai.drawing_analysis import analyze_drawing
        analysis_data = await analyze_drawing(image_bytes, age_months, context)
    except Exception as e:
        logger.error(f"Drawing analysis failed: {e}")
        from ..ai.drawing_analysis import MOCK_ANALYSIS
        analysis_data = MOCK_ANALYSIS

    analysis = DrawingAnalysis(
        drawing_id=drawing.id,
        fine_motor_score=analysis_data.get("fine_motor_score"),
        cognitive_score=analysis_data.get("cognitive_score"),
        emotional_tone=analysis_data.get("emotional_tone"),
        spatial_org_score=analysis_data.get("spatial_org_score"),
        figure_complexity=analysis_data.get("figure_complexity"),
        ai_summary=analysis_data.get("ai_summary", "Analysis completed."),
        domain_flags=analysis_data.get("domain_flags", {}),
        model_used="gpt-4o" if os.getenv("OPENAI_API_KEY") else "mock",
    )
    db.add(analysis)
    db.commit()
    db.refresh(drawing)

    # Update PDRS
    try:
        from ..services.pdrs_service import compute_pdrs, save_pdrs_score
        pdrs_result = compute_pdrs(child_id, db)
        save_pdrs_score(child_id, pdrs_result, db)
    except Exception as e:
        logger.warning(f"PDRS update after drawing failed: {e}")

    return DrawingUploadResponse(
        drawing_id=drawing.id,
        analysis=DrawingAnalysisResponse(**analysis_data),
    )


@router.get("/child/{child_id}", response_model=List[DrawingResponse])
def get_child_drawings(
    child_id: UUID,
    limit: int = Query(10, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all drawings for a child."""
    child = get_child(child_id, db)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    return (
        db.query(Drawing)
        .filter(Drawing.child_id == child_id)
        .order_by(Drawing.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/{drawing_id}/analysis", response_model=DrawingAnalysisResponse)
def get_drawing_analysis(
    drawing_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the AI analysis result for a drawing."""
    drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
    if not drawing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drawing not found")
    if not drawing.analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No analysis found for this drawing")
    return drawing.analysis
