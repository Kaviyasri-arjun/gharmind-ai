/**
 * GHARMIND AI — Intelligence Module Mock Data
 * All 14 intelligence modules: Routine Learning, Predictions, Power Cut,
 * Energy, Roles, Safety, Cultural Context, Memory Timeline, etc.
 */

// ── 1. Routine Learning Engine ────────────────────────────────────────

export const ROUTINE_PROFILE = [
  { time: "05:30", activity: "Paati wakes, begins morning prayers", type: "spiritual", frequency: "daily", dayType: "all", confidence: 0.96, explanation: "Observed on 27 of the last 28 days. Consistent early morning pattern." },
  { time: "06:00", activity: "Morning pooja by Lakshmi", type: "spiritual", frequency: "daily", dayType: "weekday", confidence: 0.94, explanation: "Weekday pooja at 6:00 AM confirmed on 13 of last 14 weekdays." },
  { time: "06:15", activity: "Water motor operation", type: "appliance", frequency: "daily", dayType: "weekday", confidence: 0.91, explanation: "Motor runs within 06:10–06:25 window on 12 of last 14 weekdays. Aligned with CMWSSB supply." },
  { time: "09:00", activity: "Venkat departs for office", type: "commute", frequency: "weekly", dayType: "weekday", confidence: 0.94, explanation: "Office departure between 08:50–09:10 on all 5 weekdays for past 3 weeks." },
  { time: "14:00", activity: "Power outage window (TNEB pattern)", type: "infrastructure", frequency: "weekly", dayType: "weekday", confidence: 0.76, explanation: "Load shedding at 2:00 PM confirmed on 5 of last 7 Thursdays for this zone." },
  { time: "17:00", activity: "Evening filter coffee preparation", type: "meal", frequency: "daily", dayType: "all", confidence: 0.88, explanation: "Coffee preparation detected between 16:50–17:10 on 25 of last 28 days." },
  { time: "18:00", activity: "Arjun tuition class", type: "education", frequency: "weekly", dayType: "weekday", confidence: 0.86, explanation: "Tuition attendance on Mon/Wed/Thu/Fri for past 4 weeks. Consistent pattern." },
  { time: "20:00", activity: "Exam quiet mode enforced", type: "study", frequency: "daily", dayType: "weekday", confidence: 0.92, explanation: "Quiet mode activated 8:00–10:00 PM on weekdays during exam weeks. Current exam week active." },
  { time: "22:00", activity: "Household wind-down", type: "sleep", frequency: "daily", dayType: "all", confidence: 0.89, explanation: "Lights dimmed and TV off between 21:45–22:15 on 24 of last 28 days." },
];

// ── 2. Context-Aware Next-Hour Predictions ────────────────────────────

export const NEXT_HOUR_PREDICTIONS = [
  { action: "Run water motor", confidence: 0.96, timeframe: "Within 7 minutes", explanation: "Tank at 42%. CMWSSB supply window active until 6:45 AM. Historical pattern confirms motor run at this time.", suggestedAction: "Start the water motor immediately to fill the tank before the supply window closes." },
  { action: "Breakfast preparation begins", confidence: 0.88, timeframe: "Within 22 minutes", explanation: "Lakshmi typically begins breakfast prep 20–30 minutes after pooja. Pooja started at 6:00 AM today.", suggestedAction: "Kitchen will be occupied shortly. Delay any loud activities near the kitchen area." },
  { action: "Arjun prepares for school", confidence: 0.91, timeframe: "Within 35 minutes", explanation: "School day confirmed. Bus departure at 8:00 AM. Uniform and bag check typically at 7:15 AM.", suggestedAction: "Ensure Arjun's school bag is packed and uniform is ready." },
];

// ── 3. Power Cut Intelligence ─────────────────────────────────────────

export const POWER_CUT_INTEL = {
  riskLevel: "high" as "low" | "medium" | "high",
  probability: 76,
  expectedTime: "2:00 PM",
  expectedDuration: "60–90 minutes",
  pattern: "TNEB Thursday load shedding pattern for Zone C2, R.S. Puram",
  historicalConfirmation: "5 of last 7 Thursdays had outage at this time",
  affectedActivities: [
    "Arjun's online study session (WiFi dependent)",
    "Lakshmi's mixer/grinder usage for evening snacks",
    "Ceiling fan in study room (comfort for Arjun)",
    "WiFi router (connectivity for all devices)",
  ],
  recommendations: [
    { action: "Charge all laptops, phones, and tablets to 100% by 1:30 PM", priority: "high" },
    { action: "Download study materials for offline access before 1:00 PM", priority: "high" },
    { action: "Run water motor before 1:45 PM (motor cannot operate during outage)", priority: "medium" },
    { action: "Switch off non-critical appliances to reduce load on UPS backup", priority: "medium" },
    { action: "Prepare snacks before 1:30 PM (mixer will be unavailable)", priority: "low" },
    { action: "Inform Venkat to save work and avoid video calls at 2:00 PM", priority: "medium" },
  ],
};

