# GHARMIND AI — API Design
## REST + WebSocket API Specification

---

## Design Principles

1. **Resource-oriented**: Clean REST hierarchy following `/v1/{resource}/{id}/{sub-resource}`
2. **Household-scoped**: All resources belong to a household — enforced via JWT claim
3. **Real-time capable**: Critical live data delivered via WebSocket, not polling
4. **Consistent errors**: RFC 7807 problem detail format throughout
5. **IST-aware**: All timestamps returned in ISO 8601 with Asia/Kolkata timezone

---

## Base URL

```
Production:  https://api.gharmind.in/v1
Development: http://localhost:8000/v1
WebSocket:   wss://api.gharmind.in/ws
```

---

## Authentication

All API endpoints require a valid AWS Cognito JWT in the Authorization header:

```
Authorization: Bearer <cognito_access_token>
```

The JWT contains a `household_id` claim used for row-level security.

---

## API Resource Map

```
/v1
  /auth
    POST /register             → Register new user
    POST /login                → Login (Cognito)
    POST /refresh              → Refresh token

  /households
    POST   /                   → Create household
    GET    /{id}               → Get household details
    PATCH  /{id}               → Update household settings
    DELETE /{id}               → Delete household (soft)

    POST   /{id}/onboard       → Complete onboarding wizard
    GET    /{id}/status        → Household health/status summary

  /households/{id}/members
    GET    /                   → List family members
    POST   /                   → Add family member
    GET    /{member_id}        → Get member details
    PATCH  /{member_id}        → Update member
    DELETE /{member_id}        → Remove member

  /households/{id}/rooms
    GET    /                   → List rooms with current state
    POST   /                   → Add room
    PATCH  /{room_id}          → Update room
    DELETE /{room_id}          → Remove room

  /households/{id}/appliances
    GET    /                   → List appliances with state
    POST   /                   → Add appliance
    PATCH  /{appliance_id}     → Update appliance
    DELETE /{appliance_id}     → Remove appliance

  /households/{id}/twin
    GET    /state              → Current twin state snapshot
    GET    /history            → Historical snapshots (paginated)
    POST   /simulate-time      → Manually advance simulation
    GET    /occupancy          → Real-time room occupancy map
    GET    /resources          → Current resource status (water/power/internet)

  /households/{id}/routines
    GET    /                   → List all routines
    POST   /                   → Create routine
    GET    /{routine_id}       → Get routine details
    PATCH  /{routine_id}       → Update routine
    DELETE /{routine_id}       → Delete routine

    GET    /{routine_id}/executions  → Execution history
    GET    /upcoming           → Routines in next 24 hours
    GET    /overdue            → Currently overdue routines

  /households/{id}/predictions
    GET    /                   → Current prediction feed
    GET    /timeline           → 24-hour prediction timeline
    GET    /{prediction_id}    → Specific prediction with reasoning
    POST   /{prediction_id}/feedback  → Rate prediction (helpful/wrong)
    POST   /refresh            → Force regenerate predictions

  /households/{id}/simulator
    POST   /run                → Run a What-If simulation
    GET    /runs               → List past simulation runs
    GET    /runs/{run_id}      → Get simulation result
    GET    /scenarios          → List built-in scenario templates

  /households/{id}/chat
    POST   /message            → Send message to Gharji AI
    GET    /history            → Conversation history
    DELETE /history            → Clear conversation

  /households/{id}/insights
    GET    /weekly             → Weekly household insights
    GET    /patterns           → Detected routine patterns
    GET    /anomalies          → Recent anomalies
    GET    /festival-impact    → Upcoming festival impact analysis

  /households/{id}/calendar
    GET    /events             → Custom household events
    POST   /events             → Add custom event
    GET    /festivals          → Upcoming Indian festivals (30 days)

  /system
    GET    /health             → API health check
    GET    /version            → API version info

/ws
  /twin-stream/{household_id}  → WebSocket: live twin state stream
  /predictions/{household_id}  → WebSocket: real-time prediction alerts
```

---

## Key Endpoint Specifications

### GET /households/{id}/twin/state

Returns the current household Digital Twin state.

