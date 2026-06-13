# GHARMIND AI — API Request/Response Examples
## Coimbatore Demo Household (Sundaram family)

**Base URL**: `http://localhost:8000`  
**Household ID**: `a1b2c3d4-e5f6-7890-abcd-111111111111`  
**Auth**: None required in dev (`SKIP_AUTH=true`)

---

## 1. Health Check

```
GET /system/health
```

**Response:**
```json
{
  "status": "healthy",
  "app": "GHARMIND AI",
  "version": "1.0.0",
  "env": "development",
  "database": "connected",
  "bedrock_mock": true,
  "skip_auth": true,
  "timestamp": 1719312000.0
}
```

---

## 2. Get Household Details

```
GET /v1/households/a1b2c3d4-e5f6-7890-abcd-111111111111
```

**Response:**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-111111111111",
  "name": "Sundaram Residence",
  "city": "Coimbatore",
  "state": "Tamil Nadu",
  "home_type": "independent",
  "ai_persona_name": "Gharji",
  "language_preference": "hinglish",
  "twin_initialized": true,
  "onboarding_complete": true,
  "subscription_tier": "pro",
  "tags": ["nuclear_family", "has_students", "working_father", "exam_week"],
  "members_count": 4,
  "rooms_count": 6,
  "appliances_count": 6,
  "created_at": "2024-10-25T06:00:00+05:30"
}
```

---

## 3. List Family Members

```
GET /v1/households/{id}/members
```

**Response:**
```json
{
  "total": 4,
  "members": [
    {
      "id": "...222201",
      "name": "Lakshmi",
      "nickname": "Amma",
      "role": "parent",
      "age": 40,
      "simulated_location": "kitchen",
      "is_primary_contact": true
    },
    {
      "id": "...222202",
      "name": "Venkat",
      "nickname": "Appa",
      "role": "parent",
      "age": 44,
      "simulated_location": "master_bedroom",
      "is_primary_contact": false
    },
    {
      "id": "...222203",
      "name": "Arjun",
      "role": "child",
      "age": 17,
      "simulated_location": "arjun_room",
      "is_primary_contact": false
    },
    {
      "id": "...222204",
      "name": "Paati",
      "role": "grandparent",
      "age": 68,
      "simulated_location": "pooja_room",
      "is_primary_contact": false
    }
  ]
}
```

---

## 4. Digital Twin State (Live)

```
GET /v1/households/{id}/twin/state
```

**Response:**
```json
{
  "household_id": "a1b2c3d4-...",
  "snapshot_at": "2024-10-25T06:08:00+05:30",
  "temporal": {
    "ist_time": "06:08:00",
    "date": "2024-10-25",
    "day_of_week": "Friday",
    "season": "post_monsoon",
    "phase_of_day": "early_morning",
    "is_school_day": true
  },
  "members": {
    "...222201": {"name": "Lakshmi", "location": "kitchen", "activity": "breakfast_preparation"},
    "...222204": {"name": "Paati", "location": "pooja_room", "activity": "morning_aarti"}
  },
  "appliances": {
    "...444401": {"name": "Water Motor", "type": "motor", "state": "off", "alert": "DUE IN 7 MIN"}
  },
  "resources": {
    "power": {"available": true, "quality": "stable", "cut_risk": "high", "cut_prediction": "14:00"},
    "water": {"available": true, "tank_level_pct": 42.0, "alert": "LOW — Run motor soon"},
    "internet": {"available": true}
  },
  "urgency_score": 55,
  "context_summary": "Early Morning • Post Monsoon • Water LOW — Run motor soon • Power cut risk at 14:00"
}
```

---

## 5. Prediction Feed

```
GET /v1/households/{id}/predictions?horizon=today&limit=5
```

**Response:**
```json
{
  "household_id": "a1b2c3d4-...",
  "generated_at": "2024-10-25T06:08:05+05:30",
  "horizon": "today",
  "predictions": [
    {
      "prediction_type": "appliance_action",
      "title": "💧 Water Motor — Run at 6:15 AM",
      "action_suggestion": "Motor 6:15 ku chalao — tank 42% irukku, school ku paani venum.",
      "predicted_for": "2024-10-25T06:15:00+05:30",
      "confidence": 0.96,
      "priority": "critical",
      "category": "water",
      "evidence": {"points": ["14 consecutive weekday runs", "Tank 42%", "CMWSSB supply window"]}
    },
    {
      "prediction_type": "power_event",
      "title": "⚡ TNEB Power Cut Expected — 2:00 PM",
      "action_suggestion": "2 PM power cut — devices charge pannu. Arjun laptop charge.",
      "predicted_for": "2024-10-25T14:00:00+05:30",
      "confidence": 0.76,
      "priority": "high",
      "category": "power"
    },
    {
      "prediction_type": "routine_start",
      "title": "📚 Exam Tomorrow — Quiet Mode Required",
      "action_suggestion": "Arjun exam naalaiku — TV 8 PM ku off pannu.",
      "predicted_for": "2024-10-25T20:00:00+05:30",
      "confidence": 0.92,
      "priority": "high",
      "category": "study"
    }
  ],
  "summary": {"critical_count": 1, "high_count": 2, "normal_count": 1, "total": 4}
}
```

---

## 6. Chat with Gharji

```
POST /v1/households/{id}/chat/message
Content-Type: application/json

