"""
GHARMIND AI — What-If Simulator Engine
Forks the Digital Twin state, applies perturbations, runs forward simulation,
analyzes impact, and generates Claude-powered narrative + action plan.
"""
from __future__ import annotations

import copy
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.logging_config import get_logger
from app.models.prediction import SimulationRun
from app.models.routine import Routine
from app.services.bedrock.claude_client import claude_client
from app.services.bedrock.prompts import build_whatif_messages

logger = get_logger(__name__)
IST = ZoneInfo("Asia/Kolkata")

# ── Cascade rules for each perturbation type ──────────────────────────

CASCADE_RULES: dict[str, list[dict[str, Any]]] = {
    "power_cut": [
        {"effect": "wifi_off", "description": "WiFi router loses power"},
        {"effect": "wfh_disruption", "condition": "work_hours AND wfh_member_home"},
        {"effect": "inverter_drain", "description": "Inverter backup begins"},
        {"effect": "motor_stops", "description": "Water motor cannot run"},
        {"effect": "fridge_risk", "trigger_after_hours": 2, "description": "Fridge temperature rises"},
        {"effect": "cooking_risk", "condition": "induction_only", "description": "Induction cooking fails"},
    ],
    "water_shortage": [
        {"effect": "motor_ineffective", "description": "Motor cannot fill tank"},
        {"effect": "morning_crisis", "condition": "tank_below_20_pct AND school_day"},
        {"effect": "laundry_postpone", "description": "Laundry must be deferred"},
        {"effect": "shower_limit", "description": "Shower time must be reduced"},
    ],
    "unexpected_guest": [
        {"effect": "kitchen_surge", "description": "Kitchen activity increases x1.8"},
        {"effect": "water_surge", "description": "Water usage increases x1.5"},
        {"effect": "study_disruption", "condition": "guests_include_children"},
        {"effect": "chai_extra", "description": "Extra chai rounds required"},
        {"effect": "snack_prep", "description": "Snack preparation needed"},
    ],
    "exam_week": [
        {"effect": "quiet_hours", "description": "Extended quiet hours (6am–11pm)"},
        {"effect": "tv_restricted", "description": "TV limited to 1 hour evening"},
        {"effect": "tuition_cancel", "description": "Home tuition visits cancelled"},
        {"effect": "study_schedule", "description": "Structured study sessions active"},
    ],
    "motor_failure": [
        {"effect": "tank_drain_only", "description": "No refill possible"},
        {"effect": "morning_crisis", "description": "Crisis if tank below 30%"},
        {"effect": "plumber_needed", "description": "Repair required"},
    ],
    "internet_outage": [
        {"effect": "wfh_disruption", "description": "WFH productivity lost"},
        {"effect": "mobile_data_fallback", "description": "Switch to mobile hotspot"},
        {"effect": "streaming_off", "description": "TV streaming unavailable"},
    ],
}

TICK_MINUTES = 15  # Forward simulation resolution


