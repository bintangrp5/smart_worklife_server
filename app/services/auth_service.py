"""
AuthService — business logic layer untuk autentikasi.
Router hanya meneruskan request; semua logic ada di sini.
"""
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import auth as crud_auth
from app.core.security import verify_password, create_access_token, get_password_hash
from app.schemas.auth import (
    UserRegister, UserLogin, Token, OTPVerify,
    ForgotPassword, ResetPassword, OTPResend, UserOut, UserProfileUpdate
)


class AuthService:

    @staticmethod
    async def register_user(db: AsyncSession, data: UserRegister) -> UserOut:
        existing = await crud_auth.get_user_by_email(db, data.email)
        
        if existing:
            # Jika user sudah ada DAN sudah diverifikasi, baru lempar error
            if existing.is_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email sudah terdaftar.",
                )
            
            # Jika user sudah ada tapi BELUM diverifikasi, anggap sebagai pendaftaran ulang
            # Update password (mungkin user ganti password saat coba daftar lagi)
            existing.hashed_password = get_password_hash(data.password)
            existing.full_name = data.full_name
            user = existing
        else:
            # Jika benar-benar baru
            if data.password != data.confirm_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password dan konfirmasi password tidak cocok.",
                )
            user = await crud_auth.create_user(
                db, full_name=data.full_name, email=data.email, password=data.password
            )

        otp = await crud_auth.update_user_otp(db, user)

        # Import di sini agar tidak circular import
        from app.services.email_service import send_otp_email
        email_sent = await send_otp_email(user.email, otp)
        if not email_sent:
            # Dev mode: OTP tetap tersimpan di DB walau email gagal.
            # Ambil OTP via: python dev_get_otp.py <email>
            print(f"[DEV WARNING] Email OTP gagal dikirim ke {user.email}. OTP={otp}")

        # Buat UserOut secara manual agar tidak trigger lazy-load relasi bmi_profile
        return UserOut(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_verified=user.is_verified,
            gender=user.gender,
            age=user.age,
            industry=user.industry,
            work_start_time=user.work_start_time,
            work_end_time=user.work_end_time,
            weight_kg=None,
            height_cm=None,
        )

    @staticmethod
    async def login_user(db: AsyncSession, data: UserLogin) -> Token:
        user = await crud_auth.get_user_by_email(db, data.email)
        if not user or not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email atau password salah.",
            )
        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email atau password salah.",
            )
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email belum diverifikasi.",
            )
        access_token = create_access_token(subject=user.id)
        
        # Ambil BMI jika ada (tanpa lazy load)
        from app.models.health import BMIProfile
        bmi_res = await db.execute(select(BMIProfile).where(BMIProfile.user_id == user.id))
        bmi = bmi_res.scalars().first()

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "is_verified": user.is_verified,
                "gender": user.gender,
                "age": user.age,
                "industry": user.industry,
                "work_start_time": user.work_start_time,
                "work_end_time": user.work_end_time,
                "weight_kg": bmi.weight_kg if bmi else None,
                "height_cm": bmi.height_cm if bmi else None,
            }
        }

    @staticmethod
    async def verify_otp(db: AsyncSession, data: OTPVerify) -> dict:
        user = await crud_auth.get_user_by_email(db, data.email)
        if not user:
            raise HTTPException(status_code=404, detail="User tidak ditemukan.")
        if user.otp_code != data.otp_code:
            raise HTTPException(status_code=400, detail="Kode OTP salah.")
        if user.otp_expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Kode OTP sudah kadaluarsa.")

        user.is_verified = True
        user.otp_code = None
        user.otp_expires_at = None
        await db.commit()
        await db.refresh(user)

        from app.core.security import create_access_token
        access_token = create_access_token(subject=user.id)

        # Ambil BMI jika ada
        from app.models.health import BMIProfile
        bmi_res = await db.execute(select(BMIProfile).where(BMIProfile.user_id == user.id))
        bmi = bmi_res.scalars().first()

        return {
            "message": "Email berhasil diverifikasi.",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "is_verified": user.is_verified,
                "gender": user.gender,
                "age": user.age,
                "industry": user.industry,
                "work_start_time": user.work_start_time,
                "work_end_time": user.work_end_time,
                "weight_kg": bmi.weight_kg if bmi else None,
                "height_cm": bmi.height_cm if bmi else None,
            }
        }

    @staticmethod
    async def resend_otp(db: AsyncSession, data: OTPResend) -> dict:
        user = await crud_auth.get_user_by_email(db, data.email)
        if not user:
            raise HTTPException(status_code=404, detail="User tidak ditemukan.")
        otp = await crud_auth.update_user_otp(db, user)

        from app.services.email_service import send_otp_email
        await send_otp_email(user.email, otp)
        return {"message": "OTP baru telah dikirim ke email."}

    @staticmethod
    async def forgot_password(db: AsyncSession, data: ForgotPassword) -> dict:
        user = await crud_auth.get_user_by_email(db, data.email)
        if user:
            otp = await crud_auth.update_user_otp(db, user)
            from app.services.email_service import send_otp_email
            await send_otp_email(user.email, otp)
        # Selalu return success (tidak bocorkan apakah email terdaftar)
        return {"message": "Instruksi reset password telah dikirim ke email jika akun terdaftar."}

    @staticmethod
    async def reset_password(db: AsyncSession, data: ResetPassword) -> dict:
        user = await crud_auth.get_user_by_email(db, data.email)
        if not user:
            raise HTTPException(status_code=404, detail="User tidak ditemukan.")
        if user.otp_code != data.otp_code:
            raise HTTPException(status_code=400, detail="Kode OTP salah.")
        if user.otp_expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Kode OTP sudah kadaluarsa.")

        user.hashed_password = get_password_hash(data.new_password)
        user.otp_code = None
        user.otp_expires_at = None
        await db.commit()
        return {"message": "Password berhasil diperbarui."}

    @staticmethod
    async def update_user_profile(db: AsyncSession, user_id: uuid.UUID, data: UserProfileUpdate) -> UserOut:
        from app.models.user import User
        from app.models.health import BMIProfile
        from sqlalchemy import select

        # 1. Update User core fields
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User tidak ditemukan.")

        if data.gender is not None: user.gender = data.gender
        if data.age is not None: user.age = data.age
        if data.industry is not None: user.industry = data.industry
        if data.work_start_time is not None: user.work_start_time = data.work_start_time
        if data.work_end_time is not None: user.work_end_time = data.work_end_time

        # 2. Update/Create BMI Profile if health data provided
        bmi_result = await db.execute(select(BMIProfile).where(BMIProfile.user_id == user_id))
        bmi = bmi_result.scalars().first()

        if data.weight_kg is not None or data.height_cm is not None:
            if not bmi:
                bmi = BMIProfile(user_id=user_id)
                db.add(bmi)

            if data.weight_kg is not None: bmi.weight_kg = data.weight_kg
            if data.height_cm is not None: bmi.height_cm = data.height_cm

            bmi.calculate_bmi()

        await db.commit()
        await db.refresh(user)

        # Prepare response — query BMI eksplisit, jangan lazy-load via relasi (async incompatible)
        bmi_after = None
        if bmi is not None:
            await db.refresh(bmi)
            bmi_after = bmi

        return UserOut(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_verified=user.is_verified,
            gender=user.gender,
            age=user.age,
            industry=user.industry,
            work_start_time=user.work_start_time,
            work_end_time=user.work_end_time,
            weight_kg=bmi_after.weight_kg if bmi_after else None,
            height_cm=bmi_after.height_cm if bmi_after else None,
        )