{
  "message": "Motor chalana chahiye abhi?",
  "language": "hinglish"
}
```

**Response:**
```json
{
  "message_id": "msg_a1b2c3d4",
  "response": "Haan Lakshmi ji! Motor abhi chalao — tank 42% hai aur Arjun ko school jaana hai. CMWSSB supply window 6:45 tak hai, abhi start karo toh full bhar jayega. Aur ek baat — aaj 2 baje power cut ka chance hai, toh usse pehle paani bhar ke rakh lo.",
  "language": "hinglish",
  "household_context_used": true
}
```

---

## 7. What-If Simulation: Power Cut

```
POST /v1/households/{id}/simulator/run
Content-Type: application/json

{
  "scenario_name": "TNEB Power Cut During Arjun Study",
  "hypothesis": "What if power goes out at 2 PM while Arjun is preparing for exam?",
  "perturbations": [
    {"type": "power_cut", "params": {"start_time": "14:00", "duration_hours": 1.5}}
  ],
  "sim_duration_hours": 6
}
```

**Response:**
```json
{
  "run_id": "uuid-...",
  "status": "complete",
  "scenario_name": "TNEB Power Cut During Arjun Study",
  "result_summary": "Power cut at 2 PM will cause WiFi to drop and Arjun's laptop will run on battery (2.5hr capacity). Start charging all devices by 1:30 PM. Study session can continue with books during cut. Fan off — may need to move to cooler room.",
  "overall_severity": "moderate",
  "impact_analysis": {
    "disrupted_routines": [
      {
        "routine": "Arjun Study Session",
        "baseline_time": "14:00-16:00",
        "simulated_time": "14:00 laptop only, no wifi",
        "severity": "medium",
        "mitigation": "Download study materials by 1:30 PM"
      }
    ],
    "resource_impacts": [
      {"resource": "power", "projected_level_after": "Cut for 1.5 hours"},
      {"resource": "inverter_battery", "projected_level_after": "~40% after cut"}
    ],
    "cascade_chain": [
      "Power cut → WiFi off",
      "WiFi off → Online study materials inaccessible",
      "No fan → Arjun may lose focus in heat",
      "Inverter → limited to lights + 1 fan only"
    ]
  },
  "action_plan": [
    {"time": "13:00", "action": "Download all exam PDFs and videos offline"},
    {"time": "13:30", "action": "Charge laptop, phone, and tablet fully"},
    {"time": "13:45", "action": "Fill water bottles (motor won't run during cut)"},
    {"time": "14:00", "action": "Power cut — switch to book-based revision"},
    {"time": "14:30", "action": "Move Arjun to cooler room (tile floor) if needed"},
    {"time": "15:30", "action": "Power restored — resume online study"}
  ],
  "risk_flags": [
    {"risk": "Laptop battery dies mid-study", "severity": "medium", "mitigation": "Full charge by 1:30 PM ensures 2.5hr backup"},
    {"risk": "Heat causes discomfort/focus loss", "severity": "low", "mitigation": "Wet towel, move to ground floor"}
  ]
}
```

---

## 8. What-If: Unexpected Guests on Exam Eve

```
POST /v1/households/{id}/simulator/run
Content-Type: application/json