class WhatIfSimulator:
    """
    Runs forward household simulations for What-If scenario planning.
    All simulations run in memory — no writes to production DB during simulation.
    """

    async def run_simulation(
        self,
        db: AsyncSession,
        household_id: str,
        scenario_name: str,
        hypothesis: str,
        perturbations: list[dict[str, Any]],
        sim_start: datetime,
        sim_duration_hours: int,
        baseline_state: dict[str, Any],
        household_name: str,
        city: str,
        member_summary: str,
        language: str = "hinglish",
    ) -> dict[str, Any]:
        """
        Execute a What-If simulation.

        1. Fork the baseline twin state
        2. Apply perturbations
        3. Run forward simulation (15-min ticks)
        4. Analyze impact vs baseline
        5. Generate Claude narrative
        6. Persist simulation run
        7. Return full result
        """
        logger.info(
            "whatif_simulation_start",
            household_id=household_id,
            scenario=scenario_name,
            duration_hours=sim_duration_hours,
        )

        # Create DB record (status=running)
        sim_run = SimulationRun(
            household_id=UUID(household_id),
            scenario_name=scenario_name,
            scenario_type=self._infer_type(perturbations),
            hypothesis=hypothesis,
            perturbations={"perturbations": perturbations},
            sim_start_time=sim_start,
            sim_duration_hours=sim_duration_hours,
            sim_resolution_mins=TICK_MINUTES,
            status="running",
        )
        db.add(sim_run)
        await db.flush()
        run_id = str(sim_run.id)

        try:
            # ── 1. Fork baseline ────────────────────────────────────
            sim_state = copy.deepcopy(baseline_state)

            # ── 2. Apply perturbations ──────────────────────────────
            sim_state = self._apply_perturbations(sim_state, perturbations, sim_start)

            # ── 3. Forward simulation ───────────────────────────────
            timeline: list[dict[str, Any]] = []
            current_time = sim_start
            end_time = sim_start + timedelta(hours=sim_duration_hours)

            disruptions: list[str] = []
            disrupted_routines: list[dict[str, Any]] = []
            resource_impacts: list[dict[str, Any]] = []
            cascade_events: list[str] = []

            routines_result = await db.execute(
                select(Routine).where(
                    Routine.household_id == UUID(household_id),
                    Routine.is_active.is_(True),
                )
            )
            routines = routines_result.scalars().all()

            while current_time <= end_time:
                tick = self._advance_sim_tick(
                    sim_state,
                    current_time,
                    perturbations,
                    routines,
                )
                timeline.append({
                    "time": current_time.strftime("%H:%M"),
                    "events": tick["events"],
                    "anomalies": tick["anomalies"],
                })
                cascade_events.extend(tick.get("cascades", []))
                disruptions.extend(tick.get("disruptions", []))
                current_time += timedelta(minutes=TICK_MINUTES)

            # ── 4. Impact analysis ──────────────────────────────────
            disrupted_routines = self._analyze_routine_impact(
                routines, perturbations, sim_start, end_time, baseline_state
            )
            resource_impacts = self._analyze_resource_impact(
                perturbations, baseline_state, sim_duration_hours
            )
            cascade_chain = self._build_cascade_chain(perturbations, cascade_events)
            overall_severity = self._assess_severity(
                disrupted_routines, resource_impacts
            )

            # ── 5. Claude narrative ─────────────────────────────────
            system, messages = build_whatif_messages(
                household_name=household_name,
                city=city,
                language=language,
                member_summary=member_summary,
                baseline_summary=baseline_state.get("context_summary", "Normal household state"),
                scenario_description=hypothesis,
                perturbations={"perturbations": perturbations},
                timeline_events=[e for tick in timeline for e in tick["events"]],
                disrupted_routines=disrupted_routines,
                resource_impacts=resource_impacts,
                cascade_chain=cascade_chain,
            )

            try:
                claude_result = await claude_client.invoke_structured(
                    messages=messages,
                    system_prompt=system,
                    mock_key="whatif_simulation",
                )
            except Exception as e:
                logger.warning("claude_whatif_failed", error=str(e))
                claude_result = {
                    "result_summary": f"Simulation complete. {len(disrupted_routines)} routines affected.",
                    "action_plan": [],
                    "risk_flags": [],
                    "silver_lining": None,
                }

            # ── 6. Persist results ──────────────────────────────────
            impact_analysis = {
                "disrupted_routines": disrupted_routines,
                "resource_impacts": resource_impacts,
                "cascade_chain": cascade_chain,
                "member_impacts": [],
                "overall_severity": overall_severity,
            }

            sim_run.status = "complete"
            sim_run.result_summary = claude_result.get("result_summary", "")
            sim_run.impact_analysis = impact_analysis
            sim_run.risk_flags = {"flags": claude_result.get("risk_flags", [])}
            sim_run.recommendations = {"action_plan": claude_result.get("action_plan", [])}
            sim_run.timeline = {"ticks": timeline[:20]}  # Store first 20 ticks only
            sim_run.completed_at = datetime.now(IST)
            await db.commit()

            # ── 7. Return full result ───────────────────────────────
            return {
                "run_id": run_id,
                "status": "complete",
                "scenario_name": scenario_name,
                "result_summary": claude_result.get("result_summary", ""),
                "overall_severity": overall_severity,
                "impact_analysis": impact_analysis,
                "action_plan": claude_result.get("action_plan", []),
                "risk_flags": claude_result.get("risk_flags", []),
                "silver_lining": claude_result.get("silver_lining"),
                "cascade_chain": cascade_chain,
            }

        except Exception as e:
            sim_run.status = "failed"
            await db.commit()
            logger.error("whatif_simulation_failed", error=str(e))
            raise

    def _apply_perturbations(
        self,
        state: dict[str, Any],
        perturbations: list[dict[str, Any]],
        sim_start: datetime,
    ) -> dict[str, Any]:
        """Modify the forked twin state with perturbation effects."""
        for pert in perturbations:
            ptype = pert.get("type", "")
            params = pert.get("params", {})

            if ptype == "power_cut":
                cut_start = params.get("start_time", sim_start.isoformat())
                state["_power_cut_at"] = cut_start
                state["_power_cut_duration_hours"] = params.get("duration_hours", 1.5)

            elif ptype == "water_shortage":
                state["resources"]["water"]["available"] = False
                state["_water_shortage"] = True

            elif ptype == "unexpected_guest":
                state["_guest_count"] = params.get("count", 4)
                state["_guest_arrival"] = params.get("arrival_time", "16:00")
                state["_guest_includes_children"] = params.get("includes_children", False)

            elif ptype == "exam_week":
                state["_exam_mode"] = True
                state["_exam_member"] = params.get("member_id")
                state["_exam_type"] = params.get("exam_type", "general")

            elif ptype == "motor_failure":
                # Find motor in appliances and mark as failed
                for app_state in state.get("appliances", {}).values():
                    if app_state.get("type") == "motor":
                        app_state["state"] = "error"
                        app_state["alert"] = "MOTOR FAILURE"

            elif ptype == "internet_outage":
                state["resources"]["internet"]["available"] = False

        return state

    def _advance_sim_tick(
        self,
        state: dict[str, Any],
        current_time: datetime,
        perturbations: list[dict[str, Any]],
        routines: list[Any],
    ) -> dict[str, Any]:
        """Advance simulation by TICK_MINUTES, returning events and anomalies."""
        events: list[str] = []
        anomalies: list[str] = []
        cascades: list[str] = []
        disruptions: list[str] = []

        # Check power cut activation
        if "_power_cut_at" in state:
            try:
                cut_at = datetime.fromisoformat(str(state["_power_cut_at"]))
                if cut_at.tzinfo is None:
                    cut_at = cut_at.replace(tzinfo=IST)
                cut_end = cut_at + timedelta(hours=state.get("_power_cut_duration_hours", 1.5))

                if cut_at <= current_time < cut_end:
                    if state["resources"]["power"].get("available", True):
                        state["resources"]["power"]["available"] = False
                        events.append(f"{current_time.strftime('%H:%M')} — ⚡ Power cut starts")
                        cascades.extend([
                            f"{current_time.strftime('%H:%M')} — WiFi router off",
                            f"{current_time.strftime('%H:%M')} — Inverter activates",
                            f"{current_time.strftime('%H:%M')} — Motor cannot run",
                        ])
                elif current_time >= cut_end:
                    if not state["resources"]["power"].get("available", True):
                        state["resources"]["power"]["available"] = True
                        events.append(f"{current_time.strftime('%H:%M')} — ⚡ Power restored")
            except (ValueError, TypeError):
                pass

        # Check routine events at this tick
        for routine in routines:
            if not routine.next_expected_at:
                continue
            expected = routine.next_expected_at
            if expected.tzinfo is None:
                expected = expected.replace(tzinfo=IST)

            tick_window_end = current_time + timedelta(minutes=TICK_MINUTES)
            if current_time <= expected < tick_window_end:
                # Check if this routine would be disrupted
                disrupted = self._is_routine_disrupted(routine, state)
                if disrupted:
                    disruptions.append(routine.name)
                    events.append(
                        f"{current_time.strftime('%H:%M')} — ⚠️ {routine.name} disrupted: {disrupted}"
                    )
                else:
                    events.append(
                        f"{current_time.strftime('%H:%M')} — ✅ {routine.name} starts"
                    )

        # Check guest arrival
        if "_guest_arrival" in state:
            guest_hour = int(str(state["_guest_arrival"]).split(":")[0])
            if current_time.hour == guest_hour and current_time.minute == 0:
                events.append(
                    f"{current_time.strftime('%H:%M')} — 👥 {state['_guest_count']} guests arrive"
                )
                cascades.extend([
                    f"{current_time.strftime('%H:%M')} — Kitchen activity +80%",
                    f"{current_time.strftime('%H:%M')} — Extra chai rounds needed",
                ])

        return {
            "events": events,
            "anomalies": anomalies,
            "cascades": cascades,
            "disruptions": disruptions,
        }

    def _is_routine_disrupted(
        self, routine: Any, sim_state: dict[str, Any]
    ) -> str | None:
        """Check if a routine would be disrupted by the current sim state."""
        if routine.routine_type == "motor":
            if not sim_state["resources"]["power"].get("available", True):
                return "Power cut — motor cannot run"
            if sim_state.get("_water_shortage"):
                return "Water shortage — no supply"
        if routine.routine_type in ("meal", "school_prep"):
            if not sim_state["resources"]["power"].get("available", True):
                hour = datetime.now(IST).hour
                if hour >= 18:  # Evening cooking
                    return "Power cut — cooking disrupted"
        if routine.routine_type == "tuition":
            if sim_state.get("_exam_mode"):
                return "Exam week — tuition cancelled"
        return None

    def _analyze_routine_impact(
        self,
        routines: list[Any],
        perturbations: list[dict[str, Any]],
        sim_start: datetime,
        sim_end: datetime,
        baseline: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Compare baseline routine timing vs simulated timing."""
        impacts: list[dict[str, Any]] = []
        pert_types = {p["type"] for p in perturbations}

        for routine in routines:
            impact: dict[str, Any] | None = None

            if routine.routine_type == "motor" and "power_cut" in pert_types:
                cut_params = next(p["params"] for p in perturbations if p["type"] == "power_cut")
                impact = {
                    "routine": routine.name,
                    "baseline_time": "06:10",
                    "simulated_time": "MISSED — power cut",
                    "deviation_mins": None,
                    "severity": "critical",
                    "mitigation": "Run motor BEFORE the power cut window",
                }

            elif routine.routine_type == "meal" and "power_cut" in pert_types:
                impact = {
                    "routine": routine.name,
                    "baseline_time": "19:00",
                    "simulated_time": "18:15 (must complete before cut)",
                    "deviation_mins": -45,
                    "severity": "high",
                    "mitigation": "Start dinner prep 45 min earlier",
                }

            elif routine.routine_type == "tuition" and "exam_week" in pert_types:
                impact = {
                    "routine": routine.name,
                    "baseline_time": "17:00",
                    "simulated_time": "CANCELLED",
                    "deviation_mins": None,
                    "severity": "medium",
                    "mitigation": "Notify students of cancellation",
                }

            if impact:
                impacts.append(impact)

        return impacts

    def _analyze_resource_impact(
        self,
        perturbations: list[dict[str, Any]],
        baseline: dict[str, Any],
        duration_hours: int,
    ) -> list[dict[str, Any]]:
        """Analyze how resources are impacted by perturbations."""
        impacts: list[dict[str, Any]] = []

        for pert in perturbations:
            if pert["type"] == "power_cut":
                impacts.extend([
                    {
                        "resource": "power",
                        "baseline_level": "Available",
                        "projected_level_after": f"Cut for {pert['params'].get('duration_hours', 1.5)} hours",
                        "concern": "Inverter backup capacity",
                    },
                    {
                        "resource": "inverter_battery",
                        "baseline_level": "100%",
                        "projected_level_after": "~40% after cut",
                        "concern": "Limited to fans + LED lights only",
                    },
                ])
            elif pert["type"] == "water_shortage":
                impacts.append({
                    "resource": "water",
                    "baseline_level": "Normal",
                    "projected_level_after": "Tank draining only — no refill",
                    "concern": "Morning crisis if tank below 20%",
                })
            elif pert["type"] == "unexpected_guest":
                count = pert["params"].get("count", 4)
                impacts.append({
                    "resource": "water",
                    "baseline_level": "Normal",
                    "projected_level_after": f"x{1 + count * 0.1:.1f} usage",
                    "concern": "May need extra motor run",
                })

        return impacts

    def _build_cascade_chain(
        self,
        perturbations: list[dict[str, Any]],
        observed_cascades: list[str],
    ) -> list[str]:
        """Build a human-readable cascade chain for the perturbations."""
        chain: list[str] = []
        for pert in perturbations:
            ptype = pert["type"]
            rules = CASCADE_RULES.get(ptype, [])
            for rule in rules[:4]:  # Max 4 cascade events per perturbation
                chain.append(rule["description"])
        return chain[:8]  # Cap cascade chain at 8 items

    def _assess_severity(
        self,
        disrupted_routines: list[dict[str, Any]],
        resource_impacts: list[dict[str, Any]],
    ) -> str:
        """Assess overall simulation severity."""
        critical_count = sum(
            1 for r in disrupted_routines if r.get("severity") == "critical"
        )
        high_count = sum(
            1 for r in disrupted_routines if r.get("severity") == "high"
        )

        if critical_count >= 2:
            return "critical"
        if critical_count >= 1 or high_count >= 2:
            return "significant"
        if high_count >= 1:
            return "moderate"
        return "minimal"

    def _infer_type(self, perturbations: list[dict[str, Any]]) -> str:
        """Infer scenario type from perturbation types."""
        if not perturbations:
            return "general"
        return perturbations[0].get("type", "general")


# ── Singleton instance ─────────────────────────────────────────────────
whatif_simulator = WhatIfSimulator()
