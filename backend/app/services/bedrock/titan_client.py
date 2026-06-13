"""
GHARMIND AI — AWS Bedrock Titan Embeddings Client
Wraps boto3 for Titan Embed Text v1 (1536-dim vectors).
Used by: ContextAgent (context embeddings), MemoryService (semantic search),
         PredictionEngine (routine similarity matching).
"""
from __future__ import annotations

import json
import time
from typing import Any

import boto3
from botocore.exceptions import ClientError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import settings
from app.core.exceptions import BedrockError, BedrockThrottleError
from app.logging_config import get_logger

logger = get_logger(__name__)

# Fixed dimensions for Titan Embed Text v1
TITAN_EMBEDDING_DIMS = 1536
TITAN_MAX_CHARS = 8000  # Titan input character limit


def _mock_embedding(text: str) -> list[float]:
    """
    Generate a deterministic mock embedding for local development.
    Uses text hash to produce consistent (though not semantically meaningful) vectors.
    """
    import hashlib
    import math

    h = hashlib.md5(text.encode()).digest()
    seed = int.from_bytes(h, "big")

    result: list[float] = []
    for i in range(TITAN_EMBEDDING_DIMS):
        val = math.sin(seed * (i + 1) * 0.0001) * 0.5
        result.append(round(val, 6))

    # L2 normalize
    magnitude = sum(v * v for v in result) ** 0.5
    if magnitude > 0:
        result = [v / magnitude for v in result]

    return result


class TitanClient:
    """
    AWS Bedrock Titan Embeddings client.
    Provides text-to-vector embedding with automatic batching.
    """

    def __init__(self) -> None:
        self._client: Any = None
        self.model_id = settings.BEDROCK_TITAN_EMBED_MODEL_ID

    @property
    def client(self) -> Any:
        """Lazy-initialize boto3 Bedrock Runtime client."""
        if self._client is None:
            kwargs: dict[str, Any] = {"region_name": settings.BEDROCK_REGION}
            if settings.AWS_ACCESS_KEY_ID:
                kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
            self._client = boto3.client("bedrock-runtime", **kwargs)
        return self._client

    @retry(
        retry=retry_if_exception_type((BedrockThrottleError, ConnectionError)),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def embed(self, text: str) -> list[float]:
        """
        Generate a 1536-dimensional embedding for the given text.

        Args:
            text: Input text (max 8000 chars — auto-truncated)

        Returns:
            List of 1536 floats (L2-normalized)
        """
        if settings.BEDROCK_MOCK_RESPONSES:
            return _mock_embedding(text)

        # Truncate to model limit
        if len(text) > TITAN_MAX_CHARS:
            text = text[:TITAN_MAX_CHARS]
            logger.debug("titan_embed_truncated", original_len=len(text))

        t0 = time.perf_counter()
        try:
            body = json.dumps({"inputText": text})
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType="application/json",
                accept="application/json",
            )
            response_body = json.loads(response["body"].read())
            embedding: list[float] = response_body["embedding"]
            latency_ms = round((time.perf_counter() - t0) * 1000, 2)
            logger.debug(
                "titan_embed_success",
                text_chars=len(text),
                dims=len(embedding),
                latency_ms=latency_ms,
            )
            return embedding

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ("ThrottlingException", "TooManyRequestsException"):
                raise BedrockThrottleError(model_id=self.model_id) from e
            logger.error("titan_embed_error", error=str(e))
            raise BedrockError(message=str(e), model_id=self.model_id) from e

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        Titan doesn't support batch API — calls are sequential with small delays.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings in the same order
        """
        results: list[list[float]] = []
        for i, text in enumerate(texts):
            embedding = await self.embed(text)
            results.append(embedding)
            if not settings.BEDROCK_MOCK_RESPONSES and i < len(texts) - 1:
                # Small delay between API calls to avoid throttling
                import asyncio
                await asyncio.sleep(0.05)
        return results

    @staticmethod
    def embedding_to_pg_literal(embedding: list[float]) -> str:
        """
        Convert embedding list to PostgreSQL vector literal string.
        Format: '[0.1,0.2,...,0.n]' — used in raw SQL queries.
        """
        return "[" + ",".join(str(v) for v in embedding) + "]"

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two embeddings."""
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = sum(x * x for x in a) ** 0.5
        mag_b = sum(x * x for x in b) ** 0.5
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)


# ── Singleton instance ─────────────────────────────────────────────────
titan_client = TitanClient()
