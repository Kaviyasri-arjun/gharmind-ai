# GHARMIND AI — Backend Demo Walkthrough
## Coimbatore Household: Sundaram Family

---

## Context: The Sundaram Family, R.S. Puram, Coimbatore

| Member | Role | Key Detail |
|---|---|---|
| **Lakshmi** (40) | Mother | Morning pooja 6 AM, manages household |
| **Venkat** (44) | Father | Office at 9 AM, drives to Tidel Park |
| **Arjun** (17) | Son | 12th Board exam TOMORROW (Physics) |
| **Paati** (68) | Grandmother | Early riser, temple visits Tue/Fri |

**Today's critical context:**
- Arjun's board exam is tomorrow morning at 10 AM
- Water motor runs at 6:15 AM (CMWSSB supply window)
- TNEB power cut expected around 2:00 PM (Thursday pattern)
- Evening chai at 5 PM
- Arjun's tuition at 6 PM — should he skip for exam prep?

---

## Setup (One-time)

```powershell
# 1. Start PostgreSQL
docker run --name gharmind-pg -e POSTGRES_DB=gharmind -e POSTGRES_USER=gharmind -e POSTGRES_PASSWORD=devpassword -p 5432:5432 -d pgvector/pgvector:pg16

# 2. Navigate to backend
cd c:\Users\Hp\OneDrive\Desktop\Gharmind-ai\backend

# 3. Install dependencies
pip install -e .
# OR: poetry install

# 4. Seed the database (creates tables + demo data)
python -m scripts.seed_coimbatore_demo

# 5. Start the backend
uvicorn app.main:app --reload
```

---

## Demo Flow (5 minutes)

### Minute 0:00 — "The System Comes Alive"

Open browser: `http://localhost:8000/docs`

Show the Swagger UI. Point out the route groups:
- `/v1/households` — Family management
- `/v1/households/{id}/twin` — Live Digital Twin
- `/v1/households/{id}/predictions` — AI prediction feed
- `/v1/households/{id}/chat` — Gharji conversational AI
- `/v1/households/{id}/simulator` — What-If engine

---

### Minute 0:30 — "Meet the Family"

```
GET /v1/households/a1b2c3d4-e5f6-7890-abcd-111111111111/members
```

**Talking point**: "Four family members — each with their own schedule, preferences, and simulated location. Arjun is in his room studying because his board exam is tomorrow. The AI knows this."

---

### Minute 1:00 — "The Digital Twin" (HERO MOMENT #1)

```
GET /v1/households/{id}/twin/state
```

**Talking point**: "This is a fully software-simulated household. No sensors. No IoT. Paati is in the pooja room — the system knows it's 6 AM and she rises at 4:30. The water motor alert says 'DUE IN 7 MINUTES' — it calculated this from 350 historical motor runs and today's tank level of 42%."

**Key visual**: Point to `urgency_score: 55` and the power cut prediction at 2 PM.

---

### Minute 1:45 — "Predictions That Think Ahead" (HERO MOMENT #2)

```
GET /v1/households/{id}/predictions?horizon=today
```

**Talking point**: "Three predictions, generated automatically:
1. CRITICAL: Run motor NOW (94% confidence, 14 historical data points)
2. HIGH: Power cut at 2 PM (TNEB pattern, 76% confidence)
3. HIGH: Exam quiet mode at 8 PM (calendar-aware, 92% confidence)

This is NOT a schedule. It's contextual intelligence. It combined the motor history, Coimbatore water supply window, exam calendar, AND the TNEB zone C2 Thursday pattern."

---

### Minute 2:30 — "Gharji Speaks" (HERO MOMENT #3)

```
POST /v1/households/{id}/chat/message
{"message": "Motor chalana chahiye abhi?"}
```

**Talking point**: "This is a live Claude 3 Sonnet call through AWS Bedrock. The system injected: household context, member locations, active predictions, and historical memories. Gharji responded in Hinglish because that's Lakshmi's preference."

**Follow-up chat:**
```
{"message": "Arjun ka exam kal hai, aaj ghar mein kya adjust karna chahiye?"}
```

**Expected response**: Full household adjustment plan — TV off by 8, no visitors, Lakshmi prepares exam-day meal tonight, quiet mode enforced.

---

### Minute 3:30 — "What-If Simulator" (HERO MOMENT #4)

```
POST /v1/households/{id}/simulator/run
{
  "scenario_name": "TNEB Power Cut During Arjun Study",
  "hypothesis": "Power cut at 2 PM during exam preparation",
  "perturbations": [{"type": "power_cut", "params": {"start_time": "14:00", "duration_hours": 1.5}}],
  "sim_duration_hours": 6
}
```

**Talking point**: "We just simulated the FUTURE. The engine:
1. Forked the twin state
2. Applied the power cut at 2 PM
3. Ran a 6-hour forward simulation
4. Traced the cascade: power off → WiFi drops → laptop on battery → can't access online materials → heat without fan
5. Generated an action plan: download materials by 1 PM, charge everything by 1:30, fill water before cut
6. All narrated by Claude in plain Hinglish."

---

### Minute 4:30 — "The Collision Scenario"

```
POST /v1/households/{id}/simulator/run
{
  "scenario_name": "Guests During Board Exam Eve",
  "hypothesis": "6 relatives arrive at 5 PM before Arjun's exam",
  "perturbations": [{"type": "unexpected_guest", "params": {"count": 6, "arrival_time": "17:00", "includes_children": true}}],
  "sim_duration_hours": 6
}
```

**Talking point**: "The AI found the collision: guests with children = NOISE, on the evening before a board exam. Its solution? Zone the house. Arjun upstairs, door closed. Children in hall with toys. Lakshmi preps Arjun's dinner BEFORE guests arrive. Venkat handles the welcome."

---

### Minute 5:00 — Close

**Talking point**: "Everything you just saw runs on:
- AWS Bedrock (Claude Sonnet + Titan Embeddings)
- PostgreSQL with pgvector (semantic memory)
- FastAPI (async, production-ready)
- ZERO hardware. Pure software intelligence.

This works for every Indian household — Coimbatore, Pune, Delhi, Bengaluru.
Each family gets their own Gharji. Their own Digital Twin. Their own predictions.
Built for Bharat."

---

## Quick Reference: All Endpoints for Demo

| # | Method | Endpoint | Purpose |
|---|---|---|---|
| 1 | GET | `/system/health` | Health check |
| 2 | GET | `/v1/households/{id}` | Household details |
| 3 | GET | `/v1/households/{id}/members` | Family list |
| 4 | GET | `/v1/households/{id}/twin/state` | Live twin state |
| 5 | GET | `/v1/households/{id}/predictions` | Prediction feed |
| 6 | GET | `/v1/households/{id}/routines` | Active routines |
| 7 | POST | `/v1/households/{id}/chat/message` | Chat with Gharji |
| 8 | POST | `/v1/households/{id}/simulator/run` | What-If simulation |
| 9 | GET | `/v1/households/{id}/simulator/scenarios` | Scenario templates |
| 10 | GET | `/v1/households/{id}/simulator/runs` | Past simulations |
