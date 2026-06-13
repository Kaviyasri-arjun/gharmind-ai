# GHARMIND AI — Household Digital Twin Design

---

## What Is the Household Digital Twin?

The Household Digital Twin (HDT) is a **continuously running software simulation** of a real Indian home. It maintains a live virtual replica of the household — its rooms, appliances, family members, routines, and environmental conditions — without any physical sensors.

Instead of IoT sensors, the HDT uses:
- **User-provided data** (household setup, member schedules, routine definitions)
- **Statistical models** of Indian household behavior
- **Festival/seasonal context** to modulate baseline patterns
- **Historical pattern replay** to simulate realistic variation

The result is a system that *behaves like* a sensor-equipped smart home without requiring any hardware.

---

## Digital Twin Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                    HOUSEHOLD DIGITAL TWIN                      │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    TWIN ENGINE                           │  │
│  │  (State machine running on 1-minute tick)               │  │
│  └──────────┬─────────────────────────────────────────────┘  │
│             │                                                  │
│   ┌─────────▼───────────────────────────────────────────┐    │
│   │                  STATE MODELS                        │    │
│   │                                                      │    │
│   │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │    │
│   │  │ Occupancy    │  │ Appliance    │  │  Time     │  │    │
│   │  │ Model        │  │ Model        │  │  Model    │  │    │
│   │  │              │  │              │  │           │  │    │
│   │  │ Who is home  │  │ What's on   │  │ IST clock │  │    │
│   │  │ What room    │  │ Power draw  │  │ Phase day │  │    │
│   │  │ What doing   │  │ Schedules   │  │ Season    │  │    │
│   │  └──────────────┘  └──────────────┘  └───────────┘  │    │
│   │                                                      │    │
│   │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │    │
│   │  │ Water        │  │ Power        │  │ Pattern   │  │    │
│   │  │ Model        │  │ Model        │  │ Detector  │  │    │
│   │  │              │  │              │  │           │  │    │
│   │  │ Tank level   │  │ Grid status │  │ Routine   │  │    │
│   │  │ Supply sched │  │ Cut history  │  │ learning  │  │    │
│   │  │ Usage rate   │  │ Quality      │  │ Anomaly   │  │    │
│   │  └──────────────┘  └──────────────┘  └───────────┘  │    │
│   └──────────────────────────────────────────────────────┘    │
│             │                                                  │
│   ┌─────────▼─────────────────────────────────────────────┐   │
│   │              EVENT SIMULATOR                           │   │
│   │  Generates synthetic household events every minute    │   │
│   │  Emits: state_changed, routine_triggered, anomaly_    │   │
│   │         detected, resource_event, member_moved        │   │
│   └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                          │
               ┌──────────▼──────────┐
               │   Event Stream      │
               │   (Redis Pub/Sub)   │
               └──────────┬──────────┘
                          │
         ┌────────────────┼────────────────────┐
         ▼                ▼                    ▼
   ContextAgent    WebSocket clients    Snapshot Store
```

---

## The Twin Tick Cycle

The Digital Twin runs on a **1-minute tick cycle**:

```
Every 60 seconds:
│
├─ 1. advance_time()
│      Update IST clock, check phase-of-day transitions
│
├─ 2. apply_routine_triggers()
│      Check all active routines — should any start/stop now?
│      Apply schedule expressions against current time
│
├─ 3. update_occupancy()
│      Move members between rooms based on routine logic
│      Apply probabilistic transitions (e.g., 80% chance Anjali moves
│      from pooja room to kitchen at 7am on weekdays)
│
├─ 4. update_appliances()
│      Apply appliance state transitions based on:
│      - Manual schedules
│      - Routine triggers
│      - Occupancy (lights follow members)
│      - Energy models (geyser off after 20 min)
│
├─ 5. update_resources()
│      Water tank: deduct usage, check supply schedule
│      Power: check cut schedule, apply noise
│      Internet: check connectivity model
│
├─ 6. detect_patterns()
│      Compare current state against routine expectations
│      Flag anomalies (motor not running, member not returned)
│
├─ 7. generate_snapshot()
│      Serialize full household state to PostgreSQL
│      Emit state_update event to Redis pub/sub
│
└─ 8. update_next_expected_times()
       Update routine.next_expected_at for all active routines
