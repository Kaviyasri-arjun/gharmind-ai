/**
 * GHARMIND AI — Core TypeScript Type Definitions
 * Household, Members, Twin State, Predictions
 */

// ─── Household ────────────────────────────────────────────────────────────────

export interface Household {
  id: string
  name: string
  city: string
  state: string
  pincode?: string
  timezone: string
  language_preference: 'en' | 'hi' | 'hinglish'
  home_type: 'apartment' | 'villa' | 'row_house' | 'independent'
  floors: number
  ai_persona_name: string
  subscription_tier: 'free' | 'pro' | 'family'
  twin_initialized: boolean
  onboarding_complete: boolean
  tags: string[]
  created_at: string
}

export interface FamilyMember {
  id: string
  household_id: string
  name: string
  nickname?: string
  role: 'parent' | 'child' | 'grandparent' | 'help' | 'tenant'
  age?: number
  gender?: string
  work_schedule?: WorkSchedule
  school_schedule?: SchoolSchedule
  typical_wake_time?: string
  typical_sleep_time?: string
  is_primary_contact: boolean
  receives_alerts: boolean
  phone_number?: string
  preferences?: MemberPreferences
  simulated_location?: string
}

export interface WorkSchedule {
  type: 'office' | 'wfh' | 'hybrid' | 'business' | 'none'
  days: string[]
  start?: string
  end?: string
  wfh_days?: string[]
}

export interface SchoolSchedule {
  school_name: string
  bus_time: string
  return_time: string
  has_tuition: boolean
}

export interface MemberPreferences {
  chai_time?: string
  quiet_hours?: [string, string]
  language?: 'en' | 'hi' | 'hinglish'
}


// ─── Rooms & Appliances ───────────────────────────────────────────────────────

export interface Room {
  id: string
  household_id: string
  name: string
  room_type: RoomType
  floor: number
  area_sqft?: number
  position_x?: number
  position_y?: number
}

export type RoomType =
  | 'bedroom'
  | 'kitchen'
  | 'bathroom'
  | 'pooja_room'
  | 'study'
  | 'living_room'
  | 'balcony'
  | 'garage'
  | 'dining'

export interface Appliance {
  id: string
  household_id: string
  room_id?: string
  name: string
  appliance_type: ApplianceType
  brand?: string
  is_critical: boolean
  auto_schedule?: ApplianceSchedule
}

export type ApplianceType =
  | 'motor'
  | 'geyser'
  | 'fan'
  | 'ac'
  | 'tv'
  | 'fridge'
  | 'washing_machine'
  | 'wifi'
  | 'gas_stove'
  | 'chimney'
  | 'inverter'

export interface ApplianceSchedule {
  on: string
  off?: string
  days: string[]
  auto_off_after_mins?: number
}


// ─── Twin State ───────────────────────────────────────────────────────────────

export interface TwinStateSnapshot {
  household_id: string
  snapshot_at: string
  temporal: TemporalContext
  members: MemberState[]
  rooms: RoomState[]
  appliances: ApplianceState[]
  resources: ResourceStatus
  context_summary: string
  urgency_score: number
}

export interface TemporalContext {
  ist_time: string
  date: string
  day_of_week: string
  week_number: number
  month: number
  season: Season
  phase_of_day: PhaseOfDay
  festivals_active: string[]
  is_holiday: boolean
  is_school_day: boolean
  days_to_next_festival?: number
}

export type Season =
  | 'summer'
  | 'monsoon'
  | 'post_monsoon'
  | 'winter'
  | 'spring'
  | 'winter_onset'

export type PhaseOfDay =
  | 'brahma_muhurta'
  | 'early_morning'
  | 'morning_rush'
  | 'late_morning'
  | 'midday'
  | 'afternoon'
  | 'chai_time'
  | 'evening'
  | 'dinner_time'
  | 'night'
  | 'late_night'

export interface MemberState {
  id: string
  name: string
  location: string  // room name
  activity: string
  status: 'home' | 'away' | 'sleeping' | 'active'
}

export interface RoomState {
  id: string
  name: string
  room_type: RoomType
  is_occupied: boolean
  occupants: string[]  // member names
  lighting_state: 'off' | 'dim' | 'on' | 'auto'
  temperature_c?: number
}

export interface ApplianceState {
  id: string
  name: string
  appliance_type: ApplianceType
  state: 'off' | 'on' | 'standby' | 'error'
  power_watts?: number
  alert?: string
  last_on_at?: string
}

export interface ResourceStatus {
  power: {
    available: boolean
    quality: 'stable' | 'unstable' | 'cut'
    cut_risk: 'none' | 'low' | 'medium' | 'high'
    next_cut_prediction?: string
  }
  water: {
    available: boolean
    tank_level_pct: number
    supply_expected_at?: string
    alert?: string
  }
  internet: {
    available: boolean
    speed?: 'normal' | 'slow' | 'down'
  }
  gas?: {
    status: 'sufficient' | 'low' | 'empty'
  }
}


// ─── Household Status ─────────────────────────────────────────────────────────

export interface HouseholdStatus {
  household_id: string
  as_of: string
  urgency_score: number
  active_alerts: number
  pending_predictions: number
  twin_health: 'healthy' | 'degraded' | 'offline'
  summary: string
  household_mood: HouseholdMood
}

export type HouseholdMood =
  | 'calm'
  | 'active'
  | 'festive_preparation'
  | 'exam_mode'
  | 'guest_expected'
  | 'alert'
  | 'critical'
