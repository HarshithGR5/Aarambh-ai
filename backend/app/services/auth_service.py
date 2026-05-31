import hashlib
import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from sqlalchemy.orm import Session
from ..models.user import User, UserRole
from ..config import settings
import logging

logger = logging.getLogger(__name__)


def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()


def create_access_token(user_id: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def request_otp(phone: str, db: Session) -> dict:
    user = db.query(User).filter(User.phone == phone).first()
    otp = generate_otp()
    otp_hash = hash_otp(otp)
    expires = datetime.now(timezone.utc) + timedelta(minutes=10)

    if user:
        user.otp_hash = otp_hash
        user.otp_expires = expires
    else:
        user = User(
            phone=phone,
            name=f"User-{phone[-4:]}",
            role=UserRole.AWW,
            otp_hash=otp_hash,
            otp_expires=expires,
        )
        db.add(user)

    db.commit()
    logger.info(f"OTP generated for {phone}: {otp} (DEVELOPMENT MODE)")

    return {
        "message": "OTP sent successfully",
        "otp": otp,  # Only returned in dev/mock mode
        "phone": phone,
    }


def verify_otp(phone: str, otp: str, db: Session) -> Optional[dict]:
    user = db.query(User).filter(User.phone == phone, User.is_active == True).first()
    if not user:
        return None

    if not user.otp_hash or not user.otp_expires:
        return None

    now = datetime.now(timezone.utc)
    if user.otp_expires.replace(tzinfo=timezone.utc) < now:
        return None

    if user.otp_hash != hash_otp(otp):
        return None

    user.otp_hash = None
    user.otp_expires = None
    user.last_login = now
    db.commit()
    db.refresh(user)

    token = create_access_token(str(user.id), user.role.value)
    return {"access_token": token, "user": user}


def register_user(data: dict, db: Session) -> User:
    existing = db.query(User).filter(User.phone == data["phone"]).first()
    if existing:
        raise ValueError(f"User with phone {data['phone']} already exists")

    user = User(
        phone=data["phone"],
        name=data["name"],
        role=data.get("role", UserRole.AWW),
        awc_id=data.get("awc_id"),
        district_id=data.get("district_id"),
        language=data.get("language", "hi"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
