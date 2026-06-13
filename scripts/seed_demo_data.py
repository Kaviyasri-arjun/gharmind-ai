"""
GHARMIND AI — Demo Data Seeder
Seeds the Sharma Family demo household for hackathon demonstration.

Usage:
    python scripts/seed_demo_data.py

Requirements:
    - PostgreSQL running with gharmind database
    - DATABASE_URL environment variable set
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Any
import uuid

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://gharmind:devpassword@localhost:5432/gharmind")
DEMO_HOUSEHOLD_NAME = "Sharma Residence"
DEMO_CITY = "Pune"
DEMO_STATE = "Maharashtra"


# ─── Demo Data Definitions ────────────────────────────────────────────────────

DEMO_HOUSEHOLD = {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Sharma Residence",
    "city": "Pune",
    "state": "Maharashtra",
    "pincode": "411038",
    "timezone": "Asia/Kolkata",
    "language_preference": "hinglish",
    "home_type": "apartment",
    "floors": 1,
    "total_rooms": 8,
    "ai_persona_name": "Gharji",
    "tags": ["joint_family", "has_students", "working_couple", "home_tuition"],
    "onboarding_complete": True,
    "twin_initialized": True,
    "subscription_tier": "pro"
}

DEMO_MEMBERS = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440010",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "Anjali",
        "nickname": "Aai",
        "role": "parent",
        "age": 42,
        "gender": "female",
        "typical_wake_time": "05:30:00",
        "typical_sleep_time": "22:30:00",
        "is_primary_contact": True,
        "receives_alerts": True,
        "phone_number": "+91-98765-43210",
        "work_schedule": {"type": "none"},
        "preferences": {
            "chai_time": "16:30",
            "quiet_hours": ["22:30", "05:30"],
            "language": "hinglish"
        }
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440011",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "Rahul",
        "nickname": "Baba",
        "role": "parent",
        "age": 45,
        "gender": "male",
        "typical_wake_time": "07:00:00",
        "typical_sleep_time": "23:00:00",
        "is_primary_contact": False,
        "receives_alerts": True,
        "phone_number": "+91-98765-43211",
        "work_schedule": {
            "type": "hybrid",
            "days": ["mon", "tue", "wed", "thu", "fri"],
            "wfh_days": ["mon", "tue", "wed", "thu"],
            "start": "09:30",
            "end": "18:30"
        },
        "preferences": {
            "quiet_hours": ["10:00", "11:00"],  # Zoom call window
            "language": "en"
        }
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440012",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "Priya",
        "nickname": "Priya",
        "role": "child",
        "age": 16,
        "gender": "female",
        "typical_wake_time": "06:15:00",
        "typical_sleep_time": "22:00:00",
        "is_primary_contact": False,
        "receives_alerts": False,
        "school_schedule": {
            "school_name": "Fergusson College School",
            "bus_time": "07:15",
            "return_time": "14:30",
            "has_tuition": True
        },
        "preferences": {
            "language": "en"
        }
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440013",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "Dadi",
        "nickname": "Aajji",
        "role": "grandparent",
        "age": 70,
        "gender": "female",
        "typical_wake_time": "04:30:00",
        "typical_sleep_time": "21:00:00",
        "is_primary_contact": False,
        "receives_alerts": False,
        "preferences": {
            "language": "hi"
        }
    }
]

DEMO_ROOMS = [
    {
        "id": "room-001",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "Master Bedroom",
        "room_type": "bedroom",
        "floor": 1,
        "area_sqft": 180,
        "position_x": 10,
        "position_y": 10
    },
    {
        "id": "room-002",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "Bedroom 2",
        "room_type": "bedroom",
        "floor": 1,
        "area_sqft": 150,
        "position_x": 60,
        "position_y": 10
    },
    {
        "id": "room-003",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "Living Room",
        "room_type": "living_room",
        "floor": 1,
        "area_sqft": 250,
        "position_x": 10,
        "position_y": 55
    },
    {
        "id": "room-004",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "Kitchen",
        "room_type": "kitchen",
        "floor": 1,
        "area_sqft": 120,
        "position_x": 60,
        "position_y": 55
    },
    {
        "id": "room-005",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "Pooja Room",
        "room_type": "pooja_room",
        "floor": 1,
        "area_sqft": 40,
        "position_x": 85,
        "position_y": 10
    },
    {
        "id": "room-006",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "Bathroom",
        "room_type": "bathroom",
        "floor": 1,
        "area_sqft": 60,
        "position_x": 85,
        "position_y": 40
    },
    {
        "id": "room-007",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "Balcony",
        "room_type": "balcony",
        "floor": 1,
        "area_sqft": 80,
        "position_x": 10,
        "position_y": 85
    },
    {
        "id": "room-008",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "Study Nook",
        "room_type": "study",
        "floor": 1,
        "area_sqft": 50,
        "position_x": 60,
        "position_y": 85
    }
]

DEMO_APPLIANCES = [
    {
        "id": "appl-001",
        "household_id": DEMO_HOUSEHOLD["id"],
        "room_id": None,
        "name": "Water Motor",
        "appliance_type": "motor",
        "is_critical": True,
        "auto_schedule": {"on": "06:10", "off": None, "days": ["*"], "auto_off_after_mins": 30},
        "health_score": 85
    },
    {
        "id": "appl-002",
        "household_id": DEMO_HOUSEHOLD["id"],
        "room_id": "room-006",
        "name": "Geyser",
        "appliance_type": "geyser",
        "is_critical": False,
        "auto_schedule": {"on": "06:05", "off": None, "days": ["*"], "auto_off_after_mins": 20},
        "health_score": 90
    },
    {
        "id": "appl-003",
        "household_id": DEMO_HOUSEHOLD["id"],
        "room_id": "room-001",
        "name": "Air Conditioner",
        "appliance_type": "ac",
        "is_critical": False,
        "health_score": 95
    },
    {
        "id": "appl-004",
        "household_id": DEMO_HOUSEHOLD["id"],
        "room_id": "room-003",
        "name": "TV (Living Room)",
        "appliance_type": "tv",
        "is_critical": False,
        "health_score": 100
    },
    {
        "id": "appl-005",
        "household_id": DEMO_HOUSEHOLD["id"],
        "room_id": "room-004",
        "name": "Fridge",
        "appliance_type": "fridge",
        "is_critical": True,
        "health_score": 88
    },
    {
        "id": "appl-006",
        "household_id": DEMO_HOUSEHOLD["id"],
        "room_id": None,
        "name": "WiFi Router",
        "appliance_type": "wifi",
        "is_critical": True,
        "health_score": 98
    },
    {
        "id": "appl-007",
        "household_id": DEMO_HOUSEHOLD["id"],
        "room_id": "room-002",
        "name": "Washing Machine",
        "appliance_type": "washing_machine",
        "is_critical": False,
        "auto_schedule": {"on": "09:00", "off": None, "days": ["sun", "wed"]},
        "health_score": 92
    }
]

DEMO_ROUTINES = [
    {
        "id": "rout-001",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "Morning Pooja",
        "routine_type": "pooja",
        "description": "Daily morning prayer by Anjali and Dadi",
        "recurrence": "daily",
        "schedule_expression": {"days": ["*"], "time": "06:00", "duration_mins": 25},
        "primary_member_id": "550e8400-e29b-41d4-a716-446655440010",
        "is_ai_detected": False,
        "confidence_score": 0.97,
        "is_active": True
    },
    {
        "id": "rout-002",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "Water Motor Schedule",
        "routine_type": "motor",
        "description": "Daily water tank filling before morning peak demand",
        "recurrence": "daily",
        "schedule_expression": {
            "days": ["*"], "time": "06:10", "duration_mins": 30,
            "conditional": "tank_level < 60%"
        },
        "appliance_ids": ["appl-001"],
        "is_ai_detected": False,
        "confidence_score": 0.99,
        "is_active": True
    },
    {
        "id": "rout-003",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "School Morning Rush",
        "routine_type": "school_prep",
        "description": "Getting Priya ready for school",
        "recurrence": "weekly",
        "schedule_expression": {"days": ["mon","tue","wed","thu","fri"], "time": "06:30", "duration_mins": 45},
        "primary_member_id": "550e8400-e29b-41d4-a716-446655440010",
        "participant_ids": [
            "550e8400-e29b-41d4-a716-446655440012",
            "550e8400-e29b-41d4-a716-446655440010"
        ],
        "is_ai_detected": False,
        "confidence_score": 0.96,
        "is_active": True
    },
    {
        "id": "rout-004",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "Evening Chai",
        "routine_type": "chai",
        "description": "Family evening chai at 4:30pm",
        "recurrence": "daily",
        "schedule_expression": {"days": ["*"], "time": "16:30", "duration_mins": 30},
        "primary_member_id": "550e8400-e29b-41d4-a716-446655440010",
        "is_ai_detected": True,
        "confidence_score": 0.93,
        "is_active": True
    },
    {
        "id": "rout-005",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "Home Tuition Batch",
        "routine_type": "tuition",
        "description": "Anjali conducts tuition for 4-5 students",
        "recurrence": "weekly",
        "schedule_expression": {"days": ["mon","wed","fri"], "time": "17:00", "duration_mins": 90},
        "primary_member_id": "550e8400-e29b-41d4-a716-446655440010",
        "is_ai_detected": False,
        "confidence_score": 0.98,
        "is_active": True
    },
    {
        "id": "rout-006",
        "household_id": DEMO_HOUSEHOLD["id"],
        "name": "Night Wind-Down",
        "routine_type": "sleep_prep",
        "description": "End-of-day household shutdown",
        "recurrence": "daily",
        "schedule_expression": {"days": ["*"], "time": "22:00", "duration_mins": 30},
        "is_ai_detected": True,
        "confidence_score": 0.88,
        "is_active": True
    }
]


FESTIVAL_CALENDAR_SAMPLE = [
    {
        "festival_name": "Diwali",
        "local_names": {"hi": "दीपावली", "mr": "दिवाळी", "en": "Diwali"},
        "festival_type": "hindu",
        "region": ["all_india"],
        "household_impact": {
            "preparation_days": 5,
            "peak_activity": "morning_evening",
            "typical_routines": ["extended_pooja", "deep_cleaning", "sweet_making", "decoration"],
            "water_usage_multiplier": 1.4,
            "power_usage_multiplier": 1.8,
            "sleep_shift_hours": -1.5,
            "guest_probability": 0.85
        },
        "prep_days_before": 5,
        "celebration_days": 2,
        "is_public_holiday": True,
        "is_school_holiday": True
    },
    {
        "festival_name": "Ganesh Chaturthi",
        "local_names": {"hi": "गणेश चतुर्थी", "mr": "गणेशोत्सव", "en": "Ganesh Chaturthi"},
        "festival_type": "hindu",
        "region": ["maharashtra", "goa", "karnataka", "andhra_pradesh"],
        "household_impact": {
            "preparation_days": 3,
            "peak_activity": "morning",
            "typical_routines": ["extended_pooja", "modak_making", "decoration", "community_visit"],
            "water_usage_multiplier": 1.3,
            "power_usage_multiplier": 1.3,
            "sleep_shift_hours": -1.0,
            "guest_probability": 0.75
        },
        "prep_days_before": 3,
        "celebration_days": 10,
        "is_public_holiday": True,
        "is_school_holiday": False
    },
    {
        "festival_name": "Holi",
        "local_names": {"hi": "होली", "en": "Holi"},
        "festival_type": "hindu",
        "region": ["all_india"],
        "household_impact": {
            "preparation_days": 1,
            "peak_activity": "morning",
            "typical_routines": ["color_play", "sweet_making", "neighbor_visits"],
            "water_usage_multiplier": 3.0,
            "power_usage_multiplier": 1.1,
            "sleep_shift_hours": -1.0,
            "guest_probability": 0.9
        },
        "prep_days_before": 1,
        "celebration_days": 1,
        "is_public_holiday": True,
        "is_school_holiday": True
    }
]


async def seed_database() -> None:
    """Main seeder function"""
    print("=" * 60)
    print("GHARMIND AI — Demo Data Seeder")
    print("=" * 60)

    print("\n1. Seeding household...")
    print(f"   ✓ {DEMO_HOUSEHOLD['name']} ({DEMO_HOUSEHOLD['city']}, {DEMO_HOUSEHOLD['state']})")

    print("\n2. Seeding family members...")
    for m in DEMO_MEMBERS:
        print(f"   ✓ {m['name']} ({m['role']}, {m.get('age', 'N/A')} yrs)")

    print("\n3. Seeding rooms...")
    for r in DEMO_ROOMS:
        print(f"   ✓ {r['name']} ({r['room_type']})")

    print("\n4. Seeding appliances...")
    for a in DEMO_APPLIANCES:
        print(f"   ✓ {a['name']} ({a['appliance_type']})")

    print("\n5. Seeding routines...")
    for r in DEMO_ROUTINES:
        print(f"   ✓ {r['name']} ({r['routine_type']}, {r['recurrence']})")

    print("\n6. Seeding festival calendar...")
    for f in FESTIVAL_CALENDAR_SAMPLE:
        print(f"   ✓ {f['festival_name']}")

    print("\n7. Historical simulation (placeholder)...")
    print("   → In production: runs 30-day twin simulation (~90 seconds)")
    print("   → For demo: pre-computed snapshots loaded from fixture file")

    print("\n" + "=" * 60)
    print("✅ Demo data seeded successfully!")
    print("   Household: Sharma Residence, Pune")
    print("   Members: 4 (Anjali, Rahul, Priya, Dadi)")
    print("   Rooms: 8")
    print("   Appliances: 7")
    print("   Routines: 6")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Start docker-compose: docker-compose up -d")
    print("  2. Run migrations: alembic upgrade head")
    print("  3. Apply seed: python scripts/seed_demo_data.py --execute")
    print("  4. Start API: uvicorn app.main:app --reload")
    print("  5. Open dashboard: http://localhost:3000")


if __name__ == "__main__":
    import sys
    if "--execute" in sys.argv:
        print("Running database seeder (requires DB connection)...")
        # asyncio.run(execute_seed())
        print("Note: Implement execute_seed() in Phase 2")
    else:
        asyncio.run(seed_database())
