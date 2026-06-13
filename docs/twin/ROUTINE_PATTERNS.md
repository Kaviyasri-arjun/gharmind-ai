# GHARMIND AI — Indian Household Routine Catalog

A comprehensive catalog of routine patterns unique to Indian households.
These serve as seed templates and training signals for the AI pattern engine.

---

## Routine Categories

```
DAILY ROUTINES
  ├── Spiritual / Ritual
  ├── Morning Operations
  ├── School / Education
  ├── Work / Professional
  ├── Meals
  ├── Hygiene / Cleaning
  └── Evening / Night

WEEKLY ROUTINES
  ├── Deep Cleaning
  ├── Religious (weekly)
  └── Shopping / Errands

SEASONAL ROUTINES
  ├── Monsoon-specific
  ├── Summer-specific
  └── Winter-specific

FESTIVAL ROUTINES
  ├── Diwali
  ├── Ganesh Chaturthi
  ├── Navratri / Garba
  ├── Holi
  ├── Eid
  └── Christmas

CONDITIONAL ROUTINES
  ├── Exam Week
  ├── Guest Visit
  ├── Power Cut Response
  └── Water Shortage
```

---

## Routine Templates (Seed Data)

### R001: Morning Pooja

```json
{
  "id": "template_morning_pooja",
  "name": "Morning Pooja",
  "routine_type": "pooja",
  "description": "Daily morning prayer ritual",
  "recurrence": "daily",
  "schedule_expression": {
    "days": ["*"],
    "time": "06:00",
    "duration_mins": 20
  },
  "festival_overrides": {
    "any_festival": {"duration_multiplier": 2.5, "start_time_shift_mins": -30},
    "ganesh_chaturthi": {"duration_multiplier": 4.0, "start_time_shift_mins": -60}
  },
  "rooms_involved": ["pooja_room"],
  "appliances_involved": ["pooja_lamp", "incense_burner"],
  "quiet_required": true,
  "typical_members": ["grandmother", "mother"],
  "regional_prevalence": "high",
  "regions": ["maharashtra", "gujarat", "karnataka", "andhra_pradesh", "tamil_nadu"]
}
```

### R002: Water Motor Operation

```json
{
  "id": "template_water_motor",
  "name": "Water Motor Schedule",
  "routine_type": "motor",
  "description": "Daily water tank filling before peak demand",
  "recurrence": "daily",
  "schedule_expression": {
    "days": ["*"],
    "time": "06:00",
    "duration_mins": 30,
    "conditional": "tank_level < 60%"
  },
  "seasonal_overrides": {
    "summer": {"start_time_shift_mins": -30, "duration_multiplier": 1.2},
    "monsoon": {"start_time_shift_mins": 0, "duration_multiplier": 0.8}
  },
  "city_overrides": {
    "water_supply_time": "adjust start to 15min before supply window"
  },
  "appliances_involved": ["water_motor"],
  "urgency": "critical",
  "typical_members": ["any_adult"],
  "indian_pain_point_rank": 1,
  "notes": "Voted #1 most stressful daily task by Indian households in surveys"
}
```

### R003: School Morning Rush

```json
{
  "id": "template_school_morning",
  "name": "School Morning Rush",
  "routine_type": "school_prep",
  "description": "Getting child ready for school — breakfast, uniform, bag",
  "recurrence": "weekly",
  "schedule_expression": {
    "days": ["mon", "tue", "wed", "thu", "fri"],
    "time": "06:30",
    "duration_mins": 45
  },
  "sub_routines": [
    {"name": "wake_child", "time": "06:30"},
    {"name": "breakfast_prep", "time": "06:45", "duration_mins": 20},
    {"name": "bag_check", "time": "07:00"},
    {"name": "school_bus_wait", "time": "07:10", "duration_mins": 10}
  ],
  "members": ["mother", "school_child"],
  "rooms_involved": ["bedroom", "kitchen", "bathroom"],
  "downstream_dependencies": ["water_motor", "geyser"],
  "exam_week_override": {"start_time_shift_mins": -30, "intensity": "high"}
}
```

### R004: Evening Chai

```json
{
  "id": "template_evening_chai",
  "name": "Evening Chai Time",
  "routine_type": "chai",
  "description": "The sacred Indian evening chai ritual",
  "recurrence": "daily",
  "schedule_expression": {
    "days": ["*"],
    "time": "16:30",
    "duration_mins": 30,
    "tolerance_mins": 30
  },
  "social_context": "Often includes neighbor visits, family gathering",
  "rooms_involved": ["kitchen", "living_room", "balcony"],
  "appliances_involved": ["gas_stove"],
  "members": ["any_home_members"],
  "wfh_override": {
    "additional_chai_at": ["10:30", "13:00"],
    "notes": "WFH increases daily chai count to 3-4"
  },
  "indian_pain_point_rank": 2,
  "universality": "extremely_high"
}
```

### R005: Home Tuition Batch

