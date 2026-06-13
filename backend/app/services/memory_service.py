"""
GHARMIND AI — Household Memory Service
Manages pgvector-based semantic memory for each household.
Stores: routine patterns, preferences, festival behaviors, seasonal adjustments.
Retrieves: semantically similar memories given current context.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.logging_config import get_logger
from app.models.prediction import HouseholdMemory
from app.services.bedrock.titan_client import titan_client

logger = get_logger(__name__)
IST = ZoneInfo("Asia/Kolkata")


class MemoryService:
    """Manages the semantic memory store for household AI."""

    async def store_memory(
        self,
        db: AsyncSession,
        household_id: str,
        memory_type: str,
        title: str,
        content: str,
        structured_data: dict[str, Any] | None = None,
        valid_seasons: list[str] | None = None,
        valid_months: list[int] | None = None,
        importance_score: int = 50,
    ) -> HouseholdMemory:
        """Store a new household memory with Titan embedding."""
        embedding = await titan_client.embed(content)
        embedding_str = titan_client.embedding_to_pg_literal(embedding)

        memory = HouseholdMemory(
            household_id=UUID(household_id),
            memory_type=memory_type,
            title=title,
            content=content,
            structured_data=structured_data,
            embedding_text=embedding_str,
            observed_at=datetime.now(IST),
            valid_seasons=valid_seasons,
            valid_months=valid_months,
            importance_score=importance_score,
        )
        db.add(memory)
        await db.flush()
        logger.debug("memory_stored", title=title, type=memory_type)
        return memory

    async def find_relevant_memories(
        self,
        db: AsyncSession,
        household_id: str,
        context_text: str,
        top_k: int = 5,
        memory_type: str | None = None,
        min_similarity: float = 0.65,
    ) -> list[dict[str, Any]]:
        """
        Find memories most semantically similar to the current context.
        Uses pgvector cosine similarity search.
        """
        embedding = await titan_client.embed(context_text)
        embedding_literal = titan_client.embedding_to_pg_literal(embedding)

        type_filter = "AND memory_type = :mtype" if memory_type else ""
        query_str = f"""
            SELECT
                id::text,
                title,
                content,
                memory_type,
                importance_score,
                observation_count,
                1 - (embedding <=> :embedding::vector) AS similarity
            FROM household_memories
            WHERE household_id = :hid
              AND embedding IS NOT NULL
              AND confidence >= 0.5
              {type_filter}
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit
        """

        params: dict[str, Any] = {
            "embedding": embedding_literal,
            "hid": household_id,
            "limit": top_k,
        }
        if memory_type:
            params["mtype"] = memory_type

        try:
            result = await db.execute(text(query_str), params)
            rows = result.mappings().all()

            memories = [
                {
                    "memory_id": row["id"],
                    "title": row["title"],
                    "content": row["content"],
                    "memory_type": row["memory_type"],
                    "importance": row["importance_score"],
                    "observations": row["observation_count"],
                    "similarity": round(float(row["similarity"]), 3),
                }
                for row in rows
                if float(row["similarity"]) >= min_similarity
            ]

            # Update last_accessed_at for retrieved memories
            if memories:
                memory_ids = [UUID(m["memory_id"]) for m in memories]
                await db.execute(
                    update(HouseholdMemory)
                    .where(HouseholdMemory.id.in_(memory_ids))
                    .values(last_accessed_at=datetime.now(IST))
                )

            return memories

        except Exception as e:
            logger.warning("memory_search_failed", error=str(e))
            return []

    async def increment_observation(
        self, db: AsyncSession, memory_id: str
    ) -> None:
        """Increment observation count for a memory (reinforces patterns)."""
        await db.execute(
            text("""
                UPDATE household_memories
                SET observation_count = observation_count + 1,
                    updated_at = NOW()
                WHERE id = :mid
            """),
            {"mid": memory_id},
        )

    async def seed_initial_memories(
        self, db: AsyncSession, household_id: str, household: Any
    ) -> int:
        """
        Seed initial household memories based on known patterns.
        Called after twin initialization.
        Returns number of memories created.
        """
        initial_memories = [
            {
                "type": "routine_pattern",
                "title": "Water motor runs every morning",
                "content": (
                    f"The household in {household.city} runs the water motor "
                    "every morning, typically between 06:00 and 06:45. "
                    "This is critical before the morning school and work rush."
                ),
                "importance": 90,
            },
            {
                "type": "cultural_pattern",
                "title": "Morning pooja is daily ritual",
                "content": (
                    "Morning pooja is performed daily by the family matriarch, "
                    "typically starting at 06:00. During festival weeks, "
                    "duration extends by 30-45 minutes and starts earlier."
                ),
                "importance": 80,
            },
            {
                "type": "seasonal_pattern",
                "title": f"City-specific power cut pattern for {household.city}",
                "content": (
                    f"In {household.city}, load shedding follows predictable weekly patterns. "
                    "Evening power cuts (typically 7:30pm) affect dinner preparation and "
                    "require advance device charging and meal scheduling."
                ),
                "importance": 75,
            },
            {
                "type": "festival_behavior",
                "title": "Diwali week changes household rhythms",
                "content": (
                    "During Diwali preparation week, water usage increases by 40%, "
                    "morning routines start 1 hour earlier, cleaning frequency doubles, "
                    "and guest probability is high. Power usage also increases due to decoration lights."
                ),
                "importance": 85,
            },
        ]

        count = 0
        for mem in initial_memories:
            try:
                await self.store_memory(
                    db=db,
                    household_id=household_id,
                    memory_type=mem["type"],
                    title=mem["title"],
                    content=mem["content"],
                    importance_score=mem["importance"],
                )
                count += 1
            except Exception as e:
                logger.warning("seed_memory_failed", title=mem["title"], error=str(e))

        logger.info("memories_seeded", household_id=household_id, count=count)
        return count


# ── Singleton instance ─────────────────────────────────────────────────
memory_service = MemoryService()
