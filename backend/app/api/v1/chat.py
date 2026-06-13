"""
GHARMIND AI — Gharji Chat API Endpoints
Conversational AI with full household context. Supports streaming.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.dependencies import AuthUser, DBSession
from app.services.chat_service import chat_service
from app.services.household_service import household_service
from app.services.prediction_engine import prediction_engine
from app.services.twin_service import twin_service

router = APIRouter(prefix="/households/{household_id}/chat", tags=["Gharji Chat"])


class ChatMessageRequest(BaseModel):
    message: str = Field(..., max_length=1000, examples=["Motor chalana chahiye abhi?"])
    language: str | None = None  # Override household default
    stream: bool = False


@router.post("/message")
async def send_chat_message(
    household_id: str,
    body: ChatMessageRequest,
    db: DBSession,
    user: AuthUser,
) -> Any:
    """
    Send a message to Gharji (household AI companion).
    Returns a streaming response if stream=True, otherwise full text.
    """
    household = await household_service.get_household(db, household_id)
    members = await household_service.list_members(db, household_id)
    member_summary = ", ".join(f"{m.name} ({m.role}, {m.age or '?'}y)" for m in members)

    twin_state = await twin_service.advance_tick(db, household_id)

    # Get current predictions for context
    predictions: list[dict[str, Any]] = []
    try:
        predictions = await prediction_engine.generate_predictions(
            db=db,
            household_id=household_id,
            twin_state=twin_state,
            household_name=household.name,
            city=household.city,
            state_name=household.state,
            language=household.language_preference,
        )
    except Exception:
        pass

    language = body.language or household.language_preference

    if body.stream:
        async def token_generator():
            async for chunk in chat_service.stream_response(
                db=db,
                household_id=household_id,
                user_message=body.message,
                household_name=household.name,
                city=household.city,
                state_name=household.state,
                language=language,
                member_summary=member_summary,
                twin_state=twin_state,
                predictions=predictions,
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            token_generator(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # Non-streaming response
    response = await chat_service.get_response(
        db=db,
        household_id=household_id,
        user_message=body.message,
        household_name=household.name,
        city=household.city,
        state_name=household.state,
        language=language,
        member_summary=member_summary,
        twin_state=twin_state,
        predictions=predictions,
    )

    return {
        "message_id": f"msg_{household_id[:8]}",
        "response": response,
        "language": language,
        "household_context_used": True,
    }