```json
{
  "id": "template_home_tuition",
  "name": "Home Tuition Batch",
  "routine_type": "tuition",
  "description": "Tuition classes conducted at home",
  "recurrence": "weekly",
  "schedule_expression": {
    "days": ["mon", "wed", "fri"],
    "time": "17:00",
    "duration_mins": 90
  },
  "household_impact": {
    "noise_required": "low",
    "rooms_reserved": ["living_room", "study"],
    "extra_persons": 4,
    "water_usage_extra": true,
    "snack_prep_at": "16:45"
  },
  "members": ["mother_as_teacher", "visiting_students"],
  "quiet_enforcement": "moderate"
}
```

### R006: Geyser / Hot Water Schedule

```json
{
  "id": "template_geyser",
  "name": "Geyser Morning Schedule",
  "routine_type": "appliance",
  "description": "Morning hot water preparation for bathing",
  "recurrence": "daily",
  "schedule_expression": {
    "days": ["*"],
    "time": "06:05",
    "auto_off_after_mins": 20
  },
  "winter_override": {
    "start_time_shift_mins": -10,
    "duration_multiplier": 1.3
  },
  "summer_override": {
    "skip_if_ambient_temp_above": 30
  },
  "appliances_involved": ["geyser"],
  "safety_note": "Auto-off critical — forgetting geyser is common"
}
```

### R007: Evening Aarti / Prayer

```json
{
  "id": "template_evening_aarti",
  "name": "Evening Aarti (Sandhya)",
  "routine_type": "pooja",
  "description": "Evening prayer, typically at sunset",
  "recurrence": "daily",
  "schedule_expression": {
    "days": ["*"],
    "time": "sunset",
    "duration_mins": 10
  },
  "sunset_based": true,
  "rooms_involved": ["pooja_room", "living_room"],
  "quiet_required": true,
  "members": ["grandmother", "mother"],
  "regional_prevalence": "very_high"
}
```

### R008: Weekly Deep Cleaning

```json
{
  "id": "template_deep_cleaning",
  "name": "Weekly Deep Cleaning",
  "routine_type": "cleaning",
  "description": "Full household cleaning — mopping, dusting, bathrooms",
  "recurrence": "weekly",
  "schedule_expression": {
    "days": ["sun"],
    "time": "09:00",
    "duration_mins": 180
  },
  "festival_override": {
    "any_festival_prep": {
      "frequency": "daily",
      "duration_multiplier": 1.5,
      "days_before_trigger": 5
    }
  },
  "rooms_involved": ["all"],
  "water_usage_multiplier": 2.0,
  "members": ["mother", "available_adults"]
}
```

### R009: Laundry Cycle

```json
{
  "id": "template_laundry",
  "name": "Laundry Schedule",
  "routine_type": "cleaning",
  "recurrence": "weekly",
  "schedule_expression": {
    "days": ["sun", "wed"],
    "time": "09:00",
    "duration_mins": 60
  },
  "sub_routines": [
    {"name": "load_machine", "time": "09:00"},
    {"name": "hang_clothes", "time": "10:00"},
    {"name": "fold_evening", "time": "17:00"}
  ],
  "appliances_involved": ["washing_machine"],
  "rooms_involved": ["bathroom", "balcony"],
  "weather_dependency": {
    "avoid_if": "rain_forecast AND balcony_only"
  }
}
```

### R010: Power Cut Response Protocol

```json
{
  "id": "template_power_cut_response",
  "name": "Power Cut Protocol",
  "routine_type": "conditional",
  "description": "Automatic household response to power cut",
  "recurrence": "conditional",
  "trigger": "power_available == FALSE",
  "pre_cut_actions": [
    {"action": "charge_all_devices", "trigger_mins_before": 30},
    {"action": "complete_cooking", "trigger_mins_before": 45},
    {"action": "fill_water_bottles", "trigger_mins_before": 15}
  ],
  "during_cut_actions": [
    {"action": "switch_to_inverter", "priority": "critical"},
    {"action": "reduce_fan_count", "note": "Inverter backup management"},
    {"action": "switch_to_phone_data", "note": "WiFi down"}
  ],
  "post_cut_actions": [
    {"action": "restart_motor_if_needed"},
    {"action": "check_fridge_items"},
    {"action": "restart_pending_appliances"}
  ]
}
```

### R011: Exam Week Protocol

```json
{
  "id": "template_exam_week",
  "name": "Exam Week Mode",
  "routine_type": "study",
  "description": "Full household adjustment during school/competitive exams",
  "recurrence": "conditional",
  "trigger": "exam_period == TRUE",
  "household_adjustments": {
    "quiet_hours_extended": ["06:00", "23:30"],
    "tv_restricted_to": ["20:00", "21:00"],
    "tuition_home_visits": "cancelled",
    "social_visits": "discouraged",
    "meal_times": "flexible",
    "chai_delivery_to_study_room": true
  },
  "study_schedule": {
    "morning_session": {"time": "05:30", "duration_hrs": 2},
    "evening_session": {"time": "18:00", "duration_hrs": 3},
    "night_session": {"time": "21:00", "duration_hrs": 2}
  },
  "members_affected": ["all"],
  "primary_member": "student"
}
```

