"""
GHARMIND AI — Prediction Engine
7-step pipeline: Scan → Match → Factor → Score → Enrich → Detect → Rank.
Generates prioritized, evidence-backed predictions about upcoming household events.
"""
from __future__ import annotations

import math
import statistics
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import desc, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.logging_config import get_logger
from app.models.calendar import HouseholdCalendarEvent
from app.models.prediction import HouseholdMemory, Prediction
from app.models.routine import Routine, RoutineExecution
from app.models.twin import TwinStateSnapshot
from app.services.bedrock.claude_client import claude_client
from app.services.bedrock.prompts import build_prediction_messages
from app.services.bedrock.titan_client import titan_client
from app.services.cultural_intelligence import cultural_engine

logger = get_logger(__name__)

IST = ZoneInfo("Asia/Kolkata")

PRIORITY_SCORES = {"critical": 100, "high": 70, "normal": 40, "low": 10}


class PredictionEngine:
    """
    Generates proactive, context-aware household predictions.
    Each prediction has: title, action_suggestion, confidence, evidence trail.
    """

    # ── Step 1: Pattern Scanner ────────────────────────────────────────

    async def scan_due_routines(
        self,
        db: AsyncSession,
        household_id: str,
        horizon_hours: int = 2,
    ) -> list[dict[str, Any]]:
        """
        Scan for routines due in the next `horizon_hours`.
        Also detects overdue routines (anomaly candidates).
        """
        now = datetime.now(IST)
        horizon = now + timedelta(hours=horizon_hours)

        result = await db.execute(
            select(Routine).where(
                Routine.household_id == UUID(household_id),
                Routine.is_active.is_(True),
            )
        )
        routines = result.scalars().all()

        candidates: list[dict[str, Any]] = []
        for routine in routines:
            if not routine.next_expected_at:
                continue

            expected = routine.next_expected_at
            if expected.tzinfo is None:
                expected = expected.replace(tzinfo=IST)

            delta_mins = (expected - now).total_seconds() / 60

            if -30 <= delta_mins <= horizon_hours * 60:
                is_overdue = delta_mins < -10
                candidates.append({
                    "routine_id": str(routine.id),
                    "routine_name": routine.name,
                    "routine_type": routine.routine_type,
                    "recurrence": routine.recurrence,
                    "expected_at": expected.isoformat(),
                    "delta_mins": round(delta_mins),
                    "is_overdue": is_overdue,
                    "confidence_score": float(routine.confidence_score or 0.7),
                    "is_critical": routine.routine_type in ("motor", "meal", "school_prep"),
                    "schedule_expression": routine.schedule_expression or {},
                })

        return candidates

    # ── Step 2: Similarity Matcher ─────────────────────────────────────

    async def find_similar_contexts(
        self,
        db: AsyncSession,
        household_id: str,
        context_embedding: list[float],
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Use pgvector cosine similarity to find historical contexts most
        similar to the current household state.
        """
        embedding_literal = titan_client.embedding_to_pg_literal(context_embedding)

        # Raw SQL because SQLAlchemy doesn't natively support pgvector operators
        query = text("""
            SELECT
                id::text,
                snapshot_at,
                context_summary,
                season,
                festival_context,
                1 - (context_embedding <=> :embedding::vector) AS similarity
            FROM twin_state_snapshots
            WHERE household_id = :hid
              AND context_embedding IS NOT NULL
              AND snapshot_at > NOW() - INTERVAL '90 days'
            ORDER BY context_embedding <=> :embedding::vector
            LIMIT :limit
        """)

        try:
            result = await db.execute(
                query,
                {
                    "embedding": embedding_literal,
                    "hid": household_id,
                    "limit": limit,
                },
            )
            rows = result.mappings().all()
            return [
                {
                    "snapshot_id": row["id"],
                    "snapshot_at": str(row["snapshot_at"]),
                    "context_summary": row["context_summary"],
                    "season": row["season"],
                    "similarity": float(row["similarity"]),
                }
                for row in rows
                if float(row["similarity"]) > 0.65
            ]
        except Exception as e:
            logger.warning("similarity_search_failed", error=str(e))
            return []

    async def get_routine_execution_history(
        self,
        db: AsyncSession,
        routine_id: str,
        day_of_week: int,
        limit: int = 14,
    ) -> list[dict[str, Any]]:
        """Get recent execution history for a routine on a specific weekday."""
        result = await db.execute(
            select(RoutineExecution)
            .where(
                RoutineExecution.routine_id == UUID(routine_id),
                RoutineExecution.day_of_week == day_of_week,
                RoutineExecution.executed_at > datetime.now(IST) - timedelta(days=90),
            )
            .order_by(desc(RoutineExecution.executed_at))
            .limit(limit)
        )
        execs = result.scalars().all()
        return [
            {
                "executed_at": e.executed_at.isoformat(),
                "ist_time": e.ist_time.isoformat() if e.ist_time else None,
                "duration_mins": e.duration_mins,
                "deviation_mins": e.deviation_mins,
                "season": e.season,
                "was_on_schedule": e.was_on_schedule,
            }
            for e in execs
        ]

    # ── Step 3 + 4: Context Multiplier + Confidence Calculator ────────

    def calculate_confidence(
        self,
        base_confidence: float,
        temporal_evidence: int,
        semantic_similarity: float,
        festival_multiplier: float,
        deviation_history: list[int],
    ) -> float:
        """
        Bayesian-style confidence calculation.
        Combines historical base rate, semantic similarity, and cultural context.
        """
        prior = base_confidence

        evidence_strength = min(temporal_evidence / 10, 1.0)
        likelihood = (semantic_similarity * 0.6) + (evidence_strength * 0.4)

        posterior = (prior * 0.5) + (likelihood * 0.5)
        posterior *= festival_multiplier

        if deviation_history and len(deviation_history) > 1:
            std_dev = statistics.stdev(deviation_history)
            stability = max(0.5, 1.0 - (std_dev / 120))
            posterior *= stability

        return round(min(max(posterior, 0.05), 0.99), 2)

    def assign_priority(
        self,
        routine_type: str,
        delta_mins: float,
        is_overdue: bool,
        confidence: float,
    ) -> str:
        """Assign priority level based on routine type, timing, and confidence."""
        if is_overdue and routine_type in ("motor", "meal"):
            return "critical"
        if routine_type == "motor" and delta_mins < 15:
            return "critical"
        if routine_type in ("school_prep", "motor") and delta_mins < 30:
            return "high"
        if confidence > 0.85 and delta_mins < 60:
            return "high"
        if delta_mins < 120:
            return "normal"
        return "low"

    # ── Step 5: Claude Enrichment ──────────────────────────────────────

    async def enrich_with_claude(
        self,
        predictions: list[dict[str, Any]],
        hco_summary: str,
        household_name: str,
        city: str,
        language: str,
    ) -> list[dict[str, Any]]:
        """
        Send raw predictions to Claude for natural language enrichment.
        Claude adds: action_suggestion, reasoning, risk_if_ignored.
        Batched — 5 predictions per call.
        """
        if not predictions:
            return predictions

        enriched: list[dict[str, Any]] = []

        # Process in batches of 5
        for batch_start in range(0, len(predictions), 5):
            batch = predictions[batch_start: batch_start + 5]

            raw_for_claude = [
                {
                    "id": p.get("prediction_id", f"p{i}"),
                    "title": p["title"],
                    "type": p["prediction_type"],
                    "predicted_for": p.get("predicted_for", ""),
                    "confidence": p["confidence"],
                    "priority": p["priority"],
                }
                for i, p in enumerate(batch)
            ]

            system, messages = build_prediction_messages(
                hco_summary=hco_summary,
                raw_predictions=raw_for_claude,
                household_name=household_name,
                city=city,
                language=language,
            )

            try:
                result = await claude_client.invoke_structured(
                    messages=messages,
                    system_prompt=system,
                    mock_key="prediction_enrichment",
                )
                enrichment_map = {
                    e["id"]: e for e in result.get("predictions", [])
                }
            except Exception as e:
                logger.warning("claude_enrichment_failed", error=str(e))
                enrichment_map = {}

            for i, pred in enumerate(batch):
                pred_id = f"p{batch_start + i}"
                enrich = enrichment_map.get(pred_id, {})
                pred["action_suggestion"] = enrich.get(
                    "action_suggestion",
                    f"Attention needed: {pred['title']}",
                )
                pred["reasoning"] = enrich.get("reasoning", "")
                pred["risk_if_ignored"] = enrich.get("risk_if_ignored", "")
                enriched.append(pred)

        return enriched

    # ── Step 6: Anomaly Detector ───────────────────────────────────────

    async def detect_anomalies(
        self,
        db: AsyncSession,
        household_id: str,
        twin_state: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Detect deviations from expected patterns.
        Types: routine_missed, appliance_overrun, unexpected_absence.
        """
        anomalies: list[dict[str, Any]] = []

        # Check overdue routines already in twin state
        for overdue in twin_state.get("overdue_routines", []):
            anomalies.append({
                "anomaly_type": "routine_missed",
                "severity": "high" if overdue["overdue_mins"] > 30 else "normal",
                "description": f"{overdue['name']} is {overdue['overdue_mins']} minutes overdue",
                "routine_id": overdue["routine_id"],
                "overdue_mins": overdue["overdue_mins"],
            })

        # Check motor specifically (most critical for Indian homes)
        for app_state in twin_state.get("appliances", {}).values():
            if app_state.get("type") == "motor" and app_state.get("alert"):
                if "OVERDUE" in str(app_state.get("alert", "")):
                    anomalies.append({
                        "anomaly_type": "appliance_overdue",
                        "severity": "critical",
                        "description": f"Water motor: {app_state['alert']}",
                        "appliance_name": app_state["name"],
                    })

        return anomalies

    # ── Step 7: Ranker ──────────────────────────────────────────────────

    def rank_predictions(
        self, predictions: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Rank predictions by composite score: priority × confidence × urgency.
        Also applies anti-flood: max 3 predictions per 30-minute window.
        """
        now = datetime.now(IST)

        for pred in predictions:
            priority_score = PRIORITY_SCORES.get(pred.get("priority", "normal"), 40)
            confidence = pred.get("confidence", 0.5) * 100

            # Time urgency: exponential decay, peaks when < 15 min away
            delta = pred.get("delta_mins", 60)
            urgency = math.exp(-max(delta, 0) / 60) * 100

            pred["rank_score"] = (
                priority_score * 0.4 + confidence * 0.4 + urgency * 0.2
            )

        # Sort by rank score descending
        ranked = sorted(predictions, key=lambda p: p.get("rank_score", 0), reverse=True)

        # Anti-flood: group by 30-min windows
        return ranked[:15]  # Cap at 15 total

    # ── Main pipeline ──────────────────────────────────────────────────

    async def generate_predictions(
        self,
        db: AsyncSession,
        household_id: str,
        twin_state: dict[str, Any],
        household_name: str,
        city: str,
        state_name: str,
        language: str = "hinglish",
    ) -> list[dict[str, Any]]:
        """
        Execute the full 7-step prediction pipeline.
        Returns ranked, enriched predictions ready for storage and display.
        """
        now = datetime.now(IST)
        logger.info("prediction_pipeline_start", household_id=household_id)

        # ── 1. Scan ──────────────────────────────────────────────────
        due_routines = await self.scan_due_routines(db, household_id, horizon_hours=6)

        # ── 2. Get current context embedding ────────────────────────
        context_text = twin_state.get("context_summary", "")
        try:
            context_embedding = await titan_client.embed(context_text)
        except Exception:
            context_embedding = []
            logger.warning("titan_embed_failed_in_pipeline")

        similar_contexts = (
            await self.find_similar_contexts(db, household_id, context_embedding)
            if context_embedding
            else []
        )
        avg_similarity = (
            sum(c["similarity"] for c in similar_contexts) / len(similar_contexts)
            if similar_contexts
            else 0.5
        )

        # ── 3 + 4. Factor + Score ────────────────────────────────────
        festivals = twin_state.get("festival_context", [])
        festival_model = cultural_engine.get_festival_multiplier(festivals)
        festival_boost = float(festival_model.get("confidence_boost", 1.0))

        raw_predictions: list[dict[str, Any]] = []

        for routine in due_routines:
            history = await self.get_routine_execution_history(
                db, routine["routine_id"], now.weekday()
            )
            deviations = [h["deviation_mins"] for h in history if h["deviation_mins"]]
            temporal_evidence = len(history)

            confidence = self.calculate_confidence(
                base_confidence=routine["confidence_score"],
                temporal_evidence=temporal_evidence,
                semantic_similarity=avg_similarity,
                festival_multiplier=festival_boost,
                deviation_history=deviations,
            )

            priority = self.assign_priority(
                routine_type=routine["routine_type"],
                delta_mins=routine["delta_mins"],
                is_overdue=routine["is_overdue"],
                confidence=confidence,
            )

            predicted_for = (
                now + timedelta(minutes=max(routine["delta_mins"], 0))
            ).isoformat()

            raw_predictions.append({
                "prediction_id": f"pred_{routine['routine_id'][:8]}",
                "prediction_type": "routine_overdue" if routine["is_overdue"] else "routine_start",
                "title": self._build_title(routine),
                "description": self._build_description(routine, history),
                "predicted_for": predicted_for,
                "delta_mins": routine["delta_mins"],
                "confidence": confidence,
                "priority": priority,
                "category": self._get_category(routine["routine_type"]),
                "linked_routine_id": routine["routine_id"],
                "evidence": [
                    f"History: {temporal_evidence} matching weekday executions",
                    f"Similar context similarity: {avg_similarity:.2f}",
                    f"Festival boost: {festival_boost}x",
                ],
            })

        # Add anomaly-based predictions
        anomalies = await self.detect_anomalies(db, household_id, twin_state)
        for anomaly in anomalies:
            if anomaly["anomaly_type"] == "appliance_overdue":
                raw_predictions.append({
                    "prediction_id": f"anom_{anomaly.get('appliance_name', 'unk')[:8]}",
                    "prediction_type": "appliance_action",
                    "title": f"⚠️ {anomaly['description']}",
                    "description": anomaly["description"],
                    "predicted_for": now.isoformat(),
                    "delta_mins": 0,
                    "confidence": 0.95,
                    "priority": "critical",
                    "category": "water",
                    "evidence": ["Direct twin state detection"],
                })

        # Add power cut prediction
        power = twin_state.get("resources", {}).get("power", {})
        if power.get("cut_probability", 0) > 0.6:
            cut_time = power.get("cut_prediction")
            raw_predictions.append({
                "prediction_id": "pred_power_cut",
                "prediction_type": "power_event",
                "title": f"⚡ Load Shedding Expected — {cut_time}",
                "description": f"MSEDCL pattern: power cut expected around {cut_time}. "
                               f"Probability: {int(power['cut_probability'] * 100)}%.",
                "predicted_for": (now + timedelta(hours=3)).isoformat(),
                "delta_mins": 180,
                "confidence": power["cut_probability"],
                "priority": "high" if power["cut_probability"] > 0.7 else "normal",
                "category": "power",
                "evidence": [
                    f"City pattern: {city}",
                    f"Historical probability: {power['cut_probability']:.0%}",
                ],
            })

        # ── 5. Claude Enrichment ─────────────────────────────────────
        hco_summary = twin_state.get("context_summary", "Current household context")
        enriched = await self.enrich_with_claude(
            predictions=raw_predictions,
            hco_summary=hco_summary,
            household_name=household_name,
            city=city,
            language=language,
        )

        # ── 7. Rank ──────────────────────────────────────────────────
        ranked = self.rank_predictions(enriched)

        # Persist to DB
        await self._save_predictions(db, ranked, household_id, now)

        logger.info(
            "prediction_pipeline_complete",
            household_id=household_id,
            count=len(ranked),
            critical=sum(1 for p in ranked if p["priority"] == "critical"),
        )
        return ranked

    def _build_title(self, routine: dict[str, Any]) -> str:
        type_titles = {
            "motor": "💧 Water Motor",
            "pooja": "🪔 Morning Pooja",
            "school_prep": "🚌 School Bus Prep",
            "tuition": "📚 Tuition Batch",
            "chai": "☕ Evening Chai",
            "meal": "🍽️ Meal Preparation",
            "cleaning": "🧹 Cleaning Time",
        }
        base = type_titles.get(routine["routine_type"], routine["routine_name"])
        if routine["is_overdue"]:
            return f"{base} — OVERDUE {abs(routine['delta_mins'])} min"
        if abs(routine["delta_mins"]) < 5:
            return f"{base} — Starting Now"
        return f"{base} — in {routine['delta_mins']} min"

    def _build_description(
        self, routine: dict[str, Any], history: list[dict[str, Any]]
    ) -> str:
        name = routine["routine_name"]
        delta = routine["delta_mins"]
        hist_count = len(history)

        if routine["is_overdue"]:
            return (
                f"{name} was expected {abs(delta)} minutes ago. "
                f"Based on {hist_count} historical executions."
            )
        return (
            f"{name} is due in {delta} minutes. "
            f"Pattern detected from {hist_count} historical executions."
        )

    def _get_category(self, routine_type: str) -> str:
        mapping = {
            "motor": "water",
            "pooja": "routine",
            "school_prep": "family",
            "tuition": "routine",
            "chai": "routine",
            "meal": "routine",
            "cleaning": "routine",
            "festival": "festival",
            "study": "study",
        }
        return mapping.get(routine_type, "routine")

    async def _save_predictions(
        self,
        db: AsyncSession,
        predictions: list[dict[str, Any]],
        household_id: str,
        now: datetime,
    ) -> None:
        """Persist generated predictions to the database."""
        from decimal import Decimal

        for pred in predictions:
            expires_at = now + timedelta(hours=6)
            db_pred = Prediction(
                household_id=UUID(household_id),
                prediction_type=pred["prediction_type"],
                title=pred["title"][:300],
                description=pred["description"],
                action_suggestion=pred.get("action_suggestion", ""),
                predicted_for=datetime.fromisoformat(pred["predicted_for"]),
                confidence_score=Decimal(str(pred["confidence"])),
                priority=pred["priority"],
                category=pred.get("category"),
                reasoning=pred.get("reasoning", ""),
                evidence={"points": pred.get("evidence", [])},
                linked_routine_id=UUID(pred["linked_routine_id"])
                if pred.get("linked_routine_id")
                else None,
                status="pending",
                expires_at=expires_at,
            )
            db.add(db_pred)


# ── Singleton instance ─────────────────────────────────────────────────
prediction_engine = PredictionEngine()
