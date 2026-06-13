"""
GHARMIND AI — Household API Endpoints
CRUD for households, members, rooms, appliances, and onboarding.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.security import CurrentUser, get_current_user
from app.dependencies import AuthUser, DBSession
from app.services.household_service import household_service
from app.services.twin_service import twin_service

router = APIRouter(prefix="/households", tags=["Households"])


# ── Request / Response schemas (inline Pydantic models) ───────────────

class CreateHouseholdRequest(BaseModel):
    name: str = Field(..., max_length=200, examples=["Sharma Residence"])
    city: str = Field(..., examples=["Pune"])
    state: str = Field(..., examples=["Maharashtra"])
    pincode: str | None = None
    home_type: str | None = Field(None, examples=["apartment"])
    language_preference: str = "hinglish"
    ai_persona_name: str = "Gharji"
    tags: list[str] = []


class AddMemberRequest(BaseModel):
    name: str = Field(..., examples=["Anjali"])
    role: str = Field(..., examples=["parent"])
    age: int | None = None
    gender: str | None = None
    nickname: str | None = None
    is_primary_contact: bool = False
    phone_number: str | None = None
    work_schedule: dict[str, Any] | None = None
    school_schedule: dict[str, Any] | None = None
    preferences: dict[str, Any] | None = None


class AddRoomRequest(BaseModel):
    name: str = Field(..., examples=["Pooja Room"])
    room_type: str = Field(..., examples=["pooja_room"])
    floor: int = 0
    area_sqft: float | None = None
    position_x: float | None = None
    position_y: float | None = None


class AddApplianceRequest(BaseModel):
    name: str = Field(..., examples=["Water Motor"])
    appliance_type: str = Field(..., examples=["motor"])
    room_id: str | None = None
    brand: str | None = None
    is_critical: bool = False
    auto_schedule: dict[str, Any] | None = None


# ── Endpoints ──────────────────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_household(
    body: CreateHouseholdRequest,
    db: DBSession,
    user: AuthUser,
) -> dict[str, Any]:
    """Create a new household for the authenticated user."""
    household = await household_service.create_household(
        db=db,
        owner_user_id=user.user_id,
        name=body.name,
        city=body.city,
        state=body.state,
        pincode=body.pincode,
        home_type=body.home_type,
        language_preference=body.language_preference,
        ai_persona_name=body.ai_persona_name,
        tags=body.tags,
    )
    return {
        "id": str(household.id),
        "name": household.name,
        "city": household.city,
        "state": household.state,
        "ai_persona_name": household.ai_persona_name,
        "language_preference": household.language_preference,
        "twin_initialized": household.twin_initialized,
        "onboarding_complete": household.onboarding_complete,
        "created_at": household.created_at.isoformat(),
    }


@router.get("/{household_id}")
async def get_household(
    household_id: str,
    db: DBSession,
    user: AuthUser,
) -> dict[str, Any]:
    """Get household details."""
    household = await household_service.get_household(db, household_id)
    members = await household_service.list_members(db, household_id)
    rooms = await household_service.list_rooms(db, household_id)
    appliances = await household_service.list_appliances(db, household_id)

    return {
        "id": str(household.id),
        "name": household.name,
        "city": household.city,
        "state": household.state,
        "home_type": household.home_type,
        "ai_persona_name": household.ai_persona_name,
        "language_preference": household.language_preference,
        "twin_initialized": household.twin_initialized,
        "onboarding_complete": household.onboarding_complete,
        "subscription_tier": household.subscription_tier,
        "tags": household.tags or [],
        "members_count": len(members),
        "rooms_count": len(rooms),
        "appliances_count": len(appliances),
        "created_at": household.created_at.isoformat(),
    }


@router.post("/{household_id}/members", status_code=status.HTTP_201_CREATED)
async def add_member(
    household_id: str,
    body: AddMemberRequest,
    db: DBSession,
    user: AuthUser,
) -> dict[str, Any]:
    """Add a family member to the household."""
    member = await household_service.add_member(
        db=db,
        household_id=household_id,
        name=body.name,
        role=body.role,
        age=body.age,
        gender=body.gender,
        nickname=body.nickname,
        is_primary_contact=body.is_primary_contact,
        phone_number=body.phone_number,
        work_schedule=body.work_schedule,
        school_schedule=body.school_schedule,
        preferences=body.preferences,
    )
    return {
        "id": str(member.id),
        "name": member.name,
        "role": member.role,
        "age": member.age,
        "is_primary_contact": member.is_primary_contact,
    }


@router.get("/{household_id}/members")
async def list_members(
    household_id: str,
    db: DBSession,
    user: AuthUser,
) -> dict[str, Any]:
    """List all family members."""
    members = await household_service.list_members(db, household_id)
    return {
        "total": len(members),
        "members": [
            {
                "id": str(m.id),
                "name": m.name,
                "nickname": m.nickname,
                "role": m.role,
                "age": m.age,
                "simulated_location": m.simulated_location,
                "is_primary_contact": m.is_primary_contact,
            }
            for m in members
        ],
    }


@router.post("/{household_id}/rooms", status_code=status.HTTP_201_CREATED)
async def add_room(
    household_id: str,
    body: AddRoomRequest,
    db: DBSession,
    user: AuthUser,
) -> dict[str, Any]:
    """Add a room to the household floor plan."""
    room = await household_service.add_room(
        db=db,
        household_id=household_id,
        name=body.name,
        room_type=body.room_type,
        floor=body.floor,
        area_sqft=body.area_sqft,
        position_x=body.position_x,
        position_y=body.position_y,
    )
    return {
        "id": str(room.id),
        "name": room.name,
        "room_type": room.room_type,
        "floor": room.floor,
    }


@router.post("/{household_id}/appliances", status_code=status.HTTP_201_CREATED)
async def add_appliance(
    household_id: str,
    body: AddApplianceRequest,
    db: DBSession,
    user: AuthUser,
) -> dict[str, Any]:
    """Add an appliance to the household."""
    appliance = await household_service.add_appliance(
        db=db,
        household_id=household_id,
        name=body.name,
        appliance_type=body.appliance_type,
        room_id=body.room_id,
        brand=body.brand,
        is_critical=body.is_critical,
        auto_schedule=body.auto_schedule,
    )
    return {
        "id": str(appliance.id),
        "name": appliance.name,
        "appliance_type": appliance.appliance_type,
        "is_critical": appliance.is_critical,
    }


@router.post("/{household_id}/initialize-twin")
async def initialize_twin(
    household_id: str,
    db: DBSession,
    user: AuthUser,
) -> dict[str, Any]:
    """Initialize the Household Digital Twin (run after onboarding)."""
    success = await twin_service.initialize_twin(db, household_id)
    return {
        "success": success,
        "message": "Digital Twin initialized successfully" if success else "Initialization failed",
        "household_id": household_id,
    }
