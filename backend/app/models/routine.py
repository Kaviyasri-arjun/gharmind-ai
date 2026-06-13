"""
GHARMIND AI — Routine & RoutineExecution Models
Defines household routines and their execution history.
"""
import uuid
from datetime import datetime, time
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    Time,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Routine(Base, TimestampMixin):
    """
    A named, recurring household activity.
    Can be user-defined or AI-detected from pattern analysis.
    pattern_embedding (pgvector) enables semantic routine similarity matching.
    """

    __tablename__ = "routines"

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

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    routine_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # types: pooja, motor, tuition, meal, study, chai, cleaning, exercise, commute, festival

    # ── Scheduling ──────────────────────────────────────────────────
    recurrence: Mapped[str] = mapped_column(String(50), nullable=False)
    # values: daily, weekly, monthly, annual, conditional

    # schedule_expression: {"days": ["mon","wed","fri"], "time": "17:00", "duration_mins": 90}
    schedule_expression: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    conditional_trigger: Mapped[str | None] = mapped_column(Text)
    # e.g., "when season=monsoon AND time=05:30"

    # ── Participants ────────────────────────────────────────────────
    primary_member_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("family_members.id", ondelete="SET NULL"),
    )
    participant_ids: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    appliance_ids: Mapped[list[str] | None] = mapped_column(ARRAY(String))

    # ── AI learning metadata ────────────────────────────────────────
    is_ai_detected: Mapped[bool] = mapped_column(Boolean, server_default="false")
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))
    detection_method: Mapped[str | None] = mapped_column(String(50))
    # values: pattern_match, explicit, inferred

    # ── State ───────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    last_executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_expected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    execution_count: Mapped[int] = mapped_column(Integer, server_default="0")

    # pgvector pattern embedding — stored as Text, cast to vector in SQL queries
    pattern_embedding_text: Mapped[str | None] = mapped_column(
        "pattern_embedding", Text, nullable=True
    )

    # ── Relationships ───────────────────────────────────────────────
    household: Mapped["Household"] = relationship("Household", back_populates="routines")  # type: ignore[name-defined]
    executions: Mapped[list["RoutineExecution"]] = relationship(
        "RoutineExecution", back_populates="routine", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Routine {self.name!r} ({self.routine_type}) recurrence={self.recurrence}>"


class RoutineExecution(Base):
    """
    Log of every time a routine runs (real or simulated).
    Used for pattern learning and prediction accuracy measurement.
    """

    __tablename__ = "routine_executions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    routine_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("routines.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    household_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_mins: Mapped[int | None] = mapped_column(SmallInteger)

    # ── Context at execution time ───────────────────────────────────
    ist_time: Mapped[time] = mapped_column(Time, nullable=False)
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    season: Mapped[str | None] = mapped_column(String(20))
    festival_context: Mapped[list[str] | None] = mapped_column(ARRAY(String))

    was_predicted: Mapped[bool] = mapped_column(Boolean, server_default="false")
    prediction_accuracy: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))

    # ── Deviation tracking ──────────────────────────────────────────
    was_on_schedule: Mapped[bool] = mapped_column(Boolean, server_default="true")
    deviation_mins: Mapped[int] = mapped_column(SmallInteger, server_default="0")
    deviation_reason: Mapped[str | None] = mapped_column(Text)

    # execution_type: real (user confirmed) | simulated (twin-generated)
    execution_type: Mapped[str] = mapped_column(String(20), server_default="'real'")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ── Relationships ───────────────────────────────────────────────
    routine: Mapped["Routine"] = relationship("Routine", back_populates="executions")

    def __repr__(self) -> str:
        return f"<RoutineExecution routine={self.routine_id} at={self.executed_at}>"