### R012: Guest Arrival Preparation

```json
{
  "id": "template_guest_arrival",
  "name": "Guest Arrival Prep",
  "routine_type": "conditional",
  "description": "Preparation when guests are expected",
  "recurrence": "conditional",
  "trigger": "guest_expected_within_hours <= 6",
  "prep_cascade": [
    {"task": "extra_cleaning", "trigger_hours_before": 6},
    {"task": "guest_room_prep", "trigger_hours_before": 3},
    {"task": "extra_cooking", "trigger_hours_before": 2},
    {"task": "snack_arrangement", "trigger_hours_before": 1},
    {"task": "fresh_chai_ready", "trigger_mins_before": 30}
  ],
  "resource_adjustments": {
    "water_usage_multiplier": 1.5,
    "cooking_sessions_extra": 2,
    "extra_bed_linens": true
  }
}
```

### R013: Monsoon Routine Adjustments

```json
{
  "id": "template_monsoon_adjustments",
  "name": "Monsoon Season Routines",
  "routine_type": "seasonal",
  "season": "monsoon",
  "active_months": [6, 7, 8, 9],
  "adjustments": {
    "water_motor": {"frequency_change": "less_frequent", "note": "Rain supplements supply"},
    "laundry": {"timing_change": "morning_only", "note": "Afternoon rain risk"},
    "windows": {"close_at": "14:00", "note": "Pre-emptive rain close"},
    "drying": {"move_inside_if_rain": true},
    "umbrella_reminder": {"trigger": "morning_departure"},
    "footwear_mat": {"at_entry": "mandatory"}
  }
}
```

### R014: Festival Preparation Cascade

```json
{
  "id": "template_festival_prep",
  "name": "Festival Preparation",
  "routine_type": "festival",
  "description": "Multi-day festival preparation routine cascade",
  "recurrence": "annual",
  "applicable_festivals": ["diwali", "ganesh_chaturthi", "navratri"],
  "prep_timeline": {
    "days_before_7": {
      "tasks": ["order_supplies", "plan_menu"],
      "intensity": "low"
    },
    "days_before_5": {
      "tasks": ["deep_cleaning_begins", "decoration_shopping"],
      "intensity": "moderate",
      "water_usage_extra": 1.3
    },
    "days_before_3": {
      "tasks": ["main_cleaning", "rangoli_materials", "sweet_making_starts"],
      "intensity": "high",
      "water_usage_extra": 1.5,
      "cooking_sessions_extra": 2
    },
    "days_before_1": {
      "tasks": ["final_cleaning", "decoration_setup", "cooking_peak"],
      "intensity": "very_high",
      "all_hands_on_deck": true
    },
    "day_of": {
      "morning_shift_hours": -2,
      "pooja_duration_multiplier": 3.0,
      "guest_probability": 0.9
    }
  }
}
```

### R015: Night Wind-Down Routine

```json
{
  "id": "template_night_windown",
  "name": "Night Wind-Down",
  "routine_type": "sleep_prep",
  "description": "End-of-day household shutdown routine",
  "recurrence": "daily",
  "schedule_expression": {
    "days": ["*"],
    "time": "22:00",
    "duration_mins": 30
  },
  "sub_routines": [
    {"task": "lock_main_door", "time": "22:00"},
    {"task": "turn_off_main_lights", "time": "22:15"},
    {"task": "check_gas_off", "time": "22:10"},
    {"task": "check_motor_off", "time": "22:00"},
    {"task": "set_morning_alarm", "time": "22:30"}
  ],
  "appliances_to_check": ["gas_stove", "water_motor", "geyser", "fans_all"],
  "notes": "Forgetting to check gas/motor is a common household anxiety"
}
```

---

## Routine Frequency Matrix

| Routine | Daily | Weekly | Monthly | Festival | Conditional |
|---|---|---|---|---|---|
| Morning Pooja | ✓ | | | Extended | |
| Water Motor | ✓ | | | Increased | |
| School Rush | Mon-Fri | | | Modified | Exam Week |
| Evening Chai | ✓ | | | | |
| Geyser | ✓ | | | | Weather |
| Evening Aarti | ✓ | | | | |
| Deep Cleaning | | ✓ | | Pre-festival | Guest |
| Laundry | | ✓ | | | Weather |
| Tuition | | 3x | | | Exam Off |
| Power Cut | | | | | When cut |
| Exam Mode | | | | | Exam week |
| Guest Prep | | | | | Guest +6h |
| Festival Prep | | | | Annual | |
| Night Wind-Down | ✓ | | | | |

---

## Regional Routine Variations

| Region | Unique Routines | Notes |
|---|---|---|
| Maharashtra | Ganesh puja, fish market early AM | Pune, Mumbai |
| South India | Oil bath Saturdays, different festival timings | Tamil Nadu, Karnataka |
| North India | Puja room facing east, different festival months | Delhi, UP |
| Gujarat | Uttarayan kite festival (Jan), business community routines | |
| Bengal | Durga Puja as primary festival, fish market AM | |
| Punjab | Gurpurab celebrations, langar visits | |
