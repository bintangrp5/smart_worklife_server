"""
Health models — BMI Profile, Hydration Settings, and Hydration Logs.
Supports BMI calculation (WHO standard) and daily hydration tracking.
"""
import uuid
from datetime import datetime, date, time, timezone

from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, DateTime, Date, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class BMIProfile(Base):
    """
    Tabel bmi_profiles — Profil BMI pengguna.
    Relasi 1-to-1 dengan User. Dihitung otomatis dari tinggi & berat badan.

    Rumus BMI: weight_kg / (height_cm / 100)²
    Kategori:
      - Underweight: < 18.5
      - Normal: 18.5 – 24.9
      - Overweight: 25.0 – 29.9
      - Obese: ≥ 30.0
    """
    __tablename__ = "bmi_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        unique=True, nullable=False
    )
    height_cm: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Tinggi badan dalam cm"
    )
    weight_kg: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Berat badan dalam kg"
    )
    bmi_value: Mapped[float | None] = mapped_column(
        Float, comment="Nilai BMI yang dihitung"
    )
    bmi_category: Mapped[str | None] = mapped_column(
        String(20), comment="underweight | normal | overweight | obese"
    )
    calculated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), comment="Waktu perhitungan BMI terakhir"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="bmi_profile")

    def calculate_bmi(self) -> None:
        """Calculate BMI and set category based on WHO standards."""
        if self.height_cm and self.weight_kg and self.height_cm > 0:
            height_m = self.height_cm / 100
            self.bmi_value = round(self.weight_kg / (height_m ** 2), 1)

            if self.bmi_value < 18.5:
                self.bmi_category = "underweight"
            elif self.bmi_value < 25.0:
                self.bmi_category = "normal"
            elif self.bmi_value < 30.0:
                self.bmi_category = "overweight"
            else:
                self.bmi_category = "obese"

            self.calculated_at = datetime.now(timezone.utc)

    def __repr__(self) -> str:
        return f"<BMIProfile(bmi={self.bmi_value}, category='{self.bmi_category}')>"


class HydrationSetting(Base):
    """
    Tabel hydration_settings — Pengaturan hidrasi per user.
    Relasi 1-to-1 dengan User.
    Target harian dihitung: weight_kg × 30 ml.
    """
    __tablename__ = "hydration_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        unique=True, nullable=False
    )
    daily_target_ml: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Target air harian dalam ml (BB × 30)"
    )
    reminder_interval_minutes: Mapped[int] = mapped_column(
        Integer, default=60, comment="Interval pengingat dalam menit"
    )
    reminder_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    reminder_start_time: Mapped[time] = mapped_column(
        Time, default=time(8, 0), comment="Jam mulai pengingat"
    )
    reminder_end_time: Mapped[time] = mapped_column(
        Time, default=time(20, 0), comment="Jam akhir pengingat"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="hydration_setting")

    def __repr__(self) -> str:
        return f"<HydrationSetting(target={self.daily_target_ml}ml, interval={self.reminder_interval_minutes}min)>"


class HydrationLog(Base):
    """
    Tabel hydration_logs — Log setiap kali user minum air.
    Digunakan untuk tracking progress terhadap target harian.
    """
    __tablename__ = "hydration_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    amount_ml: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Jumlah air dalam ml"
    )
    log_date: Mapped[date] = mapped_column(
        Date, nullable=False, default=lambda: datetime.now(timezone.utc).date(),
        comment="Tanggal log untuk query harian"
    )
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="hydration_logs")

    def __repr__(self) -> str:
        return f"<HydrationLog(amount={self.amount_ml}ml, date={self.log_date})>"