```

---

## Occupancy Model

### Member Movement Simulation

Member locations are simulated using a **probabilistic state machine** per member, per time-of-day.

```python
# Example: Anjali (Mother) movement model — weekday
ANJALI_WEEKDAY_MODEL = {
    "04:00-06:00": {"pooja_room": 0.7, "bedroom": 0.3},
    "06:00-07:30": {"kitchen": 0.65, "pooja_room": 0.25, "bedroom": 0.1},
    "07:30-08:30": {"kitchen": 0.5, "living_room": 0.3, "balcony": 0.2},
    "08:30-10:00": {"kitchen": 0.4, "bedroom": 0.3, "living_room": 0.3},
    "10:00-12:00": {"living_room": 0.4, "kitchen": 0.3, "bedroom": 0.3},
    "12:00-14:00": {"kitchen": 0.8, "living_room": 0.2},
    "14:00-16:00": {"bedroom": 0.6, "living_room": 0.4},   # Afternoon rest
    "16:00-17:30": {"kitchen": 0.7, "living_room": 0.3},   # Chai time
    "17:30-20:00": {"kitchen": 0.5, "living_room": 0.3, "study": 0.2},
    "20:00-22:00": {"living_room": 0.6, "kitchen": 0.3, "bedroom": 0.1},
    "22:00-04:00": {"bedroom": 0.98, "bathroom": 0.02},
}
```

### Festival Adjustment
During festival weeks, all models shift:
- Pooja room probability × 3 during festival prep
- Kitchen probability × 1.5 (more cooking)
- Bedroom (rest) probability × 0.5 (less sleep during celebrations)

---

## Appliance State Model

### Appliance Behavior Types

| Type | Simulation Approach |
|---|---|
| **Schedule-driven** (motor, geyser) | Fixed on/off times ± Gaussian noise (σ = 10 min) |
| **Occupancy-driven** (lights, fans) | Turn on/off based on room occupancy |
| **Routine-driven** (washing machine, mixer) | Trigger when associated routine is active |
| **Always-on** (fridge, WiFi) | Continuous, occasional simulated restarts |
| **Demand-driven** (AC, cooler) | Conditional on simulated temperature model |

### Water Motor Simulation

```python
class WaterMotorModel:
    """
    Simulates water tank level and motor run decisions.
    This is the single most important appliance for Indian households.
    """

    TANK_CAPACITY_LITERS = 1000
    DAILY_USAGE_LITERS = {
        "weekday": 450,
        "weekend": 600,
        "festival_week": 700,
        "guest_present": 800
    }

    SUPPLY_WINDOWS = {
        "metro": [{"start": "06:00", "duration_mins": 60}],
        "tier2": [{"start": "05:30", "duration_mins": 45}, {"start": "17:00", "duration_mins": 30}],
        "rural": [{"start": "06:00", "duration_mins": 30}]
    }

    def should_run_motor(self, state: TwinState) -> tuple[bool, str]:
        tank_pct = state.water_tank_level / self.TANK_CAPACITY_LITERS

        if tank_pct < 0.20:
            return True, "CRITICAL: Tank below 20%"
        if tank_pct < 0.40 and self._is_pre_peak_time(state.ist_time):
            return True, "Pre-emptive fill before morning peak"
        if tank_pct < 0.50 and state.cultural.festival_active:
            return True, "Festival week — maintain higher level"

        return False, "Tank level sufficient"
```

### Power Cut Simulation

```python
class PowerModel:
    """
    Simulates MSEDCL / BESCOM / TNEB-style load shedding patterns.
    Uses city-specific patterns loaded from seed data.
    """

    def __init__(self, city: str):
        self.cut_schedule = self._load_city_schedule(city)
        # Typical patterns: Mon/Tue 7:30pm, Thu 2pm, some randomness
        self.reliability_score = 0.75  # 75% adherence to schedule

    def get_power_status(self, ist_datetime: datetime) -> PowerStatus:
        scheduled_cut = self._check_schedule(ist_datetime)
        if scheduled_cut:
            # Apply reliability noise
            if random.random() < self.reliability_score:
                return PowerStatus.CUT
            # Or it came late
            if random.random() < 0.2:
                return PowerStatus.UNSTABLE
        return PowerStatus.AVAILABLE
```

---

## Household Twin State Schema

The in-memory state object kept by the twin engine:

```python
@dataclass
class HouseholdTwinState:
    household_id: UUID
    as_of: datetime   # IST datetime

    # Temporal
    phase_of_day: str
    season: str
    festivals_active: list[str]
    is_school_day: bool

    # Members
    member_locations: dict[UUID, str]     # member_id → room_name
    member_activities: dict[UUID, str]    # member_id → current_activity
    members_home: list[UUID]

    # Rooms
    room_occupancy: dict[UUID, bool]
    room_occupants: dict[UUID, list[UUID]]

    # Appliances
    appliance_states: dict[UUID, ApplianceState]

    # Resources
    water_tank_level_pct: float
    power_available: bool
    power_quality: str        # stable, unstable, cut
    internet_available: bool

    # Routines
    active_routine_ids: list[UUID]
    overdue_routine_ids: list[UUID]

    # Derived metrics
    activity_level: str    # quiet, moderate, active, peak
    urgency_score: int
