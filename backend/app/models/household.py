"""
GHARMIND AI — Household & FamilyMember Models
Core household entity and family member definitions.
"""
import uuid
from datetime import datetime, time
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    Text,
    Time,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Household(Base, TimestampMixin):
    """
    Root entity. One row per registered home.
    Every other table cascades from household_id.
    """

    __tablename__ = "households"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    owner_user_id: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    pincode: Mapped[str | None] = mapped_column(String(10))
    timezone: Mapped[str] = mapped_column(String(50), server_default="'Asia/Kolkata'")
    language_preference: Mapped[str] = mapped_column(String(20), server_default="'hinglish'")
    home_type: Mapped[str | None] = mapped_column(String(50))
    floors: Mapped[int] = mapped_column(SmallInteger, server_default="1")
    total_rooms: Mapped[int] = mapped_column(SmallInteger, server_default="4")

    # Contextual tags: ['joint_family', 'has_students', 'working_couple']
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String))

    # Onboarding state
    onboarding_complete: Mapped[bool] = mapped_column(Boolean, server_default="false")
    twin_initialized: Mapped[bool] = mapped_column(Boolean, server_default="false")
    ai_persona_name: Mapped[str] = mapped_column(String(100), server_default="'Gharji'")
    subscription_tier: Mapped[str] = mapped_column(String(50), server_default="'free'")

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # ── Relationships ───────────────────────────────────────────────
    members: Mapped[list["FamilyMember"]] = relationship(
        "FamilyMember", back_populates="household", cascade="all, delete-orphan"
    )
    rooms: Mapped[list["Room"]] = relationship(  # type: ignore[name-defined]
        "Room", back_populates="household", cascade="all, delete-orphan"
    )
    appliances: Mapped[list["Appliance"]] = relationship(  # type: ignore[name-defined]
        "Appliance", back_populates="household", cascade="all, delete-orphan"
    )
    routines: Mapped[list["Routine"]] = relationship(  # type: ignore[name-defined]
        "Routine", back_populates="household", cascade="all, delete-orphan"
    )
    predictions: Mapped[list["Prediction"]] = relationship(  # type: ignore[name-defined]
        "Prediction", back_populates="household", cascade="all, delete-orphan"
    )
    memories: Mapped[list["HouseholdMemory"]] = relationship(  # type: ignore[name-defined]
        "HouseholdMemory", back_populates="household", cascade="all, delete-orphan"
    )
    calendar_events: Mapped[list["HouseholdCalendarEvent"]] = relationship(  # type: ignore[name-defined]
        "HouseholdCalendarEvent", back_populates="household", cascade="all, delete-orphan"
    )
    simulation_runs: Mapped[list["SimulationRun"]] = relationship(  # type: ignore[name-defined]
        "SimulationRun", back_populates="household", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Household {self.name!r} ({self.city})>"


class FamilyMember(Base, TimestampMixin):
    """
    A person who lives in or is associated with the household.
    Each member has their own schedule, preferences, and simulated location.
    """

    __tablename__ = "family_members"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    household_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("households.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(50))
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    # roles: parent, child, grandparent, help, tenant

    age: Mapped[int | None] = mapped_column(SmallInteger)
    gender: Mapped[str | None] = mapped_column(String(20))

    # Schedules stored as JSONB for flexibility
    work_schedule: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    # {"type": "hybrid", "days": ["mon","tue","wed","thu","fri"], "wfh_days": ["mon","tue","wed","thu"]}
    school_schedule: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    # {"school_name": "...", "bus_time": "07:15", "return_time": "14:30"}

    typical_wake_time: Mapped[time | None] = mapped_column(Time)
    typical_sleep_time: Mapped[time | None] = mapped_column(Time)

    # Contact & alerts
    is_primary_contact: Mapped[bool] = mapped_column(Boolean, server_default="false")
    receives_alerts: Mapped[bool] = mapped_column(Boolean, server_default="true")
    phone_number: Mapped[str | None] = mapped_column(String(20))

    # Preferences JSON: {"chai_time": "16:30", "quiet_hours": ["22:00","05:30"], "language": "hinglish"}
    preferences: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    # Simulated state (updated by Digital Twin engine)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    simulated_location: Mapped[str | None] = mapped_column(String(50))

    # ── Relationships ───────────────────────────────────────────────
    household: Mapped["Household"] = relationship("Household", back_populates="members")

    def __repr__(self) -> str:
        return f"<FamilyMember {self.name!r} ({self.role})>"
