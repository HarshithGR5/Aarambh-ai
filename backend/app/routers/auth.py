from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.auth import OTPRequest, OTPVerify, UserRegister, TokenResponse, OTPRequestResponse, UserResponse
from ..services.auth_service import request_otp, verify_otp, register_user
from ..middleware.auth_middleware import get_current_user, require_admin
from ..models.user import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/request-otp", response_model=OTPRequestResponse)
def request_otp_endpoint(data: OTPRequest, db: Session = Depends(get_db)):
    """Request OTP for phone-based login. Returns mock OTP in development mode."""
    result = request_otp(data.phone, db)
    return result


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp_endpoint(data: OTPVerify, db: Session = Depends(get_db)):
    """Verify OTP and return JWT access token."""
    result = verify_otp(data.phone, data.otp, db)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP or OTP has expired. Please request a new one.",
        )
    return TokenResponse(access_token=result["access_token"], user=result["user"])


@router.post("/register", response_model=UserResponse)
def register_user_endpoint(
    data: UserRegister,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Register a new user (admin only)."""
    try:
        user = register_user(data.model_dump(), db)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return current_user


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh JWT token."""
    from ..services.auth_service import create_access_token
    new_token = create_access_token(str(current_user.id), current_user.role.value)
    return TokenResponse(access_token=new_token, user=current_user)
