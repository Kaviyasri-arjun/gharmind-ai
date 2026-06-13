"""
GHARMIND AI — Calendar Models
FestivalCalendar (global reference) and HouseholdCalendarEvent (per-household).
"""
import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class FestivalCalendar(Base):
    """
    Global Indian festival calendar with household behavior impact models.
    Pre-populated at deployment — not household-specific.
    """

    __tablename__ = "festival_calendar"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    festival_name: Mapped[str] = mapped_column(String(200), nullable=False)

    # local_names: {"hi": "दीपावली", "mr": "दिवाळी", "en": "Diwali"}
    local_names: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    festival_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # types: hindu, muslim, christian, sikh, national, regional

    region: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    # values: all_india, maharashtra, goa, karnataka, etc.

    # ── Date information ────────────────────────────────────────────
    gregorian_date: Mapped[date | None] = mapped_column(Date, index=True)
    lunar_month: Mapped[str | None] = mapped_column(String(30))
    lunar_tithi: Mapped[str | None] = mapped_column(String(50))
    calculation_rule: Mapped[str | None] = mapped_column(Text)

    # ── Household behavior impact model ────────────────────────────
    # household_impact: {
    #   "preparation_days": 5,
    #   "water_usage_multiplier": 1.4,
    #   "power_usage_multiplier": 1.6,
    #   "sleep_shift_hours": -1.5,
    #   "typical_routines": ["extended_pooja", "deep_cleaning"],
    #   "guest_probability": 0.85
    # }
    household_impact: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    prep_days_before: Mapped[int] = mapped_column(SmallInteger, server_default="1")
    celebration_days: Mapped[int] = mapped_column(SmallInteger, server_default="1")
    recovery_days: Mapped[int] = mapped_column(SmallInteger, server_default="0")

    is_public_holiday: Mapped[bool] = mapped_column(Boolean, server_default="false")
    is_school_holiday: Mapped[bool] = mapped_column(Boolean, server_default="false")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<FestivalCalendar {self.festival_name!r} type={self.festival_type}>"


class HouseholdCalendarEvent(Base, TimestampMixin):
    """
    A household-specific custom calendar event.
    Examples: exams, tuition schedules, guest visits, travel.
    impact_tags guide AI prediction adjustments.
    """

    __tablename__ = "household_calendar_events"

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
    member_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("family_members.id", ondelete="SET NULL"),
    )

    event_name: Mapped[str] = mapped_column(String(200), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # types: exam, tuition, guest, travel, medical, birthday, other

    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    is_recurring: Mapped[bool] = mapped_column(Boolean, server_default="false")
    # recurrence_rule: {"frequency": "weekly", "day": "tuesday"}
    recurrence_rule: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    # impact_tags guide AI: ['quiet_hours', 'no_interruptions', 'extra_water', 'early_wake']
    impact_tags: Mapped[list[str] | None] = mapped_column(ARRAY(String))

    description: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    # ── Relationships ───────────────────────────────────────────────
    household: Mapped["Household"] = relationship("Household", back_populates="calendar_events")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return f"<HouseholdCalendarEvent {self.event_name!r} type={self.event_type}>"
