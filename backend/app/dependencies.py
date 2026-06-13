"""
GHARMIND AI — FastAPI Dependency Injection
Shared dependencies used across all API routes.
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import CurrentUser, get_current_user
from app.db.session import get_db

# ── Typed dependency aliases (cleaner route signatures) ───────────────

DBSession = Annotated[AsyncSession, Depends(get_db)]
AuthUser = Annotated[CurrentUser, Depends(get_current_user)]
