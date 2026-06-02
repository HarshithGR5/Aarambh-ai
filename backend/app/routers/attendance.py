from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date
from pydantic import BaseModel
from ..database import get_db
from ..models.attendance import Attendance
from ..middleware.auth_middleware import get_current_user
from ..models.user import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class AttendanceEntry(BaseModel):
    child_id: UUID
    present: bool


class BatchAttendanceRequest(BaseModel):
    date: date
    entries: List[AttendanceEntry]


class BulkAttendanceEntry(BaseModel):
    child_id: UUID
    present: bool
    date: Optional[date] = None


class BulkAttendanceRequest(BaseModel):
    entries: List[BulkAttendanceEntry]


class AttendanceResponse(BaseModel):
    id: int
    child_id: UUID
    date: date
    present: bool
    marked_by: UUID

    class Config:
        from_attributes = True


@router.get("/today", response_model=List[AttendanceResponse])
def get_today_attendance(
    awc_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get attendance records for today filtered by AWC."""
    from ..models.child import Child
    today = date.today()
    query = (
        db.query(Attendance)
        .join(Child, Attendance.child_id == Child.id)
        .filter(Attendance.date == today)
    )
    effective_awc = awc_id or current_user.awc_id
    if effective_awc:
        query = query.filter(Child.awc_id == effective_awc)
    return query.all()


@router.post("/bulk", response_model=dict)
def mark_attendance_bulk(
    data: BulkAttendanceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark attendance for multiple children. date defaults to today if not provided."""
    today = date.today()
    saved = 0
    for entry in data.entries:
        att_date = entry.date or today
        existing = db.query(Attendance).filter(
            Attendance.child_id == entry.child_id,
            Attendance.date == att_date,
        ).first()
        if existing:
            existing.present = entry.present
            existing.marked_by = current_user.id
        else:
            record = Attendance(
                child_id=entry.child_id,
                date=att_date,
                present=entry.present,
                marked_by=current_user.id,
            )
            db.add(record)
        saved += 1
    db.commit()
    return {"message": f"Attendance saved for {saved} children on {today}", "count": saved}


@router.post("/batch", response_model=dict)
def mark_attendance_batch(
    data: BatchAttendanceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mark attendance for multiple children at once."""
    saved = 0
    for entry in data.entries:
        existing = db.query(Attendance).filter(
            Attendance.child_id == entry.child_id,
            Attendance.date == data.date,
        ).first()
        if existing:
            existing.present = entry.present
            existing.marked_by = current_user.id
        else:
            record = Attendance(
                child_id=entry.child_id,
                date=data.date,
                present=entry.present,
                marked_by=current_user.id,
            )
            db.add(record)
        saved += 1

    db.commit()
    return {"message": f"Attendance saved for {saved} children on {data.date}", "count": saved}


@router.get("/child/{child_id}", response_model=List[AttendanceResponse])
def get_child_attendance(
    child_id: UUID,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get attendance history for a child."""
    query = db.query(Attendance).filter(Attendance.child_id == child_id)
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    return query.order_by(Attendance.date.desc()).limit(90).all()


@router.get("/date/{attendance_date}", response_model=List[AttendanceResponse])
def get_attendance_by_date(
    attendance_date: date,
    awc_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all attendance records for a given date."""
    from ..models.child import Child
    query = (
        db.query(Attendance)
        .join(Child, Attendance.child_id == Child.id)
        .filter(Attendance.date == attendance_date)
    )
    if awc_id:
        query = query.filter(Child.awc_id == awc_id)
    elif current_user.awc_id:
        query = query.filter(Child.awc_id == current_user.awc_id)
    return query.all()
