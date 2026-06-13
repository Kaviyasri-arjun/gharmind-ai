"""
GHARMIND AI — Household Service
CRUD operations for households, family members, rooms, and appliances.
Also handles onboarding flow and twin initialization.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.logging_config import get_logger
from app.models.household import FamilyMember, Household
from app.models.twin import Appliance, Room

logger = get_logger(__name__)
IST = ZoneInfo("Asia/Kolkata")


class HouseholdService:
    """Manages household CRUD and onboarding."""

    # ── Household ──────────────────────────────────────────────────────

    async def create_household(
        self,
        db: AsyncSession,
        owner_user_id: str,
        name: str,
        city: str,
        state: str,
        pincode: str | None = None,
        home_type: str | None = None,
        language_preference: str = "hinglish",
        ai_persona_name: str = "Gharji",
        tags: list[str] | None = None,
    ) -> Household:
        """Create a new household."""
        # Check for duplicate
        existing = await db.execute(
            select(Household).where(
                Household.owner_user_id == owner_user_id,
                Household.deleted_at.is_(None),
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError("User already has an active household")

        household = Household(
            owner_user_id=owner_user_id,
            name=name,
            city=city,
            state=state,
            pincode=pincode,
            home_type=home_type,
            language_preference=language_preference,
            ai_persona_name=ai_persona_name,
            tags=tags or [],
        )
        db.add(household)
        await db.flush()
        logger.info("household_created", household_id=str(household.id), name=name)
        return household

    async def get_household(
        self, db: AsyncSession, household_id: str, owner_user_id: str | None = None
    ) -> Household:
        """Get a household by ID, optionally verifying ownership."""
        query = select(Household).where(
            Household.id == UUID(household_id),
            Household.deleted_at.is_(None),
        )
        if owner_user_id:
            query = query.where(Household.owner_user_id == owner_user_id)

        result = await db.execute(query)
        household = result.scalar_one_or_none()
        if not household:
            raise NotFoundError("Household", household_id)
        return household

    async def update_household(
        self,
        db: AsyncSession,
        household_id: str,
        **kwargs: Any,
    ) -> Household:
        """Update household fields."""
        household = await self.get_household(db, household_id)
        for key, value in kwargs.items():
            if value is not None and hasattr(household, key):
                setattr(household, key, value)
        await db.flush()
        return household

    # ── Family Members ─────────────────────────────────────────────────

    async def add_member(
        self,
        db: AsyncSession,
        household_id: str,
        name: str,
        role: str,
        age: int | None = None,
        gender: str | None = None,
        nickname: str | None = None,
        work_schedule: dict[str, Any] | None = None,
        school_schedule: dict[str, Any] | None = None,
        typical_wake_time: Any | None = None,
        typical_sleep_time: Any | None = None,
        is_primary_contact: bool = False,
        phone_number: str | None = None,
        preferences: dict[str, Any] | None = None,
    ) -> FamilyMember:
        """Add a family member to a household."""
        member = FamilyMember(
            household_id=UUID(household_id),
            name=name,
            nickname=nickname,
            role=role,
            age=age,
            gender=gender,
            work_schedule=work_schedule,
            school_schedule=school_schedule,
            typical_wake_time=typical_wake_time,
            typical_sleep_time=typical_sleep_time,
            is_primary_contact=is_primary_contact,
            phone_number=phone_number,
            preferences=preferences,
        )
        db.add(member)
        await db.flush()
        return member

    async def list_members(
        self, db: AsyncSession, household_id: str
    ) -> list[FamilyMember]:
        result = await db.execute(
            select(FamilyMember).where(
                FamilyMember.household_id == UUID(household_id)
            )
        )
        return list(result.scalars().all())

    # ── Rooms ──────────────────────────────────────────────────────────

    async def add_room(
        self,
        db: AsyncSession,
        household_id: str,
        name: str,
        room_type: str,
        floor: int = 0,
        area_sqft: float | None = None,
        position_x: float | None = None,
        position_y: float | None = None,
    ) -> Room:
        room = Room(
            household_id=UUID(household_id),
            name=name,
            room_type=room_type,
            floor=floor,
            area_sqft=area_sqft,
            position_x=position_x,
            position_y=position_y,
        )
        db.add(room)
        await db.flush()
        return room

    async def list_rooms(
        self, db: AsyncSession, household_id: str
    ) -> list[Room]:
        result = await db.execute(
            select(Room).where(Room.household_id == UUID(household_id))
        )
        return list(result.scalars().all())

    # ── Appliances ─────────────────────────────────────────────────────

    async def add_appliance(
        self,
        db: AsyncSession,
        household_id: str,
        name: str,
        appliance_type: str,
        room_id: str | None = None,
        brand: str | None = None,
        is_critical: bool = False,
        auto_schedule: dict[str, Any] | None = None,
    ) -> Appliance:
        appliance = Appliance(
            household_id=UUID(household_id),
            room_id=UUID(room_id) if room_id else None,
            name=name,
            appliance_type=appliance_type,
            brand=brand,
            is_critical=is_critical,
            auto_schedule=auto_schedule,
        )
        db.add(appliance)
        await db.flush()
        return appliance

    async def list_appliances(
        self, db: AsyncSession, household_id: str
    ) -> list[Appliance]:
        result = await db.execute(
            select(Appliance).where(Appliance.household_id == UUID(household_id))
        )
        return list(result.scalars().all())

    # ── Onboarding ─────────────────────────────────────────────────────

    async def complete_onboarding(
        self, db: AsyncSession, household_id: str
    ) -> Household:
        """Mark household onboarding as complete."""
        household = await self.get_household(db, household_id)
        household.onboarding_complete = True
        await db.flush()
        logger.info("onboarding_complete", household_id=household_id)
        return household


# ── Singleton instance ─────────────────────────────────────────────────
household_service = HouseholdService()
