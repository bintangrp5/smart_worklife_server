import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str] = None
    is_verified: bool
    # Onboarding fields
    gender: Optional[str] = None
    age: Optional[int] = None
    industry: Optional[str] = None
    work_start_time: Optional[str] = None
    work_end_time: Optional[str] = None
    # BMI fields (optional to include here)
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    gender: Optional[str] = None
    age: Optional[int] = None
    industry: Optional[str] = None
    work_start_time: Optional[str] = None
    work_end_time: Optional[str] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[UserOut] = None


class TokenPayload(BaseModel):
    sub: Optional[str] = None


class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class OTPVerify(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=4, max_length=4)


class OTPResend(BaseModel):
    email: EmailStr


class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=4, max_length=4)
    new_password: str = Field(..., min_length=8)


class GoogleAuth(BaseModel):
    id_token: str
