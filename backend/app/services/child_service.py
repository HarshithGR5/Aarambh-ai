from datetime import date
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from ..models.child import Child
from ..models.pdrs import PDRSScore
from ..utils.qr_generator import generate_child_qr
import logging

logger = logging.getLogger(__name__)


def get_age_months(dob: date) -> int:
    today = date.today()
    months = (today.year - dob.year) * 12 + (today.month - dob.month)
    if today.day < dob.day:
        months -= 1
    return max(0, months)


def create_child(data: dict, registered_by_id: UUID, db: Session) -> Child:
    child = Child(**data, registered_by=registered_by_id)
    db.add(child)
    db.flush()  # get the ID

    qr_code = generate_child_qr(str(child.id))
    child.qr_code = qr_code
    db.commit()
    db.refresh(child)
    return child


def get_child(child_id: UUID, db: Session) -> Optional[Child]:
    return db.query(Child).filter(Child.id == child_id, Child.is_active == True).first()


def get_children_by_awc(awc_id: int, db: Session) -> List[Child]:
    return db.query(Child).filter(Child.awc_id == awc_id, Child.is_active == True).order_by(Child.full_name).all()


def get_all_children(db: Session, awc_id: Optional[int] = None, limit: int = 100, offset: int = 0) -> List[Child]:
    query = db.query(Child).filter(Child.is_active == True)
    if awc_id:
        query = query.filter(Child.awc_id == awc_id)
    return query.order_by(Child.full_name).offset(offset).limit(limit).all()


def update_child(child_id: UUID, data: dict, db: Session) -> Optional[Child]:
    child = get_child(child_id, db)
    if not child:
        return None
    for key, value in data.items():
        if value is not None and hasattr(child, key):
            setattr(child, key, value)
    db.commit()
    db.refresh(child)
    return child


def enrich_child_with_age(child: Child) -> dict:
    age_months = get_age_months(child.date_of_birth)
    child_dict = {
        "id": child.id,
        "full_name": child.full_name,
        "date_of_birth": child.date_of_birth,
        "gender": child.gender,
        "awc_id": child.awc_id,
        "parent_name": child.parent_name,
        "parent_phone": child.parent_phone,
        "parent_language": child.parent_language,
        "registration_date": child.registration_date,
        "photo_url": child.photo_url,
        "qr_code": child.qr_code,
        "is_active": child.is_active,
        "notes": child.notes,
        "created_at": child.created_at,
        "age_months": age_months,
        "age_years": age_months // 12,
        "age_months_remainder": age_months % 12,
        "latest_pdrs_score": None,
        "latest_risk_level": None,
    }
    return child_dict
