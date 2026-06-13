/**
 * GHARMIND AI — API Client
 * Connects to the FastAPI backend. Falls back to mock data if backend unavailable.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const HOUSEHOLD_ID = "a1b2c3d4-e5f6-7890-abcd-111111111111";

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${BASE_URL}${path}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: { "Content-Type": "application/json", ...options?.headers },
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
    return res.json();
  } catch {
    // Return mock data if backend is unreachable
    return getMockData(path) as T;
  }
}

export async function getHousehold() {
  return fetchAPI<any>(`/v1/households/${HOUSEHOLD_ID}`);
}

export async function getMembers() {
  return fetchAPI<any>(`/v1/households/${HOUSEHOLD_ID}/members`);
}

export async function getTwinState() {
  return fetchAPI<any>(`/v1/households/${HOUSEHOLD_ID}/twin/state`);
}

export async function getPredictions() {
  return fetchAPI<any>(`/v1/households/${HOUSEHOLD_ID}/predictions?horizon=today&limit=8`);
}

export async function getRoutines() {
  return fetchAPI<any>(`/v1/households/${HOUSEHOLD_ID}/routines`);
}

export async function sendChat(message: string) {
  return fetchAPI<any>(`/v1/households/${HOUSEHOLD_ID}/chat/message`, {
    method: "POST",
    body: JSON.stringify({ message, language: "en" }),
  });
}

export async function runSimulation(scenario: any) {
  return fetchAPI<any>(`/v1/households/${HOUSEHOLD_ID}/simulator/run`, {
    method: "POST",
    body: JSON.stringify(scenario),
  });
}

export async function getScenarios() {
  return fetchAPI<any>(`/v1/households/${HOUSEHOLD_ID}/simulator/scenarios`);
}

// ── Mock data (for offline/demo use without backend) ─────────────────

function getMockData(path: string): any {
  if (path.includes("/members")) return MOCK_MEMBERS;
  if (path.includes("/twin/state")) return MOCK_TWIN;
  if (path.includes("/predictions")) return MOCK_PREDICTIONS;
  if (path.includes("/routines")) return MOCK_ROUTINES;
  if (path.includes("/chat")) return MOCK_CHAT;
  if (path.includes("/simulator/scenarios")) return MOCK_SCENARIOS;
  if (path.includes("/simulator/run")) return MOCK_SIM_RESULT;
  if (path.includes("/households/")) return MOCK_HOUSEHOLD;
  return {};
}

const MOCK_HOUSEHOLD = {
  id: HOUSEHOLD_ID, name: "Sundaram Residence", city: "Coimbatore", state: "Tamil Nadu",
  ai_persona_name: "Gharji", language_preference: "en", twin_initialized: true,
  onboarding_complete: true, tags: ["nuclear_family", "has_students", "exam_week"],
  members_count: 4, rooms_count: 6, appliances_count: 6,
};

const MOCK_MEMBERS = {
  total: 4,
  members: [
    { id: "1", name: "Lakshmi", nickname: "Amma", role: "parent", age: 40, simulated_location: "kitchen", is_primary_contact: true },
    { id: "2", name: "Venkat", nickname: "Appa", role: "parent", age: 44, simulated_location: "master_bedroom", is_primary_contact: false },
    { id: "3", name: "Arjun", role: "child", age: 17, simulated_location: "study_room", is_primary_contact: false },
    { id: "4", name: "Paati", role: "grandparent", age: 68, simulated_location: "pooja_room", is_primary_contact: false },
  ],
};

const MOCK_TWIN = {
  household_id: HOUSEHOLD_ID, snapshot_at: new Date().toISOString(),
  temporal: { ist_time: "06:08:00", date: new Date().toISOString().split("T")[0], day_of_week: "Friday", season: "post_monsoon", phase_of_day: "early_morning", is_school_day: true },
  members: {
    "1": { name: "Lakshmi", location: "kitchen", activity: "breakfast_preparation", status: "home" },
    "2": { name: "Venkat", location: "master_bedroom", activity: "waking_up", status: "home" },
    "3": { name: "Arjun", location: "study_room", activity: "studying", status: "home" },
    "4": { name: "Paati", location: "pooja_room", activity: "morning_aarti", status: "home" },
  },
  resources: {
    power: { available: true, quality: "stable", cut_risk: "high", cut_probability: 0.76, cut_prediction: "14:00" },
    water: { available: true, tank_level_pct: 42, alert: "LOW — Water motor should be run soon", motor_running: false },
    internet: { available: true },
  },
  urgency_score: 62,
  context_summary: "Early Morning • Exam preparation active • Motor overdue • Power cut risk at 2 PM",
};

const MOCK_PREDICTIONS = {
  predictions: [
    { prediction_type: "appliance_action", title: "💧 Water Motor — Run at 6:15 AM", action_suggestion: "Run the water motor immediately. Tank is at 42% and the municipal supply window closes at 6:45 AM.", predicted_for: "2024-10-25T06:15:00+05:30", confidence: 0.96, priority: "critical", category: "water" },
    { prediction_type: "power_event", title: "⚡ Power Cut Expected — 2:00 PM", action_suggestion: "Charge all essential devices before the expected power outage. Ensure Arjun's laptop is fully charged.", predicted_for: "2024-10-25T14:00:00+05:30", confidence: 0.76, priority: "high", category: "power" },
    { prediction_type: "routine_start", title: "📚 Exam Quiet Mode — 8 PM", action_suggestion: "Enforce quiet hours from 8 PM. Television and loud appliances should be turned off.", predicted_for: "2024-10-25T20:00:00+05:30", confidence: 0.92, priority: "high", category: "study" },
    { prediction_type: "routine_start", title: "☕ Filter Coffee — 5:00 PM", action_suggestion: "Evening coffee preparation is scheduled for 5:00 PM. Lakshmi will prepare.", predicted_for: "2024-10-25T17:00:00+05:30", confidence: 0.93, priority: "normal", category: "routine" },
  ],
  summary: { critical_count: 1, high_count: 2, normal_count: 1, total: 4 },
};

const MOCK_ROUTINES = {
  total: 6,
  routines: [
    { id: "r1", name: "Morning Pooja", routine_type: "pooja", recurrence: "daily", is_active: true, confidence_score: 0.97, execution_count: 340 },
    { id: "r2", name: "Water Motor", routine_type: "motor", recurrence: "daily", is_active: true, confidence_score: 0.99, execution_count: 350 },
    { id: "r3", name: "Venkat Office Departure", routine_type: "commute", recurrence: "weekly", is_active: true, confidence_score: 0.94, execution_count: 220 },
    { id: "r4", name: "Evening Filter Coffee", routine_type: "chai", recurrence: "daily", is_active: true, confidence_score: 0.92, execution_count: 300 },
    { id: "r5", name: "Arjun Tuition", routine_type: "tuition", recurrence: "weekly", is_active: true, confidence_score: 0.88, execution_count: 160 },
    { id: "r6", name: "Arjun Night Study", routine_type: "study", recurrence: "daily", is_active: true, confidence_score: 0.85, execution_count: 90 },
  ],
};

const MOCK_CHAT = { message_id: "msg_demo", response: "Yes, Lakshmi. Please run the water motor now. The tank is at 42% and the CMWSSB supply window closes at 6:45 AM. Additionally, there is a 76% probability of a power cut at 2:00 PM today — I recommend filling the tank completely before then.", language: "en", household_context_used: true };

const MOCK_SCENARIOS = { scenarios: [
  { id: "s1", name: "Power Cut", icon: "⚡" }, { id: "s2", name: "Motor Failure", icon: "💧" },
  { id: "s3", name: "Unexpected Guests", icon: "👥" }, { id: "s4", name: "Exam Week", icon: "📚" },
]};

const MOCK_SIM_RESULT = {
  run_id: "sim-001", status: "complete", scenario_name: "Power Cut at 2 PM",
  result_summary: "A power outage at 2:00 PM will cause the WiFi router to lose connectivity, disrupting Arjun's online study session. All devices should be fully charged by 1:30 PM. Study materials should be downloaded for offline access before the outage begins.",
  overall_severity: "moderate",
  action_plan: [
    { time: "13:00", action: "Download all study materials for offline access" },
    { time: "13:30", action: "Fully charge all devices including Arjun's laptop and phone" },
    { time: "13:45", action: "Fill water bottles (motor cannot run during power outage)" },
    { time: "14:00", action: "Expected power outage — switch to textbook-based revision" },
    { time: "15:30", action: "Power expected to be restored — resume online study" },
  ],
  risk_flags: [
    { risk: "Laptop battery may deplete during extended study session", severity: "medium", mitigation: "Ensure full charge by 1:30 PM to guarantee 2.5 hours of backup" },
    { risk: "Room temperature may rise without fan or AC", severity: "low", mitigation: "Relocate to ground floor room with better ventilation" },
  ],
  cascade_chain: ["Power outage → WiFi router loses connectivity", "No internet → Online study materials become inaccessible", "No cooling → Elevated room temperature may affect concentration"],
};
