"use client";

import { cn } from "@/lib/utils";
import {
  ROUTINE_PROFILE,
  NEXT_HOUR_PREDICTIONS,
  POWER_CUT_INTEL,
  FAMILY_ROLES,
  ENERGY_INSIGHTS,
  SAFETY_ALERTS,
  MEMORY_TIMELINE,
  CULTURAL_CONTEXT,
  COMPARISON_DATA,
} from "@/lib/intelligence-data";

// ═══════════════════════════════════════════════════════════════════
// 1. ROUTINE PROFILE CARD
// ═══════════════════════════════════════════════════════════════════

export function RoutineProfileCard() {
  return (
    <div className="glass rounded-xl p-4">
      <h3 className="text-xs font-semibold text-white/70 mb-3 flex items-center gap-2">
        📋 Learned Routine Profile
        <span className="ml-auto text-[9px] text-emerald-400 font-normal">{ROUTINE_PROFILE.length} patterns detected</span>
      </h3>
      <div className="space-y-1.5 max-h-[220px] overflow-y-auto pr-1">
        {ROUTINE_PROFILE.map((r, i) => (
          <div key={i} className="flex items-center gap-2 py-1 border-b border-white/[0.03] last:border-0">
            <span className="text-[10px] font-mono text-muted-foreground w-12 flex-shrink-0">{r.time}</span>
            <span className="text-[10px] text-white/80 flex-1 truncate">{r.activity}</span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-white/[0.05] text-muted-foreground">{r.dayType}</span>
            <span className={cn("text-[10px] font-mono font-bold", r.confidence >= 0.9 ? "text-emerald-400" : r.confidence >= 0.8 ? "text-blue-400" : "text-yellow-400")}>
              {Math.round(r.confidence * 100)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// 2. NEXT HOUR PREDICTION CARD
// ═══════════════════════════════════════════════════════════════════

export function NextHourPredictionCard() {
  return (
    <div className="glass rounded-xl p-4">
      <h3 className="text-xs font-semibold text-white/70 mb-3 flex items-center gap-2">
        <span className="w-1.5 h-1.5 rounded-full bg-saffron-400 animate-pulse" />
        Next 1 Hour — Predicted Actions
      </h3>
      <div className="space-y-2.5">
        {NEXT_HOUR_PREDICTIONS.map((p, i) => (
          <div key={i} className="bg-white/[0.03] rounded-lg p-2.5 border border-white/[0.05]">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <p className="text-[11px] font-medium text-white/90">{p.action}</p>
                <p className="text-[9px] text-muted-foreground mt-0.5">{p.timeframe}</p>
              </div>
              <span className={cn("text-[10px] font-mono font-bold", p.confidence >= 0.9 ? "text-emerald-400" : "text-blue-400")}>
                {Math.round(p.confidence * 100)}%
              </span>
            </div>
            <p className="text-[9px] text-muted-foreground/80 mt-1.5 italic">Reason: {p.explanation}</p>
            <p className="text-[9px] text-saffron-400/80 mt-1">→ {p.suggestedAction}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// 3. POWER CUT INTELLIGENCE CARD
// ═══════════════════════════════════════════════════════════════════

export function PowerCutIntelCard() {
  const p = POWER_CUT_INTEL;
  const riskColor = p.riskLevel === "high" ? "text-red-400 bg-red-500/10 border-red-500/30" : p.riskLevel === "medium" ? "text-orange-400 bg-orange-500/10 border-orange-500/30" : "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";

  return (
    <div className="glass rounded-xl p-4">
      <h3 className="text-xs font-semibold text-white/70 mb-3">⚡ Power Cut Intelligence</h3>
      <div className={cn("inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase border mb-3", riskColor)}>
        Risk: {p.riskLevel} — {p.probability}% probability at {p.expectedTime}
      </div>
      <p className="text-[9px] text-muted-foreground mb-2">Duration: {p.expectedDuration} • Pattern: {p.pattern}</p>

      <div className="mb-3">
        <p className="text-[9px] font-semibold text-white/50 uppercase mb-1">Affected Activities</p>
        <div className="space-y-0.5">
          {p.affectedActivities.map((a, i) => (
            <p key={i} className="text-[9px] text-orange-300/70">• {a}</p>
          ))}
        </div>
      </div>

      <div>
        <p className="text-[9px] font-semibold text-white/50 uppercase mb-1">Recommended Actions</p>
        <div className="space-y-1">
          {p.recommendations.slice(0, 4).map((r, i) => (
            <div key={i} className="flex items-start gap-1.5">
              <span className={cn("text-[8px] px-1 py-0.5 rounded uppercase font-bold mt-0.5", r.priority === "high" ? "bg-red-500/20 text-red-400" : r.priority === "medium" ? "bg-orange-500/20 text-orange-400" : "bg-slate-500/20 text-slate-400")}>{r.priority}</span>
              <p className="text-[9px] text-white/70">{r.action}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// 5. ROLE RECOGNITION PANEL
// ═══════════════════════════════════════════════════════════════════

export function RoleRecognitionPanel() {
  return (
    <div className="glass rounded-xl p-4">
      <h3 className="text-xs font-semibold text-white/70 mb-3">👥 Household Role Recognition</h3>
      <div className="grid grid-cols-2 gap-2">
        {FAMILY_ROLES.map((m, i) => (
          <div key={i} className="bg-white/[0.03] rounded-lg p-2.5 border border-white/[0.04]">
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-sm">{m.icon}</span>
              <div>
                <p className="text-[10px] font-medium text-white/90">{m.name}</p>
                <p className="text-[8px] text-saffron-400 uppercase font-bold">{m.role}</p>
              </div>
            </div>
            <div className="space-y-0.5">
              {m.personalizedSuggestions.slice(0, 2).map((s, j) => (
                <p key={j} className="text-[8px] text-muted-foreground leading-tight">• {s}</p>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// 6. ENERGY OPTIMIZATION CARD
// ═══════════════════════════════════════════════════════════════════

export function EnergyOptimizationCard() {
  const e = ENERGY_INSIGHTS;
  return (
    <div className="glass rounded-xl p-4">
      <h3 className="text-xs font-semibold text-white/70 mb-3 flex items-center gap-2">
        🔋 Energy Optimization
        <span className="ml-auto text-[10px] text-emerald-400 font-bold">↓ {e.estimatedSavings}% potential savings</span>
      </h3>
      <div className="mb-3">
        <p className="text-[9px] font-semibold text-white/50 uppercase mb-1">Top Energy Consumers</p>
        {e.topConsumers.slice(0, 3).map((c, i) => (
          <div key={i} className="flex items-center gap-2 py-1 border-b border-white/[0.03]">
            <span className="text-[9px] text-white/70 flex-1">{c.appliance}</span>
            <span className="text-[8px] text-muted-foreground">{c.usage}</span>
          </div>
        ))}
      </div>
      <div>
        <p className="text-[9px] font-semibold text-white/50 uppercase mb-1">Recommendations</p>
        {e.recommendations.slice(0, 3).map((r, i) => (
          <p key={i} className="text-[8px] text-emerald-300/70 mb-0.5">→ {r}</p>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// 7. SAFETY MONITORING PANEL
// ═══════════════════════════════════════════════════════════════════

export function SafetyAlertsPanel() {
  return (
    <div className="glass rounded-xl p-4">
      <h3 className="text-xs font-semibold text-white/70 mb-3 flex items-center gap-2">
        🛡️ Safety Monitoring
        <span className="ml-auto text-[9px] text-emerald-400">All systems nominal</span>
      </h3>
      <div className="space-y-2">
        {SAFETY_ALERTS.map((a) => (
          <div key={a.id} className="flex items-start gap-2 py-1.5 border-b border-white/[0.03]">
            <span className={cn("text-[8px] px-1.5 py-0.5 rounded uppercase font-bold mt-0.5",
              a.severity === "critical" ? "bg-red-500/20 text-red-400" :
              a.severity === "high" ? "bg-orange-500/20 text-orange-400" :
              a.severity === "medium" ? "bg-yellow-500/20 text-yellow-400" :
              "bg-slate-500/20 text-slate-400"
            )}>{a.severity}</span>
            <div className="flex-1">
              <p className="text-[9px] text-white/80">{a.appliance}: {a.reason}</p>
              <p className="text-[8px] text-muted-foreground mt-0.5">→ {a.action}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// 8. 7-DAY MEMORY TIMELINE
// ═══════════════════════════════════════════════════════════════════

export function MemoryTimelinePanel() {
  return (
    <div className="glass rounded-xl p-4">
      <h3 className="text-xs font-semibold text-white/70 mb-3">🧠 7-Day Household Memory</h3>
      <div className="space-y-2 max-h-[200px] overflow-y-auto pr-1">
        {MEMORY_TIMELINE.map((d, i) => (
          <div key={i} className="flex gap-3 py-1.5 border-b border-white/[0.03] last:border-0">
            <div className="w-16 flex-shrink-0">
              <p className="text-[9px] font-medium text-white/80">{d.day}</p>
              <div className="flex items-center gap-1 mt-0.5">
                <div className="h-1 flex-1 rounded-full bg-white/[0.1] overflow-hidden">
                  <div className="h-full rounded-full bg-emerald-400/60" style={{ width: `${d.consistency}%` }} />
                </div>
                <span className="text-[8px] text-muted-foreground">{d.consistency}%</span>
              </div>
            </div>
            <div className="flex-1">
              <p className="text-[8px] text-saffron-400/80 mb-0.5">{d.highlight}</p>
              <p className="text-[8px] text-muted-foreground">{d.events.join(" • ")}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// 11. CULTURAL CONTEXT PANEL
// ═══════════════════════════════════════════════════════════════════

export function CulturalContextPanel() {
  const c = CULTURAL_CONTEXT;
  return (
    <div className="glass rounded-xl p-4 border border-amber-500/10">
      <h3 className="text-xs font-semibold text-white/70 mb-2 flex items-center gap-2">
        🪔 Cultural Context — {c.festivalName}
        <span className="ml-auto text-[9px] text-amber-400">{c.daysAway} days away</span>
      </h3>
      <p className="text-[8px] text-muted-foreground mb-2 italic">{c.significance}</p>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <p className="text-[8px] font-semibold text-white/50 uppercase mb-1">Preparations Needed</p>
          {c.preparations.slice(0, 3).map((p, i) => (
            <p key={i} className="text-[8px] text-amber-300/70 mb-0.5">• {p}</p>
          ))}
        </div>
        <div>
          <p className="text-[8px] font-semibold text-white/50 uppercase mb-1">Routine Adjustments</p>
          {c.routineAdjustments.slice(0, 3).map((r, i) => (
            <p key={i} className="text-[8px] text-white/60 mb-0.5">• {r}</p>
          ))}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// 14. WHY GHARMIND IS DIFFERENT
// ═══════════════════════════════════════════════════════════════════

export function WhyDifferentPanel() {
  const { traditional, gharmind } = COMPARISON_DATA;
  return (
    <div className="glass rounded-xl p-4">
      <h3 className="text-xs font-semibold text-white/70 mb-3">🏆 Why GharMind AI is Different</h3>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <p className="text-[8px] font-bold text-red-400/80 uppercase mb-1.5">Traditional Smart Home</p>
          {traditional.map((t, i) => (
            <div key={i} className="mb-1">
              <p className="text-[8px] text-muted-foreground">{t.feature}</p>
              <p className="text-[9px] text-white/50">{t.value}</p>
            </div>
          ))}
        </div>
        <div>
          <p className="text-[8px] font-bold text-emerald-400/80 uppercase mb-1.5">GharMind AI</p>
          {gharmind.map((g, i) => (
            <div key={i} className="mb-1">
              <p className="text-[8px] text-muted-foreground">{g.feature}</p>
              <p className="text-[9px] text-emerald-300/80">{g.value}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
