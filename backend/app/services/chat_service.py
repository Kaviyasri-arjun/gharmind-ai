"""
GHARMIND AI — Gharji Chat Service
Manages conversational AI interactions with the household.
Builds rich context-aware prompts and streams Claude responses.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, AsyncGenerator
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.logging_config import get_logger
from app.services.bedrock.claude_client import claude_client
from app.services.bedrock.prompts import GHARJI_SYSTEM_PROMPT
from app.services.memory_service import memory_service

logger = get_logger(__name__)
IST = ZoneInfo("Asia/Kolkata")


class ChatService:
    """Manages conversational AI interactions (Gharji)."""

    def _build_gharji_system(
        self,
        household_name: str,
        city: str,
        state_name: str,
        language: str,
        member_summary: str,
        twin_state: dict[str, Any],
        predictions: list[dict[str, Any]],
    ) -> str:
        """Build Gharji system prompt with full household context."""
        now = datetime.now(IST)
        ist_time = now.strftime("%I:%M %p")
        day_of_week = now.strftime("%A")

        temporal = twin_state.get("temporal", {})
        season = temporal.get("season", "unknown")
        festivals = temporal.get("festivals_active", [])
        festival_str = ", ".join(festivals) if festivals else "No active festival"
        urgency = twin_state.get("urgency_score", 0)

        # Build state summary
        resources = twin_state.get("resources", {})
        water = resources.get("water", {})
        power = resources.get("power", {})

        state_parts: list[str] = []
        if water.get("alert"):
            state_parts.append(f"💧 Water: {water['alert']} (tank {water.get('tank_level_pct', '?')}%)")
        if power.get("cut_prediction"):
            state_parts.append(f"⚡ Power cut expected at {power['cut_prediction']}")
        if twin_state.get("overdue_routines"):
            for r in twin_state["overdue_routines"][:2]:
                state_parts.append(f"⚠️ {r['name']} overdue {r['overdue_mins']} min")

        current_state_summary = "\n".join(state_parts) if state_parts else "All systems normal"

        # Build predictions summary
        pred_parts: list[str] = []
        for p in predictions[:3]:
            pred_parts.append(
                f"- [{p.get('priority', 'normal').upper()}] {p.get('title', '')} "
                f"(conf: {int(p.get('confidence', 0) * 100)}%)"
            )
        predictions_summary = "\n".join(pred_parts) if pred_parts else "No active predictions"

        return GHARJI_SYSTEM_PROMPT.format(
            household_name=household_name,
            city=city,
            state=state_name,
            language=language,
            member_summary=member_summary,
            ist_time=ist_time,
            day_of_week=day_of_week,
            season=season,
            festival_context=festival_str,
            urgency_score=urgency,
            current_state_summary=current_state_summary,
            predictions_summary=predictions_summary,
        )

    async def get_response(
        self,
        db: AsyncSession,
        household_id: str,
        user_message: str,
        household_name: str,
        city: str,
        state_name: str,
        language: str,
        member_summary: str,
        twin_state: dict[str, Any],
        predictions: list[dict[str, Any]],
    ) -> str:
        """Get a full (non-streaming) response from Gharji."""
        # Fetch relevant memories
        memories = await memory_service.find_relevant_memories(
            db=db,
            household_id=household_id,
            context_text=user_message,
            top_k=3,
        )
        memory_context = "\n".join(f"- {m['content']}" for m in memories)
        if memory_context:
            twin_state = {**twin_state, "_memory_context": memory_context}

        system = self._build_gharji_system(
            household_name, city, state_name, language,
            member_summary, twin_state, predictions
        )
        messages = [{"role": "user", "content": user_message}]

        response = await claude_client.invoke(
            messages=messages,
            system_prompt=system,
            max_tokens=512,
            temperature=0.7,
            mock_key="chat_response",
        )
        logger.info("chat_response_generated", household_id=household_id)
        return response

    async def stream_response(
        self,
        db: AsyncSession,
        household_id: str,
        user_message: str,
        household_name: str,
        city: str,
        state_name: str,
        language: str,
        member_summary: str,
        twin_state: dict[str, Any],
        predictions: list[dict[str, Any]],
    ) -> AsyncGenerator[str, None]:
        """Stream Gharji response tokens for real-time UI."""
        system = self._build_gharji_system(
            household_name, city, state_name, language,
            member_summary, twin_state, predictions
        )
        messages = [{"role": "user", "content": user_message}]

        async for chunk in claude_client.stream(
            messages=messages,
            system_prompt=system,
            max_tokens=512,
        ):
            yield chunk


# ── Singleton instance ─────────────────────────────────────────────────
chat_service = ChatService()
