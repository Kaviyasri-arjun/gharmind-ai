#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# GHARMIND AI — API Testing with cURL
# Coimbatore Demo Household (Sundaram family)
# ═══════════════════════════════════════════════════════════════════════════
#
# Prerequisites:
#   1. Backend running: uvicorn app.main:app --reload
#   2. Database seeded: python -m scripts.seed_coimbatore_demo
#
# NOTE: SKIP_AUTH=true is set — no auth token needed for local dev.
# ═══════════════════════════════════════════════════════════════════════════

BASE_URL="http://localhost:8000"
HOUSEHOLD_ID="a1b2c3d4-e5f6-7890-abcd-111111111111"

echo "═══════════════════════════════════════════════════"
echo "  GHARMIND AI — API Test Suite (cURL)"
echo "═══════════════════════════════════════════════════"
echo ""

# ─── 1. Health Check ─────────────────────────────────────────────────────
echo "1. Health Check"
echo "   GET /system/health"
curl -s $BASE_URL/system/health | python -m json.tool
echo ""
echo "---"

# ─── 2. Get Household ────────────────────────────────────────────────────
echo "2. Get Household (Sundaram Residence)"
echo "   GET /v1/households/$HOUSEHOLD_ID"
curl -s $BASE_URL/v1/households/$HOUSEHOLD_ID | python -m json.tool
echo ""
echo "---"

# ─── 3. List Family Members ──────────────────────────────────────────────
echo "3. List Family Members"
echo "   GET /v1/households/$HOUSEHOLD_ID/members"
curl -s $BASE_URL/v1/households/$HOUSEHOLD_ID/members | python -m json.tool
echo ""
echo "---"

# ─── 4. Get Twin State (Live) ────────────────────────────────────────────
echo "4. Get Live Digital Twin State"
echo "   GET /v1/households/$HOUSEHOLD_ID/twin/state"
curl -s $BASE_URL/v1/households/$HOUSEHOLD_ID/twin/state | python -m json.tool
echo ""
echo "---"

# ─── 5. Get Predictions ──────────────────────────────────────────────────
echo "5. Get Prediction Feed"
echo "   GET /v1/households/$HOUSEHOLD_ID/predictions"
curl -s "$BASE_URL/v1/households/$HOUSEHOLD_ID/predictions?horizon=today&limit=5" | python -m json.tool
echo ""
echo "---"

# ─── 6. List Routines ────────────────────────────────────────────────────
echo "6. List Active Routines"
echo "   GET /v1/households/$HOUSEHOLD_ID/routines"
curl -s $BASE_URL/v1/households/$HOUSEHOLD_ID/routines | python -m json.tool
echo ""
echo "---"

# ─── 7. Chat with Gharji ─────────────────────────────────────────────────
echo "7. Chat with Gharji (Hinglish)"
echo "   POST /v1/households/$HOUSEHOLD_ID/chat/message"
curl -s -X POST $BASE_URL/v1/households/$HOUSEHOLD_ID/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Motor chalana chahiye abhi?", "language": "hinglish"}' | python -m json.tool
echo ""
echo "---"

# ─── 8. Chat — Exam Context ──────────────────────────────────────────────
echo "8. Chat — Exam prep question"
echo "   POST /v1/households/$HOUSEHOLD_ID/chat/message"
curl -s -X POST $BASE_URL/v1/households/$HOUSEHOLD_ID/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Arjun ka exam kal hai, ghar mein kya adjust karna chahiye?"}' | python -m json.tool
echo ""
echo "---"

# ─── 9. What-If Simulation: Power Cut ────────────────────────────────────
echo "9. What-If Simulation: Power Cut at 2 PM"
echo "   POST /v1/households/$HOUSEHOLD_ID/simulator/run"
curl -s -X POST $BASE_URL/v1/households/$HOUSEHOLD_ID/simulator/run \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "TNEB Power Cut During Arjun Study",
    "hypothesis": "What if power goes out at 2 PM during Arjun exam prep?",
    "perturbations": [
      {"type": "power_cut", "params": {"start_time": "14:00", "duration_hours": 1.5}}
    ],
    "sim_duration_hours": 6
  }' | python -m json.tool
echo ""
echo "---"

# ─── 10. What-If: Exam + Guest Collision ─────────────────────────────────
echo "10. What-If: Unexpected guests during exam prep"
echo "    POST /v1/households/$HOUSEHOLD_ID/simulator/run"
curl -s -X POST $BASE_URL/v1/households/$HOUSEHOLD_ID/simulator/run \
  -H "Content-Type: application/json" \
  -d '{
    "scenario_name": "Guests During Board Exam Eve",
    "hypothesis": "What if 6 relatives arrive at 5 PM the evening before Arjun exam?",
    "perturbations": [
      {"type": "unexpected_guest", "params": {"count": 6, "arrival_time": "17:00", "duration_hours": 3, "includes_children": true}}
    ],
    "sim_duration_hours": 6
  }' | python -m json.tool
echo ""
echo "---"

# ─── 11. List Simulation Runs ────────────────────────────────────────────
echo "11. List Past Simulation Runs"
echo "    GET /v1/households/$HOUSEHOLD_ID/simulator/runs"
curl -s $BASE_URL/v1/households/$HOUSEHOLD_ID/simulator/runs | python -m json.tool
echo ""
echo "---"

# ─── 12. Get Scenario Templates ──────────────────────────────────────────
echo "12. Available What-If Scenario Templates"
echo "    GET /v1/households/$HOUSEHOLD_ID/simulator/scenarios"
curl -s $BASE_URL/v1/households/$HOUSEHOLD_ID/simulator/scenarios | python -m json.tool
echo ""
echo "---"

# ─── 13. Prediction Feedback ─────────────────────────────────────────────
echo "13. Submit Prediction Feedback (mock ID)"
echo "    POST /v1/households/$HOUSEHOLD_ID/predictions/{id}/feedback"
echo "    (Skipped — need actual prediction ID from step 5)"
echo ""

echo "═══════════════════════════════════════════════════"
echo "  ✅ All API tests complete!"
echo "═══════════════════════════════════════════════════"