// ── 4. Enhanced Gharji Quick Actions ──────────────────────────────────

export const GHARJI_QUICK_ACTIONS = [
  { id: "predict", label: "Predict Today", icon: "🔮", response: "Today's key predictions: Water motor should run by 6:15 AM (96% confidence). A power outage is expected at 2:00 PM (76% confidence). Exam quiet mode will activate at 8:00 PM. Evening coffee is scheduled for 5:00 PM. All routines are on track." },
  { id: "energy", label: "Energy Report", icon: "⚡", response: "Current energy status: Total household consumption is moderate. Water motor accounts for 35% of morning peak usage. Recommendation: Delay washing machine operation to after 3:30 PM when power is restored. Estimated savings: 12% by shifting high-power appliances to off-peak hours." },
  { id: "status", label: "Home Status", icon: "🏠", response: "Household status: All 4 members are home. Paati is in the pooja room. Lakshmi is in the kitchen preparing breakfast. Venkat is getting ready for office departure at 9:00 AM. Arjun is studying in his room. Water tank is at 42% — motor should run now. No safety alerts active." },
  { id: "power", label: "Power Risk", icon: "🔋", response: "Power cut intelligence: There is a 76% probability of a power outage at 2:00 PM today based on TNEB Thursday patterns for Zone C2. Expected duration: 60–90 minutes. Key actions: Charge all devices by 1:30 PM, download offline study materials, and run the water motor before 1:45 PM." },
  { id: "routine", label: "Routine Profile", icon: "📋", response: "Today's routine profile: 9 routines identified with average confidence of 89%. Most consistent: Water motor (91%), Morning pooja (94%), Venkat office departure (94%). Most variable: Arjun tuition (86% — sometimes cancelled). Exam quiet mode is active tonight (92% confidence)." },
  { id: "safety", label: "Safety Alerts", icon: "🛡️", response: "Safety status: No critical alerts. One advisory: The water motor has been running for its standard duration — auto-shutoff will activate in 5 minutes. Geyser is operating within normal parameters. No appliance anomalies detected. All systems nominal." },
];

// ── 5. Household Role Recognition ─────────────────────────────────────

export const FAMILY_ROLES = [
  { name: "Lakshmi", role: "Homemaker", icon: "👩‍🍳", traits: ["Manages kitchen routines", "Coordinates family schedules", "Handles water and cooking operations"], personalizedSuggestions: ["Run water motor before 6:45 AM supply window closes", "Begin evening snack prep before 1:30 PM (power cut at 2:00 PM)", "Festival preparation: Check pooja supplies for Pongal next week"] },
  { name: "Venkat", role: "Working Professional", icon: "💼", traits: ["Fixed weekday commute pattern", "Office hours 9 AM–6 PM", "Requires device charging"], personalizedSuggestions: ["Depart by 9:00 AM to avoid peak traffic", "Charge laptop fully before leaving (power cut risk at 2 PM)", "Save all important work before 1:45 PM today"] },
  { name: "Arjun", role: "Student", icon: "🎓", traits: ["Board exam preparation active", "Tuition 4 days/week", "Requires quiet study environment"], personalizedSuggestions: ["Download all study PDFs before 1:00 PM (offline access needed)", "Quiet mode will be enforced from 8:00 PM tonight", "Charge laptop to 100% before the expected power outage"] },
  { name: "Paati", role: "Elderly Family Member", icon: "👵", traits: ["Early morning pooja routine", "Afternoon rest period", "Temple visits Tuesday/Friday"], personalizedSuggestions: ["Morning pooja room will be ready by 5:30 AM", "Afternoon rest period: minimize household noise 1:00–3:00 PM", "Ceiling fan backup available via UPS during power outage"] },
];

// ── 6. Energy Optimization ────────────────────────────────────────────

export const ENERGY_INSIGHTS = {
  estimatedSavings: 14,
  currentLoad: "Moderate",
  peakHours: "6:00–7:00 AM, 6:00–8:00 PM",
  topConsumers: [
    { appliance: "Water Motor", usage: "35% of morning peak", recommendation: "Run once daily during supply window only" },
    { appliance: "Geyser", usage: "22% of morning peak", recommendation: "Limit to 15 minutes. Consider solar water heating." },
    { appliance: "Ceiling Fan (Study Room)", usage: "18% of daily base", recommendation: "Switch to low speed during mild weather" },
    { appliance: "Television", usage: "12% of evening peak", recommendation: "Turn off during exam quiet hours (saves 45 minutes daily)" },
  ],
  recommendations: [
    "Shift washing machine usage to 3:30 PM (after power restoration, off-peak rates)",
    "Reduce geyser duration from 20 minutes to 15 minutes (sufficient for current season)",
    "Turn off WiFi router during confirmed sleep hours (11 PM – 5 AM) — saves 6 hours daily",
    "Use natural ventilation in mornings instead of ceiling fan before 8:00 AM",
  ],
};