**Response:**
```json
{
  "household_id": "uuid",
  "snapshot_at": "2024-10-28T06:15:00+05:30",
  "temporal": {
    "ist_time": "06:15:00",
    "phase_of_day": "early_morning",
    "day_of_week": "Monday",
    "season": "winter_onset",
    "festivals_active": ["Diwali Prep Week"],
    "is_school_day": true,
    "days_to_next_festival": 4
  },
  "members": [
    {
      "id": "uuid",
      "name": "Anjali",
      "location": "pooja_room",
      "activity": "morning_pooja",
      "status": "home"
    }
  ],
  "rooms": [
    {
      "id": "uuid",
      "name": "Pooja Room",
      "room_type": "pooja_room",
      "is_occupied": true,
      "occupants": ["Anjali"],
      "lighting_state": "on"
    }
  ],
  "appliances": [
    {
      "id": "uuid",
      "name": "Water Motor",
      "state": "off",
      "alert": "overdue_15min",
      "last_run": "2024-10-27T17:45:00+05:30"
    }
  ],
  "resources": {
    "power": {"available": true, "quality": "stable", "cut_risk": "low"},
    "water": {"available": true, "tank_level_pct": 38, "alert": "low"},
    "internet": {"available": true}
  },
  "context_summary": "Festive Monday morning. Motor overdue. Pooja active.",
  "urgency_score": 72
}
```

---

### GET /households/{id}/predictions

Returns the active prediction feed, sorted by priority.

**Query params:**
- `horizon` — `30min` | `2h` | `today` | `week` (default: `2h`)
- `priority` — `critical` | `high` | `all` (default: `all`)
- `limit` — integer (default: 10, max: 50)

**Response:**
```json
{
  "household_id": "uuid",
  "generated_at": "2024-10-28T06:15:05+05:30",
  "predictions": [
    {
      "id": "uuid",
      "type": "routine_start",
      "title": "Water Motor — Run Now",
      "description": "Tank at 38%. School rush at 7:15am. Motor overdue by 15 minutes.",
      "action_suggestion": "Motor chalao abhi. Tank 38% hai, 7:15 tak school bus hai.",
      "predicted_for": "2024-10-28T06:15:00+05:30",
      "confidence": 0.94,
      "priority": "critical",
      "category": "water",
      "reasoning": "Historical: motor ran at 06:20 avg on Mondays. Tank below 40% threshold. Festival week: +25% water usage.",
      "expires_at": "2024-10-28T07:00:00+05:30"
    },
    {
      "id": "uuid",
      "type": "power_event",
      "title": "Load Shedding Expected at 7:30pm",
      "description": "MSEDCL pattern shows Monday evening cuts. Charge devices before 7pm.",
      "action_suggestion": "7 baje se pehle saare devices charge kar lo. Dinner 7:15 tak ready karo.",
      "predicted_for": "2024-10-28T19:30:00+05:30",
      "confidence": 0.79,
      "priority": "normal",
      "category": "power"
    }
  ],
  "summary": {
    "critical_count": 1,
    "high_count": 2,
    "normal_count": 5,
    "next_critical_at": "2024-10-28T06:15:00+05:30"
  }
}
```

---

### POST /households/{id}/simulator/run

Run a What-If simulation.

**Request:**
```json
{
  "scenario_name": "Power cut during Diwali dinner",
  "hypothesis": "What happens if power goes out at 7:30pm tonight?",
  "perturbations": [
    {
      "type": "power_cut",
      "params": {
        "start_time": "2024-10-28T19:30:00+05:30",
        "duration_hours": 1.5,
        "affects_inverter": false
      }
    }
  ],
  "sim_start": "2024-10-28T17:00:00+05:30",
  "sim_duration_hours": 6
}
```