{
  "scenario_name": "Guests During Board Exam Eve",
  "hypothesis": "What if 6 relatives arrive at 5 PM the evening before Arjun's exam?",
  "perturbations": [
    {
      "type": "unexpected_guest",
      "params": {"count": 6, "arrival_time": "17:00", "duration_hours": 3, "includes_children": true}
    }
  ],
  "sim_duration_hours": 6
}
```

**Response:**
```json
{
  "run_id": "uuid-...",
  "status": "complete",
  "scenario_name": "Guests During Board Exam Eve",
  "result_summary": "6 guests arriving during exam prep evening will disrupt Arjun's critical study session. Children will create noise. Lakshmi will be occupied in kitchen. Solution: zone the house — Arjun stays in his room with door closed, guests in living room + hall.",
  "overall_severity": "significant",
  "action_plan": [
    {"time": "16:30", "action": "Alert family: guests coming, Arjun has exam"},
    {"time": "16:45", "action": "Move Arjun's study to upstairs room with door closed"},
    {"time": "17:00", "action": "Guests arrive — Venkat handles welcome"},
    {"time": "17:15", "action": "Lakshmi prepares filter coffee for guests"},
    {"time": "17:30", "action": "Children directed to hall/outdoor — NOT upstairs"},
    {"time": "19:00", "action": "Light dinner served to guests"},
    {"time": "20:00", "action": "Guests leave — Arjun resumes full study mode"}
  ],
  "risk_flags": [
    {"risk": "Children running upstairs disrupting Arjun", "severity": "high", "mitigation": "Lock upstairs door, provide toys in hall"},
    {"risk": "Lakshmi too busy to prepare Arjun's dinner", "severity": "medium", "mitigation": "Prepare Arjun's food at 4:30 PM before guests arrive"},
    {"risk": "Guests staying past 8 PM", "severity": "medium", "mitigation": "Venkat politely mentions exam next day at 7:30 PM"}
  ]
}
```

---

## 9. List Available Scenarios

```
GET /v1/households/{id}/simulator/scenarios
```

**Response:**
```json
{
  "scenarios": [
    {"id": "s001", "name": "Power Cut During Dinner", "icon": "⚡", "perturbation_types": ["power_cut"]},
    {"id": "s002", "name": "Water Motor Failure", "icon": "💧", "perturbation_types": ["motor_failure"]},
    {"id": "s003", "name": "Unexpected Guests", "icon": "👥", "perturbation_types": ["unexpected_guest"]},
    {"id": "s004", "name": "Exam Week Mode", "icon": "📚", "perturbation_types": ["exam_week"]},
    {"id": "s005", "name": "Festival Tomorrow", "icon": "🪔", "perturbation_types": ["festival_tomorrow"]},
    {"id": "s006", "name": "Internet Outage", "icon": "📡", "perturbation_types": ["internet_outage"]}
  ]
}
```

---

## 10. Create a Routine

```
POST /v1/households/{id}/routines
Content-Type: application/json

{
  "name": "Kolam Drawing (Rangoli)",
  "routine_type": "festival",
  "recurrence": "daily",
  "description": "Morning kolam at entrance — Tamil tradition",
  "schedule_expression": {"days": ["*"], "time": "05:45", "duration_mins": 15}
}
```

**Response:**
```json
{
  "id": "new-uuid",
  "name": "Kolam Drawing (Rangoli)",
  "routine_type": "festival",
  "recurrence": "daily",
  "is_active": true
}
```

---

## Demo Walkthrough Sequence

For the best demo experience, run these in order:

1. **Health check** — proves backend is alive
2. **Get household** — show the Coimbatore family context
3. **List members** — show Lakshmi, Venkat, Arjun, Paati with live locations
4. **Twin state** — 💥 hero moment: real-time household simulation, motor overdue alert
5. **Predictions** — 💥 second hero moment: AI predicted motor, power cut, exam quiet mode
6. **Chat "Motor chalana chahiye?"** — Gharji responds contextually in Hinglish
7. **Chat "Arjun ka exam kal hai"** — household adjustments suggested
8. **What-If: Power cut** — 💥 third hero moment: full cascade chain + action plan
9. **What-If: Guests on exam eve** — shows household zoning intelligence
10. **Scenario templates** — proves extensibility

**Total demo time**: ~4-5 minutes with narration between API calls.
