"""
Auth Router — thin layer: validasi input, delegasi ke AuthService, return response.
Logic bisnis TIDAK ada di sini — semua ada di app.services.auth_service.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import (
    UserRegister, UserLogin, Token, OTPVerify,
    ForgotPassword, ResetPassword, GoogleAuth, UserOut, OTPResend, UserProfileUpdate
)
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user_id
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    return await AuthService.register_user(db, data)


@router.post("/verify-otp")
async def verify_otp(data: OTPVerify, db: AsyncSession = Depends(get_db)):
    return await AuthService.verify_otp(db, data)


@router.post("/resend-otp")
async def resend_otp(data: OTPResend, db: AsyncSession = Depends(get_db)):
    return await AuthService.resend_otp(db, data)


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await AuthService.login_user(db, data)


@router.post("/forgot-password")
async def forgot_password(data: ForgotPassword, db: AsyncSession = Depends(get_db)):
    return await AuthService.forgot_password(db, data)


@router.post("/reset-password")
async def reset_password(data: ResetPassword, db: AsyncSession = Depends(get_db)):
    return await AuthService.reset_password(db, data)


@router.put("/profile", response_model=UserOut)
async def update_profile(
    data: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: uuid.UUID = Depends(get_current_user_id)
):
    return await AuthService.update_user_profile(db, current_user_id, data)


@router.post("/google", response_model=Token)
async def google_auth(data: GoogleAuth, db: AsyncSession = Depends(get_db)):
    """
    Endpoint untuk login/register via Google.
    Aplikasi mobile akan mengirimkan id_token dari Google.
    NOTE: Implementasi verifikasi google-auth library menyusul.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google Auth verification logic needs to be implemented with google-auth library.",
    )