```

---

## Pattern Detector

The Pattern Detector runs as part of the tick cycle to identify behavioral patterns from routine execution history.

### Pattern Types Detected

```python
DETECTABLE_PATTERNS = {
    "temporal_pattern": {
        "description": "Routine consistently happens at same time",
        "detection": "stddev(execution_times) < 15 minutes over 10+ instances",
        "example": "Motor always runs 6:10-6:40am on weekdays"
    },
    "sequential_pattern": {
        "description": "Routine A consistently precedes Routine B",
        "detection": "correlation(A.time, B.time) > 0.8 with B always 20-40 min after A",
        "example": "Geyser on → 20 min → Someone bathes → 5 min → Geyser off"
    },
    "conditional_pattern": {
        "description": "Routine changes based on context",
        "detection": "statistically different timing between context states",
        "example": "Motor runs 30 min earlier on festival weeks"
    },
    "seasonal_pattern": {
        "description": "Routine behavior varies by season",
        "detection": "ANOVA across seasons shows significant difference",
        "example": "AC runs all night in summer, rarely in winter"
    },
    "absence_pattern": {
        "description": "Routine that normally happens did NOT happen",
        "detection": "Expected routine not executed within 2σ of normal window",
        "example": "Anjali didn't do evening pooja — unusual on weekdays"
    }
}
```

---

## Demo Household: Sharma Family, Pune

### Profile

| Detail | Value |
|---|---|
| Location | Kothrud, Pune, Maharashtra |
| Home Type | 3BHK Apartment, Floor 4 |
| City Type | Tier 1 (Metro) |
| MSEDCL Zone | Load shedding Mon/Tue 7:30pm |
| Water Supply | PCMC — 6am, 45 minutes daily |

### Family Members

| Member | Role | Key Routine |
|---|---|---|
| Anjali (42) | Mother/Homemaker | Morning pooja, tuition batches, evening prep |
| Rahul (45) | Father/IT Manager | WFH Mon-Thu, office Fri, 10am Zoom |
| Priya (16) | Daughter/JEE Student | School 7:15, tuition 5pm, study 9pm |
| Dadi (70) | Grandmother | Early rising, 6am aarti, afternoon nap |
| Kaka (35) | Uncle (tenant/relative) | Irregular schedule |

### Rooms

| Room | Type | Key Features |
|---|---|---|
| Master Bedroom | Bedroom | AC, attached bath |
| Bedroom 2 (Priya+Dadi) | Bedroom | Shared, study table |
| Living Room | Living | TV, sofa, tuition space |
| Kitchen | Kitchen | Chimney, 3-burner, fridge |
| Pooja Room | Pooja Room | Dedicated, lamp always on |
| Bathroom 1 | Bathroom | Shared |
| Balcony | Balcony | Washing, plants, Dadi's sitting |
| Study Nook | Study | Computer, printer |

### Key Appliances

| Appliance | Type | Schedule |
|---|---|---|
| Water Motor | Motor | 6:10am auto-start |
| Geyser | Geyser | 6:05am, off after 20 min |
| AC (Master) | AC | On when Rahul WFH and temp > 28°C |
| Washing Machine | Washing | Sun/Wed 9am |
| WiFi Router | Network | Always-on |
| TV (Living) | TV | Evening 8pm, news |
| Chimney | Kitchen | During cooking |
| Pooja Lamp | Ritual | Always on |

---

## Twin Initialization Flow

When a new household is onboarded:

```
1. USER INPUT (Onboarding wizard)
   └─ Family members + schedules
   └─ Rooms and appliances
   └─ Known routines
   └─ City + pincode

2. TWIN INITIALIZATION
   └─ Load city's power cut schedule
   └─ Load city's water supply schedule
   └─ Initialize tank at 60%
   └─ Set all appliances to default states
   └─ Compute initial routine schedule

3. HISTORICAL SIMULATION (background job)
   └─ Simulate last 30 days of household activity
   └─ Generate 43,200 state snapshots (30 days × 1440 min)
   └─ Embed all snapshots with Titan
   └─ Store in twin_state_snapshots
   └─ Extract initial pattern memories

4. FIRST CONTEXT GENERATION
   └─ ContextAgent runs immediately
   └─ First predictions generated
   └─ Dashboard populated

Total onboarding time: ~2-3 minutes
```
