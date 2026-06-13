/**
 * GHARMIND AI — Prediction & Simulation TypeScript Types
 */

// ─── Predictions ─────────────────────────────────────────────────────────────

export type PredictionType =
  | 'routine_start'
  | 'routine_overdue'
  | 'appliance_action'
  | 'member_arrival'
  | 'member_departure'
  | 'festival_prep'
  | 'power_event'
  | 'water_event'
  | 'meal_time'
  | 'study_reminder'
  | 'maintenance'

export type PredictionPriority = 'critical' | 'high' | 'normal' | 'low'

export type PredictionCategory =
  | 'water'
  | 'power'
  | 'routine'
  | 'family'
  | 'festival'
  | 'food'
  | 'study'
  | 'maintenance'

export type PredictionStatus = 'pending' | 'confirmed' | 'dismissed' | 'expired'

export interface Prediction {
  id: string
  household_id: string
  type: PredictionType
  title: string
  description: string
  action_suggestion: string
  predicted_for: string     // ISO datetime
  prediction_window: string // e.g., "30 minutes"
  confidence: number        // 0-1
  priority: PredictionPriority
  category: PredictionCategory
  status: PredictionStatus
  linked_routine_id?: string
  expires_at: string
  generated_at: string
}

export interface PredictionDetail extends Prediction {
  reasoning: string
  evidence: string[]
  context_snapshot_id?: string
}

export interface PredictionFeed {
  household_id: string
  generated_at: string
  predictions: Prediction[]
  summary: {
    critical_count: number
    high_count: number
    normal_count: number
    next_critical_at?: string
  }
}

export interface PredictionFeedback {
  prediction_id: string
  feedback: 'helpful' | 'not_helpful' | 'wrong'
  note?: string
}


// ─── Routines ─────────────────────────────────────────────────────────────────

export type RoutineType =
  | 'pooja'
  | 'motor'
  | 'tuition'
  | 'meal'
  | 'study'
  | 'chai'
  | 'cleaning'
  | 'exercise'
  | 'commute'
  | 'festival'
  | 'appliance'
  | 'sleep_prep'
  | 'conditional'
  | 'seasonal'

export interface Routine {
  id: string
  household_id: string
  name: string
  description?: string
  routine_type: RoutineType
  recurrence: 'daily' | 'weekly' | 'monthly' | 'annual' | 'conditional'
  schedule_expression: ScheduleExpression
  primary_member_id?: string
  participant_ids: string[]
  appliance_ids: string[]
  is_ai_detected: boolean
  confidence_score?: number
  is_active: boolean
  last_executed_at?: string
  next_expected_at?: string
  execution_count: number
  created_at: string
}

export interface ScheduleExpression {
  days: string[]        // ['mon','tue'] or ['*']
  time?: string         // '06:00'
  duration_mins?: number
  auto_off_after_mins?: number
  conditional?: string
}

export interface RoutineExecution {
  id: string
  routine_id: string
  household_id: string
  executed_at: string
  ended_at?: string
  duration_mins?: number
  was_predicted: boolean
  prediction_accuracy?: number
  deviation_mins: number
  execution_type: 'real' | 'simulated'
}


// ─── What-If Simulator ────────────────────────────────────────────────────────

export type PerturbationType =
  | 'power_cut'
  | 'water_shortage'
  | 'internet_outage'
  | 'unexpected_guest'
  | 'member_absent'
  | 'member_sick'
  | 'exam_week'
  | 'festival_tomorrow'
  | 'school_holiday'
  | 'motor_failure'
  | 'gas_cylinder_empty'

export interface Perturbation {
  type: PerturbationType
  params: Record<string, unknown>
}

export interface SimulationRunRequest {
  scenario_name: string
  hypothesis: string
  perturbations: Perturbation[]
  sim_start: string        // ISO datetime
  sim_duration_hours: number
}

export type SimulationSeverity = 'minimal' | 'moderate' | 'significant' | 'critical'

export interface RoutineImpact {
  routine: string
  baseline_time: string
  simulated_time: string
  deviation_mins: number
  impact_description: string
  severity: 'none' | 'low' | 'medium' | 'high' | 'critical'
  mitigation: string
}

export interface ResourceImpact {
  resource: string
  baseline_level: string
  projected_level_after: string
  concern?: string
}

export interface ActionPlanStep {
  time: string
  action: string
  urgency?: PredictionPriority
}

export interface RiskFlag {
  risk: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  mitigation: string
}

export interface SimulationResult {
  run_id: string
  status: 'running' | 'complete' | 'failed'
  scenario_name: string
  result_summary: string
  overall_severity: SimulationSeverity
  impact_analysis: {
    disrupted_routines: RoutineImpact[]
    resource_impacts: ResourceImpact[]
    cascade_chain: string[]
    member_impacts?: Array<{
      member: string
      impact: string
      severity: string
    }>
  }
  action_plan: ActionPlanStep[]
  risk_flags: RiskFlag[]
  completed_at?: string
}

export interface ScenarioTemplate {
  id: string
  name: string
  description: string
  icon: string
  perturbation_types: PerturbationType[]
  default_params?: Record<string, unknown>
}


// ─── Chat ─────────────────────────────────────────────────────────────────────

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  language: 'en' | 'hi' | 'hinglish'
  created_at: string
  referenced_predictions?: string[]
  context_used?: string[]
}

export interface ChatMessageRequest {
  message: string
  language?: 'en' | 'hi' | 'hinglish'
  context_include?: boolean
}

export interface ChatMessageResponse {
  message_id: string
  response: string
  language: string
  referenced_predictions: string[]
  context_used: string[]
}


// ─── Festivals & Calendar ─────────────────────────────────────────────────────

export interface Festival {
  id: string
  festival_name: string
  local_names: Record<string, string>
  festival_type: 'hindu' | 'muslim' | 'christian' | 'sikh' | 'national' | 'regional'
  region: string[]
  gregorian_date?: string
  household_impact: FestivalHouseholdImpact
  prep_days_before: number
  celebration_days: number
  is_public_holiday: boolean
  is_school_holiday: boolean
}

export interface FestivalHouseholdImpact {
  preparation_days: number
  peak_activity: string
  typical_routines: string[]
  water_usage_multiplier: number
  power_usage_multiplier: number
  sleep_shift_hours: number
  guest_probability?: number
}

export interface CalendarEvent {
  id: string
  household_id: string
  member_id?: string
  event_name: string
  event_type: 'exam' | 'tuition' | 'guest' | 'travel' | 'medical' | 'birthday' | 'other'
  start_at: string
  end_at?: string
  is_recurring: boolean
  impact_tags: string[]
  description?: string
}