**Response:**
```json
{
  "run_id": "uuid",
  "status": "complete",
  "scenario_name": "Power cut during Diwali dinner",
  "result_summary": "Agar aaj 7:30 baje light gayi, dinner 7:15 tak complete karna hoga. Diwali lights inverter pe chalenge — 3 ghante ka backup. Devices 7 baje tak charge kar lo.",
  "overall_severity": "significant",
  "impact_analysis": {
    "disrupted_routines": [
      {
        "routine": "Dinner Preparation",
        "baseline_time": "20:00",
        "simulated_time": "18:45",
        "severity": "high",
        "mitigation": "Start dinner at 6:45pm instead of 8pm"
      }
    ],
    "resource_impacts": [
      {
        "resource": "inverter_battery",
        "baseline_level": "100%",
        "projected_level_after": "35%",
        "concern": "If cut extends beyond 2 hours, inverter insufficient"
      }
    ],
    "cascade_chain": [
      "Power cut at 7:30pm",
      "→ WiFi off (Rahul's OTT streaming disrupted)",
      "→ Motor off (cannot fill tank overnight)",
      "→ Inverter: fans + essential lights only",
      "→ Cooking must complete before cut"
    ]
  },
  "action_plan": [
    {"time": "18:30", "action": "Start dinner preparation immediately"},
    {"time": "18:45", "action": "Charge all phones and tablets"},
    {"time": "19:00", "action": "Dinner must be served"},
    {"time": "19:25", "action": "Switch critical appliances to inverter"},
    {"time": "19:30", "action": "Expected power cut — household prepared"}
  ],
  "risk_flags": [
    {
      "risk": "Inverter capacity insufficient for extended cut",
      "severity": "medium",
      "mitigation": "Limit to 2 fans + LED lights only during cut"
    }
  ]
}
```

---

### POST /households/{id}/chat/message

Send a natural language message to Gharji (the household AI).

**Request:**
```json
{
  "message": "Motor chalana chahiye abhi?",
  "language": "hinglish",
  "context_include": true
}
```

**Response (streaming SSE):**
```json
{
  "message_id": "uuid",
  "response": "Haan, bilkul abhi chalao! Tank 38% hai aur school bus 7:15 par hai. Diwali week mein paani zyada lagta hai — abhi chalao toh kal subah tak full rahega.",
  "language": "hinglish",
  "referenced_predictions": ["uuid-motor-prediction"],
  "confidence": 0.95,
  "context_used": ["water_tank_level", "school_schedule", "festival_context"]
}
```

---

## WebSocket Streams

### WS /ws/twin-stream/{household_id}

Real-time twin state updates. Emits every time the twin state changes.

**Message format:**
```json
{
  "event_type": "state_update",
  "timestamp": "2024-10-28T06:16:00+05:30",
  "changes": [
    {
      "component": "appliance",
      "id": "water-motor-uuid",
      "field": "power_state",
      "old_value": "off",
      "new_value": "on",
      "triggered_by": "user_action"
    }
  ],
  "full_state": { ... }  // Optional, requested via query param
}
```

**Event types emitted:**
- `state_update` — Any household state change
- `routine_started` — A routine has begun
- `routine_completed` — A routine has ended
- `anomaly_detected` — Something unexpected happened
- `resource_alert` — Water/power/internet change
- `festival_event` — Festival phase change

### WS /ws/predictions/{household_id}

Real-time prediction alerts.

**Message format:**
```json
{
  "event_type": "new_prediction",
  "prediction": { ... },
  "urgency": "critical"
}
```

---

## Error Response Format (RFC 7807)

```json
{
  "type": "https://api.gharmind.in/errors/resource-not-found",
  "title": "Household not found",
  "status": 404,
  "detail": "No household found with ID: uuid-xyz",
  "instance": "/v1/households/uuid-xyz"
}
```

**Error types:**

| Code | Type | Description |
|---|---|---|
| 400 | `bad-request` | Invalid input or schema violation |
| 401 | `unauthorized` | Missing or invalid JWT |
| 403 | `forbidden` | JWT valid but accessing another household |
| 404 | `not-found` | Resource does not exist |
| 409 | `conflict` | Duplicate resource (name clash) |
| 422 | `validation-error` | Pydantic validation failure |
| 429 | `rate-limited` | Too many requests |
| 503 | `bedrock-unavailable` | AWS Bedrock service temporarily unavailable |

---

## Rate Limits

| Endpoint Group | Limit |
|---|---|
| `/twin/state` | 60 requests/minute |
| `/predictions` | 30 requests/minute |
| `/simulator/run` | 10 requests/minute |
| `/chat/message` | 20 requests/minute |
| WebSocket connections | 3 per household |

---

## API Versioning

- Current version: `v1`
- Version in URL path: `/v1/...`
- Breaking changes will introduce `/v2/...`
- Sunset headers used for deprecated endpoints
