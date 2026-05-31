from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from ..models.user import UserRole


class OTPRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15, description="Phone number")


class OTPVerify(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    otp: str = Field(..., min_length=4, max_length=6)


class UserRegister(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    name: str = Field(..., min_length=2, max_length=200)
    role: UserRole = UserRole.AWW
    awc_id: Optional[int] = None
    district_id: Optional[int] = None
    language: str = "hi"


class UserResponse(BaseModel):
    id: UUID
    phone: str
    name: str
    role: UserRole
    awc_id: Optional[int] = None
    district_id: Optional[int] = None
    language: str
    is_active: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class OTPRequestResponse(BaseModel):
    message: str
    otp: Optional[str] = None  # Only in dev/mock mode
    phone: str
