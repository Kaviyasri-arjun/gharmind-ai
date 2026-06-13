"""
GHARMIND AI — Digital Twin Models
Room, Appliance, and TwinStateSnapshot ORM models.
"""
import uuid
from datetime import datetime, time
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
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


class Room(Base, TimestampMixin):
    """
    A physical space in the household.
    Position (x,y) is used for floor plan visualization (0-100 grid).
    State fields are updated every minute by the Twin Engine.
    """

    __tablename__ = "rooms"

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
    room_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # types: bedroom, kitchen, bathroom, pooja_room, study, living_room, balcony, garage

    floor: Mapped[int] = mapped_column(SmallInteger, server_default="0")
    area_sqft: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))

    # Floor plan grid position (0-100)
    position_x: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    position_y: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))

    # ── Simulated state (updated by Twin Engine every tick) ─────────
    is_occupied: Mapped[bool] = mapped_column(Boolean, server_default="false")
    occupants: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    # occupants stores member UUIDs as strings

    lighting_state: Mapped[str] = mapped_column(String(20), server_default="'off'")
    # states: off, dim, on, auto

    temperature_c: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    air_quality: Mapped[str | None] = mapped_column(String(20))
    noise_level: Mapped[str | None] = mapped_column(String(20))

    last_state_change: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ── Relationships ───────────────────────────────────────────────
    household: Mapped["Household"] = relationship("Household", back_populates="rooms")  # type: ignore[name-defined]
    appliances: Mapped[list["Appliance"]] = relationship(
        "Appliance", back_populates="room"
    )

    def __repr__(self) -> str:
        return f"<Room {self.name!r} ({self.room_type})>"


class Appliance(Base, TimestampMixin):
    """
    A simulated household appliance.
    State is managed by the Digital Twin engine.
    auto_schedule drives scheduled on/off behavior.
    """

    __tablename__ = "appliances"

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
    room_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rooms.id", ondelete="SET NULL"),
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    appliance_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # types: motor, geyser, fan, ac, tv, fridge, washing_machine, wifi, gas_stove, chimney

    brand: Mapped[str | None] = mapped_column(String(100))

    # ── Simulated state ─────────────────────────────────────────────
    power_state: Mapped[str] = mapped_column(String(20), server_default="'off'")
    # states: off, on, standby, error

    power_watts: Mapped[int | None] = mapped_column(SmallInteger)
    is_critical: Mapped[bool] = mapped_column(Boolean, server_default="false")

    # auto_schedule: {"on": "06:10", "off": null, "days": ["*"], "auto_off_after_mins": 30}
    auto_schedule: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    health_score: Mapped[int] = mapped_column(SmallInteger, server_default="100")
    # 0-100 simulated appliance health

    avg_daily_runtime_mins: Mapped[int | None] = mapped_column(SmallInteger)
    last_on_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_off_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # ── Relationships ───────────────────────────────────────────────
    household: Mapped["Household"] = relationship("Household", back_populates="appliances")  # type: ignore[name-defined]
    room: Mapped["Room | None"] = relationship("Room", back_populates="appliances")

    def __repr__(self) -> str:
        return f"<Appliance {self.name!r} ({self.appliance_type}) state={self.power_state}>"


class TwinStateSnapshot(Base):
    """
    Point-in-time snapshot of the entire household state.
    Generated every minute by the Twin Engine.
    context_embedding (pgvector) enables semantic similarity search.
    """

    __tablename__ = "twin_state_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    household_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("households.id", ondelete="CASCADE"),
        nullable=False,
    )
    snapshot_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Temporal context at snapshot time ───────────────────────────
    ist_time: Mapped[time] = mapped_column(Time, nullable=False)
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    # 0=Monday, 6=Sunday
    week_number: Mapped[int | None] = mapped_column(SmallInteger)
    month: Mapped[int | None] = mapped_column(SmallInteger)
    season: Mapped[str | None] = mapped_column(String(20))
    festival_context: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    is_holiday: Mapped[bool] = mapped_column(Boolean, server_default="false")
    is_exam_period: Mapped[bool] = mapped_column(Boolean, server_default="false")

    # ── Compressed household state (JSONB) ──────────────────────────
    rooms_state: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    appliances_state: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    members_state: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    power_available: Mapped[bool] = mapped_column(Boolean, server_default="true")
    water_available: Mapped[bool] = mapped_column(Boolean, server_default="true")
    internet_available: Mapped[bool] = mapped_column(Boolean, server_default="true")

    # ── AI context summary ──────────────────────────────────────────
    context_summary: Mapped[str | None] = mapped_column(Text)

    # pgvector embedding — stored as Text (cast to vector in queries)
    # Using Text here because SQLAlchemy doesn't natively support pgvector type
    # The actual column is vector(1536) — managed via raw SQL migration
    context_embedding_text: Mapped[str | None] = mapped_column(
        "context_embedding",
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # ── Relationships ───────────────────────────────────────────────
    household: Mapped["Household"] = relationship("Household")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return f"<TwinStateSnapshot {self.snapshot_at} urgency={self.context_summary}>"