// ── 7. Safety Monitoring ──────────────────────────────────────────────

export const SAFETY_ALERTS = [
  { id: "s1", severity: "low" as const, appliance: "Water Motor", reason: "Running for 23 minutes (normal cycle is 25 minutes). Auto-shutoff scheduled.", action: "No action required. Motor will stop automatically.", timestamp: "06:15 AM" },
  { id: "s2", severity: "medium" as const, appliance: "Geyser", reason: "Operating for 18 minutes. Typical duration is 15 minutes for current season.", action: "Consider turning off manually if not in use. Auto-shutoff at 20 minutes.", timestamp: "06:05 AM" },
  { id: "s3", severity: "low" as const, appliance: "UPS Battery", reason: "Battery at 85% charge. Sufficient for expected 90-minute power outage.", action: "No immediate action. Will fully charge before 2:00 PM.", timestamp: "Current" },
];

// ── 8. 7-Day Memory Timeline ──────────────────────────────────────────

export const MEMORY_TIMELINE = [
  { day: "Today", events: ["Motor 6:15 AM", "Pooja 6:00 AM", "Power cut expected 2 PM"], highlight: "Exam preparation day", consistency: 94 },
  { day: "Yesterday", events: ["Motor 6:12 AM", "Pooja 6:00 AM", "Tuition 6:00 PM", "Study 8–10 PM"], highlight: "Normal weekday", consistency: 96 },
  { day: "2 days ago", events: ["Motor 6:18 AM", "Pooja 6:00 AM", "Power cut 2:05–3:15 PM", "Coffee 5:00 PM"], highlight: "Power outage occurred", consistency: 88 },
  { day: "3 days ago", events: ["Motor 6:10 AM", "Pooja 6:00 AM", "Tuition 6:00 PM", "Study 8–10 PM"], highlight: "Normal weekday", consistency: 97 },
  { day: "4 days ago", events: ["Motor 6:20 AM", "Pooja 6:00 AM", "Guest visit 4–7 PM"], highlight: "Unexpected guest visit", consistency: 82 },
  { day: "5 days ago", events: ["Motor 6:14 AM", "Pooja 6:00 AM", "Tuition 6:00 PM", "Study 8–10 PM"], highlight: "Normal weekday", consistency: 95 },
  { day: "6 days ago", events: ["Motor 7:30 AM", "Pooja 6:30 AM", "Weekend leisure"], highlight: "Weekend — delayed routines", consistency: 78 },
];

// ── 11. Cultural Context ──────────────────────────────────────────────

export const CULTURAL_CONTEXT = {
  upcomingFestival: "Pongal",
  daysAway: 5,
  preparations: [
    "Purchase sugarcane and turmeric plants by Day 3",
    "Deep clean the house entrance for kolam display",
    "Prepare new clay pot for Pongal rice cooking",
    "Increase water storage — usage rises 40% during festival",
    "Plan guest meals — 70% probability of visitors on festival day",
  ],
  routineAdjustments: [
    "Morning pooja will extend to 45 minutes during Pongal week",
    "Kitchen activity increases 2x — plan water and power accordingly",
    "Arjun's study schedule may shift to early morning during celebrations",
    "Recommend charging all devices night before Pongal (heavy appliance use on festival day)",
  ],
  festivalName: "Pongal (Thai Pongal)",
  significance: "Harvest festival celebrating prosperity and gratitude. Four-day celebration with special cooking rituals.",
};

// ── 14. Why GharMind AI is Different ──────────────────────────────────

export const COMPARISON_DATA = {
  traditional: [
    { feature: "Interaction Model", value: "Command-based (voice or app)" },
    { feature: "Focus", value: "Individual device control" },
    { feature: "Intelligence", value: "Reactive — responds after request" },
    { feature: "Cultural Awareness", value: "None" },
    { feature: "Family Context", value: "None — treats all users identically" },
    { feature: "Prediction", value: "None — only reminders set manually" },
  ],
  gharmind: [
    { feature: "Interaction Model", value: "Autonomous anticipation — no commands needed" },
    { feature: "Focus", value: "Whole-household coordination" },
    { feature: "Intelligence", value: "Proactive — predicts and prepares ahead" },
    { feature: "Cultural Awareness", value: "Festival-aware, pooja-sensitive, season-adaptive" },
    { feature: "Family Context", value: "Role-aware — student, professional, homemaker, elderly" },
    { feature: "Prediction", value: "AI-powered with explainable confidence scores" },
  ],
};
